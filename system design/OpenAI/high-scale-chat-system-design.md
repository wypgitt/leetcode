# System Design: High-Scale Chat / Messenger

> **Focus areas:** Connection fleet · 1:1 + groups · Offline push · Ordering · Presence · Hybrid fan-out · 100M–1B users  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Relation:** Standalone mega-scale messenger (not Slack workspaces). May share patterns with `slack-system-design.md` but is a complete design for consumer/prosumer chat at extreme scale.  
> **Quality bar:** Correct fan-out math; hybrid fan-out; no unjustified per-user full inbox copies at extreme scale

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

Goal: **bound the messenger**—1:1 vs groups vs optional channels, delivery guarantees, and connection/push realities at hundreds of millions of users.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Product shape? | Consumer messenger: **1:1**, **group chats**, optional large rooms/channels | Different fan-out strategies by cohort size |
| F2 | Message types? | Text, emoji reactions, images/video pointers, optional voice notes | Object storage for media; message row holds metadata |
| F3 | Delivery semantics? | At-least-once to devices; **exact display order per conversation** | Durable log + per-conversation seq; client sync |
| F4 | Read receipts / delivery? | Delivered + read for 1:1; optional aggregated for groups | Separate receipt channel; careful write amplification |
| F5 | Offline? | Store & sync history; **mobile push** for wakeups | Push ≠ full message body always (privacy/size) |
| F6 | Presence? | Online / offline / last seen (privacy settings) | Ephemeral store; approximate; not durable SoT |
| F7 | Typing? | Best-effort typing indicators | Ephemeral pub/sub; drop under load |
| F8 | History? | Infinite scroll; search Phase 1.5 | Conversation-partitioned storage; cold tier later |
| F9 | Groups size? | Typical <50; support up to few thousand; broadcast channels separate | Hybrid fan-out thresholds |
| F10 | Multi-device? | Same user, multiple sessions; sync across devices | User-session fan-out; device inbox cursors |
| F11 | E2EE? | Optional Phase 2 (Signal-style); MVP server-side readable | Design hooks; don’t block MVP |
| F12 | Spam / block / report? | Blocks, reports, rate limits mandatory at consumer scale | Authz + abuse pipeline on send path |

**MVP functional scope (lock with interviewer):**

1. Auth’d users; contacts or phone/username discovery (pick one).  
2. **1:1** and **group** conversations; send/edit/delete text; media pointers.  
3. **Per-conversation total order**; multi-device sync via cursors.  
4. **Realtime** delivery over persistent connections for online sessions.  
5. **Offline**: history sync + push notification wake.  
6. **Presence** best-effort + typing best-effort.  
7. Delivery/read receipts for 1:1; simplified for groups.  
8. Block list + basic rate limits.

**Out of MVP (explicitly defer):**

