# System Design: Bulk Product Ingestion (Uncertain Duplicates)

> **Focus areas:** Seller catalog uploads · Fuzzy matching · ASIN mapping · Dedup confidence · Review queues · Eventual consistency · Idempotent ingest · Catalog publish  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes (upload vs match vs publish vs review), explicit dedup invariants, resolved ownership of ASIN identity vs seller SKU

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

Goal: **bound marketplace catalog ingestion**—sellers upload large product feeds; the platform must map each offer/listing to an existing ASIN or create a new one, under **uncertain duplicates** (same product described differently), with human review for ambiguous cases, and eventual consistency of customer-facing catalog.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who uploads? | 3P sellers + internal 1P merchandisers | Multi-tenant `seller_id`; authz per feed |
| F2 | Input formats? | CSV/TSV, XML, JSON lines; flat files via SFTP/S3; API for small batches | Ingest adapters → normalized `ProductDraft` |
| F3 | What is a “product”? | Title, brand, identifiers (UPC/EAN/ISBN/GTIN), attrs, images, category, condition | Core + attributes JSON; identifier priority |
| F4 | Duplicate problem? | Same physical product may already have ASIN; seller SKU ≠ ASIN | Matching pipeline + ASIN mapping |
| F5 | Exact vs fuzzy? | Exact GTIN match when valid; fuzzy title/brand/attrs when not | Tiered matcher; confidence scores |
| F6 | Auto vs human? | High confidence auto-map/create; medium → review queue; low → reject/ask | Threshold policy + review UX |
| F7 | Offer vs catalog? | Listing/offer (price, qty, condition) binds to ASIN; catalog is shared product | Separate Offer vs Catalog Product |
| F8 | Updates? | Re-upload same seller SKU updates offer/attrs; may rematch | Idempotent upsert by `(seller_id, seller_sku)` |
| F9 | Images/media? | URLs or binary upload; virus scan; CDN publish | Media pipeline async |
| F10 | Validation? | Required fields by category; prohibited content; brand gating | Rule engine pre-match |
| F11 | Feedback to seller? | Per-row status: mapped / created / needs_review / rejected + reasons | Result report + webhooks |
| F12 | Customer visibility? | Only after ASIN publish + offer active | Publish gate; not draft-visible |
| F13 | Merge/split ASINs? | Ops can merge duplicates discovered later | ASIN merge workflow (careful) |
| F14 | Rate / bulk size? | Millions of rows/day; files up to tens of GB | Async jobs; chunked processing |
| F15 | Idempotency? | Retries, re-uploads, duplicate files | Feed + row identity; content hash |

**MVP functional scope (lock with interviewer):**

1. Accept bulk feeds (S3 + API) and normalize into draft rows.  
2. Validate schema/category rules; quarantine invalid rows.  
3. **Tiered matching:** GTIN exact → identifier graph → fuzzy features → confidence.  
4. Auto **map to ASIN** or **create ASIN** above thresholds; else **review queue**.  
5. Bind **seller offer** to ASIN; emit catalog/offer events.  
6. Seller-facing job status + row-level error report.  
7. Ops review UI: confirm match, create new, or reject.  
8. Idempotent reprocessing; audit trail of decisions.

**Out of MVP (explicitly defer):**

