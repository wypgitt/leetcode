# System Design: File Store

> **Focus areas:** Set/Get · Filtering · Backup · Restore · Versioning · Recovery · GC  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split metadata/data/backup classes, explicit versioning & GC, resolved durability/RPO story  
> **Interview theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — reliability, consistency, concurrency, cost; store model artifacts, datasets, prompt blobs, eval outputs without losing classic file/object-store discipline

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

Goal: **bound the file store**—a durable multi-tenant object/file store with set/get, metadata filtering, versioning, backup/restore, and recovery. Used as source of truth for AI infra (checkpoints, datasets, configs) and general artifacts. This is **not** the volatile cache (sibling doc); this **is** durable SoT.

### 1.0 File store vs file cache

| Dimension | **File store (this doc)** | File cache |
|-----------|---------------------------|------------|
| Durability | Required (multi-AZ / ER) | Best-effort |
| SoT | Yes | No |
| Versioning | First-class | Optional etag |
| Backup/restore | First-class | N/A |
| Latency | ms–tens of ms OK | µs–ms goal |

**Scope statement:** Design a durable **file/object store** with set, get, filtering, versioning, backup, restore, and recovery.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | Put/Get/Delete/List + conditional | Object API; path keys |
| F2 | Filtering? | List by prefix, tags, time, size | Metadata index |
| F3 | Versioning? | Keep N versions or time-based | Version chain + GC |
| F4 | Backup? | Periodic + continuous options | Snapshots / cross-region copy |
| F5 | Restore? | Point-in-time / version restore | Recovery workflows |
| F6 | Consistency? | Read-after-write same key | Strong per key MVP |
| F7 | Multipart? | Large model files | Multipart / chunked upload |
| F8 | Encryption? | At rest + TLS | KMS hooks |
| F9 | Multi-tenant? | Buckets/namespaces + quotas | AuthZ + quota |
| F10 | Checksums? | Required on write | Integrity |
| F11 | Lifecycle? | Expire old versions / cold tier | GC + tiering |
| F12 | Events? | Object created/deleted | Outbox / bus |

**MVP functional scope:**

1. Put/Get/Delete object by `bucket/key`; optional `If-Match` / `If-None-Match`.  
2. List by prefix; filter by tags/metadata (indexed).  
3. Versioning on (per bucket); Get version; list versions.  
4. Multipart upload for large objects.  
5. Cross-AZ replication; async cross-region replica.  
6. Snapshot / backup export; restore to bucket or version undelete.  
7. GC for non-current versions per policy.  
8. Metrics, quotas, audit.

**Out of MVP:**

- Full POSIX FS  
- Cross-region strongly consistent dual-write  
- Client-side encryption complex CMK rotation UX (hooks)  
- Query engine over object contents (only metadata filter)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability | Critical | 11 nines class design; multi-AZ |
| N2 | RPO (regional) | Low | Async CRR RPO minutes; PITR per policy |
| N3 | RTO | Restore hours→minutes | Snapshot index readiness |
| N4 | Availability | High | 99.99% get/put same region |
| N5 | Get latency | Reasonable | p50 < 20–50ms small; large streaming |
| N6 | Correctness | No silent loss | Checksums + version CAS |
| N7 | List scalability | Prefix list OK | Avoid full scans |
| N8 | Cost | Hot/cold tier | Lifecycle to cold |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Put new key → version v1 → Get returns v1.  
2. Put update → v2 current; v1 retained → filter list tags.  
3. Multipart complete → atomic publish current version.  
4. Delete → delete marker (versioned) or purge.  
5. Backup snapshot → restore key to prior version / new bucket.  
6. Region failover read from replica (possible stale minutes).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Lost Update | CAS If-Match fail 412 |
| Multipart abandoned | GC incomplete parts |
| Partial AZ loss | Reconstruct via ER/replicas |
| GC deletes needed version | Retention legal hold / pin |
| Filter query too broad | Require prefix or indexed tag; paginate |
| Restore stomps current | Restore as new version or explicit overwrite flag |
| Clock skew on List time filter | Server time; storage monotonic version ids |
| Cross-region conflict | Last-writer per key policy documented |
| Checksum mismatch | Reject write; never persist |
| Hot key metadata | Shard metadata; cache current pointer |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Objects | 1B | 10B | 100B | 1T |
| Total bytes | 10 PB | 100 PB | 1 EB | 10 EB |
| Put QPS | 5K | 50K | 500K | 5M |
| Get QPS | 50K | 500K | 5M | 50M |
| List QPS | 1K | 10K | 100K | 1M |
| Avg object | 1 MB | mixed | mixed | mixed |
| Large object | 50 GB | 100 GB | 200 GB+ | checkpoints larger |
| Versions retained avg | 3 | 3–10 | policy | policy |
| Backup bytes/day | 100 TB | 1 PB | 10 PB | incremental critical |
| Metadata nodes | 10 | 50 | 200 | cells |

