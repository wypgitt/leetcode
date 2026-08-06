# System Design: Google Maps

> **Focus areas:** Map tiles · Geocoding / reverse geocoding · Routing · Traffic · POI / places · Offline light · Location privacy  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic (tile QPS, graph size, traffic updates), split tile/geo/routing/traffic planes, deal-breakers for “shortest path on full planet graph per request without prep”  
> **Interview theme:** Google L5+ geospatial — DB/index choice (S2/H3, graph partitions), ambiguity over Google internals (no need to recite Exact Earth/Borg)

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

Goal: **bound the product**—a **Google Maps–class** system: render maps (tiles/vector), convert addresses ↔ coordinates, find routes with live traffic, search places (POI), with light offline and strong **location privacy** constraints.

### 1.0 What this is / is not

| Dimension | **Google Maps (this doc)** | Not this |
|-----------|----------------------------|----------|
| Primary job | Tiles + geocode + route + traffic + POI | Full Street View capture fleet ops |
| Success | Fast map pan/zoom, accurate routes, fresh traffic | Perfect 3D photogrammetry MVP |
| Read path | CDN tiles / vector; cached routes | Recompute world graph naively each request |
| Write path | Traffic probes, edits, POI updates | User social check-in network |
| Privacy | Minimize location retention/leakage | Store raw GPS forever by default |
| Offline | Pack region bundles light | Full offline Earth on phone MVP |

**Scope statement:** Design Google Maps covering tile serving, geocoding, routing, traffic, POI search, light offline, and location privacy—at progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Map rendering? | Raster tiles and/or vector tiles | Tile pyramid + CDN; vector preferred modern |
| F2 | Geocoding? | Address → lat/lng; reverse too | Geo index + postal normalization |
| F3 | Routing? | Driving MVP; walk/transit Phase 1.5 | Road graph + weights; multimodal later |
| F4 | Alternatives? | 1–3 alternate routes | Yen/k-shortest or diverse paths |
| F5 | Traffic? | Live ETAs using probe/speed data | Real-time edge weights; historical priors |
| F6 | POI / Places? | Search “coffee near me”; details | Spatial index + text search |
| F7 | Navigation? | Turn-by-turn guidance | Route polyline + maneuver list; reroute |
| F8 | Offline? | Download city/region pack | Bundles; update diffs |
| F9 | User location? | Blue dot; optional share ETA | Privacy tiers; ephemeral |
| F10 | Edits? | Report closure / wrong POI | Moderation queue; trust |
| F11 | SDKs? | Mobile + web maps SDK | Same backends; quota keys |
| F12 | Autonomy HD maps? | Out of MVP | Mention only |

**MVP functional scope:**

1. **Serve map tiles** (vector MVP; raster fallback) via CDN for zoom/pan.  
2. **Geocode** and **reverse geocode** with ranked candidates.  
3. **Route** A→B driving with ETA; 1–2 alternatives.  
4. Ingest **traffic** speed samples; update edge costs; refresh ETAs.  
5. **POI search** near a point / viewport; place details.  
6. **Reroute** on deviation / closure.  
7. **Light offline**: download region pack (roads + basic tiles/POI).  
8. **Location privacy**: retention limits, coarse modes, consent.  
9. Client SDKs call rate-limited APIs with API keys.

**Out of MVP:**

