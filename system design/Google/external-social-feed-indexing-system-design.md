# System Design: External Social-Feed Indexing

> **Focus areas:** Crawl/stream ingest · Rate limits · Backfill vs realtime · Inverted index · Entity extraction · Dedup · Schema evolution · Search vs timeline · Legal/ToS · Media vs metadata · Ranking features · Idempotent ingest · Watermark lag · Time/id sharding  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split crawl/stream/index/query planes, explicit idempotency + watermarks, resolved search-vs-timeline ownership  
> **Interview theme:** 2024 L5+ Google-style — consume and index an entire Twitter-like external feed for Google Search / Knowledge / News surfaces; reliability under partner rate limits and schema churn, not “build Twitter”

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

Goal: **bound the product**—an **external social-feed indexing pipeline** that consumes a Twitter-like public feed (partner APIs + permitted crawl), normalizes posts into Google-owned indexes, and serves search / entity / freshness queries. This is **not** building the social network itself.

### 1.0 What this is / is not

| Dimension | **External feed indexing (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Ingest, normalize, index, serve lookup/search | Host user timelines / tweets as SoT |
| Success | Coverage, freshness lag, query relevance, ToS compliance | Viral engagement / follow graph UX |
| Write path | Partner stream + crawl + backfill | User compose API |
| Media | Pointers + optional cache; partner CDN remains origin | Full media CDN for the world |
| Legal | Contractual quotas, retention, takedown | Ignore ToS and scrape forever |

**Scope statement:** Design a system that **consumes and indexes an entire Twitter-like feed** with realtime + historical backfill, dual indexes (search + timeline/entity), and progressive scale under rate limits and schema evolution.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Source of posts? | Partner firehose/stream + REST + limited crawl | Multi-ingest; watermark per source |
| F2 | Entire feed? | Yes — near-complete public corpus over time | Backfill + continuous catch-up |
| F3 | What to index? | Text, entities, author, time, engagement, media refs | Canonical post doc + side indexes |
| F4 | Query types? | Keyword search, author timeline slice, entity/topic | Inverted + timeline indexes |
| F5 | Freshness SLA? | Seconds–minutes for hot; hours OK for long-tail | Priority lanes; lag metrics |
| F6 | Dedup? | Retweets/quotes/edits/syndicated copies | Content hash + canonical id map |
| F7 | Entities? | People, orgs, places, hashtags, URLs | NER + linking pipeline |
| F8 | Media? | Store metadata + thumbnails optional; full video by URL | Object store for derived assets only |
| F9 | Deletes/takedowns? | Honor partner delete + legal takedown ASAP | Tombstones; purge fanout |
| F10 | Ranking features? | Offline + nearline features for Search ranking | Feature store hooks; not full RankBrain |
| F11 | Languages? | Global; prioritize top locales MVP | Lang-id; per-locale analyzers |
| F12 | Auth for consumers? | Internal Google services first | Service ACLs; no public tweet API |

**MVP functional scope:**

1. Ingest via **stream** (realtime) + **REST/backfill** (historical gaps) under quotas.  
2. **Idempotent** normalize to canonical `Post` document.  
3. Build **inverted index** (search) + **timeline/author index** + **entity postings**.  
4. Entity extraction (hashtags/URLs/mentions MVP; NER Phase 1.5).  
5. Dedup: same post id, content-near-dup, retweet→parent link.  
6. Serve: search query, get-by-id, author recent, entity recent.  
7. Deletes/tombstones with lag SLO.  
8. Lag/watermark dashboards; backfill workers for holes.  
9. Schema versioning for partner payload evolution.

**Out of MVP:**

- Full social graph (follows) as primary product  
- Building a public Twitter clone UX  
- Perfect global media hosting  
- Real-time engagement graph at tweet cadence for all posts  
- Cross-platform unified social SoT (hooks only)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | End-to-end ingest→searchable lag | Hot path | p50 < 30s, p99 < 5 min (MVP) |
| N2 | Backfill throughput | Historical catch-up | Saturate partner quota without ban |
| N3 | Search QPS | Internal | Baseline 10K → scale table |
| N4 | Durability of index docs | Must not lose acked ingest | WAL + replay; at-least-once + idempotent |
| N5 | Availability | Index stale OK briefly; outage ≠ empty forever | Degraded serve from last good segments |
| N6 | Compliance | ToS / retention / geo | Contractual retention; purge SLAs |
| N7 | Cost | Storage dominated by text+features | Media by reference; cold tiers |
| N8 | Correctness | No resurrect after delete after purge ack | Tombstone > document |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Stream event → validate → normalize → write doc store → index update → searchable.  
2. Backfill page for author/time range → same normalize path → fill holes.  
3. Search “election debate” → inverted postings → rank → hydrate docs.  
4. Entity “#WorldCup” → entity postings by time.  
5. Partner delete → tombstone → remove from indexes → ack purge.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate stream delivery | Idempotent upsert by `source_post_id` + version |
| Edit / “tweet edit” | New `edit_version`; search sees latest; history optional |
| Rate limit 429 | Token bucket; backoff; priority: deletes > hot authors > backfill |
| Stream gap / disconnect | Cursor/watermark rewind; REST gap-fill |
| Schema field renamed | Schema registry; tolerant parsers; DLQ unknowns |
| Viral media storm | Don’t download all video; metadata + selective thumb |
| Near-dup spam | SimHash/MinHash; cluster; keep canonical |
| Legal takedown | High-priority purge queue; audit log |
| Clock skew on created_at | Prefer partner event time + ingest time dual |
| Partial index commit | Doc store commit first; index async with repair |
| Poison payload | Quarantine; don’t block partition forever |
| Partner ToS quota cut | Shed backfill; protect realtime + deletes |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Public posts in corpus | 50B | 500B | — (retention-capped) | multi-trillion events lifetime |
| New posts / day | 500M | 5B | 50B | 500B (multi-source) |
| Peak ingest events/s | 20K | 200K | 2M | 20M |
| Stream partitions | 256 | 2K | 20K | cell-local |
| Search QPS | 10K | 100K | 1M | 10M |
| Indexed doc size avg | ~2 KB | ~2–3 KB | features grow | features grow |
| Hot inverted postings | TB | tens TB | PB | multi-PB |
| Entity types tracked | 10M | 100M | 1B | knowledge-graph scale |
| Backfill workers | 200 | 2K | 20K | quota-bound |
| Delete/purge QPS peak | 1K | 10K | 100K | 1M |
| Media thumb objects | 1B | 10B | selective | selective |

**What each jump forces:**

- **10×:** Shard by time + id; separate realtime vs backfill pools; schema registry.  
- **100×:** Cell by locale/source; segment merge tiers; feature store offline; purge fanout trees.  
- **1,000×:** Multi-source social federation; approximate indexes; aggressive cold tier + sampling for long-tail.

### 1.5 Etc. (Constraints & Assumptions)

- Partner provides **stream + REST** with **strict rate limits**; crawl is supplemental and legally constrained.  
- We are a **downstream indexer**, not the social SoT — partner can delete and we must honor.  
- Prefer **metadata + URLs** for media; derived thumbs only when product needs.  
- Ranking for Google Search is a **consumer** of features — this system produces docs + features, not the full web ranker.  
- Assume eventual consistency between doc store and inverted index with repair.

**Scope statement to repeat back:**

> Design an external Twitter-like feed indexing system: multi-source ingest under rate limits, idempotent normalize, dual search/timeline indexes, entity extraction, dedup, delete/takedown, schema evolution, and progressive 10×/100×/1,000× scaling with watermarks and backfill — for Google internal retrieval, not a social network UX.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Plane |
|-------|------|------------------------|-----|-------|
| **Stream ingest** | Realtime events | ~20K/s | ~200K/s | Kafka + normalizers |
| **Backfill fetch** | REST pages | quota-bound ~2–5K req/s | ×10 workers / still quota | Crawler pool |
| **Normalize/enrich** | Parse, NER lite | ~20–40K/s | ~200–400K/s | Flink/Dataflow |
| **Doc store writes** | Upsert Post | ~20K/s | ~200K/s | Bigtable/Spanner-like |
| **Index updates** | Inverted + timeline | ~20K/s posts → amplified postings | ×10 | Indexer |
| **Search queries** | Keyword/entity | ~10K/s | ~100K/s | Query serving |
| **Purge** | Deletes | ~1K/s | ~10K/s | Priority lane |
| **Feature join** | Engagement snapshots | batch + nearline | ×10 | Feature jobs |

**Anti-pattern:** one “ingest QPS” mixing partner REST calls, Kafka records, index postings, and search QPS.

### 2.2 Storage

```text
Corpus 50B posts × 2 KB avg = 100 TB raw docs
+ inverted index ~0.5–2× text working set (analyzer-dependent) → tens–hundreds TB
+ timeline indexes (author → post_ids) smaller but hot
+ entity postings
Replicas / EC → multi-hundred TB baseline
Media thumbs optional: 1B × 20 KB = 20 TB — only if product requires
```

**At 100× post volume without retention:** multi-PB — **lifecycle tiers mandatory** (hot days, warm months, cold years / sample).

### 2.3 Postings amplification

```text
Avg tokens indexed / post ~40 after stopwording
50B posts × 40 = 2T posting edges lifetime
Realtime: 500M posts/day × 40 = 20B posting updates/day ≈ ~230K posting writes/s average
Peak ~3–5× → design indexer for ~1M posting updates/s headroom at 10×
```

### 2.4 Rate-limit math

```text
Partner: 300 req/s REST global (example interview number — lock with interviewer)
Backfill page size 100 posts → 30K posts/s theoretical
But stream already covers most; backfill for gaps + historical
Budget: 70% stream protection buffer, 20% backfill, 10% deletes/repair
Never let backfill steal delete quota
```

### 2.5 Lag / watermark

```text
Lag = now - max(event_time) successfully indexed per shard
SLO: hot shards p99 lag < 5 min
If lag > threshold: shed enrichments (skip heavy NER), keep index path
```

### 2.6 Cost sketch

```text
Dominant: doc+index storage, indexer CPU, enrichment NLP
Save: media-by-reference, cold tier, dedup near-dups, sample ultra-long-tail for secondary indexes
```

---

## 3. High-Level Design

### 3.1 Canonical data model

```text
Post {
  post_id          // Google canonical
  source           // twitter_like
  source_post_id   // partner id
  author_id
  created_at, edited_at, ingested_at
  text, lang
  entities[]       // mention, hashtag, url, ner_span
  media_refs[]     // url, type, content_hash?, thumb_gcs?
  engagement       // likes, reps, quotes (snapshot + as_of)
  reply_to, quote_of, retweet_of
  visibility       // public / withheld / tombstoned
  content_simhash
  schema_version
  edit_version
}
```

**Invariant:** `(source, source_post_id)` uniquely maps to one `post_id`. Upserts are idempotent on that key + `edit_version`.

### 3.2 Ingest modes

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| **Stream / firehose** | Low lag | Gaps on disconnect; volume spikes | **Primary realtime** |
| **REST backfill** | Repair holes; historical | Hard rate limits | Gaps + bootstrap |
| **Crawl HTML** | Fills API holes | Brittle; ToS risk | Last resort / allowed only |
| **Partner bulk dump** | Fast bootstrap | Stale snapshot | Initial load |

**Chosen MVP:** stream primary + REST gap-fill + optional one-time bulk. Crawl only if contract allows.

### 3.3 Backfill vs realtime

| Concern | Realtime lane | Backfill lane |
|---------|---------------|---------------|
| Priority | High | Low |
| Quota | Reserved | Elastic leftover |
| Ordering | Per-author approximate | By time ranges |
| Enrichment | Full or lite under load | Full offline OK |
| Failure | Rewind watermark | Re-queue range |

**Deal-breaker:** single undifferentiated worker pool — backfill starves deletes and hot ingest.

### 3.4 Index types

| Index | Key | Value | Query |
|-------|-----|-------|-------|
| **Doc store** | `post_id` | Full Post JSON/col | Hydration |
| **Inverted (search)** | term → postings | `(post_id, tf, fields…)` | Keyword |
| **Author timeline** | `author_id + created_at` | post_id | Recent by author |
| **Entity timeline** | `entity_id + created_at` | post_id | Topic/entity feed |
| **Id map** | `source+source_post_id` | post_id | Dedup / upsert |
| **SimHash buckets** | band → candidates | near-dup | Dedup clusters |
| **Tombstones** | post_id | deleted_at, reason | Purge authority |

**Search vs timeline:** inverted index optimized for recall/ranking; timeline index optimized for time-ordered scans. **Do not** serve author “latest N” from inverted index alone at scale.

### 3.5 Entity extraction

| Stage | MVP | Later |
|-------|-----|-------|
| Mentions / hashtags / URLs | Regex + partner entities | — |
| Lang-id | FastText-class | — |
| NER | Optional async | People/org/loc |
| Entity linking | Hashtag as id | KG link (MID) |
| Spam / low-quality | Heuristics | Classifiers |

Pipeline: **sync lite extract on ingest path**; **heavy NER async** so lag SLO holds.

### 3.6 Dedup strategy

| Layer | Mechanism |
|-------|-----------|
| Exact id | `(source, source_post_id)` |
| Retweet | Point to parent; optionally index once |
| Edit | Monotonic `edit_version` |
| Near-dup | SimHash; keep cluster canonical |
| Syndicated URL | Canonical URL normalize |

### 3.7 Media vs metadata

| Store | What |
|-------|------|
| Doc fields | URLs, mime, sizes, alt text if any |
| Object store | Optional thumbs / OCR text |
| CDN | Partner origin for full media |
| Index | Media-type facets; OCR tokens if extracted |

**Deal-breaker:** downloading every video into Google storage on day one — cost and ToS explosion.

### 3.8 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| SoT for social | Partner | We are indexer | Pretend we own tweets |
| Primary ingest | Stream + REST repair | Lag + completeness | Crawl-only |
| Doc vs index | Doc commit then async index | Repairable | Index-only SoT |
| Search vs timeline | Separate indexes | Different access | One inverted for all |
| Media | By reference + selective derive | Cost/ToS | Mirror all video |
| Sharding | Time + hash(id) | Retention + hotspot | Pure author shard only |
| Enrichment | Lite sync / heavy async | Lag SLO | Full NLP on critical path |
| Deletes | Priority purge lane | Legal | Best-effort someday |

---

## 4. Architecture Diagram

```text
                    +------------------+
                    | Partner APIs     |
                    | stream / REST    |
                    +--------+---------+
                             |
              +--------------+--------------+
              |                             |
              v                             v
     +----------------+            +----------------+
     | Stream Ingest  |            | Backfill / Gap |
     | (quotas, cursor)|           | Scheduler      |
     +--------+-------+            +--------+-------+
              |                             |
              +--------------+--------------+
                             v
                    +------------------+
                    | Kafka / PubSub   |
                    | topics: raw,     |
                    | deletes, dlq     |
                    +--------+---------+
                             v
                    +------------------+
                    | Normalize +      |
                    | Idempotent Upsert|
                    | schema registry  |
                    +--------+---------+
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
       +-----------+  +-----------+  +-------------+
       | Doc Store |  | Enrich   |  | Feature     |
       | (BT/Span) |  | async NER |  | nearline    |
       +-----+-----+  +-----+-----+  +------+------+
             |              |               |
             +------+-------+-------+-------+
                    v
           +-------------------+
           | Indexer           |
           | inverted/timeline |
           | entity/tombstone  |
           +---------+---------+
                     v
           +-------------------+
           | Query Serving     |
           | search / get /    |
           | author / entity   |
           +---------+---------+
                     v
           +-------------------+
           | Google consumers  |
           | Search/News/KG    |
           +-------------------+

  Control: watermarks · rate-limit tokens · purge bus · schema versions
```

**Realtime happy path:**

```text
stream event -> validate -> kafka raw -> normalize (idempotent)
  -> upsert doc -> emit index mutation -> searchable
  -> async enrich -> feature update -> reindex fields
```

**Gap fill:**

```text
watermark hole detected -> enqueue [author|time) range
  -> REST fetch under quota -> same kafka raw topic -> same path
```

**Delete:**

```text
delete event -> high-pri topic -> tombstone doc -> index purge -> audit
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Idempotent ingest:** reprocessing the same event does not duplicate docs or double-count postings incorrectly (versioned upsert).  
2. **Tombstone wins:** after purge ack, Get and Search must not return content (within purge SLO).  
3. **Watermark monotonic per shard** (with explicit rewind for repair).  
4. **Doc store precedes serving index** (or index writes are repair-reconciled against docs).  
5. **Quota safety:** never exceed partner hard limits; shed load classes in order.

#### 5.1.2 Idempotent ingest

```text
event_id (partner) or hash(source, source_post_id, edit_version, op)
dedupe cache (short TTL) + durable upsert
index mutations carry doc_generation so late events ignore stale
```

At-least-once Kafka + exactly-once *effect* via upsert generations.

#### 5.1.3 Watermarking lag

| Watermark | Meaning |
|-----------|---------|
| `source_event_time` | Partner created/edited time |
| `ingest_time` | We received |
| `indexed_time` | Searchable |
| `shard_watermark` | Max contiguous indexed event_time (gaps tracked) |

**Lag SLO alerts** on `now - indexed_watermark`. Holes tracked as intervals for backfill, not hidden by max().

**Deal-breaker:** reporting `max(event_time)` as watermark when middle gaps exist — false freshness.

#### 5.1.4 Rate limits & fairness

```text
Global token bucket (partner contract)
├── reserve: deletes / takedowns
├── reserve: realtime stream (usually push; REST for reconnect)
└── elastic: backfill / enrich refetch / thumbs
```

Per-author crawl budgets to avoid focusing firehose on celebrities only during repair.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Stream disconnect | Cursor rewind + REST fill |
| 10× | Hot partition (viral) | Split by id hash; buffer |
| 100× | Index merge IO | Tiered segments; isolate query |
| 1,000× | Multi-source conflicts | Source priority + provenance |

#### 5.1.6 Poison & schema evolution

- Schema registry: forward-compatible Avro/Protobuf.  
- Unknown fields → preserve in `raw_extensions`; don’t drop message.  
- Breaking change → dual-parse window; DLQ with replay.  
- Contract tests against partner sandbox fixtures.

### 5.2 Scalability

#### 5.2.1 Sharding

| Strategy | Pros | Cons | Use |
|----------|------|------|-----|
| **Hash(post_id)** | Even write | Time retention hard | Doc store |
| **Time + hash** | Drop old tablets | Cross-time query fanout | **Indexes** |
| **Author_id** | Timeline locality | Celebrity hotspot | Timeline with celeb subshards |
| **Locale/source cell** | Isolation | Cross-cell search | 100×+ |

**Chosen:** docs by `hash(post_id)`; inverted segments by **time buckets** (day/hour) × term shards; author timelines by `author_id` with hotspot split.

#### 5.2.2 Inverted index serving

```text
terms -> postings lists (docid delta + payload)
fresh segments (realtime memory/SSD) -> flush -> merge -> cold
query: retrieve → BM25/feature rank → hydrate from doc store
```

Realtime: Lucene/Postings-like or Google-internal equivalent; **separate serving replicas** from merge nodes.

#### 5.2.3 Search vs timeline index

| Workload | Plan |
|----------|------|
| Keyword | Inverted; time filter as posting filter / per-time term |
| Author last 50 | Timeline skiplist / log — O(k) |
| Trending entity | Entity timeline + count windows |

**Why not one store?** LSM with secondary indexes can work early; at L5+ scale, call out **specialized postings** for search and **time-ordered logs** for timelines.

#### 5.2.4 Progressive scale

| Jump | Change |
|------|--------|
| →10× | Priority lanes; time-sharded segments; schema registry; DLQ |
| →100× | Cells (geo/source); async NER fleet; feature store; purge tree |
| →1,000× | Approximate long-tail; multi-social federation; sampled secondary indexes |

#### 5.2.5 Ranking features (produced here)

| Feature class | Example | Freshness |
|---------------|---------|-----------|
| Text | BM25, length, lang | Index time |
| Author | follower_count proxy, verified | Nearline |
| Engagement | likes/reposts velocity | Nearline snapshots |
| Entity | topicality, KG prior | Offline |
| Quality | spam score, toxicity | Nearline |
| Freshness | age decay inputs | Query time |

Emit to **feature log / Feature Store**; Search ranker consumes. Indexer may store a **compact quality score** for first-pass retrieval.

#### 5.2.6 Storage tiers

| Tier | Retention | Contents |
|------|-----------|----------|
| Hot | 7–30 days | Full text + inverted + timelines |
| Warm | 1–2 years | Docs + sparse inverted |
| Cold | Longer | Docs / sample; reindex on demand |
| Legal hold | Per request | Exempt from GC |

### 5.3 Maintainability

#### 5.3.1 Schema evolution playbook

1. Add optional field → parsers ignore absence.  
2. Rename → dual-read for N weeks.  
3. Type change → new field + migrate.  
4. Partner version bump → canary normalizer → progressive rollout.

#### 5.3.2 Observability

`ingest_qps{source,lane}`, `lag_seconds{shard}`, `hole_ranges`, `429_rate`, `dlq_depth`, `index_postings_write_s`, `search_p99`, `purge_lag`, `dup_rate`, `enrich_lag`, `schema_parse_fail`.

#### 5.3.3 Testing & drills

- Replay day-of traffic through new normalizer (shadow).  
- Chaos: kill stream → measure hole fill.  
- Purge drill: inject delete; assert absence in search within SLO.  
- Contract tests for partner fixtures.  
- Near-dup evaluation set.

#### 5.3.4 Legal / ToS operability

- Quota config as code; alerts before ban threshold.  
- Retention jobs audited.  
- Takedown ticket → purge id list → attestation.  
- Provenance fields on every doc (`source`, `license_tag`, `fetched_under_contract_id`).

#### 5.3.5 Safe evolution phases

Phase 1: stream + doc + inverted + author timeline.  
Phase 2: entity index + lite NER + features.  
Phase 3: cells + cold tier + advanced dedup.  
Phase 4: multi-source social federation.

---

## 6. Wrap-Up

### 6.1 What we designed

An **external social-feed indexing system** that ingests a Twitter-like corpus via stream + rate-limited backfill, idempotently normalizes into a durable doc store, maintains **search inverted indexes** and **timeline/entity indexes**, extracts entities, dedups, honors deletes, evolves schemas, and scales through time/id sharding and cells — producing features for Google ranking consumers.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Stream vs crawl | Stream primary; REST repair; crawl last |
| Backfill vs realtime | Separate pools; never starve deletes |
| Search vs timeline | Dual indexes |
| Media | Metadata + selective derive |
| Watermarks | Contiguous holes, not max() |
| Enrichment | Heavy async |
| Exactly-once | Effect via idempotent upsert |

### 6.3 Closing line

> “We’re not building Twitter — we’re building a rate-limit-aware, watermarked ingest + dual-index system that stays complete under partner constraints, with tombstones and schema evolution as first-class as BM25.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Ingest & APIs

**Q1: Stream vs REST polling?**  
A: Stream for lag; REST for gaps/bootstrap; polling alone won’t meet freshness at scale.

**Q2: How do you handle 429s?**  
A: Shared token bucket; exponential backoff + jitter; priority classes; never spin.

**Q3: What is a cursor?**  
A: Opaque partner continuation token; persist per shard; rewind on unacked.

**Q4: At-least-once duplicates?**  
A: Idempotent upsert on `(source, source_post_id, edit_version)`.

**Q5: Ordering guarantees?**  
A: Per-author approximate; global order not required; conflict by version/time rules.

**Q6: Bulk dump vs live?**  
A: Dump for bootstrap; live for freshness; reconcile by version.

**Q7: Crawl legality?**  
A: Only under ToS/robots/contract; prefer partner API; document risk.

### 7.2 Backfill & watermarks

**Q8: How detect holes?**  
A: Expected contiguous ranges per shard from stream sequence or time buckets; compare to indexed coverage bitmap.

**Q9: Why is max(event_time) a bad watermark?**  
A: Hides gaps; use contiguous watermark + hole set.

**Q10: Backfill scheduling?**  
A: Priority queue: legal > user-facing hot queries > chronological oldest hole.

**Q11: Catch-up vs keep-up?**  
A: Separate SLOs; catch-up can use offline enrichment.

**Q12: Re-backfill after parser bug?**  
A: Versioned reprocess job; generation bump; shadow diff.

### 7.3 Indexing

**Q13: Inverted index basics?**  
A: term → sorted postings; query intersects/unions; BM25.

**Q14: Realtime inverted updates?**  
A: Soft buffer + flush segments; searchable in seconds; merge later.

**Q15: Why timeline index?**  
A: Author recent is time-ordered scan; inverted is wrong tool at scale.

**Q16: Soft delete vs hard purge?**  
A: Tombstone first for speed; hard purge per retention/legal.

**Q17: Segment merge storms?**  
A: Throttle merges; isolate from query IO; tiered levels.

**Q18: Numeric/engagement fields?**  
A: Doc values / columnar side store for sort/rank.

### 7.4 Dedup & graph links

**Q19: Retweet indexing?**  
A: Store edge; index parent content once; count engagement separately.

**Q20: Near-dup?**  
A: SimHash bands; cluster; choose canonical by engagement/time.

**Q21: Quote tweets?**  
A: Index quote text + link to quoted id; both retrievable.

**Q22: Edits?**  
A: New edit_version; search latest; optional history table.

### 7.5 Entities & NLP

**Q23: What entities MVP?**  
A: Hashtags, mentions, URLs; NER async.

**Q24: Why async NER?**  
A: Protect ingest lag SLO; backfill enrichment.

**Q25: Entity linking to KG?**  
A: Candidate gen + ranker; store `entity_id` with confidence.

**Q26: Multilingual analyzers?**  
A: Lang-id → analyzer chain; don’t use English stemming globally.

**Q27: Spam/abuse text?**  
A: Classifier features; may exclude from Search index but keep doc for integrity.

### 7.6 Media

**Q28: Store videos?**  
A: No by default; URL + optional thumb/OCR.

**Q29: Hotlinked media breakage?**  
A: Product shows placeholder; periodic link check sample; legal cache exceptions.

**Q30: Image duplicates?**  
A: Perceptual hash on thumbs if stored.

### 7.7 Ranking features

**Q31: What features leave this system?**  
A: Text stats, author priors, engagement velocity, entity topicality, spam scores.

**Q32: Fresh engagement?**  
A: Nearline snapshots; query-time join with care for QPS.

**Q33: Training data?**  
A: Feature logs + human/traffic labels in Search — separate from ingest path.

### 7.8 Consistency & deletes

**Q34: Doc indexed but enrich missing?**  
A: Serve with partial features; async fill; generation.

**Q35: Index without doc?**  
A: Repair job drops orphan postings.

**Q36: Purge SLO?**  
A: Seconds–minutes for legal; measure `purge_lag`.

**Q37: Cross-cell purge?**  
A: Fanout bus with ack; tombstone first centrally.

### 7.9 Schema evolution

**Q38: Additive change?**  
A: Optional fields; defaulting parsers.

**Q39: Breaking partner change?**  
A: Dual parse; canary; DLQ; replay.

**Q40: How version docs?**  
A: `schema_version` on Post; migrations batch.

### 7.10 Scalability & cells

**Q41: Celebrity author hotspot?**  
A: Subshard timeline by time; cache recent page.

**Q42: Viral term hotspot?**  
A: Term shard splits; caching of top queries.

**Q43: Multi-region?**  
A: Ingest regional; index cells; global query fanout with caching.

**Q44: 1,000× posts/day?**  
A: Sample long-tail for secondary indexes; prioritize head; multi-source cells.

### 7.11 Reliability drills

**Q45: Partner outage 2 hours?**  
A: Buffer; lag alerts; backfill on recovery; communicate stale to consumers.

**Q46: Poison event loops?**  
A: Quarantine key; circuit break enrich; continue partition.

**Q47: Incorrect mass delete?**  
A: Soft tombstone with undo window for non-legal; legal is stricter.

### 7.12 Product / interview meta

**Q48: How is this different from building Twitter?**  
A: No compose/follow UX SoT; downstream index under contracts.

**Q49: What do you lock first in interview?**  
A: Sources, freshness SLO, query types, media policy, delete SLA, scale numbers.

**Q50: L5 signal?**  
A: Split planes, watermarks with holes, dual indexes, quota priority, schema/ToS as design — not just “Kafka + Elasticsearch.”

**Q51: Search-after-delete race?**  
A: Generation checks; tombstone store authoritative for Get; search filters deleted bit with repair.

**Q52: How to prioritize which authors to backfill first?**  
A: Query demand logs + follower proxies + newsiness scores.

**Q53: Idempotency key design?**  
A: Prefer partner event id; else hash of stable business key + op type.

**Q54: Cross-post same text different ids?**  
A: Near-dup cluster; may keep both with cluster_id for diversity.

**Q55: Engagement snapshot skew?**  
A: Store `as_of`; don’t mix snapshots in one feature without time align.

**Q56: Why not Spanner for inverted postings?**  
A: Postings updates too write-amplified; specialized inverted engine wins; Spanner/BT for docs/maps OK.

**Q57: Time shard width?**  
A: Hour/day trade merge vs query fanout; hot hours thinner.

**Q58: Geo-withheld content?**  
A: Visibility constraints in doc; query filter by user country.

**Q59: Cost kill-switch?**  
A: Disable thumb fetch; disable heavy NER; drop cold reindex; sample.

**Q60: Closing tradeoff sentence?**  
A: Completeness under quota vs freshness vs enrichment depth — shed in that explicit order.

---

## Appendix A: Example APIs (internal)

```text
GetPost(post_id) -> Post | Tombstone
Search(query, filters, page) -> post_ids + scores
AuthorTimeline(author_id, cursor, n) -> post_ids
EntityTimeline(entity_id, cursor, n) -> post_ids
Purge(post_id|source_post_id, reason) -> ack
AdminWatermark(shard) -> lag, holes
```

## Appendix B: Priority shedding order

```text
1. Keep: deletes / takedowns
2. Keep: realtime normalize + index (lite enrich)
3. Shed: heavy NER / OCR
4. Shed: thumb derivation
5. Shed: historical backfill
6. Last: drop noncritical feature nearline
```

## Appendix C: Sharding sketch

```text
doc_rowkey     = hash(post_id) % N
timeline_key   = author_id | invert(created_at) | post_id
term_shard     = hash(term) % T
time_partition = floor(created_at / day)
segment_id     = time_partition | term_shard | generation
```

## Appendix D: Deal-breaker checklist (say out loud)

| If you hear… | Push back |
|--------------|-----------|
| “Just Elasticsearch for everything” | Timeline + purge + scale postings |
| “Crawl all media” | Cost/ToS |
| “Exactly-once Kafka” | Idempotent effects |
| “Watermark = max timestamp” | Holes |
| “One worker pool” | Priority starvation |
| “We’ll fix schema later” | Registry now |

## Appendix E: Progressive capacity narrative

**Baseline:** Single region; Kafka; doc BT; realtime segments; REST gap-fill; lite entities.  
**10×:** Quota scheduler; time-sharded index; DLQ/replay; feature nearline; celebrity subshards.  
**100×:** Cells; purge fanout; cold tier; KG linking; dedicated merge fleet.  
**1,000×:** Multi-network federation; approximate long-tail; query-driven rehydration from cold.

## Appendix F: Minimal sequence diagrams

**Upsert race (edit vs old):**

```text
old edit_version=1 arrives late after v2 applied
-> compare generations -> ignore stale -> metrics stale_drop++
```

**Search query:**

```text
query -> analyze -> retrieve postings (time filter)
-> first-pass score -> top H hydrate docs -> return
```

**Takedown:**

```text
legal -> purge API -> tombstone + kafka purge
-> indexers drop postings -> serving bit -> audit attestation
```
