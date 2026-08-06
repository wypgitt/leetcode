# System Design: High-Volume Regional AI / Copilot Prompts

> **Focus areas:** Regional Copilot prompt ingress · GPU/inference capacity · Admission & fairness · Data residency · Entra authZ · Streaming · Tenant isolation · Graceful degradation  
> **Style:** End-to-end Azure/M365 Copilot plane design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split control-plane vs GPU-time vs stream fan-out; residency as hard invariant; deal-breakers explicit  
> **Interview theme:** Microsoft / Azure — **regional Copilot prompt handling** under scarce accelerator capacity

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

Goal: design the **regional plane** that accepts Copilot / Azure OpenAI–style prompts from Microsoft 365, GitHub Copilot, Azure AI, and first-party surfaces; admits them fairly against **scarce GPU capacity**; streams tokens; and never violates **data residency**, **Entra identity**, or tenant isolation—even under overload.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Regional prompt admit → route → infer → stream → meter | Training / foundation-model research cluster |
| Geography | Azure region (or geo) as capacity + residency cell | “Just put everything in one global region” |
| Product surfaces | Copilot in M365, VS/VS Code, Azure AI apps | Full Teams chat product (sibling themes only) |
| Identity | Entra ID tenants, Conditional Access, app consents | Anonymous public ChatGPT free tier |
| Compliance | Data residency, Purview hooks, customer Lockbox-ish | Full HIPAA health product (see health doc) |

**Scope statement:** Design a **regional Copilot prompt platform**—not a single chatbot UI and not a training scheduler.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Who sends prompts? | M365 Copilot, GitHub Copilot, Azure AI apps, first-party agents | Multi-surface API + product BFFs |
| F2 | Auth? | Entra ID user + app; tenant + object id; Conditional Access | Token validation at edge; claims → policy |
| F3 | Streaming? | Yes — SSE / chunked HTTP; some WS for IDE | Stream gateways regional |
| F4 | Models? | Multi-SKU: GPT-class, embeddings, small/fast, reasoning | Model catalog + GPU pools per SKU |
| F5 | Tools / grounding? | Graph, search, plugins, RAG corpora | Tool bus after admit; residency-bound retrieval |
| F6 | Tenancy? | Hard isolation by Entra tenant; some sovereign clouds | Tenant as isolation key everywhere |
| F7 | Quotas? | Per-tenant / per-user / per-SKU RPM + TPM | Reserve/settle credits |
| F8 | Priority? | Interactive Copilot > batch eval > best-effort | Priority bands + preemption of batch |
| F9 | Residency? | Prompt + context + completions stay in geo/region | Regional cell; no silent cross-geo spill |
| F10 | Audit? | Admin audit of Copilot usage (opt-in / policy) | Purview / audit pipeline; redaction |
| F11 | Abuse? | Prompt injection, data exfil via tools, jailbreaks | Safety + DLP + tool allowlists |
| F12 | Offline / degraded? | Partial Copilot with lighter models | Explicit degradation UX |

**MVP functional scope (lock with interviewer):**

1. Authenticated prompt submit (Entra) with tenant + user + app identity.  
2. **Regional admission control**: RPM/TPM + GPU concurrency leases.  
3. Model routing across regional SKU pools with capacity signals.  
4. **Token streaming** to clients with TTFT SLO.  
5. Soft reservation + settle for tokens / GPU-seconds.  
6. Grounding stubs: Microsoft Graph / search within residency boundary.  
7. Safety / DLP hooks on input and output.  
8. Tenant admin policies: allowed models, logging, geographic pin.  
9. Observability: queue wait, GPU util, residency violations = P0.  
10. Graceful overload: queue with deadline, shed batch, downgrade model **with notice**.

**Out of MVP (explicitly defer):**

