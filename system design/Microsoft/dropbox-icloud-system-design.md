# System Design: Dropbox / iCloud (Cloud File Sync) — Microsoft Interview Practice

> **Focus areas:** Chunked upload · Metadata vs block storage · Client sync protocol · Conflict resolution · Change notifications · Dedup · Quotas · Multi-device  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic separating metadata QPS from block bytes; explicit sync cursors & conflicts; deal-breakers for “POSIX locking over WAN” and “store files as DB BLOBs”  
> **Interview theme:** Microsoft loop (team may ask domain problems) — cloud drive sync maps cleanly to OneDrive/SharePoint instincts: metadata consistency, chunking, notify-at-scale, enterprise sharing ACLs

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

Goal: **bound the product**—a Dropbox / iCloud Drive–class personal (and light shared) cloud filesystem: upload/download, sync folders across devices, share, version, detect remote changes, resolve conflicts. **Not** a raw object store alone and **not** a real-time collaborative document CRDT editor (mention as adjacent—Office/Loop territory).

### 1.0 What this is / is not

| Dimension | **Cloud Drive / Sync (this doc)** | Not this |
|-----------|-----------------------------------|----------|
| Primary job | Sync files/folders across devices + cloud | News feed / chat |
| Success | Correct eventual sync, few conflicts, fast delta | Perfect WAN POSIX |
| Metadata | Hierarchical namespace, versions, permissions | Only object key/value |
| Data plane | Chunked / content-addressed blocks | Whole-file only reupload always |
| Hard problem | Sync protocol + conflicts + notify | Training ML |
| Collab editing | File replace / versioning MVP | OT/CRDT docs (Office) |
| Microsoft lens | OneDrive-like; Entra auth hooks; compliance | Must rebuild NTFS |

**Scope statement:** Design Dropbox/iCloud-like chunked storage, metadata namespace, multi-device sync, conflict handling, sharing, and change notifications—at interview depth with progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Objects? | Files + folders; hierarchical paths | Namespace metadata tree |
| F2 | Upload? | Large files; resume; chunked | Block API + commit revision |
| F3 | Sync? | Desktop/mobile keep folder synced | Cursor / changelog protocol |
| F4 | Conflicts? | Concurrent edits → conflict copy / versions | Explicit policy |
| F5 | Sharing? | Link share + user ACLs | AuthZ on metadata |
| F6 | Versions? | History / restore | Immutable blocks + meta versions |
| F7 | Dedup? | Optional same-content once | Content-addressed chunks |
| F8 | Notifications? | Clients learn remote changes quickly | Long poll / push / WS |
| F9 | Search? | Filename MVP; content Phase 2 | Meta index |
| F10 | Quotas? | Per-user storage caps | Usage accounting |
| F11 | Offline? | Local edits; sync later | Client journal + conflict |
| F12 | Preview? | Thumbnails Phase 1.5 | Async processors |
| F13 | Selective sync? | Choose folders | Client policy |
| F14 | Photos (iCloud flavor)? | Burst photo library hooks Phase 1.5 | Same blocks; different UX |

**MVP functional scope:**

1. **Namespace:** create/rename/move/delete files and folders under user root (+ shared folders).  
2. **Chunked upload:** split → upload blocks → commit revision with block list.  
3. **Download / hydrate:** fetch blocks by id/hash; reconstruct.  
4. **Sync protocol:** cursor; pull changelog of metadata mutations.  
5. **Conflict policy:** diverging revisions from same parent → conflict copy (Dropbox-style) **or** version history last-writer with keep-both — pick one and state it.  
6. **Sharing:** user ACLs + link tokens.  
7. **Notifications:** wake clients on watched roots.  
8. **Quotas & auth**; basic version restore.

**Out of MVP:**

