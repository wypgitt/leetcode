# System Design: Dropbox / Google Drive (Cloud File Sync)

> **Focus areas:** Chunked upload · Metadata vs block storage · Client sync protocol · Conflict resolution · Change notifications · Dedup  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split metadata/block/notification planes, explicit sync cursors & conflicts, deal-breakers for “POSIX locking over WAN” fantasies  
> **Interview theme:** **2024 Meta E5** — cloud drive / Dropbox-like sync: not a trivial object store; the hard part is **correct sync**, metadata consistency, and notify-at-scale  
> **Company flavor:** Meta E5 bar — progressive scale narrative, clear tradeoffs, BOTE that separates tiny metadata QPS from huge block bytes, explicit conflict model

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

Goal: **bound the product**—a **Dropbox / Google Drive–class** personal/shared cloud filesystem: upload/download files, sync folders across devices, share with users, detect changes, resolve conflicts, and notify clients—**not** a raw S3 clone alone and **not** a collaborative Google Docs CRDT editor (mention as adjacent).

### 1.0 What this is / is not

| Dimension | **Cloud Drive / Sync (this doc)** | Not this |
|-----------|-----------------------------------|----------|
| Primary job | Sync files/folders across devices + cloud | News Feed / chat |
| Success | Correct eventual sync, few conflicts, fast delta | Perfect WAN POSIX |
| Metadata | Hierarchical namespace, versions, permissions | Only object key/value |
| Data plane | Chunked/block content-addressed store | Whole-file only reupload |
| Hard problem | Sync protocol + conflicts + notify | Training ML models |
| Collab editing | File replace / versioning MVP | Real-time OT/CRDT docs |

**Scope statement:** Design Dropbox/Google Drive: chunked upload, metadata namespace, multi-device sync, conflict handling, sharing, and change notifications—at E5 depth with progressive scale.

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
| F10 | Quotas? | Per-user storage caps | Usage accounting |
| F11 | Offline? | Local edits while offline; sync later | Client journal + conflict |
| F12 | Preview? | Thumbnails / docs preview Phase 1.5 | Async processors |

**MVP functional scope:**

1. **Namespace:** create/rename/move/delete files and folders under a user’s root (and shared folders).  
2. **Chunked upload:** split file → upload blocks → commit revision with block list.  
3. **Download / hydrate:** fetch blocks by hash; reconstruct file.  
4. **Sync protocol:** clients maintain cursor; pull changelog of metadata mutations.  
5. **Conflict policy:** if two devices commit diverging revisions from same parent → conflict copy (Dropbox-style) or last-writer-wins with version history (document choice).  
6. **Sharing:** grant user/view/edit on subtree; link tokens.  
7. **Notifications:** wake clients when namespace changes in watched roots.  
8. **Quotas & auth**; basic version history restore.

**Out of MVP:**

- Google Docs real-time collaborative editing (OT/CRDT)  
- Full-text content search across all files (hooks)  
- Arbitrary POSIX flock over network  
- Cross-region strongly consistent dual-active metadata writers  
- End-to-end encrypted vault deep dive (can mention)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Metadata op latency | Snappy UX | p99 < 100–200ms |
| N2 | Upload throughput | Saturate user bandwidth | Chunk parallel; resume |
| N3 | Durability | No silent loss after commit ACK | Multi-AZ blocks + meta |
| N4 | Sync freshness | Remote edits appear soon | Notify < few seconds typical |
| N5 | Consistency | Per-file linear revisions; namespace atomic ops | CAS on revision parent |
| N6 | Availability | High | 99.9%+; degrade previews first |
| N7 | Dedup safety | No cross-tenant leak via hash | AuthZ always on meta; careful hash APIs |
| N8 | Scale | Billions of files | Metadata sharded; blocks object store |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Alice uploads `video.mp4` from desktop → chunks upload → commit rev1 → phone notified → downloads deltas.  
2. Alice renames folder → metadata mutation → other devices apply rename without re-downloading blocks.  
3. Bob edits shared doc offline → Alice also edits → sync → **conflict copy** created; both versions preserved.  
4. Alice shares folder with Carol → Carol sees subtree; ACL checked on list/download.  
5. Alice restores prior version → new revision pointing at old block list.  
6. Identical file uploaded by two users → blocks deduped; separate metadata inodes.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Commit with unknown parent rev | 409 conflict → client rebase/conflict copy |
| Chunk upload fails mid-way | Resume missing chunks; commit only when complete |
| Orphan chunks | GC after TTL if unreferenced |
| Move folder cycles | Reject cycles; transactional move |
| Permission revoked mid-download | AuthZ fail subsequent blocks |
| Hash collision fantasy | Use SHA-256; ignore birthday fear in interview |
| Notify storm (huge folder) | Compact changelog; coalesce events |
| Clock skew | Server timestamp + logical rev ids |
| Partial local apply | Client journal; idempotent apply by mutation id |
| Dedup confirmation attack | Don’t expose “hash exists” across tenants without ownership |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 10M | 100M | 1B | multi-B |
| Files (namespace entries) | 10B | 100B | 1T | multi-T |
| Avg file size | 1 MB | 1 MB | 1–2 MB | mixed |
| Chunk size | 4 MB | 4 MB | 1–4 MB | adaptive |
| Peak metadata QPS | 50K | 500K | 5M | 50M |
| Peak chunk put QPS | 20K | 200K | 2M | 20M |
| Peak ingress GB/s | 10 | 100 | 1K | 10K |
| Sync notify watchers | 5M | 50M | 500M | huge |
| Shared folder members avg | small | skewed | celebrity folders | caps / fan-out |
| Versions retained | 100 / 30d | policy | tiered | cold |

