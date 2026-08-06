# System Design: Jenkins CI for Graphics/GPU Test Matrix

> **Focus areas:** Combinatorial matrix explosion · Sharding · Flake quarantine · Result aggregation · Hardware pool scheduling · Jenkins masters/agents at scale · Caching (images/artifacts/builds) · Driver × OS × GPU × API × branch  
> **Style:** End-to-end CI platform design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic on matrix cardinality, honest Jenkins scaling limits, resolved ownership of “who picks the GPU” vs Jenkins orchestration

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

Goal: **bound the CI product**—what matrix axes exist, which combinations must block merge vs run nightly, how Jenkins scales, and how scarce GPU hardware is scheduled without combinatorial melt-down.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who triggers builds? | PR/gated merge, nightly, release branches, manual redrive | Multiple pipelines with different matrix policies |
| F2 | Matrix axes? | Driver × OS × GPU SKU × API (Vulkan/DX/OpenGL/CUDA) × branch | Explicit axis model + expansion engine |
| F3 | Blocking vs async? | Small smoke matrix gates PR; full matrix nightly/release | Tiered matrices; not all cells blocking |
| F4 | Execution backend? | Jenkins agents + GPU nodes; may call dockerized GPU-test platform | Jenkins orchestrates; device SoT elsewhere ideally |
| F5 | Sharding? | Split huge matrices across agents/time | Shard planner; deterministic cell IDs |
| F6 | Flakes? | Retry, quarantine, don’t block forever on known flakes | Flake service integration; quarantine lanes |
| F7 | Aggregation? | Single PR status from thousands of cells | Hierarchical rollup; reason codes |
| F8 | Hardware pools? | Labeled pools per SKU/OS/API capability | Pool scheduler + queues; avoid label chaos |
| F9 | Caching? | Build caches, container layers, golden assets, ccache | Cache hierarchy per axis locality |
| F10 | Results UX? | Dashboards: which axis failed; compare vs baseline branch | Result warehouse + UI |
| F11 | Multi-branch? | Feature, release, main—different SLAs | Branch policies in matrix compiler |
| F12 | Security? | Credential isolation; privileged GPU jobs gated | Folders/credentials + privileged pools |

**MVP functional scope (lock with interviewer):**

1. Define **matrix spec** (axes + include/exclude + tiers: smoke/full).  
2. **Expand** to cells with stable `cell_id`; apply reduce rules.  
3. Jenkins Pipeline **dynamically schedules** shards onto labeled agents / GPU platform.  
4. Collect junit/logs/artifacts; **aggregate** to pipeline result.  
5. Flake retry (N) + quarantine skip with visibility.  
6. Basic caching: workspace reuse policy, registry pull-through, build cache keys.  
7. Observability: queue wait, cell duration, fail taxonomy (product vs infra).

**Out of MVP:**

- Replacing Jenkins entirely (design hooks for “Jenkins as UI only”)  
- Perfect cross-OS binary reproducibility for every shader  
- Automatic root-cause across all API failures  
- Unlimited blocking matrix on every PR  
- Single monolithic master holding all build records forever hot

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | PR smoke feedback | Fast | p50 < 20 min, p99 < 45 min (smoke tier) |
| N2 | Nightly full matrix completion | Before next nightly | > 99% cells terminal before cutoff |
| N3 | Correct aggregation | No silent skipped fails | Unknown/infra ≠ green |
| N4 | Scale of Jenkins | Masters/agents HA | No single master megabotleneck at 100× |
| N5 | Hardware fairness | Teams don’t starve | Weighted pools / quotas |
| N6 | Flake hygiene | Actionable quarantine | Min sample size; env fingerprint |
| N7 | Durability | Build metadata retained per policy | Hot N days; cold archive |
| N8 | Security | Least privilege agents | Secrets not on GPU logs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. PR opened → smoke matrix (driver_current × OS_LTS × 2 SKUs × CUDA+Vulkan) → all pass → gate green.  
2. Nightly on `main` → full matrix expanded → sharded → agents run → aggregate dashboard.  
3. One cell flakes → auto-retry → pass → mark flaky; pipeline still green per policy.  
4. Release branch → expanded release matrix (more drivers/OS) → blockers must pass.  
5. GPU node unhealthy → cells on that label requeued to healthy pool; infra reason.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Matrix expands to 200K cells | Reject or force reduce; never schedule raw |
| Agent goes offline mid-cell | Reschedule cell; infra retry budget |
| Jenkins master restart | Inflight pipelines resume; durable pipeline + external run SoT |
| Quarantined test was real regression | Quarantine review SLA; axis-aware unquarantine |
| DX cells need Windows agents | Separate OS pools; don’t pretend Linux labels work |
| Cache poison (bad object) | Cache key includes toolchain digest; purge API |
| Fan-in aggregation race | Aggregate only on terminal cell states; lock/version |
| Label mistag (H100 labeled A100) | Capability verify at start; fail infra; alert inventory |
| Privileged driver job on wrong agent | Agent tether + pool allowlist |
| Branch delete mid-matrix | Cancel pending cells; retain artifacts per retention |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| GPU agents / nodes | 200 | 2,000 | 20,000 | 200,000 |
| Jenkins masters (controllers) | 1–2 | 4 | 20 | 100+ (or Jenkins-less exec) |
| Concurrent executors | 500 | 5,000 | 50,000 | 500,000 |
| Pipelines started / day | 2K | 20K | 200K | 2M |
| Matrix cells scheduled / day | 100K | 1M | 10M | 100M |
| Peak cell starts /s | ~5 | ~50 | ~500 | ~5K |
| Avg cell duration | 15 min | 15 min | 10–20 min | 10–20 min |
| Axes cardinality (raw potential) | 5K | 20K | 100K | 500K+ |
| Artifacts / day | 5 TB | 50 TB | 500 TB | 5 PB |
| Active branches with matrices | 50 | 500 | 5K | 50K |
| Distinct cache objects | 1M | 10M | 100M | 1B |

