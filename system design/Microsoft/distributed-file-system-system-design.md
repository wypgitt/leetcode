# System Design: Distributed File System (Files, Directories, Symlinks, Traversal)

> **Focus areas:** Namespace metadata · Inodes/dirents · Symbolic links · Path traversal · Consistency · Chunk/block data plane · Permissions · Cross-directory ops  
> **Style:** High-level design with progressive scale (10× → 100× → 1,000×); LLD class model is a **sibling** (`file-system-classes-lld-system-design.md`)  
> **Microsoft themes:** Azure Files / ADLS Gen2 concepts · Entra identity · regional Azure cells · SMB/NFS-ish semantics discussion · security & compliance

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

Goal: **bound the file-system product**—POSIX-ish namespace vs object-store hierarchy, symlink semantics, consistency for rename/move, and where metadata vs bytes live at each scale. This doc is **HLD**; if the interviewer wants coded classes (`File`, `Directory`, `Symlink`, traversal), switch to the LLD sibling and implement APIs.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Abstraction? | Hierarchical dirs, files, symlinks | Namespace service + data plane |
| F2 | Ops? | create/open/read/write/close, mkdir, unlink, rename, readdir, stat | Metadata RPCs + byte I/O |
| F3 | Symlinks? | Soft links; optional hard links Phase 2 | Store target string; traversal rules + loop detection |
| F4 | Paths? | Absolute `/a/b/c`; relative with cwd | Canonical resolve algorithm |
| F5 | Consistency? | Strong for metadata in a volume; read-after-write for data in session | Single-writer metadata shard / consensus |
| F6 | Permissions? | Owner/group/ACL; Entra identities for cloud | AuthZ on every metadata op |
| F7 | Size limits? | Files to TBs; dirs with millions of entries at extreme | Chunk files; dir sharding / hash dirs |
| F8 | Snapshots? | Nice-to-have | Copy-on-write metadata later |
| F9 | Sharing? | Multi-client mount | Leases/locks for cache coherence (simplified) |
| F10 | API style? | RPC/POSIX-like; REST for cloud control | Separate data path |
| F11 | Cross-volume move? | May be copy+delete | Document non-atomic cross-shard |
| F12 | Soft delete? | Trash optional | Tombstones + GC |

**MVP functional scope (lock with interviewer):**

1. Volume with hierarchical **directories** and **files**.  
2. **Symlinks** (soft) with loop-limited resolution.  
3. Path resolution / traversal with `.` and `..`.  
4. CRUD: create, read, write (chunked), delete, mkdir, rmdir (empty), rename same-volume.  
5. `stat` / `readdir` with pagination.  
6. Basic UNIX-like mode bits or ACL stub.  
7. Durable metadata + replicated data chunks.  
8. Clear error model: `ENOENT`, `EEXIST`, `ENOTDIR`, `ELOOP`, `ENOTEMPTY`, `EACCES`.

**Out of MVP (explicitly defer):**

