# System Design: Defend & Harden an Existing System (Inventory Reservation Service)

> **Focus areas:** Reverse-design · Operational ownership · Upstream failure · Isolation · Circuit breakers · Overload · Recovery · Monitoring · Progressive hardening  
> **Style:** “A system **you** built” interview format — Amazon SDE III / L6+ bar  
> **Quality bar:** Real arithmetic, split QPS classes, explicit deal-breakers, progressive scale (10× → 100× → 1,000×), business trade-offs over textbook purity  
> **Concrete owned service:** **Inventory Reservation Service (IRS)** — the Amazon retail path that atomically reserves sellable units before order commit (Prime Day critical path)

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

## 0. How to Present “A System You Built” (Interview Framing)

Amazon frequently asks: *Walk me through a system you built. How would you harden it for 10× / 100× / failure?* This is **not** greenfield HLD from scratch—it is **reverse design + operational ownership**.

### 0.1 Narrative arc (use this every time)

| Phase | Minutes | What you say |
|-------|---------|--------------|
| Own it | 2–3 | Name, ownership boundary, business KPI it protects |
| As-built | 5–8 | Happy path, data model, deps, current SLOs |
| Pain | 3–5 | Real/credible incident or near-miss |
| Harden | 15–20 | Isolation, breakers, overload, recovery, monitoring |
| Scale | 5–8 | What breaks at 10× / 100× / 1,000× |
| Trade-offs | ongoing | Cost vs risk vs customer impact |

### 0.2 Ownership sentence (memorize a template)

> “I own **Inventory Reservation Service**. Upstream callers are Order Placement and Cart. Downstream we talk to Fulfillment Network Inventory (authoritative stock by FC), Pricing holds optionally, and we emit reservation events. Our job is: **never oversell**, **fail closed on uncertainty for hot SKUs**, and **shed load without cascading** into checkout.”

### 0.3 What interviewers grade

| Signal | Strong | Weak |
|--------|--------|------|
| Ownership | Clear blast radius, on-call stories | “We used Kafka” without why |
| Failure thinking | Upstream/downstream/self overload | Only “add Redis” |
| Isolation | Bulkheads, quotas, breakers | Shared thread pool for all deps |
| Business | Oversell vs lost sales trade-off | Pure availability slogans |
| Ops | Alarms → runbooks → game days | Metrics without actions |
| Scale | Progressive; capacity math | Jump to “Kubernetes” |

### 0.4 Pick a credible system if you lack Amazon retail

Acceptable substitutes with same hardening shape: payment auth adapter, session/token service, ads bid path, notification fanout control plane, warehouse pick-path API. **Always** pick something with: (1) hard invariant, (2) noisy neighbors, (3) upstream retries, (4) measurable customer KPI.

**This doc uses IRS** so answers stay concrete. Map your story onto the same skeleton.

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the hardening problem**—what IRS guarantees today, what fails under stress, and which customer outcomes are non-negotiable.

### 1.1 Functional Requirements (as-built + harden scope)

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What does IRS do? | Reserve N units of ASIN at FC(s) for a checkout session / order attempt | Soft hold with TTL + confirm/release |
| F2 | Who calls you? | Order Placement API (sync), Cart (soft holds), Internal tools | Different SLO/quotas per caller |
| F3 | Authoritative stock? | Fulfillment Inventory Service (FIS) is SoT by FC; IRS holds overlay | Never invent stock; reconcile |
| F4 | Reserve semantics? | Tentative hold → confirm on order place → release on cancel/TTL | State machine; idempotent keys |
| F5 | Oversell policy? | **Hard no** for 1P / high-risk; rare soft oversell only with explicit policy | Fail closed when unsure |
| F6 | Multi-FC? | Split reservation across FCs by promise date | Partial failure rules |
| F7 | Idempotency? | Required (`reservation_key` / order attempt id) | Dedup table + CAS |
| F8 | Events? | `Reserved`, `Confirmed`, `Released`, `Expired` to bus | At-least-once; consumers idempotent |
| F9 | Read APIs? | Get hold status; availability hints (not SoT for UI) | Cache carefully; label as hint |
| F10 | Harden scope? | Survive FIS blips, retry storms, Prime Day 10–100× | Isolation + admission + recovery |
| F11 | Admin ops? | Force release, TTL sweep, shard rebalance, feature flags | Audited break-glass |
| F12 | Consistency with order? | Order must not confirm without reservation (or explicit risk accept) | Dual-write discipline / outbox |

**MVP “as-built” scope (lock):**

1. `Reserve(asin, qty, fc_prefs, ttl, idem_key)` → `reservation_id` or deny.  
2. `Confirm(reservation_id)` on order commit.  
3. `Release(reservation_id)` on abandon/cancel.  
4. TTL expiry sweeper.  
5. Sync call to FIS for decrement/hold where required.  
6. Emit domain events.  
7. Metrics/alarms for latency, error, oversell risk, lag.

**Harden / interview stretch (explicitly in scope):**

- Upstream retry storms & client timeouts  
- Downstream FIS partial outage  
- Overload self-protection (load shedding)  
- Circuit breakers + bulkheads  
- Cell isolation / hot ASIN protection  
- Recovery & reconciliation after partitions  
- Progressive 10× → 100× → 1,000×

**Out of MVP (defer):**