- Perfect global GPU arbitrage that ignores residency  
- Full plugin marketplace review pipeline  
- On-device small models as primary (hooks only)  
- Multi-agent orchestration product completeness  
- Customer-managed keys deep dive (mention Azure Key Vault hooks)

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | TTFT (interactive) | p50 < 400ms, p99 < 2s excluding reasoning queues |
| N2 | Stream smoothness | Flush ≤ 50–100ms once tokens flow |
| N3 | Admission decision | p99 < 50ms when not queued |
| N4 | Availability | 99.9% regional control plane; degrade models before hard 503 |
| N5 | Residency | **0** silent cross-geo prompt/completion spills |
| N6 | Isolation | No cross-tenant data in prompts, caches, or logs by default |
| N7 | Durability of audit | Policy-required prompts retained per admin config |
| N8 | Fairness | Noisy tenant cannot starve others in same region |
| N9 | Failover | Pair-region DR only when **policy allows**; else fail closed |
| N10 | Compliance | Support EU Data Boundary / sovereign cloud variants |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Outlook Copilot summarize → Entra token → regional admit → Graph grounding → stream summary.  
2. VS Code Copilot completion → low-latency small model pool → partial stream.  
3. Azure AI app batch embeddings → separate queue, lower priority, high throughput.  
4. Tenant hits soft TPM → fair queue; interactive still preferred over batch.  
5. Region GPU brownout → route to **allowed** in-geo secondary region or lighter SKU + banner.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit same Idempotency-Key | One run; replay stream/status |
| Entra token expired mid-stream | Finish current run if already admitted; reject new |
| Tenant geo-pin = West Europe only | Never spill to East US even if GPUs idle |
| Reasoning model backlog | Interactive may choose fast model or wait with ETA |
| Prompt injection via email body | Treat retrieved content as untrusted; tool allowlist |
| Tool tries to call external HTTP | Egress policy + tenant DLP |
| GPU node death mid-generation | Incomplete run; client retry; no double-bill settle bug |
| Audit store down | Fail closed if tenant requires logging; else degrade with flag |
| Capacity stampede (9am local) | Pre-warm pools; priority queues; shed batch first |
| Sovereign cloud tenant | Separate stamp; no commercial region fallback |

### 1.4 Scales (Progressive)

| Metric | Baseline (1 region) | 10× | 100× | 1,000× |
|--------|---------------------|-----|------|--------|
| Interactive prompts / day | 50M | 500M | 5B | 50B |
| Peak admit QPS | 5K | 50K | 500K | 5M |
| Peak concurrent streams | 100K | 1M | 10M | 100M |
| Peak output tokens/s | 1M | 10M | 100M | 1B |
| GPU inventory (H100-class equiv) | 2K | 20K | 200K | 2M |
| Entra tenants active / region | 50K | 500K | 5M | global cells |
| Grounding calls / s | 2K | 20K | 200K | 2M |
| Audit events / day | 20M | 200M | 2B | retention-tiered |

**What each jump forces:**

- **10×:** Dedicated stream gateways; per-SKU GPU schedulers; Redis quota plane; Graph caching with ACL.  
- **100×:** Tenant home cells inside region; hierarchical admission; batch/interactive hard isolation; Purview scale-out.  
- **1,000×:** Multi-region geo fabric with residency compilers; capacity forecasting; sovereign stamps; global control plane for **metadata only**.

### 1.5 Etc. (Constraints & Assumptions)

- Inference is served by **Azure AI / internal model hosting**; this design owns admit, route, stream, meter, policy.  
- **Entra** is source of identity truth; Conditional Access may block Copilot entirely.  
- Data residency is a **product promise**, not a best-effort optimization.  
- GPU capacity is the scarce resource; HTTP servers are not.  
- Pair with sibling docs: Azure regional failover; health app for PHI; IDE for editor-side Copilot UX.

**Scope statement to repeat back:**

> Design a regional Copilot prompt platform: Entra-authenticated multi-surface ingress, residency-bound admission against GPU pools, model routing, streaming, grounding stubs, safety/DLP, tenant quotas, and graceful degradation—scaled 10×/100×/1,000× without silent cross-geo spill or cross-tenant leakage.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Admit / policy** | AuthZ + quota + route | ~5K/s | ~50K/s | Control plane |
| **GPU decode** | Output tokens/s | ~1M | ~10M | Inference |
| **Stream frames** | SSE events to clients | ~50K/s | ~500K/s | Gateway |
| **Grounding** | Graph/search | ~2K/s | ~20K/s | Data plane |
| **Audit / metering** | Async events | ~5K/s | ~50K/s | Bus |
| **Safety classify** | Input/output | ~turns × k | ×10 | Safety fleet |

**Anti-pattern:** one “QPS” mixing Entra validate, GPU tokens, and SSE fan-out.

### 2.2 Token & GPU math

```text
Peak output tokens/s ≈ 1M (baseline interview number)
Avg decode ≈ 50 tok/s/stream ⇒ concurrent decode streams ≈ 1M/50 = 20K
  (other streams may be TTFT-waiting or tool-blocked)

If 1×H100-class serves ~R tok/s continuous for a SKU:
  GPUs_needed ≈ peak_tok_s / R_eff
Use interviewer-given R; defend utilization 60–80% allocated.

Interactive vs batch: reserve GPU fraction G_int (e.g. 70%) so batch cannot melt Copilot Monday morning.
```

### 2.3 Stream gateway memory

```text
100K concurrent streams × 64 KB state ≈ 6.4 GB fleet-wide (order)
At 10×: ~64 GB → dedicated stream tier, not app servers
```

### 2.4 Quota / Redis ops

```text
Per admit: ~3–8 Redis ops (RPM, TPM reserve, concurrency lease)
5K admits/s × 5 ≈ 25K Redis ops/s baseline → cluster; not single node
```

### 2.5 Storage (audit / prompt store)

