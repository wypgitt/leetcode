# System Design: Shared Cloud Filesystem

> **Interview framing:** NVIDIA backend / cloud / AI-infra interviews (team-dependent). Shared storage questions appear when discussing training data lakes, checkpoint stores, developer home directories, and multi-tenant research clusters—not only “build Dropbox.”
> **Focus areas:** Metadata vs data plane · POSIX-ish vs S3+mount · Consistency · Caching · Multi-writer · Quotas · Snapshots · ML training / checkpoint I/O
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split control-plane (metadata) from data-plane (bytes); honest consistency model; correct bandwidth math for training/checkpoint workloads; deal-breakers called out

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

Goal: **bound the filesystem**—POSIX illusion vs object semantics, who shares what, which consistency clients need for training checkpoints, and where metadata becomes the bottleneck.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are the clients? | Training jobs (GPU nodes), inference services, researchers via notebooks, CI artifacts, backup agents | Heterogeneous access patterns; one API surface with multiple gateways |
| F2 | API shape? | **POSIX-ish** mount (FUSE/NFS-like) *and/or* S3-compatible + optional mount | Dual frontends over shared metadata/data planes preferred |
| F3 | Namespace model? | Hierarchical directories: `/org/project/datasets/...` | Directory tree + inode-like objects; not flat bucket alone |
| F4 | Consistency? | Read-after-write for single writer; multi-writer needs explicit rules | Lease/lock or versioned objects; no silent lost updates |
| F5 | Multi-writer? | Common on shared datasets (many readers, few writers); checkpoints usually single writer per path | Reader scale-out + writer fencing |
| F6 | Quotas? | Hard bytes + soft inodes per org/project; burst soft limits | Quota service on create/write path |
| F7 | Snapshots / versions? | Point-in-time snapshots for datasets & home dirs; retain N checkpoints | Copy-on-write metadata; immutable data chunks |
| F8 | Permissions? | IAM + POSIX mode bits / ACLs; project isolation | Authz at gateway + metadata checks |
| F9 | Durability? | “Don’t lose checkpoints” — multi-AZ object storage | Chunks durable before ACK of close/fsync policy |
| F10 | Special ML ops? | Fast sequential read of shards; atomic rename for checkpoint finalize; listing millions of files | Rename as CAS; listing via metadata index not S3 LIST alone |
| F11 | Caching? | Client page cache + optional edge/read caches for hot datasets | Cache invalidation protocol tied to consistency model |
| F12 | Observability? | Per-project throughput, hot files, metadata QPS, slow fsync | Metrics + audit trail for deletes/quota |

**MVP functional scope (lock with interviewer):**

1. Hierarchical namespace with create/open/read/write/close, mkdir, unlink, rename.
2. **Data plane:** content-addressed or extent-based chunks in object storage / block store.
3. **Metadata plane:** durable inode + directory entries + chunk maps.
4. Single-writer lease per open file (or per inode) for mutable files; many concurrent readers.
5. Quotas (bytes + file count) enforced at create/extend.
6. Snapshot create/list/restore (directory subtree).
7. Mount client (FUSE) for POSIX-ish; optional S3 gateway for tools.
8. Authn/authz (token → principal → ACL/IAM).

**Out of MVP (explicitly defer):**

