# System Design: Edge-Network Application Platform

> **Focus areas:** Deploy functions to PoPs · Routing & anycast · Edge state · Cold start · Consistency at edge · Security isolation  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Clear control vs data plane, honest consistency limits, cold-start budgets, deal-breakers for “strong global consistency on every edge mutate”  
> **Interview theme:** Google L5+ edge compute / CDN+FaaS — placement, isolation, routing, progressive global scale

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

Goal: **bound the platform**—a **multi-tenant edge application platform** that lets developers **deploy functions/apps to Points of Presence (PoPs)**, **route users to nearby healthy instances**, manage **edge-friendly state**, control **cold starts**, and reason about **consistency + security**. This is not a full AWS replacement in one region.

### 1.0 What this is / is not

| Dimension | **Edge app platform (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Run customer code near users | Global strongly consistent OLTP DB |
| Success | Low TTFB, safe isolation, fast deploy | Bit-identical state all PoPs always |
| Data plane | Anycast → PoP → isolate → invoke | Central monolith only |
| Control plane | Build, deploy, config, traffic | IDE / full CI product |
| Correctness | Per-request isolation; explicit state model | Hidden cross-PoP ACID |

**Scope statement:** Design an edge FaaS/app platform: deploy to PoPs, route traffic, isolate workloads, manage cold start, offer edge state with clear consistency, and secure multi-tenancy—scaling through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Compute model? | Functions (HTTP/event) + optional long-lived workers Phase 1.5 | FaaS MVP |
| F2 | Languages? | JS/WASM first; containers later | Isolate choice |
| F3 | Deploy API? | Upload artifact + route config; versions | Control plane |
| F4 | Routing? | Anycast/geoDNS → nearest PoP; traffic split | Health + weights |
| F5 | State? | KV/cache at edge; durable regional origin | Explicit tiers |
| F6 | Cold start SLO? | p95 cold < 50–100ms WASM; containers higher | Runtime choice |
| F7 | Triggers? | HTTPS, cron, queue from origin | Ingress types |
| F8 | Secrets? | Per-app encrypted secrets | KMS + seal at PoP |
| F9 | Observability? | Logs/metrics/traces sampled | Edge → central |
| F10 | Multi-tenant isolation? | Hard isolation required | Sandbox |
| F11 | Regions/PoPs? | Dozens → hundreds | Hierarchical control |
| F12 | SLA / preview? | Versioning, canary, rollback | Traffic manager |

**MVP functional scope:**

1. Developers deploy **versioned function artifacts** to the platform.  
2. Platform distributes to **selected PoPs** (all / geo subset).  
3. User requests hit **global VIP/anycast** → PoP proxy → **sandbox invoke**.  
4. Provide **edge KV** (eventually consistent) + APIs to **regional durable store**.  
5. **Warm pools** + snapshots to bound cold start.  
6. **mTLS, authn/z hooks, secret injection**, per-tenant CPU/mem/time limits.  
7. Canary % traffic, instant rollback by config pointer.  
8. Metrics/logs pipeline with sampling.

**Out of MVP:**

- Arbitrary persistent TCP services with sticky IPs worldwide  
- Cross-PoP serializable transactions  
- GPU training at every PoP  
- Full Kubernetes API compatibility (mention container path)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Latency | Edge advantage | p50 TTFB +10–30ms over static CDN cache hit path |
| N2 | Cold start | Predictable | WASM p95 < 100ms; container p95 < 1–2s with pool |
| N3 | Availability | PoP failures local | Global 99.99% via anycast failover |
| N4 | Isolation | No cross-tenant escape | Defense in depth |
| N5 | Deploy time | Fast iteration | Global config < 1–2 min; code push pipelined |
| N6 | Consistency | Explicit | Edge KV eventual; origin strong optional |
| N7 | Scale | Huge RPS | Horizontal PoPs; tenant quotas |
| N8 | Security | Supply chain + runtime | Signed artifacts; seccomp/WASM |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `deploy v3` → build → sign → replicate artifact → PoPs ack → traffic 1% canary → 100%.  
2. User in SYD → SYD PoP warm isolate → KV read → response 40ms.  
3. PoP unhealthy → anycast steers to next PoP.  
4. Secret rotate → control plane pushes sealed blob → apps reload.  
5. Rollback → point route to v2 atomically per PoP.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cold start stampede | Soft queue + pre-warm; shed with 503 |
| Noisy neighbor | Hard cgroup/WASM fuel limits |
| Split brain KV | Version vectors / LWW; app-level conflict |
| Origin outage | Serve stale KV / cached; degraded header |
| Bad artifact crashloop | Health check; remove from rotation |
| PoP capacity full | Overflow to nearby PoP; admit control |
| Clock skew | Avoid sync time deps; use logical versions |
| Huge artifact | Reject; size limits; delta layers |
| Tenant pin-SKU region | Placement constraints in scheduler |
| DDoS | Edge L7 shield before invoke |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| PoPs | 20 | 50 | 150 | 500+ |
| Tenants | 1K | 10K | 100K | 1M |
| Active apps | 5K | 50K | 500K | 5M |
| Global RPS | 100K | 1M | 10M | 100M |
| Deploys/day | 5K | 50K | 500K | 5M |
| Artifact store | 10 TB | 100 TB | 1 PB | multi-PB |
| Edge KV keys | 100M | 1B | 10B | 100B |
| Warm isolates | 50K | 500K | 5M | 50M+ |
| Control plane QPS | 100 | 1K | 10K | 100K |

**What each jump forces:**

- **10×:** Hierarchical config distribution; artifact CDN; per-PoP autoscaling.  
- **100×:** Cell-based control plane; WASM-first; KV sharding; progressive rollout.  
- **1,000×:** Regional aggregators, peer cache for artifacts, tenant placement packs, extreme multi-tenant densification.

### 1.5 Etc. (Constraints & Assumptions)

- PoPs have limited power/space — density matters.  
- Not all apps belong at edge (heavy stateful writes → regional).  
- Platform provides **primitives**; apps choose consistency.  
- Compliance may restrict where code/data may run.

**Scope statement to repeat back:**

> Design a multi-tenant edge application platform that deploys signed functions to PoPs, routes via anycast/health, invokes in strong sandboxes with bounded cold start, offers eventually consistent edge KV plus regional durability, and scales control/data planes through 10× / 100× / 1,000×—without pretending every mutate is globally strongly consistent.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split planes (critical)

| Plane | What | Baseline | 10× |
|-------|------|----------|-----|
| **Data plane RPS** | User invokes | 100K | 1M |
| **Control plane** | Deploy/config | 0.1–1% of data | grows with tenants |
| **Artifact replication** | Bytes to PoPs | bursty | pipelined |
| **KV reads/writes** | Edge state | 0.5–2× RPS | skewed |
| **Telemetry** | Spans/logs | sampled 1–10% | aggressive sample |

**Anti-pattern:** one “QPS” for deploys and invokes.

### 2.2 Bandwidth & artifacts

```text
Artifact 5MB × 50 PoPs = 250MB per deploy
5K deploys/day × 250MB = 1.25 PB/day if naïve full copy — DEAL-BREAKER
Must: content-addressed layers, delta, only PoPs that need app, regional distributors
```

### 2.3 Cold start math

```text
If 1% of 1M RPS cold at 500ms → disaster concurrency
Need: keep-alive pools, hysteresis scale-down, predictive pre-warm for top apps
Target: <0.1% cold on popular apps; accept cold on long-tail
```

### 2.4 Isolation density

```text
PoP: 100 servers × 64 cores × 4 isolates/core (WASM) = 25.6K concurrent
At 10M RPS global / 150 PoPs ≈ 67K RPS/PoP
If avg 5ms CPU/request → 335 cores busy — need ~10+ servers/PoP just CPU + overhead
```

### 2.5 KV consistency cost

```text
Sync replicate every write to 150 PoPs = death
Edge KV: local + async gossip / regional home
Cross-PoP read-your-write: sticky / home tip / accept lag
```

---

## 3. High-Level Design

### 3.1 API (developer / control)

| Op | Semantics |
|----|-----------|
| `POST /apps/{id}/versions` | Upload artifact; returns `version` |
| `PUT /apps/{id}/route` | `{version, percent, countries?, binders}` |
| `POST /apps/{id}/rollback` | Point to prior version |
| `PUT /apps/{id}/secrets` | Seal secrets |
| `GET /apps/{id}/status` | PoP ack map / health |
| `PUT /apps/{id}/kv/{key}` | App data plane KV (via worker SDK) |
| `GET /metrics` | Usage / errors |

**Data plane:** `https://app.example.com/*` → customer function `fetch(req)`.

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| App | `app_id` | tenant, placement policy, limits |
| Version | `(app_id, ver)` | artifact digest, runtime, created |
| Route config | `app_id` | active versions + weights + geo rules |
| Artifact | `digest` | layers CAS |
| PoP inventory | `pop_id` | capacity, health, location |
| Edge KV | `(ns, key)` | value, version, expire |
| Secret | `(app_id, name)` | sealed ciphertext |
| Deployment ack | `(pop, app, ver)` | status |

### 3.3 Runtime isolation — Why X over Y

| Approach | Cold start | Density | Safety | When |
|----------|------------|---------|--------|------|
| **Process + cgroup** | Medium | Medium | Good | Simple MVP |
| **Containers (gVisor/Firecracker)** | Slower | Lower | Strong | Untrusted native |
| **V8 isolates / WASM** | Fast | High | Strong if hardened | **Edge MVP pick** |
| **Bare metal shared** | Fast | High | Weak | Never multi-tenant |

**Chosen:** WASM or V8-isolate first; Firecracker path for heavy/native Phase 1.5.

### 3.4 Routing — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **DNS geo alone** | Simple | TTL stickiness | Small |
| **Anycast IP** | Fast failover | ECMP asymmetry | **MVP+** |
| **Client library steering** | Smart | Adoption | Mobile SDKs |
| **Central LB** | Easy consistency | Loses edge | Anti-pattern |

**Chosen:** Anycast to PoP → L7 proxy (SNI/host) → tenant scheduler → isolate.

### 3.5 State tiers

```text
L0: Request-local memory (ephemeral)
L1: Edge KV / cache (PoP local, async replicate) — eventual
L2: Regional strong DB / object store — home region
L3: Global config (version pointers) — strongly ordered via control plane

App must pick tier; platform documents guarantees
```

**Deal-breaker:** advertising “linearizable KV in every PoP” as default.

### 3.6 Cold start strategy

| Technique | Effect |
|-----------|--------|
| Keep-alive warm pool | Removes cold for active apps |
| Snapshot / pre-initialized heap | Faster isolate create |
| Bundled deps / no huge downloads at invoke | Critical |
| Predictive pre-warm (diurnal) | Top tenants |
| Soft concurrency queue | Prevent thundering init |

### 3.7 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Runtime | WASM/isolates | Cold start + density | Raw shared Node multi-tenant |
| Routing | Anycast + L7 | Failover + host routing | Hairpin to single region |
| Artifacts | CAS layers + regional fanout | Bandwidth | Full copy every PoP every deploy |
| State | Tiered KV | Honesty | Global ACID edge KV |
| Control plane | Hierarchical | Scale deploys | Chatty every PoP ↔ global DB |
| Security | Signed + sandbox + limits | Multi-tenant | Trust customer binary on host |

---

## 4. Architecture Diagram

```text
                         [Control Plane - Regional Cells]
                         +------------------------------+
  Developers -> API ---> | Deploy / Route / Secrets     |
                         | Scheduler / Placement        |
                         +------+---------+-------------+
                                |         |
                     config/artifacts     acks/health
                                v         ^
                         +------+---------+-------------+
                         | Distributors (per region)    |
                         | Artifact cache + gossip      |
                         +------+-----------------------+
                                |
        +-----------------------+-----------------------+
        v                       v                       v
   +----+-----+            +----+-----+            +----+-----+
   | PoP A    |            | PoP B    |            | PoP C    |
   |----------+            |----------+            |----------+
   | Anycast  |            | Anycast  |            | Anycast  |
   | L7 Proxy |            | L7 Proxy |            | L7 Proxy |
   | Isolates |            | Isolates |            | Isolates |
   | Edge KV  |            | Edge KV  |            | Edge KV  |
   | Telemetry|            | Telemetry|            | Telemetry|
   +----+-----+            +----+-----+            +----+-----+
        |                       |                       |
        +-----------------------+-----------------------+
                                v
                     +----------+-----------+
   Users ----------> | Global Anycast VIP   |
                     +----------------------+

   Origin / Regional durable services <--- functions call via secure egress
```

---

## 5. Design Deep Dive

### 5.1 Control plane vs data plane

| Plane | Responsibilities | Scale pattern |
|-------|------------------|---------------|
| Control | Authn developer, store versions, compute placement, push config | Cells, strong metadata DB |
| Data | Route packets, invoke, KV, egress | PoP autonomous under cached config |

**Golden rule:** data plane runs if control plane is down (stale-but-safe config).

### 5.2 Deployment pipeline

```text
1. Upload → virus scan → build/bundle → sign (platform key)
2. Store CAS digest in artifact store
3. Compute target PoP set from placement policy
4. Push digest to regional distributors → PoP pull/push
5. PoP verifies signature → stage version inactive
6. Route config update with weight
7. Health: synthetic probes per PoP
8. Increase weight; on error burn → auto rollback
```

### 5.3 Config distribution

| Method | Pros | Cons |
|--------|------|------|
| Poll global | Simple | Lag / load |
| Push tree | Fast | Complex |
| Gossip | Resilient | Convergence time |

**Chosen:** hierarchical push (global → region → PoP) + version epoch; PoP rejects older epochs.

### 5.4 Request path (happy)

```text
TCP anycast → PoP
TLS terminate (or passthrough + SNI)
Host → app_id
Load route config → version
Admit (quota, WAF)
Get/create isolate (warm preferred)
Inject env/secrets/bindings
Invoke with deadline
Write logs/metrics sampled
Response
```

### 5.5 Edge KV design

```text
API: get/put/delete/list-prefix; optional TTL
Single-key linearizability within PoP
Cross-PoP: async replication; LWW or vector clocks
Optional: key hash → home PoP/region for stronger read-your-write
Conflict: return both / last-writer-wins; app chooses
```

**Why X over Y:** CRDT counters good for likes; not for bank balance — document.

### 5.6 Consistency patterns for apps

| Pattern | How |
|---------|-----|
| Read-mostly config | Edge KV + version; poll origin |
| User session | Encrypt cookie / regional session store |
| Write-heavy ledger | Forward to regional DB; edge validates |
| Feature flags | Control plane config — strongly ordered |

### 5.7 Cold start deep dive

```text
Isolate create:
  allocate fuel/mem → load module (cached mmap) → instantiate → run
Cache modules by digest globally on node
Pool: min_warm per app per PoP based on RPS EMA
Scale down with hysteresis to avoid flapping
```

**Containers:** Firecracker snapshot resume for Phase 1.5 heavy runtimes.

### 5.8 Security

| Layer | Control |
|-------|---------|
| Supply chain | Signed artifacts; SBOM optional; deny unsigned |
| Sandbox | WASM wasmtime/V8; no raw host FS |
| Resource | CPU ms, mem, wall deadline, egress bytes |
| Network | Egress allowlist / policy; no peer tenant |
| Secrets | Sealed to PoP TPM/identity; memory scrub |
| Tenancy | Separate keys; noisy neighbor limits |
| Abuse | WAF, bot, per-app RPS |

**Deal-breaker:** running unsandboxed tenant code as root containers without gVisor/Firecracker story.

### 5.9 Reliability

| Failure | Mitigation |
|---------|------------|
| PoP offline | Anycast withdraw / health |
| Bad version | Auto rollback on error budget |
| KV partition | Local serve; resync |
| Distributor down | Peer PoP fetch artifact |
| Control plane down | Last good config |
| Thundering cold | Queue + 503 + pre-warm |

**Reliability principles:**

1. Data plane autonomy.  
2. Immutable artifacts (CAS).  
3. Health-gated traffic.  
4. Explicit deadlines everywhere.  
5. Progressive delivery.

### 5.10 Scalability

| Scale | Tactic |
|-------|--------|
| 10× | Regional distributors; PoP autoscaling; module cache |
| 100× | Control cells; WASM densify; KV shard by key; sample telemetry hard |
| 1,000× | Tenant packing; artifact P2P; geo route tables compacted; overflow meshes |

**Placement packs:** co-locate many tiny apps per node; pin large tenants to dedicated hosts.

### 5.11 Maintainability

| Practice | Why |
|----------|-----|
| Runtime ABI versioning | Safe upgrades |
| Synthetic canaries per PoP | Detect broken hosts |
| Config as data (epoch) | Debuggable |
| Chaos: kill PoPs | Practice failover |
| Tenant quotas dashboards | Support |

### 5.12 Observability

```text
Edge spans → local buffer → regional aggregator → central
High cardinality: app_id, pop_id, version, status
Default sample errors 100%, OK 1%
Log PII scrubbing hooks
```

### 5.13 Progressive scale deep dive

**Baseline:** 20 PoPs, central control DB, WASM, Redis-like KV per PoP async.

**10×:** distributors; canary automation; secret seal; module CAS cache.

**100×:** control plane cells; KV home-tip option; Firecracker pool; WAF.

**1,000×:** P2P artifacts; hierarchical route compression; dedicated noisy tenants; compliance zones (data residency).

---

## 6. Wrap-Up

### 6.1 Design summary

An **edge application platform** with a **hierarchical control plane**, **anycast data plane**, **WASM/isolate multi-tenant security**, **CAS artifact fanout**, **warm pools for cold start**, and **tiered state** (edge eventual KV + regional durable)—scaled by PoP autonomy and progressive densification.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Lost |
|----------|--------|------|
| Density vs capability | WASM first | Heavy native default |
| Consistency vs latency | Eventual edge KV | Global linearizability |
| Deploy speed vs safety | Canary + sign | Instant 100% unscoped |
| Autonomy vs control | Cached config | Live dependency on CP |

### 6.3 Deal-breakers

1. Strong global consistency as default edge KV.  
2. Unsandboxed multi-tenant native code.  
3. Full artifact replication every deploy to all PoPs.  
4. Data plane hard-down when control plane blips.  
5. Ignoring cold-start pools at high RPS.  
6. Central hairpin LB defeating edge purpose.

### 6.4 Progressive scale one-liner

> **Isolates + anycast → regional distributors & warm pools → control cells & KV tiers → P2P artifacts and packing at planet scale.**

### 6.5 Reliability / Scalability / Maintainability

```text
Reliability: PoP failover, canary rollback, CP-decoupled data plane
Scalability:  CAS fanout, WASM density, hierarchical control, KV home tips
Maintainability: epochs, synthetics, ABI versions, chaos drills
```

---

## 7. Deeper / Related Interview Questions

### 7.1 Routing & PoPs

**Q1: Anycast vs geoDNS?**  
A: Anycast failover faster; combine with health. DNS TTLs can sticky users to dead PoPs.

**Q2: How avoid tromboning?**  
A: Egress to nearest regional origin; don’t bounce back across ocean without need.

**Q3: Sticky sessions?**  
A: Prefer stateless; else cookie with region tip or consistent hash carefully.

### 7.2 Cold start

**Q4: Why WASM over containers at edge?**  
A: Instantiation cost and density; containers for compatibility.

**Q5: How size warm pools?**  
A: EMA RPS × latency × safety factor; min floors for paid tiers.

**Q6: Dependency download at invoke?**  
A: Forbid; bundle or pre-cache layers.

### 7.3 Consistency

**Q7: Read-your-write after PUT at edge?**  
A: Same PoP yes; cross-PoP need home key or sync wait.

**Q8: Can we CRDT everything?**  
A: No — wrong for unique constraints / money.

**Q9: Config vs KV consistency?**  
A: Config via control epochs (ordered); KV app data eventual.

### 7.4 Security

**Q10: Tenant breakout?**  
A: Defense in depth: WASM + process + seccomp + no shared writable FS.

**Q11: Secret exposure in dumps?**  
A: Sealed storage; inject at runtime; prevent log of env.

**Q12: Supply chain?**  
A: Sign digests; optional reproducible builds; deny unknown publishers.

### 7.5 Scale & ops

**Q13: Control plane hotspot?**  
A: Shard by tenant; cells; don’t ack storm global DB per request.

**Q14: Telemetry cardinality explosion?**  
A: Bound labels; aggregate at PoP.

**Q15: Noisy neighbor detection?**  
A: Per-app fuel; steal/throttle; relocate.

### 7.6 Estimation drills

**Q16: Artifact bandwidth without CAS?**  
A: Show PB/day math → force layering.

**Q17: Cores for 67K RPS at 5ms?**  
A: 67e3 × 5e-3 ≈ 335 cores busy.

### 7.7 Alternatives & deal-breakers

**Q18: Just use central Kubernetes?**  
A: Loses edge latency; still need PoP story.

**Q19: Smart clients only, no anycast?**  
A: Works for mobile; not for browsers/HTTPS random clients.

**Q20: Redis cluster stretched globally?**  
A: Latency/partitions — usually a bad default.

### 7.8 Interview craft

**Q21: Opening?**  
A: Split control/data; WASM; anycast; tiered state; cold start; security.

**Q22: L5+ signals?**  
A: Artifact fanout math, CP decoupling, honesty on consistency, canary.

**Q23: Common mistake?**  
A: Designing only K8s YAML; ignoring PoP bandwidth and cold start.

---

### Appendix A — Invoke path pseudocode

```text
def handle(conn):
  req = tls_http(conn)
  app = resolve(req.host)
  ver = route_pick(app, req)
  if not admit(app): return 429
  iso = warm_pool.get(app, ver) or cold_start(app, ver)
  try:
    return iso.fetch(req, deadline=app.limit)
  finally:
    warm_pool.maybe_return(iso)
```

### Appendix B — Route config

```json
{
  "app_id": "a123",
  "epoch": 8891,
  "rules": [
    {"weight": 5, "version": "v3", "countries": ["AU", "NZ"]},
    {"weight": 95, "version": "v2"}
  ]
}
```

### Appendix C — Artifact CAS

```text
digest = sha256(bundle)
layers: [runtime_base, deps, code]
PoP stores by digest; many apps share base
```

### Appendix D — KV replication

```text
onPut(key,val,ver):
  local.save
  enqueue_replicate(key,val,ver)
replicate:
  send to region hub → fanout peers (async)
onConflict: LWW by (ts, node_id) or vector
```

### Appendix E — Warm pool policy

```text
desired = clamp(min, EMA(rps)*p95_lat*safety, max)
reconcile every 5s
```

### Appendix F — Progressive scale table

| Scale | CP | DP | State | Runtime |
|-------|----|----|-------|---------|
| Baseline | Central | 20 PoPs | Per-PoP KV | WASM |
| 10× | +distributors | Autoscale | Async repl | +snapshots |
| 100× | Cells | 150 PoPs | Home tip | +Firecracker |
| 1,000× | Federated | 500 PoPs | Tiered | Packing |

### Appendix G — NFR card

```text
WASM cold p95 < 100ms (pooled popular)
Anycast PoP failover
Signed artifacts only
Edge KV eventual by default
Data plane survives CP outage
```

### Appendix H — Placement policy

```text
allow_pops: ALL | list | comply_tag
exclude: embargo countries
min_replicas: 2 regions
```

### Appendix I — Egress policy

```text
allow: *.api.customer.com, regional-db.internal
deny: metadata IP, link-local, other tenants
```

### Appendix J — Health signals

| Signal | Action |
|--------|--------|
| 5xx burn | Remove version weight |
| Isolate OOM | Crash metric; backoff |
| Probe fail | Withdraw anycast partial |
| CPU saturated | Overflow nearby |

### Appendix K — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Global sync KV” | CAP/latency math |
| “Containers everywhere” | Cold start/density |
| “CP must be up” | Cache epochs |
| “One big Kafka” | Not a PoP runtime |

### Appendix L — Related systems (conceptual)

| System | Relation |
|--------|----------|
| CDN / Anycast | Routing front |
| Workers / Lambda@Edge | Product analogs |
| CAS blob stores | Artifacts |
| Service mesh | Inspirations not copy |
| KMS/HSM | Secrets |

### Appendix M — Glossary

| Term | Meaning |
|------|---------|
| PoP | Point of Presence |
| Isolate | Lightweight sandbox instance |
| CAS | Content-addressed storage |
| Epoch | Monotonic config version |
| Fuel | Metered compute budget |
| Home tip | Preferred location for a key |

### Appendix N — Worked deploy example

```text
5MB → 3 layers (4.5MB shared base already present)
New delta 500KB × 50 PoPs = 25MB total
vs 250MB naïve — 10× save
Canary 1% 10 min → error < budget → 100%
```

### Appendix O — Consistency cheatsheet

| Op | Guarantee |
|----|-----------|
| Invoke local mem | Request scope |
| KV same PoP | Linearizable-ish local |
| KV cross PoP | Eventual |
| Route config | Epoch ordered |
| Regional SQL | Strong in region |

### Appendix P — 30m checklist

1. Clarify FaaS vs containers, state needs, cold SLO.  
2. Split CP/DP.  
3. Anycast + isolate path.  
4. Artifact CAS math.  
5. KV tiers honesty.  
6. Security layers.  
7. 10×/100×/1,000×.  
8. Deal-breakers.

### Appendix Q — Quota model

```text
per app: RPS, concurrent isolates, CPU ms/day, KV GB, egress GB
burst tokens with sustained caps
```

### Appendix R — Rollback

```text
route.epoch++
weights → previous version
PoPs apply within seconds
keep artifact for N days
```

### Appendix S — Multi-region compliance

```text
data_residency: EU keys only EU PoPs+regions
scheduler enforces placement + KV home
```

### Appendix T — Why hierarchical CP

```text
1M apps × 500 PoPs chatty heartbeats to one DB = meltdown
Aggregate health regionally
```

### Appendix U — Snapshot cold start

```text
Pre-init isolate → snapshot memory
Restore snapshot << full init
Invalidate on version change
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Distributors, warm pools, canary |
| 100× | CP cells, KV home, WAF |
| 1,000× | P2P artifacts, packing, residency |

### Appendix W — SDK bindings

```text
env.KV.get/put
env.ORIGINS.fetch
env.SECRETS.get
env.LIMITS.deadline
```

### Appendix X — Failure injection tests

| Chaos | Expect |
|-------|--------|
| Kill PoP | Traffic shifts |
| Corrupt artifact | Signature fail; no traffic |
| Delay KV repl | Apps still serve local |
| CP down | DP continues |

### Appendix Y — Opening script

> “I'll design an edge FaaS platform: signed WASM isolates at PoPs, anycast routing, hierarchical control plane, CAS artifact fanout, warm pools, and tiered state with eventual edge KV—scaling cells and densification without promising global ACID at the edge.”

### Appendix Z — Interview whiteboard order

```text
1) User → anycast → PoP proxy → isolate
2) CP deploy → distributors → PoP
3) KV tier note
4) Cold start pool
5) Security box
6) Scale arrows
```

---

*End of Edge-Network Application Platform system design.*
