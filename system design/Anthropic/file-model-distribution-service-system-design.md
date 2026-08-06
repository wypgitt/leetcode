# System Design: File / Model Distribution Service

> **Focus areas:** Regional replication · Merkle integrity · Resumable downloads · Blue/green rollout · Atomic cutover  
> **Style:** Platform service design with progressive scale (10× → 100× → 1,000×)  
> **Company theme:** Ordinary distributed systems inside AI infra — reliability, safety of artifacts, cost of WAN  
> **Sibling:** Cluster-local *weight fanout* is a consumer of this service; this doc owns **publish, replicate, version, cut over**  
> **Quality bar:** Explicit invariants for atomic pointer flips, correct resume semantics, multi-region math

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

Goal: **bound the product**—a multi-region **file/model distribution service** that stores immutable model (and related) artifacts, replicates them to regions, serves integrity-checked resumable downloads to clusters/tools, and coordinates **safe rollouts** with atomic cutover.

### 1.0 Service vs last-mile fanout

| Dimension | **This service** | **Weight distribution (sibling)** |
|-----------|------------------|-----------------------------------|
| Scope | Global/regional platform | Cluster overlay to GPUs |
| Source of truth | Manifest + object store | Consumes manifests/URLs |
| Rollout | Blue/green **pointers** / channels | Byte fanout + Ready |
| Clients | Train/infer clusters, eval, researchers, edge | Node agents |
| Hard problem | Consistency of “what is prod”, WAN replicate | Torus/P2P bandwidth |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What artifacts? | Model weights, tokenizers, adapters, safety classifier packs, config bundles | Generic content-addressed blobs + typed manifests |
| F2 | Who publishes? | Training pipelines, release eng, safety | Authz roles; signed publish |
| F3 | Who consumes? | Regional clusters, batch jobs, canaries | Presigned / mTLS download API |
| F4 | Regions? | 3+ regions active | Async replicate + read locality |
| F5 | Integrity? | Merkle tree / root hash; end-to-end | Verify on upload + download |
| F6 | Resume? | Yes — multi-GB/TB | Range GETs + chunk receipts |
| F7 | Rollout? | Blue/green channels: `staging`, `prod`, `canary` | Atomic pointer updates |
| F8 | Cutover? | Instant pointer flip after readiness | Compare-and-swap channel head |
| F9 | Rollback? | One click to previous prod pointer | Immutable versions; pointer history |
| F10 | Lifecycle? | Retain N versions; legal hold hooks | GC with refcounts from channels |
| F11 | Metadata search? | List by model family, created_at, labels | Metadata index |
| F12 | Encryption? | At rest + TLS; optional customer keys Phase 2 | KMS integration |

**MVP functional scope:**

1. Publish artifact set → content-addressed chunks → Merkle root → signed manifest.  
2. Replicate to configured regions; expose regional readiness.  
3. Resumable download API (chunks / HTTP ranges) with integrity.  
4. Channels (`prod`, `canary`, `staging`) as atomic pointers to `version_id`.  
5. Rollout workflow: promote staging → canary → prod with gates.  
6. Rollback channel pointer; audit log.  
7. Authn/z for publish/download; telemetry.

**Out of MVP:**

