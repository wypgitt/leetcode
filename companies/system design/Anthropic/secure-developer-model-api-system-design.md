# System Design: Secure Developer Model API

> **Focus areas:** API keys · Authentication · Model/version selection · Quotas · Billing · Streaming · Abuse controls  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split auth/check/inference/billing load classes, explicit key-security invariants, Anthropic Messages-API flavor (Claude models, prompt caching, safety)

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

Goal: **bound the product**—a **secure public developer API** for Claude models (Messages API style): keys, authn/z, model selection, quotas, metering/billing, streaming, and abuse—distinct from Claude Chat consumer UX and from raw GPU schedulers.

### 1.0 Developer API vs Claude Chat (say this early)

| Dimension | **Developer Model API (this doc)** | **Claude Chat** |
|-----------|------------------------------------|-----------------|
| Primary user | Developers / backend apps | End users chatting |
| Auth | API keys, OAuth for consoles | User sessions |
| Conversation store | Client-owned (stateless messages) | First-class product DB |
| Billing | Usage-based, invoices, prepaid | Subscription tiers primarily |
| SLOs | Hard latency/error budgets per tier | Soft UX SLOs |
| Prompt caching | Explicit `cache_control` hooks | Product-internal |
| Abuse | Key theft, crypto-mining-like floods, jailbreaks via API | Account spam |