- Full POSIX (byte-range locks across all clients, mmap coherency perfection, flock semantics everywhere).
- Cross-region active-active **mutable** namespace without a home region.
- Kernel NFS server reimplementation bit-for-bit.
- Transparent global dedupe across all tenants (design hooks only).
- Perfect close-to-open consistency under arbitrary multi-writer without leases.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Metadata latency | Fast open/stat/list | p50 < 5ms, p99 < 50ms in-region for cached hot paths |
| N2 | Data throughput | Saturate NIC for sequential training reads | ≥ 10–100 Gbps/node class depending on fabric |
| N3 | Small-file ops | Painful but bounded | Optimize listing + create rate; don’t pretend equal to big-file |
| N4 | Durability | Checkpoint safe after durable finalize | RPO ≈ 0 for acknowledged fsync/close-with-sync |
| N5 | Availability | Metadata HA; data via object store | 99.9%+ control plane; degrade reads if possible |
| N6 | Consistency | Documented model | Close-to-open **or** lease-based; pick one and stick |
| N7 | Multi-tenancy | No cross-project data leak; noisy neighbor limited | Quotas + QoS tokens + shuffle sharding metadata |
| N8 | Scale | See progressive table | Split **metadata QPS** from **GB/s data** |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Training job mounts `/datasets/imagenet` read-only → many nodes sequential read shards → high cache hit after warmup.
2. Trainer writes checkpoint to `/runs/exp1/ckpt.tmp` → fsync → atomic `rename` to `ckpt-000123` → readers see new or old, never partial.
3. Researcher creates project dir → quota checked → uploads via S3 API → same bytes visible via FUSE.
4. Admin snapshots `/datasets/foo` before mutation → restore earlier tree after bad preprocess.
5. Job deleted files under soft-delete retention → undelete within window.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two writers open same path | Second blocked or gets exclusive lease fail; no silent overwrite |
| Client crash holding lease | Lease expiry; reclaim; partial extents GC’d if not committed |
| fsync then metadata node dies | fsync ACK only after chunk durable + metadata commit |
| Rename races with readers | Readers finish on old inode; new opens see new |
| Hot directory with 10M children | Sharded directory entries; cursor listing; no O(N) single RPC |
| Tiny files storm (1KB × millions) | Metadata dominates; batch create API; packing optional |
| Quota exceeded mid-write | Fail write/extend; don’t leave unbounded sparse claim |
| Snapshot during active write | COW: snapshot references committed chunks only |
| Cache serving stale after overwrite | Invalidate via lease version / callback / short TTL+revalidate |
| Cross-AZ metadata partition | Single primary / consensus; followers read-only or stale |
| Multi-region write to same path | Home-region ownership; reject dual-primary |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Namespaces / tenants | 100 | 1K | 10K | 100K |
| Files (inodes) | 100M | 1B | 10B | 100B |
| Directories | 10M | 100M | 1B | 10B |
| Aggregate stored | 10 PB | 100 PB | 1 EB | 10 EB |
| Peak metadata QPS (cluster) | 50K | 500K | 5M | 50M |
| Peak data ingress | 50 GB/s | 500 GB/s | 5 TB/s | 50 TB/s |
| Peak data egress (training) | 200 GB/s | 2 TB/s | 20 TB/s | 200 TB/s |
| Concurrent mounts / clients | 5K | 50K | 500K | 5M |
| GPU nodes reading datasets | 1K | 10K | 100K | 1M |
| Snapshots retained | 100K | 1M | 10M | 100M |
| Checkpoint finalize rate | 100/s | 1K/s | 10K/s | 100K/s |
| Regions | 1 | 2 | 4 | 8+ |

**What each jump forces:**

- **10×:** Shard metadata by subtree hash; separate MDS (metadata servers); client attribute cache with callbacks.
- **100×:** Directory entry sharding; chunk placement locality; dedicated checkpoint path; QoS for noisy tenants.
- **1,000×:** Hierarchical MDS (namespace routers); regional data pools; snapshot GC at massive scale; home-cell metadata for mutable trees.

### 1.5 Etc. (Constraints & Assumptions)

- Object storage (or distributed block) is the **byte durability** layer; we own namespace + coherence.
- GPU training prefers **sequential large reads**; random tiny reads need different caching.
- Checkpoint correctness prefers **atomic rename** + durable fsync semantics over “eventual LIST.”
- POSIX is a **compatibility layer**, not a promise of single-node local FS behavior under all races.
- NVIDIA interview angle: connect answers to **training throughput**, **checkpoint RPO**, and **multi-tenant research clusters**.

**Scope statement:**

> Design a multi-tenant shared cloud filesystem with a split metadata/data plane, POSIX-ish mount and optional S3 gateway, lease-based single-writer consistency, quotas and snapshots, optimized for ML dataset reads and checkpoint finalize—scaling from tens of PB and 50K metadata QPS through 10× / 100× / 1,000× without conflating GB/s with control-plane QPS.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Metadata (open/stat/create/rename) | 50K QPS | 50M QPS | Control plane; shards + cache |
| Directory list / readdir | 5K QPS | 5M QPS | Can be heavy; cursor + cache |
| Data write ingress | 50 GB/s | 50 TB/s | Object/chunk plane |
| Data read egress | 200 GB/s | 200 TB/s | Dominated by training |
| Lease heartbeat / refresh | 10K QPS | 10M QPS | Separate cheap path |
| Snapshot create | 10/s | 10K/s | Metadata-heavy COW |

**Deal-breaker:** quoting a single “cluster QPS” that mixes 200 GB/s reads with open() calls.

### 2.2 Training read bandwidth

