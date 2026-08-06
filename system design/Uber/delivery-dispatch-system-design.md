# System Design: Delivery Dispatch System

> **Focus areas:** Courier assignment · Batching · SLA · Offer/accept · Geospatial matching · Reassignment · Fairness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — **assigning couriers to delivery tasks under ETA/SLA constraints**

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

Goal: design a dispatch system that assigns couriers to pickup/dropoff delivery tasks (food/packages), optionally batches, and meets promise SLAs under failure.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Dispatch/assignment engine | Full menu catalog |
| Truth | Task + assignment leases | Courier GPS database itself |
| Batching | Optional multi-stop | Vehicle routing research OR-Tools deep dive |
| Uber lens | SLA + courier experience | Perfect global optimum always |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Tasks? | Pickup→dropoff legs | DeliveryTask entity |
| F2 | Couriers? | Online supply from location svc | Nearby candidates |
| F3 | Offer? | Push offer accept/reject | Offer FSM |
| F4 | Batching? | Same restaurant / nearby drops | Batcher module |
| F5 | SLA? | Promise pickup/deliver-by | Scorer with deadlines |
| F6 | Reassign? | Cancel/no-show | Recovery flows |
| F7 | Priority? | VIP / late risk | Scoring weights |
| F8 | Constraints? | Vehicle type, hot bag, distance | Filters |
| F9 | Idempotency? | Task create retries | Keys |
| F10 | Multi-city? | Yes | City cells |
| F11 | Manual? | Ops assign | Admin API |
| F12 | Feedback? | Accept rates, cancels | Metrics loop |

**MVP functional scope (lock with interviewer):**

1. Create delivery task from order with pickup/dropoff + SLA timestamps.
2. Find nearby eligible couriers; score; send offer.
3. Accept → assign; timeout → next courier.
4. Track assigned→at_store→picked→delivered.
5. Reassign on fail; basic single-task (no batch) MVP ok.
6. Metrics: assign latency, offer accept rate, SLA breach.

**Out of MVP (explicitly defer):**

- Global optimal VRPTW solver always
- Autonomous robots
- Cross-city courier roaming markets

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Assign latency | Time to first offer | p50 seconds-class; p99 bounded |
| N2 | Fresh locations | Matching quality | Use location freshness SLA |
| N3 | Durability | No lost tasks | Persist tasks/offers |
| N4 | Fairness | Avoid starving couriers | Rotation/caps |
| N5 | Availability | City isolation | Degrade batching first |
| N6 | Consistency | One assignee | Lease/fencing |
| N7 | Scale | Dinner peaks | See table |
| N8 | Safety | No cross-tenant leak | Authz |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Task created → offer → accept → pickup → deliver.
2. First courier rejects → next candidate quickly.
3. Batch two orders same restaurant → one courier.
4. Courier cancel → reassign with late-risk boost.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| No couriers nearby | Expand radius / inflate ETA / queue |
| Double accept race | CAS assign winner; other release |
| Stale location | Filter by freshness |
| Offer after task canceled | Reject |
| Hot restaurant spike | Batch + radius expand |
| Courier multi-assign bug | Presence lease prevents |
| Stadium network blip | Offer timeout + retry |
| Ops force assign | Audited override |

### 1.4 Scales (Progressive)

| Metric | Baseline city | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Tasks/day | 200K | 2M | 20M | 200M |
| Peak assign QPS | 30 | 300 | 3K | 30K |
| Online couriers | 3K | 30K | 300K | 3M |
| Offers/task avg | 1.4 | 1.6 | 2.0 | 2.0 |
| Cities | 1 | 20 | 200 | 2000 |

**What each jump forces:**

- **10×:** Shard by city; candidate index from location service
- **100×:** Scoring service; batcher; offer parallelization
- **1,000×:** Hierarchical dispatchers; learned scoring with caps

### 1.5 Etc. (Constraints & Assumptions)