- Full transit GTFS worldwide perfection  
- Indoor maps / AR walking  
- Street View imagery pipeline  
- Ride-hailing marketplace  
- Fully offline planet  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Tile latency | Instant pan/zoom | p99 < 50–100ms CDN warm |
| N2 | Geocode latency | Typeahead feel | p99 < 100–200ms |
| N3 | Route latency | Snappy directions | p99 < 200–500ms typical city; bound hard cases |
| N4 | Traffic freshness | Useful ETAs | Edge speeds age < 1–5 min hot roads |
| N5 | Availability | Critical consumer | 99.9%+ tiles via CDN; degrade traffic |
| N6 | Privacy | Minimize PII location | TTL, aggregation, purpose limitation |
| N7 | Correctness | Legal/road rules matter | Graph versioning; known hazards |
| N8 | Multi-region | Global users | Geo-partitioned graphs + global tile CDN |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User pans map → vector tiles from CDN → render client-side.  
2. Types address → geocode suggestions → select → camera flies to lat/lng.  
3. Directions A→B → route service returns polyline + ETA with traffic.  
4. Probe fleet / phones contribute speeds → traffic job updates edges → ETAs improve.  
5. Search “pharmacy open now” near me → POI ranker → pins.  
6. Enter tunnel / go offline with pack → basic navigation continues.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Ambiguous address | Return candidates with confidence; don’t pick silently if low |
| One-way / turn restriction | Graph constraints in router |
| Road closure | Dynamic overlay; invalidate routes; push reroute |
| Sparse traffic rural | Fall back to historical / free-flow speeds |
| Cross-continent route | Hierarchical routing / contraction hierarchies |
| Tile stampede new zoom | CDN + immutable versioned tiles |
| Location spoofing | Don’t trust client for privileged ops; sanity checks |
| Privacy: stalkerware risk | No ambient precise history without consent |
| Graph update mid-nav | Sticky graph version per session or careful patch |
| Mega-event traffic | Spike updates; prioritize arterials |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 100M | 1B | global | global peak |
| Tile requests/s | 2M | 20M | 200M | edge-local |
| Geocode QPS | 50K | 500K | 5M | 50M |
| Route QPS | 20K | 200K | 2M | 20M |
| Traffic samples/s | 500K | 5M | 50M | 500M |
| Road graph edges | 1B order | — | planet+ | HD layers |
| POI count | 200M | 500M+ | 1B+ | dense indoor |
| Offline packs served/day | 1M | 10M | 100M | — |
| Graph partitions (cells) | 100 | 500 | 5K | fine S2 |

**What each jump forces:**

- **10×:** Vector tiles; geocode cache; CH/HL routing prep; traffic sketch aggregates.  
- **100×:** Regional routing cells; hierarchical long routes; traffic by corridor; POI sharded.  
- **1,000×:** Fine geo cells; predictive traffic; edge compute for local reroute; differential offline.

### 1.5 Etc. (Constraints & Assumptions)

- Map data comes from a **basemap pipeline** (imagery, government, partners, user edits)—we consume versioned graphs/tiles.  
- Prefer **S2/H3-style cells** as partition vocabulary without requiring Google-internal names.  
- Navigation accuracy has safety implications — degrade gracefully, never silent wrong-way.

**Scope statement to repeat back:**

> Design a Maps system that serves versioned map tiles, geocodes addresses, computes traffic-aware routes on a partitioned road graph, updates speeds from probes, searches POIs, supports light offline packs, and treats location data as sensitive—with progressive scale via CDN tiles, hierarchical routing, and geo-partitioned traffic.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Tiles** | z/x/y or vector | ~2M QPS | CDN |
| **Geocode** | forward/reverse | ~50K QPS | Search + cache |
| **Route** | A→B compute | ~20K QPS | Graph servers |
| **Traffic ingest** | speed samples | ~500K/s | Stream agg |
| **POI search** | near/text | ~30K QPS | Spatial+text |
| **Location ping** | nav session | bursty | Ephemeral / agg |
| **Basemap publish** | tile/graph build | batch | Offline pipeline |

**Anti-pattern:** one QPS for “Maps” mixing pan tiles and Dijkstra.

### 2.2 Tile math

```text
Viewport ~ 20–40 tiles on move; user pans → burst
Vector tiles: ~50–200 KB each compressed at mid zooms (varies)
2M tile QPS × 100 KB = 200 GB/s = 1.6 Tbps — CDN problem, not origin
Origin: versioned immutable tiles; hit ratio 99%+
Zoom 0–21 pyramid; most traffic mid zooms in cities
```

