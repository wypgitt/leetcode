# System Design: Pastebin

> **Focus areas:** High read:write ratio · Short IDs · Expiry/TTL · Private pastes · Object storage vs DB · CDN · Abuse/spam · Cost · Reliability · Progressive scale  
> **Style:** End-to-end content hosting design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct hot-path math, clear metadata vs blob split, deal-breakers for “everything in one SQL table” or “no abuse plan”, explicit Amazon ownership/cost/trust flavor  
> **Interview theme:** Amazon SDE III / L6 — design a **Pastebin-like** service (create/read pastes, short IDs, expiry, privacy) that you could operate: durable, cheap at read scale, hard to abuse

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

Goal: **bound the product**—a Pastebin-like service where users **create** text pastes, get a **short URL/ID**, **read** pastes quickly worldwide, optionally set **expiry** and **privacy**, with optional listing—optimized for a **very high read:write ratio**, low cost, and resistance to spam/abuse.

### 1.0 What this is / is not

| Dimension | **Pastebin (this doc)** | Not this |
|-----------|-------------------------|----------|
| Primary job | Create & fetch immutable-ish text blobs via short IDs | Google Docs collaborative editing |
| Success | Fast global reads, correct expiry/privacy, low cost/abuse | Perfect full-text search of all pastes |
| Entities | Paste, paste_id, owner (optional), visibility, TTL | Nested folders, complex ACLs enterprise |
| Read path | CDN + cache + object store | Always hit primary DB for body |
| Write path | API → metadata DB + blob store | Client uploads straight to random disk |
| Abuse | Rate limits, scanning, takedown | Ignore illegal content / spam SEO |
| Amazon lens | Ownership, cost per GB/request, reliability, customer trust | Clever encoding trivia only |

**Scope statement:** Design Pastebin: create/read pastes, short IDs, expiry, private pastes, optional listing, CDN-accelerated reads, object storage for bodies, metadata store, abuse controls—scaled 10×/100×/1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Create paste? | Yes — text body, optional title, language/syntax | Write API + storage split |
| F2 | Read by ID? | Yes — primary UX | Hot read path |
| F3 | Short IDs? | Yes — short, URL-safe, hard to enumerate if private | ID generation scheme |
| F4 | Expiry? | Optional TTL: 1h, 1d, 1w, never (or max cap) | TTL index / lifecycle |
| F5 | Private pastes? | Unlisted (secret URL) and/or password / account-only | Visibility + authz |
| F6 | Edit after create? | Usually immutable; optional edit token | Simpler cache; version if edits allowed |
| F7 | Delete? | Owner/admin delete; expiry auto-delete | Lifecycle jobs |
| F8 | Paste listing? | Optional — “my pastes” for logged-in; public recent feed optional/out | Secondary index; abuse magnet |
| F9 | Accounts? | Optional for MVP; anonymous OK with tighter limits | Auth service optional |
| F10 | Size limit? | e.g. 1 MB text default | Enforce at API; cost control |
| F11 | Syntax highlight? | Client-side from language tag | Don’t run heavy render server-side MVP |
| F12 | Raw vs rendered? | `/raw/id` and HTML view | Same blob; different content-type |
| F13 | Burn after read? | Nice-to-have | Special TTL semantics + cache care |
| F14 | Search? | Out of MVP or simple title search for “my pastes” | Avoid global public search MVP |
| F15 | Abuse reports / takedown? | Yes | Trust queue + enforce |

**MVP functional scope:**

1. `POST /pastes` — create paste (body, expiry, visibility, optional password).  
2. `GET /pastes/{id}` — fetch paste (authz for private).  
3. `GET /pastes/{id}/raw` — raw text.  
4. Short unique IDs in URLs.  
5. Expiry enforced (not serve after TTL).  
6. Unlisted/private pastes (secret ID ± password).  
7. Optional: authenticated “my pastes” list.  
8. Rate limiting + basic content safety hooks.  
9. CDN/cache for public pastes.  
10. Metrics, alarms, takedown path.

**Out of MVP:**

- Real-time collaborative editing  
- Global public search / SEO sitemap of all pastes  
- Binary file hosting (images/video) as primary product  
- Enterprise SSO / complex org ACLs  
- Guaranteed permanent legal archive  
- Running user-supplied scripts server-side

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Read latency | Global users | p99 < 100–200 ms via CDN for hot public |
| N2 | Write latency | Create paste | p99 < 200–300 ms |
| N3 | Availability | Reads critically | 99.99% read; 99.9% write |
| N4 | Durability | Don’t lose pastes | 11 9s class via object store |
| N5 | Read:write ratio | Very high | 100:1 to 1000:1 typical |
| N6 | Consistency | Read-your-write after create | Sticky/cache bypass on create redirect |
| N7 | Expiry correctness | Must not leak past TTL | Strong enough for privacy promises |
| N8 | Enumeration resistance | Private IDs | Large ID space + rate limit |
| N9 | Cost | Dominated by egress/storage | Lifecycle delete; cache hit ratio |
| N10 | Abuse resilience | Spam/malware pastes | Limits, scanning, blocklists |
| N11 | Scalability | Progressive | See scale table |
| N12 | Operability | Clear ownership | Runbooks, idempotent writes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Anonymous user pastes logs → gets `https://paste.example/Ab3xY9` → shares link → friends read via CDN.  
2. User sets expiry 24h → after TTL, GET returns 404/gone; storage reclaimed.  
3. User creates **unlisted** paste → ID not in public lists; only holder of URL can fetch.  
4. User creates **password-protected** paste → GET returns challenge; correct password returns body.  
5. Logged-in user lists “my pastes” → paginated metadata without pulling all bodies.  
6. Admin takedown → paste tombstoned; CDN purged.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate create retry | Idempotency-Key → same paste_id |
| Extremely hot paste (HN/Reddit) | CDN + origin shield; collapse requests |
| Expired paste still in CDN | Cache-Control aligned to remaining TTL; purge on expiry job |
| Burn-after-read + CDN | Generally **bypass CDN** or short-circuit at origin with single-flight delete |
| Private paste ID leaked | Password optional; rotate/delete; treat as secret capability URL |
| ID enumeration | Long enough IDs; rate limit 404s; CAPTCHA/ ban |
| Huge body (zip bomb text) | Max size; compression limits; timeout |
| Unicode / binary disguised as text | Content-type sniff carefully; store as bytes; XSS escape on HTML view |
| XSS in HTML view | Escape; CSP; raw endpoint separate |
| Malware / phishing paste | Async scan; blocklist; report button |
| Spam SEO farms | Rate limit; account tier; noindex; disable public listing |
| Region outage | Multi-AZ; optional multi-region read replicas / multi-region bucket |
| Metadata DB available, object store slow | Create fails closed or async upload with pending state |
| Clock skew on expiry | Store `expires_at` absolute; use consistent time source |
| User deletes while cached | Explicit purge / short TTL for mutable metadata |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Pastes created / day | 1M | 10M | 100M | 1B |
| Peak writes / s | 50 | 500 | 5K | 50K |
| Reads / day | 200M | 2B | 20B | 200B |
| Peak reads / s | 10K | 100K | 1M | 10M |
| Read:write | ~200:1 | similar | similar | similar |
| Avg paste size | 5 KB | 5 KB | 5 KB | 5 KB |
| Stored working set | ~50 TB | 500 TB | 5 PB | 50 PB |
| Public hot keys | 1K | 10K | 100K | 1M |
| CDN cache hit ratio | 85–95% | 90%+ | 90%+ | edge+shield |
| Active accounts | 5M | 50M | 500M | — |