- Full POSIX fcntl locking across continents  
- Hard links + all inode nlink edge cases (mention design)  
- Global distributed POSIX single-system image  
- Client page-cache coherency like AFS/SMB full fidelity  
- Encryption key hierarchy deep dive (point to Key Vault)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Metadata latency | Interactive | p50 < 5–10ms in-region; p99 < 50ms |
| N2 | Data throughput | Large sequential | Saturate NIC; 100s MB/s–GB/s per client |
| N3 | Durability | No lost acknowledged writes | Quorum/fenced replicas; RPO≈0 for ACK’d |
| N4 | Availability | Volume available across AZ | 99.9%+; degrade secondary reads carefully |
| N5 | Consistency | Linearizable metadata (or close) per volume shard | Consensus / single primary per shard |
| N6 | Scale | Billions of files at 1000× | Namespace sharding + chunk stores |
| N7 | Multi-region | DR first; active-active hard | Home region for volume |
| N8 | Security | AuthN/Z, encryption at rest | Entra + per-volume keys |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `mkdir /projects` → `create /projects/a.txt` → write chunks → `read` → `stat`.  
2. `symlink /projects/link → /projects/a.txt` → open via link → reads file.  
3. `rename /projects/a.txt → /projects/b.txt` atomic within shard.  
4. `readdir /projects` paginated.  
5. Delete file → chunks refcount→0 → async GC.  
6. Traverse `/a/./b/../b/c` → normalize to `/a/b/c`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Symlink loop `a→b→a` | Stop at MAXSYMLINKS (e.g. 40); `ELOOP` |
| Symlink to absolute vs relative | Resolve relative against link’s directory |
| `rmdir` non-empty | `ENOTEMPTY` |
| Rename over existing file | Atomic replace if same type policy allows |
| Rename dir into its descendant | Reject (`EINVAL`) — must detect |
| Concurrent create same name | One wins; other `EEXIST` |
| Write timeout after partial | Client retries with offset; idempotent chunk put |
| Metadata primary fail | Elect new primary; fence old |
| Dangling symlink | `stat` link OK; `open` follow → `ENOENT` |
| Huge directory | Paginate; shard dirents by hash |
| Path `..` above root | Stay at `/` |
| Permission denied mid-path | `EACCES` on first failing component |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Files | 100M | 1B | 10B | 100B |
| Directories | 10M | 100M | 1B | 10B |
| Avg file size | 1 MB | 1 MB | 2 MB | 2 MB |
| Active mounts / clients | 10K | 100K | 1M | 10M |
| Metadata QPS (peak) | 50K | 500K | 5M | 50M |
| Data write GB/s (cluster) | 10 | 100 | 1K | 10K |
| Symlinks | 5M | 50M | 500M | 5B |
| Volumes / tenants | 100 | 1K | 10K | 100K |
| Max dir entries (hot) | 100K | 1M | 10M | 100M |
| Replication factor | 3 | 3 | 3 | 3 (EC optional) |

**What each jump forces:**

- **10×:** Shard namespace by subtree or hash; separate metadata vs chunk servers; lease-based client cache.  
- **100×:** Hierarchical/partitioned namespace; directory shard maps; erasure coding for cold/large; volume cells.  
- **1,000×:** Many metadata rings; distributed transaction only within shard (or carefully); CDN-like read caches for cold data; hard multi-tenant isolation.

### 1.5 Etc. (Constraints & Assumptions)

- **HLD interview:** architecture, path resolution, consistency, scaling—not a full POSIX test suite.  
- **LLD sibling:** in-memory or local OOP model of nodes + traversal.  
- Volumes are the isolation unit (like Azure Files share / ADLS filesystem).  
- Block size / chunk size fixed (e.g. 4 MB) for MVP math.  
- Microsoft framing: compare briefly to Azure Blob (object) vs Azure Files (share) vs ADLS (hierarchical namespace on object).

**Scope statement:**

> Design a distributed file system HLD supporting files, directories, symbolic links, and correct path traversal—with durable chunk storage, strongly consistent per-shard metadata, rename safety, and progressive sharding from ~100M to ~100B files—while noting LLD class design is covered separately.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Metadata vs data split

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Lookup / walk components | 50K QPS | 50M QPS | Dominated by deep paths / cache misses |
| Create / unlink / rename | 5K QPS | 5M QPS | Harder; journaled |
| readdir | 2K QPS | 2M QPS | Can return large payloads |
| Chunk write QPS | 20K | 20M | 4 MB chunks → huge BW |
| Chunk read QPS | 50K | 50M | Cacheable |

**Critical:** Path walk of depth `d` can be `d` metadata lookups. Client and server **lookup caches** (with leases) are mandatory at 100×+.

### 2.2 Storage math

```text
Baseline: 100M files × 1 MB = 100 TB data
Inode/metadata ~256–512 B: 100M × 400 B ≈ 40 GB metadata
Dirents ~64 B: if 100M files each one dirent → ~6.4 GB (plus dirs)

1,000×: 100B files × 2 MB = 200e9 × 2e6 B = 400e15 B = **400 PB** data
Metadata: 100B × 400 B = 40e12 B = **40 TB** metadata (still significant; shard it)

Unit check: 100M × 1 MB = 100 × 10^12 B = **100 TB**, not PB.
```

