# System Design: Chat / Messaging System

> **Focus areas:** 1:1 + groups · Persistent connections · Per-conversation ordering · Offline sync · Fan-out · Receipts · Media pointers · Multi-device  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct fan-out math; hybrid fan-out; plane split (connection / messaging / sync); deal-breakers for global total order fantasies  
> **Interview theme:** Microsoft — **generic** messaging platform patterns (Skype/Teams DNA) without full M365 enterprise compliance stack  
> **Differentiation:** This is the **generic chat/messaging** design. For Entra tenant isolation, Purview eDiscovery, and M365 compliance, see `azure-chat-system-design.md`.

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

Goal: design a **generic chat/messaging system** supporting 1:1 and group conversations with realtime delivery, durable history, multi-device sync, and progressive scale—suitable as a Microsoft product interview on “build Skype/Teams-like messaging core” **without** requiring full enterprise compliance deep dive (that is the Azure Chat doc).

### 1.0 What this is / is not

| Dimension | **Generic chat-messaging (this doc)** | **Azure / M365 chat (sibling doc)** |
|-----------|----------------------------------------|-------------------------------------|
| Identity | User accounts (could be MSA / Entra light) | Entra ID first-class; tenants sacred |
| Tenancy | Optional / light | Hard tenant isolation |
| Compliance | Basic abuse, delete, export hooks | Purview, eDiscovery, retention, legal hold |
| Groups | Social / friend groups | Work threads, channels, guest access |
| Success | Fast correct chat | Fast correct chat **and** enterprise governance |
| Presence | Best-effort (see presence doc) | Policy-gated enterprise presence |

**Scope statement:** Design 1:1 + group messaging with ordering, offline sync, multi-device, media pointers, receipts—at progressive consumer/prosumer scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Chat types? | 1:1 and groups (cap e.g. 250–2000) | Conversation + membership |
| F2 | Realtime? | Yes when online | Connection gateway fleet |
| F3 | Offline? | History + push wake | Durable log + device cursors |
| F4 | Ordering? | Per-conversation total order | Monotonic server seq |
| F5 | Multi-device? | Phone + desktop + web | Per-device sync cursors |
| F6 | Receipts? | Delivered + read for 1:1; light for groups | Separate receipt stream |
| F7 | Media? | Images/video/files via blob pointers | Object storage + CDN |
| F8 | Edit/delete? | Edit window; delete for all/me | Mutation events + seq |
| F9 | Push? | APNs/FCM/WNS | Push ≠ SoT |
| F10 | Search? | Client local MVP; server later | Don't block MVP |
| F11 | E2EE? | Optional phase 2 | Hooks only |
| F12 | Reactions? | Optional emoji reactions | Side channel or events |
| F13 | Mentions? | @user in groups | Notification targeting |
| F14 | Spam/block? | Blocks + rate limits | Authz on send |

**MVP functional scope:**

1. Create/open 1:1; send/receive text.  
2. Create group; add/remove members; send to group.  
3. Per-conversation sequence numbers; sync `after_seq`.  
4. Realtime via persistent connections.  
5. Offline mailbox / catch-up; mobile push wake.  
6. Multi-device cursors.  
7. Delivery/read receipts (1:1).  
8. Media upload → message with `media_id`.  
9. Block list + basic rate limits.  
10. Best-effort presence/typing (delegate details to presence doc).

**Out of MVP:**

- Full M365 eDiscovery / legal hold (→ azure-chat doc)  
- Channels with 100K members (hybrid hook only)  
- Strong E2EE sealed sender  
- Voice/video SFU design  
- Global cross-chat total order  
- Perfect server-side search at 1B users  

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Online send→deliver | p50 < 200ms, p99 < 1s in-region after persist |
| N2 | Durability | ACK'd messages never lost (RPO≈0) |
| N3 | Ordering | Per-conversation total order |
| N4 | Availability | 99.9%+ messaging; degrade presence/typing first |
| N5 | Multi-region | Active connection edges; home cell for writes |
| N6 | Fan-out fairness | Large groups don't melt cluster |
| N7 | Multi-device sync | Catch-up complete; no missing after ACK |
| N8 | Scale | Progressive to 100M–1B class |

### 1.3 Cases

