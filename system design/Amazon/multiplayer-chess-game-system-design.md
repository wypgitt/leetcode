# System Design: Multiplayer Chess Game (Amazon Games / Twitch-adjacent)

> **Focus areas:** Matchmaking (ELO/Glicko) · Authoritative game server · Rules validation · Clocks · Reconnect · Anti-cheat hooks · Spectating · Concurrent games  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split matchmaking vs move vs spectate load, explicit clock/game invariants, resolved authority ownership  
> **Interview theme:** Amazon SDE III / L6 — **Realtime Games** — fair authoritative chess with Amazon operational ownership

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

Goal: **bound realtime rated chess**—fair matchmaking, server-authoritative rules/clocks, reconnect, spectate, anti-cheat hooks—framed for Amazon Games / Prime Gaming style ownership, not a chat app with a board skin.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Fair realtime chess matches | Generic MMO |
| Planes | Matchmaking vs game authority vs spectate fan-out | Client-authoritative moves |
| Success | Correct rules/clocks + fair ratings | Flashy UX only |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who plays? | Casual + rated; guests optional | Accounts for rated |
| F2 | Modes? | Bullet/blitz/rapid; optional daily | Queues per time control |
| F3 | Matchmaking? | ELO/Glicko-2; expand range | Queue service + rating SoT |
| F4 | Authority? | **Server validates all moves** | Game engine service |
| F5 | Clocks? | Server chess clocks + increment | Never trust client clock |
| F6 | Draw/resign/abort? | Standard policies | Game event state machine |
| F7 | Reconnect? | Resume within timeout | Sticky state; clock policy |
| F8 | Spectating? | Live watch; viral fan-out | Separate path from players |
| F9 | Anti-cheat? | Engine-detection hooks | Telemetry → offline analysis |
| F10 | Chat? | Thin optional | Side channel |
| F11 | Tournaments? | Phase 2 | Arena/swiss on top |
| F12 | Bots/puzzles? | Thin adapter / out of MVP | Same move API |

**MVP functional scope:**

1. Seek game in time-control queue → match by rating → create game.  
2. Authoritative moves (checks, castling, en passant, promotion, repetition/50-move claims).  
3. Server clocks with increment; flag → loss; draw offers; resign; abort policy.  
4. WebSocket realtime; reconnect/resume.  
5. Basic spectate for public games.  
6. Rating update after rated games (ELO or Glicko-2).  
7. Anti-cheat: persist move times + positions for offline analysis; report button.

**Out of MVP:**

- Full tournament platform (Swiss pairing UI)  
- Perfect real-time engine bans (async review OK)  
- 3D boards / mobile offline play sync  
- Variant chess unless asked—hooks via ruleset id  
- Perfect cheat-proofing against all engine users  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Move latency (opponent see)? | Snappy | p50 < 100ms, p99 < 500ms in-region after accept |
| N2 | Clock fairness? | Same rules for both | Server SoT; max clock skew error ≪ increment |
| N3 | Durability? | Finished games never lost | Persist moves before ACK to mover (pick & defend) |
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
| Spectator storm (100K) | Hybrid fan-out; not 100K writes to game shard |
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

### 1.5 Constraints & Assumptions

- Amazon ownership: game authority team pages on clock/desync SEVs; fair-play separate.  
- Twitch-style spectate must not starve player path.  
- Repeat: *“Authoritative chess with rated matchmaking, server clocks, reconnect, and isolated spectate fan-out.”*

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Peak | Notes |
|-------|------|-------|
| Matchmaking seeks | Hundreds–thousands/s | Queues, not game engine |
| Moves | Thousands–millions/s | Single-writer games |
| Spectate | Can dwarf moves | Fan-out / CDN-ish |
| Rating updates | Per finished game | Durable, async OK after result commit |

### 2.2 Active game memory

25K games × ~5KB state ≈ 125 MB—tiny. At 2.5M games ≈ 12.5 GB plus connections—shard.

### 2.3 Move persistence

5M games/day × 60 plies × 100B ≈ 30 GB/day move logs—cheap object/DB hybrid.

### 2.4 Cost levers

- Spectate approximate / snapshot intervals  
- Region cells reduce cross-ocean RTT  
- Shed chat first  
- Offline anti-cheat batching  

Track **$/1K games finished** and **spectate fan-out amplification**.

---