```text
Baseline: 1,000 GPU nodes, each reading training data at 200 MB/s average
Aggregate ≈ 1,000 × 0.2 GB/s = 200 GB/s  (matches table)

At 100× nodes (100K GPUs):
100,000 × 0.2 = 20,000 GB/s = 20 TB/s egress

If dataset is 50 TB and epoch streams it once:
Time ≈ 50 TB / 20 TB/s = 2.5s theoretical — unrealistic (compute-bound);
storage must still sustain burst; design for peak, not average epoch math alone.

Per-node NIC: 25–100 Gbps common; don’t claim 1 TB/s per node without fabric.
```

### 2.3 Checkpoint write math

```text
Model checkpoint: 2 TB compressed? or 200 GB sharded?
Example: 16 shards × 25 GB = 400 GB checkpoint every 30 minutes

Write time at 10 GB/s aggregate for that job:
400 / 10 = 40s — OK if overlapped / async

Finalize: N chunk commits + 1 rename — metadata small but latency-sensitive
At 1,000×: 100K finalize/s would melt a monolith MDS → shard + batch
```

### 2.4 Metadata storage

```text
Inode ~256–512 B + chunk map entries
100M files × 400 B ≈ 40 GB metadata (tight)
1B files × 400 B ≈ 400 GB
100B files × 400 B ≈ 40 TB metadata

Directory entries: name + inode id ~64–128 B each
Plus indexes, ACLs, xattrs → plan 2–5× raw

Must fit in sharded KV / NewSQL with RAM caches for hot inodes
```

### 2.5 Small-file create storm

```text
Creating 10M files of 1 KB:
Data: 10M × 1 KB = 10 GB (trivial)
Metadata ops: 10M creates + parents updates
At 50K create/s → 200s; at 5K/s → ~30 min
→ API: bulk mkdir/create; directory shard; async indexing
```

### 2.6 Snapshot space

```text
COW snapshots share unchanged chunks
If 10% of bytes churn between snapshots:
Snapshot “logical size” can be full tree; physical delta ≈ 0.1 × touched
GC must reclaim unreferenced chunks carefully (refcounts)
```

### 2.7 Critical bottlenecks (rank ordered)

1. **Metadata hotspot** on popular directories (`/datasets/foo`)  
2. **Lease/heartbeat** path if naïvely durable-per-tick  
3. **Stale client caches** after overwrite (correctness)  
4. **Checkpoint finalize latency** under MDS load  
5. **Listing** huge directories  
6. **Quota accounting races**  
7. **GC / compaction** fighting live I/O  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Namespace     → tree of Directory / File / Symlink (inodes)
Inode         → id, type, size, mtime, ACL, lease, attrs
Chunk / Extent→ immutable byte range stored in object/block plane
Chunk Map     → file offset → chunk_id (+ checksum)
Lease         → exclusive write ownership with fencing token
Snapshot      → immutable root pointer + COW refs
Mount Client  → FUSE/NFS-ish agent with page + attr cache
S3 Gateway    → object API façade over same inodes/chunks
```

### 3.2 Options: POSIX-ish vs S3+mount

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Pure S3 | Simple durability; familiar | Weak rename/atomic dir; LIST pain | Checkpoint needs atomic replace + POSIX tools |
| B. Pure POSIX distributed FS | Familiar mount | Hard coherency; ops complexity | Team underestimates MDS |
| C. **Hybrid:** MDS + chunk store + FUSE + S3 gateway | Best of both | Two frontends to maintain | Frontends diverge on semantics |
| D. NFS re-export of object | Quick demo | Consistency/scale cliffs | Production ML at 100× |

**Chosen path:** **Hybrid C** — one metadata plane + chunk data plane; FUSE for POSIX-ish; S3 gateway for pipelines; document semantic subset (especially locks and mmap).

### 3.3 Metadata vs data plane (resolve ownership)

| Plane | Owns | Does not own |
|-------|------|--------------|
| Metadata (MDS) | Paths, inodes, ACLs, leases, chunk maps, quotas, snapshots | Bulk byte transfer |
| Data (chunk servers / object) | Durable bytes, replication/erasure | Namespace truth |
| Client | Cache, readahead, write-back buffers (policy) | Authoritative size/mtime without revalidate |

**Invariant:** Bytes referenced by a **committed** chunk map entry are durable before the metadata commit that publishes them is ACKed.

### 3.4 Consistency models (pick explicitly)

| Model | Meaning | Use |
|-------|---------|-----|
| Close-to-open | Reader opening after writer close sees new data | Classic NFS-ish |
| Lease + version | Writer holds lease; attr/version bumps invalidate caches | Stronger for shared mutable |
| Immutable objects + new key | Writers create new versions; readers pin version | Datasets & checkpoints |
| Linearizable MDS | Metadata ops via consensus | Critical path ops |

**Chosen MVP:**  
- **Datasets:** immutable publish (write to staging → atomic rename/publish).  
- **Mutable files:** **exclusive write lease** + inode version; clients revalidate attrs.  
- **Reads:** allow attr cache with callback or short TTL; data cache keyed by `(chunk_id)` immutable → safe.

**Deal-breaker:** Claiming “strong consistency” while serving mutable file data from unchecked client caches.

### 3.5 Multi-writer strategies

| Strategy | When | Trade-off |
|----------|------|-----------|
| Deny (single writer lease) | Default mutable files | Simple; serializes writers |
| Byte-range locks | Rare collaborative editors | Complexity; not needed for ML checkpoints |
| Version vectors / last-writer-wins | Collaborative docs | Wrong for binary checkpoints |
| Copy-on-write versions | Git-like datasets | Storage amplification |

For NVIDIA-style training: **single writer per checkpoint path**; many readers of frozen datasets.

### 3.6 Caching architecture

```text
Client page cache  → data by chunk_id (immutable) — safest
Client attr cache  → inode version / lease epoch — must invalidate
Read cache tier    → optional (CDN/edge) for public-ish datasets
MDS memory cache   → hot inodes + dir blocks
```

Invalidation options: (1) callbacks from MDS, (2) lease break, (3) TTL+GETATTR revalidate on open.

### 3.7 Quotas

```text
On create/extend:
  reserve bytes in quota ledger (org/project)
  commit usage on durable write / punch hole releases