- Design for retries, idempotency, and city/region isolation.
- Fail closed on authz/money; degrade intentionally on non-critical paths.
- Peak ≠ average; stadium/airport spikes are first-class.
- Location service provides nearby/get APIs.
- Order service owns customer order FSM; dispatch owns DeliveryTask assignment.

**Scope statement:**

> City-sharded delivery dispatch with task SOR, courier offers, scoring, optional batching, reassignment, and SLA-aware prioritization.

---

## 2. Back-of-the-Envelope Estimation

### Assign load

```text
Dinner peak tens–hundreds assigns/s/city; each may query nearby + score top K
```

### State

```text
Active tasks ~ concurrent deliveries; 10K active × 1KB fine in memory+DB
```

### Offers

```text
1.5× tasks → offer QPS slightly above assign
```

### Bottlenecks (rank ordered)

1. Courier supply shortage
2. Hot pickup locations
3. Stale geo candidates
4. Offer chatty mobile
5. Over-batching hurting ETA
6. Single global scorer bottleneck

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
DeliveryTask
Stop (pickup/dropoff)
Offer
Assignment (lease)
CourierEligibility
BatchPlan
ScoreContext
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Push first courier FIFO | Simple | Poor SLA | Dense cities |
| B. Score top-K each tick | Good quality | Compute cost | — chosen |
| C. Continuous auction | Market efficient | Complexity/UX | Later |
| D. Pure human ops | Control | No scale | Incidents only |

**Chosen path:**

- Task SOR + periodic/ event-driven matcher that scores nearby couriers, sends time-bounded offers, CAS-assigns on accept.
- Batching as optimization layer on top.

### 3.3 Core design mechanics

**Assign loop:**
```text
on task READY_TO_DISPATCH or timer:
  candidates = location.nearby(pickup, r) filtered eligible
  ranked = score(candidates, sla_risk, distance, load, accept_prob)
  send offers to top N (seq or small parallel)
on accept: CAS assign if still open
on timeout/reject: next
```

**Assignment invariant:** at most one courier lease owner; fencing token on task.

**Batching:** group tasks with compatible pickup and dropoff detour bounds; score batch utility vs singles.

### 3.4 API sketch

```text
POST /tasks {order_id, pickup, dropoff, sla}
POST /tasks/{id}/cancel
POST /offers/{id}/accept|reject
GET  /tasks/{id}
POST /admin/tasks/{id}/force_assign
```

### 3.5 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Parallel offers | Speed vs overbooking risk |
| Batching | Efficiency vs ETA risk |
| Larger radius | Fill rate vs long pickup |
| Learned scores | Quality vs explainability |



---

## 4. Architecture Diagram

