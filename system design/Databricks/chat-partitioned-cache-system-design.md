# System Design: Chat with Partitioned Hot Cache

> **Focus areas:** Partitioned hot cache · Channel affinity · Read path · Invalidation · Fan-out · Consistency vs latency · Channel seq · Tombstone deletes  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct cache coherence under send/delete races, honest partition sizing math, clear fan-out vs cache interaction  
> **Interview theme:** Databricks — group chat where recent messages are cached on partition nodes affined to channel ranges

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

Goal: design **real-time group chat** where the **recent message window per channel** lives on a **partitioned hot cache tier** with **channel affinity**—and prove the cache stays coherent under sends, deletes, concurrent races, and fan-out.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Core problem | Partitioned cache for hot channel history | Generic chat without cache story |
| Ordering | Per-channel `channel_seq` (total order) | Global cross-channel order |
| Delete | Delete-for-everyone as tombstone event | Silent row purge only |
| Fan-out | Push to online; cache accelerates pull/sync | Per-recipient message store copies |
| Scale lever | Channel-partitioned cache + durable log | Single Redis for everything |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | 1:1 or group? | **Group chat** primary; 1:1 is a 2-member channel | Membership ACL + fan-out |
| F2 | Max group size? | 50 MVP; 500–5k later | Push vs pull threshold; cache is per-channel not per-user |
| F3 | Send API? | Text MVP; media as object-store pointer Phase 2 | Cache stores metadata + body or pointer |
| F4 | **Ordering?** | **Per-channel total order** for display | Server-assigned monotonic `channel_seq` |
| F5 | History read? | Paginate by seq; recent window must be fast | **Partition cache owns last K messages** |
| F6 | Realtime? | Online members see new messages in seconds | WS push; cache write-through on send |
| F7 | **Delete-for-everyone?** | Author/admin retracts for all members | **Tombstone DELETE op** in channel log + cache invalidation |
| F8 | Delete after read? | Body hidden for everyone; placeholder OK | Scrub body in SoT; cache entry marked DELETED |
| F9 | Offline / multi-device? | Catch-up sync by seq cursor | Pull path hits partition cache or backfills from log |
| F10 | Edit? | Optional; version bump | UPDATE op or delete+replace; invalidate cache entry |
| F11 | Search? | Must not return deleted bodies | Async index on tombstone stream (Phase 2) |
| F12 | Membership changes? | Join/leave affects fan-out not cache key | Cache keyed by `channel_id`, not user |

**MVP functional scope:**

1. Create group channel, join/leave, send text message with idempotent `client_msg_id`.  
2. **Read recent history** (`GET /channels/{id}/history?after_seq=&limit=`) served from **partition cache** when window covered.  
3. Real-time push to online members over WebSocket.  
4. **Delete-for-everyone**: append DELETE event with new `channel_seq`; invalidate cache; push retract.  
5. Concurrent send vs delete resolved by **channel_seq total order**.  
6. Offline device sync: apply ops in seq order including tombstones.  
7. **Partition assignment**: `channel_id → cache partition owner` via consistent hash.

**Out of MVP:** E2E encryption, 100k-member broadcast channels, threads at scale, cross-region active-active writes for same channel.

### 1.2 Non-Functional Requirements

| # | NFR | Target | Notes |
|---|-----|--------|-------|
| N1 | Send ACK latency | p50 < 80ms, p99 < 200ms in-region | Persist + seq before ACK; fan-out async |
| N2 | **History read (hot window)** | p50 < 15ms, p99 < 50ms from partition cache | Miss → backfill once, then hot |
| N3 | Delete visibility (online) | p99 < 1s body hidden | Push + cache invalidation |
| N4 | Durability | RPO ≈ 0 for ACK’d ops | Durable log is SoT; cache is derived |
| N5 | **Cache consistency** | No deleted body served after delete ACK | Owner authoritative; version fencing |
| N6 | Per-channel write order | Linearizable send/delete on channel | Single writer per channel partition |
| N7 | Availability | 99.9% messaging | Degrade cache replica reads; never lose log |
| N8 | Retention | 1 year warm; tombstones retained | Body scrub; seq holes OK |

### 1.3 Cases

**Happy paths**

1. User opens channel → router hits partition owner → ring buffer returns last 50 messages in seq order.  
2. Member sends → sequencer assigns seq → durable log → **write-through to owner cache** → async fan-out push → online clients render.  
3. Author deletes → DELETE tombstone durable with seq N+1 → **cache updates in place** (body null, state DELETED) → invalidation bus → push DELETE event.  
4. Offline client syncs `after_seq=100` → cache or log returns ops 101..120 including tombstone → correct UI.  
5. Idempotent resend of same `client_msg_id` → same `(message_id, seq)` returned.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cache miss (cold channel) | Owner backfills from durable log, populates ring, serves read |
| Delete races in-flight send | Total order via seq: if DELETE seq > SEND seq → final DELETED |
| Delete before send visible to reader | Tombstone buffered; SEND with lower seq applied as DELETED |
| **Stale cache replica** after delete | Read checks `entry.version` vs channel `head_seq`; reject stale body |
| Missed invalidation message | Read-through validates `state` from owner or SoT on mismatch |
| Hot channel on one partition | Vertical scale partition; optional read replicas with fencing |
| Partition node crash | Rebuild ring from log tail; temporary elevated latency |
| Rebalance (add partition) | Consistent hash migration; dual-read during move |
| Large group (2k members) | Fan-out push online only; offline pull from cache/log — **O(1) cache write** |
| Member leaves mid-fanout | Stop future push; history policy: retain or hide per product |
| Clock skew | Never order by client clock; `channel_seq` only |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 1M | 10M | 100M | 1B |
| Active channels | 5M | 50M | 500M | 5B |
| Peak send QPS (global) | 10K | 100K | 1M | 10M |
| Peak history read QPS | 50K | 500K | 5M | 50M |
| Avg group size | 8 | 10 | 12 | 15 |
| **Hot channels in cache** | 1M | 8M | 50M | 200M (sampled/LRU) |
| Cache partitions P | 32 | 128 | 512 | 2,048 |
| Push fan-out deliveries/s | 80K | 800K | 8M | 80M |
| Delete QPS peak | 200 | 2K | 20K | 200K |

