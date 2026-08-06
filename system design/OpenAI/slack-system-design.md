# System Design: Slack

> **Focus areas:** Workspaces · Channels · Threads · Message ordering · Presence · Fan-out  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved fan-out ownership, honest MVP vs extreme-scale paths

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

Goal: **bound the product**—what Slack-like surface we build, what we defer, and at which scale the design must still hold.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who are the users? | Knowledge workers in companies; multi-tenant SaaS | Everything keyed by `workspace_id` / `team_id` from day 1 |
| F2 | Workspace model? | Org creates a workspace; users join via invite; roles: owner/admin/member/guest | Authz on every channel/message; guest channel allowlists |
| F3 | Channel types? | Public, private, DMs, MPIM (group DM); optional externally shared later | Separate membership graphs; private channel ACL is a deal-breaker if wrong |
| F4 | Core messaging? | Send/edit/delete text; attachments Phase 1.5; emoji reactions; @mentions; unread badges | Append-only message log + soft delete/edit metadata |
| F5 | Threads? | Reply-in-thread; thread unread distinct from channel unread; optional “also send to channel” | Thread = rooted at parent message; separate fan-out cohort |
| F6 | Message ordering guarantee? | Per-channel causal/total order for display; global order across channels **not** required | Per-channel sequence / Lamport-ish server timestamp + channel seq |
| F7 | Realtime delivery? | Messages appear in seconds for online members; offline catch-up on reconnect | WebSocket gateway + backlog sync API |
| F8 | Presence? | Online / away / DND / offline; “last active”; optional “viewing channel” typing indicators | Ephemeral presence store; high churn; do not treat as durable truth |
| F9 | Search? | Full-text search across channels user can access | Async index; authz-filtered query path (Phase 1 hard requirement often) |
| F10 | Notifications? | Mobile/desktop push for mentions, DMs, keywords; respect DND | Notification service + preference engine; not same path as in-app fan-out |
| F11 | Apps / bots / slash commands? | Out of MVP or thin webhook stub | Extensibility hooks; don’t block MVP on Events API |
| F12 | Admin / compliance? | Retention policies, export, eDiscovery later | Soft-delete + retention jobs; immutable audit for admin actions |

**MVP functional scope (lock with interviewer):**

1. Multi-tenant **workspaces** with roles and invites.
2. **Public/private channels**, DMs, MPIMs; join/leave; membership ACL.
3. Send / edit / delete messages; **threads** with parent pointer.
4. **Per-channel total order** for message display; client sync via cursor.
5. **Realtime fan-out** to online members over WebSocket; offline catch-up via history API.
6. **Presence** (online/away/offline) + typing indicators (best-effort).
7. Unread counts / last-read cursors per user×channel (and per thread).
8. Basic rate limits; @channel/@here carefully limited.

**Out of MVP (explicitly defer):**

- Huddles / voice-video
- Externally shared channels (Slack Connect)
- Full Apps Directory / Workflow Builder
- Enterprise Grid multi-workspace org complexity (design hooks: `org_id`)
- End-to-end encryption
- Perfect global presence accuracy

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Message delivery latency (online)? | Feels instant | p50 < 200ms, p99 < 1s end-to-end in-region after persist |
| N2 | Durability? | No lost messages once ACK’d to sender | RPO ≈ 0 for ACK’d messages; at-least-once delivery to clients |
| N3 | Ordering? | Per-channel total order | Server-assigned `channel_id + seq` (or equivalent); clients sort by seq |
| N4 | Availability? | Business-critical collaboration | 99.9%+ messaging control plane; degrade presence/typing first |
| N5 | Consistency? | Read-your-writes for sender; members see same channel order | Single-writer per channel partition; eventual for search/unread aggregates |
| N6 | Multi-region? | Global company | Active-active **gateways**; **home region/cell** for workspace data (single-writer) |
| N7 | Security? | Private channels must not leak | Membership checks on every read/fan-out/search hit |
| N8 | Fan-out fairness? | Large channels must not melt the system | Hybrid fan-out; slow consumers isolated |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Create workspace → invite users → create public channel → members join → messages stream in realtime.
2. Private channel: only members receive fan-out and history.
3. Reply in thread → thread followers + optional channel broadcast (“also send to channel”).
4. User reconnects after laptop sleep → sync from `last_seen_seq` → catch up missed messages.
5. Edit/delete → `message_changed` / `message_deleted` events; history shows edited tombstone.
6. @mention → notification path even if muted channel (per prefs).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click send | Idempotency-Key → one message |
| Offline send | Client queues; flush with idempotency on reconnect |
| Network split mid-publish | Persist first, then fan-out; clients pull gap by seq |
| Very large channel (50K–500K members) | Do **not** push to every socket synchronously; hybrid fan-out (§3.5) |
| Hot channel (launches, incidents) | Partitioned writers / sharded channel log; backpressure |
| Presence flapping (Wi‑Fi blips) | Debounce + grace timeout before offline |
| Unread races (read while new message arrives) | Monotonic `last_read_seq`; UI reconciles |
| User removed from private channel | Immediate ACL revoke; no further fan-out/history |
| Reordering due to multi-DC clocks | Never trust client clocks; server seq is SoT |
| Slow consumer / background tab | Drop to catch-up mode; don’t block channel publish |
| @channel in huge room | Rate-limit + admin gates; expand mentions asynchronously |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Workspaces | 10K | 100K | 1M | 10M |
| MAU | 1M | 10M | 100M | 1B |
| DAU | 200K | 2M | 20M | 200M |
| Peak concurrent WebSocket connections | 100K | 1M | 10M | 100M |
| Messages sent / day | 50M | 500M | 5B | 50B |
| Avg fan-out recipients / message (blended) | 20 | 20 | 25 | 30 |
| Peak message ingest QPS | ~1K | ~10K | ~100K | ~1M |
| Peak **event delivery** ops/s (ingest × online fan-out fraction) | ~10K–50K | ~0.1–0.5M | ~1–5M | ~10–50M+ |
| Channels (total) | 2M | 20M | 200M | 2B |
| Avg channel members | 15 | 15 | 20 | 25 |
| Presence updates / day | ~0.5B | ~5B | ~50B | ~500B |
| Stored messages (retained) | ~10B | ~100B | ~1T | retention-capped |

