# System Design: Metadata, Governance, Lineage & Discovery (Unity Catalog–Style)

> **Focus areas:** Catalog · RBAC · Schema evolution · Audit · Discovery · Lineage · Policy enforcement  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct authz semantics, explicit enforcement points, honest lineage completeness, clear metastore vs storage boundaries  
> **Interview theme:** Databricks — control-plane design for a lakehouse; Unity Catalog–like centralized governance

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

Goal: design a **centralized metadata and governance plane** for a multi-workspace lakehouse—registering tables/volumes/models, enforcing RBAC on every query, capturing lineage, supporting schema evolution safely, and enabling discovery/search—without becoming the data path bottleneck.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the product? | Unity Catalog–like: one catalog across workspaces | Hierarchical namespace; federated enforcement |
| F2 | Entities to register? | Catalog → schema → table/view/volume/function/model | Normalized metastore schema |
| F3 | Auth model? | RBAC + optional ABAC (tags, classifications) | Privileges on securable objects |
| F4 | Enforcement point? | **Query planning path** before scan | Engine asks catalog; deny by default |
| F5 | Column-level security? | Masking + row filters for PII | Policy attached to column/table |
| F6 | Lineage? | Table/column lineage from jobs and queries | Async ingest; graph for impact analysis |
| F7 | Schema evolution? | Add columns OK; breaking changes gated | Compatibility checks + approvals |
| F8 | Audit? | Who accessed what, when, from where | Immutable append-only audit log |
| F9 | Discovery? | Search tables, columns, tags, owners | Search index synced from catalog |
| F10 | Sharing? | Cross-workspace / cross-account Delta sharing | Grant external location + credential |
| F11 | External tables? | Register cloud path without moving data | Storage credential + external location |
| F12 | Tags/classification? | `PII`, `GDPR`, `finance` propagate to lineage | Tag-based policies |
| F13 | Approvals? | Breaking DDL requires owner approval | Workflow integration optional MVP+ |
| F14 | Volumes? | Non-tabular files (ML artifacts, raw landing) | Separate securable type |
| F15 | Service principals? | Jobs/automation distinct from humans | Machine identity grants |

**MVP functional scope (lock with interviewer):**

1. **Catalog API**: create/list/drop catalog, schema, table, column metadata.
2. **RBAC**: grants on `SELECT`, `MODIFY`, `CREATE`, `USE CATALOG`, `USE SCHEMA`; inherit + explicit deny.
3. **Enforcement hook**: engine calls `authorize(principal, action, resource)` during analysis.
4. **Schema evolution**: register new columns; reject incompatible type changes without admin.
5. **Audit log**: append-only events for access, grant/revoke, DDL.
6. **Lineage ingest**: jobs emit `(source_tables, target_table, job_id)` events; store directed graph.
7. **Discovery**: search by name, owner, tag; show schema + sample lineage upstream/downstream.
8. **External locations**: bind storage URLs to credentials; prevent path escape.

**Out of MVP (explicitly defer):**

