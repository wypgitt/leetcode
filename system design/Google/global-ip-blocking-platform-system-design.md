# System Design: Global IP-Blocking Platform

> **Focus areas:** Blocklist distribution · Edge enforcement · Push vs pull · Propagation latency · Geo/jurisdictional rules · Audit & kill-switch  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Google L5+ — database choice, partitioning, ambiguity > reproducing Google internals

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

Goal: **bound the platform**—a control plane + data plane that ingests government/policy IP blocklists (and CIDR ranges), resolves conflicts across overlapping sources, and distributes them worldwide so **edge enforcers** (LBs, CDN POPs, DNS, application gateways) can deny traffic with **low-latency updates** and a clear audit trail. This is **not** a WAF rule engine or DDoS scrubbing fabric—though those may *consume* the same blocksets.

### 1.0 What this is / is not

| Dimension | **Global IP-blocking platform (this doc)** | Not this |
|-----------|--------------------------------------------|----------|
| Primary job | Authoritative block policy → worldwide enforcement snapshots | Packet scrubbing / volumetric DDoS |
| Success | Propagation SLO, correct deny/allow, auditability | Zero false positives forever |
| Data | IP/CIDR sets + metadata (source, jurisdiction, expiry) | Full L7 WAF signatures MVP |
| Path | Control plane publish + edge lookup | Inline DPI of every packet body |

**Scope statement:** Design a **global IP-blocking platform** that ingests multi-source blocklists, resolves conflicts, and distributes versioned enforcement sets to edges with tight propagation SLOs, kill-switch, and legal audit.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who publishes blocks? | Policy ops + automated ingest from govt/feeds | Dual path: human API + feed importers |
| F2 | What is blocked? | IPv4/IPv6 addresses and CIDR prefixes | Longest-prefix / set membership at edge |
| F3 | Where enforced? | Global edge (CDN/LB/DNS/app GW) | Push snapshots to POPs + local lookup |
| F4 | Latency of updates? | Seconds to low minutes worldwide | Versioned push + pull fallback |
| F5 | Geo / jurisdiction? | Block may apply only in region X | Scoped rules: `(set_id, region, cidr)` |
| F6 | Allowlist overrides? | Yes—safety & false-positive escape | Precedence: allow > deny (document) |
| F7 | Emergency kill-switch? | Global or per-region disable of a set | Signed kill + epoch bump |
| F8 | Audit / legal? | Who added what, when, why, evidence | Immutable audit log + retention |
| F9 | Conflict resolution? | Overlapping feeds; severity tiers | Explicit merge policy + precedence |
| F10 | Lookup API? | Edge: `IsBlocked(ip, region, product)` | Hot path in-memory; cold control plane |
| F11 | Expiry / TTL? | Temporary sanctions, court orders | Expiry in rule; GC + re-publish |
| F12 | False positive workflow? | Unblock ticket → expedited allow | Fast-path allow publish |

**MVP functional scope:**

1. Ingest block/allow rules (IP or CIDR) with source, jurisdiction scope, severity, expiry, evidence ref.  
2. Validate + normalize (canonical CIDR, reject bogons if policy says so).  
3. Merge into versioned **enforcement snapshots** per `(product, region)` or global.  
4. Distribute snapshots to edges (push primary, pull reconcile).  
5. Edge hot-path: O(1)/O(log n) `IsBlocked(ip)` with allow precedence.  
6. Kill-switch: disable a source/set/region within SLO.  
7. Audit trail for every mutation and every published version.  
8. Metrics: propagation lag, deny rate, false-positive tickets, edge memory.

**Out of MVP:**

