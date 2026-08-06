# System Design: Geo-Distributed Sensor Ingestion

> **Focus areas:** Edge gateways · Time-series · Late/out-of-order · Exactly-once-ish · Geo routing · Downsample · Alerts · Device identity
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **Geo-distributed sensor ingestion** — IoT-scale telemetry with correctness

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-q&a)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design **geo-distributed sensor ingestion**: devices→regional edges, durable ingest, time-series storage, late/out-of-order handling, downsampling, alerts, and device identity/security.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Ingest+store+query sensor telemetry | Full digital twin app suite |
| Data | Time-series points/events | Transactional OLTP orders |
| Amazon lens | Device security, cost/cardinality, regional | Arduino hobby demo |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Devices? | Millions; flaky networks | Offline buffer |
| F2 | Ingest? | MQTT/HTTPS to regional edge | Auth per device |
| F3 | Ordering? | Device time + server time | Late/OOO windows |
| F4 | Storage? | Hot TS + cold tier | Retention policies |
| F5 | Query? | Range aggregates | Downsample |
| F6 | Alerts? | Stream rules | Dedup notifications |
| F7 | Geo? | Write to nearest region | Cross-region query optional |
| F8 | Schema? | Metric registry | Cardinality control |
| F9 | Exactly-once? | Idempotent keys | At-least-once transport |
| F10 | Config? | Desired device state | Control plane |
| F11 | Firmware? | Out of MVP optional | Separate |
| F12 | Multi-tenant? | Customers/sites | Isolation |

**MVP scope:**

1. Device auth ingest
2. Regional edge accept
3. Durable write ahead of ACK
4. TS store hot
5. Basic range query+downsample
6. Late arrival window
7. Alert rules simple
8. Quotas/cardinality guards
9. Dashboards lag

**Out of MVP:** Global strongly consistent sensor state; On-device ML platform; Video camera always-on ingest.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Ingest ACK | p99<100–300ms regional |
| N2 | Durability | No loss after ACK |
| N3 | Late window | configurable e.g. 15m–24h |
| N4 | Query | Interactive aggregates seconds |
| N5 | Avail | Regional degrade ok |
| N6 | Cardinality | Hard caps |
| N7 | Security | Device certs/keys |
| N8 | Cost | Downsample+tier |

### 1.3 Cases

**Happy:** device publish→edge auth→durable→TS; alert fires once; query downsample.
**Edges:** clock skew; burst reconnect; cardinality explosion; poison metric; region fail; duplicate retries; late points after downsample.

| Case | Behavior |
|------|----------|
| Duplicate request | Idempotent key returns same result |
| Partial failure mid-path | Compensate or retry with fencing/CAS |
| Hot partition / noisy neighbor | Shuffle shard + fair-share quotas |
| Region / AZ loss | Cell failover; degrade non-critical |
| Clock skew | Server-side truth; opaque tokens |
| Poison input | Quarantine/DLQ; never silent drop of accepted work |
| Authz miss | Fail closed; audit |
| Traffic surge 10× | Shed by priority; preserve SLO class |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Devices | 1M | 10M | 100M | 1B |
| Points/s | 100K | 1M | 10M | 100M |
| Metrics/device | 10 | 20 | 50 | 100 |
| Regions | 3 | 8 | 20 | 50 |
| Alert rules | 10K | 100K | 1M | 10M |
| Hot retention | 7d | 14d | 30d | 30d+cold |

**Jumps:** 10× edge+TS shard; 100× geo cells+stream alerts; 1,000× hierarchical downsample+edge agg.

### 1.5 Scope repeat-back

> Geo sensor ingest with durable regional ACK, TS storage, late/OOO handling, downsample, alerts, cardinality safety.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Points

```text
1M devices×0.1Hz=100K/s; 200B/point≈160Mbps
```

### 2.2 Cardinality

```text
devices×metrics series explosion
```

### 2.3 Storage

```text
100K/s×86400×200B≈1.7TB/day hot
```

### 2.4 Alerts

```text
stream evaluate subset
```

### 2.X Bottlenecks

(1) Hot keys/partitions (2) synchronous fan-out (3) durable write path (4) auth/token validation (5) downstream blast radius (6) not abstract QPS alone.

### 2.Y Cost / frugality

