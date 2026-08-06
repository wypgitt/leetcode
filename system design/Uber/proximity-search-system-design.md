# System Design: Proximity Search System

> **Focus areas:** Geospatial index · Radius/k-NN · H3/S2/geohash · Freshness · Pagination · Multi-entity types · City sharding  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — **search entities (drivers, restaurants, POIs) near a lat/lng under latency SLOs**

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

Goal: design a proximity search service that returns nearest entities within radius or top-K by distance for marketplace use cases (drivers, restaurants, chargers, etc.).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Geo nearby queries | Full routing/ETA engine |
| Truth | Entity location index + metadata filters | Raw GPS firehose store |
| Clients | Matching, Eats, maps | Client-side brute force |
| Uber lens | Freshness + filters matter | Academic k-NN only |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Query types? | Radius, top-K, bbox | Unified API |
| F2 | Entities? | Drivers, restaurants, stops | type tag + schema |
| F3 | Filters? | Product, open, rating min | Predicate pushdown |
| F4 | Freshness? | Max age for drivers | TTL exclude stale |
| F5 | Updates? | High-frequency pings | Ingest stream |
| F6 | Pagination? | Cursor for large radius | limit+token |
| F7 | Sort? | Distance; optional score blend | Haversine refine |
| F8 | Multi-city? | Route by geofence | City cells |
| F9 | Consistency? | Eventually consistent index | Seconds lag OK |
| F10 | Auth? | Internal services | mTLS |
| F11 | Delete? | Entity offline removes | Tombstone/TTL |
| F12 | Accuracy? | Refine index candidates | True distance sort |

**MVP functional scope (lock with interviewer):**

1. Ingest entity location updates with type and metadata.
2. H3 (or S2) cell index: entity_id in cell sets.
3. Query: lat/lng + radius → k-ring cells → candidates → filter → distance sort → top K.
4. Freshness cutoff for moving entities.
5. City/geofence routing to shard.
6. Metrics: query latency, candidate set size, stale rate.

**Out of MVP (explicitly defer):**

- Full vector semantic geo
- Global single index without sharding

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Query p99 | Matching loop | < 20–50ms in-region |
| N2 | Update throughput | Driver pings | 100K–1M/s regional |
| N3 | Freshness | Drivers | exclude > 10–30s default |
| N4 | Correctness | No cross-city bleed | Geofence enforced |
| N5 | Availability | Degrade wider ring | Partial results flagged |
| N6 | Scale | See table | Shard by city/H3 parent |
| N7 | Memory | Hot index | Bounded per cell caps |
| N8 | Fairness | No hot cell monopolize CPU | Per-shard limits |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Matcher queries 3km drivers UberX → 40 candidates → top 15 by ETA proxy.
2. Restaurant nearby 2km open_now filter → paginated list.
3. Driver goes offline → removed from index within TTL.
4. Boundary query expands k-ring to avoid missing edge entities.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Hex boundary miss | k-ring + distance refine |
| Hot downtown cell | Cap entities/cell; secondary sort |
| Stale driver included | Freshness filter + metric |
| Huge radius | Reject/limit max radius |
| Duplicate entity ids | Last-write-wins with version |
| Shard wrong city | Geofence redirect |
| Index lag 5s | Acceptable; document EC |
| Poison coordinates | Validate lat/lng bounds |

### 1.4 Scales (Progressive)

| Metric | Baseline city | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Indexed moving entities | 10K | 100K | 1M | 10M |
| Update QPS | 5K | 50K | 500K | 5M |
| Search QPS | 2K | 20K | 200K | 2M |
| Cell count hot | 5K | 50K | 500K | 5M |
| Avg candidates/query | 200 | 300 | 400 | 500 cap |

**What each jump forces:**

- **10×:** Redis/memory sharded index; parent H3 routing
- **100×:** Dedicated search fleets; optional R-tree for static POIs
- **1,000×:** Hierarchical cells; edge cache for popular queries

### 1.5 Etc. (Constraints & Assumptions)

- Design for retries, idempotency, and city/region isolation.
- Fail closed on authz/money; degrade intentionally on non-critical paths.
- Peak ≠ average; stadium/airport spikes are first-class.
- Distance refine on final set; index is approximate retrieval.
- Entity metadata small; heavy fields fetched after ids returned.

**Scope statement:**

> City-sharded geospatial proximity index with streaming updates, filtered radius/top-K queries, freshness gates, and progressive scale to millions of moving entities.

---

## 2. Back-of-the-Envelope Estimation

### Updates

```text
10K drivers × 0.2 Hz ≈ 2K/s; 100× → 200K/s shardable
```

### Query CPU

```text
200 candidates × haversine × 20K QPS → CPU bound; cap K
```

### Memory

```text
1M entities × 100 B index ≈ 100 MB per shard slice
```

### Bottlenecks (rank ordered)

1. Hot cells
2. Oversized k-rings
3. Update/write amp
4. Filter pushdown missing
5. Cross-shard queries at borders

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
GeoEntity
CellIndex
QuerySpec
Candidate
FreshnessPolicy
ShardRouter
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Postgres PostGIS only | Simple | Write/read scale | Ping QPS |
| B. Geohash in Redis | Fast | Boundary pain | OK with care |
| C. H3 cell inverted index | Uber-common | Ops learning | — preferred |
| D. Brute force all online | Correct | O(n) death | Any real city |

**Chosen path:**

- Streaming ingest → **H3 inverted index** per city shard + freshness/version on entity.
- Query: ring expansion until enough candidates or max rings.
- Optional second fetch for display fields.

