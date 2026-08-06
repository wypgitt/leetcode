# System Design: Truck-Tracking Service

> **Focus areas:** High-rate GPS ingest · Geospatial indexing · Geofences · ETA · Pub/sub fan-out · Telemetry durability tiers · Fleet queries · Idempotent updates  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — mobility telemetry / asset tracking at fleet scale (cousin of driver location tracking)  
> **Quality bar:** Separate hot last-known position from history; correct geofence eventing; no OLTP melt from pings

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

Goal: design a **truck-tracking service**—ingest frequent GPS/telemetry from trucks, answer “where is truck X / which trucks near Y”, fire geofence events, support ETA and live maps for dispatchers.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Fleet tracking + geo queries + geofences | Full TMS/WMS ERP |
| Actors | Trucks/devices, dispatchers, optional customers | Rider marketplace matching |
| Data | Location + basic telemetry (speed, heading, fuel?) | Full ELD compliance product (mention) |
| Uber lens | Streaming ingest, geo index, fan-out | Building satellite network |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Who emits locations? | Onboard device / phone app | Device auth, clock skew |
| F2 | Update rate? | 1–5s moving; slower idle | Adaptive sampling |
| F3 | Queries? | Last position; nearby trucks; fleet map | Hot KV + geo index |
| F4 | History? | Breadcrumb trail hours–days | Time-series / cold store |
| F5 | Geofences? | Enter/exit yard, customer site | Event detection |
| F6 | ETA? | To destination / next stop | Routing integration |
| F7 | Live share? | Dispatcher WS/map | Pub/sub |
| F8 | Alerts? | Speeding, offline, geofence | Rules engine |
| F9 | Multi-tenant? | Fleets/orgs | Tenant isolation |
| F10 | Offline device? | Buffer & flush | Gap handling |
| F11 | Route assign? | Optional link to trip | Trip association |
| F12 | Sensors? | Optional temp/door | Extensible telemetry |

**MVP scope:**

1. Authenticated devices upsert location pings idempotently.  
2. Maintain **last known position** + geo index per tenant.  
3. APIs: get truck, query nearby, list fleet viewport.  
4. Short history breadcrumbs (e.g. 72h hot).  
5. Geofence enter/exit events.  
6. Dispatcher live map via pub/sub.  
7. Offline / stale detection.

**Out of MVP:** full route optimization, driver payroll, complete ELD legal suite, video telematics platform.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Ingest p99 | < 100–200ms ACK |
| N2 | Last-pos read p99 | < 50–100ms |
| N3 | Map freshness | Age p95 < 5–15s when moving |
| N4 | Durability | Hot last-pos durable enough; history tiered |
| N5 | Multi-tenant isolation | No cross-fleet leak |
| N6 | Scale | Millions of vehicles class at 1000× |
| N7 | Cost | Downsample history aggressively |

### 1.3 Cases

**Happy:** Truck pings → last pos updates → dispatcher map moves → enters yard geofence → event.  

| Case | Behavior |
|------|----------|
| Burst reconnect flush | Rate-limit; order by device_ts |
| GPS teleport | Sanity filter; flag |
| Duplicate ping | Idempotent `ping_id` / (device, seq) |
| Stale truck | Mark offline after T |
| Hot city viewport query | Tile/cell aggregation |
| Geofence chatter at boundary | Hysteresis / dwell |
| Tenant misconfig fence | Authz on fence ownership |
| Device clock skew | Prefer server receive_time for freshness; keep device_ts |
| Partition of ingest | Buffer locally; backlog drain |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Trucks | 50K | 500K | 5M | 50M |
| Peak pings / s | ~25K | ~250K | ~2.5M | ~25M |
| Tenants / fleets | 500 | 5K | 50K | 500K |
| Geofences | 50K | 500K | 5M | 50M |
| Dispatcher map viewers | 2K | 20K | 200K | 2M |
| History retain hot | 72h | 72h | 48h | 24h + cold |

**Jumps:** 10× shard geo by region; 100× stream bus + tile queries; 1,000× hierarchical indexes, edge ingest, aggressive downsample.

### 1.5 Scope repeat-back

> Multi-tenant truck tracking: high-rate ingest, hot last-known + geo index, breadcrumbs, geofence events with hysteresis, live dispatcher fan-out—scaled by regional shards and telemetry tiering.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Ingest bandwidth

```text
Baseline 25K pings/s × 200 B ≈ 5 MB/s
100×: 2.5M × 200 B ≈ 500 MB/s
1000×: 25M × 200 B ≈ 5 GB/s → edge aggregation / binary proto / delta encoding
```

