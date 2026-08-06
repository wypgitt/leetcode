# System Design: Delta-like Transaction Log / Table Format

> **Focus areas:** Optimistic concurrency · Commit protocol · Checkpoints · Snapshot reads · Compaction · Vacuum · Deletion vectors · Streaming idempotent sinks · Iceberg comparison  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct invariants, explicit commit semantics, honest conflict/retry behavior, vacuum safety, snapshot isolation guarantees  
> **Interview theme:** Databricks — lakehouse table format / transaction log core

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

Goal: design a **Delta-like transaction log** layered on object storage (S3/ADLS/GCS) that turns a folder of Parquet files into an **ACID table** with concurrent writers, snapshot reads, time travel, and operational maintenance (checkpoint, compact, vacuum)—the core of a lakehouse table format.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the unit of transaction? | **One table** = data files + `_delta_log/` | Per-table serial version line; no cross-table 2PC in MVP |
| F2 | What does a commit mean? | Atomic publish of a new table version | Single atomic log entry (or multi-part commit file) bumps version |
| F3 | Log contents? | **Actions**: add/remove files, metadata, protocol, txn, domainMetadata | JSON/Avro lines; replay reconstructs snapshot |
| F4 | Reader guarantee? | **Snapshot isolation** — consistent file set at version V | Never mix files from two versions; pin version at read start |
| F5 | Writer concurrency? | **Optimistic** — many writers, retry on conflict | Read version N, write data, commit N+1 only if still at N |
| F6 | Conflict detection? | Overlapping writes to same files/partitions or blind append rules | Predicate / partition overlap or “whole table” for small tables |
| F7 | Checkpoints? | Periodic materialized snapshot of log tail | Parquet checkpoint every N commits; bound metadata read |
| F8 | Time travel? | Query `AS OF VERSION v` or `TIMESTAMP t` | Version monotonic; timestamp from commit actions |
| F9 | Schema evolution? | Add columns, type widening per rules | `metaData` action replaces prior; enforce compatibility |
| F10 | Updates/deletes? | Copy-on-write rewrite **or** deletion vectors (DV) | MVP: rewrite files; scale: DV + lazy rewrite |
| F11 | Change Data Feed (CDF)? | Optional row-level change stream per commit | `cdc` actions or derived from add/remove + DV |
| F12 | Stats for pruning? | Min/max/nullCount per file per column | `add` action carries stats; reader skips files |
| F13 | Vacuum? | Delete orphaned data files after retention | Must respect time-travel retention; irreversible |
| F14 | Log compaction? | Merge small JSON commits into fewer files | `_last_checkpoint` + checkpoint writer |
| F15 | Streaming sink? | Idempotent micro-batch commits | `(batchId, txn appId)` in `txn` action |
| F16 | Multi-table transaction? | Nice-to-have | Defer; mention catalog-level protocols Phase 2 |
| F17 | UniForm / interop? | Read same data as Iceberg/Hudi | Dual metadata optional; compare in interview |

**MVP functional scope (lock with interviewer):**

1. Append-only **add** commits with OCC on object storage (put-if-absent on next log file).
2. Snapshot read: latest checkpoint + tail JSON → active file list + schema + partition spec.
3. **Remove** actions for overwrite/MERGE (copy-on-write file replacement).
4. Checkpoint every **100 commits** (configurable); `_last_checkpoint` pointer.
5. Time travel by version; timestamp resolution via commit timestamps.
6. Basic conflict: two writers cannot commit overlapping **add+remove** on same partition set without retry.
7. `txn` action for streaming idempotency (`appId`, `batchId`).
8. Vacuum with `retentionHours` guard (default 7 days) — document footgun.

**Out of MVP (explicitly defer):**