Soft limit → warn; hard limit → ENOSPC-like
Inode count separate from bytes
```

**Deal-breaker:** Checking quota only at file create, not on append/extend.

### 3.8 Snapshots

```text
snapshot(subtree):
  COW: clone root directory inode refs (increment chunk refcounts)
  New writes allocate new chunks; old snapshot keeps old maps
restore: publish snap root as live (or copy-out)
GC: drop chunks when refcount=0 and not in any live/snap map
```

### 3.9 Checkpoint-friendly API semantics

```text
1. create ckpt.tmp (exclusive)
2. write shards / multi-part
3. fsync / commit chunk map
4. rename ckpt.tmp → ckpt-N  (atomic directory entry CAS)
Readers either miss file or see complete inode — never torn map
```

Optional: `publish(path, expected_version)` for compare-and-swap.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Byte durability | Object/erasure store | Cheap EB scale | Triple-replicate everything in MDS disks |
| Namespace | Sharded MDS / NewSQL | Low latency ops | Single Postgres for 50M QPS |
| Mutable coherency | Write leases + versions | Correct multi-client | TTL-only caches forever |
| Datasets | Immutable + rename publish | Training scale | In-place overwrite of shared shards |
| S3 + POSIX | Shared chunk IDs | One truth | Two stores dual-write |
| Listing | Dir shards + cursors | Huge dirs | Recursive S3 LIST as SoT |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  GPU trainers / notebooks / CI          S3 tools / pipelines
           |                                    |
           v                                    v
   +---------------+                    +---------------+
   | FUSE / Mount  |                    | S3 Gateway    |
   | Client Agent  |                    | (IAM mapped)  |
   +-------+-------+                    +-------+-------+
           |                                    |
           +----------------+-------------------+
                            |
                            v
                 +----------------------+
                 | API / Protocol GW    |
                 | authz, QoS, routing  |
                 +----------+-----------+
                            |
           +----------------+----------------+
           |                                 |
           v                                 v
  +------------------+             +------------------------+
  | Metadata Plane   |             | Data / Chunk Plane     |
  | (MDS shards,     |  chunk ids  | Object storage /        |
  |  leases, quotas, |-----------> | chunk servers          |
  |  snapshots)      |             | (multi-AZ)             |
  +--------+---------+             +------------------------+
           |
           v
  +------------------+
  | Quota Ledger +   |
  | Audit / Metrics |
  +------------------+
```

### 4.2 Sequence: write + atomic checkpoint rename

```text
Client                 MDS                      Object Store
  |                     |                            |
  |-- Open(excl) ------>| grant lease_id, inode      |
  |-- Write chunks ---->| (optional allocate) ------>| PUT chunk
  |<- checksums --------|<---------------------------|
  |-- Commit map ------>| durable map + size         |
  |-- Fsync ----------->| wait durability ------------|
  |<- OK ---------------|                            |
  |-- Rename tmp→final->| CAS dirent; bump versions  |
  |<- OK ---------------|                            |
  |-- Close/lease drop->|                            |
```

