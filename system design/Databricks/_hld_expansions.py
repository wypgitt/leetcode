"""Domain-specific HLD expansions — real architecture depth, no filler."""

EXPANSIONS: dict[str, str] = {}


def _register(slug: str, content: str) -> None:
    EXPANSIONS[slug] = content.strip()


_register(
    "online-bookstore",
    """
### 5.8 Checkout saga (reserve → pay → fulfill)

```text
States: CART_VALIDATED → INVENTORY_RESERVED → PAYMENT_AUTHORIZED → PAYMENT_CAPTURED → FULFILLING → SHIPPED

Reserve (per SKU, conditional):
  UPDATE inventory SET available = available - qty, version = version + 1
  WHERE sku = ? AND warehouse = ? AND available >= qty AND version = ?

Payment uncertainty:
  if capture response unknown → inquiry by (order_id) idempotency key
  never double-capture with new key

Release path:
  reservation TTL 15m; sweeper returns stock; order → EXPIRED
```

**Deal-breaker:** decrement inventory only in cache; oversell under race.

### 5.9 Flash-sale hot SKU

| Technique | Purpose |
|-----------|---------|
| Per-SKU queue at checkout | Serialize reserves on one row |
| Split inventory across virtual pools | Reduce single-row contention |
| Early "join waitlist" | Shed load before payment path |
| CDN for static PDP | Keep reads off OLTP |

### 5.10 Search vs catalog consistency

CDC from `products`/`inventory` → OpenSearch. PDP reads **Postgres SoT** for price/stock badge; search may lag minutes. Checkout always revalidates inventory from SoT — never trust search index for purchase decision.

### 5.11 Multi-region (Phase 2)

| Plane | Mode |
|-------|------|
| Catalog/browse | Active-active + CDN |
| Cart | Home region per user_id |
| Orders/inventory writes | **Home cell** per customer or warehouse region |
| Payment | PSP region constraints |

### 5.12 Failure modes table

| Failure | Mitigation | User-visible |
|---------|------------|--------------|
| Reserve fails (OOS) | Abort checkout | OUT_OF_STOCK |
| Pay timeout | PENDING_PAYMENT + inquiry job | "Processing" |
| Crash after reserve | Resume pay or release | Retry safe |
| Search down | Browse via DB SKU lookup | Degraded search |
| Hot SKU lock timeout | Queue + retry | Wait or try later |

### 5.13 Sequence: checkout with idempotency

```text
Client          Checkout           Inventory        Payment
  |--checkout-->|                  |                |
  |             |--reserve SKU---->|                |
  |             |<-OK--------------|                |
  |             |--auth/capture------------------->|
  |             |<-OK------------------------------|
  |             |--commit reserve->|                |
  |<-order_id---|                  |                |
  | (retry)     |--idem hit------>|                |
  |<-same order-|                  |                |
```
""",
)

_register(
    "bookstore-pricing-api",
    """
### 5.8 Batch orchestration internals

```text
POST /v1/prices { isbns: [..100] }

Phase 1 — partition request:
  hits = []
  misses = []
  for isbn in isbns:
    e = cache.get(isbn)
    if e && fresh: hits.append(e)
    else: misses.append(isbn)

Phase 2 — dedupe misses:
  unique_misses = distinct(misses)

Phase 3 — coalesced fetch:
  for isbn in unique_misses:
    coalescer.do(isbn, () => fetch_with_deadline(isbn, remaining_budget))

Phase 4 — assemble per-item status:
  OK | STALE(retrieved_at) | UNAVAILABLE | INVALID_ISBN
```

**Never block entire batch** on one slow ISBN — per-item deadline within overall batch budget.

### 5.9 Upstream amplification control

Same playbook as book-price-aggregator: tier sellers, feed snapshots, singleflight, negative cache for unknown ISBNs (short TTL).

### 5.10 SLA tiers

| Tier | Max staleness | Rate limit |
|------|---------------|------------|
| Standard | 120s | 200 QPS |
| Premium | 30s | 2K QPS |
| Enterprise | 10s + webhook | Custom |

### 5.11 Rate limiting & fairness

Token bucket per `api_key`; cost = `len(isbns)`; 429 with `Retry-After`. Shuffle-shard limiter keys to avoid Redis hot spot on one enterprise key.

### 5.12 Failure modes

| Case | Behavior |
|------|----------|
| Partner 5xx | ISBN → UNAVAILABLE; others OK |
| Partner slow | Timeout; partial batch |
| Cache partition | Bypass cache; admission control |
| Duplicate batch retry | Optional request-hash idempotency cache |

### 5.13 Comparison to fan-out aggregator

| Dimension | Pricing API | Price aggregator |
|-----------|-------------|------------------|
| Interaction | Read batch | Quote + optional buy |
| Amplification | Batch coalesce | Fan-out to N sellers |
| Money path | None | Saga + payment |
| Freshness | Labeled staleness OK | Revalidate on buy |
""",
)

