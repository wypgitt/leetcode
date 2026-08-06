# System Design: Candy-Crush Board Initialization & Possible Moves

> **Focus areas:** Match-free board generation · Move detection · Gravity & cascade · Game server / authoritative state · Anti-cheat (light) · Deterministic replay  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct board invariants, split client prediction vs server authority, explicit RNG/seed story, deal-breakers for “trust the client” and “scan whole board every frame on server”  
> **Interview theme:** Classic Google L5+ game-backend + algorithms — correctness under concurrency, fair RNG, cascade simulation at scale, progressive multiplayer/async load

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

Goal: **bound the product**—a **Candy-Crush-style match-3** backend that **initializes boards without pre-existing matches**, **enumerates / validates possible moves**, applies **swaps → match → gravity → cascade**, and keeps **authoritative game state** with **light anti-cheat**. This is not a full social network or monetization platform.

### 1.0 What this is / is not

| Dimension | **Board init + moves (this doc)** | Not this |
|-----------|-----------------------------------|----------|
| Primary job | Fair boards, legal moves, cascade resolution | Full game studio / live-ops CMS |
| Success | Correct invariants; fair RNG; cheat-resistant scores | Pixel-perfect client animation sync globally |
| Data plane | Session state + move log + RNG seed | Arbitrary analytics warehouse MVP |
| Query | Get board / submit move / list hints | Ad-hoc SQL over all historic tiles |
| Correctness | Server-authoritative board after each move | Trust client-reported cascades |

**Scope statement:** Design board generation (no initial matches), move detection/validation, gravity+cascade simulation, game-server state, and light anti-cheat—scaling sessions through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Board size / colors? | Classic ~9×9, 5–6 candy colors; specials Phase 1.5 | Grid `R×C`, color set `K` |
| F2 | Initial board rules? | No 3-in-a-row at t=0; preferably ≥1 legal move | Generator + solvability check |
| F3 | Move definition? | Adjacent swap that creates ≥1 match of 3+ | Validate adjacency + match after swap |
| F4 | Cascade? | Matches clear → gravity → refill → repeat until stable | Deterministic sim loop |
| F5 | Specials (striped/wrapped)? | Phase 1.5 OK; mention hooks | Match-length → special spawn rules |
| F6 | Hints / possible moves? | Yes — list or “exists?” for UX + shuffle | Move enumerator API |
| F7 | Shuffle when stuck? | Yes if zero moves and moves remain | Reshuffle preserving no-match init rules |
| F8 | Authoritative server? | Yes for score/lives/progress | Client may predict; server commits |
| F9 | Multiplayer? | Async levels MVP; realtime PvP out | Session-scoped state |
| F10 | Seeded boards? | Same seed ⇒ same board for fairness / QA | Deterministic RNG |
| F11 | Levels / objectives? | Score / clear N / collect — thin layer | Level config separate from engine |
| F12 | Anti-cheat? | Light: validate moves, rate limits, seed binding | Reject impossible deltas |

**MVP functional scope:**

1. Generate `R×C` board with `K` colors: **no initial matches**, optionally **≥1 legal move**.  
2. Enumerate possible moves (or existence check) for hints / stuck detection.  
3. Accept swap moves; reject illegal; apply match → clear → gravity → refill → cascade until stable.  
4. Persist session state (board, score, moves left, seed, version).  
5. Return post-move board + cascade events for client animation (or compact diff).  
6. Light anti-cheat: adjacency, seed-bound RNG, move rate, score bounds.  
7. Shuffle path when no moves remain (if level allows).

**Out of MVP:**