**What each jump forces:**

- **10×:** Metadata partitions; chunk managers; dedicated list indexes.  
- **100×:** Cells by bucket hash; cold tier; incremental backup only.  
- **1,000×:** Global namespace service; per-cell SoT; hierarchical restore catalogs.

### 1.5 Etc. (Constraints & Assumptions)

- Keys are strings (paths); buckets = tenants/projects.  
- AI checkpoints are large, write-rarely, read-burst on resume.  
- Prefer **immutable versions** over in-place mutate.  
- Filtering is on **metadata**, not full content search MVP.

**Scope statement:**

> Design a durable versioned file/object store with set/get, metadata filtering, multipart large objects, backup/restore, GC, and multi-AZ durability—supporting AI artifacts and general files—scaling via metadata partitions and cells, with explicit RPO/RTO for regional failure.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Store |
|-------|------|----------|-----|-------|
| **Metadata Put/Get** | key→locator | ~5–50K/s | ×10 | Metadata DB |
| **Data plane Put/Get** | bytes | GB/s | ×10 | Chunk/blob servers |
| **List/Filter** | index query | ~1K/s | ×10 | Secondary index |
| **Version GC** | background | continuous | — | Workers |
| **Backup/replication** | bytes pipe | 10+ Gbps | ×10 | Pipeline |
| **Restore** | rare burst | spike | — | Pipeline |

**Anti-pattern:** counting only “5K put QPS” while ignoring 50 GB multipart and backup pipe.

### 2.2 Metadata size

```text
1B objects × 500 B meta ≈ 500 TB raw meta (heavy)
Reality: compress + columnar; still → partitioned metadata mandatory
Per object: key, version, etag, size, tags, locator, timestamps, crc
```

### 2.3 Version amplification

```text
If every Put keeps forever: storage × writes forever
Policy: keep last N=3 or 30 days noncurrent
AI checkpoints: pin “good” versions; GC rest
```

### 2.4 Backup math

```text
10 PB fleet, 2% daily change → 200 TB/day incremental
Full backup daily impossible at 1,000× without incremental + synthetic full
```

### 2.5 Throughput

```text
Put 5K/s × 1 MB avg = 5 GB/s ingest
Get 50K/s × 100 KB avg = 5 GB/s egress (skewed by large)
NIC/disk planning from byte rates not only QPS
```

---

## 3. High-Level Design

### 3.1 API shape

| Method | Purpose |
|--------|---------|
| `PUT /b/{bucket}/{key}` | Set (optional versioning) |
| `GET /b/{bucket}/{key}` | Get current |
| `GET /b/{bucket}/{key}?versionId=` | Get version |
| `DELETE /b/{bucket}/{key}` | Delete / delete-marker |
| `GET /b/{bucket}?prefix=&tag=&from=` | List/filter |
| `POST multipart/*` | Initiate/part/complete |
| `POST /b/{bucket}/restore` | Restore version / PITR |
| `POST /admin/snapshots` | Backup snapshot |

### 3.2 Domain model

