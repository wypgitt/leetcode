#!/usr/bin/env python3
"""Remaining six Amazon system design document builders."""
from __future__ import annotations

from textwrap import dedent

# Re-use helpers by duplicating minimal ones to avoid circular imports issues
# when generate_all imports this module.


def qa(items, start=1):
    parts = []
    for i, (q, a) in enumerate(items, start):
        parts.append(f"**Q{i}. {q}**\n\n**A:** {a}\n")
    return "\n".join(parts)


TOC = dedent(
    """\
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
    """
)


def header(title, focus, theme, quality):
    return dedent(
        f"""\
        # System Design: {title}

        > **Focus areas:** {focus}
        > **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
        > **Quality bar:** {quality}
        > **Interview theme:** Amazon SDE III / L6 — {theme}

        ---

        """
    )


def wrapup(name, designed, decisions, risks):
    dec = "\n".join(f"{i}. {d}" for i, d in enumerate(decisions, 1))
    rsk = "\n".join(f"- {r}" for r in risks)
    return dedent(
        f"""\
        ## 6. Wrap-Up

        ### 6.1 What we designed

        {designed}

        ### 6.2 Key decisions worth defending

        {dec}

        ### 6.3 Risks & follow-ups

        {rsk}

        ### 6.4 How to present in 45 minutes

        | Time | Topic |
        |------|-------|
        | 0–5 | Scope, requirements, ownership |
        | 5–12 | Estimation + progressive scale |
        | 12–22 | HLD + ASCII architecture |
        | 22–35 | Deep dive |
        | 35–45 | Tradeoffs + Q&A traps |

        ### 6.5 One-sentence closer

        > We designed **{name}** with explicit planes, SLOs, ownership boundaries, and a progressive scale story that protects customer experience while controlling cost and ops load.

        ---
        """
    )


def appendices(extra):
    return dedent(
        f"""\
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

        {extra}

        """
    )


def extended_block(title: str, notes: list[tuple[str, str]]) -> str:
    parts = [f"## Extended Notes — {title}\n"]
    for i, (h, body) in enumerate(notes, 1):
        parts.append(f"### E{i}. {h}\n\n{body}\n")
    parts.append("---\n")
    return "\n".join(parts)


# =============================================================================
# 2. Leaderboard
# =============================================================================


def build_leaderboard() -> str:
    h = header(
        "Real-Time Game Leaderboard / Ranking (Amazon Games)",
        "Sorted sets · Sharding · Real-time updates · Top-K · Nearby ranks · Anti-cheat hooks · Season resets · Spectator fanout · Progressive scale",
        "**Amazon Games / Twitch-adjacent** real-time leaderboard ownership—correctness under write spikes, fair competition, and cost-efficient reads",
        "Split write ingest vs read fanout, correct sorted-set math, deal-breakers for “single Redis global ZSET” at 100×",
    )
    s1 = dedent(
        """\
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
        """
    )
    s2 = dedent(
        """\
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
        """
    )
    s3 = dedent(
        """\
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
        """
    )
    s4 = dedent(
        """\
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
        """
    )
    s5 = dedent(
        """\
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
        """
    )
    s7 = "## 7. Deeper / Related Interview Questions\n\n"
    s7 += "### 7.1 Core\n\n" + qa(
        [
            (
                "Why not MySQL ORDER BY score LIMIT 100?",
                "Write-heavy competitive games need log-N updates and fast rank ops. SQL can archive/analytics but not hot path at 50K+ updates/s with rank queries.",
            ),
            (
                "How do you shard a single hot global board?",
                "Hash players into partial ZSETs; top-K via merge of per-shard tops; rank via local rank + offsets or periodic global histograms for approximate rank.",
            ),
            (
                "Exact global rank vs approximate?",
                "Exact is costly at extreme scale. Many games show exact within shard/region and approximate globally—product decision, say it aloud.",
            ),
            (
                "Season reset without downtime?",
                "Fence token + dual board versions; archive async; read-only old board; never flip by wiping memory without versioning.",
            ),
            (
                "Idempotency?",
                "match_id unique key; duplicate posts return same ack without double counting.",
            ),
            (
                "Spectator 1M readers of top-10?",
                "Cache top-K with short TTL + pub/sub invalidation; don’t hit ZSET per spectator.",
            ),
            (
                "Friends leaderboard at Facebook scale?",
                "Not Amazon Games usual—but if needed, cap friends, precompute, or aspirational boards; avoid full graph join online.",
            ),
            (
                "Cheater already on board?",
                "Quarantine flag + rebuild segment from WAL excluding events; audit trail; visible removal messaging policy.",
            ),
        ]
    )
    s7 += "\n### 7.2 Traps\n\n" + qa(
        [
            (
                "Single Redis ZSET for everything?",
                "Deal-breaker at 100×—hot key, memory, blast radius. Shard by board and cell by title.",
            ),
            (
                "Strongly consistent global ranks across regions?",
                "Expensive; prefer regional authority + async global aggregation.",
            ),
            (
                "Store every historical rank change in Redis?",
                "No—hot current season in memory; history in cold store.",
            ),
        ],
        9,
    )
    notes = extended_block(
        "Real-Time Leaderboard",
        [
            (
                "Composite scores",
                "Discuss encoding score+time without floating point pain. Integer millis and fixed-point scores.",
            ),
            (
                "Write auth",
                "Game server secrets vs player-submitted scores. Never trust client score without server authority.",
            ),
            (
                "Twitch / Prime Gaming",
                "Optional event topics for drops eligibility based on rank thresholds—consume via bus, don’t put Twitch in the hot ZADD path.",
            ),
            (
                "Memory eviction",
                "Cold boards offload to snapshots; reload on demand. Keep only active seasons hot.",
            ),
            (
                "Legal / fairness communications",
                "When ranks rewind due to cheat bans, product messaging matters as much as tech.",
            ),
            (
                "Multi-mode boards",
                "board_id encodes game|mode|region|season. Cardinality control via lifecycle TTLs.",
            ),
            (
                "Testing",
                "Deterministic tie fixtures; season fence chaos tests; idempotency fuzzing; load replay of season endings.",
            ),
            (
                "Cost metric",
                "USD per million updates + RAM per active board. Archive aggressively.",
            ),
            (
                "Nearby UX",
                "Show denser competition around player; motivates engagement more than only top-100.",
            ),
            (
                "Cross-title platform",
                "Shared leaderboard platform with per-title cells—Amazon Games org pattern.",
            ),
            (
                "Backup restore",
                "Restore from WAL+snapshot to last ack; rebuild caches; verify checksum of top-K.",
            ),
            (
                "Rate limits",
                "Per player update rate; per match once; burst tokens for server recoveries.",
            ),
            (
                "Data model evolution",
                "Add secondary scores (wins) via versioned entry payloads without breaking sort.",
            ),
            (
                "Privacy",
                "Friends boards need authz; don’t leak quiet players’ ranks publicly if opted private.",
            ),
            (
                "Comparison to chess ratings",
                "Elo/TrueSkill is a different problem (skill estimation). Leaderboards are ordered scores; they can display MMR but storage path differs.",
            ),
        ],
    )
    ap = appendices(
        dedent(
            """\
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
            """
        )
    )
    wrap = wrapup(
        "Real-Time Game Leaderboard",
        "A **real-time leaderboard platform** for Amazon Games: signed score ingest, anti-cheat gates, sharded sorted-set rank engines, durable WAL, top-K cache, season fencing/archives, friends boards, progressive scale.",
        [
            "Shard by board/cell; no single global ZSET",
            "Idempotent match updates + season fences",
            "Memory hot ranks + WAL durability",
            "Cache top-K for spectator storms",
            "Exact vs approximate rank as explicit product choice at extreme scale",
        ],
        [
            "Hot board memory explosions",
            "Friends fanout costs",
            "Cheat-driven rewinds UX",
            "Cross-region global exactness pressure",
        ],
    )
    end = "\n*End of document — Real-Time Game Leaderboard (SDE III)*\n"
    return "\n".join([h, TOC, s1, s2, s3, s4, s5, wrap, s7, ap, notes, end])


# =============================================================================
# 3. Alexa advertising workflow
# =============================================================================