**What each jump forces:**

- **10×:** Controller HA / horizontal masters by org; external build metadata; shard planner service.  
- **100×:** Jenkins as orchestrator client to GPU-test platform; result warehouse; aggressive matrix reduce.  
- **1,000×:** Hierarchical CI (meta-scheduler); controllers federated; most execution API-driven; cold storage everything.

### 1.5 Etc. (Constraints & Assumptions)

- Graphics matrix includes **Windows + Linux** agent OS families.  
- APIs: **Vulkan, DirectX, OpenGL, CUDA** (DX ⇒ Windows).  
- Sibling design: **dockerized GPU-test platform** owns device leases/health; Jenkins should not be GPU SoT at scale.  
- “Green” means **policy-green** (quarantines visible), not “we hid failures.”  
- Combinatorial completeness is a **product myth**—always reduce.

**Scope statement:**

> Design a Jenkins-centered CI system for NVIDIA-style graphics/GPU matrices that expands driver × OS × GPU SKU × API × branch combinations under strict explosion control, shards work across hardware pools, aggregates results with flake quarantine, and scales controllers/agents/caches from lab size to fleet size without lying about green builds or double-booking GPUs.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Matrix cardinality (do the multiply out loud)

```text
Example axes:
  drivers: 5
  OS images: 6
  GPU SKUs: 10
  APIs: 4   (Vulkan, DX, OpenGL, CUDA)
  branches: 3 active policies (but branch is trigger, not always axis)

Raw cells if naïve PR matrix:
5 × 6 × 10 × 4 = 1,200 cells per pipeline

If 2K pipelines/day × 1,200 = 2.4M cells/day → impossible for PR gate

Smoke reduce example:
  drivers: 1 (current)
  OS: 2
  SKU: 3
  API: 2
= 12 cells per PR  → viable
```

**Deal-breaker:** saying “we run the full Cartesian product on every PR” without a hardware miracle.

### 2.2 Split load classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Pipeline starts | ~1/s | ~1K/s | Controllers |
| Cell schedule decisions | ~5/s | ~5K/s | Planner |
| Agent heartbeats / Jenkins protocol | high | extreme | Classic Jenkins pain |
| Result ingest | ~5/s | ~5K/s | Warehouse |
| Artifact bytes | ~500 MB/s peaks | huge | Object store |
| Cache reads | >> result writes | enormous | CDN/caches |

**Critical insight:** Classic Jenkins remoting chatty-ness becomes the bottleneck before GPUs do—plan to **externalize execution**.

### 2.3 Hardware concurrency math

```text
100K cells/day ÷ 86400 ≈ 1.16 cells/s average
Peak ~5/s
Mean duration 15 min = 900s
Concurrency ≈ 1.16 × 900 ≈ 1,040 agent-slots busy average
With utilization 50% scheduling inefficiency → need ~2K GPU executors baseline—or smaller if cells share MIG
```

At **100×** (10M cells/day):

```text
~116 cells/s avg; peak ~500/s
concurrency ≈ 116 × 900 ≈ 100K slots → matches 20K nodes × multi-exec/MIG carefully
```

### 2.4 Controller storage

```text
Per cell metadata ~2–5 KB (without logs)
Baseline 100K cells/day × 5 KB ≈ 500 MB/day metadata
Keep hot 30 days → ~15 GB (fine)

1000×: 100M cells/day × 5 KB ≈ 500 GB/day metadata
→ cannot keep in Jenkins built-in DB; external warehouse + thin controllers
```

### 2.5 Cache hit economics