**What each jump forces:**

- **10×:** Dedicated cache partition fleet; Kafka channel-events; presence-filtered fan-out.  
- **100×:** Hybrid fan-out (push ≤500 members, pull larger); cache LRU across cold channels; read replicas with version check.  
- **1,000×:** Cell architecture; cold history in object-store segments; streaming fan-out pipeline; partition autoscaling.

### 1.5 Scope repeat-back

> Design group chat with a **durable per-channel sequenced log** as source of truth, a **partitioned hot cache** affined by `channel_id` holding the recent message window, **write-through invalidation on send/delete**, realtime **fan-out decoupled from cache writes**, and **delete-for-everyone as tombstone events** that converge online push and offline sync.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split: ingest vs read vs fan-out

```text
Baseline peak:
  Send (write) QPS:     10,000/s
  History read QPS:     50,000/s   (5× send — scrolling, reconnect, prefetch)
  Delete QPS:             200/s   (~2% of sends)

Do not conflate send QPS with fan-out deliveries:
  Fan-out deliveries ≈ send_qps × avg_group_size × online_fraction
                     ≈ 10,000 × 8 × 0.35 ≈ 28,000 push deliveries/s baseline
```

At **100×**:

```text
Send: 1M/s; Read: 5M/s; Fan-out (with hybrid): ~8M/s push (not 1M×12=12M — pull caps large groups)
Cache must absorb read QPS >> write QPS — this is why partitioned hot cache exists.
```

### 2.2 Cache memory math

**Per-entry size (order of magnitude):**

```text
message_id (16 B) + channel_id (8 B) + sender_id (8 B) + channel_seq (8 B)
+ body (~400 B avg text) + metadata/state (32 B) + version (8 B) ≈ 480 B → round to 500 B
```

**Ring buffer per hot channel:**

```text
K = 100 recent messages per channel (configurable 50–200)
Per-channel cache footprint: K × 500 B = 100 × 500 B = 50 KB

Baseline: 1M hot channels in cache simultaneously
  1,000,000 × 50 KB = 50 GB cluster-wide cache RAM

With indexes (message_id → entry pointer, ~40 B × 100 per channel):
  + 1M × 100 × 40 B ≈ 4 GB
Total ≈ 54 GB (+ ~20% overhead) → ~65 GB baseline cluster
```

**Per partition node (P = 32 partitions, RF = 2 for HA):**

```text
Primary ownership: each node owns 1/P of channels
  Hot channels per primary ≈ 1M / 32 ≈ 31,250 channels
  RAM per primary ≈ 65 GB / 32 ≈ 2 GB (+ indexes) ≈ 2.5 GB per node primary

At 100× with 50M hot channels sampled (not all channels hot):
  50M × 50 KB = 2.5 TB cluster-wide
  P = 512 → ~4.9 GB primary per node (+ replicas)
  → need LRU eviction for cold channels; durable log always backfills
```

**Eviction policy:** LRU by `last_read_ts` or `last_write_ts` within partition; evict whole channel ring, not individual messages (simpler coherence).

### 2.3 Partition sizing math

**Goal:** each partition sustains write + read load without saturating CPU/network.

```text
Channels uniformly hashed to P partitions.
Expected hot channels per partition: H / P
Expected send QPS per partition: S / P
Expected read QPS per partition: R / P

Baseline: S=10K, R=50K, P=32
  Write per partition: 10,000/32 ≈ 312 ops/s
  Read per partition:   50,000/32 ≈ 1,562 ops/s

Single partition node comfortable bound (rule of thumb): ~5K–10K cache reads/s, ~1K writes/s
  → P=32 is comfortable at baseline; monitor hot-spot skew.

Skew: top 0.1% channels may carry 10× average traffic
  celebrity channel on one partition: 100× normal write/read
  Mitigation: dedicated hot partition override, rate limits, read replicas
```

**Choosing P:**

```text
P ≥ max(S / W_max, R / R_max) × safety_factor
  W_max ≈ 800 writes/s/partition (cache write-through + log)
  R_max ≈ 8,000 reads/s/partition

Baseline: max(10000/800, 50000/8000) × 2 = max(12.5, 6.25) × 2 ≈ 25 → P=32 OK
100×: max(1M/800, 5M/8000) × 2 = max(1250, 625) × 2 → P ≥ 2500? 
  In practice use 512 partitions + hot-channel isolation + read replicas, not 2500 tiny nodes
```

### 2.4 Fan-out math (interaction with cache)

```text
Cache write path: O(1) per send — update owner partition ring regardless of group size
Fan-out path:     O(online_members) push deliveries — decoupled async

Baseline:
  10K send/s × 8 members × 35% online ≈ 28K WS deliveries/s
  Payload ~600 B (event frame) → 28,000 × 600 B ≈ 16.8 MB/s egress (manageable)

100× with hybrid (groups > 500 → pull):
  Small groups (90% of sends): 900K/s × 10 × 0.3 ≈ 2.7M push/s
  Large groups (10%): pull on open — 0 push amplification at send time
  Cache still 1M write/s global — partition scaling problem, not fan-out × cache
```

**Key insight for interview:** fan-out does **not** multiply cache entries; cache is **per-channel**. Fan-out multiplies **network deliveries**, not **cache footprint**.

### 2.5 Durable storage (SoT behind cache)

