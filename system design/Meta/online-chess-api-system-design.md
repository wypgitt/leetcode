# System Design: Online Chess API

> **Focus areas:** REST/WebSocket API design · Resources & state machines · Auth · Idempotency · Clocks · Matchmaking contracts · Error model · Versioning  
> **Style:** API-first product design with progressive scale (10× → 100× → 1,000×) — infra only as needed to back the API  
> **Quality bar:** Clear resource model, explicit game invariants in API semantics, deal-breakers for “client-authoritative moves”  
> **Interview theme:** Meta API design interview flavor — chess as the domain; **contracts, consistency, and client UX** over drawing Kafka clusters first

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

Goal: **bound the API**—a clean, evolvable **Online Chess HTTP + realtime API** for matchmaking, authoritative gameplay, clocks, draws/resigns, reconnect, and spectate hooks. Distributed infra exists behind the API, but the interview wins on **resource design, state transitions, idempotency, and error semantics**.

### 1.0 What this is / is not

| Dimension | **Online Chess API (this doc)** | Not this |
|-----------|--------------------------------|----------|
| Primary job | Stable client-facing contracts | Deep Kafka cell topology first |
| Success | Correct game semantics over the wire | Pretty board CSS |
| Authority | Server validates moves/clocks | Trust client FEN |
| Realtime | WebSocket (or SSE) events | Poll-only MVP optional degrade |
| Scale story | How API shape enables scale | Premature 1B-user shard porn |

**Scope statement:** Design an online chess **API**: resources, auth, matchmaking, moves, clocks, game lifecycle, reconnect, spectate, ratings—with progressive load; infra sketched only to support API guarantees.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Clients? | Mobile + web | REST + WebSocket; compact payloads |
| F2 | Auth? | User accounts; guests optional | OAuth2/JWT; guest tokens |
| F3 | Modes? | Bullet/blitz/rapid; rated/casual | `time_control` + `rated` fields |
| F4 | Matchmaking? | Rating-based seek | `Seek` resource + match callback/event |
| F5 | Moves? | Server-authoritative | `POST /games/{id}/moves` validates |
| F6 | Clocks? | Server clocks with increment | Clock fields on game; flag events |
| F7 | Draw/resign/abort? | Yes with rules | Explicit action endpoints / events |
| F8 | Reconnect? | Resume state + missed events | Snapshot + `since_seq` |
| F9 | Spectate? | Public games optional | Read-only channel; separate from players |
| F10 | History? | PGN / move list | `GET /games/{id}` + export |
| F11 | Ratings? | After rated games | Rating on users; async update OK if visible |
| F12 | Anti-cheat? | Telemetry hooks | Events ingested; not blocking move ACK path heavily |

**MVP functional scope:**

1. Auth + user profile with ratings per time class.  
2. Create/cancel seek; get matched into a game.  
3. Game resource with full state (FEN, moves, clocks, status).  
4. Submit move (SAN or UCI); server validates; broadcasts.  
5. Resign, draw offer/accept/decline, abort policy.  
6. WebSocket game channel with sequenced events.  
7. Reconnect: fetch snapshot + replay from sequence.  
8. List recent games; get PGN.  
9. Basic spectate subscribe for public games.  
10. Consistent error model + idempotency keys on mutating calls.

**Out of MVP:**

- Full tournament/swiss API surface  
- Variants (Crazyhouse) — keep `ruleset` extension point  
- Perfect real-time cheat bans  
- Voice/video  
- Server-side engine opponent as core (thin bot user OK)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Move visibility latency | Snappy | p99 < 500ms in-region event delivery |
| N2 | API correctness | Illegal moves never accepted | Server rules engine |
| N3 | Clock fairness | Server SoT | Client clock display only |
| N4 | Durability | Finished games persisted | Persist before/at ACK policy |
| N5 | Idempotency | Retries safe | `Idempotency-Key` / `client_move_id` |
| N6 | Versioning | Evolve without breaking | `/v1` + additive changes |
| N7 | Availability | Play critical | Degrade spectate/history first |
| N8 | Privacy | Private games | AuthZ on game resources |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `POST /seeks` → matched → `game.started` WS → moves → checkmate → `game.ended` + ratings.  
2. Draw offer → accept → end draw.  
3. Disconnect → reconnect with `since_seq` → catch up.  
4. Spectator connects to public game stream.  
5. Abort within policy window → no rating change.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-submit move | Idempotent same `client_move_id` → same response |
| Illegal move | `409` / `422` with reason; clock keeps running |
| Move after flag | `409 GAME_OVER` or `CLOCK_FLAG` |
| Seek matched twice | Server atomic claim; one game only |
| WS drop mid-game | HTTP snapshot + resume stream |
| Draw offer spam | Rate limit; one outstanding offer |
| Spectate storm | Separate channel; don’t block players |
| Stale client FEN | Ignore client FEN; server returns authoritative state |
| Guest vs rated | Reject rated seek for guests |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 1M | 10M | 100M | 1B |
| Concurrent games | 25K | 250K | 2.5M | 25M |
| Move submits/s | 5K | 50K | 500K | 5M |
| WS events/s (players) | ~10K | ~100K | ~1M | ~10M |
| Seek ops/s | 200 | 2K | 20K | 200K |
| Spectate events/s | 20K | 200K | 2M | 20M+ |
| REST reads (history) | 1K | 10K | 100K | 1M |