- Realtime synchronous PvP / shared board  
- Full special-candy physics encyclopedia (hooks only)  
- Client-trusted high scores without validation  
- Procedural infinite unique art assets  
- Full economy / IAP / social gifting  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Move latency | Feels instant | p99 validate+sim < 30–50ms in-region |
| N2 | Board gen latency | On level start | p99 < 100ms (retry loops bounded) |
| N3 | Correctness | No silent illegal clears | Deterministic given seed+moves |
| N4 | Availability | Session resume | 99.9% session store; sticky or shard by session |
| N5 | Fairness | Same seed → same board | Shared RNG algorithm versioned |
| N6 | Cheat resistance | Obvious score hacks fail | Server authority; anomaly flags |
| N7 | Scale | Millions concurrent sessions | Stateless game workers + sharded state |
| N8 | Observability | Debug bad boards | Seed + move log replay |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Start level → server generates seed → board → client renders.  
2. Player swaps adjacent candies → server validates → cascade → score update → response.  
3. Hint request → server returns one/all legal moves.  
4. No moves → shuffle → new board still match-free with moves.  
5. Level complete → persist progress; award stars.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Swap creates no match | Reject (or allow “wasted move” if product says so—usually reject) |
| Generator keeps producing matches | Retry with new seed; cap attempts; fallback constructive fill |
| Cascade loops forever | Hard iteration cap; assert progress (tiles cleared or settled) |
| Client sends future board | Ignore board; only accept move coordinates |
| Double-submit same move | Idempotency key / version check |
| Session worker crash mid-cascade | Replay from last committed version + move log |
| Clock skew on client | Server timestamps only |
| Hint on huge board | Precompute or incremental; cache until board changes |
| All colors blocked by walls (level geo) | Respect mask; generator uses playable cells only |
| Score overflow | Cap + anomaly |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 1M | 10M | 100M | 1B |
| Concurrent sessions | 50K | 500K | 5M | 50M |
| Moves/s (global) | 20K | 200K | 2M | 20M |
| Level starts/s | 2K | 20K | 200K | 2M |
| Avg cascade depth | 2–4 | 2–4 | 2–5 | 2–6 |
| Board cells | ~81 | 81–144 | mix | mix + events |
| Session state size | ~1–2 KB | 2–4 KB | 4 KB | +replay |
| Hint QPS | 5K | 50K | 500K | 5M |
| Game workers | 50 | 500 | 5K | cell fleets |
| Regions | 1–3 | 5–8 | 12+ | global PoPs |

**What each jump forces:**

- **10×:** Shard sessions; cache level configs; avoid full-board O(n²) naiveté on hot path without care.  
- **100×:** Regional game cells; move log in Kafka for analytics/replay; hint cache; rate limits.  
- **1,000×:** Edge prediction + regional authority; compact binary protocols; generative board pools; anti-cheat scoring fleet.

### 1.5 Etc. (Constraints & Assumptions)

- Client handles animation; server returns **event list** or final board + RNG stream consumed.  
- Levels defined by config (objectives, blockers mask)—engine is generic.  
- **Determinism** is a first-class requirement for support and anti-cheat.  
- “Candy Crush” here means match-3 genre mechanics, not King IP specifics.

**Scope statement to repeat back:**

> Design a match-3 game backend that generates match-free boards (preferably with legal moves), validates swaps, simulates gravity and cascades authoritatively, exposes possible-move/hint APIs, and applies light anti-cheat—scaling sessions through 10× / 100× / 1,000× with sharded session state and deterministic seeded RNG.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Level start** | Board gen + session create | ~2K/s | ~20K/s | Game API |
| **Move submit** | Validate + cascade | ~20K/s | ~200K/s | Game workers |
| **Hint** | Enumerate moves | ~5K/s | ~50K/s | Cacheable per board hash |
| **Session read** | Resume / sync | ~10K/s | ~100K/s | Session store |
| **Progress write** | Level complete | ~1K/s | ~10K/s | Player DB |
| **Telemetry** | Moves / funnels | ~25K/s | ~250K/s | Log bus |

**Anti-pattern:** one “QPS” mixing board gen CPU, Redis session GETs, and analytics Kafka.

### 2.2 Board gen cost

```text
Naive rejection sampling:
  fill random → scan matches → retry
  P(no match) depends on K and size
  For 9×9, K=6: often succeeds in few tries; worst case unbounded → MUST cap

Constructive approach:
  fill cell-by-cell choosing colors that don't complete a match
  then verify ≥1 move; if not, local reshuffle
  Expected CPU: O(R*C*K) ~ few thousand ops → microseconds–low ms

At 2K starts/s × 1ms gen = 2 cores; at 200K/s need pooling / pre-gen
```

### 2.3 Move validation + cascade cost

```text
Board cells N = R*C ≈ 81
Match scan: O(N) rows + cols
Gravity: O(N)
Cascade depth D ≈ 3 average, rare 10+
Work ≈ D * O(N) ≈ hundreds of cell ops → well under 1ms CPU

At 2M moves/s: still mostly network/serialization bound if engine is tight C++/Rust/Go
Bottleneck shifts to session store RPS and locking
```

### 2.4 Possible moves enumeration

