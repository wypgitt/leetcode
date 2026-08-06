# System Design: Leader–Follower Election (Raft / Paxos–Style, Productized)

> **Focus areas:** Leader election · Quorum · Terms/epochs · Fencing · Heartbeats · Split-brain prevention · Membership changes · Witnesses · Multi-region  
> **Style:** Infrastructure / coordination service design with progressive scale (10× → 100× → 1,000×)  
> **Microsoft themes:** Azure Service Fabric–like reliability · Cosmos DB lease patterns · AKS / control-plane HA · regional pairs · Entra for admin APIs · “design election as a product”

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

Goal: **bound what “election” means as a product**—not only the Raft textbook algorithm, but a **coordination primitive** teams use for primary selection, partition leadership, singleton workers, and failover—with correct fencing at Microsoft Azure scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who uses this? | Internal services needing a primary | Election-as-a-service / library + managed service |
| F2 | Unit of leadership? | **Shard / group / resource** | Many independent election groups |
| F3 | Safety goal? | ≤1 active leader per group per term | Quorum + fencing tokens |
| F4 | Liveness goal? | Elect new leader after failure | Timeouts + randomized backoff |
| F5 | Data vs lease-only? | Both: Raft log groups AND lease leaders | Two modes or unified epoch API |
| F6 | Clients? | Need to discover current leader | Lookups + watches |
| F7 | Fencing? | Old leader must not commit | Epoch in every write path |
| F8 | Membership? | Add/remove voters | Joint consensus / reconfig |
| F9 | Observers? | Read-only followers | Non-voting learners |
| F10 | Multi-region? | Prefer region for latency; DR | Voter placement + witness |
| F11 | Admin? | Force step-down, inspect terms | Audited control plane |
| F12 | Auth? | Only trusted nodes vote | mTLS + Entra node identity |

**MVP functional scope (lock with interviewer):**

1. Create an **election group** with odd-sized voter set (3/5).  
2. Nodes run **candidate/leader/follower** roles with **terms**.  
3. Leader sends heartbeats; election on timeout.  
4. Clients query **leader + epoch**; watches on change.  
5. **Fence** operations with epoch (reject stale).  
6. Persist votes/terms on disk (crash-safe).  
7. Basic metrics: election rate, leader tenure, quorum loss.  
8. Optional: lease-only mode without full replicated log.

**Out of MVP (explicitly defer):**

- Full multi-Raft millions of groups optimized kernel  
- Byzantine fault tolerance (BFT)  
- Perfect leadership stickiness under flapping networks without trade-offs  
- Cross-group transactions  
- Human-in-the-loop voting  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Safety | Never two leaders same term commit | Inviolable |
| N2 | Election time | Fast failover | p50 < 1–2s; p99 < 5–10s tunable |
| N3 | Heartbeat overhead | Small | Dominates at 1000× groups—batch/aggregate |
| N4 | Durability of term/vote | Survive process crash | Fsync vote record |
| N5 | Availability | Progress if majority alive | Minority partitions block elections (correct) |
| N6 | Scalability | Millions of groups | Sharded coordination / multi-Raft |
| N7 | Multi-region | Survive AZ loss; region loss carefully | Placement policies |
| N8 | Operability | Debuggable elections | Term timelines, reason codes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Bootstrap 3 voters → elect leader term 1 → heartbeats → clients pin leader.  
2. Kill leader → timeout → new election term 2 → new leader → clients refresh.  
3. Leader step-down for upgrade → orderly election.  
4. Learner catches up logs (Raft mode) → promote to voter via reconfig.  
5. Client write with epoch `E` → accepted; old leader with `E-1` rejected.  
6. Quorum loss → no leader; service reads may be stale-allowed mode only if product says so.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Split vote | Randomized timeouts → retry higher term |
| Network partition majority/minority | Majority elects; minority cannot |
| Old leader in minority still thinks leader | Heartbeats fail; on heal, higher term fences |
| Disk lose vote history | Risk double vote → **must** durable vote store |
| Clock jumps | Use timeouts carefully; don’t use absolute wall for safety |
| Flapping leader | Increase timeouts; priority/ sticky; alert |
| Two candidates same term | Voters vote once per term |
| Reconfig remove node mid-term | Joint consensus; never under-quorum |
| GC pause > election timeout | May spurious election—tune or use lease + longer timeout |
| Client caches dead leader | Watch + retry on fence errors |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Election groups | 1K | 10K | 100K | 1M |
| Voters per group | 3–5 | 3–5 | 3–5 | 3–5 (mostly) |
| Nodes (machines) | 30 | 200 | 2K | 20K |
| Elections / hour (steady) | ~10 | ~100 | ~1K | ~10K |
| Heartbeat msgs / s | 5K | 50K | 500K | 5M |
| Leader lookups / s | 20K | 200K | 2M | 20M |
| Avg failover SLO | 2s | 2s | 2–5s | 5–15s (tuned) |
| Regions | 1 | 2 | 3+ | many |
| Admin tenants | 10 | 50 | 200 | 1K |

