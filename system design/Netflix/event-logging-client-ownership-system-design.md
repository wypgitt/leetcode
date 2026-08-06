# System Design: Event Logging Platform — Client Library Ownership vs Docs-Only SDK

> **Focus areas:** Schema evolution · Client vs server ownership · Batching & backpressure · Privacy / PII scrubbing · Delivery guarantees · Observability of observability · Multi-platform rollout · Cost at Netflix scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit ownership boundaries, split dissimilar QPS (ingest vs query vs config), deal-breaker gallery, Netflix 2025–26 platform interview themes  
> **Interview theme:** Netflix Platform — should the event-logging team **own and ship client libraries** (iOS, Android, TV, Web) or publish **docs-only contracts** and let product teams integrate?

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

Goal: **design an internal event-logging platform** that collects structured behavioral and operational events from Netflix clients and services, with a deliberate strategy for **who owns client integration** — centralized SDK team vs docs-only schema registry.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Ingest, validate, route, store, query events at scale | Full product analytics BI suite (Tableau replacement) |
| Client strategy | Own libs vs docs-only — core interview fork | Generic "Kafka tutorial" |
| Events | Clickstream, playback, errors, experiments | Billing ledger / payment events (sibling) |
| Delivery | At-least-once with idempotency; best-effort on client | Exactly-once end-to-end without tradeoffs stated |
| Privacy | PII scrub, consent gates, retention | Full legal/compliance sign-off doc |
| Query | Real-time aggregates + batch warehouse export | Ad-hoc SQL for every PM |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What events? | UI clicks, navigation, playback milestones, errors, perf, A/B exposure | Typed schema registry |
| F2 | Who emits? | All client apps (mobile, TV, web) + some backend services | Multi-language SDK or HTTP contract |
| F3 | Schema ownership? | Central analytics/platform owns canonical schemas | Registry + validation |
| F4 | Client lib ownership? | **Interview fork:** platform owns vs product owns | Release cadence, staffing, quality bar |
| F5 | Offline / flaky network? | Queue locally; flush on reconnect | Client buffer + disk persistence |
| F6 | Batching? | Yes — reduce requests, amortize overhead | Batch size + time triggers |
| F7 | Real-time needs? | Dashboards, alerting on error spikes | Stream processing path |
| F8 | Historical needs? | Data warehouse, ML features, replay | Cold storage + export |
| F9 | Experimentation hooks? | `experiment_id`, `cell`, exposure logging | First-class fields + validation |
| F10 | PII policy? | No raw email/password; hash device ids per policy | Client + server scrubbers |
| F11 | Debug mode? | Sampled verbose logs for eng | Feature flag + rate cap |
| F12 | Schema changes? | Backward compatible adds; breaking = new event type | Versioned schemas |
| F13 | Kill switch? | Disable non-critical events under outage | Remote config |
| F14 | Cross-app identity? | Profile id when authed; anonymous pre-login | Subject resolution rules |

**MVP functional scope (lock with interviewer):**

1. Schema registry with JSON/Protobuf definitions, versioning, and CI validation.
2. HTTPS ingest API accepting batched events with auth (app token + device attestation optional).
3. Server-side validation, PII scrub, enrichment (server timestamp, geo coarse, app version).
4. Durable write to Kafka (or equivalent) → stream consumers + daily warehouse load.
5. **Hybrid client strategy MVP:** platform-owned **thin reference SDK** + **mandatory schema docs**; product teams may wrap or reimplement if they pass certification tests.
6. Client offline queue with max size and drop-low-priority policy.
7. Idempotency via `event_id` (UUID) for dedupe window.
8. Ops dashboards: ingest rate, validation error rate, lag, dropped-client-events.

**Out of MVP (explicitly defer):**

