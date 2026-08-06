# System Design: Homepage Above-the-Fold Deduplication

> **Focus areas:** Cross-row title uniqueness · Page constructor · Candidate budgets · Viewport definition · Deterministic layout · Interaction with personalization CGs · Performance under peak open  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Clear ownership (server vs client), correct latency math, explicit deal-breakers, Netflix homepage delivery 2025–26 themes  
> **Interview theme:** Render the homepage “above the fold” without repeating the same title across modules

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

Goal: **bound homepage deduplication**—given many personalized rows competing for the same hot titles, produce an above-the-fold layout where each title appears at most once (policy), without emptying rails or blowing the page-build SLO.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Cross-module title dedup for first screen | Full recommender training |
| Scope | Above-the-fold (+ optional first N rows) | Infinite scroll pagination (sibling: viewport-pagination-dedup) |
| Plane | Page construction / layout | CDN video delivery |
| Identity | Profile-scoped page | Account mashup |
| Time horizon | Single page build / session open | Cross-session fatigue (suppression sibling) |
| Optimization | Greedy constrained allocation | Global combinatorial optimizer |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is “duplicate”? | Same `title_id` (or collection parent policy) | Canonical id mapping |
| F2 | Where enforced? | Server page constructor (client assist OK) | Server SoT |
| F3 | Which rows participate? | All above-fold modules; CW often privileged | Priority / pin rules |
| F4 | Who wins conflicts? | Higher-priority row keeps title; loser backfills | Row priority + candidate pools |
| F5 | Empty row risk? | Must still fill min titles | Oversized candidate lists |
| F6 | Series / seasons? | Dedup by show_id optional | Policy flag |
| F7 | Artwork variants? | Same title different art still duplicate | Key = title_id |
| F8 | Editorial pins? | Pinned may force keep; others yield | Pin precedence |
| F9 | Ads modules? | Ads not titles; skip or separate | Don’t dedup ads vs organic wrongly |
| F10 | Logging? | Log drops for analysis | `dedup_drop` events |
| F11 | Determinism? | Same inputs → same layout | Pure function constructor |
| F12 | Partial refresh? | Refresh one row without reshuffle chaos | Stable IDs / surgical rebuild |
| F13 | Kids profiles? | Filter before dedup; never show adult | Filter ordering invariant |
| F14 | Entitlements? | Unplayable titles never allocated | Pre-dedup eligibility |
| F15 | Evidence strings? | “Because you watched X” may reference dropped title | Evidence from winner row only |
| F16 | A/B layout? | Dedup policy version stamped | Experiment hooks |
| F17 | Locale / dub? | Same title_id across languages | Canonical id unchanged |
| F18 | Collection rails? | Dedup member vs collection parent policy | Config per template |
| F19 | Minimum diversity? | Optional genre caps after dedup | Secondary pass |
| F20 | Brownout? | Dedup never blocks page | Always emit layout |

**MVP functional scope (lock with interviewer):**

1. Define above-the-fold = first K rows or pixel/viewport estimate by device class.  
2. Gather ranked candidate lists per row (**oversampled**).  
3. Greedy allocate titles by row priority with a global `seen` set.  
4. Backfill from remaining candidates to meet `min_items`.  
5. Privileged rows (e.g. CW) exempt or soft-exempt per policy.  
6. Emit layout + dedup diagnostics (sampled).  
7. Integrate with recommendation page service; impressions log **post-dedup** layout only.

**Out of MVP (explicitly defer):**

