# System Design: Google Photos-like Library (Mobile/Frontend Architecture)

> **Focus areas:** Mobile upload · Backup · Library grid · Dedup · Sync · Thumbnails · Offline · Privacy  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths  
> **Interview theme:** Uber — **mobile/frontend-heavy photos backup and library architecture**

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

Goal: design a Google Photos–style system emphasizing mobile client architecture, background backup, library sync, thumbnails, dedup, and privacy-aware sharing—with a credible backend sketch.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Backup + library UX + sync | Full social network |
| Emphasis | Mobile/frontend architecture | Only object store ops trivia |
| Uber lens | Offline-first sync patterns transferable to driver apps | Ignore mobile constraints |
| AI | Optional basic dedup/label hooks | Full Vision platform deep dive |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Backup? | Auto upload on Wi‑Fi/charging prefs | Background tasks |
| F2 | Library? | Chronological grid + albums | Local cache + remote |
| F3 | Dedup? | Hash/perceptual | Client+server |
| F4 | Thumbnails? | Multi-res | CDN |
| F5 | Offline? | Browse cached; queue uploads | Local DB |
| F6 | Sync? | Incremental changes | Cursor/token |
| F7 | Share? | Links/albums | ACL |
| F8 | Delete? | Trash + retention | Soft delete |
| F9 | Search? | Time/people/labels basic | Index hooks |
| F10 | Quota? | Storage limits | Metering |
| F11 | HEIC/video? | Transcode pipeline | Async |
| F12 | Conflict? | Same asset multi-device | Content hash identity |

**MVP functional scope (lock with interviewer):**

1. Mobile local media index + upload queue with constraints (Wi‑Fi/battery).
2. Resumable upload sessions to blob store.
3. Server asset record + derivatives (thumb/preview).
4. Library API with sync cursor; local Room/SQLite cache.
5. Grid UI virtualized; progressive image load.
6. Basic exact-hash dedup; trash/restore.
7. Auth’d share link for album.

**Out of MVP (explicitly defer):**

- Perfect face clustering globally
- Full editor suite like desktop Lightroom

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Upload reliability | Flaky mobile nets | resumable; idempotent |
| N2 | Scroll perf | 60fps grid | virtualize + thumbs |
| N3 | Battery/data | User prefs | respect constraints |
| N4 | Sync lag | Second device | seconds–minutes |
| N5 | Availability | Library reads | CDN+cache |
| N6 | Durability | Originals | multi-AZ object store |
| N7 | Privacy | Private by default | ACL |
| N8 | Cold start | Large libraries | paginated sync |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Photo taken → queued → uploaded on Wi‑Fi → thumb appears library.
2. Second device syncs new items via cursor.
3. Duplicate exact file not double-charged quota.
4. Offline scroll through cached months.
5. Share album link to friend with view ACL.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload killed mid-way | resume session |
| Hash collision rare | strong hash + size |
| Clock wrong on phone | server capture_time + client_time |
| Library 1M items | year indexes; lazy windows |
| Quota exceeded | pause queue; UX |
| Revoke share | ACL invalidate CDN tokens |
| Corrupt local DB | resync from server |
| Live photo/video large | chunked; background |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|----------|----------|----------|
| Users | 10M | 100M | 1B | 2B |
| Assets/day ingest | 50M | 500M | 5B | edge+tier |
| Avg library size | 5K | 10K | 20K | mixed |
| Read QPS thumbs | 100K | 1M | 10M | CDN |
| Regions | 1–2 | multi | multi | local |

**What each jump forces:**

- **10×:** Resumable uploads; CDN thumbs; sync cursors
- **100×:** Regional storage; async derivatives; client smarter batching
- **1,000×:** Tiered cold storage; on-device ML labels; edge upload

### 1.5 Etc. (Constraints & Assumptions)

- Design for retries, idempotency, and city/region isolation.
- Fail closed on authz/money; degrade intentionally on non-critical paths.
- Peak ≠ average; stadium/airport spikes are first-class.
- Object storage holds bytes; metadata DB holds indexes.
- Mobile OS background limits are first-class constraints.

**Scope statement:**

> Photos backup/library with mobile upload queue, resumable transfers, sync cursors, virtualized UI, derivatives CDN, dedup, sharing ACLs—frontend architecture emphasized.

---

## 2. Back-of-the-Envelope Estimation

### Ingest

```text
50M photos/day × 3MB ≈ 150PB/day raw unrealistic—typical compressed ~1–2MB; still multi-PB/month → tiering essential
```

### Thumbs

```text
50KB thumb × 50M ≈ 2.5TB/day derivatives
```

### Sync

```text
Delta items not full library each open
```

### Bottlenecks (rank ordered)

1. Upload storms evenings
2. Thumbnail stampede
3. Large library sync
4. Transcode CPU
5. Quota accounting races
6. On-device DB size

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
LocalMediaItem
UploadJob
RemoteAsset
Derivative
SyncCursor
Album/ACL
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Upload full quality only on demand | Save data | Weak backup product | Backup goal |
| B. Server-pull from camera roll | — | Impossible remotely | Security |
| C. Client queue + resumable upload + sync cursor + CDN thumbs | Fits mobile | Complexity | — chosen |
| D. Only desktop sync client | Simpler | Misses mobile | Product |

