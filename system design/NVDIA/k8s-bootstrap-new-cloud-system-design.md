# System Design: Bootstrap Kubernetes in a New Cloud

> **Focus areas:** Day-0 networking · IAM · Control plane · Workers · CNI · CSI · GPU operators / device plugins · Observability · GitOps · Cluster API vs managed · Security baselines · Multi-cluster fleet  
> **Style:** End-to-end platform / ops HLD with progressive scale (single cluster → 10× → 100× → 1,000× fleets)  
> **Quality bar:** Explicit Day-0 ordering, honest managed vs self-managed trade-offs, GPU-aware NVIDIA interview lens, deal-breakers called out  
> **Interview theme:** NVIDIA cloud / infra / ML platform — “first Kubernetes in a new cloud provider or region” as a **bootstrap system**, not a YAML dump

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

Goal: **bound Day-0**—what “Kubernetes in a new cloud” must provide on day one (who lands workloads, GPU or not, regulated or not), and how the design evolves into a **fleet**.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | New cloud meaning? | New public cloud account/region, or on-prem-like private cloud API | Need provider-specific CCM/CSI/CNI ports |
| F2 | Managed K8s or self-managed? | Prefer managed if available; else Cluster API / kubeadm-style | Decision tree early |
| F3 | Workload types? | Stateless services + **GPU training/inference** jobs | GPU operator, device plugin, drivers, taints |
| F4 | Network model? | Private nodes; public LB only where needed; optional flat VPC | CNI + subnet plan before cluster create |
| F5 | Identity? | Cloud IAM + K8s RBAC + workload identity | No long-lived keys on nodes if possible |
| F6 | Storage? | Block for databases; shared FS / object for datasets | CSI drivers + storage classes |
| F7 | Cluster lifecycle? | IaC + GitOps from day 1 | Bootstrap ≠ ClickOps |
| F8 | Observability? | Metrics, logs, traces, GPU telemetry | Agents planned in Day-0 addons |
| F9 | Multi-tenancy? | Teams share cluster at first; hard isolation later | Namespaces → clusters → cells |
| F10 | Registry / artifacts? | Private container registry in-region | Pull-through + image signing later |
| F11 | Policy? | PSS/PSA baselines; network policies | Admission from early days |
| F12 | Outbound access? | Controlled egress for package/GPU driver deps | NAT + allowlists |

**MVP functional scope (lock with interviewer):**

1. **Landing zone:** accounts/folders, VPC/subnets, IAM roles, private connectivity pattern.  
2. **One regional cluster** (managed preferred) with HA control plane.  
3. **Node pools:** CPU system pool + GPU pool (tainted).  
4. **CNI** with NetworkPolicy support; **CSI** default StorageClass.  
5. **GPU stack:** driver + device plugin / NVIDIA GPU Operator (or cloud equivalent).  
6. **GitOps** (Argo CD / Flux) + IaC (Terraform/Pulumi/Crossplane) for cluster and addons.  
7. **Observability baseline:** metrics + logs + alerts; GPU DCGM exporter when GPUs present.  
8. **Security baseline:** private nodes, RBAC, PSA baseline/restricted tier plan, secrets encryption, CIS-ish hardening.  
9. Document Day-0 → Day-2 runbooks; path to multi-cluster.

**Out of MVP (explicitly defer):**

