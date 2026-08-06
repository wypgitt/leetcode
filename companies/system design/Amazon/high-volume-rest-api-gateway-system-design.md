# System Design: High-Volume REST API Gateway / Client-Service Layer

> **Focus areas:** AuthN/Z · Routing · Rate limiting · Retries · Aggregation · Multi-tenant · Caching · Abuse  
> **Style:** Amazon SDE III end-to-end design with progressive scale (10× → 100× → 1,000×)  
> **Amazon themes:** Customer impact · Least privilege · Cell isolation · Operational excellence · Cost at the edge  
> **Quality bar:** Correct arithmetic, explicit invariants, clear consistency for aggregation, honest MVP vs extreme-scale paths

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

Goal: **bound the gateway**—is it a pure reverse proxy, a BFF (backend-for-frontend), or an Amazon-style edge + service mesh combo? Lock auth, tenancy, aggregation, and failure semantics.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who calls the API? | External developers, mobile/web apps, internal services | Separate public edge vs internal; different auth |
| F2 | Auth? | API keys, OAuth2/JWT, IAM SigV4 for internal | AuthN at edge; AuthZ with policies / scopes |
| F3 | Routing? | Path/host → service; versioning (`/v1`, `/v2`) | Route table as data; canary & blue/green |
| F4 | Rate limiting? | Per API key / tenant / IP / method | Distributed limiters; soft vs hard limits |
| F5 | Retries? | Gateway retries idempotent GETs; POST only if idempotency key | Strict retry classes; budget & hedged requests carefully |
| F6 | Aggregation? | Some endpoints fan-out to N microservices (BFF) | Parallel calls; partial failure policy; timeouts |
| F7 | Multi-tenant? | Yes—tenants isolated by key/account | Quotas, shuffle shards, noisy-neighbor controls |
| F8 | Caching? | Cache GETs at edge/CDN where safe | Cache keys include tenant + authz context carefully |
| F9 | Request/response transforms? | Headers, light enrichment; not heavy business logic | Keep gateway thin; push logic to services |
| F10 | Observability? | Per-route latency, error, saturation; trace propagation | OpenTelemetry; consistent `request_id` |
| F11 | Abuse protection? | WAF, bot scores, schema validation, payload limits | Defense in depth before origin |
| F12 | Developer experience? | Keys, docs, sandbox, usage dashboards | Control plane distinct from data plane |

**MVP functional scope (lock with interviewer):**

1. TLS termination, request validation (size, schema basics), routing to upstream services.
2. AuthN: API key + JWT validation; AuthZ: scope / resource policy checks.
3. Per-tenant and per-route **rate limits** with 429 + `Retry-After`.
4. Retries for safe/idempotent requests with budgets; propagate idempotency keys.
5. Optional **aggregation** endpoint pattern (parallel fan-out, timeout, partial response policy).
6. Multi-tenant quotas and basic fair use.
7. Metrics, logs, traces; request IDs; basic WAF rules.

**Out of MVP (explicitly defer):**