```text
If 10% tenants enable prompt logging:
  5M prompts/day logged × 4 KB ≈ 20 GB/day/region raw
  Hot 30d ≈ 0.6 TB; warm/cool tier thereafter
Never put full prompts in shared global analytics without residency tags.
```

### 2.6 Grounding amplification

```text
Copilot turn may do 1–5 Graph calls
Peak Graph QPS ≈ admit_QPS × avg_tools
Cache with tenant-scoped keys; ACL re-check on hit
```

### 2.7 Cost intuition (interview signal)

```text
Dominant cost: GPU-seconds, then grounding, then stream egress
Optimize: prompt cache (tenant-safe), speculative decoding, small models for complete/complete-ish,
shed batch, shorten max_tokens under overload — not “add more app pods”
```

### 2.8 Latency budget (interactive)

```text
Edge pop → regional front door: 5–40ms (geo)
Entra validate (cached keys): 1–5ms
Admit + route: 5–20ms
Queue wait: 0–seconds (SLO separate)
Model TTFT: 100–800ms typical
Total TTFT ≈ network + admit + queue + model
```

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency / notes |
|-------|----------------|---------------------|
| Identity / Policy | Entra, Conditional Access, tenant Copilot settings | Strong authN; policy cache TTL |
| Admission / Quota | RPM, TPM, concurrency leases | Atomic reserve; fail closed |
| Routing / Capacity | SKU pools, health, residency compiler | Soft state OK; stale = safer reject |
| Inference | GPU workers, KV cache, batching | Lease fenced per run |
| Stream | Client fan-out | Best-effort frames; durable status separate |
| Grounding | Graph/search/plugins | Tenant ACL on every call |
| Audit / Meter | Usage, optional prompts | Async; residency-tagged |
| Safety / DLP | Classifiers, Purview hooks | Fail closed on high-risk categories |

**Deal-breaker:** treating residency as a routing *preference* instead of a **compiler constraint**.

### 3.2 Domain model

```text
EntraTenant
  ├── CopilotPolicy (geo_pin, allowed_models, audit_mode, dlp_mode)
  ├── Quotas (RPM/TPM/concurrency per SKU class)
  └── Users / Apps / Groups (Entra)

PromptRun
  ├── identity: tenant_id, user_oid, app_id, client_surface
  ├── residency: geo, region_cell
  ├── request: messages/parts, tools, max_tokens, model_pref
  ├── routing: resolved_model, pool_id, degradation_flags
  ├── status: created|admitted|queued|running|completed|failed|cancelled|refused
  ├── leases: quota_lease_id, gpu_lease_id
  ├── usage: prompt_tokens, completion_tokens, grounding_calls
  └── safety_outcome / dlp_outcome
```

**Run state machine:**

```text
created → admitted → queued → running
                              ├→ completed
                              ├→ incomplete
                              ├→ failed
                              ├→ cancelled
                              └→ refused
```

CAS single terminal transition; settle quotas on terminal.

### 3.3 API shape (regional)

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/copilot/runs` | Create + optionally stream |
| GET | `/v1/copilot/runs/{id}` | Status + usage |
| GET | `/v1/copilot/runs/{id}/events?after=` | Resume stream |
| POST | `/v1/copilot/runs/{id}/cancel` | Cancel |
| GET | `/v1/capacity/sku` | Internal capacity signals |
| GET | `/v1/admin/policy` | Tenant policy (admin) |

```http
POST /v1/copilot/runs
Authorization: Bearer <Entra access token>
Idempotency-Key: ...
x-ms-client-request-id: ...
{
  "surface": "m365_outlook",
  "model": "auto",
  "stream": true,
  "max_tokens": 2048,
  "messages": [{"role":"user","content":[{"type":"text","text":"Summarize..."}]}],
  "tools": {"graph": true, "web": false},
  "grounding": {"message_id": "...", "mailbox": "..."},
  "policy_context": {"sensitivity_label": optional}
}
```

### 3.4 HLD options

#### Option A — Global anycast → single mega region

| Pros | Cons |
|------|------|
| Simple capacity pooling | **Breaks residency**; latency; blast radius |

**Deal-breaker** for enterprise Copilot with geo promises.

#### Option B — Regional cells, hard pin (chosen MVP)

| Pros | Cons |
|------|------|
| Residency natural; blast radius limited; Entra CA matches region | GPU stranded per region; need capacity planning |

**Choice:** **Option B** with explicit **in-geo** secondary only when policy allows.

#### Option C — Geo fabric with residency compiler + soft spill

| Pros | Cons |
|------|------|
| Better utilization within legal geo | Complex; easy to mis-implement spill |

**Phase 2** inside EU / US geos—not cross-sovereign.

### 3.5 Admission & fairness

```text
Admit pipeline:
  1. Validate Entra token (issuer, aud, tid, oid, scp/roles)
  2. Load tenant CopilotPolicy (geo_pin, model allowlist)
  3. Residency compile → candidate region cells
  4. Safety/DLP pre-check (cheap)
  5. Quota reserve (RPM/TPM/concurrency)
  6. Priority queue enqueue OR immediate GPU lease
  7. Dispatch to model pool