### 4.3 Sequence: multi-reader dataset

```text
Trainer A/B/C          MDS                 Cache/Object
  |-- Open RO -------->| check ACL         |
  |<- inode+map -------|                   |
  |-- GET chunk_id -------------------> hit/miss
  |<- bytes ---------------------------|
  (attr cache; data cache by chunk_id immutable)
```

### 4.4 Sequence: lease steal after client death

```text
Writer (dead)      Lease Reaper           New Writer
     |                  |                      |
  (no renew)            |                      |
     |                  |-- expire lease ----->|
     |                  |-- fence epoch++ ---->|
     |                                     Open(excl) OK
  old Write(lease_old) -----------------> REJECT
```

### 4.5 Scale cells

```text
Global Namespace Router: /org → home metadata cell
Cell:
  MDS shard set | Quota | Lease managers
Data pools: may be regional; chunk_id includes pool
Clients: mount with cell directory; cross-cell path rare
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Publish ⇒ durable bytes:** chunk PUT durable before map commit ACK.  
2. **Atomic rename:** directory entry CAS; readers never observe half-updated maps.  
3. **Lease fencing:** writes require current `lease_id` / epoch.  
4. **Quota non-negative & bounded:** reservations prevent silent overcommit beyond policy.  
5. **Snapshot immutability:** snap root’s reachable chunk set doesn’t change.  
6. **Authz on every mutating path:** including S3 and FUSE.  
7. **GC safety:** only reclaim chunks with refcount 0 across live+snap+pending.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| MDS primary crash | Consensus election; replay log; leases may expire → clients renew |
| Object PUT timeout after success | Idempotent chunk_id (content hash or UUID); commit only if exists |
| Client crash mid-write | Uncommitted extents GC; lease expiry |
| Split-brain MDS | Raft/Paxos epoch; followers don’t accept writes |
| Quota store lag | Reserve in same TX as create/extend or two-phase reserve |
| Snapshot GC bug | Refcount audits; rate-limited GC; quarantine |

**fsync semantics (resolve with interviewer):**

- **Strict:** ACK fsync only when chunks + metadata durable.  
- **Relaxed:** ACK on client buffer flush to MDS buffer (document risk)—usually wrong for checkpoints.

### 5.2 Scalability

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| 1× | Single MDS (HA pair) + object store; FUSE clients; PG/etcd for meta OK |
| 10× | Hash-shard inodes/dirs; attr cache + lease callbacks; QoS |
| 100× | Directory sharding; namespace routers; checkpoint fast path; read caches |
| 1000× | Cells / home regions; hierarchical MDS; regional data pools; bulk APIs |

**Hot directory techniques**

- Shard dirents by `hash(filename)` into buckets.  
- Cache negative lookups carefully (TTL).  
- Prefer wide trees over single dir with 50M children when product allows.

**Training read scaling**

- Immutable chunks → aggressive client + node-local cache.  
- Placement: replicate hot dataset chunks near GPU racks / use parallel object gateways.  
- Avoid MDS on every read—only on open / cache miss of map.

**Metadata QPS scaling**

- Batch getattr/lookup RPCs.  
- Lease renewals batched per client agent.  
- Separate read-only MDS replicas for stat-heavy traffic with known staleness bound.

### 5.3 Maintainability

- Protocol version negotiation (client ↔ MDS).  
- Feature flags for relaxed vs strict fsync.  
- Chaos: kill MDS leader, inject slow object PUT, expire leases under load.  
- Schema migrations for inode attrs with dual-read.  
- Clear semantic doc: “POSIX subset.”

**Observability (must-have)**

- Metrics: metadata QPS/latency by op, lease expiries, fsync latency, GB/s in/out per project, cache hit ratio, ENOSPC/quota rejects, rename rate.  
- Traces: `inode_id`, `lease_id`, `chunk_id`, `project_id`.  
- Audits: delete, ACL change, snapshot restore.

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× — correct MVP**

```text
MDS: Postgres/etcd/Raft KV with inode + dirent tables
Data: S3/MinIO/GCS
Client: FUSE with write-back + fsync → commit
Locks: exclusive lease row per inode
Snapshots: COW root pointer clone
```

First bottleneck: **MDS CPU + lock** on hot projects; **small-file create**.

**10× — shard & cache**

- Shard key `hash(inode_id)` or subtree.  
- Client attr cache with version.  
- Quota service co-partitioned with project.  
- S3 gateway share same MDS.

**100× — namespace routers + dir shards**

- Routers map path prefixes → MDS sets.  
- Directory buckets; parallel readdir.  
- Dedicated lease managers.  
- Dataset publisher API (immutable).  

**1000× — cells**

```text
org → home cell (mutable metadata)
Cross-cell reads of published datasets via immutable refs + regional replicas
Archive cold metadata; keep hot working sets
Bulk ingest path bypasses per-file RPC where possible
```

### 5.5 ML training & checkpoint specifics

| Pattern | Design |
|---------|--------|
| Dataset epoch reads | Immutable tree; client readahead; local SSD cache |
| Shuffle | Client-side index; avoid MDS per sample |
| Checkpoint | Temp file + fsync + atomic rename |
| Shared write of metrics | Prefer side channel (KV/DB), not FS multi-writer |
| Multi-node sharded ckpt | One directory; N files; barrier then publish marker file |

**Deal-breaker for training:** Using eventually consistent LIST to detect “checkpoint ready.”

### 5.6 S3 gateway semantics mapping

| S3 op | FS mapping |
|-------|------------|
| PUT object | create/truncate + write + commit (+ optional exclusive) |
| GET | open + read chunks |
| LIST | readdir with prefix → cursor |
| DELETE | unlink (+ soft delete) |
| Copy | server-side chunk refcount++ if same store |
| Multipart | staged parts → commit map |

Document where S3 weak listing differs from POSIX readdir caching.

### 5.7 Security & multi-tenancy

- Short-lived mount tokens scoped to project paths.  
- Encryption at rest (object KMS); optional client-side.  
- Cross-project hardlinks disallowed or carefully audited.  
- Rate limits per principal; quarantine runaway clients.

### 5.8 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| One QPS number for data+meta | Wrong capacity plan |
| TTL caches without version | Stale training reads / torn views |
| Dual-write S3 and separate FS | Divergence |
| GC without snap refs | Instant data loss |
| Global single MDS at 100× | Meltdown |
| Active-active mutable dirs | Split brain |
| Quota only on create | Overcommit via append |
| Claiming full POSIX | Interview trap |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Architecture | Split MDS + chunk/object data plane |
| Frontends | FUSE POSIX-ish + S3 gateway |
| Mutable consistency | Exclusive write leases + inode versions |
| Datasets / ckpt | Immutable publish + atomic rename |
| Scale | Shard MDS → routers → cells |
| Quotas | Reserve/commit on create & extend |
| Snapshots | COW metadata + chunk refcounts |

### 6.2 Top risks

1. Underestimating metadata at small-file / listing scale  
2. Cache coherency bugs → silent wrong training data  
3. Lease false expiry → torn writes if fencing weak  
4. GC deleting live snapshot data  
5. Hot directory / hot project noisy neighbor  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Requirements: POSIX vs S3, consistency, ML I/O |
| 5–12 | Split planes; inode/chunk model |
| 12–22 | HLD + lease + rename checkpoint flow |
| 22–32 | Caching, quotas, snapshots |
| 32–40 | Scale 10×/100×/1000×; bandwidth math |
| 40–45 | Failure modes + deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Consistency & POSIX

**Q: Do you provide close-to-open consistency?**  
A: Yes as MVP baseline for mutable files with lease drop on close; for datasets prefer immutable publish. State it explicitly.

**Q: What about mmap shared write?**  
A: Out of MVP or best-effort; true shared mmap coherency is a cluster-FS research problem—don’t pretend.

**Q: Is rename atomic?**  
A: Directory entry CAS on MDS; critical for checkpoints.

**Q: How do readers avoid torn files?**  
A: Never update chunk map in place without version; publish new map or rename new inode.

### 7.2 Metadata plane

**Q: Why not put metadata in object store user xattrs?**  
A: Listing, rename, leases, quotas need low-latency structured store; objects are poor for tree mutations at high QPS.

**Q: Raft vs NewSQL vs etcd?**  
A: etcd for small clusters; sharded Raft/NewSQL for 10×+; cells at 1000×.

**Q: How to shard directories?**  
A: Hash filename into N buckets; keep directory inode as aggregator for counts/mtime approximations.

### 7.3 Caching

**Q: Why is caching chunk_id safe?**  
A: Chunks immutable; new writes → new chunk ids; maps versioned.

**Q: Attr cache danger?**  
A: Stale size/mtime/ACL; mitigate with version checks on open and lease breaks.

**Q: Can we use CDN for training data?**  
A: Yes for immutable public-ish datasets; not for mutable home dirs.

### 7.4 Multi-writer & leases

**Q: Lease length?**  
A: Seconds to tens of seconds with renew; balance false expiry vs failover time.

**Q: What if network blip expires lease while writer continues?**  
A: Fencing token rejects further commits; client must reopen; may lose uncommitted buffers—surface error.

**Q: Byte-range locks?**  
A: Only if product requires; ML checkpoints usually don’t.

### 7.5 Quotas & multi-tenant

**Q: Soft vs hard?**  
A: Soft alerts; hard blocks extend/create; optional grace.  

**Q: Race two writers near quota?**  
A: Atomic reserve in quota ledger with project key.

**Q: Noisy neighbor bandwidth?**  
A: Token buckets at gateway; per-project fair share on chunk gateways.

### 7.6 Snapshots & GC

**Q: How long do snapshots take?**  
A: Metadata COW of roots—seconds for large trees if refcount increments batched; not full data copy.

**Q: GC correctness?**  
A: Refcounts across live+snap; generation barriers; auditor job.

**Q: Can snapshot include in-flight writes?**  
A: Only committed maps; document crash-consistent vs application-consistent.

### 7.7 ML / NVIDIA-flavored

**Q: How to make ImageNet-scale training not kill MDS?**  
A: Immutable dataset, open few shard files, sequential reads, client cache, avoid per-sample open.

**Q: Checkpoint every N steps across 256 GPUs?**  
A: Sharded files + marker; or single writer aggregator; always durable finalize before marking success.

**Q: Compare to Lustre/GPFS/JuiceFS/Alluxio?**  
A: Same split brain of meta vs data; call out lease/consistency and cloud object backend differences.

### 7.8 S3 gateway

**Q: Is LIST strongly consistent?**  
A: Align with MDS; avoid raw eventually consistent bucket LIST as SoT.

**Q: Multipart upload failure?**  
A: Abort cleans parts; no publish without complete.

### 7.9 Multi-region

**Q: Active-active home dirs?**  
A: Avoid. Home cell for mutable metadata; replicate immutable datasets read-only.

**Q: DR?**  
A: Async replicate MDS log + object cross-region; promote with fence epoch.

### 7.10 Performance traps

**Q: Millions of tiny files?**  
A: Packing/compaction, bulk APIs, or discourage pattern; metadata capacity planning.

**Q: fsync storm?**  
A: Group commit on MDS; client coalescing; async checkpoint where product allows.

### 7.11 Security

**Q: Confused deputy via mount?**  
A: Path-scoped tokens; server-side ACL recheck; no trusting client-sent uid alone.

**Q: Encryption keys per tenant?**  
A: KMS envelope per project; rotate with re-encrypt jobs offline.

### 7.12 Interview arithmetic traps

**Q: 1000 nodes × 200 MB/s = ?**  
A: **200 GB/s**, not 200 MB/s cluster. Units matter.

**Q: 100B inodes × 400 B = ?**  
A: **40 TB** metadata raw—plan indexes/RAM accordingly.

### 7.13 Reliability drills

**Q: Kill writer during checkpoint?**  
A: Temp not renamed; previous ckpt remains; no torn final.  

**Q: MDS failover during fsync?**  
A: Client retries; idempotent commit; no ACK until new leader has entry.

### 7.14 Comparison questions

**Q: Why not only S3?**  
A: Atomic dir rename, leases, POSIX tools, efficient tree ops—object alone is awkward.

**Q: Why not only NFS filer?**  
A: Cloud elasticity, EB scale, multi-tenant QoS, object cost model.

### 7.15 “Say this” correctness line

> We never conflate data GB/s with metadata QPS; mutable writes are leased and fenced; checkpoints publish via durable commit + atomic rename; dataset bytes are immutable chunks safe to cache; snapshots are COW with refcounted GC.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- inodes
(inode_id BIGINT PK,
 parent_id BIGINT,
 type SMALLINT,  -- dir/file/symlink
 name TEXT,
 size BIGINT,
 version BIGINT,
 lease_id UUID NULL,
 lease_until TIMESTAMPTZ NULL,
 mode INT,
 owner_id, project_id,
 mtime, ctime,
 UNIQUE(parent_id, name)  -- per dir shard

-- chunk_map
(inode_id, offset, chunk_id, length, checksum)

-- chunks
(chunk_id, pool, size, refcount, sha256)

-- quotas
(project_id, bytes_used, bytes_reserved, bytes_hard, inodes_used, inodes_hard)

-- snapshots
(snap_id, root_inode, project_id, created_at, label)
```

