# System Design: Crash-Resilient Filesystem

> **Focus areas:** WAL journaling · Metadata vs data ordering · fsync semantics · Recovery replay · fsck bounds · Copy-on-write snapshots · Checksums · Extent maps · Superblock redundancy  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct crash-consistency invariants, split dissimilar IOPS (metadata journal vs data write vs scrub vs recovery), explicit deal-breakers, Netflix storage / platform 2025–26 interview themes  
> **Interview theme:** Netflix storage — local filesystem that survives power loss without metadata corruption, with bounded mount-time recovery and integrity for multi-TB media volumes

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

Goal: **design a crash-resilient local filesystem** that preserves POSIX-visible durability contracts after sudden power loss, using **write-ahead logging (WAL) for metadata**, explicit **data-before-metadata ordering**, **fsync semantics**, **bounded recovery replay**, optional **copy-on-write snapshots**, and **checksums** over metadata and data blocks — at Netflix-scale volumes from workstation encodes through multi-PB origin storage nodes.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Single-node / single-volume FS crash consistency | Distributed GFS / S3 object store |
| Recovery | Journal replay + bounded fsck | Full backup restore only (sibling) |
| Scope | Block device → VFS → apps | RAID controller firmware |
| Snapshots | CoW block-level (optional) | Continuous remote replication |
| Integrity | Inline checksums + scrub | End-to-end app-layer Merkle only |
| Client | Kernel VFS + FUSE class | Browser / mobile client |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Crash model? | Power loss / kernel panic anytime; no torn 512B guarantee on NVMe without PI | Assume sector atomicity ≥ 4 KiB or use checksum detect |
| F2 | Durability contract? | `fsync(fd)` persists file data + enough metadata to find it after reboot | Data blocks before committing inode size/extents |
| F3 | Metadata updates? | create / unlink / rename / truncate / alloc free | Single journal TX per logical operation |
| F4 | File layout? | Large sequential media + small sidecar metadata | **Extent maps** with run-length encoding |
| F5 | Directory structure? | Millions of files per volume | B+tree or HTree directories; journaled |
| F6 | Snapshots? | Point-in-time for encode checkpoints | **CoW** on block alloc; refcount tree |
| F7 | Corruption detection? | Silent bit rot unacceptable | **Checksum** per metadata block + per data extent |
| F8 | Recovery at mount? | Automatic replay; no manual fsck for clean crashes | WAL replay + **bounded fsck** for orphan blocks |
| F9 | fsync API? | POSIX `fsync`, `fdatasync`, `sync` | Separate data-only vs full metadata flush paths |
| F10 | Hard links / reflinks? | Hard links MVP; reflink = CoW share | inode `nlink`; shared extent refcounts |
| F11 | Max volume size? | 100 TB baseline → PB class at 1000× | 64-bit block pointers; extent map depth |
| F12 | Online scrub? | Background verify without unmount | Read checksums; quarantine bad blocks |
| F13 | Superblock? | Must survive primary superblock corruption | **Redundant superblocks** + CRC |
| F14 | TRIM / discard? | SSD longevity on origin nodes | Journaled free-extent + async TRIM |

**MVP functional scope (lock with interviewer):**

1. Format volume with primary + backup superblocks, block size 4 KiB (configurable 4K/64K).
2. **Extent-map inodes** for data; no indirect block chains for files > 1 extent in MVP deep dive.
3. **WAL journal** for metadata transactions: alloc, free, inode, dirent, refcount.
4. **Ordering rule:** dirty data blocks flushed before journal commit that exposes new extents.
5. Mount: read superblock → if `needs_recovery`, **replay journal** → mark clean.
6. `fsync`: flush file data → flush inode + extent metadata via journal commit.
7. Per-block **checksums** (CRC32c or xxHash) stored in metadata or inline footer.
8. **Bounded fsck:** scan orphan blocks in free-space bitmap window only; no full-tree walk on every mount.
9. Metrics: mount recovery time, journal wrap rate, scrub errors, fsync p99.

**Out of MVP (explicitly defer):**