def build_alexa() -> str:
    h = header(
        "Alexa Triggering / Advertising Workflow (Voice → Intent → Ad Decisioning → Measurement)",
        "Voice trigger · ASR/NLU · Intent routing · Ad decisioning · Privacy · Consent · Measurement · Brand safety · Progressive scale",
        "**Alexa / Advertising** workflow ownership—privacy-first voice ad experiences with measurable outcomes and clear trust constraints",
        "Separate voice plane from ads plane, privacy non-negotiables, deal-breakers for “send raw audio to advertisers”",
    )
    s1 = dedent(
        """\
        ## 1. Clarify Requirements (Interview Q&A)

        Goal: design the **Alexa-triggering advertising workflow**: wake/trigger → ASR → NLU/intent → eligibility → ad decisioning → TTS/response rendering → impression/outcome measurement—under strict **privacy, consent, and brand-safety** constraints.

        ### 1.0 What this is / is not

        | Dimension | **This doc** | Not this |
        |-----------|--------------|----------|
        | Job | Orchestrate voice→ad decision→measure | Train foundation ASR models from scratch |
        | Ads | Alexa media / sponsored skills / shopping hints | Programmatic web display ads full stack |
        | Privacy | On-device/edge minimization; purpose limitation | Raw audio sharing with advertisers |
        | Success | Relevant, consented, brand-safe, measurable | Max ads regardless of trust |

        ### 1.1 Functional Requirements

        | # | Question | Answer | Implication |
        |---|----------|--------|-------------|
        | F1 | Triggers? | Wake word, push-to-talk, routine, skill invoke | Trigger metadata |
        | F2 | Understanding? | ASR text + NLU intent/slots | Intent graph |
        | F3 | When ads? | Eligible intents / content slots only | Policy engine |
        | F4 | Ad types? | Audio ads, sponsored skill suggestion, shopping recommendation | Creative renderer |
        | F5 | Decisioning? | Auction / curated + relevance | Ads decision service |
        | F6 | Consent? | Household/user privacy settings | Consent service hard gate |
        | F7 | Measurement? | Played, completed, opt-out, conversion hooks | Privacy-preserving events |
        | F8 | Kids profiles? | Strict no personalized ads mode | Policy packs |
        | F9 | Latency? | Keep conversational | Budget ASR∥ads prefetch |
        | F10 | Brand safety? | Category blocks, keyword, contextual | Safety filters |
        | F11 | Frequency cap? | Household/device caps | Cap store |
        | F12 | Fallback? | Content without ad | Never block answer for ad fail |
        | F13 | Advertiser reporting? | Aggregated | No user-level raw audio |
        | F14 | A/B? | Experiment framework | Layer experiments |
        | F15 | Multi-locale? | Yes | Locale policy packs |

        **MVP:** trigger→ASR/NLU→eligibility→decision→render audio/suggestion→measure play/complete; consent+kids gates; frequency caps; brand safety; degrade to no-ad.

        **Out of MVP:** selling raw transcripts to third parties; on-device full auction; cross-home identity graphs without consent.

        ### 1.2 NFRs

        | # | Target |
        |---|--------|
        | N1 End-to-end response | Conversational; ads path p99 add ≤ 50–100ms beyond content |
        | N2 Privacy | Purpose limitation; minimization; retention TTLs |
        | N3 Availability | Ads failure never fails user answer |
        | N4 Measurement integrity | Fraud-resistant aggregated reporting |
        | N5 Kids / sensitive | Fail closed |
        | N6 Audit | Policy version on each decision |

        ### 1.3 Cases

        Happy: “play weather” → content + eligible trailing brand audio; shopping intent → sponsored product with disclosure; opt-out → no personalized ads.

        | Case | Behavior |
        |------|----------|
        | Consent off | No personalized ads |
        | Kids profile | No personalized ads; limited/none per policy |
        | ASR low confidence | Skip ads; clarify |
        | Ads timeout | Serve content only |
        | Sensitive intent (medical/finance) | Suppress ads |
        | Frequency exceeded | Skip |
        | Household multi-user | Speaker recognition optional; default household policy |

        ### 1.4 Scales

        | Metric | Base | 10× | 100× | 1,000× |
        |--------|------|-----|------|--------|
        | Voice requests/s | 100K | 1M | 10M | 100M |
        | Ad-eligible/s | 20K | 200K | 2M | 20M |
        | Decision QPS | 20K | 200K | 2M | cells |
        | Measurement events/s | 50K | 500K | 5M | aggregated edge |

        ### 1.5 Constraints

        - **Never** send raw audio to advertisers.
        - Ads are a guest in the voice loop—content reliability first.
        - Privacy legal packs differ by country.

        ---
        """
    )
    s2 = dedent(
        """\
        ## 2. Back-of-the-Envelope Estimation

        ### 2.1 Planes

        | Plane | What |
        |-------|------|
        | Voice understanding | ASR/NLU |
        | Policy / consent | Eligibility |
        | Ads decision | Auction/retrieval |
        | Render | TTS / skill directive |
        | Measurement | Events → aggregate |

        ### 2.2 Latency budget

        | Step | Budget |
        |------|--------|
        | Trigger + streaming ASR partial | overlapping |
        | NLU intent | 20–40 ms |
        | Consent + policy | 5–15 ms |
        | Ad decision | 20–40 ms |
        | Merge into response plan | 5 ms |
        | **Ads additive p99** | **≤ 50–100 ms** |

        Prefetch ads on speculative intents when safe.

        ### 2.3 Privacy math

        Prefer on-device wake; cloud ASR with retention limits; measurement as counts with differential privacy noise for small cells.

        ---
        """
    )
    s3 = dedent(
        """\
        ## 3. High-Level Design

        ### 3.1 Components

        | Component | Role |
        |-----------|------|
        | Device / Wake | Trigger, capture policy |
        | Speech Plane | ASR, NLU, dialog |
        | Privacy & Consent Service | Gates |
        | Eligibility / Policy Engine | Intent allowlists, sensitive categories |
        | Ads Decisioning | Retrieve + score + auction |
        | Creative / TTS Renderer | Directives |
        | Frequency Cap Store | Household caps |
        | Measurement Pipeline | Play/complete/convert (aggregated) |
        | Advertiser Reporting | Aggregates only |
        | Experimentation | Layers |
        | Audit Log | decision_id, policy_version |

        ### 3.2 Workflow

        ```text
        Trigger → ASR → NLU intent
          → Consent/Policy eligibility
          → if eligible: Decisioning (retrieve → rank → auction → brand safety)
          → Response planner merges content + optional ad directive
          → Render (TTS/audio)
          → Measurement events (privacy-preserving)
        ```

        ### 3.3 API (internal)

        ```text
        POST /ads/decide
          { request_id, intent, slots_redacted, locale, household_token, consent_flags }
        → { ad_creative_ref?, disclosure, bid_meta, decision_id, ttl }
        ```

        Note: **redacted slots**—no unnecessary PII.

        ### 3.4 Tradeoffs

        | Decision | Choose | Deal-breaker |
        |----------|--------|--------------|
        | Audio to advertisers | **Never** | Raw audio sharing |
        | Ads vs content | Content wins on timeout | Block answer for ads |
        | Identity | Household token + consent | Silent cross-home graph |
        | Measurement | Aggregated + fraud checks | User-level transcript feeds |
        | Kids | Fail closed | Personalized kids ads |

        ---
        """
    )
    s4 = dedent(
        """\
        ## 4. Architecture Diagram

        ```text
        Device Wake/PTT --> Speech Gateway --> ASR --> NLU --> Dialog Manager
                                                              |
                                                              v
                                                    Privacy/Consent Gate
                                                              |
                                              eligible? no --> Content-only Response
                                              yes
                                                              v
                                                    Policy/Eligibility
                                                              v
                                                    Ads Decisioning
                                                 (retrieve/rank/auction/safety)
                                                              v
                                                    Response Planner -----> TTS/Directives
                                                              |
                                                              v
                                                      Measurement (agg)
        ```

        ### 4.2 Privacy boundary

        ```text
        [Device audio] -> Speech Plane (purpose: understand)
                \\-> NOT to Advertisers
        [Redacted intent features] -> Ads Decisioning
        [Aggregates] -> Advertiser Reporting
        ```

        ---
        """
    )
    s5 = dedent(
        """\
        ## 5. Design Deep Dive

        ### 5.1 Invariants

        1. Ads never receive raw audio.
        2. Consent/kids gates non-bypassable.
        3. Content response succeeds if ads fail.
        4. Every ad decision has decision_id + policy_version.
        5. Sensitive intents suppress ads.

        ### 5.2 Decisioning internals

        Retrieve campaigns by locale/intent category → filter consent/brand safety/frequency → score relevance → auction → choose creative → return directive.

        ### 5.3 Measurement & fraud

        Client/device play signals signed; dedupe; bot detection; report aggregates with thresholds; delay reports to reduce linkage.

        ### 5.4 Progressive scale

        10×: cache eligibility; speculative prefetch. 100×: regional decision cells. 1,000×: on-device eligibility + edge decision tokens.

        ### 5.5 Ownership

        Speech owns ASR/NLU SLOs; Ads owns decision/measurement; Privacy owns policy packs; shared contract on redacted feature schema.

        ---
        """
    )
    s7 = "## 7. Deeper / Related Interview Questions\n\n" + qa(
        [
            (
                "Why separate speech and ads planes?",
                "Different trust boundaries, SLOs, and failure modes. Speech outage is existential; ads must be optional. Privacy minimization requires a hard boundary.",
            ),
            (
                "Can advertisers target by transcript keywords?",
                "Only via redacted, policy-approved features/categories—not raw transcripts dumps. Prefer contextual intent categories.",
            ),
            (
                "How do frequency caps work across devices in a home?",
                "Household graph with consent; caps store keyed by household_token; eventual consistency OK if slightly under-cap.",
            ),
            (
                "Kids mode?",
                "Fail closed on personalized ads; follow marketplace/legal packs; separate profile flag from NLU.",
            ),
            (
                "Ads timeout strategy?",
                "Hard deadline; return content-only; measure ads_timeout_rate.",
            ),
            (
                "How is this different from retail sponsored products?",
                "Modality (audio), disclosure UX, privacy sensitivity of microphones, household identity, and conversational interruption costs.",
            ),
            (
                "Measurement without stalking?",
                "Aggregates, cohort thresholds, limited retention, no raw audio, fraud filters, optional on-device contribution.",
            ),
            (
                "Deal-breaker?",
                "Sending raw audio or full transcripts to advertisers, or failing user answers when ads are down.",
            ),
        ]
    )
    notes = extended_block(
        "Alexa Advertising Workflow",
        [
            (
                "Disclosure UX",
                "Voice disclosure must be clear (“from a sponsor”) without wrecking UX. Product + legal co-own copy; system carries disclosure flags mandatorily.",
            ),
            (
                "Speculative prefetch",
                "When partial ASR suggests high probability of eligible intent, prefetch ads decision with cancel-on-miss to hide latency—only if privacy policy allows speculative processing.",
            ),
            (
                "Brand safety lists",
                "Global + advertiser exclusions + contextual blocks (news tragedies, etc.). Nearline update kill-lists.",
            ),
            (
                "Skill sponsored suggestions",
                "Different creative type; still through eligibility + disclosure; don’t hijack user-requested skill without policy.",
            ),
            (
                "Shopping through Alexa",
                "Sponsored product cards/voice offers need retail catalog join; reuse retail ads relevance with voice features.",
            ),
            (
                "Data retention",
                "ASR retention vs ads feature retention differ; document TTLs; advertising features store less.",
            ),
            (
                "Multi-locale policy",
                "EU consent differs from US; pack engine selects rules by country.",
            ),
            (
                "Experimentation ethics",
                "Holdouts for ads load; never experiment away legally required disclosures.",
            ),
            (
                "Security",
                "Decision API auth between speech and ads; prevent skill spoofing measurement events.",
            ),
            (
                "Cost",
                "Decision QPS × model cost; cache non-personalized contextual ads for popular intents.",
            ),
            (
                "Outage storytelling",
                "L6 answer: ads down → conversation continues; speech down → device local errors; measurement lag OK.",
            ),
            (
                "Identity",
                "Prefer household tokens over advertising IDs familiar from mobile; microphone context is more sensitive.",
            ),
            (
                "Audio creative supply",
                "Transcoded TTS vs pre-recorded; loudness norms; cache creatives at edge CDN.",
            ),
            (
                "Human review",
                "Ads creatives reviewed offline; runtime still enforces brand safety.",
            ),
            (
                "Related systems",
                "Alexa Speech, Privacy Hub, DSP/advertiser portal, Retail Catalog, Experimentation platform.",
            ),
        ],
    )
    ap = appendices(
        dedent(
            """\
            ### Appendix F — Event schema (privacy-preserving)

            ```text
            AdDecision { decision_id, request_id, eligible, campaign_id?, policy_version, ts }
            AdMeasure  { decision_id, event: played|complete|skip|error, ts }  # no transcript
            ```

            ### Appendix G — Runbooks

            **Ads p99 high:** serve content-only; scale decision cells; disable heavy models.
            **Privacy incident:** kill personalized ads globally; invalidate feature caches; notify privacy oncall.

            ### Appendix H — Closer checklist

            - [ ] Privacy boundary explicit
            - [ ] Content > ads on failure
            - [ ] Consent/kids fail closed
            - [ ] Measurement aggregated
            - [ ] Latency budget
            - [ ] Progressive scale
            """
        )
    )
    wrap = wrapup(
        "Alexa Triggering / Advertising Workflow",
        "A privacy-first **voice advertising workflow**: trigger→ASR/NLU→consent/policy eligibility→ads decisioning→render→aggregated measurement, with content always winning on ads failure.",
        [
            "Hard privacy boundary (no raw audio to advertisers)",
            "Consent/kids/sensitive-intent fail closed",
            "Ads additive latency budget + content fallback",
            "Aggregated measurement + fraud controls",
            "Clear ownership split Speech vs Ads vs Privacy",
        ],
        [
            "Regulatory pack complexity",
            "Household identity edge cases",
            "Speculative prefetch vs privacy",
            "Brand safety in breaking news",
        ],
    )
    end = "\n*End of document — Alexa Triggering / Advertising Workflow (SDE III)*\n"
    return "\n".join([h, TOC, s1, s2, s3, s4, s5, wrap, s7 + "\n---\n", ap, notes, end])


