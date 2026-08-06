# System Design: Tic-Tac-Toe API (HLD + LLD Hybrid)

> **Focus areas:** Resource model · Server-authoritative rules · Matchmaking · Realtime moves · Idempotency · Rematch · Ratings (light) · Clean LLD  
> **Style:** Microsoft API/LLD hybrid — smaller than full product HLD but complete; progressive scale (10× → 100× → 1,000×) still told  
> **Quality bar:** Client never trusted for win detection; explicit state machine; reconnect; error model  
> **Interview theme:** Often coded LLD + API contracts; may expand to multiplayer infra

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

Goal: **design a Tic-Tac-Toe API** (and object model) for creating games, matching players, applying legal moves server-side, detecting win/draw, handling resign/timeout, reconnect, and listing history—with optional ratings and rematch.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Multiplayer Tic-Tac-Toe **API + domain LLD** | AAA game engine |
| Authority | Server validates every move | Client says “I won” |
| Realtime | WebSocket (or long-poll MVP) | Pure offline single-device only |
| Board | Classic 3×3 (N×N extension noted) | Chess/Go complexity |
| Microsoft lens | Clean contracts + testable domain | Premature global mesh |

**Scope statement:** Tic-Tac-Toe multiplayer API: auth, matchmaking, authoritative gameplay, clocks/turn timeouts, reconnect, history—plus LLD for board rules.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Modes? | PvP online; vs bot optional | `opponent: USER\|BOT` |
| F2 | Matchmaking? | Random or friend invite | Seek + invite codes |
| F3 | Board? | 3×3 classic | `Board` 9 cells |
| F4 | Turns? | X always first | Enforce `next_mark` |
| F5 | Win/draw? | 3-in-row / full board | Pure functions in domain |
| F6 | Resign? | Yes | Terminal state |
| F7 | Timeout? | Turn timer optional MVP | Server clock |
| F8 | Rematch? | Yes | New game from lobby |
| F9 | Reconnect? | Resume state | Snapshot + seq |
| F10 | Spectate? | Optional | Read-only channel |
| F11 | Ratings? | Simple Elo Phase 1.5 | Async update |
| F12 | Auth? | Users; guests optional | JWT / guest token |
| F13 | History? | Recent games | Persist finished games |
| F14 | Chat? | Out of MVP | — |

**MVP scope:**

1. Register/login (or accept provided auth).  
2. Create seek / cancel seek / invite by code.  
3. On match: create `Game` with two players, marks assigned.  
4. `POST move` with cell index; server validates; broadcast.  
5. Auto terminal: win / draw; resign endpoint.  
6. Optional turn timeout → forfeit.  
7. WebSocket game events with `seq`.  
8. Reconnect: `GET game` + subscribe `since_seq`.  
9. List my games; get finished game.  
10. Idempotency on move retries.

**Out of MVP:** tournaments, wagering, 5×5 variants (keep extension hook), fancy anti-cheat beyond legality.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Move ACK / opponent see | p99 < 300–500ms in-region |
| N2 | Matchmaking | p50 < 2s when players available |
| N3 | Correctness | Zero illegal accepts |
| N4 | Durability | Finished games persisted |
| N5 | Availability | Degrade matchmaking before in-game |
| N6 | Concurrency | Exactly one legal apply per turn |
| N7 | Security | Can’t move as opponent |
| N8 | Scale | See table — game is tiny payloads |

### 1.3 Cases

**Happy:** match → X plays → O plays → … → win/draw → rematch.  
**Edges:** double-click move; move after game over; wrong turn; occupied cell; disconnect mid-game; both disconnect; seek cancel race; rematch one accepts; bot game; invite expired.

| Case | Behavior |
|------|----------|
| Duplicate move idem key | Same result |
| Illegal cell | 422 |
| Not your turn | 409 |
| WS drop | Reconnect snapshot |
| Turn timeout | Auto resign/forfeit |
| Matchmaking empty | Wait / timeout seek |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 100K | 1M | 10M | 100M |
| Games / day | 500K | 5M | 50M | 500M |
| Peak moves / s | 200 | 2K | 20K | 200K |
| Concurrent games | 20K | 200K | 2M | 20M |
| WS connections | 40K | 400K | 4M | 40M |
| Matchmaking seeks / s | 50 | 500 | 5K | 50K |

