# System Design: Ads Campaign Intake System

> **Focus areas:** Trafficking API · Schema validation · Workflow states · Asset ingestion · Brand safety gates · Publish to serving snapshot · Audit & RBAC
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct entity lifecycle, integer money fields, split write QPS (draft vs publish vs asset upload), explicit deal-breakers, Netflix Ads 2025–26 themes
> **Interview theme:** Netflix Ads — intake advertiser campaigns from API/UI with validation so bad config never reaches the ad decision fleet

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

Goal: **bound **campaign intake**—the control-plane workflow that accepts advertiser trafficking requests, validates hierarchy (advertiser → campaign → line → creative), ingests assets, runs brand-safety checks, and publishes immutable serving snapshots.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Intake + validation + publish pipeline | Real-time ad auction |
| Input | Trafficking API, bulk CSV, partner feeds | Click/impression measurement |
| Output | Validated config + compiled snapshot version | Advertiser billing settlement |
| Users | Ad ops, automated partners, review queue | End viewers |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Hierarchy? | Advertiser → Campaign → LineItem → Creative | Nested CRUD with FK integrity |
| F2 | Intake channels? | REST API + ops UI + SFTP bulk | Unified ingestion adapter layer |
| F3 | Validation? | Schema, budgets, flights, targeting refs | Compiler/linter before publish |
| F4 | Assets? | Video creatives, thumbnails, VAST metadata | Object store + transcode hooks |
| F5 | Brand safety? | Auto scan + manual review queue | State machine BLOCK/ALLOW |
| F6 | Workflow? | DRAFT → REVIEW → APPROVED → PUBLISHED | Explicit transitions + audit |
| F7 | Idempotency? | Partner request keys on create | Dedupe external IDs |
| F8 | Partial updates? | Patch line budget without full resubmit | Optimistic locking + version |
| F9 | Publish? | Immutable snapshot to serving plane | Handoff to config rollout sibling |
| F10 | Rollback? | Revert to prior published version | Pointer swap, not delete |
| F11 | Multi-tenant? | Strict advertiser isolation | RLS / advertiser_id scope |
| F12 | SLA? | Publish within minutes of approval | Async jobs + status webhooks |

**MVP functional scope (lock with interviewer):**

1. CRUD for advertiser/campaign/line/creative with workflow states.
2. Schema validation + referential integrity (segments, caps refs exist).
3. Creative asset upload to object store with checksum + duration probe.
4. Brand-safety async scan with manual override queue.
5. Publish pipeline producing `ConfigVersion` + compiled snapshot.
6. Audit log: actor, diff summary, timestamp for every mutation.
7. Idempotent create by `external_traffic_id` for partner API.
8. Webhook/callback on publish success or validation failure.

**Out of MVP (explicitly defer):**

- Full self-serve UI parity with enterprise DSP
- Real-time ML creative scoring as hard gate day one
- Cross-advertiser creative sharing marketplace
- In-intake auction simulation at full QPS

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
| --- | --- | --- | --- |
| N1 | Validation latency? | Seconds OK pre-publish | p99 compile < 30s |
| N2 | API availability? | Ops critical | 99.9% |
| N3 | Durability? | No lost approved campaigns | Quorum OLTP + asset WORM |
| N4 | Concurrency? | Many editors same campaign | Optimistic version conflict 409 |
| N5 | Scale writes? | Bursty trafficking windows | See scale table |
| N6 | Security? | Partner API keys scoped | OAuth + advertiser scope |
| N7 | Audit retention? | Years for disputes | 7y append-only |
| N8 | PII? | Minimal in intake DB | Hash where possible |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Partner POST campaign bundle → validation passes → assets transcode → brand OK → publish v1001.
2. Ops edits line budget in DRAFT → version bump → re-validate → publish.
3. Duplicate partner idempotency key → 200 with original resource IDs.
4. Rejected creative → state REVIEW_FAILED with actionable errors.
5. Emergency pause campaign → publish empty eligibility for lines.
6. Bulk CSV import → row-level error report without failing entire file.

**Edge / failure cases**