**What each jump forces:**

- **10×:** Shared node hosts many groups (multi-Raft); batched heartbeats.  
- **100×:** Hierarchical coordinators; lease store shards; watcher fanout optimization.  
- **1,000×:** Group placement service; heartbeat aggregation; region-aware quorums; avoid chatty all-to-all.

### 1.5 Etc. (Constraints & Assumptions)

- Crash-fault model (not Byzantine).  
- Majority quorum (`floor(N/2)+1`).  
- Safety over availability under partition (CP for leadership).  
- Microsoft framing: compare to Service Fabric primary election, Azure Storage partition masters, Cosmos lease blobs, AKS etcd—**principles** matter more than product names.  
- Productize as **LeaderService**: `Acquire`, `Renew`, `Observe`, `Fence(epoch)`.

**Scope statement:**

> Design a productized leader–follower election system providing safe single-leader semantics per group via quorum votes, terms/epochs, heartbeats, and fencing—supporting thousands to millions of independent groups with AZ-aware placement and progressive scaling of heartbeat and watch traffic.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Message classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Heartbeats | 5K/s | 5M/s | Dominant |
| Vote requests (bursts) | low avg, spiky | spiky | Must not melt |
| Leader lookups | 20K/s | 20M/s | Cache + watch |
| Lease renewals (lease mode) | similar to HB | huge | Batch |
| Reconfig ops | rare | rare | Critical path correctness |

**Critical insight:** At 1M groups with 150ms heartbeats and 3 voters:

```text
Naive: each leader → 2 followers every 150ms
1M × 2 / 0.15 ≈ 13.3M heartbeat msgs/s  (table used 5M with longer interval / batching)
→ Must batch, piggyback, or use store-centric leases at extreme scale
```

### 2.2 Election storm math

```text
If correlated failure causes 100K groups to elect simultaneously:
vote RPCs ≈ 100K × (N-1) ≈ 400K bursts
→ jitter election timeouts; stagger; rate-limit elections per node
```

### 2.3 Storage

```text
Per group durable state: currentTerm, votedFor, optional log pointer ~128 B
1M groups × 128 B = 128 MB metadata — tiny
Raft logs for data-groups separate (workload-defined)
Lease mode: epoch + owner + expiry in replicated KV
```

### 2.4 Memory

```text
In-memory leadership table: group_id → (leader, epoch, expiry)
1M × 64 B ≈ 64 MB per full replica of directory — shard directory
Watchers: millions of client watches → pubsub tree / trie by group prefix
```

### 2.5 Failover latency budget

```text
detection ≈ election_timeout (e.g. 1s) + network
campaign ≈ 1 RTT vote (majority)
notify clients ≈ watch push RTT
total ≈ 1–3s typical with aggressive timeouts
Too aggressive → spurious elections under GC/load
```

### 2.6 Critical bottlenecks