- Full Slack-style workspace admin / channel directory product  
- Strong E2EE + sealed sender (mention as Phase 2)  
- Perfect global presence  
- Stories / status / payments  
- Server-side full-text search at 1B (phase carefully)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Online delivery latency | Feels instant | p50 < 200ms, p99 < 1s in-region after persist |
| N2 | Durability | ACK’d messages never lost | RPO ≈ 0 for ACK’d sends |
| N3 | Ordering | Per-conversation total order | Server seq SoT |
| N4 | Availability | Chat is critical | 99.9%+ messaging; degrade presence/typing first |
| N5 | Multi-region | Global users | Active-active **connection gateways**; **home cell** for conversation writes |
| N6 | Fan-out fairness | Large groups don’t melt cluster | Hybrid fan-out; isolation |
| N7 | Privacy | Blocks honored; no leak across convos | Membership/ACL on every read/fan-out |
| N8 | Scale | 100M–1B users class | Connection fleet + hybrid fan-out mandatory |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. A sends to B (both online) → persist → push to B’s sessions → ACK.  
2. B offline → persist; push notification; on open, sync from cursor.  
3. Group of 20 → persist once; fan-out to online members; others sync later.  
4. Multi-device: phone + desktop both receive; read on one updates receipts.  
5. User blocks sender → future sends rejected / dropped per policy.  
6. Edit/delete → new event referencing `message_id` + seq; not reorder.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-tap send | Client `msg_id` idempotency → one persisted message |
| Offline compose | Client queue; flush with idempotency |
| Large group 50K (channel-like) | **Do not** write per-user inbox copy; hybrid / pull |
| Hot celebrity broadcast | Channel mode: fan-out on read / active subscribers only |
| Reconnect after sleep | Sync `after_seq` gaps; don’t rely on push alone |
| Presence flap | Debounce; conn_count across devices |
| Push privacy | Notification may be opaque (“New message”) if needed |
| Slow consumer | Kick to catch-up mode; don’t block conversation write |
| Cross-region friends | Write to conversation home; edge conn forwards |
| Receipt storms in huge groups | Aggregate or disable precise receipts |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Registered users | 10M | 100M | 1B | 10B (theo) |
| MAU | 5M | 50M | 500M | 5B |
| DAU | 1M | 10M | 100M | 1B |
| Peak concurrent connections | 500K | 5M | 50M | 500M |
| Messages sent / day | 100M | 1B | 10B | 100B |
| Avg recipients / msg (blended) | 2.5 | 2.5 | 3 | 3–4 |
| Peak **ingest** QPS | ~2K | ~20K | ~200K | ~2M |
| Peak **online push ops**/s | ~5K–15K | ~50K–150K | ~0.5–1.5M | ~5–15M+ |
| Conversations (active/week) | 20M | 200M | 2B | 20B |
| Group share of msgs | ~30% | ~30% | ~35% | ~35% |
| Push notifications / day | ~50M | ~500M | ~5B | ~50B |
| Presence updates / day | ~1B | ~10B | ~100B | ~1T |

**What each jump forces:**

- **10×:** Dedicated WS/HTTP2/QUIC gateway fleet; conn directory; Kafka/async fan-out; Redis presence.  
- **100×:** Conversation **home cells**; hybrid fan-out; media CDN; push provider sharding; receipt aggregation.  
- **1,000×:** Extreme connection tier; conversation sharding; cold history; presence aggregation; optional channel/broadcast product mode; careful **no mega inbox tables**.

### 1.5 Etc. (Constraints & Assumptions)

- Not building Slack workspaces; **conversation-centric** social graph.  
- Optional “channels” = large read-heavy rooms with different fan-out (document explicitly).  
- Single primary cloud multi-AZ; global edge gateways.  
- Reference Slack-like patterns for large rooms, but **1:1 inbox economics differ**.

**Scope statement:**

> Design a global messenger for 1:1 and group chat with per-conversation ordering, multi-device realtime delivery, offline sync + push, and best-effort presence—starting ~1M DAU / 500K conns and scaling through 10× / 100× / 1,000× using hybrid fan-out and home-cell single-writer conversations—without unjustified full per-user message copies at extreme scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Connections

```text
Baseline peak conns: 500,000
State/conn ≈ 10–30 KB → 5–15 GB across gateway fleet
Gateway capacity (evented): ~50K–200K conns/node
→ tens of nodes baseline; at 1000× (500M conns) → thousands of gateway nodes + regions
```

### 2.2 Fan-out math (correctness critical)

**Ingest vs delivery are different:**

```text
Peak ingest baseline ~2,000 msg/s
Blended online delivery factor:
  Not every recipient is online; not every msg goes to huge groups.

Online delivery ops ≈ ingest × (avg online recipients notified)

Example baseline:
2,000 msg/s × 3 online notify ≈ 6,000 delivery ops/s (order-of-magnitude)

At 100×: 200K ingest × 3 ≈ 600K delivery ops/s
At 1000×: 2M ingest × 3–5 ≈ 6–10M delivery ops/s  (plus multi-device multiplier!)
```

**Multi-device multiplier:** if avg 1.5 online sessions/user notified:

```text
600K recipient-notifies × 1.5 ≈ 900K session pushes/s at 100×
```

**Large group trap (why hybrid):**

```text
Naive: 1 msg to 100,000-member room × write per member inbox
= 100,000 row writes per message

If that room gets 10 msg/s:
1M inbox writes/s from ONE conversation → impossible / absurd cost

Therefore: store message ONCE in conversation log; members pull/sync;
push only to currently connected active subscribers (or notify badges).
```

