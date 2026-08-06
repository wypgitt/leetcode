# NVIDIA System Design Interview Prep

> Folder name matches the created directory `NVDIA`. NVIDIA interviews are **exceptionally team-dependent**. Backend/cloud candidates get conventional distributed-systems questions; AI-infrastructure teams get **GPU scheduling, training, inference, telemetry**; graphics/kernel/hardware teams may get **low-level design**.
>
> Core AI/infra themes (Exponent): distributed training, GPU resource management, parallel computing, utilization, node-failure recovery.

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

---

## A/B — GPU, AI, and compute infrastructure

| Evidence | Problem | File |
|----------|---------|------|
| A | Distributed training for a very large model | [distributed-training-system-design.md](./distributed-training-system-design.md) |
| A | Distributed inference across GPU nodes | [distributed-inference-system-design.md](./distributed-inference-system-design.md) |
| A/B | GPU resource manager / job-scheduling interface | [gpu-resource-manager-system-design.md](./gpu-resource-manager-system-design.md) |
| B | Compute-cluster control plane | [compute-cluster-control-plane-system-design.md](./compute-cluster-control-plane-system-design.md) |
| B | GPU telemetry collection and analytics | [gpu-telemetry-analytics-system-design.md](./gpu-telemetry-analytics-system-design.md) |
| B | Artifact store on Kubernetes + Cassandra | [k8s-cassandra-artifact-store-system-design.md](./k8s-cassandra-artifact-store-system-design.md) |
| B | Dockerized GPU-test platform | [dockerized-gpu-test-platform-system-design.md](./dockerized-gpu-test-platform-system-design.md) |
| B | Jenkins CI for graphics/GPU test matrix | [jenkins-gpu-test-matrix-system-design.md](./jenkins-gpu-test-matrix-system-design.md) |

---

## General backend and distributed systems

| Problem | File |
|---------|------|
| Shared cloud filesystem | [shared-cloud-filesystem-system-design.md](./shared-cloud-filesystem-system-design.md) |
| Bidirectional data-sync dashboard with conflict resolution | [bidirectional-data-sync-dashboard-system-design.md](./bidirectional-data-sync-dashboard-system-design.md) |
| Distributed multi-user counter | [distributed-multiuser-counter-system-design.md](./distributed-multiuser-counter-system-design.md) |
| URL-shortening service | [url-shortener-system-design.md](./url-shortener-system-design.md) |
| Proximity server | [proximity-server-system-design.md](./proximity-server-system-design.md) |
| Chatbot service (multiple information kinds) | [chatbot-service-system-design.md](./chatbot-service-system-design.md) |
| API operating across multiple servers | [multi-server-api-system-design.md](./multi-server-api-system-design.md) |
| Redesign an existing NVIDIA system | [redesign-existing-nvidia-system-system-design.md](./redesign-existing-nvidia-system-system-design.md) |
| Platform such as Facebook or Uber | [social-or-rideshare-platform-system-design.md](./social-or-rideshare-platform-system-design.md) |

---

## Hardware, OS, and low-level design

| Problem | File |
|---------|------|
| Fixed-size-block memory manager (no malloc/free/new/delete) | [fixed-block-memory-manager-lld-system-design.md](./fixed-block-memory-manager-lld-system-design.md) |
| General memory allocator | [memory-allocator-lld-system-design.md](./memory-allocator-lld-system-design.md) |
| Control signal crossing power/clock domains (SoC) | [soc-clock-domain-crossing-lld-system-design.md](./soc-clock-domain-crossing-lld-system-design.md) |
| Minimal shader-compilation pipeline (+ graphics API compare) | [shader-compilation-pipeline-lld-system-design.md](./shader-compilation-pipeline-lld-system-design.md) |
| Git branching and release strategy for a graphics repository | [graphics-git-branching-release-system-design.md](./graphics-git-branching-release-system-design.md) |
| Bootstrap first Kubernetes deployment in a new cloud | [k8s-bootstrap-new-cloud-system-design.md](./k8s-bootstrap-new-cloud-system-design.md) |
| Extend LRU cache (serialization, multithreading, CUDA/LFU) | [lru-cache-extensions-lld-system-design.md](./lru-cache-extensions-lld-system-design.md) |

---

**Prep priority (backend / cloud / AI infra):** GPU job scheduler → compute-cluster control plane → GPU telemetry → distributed inference → distributed training → artifact store → shared cloud FS → proximity / counters. For graphics/CUDA/compiler/hardware roles, **role description overrides** this order completely.
