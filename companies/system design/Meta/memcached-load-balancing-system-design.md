# System Design: Load Balancing for Memcached Servers

> **Focus areas:** Consistent hashing · Request routing · Hot keys · Replication · Connection pooling · Failover · Rebalancing · Client vs proxy · Soft/hard state  
> **Style:** End-to-end infrastructure design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct hash math; split client/proxy/server planes; deal-breakers for “modulo N rehash on every scale” and “LB with no hot-key story”  
> **Interview theme:** Classic Meta infra — scale a giant Memcached fleet without melting on rebalance or celebrities keys

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the problem**—design **load balancing / request distribution for Memcached servers** powering a large social/web cache tier: route get/set/delete to the right nodes, survive node churn, handle hot keys, and keep hit rate high across progressive scale.

### 1.0 What this is / is not

| Dimension | **Memcached LB (this doc)** | Not this |
|-----------|-----------------------------|----------|
| Primary job | Distribute cache ops across mc servers | Replace DB; design full TAO |
| Data | Ephemeral cache key/value | Durable source of truth |
| Success | High hit rate, even load, fast failover | Perfect consistency |
| Balancer | Client library and/or proxy layer | L4 TCP RR alone without key affinity |
| Consistency | Best-effort cache | Linearizable store |

**Scope statement:** Design how clients/proxies choose Memcached servers (consistent hashing, pools, failover, hot keys) as the fleet grows 10×→1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Ops? | get, multiget, set, add, delete, touch | Route by key |
| F2 | Keyspace? | Huge; skewed (celebrities) | Hot-key strategy |
| F3 | Who routes? | Client lib and/or mcrouter-like proxy | Placement of LB logic |
| F4 | Pools? | Multiple pools by workload | Pool configs |
| F5 | Replication? | Optional replica sets for hot/HA | Replication factor |
| F6 | Failover? | Skip dead hosts quickly | Health + outage windows |
| F7 | Rebalance? | Add/remove hosts with minimal misses | Consistent hash / continuum |
| F8 | Multiget? | Batch keys → fanout per server | Scatter-gather |
| F9 | TLS/auth? | Internal DC mostly; optional | Sidecar/proxy |
| F10 | Observability? | Hit rate, latency, err, occupancy | Metrics |
| F11 | Thundering herd? | Stale-while-revalidate / leases | Client+app coop |
| F12 | Cross-region? | Usually regional caches | No global mc affinity |

**MVP functional scope:**

1. Key-based routing via **consistent hashing** (ketama-style) to Memcached nodes.  
2. Client library and/or shared proxy (mcrouter-class) with connection pools.  
3. Health checking; temporary failover; retry policies that don’t amplify outages.  
4. Multiget assembly/scatter.  
5. Hot-key detection + replication / local client cache / slab.  
6. Controlled rebalance on membership change; config distribution.  
7. Pool isolation (e.g., user vs feed vs negative-cache).  
8. Dashboards + key sampling (careful PII).

**Out of MVP:**

- Making Memcached durable  
- Cross-DC synchronous cache  
- Full DB query planner  
- Arbitrary Lua at every edge without bounds

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Get latency | Inline with app | p99 < 1–5ms in-DC |
| N2 | Availability | High for cache | Degrade to DB on miss/fail |
| N3 | Hit rate | Workload-dep | Minimize rebalance miss storm |
| N4 | Balance | Even bytes/QPS | <2× imbalance typical; handle hot keys separately |
| N5 | Failover speed | Fast detect | Seconds; avoid flapping |
| N6 | Ops safety | Safe add/remove | Staged draining |
| N7 | Connection scale | Many apps | Pooling / proxy |
| N8 | Correctness | Stale OK | No cross-key corruption |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `get(user:123)` → hash → server 17 → HIT.  
2. `multiget` 50 keys → 8 servers → merge.  
3. Add 10% capacity → consistent hash moves ~10% keys.  
4. One server dies → failover; keys remapped or miss to DB.  
5. Hot key replicated to R nodes; reads spread.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Modulo hashing scale-out | Mass miss — forbidden |
| Hot key `page:Taylor` | Replicate / client cache / lease |
| Multiget partial timeout | Return partial + mark misses |
| Network blip | Short retry; circuit break |
| Thundering herd on miss | Singleflight / lease |
| Config split brain | Versioned membership; epoch |
| Uneven key lengths/values | Monitor bytes not just QPS |
| Proxy overload | Scale proxy tier; client bypass for some pools |
| Dirty failover flap | Hysteresis; grace |
| Key migration mid-set | Accept transient double; TTL heals |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Memcached servers | 200 | 2K | 20K | 200K (many clusters) |
| Peak get QPS | 10M | 100M | 1B | multi-cluster |
| Peak set QPS | 1M | 10M | 100M | — |
| Working set | tens TB | hundreds TB | PB | many pools |
| Clients / app hosts | 5K | 50K | 500K | proxies mandatory |
| Connections without proxy | explosive | — | — | — |
| Hot keys | dozens | hundreds | dynamic | automated |
| Pools | 5–10 | 20+ | many | platform |

