# System Design: Model-Weight Distribution

> **Focus areas:** Huge artifact fanout · Chunking & integrity · P2P / tree / CDN tradeoffs · Bandwidth math · Cold start · Canary  
> **Style:** AI-infra distributed systems with progressive scale (10× → 100× → 1,000×)  
> **Company theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — GPU efficiency, reliability, cost  
> **Quality bar:** Correct arithmetic for 100GB–1TB models to hundreds/thousands of GPUs, explicit invariants, resolved topology choice

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

Goal: **bound the problem**—move a huge model weight artifact from durable storage to many GPU workers over constrained links, fast enough that cluster idle time does not dominate rollout cost, correctly enough that no worker serves a corrupt or partial checkpoint.

### 1.0 What this is / is not (say this early)

| Dimension | **This doc (weight distribution)** | **Sibling: File/Model Distribution Service** |
|-----------|------------------------------------|-----------------------------------------------|
| Primary question | How do bits get onto GPUs *fast*? | How do regions *store, version, and cut over*? |
| Hot path | Seed → chunks → workers → GPU memory / local NVMe | Manifest publish → regional replicas → clients |
| Success metric | Time-to-ready (TTR) for N GPUs; abort on bad hash | Integrity, resumability, atomic rollout |
| Topology | P2P / tree / hybrid overlay | CDN + object store + Merkle manifests |
| Canary | First rack/pod validates before full fanout | Blue/green model pointer cutover |

**Scope statement:** Design the **cluster-local (and cross-rack) weight fanout plane**, not the global model registry product (though we integrate with it).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is distributed? | Checkpoint / safetensors / sharded weights 100GB–1TB | Chunked objects; not single HTTP GET |
| F2 | Who receives? | Inference/training GPU workers (100s–1000s) | Overlay or staged tree; avoid single origin melt |
| F3 | Destination? | Local NVMe then mmap / load to HBM; or direct RDMA path Phase 2 | Two-stage: disk then GPU |
| F4 | Integrity? | SHA-256 / BLAKE3 per chunk + full manifest | Fail closed; never load unverified |
| F5 | Resumability? | Yes — flaky workers / preemption | Chunk bitmap + resume |
| F6 | Topology options? | Compare P2P, tree, CDN/origin | Hybrid is usually the answer |
| F7 | Versioning? | Immutable `model_version_id` + manifest | Pin exact bytes for a rollout |
| F8 | Canary? | Validate on small cohort before full blast | Staged fanout gates |
| F9 | Auth? | Cluster IAM; signed manifests | Prevent arbitrary weight injection |
| F10 | Multi-region? | Often same region first; cross-region via regional seeds | Seed hierarchy |
| F11 | Partial shards? | Tensor-parallel ranks need different shards | Manifest lists per-rank objects |
| F12 | Eviction? | Local cache with LRU by version popularity | Disk budget per node |

**MVP functional scope (lock with interviewer):**

1. Publish immutable weight package: chunks + Merkle/manifest + signatures.  
2. Workers discover peers / parents and download missing chunks.  
3. Verify every chunk before mark-ready; assemble local cache.  
4. Report readiness to orchestrator; load into inference runtime.  
5. Canary gate: N% workers green before widen.  
6. Observability: per-chunk progress, bandwidth, hash failures, TTR.  
7. Support at least one topology: **hybrid tree + limited P2P**.

**Out of MVP (explicitly defer):**