### 2.3 Bandwidth

```text
Chunk 4 MB; write 10 GB/s cluster → 10e9/4e6 ≈ 2500 chunk writes/s baseline OK
1,000× 10 TB/s → need thousands of storage nodes + EC/replication pipelines
```

### 2.4 Path walk cost

```text
Avg path depth 5; cache hit rate 95% → 0.25 primary lookups / op effective
At 50M metadata ops/s with bad cache → melt; with 95% hit → ~2.5M backend lookups/s
```

### 2.5 Memory

```text
Metadata cache per client: thousands of dentries — MBs
Server metadata cache: GBs per shard for hot dirs
Lease table: clients × cached inodes — must bound
```

### 2.6 Critical bottlenecks

1. Hot directory (e.g. `/tmp` or mail spool)  
2. Deep path walks without cache  
3. Rename across metadata shards  
4. Small-file metadata amplification  
5. readdir storms on huge dirs  
6. Symlink storms / loops  
7. Chunk GC backlog after mass delete  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Volume → rooted namespace
Inode  → id, type (file|dir|symlink), attrs, times, ACL ref
Dir    → map name → inode_id (dirents)
File   → ordered chunk list / extent map → chunk_ids
Symlink→ target string (not canonicalized at create)
Chunk  → immutable or versioned blob bytes (replicated)
```

### 3.2 Options: namespace architecture

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Single metadata server | Simple | Scale/HA ceiling | >~10K QPS durable mutates |
| B. Subtree sharding (GFS/HDFS-ish evolution) | Locality for dirs | Rebalance pain; hot dirs | Cross-subtree rename common |
| C. Hash inode-id sharding | Even load | Path walk hops | Deep walks without cache |
| D. **Hybrid: shard by directory id + cached walks** | Practical | Complexity | Ignoring hot-dir special case |

**Chosen path:**

- **MVP:** One metadata primary + followers (Raft) per volume; chunk servers separate.  
- **10×–100×:** Shard metadata by `dir_inode_id` ranges / hash; path resolution uses recursive lookup with client dentry cache + leases.  
- **Data plane:** Chunk/block stores (like Azure Storage extent nodes) addressed by `chunk_id`.

### 3.3 Options: data plane

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Store file bytes inside metadata DB | Simple tiny files | Melts for large files | Files ≫ MB |
| B. Chunk servers + replication | Classic DFS | More ops | — |
| C. Put chunks in object store (Blob) | Ops leverage Azure | Latency/POSIX sync semantics | Hard POSIX fsync guarantees without WAL |
| D. Erasure coding | Storage efficiency | Rebuild cost | Hot tiny writes |

**Chosen:** Chunk servers (or Blob with block list) for file data; metadata keeps extent map. Small-file optimization: inline < threshold (e.g. 64 KB) in metadata log.

### 3.4 Path resolution & traversal

```text
resolve(path, cwd, follow_symlinks=True):
  if path.absolute: node = root else node = cwd
  components = split(path)
  symlinks_followed = 0
  i = 0
  while i < len(components):
    name = components[i]
    if name == '.' : i++; continue
    if name == '..': node = parent(node) or root; i++; continue
    child = lookup(node, name)  # ENOTDIR if node not dir
    if child is symlink and (follow or i < last):
      symlinks_followed += 1
      if symlinks_followed > MAX: raise ELOOP
      target = read_symlink(child)
      # splice target components; if target absolute, reset node=root
      continue  # do not i++
    node = child; i += 1
  return node
