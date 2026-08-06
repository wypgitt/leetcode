# System Design: Facebook Chat API Layer

> **Focus areas:** Chat API gateway · Persistent connections · Fan-out delivery · Presence · Message durability handoff · Rate limits · Multi-device sync · Backpressure · AuthZ  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** API layer ≠ full chat storage/Kafka internals; clear ownership boundary; deal-breakers for “store all messages in API nodes’ memory”  
> **Interview theme:** Meta chat edge — the **API/connection layer** that fronts Messenger-style chat backends

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

Goal: **bound the product**—the **Facebook Chat API Layer**: the edge/gateway that terminates client connections (MQTT/WebSocket/HTTPS), authenticates, rate-limits, routes RPCs, streams real-time events (messages, receipts, typing, presence), and hands off durability to downstream chat services.

### 1.0 What this is / is not

| Dimension | **Chat API layer (this doc)** | Not this |
|-----------|-------------------------------|----------|
| Primary job | Connection + API facade + realtime push | Full message DB / search / E2EE key server deep dive |
| Success | Low-latency delivery, sticky sessions, backpressure | Perfect offline analytics |
| State | Connection registry, presence hints, inflight | Canonical message history |
| Protocols | MQTT / WS / HTTP APIs | Raw SQL to clients |
| Ownership | Edge + session routing | Thread store, attachment store (downstream) |

**Scope statement:** Design the chat API/connection layer that fronts Facebook/Messenger chat backends at scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Client APIs? | Send message, sync history, ack delivery/read, typing, presence | RPC + push channels |
| F2 | Transport? | Persistent MQTT/WS + HTTPS fallback | Connection managers |
| F3 | Multi-device? | Same user multiple sessions | Fan-out to session set |
| F4 | Auth? | Session tokens / app auth | Validate at edge |
| F5 | Ordering? | Per-thread approximate order; server timestamps/ids | Downstream ids; edge preserves |
| F6 | Offline? | Queue for push / sync on reconnect | Hand off to push + sync API |
| F7 | Groups? | Large threads supported | Don’t explode edge CPU |
| F8 | Attachments? | Upload via separate media API; message refs | Edge validates refs |
| F9 | Rate limits? | Anti-spam per user/thread | Edge enforcement |
| F10 | Presence? | Online/away/active | Presence service + aggregation |
| F11 | Admin? | Force logout, drain connections | Control plane |
| F12 | Encryption? | Transport TLS; E2EE payload opaque optional | Edge may not inspect body |

**MVP functional scope:**

1. Terminate persistent connections; map `user_id → connection_ids`.  
2. HTTP/RPC: send, sync (cursor), mark delivered/read, fetch thread metadata.  
3. Push: new message, receipts, typing, presence deltas to online sessions.  
4. AuthN/AuthZ on every call; thread membership checks (cached).  
5. Rate limiting and abuse shields.  
6. Sticky routing to connection cells; graceful drain.  
7. Hand off durable write to Message Service; edge awaits ack before client ack (or policy).  
8. Integrate Push Notification Service for offline.

**Out of MVP:**

- Full Cassandra message store design (interface only)  
- Full E2EE key distribution product  
- Chatbots platform  
- Voice/video signaling deep (mention hooks)  
- Server-side message search index

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Send latency | Feels instant | p99 < 100–200ms online path (edge+store ack) |
| N2 | Push latency | Online recipients fast | p99 < 100–300ms after durable |
| N3 | Connections | Massive concurrent | Millions+/cell; many cells |
| N4 | Availability | Chat critical | 99.9%+; reconnect storms OK |
| N5 | Ordering | Per-thread | Monotonic message ids from store |
| N6 | Backpressure | Protect backends | Shed typing; queue bounds |
| N7 | Security | No cross-user leak | AuthZ; IDOR tests |
| N8 | Multi-region | Users global | Home region / cell affinity |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User A online sends to B online → durable → push to B’s devices → delivery ack.  
2. B offline → store + mobile push; on reconnect sync cursor.  
3. Typing indicators to online thread members (ephemeral).  
4. User multi-device: message appears on phone + desktop.  
5. Connection drain for deploy → clients reconnect elsewhere.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Downstream store timeout | Client retry with idempotency key; no double send |
| Recipient connection flapping | Presence debounce; push coalescing |
| Thundering herd reconnect | Jittered backoff; connect rate limit |
| Huge group 10K members | Don’t push typing to all; sample; message fan-out via dedicated service |
| Auth token expiry | Refresh; drop connection |
| Poison oversized payload | Reject at edge |
| Hot celebrity broadcast thread | Special fan-out path downstream; edge doesn’t loop 50M |
| Edge OOM | Connection shedding; health checks |
| Split brain session registry | Lease/heartbeat; single writer per connection id |
| E2EE opaque payload | Size limits still enforced |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU chat | 100M | 1B | — | extreme |
| Peak concurrent connections | 20M | 200M | 2B | cell fabric |
| Messages send/s | 200K | 2M | 20M | 200M |
| Push events/s | 1M | 10M | 100M | hierarchical |
| Sync/history QPS | 100K | 1M | 10M | 100M |
| Typing events/s | 500K | 5M | shed | shed aggressively |
| API nodes | hundreds | thousands | tens of k | many cells |
| Threads touched/s | high | ×10 | ×100 | ×1000 |

