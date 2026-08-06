# System Design: Boggle Solver (Puzzle Service)

> **Focus areas:** Trie + DFS board search · Board generation · Multiplayer / API service · Scale puzzle serving + solve · Fairness & anti-cheat  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct DFS/trie pruning, precompute vs online solve tradeoffs, deal-breakers for “spawn unbounded CPU per HTTP request” fantasies  
> **Interview theme:** Google L5+ algorithmic service — classic Boggle search packaged as a scalable multiplayer puzzle platform with clear CPU isolation

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

Goal: **bound the product**—a **Boggle-like puzzle platform** that generates boards, validates/finds words via trie-guided DFS, serves multiplayer rounds over APIs, and scales both **puzzle serving** and **solve compute** without melting the fleet on pathological boards.

### 1.0 What this is / is not

| Dimension | **Boggle solver / puzzle service (this doc)** | Not this |
|-----------|-----------------------------------------------|----------|
| Primary job | Generate boards, solve/validate words, run rounds | General Scrabble AI / NLP |
| Success | Correct dictionary words; fair timed rounds; low latency UX | Unbounded exhaustive search as user-facing sync API |
| Algorithm | Trie + DFS with visited prune | Naive permute all paths without trie |
| Multiplayer | Shared board rounds, scores | Full MMO world |
| Scale | Many concurrent games + solve QPS | Single offline script |

**Scope statement:** Design a Boggle solver service: trie DFS, board generation, multiplayer/API, scaling puzzle serving and solve throughput—with progressive scale and CPU isolation.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Board size? | 4×4 classic; optional 5×5 | Config; complexity ↑ fast |
| F2 | Dictionary? | English ENABLE/SOWPODS-like; multi-lang later | Versioned dict + trie |
| F3 | Solve API? | Return all words OR validate player word | Two endpoints |
| F4 | Scoring? | Boggle lengths; optional rarity | Score service |
| F5 | Multiplayer? | Timed rounds; same board; live scores | Room / match service |
| F6 | Board gen? | Fair dice / letter freqs; seedable | Generator + difficulty |
| F7 | Min word len? | 3+ | Filter |
| F8 | Qu / special tiles? | Optional Qu as one tile | Tile model |
| F9 | Anti-cheat? | Server authoritative validation | Never trust client word list |
| F10 | Spectate / replay? | Phase 1.5 | Event log |
| F11 | Solo practice? | Yes | Same solve path |
| F12 | Leaderboards? | Daily boards | Precomputed solutions |

**MVP functional scope:**

1. Versioned dictionary → build trie.  
2. Generate seedable 4×4 boards with letter distribution.  
3. `POST /solve` (internal/precompute) → all words + scores.  
4. `POST /validate` player submission path-aware or word-in-solution.  
5. Multiplayer room: create/join, start timer, submit words, final score.  
6. Precompute solutions for published daily/competitive boards.  
7. Rate-limit online solve; isolate CPU workers.  
8. Auth users; persist match history summary.

**Out of MVP:**

- Full cheat ML vision detecting phone dictionaries (mention)  
- Arbitrary N×N (N≥6) online sync solve without precompute  
- Crossword/anagram all word games  
- User-uploaded custom dictionaries without moderation hooks

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Solve correctness | All dictionary words on board | Golden tests vs brute |
| N2 | Validate latency | Instant feel | p99 < 50–100ms |
| N3 | Full solve latency | Precompute OK seconds; online bounded | Worker budget e.g. < 200ms 4×4 |
| N4 | Round sync | Fair start | Server clock start_at |
| N5 | Availability | Games continue | Stateless solve workers + durable rooms |
| N6 | Fairness | Same board/solution dict version | Pin dict_version on match |
| N7 | Abuse | CPU DoS protection | Queues, caps, auth |
| N8 | Scale | Many concurrent rooms | Shard by room_id |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Solo: generate board → client plays → validate each word → score.  
2. Daily: midnight publish board + precomputed solution set → millions fetch.  
3. Multiplayer: 4 players join → countdown → submit → end → rankings.  
4. Admin regenerates dict v2 → new matches pin v2; old continue v1.  
5. Practice “hint” uses precomputed remaining words.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate word submit | Score once |
| Word not on board | Reject |
| Word not in dict | Reject |
| Path reuse cell | Invalid if rules require unique cells |
| Pathological board | Worker timeout; fall back precompute-only |
| Dict mismatch client | Server authoritative |
| Late submit after round | Reject by server time |
| Room partition | Sticky room owner / Redis state |
| Seed collision | Include salt / UUID board_id |
| Cheaters with full list | Rate limit; detect superhuman rates; optional delay reveal |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 100K | 1M | 10M | 100M |
| Concurrent rooms | 5K | 50K | 500K | 5M |
| Validate QPS | 2K | 20K | 200K | 2M |
| Full solve QPS (online) | 50 | 200 | 500 | precompute-heavy |
| Daily board fetches | 100K | 1M | 10M | 100M |
| Dict size words | 200K | 200K–1M | multi-lang | multi-lang |
| Board size | 4×4 | 4×4/5×5 | mix | mix |
| Worker cores (solve) | 20 | 100 | 500 | cell fleets |