- Google Docs / Office real-time coauthoring (CRDT/OT)  
- Full-text content search across all bytes  
- Arbitrary POSIX `flock` over WAN  
- Dual-active strongly consistent multi-region metadata writers  
- E2E encrypted vault deep dive (can mention)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Metadata op latency | Snappy | p99 < 100–200ms |
| N2 | Upload throughput | Saturate user link | Parallel chunks; resume |
| N3 | Durability | No silent loss after commit ACK | Multi-AZ blocks + meta |
| N4 | Sync freshness | Remote edits appear soon | Notify < few seconds typical |
| N5 | Consistency | Per-file linear revisions; atomic namespace ops | CAS on parent revision |
| N6 | Availability | High | 99.9%+; degrade previews first |
| N7 | Dedup safety | No cross-tenant leak via hash | AuthZ always on meta |
| N8 | Scale | Billions of files | Metadata sharded; blocks object store |
| N9 | Security | Sharing must not leak | Capability checks every download |
| N10 | Maintainability | Clear planes | Meta / Block / Notify / Client |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Alice uploads `video.mp4` desktop → chunks → commit rev1 → phone notified → downloads deltas.  
2. Rename folder → metadata mutation → other devices rename without re-download.  
3. Bob & Alice edit offline → sync → **conflict copy** created; both preserved.  
4. Share folder with Carol → ACL checked on list/download.  
5. Restore prior version → new revision pointing at old block list.  
6. Identical file by two users → blocks deduped; separate inodes.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Commit with unknown parent rev | 409 → rebase / conflict copy |
| Chunk upload fails mid-way | Resume missing chunks; commit only when complete |
| Orphan chunks | GC after TTL if unreferenced |
| Move folder cycles | Reject; transactional move |
| Permission revoked mid-download | AuthZ fail subsequent blocks |
| Hash confirmation attack | Don’t reveal cross-tenant “hash exists” |
| Notify storm (huge folder) | Compact changelog; coalesce |
| Clock skew | Server time + logical rev ids |
| Partial local apply | Client journal; idempotent mutation ids |
| Quota exceed mid-commit | Reject commit; keep uploaded chunks temporary |
| Shared folder “celebrity” fanout | Cap watchers; hierarchical notify |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 10M | 100M | 1B | multi-B |
| Files (namespace entries) | 10B | 100B | 1T | multi-T |
| Avg file size | 1 MB | 1 MB | 1–2 MB | mixed |
| Chunk size | 4 MB | 4 MB | 1–4 MB adaptive | adaptive |
| Peak metadata QPS | 50K | 500K | 5M | 50M |
| Peak chunk put QPS | 20K | 200K | 2M | 20M |
| Peak ingress GB/s | 10 | 100 | 1K | 10K |
| Sync notify watchers | 5M | 50M | 500M | huge |
| Shared folder members | small | skewed | celebrity folders | caps |
| Versions retained | policy 30d / N | tiered | cold | cold |

**What each jump forces:**

- **10×:** Split metadata DB vs block store; chunked upload; changelog cursors.  
- **100×:** Metadata cells by namespace; notify fanout service; block EC/cold tier; GC fleets.  
- **1,000×:** Hierarchical notify; watch compaction; edge upload; isolate hot shared folders.

### 1.5 Etc. (Constraints & Assumptions)

- Clients are **smart** (desktop agent / mobile) with local DB — sync protocol is first-class.  
- **Blocks are immutable**; updates create new revisions.  
- Microsoft framing: think OneDrive/SharePoint metadata + Azure Blob-like bytes; Entra ID authz hooks.  
- Previews/virus scan = async pipeline.  
- Strong consistency **per namespace partition**; not global linearizability across all users.

**Scope statement to repeat back:**

> Design a Dropbox/iCloud-class system: chunked content-addressed (or chunk-id) storage, hierarchical metadata with revision CAS, multi-device sync via changelogs and notifications, explicit conflict copies, sharing ACLs, and progressive scale—separating metadata QPS from block bandwidth, without pretending we offer WAN POSIX locks.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split planes (critical)

| Plane | What | Baseline peak | Notes |
|-------|------|---------------|-------|
| Metadata | rename/commit/list | 50K QPS | Small payloads |
| Block put | chunk uploads | 20K QPS / 10 GB/s | Huge bytes |
| Block get | downloads | higher | CDN/cache |
| Notify | wake devices | millions watchers | Coalesce |
| GC / scan | background | steady | Separate |

**Anti-pattern:** sizing API servers for terabit uploads.

### 2.2 Chunk math

```text
Avg file 1 MB; chunk 4 MB → many files = 1 chunk
Large 100 MB file → 25 chunks of 4 MB
Commit stores ordered list of chunk ids/hashes

Dedup ratio (consumer): maybe 1.1–1.5× effective; enterprises higher
Never rely on dedup for capacity planning promises
```

### 2.3 Metadata size