### 2.3 Graph & routing math

```text
Planet roads: hundreds of millions to ~1B+ directed edges (order)
Dijkstra on full planet per request = DEAL-BREAKER
Need: contraction hierarchies / hub labels / A* + partitions
City route: explore << 1M edges with CH → milliseconds
Cross-country: hierarchical long-distance backbone
```

### 2.4 Traffic math

```text
500K samples/s × 50B = 25 MB/s ingest — easy for Kafka
Unique edges touched/min: << all edges; focus on active roads
Aggregate to edge_id speed EMA every 30–60s
Publish traffic deltas to routing cells; clients get ETA refresh
```

### 2.5 Geocode / POI

```text
Geocode: normalized query → candidates from inverted index + geo
Cache top queries (“Statue of Liberty”) at edge
POI: geohash/S2 cell → posting lists; intersect with text
200M POI × 1 KB = 200 GB — sharded spatial DB + search index
```

### 2.6 Offline packs

```text
City pack: vector + graph + POI subset ≈ 100 MB–1 GB
1M downloads/day × 300 MB = 300 TB/day egress — CDN + differential updates
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `GET /tiles/v/{version}/{z}/{x}/{y}.mvt` | Vector tile |
| `GET /geocode?q=` | Forward geocode candidates |
| `GET /geocode/reverse?lat=&lng=` | Reverse |
| `POST /directions` | `{origin, destination, mode, options}` → routes |
| `POST /directions/reroute` | Updated position + remaining destination |
| `GET /traffic/viewport` or embed in route | Speeds / incidents |
| `GET /places/search` | Text + location bias |
| `GET /places/{id}` | Details |
| `POST /offline/packs` | Manifest for region download |
| `POST /probes` (internal/SDK) | Aggregated speed contributions |

### 3.2 Data model

| Entity | Key | Store | Notes |
|--------|-----|-------|-------|
| Tile | `(version,z,x,y)` | Object + CDN | Immutable |
| RoadGraph | `graph_version` + `partition` | Graph store / mmapped | Nodes/edges/attrs |
| EdgeTraffic | `edge_id` | Redis/Bigtable | speed, confidence, ts |
| Place / POI | `place_id` | SQL + search index | geo, categories, hours |
| AddressDoc | normalized | Search index | geocode |
| Incident | `incident_id` | SQL + pub | closure, accident |
| OfflinePack | `region_id, pack_ver` | Object CDN | bundle |
| PrivacyBudget | `user/device` | policy | retention |

### 3.3 Spatial indexing — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Lat/lng bounding box SQL** | Simple | Poor scale | Toys |
| **Geohash prefixes** | Easy; Redis-friendly | Edge distortion | MVP POI |
| **S2 / H3 cells** | Uniform hierarchy | Learning curve | **Chosen** |
| **R-tree** | Classic GIS | Harder distributed | Single-node GIS |
| **Quadtree tiles** | Natural for maps | — | Tile pyramid itself |

**Chosen:** S2/H3 for POI + traffic partitions; XYZ/quad for tiles.

### 3.4 Routing algorithms — Why X over Y

| Approach | Pros | Cons | Deal-breaker? |
|----------|------|------|---------------|
| Dijkstra each request planet | Correct | Too slow | **Yes at scale** |
| A* Euclidean | Better | Still heavy long-haul | Assist only |
| **Contraction Hierarchies (CH)** | Fast prep queries | Prep cost; dynamic traffic harder | **Strong pick** |
| Customizable CH / CRP | Traffic-friendly | Complex | **100× pick** |
| Hub labels | Ultra fast | Memory | Regional |
| ML ETA only without graph | — | Illegal turns | Deal-breaker alone |

**Chosen MVP:** CH or CRP per region + live weight overlays; hierarchical stitching for long routes.

### 3.5 Traffic — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| Per-probe update every edge live | Fresh | Noise / cost |
| **Aggregate EMA / sketches per edge** | Stable | Lag |
| Historical profiles by TOD | Cold start | Misses incidents |
| Incident-first + speeds | Practical | Need both |

**Chosen:** Historical prior + real-time EMA on active edges + incident overlays.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Tile delivery | CDN immutable versions | QPS | Origin render per request |
| Vector vs raster | Vector MVP | Style/offline/size | Raster-only forever |
| Routing prep | CH/CRP partitions | Latency | Naive Dijkstra world |
| Traffic | Aggregates not raw GPS store | Privacy+scale | Keep precise traces forever |
| POI | S2 + text index | Geo queries | Table scan |
| Offline | Region packs + diffs | Size | Full planet download |
| Privacy | Purpose-limited aggregation | Safety/trust | Raw breadcrumb DB default |

**DB choice note:**  
- **Object store + CDN:** tiles, offline packs.  
- **Memory-mapped graph shards:** routing hot path.  
- **Bigtable/Cassandra-like:** traffic time series by edge.  
- **Search (inverted + geo):** geocode & places.  
- **Distributed SQL:** place canonical records, incidents, entitlements.

---

## 4. Architecture Diagram

```text
                    +------------------+
   Map SDKs ------> | API Gateway      |---- rate limits / API keys
                    +--------+---------+
          +---------+--------+--------+----------+
          |         |        |        |          |
          v         v        v        v          v
     Tile CDN   Geocode   Directions  Places   Offline
     (vector)   Service   Service     Search   Manifest
          ^         ^        ^        ^
          |         |        |        |
     Tile Build   Address   Road      POI
     Pipeline     Index     Graph     Index
                             ^
                             | weights
                      +------+-------+
                      | Traffic Agg  |<-- probe samples (Kafka)
                      | + Incidents  |
                      +--------------+

 Privacy / Loc Policy  --->  scrub, aggregate, TTL on any location path