- Global multi-region active-active control plane for a single cluster  
- Perfect zero-trust service mesh on hour one (can stage)  
- Bare-metal PXE from scratch unless interviewer demands it  
- Multi-cluster service discovery fabric on day one  
- Training a 10K-GPU job as the bootstrap acceptance test (use small GPU smoke)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time to first useful cluster? | Days not months | MVP cluster usable in ≤ 1–2 weeks with automation |
| N2 | Control plane availability? | Production-minded even for “first” | Multi-AZ managed or 3-etcd self-managed |
| N3 | Node bootstrap time? | Auto-scale friendly | GPU node ready (driver loaded) in tens of minutes SLO |
| N4 | Upgrade story? | Must exist from day 1 | Version skew policy N / N-1 |
| N5 | Blast radius? | Single cluster loss survivable for non-prod first | Separate prod later |
| N6 | Compliance? | Soft baseline → harden | Encrypt etcd/secrets; audit logs |
| N7 | Reproducibility? | Another region = same modules | IaC modules + GitOps apps |
| N8 | Scale path? | To fleet | Cluster API / fleet manager later |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. IaC applies landing zone → VPC/IAM → managed cluster → node pools → addons via GitOps → GPU smoke pod `nvidia-smi` → app namespace deployed.  
2. Developer pushes Helm/Kustomize to Git → GitOps reconciles → service on internal LB.  
3. Cluster upgrade: control plane then node pools rolling; GPU pool drained with PodDisruptionBudgets.  
4. New region: reuse modules; new state backend key; same addon app-of-apps.  
5. On-call gets alert on node NotReady; auto-repair replaces node.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cloud missing managed K8s | Fall back Cluster API / self-managed; longer Day-0 |
| GPU quota = 0 in region | Bootstrap CPU-only; GPU pool gated on quota ticket |
| CNI IP exhaustion | Sized pod CIDR; plan secondary ranges early |
| CSI broken → pods Pending | Separate storage validation job in bootstrap checklist |
| Driver mismatch vs CUDA image | Node feature discovery + admission / capacity labeling |
| GitOps can’t reach cluster | Bootstrap break-glass kubeconfig in vault; break-glass runbook |
| Accidental public API server | Deny by policy; private endpoint default |
| etcd disk full (self-managed) | Monitoring + compaction; managed avoids most of this |
| IAM too wide on nodes | Instance roles scoped; IRSA/Workload Identity for pods |
| Addon crash loops | Health checks block “bootstrap complete” |
| Multi-AZ LB quirks per cloud | Document cloud-specific CCM annotations |
| Cluster delete with PV data | Retention policy; don’t test delete in prod |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 cluster) | 10× | 100× | 1,000× |
|--------|----------------------|-----|------|--------|
| Clusters | 1 | 10 | 100 | 1,000 |
| Regions / clouds | 1 | 2–3 | many | multi-cloud fleet |
| Nodes / cluster | 10–50 | 100–500 | 1K–5K | cell architecture |
| GPU nodes | 2–16 | 100+ | thousands | superpod-scale cells |
| Namespaces / teams | 5–20 | 50–100 | hard multi-tenant limits | cluster-per-team/cell |
| GitOps apps | 20 | 200 | 2K | hierarchical app-of-apps |
| Policy objects | dozens | hundreds | thousands | Fleet policy engine |
| Control planes to patch | 1 | 10 | 100 | automated waves |
| Observability series | 100K | 1M | 10M+ | regional metric tenants |
| Platform engineers | 2–4 | 8–15 | 30–50 | platform org + cell teams |

**What each jump forces:**

- **10× clusters:** Fleet inventory; shared modules; progressive delivery of cluster upgrades; shared observability tenants.  
- **100×:** Cluster API / GKE Fleet / ACK-style management; policy-as-code (OPA/Gatekeeper/Kyverno) at fleet; multi-cluster GitOps.  
- **1,000×:** Cells/partitions of the platform; hierarchical control planes; no snowflake clusters; GPU capacity as a separate scheduler fabric.

### 1.5 Etc. (Constraints & Assumptions)

- “New cloud” has a programmable API for VPC, IAM, VMs/GPUs, LB, disks (or we build the missing CCM pieces).  
- We may not have unlimited GPU quota on day one.  
- Platform team owns **cluster lifecycle + baselines**; app teams own workload charts.  
- NVIDIA lens: GPU operator, MIG/time-slicing optional Phase 2, DCGM, CUDA compatibility.  
- Secrets never only in Git plaintext—SOPS/SealedSecrets/ESO + KMS.

**Scope statement:**

> Design Day-0 through Day-2 bootstrap of the first Kubernetes deployment in a new cloud—landing zone, control plane, workers, CNI/CSI, GPU enablement, observability, GitOps, and security baselines—then show the path from one cluster to a multi-cluster fleet at 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Address space (do this before clicking “create”)

```text
VPC CIDR example: 10.20.0.0/16
  public subnets:  3 × /24  (NAT, LB only)
  private subnets: 3 × /20  (nodes)
Pod CIDR (if not VPC-native): 10.100.0.0/16 → ~65K pods
Service CIDR: 10.200.0.0/20

Nodes=50, pods/node=64 → need ≥ 3200 pod IPs (+ headroom)
GPU nodes often fewer pods but larger — still plan /14-/16 pod space for growth

100× clusters: per-cluster VPC or shared VPC with per-cluster pod ranges—document collision policy
```

**Unit check:** `/24` = 256 addresses; unsuitable as sole private range for a growing cluster.

### 2.2 Control plane sizing (self-managed only)

```text
etcd: 3 or 5 members; SSD; latency matters
API server: 2+ replicas behind LB
Baseline cluster 100 nodes: managed is fine default
5K nodes: need control plane tuning / split clusters / hierarchical schedulers
```

### 2.3 GPU node bootstrap cost

```text
Cold GPU VM start: 3–10+ minutes (cloud dependent)
Driver + toolkit + plugin: +5–20 minutes first image bake
Strategy: golden AMI/image with driver preinstalled vs Operator install on boot
  Prebaked image: faster scale-up, more image maintenance
  Operator: flexible, slower first boot
```

### 2.4 Observability volume

```text
Baseline 30 nodes × ~2K series/node ≈ 60K series
GPU: DCGM adds per-GPU metrics — 8 GPU/node × 50 metrics ≈ material
Logs: 5 KB/s/node → 30×5 ≈ 150 KB/s → ~13 GB/day raw (+ingestion tax)
Design retention tiers early or bill shock at 100×
```