**What each jump forces:**

- **10×:** Split metadata DB vs block store; chunked upload; changelog cursors.  
- **100×:** Metadata cells by namespace; notify fan-out service; block EC/cold tier; GC fleets.  
- **1,000×:** Hierarchical notify; bloom/watch compaction; edge upload; strict isolation of hot shared folders.

### 1.5 Etc. (Constraints & Assumptions)

- Clients are **smart** (desktop agent / mobile app) with local DB — sync protocol is first-class.  
- **Blocks are immutable**; updates create new revisions.  
- Interview (Meta E5 2024): expect deep dive on **sync + conflicts**, not only S3 APIs.  
- Previews/virus scan = async pipeline hooks.  
- Strong consistency **per namespace partition**; global linearizability across all users unnecessary.

**Scope statement to repeat back:**

> Design a Dropbox/Google Drive–class system: chunked content-addressed storage, hierarchical metadata with revision CAS, multi-device sync via changelogs and notifications, explicit conflict copies, sharing ACLs, and progressive scale—separating metadata QPS from block bandwidth, without pretending we offer WAN POSIX locks.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Metadata ops** | mkdir/rename/commit/list | ~50K/s | ~500K/s | Metadata DB |
| **Chunk uploads** | Block puts | ~20K/s | ~200K/s | Block/object store |
| **Chunk downloads** | Block gets | higher than puts | ×10 | Block + CDN/cache |
| **Changelog reads** | Sync pull | ~users reconnecting | ×10 | Changelog / meta |
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
  Assume avg file 1 MB, chunk 4 MB → many files single chunk
  10B × 1 MB = 10 EB logical — wait, 10B × 1MB = 10 PB logical
  With replication×3 → 30 PB; with dedup lower
  Interview: keep orders straight — **PB-scale data**, **TB-scale metadata**
```

### 2.3 Upload math

```text
Peak ingress 10 GB/s
Chunk 4 MB → chunk puts/s = 10 GB/s / 4 MB = 10e9 / 4e6 = 2,500/s average?
Peak often higher burst: design for 20K chunk puts/s baseline peak

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
```

### 2.7 Progressive BOTE summary

| Scale | Files | Meta QPS | Ingress | Notify model |
|-------|-------|----------|---------|--------------|
| Baseline | 10B | 50K | 10 GB/s | Long-poll + push |
| 10× | 100B | 500K | 100 GB/s | Sharded changelog |
| 100× | 1T | 5M | 1 TB/s | Cells + edge upload |
| 1,000× | multi-T | 50M | extreme | Hierarchical watch |

### 2.8 Metadata memory & partition counts

```text
Namespace node ~150–300B + indexes
10B files × 200B = 2TB meta raw — sharded by namespace_id
Hot namespaces (shared folders) get dedicated shards

Block index: content_hash → locator, size, refcount
  distinct blocks << files if dedup; 1B blocks × 64B ≈ 64GB index order (compressed)

Kafka/changelog: partitions by namespace_id; 512→8K
```

### 2.9 Upload amplification & naive cost

| Naive | Cost | Fix |
|-------|------|-----|
| Whole-file reupload on 1B change | bandwidth death | Chunk/CDC |
| Meta in object store only | list/rename hard | Explicit namespace DB |
| Notify all members with payloads | storm | Cursor+pull |
| Cross-user dedup without authz | leak via timing | Careful capability |
| Sync poll 1s × 100M clients | origin death | Long-poll/push |

```text
Chunk 4MB: 1GB file = 256 blocks; parallel PUT; commit manifests once
CDC: better delta; more CPU; watch chunk explosion small files
```

### 2.10 Sync storm math

```text
1M clients wake: need notify or long-poll fanout control
Changelog read: O(delta) not O(tree)
If cursor compacted past: full rescan / snapshot hydrate — rare expensive path
```

### 2.11 10×/100×/1,000× card

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Meta QPS | 50K | 500K | 5M | cells |
| Ingress | 10GB/s | 100GB/s | 1TB/s | edge upload |
| Notify | push/longpoll | sharded | hierarchical watch | |
| Dedup | optional | opportunistic | EC+dedup careful | |

**Pitch:** “Drive = chunked content plane + strongly consistent namespace metadata + cursor sync. Commit is atomic metadata transaction after blocks durable.”


---

## 3. High-Level Design

### 3.1 APIs

#### 3.1.1 Chunk / block upload

```http
POST /v1/blocks/{content_hash}
Content-Type: application/octet-stream
Content-Length: ...
If-None-Match: *   # optional skip if exists (authz!)

