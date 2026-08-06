#!/usr/bin/env python3
"""Generate thorough system-design markdown docs for Fundamentals bank."""
from __future__ import annotations
import json, argparse, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "_manifest.json").read_text())

# Domain packs inject problem-family-specific depth
DOMAIN_HINTS = {
    "01-core-primitives": {
        "focus": "IDs · consistency · sharding · caching · coordination · durability",
        "hot_paths": ["control-plane API", "data-plane hot path", "metadata store", "cache tier", "async workers"],
        "deal_breakers": ["single leader without failover", "unbounded in-memory state", "no idempotency", "cross-region sync on critical path"],
        "algos": ["consistent hashing", "token bucket / sliding window", "quorum R+W>N", "lease/fencing tokens", "Bloom filters"],
    },
    "02-data-platforms": {
        "focus": "ingestion · schema · exactly-once · warehouse/lakehouse · query · lineage",
        "hot_paths": ["ingest gateway", "streaming log", "batch/stream processors", "catalog/metastore", "query engine"],
        "deal_breakers": ["unbounded reprocessing without checkpoints", "no schema registry", "monolithic warehouse for interactive+ETL", "missing late-data policy"],
        "algos": ["watermarking", "HyperLogLog / Count-Min", "LSM/columnar formats", "partition pruning", "consistent snapshot isolation"],
    },
    "03-social-collaboration": {
        "focus": "fanout · ranking · realtime · presence · CRDT/OT · notifications",
        "hot_paths": ["write API", "fanout/timeline workers", "websocket gateway", "graph/store", "notification pipeline"],
        "deal_breakers": ["fanout-on-write for celebrity without hybrid", "strong ordering globally when unnecessary", "CRDT without tombstone GC"],
        "algos": ["push/pull hybrid fanout", "OT/CRDT", "graph BFS sampling", "score ranking", "ring buffers for live chat"],
    },
    "04-media-content": {
        "focus": "upload · transcoding · CDN · ABR · recommendations · moderation",
        "hot_paths": ["upload ingress", "transcode farm", "origin/CDN", "manifest/playlist", "ranking service"],
        "deal_breakers": ["serving originals without ladder", "no CDN", "sync moderation blocking upload forever"],
        "algos": ["ABR ladder", "consistent hashing for cache", "perceptual hash", "embedding ANN", "token bucket for encoding slots"],
    },
    "05-maps-marketplaces-logistics": {
        "focus": "geo · matching · inventory · live location · pricing · dispatch",
        "hot_paths": ["location ingest", "geo index", "matcher/dispatcher", "inventory/booking", "ETA service"],
        "deal_breakers": ["global lock for seats", "polling all drivers", "no idempotent booking", "stale location as truth"],
        "algos": ["geohash/S2", "KD-tree / R-tree", "Hungarian/auction matching", "A*/contraction hierarchies", "inventory overbooking controls"],
    },
    "06-ecommerce-advertising": {
        "focus": "catalog · cart · checkout · inventory · ads auction · attribution",
        "hot_paths": ["product read path", "cart/checkout", "inventory reservation", "ad decisioning", "click/impression pipeline"],
        "deal_breakers": ["oversell without reservation", "auction >100ms RTB budget", "click stream in OLTP"],
        "algos": ["optimistic inventory", "second-price/GSP", "bloom for freq cap", "sharded counters", "outbox pattern"],
    },
    "07-payments-fintech": {
        "focus": "ledger · idempotency · reconciliation · risk · settlement",
        "hot_paths": ["payment API", "orchestrator", "ledger", "processor adapters", "webhook/outbox"],
        "deal_breakers": ["mutable balances without journal", "no idempotency keys", "dual-write without outbox", "FX without holds"],
        "algos": ["double-entry", "saga/state machine", "fencing", "deterministic matching engine", "HLL for fraud features"],
    },
    "08-enterprise-saas": {
        "focus": "tenancy · identity · RBAC/ABAC · audit · workflows · integrations",
        "hot_paths": ["authN/authZ", "tenant router", "workflow engine", "audit log", "integration/webhook workers"],
        "deal_breakers": ["shared DB without tenant isolation", "check permissions only in UI", "mutable audit log"],
        "algos": ["policy evaluation", "hierarchical ACLs", "outbox", "cursor pagination", "SCIM sync"],
    },
    "09-observability-reliability": {
        "focus": "metrics · logs · traces · alerting · DR · security ops",
        "hot_paths": ["agents/collectors", "ingest pipeline", "TSDB/log index", "alert evaluator", "incident tooling"],
        "deal_breakers": ["cardinality explosion", "sync alert on every sample", "single-region observability for multi-region prod"],
        "algos": ["DDSketch/hdr histograms", "trace sampling", "alert grouping", "consistent hashing shard", "SLO burn-rate"],
    },
    "10-ai-llm-ml": {
        "focus": "inference · RAG · GPU scheduling · gateways · agents · cost/quotas",
        "hot_paths": ["API gateway", "model router", "GPU schedulers", "vector index", "usage/quota"],
        "deal_breakers": ["unbounded context in OLTP", "no token accounting", "shared GPU without isolation", "RAG without ACL filters"],
        "algos": ["ANN (HNSW/IVF)", "KV-cache reuse", "bin-packing GPUs", "speculative decoding", "circuit breakers"],
    },
    "11-devices-iot": {
        "focus": "device identity · telemetry · OTA · offline sync · edge",
        "hot_paths": ["device auth", "telemetry ingest", "command plane", "OTA rollout", "sync engine"],
        "deal_breakers": ["chatty always-on GPS", "OTA without staged rollout/rollback", "unbounded offline queue"],
        "algos": ["exponential backoff", "CRDT/LWW", "Merkle sync", "chunked resumable upload", "geofenced batching"],
    },
    "12-developer-tools-cloud": {
        "focus": "git · CI · artifacts · multi-tenant compute · control planes",
        "hot_paths": ["API/control plane", "job scheduler", "artifact store", "runners/workers", "cache"],
        "deal_breakers": ["untrusted code without sandbox", "monolithic control+data plane", "no remote cache at scale"],
        "algos": ["content-addressed storage", "DAG scheduling", "fair share / DRF", "Merkle trees", "copy-on-write"],
    },
    "13-domain-specific": {
        "focus": "domain workflows · compliance · audit · integrations · correctness",
        "hot_paths": ["domain API", "workflow/state machine", "integration adapters", "audit/compliance", "notification"],
        "deal_breakers": ["skip audit for PHI/PII", "no legal hold", "strong consistency everywhere when workflow async suffices"],
        "algos": ["state machines", "outbox", "temporal workflows", "evidence hashing", "calendar/interval indexes"],
    },
    "14-lld-machine-coding": {
        "focus": "concurrency · data structures · durability · API contracts · tests",
        "hot_paths": ["public API", "in-memory structures", "persistence/WAL optional", "background maintenance"],
        "deal_breakers": ["data races", "unbounded memory", "blocking GC on hot path", "lost updates without versioning"],
        "algos": ["LRU/LFU", "token bucket", "ring buffer", "skip lists / B+trees", "lock striping"],
    },
}