**What each jump forces:**

- **10×:** Precompute competitive boards; validate via hashset of solutions; Redis rooms.  
- **100×:** Edge CDN for daily puzzles; room shards; solve only async/internal.  
- **1,000×:** Regional cells; almost no sync full-solve API; massive read path caching.

### 1.5 Etc. (Constraints & Assumptions)

- Ambiguity: is “solver” a **library interview** or **multiplayer product**? Provide both—algorithm core + service wrap.  
- Rules: 8-direction adjacency; no cell reuse per word (classic).  
- Dictionary licensing matters in real life—version & attribution.  
- Client may run offline helper; **server validates** for ranked play.

**Scope statement to repeat back:**

> Design a Boggle puzzle platform with trie-guided DFS solving, seedable board generation, authoritative validation, multiplayer timed rounds, and scale via precomputed solutions + sharded rooms—protecting workers from unbounded solve CPU.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Board fetch** | Daily/static | high read | CDN |
| **Validate word** | During rounds | 2K QPS | Stateless API + solution set |
| **Full solve** | Gen/admin/practice | low | Worker pool |
| **Room events** | Join/submit/score | bursty | Room shard / Redis |
| **Matchmaking** | Optional | medium | Queue |
| **Leaderboard** | End of day | burst | Preagg |

**Anti-pattern:** every validate recomputes full DFS.

### 2.2 DFS complexity

```text
4×4: 16 cells; path length ≤16; branching ≤7 after first
Worst naive exponential; trie prunes aggressively
Typical English dict solve 4×4: sub-ms to tens of ms in C++/Go
5×5: significantly harder — budget carefully
6×6 online sync: often deal-breaker without heavy optimize/precompute
```

### 2.3 Memory

```text
200K words × avg 5 chars → ~1MB raw
Trie nodes: often tens of MB depending on impl — fine per worker
Solution set per board: ~100–1000 words → few KB
1M precomputed boards × 5KB = 5GB — OK object store + cache hot
```

### 2.4 Multiplayer bandwidth

```text
5K rooms × 4 players × submit 1 word / 5s = 4K validates/s order
Score broadcast: coalesce to 2–5 Hz / room not per keystroke
```

### 2.5 Daily puzzle thundering herd

```text
10M users fetch daily at 00:00 local staggered by TZ
CDN cache board JSON + solution hash metadata
Origin nearly idle
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/boards` | `{size, dict_version, seed?}` → board_id, grid |
| `GET /v1/boards/{id}` | Grid + meta (no full solution in ranked) |
| `POST /v1/boards/{id}/solve` | Internal/admin; returns words (authz) |
| `POST /v1/boards/{id}/validate` | `{word, path?}` → accept/score |
| `POST /v1/rooms` | Create multiplayer room |
| `POST /v1/rooms/{id}/join` | Join |
| `POST /v1/rooms/{id}/start` | Pin board + start_at |
| `POST /v1/rooms/{id}/submit` | Word submit during round |
| `GET /v1/rooms/{id}` | State/scores |
| `GET /v1/daily/{date}` | CDN-friendly daily |

**Board schema:**

```text
Board {
  board_id,
  size,
  grid: [[tile]],  // tile may be "Qu"
  dict_version,
  seed,
  solution_id,     // points to precomputed set
  difficulty
}
```

### 3.2 Data model