- Perfect real-time lineage for ad-hoc notebook cells (sampling OK)
- Full ABAC with arbitrary boolean expressions across all attributes
- Bi-directional active-active catalog replication globally
- Automatic PII ML classification at 99% precision
- Replacing cloud IAM entirely (catalog complements IAM)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Authz latency on query start? | Must not dominate planning | p99 < 50ms cached; < 200ms cold |
| N2 | Metastore read QPS? | Every query plans | 2K baseline; scale horizontally |
| N3 | Catalog availability? | Critical path | 99.95% monthly |
| N4 | Lineage completeness SLO? | Best effort + gaps labeled | 95% job coverage; ad-hoc 70% |
| N5 | Lineage ingest lag? | Minutes OK | p95 < 5 min behind job finish |
| N6 | Audit durability? | Compliance | 0 loss for emitted events; 7-year retention |
| N7 | Search freshness? | Near real-time | Index lag < 1 min |
| N8 | Consistency? | Strong for grants/DDL | Read-your-writes for admin APIs |
| N9 | Multi-tenant isolation? | No cross-tenant leakage | Namespace + cell boundaries |
| N10 | Fail-safe authz? | **Fail closed** on ambiguity | Deny if catalog unreachable (configurable break-glass) |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Analyst searches "customer revenue" → finds `sales.fact_orders` → checks lineage → sees upstream `raw.events` → requests access → owner grants `SELECT`.
2. ETL job finishes → emits lineage `raw.clickstream → curated.events` → downstream impact graph updated.
3. Engineer adds nullable column `device_type` → schema version bumps → BI queries continue (backward compatible).
4. SQL engine plans query → catalog returns allowed columns; masks `email` as `hash(email)`.
5. Admin revokes `SELECT` on PII table → next query fails authz immediately (cache TTL bounded).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Metastore timeout during query | Fail closed (deny) or stale cache with short TTL + alert |
| Grant cache stale after revoke | Max TTL 60s; pub/sub invalidation on revoke |
| Lineage event duplicate | Idempotent `(job_id, run_id, edge_id)` |
| Circular lineage | Store but detect cycles in impact analysis UI |
| External table path traversal | Validate path under registered external location prefix |
| Breaking schema change (drop column) | Block or require approval workflow |
| Cross-workspace share expired | Credential rotation; deny access |
| Orphan table (files exist, no catalog entry) | Discovery scan job; quarantine unregistered paths |
| GDPR delete request | Lineage identifies dependents; orchestrate delete/cascade |
| Break-glass admin access | Time-bound grant + mandatory audit reason |
| Engine bypass attempt (direct S3) | IAM scoped to catalog-vended creds only |
| Hive metastore migration | Dual-publish; cutover with parity checker |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Registered tables | 10K | 100K | 1M | 10M |
| Columns (total) | 200K | 2M | 20M | 200M |
| Principals (users+SP) | 5K | 50K | 500K | 5M |
| Workspaces / accounts | 10 | 100 | 1K | 10K |
| Authz checks / s (peak) | 5K | 50K | 500K | 5M |
| Lineage edges / day | 1M | 10M | 100M | 1B |
| Audit events / day | 5M | 50M | 500M | 5B |
| Search queries / day | 50K | 500K | 5M | 50M |
| Grant tuples | 500K | 5M | 50M | 500M |
| Metastore storage | 50 GB | 500 GB | 5 TB | 50 TB |

**What each jump forces:**

- **10×:** Authz result cache; metastore read replicas; async lineage via Kafka; ES search cluster.
- **100×:** Shard catalog by metastore cell; materialized effective-permissions; lineage graph DB partition.
- **1,000×:** Hierarchical federation; edge catalog replicas; sampled ad-hoc lineage; tiered audit cold storage.

### 1.5 Etc. (Constraints & Assumptions)

- Catalog stores **metadata**, not table bytes (those live in object storage).
- Table format (Delta/Iceberg) has its own transaction log; catalog points to storage location + schema snapshot.
- **IAM is necessary but not sufficient**—catalog RBAC is finer-grained (column, row).
- Lineage is **derived** from telemetry; may be incomplete for ad-hoc SQL.
- Compliance requires **immutable audit**—no UPDATE/DELETE on audit rows.

**Scope statement:**

> Design a Unity Catalog–like control plane: hierarchical catalog, RBAC/ABAC enforcement on query planning, schema evolution policies, immutable audit, search/discovery, and async lineage—scaling from ~10K tables / 5K authz QPS through 10× / 100× / 1,000× via caching, sharding, and async pipelines.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Authz check amplification

```text
Baseline: 500 concurrent queries
Each query touches 20 table references (joins, CTEs, views)
Authz checks if naive: 500 × 20 = 10,000 checks/s

With batch authorize API:
  500 × 1 batch(20 resources) = 500 RPCs/s
With 80% cache hit on repeated dashboard queries:
  Effective ≈ 100 RPCs/s cold + 400 cache hits
```

