# System Design: Distributed Web Crawler

> **Focus areas:** Frontier · Politeness · Deduplication · Bounded concurrency · Failures · Recrawl · WARC/metadata  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split discover/fetch/parse/store, **politeness as hard constraint**, honest JS-render trade-offs  
> **Interview theme:** Meta content ingestion / index freshness fundamentals — reliability, concurrency, cost, compliance

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

Goal: **bound the crawler**—seed → frontier → polite fetch → parse → dedupe → store → discover, with bounded concurrency and principled failures. Downstream may feed **search index, link graph, integrity/safety corpora, or ML datasets**, but the interview is won on frontier, politeness, dedupe, and scale.

### 1.0 Purpose framing

| Use | Implication | Same crawler core? |
|-----|-------------|--------------------|
| Search / discoverability | Freshness + signals | Yes |
| Link / knowledge graph | Outlink quality | Yes |
| Safety / integrity research | Retention policy | Yes |
| ML pretraining corpus | Scale + dedupe + license | Yes |

**Scope statement:** Design a **distributed web crawler** with politeness, dedupe, bounded concurrency, durable outputs, and recrawl—optionally feeding Meta index/ML pipelines.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Purpose? | Index freshness / corpus / change monitor | Storage + recrawl policy |
| F2 | Seeds? | Editorial + sitemaps + continuous discovery | Frontier priorities |
| F3 | Scope? | Public web subset; robots.txt; no login MVP | Robots cache; allow/deny |
| F4 | Content? | HTML primary; PDF optional | Parser matrix; MIME allowlist |
| F5 | JS render? | Phase 2 selected hosts | Separate render farm |
| F6 | Dedupe? | URL canonical + content fingerprint | Bloom/exact + simhash optional |
| F7 | Politeness? | Per-host limits; Crawl-delay; global caps | Host queues **hard** |
| F8 | Output? | WARC/blobs + metadata (URL, status, links, text) | Immutable snapshots |
| F9 | Recrawl? | Importance × change rate | `next_fetch_at` scheduler |
| F10 | Concurrency? | High global; low per host | Two-level limits |
| F11 | Failures? | Retry transient; DLQ poison | Backoff; budgets |
| F12 | Compliance? | robots, ToS, legal assumed | Fail closed on disallow |

**MVP functional scope:**

1. Seed → frontier → fetch → parse → extract links/text → store → enqueue.  
2. robots.txt + per-host politeness (hard).  
3. URL canonicalization + dedupe.  
4. Bounded global concurrency + per-host concurrency (often 1).  
5. Retries with exponential backoff; honor 429/Retry-After.  
6. Content to object store; metadata index.  
7. Recrawl scheduler.  
8. Metrics: pages/s, 429s, robots denies, queue age, per-host delay.

**Out of MVP:**

- Full Chrome for all pages  
- Logged-in crawling  
- Perfect global near-duplicate clustering  
- Online embedding/index build (hooks)  
- Malware detonation sandbox fleet

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Throughput | Pages/day KPI | Baseline 10M/day → 10B/day at 1,000× |
| N2 | Politeness | **Hard constraint** | Default ≤1 concurrent/host; ≥1s spacing; Crawl-delay |
| N3 | Freshness | Tiered | Important pages hours–day |
| N4 | Durability | Fetched bytes kept | Object store; frontier checkpoints |
| N5 | Availability | Best-effort continuous | Can pause; not user-facing SLO |
| N6 | Correctness | No unbounded loops | Budgets, dedupe, depth limits |
| N7 | Compliance | robots / legal | Fail closed |
| N8 | Cost | Bandwidth + parse + store | Smart recrawl & dedupe |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seed → discover links → polite fetch → parse → WARC → enqueue children.  
2. Sitemap burst admits under host budget.  
3. 304/ETag unchanged → update schedule; skip body.  
4. 429 → backoff host; widen politeness.  
5. robots update → refresh; drop disallowed.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Facet / calendar traps | Filters, depth, param allowlist, budget |
| Soft 404 | Heuristics; don’t poison corpus |
| DNS fail | Negative cache; retry budget |
| Redirect chains | Cap (e.g. 5); canonicalize final |
| Duplicate content | Content hash / simhash; choose canonical |
| Zip bomb / huge HTML | Size limits; timeouts; sandbox parser |
| IP ban | Detect; slow down; rotate **only if policy allows** |
| robots unreachable | Fail closed or last-known (document) |
| Parser crash | Isolate; DLQ; don’t kill fleet |
| Clock skew `next_fetch_at` | Scheduler server time |
| Host with 1e9 URLs | Per-host budget & priority |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Pages fetched / day | 10M | 100M | 1B | 10B |
| Avg fetch QPS | ~115 | ~1.2K | ~12K | ~115K |
| Peak fetch QPS | ~500 | ~5K | ~50K | ~500K |
| Frontier URLs | 100M | 1B | 10B | 100B |
| Distinct hosts | 1M | 5M | 20M | 50M+ |
| Fetcher workers | 200 | 2K | 20K | 200K |
| Parse CPU cores | 100 | 1K | 10K | 100K |
| Store writes GB/day | ~10–50 | ×10 | ×10 | ×10 |
| robots cache entries | 1M | 5M | 20M | 50M |

**What each jump forces:**

- **10×:** Sharded frontier by host; dedicated politeness schedulers.  
- **100×:** Host-affinity fetchers; bloom layers; geo egress pools.  
- **1,000×:** Cell by TLD/host hash; prioritized recrawl tiers; heavy dedupe platform.

