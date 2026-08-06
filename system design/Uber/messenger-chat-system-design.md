# System Design: Facebook Messenger-like Chat

> **Focus areas:** Connection fleet · 1:1 + groups · Offline push · Ordering · Presence · Hybrid fan-out · Idempotent send · Multi-device sync  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Interview theme:** Uber — consumer-scale realtime messaging (often used to probe WebSockets, fan-out, and consistency under global users)  
> **Quality bar:** Correct fan-out math; hybrid fan-out; conversation home-cell writes; no unjustified per-user full inbox copies at extreme scale

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

Goal: **bound the messenger**—1:1 vs groups vs optional large rooms, delivery guarantees, multi-device sync, and at which scale the design must still hold. Uber interviewers often care as much about **connection fleet + fan-out math** as about the message table schema.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Product | Consumer messenger (Messenger / WhatsApp-class patterns) | Slack workspaces / enterprise admin |
| Realtime | Persistent connections + push wake | Pure polling chat |
| Storage | Conversation-partitioned durable log | Email-style folders as primary model |
| Uber lens | Streaming, fan-out, idempotency, degrade modes | Building Facebook Social Graph |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Product shape? | **1:1** and **group chats**; optional large rooms later | Different fan-out by cohort size |
| F2 | Message types? | Text, reactions, images/video **pointers**, voice notes | Object storage for media; message row = metadata |
| F3 | Delivery semantics? | At-least-once to devices; **exact display order per conversation** | Durable log + per-conversation `seq`; client sync |
| F4 | Read / delivery receipts? | Delivered + read for 1:1; aggregated/optional for groups | Separate receipt path; careful write amplification |
| F5 | Offline? | Store & sync history; **mobile push** to wake | Push ≠ full message body (privacy/size) |
| F6 | Presence? | Online / offline / last seen (privacy settings) | Ephemeral store; approximate; not durable SoT |
| F7 | Typing? | Best-effort typing indicators | Ephemeral pub/sub; drop under load |
| F8 | History? | Infinite scroll; search Phase 1.5 | Conversation-partitioned storage; cold tier later |
| F9 | Group size? | Typical <50; up to a few thousand; channels separate | Hybrid fan-out thresholds |
| F10 | Multi-device? | Same user, multiple sessions; sync across devices | User-session fan-out; per-device cursors |
| F11 | E2EE? | Optional Phase 2; MVP server-readable OK | Design hooks; don’t block MVP |
| F12 | Abuse? | Block, report, rate limits mandatory | Authz + abuse checks on send path |
| F13 | Edit / delete? | Soft delete + edit events | Append events; never rewrite history order |
| F14 | Mentions / replies? | Reply threads light; quote reply OK | Parent `message_id` refs |

**MVP functional scope (lock with interviewer):**

1. Auth’d users; contacts or username discovery (pick one).  
2. **1:1** and **group** conversations; send/edit/delete text; media pointers.  
3. **Per-conversation total order**; multi-device sync via cursors.  
4. **Realtime** delivery over persistent connections for online sessions.  
5. **Offline**: history sync + push notification wake.  
6. **Presence** best-effort + typing best-effort.  
7. Delivery/read receipts for 1:1; simplified for groups.  
8. Block list + basic rate limits + idempotent client `msg_id`.

**Out of MVP (explicitly defer):**