### 2.3 Storage

```text
Avg message metadata ~200–500 B (text small; media is pointer)
100M msgs/day × 400 B = 40 GB/day metadata
1,000×: 100B msgs/day × 400 B = 40 TB/day

Retained 1 year at 100× (10B/day):
10B × 365 × 400 B ≈ 1.46e15 B ≈ 1.5 PB / year
(Not 1.5 EB—watch units.)
```

Media object storage often dominates; estimate separately (e.g. 20% msgs with 200 KB avg → huge).

### 2.4 “Inbox copy” cost (deal-breaker math)

| Approach | Write amp for group size G | When OK |
|----------|----------------------------|---------|
| Fan-out-on-write (copy to each inbox) | ×G | Small G (≤20–50), 1:1 |
| Fan-out-on-read (single log) | ×1 write | Large G, channels |
| Hybrid | small G write-fanout; large G read-fanout | **Chosen** |

**Do not** propose per-user full copies for all messages at 1B users without a threshold model.

### 2.5 Bandwidth

```text
Realtime events ~200–500 B
1M session pushes/s × 300 B ≈ 300 MB/s  (manageable)
Push provider traffic separate (APNs/FCM)

History sync storms after outage can dwarf steady realtime—rate-limit catch-up.
```

### 2.6 Presence traffic

```text
Heartbeat every 30s × 50M online = ~1.7M presence writes/s if naïve
→ shard, TTL refresh coalescing, don’t persist every beat to DB
```

### 2.7 Critical bottlenecks

1. Connection gateway fleet + conn directory  
2. Hot conversation partitions  
3. Large-group fan-out amplification  
4. Push provider quotas  
5. Receipt/unread write amplification  
6. Cross-region write RTT to home cell  

---

## 3. High-Level Design

### 3.1 Core entities

```text
User → Devices/Sessions (conn)
Conversation (1:1 or group) → Members
Message(conversation_id, seq, sender, body_ref, ...)
Cursor(user, conversation, device?) → last_read_seq / last_sync_seq
```

### 3.2 Persist-first messaging path

```text
Send API/WS → authz member → idempotency check
  → assign seq (single-writer partition)
  → durable append message
  → ACK sender
  → async fan-out (realtime) + push decide + search index later
```

**Invariant:** Never ACK before durable persist. Fan-out may lag; sync repairs.

### 3.3 Fan-out strategy (hybrid) — deep trade-off

| Mode | Mechanism | Use |
|------|-----------|-----|
| **Write fan-out** | After persist, enqueue notify for each member (or active sessions) | 1:1, small groups (G ≤ T, e.g. 50) |
| **Read fan-out** | Persist only to conversation log; clients poll/sync; push optional badge | Large groups / channels |
| **Hybrid** | Threshold T on member count or “conversation kind” | **Default at scale** |

**Session routing:** Conn directory `user_id → {gateway_id, session_id}[]`. Group notifies by **user**, then expand sessions.

**Ownership:** Fan-out workers own delivery attempts; conversation partition owns seq assignment. Do not let every gateway invent seq.

### 3.4 Options: storage for messages

| Store | Pros | Cons | Deal-breaker |
|-------|------|------|--------------|
| Postgres partition by conv | TX, simple MVP | Hot write limits | 1B-user all-in-one PG |
| Cassandra/Scylla/Dynamo | Wide-time writes | Multi-key TX harder | Needing cross-conv TX |
| Kafka + cold store | Great pipeline | Not primary random history UX alone | Using Kafka as only history store for sync UX without KV |

**Chosen:** Conversation-keyed log store (Cassandra-style or Dynamo) + Postgres for user/graph/membership; MVP can start Postgres and migrate message log.

### 3.5 Offline delivery & push

```text
On persist:
  for each recipient:
    if online sessions: realtime push
    else if prefs allow: enqueue push notification job
History always durable in conversation log regardless
```

Push payload: minimal (conversation_id, collapse_key); client fetches body over TLS after unlock if privacy requires.