```text
Brute force: try each adjacent pair (~2*R*C edges) × simulate match check
  ~160 swaps × O(N) ≈ 10K ops → fine for MVP

Optimize: for each cell, check if swap L/R/U/D creates match using local patterns
  O(N) pattern matching — prefer at 100× hint QPS

Cache: key = hash(board) → moves[]; invalidate on change
```

### 2.5 Session memory

```text
50K sessions × 2KB = 100 MB — trivial
5M sessions × 4KB = 20 GB — shard Redis/Memorystore
50M → multi-region session fabric + TTL idle eviction
```

### 2.6 Anti-cheat bandwidth

```text
Don't re-simulate entire level history on every move at 20M moves/s globally
  → incremental validate; sample full replay; anomaly offline
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/levels/{id}/start` | Create session; return `{session_id, seed, board, moves_left, version}` |
| `POST /v1/sessions/{id}/moves` | Body: `{x1,y1,x2,y2, client_move_id}` → cascade events + new board + score |
| `GET /v1/sessions/{id}` | Resume state |
| `GET /v1/sessions/{id}/hints` | `{moves: [[a,b],...]}` or `{exists: true, sample: ...}` |
| `POST /v1/sessions/{id}/shuffle` | If stuck and allowed |
| `POST /v1/sessions/{id}/complete` | Finalize score; server re-validates bounds |
| `GET /internal/replay?seed=&moves=` | Support / QA |

**Move response schema:**

```text
MoveResult {
  version,
  score_delta,
  score_total,
  moves_left,
  board,                 // final stable grid
  events: [              // for animation
    {type: MATCH, cells, colors},
    {type: CLEAR, cells},
    {type: FALL, from, to},
    {type: SPAWN, cell, color},
    {type: SPECIAL, ...} // Phase 1.5
  ],
  status: PLAYING|WON|LOST|SHUFFLE_NEEDED
}
```

### 3.2 Data model

| Entity | Key | Value |
|--------|-----|-------|
| Session | `session_id` | board, score, moves_left, seed, rng_offset, version, level_id, user_id |
| Level config | `level_id` | grid mask, K, objectives, move budget, specials flags |
| Player progress | `user_id` | stars, unlocked, lives |
| Move log (optional) | `(session_id, seq)` | move coords + version |
| Board pool (scale) | `(level_id, pool_slot)` | precomputed seed+board |
| RNG algorithm | `algo_version` | code id for determinism |
| Anomaly flag | `user_id` | soft ban / review |

### 3.3 Core invariants

```text
I1: After generation and after every cascade settles: no 3+ match exists
I2: A legal move is an adjacent swap that creates ≥1 match in the resulting grid
I3: Given (algo_version, seed, move_list), board+score are uniquely determined
I4: Client cannot invent candies; refill colors come from server RNG stream
I5: version increments monotonically per successful move
```

**Deal-breaker:** accepting client-supplied post-cascade board as truth.

### 3.4 Board generation — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Rejection sampling** | Simple | Unbounded retries; rare pathological | Tiny boards / prototypes |
| **Constructive cell fill** | Fast; guarantees no match | May yield 0 moves | **MVP pick** |
| **Template + permute** | Controllable difficulty | Content ops heavy | Live events |
| **Precomputed pool** | Zero gen latency | Storage; less variety | **100×+ starts/s** |
| **Constraint solver** | Rich constraints | Overkill CPU | Hard puzzle modes |

**Chosen MVP:** constructive fill → ensure ≥1 move (local swaps / limited reshuffle) → persist seed.

**Constructive fill sketch:**

```text
for r in 0..R:
  for c in 0..C:
    if masked: continue
    forbidden = colors that would complete match left/up
    board[r][c] = rng.choice(K \ forbidden)
# then:
if not has_any_move(board):
  reshuffle_playable(board, rng)  // bounded attempts
```

### 3.5 Match detection — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Full row/col scan** | Simple correct | O(N) each time | **MVP** — N tiny |
| **Union regions** | Good for specials | More code | Specials Phase 1.5 |
| **Incremental dirty rect** | Faster large boards | Complexity | Huge boards / 1,000× |
| **GPU client only** | Pretty | Not authoritative | Never sole truth |

**Match rule MVP:** ≥3 consecutive same color horizontally or vertically (diagonals no). Overlapping regions merge for clear.

### 3.6 Gravity & cascade

```text
loop:
  matches = find_matches(board)
  if matches empty: break
  clear(matches); apply_score_rules()
  maybe_spawn_specials()  // Phase 1.5
  apply_gravity()         // per-column compact down
  refill_from_top(rng)    // consume seeded RNG
  assert iterations < CAP
```