- Full A9 relevance / search ranking deep dive  
- Perfect global active-active catalog writes  
- Generative title rewriting as core path  
- Automatic brand registry lawsuits / IP court system  
- Real-time single-item seller Central UX (mention as sibling)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Ingest latency | Bulk not interactive | First result rows minutes; full feed hours OK |
| N2 | Match quality | Precision over reckless merge | Auto-map precision ≥ 99.5% target; measure |
| N3 | Throughput | Peak seller season | See scale table; partition by seller/feed |
| N4 | Durability | No silent drop of accepted feeds | Object store + durable queue before ACK |
| N5 | Consistency | Customer catalog eventual | Draft → matched → published stages |
| N6 | Idempotency | Safe retries | Same feed/row → same outcome |
| N7 | Audit | Why this ASIN? | Decision log with features + reviewer |
| N8 | Isolation | Bad seller can’t poison others | Per-seller quotas; poison-row quarantine |
| N9 | Operability | Own the pager | Match drift alarms; review backlog SLO |
| N10 | Efficiency | Don’t O(n²) fuzzy all catalog | Blocking keys / candidate generation |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seller uploads 100K CSV → validate → 80K GTIN exact map → 15K fuzzy auto-create/map → 5K review → offers published.  
2. Re-upload same file → idempotent; only changed rows rematch.  
3. New unique product (valid GTIN, no ASIN) → create ASIN → offer bind → search index.  
4. Reviewer confirms suggested ASIN → map + publish.  
5. Seller updates price/qty only → skip rematch; offer patch.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Invalid GTIN checksum | Don’t trust as exact; fall to fuzzy or reject per policy |
| Two ASINs for same GTIN (data debt) | Conflict queue; don’t auto-pick randomly |
| Fuzzy score in gray zone | Review queue; never silent auto-merge |
| Seller copies competitor title badly | Brand gating / similarity to restricted brands → review |
| Image URL 404 | Soft fail media; listing may stay suppressed |
| Feed truncated mid-upload | Multipart complete check; reject incomplete |
| Duplicate rows in one feed | Last-write or deterministic merge by row_id |
| Malicious content / phishing URL | Scanner + deny lists |
| Reviewer disagrees with model | Human wins; label captured for retraining |
| ASIN merge after publish | Redirect mapping; offers rebind; search tombstone |
| Hot brand / category flood | Quotas; priority lanes for trusted sellers |
| Matcher model rollback | Versioned matcher; can reprocess feeds |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active sellers | 50K | 500K | 5M | 50M |
| Rows ingested / day | 20M | 200M | 2B | 20B |
| Peak feed files / hour | 2K | 20K | 200K | 2M |
| Peak row process /s | 5K | 50K | 500K | 5M |
| Catalog ASINs | 50M | 200M | 500M | 1B+ |
| Fuzzy candidate lookups /s | 2K | 20K | 200K | 2M |
| Review decisions / day | 50K | 500K | 5M | 50M* |
| Auto-map rate | 90% | 92% | 95% | 97% |
| Media objects / day | 5M | 50M | 500M | 5B |

\*At extreme scale, review is sampling + specialist queues, not 1:1 humans on every gray row.

**What each jump forces:**

- **10×:** Chunk workers; candidate index; separate offer vs catalog DBs; review tooling.  
- **100×:** Seller cells / feed partitions; ANN/blocking at scale; matcher feature store; auto-threshold tuning.  
- **1,000×:** Hierarchical catalog shards; near-dupe clustering offline; human review only for high-risk; stream ingest.

### 1.5 Etc. (Constraints & Assumptions)

- **ASIN** is the customer-facing product identity (Amazon-style).  
- **Seller SKU** is seller-local; mapping table is mandatory.  
- Matching is **probabilistic**; policy thresholds are product decisions.  
- Catalog publish is **eventually consistent** with search/PDP caches.  
- We optimize **precision of auto-merge** over recall of automation (wrong merge is catastrophic).

**Scope statement:**

> Design a bulk product ingestion system that accepts seller catalogs, validates and normalizes rows, maps uncertain duplicates to ASINs via tiered exact/fuzzy matching with review queues, binds offers, and publishes eventually consistent catalog state—correct under retries and scaled from tens of millions of rows/day through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (deal-breaker if mixed)

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Upload / store** | Bytes to S3 | GB/s bursts | Very high | Object storage |
| **Validate / normalize** | CPU row parse | 5K rows/s | 5M/s | Stateless workers |
| **Exact match** | GTIN/ASIN KV | 3K/s | 3M/s | Identifier index |
| **Fuzzy match** | Candidate + score | 2K/s | 2M/s | Search/ANN + scorer |
| **Publish** | Catalog/offer writes | 1K/s | 1M/s | Catalog SoT shards |
| **Review** | Human/API decisions | ~1/s avg | Policy-capped | Review service |
| **Seller status reads** | Job dashboards | 500/s | 500K/s | Cached read model |

### 2.2 Storage

```text
Raw feed: 20M rows/day × 2 KB ≈ 40 GB/day raw
Normalized draft + features ≈ 3–5 KB/row → ~80–100 GB/day
Decision audit ~500 B/row → ~10 GB/day
Media: assume 30% rows new image × 200 KB → heavy; store by hash dedup

Retain raw feeds 90d hot / 2y cold (compliance + disputes)
ASIN mapping table: sellers × skus — 500M mappings × 200 B ≈ 100 GB baseline
```