- Full GraphQL gateway (mention as alternative)
- Arbitrary plugin sandbox for customer code at the edge
- Global exactly-once mutation guarantees
- Heavy response rewriting / business workflows in gateway
- Active-active multi-region session affinity for all tenants

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency overhead of gateway? | Small vs origin | p50 < 5–10ms added in-region; p99 < 20–40ms excluding origin |
| N2 | Availability? | Edge 99.99% aspirational; origin may be lower | Shed non-critical; fail open vs closed by policy |
| N3 | Throughput? | See scale table | Horizontal scale; connection pools |
| N4 | Multi-tenant fairness? | One tenant cannot melt the edge | Quotas + isolation + cells |
| N5 | Consistency of rate limits? | Eventually consistent OK if bounded overshoot | Prefer Redis/Dynamo token buckets; accept small overshoot |
| N6 | Security? | No plaintext secrets; least privilege upstream | mTLS to origins; short-lived tokens |
| N7 | Multi-region? | Active-active edge; regional origins | Route to nearest healthy cell |
| N8 | Payload limits? | e.g. 1–10 MB default | Explicit caps; streaming for large uploads (often bypass) |
| N9 | Dependency timeouts? | Aggregation must not wait forever | Per-upstream timeout + overall deadline |
| N10 | Cost? | Edge compute & egress dominate at scale | Cache; compression; avoid huge fan-out |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client → TLS → auth → rate limit → route → upstream → response → (optional cache).
2. Aggregated “product page” API → parallel product, price, inventory, reviews → compose 200.
3. Idempotent PUT with `Idempotency-Key` → upstream dedupe → safe client retry.
4. Canary: 5% traffic to v2 upstream by tenant or header.
5. 429 when tenant exceeds QPS; client backs off.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Expired JWT | 401; no upstream call |
| Valid auth, forbidden scope | 403 |
| Rate limit exceeded | 429 + Retry-After; metric by tenant |
| Upstream 503 | Retry if policy allows; else 502/503 with budget |
| Upstream timeout | Fail that branch; aggregation partial or 504 per policy |
| Partial aggregation failure | Return 207/200 with errors array **or** fail closed—pick per API |
| Replay attack | Short JWT TTL; optional nonce for sensitive POSTs |
| Cache poisoning | Vary on auth/tenant; do not cache personalized blindly |
| Huge body | 413; or stream bypass to S3 for uploads |
| Hot tenant | Soft throttle → hard throttle → isolate cell |
| Origin brownout | Circuit breaker; shed load; serve stale cache if allowed |
| Clock skew | JWT `nbf`/`exp` skew leeway (seconds) |
| Header smuggling | Normalize requests; reject ambiguous CL/TE |
| Dependency retry storm | Retry budgets + jitter; collab with clients |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants / API keys | 10K | 100K | 1M | 10M |
| Peak edge RPS | 50K | 500K | 5M | 50M |
| Avg request size | 2 KB | 2 KB | 2–5 KB | 2–5 KB |
| Avg response size | 5 KB | 5 KB | 5–20 KB | 5–20 KB |
| Authenticated % | 95% | 95% | 95% | 95% |
| Cacheable GET % | 30% | 30% | 40% | 50%+ (push) |
| Aggregation fan-out avg | 3 | 3 | 4 | 5 |
| Upstream services | 50 | 100 | 300 | 1,000 |
| Regions / POPs | 2 | 5 | 15 | 50+ POPs |
| Rate-limit checks / s | 50K | 500K | 5M | 50M |
| Config updates / day | 100 | 500 | 2K | 10K |

**What each jump forces:**

- **10×:** Distributed rate limits; connection pooling; auth key cache; horizontal gateway fleet.
- **100×:** Edge POPs / CloudFront+API Gateway style; cell-based tenants; local limiters with global reconciliation; aggregation budgets.
- **1,000×:** Anycast/POP termination; hierarchical limits (POP → region → global); sharded control plane; origin shielding; aggressive caching & CDN.

### 1.5 Etc. (Constraints & Assumptions)

- Gateway is **mostly protocol & policy**, not core business logic.
- Mutations that need strong consistency live in owning services; gateway does not become a distributed transaction manager.
- Large file uploads preferably use **presigned URLs** (bypass), not streamed through gateway fleets.
- Amazon context: think API Gateway + ALB/NLB + Envoy/App Mesh patterns; interview for ownership of edge reliability.
- Fail-open vs fail-closed for rate-limit store outages is a **product decision** per route class.

**Scope statement:**

> Design a high-volume multi-tenant REST API gateway / client-service layer providing auth, routing, rate limiting, safe retries, optional response aggregation, and observability—scaling from ~50K RPS baseline through 10× / 100× / 1,000× with edge cells and hierarchical controls.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS / work classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Edge RPS | 50K | 50M | Terminates TLS + policy |
| Auth validations | ~48K | ~48M | Cache JWKS / API key records |
| Rate-limit ops | 50K | 50M | Often 1–2 ops per request |
| Origin calls (no agg) | ~35K | ~25M | Cache reduces |
| Origin calls (with agg) | ~50K × 0.2 × 3 ≈ 30K extra | scales with fan-out | Cap fan-out |
| Config reads | high but cached | push/invalidate | Avoid per-request control-plane hits |

### 2.2 Bandwidth

```text
Baseline ingress: 50K × 2 KB ≈ 100 MB/s ≈ 0.8 Gbps
Baseline egress:  50K × 5 KB ≈ 250 MB/s ≈ 2 Gbps
1,000×: hundreds of Gbps → must terminate at many POPs; CDN for cacheables
```

Aggregation multiplies **origin** bandwidth more than client bandwidth.

### 2.3 Connections & concurrency

```text
If avg upstream latency 20ms and 50K RPS to origins:
  concurrent origin calls ≈ 50K × 0.02 = 1,000
With aggregation and retries, design for 5–10× headroom → 5K–10K concurrent
At 1,000×: millions concurrent → connection pools, HTTP/2/QUIC, region local origins
```

