# System Design: Real-Time Game Leaderboard / Ranking (Amazon Games)

> **Focus areas:** Sorted sets · Sharding · Real-time updates · Top-K · Nearby ranks · Anti-cheat hooks · Season resets · Spectator fanout · Progressive scale
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split write ingest vs read fanout, correct sorted-set math, deal-breakers for “single Redis global ZSET” at 100×
> **Interview theme:** Amazon SDE III / L6 — **Amazon Games / Twitch-adjacent** real-time leaderboard ownership—correctness under write spikes, fair competition, and cost-efficient reads

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

Goal: **bound the product**—a **real-time game leaderboard** that ingests score updates, maintains rankings (global, regional, friends, seasonal), serves top-K and “around me” queries with low latency, and handles season resets, ties, and anti-cheat hooks at Amazon Games scale.

### 1.0 What this is / is not

| Dimension | **Leaderboard (this doc)** | Not this |
|-----------|----------------------------|----------|
| Primary job | Rank players by score fast | Full matchmaking / lobby |
| Success | Correct-enough ranks, low latency, fair seasons | Exact global serializability of every write |
| Storage | Sorted structures + checkpoints | Table scan ORDER BY each read |
| Real-time | Seconds or sub-second visibility | Daily batch ranks only |
| Amazon lens | Player trust, cost, ops ownership, Prime Gaming hooks | Esports broadcast graphics alone |

**Scope:** Design real-time leaderboards: ingest, sharded ranking, top-K + nearby, seasons, friends boards, anti-cheat hooks, progressive scale.

### 1.1 Functional Requirements

| # | Question | Answer | Implication |
|---|----------|--------|-------------|
| F1 | Rank by what? | Score; optional time-to-score tie-break | Composite sort key |
| F2 | Boards? | Global, regional, mode, seasonal, friends | Multiple board_ids |
| F3 | Queries? | Top-K, my rank, nearby ±N | Different access patterns |
| F4 | Update rate? | After match / event; bursts | Write path optimized |
| F5 | Freshness? | Near real-time (≤1–2s typical) | Memory ranking + async persist |
| F6 | Seasons? | Timed reset + archive | Versioned boards |
| F7 | Ties? | Deterministic policy | score, then timestamp, then player_id |
| F8 | Friends? | Rank among friends list | Separate structure or filter |
| F9 | Anti-cheat? | Hooks to reject/quarantine scores | Validation gate |
| F10 | Spectators? | Hot top-K fanout | Cache + pub/sub |
| F11 | Auth? | Player identity from game services | Signed updates |
| F12 | Cross-region? | Regional boards; global optional | Cell design |
| F13 | Historical? | Season archives | Cold store |
| F14 | Admin? | Manual ban/wipe | Audit |
| F15 | Prime / Twitch drops? | Optional overlays | Event bus |

**MVP:** ingest authenticated score updates; maintain seasonal global + regional boards; top-100; my rank; nearby 10; season reset/archive; basic anti-cheat reject list; metrics.

**Out of MVP:** full matchmaking; pixel-perfect esports graphics; ML skill rating (TrueSkill) as sole rank (can coexist); infinite historical replay UI.

### 1.2 Non-Functional Requirements

| # | Target |
|---|--------|
| N1 Write ack | p99 < 50–100ms |
| N2 Top-K read | p99 < 30–50ms |
| N3 My rank | p99 < 50ms |
| N4 Availability | 99.9%+; season boundary careful |
| N5 Durability | No lost committed scores after ack |
| N6 Fairness | Deterministic ties; anti-cheat hooks |
| N7 Cost | Memory for hot boards; cold archive |
| N8 Scale | Write spikes at season end / events |

### 1.3 Cases

Happy: finish match → score up → rank updates → client sees new rank; view top-100; friends board; season rollover archives prior.

| Case | Behavior |
|------|----------|
| Duplicate update | Idempotency key (match_id) |
| Score decrease policy | Game-specific (allow or monotonic) |
| Cheater spike | Quarantine board / reject |
| Hot key player | Shard by board; not by player alone |
| Season flip mid-write | Dual-write window / fence token |
| Friends list huge | Cap / sample / precompute |
| Spectator storm | Cache top-K; pub/sub invalidate |

### 1.4 Scales

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Concurrent players | 1M | 10M | 100M | 1B class |
| Score updates/s peak | 50K | 500K | 5M | 50M |
| Boards active | 10K | 100K | 1M | many cells |
| Top-K QPS | 100K | 1M | 10M | edge cached |
| Rank QPS | 200K | 2M | 20M | sharded |