### 2.5 GitOps reconcile load

```text
20 apps × reconcile every 3 min ≈ low
2K apps: need sharding AppControllers / root app-of-apps per cluster
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Wrong VPC/CIDR** (painful to renumber)  
2. **IAM / private API endpoint misconfig** (bootstrap lockout)  
3. **GPU driver ↔ CUDA image skew**  
4. **CNI / NetworkPolicy / LB cloud integration**  
5. **Snowflake ClickOps cluster** (cannot reproduce region 2)  
6. **Observability + etcd / API server overload** at node growth  
7. **Upgrade fear** without PDBs and surge capacity  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
LandingZone   → cloud org, accounts, VPC, IAM, KMS, registry
Cluster       → control plane + node pools + cloud integrations
Addon         → CNI, CSI, DNS, ingress, GPU, obs, policy, GitOps
Fleet         → inventory + desired cluster generations
Cell          → isolation boundary at large scale (region × env × GPU family)
WorkloadIdentity → cloud role ↔ K8s SA mapping
```

**Bootstrap state machine:**

```text
LZ_READY → CLUSTER_PROVISIONED → CNI_HEALTHY → CSI_HEALTHY →
GPU_READY (optional) → OBS_READY → GITOPS_READY → BASELINE_SECURE →
SMOKE_PASSED → DECLARED_READY → (Day2: UPGRADEABLE)
```

Do **not** mark READY if GPU pool promised but `nvidia-smi` smoke fails.

### 3.2 Options: managed vs Cluster API vs kubeadm

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Managed K8s (EKS/GKE/AKS/…) | Less etcd toil; cloud IAM hooks | Region/feature lag; less control | Cloud has no managed offering |
| B. Cluster API (CAPI) | Consistent multi-cloud; GitOps-native lifecycle | Needs management cluster; provider maturity varies | No stable infra provider for that cloud |
| C. kubeadm / DIY | Maximum control | You own etcd/DR forever | Platform team size = 2 and prod GPUs |

**Chosen path:**

- **MVP in new commercial cloud with managed K8s:** **Managed control plane** + IaC + GitOps addons.  
- **If no managed / private cloud:** **Cluster API** with a small bootstrap management cluster (chicken-egg: use temporary managed elsewhere or cloud VMs + kubeadm once to host CAPI).  
- **Avoid** long-term snowflake kubeadm without CAPI encapsulation.

### 3.3 Day-0 ordering (critical)

Order matters more than fancy mesh choices:

```text
1. Org / account / billing / quotas (GPU!)
2. KMS keys + secrets backend
3. VPC, subnets, NAT, private DNS, endpoints
4. IAM roles for control plane, nodes, CI, GitOps deployers
5. Container registry + base images pull path
6. Create cluster (private API)
7. Bootstrap break-glass admin (time-boxed)
8. Install CNI (if not bundled) → core DNS path
9. CSI + default StorageClasses
10. Metrics server / cluster autoscaler / CCM features
11. Observability agents
12. Policy admission (PSA/Gatekeeper/Kyverno)
13. GPU Operator / drivers / device plugin
14. GitOps controller + root app
15. Platform addons as code (ingress, cert-manager, …)
16. Smoke tests (CPU + GPU) → READY
```

**Deal-breaker:** Installing GPU apps before device plugin healthy; or GitOps before network/DNS works.

### 3.4 Networking design

| Concern | MVP choice |
|---------|------------|
| API server | Private endpoint; break-glass via bastion / VPN / ZTNA |
| Nodes | Private subnets only |
| Pod networking | Cloud-native CNI when good (e.g. VPC CNI variants) else Calico/Cilium |
| NetworkPolicy | Required capability—pick CNI that enforces |
| Egress | NAT gateway; explicit allowlists for registries/drivers |
| Ingress | Internal LB default; public only for approved ingress class |
| DNS | CoreDNS + cloud private zones for services |

**Cilium vs Calico vs cloud CNI:** pick one; don’t run two dataplanes. For NVIDIA GPU clusters, prefer CNI with clear eBPF/perf story if east-west training traffic is heavy—call the trade-off (ops complexity vs features).

**IPAM deal-breaker:** Undersized secondary ranges that force cluster recreate.

### 3.5 IAM & workload identity

```text
Human:    SSO → cloud IAM → short-lived kubeconfig (or OIDC to API server)
Node:     instance profile / managed identity (minimal)
Pod:      Workload Identity / IRSA / federated OIDC → cloud roles
GitOps:   deploy SA limited to namespace sets; cluster-admin only for platform root
CI:       OIDC to cloud; no exported AK/SK in Jenkins
```

**Deal-breaker:** Long-lived `admin.conf` in Slack.

