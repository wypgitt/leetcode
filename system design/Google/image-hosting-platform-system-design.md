# System Design: Image-Hosting Platform

> **Focus areas:** Direct-to-blob upload · Virus scan · Async resize · Metadata · CDN · Signed URLs · ACLs · EXIF strip · Hash dedup · Multi-format (JPEG/WebP/AVIF)  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×) — **2024 L5 candidate report style**  
> **Quality bar:** Correct arithmetic (storage TB/PB, QPS split), explicit upload vs transform vs serve planes, deal-breakers for “proxy all bytes through app servers”  
> **Interview theme:** Classic Google L5 media platform — durable upload, safe processing, global read path, permissions that don’t leak via CDN

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—an **image-hosting platform** (think Photos / Drive images / social CDN backend): users upload images, the system stores originals, derives variants (thumbnails/resizes/formats), serves them globally via CDN, and enforces **permissions**.

### 1.0 What this is / is not

| Dimension | **Image-hosting platform (this doc)** | Not this |
|-----------|--------------------------------------|----------|
| Primary job | Upload → store → transform → serve | Full social network / feed ranking |
| Success | Durable originals, fast views, correct ACL | ML image understanding as MVP |
| Write path | Presigned direct-to-blob | App server as byte proxy (anti-pattern) |
| Read path | CDN + signed URLs / public cache policy | Origin fetch every view |
| Metadata | Owner, ACL, dims, hashes, variants | Full DAM / Creative Cloud suite |

**Scope statement:** Design an image-hosting platform covering upload, virus scan, async resize pipeline, metadata DB, blob storage, CDN, and permissions—at progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who uploads? | Authenticated users / apps; multi-tenant | `owner_id` + ACL; quotas |
| F2 | Upload API? | **Presigned URL** direct to object storage | Control plane mints URL; data plane bypasses API |
| F3 | Max size / types? | e.g. ≤ 25–50 MB; JPEG/PNG/WebP/GIF/HEIC | Validation; reject/transcode HEIC |
| F4 | Variants? | Thumb (≤200px), medium, large; WebP/AVIF | Async job pipeline; derivative objects |
| F5 | Original preserved? | Yes — immutable original blob | Derivatives keyed by transform spec |
| F6 | Metadata? | Width/height, content-type, size, hash, created | Metadata DB separate from blobs |
| F7 | Permissions? | Private default; share link; public album optional | ACL check at URL mint / cookie authz |
| F8 | Dedup? | Optional content-hash dedup across owners? | **Per-owner** dedup MVP; global careful (privacy) |
| F9 | EXIF? | Strip GPS for serve variants; keep original policy | Privacy: strip on derivatives; original access ACL’d |
| F10 | Virus/malware? | Yes — scan before “ready” / before public serve | Async scanner gate |
| F11 | Delete? | Soft delete + GC; revoke URLs | Manifest + CDN purge/short TTL tokens |
| F12 | Listing? | User library list/pagination | Metadata indexes by owner |

**MVP functional scope (lock with interviewer):**

1. Authn user requests **upload session** → receives **presigned PUT** (+ limits).  
2. Client uploads **directly to blob store**; completes via callback/`CompleteUpload`.  
3. System records metadata (`PROCESSING`), runs **virus scan**, strips risky EXIF on derivatives.  
4. **Async resize/transcode** pipeline produces thumb/medium/large (+ WebP/AVIF).  
5. Mark `READY`; client fetches via **CDN** with **signed URL** (private) or public cacheable URL.  
6. ACL: owner, explicit share, optional public.  
7. Dedup by **hash within owner** (optional global only for public CDN assets).  
8. Delete/revoke; quota enforcement.

**Out of MVP:**

