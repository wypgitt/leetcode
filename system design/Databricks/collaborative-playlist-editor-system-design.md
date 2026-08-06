# System Design: Collaborative Playlist Editor (Spotify-like Shared Playlists)

> **Focus areas:** OT/CRDT · Real-time sync · Conflict resolution · Presence · Offline merge · WebSocket sync · Snapshot + op log  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit latency budgets, honest OT vs CRDT trade-offs, failure-first offline merge  
> **Interview theme:** Databricks — classic HLD; converges on ordered replicated data, durable logs, and merge semantics familiar from Delta/Lakehouse lineage

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

Goal: **bound a Spotify-like collaborative playlist editor**—multiple users reorder/add/remove tracks concurrently, stay in sync in real time, merge offline edits safely, and show who is active—without losing concurrent intent to naive last-write-wins.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the product? | Shared **playlists** (ordered track lists) editable by multiple users; like Spotify collaborative playlists | Core = **ordered list CRDT/OT**, not a chat log |
| F2 | Who can edit? | Owner invites collaborators; roles: **owner / editor / viewer**; optional link-share view-only | AuthZ on every op; reject mutations for viewers |
| F3 | Track identity? | Same **catalog track** (`track_id`) may appear **multiple times**; each list position is a unique **entry** (`entry_id`) | Never key list by `track_id` alone |
| F4 | Edit operations? | **Insert** after/before entry, **delete** entry, **move** entry, **edit metadata** (title, description, cover art ref) | Finite op vocabulary; versioned op log |
| F5 | Ordering guarantee? | All clients converge to **same total order**; concurrent inserts at same anchor both appear | Server total-order or CRDT merge; **not LWW on whole list** |
| F6 | Real-time sync? | Changes visible in **<1s** for online editors; typing/presence optional | WebSocket room per playlist + durable op broadcast |
| F7 | Offline editing? | Mobile may queue ops offline; merge on reconnect without silent data loss | CRDT or OT with **transform**; idempotent `op_id` |
| F8 | History / undo? | Phase 2; MVP may expose op log for audit only | Op log is durable; undo = inverse ops later |
| F9 | Playlist size? | Typical **50–500** tracks; power users **10K**; hard cap **50K** with pagination | Snapshot + paginated load; bulk ops async |
| F10 | Catalog / playback? | We **reference** catalog tracks; playback is separate service | Store `track_id` pointers; validate existence async |
| F11 | Notifications? | "Alice added 3 songs" optional; not blocking sync path | Async notification worker from op log |
| F12 | Compliance / takedown? | If catalog track removed, playlist shows **unavailable** stub; no silent delete of user history | Tombstone entries; metadata flag `available=false` |

**MVP functional scope (lock with interviewer):**

1. Create playlist; invite editors/viewers; role-based ACL.
2. **Load playlist:** snapshot (ordered `entry_id`s + track metadata) + optional tail ops.
3. **Submit ops:** insert/delete/move/metadata with client `op_id` idempotency.
4. **Server total-orders** ops per playlist (`server_seq`); apply to authoritative state; ACK after durable append.
5. **WebSocket sync:** broadcast applied ops to subscribed clients in `server_seq` order.
6. **Offline merge:** client queues ops; on reconnect, submit batch; server transforms against concurrent ops; return catch-up stream.
7. **Presence:** who is viewing/editing playlist (best-effort); optional "Alice is dragging track X".
8. **Snapshot + compaction:** periodic snapshot of list state; truncate op log before snapshot seq.
9. Rate limits per user/playlist; audit log of admin actions.

**Out of MVP (explicitly defer):**

