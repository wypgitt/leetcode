Dropbox File Sync

> **Focus areas:** Chunking · Dedup · Sync protocol · Metadata · Sharing · Versioning · Conflict · Multi-device
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Databricks — file sync, chunking, metadata correctness; pairs with ranged-file-cache LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-q&a)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design **Dropbox-like file storage**: upload/download, chunking+dedup, namespace metadata, multi-device sync, sharing, versioning, conflict handling, and strong durability.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Cloud files + sync clients | Full Google Docs collab editing |
| Unit | Files/chunks/namespaces | Block storage for VMs |
| Amazon lens | Durability, sync correctness, cost | USB drive metaphor only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Upload/download? | Chunked resumable | Retry safe |
| F2 | Dedup? | Content-hash chunks | Cross-user optional policy |
| F3 | Namespace? | Tree per user/team | Strong meta ops |
| F4 | Sync? | Delta + cursor | Multi-device |
| F5 | Sharing? | Links/ACLs | Authz |
| F6 | Versions? | History + restore | Retention |
| F7 | Conflicts? | Rename/keep both | No silent lose |
| F8 | Search? | Name/meta MVP | Content search later |
| F9 | Offline? | Client local + queue | Eventual sync |
| F10 | Enterprise? | Admin, DL P hooks | Cells |
| F11 | Preview? | Async generators | Optional |
| F12 | Quotas? | Bytes/devices | Fair |

**MVP scope:**

1. Chunk upload/download
2. Namespace CRUD
3. Sync cursor/delta
4. Sharing links+ACL
5. Versions basic
6. Conflict=keep both
7. Dedup within account
8. Quotas
9. Audit deletes

**Out of MVP:** CRDT realtime co-editing; Global cross-user dedup always-on; Bit-perfect LAN sync p2p MVP.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Meta op | p99<100–200ms |
| N2 | Sync lag | seconds typical |
| N3 | Durability | 11-nines chunks |
| N4 | Consistency | Namespace linearizable per user |
| N5 | Conflict | Never silent drop |
| N6 | Avail | 99.9%+ |
| N7 | Cost | Dedup+cold tier |
| N8 | Privacy | ACL enforced |

### 1.3 Cases

**Happy:** chunk upload→commit file→other device delta sync; share link; restore version.
**Edges:** conflict dual edit; partial chunk; hash collision (assert); revoke share; huge directory; reinstall resync; ransomware version wipe.

| Case | Behavior |
|------|----------|
| Duplicate request | Idempotent key returns same result |
| Partial failure mid-path | Compensate or retry with fencing/CAS |
| Hot partition / noisy neighbor | Shuffle shard + fair-share quotas |
| Region / AZ loss | Cell failover; degrade non-critical |
| Clock skew | Server-side truth; opaque tokens |
| Poison input | Quarantine/DLQ; never silent drop of accepted work |
| Authz miss | Fail closed; audit |
| Traffic surge 10× | Shed by priority; preserve SLO class |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Users | 50M | 500M | 5B | — |
| Files | 10B | 100B | 1T | 10T |
| Stored logical | 50PB | 500PB | 5EB | 50EB |
| Sync QPS peak | 100K | 1M | 10M | 100M |
| Chunk size | 4MB | 4MB | 4MB | 1–4MB adaptive |
| Devices/user | 3 | 3 | 4 | 5 |

**Jumps:** 10× meta shard+chunk store; 100× cells+regional; 1,000× smarter sync+edge caches.

### 1.5 Scope repeat-back

> Chunked durable store + namespace metadata + delta sync + sharing/versioning with explicit conflicts.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Chunk math

```text
4MB chunks; 1GB file=256 chunks; hash index huge
```

### 2.2 Meta

```text
File rows + tree; list dir hot
```

### 2.3 Sync

```text
Delta feed per namespace; cursor
```

### 2.4 Dedup

```text
Hash→chunk_id map; refcounts
```

### 2.X Bottlenecks

(1) Hot keys/partitions (2) synchronous fan-out (3) durable write path (4) auth/token validation (5) downstream blast radius (6) not abstract QPS alone.

### 2.Y Cost / frugality