**What each jump forces:**

- **10×:** Consistent hash everywhere; connection pooling; basic hot-key.  
- **100×:** Proxy tier (mcrouter); replica sets; automated membership; pool platform.  
- **1,000×:** Many independent clusters; hierarchical config; rack-aware; SLO-driven autosplit pools.

### 1.5 Etc. (Constraints & Assumptions)

- Memcached is **cache**, not DB; misses hit TAO/MySQL/etc.  
- In-DC latency budget tiny.  
- Keys are strings; values opaque blobs with TTL.  
- Goal of LB: **key affinity + balance + churn resilience**.

**Scope statement to repeat back:**

> Design load balancing for Memcached: consistent-hash routing via clients and/or proxies, health-aware failover, multiget fanout, hot-key mitigation, and membership rebalance that minimizes miss storms—scaled through pools and proxy tiers.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Notes |
|-------|-------|
| Gets | Dominant |
| Sets/deletes | Invalidation / fill |
| Multigets | Fanout amplification |
| Config watches | Membership |
| Health checks | Control plane |

### 2.2 Why not L4 RR?

```text
Memcached is a sharded hashmap. Random TCP LB without key routing
→ get goes to wrong box → artificial miss → DB melt
Deal-breaker: layer-4 round-robin across mc nodes for key-value ops
```

### 2.3 Consistent hashing miss math

```text
N servers; add M servers
Expected key movement ≈ M/(N+M)
Add 10% capacity → ~9–10% keys remapped (vs nearly 100% with modulo)
```

### 2.4 Connection explosion

```text
5K app hosts × 200 mc servers = 1M TCP conns
Each mc handling 5K inbound conns — painful
Proxy tier: hosts → few proxies → mc servers
```

### 2.5 Multiget fanout

```text
multiget 100 keys; N=200; roughly ~100 distinct servers worst, typically dozens
Timeouts: per-server budget; partial results
```

### 2.6 Hot key

```text
1 key at 2M QPS to one server (200K QPS cap) → overload
Need replicate R=10 → 200K/server or client-side cache 1ms TTL
```

### 2.7 Vnode balance math

```text
Physical N=200; vnodes/server=100 → 20K continuum points
Stddev of load ↓ as √(points) improves; diminishing returns past ~100–200 vnodes
Weight 2× RAM → 2× points
Too many vnodes: memory + binary-search cost on proxy
```

### 2.8 mcrouter hop cost

```text
Extra hop in-DC: ~100–300µs typical budget OK vs 1–5ms get SLO
Benefit: 5K apps × 200 mc → 1M conns becomes 100 proxies × 200 mc = 20K conns
Proxy CPU bound on multiget fanout + serialization
```

### 2.9 TKO / failover miss storm

```text
Host dies owning 1/N keys; without replicas → those keys miss until refill
N=200 → 0.5% keyspace cold; at 10M QPS → 50K miss/s to DB — plan headroom
Flapping TKO without hysteresis doubles miss storms — deal-breaker
```

### 2.10 Multiget scatter

```text
100 keys; ketama → often 30–60 unique servers
Parallel get; deadline 2–3ms per server; merge partial
Worst case fanout min(keys, N) — cap multiget size (e.g. 100–200)
```

### 2.11 Rebalance worksheet

| Change | Approx keys moved | DB fill risk |
|--------|-------------------|--------------|
| +1 / N=200 | ~0.5% | Low |
| +10% capacity | ~9% | Plan |
| Replace 20% fleet | ~20% | Staged drain |
| Modulo N→N+1 | ~100% | Outage |

### 2.12 BOTE anti-patterns

| Anti-pattern | Failure |
|--------------|---------|
| Modulo hash | Mass miss on scale |
| L4 RR | Wrong node → artificial miss |
| Retry next 10 ring owners | Outage amplification |
| Ignore hot keys | Single host melt |

---

## 3. High-Level Design