- Multi-table atomic commit across tables
- Row-level locking / serializable isolation beyond snapshot + OCC
- Automatic liquid clustering / Z-order maintenance as productized service
- Active-active multi-writer same table across regions without external coordinator
- Instant blind `INSERT` with zero conflict check on partitioned tables under heavy concurrent MERGE

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Commit latency? | Batch analytics | p50 < 2s, p99 < 15s (incl. data write + log commit) |
| N2 | Read latency (metadata)? | Interactive queries | p99 metadata load < 500ms for 1M-file table with checkpoint |
| N3 | Correctness | No torn reads | Reader never sees partial commit |
| N4 | Durability | Committed version survives process crash | Log commit is the durability barrier |
| N5 | Writer throughput? | Many concurrent jobs | 10–100 commits/min/table baseline; OCC retry under conflict |
| N6 | Conflict rate? | Observable, bounded retries | Exponential backoff; alert if > 20% conflicts |
| N7 | Time travel retention | Compliance + debug | Default 30 days versions; vacuum obeys min retention |
| N8 | Storage efficiency | Avoid log explosion | Checkpoint + log compaction; DV reduce rewrite amplification |
| N9 | List scalability? | Object store LIST is expensive | Do not LIST data dir for truth; trust log |
| N10 | Protocol evolution | Forward compatible readers | `protocol` action minReaderVersion / minWriterVersion |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Single writer append batch → write Parquet files → commit log version N → readers at N see new files.
2. Reader pins version 42 → scans file list from checkpoint+tail → predicate pruning via stats → correct result.
3. MERGE job: read v100 → write new files + remove old → commit v101 succeeds → old files eligible for vacuum after retention.
4. Streaming batch 7: first attempt crashes after commit → retry sees `txn` for `(appId,7)` → no-op success.
5. Checkpoint at v9000 → new reader loads one Parquet checkpoint + logs 9001+ only.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two writers commit same version | Exactly one wins put-if-absent; other retries from new head |
| Writer crash before log commit | Uncommitted data files orphaned; vacuum cleans after retention |
| Writer crash after log commit | Version visible; no rollback of published version |
| Partial multi-file commit | **Forbidden** — single atomic commit file per version (or all parts present before publish) |
| Reader reads during commit | Sees vN or vN+1 entirely; never hybrid |
| Stale reader cache | Refresh log tail; version pin prevents mixing |
| Checkpoint corrupt / partial | Fall back to JSON replay from version 0 or last good checkpoint |
| Vacuum deletes time-travel file | **Data loss** — enforce retentionHours + dry-run listing |
| Schema breaking change | Writer bumps protocol; reject or coerce per rules |
| Concurrent vacuum + commit | Vacuum uses snapshot at start; never delete file referenced by retained version |
| S3 eventual consistency (legacy) | Use strong read-after-write for commit path; list not used for commit decision |
| Blind append conflict miss | Document: append-only streams may skip file overlap check — risk duplicate rows if misused |
| DV + compaction interaction | Compaction rewrites base without DV; new file drops DV |
| Iceberg double-write | UniForm writes second metadata — out of MVP |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tables (managed) | 5K | 50K | 500K | 5M |
| Commits/day/table (hot) | 1K | 10K | 100K | 1M |
| Data files/table | 10K | 100K | 1M | 10M |
| Log JSON files/table | 1K | 10K | 100K | 1M (must checkpoint) |
| Table size (hot) | 10 TB | 100 TB | 1 PB | 10 PB |
| Concurrent readers/table | 50 | 500 | 5K | 50K |
| Concurrent writers/table | 2–5 | 10 | 50 | 100+ (partition isolation) |
| Metadata read QPS (catalog) | 200 | 2K | 20K | 200K |
| Checkpoint size | 5 MB | 50 MB | 500 MB | 5 GB (partitioned checkpoint) |
| Vacuum scan scope | 10K files | 100K | 1M | incremental vacuum + SHALLOW CLONE awareness |

**What each jump forces:**

- **10×:** Checkpoint every 100 commits; cache log tail in driver/coordinator; partition-scoped conflict checks.
- **100×:** Deletion vectors; async checkpoint/compaction workers; incremental vacuum; stats index sidecar.
- **1,000×:** Partitioned checkpoints; table per cell; log shipping cache; conflict avoidance via table locks / single-writer hot partitions; UniForm only where needed.

### 1.5 Etc. (Constraints & Assumptions)

- Object storage is **authoritative** for bytes; no HDFS block reports.
- Commit atomicity relies on **single-key create** semantics (`If-None-Match: *` on S3, `create-if-not-exists` on ADLS).
- **Log is source of truth** for which data files belong to the table; never infer from LIST on `data/`.
- Data files are **immutable** once written; updates = new files + remove old in log.
- Clocks: commit timestamps from writer wall clock; not used for ordering across writers (version integer orders).
- One **table directory** = `{tableRoot}/_delta_log/` + `{tableRoot}/...` data paths.

**Scope statement:**

> Design a Delta-like transaction log on object storage with OCC commits, checkpoint-accelerated snapshot reads, copy-on-write + deletion vectors, safe vacuum with retention, streaming idempotent sinks, and a clear comparison to Apache Iceberg—scaling from thousands of commits/day to millions via checkpointing, compaction, and partition-scoped concurrency.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Metadata read amplification (the real cost)

Without checkpoint, cold snapshot at version V requires reading V JSON files:

```text
Baseline: 10K commits/table, no checkpoint
Cold read = 10K LIST + 10K GET (JSON) ≈ 10K × 4 KB = 40 MB metadata
At 500 concurrent readers starting fresh → 5M GETs — unacceptable

With checkpoint every 100 commits:
JSON tail ≤ 100 files + 1 checkpoint Parquet (~5 MB)
Cold read ≈ 100 × 4 KB + 5 MB ≈ 5.4 MB — 7× better; still need checkpoint
At 100K commits without checkpoint: 400 MB+ metadata read per snapshot
```

