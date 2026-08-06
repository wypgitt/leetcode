# System Design: Instagram DM Landing Screen

> **Focus areas:** Mobile architecture · Inbox pagination · Local cache / SQLite · Realtime sync · Offline-first UX · Unread badges  
> **Style:** Client-heavy Meta messaging design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split mobile sync vs backend fanout, correct pagination cursors, deal-breakers for “REST refetch entire inbox every open”  
> **Interview theme:** Instagram DMs landing (thread list) — fast paint from disk, delta sync, realtime pushes, offline composition

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

Goal: **bound the product**—the **Instagram DM landing screen** (inbox / thread list): show conversations ranked by recent activity, unread state, avatars/previews, with **instant open from local cache**, **realtime updates**, and **offline** use.

### 1.0 What this is / is not

| Dimension | **DM landing screen (this doc)** | Not this |
|-----------|----------------------------------|----------|
| Primary job | Thread list UX + sync | Full E2EE Messenger redesign / WhatsApp calls |
| Client | Mobile-first (iOS/Android) | Admin moderation tool |
| Success | TTI from cache; correct unreads; battery-friendly | Perfect server-rendered HTML inbox |
| Data | Thread summaries + cursors | Full media CDN architecture deep dive |
| Realtime | New msg / read / mute / requests | Global feed ranking |

**Scope statement:** Design Instagram DM landing: mobile local store, paginated inbox APIs, delta sync, push/realtime, offline, badge counts—plus backend supporting those contracts at scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What’s on landing? | Threads: avatar, title, preview, time, unread, mute | `ThreadSummary` model |
| F2 | Order? | Recency (last message / last activity) | Sort key `sort_ts` |
| F3 | Pagination? | Infinite scroll; ~20–50 / page | Cursor by `sort_ts` + `thread_id` |
| F4 | Tabs? | Primary / General / Requests | Folder filters; separate cursors |
| F5 | Realtime? | New message bumps thread; typing optional | Push + MQTT/WS gateway |
| F6 | Offline? | Show cached inbox; queue sends | SQLite + outbox |
| F7 | Unread badge? | App icon + in-list bold | Server authoritative counter + local |
| F8 | Message requests? | Separate section | Privacy gated threads |
| F9 | Groups? | Yes summaries | Participant snippets denormalized |
| F10 | Search? | Local recent + server search Phase 1.5 | Local FTS optional |
| F11 | Multi-device? | Yes; read state syncs | Server truth; delta sync |
| F12 | Vanish / E2EE? | Hooks; not full MVP crypto | Metadata may differ |

**MVP functional scope:**

1. Landing paints **from local DB in <100–200ms** cold-ish start when cache warm.  
2. **Delta sync** on foreground / push wakes inbox.  
3. **Cursor pagination** for older threads.  
4. Realtime: new message, delete, mute, mark-read, thread mute.  
5. Offline: browse cached threads; composer outbox (thread open may be sibling; mention landing impact).  
6. Unread counts authoritative from server with optimistic local.  
7. Message requests folder.

**Out of MVP:**

- Full chat bubble renderer deep dive (only summary preview)  
- Voice/video calls signaling  
- Full E2EE key management  
- Desktop-perfect parity quirks  
- Server-side ML inbox ranking (recency MVP; relevance Phase 2)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Time-to-interactive (cached) | Instant inbox | p50 < 150ms to first paint from disk |
| N2 | Sync freshness | Opens feeling live | Delta apply p95 < 1–2s on good network |
| N3 | Battery / radio | Not chatty | Coalesce; push-driven; backoff |
| N4 | Pagination latency | Smooth scroll | p99 < 200–300ms |
| N5 | Consistency | Multi-device reads | Eventual ≤ seconds; no lost threads |
| N6 | Offline correctness | No silent loss of sends | Outbox durable on device |
| N7 | Scale backend | Huge MAU | Sharded inbox by user |
| N8 | Privacy | Requests gated | AuthZ on every thread |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Cold start with cache → paint inbox → background delta sync → subtle updates.  
2. Push “new message” → wake → patch thread row → bump to top → badge++.  
3. Scroll down → fetch next cursor page → merge into SQLite.  
4. Mark thread read on another device → realtime → unread clear locally.  
5. Offline open → cached list; banner “offline”; later sync.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cache empty (reinstall) | Blocking sync first page; skeleton UI |
| Conflict preview vs server | Server wins on sync; preserve outbox sends |
| Thread deleted | Tombstone locally; remove from UI |
| Mute while offline | Local mute; sync when online |
| Clock skew sort | Server `sort_ts`; don’t trust client now() |
| Huge inbox (10k threads) | Paginate; don’t download all |
| Duplicate push | Idempotent event ids |
| Badge drift | Periodic reconcile `/badge` |
| Requests spam | Separate folder; rate limits |
| Partial sync fail | Resume with sync token; don’t wipe cache |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU messaging | 100M | 1B | — | extreme |
| DAU open inbox | 40M | 400M | multi-B class | — |
| Peak inbox sync QPS | 100K | 1M | 10M | 100M |
| Avg threads / user (active) | 80 | 80–150 | 150+ | long-tail huge |
| Messages send QPS (global) | 500K | 5M | 50M | 500M |
| Push notifications/s | 200K | 2M | 20M | 200M |
| Concurrent WS/MQTT conns | 5M | 50M | 500M | cell fabric |
| Page size | 30 | 30 | 30 | 30 |
| Local DB size median | 5–20 MB | similar | similar | eviction policies |

