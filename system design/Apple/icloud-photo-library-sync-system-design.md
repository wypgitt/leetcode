# System Design: iCloud Photo Library Synchronization

> **Focus areas:** Privacy · E2E / server-blind ciphertext · Offline-first · Conflict resolution · Battery · On-device vs server split · Dedup & derivatives  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, honest MVP vs extreme-scale paths, Apple-style privacy boundaries

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

Goal: **bound the product**—what “photo library sync” means across devices, what the server may see, and which consistency model users actually need for memories, albums, and edits.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What syncs? | Originals (or optimized), edits, albums, favorites, deletions, Shared Albums optional | Separate **asset** vs **metadata** planes; tombstones for delete |
| F2 | Devices? | iPhone, iPad, Mac, Apple TV (read-heavy), web (limited) | Per-device sync agents; web may use server-side decrypt only if keys available (usually not for E2E) |
| F3 | Optimize Storage? | Keep device copies “optimized”; full res in cloud; download on demand | Local eviction policy; cloud is source of full fidelity |
| F4 | Edits? | Non-destructive edit recipes + rendered previews | Sync recipes (small) eagerly; re-render on device or cache derivatives |
| F5 | Conflict model? | Last-writer-wins on simple flags; merge albums; duplicate assets rare | CRDT-ish sets for membership; LWW with vector clocks for attrs |
| F6 | Capture offline? | Camera roll works offline; sync when network/power ok | Local-first ingest; upload scheduler battery-aware |
| F7 | Dedup? | Same photo imported twice should ideally coalesce | Content hash + perceptual hash hints; user-visible “duplicates” UI later |
| F8 | Live Photos / video? | Supported; larger blobs; streaming download | Chunked upload; resumable; separate bitrate ladders for video |
| F9 | Shared Library / Shared Albums? | Optional phase; ACL + invite | Separate share graph; still ciphertext per share key |
| F10 | Search / Memories? | On-device ML preferred; server may index only non-sensitive derived signals if Advanced Data Protection off | Prefer on-device embeddings; server-blind when ADP on |
| F11 | Delete / Recently Deleted? | Soft delete 30 days then purge | Tombstone + retention sweeper; multi-device ack |
| F12 | Auth? | Apple ID + device trust; iCloud Keychain for keys | Per-device identity keys; library master key wrapped per device |

**MVP functional scope (lock with interviewer):**

1. Capture photo/video → durable local asset → background upload of **encrypted** original + metadata.
2. Multi-device sync of library index (albums, favorites, dates, edit recipes).
3. Optimize Storage: keep thumbnails + recent full-res; fetch originals on demand.
4. Deletion with tombstones and Recently Deleted window.
5. Resumable chunked upload/download; battery/Wi‑Fi aware scheduler.
6. Conflict rules for metadata and album membership.

**Out of MVP (explicitly defer):**

