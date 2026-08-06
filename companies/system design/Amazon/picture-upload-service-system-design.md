# System Design: Picture Upload Service

> **Focus areas:** Presigned upload · Virus/malware scan · Thumbnails/variants · CDN · Metadata · Abuse · Privacy  
> **Style:** Amazon SDE III end-to-end design with progressive scale (10× → 100× → 1,000×)  
> **Amazon themes:** Customer trust & safety · Least privilege · Cost of storage/egress · Cell isolation · Operational excellence  
> **Quality bar:** Correct arithmetic (storage & bandwidth), explicit threat model, async processing invariants, honest MVP vs extreme-scale paths

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

Goal: **bound the upload product**—who uploads, what formats, when images become publicly viewable, and what “safe” means (malware, NSFW, copyright, spam).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who uploads? | Customers, sellers, internal tools; multi-tenant | AuthZ; per-tenant quotas; abuse scores |
| F2 | Upload method? | **Presigned URL** direct to object storage | API never proxies multi-MB bodies at scale |
| F3 | Formats / size? | JPEG/PNG/WebP/HEIC; max e.g. 20–25 MB | Validate content-type + magic bytes; reject zip bombs |
| F4 | Processing? | Virus scan + generate thumbnails / responsive variants | Async pipeline after upload finalize |
| F5 | When visible? | After scan + basic processing **or** private until approved | State machine; CDN only serves “ready” |
| F6 | Metadata? | Owner, dims, EXIF (scrub?), tags, checksum, status | Metadata DB separate from blob store |
| F7 | Delivery? | CDN signed or public URLs by product | Cache variants; short-lived signed URLs for private |
| F8 | Replace/delete? | Soft delete + GC; replace creates new version | Immutability simplifies CDN/cache |
| F9 | Abuse? | Rate limits, malware, spam images, CSAM reporting hooks | Trust & safety pipeline; blocklists |
| F10 | Dedup? | Optional perceptual / hash dedup for storage savings | Hash at ingest; careful with privacy |
| F11 | Transformations? | On-upload variants; optional on-the-fly resize at edge later | Prefer pre-generate common sizes in MVP |
| F12 | Notifications? | Webhook/event when ready or rejected | At-least-once domain events |

**MVP functional scope (lock with interviewer):**

1. Authenticated `POST /uploads` → returns **presigned PUT** + `image_id`.  
2. Client uploads directly to S3 (or equivalent); client calls `POST /uploads/{id}/complete` (or S3 event triggers).  
3. Async: **malware scan** → **validate image** → **strip dangerous EXIF** → **generate variants** → mark `READY`.  
4. Metadata API: get status, dims, URLs.  
5. CDN delivery for ready variants; delete/hide APIs.  
6. Quotas, rate limits, basic abuse throttles; virus reject path.

**Out of MVP (explicitly defer):**