- Active-active multi-writer on one volume (cluster FS sibling)
- Full POSIX ACLs / SELinux xattrs day one
- Encryption at rest inside FS (may defer to LUKS below FS)
- Cross-volume deduplication
- Guaranteed sub-millisecond fsync on HDD (state media class)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Metadata write IOPS? | Hot on small-file workloads | Baseline 2K metadata ops/s; scale table |
| N2 | Sequential write BW? | Encode / ingest saturates disk | ≥ 80% raw device BW for large IO |
| N3 | fsync latency? | Small journal commits | p99 < 5–15 ms NVMe; < 50 ms SATA SSD |
| N4 | Mount recovery time? | Operators tolerate seconds, not hours | Replay ≤ 30 s for 256 MB journal at baseline |
| N5 | fsck bound? | No unbounded full scan on clean mount | Full fsck only on `UNCLEAN` or checksum mismatch |
| N6 | Space amplification? | Snapshots + CoW overhead | ≤ 10–20% metadata overhead baseline |
| N7 | Correctness | No exposed unallocated blocks after crash | Crash consistency invariants (§5.1) |
| N8 | Scale | Volume size + IOPS through 1000× | See §1.4 |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. **Create + write + close:** alloc blocks → write data → journal inode extents → commit → file visible after reboot.  
2. **Append large mezzanine file:** extend extent run; single journal commit for tail extent growth.  
3. **Rename atomic:** journal new dirent + unlink old in one TX; no orphan name on crash.  
4. **fsync after encode frame flush:** data on platter before inode size visible to readers.  
5. **Snapshot:** CoW at block granularity; parent and child share unmodified extents.  
6. **Clean unmount:** checkpoint journal; set superblock `clean=1`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Crash after data write, before journal commit | Old inode visible; new data in orphan blocks reclaimed by bounded fsck |
| Crash after journal commit, before checkpoint | Replay reapplies TX idempotently; reach committed state |
| Torn journal block | Checksum fail → stop replay; restore backup superblock / alternate journal copy |
| Primary superblock corrupt | Mount from **redundant superblock** copy; verify CRC + serial |
| Double fsync same file | Idempotent commit if no new dirty data |
| `fdatasync` vs `fsync` | datasync skips atime/mtime if policy allows; still orders data before exposing size |
| Snapshot delete while read open | Refcount delay free until last reader closes |
| Journal full during burst metadata | Throttle or checkpoint early; never silent drop |

### 1.4 Scales (Progressive)

**Volume size and IOPS — baseline = single origin encode node (~10 TB NVMe, mixed workload).**

| Metric | Baseline (1×) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Volume capacity | 10 TB | 100 TB | 1 PB | 10 PB |
| Files / volume | 10 M | 50 M | 200 M | 1 B |
| Peak random read IOPS | 50 K | 500 K | 5 M | 50 M |
| Peak random write IOPS | 10 K | 100 K | 1 M | 10 M |
| Metadata journal ops / s | 2 K | 20 K | 200 K | 2 M |
| Sequential write BW | 2 GB/s | 4 GB/s | 8 GB/s | 16 GB/s+ |
| Journal size | 256 MB | 1 GB | 4 GB | 16 GB |
| Snapshot count (active) | 4 | 16 | 64 | 256 |
| Scrub throughput | 100 MB/s | 300 MB/s | 1 GB/s | 4 GB/s |
| Mount replay budget | 15 s | 30 s | 60 s | 120 s (parallel replay) |

**Split classes:** metadata journal commit ≠ data page cache flush ≠ scrub read ≠ snapshot CoW ≠ recovery replay.

**What each jump forces:**

- **10×:** Group commit journal; larger extent runs; checkpoint thread; backup superblock on alternate span.  
- **100×:** Sharded allocation groups (block groups); per-CPU journal buffers; parallel scrub workers; snapshot refcount btree.  
- **1,000×:** Allocation regions with independent journals; metadata tier on fast NVMe + data on QLC; hardware offload checksums; approximate lazy fsck with full verify offline.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like **media origin / encode farm**: large sequential writes dominate; fsync on manifest sidecars and segment boundaries.  
- Underlying device exposes 512e or 4Kn sectors; FS block ≥ 4 KiB.  
- Single writer per volume (no shared-disk VMFS).  
- Sibling docs: file backup, CDN origin, video streaming storage tier.

**Scope statement:**

> Design a **crash-resilient local filesystem** with WAL metadata journaling, strict data-before-metadata ordering, POSIX fsync semantics, extent-map inodes, redundant superblocks, checksums, optional CoW snapshots, bounded mount recovery via journal replay, and fsck that runs in bounded time — scaling volume size and IOPS 10× / 100× / 1,000× with explicit split of metadata vs data paths.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Block and metadata footprint

```text
Block size B = 4096 B
Volume size V = 10 TB (baseline)
Blocks N = V / B ≈ 2.73 × 10^9 blocks

Inode size ≈ 256 B (extent map header + inline extents)
If avg file size 1 MB → ~10 M files
Inode table ≈ 10 M × 256 B ≈ 2.5 GB (plus btree/dir index overhead ~2× → ~5 GB metadata class)
```