```

**Tile path:**

```text
Basemap build -> vector tiles version V -> object store -> CDN
Client: GET /tiles/v/V/z/x/y.mvt -> render
```

**Directions path:**

```text
POST /directions {A,B}
  -> snap A,B to graph
  -> pick partitions
  -> CH/CRP query with traffic weights
  -> alternatives
  -> return polyline, maneuvers, ETA, graph_version
```

**Traffic path:**

```text
SDK probes (coarse/aggregated) -> Kafka
  -> map-match to edges
  -> EMA update EdgeTraffic
  -> publish deltas to routing cells
  -> optional viewport traffic tiles
```

**Geocode path:**

```text
query normalize -> retrieve candidates (text+geo) -> rank -> respond
reverse: S2 cell -> nearby address docs -> rank by distance+hierarchy
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Tile immutability** per version; clients pin `V` or negotiate.  
2. **Route uses consistent graph_version** (+ traffic snapshot epoch).  
3. **Never invent turn against hard restriction** without flagging.  
4. **Traffic degrade ≠ wrong graph** — fall back free-flow.  
5. **Location data purpose-limited**; retention enforced.  
6. **Incidents** can override speeds (closure → infinite cost / blocked).

#### 5.1.2 Map-matching probes

```text
raw points noisy
  -> HMM / geometric map-match to edge
  -> derive speed
  -> discard low-confidence
  -> aggregate
Wrong match => bad traffic; confidence thresholds mandatory
```

#### 5.1.3 Routing failures

| Case | Behavior |
|------|----------|
| No path | Explicit unreachable; suggest mode change |
| Timeout hard instance | Hierarchical fallback; simpler cost |
| Stale traffic | Use prior; mark ETA confidence low |
| Mid-nav graph publish | Sticky version until reroute |

#### 5.1.4 Privacy reliability (product correctness)

