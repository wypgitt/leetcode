# System Design: iOS Photo Gallery

> **Focus areas:** Device library sync · Resumable upload · Dedup · Derivatives · Albums · iCloud-style backup · Privacy · On-device vs cloud ML · Serve/ACL  
> **Style:** Microsoft loop — consumer media + cloud sync (OneDrive/Photos-adjacent); progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split upload / metadata / derive / ML / serve planes; never block camera-roll ACK on face clustering; correct durability & authz  
> **Interview theme:** Mobile + cloud storage HLD; often pairs with “how would the iOS client work?”

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

Goal: **bound an iOS photo gallery + cloud backup**—the phone remains the snappy local gallery; the cloud provides durable backup, cross-device sync, albums/sharing hooks, derivatives for fast browse, and eventual search (people/objects)—with privacy and quota.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | iOS Photos-like library + cloud sync/backup | Full Instagram social network |
| Local | PHPhotoLibrary / on-device cache of derivatives | Thin web-only gallery |
| Cloud | Originals + metadata + albums | Public CDN without ACL |
| ML | Async (on-device preferred for faces) | Sync face cluster in upload RPC |
| Microsoft lens | OneDrive/Photos-class; Azure Blob; Graph-ish APIs | Exact Apple private API speculation |

**Scope statement:** Design an iOS photo gallery with local-first UX, resumable cloud backup, dedup, derivatives, albums, trash/quota, and async indexing—scaled progressively.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Local gallery? | Chronological grid; years/months/days | Local index + cloud hydrate |
| F2 | Backup? | Auto when Wi-Fi (+ optional cellular) | Background upload agent |
| F3 | Media types? | Photo + short video; HEIC/JPEG/PNG | Format pipeline |
| F4 | Dedup? | Same asset shouldn’t double-store per user | Content hash per owner |
| F5 | Multi-device? | iPhone + iPad + web viewer | Sync token / change feed |
| F6 | Albums? | User albums; favorites | Membership tables |
| F7 | Sharing? | Shared album / link Phase 1.5 | ACL + tokens |
| F8 | Search? | Time, place, text, people (eventual) | Metadata + ML index |
| F9 | Faces? | Prefer on-device clustering; cloud optional | Privacy trade-off explicit |
| F10 | Edit? | Non-destructive crop/rotate | Edit sidecar; re-derive |
| F11 | Delete? | Trash 30d; restore | Soft delete + GC |
| F12 | Quota? | Per-account storage | Meter logical + physical policy |
| F13 | Offline? | Browse cached; queue uploads | Local DB + outbox |
| F14 | Live Photos / bursts? | Phase 1.5 | Paired assets |

**MVP scope:**

1. Local library browser (grid + day sections) with smooth scroll.  
2. Background **resumable upload** of originals to cloud object store.  
3. Per-owner **content-hash dedup**; skip byte upload on hit.  
4. **Derivative pipeline**: thumb, display, scrub.  
5. **Change sync**: device pulls/pushes metadata mutations (favorite, album, delete).  
6. Albums create/add/remove; favorites.  
7. Trash/restore; quota enforcement.  
8. Signed URL serve with ACL.  
9. Async object/scene labels; people search via on-device face clusters + optional server embeddings.

**Out of MVP:** cinematic editor, print store, perfect E2EE library with rich server search (call out trade-off), cross-user silent dedup of private photos.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Local scroll FPS | 60fps; no main-thread decode storms |
| N2 | Upload control-plane ACK | Fast; bytes direct to blob |
| N3 | Thumb ready after upload | p50 < 5–15s; p99 < 60s |
| N4 | Durability of backed-up originals | Object store 11-nines class |
| N5 | Library list (cloud metadata) | p99 < 100–200ms |
| N6 | Sync lag multi-device | Seconds–minutes OK |
| N7 | Privacy | Private default; ACL on every serve |
| N8 | Battery / thermal | Adaptive upload; Wi-Fi preference |
| N9 | ML search ready | Eventual (minutes–hours) |
| N10 | Offline correctness | No lost favorites/deletes (outbox) |

### 1.3 Cases

**Happy**

1. Shoot 50 photos → appear instantly local → Wi-Fi backup → thumbs on iPad later.  
2. Favorite on iPhone → syncs to iPad.  
3. Reinstall app → restore library from cloud (progressive).  
4. Duplicate import → hash hit → no second billable store.  
5. Trash → hide → GC after retention.