- Full ML NSFW classifier ensemble (mention as Phase 2; stub hook)  
- Arbitrary on-the-fly image magick for every size (cost/DoS)  
- Cross-region active-active metadata writes  
- Client-side encryption with customer-managed keys (Enterprise Phase 2)  
- Video upload (different pipeline)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-ready (upload→viewable)? | Interactive | p50 < 5s, p99 < 30s for ≤5 MB images (baseline) |
| N2 | Upload success durability? | No lost finalized uploads | Object durable before processing; metadata consistent |
| N3 | Availability? | Upload API 99.9%+; processing eventual | Degrade processing lag before refusing uploads if safe |
| N4 | Security? | No malware served; least privilege | Private buckets; scan gate; signed URLs |
| N5 | Privacy? | EXIF GPS scrubbing by default | Policy explicit |
| N6 | Scalability? | See table | Direct-to-S3; async workers elastic |
| N7 | Cost? | Storage + egress + compute | Lifecycle tiers; WebP; CDN cache hit |
| N8 | Multi-region? | Upload nearest; metadata home cell | Regional buckets + replication policy |
| N9 | Consistency? | Strong metadata per image_id | Conditional state transitions |
| N10 | Abuse resistance? | Quotas + detection | Per-tenant bytes/day; anomaly alerts |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Request upload → presign → PUT bytes → complete → scan OK → variants → `READY` → CDN URLs.  
2. Replace: new `image_id` (immutable) or version++ with atomic pointer swap.  
3. Delete: mark deleted → CDN invalidate / signed URLs expire → GC blob later.  
4. Duplicate content-hash → optionally reuse blob, new metadata ownership row.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Presign expired before PUT | 403 from S3; client requests new upload session |
| Complete called without object | 404/409; no processing |
| Object exceeds declared size | Abort; reject; quarantine |
| Content-type mismatch / not an image | Reject; delete/quarantine object |
| Malware detected | State `REJECTED_MALWARE`; never CDN; alert T&S |
| Image bomb (huge decompressed dims) | Limit pixels / memory; reject |
| Worker crash mid-variant | Pipeline idempotent; retry from checkpoint |
| Partial variants | Don’t mark READY until required set complete |
| Hot celebrity image | CDN cache; origin shield |
| Abusive upload flood | Rate limit; quarantine tenant; circuit |
| Stolen cookie upload | Short-lived presign; auth on session create |
| EXIF GPS leakage | Strip by default; product exception list |
| CDN serves stale after delete | Short TTL for private; invalidation for public |
| Double complete | Idempotent; same state machine |
| Bucket ransomware / key leak | Least privilege; object lock optional; monitoring |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Daily uploads | 10M | 100M | 1B | 10B |
| Peak upload completes / s | ~500 | ~5K | ~50K | ~500K |
| Avg original size | 2 MB | 2 MB | 1.5–3 MB | 1.5–3 MB |
| Variants per image | 4 | 4 | 5 | 6 |
| Peak image views / s | 50K | 500K | 5M | 50M |
| Stored images (objects) | 1B | 10B | 100B | 1T |
| Metadata QPS (read) | 20K | 200K | 2M | 20M |
| Malware scan capacity | 500/s | 5K/s | 50K/s | 500K/s |
| Tenants | 1M | 10M | 100M | 1B (device/app ids) |
| Regions for upload | 2 | 4 | 8 | 15+ |

**What each jump forces:**

- **10×:** Event-driven processing; worker autoscaling; metadata sharding; CDN mandatory.  
- **100×:** Regional ingest buckets; processing cells; hierarchical abuse limits; storage lifecycle; origin shield.  
- **1,000×:** Global POP delivery; fingerprinting/dedup at scale; dedicated T&S pipelines; cold tiering; per-tenant isolation for whales.

### 1.5 Etc. (Constraints & Assumptions)

- **Never** stream large uploads through the API fleet as the steady-state design.  
- Serving malware or CSAM is a **company-level Sev**—scan gates are correctness, not nice-to-have.  
- Thumbnails are derived data; originals are source of truth (unless legal delete).  
- Amazon interview flavor: think S3 + CloudFront + Lambda/ECS workers + DynamoDB metadata + SQS, plus Trust & Safety hooks.

**Scope statement:**

> Design a multi-tenant picture upload service with presigned direct-to-storage uploads, async malware scanning and variant generation, metadata ownership, CDN delivery, and abuse controls—scaling from ~10M uploads/day through 10× / 100× / 1,000× with regional ingest and cell-friendly processing.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Ingress bandwidth

```text
Baseline: 500 uploads/s × 2 MB = 1,000 MB/s ≈ 8 Gbps peak ingest
10×: ~80 Gbps
100×: ~0.8 Tbps  → must be regional / many endpoints; direct-to-S3 essential
1,000×: multi-Tbps globally → per-region ingest + edge acceleration (S3 Transfer Accel / POP)
```

### 2.2 Storage growth

```text
Originals: 10M/day × 2 MB = 20 TB/day
Variants: assume +50–100% bytes → ~30–40 TB/day total new
Year ≈ 7–15 PB/year before deletion/dedup/compression
1,000×: absurd without lifecycle, dedup, tiering, retention policies
```

Say retention + cold tier explicitly; don’t “store forever” silently.

### 2.3 Processing compute

```text
Decode + resize CPU: assume ~200–500 ms CPU-equivalent per image on typical size
Baseline 500/s → hundreds of CPU cores busy + scan costs
Scan may be comparable or heavier than resize depending on engine
Pipeline stages parallelizable per image; shard by image_id
```

### 2.4 Egress / CDN

```text
Views 50K/s × 100 KB average variant = 5 GB/s ≈ 40 Gbps egress
CDN hit ratio 90%+ → origin ~4 Gbps
At 1,000× views: Tbps class → CDN is the product for reads
```

### 2.5 Metadata store