**Critical insight:** Governance sits on **planning hot path**—must batch and cache, never N+1 table lookups.

### 2.2 Metastore read QPS

```text
Planning requires:
  - Resolve table → storage location + schema
  - Partition stats (optional)
  - View expansion

Avg 3 metastore reads per query × 500 QPS = 1,500 reads/s baseline
10×: 15K/s → read replicas + client-side snapshot cache
100×: 150K/s → shard by catalog; co-locate cache with engines
```

### 2.3 Lineage write volume

```text
Baseline: 10K jobs/day, avg 5 edges each = 50K edges/day ≈ 0.6 edges/s avg
Peak ETL window: 100× avg → 60 edges/s sustained
100× scale: 100M edges/day ≈ 1,200 edges/s peak → Kafka + batch graph insert

Storage:
  Edge ~256 B × 100M/day × 365 ≈ 9 TB/year raw
  With compression + pruning old runs: ~2–3 TB/year
```

### 2.4 Audit log volume

```text
Baseline: 5M events/day
Event ~512 B → 2.5 GB/day → 900 GB/year
100×: 500M events/day → 250 GB/day → need tiered storage (hot 30d, cold S3/Glacier)

Ingest QPS peak: 500M / 86400 × 10 (peak factor) ≈ 58K events/s
→ Append-only log (Kafka → object storage / ClickHouse / Splunk)
```

### 2.5 Search index size

```text
1M tables × (name + desc + 50 col names + tags) ≈ 4 KB/doc → 4 GB index
10M tables → 40 GB + replicas → manageable ES cluster
```

### 2.6 Grant tuple storage

```text
500K grants × 200 B ≈ 100 MB
50M grants (100×) ≈ 10 GB
Effective permission materialization for 500K principals × 1M tables worst-case explosive
→ Compute on demand + cache; don't materialize full cross product
```

### 2.7 Authz cache sizing

```text
Cache key: (principal_id, resource_id, action) → allow/deny + policy version
Hot principals (service accounts): 1K × 10K resources × 64 B ≈ 640 MB
TTL 30–60s; invalidate on grant change via pub/sub
```

### 2.8 Bottlenecks (ranked)

1. Authz on critical path without batching/caching  
2. Metastore read storm at cluster startup (thousands of executors)  
3. Lineage graph query latency for deep graphs (100+ hops)  
4. Audit ingest backpressure during peak  
5. Grant explosion / role inheritance depth  
6. External table path validation latency  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Securable        → catalog | schema | table | view | column | volume | function
Principal        → user | group | service_principal
Privilege        → USE_CATALOG | USE_SCHEMA | SELECT | MODIFY | CREATE_TABLE | ALL
Grant            → (principal, securable, privilege, grant_option?)
Policy           → row_filter | column_mask | tag_policy (ABAC)
TableMetadata    → location, format, schema_version, owner, tags
LineageEdge      → (source, target, job_id, run_id, timestamp, column_map?)
AuditEvent       → (actor, action, resource, timestamp, ip, outcome, detail)
ExternalLocation → storage URL prefix + storage_credential binding
EffectivePerm    → computed allow/deny with inheritance chain
```

### 3.2 Namespace hierarchy (Unity Catalog–like)

```text
metastore
  └── catalog (e.g., prod, dev)
        └── schema (e.g., finance)
              ├── table fact_revenue
              ├── view v_revenue_daily
              ├── volume ml_models
              └── function udf_tax