### 1.5 Etc. (Constraints & Assumptions)

- Politeness **outranks** throughput ambitions.  
- Identify UA; provide contact; honor robots.  
- Downstream index/ML are consumers—not the crawler itself.

**Scope statement:**

> Design a distributed web crawler: politeness-first host scheduling, URL/content dedupe, bounded global and per-host concurrency, robust failure/backoff, durable WARC/metadata output, and intelligent recrawl—scaling 10M→10B pages/day.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Discover/enqueue** | URL admits | ~few× fetch | ×10 | Frontier |
| **Fetch** | HTTP GETs | ~115/s avg | ~1.2K | Fetcher fleet |
| **Parse** | HTML→links/text | ~fetch rate | ×10 | Parsers |
| **Store** | WARC/object put | ~fetch rate | ×10 | Object store |
| **robots/DNS** | Aux lookups | ≪ fetch | ×10 | Caches |
| **Scheduler** | next_fetch_at | continuous | ×10 | DB/queue |

### 2.2 Bandwidth

```text
Avg downloaded body 50 KB (HTML heavy; many small)
10M pages/day × 50 KB ≈ 500 GB/day raw
+ headers/retries overhead ≈ 0.6–1 TB/day baseline
1,000× → ~0.5–1 EB/day class — forces selectivity, compression, change-detection
```

### 2.3 Frontier memory / storage

```text
100M URLs × 100B metadata ≈ 10 TB order (with indexes) — disk/DB not RAM
Need: sharded frontier store (Bigtable/Cassandra/custom)
In-RAM: per-host priority queues for “ready now” subset only
```

### 2.4 Politeness vs throughput

```text
If 1M hosts, 1 fetch / host / 2s theoretical cap = 500K QPS
Reality: host skew — top hosts huge URL counts but still 1 concurrent
Throughput bottleneck often = politeness on valuable hosts + DNS/TLS
```

### 2.5 Parse CPU

```text
HTML parse ~1–5 ms–tens of ms / page depending quality
115 QPS → few CPU cores; 115K QPS → thousands of cores + isolation
```

### 2.6 Frontier admit rate arithmetic

```text
Baseline: 10M pages/day ≈ 115 fetch/s sustained
Outlinks/page ≈ 40 (HTML-heavy); useful unique admit rate ≈ 2–5× fetch
  (most links already seen or filtered)
Admit attempts ≈ 115 × 40 = 4,600 canonicalize+bloom checks/s
Bloom false-positive rate target 1% → ~1% fall through to exact KV
Exact KV get QPS ≈ 46/s baseline; at 100× → ~4.6K/s (still OK if batched)
At 1,000× with 115K fetch/s: bloom checks ≈ 4.6M/s → need sharded blooms per cell
```

### 2.7 DNS & TLS overhead

```text
New host fraction: assume 5% of fetches hit cold DNS
Baseline: 0.05 × 115 ≈ 6 DNS lookups/s trivial
100×: ~600/s; with negative-cache + TTL cache still fine
1,000×: ~6K/s DNS — dedicated recursive resolvers + per-AZ cache mandatory
TLS handshake ~1–2 RTT; connection pool reuse critical
  Without reuse: 115K handshakes/s impossible
  With pool: amortize handshakes to <<1% of fetches
Keep-alive pool: ~50–200 conns/hot host max under politeness (usually 1–2)
```

### 2.8 robots.txt cache math

```text
Hosts active/day ≈ 1M baseline (skewed)
robots fetch once / 24h typical + on 404 refresh
1M / 86400 ≈ 12 robots fetches/s average; bursty at seed waves
Cache hit target >99.9% for fetch path
robots body avg 5 KB → 1M × 5 KB = 5 GB cache working set (fits RAM fleet)
Fail-closed on cache miss + fetch timeout: mark host temporarily blocked, retry later
```

### 2.9 Priority queue working set

```text
"Ready now" URLs in RAM heaps: not full frontier
Per politeness shard: top hosts with next_fetch_at ≤ now
Working set heuristic: 10K–100K ready URLs / shard × 200B ≈ 2–20 MB
Full frontier 100M URLs stays on disk/DB; scheduler pages due sets
Recrawl: 20% of daily fetches are refreshes → 2M refresh/day baseline
```

### 2.10 End-to-end latency budget (single URL)

```text
Canonicalize + bloom:     <1 ms
Exact dedupe get:         1–5 ms
Frontier enqueue:         2–10 ms
Wait in politeness queue: seconds–hours (dominant; policy)
DNS (cache hit):          <1 ms
Fetch RTT + download:     50–500 ms typical
WARC put:                 10–50 ms
Parse + outlink emit:     5–50 ms
SLO: time-to-first-fetch for high-pri seed ≪ minutes; deep crawl may be days
```

---

## 3. High-Level Design

### 3.1 Components

| Component | Responsibility |
|-----------|----------------|
| Seed Manager | Editorial seeds, sitemaps |
| Frontier | Durable URL store + priorities |
| Politeness Scheduler | Per-host rate / concurrency |
| Fetcher Workers | HTTP fetch with budgets |
| robots/DNS Cache | Compliance + perf |
| Parser Fleet | Links, text, language, MIME |
| Dedupe Service | URL + content fingerprints |
| Object Store | WARC / blobs |
| Metadata DB | URL state, etag, next_fetch_at |
| Recrawl Scheduler | Importance × change |
| DLQ / Poison | Bad URLs / parse crashes |

