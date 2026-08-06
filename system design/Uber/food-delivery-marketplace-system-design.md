# System Design: Food Delivery Marketplace

> **Focus areas:** Restaurants · Menus · Cart/checkout · Order FSM · Courier hooks · ETA · Catalog search · Ratings  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — **Uber Eats-style three-sided marketplace (diner, restaurant, courier)**

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

Goal: design a food-delivery marketplace covering catalog, cart/checkout, order lifecycle, restaurant acceptance, and courier delivery hooks with ETAs.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Eats marketplace core | Full maps/navigation stack |
| Sides | Diner + restaurant + courier | Single-restaurant POS only |
| Truth | Order FSM + catalog versions | Courier GPS store internals |
| Uber lens | Promise ETA + accurate catalog | Pretty photos alone |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Catalog? | Menus, items, modifiers, hours | Versioned catalog |
| F2 | Discovery? | Feed/search/nearby | Geo + rank |
| F3 | Cart? | Modifiers, fees, promos | Cart service |
| F4 | Checkout? | Pay + place order | Idempotent place |
| F5 | Restaurant? | Accept/reject/prep time | Merchant app APIs |
| F6 | Courier? | Dispatch handoff | Delivery task created |
| F7 | ETA? | Prep + courier legs | ETA service |
| F8 | Live tracking? | Courier map | Location subscribe |
| F9 | Ratings? | Restaurant/courier/diner | Async |
| F10 | Refunds? | Missing item etc. | Order adjustments |
| F11 | Scheduling? | ASAP + scheduled | Promise windows |
| F12 | Multi-restaurant cart? | Usually no in MVP | Explicit defer |

**MVP functional scope (lock with interviewer):**

1. Browse nearby restaurants + menu read models.
2. Cart with modifiers/fees; quote totals.
3. Place order idempotently; pay via payments API.
4. Restaurant accept/reject; prep timer.
5. Create delivery task; track states to delivered.
6. Basic ETA + push notifications on transitions.

**Out of MVP (explicitly defer):**

- Multi-restaurant carts
- Dark kitchen optimization OR
- Full ads auction platform

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Browse latency | Feed/menu | p99 < 300–500ms |
| N2 | Place order | Checkout | p99 < 1–2s + pay |
| N3 | Catalog freshness | Hours/86'd items | minutes or better for 86 |
| N4 | Order durability | No lost placed order | Persist before ACK |
| N5 | Availability | City cells | Degrade discovery first |
| N6 | Consistency | Order single-writer | Strong per order |
| N7 | Scale | Lunch/dinner peaks | See table |
| N8 | Money | Idempotent pay | Payments API |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Search → menu → cart → pay → restaurant accept → courier pickup → deliver → rate.
2. Item 86'd before accept → diner notified / partial path.
3. Scheduled order fires at promise window.
4. Refund missing item post-delivery.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Restaurant offline mid-checkout | Fail place or reroute policy |
| Double place tap | Idempotency key |
| Accept after timeout | Reject; cancel/refund path |
| Courier cancel after pickup | Redispatach; diner comms |
| Menu version drift | Pin menu version on cart |
| Payment fail | No order accept |
| Storm lunch peak | Admission control; prep time inflation |
| Address outside zone | Reject early |

### 1.4 Scales (Progressive)

| Metric | Baseline city | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Orders/day | 200K | 2M | 20M | 200M |
| Peak place QPS | 50 | 500 | 5K | 50K |
| Restaurants | 5K | 50K | 500K | 5M |
| Menu reads QPS | 5K | 50K | 500K | 5M |
| Active couriers | 3K | 30K | 300K | 3M |

**What each jump forces:**

- **10×:** City sharding; catalog CDN/read replicas
- **100×:** Order cells; feed ranking platform; 86 propagation bus
- **1,000×:** Global multi-cell; hierarchical discovery; strict peak tooling

### 1.5 Etc. (Constraints & Assumptions)

- Design for retries, idempotency, and city/region isolation.
- Fail closed on authz/money; degrade intentionally on non-critical paths.
- Peak ≠ average; stadium/airport spikes are first-class.
- One restaurant per order in MVP.
- Dispatch algorithm can be a separate service behind an interface.

**Scope statement:**

> Three-sided food marketplace with catalog, cart/checkout, order FSM, restaurant acceptance, courier delivery handoff, ETAs, and city-scaled read/write paths.

---

## 2. Back-of-the-Envelope Estimation

### Orders

```text
200K/day ≈ 2.3/s avg; peak 20–50× lunch → tens of place/s; reads dominate
```

### Catalog

```text
5K restaurants × ~200 items × 500B ≈ 500MB raw; serve via cached read models
```

### Events

```text
Each order ~20–50 events → millions/day telemetry
```

### Bottlenecks (rank ordered)

