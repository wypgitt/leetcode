# System Design: Messenger / WhatsApp Chat

> **Focus areas:** Realtime delivery · Message ordering · 1:1 & groups · Offline delivery · Multi-device sync · End-to-end encryption hooks  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split connection/messaging/sync planes, explicit ordering & inbox semantics, deal-breakers for “global total order for all chats” fantasies  
> **Interview theme:** Classic Meta messaging — persistent connections, per-conversation ordering, durable offline queues, group fan-out, and sync across devices  
> **Company flavor:** Meta — Messenger + WhatsApp DNA: connection gateways, chat servers, message stores, receipt/presence, E2EE as product constraint (WhatsApp) vs optional (Messenger evolution)

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

Goal: **bound the product**—a global **chat system** supporting 1:1 and group messaging with realtime delivery when online, durable offline queues, multi-device sync, delivery/read receipts, and clear ordering guarantees **per conversation**.

### 1.0 What this is / is not

| Dimension | **Messenger/WhatsApp chat (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Deliver messages between users/devices | News Feed / social graph product |
| Success | Fast, reliable, correctly ordered chats | Global search analytics warehouse |
| Connection | Long-lived WebSocket/TCP sessions | Pure request/response REST only |
| Hard problem | Offline + multi-device + group fan-out | ML ranking |
| Crypto | E2EE constraints (WhatsApp-style) affect server visibility | Designing Signal protocol from scratch (hooks) |

**Scope statement:** Design a WhatsApp/Messenger-class chat: realtime, ordering, groups, offline delivery, multi-device sync—at progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Chat types? | 1:1 and groups (size cap e.g. 256–1024) | Conversation entity; membership |
| F2 | Realtime? | Yes — messages appear live | Persistent connections / push |
| F3 | Offline? | Queue until device online; push notify | Durable inbox / mailbox per user/device |
| F4 | Ordering? | Per-conversation causal/total order | Monotonic seq per chat |
| F5 | Multi-device? | Phone + web/desktop; sync history | Device registry; sync protocol |
| F6 | Receipts? | Sent / delivered / read (product-dependent) | Receipt events; privacy settings |
| F7 | Media? | Images/video/voice notes via blob URLs | Chunk upload + CDN; message carries pointer |
| F8 | Presence? | Online/last-seen (privacy controls) | Presence service; ephemeral |
| F9 | E2EE? | WhatsApp: yes for content; server metadata OK | Server stores ciphertext; fan-out sealed |
| F10 | Edit/delete? | Delete for me / for everyone; edit window | Tombstones; sync mutations |
| F11 | Push notifications? | Mobile push when offline | APNs/FCM; not chat SoT |
| F12 | Search history? | Local device search MVP; server optional | Client index; server if not E2EE body |

**MVP functional scope:**

1. Create/open **1:1 conversation**; send text message; receive in realtime if online.  
2. **Group chat** with membership add/remove; fan-out to members.  
3. **Per-conversation sequence numbers** for ordering and sync.  
4. **Offline mailbox**: durable store until ACK from device.  
5. **Multi-device**: each device has inbox cursor; sync catch-up API.  
6. Delivery receipts; read receipts (optional/privacy).  
7. Media: upload blob → send message with `media_id`.  
8. Push notification wake-up when no active connection.  
9. Basic presence (online/offline) with privacy flags.

**Out of MVP:**

- Channels / broadcast lists with millions (design hook: different fan-out)  
- Full voice/video WebRTC SFU design (mention separate)  
- Perfect global cross-chat total order  
- Server-side plaintext search under strict E2EE  
- Payments / business API deep dive  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Send→deliver online | Feels instant | p50 < 100–200ms same region; p99 < 500ms–1s |
| N2 | Durability | No lost message after server ACK | Multi-AZ message log/store |
| N3 | Ordering | Correct in a chat | Monotonic seq; client reorder buffer |
| N4 | Offline RPO | None after ACK | Durable before ACK to sender |
| N5 | Availability | Critical social infra | 99.9%+; degrade receipts/presence first |
| N6 | Connection scale | Huge concurrent sockets | Gateway fleets; sticky sessions |
| N7 | Group fan-out | Bounded group size MVP | Async fan-out; no sync to 10K |
| N8 | Privacy | E2EE product constraints | Ciphertext at rest; minimal metadata |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Alice sends to Bob (both online) → gateway → chat service → Bob’s connection → delivered receipt → Alice UI ticks.  
2. Bob offline → message durable in Bob’s mailbox → FCM wake → Bob connects → sync pull → ACK → delivered.  
3. Group of 50 → Alice sends → fan-out to 49 mailboxes/connections.  
4. Alice phone + desktop → both receive via per-device sync cursors.  
5. Alice deletes-for-everyone → mutation message with seq; devices hide.  
6. Image: upload media → send message pointing to media → receivers fetch blob.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-send (retry) | Client `msg_id` idempotency → one seq |
| Device ACK lost | At-least-once deliver; client dedup by `msg_id` |
| Gateway dies | Client reconnects; resume sync from cursor |
| Reorder on network | Client buffer by seq; gap fill via sync API |
| Group member removed | Membership version; don’t deliver new after remove |
| Huge group (over cap) | Reject or migrate to channels model |
| Clock skew | Server-assigned seq/timestamp; don’t trust client for order |
| E2EE key change | Sender encrypts per device keys; server opaque |
| Push delayed | Connection sync is SoT; push is hint |
| Read receipt disabled | Don’t emit read events |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 100M | 1B | WhatsApp-class | extreme |
| Peak concurrent connections | 20M | 200M | 2B | multi-B |
| Messages sent /s (peak) | 200K | 2M | 20M | 200M |
| Avg recipients / message | ~1.3 (mix 1:1 + groups) | ~1.5 | ~1.5–2 | fan-out heavy |
| Delivery events /s | ~300K | 3M | 30M | 300M |
| Group size cap | 256 | 512 | 1024 | channels separate |
| Devices / user (avg) | 1.3 | 1.5 | 1.5–2 | 2+ |
| Mailbox write amplification | msgs × recipients × devices | ×10 | cells | cells |
| History stored | retention / user | huge | tiered | cold tier |
| Presence updates /s | tens of M | huge | sampled / gossip | regional |

**What each jump forces:**

- **10×:** Connection gateway tier; sharded chat servers by `conversation_id`; durable mailbox.  
- **100×:** User/conversation cells; separate receipt pipeline; media edge; E2EE device fan-out costs.  
- **1,000×:** Regional fabrics; group fan-out via membership multicast trees; cold history; presence gossip/approximate.

### 1.5 Etc. (Constraints & Assumptions)

- **Ordering is per conversation**, not global across all users.  
- Push notifications are **unreliable hints**; sync protocol is authoritative.  
- WhatsApp-style **E2EE** means servers store ciphertext; metadata (routing, timestamps) still visible — design for both “E2EE on” and “server-assist” Messenger modes.  
- Voice/video calls are a sibling system; chat may signal call invites only.  
- Meta flavor: **mqtt/websocket gateways**, chatd-like session layers, **mailbox**, **receipt** side channel.

**Scope statement to repeat back:**

> Design a Messenger/WhatsApp-class chat system with persistent connections, per-conversation sequencing, durable offline mailboxes, group fan-out within size caps, multi-device sync cursors, receipts/presence, and progressive scale—without claiming a single global total order or sync fan-out to unbounded groups on the send path.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak (order) | 10× | Store / plane |
|-------|------|------------------------|-----|---------------|
| **Connections** | Concurrent sockets | ~20M | ~200M | Gateway fleets |
| **Message writes** | Durable append | ~200K/s | ~2M/s | Message log / DB |
| **Fan-out delivers** | To recipients/devices | ~300K–1M/s | ×10 | Mailbox + push |
| **Sync pulls** | Catch-up on reconnect | spiky | ×10 | Mailbox read |
| **Receipts** | Delivered/read | ≥ message rate | ×10 | Receipt store/bus |
| **Presence** | Online flips | huge, coalesced | ×10 | Ephemeral cache |
| **Media uploads** | Blob puts | fraction of msgs | ×10 | Object store |

**Anti-pattern:** one “message QPS” that ignores fan-out × devices × receipts.

### 2.2 Connection memory math

```text
Assume 20M concurrent connections
Per connection state: 10–50 KB (buffers, session meta) — use 20 KB
Memory ≈ 20M × 20 KB = 400 TB? WAIT — that's wrong if naively one box.

Per gateway process:
  200K conns × 20 KB = 4 GB RAM (order)
Gateways needed ≈ 20M / 200K = 100 gateways (baseline)
10× → ~1,000 gateways; 100× → tens of thousands — regional cells

Always shard connections across gateway fleets; sticky user→gateway via conn registry.
```

### 2.3 Message + fan-out math

```text
Peak sends: 200,000 msg/s
Avg recipients R ≈ 1.5 (1:1 dominant + some groups)
Avg devices D ≈ 1.3
Mailbox writes ≈ 200K × 1.5 × 1.3 ≈ 390K/s

If large groups common, R rises — enforce group caps; channels different design.

Payload avg 200 bytes text ciphertext + meta 100 bytes ≈ 300 B
Ingress: 200K × 300 B ≈ 60 MB/s (modest)
Fan-out egress online: similar order × recipients
Media dominates bandwidth separately.
```

### 2.4 Storage

```text
200K msg/s × 300 B ≈ 60 MB/s ≈ 5.2 TB/day raw messages
× 365 ≈ ~1.9 PB/year before replication/indexes
Multi-device copies: prefer **one conversation log** + per-device cursors
  NOT full duplicate payload per device
Mailbox for offline: pointer/seq ranges, not second full copy when possible
Retention: WhatsApp-like device-primary history + server limited; Messenger may keep longer — lock with interviewer
```

### 2.5 Group amplification

```text
Group size G=256, message to group:
  fan-out ≤ 255 device-inbox notifications
At 1% of messages being max-size groups, amplification spikes — monitor
Deal-breaker: allow G=1M “group” with sync create-path fan-out
```

### 2.6 Sync storm on reconnect

```text
Outage 5 minutes, 20M users reconnect:
  Sync QPS spike → must rate-limit, backoff, serve cursors from caches
  Design: exponential client backoff + gateway admission
```

### 2.7 Progressive BOTE summary

| Scale | Conns | Msg/s | Mailbox writes/s | Gateways (order) |
|-------|-------|-------|------------------|------------------|
| Baseline | 20M | 200K | ~400K | ~100 |
| 10× | 200M | 2M | ~4M | ~1K |
| 100× | 2B | 20M | cells | many cells |
| 1,000× | extreme | 200M | geo fabric | POP + cells |

### 2.8 Memory footprints (gateways + presence)

```text
Per WS connection: 2–10KB kernel+app (budget 4KB avg carefully)
20M conns × 4KB = 80GB across gateway fleet — sticky map user→gateway in Redis/mem
Presence entries: user → {status, last_seen, device_set} ~64–128B
  100M online × 128B ≈ 12.8GB — sharded presence

Group fanout state: membership version vectors per conversation
```

### 2.9 Partition counts

```text
Conversation log: shard by conversation_id; partitions/DB shards 1K→50K
Mailbox/inbox: shard by user_id
Kafka: topics messages by conversation_id hash; receipts coalesced topic by user_id
Gateway registry: consistent hash user_id → gateway set
```

### 2.10 Amplification & naive costs

| Naive | Cost | Fix |
|-------|------|-----|
| Per-receipt push no coalesce | × readers | Coalesce/batch |
| Large group sync fanout on send path | latency | Async fanout workers |
| Store media in message row | DB bloat | Blob + pointer |
| Full history sync every reconnect | storm | Cursor delta |
| Global total order all chats | impossible | Per-conversation seq |

### 2.11 E2EE fanout math (WhatsApp flavor)

```text
Send to device list size D (multi-device):
  server stores ciphertext envelopes per device or fanout copies
  server cannot read body — spam signals from metadata/graph only
Group: sender keys / sender-key distribution reduces per-member encrypt cost on clients
```

**Pitch:** “Chat is connection scale + per-conversation ordering + durable mailbox. Fanout async; sync by cursor; receipts coalesced.”


---

## 3. High-Level Design

### 3.1 APIs / protocol

Realtime is typically a binary/JSON protocol over WebSocket/MQTT. REST for auth, history backfill, media.

#### 3.1.1 Send message (logical)

```text
Client → SEND {
  client_msg_id,
  conversation_id,
  type: text|media|control,
  ciphertext / body,
  media_id?,
  timestamp_client?
}
Server → ACK {
  client_msg_id,
  server_msg_id,
  seq,
  server_ts
}
```

#### 3.1.2 Sync / catch-up

```http
GET /v1/sync?device_id=&conversations=*&since_seq_map=
→ {
  "updates": [
    {"conversation_id":"c1","seq":101,"msg":{...}},
    {"conversation_id":"c1","seq":102,"type":"receipt","...":...}
  ],
  "new_cursors": {"c1": 102}
}
```

#### 3.1.3 Create group

```http
POST /v1/conversations
{"type":"group","title":"Trip","member_ids":["u1","u2",...]}
→ {"conversation_id":"g_...","membership_version":1}
```

#### 3.1.4 Receipts

```text
RECEIPT { conversation_id, seq_upto, kind: delivered|read, device_id }
```

### 3.2 Core data model / schema

**conversations**

| Column | Type | Notes |
|--------|------|-------|
| conversation_id | id | PK |
| type | 1:1 / group | |
| created_at | ts | |
| membership_version | int | bump on change |

**members**

| Column | Type | Notes |
|--------|------|-------|
| conversation_id | id | PK part |
| user_id | id | PK part |
| role | admin/member | |
| joined_at | ts | |
| muted | bool | |

**messages** (conversation log)

| Column | Type | Notes |
|--------|------|-------|
| conversation_id | id | shard key |
| seq | i64 | monotonic per chat |
| server_msg_id | id | |
| client_msg_id | id | idempotency |
| sender_id | id | |
| kind | text/media/control | |
| payload | bytes | ciphertext or body |
| server_ts | ts | |
| deleted | bool | |

**devices**

| Column | Type | Notes |
|--------|------|-------|
| user_id | id | |
| device_id | id | |
| push_token | str | |
| last_cursor_map | ref | per-conv seq ACK’d |
| last_seen | ts | |

**mailbox / inbox** (offline pending)

| Column | Type | Notes |
|--------|------|-------|
| user_id | id | shard |
| device_id | id | optional per-device |
| conversation_id | id | |
| seq | i64 | |
| payload_ref | | pointer into message log |

**Why:** single append-only **conversation log** is SoT; devices track cursors; mailbox accelerates offline delivery without N full copies.

### 3.3 Why X over Y

| Decision | Choose | Over | Why | Deal-breaker if wrong |
|----------|--------|------|-----|------------------------|
| Order key | **Per-chat seq** | Global Lamport only | UX order in thread | Global total order across chats |
| Connections | **Gateway fleets + registry** | One mega server | Horizontal sockets | Single box 20M conns |
| Offline | **Durable log + mailbox** | Only in-memory queue | Process restart loses msgs | RAM queue as SoT |
| Groups | **Async fan-out + size cap** | Sync HTTP loop | Latency/amplification | Unbounded group push |
| Multi-device | **Cursors on shared log** | Copy all msgs per device | Storage | Duplicate PB×devices |
| Push | **Hint** | SoT | Unreliable carriers | Rely on FCM for durability |
| E2EE | **Opaque payload** | Server plaintext | Product | Server search fantasy under E2EE |
| Receipts | **Side channel / soft** | Block send path | Volume | Sync receipt write in send critical path |

### 3.4 Component overview

1. **Client** — encrypt (if E2EE), local DB, reconnect/sync.  
2. **Connection Gateway** — terminate WS/MQTT; auth; route.  
3. **Presence Service** — online status; last-seen.  
4. **Chat / Conversation Service** — allocate seq; append log.  
5. **Message Store** — durable conversation partitions.  
6. **Fan-out / Delivery Service** — to online conns + mailboxes.  
7. **Device Registry & Sync** — cursors; catch-up.  
8. **Push Service** — APNs/FCM.  
9. **Media Service + CDN** — blobs.  
10. **Receipt Service** — delivered/read aggregation.  
11. **Membership Service** — group graph.  
12. **Kafka** — async fan-out, receipts, analytics.

### 3.5 End-to-end flows

**1:1 online:**

```text
Alice GW → ChatService.allocate_seq + append(log)
        → ACK Alice (server_msg_id, seq)
        → lookup Bob devices/conns
        → if online: push frame to Bob GW
        → else: mailbox + push notify
        → on Bob ACK: receipt → Alice
```

**Group:**

```text
append once to conversation log
async fan-out tasks for each member (paged)
membership_version checked so removed users skip
```

**Reconnect sync:**

```text
device presents cursors per conversation (or user-level watermark)
SyncService reads log ranges > cursor
streams updates until caught up
device ACKs new cursors
```

### 3.6 Consistency model

| Object | Model | Notes |
|--------|-------|-------|
| Message persist | Durable before sender ACK (typical) | Product choice |
| Conversation order | Total order per conversation_id via seq | Gaps repaired |
| Cross-chat order | None | |
| Delivery receipts | Eventual | Coalesce |
| Presence | Ephemeral eventual | Privacy trimmed |
| Group membership | Versioned | Fence fanout |

**Deal-breaker:** claiming global causal order across all conversations.

### 3.7 Protocol edge cases

| Case | Behavior |
|------|----------|
| Duplicate client_msg_id | Same server_msg_id |
| Gap in seq | Client fetch repair |
| Gateway death | Reconnect other GW; resume cursor |
| Member removed | Membership version rejects |
| Offline multi-device | Per-device cursor / mailbox |
| Unsend | Tombstone + revoke push best-effort |
| E2EE key missing | Client error; server opaque |

### 3.8 Schema indexes

```text
messages: PK(conversation_id, seq); UNIQUE(sender_id, client_msg_id)
mailboxes: (user_id, ts, conversation_id, seq)
memberships: (conversation_id, user_id) + version
devices: (user_id, device_id)
receipts: coalesced (conversation_id, user_id, max_seq_delivered/read)
```

### 3.9 Why X over Y expanded

| Topic | Prefer | Avoid |
|-------|--------|-------|
| Conn | WS/MQTT long-lived | Pure short poll at scale |
| Store | Conv log + mailbox | Only one or the other extreme |
| Order | Server seq per chat | Client timestamps |
| Groups | Async fanout | Sync HTTP to all members |
| Media | Blob+CDN | Inline bytes |
| E2EE | Opaque payloads | Server search of body (unless product) |

### 3.10 HLD pitch

> “Gateways hold sockets; chat service assigns seq, persists conversation log, enqueues fanout to member mailboxes/devices; online push via gateway registry; offline sync by cursor. Receipts coalesced. E2EE optional opacity.”


---

## 4. Architecture Diagram

```text
     +-------------+       +-------------+
     |  Mobile App |       |  Web/Desktop|
     +------+------+       +------+------+
            | WS/MQTT             |
            v                     v
     +-----------------------------------+
     |     Connection Gateway Fleet      |
     |  (sticky sessions, TLS terminate) |
     +---------------+-------------------+
                     |
         +-----------+-----------+
         |                       |
         v                       v
 +---------------+      +------------------+
 | Presence Svc  |      |  Chat Service    |
 +---------------+      |  seq + append    |
                        +--------+---------+
                                 |
                                 v
                        +------------------+
                        | Conversation Log |
                        | shard(conv_id)   |
                        +--------+---------+
                                 |
                                 v
                        +------------------+
                        | Delivery / Fanout|
                        +--------+---------+
                   +-----+--------+--------+
                   |              |        |
                   v              v        v
            +-----------+  +---------+  +------+
            | Mailbox   |  | Online  |  | Push |
            | per user  |  | push GW |  | APNs |
            +-----------+  +---------+  +------+
                   |
                   v
            +------------------+
            | Sync on reconnect|
            +------------------+

 Cross-cutting: Device Registry, Membership, Media/CDN,
                Receipt pipeline, E2EE key directory (opaque),
                Home cell / region routing
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Durability before sender ACK** — after ACK, message is in conversation log (multi-AZ).  
2. **Per-conversation seq monotonic** — unique seq per chat; no reuse.  
3. **Idempotent send** on `client_msg_id` (and sender).  
4. **At-least-once delivery to devices**; **exactly-once UX** via client dedup.  
5. **Membership version** gates group delivery.  
6. **Push is not durable SoT**.  
7. **Cursor advance only after durable client persist** (client responsibility) / server mailbox drain ACK.

#### 5.1.2 Ordering & gaps

```text
Client receive path:
  expect seq = last+1
  if gap: buffer out-of-order; request sync fill
  if duplicate seq/msg_id: ignore
```

Server never claims global order across conversations.

#### 5.1.3 Exactly-once myths

| Layer | Reality |
|-------|---------|
| Network | At-least-once |
| Server log | Idempotent append on client_msg_id |
| Device UX | Dedup → appears once |

**Deal-breaker:** promising end-to-end exactly-once without client dedup story.

#### 5.1.4 Gateway failure

- Conn registry removes session.  
- Client reconnects to any gateway; sync from cursors.  
- In-flight frames may repeat → dedup.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Mailbox lag | More deliverers; partition hot users |
| 10× | Reconnect storms | Admission control; jittered backoff |
| 100× | Hot group | Async fan-out; shard membership; cap size |
| 1,000× | Cross-region latency | Home region for conv; regional gateways |

#### 5.1.6 Retries & idempotency

```text
client_msg_id unique per sender
Fanout tasks idempotent on (user_id, conversation_id, seq)
Push retry with backoff; mailbox is source of truth
```

#### 5.1.7 Data-loss prevention

1. ACK to sender only after durable log write (Meta-favored interview answer).  
2. Multi-AZ store; replay fanout from log.  
3. Media checksum before message references.  
4. Tombstones for deletes.

#### 5.1.8 Consistency under partition

```text
Two writers same conversation without leader → duplicate seq risk → single seq allocator / spool per conv shard
Gateway split: client reconnects; no dual active seq
Cross-region friends: home conversation region or CRDT-lite — MVP single home per conversation
```

### 5.2 Scalability

#### 5.2.1 Sharding keys

| Entity | Shard key |
|--------|-----------|
| Conversation log | `conversation_id` |
| User mailbox | `user_id` |
| Connections | gateway by sticky `user_id` / random + registry |
| Membership | `conversation_id` |

**1:1 conversation_id:** canonical pair `min(u1,u2)|max(u1,u2)` or allocated id.

#### 5.2.2 Online delivery path

```text
deliver(msg, recipient):
  sessions = conn_registry.lookup(recipient)
  if sessions:
    for s in sessions: gateway_push(s, msg)
  else:
    mailbox.enqueue(recipient, msg_ref)
    push_notify(recipient)
```

Multi-device: deliver to all active sessions; each device maintains own cursor.

#### 5.2.3 Group fan-out

```text
on_group_message(conv, msg):
  members = membership.list(conv)  # cached
  for page in members.pages():
    fanout_queue.publish(page, msg_ref)
```

Optimizations at scale:

- **Broadcast trees** within cell.  
- **Copy-on-write membership** snapshots with version.  
- Split mega-groups into **channels** (followers pull / different product).

#### 5.2.4 Sync protocol

Watermarks:

```text
device_cursors[conv_id] = last_acked_seq
on_sync: read (cursor, latest] from log
large backlog: paginate; priority recent convs
```

**Session resume:** optional `since_token` for stream.

#### 5.2.5 Receipts & presence at scale

- Receipts coalesced (`delivered_upto seq`).  
- Presence: sticky online with heartbeat; last-seen delayed; privacy flags; **don’t** write DB every heartbeat — ephemeral store + sample.

#### 5.2.6 E2EE fan-out (WhatsApp flavor)

```text
Sender fetches device list + pubkeys for recipients
Encrypts per device (or sender keys / channel keys for groups — protocol detail)
Server routes opaque blobs to device inboxes
Server cannot read body; still sees routing metadata
```

Group E2EE: sender keys / chain keys — mention as protocol layer; infra still sequences envelopes.

#### 5.2.7 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Gateway fleets; sharded logs; mailbox; push |
| →100× | Cells; receipt pipeline; media edge; membership cache |
| →1,000× | Regional fabrics; channel model for huge audiences; approx presence; cold history tier |

#### 5.2.8 Hot keys

| Hot key | Fix |
|---------|-----|
| Huge group conversation_id | Fanout shards; slow-mode rate limit |
| Celebrity 1:1? rare | Still per-conv seq OK |
| Receipt storm | Coalesce |

#### 5.2.9 Cache hierarchy

```text
Gateway local: recent conv sessions
Redis: presence, gateway map, rate limits
Message store: primary
CDN: media
```

#### 5.2.10 Backpressure

```text
Fanout lag → slow sender (ack delay) or group slow-mode
Reconnect storm → admission control + client backoff
```

#### 5.2.11 Path evolution

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Conn | more GW | cells | POP GW |
| Send | sharded seq | conv homes | geo fabric |
| Sync | cursor caches | rate limit | hierarchical |
| Receipts | coalesce | sample presence | privacy trim |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
group_max_size: 256
ack_timeout_ms: 5000
mailbox_retain_days: 30
sync_page_size: 200
presence_heartbeat_s: 30
e2ee_required: true|false
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `conn_gauge` | Capacity |
| `send_qps` / `send_p99` | UX |
| `fanout_lag` | Delivery health |
| `mailbox_depth` | Offline backlog |
| `sync_lag_seconds` | Reconnect health |
| `gap_fill_rate` | Ordering issues |
| `push_fail_rate` | Wake-ups |
| `hot_conversation_qps` | Shard balance |

#### 5.3.3 Testing

- Idempotent send fuzz.  
- Reorder/gap fill tests.  
- Gateway kill → reconnect sync.  
- Group membership races.  
- E2EE device add/remove.  
- Chaos: drop ACKs, duplicate delivers.

#### 5.3.4 Safe evolution

Phase 1: 1:1 + seq + mailbox.  
Phase 2: groups + receipts.  
Phase 3: multi-device sync polish.  
Phase 4: cells + E2EE device fan-out at full scale.

### 5.4 Ordering & gap repair

```text
Server seq monotonic per conversation
Client reorder buffer by seq
Gap: GET /sync?after_seq=
Never use wall clock as sole order
```

### 5.5 E2EE & spam (Meta flavor)

```text
Server sees metadata: graph, sizes, timestamps
Spam: report graphs, rate limits, client-side blocklists
Sender keys for groups; device list changes trigger rekey
```

### 5.6 Progressive evolution

| Stage | Delivery | Groups | Security |
|-------|----------|--------|----------|
| MVP | WS+DB | Async fanout | TLS |
| Prod | mailbox+log | membership ver | optional E2EE |
| Scale | cells | slow-mode | key infra |


---

## 6. Wrap-Up

### 6.1 What we designed

A **Messenger/WhatsApp-class chat system** with connection gateways, per-conversation sequenced durable logs, async group fan-out under size caps, offline mailboxes + push hints, multi-device cursors/sync, receipts/presence, and E2EE-opaque payloads—scaled via sharding and cells.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Ordering | Per conversation seq |
| Delivery | At-least-once + client dedup |
| Offline | Durable log + mailbox; push hint |
| Groups | Cap size; async fan-out |
| Multi-device | Shared log + cursors |
| E2EE | Opaque payload; metadata remains |

### 6.3 Closing line

> “Chat is a sequenced log plus fan-out problem—get per-conversation ordering, durable ACK semantics, and offline cursors right before talking about fancy global consistency.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Ordering & consistency

**Q1: Do we need total order across all chats?**  
A: No — only per conversation. Global order is expensive and unused by UX.

**Q2: Who assigns seq?**  
A: Single-writer partition for that `conversation_id` (chat service shard) allocates monotonic seq.

**Q3: Client timestamps for order?**  
A: Unsafe under clock skew; display ts OK; order by server seq.

**Q4: Causal order across devices?**  
A: Per-chat seq + client buffering; for E2EE apps, local DB merge by seq.

**Q5: What about concurrent sends in a group?**  
A: Serialized by conversation shard; seq defines order.

### 7.2 Delivery & offline

**Q6: When do we ACK the sender?**  
A: After durable append to conversation log (and necessary index), not after all recipients read.

**Q7: Offline user — where does message live?**  
A: In conversation log (SoT) + mailbox pointer for efficient wakeup; device syncs by cursor.

**Q8: Why not only mailbox without log?**  
A: Multi-device and history backfill need a canonical conversation log.

**Q9: Push notification body?**  
A: Often truncated/preview; under E2EE may be generic “New message”; sync fetches ciphertext.

**Q10: At-least-once duplicates?**  
A: Client dedups on `client_msg_id` / `server_msg_id`.

### 7.3 Connections

**Q11: How many connections per gateway?**  
A: Order 100K–1M depending on language/event loop; size fleet from concurrent users × devices.

**Q12: Sticky sessions?**  
A: User/device sticky to gateway; registry maps user→conn; on fail, remaps.

**Q13: Long polling vs WebSocket?**  
A: WS/MQTT preferred for bidirectional; long poll fallback for hostile networks.

**Q14: Heartbeats?**  
A: Application ping + load balancer idle timeouts; presence derived.

### 7.4 Groups

**Q15: Max group size?**  
A: MVP 256–1024; beyond that use channels/broadcast with different fan-out.

**Q16: How is fan-out done?**  
A: Append once; async workers notify members’ devices/mailboxes in pages.

**Q17: Member removed mid-fan-out?**  
A: Check `membership_version` or membership set at deliver time; skip removed.

**Q18: Admin messages / control messages?**  
A: Same log with `kind=control` (title change, member add); clients apply.

### 7.5 Multi-device sync

**Q19: How do desktop and phone stay in sync?**  
A: Shared conversation log; each device stores cursors; both receive online pushes; catch-up on resume.

**Q20: Linked device authorization?**  
A: Device pairing (QR) adds device keys; E2EE must encrypt to new device.

**Q21: History on new device?**  
A: Product choice: limited server history, device-to-device transfer, or empty — lock with interviewer.

**Q22: Cursor corruption?**  
A: Resync from last known snapshot / full conversation fetch with auth.

### 7.6 Receipts & presence

**Q23: Delivered vs read?**  
A: Delivered = device ACK; read = UI open / visibility; user can disable read receipts.

**Q24: Receipt amplification?**  
A: Coalesce `upto_seq`; don’t send per-message receipt storms in large groups (WhatsApp often limits group read receipts).

**Q25: Presence privacy?**  
A: Last-seen settings; only share with certain users; don’t persist every heartbeat.

### 7.7 E2EE & media

**Q26: What can the server see with E2EE?**  
A: Routing ids, timestamps, message size, group membership — not plaintext body.

**Q27: Media encryption?**  
A: Encrypt blob client-side; server stores opaque object; message carries key material for recipients (protocol-dependent).

**Q28: Server-side spam detection under E2EE?**  
A: Limited to metadata/graph signals; client-side reporting; challenge for abuse — discuss honestly.

### 7.8 Scale & Meta flavor

**Q29: Hottest shard?**  
A: Celebrity 1:1 rare; large groups / broadcast — monitor `conversation_id` QPS; split channels.

**Q30: 10× vs 100×?**  
A: 10× gateway+mailbox; 100× cells, receipt isolation, membership caching, reconnect admission.

**Q31: Deal-breakers?**  
A: Global total order; sync fan-out unbounded groups; push as SoT; no idempotency; no client dedup; plaintext search under E2EE without caveat.

**Q32: Message edit/delete for everyone?**  
A: Control message with new seq referencing target; clients hide; server may retain tombstone metadata.

**Q33: Unsend after deliver?**  
A: Best-effort revoke; offline copies may remain — product honesty.

**Q34: Cross-region friends?**  
A: Conversation home region; gateways local; cross-ocean latency on send path acknowledged.

**Q35: How does WhatsApp differ from Messenger historically?**  
A: WhatsApp: E2EE default, device-centric; Messenger: richer server-side features historically; infra patterns (gateway, mailbox, seq) still rhyme.

**Q36: Kafka in the path?**  
A: Great for async fan-out/receipts/analytics; **not** a substitute for per-chat seq primary log unless carefully designed.

**Q37: Why conversation log over per-user only inbox?**  
A: Groups and multi-device need shared history; per-user inbox alone duplicates and complicates group semantics.

**Q38: Rate limits?**  
A: Per-user send QPS; per-group; anti-spam; stray media upload quotas.

---

### 7.9 Algorithms & hashing

**Q39: How is conversation_id generated?**  
A: Snowflake/UUID; DM can be deterministic hash of sorted user pair + salt.

**Q40: Consistent hashing for gateways?**  
A: user_id → gateway; on GW drain remint map; clients reconnect.

**Q41: Why coalesce receipts?**  
A: Read receipts in large groups amplify worse than messages; batch max_seq.

**Q42: Backpressure algorithm for groups?**  
A: Token bucket per conversation send rate; slow-mode admin.

### 7.10 Failure & multi-region

**Q43: Region failure with open sockets?**  
A: Clients reconnect to other region; sync from cursor; conv home failover planned.

**Q44: Split-brain seq?**  
A: Fenced leader per conv shard; epoch in seq space.

**Q45: Push notification vs in-app socket?**  
A: Push when no active socket; privacy-limited body under E2EE.

### 7.11 Estimation & closers

**Q46: RAM for 200M conns × 4KB?**  
A: 800GB gateway fleet — order-of-magnitude OK with many hosts.

**Q47: 20M reconnect after outage?**  
A: Admission + jittered backoff; sync prioritized recent convs.

**Q48: Deal-breakers?**  
A: Client-time order; sync fanout huge groups on request path; ACK before durable; global order.

**Q49: Messenger vs WhatsApp in interview?**  
A: Call out E2EE + multi-device differences; same skeleton: GW, log, fanout, sync.

**Q50: Cut for time?**  
A: Deep crypto; keep ordering, durability ACK, fanout, sync cursors, scale jumps.


### Appendix A — Send path pseudocode

```text
def send(alice, req):
  if seen(alice, req.client_msg_id): return prior_ack
  conv = load_conv(req.conversation_id)
  authorize(alice, conv)
  seq = next_seq(conv)  # locked partition
  msg = append_log(conv, seq, req)
  ack_alice(msg)
  enqueue_fanout(conv, msg)
  return ack
```

### Appendix B — Fan-out pseudocode

```text
def fanout(conv, msg):
  for user in members(conv):
    if user == msg.sender: notify_other_devices(user, msg); continue
    sessions = registry.online(user)
    if sessions: push_all(sessions, msg)
    else: mailbox.add(user, msg.ref); push_notify(user)
```

### Appendix C — Client reorder buffer

```text
on_msg(m):
  if m.seq <= last: ignore
  if m.seq == last+1: apply; last++; drain_buffer()
  else: buffer[m.seq]=m; request_gap_fill(last+1, m.seq-1)
```

### Appendix D — Progressive scale table

| Scale | GW | Log | Fan-out | Sync |
|-------|----|-----|--------|------|
| Baseline | Fleet | Shard by conv | Async | Cursor API |
| 10× | Regional GW | More shards | Queue partitions | Backoff |
| 100× | Cells | Home cell | Membership cache | Priority sync |
| 1,000× | POP+cell | Tiered history | Trees/channels | Cold archive |

### Appendix E — BOTE worked example

```text
20M conns / 200K per GW ≈ 100 GWs
200K msg/s × 1.5 recipients × 1.3 devices ≈ 390K deliver ops/s
Storage 5 TB/day raw → retention policy mandatory narrative
```

### Appendix F — Receipt coalesce

```text
device sends DELIVERED_UPTO(conv, seq=150)
server updates watermark; notifies sender UI once
```

### Appendix G — Membership version

```text
deliver check:
  if msg.membership_version < user.removed_at_version: drop
```

### Appendix H — NFR card

```text
Durable before ACK
Per-chat monotonic seq
Online p50 deliver < 200ms same region
Offline: mailbox + push hint
Group cap enforced
Client dedup required
```

### Appendix I — Deal-breaker checklist

1. Global total order  
2. Unbounded sync group fan-out  
3. In-memory-only offline queue  
4. Push as durability  
5. No client_msg_id idempotency  
6. Server plaintext search under E2EE without disclaimer  

### Appendix J — Media path

```text
client → upload encrypted blob → media_id
client → send chat msg {media_id, keys...}
receiver → fetch blob with auth → decrypt
```

### Appendix K — Presence

```text
heartbeat every 30s → ephemeral online set
disconnect → grace 60s → offline
last_seen update throttled (e.g. 1/min)
```

### Appendix L — Comparison: mailbox vs shared log

| Property | Mailbox only | Shared log + cursors |
|----------|--------------|----------------------|
| 1:1 offline | OK | OK |
| Multi-device | Hard/dupe | Natural |
| Groups | Dupe payloads | Single append |
| History | Weak | Strong |
| Choice | — | **Preferred** |

### Appendix M — Reconnect storm control

```text
gateway admission tokens
client jitter backoff
sync large users last
serve cached cursors
```

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Use Firebase only” | Not Meta-scale design interview |
| “Kafka as chat DB” | Need per-chat seq + UX query |
| “SQL one table worldwide” | Shard/cells |
| “Exactly-once network” | Impossible; dedup |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Seq | Monotonic per-conversation order key |
| Mailbox | Offline pending delivery index |
| Cursor | Device watermark in log |
| Gateway | Persistent connection terminator |
| Fan-out | Deliver to members/devices |
| Envelope | Opaque E2EE payload |

### Appendix P — 30m interview checklist

1. Clarify 1:1/groups, E2EE, multi-device, receipts.  
2. BOTE: conns + msg/s × fan-out.  
3. Draw GW → chat seq log → fan-out → mailbox/push.  
4. Deep dive ordering, sync, groups.  
5. Walk 10×/100×/1,000×.  
6. Deal-breakers.

### Appendix Q — Delete for everyone

```text
control msg seq=n+1 {type: revoke, target_seq:n}
clients hide target; may retain tombstone
offline devices apply on sync
```

### Appendix R — Idempotency keying

```text
unique (sender_id, client_msg_id) → server_msg_id, seq
retries return same ack
```

### Appendix S — Cell routing

```text
conversation_id → home cell
users connect to nearest GW
GW forwards send to home cell chat service
cross-cell deliver via async fabric
```

### Appendix T — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | GW fleets, mailbox, sharded log |
| 100× | Cells, receipt pipeline, membership cache |
| 1,000× | Channels for huge audiences, cold tier, approx presence |

### Appendix U — Security notes

```text
Auth tokens on connect
Device pairing
Rate limits
E2EE key directory integrity (trust model)
Metadata minimization
```

### Appendix V — Meta interview closing

> “I’d treat each chat as a sequenced durable log, terminate millions of sockets at gateway fleets, fan-out asynchronously with offline mailboxes and push as wake-up only, and sync multi-device via cursors—capping groups and keeping E2EE payloads opaque.”

---


## Appendix W — Anti-patterns (deepened)

| Anti-pattern | Why | Instead |
|--------------|-----|---------|
| ACK before durable | Silent loss | Persist then ACK |
| Client timestamps order | Skew/lies | Server seq |
| Sync fanout 10K group | Tail latency | Async+mailbox |
| No cursor sync | Reconnect storm | Delta sync |
| Receipt per member sync | Amplification | Coalesce |
| Presence exact global | Cost/privacy | Approx+trim |

## Appendix X — 90s pitch

> “Realtime gateways, per-conversation server sequencing, durable log before ACK, async fanout to mailboxes, cursor sync, coalesced receipts. Scale connections horizontally; cellize; E2EE as opacity layer. Deal-breakers: client-time order and huge sync fanout.”


*End of Messenger / WhatsApp Chat system design.*