**What each jump forces:**

- **10×:** Sticky user home region; sync tokens; push infra; connection gateways.  
- **100×:** Inbox store cells; fanout optimizations; event multicast; aggressive client caching.  
- **1,000×:** Regional gateway fabric; snapshot+delta cold start; thread summary denormalization pipelines.

### 1.5 Etc. (Constraints & Assumptions)

- Landing screen cares about **ThreadSummary**, not full message history (chat screen separate but shares sync bus).  
- Mobile OS kills network freely — design for **push + resume**.  
- Server is source of truth; client cache is performance + offline.  
- Instagram-specific: Requests vs Primary; vanity presence light.

**Scope statement to repeat back:**

> Design the Instagram DM landing screen end-to-end: mobile SQLite cache for instant paint, cursor-paginated thread list APIs, token-based delta sync, realtime/push patching of summaries, offline-safe behavior, and unread badges—backed by a user-sharded inbox service scaling through 10× / 100× / 1,000× without refetching the entire inbox on every open.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Landing open sync** | Delta or snapshot | ~100K/s peak | Inbox sync API |
| **Pagination** | Older threads | fraction of opens | Inbox API |
| **Realtime events** | Msg/read/mute | ~1M+/s fanout msgs | Gateway + pubsub |
| **Push** | Mobile notify | ~200K/s | Push service |
| **Local DB ops** | Client only | n/a server | SQLite |
| **Send message** | Affects summary | high | Chat write path |

**Anti-pattern:** treating “inbox QPS” as equal to “message send QPS.”

### 2.2 Payload math

```text
ThreadSummary ≈ 300–800 bytes (ids, preview text truncated, urls, flags)
Page of 30 ≈ 15–25 KB
Delta of 10 changed threads ≈ 5–10 KB
Prefer deltas ≪ full snapshot
```

### 2.3 Full refetch cost (deal-breaker math)

```text
40M DAU × 10 opens/day × 80 threads × 500B = 1.6e15 B/day ≈ 1.6 PB/day
Just for inbox refetch — absurd
Hence: local cache + delta sync mandatory
```

### 2.4 Connection math

```text
5M concurrent MQTT/WS
Each idle heartbeat 30–60s → manageable with specialized gateways
Events sparse per user; fanout to online devices only
```

### 2.5 Unread badge

```text
Badge = sum unread across folders OR primary-only (product choice)
Must reconcile: local optimistic ++/-- vs server counter endpoint
```

### 2.6 Local storage

```text
80 threads × 500B + indexes ≈ small
Message previews only on landing; don’t store full histories in landing table
Evict LRU thread summaries beyond N if needed
```

---


### 2.7 Delta vs snapshot bandwidth worksheet

```text
Snapshot first page 30 × 600B ≈ 18 KB (+ JSON overhead ~25 KB)
Delta typical open: 0–15 changed threads × 600B ≈ 0–10 KB
If 20% of opens need snapshot reset (token invalid):
  blended ≈ 0.8×8KB + 0.2×25KB ≈ 11.4 KB / open
40M DAU × 10 opens × 11.4 KB ≈ 4.6 TB/day — still large but ~350× better than full refetch PB-scale
```

### 2.8 Client SQLite / Room sizing

```text
threads table: 500 summaries × 800B ≈ 400 KB
indexes (folder, sort_ts, thread_id) ≈ +150 KB
outbox pending: tens of KB
sync_meta: negligible
Messages NOT stored here — only preview_text truncated (~120 chars)
LRU evict summaries beyond 2K threads for power users
Encrypted-at-rest via SQLCipher / OS file protection
```

### 2.9 Badge reconcile math

