# System Design: Multi-Server API Platform

> **Focus areas:** Stateless APIs · Sticky sessions · Service discovery · Load balancing · Shared-state consistency · AuthN/Z · Rate limits · Idempotency · Multi-AZ  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit consistency choices, honest sticky-session deal-breakers, resolved ownership of shared state

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

Goal: **bound “API across multiple servers”**—what must be horizontally scalable, which requests may be sticky, and how shared state stays correct under multi-AZ failure.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What does the API do? | Internal/product REST+gRPC platform used by many NVIDIA services (jobs, registry metadata, telemetry queries) | Generic multi-tenant API plane; domain handlers pluggable |
| F2 | Clients? | Services, CLIs, web UIs, partner integrations | mTLS + OAuth2/OIDC; API keys for machine clients |
| F3 | Sync vs async? | Mostly sync request/response; long ops return `202` + job id | Separate request path from async work plane |
| F4 | Session needs? | Prefer **stateless**; rare WebSocket / progressive upload may need affinity | Sticky as **exception**, not default |
| F5 | Auth? | User + service identity; RBAC/ABAC on resources | Auth at edge + service-level authz |
| F6 | Rate limits? | Per principal, per route, per tenant; burst + sustained | Distributed token buckets; fail policy explicit |
| F7 | Idempotency? | Required for mutating POSTs that can be retried | Idempotency-Key store with TTL |
| F8 | Shared state? | Sessions (rare), caches, quotas, feature flags, config | Externalize; never rely on local heap for truth |
| F9 | Discovery? | Dynamic instances in K8s / VMs; rolling deploys | Service registry + health checks |
| F10 | Multi-AZ? | Required; survive single AZ loss | Stateless replicas in ≥3 AZs; data plane HA |
| F11 | Observability? | Request traces, RED metrics, audit of mutations | Correlation ids end-to-end |
| F12 | Versioning? | URI or header versioning; deprecate gracefully | Gateway routes by version; canaries |

**MVP functional scope (lock with interviewer):**

1. Horizontally scaled **stateless** API servers behind a load balancer.  
2. **AuthN** (JWT / mTLS) + **AuthZ** checks per request.  
3. **Rate limiting** per API key / user / tenant.  
4. **Idempotent** mutating endpoints via `Idempotency-Key`.  
5. **Service discovery** + health-based LB; graceful drain on deploy.  
6. Optional **sticky sessions** only for explicitly marked routes (e.g. upload resume).  
7. Multi-AZ active-active API tier; shared stores with clear consistency model.  
8. Structured logs, metrics, distributed tracing.

**Out of MVP (explicitly defer):**

- Perfect global active-active writes for strongly consistent domain entities without home-region  
- Client-specific SDKs for every language  
- GraphQL federation (mention as Phase 2)  
- Full multi-region strong consistency for all resources  
- Custom L7 WAF rules beyond baseline

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Interactive APIs | p50 < 20ms, p99 < 100ms in-region excluding handler work |
| N2 | Availability | Multi-AZ | 99.9%+ monthly for API edge; degrade non-critical features first |
| N3 | Consistency | Per-resource clarity | Strong for authz/quota mutations; eventual OK for caches/flags |
| N4 | Throughput | See scale table | Split read/write/auth/rate-limit paths |
| N5 | Deploy safety | Zero-downtime | Rolling + readiness; connection drain |
| N6 | Security | Least privilege | Short-lived tokens; audit mutations |
| N7 | Multi-region | DR first; optional read replicas | Home region for authoritative writes unless stated |
| N8 | Idempotency window | Retries within hours | e.g. 24h key retention |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client → LB → healthy API replica → auth → rate limit → handler → DB/cache → response.  
2. Mutating POST with `Idempotency-Key` → first call commits; replay returns same result.  
3. Rolling deploy: new pods Ready → LB adds; old pods drain connections → terminate.  
4. AZ failure: remaining AZs absorb traffic; in-flight retries succeed via idempotency.  
5. Sticky upload: client pinned via cookie/consistent hash for duration of session.  
6. Long job: `POST` returns `202` + `Location`; client polls status on any replica.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Instance dies mid-request | Client retries; idempotent mutations safe; non-idempotent must not double-apply |
| LB sends to draining pod | Readiness false → no new traffic; finish in-flight within grace |
| Auth service slow | Cache JWKS / introspect with TTL; fail closed on critical paths |
| Rate-limit store partition | Document fail-open vs fail-closed; prefer fail-closed for abuse-sensitive routes |
| Sticky target dies | Re-pin to new instance; session state must be reconstructable from shared store |
| Split-brain cache | Never use local cache as sole authz truth |
| Clock skew | Token `nbf`/`exp` with skew tolerance; prefer short TTLs |
| Thundering herd on cold cache | Singleflight / request coalescing |
| Duplicate deploy two versions | Canary %; schema backward compatible |
| Cross-AZ latency spike | Prefer same-AZ data when possible; measure tax |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak RPS (all routes) | 5K | 50K | 500K | 5M |
| Peak write RPS | 1K | 10K | 100K | 1M |
| Concurrent connections | 50K | 500K | 5M | 50M |
| API instances | 20 | 200 | 2,000 | 20,000 |
| Tenants / principals | 1K | 10K | 100K | 1M |
| Distinct routes | 50 | 80 | 120 | 200 |
| Auth validations /s | 5K | 50K | 500K | 5M |
| Rate-limit checks /s | 5K | 50K | 500K | 5M |
| Idempotency lookups /s | 500 | 5K | 50K | 500K |
| AZs | 3 | 3 | 3–4 | 3–4 / multi-region cells |
| Payload avg | 2 KB | 2 KB | 4 KB | 4–8 KB |
| WebSocket / sticky sessions | 1K | 10K | 100K | 1M |

