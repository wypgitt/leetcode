# System Design: Distributed Cache (Microsoft / Azure Platform)

> **Focus areas:** Consistent hashing · Replication/quorum · TTL/versioning · Invalidation · Stampede control · Hot keys · Multi-tier · Cells · Stale-while-revalidate · Azure regions  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Coherence classes; hit-rate economics; hot-key & stampede as first-class; ownership vs origin services; compliance isolation  
> **Interview theme:** Microsoft L61–L64 — **distributed cache** platform for Azure services, Microsoft 365 read paths, and Copilot/context overlays (Azure Cache–adjacent mental model without claiming internals)

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

Goal: Design a **multi-tenant distributed cache platform** that absorbs Microsoft/Azure read QPS, protects origins (Cosmos/SQL/KV/search), and offers explicit freshness/consistency classes for directory objects, document metadata, feature flags, and session-like data.

### 1.0 What this is / is not

| Dimension | **Distributed Cache (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Job | Low-latency get/set + invalidation | Source of truth datastore |
| Durability | Best-effort / warmable | Primary ledger |
| Success | Hit rate + origin protection + p99 | Infinite retention |
| Microsoft lens | M365 latency, Azure control-plane reads, wrong-config trust | Generic Redis tutorial |

### 1.1 Functional requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | API? | Get/Set/Del/MultiGet/GetMeta | Version/etag in meta |
| F2 | Tenants? | Many services/namespaces | Quotas + ACLs |
| F3 | Freshness? | Per-class TTL + invalidation | Coherence matrix |
| F4 | Replication? | N=3 typical in region | Quorum/repair optional |
| F5 | Hot keys? | Detect + replicate | First-class |
| F6 | Invalidation? | Bus + TTL backstop | At-least-once + version |
| F7 | Tiers? | L1/L2/origin | Rules per tier |
| F8 | Negative cache? | Short TTL | Careful errors |
| F9 | Observability? | Hit/miss/origin/staleness | Namespace labels bounded |
| F10 | Admin? | Flush by key/prefix gated | Audit |
| F11 | Auth? | Managed identity / keys | No anonymous fill from clients |
| F12 | Geo? | Regional L2; careful global | Avoid invalidation storms |

**MVP:** cache-aside L2 fleet, consistent hash, replicas, TTL+version, invalidation bus, singleflight, hot-key tooling, multi-tenant namespaces, Azure region deployment.

**Out:** Replacing Cosmos/SQL as SoT; infinite retention; global strongly consistent cache; client-supplied untrusted fills.

### 1.2 NFRs

| # | Target |
|---|--------|
| N1 | get p99 < 2–5 ms in-region |
| N2 | Hit-rate targets per namespace (explicit) |
| N3 | 99.99% availability with stale degrade |
| N4 | Bounded staleness SLOs per coherence class |
| N5 | Origin QPS ceilings under stampede |
| N6 | Tenant isolation / no cross-tenant reads |
| N7 | Encryption in transit; optional at rest |
| N8 | Clear `$ / M gets` vs origin cost |

### 1.3 Cases

**Happy:** L2 hit; miss coalesce fill; invalidation drops key; SWR during origin blip; MultiGet partial fill.

**Edges:** stampede; poison null cache; hot tenant object; bus partition; memory eviction of critical keys; cross-tenant flush mistake; personalization leakage; region failover cold cache.

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Get QPS | 2M | 20M | 200M | 2B |
| Working set | 10 TB | 30 TB | 150 TB | 1 PB+ tiered |
| Hot keys | 1K | 5K | 20K | 100K |
| Invalidations/s | 20K | 200K | 2M | 20M |
| Regions | 2 | 4 | 8 | Many + sovereign |

**Jumps:** more shards → cells+edge → client/edge dictionaries + admission control.

### 1.5 Scope repeat-back

> Multi-tenant Microsoft/Azure distributed cache with consistent hashing, replication, versioned TTL, invalidation bus, stampede/hot-key controls, multi-tier coherence—scaling gets from millions to billions QPS with explicit freshness classes and origin protection.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

Gets 2M/s; sets/invalidations 20–50K/s; multi-get batches; L1 filters 30–70% depending on service.

### 2.2 Memory

```text
10 TB working set / 0.7 util ≈ 14.3 TB raw DRAM across fleet
Object avg 2 KB → ~5B keys upper; allocator fragmentation matters
Replica factor 2–3 for hot tiers → multiply carefully (often RF on subset)
```

### 2.3 Latency budget

```text
L1 in-process     <0.1 ms
L2 regional       0.5–2 ms
Origin            10–50+ ms
→ cache hit mandatory for interactive M365/Azure UX budgets
```

### 2.4 Hit-rate economics

```text
origin_qps ≈ get_qps × (1 - hit_rate)
At 2M gets/s: hit 90% → 200K origin/s; hit 89% → 220K (+20K/s)
1% hit drop can force huge origin scale-out — primary cost signal
```

### 2.5 Invalidation bandwidth

```text
20K inv/s × 200 B ≈ 4 MB/s — easy
2M inv/s × 200 B ≈ 400 MB/s — need sharded bus + coalescing
Cross-region inv fanout at 1,000× is a design hazard
```

### 2.6 Stampede math

```text
Popular key TTL expire aligned → 10K clients × simultaneous miss
Without singleflight: 10K origin gets
With singleflight: 1 origin get (+ waiters)
Probabilistic early expire spreads refresh load
```

### 2.7 Cost

Origin call $ ≫ cache DRAM $. Track `origin_qps` as primary cost/reliability signal. Admission control beats blindly growing DRAM for one-hit wonders.

---

## 3. High-Level Design

### 3.1 Components

Client SDK (L1+singleflight), Cache Proxy/Router, Storage nodes (slab/Redis-like), Replica sets, Invalidation bus (Event Hubs/Service Bus/Redis pubsub), Hot-key controller, Meta/version light service, Admin, Autoscaler, Cells, Optional CDN/edge for public objects.

### 3.2 Coherence classes

| Class | Example | Strategy |
|-------|---------|----------|
| C1 | Document metadata | TTL minutes + invalidation |
| C2 | ACLs / entitlements | Short TTL + prioritized invalidation; strong read fallback |
| C3 | Feature flags | TTL + push inv; SWR bounded |
| C4 | Session-like | Fine keys; short TTL; careful L1 |
| C5 | Public static | CDN/edge long TTL |

### 3.3 Write / read strategies — Why X over Y

| Strategy | Pros | Cons | When |
|----------|------|------|------|
| **Cache-aside** | Simple; origin SoT | Stampede risk | **Default read-heavy** |
| Write-through | Fresher cache | Write latency | Session stores owned by cache |
| Write-behind | Fast writes | Loss window | Rare for Microsoft SoT data |
| Refresh-ahead | Smooths TTL | Predictive complexity | Top-K keys |

**Chosen:** Cache-aside + versioned invalidation + SWR + singleflight.

### 3.4 Partitioning — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| **Consistent hashing + vnodes** | Minimal move on scale | Hot keys still concentrate |
| Modulo | Simple | Reshard pain |
| Directory map | Explicit | Extra dependency |

**Chosen:** Consistent hashing with virtual nodes; hot-key override map for celebrities; cells for tenants/workloads.

### 3.5 Replication

| Mode | Pros | Cons |
|------|------|------|
| RF=1 | Cheap | Miss on node loss |
| **RF=2–3** | Availability | Memory tax |
| Cross-region sync | Global hit | Inv storms / lag |

**Chosen:** In-region RF=2–3; regional caches; global only for truly global public objects via CDN.

### 3.6 Tradeoffs summary

| Decision | Choice | Deal-breaker |
|----------|--------|--------------|
| Cache ≠ SoT | Always | Treating cache as ledger |
| Version+TTL+bus | Not TTL-only for ACL | TTL-only security data |
| Singleflight | Mandatory | Ignore stampede |
| Hot keys | First-class | “Hashing fixes it” |
| Cells | Blast radius | One giant shared cache |
| L1 rules | Versioned short TTL | Cross-user L1 keys |

---

## 4. Architecture Diagram

```text
 Service (M365 / Azure control plane / Copilot)
   |- L1 in-process (+ singleflight)
   v
 Cache Router (consistent hash + cell + tenant ACL)
   |- replica set (N=2..3) in Azure AZs
   |- miss -> Origin (Cosmos/SQL/KV/Search)
   |- populate L2 (+ optional L1)
 Invalidation: Writer/CDC -> Bus -> Routers/nodes (version check)
 Hot-Key Controller -> replicate/split popular keys
 Edge/CDN tier for public objects
 Front Door / APIM optional in front of cache API for multi-tenant SaaS
```

**Degrade:** serve stale within bound; shed MultiGet width; disable L1 on bug; cell failover; origin throttle + SWR.

---

## 5. Design Deep Dive

### 5.1 Reliability (R)

**Invariants:** version monotonic per key; invalidation applied iff version ≥ cached; TTL always present; negative cache bounded; no cross-tenant access; critical namespaces eviction-protected or pinned capacity; writers authenticated.

**Failure modes:**

| Failure | Behavior |
|---------|----------|
| Node loss | Hash remap; replicas serve; warm miss |
| Bus partition | TTL backstop; lag metric; catch-up |
| Origin down | SWR stale; negative cache careful |
| Poison value | Version bump; quarantine; don’t accept client fills |
| Flush mistake | Audit; soft-delete backups optional; break-glass |

### 5.2 Scalability (S)

| Scale | Architecture |
|-------|--------------|
| 1× | Regional L2 cluster + SDK |
| 10× | More shards/replicas; bulk get; compression |
| 100× | Cells; edge tiers; invalidation sharding |
| 1,000× | Client dictionaries for head; hierarchical caches; approx admission |

### 5.3 Maintainability (M)

Namespace templates; chaos drills; canary on hit/stale metrics; safe flush tooling; clear ownership: platform vs origin; FinOps hit-rate reviews.

### 5.4 Hot keys & stampede

Detect via QPS sketches; auto-replicate; singleflight per key; probabilistic early expire; soft locks with TTL; request coalescing at proxy.

### 5.5 Consistency honesty

Not a linearizable DB. Offer `meta.version`; clients who need strong read go to origin or quorum read path. ACL class: prefer short TTL + inv + origin on miss (no long SWR).

### 5.6 Invalidation deep dive

```text
Producer (app write or CDC) -> invalidate{key, version}
Bus at-least-once
Consumer: if version >= local: drop/tombstone; else ignore stale inv
TTL is backstop if inv lost
Coalesce storms: per-key latest version wins
```

### 5.7 Multi-tier rules

| Tier | Scope | TTL | Danger |
|------|-------|-----|--------|
| L1 | Process | Seconds | Personalization leak; stale ACL |
| L2 | Region cluster | Class-based | Hot keys; memory |
| Edge/CDN | Pop | Long | Only public |

### 5.8 Microsoft / Azure specifics

- Namespaces map to Azure subscriptions/services.  
- Private Link / VNet for enterprise cache endpoints.  
- CMK optional for sensitive payloads.  
- Sovereign clouds: no cross-cloud invalidation.  
- Pair with App Configuration / feature flag services via C3 class.  
- Cold-start after regional failover: prefetch top-K; staggered TTL.

---

## 6. Wrap-Up

### 6.1 What we designed

Microsoft/Azure distributed cache: multi-tier, hashed shards, replicas, versioned invalidation, stampede/hot-key controls, coherence classes, progressive cells/edge, origin economics.

### 6.2 Key decisions worth defending

1. Cache ≠ SoT  
2. Version+TTL+bus (not TTL-only for ACL)  
3. Singleflight mandatory  
4. Hot keys first-class  
5. Cells for blast radius  
6. Coherence classes explicit  
7. Hit-rate economics  
8. L1 safety rules  

### 6.3 Risks & follow-ups

Invalidation storms; silent poison; personalization leakage; DRAM cost; cross-region lag; negative-cache outages.

### 6.4 Closer

> **Distributed Cache**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics, Azure tenancy.

---

## 7. Deeper / Related Interview Questions

**Q1. Cache-aside vs write-through?**

**A:** Cache-aside dominant for read-heavy Microsoft services; write-through for tightly owned session stores. State coherence class.

**Q2. How do you invalidate?**

**A:** Versioned keys + pub/sub/CDC invalidation; TTL backstop; read repair on mismatch.

**Q3. Consistent hashing why?**

**A:** Minimize key movement on cluster change; vnodes for balance.

**Q4. Hot key problem?**

**A:** Replicate; edge; stripe; never single-shard assumption.

**Q5. Stampede control?**

**A:** Singleflight, lock TTL, SWR, jittered TTL, probabilistic early expire.

**Q6. What to never cache?**

**A:** Unscoped PII in shared keys; unresolved authz; unbounded large objects without size class.

**Q7. L1 safety?**

**A:** Respect versions; short TTL; no cross-user keys; flush on identity switch.

**Q8. Replication lag read?**

**A:** Prefer replica for noncritical; primary for strong class; hedge carefully.

**Q9. Eviction policy?**

**A:** LRU/LFU per namespace; pin critical; TinyLFU admission.

**Q10. Multi-region?**

**A:** Regional L2; CDN for public; avoid chatty cross-region inv storms.

**Q11. Cache poisoning?**

**A:** Authenticate writers; signed invalidations; don’t accept client-supplied fills.

**Q12. Metrics that matter?**

**A:** Hit rate by namespace, origin qps, p99 get, eviction rate, invalidation lag, stale_served.

**Q13. Deal-breaker?**

**A:** Global unbounded TTL with no invalidation for ACL/prices-like data; or one giant shared cache without cells.

**Q14. Negative caching?**

**A:** Yes, short TTL; distinguish transient origin errors vs true 404.

**Q15. Large values?**

**A:** Chunk/compress; Blob + cache pointer; size admission.

**Q16. Cluster migration?**

**A:** Dual-write or gradual vnode move; shadow reads; never big-bang flush all.

**Q17. Personalization cache?**

**A:** Key includes user/segment; privacy TTLs; cell isolation.

**Q18. Who pages?**

**A:** Cache platform for fleet; origin service for origin errors; jointly for stampede SEVs.

**Q19. Consistency for entitlements?**

**A:** Short TTL + prioritized inv; strong origin path for security decisions; minimal SWR.

**Q20. Probabilistic early expiration?**

**A:** Expire early with probability to spread refresh—classic stampede tool.

**Q21. Memcached vs Redis?**

**A:** Memcached simple slab; Redis structures/replication—pick by features.

**Q22. Persistence needed?**

**A:** Usually no for pure cache; warmable from origin.

**Q23. Bloom filters?**

**A:** Optional negative existence filters to cut origin 404s.

**Q24. CDC invalidation?**

**A:** Change feed from SoT → invalidator workers.

**Q25. Thundering herd after deploy?**

**A:** Prefetch top-K; staggered TTL; coalescing.

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
| TinyLFU | Admission control against one-hit wonders |
| Deal-breaker | TTL-only ACL / no hot-key plan |

### B — Oncall checklist

- [ ] Hit rate & origin_qps  
- [ ] Invalidation lag SLO  
- [ ] Hot-key dashboard  
- [ ] Eviction pressure  
- [ ] Safe flush path known  
- [ ] L1 kill switch  

### C — Key schema

```text
{tenant}:{namespace}:{key} -> {version, ttl, payload, flags}
hot:{key} -> replication factor directive
neg:{key} -> short TTL miss marker
```

### D — Scale checklist

Shards → cells/edge → client head dictionaries; quantify origin melt risk.

### E — Estimation cheat-sheet

```text
origin_qps ≈ get_qps × (1 - hit_rate)
dram ≈ working_set / target_util * rf_factor
inv_MBps ≈ inv_qps × avg_inv_bytes / 1e6
```

### F — Closer checklist

- [ ] Coherence classes  
- [ ] Invalidation+TTL  
- [ ] Stampede/hot-key  
- [ ] Cells  
- [ ] Progressive scale  
- [ ] Azure tenancy/security  

---

## Deep Technical Notes — Distributed Cache

### Consistent hashing details

Virtual nodes per physical; weighted by capacity; gentle rebalance; versioned ring; avoid storing stale rings without epoch.

### Read repair

On meta mismatch across replicas, fetch origin or authoritative replica; async repair others.

### Invalidation delivery

At-least-once bus; consumers idempotent by version; snapshot lag metric; dead-letter poison messages; shard bus by key hash at high QPS.

### Admission control

TinyLFU/W-TinyLFU: don’t admit one-hit wonders thrashing working set during bots/crawlers.

### Personalization pitfalls

Never use object-id-only key for per-user payloads; include user/segment hash; encrypt sensitive; short TTL.

### MultiGet bundle

Scatter-gather; partial fill; hedge slow replica carefully; bound fanout.

### Warmup after failover

Top-K by traffic; progressive fill; origin rate limit; jittered client retries.

---

## Interview Cards — Distributed Cache (Microsoft)

### Card 1: Cache-aside vs write-through?

Cache-aside default; write-through for owned session stores.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Origin ownership (Cosmos/SQL team) vs cache platform boundary.

### Card 2: Invalidation?

Versioned bus + TTL backstop.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** CDC from Azure data services.

### Card 3: Consistent hashing?

Minimize movement; vnodes.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Online scale-out without customer downtime.

### Card 4: Hot keys?

Replicate/stripe/edge.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Viral tenant / world event.

### Card 5: Stampede?

Singleflight + SWR + jitter.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Protect shared origins on expire cliffs.

### Card 6: Never cache?

Unscoped PII; unresolved authz; huge unbounded objects.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Compliance / privacy review.

### Card 7: L1 safety?

Short TTL; versions; no cross-user.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** M365 process multi-user hosts.

### Card 8: Multi-region?

Regional L2; CDN public; careful inv.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Sovereign cloud boundaries.

### Card 9: Poisoning?

Auth writers; no client fills.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Multi-tenant SaaS threat model.

### Card 10: Metrics?

Hit, origin_qps, inv lag, stale_served.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** FinOps + SRE shared dashboard.

### Card 11: Eviction?

LRU/LFU + TinyLFU admission; pin critical.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Noisy-neighbor namespaces.

### Card 12: Negative cache?

Short TTL; careful with 5xx vs 404.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Avoid outage amplification.

### Card 13: Large values?

Blob pointer; size admission.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Compose with Azure Blob.

### Card 14: Deal-breaker?

TTL-only ACL; no cells; ignore stampede.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Security + SEV history.

---

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

Hit rate, get latency, origin qps, invalidation lag, error rate, memory saturation, singleflight waiters, stale_served.

### Rollback ladder

Disable L1 → revert router → SWR-only → shed traffic → cell isolate → bypass origin with throttle.

### Kill switches

Namespace disable; stop admissions; flush prefix gated; bypass to origin with RL.

### Security / privacy

ACL namespaces; audit flushes; PII TTLs; private endpoints; CMK optional.

### Cost worksheet

DRAM + network vs origin compute. Lever: hit rate and admission.

### Progressive scale

10× shards; 100× cells/edge; 1,000× client/edge intelligence.

### Cross-team deps

Origin data services, identity, CDC/eventing, CDN, capacity/FinOps.

---

## More Interview Q&A — Distributed Cache

**Q1. Soft vs hard TTL?**

**A:** Soft TTL serves stale while refresh; hard TTL must revalidate. SWR uses soft bounds.

**Q2. Version vectors vs integers?**

**A:** Per-key monotonic integer from SoT usually enough; vectors if multi-writer without SoT order.

**Q3. Compression?**

**A:** Compress large JSON; CPU vs network at 100×.

**Q4. Hedged gets?**

**A:** Tail latency help; watch amplification.

**Q5. CRC/version mismatch?**

**A:** Treat as miss; refetch; metric poison_rate.

**Q6. Cell sticky routing?**

**A:** Route tenants to cells; caches local.

**Q7. Warmup strategy?**

**A:** Top keys by traffic; progressive; avoid origin melt.

**Q8. Client-side CDN?**

**A:** Public assets yes; personalized no.

**Q9. Write amplify invalidation?**

**A:** Coalesce; version wins; batch.

**Q10. Observability sampling?**

**A:** Trace get→origin exemplars on misses.

**Q11. Cost of 1% hit drop?**

**A:** Quantify origin QPS and $.

**Q12. Security multi-tenant?**

**A:** Authz on flush; namespace ACLs; no cross-tenant poke.

**Q13. Refresh-ahead?**

**A:** For stable top-K; wasteful for long-tail.

**Q14. Two-phase delete?**

**A:** Tombstone short TTL then drop; helps replicas.

**Q15. Clock skew on TTL?**

**A:** Prefer absolute expire_at from server; skew bound documented.

**Q16. Connection pooling?**

**A:** Proxies pool to nodes; avoid thundering reconnects.

**Q17. Slabs vs jemalloc?**

**A:** Slab fragmentation classic memcached issue; size classes matter.

**Q18. Canary new codec?**

**A:** Dual-read; version payload envelope; rollback.

**Q19. Who owns hit-rate SLO?**

**A:** Joint: platform provides mechanics; service owns key design & TTL choices.

**Q20. Closing pitch?**

**A:** “Versioned cache-aside with singleflight, coherence classes, hot-key cells, and hit-rate economics—not a bigger Redis VM.”

---

## Progressive Architecture Jump Cards

### 1×

SDK L1 + regional L2 hash cluster + inv bus + TTL.

### 10×

More shards; compression; MultiGet; hot-key sketches; TinyLFU.

### 100×

Cells; edge; sharded invalidation; tenant quotas.

### 1,000×

Client dictionaries; hierarchical caches; approx admission; sovereign isolation.

---

## Failure Scenario Scripts

**A — Stampede:** Singleflight metrics spike; enable SWR; jitter TTL; page origin + cache.

**B — Inv bus lag:** Staleness SLO breach; rely TTL; scale consumers; replay DLQ.

**C — Poison ACL cached:** Version bump; flush namespace prefix gated; disable L1; security IR.

**D — Memory pressure:** Admission tighten; evict C1 first; protect C2 pins.

**E — Region failover cold:** Prefetch top-K; raise origin RL; accept temporary miss storm with coalescing.

---

## Coherence Matrix (whiteboard)

| Class | TTL | Invalidation | SWR | Strong fallback |
|-------|-----|--------------|-----|-----------------|
| Metadata | 5–30m | Yes | Yes | Rare |
| ACL | 10–60s | Prioritized | No/minimal | Yes |
| Flags | 1–5m | Yes | Bounded | Optional |
| Session | 1–5m | Yes | No | Yes |
| Public | hours | Optional | Yes | CDN |

---

## Ownership & SEV Model

| Symptom | Primary | Secondary |
|---------|---------|-----------|
| Hit-rate cliff | Service (keys/TTL) | Cache platform |
| Node melt hot key | Cache platform | Service |
| Wrong ACL served | Security + service | Cache |
| Inv lag | Cache platform | Eventing |
| Origin melt | Joint stampede | — |

---

## Sample 60-Second Pitch

> We provide a multi-tenant cache-aside platform. Clients use an SDK with process L1 and singleflight. A regional L2 fleet uses consistent hashing with replicas across Azure AZs. Each key carries a version and TTL; writers or CDC publish invalidations on a bus; TTL is the backstop. Coherence classes spell out freshness for metadata versus ACLs. Hot keys are detected and replicated; admission control protects DRAM from one-hit wonders. We scale through shards, then cells and edge, and we judge success by origin QPS and hit rate—not by pretending the cache is the source of truth.

---

## Appendix G — Anti-patterns

1. TTL-only for entitlements.  
2. Cross-user L1 keys.  
3. Client-untrusted fill.  
4. Unbounded MultiGet.  
5. Global sync invalidation for everything.  
6. No singleflight.  
7. Per-key Prometheus labels.  
8. Big-bang flush migration.

---

## Appendix H — Mock pushbacks

**Push:** “Make the cache strongly consistent globally.”  
**Reply:** “That’s a database. We offer versions and origin strong reads.”

**Push:** “Hashing removes hot keys.”  
**Reply:** “Removes key imbalance, not popularity imbalance.”

**Push:** “Just buy larger VMs.”  
**Reply:** “Admission + cells + hit economics beat blind DRAM growth.”

---

## Appendix I — Definition of done

- [ ] Stampede test: origin QPS bounded  
- [ ] Inv lag SLO dashboard  
- [ ] Hot-key auto-replicate  
- [ ] Namespace ACL enforced  
- [ ] Hit-rate × origin cost worksheet  
- [ ] L1 kill switch  
- [ ] Chaos node loss  

---

## Appendix J — API sketch

```text
GET  /v1/{ns}/keys/{key} -> {value, version, ttl_remaining}
SET  /v1/{ns}/keys/{key} {value, ttl, version?}
DEL  /v1/{ns}/keys/{key}
POST /v1/{ns}/keys:batchGet
POST /v1/{ns}/invalidate {key, version}
```

Auth: managed identity; admin flush requires elevated role + audit.

---

## Appendix K — Stampede control toolkit

| Tool | Effect |
|------|--------|
| Singleflight | 1 miss fill per key |
| Soft lock TTL | Distributed coalesce |
| SWR | Serve stale during refresh |
| Jittered TTL | Desync expiries |
| Probabilistic early expire | Spread refresh |
| Prefetch top-K | Deploy/failover |
| Origin RL | Hard backstop |

---

*End of Microsoft Distributed Cache system design prep.*