At **100×** (1 PB, 200 M files): inode + dir index → **hundreds of GB** metadata — must not scan all on mount.

### 2.2 Extent map efficiency

```text
Large mezzanine file 50 GB sequential → ideally 1–3 extent runs
Small sidecar JSON 4 KB → 1 block, 1 extent

Extent record ≈ 16 B (start_lba, length) in inode or leaf block
50 GB / 4 KB = 13.1 M blocks — too many for inline inode
→ extent tree: fanout 500 × 4 KiB block → depth 2 covers 500 × 500 × 4K ≈ 1 GB per leaf level step
For 50 GB: depth 2–3 extent tree nodes (journaled)
```

**Deal-breaker:** classic ext4 triple-indirect for 50 GB file → metadata read amplification on random write tail.

### 2.3 Journal sizing and replay time

```text
Journal J = 256 MB baseline
Metadata record avg size r ≈ 256 B (alloc + inode patch + dirent)
Records per full journal ≈ J / r ≈ 1 M records

Replay IO: sequential read J at 500 MB/s NVMe → ~0.5 s read
Apply CPU: 1 M ops × 2 µs ≈ 2 s
Total replay ≈ 2–5 s << 15 s budget
```

At **100×** metadata burst 200 K journal ops/s → checkpoint every 1–2 s or group-commit batch 32–128 ops.

### 2.4 fsync frequency impact

```text
Sidecar manifest fsync every 1 s during encode, 1 KB write:
  Without group commit: 1 fsync/s × 8 ms = 8 ms/s CPU + NVMe flush amp
  With group commit (8 ms window): amortize flush across clients

1000 encoders × 1 fsync/s = 1000 fsync/s → journal must batch or per-encoder queues
```

### 2.5 Checksum storage overhead

```text
CRC32c per 4 KiB block → ~0.1% overhead; 10 TB volume ≈ 10 GB checksum storage
```

### 2.6 IOPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Data read (random) | 50 K | 5 M | 50 M | page cache + readahead |
| Data write (random) | 10 K | 1 M | 10 M | delayed alloc |
| Metadata journal commit | 2 K | 200 K | 2 M | group commit essential |
| fsync / fdatasync calls | 500 | 5 K | 50 K | encoder manifests |
| Recovery replay | — (mount) | 50 K apply/s | parallel | not steady state |
| Scrub read | 25 K | 250 K | 2.5 M | background cap |
| Snapshot CoW break | 1 K | 10 K | 100 K | on write to shared block |

### 2.7 Latency budget (fsync path)

| Stage | Budget (NVMe) |
|-------|---------------|
| Copy dirty data to flush list | 0.5–1 ms |
| Device write data blocks | 1–4 ms |
| Journal write + flush | 1–5 ms |
| Apply checkpoint (async) | off hot path |
| **fsync total** | **≤ 5–15 ms p99** |

HDD class: 20–50 ms p99 — steer hot metadata to SSD journal device.

### 2.8 Critical bottlenecks

1. **Journal flush serialization** — one NVMe flush queue without group commit.  
2. **Extent tree depth** on fragmented large files — metadata read amp.  
3. **Single global alloc bitmap lock** at 100× random create/delete.  
4. **Unbounded replay** if journal never checkpoints across months of crash.  
5. **Full fsck** scanning 1 B files on billion-file volume.  
6. **Snapshot refcount hot blocks** — every write breaks CoW on shared popular block (rare for media).

---

## 3. High-Level Design

### 3.1 Layering

```text
Application (encoder, packager, origin)
    ↓ POSIX (open/write/fsync/rename)
VFS (Linux kernel)
    ↓
NetFS driver (this design)
    ├── Page cache hooks (dirty tracking)
    ├── Journal subsystem (WAL)
    ├── Allocation groups (free space)
    ├── Extent map + directory btree
    ├── Checksum / scrub engine
    └── Snapshot / CoW refcount layer
    ↓
Block device (NVMe / SATA SSD / PMem optional journal)
```

### 3.2 On-disk entities

| Entity | Role |
|--------|------|
| `Superblock` | Volume UUID, block size, feature flags, journal location, clean/dirty state, CRC |
| `Superblock copy` | Redundant copies at fixed alternate offsets |
| `Journal` | Circular WAL of typed metadata records |
| `Inode` | mode, size, timestamps, extent map root or inline extents |
| `Extent tree node` | keyed by file offset → physical run |
| `Directory block` | B+tree: name hash → inode number |
| `Block bitmap / alloc tree` | free / allocated / snapshot-reserved |
| `Refcount block` | CoW: physical block → snapshot + file refs |
| `Checksum sector` | optional aggregate per alloc group |