1. Heartbeat / renew amplification  
2. Watch storms on mass failover  
3. Correlated election storms  
4. Disk fsync on vote durability under burst  
5. Hot groups metadata shard  
6. WAN voters increasing election RTT  
7. Split-brain if fencing omitted on data plane  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Group (election_id) → Voter set + optional learners
Node roles: Follower | Candidate | Leader
Term / Epoch: monotonic fencing token
Ballot: vote granted for (term, candidate)
Lease: optional soft leadership with TTL
Client handle: {leader_addr, epoch}
```

### 3.2 Options: algorithm family

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. **Raft election + log** | Understandable; strong | Log machinery if only need mutex | Need only singleton lock but implement full SM |
| B. Multi-Paxos | Proven | Harder to explain | Interview clarity suffers |
| C. Lease in etcd/ZooKeeper/Cosmos | Simple product | External dependency; watch care | Treating lease as safe without epoch on writes |
| D. DB row lock / `UPDATE ... RETURNING` | Easy MVP | DB is SPOF/scale limit | 1M groups @ high renew |
| E. Gossip “most votes” without quorum | Soft | Split-brain | Safety-critical primaries |

**Chosen path (productized):**

- **Mode L (Log/Raft):** Full Raft groups for replicated state machines.  
- **Mode M (Mutex/Lease):** Lightweight leader lease via quorum KV (etcd-like / Cosmos lease) returning **epoch**—clients must fence.  
- Shared **directory** service maps `group → leader, epoch`.

### 3.3 Raft election (interview core)

```text
Follower: timeout → become Candidate; term++; vote for self; RequestVote
Voters: grant if term >= currentTerm AND (votedFor empty or same) AND log up-to-date
Majority → Leader; send AppendEntries heartbeats
Higher term seen → step down
```

**Log up-to-date rule:** prevent electing node missing committed entries (Raft Fig. 2).

### 3.4 Fencing (the product requirement)

```text
Every privileged op carries epoch E
Storage/service accepts only if E == current_epoch (or >= with CAS rules)
On new leader: epoch++ (or term becomes epoch)
Old leader writes fail → must re-resolve leadership
```

**Deal-breaker:** Electing a leader but not fencing the data plane (classic split-brain outage).

### 3.5 Options: where election state lives

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Peer-to-peer only | No central | Harder discovery at scale | Clients need directory anyway |
| B. Central coord cluster | Easy watches | Coord capacity | Coord as data plane |
| C. **Hybrid: P2P Raft per group + sharded directory** | Scales | Complexity | Directory without HA |

**Chosen:** Per-group Raft/lease among voters; **sharded Directory** for clients (replicated).

### 3.6 Membership changes

```text
Joint consensus (Raft):
  C_old,new overlapping majorities
  migrate to C_new
  never allow configs that lose quorum mid-flight
```

**Witness / tie-breaker:** lightweight voter with no data for even WAN topologies (use carefully).

### 3.7 Multi-region placement

| Pattern | Pros | Cons |
|---------|------|------|
| 3 voters in 3 AZs one region | Fast | Region loss fatal |
| 5 voters across 2 regions (3+2) | Region resilience | Cross-region RTT |
| 2 + witness in 3rd | Cost | Witness semantics care |

**Deal-breaker:** 2-node “cluster” without witness (split-brain or permanent no-quorum).

### 3.8 Lease mode details (Mode M)

```text
Acquire(group, owner, ttl):
  quorum write if lease expired or same owner renew
  return epoch (incremented on ownership change)

Renew before expiry
If renew fails → stop acting as leader immediately
```

**Safety:** Lease expiry must exceed max clock skew + network delay assumptions—or use loosely synchronized clocks with conservative TTL (Chubby/etcd lessons).

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Safety | Majority quorum | Prevent dual leaders | Plurality without quorum |
| Failover speed | Short timeouts | Fast | Timeouts < GC tails |
| Scale heartbeats | Multi-Raft batch / lease KV | Survive 1M groups | Unique TCP HB per group naive |
| Discovery | Sharded directory + watches | Client simplicity | Clients poll all voters forever |
| Persistence | Fsync vote/term | Crash safety | Memory-only votes |
| Multi-region | Explicit voter topology | RTT honesty | Hide WAN inside “local” timeout |

---

## 4. Architecture Diagram

### 4.1 Productized LeaderService

```text
  Client Apps / Stateful Services
              |
              v
     +------------------+
     | Leader Directory |
     | (sharded, HA)    |  Lookup / Watch / Fence validate API
     +--------+---------+
              |
              v
     +------------------+
     | Election Runtime |
     | on each node     |
     +--------+---------+
              |
     +--------+---------+--------+
     v        v         v        v
  Group A  Group B   Group C   Group ...
  Raft/Lease voters in chosen AZs
```

### 4.2 Raft election sequence

```text
Follower timeout
  → Candidate(term=T)
  → RequestVote to peers
  ← votes majority
  → Leader(term=T)
  → Heartbeats
  → Directory.Update(leader, epoch=T)
  → Watchers notified
```

### 4.3 Split-brain fence

```text
Old Leader (minority)          Storage
   |-- Write(epoch=5) ---------> REJECT (current=6)
