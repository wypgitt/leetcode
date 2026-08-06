# System Design: Dockerized GPU-Test Platform

> **Focus areas:** GPU passthrough / MIG · Container isolation · Driver/CUDA/graphics tests · Device health gates · Flake detection · Multi-tenant CI security · Artifact capture · Node scheduling  
> **Style:** End-to-end platform design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split control-plane vs GPU-device load, honest privileged-container threat model, resolved ownership of device leases vs test orchestration

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

Goal: **bound the platform**—what “GPU test in a container” means (passthrough vs MIG vs software), who submits, how isolation and device health interact, and which security constraints are non-negotiable for multi-tenant CI.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who submits tests? | Internal CI (Jenkins/GitLab), driver/CUDA/graphics teams, partner labs | Multi-tenant queues; authz by org/project; audit every bind |
| F2 | What runs? | GPU functional, driver, CUDA samples, Vulkan/OpenGL/DX conformance, stress, power | Heterogeneous images + device capabilities matching |
| F3 | Container model? | Docker/OCI with NVIDIA Container Toolkit; optional Kata/gVisor later | Runtime plugin + device plugins; privilege ladder |
| F4 | GPU access mode? | Full passthrough, MIG slices, time-sliced (shared) for light tests | Inventory by mode; not fungible across modes |
| F5 | Isolation bar? | Strong enough for multi-team CI; no cross-tenant GPU theft or host escape as baseline | Seccomp, device cgroup, network policy, image allowlist |
| F6 | Scheduling? | Schedule tests onto healthy GPU nodes matching SKU/driver/API | Device lease + capability matching; health gates before bind |
| F7 | Results? | Pass/fail/skip + logs + GPU metrics + golden diffs | Result store + artifact object storage |
| F8 | Flakes? | Detect intermittent failures; quarantine flaky tests/devices | Statistical flake service; quarantine queues |
| F9 | Device health? | Don’t schedule onto Xid-sick / ECC / thermal-bad GPUs | Health agent + gate before bind; drain/quarantine nodes |
| F10 | Artifacts? | Screenshots, frame dumps, core dumps, nvidia-smi logs, traces | Size-capped upload; retention tiers |
| F11 | Privileged needs? | Some driver tests need `--privileged` or `/dev` access | **Privilege tiers**; default least privilege; gated exceptions |
| F12 | Observability? | Per-run timeline, device id, driver version, flake score | Correlate `run_id` / `device_id` / `image_digest` |

**MVP functional scope (lock with interviewer):**

1. Submit **test run** spec: image digest, command, required GPU SKU/driver/CUDA, API (CUDA/Vulkan/…), privilege tier, timeout.  
2. **Admit** with quota + capability match; enqueue.  
3. **Health-gate** candidate devices; **lease** GPU (full or MIG) atomically.  
4. Start container with NVIDIA runtime inject; collect stdout/stderr + structured result.  
5. Upload artifacts under size/retention policy; mark terminal status.  
6. Basic **flake detection** (retry N, track pass-rate); quarantine tests below threshold.  
7. Multi-tenant: project authz, image allowlist, audit bind/start/stop.

**Out of MVP:**

- Full confidential computing / attested TEE for every GPU test  
- Perfect graphics golden-image CI across all OS SKUs (matrix is sibling design)  
- Automatic root-cause for every Xid  
- Cross-cloud GPU arbitrage  
- Running untrusted third-party containers with host-kernel module load rights

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Schedule latency (healthy free GPU → start) | CI-interactive for smoke | p50 < 5s, p99 < 30s when capacity free |
| N2 | Isolation | No cross-tenant device theft | Lease fencing + cgroup device ACL |
| N3 | Correctness | No double-bind GPU | Single allocator SoT; epoch fencing |
| N4 | Security | Privileged path tightly gated | Default non-priv; break-glass audited |
| N5 | Durability of results | Accepted run → durable result metadata | RPO ≈ 0 for terminal status + artifact pointers |
| N6 | Availability | Control plane 99.9%; devices drain gracefully | Degrade low-priority first |
| N7 | Flake signal quality | Actionable quarantine | Don’t quarantine on n=1 failure |
| N8 | Throughput | See scale table | Split submit / lease / heartbeat / result QPS |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. CI submits CUDA unit image → match H100 + driver ≥ X → health OK → lease 1 GPU → container runs → pass → artifacts uploaded → settle lease.  
2. Graphics conformance needs MIG 1g.10gb → bind MIG instance → run → collect frames → pass.  
3. Stress test requests full node exclusive → exclusive lease all GPUs on node → run 4h → complete.  
4. Flaky test fails once, passes on retry → mark `FLAKY_PASS`; update flake score.  
5. Node reports Xid 79 → health agent marks GPU `UNHEALTHY` → drain; in-flight tests fail with infra reason (not product fail).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two runs race for same GPU | Allocator CAS; loser waits/requeues |
| Container escapes attempt | Seccomp/AppArmor + no host Docker socket; alert |
| Privileged test requests host modules | Only on dedicated privileged pool; never shared tenant pool |
| Driver mismatch (image needs 550, node 535) | Capability filter excludes node; queue or fail admit |
| MIG create fails mid-bind | Abort bind TX; mark device suspect; retry elsewhere |
| Artifact upload exceeds quota | Truncate with marker; keep logs; fail soft or hard per policy |
| Agent heartbeat miss | Grace → reclaim lease; fencing rejects late complete |
| Test hangs past timeout | SIGTERM → SIGKILL; capture last nvidia-smi; mark `TIMEOUT` |
| Golden diff noise across driver | Flake/quarantine path; don’t auto-blame device |
| Multi-tenant noisy neighbor on shared GPU | Prefer exclusive or MIG; time-slice only for trusted light tests |
| Host OOM / GPU OOM | Classify infra vs test; device health check after |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPU devices | 500 | 5,000 | 50,000 | 500,000 |
| Nodes | 100 | 1,000 | 10,000 | 100,000 |
| Concurrent test containers | 400 | 4,000 | 40,000 | 400,000 |
| Test submits / day | 50K | 500K | 5M | 50M |
| Peak submit QPS | ~5 | ~50 | ~500 | ~5K |
| Peak lease/bind QPS | ~10 | ~100 | ~1K | ~10K |
| Agent heartbeats /s | ~20 | ~200 | ~2K | ~20K |
| Result writes / day | 50K | 500K | 5M | 50M |
| Artifact volume / day | 2 TB | 20 TB | 200 TB | 2 PB |
| Tenants / projects | 50 | 500 | 5K | 50K |
| Distinct images (digests/week) | 2K | 20K | 200K | 2M |
| SKUs / driver tracks | 8 / 3 | 12 / 5 | 20 / 8 | 40 / 12 |
| Privileged-pool GPUs | 20 | 100 | 500 | 2,000 |

