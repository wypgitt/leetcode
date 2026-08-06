# System Design: Storage-versus-Compute Trade-offs (Lakehouse Architecture)

> **Focus areas:** Separation · Caching · Locality · Cost · Lakehouse vs HDFS+YARN · Object storage · Multi-engine  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit I/O budgets, honest cache semantics, clear source-of-truth boundaries  
> **Interview theme:** Databricks — data platform architecture; why lakehouse separates storage from compute and what you pay for it

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

Goal: design a **cloud-native analytics platform** where durable data lives in object storage, compute scales independently, and multiple engines (Spark, SQL, ML) share the same tables—while being honest about latency, cost, and consistency trade-offs vs coupled HDFS+YARN clusters.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What workloads? | Batch ETL, interactive BI, ad-hoc SQL, ML feature generation | Mixed read patterns; shuffle-heavy vs scan-heavy |
| F2 | Who owns storage? | Central platform team; data in S3/ADLS/GCS | Object storage is source of truth for files |
| F3 | Who owns compute? | Ephemeral clusters / serverless warehouses per team | Scale-to-zero; no sticky data on nodes |
| F4 | Table format? | Open lakehouse (Delta/Iceberg/Hudi) on Parquet | ACID via transaction log; multi-engine via spec |
| F5 | Multi-engine? | Spark for ETL, Trino/Photon for BI, Python for ML | Shared metastore + open table format mandatory |
| F6 | Write semantics? | Append/merge/upsert; not full OLTP | Optimistic concurrency on table version |
| F7 | Read semantics? | Snapshot isolation; time travel optional | Readers pin snapshot; writers commit new version |
| F8 | Caching? | Optional SSD/NVMe tier to hide object storage latency | Cache is **derived**, never authoritative |
| F9 | Locality? | "Good enough" via cache + prefetch; not rack-aware HDFS | Design for remote I/O; optimize with software |
| F10 | Cost model? | Pay for storage always; pay for compute when running | Idle coupled clusters waste money |
| F11 | Migration? | Lift from on-prem HDFS+YARN or EMR | Dual-read period; metadata migration path |
| F12 | Governance? | Same tables visible to all engines with RBAC | Metastore + IAM on storage prefix |

**MVP functional scope (lock with interviewer):**

1. Durable data in **object storage** with open table format (Delta Lake as example).
2. **Ephemeral Spark/SQL clusters** attach to storage via cloud credentials; no local HDFS.
3. **Metastore** resolves table → snapshot → file list; engines read transaction log.
4. **Optional local SSD cache** on compute nodes (block or file granularity).
5. **Multi-engine read**: Spark + SQL engine share same table snapshots.
6. Write path: commit protocol updates log + data files atomically at table level.
7. Cost dashboard: storage GB-month, GET/LIST requests, egress, compute DBU/hour.

**Out of MVP (explicitly defer):**

