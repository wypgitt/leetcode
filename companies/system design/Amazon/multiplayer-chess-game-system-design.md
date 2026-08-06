# System Design: Multiplayer Chess (Amazon Interview)

> **Focus areas:** Matchmaking · Authoritative game server · Clocks · Reconnect · Anti-cheat hooks · Spectating · Concurrent games · Generalization to other multiplayer games  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split matchmaking vs move vs spectate load, explicit clock/game invariants, resolved authority ownership, honest anti-cheat scope

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

Goal: **bound a realtime rated multiplayer game**—fair matchmaking, server-authoritative rules/clocks, reconnect, spectating, anti-cheat telemetry—using **chess as the primary ruleset**, with explicit hooks to generalize (e.g. checkers, turn-based puzzles PvP, or light realtime games).

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who plays? | Casual + rated; guests optional | Accounts for rated; guest pool separate |
| F2 | Game modes? | Bullet/blitz/rapid (+ optional daily) | Queues + clock profiles per time control |
| F3 | Matchmaking? | Rating-based (ELO/Glicko); expand range over wait | MM service; atomic pair claim |
| F4 | Rules authority? | **Server validates all moves** | Authoritative engine; clients are views |
| F5 | Clocks? | Server-side; flag = loss | Never trust client clock |
| F6 | Draw / resign / abort? | Yes with explicit policies | Game event state machine |
| F7 | Reconnect? | Resume within timeout; clock policy stated | Snapshot + token; sticky game home |
| F8 | Spectating? | Live watch; viral matches possible | Fan-out **isolated** from authority |
| F9 | Anti-cheat? | Engine-detection hooks; reports | Async telemetry pipeline |
| F10 | Chat? | Thin optional; not critical path | Side channel + moderation hooks |
| F11 | Tournaments? | Phase 2 | Pairing service atop game core |
| F12 | Other games? | Design for **ruleset plugin** | `ruleset_id` + engine interface |

**MVP functional scope (lock with interviewer):**

1. Seek in a time-control queue → rating match → create game.  
2. Authoritative chess moves (checks, castling, en passant, promotion, draw claims).  
3. Server clocks + increment; flag; resign; draw offer; abort policy.  
4. WebSocket realtime; reconnect/resume with snapshot.  
5. Basic spectate for public games.  
6. Post-game rating update (ELO or Glicko-2) once.  
7. Anti-cheat: persist move times + positions; report button; offline analysis hooks.  
8. **Generalization:** `GameEngine` interface so another turn-based ruleset can plug in.

**Out of MVP (explicitly defer):**

- Full Swiss/Arena tournament product  
- Real-time inline engine bans each ply  
- Variant zoo (Crazyhouse, Chess960) unless asked—support via ruleset id  
- Perfect cheat-proofing  
- Authoritative lockstep FPS / fighting-game netcode (different genre)  
- Blockchain / NFT anything

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Move latency (opponent see) | Snappy | p50 < 100ms, p99 < 500ms in-region after accept |
| N2 | Clock fairness | Same rules both sides | Server SoT; skew ≪ increment |
| N3 | Durability | Accepted moves / results not lost | Persist before ACK (defend) |
| N4 | Availability | Play path critical | 99.9% games; degrade spectate/chat first |
| N5 | Consistency | Single authoritative state | Single-writer per `game_id` |
| N6 | Anti-cheat integrity | Tamper-evident move log | Immutable event log / PGN |
| N7 | Spectate scale | Viral game | Separate broadcast tier |
| N8 | Matchmaking UX | Bound wait vs fairness | Expand windows; show ETA |
| N9 | Operability | Own the pager | SLOs on move lag, MM wait, flag audits |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seek blitz 3+2 → match → moves → checkmate → ratings update.  
2. Draw offer → accept → draw → ratings.  
3. Disconnect → reconnect < 30s → snapshot → continue (clock ran).  
4. Spectator joins → snapshot + move stream.  
5. Abort in window → no rating change.  
6. (Generalization) Same seek/match/move protocol with `ruleset=checkers`.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double move click | Idempotency on `move_id` / ply |
| Illegal move | Reject; clock keeps ticking |
| Both disconnect | Clock continues; flag or abandon policy |
| Triple match race | Atomic dequeue; one game only |
| Move vs flag “tie” | Server_ts rule (normative) |
| Threefold / 50-move | Server verifies claim |
| Engine assistance | Async fair-play score → review |
| 100K spectators | Hot-game broadcast path |
| Rating farming | Rate limits; multi-account hooks |
| Premoves | Client UX; server accepts only on turn |
| Shard kill mid-game | Reload state; clients resync |
| Wrong ruleset version | Pin `ruleset_version` on game create |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 1M | 10M | 100M | 1B |
| DAU | 200K | 2M | 20M | 200M |
| Peak concurrent players in game | 50K | 500K | 5M | 50M |
| Peak concurrent **games** | 25K | 250K | 2.5M | 25M |
| Seek / MM ops/s | ~200 | ~2K | ~20K | ~200K |
| Moves /s (peak) | ~5K | ~50K | ~500K | ~5M |
| Spectate events /s (blended) | ~20K | ~200K | ~2M | ~20M+ |
| Games finished / day | 5M | 50M | 500M | 5B |
| Avg plies / game | ~60 | ~60 | ~60 | ~60 |
| Rating updates / day | ~10M | ~100M | ~1B | ~10B |