- Full BitTorrent tracker UX for researchers  
- Cross-cloud arbitrage of seed placement  
- In-network GPU RDMA weight streaming as primary path  
- Delta/diff updates between adjacent versions (design hooks only)  
- Encrypting every chunk at rest beyond existing disk encryption (mention)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-ready (cold) | Dominates rollout | p50 cold for 200GB → 1k GPUs under 15–30 min with good overlay; defend math |
| N2 | Time-to-ready (warm cache) | Version already local | Seconds (skip download) |
| N3 | Integrity | Zero silent corruption | Chunk + root hash; signed manifest |
| N4 | Origin protection | Object store / seed not melted | Cap origin egress; prefer peer/tree |
| N5 | Fairness | Don’t starve production traffic | QoS / separate fabric or rate limits |
| N6 | Availability | Partial cluster can still roll | Degraded fanout; retry |
| N7 | Cost | Cross-AZ / WAN expensive | Prefer same rack → AZ → region hierarchy |
| N8 | Security | No untrusted weights | Signature verify before load |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. New `model_v42` published → regional seed warm → canary rack downloads → verify → load → canary traffic → widen to all racks via P2P/tree.  
2. Worker restart with warm NVMe cache → verify manifests → ready in seconds.  
3. Tensor-parallel group of 8 → each rank fetches its shard set from local peers first.  
4. Preempted spot node → resumes chunk bitmap; does not re-download completed chunks.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Corrupt chunk from peer | Discard; ban/score peer; refetch from another source |
| Origin throttle / 429 | Back off; rely on peers; escalate seed capacity |
| Disk full on node | Evict cold versions; fail job if cannot free space |
| Manifest signature invalid | Abort rollout; page on-call; never load |
| Split brain two manifests same version | Version IDs immutable; reject ambiguous publish |
| Slow stragglers (last 1%) | Parallel sources; optional seed boost; don’t block canary forever—timeout + replace |
| Cross-AZ stampede | Topology locality scoring; AZ seed first |
| Malicious peer sends garbage | Hash fail; peer reputation; authz on overlay |
| Mid-rollout new version | Workers pin target version; no mixed cutover without orchestrator |
| GPU OOM on load after download | Separate from distribution; report load failure ≠ download failure |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Model size | 200 GB | 200 GB–1 TB | 1–4 TB MoE-style | multi-TB sharded |
| Target GPUs / rollout | 256 | 2,560 | 25,600 | 256,000 |
| Concurrent rollouts | 1–2 | 5–10 | 20–50 | many / continuous |
| Chunk size | 64–256 MB | same | same / tuned | same |
| Peak aggregate ingress needed | see §2 | 10× | 100× | fabric-bound |
| Regional seeds | 1–2 | per AZ | per pod / spine | hierarchical CDN+seed |
| Local NVMe cache / node | 2–4 TB | 4–8 TB | tiered | tiered + shared cache nodes |

**What each jump forces:**

- **10×:** Origin alone dies → must have tree or P2P; canary automation.  
- **100×:** Hierarchical seeds; cross-rack congestion control; dedicated distribution VLAN/QoS.  
- **1,000×:** Global regional replication first (sibling service); cluster fanout is last mile; delta updates matter.

### 1.5 Etc. (Constraints & Assumptions)

- Network: typically 25–100 Gbps NIC per node; rack uplinks oversubscribed (e.g., 3:1–5:1).  
- Storage: node NVMe exists; object store (S3-like) is source of truth.  
- Orchestrator (K8s / custom) decides *who* should run *which* version; we deliver bytes.  
- Training checkpoint broadcast is in-scope variant; inference fleet rollout is primary narrative.  
- Anthropic interview lens: show you can do **bandwidth math**, pick topology under oversubscription, and keep **integrity + canary** non-negotiable.

**Scope statement to repeat back:**

> Design a model-weight distribution plane that moves immutable, chunked, signed 100GB–1TB artifacts to hundreds–thousands of GPU workers over constrained/oversubscribed links using a hybrid seed + tree + P2P approach, with verification, resumability, canary gating, and progressive scale from one cluster to mega-fleet—without melting the origin.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Units and constants

| Quantity | Value |
|----------|-------|
| Model size \(M\) | 200 GB = 200 × 10^9 bytes ≈ 1.6 × 10^12 bits (use 200e9 B) |
| GPUs / workers \(N\) | 1,000 |
| Chunk size \(C\) | 128 MB |
| Chunks | \(200e9 / 128e6 ≈ 1563\) chunks |
| NIC | 25 Gbps ≈ 3.125 GB/s theoretical; practical ~2.0–2.5 GB/s TCP |
| Rack | 32 nodes × 8 GPU = 256 GPU/rack → ~4 racks for 1k GPU |
| Rack uplink | Assume 4×100 Gbps = 400 Gbps shared (example oversubscription) |

### 2.2 Naive single-origin (why it fails)

Origin must push \(M × N = 200 GB × 1000 = 200 TB\) of *logical* transfer if every worker pulls uniquely from origin.

At 25 Gbps origin NIC (one machine):

\[
T ≈ \frac{200 × 10^{12}\ \text{bits}}{25 × 10^9} ≈ 8000\ \text{s} ≈ 2.2\ \text{hours}
\]

(using 200 TB = 200 × 8 × 10^12 bits ≈ 1.6e15 bits → 1.6e15/25e9 = 64,000 s ≈ **17.7 hours** — be careful with TB vs Tebibit).

Cleaner:

- Total bytes from origin if unicast: \(200 × 10^9 × 1000 = 2 × 10^{14}\) bytes = 200 TB.  
- At 10 GB/s sustained origin egress (very fat seed farm): \(2e14 / 1e10 = 20,000\) s ≈ **5.5 hours**.  
- Interview takeaway: **unicast-from-origin does not scale**; need multicast-like efficiency via P2P/tree (each chunk crosses WAN/origin ≈ once per region, then fans out).

### 2.3 Ideal P2P / epidemic lower bound

Once one full copy exists in the cluster, peers exchange. Lower bound roughly:

\[
T_{lb} ≈ \frac{M}{b_{eff}}
\]

for the *last* seeder-limited phase, plus swarm exchange time. With good mesh, cluster TTR often approaches:

\[
T ≈ \frac{M}{b_{node}} × O(\log N)\ \text{or better with tree stages}
\]

Example: \(M=200\) GB, \(b_{node}=2\) GB/s → raw one-node fill ≈ 100 s. With tree depth 3–4 and congestion, **5–15 minutes** cold for well-tuned cluster is a defendable target—not seconds, not hours.

### 2.4 Tree fanout math

Binary tree depth \(\log_2 1000 ≈ 10\). If each parent uploads full model to 2 children sequentially:

\[
T ≈ \log_2 N × \frac{M}{b} ≈ 10 × 100\ \text{s} = 1000\ \text{s} ≈ 17\ \text{min}
\]

With degree-8 tree: depth \(≈ 4\), \(T ≈ 4 × 100 = 400\) s ≈ **7 min** (ignore contention). Contention on uplink makes this optimistic—mention oversubscription.

### 2.5 Bandwidth cost by locality

| Path | Relative cost | Policy |
|------|---------------|--------|
| Same node (already cached) | 0 | Prefer |
| Same rack peer | Low | First peer preference |
| Cross-rack same AZ | Medium | Second |
| Cross-AZ | High | Seed per AZ |
| Cross-region | Highest | Regional seed warm *before* GPU fanout |

### 2.6 Chunk & verification overhead

- 1563 chunks × BLAKE3 ≈ cheap vs network.  
- Manifest size: chunk digests ~32 B × 1563 ≈ 50 KB + metadata — negligible.  
- Verification CPU: at 5 GB/s hash throughput, 200 GB ≈ 40 s/node — overlap with download (hash as you go).

### 2.7 Cold start vs warm

| Scenario | Dominant cost |
|----------|---------------|
| Cold cluster, empty NVMe | Network fanout |
| Warm prior version, new version | Full download (unless delta) |
| Rolling restart same version | Local verify only |
| Spot churn 10%/hour | Continuous repair bandwidth |

Repair bandwidth estimate: 100 nodes/hour × 200 GB × miss_rate. If miss_rate 1.0 cold → 20 TB/h — needs healthy swarm.

### 2.8 Canary sizing

- Canary: 1 rack (256 GPUs) ≈ 25% of 1k? Too big — use **1–5%** or **1 failure domain**.  
- Example: 32 GPUs canary → if TTR canary 8 min + eval 10 min → gate → full fanout 12 min → total ~30 min rollout.

### 2.9 Cost framing (interview gold)

Idle GPU cost during wait: 1000 × H100 × $/hr. If distribution takes 1 hour vs 10 minutes, you burn **6× more idle**. Optimization of TTR is literally money — Anthropic-style cost awareness.

---

## 3. High-Level Design

### 3.1 Design goals (priority order)

1. **Correctness / integrity** — never run unverified weights.  
2. **Bounded origin load** — protect object store and seeds.  
3. **Minimize TTR** under oversubscription.  
4. **Resumability** — flaky nodes.  
5. **Operability** — canary, metrics, abort.  
6. **Cost** — locality-aware transfer.

### 3.2 Core abstraction: Weight Package

```text
WeightPackage {
  model_version_id,  // immutable
  manifest_hash,     // root
  signature,         // publisher key
  chunks: [{chunk_id, offset, length, digest, shard_key?}],
  layout: {tp_size, pp_size, file_map},
  hints: {preferred_region_seeds}
}
```

Workers never trust peer bytes without digests from **signed** manifest.

### 3.3 Component list

| Component | Role |
|-----------|------|
| Model Registry / Publisher | Creates package; signs; writes to object store |
| Regional Seed Service | Warm cache of hot versions; first hop for cluster |
| Distribution Coordinator | Assigns topology roles; tracks readiness; canary gates |
| Node Agent | Downloads, verifies, caches, reports; peer protocol |
| Overlay (tree + P2P) | Chunk exchange with locality scores |
| Orchestrator / Scheduler | Decides desired version per workload; waits on ready |
| Telemetry | TTR, hash fails, origin bytes, peer bytes |

