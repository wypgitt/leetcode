# System Design: URL Shortener at Scale

> **Focus areas:** ID generation · Redirect hot path · Analytics · Custom aliases · Abuse/spam · Caching · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split write/read/analytics load classes, resolved ownership of ID minting vs redirect serving, honest MVP vs extreme-scale paths

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

Goal: **bound the product**—what “shorten + redirect” means at internet scale, which analytics are online vs offline, and which abuse controls are non-negotiable.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who creates links? | Authenticated users + API partners; optional anonymous with stricter rate limits | `tenant_id` / `user_id` on every write; quotas from day 1 |
| F2 | Short code form? | Base62 ~7–8 chars; optional custom alias | ID generator + reserved alias namespace; uniqueness constraint |
| F3 | Redirect semantics? | 301 for permanent SEO; 302/307 for analytics-friendly; product picks default | CDN/cache interaction differs for 301 vs 302 |
| F4 | Expiration? | Optional TTL; default never expire for MVP | TTL index / soft-delete sweeper |
| F5 | Custom aliases? | Yes, paid/verified users; length ≥ min; reserved words blocked | Separate alias table + moderation |
| F6 | Analytics? | Click counts, referrer, country/ASN, device; dashboards near-real-time-ish | Async event pipeline; not on critical redirect path |
| F7 | Preview / expand API? | Optional `GET /v1/expand/{code}` for trusted clients | Authz; rate limit; no open redirect abuse |
| F8 | Edit / disable? | Owner can update target URL (policy) or disable; audit trail | Versioned mapping or `revoked_at`; cache invalidate |
| F9 | QR codes? | Generate on demand from short URL | Stateless; not a storage problem |
| F10 | Deep links / app links? | Phase 2 | Platform-specific redirect rules later |
| F11 | Bulk create? | API partners need batch | Batch API with idempotency keys |
| F12 | Admin / trust & safety? | Takedown malware/phishing URLs | Blocklist + rapid revoke path |

**MVP functional scope (lock with interviewer):**

1. Create short URL from long URL (authn required for production; anonymous optional with caps).  
2. Redirect `GET /{code}` → long URL with chosen status code.  
3. Optional TTL and custom alias (unique).  
4. Idempotent create via `(user_id, idempotency_key)`.  
5. Basic analytics: click count + coarse geo/UA aggregated asynchronously.  
6. Owner APIs: list, disable, (optional) update target.  
7. Abuse: rate limits, malware URL checks (async + sync denylist), takedown.

**Out of MVP (explicitly defer):**

- Perfect real-time global click dashboards with second-level consistency  
- Link-in-bio social graph product  
- A/B split redirects / multi-variant destinations  
- Paid link monetization / interstitial ads  
- Full brand custom domains at 1000× complexity in first hour (design hooks OK)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Redirect latency? | Hot path must feel instant | p50 < 20ms edge, p99 < 100ms in-region (cache hit); origin p99 < 200ms |
| N2 | Create latency? | Interactive API | p99 < 300ms |
| N3 | Availability? | Redirects are revenue/trust critical | 99.99% redirect; 99.9% create |
| N4 | Durability? | Accepted short codes must resolve | Mapping durable before ACK create |
| N5 | Consistency? | Create then immediately redirect (same user) | Read-your-write for creator; eventual OK for global caches |
| N6 | Analytics lag? | Near-real-time OK | p95 dashboard lag < 1–5 min; counts approximate OK |
| N7 | Abuse resistance? | Spam/malware must not dominate | Rate limits, URL scanning, rapid revoke < 60s globally for hot paths |
| N8 | Multi-region? | Global users | Active-active redirects via edge cache; writes with clear ownership |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User creates `https://example.com/very/long` → gets `https://sho.rt/aB3xY9k` → shares → recipients redirect.  
2. Custom alias `sho.rt/launch` for verified user → unique check → stored.  
3. Click storm on viral link → edge cache serves redirects; analytics sample/aggregate.  
4. Owner disables link → subsequent redirects 410/404; caches invalidated.  
5. Link with TTL expires → sweeper or lazy reject on read.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate create (same idempotency key) | Return original short URL; no second mapping |
| Custom alias collision | `409 Conflict` |
| Reserved word (`admin`, `api`, `health`) | Reject at validation |
| Malicious destination (phishing) | Sync denylist block; async scanner may disable later |
| Extremely long URL (>2–8 KB) | Reject or store hash+blob; cap length |
| Unicode / homoglyph alias | Normalize NFKC; reject confusables for custom aliases |
| Open redirect chains | Bound redirects; store final URL; optional resolve-once at create |
| Cache serves stale after disable | Short TTL + purge API; prefer 302 if analytics/disable matter |
| ID generator hotspot / collision | Unique constraint + retry; or preallocated ranges |
| Analytics loss under spike | Buffer drop oldest / sample; never fail redirect |
| DB partition for hot code | Cache + key hashing; hot-key replication at edge |
| Clock skew on TTL | Store absolute `expires_at` UTC; evaluate server-side |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active short links | 100M | 1B | 10B | 100B |
| Creates / day | 10M | 100M | 1B | 10B |
| Peak **create** QPS | ~500 | ~5K | ~50K | ~500K |
| Redirects / day | 1B | 10B | 100B | 1T |
| Peak **redirect** QPS | ~50K | ~500K | ~5M | ~50M |
| Unique creators | 1M | 10M | 100M | 1B |
| Custom aliases / day | 100K | 1M | 10M | 100M |
| Analytics events / day | 1B | 10B | 100B | 1T |
| Edge PoPs | 20 | 50 | 100 | 200+ |
| Regions (data plane) | 2 | 3 | 5 | 8+ |