```text
Order Service → Task API → Task DB
                     ^          |
                     |          v
              Offer responses   Matcher Workers ← Location nearby
                     |          |
                     v          v
                 Courier App   Assignment + Notify
                     |
                     +→ optional Batcher
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- Durable tasks before ACK.
- CAS assignment.
- Offer timeouts server-side.
- Redispatch paths.
- Idempotent task create.

**Delivery / consistency cheat-sheet**

| Layer | Guarantee |
|-------|-----------|
| Client → API | At-least-once; idempotency keys where mutations exist |
| System of record | Single-writer per entity / partition key |
| Downstream effects | At-least-once via outbox/stream; idempotent consumers |
| Reads | Read-your-writes on primary; replicas may lag |

**Deal-breakers**

- Two couriers assigned same task
- Lost tasks after place
- Ignoring freshness of courier locations

### 5.2 Scalability

- City shards; matcher pull partitions.
- Cache eligibility.
- Limit K candidates.
- Separate hot-zone matchers.

**Progressive evolution**

| Scale | Architecture posture |
|-------|----------------------|
| Baseline | Single region/city; simple durable store + stream |
| 10× | Shard by city/entity; split hot paths |
| 100× | Cells, async fan-out, careful caching, hot-key splits |
| 1,000× | Hierarchical aggregation, edge where safe, strict cost/isolation |

### 5.3 Maintainability

- Score weight configs versioned.
- Replay matcher decisions for disputes.
- Shadow new scorers.

- Versioned schemas/configs with rollback.
- Golden fixtures and replay tools for disputes/regressions.
- Published ownership boundaries between services.
- SLOs tied to user-visible failures; load-test stadium/airport peaks.

### 5.4 Multi-region clarity

| Plane | Mode |
|-------|------|
| Edge / API gateways | Active-active |
| Mutable entity writes | Home cell / city region single-writer |
| Caches / projections | Regional, eventually consistent |
| Analytics | Async lake / warehouse |

### 5.5 Security, privacy, abuse

- Courier can only accept offers aimed at them.
- Admin force audited.
- No leaking other couriers' locations to apps.

---

## 6. Wrap-Up

**What to say in 60 seconds**

> Dispatch turns delivery tasks into fenced courier assignments via nearby candidate retrieval, scoring, time-bounded offers, and reassignment—optionally batching—sharded by city and measured on SLA risk.

**MVP → next**

1. MVP: invariants + audit/outbox + single-city correctness.
2. Next: sharding, richer consumers, degradation playbooks.
3. Later: edge optimizations, hierarchical aggregation, advanced models with caps.

**Top risks**

| Risk | Mitigation |
|------|------------|
| Hot keys / stadiums | Split shards, jitter, admission control |
| Retry storms | Idempotency, client jitter, coalescing |
| Inconsistent side effects | Outbox + consumer idempotency |
| Cost explosion | Sampling, TTL, tiered storage |
| Trust / correctness bugs | Audit, clamps, kill switches |

---

## 7. Deeper / Related Interview Questions

### Matching

**Q: Parallel offers?**  
A: Possible with careful withdraw; MVP sequential is safer.

**Q: Batch vs single?**  
A: Batch when detour bound satisfied and SLA safe.

### Failures

**Q: Courier disappears after accept?**  
A: Lease heartbeats / location TTL → reassign.

### Scale & multi-region

**Q: How do you shard?**  
A: City/region cell first, then hash entity id within the cell.

**Q: Active-active writes for the same entity?**  
A: Avoid; home-cell single-writer with fencing on failover.

**Q: What do you shed first under load?**  
A: Non-critical analytics/marketing; protect money, safety, and trip-critical paths.

### Interview arithmetic / trap questions

**Q: When do units go wrong?**  
A: Mixing MB/GB/PB; using average instead of peak; forgetting retries amplify QPS; storing forever without sampling.

**Q: What do you defer explicitly?**  
A: Active-active multi-writer; perfect exactly-once for arbitrary side effects; unbounded history in primary OLTP.

**Q: What is the system of record?**  
A: Name it aloud—everything else is a projection/cache.

---

## 8. Appendices

### 8.1 Task schema

```json
{"task_id":"t","state":"OFFERING","pickup":{},"dropoff":{},"sla_deliver_by":"...","assignee":null}
```

### 8.2 Score sketch

```text
score = w1*(-pickup_eta) + w2*(-sla_risk) + w3*accept_prob + w4*(-load) + w5*fairness
```

### 8.3 States

```text
PENDING→OFFERING→ASSIGNED→AT_PICKUP→PICKED_UP→DELIVERED / CANCELED
```

### 8.4 SLOs

| SLO | Target |
|-----|--------|
| Time-to-assign p50 | low minutes/seconds |
| Double assign | 0 |
| SLA breach rate | monitor + alert |

### Interview checklist

- [ ] Clarified MVP vs out-of-scope
- [ ] Progressive 10×/100×/1000× impacts stated
- [ ] Estimation with peak ≠ average
- [ ] Single-writer / fencing story
- [ ] Idempotency + retries
- [ ] ASCII architecture
- [ ] Reliability / scalability / maintainability deep dive
- [ ] Explicit deal-breakers
- [ ] Deeper Q&A ready
- [ ] Audit / privacy / money hooks if relevant

---

*End of delivery dispatch system system design.*

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.