**What each jump forces:**

- **10×:** HA allocator; shard queues by SKU/pool; dedicated privilege pools; artifact CDN/tiering.  
- **100×:** Cell/region federation; heartbeat aggregation; MIG inventory service; flake warehouse.  
- **1,000×:** Hierarchical admit → regional place; cold artifact archive; approximate scheduling; device telemetry lake.

### 1.5 Etc. (Constraints & Assumptions)

- Hosts run **Linux** with NVIDIA driver + container toolkit; Windows graphics matrix may be sibling (Jenkins matrix doc).  
- We own **control plane + agent + runtime policy**; test binaries come from teams.  
- “Privileged” is a **first-class pool**, not a boolean sprinkled on shared nodes.  
- GPU time is scarce; **health false-negatives** (scheduling onto sick GPUs) burn more engineering time than false-positives.  
- Results are **at-least-once published**; consumers dedupe on `run_id`.

**Scope statement:**

> Design a multi-tenant dockerized GPU-test platform that schedules containerized driver/CUDA/graphics tests onto healthy GPU devices (passthrough/MIG), enforces isolation and privilege tiers, collects results/artifacts, detects flakes, and scales from hundreds to hundreds of thousands of GPUs without double-binding devices or treating privileged CI as “just another Docker flag.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Submit / admit | 5 QPS | 5K QPS | Control plane |
| Lease / bind | 10 QPS | 10K QPS | Hot path; CAS |
| Agent heartbeat | 20/s | 20K/s | Distinct plane |
| Result finalize | 5 QPS | 5K QPS | Terminal + pointers |
| Artifact PUT bytes | ~200 MB/s avg | ~200 GB/s peak-ish | Object storage |
| Health events | ~1/s | ~1K/s | Spiky on driver bugs |

**Deal-breaker:** treating “cluster QPS” as one number, or routing artifact bytes through the job OLTP DB.

### 2.2 Device utilization math

```text
Baseline: 500 GPUs, 400 concurrent containers → 80% allocation if 1:1
Many tests are short (2–10 min); turnover high:

50K tests/day ÷ 86400 ≈ 0.58 starts/s average
Peak ~5/s matches table (≈8–10× average)

If mean duration 8 min = 480s:
concurrency ≈ 0.58 × 480 ≈ 280 average; peak 400–500 with bursts
```

At **1,000×**:

```text
50M tests/day → ~580/s average starts; peak ~5K/s
mean 480s → concurrency ~280K average; provision for ~400K peak
→ cell sharding mandatory; no global single allocator loop
```

### 2.3 Artifact storage

```text
Avg artifact set: 40 MB (logs small; dumps rare but heavy)
p50: 5 MB; p99: 500 MB; rare core+frame dump: multi-GB

Baseline: 50K × 40 MB ≈ 2 TB/day raw
Retain hot 14 days: ~28 TB
Cold 90 days: compress/downsample frames → policy

1,000×: 2 PB/day raw is unsustainable as “keep everything hot”
→ default: logs + junit always; heavy dumps on fail only; sample passes
```

**Unit check:** 50K × 40 MB = 2×10^6 MB = **2 TB/day**, not 2 PB. At 1000×: 50M × 40 MB = 2×10^9 MB = **2 PB/day** if naïve—hence fail-only heavy artifacts.

### 2.4 Heartbeat & telemetry bandwidth

