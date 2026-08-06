# System Design: Distributed Filesystem (HDFS-like)

> **Focus areas:** NameNode/metadata · Chunks/blocks · Replication · Consistency · Rebalancing · Client-driven I/O  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct metadata math, explicit invariants, honest crash/recovery paths, rack-aware placement  
> **Interview theme:** Databricks — large-scale storage for analytics workloads

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

Goal: design a **distributed filesystem** (HDFS-like / Cloud Filesystem) for **large sequential files** (GB–TB), with centralized metadata, fixed-size blocks on commodity DataNodes, replication for durability, and client-driven data transfer.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the product? | Cluster filesystem for Spark/analytics: store Parquet, logs, checkpoints | Optimized for throughput, not POSIX latency |
| F2 | File sizes? | Mostly **large** (64 MB–multi-TB); many small files discouraged | Block size 128–256 MB; namespace pressure for small files |
| F3 | Access pattern? | **Write-once, read-many**; append allowed | Simpler than random write; lease on writer |
| F4 | Mutability? | Append + immutable after close MVP | No in-place random overwrite |
| F5 | API? | create, append, open/read, rename, delete, list | Metadata ops vs data ops split |
| F6 | Replication? | **RF=3** default | Rack-aware placement; min replication policy |
| F7 | Consistency? | Close-to-publish: readers see file after close | Visible length on close commit |
| F8 | Directory model? | Hierarchical namespace `/tenant/db/table/...` | Tree in metadata service |
| F9 | Security? | Per-path ACLs + block access tokens | NameNode issues delegation tokens |
| F10 | Checksums? | Per-chunk CRC32/CRC32C | Detect corruption on read and during replication |
| F11 | Snapshots? | Phase 2 (copy-on-write metadata) | Mention inode ref counting |
| F12 | Multi-tenant? | Quotas on space + file count | Per-directory counters |
| F13 | Decommission? | Drain node without data loss | Re-replicate blocks before removal |
| F14 | Client type? | Thick client (library) talks directly to DataNodes | NameNode not on data path for reads |

**MVP functional scope (lock with interviewer):**

1. HA metadata service (active + standby) with edit log WAL and periodic fsimage checkpoint.
2. Block size **128 MB**; RF=3; rack-aware replica placement.
3. Write path: client obtains block locations → pipeline replication DN1→DN2→DN3 → ack → next block.
4. Read path: client picks nearest replica; verify checksum.
5. Heartbeats + block reports from DataNodes; detect loss → re-replicate under-replicated blocks.
6. Balancer moves blocks for even disk utilization.
7. Lease-based single writer per file; lease recovery on client crash.

**Out of MVP (explicitly defer):**

- Random write / mmap mutable files  
- POSIX full compliance (hard links, fine-grained locking)  
- Cross-region strong consistency active-active writes  
- Erasure coding (cold tier Phase 2)  
- Automatic small-file merging (bundle files) — guidance only MVP  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Aggregate throughput? | Scale with cluster | 10+ GB/s per rack at 100× |
| N2 | Read latency? | Sequential streaming | Dominated by disk/network; metadata p99 < 10 ms |
| N3 | Durability? | Survive **2** simultaneous failures (RF=3) | No data loss if ≥1 replica survives |
| N4 | Availability (metadata)? | HA failover | RTO < 60 s; RPO ≈ 0 with synced standby |
| N5 | Namespace scale? | 10M–1B files | In-memory index + sharding path |
| N6 | Metadata QPS? | High list/stat at job planning | 50K–200K ops/s at 100× with sharding |
| N7 | Capacity? | PB–EB | 1 PB baseline cluster |
| N8 | Consistency? | No torn reads after close | Commit length on close |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Create file → write N blocks via pipeline → close → file visible with length Σ block sizes.
2. Read file → client fetches block locations → parallel reads from local rack replica.
3. DataNode fails → remaining replicas ≥ 2 → background re-replication restores RF=3.
4. Add new rack → new blocks prefer spread across racks; balancer redistributes over time.
5. Decommission node → admin flag → re-replicate blocks off node → confirm empty → remove.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Client crash mid-write | Lease expires → recovery reassigns lease or aborts incomplete file |
| Pipeline DN fails mid-block | Client rebuilds pipeline with remaining replicas; may truncate partial block |
| NameNode failover | Standby promotes; replay edit log tail; clients retry |
| Split-brain NameNode (misconfig) | **Prevent** with fencing / quorum; never dual active |
| Corrupt block replica | Reader tries next replica; DN reports bad block → delete and re-replicate |
| Small file flood | Namespace bloat; inode memory pressure; throttle + guidance |
| Hot file read | Many clients read same block; bypass via same replica + optional caching |
| Network partition client↔DN | Write timeout; lease recovery |
| Over-replication after node return | Excess replica deletion prioritized |
| Rename across directories | Metadata atomicity via single edit log entry |