- Full video hosting (sibling design)  
- Server-side AI tagging / face grouping (hooks)  
- Collaborative multi-writer albums with CRDT  
- Client-side encryption with zero-knowledge (mention tradeoff)  
- Infinite on-the-fly arbitrary transform API without cache (cost bomb)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Upload success durability | No silent loss after complete | Multi-AZ object store; checksum |
| N2 | Time-to-first-thumb | Feels quick | p50 < 3–5s after complete; p99 < 15–30s |
| N3 | View latency | CDN warm | p50 TTFB < 100–200ms edge |
| N4 | Availability (serve) | Critical | 99.9%+ via CDN; origin shielded |
| N5 | Security | No ACL bypass via CDN | Signed URLs / signed cookies; short TTL |
| N6 | Privacy | No GPS leak on shared thumbs | EXIF strip policy |
| N7 | Consistency | Strong metadata in home; blobs immutable | Variant readiness flags |
| N8 | Multi-region | Global users | Regional upload; geo-replicated hot; CDN |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. App requests upload → PUT to GCS/S3 → complete → scan OK → thumbs ready → show library.  
2. Owner opens image → mint signed URL → CDN HIT → bytes.  
3. Owner shares link → viewer with token sees derivatives; original optional.  
4. Re-upload same bytes (same owner) → dedup; reuse blob; new logical image or refcount++.  
5. Delete image → metadata soft-delete; signed URLs expire; GC blobs when refcount0.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Presign expired mid-upload | Client requests new URL; resumable sessions preferred |
| Complete without blob | Reject; no metadata READY |
| Virus detected | Quarantine; never publish CDN; notify user |
| Corrupt / truncated image | Identify fail → `FAILED`; no variants |
| Resize worker crash | Lease reclaim; idempotent write same object keys |
| Hot viral image | CDN cache; origin shield; optional multi-region replicate |
| ACL change private←public | Invalidate CDN; revoke tokens; shorter cache TTLs for private |
| EXIF GPS in original | Block public original; strip on all derivatives |
| Thumbnail race before READY | Client polls status; placeholders |
| Double complete | Idempotent on `upload_id` |
| Hash collision (crypto) | SHA-256; treat as identical content |
| Huge PNG bomb | Pixel/dimension limits; decoder resource caps |
| GIF animation | Policy: first frame thumb or animated GIF path |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 10M | 100M | 1B | multi-B |
| Uploads / day | 20M | 200M | 2B | 20B |
| Peak upload completes/s | 500 | 5K | 50K | 500K |
| Avg original size | 3 MB | 3 MB | 2–4 MB | 2–4 MB |
| New original bytes/day | ~60 TB | ~600 TB | ~6 PB | ~60 PB |
| Derivatives / original | ~6 | ~6–8 | ~8 | ~8–12 |
| Peak view QPS (images) | 200K | 2M | 20M | 200M |
| Metadata rows | 10B | 100B | 1T | retention/cells |
| CDN egress | high | critical | critical | critical |
| Regions (upload homes) | 3 | 5–7 | 10+ | cell fabric |

**What each jump forces:**

- **10×:** Presigned multipart; job queue shards; metadata indexes; CDN mandatory.  
- **100×:** Metadata cells by `owner_id`; regional processing; origin shield; async replication.  
- **1,000×:** Storage cold tiering; transform caches globally; ACL token services; strict quota/abuse.

### 1.5 Etc. (Constraints & Assumptions)

- Blobs are **immutable**; edits create new image version / new derivatives.  
- Control plane (metadata/ACL) ≠ data plane (bytes).  
- **Never** stream all upload bytes through the API tier at scale.  
- Formats evolve: prefer generate AVIF/WebP + JPEG fallback.  
- 2024-style expectation: talk **presigned upload**, **malware scan**, **signed URL ACL**, **AVIF**, **EXIF privacy**.

**Scope statement to repeat back:**

> Design an image-hosting platform: authenticated presigned direct-to-blob upload, virus scan and async derivative pipeline (resize + modern formats), metadata/ACL service, hash dedup (owner-scoped), EXIF stripping on serve variants, and CDN delivery via signed URLs—scaling through 10× / 100× / 1,000× with regional processing and metadata cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Presign / complete API** | Control plane | ~1–2K/s | ~10–20K/s | Stateless API |
| **Blob PUT bytes** | Direct upload | ~1.5 GB/s | ~15 GB/s | Object store |
| **Scan + transform jobs** | Per upload × variants | ~3–5K jobs/s | ~30–50K/s | Worker fleet |
| **Metadata writes** | Image + variants rows | ~2–5K/s | ~20–50K/s | DB cells |
| **Metadata reads** | Library / ACL | ~20–50K/s | ~0.2–0.5M/s | DB + cache |
| **CDN edge GETs** | Image views | ~200K/s | ~2M/s | CDN |
| **Origin GETs** | Cache miss | << edge | still << | Origin shield |

**Anti-pattern:** one “QPS” for JSON API and multi-MB GETs.

### 2.2 Storage math

```text
Baseline: 20M uploads/day × 3 MB = 60 TB/day originals
Derivatives: assume +100% bytes (thumbs small but many formats) → ~120 TB/day total class
Year ≈ 40–45 PB/year before deletion/tiering — retention & cold tier mandatory at 100×

Objects count:
  20M/day × (1 original + 6 derivatives) = 140M objects/day
  Metadata ~500B–1KB/row → hundreds of GB/day raw meta growth
```

### 2.3 Transform CPU

```text
Decode + resize + encode WebP/AVIF is CPU/GPU heavy
If 20M/day ≈ 230 uploads/s average; peak 500/s
Each needs ~6 derivatives → 3000 transforms/s peak order
If one transform = 100ms CPU → 300 cores busy average peak path
→ autoscaled worker pools; priority for thumbs first
```

### 2.4 CDN vs origin

```text
200K view QPS × 200 KB avg = 40 GB/s egress
At $0.02–0.08/GB class → dominating cost center
Origin miss ratio 1% → 2K QPS × 200 KB = 400 MB/s origin — size shield + cache TTLs
Hot image: 1M QPS possible on celeb avatar — must be edge-cached
```