- Zero-copy cross-region active-active writes to same table
- Sub-100ms interactive latency on cold multi-PB scans
- Automatic perfect cache coherence across all engines globally
- Replacing object storage with proprietary disaggregated block store
- Full OLTP row-level locking across engines

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Scan throughput (warm)? | Competitive with local disk when cached | ≥ 1–2 GB/s per executor with NVMe cache |
| N2 | Scan throughput (cold)? | Bounded by object storage + network | 200–500 MB/s per executor typical |
| N3 | Interactive query p99? | BI dashboards | p99 < 5–15s for warm partitions; cold higher |
| N4 | ETL job SLA? | Nightly + hourly incremental | Finish within window; scale out executors |
| N5 | Durability? | 11 nines object storage | Never rely on executor disk for durability |
| N6 | Availability? | Clusters ephemeral; storage always on | Re-run failed job; storage survives region AZ loss (with replication) |
| N7 | Consistency? | Snapshot isolation per table version | No reading partial writes |
| N8 | Cost predictability? | Finance needs chargeback | Tag clusters; meter storage + requests |
| N9 | Elasticity? | 10× burst for month-end | Spin 100 executors in minutes; tear down after |
| N10 | Multi-tenancy? | Noisy neighbor isolation | Quotas on concurrent scans / cache |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. BI user runs `SELECT` on partitioned fact table → planner reads metastore snapshot → executors fetch Parquet via cache miss → aggregate → result in 3s (warm).
2. ETL job appends 500 GB daily partition → writes new files + commits Delta log → downstream SQL sees new version on next query.
3. ML notebook reads same table as ETL via Spark DataFrame → identical snapshot if pinned to same version.
4. Cluster terminated → no data loss; next cluster re-attaches to same storage prefix.
5. Cache hit on hot partition → 90% of bytes served from local NVMe → 5× faster scan.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Executor dies mid-scan | Task retried; no durable state lost on executor |
| Commit conflict (two writers) | Optimistic concurrency; loser retries or fails with clear error |
| Stale cache after write | Invalidate via table version bump; readers check version |
| LIST explosion (millions of small files) | Compaction job; partition pruning; metadata indexing |
| Cross-AZ egress | Prefer same-region compute; cache reduces repeated GETs |
| Throttled object storage | Backoff; reduce concurrency; prefetch tuning |
| Metastore unavailable | Reads may use cached snapshot; writes fail closed |
| Wrong IAM credentials | Fail at plan time; audit log |
| Time travel query | Read older snapshot; no impact on latest |
| Shuffle-heavy join | Spill to local SSD; optionally disaggregated shuffle service |
| Tiny file problem | Auto-compaction; target file size 128–256 MB |
| Engine version skew | Table format backward compatibility; feature flags |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Total stored data | 500 TB | 5 PB | 50 PB | 500 PB |
| Daily ingest | 5 TB | 50 TB | 500 TB | 2 PB |
| Concurrent clusters | 20 | 200 | 2K | 20K |
| Peak executors | 500 | 5K | 50K | 500K |
| Tables | 5K | 50K | 500K | 5M |
| Files under management | 50M | 500M | 5B | 50B |
| Metastore read QPS | 2K | 20K | 200K | 2M |
| Object GET rate (peak) | 200K/s | 2M/s | 20M/s | 100M/s (must cache) |
| Monthly storage cost | $10K | $100K | $1M | $10M |
| Monthly compute cost | $50K | $500K | $5M | $50M |

**What each jump forces:**

- **10×:** SSD cache layer mandatory; partition pruning; auto-compaction; connection pooling to object storage.
- **100×:** Disaggregated shuffle; regional cache clusters; metadata sidecar (Delta cache / data skipping indexes); request coalescing for GETs.
- **1,000×:** Tiered storage (hot SSD pool vs cold object); predictive cache warming; file index services; cell-based tenancy; limit LIST via hierarchical namespace or table indexes.

### 1.5 Etc. (Constraints & Assumptions)

- Object storage **latency** ~10–50 ms first byte vs ~0.1 ms local NVMe.
- Object storage **billing**: $/GB-month + per-request + egress—not just capacity.
- HDFS+YARN coupling meant **data locality** via rack awareness; cloud separation trades that for elasticity.
- Open table format provides **ACID** without a centralized database holding all bytes.
- Assume single cloud region MVP; multi-region for DR reads later.

**Scope statement:**

> Design a lakehouse platform with separated object storage and ephemeral compute, optional SSD caching, multi-engine access via open table formats, and explicit cost/latency trade-offs—evolving from ~500 TB / 500 executors through 10× / 100× / 1,000× by caching, compaction, and metadata discipline rather than recoupling storage to compute.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Storage cost (the always-on bill)

```text
Baseline: 500 TB in S3 Standard
Storage ≈ 500 × 1024 GB × $0.023/GB-month ≈ $11,776/month

At 100× (50 PB):
50,000 TB × $0.023 ≈ $1.18M/month storage alone
→ Tier lifecycle: 80% infrequent access @ lower $/GB
→ Effective ≈ $700K–900K/month with tiering
```

**Critical insight:** Separated storage means **you pay when idle**. Coupled HDFS clusters still spin disks 24/7 attached to underutilized YARN nodes.

### 2.2 Request cost (often underestimated)

```text
Baseline peak scan:
500 executors × 40 tasks each × 10 files/task = 200K files/read wave
If each file = 1 GET + 1 HEAD ≈ 400K requests
S3 GET ≈ $0.0004/1K → 400K GETs ≈ $0.16 per wave (cheap per wave)

But: 200 concurrent BI queries/hour × 400K = 80M GETs/hour
→ $32/hour → $23K/month if uncached

At 100× without cache: unsustainable → 90%+ cache hit or coalesced reads required
```