**What each jump forces:**

- **10×:** Edge caching mandatory; separate analytics pipeline; ID range allocation; Redis/CDN layer.  
- **100×:** Sharded KV for mappings; async multi-region replication; bloom filters for negative cache; abuse ML.  
- **1,000×:** Cell/region ownership for writes; global anycast redirect; hierarchical analytics; hot-key special casing; reserved capacity for viral storms.

### 1.5 Etc. (Constraints & Assumptions)

- Short domain is owned (`sho.rt` stand-in); HTTPS everywhere.  
- We are **not** building a full CDN from scratch—use commercial CDN/edge, design invalidation correctly.  
- Analytics are **best-effort approximate** unless interviewer demands exact (then cost jumps).  
- Legal: DMCA/abuse takedown SLA exists; design for rapid disable.  
- NVIDIA interview framing: treat as classic distributed systems + caching + ID uniqueness; same rigor as GPU control-plane uniqueness problems.

**Scope statement:**

> Design a global URL shortener: durable unique short-code minting, ultra-low-latency redirects via edge cache, optional custom aliases and TTL, async click analytics, and abuse/takedown controls—scaling from ~1B redirects/day through 10× / 100× / 1,000× without sacrificing create durability or redirect availability.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| **Redirect** read | 50K QPS | 50M QPS | Dominates; must be cache-heavy |
| **Create** write | 500 QPS | 500K QPS | Durable + unique ID |
| **Update/disable** | ~50 QPS | ~50K QPS | Cache purge critical |
| **Analytics ingest** | ~50K evt/s | ~50M evt/s | Async; sample OK |
| **Dashboard query** | ~100 QPS | ~10K QPS | Pre-aggregates |

**Deal-breaker:** designing the redirect path to synchronously write every click to the primary OLTP.

### 2.2 ID space math

```text
Base62 alphabet = 62 chars
Length 7: 62^7 ≈ 3.52e12 ≈ 3.5 trillion codes
Length 8: 62^8 ≈ 2.18e14

Baseline active 100M → tiny fraction of 7-char space
1,000× active 100B → still fits in 7 chars with headroom
Use 8 chars if wanting sparsity against enumeration / branding

Enumeration risk: short codes are guessable → rate-limit expand;
do not put secrets in query-string of long URL if code is public
```

### 2.3 Storage

```text
Mapping row ~200–500 B (code, url, user_id, flags, timestamps, ttl)
Baseline 100M × 300 B ≈ 30 GB
1,000× 100B × 300 B ≈ 30 TB metadata (hot/warm)

Long URLs average 100–200 B; outliers to blob store if >2 KB

Indexes: unique(code), unique(alias), secondary(user_id, created_at)
Replication factor 3 → ~3× raw for durable store
```

**Unit check:** 100B × 300 B = 3×10^10 × 300? No: 100×10^9 × 300 = 3×10^13 B = **30 TB**. Correct.

### 2.4 Cache & bandwidth

```text
Redirect response ~200–500 B headers + Location
50K QPS × 400 B ≈ 20 MB/s egress origin (tiny if edge hits)
At 50M QPS × 400 B ≈ 20 GB/s global — edge absorbs nearly all

Cache hit ratio target ≥ 95–99% for redirects (power-law popular links)
Viral key: 1% of codes may drive 50%+ traffic → hot-key at edge
```