**Scope statement:** Design the secure Claude developer API control + data plane edge—not the chat app, not training.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who calls the API? | Server-side apps; some browser (restricted) | Key secrecy; CORS policy; optional short-lived tokens |
| F2 | Core API? | Messages create (+ stream); maybe Completions legacy | Idempotent create; SSE stream |
| F3 | Auth? | API keys (`sk-ant-...`); org/project scope | Hash-at-rest; key → org/project/role |
| F4 | Models? | `claude-haiku-*`, `claude-sonnet-*`, `claude-opus-*` + aliases | Resolve alias → immutable `model_version` at admit |
| F5 | Quotas? | RPM, TPM in/out, concurrency per key/project/org/model | Hierarchical limiter; reserve/settle |
| F6 | Billing? | Pay-as-you-go tokens (+ cache write/read prices) | Usage events → ledger → invoice |
| F7 | Streaming? | `stream: true` SSE events | Same auth/quota; settle actual tokens |
| F8 | Prompt caching? | Optional cache breakpoints | Meter cache hits/writes separately |
| F9 | Safety / abuse? | Usage policy; classifiers; key revocation | Pre/post filters; anomaly detection |
| F10 | Workspaces? | Org → projects → keys | Hierarchical authz + budgets |
| F11 | Idempotency? | Header for retries | Dedup window |
| F12 | Admin? | Console: create/revoke keys, view usage | Audit log |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/messages` with auth via API key; sync + **SSE streaming**.
2. Model alias resolution to pinned `model_version`.
3. Hierarchical quotas: org → project → key (+ per-model).
4. **Reserve/settle** for TPM + concurrency; RPM checks.
5. Usage event pipeline → billing ledger (tokens in/out, cache).
6. Key lifecycle: create, show-once, hash store, rotate, revoke.
7. Abuse: rate limits, anomaly, policy classifiers, emergency revoke.
8. Standard error model: `401/403/404/413/429/529/500` + request_id.

**Out of MVP (explicitly defer):**

- Perfect globally linearizable quota counters
- Marketplace / reseller billing complexity
- Fine-grained customer-managed VPC endpoints (hooks only)
- Batch API as primary (sibling GPU batch doc)
- Customer-trainable models

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Auth overhead? | Tiny vs inference | p99 < 5–10ms key auth+quota in-region |
| N2 | TTFT (stream)? | Competitive | Model-dependent; API overhead < 20–50ms |
| N3 | Availability? | Tiered | 99.9%+ API edge; degrade with 529 |
| N4 | Billing accuracy? | Money | ≤0.1% unresolved usage after reconciliation |
| N5 | Key security? | Breach-resistant | Keys hashed; show once; scoped |
| N6 | Abuse response? | Fast revoke | Revocation propagates ≤ seconds regionally |
| N7 | Multi-region? | Yes | Regional inference + global org contracts |
| N8 | Consistency? | Quotas eventually reconciled | Bound overshoot |
| N9 | Auditability? | Enterprise | Access + admin audit logs |
| N10 | Safety? | Policy enforcement | High-sev fail closed |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Valid key → messages request → quota allow → inference → stream SSE → settle usage → billable event.
2. Non-stream JSON response for small completions.
3. Prompt-cache hit → cheaper/faster prefill → meter `cache_read` tokens.
4. Key rotate → old key grace or immediate invalidate.
5. Org hits monthly budget → soft alert then hard 429.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Invalid / revoked key | 401; no model touch |
| Key leaked (GitHub) | Anomaly spike → alert + optional auto-suspend |
| Streaming 10× estimate | Settle debt; throttle subsequent; optional cancel |
| Duplicate Idempotency-Key | Same response / same message id |
| Alias `claude-sonnet-latest` moves | New admits resolve new version; in-flight keep old |
| Org payment delinquent | Soft → hard block; webhook to billing |
| 529 overloaded | Retry-After; don’t charge full failed prefill if policy says so |
| Browser key use | Deny or severe CORS+referrer restrictions (prefer server keys) |
| Prompt injection via API | Still apply safety classifiers; org policy mode |
| Clock skew on idempotency TTL | Server time only |
| Partial stream client abort | Cancel generation; bill tokens produced per policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Orgs | 50K | 500K | 5M | 50M |
| API keys | 200K | 2M | 20M | 200M |
| Peak **request QPS** | 20K | 200K | 2M | 20M |
| Peak **auth+quota check QPS** | 20K | 200K | 2M | 20M |
| Peak concurrent streams | 50K | 500K | 5M | 50M |
| Peak output tokens/s | ~500K | ~5M | ~50M | ~500M |
| Usage events/s | ~20–40K | ~200–400K | ~2–4M | ~20–40M |
| Billing ledger writes (agg) | ~2K | ~20K | ~200K | cells |
| Key lookups/s | = check QPS | ×10 | ×100 | regional auth caches |
| Revocation propagations/day | hundreds | thousands | — | config CDN |

**What each jump forces:**

- **10×:** Redis quota cluster; key auth cache; async usage bus; dedicated stream edge.
- **100×:** Regional authz replicas; hierarchical token budgets; billing aggregators; abuse ML; prompt-cache metering at scale.
- **1,000×:** Org home regions for contracts; sharded ledgers; global deny lists via edge; capacity SKUs per model/region.

### 1.5 Etc. (Constraints & Assumptions)

- Inference is behind an **Inference Gateway** (batching sibling docs).
- Keys never stored plaintext at rest after creation.
- Billing is **append-only usage** + separate ledger; limiter ≠ ledger.
- Constitutional / safety layers still apply on developer API (policy modes may vary by trust tier).

**Scope statement to repeat back:**

> Design Anthropic’s secure developer Messages API: API-key auth, org/project hierarchy, model alias→version resolution, hierarchical RPM/TPM/concurrency quotas with reserve/settle, streaming SSE, prompt-cache metering, usage→billing ledger, and abuse/revocation—scaled 10×/100×/1,000× with regional enforcement and global contracts.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **TLS + edge** | Connections | 20K req/s | 200K | Edge |
| **Key auth** | Hash verify / cache | 20K/s | 200K | Auth |
| **Quota check/reserve** | RPM/TPM/conc | 20K/s | 200K | Redis limiter |
| **Inference admits** | After allow | ≤20K/s | ×10 | Inference GW |
| **SSE frames** | Stream events | ~25–100K/s | ×10 | Stream edge |
| **Usage events** | Per request (+settle) | ~40K/s | ×10 | Kafka |
| **Billing aggregates** | Minute/hour rolls | ~2K/s | ×10 | Ledger workers |
| **Safety classifiers** | Input/output | ~×k of admits | ×10 | Safety |
| **Admin/console** | CRUD keys | low hundreds | ×10 | Control plane |

**Anti-pattern:** blending “API QPS” with token throughput or billing writes.

### 2.2 Auth math

```text
API key: sk-ant-api03-<secret>
Store: HMAC/SHA-256 or Argon2id hash of secret; prefix for lookup
Lookup: prefix → candidate row → constant-time compare hash