```text
1B images × 1 KB metadata ≈ 1 TB
1T images × 1 KB ≈ 1 PB metadata → must partition; cold metadata archival
Read-heavy: cache popular image metadata at edge/app
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Proxying uploads through app servers** — forbidden at scale.  
2. **Processing backlog** — time-to-ready SLO.  
3. **Malware scan capacity** — safety gate.  
4. **Storage & egress cost** — business risk.  
5. **Hot metadata partitions** — popular images.  
6. **Abuse floods** — fake uploads / bandwidth theft via presign.  
7. **CDN cache poisoning / auth mistakes** — private images leaking.  
8. **Thumbnail stampede** on viral content without CDN.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| **Upload session** | Presign + expiry + constraints (max bytes, types) |
| **Image** | Logical asset with `image_id`, owner, state |
| **Object / blob** | Bytes in bucket (original / variant) |
| **Variant** | Derived size/format (e.g. `thumb`, `w320`, `w1280`, `webp`) |
| **Scan result** | Malware / policy decision |
| **Metadata record** | Durable state + pointers + dims |
| **Delivery URL** | CDN public or signed |
| **Quarantine** | Non-servable holding area |

### 3.2 State machine

```text
CREATED → UPLOADED → SCANNING → PROCESSING → READY
                 \→ REJECTED_* (malware, invalid, policy)
READY → DELETED (soft)
Any non-terminal → EXPIRED (abandoned upload sessions)
```

Invariant: **CDN/public never serves non-READY** (except authenticated owner preview from quarantine with care).

### 3.3 Presigned upload flow

```text
1) Client → API: create upload (auth, filename, size, checksum optional)
2) API writes metadata CREATED; returns presigned PUT (scoped key, max size, content-type, short TTL)
3) Client PUT directly to object storage
4) Complete via:
   a) Client callback complete, or
   b) S3 ObjectCreated event → verify size/etag → UPLOADED
5) Enqueue processing
```

Prefer **storage events** as source of truth for “bytes arrived,” with client complete as UX accelerator.

### 3.4 Security of presigns

- Short TTL (e.g. 5–15 minutes).  
- Key path includes `tenant_id/image_id/original`.  
- Conditions: `content-length-range`, `content-type` starts-with.  
- Optional: client-supplied checksum (S3 CRC/SHA) required.  
- Rate-limit session creation (not only PUT).  
- Deny list of dangerous types (`multipart/`, `application/x-msdownload`, etc.).

### 3.5 Processing pipeline

```text
UPLOADED
  → Virus/malware scan (block on fail)
  → Sniff magic bytes + decode bounds (max pixels, max megapixels)
  → Strip geo EXIF / keep orientation as needed
  → Generate variants (parallelizable)
  → Write variant objects
  → Update metadata READY + URLs
  → Emit ImageReady event
```

Idempotency: each stage checkpointed; safe to retry.

### 3.6 Virus scan placement

| Option | Pros | Cons |
|--------|------|------|
| Sync before ACK complete | Stronger gate | Hurts UX; capacity cliff |
| **Async before READY** | Scalable | Brief non-ready window |
| Inline on GET | Too late; risk | Never for user content |

**Choose async before READY.** Owner may see processing state; public cannot fetch.

### 3.7 Thumbnails / variants

MVP set example:

| Name | Spec |
|------|------|
| `thumb` | 128px edge, WebP/JPEG |
| `sm` | 320px |
| `md` | 800px |
| `lg` | 1280px |
| `original` | stored private; not always CDN-exposed |

Generate server-side with memory limits; never trust client-resized only.

On-the-fly transforms (Phase 2): signed transform URLs with strict allowlist + edge cache—DoS risk if unbounded.

### 3.8 CDN & URL strategy

| Asset class | Strategy |
|-------------|----------|
| Public product images | CloudFront public cache; immutable URLs with content hash |
| Private user photos | Signed URLs (short TTL) or cookie auth at CDN |
| Rejected / quarantine | No CDN distribution |

Immutable URLs (`.../img/{id}/v/{contentHash}/md.webp`) simplify caching.  
Delete → invalidate or rely on TTL + auth revoke.

### 3.9 Metadata store

Access patterns:

1. `GetImage(image_id)`  
2. `ListByOwner(owner_id, cursor)`  
3. Update state transitions  
4. Abuse queries by tenant  

Fit: DynamoDB PK `image_id`, GSI `owner_id + created_at`.  
Large EXIF blobs → S3 sidecar, not row bloat.

### 3.10 Abuse & trust controls

- Quotas: uploads/day, bytes/day, concurrent processing.  
- Velocity anomalies → friction (CAPTCHA) / block.  
- Hash blocklist (known bad).  
- Report → takedown workflow.  
- CSAM: use platform-required scanning services / NCMEC flows as legally applicable (say: “comply with legal + specialized pipeline,” don’t invent details).  
- Cost abuse: abandoned multipart uploads aborted by lifecycle.

### 3.11 Trade-off tables

| Concern | Choice | Why |
|---------|--------|-----|
| Upload path | Presigned S3 | Scale + cost |
| Scan | Async pre-READY | Safety + UX balance |
| Variants | Pre-generate common | Predictable latency/cost |
| Metadata | DynamoDB | Scale status updates |
| Delivery | CloudFront | Egress/perf |
| Privacy | Strip GPS EXIF | Default safe |
| Dedup | Optional content hash | Savings vs complexity |
| Multi-region | Regional ingest + replicate | Latency |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Client App
      |
      | 1) auth create upload
      v
 +----------+       +------------------+
 | Upload   |------>| Metadata DB      |
 | API      |       | (Dynamo)         |
 +----+-----+       +--------+---------+
      | 2) presigned PUT              |
      v                               |
 +----------+                         |
 | S3 Ingest|--- ObjectCreated ------>|
 | Bucket   |           |             |
 +----------+           v             |
                  +-----------+       |
                  | Pipeline  |-------+
                  | Orchestr. |
                  +-----+-----+
                        |
        +---------------+----------------+
        v               v                v
   Malware Scan   Image Validator   Variant Workers
        |               |                |
        +---------------+----------------+
                        |
                        v
                 +--------------+     +-------------+
                 | Derived Bucket|--->| CDN (CF)    |---> Viewers
                 +--------------+     +-------------+
```