```text
100 nodes × 1 HB / 5s = 20 HB/s baseline
HB payload ~2 KB (per-GPU health summary) → 40 KB/s trivial

1,000×: 100K nodes × 0.2 Hz = 20K HB/s × 2 KB ≈ 40 MB/s
→ aggregate per rack/cell; don’t write full HB to global OLTP each tick
```

### 2.5 Image pull & cache pressure

```text
If 30% of starts miss node cache:
baseline peak 5 starts/s × 0.3 × 2 GB image ≈ 3 GB/s pull fabric (bad)
→ image cache / registry mirrors / warm pools per SKU cell
Target: >90% node cache hit for top images
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Device double-bind / lease races** under allocator failover  
2. **Sick GPU scheduling** (health gate lag) → mass false failures  
3. **Privileged pool contamination** of multi-tenant nodes  
4. **Artifact / registry bandwidth** storms after large matrix pushes  
5. **Flake false quarantine** thrashing CI  
6. **MIG reconfigure thrash** (create/destroy storms)

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
TestRun     → requested execution (image, cmd, caps, privilege tier)
Device      → physical GPU or MIG instance with health + capabilities
Lease       → time-bounded exclusive ownership of Device for a TestRun
NodeAgent   → host daemon: inventory, health, start/stop containers
Pool        → isolation domain: shared-ci | exclusive | privileged | partner
Result      → terminal status + metrics + artifact pointers
FlakeScore  → statistical view over (test_id × env fingerprint)
```

**State machine (TestRun):**

```text
ADMITTED → QUEUED → BINDING → STARTING → RUNNING → SUCCEEDED|FAILED|TIMEOUT|CANCELLED
              ↑         |          |
              +-- requeue on reclaim / infra fail (policy)
HEALTH_GATED (substate during BINDING)
INFRA_FAILED (device/node fault—not counted as product fail)
```

### 3.2 Options: where does GPU binding live?

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. K8s device plugin only | Familiar | Weak multi-dim matching, flake/health product logic elsewhere | Treating plugin as full test platform |
| B. Custom allocator + Docker agent | Precise leases, health gates | You operate agents | Team refuses agent ownership |
| C. Pure Jenkins labels | Simple MVP | Matrix explosion, weak fencing | Multi-tenant + MIG + health at scale |
| D. Hybrid: K8s for lifecycle + external GPU SoT | Scale + clarity | Dual-bind risk if both allocate | Two writers on device lease |

**Chosen path:**

- **Device lease SoT:** custom **GPU Allocator** (leader per cell) with durable lease table.  
- **Container lifecycle:** NodeAgent (Docker/containerd) or K8s RuntimeClass—but **only starts after lease commit**.  
- **CI systems** (Jenkins etc.) are **clients** of the platform API, not the device SoT.

**Deal-breaker:** Jenkins agent and K8s scheduler and custom allocator all “picking GPUs” independently.

### 3.3 Capability model & matching

```text
Device caps:
  sku, memory_mb, mig_mode, driver_version, cuda_version,
  apis: [CUDA, VULKAN, OPENGL, DX], ecc, power_limit_profile,
  pool: shared|exclusive|privileged, health: HEALTHY|SUSPECT|UNHEALTHY

Run requirements:
  sku_in | sku_family, min_driver, min_cuda, api, mig_profile?,
  exclusive_node?, privilege_tier, labels (e.g. display=:0 for GL)
```

**Match:** filter HEALTHY devices in allowed pools → score (binpack leftover / driver freshness) → bind.

### 3.4 Privilege tiers (security spine)

| Tier | Caps | Pool | Who can request |
|------|------|------|-----------------|
| T0 Sandbox | no priv; GPU via CDI/device nodes only; no host net | shared-ci | default CI |
| T1 Device | add specific `/dev/nvidia*`, SYS_ADMIN carefully scoped | shared-ci / exclusive | most CUDA/graphics |
| T2 Privileged | `--privileged` or module ops | **privileged pool only** | allowlisted jobs |
| T3 Bare-metal script | agent runs host script (rare) | privileged + break-glass | security review |

**Invariants:**

- T2/T3 **never** land on shared multi-tenant nodes.  
- Image digests for T2+ on **allowlist**; signed images preferred.  
- No Docker socket mount into test containers.  
- Network: default deny egress except artifact/registry endpoints (proxy).

**Deal-breaker:** “We’ll just use `--privileged` for everything so driver tests work.”

### 3.5 Passthrough vs MIG vs time-slice

| Mode | Isolation | Density | Use |
|------|-----------|---------|-----|
| Full GPU passthrough | Strong (per GPU) | 1 run / GPU | Correctness, perf, power |
| MIG instance | Strong within Ampere+ partitions | Multi-run / GPU | Unit/small CUDA |
| Time-sliced shared | Weak | Highest | Trusted smoke only |

**Policy:** correctness/perf → exclusive full GPU; high-volume unit → MIG; never time-slice untrusted or privileged.

### 3.6 Health gates