### 2.5 Analytics volume

```text
1B clicks/day ≈ 11.6K evt/s average; peak ~5× → ~50–60K/s (baseline)
Event raw ~200 B → 1B × 200 B ≈ 200 GB/day raw
1,000× → 200 TB/day raw → must aggregate early, sample, or columnar compress

Store aggregates:
  (code, hour, country) → count
Not every raw click forever in OLTP
```

### 2.6 Create write amplification

```text
Create path: validate → scan URL? → mint ID → INSERT → replicate → ACK
Optional: async malware scan after ACK with quick disable

At 500K create QPS: need sharded writers + ID ranges; single PG dies
```

### 2.7 Critical bottlenecks (rank ordered)

1. **Redirect origin** if cache miss storm / wrong 301 caching  
2. **Hot key** viral link overwhelming one shard (mitigate at edge)  
3. **ID uniqueness** under concurrent mint  
4. **Analytics ingest** melting primary if coupled  
5. **Cache purge lag** after disable/malware  
6. **Custom alias** contention on popular words  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
ShortLink:
  code          # opaque base62 (system-generated)
  alias?        # optional vanity (unique)
  long_url
  owner_id / tenant_id
  created_at, expires_at?
  status: ACTIVE | DISABLED | EXPIRED
  redirect_code: 301 | 302 | 307
  metadata (utm defaults, tags)

ClickEvent (async):
  code, ts, edge_pop, country, ua_class, referrer_hash
```

**Resolution key:** prefer `alias` if path matches vanity rules; else `code`.

### 3.2 Options: ID generation

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. DB auto-increment + base62 | Simple, compact | Hot sequence; leaks volume; multi-region hard | Multi-region active writes without ranges |
| B. UUID → base62 truncate | Easy | Collisions if truncated; long codes | Truncating UUID without collision strategy |
| C. Preallocated ranges (ticket servers) | High QPS; multi-region friendly | Range manager HA; wasted IDs on crash | Single ticket server SPOF |
| D. Snowflake-style (time+worker+seq) | No central DB per ID | Clock skew; slightly longer encoding | Needing strictly random unguessable IDs without rate limits |
| E. Hash(long_url) prefix | Deterministic dedupe | Collision; can’t have two aliases same URL easily | Product wants multiple shorts per URL |

**Chosen path:**

- **MVP:** Snowflake-like 64-bit ID → base62, unique constraint as safety net; or Postgres sequence with **range allocator** per API instance.  
- **100×+:** Coordinated **range allocation service** (or per-cell snowflake) so creates never bottleneck on one sequence row.

**Dedup policy (product):** same long URL → new code each time (default) OR return existing (optional). Lock with interviewer.

### 3.3 Redirect path (resolve ownership)

**Invariant:** Redirect serving never blocks on analytics or malware re-scan.

```text
Edge/CDN:
  1. Lookup code in edge cache → Location header → done
  2. Miss → origin Redirect Service → KV/DB → populate cache
  3. Emit click event async (UDP/log/queue); drop under pressure
Origin:
  Validate status ACTIVE and not expired
  Return redirect; set Cache-Control based on policy
```

**301 vs 302:**

| Code | Browser/CDN behavior | Use when |
|------|----------------------|----------|
| 301 | Aggressively cached; hard to revoke | Truly permanent, rare disable |
| 302/307 | Shorter cache; better for analytics & disable | Default for most shorteners |

**Deal-breaker:** 301 everything + no purge story when phishing takedown needed.

### 3.4 Custom aliases

```text
Rules:
  charset [a-zA-Z0-9_-], length 3–32
  reserved denylist
  NFKC normalize; reject homoglyphs
  unique globally (or per custom domain)

Write path:
  authz → validate → INSERT alias UNIQUE → bind to link_id
```

Aliases are a **separate namespace** from opaque codes to avoid burning short ID space on vanity.

### 3.5 Caching strategy

| Layer | What | TTL | Notes |
|-------|------|-----|-------|
| Browser | Redirect | Short if 302 | Limited control |
| CDN/edge | code→URL | 60s–1h + purge | Hot path |
| Origin Redis | code→URL | minutes | Protect DB |
| Negative cache | unknown codes | 10–60s | Stop enumeration storms |

**Invalidation:** on disable/update → purge edge by key + bump `cache_epoch` in origin so stale ignored.

### 3.6 Analytics pipeline

```text
Redirect edge → click log / Kafka
  → stream aggregate (code, minute, country)
  → OLAP / TSDB for dashboards
  → optional exact counter in Redis with periodic flush (approximate OK)
