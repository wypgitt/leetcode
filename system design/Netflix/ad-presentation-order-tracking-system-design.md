# System Design: Ad Presentation Order Tracking

> **Focus areas:** Pod sequencing · No back-to-back same creative · Session state vs durable counters · Separation from frequency caps · Ad pod assembly · Short-memory eligibility  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Clear separation from cap counters, explicit session vs durable semantics, split QPS classes, Netflix Ads 2025–26 interview themes  
> **Interview theme:** Netflix Ads — track what was shown recently so the ad decision service never serves the same creative twice in a row and respects pod sequencing rules, without conflating this with frequency capping

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

Goal: **ad presentation order tracking**—the subsystem that remembers **recent presentation sequence** (within session, across pods, optionally cross-session) to enforce rules like “not the same ad twice in a row,” “brand A before brand B in pod,” and “no duplicate creatives in one pod,” **separate from** impression-count frequency caps.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Track order / recency of **served** ads for sequencing rules | Frequency caps (sibling: ad-frequency-capping) |
| Memory | Session ring buffer + optional short durable tail | Long-window N-per-day counters |
| Unit | Creative / line / brand sequence slots | Impression billing counts |
| When updated | On **ad served / pod returned** (decision time) | On viewable impression (caps) |
| Cross-device | Optional weak durable tail | Full household graph (sibling) |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What rules? | No same creative back-to-back; no duplicate in pod; max N same brand per pod | Predicate engine over sequence |
| F2 | Scope of “recent”? | Last 1–3 ads in session; sometimes last pod | Ring buffer depth K |
| F3 | Session definition? | Viewing session on profile+device until idle timeout | Session id + TTL |
| F4 | When record? | When decision **returns** pod to player (committed order) | Write on decision response |
| F5 | vs frequency cap? | Separate system; both filters apply | Two eligibility stages |
| F6 | Pod structure? | Fixed slots (pre/mid/post); 2–4 ads per mid-roll | Slot-aware sequencing |
| F7 | Partial pod fill? | Track only served slots; reorder next opportunity | Sparse sequence |
| F8 | Failed playback? | Order based on **decision**, not viewability (MVP) | Optional reconcile on skip |
| F9 | Cross-session? | “Don’t repeat last session’s final ad” — optional durable tail | Short Redis list per profile |
| F10 | Logged-out? | Device-scoped session only | Weaker cross-device |
| F11 | House ads? | Included in sequence to avoid back-to-back paid+same house pattern | Configurable |
| F12 | Ops override? | Disable sequencing for incident | Kill switch |
| F13 | A/B creative rotation? | Prefer alternate creative in pair | Sequence by creative group |
| F14 | Reporting? | Sequence violations sampled in debug | Not billing SoT |

**MVP functional scope (lock with interviewer):**

1. Maintain **session presentation log** (last K=5 creatives/brands) keyed by `(profile_id, device_id, session_id)`.
2. At decision: filter candidates violating **no back-to-back same creative** and **no duplicate in current pod**.
3. On pod commit: append ordered list to session log with TTL (session idle 30 min).
4. Optional **durable tail** (last 2 presentations per profile, 24h TTL) for cross-session back-to-back.
5. Metrics: sequence block rate, empty pod after sequence filter, session store latency.
6. Explicit **non-goals**: N-per-day caps (sibling), household union (sibling).

**Out of MVP (explicitly defer):**

