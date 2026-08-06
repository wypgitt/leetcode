# System Design: Text-to-Video Generation Platform

> **Focus areas:** Async jobs · GPU orchestration · Progress · Retries · Artifacts/CDN · Safety · Quotas  
> **Style:** End-to-end generative media platform with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split API/queue/GPU load classes, no double-bill retries, honest latency vs cost trade-offs

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

Goal: **bound the product**—async text-to-video generation at what fidelity, with which safety and billing invariants, and how the GPU fleet scales.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are users? | Creators, marketers, app developers via API | Multi-tenant; API keys + user sessions |
| F2 | Input? | Text prompt; optional image/first-frame; duration/resolution knobs | Job spec versioned; validate limits |
| F3 | Output? | MP4 (or similar) + thumbnail; optional latent/preview | Object store + CDN; progressive preview |
| F4 | Sync or async? | **Async** — generation takes seconds–minutes | Job API + status + webhooks/SSE |
| F5 | Progress? | % or stage events (queued, sampling, encoding) | Event log per job |
| F6 | Models? | Multiple variants (fast/cheap vs high quality) | Model registry; different GPU SKUs/queues |
| F7 | Safety? | Input moderation + output moderation | Block before GPU; post-check before publish |
| F8 | Retries? | System retries transient GPU failures | Idempotent execution; **no double bill** |
| F9 | Quotas? | Per-tenant concurrency + monthly minutes/credits | Admission + ledger |
| F10 | Editing? | Extend/regenerate later Phase 2 | Job lineage hooks |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/videos` creates job with prompt + params; returns `job_id`.  
2. Queue → GPU worker → encode → store artifact → mark succeeded.  
3. Poll/SSE/webhook for status + progress.  
4. Input safety gate; output safety before CDN publish.  
5. Quotas/credits; idempotency keys; bounded retries without double charge.  
6. Download URL (signed) for completed video.  
7. Cancel cooperatively when possible.

**Out of MVP:**

- Real-time interactive scrubbing generation  
- Full multi-shot film editor  
- Training custom video LoRAs in-product  
- Guaranteed sub-second generation  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-preview | Feels progressive | Optional low-res preview within 10–30s when supported |
| N2 | Time-to-final | Model-dependent | Fast model p50 < 60s; HQ p50 few minutes (document per variant) |
| N3 | Durability | No lost paid jobs | Job record + artifact durable; RPO≈0 for completed |
| N4 | Billing correctness | Charge once per successful policy | Ledger keyed by job_id; retry ≠ new charge |
| N5 | Availability | Submit always if capacity policy allows | 99.9% control plane; generation depends on GPU pool |
| N6 | Safety | No publish of blocked content | Fail closed on moderator errors for high-risk |
| N7 | Multi-region | Artifacts global read; generate regional | Home region for job writes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Submit → queued → running (progress events) → safety pass → CDN URL.  
2. User cancels while queued → immediate cancel; while running → cooperative abort; refund policy.  
3. Webhook delivered with signature on terminal state.  
4. Tenant hits concurrency limit → 429 with queue guidance or reject.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate POST (retry) | Idempotency-Key → same job_id |
| GPU OOM mid-run | Retry on larger SKU or fail with credit release |
| Worker dies after upload before DB update | Reconcile by artifact presence; idempotent complete |
| Safety fail on output | Status=`rejected_safety`; no public URL; may still bill policy-dependent |
| Prompt blocked on input | Never enqueue GPU; no charge or tiny classify fee |
| Long queue | ETA exposed; optional priority SKU |
| Hot model deploy bad | Canary %; rollback model version pin |
| Viral spike | Admission control; degrade to waitlist; protect training clusters if shared |
| Encoding fails after samples | Retry encode without regenerating if latents/frames kept |
| Double webhook | Receiver idempotent; we at-least-once |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 100K | 1M | 10M | 100M |
| Jobs / day | 200K | 2M | 20M | 200M |
| Peak submit QPS | ~10 | ~100 | ~1K | ~10K |
| Avg GPU-minutes / job | 2 | 2 | 2 | 1.5 (mix faster models) |
| GPU-hours / day | ~6.7K | ~67K | ~670K | ~5M |
| Concurrent GPUs (util 70%) | ~400 | ~4K | ~40K | ~300K+ |
| Avg video size | 20 MB | 20 MB | 20 MB | 20 MB |
| Artifact storage added / day | ~4 TB | ~40 TB | ~400 TB | ~4 PB |
| Progress events / day | ~2M | ~20M | ~200M | ~2B |
| Webhooks / day | ~200K | ~2M | ~20M | ~200M |

**GPU-hours arithmetic:**

```text
200K jobs/day × 2 GPU-minutes = 400K GPU-minutes/day
400K / 60 ≈ 6,667 GPU-hours/day
Continuous GPUs needed ≈ 6667/24 ≈ 278 fully busy
At 70% utilization ≈ 400 GPUs  ✓ matches table
```

**What each jump forces:**

- **10×:** Multi-queue by model; autoscale GPU pools; CDN; webhook workers.  
- **100×:** Regional generate cells; spot+on-demand mix; artifact lifecycle; stronger admission.  
- **1,000×:** Global edge upload/download; model-specialized clusters; sophisticated quota markets; multi-CDN.

### 1.5 Etc. (Constraints & Assumptions)

- Generation is **not** interactive token-streaming like chat (frames/stages instead).  
- Models are versioned; prompts snapshotted for reproducibility disputes.  
- Safety models are separate services with SLOs.  
- Billing currency: credits ≈ GPU-seconds × model multiplier (+ markup).

**Scope statement:**

> Design a text-to-video platform: async job API, safety-gated queues into GPU workers with progress events, retries without double billing, durable artifacts on object storage/CDN, and tenant quotas—scaling from ~400 to ~300K+ GPUs as jobs/day grow 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| HTTP **submit/status** | ~10–50/s | ~10K–50K/s | Control plane |
| **Queue depth** changes | — | — | Backlog metric |
| **GPU job starts** | ~few/s | ~few K/s | Bound by fleet |
| **Progress events** | ~50–200/s | ~50K–200K/s | Fan-out to SSE/webhooks |
| **Artifact PUT** bandwidth | ~order Gbps | multi-Tbps fleet | Object store |
| **CDN egress** | user-driven | enormous | Cache hit critical |
| **Safety classify** QPS | ~10–50/s in + out | ×1000 | Parallel path |

### 2.2 Latency budget (fast model example)

```text
Input safety:        100–300 ms
Queue wait:          variable (capacity)
Model sample:        20–90 s
Output safety:       0.5–3 s (sample frames)
Mux/encode:          2–15 s
Upload + finalize:   1–5 s
→ Expose stages; don’t pretend sync REST returns video bytes
```

### 2.3 Storage & CDN

```text
200K × 20 MB = 4 × 10^12 B = 4 TB/day new
Retain 30 days → ~120 TB (baseline)
1,000× → ~4 PB/day → lifecycle mandatory (hot 7d, warm 30d, delete/archive)
```

### 2.4 Bandwidth to object store

```text
If completions sustained ~2.3 jobs/s (200K/86400):
  2.3 × 20 MB ≈ 46 MB/s ≈ 0.37 Gbps average