- Perfect pixel-accurate fold prediction for all devices  
- Semantic near-duplicate detection (same story remakes)  
- Client-only enforcement as SoT  
- Cross-day historical “never show again” (suppression ≠ dedup)  
- Global ILP optimizer across all rows  
- Real-time collaborative dedup across household profiles viewing simultaneously

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Dedup stage latency | Tiny slice of page build | p99 < 5–15ms |
| N2 | Page still within SLO | Yes | Overall page p99 unchanged envelope |
| N3 | Correctness | No dupes above-fold | 100% for exact title_id policy |
| N4 | Fill rate | Rows meet min_items | >99% rows filled |
| N5 | Determinism | Replayable | Pure given seeds/inputs |
| N6 | Availability | Never fail page on dedup | Dedup always succeeds; may degrade diversity |
| N7 | Observability | Drop rates visible | Metrics without high cardinality |
| N8 | Scale | Through 1000× page QPS | CPU-only stage; no new hot KV |
| N9 | Privacy | Profile-scoped layout | Cache keys include profile |
| N10 | Testability | Property tests in CI | Golden fixtures |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Top Picks and Trending both want Title A → higher priority keeps A; Trending takes B.  
2. CW lists A → A still in CW; removed from lower rails.  
3. Editorial pin of A in row 3 → row 3 keeps A; others cannot use A.  
4. Oversampled candidates allow full rails after drops.  
5. Device class TV (fewer rows above-fold) vs mobile.  
6. Kids profile: adult titles filtered pre-dedup; rails still fill from kids pool.  
7. Experiment variant changes row order but dedup policy version logged.  
8. Replay same request_id + inputs → identical JSON layout.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Candidate list too short after dedup | Backfill from fallback CG / popular |
| All rows prioritize same 5 titles | Diversity rules + deeper candidates |
| Constructor bug allows dupe | Invariant test fails ship |
| Client reorders rows | Server positions authoritative |
| Title ID alias (remount/AVOD variants) | Canonicalization map |
| Concurrent row async fetch | Barrier then dedup; don’t stream undeduped above-fold |
| Pin conflicts two pins same title | Config validation reject / first pin wins |
| Kids filter after dedup empties row | Re-run fill with filtered pool (filter before dedup preferred) |
| CW empty (new profile) | CW row hidden or placeholder; dedup continues |
| Ranker timeout on one row | Degraded candidates; dedup still runs |
| Stale canonical map | Rare dupes or wrong merges; alert on alias drift |
| Partial row refresh mid-session | Surgical re-alloc with optional stability bias |
| Two profiles same device rapid switch | Separate cache keys; no cross-profile seen bleed |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak page builds/s | 20K | 200K | 2M | 20M |
| Rows above-fold | 5–8 | same | same | device-specific |
| Candidates / row | 30–100 | 50–150 | 100–200 | pre-trimmed |
| Titles considered / page | ~500 | ~800 | ~1K | ~1K |
| Dedup CPU ns/title | ~100 | same | same | SIMD/batch |
| DAU | 10M | 100M | 400M | 1B |
| Catalog titles (region) | 15K | 50K | 200K | 1M |

**Split classes:** page build QPS ≠ impression logging ≠ offline pre-dedup batch ≠ canonical map refresh.

**What each jump forces:**

- **10×:** Always oversample; pre-canonical ids in CG output; golden tests in CI.  
- **100×:** Dedup on precompute for stable rows; online only for volatile (CW); fragment caching post-dedup.  
- **1,000×:** Edge applies final CW privilege on signed row fragments; regional canonical maps.

### 1.5 Etc. (Constraints & Assumptions)

- Netflix-like **profile-scoped** homepage with multiple personalized rails.  
- Dedup ≠ frequency cap (ads) and ≠ Not Interested suppression.  
- Filters (maturity, entitlement, suppression) run **before** dedup.  
- Sibling docs: dynamic recommendation, viewport pagination dedup, ads modules.

**Scope statement:**

> Design server-side above-the-fold homepage deduplication that merges multi-row candidate lists into a duplicate-free first screen with privileged rails, backfill, deterministic layout, and negligible latency overhead through progressive scale from ~20K page builds/s through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 CPU cost

```text
Titles considered / page ≈ 8 rows × 60 candidates = 480
Operations: hash set insert/lookup ~ O(1)
480 × 200 ns ≈ 96 µs → negligible vs 100–400ms page budget
```

Bottleneck is **candidate generation quality / oversample**, not dedup CPU.

### 2.2 Oversample math

```text
Need show M=8 titles per row after dedup
Head-title collision rate high on top 100 catalog
Provide candidates C ≥ 3M–5M (e.g. 24–40) per row minimum

Example collision model (simplified):
  Pool overlap if rows sample from same head distribution
  P(all rows want top-10 title) ≈ high for 5+ rows
  Without oversample: expected unique titles << slots needed

If fill fails after dedup: pull from fallback list F (geo popular)
Target underfill rate < 1%
```