New Leader                     Storage
   |-- Write(epoch=6) ---------> ACCEPT
```

### 4.4 Lease acquire / renew

```text
NodeA → QuorumKV: Acquire(g, A, ttl=10s) → epoch=42
NodeA → renew loop every 3s
Network split → renew fails → A stops
NodeB → Acquire → epoch=43
Directory notifies clients
```

### 4.5 Cells / shards of directory

```text
hash(group_id) → Directory Shard (Raft)
Each shard stores leader records for its groups
Watches registered on shard
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Safety invariants (non-negotiable)

1. **Election Safety:** at most one leader per term per group.  
2. **Leader Completeness (Raft):** elected leader has all committed entries (log mode).  
3. **Fence Integrity:** data plane rejects stale epochs.  
4. **Vote durability:** a voter grants ≤1 vote per term across crashes.

#### 5.1.2 Data loss prevention

- Persist `currentTerm` and `votedFor` before granting vote.  
- Leader commits only after quorum log persist (Raft).  
- Directory updates are themselves quorum-replicated.  
- Never accept client mutate without epoch.

#### 5.1.3 Retries & liveness

- Randomized election timeouts to break split votes.  
- Pre-vote (Raft optimization) to avoid disruptive term bumps.  
- Leader stickiness: transfer leadership before shutdown.  
- Exponential backoff on flapping with alert.

#### 5.1.4 Fencing details

| Token | Scope |
|-------|-------|
| `term` / `epoch` | Leadership generation |
| `log index` | Optional compare for state machines |
| `owner_id` | Debug + renew identity |

**Storage integration pattern:**

```text
CAS: if row.epoch == client.epoch then apply; else ESTALE
```

#### 5.1.5 Rate limits

- Max elections/sec per node.  
- Heartbeat coalescing quotas.  
- Watch registration limits per client.  
- Admin force-election rate limited + audited.

#### 5.1.6 Failure modes

| Failure | System behavior |
|---------|-----------------|
| Leader crash | Election → new epoch |
| Minority partition | No leader there; majority continues |
| Quorum loss | Unavailable for writes/elections |
| Disk stall on leader | Step down or fail heartbeats → election |
| Directory shard down | Partial lookup outage; cache TTL may help reads of leadership only with caution |
| Byzantine node | Out of scope; rely on auth |

### 5.2 Scalability

#### 5.2.1 Traffic up/down

- Scale directory shards.  
- Pack many groups per process (multi-Raft).  
- Lengthen heartbeats for non-critical groups.  
- Prefer lease mode for singleton workers that don’t need logs.

#### 5.2.2 Storage

- Vote/term state tiny.  
- Raft logs: snapshot + truncate.  
- Directory: only latest leader record per group (+ short history for debug).

#### 5.2.3 Parallelization

- Groups elect independently (embarrassingly parallel).  
- Avoid global locks.  
- Batch RPCs to same peer covering many groups.

#### 5.2.4 Progressive architecture

| Scale | Design |
|-------|--------|
| 1× | Single Raft cluster or few groups; simple directory |
| 10× | Multi-Raft; shared transports; client watches |
| 100× | Directory shards; pre-vote; placement service |
| 1000× | Heartbeat aggregation, lease KV cells, region-aware topologies, hierarchical leadership (group → cell → region) |

### 5.3 Maintainability

- Explicit state machine diagram in code reviews.  
- Simulation tests (deterministic Raft tests) + Jepsen-style partitions.  
- Trace `term` timelines in UI.  
- Feature flags for pre-vote, joint config.  
- Library SDK: `withFencedEpoch(op)`.  
- Clear Mode L vs Mode M documentation so teams don’t misuse leases.  
- Chaos: inject delay, drop votes, kill leaders, clock skew tests (non-safety clocks).

---

## 6. Wrap-Up

**Deliverable:** A productized election system—Raft/lease groups with durable votes, randomized elections, and **mandatory fencing epochs**—plus a sharded leader directory for discovery/watches, evolving from thousands to millions of groups via multi-Raft, batching, and cells.

**Lines that win interviews:** Safety first; quorum; term fencing; heartbeats dominate scale; never 2-node without witness; directory ≠ source of safety (voters are).

---

## 7. Deeper / Related Interview Questions

### 7.1 Safety vs liveness