- Researcher UI pretty gallery  
- Automatic quality eval (hook only — gates call external eval)  
- P2P inside clusters (delegate to sibling)  
- Cross-cloud multi-provider replication perfection  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Publish durability | Never lose successful publish | Quorum write to object store + metadata commit |
| N2 | Regional freshness | Prod versions available locally | p50 replicate < 15–30 min for 200GB; defend |
| N3 | Download integrity | No silent corruption | Client must verify Merkle (or service streaming verify) |
| N4 | Cutover atomicity | No “half prod” pointer | CAS on channel head |
| N5 | Availability | Reads critical | 99.9% download metadata; multi-region |
| N6 | Resume correctness | Exact byte continuity | Persistent cursor / etag |
| N7 | Auditability | Who flipped prod? | Immutable audit events |
| N8 | Cost | WAN + storage controlled | Single replicate per region; dedupe by hash |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Training job publishes `model@sha` → replicate 3 regions → staging pointer → canary channel → eval green → CAS prod.  
2. Cluster agent downloads with resume after preemption.  
3. Rollback prod to previous version in < 1 minute (pointer only; bytes already local).  
4. Safety pack update published independently; models reference pack hash.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Publish crash after blobs, before manifest commit | GC orphan blobs; no version visible |
| Replicate lag in region B | Region B not in `ready_regions`; refuse prod promote if policy requires all |
| Dual promote race | CAS generation / etag fails loser |
| Client resumes with wrong etag | 409; restart or revalidate |
| GC deletes live version | Refcount from channels + grace; forbidden |
| Partial region outage | Serve from nearest ready region; warn latency/cost |
| Manifest signature fail | Reject download authorization |
| Huge burst downloads post-cutover | Redirect to regional caches / weight fanout plane |
| Rollback during canary | Canary pointer independent of prod |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Artifact versions stored | 5K | 50K | 500K | 5M |
| Avg artifact size | 200 GB | 200GB–1TB | mixed | mixed + many LoRA |
| Regions | 3 | 5 | 10 | 20+ |
| Peak publishes / day | 50 | 500 | 5,000 | 50,000 |
| Peak download starts / min | 100 | 1,000 | 10,000 | 100,000 |
| Concurrent rollout channels | 20 | 200 | 2,000 | multi-tenant |
| Metadata QPS | 1K | 10K | 100K | cell-sharded |
| WAN replicate GB/day | 10 TB | 100 TB | 1 PB | hierarchical tiering |

**What each jump forces:**

- **10×:** Metadata DB indexing; async replicate workers; CDN edge for smaller artifacts.  
- **100×:** Shard metadata; per-tenant quotas; dedicated replicate backbones.  
- **1,000×:** Federation; cold archive tier; chunk dedupe across fine-tunes; policy engine.

### 1.5 Etc.

- Object store is blob persistence; service owns **manifest + channel semantics**.  
- Clusters still run sibling P2P for last mile — this service must not become single TCP bottleneck for 10k GPUs (presign + regional + handoff).  
- Anthropic lens: **atomic cutover** and **integrity** protect safety-critical model changes.

**Scope statement:**

> Design a multi-region file/model distribution service: content-addressed chunk storage with Merkle integrity, resumable downloads, regional replication readiness, and channel-based blue/green atomic cutover with audit and rollback—scaling publishes and downloads through 10×/100×/1,000× while keeping WAN and origin costs sane.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Storage

- 5,000 versions × 200 GB = **1 PB** logical; with 3-region copy ≈ **3 PB** raw (before erasure coding).  
- Dedup: if finetunes share 70% chunks, effective storage drops materially — worth Merkle/CAS.

### 2.2 Replicate time (single 200GB version → new region)

At 5 Gbps effective inter-region:

\[
T = \frac{200 × 8\ \text{Gb}}{5\ \text{Gb/s}} = 320\ \text{s} ≈ 5.3\ \text{min}
\]

At 1 Gbps: ~27 min. Interview: **quote bandwidth assumption**.

### 2.3 Cutover vs copy

- Pointer CAS: milliseconds.  
- Users feel cutover delay only if regions not warmed — **pre-warm is the real SLO**, not the flip.

### 2.4 Metadata size

- Manifest 1563 chunks × 40 B ≈ 60 KB; 500K versions ≈ 30 GB manifests + indexes — fits in distributed SQL / KV.

### 2.5 Download stampede after prod flip

- 2,000 nodes × 200 GB = 400 TB logical; if all hit this service’s origin → death.  
- Math forces **handoff to cluster weight distribution** after first regional seed fill.

### 2.6 GC savings

- Keep prod + previous + canary + N staging; delete unreferenced after 14 days.  
- Refcount channels + pinned eval runs.

### 2.7 Request rates

- Metadata GetChannel: 1k QPS easy for Redis/SQL.  
- Blob traffic: object store / regional cache, not app servers.

---

## 3. High-Level Design

### 3.1 Core concepts

```text
BlobChunk     = content-addressed bytes (digest = id)
MerkleTree    = tree over chunk digests
ArtifactVersion = {version_id, root_hash, merkle, metadata, signature, size}
Channel       = {name, head_version_id, generation, updated_by, updated_at}
RegionReplica = {version_id, region, state: PENDING|COPYING|READY|FAILED, progress}
Rollout       = {id, channel, from, to, gates[], state}
```