### 3.4 Topology options (tradeoffs)

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **CDN / object store pull** | Simple | Origin melts at N↑; $$ egress | Tiny N or already-warm edge |
| **Tree fanout** | Predictable; easy bandwidth accounting | Root/parent bottlenecks; reparent on failure | Controlled DC fabrics |
| **BitTorrent-like P2P** | Excellent aggregate throughput; origin-light | Complexity; fairness; security scoring | Large homogeneous fleets |
| **Hybrid (recommended)** | Seeds + rack-local P2P + tree across racks | More moving parts | Production default |

**Choice for MVP:** Hybrid —

1. Regional seeds pull once from object store.  
2. Per-rack **parent** (or cache node) pulls from AZ seed.  
3. Intra-rack **P2P swarm** for chunk exchange.  
4. Cross-rack fallback via seed if peer sparse.

### 3.5 Chunking strategy

- Fixed-size chunks 64–256 MB (sweet spot: amortize overhead, allow parallel sockets).  
- Align to safetensors / shard file boundaries when possible (avoid splitting tiny files poorly).  
- Optional **erasure coding** across seeds for repair (Phase 2).  
- **Merkle tree** over chunks → root in signed manifest.

### 3.6 Download state machine (node agent)

```text
PENDING → FETCHING_MANIFEST → VERIFY_MANIFEST_SIG
  → PLAN_CHUNKS → DOWNLOADING (bitmap)
  → VERIFY_CHUNKS → ASSEMBLED → READY
  → LOADING_RUNTIME → IN_SERVICE
Failures: HASH_FAIL, DISK_FULL, TIMEOUT → RETRY / EVICT / DEAD
```

### 3.7 Peer protocol (sketch)

- Announce: `have_bitmap`, `version_id`, `rack_id`, `az`.  
- Request: `want_chunk(chunk_id)`.  
- Tit-for-tat / rarest-first (BitTorrent lessons).  
- Source preference score:

```text
score = w1*same_rack + w2*same_az + w3*peer_rtt^-1 + w4*peer_reputation
       - penalty(origin)
```

### 3.8 Canary & rollout coordination

```text
Publish → Warm seeds → Canary cohort download+load+eval
  → Gate (error rate, latency, hash OK)
  → Widen by failure domain (rack → AZ → fleet)
  → Abort = freeze pointer; do not advance desired_version
```

Distribution service **does not** flip traffic alone; it reports `Ready(version)` to orchestrator / sibling distribution service.

### 3.9 Admission & congestion

- Global token bucket on origin egress.  
- Per-rack uplink budget shared among agents.  
- Separate QoS class for weight traffic vs user inference (or off-peak windows for huge rolls).  
- **Never** let unbounded concurrent full-pulls from seed kill production RPC.

### 3.10 High-level trade-offs summary

| Decision | Options | Choice |
|----------|---------|--------|
| Topology | CDN vs tree vs P2P | Hybrid seed + tree + rack P2P |
| Chunk digest | SHA-256 vs BLAKE3 | BLAKE3 for speed; SHA-256 OK if std |
| Assemble | Sparse files vs concat | Sparse/chunk files + runtime loader |
| Delta updates | Full vs zstd dict / bsdiff | Full MVP; delta Phase 2 |
| Cache | Per-node vs shared rack cache | Per-node + optional rack cache appliance |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+------------------+     +---------------------+     +------------------+
| Model Publisher  |---->| Object Store (S3)   |<----| Regional Seeds   |
| (sign manifest)  |     | chunks + manifests  |     | (warm cache)     |
+------------------+     +----------+----------+     +--------+---------+
                                    ^                         |
                                    | limited egress          | prefer
                                    |                         v
                         +----------+-------------------------+---------+
                         |     Distribution Coordinator (canary/TTR)    |
                         +----------+-------------------------+---------+
                                    | desired_version / ready
                                    v
+-----------+   peer chunks   +-----------+   peer   +-----------+
| Rack A    |<--------------->| Rack B    |<-------->| Rack C    |
| Parent+   |                 | Parent+   |          | Parent+   |
| P2P swarm |                 | P2P swarm |          | P2P swarm |
+-----+-----+                 +-----+-----+          +-----+-----+
      |                             |                      |
      v                             v                      v
  GPU workers                   GPU workers            GPU workers
  (NVMe cache → HBM load)