### 1.4 Scales (Progressive)

| Metric | Baseline (1×) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Total capacity | 1 PB | 10 PB | 100 PB | 1 EB |
| DataNodes | 100 | 1,000 | 10,000 | 100,000 |
| Files | 10M | 100M | 1B | 10B |
| Blocks (128 MB) | ~8M | ~80M | ~800M | ~8B |
| Block replicas (RF=3) | ~24M | ~240M | ~2.4B | ~24B |
| Metadata RAM (est.) | ~4 GB | ~40 GB | Shard required | Federated namespace |
| Write throughput (agg.) | 500 MB/s | 5 GB/s | 50 GB/s | 500 GB/s |
| Metadata ops/s | 5K | 50K | 200K | 1M+ (sharded) |
| Racks / AZs | 5 | 20 | 100 | 1000+ |

**What each jump forces:**

- **10×:** NameNode federation (multiple namespaces); faster edit log (segmented); more aggressive balancer.
- **100×:** Sharded metadata by path prefix; block service separate from inode service; erasure coding tier.
- **1,000×:** Cell-based clusters; hierarchical namespace; client-side EC; cross-cell replication async.

### 1.5 Etc. (Constraints & Assumptions)

- Commodity servers with spinning disk or SSD; **network bisection** matters.
- Analytics workloads: large sequential I/O; not a database substitute.
- Single region MVP; DR via async replication to secondary cluster Phase 2.
- Block immutability after seal simplifies replica equivalence.

**Scope statement:**

> Design an HDFS-like distributed filesystem with HA NameNode, 128 MB blocks, RF=3 rack-aware replication, client-side pipelines, heartbeat-driven re-replication, and balancer—scaling from 1 PB / 10M files through 10× / 100× / 1,000× with a clear metadata sharding story.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Block and metadata counts

```text
Capacity = 1 PB = 1024^5 bytes ≈ 1.125 × 10^15 B
Block size = 128 MB = 128 × 2^20 B

Blocks (data) ≈ 1.125e15 / (128 × 2^20) ≈ 8.4 × 10^6 blocks
Replicas RF=3 → 25.2 × 10^6 replica records in block map
```

At **100×** (100 PB):

```text
~840M blocks → ~2.5B replica records
Metadata per block ~150 B (blockId, size, genstamp, 3 locations) → ~126 GB block index alone
Inode + namespace additional → metadata sharding mandatory
```

### 2.2 NameNode memory (rule of thumb)

```text
HDFS rule: ~150 B per block + ~150 B per file (historical average)
1×: 8M blocks + 10M files → (8M + 10M) × 150 B ≈ 2.7 GB + overhead → ~4 GB JVM heap

100× files/blocks → ~270 GB — does NOT fit one JVM → federation/sharding
```

**Critical insight:** Metadata scale is **O(files + blocks)**, not capacity alone — small files hurt.

### 2.3 Write throughput and pipeline

```text
Baseline aggregate write 500 MB/s
128 MB block → ~4 blocks/s cluster-wide (many clients parallel)

Single client pipeline RF=3:
  bytes on wire per user byte ≈ 3 (replication factor)
  500 MB/s user → 1.5 GB/s internal replication traffic

Per DataNode disk ~100 MB/s sustained → 500 MB/s needs ~5+ disks writing concurrently across cluster
```