Prefer cheaper read paths over linear DB growth; measure unit cost per successful customer action; sample observability firehoses.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Edge ingest | Accept/auth | Regional |
| Durable log | WAL/stream | Ordered per partition |
| TS store | Hot/cold | Eventually within window |
| Alert | Rules engine | At-least-once notify |
| Control | Device registry | Strong |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Device Auth** — Certs/keys
2. **Edge Gateway** — MQTT/HTTP
3. **Ingest Router** — Partition by device
4. **Durable Stream** — Kafka/Kinesis-like
5. **TS Writer** — Batch insert
6. **TS DB** — Hot
7. **Downsampler** — Rollups
8. **Query API** — Ranges
9. **Alert Engine** — CEP/rules
10. **Registry** — Devices/tenants
11. **Quota** — Cardinality
12. **Obs** — Lag/loss

### 3.3 API sketch

```text
PUBLISH telemetry {device_id,ts,metrics[],idem}
GET /v1/query?series&from&to&agg
POST /v1/alerts
POST /v1/devices
```

### 3.4 State machine

```text
Point: RECEIVED→DURABLE→WRITTEN→ROLLED_UP
Alert: OPEN→NOTIFIED→RESOLVED (deduped)
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| QoS | At-least-once+idem | Honest |
| Clock | Server receive + device ts | Skew tolerant |
| Agg edge vs center | Hybrid | Cost/latency |
| Schema free | Registry caps | Cardinality |
| Cross-region query | Fanout optional | Complexity |

---

## 4. Architecture Diagram

```text
Devices->Regional Edge->Durable Stream->TS Writers->Hot TS->Cold
Stream->Alert Engine->Notify
Query API->TS; Control Registry->Edge auth
```

### 4.1 Ingest

```text
TLS auth→validate schema/quota→append stream→ACK→async TS write
```

### 4.2 Late

```text
Writer accepts within window; updates rollups carefully
```

### 4.3 Alert

```text
Rule match→dedupe key→notify
```

### 4.N Cell / blast-radius model

```text
Each cell = failure domain (AZ-set or region slice)
No synchronous cross-cell locks on hot path
Control plane pushes config; data plane serves locally
Shuffle sharding for multi-tenant isolation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. ACK ⇒ durable in region
2. Auth required
3. Cardinality quotas enforced
4. Alert dedupe keys
5. Raw retained per policy before drop
6. PII minimized
7. Clock skew bounded/handled
8. Tenant isolation

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single region stream+TS |
| 10× | Shard by device; edge POPs |
| 100× | Multi-region cells; hierarchical rollups |
| 1000× | Edge aggregation; specialized TS |

### 5.3 Maintainability

- Metric registry PR review
- Alert storm playbooks
- Schema versioning
- Chaos device floods

### 5.4 Progressive scale narrative

**1×:** One region
**10×:** Multi-edge
**100×:** Global devices
**1000×:** Edge agg+tiered query

### 5.5 Idempotency

(device,metric,ts,seq) dedupe window.

### 5.6 Cardinality guard

Reject new series over quota.

### 5.7 Downsample

Optimistic rollups; late revises or separate raw.

### 5.8 Geo failover

Device reconnects other region; identity global.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| ACK before durable | Silent loss |
| Unlimited series | $ meltdown |
| Ignore late data wrongly | Wrong alerts |
| Global sync every point | Impossible |
| No device auth | Botnet ingest |
| Alert without dedupe | Pager death |

---

## 6. Wrap-Up

### 6.1 Designed

Geo sensor ingestion: regional durable ACK, TS+rollups, late/OOO windows, alerts with dedupe, cardinality guards, device identity.

### 6.2 Decisions to defend

1. Regional write affinity
2. Durable before ACK
3. Idempotent points
4. Registry+cardinality caps
5. Hierarchical downsample
6. Stream alerts
7. Device cert auth
8. Tenant isolation

### 6.3 Risks

- Cardinality bombs
- Clock skew
- Alert storms
- Region partition
- Cost of raw retention

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Device+geo scope |
| 5–15 | QPS/storage math |
| 15–25 | Edge+durability |
| 25–35 | TS/late/alerts |
| 35–45 | Cardinality+scale |

### 6.5 Closer

> **Geo-Distributed Sensor Ingestion**: regional durable ingest, honest clocks, cardinality safety, rollups, deduped alerts—cost and correctness over vanity precision.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: MQTT vs HTTPS?

MQTT for flaky; HTTPS ok.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: ACK semantics?

Durable regional.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Late window?

Config per tenant.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Downsample?

Hierarchical rollups.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Cardinality?

Hard reject.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Device auth?

mTLS/certs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: OOO points?

Buffer/reorder window.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Alert storms?