- Full Shared iCloud Photo Library with complex household ACLs
- Cross-user collaborative albums with fine-grained roles
- Perfect global perceptual dedup at 1,000×
- Server-side AI Memories when Advanced Data Protection is on
- Raw Pro formats edge cases beyond “store opaque blob + recipe”

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Privacy | User content ciphertext at rest; server cannot read originals under ADP | E2E for asset bytes + sensitive metadata; server sees opaque blobs + sync envelopes |
| N2 | Upload latency | Background OK; user-visible “syncing” | New capture durable locally < 100ms; cloud durable p50 < 60s on Wi‑Fi |
| N3 | Download on demand | Open photo from optimized library | p50 < 2s Wi‑Fi for 3–5 MB; progressive |
| N4 | Battery | Must not drain overnight | Upload scheduler respects Low Power, thermal, radio state |
| N5 | Offline | Full capture + browse local subset | Zero cloud dependency for capture path |
| N6 | Consistency | Eventual across devices; no lost edits | Causal metadata sync; conflict policy documented |
| N7 | Durability | No silent loss of accepted uploads | Multi-AZ object store; checksums end-to-end |
| N8 | Availability | Sync control plane 99.9% | Degrade: local still works; sync queues |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Shoot photo on iPhone → local DB insert → encrypt → chunk upload → other devices pull index → download thumb → optional full-res.
2. Favorite on Mac → metadata mutation syncs → iPhone heart updates.
3. Edit on iPad → recipe syncs → iPhone re-renders or fetches cached derivative.
4. Optimize Storage reclaim → local original deleted → cloud retains → fetch on open.
5. Delete → tombstone → all devices hide → after retention, purge ciphertext.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Airplane mode week | Local library grows; upload backlog; resume with backoff |
| Mid-upload kill | Chunk resume via content-addressed parts + upload session |
| Two devices favorite/unfavorite | LWW on `favorite` with `(device_id, lamport)` or merge as OR-set then LWW |
| Same asset imported twice | Dedup by file hash; present one asset_id |
| Edit vs delete race | Delete wins if tombstone causal after; else restore into Recently Deleted policy |
| Key rotation / new device | Re-wrap library keys; historical ciphertext unchanged |
| Storage quota exceeded | Pause uploads; surface UX; keep local |
| Corrupted chunk | Checksum fail → re-fetch/re-upload part |
| Clock skew | Server assigns `server_seq`; devices use causal metadata, not wall clock alone |
| Shared album invitee leaves | Rekey share or drop access; ciphertext may need re-encryption for forward secrecy (phase 2) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active photo libraries | 10M | 100M | 1B | (logical cells) 1B+ |
| Photos ingested / day | 200M | 2B | 20B | 200B |
| Avg original size | 3 MB | 3 MB | 3.5 MB | 4 MB |
| Peak upload sessions | 50K | 500K | 5M | 50M |
| Metadata mutations / day | 500M | 5B | 50B | 500B |
| On-demand original fetches / day | 100M | 1B | 10B | 100M→100B |
| Thumb/derivative bandwidth | High | Very high | CDN-class | Multi-CDN / edge |
| Devices / library (avg) | 2.5 | 2.5 | 3 | 3 |

**What each jump forces:**

- **10×:** Shard libraries by `library_id`; separate metadata log from blob store; upload session service.
- **100×:** Regional blob placement; derivative factories; push wake coalescing; cell-based sync.
- **1,000×:** Hierarchical sync cursors; cold blob tiers; per-device delta compression; strict battery budgets enforced client-side.

### 1.5 Etc. (Constraints & Assumptions)

- We design **Photo Library sync**, not the Camera ISP pipeline.
- **Advanced Data Protection (ADP)** mode: server stores encrypted blobs it cannot decrypt; search/Memories on-device.
- Without ADP (standard protection), some metadata may be server-readable for features—call the trade-off explicitly in interview.
- Trust: Apple ID account + Secure Enclave device keys.
- Web access under ADP is limited unless browser holds keys (usually out of scope).

**Scope statement:**

> Design a multi-device iCloud Photo Library that is local-first for capture, encrypts asset bytes so the server can sync without reading content (ADP), optimizes on-device storage, resolves metadata conflicts, and schedules uploads/downloads under battery and network constraints—from tens of millions of libraries through progressive 10× / 100× / 1,000× scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Ingest volume

```text
Baseline: 200M photos/day × 3 MB ≈ 600 PB/day? WAIT — unit check:
200e6 × 3e6 B = 600e12 B = 600 TB/day  (not PB)
200M × 3 MB = 600 TB/day originals ingress globally

At 100×: 20B × 3.5 MB ≈ 70e9 × 3.5e6 = 245e15 B ≈ 245 PB/day
→ Must be sharded regionally; not one pipe
```

**Unit check trap:** Saying “600 PB/day” at baseline is wrong by ~1000×. Baseline is **~600 TB/day**.

### 2.2 Metadata vs blobs

```text
Per asset metadata envelope (encrypted): ~1–2 KB
200M/day × 1.5 KB ≈ 300 GB/day metadata

Edit recipes: smaller, bursty with user actions
Album membership ops: tiny, high QPS relative to bytes
```