### 2.4 Rate limiter storage math

```text
Token bucket per (tenant, route) key
Active keys: assume 10% of tenants hot → baseline 1K hot keys; 1,000× → 1M hot keys
State ~100–200 bytes/key → 200 MB hot at extreme (fits sharded Redis)
Updates: 50M/s impossible on one shard → hierarchical / local approximation
```

### 2.5 Auth cache

| Item | Size | TTL | Notes |
|------|------|-----|-------|
| API key → tenant/policy | ~1 KB | minutes | Invalidate on rotate |
| JWKS | small | hours | Refresh on kid miss |
| Session / OAuth introspect | avoid per-request introspect | cache or JWT | |

### 2.6 Critical bottlenecks (rank ordered)

1. **Rate-limit store** centralization — must shard / hierarchize.  
2. **Auth crypto / JWKS** — cache aggressively.  
3. **Origin concurrency & fan-out amplification** — budgets.  
4. **Config push consistency** — eventual with generation numbers.  
5. **Hot tenant / hot route** — isolation.  
6. **TLS & connection churn** — keep-alive, HTTP/2.  
7. **Logging every request body** — sample; cost & PII.  
8. **Retry storms** — budgets and circuit breakers.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| **Route** | Match (host/path/method) → upstream + policies |
| **Tenant / App** | Billing, quota, ownership boundary |
| **Credential** | API key, JWT, IAM principal |
| **Policy** | AuthZ scopes, rate limits, retry, cache TTL |
| **Upstream cluster** | Set of service instances / cells |
| **Aggregation plan** | Parallel calls + compose function |
| **Request context** | request_id, tenant, deadline, trace |
| **Cell / POP** | Edge blast-radius unit |

### 3.2 Edge vs BFF vs service mesh

| Pattern | Role | Use |
|---------|------|-----|
| **Edge gateway** | Public TLS, WAF, coarse auth, rate limit | Internet entry |
| **BFF / experience API** | Aggregation for a client type | Mobile/web product APIs |
| **Mesh sidecar** | mTLS, retries, outlier detection | Service-to-service |

**Interview recommendation:** Draw **edge gateway** for external, optional **BFF** for aggregation, mesh for east-west. Don’t put all business aggregation forever in a global edge.

### 3.3 AuthN / AuthZ

```text
AuthN: prove identity (key/JWT/SigV4)
AuthZ: allow action on resource (scopes, policies)

Flow:
  1) Extract credential
  2) Validate (signature, expiry, status revoked?)
  3) Load tenant policy (cached)
  4) Authorize route + scopes
  5) Inject internal identity headers (signed) to upstream
```

Revocation: short TTLs + bloom/revocation list for emergency keys.

### 3.4 Routing & versioning

- Path prefix / host-based routing.  
- `api-version` header or `/v1` prefix.  
- Weighted routing for canaries.  
- Sticky only when required (prefer stateless).  
- Health-aware load balancing to upstreams.

### 3.5 Rate limiting

| Dimension | Example |
|-----------|---------|
| Per API key | 100 RPS |
| Per tenant | 1,000 RPS burst |
| Per IP (unauth) | 20 RPS |
| Per route | Protect expensive search |
| Concurrent in-flight | Cap fan-out heavy APIs |

Algorithms: **token bucket** (burst) + **leaky bucket** / GCRA.  
Consistency: local POP limiters with async global reconciliation; bounded overshoot OK.

Fail mode:

- **Fail closed** for expensive/mutation routes when limiter down.  
- **Fail open** with capacity caps for read-mostly public GETs—product choice.

### 3.6 Retries, timeouts, deadlines

```text
Client deadline (e.g. 2s) → gateway overall timeout
  → per-upstream timeout (e.g. 200–500ms)
Retries: only if idempotent OR Idempotency-Key present
Retry budget: e.g. max 10% of traffic retries
Backoff + jitter; no retry on 400/401/403/404
Circuit breaker on upstream error rate
Hedged requests: only for read-only, carefully (cost)
```

### 3.7 Aggregation

```text
GET /v1/product-page?id=X
  parallel:
    product-svc
    pricing-svc
    inventory-svc
    reviews-svc (optional)
  compose JSON
  policy on partial failure:
    inventory fail → show "unknown stock" OR fail request
```

Rules:

- Overall deadline.  
- Bulkheads per upstream.  
- No unbounded fan-out (N≤K).  
- Prefer BFF service over giant edge Lua/plugins for complex compose.

### 3.8 Caching

