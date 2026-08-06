# System Design: Running / Fitness Application API

> **Focus areas:** Workout ingest · GPS traces · Time-series metrics · Auth · Idempotency · Social/feed hooks · Leaderboards · Privacy · Wearable sync  
> **Style:** Microsoft API-heavy HLD (health/fitness team or Azure Health-adjacent); progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Clear resource model, write-optimized ingest, correct units, privacy of location, split hot telemetry vs cold history  
> **Interview theme:** Design the **API + backend** for a running/fitness app (Strava/Runkeeper-class)—contracts first, infra to back guarantees

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

Goal: **bound a fitness API**—mobile/wearable clients record runs and workouts, upload GPS + metrics, retrieve history and summaries, optionally share activities and compete on segments/leaderboards—with strong auth, idempotent ingest, and location privacy controls.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Fitness **API + storage + query** | Full coaching ML product |
| Ingest | Post-workout upload + optional live stream | Medical-grade device FDA stack |
| Social | Activity feed / kudos Phase 1.5 | Entire Twitter |
| Microsoft lens | Clean REST/Graph-ish API; Azure data plane | Exact Strava clone feature parity |

**Scope statement:** Design APIs for recording and syncing runs/workouts (GPS, HR, splits), history, stats, privacy, and light social—scaled 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Activities? | Run, ride, walk, workout; MVP = run + generic | `sport_type` enum |
| F2 | Ingest mode? | Mostly post-activity upload; live optional | Bulk upload + stream API |
| F3 | GPS? | Lat/lon/elev/time polylines | Compressed trace store |
| F4 | Sensors? | HR, cadence, power optional | Samples time-series |
| F5 | Splits? | km/mi splits auto-computed | Server or client compute + store |
| F6 | History? | List + detail + map | Indexed by user/time |
| F7 | Stats? | Weekly/yearly totals | Aggregates table / rollups |
| F8 | Privacy? | Private / followers / public | ACL on activity |
| F9 | Social? | Feed, kudos, comments Phase 1.5 | Event fanout |
| F10 | Segments / leaderboard? | Phase 1.5–2 | Geo matching + ranks |
| F11 | Wearables? | Apple Watch / Garmin import | Partner ingest + idempotency |
| F12 | Auth? | User accounts; OAuth | Bearer tokens; scopes |
| F13 | Units? | Metric/imperial display | Store SI; format on read |
| F14 | Edit/delete? | Trim, correct sport, delete | Version / soft delete |
| F15 | Goals? | Weekly distance Phase 1.5 | Goals resource |

**MVP scope:**

1. Auth + user profile (units, privacy default).  
2. **Create activity** via multipart/JSON upload (summary + trace).  
3. Idempotent ingest (`Idempotency-Key` / `client_activity_id`).  
4. Get activity detail (summary + decoded polyline + samples summary).  
5. List activities with cursor pagination; filters by time/sport.  
6. Update metadata (title, visibility, sport); delete/trash.  
7. Basic aggregates: distance/time/elevation per week.  
8. Privacy enforcement on every read.  
9. Optional: live session start/stop + point append (degraded polling OK).  
10. Webhooks/partner import stub.

**Out of MVP:** full route builder, training plans, advanced segment racing, medical EHR integration, perfect live race tracking for marathons.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Upload ACK (summary path) | p99 < 500ms in-region (trace async OK) |
| N2 | Large trace finalize | p99 < 2–5s depending on size |
| N3 | List history | p99 < 200ms |
| N4 | Durability | No lost activity after ACK |
| N5 | Consistency | Strong per activity; feed eventual |
| N6 | Availability | High for ingest; degrade social |
| N7 | Privacy | Location never leaked on private |
| N8 | Battery (client) | Batch GPS; compact payloads |
| N9 | Scale | See progressive table |
| N10 | Compliance | Health-ish data care; GDPR delete |

### 1.3 Cases

**Happy**