Peak 10× → ~4 Gbps; still modest vs GPU cost
At 1,000× average ~370 Gbps → parallel multipart, regional buckets
```

### 2.5 Cost dominance

```text
GPU $ / hour dominates object storage $ for short retention
Optimize: batch throughput, right-size SKU, spot for flexible jobs, latency SLOs per tier
```

### 2.6 Queue vs GPU mismatch

```text
If submit 100/s but fleet completes 20/s → queue grows 80/s
ETA ≈ queue_ahead / completion_rate
Admission control when ETA > product max or credits insufficient
```

---

## 3. High-Level Design

### 3.1 Product / API surfaces

```text
Developer:
  POST /v1/videos  → {id, status:queued}
  GET  /v1/videos/{id} → status, progress, output urls
  DELETE /v1/videos/{id} → cancel
  Webhook: video.completed / failed / safety_rejected

End-user app:
  Prompt box → spinner with stages → player
```

### 3.2 Job model

```text
VideoJob:
  job_id (ULID)
  tenant_id, user_id
  model_version
  prompt, params (duration, res, seed, fps)
  status, progress_pct, stage
  safety_input, safety_output
  credit_hold_id
  artifact_keys[]
  attempt, max_attempts
  idempotency_key
  created_at, started_at, completed_at
```

**Status enum:** `queued | running | finalizing | succeeded | failed | cancelled | rejected_safety`

### 3.3 End-to-end pipeline

```text
API Admit (auth, validate, input safety, quota, credit hold)
  → Job DB + Outbox
  → Queue (per model / priority)
  → GPU Worker (lease job)
       sample frames / latents
       progress heartbeats
  → Encode Worker (CPU/GPU encode)
  → Output safety
  → Publish artifacts (private bucket → signed URL / CDN path)
  → Settle credits + webhook