```text
Before BIND commit:
  device.health == HEALTHY
  node.drain == false
  recent_xid_window clear (policy)
  optional: quick sanity probe (nvidia-smi query) if SUSPECT→recheck

Agent continuous:
  Xid/SXid, ECC, temp, retired pages, persistence mode, fabric
  → SUSPECT → UNHEALTHY → quarantine device/node
```

**Ownership:** Agent owns raw signals; **Health Service** owns state machine; Allocator reads gates only.

**Infra vs product failure:** if device dies mid-run → `INFRA_FAILED` + auto-retry on new device (bounded); do not increment flake score for pure infra.

### 3.7 Scheduling & fairness

```text
Queues: per (cell, pool, sku_family, privilege_tier)
Priority: P0 blocking CI / release → P1 gated merge → P2 nightly → P3 experimental
Fairness: weighted fair share per project; aging; concurrent caps
```

**Exclusive node jobs:** allocate all GPUs on node or dedicated label `exclusive=true` nodes.

**Gang-like multi-GPU tests:** all-or-nothing bind of N GPUs on same node (or same NVLink domain).

### 3.8 Result collection & artifacts

```text
During run:
  stream logs to log service (chunked)
  sample GPU metrics (util, mem, power, clocks) every S seconds
On terminal:
  agent uploads artifacts → object storage (presigned)
  result service writes: status, exit_code, reason_code, artifact_uris, metrics_summary
```

**Artifact classes:** `logs`, `junit`, `frames`, `dumps`, `traces`. Retention: logs 30d; dumps 14d fail-only; frames sampled.

### 3.9 Flake detection

```text
Key: test_id + env_fingerprint
  env_fingerprint = hash(sku_family, driver_major, api, os_image, mig_mode)

Signals:
  pass_rate over last N runs (N≥20 before hard quarantine)
  infra-filtered (exclude INFRA_FAILED)
  consecutive fails vs intermittent

Actions:
  soft: label FLAKY; CI may retry
  hard: quarantine test_id (skip or dedicated flake lane)
  device quarantine separate from test quarantine
```

**Deal-breaker:** quarantining a test after one fail on a sick GPU.

### 3.10 Multi-tenant security model

| Layer | Control |
|-------|---------|
| Authn/z | SSO + project RBAC; service accounts for CI |
| Admission | Quotas, privilege tier authz, image allowlist/signature |
| Runtime | Privilege tier → pool; seccomp; no socket mount |
| Device | Lease fencing; cgroup device whitelist |
| Network | Egress proxy allowlist |
| Data | Per-tenant artifact prefixes; encrypted at rest |
| Audit | Every admit/bind/privilege escalation |

### 3.11 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Device SoT | Cell allocator + lease epochs | No double-bind | Ad-hoc `nvidia-smi` on agent |
| Privileged tests | Dedicated pool | Contain blast radius | Privileged on shared CI nodes |
| Artifacts | Object storage + pointers | OLTP stays slim | BLOBs in Postgres |
| Health | Agent + health service | Fast gate | Scheduler pings nvidia-smi synchronously each schedule (too slow/fragile alone) |
| Flakes | Stats service + infra filter | Actionable | Binary “fail=flake” |
| Images | Digest-pinned + node cache | Reproducible | `latest` tags in CI |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  CI / Dev clients
        |
        v
 +------+-------+     +------------------+
 | API Gateway  |---->| Admit / Quota    |
 +------+-------+     +--------+---------+
        |                      |
        v                      v
 +------+-------+     +--------+---------+
 | Run Service  |---->| Queue Shards     |
 +------+-------+     | (pool,sku,tier)  |
        |             +--------+---------+
        |                      |
        v                      v
 +------+----------------------+------+
 |     GPU Allocator (leader/cell)    |
 |  leases | capability index | MIG   |
 +------+----------------------+------+
        |                      ^
        v                      |
 +------+-------+     +--------+---------+
 | Node Agents  |---->| Health Service   |
 | container+GPU|     | Xid/ECC/thermal  |
 +------+-------+     +------------------+
        |
        +------> Log stream
        +------> Artifact Object Store
        +------> Result Service --> Flake Service
                    |
                    v
              Dashboards / CI callbacks
```

### 4.2 Sequence: admit → health gate → lease → run → result

```text
CI → API: CreateRun(image@sha, caps, tier=T1)
API → Admit: authz + quota + allowlist OK
API → Queue: ENQUEUE
Allocator: pop run; pick candidate device D
Allocator → Health: gate(D) → HEALTHY
Allocator: CAS lease(D, run_id, epoch++)
Allocator → Agent: Start(run, lease_epoch, runtime_spec)
Agent: inject GPU via toolkit; start container
Agent → HB running + metrics
Container exits 0
Agent → Artifacts PUT; Result: SUCCEEDED
Allocator: release lease
Flake: update pass_rate(test_id, env_fp)
```

### 4.3 Sequence: sick GPU mid-run

```text
Agent: observe Xid critical on GPU
Agent → Health: UNHEALTHY(device)
Health → Allocator: revoke leases on device
Allocator → Agent: Kill(run) if still running
Result: INFRA_FAILED(reason=Xid)
Queue: retry policy → new device (attempt++)
Flake: do NOT count as product flake
Device: quarantined until host remediation
```

### 4.4 Sequence: privileged break-glass

```text
CI → API: CreateRun(tier=T2, justification, image_sig)
Admit: require role gpu-test-privileged; image on T2 allowlist
Queue: privileged pool only
Allocator: bind only nodes labeled pool=privileged
Agent: start with elevated spec; audit event PRIV_START
On complete: PRIV_END audit; artifacts still scanned for secrets
```

### 4.5 Sequence: flake quarantine

```text
Result stream → Flake Service
if runs>=20 and pass_rate < 0.7 and infra_filtered:
  mark test_id QUARANTINED