**Critical insight:** Blob bytes dominate cost/bandwidth; **metadata QPS and conflict logic** dominate product correctness and battery (chatty sync kills radios).

### 2.3 Device-local storage

```text
User library 50k assets:
Thumbs 50k × 30 KB ≈ 1.5 GB
Optimized recent 2k × 1.5 MB ≈ 3 GB
Full originals if not optimized: 50k × 3 MB ≈ 150 GB

Optimize Storage target: keep thumbs + working set, not 150 GB
```

### 2.4 Sync traffic per device

```text
New device restore of 50k library:
Thumbs first: 1.5 GB
Metadata index: 50k × 1.5 KB ≈ 75 MB
Originals on demand over weeks/months

Daily active device:
Assume 20 new assets × 3 MB upload ≈ 60 MB
Metadata pull/push ≈ few MB
→ Radio duty cycle matters more than raw MB for battery
```

### 2.5 Control-plane QPS

```text
Libraries 10M, avg 1 sync session / 5 min while unlocked/charging subset
Hot fraction 5% → 500k devices × 12/hour ≈ 6M sessions/hour ≈ 1.7k session starts/s
Each session: cursor fetch + N mutations → amplify to ~10–50k req/s baseline metadata

1000×: cells + push coalescing mandatory
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Encrypted blob ingest & multi-region placement**
2. **Chatty metadata sync draining battery**
3. **On-demand fetch stampedes** (Memories / slideshow)
4. **Derivative generation** (thumbs, scrubbers) under privacy constraints
5. **Conflict storms** after long offline
6. **Quota / delete purge** at retention boundaries

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Library        → owned by Apple ID (or Shared Library later)
Asset          → logical photo/video; content-addressed blob refs
Rendition      → thumb / optimized / full / adjustment preview
EditRecipe     → non-destructive ops (crop, filter, exposure…)
Album / Memory → collections; membership as add/remove ops
Mutation       → signed, encrypted sync op with causal metadata
DeviceCursor   → per-device progress in library mutation log
UploadSession  → resumable chunked put of ciphertext parts
```

### 3.2 On-device vs server split

| Concern | On-device | Server |
|---------|----------|--------|
| Capture & local DB | Yes | No |
| Encryption of originals | Yes (Secure Enclave assisted keys) | Stores ciphertext only (ADP) |
| Thumb generation | Prefer on-device; may upload encrypted thumb | May store encrypted derivatives |
| Face/scene ML | On-device (privacy default) | Optional aggregates only if allowed |
| Conflict merge | Apply rules locally + via sync | Orders mutations / assigns `server_seq` |
| Blob durable store | Cache | Object store source of truth for full res |
| Battery schedule | Client OS scheduler | Provides urgency hints only |

**Deal-breaker:** Server plaintext thumbnails “for convenience” while claiming E2E under ADP.

### 3.3 Trust & key hierarchy (privacy)

```text
Device Identity Key (Secure Enclave)
   └─ wraps Library Master Key (LMK)
LMK
   ├─ Asset Content Keys (per asset or per chunk set)
   ├─ Metadata Sync Key (MSK) for mutation envelopes
   └─ Share Keys (phase 2)

New device: identity attested → unwrap LMK via iCloud Keychain / escrow per ADP rules
Server sees: wrapped key blobs, never LMK in ADP mode
```

### 3.4 Sync model options

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Periodic full snapshot | Simple | Huge; battery death | Libraries > few GB metadata |
| B. Per-asset row version + pull | Familiar | Conflicts hard; chatty | Need causal album ops |
| C. **Encrypted mutation log + cursors** | Causal, efficient deltas | Log compaction needed | — chosen |
| D. CRDT document per library | Great merge | Complex; large state | Team cannot ship CRDT runtime |

**Chosen:** Encrypted **operation log** per library shard with monotonic `server_seq`, plus client causal clocks for offline ops. Assets referenced by `asset_id` + content hash.

### 3.5 Conflict resolution policy