### 3.2 Components

| Component | Responsibility |
|-----------|----------------|
| Publish API | Authz, init upload, commit version |
| Chunk Ingest | Multipart / parallel put; verify digests |
| Metadata Store | Versions, channels, merkle pointers, audit |
| Replicator | Cross-region copy; update RegionReplica |
| Download API | Authz, presign, resume tokens, merkle proofs |
| Rollout Controller | Gate checks; CAS promote; rollback |
| Regional Cache / Seeds | Hot versions near clusters |
| GC Worker | Orphan and unreferenced cleanup |
| Audit Log | Immutable promote/rollback events |
| Policy Engine | Required regions, approvals, SODs |

### 3.3 Publish protocol

```text
1. POST /versions/init -> upload_id, chunk_plan
2. PUT chunks (parallel) with digest headers
3. Server verifies digest == address
4. POST /versions/commit {merkle_root, signature, metadata}
5. Transaction: insert ArtifactVersion ONLY if all chunks present
6. Enqueue replicate tasks to regions
```

**Invariant:** No `version_id` is listable until commit succeeds.

### 3.4 Merkle trees

- Leaf = chunk digest; internal nodes = hash(left|right).  
- Download can request **inclusion proof** for chunk i against root.  
- Root embedded in signed manifest.  
- Benefits: partial verify, resume trust, dedupe, corruption isolation.

### 3.5 Resumable downloads

Options:

| Mechanism | Pros | Cons |
|-----------|------|------|
| HTTP Range on blob files | Simple | Weaker per-chunk crypto UX |
| Chunk API `GET /chunks/{digest}` | Natural CAS | More chatty |
| Resume token (bitmap cursor) | UX friendly | Stateful |

**MVP:** Chunk API + client bitmap; optional packaged tar with ranges for small artifacts.

Resume token:

```text
{version_id, etag: root_hash, completed: [chunk_indices], exp}
```

If `etag` mismatches (shouldn’t for immutable version), restart.

### 3.6 Regional replication

```text
on commit(version):
  for region in targets:
    enqueue CopyJob(version, region)
CopyJob:
  ensure chunks missing in region bucket
  copy via inter-region pipe / object replicate
  verify sample or full merkle
  mark READY
```

**Promote policy example:** `prod` requires `READY` in {us-east, us-west, eu-west}.

### 3.7 Blue/green & atomic cutover

Channels are **pointers**, not copies:

```text
prod.head = v41 (green)
staging.head = v42
canary.head = v42
# after gates:
CAS prod.head from v41 -> v42 (generation++)
```

Blue/green serving:

- Inference control plane reads `channel=prod` → `version_id` → cluster desired version.  
- Old version bytes remain until GC — instant rollback.

**Atomicity:** single metadata CAS; workers may still run mixed versions until their orchestrators converge — that is expected; **channel read** is atomic.

### 3.8 Rollout state machine

```text
DRAFT → WARMING_REGIONS → REGIONS_READY → CANARY_POINTED
  → GATES_RUNNING → GATES_PASSED → PROD_CAS
  → COMPLETED
Any → ABORTED / ROLLED_BACK
```

Gates (external): error rate, safety eval, latency, human approval.

### 3.9 Authz model

| Action | Who |
|--------|-----|
| Publish to staging | Training CI role |
| Point canary | Release eng / automated rollout |
| Point prod | Restricted + approvals (2-person for frontier) |
| Download prod | Cluster identity / job identity |
| Delete | GC only; humans pin/unpin |

### 3.10 Trade-offs