- Full L7 WAF / bot management  
- Automated legal interpretation of court PDFs (humans + structured ingest)  
- Per-user reputation scoring  
- Active probing / honeypot feedback loops (hooks only)  
- Perfect global linearizability of every edge at T+0ms  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Propagation SLO | Critical | p99 worldwide ≤ 60s baseline; ≤ 15s emergency path |
| N2 | Edge lookup latency | Inline path | p99 < 50µs in-process; < 1ms if sidecar RPC |
| N3 | Availability (control) | High | 99.9% publish API; degrade to last-good snapshot |
| N4 | Availability (data plane) | Critical | 99.99% edge; fail-open vs fail-closed **product policy** |
| N5 | Correctness | Legal sensitivity | Deterministic merge; signed snapshots |
| N6 | Audit durability | Legal | Append-only; years retention |
| N7 | Scale of sets | Large CIDR tables | Millions of prefixes; memory-bounded edges |
| N8 | Safety | False positives costly | Allow override + staged rollout + canary |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Policy ops adds CIDR for jurisdiction `EU` → validated → merged → snapshot `vN` → edges ACK within SLO → traffic from that CIDR denied in EU only.  
2. Feed importer pulls govt list hourly → diff → new rules → publish.  
3. False-positive ticket → expedited allow → snapshot `vN+1` → allow wins over deny.  
4. Emergency kill-switch on toxic feed → edges drop that source’s contribution in <15s.  
5. Rule expires → GC removes → next snapshot no longer denies.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Overlapping deny from two feeds | Merge by precedence (severity, source rank, specificity) |
| Deny + allow same IP | **Allow wins** (MVP); audit both |
| Edge offline during publish | Pull on reconnect; version watermark |
| Partial POP update | Version fencing; optional dual-run; sticky per-connection |
| Malformed feed / poison CIDR `0.0.0.0/0` | Schema + blast-radius guards; require dual-control for global deny |
| Clock skew on expiry | Server expiry absolute time + skew skew-budget; edges use publish time + TTL |
| IPv4-mapped IPv6 | Normalize before match |
| Fail-open vs fail-closed on corrupt snapshot | **Fail closed for security products; fail open for consumer UX**—ask interviewer |
| Split-brain control plane | Single primary publisher via Raft/etcd lease; fencing token on snapshot |
| Legal hold prevents delete | Soft-delete + tombstone; still in audit |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Edge POPs / enforcer nodes | 200 | 2K | 20K | 200K |
| Distinct CIDR rules (global) | 2M | 20M | 200M | 2B (compressed/tries) |
| Products consuming sets | 5 | 20 | 100 | 500 |
| Regions / jurisdictions | 50 | 100 | 200 | 300+ |
| Publish events / day | 5K | 50K | 500K | 5M |
| Emergency publishes / day | 10 | 50 | 200 | 1K |
| Edge lookups / s (aggregate) | 10M | 100M | 1B | 10B |
| Avg snapshot size (compressed) | 50 MB | 200 MB | 1 GB | sharded sets |
| Propagation p99 target | 60s | 30s | 15s | 5–10s + delta |
| Audit events / day | 100K | 1M | 10M | 100M |

**What each jump forces:**

- **10×:** Delta publishing (not full snapshot every time); sharded topic fanout; Bloom/exact hybrid at edge.  
- **100×:** Set sharding by product/region; hierarchical distribution (global → regional relays → POP); compact tries (ART/Patricia).  
- **1,000×:** Cell/region control planes; incremental CRDT-like set sync with epochs; edge memory budgets force approximate structures + exact overflow; legal audit lake separate from hot path.

### 1.5 Etc. (Constraints & Assumptions)

- **Ambiguity first:** Ask fail-open vs fail-closed, who can publish global `/0`, and whether DNS/LB/app all share one set.  
- IPv4 + IPv6 both in scope; store as normalized prefixes.  
- Edges are untrusted relative to control plane → **signed snapshots** (ed25519/PKI).  
- Government feeds are messy (duplicates, stale, conflicting)—**merge policy is the product**.  
- Latency SLO is on **enforcement visibility**, not on human legal review.  
- Prefer **versioned immutable snapshots** over mutable shared maps.

**Scope statement:**

> Design a global IP-blocking control + data plane: multi-source ingest, jurisdictional scoping, deterministic conflict resolution, signed versioned snapshots distributed to worldwide edges with push+pull, sub-minute propagation, allow overrides, emergency kill-switch, and durable legal audit—scaling from hundreds of POPs to hundreds of thousands without melting edge memory or the publish fanout.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Edge lookup** | `IsBlocked(ip)` | ~10M/s | ~100M/s | In-process memory |
| **Snapshot publish** | Full/delta push | ~0.05–1/s avg; bursts | ×10 | Control → relays |
| **Feed ingest** | External pulls | ~1–10/min | ×10 | Importers |
| **Admin mutations** | CRUD rules | ~1–10/s | ×10 | OLTP + audit |
| **ACK / health** | Edge version reports | ~200/s | ~2K/s | Telemetry |
| **Audit writes** | Mutations + publishes | ~10–100/s | ×10 | Append log |