### 2.5 Metadata QPS

```text
Library infinite scroll: 50 items/page
DAU 2M peak browsing × 1 req/30s → ~67K list QPS — cache timelines
ACL mint for each view private: can be high — batch cookie / capability tokens
```

---

## 3. High-Level Design

### 3.1 API (control plane)

| Op | Semantics |
|----|-----------|
| `POST /v1/uploads` | Create upload session → `{upload_id, presigned_url, headers, expires}` |
| `POST /v1/uploads/{id}/complete` | Verify object exists + checksum → enqueue processing |
| `GET /v1/images/{id}` | Metadata + variant URLs (authorized) |
| `GET /v1/images/{id}/url?variant=` | Mint short-lived signed URL |
| `GET /v1/users/me/images?cursor=` | Library list |
| `POST /v1/images/{id}/acl` | Update ACL / share |
| `DELETE /v1/images/{id}` | Soft delete |
| `GET /v1/images/{id}/status` | PROCESSING / READY / FAILED / QUARANTINED |

**Data plane:** HTTP PUT/POST to object storage via presigned URL (optionally **resumable** / multipart).

### 3.2 Data model

**Image (logical)**

```text
Image {
  image_id,            // ULID / snowflake
  owner_id,
  status,              // UPLOADING|PROCESSING|READY|FAILED|QUARANTINED|DELETED
  content_hash,        // sha256 of original bytes
  bytes, width, height, content_type,
  blob_key_original,   // gs://.../orig/{hash or image_id}
  acl,                 // PRIVATE|SHARED|PUBLIC + principals
  created_at, deleted_at,
  processing_error?
}
```

**Variant**

```text
Variant {
  image_id,
  spec,                // "thumb_200", "md_1280_webp", "lg_2048_avif"
  blob_key,
  bytes, width, height, content_type,
  status,
  exif_stripped: true
}
```

**UploadSession**

```text
UploadSession {
  upload_id, owner_id, expected_hash?, max_bytes,
  presign_expiry, blob_key_temp, status
}
```

### 3.3 Object key layout

```text
tmp/{owner}/{upload_id}                  # during upload
orig/{content_hash}                      # immutable original (refcount)
deriv/{content_hash}/{spec}              # immutable derivatives
# OR if privacy isolation preferred:
orig/{owner}/{image_id}                  # no cross-owner key sharing
deriv/{owner}/{image_id}/{spec}
```

**Dedup tradeoff:**

| Layout | Pros | Cons |
|--------|------|------|
| Hash-addressed global | Storage save | Cross-tenant timing side channels; ACL complexity |
| Owner-scoped keys | Simpler privacy | Less dedup |
| **MVP:** hash + **refcount per tenant visibility** | Save storage; ACL on logical image | Careful GC |

**Chosen MVP:** content-hash blob store with **logical Image ACL**; blob readable by system only; users never get raw unsigned hash URL without authz mint. Cross-owner dedup allowed for storage but **access always via image_id ACL**.

### 3.4 Upload path options — Why X over Y

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| **Presigned direct-to-blob** | Scales; cheap API | Need complete/callback | **MVP default** |
| Proxy via API | Easy validation | Melts API NICs | Tiny admin tools only |
| Client → API → multipart fanout | Controllable | Cost/latency | Avoid |

**Deal-breaker:** all user image bytes through app servers at 15 GB/s.

### 3.5 Transform pipeline options

| Mode | Pros | Cons |
|------|------|------|
| **Async queue after complete** | Fast ACK; retryable | Thumb delay | 
| Sync thumb on complete | Instant thumb | Tail latency; timeouts |
| On-the-fly resize at edge | Flexible | Stampede; CPU$ ; cache carefully |

**Chosen:** async pipeline; **priority queue** for `thumb` first; optional edge on-the-fly only for rare specs with cache.

### 3.6 Serving & permissions — Why X over Y

| Mechanism | Pros | Cons | Use |
|-----------|------|------|-----|
| **Signed URL (query sig)** | Simple; CDN friendly | URL sharing leakage until TTL | **Private MVP** |
| Signed cookies | Nice for galleries | Cookie domain complexity | Albums |
| Public immutable URL | Max cache | ACL flip hard | Truly public |
| Auth gate at origin every time | Strong ACL | Destroys CDN hit rate | Avoid |

**Deal-breaker:** long-TTL public CDN URLs for private images.

**ACL flip strategy:** short signed TTL (60–300s); on revoke, refuse new mints; optional CDN purge for public→private.

### 3.7 Format strategy

| Format | Role |
|--------|------|
| Original | Keep as uploaded (or lossless archive) |
| JPEG | Universal fallback |
| WebP | Broad modern default |
| AVIF | Best compression; slower encode |
| Progressive JPEG | Better UX on slow nets for large |

