# System Design: Viewport Pagination & Cross-Module Dedup

> **Focus areas:** Infinite scroll homepage · Viewport-based page fetch · Session-scoped seen set · Cross-row dedup below fold · Cursor tokens · Bandwidth vs freshness · Client-server contract · Merge with above-fold allocator  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct split QPS (initial page vs pagination vs prefetch), explicit cursor semantics, deal-breakers on client-only dedup, Netflix homepage scroll 2025–26 themes  
> **Interview theme:** Infinite-scroll homepage where each viewport “page” of rows arrives without repeating titles already shown anywhere on the feed

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

Goal: **bound viewport pagination with deduplication**—as the user scrolls the homepage, fetch additional row modules in chunks aligned to viewport capacity while maintaining a **session-scoped seen set** so no title repeats across modules already rendered (above and below fold).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Paginate homepage rows + cross-module dedup | Full recommender training |
| Scope | Below-fold scroll continuation + merge with above-fold | Initial above-fold only (sibling: homepage-deduplication) |
| Unit | Viewport page / batch of rows | Per-title infinite list like TikTok |
| State | Session-scoped seen set (server authoritative) | Permanent user suppression history |
| Client role | Scroll signals, prefetch hints | Sole dedup SoT (deal-breaker) |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What triggers fetch? | User nears end of loaded rows (viewport threshold) | Scroll cursor + prefetch |
| F2 | How many rows per page? | 3–6 rows or ~1–2 viewports worth | Config by device |
| F3 | Dedup scope? | All titles already on screen + prior pages | Monotonic seen set |
| F4 | Who owns seen? | Server; encoded in signed cursor | Tamper-resistant token |
| F5 | Initial page? | Above-fold sibling runs first; cursor seeds seen | Handoff contract |
| F6 | CW updates mid-scroll? | CW row may refresh; merge policy | Volatile row handling |
| F7 | Client prefetch? | 1 page ahead OK | Idempotent page fetch |
| F8 | Backward scroll? | Already rendered; no refetch | Client cache |
| F9 | Empty page? | Must not happen; widen candidates | Fallback CG |
| F10 | Determinism? | Same cursor → same next page | Pure function given inputs |
| F11 | Profile switch? | New session cursor | Invalidate |
| F12 | Ads rows? | Separate from title seen | Module type flag |
| F13 | Partial row visible? | Row-level pagination unit | Not tile-level MVP |
| F14 | Retry? | Same cursor safe | Idempotent |
| F15 | Log impressions? | Per delivered row post-dedup | Analytics contract |
| F16 | Horizontal row scroll? | Row-internal pagination separate token | Sub-cursor optional |
| F17 | Device rotation? | Fold changes; seen persists | Cursor portable |
| F18 | Experiments? | Sticky assignment in cursor | Reproducible pages |
| F19 | End of feed? | Explicit `has_more=false` | Schedule exhaustion |
| F20 | Bandwidth caps? | Compress payloads | Row fragments |

**MVP functional scope (lock with interviewer):**

1. Initial homepage response includes `pagination_cursor` with serialized seen set (compressed).  
2. Client requests `GET /homepage/next?cursor=...` when scroll threshold hit.  
3. Server expands cursor → seen, fetches next row batch candidates, ranks, dedups, returns rows + new cursor.  
4. Merge with above-fold dedup: first page uses homepage-deduplication allocator; cursor captures resulting seen.  
5. Oversampled candidates per row; backfill on underfill.  
6. Prefetch allowed; duplicate requests with same cursor return same page (short TTL cache).  
7. Metrics: empty page rate, dedup drop rate, pagination latency.

**Out of MVP (explicitly defer):**