```text
10B files × ~200–500 B metadata ≈ 2–5 PB logical meta before indexes
→ must shard; cold namespaces; careful indexes
Per-user namespace often millions of files (photos) — photo libraries dominate iCloud flavor
```

### 2.4 Changelog / cursor volume

```text
Assume 100 metadata mutations / active user / day
10M users × 10% DAU = 1M DAU × 100 = 100M mutations/day
≈ 1K/s avg; peak 10× → ~10K/s changelog writes — fine if partitioned

Notify wakeups can amplify if naïve push per watcher per mutation
```

### 2.5 Block storage growth

```text
Ingress 10 GB/s peak ≠ sustained
Sustained: 10M users × 50 MB new/month ≈ 500 TB/month ≈ ~200 MB/s average — order check
Photos heavy users dominate tails
Replication/EC 1.2–2× overhead
```

### 2.6 Client sync bandwidth savings

```text
Without chunking: edit 10 B in 100 MB doc → reupload 100 MB
With chunking + rolling hash (rsync-like): maybe 1 chunk 4 MB — still imperfect
Block-level dedup + sync engine critical for UX
```

### 2.7 Shared folder notify amplification

```text
Folder with 50K members, 1 save/sec → 50K notifies/sec from one folder
→ DEAL-BREAKER if naïve
→ hierarchical notify, digests, client pull changelog by cursor
```

### 2.8 Cache footprints

```text
Hot metadata inode cache in Redis for active users
Block CDN for popular shared content
Session auth tokens
```

### 2.9 Amplification table

| Naive | Amp | Fix |
|-------|-----|-----|
| Whole-file reupload | × file size | Chunks |
| Push full file to all devices | × devices × size | Notify + delta pull |
| Notify each member per save | × members | Coalesce / digest |
| Metadata in same DB as blocks | ops death | Split planes |
| Cross-region sync write-anywhere | conflicts galore | Home volume / cell |

### 2.10 Progressive scale

| Concern | Baseline | 10× | 100× | 1,000× |
|---------|----------|-----|------|--------|
| Meta DB | sharded SQL/NoSQL | cells | geo home | hierarchical |
| Blocks | object store multi-AZ | multi-region | EC/cold | edge cache |
| Notify | Redis pubsub | service | tree fanout | watch compact |
| Dedup | optional per user | cluster | global careful | risk manage |

---

## 3. High-Level Design

### 3.1 UX / client surfaces

```text
Desktop sync agent                     Mobile
+---------------------------+          +------------------+
| /Users/a/Dropbox          |          | Files            |
|   Projects/               |          | Camera Upload    |
|   photo.jpg  ✓            |          | Offline ★        |
|   essay.docx  (syncing)   |          | Shared           |
| Conflicts: essay (conflict)|         +------------------+
+---------------------------+
```

Client local DB: inode cache, cursor, journal of pending ops, chunk temp store.

### 3.2 Domain model

```text
Account / User
  └── Root Namespace (volume)
        ├── Node (file | folder)
        │     id, parent_id, name, type
        │     rev (file), child_stamp (folder)
        │     acl_id
        └── FileRevision
              rev_id, parent_rev, block_list[], size, mtime, writer_device

Block / Chunk
  chunk_id or content_hash → object bytes immutable

Changelog / Journal
  namespace_id, mutation_id, op, cursor

Share / Link
  capability token → node + permission
```

### 3.3 Conflict policy (state explicitly)

**Chosen default (Dropbox-style):**

```text
If commit.parent_rev != server.head_rev:
  reject OR auto-create conflicted copy
  "essay (Alice's conflicted copy 2026-08-06).docx"
Both revisions retained; user merges manually
```

**Alternative (iCloud-ish / last writer + versions):** keep version history; present conflict UI differently. Either OK if clear.

**Deal-breaker:** silent overwrite without version history.

