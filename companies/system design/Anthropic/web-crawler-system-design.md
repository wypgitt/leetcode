# System Design: Web Crawler (Concurrent Crawler)

> **Focus areas:** Traversal · Deduplication · Bounded concurrency · Failures · Politeness · Frontier  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split discover/fetch/parse/store classes, **politeness as hard constraint**, honest JS-render trade-offs  
> **Interview theme:** Ordinary distributed-systems fundamentals inside unfamiliar AI infrastructure — reliability, consistency, concurrency, cost; note RAG / training / safety-research corpora as *uses*, but crawler fundamentals stay first-class

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

Goal: **bound the crawler**—seed → frontier → polite fetch → parse → dedupe → store → discover, with bounded concurrency and principled failure handling. Downstream may feed **RAG indexes, training/pretraining corpora, or safety research datasets**, but the interview is won on frontier, politeness, dedupe, and scale—not on embedding model choice.

### 1.0 Purpose framing (say early)

| Use | Implication | Still the same crawler core? |
|-----|-------------|------------------------------|
| Search index | Freshness + ranking signals | Yes |
| RAG corpus | Quality filters, license, chunking later | Yes |
| Training data | Scale, dedupe, toxicity/safety pipelines later | Yes |
| Safety research | Policy on harmful content retention | Yes |

**Scope statement:** Design a **distributed concurrent web crawler** with politeness, dedupe, bounded concurrency, and durable outputs—optionally feeding AI corpora.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Purpose? | Corpus / index / change monitor | Storage + recrawl policy |
| F2 | Seeds? | Editorial + sitemaps + continuous link discovery | Frontier priorities |
| F3 | Scope? | Public web subset; robots.txt; no login MVP | Robots cache; allowlists |
| F4 | Content? | HTML primary; PDF optional | Parser matrix; MIME allowlist |
| F5 | JS render? | Phase 2 selected hosts | Separate render farm |
| F6 | Dedupe? | URL canonical + content fingerprint | Bloom/exact + simhash optional |
| F7 | Politeness? | Per-host limits; Crawl-delay; global caps | Host queues **hard** |
| F8 | Output? | WARC/blobs + metadata (URL, status, links, text) | Immutable snapshots |
| F9 | Recrawl? | Importance × change rate | `next_fetch_at` scheduler |
| F10 | Concurrency? | High global; low per host | Two-level limits |
| F11 | Failures? | Retry transient; DLQ poison | Backoff; budgets |
| F12 | Compliance? | robots, ToS, legal review assumed | Fail closed on disallow |

**MVP functional scope:**

1. Seed → frontier → fetch → parse → extract links/text → store → enqueue.  
2. robots.txt + per-host politeness (hard).  
3. URL canonicalization + dedupe.  
4. Bounded global concurrency + per-host concurrency (often 1).  
5. Retries with exponential backoff; respect 429/Retry-After.  
6. Content to object store; metadata index.  
7. Recrawl scheduler.  
8. Metrics: pages/s, 429s, robots denies, queue age, per-host delay.

**Out of MVP:**

- Full Chrome for all pages  
- Logged-in crawling  
- Perfect global near-duplicate clustering  
- Online embedding/index build (hooks)  
- Malware detonation  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Throughput | Pages/day KPI | Baseline 10M/day → 10B/day at 1,000× |
| N2 | Politeness | **Hard constraint** | Default ≤1 concurrent/host; ≥1s spacing; honor Crawl-delay |
| N3 | Freshness | Tiered | Important pages hours–day |
| N4 | Durability | Fetched bytes kept | Object store; frontier checkpoints |
| N5 | Availability | Best-effort continuous | Can pause; not user-facing SLO |
| N6 | Correctness | No unbounded loops | Budgets, dedupe, depth limits |
| N7 | Compliance | robots / legal | Fail closed |
| N8 | Cost | Bandwidth + parse CPU + store | Dedup & recrawl intelligence |

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
- AI corpus use adds license/PII/safety **post-pipelines**—mention as downstream, don’t derail MVP.  
- Ethical defaults: honor robots; identify UA; provide contact.

**Scope statement:**