## 3. High-Level Design

### 3.1 Components

1. **Gateway (WS/HTTP)** — auth, route to game home.  
2. **Matchmaking Service** — queues by time control + rating bands.  
3. **Rating Service** — Glicko/ELO SoT.  
4. **Game Authority** — single-writer per game; rules + clocks.  
5. **Presence/Reconnect** — session tokens; state sync.  
6. **Spectate Fan-out** — snapshots + move pubsub; CDN edge optional.  
7. **Persistence** — active state store + durable PGN/event log.  
8. **Anti-cheat Pipeline** — async scoring.  
9. **Admin/Fair-play** — reports, restrictions.  

### 3.2 Game state machine

```text
MATCHED → STARTED → IN_PROGRESS → (CHECKMATE|RESIGN|TIMEOUT|DRAW|ABORT) → RATED?
```

### 3.3 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Authority | Server validates | Client-trusted moves |
| Clocks | Server timestamps | Client clock SoT |
| Spectate | Separate fan-out | Same socket path as players at viral scale |
| Matchmaking | Atomic dequeue | Best-effort multi-match |
| Persist | Move durable before ACK (or defend alternate) | Lossy finished games |

---

## 4. Architecture Diagram

```text
Clients
  |  WS
  v
Edge Gateway --> Matchmaking Queues --> create Game
  |                                      |
  |                                      v
  +------> Game Authority Shard (by game_id)
              |  rules + clocks + single writer
              +--> Persist moves / PGN
              +--> Pub moves --> Spectate Fan-out --> Watchers
              +--> GameOver --> Rating Service
              +--> Telemetry --> Anti-cheat (async)
```

**Region cell (100×+):**

