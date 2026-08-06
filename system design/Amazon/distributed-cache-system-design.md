# System Design: Distributed Cache (Amazon Platform)

> **Focus areas:** Consistent hashing · Replication/quorum · TTL/versioning · Invalidation · Stampede control · Hot keys · Multi-tier · Cells · Stale-while-revalidate
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Coherence classes; hit-rate economics; hot-key & stampede as first-class; ownership vs origin services
> **Interview theme:** Amazon SDE III / L6 — **distributed cache** platform for retail read paths (PDP, search overlays, session-ish data)

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

Goal: Design a **multi-tenant distributed cache platform** that absorbs Amazon read QPS, protects origins, and offers explicit freshness/consistency classes for catalog, pricing overlays, and session-like data.

### 1.0 What this is / is not
| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Low-latency get/set + invalidation | Source of truth datastore |
| Durability | Best-effort / warmable | Primary ledger |
| Amazon lens | PDP latency, wrong-price trust, Prime Day | Generic Redis tutorial |

### 1.1 Functional requirements
| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | API? | Get/Set/Del/MultiGet/GetMeta | Version/etag in meta |
| F2 | Tenants? | Many services/namespaces | Quotas + ACLs |
| F3 | Freshness? | Per-class TTL + invalidation | Coherence matrix |
| F4 | Replication? | N=3 typical | Quorum/repair |
| F5 | Hot keys? | Detect + replicate | First-class |
| F6 | Invalidation? | Bus + TTL backstop | At-least-once + version |
| F7 | Tiers? | L1/L2/origin | Rules per tier |
| F8 | Negative cache? | Short TTL | Careful errors |
| F9 | Observability? | Hit/miss/origin/staleness | Namespace labels bounded |
| F10 | Admin? | Flush by key/prefix gated | Audit |

**MVP:** cache-aside L2 fleet, consistent hash, replicas, TTL+version, invalidation bus, singleflight, hot-key tooling, multi-tenant namespaces.
**Out:** Replacing Dynamo as SoT; infinite retention; global strongly consistent cache.

### 1.2 NFRs
get p99 < 2–5ms in-region; hit rate targets per namespace; 99.99% availability with stale degrade; bounded staleness SLOs; Prime Day headroom.

### 1.3 Cases
Happy: L2 hit; miss coalesce fill; invalidation drops key; SWR during origin blip.
Edges: stampede; poison null cache; hot ASIN; bus partition; memory eviction of critical keys; cross-tenant flush mistake.

### 1.4 Progressive scale
| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Get QPS | 5M | 50M | 500M | 5B |
| Working set | 20TB | 50TB | 200TB | 1PB+ tiered |
| Hot keys | 1K | 5K | 20K | 100K |
| Invalidations/s | 50K | 500K | 5M | 50M |

Jumps: more shards → cells+edge → client/edge POCO + admission control.

### 1.5 Scope repeat-back
> Multi-tenant Amazon distributed cache with consistent hashing, replication, versioned TTL, invalidation bus, stampede/hot-key controls, multi-tier coherence—scaling gets from millions to billions QPS with explicit freshness classes.

---
## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes
Gets 5M/s; sets/invalidations 50–100K/s; multi-get batches; L1 filters 30–70% depending on service.

### 2.2 Memory
```text
20TB working set / 0.7 util ≈ 30TB raw DRAM across fleet
Object avg 2KB → 10B keys; overheads matter (allocator fragmentation)
```

### 2.3 Latency budget
L1 <0.1ms; L2 0.5–2ms; origin 10–50ms → cache hit mandatory for PDP budgets.

### 2.4 Cost
Origin call $ ≫ cache DRAM $. Hit +1% can save enormous origin fleets. Track `origin_qps` as primary cost signal.

---
## 3. High-Level Design

**Components:** Client SDK (L1+singleflight), Cache Proxy/Router, Storage nodes (slab/Redis-like), Replica sets, Invalidation bus, Hot-key controller, Meta/version service (light), Admin, Autoscaler, Cells.

