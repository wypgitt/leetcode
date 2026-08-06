# System Design: Ads Platform Data Model

> **Focus areas:** Advertisers · Campaigns · Line items · Creatives · Budgets · Targeting · Caps · Revenue model · ER diagram · Schema design interview  
> **Style:** Data-model-centric design with progressive scale (10× → 100× → 1,000×) for config/metadata — not full ad-serving HLD  
> **Quality bar:** Normalized OLTP core + denormalized serving snapshots, explicit hierarchy, versioning, audit, Netflix Ads 2025–26 interview themes  
> **Interview theme:** Netflix Ads — design the relational and document schema that ops, advertisers, and serving systems share for campaigns, budgets, targeting, and caps without designing the full real-time auction path

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

Goal: **ads platform data model**—the authoritative schema and entity relationships for advertisers, campaigns, line items, creatives, budgets, targeting dimensions, frequency cap rules, and revenue/billing attributes, optimized for **config correctness, audit, and serving snapshot export** — not the hot-path ad decision microsecond design.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | ER model, tables, constraints, versioning, snapshot export | Real-time auction / cap counter store |
| Users | Advertiser portal, ops, serving config CDN | Player / impression beacon |
| Writes | Low QPS campaign edits, workflow | 20K decisions/s |
| Reads | Portal queries + batch snapshot builders | Sub-10ms decision reads |
| Revenue | Contract fields, CPM/CPV model hooks | Billing ledger execution |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Core hierarchy? | Advertiser → Campaign → Line Item → Creative | 4-level tree + FK constraints |
| F2 | Campaign types? | Guaranteed, programmatic guaranteed, house | `campaign_type` enum |
| F3 | Line item role? | Targeting + budget + caps + bid/flight slice | Primary serving unit |
| F4 | Creative types? | Video 15/30s, static companion (future) | Polymorphic creative table |
| F5 | Budget levels? | Campaign total + line daily/total | Budget tables + currency |
| F6 | Targeting dimensions? | Geo, genre, content rating, device, profile tier | EAV or JSONB dimension sets |
| F7 | Frequency caps config? | Rules attached to line/campaign/creative | `cap_rules` FK to scope |
| F8 | Pacing? | Line-level delivery curves | `pacing_policy` sibling fields |
| F9 | State machine? | Draft → review → active → paused → ended | Status enums + valid transitions |
| F10 | Versioning? | Immutable published versions for serving | `config_version` snapshots |
| F11 | Multi-tenant? | Many advertisers; RBAC | `advertiser_id` on all rows |
| F12 | Audit? | Who changed what when | Audit log table |
| F13 | Categories? | Brand safety taxonomy (alcohol, etc.) | M:N creative ↔ category |
| F14 | Revenue model? | CPM primary; CPV optional | Rate fields + billing_type |
| F15 | Duplicate naming? | Unique slugs per advertiser | Unique constraints |

**MVP functional scope (lock with interviewer):**

1. Schema for Advertiser, Campaign, LineItem, Creative with FK integrity.  
2. Budget entities: lifetime + daily at line; optional campaign ceiling.  
3. Targeting: structured JSONB `targeting_spec` on line item + normalized geo table.  
4. Cap rules as rows referencing scope (line/campaign/creative).  
5. Published snapshot export: denormalized bundle per active line for serving CDN.  
6. Audit trail on all mutating ops.  
7. Soft delete / archive pattern — no hard delete of billed entities.

**Out of MVP (explicitly defer):**