```text
Optimistic: local badge += 1 on push; -= unread_count on mark-read
Drift sources: multi-device, missed events, folder rules
Reconcile: GET /badge every cold start + every N minutes + after token reset
Badge SLA: icon matches server within 60s when online
```

### 2.10 Progressive capacity

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Landing opens | 100K/s | 1M/s | cells | adaptive sync |
| Delta bytes/day | TB | ×10 | compression | snapshot compaction |
| Gateway conns | 5M | 50M | regional GW | tiered presence |
| Push | 200K/s | ×10 | smart collapse | OEM channels |

**Anti-patterns:** full inbox refetch; OFFSET pagination; client-only badge; device-clock sort.

---

## 3. High-Level Design

### 3.1 Client architecture (mobile)

```text
UI (Compose / UIKit)
  → ViewModel / Repository
    → LocalDataSource (SQLite / Room / GRDB)
    → RemoteDataSource (Sync API)
    → RealtimeChannel (MQTT/WS)
    → Outbox (pending mutations)
```

**Paint policy:**

1. Always render local first.  
2. Kick sync.  
3. Apply patches transactionally.  
4. Diff UI (stable thread_id keys).

### 3.2 API

| Op | Semantics |
|----|-----------|
| `GET /v1/inbox/snapshot?folder=&limit=` | Cold start first page + `sync_token` |
| `GET /v1/inbox/delta?since_token=` | Changed threads / tombstones |
| `GET /v1/inbox/page?cursor=&folder=` | Older pagination |
| `POST /v1/inbox/ack` | Confirm applied token (optional) |
| `GET /v1/badge` | Authoritative unread |
| `POST /v1/threads/{id}/read` | Mark read (also from chat screen) |
| `POST /v1/threads/{id}/mute` | Mute flags |

**ThreadSummary:**

```text
ThreadSummary {
  thread_id,
  folder: PRIMARY|GENERAL|REQUESTS,
  title,
  avatar_urls[],
  preview_text,
  preview_sender_id,
  sort_ts,
  unread_count,
  muted,
  pinned?,
  last_message_id,
  version,          // monotonic per thread
  tombstone?: bool
}
```

**Cursor:**

```text
cursor = encode(sort_ts, thread_id)  // stable tie-break
```

**Sync token:**

```text
sync_token = (user_inbox_epoch, per_shard_offset) // opaque
```

### 3.3 Backend stores

| Store | Role |
|-------|------|
| Inbox summary index per user | Ordered thread ids + denormalized summary |
| Thread service | Members, settings |
| Message service | Canonical messages (chat) |
| Pubsub / presence gateways | Online push |
| Push notification service | Offline wake |
| Counter service | Unread aggregates |

### 3.4 Sync models — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Full refetch each open** | Simple | Bandwidth death | Deal-breaker |
| **Snapshot + delta token** | Fast; correct | Token invalidation edge | **MVP** |
| **CRDT inbox** | Offline merge fancy | Complexity | Rarely needed for summaries |
| **GraphQL huge query** | Flexible | Easy to overfetch | Careful if used |

**Chosen:** SQLite cache + opaque `sync_token` deltas + paginated history of cold threads.

### 3.5 Realtime — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Long poll only** | Simple | Latency/battery | Fallback |
| **MQTT / WS gateway** | Efficient | Infra cost | **Online MVP** |
| **Push only** | Good offline wake | Coarse; slow | Complement |
| **SMS** | No | No | No |

**Chosen:** Persistent connection when app foreground/background-allowed; OS push when disconnected; both carry compact event envelopes.

### 3.6 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| First paint | Local DB | TTI | Wait for network always |
| Sync | Delta token | Bandwidth | Reset inbox every open |
| Pagination | Keyset cursor | Stability | OFFSET deep pages |
| Unread | Server truth + optimistic | Multi-device | Client-only counters |
| Offline sends | Outbox | Durability | Lose messages on kill |
| Sort key | Server sort_ts | Consistency | Device clock ordering |

---


### 3.7 Deal-breakers (landing-specific)

| Claim | Why fatal |
|-------|-----------|
| “Always wait for network before paint” | TTI death offline/slow |
| “OFFSET 10_000 for old threads” | Shifting windows; expensive |
| “Badge = local++ forever” | Multi-device drift |
| “Websocket alone, no push” | Missed wakes when process dead |
| “Store full message history in landing DB” | Size + privacy + wrong ownership |

### 3.8 Optimistic UI contract

```text
Mute/read/pin: apply local immediately + outbox
On ACK: confirm version
On reject: rollback row + snackbar
Preview for unsent outbound: show pending marker; don’t advance others’ unread
```

