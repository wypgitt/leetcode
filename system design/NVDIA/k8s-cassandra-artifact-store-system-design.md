# System Design: Artifact Store on Kubernetes + Cassandra

> **Focus areas:** Checkpoints · Image metadata · Build artifacts · Object store + Cassandra · Consistency · TTL · Multi-tenant · K8s patterns · CDN/cache  
> **Style:** Storage platform design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct size/QPS arithmetic, clear blob vs metadata split, resolved consistency/TTL, honest Cassandra data model trade-offs

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

Goal: **bound the artifact store**—durable publication and retrieval of ML/build artifacts where **large blobs live in object storage**, **Cassandra holds metadata/indexes**, and **Kubernetes** runs the control/data-plane services with clear multi-tenant isolation and TTL lifecycle.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What artifacts? | Model checkpoints, container image **metadata** (not full registry), build outputs, datasets pointers, config bundles | Type taxonomy + size classes |
| F2 | Blob sizes? | KB configs → GB checkpoints → multi-GB shards; rarely multi-TB single object without multipart | Object store + multipart; never Cassandra for bytes |
| F3 | APIs? | Upload (init/complete), download URL, list by project/job, delete, lifecycle | Presigned URLs common |
| F4 | Consistency? | Read-after-write for uploader; list eventual OK | Metadata write order matters |
| F5 | Dedup? | Content-addressed optional (hash); checkpoints often unique | CAS for immutable builds; mutable “latest” pointers separate |
| F6 | TTL / retention? | Job scratch 7d; release artifacts longer; legal hold | TTL + compaction-aware deletes |
| F7 | Multi-tenant? | Projects/orgs; quotas on bytes & QPS | Authz + quota service |
| F8 | K8s role? | Deploy API, workers, GC; maybe CSI for scratch—not SoT for blobs | 12-factor services on K8s |
| F9 | Cassandra role? | Metadata, indexes, leases for upload sessions, TTL columns | Partition design critical |
| F10 | CDN/cache? | Hot downloads for popular base images/metadata; checkpoints often cold | Cache metadata + small artifacts; large via direct object/CDN |
| F11 | Versioning? | Immutable versions + mutable tags (`latest`, `prod`) | Pointer rows vs blob rows |
| F12 | Integrity? | Checksums (sha256); optional signatures | Store digest; verify on complete |

**MVP functional scope (lock with interviewer):**

1. Create artifact record (project, type, name, version/tag).  
2. Multipart upload via presigned URLs to object store; complete with checksum.  
3. Cassandra metadata: artifact → blob locator(s), size, digest, ttl, labels.  
4. Download via authorized redirect / presigned GET.  
5. List by project + prefix; get by `(project, name, version)`.  
6. TTL sweeper / object lifecycle rules; soft-delete then purge.  
7. Quotas: bytes stored, uploads/day; RBAC.  
8. K8s deployment: API, completer, GC, CDN invalidator; Cassandra + object store external/managed.

**Out of MVP:**

- Full OCI container registry (layers/protocol)—store **metadata/pointers** only unless asked.  
- In-Cassandra blob storage for large objects.  
- Global active-active multi-region **same-key** metadata without conflict rules.  
- Bit-identical cross-cloud replication of every checkpoint (cost bomb)—make policy-based.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Upload durability | Complete ⇒ durable blob+meta | RPO≈0 after complete ACK |
| N2 | Download availability | High for release artifacts | 99.9%+ GET path |
| N3 | Metadata latency | Interactive list/get | p50 < 50ms, p99 < 300ms in-region |
| N4 | Throughput | Large parallel checkpoints | Saturate NIC/object store; API not in data path |
| N5 | Consistency | Uploader read-after-write | Conditional metadata finalize |
| N6 | Multi-tenant isolation | No cross-project reads | Authz every API; bucket prefixes / keys |
| N7 | Cost | Lifecycle tiers | Hot/warm/cold object classes |
| N8 | Operability on K8s | Rolling deploys, HPA | Stateless API; sticky not required |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Training job finishes → multipart upload checkpoint shards → complete → metadata visible → next job downloads.  
2. CI publishes build artifact → tag `release-1.2` → clients pull via CDN for small tarball.  
3. Image build records metadata (digest, base, labels) pointing at registry elsewhere.  
4. TTL expires scratch checkpoint → GC deletes object + metadata.  
5. User lists `project/foo/checkpoints/` → paginated results.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload aborted mid-multipart | Session TTL; incomplete parts GC’d; no published metadata |
| Complete with wrong checksum | Reject; leave unpublished; abort multipart |
| Dual complete retries | Idempotent complete by `upload_id` / digest |
| Metadata written before blob durable | **Forbidden**—finalize order: blob exists → CAS metadata |
| Hot partition (popular project list)** | Bucket keys; time-bucketing; cache |
| Delete while download in flight | Soft-delete grace; or versioned immutability |
| Tenant exceeds quota mid-upload | Fail complete; abort; optional partial charge policy |
| Cassandra node down | Consistency level tuned; retries; degrade list |
| Object store outage | Fail uploads; reads may succeed if CDN cached (small) |
| Tag move `prod` → new version | Pointer update; old immutable version remains |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants / projects | 100 | 1K | 10K | 100K |
| Artifacts metadata rows | 1M | 10M | 100M | 1B |
| New artifacts / day | 50K | 500K | 5M | 50M |
| Peak complete QPS | ~5 | ~50 | ~500 | ~5K |
| Peak download ops /s | ~50 | ~500 | ~5K | ~50K |
| Avg blob size | 500 MB | 500 MB | 800 MB | 1 GB |
| Bytes written / day | 25 TB | 250 TB | 4 PB | 50 PB |
| Bytes stored (retained) | 500 TB | 5 PB | 50 PB | 500 PB |
| Multipart parts / day | 5M | 50M | 500M | 5B |
| Cassandra nodes | 6 | 12 | 36 | 100+ |
| K8s API replicas | 3 | 10 | 50 | 200 |
| CDN hit ratio (small) | 50% | 60% | 70% | 80% |

