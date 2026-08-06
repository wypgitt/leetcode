# System Design: Distributed Web Crawler

> **Focus areas:** URL frontier · Politeness · Deduplication · Fetchers · Parsing · Content store · Recrawl  
> **Style:** End-to-end crawler design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split discover/fetch/parse load classes, politeness as hard constraint, honest JS-render trade-offs

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

Goal: **bound the crawler**—what we fetch, how polite we are, what we store, and at which pages/day the frontier and politeness machinery must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What’s the purpose? | Build a searchable index / research corpus / change monitor | Storage format + recrawl policy follow purpose |
| F2 | Seed URLs? | Editorial seeds + sitemap + continuous discovery from links | Frontier priority from score + discovery graph |
| F3 | Scope? | Public web subset; respect robots.txt; no login walls MVP | Robots cache; skip auth-gated |
| F4 | Content types? | HTML primary; PDF optional; images metadata only MVP | Parser matrix; MIME allowlist |
| F5 | JS rendering? | Optional Phase 2 for selected hosts | Separate render farm; expensive |
| F6 | Dedup? | URL canonicalization + content fingerprint | Bloom/exact URL set; simhash optional |
| F7 | Politeness? | Per-host rate limits; crawl-delay; global politeness | Host queues; never melt a site |
| F8 | Output? | WARC/object store + metadata index (URL, status, links, text) | Immutable snapshots; metadata DB |
| F9 | Recrawl? | Change-aware scheduling by importance & change rate | Priority frontier with next_fetch_at |
| F10 | Abuse handling? | Detect bans/CAPTCHAs; backoff; rotate egress carefully | Ethics + ToS; legal review assumed |

**MVP functional scope (lock with interviewer):**

1. Seed → frontier → fetch → parse → extract links/text → store → enqueue new URLs.  
2. robots.txt + per-host politeness.  
3. URL canonicalization + dedupe.  
4. Retries with backoff for transient errors.  
5. Content in object store (WARC or blob+meta).  
6. Recrawl scheduler for known URLs.  
7. Metrics/dashboards: pages/s, robots denies, 429s, per-host delay.

**Out of MVP:**

- Full Chrome render for all pages  
- Logged-in crawling  
- Perfect global near-duplicate clustering  
- Real-time push index to production search (design hooks only)  
- Malware detonation sandbox  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Throughput | Pages/day primary KPI | Baseline 10M pages/day; design to 10B/day at 1,000× |
| N2 | Politeness | Hard constraint | Default ≤1 concurrent req/host; ≥1s spacing (tunable); honor Crawl-delay |
| N3 | Freshness | Important pages hours–day | Priority tiers; not uniform crawl |
| N4 | Durability | Fetched content not lost | Object store 11-9s; frontier checkpoints |
| N5 | Availability | Crawler can pause; not user-facing | Best-effort continuous operation |
| N6 | Correctness | No unbounded refetch loops | Dedupe + budget + cycle detection |
| N7 | Compliance | robots, ToS, legal | Fail closed on robots disallow |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seed homepage → discover links → polite fetch → parse → store WARC → enqueue children.  
2. Sitemap.xml discovered → burst of URL admits under host budget.  
3. 304 / ETag unchanged → update next_fetch; skip body store.  
4. 429/503 → exponential backoff on host; widen politeness.  
5. robots.txt updates → refresh cache; drop disallowed URLs.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Infinite calendar / facet URLs | URL filters, crawl budget, path depth limits, param allowlist |
| Soft 404 | Heuristics; don’t poison index |
| DNS failures | Negative cache TTL; retry budget |
| Canonical redirect chains | Cap redirects (e.g. 5); canonicalize final URL |
| Duplicate content many URLs | Content hash / simhash; choose canonical |
| Trap (zip bomb, huge HTML) | Size limits; timeouts; parser sandbox |
| Host bans crawler IP | Detect; reduce rate; rotate **only if policy allows** |
| robots unreachable | Fail closed or use last-known per policy (document choice) |
| Parser crash on poison HTML | Isolate; DLQ URL; don’t kill worker fleet |
| Clock skew on next_fetch_at | Use scheduler server time |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Pages fetched / day | 10M | 100M | 1B | 10B |
| Avg fetch QPS | ~115 | ~1.2K | ~12K | ~115K |
| Peak fetch QPS | ~300 | ~3K | ~30K | ~300K |
| Unique URLs known | 100M | 1B | 10B | 100B |
| Hosts actively crawled / day | 1M | 5M | 20M | 50M+ |
| Avg page size downloaded | 50 KB | 50 KB | 50 KB | 50 KB |
| Raw download / day | ~500 TB? wait | | | |
| DNS queries / day | ~5–20M | ×10 | ×100 | ×1000 |
| New links discovered / day | ~50M | ~500M | ~5B | ~50B |
| Parser CPU fleet | tens | hundreds | thousands | tens of thousands |
| Content store growth / day | ~200–500 GB (compressed/text-focused) | ×10 | ×100 | ×1000 |