| Entity | Key | Notes |
|--------|-----|-------|
| Dictionary | `dict_version` | word list artifact |
| Trie artifact | `dict_version` | built binary |
| Board | `board_id` | grid + seed |
| SolutionSet | `solution_id` | set/map word→paths/score |
| Room | `room_id` | players, board, timers, scores |
| Submission | `(room, user, word)` | unique |
| UserStats | `user_id` | ratings |

### 3.3 Algorithm — Trie + DFS

```text
Build trie from dictionary (with word-end flags)
For each start cell (r,c):
  DFS:
    if node null: return
    mark visited
    if node.word_end and len>=min: add word
    for each neighbor 8-dir not visited:
      DFS(neighbor, node.child[letter])
    unmark visited
```

**Pruning & speedups:**

| Technique | Effect |
|-----------|--------|
| Trie prune | Early stop dead prefixes |
| Visited bitmask (16-bit 4×4) | Faster than matrix |
| Max length cap | Bound depth |
| Prefix frequency order | Minor |
| Parallel starts | Multi-core solve workers |
| Precompute | Avoid online DFS entirely for ranked |

**Deal-breaker:** generating all strings without dictionary prune.

### 3.4 Validate — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **Full DFS per validate** | No storage | CPU waste/DoS | Tiny scale |
| **Solution hashset** | O(1) word check | Needs precompute | **Ranked MVP** |
| **Path verify + dict** | Catches path cheats | Slightly more CPU | If path required |
| **Client honor system** | Cheap | Cheating | Never ranked |

**Chosen:** Precompute `SolutionSet` for match boards; validate word ∈ set (+ optional path check). Online DFS only for sandbox tools with strict quotas.

### 3.5 Board generation — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| **Physical Boggle dice** | Authentic | Limited variety |
| **Letter frequency sample** | Controllable difficulty | May create barren boards |
| **Rejection sampling** | Ensure min words / score | Gen cost |
| **Handcrafted daily** | Editorial quality | Not scalable alone |

**Chosen MVP:** dice or frequency model + **reject** if `word_count < T` or `> U` (too dense); store seed for reproducibility.

### 3.6 Multiplayer model

```text
Room states: LOBBY -> COUNTDOWN -> RUNNING -> SCORING -> DONE
On start: pick board with precomputed solution; pin dict_version
Clients sync to server start_at (UTC)
Submit words -> validate -> add score if new for user
End: finalize leaderboard; persist summary
```

### 3.7 Why X over Y (summary table)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Ranked validate | Precomputed set | Latency + CPU | DFS per submit at 200K QPS |
| Solve workers | Async/internal | Isolation | Unbounded sync solve in API pods |
| Dict | Version pinned | Fairness | Hot-swap mid-match |
| Rooms | Shard by room_id | Scale | Global lock all games |
| Daily | CDN | Read scale | Origin generate per user |
| Paths | Optional verify | Anti-cheat tier | Require heavy path search always |

---

## 4. Architecture Diagram

```text
  Clients ---> Edge/CDN (daily boards)
                 |
                 v
          +------+------+
          | API Gateway |
          +--+---+----+-+
             |   |    |
             v   v    v
        Roomsvc  Validate  Matchmaking
             |   | 
             v   v
        +----+---+----+     +------------------+
        | Redis/Memory|     | Solution Store   |
        | room state  |     | (board solutions)|
        +------+------+     +---------+--------+
               |                      ^
               |                      | write
               v                      |
        +------+------+      +--------+---------+
        | Match DB    |      | Solve Workers     |
        | history     |      | Trie DFS pool     |
        +-------------+      +--------+---------+
                                      ^
                                      | dict artifacts
                               +------+------+
                               | Dict Builder|
                               +-------------+
```

**Solve worker path:**

```text
BoardCreated / DailyJob
  -> enqueue SolveJob(board_id)
  -> worker loads trie(dict_version)
  -> DFS find all words
  -> write SolutionSet
  -> mark board READY
```

**Validate path:**

```text
submit(word)
  -> normalize
  -> if now > end_at: reject
  -> if word in SolutionSet and not seen(user,word):
       score += points(word); broadcast delta
```

**Multiplayer timeline:**