def slug_words(title: str) -> str:
    return title


def scale_table(kind: str) -> str:
    if "lld" in kind or "14-" in kind:
        return """| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ops/sec (single process) | 100K | 1M | need sharding / multi-process | distributed service |
| Working set | 1 GB | 10 GB | 100 GB | spill / shard |
| p99 latency | <1ms | <1–2ms | depends on remote | network-bound |
| Concurrent clients | 100 | 1K | 10K | 100K |

**Jumps:** 10× = tune structures + pooling; 100× = multi-process / shard keys; 1,000× = turn component into a networked service with the same invariants."""
    return """| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 1M | 10M | 100M | 1B |
| Peak QPS (read) | 10K | 100K | 1M | 10M |
| Peak QPS (write) | 1K | 10K | 100K | 1M |
| Stored entities | 100M | 1B | 10B | 100B |
| Avg payload | 2–10 KB | same | may grow | may grow |
| Hot-key concentration | top 0.1% → 20% traffic | worse | must isolate | cell + edge |
| Multi-region | single region + DR | active-passive | read replicas global | cell architecture |

**What each jump forces:**
- **10×:** caching, read replicas, async non-critical paths, connection pooling.
- **100×:** shard by tenant/entity key, separate control vs data plane, queue-based backpressure, CDN/edge where applicable.
- **1,000×:** cells / regional single-writer, hot-key isolation, tiered storage, strict SLOs + load shedding, multi-tenant fairness."""