- Full Slack-style workspace admin / channel directory  
- Strong E2EE + sealed sender (mention as Phase 2)  
- Perfect global presence consistency  
- Stories / status / in-chat payments  
- Server-side full-text search at 1B users (phase carefully)  
- Active-active dual writers on the same conversation

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Online delivery latency | Feels instant | p50 < 200ms, p99 < 1s in-region after persist |
| N2 | Durability | ACK’d messages never lost | RPO ≈ 0 for ACK’d sends |
| N3 | Ordering | Per-conversation total order | Server `seq` is SoT |
| N4 | Availability | Chat is critical | 99.9%+ messaging; degrade presence/typing first |
| N5 | Multi-region | Global users | Active-active **connection gateways**; **home cell** for conversation writes |
| N6 | Fan-out fairness | Large groups don’t melt cluster | Hybrid fan-out; isolation |
| N7 | Privacy | Blocks honored; no leak across convos | Membership/ACL on every read/fan-out |
| N8 | Throughput | See scale table | Split **send QPS**, **fan-out**, **conn heartbeats**, **sync reads** |
| N9 | Idempotency | Client retries safe | `(sender_id, client_msg_id)` unique |
| N10 | Cost | Push/conn dominate OPEX at scale | Hybrid fan-out; drop ephemeral first |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. A sends to B (both online) → persist → push to B’s sessions → ACK to A.  
2. B offline → persist; push notification; on open, sync from cursor.  
3. Group of 20 → persist once; fan-out to online members; others sync later.  
4. Multi-device: phone + desktop both receive; read on one updates receipts.  
5. User blocks sender → future sends rejected / dropped per policy.  
6. Edit/delete → new event referencing `message_id` + new `seq`; does not reorder past.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-tap send | Client `msg_id` idempotency → one persisted message |
| Offline compose | Client queue; flush with idempotency on reconnect |
| Large group 50K (channel-like) | **Do not** write per-user inbox copy; hybrid / pull |
| Hot celebrity broadcast | Channel mode: fan-out on read / active subscribers only |
| Reconnect after sleep | Sync `after_seq` gaps; don’t rely on push alone |
| Presence flap | Debounce; `conn_count` across devices |
| Push privacy | Notification may be opaque (“New message”) |
| Slow consumer | Kick to catch-up/sync mode; don’t block conversation write |
| Cross-region friends | Write to conversation home; edge conn forwards |
| Receipt storms in huge groups | Aggregate or disable precise receipts |
| Media upload fail mid-send | Message may reference pending upload; or two-phase (upload then send) |
| Partition of home cell | Fail closed on writes; serve recent cache reads carefully |
| Member removed mid-send | Authz check at persist; late fan-out skipped for removed |
| Clock skew on client | Server assigns `seq` + `server_ts`; client ts advisory |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 10M | 100M | 1B | (same class, denser) |
| DAU | 3M | 30M | 300M | 300M+ |
| Concurrent connections | 500K | 5M | 50M | 100M+ |
| Messages sent / day | 200M | 2B | 20B | 50B+ |
| Peak **send** QPS | ~5K | ~50K | ~500K | ~1M+ |
| Peak **fan-out deliveries** | ~20K | ~200K | ~2M | ~5M+ |
| Avg group size | 8 | 8 | 10 | 12 |
| Media fraction | 15% | 20% | 25% | 30% |
| Avg message metadata | 500 B | 500 B | 600 B | 600 B |
| History retained hot | 90d | 90d | 30d hot + cold | tiered |

**What each jump forces:**

- **10×:** Sticky connection fleet; conversation sharding; Redis presence; push provider scale.  
- **100×:** Hybrid fan-out; home cells; separate receipt/presence planes; media CDN; abuse ML.  
- **1,000× / mega-scale:** Channel mode for large rooms; regional connection PoPs; cold storage; connection multiplexing optimizations; cell isolation for hot celebrities.

### 1.5 Etc. (Constraints & Assumptions)

- We build **messaging platform**, not the entire social graph / feed.  
- Clients: iOS, Android, web; multiple sessions per user.  
- **Single primary cloud**, multi-AZ; multi-region with **home cell** for conversation mutation.  
- Message payloads may contain PII → encrypt at rest; scrub logs.  
- “Exactly-once delivery to device” is **not** promised; **exactly-once persist** via idempotency + **at-least-once delivery** to sessions.

**Scope statement:**

> Design a consumer messenger supporting 1:1 and group chat with durable per-conversation ordering, realtime delivery over a connection fleet, offline sync + push, best-effort presence/typing, multi-device cursors, and hybrid fan-out—starting at ~10M MAU and evolving through 10× / 100× / 1,000× with conversation home cells and degraded ephemeral features under load.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split traffic classes (do not lump)

| Class | Baseline peak | 100× | Notes |
|-------|---------------|------|-------|
| Send / persist | 5K QPS | 500K QPS | Durable write + seq assign |
| Fan-out pushes to conns | 20K QPS | 2M QPS | Dominates at scale |
| Sync / history reads | 10K QPS | 1M QPS | Cache + partition scans |
| Receipts | 5K QPS | 500K QPS | Can exceed sends if chatty |
| Presence heartbeats | 50K QPS | 5M QPS | **Must be cheap / sampled** |
| Typing events | 20K QPS | 2M QPS | Droppable |
| Push notifications | 2K QPS | 200K QPS | Provider rate limits |