```text
Send rate: 10K/s × 86400 ≈ 864M messages/day
Avg stored record (op log): ~500 B → 864M × 500 B ≈ 432 GB/day
Tombstones: 200 delete/s × 100 B × 86400 ≈ 1.7 GB/day (negligible vs bodies)

1-year retention (with body scrub on delete):
  Roughly 864M × 365 × (500 B × 0.6 after scrub) ≈ 94 TB/year raw
  + replication factor 3 → ~280 TB
  Cache holds only hot window; cold tail in Cassandra/Scylla/object segments
```

### 2.6 Latency budget (history read — cache hit)

```text
Client → API router → partition directory lookup → owner cache node → response
  Edge/API:           5–10 ms
  Directory lookup:   1–3 ms  (cached routing table)
  Cache fetch:        1–5 ms  (in-memory ring scan by seq range)
  Serialize:          2–5 ms
Total p50 target:     ~15 ms in-region

Cache miss (cold channel):
  + log backfill:     20–80 ms (depends on K and store latency)
  + populate ring:    5 ms
Total p99 miss:       ~100 ms acceptable for first open
```

### 2.7 Bottlenecks (ranked)

1. **Hot-spot partitions** — celebrity channel skew on one node.  
2. **Fan-out push storm** — large online groups; not cache, but shared WS gateways.  
3. **Stale cache replica** serving deleted body — coherence bug class.  
4. **Partition rebalance** — migration churn if P changes frequently.  
5. **Sequencer throughput** per hot channel — single-writer limit (~5–20K ops/s).  
6. **Missed invalidation** — must have read-through fence.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| **Channel log (SoT)** | Append-only SEND/DELETE/MEMBERSHIP ops with `channel_seq` | Strong per channel; durable before ACK |
| **Partition cache** | Recent K messages per channel on owner node | Owner authoritative; replicas eventual |
| **Sequencer** | Assign monotonic `channel_seq` per channel | Single writer per channel |
| **Fan-out** | Push events to online member sockets | At-least-once; async |
| **Presence** | Who is online / subscribed | Ephemeral approximate |
| **Routing directory** | `channel_id → partition_id → host` | Eventually consistent; versioned |

**Deal-breaker:** treating cache as SoT without durable log — node loss loses history.

### 3.2 Core abstractions

```text
Channel          { channel_id, member_ids[], created_at, head_seq }
ChannelOp        { channel_id, channel_seq, op_type, message_id, payload, ts }
  op_type ∈ { SEND, DELETE, MEMBER_JOIN, MEMBER_LEAVE, EDIT }

Message          { message_id, sender_id, body, state: ACTIVE|DELETED, send_seq, delete_seq? }
DeleteTombstone  { message_id, delete_seq, deleted_by }   // DELETE op in log

CachePartition   { partition_id, owned_channel_range, ring_buffers{}, msg_index{} }
RingBuffer       channel_id → sorted deque of Message (last K by seq)

PartitionMap     consistent_hash(channel_id) → partition_id
```

### 3.3 Partition assignment

```text
partition_id = consistent_hash(channel_id) mod P

Use virtual nodes (vnodes) per physical host to reduce skew:
  each physical node owns multiple hash ranges on the ring

Directory service (control plane):
  - watches partition membership
  - publishes versioned map: { partition_id → { primary, replicas[], epoch } }
  - routers cache map with TTL; stale map → retry with fresh epoch

Channel affinity guarantees:
  - all cache reads/writes for channel C go to owner(C)
  - sequencer for C may colocate on same host as cache owner (optimization)
  - colocation reduces cross-service RTT on write-through
```

**Rebalance:** add node → steal vnode ranges → **migrate channel rings** in background:

```text
for each migrating channel_id:
  dual-write to old + new partition until caught up
  flip directory epoch
  drain old partition entries after TTL
```

**Deal-breaker:** random load balancer pick among cache nodes — breaks affinity and coherence.

### 3.4 Read path

```text
GET /channels/{channel_id}/history?after_seq=S&limit=L

1. Router: pid = partition_map(channel_id); forward to primary(pid) [or local if gateway colocated]
2. Owner cache:
     if ring covers [S+1, S+L] contiguously:
         return slice from ring (filter state==DELETED → placeholder)
     else:
         MISS → fetch range from ChannelLog (Cassandra/Scylla by channel_id+seq)
         populate ring (merge, trim to K)
         return slice
3. Authz: membership check before any bytes returned (API layer or cache gate)

Pagination: clients pass after_seq cursor; never offset-by-page-number.

Read replica path (optional, 100×):
  - serve reads from replica if entry.version >= requested_min_version
  - on DELETE, owner bumps channel epoch; replicas apply invalidation or pull delta
  - if replica stale (version low): forward to primary or block body
```

**1:1 chat:** identical path — 2-member channel still has one `channel_id`, one partition, one ring.

### 3.5 Write path (send)

```text
POST /channels/{channel_id}/messages { client_msg_id, body }

1. Authz + idempotency check (client_msg_id)
2. Sequencer (per channel single writer):
     channel_seq = allocate_next(channel_id)    // Redis INCR or DB row in TX
3. ChannelLog append SEND op (durable, replicated)
4. ACK to client { message_id, channel_seq }   // after step 3 commit
5. Async side effects (parallel):
     a) Cache owner: write-through — insert into ring + msg_index
     b) Fan-out worker: push MESSAGE event to online members
     c) Search indexer: enqueue (Phase 2)
```

**Ordering invariant:** `channel_seq` assigned **before** ACK; never reuse seq.

### 3.6 Delete-for-everyone (tombstone events)

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| A. UPDATE flag in DB only | Simple | Cache/index/clients miss | Weak |
| B. **DELETE op in log + tombstone** | Offline sync natural; total order | Placeholder UX | **Chosen** |
| C. Physical row purge | Storage savings | Breaks seq; offline resurrect | Reject for MVP |
| D. Cache TTL only | Easy | Deleted body reappears | **Deal-breaker** |