**What each jump forces:**

- **10×:** Horizontal API replicas; Redis cluster for rate limits + idempotency; connection pooling; JWKS cache.  
- **100×:** Shard rate-limit / idempotency keys; per-tenant isolation; edge gateway tier separate from app; cell/shard of data.  
- **1,000×:** Regional cells; hierarchical rate limits; local auth material; avoid global sticky; Anycast/edge termination.

### 1.5 Etc. (Constraints & Assumptions)

- Prefer **stateless request handlers**; any in-memory session is a smell unless justified.  
- Shared mutable state lives in **Redis / DB / object store**, not process memory.  
- Sticky sessions are for **affinity**, not for storing authoritative business state on one box.  
- Single primary cloud region for MVP writes; multi-AZ mandatory.  
- NVIDIA-flavored example: internal “Compute API” used by job submission, model metadata, and quota services—but design is general multi-server API.

**Scope statement:**

> Design a multi-AZ, horizontally scaled API platform that is stateless by default, supports optional sticky affinity, performs auth and distributed rate limiting, provides idempotent mutations, discovers healthy backends dynamically, and keeps shared-state consistency correct as load grows 10× → 100× → 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Read APIs | 4K RPS | 4M RPS | Cacheable where safe |
| Write APIs | 1K RPS | 1M RPS | Idempotency + durable commit |
| Auth validate | 5K /s | 5M /s | Local JWT verify dominates |
| Rate-limit check | 5K /s | 5M /s | Redis / local token bucket |
| Idempotency | 500 /s | 500K /s | Only mutating retries-prone |
| Health/discover | low | higher | Control plane, not data path |

**Critical insight:** At 1,000×, **auth + rate-limit QPS ≈ request QPS**. If every request does a remote round-trip for both, you invent a second API’s worth of latency and load. Localize JWT verification; shard rate-limit state; batch where possible.

### 2.2 Bandwidth

```text
Baseline: 5K RPS × 2 KB req ≈ 10 MB/s ingress
         5K RPS × 4 KB resp ≈ 20 MB/s egress

1,000×: 5M RPS × 2 KB ≈ 10 GB/s ingress
        5M RPS × 4 KB ≈ 20 GB/s egress
→ edge/L7 termination + regional cells; not one regional ALB mythically handling all
```

### 2.3 Instance math

```text
Assume one instance sustains 250 RPS at p99 SLO (CPU + handler)
Baseline 5K RPS → 5K/250 = 20 instances (matches table)
+ 50% headroom for AZ loss: ~30 provisioned, spread across 3 AZs (~10/AZ)

1,000×: 5M/250 = 20,000 instances → must be multi-cell; autoscaling by RPS/CPU/p99
```

### 2.4 Redis / rate-limit store

```text
Token bucket key ~64–128 B + overhead
1M active principals × 128 B ≈ 128 MB (tiny)
QPS is the issue, not bytes:
5M checks/s → shard Redis; pipeline; or hierarchical local+global buckets
```

### 2.5 Idempotency store

```text
Record: key, response hash/body ref, status, expiry ≈ 0.5–2 KB
Retention 24h
Baseline writes 500/s × 86400 × 1 KB ≈ 43 GB/day worst if all unique
Usually much less (only mutating); at 1000× need TTL + sharding + store body in object store if large
```

### 2.6 Multi-AZ latency tax