**What each jump forces:**

- **10×:** Presigned multipart default; GC workers; quota service; CDN for small.  
- **100×:** Cassandra partition redesign (time buckets); metadata caches; async GC queues; storage classes.  
- **1,000×:** Cell/region artifact homes; hierarchical namespaces; aggressive TTL; cold tier; edge caches; avoid global list scans.

### 1.5 Etc. (Constraints & Assumptions)

- **Object store** (S3/GCS/Blob) is blob SoT; Cassandra is metadata SoT.  
- K8s does **not** store checkpoints on etcd or local PV as durable SoT (scratch OK).  
- Clients can speak HTTPS to object store via presigned URLs (API issues capability tokens).  
- “Container images” in scope = **metadata + pointers**; full registry may be sibling system (Harbor/ECR).  
- Checkpoints often written once, read few times (cold); build artifacts may be hotter.

**Scope statement:**

> Design a multi-tenant artifact store for checkpoints, build outputs, and image metadata: large blobs in object storage, Cassandra for metadata/indexes/TTL, Kubernetes for API/GC services, with presigned transfers, consistent publish, quotas, and CDN/cache for hot small objects—scaling from tens of TB/day toward extreme checkpoint volumes without putting blob bytes in Cassandra.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split paths (critical)

| Path | Baseline | 1,000× | Notes |
|------|----------|--------|-------|
| Metadata QPS (get/list/complete) | tens–hundreds | ~5K–20K | Cassandra + cache |
| Blob data plane bytes/s | GBs | TBs/s aggregate | **Bypass API**—presigned |
| GC delete ops/s | low | high | Lifecycle + workers |
| CDN | small artifacts | same | Not multi-GB checkpoints |

**Deal-breaker:** streaming 1 GB checkpoints through the API pods (K8s CNI melts; cost; failure domains).

### 2.2 Storage math

```text
Baseline: 50K artifacts/day × 500 MB ≈ 25 TB/day ingest
If avg retain 20 days: ~500 TB steady (order-of-magnitude)

1,000×: 50M/day × 1 GB = 50 PB/day ingest  → MUST have TTL/lifecycle
  Even 7-day retain: ~350 PB — cells, cold tier, tenant quotas mandatory

Metadata row ~500 B–2 KB:
1B rows × 1 KB = 1 TB metadata (Cassandra-comfortable with cluster)
```

### 2.3 Multipart math

```text
Part size 64 MB; blob 1 GB → ~16 parts
50M blobs/day × 16 = 800M part uploads/day ≈ 9K parts/s average
Peak 5–10× → design for tens of K part ops/s against object store
API only issues URLs (cheap) + complete (metadata write)
```

### 2.4 Cassandra load

```text
Complete: 5K QPS at 1000× — writes
Get-by-key: 20K QPS — cached
List-by-prefix: expensive if naïvely wide partitions

Partition carefully: (project_id, time_bucket) not single project mega-partition
```

### 2.5 K8s capacity