- Default: **no long-term precise trail** for Maps core features.  
- Navigation: ephemeral session location on device; server sees what is needed for traffic contribution **aggregated**.  
- Shared ETA: explicit consent; short TTL link.  
- Logs: scrub/precision reduce (lat/lng quantization).

**Deal-breaker:** designing a forever GPS breadcrumb warehouse as the core traffic system without aggregation.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Hot city tile origin | CDN |
| 10× | Route CPU | CH prep; cache popular OD |
| 100× | Traffic ingest skew | Geo partition Kafka; arterial priority |
| 1,000× | Graph publish global | Staged cell rollout; canary cities |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| Tile `(z,x,y)` | Natural CDN key |
| S2 cell | POI, traffic, graph shards |
| Graph partition | Routing locality |
| `place_id` hash | Details store |
| Time-of-day bucket | Historical traffic |

#### 5.2.2 Hierarchical routing

```text
Local: CH inside metro partition
Long: route to border hubs -> backbone network -> destination partition
Stitch paths; refine
Alternatives: penalize overlap with primary (diversity)
```

#### 5.2.3 Dynamic traffic on CH

Challenge: CH prep assumes static weights.

Approaches:

1. **Customizable Route Planning (CRP)** / metric-independent prep — strong interview answer.  
2. Periodic CH rebuild from base + slow-changing weights; overlay short-term penalties for incidents.  
3. A* with landmarks + live weights for local reroute only.

**MVP story:** regional CRP/CH with traffic **multipliers** refreshed frequently on active edges; full rebuild daily.

#### 5.2.4 Tile & vector scale

- Style separate from geometry (client style).  
- Delta updates for offline packs.  
- Overzoom / underzoom client tricks to cut QPS.

#### 5.2.5 POI search

```text
Retrieve:
  text posting list (coffee)
  ∩ S2 covering(viewport/near)
Filter: open_now, category
Rank: distance, prominence, relevance, quality
```

#### 5.2.6 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Vector CDN; geocode cache; CH; traffic EMA |
| →100× | Routing cells; CRP; incident bus; POI shards |
| →1,000× | Predictive traffic; edge reroute; fine cells; pack diffs |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
graph_version: 2026.08.05.1
tile_version: 2026.08.05.1
routing:
  algo: crp
  alternatives: 2
traffic:
  ema_half_life_s: 120
  min_confidence: 0.4
privacy:
  probe_quantize_m: 50
  retain_raw_days: 0
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `tile_cdn_hit_ratio` | Cost |
| `geocode_p99` / zero-result rate | UX |
| `route_p99` / fail_rate | Core |
| `traffic_edge_freshness` | ETA quality |
| `map_match_confidence` | Probe quality |
| `reroute_rate` | Nav quality |
| `privacy_scrub_errors` | Compliance |

#### 5.3.3 Testing

- Golden routes (known OD → path constraints).  
- Turn restriction unit tests.  
- Traffic incident injection → ETA/block.  
- Geocode ambiguity suites per country.  
- Privacy: assert no raw precise storage in traffic path.

#### 5.3.4 Operability

- Canary graph version per city.  
- Dual-run ETA models.  
- Feature flags for alternate generators.  
- Rollback tile version via client config.

---

## 6. Wrap-Up

### 6.1 What we designed

A **Maps** platform: CDN-delivered versioned **vector tiles**, **geocoding**, **traffic-aware routing** on partitioned graphs with CH/CRP-style prep, **POI** spatial+text search, **light offline packs**, and **privacy-preserving** traffic aggregation—not naive Dijkstra on the planet and not a raw GPS warehouse.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Per-request planet Dijkstra | Deal-breaker |
| Tiles at origin | Deal-breaker |
| Vector tiles | Preferred MVP |
| Traffic | Aggregate + historical + incidents |
| Privacy | Quantize/TTL/aggregate |
| Long routes | Hierarchical stitch |
| Offline | Region packs not planet |

### 6.3 30-second scale narrative

