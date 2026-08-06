# System Design: Real-Time Game Leaderboard / Ranking (Amazon Games)

> **Focus areas:** Sorted sets · Sharding · Real-time updates · Top-K · Nearby ranks · Anti-cheat · Seasons · Spectator fanout
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split write vs read; sorted-set math; deal-breaker: single global ZSET at 100×
> **Interview theme:** Amazon SDE III / L6 — **Amazon Games** real-time leaderboard ownership—fairness under write spikes

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

Goal: Real-time game leaderboard: ingest scores, maintain rankings (global/regional/friends/seasonal), top-K and nearby, seasons, anti-cheat hooks.

### 1.0 What this is / is not
| Dimension | This | Not |
|-----------|------|-----|
| Job | Rank players by score fast | Matchmaking |
| Store | Sorted structures | SQL ORDER BY each read |
| Freshness | ≤1–2s typical | Daily batch only |

### 1.1 Functional requirements
Cover score semantics & ties, board types, top-K/my-rank/nearby, freshness, seasons, friends, anti-cheat, spectators, signed auth, regions, archives, admin, overlays.

**MVP:** signed ingest; seasonal global+regional; top-100; my rank; nearby; season archive; anti-cheat reject; metrics.
**Out of MVP:** matchmaking; broadcast graphics; TrueSkill-only ranking.

### 1.2 NFRs
State numeric latency/availability/freshness/cost/privacy targets for this domain. Prefer degrade-quality-before-total-outage except fail-closed trust gates (safety/privacy/kids/consent).

### 1.3 Cases
Enumerate happy paths plus storms/spikes, dependency timeouts, stale data, abuse/fraud, and trust edge cases — with explicit behavior per case (see deep Q&A and scenario runbooks below).

### 1.4 Progressive scale
| Jump | Forces |
|------|--------|
| 10× | Cache, shard, async, sample |
| 100× | Cells, distill, edge, hierarchy |
| 1,000× | On-device/approx/platform |

### 1.5 Constraints & repeat-back
Amazon themes: customer trust, ownership, frugality, mechanisms over meetings. Repeat scope in one breath.

---
## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes
| Class | What | Base peak | Plane |
|-------|------|-----------|-------|
| A | Score ingest | 50K/s | Online write |
| B | Top-K reads | 100K/s | Online read |
| C | My rank / nearby | 200K/s | Online read |
| D | WAL persist | ~50K/s | Durability |
| E | Season archive | Batch | Offline |
| F | Spectator fanout | Bursty | Pub/sub |

### 2.2 Memory
10M players × ~32B ≈ 320MB per fat board. Hot globals dominate RAM. `ZADD`/`ZREVRANK` are O(log N).

### 2.3 Latency budget (update)
Auth 5–10 → anti-cheat 5–15 → ZADD 5–20 → WAL 5–30 → **ack p99 ≤ 50–100ms**.

### 2.4 Spike math
Season ending: ~10× writes. Pre-split shards; disable friends fanout; cache top-K.

## 3. High-Level Design

### 3.1 Components
Ingest API → Anti-cheat Gate → Board Router → Rank Shards (ZSET) + WAL; Query API + Top-K Cache; Season Manager; Archive; Admin/Audit.

### 3.2 Score key
```text
sort_key = (score << time_bits) | (max_time - ts); member = player_id
```

### 3.3 API
`POST /boards/{id}/scores`, `GET /top`, `GET /rank`, `GET /nearby`, `POST /seasons/{id}/close`.

### 3.4 Tradeoffs
Sharded ZSETs + WAL — not SQL ORDER BY per read; not one global Redis; not unbounded friends fanout. Exact vs approximate global rank is an explicit product call at 100×+.

## 4. Architecture Diagram

```text
Game Services --signed--> Ingest --> Anti-Cheat --> Board Router
                                                    |
                                    +---------------+---------------+
                                    v               v               v
                               Rank Shard 0    Rank Shard 1    Rank Shard N
                                    |               |               |
                                    +------+--------+------+--------+
                                           v               v
                                       WAL/Kafka       Top-K Cache --> Query API
                                           |
                                      Season Manager --> Archive/S3
```

Season fence: open → frozen → archived; writes carry fence epoch.

## 5. Design Deep Dive