**What each jump forces:**

- **10×:** Connection cells; session directory; rate limits; MQTT at scale.  
- **100×:** Regional cells; hierarchical fan-out; typing suppression; separate sync tier.  
- **1,000×:** Fine-grained cells; edge presence approx; heavy offline push offload.

### 1.5 Etc. (Constraints & Assumptions)

- Message Service provides durable ids and storage APIs.  
- Push Service (APNs/FCM) exists.  
- Graph/thread membership service exists.  
- We design **API layer**, not the entire Messenger monolith.

**Scope statement to repeat back:**

> Design Facebook Chat’s API/connection layer: persistent sessions, authenticated RPCs, realtime push, rate limits, multi-device fan-out, backpressure, and clean handoff to durable message/presence/push systems—scaled via connection cells and reconnect-safe clients.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes (critical split)

| Class | Characteristics | Plane |
|-------|-----------------|-------|
| Long-lived connections | Memory, fds, heartbeats | Connection managers |
| Send RPC | Durable path | Edge → Message Service |
| Sync/history | Read heavy | Sync tier / cache |
| Realtime push | Fan-out | Session router |
| Presence / typing | Ephemeral high QPS | Volatile path |
| Mobile push | Offline | Push service |

**Anti-pattern:** sizing API fleet only by “messages/s” ignoring connection memory.

### 2.2 Connection memory

```text
Assume 10KB state / connection (buffers, session meta)
20M conns × 10KB = 200 TB? No: 20e6 × 10e3 = 200e9 = 200 GB
Across fleet with headroom → many servers
fd limits, epoll, TCP memory also bind
```

### 2.3 Fan-out

```text
200K msgs/s × avg 1.5 online recipient devices ≈ 300K pushes/s
Groups amplify; use thread fan-out service, not nested loops on edge
```

### 2.4 Typing amplification

```text
Typing every 3s × millions of chatters → huge
Edge must throttle, coalesce, suppress for large threads
```

### 2.5 Reconnect storm

```text
Cell of 1M conns dies → 1M reconnects
With 10s jitter window → 100K connects/s — need admission control
```

### 2.6 Latency budget send

```text
Edge auth/rl: 5–10ms
Membership cache: 5ms
Message Service write: 20–50ms
Push enqueue: 5–10ms
Total ~50–100ms typical; p99 < 200ms
```

### 2.7 Protocol plane split math

```text
MQTT/WS: small frames (msgs, receipts, typing) — millions concurrent
HTTPS/GraphQL/Thrift: sync history, large catch-up, media bootstrap
If all history over MQTT: head-of-line + fat channel — anti-pattern
Typing 500K/s ephemeral ≫ durable 200K sends/s — must shed first
```

### 2.8 Auth & membership cache

```text
200K sends/s × membership check
Cache hit 99% → 2K/s to membership service
Fail closed on miss+service down for send
Token revalidate every N min on long-lived MQTT
```

### 2.9 Presence update volume

```text
Connect/disconnect/heartbeat aggregated
20M conns × heartbeat/30s → ~670K hb/s fleet-wide — cheap if local
Presence fanout to friends: do NOT notify all friends on every hb
Publish presence deltas sparsely; subscribers pull/cache
```

### 2.10 Pagination / sync cursors

```text
Sync 100K QPS × 50 events ≈ heavy read — separate sync tier
Cursor opaque; keyset on (thread_id, message_id)
Never OFFSET into chat history
```

### 2.11 Progressive API-layer capacity

| Scale | Conns | Send path | Push | Ephemeral |
|-------|-------|-----------|------|-----------|
| Base | Sticky nodes | Durable ack | Directory lookup | Typing OK |
| 10× | Cells | Idempotent | Router | RL |
| 100× | Regional cells | Fanout svc | Hierarchical | Shed typing |
| 1,000× | Fabric | Admission | Approx presence | Aggressive brownout |

### 2.12 BOTE anti-patterns

| Anti-pattern | Failure |
|--------------|---------|
| Messages only in edge RAM | Loss on deploy/crash |
| Size fleet by msgs/s only | Conn memory under-provisioned |
| Typing to 10K group members | Amplification death |
| Instant reconnect no jitter | Stampede after cell kill |