**Edges**

| Case | Behavior |
|------|----------|
| Upload mid-flight kill | Resume from offset / chunk |
| Hash collision (crypto) | Astronomical; still store distinct `asset_id` |
| Quota exceeded | Pause uploads; UX upsell; local keeps photos |
| Cellular expensive video | Defer / user setting |
| Shared link leaked | Revoke token; short TTL; auth optional |
| Conflicting album rename | LWW or vector clock; show both rare |
| HEIC on web | Transcode derivative JPEG/WebP |
| Live Photo pair partial | Keep pair invariant or mark incomplete |
| User disables Face ID cloud | On-device only clusters |
| Region move | Rehome library; block cross-region leakage |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 10M | 100M | 1B | 10B* |
| Photos uploaded / day | 200M | 2B | 20B | 200B |
| Avg new photos / user / day | 20 | 20 | 20 | 20 |
| Peak upload starts / s | 5K | 50K | 500K | 5M |
| Library metadata rows | 50B | 500B | 5T | — |
| Avg original size | 3 MB | 3 MB | 2.5 MB | 2 MB |
| Derivative fanout | 3–5 | 3–5 | 3–5 | 3–5 |
| Peak thumb CDN QPS | 200K | 2M | 20M | 200M |

\*Theoretical; treat as capacity planning.

**Jumps:** 10× = sharded metadata + blob multiparts; 100× = owner cells + async ML fleet; 1,000× = regional libraries, edge caches, strict lifecycle tiers.

### 1.5 Constraints & assumptions

- **Local-first:** camera roll UX never waits on cloud ML.  
- Bytes go **client → object store** (presigned), not through app servers.  
- Cross-user byte dedup of private media is a **privacy minefield**—default per-owner only.  
- Microsoft framing: Azure Blob + CDN; metadata in Cosmos/SQL; sync akin to OneDrive delta.

**Repeat-back:**

> Local-first iOS gallery with resumable cloud backup, per-owner dedup, derivatives, album/favorite sync, trash/quota, ACL’d serve, and async search—scaled via owner partitioning and separate planes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Upload bandwidth

```text
200M photos/day × 3 MB ≈ 600 PB / day raw? WAIT — recalculate:
200e6 × 3e6 bytes = 6e14 bytes = 600 TB/day ≈ 55 Gbps average
Peak 5–10× → hundreds of Gbps ingress — needs direct-to-blob + CDN egress separate
```

### 2.2 Metadata

```text
Asset row ~500 B–1 KB
50B assets × 800 B ≈ 40 PB metadata at huge scale → must shard by owner_id
Baseline 10M users × 2K photos × 800 B ≈ 16 TB — fine with sharding early
```

### 2.3 Derivatives

```text
Thumb 50 KB + display 300 KB + scrub ≈ +0.4 MB / photo
Often 10–20% of original bytes; still large at 100× → lifecycle & lazy derive
```

### 2.4 Device constraints

```text
Local SQLite/Core Data index: tens of MB–GB
Decode budget: thumbnail cache disk + memory; never full-res in grid
Background iOS time limited → chunked upload + resume essential
```

### 2.5 Bottlenecks

(1) Metadata hot partitions (2) derive backlog (3) ACL mistakes on CDN (4) battery-heavy upload (5) sync conflict UX (6) not “API QPS” alone.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| **Local library** | Instant UI, outbox | Strong on device |
| **Blob / originals** | Durable bytes | Immutable blobs |
| **Metadata** | Assets, albums, ACL | Strong per owner |
| **Derive** | Thumbs/transcodes | Eventual |
| **ML index** | Labels/embeddings | Eventual |
| **Serve** | Signed URLs / CDN | Authz at mint |

**Deal-breaker:** synchronous face clustering inside upload ACK.

### 3.2 Client architecture (iOS)

```text
┌─────────────────────────────────────────────┐
│ Photos UI (UICollectionView diffable)       │
├─────────────────────────────────────────────┤
│ Local Library Store (SQLite)                │
│  - assets, albums, thumb file cache         │
├─────────────────────────────────────────────┤
│ Sync Engine                                 │
│  - change token / delta pull                │
│  - outbox: favorite, album ops, deletes     │
├─────────────────────────────────────────────┤
│ Upload Agent                                │
│  - Wi-Fi/battery policy                     │
│  - hash → presign → chunked PUT → commit    │
└─────────────────────────────────────────────┘
         │ HTTPS                    │
         ▼                          ▼
   Metadata API              Blob (presigned)
```