### 8.2 API checklist

- [ ] Mount / unmount (token scoped)  
- [ ] lookup/open/create/read/write/close/fsync  
- [ ] mkdir/unlink/rename  
- [ ] getattr/readdir (cursor)  
- [ ] snapshot create/list/restore  
- [ ] quota get/set  
- [ ] S3: PUT/GET/DELETE/LIST/multipart  
- [ ] admin: lease break, fsck/audit, GC status  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| MDS | Metadata service owning namespace/leases |
| Chunk | Immutable byte object referenced by maps |
| Lease | Exclusive write ownership with fencing |
| COW | Copy-on-write for snapshots / versions |
| Close-to-open | Consistency after writer closes, reader opens |
| Home cell | Single-writer region for mutable metadata |
| Publish | Atomic make-visible of a complete file/tree |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | HA MDS, object data, leases, fsync+rename, quotas |
| 10× | Sharded MDS, attr cache versions, QoS |
| 100× | Dir shards, routers, checkpoint fast path, read caches |
| 1000× | Cells, regional pools, bulk ingest, hierarchical MDS |

### 8.5 Client write path sketch

```text
write(buf):
  buffer in client
  if buffer full: allocate chunk_id → PUT object → local map delta
fsync/close:
  CommitMap(inode, version, deltas, lease_id) → MDS
  MDS: verify lease; durable log; update size/version; ACK
```

