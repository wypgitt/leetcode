# System Design: Webhook Delivery Service

> **Focus areas:** Subscriptions · Durable outbox · Retries/backoff · HMAC signatures · Deduplication · Ordering · DLQ · Endpoint isolation · SSRF protection  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS types, explicit deal-breakers, at-least-once with consumer idempotency expectations, Stripe-style API correctness & ledger event integration

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

Goal: **bound the delivery product**—what we guarantee to subscribers (at-least-once, ordering scope), and how we isolate noisy/failing endpoints at high event rates.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who produces events? | Internal services (payments, billing, chat, …) | Producer API + **durable outbox** integration |
| F2 | Who consumes? | Merchant/customer HTTPS endpoints | Per-endpoint credentials & URLs |
| F3 | Subscription model? | Subscribe to event types / topics; secret for HMAC | `subscription` + `endpoint` entities |
| F4 | Delivery semantics? | **At-least-once**; consumers must be idempotent | Dedupe keys in payload/headers |
| F5 | Ordering? | **Per subscription** best-effort/strict optional; no global order | Sequence per subscription; parallel across subs |
| F6 | Signatures? | HMAC-SHA256 over body + timestamp | Replay window; key rotation |
| F7 | Retries? | Exponential backoff + jitter; max attempts → DLQ | Attempt history; retry-after respect optional |
| F8 | Success criteria? | HTTP 2xx within timeout | 3xx policy explicit; 410 → disable |
| F9 | Deduplication? | `delivery_id` / `event_id` stable across retries | Same payload + id on retry |
| F10 | Observability? | Delivery logs, status, latency, response codes | Merchant-facing portal |
| F11 | Manual ops? | Redrive DLQ, pause endpoint, rotate secret | Admin APIs + audit |
| F12 | Filtering? | Optional event-type filters / versioning | Match at enqueue time |

**MVP functional scope (lock with interviewer):**

1. CRUD **endpoints** + **subscriptions** (event types → URL).  
2. Producers publish events → **durable** before ACK.  
3. Workers deliver HTTPS POST with **HMAC signature** + timestamp.  
4. Retries with **exp backoff + jitter**; terminal **DLQ**.  
5. Stable **event_id** / **delivery_id** for consumer idempotency.  
6. Per-endpoint isolation (one bad URL doesn’t stall all).  
7. Basic portal: recent deliveries, response codes, redrive.  
8. SSRF protections on URL allow/deny.

**Out of MVP (explicitly defer):**

- Exactly-once end-to-end without consumer cooperation  
- Guaranteed total global ordering across all merchants  
- SOAP/legacy non-HTTP transports  
- Transform/mapping DSL (light filters only)  
- Mutual TLS as sole auth (can be Phase 1.5 alongside HMAC)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Enqueue latency | Producer path fast | p99 < 50–100ms durable ACK in-region |
| N2 | Delivery freshness | Soft real-time | p50 < 1s healthy endpoints; retries separate |
| N3 | Durability | No lost accepted events | Quorum/disk before producer ACK |
| N4 | Availability | High for enqueue | 99.9%+; isolate delivery failures |
| N5 | Multi-tenant fairness | Noisy endpoint isolation | Shuffle shard / per-endpoint queues |
| N6 | Multi-region | Global producers | AA ingest gateways; **home cell** for subscription delivery state |
| N7 | Security | No SSRF to cloud metadata | URL validation, egress proxy, block private ranges |
| N8 | Scale | Up to ~1000× event/s class | See scale table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Producer publishes `invoice.paid` → durable → matched subscriptions → POST → 200 → `SUCCEEDED`.  
2. Endpoint down → 503 → retry with backoff → later 200.  
3. Endpoint returns 200 twice (duplicate deliver) → consumer dedupes on `event_id`.  
4. Secret rotated → dual-key verify window; new sig with current key.  
5. Manual redrive from DLQ → new attempt under same `event_id` (or explicit redrive id policy).  
6. Pause endpoint → backlog holds; resume drains with rate limit.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Producer double publish | Producer idempotency key → one event |
| Worker crash after 200 before local complete | Re-deliver → consumer idempotency required |
| Slow endpoint (30s) | Hard timeout (e.g. 5–10s); counts as fail; isolate concurrency |
| Endpoint redirects to internal IP | Block redirects or re-validate URL (SSRF) |
| 410 Gone | Auto-disable subscription; stop retries |
| Poison payload crashes worker | DLQ after N; don’t block partition forever |
| Ordering: event 2 before event 1 on wire | If strict order enabled, per-sub concurrency=1; else document best-effort |
| Thundering herd retries | Jitter + per-endpoint token bucket |
| Huge payload | Cap size (e.g. 256KB–1MB); use pointer/fetch URL pattern if larger |
| Clock skew on timestamp sig | Allow skew window (e.g. ±5 min) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants / merchants | 1K | 10K | 100K | 1M |
| Active endpoints | 5K | 50K | 500K | 5M |
| Event types | 50 | 100 | 200 | 500 |
| Events accepted / day | 50M | 500M | 5B | 50B |
| Peak **enqueue** QPS | ~1K | ~10K | ~100K | ~1M |
| Avg subscriptions matched / event | 1.2 | 1.2 | 1.5 | 2 |
| Peak **delivery attempts**/s | ~1.5K | ~15K | ~200K | ~2M+ |
| Retry amplification (avg) | 1.3× | 1.3× | 1.5× | 1.5–2× |
| DLQ depth (steady) | ~1K | ~10K | ~100K | ~1M |
| Portal/read QPS | ~200 | ~2K | ~20K | ~200K |