### 2.3 Egress cost

```text
Cross-AZ read within region: often $0.01/GB
Scan 10 TB/day cross-AZ → 10,000 GB × $0.01 × 30 ≈ $3,000/month

Cross-region replication for DR:
50 TB/month egress × $0.02/GB ≈ $1,000/month baseline
```

**Rule:** Colocate compute with storage bucket region/AZ when possible.

### 2.4 Compute cost vs coupled cluster waste

```text
Coupled 50-node HDFS+YARN cluster:
50 nodes × $2/hr × 730 hr/month ≈ $73K/month always on
Utilization 30% → effective $243K/month of useful compute capacity wasted

Separated: 500 executors × $0.10/DBU-hr × 4 hr/day avg ≈ $6K/month
Burst to 500 executors × 8 hr for month-end → incremental only

Elasticity savings: 5–10× for spiky workloads
```

### 2.5 Bandwidth & scan math

```text
Cold scan: 500 executors × 250 MB/s = 125 GB/s theoretical
Object storage per-prefix limits ~50–100 Gbps → need cache or staggered waves

Warm scan (NVMe cache hit 80%):
Effective remote = 125 × 0.20 = 25 GB/s → fits within S3 limits per prefix with sharding
```

### 2.6 Cache sizing

```text
Hot data fraction: 5% of 500 TB = 25 TB
Per executor cache: 25 TB / 500 executors = 50 GB NVMe → feasible

At 100×: centralized SSD cache service (e.g., 500 TB shared pool)
Hit ratio target 85%+ on recurring BI queries
```

### 2.7 Shuffle spill (locality still matters locally)

```text
10 TB shuffle join:
Spill to local NVMe @ 2 GB/s → ~5,000 s without remote shuffle service
Disaggregated shuffle (100×): write shuffle to object storage or dedicated service
Trade-off: remote shuffle adds latency but enables spot/preemptible executors
```

### 2.8 Bottlenecks (ranked)

1. Uncached object storage GET rate and latency  
2. Small-file LIST/metadata amplification  
3. Cross-AZ egress on repeated scans  
4. Metastore read QPS at planning time  
5. Commit conflicts on hot tables  
6. Cache staleness causing wrong results (correctness, not throughput)  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
StorageAccount     → bucket/container, IAM policies, lifecycle rules
Table              → logical entity; maps to table format root path
Snapshot           → immutable version: schema + file list + stats
TransactionLog     → ordered commits (Delta _delta_log/, Iceberg metadata/)
ObjectStore        → durable files (Parquet, checkpoints)
ComputeCluster     → ephemeral executors with local SSD scratch + cache
CacheLayer         → block/file cache keyed by (path, offset, version)
Metastore          → table → current snapshot pointer; partition stats
Engine             → Spark, SQL, ML runtime; plans queries against snapshot
```

### 3.2 Architecture options: coupled vs separated

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. HDFS + YARN (coupled) | Strong locality; mature Hadoop stack | Cannot scale storage/compute independently; idle cost | Elastic burst workloads |
| B. Object storage only, no cache | Cheapest storage; infinite durability | Terrible scan latency at scale | Interactive BI |
| C. Lakehouse: object + table format + cache | Elastic compute; multi-engine; durable | Request billing; cache coherence complexity | Team refuses open format |
| D. Proprietary disaggregated SSD (Snowflake-style) | Great performance | Vendor lock-in; higher $/TB | Must stay open/multi-cloud |
| E. HDFS on local NVMe per cluster | Fast local reads | Data trapped on cluster; re-copy for sharing | Multi-team data mesh |

**Chosen path:**

- **MVP:** Object storage + Delta/Iceberg + ephemeral Spark/SQL clusters + executor-local SSD cache.  
- **100×+:** Shared regional cache service, disaggregated shuffle, compaction as a service, data skipping indexes (Z-order, stats).

### 3.3 Lakehouse vs HDFS+YARN (say aloud)

| Dimension | HDFS + YARN | Lakehouse (object + format) |
|-----------|-------------|----------------------------|
| Durability | 3× replication on cluster disks | 11 nines object storage + optional cross-region |
| Locality | Rack-aware block placement | Software cache + prefetch; no rack guarantee |
| Elasticity | Scale nodes = scale both | Scale executors independently of data size |
| Multi-engine | Hard (HDFS client per engine) | Natural via open table format + metastore |
| Cost when idle | Cluster + disks run 24/7 | Storage only; compute off |
| Small files | NameNode pressure | LIST + log overhead → compaction critical |
| Consistency | HDFS close() semantics | Table-format commit protocol |
| Ops burden | Cluster babysitting, rebalance | Object storage managed; tune cache/compaction |

**When HDFS still wins:** Ultra-tight latency loop on same rack (iterative algo on fixed dataset), legacy Hadoop-only tooling, air-gapped on-prem without object storage.

### 3.4 Read path latency budget (interactive SQL)

```text
Total p99 target: 8s (warm BI query, 50 GB scanned)