1. Lunch peak place+pay
2. Menu read storms
3. 86/item availability races
4. Dispatch under courier shortage
5. ETA accuracy complaints
6. Hot celebrity restaurants

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Restaurant
CatalogVersion / MenuItem / Modifier
Cart
Order (FSM)
FulfillmentTicket (restaurant)
DeliveryTask
ETAPromise
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Monolith marketplace | Simple MVP | Scale coupling | OK early |
| B. Split catalog/order/dispatch | Scale | Consistency work | — chosen at 10× |
| C. Fully event-sourced everything | Audit | Complexity | Orders yes; menus maybe not |
| D. Per-restaurant SaaS only | Merchant focus | Not diner marketplace | Wrong product |

**Chosen path:**

- Read-optimized **catalog/feed** plane + **order orchestration** SOR + interfaces to **payments**, **dispatch**, **notify**.
- Pin catalog/fee versions on cart/order for audit.

### 3.3 Core design mechanics

**Order FSM (MVP):**
```text
PLACED → RESTAURANT_ACCEPTED → PREPARING → READY_FOR_PICKUP
      → COURIER_ASSIGNED → PICKED_UP → DELIVERED
      → CANCELED / REJECTED
```

**Place order:** validate cart snapshot → pay auth/capture policy → persist order → notify restaurant → 200.

**86 item:** catalog update event → invalidate item availability; in-flight orders policy (substitute/refund).

**ETA:** prep_time_est + courier_to_store + store_to_diner (+ buffers). Recompute on state changes.

**Invariant:** placed order durable; money and order linked by ids; menu prices auditable via version.

### 3.4 API sketch

```text
GET  /restaurants/nearby
GET  /restaurants/{id}/menu
POST /carts/{id}/items
POST /orders  Idempotency-Key
POST /orders/{id}/restaurant/accept|reject
POST /orders/{id}/ready
GET  /orders/{id}
POST /orders/{id}/cancel
```

### 3.5 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Pinned menu version | Audit vs flexibility |
| Sync pay on place | Trust vs latency |
| Separate dispatch | Modularity vs race windows |
| Aggressive caching menus | Speed vs 86 staleness |



---

## 4. Architecture Diagram

```text
Diner App → API GW → Feed/Catalog reads (cache)
                   → Cart Service
                   → Order Service (SOR) → Payments
                         | outbox
                         +→ Restaurant apps
                         +→ Dispatch Service → Couriers
                         +→ Notify / ETA / Analytics
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- Idempotent place.
- Outbox for restaurant/dispatch/notify.
- Payment failure prevents accept path.
- Redispatch on courier fail.
- Catalog version pinning.

**Delivery / consistency cheat-sheet**

| Layer | Guarantee |
|-------|-----------|
| Client → API | At-least-once; idempotency keys where mutations exist |
| System of record | Single-writer per entity / partition key |
| Downstream effects | At-least-once via outbox/stream; idempotent consumers |
| Reads | Read-your-writes on primary; replicas may lag |

**Deal-breakers**

- Lost placed orders
- Charging without order
- Serving allergen-wrong stale modifiers without care
- Dual writers on order state

### 5.2 Scalability

- Shard orders by city.
- Catalog CDN + per-city caches.
- Hot restaurant read replicas.
- Dispatch as separate scaled service.
- Peak mode: longer ETAs, admission.

**Progressive evolution**

| Scale | Architecture posture |
|-------|----------------------|
| Baseline | Single region/city; simple durable store + stream |
| 10× | Shard by city/entity; split hot paths |
| 100× | Cells, async fan-out, careful caching, hot-key splits |
| 1,000× | Hierarchical aggregation, edge where safe, strict cost/isolation |

### 5.3 Maintainability

- Contract tests diner/merchant/courier apps.
- Order timeline UI for support.
- Feature flags for fees/experiments.

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

- Authz per role (diner/merchant/courier).
- PII on addresses minimized in logs.
- Fraud on promo/payment velocity.

---

## 6. Wrap-Up

**What to say in 60 seconds**

> Eats marketplace = cached catalog/discovery + durable order FSM + payments + restaurant acceptance + dispatch handoff. Pin versions for audit, isolate lunch peaks by city cells, and keep availability/ETA honest under stress.

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

### Catalog

**Q: How fast must 86 propagate?**  
A: Target seconds–minutes; pin versions for in-flight carts.

**Q: Who owns price truth?**  
A: Catalog version at checkout snapshot.

### Dispatch boundary

**Q: Is batching in MVP?**  
A: Optional; interface should allow batched delivery tasks later.

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

### 8.1 Order schema

```json
{"order_id":"o","restaurant_id":"r","state":"PREPARING","catalog_version":12,"totals":{"minor":3200},"delivery_task_id":"d"}
```

### 8.2 Place pseudocode

```text
Place(cart, idem): pay → persist ORDER PLACED → outbox RestaurantNotify+DispatchCreate → return
```

### 8.3 ETA

```text
ETA = prep + courier_to_restaurant + restaurant_to_diner + buffer(load)
```

### 8.4 SLOs

| SLO | Target |
|-----|--------|
| Place success ex pay decline | high |
| Accept latency p50 | minutes-class |
| Wrong-item complaints | monitor |

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

*End of food delivery marketplace system design.*

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