- Perfect global active-active strong consistency for all ASINs  
- Replacing FIS as inventory SoT  
- Full marketplace seller inventory unification in one design  
- ML demand forecasting inside IRS

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Reserve latency | Checkout critical | p50 < 20ms, p99 < 100ms in-region (excl. rare FIS deep path) |
| N2 | Availability | High, but **correctness > blind avail** | 99.99% for healthy path; degrade with deny/queue |
| N3 | Oversell rate | Near zero for guarded SKUs | << 0.01% of units; alarm on any unexplained |
| N4 | Durability | Accepted reserve survives crash | Quorum write before ACK |
| N5 | Idempotency window | Checkout retries | ≥ 24–72h keys |
| N6 | Hold TTL | Cart/checkout | 5–15 min typical; configurable |
| N7 | Multi-AZ | Required | AZ loss ≠ data loss |
| N8 | Blast radius | One bad ASIN/FC ≠ site-wide | Cells / shard isolation |
| N9 | Operability | On-call can act in <5 min | Runbooks + dashboards + flags |
| N10 | Cost | Efficiency matters at Amazon | Capacity for peak, not forever 10× idle |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Checkout → Reserve(ASIN,1) → FIS OK → hold persisted → Confirm on PlaceOrder → stock committed.  
2. Customer abandons → TTL expire → Release → stock returns.  
3. Retry PlaceOrder with same idem_key → same reservation; no double hold.  
4. Multi-unit multi-ASIN cart → per-line reserves under parent checkout id; all-or-nothing policy configurable.  
5. Soft FIS timeout with local optimistic hold **only** if policy allows and reconcile job exists—default interview answer: **fail closed** for hot SKUs.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Client double-submit | Idempotency returns original reservation |
| FIS 503 | Circuit open → fail closed / queue / cached deny; **no silent success** |
| FIS slow (2s) | Timeout budget; bulkhead saturated → shed |
| Upstream retry storm | Per-caller + global admission control |
| Hot ASIN (PS5-class) | Dedicated shard / stricter TTL / serialized reserve |
| Partial multi-ASIN failure | Release successful siblings; return structured errors |
| Confirm after TTL | Reject; force new reserve |
| Clock skew TTL | Server-side expiry only; lease regeneration |
| Split brain dual writers | Single-writer home cell per ASIN/FC key |
| Poison message on event bus | DLQ; reservation DB remains SoT |
| Deploy bad binary | Canary + auto-rollback on error/oversell canaries |
| AZ loss mid-write | Quorum; client retries idempotently |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak reserve QPS | 20K | 200K | 2M | 20M |
| Peak confirm/release QPS | 8K | 80K | 800K | 8M |
| Distinct hot ASINs / min | 5K | 20K | 50K | 100K+ |
| Open holds (global) | 5M | 50M | 500M | 5B |
| FIS dependency QPS | ~15K | ~150K | ~1.5M | ~15M |
| Event egress / s | 30K | 300K | 3M | 30M |
| Checkout p99 budget for IRS | 100ms | 80ms | 50ms | 50ms (cells) |
| On-call pages / week | few | rising | need automation | SRE platform |

**What each jump forces:**

- **10×:** Bulkheads, per-caller quotas, Redis/local hot-ASIN cache of denials, FIS breakers, better TTL sweepers.  
- **100×:** ASIN/FC cells, shuffle sharding, request coalescing, write-ahead admission, dedicated hot-SKU lanes.  
- **1,000×:** Hierarchical cells, regional homes, predictive capacity, strict priority classes, automated load-shedding policies as code.

### 1.5 Etc. (Constraints & Assumptions)

- Amazon-scale retail; Prime Day / lightning deals are first-class.  
- Strong preference for **practicality**: deny a sale rather than oversell a constrained ASIN.  
- Clients **will** retry aggressively—design for it.  
- You do **not** control all upstream code quality; defend in depth.  
- Efficiency: avoid holding 10× idle capacity year-round; use elastic + shed.

**Scope statement:**

> Reverse-design and harden Inventory Reservation Service: as-built reserve/confirm/release with idempotency and FIS dependency; then systematically address upstream failure, isolation, circuit breakers, overload, recovery, and monitoring through 10× / 100× / 1,000×—as if you own the on-call and the oversell KPI.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split (do not lump “QPS”)

```text
Baseline peak reserve = 20,000 / s
Assume 40% of reserves confirm, 60% expire/release
Confirm ≈ 8,000 / s; Release/Expire ≈ 12,000 / s
Read status ≈ 2–5× writes during checkout UI polls → ~40–100K read QPS

At 100×: reserve 2M/s — this is a cell’d, sharded system, not one Redis.
```

| Class | Baseline peak | 100× | Notes |
|-------|---------------|------|-------|
| Reserve write | 20K | 2M | Hottest |
| Confirm | 8K | 800K | Must be fast + correct |
| Release/Expire | 12K | 1.2M | Sweepers + explicit |
| Idempotency lookup | ≈ write | ≈ write | Same path |
| FIS calls | 0.5–1.0 × reserve | same ratio until caching | Dependency risk |
| Events | ~1.5 × mutations | | Async |

### 2.2 Open holds memory / storage

```text
Hold record ≈ 200–400 B (ids, qty, ttl, state, version)
Baseline open holds 5M × 300 B ≈ 1.5 GB (working set; plus indexes)

10×: 50M × 300 B ≈ 15 GB
100×: 500M × 300 B ≈ 150 GB
1000×: 5B × 300 B ≈ 1.5 TB just for open holds

→ Shard by hash(asin, fc) or cell; TTL-primary storage; cold confirms archived
```