**Critical insight:** At 100×, **presence heartbeats and fan-out** can dwarf durable sends. Design ephemeral planes to shed load; never put heartbeats on the conversation OLTP write path.

### 2.2 Fan-out math

```text
Baseline: 5K sends/s × avg fan-out factor
1:1: factor ≈ 1–2 (other user devices)
Groups: avg size 8 → ~7 other members × ~1.3 sessions ≈ ~9 deliveries potential
Mix: assume 60% 1:1, 40% group → effective fan-out ≈ 0.6*1.5 + 0.4*9 ≈ 4.5
5K × 4.5 ≈ 22.5K delivery attempts/s  (matches ~20K table)

100×: 500K × 4.5 ≈ 2.25M deliveries/s
If naive per-user inbox write on every send:
500K × 4.5 ≈ 2.25M inbox writes/s → expensive; hybrid avoids for large N
```

**Unit check:** 20B messages/day ÷ 86400 ≈ 231K msg/s average; peak 2–3× → ~500–700K/s. Table’s 500K peak send at 100× is consistent with spiky diurnal patterns if average is lower—state assumptions explicitly in interview.

### 2.3 Storage

```text
Message metadata ~500–600 B
Baseline 200M/day × 500 B ≈ 100 GB/day raw
90 days hot: ≈ 9 TB (+ indexes ~2× → ~18 TB provision)

100×: 20B/day × 600 B ≈ 12 TB/day
30 days hot: ≈ 360 TB hot tier → must tier to cold/object
Media: pointers only in message store; blobs in object storage + CDN
  If 25% messages have 200 KB media: 0.25 × 20B × 200KB = 1 EB/day? 
  WAIT: 0.25 × 20e9 × 2e5 B = 0.25 × 4e15 = 1e15 B = 1 PB/day media
  → aggressive compression, retention, client-size limits, dedupe
```

**Unit check:** Media at consumer scale is the real storage bill—not text rows. Cap upload sizes; lifecycle policies.

### 2.4 Connection fleet

```text
500K concurrent conns baseline
If each conn server holds 50–100K conns (realistic with efficient event loop):
  need ~5–10 servers baseline; 100× → 500–1000+ servers (plus headroom)
Heartbeat every 30s: 500K/30 ≈ 17K HB/s baseline; 50M/30 ≈ 1.7M HB/s at 100×
→ terminate HB at edge; don’t forward to message store
```

### 2.5 Latency budget (online 1:1)

```text
Client → edge conn → Send Service → durable persist+seq → fan-out → peer conn → peer
Budget p99 in-region: 30 + 40 + 80 + 40 + 30 ≈ 220ms (tight but plausible)
Cross-region: add 100–200ms+; home cell may be remote for one party
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Fan-out amplification** for large groups / celebrities  
2. **Connection fleet** churn and thundering reconnects  
3. **Hot conversation** (group chat storm) single partition  
4. **Presence/typing** overload if not sheddable  
5. **Receipt write amplification**  
6. **Media upload / CDN** cost and abuse  
7. **Push provider** rate limits during outages (catch-up storms)

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
User          → accounts; devices/sessions
Conversation  → 1:1 or group; home_cell; membership
Message       → immutable payload + server seq in conversation log
Event         → message | edit | delete | receipt | membership change
Session       → device connection; cursor (last_ack_seq per convo or global inbox view)
Inbox cursor  → per-user sync pointer(s)
```

**Message state (logical):**

```text
CLIENT_PENDING → (send) → PERSISTED (assigned seq) → DELIVERED_TO_SESSION* → READ*
* delivery/read are per-recipient projections, not mutations of message body
```

### 3.2 Options: fan-out strategy

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Write-time fan-out (per-user inbox) | Fast reads | Write amp; huge groups explode | Groups ≫ 1K or celebrity rooms |
| B. Read-time fan-out (pull from convo log) | Write once | Read amp; slow for many convos | Users with thousands of active convos without indexes |
| C. **Hybrid** | Best of both | Complexity; threshold tuning | Skipping hybrid at 100× consumer scale |

**Chosen path:**