**Jumps:** 10× shard boards; 100× cell by game/region + top-K edge; 1,000× hierarchical ranks / approximate global.

### 1.5 Constraints

- Ranking service ≠ match result authority (game services sign scores).
- Player trust: visible unfairness is existential for competitive modes.
- Prefer mechanisms: idempotency, season fencing, audit.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | What | Base peak | Plane |
|-------|------|-----------|-------|
| A | Score ingest | 50K/s | Online write |
| B | Top-K reads | 100K/s | Online read |
| C | My rank / nearby | 200K/s | Online read |
| D | Persist / WAL | ~50K/s | Durability |
| E | Season archive | Batch | Offline |
| F | Spectator fanout | Bursty | Pub/sub |

### 2.2 Sorted-set memory

Assume board with 10M players, entry 32B (player_id + score + tie): ~320 MB per fat board. 10K boards mostly small. Hot global boards dominate RAM.

### 2.3 Rank computation

Redis `ZREVRANK` O(log N); top-K `ZREVRANGE` O(log N + K). Friends board of size F: maintain per-player ZSET of friends scores or compute on read if F small (≤500).

### 2.4 Latency budget (update)

| Step | Budget |
|------|--------|
| Auth / validate signature | 5–10 ms |
| Anti-cheat gate | 5–15 ms |
| ZADD + side indexes | 5–20 ms |
| Persist async / sync quorum | 5–30 ms |
| **Ack p99** | **≤ 50–100 ms** |

### 2.5 Spike math

Season ending hour: 10× writes. Pre-split shards; disable nonessential friends recompute; cache top-K aggressively.

---

## 3. High-Level Design

### 3.1 Goals

Correct-enough real-time ranks; durable committed scores; fair seasons; cheap top-K; clear ownership with game services & anti-cheat.

### 3.2 Components

| Component | Role |
|-----------|------|
| Ingest API | Authenticated score updates |
| Validation / Anti-cheat Gate | Reject/quarantine |
| Board Router | board_id → shard/cell |
| Rank Engine (Redis/memory) | Sorted sets |
| Durability Log | WAL / Kafka |
| Rank Query API | Top-K, me, nearby |
| Top-K Cache | Spectator/hot |
| Season Manager | Fence, reset, archive |
| Friends Index | Optional boards |
| Archive Store | S3 + metadata |
| Admin / Audit | Bans, wipes |

### 3.3 Score key design

```text
sort_key = (score << time_bits) | (max_time - ts)   # higher score wins; earlier ts wins ties
member  = player_id
```

Or lexicographic tie-break fields supported by store.

### 3.4 API

```text
POST /v1/boards/{board_id}/scores
  { player_id, score, match_id, ts, sig }
GET  /v1/boards/{board_id}/top?k=100
GET  /v1/boards/{board_id}/players/{id}/rank
GET  /v1/boards/{board_id}/players/{id}/nearby?n=10
POST /v1/seasons/{id}/close
```

### 3.5 Tradeoffs

| Decision | Choose | Deal-breaker |
|----------|--------|--------------|
| Store hot ranks | Redis ZSET / similar | SQL ORDER BY per read |
| Global single ZSET | **Sharded boards / cells** | One Redis for all games |
| Durability | WAL + periodic snapshot | Memory-only |
| Friends | Cap size + dedicated structures | Join social graph online globally |
| Global rank at 1B | Hierarchical approx | Exact single structure |

---

## 4. Architecture Diagram

```text
Game Services --signed score--> Ingest API --> Anti-Cheat Gate
                                      |
                                      v
                                 Board Router
                                      |
                      +---------------+---------------+
                      v               v               v
                 Rank Shard 0    Rank Shard 1    Rank Shard N
                 (ZSET boards)   (ZSET boards)   (ZSET boards)
                      |               |               |
                      +--------+------+------+--------+
                               v             v
                           WAL/Kafka     Top-K Cache
                               |             |
                               v             v
                          Archive/S3    Query API --> Clients
                               ^
                         Season Manager
```

### 4.2 Update sequence

```text
validate sig → idempotency(match_id) → cheat gate → ZADD
  → emit event → optional pub/sub invalidate top-K → ack
```

### 4.3 Season fence