**What each jump forces:**

- **10×:** CDN mandatory; metadata DB indexed carefully; lifecycle rules for expiry.  
- **100×:** Shard metadata; multi-region reads; object store lifecycle + Intelligent-Tiering analogues; abuse automation.  
- **1,000×:** Cell/partition by ID; origin shields; maybe dedicated hot-key service; aggressive cold tiering; spam ML at ingest.

### 1.5 Etc. (Constraints & Assumptions)

- Pastes are **mostly immutable**; immutability makes caching and CDN trivial—preserve this.  
- **Capability URLs** (unlisted IDs) are a privacy model, not cryptographically perfect secrecy—state that.  
- Egress cost can dominate; **cache hit ratio** is a first-class SLO.  
- Public “recent pastes” feeds are **abuse magnets**—default off or tightly gated.  
- Ownership: one team owns paste API + metadata; storage platform is a dependency with clear SLAs.  
- Customer trust: private/expired pastes must not resurface; XSS must not steal sessions on our domain.

**Scope statement to repeat back:**

> Design a Pastebin service: users create text pastes with short IDs, optional expiry and privacy; reads dominate and are served via CDN/cache from object storage while metadata lives in a scalable DB; support optional “my pastes” listing; enforce size/rate limits and abuse controls; scale 10×/100×/1,000× with clear cost and reliability ownership.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 10× | Notes |
|-------|------|---------------|-----|-------|
| W — Create | Writes | 50/s | 500/s | Metadata + blob put |
| R — Read origin | Cache misses | 500–1500/s | 5–15K/s | After 85–95% CDN hit |
| R — Read edge | CDN | 10K/s | 100K/s | Dominates |
| L — List my pastes | Auth reads | low | medium | Metadata only |
| X — Expiry/GC | Batch/lifecycle | continuous | — | Storage reclaim |
| A — Abuse scan | Async | ~write rate | — | Nearline |

**Interview tip:** Always derive **origin QPS** from CDN hit ratio. Saying “10K read QPS hits MySQL” is a classic fail.

### 2.2 Storage math (baseline)

| Item | Math | Result |
|------|------|--------|
| New data/day | 1M × 5 KB | ~5 TB/day raw bodies |
| With redundancy | ×3 (example erasure/replication accounting) | depends on store |
| Metadata/day | 1M × ~200 B | ~200 MB/day |
| Yearly bodies (if never expire) | 5 TB × 365 | ~1.8 PB/year — **why TTL matters** |
| Assume 50% expire ≤ 30d | Working set much smaller | Lifecycle critical |

**Punch line:** Without expiry/lifecycle, storage cost explodes. TTL is a **cost feature**, not only UX.

### 2.3 Bandwidth math

| Path | Baseline |
|------|----------|
| Egress if no CDN | 200M reads × 5 KB ≈ 1 PB/day — absurd $ |
| With 90% CDN hit | Origin egress ~10% → still large but manageable |
| Ingress writes | 5 TB/day |

Emphasize: **CDN + cache-control + compression (gzip/brotli)** are economic necessities.

### 2.4 Short ID space

| ID design | Space | Notes |
|-----------|-------|-------|
| 6 char base62 | 62^6 ≈ 56.8B | OK early; enumeration risk for private |
| 8 char base62 | 62^8 ≈ 2.18e14 | Comfortable |
| 10 char base62 | ~8.4e17 | High security margin for unlisted |
| UUID | 122 bits | Not “short”; ugly URLs |

**Collision:** For 1M/day with 8-char base62, birthday collision risk negligible for years; still use **insert-if-not-exists** retry.

**Private pastes:** prefer longer IDs (e.g. 10–12 chars) or random 64+ bit tokens—**security through capability URL entropy**.

### 2.5 Latency budget

**Create**

| Step | Budget |
|------|--------|
| Auth / rate limit | 5–10 ms |
| Validate + ID gen | 1–5 ms |
| Metadata write | 10–30 ms |
| Object put | 20–80 ms |
| Total p99 | ≤ 200–300 ms |

Optimize: parallel metadata+blob where safe; or put blob then commit metadata (see consistency).

**Read (CDN miss)**

