# System Design: Internal Authorization System

> **Focus areas:** RBAC+ABAC · PDP/PEP · Audit · Break-glass  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** API correctness, idempotency, ledger/regional failure awareness, explicit deal-breakers, integer money where applicable  
> **Interview type:** **HLD / architecture** — Stripe emphasizes correctness, rollout, and ops—not only box diagrams

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

Goal: bound internal **authz**—PEP/PDP, policy-as-data, cache, audit.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|---|---|---|
| F1 | Subject? | Service+mTLS | Principal ID |
| F2 | Policy? | RBAC+ABAC versioned | Policy store |
| F3 | Default? | Deny | Fail closed money |
| F4 | Audit? | Every decision | Append log |
| F5 | Break-glass? | TTL grant | Dual approve |
| F6 | Cache? | TTL+invalidate | On revoke |
| F7 | Resources? | Journals payouts | Hierarchy |
| F8 | Latency? | ms cached | Budget eval |
| F9 | Multi-region? | Policy replica | Version sync |
| F10 | Testing? | Policy CI | Matrix tests |
| F11 | Rollout? | Shadow | Compare |
| F12 | PEP? | Sidecar | Local cache |

**MVP functional scope (lock with interviewer):**

1. `POST /v1/authz/check` — idempotent where mutating.
2. `POST /v1/policies` — idempotent where mutating.
3. `GET /v1/principals/{id}/roles` — idempotent where mutating.
4. `POST /v1/break-glass/grant` — idempotent where mutating.
5. Policy bundle signing and version registry
6. Decision audit export API

**Out of MVP (explicitly defer):**

- Customer-facing IAM product
- Per-row SQL grants without PEP
- Real-time ML risk scoring in authz path

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|---|---|---|
| N1 | Check latency | Hot path per RPC | p99 < 5ms cached, < 30ms uncached |
| N2 | Failure mode | Money mutations | Fail closed DENY |
| N3 | Policy propagation | Revoke global | < 60s cache invalidation SLO |
| N4 | Audit write rate | Every decision | Sample non-money at 1000× |
| N5 | Availability PDP | Critical | 99.99% with read replicas |
| N6 | Scale | 50K→50M checks/s | Shard PDP; PEP cache |
| N7 | Consistency | Policy version | Monotonic published version |
| N8 | Security | Tamper policy | Signed bundles |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Payout service PEP → PDP ALLOW → audit → proceed
2. Revoked role → version bump → cache invalidate → DENY
3. Break-glass dual-approved → temporary ALLOW → auto-expire
4. Shadow policy logs WOULD_DENY without blocking
5. Cached decision on repeated check → sub-ms
6. Cross-region PEP uses local policy replica same version

**Edge / failure cases**

| Case | Behavior |
|---|---|
| PDP timeout on journal post | DENY fail closed |
| Stale ALLOW after revoke | Version invalidation fanout |
| Conflicting allow/deny rules | Deny-wins precedence explicit |
| Break-glass past TTL | Hard DENY + alert |
| Principal credential rotated | Old token DENY within skew window |
| Policy eval exceeds budget | DENY on sensitive resources |
| Audit sink full | Buffer + fail closed money |
| Regional replica lag | Money DENY if version stale |
| Policy injection attempt | Signature verify reject |
| PEP bypass direct DB | Network policy block + audit |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|---|---|---|---|---|
| Service principals | 2K | 20K | 200K | 2M |
| Authz checks / s | 50K | 500K | 5M | 50M |
| Policy documents | 500 | 5K | 50K | 500K |
| Cached hit rate target | 90% | 93% | 95% | 97% |
| Audit events / day | 4B | 40B | 400B | 4T sampled |
| Break-glass / day | 5 | 20 | 100 | 500 |
| PDP regions | 2 | 3 | 6 | 12 |

**Split QPS classes:** writes ≠ reads ≠ async fanout ≠ audit export. Do not lump into one number.

**What each jump forces:**

- **10×:** PEP sidecar rollout; Redis decision cache; audit batching.  
- **100×:** Sharded PDP read path; sample audit for read-only checks; policy CDN.  
- **1,000×:** Regional PEP clusters; aggressive cache; compile policies to bytecode.

### 1.5 Etc. (Constraints & Assumptions)

- Integer minor units for money.
- Exactly-once effect via idempotency keys.
- Typed stable API errors.
- Regional failure: fence, replay, recon.

