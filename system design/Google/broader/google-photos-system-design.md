# System Design: Google Photos

> **Focus areas:** Upload · Dedup · ML indexing (face/object) · Albums · Sharing · Backup · Search by face/object · Library sync  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (PB library, upload QPS, embedding index), split upload/metadata/ML/search/serve planes, deal-breakers for “synchronous face cluster in upload request”  
> **Interview theme:** Google L5+ consumer media library — DB choice (metadata vs blob vs vector index), partitioning by `owner_id`, ambiguity over Google internals

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

Goal: **bound the product**—a **Google Photos–class** library: users back up photos/videos from devices, the system deduplicates, stores durable originals (+ derivatives), runs **async ML** for faces/objects/scenes, supports albums & sharing, and enables search (“beach”, “Mom”, “screenshot”).

### 1.0 What this is / is not

| Dimension | **Google Photos (this doc)** | Not this |
|-----------|------------------------------|----------|
| Primary job | Backup library + organize + search + share | Full social network / Stories ads |
| Success | Never lose memories; findable; private by default | Perfect pro DAM / Lightroom |
| Write path | Device backup upload; resumable | App server byte proxy |
| ML | Async index; eventual searchability | Face labels before ACK upload |
| Serve | CDN thumbs/derivatives; ACL | Public CDN without authz |
| Dedup | Content hash (+ perceptual) | Cross-user silent merge (privacy) |

**Scope statement:** Design Google Photos: upload/backup, dedup, derivative pipeline, ML indexing, albums/sharing, and face/object search—at progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What media? | Photos + short videos; HEIC/JPEG/PNG/RAW light | Format matrix; video hooks |
| F2 | Backup? | Auto backup from phone; Wi-Fi preference | Device sync agent; resumable |
| F3 | Dedup? | Same file shouldn’t double charge/store | Per-owner hash; careful cross-user |
| F4 | Library UX? | Chronological; months/years; favorites | Time index by owner |
| F5 | Albums? | User albums + auto (trip) Phase 1.5 | Album membership table |
| F6 | Sharing? | Link share; shared album multi-contributor | ACL + invite; link tokens |
| F7 | Search? | Text, object, face clusters, place/time | ML embeddings + metadata facets |
| F8 | Faces? | Cluster similar faces; user can label | Privacy: on-device option mention |
| F9 | Edit? | Rotate/filters non-destructive | Edit sidecar; derived re-gen |
| F10 | Delete? | Trash 30–60d; restore | Soft delete + GC |
| F11 | Quota? | Storage quota per account | Metering on logical + physical policy |
| F12 | Partner sharing / locked folder? | Phase 1.5 hooks | Extra ACL vault |

**MVP functional scope:**

1. **Device backup upload** (resumable) → durable blob store.  
2. **Per-owner dedup** by cryptographic hash; optional perceptual near-dup suggestions.  
3. **Derivative pipeline**: thumb, display sizes; EXIF strip on share derivatives.  
4. **Library listing** by time with pagination.  
5. **Albums** create/add/remove; **share** album or link.  
6. **Async ML**: object/scene labels + face embeddings → clusters.  
7. **Search**: text keywords, objects, people (labeled clusters), time/place filters.  
8. Trash/restore; quota enforcement.  
9. CDN serve with **ACL-aware** signed URLs.

**Out of MVP:**