```text
API CPU: metadata-bound; HPA on RPS/latency
Completer workers: checksum verify optional async; scale on queue depth
GC workers: rate-limited deletes to protect object store
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Data plane through API** (anti-pattern)  
2. **Cassandra hot partitions** on list  
3. **GC lag** → cost blowup  
4. **Quota races** on concurrent uploads  
5. **Tag pointer lost updates**  
6. **Cross-region download** without locality  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Artifact   → logical name in a project (type, tags, versions)
Version    → immutable published snapshot (digest, created_at)
Blob       → bytes in object store (key, size, checksum, storage_class)
UploadSession → multipart in-progress state (TTL)
Pointer/Tag → mutable name → version_id (e.g. prod, latest)
Namespace  → tenant/project for authz + quota
```

**State machine (version):**

```text
UPLOADING → FINALIZING → PUBLISHED → SOFT_DELETED → PURGED
                ↓
             ABORTED / FAILED
```

### 3.2 Blob vs metadata split

| Data | Store | Why |
|------|-------|-----|
| Bytes | Object store | Cost, throughput, multipart, tiers |
| Metadata / indexes | Cassandra | Query by project/name/tag; TTL |
| Upload session | Cassandra (TTL) | Resume/abort |
| Small hot artifacts (<N MB) | Object + CDN | Latency |
| Auth tokens | API + IAM | Presign |

**Deal-breaker:** storing multi-MB blobs as Cassandra `blob` columns.

### 3.3 Consistency model

**Publish protocol (ordered):**

```text
1. Create UploadSession (metadata: UPLOADING)
2. Client PUTs parts directly to object store (presigned)
3. Client Complete(upload_id, parts[], sha256)
4. Service Head/List parts verify size; optional checksum
5. Conditional metadata write: UPLOADING→PUBLISHED with blob keys
6. Update secondary indexes / tag pointers
7. ACK to client  # now read-after-write for get-by-version
```

**Invariants:**

- No `PUBLISHED` without blob durable.  
- Complete idempotent on `upload_id`.  
- Tag updates use LWT/CAS or version compare.  

**List consistency:** eventual via indexes; get-by-primary-key strong enough with CL=LOCAL_QUORUM.

### 3.4 Cassandra data model (sketch)

```text
artifacts_by_id (
  project_id, artifact_id,
  name, type, created_at, ...
) PRIMARY KEY (project_id, artifact_id)

versions_by_artifact (
  project_id, artifact_id, version_id,
  state, digest, size_bytes, blob_keys frozen<list<text>>,
  ttl_seconds, created_at, ...
) PRIMARY KEY ((project_id, artifact_id), version_id)

-- list recent: time bucket to avoid huge partitions
versions_by_project_time (
  project_id, day_bucket, created_at, artifact_id, version_id,
  name, type, size_bytes, state
) PRIMARY KEY ((project_id, day_bucket), created_at, version_id)
WITH CLUSTERING DEFAULT DESC

tags (
  project_id, artifact_name, tag,
  version_id, updated_at
) PRIMARY KEY ((project_id, artifact_name), tag)

upload_sessions (
  upload_id,
  project_id, artifact_id, state, parts_info, expires_at
) PRIMARY KEY (upload_id)
-- table TTL or column TTL on expires

quota_usage (
  project_id,
  bytes_stored counter,          -- or non-counter with CAS
  artifacts_count counter
) PRIMARY KEY (project_id)
```

**Partition warnings:**

- Don’t use `PRIMARY KEY (project_id)` alone for all versions.  
- Day buckets (or hour at extreme) for list.  
- `gpu_uuid`-style high cardinality as partition key only when lookups are point reads.

### 3.5 Object key layout

```text
s3://artifacts/{cell}/{project_id}/{artifact_id}/{version_id}/{part_or_blob}
# content-addressed optional:
s3://artifacts/{cell}/cas/{sha256}
```

CAS dedup for immutable builds; checkpoints often unique → per-version keys simpler.

### 3.6 TTL & GC

```text
On publish: set expires_at = now + ttl (policy by type)
Cassandra: optional TTLs on scratch tables; published rows sweeper-driven for control
Sweeper:
  1. Find expired PUBLISHED/SOFT_DELETED
  2. Enqueue object deletes (rate limited)
  3. Delete index rows after object delete ACK / after grace
Object store lifecycle rules: backup safety net for abandoned multipart + prefixes
```

**Order:** prefer delete blob then metadata (or soft-delete metadata first to hide, then purge blob)—pick and document. Common: **hide metadata first (soft-delete)** so new reads stop; async purge bytes; then hard-delete metadata.

### 3.7 Multi-tenant quotas & authz

| Control | Mechanism |
|---------|-----------|
| Authn | OIDC / mTLS service accounts |
| Authz | RBAC: `artifact:write` on project |
| Bytes quota | Redis/Cassandra usage + admit on complete |
| Rate limits | Token bucket per project on init/complete |
| Key isolation | Object prefix per project; deny cross listing |

