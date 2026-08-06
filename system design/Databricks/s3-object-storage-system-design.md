# System Design: S3-like Object Storage

> **Focus areas:** Bucket/key model · Multipart upload · Metadata vs data plane · Durability · Replication · Consistency · Listing · GC
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split control/metadata/data planes, explicit durability/RPO, deal-breakers for “single Postgres blob column” at scale  
> **Interview theme:** Databricks — lakehouse object storage foundation; metadata/data plane split, multipart, durability

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

Goal: **bound the product**—an **S3-like object store**: buckets/keys, put/get/delete/list, multipart, versioning hooks, high durability, and scalable metadata. Used for media, backups, data lake, ML artifacts.

### 1.0 What this is / is not

| Dimension | **S3-like object storage (this doc)** | Not this |
|-----------|--------------------------------------|----------|
| Primary job | Durable blob store by key | POSIX filesystem |
| API | Bucket/object, multipart, presign | SQL queries over bytes |
| Consistency | Strong read-after-write per key MVP | Cross-region sync write |
| Listing | Prefix/delimited | Arbitrary secondary indexes MVP |
| Success | Durability + availability + correct multipart | Cheapest HDD chaos without checksums |

**Scope statement:** Design an S3-like object storage system with separated metadata/data planes, multipart upload, replication for durability, prefix listing, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | API? | Put/Get/Delete/Head/List + multipart | S3-compatible subset |
| F2 | Keys? | Flat namespace with `/` prefix convention | Metadata index by prefix |
| F3 | Object size? | 0–5 TB class; multipart >5–8 MB parts | Part assembly |
| F4 | Consistency? | Read-after-write for new puts new keys | Per-key strong in region |
| F5 | Versioning? | Optional per bucket | Version chain + GC |
| F6 | Durability? | Multi-AZ; cross-region optional | EC or 3x repl |
| F7 | Encryption? | SSE-S3 / SSE-KMS hooks | Encrypt data plane |
| F8 | Auth? | IAM-like + presigned URLs | Auth service |
| F9 | Listing? | Prefix + delimiter + pagination | Ordered index |
| F10 | Lifecycle? | Expire / transition cold | GC workers |
| F11 | Events? | Object created/deleted | Bus/outbox |
| F12 | Checksums? | Required | Trailer/part checksums |

**MVP functional scope:**

1. Create/delete bucket; put/get/delete/head object.  
2. List by prefix with continuation tokens.  
3. Multipart upload (init, upload part, complete, abort).  
4. Multi-AZ durability (erasure coding or triple replication).  
5. Per-key read-after-write in a region.  
6. Presigned URL GET/PUT.  
7. Basic versioning OR delete markers (pick with interviewer).  
8. Metrics, quotas, authZ.

**Out of MVP:**

- Full POSIX / rename directories as atomic trees  
- Cross-region strong consistency  
- Object SQL query engine  
- Exact S3 ACL legacy maze (use IAM-style)  
- Glacier deep archive nuances (mention tiering hooks)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability | Critical | ~11 nines design goal annual |
| N2 | Availability | High | 99.99% region GET/PUT |
| N3 | Get latency | Small objects snappy | p50 < 20–50ms metadata+first byte |
| N4 | Throughput | Scale with clients | Multipart parallel |
| N5 | Listing | Correct pagination | No missed keys under concurrency caveats documented |
| N6 | Integrity | No silent corruption | End-to-end checksums |
| N7 | Cost | Hot/cold | EC for cold large; lifecycle |
| N8 | Multi-tenant | Noisy neighbor isolation | Quotas / QoS |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. PUT small object → GET returns bytes + etag.  
2. Multipart large video → complete → GET streaming.  
3. List prefix `photos/2026/` → paginated keys.  
4. Presigned upload from mobile → PUT to data plane.  
5. Delete → subsequent GET 404 (or delete marker if versioned).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Complete multipart missing part | Reject complete |
| Complete with wrong checksum | Reject |
| Concurrent PUT same key | Last-writer-wins with etags / If-Match optional |
| List during write storm | Pagination consistent-enough; document |
| Disk/bitrot | Scrubber + checksum repair from replicas/EC |
| AZ down | Reconstruct / serve from remaining |
| Metadata OK data lost | Repair job; never silently return wrong |
| Abort multipart | GC incomplete parts |
| Huge list (1e9 keys) | Prefix partitions; rate limit list |
| Presign expired | 403 |
| Bucket delete non-empty | Fail or async purge job |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Objects | 1B | 10B | 100B | 1T |
| Storage | 100 PB | 1 EB | 10 EB | 100 EB |
| PUT QPS | 10K | 100K | 1M | 10M |
| GET QPS | 100K | 1M | 10M | 100M |
| Avg object size | 100 KB | 100 KB | mixed | mixed |
| Buckets | 100K | 1M | 10M | 100M |
| List QPS | 1K | 10K | 100K | 1M |
| Multipart actives | 10K | 100K | 1M | 10M |
| Metadata nodes | 10 | 100 | 1K | cell fabric |