> Design a concurrent distributed web crawler: politeness-first host scheduling, URL/content dedupe, bounded global and per-host concurrency, robust failure/backoff, durable WARC/metadata output, and recrawl—scaling 10M→10B pages/day—usable for RAG/training/safety corpora without confusing those products with the crawler itself.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Discover/enqueue** | URL admits | ~few× fetch | ×10 | Frontier |
| **Fetch** | HTTP GETs | ~115 avg QPS | ×10 | Fetcher + egress |
| **Parse** | HTML → links/text | ~fetch rate | ×10 | CPU |
| **Dedupe checks** | URL+content | ~enqueue+fetch | ×10 | Bloom/DB |
| **Store** | WARC/bytes | GB/day | ×10 | Object store |
| **Robots fetch** | Per host rare | << fetch | ×10 | Cache |

**Anti-pattern:** one “QPS” mixing fetch, parse, and frontier DB writes.

### 2.2 Politeness caps throughput

```text
If 1M hosts, 1 req / host / 2s theoretical → 500K QPS
Reality: active hosts << total; many hosts idle
Bottleneck often: popular hosts (wikipedia-class) under strict politeness
Global QPS ≠ per-host freedom
```

**Interview line:** you cannot “just add workers” past politeness; you need more **hosts in frontier**, not more hammers on one host.

### 2.3 Bandwidth

```text
10M pages/day × 50 KB avg ≈ 500 GB/day raw
100× → ~50 TB/day
Plus WARC overhead; dedupe saves re-fetch not first fetch
```

### 2.4 Frontier storage

```text
100M URLs × 200 B ≈ 20 GB
10B URLs × 200 B ≈ 2 TB (+ indexes)
Need sharded frontier store
```

### 2.5 Render cost (Phase 2)

```text
Headless render ≫ static fetch (10–100× CPU/RAM)
Keep render allowlist tiny
```

---

## 3. High-Level Design

### 3.1 Pipeline

```text
Seeds/Sitemaps → URL Canonicalize → Dedupe admit
    → Frontier (priority, next_fetch_at, host)
    → Politeness Scheduler (per-host tokens)
    → Fetcher (bounded concurrency)
    → Parser / Link Extractor
    → Content Dedupe → Store (WARC + meta)
    → Enqueue new URLs + Schedule recrawl
```

### 3.2 Domain model

```text
URLRecord
  url_canonical, host, priority, depth, discover_parent
  next_fetch_at, last_etag, last_hash, fail_count
  state: pending|in_flight|done|banned|dlq

HostState
  robots_rules, crawl_delay, next_slot_at
  concurrent_in_flight, backoff_until
  budget_remaining (daily)

FetchResult
  status, headers, body_ref, fetched_at, redirects

Document
  content_hash, text, outlinks[], lang, mime
```

### 3.3 Frontier design

| Structure | Pros | Cons |
|-----------|------|------|
| Global priority queue | Simple | Hot lock; politeness hard |
| **Per-host queues + global host scheduler** | Politeness natural | More moving parts |
| Disk-backed PQ (host-sharded) | Scale | Complexity |

**Chosen:** **host-sharded frontier**: each shard owns set of hosts; within host, priority queue by score/`next_fetch_at`.

### 3.4 Politeness (hard)

| Rule | Default MVP |
|------|-------------|
| Max concurrent requests/host | 1 |
| Min spacing | max(1s, Crawl-delay) |
| Global concurrent fetches | Config cap (e.g. 10K) |
| robots.txt | Honor Disallow; fail closed if required |
| 429/Retry-After | Honor; increase delay |
| Identify UA | Clear bot UA + contact |

**Deal-breaker:** global worker pool that picks any URL without host tokenization → accidental DDoS.

### 3.5 Deduplication

| Layer | Mechanism |
|-------|-----------|
| URL | Canonicalize (scheme, host lower, strip fragment, sort query allowlist) |
| URL seen | Bloom + exact RocksDB/KV |
| Content | Fingerprint (xxhash/sha); optional simhash near-dup |
| Redirect | Map aliases → canonical |

### 3.6 Bounded concurrency

```text
Two levels:
  global_semaphores: max_in_flight_fetches
  per_host_semaphores: usually 1
Plus parse pool concurrency separate from fetch
Never let parse backlog OOM — backpressure to fetch
```