| Step | Budget |
|------|--------|
| Authz / metadata get | 5–20 ms |
| Object get | 20–60 ms |
| Total origin | ≤ 100 ms regional |

**Read (CDN hit):** tens of ms edge.

### 2.6 Cache math

Assume peak 10K reads/s, 90% hit → 1K origin/s.  
Metadata cache (Redis) for hot IDs: 1K hot pastes × 1 KB meta = trivial memory.  
Body cache: popular pastes at edge; origin shield collapses stampedes.

### 2.7 Scale jump worksheet

| Jump | Writes/s | Reads/s | Origin @90% hit | Metadata strategy |
|------|----------|---------|-----------------|-------------------|
| Base | 50 | 10K | 1K | Single region primary + replicas |
| 10× | 500 | 100K | 10K | Read replicas; Redis; CDN shield |
| 100× | 5K | 1M | 100K | Shard metadata by paste_id |
| 1,000× | 50K | 10M | 1M | Cells; multi-region active; tiered storage |

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Correctness of privacy & expiry** — trust promise.  
2. **Cheap global reads** — CDN, immutability, high hit ratio.  
3. **Durable writes** — no silent loss after 200 OK.  
4. **Operable ownership** — clear boundaries, alarms, lifecycle.  
5. **Abuse-resistant** — rate limits, scanning, takedown.  
6. **Simple MVP, scalable seams** — don’t overbuild CRDT editors.

### 3.2 Core components

| Component | Responsibility | Why |
|-----------|----------------|-----|
| Paste API | Create/read/delete/list | Stateless app tier |
| ID Generator | Short unique IDs | Centralize collision handling |
| Metadata Store | paste_id → attrs, expiry, visibility, blob pointer | Queryable, transactional |
| Object / Blob Store | Paste bodies | Cheap, durable, scalable |
| Cache (Redis) | Hot metadata ± small bodies | Cut DB/object QPS |
| CDN | Edge cache public/unlisted GETs | Egress + latency |
| Auth Service | Optional accounts, sessions | “My pastes”, private |
| Expiry / Lifecycle | Delete/orphan cleanup | Cost + privacy |
| Abuse / Safety | Rate limit, scan, report | Trust |
| Admin / Takedown | Tombstone + purge | Legal/ops |

### 3.3 Object storage vs DB (say this clearly)

| Data | Store | Why |
|------|-------|-----|
| Body (text bytes) | **Object store** (S3-class) | Large, immutable, cheap, lifecycle policies |
| Metadata | **DB** (DynamoDB / Aurora / etc.) | Conditional writes, queries by owner, expiry indexes |
| Hot metadata | **Redis** | Micro-latency |
| Public body hot | **CDN** | Edge |

**Deal-breaker:** stuffing multi-KB/MB bodies into a relational row for every paste → backup, bloat, buffer pool death.

**Deal-breaker:** only object store with no metadata index → can’t list “my pastes”, can’t efficient expiry query, awkward password flags.

### 3.4 API sketch

```text
POST   /v1/pastes
  Headers: Idempotency-Key?, Authorization?
  Body: { content, title?, language?, visibility, password?, expires_in? }
  → 201 { paste_id, url, expires_at }

GET    /v1/pastes/{id}
  Headers: Authorization?, X-Paste-Password?
  → 200 { metadata..., content } | 401 | 403 | 404

GET    /v1/pastes/{id}/raw
  → text/plain

DELETE /v1/pastes/{id}
  → 204

GET    /v1/me/pastes?cursor=
  → { items: [metadata...], next_cursor }

POST   /v1/pastes/{id}/report
  → 202
```

### 3.5 Data model

```text
PasteMeta:
  paste_id (PK)
  owner_id? (GSI)
  title?
  language?
  visibility: public | unlisted | private | password
  password_hash?
  blob_key
  size_bytes
  content_type
  created_at
  expires_at?
  burn_after_read: bool
  status: active | tombstoned | pending_scan
  version
  etag / content_sha256

PasteBody (object):
  key = blob_key (e.g. pastes/{shard}/{paste_id})
  bytes
  metadata headers: sha256, content-type
```

### 3.6 ID generation options

| Approach | Pros | Cons | Pick when |
|----------|------|------|-----------|
| Crypto random base62 | Simple, unguessable | Needs uniqueness check | **Default** |
| Hash(content) | Dedup | Collides different users’ secrets; privacy leak | Rarely for public only |
| Snowflake + encode | Ordered | Guessable sequences | Avoid for unlisted |
| Pre-generated ID pools | Fast | Ops complexity | Ultra-high write |

**Recommendation:** `secure_random` → base62 of length L (8 public, 10–12 unlisted) → conditional put metadata; retry on conflict.

### 3.7 Create-flow consistency options

| Strategy | Pros | Cons |
|----------|------|------|
| A: Write blob then metadata | Readers never see meta without body | Orphan blobs if meta fails |
| B: Write metadata pending then blob then active | Clear state machine | More complex reads |
| C: DB stores small bodies inline < N KB | Fewer RTTs | Hybrid complexity |

**Choose A or B.** Prefer **B** at Amazon scale for operability: `pending` → upload → `active`. GC orphans with lifecycle on prefix + sweeper.

Never return 201 until paste is **readable** (or return 202 accepted with poll—usually worse UX).

### 3.8 Read path & CDN

**Public / unlisted immutable pastes:**

```text
Client → CDN → (miss) Origin API → Cache → Metadata DB
                              ↓
                         Object Store → (cache & edge)
```

Cache-Control example:

- If `expires_at` null: `public, max-age=3600, immutable` (if truly immutable)  
- If TTL known: `public, max-age=min(3600, remaining_ttl)`  
- Password/private: `private, no-store` at CDN (origin only)

**Private / password:** do not cache body at shared CDN without varying on auth—usually **CDN bypass** or signed URL short TTL.