**Chosen path:**

- Offline-first client DB + constrained upload queue + resumable sessions.
- Server metadata + object storage + async derivatives.
- Incremental sync APIs; virtualized grid.

### 3.3 Core design mechanics

**Client:** observe camera roll → enqueue UploadJob → respect prefs → resumable PUT → ack asset_id → update local.

**Sync:** `GET /sync?cursor=` returns changed asset metas; client merges.

**UI:** windowed query by time; bind thumb URLs; prefetch nearby rows.

**Invariant:** content_hash idempotent ingest; originals durable; UI never blocks on full-res.

### 3.4 API sketch

```text
POST /v1/uploads/sessions {hash,size,mime} → session_url
PUT  /v1/uploads/sessions/{id}/chunks
POST /v1/uploads/sessions/{id}/complete → asset
GET  /v1/library/sync?cursor=
GET  /v1/assets/{id}/derivatives
POST /v1/albums / POST /v1/albums/{id}/share
DELETE /v1/assets/{id} (trash)
```

### 3.5 Trade-offs summary

| Decision | Trade-off |
|----------|-----------|
| Auto backup | UX vs data/battery |
| On-device vs server dedup | Privacy/data vs global quota |
| Aggressive prefetch | Smooth scroll vs data |
| Cold storage originals | Cost vs restore latency |



---

## 4. Architecture Diagram