**Chosen:** generate `thumb` JPEG+WebP; `medium` WebP+AVIF+JPEG; serve negotiable via `Accept` or URL variant.

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Upload | Presigned direct | Scale/cost | API byte proxy |
| Processing | Async + priority thumbs | UX + retries | Sync everything |
| Dedup | Hash blobs + ACL on image | Save $ | Unsigned hash URLs |
| EXIF | Strip on derivatives | Privacy | Serve GPS thumbs |
| ACL | Short-lived signed URLs | CDN + security | Permanent private URLs |
| Metadata | DB by owner cell | List/ACL QPS | Blobs as only metadata |
| Hot serve | CDN + shield | Egress/QPS | Origin per view |

---

## 4. Architecture Diagram

```text
  Mobile / Web / SDK
       |
       | (1) POST /uploads  (auth)
       v
  +---------------------+         +------------------+
  | API / Control Plane |-------->| Metadata DB      |
  | auth, ACL, quotas   |         | images/variants  |
  +----------+----------+         +--------+---------+
             |                             ^
             | (2) presigned PUT           | status updates
             v                             |
  +----------+----------+                  |
  | Object Storage      |                  |
  | tmp/ → orig/ hash   |                  |
  +----------+----------+                  |
             | complete                    |
             v                             |
  +----------+----------+    jobs     +----+--------------+
  | Ingest Orchestrator |-----------> | Worker Pools     |
  | virus scan gate     |             | scan / identify  |
  +---------------------+             | resize / encode  |
                                      | EXIF strip       |
                                      +----+--------------+
                                           |
                                           v
                                      Object Storage deriv/
                                           |
                                           v
  Viewer --> CDN / Edge POP --> Origin Shield --> Object Storage
               ^
               | (3) GET /images/{id}/url --> signed URL (ACL checked)
```

**Upload path:**

```text
Client -> API: CreateUpload(auth, filename, size, content_type)
API -> check quota -> insert UploadSession(UPLOADING)
API -> mint presigned PUT(tmp key, max size, content-type)
Client -> PUT bytes -> Object Store
Client -> API: CompleteUpload(upload_id, sha256)
API -> HeadObject + checksum verify
API -> insert Image(PROCESSING), enqueue ScanJob
API -> 202 {image_id}
```

**Processing path:**

```text
ScanJob -> ClamAV/malware service
  if bad: QUARANTINED; stop
Identify -> dimensions, type; reject bombs
Write orig/{hash} if new (refcount++)
Enqueue TransformJobs (thumb first)
Workers -> decode -> strip EXIF -> resize -> encode -> put deriv/
Update Variant rows; when required set READY
Notify (webhook/push) optional
```

**Serve path (private):**

```text
Client -> API GetSignedUrl(image_id, variant) with auth
API -> load Image ACL; authorize
API -> sign CDN URL (expiry 120s, image_id, variant, owner)
Client -> CDN GET signed URL
CDN -> HIT or shield -> GET blob
```

**Serve path (public):**

```text
Public URL /cdn/o/{hash}/{spec} with long TTL
ACL must be PUBLIC; on demotion: purge + block
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No READY without successful scan** (for user-visible/public).  
2. **Immutability:** never overwrite `orig/{hash}` or `deriv/{hash}/{spec}` bytes.  
3. **ACL check before minting** capability URLs.  
4. **Checksum verify** on complete (client hash vs store).  
5. **Idempotent workers:** same output key; safe retries.  
6. **Soft delete first;** GC only at refcount 0.

#### 5.1.2 Upload reliability

| Technique | Role |
|-----------|------|
| Resumable / multipart | Large files; flaky mobile |
| Idempotency-Key on create/complete | Double-tap |
| Temp keys + promote | Don’t publish incomplete |
| Checksum (CRC32C/SHA-256) | Integrity |
| Session expiry GC | Abandon tmp objects |

#### 5.1.3 Processing reliability

```text
Job {job_id, image_id, type, attempt, lease_owner, lease_until}
Worker:
  claim lease
  if output exists & checksum OK: mark done (idempotent)
  else process -> write tmp -> checksum -> promote
  ack
