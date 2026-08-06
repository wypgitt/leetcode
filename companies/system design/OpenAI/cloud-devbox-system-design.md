# System Design: Cloud DevBox

> **Focus areas:** Isolation (VM/container/microVM) · Home volume persistence · Prebuilds · IDE remote · Hibernation · Secrets · CI integration · Noisy neighbor · Cold start  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar load classes, explicit invariants, resolved ownership of box lifecycle vs volume vs network

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

Goal: **bound the product**—what a “DevBox” is (remote IDE environment), what persists across stop/hibernate, and at which concurrency the design must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are the users? | Individual developers + teams; multi-tenant SaaS | Everything keyed by `org_id` / `user_id` / `project_id` from day 1 |
| F2 | What is a DevBox? | Isolated remote compute with filesystem, shell, ports, IDE (VS Code Remote / browser IDE) | Box = lifecycle + attachable **home/workspace volume** + network policy |
| F3 | Isolation level? | Strong isolation preferred (microVM / Firecracker or equivalent); containers OK for MVP if honest about threat model | Isolation choice is a **deal-breaker** for untrusted code |
| F4 | Persistence? | Source + home dir survive stop; optional ephemeral scratch; rebuild from snapshot/prebuild | Separate **compute** from **durable volume**; never treat box disk as sole SoT |
| F5 | Prebuilds? | Warm images with deps installed from Dockerfile / repo config | Prebuild pipeline + snapshot catalog; cold start vs warm pool trade-off |
| F6 | IDE experience? | VS Code Remote / browser VS Code–compatible; terminal + port forward | Gateway for SSH/agent + HTTP/WS reverse proxy for IDE |
| F7 | Start / stop / hibernate? | Start, stop (release CPU/RAM), hibernate (snapshot memory optional), auto-idle timeout | Distinct states; cost model differs; hibernate ≠ stop |
| F8 | Secrets? | Inject git tokens, cloud creds, env secrets without baking into image | Short-lived injection at start; vault + agent; never log secret values |
| F9 | Network egress? | Controllable egress; block SSRF to metadata; allow package registries | Egress proxy / security groups + DNS policy |
| F10 | CI integration? | Optional: “Open in DevBox” from PR; run same image as CI | Share image/prebuild artifact store with CI; don’t couple control planes |
| F11 | Collaboration? | MVP single-user; pair later | Sticky ownership; later: shared session with ACL |
| F12 | Multi-region? | Boxes near user or near data; org policy | Regional pools; home region for metadata; volume region affinity |

**MVP functional scope (lock with interviewer):**

1. Create / start / stop / delete DevBoxes from a project template (image + resources + volume size).
2. **Persistent workspace volume** mounted at home/workspace; survives stop/restart.
3. Connect via **IDE agent** (SSH or proprietary) + browser terminal; port forwarding for app preview.
4. **Prebuild** from repo Dockerfile / `.devbox.json`; store snapshot/image.
5. Idle auto-stop; optional hibernate Phase 1.5.
6. Secrets injection at start; egress allowlist baseline.
7. Org quotas: concurrent boxes, CPU/RAM hours, disk.

**Out of MVP (explicitly defer):**

