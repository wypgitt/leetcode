# System Design: Rolling-Window Frequency Caps

> **Focus areas:** Sliding time windows · Fixed vs rolling semantics · Bucketed counters · Exact vs approximate · Memory/latency trade-offs · Calendar sibling · Decision-path reads  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct window arithmetic, explicit error bounds for approximations, split QPS classes, Netflix Ads 2025–26 themes  
> **Interview theme:** Netflix Ads — enforce “max N impressions in last 24 hours” (not calendar day) at ad-decision latency

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

Goal: **bound rolling-window frequency caps**—count impressions in a sliding interval `[now - W, now]` per subject × scope, at decision time and on increment.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Rolling window count semantics + storage | Full cap platform (see ad-frequency-capping sibling) |
| Windows | Sliding 1h / 24h / 7d | Calendar midnight reset only |
| Exactness | Exact MVP; approx at 1000× for soft | Guaranteed exact without cost (impossible at scale) |
| Identity | Uses cap subject from parent | Full identity graph |

### 1.1 Functional Requirements

| # | Question to ask | Expected answer | Design implication |
|---|-----------------|---------------|--------------------|
| F1 | Window definition? | Last W seconds (e.g. 86400 for 24h rolling) | Sliding boundary math |
| F2 | Granularity? | Per impression timestamp | Event time ordering |
| F3 | Exact or approx? | Exact for hard caps; approx OK for soft at scale | Algorithm tiering |
| F4 | Check timing? | Ad decision before select | Sum/count in window ≤ N |
| F5 | Increment timing? | On viewable impression | Append to bucket or event list |
| F6 | Multiple windows? | Same scope may have 1h AND 24h rolling | Multi-window per key |
| F7 | Late events? | Beacons within grace (e.g. 5m) | TTL + reorder policy |
| F8 | Time source? | Server receive time vs player ts | Server authoritative |
| F9 | Cross-scope? | Creative/line/campaign hierarchy | Same as calendar caps |
| F10 | Comparison to calendar? | Rolling stricter for binge viewers | Different key namespace |

**MVP functional scope:**

1. Rolling windows: 1h, 24h, 7d (configurable W).
2. **Bucketed counter** exact algorithm (1-min buckets for 24h = 1440 buckets max per key — too heavy; use coarser buckets + correction).
3. Practical MVP: **fixed-size ring of time buckets** (e.g. 24 buckets × 1h for 24h window).
4. Check: `sum(buckets in window) >= N` → BLOCK.
5. Increment: add to current bucket; expire old buckets via TTL.
6. Idempotent impression apply (inherit from parent cap system).
7. Document error bound when bucket width > 1 min.

**Out of MVP:**

- Per-impression event list storage at billion-user scale
- Perfect sub-minute rolling without memory cost
- Client-computed rolling windows

### 1.2 Non-Functional Requirements

| # | Question | Target |
|---|----------|--------|
| N1 | Decision latency | p99 < 15ms added for rolling check |
| N2 | Memory per subject-scope | Bounded by bucket count × width |
| N3 | Over-cap (hard) | Minimize; exact path for hard rules |
| N4 | Under-block (approx) | Bounded false negatives for soft |
| N5 | Durability | Same as parent cap increment path |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User sees 2 ads in last 24h rolling; limit 3 → ALLOW.
2. Third impression increments → fourth decision within window → BLOCK.
3. Oldest bucket ages out → count drops → ALLOW again.
4. 1h rolling independent of 24h rolling on same creative.

**Edge cases**

| Case | Behavior |
|------|----------|
| Bucket boundary | Coarser buckets over-count slightly → conservative (safer) |
| Clock skew | Server ts only |
| Burst at bucket edge | May briefly allow +1 with coarse buckets — state bound |
| Replay old impression | Idempotency prevents double increment |
| Window W change mid-flight | New W from config version; old buckets TTL out |
| Subject travel regions | Home region buckets |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Rolling cap rules | 10K | 50K | 200K | 1M |
| Subject-scope keys | 50M | 500M | 5B | 50B+ |
| Check QPS | 20K | 200K | 2M | 20M |
| Increments/s | 5K | 50K | 500K | 5M |