```

| Strategy | Pros | Cons |
|----------|------|------|
| Pure FIFO | Simple | Noisy neighbor |
| Weighted fair per tenant | Fair | Starvation if weights wrong |
| **Hierarchical: surface class → tenant WFQ → user** (chosen) | Protects interactive | More knobs |
| Credits only | Good for Azure AI $ | Weak for M365 seat fairness |

**Interactive protection:** separate GPU pools or reserved watermark for Copilot interactive vs Azure AI batch.

### 3.6 Model routing

```text
Router inputs:
  surface SLA class, user/tenant preference, prompt features,
  allowed_models, capacity, latency SLO, degradation policy

Router outputs:
  model_version, pool, max_tokens cap, degradation_notice?
```

| Strategy | When |
|----------|------|
| Pin exact deployment | Regulated / eval reproducibility |
| Auto within allowlist | Default Copilot |
| Cascade fallback | Overload — **must notify** |

**Deal-breaker:** answering with a weaker model while UI still shows “GPT-4-class” with no notice.

### 3.7 Streaming ownership

| | **Option A — Coupled gateway** | **Option B — Run worker + replay** |
|---|--------------------------------|-------------------------------------|
| Complexity | Lower | Higher |
| Resume | Retry | `after_sequence` |
| MVP | **A** | Phase 2 for IDE long runs |

### 3.8 Grounding / tools

```text
Model --tool_call--> Tool Orchestrator (regional)
  ├── Microsoft Graph (mailbox/files) with delegated token OBO
  ├── Cognitive Search / index (tenant-partitioned)
  └── Plugin / webhook (egress allowlist + DLP)
Persist tool_call/tool_result in run timeline for audit/replay
```

**Invariants:**

- On-behalf-of (OBO) token exchange; never use a super-user Graph app for user mail by default.  
- Retrieved content marked `untrusted_context` for prompt assembly.  
- Tool loop caps; timeout; size limits.  
- Egress cannot hit link-local / IMDS / cross-tenant resources.

### 3.9 Safety, DLP, Purview

```text
Input → classifiers / DLP → (allow | refuse | redact)
Assemble: system layers + user + grounding(untrusted)
Stream → chunk policy → final classifiers
Optional: store prompt/response per tenant audit mode
```

| Mode | Behavior |
|------|----------|
| Audit off | Metadata/metrics only |
| Audit metadata | Tokens, model, user, timestamp |
| Audit content | Full prompt/response encrypted, residency-bound |

### 3.10 Capacity & GPU pools

```text
Region
  └── SKU Pool (e.g. chat-large, chat-small, embed, reason)
        ├── Interactive reserved watermark
        ├── Elastic shared
        └── Batch preemptible
```

Leases with heartbeat; preemption of batch under interactive pressure; never partial-gang for multi-GPU reasoning if required all-or-nothing.

### 3.11 Component trade-offs

| Component | Options | Choice |
|-----------|---------|--------|
| Front door | Azure Front Door / Traffic Manager | AFD → regional stamp |
| Quota store | Redis vs Cosmos | Redis for hot; Cosmos/PG for config |
| Run metadata | Cosmos / Postgres | Postgres/Cosmos per cell |
| Bus | Event Hubs / Kafka | Event Hubs for audit/meter |
| Secrets | Azure Key Vault | KV + managed identity |
| Identity | Entra | Mandatory |

---

## 4. Architecture Diagram

### 4.1 Regional overview

```text
[M365 / VS / Azure AI clients]
            |
            v
   +------------------+
   | Edge / AFD / POP |  (TLS, WAF, anycast)
   +--------+---------+
            |
            v
   +------------------+     +-------------------+
   | Regional Front   |---->| Entra token       |
   | Door / APIM      |     | validation (JWKS) |
   +--------+---------+     +-------------------+
            |
            v
   +------------------+     +-------------------+
   | Prompt API / BFF |---->| Policy Service    |
   | (runs, stream)   |     | (tenant geo/DLP)  |
   +--------+---------+     +-------------------+
            |
            v
   +------------------+     +-------------------+
   | Admission Ctrl   |---->| Redis quotas      |
   | (WFQ + leases)   |     | + concurrency     |
   +--------+---------+     +-------------------+
            |
            v
   +------------------+
   | Model Router     |
   +--------+---------+
            |
   +--------+---------+------------------+
   v                  v                  v