**What each jump forces:**

- **10×:** Outbox + queue workers; per-endpoint concurrency caps; HMAC; DLQ.  
- **100×:** Shuffle sharding; egress proxy fleet; delivery log cold tier; strict vs parallel modes.  
- **1,000×:** Cell architecture; hierarchical queues; adaptive concurrency (AIMD); multi-region home cells; bloom/idempotency caches carefully.

### 1.5 Etc. (Constraints & Assumptions)

- Delivery is **push HTTPS**; consumers provide public endpoints.  
- We do **not** claim exactly-once; we provide stable ids + at-least-once.  
- Ordering default: **best-effort per subscription**; strict opt-in.  
- Payload typically JSON; schema versioning via event type version.

**Scope statement:**

> Design a multi-tenant webhook delivery service: durable ingest, subscription matching, signed HTTPS delivery, retries with backoff/jitter, per-endpoint isolation, DLQ/redrive, and SSRF-safe egress—starting ~1K enqueue QPS and scaling through 10× / 100× / 1,000× (~1M enqueue QPS) with sharded queues and home-cell delivery state.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Enqueue / accept | 1K | 1M | Durable write |
| Match / fanout to subs | ~1.2K | ~2M | Amplify by match factor |
| HTTP delivery attempts | ~1.5K | ~2–3M | Includes retries |
| Delivery log writes | ~1.5K | ~2–3M | Often async batched |
| Heartbeats/leases (workers) | hundreds | 100K+ | Internal |
| Portal reads | 200 | 200K | Cache lists |

**Critical:** Retries make **attempt QPS** > **event QPS**. Plan capacity on attempts, not unique events.

### 2.2 Storage

```text
Event metadata ~500 B–1 KB; payload avg 2 KB
Delivery attempt log ~300 B each

Baseline 50M events/day × 3 KB ≈ 150 GB/day raw
1,000×: 50B events/day × 3 KB = 150 TB/day

Unit check: 50e9 × 3e3 B = 150e12 B = **150 TB/day** (not PB)
Retain hot 7–30 days; cold object storage thereafter.
```

### 2.3 Bandwidth

```text
1,000× delivery 2M attempts/s × 2 KB body ≈ 4 GB/s egress
→ many regions / egress proxies; connection reuse (HTTP keep-alive / HTTP2)
```

### 2.4 Memory

```text
Per-endpoint state: backoff cursor, circuit, in-flight ≤ tens of KB
5M endpoints × 10 KB = 50 GB cluster-wide if all hot — shard; keep cold endpoints on disk
```

### 2.5 Retry load math

```text
Success rate first try 90%, then geometric:
Attempts ≈ events × (1 + 0.1 + 0.1×0.5 + ...)  → tune with real data
If first-try success drops to 70% during outage, attempt storms → need jitter + caps
```