### 3.6 Control plane & workers

**Pools:**

| Pool | Taints / labels | Role |
|------|-----------------|------|
| `system` | Critical addons prefer here | CoreDNS, GitOps, obs, operators |
| `general` | none | Stateless services |
| `gpu` | `nvidia.com/gpu=true:NoSchedule` | Training/inference pods |

**Autoscaling:** Cluster Autoscaler or Node Autoprovisioning; GPU pools may need custom startup taints until drivers ready (`nvidia.com/gpu.present`).

### 3.7 Storage CSI

```text
StorageClasses:
  - fast-block (SSD) default for databases
  - standard-block
  - shared-fs (if Filestore/ANF/Lustre/…) for datasets — Phase 1.5
  - object via CSI or app-level SDK (often better for huge datasets)
```

Snapshots / backup: enable before prod stateful. GPU training checkpoints often → object storage, not small PVCs.

### 3.8 GPU stack (NVIDIA-specific)

```text
Options:
  A. NVIDIA GPU Operator (driver, toolkit, device-plugin, DCGM, MIG manager)
  B. Cloud GPU node images + device plugin only
  C. Custom AMI + plugin

MVP recommendation:
  - Managed node image with drivers if cloud supports well-tested images
  - Else GPU Operator on tainted nodes
  - Validate: nvidia-smi DaemonSet/Job + CUDA vectorAdd smoke
  - Label nodes with GPU product / MIG profile
```

**CUDA compatibility:** document supported driver ≥ toolkit; use Node Feature Discovery + admission to prevent unschedulable/broken pods.

**MIG / time-slicing:** Phase 2 unless interviewer requires sharing.

### 3.9 Observability

| Signal | MVP |
|--------|-----|
| Metrics | Prometheus (or managed) + Grafana; kube-state-metrics |
| GPU | DCGM exporter |
| Logs | DaemonSet shipper → regional log store |
| Traces | Optional Phase 1.5 OTel collector |
| Alerts | API server / node NotReady / GPU XID / disk / cert expiry |

Cardinality budgets from day 1.

### 3.10 GitOps & IaC split

```text
IaC (Terraform/…): cloud resources, cluster, node pools, IAM, KMS, registry
GitOps (Argo/Flux): in-cluster addons + app deployments
Cluster API (later): Cluster CRDs may live in GitOps on management cluster
```

**App-of-apps pattern:** root Application → platform → team roots.

### 3.11 Security baselines

```text
- Private nodes + private API
- Secrets encryption at rest (KMS provider)
- Audit logs to immutable store
- PSA: baseline now; restricted for new namespaces
- NetworkPolicy default-deny in prod namespaces (staged)
- Image provenance Phase 2 (cosign verify admission)
- CIS node hardening via image
- Limit hostPath / privileged (GPU may need carefully reviewed exceptions)
- Rotatable bootstrap credentials
```

**GPU privileged reality:** drivers/device plugin historically need elevated permissions—contain to operator namespaces; don’t grant cluster-wide privileged to app teams.

### 3.12 Multi-cluster path (preview)

| Stage | Pattern |
|-------|---------|
| 1 cluster | Namespaces + quotas |
| 10× | Cluster per env (dev/stage/prod) + maybe per region |
| 100× | Fleet manager; cluster generations (v1, v2 blueprints) |
| 1,000× | Cells; workload placement API; no human click per cluster |

---

## 4. Architecture Diagram

```text
                          ┌──────────────────────────────┐
                          │  Identity / SSO / Cloud IAM  │
                          └──────────────┬───────────────┘
                                         │ OIDC / short-lived
                                         v
┌────────────┐   IaC    ┌────────────────────────────────────────────┐
│ Git (infra)│─────────►│ Landing Zone: VPC · Subnets · NAT · KMS    │
└────────────┘          │ Registry · Quotas · Bastion/ZTNA           │
                        └───────────────────┬────────────────────────┘
                                            │
                                            v
                              ┌─────────────────────────┐
                              │  Managed K8s / CAPI CP  │
                              │  (multi-AZ API + etcd)  │
                              └───────────┬─────────────┘
                                          │
           ┌──────────────────────────────┼──────────────────────────────┐
           v                              v                              v
    ┌─────────────┐               ┌─────────────┐               ┌─────────────┐
    │ system pool │               │ general     │               │ GPU pool    │
    │ GitOps,obs  │               │ services    │               │ Operator /  │
    │ policy      │               │             │               │ device plug │
    └─────────────┘               └─────────────┘               └─────────────┘
           │                              │                              │
           └──────────────────────────────┼──────────────────────────────┘
                                          v
                        ┌─────────────────────────────────┐
                        │ CNI · CSI · CCM · Ingress · DNS │
                        └─────────────────────────────────┘
                                          │
                    ┌─────────────────────┼─────────────────────┐
                    v                     v                     v
             ┌────────────┐        ┌────────────┐        ┌────────────┐
             │ Metrics/Log│        │ Object /   │        │ Partner    │
             │ + DCGM     │        │ Dataset FS │        │ Cloud APIs │
             └────────────┘        └────────────┘        └────────────┘

Fleet (later):

  mgmt cluster ──Cluster API / Fleet──► cluster-a (region1)
                                   ├──► cluster-b (region2)
                                   └──► cluster-gpu-cell-01
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Control plane

| Managed | Self-managed / CAPI |
|---------|---------------------|
| Rely on provider SLA; still test upgrade | 3/5 etcd; snapshots; restore drill |
| Private endpoint HA | API server LB health checks |

**Drill:** restore from etcd backup into a new control plane (self-managed) quarterly.

#### 5.1.2 Node & GPU reliability

- Auto-repair for NotReady.  
- GPU XID alert → cordon/drain/replace.  
- Startup taint until driver ready prevents scheduler race.  
- Surge capacity for upgrades (`maxSurge`).

#### 5.1.3 GitOps reliability

- Git is desired state; cluster drift alerts.  
- Break-glass kubeconfig in vault with MFA + TTL.  
- Freeze GitOps during incident if bad sync cascading (app-of-apps pause).

#### 5.1.4 Bootstrap lockout prevention

```text
Before disabling public API:
  verify bastion/VPN path
  verify break-glass user
  verify IaC can still reach provider APIs