### 2.3 Matching cost

```text
Naive fuzzy vs 50M ASINs = impossible per row
Blocking: brand_normalized + category + title_tokens → top K=50 candidates
Score each candidate ~ cheap features + optional embedding distance
2K fuzzy/s × 50 = 100K score evals/s → batchable, cache brand blocks
```

### 2.4 Review economics

```text
Gray zone 5% of 20M = 1M/day — cannot all be human
Strategies: raise auto threshold carefully; seller self-serve “confirm match”;
sample audits; trusted seller auto-higher; cluster near-dupes for one decision
Target human review << 100K/day with tooling
```

### 2.5 Bandwidth

```text
Seller uploads concentrated; multipart S3
Internal: Kafka row events ~1–2 KB → 5K/s ≈ 10 MB/s baseline; 1,000× plan partitions
```

### 2.6 Bottleneck ranking

(1) Wrong auto-merge (quality) (2) candidate generation recall (3) review backlog (4) catalog write hotspots (brand) (5) raw parse throughput.

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
Seller Central                     Catalog Ops
+------------------------+         +---------------------------+
| Upload feed / API      |         | Review queue              |
| Job progress           |         | Suggested ASIN + score    |
| Row errors download    |         | Confirm / Create / Reject |
| Match suggestions UX   |         | Merge ASIN tools          |
+------------------------+         +---------------------------+
        |                                    |
        v                                    v
   Customer Catalog (PDP / Search) ← published ASINs + offers only
```

### 3.2 Domain model

```text
FeedJob
 ├── feed_id, seller_id, source_uri, content_hash, status
 ├── row_counts, created_at
 └── idempotency_key

ProductDraft (row)
 ├── draft_id, feed_id, seller_id, seller_sku
 ├── gtin?, brand, title, category, attrs, media_refs
 ├── content_hash, status
 └── match_decision_id?

MatchDecision
 ├── decision_id, draft_id
 ├── candidates[] {asin, score, reasons[]}
 ├── outcome: AUTO_MAP|AUTO_CREATE|REVIEW|REJECT
 ├── chosen_asin?, matcher_version
 └── reviewer_id? (if human)

AsinMapping
 ├── seller_id, seller_sku → asin  (SoT for binding)
 ├── confidence, source (AUTO|HUMAN|GTIN)
 └── updated_at

CatalogProduct (ASIN)
 ├── asin, title, brand, category, attrs, version
 └── status: DRAFT|ACTIVE|MERGED|SUPPRESSED

Offer
 ├── offer_id, seller_id, asin, seller_sku
 ├── price_cents, qty, condition, status
 └── version
```

**Ownership (resolved):**

| Concern | Source of truth |
|---------|-----------------|
| Raw bytes | Object store (S3) |
| Feed job state | Ingest Job service |
| Draft rows | Draft store |
| Seller SKU → ASIN | **AsinMapping** service |
| Product attributes (shared) | **Catalog** service |
| Price/qty/condition | **Offer** service |
| Match scores / audit | Decision log (append-heavy) |
| Review tasks | Review service |
| Search documents | Derived |

**Deal-breakers:**

- Auto-merging below precision SLO.  
- Using search index as ASIN SoT.  
- Dual-writing mapping in seller DB and catalog without owner.  
- Treating GTIN as always unique/trustworthy without validation.  
- Publishing drafts before decision finalize.

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| Upload Gateway | Auth, multipart, virus pre-check, create FeedJob |
| Feed Parser Workers | Decode CSV/XML/JSON; chunk; emit drafts |
| Validation Service | Schema, category rules, prohibited content |
| Identifier Index | GTIN/EAN/ISBN/UPC → ASIN(s) |
| Matching Service | Blocking, scoring, thresholds, decision |
| Candidate Index | Title/brand blocking + embeddings ANN |
| Catalog Service | Create/update ASIN attributes |
| Offer Service | Upsert seller offers |
| Mapping Service | Persist seller_sku → asin |
| Review Service | Queues, assignment, decisions |
| Publish / Outbox | Emit catalog.changed, offer.changed |
| Media Pipeline | Fetch, scan, hash-dedup, CDN |
| Seller Report | Row results, signed download links |
| Admin / Merge | ASIN merge/split ops |

### 3.4 Ingest pipeline stages

```text
ACCEPT → STORE → PARSE → VALIDATE → MATCH → DECIDE → BIND → PUBLISH → REPORT
                      ↘ QUARANTINE                ↘ REVIEW ↗