| Object | Strategy |
|--------|----------|
| Asset bytes | Immutable content-addressed; “edit” creates recipe, not mutate bytes |
| Favorite / hidden | LWW with `(lamport, device_id)` |
| Caption | LWW or 3-way merge with conflict clone (rare) |
| Album membership | OR-set / add-wins set; remove via tombstone tagged |
| Delete asset | Tombstone wins if causally after last edit; else quarantine UI |
| Album title | LWW |

**Invariant:** Never silently drop an original blob that any device still references without retention rules.

### 3.6 Optimize Storage

```text
Local tiers:
  T0: thumb + metadata (always)
  T1: optimized/full for recent + favorites + pinned
  T2: original (cloud); download on open / edit / share

Evict T1→cloud when disk pressure; never evict until cloud durable ACK
```

### 3.7 Upload / download scheduler (battery)

Inputs: battery %, Low Power Mode, thermal, Wi‑Fi vs cellular, user “Unlimited Cellular”, charging, backlog age, asset priority (user-initiated open ≫ background).

```text
priority = f(user_visible, age, size, network_cost)
defer if: low_power && !charging && !user_visible
prefer large uploads on Wi‑Fi + charging
coalesce radio wakes: batch metadata every T seconds
```

### 3.8 Derivatives under privacy

- Device creates encrypted thumb at ingest; uploads with asset.
- Server may **not** re-encode plaintext. Optional: server transcodes only if keys available (non-ADP) or client uploads alternate renditions.
- Video: client uploads poster + optional lower-res proxy ciphertext.

### 3.9 Multi-region

| Plane | Mode |
|-------|------|
| Metadata log | Home cell per `library_id` (single writer) |
| Blob store | Regional; place near user; async geo-replicate for DR |
| Devices | Pull from nearest edge; writes forward to home cell |
| Push notifications | Coalesced “library dirty” wakes |

---

## 4. Architecture Diagram

```text
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│   iPhone     │   │     Mac      │   │    iPad      │
│ PhotoDB+ML   │   │ PhotoDB      │   │ PhotoDB      │
│ Encrypt/SE   │   │ Encrypt      │   │ Encrypt      │
│ SyncAgent    │   │ SyncAgent    │   │ SyncAgent    │
│ UploadSched  │   │ UploadSched  │   │ UploadSched  │
└──────┬───────┘   └──────┬───────┘   └──────┬───────┘
       │                  │                  │
       │   TLS + device auth + sync envelopes (ciphertext)
       ▼                  ▼                  ▼
              ┌─────────────────────────┐
              │   Edge / API Gateway    │
              └───────────┬─────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────────┐
│ Sync Log    │   │ Upload       │   │ Push Coalescer  │
│ (home cell) │   │ Session Svc  │   │ (library dirty) │
│ server_seq  │   └──────┬───────┘   └─────────────────┘
└──────┬──────┘          │
       │                 ▼
       │         ┌──────────────┐
       │         │ Chunk/Blob   │─────────► Object Store (ciphertext)
       │         │ Assembler    │           multi-AZ + geo DR
       │         └──────────────┘
       ▼
┌─────────────┐
│ Index /     │  (opaque ids, sizes, seq—not plaintext pixels)
│ Quota /     │
│ Tombstones  │
└─────────────┘
```

**On-device path (capture):**