```text
Cell startup without cache: pull 5 GB image + build 10 min
With warm node cache: start in 30s + test 12 min

If cache hit rate 85% on nightly:
huge reduction in registry fabric and queue time
Cache key must include: toolchain, driver userspace, commit, OS
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Matrix explosion** (schedule impossible Cartesian sets)  
2. **Jenkins controller vertical scale / remoting**  
3. **GPU pool contention** across branches/teams  
4. **False green** from lost shards / mis-aggregation  
5. **Flake thrash** blocking release trains  
6. **Cache stampedes** after toolchain bump  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
MatrixSpec   → axes, includes/excludes, tiers, branch policy
Cell         → single concrete combination + test suite selector
Shard        → group of cells scheduled as one agent unit of work
PipelineRun  → triggered CI execution (PR/nightly/release)
Pool         → hardware domain (sku, os_family, api_capability, privilege)
Aggregation  → rollup tree from cells → pipeline status
FlakePolicy  → retries + quarantine rules per test×env
```

### 3.2 Options: Jenkins topology

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Single fat master | Simple | Melts early | > few K executors |
| B. Master per org + shared agents | Isolation | Agent sprawl | No shared pool efficiency |
| C. Jenkins controllers + **external executor API** | Scales | Two systems | Dual GPU scheduling without SoT |
| D. Jenkins UI only, Tekton/K8s exec | Modern | Migration cost | Interview ignores Jenkins ask |

**Chosen path:**

- **Baseline:** HA Jenkins controller(s) + Kubernetes/EC2 agents with labels.  
- **10×–100×:** **Matrix Planner service** expands/shards; Jenkins Pipeline triggers shards; **GPU-test platform** (sibling) owns device leases.  
- Controllers store pipeline pointers; **Result Warehouse** is SoT for cell outcomes.

**Deal-breaker:** Jenkins label expression as the only GPU mutex.

### 3.3 Matrix explosion control

**Techniques (stack them):**

| Technique | Mechanism | When |
|-----------|-----------|------|
| Tiering | smoke / extended / nightly / release | Always |
| Explicit include lists | Only supported tuples | APIs×OS legality (DX∩Linux=∅) |
| Exclude rules | Skip known invalid | Driver×SKU unsupported |
| Pairwise / combinatorial testing | Cover pairs not full N-wise | Huge axes |
| Diff-driven selection | Run cells touched by change | PR |
| Historical risk | Prefer cells that caught bugs | PR optional |
| Quotas | Max cells per pipeline | Hard cap |
| Time budget | Fill budget with priority cells | Nightly cutoff |
| Branch policy | Release gets more; topic branch less | Always |

**Legality example:**

```text
API=DX        → require os_family=Windows
API=OpenGL    → prefer display or EGL-capable nodes
API=CUDA      → require cuda_capable SKU
driver D on SKU S → allowlist from compatibility DB
```

**Hard cap example:**

```text
PR smoke: max 20 cells
PR extended (optional label): max 100
Nightly: max 5,000 cells (then priority fill)
Release: max 20,000 with multi-day wave
```

### 3.4 Cell identity & determinism

```text
cell_id = hash(
  matrix_version,
  driver, os_image, sku, api,
  suite_set, branch_policy_id
)
```

Deterministic IDs enable dedupe, caching, flake fingerprints, and rerun-of-failed.

### 3.5 Sharding strategies

| Strategy | Description | Trade-off |
|----------|-------------|-----------|
| By axis slice | All Vulkan cells shard A | Uneven durations |
| Binpack by ETA | Pack cells to ~target shard minutes | Better util |
| Sticky SKU | Shard stays on one SKU pool | Cache locality |
| Failed-first redrive | Rerun failed cells denser | Faster signal |

```text
Target shard wall time: 30–60 min (balance scheduling overhead vs blast radius)
Too small shards → Jenkins scheduling overhead dominates
Too large → failure loses much work; slower feedback
```

### 3.6 Hardware pool scheduling

```text
Pools keyed by:
  os_family, sku_family, api_capabilities[], driver_track, privilege_tier

Scheduler inputs:
  shard requirements, priority (PR > nightly), project quotas

Prefer:
  call GPU-test platform CreateRun / CreateBatch for GPU cells
  Jenkins agent used for non-GPU orchestration, Windows native, packaging
```

**Ownership:**

| Concern | Owner |
|---------|-------|
| Pipeline graph / gates | Jenkins (+ planner) |
| Device lease / health | GPU-test platform |
| Cell result SoT | Result warehouse |
| Flake quarantine | Flake service |

### 3.7 Flake quarantine in CI

```text
On cell test failure:
  if infra → retry on new device; don’t flake-score product
  if product → retry up to R
  update flake score (test_id × env_fingerprint)
  if QUARANTINED → skip with status Quarantined (visible)
Aggregation policy:
  quarantined ≠ failure for merge gate (configurable)
  release gate may forbid quarantines above threshold
```

### 3.8 Result aggregation

```text
Pipeline status = reduce(cell statuses)
Precedence (example):
  FAIL_PRODUCT > FAIL_INFRA > TIMEOUT > FLAKY_FAIL >
  QUARANTINED > SUCCESS > SKIPPED

PR gate policy example:
  FAIL_PRODUCT → red
  FAIL_INFRA → red or retry-wave (not silent green)
  QUARANTINED → yellow/green with badge
```

**Deal-breaker:** missing shard → green. **Unknown must not be success.**

### 3.9 Jenkins architecture at scale