- Platform-owned full-featured SDK for every exotic TV chipset day one
- Sub-second global query for arbitrary ad-hoc filters
- Perfect exactly-once from client to warehouse without duplicates
- Client-side ML feature computation
- Public third-party SDK product

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest latency (server ACK)? | Client shouldn't block UX | p99 < 50ms ingest ACK (after batch accept) |
| N2 | Client CPU / battery | Minimal | < 1% CPU avg; batching default |
| N3 | Durability after ACK | Don't lose accepted events | RF=3 Kafka; sync min ISR |
| N4 | Availability ingest | Degrade gracefully | 99.95% — client buffers on failure |
| N5 | Throughput | Netflix-scale sessions | See scale table |
| N6 | Schema drift tolerance | Reject unknown required fields | Validation + dead-letter |
| N7 | Privacy | GDPR/CCPA aligned process | Retention + delete pipeline |
| N8 | Cost | Pennies per MAU | Tiered storage; sampling for verbose |
| N9 | SDK release velocity | Match app release trains | Versioned SDK semver |
| N10 | Observability | Monitor the monitor | Meta-metrics on pipeline |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User taps "Play" → client enqueues `ui.click` + `playback.start` → batch flush every 5s or 50 events → ingest validates → Kafka → Flink aggregate error rate.
2. TV app offline 10 minutes → events persist to disk queue → on reconnect exponential backoff upload → server dedupes by `event_id`.
3. New schema field `subtitle_lang` added optional → old clients still valid → new clients populate.
4. Experiment exposure logged once per session per experiment key.
5. Backend service emits `service.request` via gRPC sidecar without mobile SDK.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Client queue full | Drop `DEBUG` tier first; never drop `ERROR` / `playback.heartbeat` policy tier |
| Invalid schema version | 400 with error code; client drops batch or routes to dead-letter file |
| Ingest regional outage | Client failover to secondary region; merge dedupe |
| Duplicate `event_id` retry | Server idempotent accept within 24h window |
| Clock skew on client | Server assigns `ts_ingest`; retain `ts_client` for debug |
| PII detected in payload | Scrub field / reject event per policy; metric `pii_reject` |
| Kafka lag spike | Autoscale consumers; temporarily increase sampling on verbose events |
| SDK bug double-sends | Dedupe + monitor SDK version error budget |
| App rollback old SDK | Schemas backward compatible; deprecated events still accepted |
| Malicious client spoofing | mTLS / signed batches / device attestation for high-trust events |
| GDPR delete subject | Tombstone pipeline purges keyed events in retention window |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU emitting events | 200M | 200M (saturated) | 300M | 500M+ |
| Peak events / s (ingress) | 2M | 20M | 50M | 200M |
| Avg event size | 500 B | 500 B | 450 B (compression) | 400 B |
| Client apps / platforms | 12 | 15 | 20 | 25+ |
| Distinct event types | 800 | 2K | 5K | 10K |
| Schema versions active | 50 | 150 | 400 | 1K |
| Ingest QPS (HTTP batches) | 40K | 400K | 1M | 4M |
| Kafka ingress MB/s | ~1 GB/s | ~10 GB/s | ~25 GB/s | ~80 GB/s |
| Warehouse daily | 50 TB | 500 TB | 1.2 PB | 4 PB |

**Split classes:** client enqueue ≠ HTTP ingest ≠ validation ≠ Kafka produce ≠ stream agg ≠ batch ETL ≠ ad-hoc query.

**What each jump forces:**

- **10×:** Regional ingest cells; aggressive batching; schema validation cache; separate hot/cold topics.
- **100×:** Edge aggregation for high-cardinality counters; sampling policies; dedicated SDK reliability team if owned libs.
- **1,000×:** Protocol buffers + zero-copy pipelines; client-side pre-aggregation for heartbeats; tiered trust paths.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like global streaming: many device types, intermittent connectivity.
- **Core interview tension:** owning client libs improves consistency but creates a **platform bottleneck** and **release coupling**.
- Docs-only reduces platform headcount but risks **schema drift**, **inconsistent batching**, and **privacy leaks**.
- Assumed compromise for Netflix: **own thin SDK + certification** for Tier-1 events; docs-only allowed for internal microservices.

**Scope statement:**

> Design an event-logging platform with schema registry, ingest, stream+batch paths, and an explicit **client ownership strategy** (owned SDK vs docs-only), evolving from ~2M events/s through 10× / 100× / 1,000× with privacy, idempotency, and client backpressure policies.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Event volume

```text
DAU = 200M
Events / DAU / day ≈ 200 (clicks, impressions, playback, errors)
Daily events = 200M × 200 = 40B events / day

Peak factor ≈ 3× daily average rate in prime time
Avg rate = 40B / 86400 ≈ 462K events/s
Peak ≈ 1.4M → round to 2M events/s baseline interview number
```

### 2.2 Bandwidth

```text
2M events/s × 500 B = 1 GB/s ingress raw
With batch compression (gzip/zstd): ~300–400 MB/s on wire
At 100×: 50M events/s → 25 GB/s raw → ~8 GB/s compressed class
```

**Deal-breaker:** per-event HTTP request at 2M/s → 2M QPS — need batching.

### 2.3 Batching math