### 5.1 Invariants
Acked scores durable per class; idempotent match_id; season fence; deterministic ties; banned players out of public top-K.

### 5.2 Sharding
Shard by board_id. Hot global boards split into partials; top-K via merge; rank via histograms (label approximate).

### 5.3 Friends & spectators
Cap friends; on-read for small F. Spectators hit cached top-K with pub/sub invalidation.

### 5.4 Anti-cheat
Sync signature/rate/delta; async quarantine + compensating rewind with audit.

### 5.5 Progressive scale
10× shards+cache; 100× cells+hierarchy; 1,000× approximate ranks/segments.

### 5.6 Observability
update_p99, topk_p99, wal_lag, cheat_rejects, fence_rejects, memory_per_board.

## 6. Wrap-Up

### 6.1 What we designed
Signed score ingest, anti-cheat gates, sharded ZSETs, WAL, top-K cache, season fencing/archives, progressive scale.

### 6.2 Key decisions worth defending
1. Shard by board/cell
2. Idempotent match + season fence
3. Memory hot + WAL durable
4. Cache top-K spectators
5. Exact vs approx explicit at scale

### 6.3 Risks & follow-ups
- Hot board memory
- Friends fanout
- Cheat rewinds UX
- Cross-region exactness

### 6.4 Closer
> **Real-Time Game Leaderboard / Ranking**: explicit planes, SLOs, ownership, progressive scale, customer trust, unit economics.

---
## 7. Deeper / Related Interview Questions — Real-Time Leaderboard

**Q1. How do you prevent double-counting on client retries?**

**A:** Idempotency key = match_id (or match_id+stat_type). Store processed keys with TTL ≥ retry window; duplicates return prior ack without mutating score twice.

**Q2. What happens if WAL and memory diverge?**

**A:** Repair job replays WAL segments into rank engine; mark board `rebuilding`; serve last snapshot top-K read-only if needed; page if repair ETA exceeds SLO.

**Q3. Can players see rank updates before durability?**

**A:** Product choice. Prize boards: no. Casual: maybe optimistic UI with reconcile. State the choice and risk window.

**Q4. How do you cap board cardinality?**

**A:** Lifecycle TTLs; archive inactive modes; reject board_id explosion from misconfigured clients; quotas per title.

**Q5. How are ties shown in UX?**

**A:** Same rank number with deterministic secondary order, or dense vs competition ranking—pick a policy and keep it stable across seasons.

**Q6. Do you need transactions across friends boards?**

**A:** Avoid. Eventual consistency for friends boards is usually fine; don’t 2PC across thousands of friend ZSETs.

**Q7. How to support ‘rank percentile’?**

**A:** Histograms/sketches per board refreshed nearline; cheaper than exact rank for huge populations.

**Q8. Security model for ingest?**

**A:** mTLS from game servers; per-title keys; no trust of game clients for authoritative scores.

---
## 8. Appendices

### A — Glossary
| Term | Meaning |
|------|---------|
| Cell | Failure-isolated unit |
| Nearline | Minutes-latency path |
| Canary | Partial bake |
| Deal-breaker | Non-negotiable bad design |
| Two-pizza | Ownership team with pager |

### B — Oncall checklist
- [ ] SLOs green
- [ ] Rollback armed
- [ ] Kill switches known
- [ ] Cost dashboards
- [ ] Privacy/safety tested

### F — Topic closer checklist
- [ ] Shard by board/cell
- [ ] Idempotent match + season fence
- [ ] Memory hot + WAL durable
- [ ] Cache top-K spectators
- [ ] Exact vs approx explicit at scale

## Deep Technical Notes — Real-Time Leaderboard

### Ingest authentication detail

Game services sign payloads with title keys rotated via KMS-like service. Ingest verifies signature, timestamp skew window, and schema. Rejects replayed old timestamps outside window. This belongs before anti-cheat ML—cheap crypto checks first.

Separate ‘server authoritative’ modes from any rare client-reported stats. If client-reported ever exists, treat as untrusted side channel needing heavier validation—not for prize boards.

### Sorted-set memory management

Track bytes per board; alert on outliers; offload cold boards to snapshot+reload; compress member payloads; avoid storing large JSON in ZSET members—keep side KV for display names.

At season end, archive then delete hot keys deliberately; don’t rely on memory pressure eviction for correctness.