- Real-time **waveform-accurate** co-editing of same drag gesture (OT on pixel cursors)
- **Branching** playlists / merge two playlists with conflict UI
- **Global active-active multi-writer** for same playlist across regions
- Full **undo/redo** stack synced across users
- Collaborative **smart shuffle / radio** algorithm co-editing
- E2E encryption of playlist contents

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Op apply latency (online)? | Feels instant | p50 < 100ms, p99 < 400ms in-region (ACK = durable) |
| N2 | Realtime fan-out latency? | See others' edits quickly | p99 < 800ms persist → push to subscribed sockets |
| N3 | Durability? | Never lose accepted ops | RPO ≈ 0 for ACK'd ops; at-least-once WS delivery |
| N4 | Convergence? | All clients same order after sync | Strong per-playlist total order via `server_seq` |
| N5 | Availability? | Editing is core UX | 99.9% control plane; degrade presence before writes |
| N6 | Offline merge correctness? | No duplicate entries from retries | Idempotent `(playlist_id, op_id)`; deterministic transform |
| N7 | Throughput? | See scale table | Partition by `playlist_id`; hot playlist isolation |
| N8 | Multi-region? | Global users | Edge WS gateways; **home cell single-writer** per playlist |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Alice creates playlist → invites Bob (editor) → both open editor → Alice inserts track after T1 → Bob sees insert via WS within 1s.
2. Bob moves track while Alice inserts at same anchor → server orders ops → both edits preserved in final list (not LWW).
3. Carol (viewer) opens playlist → read-only; mutations rejected with 403.
4. Dave offline adds 5 tracks → reconnects → batch submit → server merges → all clients converge.
5. New client joins → `GET snapshot@seq=S` + `ops since S` → renders identical list.
6. Playlist hits 10K tracks → paginated virtualized UI; snapshot loaded in chunks; tail ops still fine-grained.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit same op | Idempotent `op_id` → return original `(server_seq, applied_op)` |
| Insert after deleted entry | Server **retargets** to nearest valid anchor or append; return `transformed_op` in ACK |
| Concurrent delete + move same entry | Total order decides: if delete first, move becomes no-op with explicit ACK reason |
| Duplicate `track_id` entries | Allowed; each insert creates new `entry_id` |
| Server crash after append, before WS push | Op durable; clients gap-fill via `ops?since=` |
| Client misses WS events | Detect seq gap → pull ops range |
| Hot playlist (party mode, 200 editors) | Per-playlist op queue; rate limit; optional coalesce of bulk adds |
| Catalog track delisted | Entry remains; UI shows unavailable; playback blocked |
| Owner revokes Bob mid-edit | ACL check on every op; WS force refresh membership; reject pending client ops |
| Compaction mid-read | Snapshot version pinned; ops reference `base_snapshot_seq` |
| Two devices same user offline | Same `op_id` namespace per device session or merge by server seq |
| Oversized batch offline sync | Chunk to 100 ops/request; 413 if playlist over cap |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU (editor-capable app) | 500K | 5M | 50M | 500M |
| Collaborative playlists (active) | 2M | 20M | 200M | 2B |
| Peak concurrent WS (playlist rooms) | 50K | 500K | 5M | 50M |
| Peak op ingest QPS (global) | 500 | 5K | 50K | 500K |
| Peak op **delivery** ops/s (ingest × avg online collaborators) | ~2K | ~20K | ~200K | ~2M |
| Sync/history read QPS | 3K | 30K | 300K | 3M |
| Avg online collaborators / active playlist | 2.5 | 2.5 | 3 | 3 |
| Hot playlist peak op QPS | 5 | 20 | 50 | 100 (rate-limited) |
| Avg playlist length (entries) | 200 | 200 | 250 | 300 |
| Op log bytes / day (uncompacted) | ~6.5 GB | ~65 GB | ~650 GB | ~6.5 TB |
| Snapshot storage (all playlists) | ~400 GB | ~4 TB | ~40 TB | tiered / cold |

**What each jump forces:**

- **10×:** WS gateway fleet; Redis presence; playlist-partitioned op log; snapshot worker.
- **100×:** Home-cell routing; Kafka op fan-out; CRDB/Cassandra for op log ranges; aggressive compaction; hot playlist isolation.
- **1,000×:** Edge connection layer; binary WS protocol; cell sharding by `playlist_id`; cold snapshot tier in object store; admission control on hot keys.

### 1.5 Etc. (Constraints & Assumptions)

- **Single cloud**, multi-AZ MVP; multi-region with playlist home region at 100×.
- **Clients:** mobile + web; one sync protocol (HTTPS + WSS).
- **Catalog service** external; we cache track metadata with TTL.
- **Money/royalty** not in scope—assume playback service handles licensing.
- Clocks: server wall clock for UI timestamps; **never** use client clock for ordering.

**Scope statement:**

> Design a collaborative playlist editor: ordered track list with insert/delete/move, server-total-ordered op log + periodic snapshots, WebSocket realtime sync, offline merge with idempotent ops, and best-effort presence—starting at ~500 op/s, ~50K concurrent playlist WS connections, evolving through 10× / 100× / 1,000× with home-cell single-writer and compaction.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Op ingest vs delivery (do not conflate)

```text
Baseline peak op ingest QPS = 500
Avg online collaborators receiving each op ≈ 4 (includes multi-tab)
Peak delivery ops/s ≈ 500 × 4 = 2,000/s

Hot playlist tail (party):
  10 op/s × 80 online editors ≈ 800 deliveries/s from ONE playlist
  → still manageable; 100× hot path needs dedicated partition + rate limits
```

At **100×**:

```text
50K ingest/s × 4 ≈ 200K delivery/s
WS gateway batching: 200K events/s × ~200 B/op ≈ 40 MB/s egress (order-of)
Manageable with gateway-local fan-out batching; not like Slack megachannel
```

### 2.2 WebSocket connections

```text
Baseline peak playlist WS connections: 50,000
Per-conn state: ~8–20 KB (subs, buffers, auth) → ~0.4–1 GB / 50K
Evented gateway: ~50K–150K conns / node → ~4–8 nodes baseline (N+2)
```

At **1,000× (50M conns)**:

```text
50M × 15 KB ≈ 750 GB RAM across edge fleet
→ geo-sharded connection gateways mandatory; not one cluster
```

### 2.3 Op log storage (the durable truth)

```text
Avg op record on disk: ~180 B
  op_id(16) + playlist_id(16) + server_seq(8) + type(1)
  + entry_id(16) + anchor_entry_id(16) + track_id(8) + actor(16)
  + client_ts(8) + metadata var ~50 B + indexing overhead

Baseline: 500 ops/s × 86,400 ≈ 43.2M ops/day
43.2M × 180 B ≈ 7.8 GB/day raw op log

90-day retention without compaction: ~700 GB
With daily snapshot + truncate ops older than snapshot-1d: ~7.8 GB × 2 ≈ 16 GB hot log
```

**Compaction math:**

```text
Snapshot every 10K ops OR 24h, whichever first
Avg playlist 200 entries; snapshot row ≈ 200 × 24 B entry payload + header ≈ 5 KB
2M active playlists × 5 KB ≈ 10 GB snapshot store (baseline)
+ version history 3 deep ≈ 30 GB — fine on object store / DB
```

### 2.4 Snapshot size examples