- Tile-level virtualized grid inside single row  
- Client-computed seen as SoT  
- Cross-session “never repeat title for 30 days” (suppression sibling)  
- Optimistic client-side row insertion before server ack  
- Real-time row reordering while user mid-scroll  
- Semantic near-duplicate (remakes) detection

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Pagination latency | Faster than perceived scroll | p99 < 200–400ms |
| N2 | Initial page SLO | Unchanged | sibling budget |
| N3 | Cursor size | Fits URL/header | < 2–4 KB compressed |
| N4 | Correctness | No dupes in feed | 100% title_id policy |
| N5 | Idempotency | Retry safe | Same cursor → same page |
| N6 | Availability | Degrade to popular rows | Never blank scroll end |
| N7 | Scale | 1000× scroll fetches | See scale table |
| N8 | Security | Cursor signed | HMAC / JWT |
| N9 | Privacy | Profile-bound cursor | Auth required |
| N10 | Bandwidth | Minimal repeated metadata | Row fragments |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User opens app → above-fold page + cursor C0 with seen S0.  
2. Scroll to 80% → client prefetch next with C0 → rows R1..R5 deduped against S0 → cursor C1.  
3. Title A in Trending page 1 and Genre page 2 → A only once.  
4. Retry prefetch due to network → identical R1..R5.  
5. TV remote scroll → larger row batch per page.  
6. User scrolls 10 pages deep → seen compacts via Roaring bitmap; no dupes.  
7. Session ends → cursor discarded; new session fresh seen.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cursor tampered | 401/400; reject |
| Cursor expired (TTL) | Fresh page from recomputed seen or restart scroll |
| Seen set huge (long session) | Bloom + exact tail / rolling window policy |
| All candidates collide | Fallback popular; widen pool |
| CW updates mid-session | Optional CW refresh endpoint; merge seen |
| Profile switch | Discard cursor |
| Client renders page out of order | Server page ids monotonic; client must append in order |
| Duplicate prefetch in flight | Coalesce; idempotent cache |
| Very fast scroll | Client drops stale responses by cursor generation |
| Offline → online | Cursor invalid; soft restart from visible snapshot optional |
| Ranker brownout | Popular fallbacks; dedup still applies |
| Token size exceeds header limit | Server-side session id indirection |
| Two devices same profile | Independent cursors per device session |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| DAU | 10M | 100M | 400M | 1B |
| Peak initial page builds/s | 20K | 200K | 2M | 20M |
| Peak pagination fetches/s | 40K | 400K | 4M | 40M |
| Rows per pagination page | 4 | 4–6 | device-tuned | device-tuned |
| Avg scroll pages / session | 3 | 4 | 5 | 5 |
| Seen set size (titles) | 50–200 | 200–500 | 500–2K | compact structures |
| Cursor bytes (compressed) | 500–1500 | 1–3K | 2–4K | bloom hybrid |

**Split classes:** initial page QPS ≠ pagination QPS ≠ prefetch (often 2× pagination) ≠ CW refresh.

**What each jump forces:**

- **10×:** Signed cursor; idempotent page cache; standard row batch sizes.  
- **100×:** Compact seen (Roaring bitmap / bloom+exact); regional page service; prefetch coalescing.  
- **1,000×:** Hybrid bloom seen in cursor with exact repair; edge pagination for static rows; strict cursor TTL.

### 1.5 Etc. (Constraints & Assumptions)

- Continuation of **homepage-deduplication** for first screen.  
- Session = authenticated profile session; cursor not shared across profiles.  
- Filters before dedup on every page fetch.  
- Not the same as **search result pagination** (different dedup rules).

**Scope statement:**

> Design viewport-aligned homepage pagination with a **server-authoritative, cursor-encoded seen set** so infinite scroll modules never repeat titles already shown, scaling from ~40K pagination QPS through 10× / 100× / 1,000× with signed cursors, idempotent fetches, and compact seen serialization.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 QPS split

```text
Initial opens peak ≈ 20,000 / s
Avg user scrolls ~3 extra pages / session
Pagination QPS ≈ 20,000 × 3 × (session_duration_factor)
Peak concurrent scroll ≈ 2× initial during prime time → ~40,000 pagination / s baseline

Prefetch factor 1.5× → 60,000 prefetch attempts/s (many dedupe to cache hit)
```

At **100×** → **4M pagination/s** — page service horizontal scale; cursor verify cheap; rank dominates.

### 2.2 Seen set growth

```text
Rows per page ≈ 4
Titles per row ≈ 8
Titles per page ≈ 32
5 scroll pages ≈ 160 titles in seen
160 × 8 B id ≈ 1.3 KB raw ids
Roaring bitmap / compressed sorted deltas ≈ 200–800 B typical
```

At long binge scroll (20 pages): 600+ titles → cursor may hit 2–4 KB — need compression or bloom hybrid.

### 2.3 Latency budget (pagination path)

