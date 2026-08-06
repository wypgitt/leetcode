# System Design: Scalable File Backup (Incremental + Block Dedup)

> **Focus areas:** Content-defined chunking · Block-level deduplication · Incremental snapshots · Filesystem primitives (hard links, reflinks, xattrs) · Manifest immutability · Restore correctness · Multi-tenant isolation  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit dedup trade-offs, split dissimilar QPS (scan vs upload vs restore), deal-breaker gallery, Netflix infra / platform interview themes  
> **Interview theme:** Netflix — backup billions of files and terabytes of creative assets without storing every byte twice, while keeping restore fast and auditable

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

Goal: **durable, space-efficient backup** of file trees using **filesystem-native primitives**—incremental snapshots that only store changed content, with **block-level deduplication** so identical bytes are stored once across files, versions, and tenants where policy allows.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Backup + restore file trees with dedup | Full disaster recovery orchestration (sibling) |
| Granularity | Block/chunk level + file metadata | Whole-file copy only |
| Dedup scope | Global pool per backup domain (policy) | Cross-tenant dedup without isolation review |
| Transport | Agent scan + upload; optional FUSE mount | Real-time sync / Dropbox clone |
| Consistency | Point-in-time snapshot per job | Continuous byte-level replication |
| Storage | Object store + local chunk cache | Tape-only cold archive (defer) |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is backed up? | Directories on servers, artist workstations, build artifacts | Agent with include/exclude rules |
| F2 | Backup type? | Full initial + incremental forever | Snapshot chain + manifest diff |
| F3 | Dedup level? | Block/chunk (4–64 MiB class) not only whole file | CDC + content hash index |
| F4 | Restore granularity? | Single file, directory subtree, full machine | Manifest walk + block fetch |
| F5 | Retention? | 30d daily, 12 weekly, 7 yearly (example) | GC of unreferenced blocks |
| F6 | Encryption? | At rest per tenant; keys in KMS | Block ciphertext; no cross-tenant dedup if keys differ |
| F7 | Integrity? | Detect bit rot; verify on restore | Hash per block + manifest Merkle |
| F8 | Multi-version? | Keep immutable snapshots; no overwrite | Copy-on-write manifests |
| F9 | Concurrency? | Many agents, one backup domain | Upload idempotency by block hash |
| F10 | Bandwidth? | Throttle; resume partial uploads | Chunk upload state machine |
| F11 | Metadata? | mtime, mode, xattrs, symlinks | Separate metadata blob per snapshot |
| F12 | Delete handling? | Tombstone in manifest; GC blocks later | Reference counting |

**MVP functional scope (lock with interviewer):**

1. Agent scans source tree → **content-defined chunks** → upload unknown blocks to object store.
2. Server maintains **block index** (hash → location, ref_count).
3. Each backup job produces immutable **snapshot manifest** (file → ordered block hashes + metadata).
4. Incremental: compare with last manifest; upload only new/changed blocks.
5. Restore: fetch manifest → parallel block GET → assemble files with correct metadata.
6. Retention policy deletes old manifests; **GC** removes blocks with ref_count=0.
7. Metrics: dedup ratio, upload bytes, restore latency, GC lag, verify failures.

**Out of MVP (explicitly defer):**