1. Finish run → phone uploads summary+GPS → detail page with map.  
2. Watch syncs overnight → activities appear idempotently.  
3. User sets private → friends cannot see map.  
4. Weekly dashboard shows distance rollup.  
5. Delete activity → removed from list/aggregates (recompute).

**Edges**

| Case | Behavior |
|------|----------|
| Duplicate upload | Same `client_activity_id` → same activity |
| Partial GPS gaps | Store with gap markers; don’t fake points |
| Clock skew | Prefer GPS time; clamp outliers |
| Huge activity (ultra) | Chunked trace upload; size caps |
| Live disconnect | Buffer on device; flush; session recover |
| Visibility change public→private | Feed retract / ACL deny |
| Cheating GPS teleport | Sanity filters; flag; don’t block ACK lightly |
| Units mismatch | Store meters/seconds; client displays |
| Concurrent edit title | Version / LWW |
| Partner import replay | Idempotent external_id |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 5M | 50M | 500M | 5B |
| Activities / day | 5M | 50M | 500M | 5B |
| Peak creates / s | 200 | 2K | 20K | 200K |
| Avg GPS points / run | 1.5K | 1.5K | 1.2K | 1K |
| Trace bytes / activity | 30–80 KB | 40 KB | 40 KB | 30 KB |
| Read QPS (history) | 5K | 50K | 500K | 5M |
| Live sessions concurrent | 50K | 500K | 5M | 50M |
| Feed fanout events / day | 10M | 100M | 1B | 10B |

**Jumps:** 10× = object store for traces + rollup jobs; 100× = user cells + feed async; 1,000× = geo segment fleet, regional homes, live mesh.

### 1.5 Constraints & assumptions

- Store canonical units: meters, m/s, epoch ms, WGS84.  
- Map tiles are client/SDK concern (MapKit); API returns polyline.  
- Health data sensitivity > typical social posts.  
- Microsoft framing: Azure API Management, Cosmos/SQL, Blob for traces, Entra ID.

**Repeat-back:**

> Fitness API with idempotent activity ingest (GPS + metrics), private-by-default history and rollups, optional live sessions and light social—write-optimized storage and progressive cells.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Ingest volume

```text
5M activities/day ≈ 58/s avg; peak ~10× ⇒ ~600/s
Trace 50 KB × 5M ≈ 250 GB/day raw GPS
Samples (HR 1 Hz × 40 min) ≈ 2400 points → compressible
```

### 2.2 Storage year-1 baseline

```text
5M/day × 365 × 50 KB ≈ 90 TB traces/year
Summaries ~1 KB × 5M/day ≈ 1.8 TB/year
Rollups tiny vs traces
```

### 2.3 Live stream (optional)

```text
50K sessions × 1 point/s × 50 B ≈ 2.5 MB/s ≈ 20 Mbps — easy
At 100×: 2.5 GB/s → sharded live routers + downsample
```

### 2.4 Read patterns

```text
History list: last 20 summaries — cache per user
Detail: 1 summary + 1 polyline fetch
Maps: client decodes polyline; few MB decode local
```

### 2.5 Bottlenecks

(1) Trace write throughput (2) rollup correctness after edits (3) privacy bugs (4) live fanout (5) leaderboard abuse (6) hot celebrity athletes.

---

## 3. High-Level Design

### 3.1 Resource model

```text
User
Profile { units, default_visibility, timezone }
Activity {
  id, user_id, sport_type, start_time, end_time,
  distance_m, elev_gain_m, moving_time_s, elapsed_time_s,
  visibility, title, description,
  trace_ref, stats, device, client_activity_id,
  version, status: PROCESSING|READY|FAILED
}
Trace { activity_id, encoding: FLEX_POLYLINE|GPS_JSON_GZ, blob_key, point_count }
SampleSeries { activity_id, type: hr|cadence|power, blob_key }
LiveSession { id, user_id, started_at, last_seq, status }
Aggregate { user_id, period, sport, distance_m, moving_time_s, elev_m }
```

### 3.2 API surface (MVP)