**What each jump forces (API-relevant):**

- **10×:** Sticky game ownership; sequenced events; idempotency required.  
- **100×:** Region affinity headers; spectate fanout API separate; cursor pagination everywhere.  
- **1,000×:** Edge WS gateways; read replicas for history; matchmaking partitioned—but **API stays stable**.

### 1.5 Etc. (Constraints & Assumptions)

- Standard chess rules; FIDE-like online adaptations for abort/flag.  
- Prefer **UCI or SAN** — pick one primary (`uci` MVP) + optional SAN.  
- JSON over HTTP/WS; protobuf later as additive transport.  
- Infra behind API: game service, matchmaking, rating, store—sketched lightly.

**Scope statement:**

> Design an online chess **API** with clear resources (User, Seek, Game, Move, Rating), server-authoritative move/clock semantics, sequenced realtime events, reconnect, idempotent mutations, and a versioned error model—scalable underneath without breaking clients.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (API-centric)

| Class | Endpoint family | Baseline peak | Plane |
|-------|-----------------|---------------|-------|
| **Seek** | `/seeks` | ~200/s | Matchmaking |
| **Move** | `POST /games/{id}/moves` | ~5K/s | Game authority |
| **WS fanout** | game channels | ~10K/s | Gateway |
| **Snapshot** | `GET /games/{id}` | reconnect spikes | Game + cache |
| **History** | `/users/{id}/games` | lower | Read store |
| **Spectate** | `/games/{id}/stream` | bursty | Fanout |

**Anti-pattern:** one “QPS” mixing seeks, moves, and spectate amplification.

### 2.2 Payload sizes

```text
Move request ~100–200 B JSON
Game snapshot ~2–10 KB (moves list grows)
Event frame ~200–500 B
PGN export ~2–20 KB typical game
Design: incremental events > resend full PGN every move
```

### 2.3 Clock precision

```text
Server ms timestamps
Increment e.g. +2s
Flag detection on move attempt + timer wheel
API returns clocks_ms after every event for sync
```

### 2.4 Reconnect amplification

```text
Mass regional blip: 50K clients snapshot GET
Need CDN/cache carefully (NOT for live clocks) — only history
Live snapshot from game owner shard with rate limits
```

### 2.5 Concurrent games & move arithmetic

```text
Baseline: 100K concurrent games (order)
Avg move rate: human blitz ~0.05 moves/s/game → 5K moves/s
Bullet spikes higher; classical lower
Each move: 1 authority validate + 1 persist + 2 player WS + N spectate
Spectate fanout: 1% games hot with 1K watchers → careful isolation
100×: 10M games → 500K moves/s → sharded authorities mandatory
```

### 2.6 Matchmaking pool math

```text
Seek create ~200/s; average wait 5s → ~1K open seeks
Matching: rating bucket ±Δ; time_control exact; rated flag
Scan cost: index by (time_control, rating_bucket) not O(N) all seeks
10×: 2K seeks/s → partitioned matchmakers by time_class
```

### 2.7 Clock tick economics

```text
Do NOT wake every game every 100ms globally
Lazy evaluation: compute remaining on event (move/flag check)
Timer wheel only for games near flag (remaining < 30s) or idle abort
Near-flag set size ≪ concurrent games (e.g. 1–5%)
```

### 2.8 Storage growth

```text
Game record ~5–20 KB with moves
1M games/day × 10 KB ≈ 10 GB/day
90d hot retention + cold archive
PGN export generated or stored — prefer generate from move list
```

### 2.9 Latency budgets (API)

```text
POST move p99:
  authZ 1ms | load state 2–5ms | validate 0.1–1ms | persist 2–5ms | ACK
  Target total < 50–100ms same region
WS event after ACK: <50ms to opponent p99
Seek match notify: <200ms after match decision
```

---

## 3. High-Level Design

### 3.1 Resource model

| Resource | Identity | Key fields |
|----------|----------|------------|
| User | `user_id` | username, ratings{} |
| Seek | `seek_id` | user, time_control, rated, range |
| Game | `game_id` | white, black, state, clocks, seq |
| Move | `(game_id, ply)` | uci, san, ts, clocks_after |
| DrawOffer | `(game_id, offer_id)` | from, status |
| Rating | `(user_id, time_class)` | value, rd optional |

### 3.2 REST API surface (v1)