### Partial board merge algorithm

For top-K: pull top-K from each partial shard, merge by sort key, truncate K. For rank estimate: sum histogram buckets strictly above score + local rank adjustment. Document error bounds.

Refresh histograms every 1s via shard-local aggregation; accept brief inconsistency under write storms.

### Anti-cheat rewind protocol

Mark player quarantined; emit compensating negative events or rebuild from WAL excluding bad matches; record audit with evidence refs; notify title ops; recompute affected top-K caches.

Never silent-delete without audit on competitive modes—trust and appeals matter.

### Season fencing edge cases

Late match results after freeze: policy either reject or spill to ‘pending review’ queue. Dual-write windows are dangerous—prefer hard fence with grace rejects.

Clock issues: fence based on Season Manager logical epoch, not only wall clock on ingest nodes.

### Multi-region story

Regional leaderboards home in region. Global eventual aggregator consumes regional streams. Clients read global with higher staleness SLO. Avoid cross-region sync ZADD on hot path.

### Observability specifics

Metrics: update_p99, zadd_errors, wal_lag, topk_cache_hit, rank_p99, cheat_reject_rate, season_fence_rejects, memory_per_board_bytes, rebuild_age.

Tracing: ingest→gate→router→shard→wal. Exemplars on slow matches.

### Platform API for titles

Titles declare board configs (sort, season length, approx rank yes/no, durability class). Platform enforces quotas. This is how Amazon Games avoids each title reinventing Redis scripts.

## Interview Cards — Real-Time Leaderboard

### Card 1: How do you prevent double-counting on client retries?

Idempotency key = match_id (or match_id+stat_type). Store processed keys with TTL ≥ retry window; duplicates return prior ack without mutating score twice.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: What happens if WAL and memory diverge?

Repair job replays WAL segments into rank engine; mark board `rebuilding`; serve last snapshot top-K read-only if needed; page if repair ETA exceeds SLO.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Can players see rank updates before durability?

Product choice. Prize boards: no. Casual: maybe optimistic UI with reconcile. State the choice and risk window.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: How do you cap board cardinality?

Lifecycle TTLs; archive inactive modes; reject board_id explosion from misconfigured clients; quotas per title.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: How are ties shown in UX?

Same rank number with deterministic secondary order, or dense vs competition ranking—pick a policy and keep it stable across seasons.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: Do you need transactions across friends boards?

Avoid. Eventual consistency for friends boards is usually fine; don’t 2PC across thousands of friend ZSETs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: How to support ‘rank percentile’?

Histograms/sketches per board refreshed nearline; cheaper than exact rank for huge populations.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Security model for ingest?

mTLS from game servers; per-title keys; no trust of game clients for authoritative scores.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: How do you load test fairly?

Replay season-end traces; include hot boards and cold boards; verify idempotency under retry storms.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: What is the deal-breaker?

Single Redis ZSET for all titles/global players at 100×, or SQL ORDER BY on every read.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: How do notifications integrate?

Async consumer on score events triggers ‘you moved up’—never block ZADD ack on push notification fanout.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: GDPR/deletion?

Delete player member from hot boards; schedule cold archive scrub; retain aggregates without identifiers where required.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Cross-title tournaments?

Separate board type with explicit participant registry; don’t overload casual global board semantics.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Why shard by board_id first?

Natural isolation, blast radius limits, simple routing; only split single hot boards when metrics demand.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: How do you version sort key encoding?

board schema_version; never reinterpret old members with new encoding without migration job.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Spectator apps at Twitch scale?

Edge cached top-K JSON; short TTL; invalidate on change; CDN for anonymized public boards.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.
## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + Amazon ownership lens |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive (reliability/scale/ML/privacy) |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact; lock MVP; split load classes; name pager owners; refuse deal-breakers.

---

## 10. Operability

### Golden signals
Latency, traffic, errors, saturation, freshness, trust incidents.

### Rollback ladder
Flag off → revert artifact → shed/reduce K → cell isolate → postmortem with trust section.

### Kill switches
Disable optional stage; freeze nearline; revert pointer; shed traffic; isolate cell.

### Security/privacy baseline
Authn/z, PII TTLs, encryption, cell isolation, signed artifacts, abuse limits.