At **100×** (50 GB/s):

```text
50 GB/s / 128 MB ≈ 400 blocks/s created cluster-wide
Requires thousands of concurrent pipelines + sufficient disk parallelism
```

### 2.4 Read throughput

```text
Read amplifies less (pick 1 replica)
Spark job reading 10 TB with 1000 tasks → 10 GB/task
Locality: prefer same-rack replica → saves cross-rack bandwidth
```

### 2.5 Heartbeat and block report load

```text
100 DataNodes, heartbeat every 3 s → ~33 heartbeats/s
Block report full daily; incremental on change — amortized

10K DataNodes → 3.3K heartbeats/s — NameNode handler threads must scale
100K nodes → metadata service must shard block map service
```

### 2.6 Re-replication bandwidth

```text
Lose 1 node with 20 TB and RF drops to 2 for some blocks:
  Worst case re-replicate 20 TB × (1/2) needing 3rd copy ≈ 10 TB over maintenance window
  @ 100 MB/s/node → plan hours–days; prioritize under-replicated blocks queue
```

### 2.7 Bottlenecks (ranked)

1. NameNode memory / metadata QPS hot spots  
2. Small files exploding namespace  
3. Cross-rack write bandwidth (pipeline)  
4. Re-replication storm after rack failure  
5. Hot block / hot directory listing  
6. Edit log fsync latency on metadata writes  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Inode           → file or directory metadata (name, permissions, parent, timestamps)
Block (Chunk)   → immutable 128 MB blob identified by blockId
BlockReplica    → (blockId, datanode_id, storage_id, state)
Namespace       → tree of inodes; path → inode_id
BlockMap        → blockId → list[BlockReplica]
DataNode        → stores blocks; sends heartbeats/block reports
Lease           → (file_id, client_id, expiry) exclusive writer lock
GenerationStamp → version for replica consistency during recovery
EditLog (WAL)   → append-only metadata mutations
FsImage         → periodic checkpoint snapshot of namespace + block map
```

### 3.2 Control plane vs data plane

```text
Control plane (NameNode / MetadataService):
  - namespace mutations (create, delete, rename)
  - block allocation & replica placement policy
  - lease management
  - replication monitoring

Data plane (Client ↔ DataNode):
  - actual bytes read/write
  - checksum verify
  - pipeline replication
NameNode NOT in read/write data path (except block location lookup)
```

### 3.3 Write path (create → close)

```text
1. Client → NN: create("/path/file")
2. NN: allocate new block B on DN1, DN2, DN3 (rack-aware); record in edit log
3. Client → DN1: write packets (64 KB) → DN1 forwards → DN2 → DN3 (pipeline)
4. Packet acks propagate back; checksum per packet
5. Block full → NN: addBlock(next) repeat
6. Client → NN: close(file) → NN commits final length; visible to readers
```

**Deal-breaker:** Client writes directly without NN block allocation — loses placement and recovery.

### 3.4 Read path

```text
1. Client → NN: getBlockLocations("/path/file")
2. NN returns ordered replicas per block (network topology distance)
3. Client picks closest DN per block; may read blocks in parallel
4. Verify checksum; on failure retry next replica; report bad block
```

### 3.5 Replication placement policy (rack-aware)

```text
Replica 1: writer's local rack (or local node if local write)
Replica 2: different rack in same region
Replica 3: different rack (distinct from 1 and 2)

Constraints:
  - max 1 replica per DataNode
  - min racks = 2 for RF=3 when possible