- Multi-user live share / collaborative editing
- GPU training clusters (design hooks: accelerator SKUs)
- Nested Docker-in-Docker without privileged isolation story
- Perfect zero cold-start for arbitrary custom images
- Cross-cloud live migration of running boxes

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-shell (warm prebuild)? | Feels like local open | p50 < 10s, p99 < 30s warm; cold image pull separate SLO |
| N2 | Time-to-IDE ready? | Usable editor | p50 < 20s warm (agent + volume attach) |
| N3 | Durability of workspace? | No lost files after ACK’d write to volume | Volume replicated (AZ); RPO ≈ 0 for committed FS; snapshot RPO minutes for DR |
| N4 | Isolation? | Untrusted code must not escape / steal neighbor | Hardware virtualization preferred; noisy-neighbor CPU/IO caps |
| N5 | Availability (control plane)? | Create/start APIs | 99.9%; box runtime depends on AZ capacity |
| N6 | Security? | Secrets never in image layers; metadata IP blocked | Vault + IMDSv2-style denial; audit start/stop |
| N7 | Cost efficiency? | Idle boxes should not burn full VM cost | Auto-stop; hibernate trade-off; preemptible pools for prebuilds |
| N8 | Fairness? | One org cannot starve pool | Quotas + weighted scheduling of starts |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User creates DevBox from template → prebuild hit → volume attach → agent start → IDE connects → code/edit/run.
2. Idle 30m → auto-stop → volume retained → user Start → resume in tens of seconds.
3. Prebuild on push to `main` → new snapshot → next Create uses latest.
4. Port forward `3000` → preview URL with auth token.
5. Inject `GITHUB_TOKEN` at start → `git push` works; token rotated next start.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cold start / image miss | Pull + create; show progress; don’t pretend warm SLO |
| Volume attach timeout | Fail start with retry; don’t orphan half-mounted box |
| Host failure while running | Mark box `unhealthy`; recover volume; may lose unsynced RAM; FS durable if volume external |
| Hibernate OOM / disk full for snapshot | Fall back to stop; notify user |
| Secret revoked mid-session | Next inject fails; optional agent refresh; don’t rewrite history in image |
| Noisy neighbor IO | cgroup/IO throttle; migrate offender; isolate noisy SKUs |
| Concurrent Start spam | Idempotent start; single lease on box_id |
| Org hits concurrent quota | Queue or reject with clear error; fairness across projects |
| Egress to `169.254.169.254` | Blocked at network policy |
| Delete box | Soft-delete volume per retention; hard purge after TTL |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Orgs | 1K | 10K | 100K | 1M |
| Registered developers | 50K | 500K | 5M | 50M |
| Peak **concurrent running** boxes | 5K | 50K | 500K | 5M |
| Peak **concurrent stopped** (volume retained) | 40K | 400K | 4M | 40M |
| Creates / starts / day | 20K | 200K | 2M | 20M |
| Peak start QPS | ~5 | ~50 | ~500 | ~5K |
| Prebuild jobs / day | 5K | 50K | 500K | 5M |
| Avg workspace volume | 20 GB | 20 GB | 30 GB | 40 GB |
| Peak egress (blended) | ~10 Gbps | ~100 Gbps | ~1 Tbps | ~10 Tbps |
| Control-plane API QPS (mixed) | ~200 | ~2K | ~20K | ~200K |

**What each jump forces:**

- **10×:** Warm pools per popular image; dedicated volume attach path; regional pools; Redis for leases/quotas.
- **100×:** Cell by region+SKU; snapshot GC; prebuild cache hierarchy; fair start queues; host packing optimizer.
- **1,000×:** Global directory for box placement; multi-region volume strategy (or pin workspace region); microVM fleet automation; capacity forecasting; idle/hibernate economics as first-class product.

### 1.5 Etc. (Constraints & Assumptions)

- **Primary cloud**, multi-AZ; boxes are regional resources.
- **We do not invent a new editor**—integrate VS Code Remote / openvscode-server / similar.
- **Untrusted workloads** assumed (user code runs arbitrary binaries).
- **CI** is a sibling product that may share image registry—not the same scheduler as DevBox starts.
- **Billing:** vCPU-hour + GB-month volume + egress; hibernate billed differently from stop.

**Scope statement:**

> Design a Cloud DevBox platform: isolated remote developer environments with persistent volumes, prebuilds, IDE connectivity, secrets injection, egress controls, and stop/hibernate lifecycle—starting at ~5K concurrent running boxes and evolving through 10× / 100× / 1,000× with warm pools, fair start queues, and cell-based capacity.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump “QPS”)

| Load class | What | Baseline peak | 1,000× | Store / plane |
|------------|------|---------------|--------|---------------|
| **Control-plane API** | CRUD boxes, list, connect tokens | ~200/s | ~200K/s → shard/cells | API + Postgres |
| **Start/stop transitions** | Orchestrate VM/microVM + volume | ~5/s | ~5K/s | Orchestrator + queue |
| **Agent heartbeats** | Liveness / metrics from boxes | ~5K/s (1/s each) | ~5M/s | Ingest pipeline / Redis |
| **IDE / SSH sessions** | Long-lived connections | ~5K | ~5M | Gateway fleet |
| **Volume IOPS** (blended) | Dev FS | highly skewed | extreme | Storage plane |
| **Prebuild CI-like jobs** | Image builds | bursty | fleet of builders | Build workers |

**Anti-pattern:** “We have 5K QPS” mixing heartbeats with starts. Interviewers will ask you to split them.

### 2.2 Concurrent capacity

```text
Baseline: 5,000 running boxes
Assume SKU mix: 2 vCPU / 4 GB RAM average
→ 10,000 vCPU, 20 TB RAM reserved (before oversubscribe)

With 20% oversubscribe on CPU (dev idle often): ~8,000 physical vCPU equivalent
Hosts at 64 vCPU: ~125–160 hosts baseline (N+ spare)

1,000×: 5M boxes × 2 vCPU = 10M vCPU → multi-region mega-fleet; packing + hibernate mandatory
```