- Full cinematic video editor  
- Perfect on-device-only E2E encrypted library with server search (hard tradeoff — mention)  
- Print store / merch  
- Cross-Google Drive unified namespace deep merge  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability | “Never lose” bar | 11 nines class object store; checksums |
| N2 | Upload ACK | Fast return to camera roll | Control plane ms; bytes direct |
| N3 | Thumb ready | Quick library browse | p50 < 5–15s; p99 < 60s |
| N4 | ML search ready | Eventual OK | p50 < minutes; backlog OK hours |
| N5 | Library list latency | Instant scroll | p99 < 100–200ms |
| N6 | Privacy | Private default | ACL on every serve; ML isolation per owner |
| N7 | Availability | High for backup/serve | Multi-AZ; regional libraries |
| N8 | Consistency | Strong ownership/ACL | Search index eventual |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Phone on Wi-Fi backs up 200 photos → uploads → thumbs appear → later searchable “dog”.  
2. User creates album “Hawaii” → shares link → friend views derivatives only.  
3. Duplicate camera roll retry → hash hit → skip bytes; metadata refresh.  
4. User labels face cluster “Ada” → search “Ada” returns photos.  
5. Trash photo → hidden → GC after retention if not restored.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload offline | Local queue; resume later |
| Partial upload | Resumable chunks; no library entry until complete+commit |
| HEIC on web | Transcode derivative JPEG/WebP |
| Burst 1,000 photos | Fair queues; backoff; Wi-Fi-only mode |
| Shared album spam | Rate limits; moderation; owner ACL |
| Face miscluster | User split/merge controls; reindex |
| Cross-user identical wedding photo | **No silent global dedup merge** of libraries |
| Quota exceeded | Stop backup; notify; partial policy |
| Copyright / CSAM | Mandatory scanning hooks; legal hold |
| EXIF GPS on shared link | Strip or policy prompt |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users (MAU) | 100M | 1B | — | global |
| Photos uploaded/day | 500M | 5B | 50B | — |
| Avg photo size | 3 MB | 3–4 MB | 4 MB | HEIC/RAW mix |
| Library photos/user p50 | 5K | 5–10K | 10K+ | — |
| Peak upload Gbps | 50 | 500 | 5K | cell fabric |
| Derivative jobs/s | 10K | 100K | 1M | fleets |
| ML infer jobs/s | 5K | 50K | 500K | accelerator cells |
| Search QPS | 20K | 200K | 2M | 20M |
| Shared link QPS | 50K | 500K | 5M | CDN |

**What each jump forces:**

- **10×:** Regional upload; ML batching on GPU; search sharding by owner; CDN thumbs.  
- **100×:** Cell-per-geo libraries; embedding indexes per cell; fair backup schedulers.  
- **1,000×:** On-device ML assists; hierarchical cold storage; approximate ANN at huge cardinality.

### 1.5 Etc. (Constraints & Assumptions)

- Videos share blob/derivative patterns with shorter ML (thumbnail + ASR Phase 2).  
- Face grouping is **per-account** (or per-household sharing unit)—not a global face DB.  
- Safety scanning may be legally required; design a gated pipeline without detailing illicit content.

**Scope statement to repeat back:**

> Design Google Photos: resumable backup uploads to durable storage with per-owner dedup, async derivatives and ML indexing for objects/faces, album/sharing ACLs, and faceted search—keeping upload ACK fast, search eventual, and private-by-default serving via signed CDN URLs—scaling via owner-partitioned metadata and regional cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Backup uploads** | Bytes to blob | 50 Gbps order | Object store |
| **Commit/metadata** | Create media rows | ~10–50K/s | SQL |
| **Derivative jobs** | Thumbs | ~10K/s | Workers |
| **ML jobs** | Embeddings/labels | ~5K/s | GPU pool |
| **Library reads** | Timeline | ~100K/s | SQL+cache |
| **Search** | Query | ~20K/s | Index |
| **Serve bytes** | Thumbs/full | multi-Tbps | CDN |

### 2.2 Storage math

```text
500M photos/day × 3 MB = 1.5 PB/day originals
Derivatives ~0.3–0.5× → +0.5–0.75 PB/day
Monthly ~45–70 PB growth order (before dedup/compression/cold tier)
Dedup saves some; RAW/video dominate outliers
Must: lifecycle tiers (hot thumbs, warm display, cold original)
```

### 2.3 Dedup savings

```text
Exact hash dedup per owner: saves re-uploads / retries (high UX), modest global storage
Global byte dedup across users: large savings but privacy/legal/complexity — usually
  content-addressed with careful refcounts OR avoided for private libraries
Interview: prefer per-owner exact; mention global only for public/stock
```

### 2.4 ML / embedding math

```text
Face embedding 512-d × 4B = 2 KB/face chip
10 faces/photo average sparse — say 0.5 face/photo overall
500M photos/day × 0.5 × 2 KB = 500 GB/day face vectors (order)
ANN indexes sharded by owner_id — never one global mega-index of all humans
Object labels: posting lists per owner or global vocab with owner postings
```