# =============================================================================
# Shared recommender helpers
# =============================================================================


def recommender_extended(name: str, extras: list[tuple[str, str]]):
    base = [
        (
            "Two-stage retrieval",
            "Candidate generation (ANN/CF/graph) → ranking (GBDT/DNN) → re-rank (business rules). Defend why one giant model is a deal-breaker for ops and latency.",
        ),
        (
            "Training-serving skew",
            "Feature store with point-in-time correctness; freeze feature versions in logs; shadow diffs.",
        ),
        (
            "Feedback loops",
            "Exposure bias, position bias—use propensity weighting / randomized exploration carefully.",
        ),
        (
            "Cold start",
            "New ASINs: content features; new users: popular in segment + contextual.",
        ),
        (
            "A/B & interleaving",
            "Amazon experimentation culture—layer experiments; guardrail metrics (latency, diversity, complaints).",
        ),
        (
            "Ownership",
            "Retrieval team vs ranker team vs surface owners (homepage/PDP/email); clear contracts on candidate budgets.",
        ),
    ]
    return extended_block(name, base + extras)


def build_product_rec() -> str:
    h = header(
        "Product Recommender System (Amazon Retail)",
        "Candidate generation · Ranking · Feature store · Real-time personalization · Cold start · Diversity · Business rules · Experimentation · Progressive scale",
        "**Retail Personalization / Recommendations** ownership—customer-obsessed relevance with marketplace constraints and unit economics",
        "Split retrieve/rank/re-rank planes, correct QPS math, deal-breakers for “one DNN scores entire catalog online”",
    )
    s1 = dedent(
        """\
        ## 1. Clarify Requirements (Interview Q&A)

        Goal: design Amazon **product recommendations** across surfaces (homepage, PDP “customers also bought”, cart, email) with multi-stage ML, feature platforms, business rules (OOS, policy), and experimentation.

        ### 1.0 What this is / is not

        | Dimension | **Product recommender** | Not this |
        |-----------|-------------------------|----------|
        | Job | Personalized ASIN recommendations | Search SERP ranking |
        | Success | Relevance, conversion, satisfaction, diversity | Max CTR only |
        | Planes | Retrieve → rank → re-rank | Single model over full catalog online |
        | Amazon lens | Customer trust, Prime, marketplace fairness, cost | Pure academic CF |

        ### 1.1 Functional Requirements

        | # | Q | A | Implication |
        |---|---|---|-------------|
        | F1 | Surfaces? | Home, PDP, cart, email | Surface-specific rankers |
        | F2 | Inputs? | User history, context, item | Feature store |
        | F3 | Outputs? | Ranked ASINs + explanations hooks | Response schema |
        | F4 | Freshness? | OOS nearline; models hours–days | Dual freshness |
        | F5 | Business rules? | OOS, blocked, age, geo | Re-rank filters |
        | F6 | Diversity? | Category/brand diversity | MMR / constraints |
        | F7 | Cold start? | New users/items | Content + segment popularity |
        | F8 | Realtime signals? | Session clicks | Stream features |
        | F9 | Explanations? | Optional “because you viewed” | Rule-based labels |
        | F10 | Experiments? | Continuous A/B | Exp platform |
        | F11 | Multi-marketplace? | Yes | Cells |
        | F12 | Sponsored? | Optional labeled | Ads merge policy |
        | F13 | Latency? | Surface-dependent | Budgets |
        | F14 | Privacy? | Purpose-limited profiles | TTLs |
        | F15 | Feedback? | Purchase/return/click | Label pipelines |

        **MVP:** PDP + homepage widgets; 2-stage retrieve+rank; OOS filter; session features; logging; A/B hooks.

        ### 1.2 NFRs

        | Surface | p99 |
        |---------|-----|
        | PDP widget | < 100–150 ms |
        | Homepage module | < 200–300 ms (parallel) |
        | Email (offline) | hours OK |

        Availability high; degrade to popular/similar. Cost: infer $/1K recommendations.

        ### 1.3 Cases

        Happy: view ASIN → related items; homepage personalized rail; cart cross-sell.

        | Case | Behavior |
        |------|----------|
        | OOS | Filter/replace |
        | Gift shopping | Session intent demotes personal history |
        | Filter bubble | Diversity constraints |
        | New ASIN | Content kNN |
        | Bot traffic | Downweight training |

        ### 1.4 Scales

        | Metric | Base | 10× | 100× | 1,000× |
        |--------|------|-----|------|--------|
        | Recs QPS | 200K | 2M | 20M | cells+edge |
        | Catalog ASINs | 400M | — | — | growth |
        | Candidates/request | 500–2000 | — | — | multi-channel |
        | Feature reads/s | 2M | 20M | 200M | cached |

        ---
        """
    )
    s2 = dedent(
        """\
        ## 2. Back-of-the-Envelope Estimation

        ### 2.1 Planes

        | Plane | Work |
        |-------|------|
        | Online retrieve | ANN / inverted / CF recall |
        | Online rank | Score 500–2000 cands |
        | Feature hydrate | User/item/context |
        | Nearline | Session aggregates, OOS |
        | Offline | Train, batch recs for email |

        ### 2.2 Latency budget (PDP)

        | Step | ms |
        |------|----|
        | Context resolve | 5–10 |
        | Retrieve (parallel channels) | 20–40 |
        | Feature fetch | 20–40 |
        | Ranker | 20–40 |
        | Business re-rank | 5–10 |
        | **Total** | **≤ 100–150** |

        ### 2.3 Cost

        Scoring 1000 cands × 200K QPS is impossible if naive—hence retrieve narrows first; cache user features; distill rankers.

        ---
        """
    )
    s3 = dedent(
        """\
        ## 3. High-Level Design

        ### 3.1 Components

        | Component | Role |
        |-----------|------|
        | Recs API | Surface contracts |
        | Context Service | Device, geo, session |
        | Candidate Generators | CF, co-view, ANN content, graph |
        | Feature Store | Online + offline |
        | Ranker Fleet | GBDT/DNN | 
        | Re-ranker | Diversity, business rules, ads merge |
        | Experimentation | Variants |
        | Log/Join | Training data |
        | Model Platform | Train/deploy/shadow |
        | Popularity Fallback | Degradation |

        ### 3.2 Flow

        ```text
        Request → Context → Parallel Retrieve → Union/Dedup → Features
               → Rank → Re-rank (OOS/diversity/policy/ads) → Response
               → Async logs
        ```

        ### 3.3 Tradeoffs

        | Decision | Choose | Deal-breaker |
        |----------|--------|--------------|
        | Stages | Multi-stage | Score full catalog online |
        | Features | Shared store | Ad-hoc DB joins online |
        | Fallback | Popularity/similar | Empty widget |
        | Ads | Labeled merge | Silent replace all organic |

        ---
        """
    )
    s4 = dedent(
        """\
        ## 4. Architecture Diagram

        ```text
        Client Surface --> Recs API --> Context
                              |
                              +--> CG: Co-purchase / Co-view
                              +--> CG: ANN content embedding
                              +--> CG: Personal CF / two-tower
                              |
                              v
                           Dedup/Union (budget K)
                              |
                              v
                        Feature Store hydrate
                              |
                              v
                           Ranker (model)
                              |
                              v
                     Re-rank: OOS, diversity, policy, ads
                              |
                              v
                           Response ASINs
                              |
                              v async
                      Logs → Training → Registry → Canary
        ```

        ---
        """
    )
    s5 = dedent(
        """\
        ## 5. Design Deep Dive

        ### 5.1 Invariants

        1. Never recommend blocked/illegal/OOS (per policy).
        2. Experiment assignment sticky per surface rules.
        3. Logging includes candidate features point-in-time.
        4. Fallback non-empty for critical surfaces.
        5. Marketplace isolation.

        ### 5.2 Candidate channels

        Co-purchase graph, co-view, search→purchase, two-tower ANN, editorial, trending. Budget per channel; explore slot.

        ### 5.3 Ranking

        Learning-to-rank with calibration per surface. Multi-objective: CTR proxy, CVR, profit contribution, satisfaction (returns-).

        ### 5.4 Feature store

        User: long-term affinities; session: short-term intent; item: price, category, embedding; context: device/time.

        ### 5.5 Progressive scale

        10×: cache features; ANN shards. 100×: marketplace cells; distilled models. 1,000×: edge caches for anonymous; on-device session models light.

        ### 5.6 Marketplace fairness

        Avoid entrenching only megabrands—diversity constraints; small-seller exploration quotas as product policy.

        ---
        """
    )
    s7 = "## 7. Deeper / Related Interview Questions\n\n" + qa(
        [
            (
                "Why multi-stage vs one model?",
                "Catalog too large to score; stages specialize; ops can hotfix retrieval; latency/cost control.",
            ),
            (
                "How do you handle position bias?",
                "Propensity scoring, inverse propensity weighting, occasional randomized exploration, eye-tracking proxies—pick pragmatic mix.",
            ),
            (
                "Returns as labels?",
                "Purchases with quick returns are negative/weak; join order lifecycle into labels carefully.",
            ),
            (
                "Gift mode?",
                "Session intent classifiers demote personal historical affinity; boost category from browsing.",
            ),
            (
                "Deal-breaker?",
                "Online full-catalog DNN scoring per request; or empty homepage when ranker fails.",
            ),
            (
                "Sponsored products in widget?",
                "Labeled, relevance threshold, reserved organic slots—Ads owns auction; Recs owns merge policy.",
            ),
            (
                "Feature store vs joining production DBs?",
                "PIT correctness and p99; production DBs aren’t feature stores.",
            ),
            (
                "Success metrics?",
                "Surface CTR/CVR, revenue, diversity, complaint rate, latency, model freshness, fallback rate.",
            ),
        ]
    )
    notes = recommender_extended(
        "Product Recommender",
        [
            (
                "Surface-specific models",
                "PDP related-items ≠ homepage for-you. Shared retrieval, divergent rank heads.",
            ),
            (
                "Real-time session",
                "Clickstream → session store (Redis) with TTL; ranker reads last-N events.",
            ),
            (
                "Embedding training",
                "Two-tower with in-batch negatives; ANN index rebuild cadence vs nearline partial updates.",
            ),
            (
                "Business value",
                "Optimize customer long-term value not only immediate CTR—mention returns and complaint guardrails.",
            ),
            (
                "Catalog taxonomy",
                "Browse nodes as features; avoid recommending incompatible product types.",
            ),
            (
                "International",
                "Marketplace cells; currency/price features local; don’t leak US inventory into DE.",
            ),
            (
                "Email batch",
                "Offline generate + personalize at send; cheaper than online QPS.",
            ),
            (
                "Model distillation",
                "Large teacher offline; small student online for p99.",
            ),
            (
                "Debug tools",
                "Explain: channels, scores, filters fired—internal only.",
            ),
        ],
    )
    ap = appendices(
        dedent(
            """\
            ### Appendix F — Response schema

            ```json
            {"surface":"pdp_related","asins":[{"asin":"B0..","reason":"coview"}],"model_versions":{},"exp_ids":[]}
            ```

            ### Appendix G — Closer checklist

            - [ ] Retrieve/rank/re-rank split
            - [ ] Feature store PIT
            - [ ] Fallbacks
            - [ ] OOS/policy filters
            - [ ] Experiments
            - [ ] Progressive scale
            """
        )
    )
    wrap = wrapup(
        "Product Recommender",
        "Amazon retail **product recommendations**: multi-channel candidate generation, feature store, rankers, business re-ranking, experimentation, fallbacks, progressive scale across surfaces.",
        [
            "Multi-stage retrieve→rank→re-rank",
            "Feature store with PIT logging",
            "Surface-specific objectives + shared retrieval",
            "Non-empty fallbacks",
            "Labeled ads merge policy",
        ],
        [
            "Feedback loops / bias",
            "Cold-start catalog churn",
            "Multi-objective tension",
            "Cost at 100× QPS",
        ],
    )
    end = "\n*End of document — Product Recommender (SDE III)*\n"
    return "\n".join([h, TOC, s1, s2, s3, s4, s5, wrap, s7 + "\n---\n", ap, notes, end])


