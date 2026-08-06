# System Design: Model Evaluation & Monitoring Platform

> **Focus areas:** Dataset versioning · Golden sets · Offline/online eval · Safety metrics · Human review · Regression detection · Statistical rigor  
> **Style:** End-to-end AI infra design with progressive scale (10× → 100× → 1,000×)  
> **Theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — GPU batching, reliability, safety, cost, evaluation rigor  
> **Quality bar:** Correct arithmetic, split offline-batch vs online-scoring load classes, explicit contamination controls, canary vs full regression invariants

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

Goal: **bound the product**—an internal/platform evaluation and monitoring system that lets Anthropic (and enterprise customers, if scoped) measure model quality, safety, and regressions across versions, with human review in the loop. Not training. Not the production chat product itself.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are the users? | Model researchers, safety teams, release managers, optionally enterprise API customers viewing their evals | RBAC by org/team; audit every mutation |
| F2 | What is an “eval”? | Versioned dataset + rubric + model/config → scored run with metrics + artifacts | Immutable `EvalRun` as unit of record |
| F3 | Dataset types? | Golden sets, adversarial/jailbreak suites, capability benchmarks, customer canaries, production samples (anonymized) | Dataset registry with lineage + contamination flags |
| F4 | Offline vs online? | Both: batch offline before release; online continuous scoring on traffic samples | Separate pipelines; shared metric definitions |
| F5 | Metrics? | Quality (accuracy/helpfulness), safety (harmlessness, honesty, jailbreak resist), latency/cost, regression deltas | Metric catalog; typed scorers; confidence intervals |
| F6 | Human review? | Spot-check disagreements, safety edge cases, rubric calibration | Review queues with SLAs; double-blind when needed |
| F7 | Regression gates? | Canary suite must pass before promote; full suite nightly / pre-release | Gate service; block promote on fail + override audit |
| F8 | Model targets? | Claude versions, fine-tunes, prompt/system variants, tool configs | `SubjectUnderTest` = model + prompt + tools + params |
| F9 | Scoring methods? | Exact match, rubrics, LLM-as-judge, human labels, classifiers | Pluggable scorers; judge models versioned too |
| F10 | Contaminated data? | Must detect / quarantine train-set leakage into evals | Hash/fingerprint; membership checks; holdout vault |
| F11 | Comparisons? | A/B two models; multi-arm; slice by domain/language/risk | Diff views; stratified sampling; significance tests |
| F12 | Alerts? | Metric drift, safety spike, judge disagreement surge | Online monitors → Pager/Slack; runbook links |

**MVP functional scope (lock with interviewer):**

1. **Dataset registry**: create/version datasets; immutable snapshots; tags (golden, canary, safety, capability).
2. **Eval run orchestration**: submit run against subject (model version + config); batch inference with GPU-efficient packing.
3. **Scorers**: exact/regex, rubric LLM-judge, safety classifiers; aggregate metrics with CIs.
4. **Human review queue**: sample disagreements + all critical safety failures.
5. **Regression gates**: canary suite blocking promote; full suite async; dashboard diffs vs baseline.
6. **Online monitoring**: sample production traffic → score → dashboards/alerts (shadow, not user-facing).
7. **Audit log**: who changed datasets, rubrics, gates, overrides.

**Out of MVP (explicitly defer):**

- Full RLHF preference data platform (hooks only)
- Customer-facing public leaderboard product
- Perfect automatic contamination proofs
- Multi-cloud inference orchestration
- Auto-remediation that changes production weights

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Canary suite latency? | Blocks release; must be fast | p95 wall time < 30–60 min for canary; parallelizable |
| N2 | Full suite? | Nightly / pre-release | Hours OK; cost-aware scheduling |
| N3 | Online score lag? | Near-real-time drift | p95 sample→score < 5–15 min |
| N4 | Durability? | Runs must be reproducible | Immutable inputs + outputs; RPO≈0 for completed runs |
| N5 | Availability? | Offline can degrade; gates must not silently pass | Gate fail-closed on infra errors |
| N6 | Isolation? | Safety datasets highly sensitive | Separate vault; need-to-know ACL |
| N7 | Cost? | GPU + judge tokens dominate | Batch, cache prefixes, schedule off-peak |
| N8 | Statistical rigor? | No false confidence | Report n, CI, effect size; not just point scores |
| N9 | Privacy? | Prod samples may contain PII | Scrub/tokenizeize before offline store; retention |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Researcher uploads golden set v3 → tags `canary` → kicks eval on `claude-X` vs baseline → metrics + CI → gate green → promote.
2. Safety suite finds jailbreak success rate ↑ → gate red → human review triage → block release.
3. Online sampler sees honesty metric drift on tool-use slice → alert → offline deep dive.
4. Two models compared; stratified slices show regression only in code → targeted fix.
5. Human reviewers calibrate rubric; inter-rater κ tracked; judge prompts updated under version.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Dataset mutated mid-run | Impossible: runs pin `dataset_snapshot_id` |
| Judge model itself regresses | Pin judge version; meta-eval judges against human gold |
| Contaminated item discovered | Quarantine item; mark affected historical runs `suspect` |
| GPU fleet brownout mid-suite | Checkpoint partial results; resume; don’t mark pass |
| Thundering herd of evals pre-release | Fair queues by team + priority (release > research) |
| Human review backlog | Prioritize critical safety; age-out low severity with audit |
| Online sample includes secrets | Redact pipeline; drop from durable store if fails scrub |
| Tiny n for rare slice | Suppress “significant” claims; require min-n |
| Override gate to ship | Dual-control + written rationale + time-boxed |
| Duplicate prompts across suites | Dedup fingerprints; shared item library |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Datasets | 200 | 2K | 20K | 200K |
| Items (prompts) total | 2M | 20M | 200M | 2B |
| Eval runs / day | 500 | 5K | 50K | 500K |
| Items scored / day (offline) | 5M | 50M | 500M | 5B |
| Online samples / day | 1M | 10M | 100M | 1B |
| Concurrent GPU jobs | 50 | 500 | 5K | 50K |
| Human review labels / day | 2K | 20K | 200K | 2M (mostly auto) |
| Metric time series points / day | 50M | 500M | 5B | 50B |
| Teams / tenants | 20 | 200 | 2K | 20K |
| Gate checks / day | 100 | 1K | 10K | 100K |