| Case | Behavior |
| --- | --- |
| Targeting references deleted segment | Publish blocked; linter lists dangling refs |
| Budget below already delivered spend | Reject or force EXHAUSTED state |
| Asset transcode failure | Line stays PENDING_ASSET; retry with backoff |
| Concurrent publish race | CAS on campaign version; one wins |
| Partial bulk import | Commit valid rows; quarantine invalid with report |
| Brand safety timeout | Fail closed to REVIEW queue, not auto-approve |
| Currency mismatch | Reject at validation |
| Oversized creative | Reject with limit in error payload |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
| --- | --- | --- | --- | --- |
| Advertisers | 5K | 50K | 200K | 1M |
| Campaigns active | 20K | 100K | 500K | 2M |
| Lines active | 50K | 200K | 1M | 5M |
| Intake API writes / s | 50 | 500 | 2K | 10K |
| Publish jobs / hour | 500 | 2K | 10K | 50K |
| Asset uploads / day | 5K | 50K | 200K | 1M |
| Validation compiles / day | 10K | 50K | 200K | 1M |

**Split classes:** draft CRUD ≠ asset upload ≠ brand scan ≠ compile/publish ≠ audit export

**What each jump forces:**

- **10×:** Async job queue for compile; object store multipart upload; validation worker pool.
- **100×:** Shard OLTP by advertiser_id; CDN for compiled artifacts; bulk import streaming parser.
- **1,000×:** Regional intake cells; creative scan farm; delta snapshots; partner rate limits per tenant.

### 1.5 Etc. (Constraints & Assumptions)

- Sibling to ads data model (entities) and config rollout (publish fan-out).
- Money fields in integer minor units; never float in OLTP.
- Serving never reads draft tables — only published snapshots.
- Brand-safety categories may be fail-closed (no serve until approved).

**Scope statement:**

> Design an **ads campaign intake system** that validates and publishes trafficking config from API/UI/bulk feeds through workflow, asset ingestion, and brand-safety gates — scaling from ~50 intake writes/s through 10× / 100× / 1,000× with immutable publish handoff to serving.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Intake write rate

```text
Peak API writes ≈ 50/s baseline
Avg payload 5–20 KB JSON
50 × 20 KB ≈ 1 MB/s ingress (small)
Bulk windows: 10× burst for 15 min → queue absorbs
```

**Deal-breaker:** synchronous full compile on every PATCH.

### 2.2 Storage

```text
OLTP row ~2 KB × 5M lines ≈ 10 GB metadata
Assets: 50 MB avg creative × 200K ≈ 10 PB object store (CDN cached subset)
Audit: 500 B/event × 10M/day × 365 × 7y → tier cold archive
```

### 2.3 Publish compile

```text
Compile job: join lines + targeting + caps refs → snapshot 2–5 MB
500 publishes/hr baseline → ~0.14/s — trivial CPU if async
At 100×: 10K/hr → worker pool 50–100 cores burst
```

### 2.4 QPS classes (split)

| Class | Baseline | 100× | 1,000× | Notes |
|-------|----------|------|--------|-------|
| Draft CRUD | 50/s | 500/s | 2K/s | OLTP sharded |
| Asset upload | 5/s | 50/s | 200/s | multipart |
| Brand scan jobs | 10/s | 100/s | 500/s | async |
| Publish compile | 0.14/s | 2.8/s | 14/s | CPU bound |
| Audit reads | 20/s | 200/s | 1K/s | read replica |

### 2.5 Latency budget

| Stage | Budget |
|-------|--------|
| CRUD ACK | < 100ms p99 |
| Upload URL mint | < 50ms |
| Validation (async) | < 30s p95 |
| Publish E2E | < 2 min p95 |
| Brand manual review | human SLA |

### 2.6 Critical bottlenecks

1. Synchronous compile blocking API workers
2. Single-table campaigns without advertiser shard
3. Asset virus scan inline on request thread
4. Bulk import loading entire file into memory
5. Missing idempotency on partner creates

### 2.7 Cost intuition

```text
Dominant: object storage + transcode + brand ML scan
OLTP modest; optimize publish fan-out not intake DB
Track $/1K publishes and failed validation rate
```

### 2.8 Deal-breaker

Serving reading mutable draft rows — always publish immutable snapshot.

---

## 3. High-Level Design

### 3.1 Planes

```text
Control Plane: Intake API → OLTP → Workflow → Validator → Publisher
Asset Plane: Upload → Scan → Transcode → Catalog metadata
Safety Plane: Auto classifier → Manual review queue
Serving Handoff: CompiledSnapshot + ConfigVersion → Rollout sibling
```

### 3.2 Entities

| Entity | Role |
|--------|------|
| Advertiser | Tenant root |
| Campaign | Budget/flight container |
| LineItem | Targeting + pricing + pacing refs |
| Creative | Asset refs + duration + tags |
| IntakeJob | Bulk import tracker |
| PublishVersion | Immutable output |
| AuditEntry | Append-only change log |

