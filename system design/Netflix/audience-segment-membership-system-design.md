# System Design: Audience Segment Membership

> **Focus areas:** Segment definition · Batch materialization · Low-latency membership lookup · Privacy · Refresh cadence · Negative segments · Size estimation
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, split dissimilar QPS, explicit deal-breakers, Netflix 2025–26 interview themes
> **Interview theme:** Netflix Ads — build and serve audience segments for targeting with fresh membership checks at ad-decision latency

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

Goal: **bound **audience segment membership**—offline construction of segments from viewing/behavior signals and online `is_member(profile, segment)` checks within ad-decision budget.**

### 1.0 What this is / is not

| Dimension | This doc | Not this |
| --- | --- | --- |
| Job | Segment build + membership lookup | Full identity graph product |
| Online | Boolean membership + optional tier | Batch-only overnight targeting |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
| --- | --- | --- | --- |
| F1 | Segment types? | Rule-based, lookalike, imported | Compiler + batch jobs |
| F2 | Online check? | During ad decision | p99 < 5–10ms |
| F3 | Offline build? | Hourly/daily refresh | Spark jobs |
| F4 | Cardinality? | Thousands of segments | Inverted indexes |
| F5 | Privacy? | No raw PII in serving bitmap | Hashed profile keys |
| F6 | Negative segments? | Exclusion lists | Separate deny bitmap |
| F7 | Size estimate? | For trafficking UI | HyperLogLog offline |
| F8 | Cross-region? | Global segments | Replicated bitmaps/CDN |
| F9 | Stale membership? | Bounded TTL | Version stamp on snapshot |
| F10 | Kids? | Exclude from ads segments | Hard filter |
| F11 | Partner segments? | Imported IDs mapped | Mapping table |
| F12 | Deletes? | GDPR propagate | Rebuild/remove from bitmap |

**MVP functional scope (lock with interviewer):**

1. Segment definition DSL with validate/compile.
2. Offline job materializes membership bitmap/roaring set per segment.
3. Online service: batch `is_member(profile, [seg...])`.
4. Snapshot version in ad decision.
5. Negative/exclusion segment support.
6. Size estimation API for ops.
7. GDPR delete pipeline.
8. Metrics: staleness, lookup p99, false rate.

**Out of MVP (explicitly defer):**

- Real-time per-play segment update on hot path
- Individual-level segment export to advertisers
- Perfect cross-device graph day one

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
| --- | --- | --- | --- |
| N1 | Hot path latency? | See plane | p99 per budget table |
| N2 | Durability? | No lost facts | Quorum + outbox |
| N3 | Availability? | Critical tier | 99.9–99.99% |
| N4 | Idempotency? | Retries safe | Keys on all writes |
| N5 | Scale | Through 1000× | Progressive table |
| N6 | Consistency? | Plane-appropriate | Strong OLTP; eventual agg |
| N7 | Audit? | Compliance | Append-only 7y |
| N8 | Privacy? | Min PII | Hash identifiers |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Segment definition DSL with validate/compile.
2. Offline job materializes membership bitmap/roaring set per segment.
3. Online service: batch `is_member(profile, [seg...])`.
4. Snapshot version in ad decision.
5. Negative/exclusion segment support.
6. Size estimation API for ops.

**Edge / failure cases**

| Case | Behavior |
| --- | --- |
| Duplicate client retry | Idempotent 200/409 |
| Downstream lag | Backpressure + DLQ |
| Regional outage | Failover bounded staleness |
| Hot key / shard | Isolate + partition key discipline |
| Bad deploy | Canary + rollback pointer |
| Late/arriving events | Watermark + reconcile |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
| --- | --- | --- | --- | --- |
| Peak write QPS | 100 | 1K | 10K | 100K |
| Peak read QPS | 1K | 10K | 100K | 1M |
| Distinct entities | 1M | 10M | 100M | 1B |
| Async events / s | 500 | 5K | 50K | 500K |
| Storage hot tier | 100 GB | 1 TB | 10 TB | 100 TB |

**Split classes:** offline build ≠ snapshot publish ≠ online membership lookup ≠ size estimate API

**What each jump forces:**