```

**Why:** survive single rack switch failure without losing all replicas.

### 3.6 Consistency model

| Operation | Guarantee |
|-----------|-----------|
| Create / mkdir | Immediately visible in namespace after NN ack |
| Write before close | Readers may not see partial file (MVP: read only after close) |
| Close | Atomic publish of file length and block list |
| Rename | Atomic at metadata level |
| Delete | NameNode removes mapping; DataNodes delete blocks async |
| Concurrent writers | **Not allowed** — lease enforces single writer |

HDFS classic: **single-writer, multiple-reader** after close.

### 3.7 Options for metadata store

| Option | Pros | Cons | When |
|--------|------|------|------|
| A. Single HA NameNode + in-memory | Simple; fast lookups | Memory ceiling | 1×–10× with federation |
| B. NameNode Federation | Multiple independent namespaces | Cross-shard paths hard | 10× |
| C. Sharded metadata (inode service) | Horizontal scale | Complex routing | 100× |
| D. Block map separate service | Offload replica index | Split consistency | 100× |
| E. KV + consensus (modern CFS) | Strong HA story | Rewrite HDFS model | Greenfield |

**Chosen path:**

- **MVP:** Active/Standby NameNode, in-memory namespace + block map, edit log on quorum storage, daily fsimage + incremental edits.
- **100×:** Federation + block service shards; path-based routing.

### 3.8 Re-replication and maintenance

```text
Under-replicated block: live_replicas < target_RF
Over-replicated: live_replicas > target_RF → drop excess

Priority queue:
  1. Critical under-replicated (only 1 left)
  2. Normal under-replicated
  3. Balancer moves (low priority)

Decommission:
  DN marked DECOMMISSIONING → re-replicate all blocks off → DECOMMISSIONED
```

### 3.9 Balancer (rebalancing)

```text
Goal: even disk utilization across DataNodes (± threshold, e.g., 10%)

Algorithm sketch:
  pick over-utilized DN O and under-utilized U
  choose block B on O movable to U (respect rack policy)
  copy B to U → NN updates block map → delete old replica on O

Throttled to avoid saturating network during business hours
```

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Block size | 128 MB | Balance metadata vs seek | 4 KB blocks |
| Replication | 3× | Survive 2 failures | RF=2 without justification |
| Metadata | In-memory + WAL | Latency | Recompute block map from scratch on every read |
| Writes | Pipeline | Bandwidth efficient | NN proxies all bytes |
| Small files | Discourage | Namespace cost | Ignore small-file problem |
| Consistency | Close-to-publish | Analytics fit | POSIX random write |
| EC vs replication | Replication MVP | Simple reads | EC for hot write path MVP |

---

## 4. Architecture Diagram

### 4.1 Cluster overview

```text
                    +---------------------------+
                    |   Active NameNode (NN)    |
                    |   + Standby NN            |
                    |   EditLog (QJM/ZKFC)      |
                    +-------------+-------------+
                                  |
            metadata ops          | heartbeats / block reports
                                  |
     +------------+---------------+---------------+------------+
     |            |               |               |            |
     v            v               v               v            v
 +--------+  +--------+     +--------+     +--------+   +--------+
 | DataNode|  | DataNode|     | DataNode|     | DataNode|   | DataNode|
 | Rack A  |  | Rack A  |     | Rack B  |     | Rack B  |   | Rack C  |
 +--------+  +--------+     +--------+     +--------+   +--------+

 Clients (Spark, distcp, CLI)
     |  \
     |   \---- data read/write (block access tokens)
     v
  DataNodes directly
```

### 4.2 Write pipeline sequence

```text
Client          NameNode        DN1 (primary)      DN2            DN3
  |--create----->|               |                  |              |
  |<-locations---|               |                  |              |
  |--write pkt------------------>|--forward pkt---->|--forward--->|
  |<-ack-------------------------|<--ack-------------|<--ack--------|
  | (repeat)                     |                  |              |
  |--close------>|               |                  |              |
  |<-success-----|               |                  |              |
```

### 4.3 Failover: DataNode dies during write

```text
Client writing block to DN1→DN2→DN3
DN2 fails:
  Client detects timeout
  Client → NN: updatePipeline(exclude=DN2, remaining=[DN1,DN3], add DN4)
  Resume from last acked packet offset (generation stamp bump)
```

### 4.4 NameNode HA failover

```text
Active NN crash:
  ZKFC detects / QJM last shared edit id
  Standby NN rolls edit log forward → becomes Active
  Clients retry metadata ops with backoff
  DataNodes continue heartbeats to new Active
```

### 4.5 Read with replica choice

```text
Client needs block B:
  NN returns [DN_local_rack, DN_same_region, DN_far]