### 3.3 Domain model

```text
UserLibrary { owner_id, quota_used, quota_limit, region }
Asset {
  asset_id, owner_id, content_hash, media_type,
  captured_at, width, height, orientation,
  blob_key, size_bytes, state: LOCAL_ONLY|UPLOADING|BACKED_UP|TRASHED,
  favorite, trashing_at?
}
Derivative { asset_id, kind, blob_key, bytes, ready }
Album { album_id, owner_id, title, type: USER|SYSTEM }
AlbumMember { album_id, asset_id, pos }
Share { resource_id, token_hash, role, expires_at }
Change { owner_id, seq, type, payload }  // sync feed
```

### 3.4 Upload protocol

```text
1. Client computes sha256 (streaming)
2. POST /v1/assets:intent {hash, size, mime, captured_at, device_asset_id}
   → {asset_id, upload: SKIP|PRESIGN{url, headers, chunk_plan}}
3. If PRESIGN: PUT chunks (or single PUT); optional block list commit
4. POST /v1/assets/{id}/complete {etag/checksum}
5. Server verifies size/hash; marks BACKED_UP; enqueues derive + ML
6. Client stores cloud asset_id ↔ local id mapping
```

**Idempotency:** `(owner_id, device_asset_id)` and/or content hash for skip.

### 3.5 Sync protocol

```text
GET /v1/library/delta?since={token}
→ {changes[], new_token, reset?: bool}

POST /v1/library/mutations  (batch outbox)
  Idempotency-Key per batch
→ apply with per-owner seq
```

**Conflict policy (MVP):** last-writer-wins on scalar fields (`favorite`, `title`) with `updated_at` / `server_seq`; membership add/remove idempotent sets.

### 3.6 Service map

| Service | Role |
|---------|------|
| Metadata API | Assets, albums, delta, quota |
| Upload Authed | Intent + complete |
| Blob Store | Originals + derivatives |
| Derive Workers | Thumb/transcode |
| ML Workers | Labels / embeddings (optional cloud) |
| ACL / Sign | Short-lived URLs |
| CDN | Thumb/display egress |
| Quota / Billing meter | Usage events |
| GC | Trash + orphan blobs |
| Notification | Optional “backup complete” |

### 3.7 Serve & authz

```text
Client asks GET /v1/assets/{id}/content?kind=thumb
Server checks ACL → 302/JSON with signed URL (TTL 5–15 min)
CDN caches by URL (unique signature) — never public anonymous originals
```

Shared albums: membership or link token grants role `viewer|contributor`.

### 3.8 On-device vs cloud ML

| Approach | Pros | Cons |
|----------|------|------|
| On-device faces | Privacy, Apple-like story | Weaker cross-device people search unless sync embeddings carefully |
| Cloud ML | Unified search | Privacy, cost, residency |
| Hybrid | Labels cloud; faces on-device | Complexity |

**Interview stance:** default hybrid—scene/object cloud async; face clusters on-device; optional encrypted embedding sync later.

### 3.9 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Upload path | Presigned direct | Scale bandwidth |
| Dedup | Per-owner hash | Privacy |
| Sync | Delta token + outbox | Mobile-friendly |
| Derive | Async queue | Fast ACK |
| Faces | On-device MVP | Privacy bar |
| Metadata DB | Owner-partitioned | Natural shard |
| Consistency | Strong metadata; eventual derive/ML | UX truth vs search |
| Cross-region | Sticky library home | Compliance |

### 3.10 Progressive architecture

| Scale | Add |
|-------|-----|
| 1× | Single region; Blob + SQL/Cosmos; derive queue; iOS sync |
| 10× | Metadata shards; multipart; CDN; lifecycle cool/archive |
| 100× | Owner cells/stamps; ML fleet; shared album service |
| 1,000× | Multi-region homes; edge POPs; tiered storage; abuse/malware scan fleet |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
┌──────── iOS Device ────────┐
│ UI │ Local DB │ Upload/Sync│
└───────┬───────────┬────────┘
        │ meta      │ bytes (presigned)
        ▼           ▼
   ┌─────────┐  ┌──────────────┐
   │Metadata │  │ Object Store │
   │  API    │  │ (hot tier)   │
   └────┬────┘  └──────┬───────┘
        │              │ events
        ▼              ▼
   ┌─────────┐  ┌──────────────┐     ┌─────────┐
   │ Delta / │  │ Derive + ML  │────▶│ Search  │
   │ Quota   │  │  workers     │     │ index   │
   └─────────┘  └──────────────┘     └─────────┘
                       │
                       ▼
                ┌──────────────┐
                │ CDN + Sign   │
                └──────────────┘