```

**Deal-breaker:** Private API + broken VPN + no break-glass = paperweight cluster.

#### 5.1.5 Failure modes

| Failure | Response |
|---------|----------|
| AZ loss | Multi-AZ node pools; etcd spanning AZs |
| Registry outage | Warm cache / mirrors for critical images |
| CCM cannot create LB | Pre-create or use Ingress with known annotations; alert |
| IP exhaustion | Expand ranges or new cluster; monitor allocations |
| Bad cluster upgrade | Surge + PDB; rollback plan per managed offering |
| Secret KMS disable | Avoid; break-glass keys procedure documented |

### 5.2 Scalability

#### 5.2.1 Vertical limits of one cluster

Practical soft limits (order-of; version-dependent):

```text
~few thousand nodes / cluster before ops pain
~100K pods (often less in practice)
etcd object count / watch storms from bad controllers
```

**Jump:** prefer **more clusters** over hero-tuning one mega-cluster for multi-tenant GPU—cells isolate failure.

#### 5.2.2 Fleet scaling patterns

| Pattern | Use |
|---------|-----|
| Blueprint modules | Same cluster generation everywhere |
| Progressive rollout | Canary cluster → wave 1 → wave N |
| Hierarchical GitOps | Org → cloud → region → cluster |
| Policy federation | Kyverno/OPA constraints at fleet |
| Capacity service | Separate GPU inventory from K8s API |

#### 5.2.3 Progressive jump cards

**10×:** “Second region from modules; env-separated clusters; shared observability tenant; upgrade waves.”  
**100×:** “Management cluster + Cluster API/fleet; cluster generations; automated compliance scans.”  
**1,000×:** “Cell architecture; placement API; platform control plane HA; no human per-cluster clicks.”  

#### 5.2.4 What does *not* scale

- ClickOps console clusters  
- One shared `kubeconfig` admin for all humans  
- Single Prometheus without federation/sharding  
- Default-allow NetworkPolicy forever  
- GPU and system addons fighting on the same small node pool  

### 5.3 Maintainability

#### 5.3.1 Module boundaries

```text
modules/
  landing_zone/
  k8s_cluster/
  node_pools/
  gitops_bootstrap/
gitops/
  platform/   # CNI config, obs, policy, gpu-operator
  teams/