| Method | Path | Semantics |
|--------|------|-----------|
| `POST` | `/v1/seeks` | Create seek |
| `DELETE` | `/v1/seeks/{seek_id}` | Cancel |
| `GET` | `/v1/seeks/{seek_id}` | Status (open/matched) |
| `GET` | `/v1/games/{game_id}` | Authoritative snapshot |
| `POST` | `/v1/games/{game_id}/moves` | Submit move |
| `POST` | `/v1/games/{game_id}/resign` | Resign |
| `POST` | `/v1/games/{game_id}/draw/offer` | Offer draw |
| `POST` | `/v1/games/{game_id}/draw/accept` | Accept |
| `POST` | `/v1/games/{game_id}/draw/decline` | Decline |
| `POST` | `/v1/games/{game_id}/abort` | Abort if legal |
| `GET` | `/v1/games/{game_id}/pgn` | Export |
| `GET` | `/v1/users/{id}` | Public profile |
| `GET` | `/v1/users/{id}/games` | History cursor |
| `GET` | `/v1/ws` | WebSocket upgrade (auth) |

### 3.3 WebSocket contract

```text
Client → Server:
  { "op": "subscribe", "channel": "game:{id}", "since_seq": 42 }
  { "op": "ping" }

Server → Client (sequenced):
  { "seq": 43, "type": "move", "data": {...} }
  { "seq": 44, "type": "clock", "data": {...} }
  { "seq": 45, "type": "game_ended", "data": {...} }
```

**Rule:** Every gameplay mutation that changes state increments `seq`. Clients reconcile by seq, not wall clock.

### 3.4 Game status state machine (API-visible)

```text
PENDING → ACTIVE → ENDED
ENDED.reason ∈ {
  checkmate, resignation, timeout, draw_agreement,
  stalemate, insufficient_material, fifty_move,
  threefold, abort, abandon
}
```

### 3.5 Move request / response

**Request:**

```json
{
  "client_move_id": "c9a1…",
  "uci": "e2e4",
  "offer_draw": false
}
```

**Response (200):**

```json
{
  "game_id": "g_123",
  "seq": 12,
  "ply": 1,
  "uci": "e2e4",
  "san": "e4",
  "fen": "…",
  "status": "active",
  "clocks": {"white_ms": 178000, "black_ms": 180000, "server_ts": 1710000000123},
  "turn": "black"
}
```

**Error (422):**

```json
{
  "error": {
    "code": "ILLEGAL_MOVE",
    "message": "Move leaves king in check",
    "game_id": "g_123",
    "seq": 11,
    "fen": "…",
    "clocks": {"white_ms": 177500, "black_ms": 180000, "server_ts": 1710000000456}
  }
}
```

**Important:** Even on illegal move, return **authoritative clocks/seq** so clients resync.

### 3.6 Why X over Y (API decisions)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Authority | Server rules engine | Fairness | Client sends FEN as truth |
| Realtime | WS events + HTTP mutations | Clear ACK semantics | Moves only over unreliable fire-and-forget UDP fantasy |
| Move ID | `client_move_id` idempotency | Mobile retries | Rely on network “once” |
| Clocks | Server ms in every event | Sync | Trust client timer |
| Spectate | Separate subscribe | Protect players | Same write path as movers |
| Versioning | `/v1` additive JSON | Evolve | Random breaking field renames |
| Seek vs Game | Distinct resources | Matchmaking lifecycle | Overload `POST /games` to mean seek |
| Flag order | Check clock before apply move | Fair timeout | Accept move then notice flag |
| Ratings | Async post-game | Don’t block ACK | Sync Glicko on move path |
| Anti-cheat | Hooks + offline | Latency | Engine on every move blocking |
| History | Cursor pages | Scale | Offset deep history |
| Abort | Policy window | Griefing | Abort anytime after move 20 |

**Expanded deal-breakers:**

1. **Client-authoritative FEN** — cheating trivial; API must validate.  
2. **No idempotency on moves** — mobile double-submit loses/desyncs games.  
3. **Mixing spectate load into player WS path** — viral game DOSes players.  
4. **Trusting client clocks** — flag fights and unfair wins.  
5. **Matchmaking as `POST /games` with empty body tricks** — unclear lifecycle; seeks need cancel/expiry.

### 3.7 AuthZ matrix

| Action | White/Black | Spectator | Other |
|--------|-------------|-----------|-------|
| Read public game | ✓ | ✓ | ✓ |
| Read private game | ✓ | ✗ | ✗ |
| Move | turn player | ✗ | ✗ |
| Resign | either player | ✗ | ✗ |
| Draw accept | recipient | ✗ | ✗ |

---

## 4. Architecture Diagram