_register(
    "batch-streaming-ingestion",
    """
### 5.8 Unified batch + streaming model

```text
Sources:
  Batch: S3 landing, DB snapshots, hourly files
  Stream: Kafka/Kinesis, CDC, webhooks

Bronze landing:
  Autoloader / structured streaming reads with schema inference + evolution
  Checkpoint offsets in durable store (DBFS/S3 checkpoint path)

Silver:
  Deduplicate by key + merge (SCD Type 1/2 per table policy)
  Data quality expectations (null rate, range checks) → quarantine DLQ

Gold:
  Aggregations, marts; scheduled or triggered by silver commit
```

### 5.9 Checkpointing & effectively-once

```text
Micro-batch N:
  read offsets [start, end)
  transform → staging files
  commit table version V+1 (Delta/Iceberg OCC)
  if commit OK: checkpoint = end
  else: retry batch (idempotent sink by batch_id)
```

**Deal-breaker:** advance checkpoint before durable sink commit → data loss on crash.

### 5.10 Schema evolution

| Change | Handling |
|--------|----------|
| Add column | Merge schema; null default |
| Rename | Metadata migration + compat reader |
| Breaking type | New table version; dual-write window |

Schema registry optional; enforce on write in silver layer.

### 5.11 Backpressure & recovery

| Signal | Action |
|--------|--------|
| Consumer lag ↑ | Autoscale executors |
| Sink commit conflicts ↑ | Reduce concurrent writers; partition table |
| DLQ depth ↑ | Alert; pause bad source partition |
| Cluster preemption | Checkpoint resume from last committed offset |

### 5.12 Medallion file layout

```text
s3://lake/bronze/source/yyyy/mm/dd/hour/part-*.parquet
s3://lake/silver/domain/table/  (_delta_log commits)
s3://lake/gold/mart/table/
```

Target file size 128MB–1GB; avoid millions of small files (compaction job).

### 5.13 Cost controls

Spot/preemptible workers with checkpoint; auto-terminate idle clusters; Z-order/hilbert on hot filter columns; tier cold bronze to IA/Glacier after N days.

### 5.14 Progressive scale

**1×:** Single workspace, micro-batch streaming + daily batch jobs, Delta commits.

**10×:** Separate ingest vs transform clusters; partition by source; schema registry.

**100×:** Multi-workspace cells; shuffle service; job queues with fair share.

**1000×:** Global catalog federation; aggregate metadata tier; cross-region read replicas with home writer per table.
""",
)

