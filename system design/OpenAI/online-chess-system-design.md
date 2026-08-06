# System Design: Online Chess

> **Focus areas:** Matchmaking (ELO/Glicko) · Authoritative game server · Rules validation · Clocks · Reconnect · Anti-cheat hooks · Spectating · Concurrent games  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split matchmaking vs move vs spectate load, explicit clock/game invariants, resolved authority ownership

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

Goal: **bound the product**—realtime rated chess with fair matchmaking, server-authoritative rules/clocks, reconnect, and anti-cheat hooks—not a generic chat app with a board skin.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who plays? | Casual + rated players; guests optional | Accounts for rated; guest pool separate |
| F2 | Game modes? | Rapid/blitz/bullet + optional daily correspondence | Different clock & matchmaking queues per time control |
| F3 | Matchmaking? | Rating-based (ELO or Glicko-2); expand rating range over time | Queue service + rating SoT; not random only |
| F4 | Rules authority? | **Server validates all moves** | Authoritative game engine service; clients are views |
| F5 | Clocks? | Server-side chess clocks; flag falls end game | Never trust client clock; server timestamps |
| F6 | Draw / resign / abort? | Resign, draw offer/accept, abort rules (e.g. early + little play) | Explicit game events in state machine |
| F7 | Reconnect? | Resume same game after disconnect within timeout | Sticky game state; reconnect token; clock keeps running (policy) |
| F8 | Spectating? | Watch live games; optional broadcast big matches | Fan-out path separate from player move path |
| F9 | Anti-cheat? | Engine-detection hooks; fair play reviews | Move telemetry → analysis pipeline; not only client trust |
| F10 | Chat? | Optional premove chat; keep thin in MVP | Side channel; moderate; not on critical move path |
| F11 | Tournaments? | Phase 2 / optional | Arena/swiss services on top of game core |
| F12 | Puzzles / bots? | Out of MVP or thin bot adapter | Same move API; bot as special player |

**MVP functional scope (lock with interviewer):**

1. Seek game in a time-control queue → match by rating → create game.
2. Authoritative moves (chess rules: checks, castling, en passant, promotion, repetition/50-move claims).
3. Server clocks with increment; flag → loss; draw offers; resign; abort policy.
4. WebSocket (or similar) realtime; reconnect/resume.
5. Basic spectate for public games.
6. Rating update after rated games (ELO or Glicko-2).
7. Anti-cheat: persist move times + positions for offline analysis; report button.

**Out of MVP (explicitly defer):**

- Full tournament platform (Swiss pairing UI)
- Perfect real-time engine bans (async review OK)
- 3D boards / mobile offline play sync
- Variant chess (Crazyhouse etc.) unless asked—design hooks via ruleset id
- Perfect cheat-proofing against all engine users

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Move latency (opponent see)? | Snappy | p50 < 100ms, p99 < 500ms in-region after accept |
| N2 | Clock fairness? | Same rules for both | Server SoT; max clock skew error ≪ increment |
| N3 | Durability? | Finished games never lost | Persist moves before ACK to mover (or before broadcast—pick & defend) |
| N4 | Availability? | Matchmaking + games critical | 99.9% control; degrade spectate/chat first |
| N5 | Consistency? | Single authoritative game state | Single-writer per `game_id` |
| N6 | Anti-cheat integrity? | Tamper-evident move log | Signed server events; immutable PGN store |
| N7 | Scale spectate? | Viral game | Separate fan-out; don’t block players |
| N8 | Fair matchmaking wait? | Trade wait vs rating distance | Expand windows; show expected wait |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Seek blitz 3+2 → match ~equal rating → game start → moves → checkmate → ratings update.
2. Draw offer → opponent accepts → draw → ratings.
3. Player disconnects → reconnect within 30s → state sync → continue (clock ran).
4. Spectator joins popular game → receives snapshots + move stream.
5. Abort within allowed window → no rating change (policy).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double move click | Idempotency on `move_id` / ply; reject illegal |
| Client sends illegal move | Reject; clock still ticks (no free pause) |
| Both disconnect | Clock continues; flag or abort policy |
| Matchmaking race (triple match) | Atomic dequeue; only one game created |
| Clock flag near last move | Server order: validate move vs flag using server_ts — define rule |
| Threefold / 50-move claim | Server verifies claim; auto-draw optional policy |
| Engine-assisted play | Async fair-play score; provisional restrictions |
| Spectator storm (100K) | Hybrid fan-out / CDN-ish snapshot; not 100K writes to game shard |
| Rating windmill farming | Rate limits; dual accounts detection hooks |
| Premoves | Client UX; server only accepts when it’s their turn |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 1M | 10M | 100M | 1B |
| DAU | 200K | 2M | 20M | 200M |
| Peak concurrent players in game | 50K | 500K | 5M | 50M |
| Peak concurrent **games** | 25K | 250K | 2.5M | 25M |
| Seek / matchmaking ops/s | ~200 | ~2K | ~20K | ~200K |
| Moves /s (peak) | ~5K | ~50K | ~500K | ~5M |
| Spectate events /s (blended) | ~20K | ~200K | ~2M | ~20M+ |
| Games finished / day | 5M | 50M | 500M | 5B |
| Avg plies / game | ~60 | ~60 | ~60 | ~60 |
| Rating updates / day | ~10M | ~100M | ~1B | ~10B |