```text
  Mobile/Web clients
           |
           |  HTTPS REST                 WSS
           v                             v
  +--------+----------+        +--------+----------+
  | API Gateway       |        | WS Gateway        |
  | auth, rate limit  |        | subscribe, seq    |
  | idempotency       |        +---------+---------+
  +--------+----------+                  |
           |                             |
           v                             v
  +--------+----------+        +---------+---------+
  | Chess API Service |<------>| Game Authority    |
  | resource mapping  |        | (per game_id)     |
  +--+------+---------+        | rules + clocks    |
     |      |                  +---------+---------+
     |      |                            |
     v      v                            v
 Seeks   Ratings                   Game Store
 Matchmaking                        Event log (seq)
     |                                   |
     v                                   v
  Seek queue                         Spectate fanout
                                     (read replicas)
```

**Matchmaking sequence:**

```text
POST /seeks
 → validate rating/time_control
 → enqueue
 → match found
 → create Game PENDING→ACTIVE
 → notify both users via WS `game_matched` + body includes game_id
 → DELETE seek resources
```

**Move sequence:**

```text
POST /games/{id}/moves (Idempotency-Key / client_move_id)
 → authZ turn
 → load authoritative state
 → check clock flag first (policy order)
 → validate legal move
 → apply → persist → seq++
 → ACK HTTP response
 → publish WS event to players (+ spectate async)
```

**Reconnect sequence:**

```text
GET /games/{id} → snapshot {seq, fen, moves, clocks, status}
WS subscribe since_seq=snapshot.seq
 → receive seq+1…
```

---

## 5. Design Deep Dive

### 5.1 Reliability (API semantics)

#### 5.1.1 Invariants clients can trust

1. **Server FEN/status is authoritative** after every successful response.  
2. **`seq` monotonically increases** per game; no gaps on a single authority (gaps ⇒ client must snapshot).  
3. **Illegal move never changes board**; may still update sync fields (clocks).  
4. **Idempotent move retries** return the original success body.  
5. **Game terminal state is sticky** — further moves error with `GAME_OVER`.  
6. **Clock fields use server_ts** for client extrapolation between events.

#### 5.1.2 Ordering: flag vs move

Document explicitly:

```text
On move request at server_ts T:
  if current_player clock expired at T: end by timeout (ignore move)
  else validate move; apply; switch clock with increment
```

#### 5.1.3 Persistence vs ACK

Pick and advertise:

| Policy | Pros | Cons |
|--------|------|------|
| Persist then ACK move | Safe | Slightly higher latency |
| ACK then persist async | Faster | Risk on crash — compensate with WAL |

**MVP recommendation:** persist to game log before ACK (or simultaneous disk WAL).

#### 5.1.4 Error model (stable codes)

| Code | HTTP | When |
|------|------|------|
| `ILLEGAL_MOVE` | 422 | Rules fail |
| `NOT_YOUR_TURN` | 409 | Wrong side |
| `GAME_OVER` | 409 | Terminal |
| `CLOCK_FLAG` | 409 | Timed out |
| `IDEMPOTENCY_CONFLICT` | 409 | Same key different body |
| `SEEK_NOT_FOUND` | 404 | Cancel race |
| `UNAUTHORIZED` | 401 | Auth |
| `FORBIDDEN` | 403 | Private game |
| `RATE_LIMITED` | 429 | Abuse |
| `ABORT_NOT_ALLOWED` | 409 | Policy |

### 5.2 Scalability (what the API enables)

#### 5.2.1 Game affinity

```text
Header optional: X-Game-Owner: cell-14
Or resolve via game_id hash → authority
Clients don't shard — gateways route
```

#### 5.2.2 Spectate isolation

API: `subscribe channel=spectate:game_id` delivers **at-least-once**, may coalesce clocks. Player channel prioritizes latency/correctness.

#### 5.2.3 Pagination

All list endpoints: cursor tokens opaque, never offsets.

#### 5.2.4 Progressive scale vs API stability

| Scale | Infra change | API change |
|-------|--------------|------------|
| 10× | Sticky owners | None |
| 100× | Regional cells | Optional `region` field already present |
| 1,000× | Edge WS | Same events; maybe binary encoding additive |

### 5.3 Maintainability

#### 5.3.1 Versioning policy

- Additive fields OK.  
- Never reuse enum meanings.  
- Deprecate with `Sunset` headers.  
- New move representation → support both for a generation.

#### 5.3.2 Contract testing

- Golden games: illegal castling, en passant, promotion, repetition claims.  
- Idempotency fuzz.  
- Clock flag boundary tests.  
- WS reconnect gap tests.

#### 5.3.3 Observability (API)

| Metric | Why |
|--------|-----|
| `move_success_rate` | Health |
| `illegal_move_rate` | Client bugs / attacks |
| `ack_latency_p99` | UX |
| `ws_catchup_depth` | Blips |
| `idempotent_hits` | Mobile network quality |

### 5.4 Move validation deep dive

#### 5.4.1 Validation pipeline

```text
1. AuthN + AuthZ (player, turn)
2. Idempotency lookup (client_move_id)
3. Clock flag check at server_ts
4. Status must be ACTIVE
5. Parse UCI/SAN → from,to,promo
6. Pseudo-legal generation / apply
7. King safety (including pinned moves)
8. Special: castling rights, ep square, promo
9. Claim checks: threefold / 50-move if offered via API
10. Persist + seq++ + ACK + publish
```