**What each jump forces:**

- **10×:** Sticky/conn-heavy WS gateways; Redis for presence & routing; Kafka (or equiv) for durable fan-out async; read replicas.
- **100×:** Workspace **cells**; channel-partitioned message log; hybrid fan-out for large channels; unread/mention materialized carefully.
- **1,000×:** Multi-region home cells; connection gateways at edge; cold/hot message tiering; presence gossip/aggregation; per-tenant fairness; search/index fleet is its own product.

### 1.5 Etc. (Constraints & Assumptions)

- **We build messaging + presence**, not the full Slack suite (no huddles MVP).
- **Single primary cloud**, multi-AZ; multi-region DR with workspace home region.
- **Clients:** desktop web + mobile; one protocol family (WS + REST/HTTP sync).
- **Attachments:** object storage pointers in MVP schema even if upload ships Phase 1.5.
- **Compliance retention:** configurable; estimate storage **with retention**, not infinite history for 1B MAU.

**Scope statement:**

> Design a Slack-like system: multi-tenant workspaces, channels (public/private/DM), threaded messages with per-channel ordering, realtime fan-out to online users, offline sync, and best-effort presence—starting at ~200K DAU / 100K concurrent sockets and evolving through 10× / 100× / 1,000× with hybrid fan-out and cell architecture.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Connections

```text
Baseline peak WS connections: 100,000
Per-conn state on gateway: ~10–30 KB (buffers, subs, auth) → ~1–3 GB / 100K
Gateway capacity (evented): often 50K–200K conns / fat node (real-world tune)
→ ~4–8 gateway nodes baseline (N+2), many more at 1000×
```

At **1,000× (100M conns):**

```text
100M × 20 KB ≈ 2 TB RAM across the edge fleet (not a single cluster)
→ geo-sharded connection gateways mandatory
```

### 2.2 Ingest vs delivery (do not conflate)

```text
Baseline messages/day: 50M
≈ 50e6 / 86400 ≈ 580 msg/s average
Peak factor 5–10× → ~3K–6K ingest/s (order-of; table uses ~1K conservative blended peak)
```

**Fan-out amplification:**

```text
If every message were pushed to all members online:
  1K msg/s × 20 recipients ≈ 20K delivery ops/s (baseline blended)

But large channels dominate tails:
  100 msg/s into a 100K-member channel × 30% online ≈ 3M deliveries/s from ONE hot channel
→ hybrid fan-out is not optional past mid-scale
```

Split metrics in interviews:

| Class | Baseline peak (order) | 1,000× (order) |
|-------|------------------------|----------------|
| Message **ingest** (durable write) | ~1K/s | ~1M/s |
| Online **push deliveries** | ~10K–50K/s | ~10M–50M+/s (with hybrid controls) |
| History / sync reads | ~5K–20K/s | ~5M–20M/s |
| Presence updates | ~5K–20K/s | ~5M–20M/s |
| Search index writes (async) | ~1K–5K/s | ~1M–5M/s |

### 2.3 Storage

```text
Avg message size stored: ~500 B–1 KB metadata+text (attachments aside)
Baseline retained messages: 10B × 800 B ≈ 8 TB raw
+ indexes/replicas → tens of TB

1,000× without retention: absurd (petabytes–exabytes)
→ retention policies, cold tier, attach-to-object-store dominate design
```

**Thread storage:** same message table with `thread_ts` / `parent_id`; not a separate DB by default.

### 2.4 Bandwidth

```text
Assume 1 KB on wire per delivery (JSON event)
Baseline 20K deliveries/s × 1 KB ≈ 20 MB/s ≈ ~1.7 TB/day egress (order)
1,000×: terabytes/hour possible → edge termination + binary protocols (MessagePack/Protobuf) help
```

### 2.5 Presence memory

```text
Presence record: ~50–100 B (user_id, status, last_seen, workspace)
1M MAU online fraction 20% → 200K × 100 B = 20 MB (tiny)
1,000×: 200M online × 100 B = 20 GB — still OK if sharded by workspace/cell
```

**Cardinality trap:** “who is viewing this channel” at huge scale → sample / approximate / limit to recent actives; don’t store full matrices forever.

### 2.6 Unread / badge storage

```text
Per user × channel cursor: ~32–64 B
200K DAU × 80 channels ≈ 16M rows ≈ ~1 GB
1,000×: multi-TB cursor tables → shard with workspace; compact cold users
```

---

## 3. High-Level Design

### 3.1 Product / UX surfaces (wireframe)

```text
+--------------------------------------------------------------------------+
| Workspace v | Search                     | Activity | DMs | You [Online] |
+-------------+----------------------------------------+-------------------+
| Channels    | #incident-2026            | Thread   | Members / Pins     |
| # general   |                          |          |                     |
| # eng       | Alice  10:01  We rolled  | Replies  | @alice online       |
| * incident  | back the bad deploy...   | 12       | @bob away           |
|             |                          |          |                     |
| DMs         | Bob  10:02  Checking     | > reply  |                     |
| @ alice     | logs in us-east...       |          |                     |
|             |                          |          |                     |
|             | [ Message #incident... ] |          |                     |
+-------------+----------------------------------------+-------------------+
```

Client maintains: channel subscription set, local message store sorted by `seq`, thread open state, presence map (LRU), `last_read_seq`.