- Cross-region active-active dedup index without conflict resolution
- Client-side encryption that breaks global dedup (document trade-off)
- Instant VM boot from backup (sibling: image restore)
- Deduplication across encrypted tenants with different keys
- Real-time continuous backup (near-CDP)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Initial full backup throughput? | Saturate uplink reasonably | ≥ 100 MB/s per agent (configurable) |
| N2 | Incremental scan time? | Large trees | 1M files / 30 min class with incremental metadata index |
| N3 | Dedup ratio? | Media + code repos | 3–10× space savings typical |
| N4 | Restore RTO (single file)? | Minutes | p99 < 5 min for 1 GB file |
| N5 | Restore RTO (full tree)? | Hours parallelized | Dominated by egress + disk |
| N6 | Durability | 11 nines object store | Block stored in replicated object storage |
| N7 | Availability | Backup can lag; restore critical | Restore path HA |
| N8 | Correctness | Byte-identical restore | Hash verify on write |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. First full backup: scan → chunk → upload all blocks → write manifest v1.  
2. Daily incremental: only changed files re-chunked; 90% blocks dedup hits locally or on server.  
3. Restore file: manifest lookup → 20 block GETs → assemble → verify SHA-256.  
4. Two files share same block (identical segment): second upload skipped via hash hit.  
5. Retention expires snapshot: manifest deleted; ref_count decremented; GC frees blocks.  
6. Agent crash mid-upload: resume from last acknowledged block batch.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Block hash collision (SHA-256) | Treat as equal; document astronomically low risk; optional verify bytes on collision flag |
| Same hash, different bytes (attack) | Reject upload if server-side sample verify fails |
| File modified during scan | Snapshot consistency policy: retry file or copy-on-read stable snapshot (LVM/ZFS) |
| Hard link in source | Manifest records inode link count; restore recreates links |
| Symlink loop | Scan depth limit; record symlink as metadata only |
| Sparse file | Store only non-zero ranges as blocks + sparse map |
| Block uploaded but manifest commit fails | Orphan block; GC after grace if unreferenced |
| Dedup index split-brain | Single writer per domain or CRDT ref_count with repair job |
| Tenant A block equals tenant B | Dedup only within same encryption domain |
| Partial restore path exists | Skip existing; idempotent restore mode |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Protected agents | 1K | 10K | 100K | 1M |
| Total source data | 10 PB | 100 PB | 1 EB | 10 EB |
| Unique blocks (working set) | 500M | 5B | 50B | 500B |
| Daily new/changed data | 50 TB | 500 TB | 5 PB | 50 PB |
| Daily incremental jobs | 1K | 10K | 100K | 1M |
| Block upload QPS (peak) | 5K | 50K | 500K | 5M |
| Manifest size (large snapshot) | 500 MB | 2 GB | 10 GB | 50 GB |
| Dedup ratio (effective) | 4× | 5× | 6× | 7× (diminishing) |

**Split classes:** scan/metadata ≠ block upload ≠ index lookup ≠ restore egress ≠ GC.

**What each jump forces:**

- **10×:** Batch block uploads; local agent cache of recent hashes; gRPC streaming.  
- **100×:** Sharded block index by hash prefix; separate hot/warm storage tiers; parallel manifest compaction.  
- **1,000×:** Probabilistic bloom on agent; edge POP caches; erasure-coded cold pool; strict domain sharding.

### 1.5 Etc. (Constraints & Assumptions)

- Object storage (S3-compatible) is **durable SoT** for block payloads.  
- Agents run on Linux/macOS with read access to source trees.  
- **Content-defined chunking (CDC)** for boundary stability across inserts.  
- Filesystem primitives on agent: `copy_file_range`, reflinks where available for local staging cache.  
- Sibling docs: crash-resilient filesystem, DR orchestration, ransomware detection.

**Scope statement:**

> Design a scalable incremental backup system that chunks files with CDC, deduplicates blocks by cryptographic hash, stores payloads in object storage, maintains immutable snapshot manifests, and restores byte-correct trees—scaling from 10 PB through 10× / 100× / 1,000× with explicit GC and encryption-domain rules.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Chunking and block count

```text
Source logical data = 10 PB (baseline)
Average chunk size = 8 MiB (CDC target)
Theoretical max chunks = 10 PB / 8 MiB ≈ 1.25 × 10^9 blocks

With 4× dedup across files/versions:
Unique blocks ≈ 312M
Storage raw ≈ 2.5 PB unique bytes
Metadata per block ≈ 128 B (hash, ref, location, size)
Index memory ≈ 312M × 128 B ≈ 40 GB (before overhead)
```