| Playlist size | Snapshot payload (order-of) | Notes |
|---------------|----------------------------|-------|
| 50 tracks | ~1.5 KB | Single HTTP response |
| 500 tracks | ~15 KB | gzip → ~4 KB |
| 10K tracks | ~300 KB | Paginate snapshot API; virtual scroll |
| 50K tracks (cap) | ~1.5 MB | Must chunk; async rebuild |

```text
Cold open (500-track playlist):
  GET snapshot: 15 KB @ 3K QPS ≈ 45 MB/s read (baseline blended — OK)
  Tail ops since snapshot: usually <100 ops × 180 B ≈ 18 KB
```

### 2.5 Bandwidth

```text
WS push: applied op ~220 B JSON (or ~120 B protobuf at scale)
2K deliveries/s × 220 B ≈ 440 KB/s baseline realtime egress

Offline catch-up worst case: client 24h behind on active playlist
  Assume 200 ops × 180 B ≈ 36 KB — trivial
  Power editor day: 5K ops × 180 B ≈ 900 KB — still OK
```

### 2.6 Presence memory

```text
Presence record: ~80 B (user_id, playlist_id, status, last_seen, cursor_entry_id)
50K concurrent editors in rooms; unique presence keys maybe 30K (overlap)
30K × 80 B ≈ 2.4 MB — negligible
100×: 3M keys × 80 B ≈ 240 MB sharded Redis — fine
```

### 2.7 Bottlenecks (ranked)

1. **Hot playlist partition** — single-writer sequencer becomes serial bottleneck  
2. **Op log write + index** on `(playlist_id, server_seq)` range scans  
3. **Snapshot rebuild** for 10K+ entry lists under heavy churn  
4. **WS fan-out** during viral party playlist (mitigate with batching + rate limits)  
5. **Offline batch merge** storms after conference Wi-Fi reconnect (admission + chunking)

---

## 3. High-Level Design

### 3.1 Product / UX surfaces (wireframe)

```text
+--------------------------------------------------------------------------+
| ♫ My Playlists    |  Summer Road Trip  [Collaborative]  👤👤👤 3 editing |
+-------------------+------------------------------------------------------+
| > Summer Road Trip|  [Cover]  Title: Summer Road Trip                    |
|   Workout Mix     |  By Alice · 142 tracks · Updated 2m ago              |
|   Party Queue *   |                                                      |
|                   |  #  Title                    Artist      Added by    |
|                   |  1  Mr. Brightside           Killers     Alice         |
|                   |  2  Dog Days Are Over        Florence    Bob ←drag   |
|                   |  3  ▶ (new) Levitating       Dua Lipa    You         |
|                   |  ...                                                 |
|                   |  [ + Add songs ]    Bob is editing row 2...          |
+--------------------------------------------------------------------------+
```

Client maintains: local ordered list keyed by `entry_id`, `last_applied_seq`, pending offline op queue, presence map.

### 3.2 Domain model

```text
User
  └── Playlist (playlist_id, owner_id, title, description, cover_ref, acl_policy)
        ├── PlaylistMembership (user_id, role: owner|editor|viewer)
        ├── PlaylistEntry (entry_id, track_id, added_by, added_at, available)
        │     └── stable identity for list CRDT/OT (not same as track_id)
        ├── OpLog (playlist_id, server_seq, op_type, payload, actor, op_id)
        └── Snapshot (playlist_id, snapshot_seq, entries[], metadata_hash)
```

**Identity & ordering fields:**

| Field | Role |
|-------|------|
| `entry_id` | ULID per list row — survives track_id duplicates |
| `server_seq` | Monotonic **per playlist** — total order SoT |
| `op_id` | Client UUID — idempotency |
| `snapshot_seq` | Last op included in snapshot |
| `transformed_payload` | What server actually applied (may differ from client intent) |

**Deal-breaker:** replacing entire playlist JSON with LWW on save — concurrent edits silently lost.

### 3.3 OT vs CRDT trade-offs (say aloud early)

| Dimension | OT (server transform) | CRDT (RGA / LSEQ / Fractional) |
|-----------|----------------------|--------------------------------|
| Ordering SoT | Central server total order | Replica merge without server |
| Offline | Queue ops; server transforms on submit | Apply locally; merge on sync |
| Complexity | Transform functions per op pair | Metadata per entry (LSEQ strings grow) |
| Storage | Compact ops | Tombstones + identifiers accumulate |
| Multi-region write | Natural single-writer home cell | Tempting multi-writer — harder ACL |
| Interview clarity | Easier to explain | Better for true P2P offline |
| Databricks angle | Like **single-writer transaction log** | Like **mergeable replicated structure** |

**Choice for MVP:** **Server-sequenced OT-lite**

- Client proposes op; server assigns `server_seq`, applies against current state, may retarget anchors; broadcasts **applied op**.
- Offline clients submit same ops; server transforms identically — deterministic convergence.
- **Phase 2 / offline-first mobile:** hybrid with **RGA** entry IDs (already have `entry_id`) and LSEQ-style fractional positions for local apply before sync.

**Deal-breakers:**

- CRDT with unbounded LSEQ strings on 10K-track list without compaction  
- OT without idempotent op IDs (retries duplicate rows)  
- Client-authoritative ordering without server validation  

### 3.4 Latency budget (online op path)

```text
Total p99 target: 400ms (ACK = durable append)

Client → Edge TLS                     10–30ms
Edge → Playlist Op Service (home cell)  5–20ms
AuthZ + membership check               5–15ms   (cached ACL)
Load playlist head state (cache)       2–10ms
Apply op + allocate server_seq (TX)  15–40ms
Append op log durable (sync replicate) 20–80ms
Publish to fan-out bus                 5–15ms
ACK to client                          5–10ms
Async WS push to collaborators       50–200ms (not on ACK critical path)
──────────────────────────────────────────────
Sum (ACK path)                         ~70–220ms typical; budget 400ms p99
```