```text
t < T_close: writes to board_v
T_close ≤ t < T_grace: dual policy (reject or buffer)
t ≥ T_open_next: writes to board_v+1; v archived read-only
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Acked score is durable (WAL quorum) before or atomically with visibility policy.
2. Idempotent match_id.
3. Season fence token on writes.
4. Deterministic tie-break.
5. Banned players excluded from public top-K.

### 5.2 Sharding

Shard by `board_id` (natural isolation). Hot global board: split by player_id hash into M partial boards + merger for top-K (tournament merge) at 100×.

### 5.3 Nearby ranks

`rank = ZREVRANK`; nearby = `ZREVRANGE(rank-N, rank+N)`. If sharded partial boards, store player→shard map.

### 5.4 Friends leaderboard

Options: (A) on read filter if friends ≤ 200; (B) per-player friends ZSET updated on friend score changes (write fanout); (C) approximate. Choose A for MVP, B for large social games carefully.

### 5.5 Anti-cheat integration

Synchronous light checks (signature, rate, score delta bounds); async heavy ML quarantine that can rewind ranks via compensating events.

### 5.6 Progressive scale

10×: more shards, top-K cache. 100×: cells per title/region; hierarchical global. 1,000×: approximate ranks + segment boards.

### 5.7 Reliability

Redis cluster; WAL replay; dual-AZ; season runbooks; backup archives.

### 5.8 Observability

`update_p99`, `topk_p99`, `rank_p99`, `idempotent_hits`, `cheat_rejects`, `season_lag`, memory per board.

---

        ## 6. Wrap-Up

        ### 6.1 What we designed

        A **real-time leaderboard platform** for Amazon Games: signed score ingest, anti-cheat gates, sharded sorted-set rank engines, durable WAL, top-K cache, season fencing/archives, friends boards, progressive scale.

        ### 6.2 Key decisions worth defending

        1. Shard by board/cell; no single global ZSET
2. Idempotent match updates + season fences
3. Memory hot ranks + WAL durability
4. Cache top-K for spectator storms
5. Exact vs approximate rank as explicit product choice at extreme scale

        ### 6.3 Risks & follow-ups

        - Hot board memory explosions
- Friends fanout costs
- Cheat-driven rewinds UX
- Cross-region global exactness pressure

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **Real-Time Game Leaderboard** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---

## 7. Deeper / Related Interview Questions

### 7.1 Core

**Q1. Why not MySQL ORDER BY score LIMIT 100?**

**A:** Write-heavy competitive games need log-N updates and fast rank ops. SQL can archive/analytics but not hot path at 50K+ updates/s with rank queries.

**Q2. How do you shard a single hot global board?**

**A:** Hash players into partial ZSETs; top-K via merge of per-shard tops; rank via local rank + offsets or periodic global histograms for approximate rank.

**Q3. Exact global rank vs approximate?**

**A:** Exact is costly at extreme scale. Many games show exact within shard/region and approximate globally—product decision, say it aloud.

**Q4. Season reset without downtime?**

**A:** Fence token + dual board versions; archive async; read-only old board; never flip by wiping memory without versioning.

**Q5. Idempotency?**

**A:** match_id unique key; duplicate posts return same ack without double counting.

**Q6. Spectator 1M readers of top-10?**

**A:** Cache top-K with short TTL + pub/sub invalidation; don’t hit ZSET per spectator.

**Q7. Friends leaderboard at Facebook scale?**

**A:** Not Amazon Games usual—but if needed, cap friends, precompute, or aspirational boards; avoid full graph join online.

**Q8. Cheater already on board?**

**A:** Quarantine flag + rebuild segment from WAL excluding events; audit trail; visible removal messaging policy.

### 7.2 Traps

**Q9. Single Redis ZSET for everything?**

**A:** Deal-breaker at 100×—hot key, memory, blast radius. Shard by board and cell by title.

**Q10. Strongly consistent global ranks across regions?**

**A:** Expensive; prefer regional authority + async global aggregation.

**Q11. Store every historical rank change in Redis?**

**A:** No—hot current season in memory; history in cold store.

        ## 8. Appendices

        ### Appendix A — Glossary

        | Term | Meaning |
        |------|---------|
        | Two-pizza team | Ownership team with pager |
        | Cell | Failure-isolated unit |
        | Nearline | Minutes-latency path |
        | Shadow | Score without user impact |
        | Canary | Partial traffic bake |
        | Deal-breaker | Non-negotiable bad design |

        ### Appendix B — Estimation cheat-sheet

        ```text
        QPS_peak ≈ DAU × actions/day / 86400 × peak_factor
        Storage ≈ rows/day × bytes × retention
        ```

        ### Appendix C — Oncall checklist

        - [ ] SLOs green
        - [ ] Canary/rollback armed
        - [ ] Kill switches known
        - [ ] Blast radius mapped
        - [ ] Cost dashboards
        - [ ] Privacy/safety paths tested

        ### Appendix D — LP mapping

        | LP | Signal |
        |----|--------|
        | Customer Obsession | Trust + latency under failure |
        | Ownership | Clear pager |
        | Dive Deep | Correct math + invariants |
        | Frugality | Unit cost metrics |

        ### Appendix F — Schemas

```text
ScoreEvent { event_id, board_id, player_id, score, match_id, ts, season, sig }
BoardMeta  { board_id, season, state, shard, fence }
RankView   { player_id, rank, score, nearby[] }
```

### Appendix G — Runbooks

**Hot board memory:** split shard; enable hierarchical top merge.
**Season stuck:** check fence; freeze writes; manual cutover checklist.
**Cheat wave:** enable quarantine lane; rebuild from WAL.

### Appendix H — Capacity sketch

| Tier | Count | Notes |
|------|-------|-------|
| Ingest | 30 | stateless |
| Redis shards | 40 | hot boards |
| Query | 30 | + cache |
| Kafka | 12 brokers | WAL |

### Appendix I — Closer checklist

- [ ] Split write/read planes
- [ ] Idempotency + season fence
- [ ] Shard story beyond one ZSET
- [ ] Top-K cache for spectators
- [ ] Anti-cheat hooks
- [ ] Progressive scale



## Extended Notes — Real-Time Leaderboard

### E1. Composite scores

Discuss encoding score+time without floating point pain. Integer millis and fixed-point scores.

### E2. Write auth

Game server secrets vs player-submitted scores. Never trust client score without server authority.

### E3. Twitch / Prime Gaming

Optional event topics for drops eligibility based on rank thresholds—consume via bus, don’t put Twitch in the hot ZADD path.

### E4. Memory eviction

Cold boards offload to snapshots; reload on demand. Keep only active seasons hot.

### E5. Legal / fairness communications

When ranks rewind due to cheat bans, product messaging matters as much as tech.

### E6. Multi-mode boards

board_id encodes game|mode|region|season. Cardinality control via lifecycle TTLs.

### E7. Testing

Deterministic tie fixtures; season fence chaos tests; idempotency fuzzing; load replay of season endings.

### E8. Cost metric

USD per million updates + RAM per active board. Archive aggressively.

### E9. Nearby UX

Show denser competition around player; motivates engagement more than only top-100.

### E10. Cross-title platform

Shared leaderboard platform with per-title cells—Amazon Games org pattern.

### E11. Backup restore

Restore from WAL+snapshot to last ack; rebuild caches; verify checksum of top-K.

### E12. Rate limits

Per player update rate; per match once; burst tokens for server recoveries.

### E13. Data model evolution

Add secondary scores (wins) via versioned entry payloads without breaking sort.

### E14. Privacy

Friends boards need authz; don’t leak quiet players’ ranks publicly if opted private.

### E15. Comparison to chess ratings

Elo/TrueSkill is a different problem (skill estimation). Leaderboards are ordered scores; they can display MMR but storage path differs.

---


## 9. Interview Walkthrough Script (35–45 min)

### 9.1 Opening (2 min)

Restate the problem in Amazon terms: customer impact, ownership boundary, what is explicitly out of scope. Ask clarifying questions from §1 before drawing boxes.

### 9.2 Requirements lock (5 min)

Lock MVP vs out-of-scope. State NFRs as numbers. Mention progressive scale early so the interviewer knows you will not design only for today’s QPS.

### 9.3 Estimation (5 min)

Split load classes. Show latency budget table. Call out the unit-cost metric you will optimize (RAM$/QPS, $/1K inferences, etc.).

### 9.4 HLD + diagram (10 min)

Draw the ASCII architecture. Narrate primary happy path. Name owning teams for each box.

### 9.5 Deep dive (10–12 min)

Pick 2–3 sharp topics: failure modes, consistency, scale jump, privacy/safety. Avoid laundry-listing every component again.

### 9.6 Close (3 min)

Risks, metrics, pager ownership, and the single deal-breaker design you refused.

---

## 10. Metrics, Alarms, and Runbooks

### 10.1 Golden signals

| Signal | Example metrics | Alarm intuition |
|--------|-----------------|-----------------|
| Latency | p50/p99 by endpoint | Burn error budget |
| Traffic | QPS, bytes, fanout | Sudden cliffs/spikes |
| Errors | 5xx, dependency timeouts | Page on rate |
| Saturation | CPU, RAM, queue depth | Predictive scale |
| Freshness | Index/model age | Product SLO |
| Trust | Safety blocks, privacy denials | Near-zero incidents |

### 10.2 Dashboard rows (minimum)

1. Customer-facing SLO panel  
2. Dependency health panel  
3. Data/ML freshness panel  
4. Cost panel  
5. Experiment guardrails panel  

### 10.3 Incident severity guide

| Sev | Example | Response |
|-----|---------|----------|
| SEV-1 | Safety/privacy leak OR total outage of critical path | Immediate war room |
| SEV-2 | Elevated p99 / partial degrade | Page; mitigate via fallback |
| SEV-3 | Stale models / elevated fallback rate | Business hours + ticket |
| SEV-4 | Cosmetic / tooling | Backlog |

### 10.4 Generic rollback ladder

```text
1) Feature flag OFF / kill switch
2) Canary revert / last-good artifact
3) Traffic shed / reduce K / disable optional stage
4) Cell isolation if blast radius regional
5) Postmortem with customer-trust section
```

---

## 11. Consistency, Correctness, and Data Contracts

### 11.1 Contract checklist

- Request/response schema versioned  
- Idempotency keys where writes exist  
- Policy/model/index versions stamped on decisions  
- Point-in-time features for ML training joins  
- Explicit freshness SLOs for nearline  

### 11.2 Poison-pill protection

Bad deploys, bad dictionaries, bad campaigns, bad embeddings: always have shadow → canary → bake → automatic rollback on guardrail breach.

### 11.3 Replay & audit

For trust-impacting systems (ads, safety, leaderboards, recommendations enforcement), keep enough audit to answer: “Why did the customer see X at time T?”

---

## 12. Security & Privacy Baseline (Amazon interview expectation)

| Control | Expectation |
|---------|-------------|
| Authn/z | Service-to-service auth; least privilege |
| PII | Purpose limitation; retention TTLs; access reviews |
| Encryption | In transit everywhere; at rest for stores |
| Tenancy | Marketplace/cell isolation where required |
| Secrets | No secrets in artifacts/logs |
| Abuse | Rate limits, bot controls, fraud hooks |
| Supply chain | Signed model/index/pack artifacts |

---

## 13. Cost & Capacity Planning Worksheet

### 13.1 Questions to answer aloud

1. What is the dominant cost driver (RAM, GPU, egress, human review, CDN)?  
2. What lever moves unit cost fastest (cache hit, candidate budget, sampling)?  
3. What is the 10× cost if you do nothing architectural?  
4. What is the 10× cost after the designed jump?  

### 13.2 Capacity formula templates

```text
online_instances ≈ peak_QPS × cost_per_req_cpu_sec / (cores × util_target)
cache_memory    ≈ hot_keys × bytes_per_key × overhead
train_budget    ≈ samples × epochs × $/GPU-hour
egress_monthly  ≈ QPS_avg × resp_bytes × 2.6e6
```

### 13.3 Frugality narrative

L6 candidates who only chase latency without unit economics miss Amazon’s bar. Tie every luxury (heavy DNN online, exact global rank, unsampled logs) to a cost and a customer benefit.

---

## 14. Progressive Scale Playbook (reuse verbally)

| Jump | Typical moves |
|------|----------------|
| 10× | Caching, shard split, async offload, sampling |
| 100× | Cells, hierarchical aggregation, distilled models, edge |
| 1,000× | On-device/edge intelligence, approximate algorithms, platformization |

Always pair each jump with **what breaks if you only scale vertically**.

---

## 15. Cross-Team Interfaces

Document the APIs you do *not* own but depend on. Interviewers listen for blast-radius thinking.

| Dependency | Failure mode | Your mitigation |
|------------|--------------|-----------------|
| Identity / auth | Outage | Cached tokens / degrade personalization |
| Catalog | Stale/OOS | Nearline status + kill list |
| Feature store | Slow | Budgets + cached features + fallback |
| Ads | Timeout | Organic-only path |
| Experimentation | Mis-assign | Sticky assignment cache |
| Logging | Backpressure | Sample + local buffer |

---


## 16. Additional Deep Q&A — Real-Time Leaderboard

### Q1. How do you encode tie-breaks without floats?

Use integer scores (fixed point) and compose a 64-bit sort key: high bits score, middle bits inverted timestamp, low bits player hash. Document overflow limits.

### Q2. WAL before or after ZADD visibility?

Pick explicitly: (A) WAL quorum then ZADD (stronger durability, higher latency); (B) ZADD then async WAL with risk window. For competitive cash/prize boards prefer A or sync replication.

### Q3. How do approximate global ranks work?

Maintain score histograms or count-min style rank sketches per shard; estimate rank as sum of counts above score + local rank. Product labels as approximate.

### Q4. Friends board write amplification?

If each score update fans out to all friends’ boards, costs explode. Cap friends, batch, or compute on read for small F; for large F use aspirational sample sets.

### Q5. Season archive format?

Snapshot top-N + player rank samples + full cold dump to S3/Parquet; keep metadata in OLTP for ‘my final rank’ lookups.

### Q6. How to handle clock skew on timestamps?

Prefer server receive time for tie-break, not client clock; bound match end times via game service.

### Q7. Prize payout boards vs casual?

Higher durability and audit; possibly stronger consistency cell; manual freeze before payout; dual control for edits.

### Q8. Multi-title platform tenancy?

board_id namespaces per title; noisy neighbor limits; separate Redis cells for AAA launches.

### Q9. Replay after data loss?

Rebuild from WAL; verify top-K checksums vs periodic snapshots; communicate rebuild ETA if public boards pause.

### Q10. Why not leader-election single primary for all writes?

Single primary doesn’t scale write spikes; shard by board; use primary per shard only.

## 17. Scenario Drills — Leaderboard

| Scenario | What you do | What you say |
|-----------|-------------|--------------|
| Season end write storm | Pre-split; disable friends fanout; cache top-K | Write path protected |
| Cheater in top-10 | Quarantine + rebuild segment | Audit + fairness messaging |
| Redis shard loss | Promote replica / replay WAL | Durability story |
| Wrong fence during season flip | Halt writes; repair; reopen | Fence tokens are sacred |

## 18. Final Checklist — Leaderboard

- [ ] Idempotent match updates
- [ ] Season fence design
- [ ] No single global ZSET at scale
- [ ] Top-K spectator cache
- [ ] Anti-cheat hooks
- [ ] Durability vs latency choice explicit
- [ ] Exact vs approximate rank product call
- [ ] Archive + payout audit path

## 19. Expanded Design Notes — Leaderboard

### 19.1 Board metadata state machine

States: `warming` → `open` → `frozen` → `archived`. Writes allowed only in `open` (and optionally `warming` for tests). `frozen` used pre-payout. Transitions require Season Manager fencing with monotonic epoch.

### 19.2 Query patterns

Top-K is hot and cacheable. My rank is per-player and should be served from the shard owning the player’s member. Nearby needs rank position then range. Avoid scanning.

### 19.3 Anti-cheat layering

L0 signature + schema. L1 rate/delta bounds. L2 async anomaly models. L3 human investigation for esports. Rewinds emit compensating events rather than silent deletes when possible.

### 19.4 Pub/sub invalidation

On top-K membership change, publish board_id invalidate. Spectators read cache. If pub/sub drops, short TTL self-heals. Do not push full top-K over pub/sub to millions—invalidate only.

### 19.5 Multi-region

Regional boards authoritative in-region. Global boards either eventual aggregation or pinned home region. Cross-region synchronous ZADD is a latency/availability trap.

### 19.6 Testing strategy

Deterministic fixtures for ties; chaos for shard loss; load tests replaying season endings; property tests for idempotency; fence cutover rehearsals.

### 19.7 Product analytics

Rank-up events drive engagement notifications—emit from stream processors, not inline with ZADD ack path beyond a lightweight event.

### 19.8 Evolution

Add secondary objectives (wins, KD) as display overlays without changing primary sort unless versioned board type changes.

## 20. Worked Example — Hot Global Board Split

10M players on one logical board. Shard into 16 partial ZSETs by `hash(player_id) % 16`. Each partial ~625K members ≈ 20MB+ overhead.

Top-100 global: fetch top-100 from each partial (1600 rows) and merge—cheap. Global rank for a player: local rank + estimate of how many players in other shards have higher score using per-shard score histograms (1–5KB each) refreshed every second.

---

## 21. API Error Codes (illustrative)

| Code | Meaning |
|------|---------|
| 409 idempotency conflict | Same match_id different payload |
| 423 season frozen | Fence rejects write |
| 429 rate limited | Player/server storm |
| 422 cheat reject | Gate rejection |
| 404 board unknown | Bad board_id |

---

*End of document — Real-Time Game Leaderboard (SDE III)*