**Deal-breaker:** storing whole files on change only → 10 PB backup for 10 PB source after small edits to large files.

### 2.2 Incremental daily delta

```text
Daily change rate ≈ 0.5% of source = 50 TB/day
After dedup (30% unique bytes) ≈ 15 TB new unique blocks/day
Upload at 1 Gbps effective ≈ 15 TB / (125 MB/s) ≈ 34 hours serial → need parallel agents/regions
Peak upload QPS (8 MiB blocks) ≈ 15 TB / 8 MiB / 86400 ≈ 22 blocks/s average
Peak burst 10× ≈ 220 blocks/s → 220 PUT/s per domain (manageable with batching)
```

### 2.3 Manifest size

```text
Files in tree = 100M
Per file manifest entry ≈ 64 B path hash + 16 B mtime + avg 4 block refs × 32 B hash ≈ 208 B
Raw manifest ≈ 100M × 208 B ≈ 20 GB per snapshot (uncompressed)
Compression (zstd) ≈ 5–10× → 2–4 GB on wire
At 100×: 10B files → need hierarchical manifests (directory sub-manifests)
```

### 2.4 Restore egress

```text
Restore 1 TB tree, dedup ratio irrelevant (must fetch all blocks for that snapshot)
1 TB / 8 MiB = 131,072 GETs
At 50 ms per GET parallel 256-wide ≈ 131072/256 × 0.05 ≈ 26 s network-only ideal
Realistic with overhead: minutes to tens of minutes
```

### 2.5 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Block hash lookup | 20K | 200K | 2M | bloom + shard |
| Block PUT (new) | 5K | 50K | 500K | idempotent by hash |
| Manifest read | 500 | 5K | 50K | restore + verify |
| Manifest write (commit) | 1K | 10K | 100K | single per job |
| GC ref decrement | 2K | 20K | 200K | async queue |
| Agent scan (files/s) | 10K | 50K | 200K | local SSD metadata |

### 2.6 Latency budget (single-file restore)

| Stage | Budget |
|-------|--------|
| Resolve snapshot + path | 50–200ms |
| Manifest fetch (cached) | 10–50ms |
| Block index lookup (batch) | 20–100ms |
| Parallel block GET (10 blocks) | 200–800ms |
| Assemble + verify | 50–200ms |
| **Total** | **< 2s p99 small file** |

Large restores dominated by throughput not latency.

### 2.7 Critical bottlenecks

1. **Manifest size** for billion-file trees.  
2. **Hot hash index** memory vs disk lookup latency.  
3. **GC pauses** if ref_count updates synchronous on delete.  
4. **Agent CPU** for CDC on high-change workloads.  
5. **Cross-tenant dedup** vs encryption isolation.

### 2.8 Cost intuition

```text
Storage cost ≈ unique_bytes × $/GB-month × EC overhead
Egress cost dominates restore drills
Dedup saves storage but index + compute adds cost
Track: $/TB-source-month and dedup_ratio
```

---

## 3. High-Level Design

### 3.1 Data flow overview

```text
Source FS → Agent (scan, CDC, hash) → Block Upload API → Object Store
                              ↓                ↓
                         Local hash cache   Block Index (hash → ref, uri)
                              ↓
                         Manifest Builder → Immutable Manifest Store
Retention job → drop old manifests → ref_count-- → GC orphan blocks
Restore → Manifest walk → block GET → assemble → verify
```

### 3.2 Core entities

| Entity | Role |
|--------|------|
| `Block` | Content-addressed blob (hash, size, storage_uri, encryption_key_id) |
| `BlockIndexEntry` | hash → {ref_count, uris[], tenant_domain, created_at} |
| `SnapshotManifest` | Immutable map: path → {metadata, block_hash[]} |
| `BackupJob` | Agent run: base_snapshot?, new_manifest, stats |
| `RetentionPolicy` | Rules per path/domain |
| `AgentCheckpoint` | Resume state for partial uploads |