**Anti-pattern:** designing the whole system around admin CRUD QPS while the real fire is **lookup QPS × POP count** and **fanout bandwidth**.

### 2.2 Snapshot size & bandwidth

```text
2M IPv4 CIDRs × ~16–24B compact = ~32–48 MB raw
+ IPv6 + metadata → ~50–100 MB uncompressed
zstd → ~50 MB compressed (order)

200 POPs × 50 MB full push = 10 GB fanout per full publish
If full publish every 60s → 10 GB/min = unsustainable long-term
→ Prefer deltas: 0.1% change → ~50 KB × 200 = 10 MB/publish
```

### 2.3 Propagation math

```text
Target p99 ≤ 60s:
  compose snapshot: 1–5s
  sign + persist: <1s
  fanout to regional relays: 2–10s
  relay → POP: 2–10s
  load + atomic swap: 1–5s
Budget slack for retries + stragglers
Emergency path: precomputed “disable set X” tiny delta < 1 KB → seconds
```

### 2.4 Edge memory

```text
Exact Patricia/ART for 2M prefixes: tens of MB–low hundreds MB / process
At 200M prefixes: multi-GB → shard by product OR Bloom(deny) + exact overflow OR hierarchical tries
Lookup budget: < 50µs → must be local RAM; no remote call on deny path
```

### 2.5 Audit storage

```text
100K events/day × 2 KB = 200 MB/day raw
× 7 years ≈ 500 GB + indexes → easy with object store + indexed metadata
Hot query: last 90 days in OLAP/Search; cold in object store
```

### 2.6 Conflict / merge cost

```text
Naive rebuild from all rules each publish: O(R log R)
R=2M → OK on fat composer (~few seconds)
R=200M → incremental merge + segment trees / roaring bitmaps for IPv4
```

---

## 3. High-Level Design

### 3.1 APIs

| Op | Semantics |
|----|-----------|
| `CreateRule(source, cidr, scope, severity, expiry, evidence)` | Add deny or allow |
| `RevokeRule(rule_id, reason)` | Tombstone; new snapshot |
| `PublishSnapshot(product, region?, mode=full\|delta)` | Compose + sign + distribute |
| `KillSwitch(target, scope)` | Emergency disable source/set/region |
| `GetVersion(edge_id)` / `PullSnapshot(since_version)` | Reconcile |
| `IsBlocked(ip, region, product)` | Edge local API (library/sidecar) |
| `AckVersion(edge_id, version)` | Telemetry for lag SLO |
| `AuditQuery(filters)` | Legal / ops investigation |

### 3.2 Domain model

```text
Source      { source_id, rank, trust, jurisdiction_default }
Rule        { rule_id, source_id, action: DENY|ALLOW, cidr, scopes[], severity, expiry, evidence_ref }
Snapshot    { version, product, region, epoch, merkle_root, sig, created_at, parent_version }
SnapshotSeg { version, shard, blob_ref, checksum }   // at 100×+
EdgeState   { edge_id, current_version, last_ack, health }
AuditEvent  { id, actor, op, before, after, ts, ticket_ref }
```

**Invariant:** Edges only load **signed** snapshots whose `version` advances monotonically per `(product, region)` stream.

### 3.3 Push vs pull

| Mode | Pros | Cons | Use |
|------|------|------|-----|
| **Push** | Fast propagation; fits SLO | Fanout complexity; stragglers | **Primary** |
| **Pull** | Simple; self-heal | Poll lag; thundering herd on version bump | **Reconcile / catch-up** |
| Hybrid | Best of both | Two paths to maintain | **MVP choice** |

**Chosen MVP:** control plane pushes version notification + delta via regional relays; edges pull blob if notification missed; periodic pull every N minutes as safety net.

**Deal-breaker:** pull-only with 5-minute poll when emergency legal block needs <60s.

### 3.4 Exact sets vs Bloom filters

| Structure | Pros | Cons | When |
|-----------|------|------|------|
| **Exact trie / ART / Patricia** | No false positives | Memory | **MVP default** for deny/allow |
| Bloom (deny) | Tiny memory | False positives | Extreme scale hint only |
| Roaring bitmap (IPv4) | Fast set ops | IPv6 harder | IPv4 segments |
| Hash set of IPs | Simple | Explodes for wide CIDRs | Host-only lists |

