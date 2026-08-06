# System Design: Picture Upload Service

> **Focus areas:** Presigned upload · Virus/abuse scan · Image processing · CDN · Metadata · Dedup · Quotas · Privacy delete
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **Picture upload service** — durable media ingest with safety and cost control

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

Goal: design a **picture upload service**: client→object store uploads, metadata, async processing (thumbnails/transcode), abuse scanning, CDN delivery, quotas, and privacy-correct deletes.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Upload+process+serve images | Full social network |
| Store | Object store + metadata DB | DB BLOBs |
| Amazon lens | Abuse, cost, privacy delete | Toy /tmp uploads |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Upload? | Presigned multipart | No big bodies via API |
| F2 | Formats? | JPEG/PNG/WebP/HEIC | Normalize pipeline |
| F3 | Processing? | Thumbs, EXIF strip, variants | Async workers |
| F4 | Scan? | Malware/CSAM/policy | Fail closed public |
| F5 | Serve? | CDN signed/public | Authz-aware |
| F6 | Metadata? | Owner, album, sizes | Queryable |
| F7 | Dedup? | Hash optional | Cost save |
| F8 | Quotas? | Count/bytes/rate | Fair use |
| F9 | Delete? | Hard delete+purge CDN | Privacy SLO |
| F10 | EXIF? | Strip GPS by default | Privacy |
| F11 | Versions? | Replace/versioned | Immutable objects |
| F12 | Admin? | Takedown | Trust tools |

**MVP scope:**

1. Presigned upload init/complete
2. Metadata records
3. Async thumbs
4. AV/policy scan before public
5. CDN URLs
6. Quotas
7. Delete+purge
8. Metrics

**Out of MVP:** Realtime collaborative photo editing; Full ML fashion search; Unbounded original retention forever free.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Upload init | p99<200ms |
| N2 | Complete visible | seconds after process |
| N3 | Durability | 11-nines class object store |
| N4 | Privacy delete | CDN purge SLO hours |
| N5 | Scan lag | p99 minutes |
| N6 | Avail | 99.9%+ upload path |
| N7 | Cost | $/GB + transform |
| N8 | Abuse | Block before viral serve |

### 1.3 Cases

**Happy:** init→PUT parts→complete→scan→process→CDN ready; delete purges.
**Edges:** incomplete MPU; malware; huge image zip bomb; hot album; signed URL leak; EXIF GPS; fanout thumbs fail.

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
| Uploads/day | 10M | 100M | 1B | 10B |
| Peak upload QPS | 2K | 20K | 200K | 2M |
| Stored images | 1B | 10B | 100B | 1T |
| Avg size | 2MB | 2MB | 3MB | 3MB |
| Storage | 2PB | 20PB | 300PB | 3EB |
| Variants/image | 4 | 4 | 6 | 8 |

**Jumps:** 10× async fleet+CDN; 100× cells+lifecycle tiers; 1,000× edge process+smart dedup.

### 1.5 Scope repeat-back

> Presigned picture ingest with scan, variants, CDN, quotas, privacy deletes—cost-aware at PB scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Bytes

```text
10M×2MB=20TB/day ingress
```

### 2.2 Variants

```text
4× storage amplification unless smart
```

### 2.3 Workers

```text
process CPU bound; autoscale on queue
```

### 2.4 CDN

```text
egress dominates $; cache hit critical
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
| Ingest | Presign+complete | Strong meta |
| Object | Bytes durable | Immutable |
| Scan/process | Async pipelines | At-least-once |
| Serve | CDN | Cached |
| Trust | Takedown | Strong |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Upload API** — Init/complete
2. **Object store** — Bytes
3. **Metadata DB** — Pointers/state
4. **Scan workers** — AV/policy
5. **Image workers** — Variants
6. **CDN** — Serve
7. **Quota** — Bytes/count
8. **Signer** — URL auth
9. **GC/lifecycle** — Abort MPU+cold
10. **Takedown** — Trust
11. **Event bus** — State changes
12. **Obs** — Lag metrics

### 3.3 API sketch

```text
POST /v1/uploads/init {size,hash,content_type}
PUT presigned parts
POST /v1/uploads/complete
GET /v1/pictures/{id}
DELETE /v1/pictures/{id}
```

### 3.4 State machine

```text
INIT→UPLOADING→UPLOADED→SCANNING→PROCESSING→READY
→REJECTED|DELETED
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Proxy upload | Presigned direct | Save API bandwidth |
| Sync process | Async | Fast ACK |
| Public CDN | Signed for private | Authz |
| EXIF keep | Strip GPS default | Privacy |
| Dedup | Optional content hash | Sharing risk |