### 3.2 URL state machine

```text
DISCOVERED → QUEUED → FETCHING → FETCHED|ERROR
FETCHED → PARSED → (links enqueued)
ERROR → RETRY_WAIT → QUEUED | DEAD
robots disallow → BLOCKED
```

### 3.3 Canonicalization (MVP rules)

```text
1. Lowercase scheme/host
2. Remove default ports
3. Normalize percent-encoding
4. Strip fragments
5. Sort query params; drop tracking params (utm_*)
6. Trailing slash policy per host heuristics
7. Resolve relative → absolute against base
```

### 3.4 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Frontier keying | **Shard by host** | Politeness locality | Random URL shard ignoring host |
| Per-host concurrency | 1 default | Politeness | 100 concurrent to one news site |
| Dedupe | Canonical URL + content hash | Cost/quality | No dedupe → infinite traps |
| JS render | Opt-in farm | Cost | Headless Chrome for all HTML |
| Storage | Immutable WARC + metadata | Audit/replay | Overwrite-only lose history |
| Recrawl | Adaptive schedule | Freshness/$ | Blind daily refetch all |
| robots | Fail closed | Compliance | Ignore robots for speed |
| Frontier store | Durable KV/wide-column | Survive restarts | In-RAM queue only loses work |
| Bloom layer | Probabilistic front door | Admit QPS | Exact DB hit every outlink |
| DNS | Shared recursive + neg cache | Tail latency | Per-worker OS resolver stampede |
| Priority | Score = importance × freshness need | Budget | FIFO only starves fresh news |
| Parser isolation | Separate fleet + DLQ | Blast radius | Parse in fetcher thread OOMs all |
| Change detection | ETag/Last-Modified + hash | Bandwidth | Full body every recrawl forever |
| Redirects | Cap hops; store terminal URL | Traps | Follow infinite redirect chains |

**Expanded deal-breaker narratives (say out loud):**

1. **Host-oblivious sharding:** politeness tokens on node A, URLs on node B → either over-fetch a host or serialize every fetch on a global lock.  
2. **“Crawl faster = raise concurrency”:** news publishers ban you; legal/compliance incident. Throughput comes from **more hosts**, not smashing one.  
3. **No bloom/exact URL dedupe:** calendar traps and session-id URLs explode frontier to trillions.  
4. **Render everything:** headless cost 10–100× HTML parse; only score pages that need JS.  
5. **Ignore robots for MVP speed:** interviewer may end the loop; fail closed is the professional answer.

### 3.5 APIs (internal)

| Op | Semantics |
|----|-----------|
| `EnqueueURL(url, pri, parent)` | Admit with budget checks |
| `LeaseHostBatch(host, n)` | Scheduler grants fetch leases |
| `CompleteFetch(result)` | Persist + schedule next |
| `GetRobots(host)` | Cached rules |
| `AdminPause(host/global)` | Ops kill switch |

---

## 4. Architecture Diagram

```text
  Seeds / Sitemaps / Outlinks
              |
              v
     +--------+---------+
     | URL Canonicalize |
     | + Dedupe admit   |
     +--------+---------+
              |
              v
     +--------+---------+       +------------------+
     | Frontier Store   |<----->| Recrawl Scheduler|
     | sharded by host  |       | next_fetch_at    |
     +--------+---------+       +------------------+
              |
              v
     +--------+---------+
     | Politeness       |
     | per-host queues  |
     | tokens / delays  |
     +--------+---------+
              |
              v
     +--------+---------+     +----------------+
     | Fetcher Workers  |---->| robots + DNS   |
     | host-affinity    |     | caches         |
     +--------+---------+     +----------------+
              |
       +------+------+
       v             v
 +-----+-----+  +----+-----+
 | Object    |  | Parser   |
 | Store WARC|  | Fleet    |
 +-----------+  +----+-----+
                     |
                     v
              metadata DB + outlinks → frontier
              DLQ for poisons
```

**Fetch lease path:**

```text
scheduler picks host with due URLs and available token
 → lease up to N URLs (N usually 1)
 → fetcher GETs with timeout, size cap, redirect cap
 → on 429: set host penalty until Retry-After
 → on 200: put WARC; emit parse job
 → update etag/last_modified/next_fetch_at
```

**Discover path:**