```

### 3.4 Idempotency & billing (deal-breaker section)

**Problem:** Clients retry POSTs; workers retry runs; webhooks retry—users must not pay 3×.

**Rules:**

| Event | Billing effect |
|-------|----------------|
| Idempotent recreate same key | No new hold |
| System retry attempt 2 of same job | Same hold; no second charge |
| User new job (new key) | New hold |
| Failure before billable success policy | Release hold (or charge classify fee only) |
| Success | Settle once (`UNIQUE job_id` settle) |

```text
Reserve(credits) at admit
Execute with attempts ≤ N
Settle OR Release exactly once (CAS on billing_state)
```

**Deal-breakers:**

- Charging per GPU attempt blindly  
- New `job_id` on internal retry  
- Settling in the worker without idempotency  

### 3.5 Queues & GPU orchestration

**Queues:** `model_fast_p0`, `model_fast_p1`, `model_hq`, `encode`

**Worker loop:**

```text
lease = queue.Claim(visibility_timeout)
heartbeat progress → job service
produce frames to scratch (local SSD / ephemeral)
on success: upload → Complete(job)
on fail: classify retryable → Retry or Fail
on timeout visibility: another worker may claim — MUST be safe
```

**Exactly-once effect:** completion is idempotent upsert; artifact keys deterministic `s3://.../{job_id}/v1.mp4`.

**GPU scheduler integration:** either embed simple pool autoscaler or call external GPU scheduler (credits doc). Here: **pools per model** with desired replica counts from queue lag.

### 3.6 Progress events

```text
stages: validating → queued → allocating → sampling(0–90%) → encoding → safety → uploading → done
```

**Transport:**

- SSE/WebSocket for interactive clients  
- Polling GET for simple SDKs  
- Webhooks for servers  

**Storage:** append-only `job_events(job_id, seq, type, payload)` for replay.

### 3.7 Safety

**Input path (before GPU):**

- Prompt text classifiers (sexual, violence, PII, disallowed public figures policy, etc.)  
- Block → `rejected_safety` without GPU spend  

**Output path (before publish):**

- Sample frames / audio → vision-audio moderators  
- Fail closed on moderator timeout for risky tiers; or quarantine for human review (enterprise)

**Ownership:** Safety service decides; workers cannot mark `succeeded` without safety token.

### 3.8 Artifact storage & CDN

```text
Write: private bucket, versioned, encryption at rest
Publish: copy/flag to CDN origin OR signed URLs with TTL
Thumbnails: generated during finalize
Lifecycle: tenant retention settings
```

**Hot linking / abuse:** signed URLs; rate limits; virus scan optional.

### 3.9 Model variants

| Variant | GPU | Latency | Credit weight |
|---------|-----|---------|---------------|
| turbo | L40S | ~30–60s | 1× |
| default | A100 | ~1–3 min | 3× |
| hq | H100 | ~3–10 min | 8× |

Pin `model_version` at job creation for reproducibility.

### 3.10 Cancellation

```text
queued: remove from queue; release credits
running: set cancel_flag; worker checks between steps; abort; release/settle partial per policy
finalizing: best-effort abort upload; may still complete
```

### 3.11 Multi-tenant quotas

- Max concurrent running jobs / tenant  
- Max submits / minute  
- Monthly credit budget  
- Fair share across tenants on shared pools (weighted)

---

## 4. Architecture Diagram

### 4.1 System context