**What each jump forces:**

- **10×:** Metadata sharding by bucket/key; EC for large; CDN optional front.  
- **100×:** Bucket as cell; range partitioning; tiered media.  
- **1,000×:** Global namespace service; hierarchical metadata; cold storage robots/tape hooks.

### 1.5 Etc. (Constraints & Assumptions)

- Single-region strong consistency MVP; CRR async optional.  
- S3 API subset enough for interview—not byte-perfect compatibility.  
- Clients may be apps, Hadoop/Spark, mobile via presign.

**Scope statement:**

> Design an S3-like object store with bucket/key API, multipart upload, checksummed multi-AZ durable data plane, scalable metadata for prefix listing, presigned access, and progressive sharding through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Metadata** | key→locator, list | 10–50% of ops | Metadata KV |
| **Data PUT** | bytes write | 10K QPS | Storage nodes |
| **Data GET** | bytes read | 100K QPS | Storage + cache |
| **Multipart control** | init/complete | lower QPS | Metadata |
| **GC / scrub** | background | continuous | Workers |
| **List** | prefix scan | spiky | Metadata ordered |

### 2.2 Capacity

```text
100 PB usable
With 3x replication → 300 PB raw
With EC 6+3 (1.5×) → 150 PB raw — better for large cold
Mixed strategy: replicate small/hot; EC large/cold
```

### 2.3 Metadata size

```text
1B objects × 500B metadata ≈ 500 TB metadata cluster
Must be sharded KV/ordered store — not one RDBMS primary
```

### 2.4 Small object problem

```text
10K PUT/s × 10 KB = 100 MB/s trivial bandwidth
IOPS/metadata dominate — aggregate small objects / use replication not EC
```

### 2.5 Large object

```text
5 GB object, 8 MB parts ≈ 640 parts
Parallel PUT parts; complete assembles manifest
GET may redirect to part ranges or reassembled stream
```

### 2.6 Metadata QPS arithmetic

```text
Baseline ops: 10K PUT/s + 100K GET/s
Metadata touches:
  PUT: 1–2 writes (version + locator) + quota read
  GET: 1 read (often cached)
  LIST: range scan cost ∝ pages
Assume meta cache hit 80% on GET → origin meta GET ≈ 20K/s
Meta PUT ≈ 10–20K/s
1B keys × 3 replicas → metadata cluster must shard; single primary dies
At 100×: meta GET origin ~2M/s → per-key caches + cell-local meta mandatory
```

### 2.7 Replication vs EC cost math

```text
Usable 100 PB
3× replication: 300 PB raw; write amp ≈ 3× network on PUT
EC 6+3 (1.5×): 150 PB raw; encode CPU + gather on rebuild
EC 10+4 (1.4×): 140 PB raw; higher rebuild fan-in
Break-even intuition:
  Objects < ~1 MB: replication preferred (IOPS, latency, tail)
  Objects ≫ multi-MB: EC wins $ and space
Hybrid: replicate first N MB / hot class; EC cold large
```

### 2.8 Multipart control-plane load

```text
1K large uploads/s starting, avg 64 parts, part rate 64K PUT-part/s
Complete rate 1K/s — each complete validates part set + commits manifest
Incomplete TTL 7d: GC scans multipart table; orphans reclaim bandwidth
Part size 8 MB × 64K/s = 512 GB/s ingest at that hypothetical — size fleets to real SLO
```

### 2.9 Durability / scrub bandwidth

```text
100 PB usable; scrub every 90 days
Scrub read rate ≈ 100 PB / 90d ≈ 12.8 Gbps average cluster-wide (order-of-mag)
Must throttle vs customer GET; prioritize checksum mismatch repair
Interview: show scrub is a first-class capacity citizen, not "when idle"
```

### 2.10 Latency budgets

```text
Small PUT p99 (same region):
  auth+quota 1ms | place+write quorum 10–30ms | meta commit 2–5ms | total ~20–40ms
Small GET p99:
  meta 1ms (cache) | data 5–15ms | total ~10–20ms
Multipart complete:
  validate parts 5–20ms | meta commit; not on data path of bytes
Cross-AZ write adds ~1–2ms RTT each; 3 AZ quorum bounded by slowest
```

---

## 3. High-Level Design

### 3.1 API (S3-like subset)