Auth cache: (key_id → org, project, scopes, revoked_version) TTL 5–30s
Revoke must short-circuit cache (version epoch / pubsub invalidate)

20K checks/s × 1 Redis RTT ≈ needs local L1 cache hit rate >90%
If 95% L1 hit: Redis auth QPS ≈ 1K/s baseline — comfortable
At 2M checks/s (100×): still need L1 + regional Redis; not one global Redis
```

### 2.3 Quota math (reserve/settle)

```text
Dimensions per request:
  RPM: +1 request in window
  Concurrency: +1 in-flight
  TPM_in: + estimated_input_tokens (incl. cache-aware)
  TPM_out: + estimated_max_output (or soft reserve)

On complete:
  settle actual input/output/cache tokens
  concurrency -1
  adjust TPM debt/credit

Check latency budget: p99 < 10ms → Redis pipeline multi-key updates in region
```

### 2.4 Token / GPU cost → billing

```text
Example list prices (illustrative only for interview math):
  Sonnet: $3 / MTok in, $15 / MTok out
  Cache read: $0.30 / MTok; cache write: $3.75 / MTok (illustrative)

Baseline 500K out tok/s × 86400 ≈ 43.2B out tok/day
If 30% of peak sustained average → rough; use interviewer numbers

Revenue/cost coupling:
  Unmetered cache writes or failed-prefill billing disputes → support load
  Must emit usage with request_id, model_version, cache breakdown
```

### 2.5 Streaming amplification

```text
50K concurrent streams
Event every 20 tokens → if 40 tok/s → 2 events/s/stream → 100K events/s
Edge memory: 50K × 64KB ≈ 3.2 GB — fine fleetside
Problem is NOT memory; it's authz cancel paths + settle correctness
```

### 2.6 Billing pipeline volume

```text
20K requests/s × 2 events (start+end) ≈ 40K usage msgs/s
Kafka partition by org_id
Aggregator: per (org, project, model, minute) rollups
Ledger write amplification: 40K/s → ~few K/s rollup updates if buffered

At 2M req/s: must aggregate at edge collectors before central ledger
```

### 2.7 Cost of abuse / leaked keys

```text
Leaked key at 100 RPM × 4K out tokens × 60 min =
  100×4000×60 = 24M out tokens in an hour
At $15/MTok → $360/hour — material; detection SLA minutes not days
```

---

## 3. High-Level Design

### 3.1 Domain model

```text
Organization
  ├── BillingAccount (payment method, credits, invoice currency)
  ├── Projects[]
  │     ├── Budgets / model allowlists
  │     └── API Keys[]
  │           ├── key_id, prefix, hash, scopes, status
  │           ├── rate_limit overrides
  │           └── last_used_at
  ├── Members / Roles (console)
  └── Usage → Ledger lines → Invoices

Request (Messages)
  ├── request_id
  ├── key_id, org_id, project_id
  ├── model_requested → model_version_resolved
  ├── messages[], system[], tools[], cache_control
  ├── stream bool
  ├── status, error_code
  ├── usage {input, output, cache_read, cache_write}
  └── safety_outcome
```

### 3.2 API surface

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/messages` | Create message (stream optional) |
| POST | `/v1/messages/count_tokens` | Token estimate (optional MVP+) |
| GET | `/v1/models` | List accessible models |
| POST | `/v1/keys` (console API) | Create key |
| POST | `/v1/keys/{id}/revoke` | Revoke |
| GET | `/v1/usage` | Usage query |

```http
POST /v1/messages
x-api-key: sk-ant-api03-...
anthropic-version: 2023-06-01
Idempotency-Key: ...
{
  "model": "claude-sonnet-4-...",
  "max_tokens": 1024,
  "messages": [{"role":"user","content":"Hello"}],
  "stream": true
}
```

**SSE event types (illustrative):** `message_start`, `content_block_delta`, `message_delta`, `message_stop`, `error`.

### 3.3 Authentication & API keys