_register(
    "stock-trading-platform",
    """
### 5.8 Matching engine (per symbol shard)

```text
Single writer thread / process per symbol — in-memory order book:
  bids: max-heap by price, then time
  asks: min-heap by price, then time

Match rule: price-time priority (default US equities)

Order types MVP: LIMIT, MARKET, IOC, FOK
```

**Deal-breaker:** distributed lock on book without single-writer — latency and correctness collapse.

### 5.9 Order book structure

```text
PriceLevel { price, queue of OrderNode FIFO }
OrderNode { order_id, remaining_qty, timestamp }

Trade event: { symbol, price, qty, buy_order_id, sell_order_id, ts }
Append to immutable audit log before ACK to participant
```

### 5.10 Market data fan-out

Matching engine publishes trades + top-of-book deltas to market data service → WebSocket/UDP multicast to subscribers. Separate read scale from write path.

### 5.11 Regulatory audit

Append-only **event log** (WORM storage): every order, cancel, modify, trade with microsecond timestamps and sequence numbers. Replay reconstructs book state for dispute investigation.

### 5.12 Settlement hooks

End-of-day: net positions per account → clearing/settlement file to DTCC-like counterparty. Platform does not hold cash in MVP — integrate ledger service.

### 5.13 Failure modes

| Failure | Behavior |
|---------|----------|
| Matcher crash | Recover book from snapshot + event replay |
| Duplicate order | Idempotent client_order_id |
| Market halt | Reject new orders; cancel open per policy |
| Fat finger price | Risk checks pre-match (price bands) |

### 5.14 Latency budget (HFT vs retail)

Retail MVP: p99 match < 10ms in-process. HFT colocated microsecond path is different product — be honest about scope.

### 5.15 Sequence: limit order match

```text
Broker API → Risk → Order Router (by symbol) → Matcher shard
  → book.add(order)
  → while crossable: emit Trade events
  → ACK order state OPEN/PARTIAL/FILLED
  → async publish to market data + audit log
```
""",
)

_register(
    "hierarchical-filesystem",
    """
### 5.8 Inode / dentry model

```text
Inode { id, type=file|dir, size, permissions, owner, timestamps, data_ptrs }
Dentry { parent_inode, name, child_inode_id }  UNIQUE(parent, name)

File data: chunk/block IDs (see distributed FS) or inline for tiny files
```

### 5.9 Path resolution

```text
resolve("/a/b/c"):
  inode = root
  for component in ["a","b","c"]:
    dentry = metadata.lookup(inode, component)
    if not dentry: ENOENT
    inode = dentry.child
  return inode
```

Path cache: `(parent_id, name) → child_id` with version invalidation on rename/delete.

### 5.10 Atomic rename

```text
rename("/a/old", "/b/new"):
  TX:
    validate no cycle if directory
    unlink existing /b/new if exists (policy: replace or fail)
    update dentry parent+name atomically
    bump directory version counters
  commit
```

**Deal-breaker:** copy-delete rename for large trees on every rename — use metadata-only pointer update.

### 5.11 Hard links vs symlinks

Hard link: multiple dentries → same inode; refcount on inode. Symlink: inode type LINK storing target path; resolve with loop detection (max depth).

### 5.12 Locking

| Op | Lock granularity |
|----|------------------|
| Read file | Shared on inode or range |
| Write | Exclusive on file or byte range lease |
| Rename dir | Exclusive on source parent + target parent (ordered to prevent deadlock) |

### 5.13 POSIX subset MVP

Support: create, read, write, mkdir, readdir, rename, unlink, stat. Defer: full ACL, advisory locks across nodes, mmap coherence.

### 5.14 Scale

Shard metadata by **parent inode hash** or **path prefix** (e.g. /home/user_id). Hot directory (single folder with millions of files) → hash subdirectories `{inode_id % 1000}/`.

### 5.15 Failure modes

| Failure | Mitigation |
|---------|------------|
| Metadata leader loss | Failover replica; fencing epoch |
| Orphan inode | GC scan link count |
| Split brain writer | Lease + fencing on metadata TX |
""",
)