**What each jump forces:**

- **10×:** Dedicated inference batch fleet; object store for artifacts; Postgres metadata + warehouse for metrics.
- **100×:** Shard run workers; dataset content-addressed store; human review routing; online stream processing.
- **1,000×:** Multi-region eval cells; hierarchical sampling; aggressive LLM-judge distillation; cold artifact tiers.

### 1.5 Etc. (Constraints & Assumptions)

- Platform **consumes** Inference Gateway / batch inference APIs; does not own training.
- **Safety datasets** may never leave the vault region; no logging of raw jailbreak success strings to unrestricted sinks.
- **LLM-as-judge** is a first-class scorer but never the sole gate for critical safety without human/classifier backup.
- Progressive scale stresses **items scored/day** and **GPU hours**, not only “number of dashboards.”

**Scope statement to repeat back:**

> Design a model evaluation and monitoring platform: versioned datasets and golden/canary suites, reproducible offline eval runs with batched GPU inference, pluggable scorers (exact, classifiers, LLM-judge), human review queues, online traffic sampling for drift, and fail-closed regression gates with statistical reporting—scaling through 10× / 100× / 1,000× while controlling contamination, cost, and safety data isolation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Control plane** | Create dataset/run, gate API | ~50–200/s | ~0.5–2K/s | Postgres |
| **Batch inference** | Prompt → completion | ~5M items/day ≈ ~60/s avg, ~500/s peak | ×10 | GPU batch |
| **Scoring** | Judge/classifier on outputs | ~1–3× inference items | ×10 | CPU/GPU mix |
| **Online sample ingest** | Kafka → sample store | ~10–50/s | ~100–500/s | Stream |
| **Human review** | Label API | ~few/s | ~tens/s | Postgres |
| **Metrics write** | Aggregates + raw scores | ~100–1K/s | ~1–10K/s | Warehouse + TSDB |
| **Artifact IO** | Prompts/outputs blobs | GBs–TBs/day | ×10 | Object store |

**Anti-pattern:** one “eval QPS” mixing dashboard clicks, GPU inference, and warehouse inserts.

### 2.2 Canary suite wall-clock

```text
Canary items: 5,000
Avg output tokens: 400
Avg input tokens: 800
Tokens total ≈ 5e3 × 1.2e3 = 6e6 tokens

Assume batch throughput: 50K output tokens/s on allocated pool
Generation-bound time ≈ 5e3 × 400 / 5e4 = 40s (ideal)
+ queue, judge, stragglers → budget 30–60 min wall with parallelism headroom

Judge (LLM): another ~5e3 × 300 out tokens → similar order
Plan: overlap generation batches with judge batches on separate pools
```

### 2.3 Full suite cost (order)

```text
Full suite: 500K items/day equivalent for nightly
Avg 1K tokens in+out billed ≈ 5e8 tokens
If $3 / 1M tokens blended → ~$1,500/night order (tune with interviewer)
At 100× → $150K/night unless sampling, caching, cheaper judges

Cost levers:
  - Prefix cache shared system rubrics
  - Distilled judge for bulk; LLM-judge for disputed
  - Stratified downsample non-canary
  - Spot/preemptible for research; reserved for gates
```

### 2.4 Online monitoring volume

```text
Prod turns/day: 200M (example)
Sample rate 0.5% → 1M samples/day
Score with cheap classifiers first; escalate 5% to LLM-judge → 50K judge/day
Keep GPU for online path tiny vs offline fleet
```