```text
Bucket
  policies: versioning, retention, quota, encryption, lifecycle
ObjectKey
  versions[]: Version
Version
  version_id, is_current, etag, size, crc, tags, created_at
  locator: [{chunk_id, offset, len, checksum}] | blob_id
  state: complete | delete_marker | uploading
MultipartUpload
  upload_id, parts[], expires_at
Snapshot
  snapshot_id, time, manifest_locator, scope (bucket/prefix)
```

### 3.3 Metadata vs data plane

| Plane | Responsibility |
|-------|----------------|
| Metadata | Keys, versions, tags index, current pointer, CAS |
| Data | Chunks/blobs on disk/object erasure coding |
| Control | GC, backup, compaction, rebalance |

**Deal-breaker:** single relational row holding multi-GB bytes.

### 3.4 Versioning model

| Approach | Pros | Cons |
|----------|------|------|
| Overwrite in place | Simple | No restore; risk |
| Copy-on-write versions | Safe restore | Storage × |
| Content-addressed immutability | Dedup | App uses new keys |

**Chosen:** COW versions with current pointer CAS; GC noncurrent by policy; content-addressed chunks underneath for dedup.

### 3.5 Filtering / indexing

| Filter | Index |
|--------|-------|
| Prefix list | Key sorted (SSTable / B-tree) |
| Tags `team=x` | Secondary inverted index tag→keys |
| Time range | (bucket, time, key) index or version id time-sortable |
| Size | Optional sparse index; careful |

**Deal-breaker:** `SELECT * WHERE tag` full metadata scan at 100B objects.

List always **paginated** with opaque cursor.

### 3.6 Backup & restore

| Mode | RPO | Cost | Use |
|------|-----|------|-----|
| Multi-AZ sync/quorum write | ~0 AZ | High | Default durable Put |
| Async CRR | minutes | Med | DR |
| Periodic snapshot manifests | hours | Med | PITR / ransomware |
| Version undelete | depends retention | Low | Oops delete |

**Restore flows:**

1. **Undelete version** — make prior version current (CAS).  
2. **Snapshot restore** — materialize keys from manifest to destination bucket.  
3. **Regional DR** — promote CRR replica read-write (document divergence).

### 3.7 Durability techniques

| Technique | Role |
|-----------|------|
| Replication (3×) | Simple repair |
| Erasure coding (e.g. 6+3) | Cold/hot cost save |
| Checksums end-to-end | Detect rot |
| Scrubber | Background verify |
| Quorum write ack | Put durability |

**Chosen MVP:** EC or 3-AZ replication for chunks; metadata Raft/Paxos/Quorum DB.

### 3.8 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Versioning | COW + GC policy | Restore without full backup | In-place only |
| Meta/data split | Mandatory | Scale | Monolithic files in SQL |
| Filter | Indexed prefix+tags | Predictable | Unindexed scans |
| Backup | Incremental + manifests | Feasible at PB | Daily full only |
| Consistency | Strong per key | App simplicity | Casual eventual for current pointer |
| Large files | Multipart + chunks | Resume | Single PUT 100GB |

---

## 4. Architecture Diagram

```text
                 Clients / AI jobs / Cache
                          |
                          v
                 +--------+--------+
                 | API Gateway     |
                 | authz, quota    |
                 +--------+--------+
                          |
            +-------------+-------------+
            v                           v
   +--------+--------+         +--------+--------+
   | Metadata Service|         | Multipart Coord |
   | versions, CAS   |         +--------+--------+
   | list indexes    |                  |
   +--------+--------+                  |
            |                           |
            v                           v
   +--------+--------+         +--------+--------+
   | Meta Store      |         | Chunk / Blob    |
   | (Raft partitions|         | Storage Nodes   |
   |  + tag index)   |         | (EC / replica)  |
   +--------+--------+         +--------+--------+
            |                           |
            +-------------+-------------+
                          |
                          v
               +----------+-----------+
               | GC / Lifecycle       |
               | Backup / CRR / Scrub |
               +----------+-----------+
                          |
                          v
               Snapshot manifests / Remote region
```