---

## 4. Architecture Diagram

```text
 +------------------ Mobile App ------------------+
 |  Inbox UI                                      |
 |     ^                                          |
 |     | observe                                  |
 |  Repository / Sync Engine                      |
 |     |                 ^                        |
 |     v                 | events                 |
 |  SQLite (threads,     |                        |
 |   sync_meta, outbox)  |                        |
 |     |                 |                        |
 |     | HTTP sync       | MQTT/WS                |
 +-----+-----------------+------------------------+
       |                 |
       v                 v
 +-----+-----+     +-----+------+
 | Inbox API |     | Realtime   |
 | snapshot/ |     | Gateway    |
 | delta/page|     +-----+------+
 +-----+-----+           |
       |                 | subscribe user_id
       v                 v
 +-----+-----------------+------+
 | User Inbox Cell (home)       |
 | summary index + unread       |
 +-----+-----------------+------+
       ^                 ^
       | writes          | fan-in events
       |                 |
 +-----+------+   +------+------+
 | Message    |-->| Event Bus   |
 | Service    |   | (Kafka)     |
 +------------+   +-------------+
                         |
                         v
                  Push Service → APNs/FCM
```

**Cold start:**

```text
open Inbox
  -> query SQLite ORDER BY sort_ts DESC LIMIT 30
  -> render
  -> GET /delta?since_token=local
     or /snapshot if token null/invalid
  -> upsert rows in txn; advance token
  -> reconcile badge
```

**Realtime patch:**

```text
event ThreadSummaryChanged {thread_id, version, fields...}
  -> if version > local: upsert
  -> reorder list
  -> update badge if unread delta included
```

**Pagination:**

```text
user near end
  -> GET /page?cursor=last_local&folder=PRIMARY
  -> insert older rows (don’t jump scroll)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Server is source of truth** for membership, unread, previews.  
2. **Local DB applies events idempotently** by `(thread_id, version)` / event_id.  
3. **Never shrink sync_token past unapplied data** — advance after txn commit.  
4. **Tombstones** win over late updates with lower version.  
5. **Outbox mutations** retry until server ACK; landing reflects pending previews cautiously.  
6. **AuthZ**: every thread summary fetch checks viewer membership.

#### 5.1.2 Conflict rules

| Conflict | Resolution |
|----------|------------|
| preview text | Higher `version` / server event ts |
| unread_count | Server value on sync; optimistic local until ack |
| mute | Last-write-wins with server timestamp |
| folder move | Server |

#### 5.1.3 Token invalidation

If server cannot serve delta (`token too old`, `epoch bump`):

```text
return 410 + new snapshot of first page
client: replace folder rows carefully OR merge by version
keep outbox intact
```

#### 5.1.4 Push vs realtime race

Apply both idempotently. Prefer richer realtime payload; push may only wake + “sync now”.

### 5.2 Scalability

#### 5.2.1 User home cells

```text
user_id → home cell owns inbox summary index
All devices sync against home
Cross-region: secondary read replicas optional; writes to home
```

#### 5.2.2 Write path impact on landing

```text
Message send → durable message → update summaries (sort_ts, preview, unread)
  → events to gateways → push offline devices
High fanout groups: async fanout; landing may lag seconds
```

#### 5.2.3 Pagination vs delta

- Delta: changed hot threads since token  
- Page: scroll into colder threads  
- Merge client-side by `thread_id` with version checks  

#### 5.2.4 Room/SQLite cache deep dive

```text
Repository flow:
  Flow/LiveData observe threads DAO
  SyncEngine: snapshot|delta|page → single writer transaction
  Upsert: INSERT OR REPLACE / ON CONFLICT(thread_id) DO UPDATE
          WHERE excluded.version >= threads.version
  Tombstone: soft-delete; UI filter deleted_at IS NULL
  Migrations: Room schema version; destructive only on logout
```

**Transaction rule:** advance `sync_token` only after successful upsert txn commit.

#### 5.2.5 Cursor pagination deep dive

```text
Keyset: WHERE (sort_ts, thread_id) < (:ts, :id) ORDER BY sort_ts DESC, thread_id DESC LIMIT N
Stable under inserts; no OFFSET drift
Cursor opaque; includes folder + sort key version
Pins: separate section or sort_ts = MAX / pin_rank overlay
```

#### 5.2.6 Delta sync protocol

```text
GET /delta?since_token=T0
Response:
  upserts: [ThreadSummary...]
  deletes: [thread_id...]
  next_token: T1
  reset?: false