**Critical insight:** The design problem is **bounding metadata read**, not “store Parquet in a folder.”

### 2.2 Commit path latency budget

```text
Typical MERGE commit:
  Plan + scan input:        (query-dependent, seconds–minutes)
  Write new Parquet files:  1–30s
  Build commit actions:     50–200ms
  Atomic log put:           50–500ms (S3 PUT latency)
  Publish to catalog:       20–100ms optional

Log-only micro-batch append (small):
  Data write 200ms + log put 100ms → ~300ms p50
```

Say aloud: **data write dominates**; still optimize log tail cache because metadata storms hurt query startup.

### 2.3 Log storage growth

```text
Average commit JSON size:
  10 add actions × 2 KB stats each ≈ 20 KB/commit

1K commits/day × 20 KB ≈ 20 MB/day/log/table
100K commits/day (100× hot table) ≈ 2 GB/day
Annual ≈ 730 GB log JSON alone — checkpoint + log compaction mandatory

Checkpoint every 100 commits:
  1 Parquet ~5 MB replaces 100 × 20 KB = 2 MB JSON — checkpoint larger but 1 GET vs 100
```

### 2.4 Data file churn (copy-on-write vs DV)

```text
UPDATE 1% of 1 TB table, 1000 files, copy-on-write:
  Rewrite ~10 files × 1 GB = 10 GB written per UPDATE commit

Same with deletion vectors (DV):
  Write DV file ~few MB + optional new rows file
  Read path: base + DV merge — 100× less write amplification for wide tables

100 concurrent UPDATE writers without partition isolation:
  Conflict rate → retry storm — partition scope essential
```

### 2.5 Vacuum scope

```text
Table 100 TB, 100K files, daily churn 1K files removed from log
Vacuum lists candidate orphans: compare log-referenced set vs storage LIST (expensive)

Incremental vacuum: track referenced files from last N versions only if retention allows
LIST 100K keys @ 1K LIST pages → minutes + API cost — run off critical path
```

### 2.6 Streaming sink throughput

```text
Micro-batch every 30s → 2 commits/min/table/stream
10 streams same table → 20 commits/min → 28K/day — moderate OCC conflicts if same partition

txn idempotency: duplicate retry of batch 7 → O(1) log tail scan for txn action
```

### 2.7 Bottlenecks (ranked)

1. Uncheckpointed log tail → metadata read explosion  
2. Copy-on-write UPDATE/MERGE on wide tables  
3. OCC conflict storms on hot partitions  
4. Vacuum LIST cost + accidental retention violation  
5. Checkpoint writer lagging hot table  
6. Reader cache staleness causing wrong snapshot if version not pinned  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
TableSnapshot     → version, schema, partitionSpec, files[], protocol, metadata
LogStore          → atomicPut(path, bytes) with create-if-absent
DeltaLog          → tableRoot/_delta_log/
CommitActions     → add | remove | metaData | protocol | txn | cdc | domainMetadata
Checkpoint        → Parquet materialization of actions up to version V
SnapshotProvider  → getSnapshotAt(version?) → TableSnapshot
ConflictChecker   → overlapping(add, remove, readPredicates) → bool
Maintenance       → checkpoint, compact, vacuum, optimize
StreamingTxn      → (appId, batchId) → idempotent commit gate
```

### 3.2 Physical layout

```text
s3://bucket/warehouse/db/table/
  _delta_log/
    00000000000000000001.json          # commit v1 (newline-delimited actions)
    00000000000000000002.json
    ...
    000000000000000099.json
    00000000000000000100.checkpoint.parquet
    _last_checkpoint                   # JSON pointer {version, size, parts}
  part-00000-uuid.c000.snappy.parquet  # data files (paths in add.path)
  _deletion_vector_xxx.bin             # optional DV sidecars
```

**Version = numeric suffix of log file.** Checkpoint at multiples of N (typically 100).

### 3.3 Commit protocol (optimistic concurrency)

```text
1. snapshot = readHead()                    # version v, file set F_v
2. plan = executeWrite(snapshot)            # produce new files N, removed files R
3. actions = [
     add(N*),
     remove(R*),
     metaData? protocol? txn?
   ]
4. attempt atomic create:
     path = _delta_log/{v+1:020d}.json
     LogStore.write(path, actions, overwrite=false)
5. if success → commit v+1 published
   if conflict (file exists) → goto 1 with exponential backoff
```

**Invariants:**

- No in-place mutation of data files referenced by any retained version.
- A commit file appears **atomically** from readers’ perspective (single PUT or multipart complete).
- Remove without add is valid (delete-only commit).

### 3.4 Options: locking vs pure OCC

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Pure OCC (put-if-absent) | Simple; no lock service | Retry under contention | Hot single partition many writers |
| B. Catalog lease lock | Fewer conflicts | External dependency; fence stale owners | Lock SPOF without HA |
| C. Partition-level locks | Finer granularity | Complex | Table has no partition columns |
| D. Single writer queue | Zero conflict | Throughput ceiling | Many concurrent ETL jobs |

**Chosen path:**

- **MVP:** Pure OCC + partition overlap conflict detection + bounded retry.  
- **100×+:** Optional catalog lock for `OPTIMIZE`/vacuum; partition append mode for ingest; DV for updates.

### 3.5 Conflict detection granularity

```text
Writer W1 read v10, writer W2 read v10:

Conflict if W1's touched partitions ∩ W2's touched partitions ≠ ∅
  AND (W1 removes files OR W2 removes files OR both add with overwrite semantics)

Append-only INSERT into partition P:
  Conflict only with other commits that REMOVE files in P or REPLACE P

Blind append (streaming):
  May skip overlap check IF protocol allows — trades correctness risk for throughput
  Strong answer: use txn + deterministic dedup keys in data for idempotent retries
```

**Iceberg contrast:** Iceberg uses atomic **`metadata.json` swap** with known-base snapshot ID; conflicts detected at catalog/commit service via CAS on root pointer—similar OCC at snapshot level, not file level.

### 3.6 Snapshot read path

```text
function loadSnapshot(version = LATEST):
  if version == LATEST:
    start = readLastCheckpointPointer()
    replay from start.version + 1 tail JSON to head
  else:
    load checkpoint ≤ version, replay JSON (version+1 .. target)

  apply actions in order:
    add    → insert into fileIndex[path]
    remove → mark deleted (tombstone in memory)
    metaData → replace schema/config
    protocol → update requirements

  yield TableSnapshot(version, activeFiles, schema, stats)
```

**Reader pin:** Spark/DataFrame `read.format("delta").option("versionAsOf", 42)` fixes snapshot for query duration.

**Never LIST `data/`** for membership—only log actions define membership.

### 3.7 Checkpoints

Purpose: collapse prefix of log into one (or partitioned) Parquet files.

```text
CheckpointWriter (async job):
  every N commits OR log JSON count > threshold:
    read snapshot at v
    emit checkpoint Parquet with columns mirroring actions (add/remove rows)
    write _last_checkpoint { version: v, size, numParts }
    optional: delete JSON files < v - retention (only if log cleanup enabled AND safe)
```

**Multi-part checkpoint:** for 10M files, partition checkpoint by `(partition.col)` hash to keep part < 128 MB.

**Recovery:** if `_last_checkpoint` corrupt, scan backward for highest `{v}.checkpoint.parquet` or replay JSON from 0.

### 3.8 Time travel

```text
AS OF VERSION 42     → loadSnapshot(42)
AS OF TIMESTAMP t    → binary search commit timestamps in log ≤ t → version v
```

Retention: all versions ≥ (now - retentionHours) must remain readable; vacuum must not delete files still referenced by those versions.

### 3.9 Deletion vectors vs copy-on-write

| Approach | Write amp | Read amp | Vacuum | MVP |
|----------|-----------|----------|--------|-----|
| Copy-on-write | High on UPDATE | Low | Standard | Yes |
| Deletion vectors (DV) | Low | Medium (merge DV) | DV + base lifecycle | Phase 2 |

```text
remove action with dataChange=false + DV path:
  base Parquet unchanged
  DV bitmap marks deleted row offsets
Reader: read base + apply DV filter → logical row set
OPTIMIZE: rewrite file without DV (bin-packing)
```

### 3.10 Compaction (two meanings — disambiguate in interview)

**Log compaction:** checkpoint absorbs old JSON; optional delete obsolete JSON after checkpoint verified.

**Data compaction (OPTIMIZE):**

```text
Read small files in partition P at v
Write consolidated files N
Commit: add(N), remove(old small files)
Z-order / liquid clustering: sort layout in N — layout optimization, not correctness
```

### 3.11 Vacuum

```text
referenced = ⋃ files in add \ remove for versions with version ≥ v_min_retained
candidates = LIST(data/) - referenced - paths in retained DV
DELETE candidates older than retentionHours since unreferenced

Safety:
  v_min_retained = headVersion - versionsWithin(retentionHours)
  dryRun list first
  never run vacuum with retentionHours=0 in prod
```

**Footgun:** vacuum permanently destroys ability to time-travel before retention window for deleted files.

### 3.12 Streaming idempotent sink

```text
Structured Streaming foreachBatch:
  txnId = (appId = streamingQueryId, batchId = epoch)

On commit, include action:
  { "txn": { "appId": "...", "batchId": 7, "version": 101, "lastUpdated": ts } }

Before writing batch 7 again:
  if txn(appId, batchId) exists in log with version committed → skip data write OR no-op commit
  else write files + commit with txn action
```

This gives **effectively-once** semantics assuming batch processing is deterministic.

### 3.13 Schema & protocol evolution

```text
metaData action: schemaString, partitionColumns, configuration
protocol action: minReaderVersion, minWriterVersion, readerFeatures, writerFeatures