**Correct download arithmetic:**

```text
10M pages/day × 50 KB = 500 × 10^9 B = 500 GB/day  (not TB)
10B pages/day × 50 KB = 500 TB/day
```

**What each jump forces:**

- **10×:** Distributed frontier; sharded host queues; DNS cache cluster.  
- **100×:** Priority frontier tiers; content-store lifecycle; render farm optional small %.  
- **1,000×:** Geo egress PoPs; per-TLD politeness governance; massive URL DB (Bigtable/Cassandra); bloom layers.

### 1.5 Etc. (Constraints & Assumptions)

- **Legal/ethical crawling** assumed in scope; we design technical politeness.  
- **HTTP(S)** only MVP.  
- **No guarantee** of complete web coverage.  
- **Seed quality** dominates usefulness more than raw QPS.

**Scope statement:**

> Design a distributed web crawler that politely discovers and fetches public pages at 10M→10B pages/day, with a prioritized URL frontier, robots/per-host rate limits, URL/content dedupe, retries, WARC/object storage, and recrawl scheduling—without melting origin sites or the crawler itself.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| **Fetch** HTTP requests | ~115/s avg | ~115K/s | Politeness-limited, not CPU |
| **DNS** lookups | ~50–100/s (cached) | ~50–100K/s | Cache hit rate critical |
| **Parse** pages | ~115/s | ~115K/s | CPU bound |
| **URL admit / dedupe checks** | ~500/s–few K/s | ~0.5–5M/s | Discover >> fetch |
| **robots.txt fetches** | << fetch | scales with hosts | Aggressive cache |
| **Index/metadata writes** | ~115/s | ~115K/s | Separate from raw store |

**Discovery amplification:** one page may yield 50 links → admit path must be cheaper than fetch path.

### 2.2 Frontier memory / storage

```text
URL record: ~100–200 B (url hash, host_id, score, next_fetch, state)
100M URLs × 150 B ≈ 15 GB metadata
100B URLs × 150 B ≈ 15 TB → distributed KV / wide-column
```

### 2.3 Politeness math (the real bottleneck)

```text
If default 1 req / host / second:
  To sustain 115K fetch/s need ≥115K hosts "due" concurrently
At baseline 300 peak QPS: need diverse host set; seed-heavy crawl stalls on few hosts
→ Frontier must interleave many hosts (host-based scheduling)
```

### 2.4 Bandwidth

```text
Baseline avg 115 pages/s × 50 KB ≈ 5.75 MB/s ≈ ~500 GB/day
1,000×: 115K × 50 KB ≈ 5.75 GB/s ≈ ~500 TB/day
Egress IP reputation + provider caps become program risks
```

### 2.5 DNS cache

```text
Without cache: every fetch → DNS → melts resolvers and adds latency
Positive TTL per DNS; negative TTL short (e.g. 60s)
100B URL crawl still maps to << hosts; cache by hostname
```

### 2.6 Storage tiers

```text
Keep: WARC/raw compressed, extracted text, link edges, fetch metadata
Lifecycle: hot 30d → warm → cold glacier; revisit metadata always hot
```

---

## 3. High-Level Design

### 3.1 Pipeline overview

```text
Seeds → URL Normalizer → Dedupe/Admit → Frontier (priority + host queues)
        → Host Scheduler (politeness, robots) → Fetcher Fleet
        → Content Store ← bytes
        → Parser → Link Extractor → back to Admit
                 → Text/Metadata Index
        → Recrawl Scorer → Frontier (next_fetch_at)
```

