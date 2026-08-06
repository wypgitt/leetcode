# System Design: Distributed Key-Value Store (Microsoft / Azure Platform)

> **Focus areas:** Partitioning · Quorum / Raft · WAL · Compaction · TTL · Hot keys · Multi-region Azure · Compliance tenancy · Progressive scale  
> **Style:** End-to-end infrastructure design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic; split data / control / backup planes; explicit CAP & consistency deal-breakers; Azure region/AZ honesty  
> **Interview theme:** Microsoft L61–L64 / Azure infra — design a **distributed key-value store** usable by Azure services, Microsoft 365 backends, and first-party platforms (Cosmos-like / Azure Cache–adjacent durability story without claiming a product identity)

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

Goal: Design a **multi-tenant distributed key-value store** that offers durable `Get`/`Put`/`Delete` (optional CAS/TTL), tunable consistency, Azure multi-AZ / multi-region deployment options, and operability under Microsoft-scale tenancy and compliance constraints.

### 1.0 What this is / is not

| Dimension | **Distributed KV store (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Durable low-latency point KV | Full SQL / GraphQL engine |
| Success | p99 Get low-ms regional; durable Puts; HA across AZs | Ad-hoc joins / OLAP |
| Data plane | Replicated partitions (shards/ranges) | Data warehouse |
| Query | Point ops; limited prefix/range optional | Secondary indexes everywhere |
| Correctness | Tunable; state quorum/leader model | “Always CA + global sync + single-digit ms” |
| Microsoft lens | Azure regions, sovereign clouds, Entra tenancy, compliance | Generic Redis tutorial |

### 1.1 Functional requirements

| # | Question to ask | Expected / typical answer | Design implication |
|---|-----------------|---------------------------|--------------------|
| F1 | API surface? | `Get`, `Put`, `Delete`, optional `CAS`, `TTL`, `MultiGet` | Versioned responses; idempotent clients |
| F2 | Value size? | Bytes to ~1–2 MB typical; larger → blob pointer | Hard limit + offload path |
| F3 | Range / prefix? | Optional Phase 1.5 | Ordered keys (range shards) vs hash-only |
| F4 | Consistency default? | Strong within region (leader/quorum); eventual cross-region | Raft/Paxos per shard + async geo |
| F5 | TTL? | Sessions, leases, ephemeral config | Tombstones + compaction |
| F6 | Transactions? | Single-key atomic MVP; multi-key later | Honesty about 2PC cost |
| F7 | Multi-tenant? | Subscription / resource-group / namespace | Quotas, ACLs, encryption keys |
| F8 | Change feed / CDC? | Optional for Azure Event Hubs / Service Bus consumers | WAL tail / change log |
| F9 | Backup / PITR? | Snapshots + WAL archive to blob | Backup plane separate |
| F10 | AuthN/Z? | Entra / managed identity / keys | Auth at gateway; tenant isolation |
| F11 | Cross-region? | Async geo-replication; optional sync for compliance SKUs | RPO/RTO explicit per SKU |
| F12 | Admin? | Split/merge, rebalance, failover, flush-namespace gated | Control plane + audit |

**MVP functional scope:**

1. `Put(ns, key, value, ttl?, expect_ver?)`, `Get(ns, key, consistency?)`, `Delete`, optional `CAS`.  
2. Namespaced keys; opaque values with size cap (e.g. 1 MB).  
3. Cluster partitioned into shards with **leader + followers** (RF=3 across AZs).  
4. Strong consistency on leader path; optional stale follower reads with `max_staleness`.  
5. Durability: WAL + majority replicate before ACK.  
6. Membership, failure detection, leader election per shard; online split/move.  
7. TTL via tombstones + compaction.  
8. Metrics, tracing, admin APIs, encrypted-at-rest, audit logs.

**Out of MVP:**

- Distributed SQL / multi-shard ACID  
- Global synchronous commit for all writes at single-digit ms  
- Unlimited value sizes  
- Active-active multi-writer same key across regions without conflict resolution  
- Replacing Azure Blob as large-object SoT

### 1.2 Non-functional requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Get latency (regional) | Online path | p50 < 1–3 ms; p99 < 10–20 ms |
| N2 | Put latency (durable) | Same region | p50 < 3–5 ms; p99 < 20–40 ms |
| N3 | Durability | No silent ack loss | Majority WAL policy documented |
| N4 | Availability | AZ failure OK | 99.99% with 3 AZ |
| N5 | Consistency | Tunable | Default leader-strong; geo eventual |
| N6 | Throughput | Platform-scale | Millions ops/s per region cell |
| N7 | Operability | Online rebalance | Shard move without long downtime |
| N8 | Isolation | Noisy-neighbor control | Per-tenant quotas / cells |
| N9 | Compliance | Encryption, audit, residency | CMK optional; region pin |
| N10 | Cost | Clear unit economics | `$ / M ops` + `$ / GB-month` |

### 1.3 Cases (flows & edge cases)

**Happy paths**

1. Client `Put` → gateway auth → proxy resolves shard → leader WAL + quorum → ACK + version.  
2. Client `Get` (strong) → leader ReadIndex/lease → return value.  
3. Client `Get` (eventual) → nearest healthy follower if lag ≤ bound.  
4. Node dies → lease expires → new leader → clients refresh directory epoch.  
5. TTL expires → Get returns not_found; space reclaimed on compaction.  
6. Hot range auto-splits; directory epoch increments; clients refresh on fencing.  
7. Geo async replica lags; DR failover with documented RPO.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Hot key | L1/L2 cache; key striping; client backoff; refuse unbounded fanout |
| Network partition | Majority Raft wins; minority unavailable |
| Slow follower | Remove from quorum; snapshot catch-up |
| Giant value | Reject or blob-pointer offload |
| Clock skew | Logical term/index; no wall-clock safety |
| Split brain | Quorum + fencing tokens / epoch |
| Compaction storm | Throttle vs foreground WAL |
| Rebalance mid-write | Dual-route or quiesce handoff |
| CAS conflict | Return conflict; client retry |
| Disk full | Shed writes; alert; reject Puts |
| Tenant abuse | Quota throttle; cell isolate |
| Cross-region sync demand | Offer SKU with honesty on latency |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Usable data / region | 500 TB | 5 PB | 50 PB | Multi-cell EB-class |
| Shards | 2K | 20K | 200K | 1M+ across cells |
| Nodes | 200 | 2K | 20K | Cell fabric |
| Peak Get QPS | 2M | 20M | 200M | Multi-cell |
| Peak Put QPS | 400K | 4M | 40M | Multi-cell |
| Avg value | 1 KB | 1 KB | 1–2 KB | Mixed |
| RF | 3 | 3 | 3–5 | 3 + geo |
| Azure regions | 1–2 | 3–4 | Many + sovereign | Cell + directory fabric |
| p99 Get regional | <15 ms | <15 ms | Cell-local | Edge + cells |

**What each jump forces:**

- **10×:** Automatic split/merge; compaction IO budgets; proxy tiers; directory snapshots.  
- **100×:** Regional **cells**; hierarchical control plane; hot-key service; tenant isolation cells.  
- **1,000×:** Many independent KV cells; global shard directory; no single cluster brain; sovereign cloud forks.

### 1.5 Scope / constraints

- Commodity Azure VMs / bare metal with NVMe + DRAM; LSM local engine OK.  
- In-region AZ RTT low; cross-region RTT tens–hundreds of ms — never hide this.  
- Tenants may require EU/US residency, sovereign clouds, CMK.  
- Clients: Azure services, M365 backends, first-party apps via SDK/gateway.

**Scope repeat-back:**

> Design a Microsoft/Azure-oriented distributed KV store: sharded replicated partitions, leader-quorum durable writes, LSM+WAL storage, TTL/tombstones, online rebalance, hot-key defenses, multi-tenant compliance isolation, and progressive scale from single-region clusters to multi-cell geo deployments—without pretending to be distributed SQL or magically sync-global at single-digit ms.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| Point Get | Read path | 2M/s | Leader/follower + cache |
| Point Put/Delete | Write path | 400K/s | WAL + replicate |
| Compaction | Background IO | Bursty | Storage engine |
| Rebalance / snapshot | Ops | Episodic | Admin |
| Backup / WAL ship | Continuous | Backup → Blob |
| Control plane | Membership | Low QPS | Critical correctness |
| Change feed | Consumers | Optional | CDC |

### 2.2 Capacity math

```text
500 TB usable × RF=3 → 1.5 PB raw
LSM overhead / fragmentation ~1.3–2× → plan ~2–3 PB disk in region

Avg 1 KB value → upper bound ~5e11 keys (usually fewer, larger values)

Hot working set 5%: 0.05 × 500 TB = 25 TB DRAM cluster-wide
  → often a look-aside distributed cache sits in front (see sibling cache doc)
```

### 2.3 Shard sizing

```text
Target shard data: 20–100 GB (rebuild/move hours, not days)
500 TB / 50 GB ≈ 10K shards — operable with directory + automation
Baseline design often starts 2K shards and splits

Write QPS/shard: 400K puts / 2K shards = 200 puts/s/shard — healthy
Hot key can concentrate 100× → special path mandatory
```

### 2.4 WAL & network bandwidth

```text
400K puts/s × (1 KB + 128 B overhead) ≈ 450 MB/s cluster ingest payload
RF=3 cross-node before batching: ~1.35 GB/s network+disk
With group commit + parallel shards on 200 nodes: ~2–7 MB/s/node — feasible
At 100× (40M puts/s): need cells; single region cluster melts
```

### 2.5 Latency budget (same region, cross-AZ)

```text
Gateway auth + route     0.2–0.5 ms
Leader in-mem apply      0.05 ms
WAL group commit         0.5–2 ms
Replicate to peer AZ     0.5–2 ms
Total Put p50            few ms
Get DRAM / block cache   <1–2 ms
Get NVMe SST             1–5 ms
```

### 2.6 Cross-region sync tax

```text
East US ↔ West Europe RTT ~80–100 ms
Sync RF across continents → Put p50 > 80 ms — often deal-breaker for interactive SKUs
Hence: regional primary + async geo (RPO minutes) OR explicit “sync geo” SKU with latency SLO
```

**Deal-breaker:** promising sync triple-replicate across continents at single-digit ms Put latency.

### 2.7 Directory / consistent hashing arithmetic

```text
Virtual nodes: 128–256 vnodes / physical node for hash rings
OR directory map: shard_id → {peers, epoch, key_range}

2K shards × ~200 B metadata ≈ 400 KB — trivial client cache
200K shards × 200 B ≈ 40 MB — versioned snapshots + watch diffs

Reshard move: 50 GB at 200 MB/s ≈ 250 s + catch catch-up — throttle
```

### 2.8 Quorum latency math

```text
RF=3, majority = 2 (Raft) or W=2/R=1 (Dynamo-style)
Same-AZ RTT 0.2–0.5 ms; cross-AZ +0.5–2 ms
p99 dominated by slow fsync / noisy neighbor — isolate WAL devices / Premium SSD
```

### 2.9 Compaction write amplification

```text
LSM write amp often 10–30× depending levels
400K puts/s × 1 KB × 15 amp ≈ 6 GB/s cluster disk write — capacity plan!
Throttle compaction vs foreground; compaction_debt metric before latency cliff
```

### 2.10 Tombstone / TTL tax

```text
Delete-heavy or short-TTL workloads retain tombstones until compaction proves safety
Budget tombstone bytes/count per shard; force compact when exceeded
TTL storm after lease expiry event → compaction backlog risk
```

### 2.11 Cost sketch (interview)

```text
Dominant: NVMe + network + DRAM cache tier
Track: $ / M durable puts, $ / GB-month usable, origin/cache hit if layered
1% Get miss increase at 2M QPS → +20K origin-equivalent ops/s — quantify
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `Put(ns, key, value, ttl?, expect_ver?)` | Upsert; optional CAS |
| `Get(ns, key, consistency?)` | Value + version / not_found |
| `Delete(ns, key, expect_ver?)` | Tombstone |
| `MultiGet(ns, keys[])` | Bounded fanout |
| `GetPrefix(ns, prefix, limit)` | Optional ordered scan |
| Admin: split/merge/move/snapshot/failover | Control plane |

**Key encoding:**

```text
FullKey = tenant_id | ns | user_key
Version = (raft_term, log_index) or monotonic epoch-seq per shard
ETag / CAS = version opaque to clients
```

**REST / gRPC surface (Azure-style):**

```text
PUT    /v1/{tenant}/{ns}/items/{key}
GET    /v1/{tenant}/{ns}/items/{key}?consistency=strong|eventual
DELETE /v1/{tenant}/{ns}/items/{key}
POST   /v1/{tenant}/{ns}/items:batchGet
Headers: Authorization, x-ms-client-request-id, If-Match
```

### 3.2 Component inventory

| Component | Role |
|-----------|------|
| Client SDK | Retries, hedging, directory cache, auth |
| Front Door / API Gateway | TLS, Entra, WAF, rate limits |
| KV Proxy / Router | Shard resolve, MultiGet scatter-gather |
| Shard Directory | key_range → shard → peers + epoch |
| Shard replicas | Leader + followers; Raft; LSM |
| Hot-Key Controller | Detect Zipf; replicate/stripe |
| Control Plane | Membership, rebalancer, config |
| Backup Plane | Snapshot + WAL → Azure Blob |
| Observability | Metrics, traces, audit |
| Change Feed | Optional WAL consumers |

### 3.3 Partitioning — Why X over Y

| Approach | Pros | Cons | Deal-breaker when |
|----------|------|------|-------------------|
| **Hash shards** | Even load | Weak range | Need prefix scans |
| **Range shards + directory** | Split/scan; operable moves | Hot ranges | No auto-split |
| Consistent hash ring alone | Simple mental model | Awkward tenant moves | Enterprise tenancy |
| Static modulo | Easy demo | Rebalance rebuild | Any 10× growth |

**Chosen:** **Range-partitioned shards** with a **versioned shard directory** (hash-prefix optional for tenant mixing):

- Future prefix scans.  
- Hot ranges split.  
- Directory epoch fences stale clients.  
- Aligns with Azure resource-model mental model (explicit placement).

### 3.4 Replication & consensus — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Raft per shard** | Clear leadership & durability | Many groups overhead | **Strong MVP** |
| Multi-Paxos | Proven | Complexity | Fine alternative |
| Leaderless quorum (Dynamo) | Write availability | Conflicts; read repair | If AP preferred |
| Primary-backup custom | Simple | Subtle failovers | Risky unless careful |
| Async only | Fast | Data loss | Cache ≠ DB |

**Chosen:** **Raft (or equivalent) per shard**, RF=3 across AZs in an Azure region:

- Put ACK after majority durable log.  
- Get default from leader (linearizable option).  
- Optional follower reads with `max_staleness`.  
- Geo: async ship committed log / snapshots to paired region.

**Deal-breaker:** “eventual is fine” for ACL/entitlement keys without telling clients when stale.

### 3.5 Storage engine — Why X over Y

| Engine | Pros | Cons | When |
|--------|------|------|------|
| **LSM (RocksDB-class)** | High write throughput | Compaction IO | **Default** |
| B-Tree | Read-friendly | Random write amp | Small read-heavy |
| In-memory + snap | Fast | Cost / durability story | Pure cache |
| Bitcask-style | Simple teaching | Compaction/range limits | Toy designs |

**Chosen:** LSM per node: Memtable + WAL → SST levels; tombstones for delete/TTL; rate-limited compaction.

### 3.6 Multi-region Azure strategy

| SKU | Write path | RPO | Latency | Use |
|-----|------------|-----|---------|-----|
| Single-region HA | Raft in-region | ~0 (AZ) | Best | Default interactive |
| Async geo | Primary region + async | Minutes | Regional p99 | Most global apps |
| Sync geo (premium) | Cross-region majority | ~0 | High latency | Compliance niches |

**Chosen default:** single-region strong + async geo DR. Offer sync geo as explicit SKU.

### 3.7 Multi-tenancy & compliance

| Mechanism | Purpose |
|-----------|---------|
| Namespace + tenant_id in key | Logical isolation |
| Quota (ops, storage, connections) | Noisy neighbor |
| Optional dedicated cells | Enterprise / sovereign |
| Encryption at rest (platform or CMK) | Compliance |
| Audit trail on admin + data-plane samples | SOC / ISO |
| Region pin | Data residency |

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Partition | Range + directory | Split/scan/ops | Static hash no move |
| Consensus | Raft per shard | Clear durability | Hope-based replication |
| Engine | LSM | Write-heavy platform | Unbounded B-Tree random write |
| Cross-region | Async DR default | Latency honesty | Sync-global + fast for all |
| Hot key | Cache + stripe | Zipf reality | Ignore hot keys |
| Multi-key txn | Out of MVP | Honesty | Hidden 2PC |
| Tenancy | Quotas + cells | Azure enterprise | Shared-everything chaos |

---

## 4. Architecture Diagram

```text
  Apps / Azure services / M365 backends
              |
              v
     +--------+--------+
     | Front Door/APIM |  TLS, Entra, WAF, RL
     +--------+--------+
              |
              v
     +--------+--------+
     | KV Proxy/Router |  MultiGet, hedge, tenant quota
     +--------+--------+
              |
              v
     +--------+--------+
     | Shard Directory |  range→shard→leader, epoch
     +--------+--------+
              |
     +--------+--------+--------+
     |                 |        |
     v                 v        v
 +---+---+         +---+---+  ...
 |Shard A|         |Shard B|
 | L F F |         | L F F |   RF=3 across AZs
 +---+---+         +---+---+
     |                 |
     v                 v
  LSM+WAL           LSM+WAL
  (NVMe)            (NVMe)

 Control Plane: membership, rebalancer, config, cert rotation
 Backup Plane:  snapshot + WAL archive --> Azure Blob (CMK optional)
 Hot-Key Ctrl:  sketches --> replicate / stripe directives
 Geo:           async log/snapshot ship --> paired Azure region
 Observability: metrics, traces, audit
```

**Put path:**

```text
Client Put
  -> auth + tenant quota
  -> resolve shard (cached map + epoch)
  -> leader append Raft log
  -> majority WAL ack
  -> apply memtable
  -> respond version / etag
```

**Get path (linearizable):**

```text
Client Get(strong)
  -> leader ReadIndex / lease read
  -> memtable / block cache / SST
  -> return
```

**Follower stale read:**

```text
Get(eventual, max_stale=100ms)
  -> nearest follower if lag OK else forward leader
```

**Split path:**

```text
Auto/admin choose split key
  -> dual-route or brief quiesce
  -> new Raft group
  -> directory epoch++
  -> clients refresh on fencing mismatch
```

**Degrade modes:** shed MultiGet width; reject oversized values; read-only on disk pressure; cell isolate noisy tenant; geo failover with RPO > 0 acknowledged.

---

## 5. Design Deep Dive

### 5.1 Reliability (R)

#### 5.1.1 Invariants

1. **Acked Put is in majority WAL** for the shard’s primary region.  
2. **Directory epoch fencing** — stale clients cannot write wrong leaders forever.  
3. **Single leader per shard term** (Raft).  
4. **Tombstones visible as delete** before space reclaim.  
5. **Backup plane never mutates serving truth** silently.  
6. **Tenant isolation** — no cross-tenant key access without authz.  
7. **Encryption keys** rotated without plaintext leakage.

#### 5.1.2 Failure handling

| Failure | Mechanism |
|---------|-----------|
| Leader crash | Election; clients refresh |
| AZ loss | Remaining majority (RF=3 across AZs) |
| Disk corruption | Checksums; restore from peers/backup |
| Lost minority | Snapshot + log catch-up |
| Directory outage | Cached maps continue; make directory HA (Raft/etcd-like) |
| Region loss | Promote geo secondary; accept RPO |
| Compaction backlog | Throttle writes; prioritize WAL |

#### 5.1.3 Durability & WAL

```text
Group commit windows: coalesce Puts → one fsync
Checksum every record; CRC on SST blocks
Never ACK before majority durable (strong SKU)
Optional: ack after local fsync only = reduced durability SKU (document!)
```

#### 5.1.4 Consistency honesty matrix

| Mode | Guarantee | Latency | Use |
|------|-----------|---------|-----|
| Strong / linearizable | Leader reads | Higher | Authz, counters needing accuracy |
| Bounded staleness | Follower lag ≤ T | Lower | Feeds, configs |
| Eventual geo | Cross-region lag | Regional | DR / analytics |

### 5.2 Scalability (S)

| Scale | Architecture jump |
|-------|-------------------|
| 1× | Single-region Raft shards + directory + proxies |
| 10× | Auto split/merge; compaction budgets; proxy scale-out; WAL device isolation |
| 100× | **Cells** per tenant/workload class; hierarchical directory; hot-key service |
| 1,000× | Many cells + global router; sovereign clouds; no single meta brain |

#### 5.2.1 Hot keys

Detection: Count-Min / top-K sketches on proxies and leaders.  
Mitigations: (1) look-aside cache, (2) replicate hot key to N readers, (3) stripe key into K subkeys with app merge, (4) admit/reject overload.  
**Never** assume uniform hash eliminates Zipf.

#### 5.2.2 MultiGet fanout

Bound keys per call (e.g. 100). Scatter with hedged retries carefully — hedging amplifies load. Partial results + continuation tokens for large sets.

#### 5.2.3 Rebalance without meltdown

Throttle bytes/s per move; prefer off-peak; dual-route reads during catch-up; pause moves when compaction_debt high.

### 5.3 Maintainability (M)

| Practice | Detail |
|----------|--------|
| Cell templates | Identical shard software images |
| Canary | % shards / % tenants |
| Chaos | Kill leader, lose AZ, stall compaction |
| Runbooks | Split brain checklist, disk full, geo failover |
| Schema-less honesty | Values opaque; app owns evolution |
| Ownership | Data plane team vs tenant app team paging matrix |
| Compliance evidence | Audit exports, encryption attestations |

### 5.4 Compaction deep dive

- Leveling vs universal compaction tradeoffs (read amp vs write amp).  
- Separate foreground WAL disk from SST disks when possible.  
- Tombstone GC must respect snapshot / change-feed retention.  
- **Priority:** never let compaction starve WAL; never let WAL fill disk silently.

### 5.5 TTL deep dive

```text
Put with TTL → store expire_at absolute (server time)
Get → if now >= expire_at treat as miss (lazy)
Compaction → drop expired; write tombstone if needed for replicas
Clock: use hybrid logical or leader time; document skew bound
```

### 5.6 Security & compliance (Microsoft-specific)

- Entra ID / managed identities for service principals.  
- Per-tenant encryption keys (platform-managed or CMK via Key Vault).  
- Soft-delete / purge protection for compliance SKUs.  
- Data residency: refuse cross-region replication if policy forbids.  
- Admin ops require PIM-like elevation + audit.  
- TLS everywhere; private-link style network isolation for enterprise.

### 5.7 Progressive scale narrative (interview script)

> At baseline we run one Azure region, RF=3 across AZs, Raft per shard, LSM+WAL.  
> At 10× we automate splits and treat compaction as a first-class capacity signal.  
> At 100× we cell the fleet so a tenant or workload cannot take down the shared brain.  
> At 1,000× the product is a fabric of cells with a global directory—not a bigger single cluster.

---

## 6. Wrap-Up

### 6.1 What we designed

A Microsoft/Azure-oriented distributed KV store: range-sharded Raft replicas, LSM+WAL durability, TTL/tombstones, directory fencing, hot-key controls, multi-tenant quotas/cells, async geo DR, backup to blob, progressive scale to multi-cell.

### 6.2 Key decisions worth defending

1. KV ≠ SQL — keep MVP honest.  
2. Raft majority before ACK for strong SKU.  
3. Range + directory for operable splits.  
4. Async geo default; sync geo is a priced SKU.  
5. Hot keys first-class (Zipf).  
6. Compaction debt as SLO signal.  
7. Tenant isolation / CMK / residency as product features.  
8. 1000× = cells, not infinite vertical scale.

### 6.3 Risks & follow-ups

Directory HA; compaction storms; hot-key SEVs; geo failover RPO surprises; CMK key unavailability blocking reads; MultiGet amplification; tombstone piles from TTL storms.

### 6.4 Closer

> **Distributed KV Store**: explicit consistency planes, Azure AZ/region honesty, WAL+quorum durability, operable sharding, compliance tenancy, progressive cells—defend every CAP claim with latency math.

---

## 7. Deeper / Related Interview Questions

**Q1. Hash vs range partitioning?**

**A:** Hash balances load; range enables prefix/scan and clean splits. Prefer range+directory for operable Azure-scale clusters; hash-prefix within tenant if needed.

**Q2. Why Raft over leaderless quorum?**

**A:** Clear single leader simplifies linearizable reads and conflict-free Puts. Leaderless (Dynamo) favors AP with vector clocks—mention when write-availability under partition is the #1 goal.

**Q3. What is a WAL and why fsync?**

**A:** Write-ahead log records mutations before apply. Fsync (or group commit) makes acknowledged data survive process crash; quorum WAL survives node loss.

**Q4. How does compaction work?**

**A:** LSM flushes memtables to SST; merges levels to reclaim space and drop tombstones. Write amp is the tax; throttle so foreground Puts keep p99.

**Q5. How do you implement TTL?**

**A:** Store expiry; lazy filter on Get; physical delete in compaction. Mind clock source and change-feed retention.

**Q6. Hot key remedies?**

**A:** Cache, replicate, stripe, admit control. Measuring top-K continuously beats hoping hashes are uniform.

**Q7. Quorum R/W settings?**

**A:** With Raft majority, W_eff=majority. Dynamo-style R+W>N for strong reads. State your N/R/W and failure model.

**Q8. Read repair vs anti-entropy?**

**A:** Read repair fixes touched keys; Merkle/anti-entropy repairs idle divergence. Both useful; Raft reduces divergence within primary region.

**Q9. How do clients find the leader?**  

**A:** Cached shard directory with epoch; on redirect/fencing error, refresh. Avoid gossip-only without epoch.

**Q10. Cross-region consistency?**

**A:** Default async. Sync geo increases Put latency by RTT. Never claim both sync-global and single-digit ms.

**Q11. CAS / optimistic concurrency?**

**A:** `If-Match: version` on Put; conflict → 412/409; client rereads. Prevents lost updates on single key.

**Q12. Large values?**

**A:** Reject > limit or store pointer to Blob; cache small metadata in KV.

**Q13. How to rebalance safely?**

**A:** Throttled move, dual-route, epoch bump, pause under IO debt. Never big-bang remap.

**Q14. Multi-tenant noisy neighbor?**

**A:** Per-tenant QPS/storage quotas; dedicated cells for whales; admission control at proxy.

**Q15. Encryption / CMK failure mode?**

**A:** If CMK unavailable, fail closed for that tenant (document). Cache DEKs with short TTL carefully.

**Q16. Change feed design?**

**A:** Tail committed Raft log / dedicated CDC topic; at-least-once; ordered per shard/key.

**Q17. Backup / PITR?**

**A:** Periodic SST snapshots + WAL archive to Blob; restore creates new shard replicas; test restores regularly.

**Q18. Split brain prevention?**

**A:** Raft votes + durable term; directory epoch fencing; never dual active leaders for same shard term.

**Q19. Follower reads safe for authz?**

**A:** Usually no—use strong/leader for security decisions. Stale allow is a security bug.

**Q20. Deal-breaker answers?**

**A:** Sync cross-coast + 5 ms Put; ignore hot keys; static hashing with no move; unbounded MultiGet; shared plaintext keys across tenants.

**Q21. Consistent hashing details?**

**A:** Vnodes smooth balance; weighted by capacity; minimize key movement on node add/remove. Directory-based maps often more operable at enterprise scale.

**Q22. How do you test correctness?**

**A:** Jepsen-style partition tests; linearizability checkers on strong path; chaos AZ loss; property tests for CAS/TTL.

**Q23. Memtable flush vs Put latency?**

**A:** Stall if flush backlog; multiple memtables; isolate flush threads; alert on flush latency.

**Q24. Who pages?**

**A:** KV platform for Raft/disk/compaction; tenant app for poison values / bad CAS loops; jointly for hot-key SEVs.

**Q25. Azure private networking?**

**A:** Private endpoints / VNet injection; deny public data plane for enterprise SKUs.

---

## 8. Appendices

### A — Glossary

| Term | Meaning |
|------|---------|
| WAL | Write-ahead log |
| Raft term | Leadership generation |
| Directory epoch | Fencing token for shard map |
| Tombstone | Delete marker retained until compacted |
| Cell | Failure-isolated KV deployment unit |
| CMK | Customer-managed encryption key |
| RPO/RTO | Data loss / recovery time objectives |
| Write amp | Extra IO from compaction |
| Deal-breaker | Sync-global+fast; ignore Zipf; no fencing |

### B — Oncall checklist

- [ ] Put/Get p99 & error budgets  
- [ ] Compaction debt / disk util  
- [ ] Leader election rate  
- [ ] Hot-key dashboard  
- [ ] Geo lag SLO  
- [ ] Directory HA healthy  
- [ ] CMK / cert expiry  

### C — Key / metadata schema

```text
{tenant}/{ns}/{key} -> {
  value, version:(term,index),
  expire_at?, checksum, flags
}
shard_map_epoch -> snapshot blob
hot:{key} -> replication/stripe directive
```

### D — Scale checklist

Shards → compaction budgets → cells → global directory fabric; always quantify cross-region RTT.

### E — Estimation cheat-sheet

```text
raw_disk ≈ usable × RF × lsm_overhead
puts_bw ≈ put_qps × (value + overhead) × RF
shards ≈ usable / target_shard_size
compaction_bw ≈ put_payload × write_amp
```

### F — Closer checklist

- [ ] Consistency modes named  
- [ ] WAL + quorum ACK  
- [ ] Split/rebalance story  
- [ ] Hot keys  
- [ ] Geo RPO honesty  
- [ ] Tenant/compliance  

---

## Deep Technical Notes — Distributed KV

### Group commit

Coalesce many Puts into one fsync window (e.g. 1 ms) to amortize disk latency. Cap window to protect p99. Trade throughput vs latency explicitly.

### Snapshot catch-up

Slow follower: install SST snapshot + remaining log. Throttle so leader disk not stolen from foreground. Prefer incremental where possible.

### Membership changes

Joint consensus / explicit config changes in Raft. Never “just add node” without log configuration entry.

### Hedged Gets

Duplicate Get to second replica after delay threshold; cancel loser. Helps p99; risks load amplification—gate under overload.

### Anti-entropy across geo

Async ship committed index watermarks; verify checksums; alert on lag. Failover runbooks must state last applied index.

### Soft delete for compliance

Mark deleted; retain until legal hold expires; separate purge API with dual control.

### MultiGet partial failure

Return per-key status; do not fail entire batch on one shard timeout; clients retry missing keys.

### Tenant cell routing

```text
tenant_id -> cell_id (sticky)
cell_id -> regional proxies + shard directory
migration: dual-read / dual-write windows carefully
```

---

## Interview Cards — Distributed KV (Microsoft)

### Card 1: Hash vs range?

Range+directory for splits/scans; hash for pure point balance. Azure tenancy prefers operable moves.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Name Azure region/AZ placement, compliance residency constraint, and the customer-visible failure if ignored.

### Card 2: Raft vs Dynamo quorum?

Raft for clear linearizability; Dynamo for AP. State N/R/W or majority explicitly.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Tie to Azure multi-AZ RF=3 story and Entra-secured admin failover.

### Card 3: WAL + fsync?

Durability before ACK; group commit for amp. Never silent ack-ahead of disk for strong SKU.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Map to Premium SSD / NVMe SKUs and supportability evidence.

### Card 4: Compaction debt?

Write amp tax; throttle; alert before p99 cliff. Tombstones from TTL amplify debt.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Capacity planning with FinOps — `$/GB` includes amp.

### Card 5: Hot keys?

Detect + cache/replicate/stripe. Hashing does not remove Zipf.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Protect shared Azure cell from one viral tenant key.

### Card 6: Cross-region?

Async default; sync SKU with RTT tax. Speak RPO/RTO.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Sovereign cloud and data residency refusals.

### Card 7: TTL?

Lazy expire + compaction GC; hybrid clocks; change-feed retention.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Session/lease keys for M365-like workloads.

### Card 8: Directory fencing?

Epoch++ on map change; stale clients refresh. Prevents split-brain writes.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Control-plane HA as seriously as data plane.

### Card 9: CAS?

If-Match versions; conflict errors; no silent lost update.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** API design parity with Azure optimistic concurrency patterns.

### Card 10: Multi-tenant isolation?

Quotas, ACLs, optional dedicated cells, CMK.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Enterprise compliance deal-breaker if missing.

### Card 11: Large values?

Size cap or Blob pointer. KV stays metadata-fast.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Compose with Azure Blob; don't reinvent object store.

### Card 12: Backup/PITR?

Snapshots + WAL to Blob; tested restores.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Auditability for support / compliance.

### Card 13: Follower reads?

OK with max_staleness; not for authz.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Security review will ask this—answer crisply.

### Card 14: Deal-breaker?

Sync-global+fast; ignore hot keys; no fencing; cross-tenant leakage.

**Follow-ups:** What breaks at 10×? Who pages? Fallback? Metric?

**Microsoft angle:** Interviewers reward explicit “I won't promise that.”

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope: KV not SQL; Azure multi-AZ; consistency SKUs |
| 5–12 | Estimation: disk, WAL BW, quorum RTT, geo tax |
| 12–22 | HLD + ASCII: directory, Raft shards, LSM |
| 22–35 | R/S/M: failover, compaction, hot keys, cells |
| 35–45 | Tradeoffs, compliance, Q&A |

---

## 10. Operability

### Golden signals

Put/Get latency, error rate, disk util, compaction debt, leader elections, geo lag, hot-key QPS, tenant throttle rate.

### Rollback ladder

Disable follower reads → pause rebalance → write-shed noncritical tenants → read-only mode → cell isolate → geo failover.

### Kill switches

Per-tenant deny; stop admissions; disable change feed; block MultiGet > N; freeze splits.

### Security / privacy

Namespace ACLs; CMK; audit admin; private networking; residency pin.

### Cost worksheet

NVMe + network + DRAM cache vs missed-SLA refunds. Lever: hit cache tier, right-size RF, compaction efficiency.

### Progressive scale

10× splits/compaction; 100× cells; 1,000× fabric + sovereign.

### Cross-team deps

Identity (Entra), Key Vault, Blob backup, networking, capacity/FinOps, tenant app teams.

---

## More Interview Q&A — Distributed KV

**Q1. RocksDB vs home-grown?**

**A:** Prefer mature LSM; invest in sharding/ops. Custom engines need extreme justification.

**Q2. Why not store everything in Redis?**

**A:** Redis-as-cache ≠ durable KV. Persistence modes exist but operational model differs; be explicit about durability.

**Q3. Idempotent Puts?**

**A:** Client request IDs + dedupe window OR pure CAS overwrite semantics documented.

**Q4. How many shards per node?**

**A:** Tens–hundreds; too many → Raft overhead; too few → coarse balance. Measure election and fd limits.

**Q5. Secondary indexes?**

**A:** Out of MVP; app dual-writes or separate index service. Global secondary index is a different product.

**Q6. Serialization format?**

**A:** Opaque bytes; optional schema registry at app layer. Avoid server-side schema coupling.

**Q7. Observability cardinality?**

**A:** Metrics by cell/shard class; exemplars for tenant; not per-key Prometheus labels.

**Q8. Chaos: lose 2 AZs?**

**A:** With RF=3 majority lost → unavailable. Discuss RF=5 for stricter SKUs vs cost.

**Q9. Canary config flags?**

**A:** Per-cell feature flags; shadow reads comparing versions; never dual-write divergent codecs without epoch.

**Q10. Thundering herd after outage?**

**A:** Client jitter; server admission; prefer stale reads temporarily for noncritical classes.

**Q11. Compare to Azure Cosmos DB mental model?**

**A:** Partition keys, RU-like quotas, consistency levels, geo—map concepts without claiming internals.

**Q12. Compare to etcd/ZooKeeper?**

**A:** Those are low-volume coordination stores. General KV needs many shards; don't put high QPS in one Raft group.

**Q13. Coordination vs data plane?**

**A:** Keep membership/directory HA but separate from bulk KV bytes.

**Q14. Delete performance?**

**A:** Tombstone cheap; space reclaim later. Delete storms → compaction debt.

**Q15. Scan vs many Gets?**

**A:** Prefix scan if ordered; else MultiGet. Bound both.

**Q16. Encryption performance?**

**A:** AES-NI/TLS offload; encrypt SST; DEK cache. Measure Put p99 with CMK path.

**Q17. Multi-cluster migration?**

**A:** Dual-write window or change-feed mirror; cutover with epoch; verify checksum samples.

**Q18. What metric proves durability?**

**A:** Zero ack-loss in crash tests; restore drills; geo lag < RPO.

**Q19. What metric proves isolation?**

**A:** Cross-tenant access attempts denied; chaos noisy-neighbor QPS contained.

**Q20. Closing line?**

**A:** “I’d ship regional Raft-LSM shards with directory fencing, async geo, explicit consistency SKUs, and cell isolation—and I refuse sync-global single-digit ms.”

---

## Progressive Architecture Jump Cards

### 1× — Regional MVP

Proxies + directory + Raft RF=3 + LSM. Strong Put/Get. Backup to Blob nightly + WAL archive.

### 10× — Operable growth

Auto-split; compaction SLO; WAL device isolation; MultiGet bounds; hot-key sketches.

### 100× — Cells

Tenant/workload cells; hierarchical routers; dedicated whale cells; per-cell directories.

### 1,000× — Fabric

Global cell directory; sovereign clouds; automated DR drills; approx admission at edge; no single brain.

---

## Failure Scenario Scripts (say aloud)

**Scenario A — Leader disk stall:** Raft steps down on heartbeat miss; new leader; p99 spike brief; compaction continues on survivors; page if elections flapping.

**Scenario B — AZ loss:** Two AZs remain; majority OK; re-replicate to restore RF when AZ returns; capacity headroom pre-planned.

**Scenario C — Geo failover:** Promote secondary; publish RPO gap; clients redirect via Traffic Manager / Front Door; reconcile divergent in-flight Puts.

**Scenario D — TTL storm:** Lease expiry event deletes millions keys; tombstones spike; throttle deletes; prioritize compaction; communicate storage lag.

**Scenario E — CMK disable:** Tenant data plane fails closed; status page; support runbook; no plaintext fallback.

---

## API Contract Sketch (gRPC)

```text
service KeyValue {
  rpc Put(PutRequest) returns (PutResponse);
  rpc Get(GetRequest) returns (GetResponse);
  rpc Delete(DeleteRequest) returns (DeleteResponse);
  rpc BatchGet(BatchGetRequest) returns (BatchGetResponse);
}

message PutRequest {
  string tenant = 1;
  string ns = 2;
  bytes key = 3;
  bytes value = 4;
  int64 ttl_ms = 5;
  bytes expect_version = 6;
  string request_id = 7;
}
```

Idempotency: `request_id` retained short TTL on leader for dedupe of retried Puts when desired.

---

## Consistency Worked Examples

**Example 1 — Counter-like key without CAS:** Lost update under concurrent Puts. Fix: CAS loop or atomic server `Add` API (extension).

**Example 2 — ACL key with follower read:** Stale allow after revoke. Fix: strong read for authz path.

**Example 3 — Config key with bounded staleness:** 5s lag OK for feature flags; document.

**Example 4 — Geo: write East, read West immediately:** Miss/stale until async catches up; session stickiness or read-your-write token (region pin).

---

## Capacity Planning Worksheet

```text
Inputs: usable_TB, put_qps, get_qps, avg_value, rf, write_amp, hotspot_factor
Disk_TB = usable_TB * rf * lsm_overhead
Wal_GBps = put_qps * avg_value * rf / 1e9
Nodes ≈ max(Disk_TB / disk_per_node, Wal_GBps / wal_budget_per_node, get_qps / get_budget_per_node)
Hot_budget = hotspot_factor * avg_load  # size cache/stripe for this
Cells ≈ ceil(nodes / nodes_per_cell_max)
```

Work an example in interview with round numbers; show unit cancellations.

---

## Ownership & SEV Model

| Symptom | Primary owner | Secondary |
|---------|---------------|-----------|
| Raft elections storm | KV platform | — |
| Tenant Put 429s | Tenant app (quota) | Platform if bug |
| Geo lag breach | KV platform | Capacity |
| Wrong value app logic | Tenant app | — |
| Cross-tenant leak | Security + platform | Sev-1 |
| Compaction debt SEV | KV platform | FinOps |

---

## Sample 60-Second Pitch

> We expose a versioned Get/Put/Delete API with tenant namespaces. Data is range-partitioned into many Raft groups, three replicas across Azure AZs, LSM with WAL for durability. Clients cache a fenced shard directory. Strong reads hit leaders; eventual reads may use followers with a lag bound. Cross-region is async by default with explicit RPO. Hot keys are detected and mitigated; compaction debt is a capacity signal; noisy tenants get quotas or dedicated cells. At extreme scale we federate cells rather than growing one cluster forever.

---

## Appendix G — Anti-patterns

1. One Raft group for the whole dataset.  
2. Sync geo for all SKUs.  
3. Unlimited value sizes in memtable path.  
4. Per-key metrics in Prometheus.  
5. Follower reads for security tokens.  
6. Rebalance at full line-rate during peak.  
7. Silent fail-open auth on gateway.  
8. Claiming linearizability under async geo.

---

## Appendix H — Reading map (concepts, not product claims)

- Log replication / Raft mental model  
- LSM compaction & write amplification  
- Dynamo papers for quorum AP contrast  
- Azure well-architected: reliability, security, cost  
- Consistency models primer (linearizability vs eventual)

---

## Appendix I — Mock interviewer pushbacks

**Push:** “Just use strong consistency everywhere.”  
**Reply:** “In-region yes by default; cross-region strong implies RTT—productize as SKU.”

**Push:** “Hashing fixes hot keys.”  
**Reply:** “Hashing balances keys, not popularity. One key still hits one shard.”

**Push:** “Why not SQL?”  
**Reply:** “Different product; secondary indexes and multi-row ACID explode scope.”

**Push:** “How do you guarantee zero RPO DR?”  
**Reply:** “Only with sync replication; here’s the latency. Otherwise RPO>0.”

**Push:** “Show me numbers.”  
**Reply:** Walk §2 arithmetic on whiteboard.

---

## Appendix J — Definition of done for MVP launch

- [ ] Strong Put/Get path green under AZ kill  
- [ ] Backup restore drill success  
- [ ] Tenant quota enforced  
- [ ] Hot-key dashboard + runbook  
- [ ] Compaction debt alert  
- [ ] Latency SLO dashboards  
- [ ] Security review (authz, encryption, audit)  
- [ ] Load test at 2× peak  

---

*End of Microsoft Distributed Key-Value Store system design prep.*