```text
Batch size = 50 events
Batch interval = 5 s max wait
Events / user / s ≈ 0.002 average (200/day spread)
Concurrent active users peak ≈ 30M
Events / s from users ≈ 60K/s ... plus playback heartbeats dominate

Playback heartbeats: 30M streams × 1/30s ≈ 1M/s alone
Hence total ~2M/s baseline credible
```

```text
If batch size 20 for heartbeats coalesced on client:
Ingest QPS ≈ 2M / 20 = 100K QPS → still need connection pooling + regional sharding
Target batches: 50–100 events → 20K–40K ingest QPS baseline
```

### 2.4 Kafka partitions

```text
Target per-partition throughput ≈ 5–10 MB/s
1 GB/s / 5 MB/s ≈ 200 partitions minimum baseline
With headroom: 400–800 partitions per topic tier
Keys: hash(profile_id) for locality; avoid hot key on global counters
```

### 2.5 Storage (30-day hot + warehouse)

```text
Daily raw = 40B × 500B = 20 TB/day
30-day Kafka retention (subset full): maybe 3 days hot = 60 TB tiered
Warehouse compressed columnar ~5× → ~4 TB/day long-term
Yearly warehouse ≈ 1.5 PB before lifecycle to cold glacier
```

### 2.6 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Client enqueue (logical) | 2M/s | 50M/s | 200M/s | mostly in-memory |
| HTTP ingest requests | 40K | 1M | 4M | batched |
| Validation CPU | 2M/s | 50M/s | 200M/s | SIMD / cache schemas |
| Kafka produce | 2M/s | 50M/s | 200M/s | async pipeline |
| Dedupe lookups | 200K/s | 5M/s | 20M/s | 10% retry rate assumption |
| Stream agg | 500K/s | 10M/s | 40M/s | filtered subset |
| Schema registry reads | 500 | 5K | 50K | cached on ingest |
| Warehouse load jobs | 1K/min | 10K/min | 40K/min | partitioned |

### 2.7 Client resource budget

```text
Queue on disk max = 2 MB per app (policy)
Memory queue = 256 KB default
Flush thread: 1 background thread per app
Serialization: protobuf ~30% smaller than JSON → prefer protobuf in owned SDK
```

### 2.8 Latency budget (ingest path)

| Stage | Budget |
|-------|--------|
| LB + TLS termination | 2–5ms |
| Auth + rate limit | 1–3ms |
| Schema validate batch | 5–15ms |
| PII scrub | 3–10ms |
| Kafka produce ack (min ISR) | 10–30ms |
| **Total server p99** | **< 50ms** |

Client async: enqueue < 1ms on hot path.

### 2.9 Staffing implication (ownership fork)

| Strategy | Team size (illustrative) | Risk |
|----------|--------------------------|------|
| Full owned SDK all platforms | 25–40 eng (iOS/Android/TV/Web/Release) | High consistency, high cost |
| Docs-only + certification | 8–12 platform eng | Fragmentation risk |
| Hybrid thin SDK | 15–20 eng | Balanced — Netflix typical answer |

### 2.10 Critical bottlenecks

1. **Uncoalesced heartbeats** — dominant volume.
2. **Schema validation CPU** at 50M/s.
3. **Hot keys** if routing all events to one partition key badly.
4. **Client disk queue abuse** on memory-constrained TVs.
5. **SDK release train** blocking app releases if owned libs mismanaged.

---

## 3. High-Level Design

### 3.1 Ownership strategy (the interview fork)

```text
                    ┌─────────────────────────────────────┐
                    │         Schema Registry (SoT)        │
                    │  event types, fields, privacy class  │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
          v                           v                           v
 ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
 │ Owned Thin SDK  │       │ Partner SDK wrap│       │ Docs-only HTTP  │
 │ (Platform team) │       │ (App team ext)  │       │ (Services/TV)   │
 └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
          │                           │                           │
          └───────────────────────────┼───────────────────────────┘
                                      v
                           ┌─────────────────────┐
                           │   Ingest Gateway    │
                           │ validate / scrub    │
                           └──────────┬──────────┘
                                      v
                           ┌─────────────────────┐
                           │   Kafka / Pulsar    │
                           └──────────┬──────────┘
                                      v
                    ┌─────────────────┴─────────────────┐
                    v                                   v
           ┌────────────────┐                 ┌────────────────┐
           │ Stream (Flink) │                 │ Batch (Spark)  │
           │ alerts / RT    │                 │ warehouse / ML │
           └────────────────┘                 └────────────────┘
```

**Recommended Netflix answer:** **Hybrid**