Idempotency keys (24h):

```text
20K reserve/s × 86400 ≈ 1.7B keys/day baseline peak-day math if sustained
Peak hour more relevant: 20K × 3600 = 72M keys/hour
Payload ~100 B → ~7.2 GB/hour ingress to idem store at sustained peak
Use TTL’d KV + hash of request; not eternal SQL rows for all keys
```

### 2.3 Latency budget (checkout)

```text
Checkout total p99 budget example: 800ms
IRS slice: 100ms
  - Auth/quota: 2ms
  - Idempotency: 3ms
  - Local shard CAS: 10ms
  - FIS: 40–60ms (danger zone)
  - Event outbox: 5ms (async after ACK optional)

Deal-breaker: unbounded FIS wait eating entire checkout budget.
```

### 2.4 Retry amplification (critical math)

```text
Client timeout = 200ms; IRS p99 = 150ms → many false timeouts
Each user action retries 3×; 1000 clients × 3 = 3× load
If 10% of calls slow: effective arrival λ_eff ≈ λ × (1 + extra retries)

Example: 20K QPS offered → 60K QPS attempted under partial brownout
Without admission control, self-DDoS.
```

**Amplification factor** under brownout can be **3–10×**. Hardening must assume this.

### 2.5 Hot ASIN skew

```text
Lightning deal: 50% of reserve QPS on 100 ASINs for 5 minutes
At 100× global 2M QPS → 1M QPS on 100 keys → 10K QPS/key
Single-key row lock / single shard partition melts.

→ Hot-key isolation: local token buckets, queue-per-key, coarse locks, FC striping
```

### 2.6 Cost / efficiency sketch

```text
Always-on capacity for 100× peak year-round: wasteful
Amazon bar: provision for expected peak + safety; shed beyond; elastic warm pools
Measure: $ per 1K successful reserves; $ per denied-with-cause (cheap) vs oversell (very expensive brand/ops)
```

### 2.7 Bottleneck ranking

1. Hot ASIN/FC partitions  
2. FIS latency & error amplification  
3. Retry storms from Order Placement  
4. Idempotency/CAS contention  
5. TTL sweeper lag → “phantom” stock  
6. Event bus lag (secondary if DB is SoT)

---

## 3. High-Level Design

### 3.1 As-built control plane (what you “built”)

```text
Order Placement / Cart
        |
        v
   API Gateway + Auth
        |
        v
 Inventory Reservation Service
   - Admission / quotas
   - Idempotency store
   - Reservation state (sharded)
   - Outbox for events
        |
        +-----> FIS (fulfillment inventory)
        +-----> (optional) Promise / Pricing
        +-----> Event bus → Order, Notifications, Analytics
```

### 3.2 Reservation state machine

```text
         Reserve OK
NULL ──────────────► HELD ──Confirm──► CONFIRMED
                       │
                       ├─Release──► RELEASED
                       └─TTL─────► EXPIRED (≡ released stock)
```

**Invariants:**

1. Units held ≤ FIS available + explicit risk policy (default 0 risk).  
2. Idempotent Reserve with same key → same `reservation_id` + body hash check.  
3. Confirm only from `HELD` and unexpired.  
4. Stock effects are monotonic per reservation (no double release credit).

### 3.3 Hardening layers (the interview meat)

| Layer | Purpose | Amazon theme |
|-------|---------|--------------|
| **Admission control** | Bound accepted work | Efficiency, overload |
| **Bulkheads** | Isolate dependency pools | Reliability |
| **Circuit breakers** | Stop calling sick deps | Fail fast |
| **Timeouts + budgets** | Cap wait | Latency SLOs |
| **Idempotency** | Make retries safe | Practicality |
| **Load shedding** | Protect core | Scalability |
| **Cells / shards** | Limit blast radius | Operational ownership |
| **Reconciliation** | Heal after uncertainty | Correctness |
| **Observability** | Detect → act | Ownership |

### 3.4 Upstream failure modes (callers)

| Failure | Symptom | Defense |
|---------|---------|---------|
| Aggressive retries | QPS spike, duplicate keys | Idempotency + retry-after + client guidance |
| No backoff | Synchronized retry herds | Jittered `Retry-After`; hedge only once |
| Long client timeout | Pile-up of in-flight | Server timeout < client; shed 503 |
| Bad deploy of caller | Weird payloads / fanout | Schema validation; per-caller quotas |
| Thundering herd on deal start | Hot key melt | Coalesce; queue; fair share |

**Deal-breaker:** Treating all callers as trusted and unlimited.

### 3.5 Downstream failure (FIS)

| Strategy | When | Trade-off |
|----------|------|-----------|
| Fail closed | Hot / constrained ASIN | Lost sale; no oversell |
| Serve stale availability deny | Known OOS cache | May deny available stock briefly |
| Queue + async reserve | Non-interactive paths | Not for sync checkout |
| Hedged request (2nd AZ) | Rare; p99 | Extra load; careful |
| Degraded “soft hold” + reconcile | Explicit business approve | Oversell risk window |

**Default SDE III answer:** fail closed on uncertainty for inventory-critical path; measure lost GMV vs oversell cost; feature-flag soft modes.