+----------+   +-------------+   +--------------+
| GPU Pool |   | GPU Pool    |   | Embed Pool   |
| chat-lg  |   | chat-small  |   |              |
+----+-----+   +------+------+   +------+-------+
     |                |                 |
     +--------+-------+---------+-------+
              v
     +----------------+     +------------------+
     | Stream Gateway |---->| Client SSE/WS    |
     +--------+-------+     +------------------+
              |
              v
     +----------------+     +------------------+
     | Tool Bus       |---->| Graph / Search   |
     | (OBO)          |     | (tenant ACL)     |
     +--------+-------+     +------------------+
              |
              v
     +----------------+     +------------------+
     | Safety / DLP   |---->| Purview / Audit  |
     +----------------+     | (residency cell) |
                            +------------------+
```

### 4.2 Residency compiler

```text
Tenant.geo_pin = "EU"
Surface region preference = "westeurope"
Capacity: westeurope=LOW, northeurope=OK, eastus=HIGH

Compiler:
  candidates = intersect(policy_allowed_regions, geo_EU)
  // eastus excluded even if HIGH
  pick northeurope (in-geo spill allowed by policy)
```

### 4.3 Admit sequence

```text
Client -> APIM -> Prompt API
  -> validate Entra
  -> policy
  -> residency compile
  -> reserve quota (Redis)
  -> enqueue / lease GPU
  -> start run
  -> stream tokens
  -> settle usage + audit event
```

### 4.4 Overload degradation

```text
Demand > Interactive watermark?
  -> preempt batch leases (grace)
  -> shorten max_tokens / prefer small model (notify)
  -> queue with deadline; else 503 + Retry-After
Never: unbounded queue holding GPUs forever
Never: spill to forbidden geo
```

### 4.5 Multi-region geo (Phase 2)

```text
                    +------------------+
                    | Global Directory |
                    | (tenant→geo only)|
                    +--------+---------+
                             |
           +-----------------+-----------------+
           v                 v                 v
      [US Geo cells]    [EU Geo cells]   [Sovereign]
      residency-bound   residency-bound  isolated stamp
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **No silent cross-geo spill** of prompt, grounding content, or completion.  
2. **No cross-tenant cache hits** without ACL re-validation.  
3. Quota reserve must not double-spend under retries (`Idempotency-Key` + lease id).  
4. GPU lease fenced by `lease_generation`; dead workers cannot keep generating billable tokens without heartbeat.  
5. Terminal run settles exactly once (sweeper for expired leases).  
6. If tenant requires audit logging, **fail closed** when audit pipeline is down.  
7. Tool OBO tokens scoped least-privilege; no broad app-only mail read by default.  
8. Degradation that changes model quality is **user/tenant visible**.  
9. Safety refusals are terminal successful *policy* outcomes, not silent truncations without status.  
10. Sovereign cloud tenants never fall back to commercial regions.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single regional stamp; APIM; Redis quotas; 2–3 SKU pools; SSE gateway |
| 10× | Stream tier; hierarchical WFQ; Graph cache; safety fleet; Event Hubs meter |
| 100× | Cells within region (tenant hash); per-SKU schedulers; batch isolation; Purview scale |
| 1,000× | Geo fabrics; capacity forecasting; speculative decode; on-device assist hooks; sovereign stamps |

### 5.3 Maintainability

- Model catalog as data (deployments, limits, cost weights).  
- Policy as versioned documents with canary tenants.  
- Router rules unit-tested with capacity fixtures.  
- Chaos: kill GPU node, Redis failover, Entra JWKS blip, audit outage.  
- Clear ownership: Capacity vs Copilot Product vs Safety vs Identity.

### 5.4 Progressive scale narrative

**1× — One Azure region, one stamp**  
All Copilot surfaces pin to `westeurope`. Postgres/Cosmos for runs; Redis quotas; two pools (large/small). Manual capacity sheets.

**10× — Workday stampede**  
9am CET spike. Interactive watermark saves Outlook Copilot; Azure AI batch preempted. Stream gateway fleets autoscaled on concurrent connections, not CPU of API pods alone.

**100× — Cellization**  
Tenant id → cell. Hot tenants isolated. Hierarchical admission. Grounding caches partitioned. Audit lake per cell with residency tags.

**1,000× — Geo compiler + forecasting**  
US/EU geos with in-geo spill. Predictive scale of GPU VMSS. Global directory stores only tenant→geo metadata. Product still explains when quality degrades.

### 5.5 Entra integration deep dive

```text
Access token claims used:
  tid, oid, appid/azp, scp/roles, idtyp, wids (optional),
  xms_cc / CAE critical events (optional continuous access)

APIM / middleware:
  - validate signature via Entra JWKS (cache)
  - audience check for Copilot APIs
  - map tid → TenantPolicy
  - Continuous Access Evaluation: revoke mid-session for high-risk

OBO for Graph:
  user token → OBO → Graph token
  cache OBO tokens carefully (user+tenant+scope keyed)
```

**Interview line:** Conditional Access can disable Copilot for a tenant; design must honor `blocked` policy as admit reject, not inference-time surprise.

