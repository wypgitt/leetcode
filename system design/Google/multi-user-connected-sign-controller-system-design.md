# System Design: Multi-User Connected-Sign Controller

> **Focus areas:** Multi-writer letter/color cells · Conflict resolution (CRDT vs OT vs LWW) · Offline queue + sync · Device-as-edge · Presence · WebSocket/MQTT · Partition tolerance · Android client · Audit/rollback  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit authority model (cloud vs device), resolved concurrency story, failure UX for offline/device death, correct sync arithmetic  
> **Interview theme:** Google Android L5 report — collaborative real-time control of a physical LED sign with conflicting edits, flaky radios, and battery/connectivity constraints

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

Goal: **bound the product**—multiple users collaboratively control a **connected LED sign** (letters + colors). Clients edit cells, must survive offline and device failures, and must resolve conflicting writes without corrupting the physical display.

### 1.0 What this is / is not

| Dimension | **Connected-sign controller (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Multi-user real-time control of letter/color grid on a physical sign | Generic collaborative doc (Docs/Figma full fidelity) |
| Success | Correct visible sign state; low conflict surprise; recover from offline | Perfect CRDT theory without device constraints |
| Edge | Android phones + sign firmware/gateway | Server-only toy simulation |
| Authority | Explicit: cloud SoT with device apply, or device SoT with cloud mirror | Ambiguous dual SoT (deal-breaker) |
| Offline | Queue + sync; conflict UX | Silent drop of edits |

**Scope statement:** Design a multi-user connected-sign controller where clients edit individual letters/colors, handle conflicting edits, offline state, and device failures—framed as a Google Android L5 system design.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the sign? | Fixed LED matrix / character cells (e.g. 32×8 or 16 letters × RGB) | Grid model: cell = `{char, color, meta}` |
| F2 | Who edits? | Multiple authenticated users per sign (family/team) | ACL: `sign_id` + role; presence |
| F3 | Edit granularity? | Per cell (letter and/or color independently) | Cell-level ops; not whole-frame only |
| F4 | Latency feel? | Near-real-time when online (< few hundred ms) | Push channel (WS/MQTT) |
| F5 | Offline? | Edit offline; sync later; show conflict UX | Local queue + merge |
| F6 | Conflict policy? | Prefer mergeable per-cell; last writer for same cell OK if explained | CRDT-lite or LWW+vector |
| F7 | Device role? | Sign is edge device; may reboot, lose Wi‑Fi | Device apply loop + recovery |
| F8 | Presence? | See who is editing / connected | Presence channel; soft |
| F9 | History? | Undo recent; audit who changed what | Append ops log + snapshots |
| F10 | Auth? | Google account / OAuth; invite codes | Token to gateway; device pairing |
| F11 | Android specifics? | Foreground + background sync; Doze | WorkManager; WS lifecycle |
| F12 | Multi-sign? | User may own/control several signs | `user ↔ signs` membership |

**MVP functional scope:**

1. Pair Android client ↔ sign (device identity + owner ACL).  
2. Render grid on clients; edit letter and/or color per cell.  
3. Online: push ops to peers + sign within ~100–500 ms.  
4. Offline: local optimistic UI + durable op queue; sync on reconnect.  
5. Conflict resolution for concurrent same-cell edits (chosen model below).  
6. Device reconnect: fetch latest snapshot + catch-up ops; re-apply to LEDs.  
7. Presence (who’s online on this sign).  
8. Audit trail of ops; rollback to snapshot / undo last N.  
9. Soft locks / “editing cell” indicators (advisory, not exclusive MVP).

**Out of MVP:**

- Full OT for free-form text documents  
- Video/animation timelines as first-class (hooks for frame sequences)  
- Cross-sign multiplayer games  
- Perfect pixel-level collaborative drawing (cell grid only)  
- Offline-first forever without cloud (cloud remains coordination plane)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Online edit latency | Feels live | p50 < 150ms cloud RTT path; p99 < 500ms same region |
| N2 | Sign apply lag | Visible promptly | < 1s from accepted op when device online |
| N3 | Durability of accepted ops | No silent loss after ACK | Durable log before ACK to client |
| N4 | Offline queue | Survive app kill | Room/SQLite; retry with backoff |
| N5 | Availability (control) | High for cloud APIs | 99.9%; sign may be offline often |
| N6 | Consistency | Per-cell mergeable; monotonic apply on device | Explicit model (not “eventual” handwave) |
| N7 | Battery | Background polite | Coalesce; MQTT QoS chosen carefully |
| N8 | Security | Only ACL members control sign | Mutual TLS or signed device tokens; no open MQTT |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User A changes cell (3,0) letter to `H` → peers see update → sign LEDs update.  
2. User B changes color of different cell → merges cleanly.  
3. Two users edit different cells concurrently → both apply.  
4. User goes offline in subway → edits locally → reconnect → sync → sign updates.  
5. Sign power-cycles → reconnects → pulls snapshot → LEDs restore.  
6. Owner rolls back last 5 minutes → clients + sign converge to snapshot.  
7. Presence: “Alice editing” indicator while focused on a cell.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two writers same cell online | Merge by policy (LWW timestamp+actor or CRDT register); UX toast |
| Offline both edit same cell | On sync: conflict marker or deterministic LWW; optional pick UI |
| Op ACK then crash before local clear | Idempotent op_id; server dedupe |
| Device offline, cloud accepts ops | Queue for device; apply on reconnect in order |
| Split brain: local Wi‑Fi direct vs cloud | **Forbid dual SoT**; direct mode is “local override” with explicit mode switch |
| Clock skew LWW | Server timestamp on accept; client logical clock secondary |
| Malicious / revoked user | ACL check; device ignores unsigned ops |
| Flood of edits | Rate limit per user; coalesce color scrubbing |
| Android Doze kills WS | Persistent connection via FCM high-pri nudge + reconnect; MQTT keepalive tuned |
| Partial apply on LED (crash mid-frame) | Transactional framebuffer swap / generation counter |
| Rollback vs in-flight offline op | Reject or rebase offline ops against new base snapshot |
| Sign factory reset | Re-pair; revoke old device cert |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active signs | 10K | 100K | 1M | 10M |
| Peak online users | 20K | 200K | 2M | 20M |
| Concurrent editors / hot sign | 5 | 10 | 20 | 50 (soft cap) |
| Ops/s global | 5K | 50K | 500K | 5M |
| Ops/s per hot sign | 20 | 50 | 100 | 200 (coalesce) |
| Avg cells / sign | 128 | 128–1K | 1K–4K | larger matrices |
| Snapshot size | ~2–20 KB | ~20–100 KB | ~100 KB–1 MB | chunked |
| Presence updates/s | 2K | 20K | 200K | regional fanout |
| Android clients (DAU) | 50K | 500K | 5M | 50M |
| Device reconnect storms | rare | deploy day | regional outage | cell isolation |

**What each jump forces:**

- **10×:** Shard by `sign_id`; sticky WS gateway; per-sign op log partitions.  
- **100×:** Regional cells; presence fanout trees; snapshot compaction; device MQTT broker tiering.  
- **1,000×:** Sign home cells; edge PoPs for device ingress; aggressive op coalescing; cold signs hibernated.

### 1.5 Etc. (Constraints & Assumptions)

- Physical sign has limited CPU/RAM; firmware prefers **snapshot apply + short op catch-up**, not infinite OT.  
- Radios: Wi‑Fi primary; optional BLE provisioning only.  
- Android is primary client (interview lens); web secondary.  
- Prefer **server-assigned timestamps / Lamport** over trusting device wall clocks for LWW.  
- “Letter” may be glyph index into a font; color is RGB565 or RGB888.

**Scope statement to repeat back:**

> Design a multi-user connected-sign controller: cell-level letter/color edits, real-time sync, offline queues, conflict resolution, device-as-edge apply with clear cloud authority, presence, audit/rollback—scaling signs via `sign_id` sharding through 10× / 100× / 1,000×, with Android battery and connectivity constraints first-class.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | 10× | Plane |
|-------|------|----------|-----|-------|
| **Cell ops** | setLetter / setColor | ~5K/s | ~50K/s | Op log + fanout |
| **Snapshots** | full grid pull | << ops | ×10 | Object/blob or row |
| **Presence** | join/leave/heartbeat | ~2K/s | ~20K/s | Ephemeral Redis |
| **Device apply** | MQTT/WS to sign | ~ops rate online signs | ×10 | Device gateway |
| **Auth / ACL** | token refresh | low | ×10 | Control plane |
| **History read** | audit UI | bursty | ×10 | Cold log store |

**Anti-pattern:** treating color-scrubbing (60 events/s from one finger) the same as discrete letter picks—**coalesce** drag updates.

### 2.2 Bandwidth sketch

```text
Op message ≈ 80–200 bytes (json/protobuf + framing)
5K ops/s × 150 B ≈ 750 KB/s ingress (trivial)
Fanout: avg 3 subscribers × 5K = 15K msgs/s ≈ 2.25 MB/s
At 100×: ~225 MB/s fanout → need regional gateways + per-sign rooms
Hot sign 100 ops/s × 20 watchers = 2K msgs/s localized — fine if sharded by sign
```

### 2.3 Storage sketch

```text
Op log: 5K ops/s × 150 B × 86400 ≈ 65 GB/day raw
Retain hot 7d + compact to snapshots: keep snapshots every N ops or T seconds
10K signs × 20 KB snapshot ≈ 200 MB active state (tiny)
Audit 90d: tier to cold object store
```

### 2.4 Device reconnect storm

```text
Regional Wi‑Fi blip: 100K signs reconnect
Without jitter: thundering herd on snapshot service
With jitter 0–60s + cached ETag snapshots: spread load
Snapshot QPS peak ≈ 100K / 30s ≈ 3.3K/s — design for this
```

### 2.5 Battery / radio

```text
WS ping every 30s: costly on cellular
MQTT keepalive 60–120s + FCM wake for actionable pushes: better for idle viewers
Editors: foreground WS OK; background: pause live stream, sync on resume
```

---

## 3. High-Level Design

### 3.1 Domain model

```text
Sign
  sign_id, owner_id, acl[], device_id, firmware_ver, mode (CLOUD|LOCAL_OVERRIDE)
  grid: width, height, cell[x,y] -> { letter, color, updated_at, actor_id, lamport }

Op (append-only)
  op_id (client UUIDv7), sign_id, cell, field (LETTER|COLOR), value
  base_snapshot_id?, client_ts, server_ts, actor_id, lamport

Snapshot
  snapshot_id, sign_id, generation, grid_blob, created_at

DeviceSession
  device_id, last_applied_generation, last_op_seq, online
```

### 3.2 API (logical)

| Op | Semantics |
|----|-----------|
| `EditCell(sign, cell, field, value, op_id)` | Submit edit; durable ACK with server_ts/seq |
| `GetSnapshot(sign, if_none_match?)` | Full grid + generation |
| `Subscribe(sign)` | Push ops + presence |
| `SyncOffline(ops[])` | Batch upload queued ops |
| `Rollback(sign, snapshot_id \| seq)` | Admin/owner; bump generation |
| `PresenceHeartbeat(sign, focus_cell?)` | Soft presence |
| `PairDevice / RotateDeviceCreds` | Provisioning |

### 3.3 Authority model (critical interview fork)

| Model | Pros | Cons | Verdict |
|-------|------|------|---------|
| **A. Cloud SoT, device apply** | Clear merge; audit; multi-user natural | Sign needs cloud to accept “truth” | **MVP default** |
| **B. Device SoT, cloud mirror** | Works offline LAN party | Multi-user WAN conflicts hard; audit weak | Local-only mode |
| **C. Dual equal SoT** | — | Split brain | **Deal-breaker** |

**Chosen:** **Cloud is source of truth** for collaborative WAN mode. Device holds a **replica** and applies generations. Optional **LOCAL_OVERRIDE** mode: device temporarily authoritative on LAN; on exit, full snapshot upload with explicit conflict review.

**Deal-breaker:** claiming both phone offline queue and device local edits are co-equal without a merge epoch.

### 3.4 Concurrency: CRDT vs OT vs LWW

| Approach | Fit for letter/color cells | Complexity | Offline | Interview take |
|----------|----------------------------|------------|---------|----------------|
| **LWW register per field** | Excellent (char, color are registers) | Low | Easy with server_ts | **MVP default** |
| **CRDT (LWW-Element-Set / MV-Register)** | Good; multi-value until observe | Medium | Natural | Upgrade if need multi-value UX |
| **OT** | Overkill for fixed cells; great for strings | High | Hard | Skip for grid cells |
| **Whole-frame LWW** | Simple | Loses concurrent different-cell edits | Bad UX | Reject |

**Chosen MVP:** treat each `(cell, field)` as an **LWW-Register** ordered by `(server_ts, actor_id)` after durable accept. Clients may show **pending** local value until ACK. For true simultaneous offline edits on same field: deterministic LWW + optional “conflict chip” listing discarded value for undo.

**When CRDT:** if product wants “both colors kept as alternatives” (MV-Register) or collaborative brushes—mention as Phase 1.5.

**When OT:** if sign becomes free-text marquee with insert/delete in a string—different product.

### 3.5 Transport: WebSocket vs MQTT vs SSE

| Transport | Clients | Devices | Notes |
|-----------|---------|---------|-------|
| **WebSocket** | Android/Web editors | Possible | Bidirectional; sticky gateway |
| **MQTT** | Optional | **Preferred for signs** | QoS1, retained last snapshot topic optional |
| SSE | View-only | Poor | One-way |
| FCM | Wake / notify | N/A | Resume sync, not op stream |

**Chosen:** Android editors → **WebSocket** to realtime gateway. Signs → **MQTT** (QoS1) to device broker, payload = op batches or “fetch snapshot” commands. Bridge cloud op log → MQTT publish per `sign/{id}/ops`.

### 3.6 Offline queue + sync

```text
Local:
  Room DB: pending_ops(op_id, payload, status)
  Optimistic UI applies pending on top of last ACK snapshot

Online sync:
  1. Pull snapshot if local_generation << server
  2. Rebase or LWW-merge pending ops
  3. Upload batch SyncOffline with idempotent op_ids
  4. Receive accept/reject per op; clear pending; subscribe live
```

**Conflict UX:**

| Situation | UX |
|-----------|-----|
| Different cells | Silent merge |
| Same cell, your pending lost LWW | Toast + “Restore mine” (new op) |
| Rollback invalidated base | Banner “Sign reset; review your edits” |

### 3.7 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Authority | Cloud SoT | Multi-user + audit | Dual SoT |
| Concurrency | Per-field LWW (+ server_ts) | Cells are registers | Whole-frame LWW |
| Device protocol | MQTT QoS1 | Flaky edge, wake/sleep | Fire-and-forget UDP only |
| Offline | Durable queue + idempotent op_id | App kills common | Memory-only queue |
| Fanout | Per-sign room / topic | Natural shard key | Global broadcast bus |
| History | Append op log + snapshots | Rollback/audit | Mutable single row only |
| Clocks | Server accept time | Skew | Trust client wall clock for LWW |

---

## 4. Architecture Diagram

```text
  +------------------+         +------------------+
  | Android Client A |         | Android Client B |
  | Room offline Q   |         | optimistic UI    |
  | WS session       |         | presence         |
  +--------+---------+         +--------+---------+
           |  WSS/TLS                    |
           v                             v
  +------------------------------------------------+
  |           Realtime Gateway (sticky by sign_id) |
  |  authZ · rate limit · coalesce · presence hub  |
  +----------------------+-------------------------+
                         |
                         v
  +----------------------+-------------------------+
  |              Sign Coordination Service         |
  |  accept op → durable log → version++ → fanout  |
  +------+-------------+-------------+-------------+
         |             |             |
         v             v             v
  +------------+ +-----------+ +------------------+
  | Op Log     | | Snapshot  | | ACL / Pairing    |
  | (Kafka/PG) | | Store     | | Membership       |
  +------+-----+ +-----------+ +------------------+
         |
         | bridge
         v
  +----------------------+     +------------------+
  | Device Gateway/MQTT  |---->| Sign Firmware    |
  | topics sign/{id}/#   |     | framebuffer+gen  |
  +----------------------+     +------------------+

  Presence: gateway ↔ Redis (TTL heartbeats, pub/sub per sign)
  Push wake: FCM → Android "sync now" (not full op payload)
```

**Online edit path:**

```text
Client EditCell(op_id)
  -> Gateway authZ + coalesce
  -> Coord: persist op (idempotent), assign seq/server_ts
  -> Fanout WS to subscribers
  -> Publish MQTT to device
  -> ACK client {seq, server_ts}
Device: apply if seq == last+1 else snapshot resync
```

**Offline sync path:**

```text
Reconnect -> GetSnapshot(etag) -> merge pending -> SyncOffline(batch)
  -> per-op LWW accept/reject -> clear queue -> resume Subscribe
```

**Device recovery:**

```text
Boot -> MQTT connect (mTLS) -> PUBLISH last_applied_gen
  -> Broker/Coord: if lag > threshold then snapshot else op replay
  -> Atomic framebuffer swap at generation G
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Single SoT in CLOUD mode:** only coordination service assigns `seq` / `generation`.  
2. **Idempotent ops:** `(sign_id, op_id)` unique; retries safe.  
3. **Device monotonic apply:** never apply `seq` < `last_applied` without explicit rollback generation bump.  
4. **ACK ⇒ durable:** client may only drop pending after ACK (or confirmed reject).  
5. **LED publish atomic:** firmware double-buffers frames by `generation`.  
6. **ACL on every mutate:** revoked users’ ops rejected; device verifies signed envelopes optional hardening.

#### 5.1.2 Failure modes

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Gateway crash | WS drop | Client reconnect sticky hash; resume from `last_seq` |
| Coord crash after persist before fanout | Consumer lag / outbox | Outbox pattern: persist + outbox row; publisher drains |
| MQTT at-least-once dup | seq dedupe on device | Ignore dup seq |
| Lost MQTT message | Device gap detection | Snapshot resync |
| Android process death | Pending rows in Room | Sync on boot |
| Clock skew | — | Ignore client_ts for LWW winner |
| Poison op | Schema validation | Reject; alert; don’t block seq (or quarantine) |
| Rollback race | generation fence | All clients hard-resync |

#### 5.1.3 Partition tolerance

```text
Client partitioned from cloud:
  - Local edits queued; UI shows "Offline"
  - Cannot claim device updated until sync (unless LOCAL_OVERRIDE)

Device partitioned:
  - Cloud still accepts collaborative edits
  - Device applies on heal
  - Physical sign stale — product-honest UX on clients ("Sign offline")

Split: some clients see cloud, device on old LAN-only:
  - LOCAL_OVERRIDE must be explicit; else device only trusts cloud creds
```

**CAP note:** for a given sign in CLOUD mode we choose **consistency of accepted order** over updating the physical device during partition (AP for device availability of *stale* display is OK; CP for *authority*).

#### 5.1.4 Rollback & audit

- Op log is append-only; rollback = **new snapshot** + `generation++` + truncate-or-tombstone logical timeline for clients.  
- Audit UI reads op log: `{actor, cell, field, old, new, ts}`.  
- Soft undo: invert last op if still LWW-winner compatible; else restore-from-snapshot.

### 5.2 Scalability

#### 5.2.1 Shard key

**`sign_id`** is the unit of serial accept. All ops for a sign go through a single logical writer (partition / actor / row lock).

| Scale | Mechanism |
|-------|-----------|
| Baseline | PG row per sign + `seq` counter; WS rooms in-memory |
| 10× | Kafka partition by `sign_id`; gateway consistent hash |
| 100× | Regional **home cell** for sign; cross-region read-only mirrors optional |
| 1,000× | Hibernate cold signs (no hot room); wake on first subscribe |

#### 5.2.2 Coalescing

Color scrubbing: gateway merges outstanding un-ACKed color ops for same `(actor, cell)` within 50ms window → one op. Letter picks: no coalesce.

#### 5.2.3 Presence scalability

Presence is **lossy-ok**. Redis HASH per sign + TTL; broadcast diffs only. At 100× use regional presence; don’t store forever.

#### 5.2.4 Snapshot strategy

| Trigger | Action |
|---------|--------|
| Every N ops (e.g. 100) | Compact snapshot |
| Every T seconds if dirty | Snapshot |
| Rollback | Snapshot |
| Device lag > M ops | Send snapshot not replay |

Snapshots in object store; metadata in DB. ETag = `generation`.

### 5.3 Maintainability

#### 5.3.1 Firmware vs cloud contract

Versioned schema: `op_envelope_v1`. Device rejects unknown critical fields; cloud gates features by `firmware_ver`.

#### 5.3.2 Android client considerations

| Concern | Approach |
|---------|----------|
| WS lifecycle | Connect foreground; disconnect/backoff background |
| Sync | WorkManager + expedited on FCM |
| Storage | Room for queue + last snapshot |
| Doze | Can’t rely on frequent WS; FCM high-priority for “sign needs attention” rare |
| Security | Store device pairing secrets in Keystore; short-lived user tokens |
| UI thread | Apply ops on background; DiffUtil grid updates |
| Battery | Batch presence; coalesce paints |

#### 5.3.3 Observability

| Metric | Why |
|--------|-----|
| `op_accept_latency` | UX online |
| `fanout_lag` | Gateway health |
| `device_apply_lag` | Physical freshness |
| `offline_queue_depth` | Client health |
| `conflict_lww_discard` | UX pain |
| `snapshot_resync_rate` | Gap/storm indicator |
| `mqtt_reconnects` | Device fleet |
| `rollback_count` | Support |

#### 5.3.4 Multi-writer same cell (worked)

```text
t1: Alice sets (0,0) letter="A" (pending)
t2: Bob sets (0,0) letter="B" (pending)
Server accepts Alice seq=10 server_ts=100
Server accepts Bob seq=11 server_ts=101
LWW winner = Bob "B"
Alice UI: was optimistic "A"; on seeing seq=11, set "B"; toast optional
Audit: both ops retained; winner marked
```

Offline variant: both upload on reconnect; same LWW by server_ts order of accept (not client_ts).

### 5.4 LED grid model (detail)

```text
Grid G[W][H]:
  letter: uint16 glyph_id or UTF-8 codepoint (product choice)
  color:  uint16 RGB565 (device) / uint32 RGB888 (clients)
  meta:   generation_touched, actor_id

Frame apply:
  working_fb <- apply ops
  if complete: active_fb.swap(working_fb); gen = G
```

Brightness / power: firmware may clamp color; cloud stores **requested** color; device reports **effective** if needed (Phase 1.5).

### 5.5 Security & pairing

```text
1. Owner creates sign in app → one-time pair code
2. Device shows code / BLE provision → exchanges device cert
3. Cloud binds device_id ↔ sign_id
4. MQTT mTLS; WS user OAuth + sign ACL
5. Rotate certs; revoke on theft
```

**Deal-breaker:** public MQTT broker topic without auth.

### 5.6 Progressive scale narrative

> **Baseline:** monolithic coord + PG op log + one WS tier + MQTT broker; LWW per field; Room offline queue.  
> **10×:** shard gateways and Kafka by `sign_id`; snapshot store; coalescing.  
> **100×:** regional home cells; presence/redis tiers; device reconnect jitter; cold hibernation.  
> **1,000×:** cell mesh; edge MQTT PoPs; aggressive compaction; multi-value CRDT only where product pays for complexity.

---

## 6. Wrap-Up

### 6.1 Decisions locked

| Area | Decision |
|------|----------|
| Authority | Cloud SoT; device replica apply |
| Concurrency | Per-(cell,field) LWW with server_ts; CRDT optional |
| Offline | Durable idempotent queue + rebase/LWW sync |
| Transport | WS clients; MQTT devices |
| Scale key | `sign_id` serial accept + rooms |
| History | Append-only ops + snapshots; rollback = new generation |

### 6.2 Deal-breakers called out

- Dual equal sources of truth  
- Whole-frame LWW destroying concurrent cell edits  
- Trusting client wall clocks for conflict winners  
- Unauthenticated device channels  
- ACK before durability  
- Infinite OT on tiny microcontroller without snapshots  

### 6.3 30-second close

> We model the sign as a grid of LWW registers coordinated by a cloud single-writer per `sign_id`, fan out over WS/MQTT, and treat Android offline as an idempotent op queue with honest conflict UX. The device is an edge projector of cloud generations—not a second brain—unless the user explicitly enters local override.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & product

**Q1: Why cell-level vs full framebuffer uploads?**  
A: Concurrent multi-user edits merge; bandwidth; audit granularity. Full frames as snapshots only.

**Q2: Is this Figma?**  
A: No—fixed discrete cells; simpler CRDT/LWW; physical apply constraints dominate.

**Q3: What’s the UX if the sign is offline?**  
A: Clients edit cloud truth; badge “Sign offline”; device catches up later.

**Q4: Who can rollback?**  
A: Owner/admin role; audit the rollback event itself.

**Q5: Free-form text marquee?**  
A: Different model (string OT/CRDT); don’t pretend LWW cells solve inserts.

### 7.2 CRDT vs OT vs LWW

**Q6: Why not OT?**  
A: OT needs transform functions and central ordering complexity disproportionate to registers.

**Q7: Why not full OR-Set CRDT?**  
A: Letters aren’t sets of add/remove needing commutativity beyond LWW; MV-Register if product wants branches.

**Q8: Does LWW lose data?**  
A: Loses the losing write’s *effect*; retains audit; offer restore.

**Q9: Happens-before without server?**  
A: Offline vector clocks possible; still need tie-break; server_ts simpler for MVP.

**Q10: Can CRDT run on device?**  
A: Possible for LOCAL_OVERRIDE merge later; MCU may only apply snapshots.

**Q11: Color scrubbing conflicts?**  
A: Coalesce per actor; LWW last coalesced wins; don’t spam log.

**Q12: Multi-value register UX?**  
A: Show two candidates; user picks; write resolving op—Phase 1.5 CRDT.

### 7.3 Sync & offline

**Q13: Exactly-once ops?**  
A: At-least-once delivery + idempotent `op_id` ⇒ effectively-once apply.

**Q14: Rebase vs LWW on sync?**  
A: LWW for registers; rebase if you had optimistic dependencies (rare here).

**Q15: Large offline queue?**  
A: Cap with coalesce; if >N, replace with “upload as snapshot diff” after pull.

**Q16: Encryption of offline DB?**  
A: SQLCipher / EncryptedFile; tokens in Keystore.

**Q17: Clock change on phone?**  
A: Irrelevant for winners if server_ts rules.

**Q18: Partial batch sync failure?**  
A: Per-op results; retry failed only; don’t double-apply ACKed.

### 7.4 Device & edge

**Q19: MQTT QoS0/1/2?**  
A: QoS1 typical; QoS2 rarely worth it if seq idempotent.

**Q20: Retained MQTT messages?**  
A: Optional retained “latest generation” pointer; careful with ACL.

**Q21: Device applies out of order?**  
A: Buffer small gaps; else snapshot resync; never paint unordered.

**Q22: Firmware OTA vs state?**  
A: Pause apply; persist last_gen; resume; schema compat check.

**Q23: BLE vs Wi‑Fi?**  
A: BLE for pairing; Wi‑Fi for ops. Don’t stream ops over BLE MVP.

**Q24: Power failure mid-frame?**  
A: Double buffer + gen in FRAM/flash; on boot validate.

**Q25: Device stolen?**  
A: Revoke certs; sign enters unpaired; remote wipe commands best-effort.

### 7.5 Realtime gateway

**Q26: Sticky sessions?**  
A: Hash `sign_id` to gateway set; presence local; drain on deploy.

**Q27: Fanout explosion?**  
A: Cap watchers; coalesce; snapshot for late joiners not full replay.

**Q28: WS vs MQTT for phones?**  
A: WS easier in app; MQTT possible; pick one primary for clients.

**Q29: Backpressure?**  
A: Slow consumer → disconnect or snapshot-only mode; rate limit editors.

**Q30: Cross-region editors?**  
A: Sign home region; foreign editors extra RTT; don’t multi-master seq.

### 7.6 Presence & UX

**Q31: Exclusive locks?**  
A: Advisory only MVP; hard locks anger users; LWW resolves.

**Q32: Presence accuracy?**  
A: Soft TTL; don’t drive LED state from presence.

**Q33: Conflict toast spam?**  
A: Aggregate; only on focus cell or undo stack.

**Q34: Accessibility?**  
A: Grid navigation; announce letter/color changes.

### 7.7 History & rollback

**Q35: How far back audit?**  
A: Hot log 7–30d; cold archive; snapshots for restore points.

**Q36: Rollback vs GDPR delete user?**  
A: Tombstone actor display; legal redaction pipeline separate from LED state.

**Q37: Point-in-time restore?**  
A: Snapshot + replay ops to T; or store periodic snapshots.

**Q38: Undo across users?**  
A: Product policy: undo own ops if still visible effect; else request rollback.

### 7.8 Security

**Q39: Can user forge device messages?**  
A: mTLS device cert ≠ user token; map binding in cloud.

**Q40: IDOR on sign_id?**  
A: AuthZ every subscribe/edit; random UUIDs not sufficient alone.

**Q41: Abuse flood LEDs?**  
A: Per-user rate limits; owner mute; anomaly detection.

**Q42: Privacy of presence?**  
A: Only share within ACL; settings to appear invisible.

### 7.9 Scalability & cells

**Q43: Hot celebrity sign?**  
A: Cap concurrent editors; viewers snapshot+throttle; QOS degrade viewers first.

**Q44: 10M signs mostly idle?**  
A: Hibernate; no Kafka hot partition thrash; lazy wake.

**Q45: Reconnect storm?**  
A: Jitter; CDN/object cache for snapshots; MQTT broker autoscale.

**Q46: Multi-cell home?**  
A: `home_cell(sign_id)`; migrate rare; pin during sessions.

### 7.10 Android L5 craft

**Q47: How do you open the interview?**  
A: Grid model, authority, conflict policy, offline, device failure—lock those before drawing boxes.

**Q48: What numbers matter?**  
A: Ops/s per sign, fanout watchers, snapshot storm, offline queue depth, device lag.

**Q49: Common junior mistake?**  
A: Global WebSocket broadcast; trusting client timestamps; OT by default; no device gap resync.

**Q50: How to show L5 seniority?**  
A: Explicit deal-breakers; generation fencing; outbox; coalesce; Doze/FCM reality; progressive scale.

### 7.11 Alternatives & pushbacks

**Q51: Just use Firebase Realtime Database?**  
A: Possible MVP; still need device bridge, ACL, conflict UX, firmware contract—don’t stop at “Firebase.”

**Q52: Just use Git on device?**  
A: Wrong granularity/latency; poor LED apply.

**Q53: Operational transform like Google Docs?**  
A: Signal you know OT—but justify LWW for registers.

**Q54: Peer-to-peer CRDT only?**  
A: Cool research; physical device + ACL + audit push you to cloud coordination for WAN product.

### 7.12 Worked failure drills

**Q55: Gateway deployed, half connections drop.**  
A: Clients exponential backoff + jitter; resume `last_seq`; metrics on resync ratio.

**Q56: Kafka partition stuck for sign.**  
A: Page on lag; dual-write outbox to PG fallback optional; don’t let device spin.

**Q57: Alice offline 2 days, Bob changed everything.**  
A: Pull snapshot; Alice’s pending LWW mostly lose; UI review list before push optional.

**Q58: LOCAL_OVERRIDE then cloud edits arrive.**  
A: Mode exit requires merge wizard: device snapshot vs cloud; pick baseline; generation bump.

### 7.13 Glossary

| Term | Meaning |
|------|---------|
| Generation | Monotonic epoch of grid truth; fences rollback |
| Seq | Per-sign op ordinal |
| LWW-Register | Last-write-wins value per field |
| Outbox | Durable events to publish after commit |
| Hibernation | Tear down hot rooms for idle signs |
| LOCAL_OVERRIDE | Explicit device-authoritative mode |

### 7.14 Appendix — Op envelope (protobuf sketch)

```text
message CellOp {
  string op_id = 1;
  string sign_id = 2;
  uint32 x = 3;
  uint32 y = 4;
  Field field = 5; // LETTER = 1; COLOR = 2
  oneof value { uint32 glyph = 6; uint32 rgb = 7; }
  string actor_id = 8;
  int64 client_ts_ms = 9;
}
message Accept {
  string op_id = 1;
  uint64 seq = 2;
  int64 server_ts_ms = 3;
  uint64 generation = 4;
  bool applied = 5; // false if LWW loser stored for audit only? or still applied chronologically with winner last
}
```

**Note:** Even LWW losers are **logged**; the **materialized grid** holds winners only.

### 7.15 Appendix — State machine (device)

```text
BOOT -> CONNECTING -> SYNCING (snapshot|replay) -> LIVE
LIVE --gap--> SYNCING
LIVE --rollback gen--> SYNCING
Any --auth_fail--> unpaired
```

### 7.16 Appendix — Conflict matrix

| A\B | Diff cell | Same cell letter | Same cell color |
|-----|-----------|------------------|-----------------|
| Online/online | merge | LWW | LWW |
| Offline/offline | merge | LWW + chip | LWW + chip |
| Offline/online | merge | LWW | LWW |

### 7.17 Appendix — NFR card

```text
Online p50 edit path < 150ms (regional)
Durable ACK before pending clear
Device apply < 1s when connected
Idempotent op_id
Cloud SoT; generation fence
Android: Room queue + FCM wake
```

### 7.18 Appendix — Why not central lock per cell

| Approach | Problem |
|----------|---------|
| Exclusive lock | Dead locks with offline; high friction |
| Lease | Expiry races; still need LWW |
| LWW (+ presence) | Matches product; simpler |

### 7.19 Appendix — 10×/100×/1,000× checklist

| Item | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Shard by sign | ✓ | ✓ | ✓ |
| Home cell | | ✓ | ✓ |
| Edge MQTT PoP | | optional | ✓ |
| Hibernate idle | optional | ✓ | ✓ |
| MV-Register CRDT | | optional | product-driven |
| Snapshot CDN | ✓ | ✓ | ✓ |

### 7.20 Appendix — Interview whiteboard order

```text
1) Grid + ops API
2) Authority (cloud vs device)
3) LWW vs CRDT vs OT table
4) Online path diagram
5) Offline queue
6) Device MQTT + gap resync
7) Rollback/audit
8) Scale by sign_id + storms
9) Android Doze/battery
10) Deal-breakers
```

### 7.21 Appendix — Sample metrics dashboard

| Panel | Signal |
|-------|--------|
| Live ops/s | Traffic |
| Accept p99 | UX |
| Device lag p99 | Hardware freshness |
| Conflict rate | Product pain |
| Resync/s | Reliability |
| Queue depth (telemetry) | Client health opt-in |

### 7.22 Appendix — ACL model

```text
roles: OWNER | EDITOR | VIEWER
OWNER: pair, rollback, ACL
EDITOR: EditCell
VIEWER: Subscribe + presence optional
Service account: device identity ≠ human EDITOR
```

### 7.23 Appendix — Coalescing algorithm

```text
on ColorDrag(cell, rgb):
  pending[cell] = rgb
  schedule flush in 50ms