### 3.3 Crash consistency model

**Golden rule:** *No metadata pointing to a block is committed until all dependent data blocks for that commit epoch are durable.*

| Operation | Order |
|-----------|-------|
| create write | data blocks → journal(inode alloc + extents) → commit |
| truncate shrink | journal (free extents) → commit → optionally zero |
| rename | journal (dirent ops) single TX → commit |
| unlink | journal (decrement nlink, free if 0) → commit |
| snapshot create | journal (root refcount bump) → commit; no data copy |

After crash, either **pre-TX** or **post-TX** state — never pointing at garbage.

### 3.4 Journal transaction shape

```text
TX begin (tx_id, timestamp)
  ALLOC block 1001..1008
  INODE 42 patch: size 32768, extent [1001,8]
  DIRENT add ("manifest.json" → inode 42)
TX commit (tx_id, crc)
```

Replay: scan journal for complete commits only; partial tail discarded.

### 3.5 fsync semantics

| API | Guarantees |
|-----|------------|
| `fdatasync` | File **data** + metadata required to read that data (size, extents) |
| `fsync` | Above + inode metadata (atime/mtime per policy) |
| `sync()` | Global flush — expensive; background `syncfs` preferred |

Implementation:

```text
fdatasync(fd):
  flush dirty pages for inode
  wait data device writes
  journal commit inode fields needed for read(fd)
  return
```

### 3.6 Superblock redundancy

```text
Primary superblock @ block 0
Backup copies @ blocks: N/4, N/2, 3N/4 (spaced to survive localized corruption)
Each copy: same serial, monotonic write_generation, CRC32c
Mount: try copies in order; pick highest valid generation
Update: write backup first, then primary (or two-phase commit flag)
```

### 3.7 Snapshots (CoW)

```text
snap = create_snapshot()
  for each alloc group: mark refcount baseline
  new writes to shared block B:
    if B refcount > 1: allocate B', copy, dec old ref, point inode to B'
```

Delete snapshot: decrement refcounts; free blocks when ref hits 0.

### 3.8 Checksums

- **Metadata blocks:** CRC in block header; verify on every read.  
- **Data blocks:** footer CRC or external tree keyed by physical block id.  
- **Scrub:** sequential read → verify → alert + remap if redundant copy exists.

### 3.9 fsck bounds

| Mode | When | Bound |
|------|------|-------|
| Replay only | `needs_recovery` after crash | O(journal size) |
| Orphan block reclaim | post-replay | O(journal orphan list) not O(files) |
| Full fsck | admin flag / repeated checksum fail | O(blocks) — offline only at 1000× |
| Lazy verify | background scrub | rate-limited |

Never run O(all files) walk on every mount at billion-file scale.

### 3.10 Failure policy

| Failure | Policy |
|---------|--------|
| Journal checksum error | Stop mount; prompt admin; try backup journal ring |
| Data checksum error | EIO to reader; scrub quarantine block |
| Superblock mismatch | Select valid redundant copy |
| Journal full | Force checkpoint; backpressure writers |
| Recovery exceeds budget | Continue in background `RECOVERING` read-only mode (policy) |

### 3.11 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Metadata | WAL journal, not in-place update |
| Data ordering | Write data before commit metadata |
| Large files | Extent maps + tree |
| Snapshots | Block CoW with refcounts |
| Integrity | CRC32c baseline; SHA256 optional scrub |
| Recovery | Replay-first; bounded orphan reclaim |
| Scale | Allocation groups sharded at 100× |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+   write/read/fsync   +-------------------+
|  Encoder    |--------------------->| VFS / NetFS       |
|  App        |                      +---------+---------+
+-------------+                                |
                    +--------------------------+---------------------------+
                    |                          |                           |
                    v                          v                           v
           +--------+--------+       +---------+---------+       +---------+---------+
           | Page cache      |       | Journal (WAL)     |       | Extent / Dir      |
           | dirty tracking  |       | group commit      |       | btree + alloc grp |
           +--------+--------+       +---------+---------+       +---------+---------+
                    |                          |                           |
                    v                          v                           v
           +--------+--------+       +---------+---------+       +---------+---------+
           | Data block IO   |       | Journal flush     |       | Checksum / scrub  |
           | (NVMe queue)    |       | (barrier/FUA)     |       | background        |
           +--------+--------+       +---------+---------+       +---------+---------+
                    |                          |
                    v                          v
           +--------+---------------------------------------------------------+
           |                     Block device (NVMe)                          |
           |  [Superblock x4] [Journal ring] [Data] [Metadata] [Refcount]     |
           +--------+---------------------------------------------------------+