### 2.5 Search

```text
Query “dog” → owner-scoped posting list intersect time filters
People search → cluster_id → media_ids
Latency: owner shard local; cache frequent
```

### 2.6 Sharing amplification

```text
Viral shared album: read-heavy
Precompute authorized derivative URLs / cookies
CDN with signed access; metadata cached
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/media:upload` | Start resumable backup session |
| `POST /v1/media:complete` | Commit; enqueue processing |
| `GET /v1/library` | Timeline page `{before_ts, limit}` |
| `POST /v1/albums` | Create album |
| `POST /v1/albums/{id}/media` | Add media |
| `POST /v1/albums/{id}/share` | Create share / link |
| `GET /v1/search?q=` | Text/object/people |
| `POST /v1/people/{cluster}/label` | Name a face cluster |
| `POST /v1/media/{id}:trash` | Soft delete |
| `GET /v1/media/{id}/url` | Mint signed URL for rendition |

### 3.2 Data model

| Entity | Key | Store | Notes |
|--------|-----|-------|-------|
| MediaItem | `media_id` | Spanner-like | owner, ts, hash, state, geo |
| BlobRef | `hash` / `blob_id` | Object store | bytes |
| Rendition | `(media_id, type)` | Object paths | thumb/display |
| Album | `album_id` | SQL | owner, title |
| AlbumMember | `(album_id, media_id)` | SQL | order |
| ACL / Share | `share_id` | SQL | link token hash, perms |
| FaceCluster | `(owner_id, cluster_id)` | SQL | label optional |
| FaceObs | `(media_id, face_id)` | SQL + vec | embedding ref |
| LabelPosting | `(owner_id, label)` | Search index | media ids |
| Trash | `media_id` | SQL | delete_at |

**States:** `UPLOADING → COMMITTED → SCAN_OK → DERIV_READY → ML_PENDING → INDEXED` (flags can be bitset).

### 3.3 Dedup — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Per-owner SHA-256** | Simple; private | Misses re-encodes | **MVP exact** |
| Perceptual hash (pHash) | Near-dup | False positive merges | Suggest only |
| Global content-addressed store | Storage $ | Privacy/refcount hell | Careful platforms |
| No dedup | Simple | Quota pain; waste | Tiny systems |

**Chosen:** Exact per-owner dedup on commit; perceptual **suggestions** not auto-delete.

### 3.4 ML indexing — Why X over Y

| Approach | Pros | Cons | Deal-breaker? |
|----------|------|------|---------------|
| Sync ML in upload | Instant search | Latency/cost melt | **Yes for MVP ACK** |
| **Async queues** | Fast backup UX | Eventual search | **Chosen** |
| On-device ML only | Privacy | Weak server search; device variance | Option / hybrid |
| One global face DB | — | Privacy nightmare | **Deal-breaker** |

### 3.5 Search architecture — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| SQL `LIKE` | — | No scale/semantic |
| **Inverted labels + facets** | Solid MVP | Scenes limited by vocab |
| **ANN embeddings** | Semantic “beach sunset” | Ops; ANN recall |
| External Elasticsearch only | Familiar | Owner isolation / multi-tenant care |

**Chosen:** Metadata facets + label postings + per-owner face ANN / cluster lookup; optional CLIP-like embedding index Phase 1.5.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Upload | Direct-to-blob | Scale | API proxy bytes |
| Dedup | Per-owner hash | Privacy | Silent cross-user library merge |
| ML | Async | UX | Sync face cluster on upload |
| Faces | Per-owner clusters | Privacy | Global biometric DB |
| Serve | Signed CDN | ACL | Public URLs for private |
| Metadata DB | Distributed SQL | ACL/tx | Dumb KV without indexes |
| Search | Owner-scoped indexes | Isolation | One shared unscoped ES |

---

## 4. Architecture Diagram