#### 5.4.2 Rules engine placement

| Placement | Pros | Cons |
|-----------|------|------|
| In-process library on authority | Low latency | Deploy coupled |
| Sidecar | Isolate crashes | Hop cost |
| **MVP: in-process** | Meets p99 | Fuzz heavily |

#### 5.4.3 Illegal move philosophy

Return **422 ILLEGAL_MOVE** with authoritative `fen`, `seq`, `clocks` — client resyncs UI; never soft-apply.

#### 5.4.4 Draw claims API

```text
POST /games/{id}/claim { type: "threefold"|"fifty_move" }
Server verifies from move history hash counts — not client honor
```

### 5.5 Clocks deep dive

#### 5.5.1 Representation

```text
clocks: {
  white_ms, black_ms,
  running: "white"|"black"|null,
  last_switch_server_ts,
  increment_ms,
  time_control: "180+2"
}
```

Client display: `remaining = *_ms - (now - last_switch)` for side to move; resync on every event.

#### 5.5.2 Flag detection

```text
On any mutation or timer-wheel fire:
  if side_to_move remaining <= 0 → GAME_OVER timeout
Move that arrives after flag: rejected with CLOCK_FLAG (game already ended)
```

#### 5.5.3 Increment & delay variants

Document supported: sudden death, increment (Fischer), optional bronstein later. API `time_control` string parsed server-side; unknown → 400.

#### 5.5.4 Disconnect clocks

Clock **keeps running** (standard online chess). Abort/abandon policies separate (no-move in opening N seconds).

### 5.6 Matchmaking APIs deep dive

#### 5.6.1 Seek resource lifecycle

```text
POST /seeks → OPEN
match → MATCHED (body includes game_id) → seek deleted/archived
DELETE → CANCELED
TTL expiry → EXPIRED
```

#### 5.6.2 Matching index

```text
Key: (variant, time_class, rated)
Structure: rating-sorted structures / bucket queues
On seek: probe overlapping rating window; CAS claim both seeks
Create game atomically; notify both
```

#### 5.6.3 Fairness

- No “sneak peek” opponent identity before accept if rated (policy).  
- Prevent self-match / multi-account pairing heuristics (hooks).  
- Rate-limit seek spam.

#### 5.6.4 Challenges (direct match) Phase 1.5

```text
POST /challenges { opponent_id, time_control }
 → PENDING until accept/decline/expire
On accept → same Game create path as seeks
```

### 5.7 WebSockets deep dive

#### 5.7.1 Channels

| Channel | Members | Guarantees |
|---------|---------|------------|
| `game:{id}` | players | Ordered seq; low latency |
| `spectate:{id}` | watchers | At-least-once; may coalesce clocks |
| `user:{id}` | that user | match found, seeks expired |

#### 5.7.2 Reconnect algorithm (client)

```text
1. GET snapshot → seq=S
2. WS subscribe since_seq=S
3. If server signals GAP → re-snapshot
4. Buffer events during snapshot race; dedupe by seq
```

#### 5.7.3 Backpressure

```text
Slow spectator: drop/coalesce clock frames; never block player publish
Per-connection quotas; max subscriptions
```

#### 5.7.4 Why HTTP for moves still

ACK semantics, idempotency keys, easy retries, cache-free mutation clarity. WS can optionally carry move ops as dual transport later — same authority.

### 5.8 Anti-cheat hooks (API-first)

#### 5.8.1 What belongs in online path

| Hook | When | Blocks move? |
|------|------|--------------|
| Rate absurd moves | Online | Soft delay / flag review |
| CAPTCHA on seek storm | Online | Seek reject |
| Engine score shadow | Async | No (post-game) |
| Multi-accounting pair | Matchmaking | Reroll match |

#### 5.8.2 Event stream for offline

```text
Emit GameMove events to anti-cheat pipeline:
  {game_id, ply, uci, clocks, ratings, client_meta}
Store for cloud-engine analysis; API exposes appeal status later
```

#### 5.8.3 Privacy

Client metadata minimized; retain under policy; never expose opponent device fingerprints via API.

### 5.9 Progressive scale (10× / 100× / 1,000×)

| Jump | Infra | API |
|------|-------|-----|
| →10× | Sticky game owners; timer wheels | Unchanged contracts |
| →100× | Regional cells; spectate fanout tree | Optional `region` already on resources |
| →1,000× | Edge WS gateways; binary event encoding additive | Same JSON `/v1`; `/v2` only if needed |

**Narrative:**

- **10×:** Authority affinity + idempotency correctness dominate.  
- **100×:** Spectate isolation and regional matchmaking pools.  
- **1,000×:** Edge fanout; anti-cheat offline scale; API semantics stable.

### 5.10 Failure drills