### 3.3 Content-defined chunking (CDC)

Use rolling hash (Rabin/Karp) with target average chunk size **8 MiB** (min 2 MiB, max 64 MiB).

**Why CDC not fixed blocks:** inserting bytes at file start shifts fixed boundaries → poor dedup. CDC boundaries stable under local edits.

```text
function chunk(file_stream):
  boundaries = cdc_split(stream, avg=8MiB)
  for each segment:
    hash = SHA256(segment)
    emit BlockRef(hash, len)
```

### 3.4 Incremental snapshot algorithm

```text
function incremental_backup(source, last_manifest):
  new_manifest = empty
  for path in walk(source):
    meta = stat(path)
    if unchanged_quick_check(path, meta, last_manifest):
      new_manifest[path] = last_manifest[path]  # reuse block list
    else:
      blocks = chunk_and_upload(path)
      new_manifest[path] = {meta, blocks}
  commit_manifest(new_manifest)  # atomic pointer swap
  enqueue_retention_gc()
```

**Quick check:** size + mtime + inode change flag; optional fast hash (xxHash) of first/last block.

### 3.5 Dedup index operations

| Operation | When | Notes |
|-----------|------|-------|
| `LOOKUP(hash)` | Before upload | Hit → skip PUT |
| `REGISTER(hash, uri)` | After successful PUT | ref_count++ or insert |
| `REFERENCE(manifest)` | On manifest commit | increment all blocks in snapshot |
| `DEREFERENCE(manifest)` | On retention delete | decrement; queue GC if 0 |

**Idempotent upload:** `PUT block/{hash}` if-not-exists semantics.

### 3.6 Filesystem primitives on agent

| Primitive | Use |
|-----------|-------|
| `readdir` + `stat` | Scan |
| `copy_file_range` / `sendfile` | Local staging without userspace copy |
| `ioctl FIEMAP` (optional) | Extent map for sparse files |
| `xattr` | Capture extended attributes in metadata blob |
| Hard links | Detect via (dev, inode); manifest stores nlink |
| Reflink (btrfs/xfs) | Local cache CoW clone for verify pass |

Agent **does not require** special kernel backup API for MVP; optional VSS/ZFS snapshot for consistency.

### 3.7 Manifest immutability

Manifests are **append-only** content-addressed JSON/Protobuf blobs in object storage.

```text
snapshot_id = SHA256(canonical_manifest_bytes)
backup_domain.latest_snapshot = snapshot_id  # atomic CAS
```

Never mutate committed manifest; retention deletes whole manifest objects.

### 3.8 Restore modes

| Mode | Flow |
|------|------|
| File | Path lookup in manifest → fetch blocks → write file |
| Subtree | Prefix walk manifest → parallel restore |
| Full | Download root manifest (+ sub-manifests) → full walk |
| Verify-only | Hash all blocks without writing disk |

### 3.9 Encryption domains

| Policy | Dedup scope |
|--------|-------------|
| Server-side SSE-KMS per domain | Dedup within domain |
| Client-side per-agent keys | No cross-agent dedup |
| Envelope encryption | Block key wrapped per domain |

### 3.10 Consistency snapshot

| Source FS | Approach |
|-----------|----------|
| Plain ext4 | Best-effort; retry changed files |
| LVM/ZFS snapshot | Read stable snapshot device |
| Database | App quiesce + snapshot (out of scope) |

Document **crash-consistent** vs **application-consistent** with interviewer.

### 3.11 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Chunking | CDC 8 MiB average |
| Addressing | SHA-256 content hash |
| SoT payload | Object store |
| SoT metadata | Manifest + index |
| Dedup | Global per encryption domain |
| GC | Async ref_count |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+  scan/chunk   +-------------+   PUT/HEAD   +--------------+
| Agent  |-------------->| Upload Svc  |------------->| Object Store |
+--------+               +------+------+              +--------------+
    |                           |
    | hash lookup               | register
    v                           v