### 2.5 Storage

```text
Item text ~2 KB; output ~2 KB; scores ~0.5 KB
5M items/day scored → ~25 TB/year raw (before compression/retention)
Retain raw outputs 90d hot; aggregates forever; safety vault longer under policy
```

### 2.6 Statistical power (interview talking point)

```text
Detect 2% absolute drop in accuracy from 80% baseline
Rough n ≈ (z^2 * p(1-p)) / E^2 for proportion CI; for A/B use power analysis
Order-of: thousands of items per critical slice, not dozens
Canary must be large enough OR accept only large regressions detectable
```

---

## 3. High-Level Design

### 3.1 Product / UX surfaces

```text
+-----------------------------------------------------------------------+
| Eval Platform     [Datasets] [Runs] [Gates] [Online] [Review] [Admin] |
+-------------------+---------------------------------------------------+
| Suites            |  Run: claude-X vs baseline-Y                      |
|  canary-v12       |  Status: RUNNING  62%   ETA 18m                   |
|  safety-jailbreak |  Metrics: helpfulness 0.81 (±0.01)  Δ -0.02*      |
|  code-gold        |  Safety: jailbreak_success 0.4%  Δ +0.2% FAIL     |
|  * New dataset    |  [Diff slices] [Artifacts] [Override…] [Promote]  |
+-------------------+---------------------------------------------------+
| Review queue (12 critical) | Online drift: honesty↓ tool-use slice    |
+-----------------------------------------------------------------------+
```

### 3.2 Domain model

```text
Org / Team
  └── Dataset
        ├── DatasetVersion (immutable snapshot)
        │     └── Item[]  (prompt, refs, tags, fingerprints, contamination_state)
        ├── Rubric / MetricSpec (versioned)
        └── Suite (ordered set of dataset versions + gates)

SubjectUnderTest
  model_version + system_prompt_hash + tools + decoding_params + inference_route

EvalRun
  ├── suite_or_datasets pinned
  ├── subject + baseline_run_id?
  ├── status state machine
  ├── ItemResult[] (output, scores, judge_trace refs)
  ├── AggregateMetrics + CIs + slice metrics
  ├── gate_decision
  └── artifacts (manifest in object store)

OnlineMonitor
  └── sample → score → time series → alert rules

ReviewTask
  └── item_result refs + assignees + labels + adjudication
```

**Immutability invariant:** once `DatasetVersion` is `published`, content bytes and item IDs never change. Edits create `v+1`.

**EvalRun state machine:**

```text
created → queued → running → scoring → aggregating
                                      ├→ completed
                                      ├→ failed
                                      ├→ cancelled
                                      └→ completed_suspect (contamination/infra caveat)
GateDecision: pending | pass | fail | overridden
```

CAS terminal transitions; partial checkpoints for resume.

### 3.3 Dataset versioning & golden sets

| Concern | Approach |
|---------|----------|
| Versioning | Content-addressed item blobs; manifest Merkle root per version |
| Golden set | Curated, slow-changing, human-validated; tag `golden` |
| Canary | Subset of golden + high-signal adversarial; must finish fast |
| Full regression | Union of suites; nightly; non-blocking except pre-major |
| Lineage | `derived_from`, transform jobs, sampling seeds |
| Fingerprints | Normalized text hash + embedding near-dup for contamination |

**Deal-breaker:** mutable “live” datasets that change under a published run ID.

### 3.4 Offline eval orchestration

```text
Submit EvalRun
  → resolve pins (datasets, rubrics, subject, judge versions)
  → expand items → shards (by hash)
  → batch inference workers (pack by length; prefix cache)
  → write outputs to object store + result rows
  → scoring workers (deterministic first, then classifiers, then judge)
  → aggregate + CI + slice
  → gate evaluate
  → notify
```

**GPU efficiency:**

- Sort/pack similar lengths; continuous batching where gateway supports.
- Share long system/rubric prefixes via prompt cache.
- Separate pools: generation vs judge (different latency/cost).
- Cap max concurrent runs per team; priority queue for release canaries.

### 3.5 Online eval / monitoring

```text
Prod traffic → Privacy scrubber → Sampler (stratified)
  → Feature log (model version, route, tools, outcome)
  → Async score path (classifiers → optional judge)
  → Metrics TSDB + warehouse
  → Alert manager (drift, safety spikes)
```

**Invariant:** online path must not add user-visible latency. Fail open for monitoring; never block chat on eval infra.

**Stratification:** by model version, locale, tool-use, risk classifier score, free vs paid—so rare safety slices aren’t drowned.

### 3.6 Safety metrics (first-class)