**Scope statement:**

> Design internal authorization from ~50K checks/s to 1000x fail-closed.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
50K checks/s × ~500 B ≈ 25 MB/s decision traffic baseline.
Peak/average ratio ~3–4× for burst planning
Split classes: sync writes, sync reads, async workers, audit/export
```

### 2.2 Storage

```text
Audit 4B/day × 200 B ≈ 800 GB/day — tier to cold in hours.
Idempotency records: same order as writes; retain long for money paths
Audit/log: append-only; tier hot → cold object store
Unit-check discipline: 1e9 rows × 1 KB = 1 TB (not PB)
```

### 2.3 Bandwidth

```text
Policy bundle push ~MB on version change infrequent.
Internal replication (WAL/outbox) similar order to write bandwidth
```

### 2.4 Memory

```text
PEP cache 50M entries × 64 B impossible — LRU hot principals only.
Working set for hot keys: partition by hash; never single global Redis
```

### 2.5 Bottleneck ranking (interview)

1. Uncached eval CPU 2. Audit write amp 3. Invalidation fanout 4. Policy complexity

**Say early:** correctness and API semantics > raw QPS.

### 2.6 Domain-specific note

```text
Separate money PEP (strict timeout) from analytics PEP.
```

---

## 3. High-Level Design

### 3.1 Core entities

```text
Resource
  IdempotencyRecord
  AuditEnvelope
  OutboxEvent
Directory: tenant/shard → home cell (epoch)
IdempotencyRecord (key, hash, status, response)
Outbox → downstream at-least-once (consumers idempotent)
AuditEnvelope (who, when, request_id, diff)
```

### 3.2 Sacred invariant

```text
Accept implies durable commit before ACK; idempotent keys prevent double effect
```

**Deal-breaker:** acknowledging success before durable commit on money-adjacent paths.

### 3.3 Core protocol

```text
Auth validate TX idempotency domain write outbox commit ACK
```

**Ordering:** durable local state **before** external side effects (rail, webhook, third-party route).

### 3.4 API surface (product)

| API | Semantics |
|---|---|
| `POST /v1/resources` | Idempotent / typed errors / RYW where applicable |
| `GET /v1/resources/{id}` | Idempotent / typed errors / RYW where applicable |

Stripe-flavored: `Idempotency-Key`, `Request-Id`, typed errors, expandable objects.

### 3.11 Policy-as-data model

Policies stored as signed JSON/RegO bundles with monotonic `policy_version`.
Services embed **no** authorization rules in application code — only PEP calls.

### 3.12 PEP / PDP separation

```text
PEP (sidecar): extract (principal, action, resource) → cache → PDP → audit
PDP (stateless pool): load policy version → evaluate → return ALLOW/DENY + obligations
```

### 3.13 Break-glass workflow

Dual approver via ticketing integration → `break_glass_grants` row → PDP injects temporary rule → max TTL 4h → page SecOps → enhanced audit.

### 3.14 Fail-closed matrix

| Path | PDP down | Timeout |
|------|----------|---------|
| Post journal / payout | DENY | DENY |
| Read dashboard analytics | DENY or cached ALLOW (flag) | Short cache only |


### 3.5 Read path

| Data class | Consistency | Mechanism |
|------------|-------------|-----------|
| Money / inventory / assignment state | Strong RYW | Home cell + version |
| Lists / dashboards / rankings | Eventual OK | Replicas + cache with SLO |
| Audit history | Strong per id | Primary or bounded-lag replica |

### 3.6 Async / integration

```text
Domain TX commits → outbox row
Worker claims with lease → external call with stable idempotency key
Timeout → inquiry, not blind new key
Ledger: journal_key = f(domain_transition_id) where applicable
```

### 3.7 Multi-region

| Plane | Mode |
|-------|------|
| API edge | Active-active |
| Durable writes | **Home cell per shard** |
| Reads | RYW via home; stale OK for analytics |
| Failover | Epoch fence + WAL/outbox replay + recon |

### 3.8 Storage trade-offs

| Data | Store | Why |
|------|-------|-----|
| Primary domain rows | Strong SQL / Spanner | TX + constraints |
| Idempotency | SQL unique + cache | Correctness + speed |
| Outbox | Same TX as domain | Reliable async |
| Audit | Append-only log | Compliance |
| Cache | Redis with TTL | Latency — not SoT for money |

### 3.9 Rollout & operations

- **Dark launch:** shadow traffic, compare outputs.  
- **Feature flags:** per-tenant rollout; default safe on outage.  
- **Expand/contract migrations:** nullable column → backfill → enforce.  
- **Recon jobs:** compare external vs internal; open breaks as tickets.  
- **Runbooks:** stuck PROCESSING, failover, hot shard, DLQ depth.

### 3.10 Deal-breakers (say early)

| Temptation | Failure |
|---|---|
| ACK before durable | Ghost state |
| Skip idempotency | Double effect |
| Multi-master shard | Split brain |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Microservices → PEP sidecar → Decision cache → PDP cluster → Policy Store (versioned)
                                    ↓
                              Audit Log (immutable)
```