**Why server sim over client report:** fairness, anti-cheat, multi-platform parity.

### 3.7 Possible moves

```text
def has_move(board):
  for each adjacent pair (a,b):
    swap(a,b)
    ok = creates_match(board)
    swap(a,b)  // revert
    if ok: return True
  return False

# Pattern optimization (interview signal):
# For cell (r,c), check configurations like:
#   XX.X with swap, X.XX, and vertical analogs, "L/T" pre-match shapes
```

**Hints API:** return up to H moves; cache by `board_hash`.

### 3.8 Game server topology

```text
Client → API Gateway → Game Service (stateless)
  → Session Store (Redis) with optimistic version
  → Level Config Store
  → (optional) Move Log Kafka
  → Player Progress DB
Anti-Cheat (async) consumes move log / score anomalies
```

### 3.9 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Authority | Server | Fairness / cheat | Client score trust |
| RNG | Seeded + versioned algo | Replay / fairness | `Math.random` unsynced |
| Gen | Constructive (+ pool at scale) | Latency bounds | Unbounded rejection |
| Cascade | Server loop | Parity | Animation-only truth |
| Hints | Pattern/brute + cache | UX + stuck detect | Ignore zero-move boards |
| Concurrency | Version CAS on session | Lost update prevention | Blind overwrite |
| Anti-cheat | Validate + bounds + sample replay | Cost/benefit | Full ML on every move MVP |

---

## 4. Architecture Diagram

```text
                         +------------------+
   Mobile/Web clients -> |   API Gateway    |
                         +--------+---------+
                                  |
                                  v
                         +--------+---------+
                         |  Game Service    |  (stateless workers)
                         |  - gen board     |
                         |  - validate move |
                         |  - cascade sim   |
                         |  - hints         |
                         +---+-----+----+---+
                             |     |    |
              +--------------+     |    +----------------+
              v                    v                     v
     +--------+--------+  +-------+-------+    +--------+--------+
     | Session Store   |  | Level Config  |    | Player Progress |
     | Redis / Spanner |  | (CMS / DB)    |    | (DB)            |
     +--------+--------+  +---------------+    +--------+--------+
              |                                          ^
              | move log (optional)                      | complete
              v                                          |
     +--------+--------+                         +-------+-------+
     | Kafka / PubSub  |------------------------>| Anti-Cheat    |
     +--------+--------+   sampled replay        | + anomalies   |
              |                                  +---------------+
              v
     +--------+--------+
     | Analytics / BI  |
     +-----------------+

   Optional at 100×+:
   +------------------+     +-------------------+
   | Board Seed Pool  | --> | Game Service      |
   | pre-gen workers  |     | pop seed on start |
   +------------------+     +-------------------+
```

---

## 5. Design Deep Dive

### 5.1 Board representation

```text
board[r][c] = {
  color: 0..K-1 | EMPTY,
  type: NORMAL | STRIPED_H | ... ,  // Phase 1.5
  blocker: NONE | ICE | ...         // level mask layer
}
// Wire: compact int16 grid + separate mask from level config
```

**Column-major gravity** often simpler: each column is a stack.

### 5.2 Seeded RNG

| Concern | Approach |
|---------|----------|
| Algorithm | xorshift128+ / PCG32 — **versioned** |
| Binding | `seed = hash(user_id, level_id, attempt_id, server_secret_salt?)` or pure random stored |
| Refills | RNG advances only on server; client may mirror if same algo for prediction |
| Security | If anti-cheat matters, **don't ship secret** that lets clients predict future refills for advantage—or accept cosmetic prediction only |

**Interview nuance:** cosmetic client prediction can use mirrored RNG; competitive integrity may withhold refill stream until commit.

### 5.3 Initialization algorithm (production)

```text
def generate_board(level, rng):
  for attempt in range(MAX_ATTEMPTS):
    b = constructive_fill(level.mask, level.K, rng)
    if find_matches(b):  # should be impossible if constructive correct
      continue
    if level.require_move and not has_move(b):
      if try_local_fix(b, rng): 
        return b, rng
      continue
    return b, rng
  return pooled_fallback(level)  # or relax constraints
```

**Deal-breaker:** infinite retry loop without timeout in request path.

### 5.4 Move validation pipeline

