# System Design: Fitness Wearable Heart-Rate Platform

> **Focus areas:** Device telemetry ingestion · Time-series storage · Real-time alerts · FHIR / health hooks · Privacy & consent · Edge buffering · Anomaly detection · Multi-tenant health cloud  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic on samples/sec, split ingest/query/alert planes, explicit PHI/consent boundaries, honest MVP vs clinical-grade claims  
> **Interview theme:** Microsoft — health / wearable in Microsoft ecosystem (Azure, FHIR, compliance); not a toy “store BPM in SQL”

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

Goal: **bound the product**—a cloud platform that ingests **heart-rate (and related vitals)** from fitness wearables, stores time-series efficiently, powers companion apps (live + historical), raises **alerts** on dangerous patterns, and optionally exports/integrates via **FHIR / health ecosystem hooks**—with privacy, consent, and regional compliance first-class.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Wearable HR telemetry platform + alerts + health exports | Full EHR / hospital EMR replacement |
| Device | Consumer wearables + phone gateway | Implanted Class III clinical device FDA dossier |
| Data | Time-series HR, HRV, optional SpO2/steps | Radiology / genomic pipelines |
| Alerts | Threshold + simple anomaly; notify user/contacts | Guaranteed medical diagnosis |
| FHIR | Export / sync Observation & related resources | Complete enterprise FHIR server for all hospital workflows |
| Microsoft lens | Azure IoT/Event Hubs, FHIR service, PHI compliance | Pure academic DSP |

**Scope statement:**

> Design a multi-region-capable fitness wearable heart-rate platform: device→phone→cloud ingestion, durable time-series, real-time streaming views, configurable alerts, companion APIs, and FHIR/health hooks—with consent/PHI controls—from ~10M devices through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | What samples? | HR BPM @ 1Hz continuous; bursts of RR intervals | Time-series + optional high-freq blobs |
| F2 | Path to cloud? | Wearable → BLE → phone app → cloud; some LTE watches direct | Ingest gateways; device auth; offline buffer |
| F3 | Live view? | Companion app sees near-real-time HR | Hot stream path ≠ historical query path |
| F4 | History? | Days→years; charts, zones, resting HR | Downsample tiers; cold storage |
| F5 | Alerts? | High/low HR, sustained tachycardia, irregular pattern flags | Rules engine + notify; not diagnostic claims |
| F6 | Sharing? | User shares with coach/clinician with consent | ACL + audit |
| F7 | FHIR? | Export Observations; webhook to provider FHIR | Mapping layer; consent-gated |
| F8 | Goals/sessions? | Workouts with HR zones | Session service |
| F9 | Multi-device? | Watch + chest strap; user may switch | Device registry; merge policy |
| F10 | Battery/offline? | Buffer on phone/watch; backfill later | Idempotent ingest; out-of-order handling |
| F11 | Admin? | Device fleet health, ingest lag, alert delivery SLOs | Ops dashboards |
| F12 | Identity? | MSA / Entra for users; device attestation | Separate device credentials |

**MVP functional scope:**

1. Register user + device; secure pairing tokens.  
2. Ingest HR samples (batched) with device timestamp + receive timestamp.  
3. Store raw-ish hot tier (e.g. 1Hz) for recent window; downsample for older.  
4. Query APIs: latest, range aggregates, workout session summary.  
5. Alert rules: threshold + sustained duration; push/email notify.  
6. Consent record; basic FHIR Observation export for opted-in users.  
7. Offline backfill with dedupe keys.

**Out of MVP:**

- Guaranteed clinical arrhythmia diagnosis / regulatory clearance claims  
- Full bidirectional EHR write-back for all resources  
- Perfect continuous ECG storage for all users  
- Active-active dual-writer for same user’s raw stream in two regions  
- Social feed of workouts (can be Phase 2)

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Ingest durability | ACK only after durable write (or WAL) |
| N2 | Live lag (device→app) | p50 < 2s, p99 < 10s when online |
| N3 | Query range (24h @ 1Hz) | p99 < 500ms with pre-agg |
| N4 | Alert evaluation latency | p99 < 15–30s from sample time when online |
| N5 | Availability | Ingest 99.9%+; degrade query before dropping ingest |
| N6 | Ordering | Best-effort order; tolerate out-of-order within window |
| N7 | Privacy | PHI encryption; consent; regional residency options |
| N8 | Cost | Downsample aggressively; don’t keep 1Hz forever for all |
| N9 | Scale | See progressive table |
| N10 | Safety messaging | UX must not claim emergency-medical guarantee |