### 3.6 Circuit breaker design

States: `CLOSED → OPEN → HALF_OPEN → CLOSED`.

```text
Per dependency + per cell + optionally per caller class:
  error_rate > 20% OR p99 > budget for 30s → OPEN
  OPEN: fail fast locally (no FIS call)
  after 30s → HALF_OPEN: allow probe % 
  probes OK → CLOSED; fail → OPEN
```

| Knob | Typical | Notes |
|------|---------|-------|
| Window | 10–30s | Too short → flappy |
| Min requests | 50–200 | Avoid open on tiny samples |
| Open duration | 15–60s | Align with FIS recovery |
| Half-open probes | 1–5% | Cap absolute QPS |
| Scope | **Per shard/cell** | Global breaker = site-wide outage amplifier |

**Deal-breaker:** One global breaker for all ASINs/FCs.

### 3.7 Bulkheads & isolation

```text
Thread/IO pools:
  - FIS_POOL (size N)
  - IDEM_POOL
  - DB_POOL
  - EVENT_POOL (non-blocking preferred)

Caller bulkheads:
  - ORDER_PLACEMENT quota
  - CART quota
  - INTERNAL/BATCH quota (lowest priority)
```

Shed order under overload: **BATCH → CART soft holds → CHECKOUT reserves** (protect revenue path last—or reverse if oversell risk dominates; **state the business choice**).

### 3.8 Overload & load shedding

| Signal | Action |
|--------|--------|
| CPU / in-flight > limit | 503 + `Retry-After` |
| Queue depth | Shed lowest priority |
| Hot key tokens exhausted | Fast deny “try again” / sold out |
| Dependency OPEN | Local policy deny |
| Partial deploy unhealthy | Canary abort |

Prefer **explicit 503** over silent queueing that grows latency to infinity (latency death spiral).

### 3.9 Recovery & reconciliation

1. **Idempotent retry** of uncertain Reserve (same key).  
2. **Confirm/Release** are CAS on version.  
3. **Reconciler** compares HELD set vs FIS holds periodically.  
4. **Sweeper** expires TTLs; alert if lag > threshold.  
5. **Undo logs / outbox** for event repair.  
6. **Break-glass** force-release with audit.

### 3.10 Monitoring (actionable)

Golden signals + **business** signals:

| Signal | Alarm idea |
|--------|------------|
| Reserve success rate | Drop vs baseline |
| p99 latency | Budget burn |
| FIS error / open circuits | Dependency |
| Oversell canaries / negative stock events | Sev-2 |
| Idempotency mismatch 409 rate | Client bugs |
| TTL sweeper lag | Phantom inventory |
| Shed rate | Capacity |
| Per-cell saturation | Rebalance |
| Retry amplification ratio | Client timeout misconfig |

### 3.11 Trade-off tables

| Concern | Choice | Deal-breaker |
|---------|--------|--------------|
| Uncertainty | Fail closed (default) | Silent success without FIS |
| Consistency | Single-writer per ASIN/FC cell | Multi-master without CRDT/reconcile |
| Cache | Negative cache short TTL | Positive “in stock” cache as SoT |
| Events | After durable state | Event-before-DB as SoT |
| Shedding | Priority + 503 | Unlimited queue |
| Breakers | Per-cell | One global breaker |
| Retries | Idempotent + jitter | Blind replay new keys |

---

## 4. Architecture Diagram

### 4.1 As-built + harden overlay

```text
                    +---------------------------+
                    |  Per-caller quotas / WAF  |
                    +-------------+-------------+
                                  |
                                  v
+-------------+     +---------------------------+     +------------------+
| Order Place | --> | IRS API (admission first) | --> | Idempotency KV   |
| Cart        |     |  deadlines / priority     |     +------------------+
+-------------+     +-------------+-------------+
                                  |
                    +-------------+-------------+
                    | Reservation shards/cells  |
                    |  CAS state machine        |
                    +------+-------------+------+
                           |             |
              bulkhead+CB  v             v  outbox
                    +------------+   +----------------+
                    | FIS client |   | Event bus      |
                    +------------+   +----------------+
                           |
                    circuit / timeout / hedge(policy)
```

### 4.2 Request path with budgets

```text
t0  Accept connection
t1  Authenticate + caller quota (fail 429)
t2  Deadline = min(client, server_max=100ms)
t3  Idempotency lookup
t4  Local shard lock/CAS attempt
t5  FIS call with remaining budget (e.g. 60ms) in FIS_POOL
t6  Persist HELD + outbox
t7  ACK
On any budget exceed: fail fast; no dangling untracked FIS side effect
    (or compensate if FIS call already succeeded — see §5)
```

### 4.3 Circuit breaker + bulkhead

```text
Request → Acquire FIS_POOL permit? --no--> Shed/Fail
                 |yes
                 v
         Breaker state OPEN? --yes--> Fail closed (policy)
                 |no
                 v
         Call FIS with timeout
           |ok                |error/timeout
           v                  v
        Record success     Record failure → maybe OPEN
```

### 4.4 Hot ASIN lane

```text
hash(asin) → normal shard
if asin in HOT_SET:
  → Hot lane: single-flight coalescing, token bucket, shorter TTL, extra metrics
Lightning deal flag → prefetch negative/positive hints; serialize increments
```

### 4.5 Recovery loop