```text
Same-AZ Redis: ~0.2–0.5 ms
Cross-AZ Redis: ~1–2 ms
Cross-AZ DB sync replica lag: ms–seconds depending on setup
Design: prefer co-locating chatty dependencies; accept cross-AZ for HA writes to quorum
```

### 2.7 Critical bottlenecks (rank ordered)

1. **Remote auth introspection on every request**  
2. **Single Redis for global rate limits**  
3. **Sticky sessions concentrating load on hot instances**  
4. **Idempotency store as unsharded primary**  
5. **Chatty cross-AZ dependency calls in request path**  
6. **Connection storms on deploy / AZ failover**  

---

## 3. High-Level Design

### 3.1 Core principle: stateless by default

```text
Request arrives with all needed identity + idempotency context
Any healthy replica in any AZ can serve it
Authoritative state: external stores (DB, object, Redis)
Local memory: caches with TTL + stampede control only
```

**Deal-breaker:** “We store logged-in sessions only in server memory and use sticky LB forever.”

### 3.2 Options: load balancing

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. L4 round-robin / least-conn | Simple, fast | No HTTP awareness | Need header routing / gRPC careful drain |
| B. L7 gateway (Envoy/ALB/NGINX) | Retries, auth hooks, canary | Extra hop | Treating it as app server |
| C. Client-side LB (RPC) | Low latency, elegant | Needs discovery + hedged retries | Clients outdated without library |
| D. Consistent hash sticky | Affinity for uploads/WS | Hot keys; failover complexity | Using sticky to hide missing shared state |

**Chosen path:**

- **Edge L7 gateway** for public/partner traffic (TLS, WAF lite, canary).  
- **Internal mesh / client LB** for service-to-service.  
- **Sticky only** on labeled routes via cookie or consistent hash of session id—with state in Redis.

### 3.3 Service discovery & health

```text
Registry (K8s Endpoints / Consul / internal):
  instance → {ip, port, zone, version, weight, ready}

LB watches registry:
  Ready=true  → in pool
  Ready=false → drain (no new); keep until connections done or timeout
  Health fail → eject (outlier detection)
```

**Readiness vs liveness:**

| Probe | Meaning |
|-------|---------|
| Liveness | Process deadlocked/crashed → restart |
| Readiness | Can accept traffic (deps OK enough) → LB inclusion |
| Startup | Slow boot; don’t kill early |

**Deal-breaker:** Only liveness; kill pods that are slow to warm → restart loops under load.

### 3.4 Sticky sessions — when and how

| Use case | Affinity OK? | Where state lives |
|----------|--------------|-------------------|
| Pure REST CRUD | No | N/A |
| Multipart upload resume | Optional | Upload parts in object store; affinity reduces redirect churn |
| WebSocket fanout | Often yes | Connection on instance; broadcast via Redis/NATS |
| Server-side session shopping cart | Prefer no | Redis session store; any instance |
| Legacy app with in-memory session | Migrate | Externalize ASAP |

**Mechanisms:**

1. **Cookie stickiness** (`AWSALB`, `INGRESSCOOKIE`) — simple; opaque to app.  
2. **Consistent hash on `session_id` / `connection_id`** — mesh-friendly.  
3. **Explicit binding service** — register `session → instance` in Redis with TTL.

**Failover rule:** If sticky target unhealthy, rebind; client must tolerate replay; server must not require local-only memory.

**Deal-breaker:** Sticky as substitute for a session store.

### 3.5 Shared state consistency

| State | Consistency | Store | Notes |
|-------|-------------|-------|-------|
| User / resource records | Strong (per key) | Primary DB / Spanner-like | Home shard |
| Sessions | Strong enough (read-your-writes) | Redis with replication | Short TTL |
| Rate-limit counters | Approximate OK | Redis cluster | Slight overshoot acceptable |
| Idempotency records | Strong per key | Redis/DB with uniqueness | Fence duplicates |
| Feature flags | Eventual | CDN/config push | Stale seconds OK |
| Auth JWKS | Eventual | Local cache + refresh | Rotate carefully |

**CAP phrasing for interview:** For a given resource key, pick single-writer / consensus path; caches are forever secondary.

### 3.6 AuthN / AuthZ

```text
Edge:
  - Terminate TLS
  - Validate JWT (local JWKS) or mTLS
  - Attach trusted identity headers to mesh (or use SPIFFE)

Service:
  - Re-validate or trust mesh identity (document trust boundary)
  - AuthZ: RBAC/ABAC on resource; never trust client-supplied tenant_id alone
```

**Patterns:**

| Pattern | Use |
|---------|-----|
| JWT local verify | Human & service tokens; scalable |
| Token introspection | Opaque tokens; cache aggressively |
| mTLS / SPIFFE | Service-to-service |
| API keys | Simple machine clients; hash at rest; scoped |