```text
L1: Controllers (HA pair / multi-controller)
    - Pipeline definitions, credentials (masked), thin run records
L2: Build agents / orchestrator agents (non-GPU)
L3: GPU execution via platform API or specialized GPU agents
L4: Shared services: planner, results, flakes, caches, artifacts
```

**Controller scaling patterns:**

- Split by **folder/org** (driver vs CUDA vs graphics).  
- Externalize logs to ELK/object storage (not controller disk).  
- Use **Jenkins Configuration as Code**; immutable controller images.  
- Cap executors per controller; queue externally if needed.

### 3.10 Caching architecture

| Cache layer | Content | Key material |
|-------------|---------|--------------|
| Registry pull-through | Container images | digest |
| Node image cache | Warm layers on GPU nodes | digest + node pool |
| Compiler/build cache | ccache/sccache objects | toolchain + commit inputs |
| Golden assets CDN | Reference frames | asset_version + api |
| Workspace cache | sparse checkouts | branch + commit (careful dirty) |
| Test binary cache | Built test exes | commit + OS + driver_track |

**Invalidation:** toolchain bump → namespace version prefix; don’t rely on timed TTL alone for correctness.

### 3.11 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Full Cartesian on PR | Never | Hardware finite | “Complete coverage every PR” |
| GPU SoT | External platform | Fencing/health | Jenkins labels only |
| Results SoT | Warehouse | Controller durability | Jenkins remote API as only truth |
| Shard size | 30–60 min | Overhead vs blast radius | 1 cell = 1 pipeline always at 100× |
| Flakes | Stats + visible skip | Honesty | Hide fails |
| Controllers | Multi + thin | Scale | One eternal master |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Git PR / cron / release
           |
           v
  +--------+---------+
  | Jenkins Controller|
  | (Pipeline kickoff)|
  +--------+---------+
           |
           v
  +--------+---------+     +------------------+
  | Matrix Planner   |---->| Compatibility DB |
  | expand/reduce/   |     | driver×sku×api   |
  | shard            |     +------------------+
  +--------+---------+
           |
           +-------------------+
           |                   |
           v                   v
  +--------+--------+   +------+-----------+
  | Shard Queues    |   | Result Warehouse |
  | (priority/pool) |   | + Aggregation    |
  +--------+--------+   +------+-----------+
           |                   ^
           v                   |
  +--------+--------+          |
  | GPU Test Platform|---------+
  | (leases/health)  |  cell results
  +--------+--------+
           |
           v
     GPU / Windows pools
           |
           v
  Artifacts + Caches + Flake Service
           |
           v
  PR status / dashboards / quarantine UI
```

### 4.2 Sequence: PR smoke matrix

```text
PR → Jenkins: Pipeline
Jenkins → Planner: Expand(tier=smoke, commit, touched_paths)
Planner: apply includes/excludes → 12 cells → 3 shards
Jenkins: parallel shard jobs
Each shard → GPU platform: batch runs
Runs finish → Results upsert cells
Aggregator: all terminal → compute gate status
Jenkins: set Git status check (policy-green)
```

### 4.3 Sequence: nightly full with time budget

```text
Cron → Jenkins nightly
Planner: candidate cells 50K → priority score → select top 5K within budget
Shard binpack by SKU sticky
Schedule waves while pools free
Cutoff T+8h: cancel pending; mark incomplete as TIMEOUT_BUDGET (not success)
Dashboard: coverage % of desired matrix
```

### 4.4 Sequence: flake quarantine interaction

```text
Cell fail product → retry → fail
Flake service: pass_rate low, n≥20 → QUARANTINED
Next pipelines: cell skipped Quarantined
Aggregator: PR policy allows; release policy fails if quarantines > N
Owner fixes → unquarantine → back to active
```

### 4.5 Sequence: controller failover

```text
Controller A dies
HA/cold standby or multi-controller routing resumes
Durable pipeline + external cell SoT continue
Agents reconnect
In-flight GPU runs unaffected (platform leases)
Jenkins reconciles shard job state from warehouse
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Unknown/missing cell ≠ SUCCESS | Aggregator default fail-closed for gates |
| R2 | Matrix hard caps enforced | Planner reject/truncate with explicit reason |
| R3 | Illegal tuples never scheduled | Compatibility DB |
| R4 | Infra fails don’t quarantine tests | Reason taxonomy shared with GPU platform |
| R5 | Device double-bind impossible | Platform leases—not Jenkins labels |
| R6 | Credentials not in artifacts | Masking + log scrub + no env dump |
| R7 | Deterministic cell_id | Versioned hash function |
| R8 | Quarantine visible | Status + UI badge |

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| Planner down | No new expands; running shards continue |
| Warehouse down | Buffer results; gates fail-closed if past SLA |
| Controller restart | Resume from durable state + warehouse |
| Pool outage (all H100) | Queue; optionally substitute policy (explicit) |
| Cache poison | Key bump / purge; rebuild |
| Shard agent loss | Requeue remaining cells; don’t mark success |