### 4.2 Allow check (cache miss)

Service RPC → PEP intercept → cache miss → PDP eval v42 → ALLOW → cache 60s → audit → proceed

### 4.3 Revoke propagation

Admin removes role → policy v43 published → pub/sub `invalidate(principal_id)` → all PEPs drop cache entries

### 4.4 Break-glass

Ticket approved ×2 → POST /break-glass/grant → PDP includes temp rule → expires → DENY resumes

### 4.5 Regional failure

US-East PDP degraded → PEP uses replica policy read-only same version → if stale version → money DENY


---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable** before client success on critical writes.  
2. **Idempotent mutations** by `(tenant, idempotency_key)` + body hash.  
3. **Append-only audit** — corrections are new records, not edits.  
4. **Single-writer home** per shard for strong consistency domains.  
5. **Outbox** for async side effects; at-least-once with idempotent consumers.  
6. **Fencing tokens** on failover to prevent zombie writers.  
7. **Integer money** where applicable — no floats.  
8. **Recon breaks** visible — never silent fix.  
9. **Typed errors** — idempotent replay must not flip 200↔500 arbitrarily.  
10. **Rate limit + auth** fail closed on money paths when uncertain.

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Client retry storm | Idempotency + 409 PROCESSING policy |
| Worker crash after external success | Inquiry + stable external key |
| Hot shard | Split keyspace; isolate tenant; shed reads |
| Regional partition | Home cell authority; edge read-only degrade |
| Cache stampede | Jitter TTL; single-flight |
| Poison message | DLQ + alert |
| Schema migration error | Expand/contract; rollback flag |

**Resolved:** "exactly-once" = **idempotency keys + durable TX + no second economic effect**.

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Modular monolith; single primary DB; basic cache |
| 10× | Service boundary; outbox; idempotency cache; read replicas |
| 100× | Shards + directory; cells; hot-key isolation; cold tier |
| 1000× | Regional homes; stream processors; adaptive shed; archive tier |

**Hotspot patterns:** detect early via p99 skew; isolate; preaggregate; never weaken invariants.

### 5.3 Maintainability

- Property tests for domain invariants.  
- Contract tests for API error shapes and replay behavior.  
- Chaos drills: kill after commit, duplicate requests, failover mid-TX.  
- Versioned recipes / policies / workflow definitions.  
- Ops dashboards: idempotency age, outbox lag, recon open count.

### 5.4 Progressive scale deep dive

**1× (baseline):** Single region primary; TX per write; idempotency unique constraint; nightly recon.

**10×:** Extract service; Redis cache; outbox workers; continuous recon; feature flags.

**100×:** Directory sharding; cells; hot tenant isolation; CQRS read models.

**1000×:** Multi-region homes; time partitions; adaptive concurrency; archive tier; load shed reads first.

### 5.5 Concurrent same-key retries

```text
T0: Request A inserts idempotency PROCESSING
T1: Request B conflicts → 409 Retry-After or short poll
T2: A commits COMPLETE
T3: B reads COMPLETE → returns same response
Sweeper resolves stuck PROCESSING via inquiry — never new business key
```

### 5.6 Cross-shard operations

Prefer **single-shard TX**. Cross-shard: saga + outbox + compensating steps; document eventual completion.

### 5.7 Cache coherency

Money/inventory reads: short TTL + version OR bypass cache. Hint caches OK when stale SLO documented.

### 5.8 Rollout: dark launch

Shadow compare → cohort flag ON → authoritative cutover → remove legacy. Instant rollback = flag OFF + recon.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Float money | Rounding exploits |
| Edit audit history | Compliance failure |
| Multi-master same shard | Split brain |
| Skip idempotency | Double effect |
| ACK before durable | Ghost state |