```

**Ownership:** Analytics is **downstream**; redirect success does not depend on Kafka ACK (at-most-once clicks acceptable unless product requires stronger—then dual-write risk).

### 3.7 Abuse & trust

| Control | Where |
|---------|-------|
| Create rate limit | API gateway per user/IP/API key |
| URL denylist / Safe Browsing-like | Sync check on create + continuous recheck |
| Redirect block | Status DISABLED; edge purge |
| Enumeration | Rate limit 404s; CAPTCHA on suspicious |
| Bulk spam detection | Velocity features; shadow-ban |
| Custom alias abuse | Verified accounts; cooldown |

**Rapid revoke SLO:** write DISABLED → purge edge < 60s p99 for known keys; viral keys pre-warmed with short TTL.

### 3.8 Multi-region clarity

| Plane | Mode |
|-------|------|
| Redirect read | Global edge; any region origin on miss |
| Create write | **Home cell** per tenant/user OR regional write with async replicate |
| Mapping replication | Async to other regions; accept brief miss → pull from home |
| Analytics | Regional ingest → global rollup |

**Chosen:** Active-active **redirect**; creates go to regional primary with async replication + cache fill on first redirect elsewhere.

**Deal-breaker:** Dual independent writers minting overlapping ID ranges without coordination.

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| ID mint | Ranges / snowflake | Scale creates | Single AUTO_INCREMENT globally |
| Redirect SoT | KV/Cassandra/Dynamo-style | Massive read | Joins in normalized SQL on hot path |
| Cache | CDN + Redis | Absorb 99% | Hit SQL every redirect |
| Analytics | Async aggregate | Protect redirect | Sync INSERT click |
| Disable | 302 default + purge | Revocation works | 301 forever |
| Exact click counts | Approx OK | Cost | Strongly consistent global counter per click |

### 3.10 APIs

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/links` | Create (Idempotency-Key) |
| GET | `/v1/links/{id}` | Metadata for owner |
| PATCH | `/v1/links/{id}` | Update URL / disable |
| GET | `/v1/links/{id}/stats` | Aggregates |
| GET | `/{code}` | Public redirect |
| POST | `/v1/links:batch` | Bulk create |
| POST | `/v1/admin/takedown` | Trust & safety |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
        Creators / API partners              End users (clicks)
                 |                                    |
                 v                                    v
          +--------------+                    +---------------+
          | API Gateway  |                    | CDN / Edge    |
          | auth, RL     |                    | anycast       |
          +------+-------+                    +-------+-------+
                 |                                    |
        +--------+--------+                           |
        v                 v                           v
 +-------------+   +-------------+            cache hit? --yes--> 302/301 Location
 | Link Service|   | Alias Svc   |                   |
 +------+------+   +------+------+                  no
        |                 |                           v
        v                 v                    +--------------+
 +--------------------------------+            | Redirect Svc |
 | Mapping Store (sharded KV/SQL) |<-----------|             |
 +----------------+---------------+            +------+-------+
                  |                                   |
                  |                                   v
                  |                            +--------------+
                  |                            | Click Bus    |
                  |                            | (Kafka/log)  |
                  v                                   |
           +-------------+                            v
           | ID Allocator|                    +---------------+
           +-------------+                    | Aggregators   |
                                              | → OLAP/dash   |
           +-------------+
           | Abuse/Scan  |
           +-------------+
```

### 4.2 Sequence: create

```text
Client → API: POST /links {url, alias?, ttl?} + Idempotency-Key
API → validate + rate limit
API → (optional) sync denylist
API → ID Allocator: next_id / or check alias unique
API → Mapping Store: INSERT (durable)
API → ACK {short_url}
API → async: malware deep scan, cache warm optional
```

### 4.3 Sequence: redirect + analytics

```text
Browser → Edge: GET /aB3xY9k
Edge cache HIT → 302 Location: https://...
Edge → async log click
---
Edge MISS → Redirect Svc → Redis → miss → KV
KV → {url, status}
if DISABLED → 410
else → fill caches → 302
→ async click event (best effort)
```

### 4.4 Sequence: takedown

```text
Trust → Admin API: takedown(code)
→ Mapping status=DISABLED
→ Purge CDN key + Redis
→ Enqueue recheck similar URLs
Subsequent redirects fail closed
```

### 4.5 Scale cells

```text
Global Edge (shared)
Cell US | Cell EU | Cell APAC
  Link Service + Mapping shards + ID ranges