```

### 4.2 Sequence: create file + write + fsync

```text
App→VFS: open(O_CREAT), write(data), fsync
VFS→NetFS: allocate blocks via alloc group
NetFS→Device: write data blocks (async)
App→NetFS: fsync
NetFS: wait data writes complete
NetFS→Journal: TX{alloc, inode extents, size}
NetFS→Device: journal write + FLUSH/FUA
NetFS→Journal: mark commit
NetFS→App: fsync OK
(checkpoint thread later copies to home metadata locations)
```

### 4.3 Sequence: crash + mount recovery

```text
Boot→Mount: read superblock copies → pick valid
Mount: sees clean=0, journal_tail
Mount→Journal: scan commits from last checkpoint
For each committed TX: idempotent apply (alloc, inode, dirent)
Mount→Orphan reclaim: free blocks allocated but not in committed inode
Mount→Superblock: set clean=1, bump generation
Mount→App: volume ready (RO→RW after replay done)
```

### 4.4 Sequence: snapshot CoW write

```text
App writes block B shared with snapshot S
NetFS: refcount(B) > 1
NetFS→Alloc: allocate B'
NetFS→Device: read B, write B'
NetFS→Journal: TX{inode extent B→B', refcount dec B, inc B'}
NetFS→Device: journal commit
App write completes to B' (parent snapshot still reads B)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Atomic metadata commits** via complete journal TX records only.  
2. **Data before metadata** for any block becoming reachable.  
3. **Idempotent replay** — applying same committed TX twice is safe.  
4. **No double-free** — free only after journal commit decrements refcount.  
5. **Superblock CRC** detects torn primary; fall back to redundant copy.  
6. **Checksum fail closed** — return EIO, not silent garbage.  
7. **Snapshot isolation** — readers of snapshot never see post-snapshot writes.  
8. **Bounded mount work** — replay O(journal); orphan reclaim O(uncommitted alloc).

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Crash mid-data-write | Partial block checksum fail or old content visible |
| Crash mid-journal-write | TX incomplete → ignored on replay |
| Crash post-commit pre-checkpoint | Replay applies committed TX |
| Both superblocks corrupt | Volume offline; restore from backup (out of FS scope) |
| Journal ring wrap before checkpoint | Stall writes or force checkpoint — never overwrite uncheckpointed |

### 5.2 WAL record types

| Type | Payload |
|------|---------|
| `TX_BEGIN` | tx_id |
| `BLOCK_ALLOC` | group, start, count |
| `BLOCK_FREE` | group, start, count |
| `INODE_UPDATE` | inode_id, diff blob (size, extents delta) |
| `DIRENT_ADD/DEL` | dir_inode, name, child_inode |
| `REFCOUNT_ADJ` | block, delta |
| `TX_COMMIT` | tx_id, crc |

Checkpoint: flush live metadata trees to fixed on-disk locations; truncate journal.

### 5.3 Metadata vs data ordering (deep)

**Why order matters:** if inode size committed before data durable, after crash reader sees size > 0 but reads stale/zero block → **uninitialized data exposure** (security + correctness).

```text
Wrong:
  journal commit size=4096 → crash → read returns old disk garbage for new block

Right:
  write new block 4096 bytes → flush
  journal commit size=4096 + extent
```

**append optimization:** allocate extent lazily (delayed allocation) but never commit until flush.

**rename:** only metadata — order is journal atomicity, not data.

### 5.4 Group commit

```text
window = 1–8 ms OR batch = 64 TX
collect ready commits → single FLUSH
amortizes NVMe round-trip across many fsync callers
trade: adds up to window latency vs 10× throughput
```

At 100×: per-CPU journal staging buffers → single serializing flush thread.

### 5.5 Extent map mechanics

Inline up to 4 extent runs in inode; overflow to extent B+tree keyed by logical offset. Coalesce adjacent runs on sequential append; split on rare random overwrite. Directories use same extent machinery.

### 5.6 fsck bounds (algorithm sketch)

```text
function mount_recovery():
  replay_journal()
  orphans = journal.alloc_list - committed_extents
  for b in orphans: free(b)   # O(orphans) typically << O(blocks)
  verify_superblock_consistency()
  if checksum_fail_flags: schedule offline full fsck
  mark_clean()

function offline_full_fsck():  # admin only at scale
  walk alloc bitmap vs inode/extent scan
  rebuild refcount if snapshot enabled
  O(blocks + files) — run on replica or maintenance window
```

**Interview line:** mount fsck is **replay + orphan reclaim**, not traverse all inodes.

### 5.7 Copy-on-write snapshots