_register(
    "chat-partitioned-cache",
    """
### 5.8 Partition assignment

```text
channel_id → partition = consistent_hash(channel_id) mod P

Each cache partition owns channel_id range:
  recent_messages[channel_id] → ring buffer of last K messages
  message_by_id[message_id] → entry (secondary index)
```

Client reads route to partition owner via gateway directory or embedded hash.

### 5.9 Read path

```text
GET history(channel_id, after_seq):
  p = partition(channel_id)
  if local: serve from ring buffer if seq range covered
  else: forward to owner partition
  on miss: backfill from durable channel log → populate cache
```

### 5.10 Invalidation on send/delete

```text
On MESSAGE or DELETE event:
  owner partition updates ring + id index
  publish invalidation {channel_id, message_id, seq} to bus
  peer partitions drop stale entries if replicated
```

**Deal-breaker:** TTL-only eviction without delete events — deleted bodies reappear until expiry.

### 5.11 Consistency vs latency

| Mode | Guarantee | Cost |
|------|-----------|------|
| Strong per channel | All reads via owner | Higher RTT cross-partition |
| Eventual replicated | Async replicate ring | Stale window ms–s |

MVP: **owner authoritative**; optional async replica for read scaling with version check.

### 5.12 Hot channel

Celebrity channel on one partition → vertical scale partition; split **read replicas**; still single writer for mutations routed to owner.

### 5.13 Memory sizing

```text
P partitions, 1M hot channels, K=100 msgs, 500B avg
1M × 100 × 500B ≈ 50GB cluster-wide ÷ P per node
```

Eviction: LRU across cold channels within partition; never evict without checking durable log tail.

### 5.14 Fan-out interaction

Cache accelerates **history pull**; realtime push bypasses cache for online users but write-through updates cache on send.

### 5.15 Failure modes

| Failure | Mitigation |
|---------|------------|
| Partition node crash | Rebuild from Kafka/log; temporary miss → backfill |
| Missed invalidation | Read-through checks seq + deleted flag from SoT |
| Rebalance | Consistent hash with virtual nodes; gradual migration |
""",
)

_register(
    "digital-game-store",
    """
### 5.8 Purchase → entitlement saga

```text
States: CREATED → PAID → ENTITLED → COMPLETED | REFUNDED

1. Create order with idempotency_key
2. Charge payment (integer cents)
3. Grant entitlement row (user_id, game_id, license_type)
4. Emit receipt + optional Steam-key assignment

Crash after pay: resume grant; if grant fails → refund
```

### 5.9 Entitlement SoT

```text
entitlements(user_id, game_id, granted_at, source_order_id, revoked_at)
UNIQUE(user_id, game_id) where revoked_at IS NULL
```

Download authorization checks entitlement + not revoked + not chargeback-frozen.

### 5.10 Download authorization

```text
GET /download/{game_id}:
  assert entitlement valid
  mint signed URL (CloudFront/S3 presign) TTL 15m
  log download event for fraud analytics
```

**Deal-breaker:** long-lived unsigned download URLs — piracy redistribution.

### 5.11 DRM / license keys (Phase 2)

Optional third-party key pool; assign atomically `UPDATE keys SET used=true WHERE id=? AND used=false`. Out of MVP: full client attestation.

### 5.12 Refunds

Revoke entitlement (`revoked_at=now`); invalidate active sessions on next heartbeat; payment refund via PSP idempotent API.

### 5.13 Catalog vs ownership

Catalog in CDN/DB; user library = join entitlements × catalog metadata. Search indexes public catalog only.

### 5.14 Fraud hooks

Velocity limits on purchases; geo mismatch; payment risk score; block entitlement grant pending review for high-risk.

### 5.15 Progressive scale

**1×:** Monolith + Postgres entitlements + S3 assets + payment saga.

**10×:** Shard entitlements by user_id; CDN for downloads; async receipt email.

**100×:** Regional asset edge; entitlement cache with version; anti-fraud service.

**1000×:** Cells by region; geo-restricted SKUs; separate read path for library.
""",
)