**Coherence classes:**
| Class | Example | Strategy |
|-------|---------|----------|
| C1 | Product description | TTL minutes + invalidation |
| C2 | Price/deal | Short TTL + prioritized invalidation + SWR bound |
| C3 | Session/entitlement | Fine keys; short TTL; avoid shared L1 mistakes |
| C4 | Public static | CDN/edge long TTL |

**Tradeoffs:** memory vs hit rate; stale vs availability; fanout invalidation vs TTL-only; cell isolation vs efficiency.

---
## 4. Architecture Diagram

```text
 Service (PDP)
   |- L1 in-process (+ singleflight)
   v
 Cache Router (consistent hash + cell)
   |- replica set (N=3)
   |- miss -> Origin / Product Service
   |- populate L2 (+ optional L1)
 Invalidation: Writer -> Bus -> Routers/nodes (version check)
 Hot-Key Controller -> replicate/split popular keys
 Edge/CDN tier for public objects
```

Degrade: serve stale within bound; shed multi-get wideness; disable L1 on bug; cell failover.

---
## 5. Design Deep Dive

### 5.1 Reliability (R)
Invariants: version monotonic per key; invalidation applied iff version ≥ cached; TTL always present; negative cache bounded; no cross-tenant access; critical namespaces eviction-protected or pinned capacity.

### 5.2 Scalability (S)
| Scale | Architecture |
|-------|--------------|
| 1× | Regional L2 cluster + SDK |
| 10× | More shards/replicas; bulk get; compression |
| 100× | Marketplace cells; edge tiers; invalidation sharding |
| 1,000× | Client dictionaries for head; hierarchical caches; approx admission |

### 5.3 Maintainability (M)
Namespace templates; chaos drills; canary on hit/stale metrics; safe flush tooling; clear ownership: platform vs origin.

### 5.4 Hot keys & stampede
Detect via QPS sketches; auto-replicate; singleflight per key; probabilistic early expire; soft locks with TTL.

### 5.5 Consistency honesty
Not a linearizable DB. Offer meta.version; clients who need strong read go to origin or quorum read path.

---
## 6. Wrap-Up

### 6.1 What we designed
Amazon distributed cache platform: multi-tier, hashed shards, replicas, versioned invalidation, stampede/hot-key controls, coherence classes, progressive cells/edge.

### 6.2 Key decisions worth defending
1. Cache ≠ SoT
2. Version+TTL+bus (not TTL-only for prices)
3. Singleflight mandatory
4. Hot keys first-class
5. Cells for blast radius
6. Coherence classes explicit
7. Hit-rate economics
8. L1 safety rules

### 6.3 Risks & follow-ups
Invalidation storms; silent poison; personalization leakage; DRAM cost; cross-region lag.

### 6.4 Closer
> **Distributed Cache**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Distributed Cache

**Q1. Cache-aside vs write-through?**

**A:** Cache-aside dominant for Amazon read-heavy catalog; write-through/write-behind for session-like tightly owned stores. State coherence.

**Q2. How do you invalidate?**

**A:** Versioned keys + pub/sub invalidation; TTL as backstop; read repair on mismatch.

**Q3. Consistent hashing why?**

**A:** Minimize key movement on cluster change; vnodes for balance.

**Q4. Hot ASIN problem?**

**A:** Replicate hot keys; edge cache; split; never single shard assumption.

**Q5. Stampede control?**

**A:** Singleflight, lock TTL, stale-while-revalidate, jittered TTL.

**Q6. What to never cache?**

**A:** Unscoped PII in shared keys; unresolved authz; unbounded large objects without size class.

**Q7. L1 safety?**

**A:** Process-local L1 must respect versions; short TTL; no cross-user keys.

**Q8. Replication lag read?**

**A:** Prefer replica for noncritical; primary for strong class; hedge requests.

**Q9. Eviction policy?**

**A:** LRU/LFU per namespace; pin critical; admission control (TinyLFU).

**Q10. Multi-region?**

**A:** Regional L2; global objects via CDN/origin; avoid cross-region chatty invalidation storms.

**Q11. Cache poisoning?**

**A:** Authenticate writers; signed invalidations; don’t accept client-supplied cache fills.

**Q12. Metrics that matter?**

**A:** Hit rate by namespace, origin qps, p99 get, eviction rate, invalidation lag, stale_served.