```text
US-EAST | EU-WEST | AP-SOUTH
  each: MM queues, game shards, rating local write with global reconcile policy
Spectate: regional + global amplify for celebrities
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Only server accepts legal moves for the side to move.  
2. Clock flag evaluated with server time against move accept order—documented.  
3. Single writer per `game_id` (lease/actor).  
4. Finished game result durable before rating apply.  
5. Spectate lag never blocks player ACK path.  
6. Rated games require authenticated accounts.  
7. Move log tamper-evident for fair-play.

### 5.2 Matchmaking

Queues keyed by `(time_control, rated?, region)`. Seekers expand rating window over time. Matching uses atomic pop of two compatible seekers (Redis Lua / DB txn). Avoid triple-match by fencing tokens.

### 5.3 Authoritative engine

Server holds FEN + history; validates UCI/SAN moves; handles promotions; detects checkmate/stalemate; verifies claims. Library can be battle-tested rules engine—ownership of versioned ruleset artifact.

### 5.4 Clocks

On move accept: `clock[side] -= (now - turn_started) - lag_comp?; clock[side] += increment`. Lag compensation policy must be fair and abuse-resistant (cap). Flag check before accepting move if time already expired.

### 5.5 Reconnect

Client presents `game_id` + reconnect token; server sends full snapshot (FEN, clocks, offers); clock continued during disconnect per policy (standard online chess).

### 5.6 Spectate scale

Players publish to a game topic; spectate service maintains snapshot + delta stream; for viral games, hierarchical fan-out / edge WS rooms; snapshot every N plies for joiners. **Never** have 100K spectators open direct write interest on the game actor.

### 5.7 Progressive scale

| Jump | Move |
|------|------|
| 10× | Shard games by game_id; Redis active; Kafka analytics |
| 100× | MM band partitions; region cells; spectate pipeline |
| 1,000× | Edge gateways; approx spectate; fair-play platform fleet |

### 5.8 Anti-cheat

Log think times, engine-correlation offline, cloud-engine API abuse signals, multi-account graphs. Provisional restrictions; appeals. Real-time bans rare—false positives are trust SEVs.

### 5.9 Data model sketch

```text
players(player_id, rating_by_tc, provisional)
queues(seek_id, player_id, tc, rating, created)
games(game_id, white, black, tc, state, started_at)
moves(game_id, ply, uci, server_ts, clocks_json)
results(game_id, result, reason, rated)
fairplay_events(...)
```

### 5.10 Security

- Auth tokens short-lived  
- Rate-limit seeks/moves  
- No trust of client legality  
- Spectate authz for private games  
- Abuse: bot farms, rating manipulation  

---

## 6. Wrap-Up

### 6.1 What we designed

Matchmaking, authoritative game shards with clocks, reconnect, durable results/ratings, isolated spectate fan-out, async anti-cheat, progressive region cells.

### 6.2 Key decisions

1. Server authority for moves/clocks  
2. Single-writer game actors  
3. Spectate off player path  
4. Atomic matchmaking  
5. Durable result before rating  
6. Degrade spectate/chat before games  

### 6.3 Risks

- Clock edge races  
- False-positive cheat bans  
- Viral spectate storms  
- Cross-region fairness  
- Matchmaking deadzones at rating extremes  

### 6.4 Closer

> **Multiplayer Chess Game**: authoritative rules/clocks, fair matchmaking, reconnect, spectate isolation, ownership, progressive scale, customer trust (fair play).

---

## 7. Deeper / Related Interview Questions — Multiplayer Chess

**Q1. Why not let clients validate moves for speed?**

**A:** Cheating and desync. Server authority is non-negotiable for rated play.

**Q2. How do you handle move that arrives as flag falls?**

**A:** Define total order with server_ts; typically flag checked at evaluation instant; document and golden-test.

**Q3. Spectate 1M viewers on a championship game?**

**A:** Hierarchical pubsub / edge rooms / HLS-like snapshot+delta; player shard untouched.

**Q4. Glicko vs ELO?**

**A:** Glicko-2 models RD; mention confidence; either OK if consistent and durable.

**Q5. Where is game state stored?**

**A:** In-memory actor + Redis/hot store; durable event log for recovery and PGN.

**Q6. Abort vs resign?**

**A:** Policy by plies/time; rating impact differs; server enforces.

**Q7. Daily/correspondence games?**

**A:** Different clock service (calendar); not hot WS shard forever—wake on move.

**Q8. Deal-breaker?**

**A:** Client-authoritative clocks/moves; or spectate load on the game writer path.


## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + Amazon ownership lens |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive (reliability/scale/trust) |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact; lock MVP; split load classes; name pager owners; refuse deal-breakers.

---

## 10. Operability

### Golden signals
Latency, traffic, errors, saturation, freshness/backlog, trust incidents.

### Rollback ladder
Flag off → revert artifact → shed/reduce load → cell isolate → postmortem with trust section.

### Kill switches
Disable optional stage; freeze nearline; revert pointer; shed traffic; isolate cell/tenant.

### Security/privacy baseline
Authn/z, PII TTLs, encryption, cell isolation, signed artifacts, abuse limits, audit trails.

### Cost worksheet
Dominant cost driver; fastest unit-cost lever; 10× cost with/without architectural jump.

```text
instances ≈ peak_QPS × cpu_sec / (cores × util)
```

### Progressive scale
10× cache/shard/async; 100× cells/partition/edge; 1,000× approximate/platform/multi-tenant cells.

### Cross-team deps
Identity, catalog/inventory, payments, notifications, experimentation, logging — each with failure mitigation.

## More Interview Q&A — Multiplayer Chess Game

**Q1. Where do you put WebSocket sticky sessions?**

**A:** Sticky to region + game home; reconnect tokens survive node loss via shared state.

**Q2. How to test clock fairness?**

**A:** Deterministic virtual clock in unit tests; chaos network delay integration tests.

**Q3. Cheating with engine on another device?**

**A:** Hard; statistical detection + reports; don’t promise perfect.

**Q4. Correspondence storage?**

**A:** Cold state in DB; wake on move; not hot Redis forever.

**Q5. Rating inflation?**

**A:** Pool monitoring; provisional periods; activity requirements.

**Q6. Why Kafka for moves?**

**A:** Analytics/anti-cheat; not the primary ACK path—actor memory/Redis first.

**Q7. Can spectators see chat?**

**A:** Policy; moderate; separate channel.

**Q8. How to handle illegal castle attempt?**

**A:** Reject; no time pause; optional warn.

**Q9. Multi-board puzzles?**

**A:** Different product; share rules lib only.

**Q10. Cross-region match?**

**A:** Higher RTT; prefer regional MM; show latency warning.

**Q11. Exactly-once rating?**

**A:** Idempotent by game_id unique constraint.

**Q12. What’s a deal-breaker again?**

**A:** Client-trusted clocks/moves; spectate on writer.

**Q13. Prime Gaming entitlement?**

**A:** Entitlement service gate for cosmetics/modes; not on move path.

**Q14. How big is a move message?**

**A:** Tens–hundreds of bytes; batch rare.

**Q15. Abort griefing?**

**A:** Limit aborts; rating penalties; detection.

**Q16. Observability top panel?**

**A:** move_p99, mm_wait_p95, reconnect_success, spectate_lag, rating_apply_lag.

## Deep Technical Addenda — Multiplayer Chess Game


### Game actor pattern

Each game is an actor with a mailbox. Commands: Move, Resign, OfferDraw, ClaimDraw, Abort, TickFlag. TickFlag scheduled via timer wheel keyed by soonest clock expiry.

### Persistence strategy

Write-ahead move log (Redis stream / Kafka / DB) before ACK—or ACK after memory+async with repair (harder to defend for rated). Prefer WAL-before-ACK for rated blitz+.

### Matchmaking banding

```text
tc=blitz → bands by rating floors; overflow to adjacent bands as wait grows
```

Avoid one giant sorted set hotspot at 1,000×—partition bands.

### Spectate protocol

1. Join → latest snapshot (FEN, ply, clocks approx)  
2. Subscribe deltas  
3. Periodic keyframes for late joiners  
4. Drop chat under load  

### Fair-play scoring

Features: move match to engine top lines, timing regularity, opponent strength, account graph. Human review for bans; automatic only for clear automation.

### Amazon angle

Relate to Twitch spectate lessons and Amazon Games platform cells: title-specific game logic, shared gateway/matchmaking platform optional.


## Tradeoff Matrices — Multiplayer Chess Game

### Consistency vs latency

| Choice | Latency | Correctness | Use when |
|--------|---------|-------------|----------|
| Sync durable then serve | Higher | Stronger | Money/trust/enforcement paths |
| Serve then async durable | Lower | Risk window | Non-money UX with repair |
| Cached eventual | Lowest | Stale OK | Read-heavy dashboards / portals |

### Exact vs approximate

| Choice | Cost | UX risk | Use when |
|--------|------|---------|----------|
| Exact | High at scale | Low confusion | Checkout, ledger, rating |
| Approximate labeled | Lower | Need UX copy | Analytics, spectate fan-out |
| Hierarchical | Medium | Ops complexity | Multi-region aggregates |

### Availability vs correctness

| Choice | Availability | Correctness | Use when |
|--------|--------------|-------------|----------|
| Fail closed | Lower during dep outage | Safer trust | Fraud, consent, money |
| Fail open degrade | Higher | Risk wrong UX | Optional personalization |
| Shed load | Partial | Protects core | Peak storms |

## Operability Addenda — Multiplayer Chess Game

### Deploy pipeline

```text
build artifact → static validation → shadow → canary → bake → full
                     ↓ fail              ↓ guardrail fail
                  reject              auto rollback
