# System Design: Music Shuffle with Cooldown

> **Focus areas:** Fair shuffle algorithms · Anti-repeat / cooldown constraints · Play history · Distributed playlist state · Cross-device sync · Seeded randomness · Personalization hooks · Offline playback  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct shuffle math (not `ORDER BY RAND()` at scale), explicit cooldown windows, deal-breakers for “global lock per user on every skip”  
> **Interview theme:** Google L5+ consumer/media — shuffle a large library/playlist so songs don’t repeat too soon, across devices, with fairness and low latency

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

Goal: **bound the product**—a **music shuffle service** that produces a listening order with **cooldown constraints** (no song/artist/album repeats too soon), maintains **history**, and keeps **playlist/session state** consistent across devices.

### 1.0 What this is / is not

| Dimension | **Music shuffle + cooldown (this doc)** | Not this |
|-----------|------------------------------------------|----------|
| Primary job | Next-track selection under anti-repeat rules | Full DSP audio CDN design |
| Success | Feels random + fair; respects cooldown; snappy skips | Cryptographic RNG purity alone |
| State | Per-user/session shuffle cursor + history | Stateless pure random each play |
| Catalog | User library / playlist / radio pool | Entire world’s songs in one bag always |
| Offline | Prefetch queue continues constraints | Must call server every skip |

**Scope statement:** Design shuffle-with-cooldown for playlists and libraries: fair algorithms, history/cooldown enforcement, distributed session state, progressive scale to hundreds of millions of listeners.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Shuffle scope? | Playlist, liked songs, radio station pool | Pool = candidate set |
| F2 | Cooldown unit? | Song must not repeat until N others / T time; also artist/album gaps | Multi-key constraints |
| F3 | Fairness? | Each song roughly equal plays per cycle | Bag / weighted cycle |
| F4 | Skips? | Instant next; still counts for cooldown optional policy | Soft vs hard history |
| F5 | Cross-device? | Continue same shuffle session on phone↔speaker | Session state store |
| F6 | Offline? | Queue of next K tracks cached | Client-side generator + sync |
| F7 | Explicit replay? | User can replay; bypass cooldown | Override flag |
| F8 | Weighting? | Optional popularity / affinity weights | Weighted shuffle |
| F9 | Radio / infinite? | Dynamic pool with similarity | Sampler + cooldown memory |
| F10 | Collaborative playlist? | Multi-writer playlist; shuffle per listener | Per-user session on shared pool |
| F11 | Deterministic? | Same seed → same order for debugging | Seeded PRNG |
| F12 | Analytics? | Impersonality OK; log plays | Event pipeline |

**MVP functional scope:**

1. Create shuffle session on a pool (playlist/library).  
2. Generate order with **song cooldown** (e.g. no repeat until ≥ 50% of pool or min gap).  
3. **Artist cooldown** (e.g. no same artist within last K plays).  
4. `next`, `previous` (bounded), `skip`, `seek-in-queue`.  
5. Persist session: cursor, seed, history ring, remaining bag.  
6. Sync across devices; conflict policy.  
7. Prefetch next K URLs from existing audio service.  
8. Offline: continue from cached queue; reconcile on reconnect.  
9. Telemetry for play/skip.

**Out of MVP:**

- Full recommendation ML radio (hooks for scoring candidates)  
- Audio encoding/CDN (assume track URL service exists)  
- Social listening party sync as primary (mention extension)  
- Perfect mathematical discrepancy-free infinite shuffle proofs

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Next-track latency | Feels instant | p99 < 50–100 ms API; local < 16 ms |
| N2 | Consistency cross-device | Soft real-time | < 1–2 s sync typical |
| N3 | Availability | Playback continues | Client queue survives API blip |
| N4 | Fairness window | One “epoch” through pool | Each track once per epoch (unweighted) |
| N5 | Cooldown correctness | Never violate hard constraints if feasible | Soft relax if infeasible |
| N6 | Scale | Huge concurrent sessions | Shard by user_id |
| N7 | Determinism | Debug via seed | Replayable generator |
| N8 | Privacy | History sensitive | Encrypt/ACL user data |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User shuffles 200-song playlist → hears variety; first repeat only after ~cooldown.  
2. Skip 5 times quickly → still instant; history updated.  
3. Switch phone→desktop → same upcoming queue.  
4. Offline flight mode → plays prefetched 50; syncs history later.  
5. Small playlist (5 songs) → constraints relax with notice.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Pool size < cooldown | Relax artist/song gaps proportionally |
| All candidates violate artist gap | Pick least-bad (max time since artist) |
| Weighted hit songs | Still respect hard song cooldown |
| Concurrent next on 2 devices | CAS session version; one wins; other refreshes |
| Playlist edited mid-shuffle | Reconcile bag: add new, remove deleted, keep cursor policy |
| Empty pool | Error |
| Explicit play song S | Jump; mark played; continue |
| Radio infinite pool | Sliding history; never “complete epoch” |
| Very large library 100K tracks | Don’t materialize full permutation array naively |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 10M | 100M | 1B | — |
| Concurrent sessions | 1M | 10M | 100M | 1B peak events |
| Next-track QPS | 50K | 500K | 5M | 50M |
| Avg pool size | 200 | 500 | 1K | 10K library |
| History ring | 200 | 500 | 1K | compressed |
| Prefetch K | 50 | 50 | 30–50 | adaptive |
| Devices / user | 2 | 3 | 5 | many IoT |