### Cost worksheet
Dominant cost driver; fastest unit-cost lever; 10× cost with/without architectural jump.

```text
instances ≈ peak_QPS × cpu_sec / (cores × util)
```

### Progressive scale
10× cache/shard/async; 100× cells/distill/edge; 1,000× on-device/approximate/platform.

### Cross-team deps
Identity, catalog, feature store, ads, experimentation, logging — each with failure mitigation.

---

## More Interview Q&A — Real-Time Leaderboard

**Q1. How do you prevent double-counting on client retries?**

**A:** Idempotency key = match_id (or match_id+stat_type). Store processed keys with TTL ≥ retry window; duplicates return prior ack without mutating score twice.

**Q2. What happens if WAL and memory diverge?**

**A:** Repair job replays WAL segments into rank engine; mark board `rebuilding`; serve last snapshot top-K read-only if needed; page if repair ETA exceeds SLO.

**Q3. Can players see rank updates before durability?**

**A:** Product choice. Prize boards: no. Casual: maybe optimistic UI with reconcile. State the choice and risk window.

**Q4. How do you cap board cardinality?**

**A:** Lifecycle TTLs; archive inactive modes; reject board_id explosion from misconfigured clients; quotas per title.

**Q5. How are ties shown in UX?**

**A:** Same rank number with deterministic secondary order, or dense vs competition ranking—pick a policy and keep it stable across seasons.

**Q6. Do you need transactions across friends boards?**

**A:** Avoid. Eventual consistency for friends boards is usually fine; don’t 2PC across thousands of friend ZSETs.

**Q7. How to support ‘rank percentile’?**

**A:** Histograms/sketches per board refreshed nearline; cheaper than exact rank for huge populations.

**Q8. Security model for ingest?**

**A:** mTLS from game servers; per-title keys; no trust of game clients for authoritative scores.

**Q9. How do you load test fairly?**

**A:** Replay season-end traces; include hot boards and cold boards; verify idempotency under retry storms.

**Q10. What is the deal-breaker?**

**A:** Single Redis ZSET for all titles/global players at 100×, or SQL ORDER BY on every read.

**Q11. How do notifications integrate?**

**A:** Async consumer on score events triggers ‘you moved up’—never block ZADD ack on push notification fanout.

**Q12. GDPR/deletion?**

**A:** Delete player member from hot boards; schedule cold archive scrub; retain aggregates without identifiers where required.

**Q13. Cross-title tournaments?**

**A:** Separate board type with explicit participant registry; don’t overload casual global board semantics.

**Q14. Why shard by board_id first?**

**A:** Natural isolation, blast radius limits, simple routing; only split single hot boards when metrics demand.

**Q15. How do you version sort key encoding?**

**A:** board schema_version; never reinterpret old members with new encoding without migration job.

**Q16. Spectator apps at Twitch scale?**

**A:** Edge cached top-K JSON; short TTL; invalidate on change; CDN for anonymized public boards.

## Deep Technical Addenda — Real-Time Leaderboard

### Ingest authentication detail

Game services sign payloads with title keys rotated via KMS-like service. Ingest verifies signature, timestamp skew window, and schema. Rejects replayed old timestamps outside window. This belongs before anti-cheat ML—cheap crypto checks first.

Separate ‘server authoritative’ modes from any rare client-reported stats. If client-reported ever exists, treat as untrusted side channel needing heavier validation—not for prize boards.

### Sorted-set memory management

Track bytes per board; alert on outliers; offload cold boards to snapshot+reload; compress member payloads; avoid storing large JSON in ZSET members—keep side KV for display names.

At season end, archive then delete hot keys deliberately; don’t rely on memory pressure eviction for correctness.

### Partial board merge algorithm

For top-K: pull top-K from each partial shard, merge by sort key, truncate K. For rank estimate: sum histogram buckets strictly above score + local rank adjustment. Document error bounds.

Refresh histograms every 1s via shard-local aggregation; accept brief inconsistency under write storms.

### Anti-cheat rewind protocol

Mark player quarantined; emit compensating negative events or rebuild from WAL excluding bad matches; record audit with evidence refs; notify title ops; recompute affected top-K caches.

Never silent-delete without audit on competitive modes—trust and appeals matter.

### Season fencing edge cases