| Metric family | Examples | Scoring |
|---------------|----------|---------|
| Harmlessness | Toxic/violent/criminal assistance | Classifiers + human |
| Honesty | Hallucination on grounded tasks; calibration | Rubrics + factuality checks |
| Jailbreak resistance | Prefill/roleplay/obfuscation suites | Success rate ↓ is good |
| Over-refusal | Benign refused | Track false refusals |
| Child safety / CSAM | Separate vault; specialized classifiers | Highest severity; dual control |
| Prompt injection | Tool/browser contexts | Adversarial suites |

**Reporting:** always pair attack success rate with over-refusal; optimizing one can destroy the other.

### 3.7 Human review

```text
Triggers:
  - Critical safety failures (auto-enqueue)
  - Judge confidence low / judge≠classifier
  - Random audit sample
  - Researcher-requested adjudication

Queue priorities: P0 safety > P1 gate-blocking > P2 calibration > P3 research

Double-label rate for calibration; compute Cohen’s κ
Adjudication creates gold labels that can graduate into golden sets
```

**UX:** side-by-side model outputs; hide model identity for blind review when measuring preference.

### 3.8 Regression detection & gates

| Gate type | When | Fail behavior |
|-----------|------|---------------|
| **Canary** | Pre-promote | Block promote; fail-closed on infra error |
| **Full** | Nightly / release train | Alert; block only for major version if configured |
| **Online** | Continuous | Alert; auto-rollback policy optional & careful |
| **Slice** | Per-domain thresholds | Fail if any critical slice regresses beyond ε |

**Statistical gate (chosen):**

```text
Fail if:
  (metric_new - metric_base) < -ε
  AND CI suggests real drop (e.g. p < α or CI entirely below -ε)
  OR any P0 safety absolute threshold breached
```

**Deal-breaker:** gate that “passes” when scoring didn’t finish.

### 3.9 Contamination controls

```text
Item ingest → normalize → fingerprint
  → near-dup vs training corpus bloom/index (best-effort)
  → near-dup vs other evals
  → mark contamination_state: clean | suspect | known_train | held_out_vault

Held-out vault: never used in training; physical/process isolation
If contamination found post-hoc: mark runs suspect; recompute gates excluding item
```

Honest interview line: perfect membership inference is hard—**process + vault + monitoring** beats claiming cryptographic proof.

### 3.10 API shape (internal)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/datasets` | Create dataset |
| POST | `/v1/datasets/{id}/versions` | Publish immutable version |
| POST | `/v1/evals/runs` | Start eval run |
| GET | `/v1/evals/runs/{id}` | Status + metrics |
| POST | `/v1/gates/check` | Evaluate promote decision |
| GET | `/v1/review/tasks` | Review queue |
| POST | `/v1/review/tasks/{id}/label` | Submit label |
| GET | `/v1/monitors/metrics` | Online series |

```http
POST /v1/evals/runs
Idempotency-Key: ...
{
  "suite_id": "suite_canary_v12",
  "subject": {
    "model_version": "claude-X",
    "system_prompt_hash": "sha256:...",
    "decoding": {"temperature": 0}
  },
  "baseline_run_id": "run_...",
  "priority": "release"
}
```

### 3.11 High-level component trade-offs

| Component | Options | Choice |
|-----------|---------|--------|
| Metadata DB | Postgres vs Dynamo | Postgres cells MVP |
| Artifacts | S3/GCS | Object store + manifest |
| Metrics | Prometheus only vs warehouse | TSDB for alerts + warehouse for science |
| Orchestration | Cron + k8s jobs vs Temporal | Temporal/workflow engine for runs |
| Judge | Always frontier LLM | Distilled + escalate |
| Online sample store | Kafka+Parquet | Tiered |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +------------------+     +---------------------+
| Web UI /    |---->| API Gateway /    |---->| Control Plane       |
| CLI / CI    |     | AuthZ            |     | (datasets, runs,    |
+-------------+     +--------+---------+     |  gates, review)     |
                             |               +----------+----------+
                             |                          |
                             v                          v
                    +----------------+         +--------+----------+
                    | Workflow       |-------->| Metadata Postgres |
                    | Orchestrator   |         | + Audit log       |
                    +--------+-------+         +-------------------+
                             |
         +-------------------+-------------------+------------------+
         v                   v                   v                  v
+----------------+  +----------------+  +----------------+  +---------------+
| Batch Infer    |  | Scoring Fleet  |  | Object Store   |  | Human Review  |
| Workers (GPU)  |  | (judge/clf)    |  | artifacts      |  | Service       |
+--------+-------+  +--------+-------+  +----------------+  +---------------+
         |                   |
         v                   v
+----------------+  +----------------+
| Inference GW   |  | Metrics TSDB + |
| + Prompt Cache |  | Warehouse      |
+----------------+  +--------+-------+
                             ^
+----------------+           |
| Prod Sampler   |-----------+
| (online path)  |
+----------------+
```

### 4.2 Offline run data plane

```text
EvalRun
  → Item shards (hash(item_id) % N)
       → Packer (length buckets)
            → Inference batch
                 → Output blobs
                      → Score DAG
                           → Aggregates
                                → Gate