### 3.7 Failure & retry

| Error | Action |
|-------|--------|
| DNS/timeout/5xx | Exp backoff; fail_count++; eventually DLQ |
| 404/410 | Done; rare recrawl |
| 429/503 | Host backoff; don’t burn fail_count same way |
| robots disallow | Drop |
| Parse exception | DLQ URL; keep raw body if stored |
| Truncated body | Retry once; else DLQ |

### 3.8 Storage outputs

| Artifact | Use |
|----------|-----|
| WARC / object bytes | Raw evidence |
| Metadata DB | URL, status, hashes, links |
| Outlink edges | Optional graph |
| Text extract | Downstream RAG/training (separate jobs) |

### 3.9 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Frontier | Per-host queues | Politeness | Global only PQ |
| Concurrency | Global + per-host | Scale without abuse | Unbounded workers |
| Dedupe | URL + content | Save $ & loops | URL only |
| JS render | Opt-in Phase 2 | Cost | Render everything |
| Recrawl | Priority schedule | Freshness ≠ uniform | Round-robin all URLs |
| robots | Fail closed default | Compliance | Ignore robots |

---

## 4. Architecture Diagram

```text
  Seeds / Sitemap consumers
            |
            v
  +---------+----------+
  | URL Normalizer &   |
  | Dedupe Admit       |---- Seen URL store (Bloom+KV)
  +---------+----------+
            |
            v
  +---------+----------+
  | Frontier Shards    |  host -> PQ(next_fetch_at, priority)
  +---------+----------+
            |
            v
  +---------+----------+
  | Politeness Engine  |  tokens / crawl-delay / backoff
  | HostState cache    |  robots cache
  +---------+----------+
            |
            v
  +---------+----------+     +----------------+
  | Fetcher Fleet      |---->| Egress / DNS   |
  | global concurrency |     +----------------+
  +---------+----------+
            |
            v
  +---------+----------+
  | Parse Workers      |---- backpressure ----
  +---------+----------+
            |
      +-----+------+
      v            v
  Store (WARC)   Link Enqueue -> Dedupe Admit
  Meta DB
            |
            v
  Recrawl Scheduler updater
```

**Per-host scheduling sketch:**