```text
 Device backup agent
        |
        | resumable PUT
        v
 +--------------+     complete      +------------------+
 | Object Store | ----------------> | Media Metadata   |
 | (originals)  |                   | Service (SQL)    |
 +------+-------+                   +--------+---------+
        |                                    |
        | jobs                               | library/search API
        v                                    v
 +--------------+     embeddings     +------------------+
 | Derivative   | -----------------> | ML Indexer       |
 | Workers      |                    | (GPU)            |
 +------+-------+                    +--------+---------+
        |                                     |
        | thumbs                              | labels/faces
        v                                     v
 +--------------+                    +------------------+
 | CDN (signed) |                    | Search Index     |
 +--------------+                    | owner-sharded    |
        ^                            +--------+---------+
        |                                     ^
   Share/ACL mint ----------------------------+
```

**Backup path:**

```text
device scans local gallery
  -> skip if hash known (server check)
  -> resumable upload blob
  -> complete(media metadata, EXIF time/gps)
  -> enqueue Scan + Deriv + ML
  -> show in library as processing/ready
```

**Search path:**

```text
query parse (people vs text vs date)
  -> retrieve candidates owner-scoped
  -> fuse rank (time proximity, confidence)
  -> return media ids + mint thumb URLs
```

**Share path:**

```text
create share link (token hash stored)
  -> viewer presents token
  -> authz album membership
  -> signed URLs for allowed renditions (EXIF-stripped)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No library commit without durable bytes + checksum.**  
2. **ACL checked on every URL mint**; share tokens hashed at rest.  
3. **Soft delete restores** until GC; legal hold blocks GC.  
4. **ML/index eventual** — upload success ≠ searchable yet (surface status).  
5. **Face data scoped to owner** (or explicit household graph).  
6. **Derivatives never become sole copy** of original until policy says so.

#### 5.1.2 Commit protocol

```text
upload bytes -> durable
CompleteUpload RPC:
  begin tx
    if hash exists for owner: reuse blob_id; refcount++
    else register blob
    insert media row COMMITTED
  commit
  enqueue jobs (at-least-once)
Idempotency-Key on complete prevents double rows
```

#### 5.1.3 Job reliability

| Job | Failure handling |
|-----|------------------|
| Virus/safety scan | Block READY_PUBLIC/SHARE; retry; quarantine |
| Derivatives | Retry; poison queue |
| ML | Retry; search lag metrics |
| Index update | Idempotent upsert by media_id |

#### 5.1.4 Sharing risks

- Rotating link tokens; revoke.  
- Password-optional shares Phase 1.5.  
- Contributor shared albums: write ACL separate from read; conflict on deletes.  
- Strip GPS from shared derivatives by default.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Deriv backlog | Autoscale workers |
| 10× | ML GPU starve | Batch infer; priority for recent |
| 100× | Hot celebrity shared album | CDN; cache ACL grants |
| 1,000× | Reindex migration | Shadow indexes; owner canaries |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| `owner_id` | Primary shard key for library/search/faces |
| `media_id` | Unique; hash for blob path |
| Time buckets | Timeline pagination `(owner_id, captured_at)` |
| Geo cell (optional) | Place search |
| Album_id | Membership; may secondary index |

**Critical:** almost all user queries are **single-owner** — shard by owner for locality.

#### 5.2.2 Face clustering

```text
On new face embedding e for owner O:
  ANN query top neighbors in O's index
  if sim >= T: assign cluster
  else: new cluster