```

**Interview gold:** Show loop detection, `.`/`..`, last-component no-follow for `lstat`/`unlink`/`symlink` ops.

### 3.5 Rename & directory cycles

**Same-directory rename:** atomic dirent swap/replace under directory lock / single Raft op.

**Cross-directory rename:**

```text
lock order: sort(parent_a, parent_b) by inode_id to avoid deadlock
if moving directory: ensure dst is not descendant of src (ancestor walk / generation)
commit: remove dirent src + insert dirent dst + update parent pointers (+..)
```

**Cross-shard rename:** Two-phase commit or copy+delete. **Deal-breaker:** pretend atomic cross-shard without protocol.

### 3.6 Symlinks vs hard links

| Feature | Soft (symlink) | Hard link |
|---------|----------------|-----------|
| Store | Path string | Extra dirent to same inode |
| Cross-volume | OK (may dangle) | Usually no |
| Directories | Usually forbidden for hard | Soft allowed |
| nlink | N/A | Must track |
| Delete | Remove link | Free inode when nlink=0 |

MVP: soft links only; mention hard links need inode refcount + no dir hard links.

### 3.7 Consistency model

| Plane | Model |
|-------|-------|
| Metadata mutations | Linearizable via Raft primary per shard |
| Data chunk write | Quorum ACK; client then updates file version in metadata |
| Client cache | Lease/callback; on break, invalidate |

**Write path (simplified):**

```text
1) allocate chunk_ids / get write lease
2) write bytes to chunk replicas (quorum)
3) commit size/mtime/extent to metadata with file generation++
4) fsync semantics: ACK after 2+3 durable
```

### 3.8 Permissions & Microsoft identity

- Mount authenticates via Entra OAuth / Kerberos-like token.  
- ACL evaluated on each lookup component (or cached with lease).  
- Traversal requires execute/list on directories (POSIX semantics).  
- Compliance: per-volume encryption keys in Key Vault; audit metadata ops.

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Hot metadata | Raft shard + leases | Correct + fast reads | Eventually consistent dirents for MVP POSIX |
| Huge dir | Hash-partitioned dirents | Avoid single row | Unbounded single map in one Raft log entry |
| Tiny files | Inline bytes | Cut RPCs | 3 chunk RPCs for 100-byte files always |
| Large files | Chunk list / extents | Stream | Single blob without chunking limits parallelism |
| Symlink resolve | Client-assisted + server verify | Performance | Server-only walk every open without cache |
| Multi-region | Volume home region | Avoid split-brain | Active-active metadata writers |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Clients / Mounts (agent)
           |
           v
  +------------------+
  | Gateway / Front  |  authn (Entra), rate limits
  +--------+---------+
           |
     +-----+------+
     |            |
     v            v
 +---------+  +--------------+
 | Meta    |  | Chunk / Data |
 | Shards  |  | Nodes / Blob |
 | (Raft)  |  |              |
 +----+----+  +------+-------+
      |              |
      +------+-------+
             v
      +--------------+
      | GC / Compactor|
      | Repair        |
      +--------------+
```

### 4.2 Path walk sequence

```text
Client                Meta Shard
 |--LOOKUP /a ------->|
 |<- inode a ---------|
 |--LOOKUP a/b ------>|  (maybe different shard via location hint)
 |<- inode b ---------|
 |--OPEN b/c -------->|
 |<- file handle + extents
 |--READ chunk ------> Chunk store
 |<- bytes -----------|
```

### 4.3 Symlink resolution

```text
lookup "link" -> type=symlink target="../x/y"
splice → resolve relative to parent of link
follow until file/dir or ELOOP
```

### 4.4 Rename within volume

```text
Client → Meta Coordinator
  lock parents
  cycle check if dir
  Raft multi-op / single batched log entry on owning shards
  (same shard: one atomic log entry)
```

### 4.5 Sharded namespace at 100×