### 3.3 Workflow states

| State | Meaning |
|-------|--------|
| DRAFT | Editable |
| VALIDATING | Linter running |
| REVIEW | Brand/safety human |
| APPROVED | Ready to publish |
| PUBLISHED | Snapshot live |
| PAUSED | Eligibility off |
| ARCHIVED | Historical |

### 3.4 Intake API (logical)

```text
POST /advertisers/{id}/campaigns (Idempotency-Key)
PATCH /lines/{id} (If-Match: version)
POST /lines/{id}/creatives/upload-url
POST /campaigns/{id}/publish
GET /campaigns/{id}/validation-errors
```

### 3.5 Validation pipeline

```text
1. JSON schema + business rules
2. FK checks: segments, cap rules, currencies
3. Asset readiness: transcoded, duration match
4. Brand safety score thresholds
5. Simulation: zero eligible users warning (optional)
Output: ValidationReport { errors[], warnings[] }
```

### 3.6 Publish handoff

```text
publish(campaign_id):
  assert state == APPROVED
  compiled = compile(lines, creatives, rules)
  version = insert config_versions
  upload compiled to object store
  emit PublishEvent → Rollout Controller
  state = PUBLISHED
```

### 3.7 Store choices

| Component | Choice |
|-----------|--------|
| OLTP | PostgreSQL sharded by advertiser |
| Assets | S3 + CDN |
| Jobs | SQS/Kafka + workers |
| Audit | Append-only table + WORM export |
| Idempotency | Redis/Dynamo TTL |

### 3.8 Failure policy

| Failure | Policy |
|---------|--------|
| Validation fail | Stay DRAFT; return errors |
| Publish fail mid-flight | Retry job; no partial pointer |
| Asset scan malware | Quarantine; alert security |
| DB conflict | 409; client refresh |

### 3.9 Consistency

- OLTP strong per advertiser shard
- Publish is single-writer per campaign version
- Serving reads only immutable snapshots (eventual fan-out)

### 3.10 Trade-offs

| Topic | Decision |
|-------|----------|
| Draft mutability | Allowed until publish |
| Validation | Async for heavy checks |
| Bulk import | Partial success OK |
| Brand safety | Fail closed to review |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+----------+    CRUD     +-------------+    jobs    +----------------+
| Partner  |----------->| Intake API  |--------->| Validator/     |
| / Ops UI |            +------+------+          | Compiler       |
+----------+                   |                 +-------+--------+
                               v                         |
                        +------+------+                  | publish
                        | OLTP Store  |                  v
                        +-------------+          +-------+--------+
                                                     | Object Store   |
                                                     +-------+--------+
                                                             |
                                                             v
                                                     +-------+--------+
                                                     | Config Rollout |
                                                     +----------------+
```

### 4.2 Sequence: publish

```text
Ops→API: POST publish(campaign)
API→OLTP: CAS state APPROVED
API→JobQueue: compile job
Worker→OLTP: load graph
Worker→ObjectStore: put snapshot
Worker→Rollout: notify version
Worker→OLTP: state PUBLISHED
```

### 4.3 Sequence: asset upload

```text
Client→API: request upload URL
API→ObjectStore: presigned PUT
Client→ObjectStore: upload bytes
ObjectStore→Event: ObjectCreated
TranscodeWorker→SafetyScan→OLTP: attach metadata
```

### 4.4 Sequence: validation failure

```text
Client→API: PATCH line targeting
API→OLTP: save draft
API→Validator: enqueue
Validator→SegmentSvc: resolve segment_id
SegmentSvc→404
Validator→OLTP: errors[]
API→Client: 422 with field paths
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Published snapshots are immutable.
2. Idempotent partner creates by external key.
3. Brand-safety fail closed.
4. Audit append-only.
5. Money integer minor units.
6. Serving never reads DRAFT.
7. Publish is CAS on campaign version.
8. Validation errors are actionable field paths.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Concurrent publish | One wins CAS; other 409 |
| Transcode stuck | Alert; SLA breach page |
| Bulk row bad targeting | Quarantine row; continue file |
| Partner retry storm | Rate limit + idempotent 200 |

### 5.2 Scalability

| Scale | Changes |
|-------|--------|
| 1× | Monolith intake + PG + S3 |
| 10× | Job workers; read replicas |
| 100× | Advertiser shards; scan farm |
| 1,000× | Regional intake; delta compile |

### 5.3 Maintainability