### 2.3 Memory per request

```text
seen set: up to ~64–80 title_ids above-fold × 16 B id ≈ 1–2 KB
candidate lists: 8 × 60 × 16 B ≈ 7.7 KB (references, not full metadata)
Total allocator working set ≪ 100 KB — stack/heap trivial per pod
```

### 2.4 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Page builds (embeds dedup) | 20K | 2M | 20M | horizontal page pods |
| Dedup-only if extracted | 20K | 2M | 20M | still in-process preferred |
| Dedup drop events (sampled) | 2K | 20K | 200K | 10% sample |
| Canonical map reads | 20K | 2M | 20M | in-memory cache |
| Fallback CG pulls | 200 | 2K | 20K | on underfill |

**Deal-breaker:** treating dedup as separate networked microservice with Redis `seen` per user — wrong problem (that’s suppression).

### 2.5 Latency budget (page build slice)

| Stage | Budget |
|-------|--------|
| Fetch row candidates (parallel) | 50–200ms (dominant) |
| Filter entitlement/maturity | 5–15ms |
| Rank per row | 20–80ms |
| **Dedup allocator** | **<5–15ms p99** |
| Attach metadata/art | 10–30ms |
| Serialize response | 5–10ms |

### 2.6 Failure cost of client-only dedup

```text
Client removes dupes after paint → layout shift, empty holes, analytics lies
Server dedup avoids FOUC / empty rails
Training on pre-dedup impressions → biased models (shown titles user never saw)
```

### 2.7 Metrics volume

```text
dedup_drops / s ≈ pages/s × avg_drops
20K × 5 drops = 100K events/s → aggregate; sample raw at 1–10%
Cardinality: never label metrics by title_id at full cardinality
```

### 2.8 Score loss estimation

```text
If Top Picks loses rank-1 title A to CW:
  Takes rank-2 D instead
  score_loss ≈ score(A) - score(D) — track distribution sampled
High score_loss → increase oversample or adjust row priority product-side
```

### 2.9 Critical bottlenecks

1. Under-sampled CG lists → empty rows  
2. Wrong priority ordering → CW loses titles  
3. Non-canonical IDs → visual dupes  
4. Partial row streaming before dedup complete  
5. Caching pre-dedup fragments incorrectly keyed  
6. Filter-after-dedup causing refill loops

### 2.9 Cost intuition

```text
Dedup CPU cost ≈ $0 marginal vs ranker/GPU/feature store
Real cost driver: deeper candidate pools → more rank compute upstream
Track: row_underfill_rate, score_loss_p95, page_build_latency
```

---

## 3. High-Level Design

### 3.1 Placement in personalization funnel

```text
CGs → filter → rank per row → ranked candidate lists → DEDUP ALLOCATOR → final row items → metadata → response
                                                              ↓
                                                    impression logs (post-dedup)
```

Filters (maturity/entitlement/suppression) **before** dedup.

### 3.2 Entities

| Entity | Role |
|--------|------|
| `RowTemplate` | id, priority, min_items, target_items, privileges |
| `CandidateList` | ordered title_ids + scores from ranker |
| `DedupPolicy` | fold config, canonical mode, pin rules |
| `SeenSet` | global set for current page build |
| `Layout` | final row → items mapping |
| `DedupDiagnostic` | drops, backfills, policy version |

### 3.3 Core algorithm (greedy priority pass)

```text
seen = {}
for row in rows_by_priority:
  out = []
  for title in row.candidates:  # already ranked
    cid = canonical(title)
    if cid in seen and not row.allow_duplicate:
      log_drop(row, title); continue
    out.append(title); seen.add(cid)
    if len(out) == row.target: break
  if len(out) < row.min:
    backfill(row, out, seen, fallbacks)
  emit(row, out)
validate(layout)  # CI + optional runtime assert
```

### 3.4 Priority & privileges

| Row type | Priority | Dup policy |
|----------|----------|------------|
| Continue Watching | Highest | Keep; others yield |
| Because You Watched | High | Standard |
| Top Picks | High | Standard |
| New & Popular | Medium-High | Standard |
| Trending / Popular | Medium | Standard |
| Genre rails | Lower | Standard |
| Editorial pinned | Pin-local highest for pinned ids | Pin wins |
| Live / Events (if any) | Configurable | Often privileged |