Dedupe+mute.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Cross-region read?

Fanout/optional.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Exactly-once?

Idempotent keys.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Video sensors?

Separate path.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Who pages loss?

Ingest oncall.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Schema evolution?

Registry versions.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Edge agg?

At 1000×.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

ACK before durable / no cardinality cap.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

$/million points + series stored.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

---

## 8. Appendices

### A. Glossary

| Term | Meaning |
|------|---------|
| Cell | Isolated failure domain for blast-radius control |
| Fence / fencing token | Invalidates stale writers after lease steal |
| Idempotency key | Client key making retries safe |
| Outbox | Durable event publish coupled to DB commit |
| Shuffle sharding | Map tenants to overlapping server subsets |
| SLO / error budget | Reliability contract; burn rate drives decisions |
| Unit cost | $ per successful customer action |
| DLQ | Dead-letter queue for poison / exhausted retries |
| Control vs data plane | Config/orchestration vs hot-path serving |
| Progressive scale | Explicit 10×/100×/1,000× architecture jumps |

### B. Ownership matrix

| Concern | Owns | Pages when |
|---------|------|------------|
| Hot-path latency/errors | Serving team | p99 / 5xx burn |
| Durability / data loss risk | Storage/data team | RPO/RTO alarms |
| Abuse / security | Trust & safety / AppSec | exploit or abuse spike |
| Cost regression | Serving + FinOps | unit-cost burn |
| Downstream dependency | Owning service | dependency SEV |

### C. Metrics that matter

- Success rate by criticality class
- Latency histograms (p50/p90/p99) on customer-visible path
- Queue lag / backlog age
- Retry / duplicate attempt rate
- Cache hit ratio where applicable
- Error budget burn rate
- Unit cost trend
- Cell imbalance / hot partition indicators

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope & non-goals |
| 5–12 | Back-of-envelope math |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive invariants & failures |
| 35–45 | Progressive scale, ownership, SEV |

---

## 10. Operability

### Golden signals

ingest ACK p99, durable lag, write errors, series count, alert rate, query p99, drop/reject rate, $/M points

### Rollback ladder

pause alerts→revert writer→read-only query→shed high-card tenants

### Kill switches

block tenant ingest; disable metric prefix; mute all alerts; drop to edge buffer only

### Security / privacy

Device certs; rotate; least privilege; encrypt in transit/rest; anomaly device behavior

### Cost worksheet

Series×retention dominates; downsample early; reject junk cardinality; sample raw

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Device identity PKI, stream platform, TS DB, paging/notify, tenant apps

---

## More Interview Q&A — Geo-Distributed Sensor Ingestion

**Q1. Kafka vs Kinesis?**

**A:** Either; own partitions by device.

**Q2. Prometheus?**

**A:** Not multi-tenant ingest primary.

**Q3. OWASP IoT?**

**A:** Secure provisioning.

**Q4. Gzip points?**

**A:** Batch compress.

**Q5. GPS tracks?**

**A:** PII policy.

**Q6. Firmware OTA?**

**A:** Separate system.

**Q7. SQL on TS?**

**A:** Limited; use TS query.

**Q8. Backfill?**

**A:** Controlled jobs.

**Q9. Exactly once notify?**

**A:** Idempotent pages.

**Q10. What not?**

**A:** Strong global order all devices.

**Q11. How do you canary this?**

**A:** Percent or cell-scoped; auto-rollback on SLO burn.

**Q12. What is the SEV1 customer line?**

**A:** State impact, blast radius, mitigation, next update ETA.

**Q13. How do you test failure?**

**A:** Game day: kill AZ, dependency timeout, duplicate inject.

**Q14. What is read-your-write strategy?**

**A:** Sticky session, sync path, or version tokens as needed.

**Q15. How do you bound cardinality?**

**A:** Allowlists, quotas, deliberate metric labels.

**Q16. What is the degrade mode?**

**A:** Shed noncritical; preserve integrity/security path.

**Q17. How do you handle poison?**

**A:** Quarantine/DLQ; alert owner; capped redrive.

**Q18. What is multi-region story?**

**A:** Home cell writes; regional reads/failover documented.

**Q19. How do you prevent noisy neighbors?**

**A:** Quotas + shuffle sharding + fair queues.

**Q20. What would you not build in MVP?**

**A:** Global strongly consistent sensor state.

---

## Worked Capacity Narrative — Geo-Distributed Sensor Ingestion

Points/s and active series are the two knobs. Cap series growth before disk.