```text
                Location Map (dir→shard)
                        |
        +---------------+---------------+
        v               v               v
     Shard 0         Shard 1         Shard N
     (Raft)          (Raft)          (Raft)
        \               |               /
         \              v              /
              Chunk clusters (shared)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Data loss prevention

- Metadata log replicated (Raft majority) before ACK.  
- Chunk writes: replicate to `R` nodes; ACK on quorum; checksum per chunk.  
- **Never** point metadata at chunks not quorum-durable.  
- Generation numbers fence stale writers after primary change.

#### 5.1.2 Retries

- Client retries idempotent reads freely.  
- Creates use idempotency tokens or exclusive create flags.  
- Chunk put: content-addressed or `(chunk_id, version)` CAS.  
- Rename retries must be safe (status query if timeout).

#### 5.1.3 Fencing

- Metadata primary epoch; followers reject old primary.  
- Chunk write leases: expired lease → writes fail.  
- Client file handle includes `file_generation`; stale handle → `ESTALE`.

#### 5.1.4 Rate limits

- Per-mount metadata QPS.  
- Per-volume write bandwidth tokens.  
- readdir page size caps.  
- Symlink follow CPU caps (max depth already).

#### 5.1.5 Failure table

| Failure | Behavior |
|---------|----------|
| Chunk node death | Re-replicate from survivors; heal |
| Meta primary death | Elect; replay log; clients reconnect |
| Network partition | Minority cannot ACK writes |
| Bitrot | Checksum fail → repair from replica |
| GC races | Refcount / delete-epoch before reclaim |

### 5.2 Scalability

#### 5.2.1 Traffic elasticity

- Stateless gateways scale horizontally.  
- Add metadata shards; migrate directories (subtree move / copy-on-write map).  
- Add chunk nodes; rebalance by chunk id hash.  
- Read replicas / lease caches for lookup-heavy workloads.

#### 5.2.2 Storage

- Replication factor 3 → erasure coding for cold large files (trade CPU/rebuild).  
- Compact small-file inline arenas.  
- Snapshot via COW extent trees (phase 2).

#### 5.2.3 Parallelization

- Independent files parallel.  
- Single large file: striped chunks.  
- readdir parallel only if dir shard map allows.  
- Avoid global locks.

#### 5.2.4 Progressive architecture

| Scale | Design |
|-------|--------|
| 1× | 1 meta Raft group + chunk cluster |
| 10× | Many meta shards; client dentry cache + leases |
| 100× | Dir partitioning; volume cells; EC cold tier |
| 1000× | Hierarchical location service; tenant cells; geo-DR standby |

### 5.3 Maintainability

- Explicit inode type enum; central `resolve()`.  
- Error code parity with POSIX reduces client bugs.  
- Schema migrations for dirent formats versioned.  
- Metrics: lookup latency, lease breaks, heal backlog, ELOOP rate.  
- Separate LLD exercise from distributed concerns in interviews—say so upfront.  
- Compatibility modes: “Azure Files SMB semantics” vs “POSIX NFS-like” feature flags.

---

## 6. Wrap-Up

**Deliverable:** A sharded, consensus-backed namespace with chunked data plane, correct traversal/symlink semantics, atomic renames within shards, and a clear story for hot directories and cross-shard limits—framed for Microsoft Azure storage DNA.

**Say clearly:** HLD here; coded OOP filesystem is the LLD sibling.

---

## 7. Deeper / Related Interview Questions

### 7.1 Traversal & symlinks

**Q: Difference `stat` vs `lstat`?**  
A: `lstat` does not follow final symlink; `stat` does.

**Q: Why max symlink depth?**  
A: Prevent cycles and CPU DoS.

**Q: Relative symlink when parent moves?**  
A: Still relative to link location—may break; that’s UNIX behavior.

### 7.2 Consistency

**Q: Is read-after-write guaranteed across clients?**  
A: After write ACK + lease break/invalidate, yes in this design; without cache coherency protocol, stale reads possible—call it out.

**Q: Compare to S3/Blob eventual listing?**  
A: Object stores often weaker listing; DFS metadata aims stronger.

### 7.3 Memory & caching

**Q: Unlimited client dentry cache?**  
A: No—LRU + leases; memory capped.

**Q: Cache symlink targets?**  
A: Yes with lease on symlink inode.

### 7.4 Storage & DB

**Q: Postgres as metadata?**  
A: Fine MVP for one volume; deal-breaker at 5M metadata QPS without sharding.

**Q: Why Raft not DB?**  
A: Fine-grained ops, HA primary, predictable latency; DB still OK early.

**Q: Indexing dirents?**  
A: `(parent_id, name)` unique primary; pagination by name.

### 7.5 Load balancing & hashing

**Q: Hash file path for shard?**  
A: Bad for renames (hash changes). Hash **inode id**; location map for dirs.

**Q: Consistent hashing for chunks?**  
A: Yes—`chunk_id → storage node set`.

### 7.6 Algorithms

**Q: Detect rename into descendant?**  
A: Walk parents from dst looking for src inode; or maintain parent pointers + depth.

**Q: Directory entry lookup structure?**  
A: Hash map / B-tree per dir shard; LSM in log-structured meta stores.

### 7.7 Hard links & nlink

**Q: Why defer hard links?**  
A: GC, quotas, backups, and dir hard-link bans add surface; soft links cover interview symlink ask.

### 7.8 Multi-region

**Q: Active-active volumes?**  
A: Avoid for POSIX. DR async replica + promote with fence.

### 7.9 Security

**Q: Path-based authz only?**  
A: Dangerous if symlink escapes; check each component + finalize inode ACL.

**Q: Symlink escape from share root?**  
A: Jail resolution within volume root; reject escape.

### 7.10 Comparison questions

**Q: GFS/HDFS vs this?**  
A: Those optimize large sequential analytics; fewer POSIX semantics; single master historically.

**Q: Azure Files vs Blob vs ADLS?**  
A: Files ≈ SMB shares; Blob ≈ object; ADLS ≈ hierarchical namespace over object—pick based on API needs.

**Q: When is object storage enough?**  
A: No renames/directories needed; analytics; web assets.

### 7.11 Interview traps

| Trap | Pushback |
|------|----------|
| Store TB files in SQL rows | No |
| Ignore symlink loops | DoS / correctness fail |
| Atomic cross-datacenter rename | Hard; don’t handwave |
| Hash(path) sharding | Rename breaks locality/identity |
| 100M×1MB=100PB | **100TB** |
| Claim full POSIX at global scale | Too strong |

### 7.12 LLD pivot

**Q: Interviewer asks to code classes?**  
A: Switch to sibling LLD: `Node`, `File`, `Directory`, `SymbolicLink`, `FileSystem.resolve(path)`. Keep HLD for distribution.

---

## 8. Appendices

### 8.1 API checklist (RPC-ish)

- [ ] `Lookup(parent, name)`  
- [ ] `Create(parent, name, type, attrs)`  
- [ ] `Mkdir` / `Symlink` / `Unlink` / `Rmdir`  
- [ ] `Rename(src_parent, src_name, dst_parent, dst_name)`  
- [ ] `Readdir(dir, cookie, limit)`  
- [ ] `Getattr` / `Setattr`  
- [ ] `Read` / `Write` / `Fsync`  
- [ ] `Getxattr` optional  

### 8.2 Schema sketches

```text
inodes(inode_id, type, mode, uid, gid, size, mtime, ctime,
       symlink_target NULL, inline_data NULL, gen)

