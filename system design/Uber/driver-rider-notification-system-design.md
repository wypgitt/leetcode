# System Design: Driver / Rider Notification Service

> **Focus areas:** Multi-channel push · Preferences · Dedup · Critical priority · Device tokens · Templates · SMS fallback  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — **notification delivery for trip-critical and marketing messages**

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

Goal: design a notification service that delivers trip-critical alerts and preference-compliant marketing across push, SMS, email, and in-app channels.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Notification intents + delivery | Full chat product |
| Truth | Intent + attempts + receipts | OS push internals |
| Priority | Trip/safety > marketing | Spam-max engagement |
| Uber lens | Never miss assignment push | Vanity open rates only |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Triggers? | Trip/pay/safety/growth | Producer API + allowlists |
| F2 | Channels? | Push/SMS/email/in-app | Channel router |
| F3 | Templates? | Localized variables | Versioned templates |
| F4 | Prefs? | Opt-out, quiet hours | Enforce pre-send |
| F5 | Priority? | Critical/normal/marketing | Isolated queues |
| F6 | Dedup? | Yes | dedupe_key window |
| F7 | Devices? | Multi-device | Token registry |
| F8 | Receipts? | Webhooks | Normalize status |
| F9 | Fallback? | SMS if push dead for critical | Channel plan |
| F10 | Rate limits? | Per user/producer | Token buckets |
| F11 | I18n? | Locale/TZ | Template pick |
| F12 | Live trip? | Optional WS | Narrow fan-out |

**MVP functional scope (lock with interviewer):**

1. Durable intent API with priority + dedupe_key.
2. Resolve devices + prefs; suppress marketing correctly.
3. Priority queues + provider workers (FCM/APNs/SMS/email).
4. Retries/backoff/DLQ + receipt webhooks.
5. Critical bypasses quiet hours; SMS fallback.
6. SLOs for latency and opt-out compliance.

**Out of MVP (explicitly defer):**

- Full journey builder product
- Guaranteed global SMS
- On-device template IDE

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Critical latency | Assignment/arrive | p99 < 1–2s to provider accept |
| N2 | Durability | ACK means stored | Persist before ACK |
| N3 | Pref compliance | Legal/product | ~0 marketing violations |
| N4 | Availability | Isolate cities | Shed marketing first |
| N5 | Throughput | Scale table | Shard by user |
| N6 | Ordering | Per-user best effort | Not global total order |
| N7 | PII | Phones/emails | Encrypt; minimize logs |
| N8 | Dedup | Collapse retries | Windowed keys |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Trip assigned → critical push to rider and driver.
2. Dead push tokens → SMS fallback for critical.
3. Duplicate producer retry → single user-visible notify.
4. Marketing respects quiet hours and opt-out.
5. Webhook marks delivered; analytics counts.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Invalid tokens | Scrub; fallback if critical |
| Opt-out marketing | Suppress |
| Provider 429 | Backoff + circuit |
| Missing locale | Fallback locale |
| Safety in quiet hours | Bypass |
| Replay storm | Pace; critical first |
| Poison template | DLQ |
| Many devices | Send all push; collapse id |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Intents/day | 50M | 500M | 5B | 50B |
| Peak intents/s | 5K | 50K | 500K | 5M |
| Users | 20M | 200M | 1B | 2B+ |
| Devices/user | 1.5 | 1.5 | 1.8 | 2 |
| Critical share | 10% | 10% | 10% | 10% |

**What each jump forces:**

- **10×:** Priority lanes; shard by user
- **100×:** Regional cells; paced marketing
- **1,000×:** Marketing as separate batch fan-out; edge render

### 1.5 Etc. (Constraints & Assumptions)

- Design for retries, idempotency, and city/region isolation.
- Fail closed on authz/money; degrade intentionally on non-critical paths.
- Peak ≠ average; stadium/airport spikes are first-class.
- Transactional trip/safety not suppressed by marketing prefs.
- Providers fail; retries + fallbacks required.

**Scope statement:**

> Multi-channel notification platform with durable intents, preference-aware routing, critical-priority isolation, dedupe, retries/fallback, and user/city sharding.

---

## 2. Back-of-the-Envelope Estimation

### Volume

```text
50M/day ≈ 580/s avg; peak ~5K/s
Critical ~500/s; marketing storms paced separately
```

### Storage

```text
Intent+receipt ~700B → ~35GB/day; TTL 7–30d
Tokens: 20M×1.5×200B ≈ 6GB
```

### Fan-out

```text
5K intents/s × 1.5 devices ≈ 7.5K provider calls/s peak baseline
```

### Bottlenecks (rank ordered)