| Topic | Options | Choice |
|-------|---------|--------|
| Metadata DB | Postgres vs etcd vs Spanner | Postgres + Redis cache MVP; Spanner-class at 100× |
| Replicate | Object store native vs app copy | Native when available; app verify |
| Cutover | DNS vs pointer | **Pointer in metadata** |
| Dedup | File vs chunk | Chunk CAS |
| Client verify | Optional vs mandatory | Mandatory for model class |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +------------------+     +--------------------+
| Publishers  |---->| Publish API      |---->| Metadata Store     |
+-------------+     | + Rollout Ctrl   |     | versions/channels  |
                    +--------+---------+     +---------+----------+
                             |                         |
                             v                         v
                    +----------------+        +--------+----------+
                    | Object Store   |<------>| Replicator Workers|
                    | (per region)   |        +--------+----------+
                    +--------+-------+                 |
                             |                         v
                             |              +----------+----------+
                             |              | Region READY table  |
                             |              +---------------------+
                             v
                    +----------------+     +----------------------+
                    | Download API   |---->| Regional Seeds/CDN   |
                    +--------+-------+     +----------+-----------+
                             |                        |
                             v                        v
                      Cluster Agents / Weight Fanout Plane
```

### 4.2 Channel cutover sequence

```text
ReleaseEng → RolloutCtrl: promote prod to v42
RolloutCtrl → Meta: read region_ready(v42)
RolloutCtrl → Gates: run eval
Gates → OK
RolloutCtrl → Meta: CAS prod.head v41→v42 gen=7
Meta → Audit: append
InferControl → Meta: GET prod → v42
InferControl → Clusters: desired=v42
Clusters → Download/Seeds: fetch v42 (if not cached)
```

### 4.3 Resume download

```text
Agent: GET manifest(v42) -> root, leaves
Agent: has bitmap 0..900
Agent: GET chunks 901..N (parallel)
Agent: verify each vs leaf; optional merkle proof
Agent: complete -> hand to runtime / P2P seed role
```

### 4.4 Replicate data path

```text
us-east bucket (chunks) --object replicate--> eu-west bucket
Replicator: verify root sample
Meta: RegionReplica{eu-west}=READY
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Content addressing:** `digest` is identity; never overwrite bytes at an address.  
2. **Commit atomicity:** version visible iff all chunks + signature OK.  
3. **Channel CAS:** prod head changes only via compare-and-swap on generation.  
4. **Region READY ⇒ merkle verified** (full or probabilistic policy stated).  
5. **GC never deletes** version referenced by channel or grace pin.  
6. **Audit every promote/rollback** with actor + reason.  
7. **Download authz** checked before presign.  
8. **Resume etag** bound to root_hash.  
9. **Rollback always possible** if previous bytes retained (policy).  
10. **Handoff:** service must not require per-GPU unicast from origin.

**Failures:**

| Failure | Behavior |
|---------|----------|
| Replicator crash | Job retry idempotent by chunk digest | 
| Metadata primary down | HA failover; cutover paused if CAS unavailable |
| Region permanently dark | Policy: promote with degraded region set + alert; or block |
| Presign leak | Short TTL; audience-bound tokens |
| Partial upload abandon | TTL purge orphans |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Monolith API, 1 PG, 3 buckets, workers |
| 10× | Separate publish/download; Redis channel cache; queue for replicate |
| 100× | Shard metadata by model_family; parallel replicate graph; CDN for small files |
| 1,000× | Federated regional control planes; cold Glacier-class tier; chunk gossip dedupe |

**Download scalability pattern:**

```text
Client → Download API (auth + manifest)
      → Regional object store / seed (bulk bytes)
      → Cluster P2P (sibling) for fanout
```

### 5.3 Maintainability

- Schema versioning for manifests.  
- Rollout policies as data (YAML) reviewed in PR.  
- Shadow promote in staging env.  
- Metrics: `replicate_lag_seconds`, `cas_fail`, `download_bytes`, `orphan_gc`, `prod_flips`.  
- SLOs separate for **metadata** vs **bulk transfer**.

### 5.4 Blue/green deep dive

**Myth:** blue/green means two full clusters always.  
**Here:** two (or more) **immutable versions** + traffic/channel pointer. Clusters may be draining.

States:

```text
Green (prod v41) serving
Blue (v42) warming regions + canary channel traffic split 1%
Flip prod pointer → orchestrators converge
Drain v41; keep bytes for rollback window
```

**Atomic cutover** = atomic **intent**. Serving convergence is orchestrated separately with maxSurge/maxUnavailable style.

### 5.5 Integrity deep dive

Upload path:

```text
client computes digest → PUT → server rehashes → mismatch 400
commit supplies root → server recomputes merkle from known leaves → mismatch 400
sign(root, metadata) verify with publisher key
```

Download path:

```text
mandatory client verify leaf digests
optional: mid-tree proofs for partial trust audits
```

### 5.6 Resumability correctness

- Immutable version ⇒ resume safe.  
- Never resume across different `version_id`.  
- Chunk rewrite forbidden — if corruption detected, re-fetch same digest from another region.  
- Server-side incomplete multipart uploads ≠ versions.

### 5.7 Cost controls

| Lever | Mechanism |
|-------|-----------|
| WAN | Replicate once per region; compress if helpful (weights often poorly compressible) |
| Storage | Chunk dedupe; TTL GC; archive cold |
| Requests | Manifest cache; long-lived cluster seeds |
| Stampede | Coordinate with weight distribution; staggered desired_version |

### 5.8 Safety & compliance angle (Anthropic)

- Production channel flips for frontier models may require **safety eval gates** + human approval.  
- Audit log is a safety artifact.  
- Separate channels for **safety classifiers** vs base models — independent cadence.  
- Prevent “stealth prod” by denying direct prod publish; only promote.

### 5.9 Consistency

- **Strong** read-after-write for publisher in home metadata region.  
- Channel GET: strongly consistent CAS store (Spanner/etalcd/PG primary).  
- Cross-region metadata: if multi-master hard — **single writer metadata** + regional caches with short TTL for downloads; flips go through primary.

**Recommendation:** single metadata primary (or consensus group) for channels; blobs multi-region.

### 5.10 API sketch

```text
POST   /v1/versions/init
PUT    /v1/uploads/{id}/chunks/{digest}
POST   /v1/versions/commit
GET    /v1/versions/{version_id}
GET    /v1/versions/{version_id}/merkle
GET    /v1/channels/{name}
POST   /v1/channels/{name}/cas  {expected_gen, version_id}
POST   /v1/rollouts
GET    /v1/regions/{region}/versions/{id}/status
GET    /v1/downloads/{version_id}/chunks/{digest}  # authz + redirect
```

### 5.11 GC algorithm

```text
roots = all channel heads ∪ pinned_versions ∪ recent_prod_history(K)
mark reachable chunk digests via merkle leaves
sweep unreferenced chunks older than grace
never sweep READY region copies still referenced
```

### 5.12 Multi-tenant (100×)

- `tenant_id` on versions; quotas on storage and egress.  
- Cross-tenant digest dedupe optional (side channel risk — often disable for secrets).  
- For internal Anthropic, multi-team rather than multi-customer — still quota.

---

## 6. Wrap-Up

### 6.1 What we designed

A **file/model distribution service** that publishes content-addressed, Merkle-verified artifacts, replicates them to regions with explicit READY, serves resumable authorized downloads, and coordinates **blue/green channel pointers** with **atomic CAS cutover**, audit, and rollback—while handing last-mile GPU fanout to the cluster weight distribution plane.

### 6.2 Key decisions

1. **CAS chunks + Merkle root** as integrity spine.  
2. **Commit-atomic version visibility.**  
3. **Channels as pointers**, not recopies.  
4. **CAS generation** for prod flips.  
5. **Region READY gate** before promote.  
6. **Resume via immutable digests.**  
7. **Single metadata authority** for cutover.  
8. **Handoff bulk bytes** to seeds/P2P.  
9. **GC by refcount + grace.**  
10. **Safety gates + audit** on prod.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Metadata hotspot | Shard / Spanner |
| Replicate lag surprises | Pre-warm SLOs; block promote |
| Stampede on flip | Orchestrator stagger + P2P |
| Accidental GC | Pin + dry-run GC |
| Signing key | HSM, dual control |

### 6.4 One-minute closer

> This service is the **source of truth for what model bytes exist and which pointer is prod**. Integrity is Merkle+signatures; rollout is atomic channel CAS; speed at the GPU edge is someone else’s overlay—but readiness is ours.

---

## 7. Deeper / Related Interview Questions

### 7.1 Basics

1. Why content-addressed storage for models?  
2. Channel pointer vs rewriting a `latest/` object key?  
3. How do Merkle proofs help resume?  
4. Difference between region READY and cluster Ready?