---

## 3. High-Level Design

### 3.1 API surface

| Op | Transport | Semantics |
|----|-----------|-----------|
| `SendMessage` | MQTT/HTTPS | Idempotent send; returns message_id |
| `Sync` | HTTPS | Cursor-based inbox/thread sync |
| `AckDelivered` / `AckRead` | MQTT/HTTPS | Receipts |
| `Typing` | MQTT | Ephemeral |
| `Connect` / heartbeat | MQTT/WS | Session register |
| `GetThread` | HTTPS | Metadata |
| Push frames | MQTT/WS | server → client events |

**Send payload (logical):**

```text
SendMessage {
  client_msgid,   // idempotency
  thread_id,
  body OR e2ee_blob,
  attachments[],
  reply_to?,
  expect_user_devices?
}
```

### 3.2 Components

| Component | Role |
|-----------|------|
| L4/L7 LB | Route to connection cells |
| Connection Manager | Sessions, heartbeats, frames |
| Session Directory | user → {cell, conn_id, device} |
| API Workers | Stateless HTTPS RPCs |
| Router / Push Gateway | Deliver events to conn |
| Rate Limiter | Token buckets |
| Membership Cache | Thread ACL |
| Downstream clients | Message, Presence, Push |

### 3.3 Connection model — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Pure HTTPS polling** | Simple | Latency/battery | Fallback only |
| **WebSocket only** | Familiar | Mobile OS constraints | Web + some mobile |
| **MQTT** | Light, mobile-friendly | Another protocol | **Strong mobile choice** |
| gRPC streaming | Nice RPC | LB/proxy complexity | Internal |

**Chosen:** MQTT (or equivalent) persistent for mobile; WS for web; HTTPS for sync/send fallback.

### 3.4 Ack policy — Why X over Y

| Policy | Pros | Cons |
|--------|------|------|
| Ack after edge receive | Fast | Risk loss if crash before durable |
| **Ack after Message Service durable** | Safe | Slightly slower |
| Client-only optimistic | UX | Complex reconcile |

**Chosen MVP:** Client send ack after durable store confirms; then async push to recipients.

### 3.5 Session directory — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| In-memory only on node | Fast | Lost on crash; hard lookup |
| **Distributed directory (Redis/etc.)** | Lookup by user | Must lease/heartbeat |
| Sticky LB without directory | Simple | Multi-device push hard |

**Chosen:** Session Directory with heartbeated leases; push looks up all devices.

### 3.6 Why X over Y summary

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Durability | Downstream store | Correctness | Messages only in edge RAM |
| Connections | Cells + directory | Scale | One giant process |
| Typing | Throttle/coalesce | Cost | Full fidelity large groups |
| Fan-out | Downstream + router | Groups | Edge nested loops for 10K |
| Sync | Cursor HTTPS tier | Separation | History through fat MQTT only |
| Reconnect | Jitter + admission | Stability | Instant reconnect stampede |

### 3.7 Expanded HLD tradeoffs

| Axis | A | B | Pick |
|------|---|---|------|
| Mobile transport | HTTPS poll | MQTT persistent | **MQTT + HTTPS sync** |
| Ack | After edge recv | After durable store | **After durable** |
| Presence | HB to all friends | Sparse deltas + query | **Sparse** |
| API facade | MQTT-only | MQTT + GraphQL/Thrift/HTTPS | **Split planes** |
| Group fanout | Edge loops | Downstream fanout svc | **Downstream** |

**Anti-patterns:** edge-as-DB; typing to 10K; no client_msgid; reconnect stampede; client-trusted recipients.

---

## 4. Architecture Diagram

```text
  Mobile (MQTT)  Web (WS/HTTPS)
           \         /
            v       v
        +------------------+
        | Global LB / Anycast|
        +---------+--------+
                  |
       +----------+-----------+
       | Connection Cell A/B  |
       |  Conn Managers       |
       |  local session map   |
       +----------+-----------+
                  |
       +----------+-----------+
       | Session Directory    |  user_id -> devices(cell, conn, ver)
       +----------+-----------+
                  |
       +----------+-----------+     +------------------+
       | Chat API Workers     |---->| Rate Limiter     |
       | send/sync/ack/authz  |     +------------------+
       +----------+-----------+
                  |
      +-----------+------------+--------------+
      |                        |              |
      v                        v              v
 +-----------+          +------------+  +------------+
 | Message   |          | Presence   |  | Push (APNs |
 | Service   |          | Service    |  | FCM)       |
 | durable   |          |            |  +------------+
 +-----+-----+          +------+-----+
       |                       |
       v                       v
  events bus ------> Push Router --> Connection Cells --> clients

 Membership / Graph cache consulted on send/sync
```