1. Provider rate limits
2. Shared queue starving critical
3. Template CPU
4. Webhook storms
5. Hot users
6. Sync preference lookups

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
NotificationIntent
ChannelPlan
DeviceEndpoint
DeliveryAttempt
Receipt
PreferenceProfile
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Sync send in producer | Simple | Coupling | Trip blocked on FCM |
| B. One queue all prios | Easy | Starvation | Critical delayed |
| C. Priority lanes + adapters | Control | Ops cost | — chosen |
| D. ESP-only | Fast MVP | Less control | Deep trip coupling |

**Chosen path:**

- Durable intents + priority-isolated queues + device registry + templates + provider adapters + webhook receipts.
- 202 after persist; async delivery.

### 3.3 Core design mechanics

**Pipeline:** Produce → dedupe → persist → enqueue(lane) → render → channel plan → provider → receipts.

**Dedupe:** `(user_id, dedupe_key)` returns prior intent.

**Prefs:** marketing suppressed by opt-out/quiet hours; CRITICAL bypasses quiet hours.

**Fallback:** dead push → SMS for critical only.

**Invariant:** ACK ⇒ durable intent; delivery at-least-once; collapse via dedupe.

### 3.4 API sketch

```text
POST /v1/notifications {user_id, template_id, data, priority, dedupe_key}
GET  /v1/notifications/{id}
POST /v1/devices/tokens
DELETE /v1/devices/tokens/{token}
GET/PUT /v1/preferences/{user_id}
POST /v1/provider-webhooks/{provider}
```

### 3.5 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Async delivery | Scale vs sync producer latency |
| SMS fallback | Reliability vs cost |
| Strict prefs | Trust vs send volume |
| Multi-device | Reach vs annoyance |



---

## 4. Architecture Diagram

```text
Producers → Notify API → Intent DB
           |-> CRITICAL queue → workers → Providers
           |-> NORMAL queue
           |-> MARKETING paced queue
Webhooks → Receipts → Analytics
Prefs cache / Token registry
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- Persist before ACK.
- Idempotent produce/send.
- Provider circuit breakers.
- DLQ + replay.
- Dead token scrubbing.
- Campaign pacing.

**Delivery / consistency cheat-sheet**

| Layer | Guarantee |
|-------|-----------|
| Client → API | At-least-once; idempotency keys where mutations exist |
| System of record | Single-writer per entity / partition key |
| Downstream effects | At-least-once via outbox/stream; idempotent consumers |
| Reads | Read-your-writes on primary; replicas may lag |

**Deal-breakers**

- Marketing delaying critical pushes
- Dropping intents after 202
- Ignoring opt-out
- PII-heavy unbounded logs

### 5.2 Scalability

- Shard by user/city.
- Separate pools per priority.
- Cache templates/prefs.
- Regional providers.
- 1000×: marketing batch platform.

**Progressive evolution**

| Scale | Architecture posture |
|-------|----------------------|
| Baseline | Single region/city; simple durable store + stream |
| 10× | Shard by city/entity; split hot paths |
| 100× | Cells, async fan-out, careful caching, hot-key splits |
| 1,000× | Hierarchical aggregation, edge where safe, strict cost/isolation |

### 5.3 Maintainability

- Template locale snapshot tests.
- Provider adapter interface.
- Chaos: 429 storms, webhook dupes.

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

- Producer allowlists by template class.
- Encrypt phones/emails.
- Verify webhook signatures.
- Rate limit producers/users.

---

## 6. Wrap-Up

**What to say in 60 seconds**

> Durable intents, preference-aware channel plans, priority-isolated workers, dedupe, and SMS fallback for critical trip events—scaled by user/city shards without marketing starvation.

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

### Priority & prefs

**Q: Quiet hours block assignment?**  
A: No for critical/transactional.

**Q: Stop double push on retry?**  
A: dedupe_key.

### Providers

**Q: FCM ok but no display?**  
A: Token health + receipts.

**Q: SMS cost blowup?**  
A: Critical-only fallback + budgets.

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

### 8.1 Schema

```json
{"notification_id":"n","priority":"CRITICAL","template_id":"trip.driver_assigned","dedupe_key":"trip:t:assigned"}
```

### 8.2 Pseudocode

```text
Produce: authz → dedupe → persist → enqueue(priority)
Deliver: prefs → suppress? → devices → plan → send → retry/receipts
```

### 8.3 SLOs

| SLO | Target |
|-----|--------|
| Critical p99 | <2s |
| Pref violations | ~0 |
| Dup critical same key | ~0 |

### 8.4 Templates

trip.driver_assigned, trip.driver_arrived, trip.canceled, payments.receipt, safety.*, growth.*

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

*End of driver / rider notification service system design.*

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