def estimate_block(title: str, section_id: str) -> str:
    return f"""### 2.1 Traffic

```text
Assume baseline peak read QPS R, write QPS W for "{title}".
Peak factor ≈ 10–15× average daily rate.

Example (tune in interview with interviewer numbers):
  Writes: 1K peak → ~86M writes/day if sustained (usually far spikier)
  Reads:  10K peak → mostly cache/CDN if read-heavy
```

Split **write classes** (do not lump):
1. Synchronous user-facing durable writes
2. Cache / session / ephemeral updates
3. Async pipeline / analytics events
4. Compaction / GC / repair traffic (can dominate if misdesigned)

### 2.2 Storage

```text
entities × avg_size × replication_factor × (1 + index_overhead)
Index overhead often 30–100% depending on secondary indexes.
Replication RF=3 → 3× raw; with EC (e.g. 6+3) ~1.5× for cold blobs.
```

### 2.3 Memory & cache

| Tier | What | Size heuristic | TTL / invalidation |
|------|------|----------------|--------------------|
| L1 process | hot keys / computed views | tens–hundreds MB/node | short + explicit invalidate |
| L2 Redis/Memcached | session, popular entities | 10–20% of hot working set | TTL + version bump |
| L3 CDN/edge | public immutable/mutable-with-purge | workload-specific | purge on update |
| Negative cache | misses / 404s | small | short TTL to avoid stampede |

### 2.4 Bandwidth & fanout

```text
egress ≈ QPS × avg_response_size
fanout amplification: 1 user action → N downstream writes/reads
If fanout N > 100, must batch, async, or hybrid push/pull.
```

### 2.5 Capacity sketch

```text
App nodes ≈ peak_QPS / per_node_QPS × (1 + headroom 0.5)
Per-node QPS depends on handler cost (CPU-bound vs IO-bound).
Stateful stores sized by working set + growth + compaction headroom (often 50% free).
```

Section family `{section_id}` emphasizes: {DOMAIN_HINTS.get(section_id, {}).get('focus', 'correctness and scale')}.
"""


def hld_block(title: str, section_id: str, slug: str) -> str:
    d = DOMAIN_HINTS.get(section_id, DOMAIN_HINTS["01-core-primitives"])
    comps = "\n".join(f"- **{c}**" for c in d["hot_paths"])
    deals = "\n".join(f"- {x}" for x in d["deal_breakers"])
    algos = ", ".join(d["algos"])
    return f"""### 3.1 Recommended architecture (default interview answer)

Client → API Gateway / LB → **Stateless service tier** → primary stores + cache → async log/queue → workers.

Core components for **{title}**:
{comps}

### 3.2 API sketch (illustrative)

```text
POST   /v1/resources              # create (Idempotency-Key)
GET    /v1/resources/{{id}}         # read
PATCH  /v1/resources/{{id}}         # conditional update (If-Match / version)
DELETE /v1/resources/{{id}}         # soft delete + async purge
GET    /v1/resources?cursor=...   # stable pagination
POST   /v1/admin/recompute        # control-plane / backfill (authz)
```

Return typed errors: `400` validation, `401/403` authz, `404`, `409` conflict, `429` rate limit, `503` with retry-after.

### 3.3 Data model (logical)

```text
Resource {{
  id, tenant_id, ...domain fields...,
  version, created_at, updated_at, deleted_at
}}
Event / Outbox {{
  id, aggregate_id, type, payload, created_at, published_at
}}
IdempotencyRecord {{
  key, request_hash, response_code, response_body_ref, expires_at
}}
```

Physical choices (pick with trade-offs):
| Need | Prefer | Avoid when |
|------|--------|------------|
| Relational invariants | Postgres / Spanner-class | ultra-high write append-only logs |
| Massive append | Kafka / object storage | point updates with secondary indexes |
| Low-latency KV | Redis / Dynamo-style | multi-row transactions across keys |
| Analytics | Columnar lakehouse | OLTP dual-purpose |

### 3.4 Key design choices & trade-offs

| Option A | Option B | Choose A when | Choose B when | Deal-breaker |
|----------|----------|---------------|---------------|--------------|
| Sync write path | Async + eventually consistent read | User must see durable ack | Throughput / fanout dominates | Lying about durability |
| Strong consistency | Eventual / CRDT | Money, inventory, authz | Presence, counters, feeds | Ignoring conflict types |
| Shard by tenant | Shard by entity | Noisy-neighbor isolation | Even key distribution | Hot tenant without cell limits |
| Cache-aside | Write-through | Read-heavy, tolerable stale | Need simpler consistency | Stampede without locking/singleflight |

**Algorithms / structures likely discussed:** {algos}

### 3.5 Deal-breakers for this problem family
{deals}

### 3.6 Why not the obvious alternatives?

- **Single SQL database forever:** fine to baseline; fails when write QPS, connection count, or working set exceeds vertical scale — plan shard key early even if you delay sharding.
- **“Just use Kafka for everything”:** great for async decoupling; poor as a query store or request/response bus for interactive UX.
- **Global immediate consistency:** expensive and often unnecessary; prefer single-writer home cell / entity ownership.
"""