```

### 4.3 Online path

```text
Edge/Prod → Scrub → Sample → Kafka
                              ├→ cheap classifiers (sync-ish microbatch)
                              └→ escalate → judge pool
Metrics exporter → Alertmanager
```

### 4.4 Safety vault isolation

```text
[General eval cell] ----X---- [Safety vault cell]
                         only aggregated metrics +
                         signed gate attestations cross the boundary
Raw jailbreak prompts/outputs stay in vault
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Reproducibility package per run:**

- Pins: dataset snapshot, rubric versions, subject config, judge model, decoder seeds (as applicable), scorer code digest, inference route.
- Store raw outputs; re-scoring possible if rubric changes (new run linking prior outputs).

**Failure modes:**

| Failure | Mitigation |
|---------|------------|
| Worker crash mid-shard | Checkpoint per item; lease reclaim |
| Inference 5xx | Retry with jitter; poison-pill items after N |
| Judge timeout | Requeue; don’t drop silently |
| Partial suite | Status `failed` or `completed_suspect`; gate fail-closed |
| Duplicate submit | Idempotency-Key on create run |
| Split brain promote | Gate service single-writer per subject; lease |

**Exactly-once scoring?** At-least-once with idempotent `item_result` upsert on `(run_id, item_id, scorer_version)`.

### 5.2 Scalability

**Sharding:**

- Items by `hash(item_id)`.
- Runs metadata by `org_id` cell.
- Warehouse partitions by `day, suite_id`.

**Batching & GPU:**

```text
Goal: maximize tokens/sec/GPU and goodput
- Dynamic batching; pad carefully
- Prefix cache for shared rubrics/system
- Avoid tiny runs monopolizing GPUs: coalesce research jobs off-peak
- Priority lanes: release canary > online escalate > research
```

**100× path:**

- Multi-cell orchestrators.
- Dataset CDN for hot golden sets near GPU regions.
- Hierarchical aggregation (shard → run → suite).

**1,000× path:**

- Sampled full suites with variance estimates.
- Distilled judges for 95% volume.
- Cold storage for artifacts; retrieve on demand.

### 5.3 Maintainability

- **Metric catalog** as code + DB: breaking changes require new metric version.
- **Scorer plugins** versioned containers; no silent logic change under old version ID.
- **CI for platform:** unit tests for aggregations; golden tests for gate math.
- **Rubric review** same as code review for safety-critical suites.
- **Data retention jobs** documented; legal hold support.

### 5.4 Canary vs full regression (detail)

```text
Canary (~5K–20K items):
  - High power on critical slices
  - Blocks promote
  - Runs on reserved capacity

Full (~100K–1M+ items):
  - Broad coverage
  - Nightly; may use spot
  - Informs but only blocks majors if configured
  - Produces slice heatmaps

Promotion flow:
  build → unit/safety classifiers → canary gate → staged traffic
       → full suite in parallel → online monitors soak → full promote
```

### 5.5 LLM-as-judge design

| Issue | Mitigation |
|-------|------------|
| Position bias | Randomize order; average |
| Verbosity bias | Rubric penalties; structured JSON scores |
| Judge drift | Pin version; weekly human calibration |
| Cost | Cascade: rules → clf → distilled → frontier |
| Circularity | Never use same model family exclusively for self-eval on safety P0 |

**Output schema:** score ∈ [0,1] or Likert; rationale stored; rationale not trusted alone for gates.

### 5.6 Human review queue internals

```text
ReviewTask {
  id, priority, reason, item_result_ids[],
  blind: bool, assignees[], status,
  labels[], adjudication, sla_deadline
}
```

- Lease tasks to reviewers; heartbeat; reassign on timeout.
- Gold traps (known answers) to detect careless labeling.
- Export adjudicated labels → candidate golden set PR.

### 5.7 Online drift detection

```text
For each (model_version, slice, metric):
  rolling baseline window (e.g. 7d)
  detect: mean shift, proportion spike, PSI on score dist
Alert if sustained beyond burn-in and volume threshold
```

**Careful:** product mix shifts (more coding questions) look like “quality drop”—slice and covariate-adjust.

### 5.8 Security & privacy

- RBAC: `dataset:read`, `safety_vault:read`, `gate:override`, etc.
- Encryption at rest; vault KMS keys separate.
- Prod sample scrubbers: PII NER + patterns; drop on failure for durable offline copies.
- Audit every override and dataset publish.
- No training pipeline read access to vault without dual control.

### 5.9 Cost controls

| Lever | Effect |
|-------|--------|
| Prefix cache | Big save on repeated rubrics |
| Decode temp=0 for evals | Stability + cache friendliness |
| Distilled judges | 5–20× token save |
| Stratified sampling | Full-suite cost sublinear |
| Reserved GPUs for canary only | Predictable latency; spot for research |
| Output truncation caps | Bound worst-case tokens |