| Tier | Ownership | Rationale |
|------|-----------|-----------|
| Tier-1 playback + billing-adjacent | Platform-owned SDK modules | Correctness, compliance |
| Tier-2 UI interaction | Platform thin SDK + app skinning | Consistency |
| Internal backend services | Docs-only Avro/Proto + sidecar | Velocity |
| Legacy TV chipsets | Docs-only + certification test suite | Platform can't staff N forks |

### 3.2 Entities

| Entity | Role |
|--------|------|
| `EventType` | Named schema in registry |
| `Event` | `{event_id, type, version, ts_client, payload, context}` |
| `ClientContext` | app, version, device, profile, session, locale |
| `PrivacyClass` | PUBLIC / SENSITIVE / FORBIDDEN |
| `Batch` | Container up to N events or T seconds |
| `IngestToken` | App credential scoped to event types |
| `DedupeRecord` | `event_id` → seen TTL |

### 3.3 Client SDK responsibilities (when owned)

| Responsibility | Must | Nice |
|----------------|------|------|
| Schema-compliant serialization | ✓ | |
| Offline queue + backoff | ✓ | |
| Batching / flush triggers | ✓ | |
| Remote config (sampling, kill) | ✓ | |
| PII pre-redaction | ✓ | |
| Auto context fields | ✓ | |
| Debug overlay | | ✓ |
| Client-side aggregation | | ✓ (100×) |

**Docs-only alternative:** publish spec + **conformance tests** (CI docker image); apps must pass before store release gate.

### 3.4 Ingest API (logical)

```text
POST /v1/events:batch
Headers: Authorization, X-App-Id, X-SDK-Version, X-Schema-Set-Version
Body: Batch { events[], compressed_payload? }

Response 202: { accepted: n, rejected: [...], deduped: m }
```

Validation steps:

1. AuthN/Z — token allows event types in batch.
2. Size limits — max 256 KB batch.
3. Per-event schema validation against registry snapshot.
4. PII scrubber pipeline.
5. Enrichment — server ts, ingest region.
6. Idempotency filter.
7. Produce to Kafka topic by `{event_type, privacy_tier}`.

### 3.5 Schema registry

```text
EventTypeDefinition {
  name: "playback.start"
  version: 14
  compatibility: BACKWARD
  fields: [...]
  privacy_class: SENSITIVE
  owners: ["playback-team"]
  sampling_default: 1.0
  required_context: [profile_id?, device_id, session_id]
}
```

CI gates:

- No removing required fields without new event name.
- Privacy review on new SENSITIVE fields.
- Load test simulation for expected QPS tier.

### 3.6 Topic routing

| Topic tier | Events | Retention |
|------------|--------|-----------|
| `events.critical` | playback, errors fatal | 7d hot |
| `events.interaction` | clicks, nav | 3d hot |
| `events.debug` | verbose | 1d + sampled |
| `events.audit` | consent, deletion | years (compliance) |

### 3.7 Stream vs batch

| Path | Use |
|------|-----|
| Flink / Samza | Error rate alerts, real-time experiment monitoring |
| Spark / Snowflake load | ML training, dashboards, A/B analysis |
| Iceberg / Delta lake | Time travel, GDPR deletes |

### 3.8 Remote config (client)

```json
{
  "flush_interval_ms": 5000,
  "max_batch_size": 50,
  "max_queue_bytes": 2097152,
  "disabled_events": ["debug.ui.layout"],
  "sample_rates": {"playback.heartbeat": 0.1},
  "ingest_endpoints": ["https://ingest-us-west.netflix.com"]
}
```

Pushed via existing app config system; SDK caches with TTL.

### 3.9 Privacy & consent

```text
Consent gate (client): if !analytics_consent → drop INTERACTION, keep CRITICAL errors anonymized
Server scrub: regex + column policy on FORBIDDEN fields
Pseudonymize: profile_id → keyed hash for pre-auth events
```

### 3.10 Failure policy

| Failure | Client behavior | Server behavior |
|---------|-----------------|-----------------|
| 503 ingest | Exponential backoff; persist queue | Shed DEBUG tier via 429 |
| Validation error | Drop bad events; metric locally | Return per-event errors |
| Queue full | Drop lowest priority tier | N/A |
| SDK crash safety | WAL on disk before ACK enqueue | N/A |