def diagram(slug: str, title: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9]", "", slug)[:20] or "Sys"
    return f"""```mermaid
flowchart LR
  Client[Clients / SDKs] --> Edge[Edge / CDN / DNS]
  Edge --> GW[API Gateway / LB]
  GW --> Svc[Stateless {safe} Service]
  Svc --> Cache[(Cache Redis)]
  Svc --> DB[(Primary Store)]
  Svc --> Q[Log / Queue]
  Q --> W[Async Workers]
  W --> DB
  W --> Search[(Search / Analytics)]
  Svc --> Obj[(Object Storage)]
  Admin[Control Plane / Config] --> Svc
  Obs[Metrics Logs Traces] -.-> Svc
  Obs -.-> W
```

**Read path:** Client → Edge → Gateway → Service → Cache hit return; miss → primary store → populate cache.

**Write path:** validate → idempotency → durable write (DB and/or log) → ack → async projectors update caches/search/analytics.
"""


def deep_dive(title: str, section_id: str) -> str:
    d = DOMAIN_HINTS.get(section_id, DOMAIN_HINTS["01-core-primitives"])
    return f"""### 5.1 Reliability

**Durability / no silent data loss**
- Persist before ACK for user-visible commits; use fsync / quorum as required by SLO.
- Outbox or dual-write avoidance: write state + event atomically (same TX or log-first).
- Idempotency keys on all creating side effects; replay-safe consumers.

**Retries, timeouts, circuit breaking**
- Bounded retries with exponential backoff + jitter; never retry non-idempotent without key.
- Per-dependency budgets (timeouts); fail fast with degraded mode.
- Circuit breakers / bulkheads isolate noisy dependencies.

**Rate limiting & backpressure**
- Gateway token bucket per tenant/API; load shed non-critical traffic first.
- Queue lag SLOs; stop accepting or spill to cold path when lag exceeds threshold.
- Slow-consumer disconnect policies for streams.

**Failure modes checklist for {title}**
| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Primary DB down | health + error rate | failover / promote replica; degrade writes |
| Cache storm | latency + origin QPS | singleflight, request coalescing, stale-while-revalidate |
| Poison message | consumer retry count | DLQ + quarantine + alert |
| Partial deploy bug | canary SLO burn | automatic rollback |
| Region loss | synthetic probes | DR runbook; RPO/RTO explicit |

**Consistency statement to say out loud:** define read-after-write scope (session/home cell) vs global eventual for secondary views.

### 5.2 Scalability

**Horizontal scale**
- Stateless services: HPA on CPU/RPS/concurrency.
- Stateful: shard by explicit key (tenant_id / entity_id / geo cell); avoid auto-magic opaque sharding without reshard plan.

**Elastic traffic**
- Autoscale with cooldown; pre-warm for known events (launches, games, sales).
- Queue buffering absorbs spikes; do not require sync path to absorb 100×.

**Storage growth**
- Tier hot/warm/cold; TTL/lifecycle; compaction budgets.
- Partition by time for event/log data; by hash for entity data.

**Parallelization**
- Partitioned consumers; map-reduce / DAG for batch; scatter-gather with careful fan-in limits.
- Key algorithms: {', '.join(d['algos'])}

**Multi-tenant fairness**
- Per-tenant quotas, weighted fair queues, noisy-neighbor isolation (separate pools/cells for whales).

### 5.3 Maintainability

**Operability**
- Golden signals + RED/USE; exemplar traces on error paths.
- Config/feature flags for kill-switches; schema migrations expand/contract.
- Runbooks for top failure modes; game-days for failover.

**Evolution**
- Versioned APIs; additive schema changes; dual-publish during migrations.
- Clear ownership boundaries (control plane vs data plane).

**Security & compliance hooks**
- Authn/z on every call; audit critical mutations; encryption in transit/rest; PII minimization / retention jobs.
"""