**Delete path:**

```text
DELETE /channels/{channel_id}/messages/{message_id}

1. Authz (sender or admin)
2. Sequencer: delete_seq = allocate_next(channel_id)
3. ChannelLog append DELETE op { message_id, delete_seq, deleted_by }
4. Scrub body in SoT (body=NULL, state=DELETED) in same TX if relational; or tombstone row in log store
5. ACK { delete_seq }
6. Async:
     a) Cache owner: update entry state=DELETED, body=null, version=delete_seq
     b) Publish invalidation { channel_id, message_id, delete_seq } on bus
     c) Fan-out: push DELETE event
```

**Concurrent send/delete formal rule:**

```text
For message M, let S = send_seq, D = delete_seq (if exists).
Client final state after applying all ops through head_seq H:
  if D exists and D <= H: display(M) = tombstone (no body)
  elif S exists and S <= H: display(M) = body (unless D also applied later in order)

Since ops share one total order, apply in channel_seq order:
  last op for M wins — DELETE after SEND hides body; tombstone before SEND suppresses body when SEND arrives.
```

### 3.7 Cache invalidation on send/delete

| Event | Owner partition action | Invalidation bus | Replica action |
|-------|------------------------|------------------|----------------|
| SEND | Insert/overwrite ring slot; bump `head_seq` | Optional `CACHE_UPSERT` (replicas can apply) | Apply upsert or invalidate range |
| DELETE | Mark DELETED in ring + index; bump version | **`INVALIDATE {msg_id, delete_seq}`** | Drop body or apply tombstone |
| EDIT | Update body + version | `INVALIDATE msg_id` or upsert | Same |
| Evict channel (LRU) | Drop ring | none | N/A |

**Principle:** owner is **write-through authoritative**; replicas are **read scaling only** with version fence.

**Read fence (missed invalidation safety net):**

```text
on read(entry):
  if entry.state == DELETED: return tombstone
  if entry.version < channel_head_seq_for_message:  // delete may have landed
      refresh from owner or SoT for that message_id
```

### 3.8 Consistency vs latency trade-offs

| Mode | Read latency | Consistency | When |
|------|--------------|-------------|------|
| **Owner-only reads** | Medium (cross-AZ RTT) | Strong per channel | MVP default |
| Owner write + sync replica | Low local reads | Near-strong if fenced | 10× |
| Async replica + version check | Lowest | Eventual (ms–s stale window) | 100× read-heavy |
| Client-side cache + push | Lowest | Eventual; push fixes | All scales |

**Interview answer:** prefer **owner authoritative** for correctness; add **replicas with seq/version fencing** for scale; never serve body without checking `state` and `version`.

**CAP positioning:** per-channel partition chooses **CP** on writes (durability + order); reads may trade to **AP** on replicas with bounded staleness.

### 3.9 Fan-out interaction with cache

```text
                    +-------- durable SEND/DELETE --------+
                    |                                      |
                    v                                      v
             Cache owner (O(1))                  Fan-out worker (O(online))
                    |                                      |
                    |                                      v
                    |                               WS Gateways → clients
                    v
             History pull served from cache

Online user path:
  - PUSH gives realtime (may arrive before client polls history)
  - Client dedupes by message_id; orders by channel_seq
  - Opening channel uses cache read path (not fan-out)

Offline user path:
  - No fan-out cost at send time
  - Sync API reads cache if hot else log
  - DELETE learned from log/tombstone on sync — cache accelerates but is not required

Delete fan-out:
  - Still O(online) push — but **O(1) cache update** regardless of group size
  - Large group delete does NOT fan-out N cache copies — single ring update
```

**Hybrid fan-out threshold:**

| Group size | Realtime | History |
|------------|----------|---------|
| ≤ 100 | Push all online | Cache |
| 100–500 | Push online; badge bump | Cache |
| > 500 | Push active viewers only; others pull | Cache/log on open |

### 3.10 API sketch

```text
POST   /channels                          create group
POST   /channels/{id}/members             join
POST   /channels/{id}/messages            send (Idempotency-Key: client_msg_id)
DELETE /channels/{id}/messages/{msg_id}   delete-for-everyone
GET    /channels/{id}/history             ?after_seq=&limit=
POST   /sync                              { channel_id, after_seq }  bulk catch-up
WS     subscribe(channel_ids[])           realtime events

WS event types: MESSAGE, DELETE, MEMBER_CHANGE, TYPING (ephemeral)
Event payload always includes: channel_id, channel_seq, message_id, version
```

### 3.11 Storage choices

| Data | Store | Why |
|------|-------|-----|
| Channel log | Cassandra/Scylla `(channel_id, seq)` | Range scan by seq; high write |
| Membership | Postgres / strongly consistent KV | ACL correctness |
| Partition cache | In-memory on affined nodes (+ optional Redis NOT shared across channels) | Hot window latency |
| Partition directory | etcd / ZooKeeper / control DB | Membership changes rare |
| Fan-out bus | Kafka `channel-events` keyed by channel_id | Ordering per channel |
| Presence | Redis TTL | Ephemeral |

**Deal-breaker:** one global Redis hash for all channels without partition affinity — becomes hotspot and coherence nightmare at scale.

### 3.12 Trade-offs summary

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Cache key | `channel_id` affinity | O(1) update per send | Per-user inbox cache of same messages |
| SoT | Append-only channel log | Rebuild cache; offline sync | Cache-only |
| Ordering | Server `channel_seq` | Deterministic delete/send races | Client timestamps |
| Delete | Tombstone DELETE op | Sync + invalidation | Silent purge |
| Fan-out | Async decoupled | Send ACK not blocked | Sync push to 10k sockets in API |
| Coherence | Write-through owner + bus | Fast + safe | TTL-only eviction for deletes |