Async replicate mappings cross-cell
Redirect miss: local → if miss fetch home cell → populate
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable mapping:** no create ACK until quorum/replica write of code→URL.  
2. **Uniqueness:** `code` and `alias` globally unique (within domain).  
3. **Disable monotonicity:** DISABLED/EXPIRED does not silently return to ACTIVE without audit.  
4. **Redirect isolation:** click analytics failure never fails redirect.  
5. **Takedown visibility:** after purge, edge must not serve ACTIVE for disabled codes (bounded TTL worst case).  
6. **Idempotent create:** `(owner_id, idempotency_key)` unique.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Mapping store AZ down | Multi-AZ quorum; edge still serves cached |
| ID allocator down | Local cached ranges (prefetch); fail create if empty |
| Cache inconsistency after disable | Short TTL + explicit purge; epoch check |
| Kafka down | Drop/sample clicks; redirects OK |
| Malware scanner false negative | Continuous re-scan popular links; user reports |
| Split-brain two writers same code | Unique constraint + cell ownership of ID space |

**Cancel vs resume**

- **Disable:** soft takedown; reversible by owner/admin with audit.  
- **Delete:** hard delete rare; prefer disable for forensics.  
- **Resume:** explicit re-enable API; purge negative caches.

### 5.2 Scalability

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| 1× | Monolith API + Postgres + Redis; CDN in front |
| 10× | CDN mandatory; Kafka analytics; range IDs; read replicas |
| 100× | Sharded KV mappings; regional cells; stream aggs; bloom negative cache |
| 1000× | Global anycast; hot-key edge compute; hierarchical OLAP; dedicated viral tier |

**Hot-key handling**

```text
Detect: QPS(code) > threshold
Actions:
  - Pin at all edge PoPs with longer TTL while ACTIVE
  - Origin: local in-memory + never single-shard bottleneck (key is cached)
  - Analytics: sample 1/N clicks for that code
```

**Sharding key:** `hash(code)` for mappings; creates assign code then write to shard(code). Alias index may be global unique service or co-located.

### 5.3 Maintainability

- Versioned redirect policy (`redirect_code`, cache headers) via config flags.  
- Schema migrations online (expand/contract) for mapping attributes.  
- Chaos: kill origin, partition Kafka, flood 404 enumeration.  
- Clear reason codes: `AliasTaken`, `ReservedWord`, `UrlBlocked`, `Expired`, `Disabled`.  
- Audit every takedown and target URL change.

**Observability (must-have)**

- Metrics: create QPS, redirect QPS, cache hit ratio, origin p99, disable purge lag, analytics lag, 404 rate.  
- Top-N viral codes dashboard (careful: privacy).  
- Trace create: `link_id`, `code`, `owner_id`.  
- Alert: hit ratio drop, purge lag > SLO, ID range exhaustion.

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× — correct MVP**

```text
API + Postgres
CREATE: INSERT links (code base62 from sequence)
REDIRECT: Redis GET → else SELECT → SET Redis → 302
CLICK: fire-and-forget to local log / Redis INCR
CDN optional but recommended
```

First bottleneck: **Postgres on redirects** if cache cold; **sequence** on creates.

**10× — edge + async**

- CDN caches redirects; origin Redis; Kafka for clicks.  
- Range allocator: each API pod holds 10K IDs.  
- Aggregator workers write hourly rollups to ClickHouse-like store.

**100× — sharded KV + cells**

- Mapping in DynamoDB/Cassandra/FoundationDB-style; SQL for owner dashboards only.  
- Regional write cells; async replication.  
- Custom alias service with global unique index sharded by alias hash.  
- Abuse ML features from stream.

**1000× — internet scale**

```text
Anycast edge does almost all redirects
Origin protected by multi-layer cache
Creates: 500K QPS via many cells + ID coordination
Analytics: multi-tier rollup (edge minute → region hour → global day)
Special viral service: in-edge key-value for top 10K keys
```

### 5.5 Caching correctness deep dive

| Scenario | Policy |
|----------|--------|
| New link | Optional warm; or fill on first click |
| Update URL | Purge + short TTL; epoch++ |
| Disable | Purge; negative cache ACTIVE→DISABLED |
| 301 permanent | Avoid if disable likely; document irreversible browser cache |
| Unknown code | Negative cache briefly; rate limit |