**Send path:**

```text
client Send(client_msgid)
  -> edge auth + rate limit
  -> membership check
  -> MessageService.Append (idempotent)
  -> returns message_id, ts
  -> ack client
  -> emit delivery job
  -> router pushes to online sessions
  -> offline -> Push Service
```

**Receive/push path:**

```text
event(message_id, thread, recipients[])
  -> for each recipient device in directory
  -> send frame to cell hosting conn
  -> client AckDelivered
```

**Reconnect/sync path:**

```text
connect -> register session
sync(cursor) -> Message/Sync service -> catch-up
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Edge is not source of truth for messages.**  
2. **Idempotent send** via `client_msgid` (+ user_id).  
3. **AuthZ on send/sync** — membership required.  
4. **Push is at-least-once**; clients dedupe by `message_id`.  
5. **Session leases expire**; no immortal ghost online.

#### 5.1.2 Delivery guarantees

| Guarantee | How |
|-----------|-----|
| Client→server durable | Ack after store |
| Server→client online | At-least-once push + ack |
| Offline | Push notify + sync |

#### 5.1.3 Ordering

Message Service assigns monotonic `message_id` / timestamp per thread. Edge does not reorder commits; clients sort by id.

#### 5.1.4 Drain & deploy

```text
mark cell read-only for new conns
wait in-flight sends
close conns with reconnect hint
clients jitter reconnect to other cells
```

### 5.2 Scalability

#### 5.2.1 Connection cells

```text
Cell = set of conn managers + local routing
Users not permanently pinned forever; sessions registered on connect
Directory is the source for push location
```

#### 5.2.2 Hot threads / groups

Large group fan-out executed by Message/Fanout service generating recipient batches; edge only delivers to sessions it hosts. Typing disabled or friends-only in huge threads.

#### 5.2.3 Rate limits

| Limit | Example |
|-------|---------|
| Sends / user / min | anti-spam |
| Sends / thread / min | raid protection |
| Connects / IP | reconnect storms |
| Typing / thread | coalesce 1/s |
| Sync / user | scraping |

#### 5.2.4 Backpressure

```text
If Message Service slow: fail send with retryable; shed typing first
If push backlog: drop ephemeral (typing/presence); never drop durable without retry path
```

#### 5.2.5 Progressive scale

| Scale | Add |
|-------|-----|
| 10× | Cells, directory, MQTT, RL |
| 100× | Regional affinity, fan-out service, sync tier |
| 1,000× | Hierarchical routers, approx presence, stricter shedding |

### 5.3 Maintainability

- Proto/schema versioning for frames.  
- Canary cells.  
- Explicit SLOs per RPC class.  
- Chaos: kill cell, directory blip, store latency.  
- Clear on-call boundaries: edge vs message store.

### 5.4 Presence

```text
Connection up -> Presence.online(device)
Heartbeat refresh
Disconnect / lease expire -> offline after grace
Aggregate: user online if any device online
Privacy: only expose to allowed graph
```

Edge may cache presence for typing targets; authoritative in Presence Service.

### 5.5 Multi-device sync

All devices registered. Sends from one device push to others (echo). Read receipts update all. Sync cursors per device or per user with device acks—product choice; MVP per-device cursor + thread read marks in store.

### 5.6 AuthZ / IDOR

Every `thread_id` access checks membership (cached with short TTL + invalidate on membership change). Never trust client-listed recipients for group send—server expands members.

### 5.7 Idempotency

```text
key = (user_id, client_msgid)
Message Service returns prior message_id if duplicate
Edge safe to retry on timeout
```

### 5.8 Security

TLS everywhere; token binding; payload size caps; attachment virus scan downstream; E2EE blobs opaque; rate limits; anomaly detection for spam blasts.

### 5.9 Observability

| Metric | Why |
|--------|-----|
| Concurrent conns | Capacity |
| Send p99 | UX |
| Store error rate | Dependency |
| Push lag | Realtime health |
| Reconnect rate | Incidents |
| RL rejects | Abuse |
| Directory miss | Routing bugs |

### 5.10 Client contracts

- Jittered exponential reconnect.  
- Dedup by message_id.  
- Idempotent send keys persisted locally until ack.  
- Sync after reconnect before trusting UI gaps.

### 5.11 Nested deep dive — Thrift / GraphQL / MQTT mapping

#### 5.11.1 Plane assignment

| Concern | Protocol | Why |
|---------|----------|-----|
| Persistent session, push frames | **MQTT** (mobile) / **WS** (web) | Light keepalive; bidirectional |
| Send when connected | MQTT RPC-ish or HTTPS | Prefer durable path clarity |
| History sync / large catch-up | **HTTPS** (GraphQL or Thrift/REST) | LB-friendly; fat payloads |
| Internal service calls | **Thrift/gRPC** | Typed, fast, mesh |
| Product graph queries | **GraphQL** optional facade | Aggregates thread metadata |

#### 5.11.2 Frame vs query

```text
MQTT frames: MSG_NOTIFY, RECEIPT, TYPING, PRESENCE, ACK, CONTROL
HTTPS: Sync(cursor), GetThread, SendMessage fallback, media bootstrap
Never stream multi-MB history exclusively over MQTT
```

#### 5.11.3 Schema versioning

```text
Connect negotiates protocol_ver + frame_ver
Support N-1; reject ancient vulnerable clients
GraphQL schema evolution additive; Thrift careful compat
```

#### 5.11.4 Anti-patterns

| Anti-pattern | Why |
|--------------|-----|
| All APIs only GraphQL subscriptions | Doesn’t solve fanout; mobile OS constraints |
| History only on MQTT | HOL blocking; hard LB |
| Edge invents message ids | Ordering/durability ownership wrong |

### 5.12 Nested deep dive — Auth

#### 5.12.1 Connect auth

```text
MQTT CONNECT / WS handshake carries session token
Edge validates → bind conn to user_id + device_id
Periodic revalidate; revoke list → drop conn
TLS mandatory
```

#### 5.12.2 Per-RPC AuthZ

| Op | Check |
|----|-------|
| SendMessage | thread membership (fail closed) |
| Sync | membership per thread requested |
| AckRead | membership |
| Presence subscribe | privacy graph rules |

**Deal-breaker:** trust client-supplied recipient lists for groups — server expands members.

#### 5.12.3 Membership cache

```text
key thread:{id}:members_ver → bitmap/set + ver
TTL 30–60s; hard invalidate on membership bus
Send path: cache miss → service; if both fail → 503 retryable (fail closed)
```

#### 5.12.4 IDOR battery

Attempt sync/send on non-member thread_ids; forge receipts; replay expired tokens — must 401/403.

### 5.13 Nested deep dive — Rate limits

#### 5.13.1 Key space

```text
rl:send:user:{id}
rl:send:thread:{id}
rl:conn:ip:{ip}
rl:conn:user:{id}
rl:typing:user_thread:{u}:{t}
rl:sync:user:{id}
```

#### 5.13.2 Example budgets

| Key | Limit | Notes |
|-----|-------|-------|
| send/user | 60/min | anti-spam |
| send/thread | 30/min | raid |
| typing/thread | 1/s coalesce | ephemeral |
| connect/ip | burst + sustained | reconnect storms |
| sync/user | protect history store | scraping |

#### 5.13.3 Implementation

Token buckets local+Redis; return 429 with Retry-After; brownout sheds typing before sends.

#### 5.13.4 Fairness

Celebrity threads: downstream fanout service; edge RL still applies per sender; don’t punish recipients.

### 5.14 Nested deep dive — Pagination (sync)

#### 5.14.1 Cursor model

```text
SyncRequest {thread_id? | inbox, cursor, limit}
cursor = opaque {last_message_id, ts, ver}
Response {events[], next_cursor, has_more}
```

Keyset on `(thread_id, message_id)` — **no OFFSET**.

#### 5.14.2 Gap fill

```text
reconnect → register session → Sync(cursor) → then rely on push
Push at-least-once; client dedupe message_id
UI must not assume push completeness
```

#### 5.14.3 Multi-device cursors

Per-device cursor MVP; thread read watermark in store for receipts across devices.

#### 5.14.4 Sync tier

Separate from connection managers so fat history doesn’t starve realtime frames.

### 5.15 Nested deep dive — Presence API

#### 5.15.1 API semantics

```text
Presence.online(user, device, ts)
Presence.heartbeat(device)
Presence.offline(device) / lease expire after grace
Query: GetPresence(targets[]) → {online|away|last_active} per privacy
Push: PresenceDelta to authorized subscribers (sparse)
```

#### 5.15.2 Aggregation

```text
user online iff any device online (after grace)
Flap protection: grace 30–60s on disconnect
Do not fanout heartbeat to all friends
```

#### 5.15.3 Privacy

Only expose to allowed graph; reduce precision (last_active buckets) per settings; edge must not broadcast globally.

#### 5.15.4 Load control

Under brownout: coalesce presence; reduce precision; drop subscriber pushes before durable message path.

### 5.16 Nested deep dive — Scale & deal-breakers

#### 5.16.1 Progressive scale

| Scale | Must |
|-------|------|
| 10× | Cells, session directory, MQTT, RL |
| 100× | Regional affinity, fanout service, sync tier |
| 1,000× | Hierarchical routers, approx presence, admission |

#### 5.16.2 Deal-breakers

1. Messages stored only in connection server memory.  
2. Unbounded typing/presence fanout.  
3. No idempotent `client_msgid`.  
4. Reconnect stampede without jitter.  
5. Client-trusted group recipient lists.  
6. Edge nested loops fanning to millions.

---

## 6. Wrap-Up

### 6.1 60-second pitch

> The Chat API layer terminates massive persistent connections in cells, authenticates and rate-limits RPCs, writes durably via Message Service with idempotency, and pushes events to devices through a session directory. Ephemeral signals are shed under load. Offline users get mobile push plus cursor sync. The edge never owns canonical history.

### 6.2 Deal-breakers

1. Storing messages only in connection server memory.  
2. Unbounded typing/presence fan-out.  
3. No idempotency on send.  
4. No reconnect jitter (stampede).  
5. Trusting client-provided group recipient lists without membership expansion.  
6. Edge nested loop fan-out to millions.

### 6.3 Scale one-liner

Connection cells + directory → regional affinity + fan-out service → hierarchical routers and aggressive ephemeral shedding.

---

## 7. Deeper / Related Interview Questions

### Q1. What belongs in the API layer vs Message Service?

**Answer:** API layer: connections, auth, RL, routing, push to sockets. Message Service: durable append, history, ids, thread state. Keep boundary clean.

### Q2. Why MQTT for mobile chat?

**Answer:** Lightweight keepalives, designed for unstable networks, binary framing, widely used in Messenger-class systems; reduces battery vs naive HTTP polling.

### Q3. How do you handle idempotent send?

**Answer:** Client generates `client_msgid`; store dedupes; retries safe after timeouts.

### Q4. At-least-once push implications?

**Answer:** Clients dedupe `message_id`; receipts may repeat; UI must be idempotent.

### Q5. How does session directory avoid ghosts?

**Answer:** Leases with heartbeat; on expire remove; disconnect explicit delete; version generation per connect.

### Q6. Multi-device read receipts?

**Answer:** Store thread read watermark; push update to other devices; each device updates UI.

### Q7. Large group optimization?

**Answer:** Dedicated fan-out; recipient batching; suppress typing; maybe broadcast trees; edge only last mile to local conns.

### Q8. What do you shed first under overload?

**Answer:** Typing/presence → noncritical pushes → accept send degradation with retryable errors; protect durable path fairness.

### Q9. Reconnect storm control?

**Answer:** Server hints retry-after; client jitter; connect admission tokens; brownout cells.

### Q10. Where is ordering enforced?

**Answer:** Durable Message Service per-thread sequence; clients sort; edge doesn’t invent order.

### Q11. HTTPS fallback?

**Answer:** Send/sync over HTTPS when persistent channel unavailable; push via mobile OS notifications.

### Q12. Presence privacy?

**Answer:** Only authorized viewers; last-active granularity may be reduced; edge must not broadcast globally.

### Q13. How to deploy connection servers?

**Answer:** Drain conns gracefully; rolling; clients reconnect; avoid simultaneous cell kills.

### Q14. Cross-region messaging?

**Answer:** User/thread home cell; cross-region RPC for send; push may cross region to device’s connection cell.

### Q15. E2EE impact on API layer?

**Answer:** Payload opaque; size limits; cannot server-side search/spam-inspect content easily—metadata spam signals remain.

### Q16. Sync vs push gap?

**Answer:** Push can miss; sync on foreground/reconnect fills gaps via cursor.

### Q17. Rate limit storage?

**Answer:** Token buckets in Redis/local+global; keys user, IP, thread.

### Q18. Authentication at connect?

**Answer:** Validate token on handshake; periodically revalidate; revoke → drop.

### Q19. Fan-out to author’s other devices?

**Answer:** Echo push so desktop sees phone-sent message; exclude sending conn optional (client correlates client_msgid).

### Q20. Observing silent drop bugs?

**Answer:** End-to-end tracing ids; client telemetry on missing sequences; store vs push lag dashboards.

### Q21. Why not put history sync on MQTT only?

**Answer:** Large payloads; request/response over HTTPS easier to cache/load-balance; keeps persistent channel for small realtime frames.

### Q22. Sticky sessions vs directory?

**Answer:** LB stickiness reduces churn; directory still required for multi-device and cell moves.

### Q23. Message edit/delete?

**Answer:** Downstream ops; edge pushes `message_edit` / `unsend` events; authz author only.

### Q24. Attachment handling?

**Answer:** Media uploaded elsewhere; chat send includes attachment_id; edge validates ownership/scan state.

### Q25. Capacity planning connections?

**Answer:** RAM/fd/CPU per conn; heartbeats/s; max conns per node; autoscale cells on conn count + send CPU.

### Q26. Thundering herd on celebrity thread?

**Answer:** Downstream collapse / batching; clients coalesce UI updates; rate-limit joins.

### Q27. Exactly-once delivery to client?

**Answer:** Not claimed; at-least-once + idempotent clients is the practical model.

### Q28. Directory partition tolerance?

**Answer:** Prefer availability with short wrong-route (push miss → sync heals) vs long blocking; careful consistency of leases.

### Q29. Security IDOR test?

**Answer:** Attempt sync/send on thread without membership; must 403; fuzz IDs.

### Q30. What changes at 100×?

**Answer:** Regional cells, separate sync tier, fan-out service, stricter ephemeral shedding, stronger admission control.

### Q31. Typing indicator implementation?

**Answer:** Client sends typing start/stop; edge throttles; push to online members except sender; TTL auto-clear.

### Q32. Clock skew?

**Answer:** Prefer server ids/timestamps; clients display server time.

### Q33. Dead letter for pushes?

**Answer:** If device never acks, rely on sync; optionally retry push N times then drop ephemeral.

### Q34. Brownout strategy?

**Answer:** Disable GIFs/previews, typing, presence precision; keep text send/receive.

### Q35. Success metrics?

**Answer:** Send success rate, send p99, push lag, reconnect success, RL false positives, durable dependency errors, missing-message client reports.

### Q36. How do Thrift internal APIs relate to MQTT clients?

**Answer:** Clients speak MQTT/WS/HTTPS; edge translates to Thrift/gRPC toward Message/Presence/Push services — clean boundary.

### Q37. GraphQL for chat — what belongs where?

**Answer:** GraphQL can expose thread metadata/send on HTTPS; realtime still needs persistent channel; subscriptions ≠ fanout architecture.

### Q38. Presence API privacy bug example?

**Answer:** Broadcasting online status to non-friends or on every heartbeat — fix with authz + sparse deltas + grace.

### Q39. Sync pagination vs MQTT backlog?

**Answer:** Persistent channel may drop when offline; sync cursor is source of catch-up; design for gap fill explicitly.

### Q40. Rate limit false positives?

**Answer:** Monitor RL rejects vs spam reports; tune per-user trust; avoid punishing group recipients for sender blasts.

### Q41. Why ack-after-durable at the API layer?

**Answer:** Edge crashes must not imply silent loss; client retries with `client_msgid` until store ack.

### Q42. Cell drain vs hard kill?

**Answer:** Drain: stop new conns, finish inflight, CONTROL reconnect with jitter; hard kill causes stampede — practice drain.

---

## Appendix A — Frame types

```text
MSG_NOTIFY, RECEIPT, TYPING, PRESENCE, CONTROL(reconnect), ACK
```

## Appendix B — Session record

```text
Session {user_id, device_id, conn_id, cell, protocol, lease_exp, app_ver}
```

## Appendix C — Send sequence diagram (text)

```text
Client -> Edge: Send(client_msgid)
Edge -> Store: Append
Store -> Edge: message_id
Edge -> Client: Ack(message_id)
Edge -> Router: Fanout job
Router -> Recipients: MSG_NOTIFY
```

## Appendix D — Cursor sync

```text
SyncRequest {cursor, limit}
SyncResponse {events[], next_cursor, has_more}
```

## Appendix E — Rate limit keys

```text
rl:send:user:{id}
rl:send:thread:{id}
rl:conn:ip:{ip}
rl:typing:user_thread:{u}:{t}
```

## Appendix F — Membership cache

```text
TTL 30–60s; hard invalidate on membership change bus
fail closed on cache+service miss for sends
```

## Appendix G — NFR card

```text
Ack after durable
p99 send < 200ms
Cells + directory
Idempotent client_msgid
Shed typing first
Jittered reconnect
```

## Appendix H — Reconnect hint

```json
{"action":"reconnect","retry_after_ms":1200,"jitter_ms":3000}
```

## Appendix I — Failure modes

| Failure | Edge behavior |
|---------|---------------|
| Store down | Fail send retryable; sync degraded |
| Directory down | Push miss risk; sync heals; maybe sticky local only briefly |
| Cell death | Clients reconnect |

## Appendix J — Group fan-out handoff

```text
Edge -> MessageService.Send
MessageService -> FanoutService.Expand(thread)
FanoutService -> PushRouter batches
```

## Appendix K — Presence grace

```text
disconnect -> grace 30–60s before offline (flap protection)
```

## Appendix L — Payload limits

```text
text max N KB; e2ee blob max M KB; reject oversize early
```

## Appendix M — Worked conn math

```text
5K servers × 20K conns = 100M conns
heartbeat 30s -> ~3.3K hb/s/server trivial vs messages
```

## Appendix N — Brownout levels

| Level | Action |
|-------|--------|
| L1 | Drop typing |
| L2 | Coalesce presence |
| L3 | Delay noncritical pushes |
| L4 | Admit sends only for paid/priority (rare) |

## Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Cell | Connection cluster |
| Directory | user→session lookup |
| client_msgid | Idempotency key |
| Cursor | Sync position |
| Shed | Drop lower priority traffic |

## Appendix P — 30m checklist

1. Bound API layer vs store.  
2. Connection cells + directory.  
3. Durable ack + idempotency.  
4. Push + offline push + sync.  
5. RL + shedding + reconnect.  
6. Deal-breakers.

## Appendix Q — AuthZ matrix

| Op | Check |
|----|-------|
| Send | member |
| Sync thread | member |
| Read receipt | member |
| Presence subscribe | friend/privacy |

## Appendix R — Echo suppression

```text
push to all devices except optional exclude_conn_id of sender
```

## Appendix S — Tracing

Propagate `trace_id` / `message_id` across edge→store→router→client telemetry.

## Appendix T — Metrics card

conn_count, send_p99, store_err, push_lag, reconnect_rate, rl_drop, typing_qps

## Appendix U — Protocol versioning

Negotiate on connect; support N-1 frames; reject ancient vulnerable versions.

## Appendix V — Progressive scale

| Scale | Must |
|-------|------|
| 10× | Cells, MQTT, RL |
| 100× | Regional, fan-out svc |
| 1,000× | Hierarchical push, approx presence |

## Appendix W — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Websocket everywhere” | Mobile MQTT benefits |
| “Store in Redis at edge” | Durability/scale lie |
| “Exactly-once sockets” | Not realistic; dedupe |

## Appendix X — Pseudocode send

```text
def send(user, req):
  rl.check(user, req.thread_id)
  assert membership(user, req.thread_id)
  mid = message_svc.append(user, req)  # idempotent
  push_router.enqueue(mid)
  return mid