- Complex narrative sequencing (“show trailer before promo”) across hours
- Client-only sequence memory as SoT
- Guaranteed global order across all devices without durable tail
- ML-based order optimization
- Rewriting already-served pod on player skip (Phase 2)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Decision read latency? | Tight slice of ad decision | p99 < 3–5ms read path |
| N2 | Write latency? | Async after response OK | Not blocking player |
| N3 | Availability | Degrade: skip sequence filter vs empty pod | Prefer skip filter with alert |
| N4 | Consistency | Session sticky to decision pod ideal | Same decision region |
| N5 | Storage | Millions of active sessions | Redis-class |
| N6 | Correctness | Occasional back-to-back under partition acceptable? | State ppm budget |
| N7 | Scale | 20K–20M decisions/s | See scale table |
| N8 | Privacy | Sequence not exposed externally | Internal keys |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Session empty → any eligible creative allowed → append on serve.  
2. Last ad creative C → filter removes C from candidates → serve D.  
3. Mid-roll pod slot 2 → exclude any creative already in slot 1 of same pod.  
4. Session idle 31 min → session key expires → fresh sequence.  
5. Durable tail says last ad was C → block C on new session first pod.  
6. Brand diversity: two Coca-Cola lines → treat as same brand group for pod rule.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Session store miss (new decision pod) | Read durable tail only; may allow back-to-back once |
| Write fails after decision returned | Next decision may duplicate; accept rare ppm |
| Only one candidate left and it violates sequence | Empty slot / house ad / shorten pod — product policy |
| User rewinds and re-triggers ad break | Same session id if within idle window |
| Profile switch mid-session | New session key; sequence resets |
| Parallel streams same profile (two devices) | Independent sessions unless durable tail enabled |
| Creative alias group (A/B variants) | Sequence on `creative_group_id` |
| Decision retry returns different pod | Idempotent append by `decision_id` |
| Hot session celebrity binge | Single Redis key; no hot shard issue (key per session) |
| Caps block all but one creative that violates sequence | Funnel deadlock → relax sequence (soft) or house ad |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak ad decisions / s | 20K | 200K | 2M | 20M |
| Active sessions | 500K | 5M | 50M | 200M |
| Session reads / s | 20K | 200K | 2M | 20M |
| Session writes / s | 20K | 200K | 2M | 20M |
| Durable tail reads / s | 5K | 50K | 500K | 5M |
| Avg sequence depth K | 5 | 8 | 10 | 10 |
| Bytes / session log | 200 | 300 | 400 | 400 |

**Split classes:** session read ≠ session write ≠ durable tail ≠ cap check (sibling).

**What each jump forces:**

- **10×:** Redis cluster; colocate order service with decision; pipeline read+filter inline.  
- **100×:** Session affinity hints; compress sequence encoding; optional edge session cache.  
- **1,000×:** Probabilistic recent-set for soft rules; exact session for hard no-duplicate-in-pod.

### 1.5 Etc. (Constraints & Assumptions)

- Server-side ad decision returns full pod manifest.  
- Sequence rules are **eligibility filters** like caps, not auction scoring.  
- **Session state** = primary; **durable counters** = optional short tail only.  
- Frequency caps use impression increments; sequence uses **decision commit**.  
- Netflix mid-roll pods: 2–4 ads typical.

**Scope statement:**

> Design presentation order tracking with session ring buffers and optional durable tail, enforcing no back-to-back and in-pod duplicate rules at ad decision time in <5ms, explicitly separate from frequency capping, scaling to 20M decisions/s.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Read rate

```text
Peak decisions = 20,000 / s
Each decision reads session log once
Session reads = 20,000 / s

Sequence check is O(K) in-memory after fetch
K=5 creatives × 16 B id ≈ 80 B payload
```

At **100×** → **2M reads/s** — Redis cluster with local L1 optional.

### 2.2 Write rate

```text
Writes ≈ decisions (one append per pod commit)
20,000 WRITES/s baseline

Each write: RPUSH + LTRIM + EXPIRE or overwrite compact blob
~1 Redis op pipeline per decision
```

### 2.3 Storage

```text
Active sessions ≈ 500K (baseline)
Bytes / session ≈ 200 B (ids + metadata)
Memory ≈ 500K × 200 B = 100 MB

At 100×: 5M × 300 B ≈ 1.5 GB + replication
TTL frees idle sessions automatically
```

### 2.4 Durable tail storage