Periodic reclustering (connected components) for quality
User ops: merge/split clusters → write constraints → local rebuild
```

**Deal-breaker:** clustering all users’ faces in one global graph.

#### 5.2.3 Object / scene labels

- CNN/detector → top labels with confidence.  
- Posting list: `(owner_id, label) → postings`.  
- Global vocab; owner-partitioned postings storage.

#### 5.2.4 Semantic search (Phase 1.5)

- Image embedding (CLIP-like).  
- Text query → embedding → ANN within owner shard.  
- Hybrid: keyword ∪ ANN; rank fusion.

#### 5.2.5 Storage tiers

| Tier | What |
|------|------|
| Edge/CDN | Hot thumbs |
| Standard object | Recent originals + display |
| Cold | Older originals rarely viewed |
| Archive | Optional deep archive |

#### 5.2.6 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Owner shards; GPU batch; CDN signed; scan gates |
| →100× | Regional cells; ANN per cell; fair backup; cold tier |
| →1,000× | On-device pre-embed; hierarchical storage; approximate search everywhere |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
derivatives: [thumb_256, display_2048, webp]
ml:
  face_dim: 512
  face_threshold: 0.78
  recluster_every: 7d
share:
  default_strip_gps: true
  link_ttl_optional: true
trash_retain_days: 60
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `backup_success_rate` | Core promise |
| `time_to_thumb` | Browse UX |
| `time_to_index` | Search UX |
| `ml_queue_depth` | Capacity |
| `dedup_hit_ratio` | Savings |
| `search_p99` / zero results | Quality |
| `share_403_rate` | ACL bugs |
| `face_user_split_merge` | Cluster quality signal |

#### 5.3.3 Testing

- Idempotent complete upload.  
- Dedup same-hash.  
- ACL: non-member cannot mint URL.  
- Face merge/split fixtures.  
- EXIF GPS stripped on share rendition.  
- Chaos: kill ML workers — backup still OK.

#### 5.3.4 Operability

- Model version dual-index (`ml_v3` shadow).  
- Re-embed campaigns by owner shards.  
- Feature flags for semantic search.  
- Quota repair jobs.

#### 5.3.5 On-device vs server ML (interview nuance)

| | On-device | Server |
|---|----------|--------|
| Privacy | Stronger | Need trust/policy |
| Search from web | Weak | Strong |
| Battery/CPU | Cost on phone | Cost on fleet |
| Hybrid | Upload embeddings only | Good compromise Phase 2 |

---

## 6. Wrap-Up

### 6.1 What we designed

A **Google Photos** system: resumable **backup** to durable blobs, **per-owner dedup**, async **derivatives + ML** (objects/faces), **albums/sharing** with ACL’d CDN serve, and **owner-scoped search**—upload fast, search eventual, privacy default.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Sync ML on upload | Deal-breaker |
| Global face DB | Deal-breaker |
| Cross-user silent dedup merge | Dangerous default |
| Shard key | `owner_id` |
| Search consistency | Eventual OK |
| Share GPS | Strip by default |

### 6.3 30-second scale narrative

> Baseline: direct upload, SQL metadata by owner, async thumbs+ML, inverted labels + face clusters, signed CDN. 10× forces GPU batching and search shards. 100× regional library cells and cold tiers. 1,000× on-device assists and hierarchical storage—never block backup on indexing.

### 6.4 Deal-breakers checklist

- Proxying all photo bytes through app servers.  
- Synchronous face clustering before upload ACK.  
- Global biometric identity database across users.  
- Public CDN URLs for private media without authz.  
- Table-scan search across an owner’s 1M photos.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Backup vs manual upload?**  
A: Both; backup agent is the scale driver.

**Q2: Original quality forever?**  
A: Product/quota SKU; storage tiers may recompress with consent (politically sensitive).

**Q3: Videos in scope?**  
A: Yes light — thumb + playback URL; full ABR may defer to video platform.

**Q4: Shared album contributions?**  
A: Multi-writer ACL; define who can delete.

**Q5: Memories / movies auto?**  
A: Phase 1.5 batch jobs on signals.

### 7.2 Upload & dedup

**Q6: How does device know what to upload?**  
A: Local DB of uploaded hashes/ids; server list sync delta.

**Q7: Exact vs perceptual dedup?**  
A: Exact safe auto; perceptual suggest.

**Q8: Race two devices same photo?**  
A: Idempotent complete by hash; one media or refcounted.

**Q9: Chunk size / resume?**  
A: Same as Drive/YouTube resumable patterns.

**Q10: EXIF time vs upload time?**  
A: Prefer captured_at for timeline; fallback upload_at.

### 7.3 ML & faces

**Q11: Detection vs recognition?**  
A: Detect face boxes; embed; cluster; recognition = label mapping.

**Q12: Why per-owner ANN?**  
A: Privacy + scale; queries always scoped.

**Q13: How to handle babies aging?**  
A: Soft clusters; periodic reclustering; user merges.

**Q14: Object vocab size?**  
A: Thousands of labels; confidence threshold; multi-label.

**Q15: Can search work before ML done?**  
A: Yes — filename/time/gps; degrade.

**Q16: Blind / E2E encrypted photos?**  
A: Server cannot ML search; on-device index; product tradeoff.

### 7.4 Search

**Q17: Query understanding?**  
A: Parse people names, dates (“last summer”), places, objects.

**Q18: Ranking?**  
A: Relevance × recency × quality × diversity.

**Q19: Typo / synonyms?**  
A: Vocab expansion; embeddings help.

**Q20: Screenshot vs camera?**  
A: Classifier label; filters.

### 7.5 Sharing & ACL

**Q21: Link share security?**  
A: Unguessable token; rate limit; revoke; optional login gate.

**Q22: CDN authz patterns?**  
A: Signed URL short TTL; signed cookie for album browsing.

**Q23: Remove collaborator?**  
A: ACL version++; invalidate cookies; stop minting.

**Q24: Download original vs derivative?**  
A: Permission bit; default derivative for broad links.

### 7.6 Storage & quota

**Q25: What counts toward quota?**  
A: Policy: originals + maybe versions; dedup refcount accounting.

**Q26: Trash GC?**  
A: After N days; unless legal hold / ongoing share case policy.

**Q27: Cold tier restore latency?**  
A: Minutes–hours; UI messaging.

**Q28: Why not only store thumbs?**  
A: Breaks backup promise / zoom / re-edit.

### 7.7 Data stores

**Q29: Spanner vs sharded MySQL?**  
A: Both OK; need `(owner_id, captured_at)` indexes and tx for ACL.

**Q30: Where embeddings live?**  
A: Vector store / columnar per shard; pointers in SQL.

**Q31: Bigtable for timeline?**  
A: Good for `(owner, ts)` wide rows; still need SQL for rich ACL sometimes.

**Q32: How to paginate library?**  
A: Keyset pagination on `(captured_at, media_id)` — not OFFSET.

### 7.8 Safety & compliance

**Q33: Malware in images?**  
A: Rare but scan; polyglot files.

**Q34: Abuse reporting on shares?**  
A: Report → review → takedown workflow.

**Q35: GDPR delete?**  
A: Delete media + index + embeddings; verify async.

### 7.9 Estimation drills

**Q36: 5B photos/day × 3 MB?**  
A: 15 PB/day originals — argue tiers/dedup/compression reality + regional cells.

**Q37: Search index for 10K photos/user × 1B users?**  
A: Owner shards; don’t build one monolithic index.

**Q38: Thumb CDN for 1M QPS × 30 KB?**  
A: 30 GB/s — CDN.

### 7.10 Alternatives & deal-breakers

**Q39: Store photos in DB BLOB column?**  
A: Deal-breaker at scale.

**Q40: Elasticsearch without owner filter?**  
A: Data leak risk — mandatory tenancy.

**Q41: Real-time face cluster in request?**  
A: Deal-breaker for mobile backup UX.

### 7.11 Interview craft

**Q42: How to open?**  
A: Backup durability, privacy, search eventual, share ACL — then planes.

**Q43: What impresses L5+?**  
A: Owner partitioning, async ML, face privacy scope, dedup nuance, signed serve.

**Q44: Common mistake?**  
A: Designing only ML model accuracy; ignoring upload/ACL/storage math.

---

### Appendix A — Media commit pseudocode

```text
complete(owner, hash, size, exif, idem_key):
  if seen(idem_key): return prior
  blob = find_or_put(owner, hash)
  media = insert(owner, blob, exif, state=COMMITTED)
  enqueue(Scan(media), Deriv(media), ML(media))
  return media_id