**Deal-breaker:** Trusting `X-User-Id` from the public internet without gateway signing/stripping.

### 3.7 Rate limiting

| Approach | Pros | Cons |
|----------|------|------|
| Local token bucket | Fast | Inaccurate across N instances |
| Central Redis | Accurate | Latency + hotspot |
| Hierarchical (local + global) | Best of both | Complexity |
| Gateway quotas | Protects origin | Coarse |

**Chosen:** Hierarchical — each instance allows burst locally; periodically syncs / checks global shard for tenant.

**Dimensions:** `tenant`, `principal`, `route_class`, `IP` (abuse).

**Fail policy:** Abuse/payment routes **fail-closed**; read-mostly internal **fail-open** with alert—state explicitly.

### 3.8 Idempotency

```text
Client: Idempotency-Key: <uuid>
Server:
  1. Lookup (tenant, key, route)
  2. If in-progress → 409 Conflict or wait (choose + document)
  3. If completed → return stored response (or body ref)
  4. Else begin: store fingerprint of request; execute; store response; commit
```

**Fingerprint:** hash of canonical request body + path so key reuse with different body → `422`.

**Deal-breaker:** Claiming idempotency while only deduping in local memory of one replica.

### 3.9 Multi-AZ design

```text
AZ-a: API × N | AZ-b: API × N | AZ-c: API × N
         \         |         /
          \        |        /
        Regional LB / Anycast DNS
                 |
     Data: multi-AZ Redis + multi-AZ DB (sync or quorum)
```

**On AZ loss:** LB health removes bad targets; autoscaler fills other AZs; in-flight clients retry with backoff + jitter + idempotency.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Default session | Stateless JWT | Scale horizontally | Sticky in-memory sessions |
| Rate limit | Hierarchical buckets | Accuracy + speed | Pure local only at 100× |
| Idempotency | Shared store + TTL | Correct retries | “Clients won’t retry” |
| Discovery | Ready probes + outlier eject | Safe deploys | DNS TTL only, no drain |
| Sticky | Exception routes | WS/upload | Sticky for all traffic |
| Multi-region writes | Home cell | Avoid dual writers | Active-active without CRDT/conflict story |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
                     +---------------------------+
 Clients / SDKs ---> | Edge Gateway (L7)         |
                     | TLS, WAF lite, canary,    |
                     | JWT verify, coarse RL     |
                     +-------------+-------------+
                                   |
                 +-----------------+-----------------+
                 |                                   |
                 v                                   v
        +----------------+                  +----------------+
        | API Replicas   |  (stateless)     | Sticky pool    |
        | AZ-a/b/c       |                  | (WS / upload)  |
        +--------+-------+                  +--------+-------+
                 |                                   |
      +----------+----------+                        |
      |          |          |                        |
      v          v          v                        v
 Idempotency   RateLimit   AuthZ/Config          Session/PubSub
   Store        Store       + Feature flags         (Redis)
      |          |          |
      +----------+----------+
                 |
                 v
        +------------------+
        | Domain services  |
        | DB / object / Q  |
        +------------------+
```

### 4.2 Request path sequence

```text
Client          Gateway           API Replica        Redis/DB
  |                |                   |                |
  |-- HTTPS ------>|                   |                |
  |                |-- verify JWT ---->|                |
  |                |-- coarse RL ----->|                |
  |                |-- forward ------->|                |
  |                |                   |-- fine RL ---->|
  |                |                   |-- idempotency->|
  |                |                   |-- authz/data ->|
  |                |                   |<- result ------|
  |<- response ----|<------------------|                |
```

### 4.3 Sticky WebSocket

```text
Client → Gateway (hash conn_id) → Instance I1
I1 SUB Redis channel tenant:123
Other writers PUB Redis → I1 → Client

If I1 dies:
  Client reconnects → hash to I2
  I2 SUB same channels; state from Redis (not from I1 memory)
```

### 4.4 Deploy / drain

```text
t0: mark instance Ready=false
t1: LB stops new conns; existing finish
t2: idle timeout / max drain 30–60s
t3: SIGTERM → app closes listeners → exit
t4: deregister from discovery
```

### 4.5 Multi-AZ failover

```text
Before: traffic spread a/b/c
AZ-a fails:
  health checks fail → pool = b+c
  scale out b+c
  Redis/DB continue via remaining replicas / quorum