```text
loop:
  pick host with next_slot_at <= now and in_flight < max
  pop best URL from host queue
  acquire global slot
  fetch async
  on complete: release slots; set next_slot_at = now + delay
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Politeness invariant:** never exceed per-host concurrency/spacing policies.  
2. **At-least-once fetch OK;** exactly-once not required—dedupe store handles repeats.  
3. **Frontier checkpointed**; crash resumes without silent loss of seeds (may refetch).  
4. **Poison URLs isolated** in DLQ.  
5. **robots deny ⇒ no fetch**.

#### 5.1.2 Exactly-once vs at-least-once

Crawlers are naturally **at-least-once**. Use content hash to skip re-store; idempotent meta updates.

#### 5.1.3 Backpressure

```text
If parse queue > high_watermark: pause scheduling new fetches
If object store slow: same
Never drop politeness to “catch up”
```

#### 5.1.4 Checkpointing

Frontier shards flush `next_fetch_at` and in-flight lists. In-flight on crash → requeue (at-least-once).

#### 5.1.5 Progressive reliability

| Scale | Focus |
|-------|-------|
| Baseline | Single region; Redis/RQ frontier OK-ish |
| 10× | Durable sharded Kafka/queues + KV frontier |
| 100× | Host-affine fetchers; isolated parse crashes |
| 1,000× | Cell isolation; per-cell DLQ; legal kill switches |

### 5.2 Scalability

#### 5.2.1 Sharding key

**Shard by host** (or pay-level domain) so politeness state colocates with queue. Avoid sharding by URL hash alone (splits host across workers → coordination hell).

#### 5.2.2 Scheduler scalability

| Scale | Design |
|-------|--------|
| Baseline | One scheduler process per shard |
| 10× | Many shards; consistent hash hosts → shard |
| 100× | Fetcher pulls from local shard only |
| 1,000× | Cells by host hash ranges |

#### 5.2.3 Dedupe scalability

- Cascading bloom (daily) + exact KV for positives.  
- Content hashes in columnar store.  
- Near-dup (simhash) batch offline at large scale.

#### 5.2.4 DNS & egress

DNS cache per worker; connection pools per host carefully (still politeness). Multiple egress IPs for **scale across hosts**, not to evade bans silently.

#### 5.2.5 Recrawl

Score = importance × change_probability / cost.  
Use Last-Modified/ETag. Dynamic pages shorter period; static longer.

#### 5.2.6 Cost

| Lever | Effect |
|-------|--------|
| Dedupe | Less store/fetch |
| 304 | Less bandwidth |
| Smart recrawl | Less waste |
| No blanket render | Huge $ save |
| Compression WARC | Store $ |

#### 5.2.7 Progressive scale changes

| Jump | Change |
|------|--------|
| →10× | Host-sharded frontier; bloom |
| →100× | Geo cells; offline near-dup; render farm small |
| →1,000× | Corpus platform separate; crawler cells; strict budgets |

### 5.3 Maintainability

#### 5.3.1 Config as policy

Allow/deny lists, budgets, politeness defaults, MIME allowlist—reviewed configs with audit.

#### 5.3.2 Observability

pages/s, bytes/s, 429 rate, robots deny, queue age p99, per-host delay histogram, DLQ growth, parse errors, duplicate skip rate.

#### 5.3.3 Testing

- Trap URL generators (infinite calendars).  
- robots unit tests.  
- Chaos: DNS fail, 429 storms.  
- Politeness integration test: assert spacing.

#### 5.3.4 Downstream AI hooks (keep brief)

- Emit clean WARC + license hints → offline pipeline for RAG/training/safety.  
- Crawler does **not** embed documents in MVP.  
- Safety retention policies may delete classes of content post-hoc.

#### 5.3.5 Operability

Kill switch per host/TLD; drain shard; replay DLQ; seed importer; sitemap discovery job.

---

## 6. Wrap-Up

### 6.1 What we designed

A **politeness-first concurrent crawler** with host-sharded frontier, URL/content dedupe, two-level concurrency limits, backoff/DLQ, durable WARC/metadata, and recrawl scheduling—scalable to billions of pages/day, usable as the ingestion front for AI corpora without merging those systems into the crawler design.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Politeness | Hard constraint > throughput vanity |
| Frontier | Per-host queues |
| Dedupe | URL + content |
| Concurrency | Global ∩ per-host |
| Render | Rare, expensive |
| Exactly-once | Not needed; at-least-once + idempotent store |

### 6.3 Closing line

> “Crawlers are scheduling and politeness systems that happen to speak HTTP—the AI corpus story is a downstream consumer; if you melt hosts or ignore robots, you fail the interview before embeddings come up.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Traversal & frontier

**Q1: BFS vs priority crawl?**  
A: Pure BFS wastes budget on junk; score by rank/importance/change.

**Q2: How do you avoid traps?**  
A: Depth limits, param allowlists, per-host budgets, session-id stripping.

**Q3: Sitemap vs link discovery?**  
A: Sitemaps accelerate coverage; links find the long tail.

**Q4: Why shard by host?**  
A: Colocate politeness state and queue; avoid split-brain delays.

**Q5: Frontier too large?**  
A: Drop low-score URLs; disk queues; sample discovery.

### 7.2 Politeness

**Q6: Is politeness negotiable for throughput?**  
A: No in reputable designs; legal/ethics/IP bans.

**Q7: Crawl-delay missing?**  
A: Use default spacing; adaptive if 429s.

**Q8: Multiple IPs to go faster on one host?**  
A: Generally treated as evasion—policy/legal no unless explicit permission.

**Q9: Global QPS cap why?**  
A: Protect own egress/DNS/parse; complement per-host.

**Q10: robots unreachable?**  
A: Document fail-closed vs last-known; many choose fail-closed for safety.

### 7.3 Deduplication

**Q11: Canonicalization examples?**  
A: `HTTP://A.com/x?b=1&a=2` → `http://a.com/x?a=2&b=1` (policy-dependent query).

**Q12: Bloom false positives?**  
A: OK to under-crawl; exact KV for critical; or reverse: bloom for “maybe seen” then check exact.

