# System Design: GitHub Actions–like CI

> **Focus areas:** Workflow DAGs · Job matrix · Runners (hosted/self-hosted) · Queueing · Isolation · Artifacts · Secrets · Cache · Log streaming · Retries · OIDC · Fairness · Bursty scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split dissimilar QPS classes, explicit invariants, resolved ownership of workflow state vs runner execution

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

Goal: **bound the product**—YAML workflows compiled to DAGs, jobs executed on isolated runners, with artifacts/secrets/logs, fair multi-tenant scheduling under bursty CI.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who triggers runs? | git push, PR, schedule, `workflow_dispatch`, repository_dispatch | Event ingress + dedupe |
| F2 | Workflow definition? | YAML in repo: jobs, `needs`, matrix, services, steps | Parse → validate → DAG |
| F3 | Job matrix? | Expand OS/version dimensions with exclude/include | Matrix expander; fan-out jobs |
| F4 | Runners? | GitHub-hosted + **self-hosted** labels | Dual pools; different trust |
| F5 | Isolation? | Ephemeral VM/container per job for hosted | No cross-job FS leak on hosted |
| F6 | Artifacts? | Upload/download between jobs; retention TTL | Object store + ACL by run |
| F7 | Secrets? | Repo/org/env secrets; masked logs | Inject at job start; redaction |
| F8 | Cache? | Dependency caches keyed by hash | Cache service; eviction; poison resistance |
| F9 | Logs? | Step logs stream live; downloadable after | Log stream service; object archive |
| F10 | Retries / reruns? | Re-run failed jobs/workflow; step retry limited | New attempts; idempotent side effects guidance |
| F11 | OIDC to cloud? | Federated AWS/GCP/Azure creds without long-lived keys | OIDC issuer + audience claims |
| F12 | Concurrency controls? | `concurrency` groups cancel-in-progress | Control-plane cancel + runner interrupt |

**MVP functional scope (lock with interviewer):**

1. Parse workflow YAML → validated DAG of jobs (with `needs` + matrix expansion).
2. Queue jobs when dependencies satisfied; match runners by labels.
3. Hosted runners: ephemeral isolated execution; pull repo at ref; run steps.
4. Secrets injection + log masking; artifact upload/download; basic cache.
5. Live log streaming; terminal statuses; rerun failed jobs.
6. Org/repo concurrency quotas; fairness across repos.
7. OIDC token minting for cloud roles (thin but real).

**Out of MVP (explicitly defer):**

- Full marketplace of trusted Actions with supply-chain attestation (design hooks)
- Windows/macOS fleets detail (mention SKU labels)
- Perfect exactly-once deploy side effects (user idempotency)
- Multi-region active-active mutation of the same run

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Queue wait (hosted, normal load)? | Minutes at worst, seconds typical | p50 < 30s, p99 < 3m baseline (SKU-dependent) |
| N2 | Start isolation? | Fresh environment | No secret/file leakage across jobs |
| N3 | Durability? | Accepted runs not lost | Workflow run durable before ACK to git event |
| N4 | Log durability? | After step completes, logs retained per policy | Stream may lose tail on crash; finalize upload |
| N5 | Fairness? | Monorepo ≠ starve everyone | Weighted fair queues / shuffle sharding |
| N6 | Burst absorption? | Monorepo stampede / dependency update | Elastic runners + admission control |
| N7 | Cancel latency? | Cancel-in-progress feels prompt | p99 < 15–30s cooperative interrupt |
| N8 | Multi-tenant security? | Untrusted PR code from forks | Fork PR secret restrictions; approval gates |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Push to `main` → workflow run created → jobs DAG → build → test matrix → upload artifact → deploy job with OIDC.
2. PR from fork → run without secrets → maintainers approve → re-run with secrets (policy).
3. Failed test job → rerun failed jobs → cache hit → pass.
4. `concurrency: prod` → new run cancels previous in-progress deploy.
5. Self-hosted runner labeled `gpu` picks ML job.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Invalid YAML | Fail run at parse; surface errors |
| Matrix explosion (10k jobs) | Cap expansion; reject or require approval |
| Runner dies mid-step | Job failure / retry policy; lease expiry reclaim |
| Secret in log | Masker redacts known values; advise against echo |
| Artifact > size quota | Reject upload; fail step |
| Cache poison (bad deps) | Key isolation; allow delete; checksum optional |
| Duplicate delivery of git webhook | Idempotent run creation by `(repo, event_id)` or delivery id |
| Cancel vs job just finished | CAS terminal; cancel no-op if done |
| Starvation of small repos | Fair dequeue across tenants |
| OIDC audience mismatch | Token mint fails closed |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Orgs / repos (active) | 50K repos | 500K | 5M | 50M |
| Workflow runs / day | 5M | 50M | 500M | 5B |
| Jobs / day | 20M | 200M | 2B | 20B |
| Peak job **starts**/s | ~500 | ~5K | ~50K | ~500K |
| Peak concurrent running jobs | 50K | 500K | 5M | 50M |
| Avg job duration | 5 min | 5 min | 5 min | 5 min |
| Log ingest GB/day | ~50 | ~500 | ~5K | ~50K |
| Artifact write GB/day | ~20 | ~200 | ~2K | ~20K |
| Cache ops/s peak | ~1K | ~10K | ~100K | ~1M |
| Webhook ingress peak | ~1K/s | ~10K/s | ~100K/s | ~1M/s |