### 3.1 Routing API (logical)

```text
route(key, pool) -> server | replica_set
get/set/delete routed accordingly
multiget: group keys by server; parallel; merge
```

### 3.2 Consistent hashing — Why X over Y

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **modulo(hash, N)** | Simple | Remap almost all on N change | Deal-breaker |
| **Consistent hash continuum (ketama)** | Minimal remap | Hotspots possible | **MVP** |
| Jump consistent hash | Fast, minimal memory | Harder weighted | Option |
| Rendezvous (HRW) | Clean | Costlier CPU | Option |
| Range sharding | — | Rebalance heavy | Rare for mc |

**Chosen:** Ketama-like continuum with virtual nodes for balance; weights for heterogeneous hardware.

### 3.3 Client vs proxy — Why X over Y

| Mode | Pros | Cons | When |
|------|------|------|------|
| **Thick client** | Low hop | Library sprawl; conn explosion | Small fleets |
| **Proxy (mcrouter)** | Conn mux; shared features | Extra hop (~µs–sub-ms) | **Large Meta-like** |
| Hybrid | Flexibility | Complexity | Some pools direct |

**Chosen MVP at scale:** Proxy tier for most pools; simple clients for tiny/debug pools.

### 3.4 Replication — Why X over Y

| Mode | Pros | Cons |
|------|------|------|
| No replica | Simple | Hot key death; host fail → miss |
| **Replicate sets (R)** | Read spread; HA | Set amplification; inconsistency window |
| Full cluster mirror | Waste | Rare |

**Chosen:** Optional replica factor per pool; sets go to all replicas; gets pick random/latency-based replica; deletes all.

### 3.5 Failover — Why X over Y

| Mode | Pros | Cons |
|------|------|------|
| Hard fail remap immediately | Fast | Miss storm + flap |
| **Outage mode with hysteresis** | Stable | Temporary imbalance | **MVP** |
| Dual-write migrate | Smooth | Complex | Growth ops |

**Chosen:** Health check → mark TKO; requests failover along hash ring next owners OR replica; reintegrate slowly.

### 3.6 Why X over Y summary

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Hash | Consistent + vnodes | Rebalance | modulo N |
| Path | Proxy at scale | Conns/features | Pure L4 RR |
| Hot keys | Replicate + client soft cache | Skew | Ignore skew |
| Failover | TKO + hysteresis | Stability | Flap remap storms |
| Pools | Isolate workloads | Noisy neighbor | One giant shared LRU for all |
| Membership | Versioned config | Consistency of routing | Ad-hoc `/etc/hosts` edits |

### 3.7 Expanded HLD tradeoffs

| Axis | A | B | Pick |
|------|---|---|------|
| Routing | modulo / L4 RR | Ketama + vnodes | **Ketama** |
| Path | Thick client only | mcrouter proxy | **Proxy at Meta scale** |
| Hot key | Ignore | Replicate + L1 | **Mitigate** |
| Failover | Instant remap | TKO hysteresis | **TKO** |
| Rebalance | Big-bang replace | Weighted canary ramp | **Canary ramp** |

**Anti-patterns:** modulo resize; L4 RR; retry storms; mc as source of truth; one shared LRU for all products.

---

## 4. Architecture Diagram

```text
  Application Workers (many)
           |
           |  get/set/multiget (memcache protocol or thrift)
           v
  +------------------------+
  | Proxy Tier (mcrouter)  |
  |  - consistent hash     |
  |  - pools / routes      |
  |  - retries / TKO       |
  |  - hot key replicate   |
  |  - conn pools          |
  +-----------+------------+
              |
      +-------+-------+--------+
      |               |        |
      v               v        v
  [mc pool A]    [mc pool B] [mc pool C]
   shard ring     replica sets  negative cache

  Control plane:
  Membership/Config Service --> push routing updates (epoch)
  Health checkers --> TKO signals to proxies
  Metrics: hit rate, qps/bytes per host, TKO, latency
```

**Get path:**

```text
app -> proxy
  -> hash key on continuum
  -> pick replica (if R>1)
  -> get
  -> HIT return / MISS return
```

**Set path:**

```text
app -> proxy -> set to all replicas in set (or primary+async)
```

**Membership change:**