→ 201 { "hash": "...", "size": 4194304 }
→ 200 already exists (if permitted)
```

#### 3.1.2 Commit file revision

```http
POST /v1/files/{file_id}/revisions
{
  "parent_rev": "r_10",
  "blocks": ["sha256:aa...", "sha256:bb..."],
  "size": 8388608,
  "client_mtime": 1720000000,
  "idempotency_key": "..."
}

→ 201 { "rev": "r_11", "path": "/Docs/a.bin" }
→ 409 { "error": "conflict", "server_rev": "r_12", ... }
```

#### 3.1.3 Namespace mutations

```http
POST /v1/entries
{"op":"mkdir","path":"/Projects","parent_rev":"..."}

POST /v1/entries/move
{"from":"/a","to":"/b","parent_rev_from":"..."}

DELETE /v1/entries?path=/a&rev=...
```

#### 3.1.4 Sync changelog

```http
GET /v1/sync?namespace_id=&cursor=cur_123&limit=500
→ {
  "entries": [ {"mut_id":..., "op":"update", "path":"...", "rev":"...", "blocks":[...]} ],
  "next_cursor": "cur_456",
  "reset": false
}
```

#### 3.1.5 Notifications

```text
LONGPOLL /v1/notify?cursor=...  → 200 when changes or timeout
# or WebSocket: push {namespace_id, new_cursor}
```

#### 3.1.6 Sharing

```http
POST /v1/shares
{"path":"/Projects","principal":"user:u2","role":"editor"}
```

### 3.2 Core data model / schema

**namespaces**

| Column | Type | Notes |
|--------|------|-------|
| namespace_id | id | user root or shared folder |
| owner_id | id | |
| type | personal/shared | |

**entries** (inode-like)

| Column | Type | Notes |
|--------|------|-------|
| entry_id | id | PK |
| namespace_id | id | shard key |
| parent_id | id | folder |
| name | str | unique among siblings |
| type | file/folder | |
| current_rev | id | files |
| deleted | bool | tombstone |
| path_key | str | materialized path optional |

**revisions**

| Column | Type | Notes |
|--------|------|-------|
| rev_id | id | PK |
| file_id | id | |
| parent_rev | id null | CAS chain |
| blocks | []hash | ordered |
| size | i64 | |
| mtime | ts | |
| writer_device | id | |

**blocks**

| Column | Type | Notes |
|--------|------|-------|
| content_hash | sha256 | PK |
| size | i64 | |
| storage_locator | | object store key |
| refcount | i64 | GC |

**changelog**

| Column | Type | Notes |
|--------|------|-------|
| namespace_id | id | shard |
| cursor / mut_id | monotonic | |
| op | upsert/delete/rename | |
| payload | json | |

**ACLs**

| Column | Type | Notes |
|--------|------|-------|
| entry_id | id | |
| principal | user/group/link | |
| role | viewer/editor/owner | |

**Why:** immutable blocks + revision pointers make sync/restore/dedup tractable; changelog enables cursor sync without scanning the world.

### 3.3 Why X over Y

| Decision | Choose | Over | Why | Deal-breaker if wrong |
|----------|--------|------|-----|------------------------|
| Upload | **Chunk + commit** | Single PUT whole file | Resume, dedup, parallel | 10 GB retry from 0 |
| Addressing | **Content-hash blocks** | Mutable block ids only | Dedup + integrity | No checksum story |
| Namespace | **Metadata DB** | Paths in object store only | Rename/move cheap | Rename = rewrite all objects |
| Sync | **Changelog cursor** | Full tree scan each time | Delta efficiency | Rescan 1M files/device |
| Conflicts | **Conflict copy (MVP)** | Silent LWW only | User data safety | Silent data loss |
| Notify | **Cursor + push/longpoll** | Tight busy poll | Scale | 167K+/s useless polls |
| Consistency | **CAS parent_rev** | Blind overwrite | Detect races | Lost updates |
| Sharing | **ACL on meta** | ACL on each block | Blocks reused | Broken dedup auth |

### 3.4 Component overview

1. **Client Sync Engine** — local DB, journal, chunker.  
2. **API Gateway** — auth, rate limits.  
3. **Metadata Service** — namespace, revisions, CAS.  
4. **Metadata Store** — NewSQL/Spanner-like or sharded MySQL.  
5. **Block Service** — put/get by hash.  
6. **Object / Block Store** — multi-AZ blob (HDFS/S3-like).  
7. **Changelog / Sync Service** — cursors.  
8. **Notification Service** — long-poll/WS/push.  
9. **ACL / Share Service**.  
10. **GC Workers** — orphan blocks.  
11. **Async Processors** — virus scan, thumbnails, search index.  
12. **Quota Service**.

### 3.5 End-to-end flows

**Upload + sync:**

```text
Client chunks file → parallel PUT blocks (auth, quota reserved)
Client COMMIT rev with parent_rev + block list
Metadata: CAS parent → write rev → append changelog → ACK
Notify watchers (cursor bump)
Other clients: notify → GET sync → download missing blocks → apply locally
```

**Conflict:**

```text
Device A commits parent=r10 → r11
Device B commits parent=r10 → 409
Client B downloads r11; if local dirty: create "file (conflicted copy).ext" as new file
  OR rebase if mergeable (text) — MVP: conflict copy