### 3.11 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Client ownership | Hybrid thin SDK + certification |
| Wire format | Protobuf canonical; JSON for debug tools |
| Delivery | At-least-once; event_id dedupe |
| Ordering | Per-session partial order; not global |
| SoT for schemas | Registry with CI |
| Heartbeats | Sample + aggregate at 100× |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+----------+  enqueue   +----------------+  batch POST   +------------------+
| Mobile/  |----------->| Event SDK      |-------------->| Ingest Gateway   |
| TV/Web   |            | (owned thin)   |               | (regional)       |
+----------+            +----------------+               +--------+---------+
                                                               |
                     +------------------+                      |
                     | Schema Registry  |<---------------------+
                     +------------------+                      |
                                                               v
                     +------------------+               +------+------+
                     | Remote Config    |               | Validate /  |
                     | Service          |               | Scrub /     |
                     +------------------+               | Dedupe      |
                                                        +------+------+
                                                               |
                                                               v
                                                        +------+------+
                                                        | Kafka       |
                                                        +------+------+
                                                               |
                        +----------------------+---------------+--------------------+
                        v                      v                                    v
                 +-------------+        +-------------+                      +-------------+
                 | Flink RT    |        | Spark ETL   |                      | GDPR Delete |
                 | Alerts      |        | Warehouse   |                      | Worker      |
                 +-------------+        +-------------+                      +-------------+
```

### 4.2 Sequence: client batch upload

```text
App→SDK: track("ui.click", payload)
SDK: enrich context, assign event_id, write memory queue
SDK: if batch full OR timer → serialize protobuf → POST ingest
Ingest: auth → validate → scrub → dedupe → produce Kafka
Ingest→SDK: 202 Accepted {accepted:n}
SDK: delete persisted WAL for acked events
```

### 4.3 Sequence: offline recovery

```text
Network down → SDK writes queue to disk (cap 2MB)
Network up → SDK backoff 1s,2s,4s... → retry batches
Duplicate POST → dedupe by event_id → client treats as success
```

### 4.4 Sequence: schema rollout

```text
Team proposes playback.start v15 → CI compat check → privacy review
Registry publishes v15 (backward compatible)
SDK v3.2 ships knowing v15 fields optional
Old SDK still sends v14 → valid
Ingest pins validation to max supported per app version (optional strict mode)
```

### 4.5 Docs-only integration path

```text
App team reads OpenAPI + Proto specs
Implements batch client internally
Runs certification docker: golden batches + fuzz + PII leak tests
Release gate blocks if certification fails
Platform does NOT block app release if SDK semver unchanged but cert passes
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Never block UI thread** on network I/O — async flush only.
2. **Accepted events durable** in Kafka min ISR before 202.
3. **Idempotent ingest** on `event_id` for 24–72h.
4. **Schema backward compatibility** enforced in CI.
5. **Privacy scrub** cannot be skipped on SENSITIVE paths.
6. **Critical events** bypass sampling kill except explicit ops flag.
7. **Client queue bounded** — no unbounded OOM on TV devices.
8. **SDK version tagged** on every batch for rollback analytics.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Kafka unavailable | Return 503; client retains queue |
| Partial batch invalid | Accept good events; reject bad with detail |
| Registry unreachable | Ingest uses cached schema snapshot; alert if stale > 1h |
| Dedupe store down | Fail open accept + downstream dedupe (duplicate budget) |
| Scrubber crash mid-batch | Fail batch 500; client retries whole batch idempotently |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Regional ingest clusters; Kafka 400 partitions; thin SDK v1 |
| 10× | Separate heartbeat topic with sampling; edge validation cache |
| 100× | Client-side heartbeat aggregation (30s → 5 min summaries); dedicated dedupe Redis cluster |
| 1,000× | Binary ingest protocol (HTTP/3 QUIC); optional edge coalescing proxies; tiered trust fast path |

**Sharding:** ingest by geo DNS; Kafka by `hash(profile_id || device_id)`.

### 5.3 Maintainability — owned SDK vs docs-only

| Concern | Owned SDK | Docs-only |
|---------|-----------|-----------|
| Consistent batching | Strong | Weak without enforcement |
| Schema updates | Platform releases SDK | Each team updates |
| Bug fixes (double send) | Central patch | Slow / uneven |
| Platform headcount | High | Low |
| App team velocity | Coupled to SDK release | Faster custom |
| TV long tail | Platform overwhelmed | Certified custom |
| Interview soundbite | "We own correctness paths" | "We own contracts + cert" |

**Netflix hybrid governance:**

- Platform owns **codegen** from registry → Swift/Kotlin/JS stubs.
- App teams **may** use stubs directly or wrap.
- **Certification required** for store submission regardless.
- Breaking changes only via **new event type name** (`playback.start_v2`).

### 5.4 Exact algorithm: client flush