```text
config epoch N+1 distributed
proxies reload continuum
~fraction keys move; expect miss fill
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Same key → same primary owners** for a given membership epoch (modulo intentional hot-key overrides).  
2. **Cache miss is always safe** (DB/source truth).  
3. **TKO hosts excluded** until healthy + grace.  
4. **Partial multiget failure ≠ whole failure** unless app requires.  
5. **Config epochs monotonic** on proxies.

#### 5.1.2 Retry policy

```text
Do not blindly retry storms to next N servers on timeout (amplification)
Retry once to replica if configured
Circuit-break sick hosts
```

#### 5.1.3 Consistency of replicas

Replicas may diverge briefly; TTL + delete-all + periodic repair. Acceptable for cache.

#### 5.1.4 Stampede control (app coop)

```text
LEASE / early refresh / singleflight in app or proxy
stale-while-revalidate patterns
```

### 5.2 Scalability

#### 5.2.1 Virtual nodes

```text
Each physical server → many points on ring
Improves balance; tune vnode count vs memory/CPU
Weighted: more vnodes for bigger hosts
```

#### 5.2.2 Proxy scaling

Stateless routing; scale horizontally; shard pools across proxy groups if needed; keep routing config synced.

#### 5.2.3 Hot-key playbook

| Technique | Mechanism |
|-----------|-----------|
| Replicate | R copies on distinct hosts |
| Client L1 | Process-local LRU 1–50ms |
| Split key | Cache shards `key#0..k` if value aggregable (rare) |
| Rate limit sets | Prevent write storm |
| Dedicated mini-pool | Ultra-hot entities |

#### 5.2.4 Pool isolation

Separate noisy workloads: large values vs tiny; high churn vs stable; negative caching pools.

#### 5.2.5 Progressive scale map

| Scale | Must |
|-------|------|
| Baseline | Consistent hash client |
| 10× | Pooling; vnodes; metrics |
| 100× | Proxy; replicas; automated TKO |
| 1,000× | Many clusters; platform automation; rack awareness |

### 5.3 Maintainability

- Declarative pool configs (code review).  
- Canary membership changes (add 1 host, watch miss rate).  
- Drain: remove from ring gradually / `warmup` before serving gets.  
- Standard libraries; forbid each team’s custom hash.  
- Runbooks for hot keys and imbalance.

### 5.4 Ketama continuum sketch

```text
for server in servers:
  for i in 0..vnodes-1:
    continuum[hash(server + i)] = server
sort continuum points
route(key):
  h = hash(key)
  find first point >= h (binary search), wrap around
```

### 5.5 Health / TKO

```text
consecutive failures >= threshold -> TKO for T seconds
probe soft gets
success streak -> reintegrate
exponential backoff; jitter
```

### 5.6 Multiget

```text
group keys by route(server)
parallel get per server with timeout
merge; missing keys = miss
optional: hedged request on p99 straggler (careful amp)
```

### 5.7 Warmup / cold host add

```text
add host with weight 0 -> ramp weight
or shadow dual-get fill
avoid sudden 1/N traffic to empty slab (miss spike still expected)
```

### 5.8 Security & tenancy

Internal network; optional per-pool ACLs at proxy; don’t log raw PII keys; memcache injection historically N/A binary proto preferred.

### 5.9 Observability

| Metric | Use |
|--------|-----|
| Hit rate per pool | Product health |
| QPS/bytes per host | Balance |
| TKO count | Incidents |
| Proxy CPU | Capacity |
| p99 get | SLO |
| Rebalance miss delta | Ops |

Key sampling with redaction for hot-key discovery.

### 5.10 Interaction with DB

Cache-aside standard:

```text
v = mc.get(k)
if miss: v = db; mc.set(k,v,ttl)
invalidate on write (delete)
```

LB design must not cause synchronized expiry storms—jitter TTLs.

### 5.11 Nested deep dive — Consistent hashing & vnodes

#### 5.11.1 Continuum

```text
for server in servers:
  for i in 0 .. (vnodes * weight) - 1:
    continuum[hash(server_id + "#" + i)] = server
sort continuum
route(key):
  h = hash(key)
  return first point >= h (binary search), wrap
```

#### 5.11.2 Why vnodes

| Without vnodes | With vnodes |
|----------------|-------------|
| Coarse ring arcs; unlucky hosts hot | Smoother QPS/bytes |
| Hard to weight hardware | More points = higher weight |

Tune: ~100–200 vnodes/server typical; watch proxy memory/CPU.

#### 5.11.3 Remap fraction

```text
Add M servers to N: expected move ≈ M/(N+M)
≠ modulo which moves ~all
```

#### 5.11.4 Alternatives