### 1.3 Cases

**Happy paths**

1. Watch samples HR → phone batches every 5–30s → ingest → live socket updates app → stored.  
2. User opens year chart → API reads weekly downsamples → fast render.  
3. HR > 190 for 3 minutes during non-workout → alert → push to user + emergency contact if configured.  
4. Offline hike → phone buffers → backfill → deduped store → sessions recomputed.  
5. Clinician export: user consents → FHIR Observations posted to linked FHIR endpoint.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate batches | Dedupe by `(device_id, sample_ts, metric)` or batch id |
| Clock skew on device | Store device_ts + server_ts; clamp absurd futures |
| Out-of-order samples | Reorder buffer window; late data updates downsample jobs |
| Ingest spike after outage | Backpressure + prioritized live over deep backfill |
| Alert storm (bad sensor) | Per-user / per-device rate limits; sensor quality flags |
| Consent revoked mid-export | Stop export; do not delete provider copies already sent (policy) |
| Device stolen | Revoke device credentials; remote unlink |
| User deletes account | Delete/anonymize PHI per policy; retain de-identified aggregates if allowed |
| FHIR endpoint down | Retry with backoff; DLQ; user-visible sync status |
| Twin devices both sending | Device priority / exclusive active device policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active devices | 10M | 100M | 1B | 10B |
| Online fraction | 20% | 20% | 15–25% | 15–25% |
| HR sample rate | 1 Hz | 1 Hz | 1 Hz | 1 Hz |
| Ingest points / sec (peak) | 2M | 20M | 200M | 2B |
| Batch QPS (20 samples/batch) | 100K | 1M | 10M | 100M |
| Query QPS | 10K | 100K | 1M | 10M |
| Alert evaluations / sec | 2M | 20M | 200M | 2B |
| Alerts fired / day | 1M | 10M | 100M | 1B |
| FHIR export users | 100K | 1M | 10M | 100M |
| Hot storage (7d @ 1Hz) | ~60 TB | ~600 TB | ~6 PB | ~60 PB |
| Cold storage (1y downsampled) | ~50 TB | ~500 TB | ~5 PB | ~50 PB |

**What each jump forces:**

- **10×:** Partitioned event hubs; per-user write affinity; downsample pipeline.  
- **100×:** Tiered TSDB; stream alert workers sharded by `user_id`; edge protocol optimization; regional ingest.  
- **1,000×:** Hierarchical aggregation; device-side downsampling options; cell isolation; selective 1Hz retention policies.

### 1.5 Etc. (Constraints & Assumptions)

- Phone is primary gateway for MVP; direct LTE optional.  
- **Not a medical device guarantee** unless interviewer expands scope—design for consumer + export hooks.  
- Azure-shaped: IoT Hub / Event Hubs, Azure Health Data Services (FHIR), Blob, TSDB/open source (Timescale/Influx/Kusto-like).  
- Consent is **mandatory** before clinician share / FHIR export.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Ingest arithmetic (correctness critical)

```text
10M devices × 20% online × 1 sample/s = 2,000,000 samples/s  (baseline peak)

Sample payload compact binary ~20–40 B (user_key, ts, bpm, quality)
2M/s × 30 B = 60 MB/s  (baseline)
1000×: 2B/s × 30 B = 60 GB/s  → requires regional cells + aggressive batching/downsample at edge
```

**Unit check:** 2e9 × 30 = 6e10 B/s = **60 GB/s**, not TB/s. Still enormous—hence edge downsample & retention policies at 1000×.

### 2.2 Batching effect

```text
Phone sends every 5s with 5 samples (if 1Hz): batch QPS = sample_rate / batch_size
2M samples/s / 20 samples/batch = 100K batch/s  (matches table)
Larger batches reduce QPS but increase live lag—trade-off.
```

### 2.3 Storage tiers

```text
Raw 1Hz for 7 days:
2M samples/s avg-online equivalent continuous estimate carefully:
Better: 10M devices × 86400 s/day × 1 sample × ~25% wear-time × 30 B
= 10e6 × 86400 × 0.25 × 30 ≈ 6.48e12 B/day ≈ 6.5 TB/day raw
7 days ≈ 45–65 TB (order matches table)

1 year keep 1Hz for all → hundreds of TB to PB: DON'T.
Downsample: 1/min avg → 60× reduction; 1/hour for old → more.
```