---

## 4. Architecture Diagram

### 4.1 Component diagram

```text
                         +------------------+
                         | Partition Directory|
                         | (channel → partition)|
                         +--------+---------+
                                  |
 Clients (mobile/web)              |
        |  HTTPS + WSS             |
        v                          v
 +-------------+           +-------------------+
 | API Router  |---------->| Cache Partition   |
 | + Authz     |  history  | Fleet (P nodes)   |
 +------+------+  read     | [primary/replica] |
        |                  |  ring + msg_index |
        | send/delete      +---------+---------+
        v                            ^
 +-------------+                    | write-through
 | Chat Service|                    |
 | (stateless) |----------+---------+
 +------+------+          |
        |                 | invalidate
        v                 v
 +-------------+   +---------------+   +----------------+
 | Sequencer   |   | Invalidation  |   | Channel Log    |
 | per channel |   | Bus (Kafka)   |   | (Cassandra)    |
 +------+------+   +---------------+   +----------------+
        |
        | outbox events
        v
 +-------------+     +------------------+     +----------------+
 | Fan-out     |---->| Presence Service |---->| WS Gateway     |
 | Workers     |     | (online set)     |     | Fleet          |
 +-------------+     +------------------+     +----------------+
```

### 4.2 Sequence: send → cache → fan-out

```text
Client          API/Chat       Sequencer+Log      Cache Owner       Fan-out       WS/GW       Client B
  |                |                |                |               |            |            |
  | POST message   |                |                |               |            |            |
  |--------------->|                |                |               |            |            |
  |                | append SEND    |                |               |            |            |
  |                | seq=105        |                |               |            |            |
  |                |--------------->|                |               |            |            |
  |                |                | write-through  |               |            |            |
  |                |                |--------------->|               |            |            |
  |                |                |                | ring[105]=msg |            |            |
  | 200 {seq:105}  |                |                |               |            |            |
  |<---------------|                |                |               |            |            |
  |                | publish event  |                |               |            |            |
  |                |--------------------------------|---------------->|            |            |
  |                |                |                |               | push MESSAGE|            |
  |                |                |                |               |----------->|            |
  |                |                |                |               |            | event seq=105
  |                |                |                |               |            |----------->|
```

### 4.3 Sequence: delete-for-everyone + cache invalidation

```text
Client A        API/Chat       Log+Seq        Cache Owner      Inv Bus      Fan-out     Client B
  |                |              |               |              |            |            |
  | DELETE msg M   |              |               |              |            |            |
  |--------------->|              |               |              |            |            |
  |                | DELETE seq=106              |              |            |            |
  |                |------------->|               |              |            |            |
  |                |              | tombstone     |              |            |            |
  |                |              |-------------->|              |            |            |
  |                |              |               | state=DELETED|            |            |
  |                |              |               | body=null    |            |            |
  |                |              |               |---publish--->|            |            |
  |                |              |               |              | replicas   |            |
  |                |              |               |              | drop body  |            |
  | 200 {seq:106}  |              |               |              |            |            |
  |<---------------|              |               |              |            |            |
  |                | event DELETE |               |              |            |            |
  |                |-------------------------------------------->|            |            |
  |                |              |               |              |            | push DELETE|
  |                |              |               |              |            |----------->|
  |                |              |               |              |            | B hides body
```

### 4.4 Sequence: history read (cache hit vs miss)

```text
Client          Router         Cache Owner         Channel Log
  |                |                |                    |
  | GET history    |                |                    |
  | after_seq=100  |                |                    |
  |--------------->|                |                    |
  |                | forward(pid)   |                    |
  |                |--------------->|                    |
  |                |                | ring has 101..150? |
  |                |                | YES → return 50 msgs (HIT)
  |                |                |                    |
  |< - - - - - - - - - - - - - - - |                    |
  |                                  |                    |
  | GET after_seq=50 (cold)          |                    |
  |--------------->|--------------->|                    |
  |                |                | MISS               |
  |                |                | fetch 51..100      |
  |                |                |------------------->|
  |                |                | populate ring      |
  |                |                | return slice       |
  |< - - - - - - - - - - - - - - - |                    |
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Durability before ACK:** SEND/DELETE committed in channel log before client success.  
2. **`channel_seq` strictly monotonic** per channel; holes OK, duplicates never.  
3. **Cache is derived:** rebuildable from log tail; loss of cache ≠ loss of messages.  
4. **No deleted body served** after DELETE ACK when read goes through owner or fenced replica.  
5. **Idempotency:** `(channel_id, client_msg_id)` unique for sends; delete idempotent by `message_id`.  
6. **Apply order:** clients and cache merge logic apply ops in `channel_seq` order.  
7. **Fan-out at-least-once:** clients dedupe by `message_id`; DELETE idempotent.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Cache node crash | Rebuild ring from log tail (last K seq); elevated latency until warm |
| Missed invalidation | Version fence + read-through to SoT on mismatch |
| Sequencer failover | New leader reads max(seq) from log; fence with epoch |
| Split-brain partition owner | Directory epoch + fencing token; only highest epoch writes |
| Fan-out drop | Client detects seq gap → sync API |
| Push before cache write-through | Client has seq from push; history read may retry — push payload is self-contained |
| Directory stale | Router retries; default to primary from fresh map |

#### 5.1.3 Cache rebuild after crash

```text
on partition startup(channel_id C):
  head = log.max_seq(C)
  tail = max(head - K, 0)
  ops = log.scan(C, tail+1 .. head)
  apply ops in order to empty ring (SEND inserts, DELETE tombstones)
  set channel_head_seq = head