### 2.2 Storage

```text
Last pos: 50K × 200 B ≈ 10 MB (tiny)
History 72h: 50K trucks × 0.5 Hz avg × 200 B × 72 × 3600 ≈ 1.3e13 B? 
Compute: 5e4 * 0.5 * 200 * 72 * 3600 = 5e4 * 100 * 72 * 3600
= 5e6 * 72 * 3600 = 3.6e8 * 72 = 2.592e10 B ≈ 26 GB
OK at baseline; at 1000× without downsample → tens of PB/day territory—must tier
```

**Unit check:** Always show downsample math in interview.

### 2.3 Query load

```text
Viewport queries every 2s × 2K dispatchers = 1K QPS
Must be cell/tile scans not full fleet scans
```

### 2.4 Bottlenecks

1. Hot geohash cells (ports, cities)  
2. Naive history writes every ping to OLTP  
3. Geofence evaluation O(fences) per ping  
4. Map fan-out storms  
5. Backlog drain after outage  

---

## 3. High-Level Design

### 3.1 Planes / tiers

| Tier | Data | Store |
|------|------|-------|
| Hot last-known | Latest point + status | KV (Redis/Dynamo) |
| Geo index | Cell → truck ids | Memory/Redis per shard |
| Hot history | Recent breadcrumbs | TSDB / Cassandra / S3+index |
| Cold history | Downsampled | Object/columnar |
| Events | Geofence/alerts | Kafka + consumer DB |

**Deal-breaker:** One Postgres table of all pings as only design.

### 3.2 Ingest pipeline

```text
Device → Edge Ingest (auth, validate, dedupe) → Kafka topic (tenant, truck)
  → LastPos Updater
  → Geo Index Updater
  → History Writer (batch)
  → Geofence Evaluator
  → Live Fan-out (truck_id / fleet viewport topics)
```

### 3.3 Idempotency

```text
Key: (truck_id, device_seq) or ping_id
Ignore if seq <= last_applied_seq (per truck)
Allow out-of-order within window with care—usually last-by-device_ts wins for last-pos
```

### 3.4 Geo queries

| Query | Strategy |
|-------|----------|
| Last pos | KV get |
| Nearby | H3 k-ring + filter distance |
| Viewport | Cells covering bbox; return trucks; declutter if dense |
| Fleet list | Indexed by tenant |

### 3.5 Geofencing

| Approach | Pros | Cons |
|----------|------|------|
| Point-in-polygon per ping | Accurate | CPU if many fences |
| Fence cells preindex | Fast candidates | Memory |
| Streaming CEP | Scalable | Complexity |

**Chosen:** Preindex fences to H3 cells; evaluate candidate fences only; **dwell/hysteresis** to avoid chatter.

### 3.6 Trade-offs

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| History | Tiered downsample | Cost | Forever 1Hz hot |
| Live map | Pub/sub deltas | Scale | Poll all trucks SQL |
| Multi-tenant | Shard key tenant+region | Isolation | Shared naked truck_ids |
| Offline | Stale timer | Truthful UX | Assume always online |
| ETA | Routing cache | Accuracy | Haversine-only long haul |

### 3.7 Components

1. Device auth & ingest gateway  
2. Telemetry bus (Kafka)  
3. Last-pos service  
4. Geo index shards  
5. History service  
6. Geofence service  
7. Alerting / rules  
8. Query API  
9. Live map gateway (WS)  
10. Tenant/config (fences, trucks)  
11. ETA/routing adapter  

---

## 4. Architecture Diagram

```text
Truck Devices --> Edge Ingest --> Kafka
                                   |
                 +-----------------+------------------+
                 v                 v                  v
            LastPos KV        Geo Index Shards   History TS
                 |                 |                  |
                 +--------+--------+                  |
                          v                           |
                   Geofence Engine --> Events/Alerts  |
                          |                           |
                          v                           v
                   Live Fan-out -----------------> Query API
                          |
                          v
                   Dispatcher Map WS
```

### 4.1 Ping sequence

```text
ping(seq, lat, lng, speed, device_ts)
  auth → validate jump → dedupe seq
  → update last_pos if device_ts newer
  → move geo cells if needed
  → append history batch
  → evaluate fences → emit ENTER/EXIT
  → publish delta to subscribers
```

### 4.2 Viewport query