+-------------+          +-------------+       +------------------+
| Local Bloom |          | Block Index |<----->| Manifest Service |
| + SSD cache |          |  (sharded)  |       +--------+---------+
+-------------+          +-------------+                |
                                                          v
                                                 +--------+---------+
                                                 | Retention + GC   |
                                                 +------------------+

Restore Client → Manifest Service → Block Index → Object Store → assemble
```

### 4.2 Sequence: incremental backup

```text
Agent→Index: MGET hashes (batch 1000)
Index→Agent: hits/misses
Agent→Object: parallel PUT misses only
Agent→UploadSvc: commit block registrations
Agent→ManifestSvc: PUT manifest blob
ManifestSvc→Index: REF snapshot_id (increment refs)
ManifestSvc→Catalog: CAS latest_snapshot
```

### 4.3 Sequence: restore file

```text
User→RestoreAPI: restore(path, snapshot_id)
RestoreAPI→ManifestSvc: GET manifest + path index
RestoreAPI→Index: resolve block URIs
RestoreAPI→Object: parallel GET blocks
RestoreAPI: assemble, verify SHA256, write metadata
RestoreAPI→User: OK + checksum report
```

### 4.4 Sequence: GC after retention

```text
Retention→Catalog: list manifests to delete
Retention→ManifestSvc: delete manifest object
Retention→Index: DEREF all blocks in manifest (async batch)
GCWorker: for ref_count==0: delete object + index row
GCWorker: audit log tombstone
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Content-addressed immutability** — block bytes never overwritten.  
2. **Manifest commit atomicity** — snapshot visible only after all blocks registered.  
3. **Ref_count never negative** — transactional decrement with floor 0.  
4. **Restore verifies hash** before delivering file.  
5. **Upload idempotency** by hash.  
6. **Orphan blocks** reclaimed after grace period.  
7. **Encryption domain boundaries** enforced on index shard.  
8. **Audit trail** for delete/GC actions.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| PUT succeeded, register lost | Orphan block; GC reaps; backup retries register |
| Manifest committed, refs not incremented | Repair job scans manifest → fix refs |
| Index unavailable | Agent spools blocks locally (bounded) or pauses job |
| Hash collision alert | Quarantine block; require byte compare |
| Restore partial disk full | Abort; leave restore marker; resume capable |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Single index shard (Redis/RocksDB); one object bucket |
| 10× | Hash-prefix sharding; agent bloom cache; manifest compression |
| 100× | Hierarchical manifests; separate index cluster; tiered storage |
| 1,000× | Domain cells; erasure coding cold tier; edge upload POPs |

**Sharding:** `shard = hash[0:4]` — co-locate index with object prefix.

### 5.3 Maintainability

- **Backup verifier** — nightly sample restore + hash audit.  
- **Dedup ratio dashboard** per domain.  
- **Agent auto-update** with signed bundles.  
- Metrics: `upload_bytes_unique`, `dedup_hit_rate`, `manifest_commit_latency`, `gc_lag_sec`, `orphan_block_count`.  
- Runbook: stuck job, index drift, slow GC.

### 5.4 Exact algorithm: ref_count update on commit

```text
function commit_snapshot(manifest):
  blob = serialize(manifest)
  uri = object.put_if_absent(sha256(blob), blob)
  for hash in manifest.all_block_hashes():
    index.incr_ref(hash)  // batched pipeline
  catalog.cas(domain, manifest_id=sha256(blob))
  emit BackupJobCompleted
```

Use **two-phase**: upload all blocks → commit manifest → increment refs. If crash between manifest put and incr, repair worker idempotently incr from manifest scan.

### 5.5 Exact algorithm: GC

```text
function gc_tick():
  candidates = index.where(ref_count==0 AND age>grace)
  for c in candidates:
    if index.cas(c.hash, ref_count, 0, -1):  // mark deleting
      object.delete(c.uri)
      index.delete(c.hash)
```