```

**Inheritance:** grants at catalog flow to schema/table unless overridden; explicit DENY wins.

### 3.3 Options: enforcement architecture

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. IAM only | Simple | No column-level; coarse | PII compliance |
| B. Engine-local ACLs | Fast | Inconsistent across Spark/SQL | Multi-engine |
| C. Central catalog on plan path | Consistent | Latency risk | If no cache/batch |
| D. Post-hoc audit only | No plan latency | No prevention | GDPR / SOC2 |
| E. Policy agent sidecar per executor | Distributed | Hard to update revokes | Sub-minute revoke SLA |

**Chosen path:**

- **MVP:** Central catalog service; engines call batch authorize at analysis; short-TTL cache.  
- **100×+:** Regional catalog replicas; materialized effective grants for service principals; policy compilation to engine-native filters.

### 3.4 Authz latency budget (say aloud)

```text
Query planning total: 2s budget
  Parse SQL:                    200ms
  Batch catalog resolve (20):   300ms  (parallel)
  Batch authorize (20):         100ms  (cached)
  Apply masks/filters to plan:  200ms
  Optimize remainder:           1200ms
```

Uncached cold path may add 100–150ms—acceptable if rare.

### 3.5 RBAC model

| Privilege | On | Meaning |
|-----------|-----|---------|
| USE CATALOG | Catalog | See catalog exists |
| USE SCHEMA | Schema | Resolve objects in schema |
| SELECT | Table/view/column | Read data |
| MODIFY | Table | INSERT/UPDATE/DELETE/merge |
| CREATE TABLE | Schema | DDL create |
| CREATE SCHEMA | Catalog | DDL schema |
| ALL PRIVILEGES | Any | Admin on object |
| EXTERNAL USE | External location | Register paths under cred |

**Roles:** `data_engineer`, `analyst`, `pii_reader` — groups of privileges granted to principals.

```text
Effective permission:
  walk inheritance from table → schema → catalog
  union grants from all groups principal belongs to
  apply explicit DENY
  apply column masks if SELECT allowed but restricted
```

### 3.6 Schema evolution policy

| Change | Compatibility | MVP policy |
|--------|---------------|------------|
| Add nullable column | Backward compatible | Auto-allow |
| Add NOT NULL column with default | Compatible with default | Allow with default |
| Widen type (INT→BIGINT) | Usually compatible | Allow with warning |
| Narrow type | Breaking | Block / approval |
| Rename column | Breaking for views | Block / create new column |
| Drop column | Breaking | Approval + lineage impact check |
| Change partition column | Breaking | Block |

**Implementation:** schema registry version per table; engines check `reader_schema` vs `writer_schema` on write.

### 3.7 Lineage architecture

```text
Sources:
  - Scheduled jobs (Spark DAG) → deterministic edges
  - SQL warehouse query logs → parse → table-level lineage
  - Notebook cell magic → optional coarse edges
  - Ingestion pipelines (Fivetran-style) → external source node

Storage:
  - Graph: source_table → target_table edges with metadata
  - Column lineage: optional column_map JSON on edge

Query patterns:
  - Downstream impact: BFS from node (schema change blast radius)
  - Upstream root cause: reverse BFS
  - Depth limit 50; paginate for UI
```

**Completeness:** mark confidence `HIGH` (job) vs `MEDIUM` (parsed SQL) vs `LOW` (inferred).

### 3.8 Discovery / search

```text
Index fields:
  qualified_name, description, owner, tags, column_names,
  popularity (query_count_30d), last_updated

Ranking:
  text match × popularity × recency

Facets:
  catalog, schema, tag, owner, has_lineage, PII tag
```

Sync: CDC from catalog DB → Kafka → search indexer.

### 3.9 Audit design

```text
Events:
  GRANT, REVOKE, CREATE_TABLE, ALTER, DROP, SELECT (sampled?), LOGIN,
  CREDENTIAL_USE, POLICY_CHANGE, BREAK_GLASS

Store:
  hot: 90 days queryable (ClickHouse / OpenSearch)
  cold: immutable object storage WORM 7 years

Properties:
  append-only, hash chain optional for tamper-evidence
  no PII in audit payload beyond actor id