```text
1. Load session; check status PLAYING, moves_left > 0
2. Check client_move_id idempotency
3. Check version == expected (or CAS)
4. Check adjacent + in bounds + not blocked
5. Swap; if !creates_match → reject (revert)
6. Run cascade; compute score_delta with level rules
7. Enforce score_delta ≤ max_plausible(depth, specials)
8. Persist session version+1; append move log
9. Return events
```

### 5.5 Gravity details

```text
for each column c:
  write = bottom_playable
  for r from bottom to top:
    if board[r][c] is candy and not stuck_blocker:
      compact into write; write = next_up
  fill empties from top via rng
```

Blockers (ice, chocolate) alter “playable” and clear rules—keep as data-driven level config.

### 5.6 Cascade scoring (MVP)

```text
score += cells_cleared * base * combo_multiplier
combo_multiplier increases per cascade step
4-in-a-row / 5-in-a-row → special spawn (Phase 1.5) instead of plain clear
```

### 5.7 Anti-cheat (light)

| Layer | Mechanism |
|-------|-----------|
| Protocol | Moves only (coords), not boards/scores |
| Validation | Legal swap + deterministic sim |
| Bounds | Max score/move; max cascade depth |
| Rate | Max moves/sec; humanized optional |
| Replay | Sampled full re-sim from seed |
| Economy | Server-side lives/boosters |
| Signals | Impossible completion time; perfect play bots |

**Not MVP:** kernel-level device attestation, full ML botnet graph.

### 5.8 Concurrency & session affinity

| Approach | Pros | Cons |
|----------|------|------|
| Optimistic CAS version | Simple horizontal scale | Retry on conflict |
| Sticky Redis lock | Easy serial moves | Hot lock / failover |
| Actor per session | Natural serial | Mesh complexity |

**Chosen MVP:** Redis `WATCH/MULTI` or Lua compare-and-set on `version`.

### 5.9 Reliability

| Failure | Mitigation |
|---------|------------|
| Worker crash mid-move | No commit until sim done; retry move |
| Redis blip | Client retry; session durable AOF/replication |
| Bad algo deploy | `algo_version` pin; dual-run shadow |
| Poison level config | Schema validate; canary levels |
| Cascade bug infinite | CAP + metrics; auto-fail session safe |

**Reliability principles:**

1. **Commit atomically** after full cascade.  
2. **Idempotent moves** via `client_move_id`.  
3. **Replayability** via seed + move log.  
4. **Degraded mode:** read-only resume if progress DB down; block new pays.

### 5.10 Scalability

| Scale | Tactic |
|-------|--------|
| 10× | Shard session by `session_id`; pool level configs in memory |
| 100× | Regional cells; pre-gen board pools; Kafka move logs; hint cache |
| 1,000× | Edge validate cosmetic; authority regional; binary protobuf; tiered anti-cheat |

**Session sharding:**

```text
shard = hash(session_id) % N
# or user_id sticky for all sessions of user
```

**Board pool workers:**

```text
while pool[level].size < TARGET:
  seed = random()
  board = generate(level, RNG(seed))
  push({seed, board_hash})
```

### 5.11 Maintainability

| Practice | Why |
|----------|-----|
| Pure engine library (no IO) | Unit test millions of seeds |
| Golden replay tests | Prevent cascade regressions |
| Versioned RNG + rules | Safe live updates |
| Data-driven levels | Designers don't ship code |
| Event schema for animations | Client/server decoupling |
| Feature flags for specials | Gradual rollout |

**Engine package structure:**

```text
engine/
  grid.go
  match.go
  gravity.go
  gen.go
  moves.go
  rng.go
  score.go
service/
  api.go
  session.go
  anticheat.go
```

### 5.12 Client prediction vs reconciliation

```text
Client: optimistic swap + local cascade (same algo)
Server: authoritative result
If mismatch: snap to server board (rare if deterministic + same version)
```

**Deal-breaker:** divergent RNG versions between app builds without forcing update.

### 5.13 Special candies (Phase 1.5 hooks)

| Match | Spawn |
|-------|-------|
| 4 | Striped |
| 5 | Color bomb |
| L/T shape | Wrapped |

Clear rules become graph activations—keep behind interface `ClearPlan`.

### 5.14 Progressive scale deep dive

**Baseline:** single region, Redis sessions, in-request gen.

**10×:**  
- Connection pooling, session TTLs, metrics on gen attempts.  
- Move p99 dashboards; CAS conflict rate.