| Algo | Notes |
|------|-------|
| Ketama continuum | **MVP**; weights via vnodes |
| Jump hash | Fast; equal nodes; weak weights |
| HRW / rendezvous | Natural weights; more CPU |

**Deal-breaker:** `server = hash(key) % N`.

### 5.12 Nested deep dive — mcrouter (proxy tier)

#### 5.12.1 Responsibilities

```text
consistent hash routing per pool
connection pooling + pipelining
multiget scatter/gather
TKO / retries (bounded)
replica sets / warmups
optional hot-key replicate profiles
metrics + key sampling (redacted)
```

#### 5.12.2 Conn math win

```text
Apps → few proxies → mc servers
vs apps × servers all-to-all mesh
```

#### 5.12.3 Cost

Extra in-DC hop; proxy CPU, ops, blast radius — mitigate with many proxies, pool isolation, canaries.

#### 5.12.4 Config

```text
versioned pool configs (epoch)
algo=ketama; servers[]; weights; replicas; tko{threshold,duration}
atomic reload; canary proxies first
```

### 5.13 Nested deep dive — Hot keys

#### 5.13.1 Detection

```text
proxy samples keys → top-K by QPS
host imbalance = max_qps / avg_qps; alert if >2 sustained
```

#### 5.13.2 Mitigations

| Technique | When |
|-----------|------|
| Replicate R copies | Ultra-hot reads |
| Client L1 LRU (1–50ms) | Extreme celebrities |
| Dedicated mini-pool | Persistent hot entities |
| Split key (rare) | Aggregable values only |
| Rate-limit sets | Write storms |

#### 5.13.3 Why hash alone fails

One key → one primary owner; QPS concentrates regardless of vnode count.

#### 5.13.4 Replica read/write

```text
set/delete → all replicas
get → random or least-latency replica among non-TKO
brief divergence OK (TTL heals)
```

### 5.14 Nested deep dive — TKO

#### 5.14.1 State machine

```text
healthy --(fail streak ≥ T)--> TKO
TKO --(probe success streak)--> healthy
TKO duration with exponential backoff + jitter
```

#### 5.14.2 Behavior while TKO

- Exclude from routing (or only replica failover).  
- Do **not** remap entire ring every blip.  
- Cap retries to avoid amplifying outage.

#### 5.14.3 Hysteresis

Flap (up/down) causes repeated miss storms — threshold + minimum TKO time mandatory.

#### 5.14.4 Interaction with replicas

Prefer read other replica; if pool R=1, miss to DB with coalescing/leases.

### 5.15 Nested deep dive — Multiget

#### 5.15.1 Algorithm

```text
group keys by route(server)
parallel mc get_multi per server with per-server deadline
merge map; absent keys = miss
return partial results to app
```

#### 5.15.2 Limits

- Cap keys per multiget (e.g. 100–200).  
- Bound fanout; watch proxy CPU.  
- Hedged requests only with strict amp caps.

#### 5.15.3 Partial failure

Timeout on 1/40 servers ≠ fail whole multiget; app DB-fills misses.

### 5.16 Nested deep dive — Rebalance

#### 5.16.1 Add capacity runbook

```text
1. Provision mc + metrics
2. Config epoch: add with low weight (canary)
3. Watch hit rate, imbalance, errors, DB QPS
4. Ramp weight to target
5. Document epoch
```

#### 5.16.2 Drain / remove

```text
weight → 0 or TKO → QPS drain → remove from continuum → shutdown
optional warmup on peers; expect fractional miss fill
```

#### 5.16.3 Math expectation

```text
+10% servers ≈ ~9% keys move
Plan DB headroom for fill; jitter TTLs avoid sync expiry
```

#### 5.16.4 Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| Modulo resize | Mass miss |
| Instant full weight on empty host | Miss spike + slab cold |
| Simultaneous replace 50% fleet | Outage-shaped rebalance |

### 5.17 Nested deep dive — Scale & deal-breakers

#### 5.17.1 Progressive scale

| Scale | Must |
|-------|------|
| 10× | Ketama+vnodes; pools; metrics; basic hot-key |
| 100× | mcrouter; replicas; automated TKO; membership epochs |
| 1,000× | Multi-cluster platform; rack-aware; autosplit pools |

#### 5.17.2 Deal-breakers

1. Modulo-N rehash on resize.  
2. L4 RR without key affinity.  
3. No hot-key plan.  
4. Retry amplification around the ring.  
5. All-to-all connections without proxies at large host counts.  
6. Treating Memcached as durable source of truth.

---

## 6. Wrap-Up