Client tries DN_local_rack:
  on checksum error → try next
  on success → stream to consumer (Spark task)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Block immutability after seal:** sealed block bytes never change.  
2. **Replica equivalence:** all live replicas of block B have same generation stamp and length.  
3. **RF policy:** block considered healthy iff live_replicas ≥ target_RF (usually 3).  
4. **Single writer:** at most one lease holder per open-for-write file.  
5. **Metadata durability:** committed edit log record survives before client ACK on mutation.  
6. **No block loss on close:** file length commit includes complete block list.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Single DN disk fail | Re-replicate from remaining replicas |
| Rack switch fail | RF across racks; re-replicate |
| Corrupt replica | Reader failover; block scanner deletes bad copy |
| Client crash | Lease timeout → recovery (commit or abort) |
| Active NN fail | Standby promote; replay edits |
| Split brain NN | Fencing + single writer to edit log |
| Full cluster partition | Manual recovery; prefer availability tradeoffs documented |

**Lease recovery (must say):**

```text
If client dies holding lease:
  NN waits lease timeout
  Recovery protocol picks primary replica (highest gs)
  If block complete → commit; else truncate to last valid length
  Release lease for new writer or mark file abandoned
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Single HA NN; 100 DN; 128 MB blocks; balancer |
| 10× | Federation (multiple NNs); segmented edit log; 1K DN |
| 100× | Sharded block map; inode service; EC cold tier; locality scheduler |
| 1000× | Multi-cell; hierarchical namespace; async cross-cell DR |

**Small file problem:**

```text
1 KB file still consumes 1 inode + 1 block (128 MB allocated) → wasteful
Mitigations:
  - Har archive (combine files)
  - Object store for tiny assets
  - Document "block size minimum allocation"
  - Future: bundled small file store
```

### 5.3 Maintainability

- Rolling upgrade DataNodes: version compatibility protocol.  
- Block scanner periodic verify checksums.  
- Metrics: under-replicated blocks, DN capacity, edit log lag, fsimage age.  
- Safe decommission workflow in runbook.  
- Chaos: kill DN during pipeline; NN failover during rename storm.

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
HA NameNode pair + JournalNodes (QJM)
Edit log append fsync; checkpoint fsimage every 6h + 1M edits
Client library: create/write/close/read
Re-replication monitor thread on NN
Balancer CLI nightly
```

**10×**

- **Federation:** `/tenant1` → NN1, `/tenant2` → NN2; mount table at gateway.  
- Faster checkpoint (checkpoint node); more handler threads.  
- SSD volumes on DN for hot tiers optional.

**100×**

- Shard block map by `blockId % N` services.  
- Inode path hash routing.  
- Erasure coding (EC 6+3) for cold blocks; replication for hot.  
- Centralized placement policy service.

**1000×**

- Regional cells; async replication between cells.  
- Client talks to cell-local metadata gateway.  
- Global namespace via federation tree, not single NN.

### 5.5 Metadata WAL and fsimage

```text
Edit log record examples:
  OP_ADD_BLOCK(fileId, blockId, locations[])
  OP_ALLOCATE_BLOCK(blockId, dnIds[])
  OP_CLOSE(fileId, length)
  OP_DELETE(path)

Checkpoint:
  Standby or checkpoint node applies edits to in-memory tree → fsimage snapshot to storage
  Truncate old edits after checkpoint

Recovery time ≈ load fsimage + replay tail edits
  fsimage 4 GB + 1h edits → typically sub-minute to few minutes
```

### 5.6 Block report and inventory

```text
Full block report: daily (heavy)
Incremental: on block change + periodic delta

NN reconciles:
  blocks on DN not in block map → orphan → delete
  blocks in block map missing on DN → under-replicated → schedule copy
```

### 5.7 Security tokens

```text
Client auth to NN (Kerberos/OAuth)
NN issues block access token (capabilities, expiry, blockIds)
Client presents token to DN for read/write
DN validates with NN public keys or shared secret rotation
```

Prevents arbitrary clients from reading cluster disks.

### 5.8 Comparison to object storage (S3)