**100×:**  
- Pre-gen pools for top levels.  
- Regional Redis + player DB replicas.  
- Anti-cheat consumers.  
- Compact boards on wire.

**1,000×:**  
- Game cells per geo; cross-region only for progress.  
- Hint existence bitset cached at edge for popular live events.  
- Shadow simulation fleet for top players / tournaments.

---

## 6. Wrap-Up

### 6.1 Design summary

We built a **server-authoritative match-3 engine**: constructive **match-free board generation** with optional **legal-move guarantee**, **swap validation**, **gravity/cascade simulation**, **hints**, and **light anti-cheat**, backed by **versioned session state** and **seeded RNG** for deterministic replay.

### 6.2 Key tradeoffs

| Tradeoff | Choice | Lost alternative |
|----------|--------|------------------|
| Authority vs latency | Server commit; client predict | Pure client / pure wait |
| Gen style | Constructive + pool at scale | Pure rejection sampling |
| Hint cost | Cache + patterns | Always full brute |
| Anti-cheat depth | Validate + sample | Full continuous ML |
| Determinism | Versioned RNG | Platform `rand` drift |

### 6.3 Deal-breakers (call out in interview)

1. Trusting client board/score.  
2. Unbounded rejection sampling on request path.  
3. Non-deterministic refill across clients.  
4. Blind session overwrite without versioning.  
5. Scanning “interesting” ML anti-cheat before basic validation exists.  
6. Claiming realtime PvP without lockstep/state sync design.

### 6.4 Progressive scale one-liner

> **Gen+validate cheap → shard sessions → pre-gen pools & regional cells → edge prediction with regional authority.**

### 6.5 Reliability / Scalability / Maintainability (card)

```text
Reliability: atomic commit, idempotent moves, seed replay, RNG version pin
Scalability:  shard sessions, pool boards, regional cells, cache hints
Maintainability: pure engine, golden replays, data-driven levels, flags
```

### 6.6 What to draw first (30s)

```text
Client → Game API → Engine → Redis session
                 ↘ Level config
Move log → Anti-cheat
```

---

## 7. Deeper / Related Interview Questions

### 7.1 Algorithms

**Q1: How do you generate a board with no matches?**  
A: Constructive fill forbidding colors that complete 3 with left/up neighbors; verify; optionally ensure a move.

**Q2: Prove constructive fill prevents matches?**  
A: Horizontal/vertical matches of 3+ must complete at the last placed cell of the run; forbidding that color at placement prevents completion. (Careful with both directions—check left and up as you fill scan order.)

**Q3: How detect all matches including overlaps?**  
A: Mark row runs and col runs; union cells; clear union.

**Q4: Optimize has_any_move?**  
A: Pattern templates around each cell instead of simulating every swap’s full scan.

**Q5: Worst-case cascade complexity?**  
A: O(D×N); cap D; argue N fixed small.

**Q6: How shuffle without immediate matches?**  
A: Re-run generator on playable cells; preserve blockers.

### 7.2 Systems

**Q7: Why not compute cascade only on client?**  
A: Cheat, desync, platform bugs; server is SoT for score.

**Q8: Session store Redis vs DB?**  
A: Redis for hot mutable board; DB for durable progress.

**Q9: Exactly-once moves?**  
A: Idempotency keys + version CAS; at-least-once client retry safe.

**Q10: Hot level start thundering herd?**  
A: Board seed pools; cache level config; shed load.

**Q11: Multi-region progress?**  
A: Player home region; sessions regional; progress replicated async.

### 7.3 Fairness & RNG

**Q12: Can players predict refills?**  
A: If algo+seed known, yes—mitigate by not exposing seed early, or accept for casual.

**Q13: How QA reproduces a bug?**  
A: `(algo_version, seed, moves[])` replay tool.

**Q14: Seeding with user_id only?**  
A: Predictable farming—prefer per-attempt entropy stored server-side.

### 7.4 Anti-cheat

**Q15: Minimal viable anti-cheat?**  
A: Server sim + score bounds + rate limit + sampled replay.

**Q16: Speed hacks?**  
A: Server ignores client dt; animation time ≠ sim time.

**Q17: Memory editors changing lives?**  
A: Lives authoritative in player DB, not client.

**Q18: Bot perfect play?**  
A: Statistical anomaly; soft flags; not needed for MVP correctness.

### 7.5 Product edge cases

**Q19: Allow swap with no match?**  
A: Product call; classic rejects; some modes allow.