### 5.6 GPU scheduling notes (inference, not training)

- Continuous batching / paged attention inside pool (implementation detail).  
- Control plane leases **concurrency slots** + estimated tokens, not MPI gangs (unless multi-GPU reasoning SKU needs gang).  
- Separate **prefill vs decode** capacity if interviewer goes deep.  
- Fragmentation less like training; still isolate noisy long-`max_tokens` jobs.

### 5.7 Caching without residency/tenant bugs

| Cache | Key must include | Risk if wrong |
|-------|------------------|---------------|
| Prompt prefix | tenant, model, hash, ACL epoch | Cross-tenant leak |
| Graph object | tenant, user, resource id, etag | IDOR |
| Policy | tenant, version | Stale allow |
| Embeddings | tenant, corpus version | Wrong grounding |

**Default:** prefer not to cache raw prompts globally; if semantic cache exists, make it **tenant-scoped** and policy-gated.

### 5.8 Fairness & noisy neighbors

```text
Tenant A: 10% of seats, 80% of prompts (abuse or heavy automation)
Controls:
  - per-user RPM
  - per-tenant fair share
  - automation detection → batch class
  - contract/SKU upgrades for legitimate heavy tenants
```

### 5.9 Failure modes & degradation matrix

| Failure | Action |
|---------|--------|
| GPU pool down | Failover in-geo pool; else degrade model; else 503 |
| Redis quota down | Fail closed admits (or static sealed limits if precomputed) |
| Entra JWKS down | Short cache continue; then fail closed new admits |
| Graph down | Tool-disabled answer path with notice |
| Safety fleet brownout | Fail closed high-risk; soft categories degrade carefully |
| Stream GW death | Incomplete; client retries (Option A) |
| Region AZ loss | Zone-redundant pools; stamp survives |
| Entire region loss | See failover doc; residency may force outage |

### 5.10 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Spill to US GPUs for EU tenant | Contract / regulatory breach |
| Shared prompt cache across tenants | Data leak SEV |
| Silent model downgrade | Trust destruction |
| Unbounded interactive queue | Meltdown of TTFT SLO |
| App-only Graph read of all mail | Overbroad access; compliance nightmare |
| Meter after client disconnect without fence | Billing disputes |
| Mix batch embeddings into interactive pool | Monday Copilot outage |
| Put full prompts in global telemetry | Residency + privacy incident |

### 5.11 Observability (must-have)

- Admit QPS, accept/reject/queue ratios by SKU and surface  
- Queue wait p50/p99 by priority class  
- TTFT / TPOT; GPU util; preemption rate  
- Residency compiler decisions + **forbidden spill attempts = P0 page**  
- Cross-tenant cache ACL fail counters  
- Entra auth failure taxonomy  
- Cost: GPU-seconds per tenant/surface  

### 5.12 Security checklist

- TLS everywhere; mTLS to inference if internal.  
- Key Vault for secrets; managed identities for Azure resources.  
- No prompt content in unrestricted log analytics workspaces.  
- Redaction pipelines before any secondary analytics.  
- Penetration tests for IDOR on `run_id`.  
- Plugin egress SSRF protections.

### 5.13 Product surfaces mapping

| Surface | Latency class | Typical model | Grounding |
|---------|---------------|---------------|-----------|
| Outlook / Word Copilot | Interactive | Large + tools | Graph |
| Teams meeting recap | Interactive/async | Large | Transcript store |
| GitHub / VS Copilot complete | Ultra-low latency | Small/fast | Local file context (client) |
| Azure OpenAI customer apps | Mixed | Customer-chosen | Customer RAG |
| Nightly eval batch | Batch | Any | Often none |

Client-provided code context for IDE stays on client when possible; server sees snippets per product policy.

### 5.14 Consistency of metering

```text
reserve(estimated_tokens) -> run -> settle(actual_tokens)
sweeper: expire leases -> settle/release
Idempotent settle with run_id
Billable usage events -> Event Hubs -> rating
```

### 5.15 Multi-SKU economics

Assign credit weights: `reason > chat-large > chat-small > embed`.  
Tenant contracts buy capacity units; burst pays more or queues.  
Interview: connect to Azure AI quota UX customers already know.

---

## 6. Wrap-Up

### 6.1 Designed

A **regional Copilot prompt platform**: Entra-authenticated ingress, residency compiler, hierarchical admission against GPU pools, model routing, streaming, grounding via OBO tools, safety/DLP/Purview hooks, metering, and explicit degradation—cell-scalable inside Azure geos.

### 6.2 Decisions to defend

1. Regional/hard-pin cells over global GPU soup  
2. Residency as compiler constraint  
3. Split planes: admit vs GPU vs stream vs audit  
4. Interactive GPU watermark vs batch  
5. Hierarchical WFQ fairness  
6. OBO Graph, not app-only superuser  
7. Visible model degradation  
8. Fail closed on audit/quota critical paths when policy demands  
9. Tenant-scoped caches only  
10. Sovereign isolation  