```text
Camera Roll → Media Store observer → Upload Queue (Wi‑Fi/battery)
        → Resumable Uploader → API → Metadata DB + Object Store
                                → Derivative workers → CDN
Library UI ← Local DB cache ← Sync cursor API
Share links → ACL service → signed CDN URLs
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- Resumable idempotent uploads.
- Soft delete trash window.
- Client retry with jitter.
- Derivative failure doesn’t block original backup.

**Delivery / consistency cheat-sheet**

| Layer | Guarantee |
|-------|-----------|
| Client → API | At-least-once; idempotency keys where mutations exist |
| System of record | Single-writer per entity / partition key |
| Downstream effects | At-least-once via outbox/stream; idempotent consumers |
| Reads | Read-your-writes on primary; replicas may lag |

**Deal-breakers**

- Non-resumable multi-100MB uploads
- Full library download each launch
- Private photos world-readable URLs without auth

### 5.2 Scalability

- Regional buckets; CDN; shard metadata by user_id; cold tier; client-side pagination only.

**Progressive evolution**

| Scale | Architecture posture |
|-------|----------------------|
| Baseline | Single region/city; simple durable store + stream |
| 10× | Shard by city/entity; split hot paths |
| 100× | Cells, async fan-out, careful caching, hot-key splits |
| 1,000× | Hierarchical aggregation, edge where safe, strict cost/isolation |

### 5.3 Maintainability

- Client feature flags; upload metrics; sync conflict tests; snapshot UI tests for grid.

- Versioned schemas/configs with rollback.
- Golden fixtures and replay tools for disputes/regressions.
- Published ownership boundaries between services.
- SLOs tied to user-visible failures; load-test stadium/airport peaks.

### 5.4 Multi-region clarity

| Plane | Mode |
|-------|------|
| Edge / API gateways | Active-active |
| Mutable entity writes | Home cell / city region single-writer |
| Caches / projections | Regional, eventually consistent |
| Analytics | Async lake / warehouse |

### 5.5 Security, privacy, abuse

- Encrypted in transit; optional CSE mention; signed URLs short TTL; scrub EXIF GPS on share option.

---

## 6. Wrap-Up

**What to say in 60 seconds**

> Google Photos–style design is offline-first: constrained upload queues, resumable idempotent ingest, incremental sync cursors, virtualized thumbnail grids, and CDN derivatives—with metadata SoR and object storage bytes—scaled by user shards and tiered storage.

**MVP → next**

1. MVP: invariants + audit/outbox + single-city correctness.
2. Next: sharding, richer consumers, degradation playbooks.
3. Later: edge optimizations, hierarchical aggregation, advanced models with caps.

**Top risks**

| Risk | Mitigation |
|------|------------|
| Hot keys / stadiums | Split shards, jitter, admission control |
| Retry storms | Idempotency, client jitter, coalescing |
| Inconsistent side effects | Outbox + consumer idempotency |
| Cost explosion | Sampling, TTL, tiered storage |
| Trust / correctness bugs | Audit, clamps, kill switches |

---

## 7. Deeper / Related Interview Questions

### Mobile

**Q: Background limits?**  
A: OS task budgets; user prefs; foreground boost; partial progress persistence.

**Q: Dedup?**  
A: Exact hash MVP; perceptual later.

### Sync

**Q: Two devices upload same photo?**  
A: Same content_hash → one asset; both link.

### Scale & multi-region

**Q: How do you shard?**  
A: City/region cell first, then hash entity id within the cell.

**Q: Active-active writes for the same entity?**  
A: Avoid; home-cell single-writer with fencing on failover.

**Q: What do you shed first under load?**  
A: Non-critical analytics/marketing; protect money, safety, and trip-critical paths.

### Interview arithmetic / trap questions

**Q: When do units go wrong?**  
A: Mixing MB/GB/PB; using average instead of peak; forgetting retries amplify QPS; storing forever without sampling.

**Q: What do you defer explicitly?**  
A: Active-active multi-writer; perfect exactly-once for arbitrary side effects; unbounded history in primary OLTP.

**Q: What is the system of record?**  
A: Name it aloud—everything else is a projection/cache.

---

## 8. Appendices

### 8.1 Upload state machine

QUEUED→UPLOADING→FINALIZING→DONE / FAILED_RETRYABLE

### 8.2 Local tables

media_local, upload_jobs, remote_assets, sync_state

### 8.3 SLOs

| SLO | Target |
|-----|--------|
| Resume success | high |
| Scroll jank | rare |
| Unauthorized asset access | ~0 |

### 8.4 Frontend notes

Virtualization (RecyclerView/UICollectionView/FlashList); decoded bitmap cache caps; coalesced bind

### Interview checklist

- [ ] Clarified MVP vs out-of-scope
- [ ] Progressive 10×/100×/1000× impacts stated
- [ ] Estimation with peak ≠ average
- [ ] Single-writer / fencing story
- [ ] Idempotency + retries
- [ ] ASCII architecture
- [ ] Reliability / scalability / maintainability deep dive
- [ ] Explicit deal-breakers
- [ ] Deeper Q&A ready
- [ ] Audit / privacy / money hooks if relevant

---

*End of google photos-like library (mobile/frontend architecture) system design.*

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Driver-app transferrable lessons
Background constraints, resumable uploads, sync cursors, and virtualized lists show up in Uber driver document upload and receipt capture interviews too.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Driver-app transferrable lessons
Background constraints, resumable uploads, sync cursors, and virtualized lists show up in Uber driver document upload and receipt capture interviews too.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.

### Capacity planning worksheet (fill in interview)

```text
peak_qps = avg_qps × peak_factor (often 3–10×)
headroom = 1.5–2× peak for shard imbalance
storage_hot = entities_active × bytes × retention_hot
storage_cold = events_day × bytes × retention_cold × sample_rate
network = qps × payload × fanout
timers_or_connections = concurrent_sessions × cost_each
```

Challenge your own numbers: if storage becomes PB/month, you missed sampling/TTL.

### Failure mode & effects analysis (excerpt)

| Failure | User impact | Detection | Mitigation |
|---------|-------------|-----------|------------|
| Primary store brownout | Elevated latency / writes fail | p99 + error rate | Shed non-critical; failover |
| Stream lag | Stale projections | Consumer lag SLO | Autoscale; pause non-critical |
| Bad config push | Wrong business behavior | Canaries / golden trips | Instant rollback |
| Hot key | Localized timeouts | Shard QPS skew | Split key; admission |
| Dependency timeout | Cascade | Dependency budgets | Circuit breaker + fallback |
| Clock skew | Wrong expiries | Skew metrics | Server time authority |

### Consistency patterns cheat-sheet

| Pattern | Use |
|---------|-----|
| CAS / version column | Single-row state transitions |
| Idempotency key store | Client retries |
| Outbox | DB + message atomicity |
| Lease + fencing token | Ownership of work |
| Single-writer shard / actor | Entity mutations |
| Quorum read/write | When multi-replica truth needed |
| Event-time + watermarks | Streaming windows |

### Interview narrative tips (Uber-flavored)

1. Start with marketplace entities and SLAs (freshness, money, safety).
2. Draw the **write path** first, then reads/projections.
3. Call out **geo locality** early for mobility problems.
4. Separate **control plane** (config, experiments) from **data plane**.
5. For money: minor units, idempotency, audit, reconciliation.
6. For realtime: define freshness with a number.
7. For 1000×: talk cells, hierarchical aggregation, cost budgets.
8. End with risks + kill switches.

### Driver-app transferrable lessons
Background constraints, resumable uploads, sync cursors, and virtualized lists show up in Uber driver document upload and receipt capture interviews too.

### Additional operational notes

- Page on SLO burn, not on every transient blip; use multi-window burn rates.
- Separate **user-facing errors** from **dependency noise** in dashboards.
- Keep a per-city feature flag for emergency degradations.
- Document ownership: on-call, codeowners, escalation path.
- Every external callback needs authentication and replay protection.
- Prefer additive schema changes; use explicit version fields on events.
- Load tests should include retry amplification (clients with 3× retries).
- Stadium and airport topologies are mandatory soak scenarios.
- Archive policy must be tested via restore drills, not only backups.
- When in doubt in interview: state invariant, then mechanism, then trade-off.