| Stage | Budget |
|-------|--------|
| Verify cursor + decompress seen | 1–3ms |
| Fetch CG + rank batch rows | 80–250ms |
| Dedup allocator | 5–20ms (larger seen) |
| Serialize + sign cursor | 2–5ms |
| **Total p99 target** | **< 200–400ms** |

### 2.4 Bandwidth

```text
Row payload ≈ 8 titles × (id + art + metadata) × 4 rows
≈ 32 tiles × ~2–5 KB ≈ 64–160 KB per page (varies)
Pagination 40K/s × 100 KB ≈ 4 GB/s JSON class — compress gzip/br; HTTP/2
```

### 2.5 Idempotent cache

```text
Cache key = hash(profile, cursor_in, policy_version)
TTL 30–120s
Hit rate on prefetch retry ≈ 30–50%
Reduces rank load significantly
```

### 2.6 CPU: dedup with large seen

```text
32 titles × 4 rows = 128 lookups per page in seen (O(1))
128 × 200 ns ≈ 25 µs — still negligible vs rank
Bloom false positive → wrongly drop title → need exact set or low FP bloom
```

### 2.7 Server-side session indirection (100×)

```text
When cursor > 4KB:
  cursor = { session_id, generation, sig }
  Redis/durable KV: session_id → roaring_bitmap(seen)
Memory: 4M active scroll sessions × 2KB ≈ 8 GB cluster — feasible with TTL 30–60 min
```

### 2.8 Critical bottlenecks

1. Rank/CG latency per pagination fetch  
2. Cursor size limits with long sessions  
3. Client out-of-order page apply  
4. CW refresh invalidating cursor without UX plan  
5. Underfill when catalog exhausted for user filters  
6. Forgetting to merge above-fold seen into cursor

### 2.9 Cost intuition

```text
Pagination doubles homepage-serving QPS vs open-only
Dominant cost: rank + features, not dedup
Track: pagination_p99, empty_page_rate, cursor_bytes_p95
```

---

## 3. High-Level Design

### 3.1 API contract

```text
GET /v1/homepage
  → rows_above_fold[], pagination_cursor C0, page_generation=0

GET /v1/homepage/next?cursor=C0&prefetch=true
  → rows[], pagination_cursor C1, page_generation=1, has_more=true

POST /v1/homepage/refresh-row (optional)
  → updated row + cursor patch for CW
```

### 3.2 Cursor payload (logical)

```text
PaginationCursor {
  profile_id,
  seen: CompressedSet<title_id>,  // or bloom+exact or session_ref
  page_generation: int,
  schedule_offset: int,
  policy_version: int,
  rank_context_seed: bytes,
  exp_assignments: {...},
  issued_at: ts,
  signature: HMAC
}
```

### 3.3 Pagination flow

```text
1. Decode cursor → seen_set, generation, schedule_offset
2. Select next row templates from schedule (personalized order)
3. Parallel CG + rank per row
4. Filter eligibility
5. DedupAllocator(rows, seen_set) → append-only seen
6. Build next cursor with updated seen
7. Sign + return
```

### 3.4 Row schedule

Personalized **row template order** computed at initial page (or lazily extended):

```text
row_schedule = [genre_80s, because_you_watched, comedy, ...]
page_k rows = row_schedule[k*batch : (k+1)*batch]
```

Schedule stored in cursor as template ids to keep token small.

### 3.5 Merge with above-fold

```text
Initial allocate (homepage-deduplication) → layout + seen S0
C0 = encode(S0, generation=0, schedule_offset=rows_above_fold)
First /next uses same seen — no duplicate titles between fold and page 1
```

### 3.6 Seen compaction strategies

| Strategy | When | Tradeoff |
|----------|------|----------|
| Exact sorted delta | seen < 300 | Perfect |
| Roaring bitmap | 300–2K ids | Compact |
| Bloom + exact tail | 1000× long sessions | Tiny cursor; FP risk |
| Session id indirection | cursor > 4KB | Stateful store |
| Session reset prompt | extreme scroll | UX break |

### 3.7 Prefetch protocol

Client may prefetch page N+1 when N at 70% viewport.  
Responses include `page_generation`; client ignores stale generation.  
Server caches idempotent response per cursor 60s.

### 3.8 Volatile rows (CW)