**Happy paths**

1. A→B both online: persist → fan-out sessions → ACK.  
2. B offline: persist; push notify; sync on open.  
3. Group 25: persist once; fan-out online members.  
4. Phone + desktop: both get message; read on one updates receipts.  
5. Edit/delete: new seq event referencing `message_id`.  
6. Block: future sends rejected.

**Edge cases**

| Case | Behavior |
|------|----------|
| Double-tap send | Client `msg_id` idempotency |
| Offline compose | Client queue; flush idempotent |
| Large group 50K | Hybrid / pull; not per-user inbox copy |
| Reconnect after sleep | Sync gaps by seq |
| Slow consumer | Catch-up mode; don't block writers |
| Partial fan-out failure | Retry notify; durable log is SoT |
| Media large | Chunked upload; virus scan hook |
| Clock skew | Server seq / server time SoT |
| Membership race | Authz at send on membership version |
| Push privacy | Opaque notification body optional |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| MAU | 10M | 100M | 1B | 1B+ |
| DAU | 2M | 20M | 200M | 400M |
| Concurrent connections | 500K | 5M | 50M | 100M+ |
| Messages / day | 200M | 2B | 20B | 50B+ |
| Peak send QPS | 5K | 50K | 500K | 1M+ |
| Avg group size | 8 | 12 | 15 | 20 |
| P95 group size | 50 | 100 | 250 | 500 |
| Media objects / day | 20M | 200M | 2B | 5B |

**Jumps:** 10× = split connection vs chat service, shard by conversation; 100× = hybrid fan-out + regional home cells; 1,000× = channel mode, cold storage tiers, extreme isolation.

### 1.5 Scope repeat-back

> Generic chat platform: 1:1 and groups, durable per-conversation logs with total order, realtime connection fleet, offline sync and push, multi-device cursors, media pointers, receipts—scaled with hybrid fan-out and regional cells. **Not** the full Azure/M365 compliance chat (sibling doc); presence detailed separately.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Message math

```text
20M DAU × 50 messages/user/day = 1B messages/day
Avg ≈ 1B / 86400 ≈ 11.6K msg/s
Peak 5–10× ⇒ 60K–120K msg/s

Each message:
  1 durable write (conversation log)
  + fan-out to online sessions (variable)
  + optional per-user inbox index for offline
  + receipt updates (amplified)
```

### 2.2 Connection math

```text
5M concurrent connections
Gateway capacity ~ 50K–100K conn/machine → 50–100 gateways (+headroom)
Heartbeat/ping traffic separate from messages
Sticky sessions via connection ID registry
```

### 2.3 Storage

```text
Avg message metadata 500 B–2 KB (text); media in blob
1B msg/day × 1 KB = 1 TB/day raw
Year × 0.3–1 compression/retention policy → hundreds of TB–PB
Partition by conversation_id; cold tier after 90d
Secondary index: user → conversations list
```

### 2.4 Fan-out

```text
Group size G=20, all online:
  write 1 + notify 20 ≈ OK

Group size G=10_000:
  write 10_000 inbox copies → meltdown
  → hybrid: write log once; online active members push; others pull
```

### 2.5 Latency budget

```text
Client → Gateway → Chat Service authz → Append log → ACK → Notify gateways
Persist path p99 target < 200–400ms in-region
Notify additional < 100–300ms
```

### 2.6 Bottlenecks

(1) Hot conversations (2) large group fan-out (3) connection storms (4) media upload (5) receipt write amplification (6) cross-region friends.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Connection | WSS/TCP sessions, routing | Ephemeral registry |
| Messaging / Log | Append messages, seq | Strong per conversation |
| Sync / Inbox | Device cursors, catch-up | Per device |
| Fan-out / Notify | Push to online sessions | At-least-once |
| Media | Blob storage | Durable object |
| Presence/Typing | Ephemeral | Best-effort |
| Identity / Authz | Users, blocks, membership | Strong on send/read |

**Deal-breaker:** one global ordered stream for all messages; or fan-out 1M inbox writes synchronously on send.

### 3.2 Components