| Drill | Expected |
|-------|----------|
| Authority crash mid-move | WAL/persist: client retries idempotent; at-most-one apply |
| WS blip | Snapshot + catch-up; clocks resync via server_ts |
| Matchmaker double-claim | CAS / txn ensures one game |
| Rules lib bug | Feature flag rollback; pause rated |

### 5.11 Ratings API (post-game)

```text
On ENDED:
  enqueue RatingJob {game_id, white, black, result, time_class}
  compute Glicko/Elo offline-ish (seconds OK)
  expose via GET /users/{id} when ready
  WS user channel: rating_updated event
Never block move ACK or game_ended on rating write
```

### 5.12 Abort / abandon policies (API-visible)

| Condition | Result |
|-----------|--------|
| Both agree abort in opening | `abort` |
| One player no move in T seconds at start | `abandon` unrated optional |
| Disconnect midgame | clock runs; timeout possible |
| Cheat ban midgame | `ended` special reason + rating unwind policy |

Document in OpenAPI enums so clients don’t invent UI.

### 5.13 Progressive scale narrative (long form)

- **→10×:** Sticky authorities; idempotency correctness; timer wheels for near-flag only.  
- **→100×:** Regional cells; spectate trees; matchmaking pools by time_class.  
- **→1,000×:** Edge WS; binary events additive; anti-cheat offline fleet — `/v1` move contract unchanged.

---

## 6. Wrap-Up

### 6.1 Summary

The Online Chess API is a **versioned resource + sequenced event contract** around server-authoritative game state. Matchmaking creates games; moves/actions are idempotent HTTP mutations; WebSockets deliver ordered `seq` events; reconnect is snapshot + catch-up. Scale happens under the gateway without rewriting client semantics.

### 6.2 Trade-offs

| Trade-off | Choice |
|-----------|--------|
| HTTP move vs WS-only move | HTTP mutation + WS notify (clear ACK) |
| Full snapshot vs delta | Both: snapshot on GET; deltas on WS |
| Strict vs eventual ratings | Eventual OK; game result immediate |
| SAN vs UCI | UCI primary; SAN derived |

### 6.3 Deal-breakers

1. Client-authoritative board/clocks.  
2. No idempotency on moves.  
3. Spectate sharing player write path.  
4. Breaking JSON fields without versioning.  
5. Moves accepted after terminal status.

### 6.4 Scale one-liner

Stable `/v1` contracts → sticky game owners at 10× → regional cells at 100× → edge WS at 1,000× without client rewrites.

### 6.5 Interview posture

Lead with **resources and sequences**, then lightly sketch game authority service. Resist turning it into only infra.

---

## 7. Deeper / Related Interview Questions

### 7.1 Resource & modeling

**Q1: Why is Seek separate from Game?**  
A: Different lifecycle and authZ; many canceled seeks never become games; cleaner matchmaking.

**Q2: Why not WebSocket-only for moves?**  
A: Mobile networks drop; HTTP idempotent POST gives clearer retry/ACK; WS great for push.

**Q3: FEN in every response — heavy?**  
A: Convenient for MVP; at scale can send FEN every N moves + deltas; keep field optional additive.

**Q4: How to model variants later?**  
A: `ruleset: "chess"` enum; engine plugin server-side; clients ignore unknown safely.

**Q5: Correspondence (days/move) same API?**  
A: Same resources; different clock semantics (`deadline_ts`); maybe poll-friendly.

**Q6: How are game IDs generated?**  
A: ULID/UUID; opaque; optionally embed cell hint—but don’t require clients to parse.

### 7.2 Moves & rules

**Q7: SAN vs UCI?**  
A: UCI unambiguous for engines; SAN nice UX—server can accept UCI and return both.

**Q8: How to claim threefold repetition?**  
A: `POST /moves` with claim flag or `POST /claim/threefold`; server verifies history.

**Q9: Promotion required?**  
A: UCI `e7e8q`; reject incomplete promotion.

**Q10: Premoves?**  
A: Client-only queue; server accepts only on turn with new request.

**Q11: What if two moves race?**  
A: Authority serializes; second `NOT_YOUR_TURN` or idempotent duplicate.

### 7.3 Clocks

**Q12: How do clients display smooth clocks?**  
A: Extrapolate from `clocks + server_ts`; resync on every event; never trust local alone for flag.

**Q13: Increment when applied?**  
A: After legal move for the mover, before turn switch—document.

**Q14: Clock API for flag without move?**  
A: Server timer emits `game_ended` timeout event; clients may also probe `GET` snapshot.

**Q15: Latency advantage fairness?**  
A: Server receive time; optional lag comp out of MVP; don’t let client subtract ping themselves.

### 7.4 Realtime & reconnect

**Q16: At-least-once WS delivery?**  
A: Yes possible duplicates; clients dedupe by `seq`.

**Q17: Snapshot then subscribe race?**  
A: Subscribe with `since_seq`; allow overlap; dedupe seq.

