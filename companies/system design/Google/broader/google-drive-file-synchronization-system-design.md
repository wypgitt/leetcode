# System Design: Google Drive / File Synchronization

> **Focus areas:** Delta sync · Conflicts · Versioning · Offline · Sharing ACLs · Block-level / chunk sync · Notifications  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (sync QPS vs bytes, chunk indexes), split metadata/control vs block data planes, deal-breakers for “upload whole multi-GB file on every save”  
> **Interview theme:** Google L5+ sync system — DB choice for metadata vs chunk store, partitioning by `owner_id`/`file_id`, ambiguity over Google internals (no Chubby trivia required)

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

Goal: **bound the product**—a **Google Drive–class** file sync & share system: clients keep a local folder consistent with the cloud, using **delta/block sync**, handling **offline edits** and **conflicts**, retaining **versions**, and enforcing **sharing ACLs**.

### 1.0 What this is / is not

| Dimension | **Drive / file sync (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Sync files/folders + share securely | Full Docs OT/CRDT collaborative editor |
| Success | Durable, consistent-enough sync, correct ACL | Perfect byte-identical sync under all partitions without conflict UX |
| Data plane | Chunk/block store + metadata | App server as sole byte pipe |
| Write | Delta uploads; resumable | Always full-file rewrite |
| Collab | File-level sharing; optional locks | Google Docs real-time (sibling) |
| Offline | Local queue + conflict resolve | Assume always online |

**Scope statement:** Design Google Drive–style sync: metadata namespace, block-level delta sync, versioning, offline/conflicts, sharing ACLs, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What syncs? | Files + folders; not OS special files | Namespace tree |
| F2 | Clients? | Desktop sync + mobile + web | Same APIs; different UX |
| F3 | Delta sync? | Yes — don’t reupload whole file | Content-defined or fixed chunks |
| F4 | Conflicts? | Keep both / rename; optional last-writer | Conflict copies; vector clocks/versions |
| F5 | Versions? | History for N days / revisions | Immutable version chain |
| F6 | Sharing? | User/group/link; roles reader/writer/owner | ACL evaluation; capabilities |
| F7 | Offline? | Edit offline; sync later | Local journal |
| F8 | Notifications? | Near-real-time updates to other devices | Push / long poll / watch |
| F9 | Dedup? | Chunks shared across files/versions | Content-addressed chunks |
| F10 | Large files? | Multi-GB OK | Resumable; parallel chunks |
| F11 | Selective sync? | Choose folders | Client policy |
| F12 | Docs native editors? | Out of MVP (hooks) | File placeholder + open-in-editor |

**MVP functional scope:**

1. Hierarchical **namespace** (folders/files) with metadata.  
2. **Upload/download** via **chunked**, resumable, content-addressed blocks.  
3. **Delta sync**: detect local changes; send only new chunks + metadata mutate.  
4. **Versioning** on each logical commit.  
5. **Sharing ACLs** (user, domain, link) with reader/writer.  
6. **Offline** local edits with later sync; **conflict copy** on concurrent writes.  
7. **Change notifications** so other clients pull deltas.  
8. Trash/restore; quota.  
9. Web list/preview via CDN for downloadable blobs.

**Out of MVP:**

- Real-time Google Docs/Sheets OT/CRDT  
- Full OS FS driver edge cases (symlinks everywhere)  
- Enterprise DLP complete suite (hooks)  
- Cross-region active-active strong sync without conflicts  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability | No silent file loss | Multi-AZ object/chunk store |
| N2 | Metadata latency | Snappy browse | p99 < 100–200ms |
| N3 | Sync freshness | Near-real-time when online | Notify < 1–5s; catch-up bounded |
| N4 | Large file progress | Resumable reliable | Survive network drop |
| N5 | ACL correctness | No leaks | Strong metadata authz |
| N6 | Availability | High | Multi-AZ; degrade notify ≠ lose data |
| N7 | Consistency model | Per-file linear versions; tree eventual under partition | Explicit conflict UX |
| N8 | Scale | Billions files | Shard metadata; CDC chunks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User saves `deck.pptx` → client chunks → uploads new blocks → metadata version++ → other device notified → downloads deltas.  
2. Edit 1 GB VM image slightly → few new chunks only.  
3. Share folder with coworker writer → they upload → you receive changes.  
4. Offline edit on plane → later reconnect → commit or conflict copy.  
5. Restore version from history → new version pointing at old chunk set.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two writers same file offline | Conflict: `file (conflict).ext` + keep both versions |
| Rename vs edit race | Operational transform at metadata op level or conflict |
| Move folder cycles | Reject cycles; server authoritative tree rules |
| ACL revoke mid-download | Next chunk authz fail; stop |
| Hot shared folder | Metadata watch fanout; careful notify |
| Identical chunks many files | Dedup storage refcount |
| Clock skew | Server timestamp / logical version wins for ordering |
| Partial chunk upload | Not referenced by committed version until complete |
| Quota exceeded | Reject commit; client surfaces |
| Malware upload | Scan async; quarantine share |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 50M | 500M | — | global |
| Files | 50B | 500B | 5T | — |
| Avg file size | 500 KB | mixed | +large | — |
| Sync metadata ops/s | 100K | 1M | 10M | 100M |
| Chunk upload Gbps | 20 | 200 | 2K | cell fabric |
| Versions retained | 30–100 | policy | policy | — |
| Share edge QPS | 50K | 500K | 5M | — |
| Watch/notify QPS | 200K | 2M | 20M | push fabric |
| Chunk unique store | EB | multi-EB | — | — |

**What each jump forces:**

- **10×:** Chunk dedup store; metadata shards by owner; push notify.  
- **100×:** Regional cells; change-log cursors; ACL caching; hotspot folders.  
- **1,000×:** Namespace partitioning; tiered cold chunks; bloom filters for sync.

### 1.5 Etc. (Constraints & Assumptions)

- Native Docs collaboration is a **different consistency model**; Drive stores a file pointer / export.  
- Prefer **sync protocol clarity** (cursors, revisions) over vendor API names.  
- Block-level sync ≈ content-defined chunking (CDC) or fixed blocks — pick one and defend.

**Scope statement to repeat back:**

> Design a Drive-like sync service with a strongly authorized metadata namespace, content-addressed chunk storage for delta sync, version history, offline conflict copies, sharing ACLs, and push-driven catch-up—scaling by owner/file partitioning without re-uploading whole files on each edit.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Metadata ops** | create/rename/acl | ~100K/s | Distributed SQL |
| **Chunk writes** | new blocks | 20 Gbps | Object/chunk store |
| **Chunk reads** | sync down | higher | CDN/cache warm |
| **Notify** | watches | ~200K/s | Pub/sub push |
| **List/dir** | UI browse | cacheable | Metadata |
| **Version GC** | background | batch | Workers |

**Anti-pattern:** treating “sync QPS” as only HTTP uploads of whole files.

### 2.2 Delta savings math

```text
1 GB file, change 8 MB mid-file
Fixed 4 MB blocks: touch ~3–4 blocks → upload ~12–16 MB
CDC (content-defined): often closer to changed bytes + boundaries
Full file reupload: 1 GB — DEAL-BREAKER UX/cost for frequent saves
```

### 2.3 Chunk store cardinality

```text
50B files × avg 20 chunks = 1T chunk refs (not unique)
Unique chunks much less with dedup/versions
Index: chunk_hash -> blob locator + refcount
Metadata version: ordered list/DAG of chunk hashes + lengths
```

### 2.4 Metadata size

```text
50B files × 500 B metadata ≈ 25 PB — sharded; cold files tier pointers
Active working set << total; cache hot dirs
```

### 2.5 Notify amplification

```text
1 edit -> notify all watchers of file/folder ancestors
Hot folder with 10K watchers → fanout storm
Mitigate: collapse events; per-user cursors; subscribe to prefixes carefully
```

### 2.6 Conflict rate

```text
True concurrent writers rare for binary Office files vs Docs
Still must define semantics; conflict copies OK for MVP binary files
```

---

## 3. High-Level Design

### 3.1 API / sync protocol

| Op | Semantics |
|----|-----------|
| `listChanges(cursor)` | Metadata mutations since cursor |
| `getMetadata(id)` | File/folder node |
| `commit(path/id, base_version, chunk_list, attrs)` | Create new version if base matches |
| `beginUpload(chunk_hash, size)` / `putChunk` | Idempotent chunk put |
| `download(chunk_hash)` | Authenticated get |
| `share(id, principals, role)` | ACL mutate |
| `watch(prefix)` | Register push |
| `trash/restore` | Soft delete |

**Commit CAS:** client sends `base_version`; server accepts iff current==base else conflict.

### 3.2 Data model

| Entity | Key | Store | Notes |
|--------|-----|-------|-------|
| Node | `node_id` | SQL | type file/dir, parent, name, head_version |
| Version | `(node_id, ver)` | SQL | chunk manifest, size, author, ts |
| Chunk | `chunk_hash` | Chunk store | bytes immutable |
| ACL | `node_id` | SQL | inherited + explicit |
| ChangeLog | `(shard, seq)` | Log / SQL | sync cursor |
| ShareLink | `token_hash` | SQL | capability |
| Lock (optional) | `node_id` | Redis/SQL | soft lock UX |

### 3.3 Chunking — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Whole file | Simple | Terrible deltas | Tiny MVP |
| **Fixed-size blocks** | Simple align | Boundary shift waste (insert at front) | Acceptable MVP |
| **Content-defined chunking (CDC)** | Insert-resistant | CPU to chunk | **Strong pick** |
| rsync rolling checksum remote | Efficient | Chatty protocol | Alt design |
| Operational transform per byte | Collab | Wrong for binary Drive MVP | Docs |

**Chosen MVP:** CDC (e.g. Rabin-like) ~1–4 MB avg chunks; fall back fixed for encrypted blobs already chunked client-side.

### 3.4 Conflict strategy — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Last-writer-wins silent | Simple | Data loss |
| **Conflict copy** | Safe | Clutter |
| Locks | Prevents | Offline poor |
| CRDT/OT merge | Best UX text | Not general binaries |

**Chosen:** CAS on `base_version`; on failure create conflict copy (or return 409 for client rename). Soft locks optional UX.

### 3.5 ACL — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Per-request walk to root | Correct | Latency |
| **Materialized effective ACL + inherit** | Fast | Complex updates |
| Capability-only links | Simple share | Hard enterprise groups |
| Pure centralized AuthZ service | Clean | Hotspot |

**Chosen:** Explicit ACL entries + inheritance; cache effective authz; group expansion cached; link capabilities as additional grants.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Bytes vs meta | Split planes | Scale | Files in SQL BLOB |
| Delta | CDC chunks | Save bandwidth | Full file always |
| Versions | Immutable manifests | History/restore | Mutate in place |
| Conflict | CAS + conflict copy | Safety | Silent LWW data loss |
| Sync | Cursor changelog | Efficient catch-up | Rescan entire tree always |
| Notify | Push + cursor | Freshness | Poll every second all files |
| DB | SQL metadata + chunk object store | Roles clear | One KV for everything naïve |

---

## 4. Architecture Diagram

```text
 +-------------+     meta/commit      +------------------+
 | Sync Client | -------------------> | Metadata Service |
 | (desktop)   | <------------------- | + ACL + ChangeLog|
 +------+------+     notify/push      +--------+---------+
        |                                      |
        | put/get chunks                       | head manifests
        v                                      v
 +--------------+                     +------------------+
 | Chunk Store  | <--- dedup hash --- | Version Manifests|
 | (object)     |                     +------------------+
 +------+-------+
        |
        v
   CDN / byte cache (authorized downloads)

 Share Admin UI --> ACL mutate --> ChangeLog --> watchers
 GC Workers --> refcount chunks --> delete zero-ref
```

**Sync upload path:**

```text
local fs watcher -> file changed
  -> chunk file (CDC)
  -> for each new hash: PutChunk (idempotent)
  -> Commit(node, base_ver, hashes[], attrs)
  -> on success: update local shadow state
  -> on 409: fetch remote; conflict copy or merge policy
```

**Sync download path:**

```text
receive notify OR poll listChanges(cursor)
  -> apply metadata ops locally
  -> fetch missing chunks
  -> materialize file atomically (temp + rename)
```

**Share path:**

```text
share(folder, userB, writer)
  -> ACL write + changelog
  -> authz cache invalidate
  -> userB devices notified
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Committed version only references durable chunks** (all hashes present).  
2. **Chunks immutable**; GC only at refcount 0.  
3. **ACL checked** on commit, list, and each download grant.  
4. **CAS/version** prevents silent overwrite.  
5. **Changelog monotonic per shard** for cursors.  
6. **Atomic local replace** on client (write temp → rename).

#### 5.1.2 Commit protocol (server)

```text
Commit(node_id, base, manifest, idem_key):
  authorize writer
  verify all chunks exist
  tx:
    if node.head != base: abort CONFLICT
    ver = head+1
    write Version(ver, manifest)
    node.head = ver
    append ChangeLog
  enqueue scan/preview jobs
```

#### 5.1.3 Offline & journal

```text
offline:
  local journal of intents (edit/rename/delete)
online:
  replay in order
  each commit with base from last known
  conflicts -> conflict copies; continue
```

#### 5.1.4 Failure modes

| Failure | Mitigation |
|---------|------------|
| Client crash mid-chunk | Resume put by hash |
| Commit timeout unknown | Idempotency key / read head |
| Changelog loss | Multi-AZ log; rebuild from snapshots + versions |
| GC deletes live chunk | Refcount tx careful; generation guards |
| Notify drop | Clients periodically `listChanges` |

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Split brain LWW | CAS+conflict |
| 10× | Hot ACL group | Cache; flatten |
| 100× | Notify storm | Collapse; shard watches |
| 1,000× | Metadata hotspot dir | Dir partition / secondary journals |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| `owner_id` / namespace root | Metadata shard |
| `node_id` | File identity |
| `chunk_hash` | Chunk store locality |
| Changelog `(shard, seq)` | Sync cursors |
| Share domain | Enterprise tenancy |

**Team Drives / shared folders:** shard by `drive_id` not personal owner — important nuance.

#### 5.2.2 ChangeLog sync

```text
cursor = (shard, seq)
listChanges(cursor, limit):
  return ops where seq > cursor.seq
ops include: UPSERT_NODE, DELETE, ACL_CHANGE, MOVE
Clients store cursors per shard they care about
```

Avoid full tree checksum scans except repair.

#### 5.2.3 Chunk dedup & GC

```text
refcount[chunk]++ on version create referencing it
refcount-- on version GC
async GC deletes bytes at 0
careful: concurrent commit vs GC → use pending refs / generations
```

#### 5.2.4 Hotspot shared directories

- Collapse notifications (version watermark per folder).  
- Directory listing caches with ACL variants carefully (cache key includes authz epoch).  
- Limit extreme fanout shares.

#### 5.2.5 Block-level sync details

**CDC sketch:**

```text
rolling hash over window
when hash % target_size == magic: cut chunk
compute sha256(chunk) as id
manifest = [(hash, len)] in order
```

**Encrypted client-side files:** chunk after encryption carefully (or fixed frames) so deltas still work.

#### 5.2.6 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | CDC+dedup; push notify; metadata shards |
| →100× | Shared drive sharding; watch collapse; regional cells |
| →1,000× | Cold chunk tiers; bloom sync; namespace partitioning |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
chunk:
  target_avg_bytes: 2000000
  min: 512000
  max: 8000000
versions:
  retain_days: 30
  max_revisions: 100
conflict:
  strategy: copy
notify:
  collapse_ms: 200
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `commit_success / conflict_rate` | Sync health |
| `bytes_uploaded / bytes_logical_changed` | Delta efficiency |
| `chunk_dedup_ratio` | Savings |
| `changelog_lag` | Freshness |
| `notify_fanout` | Storms |
| `acl_deny_rate` | Abuse/bugs |
| `gc_debt` | Storage |

#### 5.3.3 Testing

- CDC insert-at-start delta size tests.  
- Concurrent commit → conflict copy.  
- ACL inheritance move across folders.  
- GC correctness under concurrency.  
- Cursor catch-up after week offline.

#### 5.3.4 Operability

- Manifest format v2 dual-read.  
- Repair job: rehash files, fix refcounts.  
- Canary chunk store migration.

---

## 6. Wrap-Up

### 6.1 What we designed

A **Drive-like** system: metadata namespace with **CAS versions**, **content-addressed chunks** for delta sync, **changelog cursors** + push notify, **ACL sharing**, offline journals with **conflict copies**, and GC’d immutable history—not whole-file reuploads and not silent last-writer-wins.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Full-file sync always | Deal-breaker |
| Silent LWW | Deal-breaker for durability UX |
| SQL BLOBs for file bytes | Deal-breaker |
| CDC vs fixed | CDC preferred |
| Docs OT | Out of scope sibling |
| Cursor vs rescan | Cursor |

### 6.3 30-second scale narrative

> Baseline: metadata SQL + chunk object store, CDC manifests, CAS commits, conflict copies, changelog cursors. 10× adds dedup GC and push. 100× shards shared drives and collapses notify fanout. 1,000× cold tiers and repair blooms—authz always on metadata before bytes.

### 6.4 Deal-breakers checklist

- Re-uploading entire multi-GB files on every save.  
- Storing file bytes in relational rows.  
- Silent overwrite on concurrent edit.  
- Sync by scanning full tree every minute as sole design.  
- CDN public URLs for private files without authz.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Desktop sync vs web-only?**  
A: Sync agents dominate complexity; include them.

**Q2: Binary Office vs Docs?**  
A: Binary = version replace; Docs = collab engine — separate.

**Q3: Selective sync?**  
A: Client policy; server still holds all.

**Q4: Unlimited versions?**  
A: Policy caps; enterprise legal holds.

**Q5: POSIX FS semantics?**  
A: Approximate; not full POSIX distributed FS claim.

### 7.2 Delta & chunking

**Q6: Why CDC beats fixed blocks on inserts?**  
A: Boundary shift: fixed invalidates all subsequent blocks; CDC localizes.

**Q7: Average chunk size tradeoff?**  
A: Small → more metadata/overhead; large → worse deltas.

**Q8: How to find which chunks missing?**  
A: Client has set of hashes; upload absent; server verifies.

**Q9: Compression?**  
A: Per-chunk; encrypted payloads may not compress.

**Q10: rsync algorithm instead?**  
A: Valid; more chattiness; discuss tradeoff.

### 7.3 Conflicts & consistency

**Q11: What does CAS mean here?**  
A: Commit succeeds only if `base_version` matches head.

**Q12: Conflict copy naming?**  
A: `name (conflicted copy from user ts).ext`.

**Q13: Folder rename vs child edit?**  
A: Metadata ops ordering; server serializes per namespace rules.

**Q14: Vector clocks?**  
A: Optional; version numbers per file often enough with CAS.

**Q15: Can we auto-merge text?**  
A: Phase 2; dangerous silently for code/binary.

### 7.4 Offline

**Q16: Local shadow state?**  
A: Client DB of node_id, ver, hashes, journal.

**Q17: Week offline?**  
A: Cursor catch-up; may download a lot; conflict likelihood ↑.

**Q18: Deletes offline?**  
A: Tombstones; if remote edited → conflict policy.

**Q19: Battery/network policies?**  
A: Metered sync pause; prioritize metadata.

### 7.5 ACL & sharing

**Q20: Inheritance?**  
A: Child inherits parent unless explicit; moves recompute.

**Q21: Group membership change?**  
A: AuthZ epoch bump; cache invalidate.

**Q22: Link sharing roles?**  
A: Anyone-with-link reader/writer; token = capability.

**Q23: Confused deputy / leaked link?**  
A: Revoke; short-lived hardened links; scan access anomalies.

**Q24: Download authz?**  
A: Signed URL bound to principal/session after ACL check.

### 7.6 Notifications

**Q25: Push vs long poll vs poll?**  
A: Push best; long poll OK; tight poll wasteful.

**Q26: Fanout storm?**  
A: Collapse events; watch watermarks; bounded subscribers.

**Q27: Exactly-once notify?**  
A: At-least-once + cursor idempotent apply.

### 7.7 Versioning & GC

**Q28: Restore old version?**  
A: New head pointing at old manifest (copy-on-restore).

**Q29: When delete chunks?**  
A: When no version references; respect legal hold.

**Q30: Dedup across users?**  
A: Possible via global chunk store; privacy OK if content-addressed without leaking existence via timing — subtle; often single-tenant stores per cell.

### 7.8 Data stores & partitioning

**Q31: Metadata DB?**  
A: Spanner-like / sharded MySQL with tx for CAS+ACL.

**Q32: Chunk store?**  
A: Object store keyed by hash; multi-AZ.

**Q33: Why not Git everywhere?**  
A: Git semantics help teaching; scale/ACL/notify still needed.

**Q34: Shared drive shard key?**  
A: `drive_id` — avoids owner hotspot wrongness.

**Q35: List large directory?**  
A: Paginated; secondary indexes; avoid huge dirs (product limits).

### 7.9 Estimation drills

**Q36: 1GB file change 1MB with 4MB fixed blocks?**  
A: ~2–3 blocks ≈ 8–12MB upload order.

**Q37: 100K commits/s changelog?**  
A: Shard logs; each shard tens of K/s.

**Q38: Notify 1K watchers × 1K edits/s?**  
A: 1M msgs/s — collapse required.

### 7.10 Alternatives & deal-breakers

**Q39: Only S3 versioning + rclone?**  
A: Missing ACL inheritance, notify, conflict UX, namespace.

**Q40: Distributed FS (NFS) over WAN?**  
A: Latency/semantics deal-breaker for consumer Drive.

**Q41: Operational transform for PPTX?**  
A: Wrong tool; binary opaque.

### 7.11 Interview craft

**Q42: How to open?**  
A: Delta sync, conflicts, ACL, offline, versions — split meta/bytes.

**Q43: What impresses L5+?**  
A: CDC+CAS, changelog cursors, ACL inheritance, notify collapse, shared drive sharding.

**Q44: Common mistake?**  
A: Designing only storage buckets; no sync protocol/conflicts.

---

### Appendix A — Manifest example

```text
Version 17 of node N:
  chunks: [h1:2MB, h2:2MB, h3:900KB]
  size: 4.9MB
  parent_version: 16
  author: u42
```

### Appendix B — Commit CAS pseudocode

```text
if node.head_version != base:
  return Conflict(remote=node.head)
for h in manifest:
  assert chunk_exists(h)
ver = node.head_version + 1
write_version(node, ver, manifest)
node.head_version = ver
log.append(Changed(node, ver))
```

### Appendix C — CDC cut

```text
for byte in file:
  rh = roll(rh, byte)
  if rh % MOD == 0 and len >= MIN: emit_chunk()
emit_final()
```

### Appendix D — listChanges

```text
Change {
  seq, node_id, op, parent_id?, name?, head_ver?, acl_epoch?
}
```

### Appendix E — Conflict copy

```text
on Conflict:
  new_name = f"{name} (conflicted copy {user} {ts}){ext}"
  create new node OR new version alongside policy
  preserve both manifests
```

### Appendix F — ACL check

```text
authorize(principal, node, action):
  for n in node -> root:
    if explicit deny: fail
    if explicit allow action: ok
  check link capability
  check group expands
  default deny
```

### Appendix G — Progressive scale table

| Scale | Meta | Chunks | Sync | Notify |
|-------|------|--------|------|--------|
| Baseline | SQL | Object hash | CDC+CAS | Long poll |
| 10× | Owner shards | Dedup GC | Cursors | Push |
| 100× | Drive shards | Regional | Collapse | Storm control |
| 1,000× | Cells | Cold tier | Bloom repair | Fabric |

### Appendix H — NFR card

```text
Durable chunks multi-AZ
CAS no silent overwrite
Delta << full file
Cursor catch-up
ACL on meta and bytes
Conflict copies not LWW
```

### Appendix I — Client atomic replace

```text
download to .tmp
verify size/hash
fsync
rename over target
update local DB
```

### Appendix J — Soft locks (optional)

```text
acquireLock(node, user, ttl)
advisory only; CAS still authoritative
UI shows "X is editing"
```

### Appendix K — Malware / DLP hooks

```text
on commit: async scan
if bad: mark quarantined; shares blocked
DLP rules enterprise Phase 2
```

### Appendix L — Common pushbacks

| Pushback | Response |
|----------|----------|
| “S3 versioning enough” | No namespace/ACL/sync protocol |
| “LWW is fine” | Data loss UX |
| “Poll tree hash every 30s” | Won’t scale; use changelog |

### Appendix M — Related systems

| System | Role |
|--------|------|
| Distributed SQL | Nodes/ACL/versions |
| Object store | Chunks |
| Pub/Sub | Notify |
| CDN | Download accel |
| Redis | Lock/authz cache |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| CDC | Content-defined chunking |
| Manifest | Ordered chunk list for a version |
| CAS | Compare-and-set on version |
| Cursor | Changelog position |
| Capability link | Token granting access |
| Refcount | Chunk liveness |

### Appendix O — Worked example

```text
User edits 200 MB video lightly
CDC → ~5 new chunks × 2 MB = 10 MB upload vs 200 MB
Commit CAS ok → changelog seq+1 → 3 devices notified
Each downloads ≤10 MB
```

### Appendix P — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Read-your-write same client? | Yes after commit ACK |
| Cross-device? | After notify/catch-up |
| Strong folder listing globally? | Eventual under replication lag |
| Bytes without meta grant? | Denied |

### Appendix Q — 30m interview checklist

1. Clarify delta/conflict/ACL/offline/version.  
2. Split metadata vs chunk planes; math.  
3. CDC + CAS + conflict copy.  
4. Changelog cursor sync.  
5. ACL inheritance + signed download.  
6. Scale jumps.  
7. Deal-breakers.

### Appendix R — Move / rename op

```text
tx:
  authorize
  check name collision
  update parent+name
  bump acl inheritance if needed
  changelog MOVE
```

### Appendix S — Quota

```text
usage += new_unique_chunk_bytes (dedup aware)
or sum logical file sizes (product choice)
enforce on commit
```

### Appendix T — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Dedup GC, push, shards |
| 100× | Shared drive shard, notify collapse |
| 1,000× | Cold chunks, cells, repair blooms |

### Appendix U — Web upload path

```text
Browser -> resumable chunk API (same store)
Less FS watcher; same Commit
```

### Appendix V — Comparison: Drive sync vs Photos backup

| | Drive | Photos |
|---|-------|--------|
| Namespace | User folders | Timeline library |
| Delta | Critical | Less (new files) |
| ML | Light | Core |
| Conflict | Core | Rare |

---

*End of Google Drive / File Synchronization system design.*