| Aspect | HDFS-like DFS | S3-style object store |
|--------|---------------|------------------------|
| Mutability | Append/close | PUT overwrite whole object |
| Metadata | Central NN | Flat key; listing prefix cost |
| Throughput | Locality + pipeline | HTTP horizontal |
| Rename | Cheap metadata op | Copy+delete |
| Small files | Painful | OK |
| Analytics | Native Spark | Also common via connectors |

**Interview:** DFS wins for **mutable append + locality**; object store wins for **ops simplicity + infinite scale**.

### 5.9 Erasure coding (Phase 2 sketch)

```text
Hot blocks: RF=3 replication (fast write/read)
Cold blocks (age > 7d): EC 6+3 → 1.5× storage vs 3×

Reconstruction read: contact k data nodes; higher CPU
Transition: rewrite block group asynchronously
```

---

## 6. Wrap-Up

**Design summary**

- **Split metadata and data planes** — NameNode is brain, DataNodes are muscle, clients move bytes.  
- **128 MB blocks + RF=3 rack-aware** — durability and failure tolerance with measurable overhead.  
- **Pipeline writes** — efficient replication; recovery via generation stamps and pipeline rebuild.  
- **Edit log WAL + fsimage** — fast recovery; standby promotion for HA.  
- **Re-replication + balancer** — continuous self-healing and capacity evenness.  
- Scale path: **federation → sharded metadata → cells** as files/blocks explode.

**MVP vs later**

| MVP | Later |
|-----|-------|
| HA single namespace | Federation + sharding |
| Replication only | Erasure coding tier |
| Close-to-publish reads | Partial visibility / snapshots |
| Single region | Cross-region async DR |

**Top risks**

1. NameNode memory / small files  
2. Re-replication storm after rack loss  
3. Split-brain metadata  
4. Hot spot blocks on popular datasets  
5. Underestimating cross-rack write bandwidth  

**What I'd measure first in production**

- Under-replicated block count, time-to-RF3, DN disk utilization variance, metadata ops latency, edit log lag, pipeline error rate, mean time to recover lease.

---

## 7. Deeper / Related Interview Questions

1. Walk through lease recovery when a writer dies mid-block.  
2. Why not store file data on the NameNode?  
3. How does pipeline replication compare to star (primary fan-out)?  
4. Why 128 MB blocks — tradeoffs vs 64 MB and 256 MB?  
5. How to handle the small file problem?  
6. Erasure coding vs replication — when switch?  
7. NameNode federation vs sharding — difference?  
8. How do you prevent split-brain on failover?  
9. What happens on a network partition between client and NameNode but not DataNodes?  
10. Compare HDFS to GFS — what's different today?  
11. How would you add snapshots cheaply?  
12. Hot read on one block — scaling strategies?  
13. Consistent hashing for DataNodes — good idea?  
14. How does Spark locality scheduling interact with block placement?  
15. Design cross-region DR without dual-write corruption.  

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "Store blocks in NN database" | NN memory/network bottleneck; separate data plane |
| "RF=2 is fine" | State risk explicitly; RF=3 for analytics default |
| "Random write support" | Massive complexity — defer; append-only |
| "One big NameNode forever" | Federation/sharding at 100× |
| "Ignore rack awareness" | Rack failure loses all replicas |

---

## 8. Appendices

### A. Pseudocode — block allocation (rack-aware)

```text
function allocateBlock(replication=3, writerHint):
  racks = shuffle(uniqueRacks())
  chosen = []
  for r in racks:
    dn = pickHealthyDN(r, exclude=chosen, preferLocal=writerHint)
    if dn: chosen.add(dn)
    if len(chosen) == replication: break
  if len(chosen) < replication:
    fill from any rack without colocating two replicas on same DN
  blockId = newBlockId()
  editLog.append(OP_ALLOCATE(blockId, chosen))
  return blockId, chosen
```

### B. Pseudocode — pipeline write (client)