| Op | Semantics |
|----|-----------|
| `PUT /b/{bucket}/{key}` | Store object (small) |
| `GET /b/{bucket}/{key}` | Read object |
| `HEAD ...` | Metadata only |
| `DELETE ...` | Delete / delete marker |
| `GET /b/{bucket}?prefix&delimiter&token` | List |
| `POST multipart/init` | UploadId |
| `PUT ...?partNumber&uploadId` | Upload part |
| `POST complete` | Assemble |
| `DELETE uploadId` | Abort |
| Presign | Time-limited signed URL |

### 3.2 Planes

| Plane | Stores | Hard requirement |
|-------|--------|------------------|
| **Control** | Buckets, IAM, quotas | Strong, low QPS |
| **Metadata** | key → versions, etag, locator, size | Consistent per key |
| **Data** | Chunks/blocks/EC stripes | Checksums; repair |

### 3.3 Data model

```text
Bucket { name, region, versioning, owner, quota }
ObjectMeta {
  bucket, key, version_id,
  etag, size, content_type,
  storage_class,
  locator: [chunk_ids] | ec_manifest,
  checksum,
  created_at, deleted
}
MultipartUpload { upload_id, key, parts[] }
Chunk { chunk_id, size, checksum, placements[] }
```

### 3.4 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Metadata/data split | Separate | Scale independently | Blobs in SQL rows only |
| Durability large | **Erasure coding** | Cost | 3x everything at EB |
| Durability small | Replication | Latency/IOPS | EC on 1KB objects |
| Key listing | Ordered key index | Prefix list | Hash-only metadata no order |
| Multipart | Manifest of parts | Large objects | Single PUT 5TB through LB |
| Consistency | Per-key quorum/primary | RAW for new keys | Pure eventually w/o warning |
| GC | Async with refcounts | Multipart aborts | Never reclaim incomplete |
| Commit order | Data durable → meta pointer | No dangling GET | Meta-first without fencing |
| Versioning | Optional per bucket | Overwrite safety | Silent clobber only |
| Placement | AZ-diverse constraints | Correlated failure | All replicas one rack |
| Checksums | End-to-end (client→store) | Bitrot/corruption | Trust disk only |
| List pagination | Opaque tokens | Stable scale | OFFSET deep pages |
| Presign | Scoped signed URLs | Direct data plane | Proxy all bytes via API |

**Expanded deal-breakers:**

1. **Single RDBMS for all object metadata** — 1B keys × list prefixes dies; need sharded ordered KV.  
2. **EC on every tiny object** — encode overhead + read-amplification wrecks small-GET SLO.  
3. **Metadata commit before data durable** — clients GET 404/partial after ACK; trust destroyed.  
4. **Hash-only metadata** — cannot implement S3 prefix listing without secondary index anyway.  
5. **No multipart** — multi-GB through one TCP connection; retries wasteful; LB timeouts.

### 3.5 Put path (small object)

```text
auth → validate quota
 → allocate object version + chunk IDs
 → write data to N AZs (repl or EC encode)
 → wait durability quorum
 → commit metadata pointer (atomic)
 → ACK client with etag
```

**Critical:** metadata commit **after** durable data (or fencing) so GET never sees dangling pointer without bytes—or use two-phase with GC for orphans.

### 3.6 Multipart path

```text
init → upload_id in metadata
parts uploaded to data plane independently (idempotent part# + checksum)
complete → verify all parts → write final manifest → commit object meta → GC old version optional
abort → mark upload aborted → GC parts
```

---

## 4. Architecture Diagram

```text
                 Clients / Presigned
                         |
                         v
              +----------+-----------+
              | API Gateway / LB     |
              | auth, rate limits    |
              +-----+------+---------+
                    |      |
          control   |      |  data (PUT/GET bytes)
                    v      v
         +----------+--+  +---------------+
         | Bucket/IAM  |  | Data Routers  |
         | Quotas      |  | (placement)   |
         +------+------+  +-------+-------+
                |                 |
                v                 v
         +------+------+   +------+-------+------+
         | Metadata KV |   | Storage Node AZ1    |
         | ordered idx |   | Storage Node AZ2    |
         | multipart   |   | Storage Node AZ3    |
         +------+------+   +----------+----------+
                |                     |
                v                     v
         GC / Scrub / Compaction   Repair / EC decode
                |
                v
         Event bus (ObjectCreated)
```

**GET path:**

```text
auth → metadata get(key)
 → if missing 404
 → fetch chunks by locator (parallel)
 → verify checksums
 → stream to client
 (optional CDN for public/hot)
```

**List path:**