Clients: retry transient 5xx/timeouts with idempotency keys
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Any Ready replica can serve non-sticky requests** without local prior state.  
2. **Mutating retries** with same Idempotency-Key do not double-apply effects.  
3. **AuthZ decisions** never rely solely on untrusted client headers.  
4. **Drain before kill:** readiness false precedes SIGTERM.  
5. **Sticky affinity never owns sole copy** of business state.  
6. **Rate-limit fail policy** is explicit per route class.

**Failure modes & mitigations**

| Failure | Mitigation |
|---------|------------|
| Instance crash | LB eject; client retry; idempotency |
| Redis blip | Local stale JWT OK; RL fail policy; idempotency retry careful |
| DB primary failover | Connection pool retry; backoff; fencing on writers |
| AZ loss | N+1 capacity; multi-AZ data |
| Bad canary | Automatic rollback on error-rate / p99 |
| Replay attack | Short-lived tokens; mTLS; nonce where needed |

**Retries**

- Gateway hedged retries only on **safe** (idempotent) requests.  
- Clients use exponential backoff + jitter; cap attempts.  
- POST without idempotency key: **do not** auto-retry at gateway.

### 5.2 Scalability

**Progressive evolution**

| Scale | Architecture |
|-------|--------------|
| 1× | 3 AZ API Deployment + one Redis + one DB; JWT local verify |
| 10× | Autoscale on CPU/RPS/p99; Redis Cluster; connection pools; JWKS cache |
| 100× | Shard RL/idempotency; gateway tier; tenant cells for domain data; outlier detection |
| 1000× | Regional edge; cell-based API+data; hierarchical RL; avoid global sticky maps |

**Hot-key mitigation**

- Tenant with huge RPS: dedicated RL shard + fair share.  
- Sticky hash hot session: rare; break affinity periodically for WS via rebalance if needed.  
- Celebrity read keys: local cache + singleflight + CDN for public GETs.

**Connection scaling**

```text
50M concurrent at 1000×:
  Prefer HTTP/2 / gRPC multiplexing
  Edge terminates; keep backend conns pooled
  WebSocket: separate pool + horizontal instances; Redis fanout
```

### 5.3 Maintainability

- **API versioning:** `/v1` freeze; `/v2` additive; sunset headers.  
- **Contract tests** between gateway routes and handlers.  
- **Schema migrations** expand/contract; never break old clients mid-canary.  
- **Feature flags** for risky path changes.  
- **Chaos:** kill AZ, kill Redis primary, blackhole auth JWKS briefly.

**Observability (must-have)**

- RED: rate, errors, duration per route/tenant/version  
- Saturation: pool usage, GC, Redis hit rate  
- Trace: `trace_id` across gateway → API → deps  
- Audit: who mutated what  

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× — correct MVP**

```text
K8s Deployment, 3 AZs, HPA
ALB/NLB + Ingress
API pods: stateless handlers
Postgres primary multi-AZ
Redis for sessions/RL/idempotency
JWT verify local; JWKS fetch periodic
Sticky: Ingress cookie only on /ws and /uploads/*
```

Bottleneck first: Redis single-thread commands / hot keys; DB connections.

**10×**

- Redis Cluster; pipeline RL.  
- PgBouncer / proxy.  
- Cache JWKS + authz decisions briefly.  
- Outlier detection on gateway.  
- Load test deploy drain.

**100×**

- Split **edge gateway** service from **domain API**.  
- Idempotency bodies → object storage pointers.  
- Per-tenant shuffle shards for domain DB.  
- Hierarchical RL: in-process + Redis shard.  
- Cell: `tenant → cell`, gateway routes by directory.

**1000×**

```text
Global DNS / Anycast → regional edges
Region cell: gateway + API + data
Cross-region: async replication for reads; home-cell writes
No global sticky registry
Auth material localized (regional JWKS)
RL: local → cell → regional hierarchy
```

### 5.5 Consistency of shared state (patterns)

| Pattern | Example |
|---------|---------|
| Singleflight | Collapse stampede on cache miss |
| Versioned cache | `etag` / `resource_version`; conditional requests |
| Outbox | Domain write + event atomically |
| Read-your-writes | Sticky read to primary briefly after write, or sync token |
| Lease / fencing | Leader tasks, not request path usually |

**Session store example**

```text
SET session:{id} {json} EX 3600
API replicas all read/write Redis
Sticky optional for WS only
```

### 5.6 Auth deep dive

```text
Access token (JWT) claims:
  sub, tenant_id, scopes[], exp, iat, jti
Verify: signature via JWKS, exp, audience, issuer
AuthZ: scopes ∩ resource ACL

Rotation:
  publish new JWKS key
  dual-accept old+new for overlap window
  revoke via short TTL or denylist for jti (expensive—use sparingly)
```