CI callback: skip or route to flake lane
Owner ack + fix → unquarantine API (audited)
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Device has ≤1 valid lease owner | CAS + epoch fencing |
| R2 | Agent starts container only with valid epoch | Reject stale Start |
| R3 | T2/T3 only on privileged pool | Admit + allocator filters |
| R4 | UNHEALTHY devices not newly bound | Health gate |
| R5 | Terminal result durable before CI ACK (webhook) | Result store fsync/OK |
| R6 | Infra failures ≠ product flakes | Reason taxonomy |
| R7 | Single allocator leader per cell | Raft/etcd election |
| R8 | Late complete after reclaim rejected | lease_id / epoch check |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| Allocator leader crash | Elect; rebuild indexes from lease table; agents continue |
| Agent crash mid-run | Lease expiry → reclaim; mark INFRA; retry policy |
| Registry outage | Backoff starts; don’t burn GPU idle forever—timeout bind |
| Object store outage | Keep logs locally spool; retry upload; result `SUCCEEDED_WITH_ARTIFACT_GAP` |
| Health false positive storm | Hysteresis; require N signals; human override drain |
| Split-brain two allocators | Leader epoch on Start; agent fences old |

### 5.2 Scalability

**1×:** Single allocator + Postgres leases; 500 GPUs fine.

**10×:** Leader election; queue shards; registry mirrors; artifact tiering; privileged pool separation.

**100×:** Cells (e.g. per building/region); HB aggregators; MIG manager service; flake warehouse (columnar); CI webhooks async.

**1,000×:** Hierarchical global queue → cell placement; approximate free-device sketches; cold archive; per-tenant cells for noisy partners.

**Backpressure:** if STARTING backlog high, pause dequeue; if artifact spool disk high, shed pass-path dumps first.

### 5.3 Maintainability

- Deterministic **allocator simulator** (bind/health/flake).  
- **Shadow matching** for new capability rules.  
- Stable **reason codes**: `NoHealthySku`, `PrivilegeDenied`, `ImageNotAllowed`, `XidQuarantine`, `FlakeQuarantined`, `LeaseFenced`.  
- Version **runtime spec** schema; agents advertise supported versions.  
- Golden “platform canary” suite per SKU after driver deploy.

### 5.4 Ownership resolution (contradictions to avoid)

| Concern | Owner |
|---------|-------|
| Who may run (authz/quota) | Admit service |
| Who runs next | Queue fairness |
| Which device | Allocator |
| Is device healthy | Health service (allocator consumes) |
| Container PID lifecycle | Node agent |
| Pass/fail semantics | Result service (test exit + taxonomy) |
| Flake quarantine | Flake service |
| Privileged exception | Security policy + admit |

**Contradiction trap:** CI system kills containers while allocator still thinks lease is valid without revoke path—define Cancel API that revokes lease and signals agent.

### 5.5 Device inventory & MIG lifecycle

```text
Inventory events: device added/removed, MIG reconfigured, driver upgraded
Allocator indexes: free lists by (pool, sku, mig_profile, driver_track)

MIG:
  static profiles preferred for CI stability
  dynamic create: rate-limited; cool-down after destroy
  never reconfig under active leases
```

**Deal-breaker:** destroying MIG instances under a running container “to make room.”

### 5.6 Runtime injection details (interview-level)

```text
NVIDIA Container Toolkit / CDI:
  mounts driver libs matching host driver
  injects device nodes per lease
  sets NVIDIA_VISIBLE_DEVICES=<uuid|mig>

Graphics (GL/Vulkan):
  may need render nodes, ICD json, optional display
  headless via EGL/Vulkan; separate node label for display-attached
```

**Reproducibility:** pin driver userspace compatibility; record `driver_version`, `nvml`, `image_digest` on every result.

### 5.7 Isolation deep dive

| Threat | Mitigation |
|--------|------------|
| Cross-tenant GPU read | Exclusive lease; reset GPU between tenants (scrub) |
| Host escape via GPU | Prefer non-priv; kernel mitigations; privileged pool |
| Docker socket escape | Never mount socket; agent is only client |
| Registry poison image | Digest pin + signature verify on admit |
| Artifact secret leak | Scanner; path ACLs; short-lived URLs |
| Side-channel on shared | Don’t share untrusted; MIG/full only |

**GPU reset between tenants:**

```text
On lease release (multi-tenant pools):
  optional nvidia-smi --gpu-reset / fabric manager hooks
  clear MIG secrets; verify health before return to free list
```