**Quota race:** reserve bytes on init (estimate); settle on complete; release on abort.

### 3.8 Kubernetes deployment patterns

```text
Namespace: artifact-system
Deployments:
  artifact-api        (stateless, HPA)
  artifact-completer  (optional async verify)
  artifact-gc         (sharded workers)
  artifact-indexer    (maintain list tables)
PDB + rolling updates
Config via ConfigMaps/Secrets (object creds via IRSA/Workload Identity—not long-lived in Secret if possible)
NetworkPolicies: API ingress; workers egress to Cassandra/object store
ServiceMonitor / metrics
Cassandra: operator (K8ssandra/cass-operator) OR managed outside cluster
Object store: external managed
```

**Anti-patterns:** StatefulSet local disk as durable blob store; etcd for artifact bytes; single PVC for all tenants.

### 3.9 CDN & cache

| Content | Cache | Notes |
|---------|-------|-------|
| Metadata GET | Application cache / Redis | Short TTL; invalidate on publish/tag |
| Small artifacts (<32–64 MB) | CDN | Cache-Control; signed URLs careful |
| Large checkpoints | Direct object store / private CDN origin | Usually low hit rate; locality > CDN |
| List queries | Cache page tokens carefully | Invalidation hard—short TTL |

**Signed URL + CDN:** use cookies or CDN features that honor signatures; don’t make URLs world-cacheable if secret.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Blob bytes | Object store | Scale/cost | Cassandra blobs |
| Metadata | Cassandra | TTL, write throughput | Single PG at 1000× lists |
| Upload path | Presigned multipart | Bypass API | Stream via API pods |
| Tags | Separate pointer rows + CAS | Safe moves | Overwrite immutable version row |
| GC | Soft-delete + queue | Controllable | Only object lifecycle (metadata orphans) |
| Multi-region | Home cell for metadata | Avoid dual writers | Active-active same version_id |
| Dedup | Optional CAS | Complexity | Forced CAS for unique checkpoints |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
+-------------+     +------------------+     +------------------+
| Jobs / CI   |---->| artifact-api     |---->| Cassandra        |
| Users       |     | (K8s Deployment) |     | metadata/indexes |
+------+------+     +--------+---------+     +------------------+
       |                     |
       | presigned PUT/GET   v
       |            +------------------+
       +----------->| Object Store     |
                    | (multipart)      |
                    +--------+---------+
                             ^
+------------------+         | deletes
| artifact-gc      |---------+
| artifact-indexer |
+--------+---------+
         |
         v
+------------------+     +------------------+
| Redis metadata   |     | CDN (small objs) |
| cache (optional) |     +------------------+
+------------------+
```

### 4.2 Sequence: multipart publish

```text
Client                API                 Object Store           Cassandra
  |-- InitUpload ---->|                     |                      |
  |                   |-- create session -------------------------->|
  |<- part URLs ------|                     |                      |
  |-- PUT part1 ---------------------------->|                      |
  |-- PUT partN ---------------------------->|                      |
  |-- Complete ------>|-- list/verify ----->|                      |
  |                   |-- PUBLISHED LWT --------------------------->|
  |                   |-- update indexes/tags --------------------->|
  |<- version_id -----|                     |                      |
  |-- GET version --->|                     |                      |
  |<- presigned GET --|                     |                      |
  |-- GET bytes ---------------------------->|                      |
```

### 4.3 Sequence: TTL GC

```text
GC worker → query expired soft candidates (bucketed)
GC → soft-delete tag visibility / state=SOFT_DELETED
GC → enqueue DeleteObject(keys)
Object store ACK → delete Cassandra rows / tombstones controlled
Metrics: bytes_reclaimed, lag_seconds
```

### 4.4 Sequence: tag move

```text
API: PutTag(project, name, "prod", version=V2)
Cassandra LWT: UPDATE tags SET version_id=V2 IF version_id=V1
Success → invalidate cache
Readers of tag=prod see V2; V1 immutable remains downloadable by version_id
```

### 4.5 K8s runtime view

```text
                    +-------------------------+
                    |        Ingress          |
                    +-----------+-------------+
                                |
                    +-----------v-------------+
                    | artifact-api (HPA)      |
                    +---+-----------------+---+
                        |                 |
           +------------v--+       +------v---------+
           | Cassandra     |       | Object Store   |
           | (operator /   |       | (external)     |
           |  managed)     |       +----------------+
           +---------------+
           +------------------+
           | gc / indexer     |
           | Deployments      |
           +------------------+
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | PUBLISHED ⇒ blob exists & verified size/digest | Complete checks before CAS |
| R2 | Complete idempotent | `upload_id` primary; state machine |
| R3 | No cross-project access | Authz + key prefix |
| R4 | Quota not silently exceeded | Reserve/settle |
| R5 | Tag pointer single-writer semantics | LWT/CAS |
| R6 | Incomplete uploads bounded | Session TTL + multipart abort |
| R7 | GC eventual but complete | Queue + lifecycle safety net |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| API pod crash mid-complete | Client retry complete; idempotent |
| Cassandra unavailable | Fail writes; reads depending on CL |
| Object store 503 | Client retries parts; session remains |
| GC deletes live object | Prevent via state checks + generation |
| Split brain tag update | LWT prevents silent lost update |