**What each jump forces:**

- **10×:** Hourly buckets for 24h window (24 fields).
- **100×:** Packed multi-window hash; pipeline sum.
- **1,000×:** Count-min sketch / sliding bloom for soft; exact buckets for hard only.

### 1.5 Scope statement

> Design rolling-window frequency cap storage and evaluation: bucketed exact counters for hard caps, optional approximate structures for soft caps at scale, integrated with hierarchical scopes and idempotent impression increments.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Naive event list cost

```text
Store every impression ts per subject × scope
24h window, avg 3 imps/user/campaign → 3 timestamps × 8B = 24B
500M active keys × 24B ≈ 12 GB minimum — OK
5B keys × 24B ≈ 120 GB — painful but not impossible with TTL

Problem: decision must COUNT events in [now-W, now] → O(k) or index scan
At 2M decisions/s × 50 scopes → cannot scan lists
```

**Deal-breaker:** per-decision scan of event lists.

### 2.2 Bucketed approach

```text
24h window, 1h buckets → 24 counters per key
Value size: 24 × 2B (uint16 count) ≈ 48B + key overhead
5B keys × 64B ≈ 320 GB → Redis cluster territory at 100×+

Optimization: only store buckets for subjects with recent activity (sparse)
Working set << total subjects
```

### 2.3 Check cost

```text
Sum 24 fields in hash → O(buckets) ≈ 24 adds → <1µs CPU
Network: 1 HGETALL or HMGET pipeline per packed key
Same packing as calendar caps: fcap:{subject}:{scope}:{window_type}
```

### 2.4 Approximate sketch (1000× soft caps)

```text
Count-min sketch: d×w counters, update O(d), query O(d)
Memory ~ KB per key vs tens of bytes for buckets
Over-count possible (never under-count) → safe for cap (blocks more)
```

### 2.5 QPS split

| Class | Baseline | 100× |
|-------|----------|------|
| Rolling sum check | 400K ops/s | 40M → cache + pack |
| Bucket increment | 20K/s | 2M/s |
| Bucket rollover job | low | shard by key |

---

## 3. High-Level Design

### 3.1 Window types comparison

| Type | Key suffix | Reset |
|------|------------|-------|
| Calendar day | `day:2026-08-06` | Midnight |
| Rolling 24h | `roll:86400` + buckets | Continuous slide |
| Rolling 1h | `roll:3600` + buckets | Continuous slide |

### 3.2 Bucket indexing

```text
bucket_index = floor(unix_ts / bucket_width_sec)
bucket_width for 24h window: 3600s (1 hour) → 24 buckets cover 24h
count_in_window = sum(bucket[i] for i in current_index - 23 .. current_index)

On increment at ts:
  idx = floor(ts / bucket_width)
  HINCRBY key field=bucket:idx 1
  EXPIRE key window + grace
```

### 3.3 Error bound (coarse buckets)

```text
Worst over-count: entire bucket counted even if impression at bucket start aged out
Max error per boundary: (bucket_width / window) × N conceptual
With 1h buckets in 24h: at most ~1 extra impression counted → conservative block
Under-count (allow when should block): prevented by over-count bias
```

### 3.4 Exact sub-hour rolling (optional tier)

For 1h rolling with 1-min buckets: 60 fields — acceptable for high-value hard caps only.

### 3.5 Multi-window packed key

```text
key: fcap:{subject_id}:{scope_type}:{scope_id}
fields:
  roll_3600:b{idx} → count
  roll_86400:b{idx} → count
  day:2026-08-06 → count  (calendar sibling)
```

### 3.6 Check algorithm

```text
function rollingCount(key, window_sec, bucket_width, now):
  idx = floor(now / bucket_width)
  num_buckets = ceil(window_sec / bucket_width)
  sum = 0
  for i in 0..num_buckets-1:
    sum += HGET(key, "roll_{window}:b{idx-i}")
  return sum

function check(subject, scope, rule, now):
  cnt = rollingCount(...)
  return cnt >= rule.N ? BLOCK : ALLOW
```