| Layer | What |
|-------|------|
| CDN / POP | Public GETs, authenticated anonymizable |
| Gateway cache | Short TTL GETs with explicit Cache-Control |
| Upstream | Service-owned caches |

Cache key must include **tenant** and **anything that affects authz**.  
Mutations invalidate via TTL or event—don’t promise instant global purge at MVP.

### 3.9 Multi-tenant isolation

- Quotas in control plane.  
- Shuffle sharding of gateway workers / limiters.  
- Optional dedicated gateway fleet for whales.  
- Per-tenant dashboards and kill switches (`block_tenant`, `shed_tenant_percent`).

### 3.10 Trade-off tables

| Concern | Choice | Why |
|---------|--------|-----|
| Gateway impl | Envoy / NGINX / API GW | Proven L7 features |
| Rate limit store | Redis cluster sharded | Low latency ops |
| Auth | JWT validate at edge + key cache | Scale |
| Aggregation | BFF service | Maintainability |
| Multi-region | Active-active edge | Latency |
| Uploads | Presigned bypass | Protect gateway CPU |
| Config | Push xDS-like | Fast updates |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 Clients (Web/Mobile/Partners)
            |
            v
   +------------------+
   | DNS / Anycast    |
   +--------+---------+
            |
            v
   +------------------+     +------------------+
   | Edge POP / CDN   |---->| WAF / Bot        |
   | TLS termination  |     +------------------+
   +--------+---------+
            |
            v
   +--------------------------------------+
   | API Gateway Data Plane               |
   |  AuthN → AuthZ → RateLimit → Route   |
   |  (optional) Aggregate / Cache        |
   +----+----------+----------+-----------+
        |          |          |
        v          v          v
   Service A   Service B   Service C
   (cells)     (cells)     (cells)

   Control Plane: keys, routes, quotas, policies, canaries
        |
        v  push config (versioned)
   Data Plane fleets
```

### 4.2 Sequence: authenticated GET with cache miss

```text
Client          Gateway           AuthCache      RateLimiter     Upstream
  |-- GET ------>|                  |                |              |
  |              |-- validate JWT ->|                |              |
  |              |<-- ok/tenant ----|                |              |
  |              |-- check limit ------------------->|              |
  |              |<-- allow snip -------------------|              |
  |              |-- cache miss                                   |
  |              |-- GET (identity hdrs) ------------------------>|
  |              |<-- 200 ----------------------------------------|
  |              |-- store cache                                  |
  |<-- 200 ------|                                                |
```

### 4.3 Sequence: aggregation with partial failure

```text
Gateway                Product   Price    Inventory  Reviews
  |-- parallel ---------->|        |         |         |
  |<-- 200 ---------------|        |         |         |
  |<-- 200 ------------------------|         |         |
  |           timeout ------------------------X        |
  |<-- 200 --------------------------------------------|
  | compose: stock=UNKNOWN (policy)
  |-- 200 to client
```

### 4.4 Rate limit hierarchical

```text
Request → POP local token bucket (fast)
       → if near limit, check regional shard
       → async adjust global tenant budget
Overshoot bounded by POP capacity slices
```

### 4.5 Multi-region / cells

```text
          +--------- Global DNS / Traffic Dir ---------+
          |                                            |
          v                                            v
     Region US-EAST                               Region EU
   Edge + Gateway cell                          Edge + Gateway cell
          |                                            |
          v                                            v
   Local origins /                                Local origins /
   home services                                  home services

Tenant data residency may pin origin region; edge still global
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Failure modes & mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Gateway fleet crash | Client errors | Multi-AZ autoscaling; health checks |
| Auth store down | Cannot validate keys | Local cache; short fail policy |
| Rate limiter down | Overload risk | Fail-closed on mutations; cached last-limits |
| Upstream brownout | Latency blowups | Circuit breaker; shed; stale cache |
| Retry storm | Melts origins | Retry budgets; client education |
| Bad config push | Mass 404/401 | Canary config; instant rollback; generations |
| Hot tenant | Noisy neighbor | Quotas; isolation pool |
| Aggregation dependency down | Partial outage | Bulkheads; degrade gracefully |
| Cert expiry | TLS failure | Automated renew; pages on expiry |
| Header injection | Security incident | Strip hop-by-hop; sign internal identity |

#### 5.1.2 Consistency model

- Route/config: **eventually consistent** with monotonic `config_generation`.  
- Rate limits: **weakly consistent**; optimize for performance with bounded overshoot.  
- Auth revocation: **bounded staleness** (TTL + emergency push).  
- Aggregation: **per-request** freshness; no cross-service transactions in gateway.