def wrap_up(title: str) -> str:
    return f"""### Phased delivery

| Phase | Ship | Prove |
|-------|------|-------|
| MVP | Core happy path + durable store + authz + basic metrics | Load test baseline; chaos of dependency timeout |
| Scale 10× | Cache, async offload, replicas | p99 & error budgets under 10× |
| Scale 100× | Sharding / cells, queues, tiering | Reshard drill; backpressure test |
| Scale 1,000× | Multi-region strategy, hot-key isolation, strict multi-tenant fairness | Region failure game day |

### Decisions to restate in the last 2 minutes

1. **Invariants** for {title} (what must never break).
2. **Consistency / durability** choice and why.
3. **Bottleneck** at 100× and the scale-out lever.
4. **Degradation mode** under overload.
5. **Observability** that proves it works in production.

### Explicit non-goals recalled
Keep deferred items deferred unless interviewer expands scope.
"""


def deeper_qs(title: str, section_id: str) -> str:
    d = DOMAIN_HINTS.get(section_id, DOMAIN_HINTS["01-core-primitives"])
    algos = d["algos"]
    qs = [
        ("How do you shard, and how do you reshard without downtime?",
         "Pick a stable high-cardinality key; use consistent hashing or range shards with a directory; dual-write or rewind consumers during migration; verify with shadow reads."),
        ("Cache invalidation strategy?",
         "Versioned keys or explicit delete on write; short TTL as safety; singleflight for stampede; never infinite TTL without pubsub invalidation."),
        ("How do you guarantee idempotency?",
         "Client Idempotency-Key stored with request hash; same key+body → same result; conflict on body mismatch; TTL the records."),
        ("What is your consistency model?",
         "State the primary’s model (linearizable / snapshot / eventual) and which reads are allowed stale; home-cell single-writer for cross-region."),
        ("Hot key / thundering herd?",
         "Key splitting, local caching, coalescing, separate isolation pool, probabilistic early expiration."),
        ("How do you prevent data loss?",
         "Quorum/fsync policy matching RPO; ack only after durability; replayable log; backups + restore drills."),
        ("Backpressure design?",
         "Bounded queues, 429/503 with Retry-After, shed lowest priority, protective admission control at gateway."),
        ("Multi-region story?",
         "Active-passive vs active-active; conflict domain; RPO/RTO numbers; avoid multi-writer unless CRDT/merge defined."),
        ("Observability must-haves?",
         "Latency histograms, saturation, dependency errors, lag, business SLIs; trace critical path; cardinality-safe labels."),
        ("Security threats?",
         "Authz IDOR, injection, abuse/DDoS, secret leakage, poisoned payloads; rate limits + WAF + least privilege."),
        ("Why this store vs alternative?",
         "Map access pattern (point vs range vs append vs analytical) to engine; call out transaction and latency needs."),
        ("Pagination correctness?",
         "Seek/cursor on stable sort key + id; avoid OFFSET at deep pages; define deletion behavior."),
        ("Exactly-once?",
         "Clarify effectively-once via idempotent consumers + transactional outbox/EOS; true exactly-once is end-to-end rare."),
        ("Capacity planning method?",
         "Back-of-envelope → load test → headroom; track bytes/op and CPU/op; forecast from growth curves."),
        ("Failure injection you’d run?",
         "Kill primary, partition network, slow disk, poison message, clock skew, region DNS fail."),
        (f"Which algorithms apply to {title}?",
         f"Expect discussion of: {', '.join(algos)}. Explain complexity and failure modes, not just names."),
        ("Memory vs disk trade-off?",
         "Hot working set in RAM; cold on disk/object store; quantify hit rate needed for latency SLO."),
        ("How do you do migrations?",
         "Expand/contract schema; dual-read/dual-write; backfill with checkpoints; feature-flag cutover."),
        ("Fairness across tenants?",
         "Quotas, weighted fair queuing, separate noisy neighbors, per-tenant max concurrency."),
        ("Cost knobs?",
         "Retention, replication/EC, cache size, index count, overprovision vs spot/preemptible workers."),
        ("Load balancer / consistent hashing details?",
         "L4 vs L7; sticky sessions avoided if possible; consistent hash with virtual nodes for cache/data planes."),
        ("Indexing strategy?",
         "Primary key access first; secondary indexes cost write amp; covering indexes for hot queries; avoid over-indexing."),
        ("GC / compaction / TTL?",
         "Background workers with rate limits; measure write amp; ensure deletes meet privacy SLO including CDN/search."),
        ("How would you estimate p99 under contention?",
         "Include lock/queue wait, GC, slow dependency tails; use histogram math not averages."),
        ("What breaks at celebrity/hot-shard scale?",
         "Single partition CPU, lock contention, fanout blowups; mitigate with hybrid strategies and isolation."),
        ("Client disconnect / retry semantics?",
         "Safe retries + idempotency; distinguish cancel vs detach; document at-least-once delivery to clients."),
        ("Data model anti-patterns?",
         "Unbounded arrays in rows, cross-shard transactions as default, storing large blobs in OLTP."),
        ("How do you test correctness?",
         "Property tests, Jepsen-style under partitions for consensus pieces, contract tests for APIs, load + fault tests."),
        ("When do you introduce a queue?",
         "When work can be async, needs buffering, or fanout; not for request/response latency paths without UX change."),
        ("What’s your rollback story?",
         "Canary on SLO burn; irreversible data migrations avoided or forward-fixed; feature flags for logic rollback."),
    ]
    lines = ["| # | Question | Strong answer direction |", "|---|----------|-------------------------|"]
    for i, (q, a) in enumerate(qs, 1):
        lines.append(f"| {i} | {q} | {a} |")
    return "\n".join(lines)