Writer upgrades:
  bump minWriterVersion when using DV, column mapping, generated columns
Reader fails fast if protocol too new — safer than silent corruption
```

### 3.14 Compare Apache Iceberg (interview table)

| Dimension | Delta-like log | Apache Iceberg |
|-----------|----------------|----------------|
| Metadata tree | Linear `_delta_log/` JSON + checkpoint | Snapshot → manifest list → manifests → files (hierarchical) |
| Atomic commit | Create next `{v}.json` if absent | CAS replace `metadata.json` pointer |
| Conflict detection | OCC on version + optional partition overlap | CAS on base snapshot ID |
| Checkpoint | Parquet replay of actions | Manifests ARE incremental checkpoints |
| Partition evolution | Limited / protocol-dependent | Hidden partition spec evolution (v2) |
| Row-level delete | DV + COW remove | Position delete files + equality deletes |
| Streaming | `txn` action | `snapshot-id` + checkpoint via offset |
| Engine support | Databricks-native | Broad neutral standard |
| Metadata at 1M files | Heavy checkpoint; linear tail | Manifest pruning; partition stats |

**When Delta-like wins:** tight Spark/Databricks integration, uniform checkpoint replay, simpler mental model for interview whiteboard.

**When Iceberg wins:** open multi-engine neutrality, manifest pruning at extreme file counts, mature partition spec evolution.

**UniForm:** write Iceberg metadata alongside Delta — operational cost 2× metadata commits; mention as bridge not MVP.

### 3.15 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Truth source | Transaction log | ACID | LIST data directory |
| Concurrency | OCC + retry | Object store friendly | Distributed 2PC |
| Update wide rows | DV at scale | Write amp | Always full file rewrite |
| Metadata | Checkpoint every N | Bound cold start | Never checkpoint |
| Orphans | Async vacuum | Don't block commits | Sync LIST every commit |
| Streaming | txn idempotency | Crash recovery | Rely only on exactly-once sink |
| Hot partition | Partition locks / single writer | Conflict rate | Unlimited blind MERGE |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                    +-------------------+
  SQL/Spark ------->| Query Engine      |
  Streaming ------> | (SnapshotProvider)|
                    +---------+---------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
     +----------------+              +------------------+
     | LogStore       |              | Object Storage   |
     | (atomic put)   |              | S3 / ADLS / GCS  |
     +--------+-------+              +--------+---------+
              |                                |
              |         +----------------------+
              |         |
              v         v
     +-----------------------------+
     | table/_delta_log/           |
     |   NN.json  checkpoint.parquet|
     | table/*.parquet  DV files   |
     +-----------------------------+

     +------------------+     +------------------+
     | Checkpoint Job   |     | Vacuum / OPTIMIZE|
     | (scheduled)      |     | (maintenance)    |
     +------------------+     +------------------+
              |                         |
              v                         v
         LogStore                   LIST + DELETE
```

### 4.2 Sequence: successful OCC commit

```text
Writer                Object Storage              Reader (parallel)
  |--GET head v10----->|                            |
  |<-snapshot----------|                            |
  |--write data files->|                            |
  |--PUT log 11.json-->| (create-if-absent)         |
  |<-201 Created-------|                            |
  |                     |<--GET tail-----------------|
  |                     |---v11 actions------------->|
  |                     |                            | snapshot v11
```

### 4.3 Sequence: commit conflict + retry

```text
Writer W1                         Writer W2
  |--read v10--|                     |--read v10--|
  |--write files                    |--write files
  |--PUT v11 OK                     |--PUT v11 CONFLICT (exists)
  |                                  |--read v11 (W1's commit)
  |                                  |--replan merge
  |                                  |--PUT v12 OK
```

### 4.4 Sequence: snapshot read with checkpoint

```text
Reader                         LogStore
  |--read _last_checkpoint---->|
  |<-{version:100}-------------|
  |--GET 100.checkpoint.parquet|
  |<-Parquet actions-----------|
  |--GET 101.json..105.json----|  (tail)
  |<-replay--------------------|
  | build fileIndex            |
  |--scan data parquet-------->| (only active files)
```

### 4.5 Sequence: streaming idempotent batch

```text
Streaming Worker                     Log
  |--process batchId=7--------------|
  |--check txn(app,7) in log------->|
  |<-not found---------------------|
  |--write data + commit v+1 + txn->|
  | (crash, retry)                  |
  |--check txn(app,7)-------------->|
  |<-found version=55--------------|
  |--skip (already committed)-------|
```

### 4.6 Vacuum safety flow