**Chosen:** exact longest-prefix structures at edge; optional Bloom as **prefilter** only if FPP≈0 and still verify exact (or accept product-specific FPP—usually **unacceptable for legal IP block**).

**Deal-breaker:** Bloom-only deny for government blocks (false positives = wrongful blocking).

### 3.5 Conflict resolution

| Policy | Rule | Notes |
|--------|------|-------|
| Action precedence | ALLOW > DENY | Safety for FP |
| Specificity | Longer prefix wins within same action | `/32` over `/8` |
| Source rank | Higher trust / court order > bulk feed | Configurable |
| Severity | Critical > high > low when still tied | Document |
| Recency | Newer wins if still tied | Optional |
| Scope | Region-scoped rule ignored outside region | Hard filter |

**Composer algorithm (sketch):**

```text
for each scope (product, region):
  candidates = rules active at T covering scope
  build deny trie + allow trie with precedence
  emit immutable snapshot blob + merkle + signature
```

### 3.6 Geo / jurisdictional enforcement

```text
Client IP → edge POP region / user jurisdiction signal
IsBlocked(ip, jurisdiction, product):
  load snapshot(product, jurisdiction) or fallback global
  if allow.hit(ip): return false
  if deny.hit(ip): return true
  return false
```

**Ambiguity to resolve:** is jurisdiction from **POP location**, **user profile country**, or **DNS view**? Different products differ—parameterize.

### 3.7 Storage choices

| Component | Choice | Why | Deal-breaker |
|-----------|--------|-----|--------------|
| Rule OLTP | Spanner / Postgres-Citus / distributed SQL | Strong metadata, transactions | Single-node MySQL at 100× |
| Snapshot blobs | Object store (GCS/S3) + CDN | Large, immutable | DB BLOBs for 1GB snapshots |
| Version index | etcd/ZK or SQL | Monotonic version + lease | Unsigned “latest” file only |
| Audit | Append log (Kafka) → cold object + index | Immutability | Mutable rows as only audit |
| Edge state | In-memory + local disk checkpoint | Lookup latency | Remote Redis on every packet |

### 3.8 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Distribution | Push + pull reconcile | SLO + self-heal | Pull-only for emergency |
| Match structure | Exact trie | Legal FP intolerance | Bloom-only deny |
| Authority | Signed snapshots | Untrusted edges | Trust every POP admin |
| Merge | Deterministic composer | Replayable audit | Last-writer chaos |
| Fail mode | Product policy flag | UX vs security | Hidden global fail-open |
| Fanout | Regional relays | 10×–1000× scale | Mesh push from one VIP to 200K edges |
| Rollout | Canary % of POPs | Catch poison | Instant global `/0` deny |

---

## 4. Architecture Diagram

```text
  Govt feeds / Threat intel          Policy Ops / Tickets
           |                                |
           v                                v
  +----------------+                 +--------------+
  | Feed Importers |                 | Admin API    |
  +--------+-------+                 +------+-------+
           |                                |
           +---------------+----------------+
                           v
                  +------------------+
                  | Rule Store (SQL) |
                  | + Audit Log      |
                  +--------+---------+
                           v
                  +------------------+
                  | Snapshot Composer|
                  | merge/conflict   |
                  +--------+---------+
                           |
                    sign + merkle
                           v
                  +------------------+
                  | Object Store     |  snapshots / deltas
                  +--------+---------+
                           |
                           v
                  +------------------+
                  | Version Service  |  etcd lease / fencing
                  | publish notify   |
                  +--------+---------+
                           |
            +--------------+--------------+
            v              v              v
       Relay EU       Relay US       Relay APAC
            |              |              |
            v              v              v
         POP edges     POP edges     POP edges
         (LB/CDN/DNS/app GW)
            |
            v
       IsBlocked(ip) in-process
```

**Publish path (happy):**

```text
Admin/Importer -> Rule Store + Audit
  -> Composer builds snapshot vN (or delta vN-1→vN)
  -> Upload blob -> Sign -> Version Service CAS(vN-1 → vN)
  -> Notify relays -> push to edges -> AckVersion
  -> SLO monitor: lag = now - vN.created_at by percentile of edges
```

**Edge lookup path:**

```text
Packet/Request -> extract client IP + jurisdiction
  -> Allow trie? yes -> forward
  -> Deny trie? yes -> reject + metric
  -> forward
```