| Approach | Pros | Cons | Deal-breaker |
|----------|------|------|--------------|
| Plaintext keys in DB | Simple | Breach catastrophic | **Yes — never** |
| **Hash + prefix lookup (chosen)** | Industry standard | Rotate UX | Showing key twice |
| mTLS only | Strong | Hard for devs | Alone excludes indie devs |
| Gateway JWT exchange | Short-lived | Extra hop | OK as Phase 1.5 for browsers |

**Key lifecycle:**

```text
Create → generate secret → show once in console → store hash+prefix
Use → prefix lookup → hash verify → load grants
Rotate → new key; old revoke_at = now or now+grace
Revoke → status=revoked; epoch++; push invalidate
```

**Scopes (examples):** `messages:write`, `models:read`, project-bound, model allowlist.

**Constant-time compare** on hashes; uniform 401 messages (avoid user enumeration on keys).

### 3.4 Authorization hierarchy

```text
Edge authenticates key
  → resolve org, project, scopes
  → enforce IP allowlist / workspace restrictions (enterprise)
  → model allowlist
  → budget / payment status
  → quota reserve
  → safety policy profile for org trust tier
```

| Check | Fail closed? |
|-------|--------------|
| Auth | Yes |
| Revocation | Yes |
| Payment delinquent hard state | Yes |
| Quota Redis down | Free/startup: yes; Enterprise: discuss static ceiling |
| Safety high-sev | Yes |

### 3.5 Model / version selection

```text
Alias (claude-sonnet-latest) → Resolver → immutable model_version
Pinned ID (claude-sonnet-4-YYYYMMDD) → pass-through if allowed
```

| Strategy | Pros | Cons |
|----------|------|------|
| Aliases only | Simple UX | Surprise breaks |
| Pins only | Stable | Toil |
| **Aliases + pins (chosen)** | Best of both | Document freeze-at-admit |

**Invariant:** once admitted, `model_version` on the request record does not change mid-stream.

**Prompt caching interaction:** cache keys include `model_version` + prefix hash; alias retarget invalidates logical caches (expected).

### 3.6 Quotas

| Dimension | Algorithm (typical) | Notes |
|-----------|---------------------|-------|
| RPM | Token bucket / sliding window | Burst friendly |
| TPM | Reserve estimate + settle | Streaming essential |
| Concurrency | Atomic gauge | Prevents stampede |
| Monthly $ budget | Soft→hard | Billing-linked |

**Hierarchy:** `min(org, project, key, model-sku)` effective remaining.

| Design | Tradeoff |
|--------|----------|
| Regional hard + global soft | Low latency; bound global overshoot |
| Global hard sync every check | Too slow / chatty |
| **Chosen:** regional enforce + async global reconciler | Staff-level pragmatic |

Headers (illustrative): `anthropic-ratelimit-requests-remaining`, `retry-after`.

### 3.7 Billing & metering

```text
Request terminal → UsageEvent{
  request_id, org, project, key_id,
  model_version,
  input_tokens, output_tokens,
  cache_read_tokens, cache_write_tokens,
  latency_ms, status
} → Kafka → Aggregators → Ledger → Invoice

Credits / prepaid: decrement holding account with idempotent apply(request_id)
```

| Approach | Pros | Cons | Deal-breaker |
|----------|------|------|--------------|
| Bill from limiter counters | Simple | Not audit-grade | **Yes for money** |
| **Append-only usage events (chosen)** | Auditable | Pipeline complexity | Dropping events without DLQ |
| Sync write ledger per request | Strong | Won’t scale | At 100× |

**Pricing dimensions:** uncached input, output, cache write, cache read; maybe tool dollars later.

**Disputes:** rebuild from usage events by `request_id`; never from sampling metrics alone.

### 3.8 Streaming specifics

```text
Admit (auth, quota reserve, safety input)
  → create request row (durable minimal)
  → Inference stream
  → SSE proxy (do not buffer forever)
  → on end: settle + usage event
  → on client abort: cancel + settle partial
```

**Time-to-first-byte:** auth+quota+safety must be tightly budgeted; do not run heavy billing I/O on admit path.

### 3.9 Abuse controls