**Service identity:** mTLS SPIFFE IDs; map to internal principal; still apply authz.

### 5.7 Rate-limit algorithms

| Algorithm | When |
|-----------|------|
| Token bucket | Bursts allowed |
| Sliding window log | Precise; heavier |
| Fixed window | Simple; boundary burst |
| GCRA / leaky | Smooth |

**Multi-dimensional decision order:** IP ban → API key invalid → tenant quota → route quota → principal quota.

### 5.8 Idempotency races

```text
Two concurrent first requests same key:
  Use SET key NX EX ... = "in_progress"
  Winner executes
  Loser sees in_progress → 409 or blocking wait with timeout
  Winner SETs final response
Never execute twice without distributed lock/NX
```

### 5.9 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| In-memory sessions + sticky forever | AZ death loses sessions; hot instances |
| Gateway retries all POSTs | Double charges / double submits |
| Global single Redis at 5M RPS | Hotspot melt |
| Auth introspection every call | Latency + coupled outage |
| No readiness drain | 5xx storms on deploy |
| Active-active dual writers | Conflicting resource versions |
| Local-only rate limits | N× over-limit across fleet |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Default | Stateless replicas multi-AZ |
| Sticky | Exception for WS/upload; state still external |
| Auth | Local JWT/mTLS; authz in service |
| Rate limit | Hierarchical local + sharded Redis |
| Idempotency | Shared store with NX + TTL |
| Discovery | Readiness + outlier ejection |
| Multi-region | Home cell for authoritative writes |

### 6.2 Top risks

1. Hidden sticky dependence on local memory  
2. Non-idempotent mutations + aggressive retries  
3. Rate-limit store as SPOF without policy  
4. Cross-AZ chatty path blowing p99  
5. Trust-boundary mistakes on identity headers  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Clarify: stateless vs sticky, multi-AZ, auth, idempotency |
| 5–12 | HLD: gateway, replicas, stores |
| 12–22 | Discovery, LB, drain, sticky exceptions |
| 22–32 | Auth, RL, idempotency, consistency |
| 32–40 | Scale 10×/100×/1000× + AZ failure |
| 40–45 | Trade-offs + wrap |

---

## 7. Deeper / Related Interview Questions

### 7.1 Stateless vs sticky

**Q: When are sticky sessions justified?**  
A: Long-lived connections (WS), expensive local caches that are pure optimization, or legacy—never as sole state store.

**Q: How do you migrate off sticky sessions?**  
A: Externalize session to Redis; flip cookie affinity off; verify any instance serves correctly; then remove.

**Q: Consistent hash vs cookie stickiness?**  
A: Cookie simple at L7; consistent hash better for meshes and gRPC streams; both need rebinding on death.

### 7.2 Load balancing & discovery

**Q: L4 vs L7?**  
A: L7 for HTTP routing/canary/auth hooks; L4 for raw throughput/gRPC sometimes with careful config.

**Q: What is outlier detection?**  
A: Eject instances with elevated 5xx/latency; probe for reinclusion—stops poisoned hosts.

**Q: How does connection draining work?**  
A: Ready=false → no new conns → finish in-flight → SIGTERM → exit. Mis-order causes spikes.

**Q: Client-side LB?**  
A: Great internally with service discovery; need shared libraries, hedged retries, locality (same AZ preference).

### 7.3 Consistency

**Q: Is Redis OK for idempotency?**  
A: Yes with persistence/replication appropriate to risk; for money-like, prefer DB unique constraint + transactional outbox.

**Q: Read-your-writes after PUT?**  
A: Read primary, or return new `resource_version`, or short sticky-to-primary token.

**Q: Cache invalidation?**  
A: TTL + version; pubsub invalidation best-effort; never require perfect invalidation for authz without fallback check.

### 7.4 Auth

**Q: JWT vs opaque tokens?**  
A: JWT scales (local verify); opaque needs introspect cache; revocation easier with opaque/short JWT + denylist sparingly.

**Q: How to rotate keys?**  
A: JWKS with overlapping `kid` acceptance window.

**Q: Confused deputy?**  
A: Gateway strips inbound identity headers; only mesh-injected identity trusted.

### 7.5 Rate limits

**Q: Why are local-only limits wrong at scale?**  
A: Effective limit ≈ per-instance × N. Attackers fan out.

**Q: Exact global limits at 5M RPS?**  
A: Expensive. Hierarchical approximation with bounded overshoot is the engineering answer.

**Q: Fail-open or closed?**  
A: Product risk: payments/abuse closed; low-risk reads may open with pages alerts.