- **Small conversations (N ≤ T, e.g. 50–100):** write-time fan-out to online sessions + optional inbox pointers.  
- **Large conversations:** persist once in conversation log; online members get push via pub/sub topic; offline sync pulls by `seq`.  
- **Channels / broadcast:** subscriber pull + active-watcher push only.

### 3.3 Options: connection layer

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Short polling | Simple | Latency/batt drain | Product needs “instant” |
| B. Long polling | OK MVP | Inefficient at 50M conns | Mega-scale |
| C. WebSocket / persistent TCP | Efficient duplex | Sticky routing; reconnect storms | Ignoring sticky/session map |
| D. gRPC streaming | Strong typing | Mobile ecosystem care | — |

**Chosen:** Persistent connections (WebSocket) at edge **PoPs**; session registry maps `user_id → [conn_server]`.

### 3.4 Ordering & idempotency

**Invariant:** Within a conversation, `seq` is contiguous (or gap-tolerant with explicit sync), assigned by **single-writer** partition for that conversation.

```text
Send path:
1. Authz: member? not blocked?
2. Idempotency lookup (sender_id, client_msg_id) → return old if exists
3. Append to conversation log; assign seq; durable ACK
4. Async: fan-out to online sessions; enqueue push for offline
```

**Deal-breaker:** Multiple uncoordinated writers assigning `seq` for the same conversation (split-brain ordering).

### 3.5 Multi-region clarity

| Plane | Mode |
|-------|------|
| Connection gateways | Active-active globally (PoPs) |
| Conversation append / seq | **Single-writer home cell** per conversation |
| User inbox / unread counters | Home or carefully CRDT/approx; define RY W |
| Presence | Regional ephemeral; cross-region approximate |
| Media | Object storage multi-region / CDN |

**Deal-breaker:** Active-active dual append to same conversation without a conflict/ordering story.

### 3.6 Receipts, presence, typing (separate planes)

| Signal | Durability | Shedding |
|--------|------------|----------|
| Message body | Durable before ACK | Never shed accepted |
| Delivery receipt | Best-effort durable / batched | Aggregate under load |
| Read receipt | Durable enough for UX | Coalesce; disable in huge groups |
| Presence | Ephemeral | Sample / debounce |
| Typing | Ephemeral | First drop under load |

### 3.7 Push notifications

```text
Offline or backgrounded → Push Planner
  → respect mute, quiet hours, privacy (opaque body)
  → provider (APNs/FCM) with collapse keys per conversation
  → on open: sync API is SoT, not the push payload
```

**Deal-breaker:** Treating push as guaranteed delivery of message content.

### 3.8 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Message SoT | Conversation log (partitioned) | Natural order | Only per-user mailboxes |
| Seq assignment | Home-cell single writer | Total order | DB without partition affinity |
| Online delivery | Conn fleet + session map | Low latency | Polling every 1s |
| Large groups | Hybrid / pull | Survive celebrity | Full inbox write × N |
| Presence | Redis/memory regional | Cheap | Strong durable presence TX |
| Media | Object store + CDN | Cost/size | Inline BLOBs in message DB |
| Unread counts | Cached counters + repair | Fast badge | COUNT(*) on every open |
| Search | Async index Phase 2 | Don’t block send | Sync ES on send path |

### 3.9 Components

1. **API Gateway / Edge** — auth, TLS, rate limits.  
2. **Connection Fleet** — WebSocket servers; heartbeats; local session tables.  
3. **Session Directory** — `user_id → connections` (Redis/common store).  
4. **Send / Chat Service** — authz, idempotency, append.  
5. **Conversation Store** — sharded log + membership.  
6. **Fan-out Service** — online push; hybrid rules.  
7. **Sync / History Service** — cursor catch-up.  
8. **Push Service** — APNs/FCM.  
9. **Presence Service** — ephemeral.  
10. **Media Service** — upload URLs, virus scan, CDN.  
11. **Abuse / Block Service** — blocks, rate limits, reports.  
12. **Notification preferences** — mutes, quiet hours.

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Mobile/Web Clients
           |
           |  WSS / HTTPS
           v
  +---------------------+
  | Edge / Conn Fleet   |  (active-active PoPs)
  |  heartbeats, sticky |
  +----------+----------+
             |
    +--------+--------+------------------+
    |                 |                  |
    v                 v                  v