```

### 3.10 External tables & credential vending

```text
Register:
  external_location = s3://corp-data-lake/finance/
  storage_credential = IAM role or service account

Engine request:
  catalog validates table.location starts with external_location
  catalog vends temporary scoped credentials (15 min)
  engine reads Parquet directly; catalog not on data path after authz
```

**Deal-breaker:** Long-lived storage keys on user laptops.

### 3.11 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Authz fail mode | Fail closed | Security | Fail open on outage |
| Lineage | Async | Not on query path | Blocking query on lineage write |
| Revoke propagation | TTL + pub/sub | Performance | Infinite cache TTL |
| Schema breaking change | Gate + lineage | Prevent BI outages | Silent drop column |
| Audit | Sample SELECT at scale | Cost | No audit on PII access |
| Catalog vs format log | Catalog = governance; Delta log = ACID | Separation of concerns | Storing bytes in catalog |

---

## 4. Architecture Diagram

### 4.1 Control plane overview

```text
 +------------------+     +------------------+
 | Admin / Data      |     | Analyst UI       |
 | Steward UI        |     | (Search/Lineage) |
 +--------+---------+     +--------+---------+
          |                        |
          v                        v
 +--------------------------------------------------+
 |              Catalog API Gateway                  |
 |  (authn, rate limit, request routing)            |
 +------------------------+-------------------------+
                          |
     +--------------------+--------------------+
     |                    |                    |
     v                    v                    v
 +----------+      +-------------+     +--------------+
 | Metastore|      | Policy      |     | Grant/Role   |
 | Service  |      | Engine      |     | Service      |
 | (CRUD,   |      | (masks,     |     |              |
 |  resolve)|      |  row filters)|     |              |
 +----+-----+      +------+------+     +------+-------+
      |                   |                   |
      v                   v                   v
 +----------+      +-------------+     +--------------+
 | Metastore|      | Policy      |     | Relational   |
 | DB       |      | Store       |     | Grants DB    |
 | (HA)     |      |             |     |              |
 +----------+      +-------------+     +--------------+

 Async bus (Kafka)
      ^
      | lineage events, audit, CDC
      |
 +----+-----+      +-------------+     +--------------+
 | Spark /  |      | Lineage     |     | Audit        |
 | SQL      |----->| Ingestor    |---->| Pipeline     |
 | Engines  |      |             |     |              |
 +----+-----+      +------+------+     +------+-------+
      |                   |                   |
      | plan-time         v                   v
      | authorize   +-------------+     +--------------+
      +------------>| Authz Cache |     | Graph DB /   |
                    | (Redis)     |     | Search Index |
                    +-------------+     +--------------+
```

### 4.2 Sequence: query planning with authz

```text
SQL Engine        Catalog           Authz Cache       Policy Engine
    |--parse SQL---->|               |                 |
    |--batch resolve tables--------->|                 |
    |<-metadata + schema-------------|                 |
    |--batch authorize(principal, SELECT, tables)--->|
    |                 |--mget------>|                 |
    |                 |<-misses------|                 |
    |                 |--evaluate grants------------->|
    |                 |<-allow+masks-------------------|
    |                 |--mset cache->|                 |
    |<-authorized plan w/ column masks----------------|
    |--execute scan (data path bypasses catalog)------|
    |--emit audit + lineage (async)-------------------->|
```

### 4.3 Sequence: grant revoke propagation

```text
Admin UI     Grant Service    Metastore DB    Pub/Sub    Authz Cache (all nodes)
  |--REVOKE-->|                |               |              |
  |           |--txn revoke--->|               |              |
  |           |--commit--------|               |              |
  |           |--publish invalidate(key)------>|              |
  |           |                                |--fanout---->|
  |           |                                |              |--delete keys
  |<-OK-------|                                |              |