```

Rebuild time for K=100, log fetch ~10ms — acceptable on migration or crash recovery.

### 5.2 Partition assignment deep dive

#### 5.2.1 Consistent hashing details

```text
Ring: 0 .. 2^32-1
Each physical node: 100–200 vnodes on ring
channel_id hashed (murmur3) → walk clockwise to first vnode → partition owner

Load skew without vnodes: Pr(max_load/mean) ≈ O(log P) — bad
With vnodes: skew typically < 10–15% at P=128
Monitor per-partition QPS; manual override for celebrity channels:
  hot_channel_id → dedicated partition HOT_17
```

#### 5.2.2 Colocating sequencer + cache

| Colocated | Benefit | Risk |
|-----------|---------|------|
| Yes | Write-through in-process; lower latency | Blast radius if host dies |
| No | Independent scaling | Extra RTT on every send |

**MVP:** colocate on same JVM/process per partition shard. **100×:** separate if CPU profiles differ.

### 5.3 Read path deep dive

#### 5.3.1 Ring buffer structure

```text
RingBuffer:
  channel_id
  messages: deque sorted by channel_seq (size ≤ K)
  index: message_id → Message*
  channel_head_seq: highest seq known
  channel_version: bumps on DELETE (invalidation generation)

get_history(after_seq, limit):
  collect msgs where seq > after_seq, sorted, take limit
  for each: if DELETED → { placeholder, seq, message_id }
```

**Gap handling:** if ring min_seq > after_seq+1, partial miss → backfill missing range from log, merge.

#### 5.3.2 Authz on cache path

Never trust cache to enforce ACL — API/router checks membership before forwarding to partition. Optional: partition stores **channel_id allowlist generation** bumped on membership change to reject stale readers fast.

### 5.4 Invalidation deep dive

#### 5.4.1 Send invalidation

Send is **upsert**, not invalidate — replicas can apply upsert idempotently:

```text
UPSERT { channel_id, message_id, seq, body, state=ACTIVE, version=seq }
```

#### 5.4.2 Delete invalidation

DELETE must **scrub body everywhere**:

```text
Owner:
  entry.body = null
  entry.state = DELETED
  entry.version = delete_seq

Bus message:
  { type: INVALIDATE, channel_id, message_id, delete_seq, channel_version }

Replica:
  if local entry.version < delete_seq:
      apply tombstone or evict message_id from index
```

#### 5.4.3 Race: invalidation arrives before upsert on replica

```text
Replica sees INVALIDATE delete_seq=106 for unknown message_id
  → create tombstone stub { message_id, state=DELETED, version=106 }
Later UPSERT seq=105 arrives (out-of-order bus)
  → if 105 < 106: apply as DELETED (tombstone wins by seq order logic)
  → ring merge uses total order, not arrival order
```

**Deal-breaker:** invalidate-by-TTL hoping DELETE eventually noticed — bodies leak for TTL window.

### 5.5 Consistency vs latency deep dive

#### 5.5.1 Read-your-writes (sender)

Sender gets ACK with seq → subsequent history read on owner must include that seq:

```text
Option A: route sender's reads to primary partition (sticky)
Option B: client merges optimistic local echo with server response
```

#### 5.5.2 Replica staleness bound

```text
replica_lag_slo: p99 < 100ms behind primary
if lag > threshold: replica stops serving; forward to primary
DELETE always sync-invalidates primary before ACK (primary must be clean)
```

#### 5.5.3 Comparison table

| Pattern | Latency | Delete safety | Complexity |
|---------|---------|---------------|------------|
| Owner only | Baseline | Highest | Low |
| Read replicas + version | Best read | High if fenced | Medium |
| Redis pub/sub invalidate | Good | Medium — missed messages | Medium |
| Full CRDT messages | Lowest offline | Hard delete semantics | High — skip MVP |

### 5.6 Fan-out interaction deep dive

#### 5.6.1 Why fan-out does not touch cache size

1000-member group sends 1 message:

```text
Cache: 1 ring insert (~500 B)
Fan-out: ~350 WS frames if 35% online (350 × 600 B ≈ 210 KB network)
Storage: 1 log row
```

Deleting that message:

```text
Cache: 1 tombstone update (body scrub)
Fan-out: ~350 DELETE events
Log: 1 DELETE op row
```

#### 5.6.2 Push payload vs cache read

Push event carries full message for realtime UX — **does not duplicate cache long-term**. Client memory holds message; server cache holds K-window. Different layers.

#### 5.6.3 Active viewer optimization (large groups)

```text
presence.active_in_channel(channel_id) → subset of members
fan-out push only to active ∩ online
others: unread badge increment + rely on cache/history pull when opening
```

#### 5.6.4 Fan-out worker partition affinity

Kafka topic keyed by `channel_id` → same fan-out worker order as log. Worker reads event → looks up online members → groups deliveries by WS gateway → batch send.

### 5.7 Group chat specifics

#### 5.7.1 Membership and cache

Membership changes do **not** migrate `channel_id` partition — only fan-out recipient list changes. Cache key stable.

On MEMBER_LEAVE: stop fan-out; history policy:

| Policy | Behavior |
|--------|----------|
| Retain history | Leave does not purge cache |
| Hide future only | Standard |
| GDPR scrub | Async job; tombstone user content |

#### 5.7.2 1:1 as special case

2-member channel — same design. No separate DM storage. Partition count unchanged.

### 5.8 Channel seq ordering

#### 5.8.1 Sequencer implementation

| Approach | Durability | Latency |
|----------|------------|---------|
| DB TX: UPDATE channel SET seq=seq+1 RETURNING | Strong | ~5–15ms |
| Redis INCR + async log | Fast | Risk if log write fails — need reconciliation |
| Kafka partition as log | Natural ordering | Seq = offset — good at scale |

**MVP:** DB or Redis INCR **in same failure domain as log insert** (outbox pattern).

#### 5.8.2 Holes

If SEND fails after seq allocated → hole in seq. Clients fetching gap get empty range — OK.

#### 5.8.3 Client apply algorithm

```text
expected_seq = local_head + 1
for op in incoming_ops sorted by channel_seq:
  if op.seq < expected_seq: dedupe skip
  if op.seq > expected_seq: sync gap from server
  apply(op)
  expected_seq = op.seq + 1