### 2.6 Critical bottlenecks

1. Hot failing endpoint retry storms  
2. Enqueue durability path  
3. Egress connection churn / DNS  
4. Strict ordering concurrency=1 throughput  
5. SSRF-safe egress proxy capacity  
6. Delivery log write amplification  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Producer → Event (event_id, type, payload, occurred_at)
         → Outbox / Event Log (durable)
Subscription (tenant, filter, endpoint_id, order_mode)
Endpoint (url, secret, status, concurrency, timeout)
Delivery (delivery_id, event_id, subscription_id, attempt, status)
```

### 3.2 Producer path: durable outbox

**Pattern A — Outbox table with business TX** (when producer has DB):

```text
Business TX: update domain + insert outbox_row
CDC/poller publishes to bus → webhook service
```

**Pattern B — Webhook service ingest API** with idempotency:

```text
POST /events + Idempotency-Key → persist → ACK → async match/deliver
```

**Chosen for this design:** Webhook platform ingest + encourage domain outbox at producers. **Deal-breaker:** fire-and-forget HTTP to webhook workers without durability.

### 3.3 Matching & enqueue deliveries

```text
For each event:
  find subscriptions where type matches AND endpoint active
  create delivery records (or queue messages) keyed by (event_id, subscription_id)
```

Unique constraint on `(event_id, subscription_id)` prevents double-matching under retries.

### 3.4 Delivery workers & leases

```text
Claim delivery READY with lease (CAS)
POST to endpoint
On 2xx → SUCCEEDED
On retryable fail → schedule next_attempt_at = now + backoff
On terminal → DEAD / DLQ
```

Same lease/fencing ideas as job schedulers; stale worker cannot mark success incorrectly if lease checked—but **HTTP may have succeeded** before crash → duplicates possible ⇒ consumer idempotency.

### 3.5 Signatures (HMAC)

```text
signed_content = timestamp + "." + body
signature = HMAC_SHA256(secret, signed_content)
Headers:
  X-Webhook-Id: event_id
  X-Webhook-Delivery: delivery_id
  X-Webhook-Timestamp: t
  X-Webhook-Signature: v1=hex(sig)