**Put path (versioned):**

```text
allocate version_id -> write chunks durable -> checksum
  -> CAS metadata current pointer -> ack
failure before CAS: orphan chunks -> GC
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Acked Put is durable** in the durability zone (quorum/EC).  
2. **Current pointer CAS** prevents lost updates when required.  
3. **Checksum mismatch never becomes current**.  
4. **GC never deletes pinned / retention-held versions**.  
5. **Manifest backup refers only to durable chunks**.

#### 5.1.2 Atomic publish

Multipart: parts durable independently; **Complete** writes metadata once. Readers never see partial current.

#### 5.1.3 Recovery classes

| Failure | Recovery |
|---------|----------|
| Single disk | Reconstruct EC/replica |
| AZ loss | Remaining AZs serve |
| Metadata partition leader loss | Raft elect |
| Accidental delete | Version / delete-marker undo |
| Ransomware mass delete | Snapshot time-travel restore |
| Region loss | Promote CRR; RPO minutes |

#### 5.1.4 Backup consistency

Snapshot = metadata epoch + chunk references. Use **copy-on-write**: new writes allocate new chunks; snapshot remains stable. Avoid flushes that block Put for long—use dirty buffers with epoch fencing.

#### 5.1.5 Progressive reliability

| Scale | Focus |
|-------|-------|
| Baseline | 3-AZ replica; daily snapshot |
| 10× | EC cold tier; incremental backup |
| 100× | Cell blast radius; continuous backup |
| 1,000× | Cross-region cells; tested restore drills |

### 5.2 Scalability

#### 5.2.1 Metadata partitioning

Partition by `hash(bucket, key)` into ranges. List-by-prefix: use **ordered partitioner by (bucket, key)** for that bucket’s shards—or special prefix index.

Tradeoff: hash alone hurts prefix list → **directory partitions per bucket** with key order.

#### 5.2.2 Tag filter index

```text
index entry: (bucket, tag_key, tag_val, object_key, version)
query: seek prefix (bucket, team, ml) → paginate
update on Put/Delete async or sync (sync simpler MVP)
```

At huge scale: async index with brief query lag—or sync for strong list.

#### 5.2.3 Chunk placement

Large objects → many chunks; place across nodes; EC stripes. Rebalance background.

#### 5.2.4 Hot keys

Cache current version metadata in memory; data plane still streams chunks. Celebrity model file: CDN/cache sibling in front.

#### 5.2.5 GC & compaction

- Incomplete multipart TTL.  
- Orphan chunks (no meta ref) refcount GC.  
- Noncurrent versions lifecycle.  
- Compaction small objects (optional packing).

#### 5.2.6 Backup at scale

| Scale | Strategy |
|-------|----------|
| Baseline | Periodic full manifest + data sync |
| 10× | Incremental by dirty epoch |
| 100× | Continuous WAL shipping of meta + chunk sync |
| 1,000× | Per-cell backup; global catalog only |

#### 5.2.7 Cost

- EC for large cold checkpoints.  
- Dedup content-addressed chunks.  
- Lifecycle to glacier-class.  
- Avoid keeping infinite versions of noisy logs.

### 5.3 Maintainability

#### 5.3.1 Bucket policies as code

Versioning, retention, encryption, quota—config reviewed; progressive rollout.

#### 5.3.2 Restore drills

Quarterly: restore random prefix to dry-run bucket; measure RTO; verify checksums.

#### 5.3.3 Observability

put/get/list latency, durability scrub errors, GC lag, backup lag (RPO), orphan bytes, CAS conflict rate, multipart abandon rate.

#### 5.3.4 Safe evolution

Phase 1: single region multi-AZ.  
Phase 2: CRR.  
Phase 3: cells.  
Phase 4: customer-managed keys / WORM retention.

---

## 6. Wrap-Up

### 6.1 What we designed

A **durable versioned file/object store** with split metadata/data planes, multipart large objects, tag/prefix filtering indexes, COW versioning + GC, multi-AZ durability, and backup/restore with explicit RPO/RTO—fit for AI checkpoints and general artifacts.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Versioning | COW + policy GC |
| List/filter | Must be indexed |
| Backup | Incremental manifests |
| Strong consistency | Per-key current pointer |
| Meta/data | Always split at scale |

### 6.3 Closing line

> “This is a classic durable object store—the AI twist is huge versioned checkpoints and bursty reads, which force multipart, EC, pin/retention, and restore drills to be first-class, not footnotes.”

---

## 7. Deeper / Related Interview Questions

### 7.1 API & semantics

**Q1: Put vs Set semantics?**  
A: Idempotent Put of bytes; versioned buckets create new version; CAS optional.

**Q2: Read-after-write?**  
A: After ack, Get current in-region returns new version.

**Q3: List vs filter?**  
A: List prefix is primary; filters use secondary indexes; always paginate.

**Q4: Delete with versioning?**  
A: Insert delete marker; prior versions retained until GC.

**Q5: Conditional writes?**  
A: If-Match etag / If-None-Match * for create-only.

### 7.2 Versioning & GC

**Q6: How are version IDs generated?**  
A: Time-sortable unique ids (ULID/ts+rand) or monotonic per key.

**Q7: GC safety?**  
A: Refcount chunks; only delete when no version/snapshot refs; respect legal hold.

**Q8: Pinning versions?**  
A: Mark `retain=true` for known-good checkpoints.

**Q9: Can GC race with Get?**  
A: Refcount or generation; Get holds lease on locator during read.

**Q10: Infinite versions cost?**  
A: Lifecycle rules mandatory at scale.

### 7.3 Filtering

**Q11: Why not scan metadata?**  
A: At billions of objects, scan kills clusters; require prefix or indexed tags.

**Q12: Many tags updates?**  
A: Index update cost; limit tag cardinality; async index with lag SLA.

**Q13: Cursor design?**  
A: Opaque `(partition, key, version)` exclusive start; stable under inserts carefully.

### 7.4 Backup & restore

**Q14: What is a snapshot?**  
A: Consistent metadata view + immutable chunk refs.

**Q15: RPO vs RTO?**  
A: RPO = max data loss window; RTO = time to serve again.

**Q16: Ransomware?**  
A: WORM retention / MFA delete; offline snapshots.

**Q17: Restore one key?**  
A: Copy prior version to current or to new key—cheap.

**Q18: Restore whole bucket?**  
A: Manifest replay; parallel chunk ensure; swap pointers.

**Q19: CRR conflict?**  
A: Prefer single-writer region; or last-writer-wins with vector clocks documented.

### 7.5 Durability & recovery

**Q20: Replication vs EC?**  
A: Replica simpler/hot; EC saves $ at large sizes/cold.

**Q21: Bitrot?**  
A: Scrub + checksums; reconstruct.

**Q22: Metadata loss?**  
A: Worse than chunk loss—replicate meta more aggressively; backup manifests.

**Q23: Split brain?**  
A: Quorum membership; fencing tokens on primary.

### 7.6 Large objects / AI

**Q24: 100 GB checkpoint?**  
A: Multipart; parallel parts; complete atomic; pin version.

**Q25: Training job restart storm?**  
A: Expect Get burst; front with cache; ensure store can stream many readers.

**Q26: Dedup across checkpoints?**  
A: Content-addressed chunks; similar checkpoints share chunks.

### 7.7 Consistency & concurrency

**Q27: Lost update without CAS?**  
A: Last writer wins; offer CAS for critical configs.

**Q28: Multipart race two completes?**  
A: Only one wins CAS to current; other versions retained or abort.

**Q29: Concurrent delete and get?**  
A: Get by version still works; current may become delete marker.

### 7.8 Scalability

**Q30: 1T objects metadata?**  
A: Cells; per-bucket directories; cold meta tiering.

**Q31: Hot list prefix?**  
A: Cache list pages carefully; rate limit; denorm.

**Q32: Cross-tenant noisy neighbor?**  
A: Per-bucket IO tokens; separate storage pools optional.

### 7.9 Cost

**Q33: Cost levers?**  
A: EC, lifecycle, dedup, avoid chatty tiny objects (pack), compression.

**Q34: Small object problem?**  
A: Packing/compaction; or discourage tiny keys in API guidelines.

### 7.10 Alternatives

**Q35: Just use S3?**  
A: Fine in industry; interview wants internals: meta/data, versioning, GC, backup.

**Q36: POSIX FS?**  
A: Different semantics (dirs, locks); harder multi-tenant cloud API.

**Q37: DB BLOBs?**  
A: Deal-breaker at PB.

### 7.11 Interview craft

**Q38: Opening?**  
A: Durability target, versioning on/off, filter needs, backup RPO—then split meta/data/backup loads.

**Q39: Numbers?**  
A: Object count, bytes, put/get byte rates, version factor, daily change rate for backup.

---

### Appendix A — CAS Put pseudocode

```text
Put(bucket, key, bytes, prev_etag?):
  chunks = durable_write(bytes)  // quorum/EC
  v = new_version(etag, chunks)
  meta.CAS(bucket, key,
           expect_etag=prev_etag,
           set_current=v) or abort_and_orphan_gc(chunks)
  index.update(tags)
  return v