```text
Reconcile job (1m):
  for reservations in HELD beyond grace:
    compare with FIS hold
    if IRS HELD & FIS missing → re-apply or expire+alert
    if FIS hold & IRS missing → release FIS or create repair row
TTL sweeper:
  expire HELD where now > ttl; release FIS; emit Expired
```

### 4.6 Progressive topology

```text
1×:   IRS service + PG/Dynamo + Redis idem + FIS
10×:  shards by asin; breakers; caller quotas; sweeper fleet
100×: cells (marketplace/region/asin range); hot lanes; shuffle shards
1000×: hierarchical admission; regional homes; auto cell split
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **No ACK without durable reservation record** (or durable deny).  
2. **Idempotency:** same key + same body → same result; different body → 409.  
3. **No double-confirm** / **no double-release credit**.  
4. **Fail closed** on unknown FIS outcome for guarded SKUs (or explicit compensating transaction).  
5. **Timeout < caller timeout** to reduce duplicate in-flight.  
6. **Per-cell blast radius** capped.  
7. **Every shed/deny typed** (quota vs soldout vs dependency vs overload).  
8. **Audit** break-glass releases.

**Uncertain FIS outcome playbook**

```text
Sent Reserve to FIS → timeout → unknown
Options:
 A) Idempotent FIS API with same hold_token → retry safe (PREFERRED)
 B) Query-by-token status
 C) Fail closed to client; reconcilers heal