```

Consumer rejects if `|now - t| > window` (replay protection).

**Key rotation:** keep `secret_current` + `secret_previous` for overlap; sign with current; consumers accept either.

### 3.6 Retries: exponential backoff + jitter

```text
delay = min(cap, base * 2^attempt) * (1 + U[-jitter,+jitter])
# e.g. base=1s, cap=1h, jitter=0.2, max_attempts=12
```

Respect optional `Retry-After` on 429/503 (capped).

**Terminal failures:** 410, 404 (policy), explicit disable, max attempts, invalid SSL (policy).

### 3.7 Ordering: per subscription vs best-effort

| Mode | Concurrency | Guarantee | Cost |
|------|-------------|-----------|------|
| Best-effort (default) | N parallel per endpoint | None across events | High throughput |
| Strict per subscription | 1 in-flight | In-order success progression | Head-of-line blocking |

**Resolve contradiction:** “Ordering” does **not** mean global platform order. Opt-in strict mode uses single consumer pointer / seq per subscription.

**Resume vs cancel:**

- **Pause endpoint:** stop claiming; backlog retains order.  
- **Cancel/disable:** terminal skip remaining or DLQ per policy—**don’t** silently drop without audit.  
- **Redrive:** creates new attempts; strict mode inserts carefully to not violate seq expectations (document).

### 3.8 Deduplication

| Layer | Mechanism |
|-------|-----------|
| Producer ingest | Idempotency-Key |
| Match | Unique (event_id, subscription_id) |
| Consumer | event_id / delivery payload id |
| Retries | Same event_id & body & signature inputs (timestamp may change—document!) |

**Note:** If timestamp changes each attempt, signature changes; **event_id stays stable** for idempotency. Prefer consumer keys on `event_id` not signature.

### 3.9 Per-endpoint isolation & circuit breakers

```text
Token bucket: max in-flight + max QPS per endpoint
Circuit breaker: if error rate high → OPEN (cool down) → HALF_OPEN probe
Shuffle sharding: tenant/endpoint → subset of worker shards
```

**Deal-breaker:** one global FIFO queue for all endpoints (head-of-line across tenants).

### 3.10 SSRF protection

| Control | Detail |
|---------|--------|
| URL allowlist schemes | `https` only (http optional enterprise) |
| DNS resolve & block | Private/link-local/metadata IPs (127/8, 10/8, 169.254/16, ::1, …) |
| No insecure redirects | Re-check redirect targets |
| Egress proxy | Central allow/deny logging |
| Size/time limits | Timeout + max body |

**Deal-breaker:** naive `curl(user_url)` from worker network with cloud metadata access.

### 3.11 At-least-once & consumer expectations

We promise:

1. Accepted events will be **attempted** until success or DLQ.  
2. Duplicates may occur.  
3. Headers include stable **event_id**.  
4. Consumers **must** be idempotent.

We do **not** promise exactly-once HTTP.

### 3.12 Storage / queue trade-offs

| Component | Choice | Deal-breaker |
|-----------|--------|--------------|
| Event durability | Log/DB before ACK | ACK then Kafka without local durability story |
| Hot retry schedules | Per-shard time index / delay queues | `SELECT * FROM deliveries WHERE due` globally unindexed |
| Delivery logs | Append store + TTL | Unbounded OLTP growth |
| Secrets | KMS-backed | Plaintext in app config repo |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Producers (services)
        |
        | POST /v1/events (idempotent)  or  CDC from outbox
        v
+-------------------+
| Ingest API (AA)   |
+---------+---------+
          |
          v
+-------------------+     +------------------+
| Event Store       |---->| Matcher          |
| (home cell)       |     | (subs index)     |
+-------------------+     +--------+---------+
                                   |
                                   v
                          Delivery records / queues
                          (sharded by endpoint_id)
                                   |
                                   v
                          +------------------+
                          | Delivery Workers |
                          | (leases)         |
                          +--------+---------+
                                   |
                                   v
                          Egress Proxy (SSRF guards)
                                   |
                                   v
                          Customer HTTPS Endpoints

Side paths:
  DLQ + Redrive API
  Portal / Delivery Logs
  Metrics / Alerts (failure rate, lag, circuit open)
```

### 4.2 Sequence: happy path

```text
Producer → Ingest (idem_key, type, body) → Event Store durable → 202/200
Matcher → create Delivery(event, sub) unique
Worker → lease delivery
Worker → compute HMAC → POST egress → Endpoint
Endpoint → 200
Worker → mark SUCCEEDED; write log
```

### 4.3 Sequence: failure + retry + DLQ

```text
Worker POST → 503
→ schedule next_attempt_at = now + backoff+jitter; release lease
... attempts until max
→ DEAD; write DLQ; alert if spike
Merchant fixes endpoint → Redrive DLQ → READY attempts
```

### 4.4 Sequence: strict ordering

```text
Subscription seq 10 in-flight
Event 11 waits (not claimed) until 10 SUCCEEDED or DEAD(policy)
If 10 stuck retrying, 11 delayed → document HOL risk; offer parallel mode
```

### 4.5 Multi-region