dirents(parent_id, name, child_id, PRIMARY KEY(parent_id, name))

extents(inode_id, file_offset, chunk_id, length)

chunks(chunk_id, size, checksum, replica_locs[])

leases(inode_id, client_id, mode, expiry)
```

### 8.3 Invariants

1. Unique `(parent_id, name)` among live dirents.  
2. Directory `.` / `..` consistent (or computed).  
3. No rename of dir under itself.  
4. Chunk GC only when unreferenced and delete-epoch safe.  
5. Symlink follow ≤ MAXSYMLINKS.  
6. ACK’d write ⇒ durable quorum + metadata commit.  
7. Root has no `..` escape.

### 8.4 Progressive scale playbook

| Scale | Must have |
|-------|-----------|
| 1× | Single meta Raft, chunk replicas, resolve+symlink |
| 10× | Meta shards, client cache/leases, paginated readdir |
| 100× | Hot-dir partition, EC cold, volume cells |
| 1000× | Hierarchical location service, tenant isolation, DR |

### 8.5 Error code map

| Code | Meaning |
|------|---------|
| ENOENT | Missing component |
| ENOTDIR | Walk through non-dir |
| EEXIST | Create conflict |
| ELOOP | Symlink loop |
| ENOTEMPTY | rmdir |
| EACCES | ACL |
| ESTALE | Fenced handle |
| EINVAL | Illegal rename |
| ENOSPC | Quota/capacity |

### 8.6 Resolve test vectors

```text
/a/./b/../b/c     → /a/b/c
/a/symlink→/b/x   → /b/x when following
/a/link_loop      → ELOOP
/../etc           → /etc (root clamp) or reject outside jail
```

### 8.7 Small-file vs large-file path

```text
if size <= INLINE_MAX: store in metadata log
else: write N chunks; metadata stores extent map only
```

### 8.8 Lease / cache sketch

```text
Client caches dentry (name→inode) with lease L
On mutating op, meta breaks leases → clients invalidate
Lookup miss → RPC
```

### 8.9 GC algorithm sketch

```text
on unlink file: nlink-- (or remove last dirent)
if unreachable: mark delete_epoch = current
GC after grace: delete chunks with refcount 0
```

### 8.10 Interview 60-second summary

> Split **metadata** and **data**. Metadata shards run Raft for linearizable dirents/inodes; files are chunked to replicated storage. Path resolution handles `.`/`..` and symlinks with loop limits. Renames are atomic within a shard; cross-shard needs a real protocol. Scale with dentry leases, dir partitioning, and volume home regions on Azure—while LLD classes are a separate exercise.

### 8.11 Related systems map

```text
Mount → Gateway → Meta Shards (namespace, ACLs, symlinks)
                     ↓
                 Chunk Store (bytes)
                     ↓
                    GC / Repair / Metrics