**What each jump forces:**

- **10×:** Sticky game shards by `game_id`; Redis active state; Kafka fair-play/analytics.  
- **100×:** MM partitioned by rating bands + TC; spectate relay; regional cells.  
- **1,000×:** Edge WS gateways; game home cells; approximate leaderboards; fair-play offline fleet as its own platform.

### 1.5 Etc. (Constraints & Assumptions)

- Primary rules: FIDE-like online chess adaptations.  
- Clients: web + mobile; one realtime protocol family (WS).  
- Rated requires login; clocks always server-side.  
- Amazon bar: **operational metrics**, failure modes, cost/efficiency of spectate fan-out—not only “use Kafka.”

**Scope statement:**

> Design a multiplayer chess platform for an Amazon SDE III interview: rating matchmaking, authoritative game+clock shards, reconnect, draw/resign/abort, spectate isolation, anti-cheat telemetry, and a ruleset interface for other turn-based games—from ~25K concurrent games through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **MM seek/cancel** | Queue ops | ~200/s | ~200K/s | MM + Redis |
| **Move submits** | Player moves | ~5K/s | ~5M/s | Game shards |
| **Clock wakeups** | Next-flag heap | ≪ games (not global tick) | local per shard | Game servers |
| **Player push** | Opponent events | ~5K/s | ~5M/s | WS gateway |
| **Spectate fan-out** | Broadcast | ~20K/s | ~20M+/s | Relay / CDN-ish |
| **Rating writes** | Post-game | ~100/s avg | ~10K/s avg | Rating DB |
| **Fair-play ingest** | Move features | ~5K/s | ~5M/s | Kafka |

**Anti-pattern:** one QPS mixing seeks, moves, and spectator amplification.

### 2.2 Concurrent games memory

```text
Active game state: ~2–5 KB (position, clocks, meta)
25K games × 5 KB = 125 MB
25M games × 5 KB = 125 GB fleet-wide  ← shard; not one node
```

### 2.3 Move bandwidth

```text
Move event ~200 B
5K moves/s × 200 B ≈ 1 MB/s (players)
Avg 4 spectators → ~5 MB/s baseline
Viral 100K spectators × ~1 move/s ≈ 100K events/s on one game → special path
```

### 2.4 Matchmaking queue size

```text
Seeker record ~100 B
50K waiting × 100 B = 5 MB — tiny
Hot path correctness: atomic pair claim
```

### 2.5 Finished game storage

```text
PGN / move log ~1–3 KB / game
5M games/day × 2 KB ≈ 10 GB/day
1,000× → ~10 TB/day → object storage + cold tier
```

### 2.6 Clock tick myth (efficiency / Amazon frugality)

```text
Do NOT wake every game every 100ms via Redis globally.
Per shard: min-heap / timer wheel of next flag deadline only.
Wake on deadline or on move.
```

### 2.7 Generalization load note

```text
Turn-based games ≈ same planes (MM, authority, spectate).
High-frequency realtime (10–60 Hz state) changes estimate class:
  state sync bandwidth dominates; often UDP + rollback — call out as different design.
```

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
+------------------------------------------------------------------+
| Chess (Amazon interview)   Blitz 3+2   Rating 1624   [Seek]      |
+-------------------+----------------------------------------------+
| Play              |     [Board 8x8]          Clocks              |
|  Seek / Challenge |   r n b q k b n r       White  1:42          |
|  In progress      |   p p p p p p p p       Black  1:55          |
| Spectate          |   Moves: 1.e4 e5 ...                         |
| Fair Play         |   [Resign] [Offer draw]                      |
+-------------------+----------------------------------------------+
```

### 3.2 Domain model

```text
User
 ├── Rating[time_control, ruleset]
 └── Preferences (region, rated default)

Seek
 └── queue_key (tc, rated, ruleset, region_pref?), rating, range, enqueued_at