```text
Ingest gateways: active-active
Directory: tenant/endpoint → home cell
Delivery state & attempts: single-writer home
Egress: regional proxies near workers; still home owns scheduling
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable event** (and durable intent to deliver to matched subs).  
2. **Unique delivery** per `(event_id, subscription_id)`.  
3. **At-least-once attempts** until terminal state.  
4. **Stable event_id** across retries.  
5. **HMAC** on every attempt with replay timestamp window.  
6. **No SSRF** to blocked ranges.  
7. **Per-endpoint isolation** for scheduling fairness.  
8. **Terminal states audited** (SUCCESS/DEAD/CANCELLED).  
9. **Home-cell single-writer** for delivery scheduling state.

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Worker death after 200 | Duplicate delivery; consumer idempotency |
| Endpoint outage | Backoff + circuit; other endpoints unaffected |
| Poison event | Max attempts → DLQ; skip |
| Secret leak | Rotate; invalidate previous after grace |
| Matcher bug misses sub | Repair job from event log + sub version |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | API + PG outbox/deliveries + worker pool |
| 10× | Queue shards by `hash(endpoint_id)`; Redis rate limits; egress proxy |
| 100× | Shuffle sharding; adaptive concurrency; log tiering; portal CQRS |
| 1000× | Cells; hierarchical schedulers; HTTP2 conn pools at huge scale; sample logs |

**Adaptive concurrency (AIMD):** increase in-flight while 2xx fast; decrease on timeouts/5xx—protects both sides.

### 5.3 Maintainability

- Contract tests for signature formats  
- Chaos: blackhole endpoints, DNS fail, worker kill  
- Customer-facing delivery timeline  
- Versioned event schemas; deprecation windows  
- Clear docs: **idempotency requirements for consumers**  

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× (~1K enqueue QPS)**

- Ingest API + Postgres `events`/`deliveries`.  
- Worker pool `SKIP LOCKED` due deliveries.  
- HMAC; simple backoff; DLQ table.  
- URL validator library for SSRF.

**10×**

- Shard deliveries by `endpoint_id`.  
- Egress proxy service.  
- Per-endpoint in-flight caps in Redis.  
- Delivery attempt logs to cheaper store.

**100×**

- Shuffle sharding across worker fleets.  
- Circuit breakers + AIMD concurrency.  
- Strict ordering as opt-in.  
- Portal via CQRS read models.  
- Autoscale on delivery lag metrics.

**1000× (~1M enqueue QPS)**

- Cells by tenant.  
- Hierarchical queues (tenant → endpoint → due heap).  
- HTTP/2 conn pools; DNS cache with SSRF revalidation.  
- Sampled verbose logs; full logs to object storage firehose.  
- Adaptive admission: shed low-priority event types under overload.

### 5.5 Consumer contract (normative)

Merchants **must**:

1. Verify signature + timestamp window.  
2. Dedupe on `id` / `X-Webhook-Id`.  
3. Return 2xx only when durable locally (or accept duplicates on redelivery).  
4. Respond within timeout; process async if heavy.  

Merchants **should**:

1. Use HTTPS with modern TLS.  
2. Rotate secrets periodically.  
3. Prefer 503 with Retry-After when overloaded (not 500 loops).  

### 5.6 Matching engine notes

```text
Index: event_type → [subscription_id...]
Filter predicates compiled (type in list, optional tenant attributes)
On subscription change: version bump; matcher uses version for repair scans
Fanout amplification monitored per event_type
```

Hot event types (e.g. `message.created`) may need dedicated pipelines.

### 5.7 Egress performance

- Keep-alive pools keyed by destination host.  
- Cap concurrent connects per host/IP.  
- Prefer IPv4/IPv6 policy explicit.  
- TLS session resumption.  
- Timeouts: connect vs total distinct.  
- Body upload streaming from object store for large payloads (rare).  

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| ACK without durability | Lost webhooks |
| Global FIFO queue | Tenant HOL |
| No SSRF controls | Cloud metadata theft |
| Exactly-once marketing | False confidence |
| Unbounded retries | Cost & storms |
| Sign without timestamp | Replay attacks |
| Dual schedulers active-active | Duplicate storms |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Semantics | At-least-once + stable ids |
| Durability | Ingest/outbox before ACK |
| Security | HMAC + SSRF egress proxy |
| Isolation | Per-endpoint queues/caps/circuits |
| Ordering | Best-effort default; strict opt-in |
| Multi-region | AA ingest; SW home delivery |

### 6.2 Risks

1. Retry storms  
2. SSRF holes  
3. Claiming exactly-once  
4. Global queue HOL  
5. Signature timestamp vs idempotency confusion  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Semantics, subscriptions, scale |
| 5–15 | Outbox + match + worker leases |
| 15–25 | Retries, DLQ, isolation, circuits |
| 25–35 | HMAC, SSRF, ordering modes |
| 35–45 | Multi-region, 1000×, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Semantics

**Q: Why not exactly-once?**  
A: HTTPS + crashes after success before local commit ⇒ duplicates. Provide stable ids; consumers dedupe.

**Q: Is Kafka EOS enough?**  
A: Helps internal processing; doesn’t eliminate duplicate HTTP side effects.

**Q: At-most-once?**  
A: Loses events on failures—usually unacceptable for webhooks.

### 7.2 Outbox & producers

**Q: Dual-write domain DB + webhook API?**  
A: Risk lost/dup. Prefer transactional outbox or single durable ingest with producer idempotency.

**Q: CDC vs poller?**  
A: CDC lower lag; poller simpler. Both OK if outbox rows are truth.

### 7.3 Retries & backoff

**Q: Why jitter?**  
A: Avoid synchronized retry stampedes when many deliveries fail together.

**Q: Infinite retries?**  
A: No—cap + DLQ; poison protection; cost control.

**Q: Should 429 use longer backoff?**  
A: Yes—honor Retry-After within caps.

**Q: Are 3xx success?**  
A: Usually no—define policy; following redirects is SSRF-sensitive.

### 7.4 Ordering

**Q: Guarantee order for a subscription?**  
A: Strict mode with concurrency 1; accept HOL blocking.

**Q: Does success order equal enqueue order under retries?**  
A: Only with strict mode and policies for DEAD (block vs skip).

**Q: Cross-subscription order?**  
A: Not provided.

### 7.5 Signatures & security

**Q: Why timestamp in signature?**  
A: Replay protection within window.

**Q: Why not only mTLS?**  
A: Operational burden for many merchants; mTLS optional add-on.

**Q: SSRF to 169.254.169.254?**  
A: Block link-local/metadata; resolve & verify IPs; egress proxy.

**Q: Rotating secrets?**  
A: Dual keys; overlap window; audit.

### 7.6 Isolation & fairness

**Q: Noisy slow endpoint?**  
A: Low concurrency, circuit open, separate shard—don’t share FIFO with healthy endpoints.

**Q: Shuffle sharding?**  
A: Map endpoint to 2 of N shards; isolates blast radius.

**Q: Fairness vs latency?**  
A: Weighted caps; priority event types optional.

### 7.7 Deduplication

**Q: delivery_id vs event_id?**  
A: `event_id` = business event identity across retries; `delivery_id` may identify an attempt chain; document which consumers should key on (usually `event_id`).

**Q: Changing body on retry?**  
A: Don’t—body must be stable for a given event_id.

### 7.8 DLQ & ops

**Q: Auto-redrive?**  
A: Careful—prefer manual/auto only when health recovers (HALF_OPEN success streak).

**Q: Poison message?**  
A: Detect crash loops; skip to DLQ quickly; alert.

**Q: Replay last 24h?**  
A: Time-range redrive tool with rate limit; audit.

### 7.9 Multi-region

**Q: Active-active delivery schedulers for same endpoint?**  
A: Risk double delivery storms + conflicting state—home cell owns schedule.

**Q: Producer in region A, endpoint in B?**  
A: Fine—schedule in home; egress from convenient region.

**Q: Failover?**  
A: Fence epoch; expect duplicate deliveries; consumers idempotent.

### 7.10 Scale to 1M enqueue QPS

**Q: One Postgres?**  
A: No—shard event store & delivery queues by tenant/endpoint; log-oriented ingest.

**Q: Logging every attempt at 3M/s?**  
A: Sample or tier; aggregate metrics hot path; full logs to cheap object storage async.

**Q: DNS per attempt?**  
A: Cache DNS carefully with TTL; still revalidate for SSRF when TTL refreshes.

### 7.11 Comparison

**Q: vs Amazon SNS / EventBridge?**  
A: Similar product shape; interview expects you to rebuild core: durability, retry, sigs, isolation, DLQ.

**Q: vs Kafka consumers directly?**  
A: Kafka great internally; external customer HTTPS needs this delivery layer.

### 7.12 Observability

**Q: SLOs?**  
A: Enqueue success; time-to-first-attempt; success rate excluding customer faults; DLQ rate; lag by endpoint.

**Q: Customer debugging?**  
A: Show request headers (redacted), response code/body snippet, attempt timeline.

### 7.13 Payload & schemas

**Q: Large payloads?**  
A: Cap; store blob; send pointer event; or signed GET fetch.

**Q: Versioning?**  
A: `type` + `schema_version`; additive changes; dual-publish during migrations.

### 7.14 Interview traps

**Q: 50B events/day × 3 KB = 150 PB/day?**  
A: **150 TB/day**. 50e9×3e3=150e12 B=150 TB.

**Q: Global ordering + 1M QPS?**  
A: Essentially impossible without severe bottleneck—don’t offer it.

**Q: “We’ll dedupe in Redis exactly-once”?**  
A: Helps, but crash windows + Redis loss still need consumer idempotency for money-ish effects.

### 7.15 Cancel / pause / resume (resolved)

**Q: Pause vs delete vs DLQ?**  
A:  
- **Pause:** retain backlog; no attempts.  
- **Disable/delete:** stop future matches; in-flight finish or cancel per policy; audit.  
- **Resume:** drain with rate limit; circuits start HALF_OPEN.  
- **Redrive:** explicit from DLQ; not automatic un-cancel.

**Q: Ownership of work?**  
A: Matcher owns creating delivery rows; **workers** own attempts under leases; control plane owns pause/disable. Producers do not push HTTP to customers directly.

---

## 8. Appendices

### 8.1 Schema sketches

```text
endpoints(endpoint_id, tenant_id, url, secret_ref, status, max_in_flight, timeout_ms)
subscriptions(subscription_id, tenant_id, endpoint_id, event_types[], order_mode, status)
events(event_id, tenant_id, type, payload_ref, idempotency_key, created_at)
  UNIQUE(tenant_id, idempotency_key)