```text
create room -> join -> start (board READY required)
countdown 3s -> running 180s -> scoring freeze -> results
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Ranked match never starts** without `SolutionSet` READY.  
2. **dict_version immutable** for a match lifetime.  
3. **Server time** gates accepts.  
4. **Unique (user, word)** scoring.  
5. **Solve workers idempotent** on `board_id`.  
6. **Trie build checksum** matches dict artifact.

#### 5.1.2 CPU DoS controls

```text
- Auth + rate limits on /solve
- Queue with max depth; 429 when full
- Per-job timeout (e.g. 200ms 4×4, 1s 5×5)
- Separate worker deployment from latency-sensitive API
- Circuit break online solve; degrade to precomputed-only
```

**Deal-breaker:** sharing thread pool between validate and full DFS solve.

#### 5.1.3 Correctness testing

| Test | Purpose |
|------|---------|
| Golden boards | Known word lists |
| Brute cross-check small dict | Completeness |
| Property: every solution word has ≥1 valid path | Consistency |
| Random fuzz boards | Crashes/timeouts |
| Unicode / Qu tiles | Edge letters |

#### 5.1.4 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Slow solve blocks API | Separate workers |
| 10× | Redis room hotspot | Shard rooms; hash tags |
| 100× | Daily herd | CDN + TZ stagger |
| 1,000× | Multi-lang tries memory | Locale-sharded workers |

### 5.2 Scalability

#### 5.2.1 Partitioning

| Key | Purpose |
|-----|---------|
| `room_id` | Multiplayer state |
| `board_id` | Solutions |
| `dict_version` + locale | Trie workers |
| Daily `date+locale` | CDN keys |

#### 5.2.2 Precompute strategy

```text
Competitive / daily / room boards: always precompute
Custom "random practice":
  - try solve async; client plays validate against result when ready
  - or use large pool of READY boards served randomly (better)