```text
Camera → Local Asset Store → Encrypt(chunks) → Upload Queue
                ↓
         PhotoDB index + thumb
                ↓
         Mutation: ASSET_ADD (encrypted envelope) → SyncAgent
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Durability of uploads

```text
1. Local durable write (SQLite/Core Data + file) BEFORE ACK to Camera UI
2. Encrypt + checksum per chunk (e.g. 1–4 MB)
3. UploadSession: session_id, asset_id, part_etags[]
4. Complete: server verifies part set + Merkle/checksum → commit blob_ref
5. Only then: mutation ASSET_ADD becomes globally visible
6. Devices may see "uploading" state via local flags
```

**Invariant:** Cloud durability ACK precedes local eviction of last original copy.

#### 5.1.2 Sync log & exactly-once apply

- Server assigns `server_seq` per library.
- Clients ACK cursor.
- Mutations idempotent by `mutation_id` (UUID from device).
- Replay safe: apply is upsert by `mutation_id`.

#### 5.1.3 Failure modes

| Failure | Mitigation |
|---------|------------|
| Device lost mid-upload | Resume session; or restart parts |
| Home cell outage | Local capture continues; sync queues; sticky region failover with epoch fence |
| Split-brain dual writers | Single-writer home cell; epoch |
| Bitrot in object store | Checksums + scrubber; client verifies on download |
| Push loss | Periodic pull reconcile |

#### 5.1.4 Delete & purge

```text
soft_delete → tombstone(seq) → hide on devices
after R days AND all durable refs unused → crypto-erase keys + delete parts
Recently Deleted restore = inverse mutation if within window
```

### 5.2 Scalability

#### 5.2.1 Sharding

```text
library_id → home_cell (consistent hash / directory)
mutation log partitioned by library_id
blob keys: /libs/{library_id}/assets/{asset_id}/{rendition}/{part}
```

Hot libraries (influencers / Shared) → dedicated shards.

#### 5.2.2 Cursor & compaction

```text
Retain detailed log for L days / M mutations
Compact: snapshot library index ciphertext → new baseline
Clients lagging → snapshot + catch-up
```

#### 5.2.3 Bandwidth shaping

- Thumb-first restore pipelines.
- Parallel part downloads capped per device.
- CDN for popular encrypted derivatives (still ciphertext; URL auth).

#### 5.2.4 Progressive scale map

| Scale | Change |
|-------|--------|
| 1× | Monolithic sync + object store; per-library log |
| 10× | Cell directory; upload session service; push coalescing |
| 100× | Regional blobs; compaction fleet; derivative client-upload norms |
| 1000× | Hierarchical cursors; cold tier; strict client radio budgets |

### 5.3 Maintainability & product evolution

- Version mutation schema (`op_type`, `schema_v`).
- Feature flags per account for Shared Library.
- Migration: adding edit recipe fields is additive; old clients ignore unknown.
- Observability without breaking privacy: metrics on sizes, latency, error codes—not on pixel content or captions.

### 5.4 Conflict deep dive (examples)

**Album membership:**

```text
Device A offline: add asset X to Album Q
Device B offline: remove X from Q (was present)
On merge: add-wins OR-set → X present; if product wants remove-wins, document—Apple-like often add-wins with user visibility
```

**Caption LWW:**

```text
A: "Beach" @ lamport 5
B: "Ocean" @ lamport 6 → Ocean wins
Equal lamport → tie-break device_id
```

**Edit recipes:** treat as LWW document or append-only recipe chain with explicit “revert”.

### 5.5 Battery-conscious behavior

| Lever | Mechanism |
|-------|-----------|
| Coalesce | Batch mutations; min interval between sync wakes |
| Defer | Large originals wait for Wi‑Fi+charging unless user opens |
| Adaptive parallelism | 1 stream on cellular; N on Wi‑Fi power |
| Budget | OS background budget integration (BGTaskScheduler-like) |
| Avoid wakeups | Prefer push-coalesced dirty bits over polling |

### 5.6 Security checklist

- TLS 1.3; pin where appropriate.
- Device attestation for key unwrap.
- Per-chunk AEAD (AES-GCM); AAD includes `library_id, asset_id, part_no`.
- Server authorization: bearer of device session can only touch own library.
- Rate-limit download to mitigate account takeover bulk exfil (still encrypted—but user’s keys on device).

### 5.7 Search & Memories (privacy fork)

| Mode | Behavior |
|------|----------|
| ADP on | Embeddings & faces on-device; sync encrypted indices if needed |
| Standard | May allow server-assisted features—disclose to interviewer |

**Interview win:** Offer both modes; don’t claim server Magic while ADP E2E holds.

---

## 6. Wrap-Up

### 6.1 What we designed

A local-first, privacy-preserving Photo Library: devices capture and encrypt, server orders an encrypted mutation log and stores opaque blobs, Optimize Storage evicts only after durable ACK, conflicts follow explicit LWW/OR-set rules, and uploads respect battery/network.

### 6.2 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| E2E vs server AI | E2E under ADP | Apple privacy bar |
| CRDT vs op-log | Op-log + selective CRDT sets | Ship complexity |
| Eager full-res sync | Optimize Storage | Disk + bandwidth |
| Strong sync freshness | Eventual + push | Battery |

### 6.3 MVP → scale path

MVP: single-region log + object store + client encrypt + basic LWW.  
10–100×: cells, sessions, coalesced push, compaction.  
1000×: regional blobs, cold tier, hierarchical cursors.

### 6.4 Risks

- Chatty sync regressions (battery).
- Evict-before-ACK bugs (data loss).
- Vague conflict UX (user trust).
- Claiming server Memories under ADP (inconsistency).

---

## 7. Deeper / Related Interview Questions

### 7.1 Privacy & crypto

**Q: Does the server generate thumbnails?**  
A: Under ADP, no plaintext. Client uploads encrypted thumbs/proxies, or features degrade.

**Q: How do new devices get keys?**  
A: LMK wrapped to device identity via Keychain sync / secure enrollment; server stores wraps only.

**Q: Can support decrypt a user’s photos?**  
A: Not under ADP. Escrow/recovery flows are a separate product decision with explicit UX.

### 7.2 Sync semantics

**Q: Is sync strongly consistent?**  
A: No—per-library single-writer log gives a total order of **committed** mutations; devices are eventually consistent with causal offline ops.

**Q: How do you prevent lost favorites?**  
A: Idempotent mutations + cursor ACK; LWW is explicit, not silent drop of blobs.

**Q: Offline for a month—what happens?**  
A: Large catch-up; may snapshot; upload backlog prioritized; conflict policy applies.

### 7.3 Storage & Optimize

**Q: When can we delete the local original?**  
A: Only after cloud durable commit of ciphertext + checksum verify policy.

**Q: User opens an old burst of 500 RAW files?**  
A: Queue fetches; show progressive; cap concurrent; don’t freeze UI.

### 7.4 Battery & networking

**Q: Why not sync every mutation immediately?**  
A: Radio spinup energy dominates; coalesce.

**Q: Cellular upload of 4K video?**  
A: Default defer; user setting override; clear metering UX.

### 7.5 Conflicts

**Q: Two edits different fields?**  
A: Field-level LWW or structured merge on recipe JSON paths.

**Q: Delete vs edit?**  
A: Tombstone causal check; Recently Deleted safety net.

### 7.6 Scale

**Q: 245 PB/day ingest?**  
A: Regional admission, many cells, not a single cluster; lifecycle to cold storage.

**Q: Hot Shared Album?**  
A: Dedicated shard; fan-out via per-subscriber cursors; careful rekey.

### 7.7 Derivatives & video

**Q: Scrubbing timeline for 4K60?**  
A: Client-generated proxy rendition ciphertext; seek indexes alongside.

**Q: Live Photo?**  
A: Paired still + video motion as asset bundle with atomic commit.

### 7.8 Abuse & quota

**Q: Stolen account bulk download?**  
A: Step-up auth; rate limits; device lists; remote wipe keys.

**Q: Quota exceeded mid-library?**  
A: Pause ASSET_ADD commit; keep local; notify.

### 7.9 Comparison

**Q: vs generic S3 + DB file sync?**  
A: Photo-specific recipes, Optimize Storage, battery scheduler, ADP key hierarchy, album semantics.

**Q: vs Google Photos?**  
A: Interview: stress on-device ML + E2E option as differentiators without disparaging.

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| Server plaintext thumbs + “E2E” | Contradicts ADP |
| Evict local before ACK | Data loss |
| Full resync every launch | Battery + network death |
| Global wall-clock LWW only | Clock skew; use lamport/server_seq |
| 200M×3MB=600PB/day | **600 TB/day** |

### 7.11 Reliability drills

1. Kill app at 60% upload → resume parts.  
2. Eviction race → never drop last copy pre-ACK.  
3. Dual device album edits offline → OR-set outcome.  
4. Home cell failover → epoch fence; no dual log heads.  
5. Corrupt part → checksum fail; re-get.

### 7.12 API sketch questions

**Q: Pull API?**  
A: `GET /libraries/{id}/mutations?after_seq=S&limit=N` → encrypted envelopes + `server_seq`.

**Q: Upload API?**  
A: `POST /upload_sessions` → put parts → `complete` → returns `blob_ref`.

### 7.13 Shared Library teaser

**Q: How would Shared Library differ?**  
A: Multi-writer with careful OT/CRDT or per-participant logs + merge; share key; ACL; rekey on leave—explicitly harder; defer details unless asked.

### 7.14 Observability without spying

**Q: What metrics are OK?**  
A: Upload success rate, part retries, cursor lag, battery energy samples, error codes—not captions, GPS plaintext, faces.

### 7.15 Web access

**Q: iCloud.com photos under ADP?**  
A: Limited unless keys in browser; often “use device” guidance—product honesty.

---

## 8. Appendices

### 8.1 Schema sketches

```text
-- device local
assets(asset_id, content_hash, local_path, cloud_blob_ref NULL,
       favorited, deleted_at, recipe_json, updated_lamport, ...)