```text
Profiles with ads ≈ 5M DAU ads tier
Tail key per profile: last 2 entries × 32 B ≈ 64 B
5M × 64 B ≈ 320 MB
TTL 24h rolling
```

### 2.5 QPS classes (split)

| Class | Baseline peak | 100× | 1,000× | Notes |
|-------|---------------|------|--------|-------|
| Session sequence read | 20K | 2M | 20M | 1 per decision |
| Session sequence write | 20K | 2M | 20M | async pipeline |
| Durable tail read | 5K | 50K | 500K | new session / miss |
| Durable tail write | 5K | 50K | 500K | on session end or each pod |
| Cap check (sibling) | 20K | 2M | 20M | separate service |

### 2.6 Latency budget

| Stage | Budget |
|-------|--------|
| Resolve session_id | <0.5ms |
| GET session log | 1–2ms |
| Evaluate predicates (K=5) | <0.5ms |
| **Order tracking read total** | **≤3–5ms p99** |
| Async write | off critical path |

### 2.7 Comparison to frequency cap read amplification

```text
Caps: 50 candidates × 3 scopes = 150 key ops (packed to ~20)
Sequence: 1 session GET + O(K) scan
Sequence is cheaper per decision when K small
Do NOT merge into cap store — different update triggers and TTL
```

### 2.8 Critical bottlenecks

1. **Extra RTT** if sequence service is remote without colocation.  
2. **Session stickiness loss** → split sequence state.  
3. **Write-after-read race** two parallel decisions same session.  
4. **Over-filtering** leaving empty pod.  
5. **Conflating with caps** → wrong increment timing.

### 2.9 Cost intuition

```text
Cheap relative to cap counters at same QPS (tiny values)
Main cost: Redis ops count at 1000×
Monitor: sequence_block_rate vs revenue impact
```

---

## 3. High-Level Design

### 3.1 Placement in ads funnel

```text
Ad request → targeting → budget/pacing → frequency caps → PRESENTATION ORDER → rank → select → return pod
                                                              ↑                      ↓
                                                      Session Order Store    async append log
```

Order filter runs **after caps**, **before** final auction/select (or integrated in candidate filter).

### 3.2 Entities

| Entity | Role |
|--------|------|
| `ViewingSession` | profile+device+session_id with idle TTL |
| `PresentationLog` | Ordered deque of last K `PresentationRecord` |
| `PresentationRecord` | creative_id, line_id, brand_id, pod_id, slot, ts, decision_id |
| `SequenceRule` | NO_BACK_TO_BACK, NO_POD_DUP, BRAND_POD_LIMIT, etc. |
| `DurableTail` | Last M presentations per profile (cross-session) |
| `CreativeGroup` | A/B variants sharing sequence slot |

### 3.3 Session vs durable

| Store | Purpose | TTL | Update trigger |
|-------|---------|-----|----------------|
| Session log | In-session back-to-back, pod dup | 30 min idle | Each pod commit |
| Durable tail | Cross-session first-ad rule | 24h | Pod commit + session end |

**Not** impression counters — no increment on viewability for MVP sequence.

### 3.4 Read API (logical)

```text
GetRecentSequence(session_key, profile_id) → SequenceView
SequenceView = { session_entries[K], durable_tail[M], version }
```

### 3.5 Filter API (logical)

```text
FilterBySequence(candidates[], sequence_view, current_pod_slots[]) → eligible[]

Rules applied:
  R1: creative_id != last.session.creative_id (NO_BACK_TO_BACK)
  R2: creative_id not in current_pod_slots (NO_POD_DUP)
  R3: brand_id count in pod < limit
  R4: creative_group not in last durable tail (optional)
```

### 3.6 Write API (logical)

```text
AppendPresentation(session_key, records[], decision_id) → OK
  idempotent on decision_id
  RPUSH + LTRIM to K
  refresh EXPIRE(session_idle_ttl)
  async update durable_tail[profile_id]
```

### 3.7 Session key design