**Q: Can we always elect a leader?**  
A: Not under minority partitions—by design (CAP). Prefer no leader over two.

**Q: Why random timeouts?**  
A: Reduce split votes; improve liveness.

### 7.2 Raft vs Paxos vs leases

**Q: When is lease enough?**  
A: Singleton schedulers, partition masters without needing replicated log on the election service itself.

**Q: When full Raft?**  
A: When the group replicates a state machine / config log.

**Q: Is Paxos “better”?**  
A: Equivalent power; Raft usually clearer in interviews.

### 7.3 Fencing & split-brain

**Q: Classic outage pattern?**  
A: Network blip elects new primary; old primary still writes. **Fence tokens** prevent this.

**Q: Is directory update enough?**  
A: No—clients/storage must enforce epoch, not just DNS/directory.

### 7.4 Memory / performance

**Q: 1M heartbeats?**  
A: Don’t do naive per-group sockets. Multi-Raft batching, longer TTL leases, aggregate renew.

**Q: Store all watches in one process?**  
A: Shard; use pubsub topics per directory shard.

### 7.5 Storage & DB

**Q: Leader election via SQL `SELECT FOR UPDATE`?**  
A: MVP for low QPS; fsync/row contention fails at high renew rates; still need fencing version column.

**Q: Cosmos change feed lease (Functions)?**  
A: Similar lease pattern; discuss epoch/ETag as fence.

**Q: etcd vs home-grown?**  
A: etcd embeds Raft; building product may wrap it or implement specialized multi-Raft.

### 7.6 Load balancing & hashing

**Q: Place groups on nodes?**  
A: Consistent hash / placement service with AZ constraints; rebalance throttled.

**Q: Directory shard key?**  
A: `hash(group_id)`.

### 7.7 Algorithms

**Q: Log matching / up-to-date?**  
A: Compare last log term/index so new leader isn’t missing commits.

**Q: Pre-vote?**  
A: Check electability before incrementing term—reduces disruption.

**Q: Leader transfer?**  
A: Send timeout-now to chosen follower for graceful handoff.

**Q: Quorum sizes?**  
A: 3 → tolerate 1 failure; 5 → tolerate 2; cost↑.

### 7.8 Multi-region

**Q: Voters in 3 distant regions?**  
A: Commit/election RTT becomes WAN-bound—often worse than regional + DR.

**Q: RPO/RTO for coordination?**  
A: Coordination system itself needs DR story; cold standby voters.

### 7.9 Clocks

**Q: Do we need synced clocks for Raft safety?**  
A: No for safety. Leases need bounded skew assumptions for liveness/safety of expiry.

**Q: Hybrid logical clocks?**  
A: Optional for event ordering elsewhere; not required for votes.

### 7.10 Comparison to Microsoft systems

**Q: Service Fabric primary failover?**  
A: Similar ideas: replica sets, primary, quorum acknowledgments, failover.

**Q: AKS control plane?**  
A: etcd quorum—same class of problem.

**Q: Azure Storage partition master?**  
A: Specialized leadership + assignment; fencing critical for extent nodes.

### 7.11 Interview traps

| Trap | Pushback |
|------|----------|
| Rank by highest CPU = leader | Not safe |
| 2 nodes active-active | Split-brain |
| Election without durable votes | Double vote after crash |
| Rely on wall clock for safety | Dangerous |
| Directory as only fence | Insufficient |
| Claim BFT with Raft | Wrong model |
| 1M groups × chatty HB ignore math | Won’t scale |

### 7.12 Related deeper topics

**Q: Read quorums / lease reads?**  
A: Leader lease can allow locals reads; must be carefully proven.

**Q: Witness vs learner?**  
A: Witness votes; learner doesn’t. Different purposes.

**Q: Hierarchical leadership?**  
A: Cell leader + per-shard leaders; reduces blast radius.

---

## 8. Appendices

### 8.1 API checklist (LeaderService)

- [ ] `CreateGroup(voters, mode=L|M, timeout_policy)`  
- [ ] `DeleteGroup`  
- [ ] `Lookup(group) → {leader, epoch, mode}`  
- [ ] `Watch(group)` / `WatchPrefix`  
- [ ] `StepDown(group)` (leader or admin)  
- [ ] `Reconfigure(voters)`  
- [ ] `ForceFence(epoch)` / admin inspect  
- [ ] SDK: `RunAsLeader(fn)` renew loop + cancel on loss  