```

### 4.4 Sequence: schema evolution with impact check

```text
Engineer     Catalog API    Lineage Svc    Approval (opt)
  |--ALTER DROP COLUMN-->|          |              |
  |           |--check compat-----> FAIL breaking  |
  |           |--impact analysis------------->|    |
  |           |<-downstream 12 dashboards-------|  |
  |           |--require approval---------------->| |
  |<-PENDING--|                                   |
  |--approved------------------------------------->|
  |           |--apply DDL version bump           |
  |           |--emit audit                       |
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **No unauthorized read:** if authorize fails or times out → deny (default).  
2. **Grant durability:** acknowledged grant survives metastore failover.  
3. **Audit append-only:** no mutation of historical audit records.  
4. **External path safety:** table location ⊆ registered external location.  
5. **Schema version monotonicity:** version increments on every successful DDL.  
6. **Lineage idempotency:** duplicate job emits same edge idempotently.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Metastore primary down | Failover to replica; brief write unavailability |
| Authz cache split-brain | Short TTL; version stamp on grant epoch |
| Lineage Kafka lag | Backpressure; consumers scale; SLO alert |
| Search index stale | Degraded discovery; catalog API still authoritative |
| Policy engine bug allows PII | Canary policies; integration tests; deny override |
| Break-glass abuse | Time-bound + manager approval + enhanced audit |
| Graph DB slow for deep BFS | Depth limit; precomputed adjacency for hot tables |
| Credential vending failure | Query fails; no fallback to broad IAM role |

**Break-glass (explicit):**

```text
if emergency AND break_glass_token valid:
  allow with BREAK_GLASS audit event (reason, ticket_id)
  alert security team in real time
  auto-expire in 4 hours
else:
  deny
```

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Single-region metastore HA; Redis authz cache; Kafka lineage; ES search |
| 10× | Read replicas; batch APIs; audit to ClickHouse; graph DB sharding by catalog |
| 100× | Metastore cells per tenant; regional catalog replicas; sampled SELECT audit |
| 1000× | Federated catalogs; hierarchical lineage aggregation; cold audit tier |

**Authz batch API (critical):**

```text
authorize_batch(principal, [(action, resource), ...]) → [(decision, policies), ...]
Single round trip; cache mget for all keys; compute misses in one grant evaluation pass
```

**Metastore sharding:**

```text
shard_key = hash(catalog_id) mod N
cross-shard: rare admin queries; user queries single catalog 99% time
```

### 5.3 Maintainability

- **Policy-as-code:** row filters in versioned repo; CI tests against sample queries.  
- **Migration:** Hive metastore → UC export/import; parity checker for table counts.  
- **Observability:** authz cache hit, plan-time catalog latency, lineage lag, audit drop rate.  
- **Contract tests:** engine ↔ catalog API version compatibility.  
- **Runbooks:** revoke not taking effect → check cache TTL + pub/sub; metastore failover.

### 5.4 Progressive scale deep dive

**1× — correct MVP**

```text
Metastore: Postgres HA (Patroni)
Catalog API: gRPC + REST
Engines: hook at analysis phase
RBAC: table-level SELECT/MODIFY
Column masks: hash/email on 5 PII columns
Lineage: Spark jobs emit post-run
Audit: all DDL + grant + sample 1% SELECT
Search: ES single cluster
```

**10×**

- Redis cluster authz cache with grant epoch.  
- Metastore read replicas + connection pooling.  
- Lineage: SQL parser for warehouse queries.  
- Tag propagation job when tag added to schema.

**100×**

- Cell per business unit; cross-cell sharing via Delta Share protocol.  
- Materialized effective permissions for top 1K service principals.  
- Audit: hot/cold split; compliance export API.  
- Impact analysis precomputes downstream count cache.

**1000×**

- Federated search across cells.  
- Lineage sampling for ad-hoc; full for production jobs.  
- Graph summarization (collapse staging tables).  
- Automated classification suggestions (human confirm).

### 5.5 Column-level security enforcement