Parse + auth:           100ms
Metastore resolve:      200ms  (snapshot + partition pruning)
Planning:               500ms
Task launch:            1s
Data read (80% cache):  4s     (50 GB × 0.2 remote @ 250 MB/s + cache hits)
Shuffle/aggregate:      1.5s
Result return:          700ms
```

Cold path (0% cache): data read dominates → 50 GB @ 125 MB/s aggregate ≈ 400s → need partition pruning to ≤ 5 GB or pre-warm cache.

### 3.5 Write path commit protocol (Delta-style sketch)

```text
1. Stage new data files to temp prefix (Parquet)
2. Write commit entry to _delta_log/ (atomic put-if-absent on object store)
3. On success: new snapshot version N+1 visible
4. On conflict: abort; optional retry with exponential backoff
5. Async: register partition stats in metastore; invalidate caches for version N+1
```

**Invariant:** Readers never see uncommitted files; they read snapshot at version ≤ latest committed.

### 3.6 Caching strategy

| Cache type | Granularity | Invalidation | Use case |
|------------|-------------|--------------|----------|
| Executor block cache | 1–4 MB blocks | Table version bump | Repeated scans same cluster |
| OS page cache | File pages | Process restart | Short-lived |
| Regional shared cache | Block/hash of file | Version + TTL | Cross-cluster BI |
| Metastore snapshot cache | Whole file list | New commit | Planning |
| Result cache | Query hash → result | TTL + table version deps | Identical dashboard queries |

**Deal-breaker:** Treat cache as source of truth without version checks.

```text
Cache key: (bucket, path, file_version_or_etag, byte_range)
Lookup:
  if cached.version >= required_snapshot_file_version:
    serve from cache
  else:
    fetch from object storage; populate cache
```

### 3.7 Multi-engine access

```text
Spark ETL:
  writes via DataFrame → Delta commit
SQL warehouse:
  reads latest snapshot; vectorized Parquet reader
Trino (optional):
  Iceberg/Delta connector; same metastore catalog
ML Python:
  reads via Spark or direct Parquet with pinned snapshot

Shared requirements:
  - Unity Catalog / Hive metastore for name resolution
  - Table format spec for snapshot isolation
  - IAM: all engines assume role with prefix-scoped access