```

### Appendix B — GC

```text
periodically:
  for noncurrent versions past retention and not pinned:
    remove meta ref
  for chunks with refcount 0 and age > grace:
    delete chunk
  for expired multipart:
    abort + delete parts
```

### Appendix C — Snapshot

```text
epoch = meta.fence()
manifest = iterate keys+current/pinned versions at epoch
persist manifest immutably
// chunks already immutable via COW
```

### Appendix D — Progressive scale

| Scale | Meta | Data | Backup | Filter |
|-------|------|------|--------|--------|
| Baseline | Few Raft groups | 3-AZ | Daily snap | Prefix+tags sync |
| 10× | Many partitions | EC cold | Incremental | Sharded indexes |
| 100× | Cells | Per-cell EC | Continuous | Async OK some ns |
| 1,000× | Global name + cells | Regional | Per-cell | Cell-local queries |

### Appendix E — Metrics

| Metric | Why |
|--------|-----|
| durability_scrub_errors | Silent rot |
| backup_lag_seconds | RPO |
| gc_orphan_bytes | Leak |
| cas_conflicts | Contention |
| multipart_abandon | Client bugs |
| list_p99 | Index health |

### Appendix F — NFR card

```text
Durability multi-AZ 11-9s class
Read-after-write in-region
Version restore < minutes per key
Bucket PITR per snapshot schedule
Checksum fail => reject
List always paginated + indexed filters
```

### Appendix G — Worked numbers

```text
1B objects × 500B meta = 500 TB meta raw → partition aggressively
10 PB data, 3× replica = 30 PB raw; EC 6+3 ≈ 1.5× = 15 PB
Put 5K/s × 1MB = 5 GB/s
Daily change 2% of 10 PB = 200 TB incremental backup
Versions N=3 → up to ~3× logical before GC/dedup
```

### Appendix H — Pushbacks

| Pushback | Response |
|----------|----------|
| “Store versions forever” | Cost blowup; policy GC + pins |
| “Filter any JSON field” | Need indexes; limit schema |
| “Sync active-active global” | Conflicts; prefer home region |
| “Single Postgres” | Meta maybe; data never |

### Appendix I — Related systems

| System | Relation |
|--------|----------|
| File cache | Speeds Get; store is SoT |
| Model registry | Points at store versions |
| Backup vault | Offline copies |
| Kafka outbox | Object events |

### Appendix J — Non-goals

- Content full-text search  
- POSIX rename atomic dirs (can emulate)  
- Byte-range transactional write (except multipart parts)  

### Appendix K — Security notes

- AuthZ per bucket/prefix  
- SSE-S3 / SSE-KMS  
- Audit log of deletes/restores  
- Optional WORM / object lock  

### Appendix L — Multipart state machine

```text
initiated -> uploading parts -> completing -> completed
                 \-> aborted (TTL or explicit)