### 5.10 ABAC attribute pipeline

Fetch merchant_tier, env, cell_id from directory with 30s cache. Missing attribute → DENY on sensitive actions.

### 5.11 Policy compilation

Compile RegO to WASM for fast eval; cache compiled artifact per policy_version.

### 5.12 Decision audit sampling

100% money mutations; 1% sample read-only checks at 1000× to control cost.

### 5.13 Shadow policy rollout

Run v43 shadow alongside v42; log decision diffs; zero user impact until cutover.

### 5.14 Obligations pattern

ALLOW may carry obligations: mask_fields, require_dual_control — PEP enforces downstream.

### 5.15 Cross-service delegation tokens

Narrow JWT: action=read, resource=journal/123, TTL 5m — PDP validates chain.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|---|---|
| Model | RBAC+ABAC policy-as-data signed |
| Eval | PEP cache + PDP pool |
| Failure | Fail closed money |
| Audit | Every decision with version |
| Break-glass | Dual control TTL |

### 6.2 Risks

1. Stale cache after revoke
2. PDP overload cascade
3. Policy complexity regression
4. Break-glass abuse
5. Audit cost at 1000×

### 6.3 45-minute interview plan

| Min | Focus |
|---|---|
| 0-5 | Scope |
| 5-15 | API+entities |
| 15-25 | Idempotency |
| 25-35 | Multi-region |
| 35-45 | Scale |

---

## 7. Deeper / Related Interview Questions

### 7.1

**Q: Fail open or closed?**  
A: Closed for money; configurable read-only.

### 7.2

**Q: Cache invalidation?**  
A: Policy version bump + pub/sub by principal prefix.

### 7.3

**Q: 50M checks/s?**  
A: Shard PDP; PEP cache; sample audit.

### 7.4

**Q: ABAC vs RBAC?**  
A: Both — roles coarse, attributes fine.

### 7.5

**Q: Break-glass?**  
A: Dual approve, TTL, enhanced audit.

### 7.6

**Q: Service mesh?**  
A: PEP as ext_authz filter.

### 7.7

**Q: Policy rollback?**  
A: Revert version pointer; invalidate all caches.

### 7.8

**Q: Deny default?**  
A: Yes explicit allow only.

### 7.9

**Q: Audit tamper?**  
A: Hash chain to immutable store.

### 7.10

**Q: Integration access mgmt?**  
A: Human roles synced; machines separate.

### 7.11

**Q: Latency budget?**  
A: 5ms cached 30ms uncached.

### 7.12

**Q: Trap ACL in code?**  
A: Policy-as-data.

### 7.13

**Q: Trap fail open outage?**  
A: Never payouts.

### 7.14

**Q: Shadow mode?**  
A: Log diffs pre-cutover.

### 7.15

**Q: Cross-region?**  
A: Replicate policy; version sync.

### 7.16

**Q: Principal types?**  
A: Service mTLS vs human SSO.

### 7.17

**Q: Obligations?**  
A: ALLOW with conditions enforced by PEP.

### 7.18

**Q: Policy testing?**  
A: CI matrix per bundle.

### 7.19

**Q: Seccomp bypass?**  
A: Network deny direct data plane.

### 7.20

**Q: Retention?**  
A: Years immutable audit.

---

## 8. Appendices

### 8.1 Schema sketches

```text
policies(id, version, body, signature, published_at)
principals(id, type, attrs_json)
role_bindings(principal_id, role, scope)
authz_decisions(id, principal, action, resource, decision, policy_version, inputs_hash, ts)
break_glass_grants(id, principal, approvers, reason, expires_at)
```

### 8.2 API request/response sketch

```text
POST /v1/authz/check
{ principal: svc_payments, action: post_journal, resource: book/mer_1 }
→ { allowed: true, policy_version: 42 }
```

### 8.3 State machine

```text
PolicyVersion: draft → published → deprecated; Grant: active → expired
```

### 8.4 State / status checklist

- [ ] Resource lifecycle states enumerated  
- [ ] Idempotency: PROCESSING / COMPLETE / FAILED  
- [ ] Home cell epoch monotonic on failover  
- [ ] Outbox published_at null until worker ack  
- [ ] Audit actor + request_id on every mutation  

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Idempotency TX, integer money if applicable, basic audit |
| 10× | Outbox, cache, service split, recon jobs |
| 100× | Sharding, directory, hot isolation, CQRS reads |
| 1000× | Regional homes, partitions, archive tier, load shed |