```text
parser extracts <a href>
 → canonicalize
 → bloom/exact seen?
 → score priority (depth, parent importance, link equity heuristic)
 → enqueue if budgets allow
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No fetch without robots allow** (or documented last-known policy).  
2. **Per-host concurrency ceiling never exceeded**.  
3. **Frontier durable** — crash doesn’t lose leased URLs forever (lease timeout reclaim).  
4. **Fetched bytes immutable** once ACKed to store.  
5. **Poison isolation** — parser crash doesn’t take down fetcher fleet.

#### 5.1.2 Retries & leases

```text
Lease TTL = 5 minutes
If worker dies: URL becomes leasable again
Retries: 3–5 for transient (5xx, timeout)
429/503: host-level backoff separate from URL retry count
DNS failures: negative cache 5–15m
```

#### 5.1.3 Exactly-once?

At-least-once fetch is normal (re-fetch on reclaim). Idempotent store by `(url, content_hash, fetch_ts)` or WARC records unique ID. Downstream index must tolerate duplicates.

### 5.2 Scalability

#### 5.2.1 Host-affinity

Fetchers pinned to host hash ranges so politeness state is local (tokens, last_fetch_at) without cross-node chatty locks.

#### 5.2.2 Frontier sharding

```text
shard = hash(hostname) % N
All URLs for host live on same shard as politeness state
Global “ready queue” is merge of per-host due heaps
```

#### 5.2.3 Dedupe layers

| Layer | Structure | Purpose |
|-------|-----------|---------|
| URL bloom | In-mem approx | Cheap reject |
| URL exact | Key-value | Canonical seen |
| Content hash | SHA256 | Exact dup body |
| Simhash | Optional | Near-dup clustering Phase 1.5 |

#### 5.2.4 Progressive scale

| Scale | Must add |
|-------|----------|
| 10× | Host-sharded frontier + politeness schedulers |
| 100× | Geo egress; render farm opt-in; layered blooms |
| 1,000× | Cells by TLD; tiered recrawl platform; dedicated dup clusters |

### 5.3 Maintainability

- Config as data: per-host overrides, MIME allowlists, param strip lists.  
- Replay: WARC → reparse without refetch for parser upgrades.  
- Clear metrics/ownership: crawl SRE vs parser quality vs compliance.  
- Chaos: kill fetchers mid-lease; ensure reclaim.

#### 5.3.1 Config surfaces

| Config | Owner | Hot-reload? |
|--------|-------|-------------|
| Global crawl budget (pages/day) | Capacity | Yes |
| Per-host RPS / concurrency | Compliance + crawl | Yes |
| Tracking-param strip list | Quality | Yes |
| MIME allow/deny | Security | Yes |
| Render allowlist (host/path) | Cost | Yes |
| User-Agent string | Legal | Controlled |
| Kill switch host/TLD/global | Oncall | Yes (instant) |

#### 5.3.2 Ownership boundaries

| Team lens | Owns |
|-----------|------|
| Crawl SRE | Frontier durability, fetcher health, politeness bugs |
| Content quality | Priority scores, soft-404, language, boilerplate |
| Compliance | robots, ToS, blocklists, legal holds |
| Indexing (downstream) | Consume WARC/metadata; crawl must not block on them |

### 5.4 Frontier deep dive

#### 5.4.1 Frontier record

```text
url_id / canonical_url
host
priority_score
depth
discover_ts, last_fetch_ts, next_fetch_at
state: DISCOVERED|QUEUED|FETCHING|FETCHED|ERROR|BLOCKED|DEAD
etag, last_modified, content_hash
fail_count, last_status
lease_owner, lease_until
parent_url_id (optional, sample)
importance_class: SEED|SITEMAP|OUTLINK|REFRESH
```

#### 5.4.2 Admit pipeline

```text
raw href
 → resolve absolute
 → canonicalize (scheme/host/port/path/query policy)
 → scheme allowlist (http/https only MVP)
 → host allow/deny / IP private ranges block (SSRF)
 → bloom may-contain? if yes → exact KV get
 → if seen: maybe refresh priority bump; else insert
 → score priority; write frontier; notify host scheduler
```

**Budgets at admit:** max depth, max URLs/host/day, global discover QPS, MIME hints from extension.

#### 5.4.3 Host-sharded frontier why

```text
shard = hash(hostname) % N_shards
Politeness state (tokens, last_fetch, robots snapshot ref) co-located
LeaseHostBatch never cross-shard chats for the common path
Resharding: consistent hashing with virtual nodes; migrate host wholes
```

**Deal-breaker:** sharding by `hash(url)` scatters one host across all shards → cannot enforce “1 concurrent” without distributed locks.

#### 5.4.4 Ready-set scheduling

```text
Per shard:
  host_heap keyed by next_eligible_at
  while workers idle:
    host = heap.pop_min if due
    if host.tokens > 0 and host.inflight < max_conc:
      lease URLs with next_fetch_at <= now ordered by priority
      push host back with updated next_eligible_at