**What each jump forces:**

- **10×:** Session store redis/memory + durable log; edge caches for catalog metadata.  
- **100×:** Client-authoritative next with server reconcile; avoid central RNG lock.  
- **1,000×:** Pure client generation from seed+compact state; server = backup + analytics; CRDT-ish session.

### 1.5 Etc. (Constraints & Assumptions)

- Track metadata (artist_id, album_id, duration) available from catalog service.  
- Audio bytes served elsewhere; we return `track_id` (+ URL token).  
- “Fair” ≠ uniform ignore likes — support weights later.  
- Cooldown is product policy; make numbers configurable.

**Scope statement to repeat back:**

> Design a music shuffle-with-cooldown system: fair epoch-based (or weighted) selection, song/artist/album anti-repeat constraints, compact session state synced across devices, offline queues, and progressive scale without per-skip global locks.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Naive anti-patterns

```text
SELECT * FROM playlist ORDER BY RAND() LIMIT 1
→ O(n) or worse; repeats; no cooldown; DB melt at 5M QPS
```

**Deal-breaker** in interview if this is the whole design.

### 2.2 Session state size

```text
session_id, user_id, pool_id, seed (8B), cursor, version
remaining: bitset or list of track indices
history ring: last H track_ids (8B each)
For pool N=10_000: bitset ≈ 1.25 KB; history H=200 → 1.6 KB
Session ≈ 5–20 KB → 100M sessions = 0.5–2 TB — shard + TTL inactive
```

### 2.3 QPS

```text
1M concurrent listeners, avg song 3 min, 10% skip extra
next ≈ 1M / 180 ≈ 5.5K/s + skips → ~10K/s baseline
At 100M concurrent: ~1M/s — must be mostly local/edge
```

### 2.4 Materialized permutation

```text
N=100K track_ids × 8B = 800 KB per session — wasteful × 100M users
Prefer: Fisher–Yates online / epoch bag with bitset, not full array for huge N
```

### 2.5 Constraint feasibility

```text
Artist gap K=5, but playlist is 6 songs by 1 artist → impossible
Detect: if distinct artists < need, relax
```

### 2.6 Cross-device sync bandwidth

```text
State delta ~1 KB every track
1M sessions × track/3min → ~5K updates/s — fine
```

---

## 3. High-Level Design

### 3.1 Core abstraction

```text
ShuffleSession {
  pool_version
  seed
  epoch_id
  remaining_set   # unplayed in epoch
  history_ring    # recent plays for cooldown
  queue           # precomputed next K
  version         # CAS
}
```

API:

```text
POST /v1/shuffle/sessions  {pool_id, mode}
GET  /v1/shuffle/sessions/{id}/next
POST /v1/shuffle/sessions/{id}/skip
POST /v1/shuffle/sessions/{id}/play_explicit {track_id}
GET  /v1/shuffle/sessions/{id}  # sync
PUT  /v1/shuffle/sessions/{id}  # client reconcile
```

### 3.2 Algorithm choices — Why X over Y

| Approach | Pros | Cons | Use |
|----------|------|------|-----|
| **Fisher–Yates full permute** | Perfect fair epoch | Memory for huge N | N ≤ ~10K |
| **Online Fisher–Yates (partial)** | O(1) next | Need swap array | Medium N |
| **Bitset bag + random pick** | Compact | Rejection sampling | Good MVP |
| **Weighted random w/ cooldown mask** | Personalization | Bias complexity | Radio |
| **ORDER BY RAND()** | Simple | Unfair/repeats/scale | Never sole |
| **MRU blocklist only** | Easy cooldown | Starvation / unfair | Insufficient alone |

**MVP recommendation:** Epoch bag (each track once) + **rejection/repair** for artist/album gaps + history ring for time-based cooldowns.