Prefer cheaper read paths over linear DB growth; measure unit cost per successful customer action; sample observability firehoses.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Chunk store | Bytes immutable | Durable |
| Metadata | Namespace/tree | Strong per ns |
| Sync | Cursors/deltas | Per device |
| Sharing | ACL/links | Strong |
| Process | Preview/virus | Async |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Client sync engine** — Local journal
2. **Meta service** — Tree/ACLs
3. **Chunk service** — Put/get hash
4. **Block store** — Objects
5. **Sync feed** — Delta log
6. **Share service** — Links
7. **Version GC** — Retention
8. **Quota** — Bytes
9. **Scan** — Malware
10. **Notify** — Push wake
11. **Admin** — Enterprise
12. **Search index** — Names

### 3.3 API sketch

```text
POST /chunks/{hash}
POST /files/commit {path,chunks[],rev}
GET /delta?cursor=
POST /share
POST /restore/{rev}
```

### 3.4 State machine

```text
File rev N→N+1 commit
Chunk: UPLOADING→COMMITTED→GC_CANDIDATE
Share: ACTIVE→REVOKED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Sync vs backup | Sync+history | Product |
| Cross-user dedup | Off/default account | Privacy |
| Conflict | Keep both | No silent lose |
| Chunk size | ~4MB | Balance |
| Meta DB | Keyspace by ns | Scale lists |

---

## 4. Architecture Diagram

```text
Clients<->Sync/Meta API<->Namespace DB
Clients<->Chunk API<->Object Store
Delta Log->Notify->Clients; Share/ACL->Meta
```

### 4.1 Commit

```text
Client uploads missing chunks; commit rev CAS; append delta
```

### 4.2 Sync

```text
Pull delta from cursor; fetch chunks; apply
```

### 4.3 Conflict

```text
CAS fail→branch/rename; surface to user
```

### 4.N Cell / blast-radius model

```text
Each cell = failure domain (AZ-set or region slice)
No synchronous cross-cell locks on hot path
Control plane pushes config; data plane serves locally
Shuffle sharding for multi-tenant isolation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Commit only if chunks present
2. Rev CAS for path updates
3. No silent overwrite on conflict
4. ACL checked every download
5. Refcount GC safe
6. Delete/revoke honored
7. Quota before accept
8. Delta cursor monotonic

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | PG meta+S3 chunks |
| 10× | Shard ns; CDN download |
| 100× | Cells; regional affinity |
| 1000× | Edge caches; adaptive chunking |

### 5.3 Maintainability

- Client protocol versioning
- GC canaries
- Conflict UX metrics
- Hash migration plan

### 5.4 Progressive scale narrative

**1×:** Single region
**10×:** Sharded meta
**100×:** Multi-region cells
**1000×:** Smart sync + WAN optimize

### 5.5 CAS revs

Namespace path rev fencing prevents lost updates.

### 5.6 Dedup refcount

GC only at 0; race-safe.

### 5.7 Delta log

Per-namespace partitioned stream.

### 5.8 Ransomware

Version history + atypical delete alerts.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| Silent conflict win | Data loss trust SEV |
| Chunk without hash verify | Corruption |
| Global lock tree | Meltdown |
| Cross-user dedup naive | Privacy leak |
| Unbounded versions | Cost blowup |
| Meta in client only | Split brain |

---

## 6. Wrap-Up

### 6.1 Designed

Dropbox-like: chunked immutable store, strong namespace meta with rev CAS, delta sync, sharing, versions, explicit conflicts.

### 6.2 Decisions to defend

1. Content-hash chunks
2. Rev CAS commits
3. Keep-both conflicts
4. Account-scoped dedup default
5. Delta cursors
6. Version retention policy
7. Push notify
8. ACL on every get

### 6.3 Risks

- Huge directories
- Sync storms
- GC bugs
- Client protocol skew
- Share leaks

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Sync vs backup |
| 5–15 | Chunk+dedup math |
| 15–25 | Meta+CAS |
| 25–35 | Delta/conflict/share |
| 35–45 | Scale+GC+enterprise |

### 6.5 Closer

> **Dropbox-like File Storage**: immutable chunks, CAS namespace, delta sync, explicit conflicts, ACL everywhere, cost-aware GC.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Chunk size?

~4MB adaptive.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Dedup scope?

Account default.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Conflict policy?

Keep both.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Rev CAS?

Lost-update prevention.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Delta design?

Per-ns log+cursor.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Sharing revoke?

Immediate authz deny.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Offline?