```

### 4.2 Intra-rack P2P

```text
Seed/AZ  --->  Rack Parent (full or near-full bitmap)
                 |         \
                 v          v
              Worker1 <-> Worker2 <-> Worker3  (rarest-first)
                 \          |          /
                  +---- verify ----+
                         |
                      READY
```

### 4.3 Sequence: cold rollout with canary

```text
Publisher → ObjectStore: PUT chunks+manifest+sig
Coordinator → Seeds: warm(model_v42)
Seeds → ObjectStore: GET (once)
Coordinator → Canary agents: fetch v42
Agents → Peers/Seed: chunks; verify
Agents → Coordinator: Ready
Orchestrator: canary traffic; eval OK
Coordinator → All agents: fetch v42
Agents → Coordinator: Ready(N%)
Orchestrator: full cutover
```

### 4.4 Failure: bad peer chunk

```text
Worker: GET chunk_77 from peer P
Worker: digest mismatch
Worker: strike(P); GET chunk_77 from seed
Worker: digest OK; mark bitmap
Telemetry: hash_fail{peer=P}++
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Immutable `model_version_id`** — bytes never change after publish.  
2. **Signed manifest** verified before any chunk accepted as authoritative.  
3. **No chunk is READY until digest matches.**  
4. **No runtime load until full required shard set verified.**  
5. **Canary gate before fleet widen** (policy-configurable but default on for prod).  
6. **Origin egress budget enforced** — shed to peers, don’t stampede.  
7. **Resume via persistent bitmap** survives agent restart.  
8. **Peer data is untrusted** — only digests from manifest are trust root (plus publisher keys).  
9. **Rollout abort is first-class** — freeze desired version; partial Ready OK.  
10. **Separate download failure from load/OOM failure** in metrics and state.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Seed down | Other seeds / object store with strict rate limit; degrade TTR |
| Parent down | Reparent to adjacent rack parent; bitmap gossip |
| Hash fail rate spike | Pause widen; investigate poison; revoke peer set if needed |
| Disk full | Evict LRU versions ≠ in-use; if still full, mark node unschedulable |
| Coordinator loss | HA lease; agents continue download; gate decisions need leader |
| Clock skew | Don’t use wall clock for integrity; versions are IDs |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× (≤256 GPU) | Pull from 1–2 seeds; light P2P optional |
| 10× | Rack parents + intra-rack swarm mandatory; origin caps |
| 100× | Hierarchical seeds; per-pod cache; QoS; dedicated distribution window |
| 1,000× | Regional replication service owns WAN; cluster is last mile; deltas |

**Straggler mitigation:**

- Parallel multi-source GET for rare chunks.  
- Seed “surge” temporarily for last 5% (bounded).  
- Replace node if past deadline (scheduler).  
- Don’t block entire rack READY on one dead disk — mark node bad.

### 5.3 Maintainability

- Package format versioned (`manifest_schema=2`).  
- Chaos: kill seeds mid-roll; inject corrupt chunks in staging.  
- Metrics (low cardinality): `ttr_seconds`, `origin_bytes`, `peer_bytes`, `hash_failures`, `canary_abort`, `cache_hit_ratio`.  
- Avoid per-chunk_id Prometheus labels.  
- Runbooks: abort rollout, rebuild seed, revoke signing key (rare).

### 5.4 Security deep dive

| Threat | Control |
|--------|---------|
| Malicious weights | Offline signed manifests; dual control publish |
| Peer poisoning | Hash + reputation + optional mTLS node identity |
| Confused deputy registry | IAM on publish; environment separation |
| Rollback to vulnerable | Orchestrator policy; distribution will serve old if asked — policy elsewhere |
| Supply chain | Provenance metadata in manifest (build id, training job) |

### 5.5 GPU efficiency angle

- Overlap: download chunk \(i+1\) while verifying \(i\) while optionally staging to GPU if runtime supports.  
- Prefer finishing **local NVMe** before claiming GPU exclusively for load — reduces expensive GPU idle with empty weights.  
- For TP groups: schedule distribution affinity so ranks that share shards co-locate in rack (placement hint to scheduler).

### 5.6 Comparison vignette (say in interview)

> “Pure CDN pull is fine for 10 nodes. At 1000 GPUs and 200GB, unicast origin cost is hundreds of terabytes. I’d warm regional seeds once, tree across racks to respect uplinks, and BitTorrent-style rarest-first inside the rack. Canary one failure domain, verify BLAKE3, then widen. Integrity and origin protection beat shaving one minute of TTR.”