#### 5.1.3 Retries vs exactly-once

Gateway never provides exactly-once mutations. It provides:

1. Propagation of `Idempotency-Key`.  
2. Retries only when safe.  
3. At-most-once by default for non-idempotent POST without key.

#### 5.1.4 Amazon ownership themes

- **Customer Impact:** Distinguish retail browse (degrade OK) vs checkout/payments (fail closed carefully).  
- **Security:** Gateway is a high-value target—WAF, least privilege, no logging secrets.  
- **Operational excellence:** Config rollback in minutes; game days for dependency brownouts.  
- **Frugality:** Aggregation fan-out is a cost multiplier—budgets and caching.  
- **Ownership:** Clear DRI for route policies vs upstream SLOs.

### 5.2 Scalability

#### 5.2.1 Progressive scale changes

| Scale | Change |
|-------|--------|
| 1× | Single region ALB + gateway fleet + Redis limiter + JWT auth |
| 10× | Shard limiters; auth caches; pool tuning; WAF |
| 100× | Multi-region edge; cells; hierarchical limits; BFF split |
| 1,000× | Global POPs; anycast; origin shield; per-tenant isolation; push config fabric |

#### 5.2.2 Sharding keys

| Component | Key |
|-----------|-----|
| Rate limit | `hash(tenant_id, route_id)` |
| Auth key cache | `key_id` |
| Gateway workers | Stateless; any |
| Aggregation BFF | By API experience |
| Control plane | Tenant / route partitions |

#### 5.2.3 Aggregation at high scale

- Cap fan-out.  
- Prefer precomputed materialized “page models” for hottest SKUs.  
- Collapse duplicate upstream calls within one request.  
- Use hedging only with strict cost controls.

#### 5.2.4 Multi-tenant fairness

- Per-tenant RPS and concurrency.  
- Weighted fair sharing at edge when overloaded (shed lowest priority tenants first).  
- Marketplace sellers vs internal—separate classes if needed.

### 5.3 Maintainability

#### 5.3.1 Configuration as data

Routes, weights, limits, auth requirements—declarative, versioned, reviewed (CI policy lint).

#### 5.3.2 Control plane vs data plane

| Plane | Responsibility |
|-------|----------------|
| Control | Keys, routes, quotas, canary % |
| Data | Per-request path; no DB chatty calls |

Push config via xDS / S3+notify / AppConfig patterns; data plane never blocks on control plane QPS.

#### 5.3.3 Observability

| Signal | Use |
|--------|-----|
| RPS, latency, error by route | SLO |
| Limit rejects by tenant | Abuse / bad clients |
| Upstream latency breakdown | Aggregation debug |
| Retry count / budget burn | Meltdown early warning |
| Config generation skew | Bad push |
| Cache hit ratio | Cost/perf |

Propagate `x-amzn-requestid` / `traceparent`. RED + USE metrics.

#### 5.3.4 Testing & game days

- Contract tests for routes.  
- Load tests with hot tenant.  
- Chaos: kill limiter shard, kill one upstream in aggregation.  
- Canary config then blast radius limited.

#### 5.3.5 Security & compliance

- TLS 1.2+; HSTS.  
- WAF rules; bot management.  
- Request size limits; JSON depth limits.  
- Strip internal headers from external clients.  
- Sign/mint internal service identity.  
- PII redaction in access logs; sampling.

### 5.4 Progressive scale deep dive

**MVP:** Regional gateway, JWT+API keys, Redis token buckets, retries for GET, simple aggregation BFF for 1–2 pages, CloudWatch/X-Ray.  

**10×:** Shard Redis; add CDN for public GETs; connection pools; per-route concurrency; WAF.  

**100×:** Multi-region active-active edge; tenant cells; hierarchical rate limits; config canaries; origin brownout playbooks.  

**1,000×:** POP-local decisions; global budget reconciler; dedicated whale fleets; precomputed aggregation for top traffic; formal API marketplace quotas.

### 5.5 Idempotency & client collaboration

Document for clients:

- Use idempotency keys on POSTs that create resources.  
- Honor `Retry-After`.  
- Exponential backoff.  
- Treat 409/425 semantics explicitly.  
Gateway should not invent body dedupe for arbitrary POSTs.

### 5.6 Fail-open vs fail-closed matrix