### 2.3 Storage

```text
Stopped + running volumes retained:
Baseline: 40K volumes × 20 GB = 800 TB logical
+ replication (3×) → ~2.4 PB raw-ish (order; depends on storage tech)

1,000×: 40M × 40 GB = 1.6 EB logical → retention, tiering, GC are existential
```

**Always pair storage estimates with retention / idle GC policy.** Infinite keep of every stopped box at 1,000× is not a serious design.

### 2.4 Cold start vs warm pool

```text
Cold path: schedule host + pull 5 GB image @ 500 MB/s = ~10s pull + boot 2–5s + volume attach 2–5s
          → often 20–60s (p99 higher under contention)

Warm pool: pre-booted microVM with image loaded, waiting for volume attach + user context
          → target 5–15s to shell

Pool cost: 100 warm slots × 2 vCPU = 200 vCPU idle burn — budget explicitly
```

### 2.5 Heartbeat & control chatter

```text
5K boxes × 1 heartbeat/s × 200 B ≈ 1 MB/s — fine
5M boxes × 1/s × 200 B ≈ 1 GB/s — need aggregation, sampling, regional collectors
```

At 1,000×, push metrics through local agents → regional aggregators; do not write every heartbeat to Postgres.

### 2.6 Gateway memory (IDE connections)

```text
Per IDE/SSH connection state: ~50–100 KB
5K conns → ~250–500 MB
5M conns → ~250–500 GB fleet-wide  ← not TB on one box
```

### 2.7 Prebuild burst

```text
Mon morning: 10% of 50K users refresh → 5K prebuild/start surge
At 100 builds concurrent × 10 min = capacity planning problem
Builders should use spot/preemptible + cache layers (registry + buildkit cache)
```

---

## 3. High-Level Design

### 3.1 Product / UX surfaces

```text
+--------------------------------------------------------------------------+
| Cloud DevBox     Project: payments-api     Region: us-east-1    [User]   |
+------------------+-------------------------------------------------------+
| MY BOXES         |  box-7f3a   RUNNING   2vCPU 4GB   vol 42GB            |
| > payments-api   |                                                       |
|   experiment-x   |  [Open in VS Code]  [Browser IDE]  [Stop] [Hibernate] |
|   (stopped)      |                                                       |
|                  |  Ports: 3000 → https://preview.../t/abc               |
| TEMPLATES        |  Prebuild: main@a1b2c3  (2h ago)  HIT                 |
| > Node 20        |                                                       |
| > Python CUDA    |  Terminal                                           |
|                  |  $ npm run dev                                        |
+------------------+-------------------------------------------------------+
```

### 3.2 Domain model

```text
Org
 └── Project
      ├── Template (image ref, resources, env schema, network policy)
      ├── Prebuild (git_sha, snapshot_id, status, created_at)
      └── DevBox
            ├── status: creating|starting|running|stopping|stopped|hibernating|hibernated|deleting|error
            ├── compute_lease (host_id, instance_id, fencing_token)
            ├── volume_id (durable workspace)
            ├── network_policy_id
            ├── agent_endpoint / connect_token
            └── last_active_at
```

**Ownership resolution (critical):**

| Concern | Owner (SoT) | Not owned by |
|---------|-------------|--------------|
| Box desired state / status | Control plane DB | Hypervisor alone |
| Files in workspace | **Volume service** | Ephemeral instance disk |
| Running process memory | Instance (lost on stop; saved on hibernate snapshot) | Volume |
| Image/prebuild bytes | Registry / snapshot store | User volume |
| Secrets values | Vault / secret manager | Image layers, git |
| Network policy | Control plane + data-plane enforcer | IDE client |

**Deal-breaker:** baking user secrets into image or treating instance root disk as durable home.

### 3.3 Lifecycle state machine

```text
          create
            │
            v
        creating ──► stopped ──start──► starting ──► running
                         ▲                  │           │
                         │                  X           │ idle timer / user
                         │                  ▼           │
                         └──── stopping ◄───┴── stop ◄─┘
                                              │
                         hibernate (opt)      │
                         running → hibernating → hibernated → start → starting → running
                                              │
                                           delete → deleting → (tombstone)
```

**Invariants:**