Late match results after freeze: policy either reject or spill to ‘pending review’ queue. Dual-write windows are dangerous—prefer hard fence with grace rejects.

Clock issues: fence based on Season Manager logical epoch, not only wall clock on ingest nodes.

### Multi-region story

Regional leaderboards home in region. Global eventual aggregator consumes regional streams. Clients read global with higher staleness SLO. Avoid cross-region sync ZADD on hot path.

### Observability specifics

Metrics: update_p99, zadd_errors, wal_lag, topk_cache_hit, rank_p99, cheat_reject_rate, season_fence_rejects, memory_per_board_bytes, rebuild_age.

Tracing: ingest→gate→router→shard→wal. Exemplars on slow matches.

### Platform API for titles

Titles declare board configs (sort, season length, approx rank yes/no, durability class). Platform enforces quotas. This is how Amazon Games avoids each title reinventing Redis scripts.

## Tradeoff Matrices — Real-Time Leaderboard

### Consistency vs latency

| Choice | Latency | Correctness | Use when |
|--------|---------|-------------|----------|
| Sync durable then serve | Higher | Stronger | Money/trust boards, enforcement |
| Serve then async durable | Lower | Risk window | Casual UX with repair |
| Cached eventual | Lowest | Stale OK | Top-K spectators, suggest head |

### Exact vs approximate

| Choice | Cost | UX risk | Use when |
|--------|------|---------|----------|
| Exact | High at scale | Low confusion | Small boards / cells |
| Approximate labeled | Lower | Need UX copy | Global 100× ranks |
| Hierarchical | Medium | Ops complexity | Multi-region global |

### Personalization strength

| Choice | Lift | Privacy/cost | Use when |
|--------|------|--------------|----------|
| None / segment | Low | Best privacy | Kids, restricted |
| Light re-rank | Medium | Good | Default |
| Heavy private retrieve | High potential | Costly/risky | Rare, budgeted |

## Operability Addenda — Real-Time Leaderboard

### Deploy pipeline

```text
build artifact → static validation → shadow → canary → bake → full
                     ↓ fail              ↓ guardrail fail
                  reject              auto rollback
```

### Guardrail examples

- p99 latency regression > threshold  
- empty/fallback rate rise  
- safety/privacy denials anomaly  
- undo/regret/complaint spikes  
- unit cost spike  

### Kill switches (name them in interview)

1. Disable optional stage (fuzzy, ads, assist, personalization)  
2. Freeze nearline updates  
3. Revert artifact pointer  
4. Shed traffic / reduce K  
5. Cell isolation  

## Worked Capacity Narrative — Real-Time Leaderboard

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/edge hit-rate lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Real-Time Leaderboard

Amazon interviews reward explicit trust reasoning: wrong ranks, unsafe suggestions, privacy leaks, bad fits/returns, or ads without consent are not “model issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Real-Time Leaderboard

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, distilled models, edge/client head  
- **1,000×:** on-device/edge intelligence, approximate algorithms, platform multi-tenant cells  

For each jump, state **what breaks if you only add servers**.

---

## Supplemental Depth Pack — Real-Time Leaderboard
### S1. Authoritative scores

Only game servers sign scores. Clients never authoritatively set competitive scores. Verify skew windows and schemas before anti-cheat ML.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Idempotency & durability

match_id idempotency. Choose WAL-before-visible for prize boards. Casual boards may async WAL with explicit risk window.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Season fencing

Logical epoch beats wall clock. States warming/open/frozen/archived. Late results go to reject or review—not silent dual-write.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Sharding strategy

Shard by board_id first. Split single hot global boards into partials + merge/histograms only when metrics demand.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Spectator scale

Cache top-K; invalidate via pub/sub; short TTL heals lost invalidations. Never per-spectator ZRANGE at Twitch scale.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Friends boards

Cap friends; on-read for small F; avoid write fanout explosions; eventual consistency OK.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Anti-cheat rewind

Quarantine + compensating events or WAL rebuild excluding bad matches; audit evidence; competitive messaging.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Platformization

Amazon Games shared leaderboard platform with per-title cells, durability classes, and quotas.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Scenario Runbooks — Real-Time Leaderboard