```http
POST   /v1/activities                 # create + summary; optional trace inline
PUT    /v1/activities/{id}/trace      # chunked / blob complete
GET    /v1/activities/{id}
GET    /v1/users/me/activities?cursor&from&to&sport
PATCH  /v1/activities/{id}            # title, visibility, sport
DELETE /v1/activities/{id}
GET    /v1/users/me/stats?period=week&from&to
POST   /v1/live/sessions
POST   /v1/live/sessions/{id}/points
POST   /v1/live/sessions/{id}/complete
GET    /v1/users/me                   # profile
PATCH  /v1/users/me
```

**Headers:** `Authorization: Bearer`; `Idempotency-Key` on POST create; `If-Match` on PATCH.

**Error model:** `409 CONFLICT`, `413 TRACE_TOO_LARGE`, `422 INVALID_GPS`, `403 FORBIDDEN`, `404` (no leak on private).

### 3.3 Ingest pipelines

**A. Post-workout (primary)**

```text
1. POST /activities {summary, client_activity_id, trace?}
2. If trace small: inline; else return upload URL
3. Persist summary PROCESSING → verify/normalize → READY
4. Enqueue: polyline compress, split compute, rollup update, feed event
```

**B. Live (optional)**

```text
start session → append points (seq) → complete → convert to Activity
```

### 3.4 Service map

| Component | Role |
|-----------|------|
| API Gateway | Auth, rate limit, WAF |
| Activity Service | CRUD, visibility |
| Trace Store | Blob / columnar compressed |
| Ingest Workers | Normalize, splits, sanity |
| Rollup Service | Weekly/yearly aggregates |
| Live Gateway | WebSocket/HTTP append |
| Feed Service (1.5) | Fanout to followers |
| Leaderboard (2) | Segment match + ranks |
| Notification | Optional |
| Privacy / ACL | Central checks |
| Export / Delete | GDPR |

### 3.5 Data stores

| Data | Store | Key |
|------|-------|-----|
| Activity summary | SQL / Cosmos | `activity_id`; index `(user_id, start_time)` |
| Trace bytes | Object store | `traces/{user}/{activity}` |
| Rollups | SQL | `(user_id, period_start, sport)` |
| Idempotency | KV/SQL | `(user_id, idem_key)` |
| Live buffer | Redis | `live:{session}` |
| Feed (1.5) | Fanout store / queue | follower timelines |

### 3.6 Privacy model

```text
visibility: PRIVATE | FOLLOWERS | PUBLIC
PRIVATE: only owner
FOLLOWERS: owner + accepted followers
PUBLIC: anyone (still authz for write)
Map/trace omitted or coarsened for non-authorized (policy)
List endpoints never return private others’ activities
```

**Privacy zones (Phase 1.5):** hide start/end radius (e.g. 200–500m) for public activities.

### 3.7 Stats / rollups

```text
On READY: add distance/time/elev to period buckets
On delete/edit distance: compensating transaction or rebuild from activities
Nightly reconciler for drift
```

### 3.8 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Trace inline vs blob | Hybrid by size | Latency + scale |
| Compute splits | Server async | Consistent definition |
| Live protocol | HTTP append MVP; WS later | Simpler auth |
| Feed | Async eventual | Ingest isolation |
| Leaderboard | Defer | Geo complexity |
| IDs | ULID/UUID | Sortable optional |
| Polyline | Flexible polyline / encoded | Compact |

### 3.9 Progressive architecture

| Scale | Add |
|-------|-----|
| 1× | API + SQL summaries + Blob traces + Redis idempotency |
| 10× | Async workers; rollup tables; CDN for public polys carefully |
| 100× | User cells; feed service; live sharded gateways |
| 1,000× | Regional homes; segment index geo; downsample live; cold tier traces |

---

## 4. Architecture Diagram

### 4.1 HLD

```text
Mobile / Watch
     │
     ▼
┌─────────────┐     ┌──────────────┐
│ API Gateway │────▶│ Activity API │──▶ Summary DB
│ Auth / RL   │     │              │──▶ Idempotency
└─────────────┘     └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        Trace Blob   Ingest Queue   Live GW/Redis
                           │
                           ▼
                 Workers: normalize, splits,
                 rollups, feed events, sanity
```