**Q20: Moves left vs time levels?**  
A: Engine agnostic; timer is session field checked server-side.

**Q21: Hint fairness (always best move)?**  
A: Return any legal or ranked by immediate score—product.

### 7.6 Estimation drills

**Q22: CPU for 2M moves/s if each cascade 0.05ms?**  
A: 2e6 × 5e-5 = 100 cores order-of-magnitude—plus overhead; plan hundreds of workers.

**Q23: Memory for 5M sessions × 4KB?**  
A: 20 GB (+ replicas).

**Q24: Hint cache hit rate impact?**  
A: Board changes every move → short TTL; still helps multi-hint UI spam.

### 7.7 Alternatives & deal-breakers

**Q25: Store only seed, recompute board from all moves each request?**  
A: Works small depths; becomes CPU heavy—snapshot board each commit.

**Q26: CRDT board for multiplayer?**  
A: Wrong model for turn-ish match-3; use locks/turns.

**Q27: Generative ML boards?**  
A: Overkill; constraints + seed pools suffice.

### 7.8 Interview craft

**Q28: How to open?**  
A: Clarify board rules, cascade, server authority, hints, scale of sessions—not Unity details.

**Q29: What impresses L5+?**  
A: Determinism/replay, constructive gen, version CAS, progressive pools, explicit cheat boundaries.

**Q30: Common mistake?**  
A: Deep Unity animation talk; no API/state; or trusting client scores.

---

### Appendix A — Grid scan for matches

```text
def find_matches(board):
  marked = empty_set()
  # horizontal
  for r in rows:
    run = 1
    for c in 1..C-1:
      if same(board[r][c], board[r][c-1]): run++
      else:
        if run >= 3: mark(r, c-run..c-1)
        run = 1
    if run >= 3: mark(...)
  # vertical analogous
  return marked
```

### Appendix B — Creates match after swap

```text
def creates_match(board, a, b):
  swap(a,b)
  # dirty check around a and b only (optimization)
  ok = match_involving(a) or match_involving(b)
  swap(a,b)
  return ok
```

### Appendix C — Local move patterns (hint)

```text
# Example horizontal: cells A B C D
# Pattern XX_X with X same and blank different → swap blank with neighbor
# Enumerate known match-3 precursor shapes — O(1) per cell
```

### Appendix D — Session Redis schema

```text
HSET sess:{id}
  user, level, seed, rng_off, version, score, moves_left,
  board_b64, status, algo_ver, updated_at
EXPIRE sess:{id} 86400
```

### Appendix E — CAS move Lua sketch

```text
if redis.call('HGET', key, 'version') ~= ARGV[1] then return err end
-- apply board blob, score, version+1
```

### Appendix F — Score bound heuristic

```text
max_delta ≈ cells * max_cascade_depth * max_multiplier * base
if score_delta > max_delta * SAFETY: flag + reject
```

### Appendix G — Progressive scale table

| Scale | Gen | Session | Sim | Anti-cheat |
|-------|-----|---------|-----|------------|
| Baseline | In-request | 1 Redis | In-process | Validate |
| 10× | +metrics | Sharded | Worker pool | Rate limits |
| 100× | Seed pools | Regional | Binary proto | Kafka sample |
| 1,000× | Event pools | Cell fabric | Edge predict | Tiered fleet |

### Appendix H — Level config JSON

```json
{
  "level_id": 105,
  "rows": 9,
  "cols": 9,
  "colors": 6,
  "moves": 25,
  "objective": {"type": "SCORE", "target": 50000},
  "mask": [[1,1,1,...]],
  "require_initial_move": true,
  "specials": false
}
```

### Appendix I — Event list example

```json
{
  "events": [
    {"type": "MATCH", "cells": [[2,3],[2,4],[2,5]], "step": 0},
    {"type": "CLEAR", "cells": [[2,3],[2,4],[2,5]], "step": 0},
    {"type": "FALL", "from": [1,3], "to": [2,3], "step": 0},
    {"type": "SPAWN", "cell": [0,3], "color": 4, "step": 0}
  ]
}
```

### Appendix J — NFR card

```text
Move p99 < 50ms in-region
Gen p99 < 100ms with attempt cap
Deterministic replay
CAS session versions
No client-trusted score
```

### Appendix K — Comparison: rejection vs constructive vs pool