### 3.9 Expiry design

| Mechanism | Role |
|-----------|------|
| `expires_at` in metadata | Authoritative check on read |
| Cache max-age ≤ remaining TTL | Prevent CDN resurrection |
| Object lifecycle / sweeper | Delete blob after expiry + grace |
| Optional DynamoDB TTL / scheduled job | Delete metadata |
| Tombstone short period | Soft delete for abuse investigations |

**Burn after read:** origin transaction: read → mark deleted → purge caches; **disable CDN** or use signed single-use URLs.

### 3.10 Privacy model

| Visibility | Listing | Fetch requirement |
|------------|---------|-------------------|
| public | May appear in public feeds (if enabled) | Anyone with ID |
| unlisted | No public lists | Secret ID (capability URL) |
| password | No lists | ID + password |
| private | Owner list only | AuthN as owner (or ACL) |

**Enumerate:** rate-limit failed GETs per IP/API key; WAF; longer IDs for non-public.

### 3.11 Optional paste listing

- **My pastes:** GSI/`owner_id + created_at` — safe if authz correct.  
- **Public recent:** globally ordered feed — **spam magnet**; if required, separate service with heavy moderation, noindex, rate limits, and probably not MVP.

### 3.12 Tradeoffs table

| Decision | Options | Choose | Why | Deal-breaker |
|----------|---------|--------|-----|--------------|
| Body storage | SQL vs object store | **Object store** | Cost/scale | SQL bodies at PB |
| ID type | Sequential vs random | **Random base62** | Unguessable | Auto-inc IDs for unlisted |
| CDN for all | Yes vs selective | **Public/unlisted only** | Auth caching hard | CDN-cache password pastes shared |
| Public feed | Yes vs no | **No in MVP** | Abuse/cost | Unmoderated public firehose |
| Sync scan on write | Inline vs async | **Async + pending for risky** | Latency | Blocking AV on every write without need |
| Multi-region active-active | Yes vs primary+CRR | Start **single primary writes** + CRR reads | Conflict simplicity | Multi-writer without cells |

### 3.13 Abuse / spam controls (MVP+)

1. **Rate limits:** per IP, per account, per CIDR; stricter for anonymous.  
2. **Size & complexity limits:** max bytes, max lines.  
3. **CAPTCHA** on anonymous after threshold.  
4. **Async content scan:** malware URLs, phishing, known bad payloads.  
5. **noindex** headers for unlisted; robots policy.  
6. **Report + takedown** workflow; block re-upload via hash.  
7. **WAF / bot management** on create.  
8. Disable or gate **public listing** and search.  
9. Account reputation tiers (trusted publishers).  
10. Cost anomaly alerts (egress spike = hot abuse).

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
                     +------------------+
   Users/Browsers →  |       CDN        |  (public/unlisted GETs)
                     +--------+---------+
                              | miss / non-cacheable
                              v
                     +------------------+
                     |  Paste API (ASG) |  ← WAF / Rate limiter
                     +--------+---------+
                              |
           +------------------+------------------+
           |                  |                  |
           v                  v                  v
   +---------------+  +---------------+  +----------------+
   | Metadata DB   |  | Redis Cache   |  | Object Store   |
   | (Dynamo/SQL)  |  | meta/hot body |  | (S3-class)     |
   +---------------+  +---------------+  +----------------+
           |
           | owner_id GSI
           v
   +---------------+     +------------------+
   | Auth Service  |     | Expiry Sweeper / |
   | (optional)    |     | Lifecycle rules  |
   +---------------+     +--------+---------+
                                  |
                                  v
                         +------------------+
                         | Abuse Scan Workers|
                         | Report Queues     |
                         +------------------+
```

### 4.2 Create sequence

```text
Client        API          RateLimit     MetaDB        ObjectStore     Queue
  |            |               |           |               |             |
  |--POST----->|--check------->|           |               |             |
  |            |--gen id------>|--put pending------------->|             |
  |            |               |           |--put blob---->|             |
  |            |               |           |--activate---->|             |
  |            |               |           |               |--scan msg-->|
  |<--201 id---|               |           |               |             |
```

### 4.3 Read sequence (public, CDN miss)

```text
Client    CDN       API       Redis      MetaDB     ObjectStore
  |--GET-->|         |          |          |           |
  |  miss  |--GET--->|--meta--->|          |           |
  |        |         |  miss    |--get---->|           |
  |        |         |<-meta----|<---------|           |
  |        |         |--get body---------------------->|
  |        |         |<---------bytes------------------|
  |        |<-200----| (set cache)                     |
  |<-200---| cache for remaining TTL                   |
```

### 4.4 Expiry / GC

```text
  Sweeper / TTL stream
        |
        v
  Find expired meta → mark tombstone → purge Redis → CDN purge API
        |
        v
  Delete object (or lifecycle rule on expires header / tag)
        |
        v
  Hard-delete meta after grace
```

### 4.5 Cell architecture at 100×+

```text
                 Global Router (by paste_id hash or region affinity)
                     |
     +---------------+---------------+
     |               |               |
  Cell A          Cell B          Cell C
  API+Meta+Redis  API+Meta+Redis  API+Meta+Redis
     \               |               /
      \              |              /
         Multi-region Object Store / CRR