### 4.2 Create activity sequence

```text
Client          API            DB/Blob         Workers
  |--POST act-->|               |               |
  |             |--insert------>|               |
  |             |--put trace--->|               |
  |             |--enqueue-------------------->|
  |<-201 READY/PROCESSING-------|               |
  |             |               |<--update READY|
```

### 4.3 Cell topology (100×)

```text
owner_id → cell
Cell = Activity API + Summary DB + queues + live shard
Traces in regional blob accounts
Feed cross-cell via events (async)
```

### 4.4 Read path

```text
List: cache key user:activities:cursor → Summary DB
Detail: Summary + authorized Trace fetch (signed URL or proxy small)
Stats: rollup table; fallback scan limited window
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Idempotent create under same user + idem key / client_activity_id.  
2. After READY ACK (or explicit PROCESSING→READY), summary+trace durable.  
3. Private activities never appear in others’ feeds/search.  
4. Rollups eventually match sum of non-deleted activities.  
5. Live complete exactly-once transitions to one activity.  
6. Delete removes authorization to traces (GC).

**Failure handling**

| Failure | Mitigation |
|---------|------------|
| Worker crash mid-process | At-least-once; idempotent handlers |
| Trace put fails | Activity FAILED/retryable; client reupload |
| Rollup drift | Reconciler |
| Live point loss | Client buffer + seq gaps recorded |
| Partial public leak | Authz middleware + integration tests |

**Degraded modes:** accept summary without map; delay feed; disable live; stats approximate banner.

### 5.2 Scalability

**Partition:** `user_id` for summaries, idempotency, rollups, live sessions.

**Trace store:** object storage scales independently; avoid SQL BLOBs at 10×+.

**10×:** async processing; compress polylines; rollups.  
**100×:** cells; feed async; cache lists; rate-limit creates per user.  
**1,000×:** cold storage lifecycle for old traces; segment matching fleet; edge live ingestion; downsample public live maps.

**Hot athletes:** separate read replicas; cache public activities; protect write with fair quotas.

**Backpressure:** 429 on create storms; shed live resolution; never ACK durable write falsely.

### 5.3 Maintainability

- Versioned API `/v1`; additive sport types.  
- Canonical unit tests for distance/splits.  
- Contract tests for privacy matrix.  
- Feature flags: live, feed, privacy-zone, partner import.  
- Clear SLOs: ingest success, processing lag, list latency.  
- LLD: `Activity`, `Trace`, `VisibilityPolicy`, `RollupCalculator`, `LiveSession`.

### 5.4 Security & privacy

- OAuth scopes: `activities:read`, `activities:write`.  
- Field-level redaction for unauthorized (strip trace).  
- Start/end privacy zones for PUBLIC.  
- Export + delete account pipelines.  
- Anti-scraping on public endpoints.  
- Treat GPS as sensitive PII/location data.

### 5.5 Consistency

| Operation | Consistency |
|-----------|-------------|
| Create/get by id | Strong |
| List after create | Read-your-writes (same region) |
| Rollups | Eventual (seconds–minutes) |
| Feed kudos | Eventual |
| Visibility downgrade | Strong deny ASAP; feed retract async |

### 5.6 GPS / data quality

```text
Reject NaN / out-of-range lat lon
Clamp speed teleports (flag, don’t always drop whole activity)
Maxwell elevation optional; prefer barometer if present
Timezone from start_time + user tz for daily buckets
Encode polyline; keep raw optional for pro tier
```

### 5.7 Partner / wearable import

```text
POST /v1/imports/garmin {external_id, payload}
Idempotent on (user_id, provider, external_id)
Map to Activity; mark source=PARTNER
```

### 5.8 Social & leaderboards (evolution)

**Feed:** on PUBLIC/FOLLOWERS READY → event → fanout to follower inboxes (or pull model for MVP).

**Kudos:** counter + who liked; idempotent per user.

**Segments (later):** geofence polyline match offline; leaderboard board per segment with cheat detection; separate service.

---

## 6. Wrap-Up

### 6.1 Summary

Write-optimized **Activity API**: idempotent creates, summaries in DB, traces in blob, async normalize/rollups, privacy-first reads, optional live and social as separate planes.

### 6.2 Trade-offs

1. Inline vs blob traces.  
2. Server vs client splits.  
3. Pull feed vs fanout.  
4. Live WS vs HTTP append.  
5. Eager rollups vs query-time aggregate.

### 6.3 Build order

Auth + create/list/get → trace blob → privacy → rollups → idempotent watch sync → live → feed.

### 6.4 Risks

| Risk | Mitigation |
|------|------------|
| Location leak | Authz tests; redaction |
| Duplicate activities | client_activity_id |
| Rollup wrong after edit | Compensating + reconcile |
| Live cost explosion | Downsample + caps |
| Cheat leaderboards | Defer; then sanity + reports |

### 6.5 Close

> Make ingest idempotent and privacy-correct first; scale traces on object storage and users into cells—social and segments are add-on planes, not blockers for MVP.

---

## 7. Deeper / Related Interview Questions

### 7.1 API design

**Q: PUT vs POST for create?**  
A: POST creates; idempotency key gives PUT-like safety.

**Q: How paginate activities?**  
A: Cursor on `(start_time, id)`; avoid big OFFSET.

**Q: Return 404 or 403 for others’ private?**  
A: Prefer 404 to avoid existence leak (policy choice—be consistent).

### 7.2 Data

**Q: Why not store GPS in Postgres rows per point?**  
A: 1.5K points × millions/day — use compressed blob / columnar.

**Q: How recompute week after delete?**  
A: Compensating decrement or rebuild window.

### 7.3 Scale jumps

**Q: 10×?** Blob traces + workers + rollups.  
**Q: 100×?** Cells + feed + live shards.  
**Q: 1,000×?** Cold tier, geo segments, regional homes.

### 7.4 Microsoft-flavored

**Q: Azure?**  
A: APIM + AKS; Cosmos/SQL; Blob; Functions/workers; SignalR/Web PubSub for live; Entra ID; Monitor.

**Q: Health compliance?**  
A: Not full HIPAA unless declared; still minimize, encrypt, residency, delete.

### 7.5 Traps

| Trap | Better |
|------|--------|
| Design Kafka before resources | API model first |
| Per-point SQL | Compressed traces |
| Public by default | Private default |
| Sync ML coaching in ingest | Async |
| Global leaderboard MVP | Defer segments |
| Float distance recklessly | Integer cm / decimal carefully |

### 7.6 Related

- Wearable heart-rate ingest  
- Notification system  
- Social feed  
- Geo proximity / segments  
- Microsoft Health application

---

## 8. Appendices

## Appendix A — Sample create payload

```json
{
  "client_activity_id": "iphone-7c9f…",
  "sport_type": "RUN",
  "start_time": "2026-08-06T12:00:00Z",
  "end_time": "2026-08-06T12:42:10Z",
  "distance_m": 10002,
  "moving_time_s": 2450,
  "elapsed_time_s": 2530,
  "elev_gain_m": 86,
  "visibility": "PRIVATE",
  "title": "Lunch run",
  "trace": {
    "encoding": "FLEX_POLYLINE",
    "data": "…"
  },
  "device": {"name": "Apple Watch", "os": "watchOS"}
}
```

## Appendix B — Schema sketch

```sql
CREATE TABLE activities (
  activity_id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  client_activity_id TEXT NOT NULL,
  sport_type TEXT NOT NULL,
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  distance_m BIGINT NOT NULL,
  elev_gain_m INT NOT NULL,
  moving_time_s INT NOT NULL,
  elapsed_time_s INT NOT NULL,
  visibility TEXT NOT NULL,
  title TEXT,
  trace_key TEXT,
  status TEXT NOT NULL,
  version INT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, client_activity_id)
);
CREATE INDEX activities_user_start ON activities(user_id, start_time DESC);