**Jumps:** 10× = sticky game servers + Redis; 100× = realm/cell by game_id; 1,000× = regional matchmaking + connection gateways.

### 1.5 Constraints

- Board state small (~bytes)—optimize **connections & matchmaking**, not storage.  
- Server authoritative.  
- Clocks monotonic server-side.

**Repeat-back:**

> Authoritative Tic-Tac-Toe API with matchmaking, legal move application, win/draw detection, reconnectable realtime events, and a clean domain model—scaled via game sharding and connection gateways.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Payload math

```text
Move request ~100 B; event ~200 B
Game state JSON ~300–500 B
500K games/day × ~9 moves ≈ 4.5M moves/day ≈ 50/s avg
```

### 2.2 Connections

```text
Concurrent games 20K × 2 players = 40K WS
Each idle heartbeat 30s → manageable on few gateway nodes
At 100× need GW fleet + Redis pubsub / Azure Web PubSub
```

### 2.3 Storage

```text
Finished game ~1 KB × 500K/day ≈ 0.5 GB/day
In-memory active games tiny
```

### 2.4 Bottlenecks

(1) WebSocket fanout (2) matchmaking lock/contention (3) hot rematch lobbies (4) not CPU for 3×3 rules.

---

## 3. High-Level Design

### 3.1 Resources

```text
User { id, display_name, rating?, guest? }
Seek { id, user_id, mode, created_at, status }
Invite { code, host_user_id, expires_at }
Game {
  id, status, board[9], next_mark, players{X,O},
  winner, win_line, move_count, version/seq,
  turn_deadline_at?, created_at, finished_at?
}
Move { game_id, seq, mark, cell, ts }
```

### 3.2 State machines

```text
Seek: OPEN → MATCHED | CANCELLED | EXPIRED

Game: WAITING → IN_PROGRESS → FINISHED
                         ↘ ABORTED

Finished reason: WIN | DRAW | RESIGN | TIMEOUT | ABORT
```

### 3.3 API

```http
POST /v1/seeks
DELETE /v1/seeks/{id}
POST /v1/invites                 # → {code}
POST /v1/invites/{code}/join
GET  /v1/games/{id}
POST /v1/games/{id}/moves        # {cell, Idempotency-Key}
POST /v1/games/{id}/resign
POST /v1/games/{id}/rematch
GET  /v1/users/me/games?cursor
WS   /v1/games/{id}/ws           # events
```

**Move body:** `{ "cell": 0-8 }` or `{ "row":0, "col":0 }`.

**Errors:** `422 ILLEGAL_MOVE`, `409 NOT_YOUR_TURN|GAME_NOT_ACTIVE`, `403`, `404`.

### 3.4 Realtime events

```text
GAME_STARTED {game, you_are: X|O}
MOVE_APPLIED {seq, cell, mark, board, next_mark, turn_deadline_at?}
GAME_FINISHED {reason, winner, win_line, board}
OPPONENT_RESIGNED
PEER_DISCONNECT / PEER_RECONNECT (optional)
ERROR {code, message}
```

Every event has monotonically increasing `seq` per game.

### 3.5 Matchmaking

**Random seek:** queue by mode; pair FIFO or simple skill buckets if ratings exist.  
**Invite:** host creates code; joiner posts code → game.  
**Bot:** immediate game with `BOT` player; server/bot policy random-legal or perfect minimax (3×3 solvable).

**Concurrency:** transactional claim of two seeks or Redis `BRPOP` pair worker.

### 3.6 LLD — domain model (core)

```text
enum Mark { X, O }
enum GameStatus { WAITING, IN_PROGRESS, FINISHED }

final class Board {
  private final Mark[] cells; // length 9, null empty
  Board place(Mark m, int cell); // returns new or mutates with checks
  Optional<Mark> winner();
  boolean full();
  List<Integer> legalMoves();
}

final class GameRules {
  static ApplyResult apply(GameState s, PlayerId actor, int cell);
  // checks status, actor==toMove, cell empty, then win/draw
}

record GameState(
  GameId id, Board board, Mark next, Players players,
  GameStatus status, Optional<Mark> winner, Optional<WinLine> line,
  long seq, Instant turnDeadline
) {}

interface GameRepository { GameState get; boolean casSave(expectedSeq, newState); }
interface Clock { Instant now(); }
interface EventPublisher { void publish(GameId, Event); }
```