### 8.2 Persistent state sketch

```text
HardState { currentTerm, votedFor, commitIndex? }
group_id, node_id
optional Raft log + snapshots
lease_record { owner, epoch, expiry }  // Mode M
```

### 8.3 Invariants

1. ≤1 leader per `(group, term)`.  
2. Votes durable before reply.  
3. Monotonic terms on nodes.  
4. Data plane accepts only current epoch.  
5. Reconfig never leaves group without possible majority.  
6. Directory epoch matches election epoch (or lags briefly; clients retry on ESTALE).

### 8.4 Progressive scale playbook

| Scale | Must have |
|-------|-----------|
| 1× | Raft or lease+epoch, durable votes, lookup |
| 10× | Multi-Raft, watches, pre-vote, metrics |
| 100× | Directory shards, placement, AZ topology |
| 1000× | HB aggregation, cells, hierarchical leaders |

### 8.5 State machine (Raft roles)

```text
Follower --timeout--> Candidate --majority--> Leader
   ^                     |                      |
   +------ higher term --+---- higher term -----+
Leader --heartbeat fail / step-down--> Follower
```

### 8.6 Timeout tuning guide

```text
heartbeat_interval = H
election_timeout ∈ [3H, 10H] randomized
H large enough >> typical GC/network hiccup
WAN voters → larger H
```

### 8.7 Client SDK pattern

```text
loop:
  info = lookup/watch
  try:
    renew_task = start_renew()
    run_business(fenced_with=info.epoch)
  on ESTALE or renew_fail:
    cancel business; continue
```

### 8.8 Directory schema

```text
leaders(group_id PK, leader_addr, epoch, mode, updated_at, voter_set_hash)
watches stored separately / push channel
```

### 8.9 Placement constraints example

```text
voters: 3
constraints: distinct_az >= 3
prefer: same_region
forbid: all in one rack
```

### 8.10 Observability

| Signal | Why |
|--------|-----|
| `elections_total` | Flapping detector |
| `leader_tenure_seconds` | Stability |
| `heartbeat_fail_total` | Network/disk |
| `estale_total` | Fencing working / client lag |
| `quorum_unavailable` | Pages |

### 8.11 SLO examples

| SLO | Target |
|-----|--------|
| Dual-leader commits | **0** |
| Failover time (regional AZ loss) | p99 < 5s (tuned) |
| Spurious elections / group / day | < 1 steady |
| Lookup p99 | < 10ms in-region |

### 8.12 Interview 60-second summary

> Leadership is a **quorum problem**. Use Raft (or quorum leases) with **durable votes** and **monotonic terms**. Export an **epoch fence** that storage checks on every write. Scale to many groups with multi-Raft and a sharded directory for watches—optimize heartbeats or you’ll drown. Under partitions, prefer **no leader** over two. Productize the SDK so app teams can’t forget fencing.

### 8.13 Related systems map

```text
SDK → Directory (lookup/watch) → Election Runtime (Raft/Lease)
                                      ↓
                              Quorum voters (AZs)
                                      ↓
                              Fenced Data Plane
```

### 8.14 Failure injection plan

1. Kill leader → single new epoch; old fenced.  
2. Partition 1 vs 2 in RF=3 → majority works; minority stalls.  
3. Drop vote messages → split vote → randomized recovery.  
4. Crash after vote grant before reply → restart honors durable vote.  
5. Client uses stale epoch → ESTALE.  
6. Reconfig remove node → joint consensus safety holds.

### 8.15 Glossary

| Term | Meaning |
|------|---------|
| Term/Epoch | Monotonic leadership generation |
| Quorum | Majority of voters |
| ISR-like set | (In log systems) in-sync replicas—related but distinct |
| Pre-vote | Dry-run election |
| Joint consensus | Two-phase membership change |
| Learner | Non-voting replica |
| Witness | Voting node without full data |
| Fencing token | Epoch required on mutate |
| Split-brain | ≥2 active leaders committing |

### 8.16 Mode L vs Mode M chooser

| Need | Mode |
|------|------|
| Replicated config/state machine | L (Raft log) |
| Singleton worker / primary pointer | M (lease + epoch) |
| Partition leader in storage engine | Either; often specialized L |
| Extremely high group count | M with batched renew |

### 8.17 Security checklist