```

**Conflict rule:** One write engine per table for MVP, or optimistic concurrency with retry; avoid concurrent incompatible DDL.

### 3.8 Cost optimization levers

| Lever | Savings | Trade-off |
|-------|---------|-----------|
| Scale-to-zero compute | 50–80% compute $ | Cold start latency |
| Lifecycle to IA/Glacier | 40–60% storage $ on cold | Retrieval latency |
| Compaction | Fewer GETs/LISTs | Compaction compute cost |
| Partition pruning | Less data scanned | Requires thoughtful schema |
| Z-order / data skipping | Skip files | Index maintenance |
| Spot/preemptible executors | 60–70% compute $ | Needs fault-tolerant tasks + disaggregated shuffle |
| Same-AZ compute | Egress $ | Less AZ fault isolation for compute |

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Source of truth | Object storage + txn log | Durability, sharing | Executor local disk |
| Locality | Software cache | Elasticity | Assuming rack-local HDFS |
| Consistency | Snapshot isolation | Multi-engine reads | Reading in-flight writes |
| Cost | Pay-per-request awareness | Real cloud bills | Ignoring GET/LIST at 100× |
| Performance | NVMe cache + compaction | Hide remote latency | Millions of tiny files |
| Coupling | Separated | Independent scale | Forcing data copy per cluster |

---

## 4. Architecture Diagram

### 4.1 End-to-end lakehouse

```text
                    +-------------------+
  Analysts/ETL ---->| Control Plane     |
                    | (clusters, IAM)   |
                    +---------+---------+
                              |
         +--------------------+--------------------+
         |                    |                    |
         v                    v                    v
 +---------------+    +---------------+    +---------------+
 | Spark Cluster |    | SQL Warehouse |    | ML Runtime    |
 | (ephemeral)   |    | (ephemeral)   |    | (ephemeral)   |
 +-------+-------+    +-------+-------+    +-------+-------+
         |                    |                    |
         +--------------------+--------------------+
                              |
                    +---------v---------+
                    | Metastore/Catalog |
                    | (snapshots, ACL)  |
                    +---------+---------+
                              |
         +--------------------+--------------------+
         |                    |                    |
         v                    v                    v
 +---------------+    +---------------+    +---------------+
 | Local NVMe    |    | Regional SSD  |    | Object Store  |
 | Block Cache   |    | Cache (100×)  |    | S3/ADLS/GCS   |
 | (per executor)|    |               |    | (source of    |
 +-------+-------+    +-------+-------+    |  truth bytes) |
         |                    |            +-------+-------+
         +--------------------+                    |
                    |                              |
                    +---------- read/write --------+
                              |
                    +---------v---------+
                    | Table Format      |
                    | (_delta_log/ etc) |
                    +-------------------+

Compaction / OPTIMIZE jobs -----> rewrite small files
Auto maintenance ----------------> expire snapshots, vacuum
```

### 4.2 Sequence: read with cache

```text
SQL Engine       Metastore       Cache           Object Storage
    |--resolve table->snapshot-->|               |               |
    |<-file list + stats---------|               |               |
    |--plan partition prune------|               |               |
    |--read block(path, off)--------------------->|               |
    |<-HIT (version ok)----------|               |               |
    |--read block(miss)-------------------------->|--GET-------->|
    |<-data--------------------------------------|<--Parquet-----|
    |--populate cache------------>|               |               |
    |<-aggregate result-----------|               |               |
```

### 4.3 Sequence: write commit

```text
Spark Driver     Executors        Object Storage       Metastore
    |--write Parquet files------->|                    |              |
    |                              |--PUT data-------->|              |
    |<-paths-----------------------|                    |              |
    |--commit log entry-------------------------------->| (atomic)     |
    |<-success-----------------------------------------|              |
    |--update stats----------------------------------->|              |
    |--cache invalidate broadcast-->|                 |              |
```

### 4.4 HDFS+YARN vs lakehouse (conceptual)

```text
HDFS+YARN (coupled):
  [Node1: DN+NM] [Node2: DN+NM] [Node3: DN+NM]
  Task scheduled where block lives → locality

Lakehouse (separated):
  [Executor A] [Executor B] ...  ----remote read--->  [S3 bucket]
  Locality recreated via cache on repeat access
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Durability:** committed data survives executor/cluster termination.  
2. **Snapshot isolation:** readers see consistent snapshot; no torn writes.  
3. **Cache correctness:** never serve cached block whose version < required snapshot.  
4. **Auth:** every read/write path validates IAM + catalog ACL.  
5. **Idempotent tasks:** Spark task retry safe; writers use deterministic file names in staging.  
6. **Metastore HA:** planning survives single node loss.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Executor loss | Retry task; no commit from failed task |
| Driver loss mid-write | Uncommitted staging files; vacuum orphan |
| Commit conflict | Retry job; serialize writers on hot table |
| Object storage throttle | Exponential backoff; reduce parallelism |
| Cache poison (corrupt block) | Checksum on read; evict; refetch |
| Metastore outage | Read-only from cached snapshots (short TTL); block DDL |
| AZ outage | Multi-AZ object storage; re-schedule compute other AZ |
| Partial network partition | Commit protocol fails closed; readers stay on old version |

**Recovery narrative (say aloud):**