### 6.3 Risks

- Stranded GPUs per region  
- Graph dependency latency  
- Prompt injection via grounding  
- Policy complexity across M365 SKUs  
- Stream gateway stampedes  
- Misconfigured geo pins  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope regional Copilot plane; residency + Entra |
| 5–12 | Load classes + GPU math |
| 12–25 | Admit → route → stream HLD + diagram |
| 25–35 | Grounding OBO, safety, quotas |
| 35–45 | Overload, 100× cells, deal-breakers |

### 6.5 Closer

> **Regional AI / Copilot prompts**: admit fairly against scarce GPUs, stream fast, ground safely with Entra OBO, never silent-spill residency, never silent-downgrade quality, scale by cells—not by hoping a global region saves you.

---

## 7. Deeper / Related Interview Questions

### 7.1 Capacity

**Q: GPUs idle in East US, EU melting—what do you do?**  
A: If policy forbids spill, you **queue/degrade/expand EU**—not steal US capacity. Discuss capacity planning and in-geo secondary.

**Q: How do you size interactive watermark?**  
A: Historical p95 concurrent interactive decode + headroom; revisit weekly; protect Sev2 Copilot UX.

### 7.2 Identity

**Q: Where do you enforce Conditional Access?**  
A: Token issuance + continuous evaluation; API rejects missing claims / revoked sessions.

**Q: Guest users in tenant?**  
A: Honor tenant guest Copilot policy; often restricted; don’t assume home-tenant geo.

### 7.3 Streaming

**Q: Client dies mid-stream—do you keep decoding?**  
A: Cancel on disconnect after grace; stop GPU waste; settle partial per policy.

**Q: IDE wants resume after laptop sleep?**  
A: Option B replay buffer Phase 2; MVP retry new run with idempotency for non-side-effect completes.

### 7.4 Grounding

**Q: How do you prevent Copilot from exfiltrating ACL-invisible files?**  
A: Graph returns only ACL-visible items for OBO identity; server must not use search indexes that ignore ACL.

**Q: Prompt injection in an email?**  
A: Untrusted content boundaries; tool confirmation for risky actions; DLP on outbound.

### 7.5 Multi-tenancy

**Q: Hot tenant thundering herd?**  
A: Per-tenant concurrency caps; isolate cell; automation detection; account team capacity packs.

### 7.6 Consistency / billing

**Q: Double settle?**  
A: Idempotent settle keyed by `run_id`; ledger monotonic.

### 7.7 Comparison traps

**Q: Is this just “API Gateway + Azure OpenAI”?**  
A: AOAI is a building block; Copilot adds residency compiler, M365 grounding, hierarchical fairness, Purview, surface SLOs, interactive watermarks.

**Q: Why not one global Kafka of prompts?**  
A: Residency, latency, blast radius, compliance.

### 7.8 Failure injection list

1. Kill inference pod mid-decode.  
2. Partition Redis.  
3. Entra JWKS 500 for 2 minutes.  
4. Graph 429 storm.  
5. Safety service latency spike.  
6. Audit Event Hubs throttle.  
7. AZ failure.  
8. Mis-shipped router allowing eastus for EU tenant (catch in compiler tests).  
9. Cache key missing `tid`.  
10. Batch job consumes all GPUs (watermark regression).

### 7.9 Extra high-value traps

- What exactly is stored where when audit is off?  
- Who can read prompt logs—tenant admin, Microsoft support, model training? (training uses opt-in / compliant pipelines—say the boundary)  
- How do embeddings jobs interact with chat pools?  
- What’s the unit of fair share—seats, prompts, tokens?  
- How do you prove residency in an incident review?  
- When is 503 better than a 30s queue?  
- How does GitHub Copilot context stay out of M365 audit lakes?  
- How do you roll a new model without breaking allowlists?  
- What is the blast radius of a poisoned plugin?  
- How do CAE revocations interact with long reasoning runs?

### 7.10 Related Microsoft prompts

- Azure regional failover / migration (sibling doc)  
- Azure Key Vault  
- Chat for Azure / M365 users  
- IDE / Visual Studio design (client Copilot UX)  
- Rate limiter / distributed cache primitives  

---

## 8. Appendices

### Appendix A — Example schemas