Block-granularity CoW: snapshot create is O(1) metadata. First write to shared block allocates copy, decrements old ref. Delete snapshot decrements refcounts; free when zero. Write amp: +1 read + 1 write on first post-snap write to shared block.

### 5.8 Checksum strategy

CRC32c on metadata blocks (every read), data block footers (scrub/read), journal records (replay), superblock (mount). Optional SHA256 weekly deep scrub.

### 5.9 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Single alloc group; 256 MB journal; inline extents |
| 10× | 4–16 alloc groups; group commit; 1 GB journal |
| 100× | 256 alloc groups; parallel scrub; extent tree cache |
| 1,000× | Volume fleet sharding; per-group journals; PMem journal tier |

### 5.10 Exact algorithm: journal commit

```text
function journal_commit(tx):
  assert all data blocks in tx are durable
  append TX_BEGIN(tx.id)
  for op in tx.ops: append op
  append TX_COMMIT(tx.id, crc(all))
  device_flush(journal_region)
  wake waiting fsync callers
  enqueue checkpoint if journal_used > threshold
```

### 5.11 Exact algorithm: replay

```text
function replay():
  last_complete = scan_for_last_valid_commit()
  for tx in journal up to last_complete:
    if tx already applied (generation check): continue
    apply_alloc_free(tx)
    apply_inode_patches(tx)
    apply_dirents(tx)
    apply_refcounts(tx)
  discard partial tail tx
```

### 5.12 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Update inode in place without journal | Torn fields → corrupt extent tree |
| Commit metadata before data flush | Uninitialized data read after crash |
| Full inode walk every mount | Hours on billion-file PB volume |
| Single superblock | One bad sector bricks volume |
| No checksums | Silent bit rot in mezzanine masters |
| Infinite journal without checkpoint | Replay unbounded |
| Snapshot without refcount | Double-free or leak |
| `fsync` returns before FLUSH | POSIX violation; data loss |
| Indirect blocks for 100 GB files | Metadata IO meltdown on tail write |

### 5.13 Progressive scale deep dive

| Scale | Volume / IOPS | Key changes |
|-------|---------------|-------------|
| 1× | 10 TB / 10 K w IOPS | Single journal; inline extents; replay < 15 s |
| 10× | 100 TB / 100 K | 16 alloc groups; 1 GB journal; group commit; backup superblocks |
| 100× | 1 PB / 1 M | 256 alloc groups; parallel replay/scrub; sharded volumes |
| 1,000× | 10 PB / 10 M | Fleet of 1000 volumes; PMem journal; lazy fsck; offline full fsck on replicas |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Crash model | Power loss anytime; sector ≥ 4 KiB atomic or checksum detect |
| Metadata durability | WAL journal with TX commit + replay |
| Ordering | Data blocks durable before metadata commit |
| fsync | Flush data → journal inode/extents → device FLUSH |
| Layout | Extent maps + directory B+tree |
| Integrity | CRC32c metadata + data; scrub background |
| Recovery | Replay journal + bounded orphan reclaim |
| fsck | Full scan offline only; not mount hot path |
| Snapshots | Block CoW + refcounts |
| Superblock | Multiple redundant copies + generation + CRC |
| Scale | Alloc groups; 1000× = fleet of volumes |

### 6.2 Risks

1. Group commit window adds fsync latency jitter  
2. Fragmentation inflates extent tree depth on mixed workloads  
3. Journal device failure if split — mitigated by ring on same volume + backup  
4. Snapshot retention → CoW space explosion  
5. Billion-file full fsck if ops mistakenly triggers online full scan  
6. Refcount bugs → double-free (catastrophic) — heavy testing + fuzz replay  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: local FS; crash model; POSIX fsync |
| 5–15 | WAL + ordering diagram; data before metadata |
| 15–25 | Extent maps; superblock redundancy; checksums |
| 25–35 | Recovery replay; bounded fsck vs full fsck |
| 35–45 | CoW snapshots; scale table; deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 WAL, ordering, fsync

**Q: Why journal metadata instead of CoW everything?**  
A: Full CoW (ZFS/btrfs) adds metadata write amp; hybrid **journal metadata + extent data** fits large sequential media. Data journaling alone blows up journal size at 2 GB/s ingest.

**Q: rename() / truncate crash consistency?**  
A: Single journal TX — rename appears or not; truncate-up zeros/discards before size commit.

**Q: fdatasync vs fsync?**  
A: `fdatasync` commits data + size/extents; may skip atime. Both require data durable before metadata commit. Map commit to NVMe FLUSH/FUA.

**Q: mmap + msync?**  
A: `msync(MS_SYNC)` same ordering as fsync for mapped pages.