```text
session_key = hash(profile_id, device_id, session_id)
session_id from client heartbeat or server issued on play start
```

Profile switch → new session_id from client.

### 3.8 Idempotency

```text
dedupe_key = decision_id
SETNX seq:dedupe:{decision_id} before append
prevents double append on decision retry
```

### 3.9 Empty pod policy

When filter removes all candidates:

| Policy | Use |
|--------|-----|
| Relax back-to-back (soft) | Revenue preserve |
| House ad fill | UX continuity |
| Shorten pod | Content-first product |
| Block break | Rare |

**Interview:** ask product; default relax soft sequence before empty.

### 3.10 Store choice

| Option | Pros | Cons | Choice |
|--------|------|------|--------|
| Redis LIST/STRING | Fast GET/SET, TTL | Volatile | **MVP** |
| In-decision memory | Zero RTT | Lost on restart / no affinity | L1 only |
| Postgres | Durable | Too slow | No hot path |
| Cap counter store | Already exists | Wrong semantics | **No merge** |

### 3.11 Trade-offs summary

| Topic | Decision |
|-------|----------|
| Update event | Pod commit (decision), not impression |
| Session primary | Yes; durable tail optional |
| vs caps | Separate service and keys |
| Fail policy | Degrade skip sequence filter |
| Pod deadlock | Relax soft rules |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+     +------------------+     +---------------------+
| Player |---->| Ad Decision Svc  |---->| Targeting / Caps    |
+--------+     +--------+---------+     +---------------------+
                      |
                      v
               +------+------+
               | Order Track |
               |   Service   |
               +------+------+
                  |         |
         read     |         |  async write
                  v         v
           +------+---+  +--+--------+
           | Session  |  | Durable   |
           | Log Store|  | Tail Store|
           | (Redis)  |  | (Redis)   |
           +----------+  +-----------+