**Deal-breaker:** caching 301 with `max-age=31536000` for user-generated links that can be weaponized.

### 5.6 Analytics correctness

| Requirement | Approach |
|-------------|----------|
| Approximate counts | Redis PFCount / sharded counters + flush |
| Unique visitors | HLL per (code, day) |
| Exact billing clicks | Stronger pipeline + dedupe cookies; costly |
| Dashboards | Pre-agg tables; not scan raw |

**Never** put unique visitor computation on the redirect mutex.

### 5.7 Security & multi-tenancy

- Authn for create/update; public redirect unauthenticated.  
- Do not leak owner PII on expand API without authz.  
- Encrypt long URLs at rest if containing tokens (users sometimes paste secrets—detect & warn).  
- SSRF: if preview-fetching destinations, block private IP ranges.  
- Tenant quotas on creates/day and custom aliases.

### 5.8 Ownership resolution (contradictions to avoid)

| Concern | Owner |
|---------|-------|
| Who mints codes | ID allocator / cell |
| What URL a code maps to | Mapping store (SoT) |
| What edge serves | Cache derived from SoT + TTL/purge |
| Click truth | Analytics pipeline (approx) |
| Takedown authority | Trust & safety + mapping status |

**Contradiction trap:** CDN as SoT without origin disable path.

### 5.9 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| Sync click write on redirect | Melts DB; raises p99 |
| UUID truncated to 6 chars | Collisions |
| Global single Postgres | Dies at 100× redirects |
| 301 + no purge | Cannot takedown phishing |
| Perfect real-time global counts | Unnecessary cost for MVP |
| Predictable sequential public IDs without RL | Enumeration / scraping |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| ID generation | Snowflake or range-allocated base62 + unique constraint |
| Redirect | Edge cache + 302 default; origin KV |
| Analytics | Async, approximate aggregates |
| Custom aliases | Separate unique namespace + reserved words |
| Multi-region | Active-active redirect; coordinated ID/write cells |
| Abuse | Rate limits + denylist + rapid disable/purge |

### 6.2 Top risks

1. Coupling analytics to redirect  
2. Wrong redirect caching (301) blocking takedown  
3. ID allocator SPOF  
4. Hot-key viral storms  
5. Alias/homoglyph abuse  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Requirements: 301 vs 302, analytics, custom aliases, abuse |
| 5–12 | API + data model + ID generation math |
| 12–22 | HLD: create vs redirect paths, cache |
| 22–32 | Scale: QPS split, sharding, edge, hot keys |
| 32–40 | Analytics pipeline + takedown consistency |
| 40–45 | Multi-region + wrap trade-offs |

---

## 7. Deeper / Related Interview Questions

### 7.1 ID generation

**Q: Why not hash(URL) as the code?**  
A: Collisions, inflexible (one code per URL), and attackers can probe. Prefer opaque IDs; optional dedupe layer separately.

**Q: How do range allocators survive crashes?**  
A: Persist allocated watermarks; on crash, skip remaining range (waste IDs, never double-issue). Waste is fine vs duplicates.

**Q: Snowflake clock skew?**  
A: Monotonic bit per worker; NTP hygiene; reject backward jumps; unique constraint backstop.

**Q: Base62 vs Base64?**  
A: Base62 URL-safe without encoding; Base64 needs URL-safe variant and careful padding.

### 7.2 Redirect & caching

**Q: When is 301 acceptable?**  
A: Truly immutable corporate redirects; not default for UGC shorteners with abuse risk.

**Q: How to handle cache stampede on cold viral link?**  
A: Singleflight/request coalescing at origin; probabilistic early refresh; pre-warm on create for paid.

**Q: Should edge compute run analytics?**  
A: Emit logs at edge; aggregate async. Keep edge logic minimal for reliability.

**Q: Negative caching risk?**  
A: Briefly caching 404 can hide a just-created link regionally—keep negative TTL short; creator read-your-write via origin.

### 7.3 Consistency

**Q: Create in US, click in EU 100ms later?**  
A: Replicate fast or on-miss fetch from home; edge fill. Document rare race → retry.

**Q: Read-your-write for creator?**  
A: Create response includes code; creator’s first redirect can sticky-route to write region or wait for quorum.

**Q: Update long URL races with redirect?**  
A: Version field; cache key includes version or purge on update.

### 7.4 Analytics

**Q: Exact count vs approximate?**  
A: Ask product. Marketing dashboards usually OK with <1% error; billing may need stronger dedupe.