### 3.5 Canonicalization

```text
canonical_id(title) → show_id or title_id per policy
Map episodic assets to parent show when "dedup seasons" enabled
Alias table: remaster_id → canonical_id (versioned, cached)
```

### 3.6 Device fold definition

| Device | Above-fold heuristic |
|--------|----------------------|
| Phone portrait | First 4–6 rows |
| Phone landscape | First 3–5 |
| Tablet | First 5–7 |
| TV / STB | First 3–5 (larger tiles) |
| Web desktop | First 5–8 |

Config by `device_class`; optional client reports `visible_row_count` hint for pagination sibling.

### 3.7 Two-pass variant (pins + CW)

```text
Pass 1: rows with forced pins / CW — populate seen
Pass 2: remaining rows by priority — standard greedy
Ensures pins never displaced by lower rows processed first
```

### 3.8 Stable layout

- Row IDs stable across sessions where template unchanged.  
- Within row, stable sort by rank score then title_id tie-break.  
- Optional `layout_seed` from request_id for exploration slots only.  
- Partial refresh: re-run only affected rows + downstream rows if seen changed.

### 3.9 Partial refresh API (logical)

```text
RebuildRows(profile, changed_row_ids[], prior_layout?, policy) → LayoutDelta
Prefer stability: if title still in top-K candidates, keep slot position
```

### 3.9 Backfill sources (ordered)

1. Remaining candidates in same row (already exhausted in greedy — skip)  
2. Row-specific fallback CG (genre popular)  
3. Global geo popular list  
4. Editorial emergency fill (rare)

### 3.10 Trade-offs summary

| Approach | Pros | Cons | Choice |
|----------|------|------|--------|
| Server greedy | Simple, fast, testable | Not globally optimal | **MVP** |
| Global ILP optimizer | Optimal relevance+diversity | Too slow / complex | No |
| Client-only | Easy server | UX holes; inconsistent | Deal-breaker as SoT |
| Pre-dedup offline only | Cheap online | CW/trending stale conflicts | Hybrid at 100× |
| Per-title distributed lock | Strong exclusion | Absurd latency | No |

### 3.11 Consistency model

- Single page build: synchronous barrier — all row candidates ready before dedup.  
- No cross-request `seen` in dedup (that’s suppression / pagination sibling).  
- Cache: post-dedup layout fragments keyed by `(profile, cw_version, policy_version)`.

### 3.12 Failure policy

| Failure | Behavior |
|---------|----------|
| One row CG empty | Use fallback list; dedup continues |
| Dedup invariant violation (bug) | Block deploy via CI; runtime sample assert |
| Canonical map miss | Treat raw title_id; alert |
| All fallbacks exhausted | Reduce min_items temporarily (last resort) + page still ships |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     ranked lists      +----------------------+
| Row Rankers |---------------------->| Page Constructor     |
| (per module)|                       |  - fetch barrier     |
+-------------+                       |  - filter (done)     |
       ^                              |  - DedupAllocator    |
       |                              |  - metadata attach   |
+-------------+                       +----------+-----------+
| CG Registry |                                  |
+-------------+                                  v
                                      +----------------------+
                                      | Homepage JSON + diag |
                                      +----------+-----------+
                                                 |
                    +----------------------------+----------------------------+
                    v                            v                            v
              +-----------+              +-------------+              +-------------+
              | Client UI |              | Impression  |              | Experiments |
              |           |              | logging     |              | analysis    |
              +-----------+              +-------------+              +-------------+
```

### 4.2 Sequence: full page build

```text
Client→PageSvc: GET /homepage (profile, device_class)
PageSvc→CW: get continue watching list
PageSvc→CGs: parallel fetch candidates per row template
PageSvc: filter (maturity, entitlement, suppression)
PageSvc→Rankers: parallel rank per row
PageSvc: DedupAllocator.run(rows, policy)
PageSvc: attach art, evidence, deeplinks
PageSvc→Client: layout JSON + dedup_policy_version
Client: render above-fold from server order
```

### 4.3 Sequence: conflict resolution

```text
CW:        [A, B, C]
TopPicks:  [A, D, E, F, G, ...]
Trending:  [A, D, H, I, ...]