on flush:
  emit one CellOp COLOR with latest rgb
letter taps: emit immediately
```

### 7.24 Appendix — Snapshot resync threshold

```text
if device_seq_gap > 500 or missing_seq: GetSnapshot
else: replay ops seq+1..head
Tradeoff: snapshot bandwidth vs many small ops
```

### 7.25 Appendix — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Use OT” | Registers don’t need it |
| “CRDT everywhere” | Cost on MCU + product UX; LWW enough |
| “P2P libp2p” | ACL/audit/device management |
| “Firebase only” | Still design device + conflicts |
| “Strong consistency globally” | Per-sign serial; not global wall |

### 7.26 Appendix — Related Google systems intuition

| Analogy | Borrow | Don’t borrow blindly |
|---------|--------|---------------------|
| Docs OT | Conflict mindset | String OT engine |
| FCM | Wake clients | Op transport of record |
| Nearby / BLE | Pairing | Runtime SoT |
| Pub/Sub | Fanout | Device constrained broker features |

### 7.27 Appendix — Testing strategy

| Test | Validates |
|------|-----------|
| Idempotent retry | op_id |
| Concurrent same cell | LWW deterministic |
| Gap skip MQTT | Resync |
| Rollback fence | generation |
| Room crash mid-sync | No dup effect |
| Reconnect storm k6 | Jitter/cache |

### 7.28 Appendix — Data retention

| Data | Hot | Cold |
|------|-----|------|
| Materialized grid | Forever (current) | — |
| Op log | 7–30d | 1y archive |
| Snapshots | last K + daily | compliance |
| Presence | minutes | none |

### 7.29 Appendix — LOCAL_OVERRIDE sequence

```text
Owner enables LOCAL_OVERRIDE on LAN
Device accepts local ops with local_seq (signed device)
Cloud marked mode=LOCAL; WAN edits rejected or queued
Exit: device UploadSnapshot → cloud conflict review → generation++ → CLOUD mode
```

### 7.30 Appendix — Final seniority signals

- Name **deal-breakers** early (dual SoT, client clocks).  
- Separate **materialized grid** vs **audit log**.  
- Treat **device as projector** with generation fencing.  
- Quantify **fanout** and **reconnect storms**.  
- Show Android **Doze/FCM/Room** realism.  
- Progressive scale with `sign_id` home cells.

---

*End of Multi-User Connected-Sign Controller system design.*