If reset: client fetches snapshot page1; may keep outbox
Idempotent apply: version gates
```

#### 5.2.7 Progressive scale

| Scale | Add |
|-------|-----|
| 10× | Sync tokens; gateway fleet; push |
| 100× | Inbox cells; event bus fanout; snapshot compaction |
| 1,000× | Tiered summary storage; regional gateways; adaptive sync |

### 5.3 Maintainability (mobile + server)

#### 5.3.1 Local schema

```text
threads(thread_id PK, folder, sort_ts, unread_count, preview_text,
        payload_json, version, deleted_at)
sync_meta(folder, sync_token, updated_at)
outbox(id, type, body, status, attempts)
```

#### 5.3.2 Battery & networking

- Exponential backoff on sync fail  
- Coalesce events into one UI frame  
- Skip full snapshot on resume if token fresh  
- Respect OS background budgets; rely on push  

#### 5.3.3 Observability

| Signal | Where |
|--------|-------|
| TTI local paint | Client |
| Delta size / latency | Client + server |
| Token reset rate | Server |
| Badge drift corrects | Client |
| Outbox age | Client |

#### 5.3.4 Security / privacy

- Requests folder isolation; redact previews  
- Device DB encrypted at rest  
- AuthZ on every summary  

### 5.4 Offline optimistic & outbox

```text
Outbox types affecting landing: mark_read, mute, pin, accept_request
Drain: network up → POST → ACK → delete outbox → optional delta
Conflict: server version wins; rebase local optimistic fields
App kill: Room persistence survives; WorkManager/BG task can drain
```

### 5.5 Badge consistency

```text
Sources of truth: server unread aggregate service
Client: optimistic deltas + periodic reconcile
Multi-device: device A reads → event → device B badge--
Folder rules: primary-only vs all — product flag must match server
Push collapse: badge count in push payload may be stale — still reconcile
```

### 5.6 Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Network-first paint | Cache-first |
| Full refetch | Delta token |
| OFFSET pages | Keyset cursor |
| Client-only badge | Server reconcile |
| Clock sort | Server sort_ts |
| Landing stores full chat | Previews only |

---

## 6. Wrap-Up

### 6.1 Design summary

The DM landing screen is an **offline-capable, cache-first mobile client** over a **user-sharded inbox summary service**. Instant paint comes from **SQLite**; freshness from **delta sync + realtime/push**; scale from **not refetching entire inboxes** and **keyset pagination**.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Cache-first vs always-fresh | Cache-first | Brief stale previews |
| Persistent socket vs push-only | Hybrid | Gateway cost |
| Denormalized previews | Fast list | Extra write fanout on message |
| Optimistic unread | Snappy UX | Occasional reconcile |

### 6.3 Deal-breakers

1. Refetching all threads on every inbox open.  
2. OFFSET pagination for deep inboxes.  
3. Trusting client clocks for ordering.  
4. Client-only unread without server reconcile (multi-device lies).  
5. Applying realtime before local txn safety (token / version races).

### 6.4 45-minute plan

1. Clarify landing vs chat thread scope; offline + realtime.  
2. Bandwidth math killing full refetch.  
3. Draw mobile SQLite + delta + gateway.  
4. Deep dive sync token, cursors, badge, offline.  
5. Backend fanout + cells at scale.  
6. Deal-breakers.

### 6.5 Phase 2

- Smart inbox ranking / filters  
- Local FTS search  
- Richer presence / activity  
- Strong E2EE metadata constraints  

---

## 7. Deeper / Related Interview Questions

### Q1. Why cache-first on mobile?

**A:** Networks are slow/unavailable; users judge apps by instant paint. Disk-cached inbox + async sync is the messaging standard.

### Q2. What is a sync token?

**A:** Opaque cursor into the user’s inbox event stream / version epoch. Delta returns changes since that token; advances after successful apply.

### Q3. Keyset vs OFFSET pagination?

**A:** OFFSET becomes slow and duplicates/misses as rows move. Keyset `(sort_ts, thread_id)` is stable and index-friendly.

### Q4. How do you avoid duplicate threads when merging delta + page?

**A:** Upsert by `thread_id` primary key; compare `version`; UI keys on `thread_id`.

### Q5. App icon badge drifting — fix?

**A:** Optimistic updates locally; periodically/on-sync call `/badge`; absolute set, don’t infinite ++.

### Q6. MQTT/WS vs push notifications?

**A:** Sockets deliver rich realtime while process can maintain connection. Push wakes cold apps and survives socket loss. Use both.

### Q7. What goes in ThreadSummary vs full message?

**A:** Summary: denormalized preview fields for list performance. Full message bodies live in chat storage; landing shouldn’t download histories.

### Q8. How does offline mute work?

**A:** Write Outbox `mute(thread_id)` + local flag; sync when online; server LWW resolves multi-device.

### Q9. Message requests privacy on landing?

**A:** Separate folder; previews may be generic (“sent you a message”) until accept; don’t leak into Primary deltas.

### Q10. How to handle 10,000-thread inboxes?

**A:** Only snapshot top page; paginate rest; delta for changes; local LRU eviction for very old summaries.

### Q11. Group chat preview fanout cost?

**A:** Each message updates N member inbox indices — async workers, batching, backpressure. Landing eventual for huge groups.

### Q12. Exactly-once event delivery to mobile?

**A:** At-least-once + idempotent version checks. Exactly-once across mobile radios is unrealistic.

### Q13. Cleartext preview vs E2EE?

**A:** If E2EE, server may only store ciphertext; landing preview might be device-decryptable metadata or placeholder. Call out as product constraint.

### Q14. Typing indicators on landing?

**A:** Usually chat-screen only; landing optional lightweight. High volume — ephemeral, not stored in SQLite.

### Q15. How to test sync engine?

**A:** Record/replay event sequences; crash mid-txn; token reset; airplane mode toggles; multi-device interleaving.

### Q16. Snapshot invalidation storms?

**A:** If many tokens reset, server load spikes. Mitigate: longer delta retention, gradual epoch bumps, client jitter.

### Q17. Sticky unread after mark-read?

**A:** Ensure mark-read bumps `version` and emits event; delta includes unread=0; chat screen and landing share bus.

### Q18. Local DB encryption?

**A:** Use SQLCipher / platform data protection; logout wipes keys; don’t sync raw DB to iCloud carelessly.

### Q19. Why denormalize participant avatars into summary?

**A:** List scroll can’t N+1 fetch profiles. Periodically refresh snippets; accept brief staleness.

### Q20. Server unread counter implementation?

**A:** Per-thread unread + per-user aggregate. Increment on message to recipients; decrement on read; repair job for drift.

### Q21. Background sync limits on iOS?

**A:** Prefer push-driven sync; short BGTasks; don’t rely on infinite background sockets.

### Q22. How do pins interact with sort?

**A:** Pin bucket sorts first; then `sort_ts`. Cursor pagination must include pin state in key or separate sections.

### Q23. Delta payload design?

**A:** List of upserts + tombstones + new `sync_token` + optional `badge`. Keep under ~50KB typical.

### Q24. Race: page fetch returns thread also in newer delta?

**A:** Version compare on upsert; higher wins. Harmless.

### Q25. Multi-account Instagram on one device?

**A:** Separate DB namespaces / files per user id; sync tokens isolated; careful push routing with account identity.

### Q26. Rate-limit sync APIs?

**A:** Per-user quotas; coalesce client requests; exponential backoff; distinguish foreground vs background priority.

### Q27. What if preview contains blocked content?

**A:** Server filters preview text through safety; client still trusts server-provided preview only.

### Q28. Desktop web landing differences?

**A:** Same APIs; IndexedDB instead of SQLite; more persistent WS; still delta sync.

### Q29. Biggest mobile footgun?

**A:** Advancing sync_token before DB commit; or wiping cache on any error; or full refetch “to be safe.”

### Q30. 60-second pitch?

**A:** “Landing always paints from SQLite. A sync token fetches deltas; keyset pagination loads older threads. Realtime/push patch summaries by version. Unreads are optimistic with server reconcile. Backend is user-home inbox cells updated on message write. We never download the whole inbox every open.”


### Q31. Why Room/SQLite over in-memory only?

**A:** Process death and offline opens are the product. Memory-only loses inbox across kills and forces network-first — fails Meta-style mobile bars.

### Q32. How do you merge delta + page without duplicates?

**A:** Primary key `thread_id`. Upsert by version. UI keys on thread_id. Page inserts older rows; delta updates hot ones.

### Q33. When do you reset sync_token?

**A:** Server 410 / epoch bump / retention exceeded. Client snapshot first page; preserve outbox; reconcile badge.

### Q34. Optimistic mark-read then fail?

**A:** Outbox retries; on permanent fail rollback unread_count and badge; surface error. Server remains truth.

### Q35. Group chat preview fanout cost?

**A:** Each message updates N member summaries — async workers, backlog OK for seconds. Don’t do N sync RPCs in send path.

### Q36. How to keep Requests private on landing?

**A:** Separate folder; locked preview copy; no notification content leak; explicit accept moves to Primary.

### Q37. MQTT event vs push both arrive?

**A:** Idempotent apply by version/event_id. Push often just wakes “sync now.”

### Q38. 10k-thread inbox scroll?

**A:** Don’t snapshot all. First page + keyset pagination + search. Local LRU of summaries.

### Q39. Pin sorting rules?

**A:** Pins overlay above chronological; stable secondary key; pins still in delta when preview changes.

### Q40. E2EE preview on landing?

**A:** If E2EE, previews may be ciphertext or device-decrypted only; server summary limited. Call out product mode.

### Q41. Background sync iOS limits?

**A:** Prefer push wake + BGTask sparingly; don’t rely on frequent polling. Cache-first covers UX.

### Q42. Multi-account on device?

**A:** Separate DB files / schema per user_id; sync tokens isolated; badge is per-account then aggregated for icon if product wants.

### Q43. Progressive scale pitch?

**A:** 10× tokens+gateways; 100× inbox cells; 1,000× tiered storage + adaptive sync frequency.

### Q44. Top anti-patterns?

**A:** Network-first, full refetch, OFFSET, client-only badge, device-clock ordering.

### Q45. 60-second pitch?

**A:** “Landing is cache-first SQLite, delta sync with opaque tokens, keyset pagination, realtime patches, outbox for offline, and server badge reconcile. Chat history stays in the thread screen—not this table.”

---
---

### Appendix A — NFR card

```text
Local first paint p50 < 150ms
Delta not full refetch
Keyset cursors
Idempotent versions
Badge reconcile
Outbox durable
```

### Appendix B — SQLite upsert

```text
INSERT INTO threads (...) VALUES (...)
ON CONFLICT(thread_id) DO UPDATE SET
  ... = excluded...