### 3.2 Domain model

```text
Org? (optional Enterprise Grid)
  └── Workspace (team)
        ├── UserMembership (role, status)
        ├── Channel
        │     ├── ChannelMembership (notifications prefs, last_read_seq)
        │     ├── Message[]  (channel_id, seq, ts, body, sender, edited...)
        │     │     └── ThreadReply[]  (same Message table, parent_id / thread_ts)
        │     └── Pins / Bookmarks
        └── DirectChannel / MPIM (synthetic channel types)
```

**Message identity & order:**

| Field | Role |
|-------|------|
| `message_id` | Globally unique ULID/UUID |
| `channel_id` | Partition key |
| `seq` | Monotonic **per channel** (or per channel shard) — **display order SoT** |
| `server_ts` | Wall clock for UI; not sufficient alone for order |
| `client_msg_id` | Idempotency from client |
| `parent_id` / `thread_ts` | Thread root |
| `version` | Edit version; deletes are tombstones |

**Deal-breaker:** ordering by client timestamp or by arrival at different gateways without a channel sequencer.

### 3.3 API / protocol shape

**HTTP (sync / CRUD):**

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/workspaces` | Create workspace |
| GET | `/api/conversations.list` | Channels + DMs for user |
| POST | `/api/conversations.join` | Join public channel |
| GET | `/api/conversations.history` | History by `channel` + cursor/`seq` |
| GET | `/api/conversations.replies` | Thread replies |
| POST | `/api/chat.postMessage` | Send (idempotent) |
| POST | `/api/chat.update` / `delete` | Edit / delete |
| POST | `/api/conversations.mark` | Advance `last_read_seq` |
| GET | `/api/users.list` / presence batch | Roster + presence |

**WebSocket (realtime):**

```text
Client → Server:  subscribe_channel, typing, presence_change, ping
Server → Client:  message, message_changed, message_deleted, reaction,
                  thread_broadcast, presence_change, typing, unread bump
```

**Atomic send (preferred):**

```http
POST /api/chat.postMessage
Idempotency-Key: client_msg_id
{
  "channel": "C012",
  "text": "hello",
  "thread_ts": null,
  "broadcast": false
}
```

Server transactionally:

1. Authz membership  
2. Allocate next `seq` for channel  
3. Insert message row  
4. Outbox event for fan-out + search + notifications  
5. Return `{ ok, message_id, seq, ts }`  

**ACK semantics:** HTTP 200 / WS ack means **durable**. Fan-out is after (or parallel-safe via outbox)—clients who miss push catch up by seq gap.

### 3.4 High-level architecture

```text
                    +----------------------+
                    | Mobile / Web / Desktop|
                    +----------+-----------+
                               |  WSS + HTTPS
                    +----------v-----------+
                    | Edge / LB / TLS      |
                    +----------+-----------+
                               |
              +----------------+----------------+
              v                                 v
     +----------------+                 +----------------+
     | WS Gateway     |                 | API / Sync     |
     | (connections,  |                 | (CRUD, history)|
     |  subscribe)    |                 +--------+-------+
     +--------+-------+                          |
              |  route by user/workspace         |
              v                                  v
     +----------------+                 +----------------+
     | Presence +     |                 | Channel/Msg    |
     | Conn Directory |                 | Service        |
     | (Redis)        |                 +--------+-------+
     +----------------+                          |
                                                 v
                                        +--------+-------+
                                        | Message Log DB |
                                        | (by channel)   |
                                        +--------+-------+
                                                 |
                                        +--------v-------+
                                        | Outbox / Kafka |
                                        +--------+-------+
                         +---------------+-------+---------------+
                         v               v                       v
                  Fan-out Worker   Notification          Search Indexer
                  (online push)    Worker                (async)
                         |
                         v
                  WS Gateway(s) → subscribed sockets
```

### 3.5 Fan-out design (the heart of the interview)

#### Problem

Publishing a message to a channel with **N members** can require up to **N deliveries**. At scale, naïve “query members, write to each inbox, push each socket” dies on large channels and hot keys.

#### Options

| Approach | How it works | Pros | Cons | When |
|----------|--------------|------|------|------|
| **A. Write fan-out (eager)** | On send, push to each member inbox / socket | Fast reads | Write amplification; large channel meltdown | Small channels / DMs |
| **B. Read fan-out (lazy)** | Persist once; readers pull channel log | Simple writes | Higher read cost; slower “push” feel | Huge channels, cold history |
| **C. Hybrid (chosen)** | Small channels eager-push online; large channels: push to **active subscribers** only + others pull on view | Balances cost | Need thresholds + “active” definition | Production Slack-like |
| **D. Per-user inbox everywhere** | Materialize every message into every user’s timeline | Easy unread | Storage explosion | Deal-breaker at Slack scale |

**Choice: Hybrid fan-out**

```text
on_message_persisted(channel_id, msg):
  members = membership_service.get(channel_id)           # cached
  if members.count <= THRESHOLD_SMALL:                  # e.g. 500
      online = conn_directory.lookup(members)
      push(online, msg_event)
  else:
      # large channel
      active = channel_active_viewers(channel_id)         # currently subscribed in WS
      push(active, msg_event)
      # non-viewers: update lightweight unread watermark / badge async
      bump_unread_approx(members - active, channel_id, msg.seq)