### 3.2 URL normalization & identity

**Canonicalization rules (examples):**

- Lowercase scheme/host; remove default ports; strip fragments.  
- Sort query params; drop tracking params (`utm_*`).  
- Trailing slash policy per host heuristics.  
- Decode unreserved escapes; IDN punycode.

**URL ID:** `hash64/128(canonical_url)` as primary key.

**Deal-breaker:** treating `http://A` and `https://A/` as always distinct without redirect/canonical logic—wastes budget.

### 3.3 Deduplication

| Layer | Technique | Purpose |
|-------|-----------|---------|
| URL exact | Canonical hash set / KV | Don’t enqueue duplicates |
| URL bloom | In-memory probabilistic | Cheap negative filter at 100×+ |
| Content hash | SHA256 of body | Exact duplicate bodies |
| Near-dup | SimHash / MinHash | Mirror pages / boilerplate |

**Bloom false positives:** may skip a new URL (miss) — acceptable if rare; false negatives impossible with bloom-only (must check exact store on positive).

### 3.4 Frontier & priority

**State machine per URL:**

```text
DISCOVERED → SCHEDULED → IN_FLIGHT → FETCHED / ERROR / DISALLOWED
                ↑            |
                +--- recrawl +
```

**Priority score (example):**

```text
score = w1*importance + w2*change_rate + w3*freshness_need - w4*penalty
importance: PageRank-ish / seed distance / site tier
change_rate: EMA of content-hash changes
```

**Data structure options:**

| Structure | Pros | Cons |
|-----------|------|------|
| Global heap | Simple | Poor politeness; hotspot |
| **Per-host queues + global host heap** | Natural politeness | More moving parts — **chosen** |
| Hierarchical timing wheels | Efficient next_fetch | Complexity |

**Chosen: host-based frontier**

```text
host_heap ordered by next_available_at
each host: priority queue of URLs due
scheduler: pop host → pop URL → assign fetcher → push host back with +delay
```

### 3.5 robots.txt & politeness

```text
On host schedule:
  robots = robots_cache.get(host)  # fetch/parse if stale
  if robots.disallow(path, user_agent): mark DISALLOWED; skip
  delay = max(default_delay, robots.crawl_delay, adaptive_backoff)
  concurrency = min(configured, robots.limits)
```

**Adaptive politeness:** increase delay on 429/503/timeouts; slow decay on success.

**Ownership:** Host scheduler owns rate; fetchers must not bypass.

### 3.6 DNS cache

- Local + shared Redis/DNS cache.  
- Prefetch DNS when host becomes due.  
- Separate DNS timeouts from HTTP timeouts.

### 3.7 Fetcher fleet

```text
Fetcher worker:
  receive (url, host_lease)
  apply timeouts (connect/read), size cap, redirect cap
  record status, headers, timing, final_url
  write payload to object store / WARC
  emit FetchResult event
  release host lease (or scheduler handles delay)
```

**Idempotency:** `fetch_id`; retries use same content key versioning (`url_id + fetch_ts`).

**Retries:** transient 5xx/timeouts → exponential backoff **per host**; 404 → permanent unless recrawl policy says otherwise; 3xx to other hosts → re-admit canonical.

### 3.8 Parser & link extraction

- HTML tokenizer (not regex).  
- Extract: title, text, outlinks, canonical link, nofollow handling policy.  
- Language detection optional.  
- Sandbox CPU/memory per document.

**nofollow / rel policies:** product decision—document whether to crawl.

### 3.9 Content storage

| Format | Pros | Cons |
|--------|------|------|
| WARC files | Standard for web archives | Harder random access |
| Object per fetch + metadata DB | Simple random get | Many small objects |
| Hybrid | WARC batches + metadata index | Ops complexity |

**MVP hybrid:** write objects `s3://crawl/{date}/{url_hash}` + metadata row; batch WARC export async for archive.

### 3.10 Recrawl scheduling

```text
next_fetch_at = now + interval(importance, change_ema, http_cache_headers)
Honor Cache-Control / Expires when present
Unchanged (304): grow interval (capped)
Changed: shrink interval (floored)
```

**Budgets:** daily fetch budget per domain tier to prevent starvation of long-tail hosts (see fairness).