| Layer | Controls |
|-------|----------|
| Credential | Hashing, show-once, rotation, GitHub secret scanning partnerships |
| Rate | RPM/TPM/concurrency; progressive delays |
| Economic | Prepaid/max balance; anomaly $/hour |
| Content | Input/output classifiers; policy modes |
| Network | IP reputation; geo; WAF |
| Account | KYC for high tiers; rapid revoke |
| Ops | Kill switch per key/org/model |

**Signals:** sudden TPM 100× baseline, many 400s, card-testing patterns, known bad prompt packs.

### 3.10 Safety on developer API

Still apply Constitutional / policy layers. Differences vs chat:

- Org may have **higher trust tiers** (still not “no safety”).
- Errors may return structured `refusal` vs consumer UX copy.
- Logging retention may be stricter (ZDR / enterprise no-train).

### 3.11 Component trade-offs

| Component | Options | Choice | Deal-breaker |
|-----------|---------|--------|--------------|
| Key store | PG vs KV | **PG control plane** + regional auth cache | Plaintext secrets |
| Quotas | Local only vs Redis | **Redis regional + L1** | Single global Redis RTT |
| Usage bus | Kafka vs Pulsar vs Kinesis | **Kafka-class** | Sync billing on admit |
| Stream edge | Envoy/custom | **Dedicated stream tier** | App servers holding all SSE |
| Alias config | DB vs CDN config | **Versioned config** push | Hidden alias flips without audit |

**Alternatives considered:**

- OAuth-only machine auth → poor DX for simple server keys.  
- Client-side billing estimates → not trustworthy.  
- Quotas in primary PG → latency and load kill admit path.

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +------------------+     +---------------------+
| Customer    |---->| Edge / WAF /     |---->| API Gateway         |
| backends    |     | TLS termination  |     | (Messages)          |
+-------------+     +--------+---------+     +----------+----------+
                             |                          |
                             v                          v
                    +----------------+         +--------+----------+
                    | Auth + Key     |<------->| Control Plane PG  |
                    | Cache (L1/L2)  |         | orgs/keys/aliases |
                    +--------+-------+         +-------------------+
                             |
                             v
                    +----------------+         +-------------------+
                    | Quota Limiter  |<------->| Redis regional    |
                    | reserve/settle |         | RPM/TPM/conc      |
                    +--------+-------+         +-------------------+
                             |
         +-------------------+-------------------+
         v                   v                   v
+----------------+  +----------------+  +------------------+
| Safety Policy  |  | Inference GW   |  | Usage Collector  |
| Classifiers    |  | (Claude GPUs)  |  | → Kafka          |
+----------------+  +--------+-------+  +--------+---------+
                             |                   |
                             v                   v
                      SSE to client      +-------+----------+
                                         | Billing Agg +    |
                                         | Ledger + Invoice |
                                         +------------------+
```

### 4.2 Request lifecycle (streaming)

```text
Client          Edge/API GW         Auth          Quota         Safety       Inference      Usage/Billing
  |                 |                 |             |             |              |               |
  | POST messages   |                 |             |             |              |               |
  |---------------->|                 |             |             |              |               |
  |                 | verify key      |             |             |              |               |
  |                 |---------------->|             |             |              |               |
  |                 | org/project     |             |             |              |               |
  |                 |-------------------------------------------->|              |               |
  |                 | reserve RPM/TPM/conc                        |              |               |
  |                 |---------------->|             |             |              |               |
  |                 | resolve model_version         |             |              |               |
  |                 | input classify  |             |             |              |               |
  |                 |-------------------------------------------->|              |               |
  |                 | admit ------------------------------------------>|               |
  |  SSE deltas     |<----------------------------------------------|               |
  |<----------------|               |             |             |              |               |
  |                 | settle + usage event -------------------------------------------->|
  |  message_stop   |               |             |             |              |  ledger apply |
  |<----------------|               |             |             |              |               |
```

### 4.3 Key revocation data flow

```text
Console revoke → Control PG status=revoked, epoch++
              → Pubsub / config push → regional auth caches invalidate key_id
              → In-flight: cancel flag optional for emergency