```

**Deal-breakers:**

- Eager fan-out to 500K members on every keystroke of load test  
- Storing full message copy per recipient  
- Blocking HTTP send on complete fan-out to all sockets  

**Online vs offline:**

| Recipient state | Path |
|-----------------|------|
| Online + subscribed to channel | WS push event |
| Online but not viewing | Badge/unread bump event (small) or lazy |
| Offline | Durable log only; sync on reconnect via history/cursor |
| Mobile push needed | Notification worker (prefs, mention rules)—separate |

#### Thread fan-out

Thread replies go to:

1. Users who participated / followed the thread  
2. Optionally channel (broadcast) as a summary message with `reply_count` bump  

Do **not** wake every channel member’s main timeline for every nested reply unless broadcast.

### 3.6 Message ordering deep dive

**Requirement:** In a channel, all clients show the same order.

**Mechanism:**

1. Channel (or channel shard) has a **sequencer**: `INCR channel:{id}:seq` in Redis **or** `UPDATE channel_seq` row in DB, in the same TX as insert when using DB sequencer.  
2. Message stored with `(channel_id, seq)` unique.  
3. Clients render sorted by `seq`.  
4. Gaps detected → `conversations.history?after_seq=X`.

**Trade-offs: Redis INCR vs DB sequence**

| | Redis INCR | DB monotonic |
|--|------------|--------------|
| Latency | Very fast | Slightly slower |
| Durability | Risk if msg insert fails after INCR → **seq hole** (OK) or orphan seq | TX atomic with insert |
| Failure mode | Holes acceptable; duplicates not | Cleaner |

**Holes are OK; duplicates are not.** Clients tolerate missing seq by fetching. Reusing seq = corruption.

**Multi-shard channels (extreme hot channels):**

- Rare: shard channel log by hash(time) or sub-partitions with a **merge order** (epoch + local seq)—complex.  
- Prefer: isolate hot channels on dedicated partitions; rate-limit bots; only shard when measured.

**Cross-channel order:** not required. UI “All unreads” merges by `server_ts` approximately.

**Edits/deletes:** do not reorder; emit change events referencing `message_id` + `seq`.

### 3.7 Presence & typing

**Presence is ephemeral and approximate.**

```text
Client heartbeat every 15–30s → WS Gateway → Presence Service
TTL key: presence:{workspace}:{user} = {status, last_seen, conn_count}
Grace: mark offline only after TTL expiry (e.g. 60–90s)
```

**Broadcasting presence:**

| Naïve | Problem |
|-------|---------|
| Notify all workspace members on every change | O(workspace) storm |

**Better:**

- Push presence changes only to users who **share a channel** or have DM / are in same open view  
- Or: clients pull presence for visible member lists  
- Aggregate: workspace-level “online count” as approximate counter  

**Typing indicators:** ephemeral pub/sub to channel active subscribers; 3s TTL; never durable; drop under load.

**Deal-breaker:** durable DB write per typing event.

### 3.8 Unread cursors

```text
channel_member: (user_id, channel_id) → last_read_seq, mention_count, muted...
thread_follow:  (user_id, thread_root_id) → last_read_seq
```

**Badge computation:**

- Exact: `max_seq(channel) - last_read_seq` (with care for tombstones)  
- At huge scale: maintain `unread_count` incremented on fan-out bump, decremented on mark-read (reconcile periodically)

**At-mention:** notification worker parses mentions at persist time; increments `mention_count`; push notify.

### 3.9 Storage choices & trade-offs

| Data | Store | Why |
|------|-------|-----|
| Messages | Cassandra / Scylla / DynamoDB **or** Postgres+partition **or** Kafka+cold | High write, key by channel+seq; wide time ranges |
| Membership | Postgres / strongly consistent store | ACL correctness is sacred |
| Conn directory | Redis Cluster | Hot, ephemeral |
| Presence | Redis | TTL native |
| Unread cursors | Redis + Postgres snapshot **or** sharded SQL | Hot updates |
| Search | OpenSearch/Elastic | Inverted index, authz filter |
| Attachments | Object storage | Blob |
| Outbox / async | Kafka / Pulsar | Decouple persist from delivery |

**Message store choice (interview-ready):**

| Option | Pros | Cons |
|--------|------|------|
| **Cassandra/Scylla (channel_id, seq)** | Excellent write + range scan | Multi-row TX weak; membership elsewhere |
| **DynamoDB** | Managed | Cost/complexity of GSIs; careful keys |
| **Postgres partitioned** | Transactions with sequencer | Vacuum / hot partition pain at extreme |
| **Kafka as log** | Natural stream | Not ideal random history by channel without layering |

**Practical choice:**  

- **Membership + workspace metadata:** Postgres  
- **Message log:** Cassandra/Scylla **or** Postgres early (MVP), migrate when measured  
- **MVP honesty:** Postgres for messages to ~10× if partitioned by `channel_id` hash + time; plan migration path  

**Deal-breaker:** one global Postgres table, unpartitioned, forever.

### 3.10 Caching

| Cache | Data | Invalidation |
|-------|------|--------------|
| Membership cache | channel → member set / bloom | Join/leave events |
| Channel metadata | name, type, topic | Admin updates |
| Conn directory | user → gateway node | Connect/disconnect |
| Recent history | last N messages / channel | On publish |
| Permission | user can_read channel | Membership change |

**Cache stampede:** singleflight on membership for hot channels.

**Security:** never serve history from cache without membership check (or cache **per-user** views carefully—usually check ACL then fetch shared channel cache).

### 3.11 Progressive scale evolution

| Scale | Architecture |
|-------|----------------|
| **1×** | Modular monolith; Postgres messages+membership; Redis presence/conn; WS gateway; sync fan-out worker |
| **10×** | Split WS gateway fleet; Kafka outbox; Redis Cluster; history replicas; hybrid fan-out threshold |
| **100×** | Workspace **cells** (shard by `workspace_id`); message store Cassandra/Scylla; active-viewer tracking; notification service; search fleet |
| **1,000×** | Edge WS PoPs; multi-region home cell per workspace; cold message tier; presence aggregation; dedicated hot-channel partitions; fair multi-tenant admission |

**Multi-region model (clarify “active-active”):**

- **WS/API gateways:** active-active globally (terminate near users)  
- **Workspace data:** single **home cell/region** writer  
- **Cross-region:** async replicas for DR / read-mostly; failover with explicit RPO/RTO  
- **Not default:** multi-writer CRDTs for channel sequences (ordering nightmare)

---

## 4. Architecture Diagram

### 4.1 End-to-end send path

```text
Sender Client                API                 Sequencer+MsgDB           Outbox/Kafka
     |                        |                        |                        |
     | postMessage            |                        |                        |
     |----------------------->| authz + idempotency    |                        |
     |                        |----------------------->|                        |
     |                        |  alloc seq, insert     |                        |
     |                        |  write outbox          |                        |
     |                        |<-----------------------|                        |
     |  200 {id, seq}         |                        |                        |
     |<-----------------------|                        |                        |
     |                        |                        | publish                |
     |                        |                        |----------------------->|
                                                       |
 Fan-out Worker                                        v
     |  consume event
     |  lookup members / active viewers
     |  lookup sockets in Conn Directory
     v
 WS Gateways ---- event ----> Recipient Clients
     |
     +---- Notification Worker ----> Push (mentions/DMs)
     +---- Search Indexer ----> OpenSearch