### 3.6 Ordering

- `conversation_id + seq` unique, monotonic per conversation (or shard).  
- Holes OK; duplicates not.  
- Client gap-fill via history API.  
- No global order across conversations.  
- Merge “inbox view” by `server_ts` approx for list UI.

**Sequencer options:** DB monotonic in TX; or Redis INCR with care about holes; single-writer actor per conversation partition.

### 3.7 Presence & typing

- Heartbeat → Redis TTL; `conn_count` for multi-device.  
- Broadcast presence only to relevant watchers (friends / open chat)—**not** global.  
- Typing: ephemeral to conversation active subscribers; never durable.

**Deal-breaker:** Postgres row update per typing event.

### 3.8 Unread & receipts

| Data | Approach |
|------|----------|
| Last read | `(user_id, conversation_id) → last_read_seq` |
| Unread count | Derive or maintain counter with reconcile |
| Delivery receipts 1:1 | Update on session ACK; notify sender |
| Group receipts | Aggregate (“25 read”) or omit at scale |

### 3.9 Multi-region

| Plane | Mode |
|-------|------|
| WS/TCP gateways | Active-active near users |
| Conversation writes | **Home cell** single-writer |
| User directory | Global lookup user→home, conversation→home |
| Presence | Regional with aggregation; approximate OK |
| History replicas | Optional async read replicas; session consistency caveats |

### 3.10 Trade-offs summary

| Concern | Choice | Deal-breaker |
|---------|--------|--------------|
| Large group storage | Single conversation log | Per-member full copy |
| Fan-out | Hybrid threshold | Eager write fan-out to 1M members |
| Cache membership | Short TTL + invalidation | Stale allow on private groups forever |
| Media | Object storage + CDN | Inline multi-MB in message row |
| Search | Async index Phase 1.5 | Blocking send on indexer |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Mobile/Desktop Clients
        |
        |  QUIC/HTTP2/WS
        v
+-------------------+     +------------------+
| Edge Conn Gateway |---->| Conn Directory   |
| (active-active)   |     | (user→sessions)  |
+---------+---------+     +------------------+
          |
          | RPC to home cell
          v
+---------------------------------------------+
| Home Cell                                   |
|  Chat Service (authz, idempotency, seq)     |
|  Message Log Store (by conversation)        |
|  Membership / Graph Store                   |
|  Outbox → Kafka                             |
+-------------------+-------------------------+
                    |
      +-------------+--------------+
      v                            v
 Fan-out Workers              Push Workers
 (session notify)             (APNs/FCM)
      |
      v
 Gateways push events to sessions

Presence Service (Redis) ← heartbeats from gateways
Media Store/CDN ← upload path separate
```

### 4.2 Sequence: 1:1 online

```text
A-gateway → ChatService: Send(conv, client_msg_id, body)
ChatService: authz; idempotency; seq++; durable append; ACK
Outbox → Fanout: notify B
Fanout → ConnDir: B sessions
Fanout → B-gateway: deliver event
B-gateway → device
Optional: delivery receipt path back to A
```

### 4.3 Sequence: offline + push + sync

```text
Persist message (B offline)
PushWorker → FCM/APNs (collapse per conv)
B opens app → connect gateway → Sync(conv, after_seq)
ChatService → history pages → client catch-up
```

### 4.4 Sequence: large group hybrid

```text
Persist once to conversation log (seq++)
If G > T:
  notify only active subscribers / online members who joined room presence
  others: badge via lightweight counter OR discover on sync/list
Else:
  write-fanout notify all members’ online sessions + push offline
```

### 4.5 Scale cells

```text
Global Directory: conversation_id → home_cell
                 user_id → home_cell (profile), devices anywhere