def functional_rows(title: str) -> str:
    rows = [
        ("Who are the users / clients?", f"End users, internal services, or both for {title}", "Authn model, SLAs, multi-tenant vs single-tenant"),
        ("What is the core write?", "Create/update of primary entity or event", "Durability + idempotency requirements"),
        ("What is the core read?", "Point read, search, stream, or dashboard", "Cache vs query engine choice"),
        ("Sync vs async UX?", "User waits for durable ack; heavy work async", "Queue + status resource"),
        ("AuthZ model?", "User/tenant/roles; optional public links", "Enforce on server; list vs get rules"),
        ("Retention / deletion?", "TTL + user delete + legal hold exceptions", "GC across DB/cache/search/object store"),
        ("Admin / control plane?", "Config, kill switches, rebalance, backfill", "Separate from data plane; audit"),
        ("Abuse / limits?", "Rate limits + quotas + anomaly detection", "Gateway enforcement + per-tenant fairness"),
        ("Consistency expectations?", "Read-your-writes for owner; eventual for projections", "Home cell / primary ownership"),
        ("Offline / mobile?", "Maybe; define sync if yes", "Conflict policy if offline writes"),
        ("Analytics needed?", "Often approximate / async OK", "Do not block OLTP on warehouse"),
        ("Multi-region?", "DR first; active-active only if required", "Conflict domains explicit"),
    ]
    out = ["| # | Question to ask | Expected / typical answer | Design implication |",
           "|---|-----------------|---------------------------|--------------------|"]
    for i, (q, a, imp) in enumerate(rows, 1):
        out.append(f"| F{i} | {q} | {a} | {imp} |")
    return "\n".join(out)


def nfr_rows() -> str:
    rows = [
        ("Latency", "Interactive if user-facing", "p50/p99 targets; separate slow paths"),
        ("Availability", "Tier-1 vs tier-2", "99.9%–99.99%; multi-AZ minimum"),
        ("Durability / RPO", "No loss of acked writes", "Quorum/WAL; RPO=0 or seconds"),
        ("RTO", "Minutes for region", "Failover runbook tested"),
        ("Consistency", "As above", "Document per API"),
        ("Throughput", "Baseline→1000×", "Shard + async"),
        ("Cost", "Efficient at hit rate", "Tiered storage; avoid over-index"),
        ("Security", "TLS, authz, encryption at rest", "Threat model in wrap-up"),
        ("Privacy", "Retention + delete SLO", "Cross-store purge"),
        ("Operability", "Dashboards + alerts + tracing", "Golden signals day 1"),
    ]
    out = ["| # | Question | Expected answer | Target |",
           "|---|----------|-----------------|--------|"]
    for i, (q, a, t) in enumerate(rows, 1):
        out.append(f"| N{i} | {q} | {a} | {t} |")
    return "\n".join(out)