```

Each stage is **at-least-once**; handlers idempotent on `draft_id` + stage version.

### 3.5 Tiered matching (core)

```text
1) If valid GTIN and exactly one ACTIVE ASIN → score=1.0 AUTO_MAP
2) If valid GTIN and zero ASIN → AUTO_CREATE (subject to brand/category gates)
3) If valid GTIN and multiple ASINs → REVIEW (data conflict)
4) Else generate candidates via blocking keys + ANN
5) Score features (title sim, brand, attrs, image embedding optional)
6) if score >= T_high → AUTO_MAP
   elif score <= T_low and novelty high → AUTO_CREATE
   elif T_low < score < T_high → REVIEW
   else REJECT / ask seller for identifiers
```

**Thresholds** are versioned config; different for trusted sellers.

### 3.6 Fuzzy features (interview depth)

| Feature | Notes |
|---------|-------|
| Normalized title similarity | Token Jaccard / cosine TF-IDF |
| Brand match | Synonym table; “Sony Inc” ≈ “SONY” |
| Attribute overlap | Color, size, model_number |
| Model / MPN | High weight when present |
| Image embedding distance | Phase 1.5; helps apparel |
| Category distance | Taxonomy parent distance |
| Historical seller map | Prior SKU→ASIN strong prior |

**Blocking keys examples:** `hash(brand_norm + first_3_title_tokens)`, `mpn_norm`, `model_norm`.

### 3.7 Review queue

```text
Priority = f(score_uncertainty, GMV potential, brand risk, seller trust)
UI shows: draft attrs, top-3 ASINs, diffs, image side-by-side
Actions: MAP_TO(asin) | CREATE_NEW | REJECT(reason) | NEED_INFO
SLA: P0 brand conflicts < 4h; long-tail backlog OK with seller wait
```

Human decision writes same `MatchDecision` schema with `source=HUMAN`.

### 3.8 Eventual consistency & publish

```text
Decision FINAL → Mapping upsert → Catalog create/update → Offer upsert
  → outbox events → Search indexer / PDP cache invalidation
Customer may see new offer in seconds–minutes
Seller report shows FINAL before global search convergence
```

Never claim “live on Amazon” until Offer `ACTIVE` and Catalog `ACTIVE`.

### 3.9 Idempotency model

```text
Feed: (seller_id, idempotency_key | content_hash) unique
Row: (feed_id, row_number) or (seller_id, seller_sku, content_hash)
Rematch only if content_hash of match-relevant fields changes
Price-only change → Offer path skip MATCH
```

### 3.10 API sketch

```text
POST /v1/feeds                  {source_uri|upload} Idempotency-Key
GET  /v1/feeds/{feed_id}
GET  /v1/feeds/{feed_id}/results
POST /v1/drafts/{id}/rematch    (ops/seller)
GET  /v1/review/tasks
POST /v1/review/tasks/{id}/decide
GET  /v1/mappings/{seller_id}/{seller_sku}
POST /v1/catalog/asins/merge    (ops)
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
Sellers → Upload GW → S3 (raw feeds)
                ↓
         FeedJob DB + SQS/Kafka parse topic
                ↓
         Parser workers → Draft store
                ↓
         Validation → Match requests topic
                ↓
         +------------------+
         | Matching Service |----→ Identifier Index (GTIN)
         |                  |----→ Candidate Index (OpenSearch/ANN)
         +---------+--------+
                   ↓
            Decision Log
           /     |      \
    AUTO_MAP  REVIEW   AUTO_CREATE
       |        |           |
       v        v           v
  Mapping ← Review Svc   Catalog.create
       \        |          /
        \       v         /
         → Offer Service → Outbox → Kafka → Search / Cache / Notify