```text
ETL driver dies after writing files but before commit:
  → New driver run lists staging prefix
  → Either complete commit if files complete, or garbage-collect orphans
  → Readers never saw partial commit

Executor serves stale cache after concurrent writer commits v+1:
  → Reader pinned to v; cache keyed with version; OK
  → Reader wants latest; cache miss on version → fetch new files
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Single-region S3 + Delta + Spark/SQL + local NVMe cache |
| 10× | Auto-compaction; partition stats; connection pool tuning; cache quotas |
| 100× | Regional cache cluster; disaggregated shuffle; Z-order; file index service |
| 1000× | Storage tiering; cell per tenant; predictive cache warm; metadata sharding |

**Small-file control:**

```text
Target file size: 128–256 MB
Compaction trigger: if avg_file_size < 32 MB OR files/partition > 10K
OPTIMIZE ZORDER BY (common_filter_cols) weekly for hot tables
```

**GET amplification reduction:**

```text
Before: 1M files scanned → 1M GETs
After compaction: 4K files → 4K GETs
After data skipping stats: 400 files read → 400 GETs
```

### 5.3 Maintainability

- **Table format upgrades:** backward-compatible reader versions; staged rollout.  
- **Observability:** bytes read local vs remote, GET rate, cache hit ratio, commit latency.  
- **Runbooks:** throttle storm, metastore failover, compaction backlog.  
- **Testing:** chaos kill executors mid-commit; verify no snapshot corruption.  
- **Migration tooling:** DistCp HDFS → S3; register tables in metastore; validate row counts.

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Storage: S3 bucket per env
Format: Delta Lake on Parquet
Compute: Spark on K8s/EMR/Databricks; SQL warehouse
Cache: executor NVMe, 50 GB/node
Ops: nightly compaction on top 20 tables
Governance: IAM prefix + catalog grants
```

**10×**

- Shared connection pool to S3 (HTTP/2 multiplexing).  
- Automatic OPTIMIZE on write for streaming tables.  
- Metastore read replicas + snapshot list caching.  
- Chargeback tags on clusters.

**100×**

- Disaggregated shuffle service (S3 or Redis-backed).  
- Regional SSD cache (shared across clusters).  
- File listing via Delta Checkpoint + manifest cache—not raw LIST.  
- Spot instances with checkpointing.

**1000×**

- Tenant cells: separate buckets + metastore shards.  
- Hot/cold tiering with automatic promotion on access patterns.  
- Global metadata search; federated queries across cells.  
- Dedicated I/O proxy layer coalescing GETs.

### 5.5 Locality deep dive

**Physical locality (HDFS):** scheduler places task on node holding block replica.  
**Logical locality (lakehouse):** cache makes **second** read local.

```text
First scan (cold): all remote → expensive
Repeated scan (warm): 80–95% cache hit → near-HDFS performance
Mitigation for first scan:
  - Prefetch next blocks based on query plan
  - Cache warming job after ETL completes
  - Co-locate ETL output partition with known consumer queries
```

**Shuffle locality:** always local disk or disaggregated service—never "shuffle to HDFS permanently."

### 5.6 Multi-engine consistency scenarios

| Scenario | Behavior |
|----------|----------|
| Spark writes v5; SQL reads latest | SQL sees v5 after commit completes |
| SQL time travel v3 | Reads v3 files even if v5 exists |
| Trino + Spark concurrent append | Table format serializes commits; one wins |
| Schema evolution add column | New files carry column; old files null-filled |
| Concurrent OPTIMIZE + read | Readers pin snapshot; OPTIMIZE commits new version |

### 5.7 Cost chargeback model

```text
Per team/month:
  storage_GB × rate
  + GET_count × rate
  + egress_GB × rate
  + compute_DBU × rate
  + compaction_DBU (shared pool allocated by table size)

Showback dashboard:
  "Team Analytics: 80% cost = repeated cold scans on fact_events"
  → Action: enable cache warming + partition filters
```

---

## 6. Wrap-Up

**Design summary**

- **Separate** durable bytes (object storage) from ephemeral compute (Spark/SQL clusters).  
- Use **open table format** for ACID snapshots and **multi-engine** sharing.  
- Recover **locality** via SSD cache + compaction—not rack placement.  
- Watch **request and egress billing** as much as storage GB.  
- Scale by **cache, compaction, and metadata discipline**—not recoupling HDFS.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Executor-local cache | Regional shared cache |
| Manual compaction top tables | Auto OPTIMIZE + Z-order |
| Single write engine per hot table | Managed concurrency |
| Same-region | Multi-region DR reads |

**Top risks**