- **10×:** Roaring bitmaps per segment; CDN snapshot.
- **100×:** Partition segments; multi-get pipeline.
- **1,000×:** Two-tier hot segments + long-tail bloom.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-scale progressive design (10× → 100× → 1,000×).
- Sibling docs in INDEX.md for related systems.
- State invariants before drawing boxes.

**Scope statement:**

> Design **audience segment membership** with offline materialization and online batch lookup for ad targeting — scaling to billions of profiles through roaring bitmaps, snapshot versioning, and progressive approximations.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Profile & segment universe

```text
Ads-addressable profiles (baseline)     ≈ 100M  (excludes kids / ads-free)
Active segment definitions                ≈ 10,000
Avg segment membership rate               ≈ 5% of addressable base
Avg members / segment                     ≈ 100M × 0.05 = 5M profiles
Segments evaluated / ad decision          ≈ 50 (INCLUDE + EXCLUDE lists)
Ad decisions peak (ads tier)              ≈ 20,000 / s (from frequency-cap sibling)
```

**Split classes:** offline Spark build ≠ snapshot publish ≠ online `is_member` batch ≠ size-estimate API.

### 2.2 Roaring bitmap storage math

Roaring64 compresses sparse sets well; rule of thumb for 5M members in 100M universe:

```text
Raw bitmap (100M bits)                    ≈ 12.5 MB (uncompressed)
Roaring64 compressed (5% density)         ≈ 600 KB – 2 MB / segment (varies by clustering)
10,000 segments × 1 MB avg                ≈ 10 GB per snapshot version
3 versions retained (current + rollback)  ≈ 30 GB object store + CDN edge cache
```

Mega-segment (80M members, 80% density):

```text
Roaring blob                                ≈ 8–15 MB compressed
Must tier: hot mmap on decision nodes OR reverse-index only for mega-segments
```

### 2.3 Reverse index alternative

When **many segments per profile** dominate (50 checks × 20K decisions/s):

```text
Reverse map: profile_hash → bitset of segment_ids (or roaring of segment ordinals)
100M profiles × 50 segments avg × 1 bit   ≈ 625 MB (idealized — use compressed posting lists)
Update cost: profile joins new segment → append to profile record (offline/nearline)

Lookup: O(segments_requested) bit tests locally after one profile fetch
Storage per profile posting list (50 segs × 2B id) ≈ 100 B + overhead → 10–20 GB class at 100M
```

**Choice rule:** segment-forward (bitmap per segment) when **few segments checked, many members each**; profile-reverse when **many segments checked per user**.

### 2.4 Online lookup QPS & latency

```text
Peak is_member batch calls                  ≈ 20,000 / s (1:1 with ad decisions)
Segments / batch                            ≈ 50
Bit tests / s                               ≈ 20K × 50 = 1M / s (CPU — cheap if local mmap)
Target p99                                  < 5–10 ms including snapshot version resolve

CDN fetch (cold segment, 1 MB)            ≈ 5–20 ms edge; amortize via decision-node cache
Hot set (top 500 segments = 90% traffic)  ≈ 500 MB — fits RAM per decision pod
```

At **100×** decisions (2M/s): co-locate snapshot cache on decision nodes; never central RPC per segment.

### 2.5 Offline build throughput

```text
Daily full rebuild (worst case all segments):
  10K segments × scan 100M profile traits   → Spark cluster job
  Assume 100 TB trait lake scan / 2 h       → 14 GB/s aggregate read (parallel)
Incremental (hourly hot segments ~200):
  Only re-eval rules touching recent viewing  → minutes class

Publish: write immutable snapshot objects + atomic flip `active_version` pointer
```

### 2.6 QPS classes (split)

| Class | Baseline | 100× | 1,000× | Notes |
|-------|----------|------|--------|-------|
| Online is_member | 20K/s | 2M/s | 20M/s | local cache + mmap |
| Snapshot publish | 1/hour | 4/hour | continuous micro-batch | not decision QPS |
| Spark build | 1/day | hourly partial | streaming trait join | offline |
| Size estimate API | 10/s | 100/s | 1K/s | HLL from offline |
| Admin CRUD | 1/s | 10/s | 100/s | control plane |

### 2.7 Bandwidth (CDN snapshot fan-out)