```text
metadata.range(bucket, prefix_start, prefix_end, token, limit)
 → apply delimiter common-prefixes
 → return next_token
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **ACK Put only after data durable + metadata committed** (defined order).  
2. **Checksum verify on write and read/scrub**.  
3. **No silent bitrot** — repair from redundant fragments.  
4. **Multipart complete atomic** from client view.  
5. **Quotas enforced** before accepting large writes.

#### 5.1.2 Durability math (illustrative)

```text
3-way replication across AZs; independent AZ fail rare
Scrub period detects latent sector errors
EC 6+3 tolerates 3 fragment losses
Interview: show you track MTTDL thinking, not fake precision
```

#### 5.1.3 Failure modes

| Failure | Handling |
|---------|----------|
| One AZ down | Serve from remaining; degraded re-replicate |
| Metadata shard down | Failover replica / leader election |
| Incomplete multipart orphan | Lifecycle GC after TTL |
| Wrong etag complete | Reject |
| Network partition client | Idempotent retries with the same upload_id/part |

#### 5.1.4 Consistency details

- **New object PUT:** read-after-write in region after success.  
- **Overwrite:** reader may see old/new briefly unless versioned conditional—document.  
- **List:** list-after-write may lag slightly in some designs; aim for strong if metadata primary ordered log.  
- **Cross-region:** async replication; RPO minutes.

### 5.2 Scalability

#### 5.2.1 Metadata sharding

```text
shard = hash(bucket) OR hash(bucket + key_prefix)
hot buckets: split by key ranges (directory partitioning)
avoid single bucket hotspot without range splits
```

#### 5.2.2 Data placement

```text
chunk_id → consistent hash to node sets with AZ diversity constraints
rebalance with virtual nodes; background move
```

#### 5.2.3 Caching

- Gateway buffer small HOT GETs.  
- CDN for public assets.  
- Metadata cache with version/fencing carefully (risk stale deletes).

#### 5.2.4 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | Shard metadata; EC large; multipart common path |
| 100× | Bucket cells; key-range splits; tiering |
| 1,000× | Global naming; hierarchical meta; cold vault |

### 5.3 Maintainability

- Scrubber + repair tooling first-class.  
- Manifest version evolution for EC schemes.  
- Dark traffic checksum audits.  
- Clear tenant isolation metrics (IOPS, bandwidth).  
- Chaos: kill AZ; verify durable GET.

#### 5.3.1 Control vs data ownership

| Plane | Change cadence | Risk |
|-------|----------------|------|
| IAM/bucket policy | Frequent | Authz bugs |
| Metadata schema | Rare, versioned | List/GET correctness |
| EC codec | Rare | Durability |
| Placement policy | Tunable | Balance vs risk |

#### 5.3.2 Operability checklist

- Per-tenant bandwidth/IOPS fair queues.  
- Repair backlog age SLO.  
- Multipart incomplete age histogram.  
- “ACK without durable” red alarm (should be impossible).

### 5.4 Metadata vs data plane

#### 5.4.1 Responsibilities split

| Concern | Metadata plane | Data plane |
|---------|----------------|------------|
| Key → locator | ✓ | |
| List prefix | ✓ | |
| Multipart state | ✓ | parts bytes |
| Bytes durable | | ✓ |
| Checksum store | both (meta stores expected; data verifies) | ✓ |
| IAM | control plane (ahead of both) | enforce at gateway |

#### 5.4.2 Why split scales

```text
Metadata: small values, high QPS, strong per-key consistency, ordered ranges
Data: large sequential/random IO, placement, repair bandwidth
Coupling them in one store forces wrong replication/EC tradeoffs
```

#### 5.4.3 Pointer safety

```text
States for object version:
  WRITING → DURABLE_DATA → COMMITTED → (GC old)
Or: two-phase with fencing tokens so stale writers cannot commit
Orphans (data without meta): GC by allocation journal
Dangling meta (meta without data): scrub detects; heal or error
```

#### 5.4.4 Hot metadata keys

Celebrity object (`/bucket/index.html`) → meta cache + negative caching on 404; data CDN. Never single-row lock worldwide.

### 5.5 Erasure coding vs replication

#### 5.5.1 Replication path

```text
Write to N AZ-diverse nodes; ACK on W quorum (e.g. 2/3)
Read from any; repair on checksum fail
Simple; higher storage $; great for small/hot
```

#### 5.5.2 EC path

```text
Split into k data fragments + m parity (e.g. 6+3)
Place on distinct failure domains
Read: any k of k+m; decode if needed
Rebuild: read k fragments → reconstruct missing
Write latency: wait for k+m or buffered policy (document)
```

#### 5.5.3 Selection policy

| Class | Scheme |
|-------|--------|
| <256 KB / frequently overwritten | 3× repl |
| Multi-MB cold | EC 6+3 or 10+4 |
| Compliance archive | EC + cross-region copy |
| Multipart parts | Often repl then compose; or EC per part if large |

#### 5.5.4 Rebuild storm control

```text
Throttle rebuild bandwidth per rack
Prioritize under-min-copy objects
Avoid rebalancing+rebuild simultaneous full blast
```

### 5.6 Multipart deep dive

#### 5.6.1 State machine

```text
INIT → UPLOADING → COMPLETING → COMPLETED
                 ↘ ABORTED → GC