**Win detection:** check 8 lines; or bitboards (`xBits`, `oBits`) with masks—nice interview flourish.

```text
WIN_MASKS = [
  0b111000000, 0b000111000, 0b000000111, // rows
  0b100100100, 0b010010010, 0b001001001, // cols
  0b100010001, 0b001010100              // diags
]
winner if (bits & mask) == mask
```

### 3.7 Service map

| Component | Role |
|-----------|------|
| API / Game Service | REST + rules |
| Matchmaker | Seeks → games |
| Game Store | Redis active + SQL history |
| WS Gateway | Connections; pubsub per game |
| Timeout Worker | Turn deadlines |
| Rating Worker | Optional Elo |
| Bot Worker | Optional |

### 3.8 Persistence split

| State | Store |
|-------|-------|
| Active game | Redis / memory + WAL |
| Finished game | SQL/Cosmos |
| Seeks | Redis queue |
| Idempotency move | Redis key per game |
| Ratings | SQL |

### 3.9 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Authority | Server | Anti-cheat / correctness |
| Transport | WS + REST snapshot | Reconnect friendly |
| Active store | Redis | Low latency CAS |
| History | SQL | Queryable |
| Matchmaking | Simple queue MVP | Enough for TTT |
| Bot | Minimax optional | Perfect info game |
| N×N | Parameterize later | Don’t overbuild |

### 3.10 Progressive scale

| Scale | Add |
|-------|-----|
| 1× | Monolith API+WS; Redis games; SQL history |
| 10× | Split WS gateway; Redis pubsub; sticky `game_id` |
| 100× | Game cells/realms; matchmaking service; timeout fleet |
| 1,000× | Regional realms; connection GW tier; shard seeks |

---

## 4. Architecture Diagram

### 4.1 HLD

```text
Clients
   │ REST                  │ WS
   ▼                       ▼
┌─────────┐          ┌───────────┐
│ Game API│◄────────▶│ WS Gateway│
└────┬────┘          └─────┬─────┘
     │                     │ pubsub
     ▼                     ▼
┌──────────┐         ┌───────────┐
│Matchmaker│         │ Redis     │
└────┬─────┘         │ games+bus │
     │               └─────┬─────┘
     │                     │
     ▼                     ▼
┌─────────┐          ┌───────────┐
│ SQL     │◄─────────│ Timeout / │
│ history │          │ Rating    │
└─────────┘          └───────────┘
```
### 4.2 Move sequence

```text
P1                API/Rules           Redis            WS/P2
 |--POST move---->|                   |                |
 |                |--GET+CAS apply--->|                |
 |                |--publish MOVE-------------------->|
 |<-200 state-----|                   |                |
```

### 4.3 Reconnect

```text
Client reconnect → auth → GET /games/{id} → WS subscribe(since_seq)
Server sends snapshot then events seq > since
```

### 4.4 Matchmaking