### 3.3 Cooldown rules (MVP)

```text
song_cooldown: no track_id in last min(N-1, max(1, floor(αN))) plays
artist_cooldown: no same artist_id in last A plays (e.g. 3–5)
album_cooldown: optional last B plays
soft vs hard: hard tries repair; if fail, least_bad()
```

### 3.4 Next-track pipeline

```text
1. If queue non-empty: pop
2. Else refill_queue(K):
     while queue < K:
       candidate = sample_from_remaining(seed)
       if violates_cooldown: try resample ≤ R times
       if still bad: candidate = least_bad(remaining)
       queue.push(candidate); remaining.remove(candidate)
3. On pop: history.push; if remaining empty: new_epoch() reshuffle
4. Persist session version++
```

### 3.5 Why X over Y (summary)

| Decision | Choice | Reject |
|----------|--------|--------|
| Fairness | Epoch without replacement | Pure with-replacement RNG |
| Constraints | Sample + least-bad fallback | Fail request |
| Scale | Compact state + client queue | DB RAND per skip |
| Sync | Versioned session CAS | Last write silent loss |
| Offline | Prefetch K | Online-only |

---

## 4. Architecture Diagram

### 4.1 Serving architecture

```text
┌──────────┐   next/skip    ┌─────────────────┐
│ Mobile   │───────────────►│ Shuffle API     │
│ Desktop  │◄──track_id────│  + Session CAS  │
│ Speaker  │                └────────┬────────┘
└────┬─────┘                         │
     │ prefetch audio                ▼
     │                      ┌─────────────────┐
     │                      │ Session Store   │
     │                      │ (Redis + SQL)   │
     │                      └────────┬────────┘
     ▼                               │
 Audio CDN                     Catalog (artist/album)
```

### 4.2 Client-assisted (100×+)

```text
Server: issues seed + pool snapshot hash + rules config
Client: runs same generator; maintains queue
On play: async append event → server history
On conflict: pull server session; rebase queue
```

### 4.3 Epoch bag visualization

```text
Epoch 1 remaining: ■ ■ ■ ■ ■ ■ ■ ■
Play:              ✓
remaining:           ■ ■ ■ ■ ■ ■ ■
...
remaining empty → reshuffle Epoch 2 (new permutation; optional carry cooldown)
```

### 4.4 Cooldown check

```text
history (recent first): t9 t8 t7 t6 t5 ...
candidate c artist=A
reject if c in history[0:song_gap)
reject if artist(c) in artists(history[0:artist_gap))
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Hard constraints attempted first;** soft degradation explicit in metrics.  
2. **Session updates CAS on version** — no silent lost skips.  
3. **Seed + algorithm version** define deterministic order for epoch.  
4. **Playback continues offline** with local queue.  
5. **Idempotent play events** (`play_id`) for analytics/history.  
6. **Pool version mismatch** triggers reconcile not crash.

#### 5.1.2 Exactly-once history?

At-least-once play events with dedup keys; shuffle correctness uses session apply order.

#### 5.1.3 Cross-device conflicts

```text
Device A version=5 next → version=6
Device B version=5 next → CAS fail → refetch → next from v6
Optional: sticky device leadership for active audio focus
```

#### 5.1.4 Infeasible constraints

```text
def least_bad(candidates, history):
  score = song_recency_penalty + artist_recency_penalty + album_penalty
  return argmin(score)  # never infinite loop