```text
Decision pods (baseline)                    ≈ 200
Snapshot delta per hour (200 hot segments)  ≈ 200 MB
Fan-out to pods                             ≈ 200 × 200 MB = 40 GB/h ≈ 11 MB/s (acceptable)
Full snapshot push (avoid)                  ≈ 200 × 10 GB = 2 TB — use delta + lazy fetch
```

### 2.8 Latency budget (ad decision slice)

| Stage | Budget |
|-------|--------|
| Resolve active snapshot version | 0.5 ms (local) |
| Load hot bitmaps (cache hit) | 1–2 ms |
| 50× contains() checks | 1–3 ms |
| Negative segment AND logic | < 0.5 ms |
| **Membership total** | **≤ 5–10 ms p99** |

### 2.9 Critical bottlenecks

1. **SQL JOIN profiles at decision time** — latency meltdown.  
2. **Per-segment Redis SET** at 10K segments × 5M members — memory explosion.  
3. **Stale snapshot without version stamp** — silent targeting errors.  
4. **Exporting raw membership to advertisers** — privacy violation.  
5. **Single global snapshot lock** on publish — blocks reads.

### 2.10 Cost intuition

```text
Dominant: object storage + CDN + decision-node RAM for hot bitmaps
Track: $/1M membership checks, snapshot_publish_bytes, staleness_p99_minutes
Cheaper to over-provision hot cache than miss p99 and lose ad revenue
```

### 2.11 Deal-breaker

**Warehouse query or Spark job on the ad-decision hot path** — membership must be pre-materialized with bounded staleness.

---

## 3. High-Level Design

### 3.1 Planes

```text
Control Plane: config, validation, publish, audit
Data Plane: hot read/write serving path
Async Plane: logs, aggregation, recon, batch
```

### 3.2 Core entities

| Entity | Role |
|--------|------|
| SegmentDef | Rule AST |
| MembershipSnapshot | versioned bitmap |
| ProfileIndex | reverse map optional |
| SegmentStats | HLL size |

### 3.3 APIs (logical)

```text
is_member(profile_id, segment_ids[]) → Map<id,bool>
Admin: POST /segments {rule}
Internal: publish snapshot version
```

### 3.4 Store choices

| Component | Choice | Rationale |
|-----------|--------|----------|
| OLTP/config | PostgreSQL | ACID + relations |
| Hot cache | Redis | p99 reads |
| Buffer | Kafka | Spike absorb |
| Warehouse | BigQuery/Snowflake | Reporting |
| Blobs | S3 + CDN | Fan-out |

### 3.5 Consistency model

- OLTP: strong per shard
- Async: at-least-once + idempotent sinks
- Cross-region: home affinity + bounded staleness

### 3.6 Failure policy

| Failure | Policy |
|---------|--------|
| Hot store timeout | Degrade per policy; never silent money loss |
| Broker lag | Scale consumers; delay reporting banner |
| Bad deploy | Canary rollback |
| Duplicate retry | Idempotent accept |

### 3.7 Security

RBAC, scoped tokens, audit append-only, rate limits on ingress.

### 3.8 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Correctness | Idempotency + recon |
| Latency | Cache + async where safe |
| Scale | Partition discipline |
| Ops | Canary + replay |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
Data Lake→Spark Build→Bitmap Store→CDN→Decision Node cache
                ↘ Stats (HLL)
```

### 4.2 Sequence: happy path

```text
Client→API: request
API→Store: validate + persist (idempotent)
API→Async: emit event
Worker→Sink: aggregate / fan-out
Client←API: 200/202
```

### 4.3 Sequence: failure/retry

```text
Client→API: retry same idempotency key
API→IdemStore: hit → return original
No double side effect
```

### 4.4 Sequence: scale-out

```text
Load↑ → autoscale API/consumers
Partition by hash(entity_id)
Hot tenant → isolate shard/cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Idempotent writes with client keys
2. Append-only audit for money/config facts
3. Hot path never blocks on warehouse
4. Explicit failure policies per plane
5. Version stamps on all derived artifacts
6. Split QPS classes in capacity planning
7. Reconciliation detects drift
8. Privacy: minimal PII on hot path

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Duplicate client retry | Idempotent 200/409 |
| Downstream lag | Backpressure + DLQ |
| Regional outage | Failover bounded staleness |
| Hot key / shard | Isolate + partition key discipline |