Cell: message log shards | membership shards | fan-out consumers
Edge: conn gateways worldwide
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. ACK ⇒ durable message in conversation log.  
2. `(conversation_id, seq)` unique; seq never reused.  
3. Idempotent send via `(sender_id, client_msg_id)` (or conv-scoped).  
4. Membership authz on send/history/fan-out.  
5. Fan-out failure ≠ message loss (sync repairs).  
6. Block list enforced on send path.  
7. At-least-once delivery to clients; exactly-once display via client dedupe by `message_id`.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Gateway crash | Client reconnect; sync gaps; conn dir TTL cleanup |
| Fan-out lag | Backlog consumers; clients pull |
| Home cell failover | Fence epoch; RPO on in-flight outbox; reconnect |
| Push provider down | Queue + retry; in-app sync still works |
| Hot partition | Split rare mega-convo; rate-limit bots |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Monolith + PG + Redis + few WS nodes |
| 10× | Gateway fleet; Kafka outbox; conn directory cluster |
| 100× | Cells; hybrid fan-out; sharded message log; push sharding |
| 1000× | Multi-region homes; cold/hot history; presence aggregation; broadcast mode for mega rooms; QoS classes |

**Unread at extreme scale:** maintain counters carefully; periodic reconcile to `max_seq - last_read_seq`.

**Noisy groups / bots:** per-conversation rate limits; member flood control; shuffle tenant/org if business chat.

### 5.3 Maintainability

- Protocol versioning for clients  
- Feature flags for receipt modes  
- Chaos: kill gateways, partition Kafka, block APNs  
- Privacy reviews on push payloads and last-seen  

### 5.4 Progressive scale deep dive (1× → 1000×)

**1× (~1M DAU)**

- Monolith chat API + Postgres messages (`(conversation_id, seq)`).  
- Few WS nodes with sticky LB; Redis for presence.  
- Push via one provider account.  
- Fan-out inline for small groups acceptable.

**10× (~10M DAU)**

- Dedicated gateway fleet; conn directory in Redis Cluster.  
- Outbox → Kafka → fan-out workers (decouple persist from push).  
- Message store still PG if careful partitioning—or start Cassandra/Dynamo migration for messages.  
- Rate limits + basic abuse.

**100× (~100M DAU)**

- Conversation **home cells**; edge gateways global.  
- Hybrid fan-out mandatory; channel/broadcast kind.  
- Receipt aggregation; unread counter service.  
- Media CDN; async virus scan.  
- Push provider sharding / multi-app credentials.

**1000× (~1B DAU class)**

- Extreme conn tier (regional gateway POPs).  
- Hot/cold message storage; older history in object/columnar.  
- Presence aggregation & watch-list limits.  
- QoS: drop typing/presence first under load.  
- Dedicated broadcast pipeline for mega rooms / celebrities.

### 5.5 Hybrid fan-out thresholds (tuning)

| Conversation kind | Default mode | Notes |
|-------------------|--------------|-------|
| DM (2) | Write-notify | Trivial |
| Group ≤ 50 | Write-notify + offline push | Classic |
| Group 51–2k | Online notify + selective push | Medium |
| Channel / >2k | Read-fanout + active subscribers | Critical |
| Broadcast mega | Publish log + follower pull / sampled push | Special |

Measure: p99 persist latency, fan-out lag, write amp, cost/$ per message.

### 5.6 Multi-device sync details

```text
User U devices D1, D2
Message arrives → fan-out to sessions(D1), sessions(D2)
Read on D1 → update last_read_seq → notify D2 (read sync event)
Push token per device; collapse_key per conversation avoids storms
Notification settings per device/platform
```

**Cursor types:** `last_sync_seq` (delivery catch-up) vs `last_read_seq` (unread UI)—don’t conflate.

### 5.7 Ordering edge cases

| Case | Handling |
|------|----------|
| Seq hole | Client fetches gap |
| Edit | New event `message_edited` with same `message_id`; sort by edit event seq in timeline overlays |
| Delete | Tombstone; retain seq |
| Backfill migration | Allocate seq ranges carefully; never reuse |
| Sharded hot convo | Prefer avoid; if must, epoch+local_seq merge rules documented |

### 5.8 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Per-user inbox for all msgs | O(G) writes; dies on large groups |
| Client timestamps as order | Clock skew chaos |
| Presence in SQL | Write melt |
| Block send on full fan-out | Tail latency / availability hit |
| Active-active seq | Forks |
| Push as durability | Silent loss |

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| SoT | Conversation log + seq |
| Fan-out | Hybrid by group size / kind |
| Connections | Edge fleet + directory |
| Offline | Sync + push wake |
| Multi-region | AA gateways; SW home cell |
| Presence | Ephemeral approximate |