Game
 ├── game_id, white_id, black_id, tc, rated, ruleset_id, ruleset_version
 ├── status: active|aborted|mate|resign|timeout|draw|stalemate|...
 ├── position (FEN or ruleset-specific blob)
 ├── clocks_ms {white, black}, last_stamp_server
 ├── draw_offer_from?
 ├── move_list[] / ply
 └── version / ply_seq (CAS)
```

**Ownership (resolved):**

| Concern | SoT |
|---------|-----|
| Legal position & move acceptance | **Game authority shard** |
| Clocks | **Game authority** (`server_ts`) |
| Matchmaking pairing | **MM service** atomic ops |
| Ratings | **Rating service** after terminal game |
| Spectators | Ephemeral pub/sub; not on critical path |
| Fair-play scores | Async analysis pipeline |
| Rules semantics | Versioned **engine** library on authority |

**Deal-breakers:** client-authoritative legality/clocks; multi-writer game state; spectate sockets inside authority process at viral scale.

### 3.3 Matchmaking (ELO / Glicko)

**Queue key:** `(time_control, rated, ruleset, region_pref?)`

**Algorithm (progressive expand):**

```text
on_seek(user, rating):
  enqueue(user)
  loop:
    candidates = nearby(rating ± window(t))
    if opponent = best_match(candidates):
      if atomic_claim(user, opponent): create_game(); return
    widen window every few seconds
    timeout → suggest bot / cancel
```

| Rating system | Pros | Cons |
|---------------|------|------|
| **ELO** | Simple | Weak uncertainty model |
| **Glicko-2 (preferred)** | RD helps new players | Slightly more state |
| TrueSkill | Teams | Overkill for 1v1 MVP |

**Atomic match (critical):**

```text
Redis Lua:
  remove both if still present → return pair else fail
DB: insert game uniquely; losers requeue
```

**Amazon efficiency note:** bucket queues by rating bands to avoid O(n) scans; cross-band only when expanding.

### 3.4 Authoritative game server

```text
Client --move--> WS GW --> Game Service (shard by game_id)
  1. load state (memory/Redis)
  2. check side_to_move, status active
  3. apply clock until now (server)
  4. if flagged → terminal timeout
  5. engine.validate_and_apply(move)
  6. update position, clocks, ply_seq
  7. persist (Redis + append log)
  8. ACK mover; publish opponent + spectate bus