```

### 4.2 Hybrid fan-out detail

```text
                    +------------ persisted message ------------+
                    |                                           |
                    v                                           v
            |members| <= 500 ?                          |members| > 500 ?
                    |                                           |
                    v                                           v
         push to all online members              push to active subscribers
         (conn directory)                        bump unread for others
                    |                                           |
                    +---------------------+---------------------+
                                          v
                                   WS Gateways
```

### 4.3 Reconnect / catch-up

```text
Client wakes
  → WS connect + auth
  → restore subscriptions
  → for each channel: GET history after_seq=local_max_seq
  → apply events in seq order
  → reconcile presence snapshot for visible users
```

### 4.4 Cell architecture (100×+)

```text
                 Global Directory: workspace_id → home cell
                                   |
                 +-----------------+-----------------+
                 v                 v                 v
              Cell A            Cell B            Cell C
           [API][WS*][PG/     ...                 ...
            Cassandra][Kafka][Redis]
                 |
                 * Edge WS may be global and route events to cell
                   or run per-cell with user affinity
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Durability before ACK:** message row (+ seq) committed before client gets success.  
2. **At-least-once fan-out:** push may duplicate; clients dedupe by `message_id`.  
3. **Per-channel seq monotonic:** never assign the same seq twice; holes OK.  
4. **Authz on every path:** history, push, search hits, notifications.  
5. **Idempotent send:** `(workspace, channel, client_msg_id)` unique.  
6. **Single terminal edit/delete versioning:** CAS on `version`.  
7. **Outbox atomicity:** outbox row in same TX as message insert (SQL) **or** Cassandra + independent reconciliation (inbox checkpoint patterns).  
8. **Membership revoke is urgent:** removed user dropped from conn subscription map quickly.

#### 5.1.2 Preventing data loss

| Risk | Mitigation |
|------|------------|
| Gateway crash after DB commit before push | Outbox/Kafka retry; client gap-fill by seq |
| Fan-out worker crash | Kafka consumer retry; idempotent delivery |
| Dual-write DB + Kafka without outbox | **Forbidden** — use outbox or CDC |
| Disk failure | Quorum replication (RF=3); acks=majority |
| Client offline | Durable channel log is SoT |
| Partial thread write | Single message insert; thread counts updated atomically or asynchronously with reconcile |

#### 5.1.3 Retries & idempotency

| Layer | Policy |
|-------|--------|
| Client send | Retry with same `client_msg_id` |
| API → DB | TX retry on conflict |
| Fan-out consumer | Retry with backoff; DLQ after N; **dedupe** by message_id at gateway |
| Push to socket | If fail, rely on client catch-up (don’t infinite retry block partition) |
| Notifications | At-least-once with dedupe keys |

#### 5.1.4 Rate limiting

| Dimension | Example |
|-----------|---------|
| Per user message RPM | Anti-spam |
| Per channel ingest | Protect hot channels |
| Per workspace egress | Noisy neighbor |
| @channel / @here | Strict quotas |
| WS connect rate | Connect storms |
| Presence / typing | Token-bucket; drop excess |

Algorithms: token bucket + sliding window in Redis; fail closed for write abuse.

#### 5.1.5 Backpressure

- Kafka lag high → shed non-critical events (typing/presence) first  
- Gateway outbound buffer full → disconnect slow client / mark catch-up-only  
- Never block channel sequencer on slow sockets  

#### 5.1.6 Ordering under failure

- Sequencer + durable log in home cell  
- Multi-gateway receive order irrelevant  
- Clients **always** sort by `seq`, not receive time  
- For cross-region read replicas: don’t serve history from lagging replica for active write channel without session consistency (read-your-writes → primary)

### 5.2 Scalability

#### 5.2.1 Scaling connections

- Evented WS servers (Go/Netty/Elixir)  
- Horizontal gateway fleet; user conn registry in Redis: `user → {gateway_id, conn_id}`  
- Consistent hashing optional for gateway affinity; registry lookup is enough  
- Scale out on connection count + CPU; **long connection drain** on deploy  

#### 5.2.2 Scaling message write path

- Partition Kafka by `channel_id` (ordering per channel in pipeline)  
- Message DB partition by `channel_id`  
- Hot channel detection → dedicated workers / rate limits / bot throttling  
- Attachments async: upload to blob, message carries reference  

#### 5.2.3 Scaling fan-out

| Technique | Effect |
|-----------|--------|
| Hybrid push | Caps cost of large channels |
| Batch events per connection | Less syscall/frame overhead |
| Local fan-out on gateway | Group recipients by gateway_id; one RPC per gateway with many user events |
| Mute / highlight prefs | Skip useless pushes |
| Subscription model | Only push to sockets subscribed to channel |