```text
function onTrack(event):
  if !consentAllows(event.type): return
  if sampleSkip(event.type): return
  event.event_id = uuid()
  event.ts_client = now()
  event.context = buildContext()
  queue.append(event)
  persistWAL(event)  // fsync batched
  if queue.size >= MAX_BATCH or timerExpired():
    flushAsync()

function flushAsync():
  batch = queue.drainUpTo(MAX_BATCH)
  POST ingest with retry/backoff
  on 202: WAL.remove(batch.ids)
  on 4xx permanent: WAL.drop(batch.ids); logError
  on 5xx/timeout: WAL.keep; schedule retry
```

### 5.5 Exact algorithm: server validate

```text
function handleBatch(batch, auth):
  assert auth.allows(batch.eventTypes)
  snapshot = registry.getSnapshot(auth.app_id)
  accepted = []
  for e in batch.events:
    if dedupe.seen(e.event_id): continue
    schema = snapshot.schema(e.type, e.version)
    if !schema: reject(e, UNKNOWN_TYPE); continue
    e2 = scrubPII(e, schema.privacy)
    if !validate(e2, schema): reject(e2); continue
    enrich(e2)
    accepted.append(e2)
    dedupe.mark(e.event_id, TTL=72h)
  kafka.produceMulti(accepted)
  return 202(accepted, rejected)
```

### 5.6 Heartbeat storm mitigation

```text
Baseline: 1 heartbeat / 30s / stream → 1M/s at 30M streams
Mitigation ladder:
  L1 sample 10% → 100K/s
  L2 client aggregate 5 min window → 100K/300 ≈ 333/s class (plus variance)
  L3 delta-only on meaningful state change (pause/resume/quality shift)
```

State which ladder step applies at each scale tier in interview.

### 5.7 Multi-region

| Concern | Strategy |
|---------|----------|
| Ingest | Geo-routed; client endpoint list in remote config |
| Kafka | Cluster per region; mirror critical topics for global jobs |
| Dedupe | Region-local store; cross-region duplicates acceptable at 1e-6 rate downstream |
| GDPR delete | Global orchestrator fans out to all regions |

### 5.8 Observability of observability

Metrics:

- `ingest_accept_rate`, `validation_error_rate`, `pii_scrub_rate`
- `kafka_lag`, `dedupe_hit_rate`, `client_queue_drop_rate` by SDK version
- `schema_unknown_rate` — early signal of drift (docs-only risk)
- SLO burn by app/platform

Dashboards segmented by **SDK version** vs **custom client** to prove ownership value.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Sync HTTP per click | QPS explosion; battery drain |
| Unbounded client queue | OOM; TV crashes |
| No idempotency | Retry duplicates inflate metrics |
| Schema breaking change in place | Old apps break silently |
| Platform owns everything including UI tracking wrappers | Release bottleneck |
| Docs-only with no certification | Privacy leak in one app → regulatory incident |
| Logging raw email to "debug" | GDPR fire |
| Global Kafka single partition key | Hot spot |
| Blocking play button on log flush | UX disaster |
| Trust client PII scrub only | One team forgets → leak |

### 5.10 Progressive scale deep dive

**1× (~2M events/s)** — Hybrid SDK v1; 3 ingest regions; Kafka; Flink; 400 partitions.

**10×** — Heartbeat sampling; schema snapshot cache; zstd mandatory.

**100×** — Client aggregation in SDK; gRPC sidecar for services; sharded dedupe Redis.

**1,000×** Binary protocol; edge coalesce; ML anomaly on validation CPU.

### 5.11 Security

- mTLS or signed JWT for ingest tokens; rotate keys.
- Rate limit per device / profile to prevent bot floods.
- Separate tokens for DEBUG events (higher quota approval).
- No executable code in event payloads; max nesting depth.

### 5.12 Rollout