```

Starvation control: aging boost for URLs waiting > T; separate lanes for SEED vs deep OUTLINK.

### 5.5 Politeness deep dive

#### 5.5.1 Token bucket per host

```text
rate = 1 token / crawl_delay   # robots Crawl-delay or default 1/2s
burst = 1 (usually)
concurrency = 1 (default; rare VIP hosts 2)
On 429: freeze tokens until Retry-After; multiply delay ×2 (cap)
On 5xx streak: host penalty circuit breaker
```

#### 5.5.2 Why concurrency≠throughput knob

Politeness is a **social/legal** constraint, not only technical. Aggregate crawl rate scales with **number of eligible hosts** and **discover diversity**, not per-host parallelism.

#### 5.5.3 Cross-host fairness

```text
Fetcher pool must not let 10 mega-hosts monopolize all workers
Weighted fair scheduling across hosts
Caps: max % of fleet per TLD / per ASN (optional anti-abuse)
```

### 5.6 robots.txt deep dive

#### 5.6.1 Evaluation order

```text
1. Fetch/cache robots.txt for scheme://host
2. Parse groups for our User-Agent (+ * fallback)
3. Longest matching Allow/Disallow prefix wins (common practice)
4. Honor Crawl-delay if present (policy)
5. Sitemap URLs → seed manager (not fetcher hot path)
```

#### 5.6.2 Failure policy

| Condition | Action |
|-----------|--------|
| 200 parse OK | Cache 24h (or robots Cache-Control) |
| 404 | Treat as allow-all; cache shorter |
| 5xx / timeout | **Fail closed**: do not fetch content paths; retry robots |
| Parse error | Fail closed + metric; manual override path |

**Interview line:** “We never invent allow when uncertain.”

#### 5.6.3 Cache & invalidation

```text
Key: (scheme, host)
Value: rules AST + fetched_at + etag
Push invalidation on admin; TTL refresh in background
Fetchers only read local/regional cache — never block on origin robots synchronously without budget
```

### 5.7 Bloom filters & dedupe

#### 5.7.1 Layered dedupe

| Layer | FPR / exact | Placement |
|-------|-------------|-----------|
| L0 URL Bloom | ~0.1–1% FPR | Per cell RAM |
| L1 Exact URL KV | Exact | Frontier metadata |
| L2 Content SHA256 | Exact | After fetch |
| L3 Simhash band | Approx near-dup | Phase 1.5 cluster |

#### 5.7.2 Bloom sizing arithmetic

```text
n = 1e9 URLs, p = 0.01
m ≈ -n ln(p) / (ln2)^2 ≈ 9.6e9 bits ≈ 1.2 GB
k ≈ -ln(p)/ln2 ≈ 7 hashes
At 1,000× cells: each cell holds its URL universe bloom; global union optional offline
```

#### 5.7.3 False positive handling

Bloom says “maybe seen” → exact get. Never skip exact on bloom yes if correctness of “must crawl new” matters for seeds; for bulk outlinks, bloom-yes + exact-miss is rare and OK to admit.

#### 5.7.4 Content dedupe

```text
On 200: hash body → if hash seen for other URL, mark DUPLICATE_CONTENT
Still keep URL metadata (aliases); may skip parse/index emit
Saves parse CPU and index spam
```

### 5.8 DNS deep dive

#### 5.8.1 Path

```text
fetcher needs IP
 → local LRU (host → A/AAAA, TTL)
 → miss: recursive resolver fleet (anycast)
 → negative cache NXDOMAIN / SERVFAIL (bounded TTL)
 → prefer IPv6 policy explicit
```

#### 5.8.2 SSRF / safety

```text
Resolve → check IP not in private/link-local/metadata ranges
Re-check after redirects (DNS rebinding: pin IP for request or revalidate)
Block file://, gopher://, etc. at scheme gate
```

#### 5.8.3 Performance

Connection establishment dominates cold hosts. Host-affinity helps reuse TLS sessions. At 1,000×, DNS metrics (`lookup_p99`, `nxdomain_rate`) are first-class SLO inputs.

### 5.9 Parser deep dive

#### 5.9.1 Responsibilities

1. Charset detect → unicode.  
2. Extract title, text, language, canonical link.  
3. Extract outlinks + rel attributes.  
4. Detect soft-404 / parked / doorway heuristics.  
5. Emit structured parse record; never refetch inside parse.

#### 5.9.2 Isolation

```text
Fetcher puts WARC + parse job {url, warc_ptr}
Parser workers pull jobs; crash → job retry; N fails → DLQ
Memory cap / timeout per document
Zip bomb / entity expansion defenses
```

#### 5.9.3 JS rendering bridge

```text
HTML parse finds “needs_render” signals (empty root, known SPA hosts)
 → enqueue render farm (small capacity)
 → render produces HTML snapshot WARC-converted
 → normal parse
Budget: <<1% of pages; never default path
```

### 5.10 Priority & recrawl

#### 5.10.1 Priority score sketch

```text
score = w1*seed_bonus
      + w2*1/(1+depth)
      + w3*parent_importance
      + w4*site_authority_prior
      + w5*path_quality (not /tag/page/99999)
      - w6*fail_count_penalty