```text
bbox → cover cells → mget trucks → filter tenant → optional cluster markers
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Ingest ACK only after durable log (Kafka) or equivalent.  
2. Last-pos updates monotonic per `device_seq` / newer `device_ts` policy.  
3. Tenant authz on every query/subscribe.  
4. Geofence events at-least-once; consumers idempotent on `(truck, fence, transition, period)`.  
5. History can lose fine detail via downsample—**document**—but not last-pos silently.  
6. Stale detection independent of map UI.  
7. Poison pings quarantined.  
8. Backlog drain prioritizes last-pos over full history fidelity.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Kafka + Redis geo + PG trucks; single region |
| 10× | Regional ingest; shard geo by H3 parent |
| 100× | Edge PoPs; history columnar; fence cell index |
| 1000× | Hierarchical declutter; binary telemetry; per-tenant cells |

### 5.3 Maintainability

- Protobuf schema evolution  
- Fence config as data with versioning  
- Replay from Kafka to rebuild last-pos  
- Canary ingest pipeline  

### 5.4 Progressive scale

**1×:** 50K trucks, Redis `GEO`, 72h Cassandra history.  
**10×:** Multi-region fleets; Kafka partitioning by `truck_id`.  
**100×:** Tile map APIs; stream geofence; downsample to 30–60s when idle.  
**1000×:** Edge aggregation (device sends every 1s, edge emits every 5s unless event); massive cold lake.

### 5.5 Adaptive sampling

```text
if speed < v_idle: ping every 30–60s
if speed high or near fence: 1–5s
on heading change > θ: emit early
```

### 5.6 Deal-breakers

| Temptation | Failure |
|------------|---------|
| SQL insert per ping only design | Meltdown |
| Evaluate all fences globally each ping | CPU SEV |
| No tenant checks on WS | Data leak |
| Unlimited history 1Hz | Cost bomb |
| Client-claimed truck_id without auth | Spoofing |

---

## 6. Wrap-Up

### 6.1 Designed

Truck tracking with durable ingest bus, hot last-pos + geo shards, tiered history, cell-accelerated geofences with hysteresis, live dispatcher fan-out, multi-tenant isolation, progressive edge aggregation.

### 6.2 Decisions to defend

1. Tiered storage planes  
2. Kafka as ingest buffer  
3. Seq/idempotent last-pos  
4. H3 geo + viewport cells  
5. Fence preindex + dwell  
6. Adaptive sampling  
7. Authz on subscribe  

### 6.3 Risks

- GPS urban canyons  
- Clock skew  
- Fence misconfig storms  
- Viewer fan-out  
- Regulatory telematics  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope tracking vs full TMS |
| 5–15 | Ingest + last-pos + geo |
| 15–25 | History tiering |
| 25–35 | Geofences + live map |
| 35–45 | Scale, tenants, traps |

### 6.5 Closer

> **Truck tracking:** durable high-rate ingest, hot last-known + geo index, tiered breadcrumbs, smart geofences, pub/sub maps—never let pings write a monolithic OLTP row path.

---

## 7. Deeper / Related Interview Questions

### 7.1 Ordering

**Q: Out-of-order pings?**  
A: Last-pos uses max device_ts with seq guards; history inserts ordered later.

**Q: Exactly-once geofence?**  
A: At-least-once emit; idempotent consumers.

### 7.2 Geo

**Q: Geohash vs H3?**  
A: Either; discuss boundary issues and k-rings.

**Q: Dense port with 10k trucks?**  
A: Server-side clustering for map; don’t send 10k markers every tick.

### 7.3 Geofences

**Q: Boundary flicker?**  
A: Require dwell N seconds / M pings inside before ENTER.

**Q: Huge polygon?**  
A: Simplify; cell cover; bbox reject first.

### 7.4 Multi-tenant

**Q: Noisy neighbor?**  
A: Per-tenant ingest quotas; shuffle shard; separate hot fleets.

### 7.5 ETA

**Q: Where computed?**  
A: Async worker on destination assign; cache routes; refresh on deviation.

### 7.6 Privacy / security

**Q: Customer live link?**  
A: Time-boxed token; obfuscate until near delivery.

### 7.7 Interview traps

| Trap | Pushback |
|------|----------|
| “Just use Firebase” | Fine for MVP toy; not 25M pings/s design |
| Store all in one PG | No |
| No stale state | Lying maps |
| Global pubsub one topic | Won’t scale / authz hard |

### 7.8 Metrics

| Metric | Why |
|--------|-----|
| Ingest lag | Pipeline |
| Ping age p95 | Freshness |
| Offline rate | Device health |
| Fence event rate | Config sanity |
| Viewport p99 | Dispatcher UX |

### 7.9 Uber cousins

Shares DNA with **driver location tracking**; trucks often lower churn, heavier geofence/history needs, multi-tenant fleets.

---

## 8. Appendices

### 8.1 Schemas

```text
ping: {truck_id, tenant_id, seq, lat, lng, speed, heading, device_ts, recv_ts, ping_id}