| System down | Browse GET | Search (expensive) | Checkout POST | Admin API |
|-------------|------------|--------------------|---------------|-----------|
| Rate limiter | open+cap | closed | closed | closed |
| Auth cache miss | try remote; fail closed | closed | closed | closed |
| Reviews upstream | degrade | n/a | n/a | n/a |
| Price upstream | fail closed for buy paths | n/a | closed | n/a |

### 5.7 Deal-breaker gallery

| Deal-breaker | Fix |
|--------------|-----|
| Per-request DB auth lookup | Cache credentials |
| Global Redis single shard | Shard / hierarchy |
| Retry all methods | Idempotency rules |
| Unbounded aggregation | Caps + deadlines |
| Cache personalized as public | Correct Vary / keys |
| Sync control-plane calls | Push config |
| Trust client-supplied identity headers | Strip & resign |
| Log bodies by default | Sample + redact |

---

## 6. Wrap-Up

### 6.1 Key decisions

1. Thin edge gateway + optional BFF for aggregation.  
2. AuthN at edge; AuthZ via cached policies/scopes.  
3. Distributed hierarchical rate limits with explicit fail modes.  
4. Retries only when safe; propagate idempotency keys.  
5. Deadlines, bulkheads, circuit breakers for dependencies.  
6. Active-active edge; origins respect residency/cells.  
7. Config as versioned data with canary rollback.

### 6.2 Top risks

| Risk | Mitigation |
|------|------------|
| Retry / fan-out meltdown | Budgets, breakers |
| Rate-limit inconsistency abuse | Hierarchy + caps |
| Config bad push | Canary + rollback |
| Hot tenant | Isolation |
| Cache privacy bug | Key discipline |
| Observability cost | Sampling |

### 6.3 45-minute interview plan

| Minutes | Focus |
|---------|-------|
| 0–5 | Clarify gateway vs BFF; auth; aggregation needs |
| 5–12 | Estimation: RPS, bandwidth, limiter ops |
| 12–22 | HLD: edge path, auth, limit, route |
| 22–32 | Deep dive: retries, aggregation, multi-tenant |
| 32–40 | 100×/1000× POPs, hierarchy, cells |
| 40–45 | SLOs, fail-open matrix, risks |

### 6.4 60-second pitch

> “I’d build a thin, horizontally scaled API gateway that terminates TLS, authenticates and authorizes with cached credentials, enforces per-tenant hierarchical rate limits, and routes to upstream cells. Retries are restricted to idempotent traffic with budgets. Aggregation lives in a BFF with deadlines and bulkheads. We scale with multi-region POPs, push-based config, and isolation for noisy tenants—measuring customer impact per route class.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & scope

1. Gateway vs reverse proxy vs BFF—when each?  
2. What logic must never live in the gateway?  
3. When should uploads bypass the gateway?  
4. How do you version APIs without breaking clients?  
5. Public partner API vs first-party mobile API differences?

### 7.2 AuthN / AuthZ

6. JWT validation vs introspection—trade-offs?  
7. How do you rotate API keys with zero downtime?  
8. Emergency credential revocation design?  
9. How do you prevent clients from spoofing internal identity headers?  
10. SigV4 vs bearer tokens for internal services?  
11. Scope explosion—how to organize AuthZ policies?  
12. mTLS to upstreams—why?

### 7.3 Rate limiting

13. Token bucket vs sliding window vs GCRA?  
14. How much overshoot is acceptable for distributed limiters?  
15. Hierarchical POP → region → global limits.  
16. Soft limit vs hard limit UX.  
17. Rate limit by cost units (search expensive) not just RPS.  
18. Fail-open vs fail-closed when Redis is down.  
19. How do you rate-limit aggregation endpoints fairly?  
20. Hot-key tenant melts one shard—mitigations?

### 7.4 Retries & resilience

21. Which HTTP methods are retryable by default?  
22. What is a retry budget?  
23. Hedged requests—when do they hurt?  
24. Circuit breaker parameters you’d choose.  
25. How do deadlines propagate (`budget` / `timeout`)?  
26. Interaction of client retries + gateway retries + mesh retries (retry amplification).  
27. Brownout: latency high but not erroring—what do you shed?

### 7.5 Aggregation

28. Partial failure policies—examples.  
29. How do you keep aggregation p99 under control?  
30. Fan-out storms from one popular endpoint.  
31. When to precompute page models instead?  
32. GraphQL at the edge vs REST BFF?  
33. How to avoid N+1 in composed APIs?

### 7.6 Caching