At 100×+: serve from READY pool; rarely solve online
```

#### 5.2.3 Validate scale

```text
SolutionSet in Redis/Memorystore as HashSet
OR bloom + exact secondary (careful false positive → exact check)
For daily: edge returns board; validates hit regional Redis
```

#### 5.2.4 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Solution-set validate; worker pool; Redis rooms |
| →100× | CDN daily; room shards; READY board pool |
| →1,000× | Regional cells; locale tries; almost no online solve |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
rules: {min_len: 3, directions: 8, reuse_cell: false}
scoring: {3:1,4:1,5:2,6:3,7:5,8+:11}
round_seconds: 180
solve_timeout_ms: {4:200, 5:1000}
reject_gen: {min_words: 20, max_words: 400}
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `solve_latency_ms` | Worker health |
| `solve_timeouts` | Pathological |
| `validate_qps` | Play load |
| `room_active` | Capacity |
| `cheat_suspect_rate` | Words/sec outliers |
| `dict_version_in_use` | Fairness |

#### 5.3.3 Operability

- Blue/green dict versions.  
- Rebuild solutions job if scorer changes.  
- Ban boards with offensive words (filter solution list).  
- Feature flag path verification.

---

## 6. Wrap-Up

### 6.1 What we designed

A **Boggle puzzle platform** centered on **trie-guided DFS** for solving, **seedable board generation** with quality rejection, **precomputed solution sets** for authoritative validation, multiplayer rooms with server time, and scaled read/validate paths—without running unbounded DFS on the request path.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Algorithm | Trie + DFS + visited |
| Ranked validate | Precomputed set |
| Online solve | Isolated workers + timeout |
| Multiplayer | Server authoritative |
| Scale | CDN + READY pools |
| 5×5/6×6 | Precompute / careful budgets |

### 6.3 30-second scale narrative

> Baseline: trie DFS workers precompute solutions; API validates via sets; Redis rooms. 10× hard-separates solve CPU and expands READY pools. 100× CDNs daily puzzles and shards rooms. 1,000× is regional cells with almost zero synchronous solving—correctness from golden DFS, scale from precompute.

### 6.4 Deal-breakers checklist

- DFS on every validate at scale.  
- Solve colocated with latency API pods unbounded.  
- Client-trusted scores for ranked.  
- Mid-match dictionary swap.  
- No timeout on 5×5/6×6 search.  
- Starting multiplayer before solution READY.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Solver library vs game platform?**  
A: Ask; present algorithm core then wrap service—impresses L5+.

**Q2: 4×4 or larger?**  
A: Lock 4×4 MVP; discuss complexity cliff.

**Q3: Must players submit paths?**  
A: Product; path helps anti-cheat; word-only OK with precomputed set.

**Q4: Real-time scoreboard?**  
A: Throttled broadcasts.

**Q5: Offline single player?**  
A: Bundle dict subset; ranked still server-side.

### 7.2 Algorithms

**Q6: Why trie?**  
A: Prune dead prefixes early; shared prefixes across starts.

**Q7: DFS vs BFS?**  
A: DFS natural for paths with visited; BFS less common here.

**Q8: Bitmask visited?**  
A: For 4×4, 16-bit int fast; recursion with backtrack.

**Q9: How to list paths too?**  
A: Store parent pointers / path stack when recording words.

**Q10: Dedup words multiple paths?**  
A: Use set; score once (classic rules).

**Q11: Aho-Corasick?**  
A: Alternative multi-pattern; trie DFS classic teaching answer.

**Q12: Complexity worst case?**  
A: Exponential in path length; practical pruned; still timeout-guard.

**Q13: Parallelism?**  
A: Parallelize start cells with thread-local found sets; merge.

**Q14: DAWG / GADDAG?**  
A: Scrabble structures; optional advanced.

### 7.3 Board generation

**Q15: How to ensure fun boards?**  
A: Rejection sampling on word count / score / bigram stats.

**Q16: Seed importance?**  
A: Repro for disputes & testing.

**Q17: Offensive words?**  
A: Filter solutions; optionally regenerate.

### 7.4 Systems & scale

**Q18: Why precompute?**  
A: Validate QPS ≫ solve need; stable fairness.

**Q19: Can we cache DFS?**  
A: Yes—solution sets are the cache.

**Q20: Room state store?**  
A: Redis for ephemeral; DB for history.

**Q21: Exactly-once submit?**  
A: Idempotency on `(room,user,word)`.

**Q22: Clock cheat?**  
A: Server `end_at`; ignore client clock.

### 7.5 Anti-cheat & fairness

**Q23: Instant 200 words?**  
A: Rate anomaly; captcha; delay; ban.

**Q24: Shared solution leak for daily?**  
A: Inevitable eventually; rotate; short contest windows; accept casual meta.

**Q25: Different dict advantage?**  
A: Pin version; show version in UI.

### 7.6 Multiplayer

**Q26: Matchmaking?**  
A: Skill buckets; or private rooms MVP.

**Q27: Disconnect?**  
A: Keep score; allow rejoin token until end.

**Q28: Spectators?**  
A: Read-only stream Phase 1.5.

### 7.7 Estimation drills

**Q29: 5×5 solve time?**  
A: Measure; may be 10–100× 4×4; argue precompute.

**Q30: Memory for 10M solution sets?**  
A: Cold in object storage; hot cache thousands.

**Q31: Validate at 2M QPS?**  
A: Edge+regional Redis; not DFS.

### 7.8 Alternatives & deal-breakers

**Q32: SQL `LIKE` dictionary?**  
A: Not for path-constrained board search.

**Q33: LLM to find words?**  
A: Wrong tool; nondeterministic; slow; cheating ambiguity.

**Q34: Client-only game?**  
A: Fine casual; not ranked platform.

### 7.9 Interview craft

**Q35: How to open?**  
A: Rules, board size, dict, solo vs multiplayer, validate vs full solve, scale.

**Q36: What impresses L5+?**  
A: Trie DFS details + precompute split + CPU isolation + fairness pin dict + CDN daily.

**Q37: Common mistake?**  
A: Only coding DFS; ignoring DoS and multiplayer authority.

---

### Appendix A — Trie node

```text
class Node:
  children: dict[str, Node]
  end: bool
```

### Appendix B — DFS solve

```text
def solve(board, trie):
  found = set()
  R, C = dims(board)
  def dfs(r, c, node, vis, path):
    ch = board[r][c]
    node = go(node, ch)  # handle Qu
    if not node: return
    path.append(ch)
    if node.end and len(word(path)) >= 3:
      found.add(word(path))
    vis.add((r,c))
    for nr,nc in neighbors(r,c):
      if (nr,nc) not in vis:
        dfs(nr,nc,node,vis,path)
    vis.remove((r,c))
    path.pop()
  for r in range(R):
    for c in range(C):
      dfs(r,c,trie.root,set(),[])
  return found