---

## 4. Architecture Diagram

```text
Client->UploadAPI->Presign->S3
Complete->Meta->ScanQ->ProcessQ->Variants->CDN
Delete->Meta+S3+CDN purge
```

### 4.1 Upload

```text
Init meta; client PUT; complete verifies size/hash; enqueue scan
```

### 4.2 Serve

```text
Authz; signed URL; CDN
```

### 4.3 Delete

```text
Mark deleted; delete objects; purge; audit
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

1. No public READY before scan policy allows
2. Complete verifies integrity
3. Delete removes all derivatives
4. Quotas enforced pre-presign
5. EXIF GPS stripped default
6. Signed URL expiry enforced
7. MPU aborted by GC
8. Audit takedowns

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | S3+Lambda/workers |
| 10× | Queue fleets+CDN |
| 100× | Cells+tiering |
| 1000× | Edge transform+regional ingest |

### 5.3 Maintainability

- Codec allowlist
- Pipeline versioning
- Canary processors
- Golden image tests

### 5.4 Progressive scale narrative

**1×:** Single region
**10×:** CDN global
**100×:** Multi-region ingest cells
**1000×:** Edge + ML moderation scale

### 5.5 Presign security

Short TTL; content-type bind; size bind; owner scoped.

### 5.6 Zip bombs

Pixel/dimension caps; codec timeouts.

### 5.7 Privacy delete

Origin+CDN+derivatives; verify.

### 5.8 Cost

Lifecycle cold; lazy variants; dedup careful.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| Serve before scan | Abuse viral |
| DB BLOBs | Cost/scale fail |
| Delete meta only | Privacy SEV |
| Unbounded dims | CPU DoS |
| Long-lived presign | Theft |
| Sync thumbs in request | Tail latency |

---

## 6. Wrap-Up

### 6.1 Designed

Picture upload: presigned ingest, scan-gated publish, async variants, CDN, quotas, privacy-correct delete.

### 6.2 Decisions to defend

1. Presigned multipart
2. Async scan/process
3. Fail-closed public
4. CDN signed/private
5. EXIF strip
6. Lifecycle tiers
7. Quota pre-check
8. Derivative tracking

### 6.3 Risks

- Scan lag backlog
- CDN purge delay
- Codec CVEs
- Storage $
- Signed URL sharing

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope media |
| 5–15 | Presign+math |
| 15–25 | Scan/process |
| 25–35 | CDN/delete/quota |
| 35–45 | PB scale+cost |

### 6.5 Closer

> **Picture Upload Service**: direct-to-store upload, scan before public, async variants, CDN, privacy deletes, ruthless cost control.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Why presigned?

Bypass API for bytes.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Scan gating?

No READY public until policy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Thumb timing?

Async queue.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: HEIC?

Normalize to WebP/JPEG.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Dedup risk?

Cross-user sharing leaks.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Signed URL leak?

Short TTL+revoke.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: CDN purge?

Hard purge+short TTL.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Quotas?

Bytes+rate+count.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: EXIF GPS?

Strip default.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Incomplete MPU?

Lifecycle abort.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: CSAM pipeline?

Special trust path.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Who pages scan lag?

Media platform + trust.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Multi-region?

Ingest affinity; CDN global.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Video?

Out of MVP or separate.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

Serve unscanned or delete w/o purge.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

$/GB stored+transformed+egress.

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

init/complete p99, scan lag, process lag, READY rate, reject rate, storage $, CDN hit, purge lag

### Rollback ladder

pause READY publish→revert processor→disable format→region isolate

### Kill switches

stop presign; force private; block downloads pending scan; emergency takedown API

### Security / privacy

Short presign; KMS; authz; CSAM/malware pipelines; log redaction

### Cost worksheet

Storage+egress+transform CPU; lifecycle; lazy variants; CDN hit

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Object store, CDN, trust&safety, identity, billing quotas, client apps

---

## More Interview Q&A — Picture Upload Service

**Q1. S3 vs local disk?**

**A:** Object store.

**Q2. Magick vs libvips?**

**A:** Prefer safer/faster lib; sandbox.

**Q3. Animated GIF?**

**A:** Cap frames.

**Q4. Progressive JPEG?**

**A:** Optional optimize.

**Q5. Album listing?**

**A:** Meta DB indexes.

**Q6. Client compress?**

**A:** Yes; still verify server-side.

**Q7. Encryption CEK?**

**A:** SSE-KMS; optional CSE.

**Q8. Cross-account share?**

**A:** Signed URL or ACL copy.

**Q9. Thumb race?**

**A:** Idempotent variant keys.

**Q10. What not?**

**A:** Store originals in SQL.

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

**A:** Realtime collaborative photo editing.

---

## Worked Capacity Narrative — Picture Upload Service

Ingress GB/s and process queue lag dominate. Autoscale workers on lag; cap dimensions early.

## Customer-Trust Paragraph — Picture Upload Service

Unscanned malware/CSAM and undeleted private photos are brand-ending. Privacy delete is an SLO.

## Progressive Scale Recap — Picture Upload Service

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Picture Upload Service

### S1. Presigned ingest

Direct-to-object; bound TTL/size/type.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Scan before public

Fail-closed publish gate.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Async variants

Thumbs off request path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Privacy delete

Origin+CDN+derivatives.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Quota enforcement

Pre-presign checks.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. EXIF/privacy

Strip sensitive tags.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Lifecycle cost

Cold tiers; abort MPU.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. CDN authz

Signed URLs for private.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Picture Upload Service

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| Scan backlog | Scale scanners; delay public | Latency to ready | Codec optimize |
| Malware viral | Takedown+hash block | Safety | Tune scanners |
| Storage spike | Lifecycle; quotas | Cost | Retention policy |
| CDN purge miss | Hard purge | Privacy | TTL policy |
| Presign abuse | Revoke prefix; shorten TTL | Theft stopped | WAF |
| Worker poison image | Quarantine; patch codec | Partial | Fuzz tests |


## Rapid-Fire Q&A — Picture Upload Service

**RQ1. Why does 'Presigned ingest' matter in an L6 interview?**

**A:** Direct-to-object; bound TTL/size/type. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Presigned ingest' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Presigned ingest' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Scan before public' matter in an L6 interview?**

**A:** Fail-closed publish gate. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Scan before public' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Scan before public' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Async variants' matter in an L6 interview?**

**A:** Thumbs off request path. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Async variants' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Async variants' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Privacy delete' matter in an L6 interview?**

**A:** Origin+CDN+derivatives. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Privacy delete' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Privacy delete' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Quota enforcement' matter in an L6 interview?**

**A:** Pre-presign checks. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Quota enforcement' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Quota enforcement' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'EXIF/privacy' matter in an L6 interview?**

**A:** Strip sensitive tags. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'EXIF/privacy' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'EXIF/privacy' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Lifecycle cost' matter in an L6 interview?**

**A:** Cold tiers; abort MPU. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Lifecycle cost' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Lifecycle cost' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'CDN authz' matter in an L6 interview?**

**A:** Signed URLs for private. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'CDN authz' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'CDN authz' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Picture Upload Service

### Walkthrough beat 1

Init upload; quota ok; presign returned.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Client multipart PUT; complete verifies hash.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Scan clean; process thumbs; READY.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Private view via signed CDN URL.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Malware→REJECTED; never public.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Delete removes all variants+purge.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

Hot album served from CDN.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× fleets; 100× cells/tiers; 1,000× edge process.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Picture Upload Service

- [ ] Can explain **Presigned ingest** with numbers and a deal-breaker
- [ ] Can explain **Scan before public** with numbers and a deal-breaker
- [ ] Can explain **Async variants** with numbers and a deal-breaker
- [ ] Can explain **Privacy delete** with numbers and a deal-breaker
- [ ] Can explain **Quota enforcement** with numbers and a deal-breaker
- [ ] Can explain **EXIF/privacy** with numbers and a deal-breaker
- [ ] Can explain **Lifecycle cost** with numbers and a deal-breaker
- [ ] Can explain **CDN authz** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Scan backlog**
- [ ] Has a 30-second runbook for **Malware viral**
- [ ] Has a 30-second runbook for **Storage spike**
- [ ] Has a 30-second runbook for **CDN purge miss**
- [ ] Has a 30-second runbook for **Presign abuse**
- [ ] Has a 30-second runbook for **Worker poison image**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Picture Upload Service to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Picture Upload Service: 1× → 10× break → 100× cells → 1,000× specialization.

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


*End of document — Picture Upload Service (SDE III)*