```

### 4.2 Upload sequence

```text
iOS                 Metadata           Blob
 |--intent(hash)-->|                   |
 |<--presign/SKIP--|                   |
 |---PUT chunks----------------------->|
 |--complete------>|--head/verify----->|
 |                 |--enqueue derive   |
 |<-backed_up------|                   |
```

### 4.3 Cell topology (100×)

```text
Global Directory: owner_id → {region, cell}
Each cell: Metadata + queues + cache
Blob: global namespace with region buckets; copies for DR
Derive/ML: consume cell-local queues
```

### 4.4 Delete / GC

```text
User trash → asset.state=TRASHED, trashing_at=now
Restore before T → ACTIVE
GC worker: soft-delete → remove memberships → unlink blobs if refcount 0
Derivatives GC with originals; CDN purge best-effort
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Local capture never blocked on cloud.  
2. After `complete` ACK, original is durable and checksum-verified.  
3. Dedup skip never deletes the user’s only logical asset row.  
4. ACL checked at URL mint time (and ideally token scoped).  
5. Outbox mutations eventually apply or surface error; no silent drop.  
6. Trash retention honored before hard delete.  
7. Quota cannot go permanently negative without reconciliation.

**Failure handling**

| Failure | Mitigation |
|---------|------------|
| Upload interrupt | Resume chunks; intent lease TTL |
| Complete before all chunks | Reject; client retries |
| Derive poison message | DLQ; asset still browsable via original |
| Delta token invalid | `reset=true` full hydrate (paginated) |
| Clock skew on LWW | Prefer server_seq |
| Blob bitrot | Checksums; periodic scrub |

**Degraded modes:** upload pause; browse local-only; serve originals if thumb missing; search delayed banner.

### 5.2 Scalability

**Partition:** `owner_id` for metadata and change feed. Albums co-located with owner; shared albums get their own id with member index.

**Hot users:** photographers—paginate aggressively; rate-limit upload starts; separate large-video path.

**10×:** shard metadata; CDN; multipart; connection pools.  
**100×:** cells; per-cell derive; search index per cell/region.  
**1,000×:** storage tiers (hot/cool/archive); intelligent derive (lazy beyond thumb); regional upload affinity; malware scanning async.

**Backpressure:** limit concurrent uploads per device; server 429 on intent; shed ML before derive before accept-complete (never lose accepted bytes).

### 5.3 Maintainability

- Clear client/server contracts: intent/complete/delta/mutations.  
- Feature flags: cellular upload, cloud faces, shared albums.  
- Schema evolution: additive asset fields; derivative kinds enum.  
- Observability: `upload_success_ratio`, `derive_lag_p99`, `delta_reset_rate`, `quota_block_rate`, `signed_url_4xx`.  
- Security reviews on share links.  
- LLD follow-on: `Asset`, `Album`, `SyncEngine`, `UploadSession`, `DerivativeJob`.

### 5.4 Privacy & security

- Private by default.  
- Signed URLs short TTL; no bare public containers.  
- Face data: prefer on-device; disclose cloud processing.  
- EXIF strip options on shared derivatives (GPS).  
- Malware/CSAM scanning obligations—async pipeline with legal process (mention carefully).  
- Auth: Sign in with Apple / Entra / OAuth; device attestation optional.

### 5.5 Consistency model

| Data | Model |
|------|-------|
| Asset row after complete | Strong |
| Favorite/album via outbox | Causal per owner (seq) |
| Derivatives | Eventual |
| Search | Eventual |
| Multi-device same field | LWW / server_seq |
| Shared album members | Strong membership; eventual listing |

### 5.6 iOS-specific deep dive

**Photos framework integration:** optional read from system photo library vs app-owned library—clarify with interviewer. Two modes:

1. **App sandbox library** (simpler ownership).  
2. **Integrate PHPhotoLibrary** (user permissions; background limited).