| Approach | Pros | Cons |
|--------|------|------|
| CW only on initial page | Simple | Stale CW while scrolling |
| CW refresh endpoint | Fresh | Cursor complexity |
| Periodic soft refresh | Balance | Extra QPS |

**MVP:** CW on initial; optional refresh row API at 100×.

### 3.9 Horizontal row pagination (optional)

```text
Row-level: GET /row/next?row_cursor=...
Still update global seen when new tiles materialize into viewport
Two tokens: page_cursor (vertical) + row_cursor (horizontal)
```

### 3.10 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Seen ownership | Server in signed cursor |
| Page unit | Batch of rows |
| Dedup algorithm | Same greedy as above-fold |
| Idempotency | Cursor hash cache |
| Long sessions | Roaring / bloom / session store |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+  initial      +------------------+   cursor C0   +--------+
| Client |-------------->| Homepage Service |-------------->| Client |
+--------+               | (above-fold      |               +--------+
     |                   |  dedup sibling)  |                    |
     | scroll             +--------+---------+                    |
     |                             |                              |
     |  GET /next?cursor=C0        v                              |
     +-------------------->+------------------+                   |
                           | Pagination Svc   |-------------------+
                           | - verify cursor  |
                           | - rank batch     |
                           | - dedup vs seen  |
                           | - sign C1        |
                           +--------+---------+
                                    |
                    +---------------+---------------+
                    v               v               v
              +----------+   +------------+   +-------------+
              | Rank/CG  |   | Idempotent |   | Session store|
              |          |   | page cache |   | (optional)   |
              +----------+   +------------+   +-------------+
```

### 4.2 Sequence: scroll page fetch

```text
Client: user at 75% scroll, cursor C0
Client→Pagination: GET /next?cursor=C0
Pagination: verify HMAC, decompress seen (120 titles)
Pagination: row_templates = schedule[offset:offset+BATCH]
Pagination→CG/Rank: parallel for 4 rows
Pagination: filter + dedup(seen) → 32 new titles
Pagination: seen' = seen ∪ new; C1 = encode(seen')
Pagination→Client: rows + C1, generation=1
Client: append rows; store C1; discard stale prefetches
```

### 4.3 Sequence: prefetch retry

```text
Client→Pagination: GET /next?cursor=C0 (duplicate)
Pagination→Cache: hit(idempotent_key)
Pagination→Client: cached rows + C1 (same)
```

### 4.4 Sequence: tampered cursor

```text
Client→Pagination: cursor bad sig
Pagination→Client: 400 INVALID_CURSOR
Client: reset scroll state; optional reload initial homepage
```

### 4.5 Client state machine

```text
States: LOADING | READY | PREFETCHING | APPEND | ERROR | EOF
READY + scroll_threshold → PREFETCHING(cursor)
PREFETCHING success → APPEND if generation matches
ERROR → retry same cursor (idempotent)
Profile change → LOADING (discard cursors)
EOF → stop prefetch; has_more=false
```

### 4.6 CW refresh mid-scroll

```text
Client→Pagination: POST /refresh-row {cursor, row_id=cw}
Pagination: fetch fresh CW; re-dedup against seen (CW may add new titles)
Pagination: patch layout delta; cursor unchanged or minor bump
Client: replace CW row in place without discarding scroll history
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Monotonic seen** — only grows within session (until reset).  
2. **No title duplicate** across all pages in session under policy.  
3. **Cursor integrity** — reject unsigned/tampered.  
4. **Idempotent pagination** — same cursor → same next page (within TTL).  
5. **Ordered delivery** — client applies pages by generation.  
6. **Filters before dedup** every fetch.  
7. **Above-fold seen included** in C0.  
8. **Profile bound** — cursor profile_id must match auth.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Rank timeout | Fallback CG; dedup |
| Session store miss | 400 SESSION_EXPIRED; soft restart |
| Bloom FP | Conservative drop; monitor diversity |
| Empty page after dedup | Emergency popular fill; alert |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Pagination svc colocated; exact seen in cursor |
| 10× | Idempotent cache; Roaring compression |
| 100× | Session store for large seen; dedicated pagination pods |
| 1,000× | Edge static fragments; bloom hybrid; aggressive TTL |

### 5.3 Maintainability