### 3.4 API shape

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/namespaces/{id}/nodes` | mkdir / create file placeholder |
| POST | `/v1/upload_session/start` | Begin chunked upload |
| POST | `/v1/upload_session/append` | Upload chunk (or signed direct PUT) |
| POST | `/v1/upload_session/finish` | Commit revision (CAS parent) |
| GET | `/v1/files/{node_id}/download` | Get block list + signed URLs |
| GET | `/v1/changelog?cursor=` | Sync pull |
| POST | `/v1/nodes/{id}/move` | Rename/move |
| DELETE | `/v1/nodes/{id}` | Delete (tombstone) |
| POST | `/v1/shares` | Create share |
| GET | `/v1/notify` longpoll / WS | Wake on changes |

**Prefer direct-to-blob signed uploads** for chunk bytes (same lesson as Instagram media).

### 3.5 Architecture options

| Option | Idea | Verdict |
|--------|------|---------|
| **A. Files as SQL BLOBs** | Simple | Deal-breaker at scale |
| **B. Object store only (S3 keys = paths)** | Simple | Weak sync/rename/version semantics |
| **C. Metadata DB + chunk object store + sync log (chosen)** | Industry standard | **Choose** |
| **D. POSIX distributed FS (NFSv4/WAN)** | Familiar API | Wrong product constraints |

### 3.6 Component architecture

```text
Sync clients
    |  HTTPS + notifications
    v
API / Metadata Service  -----> Metadata DB (namespaces, revs, ACLs)
    |                   -----> Changelog store
    |
    +--> signed URLs --> Block Object Store (multi-AZ)
    |
    +--> Notify Service (longpoll/WS/push)
    |
    +--> Async: antivirus, thumbnails, index, GC
```

### 3.7 Chunked upload + commit (heart)

```text
1) Client computes chunks (fixed 4MB or content-defined chunking)
2) For each chunk: HEAD/exists? if not, PUT to signed URL
3) finish(commit):
     authz + quota check
     verify all chunk_ids present
     CAS: if node.head_rev == parent_rev (or create):
        write new revision with block_list
        append changelog mutation
        update usage
     else: 409 conflict
4) ACK commit → durable metadata; blocks already durable
5) Notify watchers of namespace
```

**Content-defined chunking (CDC):** better for inserts in middle of large files; more CPU on client. Mention as optimization.

### 3.8 Sync protocol

```text
Client stores cursor C
Loop:
  mutations, next = GET /changelog?cursor=C&limit=...
  apply mutations locally (idempotent by mutation_id)
  C = next
  wait notify(C) or poll
```

**Mutation examples:** `NODE_UPSERT`, `NODE_DELETE`, `NODE_MOVE`, `ACL_CHANGE`.

**Offline journal:** client applies local ops optimistically; on connect, replay commits; resolve conflicts.

### 3.9 Dedup & security

| Mode | Behavior | Risk |
|------|----------|------|
| Per-user dedup | Hash index within account | Safe |
| Global dedup | Same hash one copy multi-tenant | Side channel if naïve exists API |

**Safe pattern:** server stores by hash but **existence check** only returns true for chunks you are allowed to reference; or always accept upload and demux in backend.

### 3.10 Sharing & AuthZ

```text
can_read(user, node):
  walk ACLs on node + ancestors (cached)
  or valid link capability

Download path always checks AuthZ before issuing block signed URLs
```

Enterprise Microsoft flavor: Entra groups, tenant boundaries, DLP hooks (mention).

### 3.11 Consistency model

| Operation | Guarantee |
|-----------|-----------|
| Commit revision | Linear per file node via CAS |
| Rename/move | Atomic in metadata partition |
| Cross-folder move across cells | Rare; coordinated txn or reject |
| Block put | Durable before commit references |
| Sync across devices | Eventual; causal via changelog order per namespace |

---

## 4. Architecture Diagram

### 4.1 Upload + sync

```text
Device A                         Cloud                         Device B
  |                                |                              |
  |--PUT chunks------------------>| Block Store                   |
  |--commit(parent_rev)---------->| Meta DB + Changelog           |
  |<-- ACK rev' -------------------|                              |
  |                                |--notify---------------------->|
  |                                |                              |--GET changelog
  |                                |<------- pull mutations -------|
  |                                |--signed GET chunks---------->|
```

### 4.2 Conflict

```text
head=rev1
Device A commits parent=rev1 → rev2
Device B commits parent=rev1 → 409
Server/client creates conflicted copy node with rev2b OR returns conflict for client to upload as new node
```

### 4.3 Metadata cell

```text
Global Directory: user/namespace → home cell
Cell:
  Meta DB primary
  Changelog
  Notify gateway
  Quota accounting