**Q18: Missed seq gap?**  
A: Resnapshot; don’t invent events.

**Q19: Multiple devices same user?**  
A: Both may subscribe; moves authZ user; last move wins via authority; UX warn optional.

**Q20: Presence (online/offline)?**  
A: Separate presence channel; don’t overload game seq.

### 7.5 Matchmaking API

**Q21: Expand rating window how?**  
A: Server-side policy; client may display expected wait; `GET seek` returns `window` widening.

**Q22: Cancel race with match?**  
A: Atomic transition: cancel fails with `SEEK_ALREADY_MATCHED` + `game_id`.

**Q23: Pool isolation?**  
A: Key by `(time_control, rated, variant, region?)`.

**Q24: Fairness vs wait time — API transparency?**  
A: Return `estimated_wait_s` advisory; not a guarantee.

### 7.6 Ratings & history

**Q25: When do ratings appear?**  
A: `game_ended` includes provisional `rating_delta` or clients poll user profile until updated.

**Q26: Glicko vs Elo in API?**  
A: Opaque `rating` number + optional `rd`; algorithm server-side.

**Q27: History pagination?**  
A: Cursor by `(ended_at, game_id)`.

**Q28: PGN authenticity?**  
A: Server-signed or HTTPS only; PGN generated from authoritative move list.

### 7.7 Security & abuse

**Q29: Anti-cheat vs move latency?**  
A: Persist move timings/engine features async; don’t run heavy ML before ACK.

**Q30: Takeover of game stream?**  
A: Auth tokens bound to user; spectate tokens scoped read-only.

**Q31: Enumeration of game IDs?**  
A: Unpredictable IDs + authZ; private games 404 vs 403 policy (prefer 404).

**Q32: Rate limits?**  
A: Per-user move rate absurdly high for chess still capped; seek creation stricter.

### 7.8 Versioning & errors

**Q33: Additive change example?**  
A: Add `accuracy` field to ended game; old clients ignore.

**Q34: Breaking change process?**  
A: `/v2`; dual-run; migrate; sunset.

**Q35: Why machine codes not only strings?**  
A: Stable `ILLEGAL_MOVE` for client branching; message for humans.

**Q36: Partial success?**  
A: Avoid; moves are atomic. Batch APIs out of MVP.

### 7.9 Infra-lite (only as needed)

**Q37: Where does authority live?**  
A: Game service shard by `game_id`; API gateway routes.

**Q38: Do we need Kafka for moves?**  
A: Not on critical ACK path; use for analytics/spectate fanout optionally.

**Q39: Store choice?**  
A: In-mem + durable log for active; SQL/KV for finished games—say briefly, return to API.

**Q40: How to open this Meta-style API interview?**  
A: Actors, resources, critical flows, non-goals—then endpoints + state machine before shards.

**Q41: What impresses?**  
A: Idempotency, seq reconnect, error bodies with authoritative state, spectate isolation, versioning policy.

**Q42: Common mistake?**  
A: Jumping to microservices mesh without defining move ACK semantics.

**Q43: End strong?**  
A: Restate invariants clients trust + one evolvability rule + one deal-breaker.

---

### Appendix A — OpenAPI-ish seek create

```yaml
POST /v1/seeks
headers:
  Authorization: Bearer ...
  Idempotency-Key: string
body:
  time_control: { base_ms: 180000, increment_ms: 2000 }
  rated: true
  rating_range: { min_delta: 0, max_delta: 100 } # optional hint
response 201:
  seek_id: ...
  status: open
```

### Appendix B — Game snapshot schema

```json
{
  "game_id": "g_123",
  "seq": 40,
  "status": "active",
  "ruleset": "chess",
  "rated": true,
  "time_control": {"base_ms": 180000, "increment_ms": 2000},
  "white": {"user_id": "u1", "rating": 1620},
  "black": {"user_id": "u2", "rating": 1610},
  "fen": "...",
  "moves": [{"ply": 1, "uci": "e2e4", "san": "e4"}],
  "clocks": {"white_ms": 170000, "black_ms": 165000, "server_ts": 1710000000},
  "turn": "white",
  "draw_offer_from": null,
  "public": true
}
```

### Appendix C — Event types

| type | data highlights |
|------|-----------------|
| `game_matched` | game_id, color |
| `game_started` | initial clocks |
| `move` | ply, uci, san, fen, clocks |
| `draw_offered` | from |
| `draw_declined` | by |
| `game_ended` | reason, winner, rating_delta? |
| `clock` | optional tick sync |
| `error` | rare server notices |

### Appendix D — Idempotency table

| Key scope | Behavior |
|-----------|----------|
| `Idempotency-Key` on seek | Same seek returned |
| `client_move_id` per game+user | Same move response |
| Resign | Second resign → `GAME_OVER` with same result |

### Appendix E — Abort policy (example)