### 5.8 Flake mathematics (say the numbers)

```text
Wilson score or Beta-Binomial on passes:
  After 20 runs, 12 pass → pass_rate=0.6 → soft flaky
  Quarantine if lower credible bound < threshold (e.g. 0.75) AND n≥20
Exclude INFRA_FAILED from denominator
Separate scores per env_fingerprint (driver 550 vs 560 ≠ same bucket)
```

### 5.9 Scheduling under fragmentation

```text
Free GPUs scattered; multi-GPU test needs 4 on one node:
  wait / binpack preference / exclusive node pool
Don’t start partial 2/4—wastes devices and fails tests
```

### 5.10 Observability

| Dashboard | Metrics |
|-----------|---------|
| Capacity | free/leased by SKU/pool; queue age p50/p99 |
| Health | unhealthy count; Xid rate; quarantine churn |
| CI | start latency; infra fail %; flake rate |
| Security | T2 starts; allowlist rejects; escape alerts |
| Artifacts | bytes/day; upload fail %; spool depth |
| Images | cache hit %; pull latency |

### 5.11 Progressive security hardening

| Phase | Controls |
|-------|----------|
| MVP | Tiers + pools + allowlist + no socket |
| 10× | Image signing; egress proxy; GPU reset |
| 100× | Syscall profiles per suite; partner cells |
| 1,000× | Attestation hooks; confidential paths for select tenants |

### 5.12 Interaction with Jenkins matrix (sibling)

- This platform is the **execution fabric**.  
- Jenkins matrix design **explodes combinations** and calls CreateRun with pinned digests/labels.  
- Shared concerns: flake quarantine keys, artifact URLs, device pools—**one SoT each**.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Run state machine + capability matching.  
2. Allocator leases + health gates + fencing.  
3. Privilege tiers / dedicated pools (security).  
4. Results + artifacts + infra-vs-product taxonomy.  
5. Flake detection with env fingerprints.  
6. Scale: cells, HB plane, artifact policy.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Admit/queue, single-cell allocator, T0–T2 pools, health gate, artifacts, basic flake |
| 10× | HA leader, shards, registry mirrors, GPU reset, webhooks |
| 100× | Multi-cell, MIG manager, flake warehouse, partner isolation |
| 1,000× | Hierarchical scheduling, archive, telemetry lake |

### 6.3 Top risks

1. Double-bind on failover.  
2. Privileged tests on shared nodes.  
3. Scheduling onto sick GPUs → CI fire drills.  
4. Artifact/registry bandwidth meltdown.  
5. Flake system blaming tests for infra.  
6. Dual allocators (K8s + custom) fighting.

### 6.4 One-sentence design

> A cell-local, lease-fenced GPU allocator that health-gates devices, runs digest-pinned containers under explicit privilege pools, publishes durable results/artifacts, and scores flakes with infra filtered out—so multi-tenant GPU CI stays correct, secure, and operable from 500 to 500K devices.

---

## 7. Deeper / Related Interview Questions

### 7.1 GPU in containers

**Q: How does a container see a GPU?**  
A: Host driver + NVIDIA container runtime/CDI injects libraries and device nodes; `NVIDIA_VISIBLE_DEVICES` selects UUIDs/MIG.

**Q: Why pin image digests?**  
A: Reproducibility and security; `latest` makes flake forensics impossible.

**Q: Passthrough vs MIG?**  
A: Passthrough = full GPU; MIG = hardware partitions with stronger isolation/density for small tests.

**Q: Can we run graphics APIs headlessly?**  
A: Often yes (EGL/Vulkan); some GL paths need render nodes or display-attached nodes—label them.

### 7.2 Scheduling & leases

**Q: Why not let each agent grab free GPUs?**  
A: Race → double-bind; no global fairness/health. Central CAS lease per cell.

**Q: What is fencing?**  
A: Epoch/lease_id on Start/Complete; stale owners rejected after reclaim.

**Q: Multi-GPU atomicity?**  
A: Bind all devices in one TX or none; never partial start.

**Q: How to avoid sick GPUs?**  
A: Health service state machine; gate before bind; infra-fail mid-run.

### 7.3 Security

**Q: Is `--privileged` required?**  
A: Sometimes for driver bring-up; never default. Dedicated pool + allowlist + audit.

**Q: Biggest multi-tenant risk?**  
A: Host escape and cross-tenant residual GPU state—mitigate with tiers, reset, no socket.

**Q: How to handle partner labs?**  
A: Separate cells/pools; stricter egress; possibly dedicated hardware.

**Q: Image supply chain?**  
A: Signatures, admit-time verify, internal registry, SBOM optional.

### 7.4 Flakes & results

**Q: Fail once—quarantine?**  
A: No. Need sample size; filter infra; fingerprint env.

**Q: Device flaky vs test flaky?**  
A: Separate models: device quarantine from health/Xid; test quarantine from pass_rate.

**Q: Golden image diffs noisy—what then?**  
A: Tolerance, perceptual hashes, quarantine, not silent pass.

**Q: Result webhook retries?**  
A: At-least-once; CI dedupes on `run_id`.