- Full star schema for reporting (outline only)  
- Real-time budget decrement in OLTP (serving counters sibling)  
- Complex deal-ID programmatic OpenRTB mapping  
- Multi-currency FX engine  
- Creative transcoding metadata (CMS sibling)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Config write QPS? | Low | < 500/s peak |
| N2 | Snapshot read build? | Batch every 30–60s + on publish | Freshness < 1 min |
| N3 | Integrity | No orphan creatives in active lines | FK + checks |
| N4 | Query patterns | Portal list/filter by advertiser, status, date | Indexes |
| N5 | Retention | Years for finance audit | Partition by year |
| N6 | Multi-region | Single primary OLTP; global read replicas | Standard PG |
| N7 | Scale rows | 100K lines, 1M creatives class | See scale table |
| N8 | Migration safety | Expand-contract | Version columns |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Ops creates draft campaign → adds line → uploads creative → attaches targeting → publish → snapshot v17 exported.  
2. Advertiser pauses line → status PAUSED → next snapshot removes from eligible set.  
3. Budget increase mid-flight → new budget row effective_from → pacing sibling picks up.  
4. Cap rule added at campaign level → applies to all lines unless overridden.  
5. Creative rejected in review → line cannot publish until swapped.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Publish with expired flight dates | Validation block |
| Line budget > campaign ceiling | Check constraint fail |
| Delete advertiser with active lines | Soft archive cascade |
| Duplicate creative hash upload | Dedup optional pointer |
| Targeting spec breaking change | New schema version; old snapshots TTL |
| Concurrent edit two ops | Optimistic locking `row_version` |
| Currency mismatch line vs campaign | Enforce same currency MVP |
| Cap rule N=0 | Reject at validation |
| Overlapping flight lines same campaign | Allowed; snapshot lists both |
| Rollback publish | Republish previous immutable version id |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Advertisers | 500 | 2K | 10K | 50K |
| Active campaigns | 5K | 20K | 100K | 500K |
| Line items | 20K | 100K | 500K | 2M |
| Creatives | 100K | 500K | 2M | 10M |
| Cap rules | 50K | 200K | 1M | 5M |
| Targeting dimension rows | 200K | 1M | 5M | 20M |
| Snapshot size (active lines) | 20K × 4KB ≈ 80MB | 400MB | 2GB | 8GB |
| Config writes / day | 10K | 50K | 200K | 1M |

**Split classes:** OLTP config ≠ serving snapshot ≠ reporting warehouse ≠ hot counters.

**What each jump forces:**

- **10×:** JSONB GIN indexes; snapshot sharding by advertiser; read replicas for portal.  
- **100×:** Line item partitioning; separate cap rules table partition; S3 snapshot bundles.  
- **1,000×:** Event-sourced config changelog; regional snapshot CDN; creative metadata cold storage.

### 1.5 Etc. (Constraints & Assumptions)

- PostgreSQL-class OLTP as SoT for config (interview default).  
- Serving reads **immutable snapshots**, not live joins on hot path.  
- Revenue: **CPM** default; fields for deal rate, bonus, makegoods.  
- Netflix Ads 2025: mostly direct IO + limited programmatic.  
- Interview focus: **tables, constraints, ER**, not Redis counter design.

**Scope statement:**

> Design the ads platform relational data model (advertiser hierarchy, budgets, targeting, caps, revenue fields) with publish versioning and serving snapshot export, scaling config metadata to millions of creatives without designing the real-time serving auction.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Row counts (baseline)

```text
Advertisers           500
Campaigns           5,000  (10 per advertiser avg)
Line items         20,000  (4 per campaign)
Creatives         100,000  (5 per line avg)
Cap rules          50,000  (~2.5 per line)
Budget rows        25,000  (line + campaign ceilings)
Targeting rows     20,000  (1 spec per line)
```

### 2.2 Storage (OLTP)

```text
Campaign row ~ 2 KB (metadata + JSON)
Line item row ~ 4 KB (targeting JSON heavy)
Creative row ~ 1 KB + asset refs
Total rough:
  5K×2KB + 20K×4KB + 100K×1KB ≈ 10 MB + 80 MB + 100 MB ≈ 190 MB
Indexes + audit 3× → ~600 MB class (tiny)
```

At **100×** creatives 10M → ~10 GB + indexes → still modest OLTP.

### 2.3 Snapshot export size

```text
Denormalized line bundle ≈ 4 KB (targeting + caps + creative refs + budget summary)
Active lines 20K × 4 KB = 80 MB per full snapshot
Delta snapshots: ~5% lines change per minute → 4 MB/min
```