```

### Appendix C — Bitmask DFS (4×4)

```text
idx = r*4+c
bit = 1<<idx
if vis & bit: return
vis |= bit
...
vis ^= bit  # backtrack
```

### Appendix D — Validate

```text
def validate(board_id, user, word):
  word = normalize(word)
  sol = solutions[board_id]
  if word not in sol: return Reject
  if seen(user, word): return Dup
  mark seen
  return Accept(points(word))
```

### Appendix E — Path verify

```text
def path_ok(board, path, word):
  # path list of coordinates
  if cells reused: return False
  if not adjacent sequentially: return False
  if spell(path) != word: return False
  return True
```

### Appendix F — Board gen

```text
def gen(seed, dict_ver):
  rng = RNG(seed)
  for attempt in range(50):
    grid = sample_dice(rng)  # or frequencies
    words = solve(grid, trie)
    if min_w <= len(words) <= max_w: return grid, words
  return best_effort
```

### Appendix G — Scoring

```text
len 3-4 -> 1
5 -> 2
6 -> 3
7 -> 5
8+ -> 11
```

### Appendix H — Progressive scale

| Scale | Validate | Solve | Rooms | Daily |
|-------|----------|-------|-------|-------|
| Baseline | set lookup | sync workers | Redis | origin |
| 10× | Redis sets | async only | sharded | cache |
| 100× | regional | pool READY | many shards | CDN |
| 1,000× | edge | rare | cells | global CDN |

### Appendix I — Room JSON

```json
{
  "room_id": "r1",
  "state": "RUNNING",
  "board_id": "b9",
  "dict_version": "en-2026-07",
  "start_at": "2026-08-06T03:00:00Z",
  "end_at": "2026-08-06T03:03:00Z",
  "scores": {"u1": 12, "u2": 8}
}
```

### Appendix J — NFR card

```text
trie DFS correct
precompute ranked
validate p99 < 100ms
solve timeout enforced
dict pinned per match
CDN daily
```

### Appendix K — Dict build

```text
words.txt -> normalize -> filter len -> trie.bin + sha256 -> artifact store
```

### Appendix L — Comparison validate strategies

| Strategy | Latency | CPU | Cheat resistance |
|----------|---------|-----|------------------|
| DFS each time | Poor | High | High |
| Solution set | Excellent | Low | High |
| Client trust | Excellent | None | None |

### Appendix M — Neighbors

```text
for dr in -1..1:
  for dc in -1..1:
    if dr==0 and dc==0: continue
    yield r+dr, c+dc if in bounds
```

### Appendix N — Anti-cheat signals

| Signal | Action |
|--------|--------|
| Words/sec too high | Cap / flag |
| Perfect solution order | Flag |
| Known solver signatures | Delay |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Trie | Prefix tree for dictionary |
| SolutionSet | All valid words on a board |
| READY board | Board with computed solutions |
| Pin | Freeze dict/board for match |
| Rejection sampling | Regenerate unfit boards |

### Appendix P — Worked complexity intuition

```text
Without trie: explore huge dead paths spelling garbage
With trie: most branches die by length 3–4
Measured > theory in interview — cite need for timeouts
```

### Appendix Q — Consistency

| Question | Answer |
|----------|--------|
| Same scores all clients? | Server authoritative |
| Solve nondeterminism? | Set semantics deterministic |
| Dict update mid-day? | New daily only |

### Appendix R — 30m checklist

1. Clarify rules, size, multiplayer, validate vs solve.  
2. Present trie DFS.  
3. Split precompute vs validate QPS.  
4. Draw API/rooms/workers/CDN.  
5. DoS timeouts + fairness dict pin.  
6. Scale 10×/100×/1,000×.  
7. Deal-breakers.

### Appendix S — Qu tile

```text
When reading tile "Qu", advance trie with 'q' then 'u' atomically
Word length counts as 2 letters typically
```

### Appendix T — Multi-lang

```text
dict_version = "es-2026-01"
workers affinity by locale to keep trie warm
```

### Appendix U — Replay

```text
append submissions with ts
recompute scores offline for disputes
```

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Precomputed validate, worker split |
| 100× | CDN daily, room shards, READY pools |
| 1,000× | Regional cells, rare online solve |

---

*End of Boggle Solver (Puzzle Service) system design.*