COMPLETING is fencing: reject new parts; validate set; commit object
```

#### 5.6.2 Complete validation

```text
1. upload_id exists and not aborted
2. all required part numbers present (1..N contiguous policy)
3. each part checksum matches client-provided on complete list
4. total size within limits
5. write object meta with part manifest as locator
6. mark upload COMPLETED; schedule old version GC if overwrite
```

#### 5.6.3 Idempotency

```text
PUT part: (upload_id, partNumber, checksum) idempotent
Complete retry: return same etag if already COMPLETED with same parts
Different part set → conflict error
```

#### 5.6.4 Abort & GC

```text
Abort marks upload; parts become reclaimable
Lifecycle: incomplete >7d → auto-abort
Refcount or allocation log prevents deleting live object parts
```

### 5.7 Consistency deep dive

#### 5.7.1 Per-key model (MVP)

| Op | Guarantee |
|----|-----------|
| PUT new key success | Subsequent GET sees object (same region) |
| Overwrite | Readers may see old or new until meta linearizes; versioned GET by versionId strong |
| DELETE | Delete marker; GET 404 after commit |
| LIST | Prefer read-your-writes via same meta leader; document lag if async index |

#### 5.7.2 Implementation levers

```text
Metadata primary per key-range (Raft) → strong per key
OR Dynamo-style quorum with vector clocks → need sibling resolution (harder for S3 API)
Prefer primary/Raft for S3-like API simplicity
```

#### 5.7.3 Cross-region

```text
Async replicate meta+data; RPO minutes
Conflict: region-primary buckets or CRR last-writer with versions
Never claim strong global RAW unless sync path (rare, expensive)
```

### 5.8 GC, scrub, lifecycle

#### 5.8.1 GC candidates

- Aborted multipart parts  
- Unreferenced chunks after overwrite/delete  
- Expired delete markers (policy)  
- Failed WRITING allocations past TTL  

#### 5.8.2 Scrubber

```text
Walk chunk placements → read checksum → repair from peers/EC
Rate limit; alert on unrepaired under-min-copy age
```

#### 5.8.3 Lifecycle transitions

```text
HOT → WARM → COLD (storage class) via background rewrite/EC convert
GET may restore; API exposes storage class on HEAD
```

### 5.9 Progressive scale (10× / 100× / 1,000×)

| Jump | Metadata | Data | API stability |
|------|----------|------|---------------|
| →10× | Hash shard buckets; caches | EC large objects; multipart default client SDK | Same |
| →100× | Key-range splits; bucket cells | Tiering; repair fleets | Same + notifications |
| →1,000× | Hierarchical directory; global namespace cells | Cold vault EC; multi-region CRR productized | Same verbs |

**Narrative:**

- **10×:** Metadata alone becomes the bottleneck before raw disk — shard and cache.  
- **100×:** Hot buckets need directory partitioning; scrub/repair are capacity planning inputs.  
- **1,000×:** EB-class forces hierarchical meta, aggressive EC/cold, and cell isolation; API verbs unchanged.

### 5.10 Failure drills

| Drill | Expected |
|-------|----------|
| Lose 1 AZ | GETs succeed; PUTs still quorum; re-replicate |
| Metadata leader crash | Election; brief elevate latency; no ACK loss if committed |
| Incomplete multipart flood | GC backlog alert; admit pressure limits |
| Checksum mismatch on GET | Retry alternate fragment; repair async; serve correct |

### 5.11 Listing & delimiter semantics

```text
List(bucket, prefix, delimiter='/', token, max)
Returns:
  contents[] — keys at this “directory” level
  common_prefixes[] — next path segments
  next_token — opaque
Implementation: ordered index scan from prefix_start
  with delimiter aggregation in streaming fashion