**What each jump forces:**

- **10×:** Sticky game servers / shards by `game_id`; Redis for active games; Kafka for analytics/anti-cheat.
- **100×:** Matchmaking partitioned by rating bands + time control; spectate pipeline separate; cell by region.
- **1,000×:** Edge WS gateways; game home cells; approximate spectate; fair-play offline fleet is its own platform.

### 1.5 Etc. (Constraints & Assumptions)

- Standard chess rules (FIDE-like online adaptations).
- Primary clients: web + mobile; one realtime protocol family.
- Rated games require login; clocks always server-side.
- Tournaments optional add-on—not required for MVP correctness.

**Scope statement:**

> Design an online chess platform: rating-based matchmaking, authoritative game+clock server, reconnect, draw/resign/abort, spectating fan-out, and anti-cheat telemetry—from ~25K concurrent games through 10× / 100× / 1,000× with sharded game authority and isolated spectate paths.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | 1,000× | Plane |
|-------|------|---------------|--------|-------|
| **Matchmaking seek/cancel** | Queue ops | ~200/s | ~200K/s | MM service + Redis |
| **Move submits** | Player moves | ~5K/s | ~5M/s | Game shards |
| **Clock ticks / flag checks** | Timer wheel | ~25K/s (games) | ~25M/s | Game servers (local) |
| **Player WS events** | Move push to opponent | ~5K/s | ~5M/s | WS gateway |
| **Spectate fan-out** | Broadcast moves | ~20K/s | ~20M+/s | Pub/sub / CDN |
| **Rating writes** | Post-game | ~100/s avg | ~10K/s avg (bursty) | Rating DB |
| **Anti-cheat ingest** | Move features | ~5K/s | ~5M/s | Kafka |

**Anti-pattern:** one “QPS” number mixing seeks, moves, and spectate amplifications.

### 2.2 Concurrent games memory

```text
Active game state: ~2–5 KB (position, clocks, meta) — denser with move list in Redis
25K games × 5 KB = 125 MB
25M games × 5 KB = 125 GB fleet-wide  ← shard; not one node
```

### 2.3 Move bandwidth

```text
Move event ~200 B on wire
5K moves/s × 200 B ≈ 1 MB/s (players only)
Spectate × avg spectators:
  If avg 4 spectators: +4× → ~5 MB/s baseline
  Viral game 100K spectators × 1 move/s ≈ 100K events/s on that game alone → special broadcast path
```

### 2.4 Matchmaking queue

```text
Pool per (time_control, rated?, variant): waiting seekers
Data: user_id, rating, expand_radius, enqueued_at (~100 B)
50K waiting × 100 B = 5 MB — tiny
Hot path: atomic match two users — correctness > size
```

### 2.5 Storage (finished games)

```text
PGN/move log ~1–3 KB / game average
5M games/day × 2 KB ≈ 10 GB/day
1,000×: ~10 TB/day → object storage + cold tier; metadata in DB
```

### 2.6 Clock tick myth