```

Version modules; promote cluster **generation** `gen-14` → `gen-15`.

#### 5.3.2 Addon lifecycle

Treat GPU Operator, cert-manager, ingress as **versioned platform products** with changelogs and upgrade notes—not ad-hoc Helm on Fridays.

#### 5.3.3 Documentation as acceptance

Bootstrap complete only when:

1. Architecture diagram current  
2. Break-glass runbook tested  
3. Upgrade runbook tested on non-prod  
4. Smoke suite in CI against the cluster  

#### 5.3.4 Observability for the platform itself

- Cluster creation duration  
- Node readiness latency (esp. GPU)  
- GitOps sync error rate  
- Policy violation counts  
- Upgrade success rate  

### 5.4 Security deep dive

#### 5.4.1 Admission stages

```text
Day0: PSA baseline; deny privileged except platform NS
Day1: image registry allowlist
Day2: signed images; stricter PSS; egress policies
```

#### 5.4.2 Secrets

External Secrets Operator + cloud secret manager; rotate; never commit raw kubeconfig.

#### 5.4.3 Supply chain

Pin chart versions; digest pins for critical images; mirror in-region registry.

#### 5.4.4 Multi-tenancy evolution

| Stage | Isolation |
|-------|-----------|
| Namespaces + RBAC + quotas | MVP |
| Soft multi-tenant + NetworkPolicy | 10× |
| Cluster-per-team / per-env | noisy neighbors / compliance |
| Cells + dedicated GPU hardware | 100×–1,000× |

### 5.5 CNI deep dive

**Questions to answer in interview:**

1. VPC-native pods vs overlay encapsulation?  
2. How are NodePort / LB integrated with cloud firewalls?  
3. NetworkPolicy implementation confirmed with a probe pod test?  
4. MTU / RDMA / GPUDirect considerations if training fabric exists (may be **outside** CNI—call out InfiniBand/RoCE networks separately)?

For NVIDIA training clusters, **storage + GPU interconnect** often matter more than fancy ingress. Separate:

```text
K8s east-west (CNI)
Storage network
GPU/RDMA fabric
```

Don’t force all onto one flat CNI story if the hardware doesn’t.

### 5.6 CSI & datasets

Training data:

- Small: PVC  
- Large: object store (S3/GCS/…) or parallel FS CSI  
- Checkpoints: object store with lifecycle  

**Deal-breaker:** Putting 100 TB datasets on default cloud disks attached as tiny PVs without throughput math.

### 5.7 Cluster API chicken-and-egg

```text
Bootstrap path:
  1) Temporary seed cluster (managed or kubeadm)
  2) Install CAPI + infra providers
  3) CAPI creates target “new cloud” clusters
  4) Move CAPI management to a stable HA mgmt cluster
  5) Decommission seed if ephemeral