- Shared DedupAllocator library with homepage-deduplication.  
- Cursor schema versioned; backward compatible decode for 1 version.  
- Metrics: `pagination_qps`, `cursor_bytes_p95`, `empty_page_rate`, `dedup_drop_rate`, `prefetch_hit_rate`.  
- Chaos: corrupt cursor, expire TTL, rank timeout.

### 5.4 Exact algorithm: next page

```text
function nextPage(cursor_token, auth):
  c = verify_and_decode(cursor_token, auth.profile_id)
  if c.session_ref: seen = sessionStore.get(c.session_ref)
  else: seen = decompress(c.seen)
  rows_templates = schedule.slice(c.offset, c.offset + BATCH)
  results = []
  for tmpl in rows_templates:
    cands = rank(cg(tmpl), context=c.rank_seed)
    cands = filter(cands, auth.profile)
    filled = []
    for t in cands:
      if canonical(t) in seen: log_drop(...); continue
      filled.append(t); seen.add(canonical(t))
      if len(filled) >= tmpl.target: break
    if len(filled) < tmpl.min: backfill(tmpl, filled, seen)
    results.append(row(tmpl, filled))
  c' = c.with(seen=seen, offset=c.offset+BATCH, generation=c.generation+1)
  cache.put(idempotent_key(c), response, ttl=60s)
  if size(seen) > THRESH: c' = spill_to_session_store(seen)
  return sign(encode(c')), results
```

### 5.5 Bloom hybrid seen (100×)

```text
cursor.seen_bloom = bloom(all_seen)
cursor.seen_exact_tail = last 100 ids
check(t):
  if t in exact_tail: return SEEN
  if bloom.may_contain(t): return SEEN  # conservative
  return NOT_SEEN
```

### 5.6 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Client maintains seen alone | Tampering; desync; dupes |
| No cursor signing | Gaming; privacy leak |
| Pagination without seen from fold | Dupes across fold boundary |
| Stream rows without generation | Out-of-order dupes/holes |
| Unbounded exact seen in cursor | 413 / header limits |
| Separate dedup rules below fold | Inconsistent UX |
| Cache pagination anonymously | Cross-profile leak |
| Offset-only pagination (page=3) | No cross-row dedup state |

### 5.7 Progressive scale deep dive

**1× (~40K pag/s)**  
Exact seen in signed cursor; shared allocator; 60s idempotent cache.

**10×**  
Roaring bitmap compression; prefetch coalescing at gateway; row schedule in cursor.

**100×**  
Bloom+exact hybrid OR session store; dedicated pagination tier; CW refresh API.

**1,000×**  
Static row fragments at edge merged with seen check at origin; cursor TTL 5–15 min; session reset UX for ultra-long scroll.

### 5.8 Multi-region

Cursor issued in region of page build; verify anywhere with shared secret.  
Rank/CG regional.  
Session store: profile home region sticky.  
Idempotent cache regional (not global — OK for prefetch).

### 5.9 Security

- HMAC-SHA256 cursor with rotating keys.  
- profile_id in cursor must match token.  
- TTL limits replay window.  
- Do not embed PII in cursor.

### 5.10 Observability

- Trace: cursor generation, rows returned, drops, bytes.  
- Alert: empty_page_rate > 0.1%; pagination p99 regression.  
- Sample cursor decode failures.

### 5.11 Impression logging

Log **page_generation** and final row items only.  
Do not log pre-dedup candidates.  
Join training on delivered tiles across scroll depth.

### 5.12 Rollout