```

**Chess engine must handle:** pins, castling, en passant, promotion, mate/stalemate, threefold/50-move/insufficient material.

### 3.5 Ruleset plugin (generalization)

```text
interface GameEngine {
  initial_position(config) -> State
  validate_apply(state, move, meta) -> Result{state', events, terminal?}
  claim_draw(state, claim_type) -> bool
  serialize(state) -> bytes  // FEN or custom
}
```

| Game type | Fits this design? | Notes |
|-----------|-------------------|-------|
| Chess / Checkers / Go (turn-based) | **Yes** | Swap engine; clocks similar |
| Correspondence | **Yes** | Persist deadlines; sweeper not hot heap |
| Card duel turn-based | **Mostly** | Hidden info → per-player views; authority still |
| Poker | **Partial** | Pots/betting SM; anti-cheat different |
| 60 Hz action game | **No (MVP)** | Different netcode (UDP, rollback) |

**Interview move:** lead with chess; show `GameEngine` to signal extensibility without boiling the ocean.

### 3.6 Chess clocks (server-side)

```text
On move accept at server_ts T:
  elapsed = T - last_stamp
  clock[side_to_move] -= elapsed
  if clock[side] <= 0: FLAG
  else:
    clock[side] += increment
    switch side
    last_stamp = T
```

**Flag vs move race (normative):**

> Timestamp move at authority receive. If `receive_ts > flag_deadline` → timeout loss. If `≤` → accept, then increment. Deterministic under replay.

**Timer wheel:** per shard min-heap of `next_flag_at`.

### 3.7 Reconnect / resume

```text
Client stores game_id + reconnect_token
On reconnect:
  auth → snapshot {position, clocks_now, ply_seq, moves_hash}
  resubscribe WS topic game:{id}:players
  if terminal → show result
```

**Clock during disconnect:** continues for blitz/rapid (standard). Optional pause modes are product exceptions.

**Grace:** both absent N minutes in long TC → abort/abandon policy.

### 3.8 Draw, resign, abort

| Action | Rules |
|--------|-------|
| Resign | Active player → opponent wins |
| Draw offer | Set offer; accept/decline; often clears on next move |
| Abort | Early plies + little time; unrated |
| Takeback | Off for rated |

### 3.9 Spectating fan-out

| Approach | Pros | Cons |
|----------|------|------|
| Push from game shard to all spectators | Simple | Melts on viral games |
| Pub/sub per game | Decouples | Still hot |
| **Hybrid (chosen)** | Players direct; spectators via relay | Extra component |

```text
Game shard --move_event--> Spectate Relay
  ├── small: Redis Pub/Sub
  └── hot: dedicated broadcaster (+ snapshot stream)
```

**Deal-breaker:** 100K spectator sockets inside authoritative process.

### 3.10 Anti-cheat hooks

```text
FairPlayEvent per move:
  game_id, ply, fen_before, uci, think_time_ms,
  client_ip_hash, device_fp, rating, ruleset
Async:
  engine match %, CPL estimates, anomalies, multi-account
Outcomes: shadow flag → review → restrictions
```

**Not on hot path:** blocking Stockfish before ACK.

### 3.11 Tournaments (optional sketch)

- Arena: continuous pairings from scores.  
- Swiss: round batch pairings.  
- Reuse Game service; `tournament_id` + pairing service.  
- Isolate tournament MM pools from ladder.

### 3.12 API / protocol

**HTTP:** seek, cancel, get game, ratings, report.

**WS:**

```text
C→S: move {game_id, ply, payload, move_id}
C→S: resign | draw_offer | draw_accept | abort
S→C: game_state | move_accepted | move_rejected | game_over
S→C: spectate_move
```

**Idempotency:** `(game_id, move_id)` unique.

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +----------------+     +------------------+
| Web/Mobile  |---->| Edge WS / HTTP |---->| API / Seek       |
+-------------+     +--------+-------+     +--------+---------+
                             |                      |
                             |                      v
                             |               +------+-------+
                             |               | Matchmaking  |
                             |               | (queues)     |
                             |               +------+-------+
                             |                      |
                             v                      v
                      +------+----------------------+
                      | Game Authority Shards       |
                      | (engine, clocks, state)     |
                      +------+------------+---------+
                             |            |
              +--------------+            +----------------+
              v                               v
     +----------------+                +----------------+
     | Redis Active   |                | Move Log / DB  |
     | Game State     |                | + Object PGN  |
     +----------------+                +--------+-------+
                                               |
              +--------------------------------+----------------+
              v                                v                v
     +----------------+                +--------------+  +--------------+
     | Spectate Relay |                | Rating Svc   |  | FairPlay Bus |
     +--------+-------+                +--------------+  +--------------+
              v
     +----------------+
     | Spectator GWs  |
     +----------------+
```

### 4.2 Match → first move

```text
UserA                MM                   GameShard              UserB
 |--seek------------>|                      |                     |
 |                   |<------seek-----------|---------------------|
 |                   |--Lua match A,B------>|                     |
 |                   |--CreateGame--------->|                     |
 |<----game_start----|<---------------------|----game_start------>|
 |--move e2e4------->|--------------------->|                     |
 |                   |                      |--validate+clock---->|
 |<--ack-------------|                      |--push move--------->|
```

### 4.3 Reconnect

```text
Client-->API: GET /games/{id}/snapshot
Client-->WS: subscribe(game_id, token)
WS-->GameShard: attach connection
GameShard-->Client: snapshot + catchup from ply_seq
```

### 4.4 Hot spectate

```text
Authority --event--> HotBroadcaster --coalesced--> Spectator GW farm
New spectator: REST snapshot + subscribe broadcast topic
Authority CPU: 2 players + 1 publish (not N sockets)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Single-writer authority per `game_id`** (shard owner + fencing).  
2. **Server clock SoT**; client clocks cosmetic.  
3. **Move ACK ⇒ durable** in active store + append log.  
4. **CAS on `ply_seq`** — no silent overwrite.  
5. **Matchmaking atomic claim** — no triple pairing.  
6. **Terminal state once** — CAS; ratings exactly once per `game_id`.  
7. **Spectate failure must not block players.**  
8. **Fair-play async** — must not add move RTT.  
9. **Ruleset version pinned** at game create for replay.  
10. **Flag/move ordering** documented and replay-safe.

**Amazon ownership signal:** page on `move_ack_p99`, `mm_double_match_count=0`, `rating_applied` lag, `spectate_lag` (soft), `fairplay_backlog`.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Monolith: MM + Game + WS; Redis; Postgres |
| 10× | Shard by `hash(game_id)`; Kafka fair-play; spectate pub/sub |
| 100× | Regional cells; hot-game broadcasters; rating CQRS; banded MM |
| 1,000× | Edge WS; PGN lake; fair-play fleet; approx leaderboards |

**Sticky routing:** `game_id → shard` via consistent hash + ownership directory; WS GW resolves home.

**MM scale:** rating-band partitions + Lua atomicity inside band coordinator; expand across bands carefully.

### 5.3 Maintainability

- Engine versioned; PGN fixture regression suite.  
- Clock property tests (flag boundaries).  
- Chaos: kill shard mid-blitz → reload + reconnect storm test.  
- Metrics without per-game Prometheus label cardinality explosion.  
- Feature flags: pause-on-disconnect modes, auto-draw policies.

### 5.4 Rating updates

```text
on_terminal(game):
  if not rated or abort: skip
  rating_svc.apply(result, tc, ruleset)  # idempotent on game_id
```

**Ordering:** per-user serialization or atomic compare to avoid lost updates under concurrent game ends.

### 5.5 Cheating prevention (honest scope)

| Layer | What |
|-------|------|
| Product | Limit analysis during live rated |
| Telemetry | Think time vs complexity; engine match offline |
| Accounts | Multi-account / farm detection |
| Reports | Human review for high suspicion |
| Sanctions | Shadow → ranked restriction |

**Cannot promise:** zero cheating. Promise: detection hooks + auditability + ops review queue.

### 5.6 Consistency & replay

Append-only moves:

```text
{ply, payload, server_ts, clock_white_after, clock_black_after, hash}
```

Rebuild position by replay for audits; hot path keeps current position.

### 5.7 Efficiency (Amazon theme)

- Timer wheel ≫ per-game threads.  
- Spectate coalescing (10–20 Hz UI) for hot games.  
- Don’t store full spectator lists on authority.  
- Cold PGN in object storage; hot metadata in DB.  
- Batch fair-play feature extraction.

### 5.8 Regional cells & RTT

Prefer matchmaking within region for UX lag. Clocks remain fair (server), but move RTT suffers cross-region—show tradeoff table in interview.

| Choice | Pros | Cons |
|--------|------|------|
| Strict regional MM | Better UX | Longer waits |
| Global MM | Faster match | Laggy play |
| **Regional prefer + expand (chosen)** | Balance | More MM logic |

---

## 6. Wrap-Up

### 6.1 What we designed

A **multiplayer chess** system (Amazon interview framing) with Glicko/ELO matchmaking, **authoritative** game+clock shards, reconnect snapshots, draw/resign/abort, hybrid spectate fan-out, async fair-play telemetry, and a **ruleset engine interface** for other turn-based games—scaled by sharding `game_id` and isolating spectator storms.

### 6.2 Key decisions worth defending

1. **Server validates moves + clocks** — clients untrusted.  
2. **Atomic matchmaking claims** — no triple games.  
3. **Single-writer game shard** with `ply_seq` CAS.  
4. **Timer wheel per shard**, not global tick storm.  
5. **Spectate ≠ player path.**  
6. **ACK after durable move.**  
7. **Ratings once per terminal `game_id`.**  
8. **Anti-cheat async.**  
9. **Split load classes** in estimates.  
10. **Honest cheat impossibility** + strong audit logs.  
11. **`GameEngine` plugin** for generalization without FPS netcode cosplay.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Shard failover mid-blitz | Fast reload + reconnect tests |
| Viral spectate | Hot-game detector + broadcasters |
| Fair-play false positives | Human review; RD-aware |
| MM wait too long | Bots / wider range / pool merge |
| Clock disputes | Immutable `server_ts` logs |
| Engine upgrade bugs | Shadow replay + version pin |

### 6.4 How to present in 45 minutes

1. Requirements + authority model (6 min)  
2. Numbers with split classes (4 min)  
3. Matchmaking atomicity (7 min)  
4. Move+clock sequence (10 min)  
5. Reconnect + spectate + anti-cheat (8 min)  
6. Scale + generalization note (5 min)  
7. Q&A (remaining)

---

## 7. Deeper / Related Interview Questions

### 7.1 Matchmaking

**Q: ELO vs Glicko-2?**  
A: Glicko-2 models uncertainty (RD)—better for new players. ELO simpler. Either fine if consistent per TC/ruleset.

**Q: How avoid matching the same two smurfs always?**  
A: Recent-opponent cooldown; IP/device soft signals; not only rating.

**Q: Queue scan complexity?**  
A: Bucket by rating; expand bands; don’t O(n) scan millions globally every seek.

**Q: Regional matchmaking?**  
A: Prefer low RTT pools; cross-region if wait high—clock fair, lag UX suffers.

**Q: How do you prevent double-match under Redis failover?**  
A: Fencing tokens; prefer under-match; game create uniqueness in DB as backstop.

### 7.2 Rules & state

**Q: Where does the rules engine run?**  
A: On authoritative game service; never trust client legality.

**Q: How to handle promotion UI races?**  
A: Move includes promotion piece; reject incomplete.

**Q: Threefold detection cost?**  
A: Maintain position hash history; claim or auto policy.

**Q: Why `ply_seq`?**  
A: Idempotency + reject stale; concurrent tabs.

**Q: How do you upgrade the engine safely?**  
A: Pin `ruleset_version` on create; dual-run replay diffs offline before default switch.

### 7.3 Clocks

**Q: Why not client clock with server sync?**  
A: Cheating/pause; use `server_ts` elapsed.

**Q: Increment before or after flag check?**  
A: Check flag on elapsed before increment; then add increment—state it.

**Q: Timer wheel vs per-game sleep threads?**  
A: Heap/timer wheel; threads-per-game won’t scale (efficiency).

**Q: Correspondence (days) clocks?**  
A: Persist deadlines in DB; sweeper; not hot memory heap for all.

**Q: DST / NTP jumps?**  
A: Monotonic clock source for deadlines where possible; store absolutes carefully.

### 7.4 Reconnect & networking

**Q: Does disconnect pause clock?**  
A: Usually no for blitz/rapid; rare product modes yes.

**Q: Snapshot vs replay all moves?**  
A: Snapshot position+clocks + recent moves; full PGN on demand.

**Q: WS vs SSE?**  
A: WS bidirectional for moves; SSE awkward for client moves.

**Q: Mobile backgrounding?**  
A: Reconnect token; expect clock ran; show accurate remaining on resume.

### 7.5 Spectating

**Q: 100K spectators on one game?**  
A: Detect hot game; dedicated broadcast tier; snapshots + delta; don’t run inside authority.

**Q: Spectator lag SLO?**  
A: Weaker than player path; batch 50–100ms OK.

**Q: Privacy?**  
A: Public by default optional; private challenges no spectate.

**Q: Cost control?**  
A: Coalesce updates; unsubscribe idle; CDN-like snapshot for huge audiences.

### 7.6 Anti-cheat

**Q: Can you detect engines in real time?**  
A: Weakly; strong signals need full-game stats. Don’t block moves on engine each ply in MVP.

**Q: What features matter?**  
A: Think-time vs complexity, match to engine top choices, accuracy outliers vs rating, multi-accounting.

**Q: False positives?**  
A: Review queues; temporary longer-TC-only; human appeals.

**Q: Can clients forge think times?**  
A: Server computes think time from receive timestamps; client fields advisory only.

### 7.7 Ratings & storage

**Q: Lost rating update?**  
A: Idempotent `rating_applied` on game; outbox; sweeper.

**Q: Where store PGNs?**  
A: Object storage; DB metadata + result; hot recent optional.

**Q: Leaderboards at 1,000×?**  
A: Approximate / tiered; cache; not raw `ORDER BY` on OLTP each page.

### 7.8 Failure injection

1. Game shard kill → reload state; clients reconnect.  
2. Redis loss → fail closed new moves if state there; recover from append log if dual-written.  
3. MM Redis split → fencing; prefer under-match vs double-match.  
4. Spectate Kafka/relay down → players unaffected.  
5. Fair-play lag → backlog; no move latency impact.  
6. Clock heap storm after time bug → monotonic server time.  
7. Duplicate `game_over` → CAS terminal + idempotent ratings.  
8. Poison PGN replay → isolate rules version.  
9. Botnet seeks → rate limit / captcha / account age.  
10. Hot celebrity match → autoscale broadcast, not authority CPU for sockets.

### 7.9 Tournaments

**Q: How do Swiss pairings interact with game service?**  
A: Pairing batch creates challenges; games normal; standings consume results async.

**Q: Arena pairing storms?**  
A: Dedicated MM pool per `tournament_id`.

### 7.10 Generalization traps

**Q: Is this just multiplayer networking?**  
A: Authority, clocks, ratings, fair-play, and spectate isolation dominate.

**Q: Why not CRDTs for the board?**  
A: Rated clocks need single authority—CRDT wrong model.

**Q: Same as online poker?**  
A: Similar authority ideas; poker adds hidden info, betting pots, different collusion.

**Q: Same as FPS?**  
A: No—tickrate, prediction/rollback, lag compensation differ; don’t force chess design onto Quake.

**Q: How much to design for “any game”?**  
A: Show `GameEngine` + shared MM/WS/spectate; deep-dive one ruleset (chess).

### 7.11 Amazon Leadership-flavored probes

**Q: Customer Obsession — lag vs fair ratings?**  
A: Prefer regional match quality; expand range only as wait grows; show ETA.

**Q: Ownership — who pages on wrong flag?**  
A: Game authority team; clock audit from move log; replay tool.

**Q: Frugality — spectate cost?**  
A: Hybrid fan-out + coalesce; don’t hold 100K sockets on game hosts.

**Q: Dive Deep — prove no double match?**  
A: Lua claim + unique game participants constraint + metric.

**Q: Bias for Action — MVP cut?**  
A: Ship ladder chess + reconnect + basic spectate; tournaments later.

### 7.12 Extra interviewer traps (high value)

- Who wins if move and flag are “simultaneous”?  
- What is durable before the opponent sees the move?  
- How do you prevent matching three players?  
- Why not tick every clock in Redis every 100ms?  
- How do spectators avoid melting the game shard?  
- Does anti-cheat run inline with move validation?  
- How do you resume after mobile backgrounding?  
- Abort vs resign vs timeout — rating impacts?  
- How is draw offer cleared?  
- How do you shard so both players hit the same authority?  
- What if rating service is down at game end?  
- How do you test rules engine upgrades?  
- Premoves: client-only or server queue?  
- How do you handle 25M concurrent games memory-wise?  
- What’s the deal-breaker in client-authoritative chess?  
- How does `ruleset_version` prevent replay ambiguity?  
- When do you refuse to reuse this design (FPS)?

### 7.13 Progressive scale Q&A

**Q: Baseline monolith OK?**  
A: Yes with clear module boundaries and Redis state.

**Q: 10× first splits?**  
A: Game shards + Kafka fair-play + spectate pub/sub.

**Q: 100×?**  
A: Regional cells; hot broadcasters; banded MM.

**Q: 1,000×?**  
A: Edge WS; PGN lake; fair-play fleet; approx leaderboards; cell blast radius.

---

## 8. Appendices

## Appendix A — Example schemas

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  handle TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ratings (
  user_id UUID NOT NULL,
  ruleset TEXT NOT NULL DEFAULT 'chess',
  time_control TEXT NOT NULL, -- bullet|blitz|rapid|classical
  rating DOUBLE PRECISION NOT NULL,
  rd DOUBLE PRECISION NOT NULL,
  volatility DOUBLE PRECISION NOT NULL,
  games_count INT NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, ruleset, time_control)
);

CREATE TABLE games (
  id UUID PRIMARY KEY,
  white_id UUID NOT NULL,
  black_id UUID NOT NULL,
  ruleset TEXT NOT NULL,
  ruleset_version TEXT NOT NULL,
  time_control TEXT NOT NULL,
  rated BOOLEAN NOT NULL,
  status TEXT NOT NULL,
  result TEXT, -- 1-0|0-1|1/2-1/2|*
  pgn_uri TEXT,
  rating_applied BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ
);

CREATE TABLE moves (
  game_id UUID NOT NULL,
  ply INT NOT NULL,
  move_id UUID NOT NULL,
  uci TEXT NOT NULL,
  server_ts TIMESTAMPTZ NOT NULL,
  clock_white_ms INT NOT NULL,
  clock_black_ms INT NOT NULL,
  fen_after TEXT NOT NULL,
  PRIMARY KEY (game_id, ply),
  UNIQUE (game_id, move_id)
);

CREATE TABLE fairplay_reports (
  id UUID PRIMARY KEY,
  game_id UUID NOT NULL,
  reporter_id UUID NOT NULL,
  suspect_id UUID NOT NULL,
  reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Auth game+clock, MM queues, WS, Redis state, ratings, reconnect snapshot |
| 10× | Game shards, Kafka fair-play, spectate pub/sub, move idempotency |
| 100× | Regional cells, hot-game broadcasters, rating CQRS, banded MM |
| 1,000× | Edge WS, PGN lake, fair-play fleet, approx leaderboards |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| Authority shard | Single-writer game process/owner |
| TC | Time control (e.g. 3+2) |
| Ply | Half-move |
| Glicko RD | Rating deviation / uncertainty |
| Flag | Clock hit zero |
| Abort | Early no-rating end |
| FairPlay event | Telemetry for engine detection |
| Spectate relay | Fan-out path isolated from authority |
| Ruleset | Pluggable game logic (chess, checkers, …) |
| Hot game | Spectator count exceeds broadcast threshold |

## Appendix D — Estimation cheat-sheet

```text
games ≈ players_in_game / 2
move_QPS ≈ games × moves_per_sec_avg (blitz higher)
spectate_QPS ≈ move_QPS × avg_spectators (heavy tail!)

Do not global-tick clocks:
  wakes ≈ games near flag + on moves

Storage/day ≈ games/day × KB/game
```

## Appendix E — Clock & flag worked example

```text
Time control: 3+2 (180_000 ms + 2_000 ms increment)
White clock = 180000, Black = 180000, side = White, last_stamp = T0

White moves at T0+1500ms (server receive):
  elapsed = 1500
  white = 180000 - 1500 = 178500
  white += 2000 → 180500
  side = Black; last_stamp = T0+1500

Black disconnects; no move; heap wakes at last_stamp + black_clock:
  flag_at = (T0+1500) + 180000
  On wake: if still Black to move and no legal move accepted → Black timeout → 1-0
```

**Move vs flag race rule (normative):**

> Compare `move.server_receive_ts` to authority `flag_deadline`. If `>` → timeout loss for side-to-move. If `≤` → accept move, then apply increment. Deterministic under replay.

## Appendix F — Matchmaking expand schedule

| Wait (s) | Rating window (±) | Notes |
|----------|-------------------|-------|
| 0–3 | 50 (or 0.5×RD) | Prefer close |
| 3–8 | 100 | |
| 8–15 | 200 | |
| 15–30 | 400 | Show “expanding…” |
| 30+ | 600+ or bot offer | Product choice |

Glicko: scale window by RD so provisional accounts match faster without wrecking established ratings.

## Appendix G — Anti-cheat feature vector (async)

```text
per move:
  think_time_ms, legal_move_count, engine_match_top1/top3,
  cpl_loss_estimate, rating, tc_class, phase (opening/mid/end)
per game aggregate:
  avg_match%, move_time_uniformity, accuracy_vs_peers,
  multi_account_risk_score
```

Pipeline: Kafka → feature workers → offline engine ensemble → risk score → review queue. **Not** on move ACK path.

## Appendix H — Spectator hot-game playbook

1. Metrics: subscribers per `game_id` exceed threshold (e.g. 5K).  
2. Mark game `hot`; authority publishes to dedicated broadcaster topic only.  
3. Broadcaster coalesces board updates (e.g. 10–20 Hz max for UI).  
4. New spectators get snapshot REST + subscribe to broadcast.  
5. Authority CPU stays bound to 2 player connections + 1 publish.

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Illegal move | Reject; clocks keep running |
| Duplicate `move_id` | Same accepted move returned |
| Triple match race | Only one game; losers requeued |
| Shard kill | Reload position/clocks; clients snapshot |
| Double `game_over` | Ratings applied once |
| Spectate relay down | Players unaffected |
| Claim threefold wrongly | Reject claim |
| Abort window exceeded | Abort rejected; must resign/play |
| Engine version pin | Replay with create-time version |
| Fair-play worker down | Moves still ACK; backlog grows |

## Appendix J — GameEngine interface sketch

```text
EngineRegistry:
  chess@1.4.0 -> ChessEngineV1_4
  checkers@0.9 -> CheckersEngineV0_9

CreateGame(ruleset, version, tc, players):
  engine = Registry.get(ruleset, version)
  state = engine.initial_position(tc.config)
  persist Game{ruleset, version, state...}

OnMove:
  engine = Registry.get(game.ruleset, game.ruleset_version)
  result = engine.validate_apply(...)
```

## Appendix K — Generalization decision matrix

| Requirement | Chess design reuse | Change |
|-------------|-------------------|--------|
| Rated 1v1 turn-based | High | Engine only |
| Hidden information | Medium | Per-player projections |
| >2 players | Medium | MM + state seats |
| Simultaneous turns | Medium | Turn model |
| Realtime physics 60 Hz | Low | Different transport & reconciliation |
| Team modes | Medium | Rating model (TrueSkill) |

## Appendix L — Amazon ops dashboard (interview gold)

| Panel | Alert idea |
|-------|------------|
| Move ACK p50/p99 | p99 > 500ms in-region |
| MM wait p50/p99 | wait explosion |
| Double-match counter | any > 0 |
| Active games vs shard memory | capacity |
| Hot games count | broadcast scaling |
| Fair-play lag | backlog hours |
| Rating applied lag | sweeper health |
| Illegal move rate | client bug or attack |
| Reconnect success rate | mobile UX |

## Appendix M — 45-minute whiteboard order

1. FR/NFR + authority (who validates?).  
2. Split QPS table.  
3. MM Lua atomicity.  
4. Move pipeline + clock math + flag race.  
5. Reconnect snapshot.  
6. Spectate hybrid.  
7. Anti-cheat async.  
8. 10×/100×/1,000× checklist.  
9. One generalization sentence (`GameEngine`).  
10. Invariants + pager metrics.

---

*End of design doc. Open with §1 authority + clocks; whiteboard §3.3–3.6 matchmaking/moves/clocks; close with invariants in §5.1 and traps in §7.12. Mention generalization via Appendix J without derailing into FPS netcode.*