### 3.11 JavaScript rendering (optional)

| Approach | Cost | When |
|----------|------|------|
| No JS | Cheap | MVP |
| Selective headless (Chrome pool) | 10–100× CPU | Allowlisted hosts / detection of empty shell |
| Partner render service | $$$ | Extreme |

**Detection:** empty body + large JS; known SPA hosts. Never default-render all pages at 1,000×.

### 3.12 Anti-ban & reputation

- Stable identifiable User-Agent + contact.  
- IP pools by region; **don’t** present as residential proxy fraud.  
- Per-IP concurrency caps.  
- Ban detection → quarantine host + alert.

---

## 4. Architecture Diagram

### 4.1 System diagram

```text
+--------+    +------------------+    +------------------+
| Seeds  |--->| Admit / Dedupe   |<---| Link Extractor   |
+--------+    +--------+---------+    +--------+---------+
                       v                       ^
              +--------+---------+             |
              | Frontier Service |             |
              | host queues+heap |             |
              +--------+---------+             |
                       v                       |
              +--------+---------+             |
              | Host Scheduler   |             |
              | robots+DNS+delay |             |
              +--------+---------+             |
                       v                       |
              +--------+---------+    +--------+---------+
              | Fetcher Fleet    |--->| Content Store    |
              +--------+---------+    +--------+---------+
                       |                       |
                       v                       v
              +--------+---------+    +------------------+
              | Parser Fleet     |--->| Metadata / Links |
              +------------------+    +------------------+
```

### 4.2 Sequence: fetch one URL

```text
Scheduler: host H due → pop URL U
Scheduler: robots allow? DNS ok?
Scheduler → Fetcher: lease(H, U, deadline)
Fetcher → Origin: GET U
Fetcher → Store: put body
Fetcher → Kafka: FetchResult
Parser: extract links/text
Admit: canonicalize → dedupe → frontier.insert
Scheduler: H.next_available = now + delay(H)
```

### 4.3 Sequence: 429 backoff

```text
Fetcher ← 429 Retry-After: 120
Fetcher → Scheduler: penalize(H, 120s+)
URL → retry queue with attempts++
If attempts > max: ERROR state; recrawl later with low priority
```

### 4.4 Frontier shard map

```text
shard = hash(host) % N
All URLs for a host on same shard → local politeness without cross-shard locks
```

**Deal-breaker:** sharding frontier by URL hash (splits one host across shards → politeness races).

---

## 5. Design Deep Dive

### 5.1 Reliability — hard invariants

| ID | Invariant | Enforcement |
|----|-----------|-------------|
| R1 | Never fetch disallowed by robots (policy) | Scheduler check; fail closed |
| R2 | Per-host politeness respected | Host shard + lease + delay |
| R3 | At-most-one in-flight fetch per URL (lease) | URL state IN_FLIGHT + timeout reclaim |
| R4 | Fetched bytes durable before discover side-effects ack | Store then emit; or outbox |
| R5 | Retries bounded | max_attempts; DLQ |
| R6 | Frontier progress checkpointed | Periodic snapshots / Kafka offsets |
| R7 | Size/time limits on fetch/parse | Hard caps |

**Degradations:**

| Failure | Behavior |
|---------|----------|
| Origin outage | Host backoff; crawl other hosts |
| Store outage | Pause fetch acks; buffer carefully |
| Parser outage | Queue FetchResults; don’t refetch blindly |
| Bloom false positive spike | Fall back to exact KV |
| DNS provider issues | Secondary resolvers; negative cache |

### 5.2 Scalability progressive

**1×:** Few fetcher workers; Postgres frontier; Redis robots/DNS; S3 content.

**10×:** Kafka pipelines; frontier sharded by host; autoscaled fetchers/parsers.

**100×:** Multi-tier priority; URL DB on Bigtable/Cassandra; bloom layers; WARC packers; geo DNS.

**1,000×:** Regional crawl cells (egress locality); hierarchical scheduling; dedicated politeness governance; selective render; lifecycle deletion.

**Starvation prevention:**

- Reserve % budget for exploration (new hosts).  
- Per-host caps so wikipedia doesn’t consume entire fleet.  
- Aging: boost URLs waiting too long.

### 5.3 Maintainability