### 7.2 Rollout

5. Design 1% canary traffic with channels.  
6. Dual control for prod flip — data model?  
7. Rollback SLA of 60s — what’s actually needed warm?  
8. How to avoid split-brain prod in two metadata replicas?

### 7.3 Scale & cost

9. 1PB replicas — erasure coding vs 3× copy?  
10. Dedup security risks across tenants.  
11. Inter-region bandwidth budgeting.  
12. Metadata at 100k QPS.

### 7.4 Failure drills

13. Commit succeeds, replicate stuck 2/3 regions — promote or not?  
14. CAS storm from buggy CI.  
15. Corrupt object store bitrot detected at read — repair path.  
16. Publisher key compromise playbook.

### 7.5 EM / mentoring

17. Junior wants mutable `s3://models/prod.bin` — coaching.  
18. Prioritize resume vs merkle UX vs UI?  
19. SLOs you’d report weekly to leadership.  
20. How this pairs with inference safety releases.

### 7.6 Sample answers (brief)

**Q2:** Mutable `latest` invites torn reads and cache poisoning; immutable version + atomic pointer gives rollback, audit, and safe CDN caching by digest.

**Q13:** Policy-driven: frontier prod requires all critical regions READY; experimental channels may allow majority. Never silently serve incomplete region without orchestrator awareness.

---

## Appendix A: Manifest schema

```json
{
  "version_id": "mdl_01H...",
  "family": "frontier-x",
  "root_hash": "blake3:...",
  "chunk_size": 134217728,
  "leaves": ["blake3:...", "..."],
  "artifacts": [{"name": "tp0.safetensors", "chunks": [0,1,2]}],
  "publisher": "train-job-123",
  "signature": "ed25519:...",
  "created_at": "2026-08-05T00:00:00Z"
}
```

## Appendix B: Channel record

```json
{
  "name": "prod",
  "head": "mdl_01H...",
  "generation": 42,
  "prev_head": "mdl_01G...",
  "updated_by": "rollout-bot",
  "updated_at": "..."
}
```

## Appendix C: Rollout policy YAML

```yaml
channel: prod
require_regions: [us-east, us-west, eu-west]
canary_channel: canary
gates:
  - type: external_eval
    id: safety-smoke
  - type: human_approval
    group: release-managers
cas:
  max_retries: 3
rollback_window_days: 14
```

## Appendix D: State machines (compact)

**Version:** `UPLOADING → COMMITTED → REPLICATING → ACTIVE → ARCHIVED → TOMBSTONED`

**RegionReplica:** `PENDING → COPYING → VERIFYING → READY → FAILED`

**Rollout:** see §3.8

## Appendix E: Client download library contract

```text
open(version_id) -> Manifest
ensure_chunks(required_set, concurrency)
verify_root()
path = materialize()  # optional
```

Must be usable by weight-distribution agents.

## Appendix F: Comparison table — cutover mechanisms

| Mechanism | Atomic? | Rollback | Cache safety |
|-----------|---------|----------|--------------|
| Overwrite latest.bin | No | Hard | Bad |
| DNS flip | Approx | Medium | Medium |
| Config map version | Yes if CAS | Easy | Good |
| Channel generation CAS | Yes | Easy | Best |

## Appendix G: Progressive feature checklist

| Scale | Feature |
|-------|---------|
| MVP | Commit, 3-region replicate, channels, resume chunks |
| 10× | Rollout controller, gates, audit UI API |
| 100× | Dedup analytics, shard meta, CDN small artifacts |
| 1,000× | Archive tier, federated regions, policy-as-code |

## Appendix H: Threat model (summary)

| Threat | Mitigation |
|--------|------------|
| Unauthorized prod flip | Authz + approvals + audit |
| Poisoned upload | Digest verify + signature |
| Bitrot | Checksums + scrubber |
| Presign exfiltration | TTL + scoped IAM |
| GC footgun | Refcount + grace + dry-run |

## Appendix I: Worked rollout timeline