### 5.7 Delta updates (Phase 2 hook)

- Between `v41` and `v42`, compute chunk-level diff (identical chunks reuse digest).  
- Content-defined chunking (CDC) improves hit rate for fine-tuned variants.  
- Tradeoff: harder caching; worth it at 1,000× continuous rollout.

### 5.8 Training checkpoint broadcast variant

Same plane: rank 0 writes shards → package → fanout to other ranks / eval fleet. Latency SLO tighter; often **tree over NCCL fabric** if available — mention as alternate transport under same manifest/integrity layer.

### 5.9 Consistency model

- **Strong** for what a worker runs: pinned version + verified bytes.  
- **Eventual** for fleet diversity during rollout (mixed versions expected until cutover).  
- Coordinator exposes `ReadyCount(version)` — never claim global consistency until orchestrator flips.

### 5.10 Operability dashboards

1. Rollout progress heatmap by rack.  
2. Origin vs peer traffic ratio (health of overlay).  
3. Hash failure spike alert.  
4. TTR histogram canary vs fleet.  
5. Disk pressure / eviction rate.

---

## 6. Wrap-Up

### 6.1 What we designed

A **model-weight distribution plane** for Anthropic-scale GPU fleets: immutable chunked signed packages, regional seeds, hybrid **tree + rack-local P2P**, strict verification, resumable bitmaps, canary-gated widen, and progressive scaling that keeps origin egress and rack uplinks from melting—so cold TTR stays in minutes, not hours.

### 6.2 Key decisions worth defending

1. **Hybrid topology**, not pure CDN or pure P2P.  
2. **Signed manifest + per-chunk digests** as trust root.  
3. **Locality-aware source selection** (rack → AZ → region).  
4. **Origin egress budgets** as first-class.  
5. **Canary by failure domain** before blast radius expand.  
6. **Resume bitmaps** for preemptible / flaky nodes.  
7. **Separate Ready vs In-Service** (download ≠ loaded ≠ serving).  
8. **Bandwidth math before architecture religion.**  
9. **Delta updates deferred** until continuous rollout demands.  
10. **Idle-GPU cost** as the business case for TTR.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Overlay complexity bugs | Start tree-only; add P2P intra-rack |
| Uplink congestion vs inference | QoS / off-peak / dedicated NIC queues |
| Huge MoE multi-TB | Shard-aware partial fetch per rank |
| Signing key compromise | Key rotation + publish freeze |
| Cross-region | Lean on sibling regional distribution service |

### 6.4 One-minute closer

> We treat weights like a **content-addressed torrent with a control plane**: seed once, fan out with locality, verify everything, canary, then widen—because at 200GB × 1000 GPUs, topology is the product.

---

## 7. Deeper / Related Interview Questions

### 7.1 Warm-ups

1. Why not `aws s3 cp` on every node?  
2. Chunk size tradeoffs (4MB vs 1GB)?  
3. SHA-256 vs BLAKE3?  
4. What does canary mean if loads are correct but model quality regresses?

### 7.2 Bandwidth & topology

5. Recalculate TTR for 1TB model, 10k GPUs, 100 Gbps NICs, 4:1 oversubscription.  
6. When is IP multicast viable in your DC?  
7. How do you prevent cross-AZ peer preference from blowing the bill?  
8. Tree reparenting algorithm when rack parent dies mid-transfer?

### 7.3 Correctness & security

9. Peer sends correct length, wrong bytes — walk the detection path.  
10. Can an attacker who compromised one worker poison others?  
11. How do you revoke a bad published version already half-downloaded?  
12. Should verification be streaming or end-of-file?

### 7.4 Product / EM angle

13. How do you prioritize engineering: shave TTR 20% vs harden canary?  
14. SLIs/SLOs you’d put on the scorecard.  
15. How this interfaces with blue/green inference cutover (sibling doc).  
16. Mentoring: junior proposes “NFS mount the checkpoint”—coaching plan.

### 7.5 Stretch

17. Design CDC delta between adjacent finetunes.  
18. RDMA / GPUDirect path under the same manifest.  
19. Multi-tenant isolation when two orgs share a cluster.  
20. Distribute tokenizer + adapter LoRA packs in the same plane.

### 7.6 Sample strong answers (brief)