### 2.4 Alert eval cost

Naive per-sample rule eval at 2M/s is feasible if **stateful stream per user** is sharded and rules are tiny (threshold + duration FSM). ML anomaly on every sample for all users at 1000× is **not** free—sample or tier users.

### 2.5 Query patterns

| Query | Strategy |
|-------|----------|
| Latest HR | Hot KV / stream cache per user |
| Last 1h chart | Hot TS segment |
| Last 1y resting trend | Daily aggregates |
| Workout detail | Session meta + raw window |

### 2.6 Critical bottlenecks

1. **Ingest fan-in** after mass reconnect  
2. **Hot partition users** (influencers sharing live—optional)  
3. **Alert state memory** at huge online counts  
4. **FHIR export storms** (bulk history sync)  
5. **Compaction / downsample lag**  
6. **PHI access audit volume**

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
User, Consent, Device, Credential
Sample(metric, ts, value, quality, device_id)
Session(workout)
AlertRule, AlertEvent
FHIRExportBinding (endpoint, scopes, status)
TimeSeries tiers: raw → 1m → 1h → 1d
```

### 3.2 Options: ingestion bus

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Direct write to SQL | Simple | Melts at 2M pts/s | Any serious fleet |
| B. IoT Hub / Event Hubs → consumers | Backpressure, scale | Ops complexity | — |
| C. Device→object storage only | Cheap | Bad live/alert latency | Live UX required |
| D. Hybrid: stream for hot + batch for backfill | Best | Two paths to unify | Ignoring dedupe across paths |

**Chosen:** **B/D hybrid**—streaming path for online batches; bulk backfill path for deep offline; both land in unified TS writer with idempotency.

### 3.3 Write path invariants

```text
1. Authenticate device/app (mTLS or signed JWT + device attestation)
2. Validate schema + consent flags
3. Durable append to partition keyed by user_id (or device_id→user)
4. ACK client
5. Async: hot cache latest, alert FSM, downsample, FHIR triggers
```

**Deal-breaker:** ACK before durability for “battery saving” without clear loss policy.

### 3.4 Time-series storage options

| Store | Use |
|-------|-----|
| Hot memory/Redis | Latest values, live fanout |
| TSDB (wide events / columnar) | Raw + rollups |
| Object storage | Cold compacted segments / Parquet |
| Kusto-like analytics | Fleet ops, research (de-identified) |

### 3.5 Alerting model

```text
Stateful FSM per (user, rule):
  samples → update rolling state (last values, sustained timers)
  fire → AlertEvent with dedupe key (user, rule, window)
  notify → push channel; respect quiet hours / severity
  escalate → emergency contacts if enabled and confirmed
```

**Quality gate:** suppress if `quality` low or device off-wrist.

### 3.6 FHIR / health hooks

```text
Consent check → map samples/aggregates to FHIR Observation
  code: LOINC 8867-4 (Heart rate) etc.
  subject: Patient (mapped)
  effectiveDateTime / valueQuantity
Push: REST create to Azure Health Data Services / partner FHIR
Or: $export style bulk for historical (rate-limited)
Subscriptions: notify partner on new Observations (Phase 2)
```

**Never** export without consent + purpose limitation recorded.

### 3.7 Privacy & residency

| Control | Mechanism |
|---------|-----------|
| Encryption | TLS + at-rest CMK (Key Vault) |
| Access | User token; caregiver ACL; break-glass audit |
| Residency | Pin user home region cell |
| Minimization | Downsample; delete raw early |
| Audit | Who read PHI when |

### 3.8 Multi-region

| Plane | Mode |
|-------|------|
| Ingest gateway | Regional anycast |
| User TS writes | **Home cell** single-writer |
| Live read | Home or sticky region |
| DR | Async replicate encrypted segments; failover fence |

### 3.9 Microsoft ecosystem fit

- **Azure IoT Hub / Event Hubs / Kafka** for ingest  
- **Azure Health Data Services (FHIR)** for clinical interoperability  
- **Microsoft Cloud for Healthcare** patterns  
- **Entra ID** for clinician/care-team identities  
- **Intune-ish device compliance** analogies for enterprise wellness programs (optional)

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Wearable --BLE-- Phone App --HTTPS batches--> Ingest Edge (regional)
                                      |                │
                                   offline            AuthZ + schema
                                   buffer              │
                                                       ▼
                                              Event Hub / Bus (partition by user)
                                                       │
                     ┌─────────────────────────────────┼──────────────────────────┐
                     ▼                                 ▼                          ▼
               TS Writers                        Alert Workers                 Live Fanout
               (hot+WAL)                         (FSM state)                  (WebPubSub)
                     │                                 │                          │
                     ▼                                 ▼                          ▼
              Hot TSDB / Cache                   Alert Events                  Companion App
                     │                           Notify Svc
                     ▼                                 │
              Downsample / Cold                   FHIR Exporter ← Consent Svc
                     │                                 │
                     ▼                                 ▼
                 Object/Parquet                 FHIR Server / Partner
```