**Gateway-local coalescing:**

```text
Worker → Gateway G1: [ (u1, evt), (u2, evt), ... ]  # same message payload once + recipient list
```

#### 5.2.4 Scaling presence

- Shard Redis by `workspace_id`  
- Debounce updates; coalesce broadcasts  
- Cap typing fan-out to active viewers  
- At 1,000×: regional presence aggregators; lazy pull for member lists  

#### 5.2.5 Storage tiering

```text
Hot (0–90 days): SSD message store / cache
Warm: compressed segments in object storage + index of offsets
Cold/compliance: WORM archive per retention policy
```

Random open of old channel: segment manifest + range fetch—not full-table Parquet scan (Parquet for analytics only).

#### 5.2.6 Parallelization

- Independent channels parallel by nature  
- Thread replies still take channel or thread sequencer (define: replies use channel seq **or** thread-local seq + parent)—pick one and stick  
  - **Common:** all messages (including replies) share **channel seq** so channel history is one ordered log; thread view filters by `thread_ts`  
- Search indexing parallel by channel partitions  
- Unread mark-read batched  

#### 5.2.7 Scale-down / deploy

- WS graceful: stop new conns → wait idle → close with `reconnect_url`  
- Kafka consumers pause partitions cleanly  
- Presence TTLs self-heal  

#### 5.2.8 When to shard (measurement)

Don’t say “at 100× we shard” as dogma. Shard when:

- Sequencer / partition CPU hot  
- Kafka consumer lag SLO breached  
- Membership cache memory per node excessive  
- Blast radius requirements (Enterprise)  
- p99 history read exceeds SLO after tuning  

**Shard key:** `workspace_id` for cells; within cell `channel_id` for message partitions. Huge workspaces may need directory override (shard busy workspace by channel ranges).

### 5.3 Maintainability

#### 5.3.1 Service boundaries

```text
/gateway-ws            # connections, subscribe, heartbeats
/api-sync              # HTTP CRUD + history
/channel-membership    # ACL
/message-service       # post/edit/delete + sequencing
/fanout-worker         # online delivery
/notification-worker   # push/email
/presence-service      # ephemeral status
/search-indexer        # async
/admin-compliance      # retention/export
```

Start modular monolith; split along these seams under pain.

#### 5.3.2 Contracts

- Protobuf/JSON schema for WS events with `event_type` + `event_id`  
- Additive evolution; clients ignore unknown types  
- Idempotency and seq semantics documented as platform invariants  

#### 5.3.3 Observability

| Metric | Why |
|--------|-----|
| Persist latency | ACK SLO |
| Fan-out lag (persist → push) | Realtime SLO |
| Kafka consumer lag | Pipeline health |
| WS conns / gateway | Capacity |
| Slow-consumer disconnects | Backpressure |
| Hot channel ingest QPS | Incident detection |
| Presence update rate | Drop under load intentionally |

Avoid high-cardinality labels (`message_id` on Prometheus)—use traces/exemplars.

#### 5.3.4 Testing

- Ordering tests: concurrent posters → unique seq, total order  
- ACL tests: private channel leakage  
- Chaos: kill fan-out worker → gap-fill works  
- Load: large channel hybrid path; slow consumer  
- Idempotency: duplicate `client_msg_id`  

#### 5.3.5 Operability

- Feature flags for fan-out threshold  
- Per-workspace kill switches  
- “Degraded mode”: persist + history OK, disable typing/presence broadcast  

---

## 6. Wrap-Up

### 6.1 What we designed

A Slack-like collaboration system: **workspaces + channels + threads**, **server-sequenced per-channel ordering**, **durable-before-ACK messaging**, **hybrid fan-out** (eager for small channels / active viewers for large), **WS realtime + cursor catch-up**, **ephemeral presence**, async **notifications/search**, evolving from a modular monolith to **workspace cells** and edge connection fleets as scale grows 10× / 100× / 1,000×.

### 6.2 Decisions to defend

1. **Persist + outbox before ACK; fan-out at-least-once** with client dedupe + seq gap-fill.  
2. **Per-channel `seq` is order SoT**—not client timestamps.  
3. **Hybrid fan-out**—large-channel eager push is a deal-breaker.  
4. **Membership/ACL in strongly consistent store**—never trust cache alone for authz.  
5. **Presence ephemeral**—degrade first under load.  
6. **Threads share channel log** (filter by parent) unless proven otherwise.  
7. **Home-cell single-writer** for workspace data; gateways active-active.  
8. **Separate ingest QPS from delivery ops/s** in estimates.  
9. **Unread cursors** rather than per-user message copies.  
10. **Measurement-driven sharding**, not folklore multipliers alone.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Hot channels | Dedicated partitions, bot limits, hybrid push |
| Fan-out lag | Prefer active-subscriber push; badge async |
| Search authz bugs | Filter on query + indexed ACL versions |
| Multi-region failover | Explicit RPO/RTO; fence old primary |
| Unread drift | Periodic reconcile against max_seq |
| Enterprise retention | Tiered storage + legal hold |

### 6.4 45-minute presentation plan