```

Writes go to cell owning ID prefix; reads follow; CDN in front globally.

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **200/201 create ⇒ subsequent GET succeeds** (same region) until expiry/delete.  
2. **Expired ⇒ not serve body** (metadata check wins even if blob remains briefly).  
3. **Tombstoned ⇒ 404/410** everywhere after purge propagation budget.  
4. **Idempotent create** with Idempotency-Key.  
5. **Password pastes** never logged in plaintext; hashes only (Argon2/bcrypt).

#### 5.1.2 Failure modes

| Failure | User impact | Mitigation |
|---------|-------------|------------|
| Object store outage | Creates fail; cached reads OK | Multi-AZ store; defer noncritical |
| Metadata DB outage | Creates/reads miss cache fail | Read replicas; cache hot; degrade list |
| CDN outage | Origin absorbs traffic | Origin shield; autoscaling; load shed |
| Cache stampede | DB melt on viral paste | Single-flight / request collapsing |
| Partial create | Orphan blob or pending forever | Sweeper; pending TTL |
| Bad deploy XSS | Account compromise risk | CSP, escape, rapid rollback |

#### 5.1.3 Durability & backup

- Object store: cross-AZ durability; optional CRR.  
- Metadata: PITR backups; continuous exports.  
- Test restore quarterly (ownership).  
- Soft-delete grace for accidental owner deletes.

#### 5.1.4 Consistency nuances

- After create, client follows redirect/URL; may hit other POP before edge knows—OK for immutable content once origin has it; for read-your-write, return body inline on create response.  
- Metadata update (tombstone) vs CDN: use purge + short max-age; for password changes, no shared cache.  
- Listing “my pastes” is **read-after-write** via primary or consistent read option.

#### 5.1.5 Security

- HTML view: escape all content; strict CSP; separate raw domain optional (`paste-raw.`) to isolate cookies.  
- HTTPS only; HSTS.  
- Secrets in URLs land in Referer logs—`Referrer-Policy` and caution on third-party images (n/a for text).  
- Admin actions audited.

### 5.2 Scalability

#### 5.2.1 Read path scaling (the main game)

```text
Edge CDN → Origin Shield → API → Redis → Meta → Object Store
```

Techniques:

- Immutability ⇒ long cache lifetimes (bounded by TTL).  
- Compression at edge.  
- Partition object keys for even prefix load.  
- Hot key: ensure CDN hit; shield absorbs miss herd.  
- Separate **control plane** (meta) from **data plane** (bytes).

#### 5.2.2 Write path scaling

- Stateless API autoscaling on CPU/RPS.  
- Metadata store: choose DynamoDB-style partition key `paste_id` for even load; or sharded MySQL.  
- Avoid global secondary indexes that hotspot on `created_at` for public feeds.  
- Async scan workers scale with queue depth.

#### 5.2.3 Metadata store choice (interview depth)

| Option | When | Tradeoff |
|--------|------|----------|
| DynamoDB | High scale, simple PK access | Listing needs GSI; TTL feature handy |
| Aurora/MySQL | Richer queries, smaller scale | Shard at 100× |
| Cassandra | Wide write | Ops heavier; TTL native |

**Amazon interview flavor:** DynamoDB + S3 is a very natural combo; defend it with access patterns: `GetItem(paste_id)`, `Query(owner_id)`, TTL.

#### 5.2.4 Expiry at scale

| Scale | Approach |
|-------|----------|
| 10× | Periodic sweeper + object lifecycle tags |
| 100× | Native TTL on metadata; S3 lifecycle by prefix/date |
| 1,000× | Tiered storage; aggressive expire defaults; paid “retain forever” |

Grace period: keep blob 24h after expiry for clock/CDN edge cases, but **serve path must 404**.

#### 5.2.5 Multi-region

| Mode | Pattern |
|------|---------|
| MVP | Single region write; CDN global |
| Growth | Object CRR; metadata global tables / DAX-style / regional read replicas |
| 1,000× | Cells per region; ID includes region or hash routing |

Conflict avoidance: **single-writer ownership** per paste_id.

#### 5.2.6 Cost controls (talk like an owner)

| Cost driver | Control |
|-------------|---------|
| Egress | CDN hit ratio SLO; compression |
| Storage | Default TTLs; lifecycle; deny forever for anon |
| Request volume | Cache meta; coalesce |
| Scan compute | Sample low-risk; full scan suspicious |
| Small-object overhead | Optionally pack tiny pastes (<2KB) in metadata store or chunk store |

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Component | Owns | Pager |
|-----------|------|-------|
| Paste API | Contracts, validation, authz | 5xx, latency |
| Metadata | Schema, GSI, TTL | Throttles, errors |
| Blob/storage config | Bucket policies, lifecycle | 403/slow GETs |
| CDN config | Cache behaviors, purge | Hit ratio drop |
| Abuse | Limits, scanners, takedown | Spam waves |
| Lifecycle workers | Orphan GC | Storage growth anomaly |

#### 5.3.2 Safe evolution

- Version API (`/v1`).  
- Additive metadata fields.  
- Blob key versioning if encryption scheme changes.  
- Feature flags for burn-after-read, public feed.

#### 5.3.3 Observability & SLOs

| SLO | Example target |
|-----|----------------|
| Read availability (incl. CDN) | 99.99% |
| Origin read p99 | < 100 ms |
| Create p99 | < 300 ms |
| CDN hit ratio (public) | > 90% |
| Expiry correctness (audit) | 99.999% (sampled) |
| Orphan blob rate | < 0.1% with GC lag < 24h |
| Abuse create block rate | monitored, not SLO flex |

Metrics: creates, reads, 404 rate, password fail rate, purge latency, storage bytes, $ egress, scan verdicts.

#### 5.3.4 Abuse deep dive

**Threats**

- Spam SEO / phishing kits hosted as pastes  
- Malware droppers (encoded)  
- Hate/illegal content  
- Storage DoS (many large pastes)  
- Egress DoS (viral hotlinking)  
- ID scanning for private pastes  

**Controls layered**

```text
WAF → Rate limit → Account tier → Size limits
     → Async ML/URL scan → Hash blocklist
     → Report/takedown → CDN purge → Ban