### 4.2 Sample ingest sequence

```text
App → POST /v1/ingest {device_id, batch_id, samples[]}
   → validate sig
   → enqueue partition(user)
   → 202 Accepted (or 200 after sync write—pick; MVP sync small batches)
Writers commit → update latest → alert evaluate → ack path complete
```

### 4.3 Alert sequence

```text
Sample → Alert Worker (owns user shard)
  if rule.breach sustained >= duration && quality.ok
    if not already open alert window
      create AlertEvent
      notify user/contacts
      optional: create FHIR Communication / flag
```

### 4.4 FHIR export sequence

```text
User enables clinical sync → stores Consent + endpoint
Exporter cron/stream:
  new aggregates → Observation bundle → POST FHIR
On failure: retry / DLQ / surface sync error
Revoke consent → stop; audit
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Idempotent ingest

```text
dedupe_key = hash(user_id, device_id, metric, device_ts_ms, value) 
or batch_id uniqueness per device
Retain dedupe bloom/TTL store per partition (e.g. 24–72h)
```

#### 5.1.2 Out-of-order & late data

- Accept late within `L` (e.g. 24–48h) into raw.  
- Rollup jobs **revisable** for affected windows (versioned aggregates).  
- Alerts: generally evaluate near-real-time; optional replay for late critical (product choice—usually don’t re-page hours later).

#### 5.1.3 Backpressure

| Stage | Action |
|-------|--------|
| Edge overload | 429 + client buffer |
| Bus lag | Autoscale writers; shed non-critical fanout |
| Deep backfill | Separate lower-priority topic |

**Priority:** live online batches > alerts > historical backfill > bulk FHIR history.

#### 5.1.4 Failure modes

| Failure | Degradation |
|---------|-------------|
| Alert workers down | Buffer samples; catch-up eval with care to avoid storm |
| TSDB down | Dual-write WAL to object; catch up |
| FHIR down | Local queue; app shows “sync delayed” |
| Region outage | Fail over home cell; brief ingest errors; clients buffer |

#### 5.1.5 Data loss policy (explicit)

- Un-ACKed batches may retry → duplicates OK.  
- ACK after durability → RPO≈0 for accepted data.  
- Device buffer size finite → oldest drop if phone storage full (surface metric).

### 5.2 Scalability

#### 5.2.1 Partitioning

```text
partition_key = user_id  (alerts + TS locality)
ingest cells by region; user home cell affinity
```

Avoid partitioning only by `device_id` if multi-device merge needed—map device→user early.

#### 5.2.2 Downsample pipeline

```text
raw 1Hz (hot 3–7d)
  → 1-min avg/min/max/HRV proxies (hot 90d)
  → 1-hour (1–2y)
  → 1-day (forever / long)