Serving CDN holds compressed protobuf ~40% size → 32 MB full bundle baseline.

### 2.4 Write throughput

```text
Peak human+API writes ≈ 50/s baseline (bulk edits rare)
Publish burst: 1 campaign → 10 lines → 10 TX/s for 2s
Far below PG limits
```

### 2.5 Read patterns (portal)

```text
List campaigns by advertiser: index (advertiser_id, status)
Get line detail with creatives: join 3 tables — OK at portal QPS
Search creatives by tag: GIN on JSONB
```

### 2.6 QPS classes (split)

| Class | Baseline | 100× | Notes |
|-------|----------|------|-------|
| Portal OLTP reads | 200/s | 2K/s | cached UI |
| Config writes | 20/s | 100/s | validated TX |
| Snapshot builder read | full scan 1/min | incremental | not per decision |
| Serving config fetch | CDN | CDN | not PG |
| Reporting ETL | batch | batch | warehouse |

### 2.7 Why not one big JSON document per advertiser?

```text
Pros: flexible
Cons: concurrent edit conflicts, partial validation, huge snapshots
Hybrid: normalized core + JSONB targeting_spec on line
```

### 2.8 Critical bottlenecks (at scale)

1. **Snapshot full scan** every second — use changefeed incremental.  
2. **Unindexed JSONB queries** in portal.  
3. **Cap rule explosion** without scope indexing.  
4. **Mutable in-place rows** without version for serving debug.  
5. **Hard delete** breaking audit — use archive.

### 2.9 Latency (non-serving)

| Operation | Target |
|-----------|--------|
| Portal get line | < 100ms |
| Publish campaign TX | < 500ms |
| Snapshot incremental build | < 30s lag |

### 2.10 Cost intuition

```text
OLTP DB cost negligible vs serving fleet
Invest in correctness, audit, snapshot pipeline
```

---

## 3. High-Level Design

### 3.1 Entity hierarchy

```text
Advertiser
  └── Campaign (flight, type, currency)
        └── LineItem (targeting, budget slice, pacing, priority)
              └── LineCreative (join) → Creative (asset, duration, categories)
        └── CampaignBudget (optional ceiling)
        └── CapRule (scope=campaign)
  └── AdvertiserUser (RBAC)
LineItem → CapRule (scope=line)
Creative → CapRule (scope=creative)
```

### 3.2 Core entities (logical)

| Entity | Key fields |
|--------|------------|
| `Advertiser` | id, name, billing_account, status, tier |
| `Campaign` | id, advertiser_id, name, flight_start/end, type, currency, status |
| `LineItem` | id, campaign_id, name, flight, bid_type, rate_cpm, priority, targeting_spec, status |
| `Creative` | id, advertiser_id, asset_uri, duration_ms, format, review_status |
| `LineCreative` | line_item_id, creative_id, weight, status |
| `Budget` | scope_type, scope_id, amount, period, spent_external_ref |
| `CapRule` | scope_type, scope_id, limit_n, window, subject_type, hardness |
| `PacingPolicy` | line_item_id, curve_type, params |
| `PublishVersion` | immutable snapshot id, created_at, diff_from |

### 3.3 Revenue model fields

| Field | Location | Meaning |
|-------|----------|---------|
| `billing_type` | LineItem | CPM, CPV, FLAT |
| `rate_cpm` | LineItem | Contract rate |
| `currency` | Campaign | ISO 4217 |
| `deal_id` | Campaign | IO reference |
| `bonus_impressions` | Campaign | Makegood pool |
| `agency_discount_pct` | Advertiser | Optional |

Serving uses rate for **reporting expectation**, not real-time billing SoT (measurement sibling).

### 3.4 Targeting model

**Hybrid approach:**

```text
line_items.targeting_spec JSONB  -- flexible dimensions
targeting_geo (line_item_id, geo_id, include bool)  -- normalized heavy dimension
targeting_content_tags M:N
```

Example JSONB:

```json
{
  "profile_tiers": ["ads_plan"],
  "devices": ["tv", "mobile"],
  "content_ratings_max": "PG-13",
  "genres_include": ["comedy", "drama"],
  "genres_exclude": ["horror"]
}
```

Validation schema version `targeting_schema_v`.

### 3.5 Cap rules in data model

```text
cap_rules (
  scope_type IN ('CREATIVE','LINE','CAMPAIGN','CATEGORY'),
  scope_id,
  limit_n,
  window_type,
  window_length,
  subject_type IN ('PROFILE','HOUSEHOLD','DEVICE'),
  hardness IN ('HARD','SOFT')
)
```

Multiple rules per scope allowed; serving evaluates all (sibling freq cap doc).

### 3.6 Budget model

```text
budgets (
  scope_type: 'CAMPAIGN' | 'LINE',
  scope_id,
  period: 'LIFETIME' | 'DAILY',
  amount_micros,
  effective_from,
  effective_to NULL
)
```

Spent amounts live in **serving counters**, not updated synchronously in OLTP every impression.

### 3.7 State machines

**Campaign.status:** DRAFT → PENDING_REVIEW → APPROVED → ACTIVE → PAUSED → COMPLETED → ARCHIVED

**Creative.review_status:** UPLOADED → PROCESSING → PENDING_REVIEW → APPROVED → REJECTED

Valid transitions enforced in application layer + CHECK constraints where simple.

### 3.8 Versioning & publish

```text
On publish:
  1. Validate DAG (creatives approved, flights valid, budgets positive)
  2. INSERT publish_versions (version++)
  3. INSERT snapshot_line_bundles (immutable copies)
  4. Emit event ConfigPublished(version)
Snapshot builder pushes to S3/CDN for serving
```

Edits after publish create **draft overlay** or new draft line version — no mutate ACTIVE snapshot rows.

### 3.9 RBAC

```text
advertiser_users (user_id, advertiser_id, role: ADMIN|TRAFFICKER|VIEWER)
Row-level security optional at 100×
```

### 3.10 Trade-offs summary

| Topic | Decision |
|-------|----------|
| OLTP | PostgreSQL normalized core |
| Flex targeting | JSONB + normalized geo |
| Serving read | Immutable snapshot bundles |
| Spent budget | External counters, not OLTP incr |
| Deletes | Soft archive |
| Audit | Append-only audit_log |

---

## 4. Architecture Diagram

### 4.1 Config vs serving separation

```text
+-------------+     CRUD      +------------------+
| Advertiser  |------------->| Ads Config API   |
| Portal/Ops  |              +--------+---------+
+-------------+                       |
                                      v TX
                             +--------+---------+
                             | PostgreSQL OLTP  |
                             | (this data model)|
                             +--------+---------+
                                      |
                            publish   | changefeed
                                      v
                             +--------+---------+
                             | Snapshot Builder |
                             +--------+---------+
                                      |
                                      v
                             +--------+---------+
                             | S3 / Config CDN  |
                             +--------+---------+
                                      |
                                      v
                             +--------+---------+
                             | Ad Decision Svc  |
                             | (reads snapshots)|
                             +------------------+
```

### 4.2 ER diagram (ASCII)

```text
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│ Advertiser  │1     *│  Campaign   │1     *│  LineItem   │
└─────────────┘───────└─────────────┘───────└─────────────┘
      │1                      │1                    │*
      │*                      │*                    │
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│AdvertiserUser│      │CampaignBudget│      │ LineCreative│*
└─────────────┘       └─────────────┘       └──────┬──────┘
                                                    │*
                                                    │
                                             ┌──────┴──────┐
                                             │  Creative   │
                                             └─────────────┘

LineItem ──*── CapRule
Campaign ──*── CapRule
Creative ──*── CapRule
LineItem ──1── PacingPolicy
LineItem ──*── Budget (scope=LINE)
Campaign ──*── Budget (scope=CAMPAIGN)
Creative ──*── CreativeCategory ──*── Category
```

### 4.3 Sequence: publish campaign