1. Uncached scans at 100× → request cost explosion  
2. Small-file death spiral without compaction  
3. Stale cache serving wrong version  
4. Idle coupled-cluster thinking on cloud bill  

**What I'd measure first in production**

- Remote vs local bytes ratio, cache hit rate, GET/LIST QPS, p99 commit latency, cost per scanned TB.

---

## 7. Deeper / Related Interview Questions

1. When would you **keep** HDFS+YARN instead of migrating?  
2. How does Delta commit differ from Iceberg commit?  
3. Executor cache vs shared regional cache—trade-offs?  
4. How to handle **LIST** on buckets with billions of objects?  
5. Disaggregated shuffle: when worth the complexity?  
6. Compare Snowflake's disaggregated storage vs open lakehouse.  
7. Spot/preemptible executors with separated storage—safe?  
8. How does Photon/C++ reader change I/O profile?  
9. Range GET vs whole-file GET for Parquet footers?  
10. Write amplification on object storage vs HDFS?  
11. Multi-cloud: replicate data or federate queries?  
12. Cache invalidation across 200 concurrent clusters?  
13. OLTP CDC into lakehouse—merge vs append?  
14. Security: credential vending vs static keys on executors?  
15. Link to ranged file cache LLD interview?

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "Object storage is free" | Request + egress math |
| "Cache replaces durable storage" | Cache derived; version checks |
| "Just use HDFS in cloud" | Elasticity + multi-engine + idle cost |
| "Locality doesn't matter" | Matters for shuffle + warm cache |
| "Separate = slower always" | First scan slower; elastic + ops win |

---

## 8. Appendices

### A. Pseudocode — version-aware cache read

```text
function read_block(path, offset, len, required_version):
  key = (path, offset, len)
  entry = cache.get(key)
  if entry and entry.file_version >= required_version:
    return entry.data  // checksum verified on insert

  data, etag = object_store.range_get(path, offset, len)
  cache.put(key, data, file_version=etag_or_table_version)
  return data
```

### B. Pseudocode — optimistic commit

```text
function commit_table(table, new_files, metadata):
  version = metastore.current_version(table)
  entry = build_log_entry(version + 1, new_files, metadata)
  ok = object_store.put_if_absent(log_path(version + 1), entry)
  if not ok:
    return CONFLICT  // another writer won
  metastore.advance_version(table, version + 1)
  emit_cache_invalidate(table, version + 1)
  return SUCCESS
```

### C. Metrics checklist

```text
bytes_read_local_total
bytes_read_remote_total
cache_hit_ratio
object_store_get_rate
object_store_list_latency_p99
commit_latency_ms
compaction_backlog_files
small_file_ratio{table}
cost_estimate_daily_usd
executor_spot_interruption_rate
```

### D. Capacity cheat sheet

```text
remote_bandwidth_needed ≈ scan_qps × avg_scan_size × (1 - cache_hit)
get_rate ≈ files_read_per_query × query_qps
cache_size ≥ hot_working_set × headroom(1.2)
compaction_compute ≈ daily_ingest / target_file_size × cost_per_file
```

### E. Clarifying questions cheat sheet (30 seconds)

1. Workload mix: ETL vs BI vs ML?  
2. Data size and growth?  
3. Latency SLO for interactive?  
4. Multi-engine requirement?  
5. On-prem HDFS migration or greenfield?  
6. Cost sensitivity vs performance?

### F. HDFS+YARN vs lakehouse decision matrix

| Workload signal | Recommend |
|-----------------|-----------|
| Elastic burst compute | Lakehouse |
| Multi-engine SQL+Spark | Lakehouse |
| Fixed 24/7 70%+ utilization on-prem | HDFS+YARN may be OK |
| Sub-second repeated iteration same node | Coupled local SSD cluster |
| Regulatory object-lock immutability | Object storage |

### G. Cost worked example (monthly)

```text
500 TB storage @ $0.023/GB        ≈ $11.8K
50M GETs @ $0.0004/1K             ≈ $20
10 TB cross-AZ egress @ $0.01/GB  ≈ $100
Compute 200K DBU @ $0.10          ≈ $20K
Total ≈ $32K/month baseline

Same on coupled 50-node cluster   ≈ $73K+ idle infra
```

---

*End of storage-versus-compute trade-offs HLD prep.*