| t | Event |
|---|-------|
| 0 | Commit v42 in us-east |
| 0–8m | Replicate west/eu |
| 8m | Regions READY |
| 8m | canary.head → v42 |
| 8–20m | Eval + human gate |
| 20m | CAS prod → v42 |
| 20–35m | Clusters converge; P2P fanout |
| 20m+14d | v41 eligible for GC if unused |

## Appendix J: SQL sketch (metadata)

```sql
CREATE TABLE versions (
  version_id TEXT PRIMARY KEY,
  root_hash TEXT NOT NULL,
  family TEXT,
  size_bytes BIGINT,
  signature TEXT,
  committed_at TIMESTAMPTZ
);
CREATE TABLE channels (
  name TEXT PRIMARY KEY,
  head TEXT REFERENCES versions(version_id),
  generation BIGINT NOT NULL,
  prev_head TEXT
);
CREATE TABLE region_replicas (
  version_id TEXT,
  region TEXT,
  state TEXT,
  progress REAL,
  PRIMARY KEY (version_id, region)
);
CREATE TABLE audit (
  id BIGSERIAL PRIMARY KEY,
  at TIMESTAMPTZ,
  actor TEXT,
  action TEXT,
  detail JSONB
);
```

CAS:

```sql
UPDATE channels SET head=$new, prev_head=head, generation=generation+1
WHERE name='prod' AND generation=$expected AND head=$old;
```

## Appendix K: Interview whiteboard (15–20 min)

1. Clarify artifacts + channels (2)  
2. Publish/commit invariants (3)  
3. Merkle + resume (3)  
4. Replicate READY (3)  
5. CAS cutover + rollback (4)  
6. Stampede handoff to P2P (3)

## Appendix L: Metrics & alerts

```text
replicate_lag_seconds{region} > 3600
cas_conflicts > baseline
download_4xx_auth spike
gc_ref_violation (should be 0)
prod_flip_without_gate (should be 0)
```

## Appendix M: Why this is an Anthropic-style question

Tests whether you separate **global artifact truth** from **cluster fanout**, treat **model prod** like a safety-sensitive config pointer, and still do classic multi-region storage engineering with integrity and cost discipline.

## Appendix N: FAQ rapid fire

**Q: Store models in Git LFS?** A: Poor for TB + regional + CAS cutover.  
**Q: Only use HuggingFace Hub?** A: Similar ideas; interview wants your invariants.  
**Q: Is Kafka needed?** A: Useful for replicate events/audit; not bulk bytes.  
**Q: Sync or async replicate?** A: Async with READY gate.  
**Q: Can prod point to non-READY region?** A: Default no for critical channels.

## Appendix O: Integration with weight distribution

```text
Distribution Service: prod -> v42, regions READY
Orchestrator: set desired=v42
Seed Service: pull from regional bucket (presigned)
Node agents: P2P fanout (sibling design)
Orchestrator: serving% on v42
```

Contract: **this service guarantees bytes+pointer; sibling guarantees TTR inside cluster.**

## Appendix P: Encryption & KMS

- SSE-KMS on buckets; TLS in transit.  
- Manifest signatures orthogonal to encryption.  
- Future: per-model CMK; rewrap on tenant move — Phase 2.

## Appendix Q: Small artifacts path

Tokenizers (MBs) can use CDN edge caching by digest; still immutable. Don’t force P2P for tiny files.

## Appendix R: Testing strategy

- Property test: random chunk corruption detected.  
- Jepsen-ish: CAS under partition.  
- Chaos: kill replicator mid-copy; ensure READY only after verify.  
- Soak: stampede download 10k clients → ensure redirects to seeds.

## Appendix S: Ownership boundaries

| Concern | Owner |
|---------|-------|
| What is prod? | This service channels |
| Are GPUs warm? | Weight distro + orchestrator |
| Is model safe? | Eval gates / safety eng |
| Traffic split % | Inference router |

## Appendix T: One-page invariants card (print for interview)

1. Bytes immutable at digest.  
2. Version invisible until commit.  
3. READY ⇒ verified in region.  
4. Prod flip = CAS(generation).  
5. Rollback = CAS to prev.  
6. GC respects refs.  
7. Bulk path ≠ metadata path.  
8. Audit always on.

---

*End of File/Model Distribution Service system design.*