```text
Dark launch pagination w/o dedup shadow metrics → enforce dedup → enable prefetch → tune batch sizes
Compare duplicate_visible_rate in scroll sessions
Guardrail: empty_page_rate
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Trigger | Viewport scroll threshold |
| State | Signed cursor with compressed seen |
| Dedup | Shared greedy allocator |
| Initial handoff | Above-fold sibling seeds C0 |
| Idempotency | Per-cursor response cache |
| Long sessions | Roaring / bloom / session store |

### 6.2 Risks

1. Cursor size growth on long sessions  
2. Bloom false positives reducing diversity  
3. CW staleness during scroll  
4. Client out-of-order page bugs  
5. Rank latency dominating UX  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Pagination vs initial page; seen scope |
| 5–15 | Cursor design + signing |
| 15–25 | Dedup merge with above-fold |
| 25–35 | Prefetch idempotency + client ordering |
| 35–45 | Scale, bloom hybrid, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Product

**Q: Why not load all rows upfront?**  
A: Latency, bandwidth, rank cost; most users don’t scroll entire homepage.

**Q: Why server seen vs client?**  
A: Tamper resistance, consistency, training logs match delivery.

**Q: TikTok-style per-title feed?**  
A: Different product; row-module pagination here.

### 7.2 Cursor design

**Q: Cursor too large?**  
A: Roaring bitmap, bloom hybrid, or session store indirection.

**Q: Stateless server?**  
A: Mostly yes with cursor; session store optional at 100×.

**Q: TTL?**  
A: 15–60 min typical; forces refresh on stale sessions.

### 7.3 Dedup

**Q: Same algorithm as above-fold?**  
A: Yes — shared library; seen monotonic.

**Q: Allow dupes far apart in feed?**  
A: Product policy; default no dupes in session.

**Q: Difference from suppression?**  
A: Suppression is cross-session hide; seen is layout state.

### 7.4 Client

**Q: Prefetch duplicates?**  
A: Idempotent server cache + generation guard.

**Q: Fast scroll?**  
A: Drop responses with old generation.

**Q: Back scroll up?**  
A: Client cache; no server refetch.

### 7.5 Traps

**Q: Redis seen per user forever?**  
A: Wrong problem — session scoped with TTL.

**Q: Paginate tiles inside row only?**  
A: Phase 2; row-level MVP for vertical scroll.

**Q: Skip signing?**  
A: Security / cheating risk.

**Q: page=2 offset only?**  
A: Cannot dedup across modules without seen state.

### 7.6 Scale

**Q: 40M pagination QPS?**  
A: Rank shards; idempotent cache; edge fragments; session store cluster.

### 7.7 CW refresh

**Q: Mid-scroll CW update?**  
A: Dedicated refresh API patching row without full cursor reset.

### 7.8 Comparison

**Q: vs search pagination?**  
A: Search uses query-specific dedup; different schedule.

**Q: vs homepage above-fold doc?**  
A: Sibling seeds seen; this extends below fold.

### 7.9 Analytics

**Q: Scroll depth metrics?**  
A: page_generation histogram; dup audit sample.

### 7.10 Session store

**Q: When cursor vs Redis session?**  
A: Cursor until size limit; then session_ref indirection.

---

## 8. Appendices

### A1. Cursor wire format (conceptual)

```text
base64url(json_payload).hmac_sha256
payload: {
  v: 3,
  pid: "profile_uuid",
  gen: 7,
  off: 28,
  seen: "roaring_b64" | null,
  sess: "session_uuid" | null,
  pol: 12,
  rs: "seed_bytes",
  iat: 1690000000
}
```

### A2. Response schema

```text
HomepageNextResponse {
  page_generation: int,
  rows: Row[],
  pagination_cursor: string,
  has_more: bool,
  dedup_policy_version: int
}
```

### A3. Launch checklist

- [ ] Above-fold handoff seen verified  
- [ ] Cursor sign/verify tests  
- [ ] Idempotent cache hit rate monitored  
- [ ] Client generation ordering tests  
- [ ] Long session cursor size load test  
- [ ] empty_page_rate dashboard  
- [ ] Session store TTL chaos test  

### A4. Glossary

| Term | Meaning |
|------|---------|
| Viewport page | Batch of rows fetched per scroll |
| Seen set | Titles already allocated in session |
| Cursor | Signed pagination state token |
| Generation | Monotonic page counter |
| Prefetch | Early fetch before user reaches end |
| Session ref | Indirection when seen too large for cursor |

### A5. 60-second summary

> Viewport pagination serves **batches of homepage rows** on scroll using a **signed cursor** that carries a compressed **seen set** from all prior modules (including above-fold). Each fetch ranks oversampled candidates, runs the **same dedup allocator**, appends to seen, and returns the next cursor — **idempotent** under prefetch retry, scaling with stateless page pods and compact seen structures.

### A6. Related systems

```text
Homepage dedup (fold) → seeds cursor
Pagination svc → extends seen
Dynamic recs → CG/rank
Client scroll controller → prefetch + ordering
Suppression → pre-filter (not seen)
```

### A7. SLO sketch

| SLO | Target |
|-----|--------|
| Duplicate rate in scroll session | 0 |
| Pagination p99 | < 400ms |
| empty_page_rate | < 0.01% |
| cursor_bytes p95 | < 3 KB |

### A8. Worked example

```text
S0 = {A..H} from above-fold (64 titles across 8 rows)
Page 1 candidates include A again → dropped
Page 1 adds 32 new titles → S1 = 96 titles
After 5 pages: S ≈ 160 titles; cursor ~800B compressed
```

### A9. Test plan

1. Fold + page1 no overlap.  
2. Retry cursor → identical page.  
3. Tamper cursor → 400.  
4. Generation mismatch → client ignores.  
5. Long session → cursor under size cap OR session ref.  
6. Profile mismatch → 403.  
7. Empty CG → fallback fills page.  
8. CW refresh → no dupes introduced.

### A10. Ownership

| Concern | Owner |
|---------|-------|
| Pagination API | Homepage platform |
| Cursor crypto | Platform security |
| Dedup allocator | Shared personalization lib |
| Client scroll | TV/mobile/web teams |
| Session store | Page infra |

### A11. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Signed cursor + exact seen |
| 10× | Roaring + idempotent cache |
| 100× | Bloom hybrid OR session store |
| 1,000× | Edge fragments + TTL policy |

### A12. On-call cheat sheet

1. pagination p99 up → rank/CG.  
2. cursor decode errors → key rotation?  
3. empty pages → fallback CG.  
4. dup reports → fold handoff bug?  
5. session store memory → TTL tuning.

### A13. Naive comparison

| Naive | Failure |
|-------|---------|
| Client seen only | Dupes / cheat |
| No idempotency | Duplicate rows on retry |
| Independent fold/page dedup | Boundary dupes |
| page=N offset only | No cross-module dedup |
| Store all seen in Redis forever | Wrong abstraction + cost |

### A14. Cost worksheet

```text
pagination_qps ≈ 2-3 × initial_page_qps
rank_cost dominates ≈ rows_per_page × rank_cost_per_row
cache_hit saves ~30-50% rank on prefetch retries
session_store_GB ≈ active_sessions × avg_bitmap_bytes
```

### A15. Non-goals

- Cross-session dedup  
- Tile-level virtualization MVP  
- Real-time row reorder mid-scroll  
- Semantic remake detection  

### A16. Client API pseudocode

```text
onScroll(percent):
  if percent > 0.75 and not prefetching and has_more:
    prefetch(next(cursor))

