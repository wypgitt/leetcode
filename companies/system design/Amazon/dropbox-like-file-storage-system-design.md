# System Design: Dropbox-like File Storage (Sync)

> **Focus areas:** Chunked upload · Content-addressed blocks · Metadata namespace · Client sync protocol · Dedup · Sharing ACLs · Conflict resolution · Change notifications · Quotas  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split metadata/block/notification planes, explicit sync cursors & conflicts, deal-breakers for “POSIX locking over WAN” or “one QPS number for everything”  
> **Interview theme:** Amazon SDE III / L6 — design a **Dropbox-like** cloud file system: sync correctness, ownership of durability/cost, and operational isolation of hot shared folders—not a raw S3 clone

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

Goal: **bound the product**—a personal/team cloud drive: upload/download files, sync folders across devices, share with users/links, detect remote changes, resolve conflicts, and notify clients—**not** a collaborative Docs CRDT editor and **not** a bare object store API alone.

### 1.0 What this is / is not

| Dimension | **Dropbox-like sync (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Sync files/folders across devices + cloud | News Feed / chat / Docs OT |
| Success | Correct eventual sync, few conflicts, fast delta | Perfect WAN POSIX |
| Metadata | Hierarchical namespace, versions, permissions | Only object key/value |
| Data plane | Chunked/block content-addressed store | Whole-file only reupload |
| Hard problem | Sync protocol + conflicts + notify + dedupe safety | Training ML models |
| Collab editing | File replace / versioning MVP | Real-time OT/CRDT docs |
| Amazon lens | Ownership of durability/cost; blast-radius isolation | “Just put files in S3” |

**Scope statement:** Design Dropbox-like file storage: chunked upload, metadata namespace, multi-device sync, conflict handling, sharing, dedupe, and change notifications—at SDE III depth with progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Objects? | Files + folders; hierarchical paths | Namespace metadata tree |
| F2 | Upload? | Large files; resume; chunked | Chunk/block API + commit |
| F3 | Sync? | Desktop/mobile clients keep folder synced | Cursor/changelog protocol |
| F4 | Conflicts? | Concurrent edits → conflict copy / version | Explicit conflict policy |
| F5 | Sharing? | Link share + user ACLs on folders/files | AuthZ on metadata |
| F6 | Versions? | Keep history / restore | Immutable blocks + meta versions |
| F7 | Dedup? | Same content not stored twice (optional) | Content-addressed chunks |
| F8 | Notifications? | Clients learn remote changes quickly | Long poll / push / websocket |
| F9 | Search? | Filename search MVP; content search Phase 2 | Meta index; separate content indexer |
| F10 | Quotas? | Per-user / team storage caps | Usage accounting |
| F11 | Offline? | Local edits while offline; sync later | Client journal + conflict |
| F12 | Preview? | Thumbnails / docs preview Phase 1.5 | Async processors |
| F13 | Virus scan? | Async scan before share / optional gate | Pipeline hook |
| F14 | Selective sync? | Choose folders to hydrate | Client policy + meta |
| F15 | Team / org? | Shared team spaces | Namespace types + IAM |

**MVP functional scope:**

1. **Namespace:** create/rename/move/delete files and folders under a user’s root (and shared folders).  
2. **Chunked upload:** split file → upload blocks → commit revision with block list.  
3. **Download / hydrate:** fetch blocks by hash; reconstruct file.  
4. **Sync protocol:** clients maintain cursor; pull changelog of metadata mutations.  
5. **Conflict policy:** if two devices commit diverging revisions from same parent → **conflict copy** (Dropbox-style); preserve both.  
6. **Sharing:** grant user/view/edit on subtree; link tokens.  
7. **Notifications:** wake clients when namespace changes in watched roots.  
8. **Quotas & auth**; basic version history restore.  
9. **Idempotent commits** via client keys.  
10. **Dedupe** at chunk level within policy (cross-user careful).

**Out of MVP:**

- Google Docs real-time collaborative editing (OT/CRDT)  
- Full-text content search across all files (hooks only)  
- Arbitrary POSIX flock over network  
- Cross-region strongly consistent dual-active metadata writers  
- End-to-end encrypted vault deep dive (mention tradeoffs)  
- Bit-perfect continuous filesystem mirror with kernel VFS semantics

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Metadata op latency | Snappy UX | p99 < 100–200ms in-region |
| N2 | Upload throughput | Saturate user bandwidth | Chunk parallel; resume |
| N3 | Durability | No silent loss after commit ACK | Multi-AZ blocks + meta; ACK only after durable |
| N4 | Sync freshness | Remote edits appear soon | Notify < few seconds typical |
| N5 | Consistency | Per-file linear revisions; namespace atomic ops | CAS on revision parent |
| N6 | Availability | High | 99.9%+; degrade previews first |
| N7 | Dedup safety | No cross-tenant leak via hash | AuthZ always on meta; careful hash APIs |
| N8 | Scale | Billions of files | Metadata sharded; blocks object store |
| N9 | Cost | Dominated by bytes + notify | Dedup, EC, cold tier, coalesce notify |
| N10 | Operability | Clear ownership | Runbooks for GC, conflict storms, hot shares |
| N11 | Multi-region | Global users | Home-region metadata; edge upload optional |
| N12 | Abuse | Ransomware / spam upload | Rate limits, quota, malware hooks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Alice uploads `video.mp4` from desktop → chunks upload → commit rev1 → phone notified → downloads deltas.  
2. Alice renames folder → metadata mutation → other devices apply rename without re-downloading blocks.  
3. Bob edits shared doc offline → Alice also edits → sync → **conflict copy** created; both versions preserved.  
4. Alice shares folder with Carol → Carol sees subtree; ACL checked on list/download.  
5. Alice restores prior version → new revision pointing at old block list.  
6. Identical file uploaded by two users → blocks deduped; separate metadata inodes.  
7. Partial upload dies → client resumes missing chunks; commit only when complete.  
8. Link share view-only → no editor sync watcher storm.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Commit with unknown/stale parent rev | 409 conflict → client rebase or conflict copy |
| Chunk upload fails mid-way | Resume missing chunks; no commit until complete |
| Orphan chunks | GC after TTL if unreferenced |
| Move folder cycles | Reject cycles; transactional move |
| Permission revoked mid-download | AuthZ fail subsequent blocks |
| Hash collision fantasy | Use SHA-256; ignore birthday fear in interview |
| Notify storm (huge folder) | Compact changelog; coalesce events |
| Clock skew | Server timestamp + logical rev ids |
| Partial local apply | Client journal; idempotent apply by mutation id |
| Dedup confirmation attack | Don’t expose “hash exists” across tenants without ownership |
| Quota exceeded mid-upload | Reject commit; allow orphan GC |
| Ransomware mass rewrite | Version history + rate anomaly alarms |
| Shared folder with 100K members | Cap sync watchers; pull-by-cursor; isolate shard |
| Cursor compacted past | Snapshot hydrate / reset flag |
| Block store slow | Commit waits for durability; client retries chunks |
| Metadata partition outage | That namespace unavailable; others OK (cells) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 10M | 100M | 1B | multi-B |
| Files (namespace entries) | 10B | 100B | 1T | multi-T |
| Avg file size | 1 MB | 1 MB | 1–2 MB | mixed |
| Chunk size | 4 MB | 4 MB | 1–4 MB | adaptive / CDC |
| Peak metadata QPS | 50K | 500K | 5M | 50M |
| Peak chunk put QPS | 20K | 200K | 2M | 20M |
| Peak ingress GB/s | 10 | 100 | 1K | 10K |
| Sync notify watchers | 5M | 50M | 500M | huge |
| Shared folder members avg | small | skewed | celebrity folders | caps / fan-out |
| Versions retained | 100 / 30d | policy | tiered | cold |
| Distinct blocks (after dedup) | ~0.7× logical | similar | careful global dedup | EC + tiers |

**What each jump forces:**

- **10×:** Split metadata DB vs block store; chunked upload; changelog cursors; basic GC.  
- **100×:** Metadata cells by namespace; notify fan-out service; block EC/cold tier; GC fleets; hot-share isolation.  
- **1,000×:** Hierarchical notify; bloom/watch compaction; edge upload; strict isolation of celebrity shared folders; regional write homes.

### 1.5 Etc. (Constraints & Assumptions)

- Clients are **smart** (desktop agent / mobile app) with local DB — sync protocol is first-class.  
- **Blocks are immutable**; updates create new revisions.  
- Strong consistency **per namespace partition**; global linearizability across all users unnecessary.  
- Previews/virus scan = async pipeline hooks.  
- Amazon bar: name owners for meta, blocks, sync, GC, abuse; cost per GB and per notify.

**Scope statement:**

> Design a Dropbox-like system: chunked content-addressed storage, hierarchical metadata with revision CAS, multi-device sync via changelogs and notifications, explicit conflict copies, sharing ACLs, safe dedupe, and progressive scale—separating metadata QPS from block bandwidth, without pretending we offer WAN POSIX locks.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Metadata ops** | mkdir/rename/commit/list | ~50K/s | ~500K/s | Metadata DB |
| **Chunk uploads** | Block puts | ~20K/s | ~200K/s | Block/object store |
| **Chunk downloads** | Block gets | higher than puts | ×10 | Block + CDN/cache |
| **Changelog reads** | Sync pull | reconnects + deltas | ×10 | Changelog / meta |
| **Notifications** | Watch wakeups | spiky | ×10 | Pubsub / push |
| **GC / compaction** | Orphan blocks | background | ×10 | Workers |
| **Preview/index** | Async | fraction | ×10 | Pipelines |

**Anti-pattern:** one “storage QPS” mixing 200-byte renames with 4 MB chunk puts.

### 2.2 Namespace vs bytes

```text
10M users × 1000 files = 10B files (baseline order)
Metadata ~500 B / entry → 10B × 500 B = 5 TB raw meta (before indexes/replication)
Real with indexes/versions: tens of TB — still << block data

Blocks:
  Assume avg file 1 MB
  10B × 1 MB = 10 PB logical
  With replication×3 → ~30 PB; with EC + dedup lower
  Interview: keep orders straight — **PB-scale data**, **TB-scale metadata**
```

### 2.3 Upload math

```text
Peak ingress 10 GB/s
Chunk 4 MB → chunk puts/s = 10e9 / 4e6 ≈ 2,500/s average of that peak bandwidth
Design for burst: ~20K chunk puts/s baseline peak

Parallelism: client uploads N chunks concurrent (e.g. 4–8)
Commit is 1 metadata txn after all chunks durable
```

### 2.4 Sync / notify math

```text
5M active watchers
If every watcher polls every 30s: 5M/30 ≈ 167K poll/s — heavy
Prefer: long-poll / push; poll only as fallback
Changelog: per-namespace append-only mutations; client cursor
Compact: coalesced path updates (rename storms)
```

### 2.5 Sharing fan-out

```text
Hot shared folder with 100K members — one rename notify:
  naive 100K push → storm
Mitigation: sharded notify topics; clients pull by cursor; membership caps for sync folders;
  “view-only link” doesn’t register 100K watchers the same way
```

### 2.6 Dedup savings (order)

```text
If 20% bytes are duplicates across users (OS images, packages):
  store once → significant $ savings
Risk: timing attacks on hash existence — authorize carefully
Cross-user dedup is a product/security decision, not free lunch
```

### 2.7 Bandwidth & cost sketch

```text
Cost ≈ stored_bytes × (replication/EC) + egress + metadata RUs + notify fanout
Optimize: dedup, EC (e.g. 6+3), cold tier for old versions, coalesce notify, selective sync
Never optimize durability below “ACK ⇒ recoverable”
```

### 2.8 Progressive BOTE summary

| Scale | Files | Meta QPS | Ingress | Notify model |
|-------|-------|----------|---------|--------------|
| Baseline | 10B | 50K | 10 GB/s | Long-poll + push |
| 10× | 100B | 500K | 100 GB/s | Sharded changelog |
| 100× | 1T | 5M | 1 TB/s | Cells + edge upload |
| 1,000× | multi-T | 50M | extreme | Hierarchical watch |

### 2.9 Latency budgets

| Path | Budget |
|------|--------|
| Metadata mutate (rename/commit) | p99 < 100–200ms |
| Chunk PUT (network dominated) | throughput-bound |
| Sync pull delta | p99 < 200–500ms for small delta |
| Notify wake | typically < 1–5s |
| Full hydrate large file | user bandwidth |

### 2.10 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | Whole-file uploads; meta+blocks coupled | Chunk + split planes |
| 100× | Hot shared folders; GC lag; notify storms | Cells; isolate; coalesce |
| 1,000× | Global write + celebrity namespaces | Home regions; hierarchical watch; EC |

### 2.11 Critical bottlenecks

1. Metadata write throughput on hot namespaces.  
2. Notify fan-out for popular shared folders.  
3. Orphan GC keeping up with abandoned uploads.  
4. Block durability ACK latency vs user upload UX.  
5. Cross-user dedup authz / side channels.

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Commit ACK means durable** — blocks + metadata recoverable.  
2. **Planes stay separate** — metadata QPS ≠ block bandwidth.  
3. **Sync is a product** — cursor/changelog, not “list S3 forever”.  
4. **Conflicts are explicit** — never silent data loss.  
5. **Cost is owned** — dedup/EC/cold tier with measurable savings.  
6. **Blast radius** — hot shared folder can’t melt the fleet.  
7. **Progressive scale** — cells when namespaces demand it.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Client Sync Agent | Local journal, chunker, cursor, conflict UI |
| API Gateway | AuthN/Z, rate limits, routing |
| Metadata Service | Namespace tree, revisions, ACL, CAS commits |
| Block / Chunk Service | Content-addressed put/get; existence checks |
| Object / Block Store | Durable blob storage (S3-like / custom) |
| Changelog Service | Per-namespace ordered mutations + cursors |
| Notify Service | Long-poll / push wakeups |
| Share / ACL Service | Principals, roles, link tokens |
| Quota Service | Usage accounting; enforce on commit |
| GC Workers | Orphan chunks; old versions; tombstones |
| Preview / AV Pipeline | Async thumbnails, virus scan |
| Admin / Support | Legal hold, takedown, restore |

### 3.3 Chunking & content addressing

| Approach | How | Pros | Cons |
|----------|-----|------|------|
| Fixed-size chunks (e.g. 4MB) | Split by offset | Simple; good parallelism | Small edit may rewrite many chunks |
| Content-defined chunking (CDC) | Rabin-like boundaries | Better delta for inserts | CPU; tiny chunk explosion risk |
| Whole-file hash only | One blob per file | Trivial | Terrible sync/delta |

**Recommendation (MVP):** fixed 4MB chunks + SHA-256 content hash; CDC as Phase 1.5 for large mutable files. Manifest = ordered list of chunk hashes + size + file hash.

### 3.4 API sketch

```text
# Blocks
PUT    /v1/blocks/{sha256}          # upload chunk (authz session)
HEAD   /v1/blocks/{sha256}          # exists? (careful cross-tenant)
GET    /v1/blocks/{sha256}          # download (authz via capability)

# Namespace / revisions
POST   /v1/namespaces/{ns}/entries  # mkdir / create file stub
POST   /v1/files/{file_id}/revisions
       body: { parent_rev, blocks[], size, client_mtime, idempotency_key }
POST   /v1/entries/move
DELETE /v1/entries

# Sync
GET    /v1/sync?namespace_id=&cursor=&limit=
LONGPOLL /v1/notify?cursor=...

# Sharing
POST   /v1/shares
POST   /v1/links
GET    /v1/quota
```

### 3.5 Data model

**namespaces**

| Field | Notes |
|-------|-------|
| namespace_id | PK; user root or shared folder |
| owner_id | Team/user |
| type | PERSONAL / SHARED / TEAM |
| root_rev / cursor_high | For sync |
| region_home | Write home |

**entries (inode-like)**

| Field | Notes |
|-------|-------|
| entry_id | PK |
| namespace_id | Shard key |
| parent_id | Folder |
| name | Unique among siblings |
| type | FILE / FOLDER |
| file_id | If file |
| deleted | Tombstone |

**file_revisions**

| Field | Notes |
|-------|-------|
| file_id | |
| rev | Monotonic / ULID |
| parent_rev | CAS |
| blocks[] | Ordered hashes |
| size | |
| status | ACTIVE / CONFLICT_COPY |
| created_by_device | |

**blocks**

| Field | Notes |
|-------|-------|
| content_hash | PK |
| size | |
| locator | Object store key |
| refcount / refs | GC |
| created_at | |

**acl / shares**

| Field | Notes |
|-------|-------|
| resource | ns or entry |
| principal | user/group/link |
| role | viewer/editor/owner |

**changelog**

| Field | Notes |
|-------|-------|
| namespace_id | Partition key |
| mut_id / cursor | Ordered |
| op | upsert/delete/move/acl |
| payload | Compact path + rev |

### 3.6 Upload + commit flow

```text
1. Client detects local change; journals intent
2. Chunk file → compute SHA-256 per chunk
3. For each missing chunk (authorized existence check): PUT block
4. Wait for all chunks durable (service ACKs)
5. POST revision with parent_rev + block list + idempotency_key
6. Metadata service:
     - AuthZ + quota check
     - CAS: parent_rev must match current head (or conflict path)
     - Write revision + update entry + append changelog
     - Bump notify cursor
7. ACK client with new rev
8. Async: AV scan, preview, usage rollup
```

**Invariant:** Never ACK commit until referenced blocks are durable and metadata txn committed.

### 3.7 Sync protocol

```text
Client stores (namespace_id → cursor)
Loop:
  LONGPOLL notify OR timer
  GET /sync?cursor=C
  if reset: hydrate from snapshot / full listing
  else: apply mutations in order (idempotent by mut_id)
  advance cursor
  fetch any needed blocks for selective sync policy
```

**Why changelog > tree walk:** O(delta) bandwidth; rename doesn’t re-download bytes.

### 3.8 Conflict resolution

| Policy | Behavior | When |
|--------|----------|------|
| **Conflict copy (recommended MVP)** | Loser (or both diverging) saved as `file (conflicted copy from DEVICE).ext` | Concurrent commits from same parent |
| Last-writer-wins + history | Head advances; loser only in version history | Lower UX friction; risk silent surprise |
| Manual merge | User picks | Binary files hard |
| CRDT/OT | Real-time docs | Out of MVP |

**Server role:** detect CAS failure (`parent_rev` stale) → return 409 with server head; client uploads conflict copy commit or rebases if mergeable (text optional).

**Never:** silently drop one side’s bytes after ACK’d local edit without preserving a recoverable version.

### 3.9 Dedup

```text
Content-addressed blocks: same hash → one stored object
refcount++ on commit reference; -- on unreference after version GC

Policies:
  A) Per-tenant dedup only — safest
  B) Global dedup — max savings; side-channel risk
  C) Opportunistic: allow HEAD only if caller already has capability / same org

Deal-breaker: public "does this hash exist?" oracle across tenants
```

### 3.10 Sharing & AuthZ

- ACL on namespace/subtree; inheritance with deny/break-glass rare.  
- Link tokens: capability URLs with role + expiry + password optional.  
- Every block GET authorized via **file capability** derived from entry ACL—not “know hash ⇒ read”.  
- Revocation: bump auth generation; short-lived block credentials (signed URLs).

### 3.11 Tradeoffs table

| Decision | Option A | Option B | Pick |
|----------|----------|----------|------|
| Chunking | Fixed 4MB | CDC | Fixed MVP; CDC later |
| Conflicts | Conflict copy | LWW | Conflict copy |
| Dedup | Per-tenant | Global | Per-tenant MVP; opt-in global carefully |
| Notify | Poll | Push/long-poll | Long-poll + push |
| Meta store | RDBMS | Dynamo/Spanner-like | Partitioned KV/SQL by ns |
| Multi-region | Active-active meta | Home region | Home region MVP |
| Blocks | Triple repl | EC | Repl hot; EC warm/cold |

### 3.12 Deal-breakers

1. Whole-file reupload as only sync mechanism at scale.  
2. Metadata in object store listings as sole namespace.  
3. Silent LWW without version history when users expect sync.  
4. Cross-tenant hash oracle for dedup.  
5. ACK commit before blocks durable.  
6. Global linearizability requirement across all namespaces.  
7. POSIX flock over WAN as MVP.  
8. One shared DB for all celebrity folders without isolation.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
┌──────────────┐   ┌──────────────┐
│ Desktop Agent│   │ Mobile Agent │
└──────┬───────┘   └──────┬───────┘
       │ chunk/sync/notify│
       ▼                  ▼
┌─────────────────────────────────────┐
│            API Gateway / Edge       │
└───────────────┬─────────────────────┘
                │
     ┌──────────┼──────────┬────────────┐
     ▼          ▼          ▼            ▼
┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│Metadata │ │ Block  │ │Changelog│ │  Notify  │
│Service  │ │Service │ │Service  │ │ Service  │
└────┬────┘ └───┬────┘ └────┬────┘ └────┬─────┘
     │          │           │           │
     ▼          ▼           ▼           ▼
┌─────────┐ ┌────────┐ ┌─────────┐ ┌──────────┐
│ Meta DB │ │ Object │ │ Log /   │ │ PubSub / │
│ (cells) │ │ Store  │ │Partitions│ │Connections│
└─────────┘ └────────┘ └─────────┘ └──────────┘
                │
                ▼
         ┌────────────┐
         │ GC / AV /  │
         │ Preview    │
         └────────────┘
```

### 4.2 Sequence: first upload

```text
Client                BlockSvc           MetaSvc            Changelog/Notify
  |                      |                  |                     |
  |-- PUT chunk1 ------->|                  |                     |
  |-- PUT chunk2 ------->|                  |                     |
  |<- durable ACK -------|                  |                     |
  |-- commit(parent, blocks) -------------->|                     |
  |                      |   verify blocks  |                     |
  |                      |   CAS + write ---->|-- append mut ------>|
  |<- {rev} --------------------------------|  bump cursor ------->|
  |                      |                  |                     |-- wake peers
```

### 4.3 Sequence: conflict

```text
Device A commit(parent=r1) -> success r2
Device B commit(parent=r1) -> 409 {head=r2}
Device B uploads blocks (if needed) -> commit conflict copy OR merge
  -> creates file (conflicted copy...).ext as r3' OR new entry
Both preserved; user resolves
```

### 4.4 Sequence: sync pull

```text
Client: GET /sync?cursor=100
Server: mutations 101..150, next_cursor=150
Client: apply; GET blocks for hydrated paths
Client: LONGPOLL until cursor>150
```

### 4.5 Cell architecture at 100×+

```text
Cell = { meta DB shard set, changelog partitions, notify slice }
Route by namespace_id → cell
Shared folder namespace lives in one cell (home)
Users may attach many namespaces across cells
Control plane: directory of namespace→cell
```

### 4.6 Hot shared folder path

```text
Celebrity ns:
  - Dedicated meta shard + changelog partitions
  - Notify: clients pull; no 1:N payload push of full mut
  - Rate limit mutations; coalesce rename storms
  - Membership: prefer link-view for huge audiences
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Commit durability:** ACK ⇒ blocks durable ∧ meta committed ∧ changelog append.  
2. **CAS lineage:** each file rev (except conflict copies) has single parent chain.  
3. **AuthZ on bytes:** hash ≠ capability.  
4. **Namespace atomicity:** move/rename all-or-nothing within partition.  
5. **Cursor monotonicity:** clients never apply mut out of order for a ns.  
6. **Quota non-negative** accounting eventually consistent but commit enforce strong enough to prevent unbounded theft.

#### 5.1.2 Failure modes

| Failure | Effect | Mitigation |
|---------|--------|------------|
| Client crash mid-upload | Orphan chunks | TTL GC |
| Meta commit fails after blocks | Orphans | GC; client retries commit idempotently |
| Changelog lose mut | Sync divergence | Dual-write in same txn / outbox |
| Notify down | Stale clients | Poll fallback; catch-up sync |
| Block store AZ loss | Durability risk | Multi-AZ / EC |
| Wrong conflict policy | User data “gone” | Conflict copies + versions |
| GC bug | Data loss | Refcount + grace + dark reads |

#### 5.1.3 Durability & backup

- Blocks: multi-AZ; optional cross-region async replica for DR.  
- Meta: quorum writes; PITR backups; legal hold flag skips GC.  
- Test restores quarterly (Amazon ownership bar).

#### 5.1.4 Consistency nuances

- Per-namespace strong ordering for changelog.  
- Cross-namespace: no global snapshot required.  
- Read-your-write on same device via client journal.  
- Cross-device: after notify + sync, see committed revs.

#### 5.1.5 Security

- Signed, short-lived block URLs.  
- Link share revocation.  
- AV on share / download gate optional.  
- Ransomware: version history immutable window.  
- Dedup side-channel controls.  
- E2E encryption vault: server can’t dedupe/preview—product tradeoff.

### 5.2 Scalability

#### 5.2.1 Metadata scaling

- Shard by `namespace_id`.  
- Avoid hotspot keys (root listing caches; paginate).  
- Secondary indexes (path) local to shard.  
- Cells at 100×+.

#### 5.2.2 Block plane scaling

- Object store horizontally scales.  
- Edge upload / regional buckets for locality.  
- Parallel chunk PUT.  
- CDN for popular public link downloads (authz cookies/signed).

#### 5.2.3 Notify scaling

- Connection fan-out service separate from meta.  
- Coalesce: wake with “cursor advanced” not full payload.  
- Shard connections by user_id / device_id.  
- Hierarchical watch for org trees at 1,000×.

#### 5.2.4 GC scaling

- Priority queues for orphan TTL.  
- Refcount batches; generation-based GC.  
- Throttle GC under user traffic (backpressure).  
- Verify with sampling dark reads before hard delete.

#### 5.2.5 Multi-region

| Model | Pros | Cons |
|-------|------|------|
| Home-region meta + global block fetch | Simpler consistency | Cross-region latency for travelers |
| Active-active meta | Low latency writes everywhere | Conflict hell; usually avoid |
| Pin shared ns to region | Predictable | Migration tooling needed |

**MVP:** home region per namespace; blocks may replicate; clients upload to nearest block gateway that replicates to home.

#### 5.2.6 Cost controls

- EC for cold versions.  
- Lifecycle: hot → warm → cold → expire per policy.  
- Dedup savings dashboards.  
- Cap version retention tiers.  
- Selective sync reduces egress.

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Metadata / CAS | Namespace team |
| Block store & dedup | Blob team |
| Sync protocol / client | Client + Sync API team |
| Notify | Realtime team |
| GC | Storage lifecycle team |
| Sharing / IAM | Identity & sharing |
| AV / Trust | Security |
| Quotas / billing | Monetization |

#### 5.3.2 Safe evolution

- Changelog schema versioned.  
- Client min-version gates.  
- Dual-publish mutation types during migrate.  
- Feature flags for CDC chunking rollout.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Commit success (non-conflict) | 99.9% |
| Commit p99 latency | < 200ms + upload time excluded |
| Sync freshness (notify→pull) | < 5s p50 |
| Durability | 11 nines aspirational / multi-AZ practical |
| GC lag (orphans) | < 24–72h |
| Conflict rate | Watch as product metric |

Alarms: commit error spikes, changelog lag, notify connection drops, orphan backlog, hot ns QPS, AV queue depth.

#### 5.3.4 Progressive scale checklist

**10×:** chunk upload; meta≠blocks; cursor sync; conflict copies; basic GC; quotas.  
**100×:** cells; notify service; EC/cold; hot-share isolation; AV pipeline.  
**1,000×:** hierarchical watch; edge upload; CDC; regional homes; automated cost policies.

### 5.4 Deep dive: revision CAS & idempotency

```text
commit(file, parent_rev, blocks, idem_key):
  if seen(idem_key): return prior result
  head = current_rev(file)
  if head != parent_rev:
     return 409 Conflict(head)
  assert all blocks durable & authorized
  new_rev = allocate()
  txn:
    write revision
    update entry head
    append changelog
    account quota
  store idem_key → new_rev
  return new_rev
```

### 5.5 Deep dive: move / rename

```text
Moves are metadata-only if within namespace:
  - Update parent_id + name
  - Single changelog op (or tombstone+create carefully)
  - Reject cycles (DFS/lock parent chain in shard)
Cross-namespace move = copy blocks refs + new entry + ACL rewrite (heavier)
```

### 5.6 Deep dive: dedup & GC

```text
On commit: for each hash, refcount++ / add reverse index file_rev→hash
On version expire: refcount-- ; if 0 → quarantine → delete after grace
Race: upload concurrent with GC → generation tokens or "pin until commit TTL"
```

### 5.7 Deep dive: client journal

```text
Local states: DIRTY → UPLOADING → COMMITTING → CLEAN
Offline edits stack; on reconnect replay
If 409: create conflict copy locally + upload
Idempotency keys survive process restart (persisted)
```

### 5.8 Deep dive: selective sync & placeholders

```text
Cloud entry exists; local placeholder with metadata only
On open: hydrate blocks
Saves disk & egress; changelog still applies meta ops
```

### 5.9 Testing & resilience

| Test | Purpose |
|------|---------|
| CAS conflict matrix | Concurrent commits |
| Crash mid-chunk | Resume |
| Chaos meta AZ | Failover |
| Notify partition | Poll catch-up |
| GC dark launch | No live data loss |
| Dedup side-channel | Timing/ACL tests |
| Hot share load | Isolation |
| Clock skew | Logical revs win |

### 5.10 Comparison: Drive vs S3 vs Docs

| | Dropbox-like | S3 | Google Docs |
|--|--------------|----|-------------|
| Namespace | Hierarchical sync | Flat keys | Doc model |
| Sync | Cursor changelog | None native | Real-time CRDT/OT |
| Conflicts | Conflict copies | Overwrite/version id | Merge |
| Dedup | Chunk CAS | Optional | N/A |
| Unit | File/folder | Object | Characters |

### 5.11 Amazon leadership connection (brief)

- **Ownership:** single-threaded owners for durability and sync correctness.  
- **Frugality:** dedup/EC/cold with measured ROI.  
- **Bias for action:** MVP conflict copies over perfect merge.  
- **Dive deep:** know why hash oracle is dangerous.  
- **Customer obsession:** never silently lose the user’s bytes.

---

## 6. Wrap-Up

### 6.1 30-second recap

> Split **metadata** (namespace, revs, ACL, CAS) from **content-addressed chunks**. Clients upload chunks, commit with parent revision, sync via **cursors/changelogs**, resolve races with **conflict copies**, share via ACL/link capabilities, notify with long-poll/push. Scale by sharding namespaces into cells; keep notify and GC as first-class owned systems. Progressive 10×/100×/1,000× forces isolation of hot shares and cost tiers—not a bigger single Postgres.

### 6.2 Key tradeoffs

1. Fixed chunks vs CDC.  
2. Conflict copy vs LWW.  
3. Per-tenant vs global dedup.  
4. Home-region vs active-active meta.  
5. Push notify vs pull-only.  
6. Triple replication vs erasure coding.

### 6.3 Risks & follow-ups

- GC correctness bugs (data loss class).  
- Celebrity shared folders.  
- Ransomware / mass overwrite.  
- E2E crypto vs server features.  
- Cross-region travelers latency.  
- Changelog compaction vs client reset storms.

### 6.4 What “good” looks like

- Clear plane separation in first 5 minutes.  
- Explicit conflict policy.  
- Dedup security discussed.  
- BOTE with separate meta vs bytes.  
- Ownership + SLOs + deal-breakers named.  
- Progressive scale narrative coherent.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. Sync vs backup-only product—what changes?  
2. Why not “files are S3 objects + CloudFront”?  
3. Online-only web vs smart clients.  
4. Team Drive vs personal.  
5. Must you support sparse files / symlinks?  
6. Max file size?  
7. Version retention policy who owns?  
8. Compliance (GDPR delete) vs version history.  
9. Preview generation SLAs.  
10. Mobile battery constraints on sync.  
11. LAN sync / relay peers?  
12. What is explicitly out of scope?

### 7.2 Chunking & dedup (Q13–Q28)

13. Why 4MB?  
14. CDC algorithm sketch.  
15. SHA-256 vs BLAKE3.  
16. Encryption at rest vs content hash.  
17. Client-side encryption impact on dedup.  
18. Cross-user dedup side channels.  
19. Block size vs small-file overhead.  
20. Compression before hash?  
21. Pack small files into packs?  
22. How do you prove dedup savings?  
23. Refcount vs mark-and-sweep.  
24. Quarantine period rationale.  
25. Dedup within org only.  
26. Chunk alignment vs media containers.  
27. Streaming upload before full hash known?  
28. Manifest signing?

### 7.3 Sync & conflicts (Q29–Q44)

29. Detail conflict copy naming.  
30. Can folders conflict?  
31. Delete vs update race.  
32. Move/delete races.  
33. Cursor reset protocol.  
34. Changelog compaction strategy.  
35. Ordering guarantees.  
36. Idempotent apply.  
37. Clock skew.  
38. Partial apply crash.  
39. Binary vs text merge.  
40. Offline for weeks.  
41. Selective sync races.  
42. Watch limit per device.  
43. Snapshot hydrate cost.  
44. Why not operational transform for all files?

### 7.4 Sharing & security (Q45–Q56)

45. ACL inheritance model.  
46. Link token design.  
47. Revocation latency.  
48. Signed URL TTL.  
49. Confused deputy via hash.  
50. AV false positive UX.  
51. Ransomware response.  
52. Legal hold.  
53. Admin impersonation audit.  
54. Public link scraping.  
55. E2E vault tradeoffs.  
56. Tenant isolation testing.

### 7.5 Scale & ops (Q57–Q72)

57. Namespace hotspot.  
58. Cell migration.  
59. Notify thundering herd.  
60. GC backlog playbook.  
61. Multi-region home change.  
62. Cost regression alarms.  
63. Cold tier restore latency.  
64. Metadata schema migration.  
65. Client protocol version skew.  
66. Chaos drill list.  
67. SLO burn alerts.  
68. Capacity planning inputs.  
69. Shared folder membership at 1M.  
70. Edge upload consistency.  
71. Dual-write changelog risks.  
72. When to build custom block store vs S3.

### 7.6 Behavioral / Amazon (Q73–Q80)

73. Tell a story owning a data-loss near miss.  
74. How you prioritize GC vs features.  
75. Frugality vs durability disagreement.  
76. Escalation when hot share melts meta.  
77. Cross-team API contract for blocks.  
78. Customer issue: “missing file” debugging path.  
79. Security review of dedup.  
80. 45-minute interview timebox plan.

---

## 8. Appendices

### Appendix A — Status cheat sheet

| State | Meaning |
|-------|---------|
| UPLOADING | Chunks in flight |
| COMMITTED | Head rev durable |
| CONFLICT_COPY | Preserved divergent edit |
| TOMBSTONED | Deleted; GC pending |
| QUARANTINED_BLOCK | Unreferenced; grace |
| LEGAL_HOLD | No GC |

### Appendix B — Revision record (sample)

```json
{
  "file_id": "f_123",
  "rev": "r_11",
  "parent_rev": "r_10",
  "blocks": ["sha256:aa", "sha256:bb"],
  "size": 8388608,
  "mtime_client": 1720000000,
  "device_id": "d_9",
  "idempotency_key": "idem_abc"
}
```

### Appendix C — Sync response (sample)

```json
{
  "entries": [
    {"mut_id": 101, "op": "upsert", "path": "/Docs/a.bin", "rev": "r_11", "blocks": ["sha256:aa"]}
  ],
  "next_cursor": "150",
  "reset": false
}
```

### Appendix D — Conflict copy policy

```text
On 409:
  local_path' = stem + " (conflicted copy from " + device_name + ")" + ext
  commit as new file entry OR new rev marked CONFLICT_COPY
  keep both; notify user
```

### Appendix E — AuthZ check for block GET

```text
1. Validate signed capability or session
2. Capability lists file_id + rev or hash set
3. Ensure requested hash ∈ file's block list
4. Enforce share expiry / revocation gen
5. Stream bytes
```

### Appendix F — Error codes

| Code | Meaning |
|------|---------|
| 409 | Revision conflict |
| 413 | Quota exceeded |
| 403 | AuthZ denied |
| 404 | Missing entry/block |
| 412 | Precondition (parent) failed |
| 429 | Rate limited |

### Appendix G — Anti-patterns

- Meta listings via S3 `ListObjects` as filesystem.  
- Global dedup HEAD without authz.  
- Commit ACK before block durability.  
- Silent overwrite on conflict.  
- Per-second sync poll from all clients.  
- Single shared Postgres for all users.  
- POSIX locks over WAN.  
- Mixing preview failures into sync critical path.

### Appendix H — Capacity worksheet

```text
meta_qps_peak =
block_put_qps_peak =
ingress_GB_s =
watchers_active =
changelog_partitions =
orphan_gc_lag_hours =
avg_dedup_ratio =
```

### Appendix I — 45-minute timebox

| Min | Topic |
|-----|-------|
| 0–5 | Requirements + out of scope |
| 5–12 | BOTE split planes |
| 12–25 | HLD APIs + commit/sync |
| 25–35 | Conflicts, dedup, sharing |
| 35–42 | Scale 10×/100×/1,000× + ownership |
| 42–45 | Wrap risks / SLOs |

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| Namespace | Sync root (user/shared) |
| Revision | Immutable file version |
| Chunk/Block | Content-addressed piece |
| Cursor | Sync position in changelog |
| Conflict copy | Preserved divergent edit |
| Capability | Authz token for bytes |
| Cell | Independent meta+log slice |

### Appendix K — Ownership RACI

| Item | R | A | C | I |
|------|---|---|---|---|
| Commit durability | Meta+Blob | Meta | Client | SRE |
| Conflict UX | Client | Product | Meta | Support |
| GC | Lifecycle | Blob | Meta | Legal |
| Hot share | Meta | Meta | Notify | Capacity |

### Appendix L — Progressive scale one-pager

| Scale | Must have |
|-------|-----------|
| 1× | Chunk+commit+cursor+conflict copy |
| 10× | Notify; GC; quotas; AV hook |
| 100× | Cells; EC/cold; isolate hot ns |
| 1,000× | Hierarchical watch; edge upload; CDC |

### Appendix M — Chunk size worksheet

```text
1 GB file / 4 MB = 256 chunks
Overhead meta per chunk ~100B → 25KB
Small 10KB files → 1 chunk each; consider packing later
```

### Appendix N — Minimal threat model

| Threat | Control |
|--------|---------|
| Unauthorized read | ACL + signed GET |
| Hash oracle | No cross-tenant exists |
| Ransomware | Versions + anomaly |
| Link leak | Expiry + revoke |
| Malware share | AV pipeline |
| Metadata tamper | Authn + audit |

### Appendix O — Commit pseudocode

```text
function commit(file_id, parent, blocks, idem):
  if cache[idem]: return cache[idem]
  for h in blocks: assert durable(h)
  txn:
    if head(file_id) != parent: abort 409
    rev = new_rev()
    save(rev, blocks)
    set_head(file_id, rev)
    log.append(...)
  cache[idem] = rev
  notify.bump(ns)
  return rev
```

### Appendix P — Client sync pseudocode

```text
while running:
  wait_notify(cursor)
  resp = sync(cursor)
  if resp.reset: full_hydrate()
  else:
    for m in resp.entries: apply(m)
  cursor = resp.next_cursor
```

### Appendix Q — Quota event (sample)

```json
{"user_id":"u1","delta_bytes":8388608,"reason":"commit","rev":"r_11","ts":1720000001}
```

### Appendix R — Interview “say this” (60 seconds)

> “I’d separate metadata from content-addressed chunks. Clients upload chunks, then CAS-commit a revision. Sync is cursor-based changelogs with long-poll notify. Concurrent edits become conflict copies—no silent loss. Sharing is ACL/capability, and hash≠permission. We scale by sharding namespaces into cells and isolating hot shared folders; cost via dedup, EC, and cold tiers. Dedup never becomes a cross-tenant oracle.”

### Appendix S — Related systems map

| System | Relation |
|--------|----------|
| S3 / object store | Block plane |
| DynamoDB / Spanner | Meta plane |
| Kafka | Changelog transport option |
| Dropbox / Drive | Product analogues |
| Git | Rev lineage inspiration (not UX) |
| CAS stores | Dedup heritage |

### Appendix T — Chaos drill list

1. Kill meta primary during commit.  
2. Block store latency injection.  
3. Notify broker down.  
4. GC delete race with commit.  
5. Hot share mutation flood.  
6. Clock jump on clients.  
7. Dual device conflict storm.  
8. Restore from backup drill.

### Appendix U — Upload validation checklist

- Auth session valid  
- Chunk size ≤ max  
- Hash matches body  
- Quota headroom  
- Rate limit  
- Malware async enqueue on commit  
- Idempotency key present for commit

### Appendix V — Comparison checklist vs common designs

| Checkpoint | Covered? |
|------------|----------|
| Plane split | Yes |
| CAS commit | Yes |
| Conflict policy | Yes |
| Dedup safety | Yes |
| Notify model | Yes |
| Progressive scale | Yes |
| Ownership/SLOs | Yes |
| Deal-breakers | Yes |

### Appendix W — Version restore flow

```text
User picks rev r5 → create new rev r12 with same block list as r5
parent = current head (r11) OR explicit restore semantics
Changelog upsert; other devices hydrate if needed
```

### Appendix X — Link share flow

```text
POST /links {path, role:viewer, expires}
→ token
GET /l/{token} → capability session
List/download under ACL of token; typically no sync watcher registration for anonymous
```

### Appendix Y — Metrics catalog

- `commit_success_rate`  
- `commit_conflict_rate`  
- `chunk_put_bytes`  
- `sync_delta_latency`  
- `notify_wake_latency`  
- `orphan_bytes`  
- `dedup_ratio`  
- `hot_namespace_qps`  
- `quota_reject_rate`

### Appendix Z — Final checklist for SDE III

- [ ] Requirements bounded; Docs/POSIX out  
- [ ] BOTE splits meta/blocks/notify  
- [ ] APIs for chunk, commit, sync, share  
- [ ] Conflict copies explicit  
- [ ] Dedup threat discussed  
- [ ] Cells / hot share plan  
- [ ] GC & durability invariants  
- [ ] Ownership & SLOs  
- [ ] 10×/100×/1,000× narrative  
- [ ] Deal-breakers listed  

---

*End of Dropbox-like file storage system design (Amazon SDE III).*