Don't: load all keys under prefix into memory
```

**Consistency:** prefer list-after-write for same key via meta primary; document if async secondary index lags.

### 5.12 Presigned URL path

```text
Client → API: POST presign {method, key, expiry, headers}
API → signed URL (HMAC / SigV4-like) scoped to op
Client → Data plane directly with signature
Gateway verifies sig, expiry, content-length bounds
Benefits: API servers don’t proxy terabytes
Risks: leaked URL until expiry — short TTL + scope
```

### 5.13 Progressive scale narrative (long form)

- **→10×:** Shard metadata; EC for large; SDK multipart default; scrub bandwidth reserved.  
- **→100×:** Bucket cells + key-range splits; lifecycle tiering; per-tenant IO fair queues.  
- **→1,000×:** Hierarchical namespace; cold vault; CRR product; API verbs unchanged for decades (S3 lesson).

---

## 6. Wrap-Up

### 6.1 Summary

S3-like storage is three planes—**control, metadata, data**—glued by checksummed locators and multipart manifests. Durability is redundancy + scrubbing; scale is metadata sharding and placement; listing needs ordered indexes, not hash maps alone.

### 6.2 Trade-offs

| Trade-off | Choice |
|-----------|--------|
| Cost vs durability | EC large; replicate small |
| Consistency vs multi-region | Strong regional; async CRR |
| List freshness vs write rate | Ordered metadata primary |
| API compatibility vs simplicity | Subset S3 |

### 6.3 Deal-breakers

1. Single SQL table of blobs at EB scale.  
2. ACK before durability quorum.  
3. Hash-only metadata with no prefix listing plan.  
4. No checksum/scrub story.  
5. Multipart without GC of abandoned parts.

### 6.4 Scale one-liner

Baseline 3-AZ repl → 10× sharded meta+EC → 100× cells/ranges → 1,000× global naming + cold tiers.

---

## 7. Deeper / Related Interview Questions

### 7.1 API & multipart

**Q1: Why multipart?**  
A: Parallelism, resume, size limits on single HTTP request, better failure isolation.

**Q2: Minimum part size?**  
A: Typically ≥5 MB except last part—keeps manifest manageable and throughput sane.

**Q3: How is etag computed?**  
A: Often MD5 for single PUT; multipart etag is MD5-of-MD5s + part count—document compatibility.

**Q4: Idempotent PUT?**  
A: Same key overwrite; use If-None-Match / If-Match for conditional. Retries safe with checksums.

**Q5: Presigned URL risks?**  
A: Leakage = access; short TTL; scope method/key; audit.

**Q6: Copy object?**  
A: Server-side copy by reference clone + COW or physical copy; metadata new key pointer.

**Q7: Range GET?**  
A: Map byte ranges to chunks; essential for media/seek.

### 7.2 Metadata

**Q8: Why ordered key store?**  
A: Prefix list and delimiter need lexicographic scan.

**Q9: Hot bucket with billions of keys?**  
A: Split table by key ranges; auto-split; avoid single shard.

**Q10: Metadata as Redis?**  
A: Too little durability/memory for billions; use Raft/Paxos KV or Bigtable-style.

**Q11: How to paginate lists?**  
A: Continuation token = last key + version; avoid offset pagination.

**Q12: Delimiter semantics?**  
A: Simulate directories: group by next path segment; return `commonPrefixes`.

### 7.3 Durability & EC

**Q13: Replication vs erasure coding?**  
A: Repl simpler/faster for small; EC saves capacity for large sequential objects.

**Q14: What does 11 nines mean practically?**  
A: Engineering program: multi-AZ, scrub, repair SLAs, ops discipline—not a magic RAID number.

**Q15: Read repair vs scrub?**  
A: Read repair on checksum fail path; scrub proactive full walk.

**Q16: AZ outage during PUT?**  
A: Write to remaining + degraded re-replicate; or fail request if durability policy unmet.

**Q17: How to avoid corrupt ACK?**  
A: Verify checksums at storage nodes before ACK; client-provided checksums preferred.

### 7.4 Consistency & concurrency

**Q18: Two writers same key?**  
A: Last complete metadata commit wins; optional conditional puts; versioning keeps both.

**Q19: Read-after-write guarantee scope?**  
A: Same region, success response returned; not global.

**Q20: List vs GET race?**  
A: Newly written key should appear; under overload some systems briefly lag—prefer strong via meta primary.

**Q21: Tombstones?**  
A: Deletes leave markers until GC; versioned buckets use delete markers.

### 7.5 GC & lifecycle

**Q22: Orphan chunks?**  
A: Refcount or generation IDs; GC after multipart abort TTL; careful with in-flight completes.

**Q23: Lifecycle expire?**  
A: Async scanner by prefix/date rules; rate-limited deletes.

**Q24: Version sprawl?**  
A: Keep N versions or days; GC noncurrent.

### 7.6 Security & multi-tenant

**Q25: AuthZ model?**  
A: IAM policies on bucket/prefix; deny by default; service roles.

**Q26: Encryption?**  
A: TLS in transit; SSE at rest with KMS keys per bucket/tenant.

**Q27: Noisy neighbor?**  
A: Per-tenant token buckets on request rate and bandwidth; separate noisy tenants.

**Q28: SSRF via presign?**  
A: N/A stores; but redirect features need care; validate hosts on callbacks/events.

### 7.7 Scale & ops

**Q29: Rebalancing data?**  
A: Background mover; maintain redundancy during moves; update locators carefully with fencing.

**Q30: Multi-region active-active?**  
A: Hard for single-key strong conflict; usually CRR primary/secondary or conflict buckets.

**Q31: CDN integration?**  
A: Origin shield GETs; invalidate on delete carefully (versioned URLs help).

**Q32: Cost levers?**  
A: EC, cold tier, compression optional, small-object packing, TTL lifecycle.

### 7.8 Alternatives & craft

**Q33: Only NFS?**  
A: Wrong API/semantics/scale for object multi-tenant cloud.

**Q34: Only one big Ceph mention without parts?**  
A: Name-check OK; still need multipart, listing, consistency story.

**Q35: How to open?**  
A: API ops, size range, consistency, durability, listing—then three planes.

**Q36: What impresses?**  
A: Put order data→meta, EC vs repl split, list tokens, multipart GC, progressive metadata split.

**Q37: Common mistake?**  
A: Drawing only storage nodes; forgetting metadata listing at 1T objects.

**Q38: End strong?**  
A: Invariants, repair/scrub, scale cells, deal-breakers.

**Q39: How do events work?**  
A: Metadata commit outbox → bus `ObjectCreated`; at-least-once to subscribers.

**Q40: Bucket name global uniqueness?**  
A: Global control plane registry; rate limited creates; DNS-like constraints.

**Q41: Why not store parts forever after complete?**  
A: Manifest references parts; can mark sealed; GC only unreferenced after abort/expire.

**Q42: Cross-account access?**  
A: Policy grants; presign; audit logs mandatory at Meta scale.

---

### Appendix A — Small PUT sequence

```text
1. Authorize
2. Quota check
3. Generate version_id, chunk_ids
4. Parallel write chunks to placements (AZ diverse)
5. Quorum ACK with checksums
6. Commit ObjectMeta(locator)
7. Return etag, version_id
```

### Appendix B — Multipart complete validation

```text
parts_expected = 1..N
for i in 1..N:
  assert part[i] exists and checksum matches client list