Edge: cache miss or epoch mismatch → re-fetch → 401
SLA: regional ≤ few seconds; global ≤ tens of seconds
```

### 4.4 Billing data flow

```text
UsageEvent (request terminal)
  → Kafka topic usage.raw (partition key org_id)
  → Flink/aggregator → usage.rollup.1m
  → Ledger applier (idempotent by request_id)
  → Balance / invoice lines
  → Customer usage API + finance export
DLQ + reconciler compares Inference completes vs ledger
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Preventing “free inference”

**Invariant:** no Inference admit without successful auth + quota reserve (or explicit internal bypass with audit).

Failed settle: sweeper TTL releases concurrency/TPM reservation; usage reconciler bills from inference completion log if event lost.

#### 5.1.2 Idempotency

- `Idempotency-Key` + key_id → stored response reference for 24h.  
- Streaming: first request owns generation; replay returns documented behavior (same id + reconnect policy or 409 conflict if parallel).  
- Billing apply idempotent on `request_id`.

#### 5.1.3 Retries

Customer guidance: retry 429/529 with jitter; do not retry non-idempotent without key.  
Internal: Inference retries only for safe failures before tokens stream; after stream starts, don’t silently double-generate.

#### 5.1.4 Rate limiting interactions with billing

Limiter overshoot ≠ free tokens: usage events still bill.  
Prepaid hard stop: when credits hit 0 mid-stream, policy either (a) cut generation or (b) allow finish + negative balance—**pick one and document**.

#### 5.1.5 Safety reliability

High-sev classifier outage → fail closed (529/403 policy).  
Don’t skip safety to save latency on public API.

#### 5.1.6 Key breach response

1. Detect (secret scanning, anomaly).  
2. Auto-suspend or rate clamp.  
3. Notify org owners.  
4. Force rotate.  
5. Forensic usage export.

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Scale | Auth | Quotas | Billing | Edge |
|-------|------|--------|---------|------|
| Baseline | PG + Redis cache | Single-region Redis | Kafka + one aggregator | Regional API |
| **10×** | L1/L2 auth caches | Redis cluster; hierarchical keys | Parallel consumers | Stream tier split |
| **100×** | Regional auth replicas | Regional hard + global reconciler | Sharded ledger by org | Multi-region active |
| **1,000×** | Edge deny lists for revoked hot keys | Capacity SKUs; fair share per model | Cell-based finance pipelines | Anycast + regional pin |

#### 5.2.2 Hot keys / noisy neighbors

Celebrity org hammering one model:

- Per-org fair share queues in Inference GW.  
- Coarser quota buckets for hot keys.  
- Isolate abusive keys without pausing entire org when possible.

#### 5.2.3 Prompt caching at API scale

```text
Customer sets cache_control breakpoints
API computes cacheable prefix hash + model_version
Inference sticky route → hit/miss
Meter: cache_write on miss populate; cache_read on hit
```

At 100×, cache index and sticky rings matter as much as raw GPUs (cost).

#### 5.2.4 Traffic spikes

Product launches / viral apps:

- Burst RPM via token buckets.  
- Concurrency caps protect GPU KV memory.  
- 529 rather than meltdown.  
- Sales-driven limit raises via config service (versioned).

#### 5.2.5 What breaks at each jump

| Jump | Breaks | Fix |
|------|--------|-----|
| 10× | PG auth on every request | Auth cache; Redis quotas |
| 100× | Central billing writers; global quota chatty | Rollups; regional enforce |
| 1,000× | Hot org; revoke fanout; ledger size | Shards; edge deny; cold usage store |

### 5.3 Maintainability

#### 5.3.1 Versioning

- `anthropic-version` request header for API behavior.  
- Model aliases versioned in config with audit.  
- Pricing version ids on usage events (critical for disputes).

#### 5.3.2 Observability

| Metric | Purpose |
|--------|---------|
| auth_fail_rate | Attacks / outages |
| quota_deny_rate by dimension | Capacity vs abuse |
| ttft / error_rate by model | SLO |
| usage_event_lag | Billing freshness |
| ledger_unreconciled | Money risk |
| revoke_propagate_s | Security SLO |
| cache_hit_rate | Cost/UX |

Trace every request with `request_id` returned to customer.

#### 5.3.3 SLOs