deliveries(delivery_id, event_id, subscription_id, status, attempt, next_attempt_at,
           lease_id, lease_until, last_http_status)
  UNIQUE(event_id, subscription_id)
delivery_attempts(delivery_id, attempt, at, status_code, latency_ms, error, body_snip)
dlq(delivery_id, reason, dead_at)
```

### 8.2 Example headers

```text
POST /merchant/hooks HTTP/1.1
Content-Type: application/json
X-Webhook-Id: evt_123
X-Webhook-Delivery: del_456
X-Webhook-Timestamp: 1710000000
X-Webhook-Signature: v1=abcdef...
User-Agent: WebhookService/1.0

{"id":"evt_123","type":"invoice.paid","created":"...","data":{...}}
```

### 8.3 Consumer checklist (publish to merchants)

- [ ] Verify HMAC + timestamp window  
- [ ] Dedupe on `event_id`  
- [ ] Return 2xx only after durable local accept  
- [ ] Respond quickly; async heavy work  
- [ ] Use HTTPS; rotate secrets  

### 8.4 Operator checklist

- [ ] SSRF egress rules tested  
- [ ] Per-endpoint caps default on  
- [ ] DLQ alerts  
- [ ] Key rotation runbook  
- [ ] Redrive rate limits  
- [ ] Chaos: kill workers mid-POST  

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| Outbox | Durable table/log ensuring emit-after-commit |
| Delivery | Per-subscription attempt chain for an event |
| DLQ | Dead-letter queue for exhausted deliveries |
| Circuit breaker | Temporarily stop calling failing endpoint |
| Shuffle sharding | Isolate tenants across random shard subsets |
| HOL blocking | Head-of-line: one stuck msg blocks later ones |
| Egress proxy | Controlled outbound HTTP path |

### 8.6 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Durable ingest, HMAC, retries, DLQ, basic workers |
| 10× | Endpoint sharding, concurrency caps, egress proxy |
| 100× | Circuits, shuffle shards, strict order opt-in, log tiering |
| 1000× | Cells, adaptive concurrency, massive conn pools, sampled logs |

### 8.7 Backoff schedule example

| Attempt | Base delay | With ±20% jitter (approx) |
|---------|------------|---------------------------|
| 1 | 1s | 0.8–1.2s |
| 2 | 2s | 1.6–2.4s |
| 3 | 4s | 3.2–4.8s |
| 4 | 8s | 6.4–9.6s |
| 5 | 16s | 12.8–19.2s |
| 6 | 32s | 25.6–38.4s |
| 7 | 64s | ~1m |
| 8 | 128s | ~2m |
| 9 | 256s | ~4m |
| 10 | 512s | ~8m |
| 11+ | cap 1h | jittered up to 1h |

Max attempts e.g. 12–20 depending on product; then DLQ.

### 8.8 Circuit breaker states

```text
CLOSED --high error rate--> OPEN --cool down--> HALF_OPEN --probes OK--> CLOSED
                               \--probe fail--> OPEN