```sql
CREATE TABLE prompt_runs (
  run_id           UUID PRIMARY KEY,
  tenant_id        UUID NOT NULL,
  user_oid         UUID NOT NULL,
  app_id           UUID NOT NULL,
  surface          TEXT NOT NULL,
  region_cell      TEXT NOT NULL,
  geo              TEXT NOT NULL,
  status           TEXT NOT NULL,
  model_requested  TEXT NOT NULL,
  model_resolved   TEXT,
  degradation_json JSONB,
  quota_lease_id   UUID,
  gpu_lease_id     UUID,
  prompt_tokens    INT,
  completion_tokens INT,
  safety_outcome   TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at     TIMESTAMPTZ
);
CREATE INDEX runs_tenant_created ON prompt_runs (tenant_id, created_at DESC);

CREATE TABLE tenant_copilot_policies (
  tenant_id        UUID PRIMARY KEY,
  geo_pin          TEXT NOT NULL,
  allowed_regions  TEXT[] NOT NULL,
  allowed_models   TEXT[] NOT NULL,
  audit_mode       TEXT NOT NULL, -- off|metadata|content
  dlp_mode         TEXT NOT NULL,
  interactive_share_bps INT NOT NULL DEFAULT 10000,
  version          BIGINT NOT NULL,
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE usage_outbox (
  id               BIGSERIAL PRIMARY KEY,
  run_id           UUID NOT NULL,
  tenant_id        UUID NOT NULL,
  payload          JSONB NOT NULL,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at     TIMESTAMPTZ
);
```

### Appendix B — Redis quota key sketch

```text
rpm:{tid}:{sku}:{yyyyMMddHHmm}  → counter INCR with TTL
tpm_reserve:{tid}:{sku}          → token bucket / sliding
conc:{tid}:{class}               → concurrency
lease:{lease_id}                 → {run_id, exp, generation}
idem:{tid}:{idem_key}            → run_id
```

### Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Regional stamp, Entra auth, Redis quotas, SKU pools, SSE, basic DLP |
| 10× | Stream fleets, WFQ, Graph OBO cache, Event Hubs meter, interactive watermark |
| 100× | Tenant cells, safety scale-out, Purview content audit tiers, batch isolation |
| 1,000× | Geo compiler, forecasting, sovereign stamps, semantic cache (tenant-safe), on-device hooks |

### Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Copilot surface | Product entry (Outlook, VS, Teams, Azure AI…) |
| Residency compiler | Policy ∩ geo ∩ capacity → legal pools |
| Interactive watermark | GPU fraction reserved for human-facing Copilot |
| OBO | On-behalf-of token exchange to Graph |
| TPM / RPM | Tokens / requests per minute |
| SKU pool | Homogeneous inference deployment capacity |
| Cell | Isolation shard within a region |
| Sovereign cloud | Physically/logically isolated national cloud |
| CAE | Continuous Access Evaluation |
| Purview | Compliance / audit / DLP platform |

### Appendix E — Estimation cheat-sheet

```text
Split: admit QPS ≠ output tokens/s ≠ SSE events/s ≠ Graph QPS

Concurrent decode ≈ peak_output_tok_s / tok_s_per_stream
GPUs ≈ peak_output_tok_s / effective_tok_s_per_GPU

Redis ops ≈ admit_QPS × ~5
Stream RAM ≈ conns × 50–100 KB

Never solve GPU shortage with more BFF replicas alone
```

### Appendix F — Sample degradation notices

```text
"Using a faster model due to high demand in West Europe."
"Graph tools temporarily unavailable; answering without mailbox grounding."
"Your organization requires EU data residency; capacity is constrained—try again shortly."
```

### Appendix G — Interview whiteboard order

1. Actors + Entra tenant boundary  
2. Regional stamp diagram  
3. Admit pipeline + Redis  
4. GPU pools + watermark  
5. Stream path  
6. Grounding OBO  
7. Overload + residency deal-breakers  
8. 100× cells  

### Appendix H — Policy pseudocode

```text
function admit(req, token):
  claims = validate_entra(token)
  policy = load_policy(claims.tid)
  if policy.copilot_blocked: reject(403)
  cells = residency_compile(policy, req.preferred_region)
  if cells.empty: reject(451 or 403 residency)
  if not safety_precheck(req): refuse()
  lease = quota.reserve(claims.tid, req.sku_class, req.est_tokens)
  if not lease: queue_or_reject()
  route = router.choose(cells, policy.allowed_models, capacity)
  run = create_run(...)
  dispatch(run, route)
  return run
```

### Appendix I — SLO / SLA sketch

| Class | TTFT p99 | Availability | Notes |
|-------|----------|--------------|-------|
| IDE complete | < 500ms | 99.9% | Small model |
| M365 chat | < 2s | 99.9% | Tools extra |
| Reasoning | n/a / ETA | 99.5% | Queue OK |
| Batch embed | throughput | 99% | Preemptible |

### Appendix J — Related internals (talk track)

Microsoft interviewers often probe whether you understand **Azure regions vs geos vs sovereign**, **Entra tenancy**, **M365 Graph ACL reality**, and **GPU scarcity**. Lead with those—not with generic “add Kafka + Kubernetes.”

---

*End of design doc. Open with §1 residency + Entra; whiteboard §4; close with invariants §5.1 and traps §7.*