1. Only one **compute lease** with valid fencing token may run for a `box_id`.
2. Volume attach is exclusive to that lease (single writer).
3. `running` is never ACK’d to user before volume mounted + agent healthy (or explicit degraded mode).
4. Stop releases compute; volume remains until delete/GC.
5. Hibernate persists memory snapshot **and** keeps volume; cost ≠ full running.

### 3.4 Isolation options (trade-off table)

| Approach | How | Pros | Cons | Deal-breaker when |
|----------|-----|------|------|-------------------|
| **A. Containers (gVisor/Kata optional)** | Shared kernel or user-space kernel | Fast start, dense packing | Escape/noisy risk higher without Kata/gVisor | Strong multi-tenant untrusted code without extra sandbox |
| **B. Full VMs** | Classic hypervisor VMs | Strong isolation | Slow/cold, expensive, heavy images | Need sub-10s warm start at density |
| **C. microVMs (Firecracker etc.) (chosen)** | Lightweight VMs, minimal device model | Strong isolation + fast boot + good density | Operational complexity; snapshot ecosystem | Team cannot operate snapshot/volume attach plane |
| **D. Remote SSH to shared hosts** | Users on big boxes | Simple | Isolation/noise disaster | Multi-tenant SaaS |

**Choice: microVM (Firecracker-class) for multi-tenant untrusted code**; containers acceptable for **trusted enterprise VPC / single-tenant** MVP if stated explicitly.

```text
Host (metal / large VM)
  └── Jailer / VMM
        └── microVM
              ├── vCPU / mem cgroup caps
              ├── virtio-blk → workspace volume
              ├── virtio-net → egress policy ENI / tap
              └── agent (IDE + metrics)
```

### 3.5 Persistence: volumes & snapshots

```text
Registry (images/prebuilds)
        │
        ▼
   Snapshot / rootfs layers  ──clone──►  Ephemeral root (optional)
        │
        └──► Workspace Volume (durable, per box)
                 ├── /home/user / workspace
                 ├── survives stop
                 └── snapshotted for DR / clone box
```

| Operation | Behavior |
|-----------|----------|
| Create box | Allocate volume (empty or from template snapshot) |
| Start | Attach volume RW exclusive |
| Stop | Detach; keep volume |
| Hibernate | Pause VM + snapshot memory to object store; volume stays |
| Clone box | New volume from snapshot; new box_id |
| Delete | Schedule volume GC after retention |

### 3.6 Prebuilds

```text
git push → Prebuild Worker
  1. checkout sha
  2. build image (Dockerfile / nix / pack)
  3. optionally run bootstrap (npm i, etc.)
  4. snapshot filesystem / push image tags
  5. register Prebuild{project, sha, digest, status}
```

**Hit path:** Create/Start resolves `prebuild_id` or `image@digest` → schedule with warm pool keyed by digest.

**Miss path:** build async or fallback base image + in-box setup (slow; product must show why).

### 3.7 IDE / connectivity

```text
Developer IDE
    │ SSH / tunnel
    v
Edge Gateway (authn, rate limit)
    │ mTLS / private path
    v
Box Agent (openvscode / sshd)
    └── port-forward sidecar → Preview Gateway (signed URLs)
```

**Connect token:** short-lived JWT/capability bound to `box_id` + `user_id`; rotate on each Open; revoke on stop.

### 3.8 Network egress controls

| Control | Mechanism |
|---------|-----------|
| Deny link-local / metadata | Security group + iptables/nft + DNS sinkhole |
| Allow package registries | Egress proxy allowlist (npm, pypi, docker, github) |
| User custom allow | Org policy → regenerate ENI rules on start |
| Ingress | Default deny public; only gateway + preview with auth |
| SSRF from user code | Egress proxy; no direct IMDS |

### 3.9 Secrets injection

```text
Start box:
  1. Control plane requests short-lived secrets from Vault (TTL 1h–12h)
  2. Deliver over attested channel to agent (not cloud-init logs)
  3. Agent exposes via env / file with 0600 / systemd credential
  4. On stop: secrets wiped with instance; next start re-fetches
```

**Never:** bake into image, commit to volume by platform (user may still write them—educate + scan optional).

### 3.10 Hibernation vs stop

| | Stop | Hibernate |
|---|------|-----------|
| CPU/RAM | Released | Released after snapshot; snapshot stored |
| Volume | Kept | Kept |
| Resume time | Boot + agent (warm image helps) | Restore memory snapshot (can be faster for heavy IDE state) |
| Cost | Volume + tiny metadata | Volume + snapshot storage (+ restore bandwidth) |
| Failure mode | Clean | Snapshot fail → degrade to stop |