### 5.6 Local agent optimizations

| Technique | Benefit |
|-----------|---------|
| Persistent hash cache (SQLite) | Skip re-hash unchanged files |
| Parallel walk + thread pool chunk | CPU utilization |
| `--files-from` incremental | Targeted backups |
| `copy_file_range` to pipe | Reduce copies |
| Adaptive chunk size | Tune for workload |

### 5.7 Hierarchical manifests (100×)

```text
root.manifest → {
  "dirs/": submanifest_uri_abc,
  "file1": {...}
}
submanifest_abc → millions of entries under dirs/
```

Restore subtree fetches only relevant submanifest.

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Fixed 4 KiB blocks | Dedup collapse on edits |
| Dedup across encryption keys | Security / compliance violation |
| Mutable block store | Silent corruption |
| Synchronous GC on delete | Latency spikes |
| Single global manifest JSON | OOM on load |
| Trust client ref_count | Drift and leaks |
| No verify on restore | Bit rot discovered too late |

### 5.9 Progressive scale deep dive

**1× (10 PB domain)**  
RocksDB index; 8 MiB CDC; daily incremental; simple retention.

**10×**  
Shard index 16 ways; agent bloom 100M hashes; zstd manifests; upload batch size 64.

**100×**  
Submanifest hierarchy; cold blocks to EC pool; dedicated restore proxies; cross-region replica of index read-only.

**1,000×**  
Cell architecture per studio/region; approximate index for bloom negatives only; separate GC fleet; rate-limited restore quotas.

### 5.10 Security

- Agent mTLS to control plane.  
- Least-privilege object store IAM per domain.  
- Immutable manifest WORM bucket option.  
- Ransomware detection: anomalous change rate alerts (sibling).

### 5.11 Rollout