**Emergency kill-switch:**

```text
KillSwitch(source=X) -> Composer emits tiny delta "drop source X"
  -> high-priority topic -> edges apply in seconds
  -> full recomposition follows async
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Edges enforce only signed snapshots** with valid cert chain.  
2. **Version monotonicity** per stream `(product, region)`.  
3. **ALLOW overrides DENY** for same match class (MVP).  
4. **Last-good snapshot remains active** if new snapshot fails validation.  
5. **Every mutation audited** before/with publish.  
6. **Kill-switch is a first-class publish**, not SSH to POPs.  
7. **Blast-radius guards** on global deny (`/0`, enormous aggregates) require dual-control.

#### 5.1.2 Data loss prevention

| Asset | Durability | Notes |
|-------|------------|-------|
| Rules | Multi-AZ SQL | RPO≈0 with sync quorum |
| Snapshots | Object store 11-9s class | Immutable |
| Audit | Kafka multi-AZ + cold copy | Legal hold |
| Edge memory | Ephemeral | Rebuild from pull |

#### 5.1.3 Retries, idempotency, fencing

- Admin `CreateRule` with `Idempotency-Key`.  
- Version CAS: only one composer primary (etcd lease).  
- Edge apply: ignore versions ≤ current; verify signature + merkle.  
- Notify at-least-once; pull reconciles duplicates.

#### 5.1.4 Rate limits

| Surface | Limit |
|---------|-------|
| Admin mutations | Per-user / per-source QPS |
| Feed import | Per-feed bandwidth + rule delta caps |
| Edge pull | Coalesce; exponential backoff; jitter |
| Emergency path | Separate priority queue; not starved by bulk |

#### 5.1.5 Fail-open vs fail-closed

| Product class | On corrupt/missing set | Rationale |
|---------------|------------------------|-----------|
| Ads / consumer web | Often **fail-open** | Availability |
| Cloud console / admin | Prefer **fail-closed** for deny-lists that are security boundaries | Safety |
| Regulated market | Jurisdiction-specific | Legal |

**Say this in interview:** “I’d make fail mode a per-product policy bit on the snapshot header—not a hidden global.”

#### 5.1.6 False positives

```text
Detect: support tickets, canary allow probes, sudden deny spike
Mitigate: expedited ALLOW publish (< SLO)
Prevent: staged rollout (1% POPs → 10% → 100%), synthetic probes from known-good IPs
```

### 5.2 Scalability

#### 5.2.1 Traffic ups/downs

- Lookups scale horizontally with edges (local data).  
- Publish fanout scales via **relay tree**, not single publisher sockets.  
- Flash crowd after big feed: compose once; edges pull compressed delta.

#### 5.2.2 Storage evolution

| Scale | Rule store | Snapshots |
|-------|------------|-----------|
| Baseline | Single SQL primary + replicas | One blob / stream |
| 10× | Partition by source_id / product | Deltas + full weekly |
| 100× | Regional SQL cells; global version service | Sharded segments |
| 1,000× | Per-cell composers; global name service | Streaming set sync |

#### 5.2.3 Parallelization

- Compose shards by prefix ranges (`0.0.0.0/2` …) in parallel; merkle tree of shards.  
- Relays fanout in parallel per region.  
- Edge load: download → verify → build trie offline → **atomic pointer swap**.

#### 5.2.4 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Deltas; Bloom prefilter optional; relay tier |
| →100× | Snapshot sharding; hierarchical tries; product-scoped streams |
| →1,000× | Regional control planes; approximate structures only as accelerators; audit lake; edge memory cgroups |

#### 5.2.5 Hot keys / hot prefixes

Wide denies (`/8`) are cheap (one trie node). Hot **lookups** are fine (read-only). Hot **updates** to popular prefixes: composer serializes per stream; consider write coalescing.

#### 5.2.6 CDN / edge enforcement patterns

| Enforcer | Integration |
|----------|-------------|
| L4 LB | XDP/eBPF or ACL programming from snapshot |
| CDN POP | In-process library in request path |
| DNS | View-based REFUSED/NXDOMAIN for mapped names (different product) |
| App GW | Middleware filter |

Share **same snapshot format**; adapters differ.

### 5.3 Maintainability

#### 5.3.1 Versioning & rollout

```text
snapshot_format_version = 3
edge library N understands N and N-1
canary: pin 1% edges to vN; watch deny rate / error / CPU
auto-rollback: Version Service points to vN-1; push rollback delta
```

#### 5.3.2 Operability

- Dashboards: propagation histogram, edges_behind_version, deny_qps, composer_duration, signature_fail.  
- SLO burn alerts on p99 lag.  
- Runbooks: poison snapshot, stuck relay, feed explosion, kill-switch drill (game day).

#### 5.3.3 Observability

| Signal | Why |
|--------|-----|
| `edge_version` | Lag SLO |
| `deny_total{product,region}` | Impact |
| `allow_override_total` | FP pressure |
| `snapshot_bytes` / `delta_bytes` | Cost |
| `composer_conflicts` | Feed quality |
| `killswitch_latency` | Emergency drill |

#### 5.3.4 Legal audit

- Immutable events: actor, ticket, evidence hash, rule diff, snapshot version produced.  
- Query: “Why was IP X denied in DE at time T?” → find active snapshot → explain matching rule + source.  
- Retention vs privacy: store CIDRs + metadata; minimize PII in tickets.

#### 5.3.5 Testing

- Deterministic merge golden tests.  
- Property tests: allow always beats deny.  
- Chaos: drop 10% notifies; assert pull heals within SLO.  
- Fuzz CIDR normalization + IPv4-mapped IPv6.  
- Load: trie build time vs memory for 10×–100× synthetic sets.

---

## 6. Wrap-Up

### 6.1 What we designed

A **global IP-blocking platform**: multi-source rules with jurisdictional scope, deterministic conflict resolution (allow > deny, specificity, source rank), signed versioned snapshots distributed via **push + pull** through regional relays, exact edge tries for FP-intolerant enforcement, emergency kill-switch, and durable audit—scaled by deltas, sharding, and hierarchical fanout.

### 6.2 Invariants to memorize

| Invariant | Why |
|-----------|-----|
| Signed monotonic snapshots | Hostile/compromised edges |
| Exact match for legal deny | Bloom FP unacceptable |
| Allow overrides deny | FP remediation |
| Last-good on bad publish | Availability |
| Kill-switch is just a fast publish | Operability under fire |
| Ambiguity: fail-open/closed per product | Interview signal |

### 6.3 What you'd say in the last 5 minutes

> “I’d clarify fail-open vs fail-closed and jurisdiction signal first. Then: OLTP rules + immutable signed snapshots, composer with explicit precedence, hybrid push/pull through regional relays, exact tries at the edge, deltas for bandwidth, and a kill-switch path measured in seconds. Bloom is an accelerator, not the legal source of truth. Scale story is fanout and memory—not lookup QPS, which is embarrassingly local.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying ambiguity

**Q1: What’s the first question you’d ask?**  
A: Fail-open vs fail-closed on missing/corrupt data, and whether blocks are global or jurisdiction-scoped.

**Q2: IP block vs user ban?**  
A: Different systems; IP is coarse, shared NAT pain; say so and keep scope.

**Q3: Who is liable for false positives?**  
A: Product + legal; design allow override + audit explainability.

### 7.2 Push vs pull

**Q4: Why not only pull?**  
A: Poll interval fights emergency SLO; thundering herd on version bump.

**Q5: Why not only push?**  
A: Lost messages, edges down, need reconcile.

**Q6: How do you avoid notify storms?**  
A: Relays, coalescing, version watermarks, jittered pull.

### 7.3 Bloom vs exact

**Q7: When is Bloom OK?**  
A: Soft security signals / prefilter with exact verify; not sole legal deny.

**Q8: What’s FPP math?**  
A: `m = -n ln(p) / (ln2)^2` bits; show you can size it—then reject Bloom-only.

**Q9: Roaring bitmaps?**  
A: Great for IPv4 set ops in composer; edges may still want tries for LPM.

### 7.4 Longest prefix match

**Q10: How do you match CIDRs efficiently?**  
A: Patricia/ART/LC-trie; LPM; separate allow/deny or unified with action flags.

**Q11: IPv6 scale?**  
A: Harder cardinality; hierarchical aggregation; product sharding.

### 7.5 Conflict resolution

**Q12: Two denies different severity?**  
A: Higher severity / source rank; document.

**Q13: Court order vs noisy feed?**  
A: Source rank; dual-control for demoting court sources.

**Q14: Overlapping scopes?**  
A: Evaluate stream for request’s jurisdiction; don’t apply foreign rules.

### 7.6 Consistency & versions

**Q15: Do all edges flip at once?**  
A: No; version fencing; brief mixed versions OK if monotonic and audited.

**Q16: CAP here?**  
A: Prefer availability of last-good enforcement under partition; control plane CP for version CAS.

**Q17: Merkle trees?**  
A: Shard integrity + partial re-fetch; audit of snapshot contents.

### 7.7 Distribution & LB

**Q18: How do regional relays help?**  
A: Reduce origin fanout from O(edges) to O(regions) then O(edges/region).

**Q19: CDN for snapshot blobs?**  
A: Yes for bytes; version authority still centralized/signed.

**Q20: Consistent hashing of edges?**  
A: Not for lookup (all edges need relevant sets); maybe for sharded set ownership in multi-tenant huge sets.

### 7.8 Memory & storage

**Q21: Edge memory budget exceeded?**  
A: Split streams by product; compress; aggregate CIDRs; spill cold regions.

**Q22: Where do rules live?**  
A: SQL for CRUD; object store for snapshots; not one without the other.

**Q23: Why not Redis as SoT?**  
A: Weak legal audit story; memory cost; easier to lose durability narrative.

### 7.9 Safety & kill-switch

**Q24: Design kill-switch?**  
A: Tiny signed delta; priority channel; pre-authorized roles; drill regularly.

**Q25: Poison `0.0.0.0/0`?**  
A: Policy reject or dual-control; canary; max-impact threshold.

**Q26: Compromised publisher?**  
A: Offline keys in HSM; dual signatures optional; rapid key revoke + rollback.

### 7.10 Algorithms

**Q27: Diff algorithm for deltas?**  
A: Ordered CIDR list diff; or roaring AND/OR/XOR for IPv4; patch instructions add/remove prefix.

**Q28: GC of expired rules?**  
A: Composer omits expired; async tombstone compaction in SQL.

**Q29: How to explain a deny?**  
A: Store rule_id annotations in leaf or sidecar explain index for audit tool (not necessarily on packet path).

### 7.11 Multi-region control plane

**Q30: Active-active composers?**  
A: Risk of version conflict—use single elected primary per stream or Spanner-serialized version.

**Q31: Cross-region RPO for rules?**  
A: Sync DB replication; publishes pause if quorum lost.

### 7.12 Interview craft

**Q32: How to open?**  
A: Clarify enforcement points, SLO, jurisdiction, fail mode, FP tolerance—then APIs + snapshot model.

**Q33: Numbers that matter?**  
A: Rules count, snapshot size, POP count, propagation p99, lookup QPS (local), fanout GB.

**Q34: Common trap?**  
A: Designing a fancy DB and forgetting edge atomic swap + signature verify.

**Q35: Google-y flavor without claiming internals?**  
A: “Versioned configs, staged rollouts, regional relays, signed artifacts”—not “I know Borg’s IP tables.”

---

### Appendix A — Precedence cheatsheet

```text
1. Scope filter (product, jurisdiction)
2. ALLOW match (LPM among allows)
3. Else DENY match (LPM among denies)
4. Else default allow
```

### Appendix B — Snapshot header

```text
version, parent_version, product, region, epoch,
format_v, fail_mode, merkle_root, sig, created_at,
rule_count, compressed_size
```

### Appendix C — Delta format sketch

```text
DELTA vN-1 -> vN
  ADD deny 203.0.113.0/24 scope=US source=feed_a
  REM deny 198.51.100.0/24
  ADD allow 203.0.113.10/32 scope=US ticket=FP-123