def build_clothing_rec() -> str:
    h = header(
        "Clothing Recommender System (Amazon Fashion)",
        "Style embeddings · Size/fit · Seasonality · Visual similarity · Catalog attributes · Returns-aware ranking · Progressive scale",
        "**Amazon Fashion** personalization—style & fit & seasonality with visual ML and returns-aware objectives",
        "Explicit fit/season constraints, visual+tabular fusion, deal-breakers for “generic product CF only”",
    )
    s1 = dedent(
        """\
        ## 1. Clarify Requirements (Interview Q&A)

        Goal: design a **clothing / fashion recommender** that accounts for **style, size/fit, seasonality, and visual similarity**, not just co-purchase patterns.

        ### 1.0 Differentiation vs generic product recs

        | Dimension | Clothing | Generic product |
        |-----------|----------|-----------------|
        | Fit | Critical (size, body) | Rarely |
        | Visual | Primary | Secondary |
        | Season | Strong | Weak |
        | Returns | High cost signal | Lower |
        | Style affinity | Latent taste | Category affinity |

        ### 1.1 Functional Requirements

        | # | Q | A | Implication |
        |---|---|---|-------------|
        | F1 | Surfaces? | Fashion home, PDP outfit, style match | Specialized CGs |
        | F2 | Size? | Use size profile / past fit | Fit filter/boost |
        | F3 | Visual? | Image embeddings | ANN visual |
        | F4 | Season? | Locale + calendar + weather | Season features |
        | F5 | Outfit? | Complementary items | Pair model |
        | F6 | Style? | Latent style clusters | Style tower |
        | F7 | Returns? | Optimize fit satisfaction | Return-aware labels |
        | F8 | Inclusivity? | Size availability diversity | Inventory-aware |
        | F9 | Trends? | Nearline trend spikes | Trend CG |
        | F10 | Cold start? | New SKUs via visual/attributes | Content path |
        | F11 | Gender/dept? | Sensitive; prefer explicit browse context | Careful features |
        | F12 | Marketplace? | Localized fashion | Cells |
        | F13 | Latency? | Similar to retail widgets | Multi-stage |
        | F14 | Modesty/safety? | Policy filters | Safety |
        | F15 | Experiment? | Yes | Exp platform |

        **MVP:** visual similar + style personalization + size-aware filter + season boost + returns-aware rank head on fashion surfaces.

        ### 1.2 NFRs

        p99 widget < 150–200ms; fit filter correctness > vanity CTR; availability of size variants checked; high return-rate guardrail.

        ### 1.3 Cases

        Happy: view dress → visually similar in season + size available; homepage style rail; outfit “complete the look”.

        | Case | Behavior |
        |------|----------|
        | Size unavailable | Show alt sizes or similar cut with stock |
        | Off-season swimwear in winter (locale) | Demote unless tropical context / intentional browse |
        | High return ASIN | Demote unless strong intent |
        | Body/size cold start | Ask-friendly UX + segment priors; don’t assume |
        | Counterfeit / policy | Block |

        ### 1.4 Scales

        Similar QPS to product recs but heavier embedding traffic; image ANN indexes large; seasonality shifts peaks (Prime Day fashion, holidays).

        | Metric | Base | 10× | 100× |
        |--------|------|-----|------|
        | Fashion recs QPS | 50K | 500K | 5M |
        | Image embedding dim | 256–512 | — | — |
        | ANN vectors | 100M styles | 200M | cells |

        ---
        """
    )
    s2 = dedent(
        """\
        ## 2. Back-of-the-Envelope Estimation

        Visual ANN: 100M vectors × 512 × 4B ≈ 200 GB (plus indexes). Shard by marketplace/department. Ranker still scores hundreds of cands—not full catalog.

        Latency budget mirrors product recs with extra visual CG parallelized.

        Returns join: order line → return reason codes → training labels delayed days–weeks.

        ---
        """
    )
    s3 = dedent(
        """\
        ## 3. High-Level Design

        ### 3.1 Extra components beyond generic recs

        | Component | Role |
        |-----------|------|
        | Visual Embedding Service | Image → vector |
        | Visual ANN | Similar styles |
        | Size/Fit Profile | Customer size graph |
        | Seasonality Service | Locale calendar/weather |
        | Outfit / Complement Model | Tops↔bottoms |
        | Returns-aware Rank Head | P(return\\|fit) |
        | Attribute Normalizer | Color, material, cut |

        ### 3.2 Flow

        ```text
        Request → Context (locale, season, size profile)
          → CG visual ANN ∥ CG CF ∥ CG trend ∥ CG outfit
          → Fit/inventory filter
          → Rank (style + purchase - return risk)
          → Diversity (color/brand/price)
          → Response
        ```

        ### 3.3 Tradeoffs

        | Decision | Choose | Deal-breaker |
        |----------|--------|--------------|
        | CF only | **CF + visual + fit** | CF-only fashion |
        | Size | Filter when known | Ignore fit |
        | Season | Soft boost + hard for extremes | None |
        | Returns | In objective | CTR-only |

        ---
        """
    )
    s4 = dedent(
        """\
        ## 4. Architecture Diagram

        ```text
        Fashion Surface --> Recs API --> Size/Fit Profile
                                   --> Seasonality
                                   --> Visual ANN  --\\
                                   --> CF/Two-Tower --+--> Filter fit/OOS --> Rank --> Diversify
                                   --> Outfit CG   --/
                                         |
                                         v
                                   Returns-aware training loop
        ```

        ---
        """
    )
    s5 = dedent(
        """\
        ## 5. Design Deep Dive

        ### 5.1 Fit modeling

        Size profile from purchases kept + returns (“too small”). Variant-level inventory (SKU size/color). Recommend style with available size, not parent ASIN only.

        ### 5.2 Visual embeddings

        Train on fashion catalog images; augment; domain-specific backbone; ANN HNSW/IVF; refresh on new images nearline.

        ### 5.3 Seasonality

        Features: month, hemisphere, weather band, event calendars. Browse intent can override (customer shopping swimwear in winter intentionally).

        ### 5.4 Outfit recommendations

        Pair compatibility model using co-purchase + visual harmony + color theory heuristics as weak priors.

        ### 5.5 Progressive scale

        Shard ANN; distill visual encoders; cache style rails for segments; cells per marketplace.

        ### 5.6 Ethics / sensitivity

        Avoid harmful body inference from images of customers; use declared/past purchase sizes with privacy care. Gender stereotypes: prefer contextual browse signals.

        ---
        """
    )
    s7 = "## 7. Deeper / Related Interview Questions\n\n" + qa(
        [
            (
                "Why can’t we reuse the generic product recommender unchanged?",
                "Fit, visual style, seasonality, and returns dominate fashion economics. Pure CF recommends wrong sizes/seasons and drives returns.",
            ),
            (
                "How do you encode size?",
                "Normalized size schemas per garment type; customer size vectors; compatibility scores; hard filter when confidence high.",
            ),
            (
                "Visual similar but wrong season?",
                "Re-rank with season features; optional hard filter for extreme mismatches unless intent overrides.",
            ),
            (
                "Optimize for returns?",
                "Multi-objective: P(purchase) - λ P(return) + satisfaction; guardrail max return-rate in experiments.",
            ),
            (
                "Cold-start garment?",
                "Visual+attribute ANN; influencer/trend tags; explore quota.",
            ),
            (
                "Deal-breaker?",
                "Ignoring size availability; or CTR-only objective that increases returns.",
            ),
        ]
    )
    notes = recommender_extended(
        "Clothing Recommender",
        [
            (
                "Attribute quality",
                "Fashion taxonomy messiness (color aliases)—invest in attribute normalization; garbage attributes wreck filters.",
            ),
            (
                "UCG images vs studio",
                "Embeddings should be robust; prefer studio for index, UGC for social proof separately.",
            ),
            (
                "Plus-size / inclusive inventory",
                "Diversity constraints ensuring available inclusive sizes aren’t drowned by majority stock.",
            ),
            (
                "Counterfeit & brand",
                "Trust signals in re-rank; policy blocks.",
            ),
            (
                "Weather partnership",
                "Optional weather API as context feature with cache.",
            ),
            (
                "Mobile visual search adjacent",
                "Same embeddings can power camera search—shared embedding platform ownership.",
            ),
            (
                "Prime try-before-you-buy",
                "If exists, labels differ from hard purchases—model separately.",
            ),
            (
                "Trend detection",
                "Nearline velocity on styles; don’t let trends violate fit filters.",
            ),
            (
                "Evaluation",
                "Offline AUC insufficient—fashion needs fit proxy metrics + human style eval panels.",
            ),
        ],
    )
    ap = appendices(
        dedent(
            """\
            ### Appendix F — Size profile sketch

            ```text
            FitProfile { customer_id, garment_type → size, confidence, updated_at }
            SkuVariant { style_id, size, color, inventory }
            ```

            ### Appendix G — Closer checklist

            - [ ] Visual + CF channels
            - [ ] Size/fit filters
            - [ ] Seasonality
            - [ ] Returns-aware objective
            - [ ] Variant inventory
            - [ ] Sensitivity/ethics note
            """
        )
    )
    wrap = wrapup(
        "Clothing Recommender",
        "Amazon Fashion **clothing recommendations** with visual ANN, style models, size/fit profiles, seasonality, outfit complements, and returns-aware ranking on top of multi-stage retrieval.",
        [
            "Fashion ≠ generic CF",
            "Variant-level inventory + fit filters",
            "Visual embeddings as first-class CG",
            "Seasonality with intent overrides",
            "Returns in the objective",
        ],
        [
            "Attribute quality debt",
            "Size cold start UX",
            "Trend vs fit conflicts",
            "Sensitive demographic inference risks",
        ],
    )
    end = "\n*End of document — Clothing Recommender (SDE III)*\n"
    return "\n".join([h, TOC, s1, s2, s3, s4, s5, wrap, s7 + "\n---\n", ap, notes, end])