### 5.2 Scalability

**1×:** API + managed object store + small Cassandra; streams avoided.

**10×:** HPA; Redis cache; CDN small; GC fleet; quotas.

**100×:** Time-bucketed list tables; cell-local homes; async indexer; storage classes (hot→cold).

**1,000×:** Regional cells; no global list; hierarchical namespaces; cold tier default for checkpoints; rate-limited GC; metadata caching tiers.

**Backpressure:**

- InitUpload rejects when project quota/reserve exhausted.  
- GC rate limit protects object store delete API.  
- List requires prefix/time window at large scale.

### 5.3 Maintainability

- Explicit artifact **types** with default TTLs.  
- Admin tooling: find orphans (blob without meta / meta without blob).  
- Schema migration playbooks for Cassandra.  
- Chaos: kill API mid-complete; verify idempotency.  
- Cost dashboards: bytes by project/type/class.

### 5.4 Ownership resolution

| Concern | Owner |
|---------|-------|
| Bytes durability | Object store |
| Publish visibility | Artifact API + Cassandra |
| Job checkpoint schedule | Training/scheduler systems |
| Image layers pull protocol | OCI registry (sibling) |
| CDN config | Edge / platform |
| K8s scheduling of API pods | Cluster ops |

**Contradiction trap:** building a full Docker registry inside this design when interviewer only asked artifact metadata—scope control.

### 5.5 Consistency deep dive

| Operation | Consistency approach |
|-----------|----------------------|
| Get by version_id | Point read LOCAL_QUORUM |
| Get by tag | Read tag → version; rare race→retry |
| List | Eventually consistent index |
| Complete | Ordered verify + LWT state transition |
| Delete | Soft then purge |

**Read-your-writes:** return version_id to uploader; clients fetch by id (not list).

### 5.6 Cassandra anti-patterns to call out

1. Unbounded partition (all project versions one partition).  
2. Secondary index on high-cardinality `digest` as sole access.  
3. Counters for quotas if you need precise CAS accounting—prefer LWT or external quota service.  
4. Large collections for thousands of blob parts in one row—store parts table or object-complete only.  
5. TTLing published rows blindly without blob GC coordination.

### 5.7 Multipart & huge checkpoints

```text
Checkpoint 2 TB = 2048 parts @ 1 GB  (or 32K @ 64 MB)
Prefer larger parts within object-store limits
Parallel PUT from training nodes
Complete payload lists part ETags
Optional: shard checkpoint as many artifacts + manifest artifact
```

**Manifest pattern:**

```text
manifest.json (small, CDN-able) → list of blob digests
improves retry granularity vs one mega-object
```

### 5.8 Multi-region

```text
Home cell per project for metadata writes
Blobs written to regional bucket
Cross-region read: replicate selectively (release artifacts) or redirect
DR: backup Cassandra + object replication rules
Failover: fence old cell generation
```

**Deal-breaker:** dual-active tag updates in two regions without CRDT/LWW policy.

### 5.9 Security

- Presigned URLs short TTL; least privilege.  
- SSE-KMS per tenant optional.  
- Virus scan async for CI artifacts (policy).  
- Signed artifacts (cosign-like) metadata fields.  
- NetworkPolicies on K8s; IRSA for S3.

### 5.10 Fairness / noisy neighbor

- Per-project rate limits on init/complete.  
- Separate GC queues so one tenant’s mass delete doesn’t starve others.  
- Object store prefix + request rate monitoring.  
- CDN only for eligible classes (don’t let one tenant pin edge with huge files).

### 5.11 Node failure / K8s pod failure

- API stateless → retry.  
- GC worker lease chunks of work (fencing token).  
- Incomplete uploads don’t publish.  
- Cassandra replica handles node loss per RF/CL.

### 5.12 Observability