> Baseline: CDN tiles, geocode index, regional CH routing, Kafka traffic EMA. 10× adds caches and stronger prep. 100× splits routing/traffic cells with CRP and incidents. 1,000× pushes predictive traffic, fine geo cells, and differential offline—privacy stays aggregation-first.

### 6.4 Deal-breakers checklist

- Shortest path on full planet graph per request without preprocessing.  
- Rendering map images on app servers per pan.  
- Storing forever precise user GPS as the traffic design.  
- Ignoring turn restrictions / one-ways.  
- Single global mutable graph file with no versions.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Raster or vector?**  
A: Prefer vector for modern Maps; raster for simple MVP/legacy.

**Q2: Which modes?**  
A: Lock driving first; walk easy; transit needs GTFS schedules.

**Q3: Real-time navigation?**  
A: Yes → reroute, snapping, guidance maneuvers.

**Q4: Offline depth?**  
A: City packs MVP; clarify size budget.

**Q5: User-generated edits?**  
A: Trust + moderation; don’t let vandalism close highways instantly without corroboration.

### 7.2 Tiles

**Q6: What is a tile pyramid?**  
A: Zoom levels; each z subdivides; XYZ addressing.

**Q7: Why immutable versioned tiles?**  
A: CDN cache forever; rollback by version pointer.

**Q8: Vector tile contents?**  
A: Layers: roads, buildings, labels, water — client styles.

**Q9: How to reduce tile QPS?**  
A: Client cache, overzoom, HTTP cache headers, HTTP/2.

**Q10: Earth curvature / projection?**  
A: Web Mercator common; mention polar distortion.

### 7.3 Geocoding

**Q11: Forward vs reverse?**  
A: Address→coords vs coords→address.

**Q12: Why hard internationally?**  
A: Format variance, missing numbers, language, political names.

**Q13: Autocomplete architecture?**  
A: Prefix index + popularity + distance bias; heavy cache.

**Q14: Ambiguity?**  
A: Return n-best with scores; UI disambiguates.

**Q15: Rooftop vs centroid accuracy?**  
A: Store geometry quality; navigation may want access point / curb.

### 7.4 Routing

**Q16: Why not Dijkstra?**  
A: Too slow at continent scale; prep indexes.

**Q17: Explain CH intuitively?**  
A: Pre-contract unimportant nodes; queries jump shortcuts.

**Q18: How does traffic break CH?**  
A: Weights change → need CRP/customizable or frequent rebuild + overlays.

**Q19: Alternatives that aren’t clones?**  
A: Diversify by penalizing shared edges; optimize different cost (time vs distance).

**Q20: Snap to road?**  
A: Map-match GPS to graph before route/reroute.

**Q21: Turn costs?**  
A: Edge-based or expansion graphs with turn restrictions as first-class.

### 7.5 Traffic

**Q22: Probe sources?**  
A: Opt-in navigation users, partner fleets — aggregated.

**Q23: Cold roads?**  
A: Historical TOD profiles; free-flow defaults.

**Q24: Incidents vs speeds?**  
A: Closures binary block; speeds continuous; both needed.

**Q25: How fast must traffic update?**  
A: Minutes for arteries; slower OK residential.

**Q26: Privacy-preserving traffic?**  
A: On-device aggregate, quantize, k-anonymity thresholds before emit.

### 7.6 POI

**Q27: place_id stability?**  
A: Canonical IDs; merges/splits hard — alias table.

**Q28: Ranking “near me”?**  
A: Distance × prominence × relevance × open-now × quality.

**Q29: Duplicate POIs?**  
A: Entity resolution (name+geo+phone); cluster.

**Q30: Hours / popular times?**  
A: Structured fields + optional visit aggregates (privacy careful).

### 7.7 Offline & mobile

**Q31: What’s in an offline pack?**  
A: Vector tiles subset, graph, critical POI, locale.

**Q32: Updates?**  
A: Differential packs; version manifests.

**Q33: Offline routing freshness?**  
A: Stale traffic OK; closures may miss — warn user.