```

### 3.6 Consistency model

| Object | Model | Notes |
|--------|-------|-------|
| Block bytes | Durable immutable | Content-hash |
| Namespace commit | Strong per namespace | Atomic rev++ |
| Sync views | Eventual via changelog | Cursor |
| Cross-namespace move | Txn or two-phase | Careful |
| Sharing ACL | Strong on access checks | |

**Deal-breaker:** marking file committed before all blocks durable and manifest linked.

### 3.7 API edge cases

| Case | Behavior |
|------|----------|
| Commit missing block | 409 INCOMPLETE |
| Conflict rev | 409 CONFLICT → conflict copy / merge |
| Cursor too old | 410 → resnapshot |
| Rename storm | Coalesce changelog |
| Dedup hash exists | AuthZ capability; no oracle |
| Quota exceed | 413/403 before commit |
| Delete open on other device | Changelog delete event |

### 3.8 Schema indexes

```text
nodes: PK(namespace_id, node_id); UNIQUE(namespace_id, parent_id, name_norm);
      INDEX(namespace_id, parent_id) -- list dir
revs: (namespace_id, rev) changelog
blocks: PK(content_hash); refcount
pending_uploads: (session_id, file_id)
shares: (resource_id, grantee)
```

### 3.9 Why X over Y expanded

| Topic | Prefer | Avoid |
|-------|--------|-------|
| Bytes | Chunk object store | Single blob always |
| Meta | OLTP/NS DB | Paths as sole S3 keys |
| Sync | Changelog cursor | Full tree poll |
| Conflict | Conflict copy / UTR | Silent LWW data loss |
| Dedup | Optional encrypted | Blind cross-tenant oracle |
| Notify | Invalidate+pull | Push file bytes |

### 3.10 HLD pitch

> “Clients upload blocks by hash, then commit a metadata revision that points to the manifest. Sync peers follow namespace changelog cursors. Sharing is ACL on namespace/nodes. Dedup and GC are refcount/careful. Scale metadata by namespace_id; scale bytes by object store.”


---

## 4. Architecture Diagram

```text
 +------------------+         +------------------+
 | Desktop Sync     |         | Mobile App       |
 | (local DB/journ) |         |                  |
 +--------+---------+         +--------+---------+
          |                            |
          +-------------+--------------+
                        |
                        v
               +------------------+
               |   API Gateway    |
               +--------+---------+
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
 +-------------+ +--------------+ +---------------+
 | Metadata    | | Block Service| | Notify/Sync   |
 | Service     | | (hash put)   | | Service       |
 +------+------+ +------+-------+ +-------+-------+
        |               |                 |
        v               v                 v
 +-------------+ +--------------+ +---------------+
 | Meta DB     | | Object Store | | Changelog     |
 | ns/entries/ | | multi-AZ/EC  | | per namespace |
 | revs/ACLs   | +--------------+ +---------------+
 +------+------+
        |
        v
 +-------------+     +----------------+
 | Quota/ACL   |     | GC / Preview / |
 |             |     | Virus / Index  |
 +-------------+     +----------------+

 Watch path: Metadata commit → changelog → Notify fanout → clients pull sync
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Commit ACK ⇒ revision durable** and blocks referenced exist (or commit rejects).  
2. **Blocks immutable**; never mutate hash bytes in place.  
3. **CAS on parent_rev** (or compare-and-swap current_rev) detects concurrent writers.  
4. **Changelog monotonic cursors** per namespace; clients can catch up.  
5. **AuthZ on every download** via metadata — hash knowledge ≠ access.  
6. **GC never deletes referenced blocks** (refcount / mark-sweep with generation).  
7. **Conflict policy never silently drops unique user bytes** in MVP (prefer conflict copy).

#### 5.1.2 Commit atomicity

```text
txn:
  assert file.current_rev == parent_rev
  verify all blocks present + owned/allowed
  insert revision
  update file.current_rev
  append changelog mutation
  update quota usage
commit → notify
```

If crash after blocks uploaded but before commit: orphan chunks → GC TTL.

#### 5.1.3 Exactly-once commits

Idempotency key on commit → same rev returned; safe client retry.

#### 5.1.4 Notification reliability

Notify is **best-effort wake-up**; client always reconciles via cursor.  
**Deal-breaker:** treating push notify as SoT without changelog.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Orphan chunks | TTL GC |
| 10× | Hot metadata partitions | Shard by namespace_id |
| 100× | Notify storms | Coalesce; pull model |
| 1,000× | Shared folder celebrity | Cap watchers; hierarchical cursors; read replicas |