```text
Do NOT wake every game every 100ms globally via Redis.
Each game shard runs a timer wheel / heap of next flag deadline only.
25K games → 25K heap entries; wake on next deadline or on move.
```

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
+------------------------------------------------------------------+
| Chess.com-like     Blitz 3+2    Rating 1624    [Seek] [Puzzles] |
+-------------------+----------------------------------------------+
| Play              |     [Board 8x8]          Clocks              |
|  Seek game        |   r n b q k b n r       White  1:42          |
|  Challenges       |   p p p p p p p p       Black  1:55          |
|  Games in progress|   ...                                        |
|                   |   Moves: 1.e4 e5 2.Nf3 ...                   |
| Spectate          |   [Resign] [Offer draw]                      |
+-------------------+----------------------------------------------+
```

### 3.2 Domain model

```text
User
 ├── Rating[time_control]  (ELO or Glicko-2 params)
 └── Preferences

Seek
 └── queue_key (tc, rated, variant), rating, range, enqueued_at

Game
 ├── game_id, white_id, black_id, tc, rated
 ├── status: matching|active|aborted|mate|resign|timeout|draw|stalemate|...
 ├── fen / compact position + move_number + side_to_move
 ├── clocks_ms {white, black}, last_stamp_server
 ├── draw_offer_from?
 ├── move_list[] / ply
 └── version / ply_seq  (CAS)
```

**Ownership (resolved):**

| Concern | SoT |
|---------|-----|
| Legal position & move acceptance | **Game authority shard** |
| Clocks | **Game authority** (server_ts) |
| Matchmaking pairing | **MM service** atomic ops |
| Ratings | **Rating service** after terminal game |
| Spectators list | Ephemeral pub/sub; not on game critical path |
| Fair-play scores | Async analysis pipeline |

**Deal-breaker:** trusting client for legality or clock; multi-writer game state without versioning.

### 3.3 Matchmaking (ELO / Glicko)

**Queue key:** `(time_control, rated, variant, region_pref?)`

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
| **ELO** | Simple, well-known | Less principled uncertainty |
| **Glicko-2 (often preferred)** | RD (uncertainty) helps matching new players | Slightly more state |
| TrueSkill | Good for teams | Overkill for 1v1 chess MVP |

**Choice:** Glicko-2 or ELO—pick one; store per time control.

**Atomic match (critical):**

```text
Redis: try MATCH via Lua:
  remove both from queue if still present → return pair
  else fail
DB: insert game uniquely; losers requeue
```

### 3.4 Authoritative game server

```text
Client --move--> WS GW --> Game Service (shard by game_id)
                         1. load state (memory/Redis)
                         2. check side_to_move, status active
                         3. apply clock until now (server)
                         4. if flagged → terminal timeout
                         5. validate move with rules engine
                         6. update fen, clocks, ply_seq
                         7. persist (Redis + append log)
                         8. ACK mover; publish to opponent + spectate bus
```

**Rules engine:** server-side library (or WASM microservice). Must handle:

- Pseudo-legal vs legal (pins)
- Castling rights / squares
- En passant
- Promotion
- Checkmate / stalemate
- Draw claims: threefold, 50-move; insufficient material

### 3.5 Chess clocks (server-side)

```text
On move accept at server_ts T:
  elapsed = T - last_stamp
  clock[side_to_move] -= elapsed
  if clock[side] <= 0: FLAG (unless move delivered earlier — define)
  else:
    clock[side] += increment
    switch side
    last_stamp = T
```

**Flag vs move race (define explicitly):**

> Prefer: timestamp the move arrival at authority; if clock already ≤0 before arrival → timeout win; if move arrives with remaining time → accept then switch. Document; never ask client.

**Timer wheel:** per shard, min-heap of `next_flag_at`; wake to end games without moves.

### 3.6 Reconnect / resume

```text
Client stores game_id + reconnect_token
On reconnect:
  auth → fetch snapshot {fen, clocks_now, ply_seq, moves_hash}
  resubscribe WS topic game:{id}:players
  if game terminal → show result
```

**Clock during disconnect:** continues (standard online chess). Optional “pause on disconnect” is product (usually no for blitz).

**Grace:** if both absent N minutes in long TC → abort/abandon policy.

### 3.7 Draw, resign, abort

| Action | Rules |
|--------|-------|
| Resign | Active player → opponent wins |
| Draw offer | Set offer; opponent accept/decline; expire on next move often |
| Abort | e.g. within first few plies + little time used; unrated |
| Takeback | Usually off for rated |

### 3.8 Spectating fan-out

| Approach | Pros | Cons |
|----------|------|------|
| Push every spectator from game shard | Simple | Melts on viral games |
| Pub/sub topic per game | Decouples | Still hot fan-out |
| **Hybrid (chosen)** | Players get direct push; spectators via broadcast tier / Redis pubsub / Kafka → WS | Extra component | Production |

```text
Game shard --move_event--> Spectate Relay
  ├── small games: Redis Pub/Sub
  └── hot games: dedicated broadcaster + optionally HLS-like snapshot stream