### 3.7 Increment algorithm

```text
function increment(subject, scope, window_sec, bucket_width, ts):
  idx = floor(ts / bucket_width)
  field = "roll_{window_sec}:b{idx}"
  HINCRBY key field 1
  EXPIRE key window_sec + grace
  # optional: zero buckets older than window (lazy on read)
```

### 3.8 Lazy vs eager bucket expiry

| Approach | Pros | Cons |
|----------|------|------|
| Lazy (sum only recent idx) | Simple | Old fields linger until TTL |
| Eager zero on rollover | Clean memory | Extra writes |
| **MVP:** lazy sum + key TTL | Few writes | Slightly larger hashes |

### 3.9 Hard vs soft tiering

| Tier | Structure | When |
|------|-----------|------|
| Hard rolling | Bucket exact (fine width) | Brand/legal |
| Soft rolling | Coarse buckets or sketch | Advertiser preference |
| Hybrid | Hard exact + soft approx AND | Most restrictive wins |

### 3.10 Integration with parent cap service

Rolling is **one window type** in `CapRule.window.type = ROLLING`. Same CheckCaps/ApplyImpression APIs; different key field layout.

---

## 4. Architecture Diagram

### 4.1 Component view

```text
Ad Decision → Freq Cap Service
                  |
                  +→ Rule: window.type=ROLLING, W=86400
                  +→ Counter Store (Redis hash buckets)
                  +→ Optional Sketch Store (soft tier)

Impression → Increment rolling bucket fields (same key as calendar)
Reconciler → compare bucket sums vs event log sample
```

### 4.2 Sequence: rolling check

```text
CapSvc loads rule: N=3, W=86400, bucket=3600
CapSvc→Redis: HMGET fcap:sub:CAMPAIGN:k1 fields [b_t, b_t-1, ... b_t-23]
CapSvc: sum=4 → BLOCK
```

### 4.3 Sequence: increment + slide

```text
Impression ts=T
idx=floor(T/3600)
HINCRBY ... roll_86400:b{idx} 1
Next check at T+30m still sums same 24 buckets — window slid implicitly
```

---

## 5. Design Deep Dive

### 5.1 Reliability

1. Idempotent increments (parent system).
2. Hard rolling caps use conservative bucket bias (over-count OK).
3. Rebuild buckets from impression log for repair.
4. Config version pins bucket width — changing width requires new key namespace.

### 5.2 Scalability path

| Scale | Rolling strategy |
|-------|------------------|
| 1× | 1h buckets for 24h; 1min for 1h window |
| 10× | Pack scopes; pipeline HMGET |
| 100× | Separate cluster for rolling vs calendar |
| 1,000× | Sketch soft; exact hard-only subset |

### 5.3 Alternative algorithms

**A. Circular buffer in value (binary)**  
Fixed 24×uint16 serialized — fewer Redis fields, one GET.

**B. Exponential decay counters**  
Single counter with decay — approximate, smooth, not exact.

**C. Redis Cell / GCRA**  
Good for rate limit; awkward for "N imps in W" with N>1.

**D. Event log + stream processor**  
Flink tumbling → materialized view; higher latency for decision.

**Interview pick:** bucketed hash for exact hard caps; sketch for soft at scale.

### 5.4 Comparison table

| Approach | Exact | Memory | Decision latency | Over-cap risk |
|----------|-------|--------|------------------|---------------|
| Event list | Yes | High | Bad (scan) | Low |
| Hour buckets 24h | ~Yes (≤1h bias) | Medium | Good | Very low |
| Minute buckets 24h | Yes | High | Good | Low |
| Count-min sketch | No | Low | Good | Low (over-block) |
| Bloom "seen in W" | No | Very low | Best | Medium |

### 5.5 Multi-region

Buckets home with subject; same as calendar counters. Travel: read home or bounded stale replica.

### 5.6 Deal-breakers