Separate **realtime SLO:** persist → push p99 < 800ms.

### 3.5 API / protocol shape

**HTTP (sync / load / submit):**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/v1/playlists` | Create playlist |
| GET | `/v1/playlists/{id}` | Metadata + ACL |
| GET | `/v1/playlists/{id}/snapshot` | Snapshot at `?at_seq=` or latest |
| GET | `/v1/playlists/{id}/ops` | Range sync `?since_seq=&limit=` |
| POST | `/v1/playlists/{id}/ops` | Submit single op or batch (idempotent) |
| POST | `/v1/playlists/{id}/members` | Invite / change role |
| DELETE | `/v1/playlists/{id}/entries/{entry_id}` | Sugar for delete op |

**Example submit:**

```http
POST /v1/playlists/P123/ops
Idempotency-Key: 7b3e9c2a-...
Authorization: Bearer ...

{
  "op_id": "7b3e9c2a-...",
  "type": "INSERT_AFTER",
  "track_id": "T999",
  "after_entry_id": "E42"
}
```

**Response (ACK):**

```json
{
  "playlist_id": "P123",
  "op_id": "7b3e9c2a-...",
  "server_seq": 1042,
  "applied": {
    "type": "INSERT_AFTER",
    "entry_id": "E9001",
    "track_id": "T999",
    "after_entry_id": "E42"
  },
  "transform_notes": []
}
```

**WebSocket:**

```text
Client → Server:  subscribe_playlist, unsubscribe, ping, presence_update
Server → Client:  op_applied, playlist_metadata_changed, presence,
                  membership_revoked, snapshot_invalidate(seq)
```

Subscribe requires membership check; server sends backlog `ops since client_last_seq` on subscribe.

### 3.6 Multi-region

```text
                    [Edge WS — us-west]
                           |
         +-----------------+------------------+
         v                 v                  v
   [Edge WS eu]     [Home Cell us-east]   [Edge WS apac]
                           |
              Playlist Op Service (single writer per playlist_id)
              Op Log DB + Snapshot Store (home region)
```

- **playlist_id → home_cell** mapping in directory (sticky for life of playlist).
- All mutating ops **forward to home cell**; reads can served from read replica with `min_seq` lag guard.
- Failover: fence old primary; promote replica; bump **epoch**; clients resync.

### 3.7 High-level architecture

```text
          +------------------+
          | Web / Mobile App |
          +--------+---------+
                   | HTTPS + WSS
          +--------v---------+
          | Edge / LB / TLS  |
          +--------+---------+
                   |
      +------------+-------------+
      v                          v
+-------------+           +-------------+
| WS Gateway  |           | Playlist API|
| (rooms,     |           | (load, ops, |
|  presence)  |           |  ACL)       |
+------+------+           +------+------+
       |                         |
       v                         v
+-------------+           +------------------+
| Conn +      |           | Playlist Op      |
| Presence    |           | Service          |
| (Redis)     |           | (sequencer,      |
+-------------+           |  transform, TX)  |
                          +--------+---------+
                                   |
                          +--------v---------+
                          | Op Log + Snapshot|
                          | Store (Postgres/ |
                          |  CRDB + S3)      |
                          +--------+---------+
                                   |
                          +--------v---------+
                          | Fan-out Bus      |
                          | (Kafka/outbox)   |
                          +--------+---------+
                                   |
                    +--------------+--------------+
                    v                             v
             WS Gateway push               Snapshot/compaction
             to subscribed clients          worker (async)
```

---

## 4. Architecture Diagram

### 4.1 Sequence: concurrent inserts at same anchor

```text
Alice                         Playlist Op Svc              Bob (via WS)
  |--INSERT_AFTER T1, track X-->|                            |
  |                             | seq=10, entry E100         |
  |<--ACK seq=10, E100----------|                            |
  |                             |---op_applied seq=10------->|
  |                             |                            |
Bob |--INSERT_AFTER T1, track Y->|                            |
  |                             | (T1 still valid)           |
  |                             | seq=11, entry E101 after E100|
  |<--ACK seq=11, E101----------|                            |
  |                             |---op_applied seq=11------->|
  |                             |                            |

Final order: ..., T1, X(E100), Y(E101)
Both concurrent intents preserved — NOT LWW
```

### 4.2 Sequence: offline merge on reconnect

```text
Offline Client                     API                     Op Log
  | (queued: INS A, DEL B, MOV C)  |                          |
  |--POST /ops batch-------------->|                          |
  |                                |--load head seq=500------>|
  |                                |--for each op transform-->|
  |                                |   (DEL B ok, MOV C retarget
  |                                |    if anchor deleted)    |
  |                                |--append seq 501..503---->|
  |<--200 [{seq,applied}...]-------|                          |
  |--WS subscribe since=503------->|                          |
  |<--catch-up + live stream-------|                          |
```

If batch overlaps server ops during offline window, each client op is transformed against **current** state at processing time — order within batch preserved.

### 4.3 Sequence: failure / retry after crash

```text
Client                Op Service              DB              Fan-out
  |--INSERT op_id K-->|                       |                 |
  |                    |--BEGIN TX------------>|                 |
  |                    |--append seq=42------->|                 |
  |                    |--COMMIT------------->|                 |
  |                    X (crash before ACK)   |                 |
  |--RETRY op_id K--->|                       |                 |
  |                    |--find op_id K------->| (unique index)  |
  |<--ACK seq=42-------|                       |                 |
  |                    |--(replay fan-out?)----|---------------->|
  |                    |   dedupe by seq       |                 |