last_pos KV: truck_id -> {lat,lng,speed,ts,seq,status}

geo: cell_id -> set(truck_id)

geofence: {fence_id, tenant_id, polygon|circle, cells[], dwell_s}

fence_state: (truck_id, fence_id) -> INSIDE|OUTSIDE
```

### 8.2 API checklist

- [ ] `POST /v1/telemetry` (batch)  
- [ ] `GET /v1/trucks/{id}`  
- [ ] `GET /v1/trucks/nearby?lat&lng&r`  
- [ ] `GET /v1/viewport?bbox`  
- [ ] `GET /v1/trucks/{id}/history?from&to`  
- [ ] `POST /v1/geofences`  
- [ ] WS `/v1/fleets/{id}/live`  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Last-known | Hot current position |
| Breadcrumb | Historical points |
| Dwell | Time required before fence transition |
| Declutter | Cluster markers on dense maps |
| Adaptive sampling | Dynamic ping rate |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Kafka, Redis geo, last-pos, basic fences |
| 10× | Region shards, history TS |
| 100× | Tile viewport, dwell, downsample |
| 1000× | Edge aggregate, hierarchical map, cold lake |

### 8.5 Fence eval pseudocode

```text
on_ping(truck, pos):
  cand = fences_for_cells(cell(pos), tenant)
  for f in cand:
    inside = contains(f, pos)
    prev = state[truck,f]
    if inside and prev==OUT and dwell_ok: emit ENTER; state=IN
    if !inside and prev==IN and dwell_ok: emit EXIT; state=OUT
```

### 8.6 Downsample policy

```text
moving: keep ≤1/5s
idle: keep ≤1/60s
always keep: fence transitions, harsh brake events, trip boundaries
```

### 8.7 Interview “say this” (60s)

> Authenticated telemetry into Kafka; update hot last-known and H3 geo indexes; write tiered history with adaptive sampling; evaluate only cell-candidate geofences with dwell; fan out deltas to authorized dispatcher maps—scale with regional shards and edge aggregation.

### 8.8 Reliability tests

1. Replay same seq → no regression.  
2. Teleport ping → rejected/flagged.  
3. Oscillate fence boundary → single ENTER.  
4. Kafka lag → last-pos still recoverable.  
5. Cross-tenant viewport → empty/denied.  

### 8.9 SLOs

| SLO | Target |
|-----|--------|
| Ingest ACK p99 | < 200ms |
| Last-pos age moving p95 | < 15s |
| Viewport p99 | < 300ms |
| Cross-tenant leaks | 0 |

### 8.10 Payload compression

```text
Use delta lat/lng, varints, batch 5–10 pings
1000× without compression fails cost interview
```

### 8.11 Related systems map

```text
Devices → Ingest → Kafka → LastPos/Geo/History/Geofence
                              ↓
                         Live Fan-out → Dispatchers
```

### 8.12 Offline detection

```text
if now - last_recv_ts > T_offline: status=OFFLINE
T depends on expected sampling mode
```

### 8.13 Unit checks

```text
25M pings/s × 200 B = 5 GB/s raw
Edge aggregate 5:1 → 1 GB/s platform ingress
```

### 8.14 Alert examples

| Alert | Rule |
|-------|------|
| Speeding | speed > limit_for_road |
| Offline | stale > T |
| Geofence | ENTER yard late |
| Temp (reefer) | sensor out of band |

### 8.15 Extra traps

| Trap | Pushback |
|------|----------|
| Websocket from each truck to each dispatcher | N×M explosion |
| Polygon check against 5M fences | Preindex |
| History = Redis lists forever | Evict/tier |

### 8.16 ELD / compliance note

Mention hours-of-service may require certified devices & immutable logs—often a specialized subsystem adjacent to tracking.

### 8.17 Security

- Mutual TLS / device certificates  
- Rotate keys  
- Signed location optional  
- PII: driver identity separate from truck telemetry ACLs  

### 8.18 Failure: ingest brownout

```text
Prefer: accept to Kafka local disk
If full: signal devices to buffer & increase sampling interval
Rebuild last-pos from latest per truck on recovery
```

---

---

## Part II — LLD / Object Model

> **Interview use:** After HLD (~25 min), zoom into classes, APIs, and race-safe last-pos updates if interviewer asks for OOD.

### 9.1 Responsibilities

| Class / Service | Owns |
|-----------------|------|
| `TelemetryIngestGateway` | Auth, validate, dedupe, ACK after durable log |
| `Truck` | Identity, tenant, device binding, metadata |
| `LocationPing` | Immutable telemetry event with seq + timestamps |
| `LastPositionStore` | Hot current position per truck; monotonic apply |
| `GeoIndexShard` | Cell → truck membership; move on cell change |
| `HistoryWriter` | Tiered breadcrumb persistence with downsample policy |
| `Geofence` | Polygon/circle definition + precomputed H3 cells |
| `GeofenceEvaluator` | Dwell/hysteresis state machine per (truck, fence) |
| `FleetQueryService` | Last pos, nearby, viewport with tenant authz |
| `LiveMapPublisher` | Pub/sub deltas to authorized subscribers |
| `AlertRuleEngine` | Speeding, offline, sensor thresholds |

### 9.2 Class diagram (ASCII)

```text
<<interface>> TelemetryHandler
     ^
     |