| Dashboard | Metrics |
|-----------|---------|
| API | init/complete QPS, latency, errors |
| Uploads | abandoned sessions, part failure rate |
| Storage | bytes by tier/project, growth |
| GC | lag, deletes/s, orphan count |
| Cassandra | pending compactions, hot partitions |
| CDN | hit ratio, origin bandwidth |

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Blob/metadata split; never Cassandra for GB bytes.  
2. Presigned multipart publish protocol + invariants.  
3. Cassandra keys (time buckets, tags).  
4. TTL/GC order; quotas.  
5. K8s deployment pattern.  
6. CDN for small; scale cells at 1000×.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Init/complete, Cassandra meta, object blobs, get/list, basic TTL, RBAC |
| 10× | CDN small, quotas, GC workers, cache |
| 100× | Time-bucket indexes, storage classes, cell homes |
| 1,000× | Aggressive TTL, cold tier, federated namespaces, rate-limited GC |

### 6.3 Top risks

1. Proxying blob bytes through API.  
2. Hot Cassandra partitions.  
3. PUBLISHED without durable blob.  
4. GC orphaning / premature delete.  
5. Quota races.  
6. Treating system as full OCI registry accidentally.

### 6.4 One-sentence design

> A K8s-hosted artifact control plane that publishes immutable versions via presigned multipart uploads to object storage, records them in carefully partitioned Cassandra metadata with tag pointers and TTL/GC, and accelerates small hot objects with CDN—while keeping large checkpoint bytes off the API and out of Cassandra.

---

## 7. Deeper / Related Interview Questions

### 7.1 Split & scope

**Q: Why Cassandra + object store?**  
A: Metadata query/TTL vs cheap durable bulk bytes.

**Q: Why not Postgres?**  
A: Fine at MVP; write/list scale and TTL patterns often push wide-row/NoSQL—or sharded PG. Cassandra is a valid interview choice if modeled well.

**Q: Why not store checkpoints on HDFS/PVC?**  
A: Possible elsewhere; object store + metadata fits multi-tenant cloud ops and lifecycle.

**Q: Full image registry?**  
A: Only if asked; otherwise metadata/pointers + external registry.

### 7.2 Consistency

**Q: How do you get read-after-write?**  
A: Finalize metadata after blob verify; return version_id; read by key.

**Q: What CL for writes?**  
A: LOCAL_QUORUM typical; discuss trade-offs.

**Q: List shows artifact before download works?**  
A: Shouldn’t if publish order correct; indexes updated after PUBLISHED.

**Q: Tag update races?**  
A: LWT IF version_id=...

### 7.3 Cassandra modeling

**Q: How to list latest 100 artifacts in a project?**  
A: `(project_id, day_bucket)` partitions; query recent buckets; avoid one giant partition.

**Q: Secondary indexes?**  
A: Sparingly; prefer table-per-query.

**Q: TTL on published rows?**  
A: Coordinate with blob GC; sweeper often clearer than blind TTLs.

**Q: Counters for quotas?**  
A: Non-idempotent; prefer reserve/settle service.

### 7.4 Uploads & large files

**Q: Why multipart?**  
A: Resume, parallelism, size limits.

**Q: Checksum when?**  
A: Client provides sha256; server verifies on complete (or async then mark).

**Q: Manifest vs single blob?**  
A: Manifest for huge checkpoints—better retries.

**Q: Can API stream bytes?**  
A: Only tiny files; never default for checkpoints.

### 7.5 TTL & GC

**Q: Soft vs hard delete?**  
A: Soft hide first; async purge; then metadata hard delete.

**Q: Orphan blobs?**  
A: Lifecycle rules + periodic reconciler comparing prefixes vs Cassandra.

**Q: Legal hold?**  
A: Clear TTL exemption flag; exclude from sweeper.

### 7.6 Multi-tenant & security

**Q: Cross-tenant read?**  
A: Authz fail; separate prefixes; no shared guessable URLs without signature.

**Q: Presigned URL leak?**  
A: Short expiry; scope to single key; audit.

**Q: Quota bypass via multipart abandon?**  
A: Session reserve + abort GC releases; bill incomplete if policy requires.

### 7.7 K8s

**Q: Where does Cassandra run?**  
A: Operator in-cluster or managed; call trade-offs (ops vs control).

**Q: HPA signals?**  
A: RPS, latency, CPU; not blob bandwidth (data plane elsewhere).

**Q: Why NetworkPolicy?**  
A: Limit blast radius; workers only reach stores.

**Q: PersistentVolume for artifacts?**  
A: Scratch only—not durable multi-tenant SoT.

### 7.8 CDN/cache

**Q: Cache checkpoints at edge?**  
A: Usually low hit rate / large—prefer regional object locality.

**Q: Invalidate on tag move?**  
A: Purge metadata cache keys; CDN for versioned URLs often immutable (cache forever by digest).

**Q: Signed URLs vs public CDN?**  
A: Private artifacts need signed/ tokenized access.

### 7.9 Scale drills