### 7.2 Recovery and fsck

**Q: How long can replay take?**  
A: O(journal size), not volume size — cap with 256 MB–4 GB ring + checkpoint.

**Q: Idempotent replay?**  
A: TX id + inode generation prevents double-apply; partial tail TX discarded.

**Q: When full fsck?**  
A: Metadata root checksum fail, admin flag, unknown superblock — **not** normal crash. e2fsck on 1 B files = hours; mount uses replay + orphan reclaim only.

### 7.3 Snapshots, extents, checksums

**Q: snapshot vs hard link?**  
A: Snapshot freezes tree view; hard link shares inode. Writable snap = CoW branch.

**Q: Why extents over indirect blocks?**  
A: 50 GB file = 1–3 metadata reads vs deep indirect chain on tail writes.

**Q: CRC vs SHA256?**  
A: CRC32c on hot path; SHA256 optional deep scrub. Inline footer vs checksum tree trade storage layout vs flexibility.

**Q: Superblock redundancy?**  
A: 3–4 spaced copies; write backups then primary with monotonic generation + CRC.

### 7.4 Comparisons and Netflix context

**Q: vs ext4/xfs/ZFS?**  
A: ext4/xfs have journals but interview tests whether you articulate **data-before-metadata**, extent maps, bounded fsck, and checksum/scrub explicitly. ZFS bundles invariants; custom design proves you understand them.

**Q: Why local FS if S3 exists?**  
A: Encode/origin nodes need low-latency **fsync** on segment manifests and mezzanine staging before upload.

**Q: vs backup sibling doc?**  
A: Crash consistency ≠ off-site backup; snapshots feed incremental backup.

### 7.5 Interview traps

| Trap | Pushback |
|------|----------|
| Skip fsync for speed | Violates durability; lose segment boundaries |
| fsck every boot | Journal replay; bound mount work |
| Metadata before data | Uninitialized read vulnerability |
| One lock / one IOPS number | Alloc groups; split data/metadata/scrub |
| Checksum in app only | FS read still returns rot |
| Indirect blocks for 100 GB files | Metadata IO meltdown |

### 7.6 Metrics that matter

**Q: What do you page on?**  
A: `scrub_errors > 0`; mount replay > SLO; journal checkpoint lag > 5 min; superblock fallback event; CoW space spike from snapshot retention.

---

## 8. Appendices

### A1. Superblock layout (sketch)

```text
Superblock {
  magic: 0x4E455446  // "NETF"
  uuid: 128-bit
  block_size: u32
  total_blocks: u64
  feature_flags: u64
  journal_start: u64
  journal_len_blocks: u32
  clean: u8
  needs_recovery: u8
  write_generation: u64
  num_alloc_groups: u32
  checksum: crc32c
}
```

### A2. Inode sketch

```text
Inode {
  mode, uid, gid, nlink
  size: u64
  atime, mtime, ctime
  inline_extents[4]: {logical_off, phys_start, len}
  extent_root_block: u64  // 0 if inline sufficient
  flags: SNAPSHOT_PIN, IMMUTABLE, ...
  inode_crc: u32
}
```

### A3. Journal TX example (hex-ish)

```text
TX_BEGIN id=9001
  BLOCK_ALLOC grp=3 start=880001 count=8
  INODE 42 size=32768 extents+=[[880001,8]]
  DIRENT_ADD dir=10 name="seg_0042.m4s" inode=42
TX_COMMIT id=9001 crc=0xA1B2C3D4
```

### A4. Launch checklist

- [ ] Data-before-metadata ordering verified by crash injection (pull power)  
- [ ] Replay idempotency fuzz tested  
- [ ] Superblock redundancy failover tested  
- [ ] fsync p99 on target NVMe documented  
- [ ] Mount replay SLO on max journal fill  
- [ ] Snapshot CoW refcount leak test  

### A5. Glossary

| Term | Meaning |
|------|---------|
| WAL | Write-ahead log — journal before applying metadata |
| Extent | Contiguous run of physical blocks |
| CoW | Copy-on-write — duplicate block on first write after snap |
| FLUSH/FUA | Force persistence through device cache |
| Orphan block | Allocated but not referenced by committed metadata |
| Alloc group | Sharded free-space region reducing lock contention |
| Checkpoint | Copy journaled metadata to home location; truncate journal |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| fsck every mount | Use journal replay; bound work |
| Metadata before data | Uninitialized read vulnerability |
| No superblock backup | Single point of corruption |
| Journal unbounded | Checkpoint + sized ring |
| Ignore fdatasync | Still must commit size/extents |
| Single IOPS number | Split data/metadata/scrub/recovery |