```

### 4.2 Match sequence

```text
DraftReady → Matcher
  → lookup GTIN
  → if ambiguous: Decision=REVIEW; enqueue
  → else candidates = block(draft)
  → scores = rank(draft, candidates)
  → apply thresholds → Decision
  → if AUTO_MAP: Mapping.bind; Offer.upsert; maybe Catalog.enrich
  → if AUTO_CREATE: Catalog.create; Mapping.bind; Offer.upsert
  → emit RowResult
```

### 4.3 Review sequence

```text
Reviewer claims task → sees candidates
  → decide MAP/CREATE/REJECT
  → durable Decision (human)
  → same bind/publish path as auto
  → training label sink (offline)
```

### 4.4 Failure / retry

```text
Matcher timeout → retry with backoff; draft stays MATCHING
Catalog create fails unique race → rematch (another winner created)
Partial publish → outbox retries; Mapping is commit point for seller SKU
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Accepted feed bytes durable** before API success.  
2. **No AUTO_MAP below T_high** for that matcher version.  
3. **AsinMapping single writer** per `(seller_id, seller_sku)`.  
4. **Decision append-only audit** — corrections are new decisions.  
5. **Idempotent stage handlers** — duplicate Kafka messages safe.  
6. **GTIN multi-ASIN never auto-picked**.  
7. **Publish only after FINAL decision**.  
8. **Offer cannot point to MERGED tombstone** — follow redirect.  
9. **Reviewer actions authorized** + logged.  
10. **Quotas** prevent one seller from starving the cluster.

**Amazon interview signal:** page on `auto_map_precision` (sampled audits), `review_backlog_age`, `poison_feed_rate`, `publish_lag_p99`.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | S3 + worker fleet + Postgres drafts + OpenSearch candidates + one review app |
| 10× | Shard drafts by seller; Kafka; separate offer/catalog; media workers; matcher autoscaling |
| 100× | ANN service; feature cache; seller trust tiers; regional ingest cells; columnar audit |
| 1,000× | Offline near-dupe clustering; streaming ingest; catalog cell by category/brand; review sampling |

**Hot keys:** popular GTINs, mega-brand title blocks — cache identifier hits; isolate celebrity ASINs.

### 5.3 Maintainability

- Version `matcher_version` on every decision.  
- Shadow-score new models before promoting thresholds.  
- Contract tests: GTIN fixtures + fuzzy golden sets.  
- Dead-letter queues per stage with replay tools.  
- Schema registry for feed formats.  
- Feature flags for image-embedding path.

### 5.4 Consistency spectrum

| Data | Model | Why |
|------|-------|-----|
| Raw feed | Strong durable object | Source evidence |
| Draft processing state | Strong per draft | Exactly-once effects |
| Match decision | Append-only | Audit |
| AsinMapping | Strong per SKU key | Seller truth |
| Catalog ASIN attrs | Strong per ASIN (single writer) | Product truth |
| Search/PDP | Eventual | Scale |
| Review assignment | Strong lease | Avoid double review |

### 5.5 Why eventual consistency is OK (and where not)

Customer discovery can lag. **Not OK:** two different ASINs sold as identical GTIN without conflict flag; offer bound without mapping; losing seller feed silently.

### 5.6 Duplicate uncertainty — product policy

Wrong merge → mixed reviews, wrong PDP, legal risk. Wrong create → fragmented catalog, worse search. **Bias to review/create cautiously** for high-risk categories (electronics serials, beauty, grocery). Apparel may tolerate more creates.

### 5.7 ASIN merge (ops)

```text
merge(from_asin, into_asin):
  mark from MERGED → redirect into
  rebind offers/mappings
  enqueue search delete/redirect
  preserve decision audit
Never hard-delete history
```

### 5.8 Observability

| Metric / alarm | Why |
|----------------|-----|
| `feed_accept_rate` / parse errors | Seller UX |
| `row_stage_lag` | Pipeline health |
| `auto_map_rate` + `review_rate` | Threshold tuning |
| `sampled_auto_map_error_rate` | Precision SLO |
| `review_backlog_p95_age` | Ops capacity |
| `gtin_conflict_count` | Catalog debt |
| `publish_lag` | Customer visibility |
| `matcher_p99` | Fuzzy cost |

---

## 6. Wrap-Up

### 6.1 What we designed

A **bulk product ingestion platform** that stores seller feeds durably, validates/normalizes rows, applies tiered exact and fuzzy ASIN matching with confidence thresholds, routes uncertain duplicates to review queues, binds offers via AsinMapping, and publishes eventually consistent catalog/search state—with full auditability and progressive scale.