```text
+----------+     +-------------+     +------------------+
| Clients  |---->| API / BFF   |---->| Job Service      |
+----------+     +------+------+     +--------+---------+
                        |                     |
                        v                     v
               +--------+------+      +-------+--------+
               | Safety        |      | Credit Ledger  |
               +---------------+      +----------------+
                                      |
                                      v
                               +------+-------+
                               | Queues       |
                               +------+-------+
                                      |
                    +-----------------+------------------+
                    v                                    v
             +------+------+                      +------+------+
             | GPU Workers | ---> scratch frames  | Encode Pool |
             +------+------+                      +------+------+
                    |                                    |
                    +-----------------+------------------+
                                      v
                               +------+------+
                               | Object Store|
                               +------+------+
                                      v
                                   CDN / Signed URL
```

### 4.2 Sequence: happy path

```text
Client → API: POST /v1/videos (Idempotency-Key)
API → Safety: check prompt → allow
API → Ledger: Reserve
API → DB: insert job queued
API → Queue: enqueue
API → Client: 200 {job_id}

Worker → Queue: claim
Worker → Job: status=running
Worker: sample... emit progress
Worker → Encode → Safety output → allow
Worker → S3: put video
Worker → Job: succeeded + artifact (CAS)
Worker → Ledger: Settle (idempotent)
Job Service → Webhook dispatcher
```

### 4.3 Sequence: retry without double bill

```text
Worker fails retryable (GPU ECC)
Job.attempt++ ; billing_state still HELD
Requeue same job_id
New worker runs; succeeds
Settle once → billing_state=SETTLED
Second settle no-op
```

### 4.4 Sequence: worker crash after S3 put

```text
S3 object exists; DB still running
Reconciler: if object+safety token present → Complete(job)
Or new worker sees deterministic key exists → finalize without regenerate
```

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Idempotent create by (tenant, key) | Unique constraint |
| R2 | At most one successful bill settle / job | CAS billing_state |
| R3 | No public artifact without output safety pass | Safety token required |
| R4 | Job terminal states immutable | DB transitions |
| R5 | Lease/claim fencing for workers | claim_token / attempt |
| R6 | Prompt + model_version immutable after create | Snapshot columns |
| R7 | Cancel/release cannot double-spend credits | Ledger idempotency |

**Degradations:**

| Failure | Behavior |
|---------|----------|
| GPU pool exhausted | Queue + ETA; 503/429 on admit if over max ETA policy |
| Safety down | Fail closed (or limited mode) |
| Object store down | Pause completes; keep sampling only if scratch safe—usually pause claims |
| Webhook target down | Retry with backoff; dead-letter |
| Region AZ loss | Fail jobs mid-run → retry other AZ; durable job records in multi-AZ DB |

### 5.2 Scalability

**1×:** One region; SQS/Kafka; GPU VM pool; Postgres jobs; S3+CloudFront.

**10×:** Autoscale on queue lag; separate encode; redis for SSE fanout; shard webhook delivery.

**100×:** Generate cells per region; tenant fair queues; artifact lifecycle; model canaries; spot for turbo tier.

**1,000×:** Global control plane with regional execution; multi-CDN; specialized HQ islands; capacity broker shared with other GPU products.

**Autoscaling signal:**

```text
desired_gpus ≈ f(queue_lag, target_p50_wait, model)
scale up fast; scale down slow (drain)
```

### 5.3 Maintainability

- Model registry with rollout % and kill switches.  
- Golden prompt suites for regressions (quality + safety).  
- Job replay tools for support (access-controlled).  
- Clear error taxonomy: `CONTENT_POLICY`, `RATE_LIMIT`, `CAPACITY`, `INTERNAL_RETRYABLE`.  
- Tracing: `job_id` across API→queue→worker→S3.

### 5.4 Ownership resolution

| Concern | Owner |
|---------|-------|
| API auth / idempotency | API gateway + job service |
| Credit hold/settle | Ledger |
| Whether content may run/publish | Safety |
| Who runs which job when | Queue + worker pools (+ optional GPU scheduler) |
| Bytes durability | Object store |
| User delivery | CDN / signed URL service |
| Progress truth | Job service event log |

**Contradiction trap:** worker writing `succeeded` while safety async—must be gated.

### 5.5 Failure modes library