**Q34: Battery?**  
A: Duty-cycle GNSS; sensor fusion; fewer server pings.

### 7.8 Privacy & safety

**Q35: Precise location retention?**  
A: Avoid by default; document purposes; TTLs.

**Q36: Shared live location?**  
A: Explicit session; stop time; access control.

**Q37: Law enforcement requests?**  
A: Policy/legal process — design minimization so less exists.

**Q38: Spoofed GPS?**  
A: Don’t grant privileges from location alone; sanity vs road network.

### 7.9 Data stores & partitioning

**Q39: Why S2/H3?**  
A: Hierarchical cells for geo fanout and sharding.

**Q40: Graph storage format?**  
A: Compact binary adjacency; memory-map per partition.

**Q41: Spanner for edges?**  
A: Wrong for hot routing scans; OK for POI canonical / incidents.

**Q42: How to publish new graph?**  
A: Blue/green versions; cell canaries; sticky sessions.

### 7.10 Estimation drills

**Q43: Tile egress 10M QPS × 80 KB?**  
A: 800 GB/s ≈ 6.4 Tbps — CDN.

**Q44: Can you Dijkstra 1B edges in 100ms?**  
A: No in general — argue prep.

**Q45: Traffic state memory for 1B edges × 8B?**  
A: ~8 GB if dense — but sparse active set much smaller; still partition.

### 7.11 Alternatives & deal-breakers

**Q46: Only Google Polyline + static ETAs?**  
A: Insufficient without graph constraints & live traffic.

**Q47: Client-only routing with OSM file?**  
A: Works offline small regions; not global live traffic product alone.

**Q48: Render maps via screenshots API?**  
A: Latency/cost deal-breaker vs tiles.

### 7.12 Interview craft

**Q49: How to open?**  
A: Clarify tiles/geocode/route/traffic/POI/offline/privacy — then planes.

**Q50: What impresses L5+?**  
A: CH/CRP vs Dijkstra, traffic vs privacy, versioned tiles/graphs, hierarchical long routes, deal-breakers.

**Q51: Common mistake?**  
A: Deep map-reduce lore; no mention of turn restrictions or CDN tiles.

---

### Appendix A — XYZ tile addressing

```text
z zoom, x column, y row
children of (z,x,y): (z+1, 2x, 2y) ... four children
```

### Appendix B — Directions request/response

```json
{
  "origin": {"lat": 37.4, "lng": -122.1},
  "destination": {"lat": 37.8, "lng": -122.4},
  "mode": "drive",
  "alternatives": true
}
```

```json
{
  "graph_version": "2026.08.05.1",
  "traffic_epoch": 1710000000,
  "routes": [
    {
      "eta_s": 2140,
      "distance_m": 62000,
      "polyline": "...",
      "maneuvers": [{"instr": "turn_right", "at_m": 1200}]
    }
  ]
}
```

### Appendix C — Map-match sketch

```text
for point in points:
  candidates = edges near point (S2)
Viterbi/HMM over candidates with transition (connectivity)
emit edge speeds for high-confidence path
```

### Appendix D — Traffic EMA

```text
speed[e] = α * sample + (1-α) * speed[e]
confidence[e] decays with time since last sample
eta_weight[e] = f(speed, historical, incident)
```

### Appendix E — Geocode pipeline

```text
normalize(query, locale)
  -> retrieve(text, geo_bias)
  -> rank(address hierarchy, popularity, distance)
  -> return top K with confidences
```

### Appendix F — Hierarchical long route

```text
route(A,B):
  pA, pB = partitions(A,B)
  if pA == pB: return local_CH(A,B)
  path1 = local_to_hub(A)
  path2 = backbone(hubA, hubB)
  path3 = hub_to_local(B)
  return stitch(path1,path2,path3)
```

### Appendix G — Offline pack manifest