```

## Appendix Y — Load test scenarios

Reconnect storm, group blast, typing flood, store latency injection, cell kill.

## Appendix Z — Success bar

Clients stay connected efficiently, sends are durably acknowledged, online push is fast, offline catch-up works, and the edge survives celeb-sized fan-out and deploy drains without becoming the database.

---


## Appendix AA — Cell placement policy

```text
New connections: hash(user_id) % cells OR least-loaded cell
Directory records actual cell
Push uses directory, not LB stickiness alone
```

## Appendix AB — Offline catch-up sequence

```text
1. Device offline; messages durable in Message Service
2. APNs/FCM wakes app (metadata only)
3. App connects MQTT; registers session
4. Sync(cursor) pulls missed events
5. UI converges; push used for future realtime
```

## Appendix AC — Spoofing / IDOR cases

| Attack | Defense |
|--------|---------|
| Send to thread not member | membership check |
| Sync other user inbox | auth binds user_id |
| Forge receipts for others | authz on receipt |
| Replay old token | expiry + revoke list |

## Appendix AD — Brownout runbook

```text
Page: Message Service p99↑
Edge: enable L1 shed typing
If worsening: L2 presence coalesce
Protect send path with admission fairness
Communicate degraded UX if needed
```

## Appendix AE — Closing interview lines

```text
"API layer owns connections, auth, RL, and last-mile push; Message Service owns durable history.
Ack after durable; idempotent client_msgid; cells + session directory; shed ephemeral first."
```

## Appendix AF — Protocol mapping cheat sheet

| Client need | MQTT/WS | HTTPS GraphQL/REST | Internal Thrift/gRPC |
|-------------|---------|--------------------|----------------------|
| Send | yes | fallback | Message.Append |
| Sync history | no (prefer HTTPS) | yes | Sync service |
| Typing | yes | rare | optional |
| Presence delta | yes | query API | Presence service |
| Push notify | yes | — | Push router |

## Appendix AG — AuthZ fail-closed table

| Dependency down | Send | Sync | Typing | Presence query |
|-----------------|------|------|--------|----------------|
| Membership | fail | fail | fail | degrade/fail |
| Token validator | drop conn | 401 | drop | 401 |
| Directory | send OK | OK | OK | push may miss→sync heals |

## Appendix AH — Rate limit brownout coupling

```text
L1: RL typing harder / drop typing frames
L2: coalesce presence
L3: admit sends with fairness; 429 excess
Never: silently ack send without durable store
```

## Appendix AI — Sync pagination examples

```text
First open: cursor=null → latest N events
Reconnect: cursor=last_acked → gap fill
Thread jump: cursor per thread_id
Reject OFFSET; reject huge limit (>100)
```

*End of Facebook Chat API Layer system design.*