```

Separate **discover priority** (first fetch) from **recrawl priority** (freshness).

#### 5.10.2 Adaptive recrawl

```text
change_rate EMA from content_hash flips
next_interval = clamp(min, max, base / (change_rate + ε))
News hosts: minutes–hours; static docs: weeks
Never exceed host politeness even if “news”
```

#### 5.10.3 Change detection

| Signal | Use |
|--------|-----|
| If-None-Match / ETag | Cheap 304 |
| If-Modified-Since | Fallback |
| Body hash | Truth of change |
| Headers-only change | Maybe skip reindex |

### 5.11 Progressive scale evolution (10× / 100× / 1,000×)

| Dimension | Baseline | 10× | 100× | 1,000× |
|-----------|----------|-----|------|--------|
| Fetch/s | ~115 | ~1.2K | ~12K | ~115K |
| Frontier shards | tens | hundreds | 1K+ | cells × shards |
| Bloom | 1–2 tiers | sharded | per-cell | hierarchical |
| Egress | 1–few regions | multi-region | geo IP localize | per-continent cells |
| Render | tiny | allowlist grow | dedicated pool | still <<1% |
| Recrawl | heuristics | change EMA | ML change predict | tiered platform |
| Ops | host pause | TLD pause | cell drain | global budget broker |

**Narrative:**

- **→10×:** Host-sharded frontier + politeness schedulers become non-negotiable; layered bloom; lease reclaim hardened.  
- **→100×:** Geo egress (crawl near targets); opt-in render farm; dup clusters; soft-404 ML; per-ASN caps.  
- **→1,000×:** TLD/cell federation; global URL directory optional; selective crawl (importance sampling); dedicated compliance plane; indexer feedback loop for priority.

### 5.12 Failure drills

| Drill | Expected |
|-------|----------|
| Kill fetcher mid-lease | Lease TTL reclaim; no permanent loss; possible duplicate WARC |
| robots origin down | Fail closed; fetch pause for those hosts |
| Parser OOM storm | DLQ; fetcher unaffected |
| Bloom corruption | Rebuild from exact KV offline; temporary over-fetch OK |
| One shard hot (huge host set) | Split shard; rebalance hosts |

---

## 6. Wrap-Up

### 6.1 Summary

A Meta-scale crawler is a **politeness-constrained distributed scheduler** around durable frontier state, not a naive thread pool of GETs. Reliability is lease/reclaim + backoff; scalability is host-sharded affinity; maintainability is WARC replay and config-driven policies.

### 6.2 Trade-offs

| Trade-off | Choice |
|-----------|--------|
| Coverage vs politeness | Politeness wins |
| Freshness vs cost | Adaptive recrawl |
| JS fidelity vs $ | Opt-in render |
| Exact near-dup vs cost | Hash first; simhash later |

### 6.3 Deal-breakers

1. Ignoring robots for throughput.  
2. Global random queue with unbounded per-host hammering.  
3. Chrome-for-everything MVP.  
4. No URL trap defenses.  
5. Undurable frontier (lost on restart).

### 6.4 Scale one-liner

Baseline host queues → 10× sharded frontier → 100× geo+affinity → 1,000× cell fabric + tiered recrawl.

---

## 7. Deeper / Related Interview Questions

### 7.1 Frontier & scheduling

**Q1: Why shard frontier by host?**  
A: Politeness and scheduling state are per-host; co-locate to avoid distributed locks on every fetch.

**Q2: Priority queue key?**  
A: Score from importance, freshness debt (`now - next_fetch_at`), depth, seed boost. Starvation: aging boost.

**Q3: How do leases prevent double fetch?**  
A: Conditional lease in DB; TTL reclaim; accept rare duplicate fetches.

**Q4: What if one host has 1e9 URLs?**  
A: Per-host budget/day; prioritize by score; don’t let one host fill shard disk alone without quotas.

**Q5: Sitemap vs link discovery?**  
A: Sitemaps great for coverage of large sites; still politeness-bound; validate URLs.

### 7.2 Politeness & compliance

**Q6: robots.txt parse failures?**  
A: Fail closed (fetch only seeds path?) or use last-good with expiry—state choice explicitly.

**Q7: Crawl-delay vs our defaults?**  
A: Honor max(our_min_spacing, Crawl-delay).

**Q8: robots for subdomains?**  
A: Each host separate; `www` vs apex not assumed identical.

**Q9: Are IP rotations ethical?**  
A: Only with policy/legal; politeness intent is not to evade bans covertly. Prefer slowdown.

**Q10: How to identify crawler?**  
A: Clear UA + contact URL/email; reverse DNS optional good citizen.

### 7.3 Fetching

**Q11: Timeouts and size caps?**  
A: Connect/read timeouts; max body bytes; max redirects; reject unexpected content-types early.

**Q12: Conditional GET?**  
A: Store ETag/Last-Modified; send If-None-Match; 304 updates schedule without body.

**Q13: HTTP/2 multiplexing vs politeness?**  
A: Multiplexing ≠ permission to explode concurrency; still enforce per-host request rate.

**Q14: TLS/SNI failures?**  
A: Record error class; backoff; don’t infinite retry.

**Q15: Canonical redirect handling?**  
A: Cap chain; set canonical to final; attribute aliases; avoid redirect loops via visited set.

### 7.4 Parsing & traps

**Q16: Spider traps?**  
A: Calendar infinite paths, session IDs, faceted nav — depth limits, param allowlists, per-host URL caps, regex denylist.

**Q17: Soft 404 detection?**  
A: Heuristics on content similarity to known 404 templates; status 200 ≠ quality.

**Q18: Parser isolation?**  
A: Separate process/container; CPU/mem limits; DLQ on crash; circuit break host if parse fail storm.

**Q19: Language/encoding?**  
A: Detect charset; normalize UTF-8 store; record original.

**Q20: Why WARC?**  
A: Standard for web archives; request/response fidelity; replayable for parser upgrades and audits.

### 7.5 Dedupe & storage

**Q21: URL dedupe vs content dedupe?**  
A: URL prevents refetch loops; content saves storage/index spam when many URLs same body.

**Q22: Bloom false positives?**  
A: OK to occasionally skip (or second-check exact). False negatives worse for traps → use exact for admit critical path as needed.

**Q23: Storage layout?**  
A: Object path by date/host hash; metadata DB points to blob; lifecycle cold tier.

**Q24: Exactly once indexing?**  
A: Downstream consumes with idempotent doc_id = hash(url)+version; crawler provides versions.

### 7.6 Recrawl & freshness

**Q25: How to estimate change rate?**  
A: History of content hash changes; adaptive interval with min/max bounds; important seeds tighter.

**Q26: Freshness SLO for homepage of major news?**  
A: Minutes–hour tier; dedicated high-pri host budgets.

**Q27: Crawl vs push feeds?**  
A: Prefer sitemaps/feeds when available; still verify with fetch.

### 7.7 Scale & JS

**Q28: When introduce headless render?**  
A: Hosts known JS-heavy and high value; never default. Queue separate with tiny concurrency.

**Q29: Geo egress pools?**  
A: Some content geo-varies; also distribute bandwidth; legal constraints apply.

**Q30: 10B pages/day bottlenecks?**  
A: DNS, TLS CPU, politeness on head hosts, store write IOPS, parser CPU, frontier DB.

### 7.8 Alternatives & craft

**Q31: Single Redis queue of URLs?**  
A: Fine toy; fails politeness, durability, host skew at scale.

**Q32: MapReduce daily crawl only?**  
A: Misses continuous freshness; OK for corpus snapshots complementing stream crawler.

**Q33: How to open?**  
A: Purpose, politeness hard, scope, JS?, output format—then draw host-sharded frontier.

**Q34: What impresses?**  
A: Lease reclaim, trap defenses, politeness tokens, adaptive recrawl, clear deal-breakers.

**Q35: Common mistake?**  
A: Maximizing QPS diagrams while treating robots as optional.

**Q36: End strong?**  
A: Invariants + scale cells + WARC replay story.

**Q37: How do you pause a legal takedown host?**  
A: Admin denylist with immediate scheduler fence; in-flight leases finish or cancel; purge policies separate.

**Q38: Metrics that matter?**  
A: pages/s, bytes/s, 429 rate, robots deny, queue age p99, per-host delay, parse fail rate, dup rate.

**Q39: Interaction with indexing?**  
A: Emit change log `{url, version, hash, links}` to Kafka; indexer is separate system.

**Q40: Budgeting discovery depth?**  
A: depth from seed, score decay, domain authority caps—prevent infinite graph walk.

**Q41: IPv6 / dual stack?**  
A: Support; cache A/AAAA; failures independent.

**Q42: CAPTCHA pages?**  
A: Detect; mark host needs_render/human; don’t burn retries; often skip for MVP corpus.

---

### Appendix A — Priority score sketch

```text
score = importance * freshness_debt * seed_boost * (0.85 ^ depth)
freshness_debt = clamp(now - next_fetch_at, 0, max)
```

### Appendix B — Politeness token bucket

```text
host.state:
  concurrent = 0
  max_concurrent = 1
  min_interval = max(1s, crawl_delay)
  next_allowed_at
  penalty_until