**Q: How to count unique clickers privacy-safely?**  
A: Daily rotating hashes of IP+UA; HLL; retention limits; GDPR delete paths.

**Q: Bot traffic?**  
A: Filter known bots in aggregate; don’t let bots dominate rate limits for humans.

### 7.5 Abuse

**Q: How fast can you kill a phishing link?**  
A: Status disable + CDN purge; p99 < 60s for popular; worst case TTL bound for uncrawled PoPs.

**Q: Homograph aliases (`paypa1`)?**  
A: Confusable detection; ASCII-only aliases MVP; brand protection lists.

**Q: Spam creates?**  
A: Per-account quotas, device signals, slow mode, URL reputation, payment for high volume.

### 7.6 Data modeling

**Q: SQL or NoSQL for mappings?**  
A: MVP SQL fine; at high QPS KV wins for `Get(code)`. Keep owner listing in SQL/secondary index store.

**Q: Soft delete vs hard?**  
A: Soft for audit/abuse forensics; GC after retention.

**Q: How to shard 100B links?**  
A: Hash(code) into thousands of shards/cells; metadata cold tier for inactive.

### 7.7 Multi-region & DR

**Q: Active-active creates?**  
A: Only with partitioned ID space / cell ownership. Otherwise home-cell writes.

**Q: Region failure?**  
A: Edge continues from cache; misses route to healthy region; creates fail over with ID fence epoch.

### 7.8 Comparison questions

**Q: vs bit.ly / tinyurl?**  
A: Same core; interview wants ID uniqueness, cache, analytics async, abuse—not branding.

**Q: vs nginx map file?**  
A: Fine for 1K corporate redirects; not for UGC at 50M QPS.

**Q: Is this a good CDN use case?**  
A: Yes—classic edge caching with purge; design invalidation carefully.

### 7.9 Algorithms & data structures

**Q: Data structure for ID → URL?**  
A: Distributed KV; local LRU; CDN.

**Q: Bloom filter use?**  
A: Optional “code might exist” to cheapen negative lookups—watch false positives.

**Q: Rate limiter?**  
A: Token bucket per API key at gateway; separate harsher bucket for 404 storms.

### 7.10 Interview trap: units

**Q: 100B links × 300 bytes = ?**  
A: **30 TB**, not 30 PB. 1e11 × 300 = 3e13 B = 30 TB.

**Q: 1B clicks/day average QPS?**  
A: 1e9/86400 ≈ **11.6K/s**, not 1M/s. Peak apply 3–5×.

### 7.11 Reliability drills

**Q: Kafka down during Super Bowl ad?**  
A: Redirects continue; counts under-report; alert; backfill impossible if never buffered—accept or local disk spool.

**Q: Purge API fails?**  
A: Short TTL safety net; retry purge; mark `must_revalidate` on origin.

**Q: Duplicate codes issued?**  
A: Unique constraint rejects; retry mint; page trust if somehow served—treat as Sev-1.

### 7.12 Product edge cases

**Q: Password-protected links?**  
A: Edge can’t cache target freely; origin challenges; different product mode.

**Q: Geo-targeted destinations?**  
A: Edge logic or origin rules; cache key must include geo dimension or bypass cache.

**Q: Expiring links for docs?**  
A: `expires_at` checked origin-side; cache TTL ≤ remaining lifetime.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- links
(link_id UUID PK,
 code TEXT UNIQUE NOT NULL,          -- base62
 alias TEXT UNIQUE NULL,
 long_url TEXT NOT NULL,
 owner_id UUID NOT NULL,
 tenant_id UUID NOT NULL,
 status TEXT NOT NULL,               -- ACTIVE|DISABLED|EXPIRED
 redirect_code INT NOT NULL DEFAULT 302,
 expires_at TIMESTAMPTZ NULL,
 cache_epoch INT NOT NULL DEFAULT 1,
 idempotency_key TEXT NULL,
 created_at, updated_at,
 UNIQUE(owner_id, idempotency_key))

-- click_rollups
(code TEXT,
 bucket_start TIMESTAMPTZ,
 country TEXT,
 clicks BIGINT,
 PRIMARY KEY (code, bucket_start, country))