### 5.2 Scalability

**1×:** One Jenkins + labeled GPU agents; declarative matrix OK for <100 cells.

**10×:** Planner service; multi-controller; external logs; result DB; smoke vs nightly tiers.

**100×:** GPU platform execution; warehouse columnar; pairwise reduce; cache mesh; org-split controllers.

**1,000×:** Federated meta-CI; Jenkins optional for UI; hierarchical aggregation; PB-scale artifact tiering.

**Backpressure:** if GPU queue wait > SLO, shrink PR matrix dynamically (keep highest-risk cells).

### 5.3 Maintainability

- Matrix specs as **code** (YAML/JSON) reviewed in Git.  
- Compatibility DB owned by driver/GPU program with CI canaries.  
- Shadow expansion: show “what would run” without scheduling.  
- Reason codes stable across Jenkins and platform.  
- Chaos drills: kill controller, drain pool, poison cache.

### 5.4 Ownership resolution

| Concern | Owner |
|---------|-------|
| What combinations exist | Matrix spec + compatibility DB |
| What runs on this trigger | Planner (tier/budget/diff) |
| Pipeline orchestration UI | Jenkins |
| Where GPU runs | GPU-test platform allocator |
| Pass/fail truth | Result warehouse |
| Merge gate interpretation | Policy engine (per branch) |
| Flake quarantine | Flake service |

**Contradiction trap:** Pipeline marks SUCCESS because Jenkins stage skipped when agent missing—aggregator must see **intended cell set** vs **observed terminals**.

### 5.5 Axis modeling deep dive

```text
driver_track: {release_r580, release_r570, develop_head, ...}
os_image: {ubuntu22.04, ubuntu24.04, win11_23h2, ...}
sku_family: {GA102, AD102, GH100, ...}  # prefer family + pick concrete pool
api: {VULKAN, DX12, OPENGL, CUDA}
suite: {conformance, functional, stress, power, regress_set}
branch_policy: {pr_smoke, pr_extended, nightly, release}
```

**Include DSL sketch:**

```yaml
tier: smoke
include:
  - driver: r580
    os: [ubuntu22.04, win11_23h2]
    sku: [AD102, GH100]
    api: [VULKAN, CUDA]
exclude:
  - os: ubuntu22.04
    api: DX12
max_cells: 20
```

### 5.6 Diff-driven selection

```text
Change touches:
  vulkan/ → boost Vulkan cells
  cuda/   → boost CUDA cells
  common/ → broader smoke
Risk score = weighted path match + historical fail rate
Fill smoke budget with highest scores under legality
```

### 5.7 Pairwise covering arrays (interview bonus)

When axes large, pairwise (all pairs of values covered) reduces cells from multiplicative to roughly `O(max_axis * sum_others)`.

```text
Rough intuition:
Full: 5×6×10×4 = 1200
Pairwise: often tens–low hundreds depending on constraints
Not perfect for 3-way interaction bugs—use for PR; nightly fuller
```

Say trade-off honestly: pairwise ≠ exhaustive.

### 5.8 Aggregation tree

```text
PipelineRun
  ├─ AxisGroup(api=VULKAN)
  │    ├─ Shard
  │    │    ├─ Cell ...
  │    │    └─ Cell ...
  └─ AxisGroup(api=CUDA)
```

UI drills from red pipeline → worst axis → cell → logs/artifacts.

### 5.9 Jenkins agent design

| Agent type | Role |
|------------|------|
| Orchestrator | Checkout, call planner, fan-out, aggregate |
| Linux GPU | Optional direct exec (MVP); prefer platform |
| Windows GPU | Native DX/GL suites |
| Build farm CPU | Compile test binaries / package |

**Ephemeral agents** preferred; autoscaling groups per pool; idle TTL.

### 5.10 Caching deep dive

**Stampede control after driver drop:**

```text
Pre-warm top N images on pool nodes before enabling matrix wave
Rate-limit simultaneous pulls per rack
Use content-addressed digests exclusively
```

**Correctness vs speed:**

- Speed caches may be best-effort.  
- Correctness artifacts (goldens) versioned immutable.  
- Never cache test **results** as success without running (except explicit quarantine skip).

### 5.11 Security & multi-tenant CI

- Jenkins folders per org; credential domains.  
- PR from forks: reduced secrets; no privileged pool.  
- Log redaction.  
- Artifact ACLs by project.  
- Privileged driver jobs: approval + dedicated agents.

### 5.12 Observability

| Dashboard | Metrics |
|-----------|---------|
| Matrix | cells intended/scheduled/terminal; coverage % |
| Pools | queue wait by SKU/OS; unhealthy agents |
| Jenkins | controller CPU/heap; remoting; queue length |
| Gates | PR time-to-green; infra fail % |
| Flakes | quarantine count; reopen rate |
| Cache | hit rate; pull latency; purge events |

### 5.13 Progressive migration off fat Jenkins