### 7.5 Artifacts & scale

**Q: Store frames in DB?**  
A: No—object storage; DB holds pointers + checksums.

**Q: 2 PB/day artifacts?**  
A: Fail-only heavy dumps; sampling; compression; tiered retention.

**Q: Registry pull storms?**  
A: Mirrors, node caches, warm pools, digest reuse across matrix.

### 7.6 Health & ops

**Q: Xid appears—what’s the platform response?**  
A: Mark device; kill/infra-fail runs; quarantine; page on-call if rate spikes.

**Q: Driver upgrade rolling?**  
A: Drain node; upgrade; canary suite; re-enable; fingerprint changes flake buckets.

**Q: Allocator failover test?**  
A: Kill leader; ensure no double-bind; in-flight agents fence epochs.

### 7.7 Comparison questions

**Q: vs plain Docker + cron on GPU boxes?**  
A: No multi-tenant fairness, health SoT, fencing, flake taxonomy, privilege pools.

**Q: vs Kubernetes + NVIDIA device plugin alone?**  
A: Necessary substrate; still need test result model, flake, privilege pools, CI semantics.

**Q: vs Jenkins label expression only?**  
A: Labels don’t fence devices or health-gate; OK tiny, fails at scale/security.

**Q: Relationship to Jenkins GPU matrix design?**  
A: Matrix expands combinations; this platform executes safely on GPUs.

### 7.8 MIG specifics

**Q: Why static MIG profiles in CI?**  
A: Dynamic reconfig thrash kills stability; static improves predictability.

**Q: Can MIG share with privileged tests?**  
A: Prefer not—privileged pool usually full-GPU dedicated nodes.

### 7.9 Reliability drills

**Q: Agent disk full of dumps?**  
A: Spool quotas; shed; alert; don’t wedge all starts.

**Q: Clock skew on lease expiry?**  
A: Server/allocator time owns truth; agent uses opaque tokens.

**Q: Cancel vs complete race?**  
A: CAS terminal state; first writer wins; loser no-op.

### 7.10 Interview trap: units

**Q: 50K tests × 40 MB = ?**  
A: **2 TB/day**, not 2 PB. 1000× naïve keep-all → **2 PB/day**—hence policy.

**Q: Heartbeat 100K nodes at 1 Hz into one Postgres row-update path?**  
A: Melts—aggregate and shard; don’t OLTP every pulse.

### 7.11 Algorithms & data structures

**Q: Free-device index?**  
A: Per-shard maps/heaps keyed by `(pool, sku, mig, driver_track)` with free counts.

**Q: Fairness?**  
A: Weighted fair queues per project + aging + concurrent caps.

**Q: Flake score?**  
A: Beta-Binomial / Wilson lower bound with min-n gate.

### 7.12 Privilege edge cases

**Q: Test needs to load a kernel module?**  
A: T3 bare-metal / privileged pool only; security review; never shared CI.

**Q: Nested containers?**  
A: Disallow by default; break-glass only.

### 7.13 Multi-region

**Q: Active-active allocators on same devices?**  
A: No—cell single-writer. Gateways may be global; binds are cell-local.

**Q: DR?**  
A: Fail over cell metadata; devices are physical—DR is capacity in another building, not magic sync of GPUs.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- test_runs
(run_id UUID PK,
 project_id UUID,
 test_id TEXT,
 image_digest TEXT,
 privilege_tier INT,
 requirements JSONB,
 state TEXT,
 lease_id UUID NULL,
 device_id TEXT NULL,
 node_id TEXT NULL,
 epoch BIGINT NULL,
 reason_code TEXT,
 created_at, updated_at,
 idempotency_key TEXT,
 UNIQUE(project_id, idempotency_key))

-- devices
(device_id TEXT PK,
 node_id TEXT,
 sku TEXT,
 mig_profile TEXT NULL,
 driver_version TEXT,
 pool TEXT,
 health TEXT,
 lease_run_id UUID NULL,
 epoch BIGINT,
 labels JSONB)

-- results
(run_id UUID PK,
 status TEXT,
 exit_code INT,
 infra BOOLEAN,
 metrics JSONB,
 artifact_manifest_uri TEXT,
 env_fingerprint TEXT,
 finished_at)

-- flake_scores
(test_id TEXT,
 env_fingerprint TEXT,
 passes INT,
 fails INT,
 last_updated,
 state TEXT, -- OK|FLAKY|QUARANTINED
 PRIMARY KEY(test_id, env_fingerprint))