```text
Pilot agents → shadow hash-only → upload throttled → full retention
Compare: restore drills weekly; dedup ratio benchmarks
Rollback: pin agent version; pause catalog CAS
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Chunking | CDC ~8 MiB average |
| Identity | SHA-256 content hash |
| Storage | Object store payloads |
| Metadata | Immutable manifests |
| Incremental | Manifest diff + block reuse |
| Dedup scope | Per encryption domain |
| GC | Async ref_count |

### 6.2 Risks

1. Manifest explosion on billion-file trees  
2. Index memory pressure at 100×  
3. Inconsistent snapshot without FS snapshot  
4. Orphan blocks if ref logic buggy  
5. Restore egress cost surprises  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: incremental + block dedup; not full DR |
| 5–15 | CDC + hash index + manifest |
| 15–25 | Upload path, idempotency, ref_count |
| 25–35 | Retention GC; encryption domains |
| 35–45 | Scale: hierarchical manifests; restore; traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Dedup fundamentals

**Q: Why CDC over fixed-size chunks?**  
A: Fixed blocks shift when bytes insert early in file; CDC keeps most boundaries stable → higher dedup.

**Q: Whole-file dedup enough?**  
A: Two similar 100 GB assets differ by 1 MB → whole-file stores twice; blocks dedup the common 99.999%.

**Q: SHA-256 collisions?**  
A: Accept for interview; optional byte verify on suspicious equality.

### 7.2 Incremental backup

**Q: How detect unchanged file fast?**  
A: mtime+size heuristic; optional rolling hash; inode metadata; compare to last manifest entry.

**Q: File truncated?**  
A: Metadata change triggers re-chunk; old blocks dereferenced on new manifest commit.

### 7.3 Consistency

**Q: File changes during backup?**  
A: Retry read; or read from filesystem snapshot; document crash-consistent outcome.

**Q: Database backup?**  
A: Out of scope — use DB dump + snapshot or logical backup sibling.

### 7.4 GC and references

**Q: Reference counting vs mark-sweep?**  
A: Ref count O(1) per block with manifest derefs; mark-sweep needs full graph walk — use ref count with repair scans.

**Q: Shared block across snapshots?**  
A: ref_count = number of manifests referencing; increment on commit each snapshot.

### 7.5 Restore

**Q: Restore latest version of one file?**  
A: Walk snapshot chain or use catalog "latest path version" index.

**Q: Parallel restore limits?**  
A: Cap GET concurrency; backoff on object store 503.

### 7.6 Encryption vs dedup

**Q: Client-side encryption?**  
A: Same plaintext → same ciphertext only with deterministic nonce (bad) or convergent encryption (trade-offs); usually per-tenant dedup only.

### 7.7 Comparison to rsync

**Q: vs rsync?**  
A: rsync delta over wire session; this system persistent block store + dedup across time/machines.

**Q: vs Restic/Borg?**  
A: Similar concepts; interview wants distributed scale + multi-tenant control plane.

### 7.8 Filesystem primitives

**Q: Why mention copy_file_range?**  
A: Shows kernel-aware performance; reduces CPU for local verify staging.

**Q: Reflinks?**  
A: Local CoW clone for testing restore without doubling disk.

### 7.9 Multi-tenancy

**Q: Shared dedup pool?**  
A: Policy decision; netflix studio isolation may forbid cross-tenant dedup.

### 7.10 Interview traps

**Q: "Store diff patches only"?**  
A: Patches don't dedup across files; blocks generalize.

**Q: "Use git"?**  
A: Git for text; poor for large binary media; no global GC at PB scale without custom pack.

**Q: "Delete block immediately when one snapshot expires"?**  
A: Must decrement ref_count; other snapshots may still reference.

### 7.11 Metrics that matter

**Q: What do you page on?**  
A: GC lag > 7d; orphan rate spike; restore verify failures; manifest commit failures; dedup ratio cliff (agent bug).

### 7.12 Cost

**Q: When dedup not worth it?**  
A: Unique encrypted random data; index cost > storage savings; very small files (chunk overhead).

---

## 8. Appendices

### A1. Block object key schema

```text
s3://backup-blocks/{domain}/{hash[0:2]}/{hash[2:4]}/{sha256}
```

### A2. Manifest entry schema

```text
FileEntry {
  path: string,
  mode: uint32,
  uid, gid, mtime, size,
  symlink_target?: string,
  xattrs: map<string,bytes>,
  blocks: [ { hash: sha256, offset: uint64, length: uint64 } ]
}
```

### A3. BlockIndexEntry schema

```text
BlockIndexEntry {
  hash: sha256,
  ref_count: int64,
  size: uint64,
  uris: [string],
  domain_id: string,
  created_at: timestamp,
  storage_class: HOT|COLD|EC
}
```

### A4. Launch checklist

- [ ] CDC parameters load-tested on representative media files  
- [ ] Ref_count repair job tested  
- [ ] Restore verify e2e on 1 TB sample  
- [ ] Retention + GC integration test  
- [ ] Encryption domain isolation verified  
- [ ] Agent resume after crash tested  

### A5. Glossary

| Term | Meaning |
|------|---------|
| CDC | Content-defined chunking |
| Manifest | Immutable snapshot metadata |
| ref_count | Number of snapshots referencing a block |
| Domain | Encryption + dedup isolation boundary |
| Orphan block | Uploaded but never referenced |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| Fixed 512 B blocks | Dedup useless |
| Skip ref_count | Storage leak |
| One manifest for EB scale | Won't load |
| Dedup across tenants | Policy violation |
| No restore verify | Data loss invisible |

### A7. Reliability test plan

1. Duplicate block upload → single object.  
2. Delete snapshot → blocks freed after grace.  
3. Shared block two snapshots → ref_count=2 until both gone.  
4. Manifest commit crash → repair incr idempotent.  
5. Restore corrupted block → verify fails loudly.

### A8. 60-second summary

> Incremental backup **chunks with CDC**, **addresses blocks by hash**, stores payloads in **object storage**, and commits **immutable manifests**. Dedup hits skip upload; **ref_count GC** frees unreferenced blocks; restore **parallel-fetches and verifies** hashes. Scale via **sharded index**, **hierarchical manifests**, and **encryption domains**.

### A9. Related systems map

```text
Agent → Upload Service → Object Store
Agent → Block Index (lookup)
Manifest Service → Catalog (latest pointer)
Retention → GC Workers
Restore Service → Object Store
KMS → encryption keys per domain
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Manifest commit success | 99.9% |
| Block durability | 11 nines (object store) |
| Restore verify pass rate | 100% |
| GC completion lag | < 72h after derefs |
| Dedup hit rate (incremental) | > 70% blocks |