- Connector-like **protocol plugins** (HTTP).  
- Integration tests with mock origins.  
- Crawl quality scorecards: useful pages %, error mix, robots denies.  
- Config as code: delay tables, UA, param strip lists.  
- Poison URL kill switches.

### 5.4 Ownership resolution

| Concern | Owner |
|---------|-------|
| Politeness & robots | Host scheduler |
| URL uniqueness | Admit/dedupe service |
| Raw bytes | Content store |
| Link graph / metadata | Metadata DB |
| Recrawl intervals | Scoring service |
| IP reputation | Egress / SRE policy |

### 5.5 Change detection

- ETag / Last-Modified / 304.  
- Content hash compare.  
- Ignore volatile regions (timestamps, ads) via DOM templates if advanced.

### 5.6 Security of the crawler itself

- SSRF: block link-local, metadata IPs, private ranges unless allowlisted.  
- Parser isolation (memory limits).  
- Secrets never logged from query strings.

---


### 5.7 URL filtering & spider-trap defense

| Defense | Mechanism |
|---------|-----------|
| Max depth from seed | Drop links beyond D |
| Path segment caps | Reject URLs with >N `/` or repeated segments |
| Query param allowlist | Per-host config; strip sorts/sessions |
| Crawl budget / domain | Daily page cap by PLD |
| Exact URL bloom + KV | Stop re-admit storms |
| Content-seen budget | If same hash from host too often, demote |
| Regex denylist | Admin-maintained trap patterns |

**Calendar traps:** detect `\d{4}/\d{2}/\d{2}` explosions; require sitemap corroboration for deep dates.

### 5.8 Link graph & importance scoring

MVP can use **seed distance** + site tier. At 100×, maintain a lightweight authority score:

```text
importance(u) ≈ α * seed_prior(host) + β * log(1+in_degree) + γ * historical_click_or_index_use
```

Recompute asynchronously (daily) so the fetch path stays lean. Never block fetch on global PageRank.

### 5.9 Recrawl policy examples

| Tier | Example | Interval |
|------|---------|----------|
| News homepage | cnn.com/ | 5–15 min |
| Popular article | high traffic | 1–6 h while hot, then days |
| Corporate about page | stable | 7–30 days |
| Long-tail blog | low change EMA | 30–90 days |

Use HTTP validators to cheaply confirm unchanged. Cap minimum interval to protect origins.

### 5.10 Observability & SLOs

| SLO / metric | Why |
|--------------|-----|
| Fetch success rate (2xx/3xx) | Health |
| 429/503 rate per host & global | Politeness / ban signals |
| robots deny rate | Scope / UA issues |
| Frontier lag (due URLs overdue) | Scheduler capacity |
| Parse error rate | Poison / bugs |
| Bytes downloaded / day | Cost |
| Unique hosts fetched / day | Diversity (anti-melting) |
| Duplicate fetch ratio | Dedupe quality |

**Alert:** sudden drop in host diversity with stable QPS → you may be hammering few hosts (bug).

### 5.11 Multi-region crawl cells

```text
Cell us-east: prefer hosts with DNS/geo affinity; store in regional bucket
Cell eu-west: GDPR-sensitive collection policies
Global URLDB: logical; physical shards; host ownership pinned to one cell
```

**Ownership:** each host assigned a home cell for politeness continuity; migrate carefully.

### 5.12 Legal / compliance hooks (technical)

- Honor `robots.txt` and `noindex` per product policy (crawl vs index separation).  
- Retain take-down / exclusion lists.  
- Log fetch justification for audits.  
- Separate **crawl** rights from **index/serve** rights.

---

## 6. Wrap-Up

### 6.1 Whiteboard order

1. Pipeline boxes + host-sharded frontier.  
2. Politeness math (hosts needed for QPS).  
3. Dedupe layers.  
4. Store + recrawl.  
5. Scale jumps + JS as expensive optional.

### 6.2 MVP → scale

| Phase | Ship |
|-------|------|
| MVP | Host queues, robots, fetch/parse/store, URL dedupe |
| 10× | Kafka, sharded frontier, DNS cache |
| 100× | Priority/recrawl EMA, bloom, WARC batches |
| 1,000× | Geo cells, lifecycle, selective render |

### 6.3 Top risks