Local journal replay.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Hash algo?

SHA-256; verify.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: GC?

Refcount+safety delay.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Team spaces?

Namespace type.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Preview?

Async.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: LAN sync?

Later optimization.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Encryption?

SSE; optional CSE.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Search?

Names first.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

Silent conflict overwrite.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

$/GB logical vs physical.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

---

## 8. Appendices

### A. Glossary

| Term | Meaning |
|------|---------|
| Cell | Isolated failure domain for blast-radius control |
| Fence / fencing token | Invalidates stale writers after lease steal |
| Idempotency key | Client key making retries safe |
| Outbox | Durable event publish coupled to DB commit |
| Shuffle sharding | Map tenants to overlapping server subsets |
| SLO / error budget | Reliability contract; burn rate drives decisions |
| Unit cost | $ per successful customer action |
| DLQ | Dead-letter queue for poison / exhausted retries |
| Control vs data plane | Config/orchestration vs hot-path serving |
| Progressive scale | Explicit 10×/100×/1,000× architecture jumps |

### B. Ownership matrix

| Concern | Owns | Pages when |
|---------|------|------------|
| Hot-path latency/errors | Serving team | p99 / 5xx burn |
| Durability / data loss risk | Storage/data team | RPO/RTO alarms |
| Abuse / security | Trust & safety / AppSec | exploit or abuse spike |
| Cost regression | Serving + FinOps | unit-cost burn |
| Downstream dependency | Owning service | dependency SEV |

### C. Metrics that matter

- Success rate by criticality class
- Latency histograms (p50/p90/p99) on customer-visible path
- Queue lag / backlog age
- Retry / duplicate attempt rate
- Cache hit ratio where applicable
- Error budget burn rate
- Unit cost trend
- Cell imbalance / hot partition indicators

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope & non-goals |
| 5–12 | Back-of-envelope math |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive invariants & failures |
| 35–45 | Progressive scale, ownership, SEV |

---

## 10. Operability

### Golden signals

commit p99, sync lag, conflict rate, chunk put/get, GC lag, share 403, storage physical/logical, $/GB

### Rollback ladder

pause GC→revert meta binary→disable share type→cell isolate

### Kill switches

pause commits; read-only namespaces; revoke all links prefix; freeze GC; block client version

### Security / privacy

ACL; encrypt; malware scan; link passwords/expiry; audit enterprise

### Cost worksheet

Physical storage after dedup + egress + meta IOPS; cold tiers; adaptive chunking

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Object store, identity, clients, trust, enterprise admin, billing

---

## More Interview Q&A — Dropbox-like File Storage

**Q1. rsync vs chunk hash?**

**A:** Content defined chunking optional later.

**Q2. BTRFS-like?**

**A:** Server not host FS.

**Q3. POSIX?**

**A:** Not full; cloud semantics.

**Q4. Lock files?**

**A:** Optional advisory.

**Q5. WebDAV?**

**A:** Gateway optional.

**Q6. E2E encryption?**

**A:** Tradeoff server features.

**Q7. Device limit?**

**A:** Quota.

**Q8. Partial download?**

**A:** Range gets.

**Q9. Thumbnail?**

**A:** Async preview service.

**Q10. What not?**

**A:** Realtime OT docs in MVP.

**Q11. How do you canary this?**

**A:** Percent or cell-scoped; auto-rollback on SLO burn.

**Q12. What is the SEV1 customer line?**

**A:** State impact, blast radius, mitigation, next update ETA.

**Q13. How do you test failure?**

**A:** Game day: kill AZ, dependency timeout, duplicate inject.

**Q14. What is read-your-write strategy?**

**A:** Sticky session, sync path, or version tokens as needed.

**Q15. How do you bound cardinality?**

**A:** Allowlists, quotas, deliberate metric labels.

**Q16. What is the degrade mode?**

**A:** Shed noncritical; preserve integrity/security path.

**Q17. How do you handle poison?**

**A:** Quarantine/DLQ; alert owner; capped redrive.

**Q18. What is multi-region story?**

**A:** Home cell writes; regional reads/failover documented.

**Q19. How do you prevent noisy neighbors?**

**A:** Quotas + shuffle sharding + fair queues.

**Q20. What would you not build in MVP?**

**A:** CRDT realtime co-editing.

---

## Worked Capacity Narrative — Dropbox-like File Storage