**Q5 sketch:** 1TB @ 2GB/s node ≈ 500s base; depth-4 degree-8 tree ≈ 2000s optimistic; with P2P rack swarm closer to 500–900s plus seed warm; call **15–30 min** with contention, and insist on hierarchical seeds so WAN isn’t in the critical path for every node.

**Q10 sketch:** Without signed manifests, yes. With signed manifests and digest checks, poisoned bytes fail closed; attacker can only DoS bandwidth, not flip model bits—unless they steal signing keys (separate HSM / offline keys discussion).

---

## Appendix A: Glossary

| Term | Meaning |
|------|---------|
| TTR | Time to Ready — bytes verified on node |
| Swarm | P2P set sharing a version |
| Seed | Authoritative full (or fat) cache |
| Manifest | Chunk list + digests + metadata |
| Failure domain | Rack/AZ unit for canary widen |
| Bitmap | Chunk completion map for resume |

## Appendix B: Example manifest (illustrative)

```json
{
  "model_version_id": "claude-x-2026-08-05.r42",
  "schema": 2,
  "root_hash": "blake3:...",
  "chunk_size": 134217728,
  "chunks": [
    {"i": 0, "digest": "blake3:...", "shard": "tp0"},
    {"i": 1, "digest": "blake3:...", "shard": "tp0"}
  ],
  "signature": "ed25519:..."
}
```

## Appendix C: Pseudo-code node agent loop

```text
on desired(version):
  m = fetch_manifest(version)
  verify_sig(m) or abort
  bitmap = load_bitmap(version) or zeros
  while not complete(bitmap):
    c = select_rarest_missing(bitmap)
    src = pick_source(c)  # rack peer > az seed > origin
    bytes = get(src, c)
    if hash(bytes) != m.digest[c]: punish(src); continue
    write_chunk(c, bytes); bitmap[c]=1; persist(bitmap)
  fsync(); mark READY(version)
```

## Appendix D: Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Signed chunks, seed pull, verify |
| 10× | Rack P2P, origin cap, canary |
| 100× | Hierarchy, QoS, straggler playbooks |
| 1,000× | Regional warm, deltas, multi-cluster coordinator federation |

## Appendix E: Interview whiteboard outline (15 min)

1. Requirements: size N, integrity, canary (2 min)  
2. Math: why origin dies (3 min)  
3. Hybrid topology diagram (4 min)  
4. State machine + invariants (3 min)  
5. Scale jumps / risks (3 min)

## Appendix F: Related Anthropic themes

- GPU efficiency: don’t idle accelerators on dumb distribution.  
- Reliability: hash fail closed.  
- Safety adjacent: only signed artifacts become production brains.  
- Cost: locality and TTR.

## Appendix G: Metrics formulas

```text
cache_hit_ratio = local_satisfied_chunks / total_chunks_needed
origin_ratio = origin_bytes / (origin_bytes + peer_bytes)   # lower is healthier swarm
canary_success = canary_ready_and_eval_pass
rollout_efficiency = ideal_lb_ttr / observed_p95_ttr
```

## Appendix H: Common mistakes

1. Forgetting rack uplink oversubscription in math.  
2. Trusting HTTP 200 without hashing.  
3. Global barrier “all 1000 ready” before any canary traffic.  
4. Mixing desired version flips without pinning.  
5. Per-chunk metrics cardinality explosion.  
6. Assuming multicast exists.  
7. Ignoring disk eviction storms when three versions coexist.

## Appendix I: Integration APIs (sketch)

```text
POST /packages {manifest} -> version_id
POST /seeds/warm {version_id, region}
GET  /status/{version_id} -> {ready_nodes, ttr_p50, origin_bytes}
POST /rollouts {version_id, canary_policy}
POST /rollouts/{id}/widen
POST /rollouts/{id}/abort
```

Agent gRPC: `Fetch(version_id)`, `GetBitmap`, `OfferChunk`, `ReportReady`.

## Appendix J: Worked numeric table (200GB, 1024 GPUs)

| Strategy | Origin TB | Approx TTR | Notes |
|----------|-----------|------------|-------|
| Naive unicast | ~200 | hours | Fail |
| Single seed + unicast | ~200 | hours | Fail |
| Tree degree 8 | ~0.2–2 | ~10–20 min | Parent risk |
| Rack P2P + AZ seed | ~0.2–1 | ~5–15 min | Recommended |
| Ideal infinite fabric | ~0.2 | ~2–5 min | Unrealistic uplinks |

*(Origin TB ≈ copies into region × size; swarm exchanges don’t count as origin.)*