1. **Edge / Azure Front Door** — TLS, DDoS.  
2. **Connection Gateway** — long-lived sockets; forward RPCs.  
3. **Chat / Conversation Service** — send, membership, authz.  
4. **Message Log Store** — partitioned append log (Cassandra/Cosmos/Kafka+DB).  
5. **Fan-out Worker** — online push; offline index updates.  
6. **Sync Service** — `GET /sync?after_seq` / device mailbox.  
7. **Receipt Service** — delivery/read (sharded lightly).  
8. **Media Service** — SAS upload, scan, CDN.  
9. **Push Service** — WNS/APNs/FCM.  
10. **User / Graph Service** — profiles, blocks, contacts.  
11. **ID Gen** — conversation-local seq; global msg UUIDs.  
12. **Presence Client** — calls presence API (separate).

### 3.3 Message send API (sketch)

```text
POST /v1/conversations/{cid}/messages
{
  "client_msg_id": "uuid",          // idempotency
  "type": "text",
  "body": "...",
  "media_ids": [],
  "reply_to": null
}
→ { message_id, seq, server_ts }
```

### 3.4 Ordering model

```text
Conversation C has monotonic seq 1..N (server assigned)
All events (message, edit, delete, membership) consume seq OR
  messages use seq; sideband for receipts (product choice)
Clients render by seq; gaps → sync fill
No global order across conversations
```

### 3.5 Trade-offs

| Topic | Choice | Why | Deal-breaker |
|-------|--------|-----|--------------|
| Fan-out | Hybrid by group size | Scale | Always write fan-out |
| Store | Conv-partitioned log | Ordering natural | User-only inbox SoT |
| Connections | Separate gateway fleet | Scale independently | Chat pods hold all sockets |
| Receipts | Separate channel | Avoid log bloat | Every read in main log at 1B |
| Media | Pointer in message | Payload size | Inline multi-MB in log |
| Multi-region | Home cell per conv | Write conflict avoid | Multi-master without CRDT story |
| E2EE | Phase 2 hooks | Interview time | Pretend full Signal in 45m |

### 3.6 Microsoft themes (light)

Even in **generic** chat, mention: WNS push, Azure Blob/CDN, Azure SignalR-like gateways, optional MSA/Entra auth, regional Azure. Deep Purview/tenant → sibling doc.

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Clients]
   |  WSS
   v
[Connection Gateway Fleet] <-----> [Conn Registry]
   |  send/sync/ack
   v
[Chat Service] ----authz----> [Membership / Blocks]
   |  append
   v
[Message Log Store] ----events----> [Fan-out Workers]
   |                                  |           |
   |                                  v           v
   |                           [Online Push]  [Offline Index]
   |                                  |           |
   |                                  v           v
   |                           [Gateways]    [Push Service]
   |
   +-----> [Sync Service] <--- device cursors ---
   |
   +-----> [Receipt Service]
   |