| Mode | Mitigation |
|------|------------|
| Non-deterministic model output on retry | Accept; new attempt may differ; seed pinned if supported |
| Stuck RUNNING | Watchdog on heartbeat; reclaim |
| Huge prompt / injection | Length limits; safety; escape in templates |
| Thumbnails leaking rejected video | Generate thumbs only after safety pass |
| Cost runaway bug | Per-tenant burn rate alarms; global kill switch |

### 5.6 Security

- Prompt isolation between tenants on shared GPUs (process sandbox).  
- Signed URLs short-lived; authz on GET job.  
- Webhook HMAC secrets per endpoint.  
- PII in prompts: retention policies; optional zero-retention mode.

### 5.7 Long-running jobs

- Visibility timeout extended via heartbeat.  
- Progress must refresh `lease_until`.  
- Max runtime cap per model to kill zombies.  
- Checkpoint frames to scratch object store for resume (Phase 1.5)—MVP may full restart attempt.

---


### 5.8 Preview & progressive delivery

For UX, optional **turbo preview**: generate low-res short sample first (bill small), then continue HQ if user confirms—or speculative HQ if credits allow. Implementation: child jobs with `parent_job_id` sharing prompt snapshot.

**Player integration:** poll until `preview_url` available; swap to `final_url` on succeed without remounting if resolutions compatible.

### 5.9 Abuse, fraud, and viral load

| Threat | Control |
|--------|---------|
| Credit card fraud → mass generations | Velocity limits; risk scoring; hold artifacts |
| Prompt spam | Per-tenant QPS; content similarity throttle |
| Bandwidth scraping of CDN | Signed URLs; referer/token binding; short TTL |
| Model extraction via API | ToS; rate limits; watermarking research (product) |

**Viral spike runbook:** raise prices / tighten quotas for free tier; protect HQ pool; serve waitlist page rather than melting GPUs.

### 5.10 Reproducibility & support tooling

Support must answer: “why does this look different today?” Store immutable: prompt, params, model_version, seed, safety decisions, worker image digest, attempt history. Provide internal replay that **does not** auto-charge.

### 5.11 Encode pipeline details

```text
frames (png/yuv on scratch SSD)
  → ffmpeg / HW encoder (h264/h265/av1)
  → mp4 faststart
  → thumbnail contact sheet
  → upload multipart
```

Keep frames until output safety + upload ACK; then delete scratch (cost + privacy).

**Failure split:** if encode fails, retry encode without resampling when frames intact—saves GPU $.

### 5.12 Comparison with image generation platforms

Similar control plane (async job, safety, credits) but video adds: longer leases, encode stage, larger artifacts, frame-level moderation sampling strategy, and much heavier GPU-minutes per request. Don’t design as “image but bigger files” only—queue timeouts and progress semantics differ.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Async job API + state machine.  
2. Safety in → queue → GPU → encode → safety out → CDN.  
3. Credit reserve/settle + idempotent retries.  
4. Progress/webhooks.  
5. Scale math: jobs → GPU-hours → fleet size.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Job API, one model pool, safety in/out, S3, poll+webhook, credits |
| 10× | Multi-model queues, autoscaling, SSE progress |
| 100× | Regional cells, lifecycle, fair tenant queues |
| 1,000× | Global capacity broker, multi-CDN, specialized HQ fleets |

### 6.3 Top risks

1. Double billing on retries.  
2. Publishing before output safety.  
3. Queue meltdown without admission control.  
4. Indefinite RUNNING after worker death.  
5. Storage cost at 1,000× without lifecycle.

### 6.4 One-sentence design

> An async, safety-gated video generation control plane that reserves credits once per job, runs version-pinned models on autoscale GPU pools with progress and idempotent completion, and publishes only moderated artifacts via signed CDN URLs.

---

## 7. Deeper / Related Interview Questions

### 7.1 API & product

**Q: Why async not sync HTTP until video returns?**  
A: Generation takes tens of seconds to minutes; sync ties up connections and fails poorly; async jobs + progress is the right UX/SLA.

**Q: Poll vs webhook vs SSE?**  
A: Poll simple; SSE good for apps; webhooks for server integrations—support at least poll+webhook in MVP.