CREATE TABLE activity_rollups (
  user_id TEXT NOT NULL,
  period_type TEXT NOT NULL, -- week|year
  period_start DATE NOT NULL,
  sport_type TEXT NOT NULL,
  distance_m BIGINT NOT NULL,
  moving_time_s BIGINT NOT NULL,
  elev_gain_m BIGINT NOT NULL,
  activity_count INT NOT NULL,
  PRIMARY KEY (user_id, period_type, period_start, sport_type)
);

CREATE TABLE ingest_idempotency (
  user_id TEXT NOT NULL,
  idem_key TEXT NOT NULL,
  activity_id UUID NOT NULL,
  response JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, idem_key)
);
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Auth, CRUD, idempotent create, privacy, list/detail |
| 10× | Blob traces, workers, rollups, compression |
| 100× | Cells, feed, live shards, cache |
| 1,000× | Cold tier, segments, regional homes, abuse |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Trace | GPS point sequence |
| Rollup | Pre-aggregated stats |
| Visibility | ACL class of activity |
| Privacy zone | Hide start/end location |
| Live session | In-progress stream |
| Client activity id | Device-stable idempotency |
| Split | Per km/mi pace segment |

## Appendix E — Estimation cheat-sheet

```text
activities/day × trace_bytes ≈ blob growth
peak_create ≈ 5–15 × avg
list_QPS cacheable per user
live_bandwidth ≈ sessions × points/s × bytes/point
```