onPrefetchResponse(resp):
  if resp.generation != expected: return
  buffer = resp
  cursor = resp.pagination_cursor

onReachEnd():
  append(buffer.rows); expected++
  if not resp.has_more: state = EOF
```

### A17. Row schedule encoding

```text
schedule_ids: ["genre_80s", "byw", "comedy", ...]
offset: integer into schedule
Avoids recomputing full personalized order each page
```

### A18. Interviewer rubric

- [ ] Cursor carries seen  
- [ ] Fold handoff  
- [ ] Idempotent prefetch  
- [ ] Stateless vs session store tradeoff  
- [ ] Long session compaction  
- [ ] Client generation ordering  

### A19. FAQ

**Why not GraphQL infinite list?**  
Same concepts — cursor + seen + dedup; transport agnostic.

**Why not offset pagination?**  
Offset doesn’t carry dedup state; reranking breaks determinism.

### A20. Session reset UX

When cursor expires or too large:  
Soft message “Refreshing recommendations” → new initial page; preserve CW via separate fetch.

### A21. Duplicate visible audit

```text
Client QA sample: hash visible title_ids in session
Compare to server expected seen
duplicate_visible_rate must ≈ 0
```

### A22. Integration test fixture

```text
Build page0 with titles [A..Z fold set]
next(C0) must not contain any of fold set
next(C1) must not contain fold + page1 sets
```

### A23. Bandwidth optimization

```text
Row fragments: ids + art URLs only; metadata lazy on focus
Delta compress repeated studio/genre fields across page
```

### A24. Metrics cardinality rules

```text
OK: dedup_drop_rate by row_template_id (low cardinality)
BAD: dedup_drop_rate by title_id (explodes)
```

### A25. Explicit non-goals recap

- Lifelong browse history in cursor  
- Client-only dedup SoT  
- Per-household shared scroll state across profiles  

---

*End of document — Netflix system design interview prep: Viewport Pagination & Cross-Module Dedup.*