**Q: How do you version outputs?**  
A: `model_version` + params snapshot; artifact key includes job_id; regenerations are new jobs with `parent_job_id`.

**Q: Seed reproducibility?**  
A: Best-effort if model supports; document nondeterminism across versions/hardware.

### 7.2 Billing & retries

**Q: What’s the double-bill failure mode?**  
A: Charging on each attempt or each client retry creating new jobs without idempotency.

**Q: When do you charge?**  
A: Common: reserve at admit; settle on success; release on hard fail/cancel before success. Safety rejects may be free or small fee—state policy.

**Q: Client retries POST after 500?**  
A: Same Idempotency-Key returns original job; must persist first response.

**Q: Worker claims twice?**  
A: Fenced claim tokens; completion CAS; deterministic artifact keys.

### 7.3 GPU & queues

**Q: How do you autoscale GPUs?**  
A: Queue lag + target wait; scale up fast / down slow; separate pools per model.

**Q: Spot instances?**  
A: Good for turbo/batch; checkpoint or accept restart; not for strict SLA HQ without fallback.

**Q: Encode on GPU or CPU?**  
A: Often CPU/hardware encoder pool to free scarce training GPUs; depends on pipeline.

**Q: How to prioritize paying enterprise?**  
A: Priority queues + reserved capacity pools + weights.

**Q: Backpressure when object store slow?**  
A: Stop claiming new jobs; alert; keep heartbeats on current.

### 7.4 Safety

**Q: Where do you moderate?**  
A: Input before GPU; output before publish; both logged.

**Q: Fail open or closed?**  
A: Prefer fail closed for publish; business may allow fail open on input with risk—document.

**Q: Adversarial prompts?**  
A: Classifier ensembles; rate limits; abuse scoring; human review queues for edge.

**Q: Can workers skip safety?**  
A: No—completion API requires safety attestation token.

### 7.5 Storage & delivery

**Q: Public bucket vs signed URL?**  
A: Signed/private preferred; CDN with auth tokens or signed cookies.

**Q: Lifecycle at 1,000×?**  
A: Mandatory tiering/deletion; tenant-specific retention; cost alerts.

**Q: Hot vs cold artifacts?**  
A: Recent jobs hot CDN; older only on GET restores.

**Q: Multipart upload?**  
A: Yes for large HQ files; complete only after full parts + safety.

### 7.6 Progress & UX

**Q: Fake progress bars?**  
A: Prefer stage-based real signals; if estimated %, bound and never go backwards except on retry reset.

**Q: How often to emit events?**  
A: Stage changes + throttled percent (e.g. ≤1/s) to limit event QPS.

**Q: ETA accuracy?**  
A: Based on queue position and empirical model runtime percentiles.

### 7.7 Multi-region & DR

**Q: Where does the job record live?**  
A: Home region DB; execute on regional GPU cell; artifacts in regional bucket with optional replicate.

**Q: Failover mid-job?**  
A: Mark failed/retryable; restart in healthy cell; billing stays one job_id.

**Q: Cross-region download?**  
A: CDN anycast; origin nearest to artifact.

### 7.8 Reliability drills

**Q: DB says running, worker gone?**  
A: Heartbeat watchdog → requeue or fail per attempt policy.

**Q: Duplicate webhook storms?**  
A: At-least-once delivery; consumers dedupe on event_id; exponential backoff.

**Q: Poison prompt crashes model process?**  
A: Isolate; mark failed; don’t infinite retry; blackhole pattern after N.

**Q: Bad model rollout?**  
A: Version pin + canary; kill switch routes back.

### 7.9 Comparison traps

**Q: How is this different from text LLM inference platform?**  
A: Longer jobs, heavier artifacts, encode step, different progress, storage/CDN dominate more, safety on frames.

**Q: How is this different from batch video transcoding?**  
A: Generative nondeterminism, safety, credits tied to model variants, prompt UX—not just ffmpeg.

**Q: Why not only use a generic job scheduler?**  
A: Need domain invariants: safety gates, media artifacts, billing, progress semantics—scheduler is a component.

### 7.10 Extra interviewer traps (high value)