-- reserved_aliases(word TEXT PRIMARY KEY)
-- takedown_audit(link_id, reason, actor, ts)
```

### 8.2 API checklist

- [ ] `POST /v1/links` + Idempotency-Key  
- [ ] `GET /v1/links/{id}` owner metadata  
- [ ] `PATCH /v1/links/{id}` update/disable  
- [ ] `GET /v1/links/{id}/stats`  
- [ ] Public `GET /{code}` redirect  
- [ ] Admin takedown + purge  
- [ ] Batch create for partners  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Code | Opaque short id (base62) |
| Alias | Vanity path chosen by user |
| Mapping | Durable code/alias → long URL |
| Edge hit | CDN served redirect without origin |
| Purge | Explicit cache invalidation |
| Range allocator | Hands out ID blocks to writers |
| Hot key | Single code with disproportionate QPS |
| Fail closed (takedown) | Prefer deny redirect if status uncertain after disable |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Durable unique mapping, Redis cache, basic rate limits |
| 10× | CDN, async analytics, ID ranges |
| 100× | Sharded KV, cells, stream aggs, abuse automation |
| 1000× | Anycast edge, viral tier, hierarchical analytics, coordinated global IDs |

### 8.5 Redirect header sketch

```text
HTTP/1.1 302 Found
Location: https://example.com/target
Cache-Control: public, max-age=60
Surrogate-Key: link-aB3xY9k
X-Link-Epoch: 4
```

### 8.6 ID encoding sketch

```text
id: 64-bit snowflake
base62 encode → 11 chars max for 2^64; trim policy to fixed 8–10
reject codes in reserved set
on UNIQUE violation: mint again (rare)
```

### 8.7 Analytics rollup sketch

```text
edge minute counters → region hour → global day
HLL unique devices per (code, day)
retention: raw 7–30d, rollups 1–2y
```

### 8.8 Abuse state machine

```text
ACTIVE → (scanner|report) → UNDER_REVIEW → DISABLED
ACTIVE → (ttl) → EXPIRED
DISABLED → (admin) → ACTIVE  # audited
```

### 8.9 Interview “say this” summary (60 seconds)

> Durable unique short-code minting via range/snowflake IDs; redirects served from edge cache with 302 by default so takedowns work; origin KV protected by Redis; clicks emitted async and aggregated approximately; custom aliases in a separate unique namespace; creates scale via cells and coordinated ID spaces; never block redirects on analytics.

### 8.10 Extra traps

| Trap | Pushback |
|------|----------|
| Sync click INSERT | Redirect p99 dies |
| 301 default for UGC | Can’t revoke phishing |
| AUTO_INCREMENT multi-region | ID clashes / hotspot |
| Exact global counter | Unnecessary MVP cost |
| 100B×300B=30PB | **30TB** |
| Cache as SoT | Disable won’t stick |

### 8.11 Reliability test plan

1. Kill Kafka → redirects OK; metrics show undercount.  
2. Disable link → purge → all PoPs stop within SLO.  
3. Duplicate idempotency create → one link.  
4. Flood unknown codes → negative cache + RL; origin survives.  
5. Allocator crash → no duplicate IDs; creates resume with new ranges.  

### 8.12 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Redirect edge p99 | < 50ms |
| Redirect origin p99 (miss) | < 200ms |
| Cache hit ratio | > 95% |
| Create p99 | < 300ms |
| Takedown purge p99 | < 60s |
| Analytics lag p95 | < 5 min |

### 8.13 Related systems map

```text
API → Link Service → ID Allocator
                                     ↘
                                       Mapping Store ← Abuse/Takedown
                                     ↗
Edge → Redirect Svc → Cache
         ↓
      Click Bus → Aggregators → OLAP
```

### 8.14 Custom domain (Phase 2 hook)

```text
tenant custom domain CNAME → our edge
TLS cert automation
namespace: (domain, alias/code) unique
billing + verification before enable
```

### 8.15 Comparison: encoding lengths

| Len | Combinations | Notes |
|-----|--------------|-------|
| 6 | ~56B | Tight at huge scale; easier guess |
| 7 | ~3.5T | Comfortable for most |
| 8 | ~218T | Extra sparsity |

Prefer longer if product wants less enumeration, not because of capacity alone.

### 8.16 Write amplification note

```text
Create ACK requires: primary write (+ quorum)
Optional: replicate N regions async (not on critical path)
Cache warm optional
Deep malware scan async
```

### 8.17 NVIDIA interview angle

Classic backend question at NVIDIA for generalist SWE roles. Emphasize: **load class split**, **uniqueness under concurrency**, **cache invalidation for safety**, and **progressive scale**—same mental models as large config/registry systems in GPU fleets (unique IDs, hot keys, global cache).

---

*End of URL shortener system design.*