```

**Rule:** `(playlist_id, op_id)` unique → safe retries. Fan-out consumers dedupe by `(playlist_id, server_seq)`.

### 4.5 Sequence: snapshot compaction

```text
Compaction Worker          Op Log              Snapshot Store
  |--select playlist P--->|                     |
  |--read ops > snap@900->|                     |
  |--apply in memory      |                     |
  |--write snapshot@950------------------------>|
  |--mark truncate safe@920 (retain buffer)     |
  |--delete ops <920------>|                     |
```

Clients with `last_seq=905` unaffected; cold start loads snapshot@950 + ops 951+.

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

**Hard invariants**

1. **Single total order per playlist:** `server_seq` strictly monotonic; no gaps on successful append (holes only on rollback of uncommitted TX).  
2. **ACK ⇒ durable:** HTTP 200 / WS `op_applied` only after op log fsync / quorum commit.  
3. **Idempotent ops:** `(playlist_id, op_id)` maps to exactly one `server_seq`.  
4. **Deterministic apply:** Given same op log prefix, all replicas compute identical entry order.  
5. **ACL enforced at apply time:** membership checked in same TX as append — not just at WS subscribe.  
6. **Transform disclosure:** if server retargets anchor, response includes `transform_notes` for client audit.  
7. **No silent catalog delete:** delisted tracks → `available=false`, entry remains.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Op service crash mid-TX | Client retries same `op_id`; no double append |
| WS push miss | Client detects seq gap; pulls `/ops?since=` |
| Redis presence down | Degrade presence; ops still work |
| Kafka fan-out lag | Monitor lag; clients pull; scale consumers |
| Hot playlist overload | Per-playlist rate limit; queue + 429; fairness |
| Snapshot worker stuck | Ops log grows; alert; read path still works |
| ACL revoke race | Version ACL; reject ops with stale epoch |
| Split-brain home cell | Epoch fencing on playlist directory; single primary |

### 5.2 Scalability: 1× → 10× → 100× → 1,000×

| Scale | Architecture |
|-------|--------------|
| **1×** | Modular monolith: Op Service + Postgres op log + Redis presence + WS gateway |
| **10×** | Shard op log by `playlist_id`; horizontal gateways; snapshot worker pool; ACL cache |
| **100×** | Home cells; Kafka fan-out; CRDB/Cassandra for op ranges; S3 snapshots; hot playlist isolation |
| **1,000×** | Global edge WS; binary protocol; tiered snapshot storage; admission on viral playlists |

**1× — correct MVP**

```text
POST /ops:
  authz → load playlist state row (FOR UPDATE) → apply op in memory
  → INSERT op_log → UPDATE playlist_head → COMMIT
  → outbox event → WS fan-out worker
GET /snapshot: read materialized snapshot row + track metadata cache
```

**10×**

- Partition Postgres by `hash(playlist_id)` or Citus.  
- Connection registry: `user_id → gateway_id` in Redis.  
- Batch WS messages every 10–20ms per playlist room.  
- Coalesce duplicate presence updates.

**100×**

- Playlist home cell routing service.  
- Op log hot store 7d + cold archive in object storage.  
- Snapshot CDN for popular public playlists.  
- Dedicated **hot playlist** queue (shard override) when op QPS > threshold.

**1,000×**

- Viral playlist: switch to **read-heavy mode** — rate limit edits to editors with tokens; viewers unlimited.  
- Precomputed snapshot every N seconds during party mode.  
- Cell migration tool for imbalanced shards.

### 5.3 Operation types & transform rules

| Op type | Payload | Server apply rule |
|---------|---------|-------------------|
| `INSERT_AFTER` | `track_id`, `after_entry_id?` | Create `entry_id`; if anchor missing, append; dedupe same `op_id` |
| `INSERT_BEFORE` | `track_id`, `before_entry_id` | Equivalent to insert after predecessor |
| `DELETE` | `entry_id` | Tombstone entry; idempotent if already deleted |
| `MOVE` | `entry_id`, `after_entry_id?` | Remove then insert; no-op if entry deleted |
| `UPDATE_META` | title/desc/cover | LWW on metadata fields with `meta_version` (separate from list order) |
| `BULK_ADD` | `[track_id...]`, `after_entry_id?` | Expand to N inserts in one TX; one server_seq range block |

**Transform examples (OT-lite):**

```text
Concurrent: A inserts X after T1; B inserts Y after T1
Server order A then B:
  Apply A → ..., T1, X
  Apply B (after_entry_id=T1) → retarget insert to after X (last insert at T1 anchor)
  Result → ..., T1, X, Y

Concurrent: A deletes E5; B moves E5 after E2
If delete seq < move seq:
  Move becomes no-op; ACK with transform_note DELETED_TARGET
```

**Conflict example (move vs move):**

```text
List: A, B, C, D
User1: MOVE C after A   (op O1)
User2: MOVE C after D   (op O2)   // concurrent

Server orders O1 before O2:
  After O1: A, C, B, D
  O2: move C after D → A, B, D, C

If O2 before O1:
  After O2: A, B, D, C
  O1: move C after A → A, C, B, D