- [ ] mTLS between voters  
- [ ] Node identity attestation  
- [ ] ACL on CreateGroup/Reconfigure  
- [ ] Audit step-down / force  
- [ ] Prevent voter spoofing  

### 8.18 Why odd number of voters?

```text
3 voters → majority 2 → tolerate 1 failure
4 voters → majority 3 → still tolerate 1 (worse cost/benefit)
Prefer odd sizes
```

### 8.19 Interaction with load balancers

- LB must not invent leadership.  
- Clients use directory or redirect from followers (`307` / “not leader”).  
- Sticky LB alone ≠ fencing.

### 8.20 Math cheat sheet

```text
heartbeat_msgs/s ≈ groups × (voters-1) / heartbeat_interval
elections storm msgs ≈ groups_failing × (voters-1)
directory_shards ≈ lookup_qps / qps_per_shard
```

### 8.21 Comparison matrix

| Approach | Safety | Scale | Complexity |
|----------|--------|-------|------------|
| Raft multi-group | High | Med-High | Med |
| Quorum lease KV | High if fenced | High | Med |
| SQL row lock | Medium | Low | Low |
| Gossip soft leader | Low | High | Low |
| BFT | High vs evil | Low | High |

### 8.22 Admin runbook snippets

```text
Flapping: raise election timeout; check disk/GC; pin leadership
Quorum loss: restore voters; never force unclean without data risk acceptance
Stale clients: verify watches; check ESTALE metrics
```

### 8.23 Pseudocode: RequestVote handler

```text
on RequestVote(term, candidateId, lastLogTerm, lastLogIndex):
  if term > currentTerm: step_down(term)
  if term < currentTerm: return false
  if votedFor not in {null, candidateId}: return false
  if not log_up_to_date(lastLogTerm, lastLogIndex): return false
  persist(votedFor=candidateId, currentTerm=term)
  return true
```

### 8.24 Pseudocode: fenced write

```text
on Write(op, epoch):
  if epoch != currentEpoch: return ESTALE
  apply(op)
```

### 8.25 Multi-Raft batching sketch

```text
peer_outbox[peer] = list of (group, AppendEntries/Heartbeat)
flush every H ms or size threshold
reduces syscalls and TLS overhead dramatically
```

### 8.26 Explicit non-goals

- Solving application-level distributed transactions  
- Replacing full service mesh  
- Byzantine / adversarial voters  
- Guaranteeing leadership during majority loss  

### 8.27 Mapping to interview whiteboard flow

1. Clarify safety vs availability.  
2. Draw 3-node Raft.  
3. Show election + heartbeat.  
4. Emphasize fencing on data plane.  
5. Scale talk: many groups, HB math, directory.  
6. Multi-region topology trade-offs.  

### 8.28 Cosmos / Blob lease analogy (Microsoft-friendly)

```text
Acquire lease on blob/item with ETag
Renew
If lost → stop
ETag/epoch → fence
Great for Mode M singleton patterns (e.g. queue processors)
Not a full Raft log replacement
```

### 8.29 When unclean leadership is tempting

Ops may ask to “force leader” without quorum after disaster.  
Treat as **data-loss-accepting** break-glass with audit—never default.

### 8.30 End-to-end reliability test matrix

| Test | Pass criteria |
|------|---------------|
| Kill primary | Exactly one new epoch commits |
| Partition | Minority cannot commit |
| Double start old+new | Only higher epoch writes succeed |
| Vote store crash | No dual vote same term |
| 10K group failover | Storm controlled; SLOs held |

---



### 8.31 Client discovery anti-patterns

- Hardcode leader DNS without epoch.  
- Cache leader forever without watches or TTL.  
- Treat HTTP 200 from old leader as success without epoch check.  
- Load balancer “pick any healthy replica” for writes.

### 8.32 Batch heartbeat frame (example)

```text
HeartbeatFrame {
  sender_node,
  items: [{group_id, term, commit_index, leader_id}]  // up to hundreds
}
Peer applies per-group as if separate heartbeats
```

### 8.33 Cost of cross-region voters (numeric intuition)

```text
RTT local AZ ≈ 1–2ms → election ~timeout + few ms
RTT cross-region ≈ 50–80ms → each vote/append slower
If heartbeat 100ms and RTT 80ms, jitter sensitivity ↑
Often better: 3 AZ same region + async DR, unless region survival required
```

---

*End of leader–follower election system design.*