```

**Deal-breaker:** algorithm that infinite-loops rejecting all candidates on tiny playlists.

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Redis loss | Dual-write SQL snapshot |
| 10× | Hot user thundering skips | Client queue |
| 100× | Sync storms | Event batching |
| 1,000× | Central next QPS | Client-authoritative RNG |

### 5.2 Scalability

#### 5.2.1 Sampling from remaining

**Bitset + random index:**

```text
pick random r in [0, remaining_count)
find r-th set bit (page ranks / hierarchical bitset)
O(log N) with summary counts
```

**Swap-list Fisher–Yates:**

```text
array of remaining ids; swap chosen with end; pop
O(1); memory O(N)
```

Choose by N.

#### 5.2.2 Weighted shuffle with cooldown

```text
Use EF or alias method on eligible subset
Eligibility = remaining ∩ not_cooling_down
If weight mass zero → least_bad on remaining
```

Avoid recomputing alias over full catalog each skip — maintain eligible structure.

#### 5.2.3 Radio / infinite pools

```text
Candidate generator (ANN / filters) → score → pick with cooldowns
History ring large (artist/song)
No epoch completeness guarantee — fairness via long-term counters
```

#### 5.2.4 Prefetch vs freshness

| K large | Better offline; stale if playlist edits |
| K small | Fresher; more API |

Adaptive K by network and edit rate.

#### 5.2.5 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Redis sessions; async analytics |
| →100× | Client generator + server backup |
| →1,000× | Edge config; compact CRDT history; regional session |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
song_gap_frac: 0.5
artist_gap: 4
album_gap: 2
resample_tries: 20
prefetch_k: 50
algorithm_version: 3
relax_order: [album, artist, song]
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `constraint_violation_soft` | Rule too strict |
| `resample_attempts` | Efficiency |
| `session_cas_conflict` | Multi-device |
| `next_latency` | UX |
| `epoch_length` | Fairness |
| `offline_queue_underrun` | Prefetch |

#### 5.3.3 Testing

- Property: in epoch of unweighted shuffle, each track once.  
- Property: no hard song repeat closer than gap when N allows.  
- Tiny playlist stress.  
- Concurrent device CAS.  
- Seed determinism golden files.

#### 5.3.4 Ops

- Kill-switch relax all cooldowns.  
- Per-user algorithm experiments.  
- Rebuild session if corrupted bitset.

---

## 6. Wrap-Up

### 6.1 What we designed

A **shuffle-with-cooldown** system: epoch bag fairness, multi-key anti-repeat, compact versioned sessions, prefetch/offline, and a path from **server next** to **client-authoritative seeded generation** at extreme QPS.

### 6.2 Memorize tradeoffs

| Topic | Tradeoff |
|-------|----------|
| Without-replacement vs with | Fairness vs infinite radio |
| Hard vs soft cooldown | UX purity vs feasibility |
| Server vs client next | Consistency vs latency/QPS |
| Prefetch K | Offline vs freshness |
| Weights vs fair epoch | Engagement vs equal airtime |
| History size | Better constraints vs state |

### 6.3 30-second scale narrative

Baseline: server Fisher–Yates/bitset sessions.  
10×: Redis + prefetch.  
100×: client generator.  
1,000×: edge/offline-first; server reconcile/analytics.

### 6.4 Deal-breakers checklist

- `ORDER BY RAND()` as architecture.  
- Infinite rejection loop on small pools.  
- Full permutation materialization for 100K×100M.  
- Global lock per user for every skip.  
- Ignoring artist clumps (“random” feels broken).  
- No multi-device version story.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Playlist or whole library?**  
A: Both; pool abstraction.

**Q2: Does skip count as played for cooldown?**  
A: Product choice — usually yes for song gap; confirm.

**Q3: Should shuffle feel “truly random” or “DJ fair”?**  
A: Fair epoch + gaps — users prefer this over clumpy RNG.

### 7.2 Algorithms

**Q4: Fisher–Yates?**  
A: Uniform random permutation; basis for fair epoch.

**Q5: How to enforce artist gap inside permutation?**  
A: Constrained shuffle / repair passes / rejection sampling with fallback.

**Q6: Weighted shuffle without starvation?**  
A: Periodic re-normalization; mini-epochs; dampen recent.

**Q7: Same seed reproducibility?**  
A: Seeded PRNG + algo version + pool ordering.

**Q8: Why not reshuffle entire list every next?**  
A: Breaks fairness; expensive; causes repeats.

### 7.3 Distributed state

**Q9: Cross-device sync?**  
A: Versioned session; CAS; audio focus optional.

**Q10: Offline reconcile?**  
A: Client applies local plays; merge history by timestamp/`play_id`; recompute queue.

**Q11: Playlist mutation?**  
A: Diff pool membership; remaining &= still_present; add new to remaining.

### 7.4 Radio & ML

**Q12: How hooks to recommenders?**  
A: Candidate service returns scored set; shuffle/cooldown chooses among top eligible.

**Q13: Exploration vs cooldown?**  
A: Keep cooldown hard; explore inside eligible set.

### 7.5 Estimation drills

**Q14: QPS for 30M concurrent, 3.5 min songs?**  
A: ≈ 30M/210 ≈ 143K next/s before skips.

**Q15: State for 200M sessions × 10 KB?**  
A: 2 PB — TTL inactive; compact; client-primary.

**Q16: Why bitset?**  
A: N=100K → ~12.5KB bits vs 800KB id list.

### 7.6 Alternatives & deal-breakers

**Q17: Redis list of full order?**  
A: OK small N; blows memory at library scale.

**Q18: Only “don’t play last 20”?**  
A: Easy repeats of favorites; unfair; artist clumps remain.

**Q19: Serverless RNG without state?**  
A: Can’t enforce cooldown/fairness.

### 7.7 Interview craft

**Q20: How to open?**  
A: Pool, cooldown rules, fairness, devices, offline — then algorithm + state.

**Q21: What impresses L5+?**  
A: Feasibility/least-bad, compact state math, client-gen shift at scale, determinism.

**Q22: Common mistake?**  
A: Discussing Kafka for 20 minutes before defining shuffle semantics.

---

### Appendix A — Fisher–Yates

```text
for i from n-1 downto 1:
  j = random(0, i)
  swap a[i], a[j]