| Phase | Pattern |
|-------|---------|
| MVP | Declarative matrix on agents |
| 10× | Planner + warehouse; thin stages |
| 100× | Platform executes GPUs; Jenkins orchestrates |
| 1,000× | Meta-scheduler; Jenkins one UI among clients |

### 5.14 Interaction with dockerized GPU-test platform

- Planner emits cells → platform runs.  
- Share: reason codes, env fingerprints, artifact URLs, quarantine keys.  
- **One** device lease SoT; **one** flake SoT; Jenkins displays.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Axes + legality + **hard caps** (explosion control).  
2. Tiered matrices (PR smoke vs nightly).  
3. Planner → shards → pools / GPU platform.  
4. Aggregation fail-closed; flake quarantine visible.  
5. Jenkins controllers thin + caches + scale path.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | YAML matrix, includes/excludes, Jenkins parallel, basic retry, junit aggregate |
| 10× | Planner service, warehouse, multi-controller, cache keys |
| 100× | Platform execution, pairwise/diff reduce, pool quotas |
| 1,000× | Federated CI, hierarchical agg, cold archives |

### 6.3 Top risks

1. Cartesian scheduling fantasy.  
2. False green from lost/skipped shards.  
3. Jenkins controller melt / remoting.  
4. Label-only GPU mutex races.  
5. Quarantine hiding real regressions.  
6. Cache poison after toolchain bump.

### 6.4 One-sentence design

> A planner-driven, tiered GPU/graphics matrix CI where Jenkins orchestrates shards under hard combinatorial caps, execution and device health live in a leased GPU platform, results aggregate fail-closed with visible flake quarantine, and controllers/caches scale out so coverage grows without pretending every PR runs the infinite Cartesian product.

---

## 7. Deeper / Related Interview Questions

### 7.1 Matrix explosion

**Q: How many cells is 5×6×10×4?**  
A: **1,200**. Call it out; then reduce for PR.

**Q: How do you cut PR matrix?**  
A: Tiering, includes, legality, diff-risk, hard caps, optional pairwise.

**Q: Is pairwise enough?**  
A: Good PR compromise; nightly/release denser for higher-way bugs.

**Q: What if product demands full matrix on PR?**  
A: Show hardware math; negotiate smoke+async full; or buy absurd capacity.

### 7.2 Jenkins scale

**Q: When does one master die?**  
A: Thousands of busy executors, huge logs on controller disk, chatty remoting—split controllers, externalize logs/results.

**Q: Agents vs cloud executors?**  
A: Ephemeral autoscaled agents per pool; immutable images.

**Q: How HA?**  
A: HA controllers / backup restore RPO; plus external SoT so builds aren’t only on one disk.

**Q: Pipeline durability?**  
A: Durable pipeline + reconcile with warehouse after restart.

### 7.3 Hardware pools

**Q: Labels soup problem?**  
A: Finite typed pools + capability DB; verify at runtime.

**Q: Windows vs Linux?**  
A: Separate pools; DX never on Linux.

**Q: Who binds GPU?**  
A: Platform allocator with leases—not `EXECUTOR_NUMBER` heuristics.

**Q: Noisy team starves others?**  
A: Quotas, weighted fair share, separate P0 PR capacity.

### 7.4 Flakes & aggregation

**Q: Retry thrice—always green?**  
A: No—track flaky; quarantine; release policies stricter.

**Q: Missing results?**  
A: Fail-closed for gates; never invent SUCCESS.

**Q: Infra vs product?**  
A: Shared taxonomy with execution platform; different retry/flake paths.

**Q: Quarantine abuse?**  
A: SLA, max quarantines, owner, expiry, release blockers.

### 7.5 Caching

**Q: What goes in cache key?**  
A: Toolchain digest, OS, commit inputs, driver track—not just branch name.

**Q: Can cache make tests skip?**  
A: Don’t cache “passed” as skip; only inputs/artifacts.

**Q: Stampede after new driver?**  
A: Pre-warm + pull rate limits.

### 7.6 Results & UX

**Q: How do engineers find signal in 5K cells?**  
A: Axis drill-down; top-fail suites; compare to baseline branch.

**Q: Rerun failed only?**  
A: Yes—by cell_id; preserve original pipeline lineage.

**Q: Cross-branch comparison?**  
A: Warehouse queries on env_fingerprint + suite.

### 7.7 Security

**Q: Fork PR wants GPU?**  
A: Restricted secrets; maybe smoke-only CPU; no privileged.

**Q: Secrets in nvidia dumps?**  
A: Scrub; ACL artifacts; careful env.

**Q: Privileged driver CI?**  
A: Dedicated pool; approvals; audit—same as platform tiers.

### 7.8 Comparison questions

**Q: vs GitHub Actions matrix?**  
A: Similar explosion issues; NVIDIA hardware pools + long graphics suites often keep Jenkins/on-prem exec.

**Q: vs Buildkite/TeamCity?**  
A: Same planner/warehouse patterns; Jenkins-specific pain is controller remoting/plugins.