def build_inflight_rec() -> str:
    h = header(
        "In-Flight Movie Recommender (Duration-Constrained)",
        "Flight duration constraints · Offline catalogs · Onboard caching · Personalization under sparse connectivity · Watch-completion · Progressive scale",
        "**Prime Video / Airlines partnership**-style in-flight recommender—movies that **fit the flight** with degraded connectivity",
        "Hard duration feasibility constraints, onboard vs ground planes, deal-breakers for “ignore runtime vs remaining flight time”",
    )
    s1 = dedent(
        """\
        ## 1. Clarify Requirements (Interview Q&A)

        Goal: recommend **movies/shows that fit remaining flight duration** (and attention context), with catalogs that may be **pre-staged onboard**, personalization that works **offline/intermittently**, and measurement on completion.

        ### 1.0 What this is / is not

        | Dimension | **In-flight recommender** | Not this |
        |-----------|---------------------------|----------|
        | Constraint | Runtime ≤ remaining flight − buffers | Unlimited catalog browse only |
        | Connectivity | Often offline / portal Wi‑Fi | Always-on Prime streaming assumptions |
        | Catalog | Airline-licensed subset + cached | Full Prime catalog everywhere |
        | Success | Completion, satisfaction, fit-to-flight | Max clicks on too-long titles |

        ### 1.1 Functional Requirements

        | # | Q | A | Implication |
        |---|---|---|-------------|
        | F1 | Constraint? | runtime + episodes fit remaining time | Hard filter |
        | F2 | Inputs? | Flight leg, remaining time, profile (optional), device | Context schema |
        | F3 | Catalog? | Onboard cached titles | Catalog snapshot |
        | F4 | Personalization? | Prefs synced pre-flight; onboard light | Hybrid |
        | F5 | Episodes? | Suggest episode counts that fit | Packing logic |
        | F6 | Kids? | Profile / seat context | Policy |
        | F7 | Languages? | Audio/subtitle availability onboard | Filter |
        | F8 | Updates mid-flight? | Remaining time updates | Recompute |
        | F9 | Fallback? | Popular fitting titles | Non-empty |
        | F10 | Licensing? | Airline window | Catalog validity |
        | F11 | Metrics? | Start, completion, abandon | Onboard logs flush later |
        | F12 | Ground personalization? | Precompute top packs | Before departure |
        | F13 | Multi-leg? | Per leg remaining | Leg_id |
        | F14 | Live TV? | Optional | Separate |
        | F15 | Ads? | Airline policy | Optional |

        **MVP:** remaining-time hard filter; onboard catalog; pre-flight personalization pack; popular fallback; completion logging with delayed sync.

        ### 1.2 NFRs

        Onboard recommend p99 < 100ms local; ground precompute OK minutes; storage on aircraft limited; privacy of profiles on shared seatback.

        ### 1.3 Cases

        Happy: 6h flight → recommend 2h movie + series pack; 45m short-haul → sitcoms/episodes; kids profile → G/PG fitting.

        | Case | Behavior |
        |------|----------|
        | Turbulence pause | Don’t over-penalize abandon |
        | Wrong remaining time | Conservative buffer (taxi/safety videos) |
        | Catalog miss | Ground sync next turnaround |
        | Shared seatback | Privacy pin / anonymous mode |
        | Multi-stop | Reset per leg |

        ### 1.4 Scales

        | Metric | Base | 10× | 100× |
        |--------|------|-----|------|
        | Flights/day | 50K | 500K | — |
        | Seat sessions/day | 5M | 50M | 500M |
        | Onboard titles | 500–5K | — | richer caches |
        | Precompute packs | per flight/user segment | — | —

        ---
        """
    )
    s2 = dedent(
        """\
        ## 2. Back-of-the-Envelope Estimation

        Onboard catalog 2K titles × metadata 2KB = small. Video assets separate (TBs) staged by airline ops—not recommender’s store.

        Pre-flight: for 300 passengers, generate personalized lists of 50 fitting titles—trivial compute on ground; push to aircraft systems.

        Mid-flight re-rank local: milliseconds on embedded service.

        Buffers: `effective = remaining - taxi_buffer - meal_buffer_optional`.

        ---
        """
    )
    s3 = dedent(
        """\
        ## 3. High-Level Design

        ### 3.1 Dual plane

        | Plane | Where | Role |
        |-------|-------|------|
        | Ground | Cloud | Personalization, licensing, pack build, heavy ML |
        | Onboard | Aircraft server / seatback | Duration filter, local re-rank, playback, logs |

        ### 3.2 Components

        Ground: Profile Service, Catalog/Licensing, Duration Pack Builder, Sync to airline content system.
        Onboard: Local Catalog Index, RemainingTime Service, Local Ranker, Playback, Log Buffer.

        ### 3.3 Feasibility filter

        ```text
        feasible(title) = runtime_minutes <= effective_remaining
        for series: n_episodes * ep_runtime <= effective_remaining
        ```

        Soft prefer titles with runtime in [0.5, 0.85] × remaining (finishable, not tiny).

        ### 3.4 Tradeoffs

        | Decision | Choose | Deal-breaker |
        |----------|--------|--------------|
        | Constraint | Hard filter first | Ignore runtime |
        | ML onboard | Light re-rank | Cloud calls mid-flight required |
        | Profile on seatback | Pin/anonymous | Dump full profile plaintext |
        | Sync | Pre-flight packs | Assume always-online streaming |

        ---
        """
    )
    s4 = dedent(
        """\
        ## 4. Architecture Diagram

        ```text
        [Ground - Amazon Cloud]
        Profile + History --> Pack Builder --> Personalized feasible lists
        Licensing Catalog -/                 |
        Flight schedule remaining estimate -/ 
                        |
                      Sync at gate / content loader
                        |
                        v
        [Onboard]
        RemainingTime --> Local Filter/Rank --> Seatback UI --> Playback
              ^                                     |
              clock/avionics feed                   v
                                              Log Buffer --> flush on landing Wi-Fi
        ```

        ---
        """
    )
    s5 = dedent(
        """\
        ## 5. Design Deep Dive

        ### 5.1 Invariants

        1. Never primarily recommend titles exceeding effective remaining time.
        2. Kids policy enforced onboard even if packs stale.
        3. Logs privacy-safe on shared devices.
        4. Playback works if personalization missing (popular feasible).

        ### 5.2 Packing algorithm

        Precompute ranked feasible set; onboard adjust as remaining shrinks; suggest “finishable tonight” packs (movie + short).

        ### 5.3 Personalization under sparse data

        Use pre-synced embeddings/affinities; avoid heavy cold cloud retrieval aloft.

        ### 5.4 Progressive scale

        10× airlines: standardize sync API. 100×: segment packs + device models. 1,000×: global airline platform multi-tenant cells.

        ### 5.5 Ownership

        Amazon video personalization owns models; airline IFE owns onboard hardware SLOs; clear contract on catalog snapshots + time remaining API.

        ---
        """
    )
    s7 = "## 7. Deeper / Related Interview Questions\n\n" + qa(
        [
            (
                "Why hard-filter runtime instead of only ranking soft penalty?",
                "Recommending a 3h movie on a 90m flight destroys trust. Soft penalties still surface infeasible titles. Hard filter first, soft preference second.",
            ),
            (
                "How do you get remaining flight time?",
                "Airline IFE/avionics integration; conservative buffers; update as flight progresses; fall back to scheduled ETA.",
            ),
            (
                "What if Wi-Fi works mid-flight?",
                "Optional enhancement path to cloud—but core must work offline. Don’t make online required.",
            ),
            (
                "Series recommendations?",
                "Pack number of episodes that fit; prefer complete arcs if tagged; don’t start long unfinished seasons without warning.",
            ),
            (
                "Deal-breaker?",
                "Design that requires cloud inference per seatback request mid-flight with no offline fallback.",
            ),
            (
                "Privacy on seatback?",
                "Session PIN, auto-logout, minimal profile cached, wipe on end-of-flight.",
            ),
        ]
    )
    notes = extended_block(
        "In-Flight Movie Recommender",
        [
            (
                "Buffer policy",
                "Taxi, safety demos, meals—product-configured buffers by airline/route. Underestimate remaining time slightly.",
            ),
            (
                "Content rating",
                "Locale/airline rules; kids seat detection if available.",
            ),
            (
                "Licensing windows",
                "Catalog snapshot expires; onboard must not show expired licenses after turnaround sync fail—fail safe hide.",
            ),
            (
                "Evaluation",
                "Completion rate within flight, rewatch, survey CSAT; not only click-through.",
            ),
            (
                "Multi-passenger households",
                "Seat profiles differ; don’t share personalization across seats without auth.",
            ),
            (
                "Short-form vs long",
                "As remaining drops below 25m, switch rails to shorts/episodes/magazines.",
            ),
            (
                "Device heterogeneity",
                "Seatback vs personal device streaming portal—same feasibility API.",
            ),
            (
                "Sync bandwidth at gate",
                "Prioritize metadata+packs first; large video assets via airline ops channels.",
            ),
            (
                "Amazon differentiation",
                "Prime tastes pre-flight sync is a plus vs generic IFE popularity lists—call this out.",
            ),
            (
                "Failure mode storytelling",
                "Personalization missing → popular feasible; time feed missing → scheduled duration; catalog corrupt → safe mode classics list.",
            ),
            (
                "A/B testing",
                "Mostly on ground pack builder; onboard flags limited; flush metrics after landing.",
            ),
            (
                "Related systems",
                "Prime Video recommender, airline IFE CMS, identity, experimentation.",
            ),
            (
                "Runtime metadata quality",
                "Wrong runtimes break trust—QA catalog; prefer source-of-truth from video asset service.",
            ),
            (
                "Attention context",
                "Red-eye vs daytime flights change genre priors—optional context feature.",
            ),
            (
                "Cost",
                "Ground precompute cheap; onboard CPU constrained—keep models tiny.",
            ),
        ],
    )
    ap = appendices(
        dedent(
            """\
            ### Appendix F — Schemas

            ```text
            FlightContext { flight_id, leg_id, remaining_min, buffers, locale }
            Title { title_id, runtime_min, rating, langs[], kids_ok }
            Pack { passenger_token?, title_ids[], model_version, built_at }
            ```

            ### Appendix G — Closer checklist

            - [ ] Hard duration filter
            - [ ] Ground vs onboard planes
            - [ ] Offline fallback
            - [ ] Kids/privacy on seatback
            - [ ] Completion metrics delayed sync
            """
        )
    )
    wrap = wrapup(
        "In-Flight Movie Recommender",
        "A **duration-constrained in-flight movie recommender** with ground personalization packs, onboard feasibility filtering/re-ranking, offline-first operation, and delayed measurement sync.",
        [
            "Hard runtime feasibility before rank",
            "Ground heavy ML / onboard light re-rank",
            "Offline-first with popular fallback",
            "Conservative time buffers",
            "Seatback privacy controls",
        ],
        [
            "Airline integration variance",
            "Runtime metadata errors",
            "Licensing snapshot staleness",
            "Wi-Fi temptation to couple cloud",
        ],
    )
    end = "\n*End of document — In-Flight Movie Recommender (SDE III)*\n"
    return "\n".join([h, TOC, s1, s2, s3, s4, s5, wrap, s7 + "\n---\n", ap, notes, end])