**Product default:** auto-**stop** on idle; hibernate opt-in for “keep IDE state” SKUs.

### 3.11 CI integration

- Shared **image digest** between CI and DevBox templates (“same bits you tested”).
- “Open PR in DevBox”: create box from PR sha prebuild; inject read-only git credentials.
- Do **not** run CI jobs on interactive DevBox hosts (noise + security); separate runner pools (see Actions design if asked).

### 3.12 High-level component trade-offs

| Component | Option A | Option B | Choice |
|-----------|----------|----------|--------|
| Orchestrator | Kubernetes custom controllers | Dedicated box orchestrator + queue | **B** at scale; K8s OK for control plane services, not necessarily for tenant microVMs |
| Volume | Cloud block volumes | Distributed FS (e.g. custom) | **Cloud block / CSI-like** MVP; custom only at extreme |
| Warm pool | Per-digest pools | Generic empty VMs | Per-digest for popular; generic fallback |
| Metadata DB | Postgres | Dynamo | **Postgres** + cell sharding |
| Placement | Bin-pack dense | Spread for reliability | Soft packing with anti-affinity for noisy |

---

## 4. Architecture Diagram

### 4.1 Control + data plane

```text
                     +---------------------------+
                     | IDE / Browser / CLI       |
                     +-------------+-------------+
                                   | HTTPS / SSH
                     +-------------v-------------+
                     | Edge: Auth + Connect GW   |
                     +------+----------+---------+
                            |          |
              +-------------v--+    +--v----------------+
              | API / Control  |    | Preview Gateway   |
              | (boxes CRUD,   |    | (signed URLs)     |
              |  quotas)       |    +-------------------+
              +--------+-------+
                       |
         +-------------+-------------+
         v                           v
+----------------+          +----------------+
| Postgres       |          | Redis          |
| boxes, volumes |          | leases, quotas |
| templates      |          | warm pool idx  |
+--------+-------+          +--------+-------+
         |                           |
         v                           v
+----------------+          +----------------+
| Orchestrator   |<-------->| Start Queue    |
| (FSM + place)  |          | (fair/tenant)  |
+--------+-------+          +----------------+
         |
         v
+----------------+     +------------------+     +----------------+
| Host Agent     |---->| microVM + Agent  |---->| Volume Attach  |
| (VMM, cgroups) |     | (user workload)  |     | Service        |
+----------------+     +--------+---------+     +--------+-------+
                                |                        |
                                v                        v
                       +----------------+       +----------------+
                       | Egress Proxy   |       | Block Storage  |
                       +----------------+       +----------------+

+----------------+     +----------------+
| Prebuild Workers|-->| Image Registry |
+----------------+     +----------------+
| Vault / Secrets |
+----------------+
```

### 4.2 Start sequence

```text
User                API               Orchestrator         Host/VMM          Volume
 |--Start(box)------>|                     |                  |                |
 |                   |--authz+quota------->|                  |                |
 |                   |--enqueue start----->|                  |                |
 |                   |<--202 accepted------|                  |                |
 |                   |                     |--place host----->|                |
 |                   |                     |--attach vol----------------------->|
 |                   |                     |<-------------attached-------------|
 |                   |                     |--boot microVM--->|                |
 |                   |                     |--inject secrets->|                |
 |                   |                     |<--agent ready----|                |
 |                   |<--status=running----|                  |                |
 |--Connect token--->|                     |                  |                |
 |======= SSH/IDE tunnel to agent ===========================================>|
```

### 4.3 Idle stop sequence

```text
Agent --heartbeat idle--> Ingest --> Orchestrator
Orchestrator --Stop--> Host: graceful agent shutdown → detach volume → destroy microVM
DB: status=stopped; compute_lease cleared; volume retained
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No double-running box:** lease + fencing token; old host fenced on reclaim.
2. **Volume single-writer:** attach API enforces; split-brain attach is a Sev-1.
3. **Durable before “Running”:** volume attached + agent health check passed.
4. **Stop is idempotent;** delete is soft then hard.
5. **Secrets not in logs/images.**
6. **Control plane down ≠ data loss:** running boxes continue until lease expiry policy; new starts fail closed on quota/lease store if required.
7. **Prebuild immutability:** digest-addressed; non-reproducible “latest” not used for billing forensics.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Host death | Detect via agent miss; fence; volume recover; box → error/stopped; user can Start |
| Redis down | Fail closed on new starts (quota/lease); running boxes keep; degrade warm pool index |
| Postgres primary down | Fail closed control plane; promote; in-flight FSMs reconcile |
| Registry brownout | Warm pool helps; cold starts queue; communicate degraded |
| Vault down | Cannot start new boxes needing secrets; running unaffected |

### 5.2 Scalability

**Placement & packing**

```text
score(host) = remaining_cpu, remaining_mem, remaining_disk_attach_slots,
              image_locality (digest cached), failure_domain, tenant_spread