```text
Vacuum Job
  |--load snapshot head v200
  |--compute v_min = 200 - retentionWindowVersions
  |--referenced = union files versions >= v_min
  |--LIST data/ prefix
  |--candidates = LIST - referenced
  |--dry-run report
  |--DELETE candidates (batched)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Atomic version publish:** version v exists fully or not at all.  
2. **Snapshot isolation:** reader at version v sees exactly the file set defined by replay through v.  
3. **No log–storage mismatch for reads:** reads trust log; orphan data inert until vacuum.  
4. **Monotonic versions:** version numbers strictly increase by 1 per successful commit (gaps OK if reserved commits abandoned—avoid gaps in MVP).  
5. **Vacuum safety:** ∀ file f deleted by vacuum, ∀ retained version u, f ∉ snapshot(u).  
6. **Txn idempotency:** `(appId, batchId)` commits at most once with same effect.  
7. **Checkpoint correctness:** replay(checkpoint@v) + tail == replay(JSON@0..v).

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Crash before data write complete | No commit; partial data orphaned |
| Crash after data write, before log | Orphan files; vacuum reclaims |
| Crash after log PUT | Commit visible; readers pick up |
| Duplicate log PUT retry | Create-if-absent fails → writer retries read head |
| Checkpoint write partial | Readers ignore incomplete; writer uses prior checkpoint |
| Two-phase multipart commit incomplete | Use single PUT for small commits; multipart completion barrier |
| Reader uses cached stale tail | Poll `_last_checkpoint` or tail listing with ETag |
| Vacuum too aggressive | Enforce retentionHours; integration tests |
| DV lost but base remains | Protocol marks dependency; read fails safe if DV missing |
| Schema corruption in metaData | Validate on read; reject commit |

**Commit uncertainty protocol (must say):**

```text
if log PUT result unknown:
  do NOT assume failure and rewrite new version blindly
  HEAD/GET the target log path
  if exists with same content hash → success
  if exists with different content → fatal / human intervention (should never happen with CAS)
  if absent → safe to retry PUT
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | JSON log + checkpoint/100; COW updates; single-region S3 |
| 10× | Tail cache in executor; partition-scoped conflicts; async checkpoint |
| 100× | Deletion vectors; partitioned checkpoints; incremental vacuum; stats cache |
| 1,000× | Manifest-like side index; hot-table dedicated coordinator; cell isolation; log object cache CDN |

**Hot table tactics:**

```text
Partition append mode for ingest (only add, no remove) → fewer conflicts
Coalesce micro-streams → fewer commits/min
OPTIMIZE off-peak → separate maintenance window
Raise checkpoint frequency on hot tables (every 50 vs 100)
```

**Admission control:** if commit retry count > 5, backoff and shed low-priority writers.

### 5.3 Maintainability

- **Protocol versioning** with feature flags in `protocol` action.  
- Golden tests: replay random action sequences → snapshot hash.  
- Fuzz OCC: N writers random MERGE → serializable outcome equivalent to sequential.  
- Metrics: commit latency, conflict rate, log tail length, checkpoint lag, vacuum bytes reclaimed.  
- Runbook: “metadata read slow” → check checkpoint health; “conflict storm” → partition skew.  
- Chaos: kill writer mid-commit, corrupt checkpoint part, duplicate streaming batch.

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Writer:
  read JSON tail from 0 or last checkpoint (small table)
  write Parquet
  atomic PUT next version JSON
Reader:
  replay log → file list → scan
Maintenance:
  manual VACUUM with 168h retention
Streaming:
  txn action in commit
```

**10×**

- Scheduled checkpoint job; `_last_checkpoint` always current within 5 min.  
- Driver caches tail ETag; invalidate on write.  
- Conflict checker enforces partition predicates from Spark query plan.

**100×**

- Deletion vectors for UPDATE-heavy workloads.  
- Partitioned checkpoint files (4 parts).  
- Incremental vacuum: only LIST prefixes touched recently.  
- Sidecar **file index** service (optional) serving file lists gRPC — log remains SoT.

**1,000×**

- Table sharded by **cell** (separate log per cell, union view) — advanced.  
- Embedded log tail in catalog (Postgres) as cache not SoT.  
- Cross-engine UniForm for Iceberg readers without replaying full Delta log.  
- Automatic OPTIMIZE + Z-order as managed policy.

### 5.5 Read path optimizations

```text
Stats pruning:
  add.minValues/maxValues/nullCount per column → skip files

Data skipping index (Delta):
  optional persisted sketch per file — extra metadata action

Column mapping (name/id):
  schema evolution without rewrite — protocol feature

Caching:
  snapshot object in executor memory (table size bounded)
  cloud log tail cached in coordinator with version watch
```

### 5.6 MERGE / UPDATE commit anatomy

```text
MERGE INTO t USING s ON ...
  read snapshot v
  identify affected files F_affected via file stats + join key ranges
  write new files N
  commit v+1:
    add(N)
    remove(F_affected)   # COW
    cdc (optional)       # row change events
    txn (if streaming)