### 5.2 Scalability

| Scale | Changes |
|-------|--------|
| 1× | MVP single region |
| 10× | Cache + partition + outbox |
| 100× | Regional cells + replay |
| 1,000× | Tiered storage + approx where safe |

### 5.3 Maintainability

- Structured metrics without high-cardinality labels
- Shadow/dry-run modes for risky changes
- Replay and diff tooling for async pipelines
- Runbooks linked to SLO dashboards
- Feature flags for gradual enablement

### 5.4 Exact algorithm: batch is_member

```text
function isMember(profile_id, segment_ids[], active_version):
  snap = localCache.get(active_version)  // mmap hot bitmaps
  profile_hash = H(profile_id)           // opaque, no PII in store
  result = {}
  for seg in segment_ids:
    bm = snap.bitmaps[seg]               // lazy CDN fetch on miss
    result[seg] = bm.contains(profile_hash)
  return result
```

```text
function eligibility(profile, include_segs[], exclude_segs[], version):
  inc = isMember(profile, include_segs, version)
  exc = isMember(profile, exclude_segs, version)
  return ALL(inc.values()) AND NOT ANY(exc.values())
```

Timeout policy: INCLUDE segments → fail-soft (treat missing as not-in-segment); regulatory EXCLUDE (e.g. kids) → fail-closed.

### 5.5 Offline materialization (Spark)

```text
function buildSegment(segment_def, trait_snapshot_v):
  rule_sql = compile(segment_def.ast)    // validate: no unbounded cross join
  df = spark.sql(rule_sql, traits=trait_snapshot_v)
  df = df.filter(NOT is_kids_profile)    // hard exclude
  bitmap = Roaring64Bitmap()
  for row in df.select(profile_hash):
    bitmap.add(row.profile_hash)
  write_s3(f"segments/{segment_def.id}/v{version}.pb", bitmap.serialize())
  stats[segment_def.id] = HLL.count(bitmap)  // size estimate for UI
```

Incremental path (hourly “recent watchers” segments):

```text
function incrementalUpdate(segment_id, delta_profiles_add, delta_profiles_remove):
  bm = loadBitmap(segment_id, current_version)
  bm.addAll(delta_profiles_add)
  bm.removeAll(delta_profiles_remove)
  writeNewVersion(segment_id, bm)  // immutable; flip pointer atomically
```

### 5.6 Snapshot publish & version flip

```text
function publish(snapshot_version, segment_manifest):
  for seg in segment_manifest:
    assert s3.exists(seg.path) and checksum(seg) == seg.expected_hash
  // Atomic compare-and-swap on global pointer
  if cas(active_version, old_v, snapshot_version):
    emit SegmentPublishedEvent(version, manifest)
    cdn.purgeWarm(active_version)  // background
  else:
    abort  // concurrent publish — retry or rollback
```

Readers never block: they pin `active_version` at start of ad decision batch; stale reads bounded by publish cadence (hourly MVP).

### 5.7 Negative segments & partner imports

```text
// Negative segment: separate deny bitmap per exclusion list
eligible = in(target_segment) AND NOT in(exclusion_segment)

// Partner imported IDs: map external_id → profile_hash via mapping table (offline)
// Never serve raw partner IDs on hot path — resolve at build time
function mapPartnerSegment(external_ids[]):
  return join(mapping_table, external_ids).select(profile_hash)
```

### 5.8 Scale-specific architecture

**1× (~20K decisions/s)**  
Roaring bitmap per segment in S3; top 500 segments mmap'd on decision pods. Hourly Spark rebuild. `segment_snapshot_version` stamped on every ad decision.

**10× (~200K decisions/s)**  
CDN edge cache for segment blobs; delta publish (only changed segments). Reverse index pilot for power users checking 80+ segments. HLL size API from offline stats.

**100× (~2M decisions/s)**  
Two-tier: **hot segments** (exact bitmap, 90% traffic) + **long-tail** (Bloom prefilter → exact confirm). Regional snapshot replicas; publish per region with global version. Near-line micro-batch for top 50 high-value segments.