```

### 8.12 Azure product mapping (talk track)

| Concept | Azure analogy |
|---------|---------------|
| Volume/share | Azure Files share / ADLS filesystem |
| Chunks | Storage extents / blobs/blocks |
| Identity | Entra ID |
| DR | Geo-redundant storage / failover |

### 8.13 Permissions walk example

```text
open /a/b/c requires search(a), search(b), read(c)
symlink final component: depends on op (follow or not)
```

### 8.14 Cross-shard rename protocol (sketch)

```text
1) Prep: lock src & dst shards with sorted ids + txn_id
2) Check constraints (exists, cycle, ACL)
3) Commit intent logs on both
4) Apply dirent mutate
5) Unlock; recovery reads intent on crash
```

Or: **copy-on-write file move** for MVP honesty if shards differ.

### 8.15 Observability SLOs

| SLO | Target |
|-----|--------|
| Lookup p99 | < 20ms cached; < 50ms uncached in-region |
| Durable write ACK p99 | Depends on size; metadata commit < 30ms |
| Heal backlog | < X chunks aged > 1h |
| ELOOP rate | alert on spikes (bug or attack) |

### 8.16 Glossary

| Term | Meaning |
|------|---------|
| Inode | File/dir/symlink metadata object |
| Dirent | Directory entry name→inode |
| Chunk | Fixed-size data blob |
| Lease | Time-bounded cache coherency grant |
| Generation | Fencing counter for file handles |
| Volume | Isolated namespace root |

### 8.17 Explicit HLD vs LLD boundary

| HLD (this doc) | LLD (sibling) |
|----------------|---------------|
| Shards, Raft, chunks, leases | Classes & methods |
| Multi-tenant Azure cells | In-memory tree |
| Quotas, GC, EC | Recursion / path string API |

### 8.18 Failure injection plan

1. Kill meta primary mid-rename → recovery no double dirent.  
2. Chunk checksum fail → read from other replica.  
3. Symlink cycle → ELOOP.  
4. Lease break under concurrent writer → no silent stale read.  
5. Hot dir overload → partition / 429.

### 8.19 Quota & multi-tenant

```text
quota per (tenant, volume): namespace_count, bytes
enforce on create/write
noisy neighbor: per-tenant rate limits at gateway
```

### 8.20 Why not “everything in one object store prefix”?

Listing, renames, append consistency, and POSIX ops become awkward; hierarchical DFS metadata exists precisely for these operations. Object prefixes are great when the API is object-native.

---



### 8.21 Write path deep dive (chunked file)

```text
Client wants to write 100 MB starting at offset 0; chunk size 4 MB.