_register(
    "collaborative-playlist-editor",
    """
### 5.8 OT vs CRDT choice

| Approach | Pros | Cons |
|----------|------|------|
| OT (server seq) | Simple total order | Server bottleneck |
| CRDT (RGA/LSEQ) | Offline merge | Metadata overhead |
| Last-write-wins | Easy | Loses concurrent edits |

**MVP:** Server-assigned **version + op log**; clients submit ops; server total-orders; clients transform against concurrent ops (OT-lite).

### 5.9 Operation types

```text
InsertTrack { op_id, after_track_id, track_id, client_ts }
DeleteTrack { op_id, track_id }
MoveTrack   { op_id, track_id, after_track_id }
UpdateMeta  { title, ... }
```

Each op: `(playlist_id, server_seq)` unique; idempotent by `op_id`.

### 5.10 Real-time sync

WebSocket room per playlist; server broadcasts op after durable append. Offline clients fetch `ops since seq` on reconnect and apply.

### 5.11 Presence

Ephemeral presence (who's editing) in Redis; not durable. Cursor/selection optional.

### 5.12 Conflict example

```text
User A inserts track X after T1
User B inserts track Y after T1 (concurrent)
Server orders: seq 10 (A), seq 11 (B)
Result order: T1, X, Y — both preserved (not LWW)
```

### 5.13 Snapshot + compaction

Periodic snapshot of track list + compact op log > seq S to control storage. Replay ops after snapshot on cold start.

### 5.14 Permissions

Owner/editor/viewer roles; ops rejected if viewer. Share link read-only.

### 5.15 Failure modes

| Failure | Mitigation |
|---------|------------|
| Duplicate op retry | Idempotent op_id |
| Server crash | Recover seq from durable log |
| Divergent clients | Resync from snapshot+ops |
""",
)

_register(
    "kv-store-qps-api",
    """
### 5.8 Service architecture

```text
API tier (stateless):
  GET/PUT/DELETE /v1/kv/{key}
  GET /v1/metrics/qps?key=&window=

Storage tier:
  Sharded KV (Redis Cluster / Dynamo-style) — key → home shard

Metrics tier:
  Each storage node emits op events → stream aggregator → sliding window counters
```

### 5.9 QPS metrics API

```text
Per-key sliding window (see kv-sliding-window-qps LLD):
  windows: 1s, 1m, 5m
  approximate at scale via count-min sketch + exact for hot keys

GET /metrics/qps?key=foo&window=60s
  → { key, window, qps, samples, as_of_ts }
```

**Clarify:** metrics are **eventually consistent** few-second lag OK for observability; not billing-grade without stronger path.

### 5.10 Sharding

```text
shard = hash(key) mod N
home shard owns writes; optional read replicas with RYW stickiness
```

Hot key mitigation: read replicas; client-side cache; split logical key namespace.

### 5.11 Durability tiers

| Tier | Durability | Latency |
|------|------------|---------|
| Cache | Optional TTL | ms |
| Standard | Async replicate | ms |
| Durable | Sync quorum | higher |

MVP: single durable tier with RF=3.

### 5.12 Rate limiting self-use

Protect metrics query path — aggregating hot key metrics can itself become hot. Pre-aggregate per shard; merge at query coordinator.

### 5.13 Idempotency

PUT with `Idempotency-Key` header for exactly-once **effect** per key scope within TTL.

### 5.14 Comparison to LLD

Interview may pivot to **single-node sliding window** implementation — HLD service view hands off to `kv-sliding-window-qps-lld-system-design.md`.

### 5.15 Failure modes

| Failure | Mitigation |
|---------|------------|
| Shard loss | Failover replica; RPO per replication mode |
| Metrics lag spike | Backpressure metrics queries; approximate mode |
| Thundering herd on popular key | Coalesce reads; local agent cache on storage node |
""",
)

_register(
    "kafka-like-message-queue",
    """
### 5.7 Leader election deep dive

```text
KRaft (modern): metadata quorum elects partition leaders; brokers vote; no ZooKeeper
On broker failure: controller detects; elect new leader from ISR; producers refresh metadata

unclean.leader.election.enable=false:
  if no ISR available → partition offline (prefer availability trade vs data loss)
```

### 5.8 Consumer rebalance cooperative protocol

```text
Revoke partitions → commit offsets → assign new partitions → resume fetch
Sticky assignor minimizes movement; cooperative avoids stop-the-world
Session timeout > processing time + heartbeat interval
```

### 5.9 Idempotent producer

```text
Producer ID (PID) + sequence per partition
Broker dedupes within session window
Enables safe retries without duplicate records in log
```

### 5.10 Dead-letter pattern

```text
process record:
  try N times
  on failure: produce to topic.DLQ with headers {original_topic, offset, error}
main consumer commits offset after DLQ handoff (policy: skip poison)
```

### 5.11 Tiered storage (1000×)

Sealed segments migrate to S3; fetch path reads local cache → object store; retention effectively unlimited with cost trade.

### 5.12 Monitoring checklist

| Metric | Alert |
|--------|-------|
| under_replicated_partitions | > 0 sustained |
| consumer_lag | SLO breach |
| isr_shrinks_rate | broker/network issues |
| request_queue_size | overload |
""",
)