def cases_block(title: str) -> str:
    return f"""**Happy paths**
1. Authenticated client performs primary create → durable ack → subsequent read sees result (read-your-writes).
2. Read-heavy path served from cache/CDN with correct TTL/invalidation.
3. Async projection updates search/analytics without blocking user ack.
4. Delete/TTL removes data from primary and secondary indexes within privacy SLO.
5. Admin kill-switch / config change rolls out safely.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate client retry | Idempotency returns original result |
| Hot key | Isolate / split / cache coalescing |
| Dependency timeout | Bounded wait; degrade or fail fast; no infinite queue for interactive |
| Partial worker failure | At-least-once + idempotent handlers; DLQ |
| Clock skew | Prefer monotonic server time / logical tokens for ordering where needed |
| Poison payload | Validate; quarantine; do not block partition forever |
| Overload | 429/503 + shed; protect durables |
| Security abuse | Rate limit + authz deny + audit |
| Regional outage | Failover per stated RPO/RTO |
| Schema change mid-flight | Versioned consumers; compatible evolution |

Domain note: tailor 2–3 cases specifically to **{title}** in the interview (the table above is the baseline set).
"""


def generate_one(m: dict) -> str:
    title = m["title"]
    slug = m["slug"]
    section_id = m["section_id"]
    section_title = m["section_title"]
    d = DOMAIN_HINTS.get(section_id, DOMAIN_HINTS["01-core-primitives"])
    focus = d["focus"]
    is_lld = section_id.startswith("14-")

    body = f"""# System Design: {title}

> **Focus areas:** {focus}
> **Style:** End-to-end design with progressive scale (10× → 100× → 1,000×)
> **Category:** {section_title}
> **Quality bar:** Interview-passable for senior/staff loops — explicit trade-offs, failure modes, and scale jumps

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

The goal of this phase is to **bound the problem**: what we build, what we defer, and at what scale we must succeed.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Design **{title}** as a production system | A toy single-process demo without failure modes |
| Scope | MVP + progressive scale path | Boiling the ocean of every adjacent product |
| Lens | Correctness, reliability, scalability, operability | Resume-driven buzzword collage |

### 1.1 Functional requirements

{functional_rows(title)}

**MVP functional scope (lock with interviewer):**

1. Core create/read (and critical update/delete) path for {title}.
2. Authn/authz appropriate to sensitivity of the data.
3. Durable storage for acked writes; idempotent creates.
4. Essential async side effects (notifications, projections) if UX requires.
5. Basic rate limits / quotas; metrics and structured logs.
6. Clear delete/TTL behavior if data can expire or users can purge.
7. One explicit degraded mode under dependency failure.

**Out of MVP (explicitly defer):**

- Nice-to-have ML personalization unless that is the problem
- Cross-region active-active with automatic conflict magic
- Full enterprise admin suite
- Perfect global ordering when causal/local ordering suffices
- Exotic multi-cloud unless asked

### 1.2 Non-functional requirements

{nfr_rows()}

### 1.3 Cases (User Flows & Edge Cases)

{cases_block(title)}

### 1.4 Scales (Progressive)

{scale_table(section_id)}

### 1.5 Etc. (Constraints & Assumptions)

Ask and record:

- Cloud vs on-prem? Single cloud multi-AZ default.
- Managed services allowed? Usually yes — discuss interfaces, not brand loyalty.
- Compliance? PII/PHI/PCI as applicable to {title}.
- Team size / time? Design for evolution, not big-bang perfection.
- Read-your-writes required? Default yes for owner reads.

**Scope statement to repeat back:**

> Design **{title}**: MVP correctness and durability first, then a clean path through 10× / 100× / 1,000× with explicit trade-offs on consistency, caching, sharding, and failure modes. Defer adjacent products unless requested.

---

## 2. Back-of-the-Envelope Estimation

{estimate_block(title, section_id)}

---

## 3. High-Level Design

{hld_block(title, section_id, slug)}

### 3.7 Detailed component responsibilities

| Component | Responsibility | State | Scale lever |
|-----------|----------------|-------|-------------|
| Gateway / LB | TLS, auth, rate limit, routing | Stateless | Horizontal |
| Service | Business logic, validation, orchestration | Stateless | Horizontal |
| Primary store | Source of truth | Stateful | Shard / vertical → cells |
| Cache | Hot read acceleration | Ephemeral | Horizontal + hash |
| Queue/Log | Async decoupling, replay | Stateful | Partition |
| Workers | Projections, GC, notifications | Mostly stateless | Consumer lag based |
| Object storage | Blobs / cold | Stateful | Unlimited bytes |
| Observability | Metrics/logs/traces | — | Separate failure domain |

{"### 3.8 LLD emphasis (machine-coding style)" if is_lld else "### 3.8 Control plane vs data plane"}

{
'''For LLD interviews, also specify:
- Thread-safety / lock ordering
- Memory bounds and eviction
- Persistence surface (if any) and crash recovery
- Public interface + complexity guarantees
- Unit + concurrency tests
''' if is_lld else '''Keep control-plane mutations (config, topology, ACLs) away from the ultra-hot data path.
Cache config with version numbers; watch/long-poll or push updates; fail closed or open explicitly.
'''
}

---

## 4. Architecture Diagram

{diagram(slug, title)}

### 4.1 Sequence (write)

```mermaid
sequenceDiagram
  participant C as Client
  participant G as Gateway
  participant S as Service
  participant D as Primary Store
  participant Q as Queue
  C->>G: POST + Idempotency-Key
  G->>S: forward
  S->>D: begin TX / durable write
  S->>D: outbox event
  D-->>S: commit
  S-->>C: 200 + resource
  S->>Q: publish (or relay from outbox)
```

---

## 5. Design Deep Dive

{deep_dive(title, section_id)}

### 5.4 Problem-specific deep notes for {title}

- Name the **single hardest invariant** (e.g., no double-spend, no lost ack, no oversell, no cross-tenant leak).
- Name the **hottest key** pattern and mitigation.
- Name the **secondary index / projection** lag and UX expectations.
- Name **one number** you will track in the interview (QPS, GB/day, fanout N, p99).

### 5.5 Storage & indexing cheatsheet

| Access pattern | Structure | Notes |
|----------------|-----------|-------|
| Point get by id | KV / PK | Cache friendly |
| Time-ordered feed | (user_id, ts, id) | Cursor pagination |
| Geo near-me | geohash/S2 + filter | Tune cell size |
| Full-text | inverted index | Async index |
| Graph 1-hop | adjacency lists | Shard by node |
| Append log | segmented log | Retention + compact |

---

## 6. Wrap-Up

{wrap_up(title)}

---

## 7. Deeper / Related Interview Questions

{deeper_qs(title, section_id)}

### 7.1 Quick algorithms / data structures drill

Expect to whiteboard or verbally justify structures relevant to **{title}**: {', '.join(d['algos'])}.

### 7.2 Numbers to memorize for interviews

| Rule of thumb | Value |
|---------------|-------|
| RTT same AZ | ~0.5–2ms |
| RTT cross-region | ~50–150ms |
| Disk sequential vs random | orders of magnitude difference |
| NIC 25–100Gbps | bandwidth ceiling per host |
| Redis simple GET | ~100K–1M ops/s/node class (order-of) |
| Postgres single primary write | often low-K to tens of K QPS before creative scaling |
| Kafka partition | throughput scales with partitions; ordering per partition |

---

*Category: {section_title} · Slug: `{slug}` · Use this as a living checklist; customize numbers with the interviewer.*
"""
    return body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-missing", action="store_true")
    ap.add_argument("--section", action="append", default=[])
    ap.add_argument("--slugs", action="append", default=[])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--min-lines", type=int, default=0, help="regenerate if fewer lines")
    args = ap.parse_args()

    written = 0
    skipped = 0
    for m in MANIFEST:
        if args.section and m["section_id"] not in args.section:
            continue
        if args.slugs and m["slug"] not in args.slugs:
            continue
        path = Path(m["path"])
        if path.exists() and not args.force:
            n = sum(1 for _ in open(path))
            if args.only_missing:
                skipped += 1
                continue
            if args.min_lines and n >= args.min_lines:
                skipped += 1
                continue
            if not args.min_lines:
                skipped += 1
                continue
        path.write_text(generate_one(m))
        written += 1
    print(f"written={written} skipped={skipped}")


if __name__ == "__main__":
    main()