WHERE excluded.version >= threads.version;
```

### Appendix C — Event envelope

```json
{
  "event_id": "e123",
  "type": "thread_summary_upsert",
  "thread_id": "t9",
  "version": 842,
  "summary": {"preview_text": "hey", "sort_ts": 1710000000123, "unread_count": 2}
}
```

### Appendix D — Sync state machine (client)

```text
IDLE -> SYNCING -> IDLE
SYNCING -> BACKOFF on error
token_invalid -> SNAPSHOT -> IDLE
```

### Appendix E — Progressive scale

| Scale | Client | Server |
|-------|--------|--------|
| Baseline | SQLite + delta | 1 region inbox |
| 10× | push coalesce | gateway fleet |
| 100× | LRU eviction | home cells |
| 1,000× | adaptive sync | regional fabric |

### Appendix F — Folder model

| Folder | Rules |
|--------|-------|
| Primary | Friends / priority |
| General | Lower priority |
| Requests | Non-followers gated |

Separate `sync_meta` per folder or single token with folder tags.

### Appendix G — Unread reconcile

```text
on_delta / on_resume:
  local_badge = sum(unread)
  server_badge = GET /badge
  if mismatch: trust server; schedule thread repair if large gap
```

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| ThreadSummary | Inbox row model |
| Sync token | Delta cursor |
| Outbox | Pending local mutations |
| Tombstone | Deleted thread marker |
| Home cell | User’s inbox authority region |

### Appendix I — 30m checklist

1. Scope landing vs chat.  
2. Full-refetch math → cache+delta.  
3. Mobile architecture diagram.  
4. Cursors, tokens, badges, offline.  
5. Scale + deal-breakers.

### Appendix J — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just REST GET /threads every time” | PB/day math |
| “OFFSET=1000” | Moving rows / cost |
| “Client clocks for order” | Skew |
| “Badge only local” | Multi-device wrong |

### Appendix K — Outbox types affecting landing

| Mutation | Local effect |
|----------|--------------|
| mark_read | unread=0 optimistic |
| mute | flag |
| accept_request | folder move |
| send_message | bump preview pending |

### Appendix L — Backend summary update pseudocode

```text
def on_message(m):
  for uid in recipients:
    summary = inbox[uid][m.thread_id]
    summary.sort_ts = m.ts
    summary.preview = truncate(m.text)
    summary.version += 1
    if uid != m.sender: summary.unread += 1
    emit(uid, summary)