34. What goes into a cache key for authenticated GET?  
35. CDN vs gateway cache vs service cache.  
36. Thundering herd on expiry—how to soft-lock?  
37. Privacy incident from mis-caching—postmortem themes.  
38. Stale-while-revalidate usefulness at gateway.

### 7.7 Multi-tenant & scale

39. Shuffle sharding for gateway fleets.  
40. Dedicated edge for marketplace whales.  
41. 50M RPS—what changes first?  
42. Control plane updates at 10K/day safely.  
43. Cell migration for a tenant’s API traffic.  
44. Cost model: egress vs compute vs origin.

### 7.8 Multi-region

45. Active-active edge with regional data residency.  
46. Sticky sessions—avoid or embrace?  
47. Cross-region failover for origins.  
48. Global rate limits vs regional—product meaning.  
49. DNS TTLs vs anycast trade-offs.

### 7.9 Observability & ops

50. Golden signals for a gateway.  
51. How to attribute latency to auth vs limit vs upstream.  
52. Sampling strategies that still catch rare tenants.  
53. Config rollback drill.  
54. Abuse dashboard essentials.

### 7.10 Security & abuse

55. Request smuggling defenses.  
56. WAF false positives vs false negatives.  
57. Schema validation at edge—how deep?  
58. Bot management for public browse.  
59. DDoS layers (L3/L4 vs L7).  
60. SSRF risks if gateway can fetch arbitrary URLs (don’t).

### 7.11 Data & APIs

61. How do you design `429` response bodies?  
62. Idempotency-Key header semantics.  
63. Pagination through a gateway—concerns?  
64. File download streaming vs buffered.  
65. CORS handling ownership.

### 7.12 Amazon ownership

66. Checkout 5xx spike—gateway or origin? How to triage in 5 minutes.  
67. Partner API complaining of unfair throttling—how investigate?  
68. Cost explosion from aggregation—how fix without breaking UX?  
69. Who owns SLO when BFF aggregates 4 services?  
70. Kill switch design for a bad route deploy.

### 7.13 Interview traps

71. Putting business DB writes in the gateway.  
72. Claiming global strongly consistent rate limits at 50M RPS.  
73. Retrying non-idempotent POSTs by default.  
74. Caching personalized responses publicly.  
75. Synchronous control-plane dependency on every request.  
76. Unbounded fan-out aggregation.  
77. Ignoring retry amplification across layers.  
78. Single region “we’ll add multi-region later” without sticky state plan.

### 7.14 Misc deep cuts

79. HTTP/2 / HTTP/3 benefits at the edge.  
80. Connection pool unfairness under many upstreams.  
81. Adaptive concurrency limits (AIMD / Vegas-like).  
82. Comparing Amazon API Gateway vs Envoy self-managed.  
83. Long-polling / SSE through gateway—timeouts.  
84. gRPC-web / REST coexistence.  
85. Quotas as product packaging (tiers).

---

## 8. Appendices

### 8.1 Route config sketch

```text
Route {
  id, match: {host, path_prefix, methods},
  auth: {types: [API_KEY, JWT], scopes: [...]},
  rate_limit: {units: RPS, steady, burst},
  retry: {max, on_statuses, idempotent_only},
  timeout_ms, deadline_ms,
  cache: {ttl_ms, vary_headers},
  upstream: {cluster, weight_overrides},
  aggregation: null | {steps: [...], partial_policy},
  fail_limiter_open: false
}
```

### 8.2 Request context headers (internal)

```text
x-request-id
x-tenant-id
x-principal
x-deadline-ms
x-traceparent
x-gateway-config-gen
x-authenticated-by  (signature / HMAC over identity tuple)
```

### 8.3 API checklist (control plane)

| API | Purpose |
|-----|---------|
| Create API key | Tenant credential |
| Rotate / revoke key | Security |
| Upsert route | Config |
| Set quota | Product packaging |
| Canary weight | Deploy |
| Block tenant | Abuse |
| Usage query | Billing / DX |

### 8.4 Rate limit algorithm (sketch)

```text
function Allow(key, cost=1):
  state = Redis.GET(key) or full_bucket
  now = server_time
  refill = (now - state.ts) * rate
  tokens = min(capacity, state.tokens + refill)
  if tokens < cost: return Deny(retry_after)
  tokens -= cost
  Redis.SET(key, {tokens, ts: now})
  return Allow
```

Hierarchical: local POP allows within slice; async debit global.

### 8.5 Aggregation pseudocode