**What each jump forces:**

- **10×:** Job queue partitions; elastic hosted pools; log/object pipelines; Redis leases.
- **100×:** Shuffle-sharded queues; regional runner pools; artifact CDN; workflow control-plane cells by shard_id(repo).
- **1,000×:** Global directory; heavy admission control; spot capacity; log tiering; dedicated whale monorepo cells.

### 1.5 Etc. (Constraints & Assumptions)

- We design **Actions-like CI**, not full GitHub (PRs/issues are event sources).
- Hosted runners are **ephemeral**; self-hosted are customer-operated with registration tokens.
- Actions (reuse steps) are container/JS runners—supply chain noted but not full product.
- Single primary cloud for hosted MVP; multi-region DR for control plane.

**Scope statement:**

> Design a GitHub Actions–like CI system: event-driven workflow DAG execution on hosted/self-hosted runners with matrix jobs, secrets, artifacts, caches, log streaming, retries/reruns, OIDC, and multi-tenant fairness—from ~50K concurrent jobs through 10× / 100× / 1,000× bursty scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 1,000× | Store |
|-------|------|---------------|--------|-------|
| **Webhook / event ingress** | git events | ~1K/s | ~1M/s | Ingress + idempotency |
| **Control-plane mutations** | create run, job state | ~2K/s | ~2M/s | Postgres/cells |
| **Job dequeue / lease** | runner claims | ~500/s | ~500K/s | Queue + Redis |
| **Heartbeats** | runner alive | ~50K/s | ~50M/s | Aggregators (not PG) |
| **Log append** | stream chunks | ~20K/s | ~20M/s | Log service / object |
| **Artifact PUT/GET** | blobs | bursty | extreme | Object store |
| **Cache GET/PUT** | deps | ~1K/s | ~1M/s | Cache store |

**Anti-pattern:** “CI is 500 QPS” while heartbeats alone are 50K/s.

### 2.2 Concurrent capacity

```text
50K concurrent jobs × 2 vCPU = 100K vCPU hosted (order)
If avg utilization 50% packing inefficiencies → more
Self-hosted not on your bill but still control-plane heartbeats
```

### 2.3 Matrix amplification

```text
1 workflow run × matrix 3 OS × 4 versions = 12 jobs
Plus needs: build → 12 tests → deploy
Peak starts ≠ peak runs
Always estimate jobs, not only workflow runs
```

### 2.4 Logs

```text
Avg 5 MB logs/job × 20M jobs/day = 100 TB/day raw? 
Wait—tune: many jobs are tiny.
Use blended 2.5 MB → 20M × 2.5 MB = 50 TB/day at baseline? Still high.
Recalibrate baseline:
  20M jobs/day × 0.5 MB avg = 10 TB/day logs baseline
  1,000× → 10 EB/day absurd without compression/retention
→ compression, sampling debug logs, retention 14–90 days, cold tier
```