albums(album_id, title, ...)
album_members(album_id, asset_id, added_lamport, removed_lamport NULL)
mutations_outbox(mutation_id, envelope_ciphertext, created_at)
cursors(library_id, last_applied_seq)

-- server
libraries(library_id, home_cell, quota_bytes, adp_enabled)
mutation_log(library_id, server_seq, mutation_id, envelope_ciphertext, device_id, ts)
blobs(blob_ref, library_id, size, checksum, storage_class, create_ts)
upload_sessions(session_id, library_id, asset_id, state, parts_json)
tombstones(library_id, asset_id, seq, purge_after)
```

### 8.2 Mutation types

```text
ASSET_ADD { asset_id, blob_ref, thumb_ref, meta_enc }
ASSET_DELETE { asset_id }
ASSET_UNDELETE { asset_id }
META_SET { asset_id, fields_enc, lamport }
RECIPE_SET { asset_id, recipe_enc, lamport }
ALBUM_CREATE / ALBUM_RENAME / ALBUM_DELETE
ALBUM_ADD_ASSET / ALBUM_REMOVE_ASSET
```

### 8.3 API checklist

- [ ] Create upload session / put part / complete  
- [ ] Push mutations (batch)  
- [ ] Pull mutations since cursor  
- [ ] Fetch blob part (authz)  
- [ ] Quota / storage class  
- [ ] Device list / revoke  
- [ ] Compact snapshot fetch  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| ADP | Advanced Data Protection — E2E for iCloud category |
| LMK | Library Master Key |
| Rendition | Derived representation (thumb/proxy/full) |
| Optimize Storage | Local eviction with cloud originals |
| server_seq | Home-cell total order for committed mutations |
| Tombstone | Soft-delete marker pending purge |
| UploadSession | Resumable chunked ciphertext put |

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Local-first, encrypt, op-log, resumable upload, basic LWW |
| 10× | Cells, push coalesce, upload sessions, eviction ACK invariant |
| 100× | Regional blobs, compaction, proxy renditions |
| 1000× | Cold tier, hierarchical cursors, strict radio budgets |

### 8.6 Priority scoring (scheduler)

```text
score = w1*user_visible + w2*is_thumb + w3*age_hours
        - w4*cellular_cost - w5*battery_penalty - w6*thermal_penalty