size = sum(part.size)
manifest = parts
commit object
mark upload completed
```

### Appendix C — EC layout sketch

```text
object → split into k data fragments + m parity
place fragments on distinct AZs/racks
read: any k of k+m
```

### Appendix D — List algorithm

```text
start = token or prefix
end = prefix_end_bound(prefix)
keys = meta.scan(start, end, limit+1)
if delimiter:
  collapse to common prefixes
next_token = last_raw_key if more
```

### Appendix E — Checksum types

| Stage | Checksum |
|-------|----------|
| Client upload | CRC32C/SHA256 optional |
| Part | per-part digest |
| Chunk store | stored digest |
| Scrub | recompute compare |

### Appendix F — Metadata schema

| Field | Notes |
|-------|-------|
| pk | bucket+key+version |
| etag | integrity/version hint |
| size | bytes |
| locator | opaque |
| storage_class | STANDARD/COLD |
| multipart_id | nullable |

### Appendix G — GC state machine

```text
UPLOAD_ABORTED → parts reclaimable after TTL
OBJECT_DELETED → chunks refcount--
VERSION_NONCURRENT → lifecycle expire
ORPHAN_CHUNK (no meta) → reclaim after grace
```

### Appendix H — NFR card

```text
ACK after durable data + meta commit
Checksums end-to-end
Multi-AZ redundancy
Prefix list via ordered index
Multipart + abort GC
Regional RAW consistency
Quotas + authZ
```

### Appendix I — Progressive scale

| Scale | Meta | Data | Notes |
|-------|------|------|-------|
| Base | Few KV shards | 3 AZ repl | |
| 10× | Many shards | EC large | |
| 100× | Cells + ranges | Tiering | |
| 1,000× | Global name | Cold vault | |

### Appendix J — Comparison

| Approach | Durability | List | Scale | Verdict |
|----------|------------|------|-------|---------|
| Postgres BYTEA | Weak at scale | OK small | Poor | Reject |
| DFS POSIX | Medium | Weak object API | Medium | Reject sole |
| Object meta+data planes | Strong design | Ordered meta | Strong | **Choose** |

### Appendix K — Error codes (subset)

| Code | Meaning |
|------|---------|
| NoSuchKey | Missing |
| NoSuchUpload | Bad uploadId |
| InvalidPart | Missing/bad part |
| EntityTooSmall | Part size |
| AccessDenied | AuthZ |
| SlowDown | Throttle |

### Appendix L — Placement constraints

```text
pick nodes:
  distinct az >= 3
  avoid same rack if possible
  respect disk free weighted