#### 5.1.6 Retries & idempotency

```text
Block PUT idempotent by content_hash
Commit idempotency_key → same rev
Notify at-least-once; clients pull changelog idempotently
```

#### 5.1.7 Data-loss prevention

1. Blocks durable (multi-AZ/EC) before commit.  
2. Commit atomic rev bump.  
3. Refcount GC only after grace.  
4. Changelog durable; snapshots for compaction.

#### 5.1.8 Consistency under partition

```text
Namespace primary fenced — no dual writers
Clients offline edit → conflict on reconnect
Cross-region: namespace home; bytes may be geo-replicated async with session guarantees productized
```

### 5.2 Scalability

#### 5.2.1 Chunking strategy

| Approach | Pros | Cons |
|----------|------|------|
| Fixed 4 MB | Simple | Boundary shifts → poor delta |
| Content-defined (CDC/rsync-like) | Better delta/dedup | CPU cost |
| MVP | Fixed size OK | Mention CDC as Phase 2 |

Large file 8 GB / 4 MB = 2000 chunks — parallel upload with window.

#### 5.2.2 Metadata sharding

- Shard key: `namespace_id` (user root or shared folder id).  
- List directory: by `(namespace_id, parent_id, name)`.  
- Avoid global path string as only key — store parent links; materialize path carefully.  
- Cross-namespace move (to different shared folder) = copy or special txn.

#### 5.2.3 Sync protocol deep dive

```text
Client state: cursor C, local tree
Loop:
  wait notify(C) or timer
  changes, C' = sync_pull(C)
  for mut in changes:
    apply_idempotent(mut)  # may download blocks
  cursor = C'
```

**Reset flag:** if server compacted history beyond C, client does guided resync (hash tree / directory crawl).

**Incremental vs full:**

- Incremental changelog for online devices.  
- Snapshot + changelog for new devices.

#### 5.2.4 Conflict resolution deep dive

| Strategy | Behavior | When |
|----------|----------|------|
| **Conflict copy** | Keep both trees as siblings | Dropbox classic; safest MVP |
| LWW + history | Winner becomes current; loser in versions | User-visible risk if silent |
| App-level merge | Text merge | Docs editors — out of MVP |
| Manual | Prompt user | Mobile UX optional |

E5 signal: **state parent_rev CAS** + **product policy** clearly.

#### 5.2.5 Notifications at scale

```text
commit → publish(namespace_id, cursor)
notify service maintains watchers by namespace
wake long-pollers / WS
large membership: don't push full payloads — only "cursor advanced"
```

#### 5.2.6 Dedup & security

```text
PUT block(hash, bytes):
  verify hash(bytes)==hash
  store if new
GET block(hash):
  require capability token from metadata (file rev grant)
  NOT world-readable by hash alone
```

Confirmation-of-file attacks: restrict “exists?” responses across tenants.

#### 5.2.7 GC

- Refcount on commit/delete + async verify.  
- Or mark-sweep: enumerate revisions → live hashes → delete unknown older than grace.  
- Incomplete uploads expire.

#### 5.2.8 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Meta/block split; changelog; chunk resume |
| →100× | Namespace cells; notify service; EC cold; GC fleets |
| →1,000× | Edge upload POPs; CDC chunking; hierarchical watches; search/preview platforms |

#### 5.2.9 Hot namespaces

```text
Shared folder 100K watchers: sharded notify; clients pull; rate-limit list/
Metadata hotspot: split namespace or cache dir listings with rev
```

#### 5.2.10 Cache hierarchy

```text
Client local disk cache
API: dir list by (namespace, parent, rev)
Block CDN/POP for hot hashes
Meta primary for commits
```

#### 5.2.11 Backpressure

```text
Upload storm: admit per-user bandwidth tokens
Changelog lag: enlarge readers; snapshot shortcut if too far
```

#### 5.2.12 Path evolution

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Upload | parallel chunks | edge ingest | regional buckets |
| Commit | NS shard | cell | hierarchical NS |
| Sync | long-poll | push invalidate | watch tree |
| GC | batch | distributed | priority queues |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
chunk_size_mb: 4
max_commit_blocks: 25000
conflict_policy: conflict_copy
changelog_retain: 30d
orphan_block_ttl: 7d
notify_timeout_s: 30
max_shared_watchers: 50k
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `commit_qps` / `commit_conflict_rate` | Sync health |
| `chunk_put_qps` / ingress_bps | Data plane |
| `sync_lag_ms` | Freshness |
| `notify_wake_qps` | Fan-out |
| `orphan_bytes` | GC |
| `quota_reject_qps` | Product |
| `acl_deny_qps` | Security |

#### 5.3.3 Testing

- CAS conflict property tests.  
- Chaos mid-commit / mid-chunk.  
- Offline edit dual-device conflict fixtures.  
- Rename under write races.  
- AuthZ: hash leak attempts.  
- Cursor compaction / reset path.

#### 5.3.4 Safe evolution