```

### 8.7 Checksum & AEAD binding

```text
AEAD_Encrypt(key=asset_key,
  plaintext=part_bytes,
  aad=library_id|asset_id|rendition|part_no|content_version)
Store: ciphertext + tag + part_checksum
```

### 8.8 Restore-new-device sketch

```text
1. Enroll device → unwrap LMK
2. Fetch snapshot + mutation catch-up
3. Download T0 thumbs in priority order (recency)
4. Background hydrate favorites / last 30 days optimized
5. Originals on demand
```

### 8.9 Interview “say this” summary (60 seconds)

> Local-first photo capture with Secure Enclave–backed keys; server stores ciphertext blobs and a per-library encrypted mutation log with single-writer `server_seq`. Optimize Storage never evicts before durable ACK. Metadata conflicts use LWW and set semantics; uploads are chunked and battery/Wi‑Fi aware. Under ADP the server cannot generate plaintext AI; Memories stay on-device. Scale via library cells, regional object stores, and log compaction.

### 8.10 Extra traps

| Trap | Pushback |
|------|----------|
| Plaintext server thumbs + ADP | No |
| Poll every 5s | Battery |
| Mutable in-place originals | Breaks addressing & sync |
| Unlimited cellular default | Bill shock + battery |
| One global Postgres log | Won’t reach 100× |

### 8.11 Reliability test plan

1. Upload resume after reboot.  
2. Eviction denied until ACK.  
3. Offline dual edits → deterministic merge.  
4. Cursor rewind replay idempotent.  
5. Purge only after retention.  
6. Key unwrap on new device; old device revoke.

### 8.12 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Local capture durable | p99 < 100ms |
| Wi‑Fi upload durable (median asset) | p50 < 60s |
| On-demand optimized fetch Wi‑Fi | p50 < 2s |
| Cursor lag (active device) | p99 < 60s |
| Upload abort rate | < 1% sessions |
| Unexpected local original loss | **0** |

### 8.13 Related systems map

```text
Camera → PhotoDB → Encrypt → UploadScheduler → UploadSession → ObjectStore
             ↓
         SyncAgent ←→ Mutation Log (home cell) ←→ other Devices
             ↓
         Push Coalescer