### 6.2 Risks

1. Accidental O(G) inbox copies on large G  
2. Conn directory as SPOF without HA  
3. Receipt write storms  
4. Underestimating multi-device amplify  
5. Active-active writes corrupting seq  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Product: 1:1/group, offline, scale target |
| 5–15 | Persist + seq + idempotency |
| 15–25 | Hybrid fan-out math |
| 25–35 | Gateways, push, multi-device |
| 35–45 | Presence, multi-region, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Fan-out & storage

**Q: Why not store messages in each user’s inbox like email?**  
A: Write amplification kills large groups. Use conversation log + hybrid notify. Email-style works for small G only.

**Q: What’s the threshold T?**  
A: Empirically 25–100 members; also product kind (channel vs group). Measure CPU/write cost.

**Q: How do users see messages in large rooms they weren’t online for?**  
A: On open, history sync by seq; optional badge from counter service.

**Q: Fan-out ownership?**  
A: Writers persist + outbox; workers deliver; gateways only push to local sockets.

### 7.2 Ordering & sync

**Q: Client timestamps for order?**  
A: No—server seq is SoT. Client ts for optimistic UI only.

**Q: Gap detection?**  
A: Expect contiguous seq; on hole, fetch `[from, to)`.

**Q: Multi-device conflicting edits?**  
A: Last-write-wins with server order for edits; or version vector Phase 2—keep simple LWW by seq/event id.

**Q: Exactly-once to client?**  
A: At-least-once push + client dedupe by `message_id`.

### 7.3 Connections

**Q: Sticky sessions?**  
A: Helpful but not required if conn directory updated; drain for deploys.

**Q: How many conns per box?**  
A: Tens/hundreds of thousands evented; watch memory/buffers; separate from chat business logic.

**Q: Long-poll vs WS vs QUIC?**  
A: WS/QUIC preferred for bidirectional; long-poll fallback for hostile networks.

**Q: Thundering reconnect after outage?**  
A: Jittered reconnect; sync rate limits; shed presence first.

### 7.4 Push & offline

**Q: Is push enough for reliability?**  
A: No—best-effort wake. Durability is conversation log + sync.

**Q: Notification storms?**  
A: Collapse keys per conversation; mute prefs; rate limits.

**Q: Data in push payload?**  
A: Privacy trade-off; often limited; fetch on open.

### 7.5 Presence

**Q: Exact online for 1B users to all friends?**  
A: Don’t. Scoped watchers; pull on open chat list; approximate last-seen.

**Q: Flapping?**  
A: Grace TTL; multi-device conn_count.

**Q: Store presence in DB?**  
A: No—Redis/memory TTL.

### 7.6 Receipts & unread

**Q: Read receipts in 10K group?**  
A: Aggregate or disable; don’t emit 10K events per reader.

**Q: Unread badge correctness?**  
A: Counters + reconcile; accept rare drift briefly.

### 7.7 Multi-region

**Q: Why not active-active message writes?**  
A: Dual sequencers → duplicate/conflicting seq. Home cell single-writer.

**Q: User travels?**  
A: Connect to nearest edge; RPC to home; latency trade-off.

**Q: Conversation between users in different regions?**  
A: Conversation still has one home; pick by creator or deterministic hash; both edges talk to that home.

### 7.8 Security & abuse

**Q: Enumeration of phone numbers?**  
A: Rate-limit discovery; privacy-preserving contact match (hashed) carefully.

**Q: Spam?**  
A: Reputation, rate limits, block graphs, ML async; challenge on anomaly.

**Q: E2EE impact?**  
A: Server fan-out still possible with ciphertext; search/push previews constrained; key directory needed.

### 7.9 Media

**Q: Upload path?**  
A: Client → object storage multipart; message contains URL + hash; CDN read; virus scan async.

**Q: Fan-out media bytes?**  
A: Never through WS; only metadata; clients fetch media separately.

### 7.10 Comparison to Slack design