```

### 4.2 Sequence: decision filter

```text
Decision→OrderSvc: GetSequence(session_key, profile)
OrderSvc→Redis: GET seq:{session_key}
OrderSvc→Redis: optional GET tail:{profile_id}
OrderSvc→Decision: SequenceView
Decision: candidates' = filter caps(candidates)
Decision: candidates'' = OrderSvc.Filter(candidates', view, pod_slots)
Decision: auction/select from candidates''
Decision→Player: pod manifest
Decision→OrderSvc: Append(decision_id, records) [async]
```

### 4.3 Sequence: idempotent append

```text
OrderSvc→Redis: SETNX dedupe:{decision_id}
  if fail → return OK
OrderSvc→Redis: GET seq:{session_key}
OrderSvc→Redis: append + trim K + EXPIRE
OrderSvc→Redis: SET tail:{profile_id} last M
```

### 4.4 Sequence: new session with durable tail

```text
session_key new → session log empty
tail:{profile} = [creative_C at T-10min]
Filter: block C for first slot (optional rule)
Serve D → append session + update tail
```

### 4.5 Sequence: interaction with caps

```text
Candidates 50 → caps → 20 → order filter → 15 → select
Both must pass; order does not read cap counts
Cap increment on impression; order append on decision
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Separate keys** from frequency cap counters.  
2. **Idempotent append** by `decision_id`.  
3. **Session TTL** refreshes on activity.  
4. **Order based on decision commit** for MVP (document if impression-based Phase 2).  
5. **Degrade** skips sequence filter on store timeout (not fail-closed unless legal pod rule — rare).  
6. **No cross-profile session bleed**.  
7. **Pod slot state** passed from decision context, not guessed.

**Failure behaviors:**

| Failure | Behavior |
|---------|----------|
| Redis read timeout | Skip sequence filter + alert |
| Redis write fail | Log; next decision may back-to-back |
| Duplicate decision_id | SETNX no-op |
| Session split across pods | Durable tail partial mitigation |
| All candidates filtered | Relax or house ad policy |

### 5.2 Scalability

| Scale | Changes |
|-------|---------|
| 1× | Redis; OrderSvc sidecar to Decision |
| 10× | Pipeline GET+filter; compact binary encoding |
| 100× | Local L1 session cache 1s TTL; shard Redis |
| 1,000× | Edge session stickiness; approximate recent-set soft rules |

**Sharding:** `hash(session_key)` for session logs; `hash(profile_id)` for tails.

### 5.3 Maintainability

- Rule config version in decision debug.  
- Metrics: `seq_check_latency`, `seq_block_rate`, `empty_pod_after_seq`, `dedupe_hit_rate`, `session_miss_rate`.  
- Shadow: log would-block without enforcing.  
- Replay tool: reconstruct sequence from decision log.

### 5.4 Exact algorithm: filter

```text
function filterSequence(candidates, view, pod_slots, rules):
  last = view.session.last()
  blocked = set()
  if rules.NO_BACK_TO_BACK and last:
    blocked.add(last.creative_id)
    blocked.add_group(last.creative_group_id)
  for s in pod_slots:
    blocked.add(s.creative_id)
  for c in candidates:
    if c.creative_id in blocked: continue
    if rules.BRAND_POD_LIMIT exceeded for c.brand_id: continue
    yield c
```

### 5.5 Exact algorithm: append

```text
function append(session_key, profile, records, decision_id):
  if not redis.setnx("dedupe:"+decision_id, ttl=1h): return
  log = redis.get(session_key) or []
  for r in records:
    log.append(r)
  log = log.take_last(K)
  redis.set(session_key, log, ex=SESSION_IDLE_TTL)
  tail = (redis.get("tail:"+profile) or []).append(records.last()).take_last(M)
  redis.set("tail:"+profile, tail, ex=24h)
```

### 5.6 Creative groups (A/B)

```text
creative_group_id shared by variants A1, A2
Back-to-back rule applies to group:
  if last.group == c.group → block
Allows alternating variants across pods
```

### 5.7 Session vs durable decision matrix

| Rule | Session only | Durable tail |
|------|--------------|--------------|
| No back-to-back in binge | ✓ | optional boost |
| No dup in pod | ✓ | n/a |
| No repeat first ad next day | | ✓ |
| Cross-device same profile | weak | ✓ partial |

### 5.8 Parallel decision race

Two ad breaks requested simultaneously (bug or UI):

```text
Mitigation: session mutex optional (expensive)
MVP: accept rare ordering glitch; idempotent per decision_id
100×: lightweight compare-and-swap on session version field
```

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Reuse cap counters for sequence | Wrong update event; window mismatch |
| Increment on impression only | Decision can't filter back-to-back |
| Client-only memory | Tampering; inconsistent |
| Global order per profile without session | Hot key + wrong semantics |
| Hard fail-closed on Redis miss | Empty pods / revenue loss |
| Unlimited K history | Memory + latency creep |

### 5.10 Progressive scale deep dive

**1×**  
Redis session keys; K=5; OrderSvc colocated; async append.

**10×**  
Binary codec for log; batch durable tail updates; dedupe TTL 1h.

**100×**  
L1 cache session GET; CAS version; session affinity on decision gateway.

**1,000×**  
Soft back-to-back via bloom recent-set; exact in-pod dup remains strict; decision log async rebuild.

### 5.11 Impression-based reconcile (Phase 2)

If player skips ad before start:

```text
Optional ImpressionEvent SKIPPED → remove last append if not viewable
Complexity: decision/impression mismatch
MVP: decision SoT; measure skip rate before Phase 2
```

### 5.12 Security

- Internal APIs only.  
- Session ids opaque; rate limit append by profile.  
- No advertiser access to sequence logs.

### 5.13 Rollout

```text
Log-only → shadow block metrics → enforce back-to-back → enforce pod dup → durable tail
Feature flag per rule type
```

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| vs frequency caps | Separate store and update event |
| Primary memory | Session ring buffer (K=5) |
| Cross-session | Optional durable tail (M=2) |
| Update trigger | Pod commit / decision_id idempotent |
| Fail policy | Skip filter on read timeout |
| Pod empty | Relax soft or house ad |

### 6.2 Risks

1. Write loss → back-to-back slip  
2. Session affinity loss → weak sequence  
3. Over-filtering with caps combined  
4. A/B group misconfiguration  
5. Durable tail stale across devices  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: sequence not caps; session vs durable |
| 5–15 | Rules: back-to-back, pod dup |
| 15–25 | APIs read/filter/append; idempotency |
| 25–35 | Storage math; why not cap store |
| 35–45 | Failures; empty pod; scale |

---

## 7. Deeper / Related Interview Questions

### 7.1 vs frequency caps

**Q: Why separate?**  
A: Caps = N impressions per window on **viewable impression**; sequence = **ordering** on **decision**. Different TTL, keys, and update events.

**Q: Can one Redis hash do both?**  
A: Anti-pattern — couples SLAs and causes increment timing bugs.

### 7.2 Session definition

**Q: How long is a session?**  
A: Idle timeout ~30 min; refreshed on append; new session on profile/device change.

**Q: Same profile two devices?**  
A: Independent session keys unless durable tail enabled.

### 7.3 Update timing

**Q: Decision or impression?**  
A: **Decision** for MVP so next break can filter; impression reconcile optional later.

### 7.4 Pod rules

**Q: Three slots same brand?**  
A: Brand pod limit rule; configurable max per pod.

**Q: House ad back-to-back with paid?**  
A: Product; often exclude house from brand limits but include in creative back-to-back.

### 7.5 Empty candidate set

**Q: All filtered out?**  
A: Relax soft sequence, house ad, or shorten pod — state tradeoff.

### 7.6 Consistency

**Q: Exactly-once sequence?**  
A: Idempotent `decision_id`; at-most-one append per decision.

### 7.7 Scale

**Q: 20M decisions/s?**  
A: Colocate read path; L1 cache; shard Redis; keep K small.

### 7.8 Cross-device

**Q: Phone then TV same show?**  
A: Session differs; durable tail helps first-ad rule only weakly.

### 7.9 Debugging

**Q: Advertiser says awkward repeat?**  
A: Sampled decision log with sequence view + rules version.

### 7.10 Traps

**Q: "Store every ad ever shown"?**  
A: That's caps / reporting — not sequence hot path.

**Q: "Use Kafka for session state"?**  
A: Too slow for synchronous filter; Kafka for audit OK.

### 7.11 ML ordering

**Q: Learn optimal order?**  
A: Out of scope; sequence is constraint filter before ranker.

### 7.12 Metrics

**Q: Page on what?**  
A: `empty_pod_after_seq` spike; read timeout rate; dedupe failure.

---

## 8. Appendices

### A1. Session log schema

```text
PresentationLog [
  { creative_id, line_item_id, brand_id, creative_group_id,
    pod_id, slot_index, ts_ms, decision_id }
  ... max K entries
]
```

### A2. Redis key layout

```text
seq:session:{session_key}     → blob log
seq:dedupe:{decision_id}      → 1 (TTL 1h)
seq:tail:{profile_id}         → last M entries blob
```

### A3. SequenceRule config

```text
SequenceRule {
  rule_id,
  type: NO_BACK_TO_BACK | NO_POD_DUP | BRAND_POD_MAX,
  scope: CREATIVE | CREATIVE_GROUP | BRAND,
  params: { max_per_pod: 2 },
  hardness: SOFT | HARD,
  version
}
```

### A4. Launch checklist

- [ ] Separate Redis namespace from fcap:*  
- [ ] decision_id idempotency tested  
- [ ] Session TTL aligned with product idle  
- [ ] Empty pod policy signed  
- [ ] Shadow metrics week completed  
- [ ] Cap + order funnel integration test  

### A5. Glossary

| Term | Meaning |
|------|---------|
| Presentation order | Time-ordered list of served ads |
| Session state | Ephemeral sequence for viewing session |
| Durable tail | Short cross-session memory |
| Back-to-back | Adjacent presentations same creative |
| Pod | Ad break with multiple slots |

### A6. Interviewer traps

| Trap | Pushback |
|------|----------|
| Same as frequency cap | Different event + window |
| Impression increment | Too late for next break |
| Unbounded history | K small |
| Strong fail-closed | Revenue / empty pod |

### A7. 60-second summary

> Presentation order tracking keeps a **small session ring buffer** (and optional **durable tail**) updated on **pod commit**, filters candidates for **no back-to-back** and **in-pod duplicate** rules in **<5ms**, stays **separate from frequency caps**, and **degrades gracefully** if store misses — never conflate impression counters with sequencing.

### A8. Related systems map

```text
Ad Decision → Order Track Service → Session Store
            → Freq Cap Service (sibling, before or after per funnel)
Impression Service → caps only (not sequence MVP)
```

### A9. SLO sketch

| SLO | Target |
|-----|--------|
| Sequence read p99 | < 5ms |
| Availability (degraded skip) | 99.95% |
| back_to_back_violation_ppm | < 50 (after enforce) |
| empty_pod_after_seq rate | < 0.1% |

### A10. Worked example

```text
Session last: creative_A
Pod slot 0: creative_B selected
Candidates for slot 1: [A, C, D]
Filter: A blocked (back-to-back + would dup pod if same)
Pick C
Append [B, C] to session
```

### A11. Binary encoding (100×)

```text
[version:1B][count:1B][entries: count × fixed 24B]
creative_id u32, brand_id u32, group_id u32, ts u32 relative
```

### A12. Ownership

| Concern | Owner |
|---------|-------|
| Order service | Ads Serving |
| Session policy | Ads Product |
| Decision log replay | Ads Infra |
| Caps (sibling) | Ads Serving |

### A13. Progressive checklist

| Scale | Must have |
|-------|-----------|
| 1× | Session GET/append + idempotency |
| 10× | Colocation + binary codec |
| 100× | L1 cache + CAS |
| 1,000× | Soft bloom tier |

### A14. Naive comparison

| Naive | Why fails |
|-------|-----------|
| Cap store last_seen field | Window != session |
| Client queue | Untrusted |
| Full impression history | Cost + latency |

### A15. On-call cheat sheet

1. Sequence read p99 up → Redis/session cluster.  
2. empty_pod spike → relax rules flag.  
3. dedupe rate anomaly → decision retry storm.  
4. Verify not cap regression (separate dashboards).

### A16. Sample debug record

```text
{
  "decision_id": "d_99",
  "session_key": "s_abc",
  "sequence_view": ["cr_1","cr_7"],
  "blocked_by_sequence": ["cr_1"],
  "selected": "cr_9"
}
```

### A17. Funnel ordering note

Recommended: `targeting → pacing → caps → sequence → rank`  
Sequence after caps reduces candidate work for order filter.

### A18. House ad interaction

House creatives may share `house_generic` group — still prevent identical back-to-back UX.

### A19. Cost worksheet

```text
redis_mem ≈ active_sessions × bytes_per_log × repl
ops_cost ≈ 2 × decisions_per_sec (read + write)
```

### A20. Explicit non-goals

- Long-horizon frequency caps  
- Household graph union  
- Guaranteed cross-device session continuity  
- Dynamic pod length optimization  

### A21. CAS session version (100×)

```text
GET seq:{key} → {version, log}
filter...
SET seq:{key} if version match else retry once
```

### A22. Audit log event

```text
SequenceAppended {
  decision_id, session_key, profile_id, entries[], rules_version
}
→ Kafka for replay / debug
```

---

*End of document — Netflix system design interview prep: Ad Presentation Order Tracking.*