Allocator (CW priority first):
  CW → [A,B,C]; seen={A,B,C}
  TopPicks → skip A → [D,E,F,G,H,I,J,K]
  Trending → skip A,D → [H,I,J,K,L,M,N,O]

Log: drop(top_picks,A,reason=cw_wins), drop(trending,A), drop(trending,D)
```

### 4.4 Sequence: underfill backfill

```text
Genre row candidates after dedup: 4 items, min=6
Allocator→FallbackCG: get genre_popular(limit=20)
Backfill adds 2 unseen eligible titles
If still short → global popular
Emit row with 6 items; metric row_underfill_backfill++ 
```

### 4.5 Integration with caching

```text
                    +------------------+
  stable rows ----->| Pre-deduped      |
  (batch)           | fragment cache   |
                    +--------+---------+
                             |
  volatile CW ------+        v
                    |   Merge + DedupAllocator (online)
                    +------------------+
                             |
                             v
                    post-dedup response cache (short TTL)
```

### 4.6 CI validation pipeline

```text
Golden fixtures → allocate() → validate(no dupes, min_items) → block merge on fail
Property test: random candidates → invariant checks
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Exact title_id uniqueness** above-fold under policy (canonical).  
2. **CW privilege** honored when configured.  
3. **min_items** best-effort with fallbacks; never null page.  
4. **Filters before dedup** — never allocate ineligible titles.  
5. **Deterministic** replay for same inputs + policy version.  
6. **Dedup never throws** away the page — always emit best-effort layout.  
7. **Impression logs reflect post-dedup** positions only.  
8. **Ads modules excluded** from title seen set unless product explicitly merges.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Ranker timeout one row | Fallback candidates; dedup |
| Canonical map stale | Use raw id; monitor dup reports |
| Backfill exhausted | Lower min or hide row template |
| Bug: duplicate in layout | CI catches; runtime sample assert |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | In-process greedy in page service |
| 10× | Oversample standards; canonical map in-process cache |
| 100× | Offline pre-dedup stable rails; online merge CW/trending only |
| 1,000× | Edge merge signed fragments; CW privilege at edge |

Dedup is **embarrassingly parallel** per request — scales with page service pods.

### 5.3 Maintainability

- Policy as data: priorities, min_items, canonical mode, fold rows.  
- Golden tests with conflict fixtures in CI.  
- Metrics: `dedup_drop_rate`, `row_underfill_rate`, `allocator_ms`, `score_loss_sampled`.  
- Shadow mode: compute drops without enforcing (debug only — don’t ship shadow to prod enforce off).  
- Version stamp `dedup_policy_version` on every response.

### 5.4 Exact algorithm: allocate with pins

```text
function allocate(rows, policy):
  seen = Set()
  layout = {}
  pinned = collect_pins(rows)
  for pin in pinned ordered by row_priority:
    assert eligible(pin.title)
    layout[pin.row].insert(pin.slot, pin.title)
    seen.add(canonical(pin.title))
  for row in rows_by_priority(rows):
    if row already has pin slots filled: continue partial
    out = layout.get(row, [])
    for title in row.candidates:
      if len(out) >= row.target: break
      cid = canonical(title)
      if cid in seen and not row.allow_duplicate: log_drop(...); continue
      out.append(title); seen.add(cid)
    if len(out) < row.min: backfill(row, out, seen)
    layout[row] = out
  assert validate(layout, policy)
  return layout
```

### 5.5 Exact algorithm: backfill

```text
function backfill(row, out, seen, fallbacks):
  for source in [row.fallback_cg, global_popular, editorial_emergency]:
    for title in source.candidates:
      if len(out) >= row.min: return
      cid = canonical(title)
      if cid in seen: continue
      if not eligible(title, row.profile): continue
      out.append(title); seen.add(cid)
      metric backfill_source++
```

### 5.6 Algorithm variants