+---------+   +--------------+   +--------------+
| Send /  |   | Sync/History |   | Presence /   |
| Chat API|   | API          |   | Typing       |
+----+----+   +------+-------+   +------+-------+
     |               |                  |
     v               v                  |
+------------------------+              |
| Conversation Store     |              |
| (home cell, by conv)   |              |
+-----------+------------+              |
            |                           |
            v                           v
     +--------------+            +-------------+
     | Fan-out      |----------->| Session Dir |
     | (hybrid)     |            | + Conn push |
     +------+-------+            +-------------+
            |
            v
     +--------------+     +---------------+
     | Push Service |     | Media / CDN   |
     +--------------+     +---------------+
```

### 4.2 Sequence: online 1:1 send

```text
A-client     ConnA      Chat Service     Conv Store     SessionDir     ConnB      B-client
   |           |             |               |              |            |           |
   |--send---->|------------>|               |              |            |           |
   |           |             |--idempot+append------------->|            |           |
   |           |             |<--seq ACK--------------------|            |           |
   |           |             |--fanout(B)------------------>|            |           |
   |           |             |              |               |--push----->|--msg----->|
   |<-ack(seq)-|<------------|              |               |            |           |
```

### 4.3 Sequence: offline + sync

```text
A sends → persist → B not in SessionDir → Push Service (collapse key)
B opens app → Sync(after_seq / inbox cursor) → History API → catch-up → render
```

### 4.4 Sequence: reconnect storm mitigation

```text
Fleet restart → clients reconnect with jittered backoff
SessionDir TTL short; don’t thundering-herd history full download
Prefer: resume cursors + incremental sync
```

### 4.5 Hybrid fan-out decision

```text
on_persist(conv, msg):
  members = membership(conv)
  if len(members) <= T:
    for u in members:
      push_online_sessions(u, msg)
      maybe_inbox_pointer(u, msg)
  else:
    publish(conv_topic, msg)           # online watchers
    # offline: no per-user copy; badge via sparse receipts / pull
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **ACK ⇒ durable** append in conversation home cell (quorum/replica).  
2. **Idempotent send** on `(sender_id, client_msg_id)`.  
3. **Single-writer seq** per conversation (partition actor / ordered log).  
4. **Authz on send and sync** — membership + block checks.  
5. **At-least-once delivery** to sessions; clients dedupe by `message_id`.  
6. **Push is wake, not SoT** — sync repairs gaps.  
7. **Edits/deletes are new events**, not silent rewrites of `seq` history.  
8. **Degrade ephemeral first** (typing → presence → receipts → still take sends).  
9. **Fan-out failure ≠ lose message** — message already persisted.  
10. **Media**: virus scan + signed URLs; never trust client-supplied open URLs blindly.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular chat service; PG/Cassandra-style conv partitions; Redis session; WS fleet |
| 10× | Shard by `conversation_id`; sticky conn; push scaling; media CDN |
| 100× | Hybrid fan-out; home cells; separate presence/receipt planes; abuse automation |
| 1000× | Channel mode; PoP expansion; cold tier; cell isolation for hot keys; QoS classes |

### 5.3 Maintainability

- Protocol versioning (client ↔ conn ↔ API).  
- Feature flags for fan-out threshold `T`.  
- Shadow dual-write carefully avoided; prefer canary cells.  
- Golden path integration tests: idempotent send, gap sync, block.  
- Chaos: kill conn servers; verify no message loss for ACK’d sends.  
- Clear ownership: Messaging Store vs Edge Conn vs Push vs Abuse.

### 5.4 Progressive scale narrative

**1×:** Single region, PG for messages + membership, Redis sessions, WS servers, FCM/APNs, simple write-time fan-out for all groups (N small).  

**10×:** Conversation sharding; connection fleet autoscaling; presence Redis cluster; unread counters; media pipeline.  

**100×:** Home cells by conversation; hybrid fan-out; receipt coalescing; push privacy modes; search async; strong abuse rate limits; cross-region friends with forward-to-home.  

**1000×:** Large-room/channel product mode; hierarchical fan-out (watcher sets); cold storage + restore; regional edge with smart routing; load shedding playbooks; celebrity/incident runbooks.

### 5.5 Hot conversation / thundering group

Symptoms: one group chat with very high send rate; single partition CPU; fan-out queue lag.  

Mitigations:

- Bound send rate per conversation / per user.  
- Coalesce typing; batch fan-out.  
- Split “chat” vs “live comments” product modes.  
- For extreme: require channel semantics (append-only log + pull).  

### 5.6 Multi-device sync model

```text
Each device stores:
  cursors: map conv_id → last_received_seq
  or a global event inbox for small-N hybrid

On connect:
  for each active conv: GET /sync?after=seq
  apply in seq order; dedupe message_id

Read receipts:
  device A marks read → receipt event → other devices update UI
```

**Deal-breaker:** Assuming one cursor per user without per-device delivery state when push-to-session matters.

### 5.7 Exactly-once vs at-least-once

| Layer | Guarantee |
|-------|-----------|
| Persist | Effectively once via idempotency key |
| Delivery to device | At-least-once |
| Display | Client dedupe + seq order |
| Receipts | At-least-once; coalesce |

### 5.8 Security & privacy

- E2EE Phase 2 changes server role (ciphertext blobs; metadata still visible).  
- Blocks enforced server-side on send.  
- Report pipeline async.  
- Signed media URLs with short TTL.  
- Don’t log message bodies in clear in shared logging systems.

### 5.9 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Per-user inbox write for 1M-member room | Meltdown |
| Dual-active writers for same conv seq | Order bugs / dup seq |
| ACK before durability | Lost chat (SEV) |
| Presence as strongly consistent global truth | Cost + lies |
| Sync ES/solr on send path | Latency SEVs |
| Push as only delivery | Missed messages |
| No idempotency on send | Double messages |
| Receipts equal priority to body path | Amplification outage |

### 5.10 Uber-flavored angles (why they ask this)

- **Streaming / WebSockets** map to driver location & trip updates.  
- **Idempotency** maps to payments and dispatch.  
- **Fan-out & degrade modes** map to marketplace event storms.  
- Mention briefly: same session directory patterns can serve trip realtime channels—but **don’t** conflate chat store with trip state machine.

---

## 6. Wrap-Up

### 6.1 Designed

Consumer messenger: durable conversation logs with single-writer sequencing, idempotent sends, connection fleet delivery, offline sync + push wake, hybrid fan-out, sheddable presence/typing/receipts, media via object storage, multi-device cursors, home-cell multi-region writes.

### 6.2 Decisions to defend

1. Conversation log as SoT + server `seq`  
2. Idempotent `(sender, client_msg_id)`  
3. Hybrid fan-out with threshold `T`  
4. Active-active conn edge; single-writer home cell for append  
5. Push is wake, sync is truth  
6. Separate ephemeral planes with load shedding  
7. Authz/block on send and history  
8. Media out of band  

### 6.3 Risks

- Reconnect storms after fleet deploy  
- Hot group partitions  
- Push provider outages  
- Unread counter drift  
- Abuse / spam arms race  
- Cross-region latency for home cell  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope 1:1/groups; defer E2EE; lock NFRs |
| 5–12 | Send path + idempotency + seq |
| 12–22 | Conn fleet + fan-out hybrid |
| 22–30 | Offline sync + push |
| 30–38 | Multi-region home cell; scale jumps |
| 38–45 | Degrade modes, abuse, Q&A traps |

### 6.5 Closer

> **Messenger:** persist-first with idempotent append and per-conversation total order; deliver via connection fleet with hybrid fan-out; repair via cursor sync; shed typing/presence before messages; home-cell writes at global scale.

---

## 7. Deeper / Related Interview Questions

### 7.1 Ordering & consistency

**Q: Why per-conversation order, not global?**  
A: Users care about conversation semantics; global total order doesn’t scale and isn’t needed.

**Q: Can seq have gaps?**  
A: Prefer contiguous; if gaps allowed, sync protocol must fetch gaps explicitly. Document.

**Q: Causal order across conversations?**  
A: Not required for MVP messenger.

**Q: Client timestamps for order?**  
A: No—server seq is SoT; client ts for display hints only.

### 7.2 Fan-out

**Q: How to choose threshold T?**  
A: Measure write amp vs read amp; start ~50–100; channels always pull.

**Q: Celebrity announcement to 50M followers?**  
A: Not a “group chat”—use broadcast/channel product with fan-out-on-read.

**Q: Online-only push enough?**  
A: No—offline needs push wake + sync.

### 7.3 Connections