- Show jobs/day → GPU-hours → fleet size math.  
- What is billed on retry?  
- Where is idempotency key stored?  
- Can a video be public without output safety?  
- How do you finalize after crash post-upload?  
- Sync vs async—defend choice.  
- How do progress events scale to 1,000×?  
- Queue lag → autoscaling formula.  
- Cancel while sampling—credit policy?  
- Deterministic S3 keys—why?  
- How do multi-model queues prevent HQ starving turbo?  
- What retention at 4 PB/day ingest?  
- Fail closed vs open on moderator timeout?  
- How do you prevent tenant A from consuming entire GPU pool?  
- What is in the job snapshot for disputes?

---

## Appendix A — Example schemas

```sql
CREATE TABLE video_jobs (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  user_id UUID NOT NULL,
  idempotency_key TEXT NOT NULL,
  model_version TEXT NOT NULL,
  prompt TEXT NOT NULL,
  params JSONB NOT NULL,
  status TEXT NOT NULL,
  stage TEXT,
  progress_pct INT NOT NULL DEFAULT 0,
  attempt INT NOT NULL DEFAULT 0,
  max_attempts INT NOT NULL DEFAULT 3,
  credit_hold_id UUID,
  billing_state TEXT NOT NULL, -- none|held|settled|released
  safety_input JSONB,
  safety_output JSONB,
  artifact_key TEXT,
  error_code TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, idempotency_key)
);

CREATE TABLE job_events (
  job_id UUID NOT NULL,
  seq BIGINT NOT NULL,
  type TEXT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (job_id, seq)
);

CREATE TABLE webhook_deliveries (
  id UUID PRIMARY KEY,
  job_id UUID NOT NULL,
  event_id UUID NOT NULL,
  endpoint_id UUID NOT NULL,
  status TEXT NOT NULL,
  attempts INT NOT NULL,
  next_attempt_at TIMESTAMPTZ,
  UNIQUE (event_id, endpoint_id)
);
```

## Appendix B — API examples

```http
POST /v1/videos
Idempotency-Key: 8f2c...
Authorization: Bearer ...
{
  "model": "turbo",
  "prompt": "A fox running through neon Tokyo streets, cinematic",
  "seconds": 4,
  "size": "1280x720",
  "seed": 42
}

→ 200 {"id":"vid_01J...","status":"queued"}
```

```http
GET /v1/videos/vid_01J...
→ {
  "id":"vid_01J...",
  "status":"running",
  "stage":"sampling",
  "progress": 55,
  "model_version":"turbo-2026-07-12"
}
```

```json
{
  "event_id": "evt_...",
  "type": "video.completed",
  "job_id": "vid_01J...",
  "output": {"url": "https://cdn.../signed...", "expires_at": 1765}
}
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Job API, safety in/out, one GPU pool, S3, credits, webhooks |
| 10× | Multi-model queues, autoscale, SSE, encode pool |
| 100× | Regional cells, tenant fairness, artifact lifecycle |
| 1,000× | Global capacity broker, multi-CDN, specialized fleets |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Job | One generation request lifecycle |
| Model version | Immutable generation stack identity |
| Credit hold | Reserved spend until settle/release |
| Claim / lease | Worker ownership of a queue message/job |
| Safety token | Attestation required to publish |
| Artifact | Stored video/thumb bytes |
| Progressive preview | Early low-res sample for UX |
| Visibility timeout | Queue reclaim window without heartbeat |
| Finalize | Upload + DB complete + bill settle |
| Canary model | Partial traffic for new versions |

## Appendix E — Estimation cheat-sheet

```text
GPU-hours/day ≈ jobs/day × gpu_minutes_per_job / 60
GPUs_busy ≈ GPU-hours/day / 24
GPUs_provisioned ≈ GPUs_busy / utilization  (e.g. / 0.7)

200K × 2 min = 400K GPU-min = 6,667 GPU-h ≈ 278 busy ≈ 400 at 70% util

Storage/day ≈ jobs/day × avg_video_bytes
200K × 20 MB = 4 TB/day

Submit QPS ≠ GPU completions/s ≠ progress event QPS

Retries must not create new billable job_ids
```

---

*End of design doc. Open with §1 async+safety+billing scope; whiteboard §3.3–3.5 pipeline and no-double-bill; close with invariants §5.1 and traps §7.*