```

### Guardrail examples

- p99 latency regression > threshold  
- error/empty/fallback rate rise  
- safety/privacy/trust denials anomaly  
- cost/unit-economics spike  
- backlog/DLQ growth beyond budget  

### Kill switches (name them in interview)

1. Disable optional stage / feature flag  
2. Freeze nearline updates  
3. Revert artifact pointer / config version  
4. Shed traffic / reduce concurrency / reduce K  
5. Cell isolation / pause tenant or marketplace  

### Oncall first five minutes

1. Check golden signals and recent deploys  
2. Confirm blast radius (cell / marketplace / tenant)  
3. Engage kill switch if customer-trust burning  
4. Preserve evidence (logs, samples, config versions)  
5. Customer messaging path if trust incident  

### Cost worksheet

Speak: peak demand → per-node capacity → headroom 2–3× → cache/async/edge lever → what 10× does → architectural jump that bends the curve.

## Worked Capacity Narrative — Multiplayer Chess Game

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/async/edge lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Multiplayer Chess Game

Amazon interviews reward explicit trust reasoning: wrong charges, undelivered critical mail, broken promotions, unfair games, privacy leaks, or silent data loss are not “ops issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Multiplayer Chess Game

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, partitioned queues, edge/client head  
- **1,000×:** platform multi-tenant cells, approximate algorithms, specialized fleets  

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Multiplayer Chess Game
### S1. Ruleset versioning

Pin engine/rules artifact; canary carefully.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Lag compensation

Capped; anti-abuse; fairness statement.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Queue fairness

Expand windows; prevent infinite wait; bots separate.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Presence

Heartbeats; disconnect timers; ghost seats.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Draw offers

State flags; one outstanding offer; cancel on move.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Threefold detection

Server hash history; claim or auto.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Bullet special cases

Tighter lag caps; higher move QPS planning.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Tournament hooks

External pairing feeds game create API.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S9. Bot adapters

Same API; marked unrated/bot pools.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S10. Chat moderation

Async; report; not on move path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S11. Observability

Move p99, MM wait, reconnect success, spectate lag, rating lag.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S12. Chaos

Kill game shard mid-game; reconnect storm; spectate amplify.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S13. Data residency

Region cells for player PII; game logs policy.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S14. Abuse farming

Multi-account; sandbagging; rate limits.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S15. Platformization

Shared realtime game platform; chess as title cell.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S16. Twitch integration

Optional broadcast sink from spectate pipeline.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Interview Cards — Multiplayer Chess Game

### Card 1: Server authority

All moves/clocks validated server-side; clients are views.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 2: Single-writer game

Actor/lease per game_id; no multi-master board state.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 3: Clock invariant

Server timestamps; documented flag-vs-move ordering; golden tests.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 4: Atomic matchmaking

Fenced dequeue of two seekers; one game created.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 5: Reconnect snapshot

Token + full state sync; clock policy explicit.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 6: Spectate isolation

Fan-out pipeline; hierarchical rooms; never block players.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 7: Durable result

Persist terminal result before rating mutation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 8: Rating SoT

Dedicated service; idempotent apply by game_id.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 9: Anti-cheat async

Telemetry pipeline; provisional actions; appeals.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 10: Region cells

Match locally when possible; RTT fairness.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 11: Idempotent moves

ply/move_id dedupe; illegal rejected without pause abuse.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 12: Degradation order

Chat → spectate quality → MM expand → never silent wrong results.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 13: PGN immutability

Append-only move log; fair-play evidence.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 14: Cost lever #1

Approximate spectate + shed chat; region localize.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 15: Deal-breaker

Client clocks; spectate on game writer; lossy finished games.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

### Card 16: SEV definition

Wrong rated result or mass clock desync = trust SEV.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for multiplayer chess.

## Related Deep Dive Q&A — Multiplayer Chess Game

**RQ1. Why does 'Server authority' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Server authority'. Name who pages and what artifact version you roll back.

**RQ2. How would you test 'Server authority' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Server authority'.

**RQ3. What regresses if 'Server authority' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Server authority'.

**RQ4. Why does 'Single-writer games' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Single-writer games'. Name who pages and what artifact version you roll back.

**RQ5. How would you test 'Single-writer games' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Single-writer games'.

**RQ6. What regresses if 'Single-writer games' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Single-writer games'.

**RQ7. Why does 'Clock fairness' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Clock fairness'. Name who pages and what artifact version you roll back.

**RQ8. How would you test 'Clock fairness' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Clock fairness'.

**RQ9. What regresses if 'Clock fairness' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Clock fairness'.

**RQ10. Why does 'Atomic matchmaking' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Atomic matchmaking'. Name who pages and what artifact version you roll back.

**RQ11. How would you test 'Atomic matchmaking' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Atomic matchmaking'.

**RQ12. What regresses if 'Atomic matchmaking' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Atomic matchmaking'.

**RQ13. Why does 'Reconnect' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Reconnect'. Name who pages and what artifact version you roll back.

**RQ14. How would you test 'Reconnect' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Reconnect'.

**RQ15. What regresses if 'Reconnect' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Reconnect'.

**RQ16. Why does 'Spectate fan-out' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Spectate fan-out'. Name who pages and what artifact version you roll back.

**RQ17. How would you test 'Spectate fan-out' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Spectate fan-out'.

**RQ18. What regresses if 'Spectate fan-out' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Spectate fan-out'.

**RQ19. Why does 'Rating durability' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Rating durability'. Name who pages and what artifact version you roll back.

**RQ20. How would you test 'Rating durability' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Rating durability'.

**RQ21. What regresses if 'Rating durability' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Rating durability'.

**RQ22. Why does 'Anti-cheat' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Anti-cheat'. Name who pages and what artifact version you roll back.

**RQ23. How would you test 'Anti-cheat' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Anti-cheat'.

**RQ24. What regresses if 'Anti-cheat' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Anti-cheat'.

**RQ25. Why does 'Region cells' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Region cells'. Name who pages and what artifact version you roll back.

**RQ26. How would you test 'Region cells' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Region cells'.

**RQ27. What regresses if 'Region cells' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Region cells'.

**RQ28. Why does 'Idempotent moves' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Idempotent moves'. Name who pages and what artifact version you roll back.

**RQ29. How would you test 'Idempotent moves' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Idempotent moves'.

**RQ30. What regresses if 'Idempotent moves' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Idempotent moves'.

**RQ31. Why does 'PGN evidence' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'PGN evidence'. Name who pages and what artifact version you roll back.

**RQ32. How would you test 'PGN evidence' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'PGN evidence'.

**RQ33. What regresses if 'PGN evidence' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'PGN evidence'.

**RQ34. Why does 'Degrade order' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Degrade order'. Name who pages and what artifact version you roll back.

**RQ35. How would you test 'Degrade order' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Degrade order'.

**RQ36. What regresses if 'Degrade order' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Degrade order'.

**RQ37. Why does 'Lag compensation' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Lag compensation'. Name who pages and what artifact version you roll back.

**RQ38. How would you test 'Lag compensation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Lag compensation'.

**RQ39. What regresses if 'Lag compensation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Lag compensation'.

**RQ40. Why does 'Bullet scale' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Bullet scale'. Name who pages and what artifact version you roll back.

**RQ41. How would you test 'Bullet scale' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Bullet scale'.

**RQ42. What regresses if 'Bullet scale' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Bullet scale'.

**RQ43. Why does 'Tournament hooks' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Tournament hooks'. Name who pages and what artifact version you roll back.

**RQ44. How would you test 'Tournament hooks' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Tournament hooks'.

**RQ45. What regresses if 'Tournament hooks' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Tournament hooks'.

**RQ46. Why does 'Unit cost' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Unit cost'. Name who pages and what artifact version you roll back.

**RQ47. How would you test 'Unit cost' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Unit cost'.

**RQ48. What regresses if 'Unit cost' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Unit cost'.

## Narrative Walkthrough — Multiplayer Chess Game

### Walkthrough beat 1

Player A seeks blitz 3+2. Matchmaking expands ±100 rating over 10s, atomically pairs with B, creates game on shard H(game_id). Both receive start snapshot with clocks. Call out MM vs game ownership boundary.

### Walkthrough beat 2

Moves flow: client → gateway → game actor validates → persist ply → ACK mover → push opponent → publish spectate topic. If actor host dies, lease failover rebuilds from event log; clocks continue from durable turn_started.

### Walkthrough beat 3

Championship game goes viral: spectate service spins hierarchical rooms; player p99 unchanged. After mate, result durable, rating applied idempotently, anti-cheat job enqueued. Mention shed chat if needed.

## Scenario Runbooks — Multiplayer Chess Game

### SEV: mass clock desync after deploy

1. Revert clock/rules artifact immediately.
2. Pause rated MM if results untrustworthy.
3. Quarantine affected games; manual/fair-play review.
4. Golden-test flag-vs-move cases in CI.

### Matchmaking creates duplicate games

1. Halt MM; inspect fencing tokens.
2. Abort extras without rating; notify players.
3. Fix atomic dequeue; add invariant metric.

### Spectator storm melts game shard

1. Confirm spectators not on writer path—if bug, emergency disconnect watchers.
2. Route spectate to fan-out only.
3. Capacity postmortem on amplification.

## Appendices — Multiplayer Chess Game

### A — Glossary
| Term | Meaning |
|------|---------|
| Cell | Failure-isolated unit (marketplace/region/tenant) |
| Nearline | Minutes-latency path |
| Canary | Partial bake of artifact |
| Deal-breaker | Non-negotiable bad design |
| Two-pizza | Ownership team with pager |
| SoT | Source of truth |
| DLQ | Dead-letter queue |
| PIT | Point-in-time (features/state) |
| FEN | Forsyth–Edwards Notation board state |
| PGN | Portable Game Notation |
| Glicko-2 | Rating system with rating deviation |
| Single-writer | One authority process/lease per game |
| Fan-out | Spectate distribution path |

### B — Oncall checklist
- [ ] SLOs green / error budget known
- [ ] Rollback armed
- [ ] Kill switches known
- [ ] Cost dashboards
- [ ] Privacy/safety/trust tested
- [ ] DLQ/backlog within budget
- [ ] Recent deploys identified

### C — Topic closer checklist
- [ ] Server-authoritative moves/clocks
- [ ] Single-writer game actors
- [ ] Atomic matchmaking
- [ ] Spectate isolated from players
- [ ] Durable results before ratings
- [ ] Progressive 10×/100×/1,000×

### D — Metric dictionary (speak these)

| Metric | Why it matters |
|--------|----------------|
| p99 latency by class | Split interactive vs async |
| Error / reject rate | Customer pain |
| Backlog age / DLQ depth | Hidden debt |
| Unit cost ($/1K ops) | Frugality |
| Trust incident count | Leadership principle signal |
| Cache hit rate | Scale lever |
| Cell saturation | Isolation health |

### E — Failure injection catalog

| Inject | Expect |
|--------|--------|
| Dependency timeout | Deadline shed / fallback |
| Dual publish / retry storm | Idempotent no double effect |
| Hot partition | Reshard / isolate |
| Clock skew | Bounded error or fail closed |
| Region loss | Cell failover story |
| Poison message | DLQ, not partition death |

### F — Amazon leadership-principle hooks

| Principle | How it shows in this design |
|-----------|------------------------------|
| Customer Obsession | Explicit trust fail-closed/open |
| Ownership | Named two-pizza + pager |
| Invent & Simplify | Prefer fewer planes with clear contracts |
| Frugality | Unit-cost levers before linear scale-out |
| Dive Deep | Metrics + invariants + runbooks |
| Bias for Action | Kill switches and rollback ladder |
| Earn Trust | Auditability, no silent money/promo bugs |

### G — One-breath closer

> **Multiplayer Chess Game**: explicit planes, SLOs, ownership, progressive scale (10×/100×/1,000×), customer trust, unit economics.

---

## Extra Drill Tables — Multiplayer Chess Game

### Load class split (say this early)

| Class | Example | SLO style | Consistency |
|-------|---------|-----------|-------------|
| Interactive read | Browse / status | Tight p99 | Eventual often OK |
| Interactive write | Checkout / move / reserve | Tight + correct | Stronger |
| Async | Email send / analytics | Freshness budgets | At-least-once |
| Control plane | Config / templates / rules | Correct rollout | Versioned artifacts |

### Ownership RACI sketch

| Concern | Responsible | Accountable | Consulted |
|---------|-------------|-------------|-----------|
| Serving path | Owning service team | Eng manager / PE | Dep teams |
| Trust policy | Safety/privacy/fraud | Director-level policy | Legal |
| Cost | Owning team | Sr. leadership | Capacity |
| Incident | Primary oncall | Secondary / IC | Comms |

### Progressive scale interview lines (memorize)

| Jump | Line to say |
|------|-------------|
| 10× | “Cache, shard, async offload, and budgets—not just more boxes.” |
| 100× | “Cells and partitioned queues; isolate blast radius by marketplace/tenant.” |
| 1,000× | “Approximate where labeled, platformize shared fleets, specialize hot paths.” |

### Anti-patterns whiteboard list

| Anti-pattern | Why it fails Amazon bar |
|--------------|-------------------------|
| One shared FIFO for all classes | Priority inversion / trust SEVs |
| Client as source of truth | Fraud + desync |
| Silent money/promo repair | Earn Trust violation |
| Global mega-model/mega-DB | Blast radius + ownership soup |
| Linear scale-only story | Misses frugality / invent & simplify |

### Sample metric alerts

| Alert | Severity hint |
|-------|---------------|
| Core p99 burn 15m | Page |
| Trust invariant flip | Page immediately |
| DLQ growth 3× baseline | Ticket → page if txn class |
| Unit cost +40% week | Capacity review |
| Cell imbalance | Rebalance job |

### Design review checklist (L6)

- [ ] Load classes split with numbers
- [ ] Invariants written as tests
- [ ] Fail-closed vs fail-open named
- [ ] Kill switches named
- [ ] 10×/100×/1,000× jumps named
- [ ] Deal-breakers refused
- [ ] Two-pizza owners named
- [ ] Customer-trust SEV defined

*End of Multiplayer Chess Game system design prep doc.*