1. Melting a small host (politeness bug).  
2. Spider traps exhausting frontier.  
3. Frontier sharded by URL not host.  
4. Treating JS-render as default.  
5. Incorrect GB/TB arithmetic in estimates.

### 6.4 One-sentence design

> A host-sharded, politeness-first crawler with prioritized recrawl, layered URL/content dedupe, and a fetch→store→parse→admit loop that scales pages/day by adding host diversity and fleets—not by slamming single origins.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & ethics

**Q: What’s more important: QPS or politeness?**  
A: Politeness is a hard constraint; QPS is maximized under that constraint via host diversity.

**Q: How do you identify your crawler?**  
A: Clear User-Agent + project URL/contact; honor robots for that UA.

**Q: robots.txt offline—fetch or skip?**  
A: Pick a policy and state it: commonly use cached copy or fail closed for safety.

### 7.2 Frontier

**Q: Why not one global priority queue?**  
A: High-priority URLs may concentrate on few hosts → politeness stall / unfairness. Host-based scheduling interleaves.

**Q: How to shard the frontier?**  
A: By host (or pay-level domain) so politeness state is local.

**Q: How to prevent starvation of low-priority URLs?**  
A: Aging boosts; reserved exploration budget; per-host caps.

**Q: Crawl budget?**  
A: Max pages per domain per day; depth limits; overall daily quota.

### 7.3 Dedup & canonicalization

**Q: Bloom filter parameters?**  
A: Size for expected URLs + target FP rate; rebuild/rotate layers; exact check on positive.

**Q: Redirect to new host—what happens to politeness?**  
A: Charge both hosts appropriately; admit final URL under destination host queue.

**Q: WWW vs apex?**  
A: Canonical via redirects/sitemap; store alias map.

**Q: Content duplicate across URLs?**  
A: Prefer canonical link relation; keep one primary; others alias.

### 7.4 Fetching & networking

**Q: Connection reuse?**  
A: HTTP keep-alive pools per host within concurrency caps.

**Q: Timeout values?**  
A: Short connect (e.g. 2–5s), read caps; don’t hold host leases forever.

**Q: How many redirects?**  
A: Cap (3–5); detect loops via set of URLs in chain.

**Q: HTTP/2 / HTTP/3?**  
A: Optional optimization; politeness still on request units/host.

**Q: DNS amplification risk?**  
A: Cap outstanding lookups; cache; resolve only for scheduled hosts.

### 7.5 Parsing & JS

**Q: Regex HTML parsing?**  
A: Insufficient; use a tokenizer/DOM. Interviewers ding regex-only.

**Q: When to use headless Chrome?**  
A: When HTML shell empty and host important; never default at scale.

**Q: Cost of rendering?**  
A: Often 10–100× vs static fetch; tiny % of traffic.

### 7.6 Storage & recrawl

**Q: WARC vs object-per-page?**  
A: WARC good for archive continuity; objects good for random access—hybrid common.

**Q: How to schedule recrawl?**  
A: Importance × change rate; honor validators; exponential backoff when stable.

**Q: How much history to keep?**  
A: Product-dependent; metadata forever (cheap), bodies with lifecycle.

### 7.7 Scale & failure

**Q: Fetcher vs parser ratio?**  
A: Fetch often network-bound; parse CPU-bound—autoscale independently (split classes).

**Q: Poison page kills parsers?**  
A: Isolate process; memory limit; DLQ; don’t refetch infinitely.

**Q: Kafka lag on parse?**  
A: Scale parsers; do not increase fetch into unbounded store backlog without backpressure.

**Q: How does 10B pages/day change architecture?**  
A: Geo cells, huge URLDB, bloom, host-sharded schedulers, lifecycle, governance.

### 7.8 Abuse & bans

**Q: Site returns CAPTCHA?**  
A: Mark host needs_js or blocked; backoff; human policy—don’t automate CAPTCHA bypass in standard design interviews unless asked.

**Q: IP rotation strategy?**  
A: Modest pools for capacity/geo; not stealth. Reputation > anonymity.

### 7.9 Comparison traps

**Q: How is this different from scraping one site?**  
A: Multi-host scheduling, discovery, recrawl, and politeness dominate.