[Media Service] <-> [Blob Object Store] <-> [CDN]
```

### 4.2 1:1 send sequence

```text
1. A gateway → ChatService.Send(client_msg_id, body)
2. Authz: A member of conv; not blocked
3. Idempotency lookup client_msg_id
4. Assign seq = next(C); persist Message
5. ACK to A (and A's other devices via notify)
6. Fan-out to B's online sessions; else push notify
7. B ACK delivered → receipt service
```

### 4.3 Group hybrid fan-out

```text
Small G <= T (e.g. 100):
  persist log
  update per-member inbox pointer (optional)
  push to online members

Large G > T:
  persist log only
  push to currently active viewers / recent readers
  others pull on open via sync(after_seq)
```

### 4.4 Multi-device sync

```text
User U devices D1, D2
Each device: cursor (cid → last_seq) or global sync token
On reconnect: SyncService returns envelopes since cursors
Read receipt on D1 → notify D2 (receipt plane)
```

### 4.5 Home cell

```text
Conversation home = hash(cid) → cell / region
All appends to home
Gateways anywhere forward RPCs to home
Cross-region latency accepted for correctness
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. ACK to sender ⇒ message durable in conversation log.  
2. `client_msg_id` idempotent.  
3. Seq monotonic per conversation; no reuse.  
4. Membership checked at send.  
5. Blocks honored.  
6. Fan-out failure ≠ loss (sync repairs).  
7. Push is wakeup only.  
8. Deletes/edits are new events, not silent rewrite without tombstone.  
9. Media not in critical path of log durability (pointer after upload).  
10. Degrade: typing → presence → receipts → realtime push; never lose ACK'd sends.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; PG messages; Redis pubsub; few gateways |
| 10× | Gateway fleet; chat service stateless; shard log by cid |
| 100× | Hybrid fan-out; home cells; cold tier; receipt isolation |
| 1000× | Channel mode; mega-group isolation; multi-cloud; cost budgets |

### 5.3 Maintainability

- Conversation event schema versioned.  
- Fan-out strategy as config threshold T.  
- Chaos: kill fan-out workers—sync still works.  
- Canary home cell.  
- Clear ownership: Messaging Platform vs Push vs Media.  
- Load tests: hot group, reconnect storm, double-send.

### 5.4 Progressive scale narrative

**1×:** Single region; 1:1 + small groups; Postgres; Socket.IO/SignalR.  
**10×:** Partitioned message store; dedicated gateways; push; media CDN.  
**100×:** Hybrid fan-out; multi-region homes; inbox index optional; search phase.  
**1000×:** Broadcast channels; storage tiering; extreme hot-key isolation.

### 5.5 Ordering deep dive

```text
Why per-conversation:
  UX needs A then B in a thread
  Seq generation scales with shard per cid

Why not global:
  Hotspot lock; useless across chats

Causal vs total:
  Total order via single writer / seq allocator per conv is simplest interview answer
```

### 5.6 Idempotency & exactly-once display

```text
Exactly-once **persist** via client_msg_id unique constraint
At-least-once **deliver** to devices
Exactly-once **display** via client dedupe on message_id
```

### 5.7 Offline & push

| Path | Role |
|------|------|
| Message log | SoT history |
| Device sync cursor | Catch-up |
| Optional inbox | Fast “unread” listing |
| Push | Wake locked phones |
| Local DB | Client cache |

**Push payload:** prefer opaque or short preview; full body via sync (privacy + size).

### 5.8 Group membership races

```text
Send path loads membership_version
If removed, reject
Add member: they sync from join_seq (history policy: full / from join)
Remove: stop fan-out; history retention policy product-specific
```

### 5.9 Receipt amplification

```text
1:1: delivery + read OK
Group 200: per-user read storms
Mitigate: aggregate (“n read”); disable precise read; sample
Never write each receipt as full message row without care
```

### 5.10 Media pipeline

```text
1. Client requests upload URL (SAS)
2. PUT bytes to blob
3. Async scan (malware)
4. Client sends message with media_id
5. Recipients fetch via CDN + authz cookie/token
```

### 5.11 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Gateway death | Reconnect other GW | Conn registry TTL |
| Chat service blip | Send errors | Client retry idempotent |
| Log store quorum loss | Writes fail | ACK only after quorum |
| Fan-out lag | Delayed realtime | Sync repair |
| Push outage | Silent offline | In-app badge on open |
| Hot conversation | Latency | Isolate shard; rate limit |

### 5.12 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Global message order | Impossible scale |
| Per-user inbox only SoT | Group history integrity pain |
| Sync fan-out 1M writes | Melts write path |
| Chat pods own sockets + DB | Can't scale independently |
| Rely on push for durability | Lost messages |
| Inline 100MB in message row | Store death |
| Cross-region multi-master append | Dup/conflict hell without CRDTs |

### 5.13 Security (generic)

- Authn on every send/sync.  
- Authz membership + block.  
- Rate limits per user/device/IP.  
- Media authz separate.  
- E2EE phase 2: server stores ciphertext; metadata still visible.  
- Report/spam pipeline async.

### 5.14 Differentiation reminder (interview gold)

> “If you need tenant isolation, eDiscovery, retention labels, and legal hold, I’d extend this with the Azure Chat enterprise control plane—separate doc. This design is the messaging core.”

### 5.15 Consistency & multi-region

```text
Single home cell writer per conversation
Read replicas optional for history (lag OK with seq checks)
Moving home cell = rare controlled migration
```

### 5.16 Unread counts

```text
Maintain per-user per-conv last_read_seq
Unread ≈ max_seq - last_read_seq (with care for tombstones)
Aggregate badge = sum with caps
Don't scan full history each open
```

### 5.17 Typing indicators

```text
Ephemeral pub/sub via gateway
TTL 3–5s; drop under load
Never persist
```

### 5.18 Search (phase 1.5)

```text
Async index message text (if not E2EE)
Eventually consistent
Query authz filter membership
Don't block send path on indexer
```

---

## 6. Wrap-Up

### 6.1 Designed

Generic Microsoft-flavored chat: connection gateways, conversation-partitioned durable log with seq, hybrid fan-out, sync cursors, push wake, media pointers, receipts plane—progressive scale 10×→1000×.

### 6.2 Decisions to defend

1. Per-conversation total order via server seq  
2. Plane split connection / log / sync / fan-out  
3. Hybrid fan-out threshold  
4. Idempotent client_msg_id  
5. Push ≠ storage  
6. Home cell for writes  
7. Receipts isolated  
8. Enterprise compliance deferred to azure-chat doc  

### 6.3 Risks

- Hot groups / viral threads  
- Reconnect storms  
- Receipt storms  
- Cross-region latency UX  
- Media abuse  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope 1:1+groups; contrast azure-chat |
| 5–15 | Send path + seq + idempotency |
| 15–25 | Gateways + fan-out + offline sync |
| 25–35 | Multi-device, receipts, media |
| 35–45 | Scale jumps, deal-breakers |

### 6.5 Closer

> **Chat Messaging**: durable per-conversation logs, realtime gateways, hybrid fan-out, multi-device sync—messaging core at Microsoft scale, with enterprise governance intentionally separated into Azure Chat.

---

## 7. Deeper / Related Interview Questions

### 7.1 Conceptual

1. Why per-conversation order instead of global?  
2. Explain hybrid fan-out and choose threshold T.  
3. How do multi-device read receipts work?  
4. What does an ACK guarantee?  
5. How do edits/deletes preserve order?  
6. Inbox model vs log model—trade-offs?  
7. How is this different from Slack channels?  
8. How would you add E2EE without rewriting fan-out?  
9. Typing vs presence vs receipts—planes?  
10. When is Kafka the message SoT vs not?

### 7.2 Quantitative

11. 100M DAU × 40 msgs/day → avg and 8× peak QPS.  
12. Group 5K members, 10% online active—push vs pull costs.  
13. Storage for 10B msgs/day × 800 B × 30 days.  
14. Gateways needed for 30M connections at 60K/conn host.  
15. Receipt QPS if every deliver/read is a write in 1:1-heavy workload.

### 7.3 Failure

16. Fan-out worker dead for 10 minutes—user experience?  
17. Split brain two homes accidentally—prevention.  
18. Client retries with new client_msg_id by bug—impact.  
19. Hot celebrity broadcast group—design mode switch.  
20. Push provider outage playbook.

### 7.4 Microsoft-flavored

21. Where would WNS fit?  
22. SignalR vs custom gateway fleet.  
23. When do you graduate this design into azure-chat compliance?  
24. Blob SAS risks for media.  
25. How Teams channel @mention would target notify.

### 7.5 Compare

26. WhatsApp vs this generic design.  
27. Discord large servers vs hybrid fan-out.  
28. SMS gateway vs IP messaging.  
29. Email threading vs chat seq.  
30. Presence service integration points.

### 7.6 Stretch

31. Design message search with authz.  
32. Migration from monolith DB to partitioned log.  
33. Cross-region conversation migration.  
34. Abuse detection online without killing latency.  
35. Partial message encryption (attachments only).

---

## 8. Appendices

### Appendix A — APIs

#### A.1 Create conversation

```http
POST /v1/conversations
{
  "type": "group",
  "memberIds": ["u1", "u2", "u3"],
  "title": "Project"
}
→ { "conversationId": "c_...", "membersVersion": 1 }
```

#### A.2 Send message

```http
POST /v1/conversations/{cid}/messages
Idempotency-Key / client_msg_id
{
  "clientMsgId": "b7c2...",
  "type": "text",
  "body": "hello",
  "mediaIds": []
}
→ { "messageId": "m_...", "seq": 105, "serverTs": "..." }
```

#### A.3 Sync

```http
GET /v1/sync?cursor=opaque_or_map
→ {
  "envelopes": [
    {"cid":"c1","seq":106,"type":"message","payload":{...}},
    {"cid":"c1","seq":107,"type":"edit","payload":{...}}
  ],
  "nextCursor": "..."
}
```

#### A.4 Receipts

```http
POST /v1/conversations/{cid}/receipts
{ "messageId":"m_...", "type":"read", "seq":105 }
```

#### A.5 Media

```http
POST /v1/media/upload-sessions
→ { "mediaId":"med_...", "uploadUrl":"https://blob.../sas", "expires":"..." }
```

### Appendix B — Schemas

#### B.1 Conversation

```text
Conversation {
  cid: UUID
  type: ONE_TO_ONE | GROUP
  title: string?
  members_version: int64
  created_at: ts
  home_cell: string
  max_seq: int64
}
```

#### B.2 Membership

```text
Membership {
  cid: UUID
  user_id: UUID
  role: OWNER | ADMIN | MEMBER
  joined_seq: int64
  left_seq: int64?
  state: ACTIVE | REMOVED
}
```

#### B.3 Message event

```text
MessageEvent {
  cid: UUID
  seq: int64
  message_id: UUID
  client_msg_id: UUID
  sender_id: UUID
  type: TEXT | MEDIA | SYSTEM | EDIT | DELETE
  body: string?              // or ciphertext
  media_ids: [UUID]
  reply_to: UUID?
  server_ts: ts
  prev_message_id: UUID?     // for edit/delete
}
```

#### B.4 Device cursor

```text
DeviceCursor {
  user_id: UUID
  device_id: UUID
  sync_token: string
  last_active_at: ts
}
```

### Appendix C — Fan-out pseudocode

```text
function onAppend(event):
  members = membership.active(event.cid)
  if members.size <= T:
    for u in members:
      offlineIndex.add(u, event)
      for sess in onlineSessions(u):
        push(sess, event)
  else:
    active = recentlyActiveMembers(event.cid)
    for u in active:
      for sess in onlineSessions(u):
        push(sess, event)
    # others: pull via sync when opening conv
```

### Appendix D — Seq allocator

```text
Options:
1) DB atomic increment on conversation row
2) Per-cid leader in memory + WAL
3) Snowflake-like with careful merge (harder for dense seq)

Interview pick: single-writer shard partition owning cid
```

### Appendix E — Idempotency table

```text
IdempotencyRecord {
  cid: UUID
  client_msg_id: UUID
  message_id: UUID
  seq: int64
  created_at: ts
}
PK (cid, client_msg_id)
TTL or permanent
```

### Appendix F — Push payload example

```json
{
  "type": "chat_wake",
  "cid": "c_...",
  "preview": "New message",
  "collapseKey": "c_..."
}
```

### Appendix G — Rate limits

| Action | Limit |
|--------|-------|
| Send msg | 30/min sustained; burst 10 |
| Create group | 10/hour |
| Add members | 50/hour |
| Sync | 120/min |
| Upload media | 50/hour; size caps |

### Appendix H — Storage tiering

| Tier | Age | Store |
|------|-----|-------|
| Hot | 0–30d | SSD / Cosmos hot |
| Warm | 30–180d | Cheaper SSD/HDD |
| Cold | 180d+ | Blob / archive |
| Delete | Policy | GC job |

### Appendix I — SLO table

| SLO | Target |
|-----|--------|
| Persist success after accept | 99.99% |
| Online deliver p99 in-region | < 1s |
| Durability of ACK'd | 100% |
| Sync catch-up 1000 events | < 2s p99 |

### Appendix J — Comparison table vs Azure Chat

| Feature | Generic chat | Azure chat |
|---------|--------------|------------|
| Entra tenant isolation | Optional | Mandatory |
| eDiscovery | Hook | First-class |
| Retention / legal hold | Deferred | Required |
| Guest access | Simple | Entitlement complex |
| Compliance boundary | Light | Purview |
| Messaging core | This doc | Reuses patterns |

### Appendix K — Event types

```text
MESSAGE_CREATE
MESSAGE_EDIT
MESSAGE_DELETE
MEMBER_ADD
MEMBER_REMOVE
TITLE_CHANGE
REACTION_ADD (optional)
REACTION_REMOVE (optional)
```

### Appendix L — Client state machine

```text
DISCONNECTED → CONNECTING → CONNECTED → SYNCING → LIVE
LIVE → (gap detected) → SYNCING
LIVE → (send) → PENDING_ACK → LIVE
App background → may drop socket; push wakes
```

### Appendix M — Hot conversation isolation

```text
Detect: append QPS or notify QPS above threshold
Actions:
  dedicated partition
  stricter rate limits
  disable receipts
  force pull mode for members
  page oncall
```

### Appendix N — Security checklist

- [ ] Authn every RPC  
- [ ] Membership authz  
- [ ] Block checks  
- [ ] Media token scoped to med_id  
- [ ] Rate limits  
- [ ] Malware scan  
- [ ] Report pipeline  
- [ ] PII in logs redacted  

### Appendix O — Capacity worksheet

```text
DAU = ______
Msgs/user/day = ______
Msgs/day = ______
Avg send QPS = ______
Peak factor = ______
Peak send QPS = ______
Avg group size = ______
Hybrid threshold T = ______
Connections = ______
GW capacity = ______
GW count = ______
```

### Appendix P — Sample membership authz

```text
function authorizeSend(user, cid):
  m = membership.get(cid, user)
  if m is null or m.state != ACTIVE: deny
  if blockService.blockedEither(user, recipients): deny
  if rateLimiter.over(user): deny
  allow
```

### Appendix Q — Delete semantics

| Mode | Effect |
|------|--------|
| Delete for me | Hide in client; server flag per user |
| Delete for all | Tombstone event; body redacted; seq retained |
| GDPR erase | Scrub body; retain minimal stub if legally required |

### Appendix R — Related docs

- `presence-service-api-system-design.md` — presence/heartbeats  
- `azure-chat-system-design.md` — M365 enterprise chat  
- OpenAI `high-scale-chat-system-design.md` — mega-scale patterns  

### Appendix S — Interview script

```text
1. Clarify 1:1 + groups; call out azure-chat out of scope
2. Draw planes
3. Send path + seq + idempotency
4. Fan-out small vs large
5. Offline sync + push
6. Numbers
7. Multi-device + receipts
8. Deal-breakers
```

### Appendix T — Glossary

| Term | Meaning |
|------|---------|
| Seq | Per-conversation monotonic order key |
| Home cell | Region/shard owning writes for a conversation |
| Hybrid fan-out | Push small/active; pull large/passive |
| Client msg id | Idempotency key from sender |
| Envelope | Sync unit wrapping an event |
| Cursor | Device catch-up position |
| WNS | Windows Push Notification Services |

### Appendix U — Anti-patterns

1. Mongo collection without shard key plan.  
2. Redis-only message storage.  
3. One Kafka topic for all chats without partitioning story.  
4. Synchronous virus scan on send critical path without timeout.  
5. Storing push tokens in the message log.  

### Appendix V — Multi-device read example

```text
max_seq=105
D1 last_read=100 → unread 5
User reads on D1 → last_read=105 → receipt events
D2 receives receipt → updates UI ticks; last_read coalesced to 105
```

### Appendix W — Group history policy

| Policy | New member sees |
|--------|-----------------|
| From join | Messages seq ≥ joined_seq |
| Full history | All (privacy risk) |
| Limited window | Last N days |

### Appendix X — Observability

Metrics: send_qps, append_latency, fanout_lag, sync_latency, conn_count, push_fail, idempotent_hits, hot_cid_count  
Logs: sample send traces with cid hash  
Alerts: append error budget; fanout lag SLO  

### Appendix Y — Migration sketch monolith → partitioned

```text
1. Introduce cid home map
2. Dual-write period
3. Tail replay to new log
4. Switch reads
5. Disable old path
```

### Appendix Z — Closing checklist for candidates

- [ ] Locked MVP scope  
- [ ] Drew plane split  
- [ ] Explained seq  
- [ ] Hybrid fan-out math  
- [ ] ACK durability semantics  
- [ ] Named degrade order  
- [ ] Differentiated from azure-chat  
- [ ] Listed deal-breakers  

---

*End of Chat / Messaging system design prep doc.*