Phase 1: single region; fixed chunks; conflict copy.  
Phase 2: sharing + notify polish.  
Phase 3: cells + CDC + cold tier.  
Phase 4: content search / previews / E2EE vaults.

### 5.4 Commit protocol deep dive

```text
1) Client ensures all blocks stored (receipts)
2) BEGIN meta txn: check parent rev/name; quota; ACL
3) Write node + manifest pointer; rev++; append changelog
4) COMMIT; notify watchers (async)
Crash before 3: no file; blocks eventually GC
Crash after 3: file exists; notify retry OK
```

### 5.5 Conflict & sync semantics

```text
If base_rev stale: reject or auto conflict-copy
Folder rename vs edit: operational transform lite / conflict copies
Selective sync: client filters paths; server still versions
```

### 5.6 Security & dedup

```text
Hash preimage/oracle: require write capability / encrypted store
Virus scan async; quarantine pointer
Link shares: capability tokens short-lived
```

### 5.7 Progressive evolution

| Stage | Bytes | Meta | Sync |
|-------|-------|------|------|
| MVP | chunk S3 | SQL NS | poll |
| Prod | dedup+EC | sharded NS | cursor+push |
| Scale | edge | cells | hierarchical watch |


---

## 6. Wrap-Up

### 6.1 What we designed

A **Dropbox/Google Drive–class sync system** with content-addressed chunk storage, hierarchical metadata + revision CAS, changelog-cursor sync, conflict copies, ACL sharing, notification wake-ups, GC, and progressive scale—aimed at **Meta E5 (2024)** depth: sync correctness over “just object storage.”

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Planes | Metadata ≠ blocks ≠ notify |
| Upload | Chunk then atomic commit |
| Sync | Changelog + cursor; notify is hint |
| Conflicts | CAS parent_rev + conflict copy MVP |
| Dedup | Hash blocks; authz via capabilities |
| Rename | Metadata op, not block rewrite |

### 6.3 Closing line

> “Drive is a sync protocol problem backed by an object store—if you only design S3 PUTs without revisions, changelogs, and conflict CAS, you’ll fail the E5 hard part.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Chunking & upload

**Q1: Why chunk files?**  
A: Resume, parallelism, dedup, bounded retries; commit assembles the file revision.

**Q2: Fixed vs content-defined chunking?**  
A: Fixed is simpler MVP; CDC improves delta uploads when bytes shift mid-file; cost is CPU.

**Q3: When is a file “safe” in the cloud?**  
A: After commit ACK with durable meta+blocks; chunk PUT alone is insufficient.

**Q4: How to prevent incomplete commits?**  
A: Commit verifies all block hashes exist; else 400; client retries missing puts.

**Q5: Ideal chunk size?**  
A: ~1–4 MB balances PUT overhead vs parallelism; tune with RTT and object-store limits.

**Q6: Multipart vs app-level chunks?**  
A: Similar ideas; app-level hashes enable dedup across files/users; both acceptable if clear.

### 7.2 Metadata & namespace

**Q7: Why not store path as object key only?**  
A: Renames/moves would rewrite data; listing/ACLs/versions harder; meta inode model wins.

**Q8: How do renames work?**  
A: Metadata transaction updates parent/name; changelog emits rename; blocks untouched.

**Q9: Directory list at scale?**  
A: Paginate by name; cache hot dirs; avoid recursive listing APIs without bounds.

**Q10: Materialized path vs parent pointers?**  
A: Parent pointers authoritative; materialized path for UX/search with careful updates.

**Q11: Cross-folder move atomicity?**  
A: Single meta txn within namespace; cross-namespace may be copy+delete.

### 7.3 Sync & notifications

**Q12: What is a cursor?**  
A: Opaque monotonic position in a namespace changelog; clients pull `> cursor`.

**Q13: Why not poll every second?**  
A: QPS explodes; use long-poll/WS wake + backoff polls.

**Q14: What if changelog compacted past cursor?**  
A: Return `reset=true`; client performs snapshot resync.

**Q15: How fast should remote edits appear?**  
A: Seconds typical; not hard realtime like chat; still notify-driven.

**Q16: Does notify carry file bytes?**  
A: No — wake + cursor; client fetches meta/blocks as needed.

### 7.4 Conflicts & versions

**Q17: How detect conflicts?**  
A: Commit includes `parent_rev`; server CAS fails if current ≠ parent.

**Q18: Conflict copy vs LWW?**  
A: Conflict copy preserves both edits (safer MVP); LWW simpler but can surprise users; always keep history if LWW.

**Q19: Can folders conflict?**  
A: Yes — concurrent mkdir/rename; may produce conflicted folder names or merge children by policy.

**Q20: Restore old version?**  
A: Create new revision pointing at old block list (COW metadata).

**Q21: Deletes with sync?**  
A: Tombstone mutation in changelog; clients trash locally; GC later.

### 7.5 Sharing & security

**Q22: Where are ACLs enforced?**  
A: Metadata list/commit/get; block get requires short-lived capability tied to authorized rev.

**Q23: Link sharing?**  
A: Token principal with role; rate-limit; optional password/expiry.