```text
function ProductPage(id, deadline):
  ctx = budget(deadline)
  futs = parallel[
    call(product, id, ctx.child(100ms)),
    call(price, id, ctx.child(100ms)),
    call(inventory, id, ctx.child(80ms)),
    call(reviews, id, ctx.child(120ms), optional=true)
  ]
  return compose(futs, policy=DEGRADE_INVENTORY_AND_REVIEWS)
```

### 8.6 Fail-open matrix (copy for whiteboard)

See §5.6 — memorize browse vs checkout differences.

### 8.7 Glossary

| Term | Definition |
|------|------------|
| BFF | Backend for frontend — experience aggregation |
| Bulkhead | Isolation of resources per dependency |
| Retry budget | Cap on retry traffic fraction |
| xDS | Dynamic config push model (Envoy) |
| Origin shield | Intermediate cache protecting origins |
| Shuffle shard | Map tenant to random subset of instances |
| Brownout | Overload showing high latency before hard errors |

### 8.8 Progressive scale checklist

- [ ] Split edge RPS vs origin RPS vs limiter ops  
- [ ] Auth caching plan  
- [ ] Hierarchical rate limits  
- [ ] Retry amplification story  
- [ ] Aggregation deadlines/bulkheads  
- [ ] Cache key privacy  
- [ ] Config canary/rollback  
- [ ] Multi-region edge  
- [ ] Whale isolation  
- [ ] Fail-open/closed matrix  

### 8.9 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Gateway availability (excl. origin) | 99.99% |
| Gateway overhead p99 | < 40ms in-region |
| Incorrect auth allow | ≈ 0 (Sev) |
| Limit false deny | low; monitored |
| Config rollback time | < 5 minutes |

### 8.10 Operator runbooks (titles)

- Upstream brownout for cluster X  
- Rate-limit Redis shard outage  
- Auth JWKS refresh failure  
- Bad config generation  
- Hot tenant isolation  
- Retry budget exhaustion  
- TLS cert expiry approaching  

### 8.11 Interview “say this” summary

> Thin edge, cached auth, hierarchical limits, safe retries, BFF aggregation with deadlines, push config, POP scale, tenant isolation, explicit fail-open matrix.

### 8.12 Worked scale example (100×)

```text
Baseline 50K RPS → 5M RPS
Assume 40% cacheable at CDN → origin 3M RPS
Aggregation on 20% of origin-bound @ 3 upstreams → extra origin load
Limiter keys hot ~100K → sharded Redis / local POP buckets
Gateway instances: if 2K RPS/instance → ~2,500 instances globally + headroom
```

### 8.13 Worked scale example (1,000×)

```text
50M RPS edge → must be POP-local decisions
Global strongly consistent limits impossible per request
Use: local admission + async global budgets
Precompute hottest aggregations
Dedicated fleets for top tenants
```

### 8.14 Security checklist

- [ ] External identity headers stripped  
- [ ] Internal identity signed  
- [ ] Body size limits  
- [ ] WAF enabled  
- [ ] Secrets not logged  
- [ ] Key rotation tested  
- [ ] mTLS to sensitive origins  
- [ ] SSRF egress deny by default  

### 8.15 Reliability test plan

1. Kill one AZ of gateways — traffic shifts, no auth outage.  
2. Redis limiter shard down — mutations fail closed; reads per policy.  
3. Aggregation dependency 100% timeout — degrade per policy, no thread exhaustion.  
4. Canary bad route — auto rollback on error rate.  
5. Hot tenant 20× traffic — others unaffected within SLO.

### 8.16 Comparison map

| Tech | Role |
|------|------|
| Amazon API Gateway | Managed edge |
| CloudFront | CDN / POP |
| ALB | L7 regional |
| Envoy / App Mesh | Data plane / mesh |
| Cognito / IAM | Auth |
| WAF Shield | Abuse / DDoS |
| ElastiCache | Limiters / caches |

### 8.17 Final trap table

| Trap | Correction |
|------|------------|
| “Strongly consistent global RPS limit” | Hierarchical approximate limits |
| “Gateway will orchestrate transactions” | Services own consistency |
| “Retry everything” | Idempotency + budgets |
| “Cache all GETs” | Authz-aware keys |
| “One region is fine” | Edge latency & DR story |

### 8.18 Amazon bar reminders

- Speak customer impact classes (browse vs buy).  
- Quantify fan-out and retry amplification.  
- Own config rollback.  
- Be explicit on fail-open/closed.  
- Separate control plane from data plane.

---

*End of document — High-Volume REST API Gateway / Client-Service Layer (Amazon SDE III)*