```

**Hotlink / egress abuse:** require referrer checks? usually not; prefer auth for private and CDN cost alerts; rate-limit origin; consider signed URLs for non-public.

**Legal trust:** retain takedown audit; ability to preserve under legal hold (override GC).

#### 5.3.5 XSS & content hosting trust

Serving user HTML on primary domain is dangerous. Patterns:

1. **Default:** render as escaped text / `<pre>`.  
2. Syntax highlight client-side from text nodes.  
3. Optional `raw` on separate origin without cookies.  
4. Never `eval` user content server-side.

#### 5.3.6 Progressive scale checklist

**10×**

- CDN in front of all public GETs  
- Redis metadata  
- Lifecycle expiry  
- Idempotency keys  
- Basic rate limits  

**100×**

- Shard / Dynamo partition strategy validated  
- Origin shield  
- Async abuse ML  
- Multi-AZ + backups tested  
- “My pastes” pagination only (no global feed)  

**1,000×**

- Cell architecture  
- Tiered storage / intelligent tiering  
- Dedicated hot-object path  
- Regional write cells  
- Automated spam economy crushing (cost to create)  

### 5.4 Deep dive: password-protected pastes

```text
Create: password → KDF (Argon2id) → store hash + params; body encrypted optional
Read:  verify password → fetch body
CDN:   Cache-Control: private, no-store
Optional: encrypt body with key derived from password (zero-knowledge-ish)
          tradeoff: cannot server-scan content; product decision
```

If body encrypted client-side, abuse scanning weakens—discuss tradeoff explicitly.

### 5.5 Deep dive: burn after read

```text
GET → begin txn / conditional update status active→consumed
    → if success, return body once
    → async purge CDN (shouldn’t be cached) + delete blob
Race: two parallel GETs — only one wins conditional; other 404
```

Distributed race needs conditional writes on metadata (`version` or `status`).

### 5.6 Deep dive: caching policy matrix

| Visibility | CDN | Redis body | Redis meta |
|------------|-----|------------|------------|
| public | yes | optional | yes |
| unlisted | yes (secret URL) | optional | yes |
| password | no | no | meta without secrets |
| private | no | no | yes (authz) |
| burn-after-read | no | no | careful |

### 5.7 Deep dive: create atomicity state machine

```text
        +--> FAILED (retryable)
        |
CREATED_PENDING --> BLOB_WRITTEN --> ACTIVE --> EXPIRED --> TOMBSTONED
        |                               |
        +-------- GC orphans -----------+---- DELETED
                                        |
                                     CONSUMED (burn)