**Quota diversity (post-dedup):** cap titles per genre in a row — second pass swap.  
**Soft dup below fold:** only above-fold rows in seen for fold pass; sibling handles scroll.  
**Stability bias:** on refresh, prefer previous winners if still in top-2K candidates.

### 5.7 Interaction with personalization

Dedup can hurt Top Picks relevance if oversample weak — measure `score_loss` from drops. Fix via deeper candidates, not by disabling dedup.  
Training pipelines must join impressions to **delivered** layout, not raw ranker output.

### 5.8 Interaction with experiments

Experiment may change row order → changes priority → changes winners. Log `exp_id`, `dedup_policy_version`, drops for analysis.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Client-only SoT | Empty holes / dupes flash |
| Dedup before kids filter | Wasted slots / refills |
| No oversample | Underfilled rails |
| Mutating CG lists without copy | Race / reuse bugs |
| Global Redis seen per user | Wrong abstraction; latency |
| Stream rows to client before dedup | User sees dupes briefly |
| Cache anonymous homepage at CDN | Cross-user leak |
| Train on pre-dedup candidates | Label noise |

### 5.10 Progressive scale deep dive

**1× (~20K page builds/s)**  
Single page service; in-process allocator; PG for policy; golden tests.

**10×**  
Standardize oversample 3–5×; canonical map service with local cache; aggregate drop metrics.

**100×**  
Batch pre-dedup for stable rails (genre, popular); online allocator merges CW + trending fragments; post-dedup fragment cache.

**1,000×**  
Signed offline fragments to edge; edge CW overlay with privilege; regional canonical maps; SIMD set ops if profiling demands (usually unnecessary).

### 5.11 Multi-region

Dedup is stateless CPU; runs in regional page builders with regional catalogs already filtered. No cross-region seen set.

### 5.12 Security & privacy

- Layout responses authenticated; cache keys include profile.  
- Dedup diagnostics internal/sampled — don’t expose drop reasons to client.  
- Kids profiles: fail-closed filters before dedup.

### 5.13 Rollout

```text
Shadow metrics (drops only) → enforce above-fold → expand device fold configs → default on
Guardrails: row_underfill_rate, duplicate_visible_rate (client QA sample)
Instant rollback: policy version flag
```

### 5.14 Observability dashboards

- `duplicate_visible_rate` (client QA / manual audit)  
- `dedup_drop_rate` by row template (low cardinality)  
- `row_underfill_rate`  
- `allocator_ms_p99`  
- `score_loss_p95` sampled

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Ownership | Server page constructor |
| Algorithm | Priority greedy + oversample + backfill |
| CW | Privileged |
| Fold | Device-class heuristic |
| Logs | Post-dedup impressions |
| Store | No hot KV; in-process seen set |
| Canonical | title_id or show_id policy |

### 6.2 Risks

1. Underfill from weak oversample  
2. Priority misconfig starving exploration  
3. Canonical ID mistakes → visible dupes  
4. Churn on partial refresh  
5. Training on wrong impression labels  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Define duplicate + above-fold |
| 5–15 | Greedy allocator + CW privilege |
| 15–25 | Oversample math + underfill |
| 25–35 | Integration with CGs/filters |
| 35–45 | Scale, client myths, traps |

---

## 7. Deeper / Related Interview Questions

### 7.1 Product semantics

**Q: Server vs client dedup?**  
A: Server SoT; client may hide flash but shouldn’t be sole enforcer for above-fold.

**Q: Why oversample?**  
A: Head titles collide across rails; without extras, rows go empty after drops.

**Q: Is dedup an ML model?**  
A: No — constrained allocation; ML produces ranked candidates.

**Q: Show vs episode id?**  
A: Policy — often dedup by show for series rails.

**Q: Relation to viewport pagination?**  
A: Sibling extends `seen` across scroll pages below fold.

### 7.2 Algorithm

**Q: Why not global optimizer?**  
A: Greedy is O(n) per page, testable, good enough; ILP overkill for interview and prod at scale.

**Q: Can we allow intentional dupes?**  
A: Rare product exception flag per row; default off above-fold.

**Q: Two-pass vs one-pass?**  
A: Two-pass when pins/CW must never lose to ordering bugs.

### 7.3 Data & training

**Q: Training on drops?**  
A: Don’t treat undelivered candidates as impressions.