**Always pair log volume with retention.**

### 2.5 Queue wait math

```text
λ starts = 500/s, μ capacity = 520/s → stable small wait
Spike λ = 5K/s for 2 min while μ = 800/s → backlog  (5K-800)*120 ≈ 504K jobs queued
→ admission + fairness + elastic scale-out critical
```

### 2.6 Heartbeat aggregation

```text
50K jobs × 1 HB/s = 50K/s — Redis OK
50M/s — must aggregate at runner proxy / regional agents
```

---

## 3. High-Level Design

### 3.1 Product surfaces

```text
+---------------------------------------------------------------------+
| repo/payments  Actions   Run #18422  push  main  ● in_progress      |
+------------------+--------------------------------------------------+
| Workflows        | Jobs DAG                                         |
| CI               |   [build] ──┬── [test (ubuntu)]                  |
| Deploy           |             ├── [test (macos)]                   |
|                  |             └── [test (windows)] ── [deploy]     |
|                  | Logs: Step "npm test" .............. streaming   |
|                  | Artifacts: coverage.zip   Cache: npm-hit         |
+------------------+--------------------------------------------------+
```

### 3.2 Domain model

```text
Repository
 └── Workflow (path, YAML identity)
      └── WorkflowRun (run_id, event, sha, status, actor)
           └── Job (job_id, name, needs[], matrix_attrs, labels, status)
                └── Step[] (runtime record)
                └── Attempts[] (retries/reruns)
           └── Artifacts[], Caches (refs), Logs
```

**Ownership (resolved):**

| Concern | SoT Owner |
|---------|-----------|
| Run/job desired state & DAG | **Control plane** (DB) |
| Who executes job now | Runner lease (`runner_id` + fencing token) |
| Step logs bytes | Log service / object store |
| Secrets values | Secret store (encrypted); not logs DB |
| Artifacts bytes | Object store |
| Cache bytes | Cache object store + index |
| OIDC private key | KMS-backed issuer |

**Deal-breaker:** runner as SoT for workflow graph; or secrets written to artifacts by platform default.

### 3.3 YAML → DAG

```text
1. Fetch workflow files at commit SHA (trusted content store)
2. Parse YAML + expression eval context (github/event/env)
3. Validate schema, permissions, max jobs
4. Expand matrix → concrete jobs
5. Build DAG from `needs` (detect cycles → fail)
6. Persist WorkflowRun + Jobs (blocked|queued|...)
7. Enqueue jobs with indegree 0
```

**Matrix expansion caps:** e.g. max 256 jobs/run (configurable)—deal-breaker if unbounded.

### 3.4 Job state machine

```text
blocked → queued → leased → in_progress → completed|failed|cancelled
                              │                 ↘ skipped (policy)
                              └──→ queued (retry/requeue on runner loss)
```

**Orchestration:** when job terminal, decrease dependents’ indegree; enqueue ready; if `if:` conditions fail → skipped.

### 3.5 Queueing & fairness

| Approach | Pros | Cons | When |
|----------|------|------|------|
| Global FIFO | Simple | Starvation by whales | Never multi-tenant alone |
| Per-repo queues | Isolation | Unfair weight; ops heavy | Partial |
| **Weighted fair / shuffle sharding (chosen)** | Good fairness | More complex | Multi-tenant CI |
| Priority (PR vs schedule) | UX | Starvation if mistuned | Add tiers |

```text
dequeue:
  pick shard(s) randomly (shuffle sharding)
  among pending, weighted by org plan / fairness credits
  match labels to available runners
```

**Concurrency groups:** map `concurrency.group` → active run; cancel older if `cancel-in-progress`.

### 3.6 Runners: hosted vs self-hosted

| | Hosted | Self-hosted |
|---|--------|-------------|
| Isolation | Ephemeral VM/microVM/container per job | Customer responsibility (warn) |
| Scaling | Platform autoscaler | Customer capacity |
| Labels | `ubuntu-latest` etc. | Custom labels |
| Trust | Platform images | Higher risk if shared |
| Network | Egress policy | Customer network / OIDC |