```

### Appendix B — Derivative set

```text
thumb_256.webp
display_2048.webp
download_jpeg (EXIF policy variant)
video: poster.jpg + proxy mp4 (optional)
```

### Appendix C — Face assign

```text
emb = embed(face_chip)
nbrs = ann.search(owner, emb, k=5)
if nbrs[0].sim >= T: cluster = nbrs[0].cluster
else: cluster = new_cluster(owner)
write FaceObs(media, emb, cluster)
```

### Appendix D — Search fusion

```text
cands = []
cands |= label_postings(owner, tokens)
cands |= people_postings(owner, labeled_clusters(tokens))
cands |= time_place_filters(...)
cands |= ann_semantic(owner, query)  # optional
return rank_and_page(cands)
```

### Appendix E — Share token

```text
token = random(128-bit+)
store hash(token), album_id, perms, exp
viewer: present token -> lookup -> mint signed cookie scoped to album
```

### Appendix F — Timeline keyset page

```text
SELECT * FROM media
WHERE owner=? AND (captured_at, media_id) < (?, ?)
AND not trashed
ORDER BY captured_at DESC, media_id DESC
LIMIT 100
```

### Appendix G — Progressive scale table

| Scale | Upload | ML | Search | Serve |
|-------|--------|----|--------|-------|
| Baseline | 1 region | GPU queue | Owner index | CDN |
| 10× | Multi-region | Batch | Sharded ANN | Signed edge |
| 100× | Cells | Accelerator cells | Cell indexes | Tiered store |
| 1,000× | Device assist | Hybrid embed | Approx everywhere | Deep cold |

### Appendix H — NFR card

```text
Durable originals
Upload ACK ⟂ ML complete
Thumb seconds; index minutes
Private default + signed serve
Owner-scoped faces
Trash restore window
```

### Appendix I — Quota accounting

```text
logical_usage += size if new blob else 0
or: bill unique blob bytes × refcount policy
enforce before complete if over quota
```

### Appendix J — EXIF policy

| Rendition | GPS | Camera serial |
|-----------|-----|---------------|
| Private original | Keep | Keep |
| Shared derivative | Strip | Strip |
| Public link | Strip | Strip |

### Appendix K — Auto albums (Phase 1.5)

```text
cluster by geo+time density -> trip album suggestions
user accepts -> materialize AlbumMember
```

### Appendix L — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just S3 + RDS” | Need ML/index/ACL/CDN story |
| “Global dedup saves $” | Privacy/refcount; per-owner first |
| “Search must be strong consistent” | Eventual OK if UX shows processing |

### Appendix M — Related systems

| System | Role |
|--------|------|
| Object store | Bytes |
| Distributed SQL | Media/ACL |
| Kafka | Job bus |
| GPU infer | ML |
| ANN / search | Retrieval |
| CDN | Thumbs |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| Rendition | Derived image size/format |
| Face chip | Cropped face image |
| Cluster | Set of faces likely same person (per owner) |
| Posting list | Inverted index list |
| Keyset pagination | Seek by key not OFFSET |

### Appendix O — Worked example

```text
User 20K photos; list page 100 → SQL keyset + cache
Search "Ada": cluster label -> 800 media ids -> rank by time -> mint 40 thumb URLs
Upload day 500M × 3 MB = 1.5 PB — cells + tiers mandatory narrative
```

### Appendix P — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Read-your-write library after upload? | Yes after commit |
| Search immediate? | No — eventual |
| Share revoke | Near-immediate mint fail; CDN TTL bound |
| Cross-device | Sync agent pulls metadata deltas |

### Appendix Q — 30m interview checklist

1. Clarify backup, dedup, ML, share, search, privacy.  
2. Storage math + owner shard.  
3. Async pipelines diagram.  
4. Face per-owner clustering.  
5. Signed CDN ACL.  
6. Scale jumps.  
7. Deal-breakers.

### Appendix R — Device sync agent

```text
loop:
  list local media
  diff with server checkpoint
  upload missing (wifi/battery policy)
  download remote metadata for other devices
  apply trash/ACL changes
```

### Appendix S — Model migration

```text
write embeddings to index_v2 shadow
evaluate recall@k offline
cut read path to v2 per shard
GC v1 vectors
```

### Appendix T — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Owner search shards, GPU batch, CDN |
| 100× | Regional cells, cold tier, fair schedulers |
| 1,000× | On-device hybrid ML, deep archive |

### Appendix U — Video light path

```text
upload video blob
poster + scrubbing sprites
optional proxy transcode
ML: object tags on keyframes; ASR Phase 2
```

### Appendix V — Locked folder hook

```text
vault_acl separate unlock factor
server stores encrypted DEKs
list endpoint omitted from default library
```

---

*End of Google Photos system design.*