| Scenario | Immediate action | Customer impact | Follow-up |
|-----------|------------------|-----------------|----------|
| Season end storm | Pre-split; disable friends fanout; cache top-K | Preserve trust/UX | Postmortem + guardrail |
| Cheater in top-10 | Quarantine + rebuild + audit | Preserve trust/UX | Postmortem + guardrail |
| Shard loss | Replica promote / WAL replay | Preserve trust/UX | Postmortem + guardrail |
| Fence bug | Halt writes; repair; reopen | Preserve trust/UX | Postmortem + guardrail |
| Prize payout | Freeze; snapshot; dual-control edits | Preserve trust/UX | Postmortem + guardrail |
| Global approx rank | Histograms; label approximate in UX | Preserve trust/UX | Postmortem + guardrail |

## Rapid-Fire Q&A — Real-Time Leaderboard

**RQ1. Why does 'Authoritative scores' matter in an L6 interview?**

**A:** Only game servers sign scores. Clients never authoritatively set competitive scores. Verify skew windows and schemas before anti-cheat ML. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Authoritative scores' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Authoritative scores' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Idempotency & durability' matter in an L6 interview?**

**A:** match_id idempotency. Choose WAL-before-visible for prize boards. Casual boards may async WAL with explicit risk window. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Idempotency & durability' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Idempotency & durability' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Season fencing' matter in an L6 interview?**

**A:** Logical epoch beats wall clock. States warming/open/frozen/archived. Late results go to reject or review—not silent dual-write. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Season fencing' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Season fencing' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Sharding strategy' matter in an L6 interview?**

**A:** Shard by board_id first. Split single hot global boards into partials + merge/histograms only when metrics demand. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Sharding strategy' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Sharding strategy' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Spectator scale' matter in an L6 interview?**

**A:** Cache top-K; invalidate via pub/sub; short TTL heals lost invalidations. Never per-spectator ZRANGE at Twitch scale. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Spectator scale' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Spectator scale' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Friends boards' matter in an L6 interview?**

**A:** Cap friends; on-read for small F; avoid write fanout explosions; eventual consistency OK. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Friends boards' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Friends boards' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Anti-cheat rewind' matter in an L6 interview?**

**A:** Quarantine + compensating events or WAL rebuild excluding bad matches; audit evidence; competitive messaging. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Anti-cheat rewind' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Anti-cheat rewind' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'Platformization' matter in an L6 interview?**

**A:** Amazon Games shared leaderboard platform with per-title cells, durability classes, and quotas. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'Platformization' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'Platformization' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Real-Time Leaderboard

### Walkthrough beat 1

In beat 1, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

In beat 2, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

In beat 3, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

In beat 4, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

In beat 5, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

In beat 6, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

In beat 7, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

In beat 8, narrate the customer journey through Real-Time Leaderboard: the request enters the system, crosses an ownership boundary, hits a budgeted dependency, and returns with an explicit degradation story if something fails. Mention the artifact version stamped on the response/decision and the metric you would watch live.

Call out one tradeoff you are making (latency vs freshness, exact vs approximate, personalization vs privacy) and why Amazon customer obsession prefers that tradeoff here.


## Pre-Onsite Checklist — Real-Time Leaderboard

- [ ] Can explain **Authoritative scores** with numbers and a deal-breaker
- [ ] Can explain **Idempotency & durability** with numbers and a deal-breaker
- [ ] Can explain **Season fencing** with numbers and a deal-breaker
- [ ] Can explain **Sharding strategy** with numbers and a deal-breaker
- [ ] Can explain **Spectator scale** with numbers and a deal-breaker
- [ ] Can explain **Friends boards** with numbers and a deal-breaker
- [ ] Can explain **Anti-cheat rewind** with numbers and a deal-breaker
- [ ] Can explain **Platformization** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **Season end storm**
- [ ] Has a 30-second runbook for **Cheater in top-10**
- [ ] Has a 30-second runbook for **Shard loss**
- [ ] Has a 30-second runbook for **Fence bug**
- [ ] Has a 30-second runbook for **Prize payout**
- [ ] Has a 30-second runbook for **Global approx rank**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.


### Extra drill

Rehearse explaining Real-Time Leaderboard to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture diagram box that owns the risk, then the kill switch. Mention what you would not build.

*End of document — Real-Time Game Leaderboard / Ranking (Amazon Games) (SDE III)*