**Background upload:** `URLSession` background sessions; exponential backoff; respect Low Power Mode.

**Thumb pipeline:** generate local thumb immediately; replace/cloud-pull display sizes later.

**Memory:** downsample; `NSCache` + disk; purge on warnings.

### 5.7 Dedup nuances

```text
Per-owner: same hash → reuse blob_key; new asset_id OR refresh metadata only
Cross-user: DO NOT silently share blob without encryption strategy
Perceptual near-dup: suggestions only (“keep both?”)
```

### 5.8 Quota accounting

```text
On complete: +original_bytes (+ maybe derivatives policy)
On trash GC: -bytes when hard-deleted
Dedup hit: +0 physical; policy choice on logical billing
Reconcile worker vs meter events
```

---

## 6. Wrap-Up

### 6.1 Summary

**Local-first iOS gallery** + **presigned resumable backup** + **owner-sharded metadata** + **async derive/ML** + **delta sync** + **ACL’d CDN**. Privacy-preserving face story; progressive cells at scale.

### 6.2 Trade-offs to say aloud

1. On-device vs cloud faces.  
2. Per-owner vs cross-user dedup.  
3. LWW sync vs CRDTs.  
4. Eager vs lazy derivatives.  
5. App-owned library vs system Photos integration.

### 6.3 Build order

Local grid + SQLite → upload intent/complete → delta sync favorites → derive thumbs → albums → trash/quota → search.

### 6.4 Risks

| Risk | Mitigation |
|------|------------|
| Data loss perception | Checksums; backup status UX; restore drills |
| ACL bug | Mandatory authz tests; signed URL scope |
| Battery drain | Adaptive scheduler |
| Derive backlog | Priority thumbs; lazy others |
| Delta reset storms | Compact change log; snapshots |

### 6.5 Close

> Keep the camera-roll path sacred; cloud is durable backup and sync—never block UX on ML—and scale by owner cells with bytes off the app tier.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product / scope

**Q: Is this iCloud Photos or Google Photos?**  
A: Clarify; this doc is iOS client + cloud backup/sync with Photos-like UX.

**Q: Must web work in MVP?**  
A: Viewer nice-to-have; mobile sync first.

### 7.2 Technical

**Q: Why presigned uploads?**  
A: App servers can’t afford multi-Gbps media; direct blob scales.

**Q: How resume works?**  
A: Chunk/block IDs; server lists missing; client PUT remainder.

**Q: How do you prevent IDOR on thumbs?**  
A: Authz before sign; object keys unguessable; token binds asset_id.

**Q: Sync conflict favorite flip?**  
A: server_seq LWW; rare UX flicker acceptable MVP.

### 7.3 Scale

**Q: 10×?** Shards + CDN + multipart.  
**Q: 100×?** Cells + ML fleet + shared album service.  
**Q: 1,000×?** Tiered storage, regional homes, lazy derive.

### 7.4 Microsoft-flavored

**Q: Azure mapping?**  
A: Blob Storage + CDN; Cosmos DB for metadata; Service Bus/Event Grid for derive; Azure AD auth; Front Door; Functions for GC.

**Q: Compliance?**  
A: Region home; GDPR delete pipeline; retention for trash; DLP for shares.

### 7.5 Traps

| Trap | Better |
|------|--------|
| Proxy all bytes via API | Presign |
| Sync face cluster in upload | Async / on-device |
| Cross-user dedup casually | Privacy risk |
| Strong consistency search | Eventual OK |
| Ignore iOS background limits | Resume design |
| Public container “for speed” | Never |

### 7.6 Related prompts

- Dropbox / OneDrive  
- Google Photos  
- Image CDN / derivative pipeline  
- Offline-first mobile sync  
- Shared album ACL

---

## 8. Appendices

## Appendix A — API sketch

```http
POST   /v1/assets/intent
POST   /v1/assets/{asset_id}/complete
GET    /v1/assets/{asset_id}
GET    /v1/library/delta?since=TOKEN
POST   /v1/library/mutations
POST   /v1/albums
POST   /v1/albums/{id}/members
POST   /v1/assets/{id}/trash
POST   /v1/assets/{id}/restore
GET    /v1/assets/{id}/content?kind=thumb|display|original
GET    /v1/quota
```

## Appendix B — Metadata schema (SQL-ish)