### 3.3 Core design mechanics

**Update:** `UPSERT entity_id → {cell, lat, lng, ts, tags, version}`; remove on offline/TTL.

**Query:**
```text
cells = h3.kRing(origin, r0)
candidates = union index[cell] for cell in cells
candidates = filter(candidates, predicates, freshness)
ranked = topK by distance(origin, candidates)
return ranked + next_page_token
```

**Invariant:** results ⊆ eligible entities in geofence; stale moving entities excluded by policy.

### 3.4 API sketch

```text
POST /v1/nearby
  {lat, lng, radius_m, type, filters{}, limit, cursor}
GET  /v1/entities/{id}
POST /internal/locations/batch  (ingest)
```

### 3.5 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| H3 vs S2 | Ergonomics vs libs |
| Exact vs approximate | CPU vs recall |
| Sync metadata fetch | Payload size vs round trips |
| Strong vs eventual index | Freshness vs write cost |



---

## 4. Architecture Diagram

```text
Location pings → Ingest → Geo Index (H3 shards per city)
Clients → Proximity API → Shard router → Index query → Refine/sort
Optional Entity Store for fat attributes
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- Idempotent ingest by (entity_id, version).
- Self-heal index from snapshot+log.
- Degrade: shrink K or widen freshness on overload.
- Circuit break hot abusive clients.

**Delivery / consistency cheat-sheet**

| Layer | Guarantee |
|-------|-----------|
| Client → API | At-least-once; idempotency keys where mutations exist |
| System of record | Single-writer per entity / partition key |
| Downstream effects | At-least-once via outbox/stream; idempotent consumers |
| Reads | Read-your-writes on primary; replicas may lag |

**Deal-breakers**

- Global scan per query
- No freshness on drivers
- Cross-city wrong results silently
- Unbounded radius

### 5.2 Scalability

- Partition index by city + H3 parent.
- Coalesce updates per entity (latest wins).
- Separate static POI index if needed.
- CDN not applicable; local memory/redis.

**Progressive evolution**

| Scale | Architecture posture |
|-------|----------------------|
| Baseline | Single region/city; simple durable store + stream |
| 10× | Shard by city/entity; split hot paths |
| 100× | Cells, async fan-out, careful caching, hot-key splits |
| 1,000× | Hierarchical aggregation, edge where safe, strict cost/isolation |

### 5.3 Maintainability

- Index format versioned.
- Replay tool from Kafka.
- Golden queries per city (stadium, airport).

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

- Internal only; rate limits.
- No precise user home leak in logs.

---

## 6. Wrap-Up

**What to say in 60 seconds**

> Proximity search is a sharded H3 inverted index with streaming updates, freshness filters, and distance-refined top-K—built for matcher-scale QPS, not one global scan.

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

### Geo

**Q: Why k-ring?**  
A: Avoid missing hex edge entities.

**Q: PostGIS enough?**  
A: Often not at ping QPS; index in memory/redis.

### Freshness

**Q: Show stale driver?**  
A: Exclude from match; maybe show faded on map product decision.

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

### 8.1 Query example

```json
{"lat":37.77,"lng":-122.41,"radius_m":3000,"type":"driver","filters":{"product":"uberx"}}
```

### 8.2 Complexity

```text
Update: O(1) amortized per entity
Query: O(cells × avg_per_cell + K log K)
```

### 8.3 SLOs

| SLO | Target |
|-----|--------|
| p99 query | <50ms |
| Stale in match results | ~0 |
| Index rebuild | hours RTO |

### 8.4 Related

driver-location-tracking, rider-driver-matching, restaurant feed retrieval

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

*End of proximity search system system design.*

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

### Geospatial index comparison (interview table)

| Index | Query | Update | Boundary |
|-------|-------|--------|----------|
| Geohash | prefix scan | simple | careful 8-neighbor |
| H3 | k-ring | good | hex rings |
| S2 | cap covering | excellent | spherical |
| R-tree | range | moderate | classic GIS |

Pick one; discuss neighbor expansion + true-distance refine.

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

### Geospatial index comparison (interview table)

| Index | Query | Update | Boundary |
|-------|-------|--------|----------|
| Geohash | prefix scan | simple | careful 8-neighbor |
| H3 | k-ring | good | hex rings |
| S2 | cap covering | excellent | spherical |
| R-tree | range | moderate | classic GIS |

Pick one; discuss neighbor expansion + true-distance refine.

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

### Geospatial index comparison (interview table)

| Index | Query | Update | Boundary |
|-------|-------|--------|----------|
| Geohash | prefix scan | simple | careful 8-neighbor |
| H3 | k-ring | good | hex rings |
| S2 | cap covering | excellent | spherical |
| R-tree | range | moderate | classic GIS |

Pick one; discuss neighbor expansion + true-distance refine.

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

### Geospatial index comparison (interview table)

| Index | Query | Update | Boundary |
|-------|-------|--------|----------|
| Geohash | prefix scan | simple | careful 8-neighbor |
| H3 | k-ring | good | hex rings |
| S2 | cap covering | excellent | spherical |
| R-tree | range | moderate | classic GIS |

Pick one; discuss neighbor expansion + true-distance refine.

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

### Geospatial index comparison (interview table)

| Index | Query | Update | Boundary |
|-------|-------|--------|----------|
| Geohash | prefix scan | simple | careful 8-neighbor |
| H3 | k-ring | good | hex rings |
| S2 | cap covering | excellent | spherical |
| R-tree | range | moderate | classic GIS |

Pick one; discuss neighbor expansion + true-distance refine.