Different total orders → different outcomes — **correct** under OT;
clients converge to server's total order.
```

### 5.4 Snapshot + compaction

**Snapshot contents:**

```json
{
  "playlist_id": "P123",
  "snapshot_seq": 9500,
  "entries": [
    {"entry_id":"E1","track_id":"T10","added_by":"U1","available":true},
    ...
  ],
  "metadata": {"title":"...", "meta_version": 12}
}
```

**Compaction policy:**

```text
Trigger when: op_count_since_snapshot > 10_000 OR age > 24h OR size > 50MB rebuild cost
Steps:
  1. Apply ops (snapshot_seq, head_seq] to build new snapshot
  2. Upload to object store; pointer in DB
  3. Truncate op log < head_seq - safety_buffer(1000)
Retain audit trail separately if compliance requires (cold storage)
```

**Cold start cost:**

```text
500-track playlist, snapshot_seq gap 200 ops:
  1 snapshot read (15 KB) + 200 ops (36 KB) ≈ 51 KB — p99 < 50ms from DB
10K-track playlist:
  Paginated snapshot 4 × 75 KB pages + tail ops — parallel fetch
```

### 5.5 Permissions model

| Role | Read | Insert/Move/Delete | Invite | Delete playlist | Transfer ownership |
|------|------|-------------------|--------|-----------------|-------------------|
| Owner | ✓ | ✓ | ✓ | ✓ | ✓ |
| Editor | ✓ | ✓ | ✗ | ✗ | ✗ |
| Viewer | ✓ | ✗ | ✗ | ✗ | ✗ |

- Share link: token maps to viewer or editor; expiring tokens.  
- Every op TX loads `membership_version`; if revoked mid-session, return 403 + WS `membership_revoked`.  
- **Deal-breaker:** caching ACL forever without invalidation on revoke.

### 5.6 Failure walkthrough (one request, crash points)

```text
Client POST INSERT op_id=K
  → [C1] API gateway timeout — client retries OK (idempotent)
  → [C2] AuthZ pass
  → [C3] BEGIN; lock playlist head
  → [C4] append op_log seq=42
  → [C5] update snapshot_head pointer in memory cache
  → [C6] COMMIT
  → [C7] return 200 ACK
  → [C8] outbox → Kafka
  → [C9] fan-out → WS gateways
  → [C10] Bob receives op_applied

Crash at C4 before COMMIT → no seq 42; retry re-applies
Crash at C6 after COMMIT → retry returns same seq 42 via op_id index
Crash at C9 → Bob pulls gap; no data loss
```

### 5.7 Observability

| Metric | Why |
|--------|-----|
| `op_apply_latency_p99` | Core write SLO |
| `persist_to_push_lag_p99` | Realtime feel |
| `op_log_bytes_per_playlist` | Compaction health |
| `hot_playlist_op_qps` | Shard isolation triggers |
| `transform_rate` (retarget/no-op) | UX conflict indicator |
| `offline_batch_size_p99` | Reconnect storm capacity |
| `ws_room_size` | Fan-out cost |
| `snapshot_rebuild_duration` | Worker capacity |
| `acl_denied_ops` | Security / revoke correctness |

Traces: span per op with `playlist_id`, `op_type`, `transform_notes` (low cardinality enums).

**Alerts:** op log uncompacted > 7 days; fan-out lag > 5s; hot playlist queue depth.

### 5.8 Security

- **AuthN:** OAuth 2.0 / JWT; playlist tokens scoped.  
- **AuthZ:** server-side every op; no client-side-only role checks.  
- **IDOR:** cannot read `/ops` or WS subscribe without membership.  
- **Rate limits:** 30 ops/min/user/playlist baseline; burst 10/s.  
- **Input validation:** `track_id` exists in catalog cache; reject 10K bulk in one op MVP.  
- **WS:** subscribe frame re-validates membership; periodic re-auth on long sessions.  
- **Audit:** immutable admin log for ACL changes.  
- **Encryption:** TLS in transit; DB + S3 at rest.

### 5.9 Presence (best-effort)

```text
presence_key = (playlist_id, user_id) → {status, last_seen_ms, editing_entry_id?}
TTL 30s; heartbeat every 10s
Fan-out presence only to playlist room subscribers
Degrade first under load: stop cursor drag broadcast; keep online count only
```

Not source of truth for list order — never persist presence to op log.

### 5.10 Offline merge algorithm (client + server)

**Client:**

```text
on_local_edit(op):
  apply optimistically to local model (optional)
  append to pending_queue with op_id
  if online: submit immediately
  else: persist queue to disk

on_reconnect:
  submit pending_queue as batch with base_seq = last_applied_seq
  on response: replace conflicting local state from server applied ops
  WS subscribe since=max(server_seq)
```

**Server batch handler:**

```text
for op in batch in order:
  if op_id exists: skip (idempotent)
  else: apply with current head; append seq; update head