| Trap | Why fail |
|------|----------|
| Calendar key for "rolling 24h" | Wrong semantics after binge |
| Scan all impressions at decision | Latency |
| Sub-second buckets globally | Memory explosion |
| Sketch for hard legal cap without bound | Compliance risk |
| No idempotency on increment | Double count in bucket |

### 5.6 Maintainability

- Metrics: `rolling_check_latency`, `bucket_width`, `sketch_overblock_rate`.
- Load test: verify sum pipeline at peak HMGET.
- Tooling: dump buckets for subject for support.

### 5.7 Worked example

```text
Limit: 3 impressions / rolling 24h
Buckets: 1h width
User impressions at: 10:00, 11:30, 14:00 (3 total)
Check at 15:00: sum buckets 10-14h = 3 → BLOCK
Check at 11:00 next day: bucket 10:00 day-1 aged out → sum may be 0 → ALLOW
```

### 5.8 Coupling to calendar caps

Same creative may have BOTH calendar daily AND rolling 24h. **Most restrictive wins** — evaluate all rules.

### 5.9 Progressive deep dive

**1×:** 24×1h buckets; HMGET on check.  
**10×:** Binary packed value; local cache "at cap" for rolling.  
**100×:** Dual-tier hard exact + soft sketch.  
**1,000×:** Edge prefilter "maybe under cap" bloom before HMGET.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Exact hard rolling | Time buckets (1h for 24h window) |
| Soft at scale | Count-min sketch optional |
| Check | Sum recent buckets via HMGET |
| Increment | HINCRBY current bucket |
| Error | Conservative over-count acceptable |

### 6.2 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Rolling vs calendar semantics |
| 5–15 | Bucket math + error bound |
| 15–25 | Redis schema + check/increment |
| 25–35 | Scale: sketch tier; packing |
| 35–45 | Hard cap exactness; traps |

---

## 7. Deeper / Related Interview Questions

**Q: Why not store timestamps?**  
A: Decision QPS × scan cost prohibitive; buckets trade precision for O(1) sum.

**Q: 24h rolling vs calendar day?**  
A: Rolling prevents "midnight reset binge"; stricter for heavy viewers.

**Q: Can buckets under-block?**  
A: Coarse buckets over-count (block early), not under-count — safe for caps.

**Q: Change bucket width live?**  
A: New config version + new key prefix; TTL old keys.

**Q: 7-day rolling memory?**  
A: 7×24 hourly buckets = 168 fields — heavy; use daily buckets (7 fields) with 1-day error bound or sketch.

**Q: Flink for rolling?**  
A: OK for analytics/recon; too slow for synchronous ad decision unless pre-materialized.

**Q: vs token bucket rate limiter?**  
A: Rate limiter smooths rate; cap counts discrete impressions in window — different semantics.

---

## 8. Appendices

### A1. Bucket field naming

```text
roll_{window_sec}:b{bucket_index}
Example: roll_86400:b292019  # bucket index = floor(ts/3600)
```

### A2. Rule extension

```text
CapRule.window {
  type: ROLLING,
  length_sec: 86400,
  bucket_width_sec: 3600,
  tier: EXACT|APPROX
}
```

### A3. Sketch parameters (soft)

```text
CMS: width=2048, depth=4 → ~0.1% over-count typical
Update on increment; query for check
If sketch_count >= N → BLOCK (may over-block)
```

### A4. Rebuild from log

```text
For each impression in [now-W, now]:
  increment bucket at impression ts (idempotent)
Compare sum to live Redis — repair drift
```

### A5. Glossary

| Term | Meaning |
|------|---------|
| Rolling window | Sliding interval ending at now |
| Bucket | Fixed time slice aggregating counts |
| Conservative bias | Over-count acceptable for caps |
| CMS | Count-min sketch |

### A6. Interviewer traps

| Trap | Answer |
|------|--------|
| Use calendar for "last 24h" | Wrong product semantics |
| Per-impression list at decision | Latency |
| Sketch for hard legal | Need bounds + policy |
| Ignore hierarchy | Category caps still apply |

### A7. 60-second summary