```

### Appendix M — Metrics

| Metric | Why |
|--------|-----|
| put_durability_seconds | Risk |
| get_checksum_fail | Integrity |
| repair_backlog | Health |
| list_p99 | Meta scale |
| incomplete_multipart_bytes | Waste |
| az_degraded_objects | Priority repair |

### Appendix N — Security checklist

- TLS everywhere  
- KMS envelope encryption  
- Short-lived credentials  
- Access logs  
- Block public accidental (account defaults)

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Locator | Pointer from meta to data fragments |
| Manifest | Multipart/EC description |
| Scrub | Background integrity walk |
| RAW | Read-after-write |
| Continuation token | List cursor |

### Appendix P — Worked metadata math

```text
100B objects × 500B = 50 PB metadata — forces aggressive sharding and lean records
Aim metadata ≤ few hundred bytes/object; offload user metadata carefully
```

### Appendix Q — Cold tier hook

```text
lifecycle: STANDARD → COLD after 30d
worker rewrite to EC denser / slower media
update storage_class; GET may restore restore-time for vault
```

### Appendix R — 30m checklist

1. API + sizes + consistency.  
2. Three planes diagram.  
3. Put order + multipart.  
4. EC vs repl.  
5. List tokens.  
6. GC/scrub.  
7. Scale jumps + deal-breakers.

### Appendix S — Idempotency keys

```text
PUT retries: same body checksum → same etag outcome OK
Upload part: (upload_id, part_number, checksum) idempotent store
Complete: only once; retries return success if already completed identical manifest
```

### Appendix T — Bucket delete

```text
if versioning / many keys:
  async purge job
  bucket state DELETING
  reject new writes
else:
  require empty
```

### Appendix U — Why Meta asks

Object storage underpins **photos, videos, attachments, ML artifacts, logs**. Interview tests durability thinking and metadata scale, not memorizing S3 XML.

### Appendix V — Deal-breaker card

| Fantasy | Reality |
|---------|---------|
| ACK on buffer | Data loss on crash |
| One Postgres | Metadata wall |
| No list plan | Breaks data lakes |
| No scrub | Bitrot |
| No multipart GC | Cost leak |

### Appendix W — Part upload request

```http
PUT /v1/b/mybucket/key?uploadId=U&partNumber=3 HTTP/1.1
Content-Length: 8388608
x-amz-checksum-crc32c: ...

[binary part]
→ 200 ETag: "part3md5" 
```

### Appendix X — Complete multipart body

```json
{
  "parts": [
    {"part_number": 1, "etag": "..."},
    {"part_number": 2, "etag": "..."},
    {"part_number": 3, "etag": "..."}
  ]
}
```

Server verifies each part exists, checksums match, contiguous 1..N.

### Appendix Y — Two-phase commit variants

| Approach | Description | Risk |
|----------|-------------|------|
| Data then meta | Write chunks; commit pointer | Orphan chunks if crash before GC |
| Meta intent then data | Tentative meta; seal | Readers must ignore unsealed |
| Witness log | Log intent; quorum data; commit | More complex; strong |

MVP: data durable → meta commit → async orphan GC.

### Appendix Z — Small object packing (Phase 1.5)

```text
Problem: billions of 1–10KB objects waste inode/chunk overhead
Approach: pack many small objects into larger containers (ec_extents)
Metadata points to (container_id, offset, len)
Trade-off: rewrite amplification on update/delete
```

### Appendix AA — Cross-region replication

```text
on meta commit (opt-in bucket):
  enqueue CRR task {bucket,key,version,locator}
replica region pulls bytes / chunk copy
updates replica meta
RPO = queue lag (minutes typical)
failover: DNS/app switch; accept possible loss within RPO
```

### Appendix AB — Quota enforcement points

| Checkpoint | Enforce |
|------------|---------|
| Create bucket | bucket count |
| Init multipart / PUT | object count, pending bytes |
| Upload part | bandwidth/request rate |
| Complete | final size vs quota |

Soft vs hard quotas: soft warn; hard 403 `QuotaExceeded`.

### Appendix AC — Scrubber algorithm

```text
for each chunk in placement DB (sharded walk):
  read local bytes
  if checksum mismatch:
    mark bad
    reconstruct from other fragments/replicas
    rewrite
    metric scrub_repair++
  rate limit to protect online traffic
```

### Appendix AD — Hot key / celebrity object

```text
viral GET on single key:
  gateway cache / CDN
  replicate chunks to more nodes (on-demand)
  never let single disk serve 100% viral traffic
```

### Appendix AE — List-during-write semantics table

| Scenario | Expected |
|----------|----------|
| PUT ACK then LIST | Key visible |
| PUT in flight LIST | May or may not |
| DELETE ACK LIST | Key gone / delete marker |
| Multipart not complete | Not listed as object |

### Appendix AF — Final interview card

```text
three planes: control / metadata / data
ACK after durable data + meta
checksums + scrub + repair
repl small / EC large
ordered metadata for prefix list
multipart + abort GC
regional RAW; async CRR
10× shard meta → 100× cells → 1000× global+cold
```

---

*End of S3-like Object Storage system design.*