**Q24: Dedup cross-tenant leak?**  
A: Never grant block access by hash alone; existence oracles restricted.

**Q25: Stolen hash?**  
A: Without capability, GET fails; hash isn’t a capability.

### 7.6 Storage & GC

**Q26: Refcount vs mark-sweep?**  
A: Refcount fast but brittle under races; mark-sweep safer at scale with grace periods; hybrid common.

**Q27: Replication vs erasure coding?**  
A: Hot recent blocks replicated; cold EC for cost; restore bandwidth tradeoff.

**Q28: Hot blocks?**  
A: Cache/CDN for popular shared content; meta still authz.

**Q29: Quota accounting?**  
A: Charge logical namespace usage (dedup billing policy product-specific — lock with interviewer).

### 7.7 Scale & E5 narrative

**Q30: Biggest E5 distinction vs junior design?**  
A: Sync protocol, CAS conflicts, changelog/notify, and plane separation—not drawing three boxes labeled “upload service.”

**Q31: 10× vs 100×?**  
A: 10× chunk+changelog; 100× cells, notify storms, GC/EC, shared-folder fan-out controls.

**Q32: Deal-breakers?**  
A: Whole-file only; silent overwrite conflicts; notify as SoT; path-as-S3-key renames; hash-is-capability; busy poll; WAN POSIX locks.

**Q33: Offline edits?**  
A: Client journals local mutations; on reconnect replay commits; resolve 409s with conflict copies.

**Q34: Mobile vs desktop sync?**  
A: Same protocol; mobile may selective sync / on-demand hydrate to save disk/battery.

**Q35: Virus scanning?**  
A: Async after commit; quarantine flag in meta; download may block until clean for enterprise tiers.

**Q36: Search filenames?**  
A: Secondary index on meta mutations; eventual; content search separate pipeline.

**Q37: Why Meta asks this?**  
A: Tests distributed systems fundamentals: consistency, sync, scale math, product-aware conflicts—transferable to Meta infra/product.

**Q38: Comparison Dropbox vs Drive?**  
A: Similar bones (chunk/meta/sync); Drive pairs with Docs collab (out of scope); Dropbox historically sync-engine famous—interview for shared core.

---

### 7.8 Algorithms & hashing

**Q39: Content-defined chunking (CDC) vs fixed?**  
A: CDC better deltas across inserts; fixed simpler; mixed policies OK.

**Q40: Merkle trees for sync?**  
A: Useful for directory diff; changelog often simpler for product sync.

**Q41: Consistent hashing of blocks?**  
A: Object store handles placement; meta stores locator; hash is content id.

**Q42: How to shard hot shared folder?**  
A: Sub-namespace mounts or metadata secondary indexes + notify shards.

### 7.9 LB, failure, memory

**Q43: LB for upload?**  
A: Edge route to nearest ingest; authz then PUT to store.

**Q44: Metadata primary fails mid-commit?**  
A: Txn abort; client retries idempotent commit; no partial node.

**Q45: Memory for block bloom filters?**  
A: Optional existence Bloom to skip uploads — careful oracle; per-tenant.

### 7.10 Estimation closers

**Q46: 1PB logical with 30% dedup savings?**  
A: ~0.7PB physical before EC; EC 1.2–1.5× → plan capacity explicitly.

**Q47: 100M clients poll every 30s?**  
A: ~3.3M QPS — need long-poll/push; not short poll.

**Q48: Deal-breakers?**  
A: Commit before blocks durable; path-only S3; silent LWW; notify with payloads; poll storms.

**Q49: Why Meta asks Drive?**  
A: Metadata consistency + sync + scale — similar to large graph/meta problems.

**Q50: 30m cut?**  
A: Skip deep CDC; nail chunk, commit, changelog cursor, conflict copy, NS shard.


### Appendix A — Commit pseudocode

```text
def commit(file_id, parent_rev, blocks, idem_key):
  if cached := idem.get(idem_key): return cached
  for h in blocks:
    assert block_store.exists(h)
  with txn:
    f = get_file(file_id)
    if f.current_rev != parent_rev: raise Conflict(f.current_rev)
    rev = insert_rev(file_id, parent_rev, blocks)
    f.current_rev = rev
    cl.append(namespace, mut(op=update, file_id, rev))
  notify(namespace)
  return idem.store(idem_key, rev)
```

### Appendix B — Client sync loop

```text
while running:
  event = wait(notify, timeout)
  mutations, next_c = api.sync(cursor)
  if reset: full_resync(); continue
  for m in mutations:
    ensure_blocks(m.blocks)
    local_db.apply(m)
  cursor = next_c
```

### Appendix C — Conflict copy

```text
on_conflict(local_file, server_rev):
  download(server_rev) → becomes current cloud/local base
  if local_dirty:
    upload_as_new_file(name + " (conflicted copy)")
```

### Appendix D — Progressive scale table