> Rolling caps need **sliding window counts** without scanning events. Use **fixed-width time buckets** in a Redis hash: **increment current bucket**, **sum last K buckets** on check. Coarse buckets **over-count slightly** (safe). At **1000×**, add **sketches for soft caps**; keep **exact buckets for hard caps**.

### A8. SLO

| Metric | Target |
|--------|--------|
| Rolling check p99 | < 12ms |
| Hard cap over-block from buckets | ≤ 1 impression equivalent |
| Rebuild drift | < 0.01% keys |

### A9. Test plan

1. Three imps in 24h → fourth blocked.
2. Imp ages out of window → allowed.
3. Duplicate impression_id → one bucket increment.
4. Compare bucket sum vs brute-force log count on sample.
5. Config bucket width change → new namespace.

### A10. Related docs

- ad-frequency-capping-system-design.md (parent)
- cross-device-frequency-enforcement-system-design.md
- ad-presentation-order-tracking-system-design.md

### A11. Numeric bucket sizing guide

| Window | Bucket width | # buckets | Max over-count bias |
|--------|--------------|-----------|---------------------|
| 1h | 1 min | 60 | 1 imp |
| 24h | 1 hour | 24 | 1 imp |
| 7d | 1 day | 7 | 1 imp |
| 30d | 1 day | 30 | 1 imp |

### A12. Packed binary value layout

```text
[version:1B][num_buckets:2B][bucket0:2B]...[bucketN:2B]
Single GET; parse in CapSvc — reduces Redis field count
```

### A13. Ownership

Rolling window logic owned by Ads Serving / Freq Cap team; shared Counter Store with calendar caps.

### A14. Launch checklist

- [ ] Bucket width documented per rule class
- [ ] Hard vs soft tier assignment
- [ ] HMGET pipeline load test
- [ ] Rebuild job validated
- [ ] Calendar + rolling interaction tested

### A15. Explicit non-goals

- Sub-second rolling precision globally
- Replacing parent cap idempotency layer
- Client-side rolling computation

### A16. On-call notes

If over-block complaints: check bucket width too coarse for product expectation.  
If over-show: verify rolling rules actually applied (not calendar keys by mistake).

### A17. Sample bucket dump

```text
key: fcap:p_123:CAMPAIGN:k_9
roll_86400:b292018 = 1
roll_86400:b292019 = 2
roll_86400:b292020 = 0
sum(last 24) = 3 → at limit 3 → BLOCK
```

### A18. Comparison to Redis TTL key per hour

Alternative: separate key per bucket `fcap:...:h292019` with TTL 86400 — more keys, simpler expiry, worse packing.

### A19. Flink materialized rolling (async path)

```text
Impression stream → tumbling 1h → sink to KV store
Decision reads materialized sum — 1–5 min lag
Use for reporting or soft caps only, not hard sync path
```

### A20. Interview one-liner

> "Rolling = sum of the last K bucket counters; increment O(1), check O(K) with small K; coarse buckets are conservatively biased; sketches only when you accept over-blocking for soft caps."

### A21. Progressive scale checklist (detailed)

| Scale | Rolling-specific requirements |
|-------|------------------------------|
| 1× | Single bucket width per window class; HMGET in pipeline |
| 10× | Binary packed values; negative cache for at-cap rolling keys |
| 100× | Dedicated Redis cluster shard for rolling fields |
| 1,000× | CMS tier for soft; exact only for hard-cap rule IDs |

### A22. Memory estimation worksheet

```text
fields_per_key = ceil(window_sec / bucket_width_sec)
bytes_per_key ≈ 32 (key) + fields × 4 (field+count) + overhead
active_rolling_keys = subjects_with_impression_in_last_window × scopes
Example: 200M keys × (32 + 24×4) ≈ 25 GB raw × 3 repl ≈ 75 GB at baseline
Sketch tier: 200M × 2KB ≈ 400 GB — use only for soft subset
```

### A23. Decision cache interaction

```text
If rolling sum >= N-1 (near cap):
  cache BLOCK for (subject, scope, window) TTL 30-60s
Reduces HMGET for repeat decisions same session
Invalidate cache on increment for that scope
Risk: brief over-show if increment delayed — bound with near-cap home read
```