**Q: 50 PB/day ingest feasible?**  
A: Only with extreme cells, short TTL, and saying no to unbounded retain—push back on requirements.

**Q: 1B metadata rows?**  
A: Fine if partitioned; bad if global scans.

**Q: Hot project?**  
A: Cache, bucket splits, rate limits, maybe dedicated cell.

### 7.10 Comparison traps

**Q: vs S3 alone?**  
A: Listing/tagging/authz/quotas/TTL product logic needs metadata plane.

**Q: vs Artifactory/Nexus?**  
A: Similar product space; interview wants your consistency + data model reasoning.

**Q: vs Docker registry?**  
A: Layer protocol & GC specifics; don’t conflate unless scoped.

**Q: vs Git LFS?**  
A: Different UX; similar pointer+blob idea.

### 7.11 Reliability drills

**Q: Complete succeeds, client never hears ACK?**  
A: Retry complete → idempotent PUBLISHED.

**Q: Metadata PUBLISHED, blob missing?**  
A: Bug—repair job; prevent via verify order.

**Q: GC vs download race?**  
A: Soft-delete grace; version immutability; 404 after grace.

### 7.12 Interview traps (high value)

- Bytes through API pods.  
- Blobs in Cassandra.  
- Unbounded partitions.  
- Publish before blob durable.  
- Forget incomplete multipart GC.  
- Counters as precise quotas.  
- Full registry scope creep.  
- CDN for multi-GB as default.  
- Dual-active tag writers.  
- List-as-SoT for read-after-write.  
- etcd/PV as durable store.  
- No soft-delete grace.  
- Ignoring cost of retain-all checkpoints.  
- Presigned URL forever.  
- Single global bucket listing.

---

## 8. Appendices

### 8.1 Schema sketches (CQL)

```cql
CREATE TABLE versions_by_artifact (
  project_id text,
  artifact_id uuid,
  version_id uuid,
  name text,
  type text,
  state text,
  digest text,
  size_bytes bigint,
  blob_keys frozen<list<text>>,
  storage_class text,
  expires_at timestamp,
  created_at timestamp,
  PRIMARY KEY ((project_id, artifact_id), version_id)
);

CREATE TABLE versions_by_project_time (
  project_id text,
  day_bucket date,
  created_at timeuuid,
  version_id uuid,
  artifact_id uuid,
  name text,
  type text,
  state text,
  size_bytes bigint,
  PRIMARY KEY ((project_id, day_bucket), created_at, version_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

CREATE TABLE tags (
  project_id text,
  artifact_name text,
  tag text,
  version_id uuid,
  updated_at timestamp,
  PRIMARY KEY ((project_id, artifact_name), tag)
);

CREATE TABLE upload_sessions (
  upload_id uuid PRIMARY KEY,
  project_id text,
  artifact_id uuid,
  object_prefix text,
  state text,
  expected_size bigint,
  created_at timestamp
);
-- use TTL on inserts for session expiry
```

### 8.2 API checklist

- [ ] `POST /v1/artifacts/{name}/uploads` init  
- [ ] `POST /v1/uploads/{id}/complete`  
- [ ] `POST /v1/uploads/{id}/abort`  
- [ ] `GET /v1/artifacts/{name}/versions/{id}`  
- [ ] `GET /v1/artifacts/{name}/tags/{tag}`  
- [ ] `PUT /v1/artifacts/{name}/tags/{tag}`  
- [ ] `GET /v1/artifacts?prefix=&day=` list  
- [ ] `DELETE /v1/versions/{id}` soft-delete  
- [ ] Admin quota APIs  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Artifact | Named logical object in a project |
| Version | Immutable published snapshot |
| Tag / pointer | Mutable ref to a version |
| Blob | Bytes in object store |
| Presigned URL | Time-limited direct access capability |
| Multipart | Parallel/resumable large upload |
| CAS | Content-addressed storage by digest |
| Soft-delete | Hidden pending purge |
| Home cell | Single-writer region for project metadata |
| Manifest | Small index listing many blob parts |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Presigned upload, Cassandra meta, complete ordering, basic TTL |
| 10× | Quotas, GC workers, CDN small, cache |
| 100× | Time-bucket lists, storage classes, cell homes |
| 1000× | Cold default, aggressive TTL, sharded GC, no global list |

### 8.5 Upload session sketch

```text
InitUploadRequest  { project, name, type, size_estimate, ttl_policy, checksum_algo }
InitUploadResponse { upload_id, part_size, urls: [{part, url, expires}] }

CompleteRequest    { upload_id, parts: [{n, etag}], sha256 }
CompleteResponse   { version_id, digest, size }

AbortRequest       { upload_id }
```