Never: invent success
```

**Failure playbook**

| Failure | Response |
|---------|----------|
| FIS regional outage | Open breakers that region; route FCs elsewhere if policy; deny FC-local |
| IRS shard meltdown | Shed traffic to shard; failover replica; rebalance |
| Bad deploy | Canary auto-rollback on error + oversell canary |
| Retry storm | Admission down to sustainable QPS; communicate Retry-After |
| Data corruption | Restore shard from PITR; reconcile FIS |
| Event bus down | Outbox retains; DB SoT; lag alarm |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Monolith IRS + multi-AZ DB; simple pool |
| 10× | Horizontal API; shard reservations; Redis idem; CB library |
| 100× | Cells; hot-ASIN service; priority admission; async confirm paths where safe |
| 1000× | Auto-split cells; hierarchical quotas; regional IRS homes; FIS locality |

**Coalescing:** 5K concurrent Reserve(ASIN=X,1) → single-flight check availability + batch decrement where FIS supports; else serialize with fair queue.

**Caching rules:**

| Cache | Allowed | TTL |
|-------|---------|-----|
| Negative OOS | Yes | 1–5s |
| Positive availability count | Hint only | sub-second / versioned |
| Idempotency results | Yes | 24–72h |
| “Success” without durable write | **Never** | — |

### 5.3 Maintainability / operational ownership

Amazon bar is **you run what you wrote**:

| Practice | Detail |
|----------|--------|
| Dashboards | Golden + business; per cell; per caller |
| Alarms | Severity mapped to customer impact |
| Runbooks | Breaker stuck open; sweeper lag; oversell; hot ASIN |
| Game days | Kill FIS; amplify retries; block AZ |
| Feature flags | Soft-hold mode; shed thresholds; hot set |
| Canaries | Synthetic reserve/confirm/release per cell |
| Capacity reviews | Pre–Prime Day; load tests with retry model |
| Postmortems | Correctness incidents > pure latency |

### 5.4 Progressive scale deep dive

**1× (~20K reserve QPS)**

- API + DynamoDB/Aurora shard + Redis idempotency.  
- FIS client with 60ms timeout, pool size 200.  
- Simple CB per FIS endpoint.  
- TTL sweeper every 1s tick.  
- Metrics: latency, error, open holds.

**10× (~200K QPS)**

- 20–40 shards; consistent hashing on `(asin, fc)`.  
- Per-caller token buckets.  
- Bulkheads separate FIS vs DB.  
- Negative caching.  
- Outbox + async events.  
- Load-test with 3× retry amplification scenario.

**100× (~2M QPS)**

- Cells by ASIN range / retail category / region.  
- Hot lane cluster.  
- Shuffle sharding to reduce noisy neighbor.  
- Admission as first filter (cheap).  
- Adaptive concurrency (AIMD) on FIS pools.  
- Automated cell rebalance.

**1000× (~20M QPS)**

- Hierarchical admission (global → cell → key).  
- Regional homes; cross-region only for failover.  
- Predictive warm capacity for scheduled deals.  
- Policy engine: which ASINs allow soft degrade.  
- Platform SRE automation for shed & rollback.

### 5.5 Upstream failure in depth

**Pattern: retry + timeout mismatch**

```text
Client timeout 500ms, server work 400ms p99, client retries ×3
→ 4× in-flight amplification, DB contention ↑, p99 ↑ → collapse
```

**Fixes:**

1. Align budgets (server 100ms, client 300ms, one retry).  
2. Idempotency keys mandatory in API contract.  
3. Return `Retry-After` with jitter advice.  
4. Hedge only on safe read paths—not blind double Reserve without idempotency.  
5. Publish client SDK with correct defaults (Amazon-style shared library).

### 5.6 Circuit breakers in depth

**Error types that trip:** timeouts, 5xx, connection fails.  
**Usually do not trip:** 404 sold out (business reject), 400 bad request.

**Half-open caution:** thundering herd of probes—cap probe QPS.

**Composition:** breaker around FIS ≠ breaker around DB. DB failure needs different policy (maybe shed all writes).

### 5.7 Overload control algorithms (interview-friendly)

| Algorithm | Use |
|-----------|-----|
| Token bucket / leaky bucket | Per caller / per key |
| AIMD concurrency | Dependency pools |
| CoDel / queue-age shedding | Drop oldest or newest intentionally |
| Priority queues | Checkout > cart > batch |
| Adaptive admission | Target latency / in-flight |

**Vegas-style:** if p99 rising, reduce admitted QPS even if CPU not 100% (prevent latency death spiral).

### 5.8 Recovery specifics

**Orphan FIS hold:** IRS timed out after FIS success → reconciler finds FIS hold without IRS row → create IRS HELD or release FIS (policy: prefer release to avoid oversell? Actually: **prefer create IRS HELD** if client may retry confirm—document choice).

**Orphan IRS HELD:** FIS missing → re-apply or expire.

**Poison confirm:** Confirm after expire → 409/410; client must re-reserve.

### 5.9 Monitoring & incident UX

**Dashboard sections:**

1. Traffic & shed  
2. Dependency health (FIS)  
3. Correctness (oversell, reconcile diffs)  
4. Saturation (pools, cells)  
5. Prime Day mode banner (flags on)

**Page only on actionable Sev:** oversell canary, reconcile diff spike, sweeper lag, cell unavailable, error budget burn.

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Cache stock counts as SoT | Oversell |
| Global circuit breaker | Total checkout outage |
| Infinite retries | Self-DDoS |
| ACK before durable write | Lost reservations / ghost confirms |
| Shared unlimited executor | One slow FIS call starves all |
| Active-active dual writers | Double sell |
| Ignoring hot keys | Meltdown on deals |
| Metrics without runbooks | MTTF ≠ MTTR |
| Soft-hold without reconcile | Silent inconsistency |
| “Just add more hosts” under brownout | Feeds the fire |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Owned system | Inventory Reservation Service |
| Correctness | No oversell; fail closed default |
| Retries | Idempotency + aligned timeouts |
| Deps | Bulkheads + per-cell breakers |
| Overload | Admission + priority shed + 503 |
| Scale | Shard → cell → hierarchical |
| Ops | Canaries, game days, reconcile |
| Business | Lost sale < oversell for constrained goods |

### 6.2 Risks

1. Retry amplification underestimated  
2. Hot ASIN concentration  
3. Soft degrade mode left on after incident  
4. Reconcile lag creating phantom availability  
5. Global breaker misconfig  
6. Client SDKs not adopted  

### 6.3 45-minute plan (this interview type)

| Min | Focus |
|-----|-------|
| 0–3 | Ownership one-liner + KPI (oversell, checkout) |
| 3–10 | As-built path + state machine + deps |
| 10–18 | Incident story / failure modes |
| 18–30 | Isolation, breakers, overload, budgets |
| 30–38 | Recovery, reconcile, monitoring |
| 38–45 | 10×/100×/1000× + trade-offs |

### 6.4 One-paragraph closer

> “I own IRS on the checkout critical path. We reserve durable, idempotent holds against FIS, fail closed on uncertainty, and isolate blast radius with per-cell bulkheads and breakers. Under overload we shed intentionally with priorities rather than melt, and we reconcile to heal. Scaling is shard → cell → hierarchical admission, with hot-ASIN lanes for deals—optimized for correctness and operational control, not just peak QPS.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Framing & ownership

**Q: Why is this an L6 design interview if the system already exists?**  
A: Amazon tests whether you can operate, harden, and evolve systems under failure and growth—not only draw greenfield boxes.

**Q: What KPI do you own?**  
A: Oversell rate, reservation p99, checkout impact (contribution to place-order failures), shed rate, reconcile diff count.

**Q: How do you bound scope in 45 minutes?**  
A: One critical path (Reserve), one hard invariant (no oversell), three harden pillars (isolation, overload, recovery).

**Q: What if your real system is small?**  
A: Scale the story honestly with progressive math; focus on failure design quality, not fake PB claims.

### 7.2 Upstream failure

**Q: Clients retry forever—what do you do?**  
A: Idempotency, 429/503 with Retry-After, per-caller quotas, publish SDK defaults, contact owning team; server-side admission is last line.

**Q: Should IRS retry FIS internally 5 times?**  
A: Bounded retries (0–2) with jitter inside budget; prefer fail fast + client idempotent retry. Internal retry storms stack with client retries.

**Q: Hedged requests?**  
A: Only if idempotent and budget allows; hedging doubles FIS load—dangerous during outage.

**Q: How do you detect retry amplification?**  
A: Metric `attempts / unique idem_keys`; alarm when ratio >> 1.2–1.5.

**Q: Upstream sends new idempotency key each retry?**  
A: Contract violation; reject or treat as new demand (oversell risk)—educate + metric + eventually WAF rules for abusive patterns.

### 7.3 Isolation & bulkheads

**Q: Thread pool vs semaphore vs separate processes?**  
A: At minimum separate concurrency limits per dep; process isolation for extreme noisy neighbors / cells.

**Q: Noisy neighbor ASIN?**  
A: Hot lane + per-key token bucket + cell split; don’t let one deal starve grocery checkout.

**Q: Shared Redis for idempotency and cache?**  
A: Risk; separate failure domains if Redis meltdown shouldn’t lose both admission and idempotency differently—at least separate clusters/DBs.

**Q: Shuffle sharding?**  
A: Map each ASIN to multiple candidate shards; pick healthy; reduces correlated failure vs fixed hash alone.

### 7.4 Circuit breakers

**Q: Breaker vs timeout vs retry—order?**  
A: Timeout always; retry rarely; breaker stops calling when unhealthy; admission stops accepting when self-overloaded.

**Q: When not to trip breaker?**  
A: Business 404/409; low sample counts; dependency only affecting tiny FC set (use scoped breakers).

**Q: Cascading breakers across microservices?**  
A: Each hop with breakers can amplify fail-closed; use budgets and partial degradation carefully; chaos-test chains.

**Q: How long to stay OPEN?**  
A: Long enough for FIS recovery, short enough to probe; typically tens of seconds; exponential with cap if probes keep failing.

**Q: Half-open thundering herd?**  
A: Single probe or tiny %; others fail fast until success.

### 7.5 Overload

**Q: Load shed oldest vs newest?**  
A: Often shed newest (protect in-flight near completion) or random; state choice. For checkout, prefer fast 503 over long wait.

**Q: Queue or shed?**  
A: Small bounded queue for micro-bursts; beyond that shed. Unbounded queues turn outages into latency disasters.

**Q: Brownout vs blackout?**  
A: Brownout: high latency, partial success—often worse; detect via p99/in-flight and shed to restore goodput.

**Q: Adaptive concurrency?**  
A: AIMD on in-flight to FIS based on timeouts; similar to TCP / Netflix concurrency limits.

**Q: Priority inversion?**  
A: Ensure batch cannot hold locks needed by checkout; separate pools and key scheduling.

### 7.6 Recovery & correctness

**Q: Exactly-once reservation?**  
A: Effectively-once via idempotency + CAS; duplicates may attempt but not double-hold.

**Q: Two-phase commit with Order DB?**  
A: Avoid distributed XA; use reservation first then order, or outbox/saga with compensating release.

**Q: TTL vs explicit release?**  
A: Both; TTL is safety net for crashes/abandons; sweeper lag is a correctness risk—monitor.

**Q: How do you prove no oversell?**  
A: Invariants + FIS as SoT + canaries (attempt reserve beyond stock in staging) + reconcile diffs + audit sampling.

**Q: Clock skew?**  
A: Expiry with server time; avoid client TTL authority; sync NTP; grace overlaps.

### 7.7 Monitoring & ops

**Q: Which alarm pages you at 3am?**  
A: Oversell/reconcile diffs, cell down, error budget burn on PlaceOrder attributed to IRS, sweeper lag critical—not every 5xx blip.

**Q: How do you validate a harden change?**  
A: Load test with retry model, game day kill FIS, canary, feature flag ramp, watch amplification ratio.

**Q: Synthetic canaries?**  
A: Continuous reserve/confirm/release on canary ASINs per cell; alert on failure patterns.

**Q: Cardinality explosion in metrics?**  
A: Avoid per-ASIN labels in hot metrics; use top-K sketches / curated hot set.

### 7.8 Scale progression

**Q: What breaks first at 10×?**  
A: FIS pool + hot keys + sweeper + idempotency store memory.

**Q: What breaks at 100×?**  
A: Single-cluster limits; need cells; cross-tenant noisy neighbors; event fanout.

**Q: Active-active multi-region IRS?**  
A: Hard for strong no-oversell; prefer single-writer home per ASIN/FC; regional for locality with careful failover.

**Q: Capex efficiency?**  
A: Elastic for known peaks (Prime Day); don’t run 100× year-round; shed with clear UX.

### 7.9 Business trade-offs

**Q: Deny sale vs risk oversell?**  
A: For constrained/high-ASIN-risk, deny; for infinite digital goods, different service. State $ impact.

**Q: Soft hold without FIS for speed?**  
A: Only with strict reconcile SLA and business signoff; interview default = no.

**Q: Cart holds vs checkout holds?**  
A: Cart more shedable; shorter TTL; lower priority under overload.

### 7.10 Behavioral hybrids (Amazon loves these)

**Q: Tell me about a time this failed.**  
A: Structure: customer impact → root cause (e.g., retry storm) → harden (budgets, breakers) → prevention (game days, SDK).

**Q: Disagree with partner team on retries?**  
A: Data: amplification metrics; propose SDK change; temporary server protections; escalate on customer impact.

**Q: How do you mentor juniors on this system?**  
A: Invariants first, then failure modes, then dashboards/runbooks—not framework trivia.

### 7.11 Extra rapid-fire (keep answers short)

**Q: Why p99 not avg?**  
A: Checkout feels p99; averages hide brownouts.  
**Q: Why typed errors?**  
A: Callers/automation react differently to soldout vs overload.  
**Q: Why outbox?**  
A: DB + bus dual-write races.  
**Q: Why not Kafka as SoT?**  
A: Need sync CAS semantics for holds.  
**Q: Backpressure propagation?**  
A: 503 upstream beats unlimited accept.  
**Q: Poison pill reservation?**  
A: Quarantine key; DLQ events; fix forward.  
**Q: Multi-FC atomicity?**  
A: Saga with compensations; or single FC decision first.  
**Q: Fairness?**  
A: Per-caller and per-ASIN caps.  
**Q: Security?**  
A: AuthN/Z, no cross-merchant reserve, audit.  
**Q: Compliance/audit?**  
A: Who break-glass released holds.  
**Q: Cost anomaly?**  
A: FIS call explosion from retries—watch $ and QPS.  
**Q: SLOs vs SLIs?**  
A: SLI = measured; SLO = target; error budget drives freeze/ship.  
**Q: Freeze window before Prime Day?**  
A: Yes for IRS; only risk-reducing changes.  
**Q: What would you build differently knowing what you know?**  
A: Admission-first architecture from day 1; idempotency in v1; cell boundaries early.

---

## 8. Appendices

### Appendix A — API sketch

```text
POST /v1/reservations
Idempotency-Key: <key>
{ "asin", "fc_id?", "qty", "ttl_sec", "priority": "CHECKOUT"|"CART" }
→ 201 { reservation_id, expires_at, state:"HELD" }
→ 409 conflict (body mismatch)
→ 429 quota
→ 503 overload / dependency (Retry-After)