Block store: global/multi-region object storage with locality hints
```

---

## 5. Design Deep Dive

### 5.1 Reliability

| Failure | Mitigation |
|---------|------------|
| Commit succeeds, notify lost | Client longpoll timeout → changelog pull still works |
| Block put lost before commit | Commit fails chunk check; retry |
| Commit crash after write | Idempotency on commit token; changelog unique mutation_id |
| Meta primary failover | Multi-AZ; careful fencing |
| GC deletes live chunk | Refcount / mark-sweep with generation; never GC freshly uploaded unreferenced until TTL |
| Client applies partial changelog | Durable local cursor only after full apply batch |

**Durability rule:** never ACK commit until revision + changelog appended durably. Blocks must be durable before being referenceable.

**Degradation order:**

1. Disable thumbnails / content search  
2. Stretch notify (clients poll)  
3. Read-only metadata if write path unhealthy  
4. Never corrupt namespace CAS invariants  

### 5.2 Scalability

**Metadata sharding:** by `namespace_id` / `user_id`. Shared folders: namespace with its own id; members reference it.

**Hot shared folder:**

- Changelog compaction / snapshots  
- Notify digests (“something changed, pull”)  
- Rate-limit path listing  
- Cap extreme member counts or tier product  

**Block plane:** object store horizontally scales; use parallel put/get; CDN for public link downloads.

**GC fleet:** scan unreferenced chunks carefully; account for in-flight uploads.

### 5.3 Maintainability

| Service | Owns |
|---------|------|
| Metadata | Namespace, revs, ACL |
| Block | Upload sessions, object durability |
| Changelog | Cursors, compaction |
| Notify | Wakeups |
| Quota | Usage ledger |
| Processors | AV, preview, index |

**Microsoft interview plus:** clear API versioning for sync clients (old desktop agents live forever)—**backward-compatible changelog ops**.

**Observability:**

| Metric | Why |
|--------|-----|
| Commit conflict rate | UX / bug |
| Changelog lag | Sync freshness |
| Orphan chunk bytes | Cost |
| Notify coalesce ratio | Storm control |
| Quota reject rate | Product |
| p99 commit | Meta health |

### 5.4 Sync cursor details

```text
cursor = (namespace_id, monotonic_mutation_seq)  # or opaque token
Gaps not allowed for a namespace sequencer
Compact: snapshot inode state at seq S; clients can reset to snapshot + catchup
```

### 5.5 Move / rename correctness

```text
move(node, new_parent, new_name):
  authz on old+new
  reject if would create cycle
  txn update parent_id/name
  changelog two logical ops or one MOVE op