return all applied ops + current head_seq
```

**Deal-breaker:** merging offline batches without referencing `base_seq` — silent overwrite of intervening server ops.

### 5.11 Data model (sketch)

```sql
CREATE TABLE playlists (
  playlist_id UUID PRIMARY KEY,
  owner_id UUID NOT NULL,
  home_cell TEXT NOT NULL,
  title TEXT,
  meta_version INT NOT NULL DEFAULT 0,
  head_seq BIGINT NOT NULL DEFAULT 0,
  snapshot_seq BIGINT NOT NULL DEFAULT 0,
  snapshot_uri TEXT,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE playlist_ops (
  playlist_id UUID NOT NULL,
  server_seq BIGINT NOT NULL,
  op_id UUID NOT NULL,
  actor_id UUID NOT NULL,
  op_type SMALLINT NOT NULL,
  payload JSONB NOT NULL,
  applied JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (playlist_id, server_seq),
  UNIQUE (playlist_id, op_id)
);

CREATE TABLE playlist_members (
  playlist_id UUID,
  user_id UUID,
  role TEXT NOT NULL,
  membership_version INT NOT NULL,
  PRIMARY KEY (playlist_id, user_id)
);
```

### 5.12 Maintainability

- Op schema versioned (`op_schema_version` in payload).  
- Golden-file tests: concurrent op sequences → expected list order.  
- Property tests: apply(op_log) deterministic across 100 shuffles.  
- Feature flag: CRDT local-apply mode for mobile beta.  
- Chaos: kill op service mid-TX; partition Kafka; flood hot playlist load test.

---

## 6. Wrap-Up

### 6.1 Design summary

A **collaborative playlist editor** treats each shared playlist as an **ordered replicated document**: clients submit typed ops; a **home-cell single writer** assigns **`server_seq`**, applies **OT-lite transforms**, and appends to a durable **op log**; **snapshots** bound recovery and cold-start cost; **WebSocket rooms** push `op_applied` events; **offline clients** batch idempotent ops on reconnect; **presence** is ephemeral and degrades first. Scale by **partitioning on `playlist_id`**, **compaction**, and **hot-key isolation**—not by abandoning total order.

### 6.2 MVP vs later

| MVP | Later |
|-----|-------|
| Server OT-lite + op log | Full CRDT local-first mobile |
| Single-region home cell | Multi-region with explicit failover |
| Metadata LWW | Field-level CRDT for title/desc |
| Audit via op log | User-visible undo/redo |
| Bulk add as multi-insert TX | Streaming import jobs |
| Best-effort presence | Live cursors / drag sync |

### 6.3 Top risks

| Risk | Mitigation |
|------|------------|
| Hot playlist serial bottleneck | Dedicated shard; rate limit; party mode |
| Op log unbounded growth | Snapshot/compaction SLO + alerts |
| Transform surprises UX | `transform_notes` + client toast |
| ACL revoke lag | membership_version in TX |
| Offline batch storms | Chunked submit + 429 backoff |
| 10K+ track snapshot latency | Paginated snapshot API |

### 6.4 Metrics to watch first

Op apply p99, persist→push lag, transform/no-op rate, op log size per playlist, compaction lag, hot playlist QPS, offline batch size on reconnect, ACL denial rate.

### 6.5 45-minute presentation plan

1. Requirements + OT vs CRDT choice (7 min)  
2. Numbers: ingest vs delivery, op log storage (5 min)  
3. Domain model + API + latency budget (8 min)  
4. Concurrent edit + offline merge sequences (10 min)  
5. Snapshot/compaction + scale table (7 min)  
6. Failure walkthrough + security (5 min)  
7. Q&A (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 OT vs CRDT fundamentals

**Q: Why not last-write-wins on the whole playlist JSON?**  
A: Two users editing different parts concurrently would lose one entire edit. LWW is only acceptable for **metadata fields** with explicit `meta_version`, not for ordered list structure where both inserts must survive.

**Q: OT vs CRDT — which for Spotify collaborative playlists?**  
A: **Server OT-lite** for MVP: simpler ACL, single home writer, compact log, easy interview narrative. **CRDT (RGA/LSEQ)** when true offline-first or multi-region multi-writer is required — at cost of metadata growth and harder delete tombstone management. Hybrid: CRDT-style `entry_id`s with server total order.

**Q: Is Google Docs OT the same as this?**  
A: Same family — central or logical ordering with transform — but playlist ops are **discrete structural edits** (insert/delete/move), not character-wise text. Transform table is smaller and testable.

**Q: Can two servers apply ops concurrently for the same playlist?**  
A: **No** in MVP — you need single-writer per playlist (row lock or partition leader). CRDT allows concurrent apply but you still want single ACL writer in practice.

**Q: Vector clocks for playlists?**  
A: Overkill when server assigns total order. Useful if building peer-to-peer sync without central server.

### 7.2 Conflict resolution scenarios

**Q: Alice deletes track B; Bob simultaneously moves track B — outcome?**  
A: Total order wins. If delete is seq N and move is N+1, move is no-op with `transform_note: TARGET_DELETED`. Client Bob removes optimistic UI state on ACK.

**Q: Both insert after the same track offline — order?**  
A: Server processes batch in client order, each transformed against current head. Third party ops interleaved during offline window applied first on reconnect before client batch — client must accept server order via `base_seq` handshake.

**Q: Same song added twice intentionally?**  
A: Allowed — two distinct `entry_id`s with same `track_id`. Deletes target `entry_id`, not `track_id`.

**Q: Move track to position that another user is currently dragging?**  
A: Server serializes moves; last ordered move wins for final position. Live drag is UI-only until drop submits op.

### 7.3 Real-time sync & WebSocket

**Q: Push vs pull for playlist sync?**  
A: **Push** for online editors in room (low fan-out — few collaborators). **Pull** on reconnect, seq gap, or backgrounded app. Do not poll entire 10K list.

**Q: Exactly-once delivery to clients?**  
A: No — at-least-once WS with dedupe by `(playlist_id, server_seq)`. Client applies idempotently.

**Q: What if WS disconnects for 30s during rapid edits?**  
A: On reconnect, `GET /ops?since=last_seq` — might fetch hundreds of ops (~tens of KB), apply in order, then resume WS.

**Q: Should we CRDT-broadcast full state each time?**  
A: **No** — op log bandwidth scales better; full state is O(n) per edit — fatal for 10K tracks.

### 7.4 Offline & mobile

**Q: How long offline is supported?**  
A: Product choice — technically unbounded if op log retained; practically encourage sync within 7d; snapshot + tail must still fit device memory.

**Q: Client optimistic UI offline — rollback pain?**  
A: Show pending ops with marker; reconcile on ACK; if transformed, animate correction — better than blocking local edits.

**Q: Airplane mode bulk add 200 songs?**  
A: Single `BULK_ADD` op or chunked inserts; on sync one TX block allocates seq range — avoids 200 round trips.

### 7.5 Snapshot & storage

**Q: Postgres vs Cassandra for op log?**  
A: Postgres/Citus fine to 100× with partitioning. At 1,000× append-heavy range scans → Cassandra/Scylla keyed by `(playlist_id, server_seq)`.

**Q: Delta Lake analogy for interview?**  
A: Op log ≈ **transaction log**; snapshot ≈ **checkpointed table version**; compaction ≈ **OPTIMIZE/VACUUM** — replay ops after snapshot to reconstruct state. Do not overclaim — playlists are single-writer, not petabyte table.

**Q: How often snapshot 10K-track playlist edited hourly?**  
A: Every 10K ops or 24h; hourly churn might mean 500 ops → snapshot not every hour unless size triggers. Monitor rebuild CPU.

**Q: Can snapshot and op log diverge?**  
A: Never if snapshot_seq ≤ head_seq and tail replay is deterministic. Worker idempotent; fence with playlist lock.

### 7.6 Scale & hot keys

**Q: 500 editors on one viral playlist — what breaks first?**  
A: Single-writer sequencer + WS fan-out. Mitigate: rate limit edits, batch broadcast, read-only viewers default, optional queue with "your op pending" UX.

**Q: Shard key?**  
A: `playlist_id` — natural isolation. User-centric sharding breaks collaboration.

**Q: Compare fan-out to Slack 100K channel?**  
A: Playlist has **far fewer** recipients (2–10 typical). Hot path is **write serialization**, not megafan-out — different bottleneck.

### 7.7 Permissions & security

**Q: Viewer tries WS subscribe?**  
A: Allowed for read sync. Mutations rejected at API with 403; WS still delivers read-only ops.

**Q: Share link leaked?**  
A: Rotate token; viewer vs editor scope; optional password; audit access.

**Q: Malicious 10K op/s spam?**  
A: Rate limits + WAF + per-user quotas; captcha on abuse; playlist owner can lock editing.

### 7.8 Multi-region

**Q: Active-active writes in two regions?**  
A: Avoid for same playlist — split-brain order. Home cell + cross-region RPC; edge WS only.

**Q: Read playlist from replica lagging 5s?**  
A: For editor, route to primary or require `read-your-writes` token. Viewers may tolerate lag with "may be stale" badge.

**Q: Failover home cell RPO?**  
A: Sync replicate op log — RPO ≈ 0 if quorum committed; in-flight un-ACKed ops client retries.

### 7.9 Product & catalog

**Q: Track removed from catalog?**  
A: Entry stays; `available=false`; skip in playback; offer replace UI Phase 2.

**Q: Merge two playlists?**  
A: Out of MVP — implement as bulk insert job reading source snapshot, generating new `entry_id`s, append-only to target.

**Q: Duplicate detection "same album already in list"?**  
A: Product feature — soft warning using catalog metadata; not a sync invariant.

### 7.10 Testing & observability

**Q: How test ordering?**  
A: Concurrent op permutations property test; golden sequences; chaos retries with same `op_id`.

**Q: How detect client-server divergence?**  
A: Optional hash chain: `state_hash` in snapshot metadata; client recomputes after apply; mismatch triggers full resync.

### 7.11 Interviewer traps table

| Trap | Strong answer |
|------|---------------|
| "Store playlist as JSON blob" | Concurrent edits lost; need op log + merge |
| "Client picks final order" | Cheating + divergence; server total order |
| "Use track_id as row key" | Duplicates break; need entry_id |
| "CRDT solves everything free" | Tombstones, metadata growth, ACL still central |
| "WebSocket alone is SoT" | Must persist before ACK; WS is cache |
| "Skip idempotency — UUID enough" | Retries duplicate rows without unique (playlist, op_id) |
| "Snapshot optional" | 10K track cold start replays millions of ops |
| "Broadcast full playlist each edit" | O(n) bandwidth — send ops only |
| "Multi-master for hot playlist" | Split brain; shard + rate limit instead |
| "Presence in op log" | Bloat; ephemeral Redis |
| "LWW for move conflicts" | Wrong UX — both users' intents matter |
| "Kafka before DB commit" | Outbox pattern; never announce uncommitted ops |

### 7.12 Databricks-themed bridges

**Q: How is op log like Delta Lake?**  
A: Both use append-only logs with periodic checkpoints for fast restore. Delta handles parquet files at petabyte scale with optimistic concurrency; playlist op log is simpler single-writer with row-level transforms — analogy for log + checkpoint, not identical concurrency model.

**Q: Exactly-once op processing in workers?**  
A: Idempotent consumers keyed by `(playlist_id, server_seq)`; snapshot worker tracks last compacted seq; DLQ poison ops with schema errors.

**Q: Lineage of playlist state?**  
A: Op log is full lineage; snapshot is derived artifact — similar to table version from history.

---

*End of collaborative playlist editor system design.*