```

### Appendix D — Propagation SLO monitor

```text
lag_edge = now - snapshot[version].created_at
alert if p99(lag_edge where healthy) > SLO
exclude drained/canary-broken edges with reason
```

### Appendix E — Progressive scale table

| Scale | Publish | Edge structure | Control plane |
|-------|---------|----------------|---------------|
| Baseline | Full + rare | Single trie | 1 composer |
| 10× | Delta primary | Trie + optional Bloom accel | Relays |
| 100× | Sharded delta | Per-product tries | Regional relays + shard composers |
| 1,000× | Streaming epochs | Memory-budgeted shards | Cell control planes |

### Appendix F — Worked fanout numbers

```text
Full 50MB × 2K edges = 100 GB
Delta 100KB × 2K = 200 MB  (500× better)
Emergency kill 1KB × 2K = 2 MB
```

### Appendix G — Fail mode decision card

| Question | If yes → |
|----------|----------|
| Wrongful allow catastrophic? | Fail-closed |
| Wrongful deny catastrophic (outage)? | Fail-open or last-good |
| Legal mandate to block? | Fail-closed for that stream |

### Appendix H — Feed importer pipeline

```text
fetch -> validate schema -> normalize CIDRs ->
diff vs prior -> quarantine huge deltas ->
write rules (idempotent) -> audit -> trigger compose
```

### Appendix I — Edge apply pseudocode

```text
on_notify(v):
  if v <= current: return
  blob = fetch(v)
  verify_sig_merkle(blob)
  idx = build_tries(blob)          # off request path
  atomic_store(&active, idx)
  current = v
  ack(v)