- Structured metrics without high-cardinality labels
- Shadow/dry-run modes for risky changes
- Replay and diff tooling for async pipelines
- Runbooks linked to SLO dashboards
- Feature flags for gradual enablement

### 5.4 Core algorithms

```text
function validateCampaign(campaign_id):
  g = loadGraph(campaign_id)
  errs = []
  errs += schemaLint(g)
  errs += fkLint(g)  // segments, caps
  errs += assetLint(g)
  errs += brandLint(g)
  return errs

function publish(campaign_id, expected_version):
  if not casState(campaign_id, APPROVED, expected_version): throw 409
  compiled = compile(loadGraph(campaign_id))
  v = storeSnapshot(compiled)
  rollout.notify(v)
  setState(PUBLISHED)
```

### 5.5 Multi-region

| Data | Strategy |
|------|----------|
| Hot path | Regional cells + home affinity where needed |
| Config | Global SoT with cached replicas |
| Async | Partitioned logs; idempotent consumers |
| DR | RPO/RTO documented per plane |

### 5.6 Security & privacy

- RBAC on control APIs
- Minimize PII on hot path; hash identifiers
- Audit append-only for money/config changes
- Rate limits and abuse detection on public ingress

### 5.7 Observability

| Metric | Use |
|--------|-----|
| p99 latency by plane | SLO tracking |
| Error rate delta post-deploy | Canary gates |
| Lag / queue depth | Async health |
| Drift / recon diff | Money & facts correctness |

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|--------|
| Sync compile on PATCH | API meltdown |
| Skip brand on 'trusted' partner | Incident |
| Float budgets | Money bugs |
| No idempotency | Duplicate campaigns |

### 5.9 Progressive scale deep dive

**1× (~50 writes/s)**
Single region; manual brand queue.

**10×**
Worker pools; presigned uploads.

**100×**
Shard OLTP; parallel bulk.

**1,000×**
Regional cells; delta snapshots.

### 5.10 Testing strategy

1. Unit: pure logic (validators, compilers, aggregators)
2. Integration: store + idempotency + outbox
3. Chaos: regional fail, cache cold, broker lag
4. Load: 10× burst on hottest class only
5. Recon: batch compare SoT vs derived views

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
| --- | --- |
| Draft vs published | Separate tables + immutable snapshot |
| Validation | Async compiler with sync schema gate |
| Assets | Presigned upload + event-driven transcode |
| Brand | Auto + manual queue fail-closed |
| Handoff | ConfigVersion to rollout sibling |

### 6.2 Risks

1. Bad publish reaches fleet without canary (mitigate: rollout sibling)
2. Asset copyright disputes (legal workflow)
3. Bulk import partial state confusion
4. Partner idempotency TTL too short
5. Validation drift vs serving compiler version

### 6.3 45-minute plan

| Min | Focus |
| --- | --- |
| 0–5 | Intake vs serving plane split |
| 5–15 | Entity hierarchy + workflow |
| 15–25 | Validation + brand safety |
| 25–35 | Publish snapshot handoff |
| 35–45 | Scale + idempotency + audit |

---

## 7. Deeper / Related Interview Questions

### 7.1 Scope

**Q: Intake vs data model?**
A: Data model defines entities; intake is workflow + validation + publish.

**Q: Why not edit serving directly?**
A: Audit, validation, blast radius.

### 7.2 Validation

**Q: Sync or async?**
A: Sync schema; async heavy compile/brand.

**Q: Partial bulk failure?**
A: Row-level quarantine with report.

### 7.3 Assets

**Q: Why presigned upload?**
A: Keeps API off bytes path; scales bandwidth.

**Q: Transcode failure?**
A: Block publish for that creative.

### 7.4 Publish

**Q: Immutable versions?**
A: Rollback + reproducibility.

**Q: Who triggers rollout?**
A: Publish event to rollout controller.

### 7.5 Money

**Q: Float budgets?**
A: Never — integer minor units.

### 7.6 Multi-tenant

**Q: Cross-advertiser leak?**
A: RLS + scoped API keys.

### 7.7 Ops

**Q: Emergency pause?**
A: Publish empty eligibility snapshot.

### 7.8 Traps

**Q: 'Just CRUD to Postgres'**
A: Missing validation/compile/snapshot.

---


## 5.11 Bulk CSV import format

```text
columns: external_id, campaign_name, line_name, budget_minor, currency,
         flight_start, flight_end, segment_id, creative_uri, ...
Row-level validation → ImportReport { accepted[], rejected[{row, errors[]}] }
Partial commit OK; rejected rows never half-create hierarchy
```