**Q: vs only dockerized platform without Jenkins?**  
A: Possible; Jenkins often remains policy/UI/gate integration—call split of duties.

### 7.9 Algorithms & data structures

**Q: How to binpack shards?**  
A: Greedy pack by ETA into target minutes; sticky SKU constraint.

**Q: Priority queues?**  
A: PR > release > nightly; within tier fair-share projects.

**Q: Compatibility lookup?**  
A: Indexed allowlist `(driver, sku, api, os) → bool` (+ reasons).

### 7.10 Reliability drills

**Q: Controller killed mid-nightly?**  
A: Resume; warehouse shows cell terminals; don’t double-count.

**Q: Planner expands wrong illegal DX/Linux?**  
A: Compatibility gate unit tests; canary expansion.

**Q: Aggregator race?**  
A: Versioned reduce; only finalize when intended set terminal or timeout policy.

### 7.11 Interview trap: units

**Q: 5×6×10×4 = 240?**  
A: **1,200**. Missed factor of 5.

**Q: 100M cells × 5 KB = 500 TB/day?**  
A: **500 GB/day**. 1e8 × 5e3 B = 5e11 B = 500 GB.

### 7.12 Branch policies

**Q: Feature branch vs release?**  
A: Feature: tiny smoke; release: wide matrix + fewer quarantines allowed.

**Q: Stacked PRs duplicate matrices?**  
A: Deduplicate by merge-base + cell_id; cache binaries across.

### 7.13 Sharding edge cases

**Q: One cell takes 4 hours?**  
A: Solo shard; don’t pack behind it; track as duration outlier; maybe split suite.

**Q: Shard partial success?**  
A: Cell-level truth; shard is transport batch only.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- matrix_specs
(spec_id, name, version, yaml, created_by, created_at)

-- pipeline_runs
(run_id UUID PK,
 jenkins_job TEXT,
 branch TEXT,
 commit TEXT,
 tier TEXT,
 intended_cell_count INT,
 status TEXT,
 created_at)

-- cells
(cell_id TEXT,
 run_id UUID,
 driver TEXT,
 os_image TEXT,
 sku TEXT,
 api TEXT,
 suite_set TEXT,
 shard_id TEXT,
 status TEXT,
 infra BOOLEAN,
 attempt INT,
 artifact_uri TEXT,
 started_at, finished_at,
 PRIMARY KEY(run_id, cell_id))

-- shards
(shard_id TEXT PK,
 run_id UUID,
 pool TEXT,
 eta_sec INT,
 status TEXT)

-- compatibility
(driver TEXT, sku TEXT, api TEXT, os_image TEXT,
 allowed BOOLEAN, reason TEXT,
 PRIMARY KEY(driver, sku, api, os_image))

-- quarantines
(test_id TEXT, env_fingerprint TEXT, state TEXT,
 owner TEXT, expires_at)
```

### 8.2 API checklist

- [ ] `POST /planner/expand` → cells + shards  
- [ ] `POST /planner/shadow` → what-if  
- [ ] `POST /results/cells:batchUpsert`  
- [ ] `GET /results/pipelines/{id}/aggregate`  
- [ ] `POST /flakes/quarantine` / unquarantine  
- [ ] Jenkins shared lib: `runMatrixTier(tier)`  
- [ ] Admin: `POST /caches/purge`  
- [ ] Admin: `POST /pools/{id}:drain`

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Cell | One concrete matrix combination execution unit |
| Shard | Batched cells for scheduling efficiency |
| Tier | smoke/extended/nightly/release matrix policy |
| Compatibility DB | Allowlist of legal axis tuples |
| Fail-closed | Missing/unknown results fail the gate |
| Env fingerprint | Hash for flake bucket (sku/driver/api/os) |
| Controller | Jenkins master process |
| Pool | Hardware domain with capabilities |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Declarative matrix + labels + junit |
| 10× | Planner caps, warehouse, HA controller, caches |
| 100× | Platform GPU exec, diff/pairwise, multi-controller |
| 1000× | Federated meta-CI, hierarchical agg, archive |

### 8.5 Matrix YAML example

```yaml
name: graphics-gpu
version: 3
tiers:
  smoke:
    max_cells: 20
    include:
      - driver: [r580]
        os: [ubuntu22.04, win11_23h2]
        sku: [AD102, GH100]
        api: [VULKAN, CUDA]
    exclude:
      - os: ubuntu22.04
        api: DX12
  nightly:
    max_cells: 5000
    strategy: priority_fill
    include_ref: full_allowlist_v3
```

### 8.6 Aggregation policy examples

```text
PR:
  red if any FAIL_PRODUCT
  red if FAIL_INFRA after retry budget exhausted
  green with badge if only QUARANTINED/SUCCESS/SKIPPED

Release:
  red if FAIL_PRODUCT
  red if quarantined_cells > 10
  red if coverage < 95% of intended release set