```

API only redirects clients to ACTIVE (or returns content).

### 5.8 Testing & resilience

| Test | Purpose |
|------|---------|
| Contract tests | API idempotency, authz matrix |
| Chaos: kill Redis | Fall back to DB |
| Chaos: object latency | Timeouts + client errors |
| Expiry audit job | Sample expired IDs must 404 |
| Load: viral key | Hit ratio + shield |
| Security: XSS fuzz | HTML view |
| Privacy: enumeration | 404 timing roughly constant |

### 5.9 Comparison: TinyURL vs Pastebin (interview pivot)

| | TinyURL | Pastebin |
|--|---------|----------|
| Value | Redirect map | Store & serve body |
| Payload | Tiny meta | KB–MB bodies |
| Storage | DB enough | **Object store** |
| CDN | Cache 302/301 | Cache **bytes** |
| Abuse | Phishing links | Phishing **content** + storage |

Don’t design Pastebin as “TinyURL with a string column.”

### 5.10 Amazon leadership connection (brief)

- **Ownership:** you alarm on storage growth and hit ratio, not only 5xx.  
- **Frugality:** default TTLs, CDN, object lifecycle.  
- **Customer trust:** expiry/privacy correctness > flashy features.  
- **Bias for action:** MVP without public feed; add when abuse story exists.  
- **Dive deep:** know why orphan blobs happen and how GC fixes them.

---

## 6. Wrap-Up

### 6.1 30-second recap

> Pastebin splits **metadata** (DB) from **bodies** (object store). Creates generate unguessable short IDs, write blob + activate metadata, then reads are dominated by **CDN** thanks to immutability. Expiry is enforced on the read path and reclaimed by lifecycle jobs. Private/password pastes bypass shared caches. Listing is “my pastes,” not a public firehose. Abuse is controlled with rate limits, scanning, and takedown. Scale by caching first, then sharding/cells, while watching **egress and storage cost**.

### 6.2 Key tradeoffs

| Tradeoff | Choice |
|----------|--------|
| SQL body vs object store | Object store |
| Short vs safe IDs | Longer for unlisted |
| CDN everything vs selective | Cache public/unlisted only |
| Public feed vs abuse | Omit in MVP |
| Inline vs async scan | Async (+ hold if risky) |
| Forever storage vs cost | Default TTLs |

### 6.3 Risks & follow-ups

- Capability URL leaks via referrers/logs  
- CDN purge lag vs expiry  
- Multi-region write conflicts if rushed  
- Encryption-at-rest vs password zero-knowledge scanning tradeoff  
- Legal holds vs lifecycle deletion  

### 6.4 What “good” looks like

- Clarified privacy modes and size/TTL caps  
- Did **back-of-envelope** including CDN hit ratio and storage with TTL  
- Drew metadata vs blob vs CDN  
- Called out **burn-after-read** and **password** caching pitfalls  
- Abuse and cost as first-class  
- Progressive scale without magic

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q1 | Anonymous creates allowed? | Yes with strict rate limits |
| Q2 | Max paste size? | Enforce (e.g. 1MB); paid tiers higher |
| Q3 | Editable pastes? | Prefer immutable; edit token if needed busts cache |
| Q4 | Custom URLs? | Abuse-heavy; authenticated only later |
| Q5 | Syntax highlight server-side? | Client-side MVP |
| Q6 | Version history? | Out of MVP |
| Q7 | Cloning paste? | Copy-on-write new ID |
| Q8 | Analytics on views? | Privacy tradeoff; approximate counters async |
| Q9 | GDPR delete? | Delete meta+blob; purge CDN |
| Q10 | Multi-file paste? | Later; zip or multiple blob keys |
| Q11 | Paste comments? | Separate system; abuse surface |
| Q12 | SLA for expiry exactness? | Read-path enforce; GC eventual |

### 7.2 IDs & privacy (Q13–Q24)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q13 | Why not auto-increment? | Enumerable |
| Q14 | How long should IDs be? | Birthday bound + adversarial enumeration |
| Q15 | Hash of content as ID? | Cross-user leakage / dedup ethics |
| Q16 | Unlisted vs password? | Capability URL vs shared secret |
| Q17 | Is unlisted secure? | High entropy + HTTPS + rate limit; not ACL |
| Q18 | Prevent timing attacks on ID existence? | Uniform 404 responses where possible |
| Q19 | Rotate ID after leak? | New paste / delete old |
| Q20 | Signed URLs? | Good for private temporary access |
| Q21 | Password storage? | KDF; never plaintext |
| Q22 | Encrypt body with password? | Privacy vs scanning tradeoff |
| Q23 | Can CDN cache unlisted? | Yes if URL secret; still risk via logs |
| Q24 | Private paste sharing to friend? | Explicit ACL or password |

### 7.3 Storage & caching (Q25–Q40)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q25 | Why not put 5KB in DynamoDB item? | Works for tiny; object store cleaner at scale/size caps |
| Q26 | When inline metadata storage? | Very small pastes optimization |
| Q27 | Cache invalidation strategy? | Immutability avoids most; purge on delete |
| Q28 | Viral paste stampedes? | CDN + shield + singleflight |
| Q29 | Negative caching 404s? | Short TTL; careful with create races |
| Q30 | Compression? | gzip/br; store compressed optional |
| Q31 | ETag / If-None-Match? | Yes for revalidation |
| Q32 | Range requests? | Optional for large pastes |
| Q33 | Metadata cache aside bugs? | TTL + purge on tombstone |
| Q34 | Object key design? | Hash prefix for partition |
| Q35 | Cross-region read latency? | CDN; regional origins |
| Q36 | Consistency after create? | Return body on create; primary read |
| Q37 | Redis down? | Bypass to DB/object |
| Q38 | Thundering herd on expiry boundary? | Expiry enforced; CDN max-age bound |
| Q39 | Hot partition in Dynamo? | High cardinality paste_id |
| Q40 | Small files + S3 request costs? | Batch/pack tiny; CloudFront cache |

### 7.4 Expiry, GC, lifecycle (Q41–Q52)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q41 | Who deletes blobs? | Lifecycle rules + sweeper |
| Q42 | What if meta deleted but blob remains? | Orphan GC by listing/prefix or tracking table |
| Q43 | What if blob deleted first? | Read 404; repair job |
| Q44 | DynamoDB TTL lag? | Still check `expires_at` on read |
| Q45 | Legal hold? | status=hold skips GC |
| Q46 | Clock skew? | Absolute timestamps; NTP; skew tolerance |
| Q47 | Extend expiry? | Owner update; bust cache max-age |
| Q48 | Burn-after-read races? | Conditional status update |
| Q49 | CDN serves expired? | max-age ≤ remaining; purge job |
| Q50 | Grace period why? | Late in-flight caches; forensic |
| Q51 | Cost of never-expire tier? | Charge; quota |
| Q52 | Backfill expiry for old data? | Batch jobs |

### 7.5 Abuse & trust (Q53–Q64)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q53 | Phishing kits? | URL/ML scan; report; blocklist hash |
| Q54 | Spam creating millions? | Tiered rate limits; payments; CAPTCHA |
| Q55 | Public recent feed abuse? | Don’t build MVP; if yes, moderate |
| Q56 | Malware binaries in base64? | Size limits; scanners; type heuristics |
| Q57 | XSS? | Escape; CSP; raw subdomain |
| Q58 | Takedown SLA? | Queue + admin API + CDN purge |
| Q59 | Reupload after ban? | Content hash / fuzzy hash |
| Q60 | Insider abuse? | Least privilege; audit |
| Q61 | DDoS read? | CDN; WAF; rate limits |
| Q62 | DDoS write? | Quotas; async; shed |
| Q63 | Sensitive data pasted? | User education; private defaults optional; scanning caution |
| Q64 | CSAM / critical abuse? | Mandatory reporting pipelines; specialized scanners |

### 7.6 Scale & operations (Q65–Q76)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q65 | 100× writes? | Partition meta; autoscale API; object parallelism |
| Q66 | Multi-region active-active? | Cells; avoid multi-writer same ID |
| Q67 | How to migrate ID scheme? | Dual-read; longer new IDs |
| Q68 | Blue/green API? | Stateless; drain |
| Q69 | DR plan? | Backup meta; CRR blobs; runbook |
| Q70 | Cost regression detect? | Egress/$ dashboards |
| Q71 | SLO burn on CDN POP loss? | Error budgets; regional failover |
| Q72 | Schema migration online? | Additive fields; dual-write carefully |
| Q73 | Observability of privacy bugs? | Canary “secret” pastes; access audit |
| Q74 | Why cells over giant shard map? | Blast radius; ownership |
| Q75 | Handle 1M/s reads? | Mostly edge; origin fraction |
| Q76 | Team split? | API/meta vs edge/CDN vs abuse |

### 7.7 Behavioral / Amazon (Q77–Q80)

| # | Question | Strong answer direction |
|---|----------|-------------------------|
| Q77 | Storage bill 5× sudden? | Orphan GC broken / TTL bug / spam wave — dive deep metrics |
| Q78 | Customer says private paste found? | Incident: ID entropy, logs, referrers, access patterns |
| Q79 | Tradeoff meeting: forever free storage? | Frugality + trust; propose tiers |
| Q80 | Own a Sev-2 CDN misconfig caching password pastes? | Correct cache policy; purge; RCA; prevent with tests |

---

## 8. Appendices

### Appendix A — Visibility / cache matrix (quick ref)

| visibility | listable | CDN | notes |
|------------|----------|-----|-------|
| public | optional | yes | noindex optional |
| unlisted | no | yes | capability URL |
| password | no | no | verify at origin |
| private | owner | no | authn required |

### Appendix B — Example metadata item (Dynamo-ish)

```json
{
  "paste_id": "Ab3xY9kQ",
  "owner_id": "U_123",
  "title": "jvm dump excerpt",
  "language": "text",
  "visibility": "unlisted",
  "blob_key": "pastes/a1/Ab3xY9kQ",
  "size_bytes": 4200,
  "sha256": "…",
  "created_at": 1754470000,
  "expires_at": 1754556400,
  "burn_after_read": false,
  "status": "active",
  "version": 1
}
```

### Appendix C — HTTP caching examples

```text
# Public immutable, no expiry
Cache-Control: public, max-age=86400, immutable
Surrogate-Key: paste:Ab3xY9kQ