```text
Ops→API: POST /campaigns/{id}/publish
API→PG: BEGIN
API→PG: validate lines, creatives, budgets, caps
API→PG: INSERT publish_versions RETURNING v
API→PG: COPY active entities → snapshot_line_bundles FOR v
API→PG: COMMIT
API→Bus: ConfigPublished(v)
SnapshotBuilder→PG: read bundles v
SnapshotBuilder→S3: put protobuf bundle
CDN: invalidate / propagate
```

### 4.4 Sequence: portal edit line targeting

```text
User→API: PATCH /line_items/{id} {targeting_spec}
API→PG: UPDATE line_items SET targeting_spec=..., row_version++
API→PG: INSERT audit_log
Response: draft state; serving unchanged until publish
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **FK integrity** — no active line without campaign.  
2. **Immutable publish snapshots** — never UPDATE snapshot rows.  
3. **Audit on mutate** — who/when/old/new.  
4. **Soft archive** — billed entities retained.  
5. **Cap rules reference valid scopes** — FK or polymorphic check.  
6. **Currency consistency** within campaign tree.  
7. **Approved creative only** on publish.  
8. **Optimistic concurrency** via `row_version`.

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Single PG; full snapshot minute |
| 10× | Read replicas; GIN indexes; incremental snapshot |
| 100× | Partition cap_rules by scope_type; S3 bundle per advertiser |
| 1,000× | Event sourcing changelog; cold archive creatives |

### 5.3 Maintainability

- JSON schema validation for targeting_spec at API.  
- Migration expand-contract for column adds.  
- ER diagram in repo; codegen for API types.  
- Metrics: publish latency, validation failure rate, snapshot lag.

### 5.4 Index plan

```sql
CREATE INDEX idx_campaigns_adv_status ON campaigns(advertiser_id, status);
CREATE INDEX idx_lines_campaign ON line_items(campaign_id, status);
CREATE INDEX idx_cap_rules_scope ON cap_rules(scope_type, scope_id);
CREATE INDEX idx_creatives_adv ON creatives(advertiser_id, review_status);
CREATE INDEX idx_targeting_geo_line ON targeting_geo(line_item_id);
CREATE INDEX idx_line_items_targeting_gin ON line_items USING GIN (targeting_spec);
```

### 5.5 Polymorphic cap scope

Option A: check constraint + scope_id FK via composite  
Option B: separate nullable FKs (creative_id, line_item_id, campaign_id) exactly one NOT NULL

**Chosen:** nullable FKs for referential integrity.

### 5.6 Denormalized snapshot bundle (serving)

```text
SnapshotLineBundle {
  line_item_id, campaign_id, advertiser_id,
  targeting_spec_resolved,
  creative_candidates[{creative_id, uri, duration, categories}],
  cap_rules[],
  budget_summary{lifetime, daily, currency},
  pacing_policy,
  rate_cpm, priority, flight,
  publish_version
}
```

Built at publish — decision service O(1) lookup by line id in memory index.

### 5.7 Reporting vs OLTP

```text
OLTP: normalized, mutable drafts
Warehouse: nightly sync campaigns/lines/impressions facts
Never join impression facts back into OLTP synchronously
```

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Decision queries PG joins live | Latency + outage coupling |
| Store spent budget in line row updated per impression | OLTP melt |
| One JSON blob per campaign | Edit conflicts; validation hell |
| Hard delete campaigns | Audit / billing gaps |
| No publish version | Cannot debug "what served" |
| Cap rules only in JSON | Hard to query/validate |

### 5.9 Progressive scale deep dive

**1×**  
Single PG, nightly + on-publish snapshots, portal indexes.

**10×**  
Incremental snapshot from logical replication; advertiser-scoped CDN paths.

**100×**  
Partition large tables by created_at; creative asset metadata to object store.

**1,000×**  
Global config cells per region; CRDT draft edits rare — still publish serial per line.

### 5.10 Category taxonomy

```text
categories (id, code, parent_id, hardness_default)
creative_categories (creative_id, category_id)
Campaign may inherit category restrictions for all creatives
```

### 5.11 Revenue recognition hooks

```text
line_items.billing_type, rate_cpm, impression_cap_contractual
Measurement service computes delivered × rate → invoice sibling
Data model stores **contract terms only**
```

### 5.12 Security

- Row-level tenant isolation by advertiser_id.  
- PII minimal in ads config (billing contact separate).  
- Encrypt sensitive deal terms at rest optional.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| SoT | PostgreSQL OLTP |
| Hierarchy | Advertiser → Campaign → Line → Creative |
| Targeting | JSONB + normalized geo |
| Caps | cap_rules table with scope FKs |
| Serving | Immutable publish snapshots |
| Budget spent | External counters |

### 6.2 Risks

1. JSONB schema drift without validation  
2. Snapshot lag after publish  
3. Polymorphic FK mistakes  
4. Orphan cap rules on scope delete  
5. Portal query slow without indexes  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: data model not serving HLD |
| 5–15 | ER + hierarchy draw |
| 15–25 | Budget, caps, targeting tables |
| 25–35 | Publish versioning + snapshots |
| 35–45 | Scale, audit, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Why snapshots?

**Q: Why not query DB at decision time?**  
A: Decision needs stable low-latency config; joins across 5 tables at 20K/s unsafe.

### 7.2 Line vs campaign

**Q: Primary serving unit?**  
A: **Line item** — targeting + budget slice; campaign groups IO.

### 7.3 Creative sharing

**Q: Same creative on multiple lines?**  
A: Yes via M:N `line_creatives` with per-line weights.

### 7.4 Cap inheritance

**Q: Campaign cap + line cap?**  
A: Both rows in cap_rules; serving evaluates hierarchy (sibling doc).

### 7.5 Budget fields

**Q: Where is spent stored?**  
A: Not OLTP — pacing counters; OLTP stores limits only.

### 7.6 Targeting JSON vs EAV

**Q: Tradeoff?**  
A: JSON flexible; normalize heavy dimensions (geo) for indexing.

### 7.7 Draft vs active

**Q: Edit active campaign?**  
A: Draft copy or new version; publish promotes to snapshot.

### 7.8 Soft delete

**Q: Delete line with spend history?**  
A: ARCHIVED status; retain rows.

### 7.9 Multi-currency

**Q: Support EUR + USD?**  
A: Per campaign currency MVP; FX in billing sibling.

### 7.10 Audit

**Q: What to log?**  
A: Entity, id, actor, diff JSON, timestamp.

### 7.11 Traps

**Q: "Put frequency counters in line_items table"?**  
A: Wrong store — hot path counters separate.

**Q: "Single table ads"?**  
A: Loses integrity and query clarity.

### 7.12 Reporting schema

**Q: Star schema?**  
A: dim_advertiser, dim_campaign, dim_line, fact_impressions — warehouse, not OLTP.

---

## 8. Appendices

### A1. advertisers table

```sql
CREATE TABLE advertisers (
  advertiser_id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  slug TEXT NOT NULL UNIQUE,
  billing_account_id UUID,
  status TEXT NOT NULL CHECK (status IN ('ACTIVE','SUSPENDED','ARCHIVED')),
  agency_discount_pct NUMERIC(5,2) DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### A2. campaigns table

```sql
CREATE TABLE campaigns (
  campaign_id UUID PRIMARY KEY,
  advertiser_id UUID NOT NULL REFERENCES advertisers(advertiser_id),
  name TEXT NOT NULL,
  deal_id TEXT,
  campaign_type TEXT NOT NULL CHECK (campaign_type IN ('IO','PROGRAMMATIC','HOUSE')),
  currency CHAR(3) NOT NULL,
  flight_start TIMESTAMPTZ NOT NULL,
  flight_end TIMESTAMPTZ NOT NULL,
  status TEXT NOT NULL,
  row_version INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CHECK (flight_end > flight_start)
);
CREATE INDEX idx_campaigns_adv_status ON campaigns(advertiser_id, status);
```

### A3. line_items table

```sql
CREATE TABLE line_items (
  line_item_id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL REFERENCES campaigns(campaign_id),
  name TEXT NOT NULL,
  flight_start TIMESTAMPTZ,
  flight_end TIMESTAMPTZ,
  billing_type TEXT NOT NULL CHECK (billing_type IN ('CPM','CPV','FLAT')),
  rate_cpm_micros BIGINT,
  priority INT NOT NULL DEFAULT 100,
  targeting_spec JSONB NOT NULL DEFAULT '{}',
  targeting_schema_v INT NOT NULL DEFAULT 1,
  status TEXT NOT NULL,
  row_version INT NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### A4. creatives table

```sql
CREATE TABLE creatives (
  creative_id UUID PRIMARY KEY,
  advertiser_id UUID NOT NULL REFERENCES advertisers(advertiser_id),
  name TEXT NOT NULL,
  asset_uri TEXT NOT NULL,
  duration_ms INT NOT NULL,
  format TEXT NOT NULL CHECK (format IN ('VIDEO','STATIC')),
  review_status TEXT NOT NULL,
  creative_hash TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### A5. line_creatives join

```sql
CREATE TABLE line_creatives (
  line_item_id UUID REFERENCES line_items(line_item_id),
  creative_id UUID REFERENCES creatives(creative_id),
  weight INT NOT NULL DEFAULT 1,
  status TEXT NOT NULL DEFAULT 'ACTIVE',
  PRIMARY KEY (line_item_id, creative_id)
);
```

### A6. budgets table

```sql
CREATE TABLE budgets (
  budget_id UUID PRIMARY KEY,
  scope_type TEXT NOT NULL CHECK (scope_type IN ('CAMPAIGN','LINE')),
  campaign_id UUID REFERENCES campaigns(campaign_id),
  line_item_id UUID REFERENCES line_items(line_item_id),
  period TEXT NOT NULL CHECK (period IN ('LIFETIME','DAILY')),
  amount_micros BIGINT NOT NULL CHECK (amount_micros >= 0),
  effective_from TIMESTAMPTZ NOT NULL DEFAULT now(),
  effective_to TIMESTAMPTZ,
  CHECK (
    (scope_type = 'CAMPAIGN' AND campaign_id IS NOT NULL AND line_item_id IS NULL) OR
    (scope_type = 'LINE' AND line_item_id IS NOT NULL)
  )
);
```

### A7. cap_rules table

```sql
CREATE TABLE cap_rules (
  rule_id UUID PRIMARY KEY,
  scope_type TEXT NOT NULL,
  creative_id UUID REFERENCES creatives(creative_id),
  line_item_id UUID REFERENCES line_items(line_item_id),
  campaign_id UUID REFERENCES campaigns(campaign_id),
  limit_n INT NOT NULL CHECK (limit_n > 0),
  window_type TEXT NOT NULL,
  window_length_sec INT,
  subject_type TEXT NOT NULL DEFAULT 'PROFILE',
  hardness TEXT NOT NULL DEFAULT 'SOFT',
  state TEXT NOT NULL DEFAULT 'ACTIVE',
  CHECK (
    (scope_type = 'CREATIVE' AND creative_id IS NOT NULL) OR
    (scope_type = 'LINE' AND line_item_id IS NOT NULL) OR
    (scope_type = 'CAMPAIGN' AND campaign_id IS NOT NULL)
  )
);
CREATE INDEX idx_cap_rules_line ON cap_rules(line_item_id) WHERE line_item_id IS NOT NULL;
```

### A8. publish_versions & snapshots

```sql
CREATE TABLE publish_versions (
  version_id BIGSERIAL PRIMARY KEY,
  published_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_by UUID NOT NULL,
  notes TEXT
);

CREATE TABLE snapshot_line_bundles (
  version_id BIGINT NOT NULL REFERENCES publish_versions(version_id),
  line_item_id UUID NOT NULL,
  bundle JSONB NOT NULL,
  PRIMARY KEY (version_id, line_item_id)
);
```

### A9. audit_log

```sql
CREATE TABLE audit_log (
  audit_id BIGSERIAL PRIMARY KEY,
  entity_type TEXT NOT NULL,
  entity_id UUID NOT NULL,
  actor_id UUID NOT NULL,
  action TEXT NOT NULL,
  diff JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### A10. Launch checklist

- [ ] FK constraints on all scopes  
- [ ] Publish TX tested rollback  
- [ ] Snapshot builder lag alert  
- [ ] targeting_spec JSON schema validator  
- [ ] RLS or app-level tenant checks  
- [ ] Archive path documented  

### A11. Glossary

| Term | Meaning |
|------|---------|
| IO | Insertion order / direct deal |
| Line item | Targeting+budget serving unit |
| Snapshot | Immutable serving config bundle |
| CPM | Cost per mille impressions |
| Makegood | Bonus impressions for under-delivery |

### A12. 60-second summary

> Ads platform data model uses **normalized PostgreSQL** for **Advertiser → Campaign → Line → Creative**, **JSONB targeting**, **cap_rules and budgets** as first-class rows, **publish versions** exporting **immutable snapshots** to CDN for serving — **not** live OLTP on the ad decision hot path.

### A13. SLO sketch (config plane)

| SLO | Target |
|-----|--------|
| Publish TX success | 99.9% |
| Snapshot propagation | < 60s p99 |
| Portal read p99 | < 200ms |
| Audit completeness | 100% mutating ops |

### A14. Worked example

```text
Advertiser Nike → Campaign "Q4 Sports" → Line "US CTV Comedy"
  budget daily $10K, rate_cpm $32, targeting genres comedy, cap 3/day campaign
  creatives [15s_A, 30s_B] on line
Publish v42 → snapshot contains 1 bundle for line id L1
```

### A15. Interviewer traps

| Trap | Pushback |
|------|----------|
| OLTP on decision path | Snapshots |
| Spent in line row | Counter service |
| No versioning | Debug impossible |
| Hard delete | Audit fail |

### A16. Related systems

```text
Config API → OLTP → Snapshot Builder → CDN → Ad Decision
Impression → Measurement → Warehouse (facts)
Pacing/Freq → read cap/budget fields from snapshot; counters separate
```

### A17. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Core ER + publish |
| 10× | Incremental snapshot |
| 100× | Partition + per-adv CDN |
| 1,000× | Changelog event source |

### A18. On-call (config)

1. Snapshot lag high → builder backlog.  
2. Publish validation spike → bad bulk import.  
3. CDN stale version → purge path.

### A19. Sample snapshot bundle JSON (truncated)

```json
{
  "line_item_id": "L1",
  "publish_version": 42,
  "targeting": {"devices": ["tv"], "genres_include": ["comedy"]},
  "creatives": [{"id": "C1", "duration_ms": 15000}],
  "cap_rules": [{"scope": "campaign", "limit_n": 3, "window": "1d"}],
  "budget": {"daily_micros": 10000000000, "currency": "USD"},
  "rate_cpm_micros": 32000000
}
```

### A20. Explicit non-goals

- Real-time auction algorithm  
- Counter/key-value store design  
- Full data warehouse modeling  
- Creative transcoding pipeline  

### A21. categories tables

```sql
CREATE TABLE categories (
  category_id UUID PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  parent_id UUID REFERENCES categories(category_id)
);
CREATE TABLE creative_categories (
  creative_id UUID REFERENCES creatives(creative_id),
  category_id UUID REFERENCES categories(category_id),
  PRIMARY KEY (creative_id, category_id)
);
```

### A22. pacing_policies table

```sql
CREATE TABLE pacing_policies (
  line_item_id UUID PRIMARY KEY REFERENCES line_items(line_item_id),
  curve_type TEXT NOT NULL CHECK (curve_type IN ('EVEN','ASAP','FRONT_LOADED')),
  params JSONB NOT NULL DEFAULT '{}'
);
```

---

*End of document — Netflix system design interview prep: Ads Platform Data Model.*