```text
Abort allowed if:
  both players agree OR
  < 2 plies AND < 15s since start
Else: 409 ABORT_NOT_ALLOWED
```

### Appendix F — Auth tokens

```text
Access JWT: sub=user_id, exp=short
Refresh: rotate
Guest: limited scopes (no rated)
WS: ticket exchange short-lived to avoid long-lived JWT in logs
```

### Appendix G — Rate limit sketch

| Endpoint | Limit |
|----------|-------|
| POST /seeks | 10/min |
| POST moves | 60/min (far above human) |
| GET history | 120/min |
| WS connect | 30/hour |

### Appendix H — NFR card

```text
Server-authoritative moves/clocks
Idempotent mutations
Sequenced WS events
Snapshot + since_seq reconnect
Stable error codes
Spectate isolated
/v1 additive versioning
Persist before move ACK
```

### Appendix I — Progressive scale

| Scale | API | Infra behind |
|-------|-----|--------------|
| Base | Full /v1 | Single region cells |
| 10× | Same | Sticky game owners |
| 100× | Same + region hint | Matchmaking partitions |
| 1,000× | Same (+ binary opt) | Edge WS + history replicas |

### Appendix J — Comparison: move transport

| Transport | ACK clarity | Retry | Verdict |
|-----------|-------------|-------|---------|
| HTTP POST | Excellent | Idempotent key | **Primary** |
| WS request/response | Good | Need corr ids | Optional later |
| Client FEN push | Poor | Unsafe | Reject |

### Appendix K — Illegal move response philosophy

Always help client resync:

```text
return authoritative {seq, fen, clocks, status, turn}
plus error.code
```

### Appendix L — Spectate API

```text
WS subscribe spectate:g_123
events: move, game_ended (may skip high-freq clock)
HTTP GET snapshot allowed if public
rate limit joins; coalesce under load
```

### Appendix M — Rating update visibility

```text
game_ended.reason = checkmate
rating_delta: {white: +8, black: -8} provisional
GET /users/{id} eventually consistent within seconds
```

### Appendix N — Cursor history

```text
GET /v1/users/u1/games?cursor=eyJ...&limit=20
response: { items: [...], next_cursor: "..." }
```

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| seq | Per-game monotonic event number |
| UCI | Universal Chess Interface move notation |
| Seek | Matchmaking request resource |
| Authority | Server component that serializes a game |
| Idempotency-Key | Client retry token |

### Appendix P — Worked flow timeline

```text
t0 POST /seeks
t1 WS game_matched
t2 GET /games/g (optional)
t3 WS subscribe since 0
t4 POST move e2e4 → seq=1
t5 opponent POST → seq=2
...
tn game_ended
```

### Appendix Q — Privacy

| Game | Listable | Spectate |
|------|----------|----------|
| public rated | yes | yes |
| private casual | participants | no |
| tournament | policy | policy |

### Appendix R — 30m checklist

1. Clarify rated/clocks/reconnect/spectate.  
2. Resource list + state machine.  
3. Move request/error shapes.  
4. WS seq + reconnect.  
5. Idempotency.  
6. Light infra backing.  
7. Versioning + deal-breakers.

### Appendix S — Sample resign

```http
POST /v1/games/g_123/resign HTTP/1.1
Authorization: Bearer ...
Idempotency-Key: resign-g_123-u1

→ 200 {"status":"ended","reason":"resignation","winner":"black","seq":41}
```

### Appendix T — Server validation checklist

```text
on move:
  authenticate
  authorize participant
  status == active
  turn matches
  clock not expired
  legal under ruleset
  apply
  persist
  seq++
  respond + publish
```

### Appendix U — Why API-first Meta interview

Meta often probes whether you can design **client-durable contracts** for interactive products. Chess is a crisp state machine to expose that skill.

### Appendix V — Deal-breaker card

| Fantasy | Reality |
|---------|---------|
| Trust client clock | Unfair flags |
| No move idempotency | Double moves on retry |
| WS-only without seq | Unrecoverable desync |
| Break fields casually | App crashes at scale |
| Spectate on write path | Player lag under viral game |

### Appendix W — Optional bot adapter

```text
Bot is a user with `bot` flag
Same move API
Server may grant slightly higher rate limits
Still server-validated
```

### Appendix X — CORS / mobile notes

```text
Mobile native: direct API
Web: strict CORS; WS tickets
Compact JSON; avoid huge move history on every tiny event
```

### Appendix Y — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Is game state linearizable? | Yes per game_id authority |
| Ratings globally strong? | No — eventual |
| Spectate same ms as player? | Not required |
| List history read-your-writes? | Aim yes in region |

### Appendix Z — Quick client algorithm

```text
on_event(e):
  if e.seq <= last: ignore
  if e.seq > last+1: resnapshot(); return
  apply(e); last=e.seq
on_http_error ILLEGAL_MOVE:
  replace_local_with(error.fen, error.clocks, error.seq)
```

---

*End of Online Chess API system design.*