```

**Fair start queue**

```text
per_org concurrent_starts_cap
global queue with weighted fair dequeue (org credit)
prevent thundering herd Monday 9am
```

**Progressive scale**

| Scale | Change |
|-------|--------|
| 1× | Single region, Postgres, Redis, microVM hosts, volume attach, basic prebuild |
| 10× | Warm pools; fair queues; read replicas; regional registry mirrors |
| 100× | Cells (region×SKU); snapshot GC; heartbeat aggregators; noisy-neighbor SKUs |
| 1,000× | Global placement directory; hibernate economics; volume tiering; capacity ML forecasts |

**Noisy neighbor**

- Hard cgroup CPU/mem/IO limits per microVM.
- Network egress bandwidth caps.
- Detect IO/CPU steal; live-migrate or force-stop offenders.
- Separate host pools: `interactive` vs `prebuild` vs `quarantine`.

### 5.3 Maintainability

- Box FSM is pure in orchestrator; host agent is dumb executor (idempotent verbs: boot/kill/attach).
- Image digests + SBOM for supply chain.
- Chaos: kill host, partition vault, registry 500s.
- Metrics: time-to-shell, attach latency, pool hit rate, start queue wait, escape alerts (none expected), volume error rate.
- Avoid high-cardinality Prometheus labels (`box_id`); use traces.

### 5.4 Cold start breakdown

| Phase | Warm hit | Cold miss |
|-------|----------|-----------|
| Schedule | ~100ms | ~100ms–2s under queue |
| Image | 0 (pooled) | seconds–minutes |
| Boot microVM | ~100–500ms | ~1–3s |
| Volume attach | ~1–5s | ~1–5s |
| Agent + IDE | ~1–5s | ~1–5s |
| **Total** | **~5–15s** | **~20s–several min** |

### 5.5 Security deep dive

- Jailer + seccomp + minimal devices on Firecracker-class VMM.
- No nested default privileged Docker; if DinD required → separate heavier VM SKU.
- Preview URLs: unguessable token + optional SSO.
- Audit: create/start/stop/delete/secret_access (metadata only).
- Tenant isolation tests continuous (network reachability probes).

---

## 6. Wrap-Up

### 6.1 What we designed

A **Cloud DevBox** platform: microVM-isolated remote environments, durable workspace volumes, prebuild snapshots, IDE/SSH connectivity via edge gateways, vault-injected secrets, egress controls, and stop/hibernate lifecycle with fair start queues and warm pools—scaled from 5K → 5M concurrent boxes via cells and capacity discipline.

### 6.2 Key decisions worth defending

1. **Compute ≠ volume** — persistence ownership is the volume service.  
2. **microVM isolation** for multi-tenant untrusted code.  
3. **Warm pools keyed by image digest** for time-to-shell SLO.  
4. **Lease + fencing** prevents double-running / double-attach.  
5. **Stop default, hibernate opt-in** — honest cost/UX trade-off.  
6. **Secrets short-lived at start**, never in images.  
7. **Split load classes** in estimates (starts vs heartbeats vs IDE conns).  
8. **Fair queues + org quotas** beat naïve FIFO under Monday storms.  
9. **CI shares digests, not hosts.**  
10. **Storage estimates include retention/GC** or 1,000× is fantasy.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Volume attach latency | Parallelize, local NVMe cache, snapshot warm |
| Pool waste | Adaptive pool sizing by hit rate / time-of-day |
| Hibernate restore failures | Automatic fallback to stop + notify |
| EB-scale volumes | Aggressive GC, tiering, per-org caps |
| Escape vulnerabilities | Bug bounty, minimal device model, rapid host drain |

### 6.4 How to present in 45 minutes

1. Requirements + isolation threat model (7 min)  
2. Numbers with split load classes + storage (5 min)  
3. Domain + FSM + volume ownership (8 min)  
4. Start sequence + warm pool (8 min)  
5. Reliability invariants + noisy neighbor (7 min)  
6. Scale/cells (5 min)  
7. Q&A (remaining)

---

## 7. Deeper / Related Interview Questions

### 7.1 Isolation & security

**Q: Why not plain Docker for DevBoxes?**  
A: Shared-kernel multi-tenant with arbitrary user code is a hard threat model. Prefer microVMs; if containers, add gVisor/Kata and be honest about residual risk.

**Q: How do you block cloud metadata SSRF?**  
A: Network policy deny to link-local; force egress via proxy; no host IMDS credentials in guest.

**Q: DinD needed for some users?**  
A: Separate SKU with stronger VM isolation and clear pricing; not default dense pool.

**Q: How are secrets kept out of images?**  
A: Build without secrets; inject at runtime via vault; scan registry optional; educate users about writing secrets to disk.

### 7.2 Lifecycle & persistence

**Q: What survives stop?**  
A: Volume contents + metadata. Not RAM, not ephemeral scratch, not injected env secrets.

**Q: Hibernate vs snapshot volume?**  
A: Volume snapshot = filesystem point-in-time. Hibernate = memory+CPU state for faster IDE resume. Different products.

**Q: Host dies mid-write?**  
A: Depends on volume durability (cloud block replication). Acknowledge possible torn writes at app level; fsck/journalled FS helps.

**Q: Can two regions attach one volume?**  
A: No—single-writer affinity. Cross-region = replicate/migrate volume, not dual attach.

### 7.3 Performance & cold start

**Q: How do you get <10s to shell?**  
A: Warm pool of booted microVMs with image layers local; attach volume; inject secrets; skip image pull.

**Q: Pool hit rate low?**  
A: Narrow SKU×digest matrix; predictive pools for org favorites; accept cold for long-tail images.

**Q: Huge monorepo volume?**  
A: Sparse checkout, overlay mounts, lazy remote FS Phase 2; MVP size quotas.

### 7.4 Scheduling & fairness

**Q: Monday 9am stampede?**  
A: Weighted fair queue; per-org start concurrency; warm pool; UX queue position.

**Q: Packing vs noisy neighbor?**  
A: Soft pack interactive; hard isolate known-heavy; migrate on steal metrics.

**Q: Preempt prebuild for interactive?**  
A: Yes—prebuild on spot/interruptible pools; interactive has priority.

### 7.5 IDE & networking

**Q: Sticky sessions?**  
A: Connect gateway routes by `box_id` → host/agent; sticky optional. Authz every connect.

**Q: Port preview security?**  
A: Signed URL TTL; optional SSO; default no public bind on `0.0.0.0` without opt-in.

**Q: SSH vs reverse tunnel?**  
A: Either; reverse tunnel avoids inbound to host fleet; enterprise may prefer private link.

### 7.6 CI integration

**Q: Reuse GitHub Actions runners for DevBoxes?**  
A: Share image digests/cache; separate pools and threat models (interactive vs ephemeral CI).

**Q: Reproduce CI failure in DevBox?**  
A: Same digest + env schema + checkout sha; not necessarily same kernel modules—document diffs.

### 7.7 Multi-region & DR

**Q: User travels?**  
A: Create box in nearest region with empty volume, or accept latency to home volume region; migrating volumes is explicit.

**Q: Region loss?**  
A: Volume snapshots cross-region async; RPO minutes–hours; control plane DR runbook; users recreate from snapshot.

### 7.8 Algorithms & structures

**Q: Placement data structure?**  
A: Per-cell free-resource heaps / segment trees; image locality map digest→hosts; consistent hash optional for sticky warm pools.

**Q: Quota enforcement?**  
A: Redis counters with org caps; Postgres periodic reconcile; fail closed on Redis loss for starts.

**Q: Idempotent start?**  
A: `Idempotency-Key` or compare-and-set on status transitions; single lease generation number.

### 7.9 Failure injection

1. Kill host mid-session → fence, volume safe, user restarts.  
2. Vault outage → no new starts with secrets.  
3. Registry 503 → warm-only mode.  
4. Redis down → fail closed starts.  
5. Orchestrator split brain → fencing tokens prevent dual run.  
6. Volume attach stuck → timeout, release lease, surface error.  
7. Hibernation disk full → fallback stop.  
8. Egress proxy overload → throttle box bandwidth, don’t open direct egress.  
9. Poison prebuild Dockerfile → DLQ prebuild, don’t block interactive pool.  
10. Clock skew on hosts → leases based on control-plane time + TTLs.

### 7.10 Comparison traps

**Q: How is this different from “SSH to a VM in AWS”?**  
A: Productized lifecycle, prebuilds, IDE UX, multi-tenant isolation, quotas, secrets, idle economics.

**Q: How is this different from Codespaces / Gitpod?**  
A: Same genre; interview focuses on isolation, volume ownership, warm pools, and scale math—not brand features.

**Q: Why not only Kubernetes pods?**  
A: Fine for control plane; for untrusted multi-tenant user kernels/workloads, microVMs (or Kata) are the stronger default story.

### 7.11 Extra interviewer traps (high value)

- What is durable when the user sees “Running”?  
- Who owns the workspace files if the microVM burns down?  
- How do you prevent two attaches of one volume?  
- Why is heartbeat QPS not start QPS?  
- How do secrets appear without landing in image history?  
- What do you bill for hibernated vs stopped?  
- How does warm pool avoid stampeding the registry?  
- What happens if auto-stop kills a long compile? (grace + notify + “keep alive” API)  
- How do you GC 40M volumes?  
- How do you prove tenant network isolation in tests?  
- When is hibernate worse than stop?  
- How do you fence a partitioned host that comes back?  
- Why per-digest pools instead of one giant pool?  
- How do preview URLs avoid becoming an open proxy?  
- What fails first under capacity exhaustion—and what do you queue vs reject?

---

## Appendix A — Example schemas

```sql
CREATE TABLE boxes (
  id              UUID PRIMARY KEY,
  org_id          UUID NOT NULL,
  project_id      UUID NOT NULL,
  user_id         UUID NOT NULL,
  status          TEXT NOT NULL,
  sku             TEXT NOT NULL,
  image_digest    TEXT NOT NULL,
  volume_id       UUID NOT NULL,
  region          TEXT NOT NULL,
  cell            TEXT NOT NULL,
  host_id         TEXT,
  instance_id     TEXT,
  lease_generation BIGINT NOT NULL DEFAULT 0,
  hibernate_snapshot_uri TEXT,
  last_active_at  TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX boxes_org_user ON boxes (org_id, user_id, updated_at DESC);

CREATE TABLE volumes (
  id              UUID PRIMARY KEY,
  org_id          UUID NOT NULL,
  size_gb         INT NOT NULL,
  storage_backend TEXT NOT NULL,
  status          TEXT NOT NULL, -- available|attached|deleting
  attached_box_id UUID,
  attach_generation BIGINT NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE prebuilds (
  id              UUID PRIMARY KEY,
  project_id      UUID NOT NULL,
  git_sha         TEXT NOT NULL,
  image_digest    TEXT,
  status          TEXT NOT NULL, -- queued|building|ready|failed
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (project_id, git_sha)
);

CREATE TABLE start_outbox (
  id              BIGSERIAL PRIMARY KEY,
  box_id          UUID NOT NULL,
  lease_generation BIGINT NOT NULL,
  payload         JSONB NOT NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at    TIMESTAMPTZ
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | microVM hosts, volume attach, Postgres FSM, Redis quotas, IDE gateway, vault inject, egress deny metadata |
| 10× | Warm pools, fair start queues, registry mirrors, read replicas, idle auto-stop |
| 100× | Cells, heartbeat aggregators, noisy-neighbor pools, snapshot GC, prebuild spot fleet |
| 1,000× | Global directory, hibernate economics, volume tiering/retention, capacity forecasting |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| DevBox | Isolated remote environment + volume + policy |
| microVM | Lightweight VM (Firecracker-class) |
| Prebuild | Immutable image/snapshot for a git sha |
| Warm pool | Pre-booted instances waiting for assign |
| Fencing token / lease generation | Prevents split-brain compute/volume |
| Hibernate | Memory snapshot + volume retain |
| Stop | Release compute; keep volume |
| Egress proxy | Controlled outbound path |
| Time-to-shell | Start → usable terminal |

## Appendix D — Estimation cheat-sheet

```text
Split: API QPS ≠ start QPS ≠ heartbeat QPS ≠ IDE conns

Running vCPU ≈ concurrent_boxes × avg_vCPU
Volumes logical ≈ retained_boxes × avg_size_gb
Warm pool cost ≈ pool_slots × sku_cost  (budget explicitly)

Heartbeats at 1,000× need aggregation — not Postgres rows/sec

Gateway RAM ≈ conns × 50–100 KB fleet-wide
```

---

*End of design doc. Open with §1 isolation + persistence questions; whiteboard §3.3–3.5 lifecycle/volumes; close with invariants in §5.1 and traps in §7.*