```

### 5.8 Managed offering gaps checklist

When evaluating “new cloud managed K8s”:

| Feature | Why it matters |
|---------|----------------|
| Private control plane | Security baseline |
| GPU node types + drivers | NVIDIA workloads |
| IAM / OIDC integration | Workload identity |
| CSI quality | Stateful + scratch |
| Upgrade control | Day-2 |
| Autopilot vs node control | GPU often needs node-level |

If gaps are fatal, choose CAPI/self-managed consciously.

---

## 6. Wrap-Up

### 6.1 Summary

| Piece | Choice |
|-------|--------|
| Control plane | Managed if viable; else Cluster API |
| Day-0 order | LZ → cluster → CNI → CSI → obs → policy → GPU → GitOps → smoke |
| Nodes | system / general / gpu tainted pools |
| Identity | OIDC + workload identity; no long-lived admin keys |
| Desired state | IaC for cloud; GitOps for in-cluster |
| Security | private API/nodes, KMS secrets, PSA, staged NetworkPolicy |
| Scale | blueprints → fleet → cells |

### 6.2 30-second pitch

> Bootstrap is a state machine: land the cloud foundation, bring up a private multi-AZ cluster, validate CNI/CSI, install policy and observability, enable GPUs with a real `nvidia-smi` smoke, and only then hand over GitOps. Scale out by cloning modules into a fleet—not by ClickOps.

### 6.3 Trade-offs

1. Managed convenience vs deep control / exotic GPU fabrics.  
2. Prebaked GPU images vs Operator flexibility.  
3. One shared cluster vs early cluster-per-env cost.  
4. Overlay CNI simplicity vs VPC-native performance/ops.  
5. Fast Day-0 vs hardened restricted PSA immediately.

### 6.4 Deal-breakers (memorize)

1. Public API server + nodes as default “for convenience.”  
2. Declaring success without CNI/CSI/GPU smokes.  
3. Undersized IP ranges forcing recreate.  
4. Long-lived cluster-admin kubeconfigs distributed widely.  
5. Snowflake cluster with no IaC/GitOps.  
6. App pods scheduled on GPU nodes before drivers ready (no startup taint).

---

## 7. Deeper / Related Interview Questions

### 7.1 Day-0 & ordering

**Q: What’s the first thing you create?**  
A: Landing zone + quotas (especially GPU), not the cluster CR. Without network/IAM/KMS, cluster create fails or is unsafe.

**Q: Why GitOps after CNI?**  
A: Controllers need pod networking and DNS; install order reduces thrash.

**Q: How do you avoid chicken-egg for GitOps credentials?**  
A: IaC creates deploy IAM + seeds initial secret; then GitOps takes over; rotate seed.

### 7.2 Managed vs self-managed

**Q: When do you refuse managed?**  
A: Missing private CP, no GPU path, broken CSI, or need for specialized networking the managed service blocks.

**Q: Is kubeadm on VMs enough?**  
A: For a lab yes; for fleet, wrap with Cluster API or accept permanent toil.

**Q: Management cluster HA?**  
A: Yes at 10×+; protect CAPI/GitOps; backup Cluster CRDs.

### 7.3 Networking

**Q: Overlay vs VPC-native?**  
A: VPC-native often simpler firewalling/perf with cloud integrations; overlay portable; pick based on cloud maturity.

**Q: How to test NetworkPolicy?**  
A: Two probe pods; deny ingress; expect timeout; add allow; expect success—automate in smoke.

**Q: GPUDirect / RDMA on K8s?**  
A: Often secondary interfaces / device plugins / host networking patterns; don’t pretend default CNI solves HPC fabric.

### 7.4 GPU

**Q: Device plugin vs Operator?**  
A: Plugin exposes resources; Operator manages driver/toolkit/DCGM lifecycle. Cloud may bake drivers—then plugin (+DCGM) may suffice.

**Q: MIG?**  
A: Partition GPU for smaller jobs; Phase 2; complicates scheduling and driver modes.

**Q: Why taint GPU nodes?**  
A: Prevent CPU workloads wasting expensive capacity; tolerations only on GPU jobs.

**Q: CUDA mismatch failure mode?**  
A: Container starts then fails; prevent with node labels + admission or compatible base images.

### 7.5 Storage & data

**Q: PVC vs object for training data?**  
A: Object for large sequential datasets; PVC/FS when POSIX needed; measure throughput.

**Q: etcd for what?**  
A: Cluster state only—not application datasets.

### 7.6 Security

**Q: Should developers be cluster-admin?**  
A: No. Namespace admin max for app teams; platform for cluster.

**Q: Privileged GPU operator—risk?**  
A: Constrain to platform namespace; audit; don’t copy privileges to apps.

**Q: How to handle break-glass?**  
A: Vault; MFA; time-bound; alert on use.

### 7.7 Observability & ops

**Q: First alerts to configure?**  
A: Node NotReady, disk pressure, API error budget, GitOps sync fail, GPU XID, cert expiry, pending pods spike.

**Q: Multi-cluster metrics?**  
A: Per-cluster Prometheus + federation or remote-write tenants; avoid one mega scrape of 1,000 clusters from one DB without design.

### 7.8 Scale & fleet

**Q: Namespace-per-team forever?**  
A: Until noisy neighbor / blast radius / compliance forces cluster splits.

**Q: How to upgrade 100 clusters?**  
A: Generations + waves + canaries + automated health signals; never big-bang Friday.

**Q: Cluster sprawl?**  
A: Inventory, TTL for scratch clusters, cost showback, blueprint enforcement.

### 7.9 NVIDIA-flavored scenarios

**Q: New cloud region with A100/H100 SKUs but immature managed K8s GPU?**  
A: CAPI/self-managed node images; validate driver; isolate as GPU cell; don’t block CPU platform.

**Q: Inference vs training clusters?**  
A: Different autoscaling, networking, and SLOs—often separate node pools or clusters.

**Q: Multi-instance GPU for SaaS inference?**  
A: MIG/time-slicing trade-offs; start with dedicated GPUs for correctness.

### 7.10 Comparison questions

**Q: vs Nomad / Slurm for GPUs?**  
A: K8s wins ecosystem/GitOps; Slurm still common for classic HPC scheduling—hybrid possible (K8s for services, Slurm for batch).

**Q: vs “just use serverless GPUs”?**  
A: May skip cluster bootstrap for some apps; not a full platform substitute for custom daemons/operators.

### 7.11 Interview traps

**Q: “We’ll fix CIDRs later.”**  
A: Often cannot without recreate—design upfront.

**Q: “Security in phase 2.”**  
A: Private API + IAM + encryption are Day-0; mesh can wait.

**Q: Units:** 1,000 clusters × 30 min manual upgrade ≠ feasible—express as **automation waves**, not hero hours.

---

## 8. Appendices

### 8.1 Bootstrap checklist (printable)

```text
[ ] GPU/CPU quotas approved
[ ] KMS + secret store
[ ] VPC/CIDRs documented + peer review
[ ] Private DNS / endpoints
[ ] IAM roles (CP, node, GitOps, CI OIDC)
[ ] Registry reachable from private nodes
[ ] Cluster created (multi-AZ)
[ ] Break-glass tested
[ ] CNI smoke (pod↔pod)
[ ] NetworkPolicy smoke
[ ] CSI smoke (PVC R/W)
[ ] Metrics/logs flowing
[ ] PSA/policy admitted
[ ] GPU operator/plugin healthy
[ ] nvidia-smi + CUDA smoke
[ ] GitOps root synced
[ ] Upgrade dry-run notes
[ ] DECLARED_READY tag in inventory
```

### 8.2 Example Terraform-ish resources (illustrative)

```text
module "lz"        { ... vpc, subnets, nat, kms ... }
module "registry"  { ... }
module "cluster"   { ... private_cluster=true ... }
module "node_cpu"  { ... }
module "node_gpu"  { ... taints = [gpu] ... }
# then kubernetes bootstrap manifests for GitOps
```

### 8.3 GPU smoke Job (illustrative)

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: gpu-smoke
spec:
  template:
    spec:
      tolerations:
        - key: nvidia.com/gpu
          operator: Exists
          effect: NoSchedule
      containers:
        - name: cuda-smoke
          image: registry.example.com/cuda-smoke:12.x
          resources:
            limits:
              nvidia.com/gpu: 1
          command: ["bash","-lc","nvidia-smi && /smoke/vectorAdd"]
      restartPolicy: Never
```