```

### 5.9 Scalability by phase

| Scale | Architecture |
|-------|--------------|
| **1×** | Monolith; Postgres log; single Redis cache cluster; WS gateway; sync fan-out |
| **10×** | P=32–128 cache partitions; Cassandra log; Kafka events; directory service |
| **100×** | P=512; read replicas; hybrid fan-out; LRU across 50M hot channels; cells |
| **1,000×** | Multi-region cells; cold segments; dedicated hot-channel partitions; edge WS |

#### 5.9.1 Hot channel mitigation

```text
Detect: partition write QPS > 5× median for 1 min
Actions:
  - pin channel to dedicated partition
  - rate-limit bot senders
  - widen K only if read-heavy (not write-heavy)
  - sequencer sharding NOT recommended — single order required
  - read replicas for history; writes still single-writer
```

### 5.10 Maintainability

- **Schema:** log ops never physically remove tombstones within retention.  
- **Metrics:** cache hit rate, replica lag, invalidation lag, partition skew, delete→hide latency.  
- **Chaos tests:** kill cache node mid-delete; drop invalidation; verify no body leak via sync path.  
- **Migration:** never change `channel_id → partition` mapping without explicit rebalance protocol.

### 5.11 Security

- AuthZ on send/delete/read — membership + role.  
- Rate limits: per-user send, per-channel delete storm.  
- Partition directory writes admin-only; routers read-only.  
- No cross-tenant cache bleed — `channel_id` globally unique.

### 5.12 E2EE note (if interviewer adds)

Server holds ciphertext in cache ring; DELETE scrubs ciphertext + emits retract event. Malicious client may retain plaintext — state honestly. Cache invalidation still required so honest clients converge.

---

## 6. Wrap-Up

### 6.1 What we designed

Group chat with **durable per-channel sequenced log**, **partitioned hot cache with channel affinity** holding the last K messages, **write-through on send**, **tombstone DELETE ops** with **invalidation bus + version fencing**, and **async fan-out** decoupled from cache footprint.

### 6.2 Decisions to defend

1. **`channel_id → consistent_hash → partition owner`** — affinity for coherent hot windows.  
2. **Log is SoT; cache is derived** — rebuild after crash.  
3. **`channel_seq` total order** — resolves send/delete races deterministically.  
4. **Delete-for-everyone = DELETE op + body scrub + cache invalidation** — not TTL.  
5. **Fan-out O(online); cache O(1) per message** — separate scaling dimensions.  
6. **Owner authoritative reads for MVP; fenced replicas at 100×**.  
7. **Hybrid fan-out** for large groups — protect WS tier.

### 6.3 Risks

| Risk | Mitigation |
|------|------------|
| Partition hot-spot | Vnodes + celebrity override + read replicas |
| Stale replica serves body | Version fence; forward to owner |
| Missed invalidation | Read-through tombstone check against SoT |
| Rebalance churn | Rare P changes; background migration |
| Fan-out lag | Kafka lag alerts; client gap sync |

### 6.4 45-minute interview plan

| Min | Focus |
|-----|-------|
| 0–5 | Clarify group chat, delete-for-everyone, read-heavy |
| 5–12 | Estimation: cache GB, P partitions, fan-out |
| 12–22 | HLD: log + partition cache + fan-out planes |
| 22–32 | Deep dive: read path, invalidation, delete tombstone |
| 32–40 | Consistency vs latency; hot channel; rebalance |
| 40–45 | Wrap risks, MVP vs 100× |

### 6.5 Closer

> **Chat with partitioned hot cache:** channel-affined ring buffers accelerate history reads; the sequenced log owns ordering and delete tombstones; write-through and invalidation keep caches coherent; fan-out scales independently because cache is per-channel, not per-member.

---

## 7. Deeper / Related Interview Questions

### 7.1 Partition assignment & cache

**Q: Why not put all channels in one Redis cluster?**  
A: Single cluster creates hot keys on celebrity channels, no clear ownership for write-through, and cross-slot multi-key coherence is painful. Partition affinity gives each node a bounded working set and clear invalidation scope.

**Q: How do you pick P (partition count)?**  
A: From read/write QPS per node capacity: `P ≥ max(S/W_max, R/R_max) × safety`, then validate skew with vnodes. Baseline 32–128; 100× 512 with replicas — not 2500 micro-nodes unless ops demands it.

**Q: What happens when you add a partition?**  
A: Consistent hash steals ranges; migrate channel rings with dual-write; bump directory epoch; drain old copies. Reads may miss during migration → backfill from log.

**Q: Can two partitions cache the same channel?**  
A: Only during migration dual-write window. Steady state: one primary owner. Replicas hold copies but owner is authoritative.

**Q: Why colocate sequencer and cache?**  
A: Write-through after seq assign is in-process — saves RTT. At extreme scale, split if CPU profiles diverge.

### 7.2 Read path

**Q: Cache hit rate expectations?**  
A: For active channels (recent send or read), near 100% on window. Long tail cold opens miss once then warm. Target cluster hit rate 85–95% depending on K and LRU size.

**Q: How paginate beyond K cached messages?**  
A: Bypass cache; read directly from channel log by seq range. Cache only optimizes the tail.

**Q: Read-your-writes for sender?**  
A: Route to primary after ACK, or client optimistic merge. Never read from lagging replica immediately after send.

**Q: How handle seq gaps in ring?**  
A: Detect `min_ring_seq > after_seq+1`; backfill missing range from log; merge into ring.

### 7.3 Invalidation & delete tombstones

**Q: What does delete-for-everyone mean under concurrency?**  
A: Append DELETE op with new `channel_seq`. All clients apply ops in order. If DELETE comes after SEND, body hidden. Offline devices converge on sync. Cache scrubs body on owner; invalidation bus updates replicas.

**Q: Soft delete flag vs tombstone event?**  
A: Flag alone fails offline sync and cache peers that never re-read DB. Tombstone in the **log** is the portable source; cache mirrors it.

**Q: Can you physically delete the row?**  
A: After retention, cold tier compaction may drop scrubbed bodies; retain tombstone or delete op in log for seq integrity until compaction window safe.

**Q: Invalidation missed — user sees deleted body?**  
A: Read fence: check `state==DELETED` or `version < delete_seq` → refresh from owner/SoT. Metric: `cache_stale_body_blocked_total`.

**Q: Delete arrives on replica before send upsert?**  
A: Create tombstone stub; when SEND upsert arrives with lower seq, apply-order logic keeps DELETED final state.

**Q: Is TTL ever acceptable for delete?**  
A: No for user-initiated delete-for-everyone — TTL is unbounded wrong UX. TTL OK for evicting **cold channels**, not individual delete semantics.

### 7.4 Consistency vs latency

**Q: Strong vs eventual cache reads?**  
A: MVP owner-only. Replicas add staleness window (~ms–100ms). DELETE ACK waits primary scrub — never ACK delete while primary still serves body.

**Q: CP or AP for chat cache?**  
A: Writes CP (durability + order). Reads may be AP on replicas with fencing — bounded staleness acceptable for scroll-back, not for delete visibility (primary clean before ACK).

**Q: Compare to CDN edge cache?**  
A: CDN lacks channel seq awareness and fine tombstone invalidation — inappropriate for personalized group history. Partition cache is origin-adjacent, membership-aware.

### 7.5 Fan-out interaction

**Q: Does fan-out duplicate cache memory?**  
A: No. One ring entry per message per channel. Fan-out multiplies network deliveries to online members, not server cache entries.

**Q: Push vs pull when group has 5k members?**  
A: Pull on channel open for history (cache). Push only to active online viewers (~ tens–hundreds). Send ACK not blocked by 5k pushes.

**Q: Delete in 5k group — 5k cache updates?**  
A: No. One cache tombstone + O(online) push. Offline members learn on sync from log/cache.

**Q: Fan-out before cache write-through — problem?**  
A: Push carries full payload for realtime; recipient OK. If recipient immediately hits history API, owner should already have write-through or client uses pushed payload until cache warm.

### 7.6 Group chat & ordering

**Q: 1:1 vs group design difference?**  
A: Same `channel_id` model. Fan-out size differs (2 vs N). Cache identical.

**Q: Vector clocks vs server seq?**  
A: Server `channel_seq` simpler for total order and delete semantics. Vector clocks for offline edits conflict — overkill for MVP chat.

**Q: How prevent duplicate messages on retry?**  
A: Idempotent `(channel_id, client_msg_id)` → same `message_id` and seq returned.

**Q: Membership change invalidate cache?**  
A: Not required for message bodies. Bump ACL generation for authz gate. Optional: evict if policy requires hiding channel from ex-member reads immediately.

### 7.7 Scale & failures

**Q: Hot channel on one partition — what breaks first?**  
A: Sequencer single-writer (~5–20K ops/s) before cache memory. Mitigate rate limits, read replicas, dedicated partition.

**Q: Rebuild cache after node loss?**  
A: Scan log tail K ops per owned channel — seconds for thousands of channels if pipelined.

**Q: Multi-region?**  
A: Home cell owns channel seq + primary cache partition. Regional WS gateways subscribe to event stream. Cross-region cache replica optional with lag label on reads.

### 7.8 Product & privacy

**Q: Delete-for-me vs delete-for-everyone?**  
A: For-me = per-user hide pointer (not in shared cache). For-everyone = tombstone in shared log + cache invalidation affecting all members.

**Q: Search still shows deleted text?**  
A: Indexer consumes DELETE stream; update doc `deleted=true`; scrub body field. Lag SLA separate from cache path.

**Q: E2EE impact?**  
A: Server scrubs ciphertext; retract event; honest clients hide. Cache invalidation still needed.

**Q: Legal hold vs user delete?**  
A: Policy flag blocks DELETE op or retains sealed copy in compliance store while scrubbing from cache + member view.

### 7.9 Testing & traps

**Q: How test concurrent send/delete races?**  
A: Property test: random interleave ops; apply via seq order; assert all clients converge. Chaos: drop invalidation messages; assert read fence blocks body.

**Q: Trap — cache TTL as delete strategy?**  
A: Wrong — body visible until TTL expires.

**Q: Trap — per-user inbox cache of same messages?**  
A: N× memory; delete must invalidate N caches — defeats partitioned shared cache.

**Q: Trap — order by client timestamp?**  
A: Clock skew breaks delete/send ordering.

**Q: Trap — sync fan-out inside send API?**  
A: Large groups blow ACK latency; blocks send path.

### 7.10 Related designs

**Q: How is this different from Slack HLD?**  
A: Slack doc covers workspace/threads/search broadly. This doc centers **partitioned hot cache coherence** with channel affinity as the scaling primitive for read-heavy history.

**Q: When use CRDTs?**  
A: Collaborative offline edits with merge — not for strict delete-for-everyone total order. Mention but defer.

**Q: Kafka as message store?**  
A: Good append log; random history by seq needs layered index or compaction consumer materializing per-channel store — cache still helps tail reads.

---

*End of chat partitioned hot cache HLD prep.*