## Appendix F — State machines

```text
Activity: PROCESSING → READY
                     ↘ FAILED → (retry) → READY
          READY → DELETED
LiveSession: OPEN → COMPLETING → CLOSED
                     ↘ ABANDONED (TTL)
```

## Appendix G — Privacy matrix

| Viewer \ Visibility | PRIVATE | FOLLOWERS | PUBLIC |
|---------------------|---------|-----------|--------|
| Owner | full | full | full |
| Follower | deny | full/coarsened | full/coarsened |
| Stranger | deny | deny | summary+map policy |
| Anonymous | deny | deny | if allowed public read |

## Appendix H — Sanity checks

```text
distance vs integrated GPS distance: warn if >15% mismatch
max speed run: flag if > 12 m/s sustained
time: end >= start; moving <= elapsed
point count caps; simplify Douglas-Peucker server-side optional
```

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Double POST same idem key | One activity |
| Private detail as other user | 404/403 |
| Delete updates rollup | Totals drop |
| Trace unauthorized | No bytes |
| Live complete twice | One activity |
| Visibility public→private | Feed retract |

## Appendix J — Runbook

1. Processing lag → scale workers; priority READY path.  
2. Blob throttling → backoff; regional account.  
3. Privacy incident → disable public list; rotate tokens.  
4. Rollup complaints → run reconciler for user.  
5. Live memory spike → downsample; cap sessions/user.

## Appendix K — Azure mapping

| Concern | Azure |
|---------|-------|
| API | API Management |
| Compute | AKS / Container Apps |
| Summaries | Azure SQL / Cosmos |
| Traces | Blob Storage |
| Live | Web PubSub |
| Queue | Service Bus |
| Identity | Entra ID |
| Monitor | Azure Monitor |

## Appendix L — OpenAPI excerpt (conceptual)

```yaml
paths:
  /v1/activities:
    post:
      parameters:
        - in: header
          name: Idempotency-Key
          required: true
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ActivityCreate'
      responses:
        '201':
          description: Created
        '409':
          description: Conflict / duplicate
```

## Appendix M — Evolution hooks

```text
Training plans & workouts library
Route builder
Segment leaderboards
Clubs / challenges
Coach sharing with consent
HealthKit bidirectional sync
```

---

*End of design doc. Open with resources §3.1 + privacy §3.6; whiteboard ingest §3.3; close with invariants §5.1 and traps §7.5.*