**Q13. Deal-breaker?**

**A:** Global unbounded TTL with no invalidation for prices, or one giant shared cache without cells.

**Q14. Negative caching?**

**A:** Yes, short TTL; careful with transient origin errors vs true 404.

**Q15. Large values?**

**A:** Chunk/compress; store blob in object store + cache pointer; size admission.

**Q16. How to migrate cluster?**

**A:** Dual-write or gradual vnode move; shadow reads; never big-bang flush all.

**Q17. Personalization cache?**

**A:** Key includes customer/segment; privacy TTLs; cell isolation.

**Q18. Who pages?**

**A:** Cache platform for fleet; product service for origin errors; jointly for stampede SEVs.

**Q19. Consistency for inventory?**

**A:** Often separate near-real-time overlay, not fat cached blob alone.

**Q20. Probabilistic early expiration?**

**A:** Expire early with probability to spread refresh—classic stampede tool.


---
## 8. Appendices

### A — Glossary
| Term | Meaning |
|------|---------|
| SWR | Stale-while-revalidate |
| Vnode | Virtual node on hash ring |
| Singleflight | Coalesce concurrent misses |
| Negative cache | Cache of misses |
| Coherence class | Freshness/consistency policy bucket |
| Cell | Failure-isolated unit |
| Deal-breaker | TTL-only prices / no hot-key plan |
| Two-pizza | Ownership with pager |

### B — Oncall checklist
- [ ] Hit rate & origin_qps
- [ ] Invalidation lag SLO
- [ ] Hot-key dashboard
- [ ] Eviction pressure
- [ ] Safe flush path known

### C — Key schema
```text
{namespace}:{key} -> {version, ttl, payload, flags}
hot:{key} -> replication factor directive
```

### D — Scale checklist
Shards → cells/edge → client head dictionaries; always quantify origin melt risk.

### E — Estimation cheat-sheet
```text
origin_qps ≈ get_qps × (1 - hit_rate)
dram ≈ working_set / target_util
```

### F — Closer checklist
- [ ] Coherence classes
- [ ] Invalidation+TTL
- [ ] Stampede/hot-key
- [ ] Cells
- [ ] Progressive scale

## Deep Technical Notes — Distributed Cache

### Consistent hashing details
Virtual nodes per physical; weighted by capacity; gentle rebalance; avoid storing ring in every client without gossip version.

### Read repair
On meta mismatch across replicas, fetch origin or authoriative replica; async repair others.

### Invalidation delivery
At-least-once bus; consumers idempotent by version; snapshot lag metric; dead-letter poison messages.

### Admission control
TinyLFU/W-TinyLFU style: don’t admit one-hit wonders thrashing working set during bots crawls.

### Personalization pitfalls
Never use ASIN-only key for per-customer priced payloads; include customer/segment hash; encrypt sensitive.

### PDP bundle
MultiGet description+images+badges; partial fill strategies; hedge slow replica.

## Interview Cards — Distributed Cache

### Card 1: Cache-aside vs write-through?

Cache-aside dominant for Amazon read-heavy catalog; write-through/write-behind for session-like tightly owned stores. State coherence.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: How do you invalidate?

Versioned keys + pub/sub invalidation; TTL as backstop; read repair on mismatch.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Consistent hashing why?

Minimize key movement on cluster change; vnodes for balance.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Hot ASIN problem?

Replicate hot keys; edge cache; split; never single shard assumption.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Stampede control?

Singleflight, lock TTL, stale-while-revalidate, jittered TTL.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: What to never cache?

Unscoped PII in shared keys; unresolved authz; unbounded large objects without size class.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: L1 safety?

Process-local L1 must respect versions; short TTL; no cross-user keys.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Replication lag read?

Prefer replica for noncritical; primary for strong class; hedge requests.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Eviction policy?

LRU/LFU per namespace; pin critical; admission control (TinyLFU).

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Multi-region?

Regional L2; global objects via CDN/origin; avoid cross-region chatty invalidation storms.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Cache poisoning?

Authenticate writers; signed invalidations; don’t accept client-supplied cache fills.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Metrics that matter?

