# System Design: Highly Available Logging System

> **Focus areas:** Ingestion · Buffering · Indexing · Retention tiers · Regional failure · Multi-tenant isolation · Query fanout  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split hot-write / index / query / cold-storage classes, honest exactly-once discussion, explicit RPO under regional loss  
> **Interview theme:** Classic observability/logging platform — durability and cost dominate; “search all logs forever” is the trap

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the platform**—a multi-tenant, highly available **logging / log management** system: agents and apps emit logs; the platform ingests, buffers, stores, indexes selectively, retains by tier, and serves search/query—surviving AZ and regional failures **without silent loss of acked data**.

### 1.0 What this is / is not

| Dimension | **HA logging system (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Durable ingest + query of logs | Full APM traces/metrics product (hooks OK) |
| Success | Acked logs not lost; query within retention SLOs | Infinite cheap full-text forever |
| Data | Structured/unstructured log events | OLTP source of truth for apps |
| Query | Time-bounded search, filters, tails | Ad-hoc warehouse SQL on all history MVP |
| HA | Multi-AZ; regional failover with stated RPO | Active-active sync everywhere magical |

**Scope statement:** Design a **highly available multi-tenant logging system** with buffered ingest, write-ahead durability, hot index + cold cheap storage, retention tiers, sampling, and regional failure strategy.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who emits? | Agents, sidecars, apps via HTTPS/gRPC; syslog optional | Ingest API + protocol adapters |
| F2 | Ack semantics? | After durable buffer | WAL/Kafka before ACK |
| F3 | Multi-tenant? | Yes — orgs/projects; quotas | Tenant isolation + shard keys |
| F4 | Schema? | Semi-structured JSON; optional schema registry | Normalize + index mapping |
| F5 | Query? | Keyword + field filters + time range; live tail | Inverted index hot; cold rehydrate |
| F6 | Retention? | Hot 7–30d; cold 90–365d; configurable | Tiered storage lifecycle |
| F7 | Sampling? | Head/tail sampling; priority levels | Ingest policy engine |
| F8 | Exactly-once? | Prefer no dupes in query; duplicates tolerable if marked | Idempotency keys optional |
| F9 | Alerting? | Optional webhook on query match Phase 1.5 | Stream rules secondary |
| F10 | Compliance? | Immutable / WORM optional; audit access | Legal hold; encryption |
| F11 | Regional HA? | Survive region loss with low RPO | Cross-region replicate buffer/cold |
| F12 | Fanout? | One event → index + cold + analytics | Pipeline consumers |

**MVP functional scope:**

1. Authenticated multi-tenant ingest (`project_id`) with batching.  
2. **Durable ACK** after write-ahead / replicated log.  
3. Parse/normalize JSON logs; extract timestamp, severity, service, trace_id.  
4. Buffer (Kafka/Pulsar) → **hot indexer** + **cold object segments**.  
5. Query API: time range + filters + full-text on hot; cold search slower/limited.  
6. Live **tail** (recent stream) with backpressure.  
7. Retention jobs: hot→warm→cold→expire; per-tenant policies.  
8. Quotas: bytes/day, ingest QPS, index cardinality guards.  
9. Regional DR: replicate acked data; document RPO/RTO.  
10. Metrics: ingest lag, ACK fail, index lag, query p99, discard/sample rates.

**Out of MVP:**

- Full distributed tracing product (accept `trace_id` field only)  
- Arbitrary warehouse joins across years at interactive latency  
- Perfect global exactly-once dedupe of all producers  
- ML anomaly detection platform (hooks: stream sink)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability of ACK | Multi-AZ quorum | RPO≈0 in region for acked |
| N2 | Cross-region RPO | Async OK | Seconds–minutes; state explicitly |
| N3 | Ingest availability | Critical | 99.99% ACK path; degrade index first |
| N4 | Ingest latency ACK | Tight | p99 < 100–250ms batch |
| N5 | Query latency hot | Interactive | p95 < 2–5s typical ranges |
| N6 | Query cold | Best effort | Seconds–minutes; async OK |
| N7 | Multi-tenant isolation | Noisy neighbor controlled | Quotas; separate partitions |
| N8 | Cost | Dominates design | Index subset; cold columnar/object |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Agent batches 100 logs → ingest ACK → appear in search within seconds.  
2. Spike traffic → buffer absorbs; index lag grows; no ACK loss.  
3. Query last 15m `severity=ERROR service=checkout` → hot index hit.  
4. Query 180d ago → cold path / rehydrate / async job.  
5. Region A fails → DNS/clients to region B; acked logs within RPO available.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Indexer down | Buffer holds; ACK continues; lag alert |
| Buffer disk full | Shed lowest priority / sample; never lie ACK without durability |
| Huge log line 10MB | Reject or truncate per policy; protect cluster |
| Cardinality explosion (user_id label) | Index allowlist; drop to cold-only fields |
| Clock skew producer | Use ingest_time fallback; reject absurd future ts |
| Duplicate producer retries | Optional event_id dedupe window; else accept dupes |
| Query fanout 10K shards | Deadline + partial results; hierarchical fan-in |
| Tenant runaway | Quota 429; circuit isolate partitions |
| Regional failover | Promote secondary; accept RPO gap; no split-brain SoT |
| Exactly-once illusion | Document at-least-once; idempotent sinks where needed |
| Bloom false negative | Must not skip segments that might match (use correctly) |
| Live tail slow consumer | Disconnect / buffer bound; don't block ingest |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants / projects | 1K | 10K | 100K | 1M |
| Ingest events/s peak | 500K | 5M | 50M | 500M |
| Ingest GB/s peak | 1 | 10 | 100 | 1K |
| Hot retention | 14d | 14d | 7–14d | shorter hot |
| Indexed fields fraction | ~100% curated | curated | aggressive | sampling+curated |
| Query QPS | 200 | 2K | 20K | 200K |
| Concurrent tails | 1K | 10K | 100K | cell-local |
| Buffer retention | 24–72h | similar | similar | longer DR |
| Cold store | 1 PB | 10 PB | 100 PB | EB class |

**What each jump forces:**

- **10×:** Partition by tenant+time; dedicated ingest fleet; index shard autoscaling.  
- **100×:** Cells; separate hot/cold query paths; heavy sampling defaults; cross-region async.  
- **1,000×:** Global edge ingest; tenant placement; query gateway scatter-gather limits; cold-only for most bytes.

### 1.5 Etc. (Constraints & Assumptions)

- Logs are **observability data**, not the customer's bank ledger — still, **acked ⇒ durable**.  
- Prefer **structured logs**; unstructured allowed as `message`.  
- **Index is expensive**; cold object/columnar is cheap — design for that asymmetry.  
- Kafka/Pulsar as **buffer**, not long-term SoT (cold object + index are).  
- “Exactly-once end-to-end” is usually **false**; be precise.

**Scope statement to repeat back:**

> Design a multi-tenant HA logging platform: durable acked ingest into a replicated buffer, fanout to hot indexes and cheap cold storage, schema-aware indexing with cardinality controls, retention tiers, query fanout with deadlines, and regional failover with an explicit RPO—scaled through tenant+time sharding and cells at 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Ingest ACK** | HTTPS/gRPC batches | ~50K req/s (batches) | ×10 | Ingest edge |
| **Events** | Expanded log lines | ~500K/s | ~5M/s | Buffer |
| **Bytes** | Compressed on wire | ~1 GB/s | ~10 GB/s | NIC/disk |
| **Index writes** | Inverted + columnar | ≤ events (sampled) | ×10 | Hot index |
| **Cold writes** | Segment objects | ~bytes | ×10 | Object store |
| **Query** | Search fanout | ~200 QPS | ~2K | Query tier |
| **Tail** | Stream subscriptions | ~1K | ×10 | Pub/merge |
| **Retention GC** | Compactions | continuous | — | Background |

**Anti-pattern:** sizing index nodes from raw GB/s as if every field is indexed forever.

### 2.2 Daily volume

```text
Baseline peak 1 GB/s; assume average 0.25 GB/s sustained
0.25 GB/s × 86400 ≈ 21.6 TB/day ingested (uncompressed-ish)
Compress 5–10× in cold → ~2–4 TB/day stored cold
Hot index expansion often 1.5–3× raw for indexed subset
If index only 20% of fields/events: index bytes ≪ cold bytes
14d hot: 21.6 × 14 ≈ 300 TB raw-equivalent; plan capacity + replicas
```

### 2.3 Buffer sizing

```text
Hold 24h at peak for safety? Expensive.
Better: 2–6h at peak + disk alerts
2h × 1 GB/s = 7.2 TB buffer cluster (raw) → with RF=3 ≈ 20+ TB disk
At 10×: 72 TB raw / ~200 TB RF=3 — still OK; at 100× must cell + shorter buffer + faster drain
```

### 2.4 Query fanout math

```text
Hot data sharded by time (1h) × tenant hash (64 shards)
Query 24h × 1 tenant → 24 × up to 64 = 1536 shard touches worst
With time-pruned segments + tenant locality: often tens of shards
Deadline 5s → per-shard budget ~100–200ms + merge
At 10K shards touched: must reject or async — hard limit in gateway
```

### 2.5 Bloom filters for search

```text
Per cold segment bloom on terms / trace_ids
False positive rate 1% → extra segment fetches OK
False negative MUST be 0 for correctness if bloom used to skip
→ blooms are membership filters built from actual terms; size ~ few KB–MB / segment
```

### 2.6 Sampling economics

```text
Sample DEBUG at 1%, keep ERROR 100%
If DEBUG is 80% of volume → save ~0.8 × 0.99 ≈ 79% DEBUG bytes
Index only ERROR+WARN+sampled INFO → large $ win
```

---

## 3. High-Level Design

### 3.1 APIs

| API | Semantics |
|-----|-----------|
| `POST /v1/projects/{id}/logs:batch` | Ingest array; returns ack_id / error per policy |
| `GET /v1/projects/{id}/logs:search` | Query DSL: time, query string, filters, page |
| `GET /v1/projects/{id}/logs:tail` | SSE/WS live stream; filter preview |
| `GET /v1/projects/{id}/logs:context` | Surrounding lines by id/time |
| `PUT /v1/projects/{id}/retention` | Hot/cold/expire policies |
| `PUT /v1/projects/{id}/processing` | Sampling, redact rules, index allowlist |
| `GET /v1/admin/lag` | Buffer/index lag (ops) |

**Log event (logical):**

```text
{
  event_id?,           // producer optional UUID
  timestamp,           // event time
  severity,
  service, host, env,
  message,
  attributes: {...},   // indexed if allowlisted
  body: {...}          // cold always; index selective
}
```

### 3.2 Domain model

```text
Tenant(org_id) / Project(project_id, quotas, retention, index_policy)
IngestBatch(batch_id, project_id, recv_time, codec, size)
LogEvent(project_id, event_time, ingest_time, fields..., fingerprint)
Segment(segment_id, project_id, time_start, time_end, cold_uri, bloom_uri, stats)
IndexShard(shard_id, time_bucket, tenant_partition, node)
QueryJob(job_id, project_id, dsl, deadline, partial_ok)
RetentionPolicy(hot_days, cold_days, expire_days, legal_hold?)
```

### 3.3 Buffer choice

| Option | Pros | Cons | Use |
|--------|------|------|-----|
| **Kafka** | Mature; replay; consumer groups | Ops; partition limits | **Strong default** |
| **Pulsar** | Native tiered storage; multi-tenant | Ecosystem/ops familiarity | Excellent at scale |
| Redis streams | Low latency | Not HA durable SoT | No for ACK SoT |
| Direct to S3 | Cheap | High ACK latency / hard query | Cold only |

**Chosen MVP:** Kafka (or Pulsar) **multi-AZ RF≥3**; ACK after produce ack=`all`. Topics partitioned by `hash(project_id) % N` + optional overload topics for huge tenants.

### 3.4 Write-ahead & durability

```text
Client → Ingest → validate/quota → produce(Kafka) RF=3 → ACK
         ↘ async: side features
Indexer and ColdWriter are consumers — crash OK if lag resumes
```

**Deal-breaker:** ACK before quorum persist (or ACK on memory queue only).

### 3.5 Hot index vs cold storage

| Tier | Store | Query | Cost |
|------|-------|-------|------|
| **Hot** | Inverted index + columnar (Lucene/ES/OpenSearch/ClickHouse-ish) | Interactive | $$$ |
| **Warm** | Fewer replicas / cheaper SSD | Slower | $$ |
| **Cold** | Object store segments (Parquet/custom) + blooms | Pruned scan / async | $ |
| **Expire** | Delete unless legal hold | — | — |

**Chosen:** always write **cold segment** (source of truth for long retention); hot index is an **acceleration layer** that can rebuild from cold/buffer for recent windows.

### 3.6 Schema & indexing policy

| Approach | Pros | Cons |
|----------|------|------|
| Index everything | Easy UX | Cardinality/$ death |
| **Allowlist + dynamic deny** | Controllable | Config burden |
| Full cold, sparse hot | Cost sane | Two paths |

**Chosen:** project index allowlist (`service`, `severity`, `trace_id`, selected attrs); rest searchable via cold `message` / rehydrate; dynamic mapping caps.

### 3.7 Dedup & exactly-once

| Layer | Guarantee |
|-------|-----------|
| Producer retry | At-least-once |
| Optional `event_id` cache | Best-effort dedupe window (e.g. 15m) |
| Index doc `_id=event_id` | Upsert idempotent |
| Query UX | May show dupes if no event_id — document |

**Never claim:** bus EOS ⇒ global exactly-once without idempotent keys.

### 3.8 Query fanout

```text
Query Gateway → AuthZ → Rewrite (tenant forced filter)
  → Planner: pick time buckets × shards
  → Scatter with deadline
  → Merge top-k / progress
  → Partial results flag if timeouts
```

### 3.9 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| ACK SoT | Replicated log | Survive indexer death | ACK on index success only |
| Long-term SoT | Cold objects | Cost | Infinite hot replicas |
| Shard key | time + tenant | Prune + isolate | Global random only |
| Index | Allowlist | Cardinality | Index all JSON keys |
| Regional HA | Async replicate + promote | Practical RPO | Sync ACK cross-region |
| Sampling | Policy engine | Cost/noise | Keep 100% DEBUG forever |
| Bloom | Skip cold segments | I/O | False-negative skips |
| Multi-tenant | Quotas + partitions | Noisy neighbor | Shared unlimited |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
  Apps / Agents / FluentBit / OTel Collector
                    |
                    v
         +---------------------+
         | Edge Ingest Gateway |  auth, quota, batch, redact
         +----------+----------+
                    | produce ack=all
                    v
         +---------------------+
         | Buffer Log Cluster  |  Kafka/Pulsar multi-AZ
         | WAL + RF=3          |
         +--+-----------+------+
            |           |
            |           +------------------+
            v                              v
   +----------------+              +----------------+
   | Hot Indexer    |              | Cold Segment   |
   | (allowlist)    |              | Writer         |
   +--------+-------+              +--------+-------+
            |                               |
            v                               v
   +----------------+              +----------------+
   | Hot Index      |              | Object Store   |
   | shards         |              | + blooms       |
   +--------+-------+              +--------+-------+
            \                               /
             \                             /
              v                           v
         +-----------------------------------+
         | Query Gateway / Merge             |
         | deadlines, partials, authz        |
         +-----------------------------------+
                         ^
                         | optional cross-region replicate
                         v
                  DR Region (async)
```

### 4.2 Critical path: ingest ACK

```text
Agent batch → TLS → authn/z → size/quota → sanitize
  → Kafka produce (project partition) → ISR quorum → 202 ACK
Indexer lag does NOT block ACK
```

### 4.3 Critical path: hot search

```text
Client query → gateway forces project_id
  → time prune segments/shards → scatter → merge → results
```

### 4.4 Critical path: regional failover

```text
Primary region down
  → clients use secondary ingest endpoint
  → buffer mirror lag = RPO (e.g. 5–60s)
  → promote secondary consumers; rebuild/catch up hot index
  → queries may miss RPO window — publish status banner
```

### 4.5 Backpressure

```text
Slow indexer → consumer lag ↑ → alert → autoscale indexers
If buffer near full → ingest priority: reject DEBUG first; protect ERROR
Never unbounded memory queues in gateway
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **ACK ⇒ record in replicated buffer** (or equivalent WAL quorum).  
2. **Ingest availability > index freshness** under degradation.  
3. **Tenant isolation on query** — hard filter `project_id`; IDOR tests.  
4. **Retention/delete honors legal hold**.  
5. **Cold segment immutable** once sealed; GC by policy only.  
6. **Bloom skips are safe** (no false negatives for used keys).  
7. **Quotas fail closed** when limiter unhealthy for free/noisy tiers.  
8. **Regional promote has single writer** for a cell after fence.  
9. **Redaction rules applied before cold leave region** if required.  
10. **Partial query results explicitly marked**.

#### 5.1.2 Write-ahead details

- Gateway does not persist local disk as SoT (optional spool for 503 retry on agent side).  
- Kafka `min.insync.replicas=2`, `acks=all`.  
- Corrupt poison messages → DLQ topic; don't block partition forever.  
- Schema validation soft vs hard: bad JSON → wrap as opaque message field.

#### 5.1.3 Exactly-once illusions

| Claim | Reality |
|-------|---------|
| Kafka EOS transactions | Help sink idempotency within pipeline; producers still retry |
| “No duplicate logs” | Need event_id + idempotent index `_id` |
| Cross-region EOS | Essentially at-least-once + dedupe |

Interview gold: **at-least-once + idempotent consumers**.

#### 5.1.4 Regional failure without loss (of acked)

```text
Goal: any batch ACKed in primary is on durable media that DR can read
Means: mirror buffer topics cross-region (async) OR dual-produce (sync cost)
MVP: async MirrorMaker/Pulsar replicator; RPO = mirror lag
Cold objects: CRR
Hot index: rebuild from buffer/cold after promote (RTO hours→mins with warm standby indexers)
```

**Deal-breaker:** “We're HA” but index-only in one AZ and ACK tied to it.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Disk full buffer | Water marks; shed samples |
| 10× | Hot tenant noisy | Separate mega-tenant topics |
| 100× | Query fanout storms | Gateways limits; pre-agg |
| 1,000× | Global mirror cost | Cell-local residency; selective CRR |

### 5.2 Scalability

#### 5.2.1 Shard by time + tenant

```text
partition_key = hash(project_id) % P
time_bucket = floor(event_time / bucket_size)   // e.g. 1h
index_shard = (time_bucket, partition_key)
cold_segment = same
```

Benefits: time prune, tenant isolation, retention drop whole segments.

#### 5.2.2 Ingest path scaling

| Jump | Technique |
|------|-----------|
| →10× | More gateway pods; more Kafka partitions; batch compression |
| →100× | Regional ingest cells; tenant placement; HTTP/2 + gRPC |
| →1,000× | Edge PoPs → regional buffers; avoid cross-ocean ACK |

#### 5.2.3 Index scaling

- Horizontal shards; avoid giant single Lucene for all tenants.  
- **Time-based indexes** rolled hourly/daily — drop cheap.  
- Segment merging throttled so merges don't starve ingest.  
- Cardinality: reject attr keys over flood threshold.

#### 5.2.4 Cold path & blooms

```text
Seal segment every N MB or T seconds
Write Parquet/ORC or row-group custom
Build bloom / fuse filters on message terms + trace_id
Upload object + metadata row (times, counts, bloom loc)
Query cold: metadata prune → bloom → download matching row groups
```

#### 5.2.5 Query planner

| Optimization | Effect |
|--------------|--------|
| Force tenant predicate | Security + prune |
| Time range required | Always (default last 15m) |
| Severity filter pushdown | Less data |
| Top-k early termination | Latency |
| Deadline + partial | Predictability |
| Cache recent popular queries | Optional |

**Hard limit:** `max_shards_touched` (e.g. 512); ask user to narrow.

#### 5.2.6 Live tail

- Tail reads from **buffer recent** or dedicated pubsub fanout, not deep index.  
- Per-connection buffer cap; disconnect slow readers.  
- Filter at edge to cut bandwidth.

#### 5.2.7 Progressive scale table

| Jump | Change |
|------|--------|
| →10× | Autoscale indexers; mega-tenant isolation |
| →100× | Cells; hot/warm/cold; async DR; sampling defaults |
| →1,000× | Edge ingest; query federation; EB cold; strict allowlists |

#### 5.2.8 Cost controls

- Sampling & severity routing.  
- Index allowlists.  
- Shorter hot retention.  
- Compression zstd.  
- Deduplicate agent heartbeats.  
- Chargeback per ingested GB / indexed GB.

### 5.3 Maintainability

#### 5.3.1 Config as code

Retention, sampling, redaction, index allowlists versioned per project; canary tenants.

#### 5.3.2 Observability of the observer

```text
ingest_ack_success, ingest_bytes, quota_rejects,
kafka_lag{consumer}, index_refresh_delay,
query_latency, query_shards_touched, query_partial_rate,
cold_scan_bytes, bloom_skip_rate, dlq_rate,
mirror_lag{region}, disk_watermark
```

#### 5.3.3 Testing

- Kill indexer: ACK continues; lag recovers.  
- Kill one AZ Kafka: still writable if ISR policy OK.  
- Chaos mirror lag: verify RPO dashboards.  
- Cardinality attack synthetic.  
- Query IDOR cross-tenant.

#### 5.3.4 Operability

- Replay from Kafka offset / cold reindex job.  
- Tenant quarantine switch.  
- “Index rebuild from cold for window W”.  
- Capacity dashboards in GB/s not only QPS.

#### 5.3.5 Safe evolution

Phase 1: ingest + Kafka + hot index + object cold.  
Phase 2: blooms + tiered query; sampling UI.  
Phase 3: multi-region DR promote runbooks.  
Phase 4: cells + edge.

---

## 6. Wrap-Up

### 6.1 What we designed

A **highly available multi-tenant logging system**: ACK after replicated buffer, fanout to hot index and cheap cold segments, schema/cardinality controls, retention tiers, query scatter-gather with deadlines and partials, sampling/backpressure, and regional failover with **explicit RPO**—not a fantasy of infinite indexed history.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| ACK vs index | ACK on buffer |
| Hot vs cold | Index accelerates; cold retains |
| Exactly-once | Idempotent sinks + optional event_id |
| Shard | time + tenant |
| HA region | Async mirror; publish RPO |
| Cost | Sample + allowlist + short hot |
| Fanout | Deadlines; max shards |
| Blooms | Skip I/O; no false negatives |

### 6.3 Closing line

> “Logging HA is about never lying on ACK, absorbing spikes in a real buffer, and putting most bytes in cold storage—indexes and cross-region sync are scoped accelerators with honest RPO, not magic.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Ingest & protocols

**Q1: gRPC vs HTTPS JSON?**  
A: gRPC/protobuf efficient at high volume; HTTPS easier for apps; support both via collectors.

**Q2: Why batching?**  
A: Amortize HTTP/Kafka overhead; aim 50–500 events or 64–256 KB.

**Q3: What if a batch partially fails validation?**  
A: Policy: reject all vs per-event errors; be explicit; don't ACK invalid silently.

**Q4: Agent disk spool?**  
A: Yes on 429/503; bounded disk; drop oldest with metric if overflowing (customer policy).

**Q5: Syslog UDP?**  
A: Best-effort; no ACK — separate low-guarantee path.

### 7.2 Buffer / WAL / Kafka

**Q6: Why RF=3?**  
A: Survive one AZ loss + maintenance; `acks=all` + `min.ISR=2`.

**Q7: How many partitions?**  
A: Target throughput / consumer parallelism; thousands OK; watch metadata; mega-tenants dedicated.

**Q8: Kafka as long-term store?**  
A: Expensive; use days of retention for replay, not years — cold objects for years.

**Q9: Pulsar tiered storage?**  
A: Attractive: buffer transparently offloads to object store; still need query indexes.

**Q10: Ordering guarantees?**  
A: Per-partition order only; per-host order if keyed by host; global order impossible cheaply.

### 7.3 Exactly-once & dedupe

**Q11: Kafka transactions enough?**  
A: Help between topics/sinks; producers and multi-region still need idempotency story.

**Q12: event_id generation?**  
A: ULIDs/UUIDv7 by producer; ingest may assign if absent (then retries duplicate).

**Q13: Dedup store size?**  
A: Bloom + LRU window per tenant for recent ids; accept rare dupes outside window.

**Q14: Why duplicates hurt?**  
A: Alert double-fire; storage $; user trust — mitigate but don't overclaim zero.

### 7.4 Indexing

**Q15: Inverted index vs columnar?**  
A: Inverted for token search; columnar for analytics filters/agg; many systems hybrid.

**Q16: Mapping explosion?**  
A: Cap distinct keys; flatten carefully; reject high-cardinality dynamic fields.

**Q17: Why time-based indexes?**  
A: Drop/retain whole index; query prune; compaction locality.

**Q18: Refresh interval tradeoff?**  
A: Faster refresh → sooner searchable, more resource; 1s–30s typical.

**Q19: Doc values / norms cost?**  
A: Disable unused features; huge savings.

### 7.5 Cold storage & blooms

**Q20: Parquet vs raw gzip JSON?**  
A: Parquet prune columns/row groups; better scans; more sealing complexity.

**Q21: How does a bloom skip work?**  
A: If term cannot be in segment, skip download; if maybe, fetch.

**Q22: Bloom false positive impact?**  
A: Extra I/O only; correctness OK.

**Q23: Could bloom false negative?**  
A: If buggy build/wrong key — **correctness bug**; test heavily; or don't skip.

**Q24: Fuse / zone maps?**  
A: Min/max on time and numeric fields for prune.

### 7.6 Query & LB

**Q25: Scatter-gather bottlenecks?**  
A: Slowest shard; mitigate with deadlines, speculative retry carefully, skew-aware placement.

**Q26: How to page results?**  
A: Search_after / keyset on (time, id); avoid deep `from+size`.

**Q27: Cross-cell query?**  
A: Gateway fans to cells owning tenant; avoid global broadcast.

**Q28: Load balancer for ingest?**  
A: L4/L7; connection reuse; optional power-of-two choices; shed load on 429.

**Q29: Consistent hashing tenants to cells?**  
A: Yes; virtual nodes; migration with dual-read.

### 7.7 Multi-tenant & memory

**Q30: Noisy neighbor?**  
A: Per-tenant produce quotas, partition isolation, query concurrency tokens.

**Q31: Heap risk on ingest?**  
A: Bound batch decode memory; stream parse; recycle buffers.

**Q32: Query memory?**  
A: Circuit break large sorts; top-k only; spill carefully.

**Q33: Hot partitions?**  
A: Split mega-tenant across partitions by `hash(service)` secondary key.

### 7.8 Retention & compliance

**Q34: Hot vs cold delete?**  
A: Drop index first (save $); cold lifecycle rules; legal hold blocks.

**Q35: WORM?**  
A: Object lock; separate compliance bucket.

**Q36: Redaction after write?**  
A: Hard — rewrite segments / tombstone fields; prefer ingest-time redact.

**Q37: GDPR delete user id in logs?**  
A: Painful; minimize PII; crypto-shredding tokens if designed in.

### 7.9 Regional HA

**Q38: Sync dual-produce ACK?**  
A: Higher latency; stronger RPO≈0 cross-region; costly; rare MVP.

**Q39: What is RTO for query after failover?**  
A: Ingest OK fast; hot query needs warm standby indexers or rebuild — state minutes–hours.

**Q40: Split brain?**  
A: Fencing token / single active primary per cell via consensus/config.

**Q41: Clients during failover?**  
A: Multi-endpoint; retry other region; idempotent event_ids help.

### 7.10 Backpressure & shedding

**Q42: Order of shed?**  
A: DEBUG/sample → INFO → delay non-critical tenants → protect ERROR/audit tenants.

**Q43: Fairness?**  
A: Weighted fair drop; don't starve small tenants entirely.

**Q44: Indexer autoscale lag signal?**  
A: Consumer lag + seal delay; scale before buffer watermark.

### 7.11 Algorithms & data structures

**Q45: HyperLogLog use?**  
A: Approximate distinct fields/services for cardinality guards.

**Q46: Count-Min sketch?**  
A: Heavy-hitter tenants/keys detection.

**Q47: LSM vs B-tree for index?**  
A: Lucene-like segments are LSM-ish; understand merge costs.

**Q48: Timing wheels for retention?**  
A: Optional; usually daily jobs + object lifecycle.

### 7.12 Storage math drills

**Q49: RF impact on cost?**  
A: Hot RF=2/3 multiplies disk; cold RF via object store 11-9s erasure cheaper.

**Q50: When to stop indexing a field?**  
A: When unique values ≈ event rate (user_id) — high cost low value for general search.

### 7.13 10× / 100× / 1,000×

**Q51: First wall at 10×?**  
A: Kafka disk & indexer CPU; mapping storms.

**Q52: At 100×?**  
A: Cross-region bandwidth $; query fanout; need cells.

**Q53: At 1,000×?**  
A: Most data never hot-indexed; edge ingest; strict defaults.

### 7.14 Deal-breakers checklist

**Q54: Name three deal-breakers.**  
A: (1) ACK without quorum durability, (2) indexing arbitrary JSON keys unbounded, (3) claiming zero RPO multi-region with only async mirror and no disclosure.

---

## Appendix A: Example query DSL

```text
{
  "time": {"from": "-15m", "to": "now"},
  "query": "timeout OR payment_failed",
  "filter": {"severity": ["ERROR","WARN"], "service": ["checkout"]},
  "limit": 100,
  "partial_ok": true,
  "deadline_ms": 5000
}
```

## Appendix B: Segment metadata row

```text
segment_id | project_id | t_start | t_end | event_count | bytes
| cold_uri | bloom_uri | min_severity | schema_version
```

## Appendix C: Interview 45-minute plan

1. Requirements + ACK semantics + tiers (7 min)  
2. Numbers GB/s + cost of index (5 min)  
3. Architecture buffer/index/cold (10 min)  
4. Query fanout + blooms (7 min)  
5. Multi-tenant + backpressure (6 min)  
6. Regional RPO/RTO (5 min)  
7. Q&A  

---

*End of highly available logging system design.*