**Q: How is this different from wget recursive?**  
A: Distributed state, dedupe at web scale, continuous operation, metrics, legal/robots.

**Q: Can you use only a message queue as frontier?**  
A: Weak priority/politeness; need host-aware scheduling state.

### 7.10 Extra interviewer traps (high value)

- Show pages/day → QPS arithmetic correctly.  
- 10M × 50KB = 500GB/day not 500TB.  
- Why shard by host not URL?  
- What happens on 429?  
- How do you stop calendar traps?  
- Is bloom enough alone?  
- Where is robots enforced?  
- How do you reclaim IN_FLIGHT after worker death?  
- What’s the backpressure signal from store/parser to fetchers?  
- When do you refetch vs 304?  
- How do you compute hosts needed for target QPS at 1 req/host/s?  
- SSRF from user-submitted seeds?  
- How do sitemaps interact with politeness?  
- What metrics indicate you’re melting origins?  
- Why is JS render not the default?

---

## Appendix A — Example metadata schema

```sql
CREATE TABLE urls (
  url_id BYTEA PRIMARY KEY,         -- 16B hash
  canonical_url TEXT NOT NULL,
  host_id BIGINT NOT NULL,
  state TEXT NOT NULL,
  priority DOUBLE PRECISION NOT NULL,
  next_fetch_at TIMESTAMPTZ,
  attempts INT NOT NULL DEFAULT 0,
  last_status INT,
  last_fetch_at TIMESTAMPTZ,
  content_hash BYTEA,
  change_ema DOUBLE PRECISION NOT NULL DEFAULT 0.5,
  depth INT NOT NULL DEFAULT 0
);
CREATE INDEX urls_host_next ON urls (host_id, next_fetch_at) WHERE state = 'SCHEDULED';

CREATE TABLE hosts (
  host_id BIGSERIAL PRIMARY KEY,
  hostname TEXT UNIQUE NOT NULL,
  next_available_at TIMESTAMPTZ NOT NULL,
  delay_ms INT NOT NULL DEFAULT 1000,
  concurrent_max INT NOT NULL DEFAULT 1,
  penalty_until TIMESTAMPTZ,
  robots_fetched_at TIMESTAMPTZ,
  robots_body TEXT
);

CREATE TABLE fetches (
  fetch_id UUID PRIMARY KEY,
  url_id BYTEA NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL,
  status INT,
  final_url TEXT,
  object_key TEXT,
  bytes INT,
  content_type TEXT,
  etag TEXT
);
```

## Appendix B — Event envelopes

```json
{
  "type": "FetchResult",
  "fetch_id": "f_...",
  "url_id": "hex...",
  "host": "example.com",
  "status": 200,
  "object_key": "s3://crawl/2026/08/05/...",
  "bytes": 48221,
  "content_hash": "sha256...",
  "discovered_links": 42
}
```

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Host queues, robots, fetch/parse/store, URL dedupe |
| 10× | Kafka, host-sharded frontier, shared DNS cache |
| 100× | Priority/recrawl EMA, bloom, WARC packers, domain budgets |
| 1,000× | Geo crawl cells, URLDB at 100B, lifecycle, selective render |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Frontier | URLs waiting/scheduled to fetch |
| Politeness | Per-host rate/concurrency limits |
| WARC | Web ARChive file format |
| Canonical URL | Normalized identity for dedupe |
| Host lease | Permission to fetch under politeness window |
| Soft 404 | 200 OK with not-found content |
| Spider trap | Explosive URL generator |
| Recrawl | Refetch known URL on schedule |
| Pay-level domain | Registrable domain used for budgeting |
| IN_FLIGHT | URL currently being fetched |

## Appendix E — Estimation cheat-sheet

```text
avg_QPS ≈ pages_per_day / 86400
10M/day ≈ 116/s; 10B/day ≈ 115,741/s

bytes/day ≈ pages/day × avg_bytes
10M × 50KB = 500 GB/day
10B × 50KB = 500 TB/day

If 1 req/host/s: need ~QPS distinct hosts due in parallel

Discover checks/s >> fetch/s  (links per page)

Parser and fetcher scale independently
```

---

*End of design doc. Open with §1 politeness + scope; whiteboard §3.4 host frontier + §3.5 robots; close with invariants §5.1 and traps §7.*