### 7.6 Idempotency

**Q: GET idempotent by definition—why keys on POST?**  
A: Clients retry after timeouts when outcome unknown; keys make POST effectively once.

**Q: What if two different bodies share a key?**  
A: Fingerprint mismatch → error; do not silently execute.

**Q: How long to retain?**  
A: Match max client retry window (24h common); store large responses by reference.

### 7.7 Multi-AZ / multi-region

**Q: Survive AZ loss?**  
A: Stateless compute in 3 AZs; data with multi-AZ quorum; capacity headroom ≥ 1 AZ.

**Q: Cross-region active-active?**  
A: Only with home-cell or CRDT/conflict story. Otherwise DR failover with fencing.

**Q: Should Redis be cross-AZ?**  
A: Yes for HA; accept latency; shard and pipeline to compensate.

### 7.8 Performance

**Q: p99 regressions from auth?**  
A: Local crypto verify; cache JWKS; avoid remote call per request.

**Q: gRPC vs REST?**  
A: gRPC for internal fanout; REST/JSON for public; both need same idempotency/auth ideas.

**Q: Avoid thundering herd on failover?**  
A: Jittered client retries; enlarge timeouts carefully; capacity buffers; cache warming.

### 7.9 Security & abuse

**Q: DDoS?**  
A: Edge absorption, IP RL, SYN cookies, challenge; protect origin with coarse gateway quotas.

**Q: Tenant isolation?**  
A: AuthZ every call; no cross-tenant IDs in paths without check; noisy-neighbor RL.

**Q: PII in logs?**  
A: Scrub tokens/bodies; structured allowlists.

### 7.10 Operations

**Q: Blue/green vs rolling?**  
A: Rolling with canary common; blue/green for big risky flips; both need drain.

**Q: Schema change with old+new servers?**  
A: Expand → migrate → delete columns; dual-read if needed.

**Q: SLOs?**  
A: Availability, gateway p99, 5xx ratio, RL false rejects, idempotency conflict rate.

### 7.11 Interview traps

**Q: “Just use sticky sessions for everything.”**  
A: Hides state bugs; creates hotspots; fails on instance death.

**Q: “Retries make APIs reliable.”**  
A: Only with idempotency and backoff; else amplify outages.

**Q: “One big Redis is fine at 5M RPS.”**  
A: Shard; hierarchical; measure.

**Q: Units:** 5M RPS × 2 KB = 10 GB/s, not 10 MB/s.

### 7.12 Comparison

**Q: API Gateway product vs custom Envoy?**  
A: Managed gateway faster MVP; custom mesh for rich internal policies—hybrid common.

**Q: Serverless vs always-on replicas?**  
A: Serverless great for spiky low-QPS; high steady RPS + sticky WS often better on containers.

### 7.13 NVIDIA-flavored angles

**Q: How does this support GPU job APIs?**  
A: Sync admit/status on this plane; heavy work async; idempotent submit; tenant quotas in RL+ledger.

**Q: Telemetry query fanout?**  
A: Read path caching; separate from write path; protect with quotas so analytics can’t melt control plane.

### 7.14 WebSocket specifics

**Q: Horizontal WS?**  
A: Pub/sub backbone; instances are connection terminals only.

**Q: Auth on WS?**  
A: Authenticate on upgrade; refresh policy; disconnect on revoke.

### 7.15 Consistency checklist say-aloud

> Shared truth in Redis/DB; API memory is cache; sticky is affinity; idempotency fences mutations; auth local; RL hierarchical; multi-AZ capacity for N-1.

---

## 8. Appendices

### 8.1 API checklist

- [ ] `Authorization` bearer / mTLS  
- [ ] `Idempotency-Key` on mutating POSTs  
- [ ] `X-Request-Id` / `traceparent`  
- [ ] Standard error envelope `{code, message, details}`  
- [ ] Versioning strategy documented  
- [ ] Rate-limit response headers (`Retry-After`)  
- [ ] Pagination cursors for lists  
- [ ] `202` + status URL for long ops  

### 8.2 Headers & identity

```text
Incoming public:
  Authorization, Idempotency-Key, Content-Type

Gateway adds (internal only):
  X-Auth-Subject, X-Auth-Tenant, X-Auth-Scopes  (signed or mesh identity)
Strip any client-supplied X-Auth-* at edge
```

### 8.3 Schema sketches

```sql
-- idempotency_records
(tenant_id, key, route, request_hash,
 status, response_ref, created_at, expires_at,
 PRIMARY KEY (tenant_id, key, route))

-- api_keys
(key_id, tenant_id, key_hash, scopes[], created_at, revoked_at)

-- audit_log
(id, tenant_id, subject, action, resource, at, payload_ref)
```