```

### Appendix J — NFR card

```text
Propagation p99 ≤ 60s (baseline)
Emergency kill ≤ 15s
Lookup p99 < 50µs in-process
Exact deny/allow (no Bloom-only)
Signed snapshots; monotonic versions
Allow > deny; audit every mutation
```

### Appendix K — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just push iptables via SSH” | Not auditable/SLO-friendly at POP scale |
| “Bloom filter CDN style” | Legal FP risk |
| “Redis pubsub globally” | Need persistence, signatures, relays |
| “Strongly consistent every edge” | Unnecessary; monotonic versions enough |

### Appendix L — Related systems

| System | Relation |
|--------|----------|
| WAF | Consumer of IP sets |
| DDoS scrubbing | Separate; may share feeds |
| Certificate / binary propagation | Similar signed artifact pattern |
| Feature flag systems | Similar versioned rollout |

### Appendix M — Non-goals

- Deep packet inspection  
- Perfect instant global atomic flip  
- Auto-parsing arbitrary court PDFs  
- Replacing IAM / user-level bans  

### Appendix N — IPv4-mapped IPv6 normalization

```text
::ffff:a.b.c.d → treat as IPv4 a.b.c.d for match
store canonical form in rules
```

### Appendix O — Dual-control for dangerous rules

```text
if impact_score(cidr, scopes) > threshold:
  require second approver
  canary_mandatory = true
