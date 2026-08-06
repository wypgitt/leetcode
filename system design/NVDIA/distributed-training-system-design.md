# System Design: Distributed Training for Very Large Models

> **Focus areas:** Data / tensor / pipeline / expert parallelism · NCCL collectives · Checkpointing · Elastic / fault recovery · Stragglers · Topology (NVLink / InfiniBand) · Gradient sync · Mixed precision  
> **Style:** NVIDIA-flavored ML systems interview — progressive scale on GPUs / nodes / model size / tokens (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic on FLOPs / bandwidth / checkpoint I/O, split control-plane vs collective traffic, honest failure & restart semantics, resolved ownership of job lifecycle vs collective membership

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

Goal: **bound the training system**—what “distributed training” means (single job vs platform), which parallelisms are in scope, and which failure / restart semantics are non-negotiable for multi-week LLM runs.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits jobs? | Research + production training teams; multi-tenant cluster | Job API + gang placement + project quotas |
| F2 | Model class? | Dense transformers + MoE; 7B → 100B+ params | Support DP/TP/PP/(EP); composable parallel plans |
| F3 | Framework? | PyTorch + NVIDIA stack (NCCL, CUDA, optionally Megatron/NeMo) | Process group bootstrap; NCCL as collective SoT |
| F4 | Parallelism? | Data, tensor, pipeline, expert; combinations | Planner chooses 3D/4D mesh from topology + memory |
| F5 | Data pipeline? | Tokenized shards on object/parallel FS; streaming | Decouple I/O from step; shuffle + resume offsets |
| F6 | Checkpointing? | Periodic async/sync checkpoints; resume after fail | Consistent global step; sharded state; atomic commit |
| F7 | Elasticity? | Prefer elastic shrink/grow; at least restart-from-ckpt | Membership epochs; replan mesh or fail→restart |
| F8 | Fault model? | Node/GPU/NIC death, NCCL hang, stragglers | Health watchdog; timeout; replace or restart job |
| F9 | Observability? | Loss, MFU, step time, NCCL time, GPU util, NVLink/IB | Telemetry with cardinality control |
| F10 | Multi-job? | Many concurrent train jobs; gang scheduling assumed | Interface to GPU resource manager (separate design) |
| F11 | Precision? | BF16/FP16 + FP32 master weights; optional FP8 | Mixed-precision pipeline; overflow/loss-scale policy |
| F12 | Topology? | Prefer NVLink domains + IB fat-tree / rail-optimized | Topology-aware rank placement |

**MVP functional scope (lock with interviewer):**

1. Submit training job: image, entrypoint, GPU count, parallel plan (or auto), dataset URI, hyperparams.  
2. **Gang-start** all ranks; bootstrap torch/NCCL process group with rank↔GPU map.  
3. Support **DP + TP + PP** (expert parallelism as stretch).  
4. Synchronous training step with NCCL AllReduce / AllGather / ReduceScatter / P2P for PP.  
5. Periodic **sharded checkpoint** to durable store; resume from last committed step.  
6. On rank failure: detect → tear down → **restart from checkpoint** (elastic optional).  
7. Metrics: step time, MFU, collective time, checkpoint latency; structured job timeline.

**Out of MVP:**

- Fully automatic 4D search over all parallel plans every failure  
- Cross-region training over WAN (design as anti-pattern unless forced)  
- Perfect zero-waste straggler elimination  
- User-defined custom collectives without NCCL  
- Spot-market preemption UX (hook via resource manager)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Step time predictability | Tight for large jobs | p99 step < 1.5× p50 when healthy |
| N2 | Checkpoint RPO | Lose at most one interval | Interval 10–30 min typical; tunable |
| N3 | Restart RTO | Minutes, not hours | Detect <60s; restart cold start <5–15 min for mid-size |
| N4 | Correctness | Bit-reproducible optional; numeric stable required | Deterministic seed + same mesh for replay; BF16 variance OK |
| N5 | Utilization | High MFU under topology fit | Aim 40–60%+ MFU for well-tuned LLM jobs (honest band) |
| N6 | Availability | Job survives single node loss via restart | Control plane 99.9%; job progress via ckpt |
| N7 | Multi-tenancy | No cross-job NCCL / GPU theft | Isolated process groups; device leases |
| N8 | Scale | See progressive table | Plan for 8 → 8K+ GPUs per job |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User submits 64×H100 job with TP=8, PP=2, DP=4 → gang placed on 8 nodes same IB domain → NCCL init → train → checkpoint every N steps → SUCCEEDED.  
2. Job hits max steps / token budget → final checkpoint → exit 0.  
3. Single GPU XID error → watchdog kills job → auto-restart from last ckpt on fresh gang.  
4. User pauses → cooperative drain at step boundary → checkpoint → release GPUs.  
5. Resume with same mesh → load sharded ckpt → continue global_step.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| One rank OOMs | Fail job (don’t limp); log allocator stats; suggest smaller microbatch / more TP/PP |
| NCCL collective hang | Watchdog timeout > expected step; abort + restart; dump flight recorder if available |
| Straggler rank (thermal / noisy neighbor) | Detect slow step contributor; optionally migrate or restart; don’t wait forever |
| Checkpoint upload partial | Never mark committed until manifest + all shards durable; readers see last good |
| Two restarts race | Job epoch / generation fences old ranks |
| Dataset shard missing mid-run | Fail with clear error; don’t silently skip unless policy |
| PP bubble dominates | Replan microbatches / stages; expose idle time metric |
| MoE expert imbalance | Capacity factor / aux loss; EP AllToAll hotspot alerts |
| Preemption mid-step | Grace → checkpoint if possible; else restart loses interval (RPO) |
| Topology split across slow links | Admission should prefer reject/wait over bad placement for huge jobs |

### 1.4 Scales (Progressive)

Progressive axes: **GPUs / nodes / model params / tokens processed**.

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPUs / job | 64 | 640 | 6,400 | 64,000 |
| Nodes (8-GPU) | 8 | 80 | 800 | 8,000 |
| Model params | 7B | 70B | ~700B | multi-trillion (MoE) |
| TP degree | 8 | 8 | 8–16 | 8–16 |
| PP degree | 1–2 | 4–8 | 8–16 | 16–64 |
| DP degree | 8 | 80 | ~400+ | thousands |
| Global batch (tokens) | ~1M | ~4–8M | ~16–32M | ~64M+ |
| Checkpoint size | ~14–30 GB | ~140–300 GB | ~1–3 TB | ~10 TB+ |
| Checkpoint interval | 15 min | 15 min | 10–20 min | 10–30 min |
| Concurrent train jobs (cluster) | 20 | 50 | 100 | 200+ |
| Cluster GPUs (shared) | 1,000 | 10,000 | 100,000 | 1,000,000 |
| Tokens / day (fleet) | 1T | 10T | 100T | 1P |

**What each jump forces:**

- **10×:** Multi-node IB first-class; async checkpoint pipeline; better straggler detection.  
- **100×:** Hierarchical collectives; sharded ckpt parallel I/O; topology DB mandatory; elastic or fast restart.  
- **1,000×:** Multidimensional parallelism planner; checkpoint hierarchy (local→DFS→object); fault domains; membership epochs; telemetry cardinality controls.

### 1.5 Etc. (Constraints & Assumptions)

- GPUs are **NVIDIA** data-center class (A100/H100/H200/B200); NVLink within node; IB/RoCE between nodes.  
- Training is **synchronous** SGD/Adam-style unless interviewer asks for async (usually don’t).  
- **Gang scheduling** provided by cluster GPU resource manager; this design owns the **training runtime + orchestration**.  
- Checkpoints land on parallel FS or object storage with sufficient aggregate bandwidth.  
- We do **not** invent a new collective library—NCCL (or CUDA-aware MPI over NCCL) is the workhorse.

**Scope statement:**

> Design a distributed training platform for very large NVIDIA-GPU models: compose data/tensor/pipeline/(expert) parallelism over NVLink/IB topology, run NCCL collectives safely, checkpoint and restart under node failure, mitigate stragglers, and scale jobs from tens to tens of thousands of GPUs with honest MFU and I/O arithmetic.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline (64 GPU) | 1,000× job | Notes |
|-------|-------------------|------------|-------|
| **Training step compute** | Dominates GPU time | Dominates | FLOPs bound if well tuned |
| **Collective traffic** | AllReduce grads DP | Huge AllGather/RS + PP P2P | Can dominate step time |
| **Data loader I/O** | Token shards | Multi-TB/day | Must overlap with compute |
| **Checkpoint I/O** | Periodic bursts | Multi-TB bursts | Separate from step path |
| **Control plane** | Heartbeats, metrics | Rank×metric cardinality | Easy to melt observability |
| **Job submit/restart** | Rare | Still rare vs steps | Not the throughput bottleneck |

**Deal-breaker:** treating “cluster QPS” like a web service; training is **step-oriented**, not request QPS.

### 2.2 Model memory arithmetic

```text
Params (FP16/BF16): 7B × 2 B = 14 GB
Adam states (FP32 m,v): 7B × 4 B × 2 = 56 GB
FP32 master weights: 7B × 4 B = 28 GB
Gradients (BF16): ~14 GB
Activations: depend on batch, seq, recompute

Rough optimizer+params+grads >> single GPU → must shard (ZeRO / TP / PP)
```

Rule of thumb interview line:

```text
“Dense model bytes on disk ≈ 2×params (BF16) for weights-only ckpt;
 full training state often 8–16× param bytes with Adam + masters.”
```

### 2.3 FLOPs & step time (order-of-magnitude)

```text
Transformer training ~ 6 × N_params × N_tokens_per_step  FLOPs (dense, rough)

Example: 70B params, 1M tokens/step:
6 × 70e9 × 1e6 = 4.2e17 FLOPs

H100 ~989 TFLOPS sparse / ~500–700 TFLOP/s usable BF16 train (be honest: use ~400 TFLOP/s effective)
64 GPUs × 400e12 = 2.56e16 FLOP/s

Ideal step ≈ 4.2e17 / 2.56e16 ≈ 16.4 s  (compute only)
With collectives/overhead MFU 50% → ~33 s/step
```

**Unit check:** Always separate **peak brochure TFLOPS** from **achieved**.

### 2.4 Gradient sync (DP AllReduce) bandwidth

```text
Grad size BF16 ≈ 2 × params
70B → 140 GB of grad payload “logical”
Ring AllReduce volume per GPU ≈ 2 × (N-1)/N × grad_size / N_gpus_in_group
  ≈ 2 × grad_size / N  (approx for large N)

For DP=64 on 70B fully replicated (pathological):
  per GPU ~ 2×140GB/64 ≈ 4.4 GB payload movement class
At 400 GB/s NVLink OK in-node; across IB 200–400 Gb/s/nic → tens of ms to seconds

Reality: you won’t DP-AllReduce full 70B—you combine TP/PP/FSDP/ZeRO to shrink.
```

Interview move: **show why 3D parallelism exists**—communication volume vs memory.

### 2.5 Pipeline bubbles

```text
PP stages = P, microbatches = M
Bubble fraction ≈ (P-1) / (M + P - 1)   (1F1B-style intuition)

P=8, M=8  → bubble ≈ 7/15 ≈ 47%  (bad)
P=8, M=32 → bubble ≈ 7/39 ≈ 18%
P=8, M=64 → bubble ≈ 7/71 ≈ 10%
```

Trade-off: more microbatches → less bubble, more activation memory / latency to optimizer step.

### 2.6 Checkpoint I/O

```text
State 2 TB, interval 15 min
Parallel write with 64 ranks × 5 GB/s aggregate effective → 400 GB/s
2 TB / 400 GB/s = 5 s ideal; reality 30–120 s with FS overhead

At 100×: 20 TB state → need hierarchical ckpt (local NVMe → burst → object)
Async ckpt: copy on write / staged; critical path = consistency barrier + metadata commit
```

### 2.7 Telemetry cardinality trap

```text
64k GPUs × 50 metrics × 1 Hz = 3.2M points/s
× 8 B ≈ 25 MB/s raw—but tag explosion (job,rank,gpu,uuid) melts TSDB

Must: aggregate at node → job → fleet; exemplars for slow ranks; high-card labels sampled
```

### 2.8 Critical bottlenecks (rank ordered)

1. **Bad topology placement** (TP across IB instead of NVLink)  
2. **Collective imbalance / stragglers** stretching every step  
3. **Checkpoint I/O storms** stalling or destabilizing FS  
4. **Activation memory** forcing tiny batches → poor MFU  
5. **Control-plane / metric cardinality** outages mistaken for training bugs  
6. **Slow restart** burning GPU-hours after trivial failures  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
TrainingJob     → user-facing unit (image, data, hparams, resources)
ParallelPlan    → {DP, TP, PP, EP, ZeRO stage} + mesh assignment
ProgressGroup   → NCCL/torch group world + subgroups (tp, dp, pp, ep)
RankAssignment  → rank → {node, gpu, nic, nvlink_domain, ib_leaf}
Trainer Runtime → step loop: forward/backward/collectives/optim
Checkpointer    → sharded state + manifest commit protocol
Health Monitor  → per-rank liveness, step progress, XID/NCCL errors
Job Controller  → start/stop/restart; epoch fencing; interacts with GPU RM
```

**Job states:**

```text
ADMITTED → PROVISIONING → BOOTSTRAP → RUNNING → CHECKPOINTING
                ↑                         │
                +------ RESTARTING <------+---- FAILED
                                          +---- SUCCEEDED
                                          +---- CANCELLED
```

### 3.2 Parallelism options & trade-offs

| Strategy | What is split | Comm pattern | Good when | Deal-breaker misuse |
|----------|---------------|--------------|-----------|---------------------|
| **DP** | Batch | AllReduce / RS+AG grads | Model fits per rank | Huge model replicated → OOM |
| **TP** (Megatron-style) | Layer tensors | AllReduce/AllGather in layer | Hidden size large; NVLink | TP across slow IB |
| **PP** | Layers by stage | P2P activations | Depth too large for 1 GPU | Tiny M → huge bubble |
| **EP** (MoE) | Experts | AllToAll tokens | Sparse MoE models | Imbalance melts EP group |
| **ZeRO/FSDP** | Opt state / params | AG params, RS grads | Mem pressure w/ DP | Over-shard → comm bound |

**Composed mesh (typical LLM):**

```text
world = DP × PP × TP (× EP)
Prefer: TP within NVLink domain (same node / HGX)
        PP across nodes with good IB
        DP outermost
```

### 3.3 Ownership & invariants

| Concern | Owner |
|---------|-------|
| Who gets which GPUs | GPU resource manager (gang bind) |
| Rank↔device map | Job controller + RM allocation |
| Collective membership | Training runtime (NCCL) under job epoch |
| Model step correctness | Trainer (optimizer + loss scale) |
| Durable progress | Checkpointer manifest |
| Failure detection | Health monitor + RM heartbeats |
| When to restart vs elastic replan | Job controller policy |

**Invariants:**

1. **No partial gang run:** all ranks up before first collective.  
2. **Single job epoch** active for a world; stale ranks fenced.  
3. **Checkpoint commit atomic:** readers only see complete manifests.  
4. **global_step monotonic** across restarts.  
5. **One writer** to job desired-state in controller.

### 3.4 Process bootstrap

```text
1. RM binds N GPUs; returns hostfile / device list
2. Controller launches N processes (or pods) with:
   RANK, LOCAL_RANK, WORLD_SIZE, MASTER_ADDR, JOB_EPOCH
3. Ranks rendezvous (TCP store / etcd)
4. Build process groups: world, tp, dp, pp, ep
5. NCCL init with topology-aware device order
6. Barrier → RUNNING
```

**Deal-breaker:** starting collectives before all ranks joined → hangs that look like “NCCL bugs.”

### 3.5 Training step (logical)

```text
for step in range(start, max):
  batch = next(data_loader)            # DP shard
  with autocast(bf16):
    loss = forward_pipeline(batch)     # PP schedule + TP ops
  backward_pipeline(loss)              # produce grads
  clip / unscale
  dp_synchronize_grads()               # RS/AR as plan dictates
  optimizer.step(); optimizer.zero_grad()
  if step % ckpt_every == 0:
    checkpointer.save(step)
  emit_metrics(step)
```

### 3.6 Gradient sync & mixed precision

| Topic | Design choice |
|-------|---------------|
| Precision | BF16 compute preferred on Ampere+; FP32 master weights |
| Loss scaling | Dynamic for FP16; often unnecessary for BF16 |
| Grad sync dtype | BF16/FP16 grads; accumulate carefully |
| Bucketization | NCCL bucketing to overlap reverse-mode with AllReduce |
| ZeRO | Stage-1/2/3 as memory demands |

**Overlap pattern:** backward of layer *i* overlaps with grad reduce of layer *i+1* (where legal).

### 3.7 Checkpoint protocol

```text
Options:
  A. Sync barrier → every rank writes shard → rank0 writes MANIFEST.tmp → rename MANIFEST
  B. Async: snapshot refs → background upload → commit when durable

Commit condition:
  all shard checksums present + manifest version = global_step
Readers:
  load highest committed manifest ≤ resume_step
```

**Sharding keys:** by TP/PP rank and ZeRO shard id—never assume single-file pickle at scale.

### 3.8 Fault recovery strategies

| Strategy | Pros | Cons | When |
|----------|------|------|------|
| **Fail & restart from ckpt** | Simple, correct | Lose interval; cold start | MVP default |
| **Elastic shrink** | Keep progress | Hard: regroup NCCL, replan batch | Mid-scale stretch |
| **Spare hot standby** | Fast replace | Waste GPUs | Critical deadline jobs |
| **Local checkpoint + peer restart** | Faster RTO | Complexity | 100×+ |

**MVP pick:** fail → release gang → re-acquire → resume ckpt. Mention elastic as evolution.

### 3.9 Straggler mitigation

```text
Detect: per-rank step_time_local vs median
Causes: thermal throttle, background GC, noisy NIC, imbalanced MoE, slow data

Mitigations:
  1. Isolate cpusets / GPU clocks / exclusive nodes
  2. Data loader prefetch & pinned memory
  3. MoE load balance
  4. Restart or migrate chronic stragglers
  5. NCCL flight recorder + timeout < ∞
```

### 3.10 Topology-aware placement interface

```text
Ask RM for:
  - pack TP groups inside NVLink domains
  - PP stages across rails with consistent NIC mapping
  - avoid cross-rack for small jobs; accept for huge jobs with hierarchy

Job spec knobs:
  topology_strict: bool
  max_cross_domain_tp: 0  # prefer
```

### 3.11 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Collective lib | NCCL | Best NVIDIA perf | Homegrown sockets for grads |
| Consistency | Sync training | Stable convergence story | Async SGD without asking |
| Progress durability | Sharded ckpt + manifest | Scale + atomicity | NFS single pickle 2TB |
| Failure | Restart from ckpt MVP | Operable | Pretend NCCL self-heals mid-collective |
| Placement | Topology-aware gang | MFU | Random GPU packing |
| Metrics | Hierarchical aggregate | Cardinality | Per-rank Prometheus labels forever |

---

## 4. Architecture Diagram

### 4.1 End-to-end platform

```text
+-------------+     +------------------+     +---------------------+
| Researchers |---->| Training API     |---->| Job Controller      |
+-------------+     +--------+---------+     +----------+----------+
                             |                          |
                             v                          v
                    +--------+---------+     +----------+----------+
                    | Artifact/Config  |     | GPU Resource Mgr    |
                    | (hparams, code)  |     | (gang bind/lease)   |
                    +------------------+     +----------+----------+
                                                        |
                     +----------------------------------+
                     v
              +------+------+------+------+
              | Rank0 | Rank1 | ... | RankN-1 |   (trainer runtimes)
              +---+---+--+---+------+---+-----+
                  |      |             |
                  +------+----NCCL-----+---- NVLink / IB fabric
                  |
                  v
         +--------+---------+     +------------------+
         | Checkpointer     |---->| Parallel FS / S3 |
         +--------+---------+     +------------------+
                  |
                  v
         +--------+---------+     +------------------+
         | Telemetry Agent  |---->| Metrics / Traces |
         +------------------+     +------------------+
```

### 4.2 Parallel mesh (example)

```text
Example: 64 GPUs, TP=8, PP=2, DP=4

Node0 GPUs[0..7] = TP group for PP stage0, DP0
Node1 GPUs[0..7] = TP group for PP stage1, DP0
Node2 ... DP1 PP0
...

DP AllReduce across nodes {0,2,4,6} for each (TP,PP) coordinate
PP P2P between stage0 ↔ stage1 within each DP replica
TP collectives stay inside node (NVLink)
```

### 4.3 Sequence: healthy step

```text
DataLoader → microbatch → PP schedule forwards → TP ops inside layers
         → PP backwards → DP grad sync → Optimizer
         → metrics
```

### 4.4 Sequence: failure → restart

```text
Rank k dies / NCCL timeout
  → Health Monitor flags job
  → Controller: set epoch=e+1; signal remaining ranks STOP
  → RM: release leases
  → Controller: create new gang request (same job_id, epoch e+1)
  → Bootstrap ranks; NCCL new world
  → Checkpointer.load(latest_manifest)
  → resume global_step+1
```

### 4.5 Checkpoint commit

```text
All ranks: write shard{step,rank}.bin (+ checksum)
Rank0: write manifest{step}.json.tmp with shard list
Durable barrier / fsync policy
Rank0: atomic rename → manifest{step}.json
Update job pointer latest_ckpt=step
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Collectives only inside live epoch | Epoch in rendezvous; abort stale |
| R2 | Gang complete before train | Controller barrier / RM bind TX |
| R3 | Checkpoint read ≤ last committed | Manifest rename atomicity |
| R4 | No dual optim steps for same step after resume | global_step in ckpt |
| R5 | Device exclusive to one job | RM lease + MIG optional |
| R6 | Hang detection finite | NCCL_TIMEOUT + step watchdog |

**Failure modes**

| Failure | Behavior |
|---------|----------|
| GPU XID / ECC storm | Drain node; fail job; blacklist device |
| IB link flap | NCCL error → restart; alert fabric |
| Rank slow not dead | Straggler policy; optional forced restart |
| Controller crash | Desired state in DB; reconcile; don’t double-start without epoch |
| FS full mid-ckpt | Abort commit; keep previous manifest |
| Silent corruption | Checksums on shards; optional end-to-end hash |

**Cancel vs checkpoint vs resume**

- **Cancel:** cooperative at step boundary if possible; else kill; last committed ckpt retained.  
- **Preempt:** signal → best-effort ckpt → PREEMPTED.  
- **Resume:** new epoch, load committed manifest only.

### 5.2 Scalability

| Scale | Architecture changes |
|-------|----------------------|
| 1× (≤8–16 GPU) | Single node / few nodes; DP+TP; sync ckpt OK |
| 10× | Multi-rack IB; async ckpt; PP common; topology prefs |
| 100× | Hierarchical AllReduce; ckpt staging via NVMe; dedicated metric pipeline |
| 1,000× | Planner service; fault domains; spare pools; multi-tier storage; EP at MoE scale |

**Collective scaling techniques**

- Tree / hierarchical reduction across racks  
- ReduceScatter+AllGather (ZeRO-2 style) vs flat AllReduce  
- CUDA Graph / persistence for steady-state steps  
- Rail-optimized / topology-aware NCCL envs  

**Data scaling**

- WebDataset / Mosaic / custom iterable shards  
- Per-DP-rank offsets checkpointed  
- Avoid global reshuffle that requires all-gather of index every epoch at huge scale  

### 5.3 Maintainability

- Versioned **parallel plan** + **runtime** + **ckpt format** (compat matrix).  
- Deterministic replay mode for debugging (fixed seeds, locked mesh).  
- Golden MFU benchmarks per SKU × model family.  
- Chaos: kill rank, drop IB, stall dataloader, fill disk.  
- Clear reason codes: `NCCLTimeout`, `OOM`, `CkptCorrupt`, `BootstrapFailed`, `TopologyUnsatisfied`.

**Observability must-haves**

| Signal | Why |
|--------|-----|
| Step time p50/p99 | Health |
| % time in NCCL | Comm bound diagnosis |
| MFU / tokens/s/GPU | Efficiency |
| CKPT duration & success | RPO risk |
| Slowest rank id | Straggler |
| GPU temp / power / XID | Hardware |
| IB retransmits | Fabric |

Cardinality policy: default **job-level** aggregates; on-demand **rank drill-down** with TTL.

### 5.4 Parallelism planner (interview-friendly)

```text
Input: model shape, max_gpus, SKU memory, topology, global_batch, seq_len
Output: TP, PP, DP, microbatch, ZeRO stage, estimated MFU & mem

Heuristics:
  TP = min(nearest_power_of_2 fitting NVLink domain, hidden_size constraints)
  choose PP so per-stage activation+params fit
  DP = world / (TP*PP)
  increase microbatches until bubble OK or mem hits cap
  if mem still high → ZeRO-1/2 or activation ckpt
```

Emphasize: planner is **heuristic + profile feedback**, not magic ILP in MVP.

### 5.5 Expert parallelism notes (MoE)

```text
Tokens routed → AllToAll to expert ranks → expert MLP → AllToAll back
Imbalance: some experts hot → stragglers
Mitigations: capacity factor, aux load-balancing loss, expert parallel degree tuning
Ckpt: expert shards large; same manifest protocol
```

### 5.6 Mixed precision deep dive

| Mode | Pros | Cons |
|------|------|------|
| FP32 | Stable | Too slow / fat |
| FP16 + loss scale | Faster | Scale care; overflows |
| BF16 | Stable on Ampere+ | Needs BF16 HW |
| FP8 (H100+) | Throughput | Recipe maturity; calibration |

Interview line: **BF16 default for modern NVIDIA training**; mention FP8 as optimization path.

### 5.7 Straggler & hang detection algorithm

```text
each rank: report progress_seq periodically to monitor
if global_step stuck for T_hang:
  dump NCCL flight recorder / stacks
  mark job FAILED_INFRA
  controller restarts with epoch++

if rank_step_time > k * median for W windows:
  label STRAGGLER; page on-call; optional replace
```

Tune `T_hang` ≫ p99 step, ≪ “burn hours unnoticed.”

### 5.8 Checkpoint performance design

```text
Tier0: GPU → pinned host / NVMe local
Tier1: parallel flush to DFS
Tier2: async replicate to object store
Commit: metadata in strongly consistent store

For 1,000×: coordinated but not single-rank serial upload
  use aggregated writers / multicast / GPUDirect Storage where available
```

### 5.9 Security & multi-tenancy

- Private process networks per job; no cross-job NCCL discovery.  
- Dataset ACLs; scrub secrets from logs.  
- Image allowlisting.  
- Escape hatch: admin can SIGKILL job epoch.

### 5.10 Interaction with GPU resource manager

```text
Training Controller                  GPU RM
   |-- RequestGang(sku, n, topology) -->
   |<- Allocation(devices, lease_epoch) --
   |-- Start ranks ----------------------
   |-- Heartbeat job health ------------>
   |-- Release / PreemptAck ----------->
```

Training system **must not** bind GPUs itself if RM is SoT—duplicate binding is a classic dual-allocator bug.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Clarify model size, GPU count, sync training, checkpoint RPO.  
2. Parallelism plan (TP in NVLink, PP across nodes, DP outer).  
3. Step loop + NCCL + mixed precision.  
4. Checkpoint manifest protocol.  
5. Failure → epoch restart; straggler/hang detection.  
6. Scale jumps: hierarchical comm, ckpt I/O, telemetry cardinality.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | DP+TP(+PP), NCCL, sync ckpt, fail→restart, basic metrics |
| 10× | Async ckpt, topology placement, hang watchdog |
| 100× | Hierarchical collectives, NVMe staging, planner v1, MoE/EP optional |
| 1,000× | Elastic/spare pools, multi-tier ckpt, cardinality-safe telemetry, fault domains |

### 6.3 Top risks

1. TP across slow links → catastrophic MFU.  
2. Unbounded NCCL hang without watchdog.  
3. Non-atomic checkpoints → corrupt resume.  
4. Telemetry cardinality outage.  
5. Dual ownership of GPU bind (trainer vs RM).

### 6.4 One-sentence design

> A topology-aware, gang-launched NVIDIA training runtime that composes DP/TP/PP/(EP) over NCCL, persists progress via atomic sharded checkpoints, and recovers from rank/node failure by fenced job epochs—optimized for MFU and honest communication/I/O bottlenecks as jobs grow from tens to tens of thousands of GPUs.

---

## 7. Deeper / Related Interview Questions

### 7.1 Parallelism

**Q: When is tensor parallel better than pipeline parallel?**  
A: When a layer doesn’t fit or you’d pay huge activation memory; TP needs fast NVLink. PP helps depth but introduces bubbles.

**Q: Why not only data parallel with ZeRO-3?**  
A: Can work; at extreme scale AllGather params every layer may lose to Megatron-style TP/PP on NVIDIA clusters—profile.

**Q: How do you place TP groups?**  
A: Inside NVLink domains first; never casually split a TP group across IB.

**Q: What does DP×TP×PP mean for world size?**  
A: Product equals world size (×EP if MoE).

**Q: What’s a pipeline bubble?**  
A: Idle time from filling/draining stages; shrink with more microbatches or schedules (1F1B).

### 7.2 NCCL & collectives

**Q: AllReduce vs ReduceScatter+AllGather?**  
A: Similar asymptotic volume; RS+AG pairs naturally with sharded opts (ZeRO).

**Q: Why do NCCL hangs happen?**  
A: Rank desync, network, GPU error, mismatched collective order—desync is #1 software cause.

**Q: How to debug?**  
A: Flight recorder, sync checks, isolate whether compute or collective, verify rank maps.

**Q: CUDA-aware MPI vs NCCL?**  
A: For NVIDIA GPU grads, NCCL is the expected answer.

### 7.3 Checkpointing

**Q: Sync vs async checkpoint?**  
A: Sync simple/stalls; async needs memory snapshot discipline and clear commit.

**Q: How atomic is “atomic”?**  
A: Manifest points only to fully written checksummed shards; rename/put-if-absent.

**Q: How often to checkpoint?**  
A: Balance RPO vs overhead; 10–30 min common; shorter near unstable clusters.

**Q: Can you checkpoint without global barrier?**  
A: Risky for consistency of optimizer/RNG; usually barrier or quiesce step.

### 7.4 Failure & elasticity

**Q: Why not continue with N-1 ranks?**  
A: Mesh and batch semantics break; collectives need planned world. Elastic requires explicit replan.

**Q: What is a job epoch?**  
A: Generation id fencing stale processes after restart.

**Q: Hot spare GPUs?**  
A: Fast RTO, expensive; use for SLA-critical runs.

**Q: Preemption during backward?**  
A: Best-effort interrupt; may lose step; rely on last ckpt.

### 7.5 Stragglers & performance

**Q: MFU definition?**  
A: Achieved FLOPs / peak FLOPs (be clear which peak).

**Q: Free GPUs but low MFU—why?**  
A: Comm bound, bubble, small batch, CPU preprocess, poor topology.

**Q: How to detect stragglers?**  
A: Per-rank timers vs median; correlate with thermals and NIC counters.

**Q: Activation checkpointing trade-off?**  
A: Recompute saves memory, costs FLOPs/time.

### 7.6 Topology

**Q: NVLink vs IB roles?**  
A: NVLink: intra-node high bandwidth low latency (TP). IB: inter-node (PP/DP hierarchy).

**Q: What if RM packs across racks?**  
A: May still run; large jobs should wait or soft-prefer; strict mode for huge TP.

**Q: Multi-rail NICs?**  
A: Pin ranks to rails carefully; avoid accidental congestion on one rail.

### 7.7 Mixed precision & numerics

**Q: Why BF16 over FP16?**  
A: Wider exponent, fewer loss-scale fires on modern NVIDIA GPUs.

**Q: Master weights?**  
A: FP32 copy for optimizer stability while compute in BF16.

**Q: Reproducibility?**  
A: Hard with atomic adds / nondeterministic kernels; offer deterministic mode for debug at speed cost.

### 7.8 Telemetry

**Q: Why does Prometheus die at 64k GPUs?**  
A: Cardinality: rank/gpu labels at 1Hz. Aggregate and sample.

**Q: What minimal dashboard?**  
A: tokens/s, step time, NCCL%, ckpt lag, job restarts, GPU errors.

### 7.9 Comparison traps

**Q: Is this Kubernetes?**  
A: K8s may launch pods; **training semantics** (mesh, ckpt, NCCL) are above it; GPU bind may be RM.

**Q: vs single-node training?**  
A: Same loop; plus membership, topology, distributed ckpt, hang detection.

**Q: Why not parameter server async?**  
A: Stale grads; rare for modern LLM pretrain interviews—sync data parallel family dominates.

### 7.10 Extra interviewer traps (high value)

- Split **compute vs collective vs ckpt I/O** load classes.  
- Show **bubble fraction** arithmetic.  
- Show why **TP must be NVLink-local**.  
- Manifest **commit** vs shard write.  
- Job **epoch fencing**.  
- Telemetry **cardinality**.  
- MFU honesty (not brochure peak).  
- Dual allocator bug with RM.  
- MoE AllToAll imbalance.  
- RPO vs interval.  
- Global batch vs microbatch vs DP.  
- ZeRO stage vs Megatron TP—when mention both.  
- What happens if one rank OOMs.  
- Why infinite NCCL timeout is dangerous.  
- Dataset offset resume.

---

## 8. Appendices

### 8.1 Example schemas

```sql
CREATE TABLE training_jobs (
  job_id UUID PRIMARY KEY,
  project_id UUID NOT NULL,
  state TEXT NOT NULL,
  epoch INT NOT NULL DEFAULT 0,
  sku TEXT NOT NULL,
  gpu_count INT NOT NULL,
  parallel_plan JSONB NOT NULL,
  dataset_uri TEXT NOT NULL,
  latest_ckpt_step BIGINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE training_restarts (
  job_id UUID NOT NULL,
  epoch INT NOT NULL,
  reason TEXT NOT NULL,
  started_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (job_id, epoch)
);

CREATE TABLE checkpoint_manifests (
  job_id UUID NOT NULL,
  step BIGINT NOT NULL,
  status TEXT NOT NULL, -- committing|committed|aborted
  location TEXT NOT NULL,
  checksum TEXT NOT NULL,
  committed_at TIMESTAMPTZ,
  PRIMARY KEY (job_id, step)
);
```

### 8.2 Job spec example

```json
{
  "project_id": "p_train",
  "image": "nvcr.io/acme/nemo:24.01",
  "command": ["python", "-m", "train"],
  "resources": {"sku": "H100", "gpus": 64},
  "parallelism": {"tp": 8, "pp": 2, "dp": 4, "zero_stage": 1},
  "precision": "bf16",
  "data": {"uri": "s3://datasets/tokens/", "seq_len": 8192, "global_batch_tokens": 1000000},
  "checkpoint": {"interval_steps": 500, "uri": "s3://ckpts/job/"},
  "topology_strict": true,
  "max_runtime_hours": 168
}
```

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| DP / TP / PP / EP | Data / tensor / pipeline / expert parallelism |
| NCCL | NVIDIA collective communications library |
| MFU | Model FLOPs utilization |
| Gang | All-or-nothing multi-GPU launch |
| Manifest | Atomic checkpoint pointer + shard list |
| Job epoch | Restart generation / fencing token |
| Bubble | Pipeline idle fraction |
| ZeRO / FSDP | Sharded optimizer/param strategies |
| XID | NVIDIA GPU error event code |
| NVLink / IB | Intra-node / inter-node high-speed fabrics |
| Straggler | Slow rank stretching synchronous steps |
| RPO / RTO | Data loss window / recovery time |

### 8.4 Progressive scale checklist

| Scale | Must add |
|-------|----------|
| 1× | DP+TP, NCCL, sync ckpt, basic metrics |
| 10× | PP, topology prefs, hang watchdog, async ckpt |
| 100× | Hierarchical comm, NVMe staging, planner, MoE hooks |
| 1,000× | Fault domains, spare/elastic, multi-tier ckpt, metric aggregation |

### 8.5 Estimation cheat-sheet

```text
param_bytes_bf16 ≈ 2 × N
train_state_bytes ≈ 8–16 × N  (Adam + masters + grads rough)

FLOPs/step ≈ 6 × N × tokens_per_step   (dense rough)
step_time ≈ FLOPs / (gpus × achieved_FLOP/s)

AllReduce ~ 2×(N-1)/N × message ≈ 2×message/N per GPU (ring intuition)
PP bubble ≈ (P-1)/(M+P-1)

ckpt_time ≈ state_bytes / aggregate_write_BW
telemetry_points ≈ gpus × metrics × hz  → aggregate!

free_gpus ≠ good_topology_for_TP
```

### 8.6 Parallelism decision cheat-sheet

```text
fits on 1 GPU? → DP (+ maybe ZeRO)
fits on 1 node with TP? → TP within node + DP across nodes
depth/memory still high? → add PP
MoE? → add EP + watch AllToAll
still OOM? → activation checkpoint, lower microbatch, ZeRO↑
```

### 8.7 Health watchdog pseudocode

```text
on_timer:
  if now - last_global_step_ts > HANG_TIMEOUT:
     capture_diagnostics()
     fail_job(reason=NCCL_OR_STEP_HANG)
  for rank in ranks:
     if rank.step_time_ewma > k * median_ewma:
        mark_straggler(rank)
```

### 8.8 Interview “say this” summary (60 seconds)

> I’d build a gang-scheduled NVIDIA training runtime: plan DP/TP/PP with TP glued to NVLink, run sync steps over NCCL, checkpoint sharded state with an atomic manifest for RPO control, and on failure fence a new job epoch and resume. At scale the hard parts are topology placement, collective hierarchy, checkpoint bandwidth, straggler/hang detection, and keeping telemetry cardinality from melting the control plane.

### 8.9 Reliability test plan

1. Kill one rank mid-step → restart from last committed ckpt; epoch bumps.  
2. Kill during checkpoint upload → no corrupt latest pointer.  
3. Induce IB loss → timeout fires; no infinite hang.  
4. Slow one rank’s dataloader → straggler metrics alert.  
5. Resume with changed world size without elastic support → hard fail with clear error.  

### 8.10 Related systems map

```text
API → Job Controller → GPU RM (gang)
                 ↓
        Rank Runtimes + NCCL (NVLink/IB)
                 ↓
        Checkpointer → Durable Store
                 ↓
        Telemetry Pipeline (aggregated)
```

### 8.11 Extra traps

| Trap | Pushback |
|------|----------|
| “Just AllReduce everything” | Memory + bandwidth won’t work for huge models |
| Infinite NCCL timeout | Hidden multi-hour GPU burn |
| Single pickle checkpoint | Won’t scale; non-atomic |
| Random placement | TP over IB destroys MFU |
| Per-rank metrics forever | TSDB meltdown |
| Trainer binds GPUs itself | Dual allocator races |
| Async SGD casually | Changes convergence story—ask first |
| Brochure TFLOPS as MFU denom | Inflated utilization narrative |

### 8.12 Observability SLOs

| SLO | Example |
|-----|---------|
| Hang detection | < 60–120s |
| Checkpoint success rate | > 99.9% commits |
| Restart RTO (mid-size) | < 15 min |
| Step time cv (healthy) | p99/p50 < 1.5 |
| Unexpected restart rate | tracked per 1k GPU-hours |

### 8.13 Mixed-precision notes card

```text
BF16 compute + FP32 master + Adam FP32 states (common)
FP16 → dynamic loss scaling
FP8 → H100+ path; validate quality
Grad clip after unscale
Check overflow metrics when using FP16/FP8
```

---

*End of design doc. Open with §1 parallelism + failure scope; whiteboard §3.2–3.8 mesh/NCCL/ckpt/restart; close with invariants §5.1 and traps §7.10.*