_register(
    "visa-payment-routing",
    """
### 5.6 Stand-in processing

When issuer link down, policy may allow **stand-in** approval up to floor limit using issuer-stored limits cache — high risk; document explicitly. MVP: decline unless issuer contract mandates stand-in with strict caps.

### 5.7 Settlement pipeline

```text
Hourly/daily:
  collect CAPTURED txns → net by merchant/issuer → generate clearing files
  idempotent file ingestion on both sides
  reconciliation job matches auth ↔ capture ↔ settlement
```

### 5.8 Chargeback hook

Chargeback event links to original `txn_id`; adjust merchant settlement; optional ledger integration (see Stripe ledger doc).

### 5.9 Multi-region active-passive

Auth writes **home region** per merchant or txn_id; failover promotes secondary; fence old epoch; replay in-flight UNKNOWN txns.

### 5.10 ISO8583 vs JSON adapters

Plugin `IssuerAdapter` interface; map internal `AuthorizationRequest` to wire format; record raw message hash for disputes (not PAN).

### 5.11 Load test scenarios

| Scenario | Expect |
|----------|--------|
| Issuer 2s latency | Timeouts; circuit; no thread exhaustion |
| Duplicate auth retry | Idempotent same response |
| BIN table switch mid-day | Versioned routing; no mixed routes per txn |
""",
)

_register(
    "group-chat-global-deletion",
    """
### 5.8 Delete visibility SLO measurement

```text
delete_visibility_lag = client_receive_delete_ts - delete_durable_ts
Track p50/p99 for online members; offline bounded by next sync duration
```

### 5.9 Concurrent send/delete formal invariant

For all clients C, after applying all ops with seq ≤ S:
  if ∃ DELETE op D for message M with D.seq = s:
    ∀ C: display(M) shows tombstone/empty

Prove by induction on seq application order.

### 5.10 Search index pipeline

```text
message_event stream → indexer
on DELETE: update doc deleted=true; remove body field
search query filters deleted=true
lag SLA: e.g. 60s — product may show deleted msg briefly in search
```

### 5.11 Backup/restore

Restore must include delete tombstones; otherwise bodies resurrect — run post-restore scrub job comparing delete log.

### 5.12 Large group delete fan-out

Delete event still O(1) write to channel log; push only to online subset; offline pull on sync — **no O(members) writes** at delete time in MVP.
""",
)

_register(
    "stock-order-manager",
    """
### 5.8 Timer wheel implementation sketch

```text
Wheel bucket = expire_at // bucket_ms
On tick(bucket):
  for order in bucket:
    if order.state in (OPEN, PARTIAL):
      enqueue venue cancel
      transition → EXPIRED or CANCEL_PENDING

On restart: rebuild buckets from index scan expire_at < now+horizon
```

### 5.9 Venue gateway pool

Persistent connections per venue; rate limit per account; circuit breaker on venue errors. Separate **order entry** from **execution report** stream (async).

### 5.10 Position / buying power (sketch)

Pre-trade risk: check buying_power ≥ order notional; hold buying_power on accept; release on cancel/fill. Integrate with portfolio service — out of MVP depth unless asked.

### 5.11 Query vs command path

Commands: place/cancel → write shard. Queries: open orders → read model or shard read with session stickiness. CQRS optional at scale.

### 5.12 Regulatory audit trail

```text
order_events(order_id, seq, event_type, payload_json, ts)
Immutable append; includes client requests, venue acks, state transitions
```

### 5.13 Market open load

Stagger timer firing across buckets; pre-warm venue sessions; admission control at API gateway per account rate.

### 5.14 Testing matrix

| Test | Expected |
|------|----------|
| Duplicate place | Same order_id |
| Cancel then late fill | Reconcile to filled + alert |
| Expire while cancel in flight | Terminal state single; venue inquiry |
| Crash after CANCEL_PENDING | Resume venue cancel |
""",
)