```

### 8.7 Interview “say this” summary (60 seconds)

> Graphics/GPU CI is a **combinatorial** problem: never schedule the raw Cartesian product on PRs—tier, legality-filter, diff-prioritize, and hard-cap. Jenkins orchestrates shards; a planner expands matrices; a GPU platform owns leases/health; a warehouse aggregates **fail-closed**; flakes quarantine visibly; controllers stay thin with externalized logs/results; caches key on digests to survive scale.

### 8.8 Extra traps

| Trap | Pushback |
|------|----------|
| Full Cartesian every PR | Hardware math |
| Labels as GPU locks | Races / no health |
| Missing shard = green | Fail-closed |
| Quarantine forever silent | Visible + SLA |
| All logs on controller disk | Melts masters |
| Cache key = branch name | Poison / wrong hits |
| 5×6×10×4=240 | **1200** |

### 8.9 Reliability test plan

1. Kill Jenkins controller mid-run → reconcile from warehouse; no false green.  
2. Drop agent mid-shard → cells requeue; statuses infra.  
3. Expand illegal DX+Linux → planner rejects.  
4. Exceed max_cells → truncate with explicit incomplete policy for nightly; reject for PR.  
5. Cache poison → purge by prefix; correctness restored.  
6. Quarantine hiding fail → release policy blocks.

### 8.10 Observability SLOs

| SLO | Example target |
|-----|----------------|
| PR smoke time-to-signal | p99 < 45 min |
| Intended cells terminal (nightly) | > 99% by cutoff |
| False green rate | ≈ 0 (monitored) |
| Infra-fail rate | < 2% cells steady |
| Cache hit rate (top images) | > 85% |
| Controller p99 API | healthy thresholds |

### 8.11 Related systems map

```text
Git → Jenkins Controller → Matrix Planner → Shard Queues
                               ↓
                     GPU Test Platform / Windows pools
                               ↓
                     Results Warehouse → Aggregator → PR Gate
                               ↓
                     Flake Service / Artifacts / Caches
```

### 8.12 Shard binpack pseudocode

```text
cells = expand(spec)
cells = sort_by(priority desc, eta desc)
shards = []
for cell in cells:
  if legal(cell) and fits_budget(cell):
    place into shard with same pool and remaining_time >= eta
    else open new shard(pool)
return shards
```

### 8.13 Compatibility examples

| driver | sku | api | os | allowed | reason |
|--------|-----|-----|----|---------|--------|
| r580 | GH100 | CUDA | ubuntu22.04 | Y | |
| r580 | GH100 | DX12 | ubuntu22.04 | N | DX requires Windows |
| r570 | AD102 | VULKAN | win11 | Y | |
| r570 | obsolete_sku | CUDA | ubuntu22.04 | N | SKU EOL |

### 8.14 Controller sizing sketch

```text
Rule of thumb (order-of-magnitude):
  Keep concurrent heavy pipelines per controller in hundreds not tens of thousands
  Externalize: logs, artifacts, cell results, agent cloud creds rotation
  Split: graphics-windows / cuda-linux / driver-bringup folders → controllers
```

### 8.15 Cache key examples

```text
image_cache:     sha256(image_digest)
build_cache:     sha256(toolchain_digest + os + commit_tree_id + define_flags)
golden_cache:    sha256(asset_version + api + sku_family)
flake_bucket:    sha256(sku_family + driver_major + api + os_image + mig_mode)
```

### 8.16 Cell status taxonomy

| Status | Gate meaning (PR default) |
|--------|---------------------------|
| SUCCESS | OK |
| FAIL_PRODUCT | Red |
| FAIL_INFRA | Retry then red |
| TIMEOUT | Red (or infra retry) |
| FLAKY_FAIL | Red or quarantine path |
| QUARANTINED | Badge; policy green |
| SKIPPED | Neutral if planned skip |
| UNKNOWN | **Red** (fail-closed) |

### 8.17 Capacity planning snippet

```text
GPU_executors_needed ≈
  (cells_per_day × avg_duration_sec) / 86400 / target_utilization

PR_capacity_reserve:
  keep 20–30% of interactive pools for P0 smoke
Nightly uses scavenger capacity + reserved windows
```

### 8.18 Plugin / shared-library guidance

```text
Prefer thin Jenkinsfile + shared library calling Planner/Platform APIs
Avoid plugin sprawl that stores huge state on controller
Pin plugin versions; immutable controller images
```

### 8.19 Windows graphics notes

```text
DX/OpenGL often need:
  GPU-attached Windows agents
  graphics driver install bake-in
  session/desktop considerations for some GL paths
  separate caching (AMI bake vs docker layers)
Don’t force-fit into Linux container matrix blindly
```

### 8.20 Final trap table (quick scan)

| Trap | Correct stance |
|------|----------------|
| Infinite matrix | Caps + tiers |
| Jenkins owns GPUs | Platform leases |
| Green on silence | Fail-closed |
| One master forever | Federate/thin |
| Hide flakes | Visible quarantine |
| Arithmetic slip | 5×6×10×4=**1200**; 1e8×5KB=**500GB**/day |

---

*End of Jenkins GPU test matrix system design.*