POST /v1/reservations/{id}/confirm  → CONFIRMED
POST /v1/reservations/{id}/release  → RELEASED
GET  /v1/reservations/{id}
```

### Appendix B — Data model (sketch)

```text
Reservation{
  reservation_id, idem_key, caller, asin, fc_id,
  qty, state, version, expires_at, created_at, updated_at
}
IdempotencyRecord{ idem_key, request_hash, reservation_id, ttl }
Outbox{ event_id, type, payload, created_at, published_at? }
ReconcileDiff{ id, kind, reservation_id, detected_at, resolved_at? }
```

### Appendix C — Timeout budget template

```text
client_total       = 300ms
server_total       = 100ms
  auth_quota       = 3ms
  idem             = 5ms
  db_cas           = 15ms
  fis              = 60ms  (hard cap)
  persist_outbox   = 10ms
margin             = 7ms
```

### Appendix D — Prime Day checklist

1. Load test with retry amplification model  
2. Hot ASIN list preloaded  
3. Breaker/swear thresholds reviewed  
4. Cell capacity + on-call staffing  
5. Feature flags default fail-closed  
6. Canaries green across regions  
7. Sweeper lag dashboard projected  
8. Comms plan for shed UX  
9. Rollback anchors ready  
10. Freeze nonessential deploys  

### Appendix E — Mapping this doc to YOUR system

| IRS concept | Your analog |
|-------------|-------------|
| Reserve | Create scarce resource lease |
| FIS | Downstream SoT dependency |
| Oversell | Double-spend / double-book |
| Hot ASIN | Hot key / celebrity user |
| Confirm | Commit side effect |
| TTL | Lease expiry |
| Shed | Brownout protection |

### Appendix F — Cheat sheet (print this)

| Pillar | One-liner |
|--------|-----------|
| Upstream | Idempotency + budgets + quotas |
| Isolation | Bulkheads / cells / hot lanes |
| Breakers | Per-cell, probe-capped |
| Overload | Admit → priority → 503 |
| Recovery | CAS + reconcile + sweeper |
| Monitoring | Golden + oversell + amplification |
| Scale | 10× shard, 100× cell, 1000× hierarchy |
| Business | Fail closed > silent oversell |

### Appendix G — Sample “ownership” monologue (90 seconds)

> “I owned Inventory Reservation for retail checkout. We take idempotent Reserve calls, persist HELD state, call FIS under a strict timeout budget, then Confirm on order place. The hard invariant is no oversell. The painful failure mode was FIS brownout plus client retries amplifying load 4× and melting our pools. We hardened with admission control, per-caller quotas, FIS bulkheads and per-cell circuit breakers, hot-ASIN lanes, and a reconciler for uncertain outcomes. We page on oversell canaries and sweeper lag, not raw CPU. At 100× we’d cell by ASIN range; at 1000× hierarchical admission and regional homes. Happy to deep-dive breakers or the reconcile semantics.”

### Appendix H — Common interviewer pushbacks & replies

| Pushback | Reply |
|----------|-------|
| “Just make FIS more available” | You don’t own FIS; design for dependency failure |
| “Use a bigger cache” | Cache isn’t SoT for stock; negative cache OK |
| “Exactly-once end-to-end?” | Effectively-once with idempotency; be precise |
| “Why not queue all reserves?” | Checkout needs sync answer; queue = latency |
| “Availability 99.999% at all costs” | Correctness/oversell trade-off; Amazon wants judgment |

### Appendix I — Progressive scale one-pager

| Scale | Peak reserve | Must-have harden |
|-------|--------------|------------------|
| 1× | 20K/s | Timeouts, idempotency, basic CB |
| 10× | 200K/s | Quotas, bulkheads, shards, neg cache |
| 100× | 2M/s | Cells, hot lanes, AIMD, game days |
| 1000× | 20M/s | Hierarchical admission, regional homes, policy engine |

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| Bulkhead | Isolated resource pool limiting blast radius |
| Brownout | Overloaded-but-up; high latency / partial fail |
| Goodput | Successful useful work per second |
| Fail closed | Deny when uncertain |
| Cell | Independent unit of deployment/data/failure |
| Amplification | Retries/hedges multiplying offered load |
| SoT | Source of truth |

---

*End of prep doc — Defend & Harden (Inventory Reservation Service). Practice aloud with a 45-minute timer; insist on invariants, budgets, and business trade-offs.*