```

### Appendix M — Related Meta systems (conceptual)

| System | Relation |
|--------|----------|
| MQTT gateways | Realtime |
| Push | Wake |
| Mailbox/inbox stores | Summaries |
| Chat message store | Canonical msgs |

### Appendix N — Worked example

```text
User has 120 threads; opens inbox 12×/day
Cached paint: 0 network bytes to first paint
Delta avg 3 threads × 600B × 12 ≈ 21 KB/day/user vs ~60 KB snapshot ×12 ≈ 720 KB
×100M users = huge savings
```

### Appendix O — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Read-your-write after send? | Optimistic local + server confirm |
| Cross-device read state | Eventual via events/delta |
| Strong global order of all threads? | Per-user sort_ts sufficient |

### Appendix P — Skeleton UI policy

```text
if local empty: show skeletons, blocking snapshot
else: show local, non-blocking delta spinner subtle
```

### Appendix Q — Security notes

| Topic | Approach |
|-------|----------|
| IDOR | Membership check |
| Preview leak | Requests redaction |
| Stolen device | Remote logout / token revoke |

### Appendix R — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Push+WS hybrid, tokens |
| 100× | Inbox cells, async fanout |
| 1,000× | Snapshot compaction, regional gateways |

### Appendix S — Client threading

```text
DB writes on single serial queue
UI observes query results
Network on background
Never read SQLite on main without async APIs
```

### Appendix T — Sample delta response

```json
{
  "sync_token": "opaque-next",
  "upserts": [{"thread_id": "t1", "version": 9, "sort_ts": 171, "unread_count": 1}],
  "tombstones": [{"thread_id": "t2", "version": 3}],
  "badge": 4
}
```

---

*End of Instagram DM Landing Screen system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Change | Why |
|------|--------|-----|
| →10× | Delta tokens; gateway fleet; push wake | Bandwidth + realtime |
| →100× | User inbox cells; async summary fanout | Write amplification |
| →1,000× | Tiered summary storage; regional gateways; adaptive sync | Hot users / global |

### 8.2 Client sync state machine

```text
IDLE → PAINT_LOCAL → SYNCING(delta|snapshot)
  → APPLY_TXN → ADVANCE_TOKEN → RECONCILE_BADGE → IDLE