```text
New SDK: canary 1% devices → monitor crash + queue drops → 10% → 100%
New schema: shadow validate (log-only rejects) → enforce
Docs-only team: require cert in CI pipeline before merge to release branch
Kill switch: remote config disable event types globally
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Client ownership | **Hybrid:** owned thin SDK + codegen + certification |
| Wire format | Protobuf batches over HTTPS |
| Ingest | Regional gateway, validate/scrub/dedupe |
| Storage | Kafka hot → warehouse cold |
| Delivery | At-least-once; event_id dedupe |
| Heartbeats | Sample + aggregate at scale |
| Schema | Central registry with backward compat CI |
| Docs-only | Allowed for services; apps must pass cert |

### 6.2 Risks

1. SDK release coupling delays app features
2. Docs-only teams ship PII leaks despite cert
3. Heartbeat volume dominates cost if sampling misconfigured
4. Schema sprawl — 10K event types unmaintainable without owners
5. Cross-region dedupe gaps → duplicate counts in dashboards
6. TV long tail not covered by thin SDK

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Clarify event types, volumes, privacy |
| 5–12 | **Ownership fork** — argue hybrid with certification |
| 12–20 | Client queue, batching, offline |
| 20–30 | Ingest validate path + Kafka + dedupe |
| 30–38 | Scale: heartbeats, QPS math trap |
| 38–45 | Stream vs batch, GDPR, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Ownership philosophy

**Q: Why not fully own all client SDKs?**
A: Netflix has dozens of device SKUs and app squads; platform becomes release bottleneck; certification scales better than centralizing every UI hook.

**Q: Why not docs-only everywhere?**
A: Playback and privacy-critical paths need identical behavior; fragmentation causes warehouse distrust and compliance gaps.

**Q: What does "thin SDK" mean?**
A: Transport, batching, queue, context, config, codegen — NOT every product analytics helper.

### 7.2 Delivery semantics

**Q: Exactly-once?**
A: End-to-end exactly-once impractical; at-least-once + idempotent `event_id` + downstream dedupe windows.

**Q: Client crash before flush?**
A: WAL on disk for Tier-1; acceptable loss for DEBUG.

**Q: Ordering guarantees?**
A: Per-partition order if keyed by session; global order not required.

### 7.3 Schema evolution

**Q: Add required field?**
A: New event type or new version with new name; never break old clients.

**Q: Rename field?**
A: Add new, deprecate old, dual-write in SDK transition.

**Q: Unknown fields?**
A: Protobuf ignores unknown; JSON strip or reject based on mode.

### 7.4 Privacy

**Q: Can profile_id be in events?**
A: Yes for authenticated Tier-1 with retention policy; hash at edge for anonymous.

**Q: Right to deletion?**
A: Orchestrated delete in warehouse + Kafka compacted topics where applicable; client queues purged on logout.

**Q: Kids profiles?**
A: Stricter sampling; some events forbidden by policy flag in SDK.

### 7.5 Cost

**Q: Biggest cost driver?**
A: Heartbeats + DEBUG verbosity — attack with sampling and aggregation.

**Q: Compress on client or server?**
A: Client zstd batch body; server stores columnar compressed.

### 7.6 Testing & comparison

**Q: How certify docs-only clients?** Docker harness with golden batches, fuzz, PII detectors.

**Q: Why not Segment / Amplitude?** Data residency, cost at Netflix volume, custom TV stacks.

**Q: OpenTelemetry?** Good for traces; business events still need schema registry.

### 7.7 Interview traps

**Q: "Just use Firehose to S3"?**
A: Still need schema, client strategy, dedupe, privacy — managed pipe ≠ platform.

**Q: "SDK in every app is fine"?**
A: Ask about TV long tail and release coupling — lead to hybrid.

**Q: "Log everything"?**
A: Cost + privacy + noise; tier events.

**Q: "Client sends directly to Kafka"?**
A: Credentials leak; no scrub/validate choke point.

### 7.8 Metrics that matter

**Q: What do you page on?**
A: Ingest error rate, Kafka lag, validation spike (schema drift), SDK queue drop rate, pii_reject anomaly.

### 7.9 Backend services path

**Q: Services without SDK?**
A: Sidecar agent or lightweight library; docs-only proto; mTLS to ingest.

---

## 8. Appendices

### A1. Event envelope schema

```text
Event {
  event_id: UUID
  type: string
  schema_version: int
  ts_client_ms: int64
  ts_ingest_ms: int64  // server
  privacy_class: enum
  context: ClientContext
  payload: bytes // typed per event
}