```

**Deal-breaker:** looping 100K spectator sockets inside the authoritative game process.

### 3.9 Anti-cheat hooks

```text
For each move, emit FairPlayEvent:
  game_id, ply, fen_before, uci, think_time_ms, client_ip_hash, device_fp, rating
Async workers:
  engine eval deltas, move-match % to engines, statistical anomalies
Outcomes: shadow flag → review queue → restrictions
```

**Not in MVP critical path:** blocking each move on engine analysis (latency killer).

### 3.10 Tournaments (optional sketch)

- Arena: continuous pairings from standing scores.  
- Swiss: round pairings batch job.  
- Reuses Game service; adds `tournament_id` + pairing service.  
- Isolate from ladder matchmaking queues.

### 3.11 API / protocol

**HTTP:** seek, cancel seek, get game, get user ratings, report.

**WS events:**

```text
C→S: move {game_id, ply, uci, move_id}
C→S: resign | draw_offer | draw_accept | abort
S→C: game_state | move_accepted | move_rejected | clock_tick_summary | game_over
S→C: spectate_move (spectators)
```

**Idempotency:** `(game_id, move_id)` unique; retries safe.

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
                      | (rules, clocks, state)      |
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

### 4.2 Match → first move sequence

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

### 4.3 Reconnect sequence

```text
Client-->API: GET /games/{id}/snapshot
Client-->WS: subscribe(game_id, token)
WS-->GameShard: attach connection
GameShard-->Client: snapshot + catchup from ply_seq
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Single-writer authority per game_id** (shard owner + fencing).  
2. **Server clock SoT**; client clocks cosmetic.  
3. **Move ACK ⇒ durable** in active store + append log (RPO≈0 for accepted moves).  
4. **CAS on ply_seq** — no silent overwrite.  
5. **Matchmaking atomic claim** — no triple pairing.  
6. **Terminal state once** — CAS status to terminal; ratings exactly once.  
7. **Spectate failure must not block players.**  
8. **Fair-play pipeline async** — must not add move RTT.

**Flag/move ordering invariant:** documented server_ts rule; deterministic replay from log.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | Monolith OK: MM + Game + WS; Redis; Postgres ratings/games |
| 10× | Shard games by hash(game_id); MM per TC; Kafka fair-play |
| 100× | Regional cells; spectate relay; rating CQRS; hot-game broadcasters |
| 1,000× | Edge gateways; approximate global leaderboards; fair-play offline fleet; cold PGN lake |

**Sticky routing:** `game_id → shard` via consistent hash; WS gateway looks up ownership directory.

**Matchmaking scale:** partition queues by rating band (e.g. 200-point buckets) + cross-band only when expanding—reduces scan cost; still use Lua atomicity within band coordinator.

### 5.3 Maintainability

- Rules engine versioned; replay suite of PGN fixtures.  
- Clock property tests (flag boundaries).  
- Chaos: kill shard mid-game → reload from Redis/log; fencing.  
- Metrics: move_latency, illegal_move_rate, mm_wait_p50/p99, flag_correctness audits, spectate_lag, fairplay_queue_depth.  
- Avoid per-game Prometheus labels.

### 5.4 Rating updates

```text
on_terminal(game):
  if not rated or abort: skip
  (r1,r2) = rating_svc.apply(result, tc)  # transactional per user pair ordering
  idempotent on game_id
```

**Ordering:** process rating by sorted user pair locks or single-threaded per user to avoid lost updates—or use atomic compare in DB.

### 5.5 Cheating prevention (honest scope)

| Layer | What |
|-------|------|
| UX friction | No analysis board during live rated (product) |
| Telemetry | Think times, accuracy vs engines offline |
| Accounts | Multi-account / farm detection |
| Reports | Human review queue for high RD / high suspicion |
| Sanctions | Shadow → ranked ban |