Meta list QPS and chunk put QPS dominate. Shard namespaces; cache dir listings carefully.

## Customer-Trust Paragraph — Dropbox-like File Storage

Silent data loss on conflict is unforgivable. Sync correctness > clever compression.

## Progressive Scale Recap — Dropbox-like File Storage

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Dropbox-like File Storage

### S1. Chunk immutability

Hash-addressed durable bytes.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Namespace CAS

Rev checks prevent lost updates.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Delta sync

Cursor streams per namespace.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Conflict UX

Never silent drop.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Dedup/refcount GC

Safe deletion.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Sharing ACL

Check every download.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Version history

Restore + ransomware defense.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. Client protocol

Versioned; backward compatible.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Dropbox-like File Storage

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Sync storm | Rate limit deltas; notify backoff | Lag | Client fix |
| GC incident | Freeze GC | Space risk | Refcount audit |
| Share leak | Revoke; audit | Exposure | Link defaults |
| Corruption report | Quarantine hash | Trust | Repair from replicas |
| Meta hotspot | Shard dir | Latency | List cache |
| Ransomware pattern | Freeze; restore versions | Recovery | Alerts |


## Rapid-Fire Q&A — Dropbox-like File Storage

**RQ1. Why does 'Chunk immutability' matter in an L6 interview?**

**A:** Hash-addressed durable bytes. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Chunk immutability' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Chunk immutability' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Namespace CAS' matter in an L6 interview?**

**A:** Rev checks prevent lost updates. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Namespace CAS' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Namespace CAS' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Delta sync' matter in an L6 interview?**

**A:** Cursor streams per namespace. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Delta sync' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Delta sync' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Conflict UX' matter in an L6 interview?**

**A:** Never silent drop. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Conflict UX' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Conflict UX' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Dedup/refcount GC' matter in an L6 interview?**

**A:** Safe deletion. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Dedup/refcount GC' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Dedup/refcount GC' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Sharing ACL' matter in an L6 interview?**

**A:** Check every download. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Sharing ACL' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Sharing ACL' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Version history' matter in an L6 interview?**

**A:** Restore + ransomware defense. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Version history' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Version history' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Client protocol' matter in an L6 interview?**

**A:** Versioned; backward compatible. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Client protocol' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Client protocol' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Dropbox-like File Storage

### Walkthrough beat 1

Client chunks file; uploads missing hashes.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Commit CAS rev; delta appended.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Second device pulls delta; downloads chunks.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Dual edit conflict→keep both.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Share link; ACL allows GET.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Revoke share; downloads fail.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Restore prior version.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× shard; 100× cells; 1,000× edge/smart sync.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Dropbox-like File Storage

- [ ] Can explain **Chunk immutability** with numbers and a deal-breaker
- [ ] Can explain **Namespace CAS** with numbers and a deal-breaker
- [ ] Can explain **Delta sync** with numbers and a deal-breaker
- [ ] Can explain **Conflict UX** with numbers and a deal-breaker
- [ ] Can explain **Dedup/refcount GC** with numbers and a deal-breaker
- [ ] Can explain **Sharing ACL** with numbers and a deal-breaker
- [ ] Can explain **Version history** with numbers and a deal-breaker
- [ ] Can explain **Client protocol** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Sync storm**
- [ ] Has a 30-second runbook for **GC incident**
- [ ] Has a 30-second runbook for **Share leak**
- [ ] Has a 30-second runbook for **Corruption report**
- [ ] Has a 30-second runbook for **Meta hotspot**
- [ ] Has a 30-second runbook for **Ransomware pattern**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Dropbox-like File Storage to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Dropbox-like File Storage: 1× → 10× break → 100× cells → 1,000× specialization.

### Extra drill

Name three wallboard metrics before a peak event and the action each triggers.

### Extra drill

Write the SEV1 one-liner: impact, blast radius, mitigation, next update ETA.

### Extra drill

Defend your consistency choice: what is lost if weakened, and who notices first.

### Extra drill

Cost challenge: cut 30% without violating the top SLO—what do you shed first?

### Extra drill

Security challenge: compromised credential—how do least privilege, fencing, and audit limit damage?

### Extra drill

Multi-tenant challenge: one tenant sends 100×—show fair-share math and protected queues.


*End of document — Dropbox-like File Storage (SDE III)*