### 6.1 60-second pitch

> Memcached load balancing is key-aware routing, not TCP round-robin. Use consistent hashing with virtual nodes, preferably behind a proxy tier that pools connections, handles TKO failover, multiget fanout, and hot-key replication. Membership is versioned; rebalances move only a fraction of keys. Cache misses fall back to source of truth. At Meta scale, pools and automation matter as much as the hash function.

### 6.2 Deal-breakers

1. Modulo-N rehash on every resize.  
2. L4 RR without key affinity.  
3. No hot-key plan.  
4. Retry amplification across the ring.  
5. Connection mesh without proxies at large host counts.  
6. Treating mc as durable source of truth.

### 6.3 Scale one-liner

Client consistent hash → proxy+TKO+replicas → multi-cluster platform with automated pools.

---

## 7. Deeper / Related Interview Questions

### Q1. Why consistent hashing?

**Answer:** When nodes change, only ~1/N keys remaps, preserving hit rate vs modulo which remaps nearly everything.

### Q2. Why not load-balance Memcached with nginx RR?

**Answer:** Gets would miss randomly; cache becomes useless; DB melts. Need key affinity.

### Q3. What are virtual nodes?

**Answer:** Multiple hash points per server on the ring to smooth imbalance and support weights.

### Q4. Client vs mcrouter proxy?

**Answer:** Proxies reduce connection explosion, centralize retries/hot-key/replication logic; cost is an extra hop and proxy ops.

### Q5. How do you handle hot keys?

**Answer:** Detect via metrics/sampling; replicate to R hosts; short client L1 caches; sometimes dedicated pools.

### Q6. Explain TKO.

**Answer:** Temporary knockout of unhealthy server after failure thresholds; probes before reintegration; prevents flap.

### Q7. Multiget timeout strategy?

**Answer:** Per-shard deadlines; return partial; app fetches misses from DB; avoid waiting for slowest forever.

### Q8. Replica set read/write?

**Answer:** Write/delete all replicas; read one (random or least latency). Accept brief inconsistency.

### Q9. How much traffic moves when adding 10% servers?

**Answer:** Roughly ~9–10% of keys—the fraction of ring ownership gained by new nodes.

### Q10. Thundering herd on expiry?

**Answer:** Jitter TTLs; leases; singleflight; stale-while-revalidate.

### Q11. Connection pooling numbers?

**Answer:** Few connections per proxy→server with pipelining; apps→proxies also pooled; avoid all-to-all.

### Q12. Weighted servers?

**Answer:** Bigger RAM hosts get more continuum points / higher weight.

### Q13. Cross-region Memcached?

**Answer:** Usually no; each region has own cache; fill from local DB/TAO. Cross-region cache adds coherence pain.

### Q14. How to drain a host for maintenance?

**Answer:** Mark TKO or remove from continuum; allow miss fill elsewhere; optional pre-copy; then shut down.

### Q15. Dirty cache after DB write?

**Answer:** Delete/invalidate key on write path; accept race windows; versioned values if needed.

### Q16. Negative caching?

**Answer:** Cache “not found” short TTL in dedicated pool to protect DB from repeated misses.

### Q17. Observing imbalance?

**Answer:** Per-host QPS and bytes; Gini/ratio alerts; adjust vnodes/weights; find hot keys.

### Q18. Retry storms?

**Answer:** Cap retries; failover only to replicas; circuit breakers; bulkheads per pool.

### Q19. Security of proxy?

**Answer:** Internal only; auth between app and proxy optional; don’t expose mc to Internet.

### Q20. Slippery slope: put logic in proxy?

**Answer:** Keep focused: routing, RL, retries, replication. Don’t build a new application server.

### Q21. Jump hash vs ketama?

**Answer:** Jump hash is fast and minimal memory for equal nodes; ketama/HRW easier for weights and heterogeneous fleets—discuss tradeoffs.

### Q22. What if proxy tier dies?

**Answer:** Redundant proxies; apps reconnect; short outage → DB load spike—capacity plan DB brownout.

### Q23. Key naming conventions?

**Answer:** Versioned prefixes `v2:user:123`; helps mass invalidate by changing version.

### Q24. Slab allocator impact on LB?

**Answer:** Value size mix causes internal fragmentation; isolate large-object pools so LB isn’t blamed for slab issues.

### Q25. How fast should failover be?

**Answer:** Seconds; faster than human; slower than single blip—use thresholds.

### Q26. Can consistent hash alone solve hot keys?