```

### Appendix B — Next with rejection

```text
def pick(session):
  for _ in range(R):
    c = sample(session.remaining, session.rng)
    if ok(c, session.history, rules): return c
  return least_bad(session.remaining, session.history)
```

### Appendix C — New epoch

```text
session.remaining = all_tracks(pool)
session.epoch_id += 1
# optional: keep history for cross-epoch artist gap
refill_queue(session)
```

### Appendix D — Session schema

```json
{
  "session_id": "s1",
  "pool_id": "pl_9",
  "pool_version": 12,
  "seed": "0xdeadbeef",
  "algo": 3,
  "epoch": 4,
  "remaining_bitset_b64": "...",
  "history": ["t1","t2"],
  "queue": ["t9","t8"],
  "version": 88
}
```

### Appendix E — CAS update

```text
UPDATE ... SET version=version+1, ... WHERE id=? AND version=?
```

### Appendix F — Relaxation ladder

```text
try: song+artist+album
else drop album gap
else drop artist gap
else allow song repeat least recent
```

### Appendix G — Progressive scale table

| Scale | Next computed | Session store |
|-------|---------------|---------------|
| Baseline | Server | Redis+SQL |
| 10× | Server + prefetch | Sharded Redis |
| 100× | Client | Backup snapshots |
| 1,000× | Client/edge | Event log |

### Appendix H — Weighted alias note

```text
Build alias on eligible weights when eligibility set changes batch-wise
Not every skip from scratch if possible
```

### Appendix I — Play event

```json
{"play_id":"p","user":"u","track":"t","ts":...,"session":"s","v":88}
```

### Appendix J — NFR card

```text
p99 next < 100ms
CAS sessions
least-bad fallback
epoch fairness
prefetch offline
no SQL RAND
```

### Appendix K — Artist clump demo

```text
Bad RNG: A A B A C
Good: A B C A … with gaps
```

### Appendix L — Previous track

```text
Bounded stack of past plays; previous doesn’t re-insert into remaining
Policy explicit
```

### Appendix M — Common pushbacks

| Pushback | Answer |
|----------|--------|
| “Just randomize list once” | OK until edits/skips/constraints/devices |
| “ML will handle” | Still need constraints layer |
| “Stateless” | Breaks cooldown + fairness |

### Appendix N — Related systems (conceptual)

- Spotify/YT Music shuffle lore (public engineering posts)  
- Recommenders as candidate sources  
- CRDTs for session merge experiments |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Epoch | One without-replacement pass |
| Bag | Remaining unplayed set |
| Least-bad | Min penalty feasible pick |
| Soft violation | Allowed after relax |
| Promoter | Explicit play bypass |

### Appendix P — Worked example

```text
N=10, song_gap=5, artist_gap=2
Play sequence ensures distance; when remaining=3 and constraints tight → least-bad
```

### Appendix Q — Consistency cheatsheet

| State | Model |
|-------|-------|
| Active session | CAS strong per shard |
| Analytics history | Eventually consistent |
| Catalog metadata | Cached eventual |
| Offline queue | Client optimistic |

### Appendix R — 30m interview checklist

1. Rules: song/artist gaps + fairness.  
2. Algorithm + least-bad.  
3. Session schema.  
4. Devices CAS.  
5. Numbers QPS/state.  
6. Scale to client RNG.  
7. Deal-breakers.  

### Appendix S — Pseudocode refill

```text
def refill(session, K):
  while len(session.queue) < K and session.remaining:
    c = pick(session)
    session.queue.append(c)
    session.remaining.remove(c)
  if not session.remaining and not session.queue:
    new_epoch(session)
```

### Appendix T — What changes at each scale

| Scale | Key change |
|-------|------------|
| 10× | Sharded sessions |
| 100× | Client generation |
| 1,000× | Offline-first + event log |

### Appendix U — Security/privacy

- Sessions private to user  
- Shared playlist ≠ shared shuffle history  
- GDPR delete history/sessions |

### Appendix V — A/B experiments

```text
algo_version in session
metrics: skip_rate, session_length, constraint_soft_rate
```

---

*End of music shuffle with cooldown system design.*