1) OPEN / create → file_inode + generation G
2) For each chunk i in 0..24:
   a. ALLOCATE or LOOKUP chunk_id for file_offset
   b. WRITE_CHUNK to replica set (primary + secondaries) with checksum
   c. Wait quorum ACK
3) COMMIT_EXTENTS metadata: update size, mtime, extent map, gen stays or ++
4) FSYNC: ensure metadata Raft commit index includes this update

Failure between 2 and 3:
- Orphan chunks possible → GC with creation epoch / refcheck
- Client retries commit with same chunk_ids (idempotent)
```

**Deal-breaker:** Point metadata size ahead of durable chunk quorum (readers see holes / checksum fails).

### 8.22 Read path & locality

```text
1) LOOKUP path → file inode + extents (cached under lease)
2) READ offset/len → map to chunk_ids
3) Fetch from nearest healthy replica (rack/AZ aware)
4) Verify checksum; on fail try other replica + repair trigger
```

Sequential read ahead: client or gateway prefetches next chunks.

### 8.23 Directory sharding strategies

| Strategy | Mechanism | Pros | Cons |
|----------|-----------|------|------|
| Single map | One Raft group owns dir | Simple | Hot dir melt |
| Hash by name | `hash(name)%B` buckets | Parallel lookup | readdir merge |
| Range by name | Lex ranges | Good readdir | Hot prefix (dated names) |
| Adaptive split | Split bucket when >T entries | Handles growth | Implementation complexity |

**Interview pick:** Start single; at 100× use hash buckets with merged readdir cursors `(bucket, name)`.

### 8.24 Symlink + ACL interaction examples

```text
/share/a (user=alice) → symlink to /share/secret (mode 700 root)
User bob follows link:
  - needs search on /share and /share/a path components
  - final open checks ACL on /share/secret → EACCES
Symlink itself may be 777; target enforces access (UNIX-like)
```

Jail: resolution never escapes volume root even if symlink says `/etc/passwd`.

### 8.25 Comparison: this DFS vs Dropbox-like sync

| Concern | DFS (this) | Dropbox-like |
|---------|------------|--------------|
| API | POSIX-ish mount | Sync folders / object |
| Conflicts | Writer leases / locks | User-level conflict copies |
| Offline | Limited | First-class |
| Rename | Namespace atomicity focus | Eventual sync events |

If interviewer wanted Dropbox, pivot; this prompt is namespace DFS.

### 8.26 Capacity planning worksheet

```text
usable_capacity ≈ raw_disk / RF          # or / EC_overhead
metadata_nodes ≈ metadata_qps / qps_per_shard
chunk_nodes ≈ (write_GB_s + read_GB_s) / per_node_GB_s × headroom
client_leases_mem ≈ active_inodes_cached × lease_entry_size
```

### 8.27 Snapshot sketch (phase 2)

```text
Snapshot S: COW mark on inode tree / extent tree
New writes allocate new chunks; old chunks shared until delete
Read at S: traverse snap pointer
Cost: metadata amplification; schedule snap GC
```

### 8.28 Encryption & compliance

- At rest: volume master key in Key Vault; chunk encryption keys wrapped.
- In transit: TLS mounts.
- Customer-managed keys (CMK) rotation: rewrap, lazy re-encrypt.
- Audit: metadata mutating ops to immutable log (who renamed what).
- Soft delete / legal hold: tombstone retention overrides GC.

### 8.29 Interview 5-minute outline

1. Requirements: files/dirs/symlinks, consistency, scale.  
2. Split meta vs data.  
3. Resolve algorithm with symlink loops.  
4. Raft metadata + chunk quorum.  
5. Rename + hot dir.  
6. Progressive shards + Azure mapping.  
7. Call out LLD sibling if they want code.

### 8.30 Anti-patterns checklist

- [ ] Path string as primary key forever  
- [ ] Synchronous cross-region POSIX  
- [ ] Unbounded readdir response  
- [ ] Follow symlinks on `unlink` final component incorrectly  
- [ ] GC without grace epoch  
- [ ] Claiming linearizability while using eventually consistent caches without leases  

---

*End of distributed file system (HLD) system design.*