### 8.6 Directory sharding sketch

```text
dirent_bucket = hash(name) % B
store key: (dir_inode, bucket, name) → child_inode
readdir: iterate buckets with cursor tokens
mtime/count: approximate aggregator or async rollup
```

### 8.7 Interview “say this” summary (60 seconds)

> Shared cloud FS for multi-tenant ML: metadata plane for tree/leases/quotas/snapshots, data plane for immutable chunks in object storage; FUSE + S3 over one truth; exclusive write leases and atomic rename for checkpoints; aggressive caching of immutable chunks; scale by sharding MDS then cells—never mix GB/s with metadata QPS.

### 8.8 Extra traps

| Trap | Pushback |
|------|----------|
| Full POSIX promise | Subset + document |
| LIST as readiness signal | Use marker/rename |
| Redis-only metadata | Durability/consistency risk |
| Cache without versions | Wrong reads |
| Single global lock file protocol only | Doesn’t scale; leases need server fence |
| 1000 nodes × 200MB/s = 200MB/s | **200 GB/s** |

### 8.9 Reliability test plan

1. Kill client mid-checkpoint → no final rename; old ckpt intact.  
2. Expire lease under write → fenced rejects.  
3. MDS leader failover during fsync → client retry succeeds once.  
4. Snapshot then overwrite → snap bytes unchanged.  
5. GC under load → refcount audit zero data loss.  
6. Quota race → never exceed hard beyond reservation policy.