**1,000× (~20M decisions/s)**  
Profile-reverse index sharded by `hash(profile)` for membership-heavy decisions; segment-forward for rare mega-segments. Edge decision nodes with 2 GB hot cache budget. Approx Bloom for soft targeting segments only — hard regulatory excludes remain exact.

### 5.9 Multi-region

| Data | Strategy |
|------|----------|
| Segment defs | Global control plane; versioned |
| Bitmaps | Replicated object store + regional CDN |
| Active pointer | CAS global; readers tolerate ≤1 publish interval lag |
| GDPR delete | Fan-out rebuild job per affected segment list |

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|--------|
| SQL JOIN profiles at decision | Latency meltdown |
| Per-segment Redis SET (5M members) | Memory explosion |
| Export membership to advertisers | Privacy violation |
| No version on decision | Silent stale targeting |
| Mutable bitmap in place | Race on publish |

### 5.11 Testing strategy

1. Unit: rule compiler, negative-segment logic, hash consistency.  
2. Integration: publish CAS + reader pin version.  
3. Bitmap round-trip: build → serialize → mmap → contains.  
4. Load: 50 segments × 20K is_member/s on one pod.  
5. GDPR: delete profile → absent from all rebuilt segments.  
6. Chaos: CDN miss storm → lazy fetch still within p99 budget or fail-soft.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
| --- | --- |
| Materialization | Roaring bitmap per segment |
| Delivery | Versioned snapshot CDN |
| Lookup | Pipeline multi-check |
| Privacy | Hashed profile ids |

### 6.2 Risks

1. Hot key tenant
2. Idempotency TTL too short
3. Canary false positive rollback
4. Cross-region staleness beyond SLA
5. Recon lag undetected

### 6.3 45-minute plan

| Min | Focus |
| --- | --- |
| 0–5 | Clarify planes + split QPS |
| 5–15 | Entities + APIs + stores |
| 15–25 | Hot path + idempotency |
| 25–35 | Async + recon |
| 35–45 | Scale table + deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Representation choice

**Q: Bitmap per segment vs profile → segments map?**  
A: **Segment-forward** (Roaring per segment) when you check ~50 segments against large populations — mmap + contains is O(1). **Profile-reverse** when users belong to hundreds of segments and you fetch one profile record. Netflix ads typically checks tens of segments per decision → segment-forward + hot cache wins at MVP.

**Q: Why Roaring not Redis SET?**  
A: 5M members × 10K segments in Redis SETs = tens of TB and O(N) memory per segment. Roaring compresses 5M into ~1 MB.

### 7.2 Online lookup

**Q: One RTT per segment?**  
A: No — batch all segment ids; one snapshot version pin; local mmap contains checks. CDN fetch only on cold segment cache miss.

**Q: What if membership service times out?**  
A: Policy per segment class: INCLUDE → fail-soft (not in segment, may under-target); regulatory EXCLUDE (kids, alcohol) → fail-closed (block ad).

### 7.3 Freshness & staleness

**Q: Hourly refresh OK?**  
A: Yes for most segments if you stamp `segment_snapshot_version` on ad decision and bound staleness (e.g. ≤ 90 min p99). High-value segments can get near-line micro-batch at 100×.

**Q: Real-time segment on every play event?**  
A: Not on hot path — Spark/near-line updates materialized bitmap; decision reads snapshot only.

### 7.4 Negative & compound segments

**Q: How do exclusion lists work?**  
A: Separate deny bitmap; eligibility = `in(target) AND NOT in(exclusion)`. Evaluate exclusions first for fail-closed regulatory segments.