Conflict: another writer removed overlapping file → retry full MERGE from new head
```

With **DV:**

```text
  add(DV files only) + remove(none) + metaData(dataSkippingNumIndexedFiles...)
  logical delete without rewriting base immediately
```

### 5.7 Multi-engine and catalog integration

```text
Hive Metastore / Unity Catalog:
  stores table location + provider=delta
  optional: synced snapshot version pointer for fast planning

Unity Catalog:
  managed table ACLs; log still on object storage
  coordinator may enforce serial commits for managed tables (product detail)
```

### 5.8 Security & governance

- IAM: writers need `PutObject` on `_delta_log/` with condition `x-amz-meta-*`; readers `GetObject`.  
- Prevent arbitrary DELETE on bucket — vacuum uses role with delete permission scoped to table prefix.  
- Audit: log every commit with user/principal in `domainMetadata` or external audit pipeline.  
- Encryption: SSE-KMS on bucket; per-table keys optional.

### 5.9 Observability

```text
delta.commit.latency_ms
delta.commit.conflicts_total
delta.log.tail.length
delta.checkpoint.lag_versions
delta.snapshot.load_ms
delta.vacuum.files_deleted
delta.streaming.txn.duplicates_avoided
```

---

## 6. Wrap-Up

**Design summary**

- **Transaction log** on object storage is the source of truth; data files are immutable blobs referenced by `add`/`remove` actions.  
- **OCC commit:** read version v, write data, atomically create log v+1; loser retries.  
- **Checkpoints** bound metadata read; tail replay stays O(checkpoint interval).  
- **Snapshot reads** pin a version; never mix files across versions.  
- **Deletion vectors** reduce write amplification; **OPTIMIZE** rewrites for read performance.  
- **Vacuum** reclaims orphans with strict retention — irreversible, time-travel sensitive.  
- **Streaming `txn` actions** enable idempotent micro-batch commits.  
- vs **Iceberg:** linear log + checkpoint vs hierarchical manifests; both CAS-style atomic metadata; Iceberg stronger at multi-engine neutrality and manifest pruning at 10M files.

**MVP vs later**

| MVP | Later |
|-----|-------|
| JSON log + Parquet checkpoint | Partitioned checkpoint, log cleanup |
| Copy-on-write MERGE | Deletion vectors + lazy optimize |
| Pure OCC | Catalog partition locks for hot keys |
| Manual vacuum | Policy-driven auto-vacuum |
| Delta-only | UniForm Iceberg metadata |

**Top risks**

1. Unbounded log without checkpoint → query planning timeout  
2. Vacuum with wrong retention → unrecoverable time travel / data loss  
3. OCC retry storm on single hot partition  
4. Blind append misuse → duplicate rows  
5. Treating LIST(data/) as membership → torn / inconsistent reads  

**What I'd measure first in production**

- Log tail length, checkpoint lag, snapshot load p99, commit conflict rate, orphan file ratio, vacuum bytes vs retention violations.

---

## 7. Deeper / Related Interview Questions

1. How is put-if-absent implemented on S3 vs ADLS vs GCS?  
2. What happens with S3 strong consistency vs legacy eventual LIST?  
3. Conflict detection: file-level vs partition-level vs snapshot-level?  
4. When is blind append safe?  
5. Walk through checkpoint + tail replay correctness proof sketch.  
6. Deletion vectors: read path cost model?  
7. How does `txn` differ from Iceberg's commit UUID / snapshot property?  
8. Vacuum vs `DELETE` remove action — what remains on storage?  
9. Can two checkpoints exist at same version? How to pick?  
10. Schema evolution: overwrite vs merge schema?  
11. Change Data Feed vs reading `add`/`remove` diff?  
12. Liquid clustering vs Z-order vs partition — layout only?  
13. How to support column-level lineage from log actions?  
14. Multi-table transaction — what would you add to protocol?  
15. Compare to Hudi timeline + base files + log files model.  

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "LIST the data folder to find files" | Log is SoT; LIST only for vacuum orphans |
| "Delete old JSON logs anytime" | Only after checkpoint verified + retention policy |
| "vacuum(retention=0) to save cost" | Destroys time travel; legal/compliance risk |
| "2PC across writers" | OCC + retry; optional external lock |
| "Reader sees partial commit" | Version appears atomically; pin snapshot |
| "Iceberg is always better" | Tradeoffs: engine ecosystem, manifest pruning, ops complexity |
| "Exactly-once without txn action" | At-least-once writes + idempotent commit gate |

---

## 8. Appendices

### A. Pseudocode — OCC commit

```text
function commit(tableRoot, produceActions):
  backoff = 100ms
  for attempt in 1..MAX_RETRIES:
    head = DeltaLog.readHead(tableRoot)       # version v, snapshot S_v
    actions = produceActions(S_v)             # deterministic from S_v
    if actions.empty: return head.version

    nextPath = tableRoot/_delta_log/{v+1:020d}.json
    payload = serializeNDJSON(actions)

    result = LogStore.atomicCreate(nextPath, payload)
    if result == CREATED:
      invalidateTailCache(tableRoot)
      return v + 1
    if result == ALREADY_EXISTS:
      if LogStore.get(nextPath).hash == hash(payload):
        return v + 1   # won but ack lost
      else:
        raise INVARIANT_VIOLATION
    sleep(backoff); backoff *= 2
    continue
  raise CONFLICT_EXHAUSTED