### 8.6 TTL policy examples

| Type | Default TTL | Notes |
|------|-------------|-------|
| checkpoint_scratch | 7d | Training intermediates |
| checkpoint_release | 180d | Promoted |
| build_artifact | 90d | CI outputs |
| image_metadata | 365d | Pointers |
| legal_hold | none | Explicit flag |

### 8.7 Interview “say this” summary (60 seconds)

> Artifact store with object storage for bytes and Cassandra for metadata: clients upload via presigned multipart, API only finalizes after verifying parts, then CAS-publishes immutable versions and tag pointers. Kubernetes runs stateless API/GC workers; never put GB blobs in Cassandra or through API pods. TTL soft-delete + rate-limited purge; quotas and RBAC per project; CDN for small hot objects; cells and time-bucketed indexes at scale.

### 8.8 Extra traps

| Trap | Pushback |
|------|----------|
| API streams 1GB | Presign data plane |
| Blob in C* | Object store |
| One partition/project | Time buckets |
| Publish before PUT | Order invariant |
| Forever retain all checkpoints | Cost; TTL |
| Full OCI in MVP | Scope |
| CDN multi-GB default | Locality/direct |
| Counter quotas only | Reserve/settle |

### 8.9 Reliability test plan

1. Retry complete after success → same version_id.  
2. Complete with bad sha256 → not PUBLISHED; parts aborted.  
3. Kill API mid-complete → client retry recovers.  
4. Soft-delete → GET tag 404; purge later removes bytes.  
5. Quota exceeded → init/complete fails cleanly.  
6. Tag LWT conflict → loser retries.  
7. Orphan reconciler removes abandoned multipart.

### 8.10 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Complete latency (metadata) | p99 < 500ms |
| InitUpload latency | p99 < 200ms |
| Read-after-write success | > 99.99% by version_id |
| GC lag | < 24h for expired |
| Orphan bytes | < 1% of stored |

### 8.11 Related systems map

```text
Clients → artifact-api (K8s) → Cassandra (meta)
              ↓ presign
         Object Store ← GC workers
              ↓
         CDN (small / digest URLs)
Scheduler/Training jobs use API for checkpoint publish/fetch
OCI Registry (sibling) for container layers
```

### 8.12 Estimation cheat-sheet

```text
bytes/day ≈ artifacts/day × avg_size
parts/day ≈ bytes/day / part_size
metadata_storage ≈ rows × ~1KB

API QPS ≠ bytes/s
  data plane bandwidth >> control plane QPS

1B rows × 1KB = 1TB metadata  (OK)
50PB/day ingest without TTL = not OK
```

### 8.13 Example metadata document

```json
{
  "project_id": "p_123",
  "artifact_id": "a_9c",
  "name": "llm-checkpoint",
  "version_id": "v_55",
  "type": "checkpoint_scratch",
  "state": "PUBLISHED",
  "digest": "sha256:abc...",
  "size_bytes": 549755813888,
  "blob_keys": ["cell-a/p_123/a_9c/v_55/manifest.json", ".../shard-0001"],
  "expires_at": "2026-08-13T00:00:00Z",
  "tags": ["latest"]
}
```

### 8.14 Manifest for sharded checkpoint

```json
{
  "digest": "sha256:manifest...",
  "shards": [
    {"key": ".../shard-0000", "sha256": "...", "size": 8589934592},
    {"key": ".../shard-0001", "sha256": "...", "size": 8589934592}
  ]
}
```

### 8.15 K8s resource sketch

```yaml
# conceptual
Deployment artifact-api:
  replicas: 3..N (HPA)
  serviceAccount: artifact-api  # IRSA
  resources: cpu/mem for JSON+auth only
Deployment artifact-gc:
  replicas: sharded by project hash
PDB: minAvailable 2 for API
NetworkPolicy: allow ingress 443; egress C*, S3
```

### 8.16 Delete ordering (chosen)

```text
1) Authz check
2) Soft-delete metadata (state=SOFT_DELETED); remove tag refs
3) Wait grace G (downloads in flight)
4) Delete object keys (rate limited)
5) Hard-delete metadata / tombstone compact later
Safety net: object lifecycle on prefix for abandoned uploads
```

### 8.17 Consistency checklist for whiteboard

- [ ] Blob durable before PUBLISHED  
- [ ] Idempotent complete  
- [ ] Tag CAS  
- [ ] Read-your-writes via version_id  
- [ ] List secondary / eventual OK  
- [ ] GC cannot delete PUBLISHED without state transition  

---

*End of design doc. Open with §3.2 blob/metadata split; whiteboard §3.3–3.8 publish/C*/TTL/K8s; close with traps §7.12.*