```

Children paths are computed, not stored fully (or stored denormalized carefully). Full path materialization can be cached.

### 5.6 iCloud-specific notes (photos)

- Camera upload as special folder with burst create  
- Device optimization: thumbnails local, full hydrate on demand (Files On-Demand / placeholder)  
- Placeholder files with attributes — client OS integration  

Same backend planes; different client policy.

### 5.7 Security

- Signed URLs short TTL, scoped to chunk  
- Link shares rotatable / password / expiry  
- Malware scanning async; quarantine  
- Ransomware heuristics: mass delete/modify rate alerts  
- Enterprise: eDiscovery export hooks  

### 5.8 Multi-region

**Home cell for metadata namespace** (single writer). Block store multi-region replication async or EC. Clients may upload to nearest region bucket then metadata references; or write region follows home.

**Avoid:** active-active metadata writers without CRDTs — conflict explosion.

---

## 6. Wrap-Up

### 6.1 Designed

Dropbox/iCloud-like sync: chunked immutable blocks, metadata revisions with CAS, changelog cursors, notify wakeups, conflict copies, sharing ACLs, quotas, progressive cells.

### 6.2 Trade-offs

| Decision | Chose | Rejected | Why |
|----------|-------|----------|-----|
| Storage | Meta + blocks | DB BLOBs | Scale |
| Conflicts | Conflict copy / versions | Silent LWW | Data safety |
| Sync | Cursor changelog | Always full scan | Efficiency |
| Dedup | Careful / per-account first | Naïve global exists | Security |
| Region | Home meta cell | Dual-active meta | Consistency |

### 6.3 Risks

- Changelog growth  
- GC correctness  
- Shared folder notify storms  
- Old clients  
- Dedup legal/security  

### 6.4 60-second pitch

> “I’d split metadata from block bytes. Clients upload immutable chunks via signed URLs, then CAS-commit a new file revision into a per-namespace metadata store and append a changelog. Other devices wake on notify and pull mutations by cursor. Concurrent commits from the same parent become conflict copies. Sharing is ACL on metadata; downloads re-check authz. Scale metadata by namespace cells; object store handles bytes; never promise WAN POSIX locks.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Chunking

**Q1. Fixed vs content-defined chunks?**  
Fixed: simple. CDC: better delta for edits; CPU cost; chunk size targets ~1–4MB average.

**Q2. Why immutable blocks?**  
Simplifies caching, dedup, versioning; updates = new blocks + new rev.

**Q3. How big should chunks be?**  
Too small: metadata amp + request overhead. Too big: worse deltas + retry cost. ~4MB common interview answer.

**Q4. Resume uploads?**  
Track uploaded chunk set per session; finish only when complete.

### 7.2 Consistency & conflicts

**Q5. CAS parent revision — explain.**  
Optimistic concurrency: commit carries `parent_rev`; server accepts iff matches head.

**Q6. Folder conflicts?**  
Same-name create; merge policies; sometimes auto-rename.

**Q7. Is sync strongly consistent across devices?**  
No — eventual via changelog; causal order per namespace.

**Q8. Can we use vector clocks?**  
Possible for richer conflicts; usually per-node linear revs suffice.

### 7.3 Notify & fanout

**Q9. Long poll vs WebSocket vs push?**  
All OK; mobile prefers push wake + pull changelog. Desktop longpoll/WS.

**Q10. Celebrity shared folder?**  
Digest notifies; clients pull; membership caps; hierarchical watches on subtrees.

**Q11. Exactly-once notify?**  
At-least-once wake; changelog idempotent apply.

### 7.4 Dedup & GC

**Q12. Cross-user dedup risks?**  
Existence oracle / timing attacks; legal custody; prefer careful designs.

**Q13. GC algorithm?**  
Refcounts with careful upload races OR mark-sweep generations; grace TTL for pending sessions.

**Q14. Encryption vs dedup?**  
Client-side E2E encrypt kills global dedup; per-user OK.

### 7.5 Geo / Microsoft

**Q15. OneDrive / SharePoint mapping?**  
Metadata + Azure Blob; Entra auth; WOPI for Office edit (out of MVP). SharePoint has richer list semantics.

**Q16. Data residency?**  
Pin namespace home region; block store residency policies.

**Q17. Files On-Demand?**  
Placeholders locally; hydrate on open; attribute cloud state.

**Q18. Ransomware recovery?**  
Version history + mass-change detection + restore workflow.

### 7.6 Traps

| Trap | Answer |
|------|--------|
| Store files in MySQL BLOB | No |
| Path string as primary identity | Use node ids; paths derived |
| Global locks for sync | No |
| Search index as SoT | No |
| Skip conflict story | Instant fail in interview |

---

## 8. Appendices

### Appendix A — Glossary

| Term | Meaning |
|------|---------|
| Namespace / volume | Root sync domain |
| Node / inode | File or folder metadata entity |
| Revision | Immutable file version metadata |
| Chunk / block | Immutable data piece |
| Cursor | Changelog position |
| Conflict copy | Extra file preserving divergent edit |
| CAS | Compare-and-set on parent rev |
| Hydrate | Download blocks to materialize file |
| Placeholder | Local stub without full bytes |

### Appendix B — Schema sketch

```sql
nodes(
  namespace_id, node_id,
  parent_id, name, type,
  head_rev,  -- files
  deleted, acl_id,
  PRIMARY KEY (namespace_id, node_id),
  UNIQUE (namespace_id, parent_id, name) WHERE not deleted
)

revisions(
  namespace_id, node_id, rev_id,
  parent_rev, size, block_list_json,
  writer_id, created_at
)

changelog(
  namespace_id, seq PRIMARY KEY,
  mutation_id UNIQUE,
  op_type, payload_json, ts
)

chunks(
  chunk_id PRIMARY KEY,
  sha256, size, storage_key, refcount, created_at
)

shares(
  share_id, node_id, permission, token_hash, expires_at
)