### 8.4 Redis key layout

```text
rl:{tenant}:{route}:{window} → counter / token bucket hash
idem:{tenant}:{key} → {status, resp_ref, req_hash}
sess:{session_id} → session json
ws:chan:{tenant}:{topic} → pubsub channel
```

### 8.5 Gateway retry policy

| Method / safety | Retry at gateway? |
|-----------------|-------------------|
| GET/HEAD safe | Yes, limited |
| PUT/DELETE idempotent by spec | Careful yes if handler is |
| POST with Idempotency-Key | Optional retry |
| POST without key | **No** |

### 8.6 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Stateless pods 3 AZ, JWT local, Redis RL+idem, drain |
| 10× | HPA, Redis Cluster, pools, outlier eject |
| 100× | Gateway split, sharded RL/idem, tenant cells |
| 1000× | Regional cells, hierarchical RL, home-cell writes |

### 8.7 Glossary

| Term | Meaning |
|------|---------|
| Sticky session | LB affinity to same instance |
| Readiness | Eligible for new traffic |
| Idempotency-Key | Client key making mutation replay-safe |
| Hierarchical RL | Local burst + global reconcile |
| Home cell | Single-writer region for a tenant/resource |
| Outlier detection | Temporary eject of bad hosts |

### 8.8 Interview “say this” summary (60 seconds)

> Multi-AZ stateless API replicas behind an L7 gateway; JWT/mTLS verified locally; hierarchical rate limits; shared Redis/DB for sessions, idempotency, and quotas; sticky only for WS/uploads with externalized state; discovery via readiness and drain; scale by sharding stores and celling tenants—not by pinning users to one forever server.

### 8.9 Reliability test plan

1. Kill one AZ → error budget holds; retries succeed.  
2. Deploy with drain → 5xx flat.  
3. Double POST same Idempotency-Key → one effect.  
4. Redis failover → RL policy behaves as documented.  
5. Sticky target kill → WS reconnects on new instance.  

### 8.10 Observability SLOs

| SLO | Example |
|-----|---------|
| Gateway availability | 99.9% |
| p99 latency (auth+RL+handler overhead excl. domain) | < 100 ms |
| Deploy-induced 5xx | ≈ 0 |
| Idempotent replay success | 100% same response |
| RL overshoot | < 5–10% bounded |

### 8.11 Capacity worksheet

```text
RPS_target = ...
RPS_per_pod = ...
pods = ceil(RPS_target / RPS_per_pod * headroom)
pods_per_az = ceil(pods / num_az)
Ensure (num_az - 1) * pods_per_az >= RPS_target / RPS_per_pod
```

### 8.12 Failure budget narrative

```text
If auth JWKS fetch fails:
  serve with cached JWKS until expire
  if cache gone → fail closed

If RL Redis down:
  route policy map → closed/open
  emit pages alert
```

### 8.13 Related systems map

```text
Clients → Edge Gateway → API Replicas (multi-AZ)
                           ├─ Auth material (JWKS)
                           ├─ Rate limit store
                           ├─ Idempotency store
                           ├─ Session / pubsub
                           └─ Domain DB / queues / object
Discovery/Ready ← orchestrator
```

### 8.14 Extra traps

| Trap | Pushback |
|------|----------|
| Sticky hides state | Externalize |
| Retry all POSTs | Need keys |
| Introspect every request | Local JWT |
| One Redis forever | Shard / hierarchy |
| DNS only discovery | Ready + drain |
| 5M×2KB=10MB/s | **10GB/s** |

### 8.15 Sample route policy table

| Route | Auth | RL | Idempotency | Sticky |
|-------|------|----|-------------|--------|
| `GET /v1/jobs/{id}` | JWT | tenant+route | n/a | no |
| `POST /v1/jobs` | JWT | tenant write | required | no |
| `GET /v1/metrics` | JWT | strict | n/a | no |
| `WS /v1/events` | JWT on upgrade | conn caps | n/a | yes |
| `POST /v1/uploads` | JWT | tenant write | required | optional |

### 8.16 gRPC notes

- Deadlines propagation mandatory.  
- Retry policy in service config: only idempotent methods.  
- Health: `grpc.health.v1`.  
- Streaming: affinity may help; state still external for resume.

### 8.17 Security checklist

- [ ] TLS everywhere  
- [ ] Strip untrusted identity headers  
- [ ] Short token TTL  
- [ ] Secret rotation  
- [ ] Audit mutations  
- [ ] Least-privilege DB creds per service  

---

*End of multi-server API system design.*