1. Requirements + scope (6 min)  
2. Numbers: ingest vs fan-out amplification (4 min)  
3. Domain + ordering + API (7 min)  
4. Fan-out hybrid deep dive (10 min)  
5. Presence + unread (4 min)  
6. Reliability invariants + scale/cells (8 min)  
7. Q&A (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Fan-out & realtime

**Q: Push vs pull fan-out?**  
A: Hybrid—push to online/active; pull history for others. Pure push dies on large channels; pure pull feels laggy for DMs.

**Q: How do you fan out one message to 200K online users?**  
A: Don’t. Push to active subscribers; update unread watermarks in bulk for the rest; users opening the channel fetch by seq. Batch by gateway.

**Q: Exactly-once delivery to clients?**  
A: No—at-least-once + idempotent `message_id` dedupe. Exactly-once across mobile/web is unrealistic.

**Q: What if fan-out is delayed 30s?**  
A: Sender already has ACK; recipients gap-fill; alert on lag SLO; shed typing/presence first.

**Q: Should offline users get a per-user inbox write?**  
A: Generally no at Slack scale—channel log + cursor is enough. Exceptions: notification personalized index, not full message copy.

### 7.2 Ordering & consistency

**Q: Why not Lamport clocks alone?**  
A: Need total order per channel for UX; server sequencer is simpler and sufficient in a home-cell single-writer model.

**Q: Seq holes?**  
A: Allowed if allocate-then-insert fails; clients fetch gaps. Duplicates forbidden.

**Q: Vector clocks?**  
A: Overkill for single-writer channel log; useful if you allowed multi-region multi-writer (we don’t by default).

**Q: How do edits interact with order?**  
A: Same `seq`, new `version`; UI in-place update via `message_changed`.

**Q: Thread reply ordering?**  
A: Replies still get channel `seq` (global channel order) and nest under `thread_ts` for thread view sorted by seq/ts.

### 7.3 Presence

**Q: Accurate presence for 1M-user workspace?**  
A: Don’t broadcast all-to-all. Heartbeat + TTL; scoped fan-out; pull for visible lists; approximate aggregates.

**Q: Flapping online/offline?**  
A: Grace period; conn_count on multi-device; only offline when all conns gone + TTL.

**Q: Where to store presence?**  
A: Redis TTL. Not Postgres.

**Q: Typing at scale?**  
A: Active viewers only; rate limit; drop under load; never persist.

### 7.4 Storage & indexing

**Q: Primary key for messages?**  
A: `((channel_id), seq)` or `(channel_id, ts, message_id)` with seq secondary—seq uniqueness is critical.

**Q: Postgres vs Cassandra for messages?**  
A: Postgres for MVP/TX; Cassandra/Scylla for huge write+range at 100×+. Membership stays SQL.

**Q: How does search not leak private channels?**  
A: Index `channel_id` + filter by user’s membership set at query time (or terms-encoded ACL with care). Never trust index alone without authz.

**Q: Soft delete vs hard delete?**  
A: Soft delete/tombstone for sync; hard delete per retention/GDPR with staged purge (DB, search, cache, backups policy).

**Q: Indexes for history?**  
A: Primary range on `(channel_id, seq)`; thread query `(channel_id, thread_ts, seq)`.

### 7.5 Caching, LB, hashing

**Q: Sticky sessions for WS?**  
A: Useful for connection longevity; not required for correctness if conn directory points to current gateway. Rebalancing needs graceful migrate.

**Q: Consistent hashing uses?**  
A: Redis Cluster slots; Kafka partitions by `channel_id`; cell assignment for workspaces; optional gateway affinity.

**Q: Cache membership for fan-out—risk?**  
A: Stale allow → leak or miss. Short TTL + pub/sub invalidation on join/leave; for private channels prefer strong read on change path.

### 7.6 Unread & notifications

**Q: Exact unread at 1,000×?**  
A: Maintain counters with careful incr/decr + periodic reconcile to `max_seq - last_read_seq`.

**Q: Mentions in encrypted-looking text / code blocks?**  
A: Parser rules; prefer structured rich text; document false positives.

**Q: Notification storms from @channel?**  
A: Rate limits, admin-only, expand async, batch push.

### 7.7 Multi-region & cells

**Q: Active-active message writes?**  
A: Avoid for same channel. Home cell single-writer; edge WS forward to home.

**Q: User traveling abroad?**  
A: Connect to nearest edge; RPC to home cell; accept latency or optional regional replicas for history with session consistency caveats.

**Q: Failover home region?**  
A: Fence old primary, promote secondary, update directory, accept RPO on in-flight outbox, reconnect clients.

**Q: Shard by user instead of workspace?**  
A: Bad for channels (shared state). Workspace/cell is natural; split mega-workspaces specially.

### 7.8 Algorithms & data structures

**Q: Data structure for channel membership at 500K users?**  
A: Sharded bitsets / chunked ID lists in object storage + Redis hot set of active; don’t load 500K UUIDs on every message—use active-subscriber set for push.

**Q: Detect gaps in seq?**  
A: Client tracks `max_contiguous_seq`; on event with seq > expected, fetch `[expected, seq)`.

**Q: Idempotency map?**  
A: `(channel_id, client_msg_id) → message_id` with TTL/unique constraint.

**Q: Fan-out recipient grouping?**  
A: `hashmap[gateway_id] → list<conn>`; O(recipients) group then O(gateways) RPCs.

**Q: Rate limit algorithm?**  
A: Token bucket per user/channel; sliding window for RPM analytics.

**Q: Approximate online count?**  
A: HyperLogLog / Redis PFCOUNT for workspace online estimates; exact only for small views.

### 7.9 Reliability drills

**Q: Redis conn directory down?**  
A: Can’t push; still persist; clients poll/sync; degrade realtime; don’t take writes offline unless policy says so.

**Q: Kafka down?**  
A: If outbox in DB, buffer and spill; or synchronous fallback push for small channels with care; search/notify delayed.

**Q: Split brain sequencer?**  
A: Single-writer per channel partition with fencing token / DB leadership; dual sequencers = duplicate seq risk—prevent.

**Q: Poison message crashes consumers?**  
A: DLQ + skip; alert; don’t block partition forever.

### 7.10 Security

**Q: IDOR on `conversations.history`?**  
A: Membership check every call; automated cross-tenant tests.

**Q: WS subscription spoof?**  
A: Server validates membership on subscribe; revalidate periodically / on revoke.

**Q: E2EE?**  
A: Out of scope for classic Slack-like search/fan-out; mention as future conflict with server-side search/notifications.

### 7.11 Product comparison traps

**Q: How is this different from Discord?**  
A: Similar realtime bones; Slack emphasizes workplace ACL, threads+inbox workflows, search/compliance; Discord emphasizes huge community guilds/voice—fan-out patterns lean even harder hybrid/lazy.

**Q: How is this different from SMS/WhatsApp?**  
A: Smaller fan-out (1:1 / small groups), different trust model; Slack’s large channels + workspace tenancy dominate architecture.

**Q: Why not use only Firebase/pub-sub?**  
A: ACL, ordering, large-channel economics, compliance, multi-region cells—need first-party control planes.

### 7.12 Extra interviewer traps (high value)

- What is durable before the sender sees a checkmark?  
- Can you lose messages if fan-out fails?  
- How do you handle a client that receives seq 10 then seq 12?  
- How do you revoke a user from a private channel in under a second?  
- Why is per-user inbox materialization dangerous?  
- How do you keep presence from dominating cluster CPU?  
- When does hybrid fan-out threshold get tuned?  
- How do bots/integrations authenticate and rate-limit?  
- How do you migrate a workspace to another cell?  
- How do you prevent high-cardinality metrics from melting Prometheus?  
- How do slow consumers affect channel latency for everyone? (They must not.)  
- How do you sync mobile after 8 hours offline without downloading everything?  
- How do shared/external channels (Slack Connect) break your shard assumptions?  
- How do you test ordering under concurrent publishers?  
- What fails first under load—and what do you degrade intentionally?

---

## Appendix A — Example schemas

```sql
-- Strongly consistent metadata (Postgres)
CREATE TABLE workspaces (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  home_cell TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspace_members (
  workspace_id UUID NOT NULL,
  user_id UUID NOT NULL,
  role TEXT NOT NULL, -- owner|admin|member|guest
  status TEXT NOT NULL DEFAULT 'active',
  PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE channels (
  id UUID PRIMARY KEY,
  workspace_id UUID NOT NULL,
  type TEXT NOT NULL, -- public|private|im|mpim
  name TEXT,
  is_archived BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX channels_workspace ON channels (workspace_id);

CREATE TABLE channel_members (
  channel_id UUID NOT NULL,
  user_id UUID NOT NULL,
  last_read_seq BIGINT NOT NULL DEFAULT 0,
  mention_count INT NOT NULL DEFAULT 0,
  muted BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (channel_id, user_id)
);

-- Idempotency for sends
CREATE TABLE client_msg_dedup (
  channel_id UUID NOT NULL,
  client_msg_id UUID NOT NULL,
  message_id UUID NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (channel_id, client_msg_id)
);
```

```cql
-- Example Cassandra message log
CREATE TABLE messages (
  channel_id uuid,
  seq bigint,
  message_id uuid,
  user_id uuid,
  thread_ts bigint,      -- 0 if top-level; else parent ts/id mapping
  body text,
  attrs map<text, text>, -- edit version, deleted, blocks json ref...
  server_ts timestamp,
  PRIMARY KEY ((channel_id), seq)
) WITH CLUSTERING ORDER BY (seq ASC);
```

```sql
-- Outbox (if messages also in Postgres MVP)
CREATE TABLE message_outbox (
  id BIGSERIAL PRIMARY KEY,
  channel_id UUID NOT NULL,
  message_id UUID NOT NULL,
  seq BIGINT NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at TIMESTAMPTZ
);
```

## Appendix B — Event envelope

```json
{
  "event_id": "evt_01J...",
  "type": "message",
  "workspace_id": "T...",
  "channel_id": "C...",
  "seq": 184422,
  "message_id": "M...",
  "server_ts": 1765000000.0123,
  "body": { "text": "hello", "user": "U..." },
  "thread_ts": null
}
```

Clients dedupe on `event_id` / `message_id` and sort on `seq`.

## Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | WS gateway, API, Postgres, Redis presence/conn, durable-before-ACK send, history cursor sync |
| 10× | Kafka/outbox, hybrid fan-out threshold, gateway fleet HPA, rate limits, search indexer |
| 100× | Workspace cells, scalable message log (Cassandra/Scylla etc.), gateway-local coalesced push, unread reconcile jobs |
| 1,000× | Edge PoPs, multi-region home cells + DR runbooks, cold tier, presence aggregation, hot-channel isolation, tenant fairness |

## Appendix D — Glossary

| Term | Meaning |
|------|---------|
| Workspace / team | Tenant boundary for users/channels |
| Channel seq | Monotonic per-channel order token |
| Hybrid fan-out | Push to small/online-active sets; others pull |
| Conn directory | user → gateway/conn mapping |
| Outbox | Transactional event publication pattern |
| Home cell | Single-writer shard for a workspace |
| Thread_ts | Root identifier for a thread |
| At-least-once | Delivery may duplicate; dedupe required |
| Active subscriber | Socket currently subscribed to channel topic |

## Appendix E — Estimation cheat-sheet (correctness)

```text
Ingest QPS ≠ delivery QPS
delivery ≈ ingest × online_recipients (with hybrid caps)

Connections memory ≈ conns × 10–30 KB  (fleet-wide)

Presence memory is usually small; presence *broadcast* is the cost center

Storage without retention at 1,000× is not meaningful—always pair with retention

Large channel example:
  50 msg/s × 100K members × 20% online = 1M pushes/s if naïve
  → hybrid reduces to ~active_viewers (e.g. 500–5,000) per message
```

---

*End of design doc. Open with §1 scope questions; whiteboard §3.5 fan-out + §3.6 ordering; close with invariants in §5.1 and traps in §7.*