```

### Appendix P — Explainability query

```text
Input: ip, time, region, product
Find snapshot active at time
Return matching allow/deny rule_ids + sources + tickets
```

### Appendix Q — Memory budget worksheet

```text
bytes ≈ C * num_prefixes * ptr_bytes  (trie dependent)
budget_per_enforcer = 512 MB
if estimate > 0.5 * budget: shard by product or aggregate
```

### Appendix R — Security threat model

| Threat | Mitigation |
|--------|------------|
| Malicious snapshot | Signatures + canary |
| Compromised edge | Limited to local traffic; can’t mint global versions |
| Feed poisoning | Quarantine, rank, dual-control |
| Insider bad publish | Audit + dual-control + rollback |

### Appendix S — 30s scale narrative

> Baseline: SQL rules, signed full snapshots, push to hundreds of POPs, exact tries. 10× forces deltas and relays. 100× shards streams and snapshot segments. 1,000× regionalizes control planes and treats edge RAM as the scarce resource—lookups were never the hard part.

### Appendix T — Glossary

| Term | Meaning |
|------|---------|
| LPM | Longest prefix match |
| Snapshot | Immutable signed enforcement set |
| Kill-switch | Priority publish disabling a set/source |
| Relay | Regional fanout node |
| Fail-open | On error, do not block |
| Fail-closed | On error, block / deny |

### Appendix U — Interview whiteboard order

1. Requirements + fail mode + SLO  
2. Domain model + precedence  
3. Composer + object store + version service  
4. Relay fanout + edge atomic swap  
5. Numbers: size, fanout, memory  
6. Kill-switch + audit  
7. 10×/100×/1000×  

### Appendix V — Sample API errors

| Code | When |
|------|------|
| 400 | Invalid CIDR |
| 409 | Version CAS conflict |
| 413 | Delta/ruleset too large without shard |
| 422 | Blast-radius guard triggered |
| 503 | Composer primary missing |

---

*End of Global IP-Blocking Platform system design.*