**Q13: Content vs URL dedupe?**  
A: Same content many URLs—keep canonical, skip store duplicates.

**Q14: Near-duplicates?**  
A: Simhash/MinHash offline; expensive online.

### 7.4 Concurrency

**Q15: Why bound parse separately?**  
A: HTML parse CPU-heavy; unbounded fetch→OOM queues.

**Q16: Async IO vs thread per fetch?**  
A: Evented/async for high connection counts; still host limits.

**Q17: Head-of-line blocking per host?**  
A: One slow URL delays host—timeouts mandatory.

**Q18: How to pick next host?**  
A: Earliest `next_slot_at` among hosts with pending URLs; fairness so tiny hosts aren’t starved (weighted).

### 7.5 Failures

**Q19: Retry storms?**  
A: Per-URL budget; per-host backoff; jitter.

**Q20: DLQ?**  
A: Poison / persistent fails for human/policy review.

**Q21: Partial WARC write?**  
A: Write temp + commit meta; or WARC with length checks.

**Q22: Fetcher crash in-flight?**  
A: Lease timeout → requeue URL.

### 7.6 Recrawl & freshness

**Q23: Uniform crawl interval?**  
A: Wasteful; use change signals + importance.

**Q24: ETag handling?**  
A: Conditional GET; on 304 update schedule only.

**Q25: News vs docs?**  
A: Separate priority tiers / politeness pools optional.

### 7.7 AI corpus angles (keep secondary)

**Q26: How does this feed RAG?**  
A: Offline jobs read WARC → cleanse → chunk → embed → vector index. Not crawler MVP.

**Q27: Training data concerns?**  
A: License, PII, toxicity filters downstream; crawler may record license headers/signals.

**Q28: Safety research corpora?**  
A: Retention & access controls stricter; still same fetch/politeness core.

**Q29: Why not crawl inside the LLM app?**  
A: Separation of concerns; politeness/caching/legal need a platform.

### 7.8 JS rendering

**Q30: When render?**  
A: Hosts known app-shell; budgeted; never default.

**Q31: Cost?**  
A: Orders of magnitude more RAM/CPU; separate pool.

### 7.9 Scalability scenarios

**Q32: 10B pages/day?**  
A: ~115K avg QPS; host sharding cells; massive egress; politeness still binds popular hosts.

**Q33: 100B frontier URLs?**  
A: Disk-backed queues; score truncation; multi-tier seen-store.

**Q34: One host dominates score?**  
A: Per-host budget so it can’t consume global capacity.

### 7.10 Alternatives & deal-breakers

**Q35: Scrapy on one box?**  
A: Fine small; won’t hit distributed politeness/frontier scale.

**Q36: Ignore robots for “research”?**  
A: Interview deal-breaker ethically/legally in most settings.

**Q37: Store only embeddings?**  
A: Lose evidence/reprocess; keep raw WARC.

### 7.11 Interview craft

**Q38: How to open?**  
A: Purpose, politeness rules, page/day target, JS or not—then draw host-queued frontier.

**Q39: What arithmetic?**  
A: Pages/day→QPS; bandwidth; frontier bytes; show politeness caps ≠ worker count.

---

### Appendix A — Canonicalization checklist

```text
- lowercase scheme/host
- remove default ports
- remove fragments
- resolve dot segments
- optional: strip tracking params (utm_*)
- stable query param order
- trailing slash policy (host-specific)
```

### Appendix B — Scheduler pseudocode

```text
function schedule():
  while true:
    host = host_heap.pop_ready(now)
    if global_in_flight >= GLOBAL_MAX: sleep; continue
    if host.in_flight >= host.max_conc: reheap; continue
    url = host.queue.pop()
    if url is None: continue
    host.in_flight++
    global_in_flight++
    async fetch(url, on_done)
    host.next_slot_at = now + host.delay
    host_heap.push(host)

function on_done(result):
  host.in_flight--; global_in_flight--
  if retryable: requeue with backoff
  else: parse_async(result)
```

### Appendix C — Progressive scale table