**Hosted isolation choice:** ephemeral VM/microVM preferred for untrusted PR code; containers with strong sandbox acceptable if threat model stated.

**Runner agent loop:**

```text
register → poll/claim job (lease) → download scripts/actions →
inject secrets → run steps → stream logs → upload artifacts →
heartbeat → finalize status → release
```

### 3.7 Secrets injection

```text
Control plane resolves secret refs allowed for this run context
  (repo/org/environment + fork rules)
Mint short-lived delivery envelope to runner over TLS
Runner exposes as env / files; scrub process list best-effort
Log masker applies secret values + patterns
Secrets never persisted in job logs store
```

**Fork PRs:** default no secrets; `pull_request_target` dangers documented; approval gates.

### 3.8 Artifacts & cache

**Artifacts:**

```text
upload → authz run_id → PUT object → index row (name, digest, size, ttl)
download → authz → signed GET
cross-job: same run; cross-run optional with retention
```

**Cache:**

```text
key / restore-keys hierarchy
GET hit → download; miss → job fills → PUT if still owner
Eviction: LRU per repo quota
Poison: allow `cache delete`; prefer immutable keys with hash of lockfile
```

### 3.9 Log streaming

```text
Runner → Log Gateway (chunked append, sequence)
       → Live subscribers (UI SSE/WS)
       → flush to object store on step end
```

**Backpressure:** drop live UI if slow; durable path prefers finalize upload. Sequence numbers for gaps.

### 3.10 Retries & reruns

| Type | Behavior |
|------|----------|
| Step `retry` | Same job attempt; limited |
| Runner loss | Requeue new attempt if policy allows |
| Re-run failed jobs | New attempts; skip succeeded unless re-run all |
| Re-run all | New workflow attempt linking prior run |

**Idempotency:** platform cannot make user deploys exactly-once—OIDC + user locks; document.

### 3.11 OIDC to cloud

```text
Job requests token → OIDC Issuer signs JWT:
  sub: repo:org/name:ref:...,
  aud: sts.amazonaws.com (or configured),
  job_workflow_ref, event_name, ...
Cloud role trust policy matches claims → short-lived cloud creds
```

No long-lived cloud keys in secrets for modern path.

### 3.12 Trade-off: execution model

| Model | Pros | Cons |
|-------|------|------|
| Push assign jobs to runners | Low poll waste | Complex connectivity to self-hosted |
| **Pull claim (chosen)** | NAT-friendly self-hosted | Poll load; mitigate with long poll / pubsub notify |
| Hybrid notify+claim | Efficient | Extra pubsub |

---

## 4. Architecture Diagram

### 4.1 System overview

```text
 Git Host events          +------------------+
 (push/PR/cron) --------> | Event Ingress    |
                          | (idempotent)     |
                          +--------+---------+
                                   v
                          +--------+---------+
                          | Workflow Engine  |
                          | YAML→DAG, state  |
                          +--+------+------+-+
                             |      |      |
                     enqueue |      |      | cancel/concurrency
                             v      v      v
                          +--------+---------+
                          | Fair Job Queues  |
                          +--------+---------+
                                   |
              +--------------------+--------------------+
              v                                         v
     +----------------+                        +----------------+
     | Hosted Pool    |                        | Self-hosted    |
     | Autoscaler +   |                        | Agent Gateway  |
     | VM/microVM     |                        | (pull claim)   |
     +--------+-------+                        +--------+-------+
              |                                         |
              +-------------------+---------------------+
                                  v
                         Job Execution (steps)
                          /      |       \
                         v       v        v
                   Log Svc   Artifact   Cache
                             Store      Store
                                  |
                                  v
                           OIDC Issuer → Cloud STS
                                  |
                          Secrets Manager
```

### 4.2 Job claim sequence

```text
Engine--job queued-->Queue
RunnerAgent--long_poll/claim-->Queue/LeaseSvc
LeaseSvc--atomic lease(job, runner, fence)-->OK
Runner<--job payload (scripts, token endpoints)--+
Runner--heartbeat-->LeaseSvc
Runner--logs chunks-->LogSvc
Runner--finish-->Engine (terminal status + fence)
Engine--unblock dependents-->
```