usage(
  account_id, bytes_used, file_count
)
```

### Appendix C — Commit pseudocode

```text
function commit(node_id, parent_rev, blocks, commit_id):
  idempotent_return_if_seen(commit_id)
  assert all_chunks_exist(blocks)
  txn:
    node = read_for_update(node_id)
    if node.head_rev != parent_rev: raise Conflict
    rev = new_rev(parent_rev, blocks)
    node.head_rev = rev.id
    append_changelog(NODE_UPSERT, ...)
    update_quota(+delta)
  notify(namespace)
  return rev
```

### Appendix D — Changelog entry

```json
{
  "seq": 123456,
  "mutation_id": "m_99",
  "op": "NODE_UPSERT",
  "node_id": "n_1",
  "name": "essay.docx",
  "parent_id": "folder_2",
  "rev": "r_8",
  "size": 182233,
  "ts": "2026-08-06T01:00:00Z"
}
```

### Appendix E — Capacity cheatsheet

| Metric | Baseline order |
|--------|----------------|
| Users | 10M |
| Files | 10B |
| Meta QPS | 50K |
| Ingress peak | 10 GB/s |
| Chunk size | 4 MB |

### Appendix F — Interview checklist

- [ ] Split meta vs blocks  
- [ ] Chunked upload + CAS commit  
- [ ] Cursor sync  
- [ ] Conflict policy stated  
- [ ] Notify ≠ full file push  
- [ ] Sharing AuthZ on download  
- [ ] Quota  
- [ ] GC orphan chunks  
- [ ] Home cell for meta  
- [ ] Direct-to-storage uploads  

### Appendix G — Related prompts

- S3-like object storage  
- Distributed file system  
- Picture upload service  
- File sharing cloud storage (bank overlap)  

### Appendix H — CDC sketch

```text
Rolling hash (Rabin):
  emit cut when hash mod target == 0
  clamp min/max chunk size
  stable cuts under inserts
```

### Appendix I — Notify coalescing

```text
on_mutation(ns):
  dirty.add(ns)
flush_every_100ms:
  for ns in dirty:
    wake(watchers[ns])  # or send digest
```

### Appendix J — Quota accounting

```text
quota check at commit (size delta)
usage ledger eventual OK if bounded; reject path must be correct
trash retention still counts until purged (product policy)
```

### Appendix K — Progressive roadmap

| Phase | Add |
|-------|-----|
| MVP | Sync, chunk, conflict copy, share link |
| 1.5 | Previews, AV, selective sync, photos |
| 2 | Content search, E2E vault option |
| 3 | Enterprise DLP, eDiscovery |

### Appendix L — Why Microsoft asks this

OneDrive/SharePoint DNA: metadata consistency, large binary planes, sync clients, sharing, residency. Excellent probe of whether you confuse object storage with a sync product.

### Appendix M — Whiteboard order

1. Client ↔ Meta ↔ Block store  
2. Commit CAS  
3. Changelog cursor  
4. Conflict copy  
5. Scale cells + notify coalesce  

### Appendix N — Sample NFRs card

```text
Commit ACK durable meta+log
p99 meta < 200ms
Notify wake < 5s typical
Zero silent overwrite without version/conflict
```

### Appendix O — Device loss / reinstall

Client has no cursor → download snapshot of namespace listing + hydrate selective paths; expensive; rate-limit; offer progressive download.

### Appendix P — Comparison Dropbox vs iCloud vs OneDrive (talk track)

| Aspect | Dropbox | iCloud Drive | OneDrive |
|--------|---------|--------------|----------|
| Heritage | Sync pioneer | Apple ecosystem / photos | M365 / SharePoint |
| Conflicts | Conflicted copies | Versions / UX differs | Versions + Office lock hooks |
| Collab | Paper etc. | iWork | Office real-time (separate) |
| Interview | Classic sync | Placeholders + photos | Enterprise ACL / tenant |

Design here covers the shared core; customize flavor with interviewer.

### Appendix Q — Malware / AV pipeline

```text
on commit → enqueue ScanJob(rev)
if malicious → quarantine rev; notify owner; block download URLs
```

Don’t block commit ACK on slow AV if product allows eventual quarantine (state clearly).

### Appendix R — Common math slips

1. Ignoring photo-library file counts  
2. Mixing Gbps ingress into meta DB capacity  
3. Assuming dedup halves storage guaranteed  
4. Forgetting notify amplification on shared folders  
5. Infinite version retention cost  

---

*End of Dropbox / iCloud system-design prep doc (Microsoft interview practice).*