### A7. Reliability test plan

1. Power loss after data write, before commit → old file size visible.  
2. Power loss after commit → new file visible after replay.  
3. Corrupt journal tail / primary superblock → discard partial TX; mount backup superblock.  
4. Duplicate replay → no double alloc.  
5. Snapshot + write → parent reads old block; scrub detects flipped bit → EIO.

### A8. 60-second summary

> A **crash-resilient filesystem** journals **metadata in a WAL**, never commits inode/extents until **data blocks are durable**, implements POSIX **fsync/fdatasync** via flush + journal commit, uses **extent maps** for large media, **redundant superblocks + CRC**, **checksums** with background scrub, **bounded mount recovery** by **replay** and orphan reclaim (not full fsck), optional **CoW snapshots**, scaling via **alloc groups** and at 1000× a **fleet of volumes** — split **metadata IOPS** from **data IOPS** in all capacity math.

### A9. Related systems map

```text
Encoder → VFS → NetFS → NVMe local volume
NetFS snapshots → Backup agent (sibling file-backup doc)
Verified segments → Object store / CDN origin upload
Scrub alerts → Storage ops / replace drive
Offline full fsck → Maintenance orchestrator on detached volume
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| fsync p99 (NVMe) | < 15 ms |
| Mount replay (256 MB journal) | < 15 s |
| Scrub coverage | 100% volume / 30 days |
| Metadata checksum fail rate | 0 tolerated without quarantine |
| Superblock fallback events | < 1 / year / volume |
| Snapshot create | < 100 ms |

### A11. Worked numeric example

```text
File seg.m4s grows by 8 blocks (32 KiB)
1. Alloc blocks 1001–1008 (journaled in TX but not committed)
2. Write 32 KiB to device
3. fsync: flush data → journal INODE size=32768 extents=[1001,8] → COMMIT → FLUSH
Crash after step 3: replay sees commit → file readable 32 KiB
Crash after step 2 only: no commit → file shows old size; blocks 1001–1008 orphan → reclaim
```

### A12. Ownership

| Concern | Owner |
|---------|-------|
| NetFS driver | Storage Platform |
| Encode fsync policy | Media Encoding |
| Scrub / replace drive | Storage SRE |
| Snapshot retention policy | Backup / DR (sibling) |
| Hardware NVMe qualification | Data Center Eng |

### A13. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | WAL + ordering + replay + redundant superblock |
| 10× | Group commit + alloc groups + 1 GB journal |
| 100× | Parallel scrub/replay + snapshot refcounts |
| 1,000× | Volume fleet + PMem journal option + lazy fsck |

### A14. Naive design comparison

| Naive | Why it fails |
|-------|--------------|
| In-place metadata update | Torn inode on crash |
| fsync without FLUSH | Data in drive cache lost on power loss |
| Full tree walk mount fsck | Billion files = hours downtime |
| Single superblock | One sector error unmountable |
| No checksums | Silent rot in mezzanine |
| Indirect blocks for huge files | Metadata IO on every tail write |

### A15. On-call cheat sheet

1. Check `mount_replay_seconds` spike → journal checkpoint stuck?  
2. Check `journal_utilization` → force checkpoint if > 90%.  
3. `scrub_errors` → identify LBA, replace drive if recurring.  
4. Superblock fallback event → plan volume image verify.  
5. CoW space growth → snapshot retention trim.  
6. fsync p99 burn → widen group commit or dedicate journal NVMe.

### A16. Sample debug record

```text
{
  "volume_uuid": "a1b2-...",
  "mount_generation": 8842,
  "replay_tx_count": 1247,
  "replay_seconds": 3.2,
  "orphan_blocks_reclaimed": 16,
  "superblock_source": "backup_copy_2",
  "journal_used_mb": 188
}
```

### A17. Cost worksheet

```text
metadata_GB ≈ file_count × 512 B × index_overhead(2×)
journal_NVMe_GB ≈ peak_metadata_ops × record_size × checkpoint_interval
scrub_CPU ≈ volume_TB × 1024 / scrub_days / 86400 × verify_cost
cow_overhead_TB ≈ snapshot_retention_days × daily_change_rate × volume_TB
```

### A18. Explicit non-goals

- Replacing S3 for cold archive  
- Byzantine fault tolerance across nodes  
- POSIX full ACL + SELinux complete parity day one  
- Guaranteed zero orphan blocks without replay (orphans reclaimed, not prevented)  
- Single monolithic 10 PB filesystem without horizontal volume split  

---

*End of document — Netflix system design interview prep.*