### 4.3 Cancel-in-progress

```text
New run same concurrency group → Engine marks old run cancelling
Engine → notify leased runner (interrupt) + set cancel flag
Runner cooperative stop → upload partial logs → job cancelled
Timeout → fence expire → force fail cancelled
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Event → run idempotency** (`delivery_id` / dedupe key).  
2. **Single lease owner** per job attempt with fencing token.  
3. **Terminal CAS** on job/run status.  
4. **Secrets never in artifact index / unmasked logs by platform.**  
5. **DAG progress monotonic** — no resurrect succeeded deps silently.  
6. **Cancel is best-effort interrupt + lease expiry hard stop.**  
7. **OIDC keys in KMS; issuers rotatable.**  
8. **Fork PRs default-deny secrets.**

**Failure table:**

| Failure | Behavior |
|---------|----------|
| Runner death | Lease TTL → requeue or fail per attempt policy |
| Control plane blip | Runners finish current; new claims pause |
| Object store outage | Artifact/cache fail steps; logs buffer then fail |
| Queue partition | Under-assign better than double-run without fence |
| Secret store down | Fail jobs needing secrets fail-closed |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Engine + Postgres + Redis queue + hosted VMs + S3 + log stream |
| 10× | Queue partitions; autoscale runners; log pipeline; read replicas |
| 100× | Cells by repo hash; shuffle-sharded fair queues; regional pools; whale isolation |
| 1,000× | Global event fabric; spot capacity; log/artifact tiering; dedicated monorepo cells |

**Bursty CI patterns:**

- Dependency bumps → thousands of repos  
- Monorepo path filters help but thundering herd remains  
- **Admission control:** max concurrent jobs per org; queue beyond; prioritize interactive PR over scheduled

### 5.3 Maintainability

- Deterministic workflow planner tests (YAML fixtures → DAG).  
- Runner image pipelines + SBOM.  
- Chaos: kill runner, cancel races, duplicate webhooks.  
- Metrics: queue_wait, lease_steal, job_duration, cache_hit, log_lag, oidc_fail, fair_share_deficit.  
- Trace `run_id` / `job_id` / `attempt`.

### 5.4 Security deep dive

- Hosted: egress controls; metadata deny; untrusted Actions pin by SHA.  
- `pull_request_target` footguns: education + defaults.  
- Self-hosted: ephemeral recommended; label hygiene; group access.  
- Log masking imperfect—defense in depth.  
- Artifact ACL: same repo/run authz always.

### 5.5 Fairness algorithm sketch

```text
credit[org] += weight[org] * dt
on dequeue: pick org with highest credit among those with pending & under concurrency cap
credit[org] -= cost(job_sku)
```

Shuffle sharding: each org maps to N queue shards; runner claims scan random shard subset—reduces hot-shard contention.

---

## 6. Wrap-Up

### 6.1 What we designed

A **GitHub Actions–like CI** platform: event-driven YAML→DAG planning, matrix jobs, fair queues, hosted ephemeral runners + self-hosted pull agents, secrets/OIDC, artifacts/cache, log streaming, retries/reruns, and concurrency cancels—scaled via cells, shuffle sharding, and admission control under burst.

### 6.2 Key decisions worth defending

1. **Control plane owns DAG; runners own execution leases.**  
2. **Matrix caps** — unbounded expansion is a deal-breaker.  
3. **Pull-claim + fencing** for self-hosted NAT reality.  
4. **Weighted fair / shuffle queues** beat global FIFO.  
5. **Fork PR secret deny by default.**  
6. **OIDC over long-lived cloud keys.**  
7. **Split heartbeats vs starts vs webhooks** in math.  
8. **Logs: live best-effort + finalize durable.**  
9. **Cancel = cooperative + lease hard stop.**  
10. **Whale monorepos get isolation at 100×+.**

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Log/artifact cost explosion | Retention, compression, quotas |
| Marketplace Action compromise | Pin SHA, allowlists, provenance later |
| Self-hosted lateral movement | Ephemeral runners, network policies |
| Queue backlog UX | Estimate wait; SKU-specific pools |
| Double run on lease bugs | Fencing tests as release gate |

### 6.4 How to present in 45 minutes

1. Requirements + fork secret policy (6 min)  
2. Numbers with split classes + matrix amp (5 min)  
3. YAML→DAG + job FSM (8 min)  
4. Fair queues + runner leases (8 min)  
5. Secrets/OIDC/artifacts/artifacts (7 min)  
6. Scale/bursts (5 min)  
7. Q&A (remaining)

---

## 7. Deeper / Related Interview Questions

### 7.1 Workflow planning

**Q: How do you detect cycles in `needs`?**  
A: Topological sort / Kahn; fail run on cycle.

**Q: When is expression evaluation done?**  
A: Plan time for static; some `if` at runtime with context—document purity limits.

**Q: Matrix exclude/include?**  
A: Expand Cartesian then filter; enforce max jobs.

**Q: Reusable workflows?**  
A: Sub-DAG import at plan; pin versions/SHA.

### 7.2 Scheduling & fairness

**Q: Why not Kafka as the job queue?**  
A: Possible; need claim/lease semantics, delay, priority—Redis/PG queues often fit better. Kafka great for events/logs.

**Q: How prevent monorepo starvation?**  
A: Per-org concurrency caps + weighted fair dequeue + dedicated cells for whales.

**Q: Priority of `workflow_dispatch` vs `schedule`?**  
A: Product weights; interactive > cron typically.

**Q: Hot label `gpu` contention?**  
A: Separate pools; don’t block `ubuntu-latest` queues.

### 7.3 Runners & isolation

**Q: VM vs container for hosted?**  
A: VMs/microVMs stronger for untrusted PRs; containers denser—state threat model.

**Q: How does self-hosted claim work behind NAT?**  
A: Outbound long-poll / WebSocket to Agent Gateway; pull job payloads.

**Q: Runner compromise?**  
A: Hosted ephemeral mitigates; self-hosted is customer risk; short-lived job tokens.

**Q: DinD in CI?**  
A: Privileged nested = risk; sysbox/kata or remote builders preferred.

### 7.4 Secrets, OIDC, supply chain

**Q: How are secrets masked in logs?**  
A: Exact value redaction + entropy heuristics; imperfect; never echo secrets.

**Q: OIDC vs stored cloud keys?**  
A: OIDC short-lived, claim-scoped; preferred.

**Q: Action provenance?**  
A: Pin commit SHA; future SLSA attestations; org allowlists.

**Q: Environment protection rules?**  
A: Required reviewers / wait timers before deploy jobs lease.

### 7.5 Artifacts, cache, logs

**Q: Artifact vs cache?**  
A: Artifacts explicit outputs with retention; caches opportunistic deps with eviction.

**Q: Cache correctness?**  
A: Keys include lockfile hashes; restore-keys fallback; corruption → miss.

**Q: Live log loss on crash?**  
A: Accept small RPO on stream; finalize uploads per step; UI shows gaps.

**Q: Multi-GB artifacts?**  
A: Size quotas; multipart upload; don’t hold in control-plane DB.

### 7.6 Retries, cancel, idempotency

**Q: At-least-once job execution?**  
A: Yes under reclaim; fencing + user idempotency for deploys.

**Q: Cancel during artifact upload?**  
A: Best-effort abort; mark cancelled; GC partial objects.

**Q: Rerun succeeded deploy job?**  
A: Dangerous; require explicit re-run all / environment gates.

### 7.7 Multi-region & DR

**Q: Where does the run live?**  
A: Home cell by `repo_id`; runners may be regional; logs/artifacts regional with metadata global.

**Q: Region outage?**  
A: Drain; restore control plane; in-flight jobs fail; rerun.

### 7.8 Algorithms & structures

**Q: DAG structure?**  
A: Adjacency list + indegree counts; matrix nodes pre-expanded.

**Q: Lease data structure?**  
A: `{job_attempt_id → runner_id, fence, expiry}`; Redis + DB mirror.

**Q: Fairness structure?**  
A: Deficit/credit counters; shuffle shard map org→shards.

**Q: Idempotency for webhooks?**  
A: `(provider_delivery_id)` unique; or hash of (repo, event, dedupe_key).

### 7.9 Failure injection

1. Duplicate webhook → one run.  
2. Runner kill mid-job → lease expiry path.  
3. Double claim attempt → fencing rejects loser.  
4. Secret store down → fail-closed.  
5. S3 outage → artifact steps fail; engine still consistent.  
6. Cancel race completion → single terminal.  
7. Matrix bomb YAML → rejected at plan.  
8. Log subscriber slow → disconnect UI; durable continues.  
9. OIDC key rotation → dual-key overlap window.  
10. Queue backlog spike → admission + UX wait estimates.

### 7.10 Comparison traps

**Q: How is this different from Jenkins?**  
A: Multi-tenant SaaS fairness, ephemeral hosted isolation, git-native events, OIDC, matrix-as-data—not a single-controller groovy monolith.

**Q: How different from a job scheduler?**  
A: Scheduler primitives (leases/retries) underneath; CI adds YAML DAG, matrices, secrets, artifacts, git identity, fork trust.

**Q: Same as Cloud DevBox?**  
A: Share isolation tech optionally; CI jobs are ephemeral non-interactive with different fairness and secret policies.

### 7.11 Extra interviewer traps (high value)

- What is durable before you ACK the git webhook?  
- Who is SoT for job status—runner or control plane?  
- How do you stop a matrix from creating 100K jobs?  
- Why are heartbeats not Postgres writes?  
- How do fork PRs get secrets? (They don’t by default.)  
- How does fencing prevent double deploy?  
- What breaks if cache keys ignore lockfiles?  
- How do you fair-share GPUs vs CPU pools?  
- What’s the RPO for live logs?  
- How does `cancel-in-progress` interact with deploy locks?  
- Why pull-claim for self-hosted?  
- How do you design whale monorepo isolation?  
- What claims go into OIDC tokens?  
- How do you test lease expiry races?  
- What do you degrade first under overload—scheduled workflows or PR checks?

---

## Appendix A — Example schemas

```sql
CREATE TABLE workflow_runs (
  id              UUID PRIMARY KEY,
  repo_id         UUID NOT NULL,
  workflow_path   TEXT NOT NULL,
  event_name      TEXT NOT NULL,
  event_delivery_id TEXT NOT NULL,
  head_sha        TEXT NOT NULL,
  status          TEXT NOT NULL,
  concurrency_key TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (repo_id, event_delivery_id)
);