**Q: What’s different from Slack?**  
A: No workspace-first tenancy; consumer graph; heavier mobile push; larger absolute user counts; fewer admin ACL features; channels optional as broadcast mode.

**Q: Shared patterns?**  
A: Persist-first, per-container seq, hybrid fan-out, edge WS, ephemeral presence, home cells.

### 7.11 Algorithms & structures

**Q: Conn directory structure?**  
A: `user_id → set(session{gateway, conn_id, device})` in Redis Cluster; secondary index gateway→sessions for drain.

**Q: Membership for large room?**  
A: Sharded member lists; active-subscriber set for push; don’t load 1M IDs every message.

**Q: Idempotency map?**  
A: `(user_id, client_msg_id) → message_id` with TTL/unique.

**Q: Rate limit?**  
A: Token bucket per user and per conversation.

### 7.12 Reliability drills

**Q: Kafka down?**  
A: Persist still OK; degrade async fan-out—fall back to sync notify for small convos carefully; clients sync.

**Q: Redis conn dir down?**  
A: Lose realtime routing; persist+sync remain; reconstruct on reconnect (session registers again).

**Q: Split-brain seq?**  
A: Fence home primary; refuse writes without leadership epoch.

### 7.13 Interview trap: units & fan-out

**Q: 10B msgs/day × 50 recipients inbox copies?**  
A: 500B writes/day—absurd. Hybrid/single-log required.

**Q: 100M conns × 30 KB?**  
A: 3 PB? No—100M×30KB=3×10^12 B=**3 TB** memory cluster-wide (still huge; sharded across many gateways).

**Q: Peak ingest 2M/s with G=100 write fan-out?**  
A: 200M notify/s—only viable with heavy sampling/hybrid/active-subset.

### 7.14 Cancel / resume / reconnect (resolved)

**Q: Does reconnect “resume stream” or “sync”?**  
A: **Sync by cursor/seq**, not opaque stream resume. Push is wake; history API is truth for gaps.

**Q: Stop typing / presence?**  
A: Ephemeral; no durable cancel. Connection drop eventually marks offline after grace.

---

## 8. Appendices

### 8.1 Schema sketches

```text
users(user_id, handle, ...)
devices(device_id, user_id, push_token, platform)
conversations(conversation_id, kind=dm|group|channel, home_cell, member_count)
conversation_members(conversation_id, user_id, role, joined_at, muted, last_read_seq)
messages(conversation_id, seq, message_id, sender_id, type, body, media_ref, created_at, edited_at, deleted)
idempotency(sender_id, client_msg_id, message_id, conversation_id)
```

### 8.2 Hybrid fan-out checklist

- [ ] Define threshold T and channel kind  
- [ ] Single append SoT  
- [ ] Active subscriber set for large rooms  
- [ ] Push collapse keys  
- [ ] Sync API with seq gaps  
- [ ] Never O(G) durable copies for mega G  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Conversation log | Append-only ordered messages for one chat |
| Hybrid fan-out | Write-fanout small; read-fanout large |
| Conn directory | Map user sessions → gateway |
| Home cell | Single-writer region for a conversation |
| Collapse key | Push dedupe key per conversation |
| Seq | Monotonic per-conversation order key |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Persist-first, seq, WS, basic push |
| 10× | Gateway fleet, conn dir, async fan-out |
| 100× | Cells, hybrid fan-out, receipt controls |
| 1000× | Global edge, cold history, broadcast mode, presence agg |

### 8.5 Fan-out decision tree (interview whiteboard)

```text
onPersist(message):
  G = member_count(conversation)
  if kind == channel OR G > T_large:
      append conversation_log only
      notify(active_subscribers)           # online viewers / pushers
      bump_lightweight_badge(optional)
  else if G <= T_small:                    # e.g. ≤ 50
      append conversation_log
      for user in members:
         notify_online_sessions(user)
         if all sessions offline: enqueue_push(user)
  else:  # medium
      append conversation_log
      notify_online_sessions(members)
      push only for mentions / muted overrides
```

### 8.6 Worked fan-out examples (correct arithmetic)

**Example A — 1:1 message**