**Q: Sticky sessions?**  
A: Yes to a conn server; SessionDir updated on connect/disconnect; TTL + heartbeat.

**Q: What if SessionDir says connected but socket dead?**  
A: Heartbeat expiry; false positives OK if sync repairs; avoid thundering pushes.

**Q: How many conns per box?**  
A: Tens of thousands to low hundreds of thousands depending on language/runtime; load test.

### 7.4 Multi-device & receipts

**Q: Read on phone—desktop updates?**  
A: Publish receipt events to user’s other sessions; persist read watermark per user×conv.

**Q: Group read receipts?**  
A: Expensive; often “seen by N” aggregates or disable.

### 7.5 Storage

**Q: SQL vs Cassandra/Dynamo vs Kafka log?**  
A: Conversation append fits partitioned log / wide-column / SQL with `(conv_id, seq)` PK. Kafka alone is awkward for random history fetches—use for CDC/async.

**Q: Message edit storage?**  
A: New event `EDIT` with `target_message_id` + patch; UI materializes latest.

### 7.6 Push

**Q: Collapse keys?**  
A: Per conversation so 100 messages don’t make 100 notifications.

**Q: Sensitive content?**  
A: Opaque notifications; fetch on open.

### 7.7 Presence

**Q: Last-seen accuracy?**  
A: Approximate; privacy settings; never block messaging on presence store failure.

**Q: Cross-region presence?**  
A: Eventual; “online” may lag—product OK.

### 7.8 Abuse & security

**Q: Spam flood?**  
A: Per-user send QPS; new-user limits; graph signals; block + report; shadowban.

**Q: E2EE impact?**  
A: Server can’t search/filter bodies; spam harder; metadata still visible; key management complexity.

### 7.9 Multi-region

**Q: Where is home cell for 1:1?**  
A: Pick by first writer, or by user-pair hash, or by primary user region; migrating home is a project.

**Q: DR failover**  
A: Fence old writer epoch; expect brief write unavailability; clients retry idempotently.

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| “Kafka guarantees exactly-once chat” | Delivery ≠ persist; clients still dedupe |
| Full mesh sockets between users | Doesn’t scale; need servers |
| Store all media in MySQL BLOB | Cost/latency disaster |
| Strong global presence | Wrong priority |
| Microservice per message type | Absurd |
| Skip idempotency “because TCP” | Mobile retries happen |

### 7.11 Metrics & SLOs

| Metric | Why |
|--------|-----|
| Send ACK p99 | UX |
| Persist success rate | Reliability |
| Fan-out lag | Online freshness |
| Sync gap repair time | Offline UX |
| Conn churn rate | Fleet health |
| Push send errors | Provider health |
| Duplicate persist rate | Idempotency efficacy |
| Hot partition CPU | Scale risk |

### 7.12 Related Uber systems

**Q: Same design as trip realtime updates?**  
A: Similar **connection fleet + session directory**; different SoT (trip state machine vs conversation log) and authz.

**Q: Chat for rider–driver?**  
A: Often short-lived trip-scoped channels with stricter TTL and PII rules—call out as variant.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- conversations
(conversation_id UUID PK,
 type TEXT, -- dm|group|channel
 home_cell TEXT,
 created_at, created_by)

-- members
(conversation_id, user_id, role, joined_at, muted_until,
 PRIMARY KEY(conversation_id, user_id))

-- messages (partitioned by conversation_id)
(conversation_id, seq BIGINT,
 message_id UUID,
 sender_id UUID,
 client_msg_id TEXT,
 kind TEXT, -- text|image|edit|delete|system
 body_ref TEXT, -- inline small or pointer
 media_refs JSONB,
 created_at,
 PRIMARY KEY(conversation_id, seq),
 UNIQUE(sender_id, client_msg_id))

-- read_watermarks
(user_id, conversation_id, read_seq, updated_at,
 PRIMARY KEY(user_id, conversation_id))