def get_expansion(slug: str) -> str:
    return EXPANSIONS.get(slug, "")


# Section 7 bulk Q&A — real answers to reach depth without filler
QA_BULK: dict[str, list[tuple[str, str]]] = {
    "batch-streaming-ingestion": [
        ("Batch vs streaming unified how?", "Same code path via micro-batch or structured streaming; bronze landing identical; silver/gold merge logic shared."),
        ("Exactly-once to Delta?", "Idempotent sink: write files then commit version; checkpoint after commit; batch_id dedupe on retry."),
        ("Schema drift from source?", "Schema inference + evolution rules; quarantine malformed rows to DLQ with raw payload."),
        ("Autoloader vs custom Kafka consumer?", "Autoloader handles file notification/ordering; Kafka consumer for queue sources; both checkpoint offsets."),
        ("Small file problem?", "Compaction/coalesce job targets 128MB–1GB; OPTIMIZE/ZORDER on hot tables at 100×."),
        ("Backpressure when sink slow?", "Increase lag; autoscale executors; pause upstream ingest if lag > SLO; never unbounded heap."),
        ("Multi-tenant noisy neighbor?", "Per-workspace quotas; fair share job queues; separate clusters for batch vs streaming SLA tiers."),
        ("GDPR delete in lakehouse?", "Delete commands in table format + rewrite files or deletion vectors; propagate to downstream marts."),
        ("Compare Delta vs Iceberg?", "Both use object storage + transaction log; discuss commit protocol, catalog integration, vendor neutrality."),
        ("Failure: executor dies mid-task?", "Scheduler retries task on another executor from lineage; idempotent stage output paths."),
    ],
    "stock-trading-platform": [
        ("Single writer per symbol why?", "Order book in-memory with microsecond updates; lock-free within thread; cross-process needs single owner."),
        ("Market order vs limit?", "Market crosses immediately at best price; limit rests on book until price match or cancel."),
        ("How publish market data?", "Matcher emits trade/top-of-book events to fanout service; UDP/WebSocket to subscribers; separate from order path."),
        ("Regulatory audit?", "Append-only immutable event log with microsecond timestamps; replay reconstructs book state."),
        ("Pre-trade risk checks?", "Price bands, max order size, buying power — sync before matcher accepts."),
        ("Halt trading?", "Reject new orders; cancel open per policy; drain matcher queue."),
        ("Fractional shares?", "Support in order qty type; matcher handles decimal qty with policy rounding."),
        ("After-hours vs regular?", "Separate books or session tags on orders; matcher filters by session."),
        ("Settlement integration?", "EOD net positions file to clearing; platform ledger hooks."),
        ("Scale beyond one matcher box?", "Shard symbols; hot symbols dedicated process; never split one symbol across matchers."),
    ],
    "hierarchical-filesystem": [
        ("Rename atomicity implementation?", "Single metadata TX updating dentry; no copy for metadata-only rename."),
        ("Path traversal attack?", "Reject .. components; resolve from root with permission check each step."),
        ("Directory with millions of files?", "Hash subdirectories; readdir paginated; avoid single directory inode hotspot."),
        ("Hard link limit?", "Inode refcount; cannot hard link directories typically."),
        ("Symlink loops?", "Max resolve depth; detect cycle."),
        ("POSIX close-to-open consistency?", "MVP: session consistency; mention NFS-style cache invalidation as hard problem."),
        ("Distributed metadata leader?", "Raft/Paxos on metadata; data nodes separate."),
        ("Quota enforcement?", "Inode/project quota counters updated on create/write."),
    ],
    "chat-partitioned-cache": [
        ("Why partition cache by channel?", "Locality for hot channels; bounded memory per node; parallel invalidation."),
        ("Consistent hash virtual nodes?", "Reduce imbalance when nodes added/removed; gradual key migration."),
        ("Cache miss after send?", "Write-through on send path; read backfill from durable log."),
        ("Cross-partition read?", "Forward to owner or proxy; client sticky to partition optional."),
        ("Celebrity channel?", "Owner partition vertical scale; read replicas with version check."),
        ("Compare to Redis single cluster?", "Partition affinity reduces cross-talk; explicit channel→node mapping."),
    ],
    "digital-game-store": [
        ("Entitlement vs license key?", "Entitlement is SoT row; key pool optional second step for DRM platforms."),
        ("Family sharing?", "Phase 2: entitlement group; policy engine on download."),
        ("Regional pricing?", "SKU per region; payment in local currency integer minor units."),
        ("Chargeback?", "Revoke entitlement; flag account; webhook from PSP."),
        ("Download CDN?", "Signed short TTL URL; bind to user session optional."),
        ("Free weekend promotion?", "Time-bounded entitlement with expires_at; sweeper job."),
    ],
    "collaborative-playlist-editor": [
        ("OT vs CRDT for playlists?", "OT with server seq simpler for interview; CRDT for offline-first product."),
        ("Delete track concurrent with move?", "Total order on server resolves; both ops preserved in op log."),
        ("Compaction of op log?", "Snapshot track list + truncate ops before snapshot seq."),
        ("Spotify-scale playlist 10k tracks?", "Paginated load; ops only for edits; snapshot delta sync."),
    ],
    "kv-store-qps-api": [
        ("QPS metric accuracy?", "Eventually consistent aggregates; exact for hot keys on owning shard."),
        ("Sliding window at scale?", "Per-shard local counters roll up; see LLD for single-node window."),
        ("Hot key on metrics?", "Pre-aggregate; rate limit metrics API for single key queries."),
        ("Strong consistency for put/get?", "Linearizable within shard via Raft or primary-backup."),
    ],
    "visa-payment-routing": [
        ("Stand-in approval?", "Policy explicit; floor limits; issuer contract; high risk — mention carefully."),
        ("Partial capture?", "Sum captures ≤ auth amount; multiple capture records linked."),
        ("ISO8583 retry?", "Same STAN/RRN for inquiry; never new auth key for same purchase."),
        ("BIN table updates?", "Versioned import; blue/green; metric on routing staleness."),
        ("Cross-border FX?", "Separate FX rate service; settlement currency vs auth currency explicit."),
        ("PCI logging rules?", "Never log PAN; token_id + last4 only."),
    ],
    "kafka-like-message-queue": [
        ("KRaft vs ZooKeeper?", "KRaft embeds metadata quorum in brokers; removes ZK ops burden."),
        ("Consumer stuck processing?", "max.poll.interval.ms exceeded → rebalance; size processing or increase interval."),
        ("Log compaction use case?", "Changelog topics; KV store rebuild from compacted topic."),
        ("MirrorMaker cross-DC?", "Active-passive replication; offset mapping; not active-active same group easily."),
        ("Producer compression?", "lz4/zstd default at scale; CPU vs bandwidth trade."),
    ],
    "group-chat-global-deletion": [
        ("Delete for me vs everyone?", "This doc is global delete; local hide is client-only flag without tombstone fanout."),
        ("Admin delete any message?", "Authorize; same DELETE event path; audit actor."),
        ("E2E encrypted delete?", "Retract message; clients honor; server drops ciphertext."),
        ("Delete latency SLO?", "Measure delete_durable → client_hide; push + invalidation paths."),
    ],
    "stock-order-manager": [
        ("GTD vs GTC?", "GTD has expire_at; GTC until cancel; timer wheel fires on GTD only."),
        ("Cancel rejected by venue?", "Stay OPEN; notify client; user retry cancel."),
        ("Replace order?", "Cancel + new order with new client_order_id; or native replace API if venue supports."),
        ("Buying power hold?", "Reserve notional on accept; release on terminal state."),
    ],
}


def get_bulk_qa(slug: str) -> list[tuple[str, str]]:
    return QA_BULK.get(slug, [])