Timeout: another worker steals lease
Poison: after N fails -> FAILED with reason; DLQ
```

**Thumb-first:** mark `READY_PREVIEW` when thumb exists so UI can render while AVIF large still encodes.

#### 5.1.4 Virus scan placement

| Placement | Pros | Cons |
|-----------|------|------|
| Before any derive | Safe | Delay thumbs |
| Parallel with identify | Faster | Must block publish |
| On download only | Weak | Too late |

**Chosen:** scan gate before derivatives leave quarantine namespace; never CDN-publish quarantined.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Worker death | Leases + idempotent keys |
| 10× | Queue lag | Autoscale; degrade AVIF first |
| 100× | Metadata hotspot | Owner cells; upload_id ULID |
| 1,000× | Storage $ | Cold tier; aggressive dedup; retention |

### 5.2 Scalability

#### 5.2.1 Control vs data plane

```text
API CPU/mem for JSON << NIC for GB/s uploads
Presign makes API scale with authentications not bytes
```

#### 5.2.2 Metadata sharding

| Strategy | Key | Notes |
|----------|-----|-------|
| **Cell by owner_id** | hash(owner) % N | Lists local; **MVP→100×** |
| Shard by image_id | good point reads | Bad for library lists |
| Secondary index service | search | Phase 2 |

Indexes: `(owner_id, created_at DESC, image_id)` for cursor pagination.

#### 5.2.3 Transform scalability

- Queue partitioned by `hash(image_id)`.  
- Separate pools: `scan`, `thumb`, `large_avif` (AVIF slow).  
- Cap concurrent decodes per worker (memory).  
- At 100×: regional workers near storage to cut egress.  
- Result cache: `deriv/{hash}/{spec}` shared across logical images with same hash.

#### 5.2.4 Hot images

```text
Celebrity avatar / meme:
  CDN cache HIT ratio → ~99.9%
  Origin shield coalesces misses
  Optional: replicate object to multi-region origins
  Avoid metadata DB on pure byte path (URL already authorized via signature)
```

Signed URL should embed enough to authorize at edge (HMAC) without DB chat on every GET. Revocation via short TTL (+ denylist for emergencies).

#### 5.2.5 Multi-region

| Concern | Design |
|---------|--------|
| Upload | Home region near user; write local bucket |
| Metadata | Home cell by owner; global directory |
| Processing | Same region as tmp/orig |
| Serve | CDN global; origin nearest / replicated hot |
| Cross-region share | Replicate on first miss or async for popular |

**Consistency:** metadata strong in home cell; cross-region read of metadata may be slightly stale — signed URLs minted in home.

#### 5.2.6 Progressive scale

| Jump | Change |
|------|--------|
| →10× | Multipart; CDN; worker autoscaling; Redis meta cache |
| →100× | Owner metadata cells; regional pipelines; origin shield |
| →1,000× | Cold/archive tier; transform edge cache; token service; abuse cells |

### 5.3 Maintainability

#### 5.3.1 Transform spec registry

```text
specs:
  thumb_200: {fit: cover, w:200, h:200, formats:[webp,jpeg], strip_exif:true}
  md_1280:   {fit: inside, w:1280, formats:[avif,webp,jpeg], progressive:true}
  lg_2048:   {fit: inside, w:2048, formats:[avif,webp,jpeg]}