On-device ML ← local embeddings (ADP)
```

### 8.14 Decision log (interview)

| Decision | Choice |
|----------|--------|
| Sync transport | Encrypted op-log + cursors |
| Bytes | Content-addressed ciphertext parts |
| Conflicts | LWW attrs + OR-set membership |
| Privacy default | ADP-capable E2E |
| Eviction | ACK-gated |
| AI | On-device when E2E |

### 8.15 Cellular policy matrix

| Condition | Thumbs | Optimized | Original/Video |
|-----------|--------|-----------|----------------|
| Wi‑Fi | Yes | Yes | Yes |
| Cellular, default | Yes | Small/recent | No (defer) |
| Cellular + user allow | Yes | Yes | Budget-capped |
| Low Power | Coalesce | Defer large | Defer |
| Charging + Wi‑Fi | Max parallelism | Max | Max |

### 8.16 Compaction algorithm

```text
periodically:
  snapshot = fold(mutations[1..S]) into encrypted library index blob
  publish snapshot@S
  retain mutations (S-W, ∞] for lagging clients
  GC older mutations when all device cursors > S-W or grace expired
```

### 8.17 Dedup notes

```text
file_hash = SHA256(original_bytes)  # pre-encrypt identity on device
if library has asset with same file_hash → reuse asset_id; don't double bill quota
perceptual hash → suggest duplicates UI; don't auto-delete
```

### 8.18 Shared Album footnote

Separate `share_id` with `ShareKey`; mutations in share log; members’ devices unwrap ShareKey; leaving member → rotate ShareKey and re-encrypt titles (forward secrecy lite) in later phase.

### 8.19 Threat model (short)

| Threat | Control |
|--------|---------|
| Curious server admin | E2E ciphertext + ADP |
| Stolen device | Secure Enclave; passcode; remote revoke |
| MITM | TLS + cert pinning |
| Malicious client on account | Authz + rate limits + device list |
| Integrity tampering | AEAD tags + server authz on blob refs |

### 8.20 Open questions to ask interviewer

1. ADP required or optional mode?  
2. Shared Library in scope?  
3. Web feature parity?  
4. RAW / ProRes as first-class?  
5. Exact conflict UX for captions?

---

*End of iCloud Photo Library synchronization system design.*