Compaction scheduled; delete raw per policy
```

#### 5.2.3 Alert state memory

```text
Per online user FSM ~100–300 B × rules
10M online × 200 B = 2 GB (fine)
1000×: 1B online → ~200 GB → sharded workers with RocksDB/state store
```

#### 5.2.4 Live fanout

Use Azure Web PubSub / SignalR-like: only for users with active app sessions. Don’t stream raw 1Hz to idle clients—send on subscribe + throttled updates (e.g. 1 Hz max to UI).

#### 5.2.5 Progressive scale

| Scale | Must have |
|-------|-----------|
| 1× | Hub + TSDB + basic rules + push |
| 10× | Downsample tiers; shard workers; dedupe |
| 100× | Regional cells; state stores; export quotas |
| 1000× | Edge downsample policies; hierarchical rollups; cell isolation |

### 5.3 Maintainability

#### 5.3.1 Service boundaries

| Service | Owns |
|---------|------|
| Device registry | Identity, keys, firmware hints |
| Ingest | Auth, validate, bus produce |
| TS store | Durability, query |
| Alerting | Rules FSM, alert events |
| Consent / sharing | Policies |
| FHIR exporter | Mapping + delivery |
| Session | Workout segmentation |

#### 5.3.2 Schema evolution

Metric dictionary versioned; clients negotiate; unknown metrics → quarantine topic.

#### 5.3.3 Observability SLOs

| SLO | Target |
|-----|--------|
| Ingest success | > 99.9% |
| End-to-end live lag p99 | < 10s |
| Alert page lag p99 | < 30s |
| Bus consumer lag | < 60s p99 |
| FHIR delivery success | > 99% (eventual) |

### 5.4 Security, PHI, compliance

- Encrypt samples at rest; field-level for exports.  
- Separate **operational telemetry** (device battery) from **PHI HR**.  
- Audit every caregiver/FHIR read.  
- Threat model: stolen phone token → short-lived creds + revoke; anomalous export detection.  
- Legal: consumer wellness vs medical device—keep claims aligned; store disclaimer metadata for alerts.

### 5.5 Sensor quality & false alerts

```text
quality score from device (perfusion, motion)
off-wrist detection → pause alerts
hysteresis + min duration
per-rule cooldown
user feedback ("I'm fine") → tune
```

### 5.6 Workout sessions

Segment by explicit start/stop or motion+HR heuristics; compute zone minutes from rollups; store session summary independently of raw for cheap history.

### 5.7 Caregiver sharing

ACL: `principal → user_id → scopes (live|history|alerts)` + expiry; all access audited; share links with Entra for clinician tenants when enterprise.

---

## 6. Wrap-Up

### 6.1 What we designed

A **wearable HR platform** with durable batched ingest, tiered time-series, stateful alert FSMs, live fanout for active sessions, consent-gated **FHIR Observation** exports, and regional home cells for PHI—scaled by partitioning on `user_id` and aggressive downsampling.

### 6.2 Key invariants

1. No ACK without durability (or explicit lossy mode).  
2. Idempotent ingest / deduped batches.  
3. Alerts respect quality + consent + rate limits.  
4. FHIR export only with active consent.  
5. Single-writer home cell for a user’s TS.

### 6.3 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| Live vs batch | Hybrid | Lag vs reconnect storms |
| Raw retention | Short + rollups | Cost |
| Alert ML | Tiered | Cost/false positives |
| FHIR sync | Async eventual | Partner reliability |
| Medical claims | Consumer + hooks | Regulatory honesty |

### 6.4 60-second pitch

> Devices buffer and batch HR to regional ingest; we partition by user into a durable stream, write tiered time-series, evaluate lightweight stateful alert rules, and fan out live only to active apps. History reads rollups, not years of 1Hz. Clinical interoperability is consent-gated FHIR Observations to Azure Health Data Services or partners—never as a side effect of raw ingest. At scale: cells, downsample, backpressure, and strict PHI audit.

### 6.5 Risks / follow-ups

- ECG/arrhythmia regulatory path  
- On-device models  
- Multi-metric fusion (SpO2, temp)  
- Population health de-identified analytics governance  

---

## 7. Deeper / Related Interview Questions

### 7.1 Ingest

**Q: Sync or async ACK?**  
A: Small batches can sync-write; at huge scale ACK after broker durability + writer SLO—be explicit about RPO.

**Q: How big should batches be?**  
A: Balance: 5–30s typical; larger saves QPS, hurts live lag.

**Q: Binary vs JSON?**  
A: Binary/protobuf at scale; JSON OK MVP.

**Q: Clock skew?**  
A: Keep both timestamps; reject impossible futures; calibrate.

### 7.2 Storage

**Q: Why not Postgres for all samples?**  
A: Write amplification / storage cost; use TSDB + rollups.

**Q: Can you keep 1Hz forever?**  
A: Economically no for billions of devices; policy per SKU/tier.

**Q: How do rollups handle late data?**  
A: Versioned windows / recompute affected ranges.

### 7.3 Alerts

**Q: Exactly-once alert?**  
A: Dedupe key per window; at-least-once notify with client dedupe.

**Q: Emergency calling 911?**  
A: Usually out of scope; contacts only; legal issues—confirm with interviewer.

**Q: Alert during workout?**  
A: Context-aware thresholds / suppress known high HR zones.

### 7.4 FHIR

**Q: Every sample as Observation?**  
A: No—aggregates or episode summaries; rate-limit; map LOINC codes.

**Q: Patient ID mapping?**  
A: Explicit link with consent; don’t invent MRNs.

**Q: FHIR vs proprietary export?**  
A: Support both; FHIR for clinical; proprietary for coach apps.

### 7.5 Privacy

**Q: Employer wellness program access?**  
A: Separate legal consent; prefer aggregates; careful with coercion ethics—mention.

**Q: GDPR delete?**  
A: Delete PHI tiers; manage FHIR already-sent policy; audit.

### 7.6 Scale

**Q: 2B samples/s?**  
A: Edge downsample, regional cells, shorter raw retention, maybe on-device aggregation.

**Q: Hot celebrity live stream of HR?**  
A: Optional separate fanout product; not default path.

### 7.7 Consistency

**Q: Read-your-writes after ingest?**  
A: Sticky to home cell; return server cursor; app waits for catch-up if needed.

**Q: Multi-device conflicting samples?**  
A: Active device priority; or merge with source tags.

### 7.8 Microsoft-specific

**Q: Azure components?**  
A: IoT Hub/Event Hubs, Functions/AKS consumers, Azure Data Explorer/TSDB, Health Data Services FHIR, Web PubSub, Key Vault, Entra.

**Q: Integration with Microsoft Health / Teams?**  
A: Export connectors + caregiver UX; compliance boundaries.

### 7.9 Comparison

**Q: vs generic IoT telemetry?**  
A: PHI, consent, FHIR, medical-adjacent alert UX, stricter residency.

**Q: vs Apple Health / Google Fit?**  
A: Similar planes; interview focus on cloud ingest/alert/FHIR design.

### 7.10 Reliability drills

1. Kill alert worker → stateful recovery from checkpoint + recent samples.  
2. Duplicate batch replay → no double count.  
3. FHIR 500s → DLQ without blocking ingest.  
4. Mass reconnect → prioritized live topic.

### 7.11 Algorithms

**Q: Sustained tachycardia rule?**  
A: FSM with consecutive/ sample-time duration above threshold; ignore gaps > G.

**Q: Resting HR?**  
A: Daily quantile while low-motion windows.

**Q: Compression?**  
A: Delta + Gorilla-style for TS; page aligned.

### 7.12 Interview traps

| Trap | Pushback |
|------|----------|
| 10M devices × 1Hz = 10M/s without online fraction | Overestimate; still use wear-time |
| Store forever at 1Hz in SQL | Cost/meltdown |
| FHIR export every beat | Partner & cost explosion |
| Claim diagnostic accuracy casually | Regulatory |
| ACK before durable write | Silent loss |
| 2e9 × 30B = 60 TB/s | **60 GB/s** |

### 7.13 UX

**Q: Show “seek medical care”?**  
A: Careful copy; configurable; not a substitute for emergency services.

### 7.14 Research analytics

**Q: Train models on population?**  
A: De-identify, consent, separate analytics environment, ethics review.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- users(user_id, home_region, ...)
-- devices(device_id, user_id, kind, status, pubkey, last_seen)
-- consents(consent_id, user_id, purpose, scopes, created, revoked_at)
-- alert_rules(rule_id, user_id, type, params_json, enabled)
-- alert_events(event_id, user_id, rule_id, severity, ts, state, dedupe_key UNIQUE)
-- sessions(session_id, user_id, start, end, summary_json)
-- fhir_bindings(user_id, endpoint, status, scopes)
-- fhir_delivery(dedupe_key, status, attempts, last_error)

-- TS (conceptual):
-- samples(user_id, ts, metric, value, quality, device_id)
-- rollup_1m(... avg, min, max, count)
```