### A11. Worked numeric example

```text
File V1: 100 MiB → 13 chunks → 13 unique hashes uploaded
Edit 1 MiB at offset 0 → CDC: ~2 chunks change at start + boundary ripple ~1-3 chunks
Upload ~3 new blocks; 10 blocks dedup hit from index
Manifest V2 references 3 new + 10 old hashes
Storage delta ≈ 24 MiB not 100 MiB
```

### A12. Pseudo-SQL catalog

```sql
CREATE TABLE backup_domains (
  domain_id UUID PRIMARY KEY,
  encryption_key_id TEXT NOT NULL,
  latest_snapshot_id BYTEA,
  retention_policy JSONB NOT NULL
);

CREATE TABLE snapshots (
  snapshot_id BYTEA PRIMARY KEY,
  domain_id UUID REFERENCES backup_domains,
  manifest_uri TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  job_id UUID NOT NULL
);
```

### A13. Ownership

| Concern | Owner |
|---------|-------|
| Agent + CDC | Client Backup Platform |
| Block index + GC | Storage Platform |
| Object store | Cloud Infra |
| Restore API | Data Protection SRE |
| KMS policies | Security |

### A14. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | CDC, hash index, manifest, restore verify |
| 10× | Sharded index, agent cache, compression |
| 100× | Hierarchical manifests, tiered storage |
| 1,000× | Cell domains, EC cold, restore proxies |

### A15. Comparison to naive design

| Naive | Why it fails |
|-------|--------------|
| Full file copy nightly | Storage × versions |
| rsync only | No cross-machine dedup pool |
| gzip whole tree | No block reuse across files |
| Single SQLite index | Won't scale past TB |

### A16. On-call cheat sheet

1. Check `orphan_block_count` trend.  
2. Check GC worker backlog.  
3. Verify object store error rate on PUT/GET.  
4. If dedup ratio drops: agent cache corruption? CDC bug?  
5. If restore slow: egress throttle; increase parallel GET.

### A17. Sample manifest fragment

```json
{
  "path": "/projects/renders/shot_042.exr",
  "size": 1342177280,
  "mtime": "2026-08-06T12:00:00Z",
  "blocks": [
    {"hash": "a1b2...", "offset": 0, "length": 8388608},
    {"hash": "c3d4...", "offset": 8388608, "length": 8388608}
  ]
}
```

### A18. CDC parameter tuning

| Parameter | Typical |
|-----------|---------|
| Target avg chunk | 8 MiB |
| Min chunk | 2 MiB |
| Max chunk | 64 MiB |
| Rolling window | 48 bytes |

### A19. Cost worksheet

```text
unique_storage_TB = source_TB / dedup_ratio
index_GB ≈ unique_blocks × 128B / 1e9
monthly_storage_$ ≈ unique_storage_TB × 1024 × $/GB
restore_$ ≈ restore_TB × egress_$/GB
```

### A20. Explicit non-goals

- Replacing versioning VCS for source code  
- Live filesystem serving from backup  
- Guaranteed sub-second RPO without snapshots  
- Deduplicating encrypted ciphertext across independent keys without policy review  

---

*End of document — Netflix system design interview prep: Scalable File Backup (Incremental + Block Dedup).*