-- audit_events
(id, ts, actor, action, run_id, detail JSONB)
```

### 8.2 API checklist

- [ ] `POST /v1/runs` + Idempotency-Key  
- [ ] `GET /v1/runs/{id}`  
- [ ] `POST /v1/runs/{id}:cancel`  
- [ ] `GET /v1/devices?sku=&pool=&health=`  
- [ ] `POST /v1/devices/{id}:drain` (admin)  
- [ ] `POST /v1/flakes/{test_id}:unquarantine`  
- [ ] Agent: `Heartbeat`, `StartAck`, `Result`, `HealthEvent`  
- [ ] CI webhook: `run.terminal`

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Passthrough | Container bound to full GPU device(s) |
| MIG | Multi-Instance GPU hardware partition |
| Lease / epoch | Fenced ownership of a device for a run |
| Privilege tier | T0–T3 runtime authority level |
| Health gate | Check device healthy before bind |
| Env fingerprint | Hash of SKU/driver/API/OS/MIG for flake buckets |
| Infra failure | Platform/device fault, not test logic fail |
| Privileged pool | Hardware/isolation domain for T2/T3 only |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Allocator + agent + health + artifacts + tiers |
| 10× | HA, shards, mirrors, GPU reset, webhooks |
| 100× | Cells, MIG manager, flake warehouse |
| 1000× | Hierarchical admit, archive, telemetry lake |

### 8.5 Agent protocol sketch

```text
Heartbeat { node_id, devices:[{device_id, health, util, xid_recent}], running:[{run_id, epoch}] }
Start     { run_id, epoch, runtime_spec, artifact_creds }
Kill      { run_id, epoch, reason }
Result    { run_id, epoch, status, exit_code, metrics_ref, artifacts[] }
HealthEv  { device_id, state, code, detail }
```

### 8.6 Runtime spec sketch

```json
{
  "image": "registry/ci/cuda-tests@sha256:…",
  "cmd": ["pytest", "-q"],
  "tier": 1,
  "env": {"NVIDIA_DRIVER_CAPABILITIES": "compute,utility"},
  "devices": ["GPU-uuid-…"],
  "network": "egress-proxy",
  "limits": {"timeout_sec": 1800, "artifact_mb": 2048},
  "scrub_gpu_on_exit": true
}
```

### 8.7 Reason codes (platform)

| Code | Meaning |
|------|---------|
| `NoHealthySku` | No matching healthy device |
| `PrivilegeDenied` | Tier not authorized |
| `ImageNotAllowed` | Digest/signature reject |
| `LeaseFenced` | Stale epoch |
| `XidQuarantine` | Device unhealthy |
| `Timeout` | Wall clock exceeded |
| `FlakeQuarantined` | Test skipped by policy |
| `ArtifactGap` | Result OK, upload incomplete |

### 8.8 Interview “say this” summary (60 seconds)

> Multi-tenant GPU-test fabric: digest-pinned containers scheduled by a cell allocator with **lease epochs**, **health gates**, and **privilege pools** so `--privileged` never lands on shared CI; agents start only after bind; results and artifacts go to durable stores; flakes scored per env fingerprint with infra failures filtered out; scale by sharding queues and cells, not by letting Jenkins pick GPUs.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| Privileged everywhere | Blast radius / escape |
| Dual GPU allocators | Double-bind |
| Quarantine on first fail | Infra noise |
| Artifacts in OLTP | DB melt |
| HB row updates globally | Control plane melt |
| Time-slice untrusted | Isolation lie |
| `latest` tags | Non-reproducible CI |

### 8.10 Reliability test plan

1. Kill allocator leader under load → no double-bind; epochs fence.  
2. Inject Xid → device quarantine; runs INFRA_FAILED; retries elsewhere.  
3. Attempt T2 on shared node → admit/allocator reject.  
4. Agent crash → lease reclaim; late Result rejected.  
5. Object store outage → spool; terminal with ArtifactGap policy.  
6. Cancel vs complete race → single terminal CAS.

### 8.11 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Queue→start (P0, capacity free) | p99 < 30s |
| Infra-fail rate | < 1% runs (steady) |
| False product-fail from sick GPU | ≈ 0 (gated) |
| Artifact upload success (fail path) | > 99% |
| Privileged starts outside pool | **0** |
| Flake quarantine precision | tracked; appeal path |

### 8.12 Related systems map

```text
CI clients → Admit/Quota → Queues → GPU Allocator ← Health Service
                                ↓
                           Node Agents → containers on GPUs
                                ↓
                     Logs + Artifacts + Results → Flake Service
                                ↓
                     Webhooks / Dashboards / Quarantine
```

### 8.13 GPU scrub checklist (between tenants)

```text
[ ] Confirm container exited / cgroup empty
[ ] GPU reset or context clear per policy
[ ] MIG state matches inventory
[ ] Health re-probe
[ ] Return device to free index with epoch++
```

### 8.14 Capacity planning snippet

```text
GPUs needed ≈ peak_concurrency / (target_alloc × mig_density)
If 40% tests MIG-capable at 2× density:
  effective slots = full_gpu_slots × (0.6×1 + 0.4×2)
Provision privileged pool separately (not fungible)
```

### 8.15 Threat model (short STRIDE-ish)

| Threat | Example | Control |
|--------|---------|---------|
| Spoofing | Fake agent | mTLS + attested node identity |
| Tampering | Mutated image | Digest + signature |
| Repudiation | Who started T2? | Audit log |
| Info disclosure | Cross-tenant artifacts | Path ACL + encryption |
| DoS | Submit flood | Quotas + fair share |
| Elevation | Tier confusion | Pool hard filter |

---

*End of dockerized GPU-test platform system design.*