## Appendix K: Canary policy example

```text
canary:
  domains: [rack-a1]
  min_ready_ratio: 0.95
  max_hash_fail: 0
  eval_job: smoke-infer-v2
  eval_timeout_min: 15
widen:
  batch_domains: 2 racks at a time
  pause_on_alert: [p99_latency, critical_safety]
abort:
  on: eval_fail OR hash_fail_rate > 0
  action: freeze desired_version; ticket
```

## Appendix L: Disk budget policy

```text
budget_nvme = 4TB
reserve_for_runtime = 0.5TB
evict_order = LRU among versions not in {desired, previous, canary}
never_evict = currently_loaded_version
```

## Appendix M: Why Anthropic asks this

They want evidence you can:

- Do **back-of-envelope networking**.  
- Choose **overlays** under real DC constraints.  
- Treat **integrity** as non-negotiable for model bytes.  
- Connect **rollout mechanics** to GPU cost.  
- Stay calm in unfamiliar “AI infra” packaging of classic fanout problems.

## Appendix N: Metrics formulas

```text
cache_hit_ratio = local_satisfied_chunks / total_chunks_needed
origin_ratio = origin_bytes / (origin_bytes + peer_bytes)   # lower is healthier swarm
canary_success = canary_ready_and_eval_pass
rollout_efficiency = ideal_lb_ttr / observed_p95_ttr
```

## Appendix O: Common mistakes

1. Forgetting rack uplink oversubscription in math.  
2. Trusting HTTP 200 without hashing.  
3. Global barrier “all 1000 ready” before any canary traffic.  
4. Mixing desired version flips without pinning.  
5. Per-chunk metrics cardinality explosion.  
6. Assuming multicast exists.  
7. Ignoring disk eviction storms when three versions coexist.

## Appendix P: Integration APIs (sketch)

```text
POST /packages {manifest} -> version_id
POST /seeds/warm {version_id, region}
GET  /status/{version_id} -> {ready_nodes, ttr_p50, origin_bytes}
POST /rollouts {version_id, canary_policy}
POST /rollouts/{id}/widen
POST /rollouts/{id}/abort
```

Agent gRPC: `Fetch(version_id)`, `GetBitmap`, `OfferChunk`, `ReportReady`.

## Appendix Q: Interview whiteboard outline (15 min)

1. Requirements: size N, integrity, canary (2 min)  
2. Math: why origin dies (3 min)  
3. Hybrid topology diagram (4 min)  
4. State machine + invariants (3 min)  
5. Scale jumps / risks (3 min)

## Appendix R: Related Anthropic themes

- GPU efficiency: don’t idle accelerators on dumb distribution.  
- Reliability: hash fail closed.  
- Safety adjacent: only signed artifacts become production brains.  
- Cost: locality and TTR.

## Appendix S: Pseudo-code node agent loop

```text
on desired(version):
  m = fetch_manifest(version)
  verify_sig(m) or abort
  bitmap = load_bitmap(version) or zeros
  while not complete(bitmap):
    c = select_rarest_missing(bitmap)
    src = pick_source(c)  # rack peer > az seed > origin
    bytes = get(src, c)
    if hash(bytes) != m.digest[c]: punish(src); continue
    write_chunk(c, bytes); bitmap[c]=1; persist(bitmap)
  fsync(); mark READY(version)
```

## Appendix T: QoS & traffic classes

| Class | Priority | Notes |
|-------|----------|-------|
| Inference RPC | Highest | User-facing tokens |
| Weight canary | High | Small cohort; bounded |
| Weight fleet | Medium | Yield to inference |
| Soft scrape / research pull | Low | Best effort |

Implement with fq_codel / DC QoS / separate VXLAN where available. Interview point: **distribution must not self-DoS serving**.

## Appendix U: Multi-SKU / heterogeneous fleets

- Different GPU generations may need different compiled kernels but **same weight bytes** (or different quantization packs).  
- Manifest can list `variant: fp8-h100` vs `bf16-a100` as separate packages sharing channel family.  
- Don’t P2P across incompatible variants (digest sets differ).

## Appendix V: Security checklist for publish path

1. Offline or HSM-backed signing keys.  
2. Dual approval for prod package promote (may live in sibling service).  
3. mTLS for agent overlay.  
4. Escape hatch: emergency revoke by version deny-list in coordinator.  
5. Red-team: compromised worker trying to seed bad chunks — must fail hash.

---

*End of Model-Weight Distribution system design.*