Metrics window: e.g. 50 requests or 30s rolling
Customer-facing: show “deliveries delayed due to endpoint errors”
```

### 8.9 SSRF validation algorithm

```text
1. Parse URL; scheme https only
2. Reject credentials in URL; reject weird ports if policy
3. Resolve DNS → set of IPs
4. For each IP: reject if private/link-local/metadata/broadcast
5. Connect via egress proxy to resolved IP with TLS SNI/Host
6. If redirect: restart validation on Location (limit hop count)
7. Enforce timeout + max response size (we usually ignore body beyond status)
```

### 8.10 Strict ordering pointer model

```text
subscription.delivery_cursor = last_succeeded_event_seq
Next claimable = min(events where seq = cursor+1 and due)
On SUCCESS: cursor++
On DEAD with policy skip: cursor++ (document data loss risk for order-dependent consumers)
On DEAD with policy block: cursor stays; alert (HOL)
```

### 8.11 Worked scale example (1000×)

```text
Enqueue peak 1M events/s
Match factor 2 → 2M new deliveries/s
First-try success 85% → retries add ~0.3–0.6M attempts/s steady
Outage of top 1% endpoints can dominate attempts → circuits essential

Egress: 2.5M attempts/s × 2KB ≈ 5 GB/s ≈ 40 Gbps
→ multi-region egress; conn reuse; HTTP/2 where possible
```

### 8.12 Interview “say this” summary (60 seconds)

> Producers get a durable ACK via ingest/outbox; we match subscriptions and create unique deliveries per `(event_id, subscription)`; workers lease and POST through an SSRF-safe egress proxy with HMAC signatures; failures retry with exponential backoff and jitter under per-endpoint concurrency caps and circuit breakers; exhausted deliveries go to DLQ with redrive; consumers must be idempotent—we’re at-least-once; ordering is best-effort by default with opt-in strict per subscription; multi-region ingest is active-active with **single-writer home cells** for scheduling state.

### 8.13 Extra traps

| Trap | Pushback |
|------|----------|
| Global FIFO | Cross-tenant HOL |
| Follow redirects blindly | SSRF |
| Exactly-once HTTP | Crash after 200 |
| Sign only body without timestamp | Replay |
| One Redis list for all | Hot key + fairness fail |
| Change body each retry | Breaks consumer dedupe assumptions |
| 50B×3KB=150PB/day | **150TB/day** |

### 8.14 Reliability test plan

1. Kill worker after endpoint 200 → duplicate; consumer dedupe.  
2. Endpoint returns 503 forever → backoff → DLQ; neighbors healthy.  
3. DNS flips to 169.254.169.254 → blocked.  
4. Strict mode stuck message → HOL visible in metrics.  
5. Secret rotation mid-traffic → dual verify works.  

### 8.15 Related systems map

```text
Domain services → Outbox/CDC → Ingest API → Event Store
                         ↓
                      Matcher → Delivery shards
                         ↓
                 Workers → Egress Proxy → Customer URLs
                         ↓
                 Logs/Metrics/Portal ; DLQ/Redrive
```

### 8.16 Pseudocode: claim + deliver

```text
function workerLoop(shard):
  d = claimDueDelivery(shard, lease=30s)
  if !d: sleep(poll); continue
  body = loadPayload(d.event_id)
  headers = sign(body, now, secrets[d.endpoint])
  resp = egress.post(d.url, body, headers, timeout=d.timeout)
  if resp.status in 200..299:
     complete(d, SUCCEEDED, fencing=d.lease_id)
  else if terminal(resp):
     complete(d, DEAD, reason=resp.status)
  else:
     scheduleRetry(d, backoff(d.attempt))
```

### 8.17 Portal UX requirements (MVP)

- List recent deliveries filtered by status/type  
- Detail: attempt timeline, status codes, latency  
- Button: pause / resume / rotate secret / redrive DLQ  
- Metrics: success rate 24h, p95 latency, currently open circuits  

---

*End of webhook delivery service system design.*