**Enforcement points (must pick consistently):**

| Point | Pros | Cons |
|-------|------|------|
| Plan rewrite (mask in scan) | Works all engines | Must not push predicate below mask |
| Engine native filter | Fast | Per-engine implementation |
| Storage encryption per column | Strong | Impractical for analytics |

**Chosen:** plan rewrite + engine pushdown guard.

```text
Original: SELECT email FROM users
Rewritten: SELECT sha2(email, 256) AS email FROM users
Guard: optimizer cannot prune mask below unauthorized join
```

**Row filter example:**

```text
Policy: region = current_user().region
Rewritten scan: ... WHERE region = 'US-WEST'  (injected)
```

### 5.6 Lineage impact analysis

```text
function downstream_impact(table, change_type):
  graph = lineage_store
  nodes = BFS(graph, start=table, direction=down, max_depth=50)
  classify nodes by:
    - dashboards (via BI metadata link)
    - production jobs (scheduled)
    - ML models (registered model link)
  return report with confidence scores

Use cases:
  DROP COLUMN → list all downstream queries referencing column (column lineage)
  GDPR DELETE → find all copies derived from user table
```

### 5.7 Discovery UX data model

```text
SearchResult:
  qualified_name: prod.finance.fact_revenue
  type: TABLE
  owner: data-finance-team
  tags: [PII, revenue]
  description: "Daily revenue fact..."
  popularity_score: 0.87
  lineage_summary: {upstream: 3, downstream: 12}
  last_altered: 2026-08-01
```

### 5.8 Hive metastore vs Unity Catalog (migration narrative)

| Hive metastore | Unity Catalog–like |
|----------------|-------------------|
| Table name + location | + catalog hierarchy + owner |
| No unified RBAC | Central grants |
| IAM separate | External locations + cred vending |
| No lineage | Built-in ingest |
| Per-workspace silo | Cross-workspace sharing |

Migration: dual-write period; read from UC, fallback Hive; validate row counts per table.

---

## 6. Wrap-Up

**Design summary**

- **Catalog** is authoritative for names, schema, ownership—not for bytes.  
- **RBAC/ABAC** enforced at **query planning** via batch authorize + bounded cache.  
- **Schema evolution** gated by compatibility rules + lineage impact.  
- **Lineage** and **audit** async, durable, compliance-grade.  
- **Discovery** via search index; catalog API remains source of truth.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Table-level RBAC | Column masks + row filters everywhere |
| Job lineage | SQL-parsed ad-hoc lineage |
| Sampled SELECT audit | Full SELECT audit for PII tables |
| Single metastore | Cells + federation |

**Top risks**

1. Authz latency/regression blocking all queries  
2. Stale cache after revoke (security)  
3. Incomplete lineage → wrong impact analysis  
4. External table path escape  

**What I'd measure first in production**

- Authz p99, cache hit rate, grant revoke propagation time, lineage lag, audit drop rate, failed plan due to GOVERNANCE.

---

## 7. Deeper / Related Interview Questions

1. Where exactly do you enforce column masks in Spark vs SQL warehouse?  
2. Fail open vs fail closed when catalog is down?  
3. How to prevent engine bypass via direct object storage access?  
4. Lineage completeness for views and dynamic SQL?  
5. Schema evolution with Delta `mergeSchema` vs strict catalog?  
6. Cross-account sharing without copying data?  
7. Compare DataHub / Amundsen vs built-in catalog?  
8. Row filter performance on large fact tables?  
9. How long to cache authz decisions after revoke?  
10. Tag-based ABAC: evaluate at plan time or storage time?  
11. Audit immutability: legal hold, WORM, hash chain?  
12. GDPR right-to-erasure orchestration using lineage?  
13. Service principal vs user delegation for jobs?  
14. Federated catalog across acquisitions?  
15. Metastore vs open table format metadata overlap?

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
| "Authz in UI only" | Plan-time enforce + IAM scoping |
| "Lineage is source of truth for ACL" | Lineage derived; catalog authorizes |
| "Cache grants forever" | TTL + epoch invalidation |
| "One big metastore forever" | Shard by catalog/cell at 100× |
| "Sync lineage on query path" | Async Kafka ingest |