### 8.6 Pseudocode

```text
function check(p,a,r):
  k=cacheKey(p,a,r,currentPolicyVersion)
  if hit: return hit
  d=pdp.eval(p,a,r,currentPolicyVersion)
  audit(p,a,r,d); cache.set(k,d,ttl); return d
```

### 8.7 Reliability / chaos drills

1. Duplicate POST same key → one resource.  
2. Kill pod after commit before response → client retry → same 200.  
3. Failover mid-TX → fence → no duplicate outbox side effect.  
4. External timeout → inquiry path → no double external call.  
5. Hot key storm → rate limit + isolate shard.  

### 8.8 Glossary

| Term | Meaning |
|---|---|
| PEP | Policy Enforcement Point — local to service |
| PDP | Policy Decision Point — central evaluator |
| ABAC | Attribute-based access control |
| Break-glass | Emergency time-boxed grant |

### 8.9 Interview "say this" (60 seconds)

> We expose Stripe-style APIs with mandatory idempotency on mutations, durable commit before ACK, and typed errors. Strong-consistency domains use single-writer home cells with directory routing. Async work uses transactional outbox; external calls use stable idempotency keys and inquiry on timeout. Failover uses epoch fencing and recon before resuming money paths. We never use floats for money, never mutate audit history, and treat reconciliation breaks as first-class ops objects.

### 8.10 Related systems map

```text
API Edge → Internal Authorization System → Domain Store
                              │
                              ├─► Idempotency / Audit
                              ├─► Outbox → Workers → External / Ledger / Webhooks
                              └─► Metrics / APM / Rate limits
```

Related docs: access-management, ledger-bookkeeping, payment-processing.

### 8.11 HLD vs integration round

| Round | What you do |
|-------|-------------|
| **System design (this)** | APIs, data model, invariants, failure, scale, rollout |
| **Integration coding** | Parse Stripe docs, call APIs, transform JSON |

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| Float dollars | Integer minor units |
| CRDT for money/inventory SoT | Single-writer + TX |
| 24h idempotency TTL on payments | Retain for years |
| Global queue for all tenants | Per-tenant shuffle shard |
| Exactly-once HTTP marketing | At-least-once + idempotent consumers |

### 8.13 Ops metrics

- write_success / write_conflict_409 / write_latency_p99  
- idempotency_processing_age_p99  
- outbox_lag_seconds  
- recon_break_open_count  
- cell_epoch / failover_count  
- cache_hit_rate / stale_read_blocked  

### 8.14 Manual override controls

```text
POST /v1/admin/...  (dual control, reason code, audit sink)
```

### 8.15 Failure mode summary

| Component | Failure | User-visible | Mitigation |
|-----------|---------|--------------|------------|
| Home DB | Primary down | Write errors fail closed | Failover + fence |
| Idempotency | Stuck PROCESSING | 409 retry | Sweeper + inquiry |
| Outbox worker | Lag | Delayed side effects | Scale workers; alert |
| External API | Timeout | Pending state | Inquiry |
| Cache | Stale | Wrong read if misused | Version check |
| Edge region | Partition | 503 or route home | Directory health |

### 8.16 Sharding key selection

```text
Good: tenant_id, merchant_id, geo_cell, resource_id hash
Bad: status alone, country alone — hotspots
Reshard: dual-write + directory epoch bump + backfill verify
```

### 8.17 Compliance & audit

Immutable audit with retention tiers; legal hold; PII minimization; break-glass access with ticket.

### 8.18 Sample recon query

```text
daily: compare sum(internal) vs sum(external) per tenant
if |delta| > threshold → open recon_break
block automated money movement if severity=critical (policy)
```

---

*End of internal authorization system system design.*

### 8.19 Internal Authorization System — rollout checklist

- [ ] Idempotency replay tests in CI  
- [ ] Failover runbook with epoch fencing  
- [ ] Recon job covers external dependencies  
- [ ] Feature-flag default safe on outage  
- [ ] Load test with 5% retry injection  

### 8.20 Internal Authorization System — load test profile

```text
warmup 10m @ 50% peak → ramp 10m → soak 60m @ peak
inject: 5% duplicate idempotency keys, 1 regional failover at t=30m
assert: zero duplicate domain effects, recon breaks < threshold
```