def build_mobile_ac() -> str:
    h = header(
        "Mobile Autocomplete & Spell-Check (On-Device + Server Hybrid)",
        "On-device LM · Server long-tail · Spell correction · Typing privacy · Sync dictionaries · Latency · Battery · Progressive scale",
        "**Amazon mobile / keyboard / app search entry** hybrid autocomplete & spell-check—privacy, battery, and offline UX with server intelligence",
        "Split on-device vs server planes, privacy constraints, deal-breakers for “every keystroke must hit server”",
    )
    s1 = dedent(
        """\
        ## 1. Clarify Requirements (Interview Q&A)

        Goal: design **mobile autocomplete and spell-check** that works **on-device** for latency/offline/privacy and uses **server** for long-tail / personalization / catalog-aware corrections—hybrid.

        ### 1.0 What this is / is not

        | Dimension | **This doc** | Not this |
        |-----------|--------------|----------|
        | Job | Next-word / phrase suggest + spell fix while typing | Full cloud SERP |
        | Location | On-device first, server assist | Server-mandatory keystroke |
        | Privacy | Minimize raw keystroke exfiltration | Log all keystrokes forever |
        | Amazon lens | App search bars, Fire devices, keyboard IME | Desktop IDE autocomplete |

        ### 1.1 Functional Requirements

        | # | Q | A | Implication |
        |---|---|---|-------------|
        | F1 | Suggest? | Words/phrases as user types | Local LM + dict |
        | F2 | Spell-check? | Underline + corrections | Confusion sets |
        | F3 | Offline? | Core works offline | On-device models |
        | F4 | Server? | Long-tail / catalog terms | Hybrid API |
        | F5 | Personalization? | User lexicon (local) | On-device store |
        | F6 | Languages? | Multi + code-switch | Language pack |
        | F7 | Privacy? | Opt-in server learn | Consent |
        | F8 | Battery? | Strict CPU budget | Quantized models |
        | F9 | Latency? | <16–30ms local | Soft realtime |
        | F10 | Catalog names? | ASIN/brand terms | Server/catalog packs |
        | F11 | Safety? | Block abusive suggestions | Filters |
        | F12 | Sync? | Dictionary packs | Delta updates |
        | F13 | Autocorrect aggressiveness? | User setting | Modes |
        | F14 | Analytics? | Aggregated opt-in | Privacy pipeline |
        | F15 | A/B? | Pack experiments | Layered |

        **MVP:** on-device dictionary+LM autocomplete; spell corrections; optional server assist when online/consented; language packs; safety; battery budgets.

        ### 1.2 NFRs

        | # | Target |
        |---|--------|
        | Local suggest | ≤ 16–30ms |
        | Server assist | ≤ 100–150ms when used |
        | Offline | Core quality OK |
        | Model size | Tens of MB per language pack |
        | Privacy | No raw keystroke stream by default |
        | Battery | Negligible vs typing session |

        ### 1.3 Cases

        Happy: offline typing suggestions; misspelling “recieve” → receive; catalog brand “firetvstick” corrected; opted-in server improves rare terms.

        | Case | Behavior |
        |------|----------|
        | No network | Local only |
        | Consent off | No server personalization learn |
        | Code switching EN/ES | Lang-ID + mixed packs |
        | Password fields | Disable learning / suggest |
        | Kids | Stricter packs |
        | Low storage | Smaller packs |

        ### 1.4 Scales

        | Metric | Base | 10× | 100× |
        |--------|------|-----|------|
        | Devices | 100M | 1B | — |
        | Server assist QPS | 200K | 2M | 20M |
        | Pack updates | weekly | — | staged |
        | Languages | 20 | 40 | 100 |

        ---
        """
    )
    s2 = dedent(
        """\
        ## 2. Back-of-the-Envelope Estimation

        On-device: 50MB pack × 100M devices = distribution challenge—delta updates, compression, CDN.

        Server assist only on uncertain local predictions → e.g. 10% of keystrokes → QPS manageable.

        Battery: limit neural infer to N ms / keystroke; fallback to n-gram.

        ---
        """
    )
    s3 = dedent(
        """\
        ## 3. High-Level Design

        ### 3.1 Components

        | Component | Where | Role |
        |-----------|-------|------|
        | Keyboard/IME / Search field SDK | Device | UI |
        | On-device LM + Dictionary | Device | Suggest/spell |
        | User Lexicon | Device | Learned words |
        | Safety Filter | Device | Blocks |
        | Pack Manager | Device | Downloads |
        | Assist API | Server | Long-tail / catalog |
        | Pack Builder | Server | Offline train |
        | Privacy Aggregate | Server | Opt-in stats |
        | Experiment | Both | Flags |

        ### 3.2 Hybrid decision

        ```text
        on each keystroke:
          local_candidates = device_model()
          if confidence high or offline or no consent:
             return local
          else:
             server_candidates = assist_api(prefix_redacted, locale, context_type)
             merge(local, server) → safety → show
        ```

        ### 3.3 Tradeoffs

        | Decision | Choose | Deal-breaker |
        |----------|--------|--------------|
        | Every keystroke server | **Hybrid / local-first** | Server-mandatory |
        | Learn passwords | **Never** | Learn from secure fields |
        | Model size | Quantized tens of MB | 1GB LM on phone |
        | Privacy | Opt-in aggregates | Raw keystroke warehouse default |

        ---
        """
    )
    s4 = dedent(
        """\
        ## 4. Architecture Diagram

        ```text
        +---------------- DEVICE ------------------+
        | Field SDK --> Local LM/Dict --> Safety   |
        |    |              ^                      |
        |    |         User Lexicon                |
        |    |         Pack Manager <--- CDN packs |
        |    v                                     |
        | optional Assist client                   |
        +------------------+-----------------------+
                           | consented + uncertain
                           v
                    +------ Server Assist ------+
                    | Catalog/long-tail index   |
                    | Privacy-preserving logs   |
                    +---------------------------+
        ```

        ---
        """
    )
    s5 = dedent(
        """\
        ## 5. Design Deep Dive

        ### 5.1 Invariants

        1. Password/secure fields never contribute to learning or server assist.
        2. Local-first offline path always works.
        3. Safety filter on both local and server candidates.
        4. Pack signatures verified.
        5. Consent gates server personalization.

        ### 5.2 On-device models

        N-gram + small transformer distilled; quantized INT8; language packs; confuse-a-tron spell lists; beam for corrections.

        ### 5.3 Server assist

        Prefix → catalog-aware suggestions (brands, ASINs names); rate limited; redacted context types (search vs chat).

        ### 5.4 Spell-check

        Edit-distance to dictionary + noisy-channel probabilities; contextual LM rescoring; don’t over-correct names in user lexicon.

        ### 5.5 Progressive scale

        10×: better deltas; 100×: on-device neural default; server only rare; 1,000×: federated learning opt-in.

        ### 5.6 Ownership

        Mobile client team owns device budgets; search suggest owns server assist; privacy owns consent UX.

        ---
        """
    )
    s7 = "## 7. Deeper / Related Interview Questions\n\n" + qa(
        [
            (
                "Why not server-only autocomplete like desktop web?",
                "Mobile offline, battery, privacy, and RTT variability. Server-only feels broken on planes/subways and risks keystroke logging perceptions.",
            ),
            (
                "How do you keep models small?",
                "Distillation, quantization, vocabulary pruning, per-language packs, delta updates, n-gram fallback.",
            ),
            (
                "Federated learning?",
                "Phase 2 opt-in for improving packs without raw central keystrokes—complex; mention as 100×+ path.",
            ),
            (
                "Catalog terms like ASIN titles?",
                "Server assist + periodic on-device brand dictionaries for head terms.",
            ),
            (
                "Deal-breaker?",
                "Requiring network for every keystroke; or learning from password fields.",
            ),
            (
                "Evaluating quality?",
                "Keystroke saved, correction acceptance, regret (undo rate), offline quality suite, battery traces.",
            ),
            (
                "Abuse suggestions?",
                "On-device safety lists + server policy; blocklist updates via packs.",
            ),
            (
                "Relation to retail search autocomplete?",
                "Different surface: this is typing UX hybrid; retail suggest is server search box at huge QPS. Share dictionaries carefully.",
            ),
        ]
    )
    notes = extended_block(
        "Mobile Autocomplete & Spell-Check",
        [
            (
                "Field types",
                "search, chat, email, password, address—policy matrix for learning/assist/autocorrect aggressiveness.",
            ),
            (
                "Undo UX",
                "Autocorrect must be easily undoable; high undo rate pages quality.",
            ),
            (
                "Personal names",
                "User lexicon protects uncommon names from “fixing”.",
            ),
            (
                "CJK / languages",
                "Different tokenization; packs per locale; code-switch detector.",
            ),
            (
                "Security",
                "Signed packs; HTTPS assist; certificate pinning optional; no plaintext lexicon backup without encryption.",
            ),
            (
                "Battery profiling",
                "CI bench on mid-tier devices; reject pack if p99 infer exceeds budget.",
            ),
            (
                "Experimentation",
                "Pack versions as experiments; careful with download sizes.",
            ),
            (
                "Server cost control",
                "Assist only when local entropy high; cache popular prefixes at edge.",
            ),
            (
                "Accessibility",
                "Suggestions compatible with screen readers; large hit targets.",
            ),
            (
                "Kids Fire tablets",
                "Stricter lexicons; disable server assist by default.",
            ),
            (
                "Metrics privacy",
                "Aggregate counters; differential privacy for rare n-grams if collected.",
            ),
            (
                "Conflict with system keyboards",
                "If embedding in Amazon apps only, scope clearly vs replacing OS IME.",
            ),
            (
                "Failure mode",
                "Pack corrupt → fall back to English tiny dict; assist timeout → local only.",
            ),
            (
                "Related systems",
                "Retail search autocomplete (server), Alexa voice spelling adjacent, CDN pack distribution, privacy consent hub.",
            ),
            (
                "Cost narrative",
                "USD per million assist calls + CDN egress for packs; local-first is frugality.",
            ),
        ],
    )
    ap = appendices(
        dedent(
            """\
            ### Appendix F — Assist API sketch

            ```text
            POST /v1/assist
              { locale, prefix, context_type, device_class, consent_token }
            → { suggestions[], corrections[], pack_hints[] }
            ```

            ### Appendix G — Closer checklist

            - [ ] Local-first / offline path
            - [ ] Secure fields never learn
            - [ ] Consent for server assist
            - [ ] Battery/model size budgets
            - [ ] Safety on merge
            - [ ] Progressive scale / federated mention
            """
        )
    )
    wrap = wrapup(
        "Mobile Autocomplete & Spell-Check",
        "A **hybrid on-device + server** mobile autocomplete and spell-check system: quantized local LM/dictionaries, user lexicon, safety, optional consented server assist for long-tail/catalog terms, signed language packs, and strict privacy/battery budgets.",
        [
            "Local-first; server assist optional",
            "Never learn from secure/password fields",
            "Quantized packs with delta CDN updates",
            "Consent-gated privacy aggregates",
            "Merge local+server through safety",
        ],
        [
            "Pack size vs quality tension",
            "Multilingual code-switch hardness",
            "Assist cost if over-triggered",
            "OS IME boundary confusion",
        ],
    )
    end = "\n*End of document — Mobile Autocomplete & Spell-Check (SDE III)*\n"
    return "\n".join([h, TOC, s1, s2, s3, s4, s5, wrap, s7 + "\n---\n", ap, notes, end])