### 8.10 Observability SLOs

| SLO | Example target |
|-----|----------------|
| open/lookup p99 | < 50ms in-region |
| fsync p99 (small) | < 100ms (+ object RTT) |
| rename p99 | < 50ms |
| Training read sustained | ≥ X GB/s per rack goal |
| Cache hit ratio (hot dataset) | > 80% after warmup |
| Quota reject correctness | 100% enforced |

### 8.11 Related systems map

```text
FUSE / S3 GW → Protocol GW → MDS shards ↔ Quota ↔ Leases
                              ↓
                         Chunk maps
                              ↓
                      Object / chunk stores
                              ↓
                      Snapshot GC / Auditor
```

### 8.12 Consistency decision matrix

| Workload | Recommendation |
|----------|----------------|
| Frozen training dataset | Immutable tree + caches |
| Checkpoint files | Single writer + fsync + atomic rename |
| Home directory edits | Lease + close-to-open |
| Collaborative text | Not this FS—use CRDT doc store |
| Metrics from N ranks | DB/queue side channel |

### 8.13 QoS sketch

```text
per project tokens: metadata_ops/s, GB/s read, GB/s write
gateway admits requests; burst credit
over-limit: delay or EAGAIN; never starve below floor share
```

### 8.14 Soft delete & undelete

```text
unlink → tombstone dirent + grace TTL
GC after TTL if not in snaps
undelete restores dirent if tombstone alive
```

### 8.15 NVIDIA interview bridge lines

- Tie durability to **checkpoint RPO**.  
- Tie caching to **GPU feed rate** and immutable shards.  
- Tie multi-tenant quotas to **shared research clusters**.  
- Admit POSIX subset—interviewers reward honesty.

---

*End of shared cloud filesystem system design.*