can_grant(host):
  now >= next_allowed_at and now >= penalty_until and concurrent < max
```

### Appendix C — Admit URL pseudocode

```text
def admit(url, parent):
  u = canonicalize(url)
  if not allowed_scheme(u): return
  if bloom.maybe_seen(u) and exact.seen(u): return
  if host_budget_exceeded(u.host): return
  if depth(parent)+1 > MAX_DEPTH: return
  if robots.disallow(u): return BLOCKED
  frontier.insert(u, score)
  exact.mark_seen(u)
```

### Appendix D — Fetch result handling

```text
match status:
  200: store; parse; update_change_model; schedule_next
  304: schedule_next; no store body
  301/302: follow if under cap; canonical update
  404/410: mark dead or long postpone
  429: host.penalty = Retry-After; requeue URL
  5xx: url.retry++; backoff
```

### Appendix E — Metadata schema

| Field | Type |
|-------|------|
| url_canonical | string PK |
| host | string |
| status_last | int |
| etag | string |
| content_hash | string |
| next_fetch_at | ts |
| priority | float |
| depth | int |
| last_error | string |
| warc_pointer | string |

### Appendix F — WARC record sketch

```text
WARC/1.0
WARC-Type: response
WARC-Target-URI: https://example.com/
WARC-Date: ...
WARC-Record-ID: <urn:uuid:...>
Content-Length: ...