ClientContext {
  app_id, app_version, sdk_version,
  device_id, profile_id?, session_id,
  locale, connection_type, client_ip_coarse
}
```

### A2. Batch request

```protobuf
message EventBatch {
  repeated Event events = 1;
  Compression compression = 2; // NONE, ZSTD
  string sdk_version = 3;
  string schema_set_hash = 4;
}
```

### A3. Registry entry

```text
EventType {
  name: "playback.start"
  version: 14
  compatibility: BACKWARD
  owner_team: "playback"
  fields: [...]
  privacy_class: SENSITIVE
  default_sample_rate: 1.0
  kafka_topic: "events.critical"
}
```

### A4. Launch checklist

- [ ] Hybrid ownership doc signed (platform + client leads)
- [ ] Certification docker in app CI
- [ ] PII scrubber golden tests
- [ ] Dedupe TTL aligned with retry policy
- [ ] Remote config kill switch tested
- [ ] Kafka lag autoscaling verified
- [ ] GDPR delete runbook
- [ ] SDK canary dashboard

### A5. Glossary

| Term | Meaning |
|------|---------|
| Thin SDK | Minimal owned client: queue, batch, transport |
| Certification | Automated conformance for any client impl |
| Schema set hash | Client-declared registry snapshot version |
| Tier-1 events | Playback, fatal errors — no sampling drop |
| WAL | Write-ahead log on client disk |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| One event = one HTTP | Batch math |
| Platform owns all UI tracking | Bottleneck + hybrid |
| Docs-only without cert | PII drift |
| Skip idempotency | Retry duplicates |
| Sync flush on click | UX + perf |

### A7. Reliability test plan

1. Duplicate batch POST → dedupe count stable.
2. Kafka down → client queue grows; no crash; recovers.
3. Schema v14 client against v15 registry → still accepts.
4. Inject email in payload → scrubbed/rejected.
5. Queue cap exceeded → drops DEBUG only.
6. Certification fails on bad client → release gate blocks.

### A8. 60-second summary

> Netflix-scale event logging needs a **schema registry**, **regional ingest** with validate/scrub/dedupe, and **Kafka → stream/batch**. The interview fork is **client ownership**: fully owned SDKs maximize consistency but **don't scale across TV long tail**; docs-only scales teams but risks **schema/PII drift**. Best answer: **hybrid thin platform SDK + codegen + mandatory certification**, protobuf batching, at-least-once with `event_id`, and **heartbeat sampling/aggregation** for 100× cost control.

### A9. Related systems map

```text
Client SDK / Custom Client → Ingest Gateway → Kafka
Schema Registry → Ingest (validation snapshot)
Remote Config → SDK (sampling, endpoints)
Flink → Alerting / RT dashboards
Spark → Warehouse / ML
Identity → profile context enrichment
GDPR Orchestrator → delete pipeline
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Ingest p99 latency | < 50ms |
| Availability | 99.95% |
| Data loss after ACK | < 0.001% |
| Validation error rate (stable apps) | < 0.1% |
| Kafka lag p99 | < 60s |

### A11. Worked ownership example

Registry PR adds optional `bitrate_switch` → codegen stubs → SDK 3.3 optional → Roku docs-only passes cert → ingest accepts v14 and v15 clients.

### A12. Pseudo-SQL for registry metadata

```sql
CREATE TABLE event_types (
  name TEXT NOT NULL,
  version INT NOT NULL,
  compatibility TEXT NOT NULL,
  privacy_class TEXT NOT NULL,
  owner_team TEXT NOT NULL,
  kafka_topic TEXT NOT NULL,
  PRIMARY KEY (name, version)
);
```

### A13. Ownership RACI

| Concern | Platform | App team | Privacy |
|---------|----------|----------|---------|
| Thin SDK | R/A | C | I |
| Custom client | C | R/A | I |
| Schema / PII | C / R | R/A | A |
| Certification | R/A | C | C |

### A14. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Registry, ingest, SDK v1, dedupe |
| 10× | Heartbeat sampling, schema cache |
| 100× | Client aggregation, sidecar for services |
| 1,000× | Binary protocol, edge coalesce |

### A15. Comparison to naive design

| Naive | Why it fails |
|-------|--------------|
| Log4j to file upload | No schema; no central query |
| Per-event REST | 2M QPS impossible |
| Platform monolithic SDK with UI helpers | Release coupling hell |
| Docs-only honor system | Warehouse distrust |
| No client queue | Data loss on flaky mobile |

### A16. On-call cheat sheet

1. Check Kafka lag + ingest 503 rate.
2. Compare validation errors by SDK version vs custom.
3. Schema snapshot stale? bounce cache.
4. Queue drop spike → remote config increase flush or disable DEBUG.
5. pii_reject spike → find offending app version; kill switch event type.

### A17. Sample rejected event response

```json
{"accepted": 48, "deduped": 2, "rejected": [{"event_id": "...", "code": "PII_FORBIDDEN", "field": "email"}]}
```

### A18. Client priority tiers

CRITICAL (playback, fatal) — never drop; STANDARD — drop at 90% queue; DEBUG — drop first.

### A19. Cost worksheet

```text
kafka_storage_TB ≈ daily_events × event_size × retention_days / compress_ratio
ingest_cpu_cores ≈ peak_events × validate_cpu_us / (1e6 × util)
savings_from_heartbeat_sample ≈ heartbeats × (1 - sample_rate)
```

---

*End of document — Netflix system design interview prep: Event Logging Client Ownership vs Docs-Only SDK.*