```text
function writeBlock(block, dataStream):
  pipeline = [DN1, DN2, DN3]
  ackQueue = Pipeline(pipeline)
  for packet in splitPackets(dataStream, 64KB):
    ackQueue.write(packet)
    if not ackQueue.waitAck(timeout):  // DN failure
      pipeline = recoverPipeline(block, failedNode)
      ackQueue = Pipeline(pipeline)
      ackQueue.resumeFrom(lastAckedOffset)
  ackQueue.close()
  nn.notifyBlockReceived(block.id)
```

### C. Pseudocode — re-replication worker

```text
function replicationMonitor():
  for block in underReplicatedBlocks(priority=HIGH):
    target = chooseTargetDN(rackAware=block)
    source = chooseSourceReplica(block, exclude=target.rack overload)
    copyBlock(source, target)
    nn.addReplica(block.id, target)
  for block in overReplicatedBlocks():
    dropExcessReplica(block)
```

### D. Metadata sizing worksheet

```text
blocks ≈ total_bytes / block_size
replicas ≈ blocks × RF
metadata_bytes ≈ (blocks + files) × 150 B × 1.3 overhead
fsimage_size ≈ metadata_bytes × compress_ratio (~0.5)
```

### E. Metrics checklist

```text
nn_edit_log_lag_seconds
under_replicated_blocks
pending_replication_blocks
datanode_capacity_used_ratio
block_report_processing_ms
pipeline_create_failures_total
bad_blocks_removed_total
balancer_bandwidth_bytes
lease_recovery_count
metadata_ops_latency_ms{op}
```

### F. Capacity cheat sheet

```text
usable_capacity ≈ raw_capacity × (1 - reserved%) / RF
max_files_before_pain ≈ nn_heap_GB / (150B × 2)  // rough
replication_network ≈ write_throughput × (RF - 1)  // extra copies
re-replication_time ≈ lost_bytes / (copier_mbps × num_copiers)
```

### G. Clarifying questions cheat sheet (30 seconds)

1. File size distribution and mutability?  
2. Replication factor and rack layout?  
3. Consistency model — read during write?  
4. Expected namespace size (files)?  
5. Analytics vs general POSIX?  
6. HA RTO/RPO for metadata?

### H. Block size tradeoff table

| Block size | Metadata load | Recovery granularity | Throughput |
|------------|---------------|----------------------|------------|
| 64 MB | Higher | Finer | Good for smaller files |
| 128 MB | Medium | Balanced | **Default** |
| 256 MB | Lower | Coarser | Better for huge sequential |
| 1 GB | Very low | Poor for stragglers | Specialized |

### I. Failure timeline example

```text
T0: Rack A power loss — 20 DN offline
T+1m: 15% blocks drop to RF=2; 2% drop to RF=1 (critical)
T+5m: Re-replication prioritizes RF=1 blocks
T+6h: 95% blocks back to RF=3
T+24h: Balancer redistributes skew from surviving racks
```

### J. Related Databricks follow-ups

- Durable embedded KV for edit log segments (`durable-embedded-kv-store-lld-system-design.md`)  
- S3 object storage design contrast (`s3-object-storage-system-design.md`)  
- Hierarchical filesystem namespace LLD  
- Checksum algorithm choice (CRC32C hardware accelerated)  

### K. Glossary

| Term | Meaning |
|------|---------|
| Block / Chunk | Fixed-size storage unit (e.g., 128 MB) |
| Generation stamp | Version for replica synchronization |
| Pipeline | Chain replication DN1→DN2→DN3 |
| FsImage | Checkpointed namespace snapshot |
| Edit log | WAL of metadata operations |
| Federation | Multiple independent namespaces |
| Decommission | Safe removal of a DataNode |

### L. Rack awareness diagram (ASCII)

```text
        Rack 1          Rack 2          Rack 3
      +--------+      +--------+      +--------+
      | DN1 R1 |      | DN3 R2 |      | DN5 R3 |
      | DN2    |      | DN4    |      | DN6    |
      +--------+      +--------+      +--------+

Block X replicas: R1 on DN1 (Rack1), R2 on DN3 (Rack2), R3 on DN5 (Rack3)
Survives loss of any single rack
```

---

*End of distributed filesystem HLD prep.*