CREATE TABLE jobs (
  id              UUID PRIMARY KEY,
  run_id          UUID NOT NULL REFERENCES workflow_runs(id),
  name            TEXT NOT NULL,
  matrix_json     JSONB NOT NULL DEFAULT '{}',
  labels          TEXT[] NOT NULL,
  needs           TEXT[] NOT NULL DEFAULT '{}',
  status          TEXT NOT NULL,
  runner_id       TEXT,
  lease_fence     BIGINT NOT NULL DEFAULT 0,
  attempt         INT NOT NULL DEFAULT 1,
  queued_at       TIMESTAMPTZ,
  started_at      TIMESTAMPTZ,
  completed_at    TIMESTAMPTZ
);
CREATE INDEX jobs_dequeue ON jobs (status, queued_at) WHERE status = 'queued';

CREATE TABLE artifacts (
  id          UUID PRIMARY KEY,
  run_id      UUID NOT NULL,
  job_id      UUID NOT NULL,
  name        TEXT NOT NULL,
  digest      TEXT NOT NULL,
  size_bytes  BIGINT NOT NULL,
  object_uri  TEXT NOT NULL,
  expires_at  TIMESTAMPTZ NOT NULL
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Event idempotency, DAG planner, leases, hosted isolation, secrets mask, artifacts, logs, OIDC |
| 10× | Autoscale pools, queue partitions, log pipeline, cache service |
| 100× | Cells, shuffle-fair queues, whale isolation, regional runners |
| 1,000× | Global admission, spot capacity, tiered logs/artifacts, dedicated monorepo cells |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| Workflow run | One invocation of a workflow file |
| Job | Node in DAG (matrix instance) |
| Attempt | Execution try of a job |
| Lease / fence | Exclusive runner ownership token |
| Hosted runner | Platform ephemeral executor |
| Self-hosted | Customer agent pull model |
| Concurrency group | Cancel/serialize runs by key |
| OIDC | Federated short-lived cloud auth |
| Shuffle sharding | Random multi-shard placement for fairness |

## Appendix D — Estimation cheat-sheet

```text
jobs/day ≈ runs/day × jobs_per_run (matrix amplifies!)
concurrent ≈ starts/s × avg_duration_s

heartbeat_QPS ≈ concurrent_jobs × hb_rate  (aggregate at scale!)
logs/day ≈ jobs/day × avg_MB × retention_factor

backlog ≈ ∫(λ-μ)+ dt during spikes
```

## Appendix E — YAML → DAG example

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps: [...]
  test:
    needs: [build]
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        node: [18, 20]
        exclude:
          - os: windows-latest
            node: 18
    runs-on: ${{ matrix.os }}
  deploy:
    needs: [test]
    if: github.ref == 'refs/heads/main'
    environment: production
```

**Expanded jobs:** `build`, `test (ubuntu,18)`, `test (ubuntu,20)`, `test (windows,20)` — **3** test jobs after exclude (not 4).  
**DAG:** build → {tests} → deploy (deploy blocked until all needed tests finish; `if` may skip).

**Cap check:** if matrix produced > max_jobs_per_run → fail planning with actionable error.

## Appendix F — Lease / fencing sequence (failure)

```text
Attempt A leased to runner R1 with fence=7
R1 GC-paused; lease TTL expires
Engine requeues; runner R2 claims with fence=8
R1 wakes, tries finalize with fence=7 → REJECTED
R2 finishes with fence=8 → ACCEPTED
```

**Deal-breaker:** accepting terminal status without fence match (double deploy risk).

## Appendix G — OIDC claim set (illustrative)

```json
{
  "iss": "https://token.actions.example.com",
  "sub": "repo:acme/payments:ref:refs/heads/main",
  "aud": "sts.amazonaws.com",
  "repository": "acme/payments",
  "repository_owner": "acme",
  "job_workflow_ref": "acme/payments/.github/workflows/ci.yml@refs/heads/main",
  "event_name": "push",
  "run_id": "18422",
  "ref": "refs/heads/main",
  "sha": "a1b2c3..."
}
```

Cloud role trust: match `sub`/` aud` / optional `job_workflow_ref` exactness for prod.

## Appendix H — Fork PR trust matrix

| Event | Secrets | OIDC elevated | Writes to repo |
|-------|---------|---------------|----------------|
| `pull_request` from fork | No (default) | Restricted | No |
| `pull_request_target` | **Dangerous** if misused | Treat as privileged | Possible — require review |
| Workflow in fork branch | Runs in fork context | Fork’s secrets only | Isolated |
| Approval gate (org) | After review | May enable secrets | Policy |

## Appendix I — Burst playbook (dependency bump Monday)

1. Detect webhook surge / queue depth.  
2. Raise hosted pool desired capacity (SKU-aware).  
3. Tighten org concurrency for scheduled events first.  
4. Preserve PR checks latency SLO with priority weights.  
5. Communicate degraded wait times in UI.  
6. Spot/preemptible for non-critical workloads.  
7. Whale monorepo: pin to dedicated cell to protect multi-tenant queues.

## Appendix J — Invariant tests

| Test | Expect |
|------|--------|
| Duplicate webhook delivery | One workflow run |
| Matrix over cap | Plan failure |
| Fence mismatch finalize | Reject |
| Cancel vs completed race | Single terminal |
| Fork PR secret access | Denied by default |
| Artifact authz cross-repo | Denied |
| Cache put after job cancel | Reject / GC |
| OIDC aud mismatch | Mint fail closed |
| Runner death | Lease expiry path; no stuck `in_progress` forever |
| Concurrency cancel | Prior run jobs cancelled/skipped |

---

*End of design doc. Open with §1 DAG + fork secrets; whiteboard §3.3–3.6 planner/queues/runners; close with invariants in §5.1 and traps in §7.*