### 8.2 API checklist

- [ ] `POST /devices` / revoke  
- [ ] `POST /v1/ingest` (batch)  
- [ ] `GET /users/me/metrics/latest`  
- [ ] `GET /users/me/metrics/range?from&to&step`  
- [ ] `CRUD /alert_rules`  
- [ ] `GET /alert_events`  
- [ ] `POST /consents` / revoke  
- [ ] `POST /fhir/bindings`  
- [ ] `GET /sessions`  
- [ ] Caregiver share APIs  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Home cell | Single-writer region for user TS |
| Rollup | Downsampled aggregates |
| FSM alert | Stateful rule evaluation |
| Observation | FHIR resource for measurements |
| Off-wrist | Sensor not reliable |
| Backfill | Offline delayed upload |
| PHI | Protected/personal health info |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Batch ingest, TS store, threshold alerts, push |
| 10× | Dedupe, rollups, sharded alert state |
| 100× | Regional cells, export quotas, quality gates |
| 1000× | Edge aggregation policies, hierarchical TS, isolation |

### 8.5 Metric dictionary (sample)

| Metric | Unit | Rate |
|--------|------|------|
| hr_bpm | beat/min | 1 Hz |
| rr_ms | ms | burst |
| spo2 | % | sparse |
| steps | count | 1/min |