## 5.12 Brand safety pipeline

```text
Upload complete → transcode → auto_classifier (audio/video/frame)
Scores → if above threshold → REVIEW queue
Human reviewer APPROVE/REJECT with reason code
REJECT blocks publish for that creative; campaign may publish other lines
```

## 7.9 Intake questions

**Q: Edit after publish?**  
A: New draft version → re-approve → new ConfigVersion; never mutate published snapshot.

**Q: Partner SLA on publish?**  
A: Webhook on PUBLISHED or VALIDATION_FAILED; async within minutes not seconds.


## 8. Appendices

### A1. Core schema sketch

```text
Campaign { id, advertiser_id, name, budget_minor, currency, flight_start, flight_end, state, version }
LineItem { id, campaign_id, targeting_json, pricing_model, pacing_mode }
Creative { id, line_id, asset_uri, duration_ms, brand_tags[] }
```

### A2. Launch checklist

- [ ] Idempotency keys on partner API
- [ ] Brand fail-closed tested
- [ ] Publish never reads DRAFT
- [ ] Audit retention policy
- [ ] Bulk import partial success

### A3. Glossary

| Term | Meaning |
|------|--------|
| Intake | Control-plane ingestion |
| Snapshot | Compiled immutable serving artifact |

### A4. Interviewer traps

| Trap | Pushback |
|------|----------|
| Edit live serving | Publish versions |
| Skip validation | Fleet incidents |

### A5. Reliability test plan

1. Idempotent retry returns same result
2. Canary/rollback under load
3. Regional failover with bounded staleness
4. Replay job produces identical aggregates
5. Chaos on hottest dependency
6. Scale test on split QPS class

### A6. 60-second summary

> **Campaign intake** = validated trafficking workflow + assets + brand gates → immutable publish to serving rollout.

### A7. Related systems map

```text
Partner → Intake API → OLTP → Validator → Publisher → Rollout → Decision Fleet
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| CRUD p99 | < 100ms |
| Publish E2E p95 | < 2 min |

### A9. Worked numeric example

See Section 2 back-of-envelope for Campaign Intake baseline numbers.

### A10. Pseudo-SQL / DDL

```sql
CREATE TABLE campaigns (
  id UUID PRIMARY KEY,
  advertiser_id UUID NOT NULL,
  budget_minor BIGINT NOT NULL,
  currency CHAR(3) NOT NULL,
  state TEXT NOT NULL,
  version BIGINT NOT NULL
);
```

### A11. Ownership

| Concern | Owner |
|---------|-------|
| Intake API | Ads Control Plane |
| Brand review | Trust & Safety |

### A12. Progressive checklist

| Scale | Must have |
|-------|----------|
| 1× | MVP invariants + metrics |
| 10× | Idempotency + cache + partition discipline |
| 100× | Regional cells + replay tooling |
| 1,000× | Tiered hot/cold + approximations where safe |

### A13. Naive design comparison

| Naive | Why it fails |
|-------|--------------|
| One DB for everything | Wrong latency class |
| No idempotency | Retries corrupt state |
| Single global queue | Hot key meltdown |
| Skip canary/validation | Fleet-wide incidents |

### A14. On-call cheat sheet

1. Check error rate delta vs deploy
2. Check lag on async plane
3. Verify idempotency / dedupe store health
4. Roll back pointer/config if SLO breach
5. Page if money/facts drift exceeds threshold

### A15. Sample debug record

```text
{
  "trace_id": "tr_abc",
  "entity_id": "ent_xyz",
  "version": 42,
  "region": "us-west-2",
  "outcome": "OK"
}
```

### A16. Cost worksheet

```text
dominant = hot_storage + stream_compute + cross_region_egress
track $/1M events and MTTR for rollbacks
```

### A17. Explicit non-goals

- Perfect global strong consistency on all reads
- Building all sibling systems in one interview
- Client-trusted counts as billing SoT

### A18. Interview rubric

- Clarify planes and split QPS
- State invariants early
- Progressive scale table
- Deal-breaker gallery
- Wrap with risks + test plan

### A19. Migration / rollout notes

Dual-write or shadow-read when replacing SoT; never big-bang cutover without recon period.

### A20. Further reading (siblings)

See INDEX.md for related Netflix docs: frequency capping, pacing, ads data model, homepage dedup, streaming, CDN.

---

*End of document — Netflix system design interview prep.*

---

*End of document — Netflix system design interview prep.*