```

### Appendix M — 30s narrative

> We split metadata and data, version with COW, index prefix/tags for filter, and treat backup as incremental manifests over immutable chunks. At 10× we partition and EC; at 100× cells and continuous backup; at 1,000× regional cells with drilled restores—AI checkpoints are just large versioned objects with pins.

### Appendix N — Delete marker vs purge

| Op | Effect |
|----|--------|
| Delete (versioned) | Delete marker current; data kept |
| Delete versionId | Remove specific version |
| Lifecycle purge | Hard delete eligible |
| Legal hold | Blocks purge |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Current pointer | Meta ref to live version |
| Manifest | Snapshot inventory |
| CRR | Cross-region replication |
| EC | Erasure coding |
| Orphan chunk | Bytes without meta ref |

### Appendix P — Filtering query planner (interview depth)

```text
List(bucket, prefix="/models/", tag={team:research}, from=t0):
  plan:
    1) Seek key index at (bucket, "/models/")
    2) Intersect with tag index postings for (bucket, team, research)
    3) Filter versions by created_at >= t0
    4) Paginate with limit + cursor
  reject if no prefix AND no selective tag (scan guard)
```

**Selectivity rule of thumb:** require at least one selective predicate (prefix length ≥ N or tag cardinality estimate < threshold).

### Appendix Q — Backup / restore drill script

```text
1. Create snapshot snap_t
2. Write canary object after snap_t (must NOT appear in restore)
3. Delete / mutate a known key after snap_t
4. Restore snap_t to bucket-restore-dryrun
5. Verify checksums of sample + full count
6. Measure wall-clock RTO
7. Document gaps; fix automation
```

### Appendix R — Version chain example

```text
key=checkpoints/run42/weights
  v3 (current)  etag=e3  pinned
  v2            etag=e2  lifecycle=30d
  v1            etag=e1  expired -> GC eligible
  delete_marker (if deleted) would become current until undelete