**Q: Score loss acceptable?**  
A: Small vs UX benefit of no dupes; monitor and tune oversample.

### 7.4 Ops

**Q: Pins vs CW conflict?**  
A: Configured precedence; validate pins at publish time.

**Q: Empty fallback?**  
A: Popular geo list always available per region.

**Q: Cache page after dedup?**  
A: Yes short TTL keyed by profile + CW version + policy version.

### 7.5 Traps

**Q: “Store seen in Redis per user forever”?**  
A: That’s suppression/history, not homepage fold dedup.

**Q: “Dedup in CDN workers”?**  
A: Personalization belongs in page service; CDN caches outputs carefully keyed.

**Q: “Dedup before entitlement filter”?**  
A: Wastes slots; may show unplayable titles.

**Q: “Global lock per title”?**  
A: Absurd; dedup is single-request local state.

### 7.6 Comparison

**Q: vs SQL DISTINCT across joins?**  
A: Doesn’t encode row priority or CW privilege.

**Q: vs ad frequency capping?**  
A: Caps are time-window counts; dedup is single-layout uniqueness.

### 7.7 Metrics

**Q: How measure success?**  
A: `duplicate_visible_rate` ~0, underfill <1%, user starts stable.

**Q: What to page on?**  
A: row_underfill spike, dup QA failures, canonical map drift.

### 7.8 Device & layout

**Q: Pixel-perfect fold?**  
A: Heuristic by device class MVP; client hint optional for sibling pagination.

**Q: Client reorders rows?**  
A: Breaks dedup assumptions; server order authoritative above-fold.

### 7.9 Internationalization

**Q: Different catalogs per country?**  
A: Filter before dedup; dedup logic unchanged.

### 7.10 Partial refresh

**Q: Only CW changed — re-run all dedup?**  
A: Surgical re-alloc downstream rows whose seen set affected; optional stability bias.

---

## 8. Appendices

### A1. Policy schema

```text
DedupPolicy {
  version: int,
  fold_rows_by_device: {phone:6, tv:4, web:7, ...},
  row_priorities: [row_template_id...],
  privileged_rows: ["continue_watching"],
  canonical_mode: TITLE | SHOW,
  min_items_default: 6,
  target_items_default: 8,
  allow_duplicate_rows: [],
  backfill_sources: ["row_fallback", "global_popular"]
}
```

### A2. Row template schema

```text
RowTemplate {
  id,
  priority: int,
  min_items,
  target_items,
  allow_duplicate: bool,
  cg_id,
  pin_slots: [{slot, title_id}]?
}
```

### A3. Dedup diagnostic event

```text
DedupDropEvent {
  request_id,
  profile_id,
  dedup_policy_version,
  row_id,
  title_id,
  canonical_id,
  winner_row_id,
  reason: CW_PRIVILEGE | PRIORITY | PIN
}
```

### A4. Launch checklist

- [ ] Golden conflict fixtures in CI  
- [ ] Undersample chaos test (force short lists)  
- [ ] Kids filter ordering test  
- [ ] Impression logging post-dedup verified  
- [ ] TV/mobile fold configs reviewed  
- [ ] Canonical alias map freshness alerts  
- [ ] row_underfill dashboard + page  

### A5. Glossary

| Term | Meaning |
|------|---------|
| Above-the-fold | First screen modules |
| Oversample | Extra candidates beyond display count |
| Privileged row | Wins conflicts (usually CW) |
| Canonical id | Title/show identity for uniqueness |
| Underfill | Row below min_items |
| Score loss | Rank penalty when title dropped |

### A6. Interviewer traps (quick)

| Trap | Pushback |
|------|----------|
| Client SoT | UX holes |
| No oversample | Empty rails |
| Dedup before filter | Wasted slots |
| Forever seen Redis | Wrong problem |
| CDN anonymous cache | Privacy leak |

### A7. Reliability test plan

1. A in three lists → one winner by priority.  
2. CW has A → others lose A.  
3. Short lists → backfill fires.  
4. Alias ids → treated same canonical.  
5. Replay same inputs → identical layout.  
6. Kids profile → no adult titles post-filter.  
7. Pin + CW conflict → policy precedence.  
8. Empty CW → page still valid.