Hit rate by namespace, origin qps, p99 get, eviction rate, invalidation lag, stale_served.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Deal-breaker?

Global unbounded TTL with no invalidation for prices, or one giant shared cache without cells.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Negative caching?

Yes, short TTL; careful with transient origin errors vs true 404.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Large values?

Chunk/compress; store blob in object store + cache pointer; size admission.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: How to migrate cluster?

Dual-write or gradual vnode move; shadow reads; never big-bang flush all.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.


## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + coherence classes |
| 5–12 | Estimation + hit-rate economics |
| 12–22 | HLD + ASCII |
| 22–35 | R/S/M: invalidation, hot keys, stampede |
| 35–45 | Tradeoffs & Q&A |

---
## 10. Operability

### Golden signals
Hit rate, get latency, origin qps, invalidation lag, error rate, memory saturation.

### Rollback ladder
Disable L1 → revert router → SWR-only → shed traffic → cell isolate.

### Kill switches
Namespace disable; stop admissions; flush prefix gated; bypass to origin with throttle.

### Security/privacy
ACL namespaces; audit flushes; PII TTLs; no cross-cell customer key share.

### Cost worksheet
DRAM + network vs origin compute. Lever: hit rate and admission.

### Progressive scale
10× shards; 100× cells/edge; 1,000× client/edge intelligence.

### Cross-team deps
Product service, pricing, identity, streaming CDC, CDN.

---
## More Interview Q&A — Distributed Cache

**Q1. Memcached vs Redis?**

**A:** Memcached simple slab cache; Redis structures/replication/persistence options—pick by features needed.

**Q2. Persistence needed?**

**A:** Usually no for pure cache; warmable from origin. Optional AOF for session stores.

**Q3. Bloom filters?**

**A:** Optional negative existence filters to cut origin 404s.

**Q4. CDC invalidation?**

**A:** Dynamo Streams/Kafka from source of truth → invalidator workers.

**Q5. Cache API design?**

**A:** Get/Set/Del/GetWithMeta; bulk get; tenant namespaces.

**Q6. SLO for staleness?**

**A:** Per class: description ≤5m; price ≤30s; session ≤0.

**Q7. Thundering herd after deploy?**

**A:** Prefetch top-K ASINs; staggered TTL; coalescing.

**Q8. Security multi-tenant?**

**A:** Authz on admin flush; namespace ACLs; no cross-tenant key poke.

**Q9. Compression?**

**A:** Compress large JSON; CPU vs network tradeoff at 100×.

**Q10. Hedged gets?**

**A:** Tail latency reduction with care for origin load amplification.

**Q11. CRC/version mismatch?**

**A:** Treat as miss; refetch; metric poison_rate.

**Q12. Cell sticky routing?**

**A:** Route customers to marketplace cell; caches local.

**Q13. Warmup strategy?**

**A:** Top ASINs by traffic; progressive fill; avoid origin melt.

**Q14. Client-side CDN?**

**A:** Public assets yes; personalized no.

**Q15. Write amplify invalidation?**

**A:** Batch coalesced invalidations; version vectors.

**Q16. Observability sampling?**

**A:** Trace get→origin path exemplars on misses.

**Q17. Cost of 1% hit drop?**

**A:** Often millions origin calls—quantify in interview.

**Q18. Replica read stale?**

**A:** Document; use version compare.

**Q19. Garbage keys?**

**A:** TTL mandatory; orphan scanner for no-TTL bugs.

**Q20. gRPC cache service?**

**A:** Yes for multi-language; keep protocol simple.

**Q21. Partial failure return?**

**A:** Return stale with header vs error—product choice per API.

**Q22. ASIN bundle keys?**

**A:** Composite keys carefully; invalidate graph of dependents.

**Q23. Feature flag in cache?**

**A:** Cache flag-evaluated results short; or evaluate online.

**Q24. Chaos testing?**

**A:** Kill vnode; delay invalidation; origin 500s; verify SWR.


## Deep Technical Addenda — Distributed Cache

### Worked stampede math
10K clients miss same key simultaneously without singleflight → 10K origin calls. With singleflight → 1 origin + 10K waits. At Prime Day, this is SEV math.