# Expiring in 10 minutes
Cache-Control: public, max-age=600

# Password
Cache-Control: private, no-store
Vary: Authorization, X-Paste-Password
```

### Appendix D — Rate limit sketch

| Subject | Create | Read 404 |
|---------|--------|----------|
| Anonymous IP | 20/hour | 100/hour |
| Logged-in | 200/hour | 1K/hour |
| Trusted | higher | higher |
| Burst | token bucket | token bucket |

### Appendix E — Error codes

| Code | Meaning |
|------|---------|
| 201 | Created |
| 200 | OK |
| 401 | Password/auth required |
| 403 | Forbidden |
| 404 | Not found / expired / tombstoned (uniform) |
| 410 | Gone (optional explicit expiry) |
| 413 | Payload too large |
| 429 | Rate limited |
| 503 | Dependency outage |

### Appendix F — Anti-patterns (deal-breakers)

| Anti-pattern | Why |
|--------------|-----|
| Bodies in SQL forever | Scale/cost |
| Sequential IDs for unlisted | Enumeration |
| CDN cache password pastes | Data leak |
| Public recent feed without abuse plan | Spam SEO hell |
| No TTL/GC | PB storage bill |
| Return 201 before blob durable | False durability |
| HTML unescaped render | XSS |
| Origin handles all reads | Melts + $$$ |

### Appendix G — Capacity worksheet

```text
Creates/day _____ × size _____ = ingress _____
Reads/day _____ × size _____ = theoretical egress _____
CDN hit ratio _____ → origin egress _____
Origin read QPS _____ 
Meta QPS _____ (after Redis hit _____)
TTL mix: 1h __% / 1d __% / 1w __% / never __% → working set _____
```

### Appendix H — 45-minute timebox

| Minutes | Focus |
|---------|-------|
| 0–5 | Requirements: privacy, TTL, size, listing |
| 5–12 | Estimates: rps, storage, CDN, ID entropy |
| 12–25 | HLD: API, meta, object, CDN |
| 25–35 | Deep dive: expiry OR abuse OR burn-after-read |
| 35–42 | Scale 10×/100×, failures, cost |
| 42–45 | SLOs, ownership, wrap-up |

### Appendix I — Glossary

| Term | Meaning |
|------|---------|
| Unlisted | Reachable by URL; not listed publicly |
| Capability URL | Secret token-in-URL authorization |
| Origin shield | Intermediate cache collapsing misses |
| Tombstone | Deleted marker retaining ID briefly |
| CRR | Cross-region replication |
| Idempotency-Key | Client key to dedupe creates |
| Surrogate-Key | CDN purge tag |

### Appendix J — Sample create response

```json
{
  "paste_id": "Ab3xY9kQ",
  "url": "https://paste.example/Ab3xY9kQ",
  "raw_url": "https://paste.example/raw/Ab3xY9kQ",
  "visibility": "unlisted",
  "expires_at": "2026-08-07T07:22:11Z",
  "size_bytes": 4200
}
```

### Appendix K — Ownership RACI

| Activity | Paste API | Storage | CDN/Edge | Abuse |
|----------|-----------|---------|----------|-------|
| Cache policy change | C | I | A | C |
| Lifecycle rule | C | A | I | I |
| Takedown | C | C | C | A |
| Schema change | A | I | I | I |
| Rate limit tiers | C | I | C | A |

### Appendix L — Progressive scale one-pager

| Scale | Bottleneck | Investment |
|-------|------------|------------|
| 10× | Origin reads / egress $ | CDN + Redis + TTL |
| 100× | Metadata & GC volume | Shard/Dynamo TTL; shield; abuse ML |
| 1,000× | Cells, cold storage, spam economy | Regional cells; tiering; create-cost controls |

### Appendix M — Comparison checklist vs common designs

| Topic | Pastebin answer |
|-------|-----------------|
| Like TinyURL? | Plus blob store & CDN bytes |
| Like S3 public bucket? | Plus short IDs, TTL UX, password, abuse |
| Like Google Docs? | No collab OT/CRDT |
| Like gist? | Similar; accounts/listing optional |

### Appendix N — Minimal threat model

| Asset | Threat | Control |
|-------|--------|---------|
| Unlisted content | URL leak / brute force | Entropy, rate limit, password option |
| User browser | XSS | Escape, CSP, raw domain |
| Platform $ | Storage/egress abuse | Quotas, TTL, CDN, anomaly alerts |
| Reputation | Phishing hosts | Scan, report, takedown |

### Appendix O — Read authz pseudocode

```text
function authorize_read(paste, principal, password):
  if paste.status != active: deny(404)
  if paste.expires_at and now >= paste.expires_at: deny(404)
  switch paste.visibility:
    case public, unlisted: allow
    case password:
      if verify(password, paste.password_hash): allow else deny(401)
    case private:
      if principal == paste.owner_id: allow else deny(403)
```

---

*End of Amazon SDE III prep doc — Pastebin System Design.*