### A8. 60-second summary

> Homepage dedup is a **server-side greedy allocator**: ranked, **oversampled** per-row candidates pass maturity filters, then a priority pass fills rails with a global `seen` set (CW privileged), backfilling to avoid empty modules — microseconds of CPU, high product value, impressions logged **after** dedup only.

### A9. Related systems map

```text
CGs/Rankers → Page Constructor (Dedup) → Client
                         ↓
                 Impression logs (post-dedup)
                         ↓
                 Training pipelines (join delivered)
Viewport pagination sibling → extends seen below fold
Suppression store → pre-filter
```

### A10. SLO sketch

| SLO | Target |
|-----|--------|
| Visible dup rate above-fold | 0 |
| Allocator p99 | < 15ms |
| Row underfill | < 1% |
| Page build p99 (dedup slice) | < 15ms |

### A11. Worked numeric example

```text
8 rows × 8 shown = 64 slots
Head-title collision heavy in top 100 catalog
Candidates 40/row → 320 ranked ids → unique pool typically ≫ 64
If only 10 candidates/row → high underfill risk when 5 rows share top-5
```

### A12. Pseudocode package

```text
allocate(rows, policy) -> Layout
validate(layout, policy) -> errors[]  # CI property test
canonical(title_id, policy) -> canonical_id
backfill(row, out, seen, policy) -> void
```

### A13. Ownership

| Concern | Owner |
|---------|-------|
| Allocator | Personalized page |
| Priorities | Product + page |
| Canonical map | Catalog |
| Metrics | Page + data |
| Fold configs | Client + product |

### A14. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Greedy server dedup + oversample |
| 10× | Device fold configs + golden tests |
| 100× | Hybrid offline pre-dedup |
| 1,000× | Edge CW merge on fragments |

### A15. JSON response snippet

```text
{
  "rows": [
    {"id":"continue_watching","items":["t_1","t_2","t_3"]},
    {"id":"top_picks","items":["t_4","t_5","t_6","t_7","t_8","t_9"]}
  ],
  "dedup_policy_version": 12,
  "fold_rows": 6
}
```

### A16. On-call cheat sheet

1. Spike in `row_underfill_rate` → check CG depth / fallback health.  
2. Dup complaints → canonical map bug? client reorder?  
3. Latency: unlikely dedup; check rank/features.  
4. Score loss spike → oversample config or priority review.

### A17. Naive comparison

| Naive | Why it fails |
|-------|--------------|
| DISTINCT in SQL join only | No CW priority |
| Client Set after render | Holes / flash |
| Random drop on conflict | Hurts relevance |
| Global title lock service | Latency / complexity |

### A18. Interaction matrix

| System | Interaction |
|--------|-------------|
| Dynamic recs | Provides candidates |
| Viewport dedup | Continues `seen` below fold |
| Ads | Separate modules |
| Suppression | Pre-filter |
| Experiments | Policy / order variants |

### A19. Cost worksheet

```text
dedup_cpu_ms ≈ titles_considered × 0.0002 ms  # negligible
marginal_cost ≈ extra rank candidates from oversample
oversample_factor 3-5x → rank QPS impact dominates
```

### A20. Explicit non-goals

- Semantic remake detection  
- Cross-session fatigue (use suppression)  
- Pixel-perfect fold ML as MVP  
- Household-shared dedup across profiles  

### A21. Stability extension spec

```text
On CW-only refresh:
  prior = previous_layout
  for row in affected_rows:
    prefer titles in prior[row] if still in candidates top 2000
  minimizes UI jump; may slightly reduce freshness
```

### A22. Sample golden fixture

```text
Input:
  cw: [A,B,C], top: [A,D,E], trend: [A,D,F]
Policy: cw priority highest
Expected:
  cw: [A,B,C], top: [D,E,...], trend: [F,...]
```

### A23. Maturity filter ordering proof sketch

Filter first → dedup operates on playable set only. Dedup first → may consume seen slots on later-filtered titles → underfill. Therefore: **filter → rank → dedup** (mandatory).

---

*End of document — Netflix system design interview prep: Homepage Above-the-Fold Deduplication.*