### 8.4 NetworkPolicy probe idea

```text
namespace netprobe:
  pod a (label run=a)
  pod b (label run=b)
  deny all ingress to b
  from a: curl b → fail
  allow from a → success
```

### 8.5 StorageClass sketch

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast-block
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: <cloud.csi.disk>
reclaimPolicy: Delete
volumeBindingMode: WaitForFirstConsumer
allowVolumeExpansion: true
```

### 8.6 RBAC sketch (platform vs team)

```text
ClusterRole platform-admin → platform group
Rolebinding team-edit → namespace team-x for team group
No cluster-admin for humans except break-glass group
```

### 8.7 GitOps app-of-apps

```text
root
 ├─ platform-operators (gpu, cert-manager, ingress)
 ├─ platform-observability
 ├─ platform-policy
 └─ teams/
     ├─ team-a
     └─ team-b
```

### 8.8 Cluster generations

```text
gen-12: k8s 1.28, cilium 1.15, gpu-op 24.x
gen-13: k8s 1.29, cilium 1.16, gpu-op 25.x
Migration: create new cluster or in-place wave with notes
```

### 8.9 Observability minimum dashboards

- Cluster / node health  
- Pending pods by reason (`Insufficient nvidia.com/gpu`, CIDR, PVC)  
- GPU utilization + XID  
- GitOps sync  
- API server latency  

### 8.10 Upgrade runbook (condensed)

```text
1. Read provider notes + GPU driver compat
2. Canary cluster first
3. Drain GPU pools politely (job completion / checkpoint)
4. Upgrade CP
5. Upgrade system pool
6. Upgrade general
7. Upgrade GPU (surge)
8. Smokes
9. Wave next clusters
```

### 8.11 Security baseline controls

| Control | MVP |
|---------|-----|
| Private API | ✓ |
| Secrets KMS | ✓ |
| Audit logs | ✓ |
| PSA baseline | ✓ |
| NetworkPolicy | staged ✓ |
| Image signing | Phase 2 |
| Runtime security | Phase 2 |

### 8.12 Capacity worksheet

```text
Expected pods = services + jobs + system DaemonSets
DaemonSets × nodes ≈ system overhead (obs+CNI+GPU agents)
GPU jobs × gpust/job ≤ GPU inventory
Leave 20–30% headroom for surge upgrades
```

### 8.13 Multi-cloud differences (interview awareness)

| Topic | Varies by cloud |
|-------|-----------------|
| VPC CNI | Yes |
| GPU images | Yes |
| Workload identity | Yes |
| LB annotations | Yes |
| Disk performance classes | Yes |

Abstract with modules; don’t pretend one YAML fits all.

### 8.14 Anti-patterns

1. Installing everything with `kubectl apply` from a laptop and no Git.  
2. Running CoreDNS on GPU nodes.  
3. Unlimited privileges for “just the Operator.”  
4. One cluster for prod+dev+CI.  
5. Ignoring cloud quotas until autoscaler flaps.  
6. Using `latest` tags for GPU driver images.  

### 8.15 Roles

| Role | Owns |
|------|------|
| Cloud foundation | LZ, network, IAM |
| Platform K8s | cluster modules, addons |
| ML platform | GPU ops, schedules, images |
| App teams | workload charts |
| Security | policy baselines, audits |

### 8.16 Interview board order

1. Clarify managed vs not + GPU needs  
2. Day-0 ordered checklist  
3. Diagram LZ → CP → pools → addons  
4. CNI/CSI/IAM/GPU deep dives as asked  
5. Security baseline  
6. Progressive fleet scale  
7. Deal-breakers  

### 8.17 Glossary

| Term | Meaning |
|------|---------|
| CCM | Cloud Controller Manager |
| CSI | Container Storage Interface |
| CNI | Container Network Interface |
| PSA | Pod Security Admission |
| CAPI | Cluster API |
| DCGM | Data Center GPU Manager |
| Cell | Isolation unit at fleet scale |

### 8.18 Related NVIDIA prep prompts

- GPU resource manager  
- Compute-cluster control plane  
- Artifact store on K8s + Cassandra  
- Dockerized GPU-test platform  
- GPU telemetry analytics  

### 8.19 Final signal

Strong candidates insist on **ordering**, **smokes**, **private-by-default**, and a **reproducible module path to region #2**—not a tour of every CNCF project.

---

*End of k8s bootstrap new cloud system design.*