### 4.2 Sequence: happy path

```text
Client          API           S3          Queue        Workers       Meta
  |--create---->|             |             |            |            |
  |<--presign---|--CREATED ------------------|----------->|
  |--PUT -------------------->|             |            |            |
  |             |<--event-----|             |            |            |
  |             |--UPLOADED -------------->|            |            |
  |             |             |             |--scan----->|            |
  |             |             |             |--variants->|            |
  |             |             |             |            |--READY ---->|
  |--GET status------------------------------------------->|
  |<-- URLs READY ----------------------------------------------------|
  |--GET CDN variant -------------------------------------------------|
```

### 4.3 Sequence: malware reject

```text
Workers: scan → FAIL
  → move/copy to quarantine prefix (or tag)
  → Meta REJECTED_MALWARE
  → do not publish CDN paths
  → emit event + T&S metric
  → optional delete original per policy after retain window
```

### 4.4 Multi-region ingest

```text
Client → nearest regional API → presign to regional bucket
Metadata home cell (single writer)
Derived variants replicated to regions near viewers OR generated per region
CDN global
```

### 4.5 Abuse control plane

```text
Upload session create
  → tenant quota check
  → risk score (history, IP, device)
  → allow / challenge / deny
Processing metrics → anomaly detector → throttle tenant
Reports → takedown → DELETED + invalidate
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Failure modes & mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| API down | Cannot start uploads | Multi-AZ; regional failover |
| S3 regional issue | Uploads fail in region | Retry other region / status page |
| Processing lag | Slow READY | Autoscale workers; priority lanes |
| Scan outage | Cannot safely READY | Pause READY transitions; backlog; don’t fail open to public |
| Variant OOM | Poison images | Pixel limits; DLQ |
| Metadata DB hotspot | Status errors | Shard; cache; isolate celebs |
| CDN misconfig | Leak private | Separate distributions; auth |
| Dual complete races | Dup work | Conditional state machine |
| Partial delete | Orphan bytes | GC sweeper by inventory |
| Key leak | Unauthorized reads/writes | Short creds; bucket policies; monitoring |

#### 5.1.2 Consistency model

- Metadata state transitions: **conditional updates** (strong per item).  
- Object existence vs metadata: reconcile via events + periodic sweeper.  
- CDN: **eventual** (TTL/invalidations).  
- Cross-region metadata: **home cell single-writer**.

#### 5.1.3 Exactly-once processing?

Pipeline is **at-least-once**. Stages use idempotent writes (`overwrite variant key`) and checkpoints. READY flipped once via CAS.

#### 5.1.4 Amazon ownership themes

- **Trust & safety:** Serving malware is worse than slow thumbnails—separate Sev classifications.  
- **Customer privacy:** EXIF GPS scrubbing default; auditable exceptions.  
- **Frugality:** Egress and storage dwarf API costs—CDN hit ratio and lifecycle matter.  
- **Mechanisms:** Presign constraints and pixel limits beat “please upload reasonable files.”  
- **Ownership:** Clear DRI for scan engine vs delivery vs metadata.

### 5.2 Scalability

#### 5.2.1 Progressive scale changes

| Scale | Change |
|-------|--------|
| 1× | One region; S3+CF; SQS pipeline; Dynamo; ECS/Lambda workers |
| 10× | Autoscale per stage; metadata GSI tuning; multipart upload; lifecycle abort |
| 100× | Regional ingest; processing cells; origin shield; priority SLO classes |
| 1,000× | Global cells; dedup fingerprint service; T&S platform; cold tiers; whale isolation |

#### 5.2.2 Sharding keys

| Data | Key |
|------|-----|
| Metadata | `image_id` |
| Owner lists | GSI `owner_id` |
| Processing queues | shard by `hash(image_id)` |
| Quotas | `tenant_id` |
| Buckets | region + hash prefix for partitions |

S3 prefixes: avoid extreme hotspots on sequential prefixes; use hash-prefixed keys.

#### 5.2.3 Priority / classes

- Interactive user profile photos vs bulk seller catalog ingest.  
- Separate queues; bulk can lag.  
- SLA pages differ.

#### 5.2.4 Deduplication

Content hash (SHA256) for exact dedup; optional perceptual hash for near-dup (careful with collisions & privacy).  
Dedup shared blobs need **refcounts** and careful delete.

### 5.3 Maintainability

#### 5.3.1 Pipeline as data / DAG

Stages configured: which variants, quality, strip rules—versioned.  
Images pin `pipeline_version` for replay.

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| Upload session create success | API health |
| Presign → PUT conversion rate | Client/UX issues |
| Time-to-READY p50/p99 | Customer SLO |
| Scan fail rate | Attacks / false positives |
| Queue depth per stage | Bottleneck |
| Variant error rate | Bad deploys |
| CDN hit ratio | Cost/perf |
| Bytes uploaded per tenant | Abuse |
| Quarantine count | Safety |

Trace `image_id` across stages. Never log raw image bytes.

#### 5.3.3 Testing & game days

- Malware sample in test harness (safe fixtures).  
- Image bombs.  
- Worker kill mid-pipeline.  
- Scan outage (must not serve unscanned).  
- Delete + CDN cache behavior.  
- Regional bucket outage.

#### 5.3.4 Security & compliance

- Buckets private; block public ACLs.  
- KMS encryption.  
- Separate quarantine account/prefix optional.  
- IAM: API can create presign only; workers limited paths.  
- Signed CDN for private content.  
- Legal hold / retention tooling.  
- Access audit for employee viewing.

### 5.4 Progressive scale deep dive

**MVP:** Presign to S3, ObjectCreated → SQS, ClamAV/managed malware scan, Sharp/libvips variants, Dynamo metadata, CloudFront signed/public, basic quotas.  

**10×:** Stage-specific worker pools; DLQ; lifecycle rules; metadata caching; multipart for large; WebP defaults.  

**100×:** Regional ingest buckets; async replication of derived; cell routers for metadata; T&S scoring service; origin shield; storage class transitions (IA/Glacier for old originals).  

**1,000×:** Fingerprint dedup; ML policy classifiers; dedicated processing for whales; global capacity planning for scan farm; automated takedown; analytics lake for abuse.

### 5.5 EXIF & privacy policy (say aloud)

Default strip: GPS, device serials, personal tags.  
Keep: orientation (or apply orientation and strip).  
Product exceptions (e.g. camera app) require explicit consent + review.

### 5.6 Cost controls

- Generate only needed variants.  
- Prefer modern codecs (WebP/AVIF) for delivery.  
- CDN caching with immutable URLs.  
- Lifecycle originals after N days if only variants needed (product-dependent).  
- Abort incomplete multipart.  
- Cap max resolution.

### 5.7 Deal-breaker gallery

| Deal-breaker | Fix |
|--------------|-----|
| App server proxies all bytes | Presigned direct upload |
| Public bucket for simplicity | Private + CDN |
| Serve before scan | READY gate |
| Unbounded resize params | Allowlist variants |
| Trust `Content-Type` header | Magic bytes + decode |
| No pixel limits | Megapixel caps |
| Metadata in bucket only | Queryable metadata DB |
| Forever retention silent | Lifecycle + product policy |
| Signed URL with 1-year TTL for private | Short TTL / cookies |
| Single global queue | Shard + priority |

---

## 6. Wrap-Up

### 6.1 Key decisions

1. Presigned direct-to-S3 uploads with constrained policies.  
2. Async pipeline: scan → validate → variants → READY gate.  
3. Private buckets + CDN delivery; signed URLs for private.  
4. Metadata state machine with conditional transitions.  
5. EXIF privacy defaults; abuse quotas.  
6. Regional ingest at scale; home-cell metadata.  
7. Cost via codecs, cache hits, lifecycle.

### 6.2 Top risks

| Risk | Mitigation |
|------|------------|
| Malware served | READY only after scan; fail closed on scan outage |
| Private leak | Authz on URL minting; separate distributions |
| Processing meltdown | Autoscale + priority + shed bulk |
| Storage bankruptcy | Lifecycle + caps + dedup |
| Abuse bandwidth | Session rate limits + tenant quotas |
| Image bombs | Decode limits |

### 6.3 45-minute interview plan

| Minutes | Focus |
|---------|-------|
| 0–5 | Clarify presign, scan, variants, privacy |
| 5–12 | Estimation: Gbps ingest, PB storage, view egress |
| 12–22 | HLD: API, S3, pipeline, CDN, metadata |
| 22–32 | Deep dive: scan gate, state machine, abuse |
| 32–40 | 100×/1000× regions, cost, T&S |
| 40–45 | SLOs, risks, fail-closed scan |

### 6.4 60-second pitch

> “Clients authenticate to create a short-lived presigned upload into a private bucket. Object arrival triggers an async pipeline that malware-scans, validates and strips sensitive EXIF, then builds an allowlisted set of variants. Only READY images get CDN URLs. Metadata lives in a sharded store with a strict state machine. We scale ingest with regional buckets, protect tenants with quotas, and treat scan outages as fail-closed for public serving—because trust beats thumbnail latency.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Upload protocol

1. Why presigned URLs over multipart through API servers?  
2. How do you constrain content-type and size in presigns?  
3. Multipart upload design for 25 MB+?  
4. Client disconnect mid-PUT—how cleaned up?  
5. Complete via client callback vs storage event—trade-offs?  
6. How do you prevent presign sharing/theft?  
7. Resumable uploads across networks?

### 7.2 Safety & scanning

8. Why not serve first and scan later for public content?  
9. What if the malware scanner is down?  
10. How do you handle false positives?  
11. Quarantine bucket design?  
12. How do you update virus definitions without downtime?  
13. Polyglot files (image+embedded)—detection approach?  
14. Legal/CSAM obligations—how do you talk about them in interview?  
15. NSFW ML—where in pipeline; async labels vs blocking?

### 7.3 Image processing

16. Megapixel bomb mitigations.  
17. Why libvips/Sharp over ImageMagick (ops lore)?  
18. Color profiles / orientation correctness.  
19. AVIF/WebP adoption trade-offs.  
20. Pre-generate vs on-the-fly transforms.  
21. How to make variant generation idempotent?  
22. GPU vs CPU for resize at scale?  
23. Animated GIF/WEBP—special cases?

### 7.4 Metadata & APIs

24. State machine transitions and CAS.  
25. Listing millions of images for a seller—pagination.  
26. Soft delete vs hard delete legal needs.  
27. Schema for variants array.  
28. How to expose processing progress to clients?  
29. Idempotency of create upload.  
30. Search images by visual similarity—separate system?

### 7.5 CDN & delivery

31. Immutable content-hashed URLs—benefits.  
32. Signed URL vs cookie auth at CDN.  
33. Cache invalidation strategies on delete.  
34. Hot image thundering herd at origin.  
35. Separate CDN distributions for public vs private.  
36. Geographic restriction needs.  
37. HTTP range requests for large originals?

### 7.6 Abuse & multi-tenant

38. Quotas: count vs bytes vs CPU-seconds.  
39. Detecting upload-as-CDN-abuse (hosting arbitrary files).  
40. Stolen account uploading malware—controls.  
41. Rate limiting session creates vs PUTs.  
42. Whale marketplace seller isolation.  
43. Cost attribution per tenant.  
44. Takedown SLA design.

### 7.7 Scale & multi-region

45. Regional ingest with global identity (`image_id`).  
46. Replicate originals vs regenerate variants remotely.  
47. Metadata home cell failover.  
48. Estimation: storage at 1B uploads/day.  
49. Dedup refcount races across regions.  
50. Cell migration for processing workers.

### 7.8 Reliability & ops

51. Poison image DLQ handling.  
52. Backfill regeneration when codec changes.  
53. GC orphaned objects.  
54. Game day: scan outage.  
55. Metrics that distinguish client errors vs pipeline bugs.  
56. SLO: time-to-READY vs upload API availability—separate.

### 7.9 Privacy & security

57. EXIF scrubbing policy.  
58. Employee access to user photos—controls.  
59. Bucket public ACL footguns.  
60. KMS key per tenant—when worth it?  
61. SSRF if you fetch images by URL import—risks.  
62. Encryption in transit/at rest checklist.  
63. Signed URL leakage via Referer logs.

### 7.10 Amazon ownership

64. Malware reached CDN—incident response outline.  
65. Storage cost +40% QoQ—investigation.  
66. Sellers complain variants soft—quality vs cost trade-off.  
67. Who owns T&S false positive appeals?  
68. Kill switch: disable uploads vs disable public serving.  
69. Cross-team dependency on shared scan platform.

### 7.11 Interview traps

70. Proxying all uploads through app.  
71. Public S3 bucket “temporary.”  
72. Trusting client content-type.  
73. Marking READY before scan.  
74. Unbounded dynamic resize query params.  
75. Ignoring egress costs.  
76. Single-table metadata without access patterns.  
77. Eternal multipart debris.  
78. Global strongly consistent multi-region metadata hand-wave.  
79. Logging PII EXIF.  
80. Treating images like small JSON API payloads in estimation.

### 7.12 Comparison questions

81. This design vs Amazon S3 Object Lambda transforms.  
82. vs Cloudinary/imgix style SaaS.  
83. vs uploading through API Gateway (limits).  
84. Lambda vs ECS for variants.  
85. DynamoDB vs Aurora for metadata.

---

## 8. Appendices

### 8.1 Schema sketches

```text
Image {
  image_id, tenant_id, owner_id,
  state, pipeline_version,
  content_type, bytes, sha256,
  width, height,
  original_s3, variants: [{name, s3, bytes, width, height}],
  scan_status, scan_details_id?,
  created_at, ready_at?, deleted_at?,
  visibility: PUBLIC|PRIVATE
}