**Q: AND/OR segment rules?**  
A: Compile to AST offline; materialize **derived segment** as new bitmap (don't interpret DSL online).

### 7.5 Lookalike & ML segments

**Q: Lookalike segments online?**  
A: Offline ML expands seed → materialize to bitmap. Don't score k-NN at decision time.

**Q: Size estimate for trafficking?**  
A: HLL or exact count from offline build — API reads stats table, not live scan.

### 7.6 Privacy & GDPR

**Q: Can advertisers get user lists?**  
A: No — only aggregate size and delivery stats. Membership store uses hashed profile ids.

**Q: User deletes account?**  
A: Rebuild or incremental remove hash from all segment bitmaps; publish new version.

### 7.7 Cross-region

**Q: User travels — segment membership?**  
A: Segments are global (viewing history); regional CDN serves same snapshot version. Staleness bounded by publish cadence, not region.

### 7.8 Interview traps

**Q: "Query warehouse at decision time"?**  
A: Latency meltdown — pre-materialize.

**Q: "Redis SET per segment"?**  
A: Memory explosion at 10K × 5M members.

**Q: "One QPS number"?**  
A: Split is_member (20K/s) vs Spark build (offline) vs publish (1/hour).

**Q: "Export segment for partner DMP"?**  
A: Policy/legal — usually hashed IDs via clean room, not raw membership API.

### 7.9 Metrics that page

**Q: What do you alert on?**  
A: `member_check_p99` burn, `segment_staleness_minutes` > SLA, publish CAS failures, CDN fetch error rate, bitmap checksum mismatch on deploy.

---

## 8. Appendices

### A1. SegmentDef schema

```text
SegmentDef {
  segment_id: UUID,
  name: string,
  type: RULE | LOOKALIKE | IMPORTED | DERIVED,
  rule_ast: JSON,              // compiled offline only
  negative: bool,                // exclusion list semantics
  refresh_cadence: HOURLY | DAILY,
  version: int64,
  state: DRAFT | ACTIVE | PAUSED
}

MembershipSnapshot {
  segment_id, snapshot_version,
  object_path, checksum, member_count_hll,
  built_at, trait_snapshot_version
}
```

### A2. Launch checklist

- [ ] Rule compiler rejects unbounded joins  
- [ ] Kids profiles hard-filtered at build  
- [ ] Publish CAS + rollback version tested  
- [ ] `segment_snapshot_version` on ad decision  
- [ ] Fail-soft vs fail-closed matrix signed  
- [ ] Hot 500 segments preloaded on decision pods  
- [ ] GDPR delete rebuild job dry-run  
- [ ] Bitmap checksum verified on CDN fetch  

### A6. 60-second summary

> Build segments **offline** (Spark → Roaring bitmaps), publish **versioned snapshots** to CDN, serve **batch is_member** on decision nodes via mmap + contains (< 5–10 ms p99). Negative segments = deny bitmaps. Never query warehouse at decision time. Stamp version; bound staleness.

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| is_member p99 | < 10 ms |
| Snapshot staleness p95 | < 90 min (hourly publish) |
| Publish success | 99.9% |
| Bitmap checksum mismatch | 0 (block deploy) |

### A9. Worked numeric example

```text
Segment "Sports_Drama_Viewer" v8841: 5M members / 100M → Roaring blob 1.2 MB
Decision checks profile p_123 against 50 segments (45 INCLUDE, 5 EXCLUDE)
  - 44 INCLUDE hits via local mmap (< 2 ms)
  - 1 cold segment fetched from CDN (1.1 MB, 8 ms) — still under p99 budget
  - EXCLUDE "Kids_Household" deny bitmap: p_123 NOT in → pass
Eligibility: all INCLUDE true AND no EXCLUDE → targetable
Ad decision logs segment_snapshot_version=8841
```

### A3. Glossary

| Term | Meaning |
|------|--------|
| SoT | Source of truth |

### A4. Interviewer traps

| Trap | Pushback |
|------|----------|
| Monolith DB | Split planes |

### A5. Reliability test plan

1. Idempotent retry returns same result
2. Canary/rollback under load
3. Regional failover with bounded staleness
4. Replay job produces identical aggregates
5. Chaos on hottest dependency
6. Scale test on split QPS class

### A6. 60-second summary

> **Audience Segment Membership** — clarify planes, idempotency, progressive scale, recon.

### A7. Related systems map

```text
See Section 4 diagram for Audience Segment Membership
```

### A8. SLO sketch

| SLO | Target |
|-----|--------|
| Hot p99 | < 100ms |

### A9. Worked numeric example

See Section 2 back-of-envelope for Audience Segment Membership baseline numbers.

### A10. Pseudo-SQL / DDL

```sql
-- See entity sketch in A1
```

### A11. Ownership

| Concern | Owner |
|---------|-------|
| Service | Platform team |

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

See INDEX.md ads data model + frequency capping (segments as targeting inputs).

---

*End of document — Netflix system design interview prep: Audience Segment Membership.*