| SLO | Target |
|-----|--------|
| Auth+quota p99 | < 10ms in-region |
| API availability (5xx excl 529) | 99.9% |
| Usage durable after success | 99.99% eventually reconciled |
| Revoke regional effective | < 5s p99 |
| High-sev policy miss | ~0 (eval programs) |

#### 5.3.4 Config & ops

- Shadow limits (observe-only).  
- Canary new model aliases to 1% keys.  
- Runbooks: billing lag, Redis quota failover, mass revoke, regional inference drain.

#### 5.3.5 Compliance

- SOC2/audit logs for key create/revoke.  
- Enterprise ZDR paths: no training retention; separate storage class.  
- Encryption at rest; field encryption for key hashes / secrets.

---

## 6. Wrap-Up

### 6.1 Summary talking points

1. **Hash-at-rest API keys**, show-once, fast revoke with cache epochs.  
2. **Admit path:** auth → authz → quota reserve → safety → inference; billing async.  
3. **Alias vs pin** resolved immutably per request.  
4. **Hierarchical RPM/TPM/concurrency** with reserve/settle for streaming.  
5. **Usage events are source of truth for money**; limiter is not.  
6. **Abuse** is economic + credential + content + network.  
7. Scale via regional enforcement, auth caches, sharded ledgers.

### 6.2 Risk register

| Risk | Impact | Mitigation |
|------|--------|------------|
| Key leak | Financial + abuse | Scanning, anomaly, rapid revoke |
| Usage event loss | Revenue leakage | Inference completion reconciler + DLQ |
| Quota overshoot | Noisy neighbor | Bound + fair queues |
| Alias surprise | Customer break | Pins + changelog |
| Billing lag | Support / cash | Lag SLOs; credits buffer |
| Safety skip under load | Harm / brand | Fail closed high-sev |
| PG control plane hotspot | Auth outage | Caches + replicas |

### 6.3 Phased rollout

| Phase | Ship |
|-------|------|
| MVP | Messages+stream, keys, basic RPM/TPM/conc, usage→invoice, safety |
| 1.5 | Prompt cache metering, count_tokens, budgets, anomaly auto-clamp |
| 2 | Multi-region active, hierarchical enterprise, ZDR, OAuth device flows |
| 3 | Cell-sharded billing, edge revoke, capacity SKUs, batch API integration |

---

## 7. Deeper / Related Interview Questions

### Q1. Why hash API keys instead of encrypting them?

**A:** Encryption implies decrypt-to-compare or decrypt-at-use; breach of decrypt key exposes all. Hashing (with prefix index) verifies without recoverable plaintext. Show-once is the UX cost.

### Q2. Where do you store the key prefix vs hash?

**A:** Both in control-plane DB: `prefix` unique index for lookup, `hash` for verify. Prefix alone must be insufficient to authenticate.

### Q3. How do you revoke keys in <5s globally?

**A:** You may not get perfect global <5s; sell **regional** SLO. Use epoch bump + pubsub invalidate; edge negative cache for hot revoked keys; accept brief cross-region lag with risk bounds.

### Q4. RPM vs TPM vs concurrency — why all three?

**A:** RPM stops request floods; TPM stops token economics abuse; concurrency stops KV/GPU slot exhaustion from slow streams. Each covers a failure mode the others miss.

### Q5. Why can’t the rate limiter be the billing system?

**A:** Limiters optimize for speed and may overshoot/approximate. Billing needs append-only, idempotent, auditable events tied to `request_id` and pricing version.

### Q6. How does reserve/settle work when `max_tokens` is huge?

**A:** Reserve `min(max_tokens, tier_cap)` or probabilistic soft reserve; raise debt as stream progresses (chunk settle); hard-cancel if exceeds hard budget.

### Q7. What’s a deal-breaker in model alias design?

**A:** Changing alias target without audit / customer communication, or changing `model_version` mid-stream.

### Q8. How do you price prompt cache writes vs reads?

**A:** Writes cost more (populate KV/prefix); reads discounted. Meter separately; include in usage events; watch customers gaming tiny oscillating prefixes.

### Q9. Sliding window vs token bucket for RPM?

**A:** Token bucket allows controlled bursts (DX-friendly). Sliding window is smoother but harsher on bursts. Often bucket for RPM, gauge for concurrency.

