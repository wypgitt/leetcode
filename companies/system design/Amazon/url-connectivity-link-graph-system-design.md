# System Design: URL Connectivity / Link-Graph Service

> **Focus areas:** Edge ingest (crawl hooks) · URL normalization · Graph storage · Forward/back links · Reachability & connectivity queries · Freshness · Spam/abuse · Scale partitioning  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct graph math vs storage math, split write ingest from query planes, explicit query classes (1-hop vs BFS vs SCC), deal-breakers for “put the web in one Neo4j”  
> **Interview theme:** Amazon SDE III / L6 — design a **link-graph / URL connectivity** service used by search, security, or site tools: ingest edges at crawl scale, answer connectivity queries cheaply, own partitions and freshness

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

Goal: **bound the graph product**—ingest URL→URL edges from crawlers or partners, store a web-scale (or corp-scale) link graph, and serve **connectivity / reachability / neighborhood** queries with clear SLAs—not a full search engine ranking stack (PageRank can be a batch consumer).

### 1.0 What this is / is not

| Dimension | **Link-graph / connectivity (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Store edges; answer graph queries | Full web search UI |
| Success | Correct neighborhoods & reachability under freshness SLO | Perfect global realtime PageRank |
| Writes | Edge upserts from crawl/ingest | User social graph MVP |
| Reads | Out/in links, k-hop, path exists, components (approx OK) | Arbitrary Cypher analytics ad-hoc |
| Hard problem | Partitioning + query fan-out + URL identity | HTML rendering |
| Amazon lens | Cost per edge, ownership of partitions, blast radius | “Just Neo4j” |

**Scope statement:** Design a URL connectivity / link-graph service: crawl-hook ingest, normalized URL nodes, adjacency storage, reachability/connectivity APIs, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who produces edges? | Crawler parsers / sitemap partners | Ingest API + Kafka |
| F2 | Edge meaning? | `from_url` links to `to_url` (HTML `<a>`) | Directed edge |
| F3 | Node identity? | Canonical URL / URL-ID | Normalization pipeline |
| F4 | Queries? | Out-neighbors, in-neighbors, “are connected within k?”, path sample | Query API classes |
| F5 | Connectivity? | Weakly/strongly connected? reachability | BFS/Union or labels |
| F6 | Freshness? | Minutes–hours after crawl | Versioned snapshots + streaming |
| F7 | Deletes? | Page gone / no longer links | Tombstones / re-crawl replace |
| F8 | Attributes? | `rel`, anchor text?, discovered_at | Edge properties optional |
| F9 | Host aggregation? | Host/domain graph optional | Rollup tables |
| F10 | Ranking signals? | Degree, outcount — not full PR in MVP | Batch jobs consume graph |
| F11 | Multi-tenant? | Often internal platform | Quotas per producer |
| F12 | Spam? | Link farms, cloaking | Trust scores / filters |
| F13 | Historical? | Keep edge history? | Time-versioned optional |
| F14 | API style? | Online low-latency + offline export | Dual serving |
| F15 | Seed crawl hooks? | Notify URL discovered | Outbound events |

**MVP functional scope:**

1. **Ingest edges** in batches (page parse result: src + list of dest URLs).  
2. **Normalize URLs** → stable `url_id`.  
3. Store **forward adjacency** (out-links) and **reverse index** (in-links).  
4. APIs: get out-links, get in-links (paginated), degree, exists-edge.  
5. **Reachability**: “is `t` reachable from `s` within k hops?” (k small, e.g. ≤3–6).  
6. **Connectivity sketch**: same weakly-connected component? (label/approx OK at scale).  
7. Replace-on-recrawl semantics for a source page’s out-edge set.  
8. Metrics, DLQ for bad URLs, producer quotas.  
9. Export snapshots for offline analytics (PageRank etc.).  
10. Basic spam/degree caps.

**Out of MVP:**

- Full interactive graph studio / Cypher for analysts  
- Exact global SCC maintenance under every edge update  
- Real-time personalized ranking  
- Storing full page HTML  
- Guaranteeing shortest path on trillion-edge graph with ms SLA globally  
- Multi-hop joins unbounded (k→∞ online)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest latency | Durable accept | p99 < 100–500ms batch ACK |
| N2 | Neighbor query | Interactive tools / ranking features | p99 < 50–100ms for 1-hop |
| N3 | k-hop reachability | Bounded k | p99 < 200–500ms typical; budgeted fan-out |
| N4 | Durability | No silent edge loss after ACK | Quorum/log |
| N5 | Availability | High for ingest & 1-hop | 99.9%+ |
| N6 | Freshness | Streaming apply | Minutes typical; snapshot hourly/daily |
| N7 | Scale | Billions nodes / trillions edges aspirational | Partitioned KV + overlays |
| N8 | Cost | Dominated by edge storage + reverse index | Compress; host rollups |
| N9 | Correctness | Normalized identity | Canonicalization must be consistent |
| N10 | Abuse | Crawl bombs / fan-out attacks | Caps, auth, budgets |
| N11 | Operability | Clear owners | Partition rebalance runbooks |
| N12 | Multi-region | Often single primary graph region MVP | DR replica |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Crawler parses `https://a.com/p` → 20 links → ingest batch → forward+reverse updated → query out-links returns them.  
2. Tool asks in-links to `https://b.com` → paginated results by rank/time.  
3. Reachability `s → t` within 3 hops → BFS with budgets → true/false + sample path.  
4. Recrawl of `a.com/p` with different links → atomic replace of that source’s out-set; reverse indexes patched.  
5. Offline job reads snapshot for PageRank.  
6. Degree API powers simple spam heuristics.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Malformed URL | Reject / DLQ; don’t poison graph |
| Redirect chains | Normalize to canonical; policy on storing redirect edges |
| Extreme out-degree (link dump) | Cap stored out-edges per page; sample or prioritize |
| Extreme in-degree (google.com) | Sharded reverse index; approx counts |
| Duplicate ingest | Idempotent upsert by (src, batch_version) |
| Partial batch failure | Retry; idempotent apply |
| Query fan-out explosion | Hop budgets, frontier caps, timeouts |
| Canonicalization mismatch | Duplicate nodes; merge jobs |
| Deleted page | Empty out-set; node may remain for in-links |
| Spam farm burst | Rate limit producer; quarantine host |
| Stale reverse index | Repair workers; version checks |
| k-hop timeout | Return partial + `truncated` |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Nodes (URLs) | 10B | 100B | 1T | multi-T |
| Edges | 100B | 1T | 10T | 100T |
| Ingest pages/s | 10K | 100K | 1M | 10M |
| Avg out-degree | 10 | 10 | 10–20 | mixed |
| Peak edge updates/s | 100K | 1M | 10M | 100M |
| 1-hop QPS | 50K | 500K | 5M | 50M |
| k-hop QPS | 1K | 10K | 100K | special fleet |
| Hot nodes (in-degree) | 1M+ | extreme | extreme | approx / tier |
| Snapshot size | tens PB compressed | … | … | cold object |

**What each jump forces:**

- **10×:** Separate forward/reverse stores; URL dictionary; streaming ingest; query budgets.  
- **100×:** Partition by url_id; sharded in-index; host rollups; async reverse repair; query gateways.  
- **1,000×:** Hierarchical graph (URL→host→domain); approx connectivity labels; offline-first for heavy analytics; cell/geo-sharded web segments.

### 1.5 Etc. (Constraints & Assumptions)

- Graph is **directed**.  
- Online queries favor **small k** and **paginated 1-hop**.  
- Exact global connectivity under continuous updates is expensive—use **labels/snapshots** for component queries.  
- Amazon: own cost of reverse index (often 2× storage).  
- Crawl politeness is crawler’s job; graph service enforces **ingest quotas**.

**Scope statement:**

> Design a link-graph service that ingests directed URL edges from crawl hooks, canonicalizes URL identity, stores forward and reverse adjacency under partition schemes, serves 1-hop and budgeted reachability/connectivity queries, and scales 10×/100×/1,000× without pretending one graph DB holds the web interactively.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Page ingest | 10K pages/s | 10M | Each page → many edges |
| Edge writes | ~100K/s | ~100M | Forward + reverse amplify |
| URL normalize/dict | ~100K+/s | huge | Cache hot hosts |
| 1-hop out query | 50K | 50M | Hot cache |
| 1-hop in query | 20K | 20M | Harder (skew) |
| k-hop | 1K | dedicated | Expensive |
| Snapshot export | batch | batch | IO heavy |

**Critical:** reverse index writes ≈ forward writes; plan **2× edge write amplification** (+ deletes/patches).

### 2.2 Storage

```text
URL dict: url_id (8B) + normalized URL (~80B avg) + meta
10B URLs × 100B ≈ 1 TB raw (plus indexes)

Edge: src_id, dst_id, ts, flags ≈ 24–40B
100B edges × 32B = 3.2 PB raw forward
Reverse similarly ~3 PB
Compressed / columnar / delta encoding → substantially less
Still multi-PB system at baseline web-ish scale

Interview tip: even “smaller corp web” — scale numbers down; architecture same
```

### 2.3 Ingest math

```text
10K pages/s × 10 links = 100K edges/s
Replace semantics: delete old outs not in new set
  If avg churn 30%, extra reverse patches
Batching 100–1000 edges/RPC reduces overhead
```

### 2.4 Query fan-out math (k-hop)

```text
BFS worst case: branching factor b=10, k=3 → up to 1110 nodes visited if tree
With web cycles + hubs: MUST cap frontier (e.g. 10K visits), time budget 100–300ms
Celebrity nodes: early truncation / prefer host-graph first stage
```

### 2.5 Hot key skew

```text
In-degree of major sites: millions–billions
Never store reverse list as single unsharded row
Shard reverse by dst_id + bucket; maintain approx count sketches
```

### 2.6 Memory / cache

```text
Cache: hot out-lists for popular sources; URL normalization LRU
Fronting 1-hop out can hit 80%+ if query skewed to crawl frontier
In-links cache harder — sample top-N + “see more” from storage
```

### 2.7 Bandwidth

```text
Ingest: 100K edges/s × 40B = 4 MB/s raw — small vs storage
At 100×: 400 MB/s edge bytes — network OK; Rocks/DB write amp matters more
Snapshot export dominates cross-cluster bandwidth
```

### 2.8 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | Single graph DB | KV adjacency + dict |
| 100× | Reverse skew; k-hop abuse | Shard; budgets; query tiers |
| 1,000× | Storage $; global BFS | Host hierarchy; approx CC; segment cells |

### 2.9 Cost owner sketch

```text
Cost ≈ edge storage ×2 (F+R) + dict + query fanout CPU + snapshot IO
Levers: compression, TTL on low-value edges, host rollups, sample in-links for UI
```

### 2.10 Critical bottlenecks

1. Reverse-index skew on hub URLs.  
2. Canonicalization consistency.  
3. k-hop query amplification / DoS.  
4. Replace-on-recrawl patch storms.  
5. Snapshot generation window vs mutability.

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Ingest durability first** — ACK only after log/KV durable.  
2. **Query classes with budgets** — never unbounded graph walks online.  
3. **Identity correctness** — normalization is a product dependency.  
4. **Skew isolation** — hubs get special storage.  
5. **Offline ≠ online** — heavy analytics on snapshots.  
6. **Cost ownership** — reverse index is explicit.  
7. **Progressive scale** — URL → host hierarchy when needed.

### 3.2 Core components

| Component | Responsibility |
|-----------|----------------|
| Ingest API / Gateway | Auth, quota, validate batches |
| Normalizer / URL Dict | Canonicalize → url_id |
| Edge Writer | Apply forward replace + reverse patches |
| Forward Store | src → [dst…] |
| Reverse Store | dst → [src…] sharded |
| Query Gateway | 1-hop, k-hop, budgets, cache |
| Reachability Workers | Bounded BFS/DFS |
| Connectivity Labeler | Batch/approx WCC/SCC labels |
| Snapshotter | Export graph segments |
| Spam / Trust | Degree caps, host reputation |
| Admin / Repair | Reindex reverse; merge dup nodes |
| Crawl Hook Emitter | Optional “new URL discovered” |

### 3.3 URL normalization (critical)

```text
Pipeline (deterministic):
  1. Scheme lower (http/https policy)
  2. Host lower; IDN → punycode
  3. Remove default ports
  4. Path normalize (resolve .., repeated //) — careful
  5. Sort query params OR strip tracking params (policy)
  6. Fragment: usually drop for graph identity
  7. Trailing slash policy per content-type/host rules
  8. Percent-encoding normalize
→ hash → url_id (64-bit or 128-bit)

Store raw → canonical mapping for debug
Redirect targets: optional edge type REDIRECT vs HYPERLINK
```

**Deal-breaker:** ad-hoc string equality without canonicalization → split-brain nodes.

### 3.4 Edge ingest semantics

| Mode | Semantics |
|------|-----------|
| **Replace page outs (recommended)** | Batch for `src` includes full out-set version `v`; writer diffs vs prior `v-1` |
| Append-only | Add edges; deletions via separate tombstones |
| Upsert edge | Single edge touch |

**MVP:** replace-by-source with `crawl_ts` / `batch_id` for idempotency.

```text
apply(src, outs[], version):
  old = forward.get(src)
  forward.set(src, outs, version) if version >= old.version
  reverse.remove(src from old-outs not in new)
  reverse.add(src to new-outs not in old)
```

### 3.5 API sketch

```text
POST /v1/ingest/pages
  { "src": "https://...", "outs": ["https://..."], "crawled_at": ..., "idem": "..." }

GET  /v1/urls/{id_or_url}/outlinks?cursor=&limit=
GET  /v1/urls/{id_or_url}/inlinks?cursor=&limit=
GET  /v1/urls/{id_or_url}/degree
GET  /v1/edge?src=&dst=          # exists?

POST /v1/query/reachability
  { "src": "...", "dst": "...", "max_hops": 3, "budget": 5000 }

POST /v1/query/connectivity
  { "a": "...", "b": "...", "mode": "wcc_label" }

GET  /v1/hosts/{host}/stats      # rollup
POST /v1/admin/repair/reverse
```

### 3.6 Data model

**url_dict**

| Field | Notes |
|-------|-------|
| url_id | PK |
| canonical_url | Unique |
| host | Secondary |
| first_seen / last_seen | |
| flags | spam, etc. |

**forward_adj**

| Field | Notes |
|-------|-------|
| src_id | PK |
| version / crawled_at | |
| dst_ids[] or columnar rows | Compressed |
| out_degree | |

**reverse_adj**

| Field | Notes |
|-------|-------|
| dst_id | PK part |
| shard_bucket | PK part |
| src_id | |
| updated_at | |

**edge_attr (optional)** | anchor, rel, type |

**wcc_labels** (batch) | url_id → component_id |

**host_graph** | host_a → host_b aggregated counts |

### 3.7 Graph storage options

| Store | Pros | Cons | When |
|-------|------|------|------|
| Wide-column / KV (Dynamo, Bigtable, Cassandra) | Scales, familiar | Multi-hop joins manual | **Default online** |
| Segmented files + RocksDB shards | Great scan/compress | Ops heavy | Very large |
| Classic graph DB | Nice query DX | Hard at web scale HA | Small corp graphs |
| Dual: KV online + warehouse snapshot | Best of both | Sync lag | **Recommended** |

### 3.8 Reachability design

```text
Online k-hop (k≤3–6):
  Bidirectional BFS if both ends known
  Prefer expand lower degree side first
  Cap: max_nodes_visited, max_ms, max_frontier
  Cache negative/positive for popular pairs short TTL

For larger connectivity:
  Use batch WCC labels: same label ⇒ connected (weakly) on snapshot
  Label freshness SLO separate from edge ingest
```

### 3.9 Connectivity / components

| Problem | Online approach | Offline approach |
|---------|-----------------|------------------|
| Weakly connected? | Labels from batch | Union-Find on snapshot |
| Strongly connected? | Rare online | Tarjan/Kosaraju batch |
| Path sample | Budgeted BFS | Precomputed landmarks optional |

**Landmark / sketch (100×+):** sample landmarks; store distances for approx reachability.

### 3.10 Tradeoffs table

| Decision | A | B | Pick |
|----------|---|---|------|
| Reverse index | Fully exact | Sampled for hubs | Exact sharded + sample UI |
| Replace vs append | Replace page outs | Append | Replace |
| url_id | 64-bit | 128-bit hash | 64 w/ collision check or 128 |
| k-hop | Sync RPC | Async job | Sync with hard budgets |
| CC | Exact live | Batch labels | Batch labels MVP |
| Host rollup | None | First-class | Yes at 10×+ |

### 3.11 Deal-breakers

1. Single Neo4j/one shard for “the web”.  
2. Unbounded BFS online.  
3. Unsharded reverse list for google.com.  
4. No URL canonicalization.  
5. Mixing PageRank iteration into online ingest path.  
6. Claiming exact live global SCC.  
7. Ingest without idempotency/versioning.  
8. Query API that returns entire in-link set without pagination.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
 Crawlers / Partners
         │
         ▼
 ┌───────────────┐     ┌──────────────┐
 │  Ingest API   │────▶│  Kafka/Log   │
 └───────────────┘     └──────┬───────┘
                              ▼
                    ┌─────────────────┐
                    │ Normalizer+Dict │
                    └────────┬────────┘
                             ▼
                    ┌─────────────────┐
                    │   Edge Writer   │
                    └───┬─────────┬───┘
                        ▼         ▼
                 Forward KV   Reverse KV (sharded)
                        │         │
                        ▼         ▼
                 ┌─────────────────────┐
                 │   Query Gateway     │
                 │  cache + budgets    │
                 └─────────┬───────────┘
                           ▼
                 Reachability / Labels
                           │
                           ▼
                 Clients: search, security, tools

 Offline: Snapshotter → S3 → Spark PageRank / WCC
```

### 4.2 Sequence: ingest page

```text
Crawler → Ingest API (auth, quota) → durable log ACK
Consumer → normalize all URLs → ids
EdgeWriter → read old forward → diff → write forward → patch reverse
Metrics: edges_added/removed
```

### 4.3 Sequence: 1-hop in-links

```text
Client → Query GW → cache?
  miss → reverse shards fan-out for dst_id buckets → merge page → return cursor
Hub dst → only top shard samples + approx_count from sketch
```

### 4.4 Sequence: reachability k=3

```text
Bidirectional BFS:
  frontierS={src}, frontierT={dst}
  alternate expand via forward/reverse
  intersect → path reconstruct
  on budget exceed → {reachable: unknown/false, truncated: true}
```

### 4.5 Multi-region / DR

```text
Primary region: ingest + online query
Async replicate KV / log to DR
Snapshot multi-region for analytics
Fail over: accept stale reads briefly; ingest pause or buffer
```

### 4.6 Hierarchical graph at 100×+

```text
URL graph (detailed) ─rollups─▶ Host graph ─▶ Pay-level domain graph
Queries:
  cheap pre-filter on host connectivity
  then URL-level confirm in neighborhood
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. After ingest ACK, edges eventually applied exactly once per version (idempotent).  
2. Forward version monotonic per src.  
3. Reverse is repairable projection of forward (eventual).  
4. url_id ↔ canonical bijective under active dict policy.  
5. Online queries never exceed declared budgets.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Writer crash mid-diff | Idempotent version apply; reverse repair |
| Dict unavailable | Fail ingest; don’t mint inconsistent ids |
| Reverse lag | Serve forward-only features; repair backlog SLO |
| Log loss | Multi-AZ log; replay |
| Query thundering herd | Cache + rate limit + hedge carefully |
| Canonicalization change | Dual-write / merge tool; epoch |

#### 5.1.3 Durability & backup

- Kafka/log retention for replay.  
- KV PITR / snapshots.  
- Periodic full graph snapshot checksum sampling.

#### 5.1.4 Consistency nuances

- Read-your-writes for producer optional via version wait.  
- Query may see reverse lag seconds–minutes—document SLO.  
- Connectivity labels lag hours—document separately.

#### 5.1.5 Security & abuse

- Authenticated producers only.  
- Per-host edge caps.  
- Query authz (internal).  
- k-hop rate limits (expensive).  
- PII in URLs: retention/redaction policies.

### 5.2 Scalability

#### 5.2.1 Partitioning

```text
url_id hash → N partitions
Forward row lives on partition(src)
Reverse rows on partition(dst) + sub-buckets
Cross-partition k-hop: query layer fans out with budget
```

#### 5.2.2 Hub handling

- Dedicated hub service for top hosts/URLs.  
- HyperLogLog for degree.  
- Store only sampled in-links for UI; full for offline.  
- Separate QoS pool.

#### 5.2.3 Ingest scaling

- Kafka partitions by src host hash (locality) or src_id.  
- Writer fleets per partition.  
- Backpressure when reverse repair lag high.

#### 5.2.4 Query scaling

- Tier1: 1-hop cached.  
- Tier2: k-hop limited QPS fleet.  
- Tier3: async job API for heavy paths.  
- Negative caching for unknown URLs.

#### 5.2.5 Offline analytics

- Columnar edge dumps.  
- WCC/SCC/PageRank on EMR/Spark.  
- Push labels back to KV for online connectivity checks.

#### 5.2.6 Cost controls

- Drop `nofollow` optional.  
- TTL edges from expired junk domains.  
- Compress posting lists (delta varint).  
- Host rollups instead of storing all low-value URL edges for some corpora.

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Ingest + schemas | Graph Ingest |
| URL dict / canonical | Identity / URL team |
| Online KV | Graph Storage |
| Query GW | Graph Query |
| Labels / PR jobs | Graph Analytics |
| Spam | Trust & Safety |
| Crawler contract | Crawl team |

#### 5.3.2 Safe evolution

- Edge schema version field.  
- Canonicalization epochs with merge.  
- Dual-read during reverse format change.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Ingest durable ACK p99 | < 500ms |
| Apply lag p99 | < 2–5 min |
| Reverse repair lag | < 15–60 min |
| Outlinks p99 | < 50–100ms |
| Reachability p99 (k≤3) | < 300–500ms |
| Truncation rate | Monitored |

#### 5.3.4 Progressive scale checklist

**10×:** dict + F/R KV; replace ingest; paginated APIs; budgets.  
**100×:** shard hubs; host graph; label batch; query tiers.  
**1,000×:** segment cells; approx sketches; landmark reachability; cold edge tiers.

### 5.4 Deep dive: reverse index repair

```text
If forward is source of truth:
  repair worker scans forward segments
  rebuilds reverse partitions asynchronously
  online writers also patch best-effort
  checksum: sample dst degrees vs scan
```

### 5.5 Deep dive: bidirectional BFS

```text
function reachable(s, t, k, budget):
  if s==t: return true
  qs, qt = {s}, {t}
  ds, dt = {s:0}, {t:0}
  visited_budget = 0
  for hop in 1..k:
    expand smaller frontier
    for each neighbor:
      visited_budget++
      if > budget: return TRUNCATED
      if in other side: return path
  return false
```

### 5.6 Deep dive: replace-on-recrawl diff

```text
old_set, new_set
add = new-old; del = old-new
write forward new_set with version
for dst in del: reverse.delete(dst, src)
for dst in add: reverse.put(dst, src)
Large churn pages: batch reverse ops; coalesce
```

### 5.7 Deep dive: connectivity labels

```text
Daily/ hourly:
  build undirected view (ignore direction for WCC)
  Union-Find / distributed connected components
  write label[url_id]=cc_id
Online: label[a]==label[b] ⇒ weakly connected on snapshot
Note: may lag; for safety+freshness use k-hop confirm
```

### 5.8 Deep dive: spam & link farms

- Cap out-degree stored.  
- Host-level edge rate limits.  
- Drop edges from quarantined hosts.  
- Trust rank offline → filter online serving.  
- Detect sudden degree spikes.

### 5.9 Testing & resilience

| Test | Purpose |
|------|---------|
| Canonicalization golden set | Identity |
| Idempotent ingest | Exactly-once apply |
| Reverse repair chaos | Convergence |
| Hub in-link load | Skew |
| k-hop budget DoS | Protection |
| Snapshot checksum | Analytics fidelity |

### 5.10 Comparison: link-graph vs social graph vs search

| | Link-graph | Social graph | Web search |
|--|------------|--------------|------------|
| Edge meaning | Hyperlink | Follow/friend | — |
| Skew | Extreme hubs | Influencers | Queries |
| Queries | Neighborhood/reachability | Feed/friends | Retrieve+rank |
| Updates | Crawl replace | User actions | Index pipeline |

### 5.11 Amazon leadership connection (brief)

- Own reverse-index cost and lag SLOs.  
- Say no to unbounded queries.  
- Frugality via compression and rollups.  
- Dive deep on canonicalization bugs (duplicate nodes).  
- Customer (search/security) SLAs differ—tier the API.

---

## 6. Wrap-Up

### 6.1 30-second recap

> Ingest page-level out-link sets through a durable log, canonicalize URLs to ids, store **forward** adjacency as source of truth and **sharded reverse** as a projection. Serve paginated 1-hop cheaply; serve reachability only with **hard hop/CPU budgets** (bidirectional BFS). Use **batch connectivity labels** and host rollups at scale. Progressive scale is partitioning, hub isolation, and hierarchical graphs—not one monster graph DB.

### 6.2 Key tradeoffs

1. Exact reverse vs sampled hubs.  
2. Live CC vs batch labels.  
3. Replace vs append edges.  
4. 64 vs 128-bit ids.  
5. Online k-hop vs async jobs.  
6. URL-only vs host hierarchy early.

### 6.3 Risks & follow-ups

- Canonicalization epoch migrations.  
- Reverse divergence bugs.  
- Query abuse.  
- Snapshot vs stream skew confusing users.  
- Storage cost cliffs.  
- Legal robots/PII in URLs.

### 6.4 What “good” looks like

- Query classes & budgets early.  
- F/R amplification in BOTE.  
- Hub skew plan.  
- Deal-breaker on single graph DB.  
- Clear freshness SLOs per API.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements (Q1–Q12)

1. Web-scale vs corporate intranet scale?  
2. Need anchor text?  
3. Historical edges?  
4. Redirect edges?  
5. JavaScript-discovered links?  
6. Who are query customers?  
7. Exact vs approx OK?  
8. Multi-tenant producers?  
9. SLA for reverse lag?  
10. Must support weighted edges?  
11. Integration with crawler frontier?  
12. Compliance deletes?

### 7.2 Identity & ingest (Q13–Q28)

13. Trailing slash policy.  
14. Tracking param stripping.  
15. HTTP vs HTTPS merging.  
16. www vs apex.  
17. url_id collision handling.  
18. Idempotency keys.  
19. Ordering across producers.  
20. Clock skew crawled_at.  
21. Partial page parses.  
22. Max outs cap policy.  
23. Internationalized domains.  
24. Data URI / javascript: links.  
25. Normalized form storage vs hash-only.  
26. Merge duplicate nodes tool.  
27. Schema evolution.  
28. Poison URL bombs.

### 7.3 Storage & query (Q29–Q48)

29. Why reverse is hard.  
30. Posting list compression.  
31. Pagination tokens.  
32. Degree sketches.  
33. Bidirectional BFS vs uni.  
34. Landmark approx.  
35. When to use graph DB.  
36. Partition rebalance.  
37. Secondary index by host.  
38. Caching strategy.  
39. Consistency of F vs R.  
40. Truncation UX.  
41. Path reconstruction storage.  
42. k=6 feasibility.  
43. Multi-hop join APIs.  
44. Read repair.  
45. Cold tier edges.  
46. Export format.  
47. Columnar vs row.  
48. Geo-partition web.

### 7.4 Connectivity & analytics (Q49–Q60)

49. WCC algorithm distributed.  
50. SCC batch.  
51. PageRank consumer.  
52. Label freshness.  
53. Incremental CC.  
54. Host graph benefits.  
55. Spam farm detection.  
56. Drift detection stream vs snapshot.  
57. Sampling edges for approx.  
58. Dynamic graphs theory vs practice.  
59. Serving PR online.  
60. Combining labels + k-hop.

### 7.5 Ops / Amazon (Q61–Q80)

61. Cost dashboard.  
62. Incident: reverse lag.  
63. Incident: wrong canonicalization.  
64. Capacity plan.  
65. Query DoS response.  
66. DR failover.  
67. Ownership boundaries with crawl.  
68. SLO burn.  
69. Migration to hierarchical graph.  
70. Data retention.  
71. Load test design.  
72. Canary ingest.  
73. Privacy review.  
74. Multi-region active.  
75. Throttle vs drop policy.  
76. DLQ replay.  
77. Cross-team API review.  
78. Frugality example.  
79. Dive-deep story.  
80. 45-minute plan.

---

## 8. Appendices

### Appendix A — Status cheat sheet

| State | Meaning |
|-------|---------|
| ACCEPTED | In log |
| APPLIED | Forward written |
| REVERSE_SYNCED | Projection OK |
| QUARANTINED_HOST | Edges filtered |
| LABEL_STALE | CC label old |

### Appendix B — Ingest batch (sample)

```json
{
  "src": "https://example.com/a",
  "outs": ["https://example.com/b", "https://other.com/"],
  "crawled_at": 1720000000,
  "idempotency_key": "crawl-123",
  "parser_version": 3
}
```

### Appendix C — Reachability response

```json
{
  "reachable": true,
  "hops": 2,
  "path": ["https://s", "https://m", "https://t"],
  "truncated": false,
  "nodes_visited": 48
}
```

### Appendix D — Error codes

| Code | Meaning |
|------|---------|
| 400 | Bad URL |
| 413 | Too many outs |
| 429 | Quota |
| 504 | Query budget timeout |
| 409 | Version conflict (rare) |

### Appendix E — Anti-patterns

- Unbounded recursive SQL joins.  
- Single reverse row for hubs.  
- Exact live SCC.  
- No pagination.  
- Canonicalize differently in crawl vs graph.  
- PageRank in ingest synchronous path.  
- Returning 10M in-links in one response.

### Appendix F — Capacity worksheet

```text
pages_per_sec =
avg_out_degree =
edge_write_amp ≈ 2 + churn_factor
reverse_shards =
max_k =
bfs_budget_nodes =
snapshot_period =
```

### Appendix G — 45-minute timebox

| Min | Topic |
|-----|-------|
| 0–5 | Requirements / query classes |
| 5–12 | BOTE + amplification |
| 12–25 | Ingest, dict, F/R stores |
| 25–35 | Reachability + labels |
| 35–42 | Scale/skew/ownership |
| 42–45 | Wrap |

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| Forward adj | Out-links |
| Reverse adj | In-links |
| WCC | Weakly connected component |
| SCC | Strongly connected component |
| Hub | Extreme degree node |
| Replace semantics | Full out-set per recrawl |
| Landmark | Precomputed distance anchors |

### Appendix I — Ownership RACI

| Item | R | A | C | I |
|------|---|---|---|---|
| Canonicalization | URL dict | Graph | Crawl | All consumers |
| Reverse lag | Storage | Storage | Query | SRE |
| k-hop budgets | Query | Query | Security | Clients |
| Snapshots | Analytics | Analytics | Storage | PR jobs |

### Appendix J — Progressive scale one-pager

| Scale | Must |
|-------|------|
| 1× | F store + dict + 1-hop |
| 10× | Reverse + replace + budgets |
| 100× | Hub shards + labels + host graph |
| 1,000× | Cells + approx + hierarchy |

### Appendix K — Normalization checklist

- [ ] Lower host  
- [ ] Punycode  
- [ ] Default port strip  
- [ ] Fragment drop  
- [ ] Param policy  
- [ ] Slash policy  
- [ ] Encoding  
- [ ] Golden tests  

### Appendix L — Minimal threat model

| Threat | Control |
|--------|---------|
| Ingest flood | Auth + quota |
| Query DoS | Budgets + RL |
| Graph poisoning | Trust filters |
| Data exfil | Authz |
| PII URLs | Redaction policy |

### Appendix M — Writer pseudocode

```text
function apply_page(src_url, outs, version):
  src = dict.id(src_url)
  dsts = [dict.id(u) for u in outs][:MAX_OUT]
  old = forward.get(src)
  if old and old.version > version: return
  forward.put(src, dsts, version)
  for d in old.dsts - dsts: reverse.del(d, src)
  for d in dsts - old.dsts: reverse.add(d, src)
```

### Appendix N — Query gateway policy

```text
1hop: cache TTL 30–300s
khop: max_hops<=6, budget_nodes<=5e3–2e4, timeout 300ms
connectivity_label: allow stale with freshness header
export: async only
```

### Appendix O — Snapshot format sketch

```text
edges.parquet: src_id, dst_id, crawled_at
urls.parquet: url_id, url, host
_manifest: version, ts, partition_count
```

### Appendix P — Interview “say this” (60 seconds)

> “I’d treat forward adjacency as source of truth from replace-on-recrawl ingest, with a durable log and a URL canonicalization dictionary. Reverse indexes are a sharded projection—especially careful on hubs. Online APIs are paginated 1-hop plus budgeted bidirectional BFS; global connectivity uses batch labels. Scale means partitioning, hub isolation, and host-level rollups—not one graph database for the web.”

### Appendix Q — Related systems map

| System | Relation |
|--------|----------|
| Web crawler | Edge producer |
| Search index | Consumer |
| PageRank jobs | Offline consumer |
| Security URL intel | Query customer |
| Knowledge graph | Different entity types |
| Social graph | Similar tech, different skew/UX |

### Appendix R — Chaos drills

1. Kill edge writer mid-diff.  
2. Dict outage.  
3. Reverse repair backlog storm.  
4. Hub query flood.  
5. Canonicalization config rollback.  
6. Snapshot corrupt partition.  
7. Kafka lag spike.  
8. Bidirectional BFS budget breach alerts.

### Appendix S — Metrics catalog

- `ingest_pages_per_sec`  
- `edges_applied_per_sec`  
- `reverse_lag_seconds`  
- `outlink_p99_ms`  
- `reachability_truncation_rate`  
- `dict_cache_hit`  
- `hub_query_qps`  
- `snapshot_age_hours`

### Appendix T — Host rollup example

```text
On edge a.com/x → b.com/y:
  host_edge[a.com→b.com].count++
Useful for cheap connectivity pre-check and spam
```

### Appendix U — Pagination cursor

```text
cursor = base64(shard, last_src_id, version)
Stable under append; replace may invalidate — document
```

### Appendix V — Comparison checklist

| Checkpoint | Covered? |
|------------|----------|
| Query classes | Yes |
| F/R amplification | Yes |
| Canonicalization | Yes |
| Hub skew | Yes |
| Budgets | Yes |
| Batch CC | Yes |
| Progressive scale | Yes |
| Deal-breakers | Yes |

### Appendix W — When numbers are “corp scale”

```text
If interviewer says 100M URLs / 1B edges:
  Same design; single region KV often enough
  Still mention hub skew and budgets — principles unchanged
```

### Appendix X — Edge type enum

| Type | Meaning |
|------|---------|
| HYPERLINK | Default `<a>` |
| REDIRECT | 30x |
| EMBED | iframe/img optional |
| CANONICAL | rel=canonical |

### Appendix Y — Failure injection worksheet

| Inject | Expect |
|--------|--------|
| Drop 10% reverse patches | Repair converges |
| Duplicate ingest | No dup edges |
| Huge out list | Cap + DLQ sample |
| k=10 request | Reject |

### Appendix Z — Final SDE III checklist

- [ ] Bounded query classes  
- [ ] BOTE with write amp  
- [ ] Dict + F/R design  
- [ ] Reachability budgets  
- [ ] Labels for connectivity  
- [ ] Hub plan  
- [ ] Ownership/SLOs  
- [ ] 10×/100×/1,000×  
- [ ] Deal-breakers  

---

*End of URL connectivity / link-graph system design (Amazon SDE III).*