```

Version specs: `thumb_200@v2` new keys; don’t mutate old derivatives.

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `upload_complete_rate` | Funnel |
| `scan_lag_s` | Safety/UX |
| `thumb_ready_latency` | Product SLO |
| `transform_fail_ratio` | Poison images |
| `cdn_hit_ratio` | Cost |
| `origin_qps` | Shield health |
| `signed_url_mint_qps` | Authz path |
| `quota_reject` | Abuse |
| `exif_gps_stripped` | Privacy audit |

#### 5.3.3 Testing

- Malicious images (zip bombs / huge dimensions).  
- ACL tests: no cross-user mint.  
- Idempotent worker crash mid-write.  
- Public→private purge.  
- Dedup refcount GC.

#### 5.3.4 Operability

- Feature flag new format (AVIF) percentage.  
- Shadow encode compare size/quality.  
- Drain region: block new uploads; finish jobs; replicate.  
- Chaos: kill scan service → no READY (fail closed).

---

## 6. Wrap-Up

### 6.1 What we designed

An **image-hosting platform** with **presigned direct-to-blob upload**, **virus-gated async transforms** (thumb-first, WebP/AVIF/JPEG), **owner-celled metadata + ACLs**, **content-hash blob dedup** with logical permissions, **EXIF stripping** on derivatives, and **CDN delivery via short-lived signed URLs**—not an API that proxies petabytes.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Upload path | Presigned direct; never proxy at scale |
| Sync vs async transforms | Async + thumb priority |
| On-the-fly resize | Rare specs only + cache |
| Private caching | Signed short TTL; not permanent public |
| Dedup | Hash blobs; ACL on image_id |
| EXIF | Strip derivatives; guard originals |
| Metadata | Separate DB; shard by owner |

### 6.3 30-second scale narrative

> Baseline: presign → GCS/S3 → complete → scan → async derivatives → Redis/MySQL metadata → Cloud CDN signed URLs. 10× adds multipart and CDN discipline. 100× cells metadata by owner and regionalizes processing with origin shield. 1,000× is cold tiers, global transform caches, and token services—cost dominated by egress and encode CPU, not JSON QPS.

### 6.4 Deal-breakers checklist

- Proxying all uploads through app servers.  
- Permanent cacheable URLs for private images.  
- Serving GPS EXIF on shared thumbs.  
- Marking READY before malware scan.  
- Overwriting mutable blob keys for “edits.”  
- Metadata only inside object custom headers (no list/query story).

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product (2024 L5 style)

**Q1: Who is the customer?**  
A: Consumer apps / internal product needing durable image hosting with variants—not a generic S3 resale without ACL/transform.

**Q2: Do we keep originals forever?**  
A: Product/retention policy; design for tiering + delete GC.

**Q3: On-the-fly crop/rotate API?**  
A: Dangerous cost; prefer preset specs + limited signed transform params with cache keys.

**Q4: Client-side compression before upload?**  
A: Encouraged; still verify server-side type/dimensions.

**Q5: HEIC from iOS?**  
A: Accept + transcode to JPEG/AVIF for web derivatives; keep original if storage allows.

### 7.2 Upload & storage

**Q6: Why presigned URLs?**  
A: Offload bandwidth; scale control plane independently; temporary scoped credentials.

**Q7: Multipart vs single PUT?**  
A: Multipart/resumable for larger files and mobile reliability.

**Q8: How to prevent clients from uploading 10 GB?**  
A: Presign conditions: `content-length-range`, content-type allowlist; quota pre-check.

**Q9: Where is source of truth?**  
A: Object store for bytes; metadata DB for ACL/status; never only one.

**Q10: Cross-region upload acceleration?**  
A: Edge POP → regional bucket; or multi-region bucket class with care on consistency/cost.

### 7.3 Security & privacy

**Q11: How do signed URLs work?**  
A: HMAC over path + expiry + variant (+ optional IP); edge verifies secret; no DB on HIT path.

**Q12: Stolen signed URL?**  
A: Short TTL; optional IP bind; revoke denylist for emergencies; don’t put long-lived secrets in URLs.

**Q13: Path traversal / guessable IDs?**  
A: Use unguessable `image_id`; never expose raw disk paths; authorize every mint.

**Q14: EXIF GPS leak?**  
A: Strip for all derivatives and any public original; private original download may keep EXIF with warning.

**Q15: Malware in polyglot files?**  
A: Scan + strict parsers; re-encode derivatives from decoded pixels (destroys many polyglots).

**Q16: SSRF via processing?**  
A: Workers only read object store; no user-supplied fetch URLs in MVP.

### 7.4 Processing pipeline

**Q17: Why re-encode instead of serving original always?**  
A: Size, format compatibility, EXIF strip, strip exploits.

**Q18: AVIF vs WebP tradeoff?**  
A: AVIF smaller/slower encode; WebP faster/wider; generate both + JPEG fallback.

**Q19: Progressive JPEG?**  
A: Better perceived load for large; still offer modern formats.

**Q20: How to prioritize thumbs?**  
A: Separate high-priority queue; READY_PREVIEW state.

**Q21: Idempotency of transforms?**  
A: Content-addressed output keys; workers safe to retry.

**Q22: Image bombs?**  
A: Max megapixels before decode; streaming decode limits; memory cgroup.

### 7.5 Dedup & GC

**Q23: Per-owner vs global dedup?**  
A: Global saves more $; privacy/side channel risks; always ACL via logical images.

**Q24: Refcounting?**  
A: `blob_refs[hash]++` on use; delete logical image decrements; GC at 0 with delay.

**Q25: Same hash different owners—can B discover A’s image?**  
A: Not if URLs/ACL are image_id based and listings are owner-scoped; avoid “upload and see if hash exists” API oracle (constant-time / no reveal).

### 7.6 CDN & hot images

**Q26: Origin shield?**  
A: Intermediate cache coalescing so 10K edge misses → 1 origin GET.

**Q27: Cache key?**  
A: Include variant/format; for signed URLs often cache by path ignoring signature if signature valid (CDN feature) — configure carefully.

**Q28: ACL change impact?**  
A: Short TTL; purge on public demotion; private mostly relies on expiry.

**Q29: Multi-CDN?**  
A: At extreme scale; complexity in invalidation and signing.

### 7.7 Metadata & consistency

**Q30: Strong consistency needs?**  
A: After complete, reader in same region should see PROCESSING/READY; use primary home cell.

**Q31: List pagination?**  
A: Cursor `(created_at, image_id)`; avoid OFFSET.

**Q32: Transactions across DB + blob?**  
A: Can’t be classic distributed TX; use state machine: blob first, then DB, GC orphans.

**Q33: Orphan tmp objects?**  
A: Lifecycle rules expire `tmp/` after 24h.

### 7.8 Estimation drills

**Q34: Year-1 storage at baseline?**  
A: ~60 TB/day originals × 365 ≈ 22 PB + derivatives — discuss retention.

**Q35: Egress cost dominance?**  
A: Views >> uploads; CDN + compression formats win.

**Q36: Why not Postgres for 1T rows?**  
A: Cell/shard; or Spanner/Bigtable; Postgres OK early with shards.

### 7.9 Alternatives & deal-breakers

**Q37: Only Cloudflare Images / imgproxy?**  
A: Fine building block; interview still wants ACL, upload, metadata, failure design.

**Q38: Store images in MySQL BLOB?**  
A: Deal-breaker at scale.

**Q39: Synchronous scan+all formats before HTTP 200?**  
A: Terrible mobile UX; use async + status.

**Q40: Unsigned `/images/{sequential_id}.jpg`?**  
A: IDOR nightmare — deal-breaker.

### 7.10 Interview craft

**Q41: How to open (2024 L5)?**  
A: Clarify private vs public, variants, max size, scan, regions — then draw control vs data plane.

**Q42: What numbers matter?**  
A: Upload bytes/s, objects/day, transform CPU, view QPS, CDN hit ratio, metadata QPS.

**Q43: What signals seniority?**  
A: Presign conditions, thumb-first readiness, EXIF policy, signed URL revocation story, owner cells, origin shield, explicit deal-breakers.

**Q44: Common failure in interview?**  
A: Beautiful resize talk but forgetting ACL on CDN; or forgetting malware scan gate.

---

### Appendix A — Presign constraints (S3-style sketch)

```text
Conditions:
  content-length-range: 1 .. max_bytes
  content-type in allowlist
  key == tmp/{owner}/{upload_id}
  x-amz-meta-owner == owner_id