### Wrong-price incident anatomy
Writer updates SoT; invalidation delayed 2m; TTL 10m; customers see old price → trust/refund cost. Fix: short TTL + prioritized bus + version checks on checkout revalidate.

### Rebalance story
Add 20% nodes; expect ~20%/N key moves with consistent hashing+vnodes—not full flush. Shadow verify.

## Tradeoff Matrices — Distributed Cache

| Choice | Pros | Cons | Amazon pick |
|--------|------|------|-------------|
| TTL-only | Simple | Stale prices | TTL+invalidation |
| Write-through | Fresher | Writer latency | Cache-aside + bus |
| Global cache | Efficient | Blast radius | Cells |
| Huge L1 | Faster | Coherence bugs | Small L1 + rules |

## Operability Addenda — Distributed Cache

Pages on origin_qps spike, invalidation lag, memory, error bursts, hot-key CPU.

## Worked Capacity Narrative — Distributed Cache

5M gets × 30% miss = 1.5M origin/s impossible—so hit rate is the architecture. Interviewers listen for that inversion.

## Customer-Trust Paragraph — Distributed Cache

Wrong price, empty PDP from poisoned nulls, or cross-user data leak are trust SEVs—not “cache curiosities.”

## Progressive Scale Recap — Distributed Cache

- **10×:** shards/replicas/bulk/compress
- **100×:** cells, edge, invalidation scale
- **1,000×:** client/edge head, admission, hierarchical

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Distributed Cache

### S1. Consistent hashing & vnodes

Partition keys with consistent hashing + virtual nodes to limit remaps on node add/remove; avoid hotspotting popular ASINs onto one vnode without replication.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S2. Replication & quorum

N=3 replicas; R/W quorums tuned per consistency class—product detail can be R=1; pricing/inventory overlays may need stricter read repair.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S3. TTL + versioning

Every value carries version/etag + TTL; stale-while-revalidate for storefront; hard TTL for security tokens.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S4. Invalidation bus

Pub/sub or streaming invalidations on writes; at-least-once with version checks; never rely on TTL alone for price correctness.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S5. Thundering herd

Singleflight/request coalescing; probabilistic early expire; negative caching with short TTL.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S6. Hot-key replication

Detect hot keys; replicate to many caches / edge POCOs; split key namespaces for flash deals.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S7. Multi-tier cache

L1 in-process → L2 regional Redis/Memcached fleet → origin (Dynamo/S3/service). Explicit coherence rules per tier.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

### S8. Cell isolation

Marketplace/region cells; no cross-cell silent sharing of customer-specific data; blast-radius limits.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?


## Scenario Runbooks — Distributed Cache

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Cache stampede on ASIN | Singleflight + serve stale | PDP stays up | Tune early-expire |
| Bad deploy caches nulls | Disable negative cache; flush version | Avoid empty PDP | Canary value checks |
| Invalidation lag | Force version bump; short TTL fallback | Price correctness | Bus lag SLO |
| Node loss 1/3 | Replica promote; rebalance gradual | Availability | Capacity headroom |
| Memory pressure eviction | Protect critical namespaces | Hit rate SLO | Tier admission |
| Region failover | Warm sibling cell; accept stale ε | Checkout continuity | DR drill |


## Rapid-Fire Q&A — Distributed Cache

**RQ1. Why does 'Consistent hashing & vnodes' matter in an L6 interview?**

**A:** Partition keys with consistent hashing + virtual nodes to limit remaps on node add/remove; avoid hotspotting popular ASINs onto one vnode without replication. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Consistent hashing & vnodes' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Consistent hashing & vnodes' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Replication & quorum' matter in an L6 interview?**

**A:** N=3 replicas; R/W quorums tuned per consistency class—product detail can be R=1; pricing/inventory overlays may need stricter read repair. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Replication & quorum' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Replication & quorum' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'TTL + versioning' matter in an L6 interview?**

**A:** Every value carries version/etag + TTL; stale-while-revalidate for storefront; hard TTL for security tokens. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'TTL + versioning' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'TTL + versioning' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Invalidation bus' matter in an L6 interview?**

