# System Design: Novel Practical LLM System (Interview Playbook + Worked Example)

> **Focus areas:** Scoping ambiguous prompts · First-principles reasoning · Reusable interview playbook · Worked example system  
> **Style:** Meta-interview skill + one full design (“Constitutional AI Feedback Loop Service”)  
> **Company theme:** Anthropic often asks *novel* practical LLM systems — ordinary distributed systems inside unfamiliar AI product/infra packaging  
> **Quality bar:** Strong clarify questions, honest estimates, explicit tradeoffs, safety/cost/reliability always considered

---

## Table of Contents

1. [Why This Doc Exists](#1-why-this-doc-exists)
2. [Reusable Interview Playbook for Any Novel Anthropic Prompt](#2-reusable-interview-playbook-for-any-novel-anthropic-prompt)
3. [Worked Example — Constitutional AI Feedback Loop Service](#3-worked-example--constitutional-ai-feedback-loop-service)
4. [Alternate Novel Prompts (Drill Pack)](#4-alternate-novel-prompts-drill-pack)
5. [Wrap-Up: Transferable Patterns](#5-wrap-up-transferable-patterns)
6. [Deeper / Related Interview Questions](#6-deeper--related-interview-questions)

---

## 1. Why This Doc Exists

Anthropic system-design interviews frequently **do not** hand you a commodity “design Twitter.” Instead you get something like:

- “Design a service that continuously improves model behavior from preference feedback under a constitution.”  
- “Design a long-context document understanding API.”  
- “Design a real-time safety classification sidecar for streaming tokens.”

The *exact* problem varies. What is stable:

1. **Clarify** until the problem is a system with interfaces and SLOs.  
2. **Estimate** tokens, QPS, storage, GPU — show arithmetic.  
3. **Split planes** (control vs data; online vs offline; sync vs async).  
4. **Name invariants** (safety fail-closed, idempotency, tenancy).  
5. **Scale** with 10×/100×/1,000× jumps.  
6. **Tie to GPU efficiency, reliability, safety, cost.**

This doc teaches the **playbook**, then runs it end-to-end on one novel system, then gives alternate drills.

---

## 2. Reusable Interview Playbook for Any Novel Anthropic Prompt

### 2.1 Mindset (30 seconds)

> “I haven’t designed this exact product, so I’ll bound it with questions, propose a thin MVP, and apply classic distributed-systems + LLM serving patterns.”

Signals confidence without fake expertise.

### 2.2 The 7-phase clock (45–60 min)

| Phase | Minutes | Output on whiteboard |
|-------|---------|----------------------|
| 1. Clarify | 8–12 | Requirements table; MVP / out |
| 2. Estimate | 5–7 | QPS, tokens/s, storage, cost drivers |
| 3. HLD | 8–10 | Boxes + APIs + tradeoffs |
| 4. Diagram | 3–4 | ASCII / boxes |
| 5. Deep dive | 10–15 | Reliability, scale, safety, maintainability |
| 6. Wrap | 3 | Decisions + risks |
| 7. Stretch Qs | remaining | Graceful extensions |

If interviewer pushes early into deep dive, **compress** clarify to top 5 questions — don’t skip entirely.

### 2.3 Clarify Requirements — question banks

Always cover four buckets: **Functional, NFR, Cases, Scales** (+ Etc constraints).

#### Functional question bank (pick 6–10)

| # | Ask | Why |
|---|-----|-----|
| F1 | Who is the user (human, model, internal service)? | Interface shape |
| F2 | What is the atomic unit of work? | Job / request / episode |
| F3 | Sync vs async vs streaming? | Architecture fork |
| F4 | Inputs/outputs schema? | Storage + validation |
| F5 | Human-in-the-loop? | Workflow |
| F6 | Multi-tenant? | Isolation |
| F7 | Online path vs offline training loop? | Split planes |
| F8 | Idempotency / retries? | Exactly-once needs |
| F9 | Versioning of models/policies? | Pinning |
| F10 | Admin / kill switch? | Operability |

#### NFR question bank

| # | Ask | Typical Anthropic flavor |
|---|-----|--------------------------|
| N1 | Latency SLO? | TTFT / decision deadline |
| N2 | Durability RPO/RTO? | Feedback must not vanish |
| N3 | Consistency? | Pointers atomic vs eventual analytics |
| N4 | Availability vs fail-closed safety? | **Safety often fail-closed** |
| N5 | Cost envelope? | GPU dominant |
| N6 | Privacy / retention? | Logs sensitive |
| N7 | Fairness / noisy neighbor? | Tenants |

#### Cases

- Happy path walkthrough (60s narrative).  
- Failure: dependency down, poison input, retry storm, partial write, model timeout, policy deny.  
- Abuse: prompt injection, exfil, ballot stuffing on feedback.

#### Scales table (always draw)

| Metric | 1× | 10× | 100× | 1,000× |
|--------|----|-----|------|--------|
| QPS / jobs | | | | |
| Tokens/s | | | | |
| Storage growth | | | | |
| Cardinality (tenants/models) | | | | |

Ask interviewer for baseline; if none, **state assumptions**.

#### Etc.

- Regions, compliance, existing gateways you may assume (InferGW, object store).  
- Explicit **out of scope** list — shows maturity.

### 2.4 First-principles decomposition (when the problem is weird)

Ask yourself five questions:

1. **Where do bits enter and leave?** (API, stream, queue, human UI)  
2. **What must be correct vs approximate?** (safety decisions vs analytics)  
3. **What is GPU-bound vs CPU/IO-bound?**  
4. **What is online-synchronous vs batch-offline?**  
5. **What can be eventually consistent?**  

Then map to known patterns:

| If you see… | Reach for… |
|-------------|------------|
| Fanout of large artifacts | Chunking, P2P/tree, manifests |
| Token streams | SSE, checkpoints, safety buffer |
| Preference / labels | Event log, aggregation, rater UX |
| Sidecar decisions | Out-of-band RPC with deadline + fail policy |
| Long documents | Chunk + index + selective expand |
| Agents | State machine + tools + policy |
| Training loops | Offline pipeline + online serving split |
| Multi-tenant SaaS | Cells, quotas, authz |

### 2.5 Back-of-envelope recipes

**Tokens/day:**

\[
\text{tokens/day} ≈ \text{requests/day} × (\text{tokens_in} + \text{tokens_out})
\]

**GPU order-of-magnitude:**

\[
\text{GPUs} ≈ \frac{\text{output_tokens/s}}{\text{tok/s per GPU}} × \text{headroom}
\]

**Storage:**

\[
\text{bytes/day} ≈ \text{events/day} × \text{avg_event_size}
\]

**Queue lag:**

If consume rate < produce rate, lag → ∞; admission required.

**Always say assumptions aloud** (“assume 150 tok/s decode effective…”).

### 2.6 HLD recipe (boxes you can reuse)

Most novel LLM systems need some subset of:

```text
Client/API → Admission/Quota → Orchestrator/Workflow
     → Inference Gateway → Model Pools
     → Safety / Policy
     → Storage (OLTP + object + queue + index)
     → Async Workers (train/eval/aggregate)
     → Observability + Admin/Kill
```

**Tradeoff table** mandatory: pick 3–5 controversial choices.

### 2.7 Deep dive pillars (Anthropic-weighted)

1. **Reliability** — invariants, failure table.  
2. **Scalability** — what breaks at 10×/100×/1,000×.  
3. **Maintainability** — versioning, replay, metrics cardinality.  
4. **Safety** — fail-closed points, injection, audit.  
5. **Cost / GPU efficiency** — batching, caching, avoid idle.  

### 2.8 Communication patterns that score well

- Restate the problem in one sentence before drawing.  
- Narrate tradeoffs (“I’d pick X because Y; Z if constraints flip”).  
- Invite course-correction (“If safety SLO is stricter, we’d…”).  
- Don’t invent fake proprietary tech names — describe mechanisms.  
- When stuck: return to **interfaces + invariants**.

### 2.9 Anti-patterns (avoid)

- Jumping to Kafka → Flink → feature store before clarifying sync path.  
- Designing full RL training cluster when they asked for an API.  
- Ignoring safety fail mode.  
- Infinite precision estimates.  
- No admission control on queues.  
- “The model will handle it” as an isolation boundary.

### 2.10 2-minute emergency template (if time collapses)

1. Users + atomic request.  
2. Sync path boxes.  
3. Async path boxes.  
4. Three invariants.  
5. One scale jump.  
6. Top risk.

---

## 3. Worked Example — Constitutional AI Feedback Loop Service

> **Novel prompt:** Design a practical service that collects preference / critique feedback on model outputs, evaluates them against a written **constitution** (principles), and feeds a continuous improvement loop (reward model / preference datasets / eval gates)—without letting noisy or adversarial feedback silently corrupt production models.

We now run the full standard structure.

### 3.1 Clarify Requirements (Interview Q&A)

#### 3.1.0 Problem framing

| Plane | Question |
|-------|----------|
| Online | How do we capture feedback & run constitutional checks? |
| Offline | How do we aggregate into datasets / training signals? |
| Gate | How do we prevent bad loops from shipping? |

**Not in MVP:** Fully automated unsupervised weight updates to frontier prod with zero human gates.

#### 3.1.1 Functional Requirements

| # | Question | Expected answer | Implication |
|---|----------|-----------------|-------------|
| F1 | Who submits feedback? | End users, raters, automated critics | Authz + trust scores |
| F2 | Feedback types? | Thumbs, pairwise pref, free-text critique, category tags | Schema evolution |
| F3 | Constitution? | Versioned principle set | Pin `constitution_version` |
| F4 | Online critique? | Optional AI critic grades output vs constitution | InferGW jobs |
| F5 | Pairwise sampling? | Yes for RM training | Pair builder |
| F6 | Human rater UX? | Internal + vendor | Task queues |
| F7 | Training consumer? | Preference datasets to RM / RLAIF pipelines | Export contracts |
| F8 | Prod gate? | Eval suite + human review before promote | Rollout service hook |
| F9 | Provenance? | Every label → conversation span + model version | Lineage |
| F10 | Abuse? | Ballot stuffing, coordinated attacks | Rate limits + anomaly |
| F11 | Streaming chats? | Feedback on partial or final | Attach to turn_id |
| F12 | Multi-model? | Many model versions parallel | Partition datasets |

**MVP scope:**

1. Ingest feedback events tied to immutable `turn_id` / `span_id`.  
2. Store constitution versions; run **AI critic + rules** scoring online (async OK).  
3. Rater tasks for pairwise preferences on sampled spans.  
4. Build preference pairs / critique corpora with lineage.  
5. Export to training lake; metrics dashboards.  
6. **Promotion gate** API: “dataset bundle X approved for train job Y.”  
7. Quotas, abuse detection, audit.

**Out of MVP:** Automatic prod weight publish; public rater marketplace; multilingual constitution editor UI polish.

#### 3.1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Ingest latency ACK | p99 < 200ms |
| N2 | Critic scoring freshness | p50 < 30s async; optional sync path < 2s for admin |
| N3 | Durability | ACK ⇒ durable event |
| N4 | Safety of loop | No auto-prod without gates |
| N5 | Privacy | PII redaction options; retention TTLs |
| N6 | Availability | Ingest 99.9%; critic degrade to queue |
| N7 | Auditability | Who approved which bundle |
| N8 | Cost | Critic tokens bounded by sampling |

#### 3.1.3 Cases

**Happy:**

1. User thumbs-down → event → critic labels principle violations → enters review sample.  
2. Rater prefers response A over B → pair stored with constitution_v3.  
3. Nightly job builds `prefs_bundle_2026-08-05` → eval harness → train RM.  
4. Bad bundle fails eval → no promote.

**Edge:**

| Case | Behavior |
|------|----------|
| Feedback on deleted chat | Retain span snapshot at feedback time or reject |
| Constitution hot-edit mid-rate | Pin version on task creation |
| Adversarial thumbs farming | Trust score; downsample; anomaly |
| Critic outage | Queue; don’t drop ingest |
| Duplicate feedback | Idempotency key |
| Poison pair (PII) | Redaction pipeline; quarantine |
| Train job reads partial export | Manifest commit atomic |

#### 3.1.4 Scales

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Feedback events / day | 5M | 50M | 500M | 5B |
| Critic LLM calls / day | 1M (sampled) | 10M | 50M (smarter sample) | hierarchical |
| Active raters | 500 | 5k | 50k | vendor mesh |
| Pairwise tasks / day | 200k | 2M | 20M | 200M |
| Constitution versions | 20 | 50 | 100 | many experiments |
| Models under study | 10 | 50 | 200 | 1k |
| Export bundle size | 200 GB | 2 TB | 20 TB | lakehouse |
| Ingest QPS peak | 200 | 2k | 20k | 200k |

**Jumps:** 10× → stream processing; 100× → sample aggressively + cells; 1,000× → federated rater + tiered critic models.

#### 3.1.5 Etc.

- Assume Chat/API products emit `turn` references.  
- Training cluster is a **consumer**; this service owns **labels + gates**.  
- Constitution text is sensitive product IP — ACL.

**Scope statement:**

> Design a Constitutional AI feedback loop service: durable multi-source feedback ingest, versioned constitution, AI critic + human preference pipelines, lineage-rich dataset export, abuse resistance, and hard promotion gates—so improvement loops are practical, measurable, and safe at progressive scale.

---

### 3.2 Back-of-the-Envelope

#### 3.2.1 Ingest volume

- 5M events/day × 2 KB ≈ 10 GB/day raw events (~3.5 TB/year). Trivial with object+OLTP hybrid; metadata in PG/KV.

#### 3.2.2 Critic cost

- If every event criticized at 2k tokens × $: too expensive.  
- **Sample:** 20% of negatives + 5% of positives + all safety-tagged → ~1M calls/day.  
- 1M × 2k tokens = 2B tokens/day → need dedicated critic pool or batch.

#### 3.2.3 Rater throughput

- 500 raters × 40 pairs/hr × 8 hr = 160k pairs/day — order matches baseline table; scale with vendors at 10×.

#### 3.2.4 Export

- 200k pairs × 4 KB = 800 MB/day text; with full context snapshots larger (10–50 KB) → 2–10 GB/day — fine.

#### 3.2.5 Why sampling is the design

Unbounded critic on 1,000× events is financially impossible; **priority sampling** is first-class architecture, not an optimization footnote.

#### 3.2.6 Gate frequency

- Bundles daily/hourly; promote weekly for large RM trains; online eval continuous.

---

### 3.3 High-Level Design

#### 3.3.1 Design goals

1. Durable, attributable feedback.  
2. Constitution-versioned judgments.  
3. Human + AI signals fused carefully.  
4. Safe export & promote.  
5. Cost-controlled critic.  
6. Abuse-resistant aggregation.

#### 3.3.2 Components

| Component | Role |
|-----------|------|
| Feedback Ingest API | ACK durable events |
| Span Store | Snapshot of model I/O under feedback |
| Constitution Registry | Versioned principles |
| Sampler | Which events get critic/rater |
| Critic Workers | LLM grades vs constitution |
| Rater Task Service | Pairwise / critique UX |
| Trust & Abuse | Account scores, anomalies |
| Pair / Dataset Builder | Assemble bundles + manifests |
| Eval Harness Gate | Quality/safety checks on bundles |
| Export Lake | Parquet/JSONL + lineage |
| Promotion Controller | CAS approve bundles for training |
| Admin / Audit | Constitution edits, promotes |
| Telemetry | Loop health |

#### 3.3.3 Online vs offline split

```text
ONLINE: ingest → durable log → sample decision → (optional) enqueue critic
NEARLINE: critic score → annotate; generate rater tasks
OFFLINE: build pairs → eval → export → (external) train → (external) model distro
GATE: Promotion Controller stands between export and train consume
```

#### 3.3.4 Constitution object

```text
ConstitutionVersion {
  id, principles: [{id, text, severity, examples}],
  signature, created_by, created_at
}
```

Critic prompt templates pin `constitution_id`. Rater guidelines render same principles.

#### 3.3.5 Feedback event schema

```text
FeedbackEvent {
  event_id, idempotency_key,
  source: user|rater|critic|system,
  turn_id, span_id,
  model_version, product,
  type: thumb|pairwise|critique|tag,
  payload, trust_context,
  ts
}
```

#### 3.3.6 Sampling policy (tradeoff core)

| Signal | Sample rate |
|--------|-------------|
| Safety user report | 100% critic + human |
| Thumb down | 50% |
| Thumb up | 5% |
| Random explore | 1% |
| Low-trust accounts | Downweight / quarantine |

#### 3.3.7 Pair building

- Prefer same prompt, two responses (A/B).  
- Include constitution_id, rater_id, agreement metrics.  
- Soft labels from critic optional as features — **don’t silently override humans** without experiment flags.

#### 3.3.8 Promotion gate

```text
Bundle Manifest {id, stats, constitution_id, model_versions, checksums}
Eval Report {toxicity, agreement, sycophancy probes, contamination checks}
CAS: approved_bundles.add(manifest_id) only if eval pass + human signoff
Train jobs must present approved manifest id
```

#### 3.3.9 Trade-offs

| Topic | Options | Choice |
|-------|---------|--------|
| Sync critic on user path | Sync vs async | Async default; sync admin |
| Store full transcripts | Full vs pointer | Snapshot immutable span at feedback |
| Critic as label vs assist | Replace human vs assist | Assist + sample human gold |
| Auto-train | Closed loop vs gated | **Gated** MVP |
| Aggregation | Simple counts vs Bradley-Terry | Start simple; BT offline |

---

### 3.4 Architecture Diagram

#### 3.4.1 Overview

```text
+----------+    +---------------+    +------------------+
| Clients  |--->| Ingest API    |--->| Event Log (Kafka)|
| Raters   |    | + Idempotency |    | + OLTP index     |
+----------+    +-------+-------+    +--------+---------+
                        |                     |
                        v                     v
               +----------------+     +-------+---------+
               | Span Snapshot  |     | Sampler         |
               | Store          |     +--------+--------+
               +----------------+              |
                        ^                      v
                        |              +-------+---------+
               +--------+--------+     | Critic Workers  |
               | Constitution    |<----| (InferGW)       |
               | Registry        |     +--------+--------+
               +--------+--------+              |
                        |                      v
                        |              +--------+--------+
                        +------------->| Rater Tasks     |
                                       +--------+--------+
                                                |
                                                v
                                       +--------+--------+
                                       | Dataset Builder |
                                       +--------+--------+
                                                |
                                                v
                                       +--------+--------+
                                       | Eval Gate +     |
                                       | Promotion CAS   |
                                       +--------+--------+
                                                |
                                                v
                                       Training Lake Consumers
```

#### 3.4.2 Sequence: thumb-down → pair → promote

```text
User → Ingest: thumb_down(turn=T)
Ingest → Log: durable ACK
Sampler → CriticQueue: job
Critic → Constitution v7 → scores principles
Builder → maybe create pairwise task vs alternative response
Rater → prefers A
Builder → bundle B42
Eval → pass
Human → approve B42
Train → pulls B42 only (CAS checked)
```

#### 3.4.3 Abuse path

```text
Many accounts thumb_down competitor outputs
Trust: correlated graph / velocity → quarantine
Sampler: downweight
Admin: review campaign
Bundle stats: show source entropy; eval fails if contaminated
```

---

### 3.5 Design Deep Dive

#### 3.5.1 Reliability invariants

1. **ACK ⇒ event durable** in log + queryable index.  
2. **Idempotency-Key** unique per producer feedback.  
3. **Span snapshot immutable** for lineage.  
4. **Constitution pin** on critic/rater tasks.  
5. **No train consume without approved manifest.**  
6. **Critic failure does not lose ingest.**  
7. **Promotion is CAS-audited.**  
8. **PII redaction applied before export** per policy.  
9. **Low-trust feedback cannot alone flip aggregates** (thresholds).  
10. **Kill switch** stops critic spend / rater assignment / promotes.

Failures:

| Failure | Behavior |
|---------|----------|
| Kafka blip | Producer retry; idempotent | 
| Critic backlog | Sample tighter; priority safety first |
| Rater fraud | Drop rater; invalidate tasks |
| Manifest checksum mismatch | Reject export |
| Constitution registry down | Pause new critic; ingest continues |

#### 3.5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | API + Kafka + workers + PG + object store |
| 10× | Partition by product; critic autoscaling; rater sharding |
| 100× | Tenant/product cells; tiered critic (small filter → large) |
| 1,000× | Federated lakes; active learning sampler; vendor rater mesh |

**Active learning:** critic uncertainty / disagreement sampling beats random at 100× cost.

#### 3.5.3 Maintainability

- Constitution PR review (docs as code).  
- Critic prompt versions alongside constitution.  
- Replay scoring when principles change (explicit regrade jobs).  
- Metrics: `ingest_qps`, `critic_lag`, `rater_agreement`, `bundle_reject_rate`, `$/bundle`, `abuse_quarantine`.  

#### 3.5.4 Safety of the loop itself

Ironic risk: feedback loop optimizes sycophancy or gaming.

Controls:

- Gold probes in rater stream.  
- Diversity constraints on bundle sources.  
- Holdout evals not optimized directly each day.  
- Human review for constitution changes.  
- Separate **safety-critical** principles with higher human rates.

#### 3.5.5 Privacy

- Snapshot minimization; encrypt at rest.  
- Export classifications: raw / redacted / synthetic.  
- Retention: feedback metadata longer than raw transcripts possible.

#### 3.5.6 Cost / GPU

- Critic is the GPU hog — sampling + small model prefilter.  
- Batch critic requests where latency allows.  
- Cache constitution embeddings / rubric prefixes.

#### 3.5.7 Consistency

- Ingest: at-least-once + idempotent.  
- Bundle publish: atomic manifest last.  
- Analytics dashboards: eventual.

#### 3.5.8 API sketch

```text
POST /v1/feedback
GET  /v1/feedback/{event_id}
POST /v1/constitutions
GET  /v1/constitutions/{id}
POST /v1/rater/tasks/next
POST /v1/rater/tasks/{id}/submit
POST /v1/bundles/build
POST /v1/bundles/{id}/eval
POST /v1/bundles/{id}/promote
GET  /v1/bundles/{id}/manifest
```

---

### 3.6 Wrap-Up (worked example)

**Designed:** a gated Constitutional AI feedback loop — durable ingest, versioned constitution, sampled AI critic, human preferences, lineage-rich bundles, eval + CAS promotion — optimized for practical continuous improvement without unsafe closed-loop weight writes.

**Defend:**

1. Online ingest ≠ online train.  
2. Sampling as architecture.  
3. Constitution pinning.  
4. Snapshots for lineage.  
5. Promote CAS gate.  
6. Abuse / trust weighting.  
7. Critic assist ≠ replace gold.  
8. Kill switches on spend and promote.  
9. Active learning at scale.  
10. Safety of the optimizer itself.

**Risks:** rater burnout; constitution vagueness; distribution shift; sycophancy attractors.

---

### 3.7 Deeper Questions (worked example)

1. How do you prevent the critic from merely parroting user thumbs?  
2. Bradley-Terry vs direct preference regression — when?  
3. Cross-lingual constitution application?  
4. Can product experiment toggles contaminate bundles?  
5. Design regrade after constitution v7→v8.  
6. Multi-tenant enterprise feedback isolation.  
7. Detecting preference privacy leakage in exports.  
8. SLOs for “loop health” weekly review.

---

## 4. Alternate Novel Prompts (Drill Pack)

*Practice the playbook. Each subsection is a seed — expand in mocks using §2.*

### 4.1 Long-Context Document Understanding API

**One-liner:** API that answers questions / extracts structured fields over 100k–1M+ token corpora with cost and citation constraints.

**Clarify spikes:** sync vs async jobs; citation mandatory?; update docs frequency; multi-doc; tenant isolation.

**Estimate spikes:** chunking 1k–2k tokens; index size; retrieval k; expand-to-full-read rate; GPU for map-reduce summarize.

**HLD skeleton:**

```text
Upload → Parse → Chunk → Embed/Index → Query Planner
  → Retrieve → (optional) Map LLM → Reduce LLM → Cite → Answer
Async job store for heavy docs; cache doc digests
```

**Invariants:** answer spans cite chunk ids; tenant ACL on retrieval; budget tokens/request; poison doc quarantine.

**Scale jumps:** hierarchical indices; doc cells; precompute summaries; speculative caching.

**Anthropic angles:** correctness of citations; cost; prompt injection via documents.

### 4.2 Real-Time Safety Classification Sidecar

**One-liner:** Sidecar that scores streaming tokens / tool calls with hard deadlines and fail-closed policies.

**Clarify spikes:** max added latency; categories; stream vs buffered windows; action on hit (block, redact, pause).

**Estimate spikes:** classifications/s; small model tok/s; GPU vs CPU classifiers; false positive cost.

**HLD skeleton:**

```text
Infer worker → token buffer (n tokens / m ms)
  → Sidecar Classify RPC (deadline)
  → Policy: allow | hold | redact | abort
  → Client stream
Fallback: if sidecar timeout → fail-closed for high-risk categories
```

**Invariants:** never emit blocked span; ordered tokens; deadline budgets; audit decisions.

**Scale jumps:** batch classify across streams; tiered models; regional sidecars; shadow mode.

**Anthropic angles:** safety vs TTFT; fail-closed; evaluation of classifier drift.

### 4.3 Other prompts to self-drill

| Prompt | Pattern anchor |
|--------|----------------|
| Eval-at-scale harness for model candidates | Job scheduler + dataset versioning + statistical tests |
| Tool-use permission broker | Policy engine + approvals (see agentic doc) |
| Memory service for assistants | Explicit write, retrieval ACL, forgetting |
| Red-team continuous scanner | Task generator + sandboxed targets + finding triage |
| Preference UI for constitution edits | Docs-as-code + review workflow + impact simulation |

For each: write F/NFR/Cases/Scales in 10 minutes; HLD in 10; one deep dive.

---

## 5. Wrap-Up: Transferable Patterns

### 5.1 Patterns that recur in Anthropic novel prompts

1. **Split online serving from offline learning.**  
2. **Version everything** (model, prompt, constitution, dataset).  
3. **Fail closed on safety-critical paths.**  
4. **Admission control / sampling for cost.**  
5. **Lineage & audit for trust.**  
6. **Idempotent ingest.**  
7. **Gates before prod side effects.**  
8. **Cells / shards at 100×.**  
9. **Human-in-loop where automation is risky.**  
10. **Measure goodput, not vanity GPU %.**

### 5.2 How to reuse this worked example

If the novel prompt is about **feedback, eval, critics, constitutions, RLHF/RLAIF** — lift §3 heavily.  
If it’s about **streaming safety** — lift §4.2.  
If it’s about **long documents** — lift §4.1.  
If it’s about **agents** — use sibling adaptive-agentic doc.  
If it’s about **weights/rollouts** — use distribution docs.

### 5.3 One-minute closer (meta)

> For novel Anthropic designs I clarify the atomic unit and safety fail mode first, split online vs offline planes, do token/GPU math with sampling/admission, then pin versions and promotion gates so the clever AI loop can’t silently corrupt production.

---

## 6. Deeper / Related Interview Questions

### 6.1 Meta / process

1. Interviewer refuses to give scale numbers — what do you do?  
2. They change the product mid-interview — how do you adapt the design?  
3. When do you push back on scope?  
4. How do you show seniority without overbuilding?

### 6.2 Cross-cutting technical

5. Compare fail-open vs fail-closed for three subsystems.  
6. Design an idempotent ingest for mobile flaky networks.  
7. How do you keep metric cardinality sane?  
8. Multi-region active-active for feedback ingest — conflicts?

### 6.3 Safety

9. Document injection vs user injection — unified framework?  
10. Can feedback loops amplify bias? Mitigations?  
11. Sidecar classifier disagreeing with post-hoc moderator — arbitration?

### 6.4 EM flavor

12. Novel project; junior proposes end-to-end auto-train to prod — coaching?  
13. Prioritize critic accuracy vs rater throughput for one quarter.  
14. Scorecard for a “novel LLM system” team.

### 6.5 Sample answers (brief)

**Q1:** State assumptions explicitly in a table; design so components scale with the assumed knobs; ask which knob they care to stress.

**Q12:** Affirm the closed-loop ambition; require promotion gates, eval harness, audit; assign a milestone that ships gated exports before any auto-promote discussion.

---

## Appendix A: Clarify worksheet (print / memorize)

```text
Users:
Atomic unit:
Sync/Async/Stream:
MVP:
Out:
NFR latency/avail/safety:
Failure cases:
Abuse cases:
Baseline scale:
Assumptions:
```

## Appendix B: Estimate worksheet

```text
QPS:
Tokens in/out:
GPU tok/s assumption:
GPUs:
Storage/day:
Queue produce vs consume:
Cost driver #1:
```

## Appendix C: Tradeoff pair library

| A | B | When A | When B |
|---|---|--------|--------|
| Sync | Async | UX needs | Cost/throughput |
| Exact | Sampled | Safety critical | Cheap telemetry |
| Fail-open | Fail-closed | Availability UX | Harm prevention |
| Monolith | Split planes | MVP speed | Scale/safety |
| Human | Model critic | Gold quality | Coverage/cost |

## Appendix D: Full worked example — constitution snippet

```text
Principle P1: Do not provide actionable cyber weaponization detail.
Principle P2: Prefer truthfulness over user-pleasing falsehoods.
Principle P3: Respect privacy; minimize unnecessary personal data.
```

Critic returns `{principle_id, verdict, severity, evidence_span}`.

## Appendix E: Bundle manifest example

```json
{
  "bundle_id": "prefs_2026_08_05",
  "constitution_id": "c_v7",
  "pair_count": 180000,
  "checksum": "blake3:...",
  "source_entropy": 0.82,
  "eval_report_id": "er_123",
  "approved": true,
  "approved_by": "prefs-oncall"
}
```

## Appendix F: Sampler pseudo

```text
on event e:
  score = priority(e.type, e.safety_tags, e.trust)
  if score > T_safety: enqueue_critic(e); maybe_rater(e)
  elif random() < p(score): enqueue_critic(e)
  else: store_only(e)
```

## Appendix G: Promotion CAS SQL

```sql
UPDATE bundle_approvals
SET approved=true, approved_by=$user, approved_at=now()
WHERE bundle_id=$id AND eval_passed=true AND approved=false;
```

Train admission:

```sql
SELECT 1 FROM bundle_approvals WHERE bundle_id=$id AND approved=true;
```

## Appendix H: Drill timer script (30 min mock)

| Min | Action |
|-----|--------|
| 0–2 | Restate prompt |
| 2–10 | Clarify + MVP |
| 10–15 | Estimates |
| 15–22 | HLD + diagram |
| 22–28 | Deep dive safety/scale |
| 28–30 | Wrap decisions |

## Appendix I: Mapping novel prompt → sibling docs

| If prompt mentions | Open |
|--------------------|------|
| Weight fanout | model-weight-distribution |
| Regional model pointers | file-model-distribution-service |
| Batching bugs / EM review | flawed-inference-batching-review |
| Tools / agents | adaptive-agentic-system |
| Unknown | this playbook |

## Appendix J: Long-context API — extra estimates

- 500-page PDF ≈ 250k tokens raw.  
- Chunk 1k with 200 overlap → ~300 chunks.  
- Embed 300 × 1k dims × 4 B ≈ fine.  
- Query: retrieve 20 chunks → 20k tokens context + answer — budget check.  
- Map-reduce for “summarize all”: cost ∝ chunks; async job.

## Appendix K: Safety sidecar — deadline math

- Token stream 50 tok/s; classify every 20 tokens ⇒ every 400ms.  
- RPC budget 50ms p99; hold back emit by window.  
- If classify p99 80ms > budget → fail-closed pause or dual-path policy by category.

## Appendix L: Interviewer push kit

| Push | Response pattern |
|------|------------------|
| “Skip estimates” | Give 3 numbers anyway — volume, GPU, storage |
| “Just use a bigger model” | Cost + latency + fail mode |
| “Make it fully autonomous” | Gate; propose phase 2 |
| “Draw more boxes” | Pause; deepen one critical path |

## Appendix M: Scorecard for self-review after mock

- [ ] Restated problem  
- [ ] MVP bounded  
- [ ] Assumptions labeled  
- [ ] Estimates with units  
- [ ] Tradeoff table  
- [ ] Safety fail mode  
- [ ] 10×/100×/1,000×  
- [ ] Invariants ≥ 5  
- [ ] Risks honest  

## Appendix N: Event log fields (feedback)

`event_id, ts, tenant_id, product, turn_id, model_version, constitution_id_used, type, payload_ref, trust_score, sample_decision, critic_job_id`

## Appendix O: Rater quality controls

- Gold tasks 5–10%.  
- Inter-rater agreement dashboards.  
- Speed caps (too fast → bot).  
- Training onboarding quiz.  
- Blind vs model version when needed.

## Appendix P: Why “practical” is in the title

Interviewers want systems that could ship: **budgets, gates, abuse, operability** — not only a glamorous diagram of “AI improves itself.”

## Appendix Q: Constitutional loop threat model

| Threat | Mitigation |
|--------|------------|
| Ballot stuffing | Trust, velocity, graph |
| Critic hacking via inputs | Treat as model; sandbox prompts |
| Contaminated bundles | Entropy + eval |
| Insider constitution sabotage | Dual control edits |
| Auto-promote bug | CAS + two-party |

## Appendix R: Progressive feature unlock

| Scale | Unlock |
|-------|--------|
| MVP | Ingest, critic sample, raters, gated export |
| 10× | Active learning; multi-product |
| 100× | Tiered critics; cells |
| 1,000× | Federated; semi-auto promote with strong eval |

## Appendix S: Worked narrative (90 seconds)

> I’d build a feedback loop service with a hard gate. Ingest thumbs and critiques durably, snapshot the span, pin a constitution version, and asynchronously run a sampled AI critic for coverage while humans label pairwise gold. Dataset builder emits immutable bundles with manifests; eval harness + human CAS promotion are required before any training job can read them. That keeps the loop practical and prevents noisy or adversarial feedback from silently steering prod. At scale I’d spend most engineering on sampling, abuse resistance, and critic cost—not on removing the gate.

## Appendix T: First-principles checklist (any novel system)

1. Interfaces  
2. Atomic unit  
3. Sync boundary  
4. Durable log?  
5. GPU vs IO  
6. Safety fail mode  
7. Tenancy  
8. Version pins  
9. Admission/sampling  
10. Scale jump story  

## Appendix U: Common Anthropic keywords → design modules

| Keyword | Module |
|---------|--------|
| Constitution | Versioned policy pack |
| Critique | LLM worker + schema |
| Preference | Pair store + raters |
| Sidecar | Deadline RPC + buffer |
| Long context | Chunk/index/map-reduce |
| Tool | Policy + sandbox |
| Eval | Harness + gates |
| Rollout | Channel CAS / canary |

## Appendix V: Storage layout suggestion (worked example)

- Kafka topic `feedback_events`  
- PG `feedback_index`, `constitutions`, `bundles`, `approvals`  
- Object store `spans/{span_id}.json`, `bundles/{id}/*.parquet`  
- Redis sampler counters / rate limits  

## Appendix W: Metrics that impress

- `% feedback with lineage complete`  
- `critic_lag_p95`  
- `$ per approved pair`  
- `bundle_reject_rate`  
- `abuse_quarantine_rate`  
- `post-train eval delta` (partner metric)

## Appendix X: Closing meta-advice

Novelty is a **presentation of fundamentals**. If you clarify ruthlessly, estimate honestly, split planes, and bind safety/cost invariants, you can design systems you have never shipped — which is exactly the skill Anthropic is testing.

---

## Appendix Y: Mini worked outline — Document Understanding API (condensed full arc)

**Clarify:** Async jobs for >X pages; citations required; tenant ACL; PII redaction; QPS 20 baseline.

**Estimate:** 10k docs/day × 100 chunks embed; 50 QPS retrieve; map-reduce on 5% queries.

**HLD:** upload→parse→chunk→index; query→retrieve→LLM→cite; job worker; cache.

**Deep dive:** injection via docs; ACL in retriever; cost caps; re-index versions.

**Wrap:** citations + ACL + budgets as invariants.

## Appendix Z: Mini worked outline — Safety Sidecar (condensed full arc)

**Clarify:** p99 +30ms budget; categories; fail-closed on C1/C2; stream hold window 16–32 tokens.

**Estimate:** 200k streams; classify 100k windows/s → fleet of small models / rules hybrid.

**HLD:** buffer→classify→policy→release; shadow mode; audit.

**Deep dive:** timeout policy; dual classifiers; training feedback loop to critic data (careful).

**Wrap:** deadlines + fail-closed + ordered emit.

---

*End of Novel Practical LLM System playbook + worked example.*