On 410: RESET_SNAPSHOT (keep outbox)
On realtime event: APPLY_IDEMPOTENT → maybe reorder UI
On mutation: OPTIMISTIC + OUTBOX → DRAIN
```

### 8.3 SQLite transaction rules

```text
1) upsert/tombstone rows
2) only then write sync_token
3) single writer for SyncEngine
4) version gate: ignore older events
5) UI observes query; don’t mutate from multiple threads unsafely
```

### 8.4 Badge consistency card

```text
optimistic local deltas OK
server GET /badge is truth
reconcile: cold start, interval, after reset, after mark-read ACK
multi-device via events
folder policy must match server
```

### 8.5 Anti-patterns

1. Network-first blank screen  
2. Full inbox refetch each open  
3. OFFSET deep pagination  
4. Client-only badge forever  
5. Sort by device clock  
6. Landing DB holds full message history

### 8.6 Event envelope examples

```text
ThreadSummaryChanged {thread_id, version, sort_ts, preview_text, unread_delta?}
ThreadTombstone {thread_id, version}
BadgeInvalidate {reason}  // client should GET /badge
MuteChanged {thread_id, muted, version}
```

Apply rules: ignore if version ≤ local; coalesce rapid events per thread_id within 50ms UI frame.

### 8.7 Offline send affecting landing

```text
Outbound message in outbox:
  local thread preview may show pending text + spinner
  sort_ts local optimistic OK for sender device
  other devices unchanged until server accept
On ACK: replace with server summary fields (authoritative preview)
```

### 8.8 Pagination + delta race

```text
Page returns thread T; newer delta also returns T with higher version
→ upsert keeps higher version; UI stable
Never delete local rows just because missing from a page response
```

### 8.9 Mobile battery note

```text
Foreground: WS/MQTT OK
Background: rely on push; bounded BG sync
Don’t poll /delta every few seconds forever
Coalesce sync triggers: resume + push + manual refresh
```

### 8.10 Folder model quick card

```text
PRIMARY / GENERAL / REQUESTS (product-dependent)
Each folder: own sync_token OR namespaced token
Requests: redacted previews; accept → move folder + delta upsert
Pins: overlay section; still versioned summaries
Mute: suppress push; landing still shows thread unless archived
```

### 8.11 Server summary update pseudocode

```text
on message_persisted(m):
  for member in members:
    summary = inbox[member].get(thread)
    summary.sort_ts = m.ts
    summary.preview = render_preview(m, member)
    summary.version += 1
    if member != sender and not muted_rules: summary.unread += 1
    emit event(member, summary)
```

<!-- deepened in-place: BOTE + nested §5 + §7 Q&A + §8 study card -->

### 8.x Quick recall

Preserve cache-first / budgeted paths; escalate with progressive tables above.