### 5.10 Consistency model for gates

```text
GateCheck reads:
  - completed aggregates for required suites
  - thresholds config version
  - open critical review tasks count

If any required run not terminal-success → FAIL (fail-closed)
If overrides present → PASS_WITH_OVERRIDE + audit
Emit signed GateAttestation for CD system
```

---

## 6. Wrap-Up

### 6.1 What we designed

A **model evaluation and monitoring platform** that treats evals as reproducible distributed batch jobs: immutable dataset versions, pinned subjects, GPU-efficient inference, layered scorers, human review, and fail-closed canary gates—plus an asynchronous online sampling path for drift—without blocking production chat on eval infra.

### 6.2 Progressive scale summary

| Scale | Dominant change |
|-------|-----------------|
| Baseline | Postgres + workflows + batch GPU + warehouse |
| 10× | Priority fleets; object artifact discipline; review SLAs |
| 100× | Cells; vault isolation; online stream metrics; judge cascade |
| 1,000× | Heavy sampling; distilled judges; multi-region; cold tiers |

### 6.3 Deal-breakers (memorize)

1. Mutable datasets under a published run.  
2. Gate pass when scoring incomplete.  
3. Safety raw data leaking to unrestricted logs.  
4. Claiming significance on tiny n.  
5. Online eval adding user-facing latency.  
6. Sole reliance on an uncalibrated LLM-judge for P0 safety.

### 6.4 Interview closing line

> I’d pin every input to an eval run, batch for GPU efficiency, score with a cascade, keep humans on the critical path for safety, and make promote gates fail-closed with confidence intervals—not vibes.

---

## 7. Deeper / Related Interview Questions

### 7.1 Why immutable dataset versions?

**A:** Reproducibility and audit. If someone “fixes a typo” in place, historical comparisons lie and gates become meaningless. Publish `v+1`; pin runs to snapshot hashes.

### 7.2 Exact match vs LLM-judge vs human—when each?

**A:** Exact/regex for deterministic tasks (code unit tests, structured extract). Classifiers for high-volume safety. LLM-judge for nuanced helpfulness. Humans for calibration, disputes, and P0 safety. Cascade for cost.

### 7.3 How do you detect contamination?

**A:** Fingerprints, near-dup search against training corpora (best-effort), process isolation for holdouts, canary strings, and post-hoc quarantine. Be honest that perfect detection is unsolved; engineering controls matter.

### 7.4 How large should a canary be?

**A:** Sized for statistical power on critical metrics/slices within wall-clock/cost budget. Often thousands of items, stratified. Pair with absolute P0 safety thresholds that don’t wait for tiny CI.

### 7.5 What if judge and human disagree a lot?

**A:** Pause trusting judge for that rubric; run calibration; measure κ; revise rubric/prompt; possibly distill from new gold. Don’t silently average away disagreement.

### 7.6 Online vs offline disagreement—whom do you trust?

**A:** Offline golden for release gates; online for drift under real mix. Investigate distribution shift. Neither blindly overrides P0 safety absolute monitors.

### 7.7 How do you schedule GPUs fairly across research and release?

**A:** Priority queues + quotas per team; reserved pool for canaries; preemption of research batch on release pressure; cost showback.

### 7.8 Fail-open or fail-closed for gates?

**A:** **Fail-closed** for promote gates. Fail-open only for non-blocking monitoring dashboards. Infra errors must not look like “model is fine.”

### 7.9 How do you handle multilingual evals?

**A:** Separate slices; native rater pools; avoid English-only judges for non-English without validation; track coverage gaps explicitly.

### 7.10 Metric gaming by models trained on public benchmarks?

**A:** Private holdout vaults, frequent adversarial refresh, contamination monitoring, and don’t use public leaderboard sets as sole ship criteria.

### 7.11 How do you version rubrics?

**A:** Rubric IDs with semver; runs pin rubric version; changing rubric creates new metric series—don’t splice incompatible scores.

### 7.12 Canary green but full suite red—ship?

**A:** Depends on policy: often ship to staged % with heightened online monitors if canary covers critical risk; block majors. Document risk. Dual-control override if business-critical.

### 7.13 How do you stop eval jobs from melting production inference?

**A:** Separate queues/pools; different auth keys; rate limits; priority isolation; batch endpoints; never share interactive latency SLOs with eval bulk.

### 7.14 What aggregates do you store vs recompute?

**A:** Store per-item scores + run aggregates. Recompute slice pivots in warehouse. Keep raw outputs for re-judge under retention.

### 7.15 How do you test the eval platform itself?

**A:** Golden fixtures with known scores; chaos on workers; gate math unit tests; canary on the platform’s own regressions (meta).

### 7.16 Privacy of production samples?