```text
Ingest writes: 1 message row
Online notify: 1 recipient × 1.5 devices ≈ 1.5 session pushes
Push offline: 0 or 1
Inbox copies: 0 extra (both read same DM log) 
```

**Example B — group G=20, all online, 1.2 sessions/user**

```text
1 message append
20 × 1.2 = 24 session pushes
If naïve per-user inbox copy also: +20 writes → avoid; log is enough
```

**Example C — channel G=500,000, 2,000 active subscribers online**

```text
1 message append (SoT)
Realtime pushes ≈ 2,000 (not 500,000)
Other members see on open via history sync
If mistaken write-fanout inbox: 500,000 durable writes/msg → system death
```

**Example D — peak ingest 200K msg/s blended × 3 online notifies**

```text
600K recipient-notifies/s
× 1.5 sessions ≈ 900K session delivers/s
Gateway fleet must be designed for this, not for ingest alone
```

### 8.7 Connection directory operations

| Op | Behavior |
|----|----------|
| Register | On connect: `SADD user:{id}:sessions session_json`; set TTL refresh |
| Heartbeat | Refresh session TTL |
| Unregister | On disconnect / TTL expiry |
| Lookup | Fan-out worker `SMEMBERS` → group by gateway → RPC batch |
| Drain gateway | List sessions on gateway; send reconnect; mark draining |

**Failure:** directory lost → clients reconnect and re-register; miss realtime until then; **messages still safe in log**.

### 8.8 Sync API sketch

```text
GET /conversations/{id}/messages?after_seq=N&limit=100
→ [{seq, message_id, ...}, ...] sorted by seq

GET /users/me/conversations?cursor=...
→ conversation list with last_message preview + unread

POST /conversations/{id}/read {last_read_seq}
```

Gap fill is client-driven; server may also send `gap_hint` if it detects jump.

### 8.9 Presence privacy matrix

| Setting | Behavior |
|---------|----------|
| Everyone | Friends/contacts can see online + last seen |
| Contacts only | Restrict watch graph |
| Nobody | Appear offline; last seen hidden |
| “Last seen recently” buckets | Quantize to reduce leak precision |

### 8.10 Interview “say this” summary (60 seconds)

> Persist-first into a per-conversation ordered log with server seq; ACK only after durability; fan out asynchronously via a connection directory to edge gateways; use **hybrid fan-out**—write-notify for small groups, single-log + active-subscriber notify for large rooms—so we never create O(G) inbox copies at mega scale; offline users sync by cursor and get push wakes; presence is ephemeral Redis; multi-region uses active-active gateways and **single-writer home cells** for conversation seq.

### 8.11 Extra traps

| Trap | Pushback |
|------|----------|
| “Email-style inbox for WhatsApp scale” | Write amp on groups |
| “Kafka as sole message history” | Awkward random access/sync UX without KV/log store |
| “Global message order” | Unnecessary; per-conversation enough |
| “Strong presence for all friends every second” | Traffic explosion |
| “Active-active seq in two regions” | Duplicate seq / forks |
| “100M × 30KB = 3PB RAM” | **3 TB** cluster-wide |

### 8.12 Reliability test plan

1. Kill gateway mid-push → client sync recovers.  
2. Inject duplicate client_msg_id → one message.  
3. Partition Kafka → persist OK; catch-up fan-out later.  
4. Large channel load test proves no per-member durable copy.  
5. Home cell failover → fence; measure duplicate delivers (client dedupe).  

### 8.13 Related systems map

```text
Edge Conn Gateway ↔ Conn Directory
        ↓
Chat Service (home) → Message Log + Membership DB
        ↓ outbox
Fan-out Workers → Gateways
Push Workers → APNs/FCM
Presence Service (Redis)
Media Upload → Object Storage/CDN
Abuse/Spam Pipeline (async)
```

### 8.14 Optional E2EE Phase-2 hooks (non-MVP)

- Client-side encryption; server stores ciphertext blobs.  
- Fan-out unchanged (opaque payloads).  
- Push previews limited; search constrained.  
- Identity key directory service; safety number UX.  
- Server still enforces membership & rate limits on ciphertext size.

---

*End of high-scale chat system design.*