## Customer-Trust Paragraph — Geo-Distributed Sensor Ingestion

Lost telemetry after ACK and alert storms both destroy ops trust—different failure modes, both SEVs.

## Progressive Scale Recap — Geo-Distributed Sensor Ingestion

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Geo-Distributed Sensor Ingestion

### S1. Durable regional ACK

No silent loss after ACK.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Device identity

Cert/key auth per device.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Cardinality control

Registry + hard quotas.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Late/OOO handling

Windows + rollup policy.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Hierarchical downsample

Hot raw → cold rollups.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Alert dedupe

Storm-safe notifications.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Geo routing

Nearest edge write affinity.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Tenant isolation

Site/customer partitions.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Geo-Distributed Sensor Ingestion

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Ingest lag | Scale writers; block new series | Delay | Shard |
| Cardinality bomb | Reject; quarantine tenant | Cost saved | Registry review |
| Alert storm | Mute rule; widen window | Pager relief | Rule fix |
| Region down | Devices failover edge | Brief gaps | DR drill |
| Clock skew mass | Prefer server time flag | Correctness | Device update |
| Dup flood reconnect | Idempotent drop | Load eased | Client backoff |


## Rapid-Fire Q&A — Geo-Distributed Sensor Ingestion

**RQ1. Why does 'Durable regional ACK' matter in an L6 interview?**

**A:** No silent loss after ACK. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Durable regional ACK' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Durable regional ACK' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Device identity' matter in an L6 interview?**

**A:** Cert/key auth per device. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Device identity' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Device identity' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Cardinality control' matter in an L6 interview?**

**A:** Registry + hard quotas. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Cardinality control' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Cardinality control' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Late/OOO handling' matter in an L6 interview?**

**A:** Windows + rollup policy. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Late/OOO handling' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Late/OOO handling' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Hierarchical downsample' matter in an L6 interview?**

**A:** Hot raw → cold rollups. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Hierarchical downsample' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Hierarchical downsample' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Alert dedupe' matter in an L6 interview?**

**A:** Storm-safe notifications. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Alert dedupe' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Alert dedupe' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Geo routing' matter in an L6 interview?**

**A:** Nearest edge write affinity. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Geo routing' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Geo routing' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Tenant isolation' matter in an L6 interview?**

**A:** Site/customer partitions. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Tenant isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Tenant isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Geo-Distributed Sensor Ingestion

### Walkthrough beat 1

Device mTLS publish; edge validates; stream append; ACK.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Writer batches to hot TS.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Duplicate retry dropped by idem key.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Late point within window updates series.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Rule fires; dedupe suppresses repeats.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Query returns 1m rollups for week range.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

New metric label explosion rejected.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× shard/edge; 100× geo cells; 1,000× edge agg.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Geo-Distributed Sensor Ingestion

- [ ] Can explain **Durable regional ACK** with numbers and a deal-breaker
- [ ] Can explain **Device identity** with numbers and a deal-breaker
- [ ] Can explain **Cardinality control** with numbers and a deal-breaker
- [ ] Can explain **Late/OOO handling** with numbers and a deal-breaker
- [ ] Can explain **Hierarchical downsample** with numbers and a deal-breaker
- [ ] Can explain **Alert dedupe** with numbers and a deal-breaker
- [ ] Can explain **Geo routing** with numbers and a deal-breaker
- [ ] Can explain **Tenant isolation** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Ingest lag**
- [ ] Has a 30-second runbook for **Cardinality bomb**
- [ ] Has a 30-second runbook for **Alert storm**
- [ ] Has a 30-second runbook for **Region down**
- [ ] Has a 30-second runbook for **Clock skew mass**
- [ ] Has a 30-second runbook for **Dup flood reconnect**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Geo-Distributed Sensor Ingestion to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Geo-Distributed Sensor Ingestion: 1× → 10× break → 100× cells → 1,000× specialization.

### Extra drill

Name three wallboard metrics before a peak event and the action each triggers.

### Extra drill

Write the SEV1 one-liner: impact, blast radius, mitigation, next update ETA.

### Extra drill

Defend your consistency choice: what is lost if weakened, and who notices first.

### Extra drill

Cost challenge: cut 30% without violating the top SLO—what do you shed first?

### Extra drill

Security challenge: compromised credential—how do least privilege, fencing, and audit limit damage?

### Extra drill

Multi-tenant challenge: one tenant sends 100×—show fair-share math and protected queues.


*End of document — Geo-Distributed Sensor Ingestion (SDE III)*