**A:** Pub/sub or streaming invalidations on writes; at-least-once with version checks; never rely on TTL alone for price correctness. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Invalidation bus' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Invalidation bus' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Thundering herd' matter in an L6 interview?**

**A:** Singleflight/request coalescing; probabilistic early expire; negative caching with short TTL. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Thundering herd' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Thundering herd' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Hot-key replication' matter in an L6 interview?**

**A:** Detect hot keys; replicate to many caches / edge POCOs; split key namespaces for flash deals. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Hot-key replication' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Hot-key replication' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Multi-tier cache' matter in an L6 interview?**

**A:** L1 in-process → L2 regional Redis/Memcached fleet → origin (Dynamo/S3/service). Explicit coherence rules per tier. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Multi-tier cache' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Multi-tier cache' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Cell isolation' matter in an L6 interview?**

**A:** Marketplace/region cells; no cross-cell silent sharing of customer-specific data; blast-radius limits. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Cell isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Cell isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Distributed Cache

### Walkthrough beat 1

PDP request: L1 miss → L2 get ASIN payload version V; hit returns; miss coalesced fetch from Product Service; populate tiers with TTL + etag. Metric: l2_hit_rate, origin_qps.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Price update: writer bumps version; publishes invalidation; caches drop or SWR fetch. Degradation: if bus down, TTL bounds staleness—state max stale seconds for price.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Flash deal hot key: replicate key to N edge nodes; optional key split; never one Redis shard. Watch hot_key_cpu.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Negative caching: 404 for bad ASIN cached 10–30s; never cache auth failures long; never cache personalized cart in shared L2 without user key.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

10× more shards/replicas; 100× cells + edge; 1,000× client/edge POCOs + approx admission. Adding RAM alone fails on invalidation and hot keys.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Consistency classes: catalog description eventual OK; entitlement/session stronger; document per API.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

SEV: serving wrong price/availability is trust incident—prefer slightly slower correct path over silent stale forever.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

Unit economics: origin_qps avoided × origin_$ vs cache fleet_$; hit rate +2% often beats +20% nodes.

Call out one tradeoff you are making (latency vs freshness, consistency vs availability, memory vs hit rate) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Distributed Cache

- [ ] Can explain **Consistent hashing & vnodes** with numbers and a deal-breaker
- [ ] Can explain **Replication & quorum** with numbers and a deal-breaker
- [ ] Can explain **TTL + versioning** with numbers and a deal-breaker
- [ ] Can explain **Invalidation bus** with numbers and a deal-breaker
- [ ] Can explain **Thundering herd** with numbers and a deal-breaker
- [ ] Can explain **Hot-key replication** with numbers and a deal-breaker
- [ ] Can explain **Multi-tier cache** with numbers and a deal-breaker
- [ ] Can explain **Cell isolation** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Cache stampede on ASIN**
- [ ] Has a 30-second runbook for **Bad deploy caches nulls**
- [ ] Has a 30-second runbook for **Invalidation lag**
- [ ] Has a 30-second runbook for **Node loss 1/3**
- [ ] Has a 30-second runbook for **Memory pressure eviction**
- [ ] Has a 30-second runbook for **Region failover**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse explaining Distributed Cache to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


*End of document — Distributed Cache (Amazon Platform) (SDE III)*


## Whiteboard Numeric Drills — Distributed Cache

### Drill A — 10× jump
State the baseline bottleneck metric, the mechanism that breaks first when traffic rises 10×, and the concrete architectural jump (not “add servers”). Name the dashboard panel that confirms the jump worked.

### Drill B — 100× jump
Explain which consistency/freshness/accuracy ε you accept at 100× and how the customer is informed or protected. Tie to a kill switch.

### Drill C — 1,000× jump
Describe cell isolation, approximate algorithms, or edge offload. Call the unit-cost metric (`$/M requests` or equivalent) and what linear scaling would have cost.

### Drill D — Ownership one-liner
Who pages for latency vs correctness vs policy? What artifact (config pointer, model version, ring map) do you revert?

### Drill E — Deal-breaker refusal
In one sentence, refuse the classic bad design for this topic and replace it with the Amazon-bar alternative.