---

## 8. Appendices

### A. Pseudocode — batch authorize

```text
function authorize_batch(principal, requests[]):
  epoch = grants_store.current_epoch()
  results = []
  misses = []
  for req in requests:
    key = (principal, req.resource, req.action, epoch)
    cached = cache.get(key)
    if cached: results[req] = cached
    else: misses.add(req)

  if misses not empty:
    perms = grants_store.evaluate(principal, misses)
    policies = policy_engine.compile(perms, misses)
    for req in misses:
      decision = combine(perms[req], policies[req])
      cache.set(key(req), decision, ttl=60s)
      results[req] = decision

  return results
```

### B. Pseudocode — lineage ingest (idempotent)

```text
function ingest_lineage(event):
  edge_id = hash(event.job_id, event.run_id, event.source, event.target)
  if graph.exists(edge_id): return OK
  graph.insert_edge(
    id=edge_id,
    source=event.source,
    target=event.target,
    job_id=event.job_id,
    confidence=event.confidence,
    column_map=event.column_map
  )
  search_index.update_lineage_counts(event.source, event.target)
  return OK
```

### C. Pseudocode — schema evolution gate

```text
function apply_ddl(table, ddl):
  new_schema = simulate(ddl, table.schema)
  compat = check_compatibility(table.schema, new_schema)
  if compat == BREAKING:
    impact = lineage.downstream(table)
    if not approval_exists(table, ddl):
      return REJECT_BREAKING(impact)
  metastore.update_schema(table, new_schema, version+1)
  audit.emit(ALTER, table, ddl, actor)
  return OK
```

### D. Metrics checklist

```text
catalog_resolve_latency_ms{p99}
authorize_batch_latency_ms{p99}
authz_cache_hit_ratio
grant_revoke_propagation_seconds
lineage_ingest_lag_seconds
audit_events_dropped_total
search_index_lag_seconds
metastore_db_replication_lag
break_glass_events_total
policy_evaluation_errors
```

### E. Entity-relationship sketch

```text
catalogs(catalog_id, name, owner)
schemas(schema_id, catalog_id, name)
tables(table_id, schema_id, name, location, format, schema_json, version)
columns(column_id, table_id, name, type, nullable, tags[])
grants(grant_id, principal_id, securable_type, securable_id, privilege)
policies(policy_id, securable_id, type, expression)
lineage_edges(edge_id, source_qn, target_qn, job_id, confidence)
audit_log(event_id, ts, actor, action, resource, outcome, detail_json)
external_locations(location_id, url_prefix, credential_id)
```

### F. Privilege escalation guards

```text
- GRANT OPTION required to re-grant
- Owner cannot be removed without ADMIN
- External location CREATE requires cloud ADMIN + catalog ADMIN
- Break-glass cannot grant permanent ALL PRIVILEGES
- Service principals cannot self-elevate
```

### G. Clarifying questions cheat sheet (30 seconds)

1. Multi-engine or Spark-only?  
2. Column/row security required MVP?  
3. Lineage from jobs only or SQL too?  
4. Compliance audit retention?  
5. Cross-workspace sharing?  
6. External tables percentage?

### H. Comparison — catalog products

| Capability | Hive MS | Unity-like | DataHub |
|------------|---------|------------|---------|
| RBAC enforcement | External | Built-in plan path | Metadata only |
| Lineage | No | Yes | Yes (ingest) |
| Search | Limited | Yes | Yes |
| Storage cred vending | No | Yes | No |
| Open source | Partial | Mixed | Yes |

---

*End of metadata, governance, lineage & discovery HLD prep.*