HTTP/1.1 200 OK
...
[body]
```

### Appendix G — Trap filters

| Pattern | Action |
|---------|--------|
| `/calendar/2020/01/01` infinite | date param normalize / deny |
| `sessionid=` | strip or deny |
| sort+facet combos | allowlist params |
| very long paths | max path segments |

### Appendix H — NFR card

```text
Politeness hard
Host-sharded frontier
Lease + reclaim
robots fail closed
Size/time/redirect caps
WARC + metadata
Adaptive recrawl
Parser isolation
```

### Appendix I — Progressive scale

| Scale | Frontier | Fetch | Aux |
|-------|----------|-------|-----|
| Base | DB + host queues | 200 workers | robots cache |
| 10× | Many shards | 2K affinity | layered bloom |
| 100× | Regional | geo egress | render opt-in |
| 1,000× | Cells | 200K workers | dedupe platform |

### Appendix J — Comparison

| Approach | Politeness | Scale | Verdict |
|----------|------------|-------|---------|
| Thread pool + queue | Weak | Poor | Reject |
| Host sharded + leases | Strong | Good | **Choose** |
| Pure batch MR | Medium | Corpus OK | Complement |
| Chrome fleet only | Costly | Low coverage/$ | Reject sole |

### Appendix K — DNS cache policy

```text
positive TTL: honor DNS TTL capped [60s, 1h]
negative TTL: 5–15m
refresh async before expiry for hot hosts
```

### Appendix L — Recrawl bounds

```text
min_interval = 1h (news tier) / 1d (default) / 7d (rare)
max_interval = 30d
if changed: decrease interval *= 0.5 (floor min)
if unchanged k times: increase *= 1.5 (ceil max)
```

### Appendix M — Metrics board

| Metric | Alert |
|--------|-------|
| 429 rate | host/global slowdown |
| queue age p99 | scale fetchers/shards |
| parse OOM | isolate; patch parser |
| robots fetch fail | compliance risk |
| store put fail | pause crawl |

### Appendix N — Security

- SSRF: block private IP ranges / link-local on resolve.  
- Limit protocols to http/https.  
- Parser sandbox.  
- Credential never sent (no login MVP).  

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Frontier | Set of URLs to crawl |
| Politeness | Rate limits per host |
| WARC | Web ARChive format |
| Lease | Temporary ownership of URL fetch |
| Soft 404 | 200 with not-found content |

### Appendix P — Worked throughput

```text
200 fetchers × 1 req per 2s avg think time = 100 QPS (order)
Need concurrency across many hosts: 200 workers can drive ~100–500 QPS with variance
10M/day ≈ 115 QPS average — baseline fleet size plausible
```

### Appendix Q — Seed types

| Seed | Notes |
|------|-------|
| Editorial allowlist | High trust |
| Trending domains | Freshness |
| Sitemap indexes | Coverage |
| RSS/Atom | Change hints |
| Outlinks | Discovery |

### Appendix R — 30m checklist

1. Purpose + politeness hard.  
2. Host-sharded frontier diagram.  
3. robots + leases + traps.  
4. WARC/metadata.  
5. Recrawl.  
6. Scale jumps.  
7. Deal-breakers.

### Appendix S — DLQ categories

| Category | Example |
|----------|---------|
| PARSE_CRASH | malformed HTML nuke |
| POLICY | legal deny |
| BUDGET | host exceeded |
| MIME | executable binary |
| LOOP | redirect cycle |

### Appendix T — Fetcher request budget

```text
max_redirects = 5
connect_timeout = 5s
total_timeout = 20s
max_body = 5 MB HTML default
max_concurrent_global = workers
max_concurrent_per_host = 1
```

### Appendix U — Why Meta asks

Validates distributed systems under **external constraints** (robots, traps, skew) similar to ingesting the open web or partner content at scale.

### Appendix V — Quick deal-breaker card

| Fantasy | Reality |
|---------|---------|
| Max QPS first | Politeness first |
| Ignore robots | Compliance fail |
| Chrome everywhere | Cost blowup |
| Redis list only | Lost state / host hammer |
| No size caps | Zip bombs |

### Appendix W — Host state record

```text
HostState {
  host,
  robots_status, robots_fetched_at, robots_body_hash,
  crawl_delay_ms,
  max_concurrent,
  next_allowed_at,
  penalty_until,
  inflight,
  urls_fetched_today,
  daily_budget,
  last_error_class,
  render_tier: NONE|OPTIONAL|REQUIRED
}
```

### Appendix X — URL priority classes

| Class | Examples | Recrawl bias |
|-------|----------|--------------|
| S0 | Editorial seeds, major news home | Minutes–hours |
| S1 | Sitemap high-pri | Hours |
| S2 | Normal discover | Days |
| S3 | Long-tail | Weeks |
| S4 | Rare / errors | Max interval |

### Appendix Y — Change detection

```text
if content_hash == prev_hash:
  unchanged_streak++
  next = min(max_interval, prev_interval * 1.5)
else:
  unchanged_streak = 0
  next = max(min_interval, prev_interval * 0.5)
  emit ChangeEvent(url, old_hash, new_hash, ts)
```

### Appendix Z — Parser output schema

```json
{
  "url": "https://example.com/a",
  "final_url": "https://example.com/a/",
  "status": 200,
  "content_hash": "sha256:...",
  "lang": "en",
  "title": "...",
  "text_bytes": 12000,
  "outlinks": ["https://..."],
  "canonical_link": "https://example.com/a",
  "fetch_ms": 230,
  "warc_record_id": "urn:uuid:..."
}
```

### Appendix AA — Cell topology at 1,000×

```text
cell_id = hash(tld or host) % num_cells
each cell owns:
  frontier shards
  politeness schedulers
  fetchers + parsers
  local robots cache
cross-cell outlinks: enqueue via durable cross-cell topic
```

### Appendix AB — Cost knobs

| Knob | Effect |
|------|--------|
| Raise min_interval | Less bandwidth |
| Drop S3/S4 discovery | Less frontier growth |
| Disable render farm | Big $ save |
| Stronger param stripping | Fewer dup URLs |
| Cold storage lifecycle | Store $ |

### Appendix AC — Legal / ops switches

```text
global_pause = true
deny_host(host)
deny_tld(tld)
max_global_qps = N
user_agent_override = "..."
# all checked before lease grant
```

### Appendix AD — Integration with indexer

```text
crawler ChangeEvent → Kafka topic crawl.changes
indexer consumes → fetch WARC pointer → extract → upsert doc
crawler does not wait on indexer ACK
backpressure: if object store unhealthy, pause fetch leases
```

### Appendix AE — Worked politeness example

```text
Host news.example with Crawl-delay: 2
min_interval = max(1000ms, 2000ms) = 2000ms
max_concurrent = 1
1000 URLs ready → throughput ≤ 0.5 QPS to that host
Global fleet can still do high QPS across millions of hosts
```

### Appendix AF — Final interview card

```text
politeness > throughput
host-sharded frontier + leases
robots fail closed
canonical + bloom/exact dedupe
trap defenses
WARC + metadata
adaptive recrawl
parser isolation
10× shards → 100× geo → 1000× cells
```

---

*End of Distributed Web Crawler system design.*
