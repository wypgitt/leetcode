# System Design: Geographically Distributed Sensor Ingestion

> **Focus areas:** High-cardinality devices · Edge aggregation · Time-series storage · Backpressure · Geo routing · Late/out-of-order data · Exactly-once-ish ingest · Multi-region fan-in  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct cardinality math, split control vs data plane, explicit backpressure stages, deal-breakers for “one Kafka topic + one Prometheus for Earth”  
> **Interview theme:** Amazon SDE III / L6 — design **geo-distributed sensor ingestion**: millions–billions of devices, regional edges, durable time-series, aggregation, and load shedding under burst—own cost and reliability

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

Goal: **bound the ingestion product**—devices worldwide emit telemetry; edge sites aggregate and buffer; regional/central systems store time-series and serve queries/alerts—under **backpressure** when downstream slows—not a full digital-twin app or SCADA UI.

### 1.0 What this is / is not

| Dimension | **Geo sensor ingest (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Ingest, aggregate, store, route telemetry | Full IoT application suite |
| Success | Durable accept, controlled loss under overload, queryable series | Perfect global exact-once + zero lag forever |
| Cardinality | Huge device×metric keys | Dozen servers |
| Hard problem | Backpressure, geo fan-in, cardinality explosion | Pretty dashboards |
| Edge role | Aggregate, buffer, auth, shed | Optional dumb pipe |
| Amazon lens | Cost per datapoint, regional ownership, blast radius | “Just Kinesis + Timestream” one-liner |

**Scope statement:** Design a geographically distributed sensor-ingestion system: device auth, edge aggregation, durable streams, time-series storage, backpressure, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who emits? | Sensors/gateways/vehicles/devices | Device identity + MQTT/HTTP/gRPC |
| F2 | Payload? | Timestamped metrics/events | Schema registry |
| F3 | Frequency? | 1s–5min typical; bursts | Batching + agg |
| F4 | Aggregation? | Edge avg/min/max/count; downsample | Edge pipeline |
| F5 | Queries? | Recent raw + downsampled history | Hot/cold TS store |
| F6 | Alerts? | Threshold / anomaly hooks | Stream processors |
| F7 | Ordering? | Per-device best-effort | Partition by device_id |
| F8 | Late data? | Yes, minutes–hours | Watermarks / rewrites policy |
| F9 | Geo? | Devices prefer nearest edge | Anycast / region map |
| F10 | Offline devices? | Buffer locally; reconnect replay | Edge/device store+forward |
| F11 | Commands? | Optional downlink Phase 1.5 | Separate control plane |
| F12 | Multi-tenant? | Often yes (customers/sites) | Tenant isolation |
| F13 | Retention? | Hot days; cold months/years | Tiering |
| F14 | Exactly-once? | At-least-once + idempotent keys | Dedup windows |
| F15 | Priority? | Critical alarms vs bulk telemetry | QoS classes |

**MVP functional scope:**

1. Device/gateway **auth** (mTLS or signed tokens).  
2. Ingest APIs at **regional edges** (HTTP/MQTT).  
3. **Validate + normalize** schema; reject poison.  
4. **Edge aggregate** (e.g. 10s–60s windows) for high-freq metrics.  
5. Durable **regional stream** + forward to storage/processors.  
6. **Time-series write** path (hot) + downsample to cold.  
7. **Backpressure**: advertise slowdown; buffer; shed bulk first.  
8. Basic **query**: latest, range for device/metric.  
9. **DLQ** for poison; metrics/alerts on lag.  
10. Multi-AZ within region; multi-region edges.

**Out of MVP:**

- Full device firmware OTA platform  
- Complex CEP IDE for customers  
- Guaranteed globally ordered single timeline for all devices  
- Storing raw at 1Hz forever for billions of series  
- Bidirectional realtime control loops with hard RTOS guarantees  
- ML training platform (hooks only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest ACK latency | Edge local | p99 < 50–200ms when healthy |
| N2 | Durability | Accepted points not lost (policy) | Multi-AZ log before ACK (or explicit buffered ACK) |
| N3 | Availability | Edges independent | Regional failure ≠ global outage |
| N4 | Cardinality | Millions–billions series | Careful key design; limits |
| N5 | Lag | Soft realtime | Alert path seconds; bulk minutes OK |
| N6 | Backpressure | No cascade meltdown | Stage-wise shedding |
| N7 | Cost | Dominated by cardinality × frequency | Aggregate early |
| N8 | Consistency | Per-device ordering preferred | Partition keys |
| N9 | Security | Device compromise contained | Per-device creds; least privilege |
| N10 | Operability | Clear owners per region/stage | Lag SLOs; runbooks |
| N11 | Late data | Bounded policy | Configurable grace |
| N12 | Scale | Progressive | Table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Device → nearest edge → validate → edge window aggregate → regional Kinesis/Kafka → TS store → dashboard query.  
2. Gateway batches 1000 sensors → edge expands/validates → write.  
3. Downstream slow → edge buffers → sends `Retry-After` / MQTT quench → devices slow.  
4. Critical alarm event bypasses heavy aggregate → priority topic → alerter < few seconds.  
5. Device offline 1h → local buffer → reconnect replay with idempotent keys.  
6. Downsample job builds 1m/5m/1h rollups for long retention.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cardinality explosion (unique ID in metric name) | Reject / limit series; quarantine tenant |
| Burst after outage | Replay throttled; priority traffic protected |
| Clock skew / future timestamps | Clamp / reject beyond skew budget |
| Late points after downsample | Policy: update cold, ignore, or side table |
| Poison JSON | DLQ; don’t block partition forever |
| Edge disk full | Shed bulk; keep alarms; alert ops |
| Region down | Devices fail over to secondary edge |
| Hot partition device | Isolate key; sub-shard |
| Duplicate replay | Dedup by (device, metric, ts, seq) |
| Schema change | Versioned schemas; compat checks |
| Amplification attack | Auth + per-device rate limits |
| Query scanning huge ranges | Force downsample tier |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Devices | 1M | 10M | 100M | 1B |
| Metrics / device | 10 | 10 | 10–20 | mixed |
| Active series | 10M | 100M | 1B+ | multi-B |
| Points in (raw)/s | 2M | 20M | 200M | 2B |
| After edge agg /s | 200K | 2M | 20M | 200M |
| Edges / POPs | 10 | 20 | 50 | 100+ |
| Regions (storage) | 3 | 3–5 | 5–10 | many |
| Alert events/s | 1K | 10K | 100K | 1M |
| Query QPS | 5K | 50K | 500K | 5M |
| Retention hot | 7d | 7d | 3–7d | shorter raw |

**What each jump forces:**

- **10×:** Edge aggregation mandatory; per-device rate limits; TS DB chosen for cardinality.  
- **100×:** Multi-POP anycast; tenant/series governors; priority classes; cold tier; regional storage homes.  
- **1,000×:** Hierarchical aggregation (device→gateway→edge→region); aggressive downsample; approximate queries; cell isolation per tenant/geo.

### 1.5 Etc. (Constraints & Assumptions)

- Prefer **aggregate-early** for periodic metrics; keep raw for events/alarms.  
- At-least-once delivery + **idempotent writes**.  
- Two ACK modes: **local durable** (edge log) vs **end-to-end durable** (region)—product choice; default edge durable + async ship.  
- Amazon: cost model in $/million points; cardinality alerts as SEVs.

**Scope statement:**

> Design a geo-distributed sensor ingestion system: authenticated high-cardinality devices, regional edges with aggregation and buffering, durable streams into time-series storage, explicit multi-stage backpressure and load shedding, late-data policies, and progressive scale—without storing raw 1Hz forever for every series on Earth.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS / point classes

| Class | Baseline | Notes |
|-------|----------|-------|
| Raw device points | 2M/s | Before agg |
| Edge-emitted points | 200K/s | 10:1 agg example |
| Alert/event points | 1K/s | High priority |
| TS writes | ≈ edge-emitted + events | |
| Downsample writes | fraction async | |
| Queries | 5K/s | Mostly recent |

**Critical:** Plan capacity on **pre-agg** for edge CPU/network and **post-agg** for central storage $.

### 2.2 Cardinality math

```text
series ≈ devices × metrics × labels_explosion
1M devices × 10 metrics = 10M series (clean)
If bad label "session_id" → series → billions → meltdown

Memory index ≈ series × 100B–1KB metadata
10M × 300B = 3 GB index order (per replica set) — OK
1B series × 300B = 300 GB — needs sharding / hierarchical labels
```

### 2.3 Bandwidth

```text
Point wire size ~50–150B compressed batch
2M points/s × 80B = 160 MB/s global raw into edges
After 10:1 agg: 16 MB/s into regional stores — huge $ win
At 100×: 16 GB/s raw → must aggregate/shard geographically
```

### 2.4 Storage

```text
200K points/s × 40B stored ≈ 8 MB/s ≈ 0.7 TB/day hot
Retain 7d ≈ 5 TB hot (plus repl)
1m rollups long-term: much smaller
At 100× without agg: untenable
```

### 2.5 Edge buffer sizing

```text
Target absorb 15 min of regional outage at post-validate rate
200K points/s × 900s × 80B ≈ 14.4 TB? Wait — that's global.
Per edge: global/10 = 20K/s × 900 × 80B ≈ 1.44 TB buffer worst case
Usually compress + shed bulk → design 100–500 GB SSD buffer/edge class
```

### 2.6 Backpressure stages

```text
Device → Edge ingress → Edge buffer → Regional stream → TS writers → Disk
Each stage: high/low watermark
Shed order: bulk metrics → verbose debug → aggregates kept → alarms last
```

### 2.7 Latency budgets

| Path | Budget |
|------|--------|
| Edge ACK (local durable) | p99 < 100ms |
| Alarm to detector | p99 < 1–5s |
| Bulk to queryable hot | p99 < 30–120s |
| Failover to secondary edge | < 30–60s DNS/anycast |

### 2.8 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | Central raw writes | Edge agg + series limits |
| 100× | Cross-region fan-in; cardinality | POP mesh; governors; homes |
| 1,000× | Series index / cost | Hierarchical keys; approx; cells |

### 2.9 Cost owner sketch

```text
Cost ≈ points_stored × retention × repl + series_index + egress + edge HW
Levers: agg ratio, retention tiers, sample debug metrics, compress codecs (Gorilla/XOR)
```

### 2.10 Critical bottlenecks

1. Cardinality explosion.  
2. Thundering herd reconnect.  
3. Hot device partitions.  
4. Unbounded buffers → disk death.  
5. Global query without downsample.

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Aggregate early, store smart.**  
2. **Backpressure is designed**, not emergent.  
3. **Priority classes** protect alarms.  
4. **Regions fail independently.**  
5. **Cardinality is a first-class SLO.**  
6. **At-least-once + idempotency**, not fairy-tale exactly-once.  
7. **Clear ownership** per edge stage and TS tier.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Device / Gateway SDK | Batch, backoff, local buffer, QoS |
| Edge Ingress | Auth, rate limit, validate |
| Edge Aggregator | Windowed rollups |
| Edge Buffer / WAL | Durable local queue |
| Regional Stream | Kafka/Kinesis per region |
| Router / Fan-in | Optional central; prefer regional home |
| TS Writer Fleet | Idempotent writes to hot store |
| Hot TS DB | Recent raw/agg |
| Cold / Downsample | Long retention |
| Stream Alerters | Critical path |
| Control Plane | Device registry, schemas, limits |
| Observability | Lag, shed counts, cardinality |

### 3.3 Protocols & ingest APIs

| Protocol | Use |
|----------|-----|
| MQTT 5 | Constrained devices; quench/backpressure |
| HTTPS POST /batch | Gateways; simple |
| gRPC streaming | High-efficiency gateways |
| CoAP | Optional niche |

```text
POST /v1/ingest
{
  "device_id": "d123",
  "sent_at": ...,
  "points": [
    {"metric":"temp_c","ts":...,"v":22.5,"seq":1901}
  ]
}
→ 202 { "accepted": N, "retry_after_ms": 0 }
→ 429 { "retry_after_ms": 2000, "shed_class": "bulk" }
```

### 3.4 Device identity & registry

```text
device_id, tenant_id, home_region, credentials, firmware, limits
Auth: mTLS device cert OR JWT from bootstrap
Compromise: revoke cert; rotate
Registry is control plane — not on every point hot path (cache)
```

### 3.5 Edge aggregation

```text
For periodic metrics:
  window W=10s–60s: emit min, max, sum, count, last
For events/alarms:
  pass-through immediately (no waiting for window close)
Config per metric class via schema
```

**Watermarks:** close windows with allowed lateness L; late updates go to “late” topic or update if policy allows.

### 3.6 Data model (time-series)

| Field | Notes |
|-------|-------|
| tenant_id | Isolation |
| device_id | Partition |
| metric | Name |
| labels | Restricted allowlist |
| ts | Event time |
| value | Numeric/bool/small bytes |
| seq | Monotonic per device metric |
| quality | OK/estimated/shed |

**Series key:** `(tenant, device, metric, labels_hash)` — labels bounded.

### 3.7 Storage layout

| Tier | Holds | Tech examples |
|------|-------|---------------|
| Edge WAL | Seconds–hours buffer | Local Rocks/disk queue |
| Regional log | Durable stream | Kafka/Kinesis |
| Hot TS | Hours–days | Timestream / VictoriaMetrics / custom |
| Cold | Months–years | Object + Parquet / TS cold tier |
| Rollups | 1m/5m/1h | Continuous downsample |

### 3.8 Backpressure design (core)

| Stage | Signal | Action |
|-------|--------|--------|
| TS writers lag | Consumer lag | Slow read from stream; raise flag |
| Stream full | Partition quota | Refuse low-pri produce; keep alarm topic |
| Edge buffer high | Disk watermark | 429/MQTT quench; shed bulk windows |
| Edge ingress CPU | Load | Sample/drop debug metrics |
| Device | Retry-After | Exponential backoff + jitter |

**Never:** infinite memory queues. **Always:** explicit shed counters as customer-visible metrics.

### 3.9 Geo routing

```text
Device → DNS/anycast → nearest healthy edge POP
Edge tagged with region
Telemetry home: tenant/device home_region storage
Cross-region: ship async; query local first
Failover: secondary POP list in device config
```

### 3.10 Tradeoffs table

| Decision | A | B | Pick |
|----------|---|---|------|
| ACK durability | Edge local | Wait region | Edge local + async (doc risk) |
| Agg location | Device | Edge | Edge (+ device batch) |
| TS DB | Push Prometheus | Purpose-built TS | Purpose-built |
| Global bus | One mega Kafka | Regional | Regional |
| Late data | Drop | Correct rollups | Bounded update window |
| QoS | Single class | Multi | Multi (alarm/bulk) |

### 3.11 Deal-breakers

1. Raw 1Hz forever × billion series.  
2. Unbounded in-memory buffers.  
3. One global Kafka cluster for all edges.  
4. High-cardinality labels unconstrained.  
5. Alerts stuck behind bulk lag.  
6. “Exactly-once” claims without idempotent keys.  
7. Single region control plane outage blocks all ingest worldwide without cache.  
8. Query path scanning raw cold for every dashboard.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
 [Devices/Gateways]
        │  MQTT/HTTPS
        ▼
 ┌──────────────────┐   ┌──────────────────┐
 │ Edge POP A (US)  │   │ Edge POP B (EU)  │  ...
 │ ingress│agg│WAL  │   │ ingress│agg│WAL  │
 └────────┬─────────┘   └────────┬─────────┘
          │                      │
          ▼                      ▼
   Regional Stream US     Regional Stream EU
          │                      │
          ▼                      ▼
   TS Writers + Alerters   TS Writers + Alerters
          │                      │
          ▼                      ▼
     Hot TS + Cold          Hot TS + Cold
          │                      │
          └───────────┬──────────┘
                      ▼
              Query Gateway / Dashboards
                      ▲
              Control Plane (registry, schemas, limits)
```

### 4.2 Sequence: healthy ingest

```text
Device batch → Edge auth/RL → validate → agg window → WAL append → 202 ACK
Async: WAL → regional stream → TS write (idempotent)
```

### 4.3 Sequence: backpressure

```text
TS lag high → stream throttle bulk → edge WAL watermark ↑
Edge returns 429 Retry-After / MQTT reason code
Device slows; alarm topic still accepted
Ops page: shed_rate, lag, buffer_%
```

### 4.4 Sequence: offline replay

```text
Device stores locally with seq
Reconnect → replay in order → edge dedups by (device,metric,ts,seq)
Throttled replay rate to protect cluster
```

### 4.5 Priority lanes

```text
Topic/queue: alarms > events > aggregates > raw_debug
Dedicated consumer pools for alarms
```

### 4.6 Cell architecture at 100×+

```text
Cell = { tenant slice or geo slice, stream, TS, writers }
Control plane maps device → cell
No noisy neighbor across cells
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. ACK modes documented; local ACK ⇒ in edge WAL.  
2. Idempotent series writes by dedup key.  
3. Alarms never share fate with bulk under overload (best-effort isolation).  
4. Series creation respects cardinality governors.  
5. Per-device ordering in a partition when using single writer key.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Edge death | Device fails over; WAL on lost edge unreplicated unless synced — accept or dual-write WAL |
| Stream AZ loss | Multi-AZ Kafka |
| TS down | Buffer in stream; lag SLO |
| Clock jump | Skew guards |
| Poison storm | Schema + DLQ + circuit |
| Replay storm | Replay budgets |

**Edge WAL durability tradeoff:** local SSD lost with rack → optional sync to regional before ACK for gold tenants.

#### 5.1.3 Durability & backup

- Stream retention 1–7d for replay.  
- TS snapshots / continuous backup.  
- Config/registry backups.

#### 5.1.4 Consistency nuances

- Event-time vs processing-time.  
- Downsample windows vs late arrivals.  
- Cross-region query may be incomplete without fan-in.

#### 5.1.5 Security

- Per-device credentials.  
- Tenant isolation.  
- Payload size caps.  
- mTLS.  
- Audit on registry changes.  
- No lateral movement via shared secrets.

### 5.2 Scalability

#### 5.2.1 Partitioning

```text
Stream key = hash(tenant, device_id)
Avoid metric in key if causes too many tiny partitions — balance
Hot device: salt key with shard id from gateway
```

#### 5.2.2 Cardinality governors

- Max series per tenant/device.  
- Label allowlists.  
- Blocklists for bad keys.  
- Slow-create rate for new series.  
- Alerts when approaching limits.

#### 5.2.3 Hierarchical aggregation (1,000×)

```text
Sensor → Gateway (1s→10s) → Edge (10s→1m) → Region rollups (1m→1h)
Each stage reduces points ~10×
```

#### 5.2.4 Query scaling

- Recent queries hit hot TS.  
- Historical forced to rollup resolution.  
- Query gateway enforces max scan series × range.  
- Materialized views for popular fleets.

#### 5.2.5 Multi-region

- Write home region.  
- Global query: scatter-gather with budgets OR central warehouse.  
- DR: async replica of cold; hot rebuild from stream if retained.

#### 5.2.6 Cost controls

- Default agg on.  
- Drop debug metrics dynamically.  
- Compress.  
- Short hot retention.  
- Tenant budgets ($ and series).

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Device SDK | IoT client |
| Edge POP | Edge ingest |
| Streams | Streaming platform |
| TS storage | Time-series |
| Alerts | Observability/alerting |
| Registry/schemas | Control plane |
| Cardinality | Shared SRE + TS |

#### 5.3.2 Safe evolution

- Schema versions with compatibility.  
- Metric class config as data.  
- Canary POPs.  
- Dual-write during TS migration.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Edge ACK success | 99.9% (excl. client errors) |
| Alarm pipeline latency | p99 < 5s |
| Bulk queryable lag | p99 < 2 min |
| Shed rate | Alert if > threshold |
| Series create failures | Watched |
| WAL disk | < 70% |

#### 5.3.4 Progressive scale checklist

**10×:** edge agg; RL; hot TS; dedup; basic shed.  
**100×:** multi-POP; QoS lanes; governors; cold tier; home regions.  
**1,000×:** hierarchical agg; cells; approx query; tenant isolation hard.

### 5.4 Deep dive: idempotent write

```text
dedup_key = hash(tenant, device, metric, ts_ms, seq)
writer: put if not exists / upsert same value
Windowed Bloom or KV dedup cache for recent (e.g. 24h)
```

### 5.5 Deep dive: MQTT backpressure

```text
Use receive maximum / quota; reason codes for quench
Broker shared across devices — isolate tenants with separate listeners
Prefer gateway aggregation to reduce connection count
```

### 5.6 Deep dive: late data policy

| Policy | Behavior |
|--------|----------|
| Drop if window closed | Simple; lossy |
| Update rollup within grace G | Correctness↑ cost↑ |
| Side channel raw_late | Auditability |

**MVP:** grace G=5–15 min for rollups; beyond → late table optional.

### 5.7 Deep dive: reconnect thundering herd

```text
Devices randomized backoff (jittered)
Edge issues staggered Retry-After
Token bucket per /24 or per cert prefix
Priority reconnect for alarm-capable devices
```

### 5.8 Deep dive: schema registry

```text
metric catalog: name, type, unit, agg_fn, qos_class, max_freq, label_schema
Unknown metric → reject or sandbox bucket with strict limits
```

### 5.9 Testing & resilience

| Test | Purpose |
|------|---------|
| Cardinality fuzz | Governors |
| Kill TS writers | Buffer/shed |
| Edge disk fill | Watermarks |
| Region failover | Device config |
| Clock skew | Guards |
| Replay flood | Throttle |
| Poison payloads | DLQ |

### 5.10 Comparison: metrics vs events vs logs

| | Sensor metrics | Events/alarms | Logs |
|--|----------------|---------------|------|
| Volume | Huge periodic | Spiky | Huge text |
| Agg | Essential | Rare | Parse/index |
| Query | TS range | Search | Search |
| Loss policy | Sometimes OK if sampled | Rarely OK | Tiered |

### 5.11 Amazon leadership connection (brief)

- Frugality: aggregate-early as default product.  
- Ownership: cardinality SEVs have clear pages.  
- Dive deep: know shed order under load.  
- Customer obsession: alarm QoS over perfect bulk.  
- Bias for action: start regional, not global bus.

---

## 6. Wrap-Up

### 6.1 30-second recap

> Devices hit nearest **edge POPs** for auth, validation, and **windowed aggregation**, with a **WAL** and explicit **backpressure**. Regional streams feed **time-series writers** with idempotent keys; **alarms ride priority lanes**. Cardinality governors prevent label explosions. Scale out via more POPs, regional homes, hierarchical aggregation, and cells—not one global pipeline that stores raw forever.

### 6.2 Key tradeoffs

1. Edge-local ACK vs end-to-end ACK.  
2. Agg ratio vs fidelity.  
3. Late-data correction vs drop.  
4. Regional vs global stream.  
5. Exact series vs approx/top-k query.  
6. MQTT vs HTTPS gateways.

### 6.3 Risks & follow-ups

- Silent shedding without customer visibility.  
- Cardinality regressions from app changes.  
- Edge WAL loss scenarios.  
- Cross-region query correctness.  
- Schema sprawl.  
- Downstream alert flapping.

### 6.4 What “good” looks like

- Cardinality math upfront.  
- Multi-stage backpressure.  
- QoS classes.  
- Geo failover story.  
- Deal-breakers named.  
- Ownership of lag/shed SLOs.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. Metrics vs discrete events mix?  
2. Hard realtime control loops needed?  
3. Multi-tenant SaaS or single fleet?  
4. Acceptable data loss under overload?  
5. Retention by metric class?  
6. Downlink commands in scope?  
7. Regulatory data residency?  
8. Device offline duration max?  
9. Gateway fan-in topology?  
10. Query users (ops vs customers)?  
11. Billing by points?  
12. Out of scope list?

### 7.2 Edge & backpressure (Q13–Q32)

13. Watermark algorithms.  
14. Shed priority order.  
15. WAL replication.  
16. MQTT quench details.  
17. 429 semantics.  
18. Buffer sizing.  
19. Disk full behavior.  
20. CPU overload sampling.  
21. Window early emit.  
22. Gateway vs edge agg.  
23. Compression codecs.  
24. Batching vs latency.  
25. POP capacity planning.  
26. Anycast failover.  
27. Edge software deploy.  
28. Poison pill isolation.  
29. Multi-tenant fairness.  
30. CoDel/queue disciplines.  
31. Backpressure testing.  
32. Customer-visible shed metrics.

### 7.3 Time-series & cardinality (Q33–Q52)

33. Series key design.  
34. Label allowlists.  
35. Gorilla compression.  
36. Out-of-order writes.  
37. Dedup windows.  
38. Hot/cold tiers.  
39. Downsample correctness.  
40. Query limits.  
41. High cardinality incident response.  
42. Sparse metrics.  
43. Boolean/bit sensors.  
44. String values policy.  
45. TS DB comparison.  
46. Partition hotspots.  
47. Index memory.  
48. Rollup chains.  
49. Recording rules.  
50. Tenant noisy neighbor.  
51. Approximate histos.  
52. Frozen series GC.

### 7.4 Geo & ops (Q53–Q70)

53. Home region selection.  
54. Cross-region ship.  
55. DR story.  
56. Data residency.  
57. Global dashboard.  
58. Clock sync (NTP).  
59. Control plane HA.  
60. Schema migration.  
61. Canary POP.  
62. Cost attribution.  
63. Capacity forecasting.  
64. SEV runbooks.  
65. Load test design.  
66. Chaos drills.  
67. Security breach device.  
68. Firmware coupling.  
69. Multi-cloud edges.  
70. 45-minute plan.

### 7.5 Behavioral / Amazon (Q71–Q80)

71. Story: prevented cost meltdown via agg.  
72. Disagreement on ACK durability.  
73. Owning a lag SEV.  
74. Frugality vs fidelity.  
75. Cross-team stream ownership.  
76. Customer angry about shed.  
77. Dive deep into cardinality bug.  
78. Bar-raiser scale narrative.  
79. Invent & simplify: metric classes.  
80. Deliver results under incomplete device clocks.

---

## 8. Appendices

### Appendix A — QoS classes

| Class | Examples | Loss policy |
|-------|----------|-------------|
| P0 Alarm | Threshold breach | Never shed first |
| P1 Event | State change | Rarely shed |
| P2 Aggregate | 1m rollup | Buffer then shed |
| P3 Debug | Verbose | First shed |

### Appendix B — Point (sample)

```json
{
  "tenant": "t1",
  "device_id": "truck_9",
  "metric": "coolant_c",
  "ts": 1720000000123,
  "v": 91.2,
  "seq": 44001,
  "labels": {"engine": "main"}
}
```

### Appendix C — Edge ACK modes

| Mode | Meaning |
|------|---------|
| ACK_LOCAL | In WAL |
| ACK_REGION | In regional stream |
| ACK_STORED | In TS (rare sync) |

### Appendix D — Error codes

| Code | Meaning |
|------|---------|
| 400 | Schema invalid |
| 401/403 | Auth |
| 413 | Batch too large |
| 429 | Backpressure |
| 503 | Edge overloaded |

### Appendix E — Anti-patterns

- Infinite Redis lists as buffers.  
- Metric names with UUIDs.  
- One global topic.  
- Alerts on same consumer as bulk.  
- Unbounded label keys.  
- Sync ACK to cold storage.  
- Dashboard queries over raw year at 1Hz.

### Appendix F — Capacity worksheet

```text
devices =
metrics_per_device =
raw_points_per_sec =
agg_ratio =
post_agg_points_per_sec =
series_count =
edge_count =
wal_minutes_target =
hot_retention_days =
```

### Appendix G — 45-minute timebox

| Min | Topic |
|-----|-------|
| 0–5 | Requirements + QoS |
| 5–12 | Cardinality + BOTE |
| 12–25 | Edge agg + WAL + stream |
| 25–35 | Backpressure + TS tiers |
| 35–42 | Geo + scale jumps |
| 42–45 | Wrap |

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| Series | Unique timeline key |
| Edge POP | Point of presence ingest |
| WAL | Write-ahead / local durable queue |
| Watermark | Event-time progress |
| Shed | Intentional drop under load |
| Home region | Storage locality |
| Governor | Cardinality limiter |

### Appendix I — Ownership RACI

| Item | R | A | C | I |
|------|---|---|---|---|
| Edge WAL | Edge | Edge | Streaming | SRE |
| Cardinality | TS | TS | Edge | Tenants |
| Alarm latency | Alerting | Alerting | Streaming | Customers |
| Schema | Control | Control | All | Devices |

### Appendix J — Progressive scale one-pager

| Scale | Must |
|-------|------|
| 1× | Auth ingest + TS |
| 10× | Edge agg + RL + dedup |
| 100× | Multi-POP + QoS + governors |
| 1,000× | Hierarchy + cells + approx |

### Appendix K — Backpressure state machine

```text
NORMAL → ELEVATED (lag) → SHED_BULK → SHED_AGG → EMERGENCY (accept alarms only)
Recovery hysteresis to avoid flap
```

### Appendix L — Minimal threat model

| Threat | Control |
|--------|---------|
| Device flood | Per-device RL |
| Stolen cert | Revocation |
| Tenant abuse | Quotas |
| Poison payload | Schema/DLQ |
| Data exfil | Authz query |

### Appendix M — Writer pseudocode

```text
function write_point(p):
  k = dedup_key(p)
  if recently_seen(k): return
  tsdb.write(series(p), p.ts, p.v)
  remember(k)
```

### Appendix N — Aggregator pseudocode

```text
on_point(p):
  if qos(p)==ALARM: emit_immediate(p); return
  buf[series].add(p)
  if window_closed(series, watermark):
     emit(minmaxsumcount(buf[series])); clear
```

### Appendix O — Interview “say this” (60 seconds)

> “I’d put authenticated devices on nearest edge POPs that validate, rate-limit, and aggregate periodic metrics into windowed rollups, with a local WAL and multi-stage backpressure that sheds bulk before alarms. Regional streams feed idempotent time-series writers with hot/cold tiers. Cardinality governors are mandatory. We scale with more POPs, regional homes, hierarchical aggregation, and cells—not one global raw firehose.”

### Appendix P — Related systems map

| System | Relation |
|--------|----------|
| AWS IoT Core | Ingest analogue |
| Kinesis/Kafka | Streams |
| Timestream/VM | TS storage |
| Prometheus | Not for billion-series raw alone |
| Flink | Agg/alerts |
| Device shadow | Adjacent control |

### Appendix Q — Chaos drills

1. Fill edge disk.  
2. Kill TS writers.  
3. Partition stream AZ.  
4. Mass reconnect.  
5. Cardinality spike.  
6. Clock skew blast.  
7. Poison JSON.  
8. Cross-region cut.

### Appendix R — Metrics catalog

- `ingest_accepted_points`  
- `ingest_shed_points{class}`  
- `edge_wal_bytes`  
- `stream_lag_seconds`  
- `ts_write_p99`  
- `series_created`  
- `alarm_pipeline_p99`  
- `failover_count`

### Appendix S — Retention matrix

| Class | Hot | Cold | Rollup |
|-------|-----|------|--------|
| Alarm | 30d | 1y | n/a |
| Agg 1m | 7d | 1y | 1h@1y |
| Debug | 24h | none | none |

### Appendix T — Label policy example

```text
allowed: engine, unit, site
forbidden: request_id, user_id, timestamp, path
max_label_values_per_key per tenant: 1000
```

### Appendix U — Failover config (device)

```json
{"edges":["https://e-us.example","https://e-eu.example"],"jitter_ms":5000}
```

### Appendix V — Comparison checklist

| Checkpoint | Covered? |
|------------|----------|
| Cardinality math | Yes |
| Edge agg | Yes |
| Backpressure stages | Yes |
| QoS | Yes |
| Geo | Yes |
| Idempotency | Yes |
| Progressive scale | Yes |
| Deal-breakers | Yes |

### Appendix W — Downsample chain

```text
raw_agg_10s → 1m → 5m → 1h → 1d
Store only what query needs at each age
```

### Appendix X — Budget card for interview

```text
Say numbers:
  1M devices × 10 metrics × 1/s = 10M/s raw
  Edge 30s avg → ~300K+/s (still high) — push longer windows or gateway agg
Show you can renegotiate frequency with interviewer
```

### Appendix Y — Control vs data plane

| Plane | Contents |
|-------|----------|
| Control | Registry, schemas, limits, certs |
| Data | Points, aggregates, alarms |
| Rule | Control cached; data path never blocks on remote control hard dependency beyond TTL |

### Appendix Z — Final SDE III checklist

- [ ] QoS + loss policy  
- [ ] Cardinality BOTE  
- [ ] Edge agg + WAL  
- [ ] Multi-stage backpressure  
- [ ] TS hot/cold  
- [ ] Geo failover  
- [ ] Ownership/SLOs  
- [ ] 10×/100×/1,000×  
- [ ] Deal-breakers  

---

*End of geo-distributed sensor ingestion system design (Amazon SDE III).*