UploadSession {
  image_id, tenant_id, expires_at,
  max_bytes, allowed_types[],
  created_at, consumed_at?
}

Quota {
  tenant_id, window, bytes_day, max_concurrent
}
```

### 8.2 API checklist

| API | Notes |
|-----|-------|
| `POST /v1/uploads` | Auth; returns presign + image_id |
| `POST /v1/uploads/{id}/complete` | Optional if event-driven |
| `GET /v1/images/{id}` | Status + URLs if authorized |
| `DELETE /v1/images/{id}` | Soft delete |
| `POST /v1/images/{id}/reprocess` | Admin |
| `GET /v1/owners/{id}/images` | Cursor page |

### 8.3 Bucket layout

```text
s3://ingest-{region}/o/{hashPrefix}/{image_id}/original
s3://derived-{region}/o/{hashPrefix}/{image_id}/{contentHash}/{variant}.webp
s3://quarantine-{region}/o/{image_id}/...
```

Block public access on all.

### 8.4 Presign policy sketch

```text
conditions:
  - content-length-range: 1 .. max_bytes
  - Content-Type starts-with "image/"
  - key exact match
expiry: now+10m
```

### 8.5 Pipeline pseudocode

```text
function OnObjectCreated(evt):
  meta = Meta.Cas(image_id, from=CREATED|UPLOADED, to=SCANNING)
  if scan(evt.key) == MALWARE:
     quarantine(evt.key); Meta.Set(REJECTED_MALWARE); return
  img = decode_bounded(evt.key, max_mp=...)
  strip_exif(img)
  parallel for v in variant_specs:
     write_derived(img, v)
  Meta.Cas(to=READY, variants=...)
  emit ImageReady