Expiry: 15 minutes
```

### Appendix B — CompleteUpload pseudocode

```text
CompleteUpload(upload_id, client_sha256):
  session = load(upload_id); authz owner
  obj = storage.Head(session.tmp_key)
  assert obj.size <= session.max_bytes
  assert obj.sha256 == client_sha256  # or server compute
  image_id = new_id()
  db.insert(Image{image_id, PROCESSING, ...})
  enqueue(ScanJob(image_id, tmp_key, sha256))
  return image_id
```

### Appendix C — Transform worker

```text
process(TransformJob):
  bytes = storage.Get(orig_key)
  img = decode_safe(bytes, max_mp=100)
  img = strip_exif(img)
  out = resize(img, spec)
  encoded = encode(out, spec.format, quality)
  key = deriv_key(hash, spec)
  storage.PutIfAbsent(key, encoded)
  db.upsert(Variant{READY, ...})
  maybe_mark_image_ready()
```

### Appendix D — HMAC signed URL

```text
payload = f"{image_id}|{variant}|{exp}|{owner_id}"
sig = HMAC_SHA256(secret, payload)
url = https://cdn.example/{image_id}/{variant}?exp=...&sig=...
Edge: verify sig & exp; map to blob_key via table or embedded map token
```

For pure edge verify without DB: embed `blob_key` hash in token claims.

### Appendix E — ACL model

```text
acl {
  mode: PRIVATE | PUBLIC | SHARED
  principals: [user:u123, group:g9]  # SHARED
}
Authorize(user, image):
  if image.deleted: deny
  if mode==PUBLIC: allow
  if user == owner: allow
  if user in principals: allow
  else deny
```

### Appendix F — EXIF policy

| Surface | GPS/EXIF |
|---------|----------|
| Derivative thumb/md/lg | Strip all sensitive |
| Public original | Forbidden or stripped copy |
| Private download original | Allow with auth; warn |
| Share link | Derivatives only MVP |

### Appendix G — Progressive scale table

| Scale | Upload | Meta | Process | Serve |
|-------|--------|------|---------|-------|
| Baseline | Presign single | 1 PG | 1 queue | CDN |
| 10× | Multipart | Cache | Pool split | Shield |
| 100× | Regional buckets | Owner cells | Regional workers | Multi-origin |
| 1,000× | Cell fabric | Many cells | Priority + GPU encode | Multi-CDN optional |

### Appendix H — Status state machine

```text
UPLOADING -> PROCESSING -> READY
                |           |
                v           v
           QUARANTINED   DELETED
                |
                v
             FAILED
```

### Appendix I — Dedup refcount

```text
on_new_image(sha):
  if blob_exists(sha):
    refcount++
  else:
    promote tmp -> orig/sha
    refcount=1

on_delete_image(sha):
  refcount--
  if refcount==0: enqueue GC(delay=7d)