### 6.2 Key decisions worth defending

1. **Tiered matching** — GTIN first, fuzzy second, human for gray zone.  
2. **Precision-biased thresholds** — wrong merge worse than extra ASIN.  
3. **AsinMapping as SoT** for seller SKU identity.  
4. **Separate Catalog vs Offer**.  
5. **Idempotent feed/row identity** with content-hash rematch.  
6. **Blocking/ANN candidates** — never full catalog scan.  
7. **Versioned matcher** + shadow eval.  
8. **Append-only decisions**.  
9. **Eventual publish** with explicit seller “live” criteria.  
10. **Trusted-seller / risk tiers** for automation rate.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Fuzzy drift / seasonal titles | Continuous audit samples |
| Review backlog explosion | Seller self-confirm; cluster tasks |
| GTIN reuse / counterfeit | Brand registry gates |
| Catalog attribute wars (multi-seller) | Attribute contribution rules |
| Media copyright | Hash + takedown workflow |
| Mega-feed noisy data | Stricter validation; row caps |

### 6.4 How to present in 45 minutes

1. Requirements + duplicate uncertainty (6 min)  
2. Numbers + why blocking (4 min)  
3. Pipeline stages + ownership (8 min)  
4. Matching tiers + thresholds + review (12 min)  
5. Publish consistency + scale jumps (8 min)  
6. Invariants / traps (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Identity & GTINs

**Q: Is GTIN enough to auto-map always?**  
A: Only if validated and uniquely maps to one ACTIVE ASIN; else conflict/review.

**Q: What if seller invents a GTIN?**  
A: Checksum + registry checks; fraud signals; don’t create trusted identity from garbage.

**Q: Multiple sellers, same GTIN, conflicting titles?**  
A: Map to same ASIN; attribute updates via contribution policy / locked fields.

**Q: ISBN vs UPC?**  
A: Identifier type specific validation; books often cleaner.

### 7.2 Fuzzy matching

**Q: Why not only embeddings?**  
A: Explainability, brand rules, cold-start; use hybrid features + ANN.

**Q: How do you generate candidates?**  
A: Blocking keys + inverted index + ANN; top-K then precise score.

**Q: How set T_high?**  
A: Offline precision-recall on labeled set; raise until precision SLO; monitor online audits.

**Q: Apparel size/color variants?**  
A: Variant graph under parent ASIN; don’t merge different sizes into one ASIN.

### 7.3 Review & ops

**Q: Can sellers confirm matches themselves?**  
A: Yes for medium confidence—reduces ops; still audit sample.

**Q: Double review?**  
A: High-risk categories dual-control; normal single reviewer with sampling.

**Q: Reviewer fatigue / rubber stamps?**  
A: Gold tasks; quality scoring; remove bad actors.

### 7.4 Consistency & publish

**Q: Seller sees SUCCESS but search misses product?**  
A: Expected eventual; show “indexing” state; alarm on publish lag.

**Q: Race: two feeds create two ASINs for same new GTIN?**  
A: Unique constraint on GTIN→ASIN where policy requires; loser remaps.

**Q: Reprocess after matcher upgrade?**  
A: Selective rematch by version; don’t flip stable high-confidence maps without care.

### 7.5 Scale & abuse

**Q: Seller uploads 1B garbage rows?**  
A: Quotas, validation fail-fast, cost controls, account limits.

**Q: Hot brand block key?**  
A: Shard blocks; cache; hierarchical brand indexes.

**Q: 1,000× review impossible?**  
A: Automation ↑, clustering, risk-based sampling, seller-assisted confirm.

### 7.6 Failure injection

1. S3 unavailable → fail accept; no phantom jobs.  
2. Kafka duplicate → idempotent decide.  
3. OpenSearch down → degrade to GTIN-only + REVIEW backlog growth alarm.  
4. Catalog shard hotspot → queue + retry; seller sees PROCESSING.  
5. Reviewer claims crash → lease expiry reassign.  
6. Poison XML bomb → parser limits; quarantine file.  
7. Image malware → media scanner blocks publish.  
8. Threshold misconfig → feature flag rollback; freeze AUTO_MAP.  
9. Clock skew on job TTL → use storage etags / absolute times.  
10. Partial offer write → transactional outbox; reconcile job.

### 7.7 Amazon Leadership-flavored probes

**Q: Customer Obsession — merge or create?**  
A: Prefer correct PDP; wrong merge harms many customers → bias review.

**Q: Ownership — who pages on precision drop?**  
A: Matching team owns matcher + thresholds; catalog owns ASIN integrity.

**Q: Frugality — human review for everything?**  
A: No; invest in features/thresholds; humans on uncertain/high-risk.

**Q: Dive Deep — prove auto-map quality?**  
A: Labeled sets, online sampled audits, dispute rate, merge rollback rate.

### 7.8 Comparison traps

**Q: Is this just ETL?**  
A: Probabilistic identity + marketplace incentives dominate.

**Q: Same as search indexing?**  
A: Indexing is downstream; identity resolution is the hard core.

**Q: Same as inventory ingest?**  
A: Offers have qty; catalog identity still separate.

**Q: Why not seller-provided ASIN only?**  
A: Abuse/mistakes; must verify; ASIN optional input becomes a feature with trust weight.

### 7.9 Extra interviewer traps (high value)

- What is the SoT for seller SKU → ASIN?  
- When do you rematch vs patch offer?  
- How do you prevent O(n²) fuzzy?  
- Gray-zone policy?  
- GTIN conflict behavior?  
- How do variants work?  
- How do you version matchers?  
- What makes a feed idempotent?  
- When is a product “live”?  
- How do you merge ASINs safely?  
- How do trusted sellers differ?  
- How do you measure precision online?  
- What belongs in review priority?  
- How do attribute updates from 3P work?  
- Deal-breaker of auto-merging on title equality alone?

### 7.10 Progressive scale Q&A

**Q: Baseline architecture?**  
A: S3, workers, PG, OpenSearch, simple review UI.

**Q: 10× first split?**  
A: Match workers autoscaling; offer/catalog split; Kafka stages.

**Q: 100×?**  
A: ANN; seller tiers; ingest cells; audit lake.

**Q: 1,000×?**  
A: Offline clustering; streaming; review sampling; catalog cells.

---

## 8. Appendices

## Appendix A — Example schemas

```sql
CREATE TABLE feed_jobs (
  feed_id UUID PRIMARY KEY,
  seller_id UUID NOT NULL,
  source_uri TEXT NOT NULL,
  content_hash TEXT NOT NULL,
  status TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  matcher_version TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (seller_id, idempotency_key)
);

CREATE TABLE product_drafts (
  draft_id UUID PRIMARY KEY,
  feed_id UUID NOT NULL REFERENCES feed_jobs(feed_id),
  seller_id UUID NOT NULL,
  seller_sku TEXT NOT NULL,
  gtin TEXT,
  brand TEXT,
  title TEXT NOT NULL,
  category TEXT,
  attrs JSONB NOT NULL DEFAULT '{}',
  content_hash TEXT NOT NULL,
  match_hash TEXT NOT NULL, -- subset relevant to rematch
  status TEXT NOT NULL,
  UNIQUE (feed_id, seller_sku)
);

CREATE TABLE match_decisions (
  decision_id UUID PRIMARY KEY,
  draft_id UUID NOT NULL,
  outcome TEXT NOT NULL,
  chosen_asin TEXT,
  score NUMERIC,
  candidates JSONB NOT NULL,
  matcher_version TEXT NOT NULL,
  source TEXT NOT NULL, -- AUTO|HUMAN
  reviewer_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE asin_mappings (
  seller_id UUID NOT NULL,
  seller_sku TEXT NOT NULL,
  asin TEXT NOT NULL,
  confidence NUMERIC NOT NULL,
  source TEXT NOT NULL,
  decision_id UUID NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (seller_id, seller_sku)
);

CREATE TABLE catalog_products (
  asin TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  brand TEXT,
  category TEXT,
  attrs JSONB NOT NULL DEFAULT '{}',
  gtin TEXT,
  status TEXT NOT NULL,
  version BIGINT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX ON catalog_products (gtin) WHERE gtin IS NOT NULL AND status = 'ACTIVE';

CREATE TABLE offers (
  offer_id UUID PRIMARY KEY,
  seller_id UUID NOT NULL,
  seller_sku TEXT NOT NULL,
  asin TEXT NOT NULL,
  price_cents BIGINT NOT NULL,
  currency CHAR(3) NOT NULL,
  qty INT NOT NULL,
  condition TEXT NOT NULL,
  status TEXT NOT NULL,
  version BIGINT NOT NULL,
  UNIQUE (seller_id, seller_sku)
);

CREATE TABLE review_tasks (
  task_id UUID PRIMARY KEY,
  draft_id UUID NOT NULL UNIQUE,
  priority INT NOT NULL,
  status TEXT NOT NULL, -- OPEN|CLAIMED|DONE
  assignee UUID,
  lease_expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Durable upload, validate, GTIN+fuzzy, thresholds, mapping, review, publish outbox |
| 10× | Kafka stages, shard by seller, media pipeline, seller reports, matcher autoscaling |
| 100× | ANN candidates, trust tiers, ingest cells, audit lake, shadow models |
| 1,000× | Near-dupe clustering, streaming ingest, review sampling, catalog cells |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| ASIN | Shared catalog product id |
| Seller SKU | Seller-local product id |
| GTIN | Global trade identifier family |
| Blocking | Cheap candidate generation |
| T_high / T_low | Auto-map / auto-create thresholds |
| Offer | Sellable listing bound to ASIN |
| Decision | Audited match outcome |
| Publish | Make ACTIVE for customers |
| Near-dupe | Suspected duplicate ASIN cluster |

## Appendix D — Estimation cheat-sheet

```text
rows/day × stages ≠ one QPS number
fuzzy_cost ≈ fuzzy_rows/s × K_candidates
review_human_capacity << gray_zone unless automation
storage_raw ≈ rows × row_bytes
Never full-scan catalog for fuzzy
```

## Appendix E — State machines

```text
FeedJob: ACCEPTED → PARSING → MATCHING → COMPLETING → DONE
                              ↘ FAILED
Draft:   PARSED → VALID → MATCHING → FINAL|REVIEW|REJECTED
Review:  OPEN → CLAIMED → DONE
ASIN:    DRAFT → ACTIVE → SUPPRESSED
                   ↘ MERGED (redirect)
Offer:   PENDING → ACTIVE → INACTIVE
```

## Appendix F — Threshold policy sketch

```text
trusted_seller:
  T_high = 0.92; T_low = 0.55
default:
  T_high = 0.97; T_low = 0.60
high_risk_category:
  T_high = 0.99; disable AUTO_CREATE without GTIN
```

## Appendix G — Feature scoring sketch

```text
score = w1*title_sim + w2*brand_match + w3*mpn_match
      + w4*attr_overlap + w5*image_sim + w6*prior_map
explain = top contributing features for UI
```

## Appendix H — Seller result CSV columns

```text
seller_sku, status, asin, outcome, score, errors, recommendation
```

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Re-upload same content_hash | No rematch storm; same mappings |
| GTIN unique hit | AUTO_MAP |
| GTIN multi ASIN | REVIEW |
| Score in (T_low, T_high) | REVIEW not AUTO |
| Human MAP | Mapping + offer |
| Price-only change | Skip MATCH |
| Duplicate Kafka decide | One mapping version |
| Merge ASIN | Redirect offers |
| Invalid checksum GTIN | Not exact path |
| Quarantine poison row | Feed continues other rows |

## Appendix J — Runbook (interview gold)

1. Precision drop → freeze AUTO_MAP; default to REVIEW; rollback matcher_version.  
2. Review backlog fire → raise seller self-confirm; temporary T_high↑.  
3. Parser outage → raw feeds safe in S3; drain lag.  
4. GTIN conflict spike → data repair squad; stop auto on those GTINs.  
5. OpenSearch red → GTIN-only mode + alarm.

## Appendix K — Evolution hooks

```text
Variant parents / child ASINs
Contribution model for attrs (voting, trusted brand owner)
Counterfeit / brand enforcement integration
Streaming Path: seller edit API sharing MatchDecision types
Offline clustering job suggesting merges to ops
```

---

*End of design doc. Open with §1 duplicate uncertainty + precision bias; whiteboard §3.5 matching tiers + ownership; close with invariants §5.1 and traps §7.9.*