```

### B. Pseudocode — load snapshot at version

```text
function loadSnapshot(tableRoot, targetVersion):
  cp = findLatestCheckpoint(tableRoot, targetVersion)
  state = empty FileIndex
  if cp:
    applyCheckpointParquet(state, cp)
    start = cp.version + 1
  else:
    start = 0

  for v in start..targetVersion:
    for action in readJSON(tableRoot, v):
      match action:
        case Add(path, stats, ...): state.add(path, stats)
        case Remove(path, ...):     state.remove(path)
        case MetaData(m):            state.schema = m
        case Protocol(p):            state.protocol = p
        case Txn(t):                 state.txns.add(t)
  return Snapshot(targetVersion, state.activeFiles(), state.schema)
```

### C. Pseudocode — streaming idempotent foreachBatch

```text
function foreachBatch(df, batchId):
  appId = streamingQuery.id
  if deltaTxnCommitted(table, appId, batchId):
    return  # already done

  files = writeParquet(df)
  commit(table, actions = [
    Add(files*),
    Txn(appId, batchId, version=nextVer)
  ])
```

### D. Pseudocode — safe vacuum

```text
function vacuum(tableRoot, retentionHours):
  head = loadSnapshot(LATEST)
  cutoffTs = now - retentionHours
  minVersion = maxVersionWithTimestampLE(head, cutoffTs)

  referenced = set()
  for v in minVersion..head.version:
    for a in readCommit(v):
      if a is Add: referenced.add(a.path)
      if a is Remove: referenced.remove(a.path)

  orphans = listStorage(tableRoot/data/) - referenced - legalDVTemp
  logDryRun(orphans)
  for path in orphans:
    if fileAge(path) >= retentionHours:
      storage.delete(path)
```

### E. Action JSON examples (sketch)

```text
{"add":{"path":"part-001.parquet","size":1048576,"partitionValues":{"dt":"2026-08-01"},
  "modificationTime":1754467200000,"dataChange":true,
  "stats":"{\"numRecords\":1000,\"minValues\":{\"id\":\"1\"},\"maxValues\":{\"id\":\"999\"}}"}}
{"remove":{"path":"part-old.parquet","deletionTimestamp":1754467201000,"dataChange":true}}
{"metaData":{"id":"uuid","format":{"provider":"parquet"},"schemaString":"..."}}
{"protocol":{"minReaderVersion":1,"minWriterVersion":4}}
{"txn":{"appId":"stream-1","batchId":7,"version":55,"lastUpdated":1754467202000}}
```

### F. Delta vs Iceberg commit flow (one-liner diagram)

```text
Delta:   ... → v.json → (v+1).json → checkpoint@100
Iceberg: metadata.json → snapshot S_n → manifest list → manifests → files
Both:    atomic publish new metadata pointer; readers never see hybrid snapshot
```

### G. Metrics checklist

```text
delta_commit_latency_ms{quantile}
delta_commit_conflicts_total
delta_log_tail_json_count
delta_checkpoint_lag_versions
delta_snapshot_load_ms{quantile}
delta_active_files_count
delta_orphan_bytes_estimated
delta_vacuum_deleted_bytes
delta_streaming_txn_skipped_total
delta_optimize_files_rewritten
```

### H. Capacity cheat sheet

```text
metadata_read_bytes ≈ tail_json_count × avg_json_size + checkpoint_size
tail_json_count ≈ commits_since_last_checkpoint
checkpoint_frequency ↑ → lower tail, higher checkpoint write cost

orphan_storage ≈ failed_commits × avg_commit_data_bytes × (1 - vacuum_frequency)

reader_metadata_qps × metadata_read_bytes = coordinator egress bottleneck
```

### I. Clarifying questions cheat sheet (30 seconds)

1. Concurrent writers or single ETL?  
2. Read-heavy vs UPDATE/MERGE heavy?  
3. Time travel retention / compliance?  
4. Streaming idempotency required?  
5. Expected files/table and commits/day?  
6. Multi-engine (Iceberg interop) needed?

### J. Related Databricks follow-ups

- `lakehouse-object-storage-system-design.md` — storage layer below table format  
- `durable-embedded-kv-store-lld-system-design.md` — local WAL patterns for executor cache  
- UniForm dual-metadata operational cost  
- Unity Catalog managed table commit serialization  

---

*End of Delta-like transaction log / table format HLD prep.*