| Scale | Meta | Blocks | Sync | Notify |
|-------|------|--------|------|--------|
| Baseline | Single cluster | Object store | Changelog | Long-poll |
| 10× | Read replicas | Parallel PUT | Compact | Push |
| 100× | Cells | EC cold | Snapshots | Sharded watch |
| 1,000× | Geo cells | Edge upload | CDC | Hierarch watches |

### Appendix E — BOTE worked example

```text
10B files × 500 B meta = 5 TB raw meta
10B × 1 MB = 10 PB logical data
Ingress 10 GB/s / 4 MB = 2500 chunk/s avg; provision peak ~10×
5M watchers long-poll 30s timeout → far fewer than 167K tight polls
```

### Appendix F — Capability token for blocks

```text
meta issues token {hash, user, exp, sig}
block service verifies sig + exp before GET
```

### Appendix G — Changelog compaction

```text
retain last 30d detailed mutations
beyond: directory snapshots / hash trees for resync
coalesce noisy paths where safe
```

### Appendix H — NFR card

```text
Commit p99 < 200ms meta
Durable multi-AZ before ACK
CAS parent_rev
Notify wake seconds-level
Conflict copy > silent loss
AuthZ on block GET
```

### Appendix I — Deal-breaker checklist

1. Whole-file reupload only  
2. Silent LWW without history  
3. Push notify as SoT  
4. S3 path = only namespace  
5. Hash-as-capability  
6. Busy poll every 1s at scale  
7. Promise POSIX flock over WAN  

### Appendix J — Rename storm

```text
client renames 10k files (bad tool)
changelog coalesce / rate limit
notify once per cursor bump batch
```

### Appendix K — Comparison: object store vs drive

| Property | Object store | Drive sync |
|----------|--------------|------------|
| API | PUT/GET key | Namespace+sync |
| Rename | Cheap key? / copy | Meta txn |
| Conflicts | Optional etag | First-class |
| Clients | App-specific | Sync engine |
| Dedup | Optional | Common |

### Appendix L — Quota

```text
reserve on chunk put or on commit
settle on commit success
reject when over soft/hard limits
```

### Appendix M — Common pushbacks

| Pushback | Response |
|----------|----------|
| “It’s just S3” | Sync/conflicts/changelog |
| “Use Git” | Not end-user UX; still similar snapshots |
| “CRDT everything” | Overkill for binary files MVP |
| “Global lock files” | Won’t scale WAN |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| Block/chunk | Immutable content unit by hash |
| Revision | File version = ordered block list |
| Namespace | Sync root (user/shared) |
| Cursor | Changelog position |
| Conflict copy | Preserved divergent edit |
| CAS | Compare-and-swap parent rev |

### Appendix O — 30m interview checklist

1. Clarify sync, conflicts, sharing, chunking.  
2. BOTE: meta vs PB data vs notify QPS.  
3. Draw client → meta/block → changelog → notify.  
4. Deep dive CAS + conflict copy + authz dedup.  
5. Walk 10×/100×/1,000×.  
6. Deal-breakers.

### Appendix P — Selective sync

```text
client marks folders online-only
meta still syncs; blocks fetched on open
saves disk; same cursors
```

### Appendix Q — Shared folder shard

```text
shared folder = its own namespace_id
members watch that namespace
hot folder: read replicas + notify sharding
```

### Appendix R — Virus scan hook

```text
on_commit → enqueue scan
status: pending|clean|infected
policy gates download for enterprise
```

### Appendix S — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Chunk+commit, changelog, GC TTL |
| 100× | Cells, notify service, EC/cold |
| 1,000× | Edge upload, CDC, hierarchical watch |

### Appendix T — Idempotency

```text
chunk put: content-hash natural idempotent
commit: idempotency_key → same rev
sync apply: mut_id idempotent
```

### Appendix U — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Read-after-write own commit? | Yes in home meta |
| Cross-device appearance? | Via changelog; seconds |
| Block without commit? | Invisible to others |
| Concurrent editors? | CAS → conflict policy |

### Appendix V — Meta E5 closing

> “I’d split metadata and content-addressed blocks, commit revisions with parent_rev CAS, sync devices through namespaced changelogs with notify as a wake-up, resolve races with conflict copies, and scale via namespace cells—keeping dedup from becoming an authorization bug.”

---


## Appendix W — Anti-patterns (deepened)

| Anti-pattern | Why | Instead |
|--------------|-----|---------|
| Commit before blocks safe | Data loss | Receipts then meta txn |
| S3 key = full path only | Rename/list pain | Namespace DB |
| Silent last-write-wins | User data loss | Conflict copies |
| Push file bodies on notify | Amplification | Cursor pull |
| Cross-tenant hash oracle | Security | AuthZ/E2EE |
| Short poll all clients | Meltdown | Long-poll/push |
| GC without grace | Rare loss | Refcount+delay |

## Appendix X — 90s pitch

> “Chunked immutable blocks, atomic namespace commits with rev/changelog, cursor sync, conflict copies, ACL on access. Scale meta by namespace_id and bytes on object store; control notify amplification. Deal-breaker: committed files with missing blocks.”


*End of Dropbox / Google Drive system design (Meta E5 2024).*