### 8.6 FHIR Observation sketch

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {"coding":[{"system":"http://loinc.org","code":"8867-4"}]},
  "subject": {"reference":"Patient/123"},
  "effectiveDateTime":"2026-08-06T12:00:00Z",
  "valueQuantity":{"value":72,"unit":"beats/minute","system":"http://unitsofmeasure.org","code":"/min"}
}
```

### 8.7 Alert rule examples

| Rule | Params |
|------|--------|
| High HR sustained | bpm>190 for 3m, not in workout |
| Low HR sustained | bpm<40 for 5m, on-wrist |
| Resting HR spike day-over-day | +20 bpm vs baseline |

### 8.8 Ingest protobuf (logical)

```text
Batch { device_id, batch_id, user_id, samples: [Sample] }
Sample { ts_ms, metric_id, value_f32, quality_u8 }
```

### 8.9 Downsample policies by SKU

| Tier | Raw retention | Notes |
|------|---------------|-------|
| Free | 24–72h | 1m forever limited |
| Plus | 7–30d raw | Richer rollups |
| Clinical research opt-in | Longer | Separate consent |

### 8.10 Interview “say this” summary

> Batched durable ingest partitioned by user; tiered TS; stateful alerts; consent-gated FHIR; live fanout only for active sessions; cells + downsample at scale.

### 8.11 Extra traps

| Trap | Pushback |
|------|----------|
| Per-sample HTTP without batching | QPS explosion |
| Single global Kafka partition | Hot spot |
| Alerts without hysteresis | Notification fatigue |
| Mixing ops logs with PHI buckets | Compliance breach |

### 8.12 Reliability test plan

1. Replay same `batch_id` → one store effect.  
2. Reverse-order samples → correct latest + rollups.  
3. Consent revoke during export → stop new sends.  
4. Alert worker restarts → no duplicate open alerts (dedupe).  
5. Downstream FHIR 503 → ingest unaffected.

### 8.13 Observability

| Metric | Why |
|--------|-----|
| samples/sec by region | Capacity |
| consumer lag | Freshness |
| alert_fire_rate | Sensor epidemics |
| fhir_fail_rate | Partner health |
| buffer_drop_rate on clients | Data loss UX |

### 8.14 Related systems map

```text
Device → App buffer → Ingest → Bus → TS / Alerts / Live
                              ↓
                         Consent → FHIR Export
                              ↓
                         Query API → Companion / Caregiver
```

### 8.15 Threat model snapshot

| Threat | Mitigation |
|--------|------------|
| Device spoofing | Attestation + rotating keys |
| Token theft | Short TTL + revoke list |
| Insider read | Least privilege + audit |
| Export abuse | Rate limits + consent scopes |

### 8.16 Capacity cheat-sheet

```text
samples/s ≈ devices × online_frac × wear_frac × rate
batch_qps ≈ samples/s / samples_per_batch
raw_TB/day ≈ samples/day × bytes_per_sample / 1e12
```

### 8.17 Distinct from generic “fitness API”

This design emphasizes **streaming ingest**, **alert FSMs**, **TS tiering**, and **FHIR/PHI**—not just CRUD for runs.

### 8.18 Late-data recompute sketch

```text
on late sample in window W:
  mark rollup W dirty
  recompute from raw if still available else approximate
  do not re-page alerts older than X (policy)
```

### 8.19 Emergency contact flow

```text
Alert severity=CRITICAL → notify user
  if unacked for T and user enabled → notify contacts
  never auto-dial emergency services in MVP
```

### 8.20 Final deal-breakers

1. Unencrypted PHI at rest  
2. FHIR without consent  
3. Single SQL table for all raw samples at fleet scale  
4. Alerting without quality/off-wrist gates  
5. Dual-writer multi-region for same user stream  

---

*End of fitness wearable heart-rate system design.*