| Scale | Frontier | Fetchers | Dedupe | Store |
|-------|----------|----------|--------|-------|
| Baseline | Few shards | Hundreds | Bloom+KV | Single bucket |
| 10× | Many host shards | Thousands | Cascading bloom | Partitioned |
| 100× | Cells | Host-affine | Offline near-dup | Multi-region |
| 1,000× | Many cells | 100K+ | Dedup platform | Corpus lake |

### Appendix D — Metrics

| Metric | Why |
|--------|-----|
| fetch_qps | Throughput |
| pages_per_day | KPI |
| http_429_rate | Politeness pressure |
| robots_deny | Scope |
| frontier_age_p99 | Freshness lag |
| dlq_size | Poison |
| duplicate_skip_rate | Dedupe value |
| parse_backlog | Backpressure |

### Appendix E — NFR card

```text
Politeness: ≤1 concurrent/host default; honor Crawl-delay & 429
Throughput: design 10M→10B pages/day with host sharding
At-least-once fetch; idempotent store
Fail closed on robots deny (MVP policy)
Raw WARC retained for reprocess
```

### Appendix F — Worked numbers

```text
10M pages/day / 86400 ≈ 116 QPS average
Peak 5× → ~500 QPS
50 KB × 10M ≈ 500 GB/day
Frontier 100M × 200 B ≈ 20 GB
1M hosts with 1 req/2s theoretical 500K QPS — but active subset & skew dominate
```

### Appendix G — URL state machine

```text
discovered -> admitted -> scheduled -> in_flight
    -> fetched_ok -> parsed -> done
    -> retry_wait -> scheduled
    -> dlq / banned / robots_blocked
```

### Appendix H — Pushbacks

| Pushback | Response |
|----------|----------|
| “Add more workers” | Politeness-bound |
| “Render all JS” | Cost blowup |
| “Skip robots” | Deal-breaker |
| “Exactly-once crawl” | Unnecessary; dedupe |
| “Design the vector DB” | Downstream; keep crawler |

### Appendix I — Related systems

| System | Relation |
|--------|----------|
| File store | WARC destination |
| File cache | Optional for robots/static |
| RAG indexer | Consumer of extracts |
| Safety classifiers | Post-pipeline |
| Change monitor | Recrawl specialization |

### Appendix J — Non-goals

- Login/session crawling MVP  
- Full web archive parity with Internet Archive  
- Online embeddings  
- Breaking CAPTCHA  

### Appendix K — robots cache

```text
Get robots.txt at most every TTL (e.g. 24h) or on 404/change
Parse Allow/Disallow/Crawl-delay/Sitemap
Negative cache failures carefully
```

### Appendix L — Content fingerprint flow

```text
body -> hash
if hash seen: link meta to canonical doc; skip WARC duplicate optional
else: store WARC; index hash
```

### Appendix M — 30s narrative

> Host-sharded frontier with politeness tokens, global concurrency caps, URL/content dedupe, and at-least-once fetch into WARC. 10× shards the frontier; 100× cells and offline near-dup; 1,000× is a corpus platform consuming crawler output. AI use cases ride the WARC—they don’t redefine politeness.

### Appendix N — Seed policy

| Source | Notes |
|--------|-------|
| Editorial allowlist | High trust |
| Sitemaps | From robots |
| RSS/Atom | Freshness |
| Link discovery | Long tail; budgeted |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Frontier | URLs waiting to be fetched |
| Politeness | Per-host rate/concurrency limits |
| WARC | Web ARChive file format |
| Pay-level domain | eTLD+1 style host aggregation |
| DLQ | Dead letter queue |
| Near-dup | Similar but not identical content |

### Appendix P — Ethical checklist (say aloud)

```text
- Honor robots.txt
- Clear User-Agent + contact
- Default conservative rates
- No credential stuffing / login walls MVP
- Legal review for corpus redistribution
```

### Appendix Q — Backoff formula

```text
delay = min(max_delay, base * 2^fail_count) + jitter
on 429: delay = max(delay, Retry-After)
host.backoff_until = now + delay
```

### Appendix R — Parse backpressure

```text
if parse_queue_depth > H:
  pause_host_scheduler = true
elif parse_queue_depth < L:
  pause_host_scheduler = false
```

---

*End of Web Crawler system design.*