-- blocks
(user_id, blocked_user_id, created_at, PRIMARY KEY(user_id, blocked_user_id))
```

### 8.2 API checklist

- [ ] `POST /v1/conversations`  
- [ ] `POST /v1/conversations/{id}/messages` + `Idempotency-Key` / `client_msg_id`  
- [ ] `GET /v1/conversations/{id}/messages?after_seq=`  
- [ ] `POST /v1/conversations/{id}/read` `{read_seq}`  
- [ ] WebSocket: `auth`, `send`, `ack`, `recv`, `typing`  
- [ ] `POST /v1/media/upload-url`  
- [ ] `POST /v1/blocks`  
- [ ] `GET /v1/inbox/sync`  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Seq | Monotonic per-conversation server order |
| Home cell | Single-writer region/cell for a conversation |
| Hybrid fan-out | Write-time for small N; pull/topic for large N |
| Session directory | Map user → connection servers |
| Collapse key | Push dedupe key per conversation |
| Cursor | Client sync pointer (`after_seq`) |
| Shedding | Drop ephemeral under load |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Persist-first, WS, idempotency, push, basic fan-out |
| 10× | Shards, session dir, media CDN, unread counters |
| 100× | Hybrid fan-out, home cells, ephemeral planes, abuse |
| 1000× | Channels, cold tier, PoPs, QoS shedding, hot-key cells |

### 8.5 Client send state machine

```text
LOCAL_QUEUED → IN_FLIGHT → ACKED(seq) → (optional) DELIVERED → READ
     ↑              |
     +---- retry on timeout/disconnect (same client_msg_id)
```

### 8.6 Load shedding order

```text
1. Typing
2. Detailed presence
3. Per-message delivery receipts in large groups
4. Push coalescing more aggressively
5. History search / non-critical extras
NEVER: drop durable ACK'd persist for accepted sends without explicit brownout product mode
```

### 8.7 Fan-out threshold worksheet

```text
Cost_write_time ≈ C_w * N
Cost_read_time  ≈ C_r * (messages_pulled_by_offline + watchers)
Choose T where expected cost minimized; revisit quarterly with metrics
```

### 8.8 Reconnect jitter

```text
backoff = min(cap, base * 2^attempt) + rand(0, jitter)
on_fleet_deploy: server sends "reconnect_after_ms" advisory
```

### 8.9 Interview “say this” summary (60 seconds)

> Persist messages first with idempotent client IDs and a single-writer per-conversation sequence; deliver online via a sticky WebSocket fleet and session directory; wake offline with push but repair with cursor sync; use hybrid fan-out so large rooms don’t multiply writes; keep presence/typing ephemeral and sheddable; multi-region gateways with home-cell appends.

### 8.10 Reliability test plan

1. Double send with same `client_msg_id` → one row.  
2. Kill conn server → clients reconnect; no loss of ACK’d messages.  
3. Offline 24h → sync catch-up complete.  
4. Block user → send rejected.  
5. Large group threshold → no per-member inbox explosion.  
6. Home cell failover → fenced writers; clients retry idempotently.  

### 8.11 Observability SLOs

| SLO | Example target |
|-----|----------------|
| Send ACK p99 (in-region) | < 300ms |
| Online delivery p99 | < 1s after persist |
| Durable loss of ACK’d | ≈ 0 |
| Fan-out lag p99 (small groups) | < 1s |
| Sync catch-up for 1000 msgs | < 2s |

### 8.12 Privacy modes

| Mode | Push body | Last seen | Headers |
|------|-----------|-----------|---------|
| Default | Preview snippet | Friends | Normal |
| Locked | “New message” | Nobody | Restricted |
| Enterprise (if ever) | Opaque | Off | MDM hooks |

### 8.13 Related systems map

```text
Clients → Conn Fleet → Chat/Send → Conversation Store (home cell)
                    → Sync/History
                    → Presence/Typing (ephemeral)
         Fan-out → SessionDir → Conn push
                 → Push Service
         Media → Object Store/CDN
         Abuse/Blocks → authz on send
```

### 8.14 Extra traps

| Trap | Pushback |
|------|----------|
| Global message IDs as order | Use per-conv seq |
| Redis-only message store | Durability lie |
| One Postgres for 1B users | Won’t shard itself |
| Receipts inline in message row updates | Hot-row contention |
| “We’ll E2EE later without metadata plan” | Metadata still leaks |

### 8.15 Rider–driver chat variant (Uber twist)

Short-lived `trip_id` conversation:

- Membership = rider + driver for trip window.  
- Auto-close / archive after trip + retention policy.  
- Stricter PII + safety tooling.  
- Same persist + realtime patterns; **TTL and moderation** differ.

---

*End of messenger / chat system design.*