| Property | Rejection | Constructive | Pool |
|----------|-----------|--------------|------|
| Latency tail | Bad | Good | Best |
| Implementation | Easy | Medium | Ops+storage |
| Variety | High | High | Finite seeds |
| Use | Proto | MVP | Scale |

### Appendix L — Gravity column pseudocode

```text
def gravity_column(col):
  stack = [cell for cell in col if is_candy(cell)]
  empties = len(col) - len(stack)
  return [spawn() for _ in range(empties)] + stack
```

### Appendix M — Anti-cheat signals

| Signal | Meaning |
|--------|---------|
| score_delta > bound | Hack / bug |
| moves faster than RTT allows | Bot / script |
| invalid version storm | Client bug / attack |
| seed mismatch | Protocol abuse |
| perfect clear rate outlier | Bot farm |

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Just do it all client-side” | Scores/lives/economy need authority |
| “RNG in the client is fine” | Desync + prediction abuse |
| “Boards can have initial matches” | Breaks genre feel; easy reject in interview if you skip |
| “SQL session per move” | Too slow; use Redis + durable progress |

### Appendix O — Related systems (conceptual)

| System | Relation |
|--------|----------|
| Redis/Memorystore | Sessions |
| Spanner/SQL | Progress, economy |
| Pub/Sub | Move log / telemetry |
| OMS/Config | Levels |
| Edge CDN | Static assets only (not authority) |

### Appendix P — Glossary

| Term | Meaning |
|------|---------|
| Cascade | Chain of match-clear-fall-refill |
| Constructive fill | Place colors avoiding immediate match |
| Legal move | Adjacent swap creating a match |
| Seed | RNG initializer for board+refills |
| Version | Optimistic concurrency token |
| Special | Striped/wrapped/bomb candy |

### Appendix Q — Worked example

```text
Start: constructive 9×9 K=6 → ~0.2ms
Player swap (2,3)-(2,4) → match 3 → clear → fall → spawn → second match → settle
Server: 0.3ms sim; Redis CAS 1ms; total << 50ms
Hint: 120 edge tries × local match check ≈ 0.1ms; cache next hints until version changes
```

### Appendix R — Consistency cheatsheet

| Question | Answer |
|----------|--------|
| Is board strongly consistent? | Yes per session via CAS |
| Cross-device resume? | Read session store; one writer |
| Client prediction divergence? | Snap to server |
| Analytics eventually consistent? | Yes via logs |

### Appendix S — 30m interview checklist

1. Clarify rules: size, colors, cascade, authority, hints.  
2. Invariants: no initial match; legal move definition.  
3. Estimate sessions & moves/s.  
4. Draw API → engine → Redis.  
5. Deep dive gen + cascade + CAS.  
6. Anti-cheat light.  
7. 10×/100×/1,000× pools & regions.  
8. Deal-breakers.

### Appendix T — Idempotent move handler

```text
def handle_move(session_id, client_move_id, swap, version):
  if seen(client_move_id): return prior_result
  sess = load(session_id)
  if sess.version != version: conflict()
  result = engine.apply(sess, swap)
  save_cas(sess, result, version+1)
  remember(client_move_id, result)
  return result
```

### Appendix U — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Shards, CAS metrics, gen attempt caps |
| 100× | Board pools, regional cells, move log |
| 1,000× | Edge predict, tiered anti-cheat, cell fabric |

### Appendix V — Testing matrix

| Test | How |
|------|-----|
| No initial matches | 1e7 random seeds |
| Cascade terminates | Fuzz moves |
| Determinism | Same seed+moves golden |
| Illegal swaps | Property tests |
| Concurrency | Parallel moves same session → one wins |

### Appendix W — Wire size

```text
Board 81 × 1 byte color = 81B (+ types)
Events list atypical 1–3 KB JSON → prefer binary at scale
Move request ~20B + auth
```

### Appendix X — Stuck detection

```text
if moves_left > 0 and not has_move(board):
  status = SHUFFLE_NEEDED
  // auto-shuffle or prompt
```

### Appendix Y — Objective checks

```text
after cascade:
  if objective.satisfied(score, collected, board): WON
  elif moves_left == 0: LOST
```

### Appendix Z — Opening script (interview)

> “I'll design a server-authoritative match-3: generate match-free boards with seeds, validate swaps, simulate cascades deterministically, expose hints, and scale sessions with Redis + regional workers. Out of scope: realtime PvP and full live-ops. Constraints: no client-trusted scores; bounded board gen.”

---

*End of Candy-Crush Board Initialization & Possible Moves system design.*