```text
region_id: "us-sf-bay"
pack_version: 42
files: [tiles.bundle, graph.bin, poi.db]
diff_from: 41
size_bytes: 380000000
```

### Appendix H — Progressive scale table

| Scale | Tiles | Route | Traffic | POI |
|-------|-------|-------|---------|-----|
| Baseline | CDN | Regional CH | EMA | S2+text |
| 10× | Vector | Cache OD | Arterial priority | Shards |
| 100× | Multi-CDN | CRP cells | Incident bus | Entity resolve |
| 1,000× | Edge style | Predictive | Fine cells | Dense indoor hooks |

### Appendix I — NFR card

```text
Tile p99 < 100ms CDN
Route p99 < 500ms typical
Traffic age hot < 5m
Privacy: aggregate probes
Graph+tile versioned
Degrade traffic ≠ illegal routes
```

### Appendix J — Cost models for routing

| Cost | Use |
|------|-----|
| Time (traffic) | Default drive |
| Distance | Shortest |
| Fuel / eco | Phase 2 |
| Toll avoid | Preference flag |

### Appendix K — Incident types

| Type | Effect |
|------|--------|
| Closure | Block edge |
| Accident | Capacity penalty |
| Construction | Scheduled weight |
| Weather region | Multiplier overlay |

### Appendix L — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Postgres + PostGIS enough” | Partly for POI; not tile CDN or CH routing at global QPS |
| “ML ETA replaces graph” | Still need legal path constraints |
| “Store all GPS” | Privacy + cost deal-breaker |

### Appendix M — Related systems (conceptual)

| System | Role |
|--------|------|
| CDN | Tiles/packs |
| Kafka | Probes/incidents |
| Search index | Geocode/POI |
| Graph cells | Directions |
| Bigtable | Traffic time series |

### Appendix N — Glossary

| Term | Meaning |
|------|---------|
| Vector tile | MVT geometry layers for a cell |
| Map-match | Snap GPS to roads |
| CH / CRP | Routing prep schemes |
| S2/H3 | Hierarchical spherical cells |
| Free-flow | Uncongested speed |
| Maneuver | Turn-by-turn instruction |

### Appendix O — Worked example

```text
Route QPS 20K; avg 5ms CPU with CH → 100 cores order (plus redundancy)
Tile 2M QPS at edge; origin 0.1% = 2K QPS — fine
Traffic 500K samples/s → map-match fleet + EMA writers partitioned by cell
```

### Appendix P — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Same route worldwide same ms? | No — traffic epochs differ |
| Tile/graph sync? | Independent versions; nav pins graph |
| POI eventual? | Yes for hours/edits |

### Appendix Q — 30m interview checklist

1. Clarify tiles/geocode/route/traffic/POI/offline/privacy.  
2. Split planes; tile egress math.  
3. Reject planet Dijkstra; propose CH/CRP.  
4. Traffic aggregation + privacy.  
5. Diagram CDN / graph / Kafka.  
6. Scale jumps.  
7. Deal-breakers.

### Appendix R — Reroute loop

```text
onGPS:
  snap
  if off_route beyond threshold:
    directions.reroute(current, dest, graph_version)
    update guidance
```

### Appendix S — Privacy modes

| Mode | Behavior |
|------|----------|
| Precise nav | On-device; ephemeral |
| Traffic contribute | Aggregated / quantized |
| Timeline | Opt-in product separate |
| Incognito | Reduced retention/server ids |

### Appendix T — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Vector CDN, CH, caches |
| 100× | CRP cells, incidents, POI shards |
| 1,000× | Predictive traffic, pack diffs, fine cells |

### Appendix U — Transit hook (Phase 1.5)

```text
GTFS static + realtime
time-dependent graph
transfer model
separate from drive CH or layered
```

### Appendix V — ETA confidence

```text
confidence = f(sample_count, age, historical_variance, incident_flag)
UI: show range or "may vary" when low
```

---

*End of Google Maps system design.*