```

### 8.6 Glossary

| Term | Definition |
|------|------------|
| Presigned URL | Time-limited authorized storage URL |
| Variant | Derived rendition of an image |
| Quarantine | Non-serving storage for bad objects |
| READY gate | State allowing public/signed delivery |
| Image bomb | Tiny compressed file, huge decoded bitmap |
| Origin shield | Intermediate cache protecting origin |
| Content-hashed URL | URL changes when bytes change; cache-friendly |

### 8.7 Progressive scale checklist

- [ ] Presign direct upload  
- [ ] Private buckets  
- [ ] Scan before READY  
- [ ] Pixel/size limits  
- [ ] Variant allowlist  
- [ ] Metadata state machine  
- [ ] CDN strategy public/private  
- [ ] Quotas / abuse  
- [ ] EXIF privacy  
- [ ] Regional ingest story  
- [ ] Cost/lifecycle  
- [ ] Fail-closed scan outage  

### 8.8 Observability SLOs

| SLO | Example |
|-----|---------|
| Create upload API availability | 99.9% |
| Time-to-READY p99 (≤5MB) | ≤ 30s |
| Malware false-open (served) | 0 |
| Private leak incidents | 0 |
| CDN hit ratio | ≥ 90% for popular |
| Processing DLQ age | < 1h |

### 8.9 Operator runbooks (titles)

- Scan engine outage (fail closed)  
- Processing backlog / READY lag  
- Suspected malware escape  
- Storage cost anomaly  
- CDN misrouting private content  
- Tenant abuse throttle  
- Quarantine surge  
- Regional S3 degradation  

### 8.10 Interview “say this” summary

> Presign to private S3, event-driven scan+variants, READY gate, CDN delivery, metadata CAS state machine, EXIF scrub, quotas—scale with regional ingest and never proxy bytes.

### 8.11 Worked scale example (100×)

```text
Uploads: 50K/s × 2 MB ≈ 100 GB/s ingest → many regions
Variants +50% storage write amp
Workers: if 300ms CPU/image → 50K × 0.3 = 15K CPU-seconds/s → ~15K cores busy (order-of-magnitude)
CDN views dominate reads; metadata cache essential
```

### 8.12 Worked scale example (1,000×)

```text
500K uploads/s globally impossible without massive regionalization
Cell metadata; dedicated scan farms; aggressive dedup/lifecycle
Product must enforce retention & max resolution or cost explodes
```

### 8.13 Fail-closed matrix

| Outage | New uploads | Processing | Public READY promotion | Existing CDN READY |
|--------|-------------|------------|------------------------|--------------------|
| API | fail | n/a | n/a | serve |
| Scan | accept to store optional | pause | **no** | serve |
| Variant workers | accept | backlog | no | serve |
| Metadata DB | fail | pause | no | may serve cached URLs |
| CDN | ok | ok | ok | degraded |

### 8.14 Security checklist

- [ ] Block public ACLs  
- [ ] Presign TTL short  
- [ ] Magic byte validation  
- [ ] Megapixel caps  
- [ ] Scan before READY  
- [ ] EXIF GPS strip  
- [ ] Signed private URLs  
- [ ] Quarantine isolation  
- [ ] Least-privilege IAM  
- [ ] Multipart abort lifecycle  

### 8.15 Reliability test plan

1. Upload then kill workers—eventually READY exactly once.  
2. Malware fixture—REJECTED; never CDN.  
3. Scan outage—no new READY.  
4. Image bomb—reject without worker death spiral.  
5. Delete private image—signed URL fails after expiry; public invalidated.  
6. Double ObjectCreated—idempotent pipeline.

### 8.16 Related AWS map

| Concern | Service |
|---------|---------|
| Blobs | S3 |
| CDN | CloudFront |
| Metadata | DynamoDB |
| Queue | SQS |
| Workers | ECS/Lambda |
| Scan | custom / marketplace appliances |
| Events | EventBridge/S3 notifications |
| Secrets/KMS | KMS |
| WAF on API | WAF |

### 8.17 Final trap table

| Trap | Correction |
|------|------------|
| Proxy uploads | Presign |
| Public bucket | Private + CDN |
| Trust Content-Type | Sniff + decode |
| READY before scan | Fail closed gate |
| Unbounded transforms | Allowlist |
| Ignore storage math | Estimate PB & lifecycle |
| Long-lived private signed URLs | Short TTL |
| Single region forever | Regional ingest plan |

### 8.18 Amazon bar reminders

- Lead with trust & safety gate.  
- Do the storage/bandwidth arithmetic.  
- Separate interactive vs bulk SLOs.  
- Privacy defaults explicit.  
- Cost is part of the design.

### 8.19 Optional Phase-2 features

- AVIF ladder + device-aware Accept negotiation  
- Perceptual dedup  
- On-the-fly transforms with strict allowlist  
- ML moderation scores  
- Customer-managed KMS (CMK)  
- Direct browser POST policies (common form POST)

### 8.20 Minimal sequence to draw first

```text
Create → Presign → S3 PUT → Event → Scan → Variants → READY → CDN
```

Narrate invariants while drawing: private bucket, READY gate, idempotent workers.

---

*End of document — Picture Upload Service (Amazon SDE III)*