```

### Appendix J — NFR card

```text
Presigned upload; checksum complete
Scan before READY
Thumb p50 < 5s
CDN p50 TTFB < 200ms
Signed URL TTL minutes
EXIF strip on derivatives
Owner-cell metadata at scale
```

### Appendix K — Cost levers

| Lever | Effect |
|-------|--------|
| AVIF/WebP | Less egress |
| Dedup | Less storage |
| CDN HIT | Less origin |
| Cold tier originals | $ after 30–90d |
| Fewer variants | Less CPU/$ |
| Client resize before upload | Less ingest |

### Appendix L — Hot viral path

```text
1M QPS meme image
-> CDN POP local HITs
-> shield coalesced miss
-> single origin GET
Metadata not on byte path
Watch ACL: if private signed, TTL keeps blast limited
```

### Appendix M — Comparison: sync vs async vs on-the-fly

| | Sync | Async pipeline | On-the-fly edge |
|--|------|----------------|-----------------|
| UX first byte | Slow complete | Fast complete; wait thumb | Flexible |
| Cost | Spiky API | Predictable queues | Risk stampede |
| Retry | Hard | Natural | Need cache |
| MVP | No | **Yes** | Limited |

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Proxy upload easier” | NIC/cost deal-breaker |
| “Long cache private OK” | ACL revocation fails |
| “Strip EXIF later” | Privacy incident risk |
| “DB BLOB” | Unscalable |
| “Exact on-the-fly any WxH” | Cost bomb without cache |

### Appendix O — Related systems

| System | Relation |
|--------|----------|
| Object storage (GCS/S3) | Bytes |
| CDN | Serve |
| Pub/Sub / SQS | Jobs |
| ImageMagick / libvips / magickwand | Transforms (`libvips` preferred perf) |
| ClamAV / cloud scan | Malware |
| Spanner/Postgres | Metadata |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Presigned URL | Time-limited capability for PUT/GET |
| Derivative / variant | Transformed object from original |
| Origin shield | Coalescing mid-tier cache |
| Refcount dedup | Share bytes; ACL on logical image |
| READY_PREVIEW | Thumb available; full ladder pending |
| Polyglot | File valid as multiple types — re-encode mitigates |

### Appendix Q — Worked numbers

```text
Peak completes 500/s × 3 MB = 1.5 GB/s ingress
6 derivatives: prefer thumbs 20 KB, md 150 KB, lg 400 KB × formats
CDN 200K QPS × 150 KB avg ≈ 30 GB/s
At 1% miss → 300 MB/s origin — OK with shield
Metadata: 500 completes/s × ~2K writes (image+variants) ≈ 1–4K DB writes/s baseline — single PG OK; cells at 100×
```

### Appendix R — libvips vs ImageMagick (interview spice)

| | libvips | ImageMagick |
|--|---------|-------------|
| Memory | Streaming; lower | Higher historically |
| Throughput | Higher for pipelines | Ubiquitous |
| Pick | **Workers MVP** | OK if controlled |

### Appendix S — Delete & CDN purge

```text
Soft delete DB
Stop minting URLs
If PUBLIC: CDN purge paths
GC after grace
Signed private: natural expiry sufficient often
```

### Appendix T — Quotas & abuse

```text
per_user:
  uploads_per_day
  storage_bytes
  max_resolution
per_ip:
  presign_rate
Fail closed on quota store errors for free tier
```

### Appendix U — 30m interview checklist

1. Clarify private/public, variants, scan, size limits.  
2. Split control vs data plane; estimate GB/s and view QPS.  
3. Draw presign → store → scan → workers → CDN.  
4. Deep dive ACL signed URLs + EXIF + dedup.  
5. Hot image + multi-region.  
6. 10×/100×/1,000× cells & tiering.  
7. Deal-breakers.

### Appendix V — Minimal SDK flow

```text
1. sdk.createUpload()
2. sdk.putDirect(presigned, file)
3. sdk.complete(uploadId, sha256)
4. poll sdk.getImage(imageId) until status in {READY, READY_PREVIEW, FAILED, QUARANTINED}
5. url = sdk.getSignedUrl(imageId, "thumb_200")
6. <img src=url />
```

### Appendix W — Content-type allowlist

```text
image/jpeg, image/png, image/webp, image/gif, image/heic, image/heif
Reject: image/svg+xml (XSS risk unless sanitized sandbox), application/*
Re-encode derivatives from pixels — do not trust client content-type alone
Magic-byte sniff on complete; mismatch → FAILED
```

### Appendix X — Resumable upload sketch

```text
CreateUpload(resumable=true) -> session_url
Client PUTs chunks with Content-Range
Object store assembles
CompleteUpload verifies full size + hash
Abandon: lifecycle deletes incomplete multipart after 24h
```

### Appendix Y — Variant readiness matrix

| State | Library UI | Share link | Original download |
|-------|------------|------------|-------------------|
| PROCESSING | Placeholder | 404/retry | Deny |
| READY_PREVIEW | Thumb OK | Thumb OK | Deny until READY |
| READY | All variants | Per ACL | Per ACL |
| QUARANTINED | Hidden | Deny | Deny |
| FAILED | Error affordance | Deny | Deny |

### Appendix Z — What AI/OCR hooks look like (non-MVP)

```text
On READY:
  enqueue(CaptionJob) / SafeSearchJob  # optional product
Never block thumb path on ML
Store labels in side table keyed by image_id
```

---

*End of Image-Hosting Platform system design.*