```

Restore v2 → new v4 copy or CAS current to v2 per API policy.

### Appendix S — EC vs replication decision matrix

| Workload | Choice | Why |
|----------|--------|-----|
| Hot tiny meta | 3× / 5× replica | Latency + simplicity |
| Hot large media | 3-AZ replica or light EC | Rebuild cost vs $ |
| Cold checkpoints | EC 6+3 / 10+4 | $ at EB scale |
| Backup vault | EC + offline air-gap | Ransomware |

### Appendix T — Quota & multi-tenant isolation

| Resource | Enforcement |
|----------|-------------|
| Bytes stored | Hard quota; Put 507 |
| Put/Get QPS | Token buckets per bucket |
| List QPS | Stricter (expensive) |
| Multipart parts | Cap concurrent uploads |
| Request fan-out | Per-principal limits |

Noisy-neighbor: separate storage pools for “elephant” AI tenants optional at 100×.

### Appendix U — Metadata schema (illustrative)

```text
Current:
  PK (bucket, key) -> {current_version_id, etag, size, updated_at}

Version:
  PK (bucket, key, version_id) -> {etag, size, crc, tags_json, locator, state, pinned}

TagIndex:
  PK (bucket, tag_k, tag_v, key, version_id)

Multipart:
  PK (bucket, key, upload_id) -> {parts[], expires_at, initiated_by}
```

### Appendix V — What AI infra changes (and what it doesn’t)

| Changes | Doesn’t change |
|---------|----------------|
| Multi-GB versioned checkpoints | Meta/data plane split |
| Pin “known good” weights | Checksums + CAS |
| Burst read on job restart | Quotas / multi-AZ durability |
| Dedup across similar ckpts | Backup RPO/RTO discipline |

---

*End of File Store system design.*