```text
Seek queue ──worker──▶ create Game ──notify both via WS/push
Invite code ──join──▶ create Game
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Only `next_mark` player can place.  
2. No move on occupied cell or finished game.  
3. `seq` increases by 1 per accepted mutation.  
4. CAS/lock ensures single apply wins under concurrency.  
5. Terminal state immutable (except rematch creates new id).  
6. Authz: actor must be player in game.

**Failure handling**

| Failure | Mitigation |
|---------|------------|
| Double submit | Idempotency key → same seq result |
| CAS fail | Retry load/apply if still legal |
| WS down | REST snapshot + resume |
| Redis loss | Accept reconnect risk MVP; or dual-write snapshot SQL periodically |
| Timeout race with move | CAS on status/seq; one wins |

### 5.2 Scalability

Board CPU irrelevant. Scale **connections** and **matchmaking**.

- Shard active games by `game_id` hash to realms.  
- WS gateway holds conns; game service owns rules; Redis pubsub or Azure Web PubSub bridges.  
- Matchmaking: sharded queues by rating bucket / region.  
- 10× → 100× → 1,000× as in §3.10.

**Backpressure:** limit seeks/user; max concurrent games/user; disconnect idle spectators first.

### 5.3 Maintainability

- **Pure domain** (`Board`, `GameRules`) unit-tested without HTTP.  
- API layer maps DTOs ↔ domain.  
- Feature flags: turn timer, ratings, bot difficulty.  
- Version events for clients.  
- Microsoft interview tip: be ready to **code** `applyMove` + win check on a whiteboard.

### 5.4 Security

- Bind WS and REST to same auth.  
- Never trust client `winner`.  
- Rate-limit moves (human max ~few/s).  
- Invite codes unguessable + TTL.  
- Guests: scoped tokens; convert on register.

### 5.5 Consistency

Active game: linearizable via Redis WATCH/CAS or Lua.  
History: write-on-finish.  
Ratings: async eventual after finish.

### 5.6 Turn timer

```text
On move apply: turn_deadline = now + N seconds
Timeout worker zset pop → try forfeit if still same seq/turn
```

### 5.7 Rematch

```text
POST rematch by either → RematchLobby {accepts[]}
Both accept → new Game; marks swapped optional
```

### 5.8 Extension: N×N / K-in-row

Parameterize `Board(size)` and `k`; win check generalize; keep API `cell` index `0..n^2-1`. Mention only if asked.

### 5.9 Bot strategy

```text
Easy: random legal
Hard: minimax + perfect; 3×3 drawable with perfect play
Bot moves async short delay for UX
```

---

## 6. Wrap-Up

### 6.1 Summary

Small realtime multiplayer API: **matchmaking + authoritative GameRules + seq events + Redis active state + SQL history**. LLD centers on immutable/pure board transitions and CAS.

### 6.2 Trade-offs

1. Redis-only active vs always SQL.  
2. WS vs long-poll MVP.  
3. Perfect bot vs random.  
4. Ratings in path vs async.  
5. Monolith vs split GW early.

### 6.3 Build order

Domain rules + tests → REST create/move → in-memory games → WS events → matchmaking → Redis → timers → history → ratings.

### 6.4 Risks

| Risk | Mitigation |
|------|------------|
| Illegal accept bug | Property tests all boards |
| Desync clients | seq + snapshot |
| Matchmaker double-pair | Atomic claim |
| Conn storms | GW autoscaling |

### 6.5 Close

> Keep rules pure and server-side; scale connections and matchmaking—not the 3×3 evaluator.

---

## 7. Deeper / Related Interview Questions

### 7.1 Coding / LLD

**Q: Implement `winner()`.**  
A: 8 masks or loop lines; return X/O/empty.

**Q: Thread safety?**  
A: Per-game lock or Redis Lua apply.

**Q: Why bitboards?**  
A: Fast + elegant for fixed 3×3; explain clearly.

### 7.2 API

**Q: Idempotent move?**  
A: Key → stored response with seq.

**Q: How spectate safely?**  
A: Read-only channel; no move authz.

### 7.3 Scale

**Q: 10×?** Sticky WS + Redis pubsub.  
**Q: 100×?** Game realms by id.  
**Q: 1,000×?** Regional matchmaking + GW tier.

### 7.4 Microsoft-flavored

**Q: Azure?**  
A: APIM; AKS; Azure Cache Redis; Web PubSub; Azure SQL; Functions for timeouts; Entra ID.

**Q: Would you use Durable Functions?**  
A: Possible for game saga; Redis CAS usually simpler for moves.

### 7.5 Traps

| Trap | Better |
|------|--------|
| Client win detection | Server rules |
| Skip seq/reconnect | Snapshot+seq |
| Overdesign Kafka | Redis fine |
| Global lock all games | Per-game CAS |
| Floaty “eventually consistent moves” | Linearizable apply |

### 7.6 Related

- Online chess API  
- Realtime game leaderboard  
- Presence service  
- WebSocket gateway design

---

## 8. Appendices

## Appendix A — Apply move pseudocode

```text
function applyMove(game, actorId, cell, now):
  if game.status != IN_PROGRESS: error GAME_NOT_ACTIVE
  mark = markFor(actorId, game.players)
  if mark != game.next_mark: error NOT_YOUR_TURN
  if cell < 0 or cell > 8: error ILLEGAL
  if game.board[cell] != empty: error ILLEGAL
  if game.turn_deadline and now > deadline: error TIMEOUT_PENDING
  board2 = copy(game.board); board2[cell] = mark
  w = winner(board2)
  if w: status=FINISHED; reason=WIN; winner=w
  else if full(board2): status=FINISHED; reason=DRAW
  else: next = opposite(mark); refresh deadline
  seq2 = game.seq + 1
  return newState