**Cannot promise:** zero cheating. Promise: detection hooks + auditability.

### 5.6 Consistency & replay

Store append-only moves:

```text
{ply, uci, server_ts, clock_white_after, clock_black_after, hash}
```

Rebuild FEN by replay for audits; active path keeps current FEN for speed.

---

## 6. Wrap-Up

### 6.1 What we designed

An **online chess** system with Glicko/ELO matchmaking, **authoritative** game+clock shards, reconnect snapshots, draw/resign/abort, hybrid spectate fan-out, and async fair-play telemetry—scaled by sharding `game_id` and isolating spectator storms from the player path.

### 6.2 Key decisions worth defending

1. **Server validates moves + clocks** — clients are untrusted.  
2. **Atomic matchmaking claims** — no triple games.  
3. **Single-writer game shard** with `ply_seq` CAS.  
4. **Timer wheel per shard**, not global tick storm.  
5. **Spectate ≠ player path.**  
6. **ACK after durable move.**  
7. **Ratings once per terminal game_id.**  
8. **Anti-cheat async** — don’t engine-eval on hot path.  
9. **Split load classes** in estimates.  
10. **Honest cheat impossibility** + strong audit logs.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Shard failover mid-blitz | Fast reload + reconnect storm tests |
| Viral spectate | Hot-game detector + dedicated broadcasters |
| Fair-play false positives | Human review; RD-aware |
| MM wait too long | Bots / wider range / pool merge |
| Clock disputes | Immutable server_ts logs |

### 6.4 How to present in 45 minutes

1. Requirements + authority model (6 min)  
2. Numbers with split classes (4 min)  
3. Matchmaking atomicity (7 min)  
4. Move+clock sequence (10 min)  
5. Reconnect + spectate + anti-cheat (8 min)  
6. Scale (5 min)  
7. Q&A (remaining)

---

## 7. Deeper / Related Interview Questions

### 7.1 Matchmaking

**Q: ELO vs Glicko-2?**  
A: Glicko-2 models uncertainty (RD)—better for new players. ELO simpler. Either fine if consistent per TC.

**Q: How avoid matching the same two smurfs always?**  
A: Recent-opponent cooldown; IP/device soft signals; not only rating.

**Q: Queue scan complexity?**  
A: Bucket by rating; expand bands; don’t O(n) scan millions globally every seek.

**Q: Regional matchmaking?**  
A: Prefer low RTT pools; cross-region if wait high—clock fairness OK (server), lag UX suffers.

### 7.2 Rules & state

**Q: Where does the rules engine run?**  
A: On authoritative game service; never trust client legality.

**Q: How to handle promotion UI races?**  
A: Move includes promotion piece; reject incomplete.

**Q: Threefold detection cost?**  
A: Maintain position hash history; claim or auto policy.

**Q: Why ply_seq?**  
A: Idempotency + reject stale; concurrent tabs.

### 7.3 Clocks

**Q: Why not client clock with server sync?**  
A: Cheating/pause; use server_ts elapsed.

**Q: Increment before or after flag check?**  
A: Check flag on elapsed before increment; then add increment—standard online pattern; state it.

**Q: Timer wheel vs per-game sleep threads?**  
A: Heap/timer wheel; threads-per-game won’t scale.

**Q: Correspondence (days) clocks?**  
A: Persist deadlines in DB; sweeper; not hot memory heap for all.

### 7.4 Reconnect & networking

**Q: Does disconnect pause clock?**  
A: Usually no for blitz/rapid; yes rare product modes.

**Q: Snapshot vs replay all moves?**  
A: Snapshot FEN+clocks + recent moves; full PGN on demand.

**Q: WS vs SSE?**  
A: WS bidirectional for moves; SSE awkward for client moves.

### 7.5 Spectating

**Q: 100K spectators on one game?**  
A: Detect hot game; dedicated broadcast tier; snapshots + delta; don’t run inside authority process.

**Q: Spectator lag SLO?**  
A: Weaker than player path; batch 50–100ms OK.

**Q: Privacy?**  
A: Rated public by default optional; private challenges no spectate.

### 7.6 Anti-cheat

**Q: Can you detect engines in real time?**  
A: Weakly; strong signals need full-game stats. Don’t block moves on Stockfish each ply in MVP.