**Answer:** No—one key still maps to one primary; need replication or client cache.

### Q27. Config distribution?

**Answer:** Versioned files/service; atomic epoch switch; canary proxies first.

### Q28. Multi-get amplification limit?

**Answer:** Cap keys per multiget; split; protect proxy/mc.

### Q29. Latency SLO budget?

**Answer:** In-DC get p99 single-digit ms; proxies must be local; avoid cross-rack if possible for ultra-hot pools.

### Q30. What changes from 200 to 20K servers?

**Answer:** Must have proxies, automated membership, pools, hot-key automation; can’t hand-edit rings.

### Q31. Consistent hashing with failed node: remap or replica?

**Answer:** Prefer replicas for HA pools; else next-on-ring failover with care about miss storms; both used in practice.

### Q32. How to test rebalance?

**Answer:** Shadow traffic; measure hit rate delta; staged weight ramp; rollback plan.

### Q33. Memcached vs Redis for this design?

**Answer:** Similar routing ideas; Redis more data structures/persistence options—question is still key hashing + hot keys + conns.

### Q34. Fairness across tenants?

**Answer:** Separate pools per product; proxy rate limits; avoid one product LRU-evicting another.

### Q35. Success metrics for LB project?

**Answer:** Hit rate stability across expansions, host imbalance ratio, failover MTTR, proxy p99, DB error burn during mc incidents, hot-key incident count.

### Q36. How many vnodes are enough?

**Answer:** Empirically ~100–200 per server often smooths balance; more has diminishing returns and costs continuum memory/CPU — measure imbalance.

### Q37. mcrouter vs thick client at 5K app hosts?

**Answer:** Proxies win on connection count and centralized TKO/hot-key; thick client OK for tiny fleets/debug pools.

### Q38. TKO vs immediate consistent-hash remap?

**Answer:** Immediate remap causes miss storms and flaps; TKO with hysteresis + replicas is stabler; reintegrate slowly.

### Q39. Multiget partial timeout — app responsibility?

**Answer:** Treat missing keys as misses; DB fill with singleflight; don’t block UI on slowest shard forever.

### Q40. Rebalance + hot key simultaneously?

**Answer:** Fix hot key with replication first; then ramp weights — otherwise imbalance metrics lie and DB burns twice.

### Q41. Why jitter TTLs in an LB design doc?

**Answer:** Synchronized expiry creates herd gets to the same owners; LB can’t save you from correlated miss storms.

### Q42. Platform checklist at 20K servers?

**Answer:** Automated epochs, proxy fleets, pool catalog, hot-key automation, rack-aware replicas, canary rebalances — no hand-edited rings.

---

## Appendix A — Continuum pseudocode

```text
def build(servers, vnodes):
  ring = []
  for s in servers:
    for i in range(vnodes * s.weight):
      ring.append((hash(f"{s.id}#{i}"), s.id))
  ring.sort()
  return ring

def route(ring, key):
  h = hash(key)
  i = lower_bound(ring, h)
  return ring[i % len(ring)][1]
```

## Appendix B — Modulo vs consistent

| Event | Modulo keys moved | Consistent |
|-------|-------------------|------------|
| N→N+1 | ~N/(N+1) ≈ all | ~1/(N+1) |
| N→N+N/10 | ~all | ~0.09 |

## Appendix C — Proxy route config sketch

```text
pool users {
  servers = [10.0.0.1:11211 weight=10, ...]
  algo = ketama
  replicas = 2
  tko = {threshold=3, duration=30s}
}
```

## Appendix D — Hot key detector

```text
sample keys at proxy
topk by qps
alert + auto replicate profile
```

## Appendix E — Multiget merge

```text
results = {}
for server, keys in groups:
  results.update(get_multi(server, keys))
return results
```

## Appendix F — TTL jitter

```text
ttl' = ttl * (0.9 + 0.2*rand)  # reduce sync expiry
```

## Appendix G — NFR card

```text
Key affinity via consistent hash
No L4 RR
Proxy at scale
TKO hysteresis
Hot-key replication
Miss → DB safe
```

## Appendix H — Failure matrix

| Failure | Effect | Mitigation |
|---------|--------|------------|
| 1 mc host | Local miss↑ | TKO + replica |
| Proxy host | App reconnect | Redundant proxies |
| Bad config | Wrong routes | Epoch canary |

## Appendix I — Connection math

```text
100 proxies × 2K mc = 200K conns total vs 5K×2K=10M without proxy
```

## Appendix J — Replica write