```sql
CREATE TABLE assets (
  asset_id UUID PRIMARY KEY,
  owner_id TEXT NOT NULL,
  content_hash BYTEA NOT NULL,
  media_type TEXT NOT NULL,
  captured_at TIMESTAMPTZ,
  blob_key TEXT,
  size_bytes BIGINT,
  state TEXT NOT NULL,
  favorite BOOLEAN NOT NULL DEFAULT false,
  server_seq BIGINT NOT NULL,
  trashing_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX assets_owner_captured ON assets(owner_id, captured_at DESC);
CREATE UNIQUE INDEX assets_owner_device ON assets(owner_id, device_asset_id);

CREATE TABLE albums (
  album_id UUID PRIMARY KEY,
  owner_id TEXT NOT NULL,
  title TEXT NOT NULL,
  server_seq BIGINT NOT NULL
);

CREATE TABLE album_members (
  album_id UUID NOT NULL,
  asset_id UUID NOT NULL,
  pos DOUBLE PRECISION,
  PRIMARY KEY (album_id, asset_id)
);

CREATE TABLE library_changes (
  owner_id TEXT NOT NULL,
  seq BIGINT NOT NULL,
  payload JSONB NOT NULL,
  PRIMARY KEY (owner_id, seq)
);
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Local DB, resume upload, metadata, derive, delta sync |
| 10× | Shards, CDN, multipart, lifecycle |
| 100× | Cells, ML fleet, share service |
| 1,000× | Tiering, regional homes, abuse/malware, lazy derive |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Intent | Upload reservation / dedup check |
| Complete | Finalize after bytes durable |
| Derivative | Thumb/display rendition |
| Delta token | Sync cursor |
| Outbox | Client pending mutations |
| Library home | Region/cell sticky placement |
| Refcount | Blob sharing within owner |

## Appendix E — Estimation cheat-sheet

```text
ingress_Bps ≈ photos/s × avg_bytes
metadata_shards ∝ owners
derive_jobs ≈ uploads × renditions
CDN_QPS dominated by thumbs not originals
```

## Appendix F — State machines

```text
Asset: LOCAL_ONLY → UPLOADING → BACKED_UP → TRASHED → HARD_DELETED
UploadSession: OPEN → COMPLETED | EXPIRED
Derivative: PENDING → READY | FAILED
ShareLink: ACTIVE → REVOKED | EXPIRED
```

## Appendix G — Conflict matrix

| Field | Policy |
|-------|--------|
| favorite | LWW server_seq |
| album title | LWW |
| album membership | Idempotent add/remove set |
| trash | Trash wins if either side trashed (define) |
| caption | LWW or CRDT text later |

## Appendix H — Invariant tests

| Test | Expect |
|------|--------|
| Kill mid-upload | Resume completes; one blob |
| Dedup retry | SKIP path; one physical |
| Favorite offline | Applies after reconnect |
| Signed URL expiry | 403 after TTL |
| Cross-user fetch | 404/403 |
| Trash GC | Bytes reclaimed after retention |
| Quota block | Intent rejected; local intact |

## Appendix I — Runbook

1. Derive lag high → scale workers; priority thumbs.  
2. Delta reset spike → investigate token breakage / compaction.  
3. Upload 5xx → check Blob throttling; backoff clients.  
4. ACL incident → revoke signing keys; rotate.  
5. Quota drift → run reconciler; freeze billing emails.

## Appendix J — iOS class sketch (LLD hook)

```text
LibraryStore
UploadManager (sessions, hash, background URLSession)
SyncEngine (token, outbox, conflict resolver)
ImagePipeline (decode, cache, downsample)
GalleryViewModel
```

## Appendix K — Azure mapping

| Concern | Azure |
|---------|-------|
| Bytes | Blob Storage (+ hierarchical namespace) |
| CDN | Azure CDN / Front Door |
| Metadata | Cosmos DB (partition owner_id) |
| Queues | Service Bus / Event Grid |
| Workers | AKS / Container Apps |
| Identity | Entra ID / Sign in with Apple federation |
| Monitor | App Insights |

## Appendix L — Privacy talking points

```text
- Private default
- On-device faces preferred
- Strip GPS on shared derivatives (setting)
- Clear retention for trash & deleted accounts
- No cross-user perceptual clustering in MVP
```

---

*End of design doc. Open with local-first + planes §3.1; whiteboard upload §3.4 + sync §3.5; close with privacy §5.4 and traps §7.5.*