**Q: What features matter?**  
A: Think-time vs complexity, match to engine top choices, accuracy outliers vs rating, multi-accounting.

**Q: False positives?**  
A: Review queues; temporary “play only with longer TC”; human appeals.

### 7.7 Ratings & storage

**Q: Lost rating update?**  
A: Idempotent `rating_applied` on game; outbox; sweeper.

**Q: Where store PGNs?**  
A: Object storage; DB holds metadata + result; hot recent in Postgres/Cassandra.

**Q: Leaderboards at 1,000×?**  
A: Approximate / tiered; not `ORDER BY rating` on hot OLTP every page view without cache.

### 7.8 Failure injection

1. Game shard kill → reload state; clients reconnect.  
2. Redis loss → fail closed new moves if state there; recover from append log if dual-written.  
3. MM Redis split → fencing; prefer under-match vs double-match.  
4. Spectate Kafka down → players unaffected.  
5. Fair-play lag → backlog; no move latency impact.  
6. Clock heap storm after DST bug → use monotonic server time.  
7. Duplicate game_over events → CAS terminal + idempotent ratings.  
8. Poison PGN replay → isolate rules version.  
9. Botnet seeks → rate limit seeks / captcha / account age.  
10. Hot celebrity match → autoscale broadcast, not game shard CPU for sockets.

### 7.9 Tournaments

**Q: How do Swiss pairings interact with game service?**  
A: Pairing batch creates seeks/challenges; games normal; standings consume results async.

**Q: Arena pairing storms?**  
A: Dedicated MM pool per tournament id.

### 7.10 Comparison traps

**Q: Is this just multiplayer networking?**  
A: Authority, clocks, ratings, fair-play, and spectate isolation dominate.

**Q: Why not CRDTs for the board?**  
A: Chess is conflict-free only with single authority—CRDT wrong model for rated clocks.

**Q: Same as online poker?**  
A: Similar authority/clock ideas; chess has richer rules + long games + spectate culture.

### 7.11 Extra interviewer traps (high value)

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
- What happens if rating service is down at game end?  
- How do you test rules engine upgrades?  
- Premoves: client-only or server-accepted queue?  
- How do you handle 25M concurrent games memory-wise?  
- What’s the deal-breaker in client-authoritative chess?

---

## Appendix A — Example schemas

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  handle TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ratings (
  user_id UUID NOT NULL,
  time_control TEXT NOT NULL, -- bullet|blitz|rapid|classical
  rating DOUBLE PRECISION NOT NULL,
  rd DOUBLE PRECISION NOT NULL,      -- Glicko
  volatility DOUBLE PRECISION NOT NULL,
  games_count INT NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, time_control)
);

CREATE TABLE games (
  id UUID PRIMARY KEY,
  white_id UUID NOT NULL,
  black_id UUID NOT NULL,
  time_control TEXT NOT NULL,
  rated BOOLEAN NOT NULL,
  status TEXT NOT NULL,
  result TEXT, -- 1-0|0-1|1/2-1/2|*
  ruleset_version TEXT NOT NULL,
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

## Appendix D — Estimation cheat-sheet

```text
games ≈ players_in_game / 2
move_QPS ≈ games × moves_per_sec_avg (blitz higher)
spectate_QPS ≈ move_QPS × avg_spectators (heavy tail!)

Do not global-tick clocks:
  wakes ≈ games that are near flag + on moves

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

**Move vs flag race rule (normative for this design):**

> Compare `move.server_receive_ts` to the authority’s `flag_deadline`. If `move.server_receive_ts > flag_deadline`, reject as timeout loss for the mover-to-play. If `≤`, accept move, then apply increment. Deterministic under replay.

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

Pipeline: Kafka → feature workers → offline Stockfish/SN ensemble → risk score → review queue. **Not** on move ACK path.

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
| Duplicate move_id | Same accepted move returned |
| Triple match race | Only one game; losers requeued |
| Shard kill | Reload FEN/clocks; clients snapshot |
| Double game_over | Ratings applied once |
| Spectate relay down | Players unaffected |
| Claim threefold wrongly | Reject claim |
| Abort window exceeded | Abort rejected; must resign/play |

---

*End of design doc. Open with §1 authority + clocks; whiteboard §3.3–3.5 matchmaking/moves/clocks; close with invariants in §5.1 and traps in §7.*