### Q10. How do you prevent browser-embedded keys?

**A:** DX docs + optional referrer/CORS deny for browser origins; prefer short-lived exchange tokens via customer backend; anomaly on browser UA patterns.

### Q11. Consistent hashing uses here?

**A:** Org → billing shard; `cache_key` → inference worker; idempotency key → request record shard. Not one ring for everything.

### Q12. How do you design the error body for 429?

**A:** Stable JSON with `type`, `message`, `request_id`; headers for remaining/reset; avoid leaking other orgs’ info.

### Q13. What indexes on the keys table?

**A:** Unique(`prefix`); index(`org_id`); index(`project_id`); status filter. Avoid full-table scans on auth path—auth should hit cache anyway.

### Q14. Fanout problem in admin audit?

**A:** Don’t synchronously notify every regional cache with large payloads. Push `key_id+epoch` invalidations; caches pull details on demand.

### Q15. How do you handle partial outage of safety classifiers?

**A:** Fail closed for high-severity; optionally degrade low-severity. Emit 529/403 rather than unfiltered generations for public API.

### Q16. Double billing risk on retries?

**A:** Idempotency-Key collapses duplicates; billing apply idempotent by `request_id`. Without idempotency, customer retries may create two billable requests—document clearly.

### Q17. How do enterprise allowlists interact with quotas?

**A:** Allowlist is authz (403 if model not permitted). Quotas are capacity/money (429). Check authz before quota to avoid burning limiter budget confusingly—or check both atomically in one policy engine.

### Q18. What’s the data structure for hierarchical remaining quota?

**A:** Nested token buckets / windows keyed by `org`, `org+project`, `org+project+key`, `org+model`. Effective allow = all layers allow. Update in a Redis Lua/pipeline for atomicity.

### Q19. How do you scale Kafka usage events at 2M req/s?

**A:** Partition by org_id carefully (hot orgs → subpartition by project); edge local aggregators emit rollups + samples of raw; keep raw for sample of disputes + always for high-$ requests.

### Q20. LB algorithm for API gateways?

**A:** Least-conn or ewma for streaming (connections long-lived); separate pools for stream vs non-stream if possible; drain gently.

### Q21. Memory risk on API nodes?

**A:** Huge `messages` payloads: enforce body size (413); skip storing full prompts in hot PG (object store refs if needed for enterprise logs); never buffer entire stream in memory for “relogging.”

### Q22. How do you test billing correctness?

**A:** Golden request fixtures → expected usage → ledger lines; chaos drop events → reconciler fills gaps; property tests on idempotent apply.

### Q23. Why regional quota enforcement?

**A:** Inference is regional; admit latency budgets can’t pay cross-coast RTT. Global contracts reconciled asynchronously with bounded overshoot.

### Q24. Algorithm for anomaly detection on leaked keys?

**A:** EWMA baseline per key on TPM/$/geo/IP entropy; z-score or robust thresholds; auto-clamp then human review for big orgs; auto-suspend for small prepaid.

### Q25. How does this interact with batch inference APIs?

**A:** Same keys/auth/billing dimensions; different latency class and quota pools (batch TPM separate from interactive). Don’t let batch starve interactive without SKU separation.

### Q26. What belongs in `anthropic-version` header?

**A:** Wire format / field semantics / default behaviors—not model weights. Model selection is the `model` field.

### Q27. Storage for idempotency records?

**A:** Redis/Dynamo with TTL 24h storing hash of request + response reference. Conflict if same key different body → 422.

### Q28. How do you keep maintainability when pricing changes?

**A:** Pricing version ids on each usage event; never reprice historical events silently; migrations via explicit rebill tools.

### Q29. Horizontal scale of the control plane PG?

**A:** It should stay relatively small (orgs/keys). Scale reads via replicas/caches. If multi-million keys, shard by org_id; auth path still L1/L2 cached.

### Q30. Staff-level closing line?

**A:** “Ordinary API gateway concerns—authn/z, quotas, billing, abuse—front an extraordinary GPU inference backend; keep money and safety correct without putting Kafka or PG on the TTFT path.”

---

*End of Secure Developer Model API system design.*