```text
for r in replicas(key):
  set(r, key, val, ttl)
# best-effort; count successes
```

## Appendix K — Drain steps

1. Stop new ownership (weight↓)  
2. Watch QPS↓  
3. TKO  
4. Power off  

## Appendix L — Pool catalog examples

| Pool | Pattern |
|------|---------|
| user_obj | small objects |
| feed_blob | medium |
| neg_cache | tiny short TTL |
| session | volatile |

## Appendix M — Worked rebalance

```text
2000 servers; add 200
fraction moved ≈ 200/2200 ≈ 9.1%
If hit rate 95%, temporary effective hit ≈ 95%*(1-0.091)+fill costs
Plan DB headroom for that delta
```

## Appendix N — Circuit breaker

```text
per-server error rate > X -> open
half-open probe
```

## Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Continuum | Hash ring points |
| TKO | Temporary knockout |
| vnode | Virtual node |
| mcrouter | Meta-style memcache proxy |
| Cache-aside | App fills on miss |
| Negative cache | Cache empty result |

## Appendix P — 30m checklist

1. Kill RR/modulo ideas.  
2. Consistent hash + vnodes.  
3. Proxy/conn math.  
4. Hot keys + TKO.  
5. Rebalance fraction.  
6. Deal-breakers.

## Appendix Q — Hedged requests caution

Hedging doubles load; only for rare p99 tails with caps.

## Appendix R — Rack awareness

Place replicas in different racks; continuum can bias—advanced.

## Appendix S — Metrics formulas

```text
imbalance = max_qps / avg_qps
alert if imbalance > 2 for sustained window (excluding known hotkey events)
```

## Appendix T — Lease protocol sketch

```text
get miss -> acquire lease -> fetch DB -> set -> release
others wait or serve stale
```

## Appendix U — Config epoch

```text
{epoch: 42, pools: {...}, hash: "sha256"}
proxies ack; control plane watches
```

## Appendix V — Progressive scale

| Scale | Must |
|-------|------|
| 10× | Ketama, pools, metrics |
| 100× | Proxy, replicas, TKO auto |
| 1,000× | Multi-cluster platform |

## Appendix W — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Redis Cluster handles it” | Still need hot-key/ops story; same principles |
| “Just add RAM” | Hot key is QPS not RAM |
| “RR is fine if identical data” | Replication×all keys impossible at scale |

## Appendix X — Partial outage UX

App should brownout features vs hard 500 when cache tier sick; serve stale if safe.

## Appendix Y — Pseudocode proxy get

```text
def get(pool, key):
  servers = owners(pool, key)  # primary + replicas
  for s in prefer_order(servers):
    if tko(s): continue
    try: return mc_get(s, key)
    except: note_fail(s)
  return MISS
```

## Appendix Z — Success bar

Expansions barely dent hit rate, hosts stay balanced except managed hot keys, failovers are boring, and DB doesn’t melt when the cache tier hiccups—because routing was designed as a key-aware system, not a TCP sprinkler.

---


## Appendix AA — Add capacity runbook

```text
1. Provision hosts with mc + monitoring
2. Add to config epoch with low weight (canary)
3. Watch hit rate, imbalance, error rate
4. Ramp weight to target
5. Document epoch in change log
```

## Appendix AB — Hot-key incident runbook

```text
1. Alert: host QPS >> peers
2. Sample keys on proxy
3. Enable replicate R=N or client L1 TTL
4. Optionally move entity to dedicated pool
5. Postmortem: why not detected earlier
```

## Appendix AC — Compare routing algorithms

| Algo | Remap on +1 | Weights | CPU |
|------|-------------|---------|-----|
| modulo | terrible | awkward | tiny |
| ketama | ~1/N | via vnodes | low |
| jump | ~1/N | hard | tiny |
| HRW | ~1/N | natural | medium |

## Appendix AD — DB brownout during mc outage

```text
Expect miss storm → protect DB with:
  request coalescing
  serve stale if app has soft state
  feature flags disable noncritical reads
  proxy negative caching short TTL
```

## Appendix AE — Interview closer

```text
"Key-aware consistent hashing, proxies for connection mux, TKO failover, hot-key replication,
and rebalance math that moves ~ΔN/N keys—not modulo carnage."
```

## Appendix AF — Sample imbalance worksheet

```text
avg QPS/host = 50k
max = 140k (hot key)
imbalance = 2.8 -> page hot-key playbook
after R=4 replicate: max ~40–50k -> healthy
```

*End of Memcached Load Balancing system design.*