```

## Appendix B — JSON examples

**Game**

```json
{
  "id": "g_123",
  "status": "IN_PROGRESS",
  "board": ["X","O",null,"X",null,null,null,null,null],
  "next_mark": "O",
  "players": {"X": "u1", "O": "u2"},
  "seq": 3,
  "turn_deadline_at": "2026-08-06T12:00:30Z"
}
```

**Event**

```json
{
  "type": "MOVE_APPLIED",
  "seq": 4,
  "cell": 4,
  "mark": "O",
  "board": ["X","O",null,"X","O",null,null,null,null],
  "next_mark": "X"
}
```

## Appendix C — SQL history

```sql
CREATE TABLE games (
  game_id UUID PRIMARY KEY,
  player_x TEXT NOT NULL,
  player_o TEXT NOT NULL,
  status TEXT NOT NULL,
  winner TEXT,
  reason TEXT,
  board TEXT NOT NULL,
  move_count INT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  finished_at TIMESTAMPTZ
);

CREATE TABLE game_moves (
  game_id UUID NOT NULL,
  seq INT NOT NULL,
  mark CHAR(1) NOT NULL,
  cell SMALLINT NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (game_id, seq)
);
```

## Appendix D — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Rules, REST, WS, seek, persist finish |
| 10× | Redis active, pubsub, sticky GW |
| 100× | Realms, matchmaker service, timers |
| 1,000× | Regional GW, sharded seeks |

## Appendix E — Glossary

| Term | Meaning |
|------|---------|
| Seek | Matchmaking request |
| Seq | Per-game event version |
| Mark | X or O |
| CAS | Compare-and-set apply |
| Realm / cell | Shard of games |
| Win line | 3 cells that won |

## Appendix F — Invariant tests

| Test | Expect |
|------|--------|
| Play occupied | Reject |
| Wrong turn | Reject |
| Winning third mark | FINISHED WIN |
| Full board no win | DRAW |
| Idempotent move | Same seq |
| Resign | Opponent wins |
| Timeout | Forfeit |
| Authz other user move | 403 |

## Appendix G — Minimax sketch (bot)

```text
function minimax(board, mark, maximizing):
  if terminal: return score
  best = -inf/inf
  for m in legal:
    best = max/min(best, minimax(result, opp, !maximizing))
  return best
```

## Appendix H — Redis key layout

```text
game:{id} → JSON state
game:{id}:idem:{key} → response
seek:queue:{mode} → list
game:{id}:events → pubsub channel
turn:zset → score=deadline_ms member=gameId
```

## Appendix I — Class diagram (text)

```text
GameService
  ├─ GameRules
  ├─ Board
  ├─ GameRepository
  ├─ Matchmaker
  ├─ EventPublisher
  └─ TimeoutScheduler
```

## Appendix J — Runbook

1. WS spikes → scale gateways; shed spectators.  
2. Illegal move rate up → client bug; check version skew.  
3. Matchmaker lag → scale workers; check queue depth.  
4. Redis failover → reconnect clients; rebuild from SQL if snapshotted.

## Appendix K — Azure mapping

| Concern | Azure |
|---------|-------|
| API | APIM + AKS |
| Realtime | Azure Web PubSub |
| Active state | Azure Cache for Redis |
| History | Azure SQL |
| Timers | Functions / worker |
| Auth | Entra ID |

## Appendix L — Interview timing guide

```text
0–5 min: clarify PvP, timers, bot, reconnect
5–15: resources + state machine + API
15–30: code Board/apply/winner
30–40: WS seq + matchmaking + Redis
40–45: scale 10×/100× + traps
```

## Appendix M — Sample unit tests list

```text
empty board no winner
row win X
col win O
diag win
draw full
reject place on filled
reject move after finish
N×N hook skipped unless asked
```

---

*End of design doc. Open with authority + state machine §3.2; code §3.6 / Appendix A; close with reconnect §4.3 and traps §7.5.*