**A:** Scrub before durable offline; minimize retention; access logs; prefer aggregated metrics; contractual/enterprise constraints may forbid raw sample export.

### 7.17 How does prompt caching change eval cost math?

**A:** Shared system/rubric prefixes → large input token discount; structure prompts for stable prefixes; still pay for unique task suffixes and outputs.

### 7.18 Multi-tenant enterprise eval SaaS—what changes?

**A:** Hard tenancy on datasets/results; customer-managed keys optional; no cross-tenant judge caches of sensitive prompts; showback billing; regional residency.

### 7.19 How do you represent tool-using agents in evals?

**A:** Scripted tool stubs or recorded environments; grade trajectories + final answer; cap steps; deterministic tool fixtures for golden.

### 7.20 What is a deal-breaker regression signal?

**A:** Any statistically meaningful drop on canary quality beyond ε, or any absolute breach of P0 safety thresholds (jailbreak ASR, child safety), or incomplete scoring treated as pass.

### 7.21 How do you handle nondeterminism?

**A:** temp=0 where possible; multiple samples for stochastic metrics; report distribution not single seed; pin seeds when API allows.

### 7.22 Should safety suites be public?

**A:** Generally no—publication accelerates attacks. Share aggregated research carefully; keep operational suites private in vault.

### 7.23 How do alerts avoid pager fatigue?

**A:** Multi-window confirmation, min volume, slice-aware baselining, severity routing, auto-close on return-to-baseline, runbooks.

### 7.24 Dataset PR review process?

**A:** Code-review-like: ownership, lint fingerprints, contamination scan, sample human audit, publish only via CI.

### 7.25 How do you compare two models with different verbosity?

**A:** Length-aware rubrics; normalize tasks; pairwise preference with position randomization; report cost/latency jointly with quality.

### 7.26 What belongs in CI of a model PR vs nightly?

**A:** CI: unit tests + tiny smoke + critical safety classifiers + small canary. Nightly: full suites + broad slices + expensive judges.

### 7.27 How do you store huge output corpora cheaply?

**A:** Object store, compression, columnar analytics exports, tiered retention, content-addressed dedup of repeated system strings.

### 7.28 Interplay with RLHF / preference platforms?

**A:** Eval platform consumes preference models as scorers; does not replace preference collection. Clear boundary: measure vs train.

### 7.29 What if CD cannot reach gate service?

**A:** Fail-closed: no promote. Cache last attestation only for emergency with dual-control break-glass, heavily audited.

### 7.30 Summarize the Anthropic-flavored angle

**A:** Evaluation rigor and safety metrics are product requirements, not dashboards bolted on. Ordinary queueing, immutability, and fail-closed gates—applied to GPU batch scoring and human review—keep model releases honest.

### 7.31 How do you budget tokens for judge prompts?

**A:** Fixed rubric prefix + truncated candidate outputs + structured response schema; hard max_tokens; reject/retry malformed JSON.

### 7.32 Slice discovery—manual or automatic?

**A:** Start manual critical slices; add automatic clustering of failures for research hypotheses; never auto-add slices to gates without review.

### 7.33 Cross-version prompt changes vs weight changes?

**A:** SubjectUnderTest includes prompt hash. Diff runs should isolate whether regression is weights, prompts, or tools.

### 7.34 How do you handle flaky items?

**A:** Track item-level variance; quarantine flakes; require multi-sample agreement; don’t let flakes flip gates randomly.

### 7.35 Warehouse vs OLTP responsibilities?

**A:** OLTP: control plane, active runs, review. Warehouse: longitudinal science, heavy joins, ad-hoc. TSDB: alerting.

### 7.36 What is “honest” reporting in a launch doc?

**A:** n per slice, CI, effect sizes, known contamination caveats, judge versions, and which gates were overridden—alongside headline scores.

### 7.37 Can online monitors auto-rollback models?

**A:** Optional for severe P0 with high precision detectors; prefer page humans for ambiguous quality dips. Auto-rollback needs rehearsal and blast-radius limits.

### 7.38 How do you onboard a new benchmark?

**A:** Import → fingerprint → contamination scan → pilot scoring → human spot-check → tag → add to suite with thresholds only after baseline week.

### 7.39 GPU stragglers in a shard?

**A:** Timeout + reassignment; speculative retry; exclude pathological prompts with cap; report straggler tail in run metrics.

### 7.40 Final system one-liner

**A:** Immutable data in, batched GPU out, cascaded scores, humans on P0, fail-closed canaries, online drift in shadow—distributed systems with an evaluation conscience.

---

## Appendix A: Example metric definitions (interview cheat sheet)

| Metric | Type | Direction | Gate? |
|--------|------|-----------|-------|
| `helpfulness_mean` | [0,1] | ↑ | canary ε |
| `honesty_grounded` | [0,1] | ↑ | canary ε |
| `jailbreak_asr` | rate | ↓ | absolute + ε |
| `over_refusal` | rate | ↓ | watch + soft |
| `latency_p95_ms` | ms | ↓ | capacity gate |
| `cost_per_task_usd` | $ | ↓ | budget gate |
| `judge_human_kappa` | κ | ↑ | platform health |