TelemetryIngestGateway --> KafkaProducer
     |
     v
LocationPipeline --> LastPositionStore
                 --> GeoIndexShard
                 --> HistoryWriter
                 --> GeofenceEvaluator --> AlertEmitter
                 --> LiveMapPublisher

FleetQueryService --> LastPositionStore
                    --> GeoIndexShard
                    --> TenantAuthz

GeofenceEvaluator --> GeofenceRepository
                    --> FenceStateStore (truck_id, fence_id) -> INSIDE|OUTSIDE
```

### 9.3 Core interfaces

```text
interface LastPositionStore {
  ApplyResult applyPing(TruckId id, LocationPing ping);  // monotonic by seq/device_ts
  Optional<LastPosition> get(TruckId id);
}

interface GeoIndexShard {
  void move(TruckId id, H3Cell oldCell, H3Cell newCell);
  Set<TruckId> queryRing(H3Cell center, int k, TenantId tenant);
}

interface GeofenceEvaluator {
  List<FenceEvent> onPing(Truck truck, GeoPoint pos, Instant recvTime);
}

class ApplyResult { boolean applied; boolean stale; TruckId id; }
```

### 9.4 Last-pos apply (race-safe)

```text
function applyPing(truck_id, ping):
  loop retry:
    cur = kv.get(truck_id)
    if cur != null and ping.seq <= cur.seq: return STALE
    if cur != null and ping.device_ts < cur.device_ts: return STALE
    new = LastPosition.from(ping)
    if kv.cas(truck_id, cur.version, new): return APPLIED
  // or single-writer partition per truck_id via Kafka key ordering
```

**Invariant:** Last-pos never regresses in `device_seq` / `device_ts` policy.

### 9.5 Geofence state machine

```text
OUTSIDE --(inside N consecutive pings / dwell_s)--> INSIDE  --> emit ENTER
INSIDE  --(outside M consecutive / dwell_s)--------> OUTSIDE --> emit EXIT
```

Chatter at boundary: require `dwell_s` and optional `min_distance` from fence edge.

### 9.6 Viewport query object flow

```text
ViewportQuery(bbox, tenant, zoom)
  -> cells = h3.cover(bbox)
  -> trucks = union(shard.queryCell(c) for c in cells)
  -> filter tenant + staleness
  -> if count > max_markers: ClusterDeclutter.apply(trucks, zoom)
  -> return ViewportResult(markers, clusters, as_of)
```

### 9.7 Extensibility

- `TelemetryDecoder` per device vendor (binary proto plugins)  
- `AlertRule` strategy objects registered by tenant  
- `DownsamplePolicy` per fleet tier (reefer vs dry van)  
- `GeoIndexBackend` interface (Redis GEO vs H3 sets)

### 9.8 Testing strategy

| Test | Assert |
|------|--------|
| Duplicate seq | No last-pos change |
| Out-of-order older ts | Ignored |
| Fence oscillation 1s | Single ENTER after dwell |
| Cross-tenant query | Empty / denied |
| Replay Kafka partition | Rebuild last-pos matches snapshot |

### 9.9 Interview LLD traps

| Trap | Pushback |
|------|----------|
| Mutable ping object shared across threads | Race |
| Geofence eval without candidate prefilter | O(all fences) |
| Last-pos in same row as 72h history | Hot row |
| Subscriber WS without tenant filter | Leak |

### 9.10 Progressive scale (object view)

| Scale | LLD change |
|-------|------------|
| 1× | In-process pipeline OK for demo |
| 10× | Separate consumer groups per stage |
| 100× | `GeoIndexShard` interface + regional impl |
| 1,000× | Edge `TelemetryAggregator` before platform objects |

---

*End of truck-tracking system design.*