### A24. Config migration playbook

```text
1. Publish new CapRule version with new bucket_width
2. New Redis field prefix roll86400_v2:
3. Dual-read during migration window (max of both sums) — conservative
4. Stop writing old prefix; TTL expire old keys
5. Recon sample compares v1 vs v2 sums vs event log
```

### A25. Extended interview Q&A bank

**Q: User watches 6 hours straight — rolling 24h behavior?**  
A: All impressions fall in recent buckets; sum rises monotonically until cap; no midnight reset relief.

**Q: Pause 25 hours — rolling behavior?**  
A: All buckets aged out; count 0; fresh allowance.

**Q: Two devices same profile?**  
A: Same subject_id → shared buckets (parent identity model).

**Q: Impression counted in bucket by event time or processing time?**  
A: Server event time; processing delay may shift bucket by 1 — document grace.

**Q: How validate bucket logic in prod?**  
A: Shadow compute brute-force from sampled event log vs bucket sum; alert drift.

**Q: Window W=86400 but bucket=7200 (2h)?**  
A: 12 buckets; max 2h over-count bias; discuss with interviewer.

**Q: Rolling cap N=1?**  
A: Degenerate to "no repeat within W" — same machinery, stricter UX.

**Q: Integration tests?**  
A: Time-travel tests with injected ts; property test sum(buckets) monotonic with imps.

### A26. Failure mode matrix (extended)

| Failure | Symptom | Mitigation |
|---------|---------|------------|
| Wrong bucket index math | Systematic under-block | Unit tests; canary rules |
| HMGET timeout | Fail-closed hard / open soft | Parent cap policy |
| Partial HINCRBY | Drift vs log | Reconciler; multi-field TX |
| Key TTL too short | Premature allow | TTL = W + grace + max_delay |
| Config version mismatch | Wrong W | Stamp version on decision |

### A27. Observability dashboard panels

1. Rolling check latency histogram by window length  
2. Distribution of bucket sums at BLOCK boundary  
3. Sketch vs exact delta (soft tier)  
4. Keys with field count > expected ( leak detection )  
5. Rebuild drift ppm  

### A28. Cross-team API contract

```text
CheckCaps(subject, candidates, now) — parent owns
RollingEvaluator.sum(key, rule, now) → int — internal module
ApplyImpression(...) — increments rolling fields per rule set
No separate public API for rolling alone in MVP
```

### A29. Historical context (interview color)

Web display ads popularized cookie-based rolling caps; CTV/streaming requires server-side profile buckets. Netflix Ads interviews often probe **calendar vs rolling** because binge viewing breaks calendar fairness.

### A30. Explicit guarantees statement

```text
HARD rolling caps (bucket exact tier):
  Guaranteed: count never UNDER-estimated for blocking (conservative bias)
  Not guaranteed: zero over-show under async increment race (see parent PPM budget)

SOFT rolling caps (sketch tier):
  Guaranteed: over-block only (sketch over-count)
  Not guaranteed: exact N enforcement
```

### A31. Worked numeric example (24h rolling, 1h buckets)

```text
N=5 impressions / rolling 24h
Buckets: 24 fields hour_0..hour_23 (or absolute epoch hours)
Now = hour 100; sum fields hour_77..hour_100 (last 24)
If sum≥5 → BLOCK
On impression at hour 100: HINCRBY field hour_100
Expired fields outside window ignored (or TTLd away)
```

### A32. Relation to parent frequency-capping doc

This file deep-dives **window mechanics**. Parent doc owns funnel placement, hard/soft fail policy, hierarchy scopes, and identity. Interviews may ask only rolling — still mention where CheckCaps sits.

### A33. 60-second summary

> Rolling caps use **time buckets** (exact) or **sketches** (soft/approx): decision sums last W buckets, impressions increment the current bucket, TTLs expire old fields — stricter fairness than calendar midnights for binge streaming, at higher storage/CPU cost.

---

*End of document — Netflix system design interview prep: Rolling-Window Frequency Caps.*