## Appendix B: Run manifest (sketch)

```json
{
  "run_id": "run_...",
  "dataset_snapshots": ["ds:canary:v12@sha256:..."],
  "subject": {"model_version": "claude-X", "system_prompt_hash": "sha256:..."},
  "judge": {"model_version": "judge-Y", "rubric": "rubric_help_v3"},
  "scorer_digests": ["sha256:..."],
  "seeds": {"shuffle": 42},
  "inference_route": "batch-pool-a",
  "created_by": "user:...",
  "gate_policy_version": "gp_v8"
}
```

## Appendix C: Priority queue weights (example)

```text
release_canary: 100
online_escalate: 80
pre_release_full: 60
research_interactive: 40
research_batch: 10
best_effort_rejudge: 5
```

## Appendix D: Contamination states

| State | Meaning | Eligible for gate? |
|-------|---------|--------------------|
| `clean` | No signals | Yes |
| `suspect` | Near-dup weak signal | Optional exclude |
| `known_train` | Confirmed overlap | No |
| `held_out_vault` | Protected | Yes (vault only) |

## Appendix E: Review SLA examples

| Priority | First touch | Resolution |
|----------|-------------|------------|
| P0 safety | 15m | 4h |
| P1 gate | 1h | 1 business day |
| P2 calibration | 1 day | 1 week |
| P3 research | best effort | backlog |

## Appendix F: Aggregation formulas (say out loud)

```text
mean_score = sum(score_i) / n
Wilson or bootstrap CI for proportions
Delta = mean_new - mean_base
Gate fail if delta < -ε and CI supports, OR hard safety threshold
Always publish n_slice; suppress if n < n_min
```

## Appendix G: Object store layout

```text
s3://evals/
  datasets/{dataset_id}/{version}/items/{item_id}.json
  datasets/{dataset_id}/{version}/manifest.json
  runs/{run_id}/outputs/{item_id}.json
  runs/{run_id}/scores/{scorer}/{item_id}.json
  runs/{run_id}/aggregates.json
  runs/{run_id}/manifest.json
```

## Appendix H: Online sampler pseudocode

```text
on_prod_turn(event):
  if not scrub(event): drop
  key = hash(user_id, turn_id, salt_week)
  if key % 10000 < sample_rate_bps:
    enrich(model_version, slices...)
    kafka.emit(sample)
```

## Appendix I: Escalate policy

```text
if safety_clf_score > t_high: enqueue P0 review + judge
elif disagreement(clf, distilled_judge): enqueue judge_frontier
elif random() < audit_rate: enqueue audit
else: metrics only
```

## Appendix J: Release train integration

```text
CD pipeline:
  1. build artifact
  2. request GateCheck(subject)
  3. require attestation signature
  4. deploy staged
  5. soak online monitors
  6. full promote
Break-glass: dual approval + page safety oncall
```

## Appendix K: Common interview math checks

```text
Items/day 5M × 2KB out ≈ 10 TB/day raw? → usually smaller after sampling;
  use 5M × 2KB = 10 GB/day — catch unit errors
GPU hours ≈ total_out_tokens / tokens_per_sec / 3600
Judge cost often ≥ generation if verbose rationales—truncate rationales in bulk path
```

## Appendix L: Failure injection tests

| Chaos | Expected |
|-------|----------|
| Kill infer worker | Shard resumes; no false pass |
| Judge 100% 500 | Run fails; gate fail |
| Postgres failover | In-flight leases recover |
| Object store lag | Backpressure; no silent empty scores |
| Duplicate Idempotency-Key | One run |

## Appendix M: RBAC matrix (abbrev)

| Role | Create dataset | Read safety vault | Override gate | Label review |
|------|----------------|-------------------|---------------|--------------|
| Researcher | Y (team) | N | N | Y |
| Safety | Y | Y | N (dual) | Y |
| Release | N | N | Y (dual) | N |
| Admin | Y | Y | Y | Y |
| Viewer | N | N | N | N |

## Appendix N: Slice examples

```text
language=en|es|...
domain=code|math|creative|medical_benign
tools=none|browser|code
risk_prior=low|mid|high
user_tier=free|paid
jailbreak_family=roleplay|obfuscation|prefill|...
```

## Appendix O: Closing checklist for the whiteboard

1. Pin immutable snapshots  
2. Split control vs GPU vs online vs review loads  
3. Canary fail-closed + stats  
4. Safety vault  
5. Judge cascade + human P0  
6. Cost: cache, batch, sample  
7. Contamination honesty  
8. Scale narrative 10×/100×/1,000×  

---

*End of document — Model Evaluation & Monitoring Platform (Anthropic interview prep)*
