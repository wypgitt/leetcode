# System Design: LeetCode Online Coding Judge

> **Focus areas:** Secure sandbox execution · Submissions · Contests · Realtime leaderboards · Idempotency · Fairness  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split submit vs execute vs leaderboard planes, explicit deal-breakers for “run untrusted code on the API box” fantasies  
> **Interview theme:** Meta L5+ reliability + scale — isolation correctness under adversarial code, contest hotspots, progressive capacity for judge fleets

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

Goal: **bound the product**—an online coding judge like LeetCode: users submit solutions, a **secure sandbox** runs them against tests, contests produce **realtime leaderboards**, and the system stays fair under cheating pressure and flash-sale-like contest spikes.

### 1.0 What this is / is not

| Dimension | **Online coding judge (this doc)** | Not this |
|-----------|------------------------------------|----------|
| Primary job | Accept code → isolate execute → judge → persist result | Full IDE product / collaborative editor deep dive |
| Success | Correct verdict; no sandbox escape; fair contests | Perfect plagiarism ML research paper |
| Execution | Untrusted user code in sandboxes | Run code in the web/API process (**deal-breaker**) |
| Contests | Timed rounds + leaderboard | Full LMS / course gradebook |
| Scale stress | Contest start spikes + viral problems | Steady blog traffic only |

**Scope statement:** Design LeetCode-class online judge: submissions, secure sandbox execution, problem bank, contests, realtime leaderboards—with progressive scale and explicit isolation invariants.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Languages? | C++/Java/Python/JS MVP; more later | Language packs + image versions |
| F2 | Verdicts? | AC, WA, TLE, MLE, RE, CE, SE | Clear state machine on submission |
| F3 | Test cases? | Sample public + hidden private | Separate sample vs judge suites |
| F4 | Run vs Submit? | “Run code” few cases; Submit full suite | Two paths; different quotas |
| F5 | Contests? | Timed; ranking by score then penalty | Contest service + leaderboard |
| F6 | Leaderboard realtime? | Yes during contest; eventual OK ±seconds | Rank store + pub/sub / WS |
| F7 | Custom test input? | Yes for Run | Sanitize size; no network |
| F8 | Discuss / solutions? | Phase 1.5 | Separate content services |
| F9 | Premium / companies? | Tags + paywall Phase 1.5 | Entitlement checks |
| F10 | Plagiarism? | Basic similarity Phase 1.5 | Async analyzer |
| F11 | Interactive / special judges? | Phase 1.5 hooks | Judge plugin interface |
| F12 | Auth? | Login required for submit | User service + rate limits |

**MVP functional scope:**

1. Problem CRUD (admin) + public problem list/detail with samples.  
2. Authenticated **Run** (custom/sample) and **Submit** (full hidden tests).  
3. Secure sandbox execution with CPU/mem/wall/file/network limits.  
4. Persist submission + per-test or aggregated verdict + runtime/memory.  
5. Contests: register, start/end window, submit only in window, score + penalty.  
6. Realtime contest leaderboard (top-N + user rank).  
7. Quotas: per-user concurrent runs, daily submit caps, contest fairness limits.  
8. Observability: queue lag, sandbox failures, escape attempt signals.

**Out of MVP:**

- Full collaborative IDE / pair programming  
- Video interviews / proctoring deep dive  
- Perfect ML plagiarism as core path  
- Mobile native offline judge  
- Multi-file project builds beyond single-file/main templates

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Isolation | No escape, no host network/FS abuse | gVisor/Firecracker/containers + seccomp |
| N2 | Submit ACK latency | Feels instant | p99 < 200–300ms to queued |
| N3 | Judge latency (easy) | Seconds | p50 < 2s, p99 < 10s suite |
| N4 | Contest fairness | Same tests; clock skew bounded | NTP; server-side contest clock |
| N5 | Leaderboard freshness | Near realtime | p99 update visibility < 2–5s |
| N6 | Durability | No lost accepted submit after ACK | Durable queue + DB write |
| N7 | Availability | Contests critical | Multi-AZ; degrade discuss, keep judge |
| N8 | Abuse | Fork bombs / crypto miners blocked | cgroup + wall time + no net |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User opens problem → Run sample → green → Submit → AC → appears in history.  
2. Contest starts → user submits → score updates → leaderboard rank rises.  
3. Compile error → CE returned quickly without running tests.  
4. TLE on test 47 → suite stops (or continues per policy) → TLE verdict.  
5. Admin publishes new problem → available in practice mode.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double-click Submit | Idempotency-Key → one submission |
| Sandbox OOM / host pressure | SE or retry on healthy node; never crash API |
| Malicious `os.system("curl...")` | Network disabled; denied |
| Fork bomb | pid/cgroup limits; kill |
| Contest submit at T+0.1s after end | Rejected by server clock |
| Judge queue backlog at contest start | Admit + show position; scale workers; priority lanes |
| Flaky floating-point | Special judge / epsilon comparator |
| Language runtime CVE | Pin images; patch fleet; kill old tags |
| Leaderboard stampede reads | Cache top-N; user rank sidecar |
| Partial suite crash mid-run | Mark SE; requeue once; alert |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| MAU | 5M | 50M | 500M | multi-B class |
| DAU | 500K | 5M | 50M | 500M |
| Peak submits/s (practice) | 200 | 2K | 20K | 200K |
| Peak submits/s (contest) | 2K | 20K | 200K | 2M |
| Avg tests / submit | 20 | 20 | 20–40 | 40 |
| Peak sandbox tasks/s | 2K | 20K | 200K | 2M |
| Concurrent sandboxes | 5K | 50K | 500K | multi-M cells |
| Problems | 3K | 5K | 10K | 20K+ |
| Active contests | 5 | 20 | 100 | 1K |
| Leaderboard reads/s (hot contest) | 10K | 100K | 1M | 10M |
| Submission rows / day | 10M | 100M | 1B | 10B |

**What each jump forces:**

- **10×:** Dedicated judge queue per language pool; Redis leaderboard; horizontal sandbox ASG.  
- **100×:** Contest-aware priority queues; shard submissions by `user_id`/`contest_id`; multi-region practice, single-home contest scoring.  
- **1,000×:** Regional judge cells; pre-warm pools before contests; leaderboard entirely edge/cache; cold submission object storage.

### 1.5 Etc. (Constraints & Assumptions)

- Untrusted code is hostile by default.  
- Hidden tests must not leak via timing side channels beyond normal verdicts (discuss openly).  
- Contests use **server time**; client clocks untrusted.  
- We are not designing the full content/community forum (hooks only).  
- Payment/premium gating is entitlement middleware, not the core design.

**Scope statement to repeat back:**

> Design a LeetCode-class online coding judge: secure sandboxed execution for Run/Submit, durable submission state, contests with score/penalty ranking, and realtime leaderboards—scaling practice and contest spikes through 10× / 100× / 1,000× with isolated judge fleets, never executing user code on request servers.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Submit API** | Create submission row + enqueue | 2K/s contest | 20K/s | API + DB |
| **Compile tasks** | Language compile | ~0.6 × submits | ×10 | Judge workers |
| **Test executions** | tests × submits | ~40K/s | ~400K/s | Sandboxes |
| **Result writes** | Verdict + metrics | ~2K/s | ~20K/s | DB/Kafka |
| **Leaderboard writes** | Score updates | ~2K/s | ~20K/s | Redis ZSET |
| **Leaderboard reads** | Poll/WS fanout | 10K/s | 100K/s | Cache/WS |
| **Problem reads** | CDN/static-ish | 50K/s | 500K/s | CDN |

**Anti-pattern:** one “QPS” mixing page views, submits, and sandbox-seconds.

### 2.2 Sandbox capacity math

```text
Assume avg suite wall time = 1.5s useful compute + scheduling
Contest peak submits/s = 2_000
Needed concurrent sandboxes ≈ 2_000 × 1.5 = 3_000
Add headroom 2× for spikes/compiles → ~6_000 slots baseline contest

10× contest: ~60_000 slots
100×: ~600_000 slots → must be multi-cell regional fleets, not one ASG
```

### 2.3 Storage math

```text
Submission metadata ~500B
Code blob avg 2KB (store object store; DB pointer)
10M submits/day → metadata 5GB/day; code 20GB/day
1,000× → 5TB metadata/day if naive → tier/archive aggressively

Test case data: 3K problems × avg 50 tests × 10KB = 1.5GB (small; cache on workers)
```

### 2.4 Leaderboard math

```text
Hot contest: 100K participants
Naive: every score update sorts full table → death
Redis ZSET: ZADD O(log N); top-100 ZREVRANGE cheap
User rank: ZREVRANK O(log N)
Read poll every 2s × 100K clients = 50K read/s → cache top-N JSON 500ms TTL + WS push
```

### 2.5 Queue backlog anti-pattern

```text
If workers = 1_000 and arrival = 5_000/s with 1.5s service:
utilization ρ = 5_000 × 1.5 / 1_000 = 7.5 → unbounded queue (DEAL-BREAKER)
Must autoscale before contest; shed Run traffic; priority for contest Submit
```

### 2.6 Network isolation cost

```text
Pulling problem tests from remote per execution adds latency & thundering herd
Cache tests on worker local SSD; version by problem_version
Image pulls at scale: pre-warm node pools with language images
```

### 2.7 Storage growth & retention (10× / 100× / 1,000×)

```text
Baseline: 10M submits/day × (500B meta + 2KB code) ≈ 25GB/day raw
Year-1 hot retention (90d): ~2.25TB code + metadata (before compression/dedup)

10×: 250GB/day → ~22TB/90d → force object lifecycle: hot 30d / warm 180d / cold glacier
100×: 2.5TB/day → ~225TB/90d → DEAL-BREAKER to keep all code in Postgres BYTEA
1,000×: 25TB/day → partition by day; content-hash dedup for identical AC templates;
         store only diffs or drop practice WA bodies after N days (policy)

Amplification: each rejudge may re-fetch code but MUST NOT duplicate blob storage
(pointer to same object_key + new execution row)
```

### 2.8 Memory footprints (workers + Redis)

```text
Per sandbox (Python microVM-ish):
  guest mem limit 256MB + Firecracker overhead ~30–50MB → budget ~320MB/slot
6_000 contest slots × 320MB ≈ 1.92TB RAM fleet (plus host OS)

Test cache per worker node:
  contest set 50 problems × 20MB suite ≈ 1GB — fits SSD; pin in page cache

Redis leaderboard:
  100K members × ~64B ≈ 6.4MB — tiny
  Hot is read QPS + WS fanout, not memory

DEAL-BREAKER: sizing fleet by “API pods” without sandbox-GB math
```

### 2.9 Partition / shard counts

```text
Kafka: partitions ≥ max(2× consumer instances, peak_submit_qps / 500)
  baseline 2K/s → 32–64 partitions; 100× → 512–1024; sticky key = submission_id
  Contest lane: dedicated topic per mega-contest OR key prefix contest_id

Postgres submissions:
  hash(user_id) % N — N=16 baseline, N=256 at 100×
  Secondary: BRIN/time index on created_at for archival sweeps

Leaderboard: one Redis key per contest_id (or sharded ZSET if >5M participants)
```

### 2.10 Amplification factors (naive cost)

| Naive approach | Amplification | Cost implication |
|----------------|---------------|------------------|
| Run all hidden tests even after first WA | × suite_len (often 40–80) wall waste | 2–5× more sandbox-seconds |
| Poll leaderboard every 1s × participants | × participants | 100K → 100K QPS origin |
| Store per-test row for every submit | × tests | 10M×50 = 500M rows/day |
| Pull language image per job | × cold start | Contest T0 meltdown |
| Judge on API host | security blast × all tenants | **Deal-breaker** |

```text
Smart defaults:
  stop-on-first-fail for WA/RE (product toggle); always full suite for AC confirmation
  top-N JSON cache 200–500ms; WS for deltas
  store aggregate metrics + first failing test only; full traces optional/sampled
```

### 2.11 Cost of wrong isolation model

```text
Shared container without seccomp/network deny:
  one escape → credential theft from judge IAM role → supply-chain incident

gVisor/Firecracker premium:
  +10–30% CPU vs bare runc — cheap vs breach

If interviewer pushes “just Docker”:
  Say: Docker ≠ security boundary; need user namespaces + seccomp + no-net +
  read-only root + dropped caps + ephemeral disk quota + separate IAM
```

### 2.12 Progressive BOTE summary card (say aloud)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak submit/s | 2K | 20K | 200K | 2M |
| Concurrent sandboxes | ~6K | ~60K | ~600K | multi-cell millions |
| Code storage/day | ~20GB | ~200GB | ~2TB | ~20TB |
| LB read origin QPS (cached) | hundreds | low thousands | edge | edge+push |
| Kafka partitions (order) | 64 | 256 | 1K | per-cell topics |

**Interview pitch:** “Capacity is sandbox-seconds and queue lag, not HTTP QPS. I size fleets from submit_rate × suite_time × headroom, isolate with microVMs, and treat leaderboards as derived Redis state rebuildable from scores.”

---

## 3. High-Level Design

### 3.1 APIs

| Op | Semantics |
|----|-----------|
| `GET /v1/problems` | List/filter problems |
| `GET /v1/problems/{id}` | Detail + samples (not hidden) |
| `POST /v1/problems/{id}/run` | Run sample/custom; returns run_id |
| `POST /v1/problems/{id}/submissions` | Submit; Idempotency-Key; returns submission_id |
| `GET /v1/submissions/{id}` | Status/verdict/metrics |
| `GET /v1/contests/{id}` | Contest metadata |
| `POST /v1/contests/{id}/register` | Register |
| `POST /v1/contests/{id}/problems/{pid}/submissions` | Contest submit |
| `GET /v1/contests/{id}/leaderboard?cursor=` | Top page + optional `user_rank` |
| `WS /v1/contests/{id}/leaderboard/stream` | Rank deltas |
| `POST /admin/problems` | Create/update problem + tests (secure) |

**Submission create body:**

```text
{
  problem_id, language, source_ref | source,
  contest_id?,
  idempotency_key,
  client_ts?  // ignored for contest eligibility
}
```

### 3.2 Data model

| Entity | Key | Notes |
|--------|-----|-------|
| User | `user_id` | auth, quotas |
| Problem | `problem_id` | metadata, difficulty, tags |
| ProblemVersion | `(problem_id, ver)` | immutable tests pointer |
| TestSuite | `suite_id` | sample vs hidden; object paths |
| Submission | `submission_id` | state machine |
| Execution | `execution_id` | sandbox attempt |
| Contest | `contest_id` | start/end, scoring rules |
| ContestReg | `(contest_id, user_id)` | registration |
| ContestScore | `(contest_id, user_id)` | score, penalty, freeze snapshot |
| Leaderboard | `contest_id` ZSET | score key encoding |

**Submission states:**

```text
CREATED → QUEUED → COMPILING → RUNNING → JUDGED
                              ↘ FAILED_SE (retriable)
JUDGED ∈ {AC, WA, TLE, MLE, RE, CE}
```

### 3.3 Scoring (contest MVP)

```text
Per problem: score if AC (partial scores optional Phase 1.5)
Penalty: minutes from start to first AC + 20× wrong submits (ICPC-like)
Rank: higher score, then lower penalty, then earlier last AC
Freeze: optional last hour hide others' details (show only own)
```

### 3.4 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Where code runs | Firecracker/gVisor microVM/sandbox fleet | Isolation | `eval` on API server |
| Queue | Kafka/SQS by language + priority | Back-pressure | Synchronous HTTP to sandbox |
| Tests storage | Object store + worker cache | Size/versioning | DB BLOBs for multi-MB cases |
| Leaderboard | Redis ZSET + cached top-N | log N updates | `ORDER BY` on MySQL every poll |
| Contest clock | Server authoritative | Fairness | Trust client timestamp |
| Idempotency | Key on create submit | Double-click | Blind insert duplicates |
| Result path | Workers write verdict; API polls/push | Scale | Long-poll held on judge node |

### 3.5 Sandbox interface

```text
ExecuteRequest {
  execution_id,
  language_image,
  source_blob,
  suite_manifest,   // list of tests + limits
  limits: {cpu_ms, wall_ms, mem_mb, pids, output_bytes},
  comparator: exact|float_eps|special_judge_ref
}

ExecuteResult {
  verdict,
  per_test: [{status, time_ms, mem_kb}] | aggregated,
  compile_log?,
  fail_test_index?
}
```

### 3.6 Security controls (MVP must-say)

1. No outbound network (or allowlist none).  
2. Read-only root; writable scratch tmpfs size-capped.  
3. seccomp/AppArmor; non-root.  
4. cgroup v2 CPU/mem/pids.  
5. Wall clock timeout > CPU time.  
6. Drop capabilities; no privileged.  
7. Fresh sandbox per execution (or aggressively reset).  
8. Secret tests never returned to client (only status).

### 3.7 Consistency model (say explicitly)

| Object | Model | Rationale |
|--------|-------|-----------|
| Submission create | Strong (primary) | Idempotency uniqueness |
| Verdict apply | Strong per `submission_id` | Monotonic JUDGED |
| ContestScore | Strong in contest home region | Fairness / last-second AC |
| Redis ZSET | Derived, eventually rebuildable | Cache of scores |
| Problem statements | Eventually consistent + CDN | Version pin in contest |
| Practice history reads | Read replica OK (seconds lag) | Not fairness-critical |

**Deal-breaker:** claiming “eventual consistency everywhere” for contest ranks during freeze window—interviewers expect a **single home writer** for scoring.

### 3.8 API edge cases (table interviewers love)

| Case | Expected behavior |
|------|-------------------|
| Duplicate `Idempotency-Key` | Same `submission_id`; no second enqueue |
| Submit after contest end | `403 CONTEST_CLOSED` (server clock) |
| Unknown language / disabled pack | `400 LANG_DISABLED` |
| Source > limit (e.g. 256KB) | `413` |
| Run with custom input huge | Reject / truncate with error |
| Get submission of another user | `403` (unless admin) |
| Leaderboard during freeze | Others’ details masked; own full |
| Rejudge mid-display | Version bump; optional freeze UX |
| Queue overloaded | `429` / `503 RETRY` with `Retry-After`; never silent drop after ACK |
| Partial WS disconnect | Client falls back to poll cached top-N |

### 3.9 Schema indexes (concrete)

```text
submissions:
  PK (submission_id)
  UNIQUE (user_id, idempotency_key) WHERE idempotency_key IS NOT NULL
  INDEX (user_id, created_at DESC)          -- history
  INDEX (contest_id, created_at)            -- contest audit
  INDEX (problem_id, verdict, created_at)   -- analytics (optional cold)

contest_scores:
  PK (contest_id, user_id)
  INDEX (contest_id, score DESC, penalty ASC, last_ac_at ASC)  -- rebuild aid

executions:
  PK (execution_id)
  UNIQUE (submission_id, attempt_no)
  INDEX (submission_id, created_at)

outbox:
  PK (id)
  INDEX (available_at) WHERE published=false
```

### 3.10 Why X over Y — expanded (Meta flavor)

| Topic | Prefer | Avoid | One-liner |
|-------|--------|-------|-----------|
| Isolation | microVM / gVisor | shared JVM `ScriptEngine` | Untrusted code = hostile |
| Job bus | Kafka + consumer groups | Redis LIST only | Need replay + lag metrics |
| Code blobs | S3/GCS | Postgres BYTEA | Growth + lifecycle |
| Rank structure | ZSET / skip list | full table sort | O(log N) update |
| Fairness clock | NTP-disciplined server | client `Date.now()` | Gaming |
| Multi-region contest | home-region write | multi-primary scores | Split-brain ranks |
| Run vs Submit lanes | separate queues | one FIFO | Practice Run starves contest |

**What to say (30s HLD pitch):**  
> “API is thin: auth, idempotent submit, enqueue. Execution plane is a priority queue into language-isolated sandbox fleets. Results land in a state machine; contest scores apply once in a home region; Redis ZSET is a rebuildable projection for top-N and rank. CDN for statements; never put hidden tests or code exec on the API tier.”

---

## 4. Architecture Diagram

```text
                     +------------------+
   Web/Mobile -----> |   API Gateway    |------> CDN (problem statements)
                     +--------+---------+
                              |
              +---------------+----------------+------------------+
              |               |                |                  |
              v               v                v                  v
      +--------------+ +-------------+ +--------------+   +--------------+
      | Problem Svc  | | Submit Svc  | | Contest Svc  |   | Leaderboard  |
      | metadata     | | idempotent  | | register     |   | API + WS     |
      +------+-------+ +------+------+ +------+-------+   +------+-------+
             |                |               |                   ^
             |                | enqueue       | score updates     |
             v                v               v                   |
      +--------------+ +-------------+ +--------------+   +------+-------+
      | Problems DB  | | Judge Queue | | Contest DB   |   | Redis ZSET   |
      | + object     | | Kafka/SQS   | | regs/scores  |   | + topN cache |
      |   tests      | +------+------+ +--------------+   +--------------+
      +--------------+        |
                              | consume
                              v
                     +--------+---------+
                     | Judge Orchestr.  |
                     | schedule/limit   |
                     +--------+---------+
                              |
              +---------------+---------------+
              |               |               |
              v               v               v
       +------------+ +------------+ +------------+
       | Sandbox    | | Sandbox    | | Sandbox    |
       | Pool Py    | | Pool C++   | | Pool JVM   |
       | microVM/   | |            | |            |
       | gVisor     | |            | |            |
       +-----+------+ +-----+------+ +-----+------+
             |              |              |
             +------+-------+------+-------+
                    v
             +------+-------+
             | Result Writer|
             | submissions  |
             | + events    |
             +------+-------+
                    |
                    +------> Object store (code, logs truncated)
                    +------> Metrics / abuse signals
```

**Practice submit path:**

```text
POST /submissions (Idempotency-Key)
  -> auth + rate limit + validate language
  -> store code blob
  -> INSERT submission QUEUED
  -> produce JudgeJob
  -> 202 {submission_id}
```

**Judge path:**

```text
Worker claims job
  -> fetch code + suite manifest (local cache hit preferred)
  -> start sandbox with limits
  -> compile (if needed)
  -> run tests until fail policy / all pass
  -> write JUDGED + metrics
  -> if contest: update score + ZADD leaderboard + publish delta
```

**Contest leaderboard read:**

```text
GET /leaderboard
  -> topN cache (300–1000ms TTL)
  -> optional ZREVRANK for me
  -> WS receives rank deltas for live UX
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **User code never runs on API/stateless app hosts.**  
2. **After submit ACK, submission durable** (DB + queue, or outbox).  
3. **Idempotency-Key** creates at most one logical submission.  
4. **Contest eligibility uses server time** only.  
5. **Hidden tests never echoed** in API responses.  
6. **Verdict monotonic** for a submission_id (no AC→WA flip without audit rejudge).  
7. **Leaderboard updates are idempotent** on `(submission_id)` apply.

#### 5.1.2 Data loss & durability

| Risk | Mitigation |
|------|------------|
| API crash after DB before enqueue | Transactional outbox / dual-write checker |
| Queue loss | Multi-AZ Kafka; acked produces |
| Worker crash mid-run | At-least-once redelivery; execution_id fence |
| DB loss | Multi-AZ primary; PITR |
| Redis leaderboard loss | Rebuild from ContestScore table |

**Deal-breaker:** fire-and-forget HTTP to a random VM without durable job record.

#### 5.1.3 Idempotency & exactly-once business

```text
Submit:
  idempotency_key + user_id → unique
  retries return same submission_id

Judge apply:
  if submission already JUDGED: ignore duplicate worker result
  contest score apply keyed by submission_id (only first AC counts for penalty rules)
```

#### 5.1.4 Retry policy

| Failure | Retry? | Notes |
|---------|--------|-------|
| CE | No | User error |
| WA/TLE/RE/MLE | No | Judged |
| Sandbox infra SE | Yes ≤2 | Different node |
| Queue timeout | Requeue | Visibility timeout |
| Comparator crash | SE + page | Special judge bug |

#### 5.1.5 Rate limiting

| Limit | Purpose |
|-------|---------|
| Concurrent runs / user | Fairness; fork abuse |
| Submits / min / user | Spam |
| Custom input size | DoS |
| Global Run QPS shed | Protect contest Submit lane |
| Per-IP + account | Bot farms |

**Contest mode:** separate queues `q.contest` > `q.practice.submit` > `q.practice.run`.

#### 5.1.6 Rejudge

Admin rejudge creates new `execution` under same or new submission policy; for contests, rejudge must be coordinated (freeze scores, recompute from log). Never silently mutate historical AC without audit trail.

#### 5.1.7 Failure modes by scale

| Scale | Dominant failure | Mitigation |
|-------|------------------|------------|
| Baseline | Worker OOM / SE spike | Auto-requeue ≤2; page on SE ratio |
| 10× | Queue lag after contest start | Pre-scale + shed Run; priority weights |
| 100× | Image pull + test cache miss storm | Pre-warm node pools; suite pin on SSD |
| 1,000× | Cross-cell clock / score split | Contest home-region single writer; read replicas only |

#### 5.1.8 Retries, backoff, poison messages

```text
Infra SE: exponential backoff 1s, 2s, 4s + jitter; max 2–3 attempts
Poison suite (special judge crash loop): circuit-open problem_version → SE + page
Do NOT retry WA/TLE/RE/CE — those are terminal user outcomes
Dead-letter: execution_id → ops console; never infinite redelivery
```

#### 5.1.9 Data-loss prevention checklist

1. ACK submit only after durable outbox row (or DB+Kafka transactional pattern).  
2. Kafka `acks=all`, min ISR; multi-AZ.  
3. Code blob upload completes **before** QUEUED (or API stores inline then async to object store with repair).  
4. Redis is never sole source of truth for scores.  
5. PITR on primary OLTP; periodic leaderboard snapshot to object store.

#### 5.1.10 Consistency under partition

```text
API ↔ DB partition: fail submit (no phantom ACK)
Worker ↔ Kafka: commit offsets after durable verdict write (or EOS sink)
Contest home region partitioned from user: queue locally? No —
  reject or buffer at edge with clear “degraded”; don’t dual-write scores
Leaderboard Redis partitioned: serve stale top-N snapshot + banner
```

**Deal-breaker:** accepting contest submits in multiple regions that each update local scores without a merge protocol.

### 5.2 Scalability

#### 5.2.1 Progressive evolution

| Jump | Architecture change |
|------|---------------------|
| Baseline | Monolith API OK; one Kafka topic; one sandbox pool; Postgres; Redis leaderboard |
| **10×** | Language pools; autoscaling; code in S3; submission DB read replicas; top-N cache |
| **100×** | Shard submissions by `user_id`; contest cells; pre-warm; WS gateway fanout; archive cold code |
| **1,000×** | Regional practice judges; contest home-region; leaderboard edge snapshots; object lifecycle tiers |

#### 5.2.2 Sandbox packing

```text
binpack microVMs on big nodes vs 1:1 VM:job
Firecracker density high; still isolate by cgroup
Pre-warm: keep N idle sandboxes per language before contest
Pull-through cache for images in each AZ
```

#### 5.2.3 Hot problem / viral spike

Viral problem causes skewed submit keys—OK because work is CPU in sandboxes, not single DB row contention—unless leaderboard or problem counters are naive.

```text
Problem ACCEPTED counter: use Redis INCR / batched flush
Avoid UPDATE problems SET ac=ac+1 row lock storm
```

#### 5.2.4 Contest start thundering herd

```text
T-10m: scale worker ASG to forecast
T-2m: pre-warm sandboxes; prime test cache for contest problems
T0: waiting room for site static; API admits submits with queue
Reads for statements: CDN only
Leaderboard: push model > poll stampede
```

#### 5.2.5 Multi-region

| Data | Strategy |
|------|----------|
| Practice problems | Replicate globally; CDN |
| Practice submits | Regional home OK |
| Contest scoring | Single home region for contest_id (strong fairness) |
| Leaderboard reads | Cache replicas worldwide; writes to home |

**Deal-breaker:** multi-writer contest scores without conflict story during last-second submits.

#### 5.2.6 Leaderboard encoding

```text
Redis score = score_points * SCORE_SCALE + (MAX_PENALTY - penalty)
Or use lexicographical member tricks carefully
ZREVRANGE 0 99 for top page
Periodic snapshot to DB for durability / freeze
```

#### 5.2.7 Hot-key handling (contest_id, problem_id)

| Hot key | Symptom | Fix |
|---------|---------|-----|
| `contest_id` score row updates | Lock contention on ContestScore | Shard score apply queue by `user_id`; row is per-user already—OK |
| `contest:{id}:lb` Redis | Single key CPU | Still OK to millions of ZADD/s; snapshot reads via local cache |
| `problem_id` AC counter | Row update storm | Redis INCR + async flush |
| Kafka partition skew | One mega-contest key | Key by `submission_id`; separate contest topic |

#### 5.2.8 Cache hierarchy

```text
L0: CDN — statements, assets
L1: API local memory — top-N JSON (200–500ms), problem metadata
L2: Redis — ZSET ranks, user_rank, rate limit tokens
L3: Postgres primary/replica — source of truth
L4: Object store — code + suites

Invalidation: problem_version bump → purge worker suite cache key
             score apply → bump top-N generation + WS delta
```

#### 5.2.9 Queue backpressure & lane evolution

| Scale | Queue design |
|-------|--------------|
| Baseline | One topic, priority header |
| 10× | Topics: `contest`, `practice.submit`, `practice.run` |
| 100× | Per-language consumer pools; admission control on Run |
| 1,000× | Per-cell Kafka; cross-cell only for global practice |

```text
Backpressure signals:
  lag_s > SLO → reject Run with 503; keep contest Submit
  sandbox_util > 0.85 → scale out; if capped, increase user concurrent limit enforcement
```

#### 5.2.10 Read/write path at 10× / 100× / 1,000×

| Path | 10× | 100× | 1,000× |
|------|-----|------|--------|
| Submit write | Outbox + Kafka | Sharded OLTP | Cell-local OLTP |
| Judge | Autoscale pool | Language cells | Regional fleets |
| Result write | Single writer svc | Partitioned appliers | Home-region contest applier |
| LB read | Redis + short cache | WS gateway + edge snapshot | Push edge boards |
| History read | Replica | User-shard query | Cold archive tier |

#### 5.2.11 Parallelization inside a suite

```text
Independent tests can run parallel in N sandboxes — careful:
  + lower wall latency for AC
  − multiplies slot usage (capacity math changes)
MVP: sequential tests; Phase 2: parallel for slow problems with slot budget
Special judge must be deterministic under parallel (no shared mutable judge state)
```

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
languages:
  python3: {image: judge-python:3.11.r42, cpu_ms: 2000, mem_mb: 256}
limits_default: {wall_factor: 2.0, pids: 64, output_mb: 1}
queues: {contest_priority: 10, practice: 5, run: 1}
idempotency_ttl_hours: 24
rejudge_enabled: true
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `submit_qps` / `run_qps` | Load split |
| `queue_lag_s` | User pain |
| `sandbox_util` | Capacity |
| `verdict_ratio` | Sudden SE spike = infra |
| `escape_deny_total` | Security |
| `leaderboard_ws_clients` | Fanout |
| `contest_submit_reject_late` | Clock/fairness |

#### 5.3.3 Testing

- Golden problems with known AC codes per language.  
- Malicious suite: network, fork, write `/`, symlink races.  
- Contest clock boundary tests.  
- Idempotent submit replay.  
- Leaderboard rebuild from scores matches Redis.

#### 5.3.4 Operability

- Canary new language image on 5% traffic.  
- Shadow-judge compare verdicts on sample.  
- Kill-switch: disable Run globally during contest meltdown.  
- Freeze leaderboard display while recomputing.

#### 5.3.5 Observability SLIs (page-worthy)

| SLI | SLO sketch | Notes |
|-----|------------|-------|
| Submit ACK latency | p99 < 200ms | Excludes judge time |
| Queue lag (contest) | p99 < 30s mid-contest | Hard UX |
| Judge wall time vs limit | ratio alerts | SE vs TLE mix |
| Verdict SE rate | < 0.1% | Infra |
| Escape deny count | anomaly page | Security |
| Leaderboard staleness | < 2s display | Derived |

#### 5.3.6 Migrations & feature flags

```text
Flags: stop_on_first_fail, parallel_tests, new_scorer_v2, freeze_enabled
Language pack rollout: dual-image shadow → compare verdict bit-exact on golden set
Schema: add columns nullable; dual-write ContestScore_v2; backfill; swap read flag
Never change penalty formula mid-contest without freeze + recompute announcement
```

#### 5.3.7 Multi-region ops

| Op | Practice | Contest |
|----|----------|---------|
| Deploy judge | Regional canary | Freeze deploys during contest window |
| Failover DB | Automated HA | Planned only; announce |
| Redis loss | Rebuild | Rebuild + freeze UX |
| Region outage | Route users | Contest home sticky; degrade others |

#### 5.3.8 Testing & replay

- Golden AC/WA corpus per language pack version.  
- Adversarial: fork bomb, `/proc` scrape, DNS, raw sockets.  
- Replay Kafka from offset for a contest → bit-identical scores (given same suite hash).  
- Load test: synthetic submit curve matching historical T0 spike.

### 5.4 Sandbox security deep dive (topic-specific)

#### 5.4.1 Threat model

| Threat | Example | Control |
|--------|---------|---------|
| Escape to host | Kernel exploit | microVM + small attack surface |
| Network exfil | Hidden test leak / crypto mine | net deny |
| Noisy neighbor | Fork/CPU | cgroup + pids |
| Timing side channel | Infer tests via time | jitter optional; don’t return per-test times for hidden on WA |
| Supply chain | Malicious pip in image | pinned images; no user-install |

#### 5.4.2 Comparator correctness

```text
exact: byte-normalized newlines
float: relative/absolute eps
special judge: runs in SAME isolation class as user (or tighter); timeout; no net
spj crash → SE, not WA (don’t punish contestant for judge bug)
```

### 5.5 Contest fairness & anti-cheat (hooks)

```text
MVP: server clock, same suite hash, rate limits, plagiarism async (AST/fingerprint)
Phase 2: IP/device clustering, paste detection, anomalous AC time distributions
Never block AC in real-time on ML suspicion without human policy — soft flag
```

### 5.6 Progressive architecture evolution (table)

| Stage | Write path | Exec path | Rank path | Isolation |
|-------|------------|-----------|-----------|-----------|
| v0 interview MVP | API→DB→Redis queue | Docker pool | SQL top-N | cgroup |
| v1 production | Outbox→Kafka | Firecracker pools | Redis ZSET | microVM |
| v2 scale | Sharded OLTP | Language cells | Cache+WS | pre-warm |
| v3 global | Regional practice | Multi-cell | Edge snapshots | supply-chain pins |

**What to say:** walk left→right; at each scale jump name the bottleneck you just removed (sync judge → queue; SQL sort → ZSET; one pool → cells).

---

## 6. Wrap-Up

### 6.1 What we designed

A **LeetCode-class online judge**: durable submissions, isolated sandbox fleets, contest scoring, and realtime leaderboards—with queues absorbing spikes and Redis/caches serving ranks—not code execution inside the API tier.

### 6.2 Memorize tradeoffs

| Topic | Stance |
|-------|--------|
| Sync vs async judge | Always async job + poll/push |
| Container vs microVM | MicroVM/gVisor preferred for hostile code |
| MySQL leaderboard | Only backup; Redis live |
| Client contest clock | Never trust |
| Exact per-test streaming to UI | Optional; aggregate OK MVP |
| Multi-region contests | Single home scoring |

### 6.3 30-second scale narrative

> Baseline: API enqueues durable judge jobs to language sandbox pools; Redis ZSET leaderboard. 10× splits pools and caches top-N. 100× adds contest priority lanes, pre-warm, sharded submission storage. 1,000× regional practice cells and home-region contests with edge-served leaderboard snapshots.

### 6.4 Deal-breakers checklist

- Running user code on the web server.  
- Synchronous request thread waiting minutes on suite.  
- Trusting client timestamps for contest end.  
- `SELECT * FROM scores ORDER BY` on every poll.  
- Returning hidden test contents on WA.  
- No cgroup/network isolation story.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Run vs Submit — why both?**  
A: Run aids debugging with samples/custom input and cheaper quotas; Submit is graded against hidden tests and counts for contests. Separating them protects judge capacity and reduces leakage pressure on hidden cases.

**Q2: Do you stop at first failure?**  
A: Often yes for speed (ICPC-style); some platforms run all for partial scoring. Product choice—state it and design comparator/score aggregator accordingly.

**Q3: How much code size limit?**  
A: e.g. 64–256KB source; prevents multi-MB paste DoS and crazy template abuse.

**Q4: Multiple files?**  
A: MVP single file / stdin-stdout; Phase 1.5 zip with allowlisted structure.

**Q5: Premium content gating?**  
A: Entitlement service check on problem get/submit; not part of sandbox.

### 7.2 Sandbox & security

**Q6: Why not Docker alone?**  
A: Docker/container escape history; for hostile multi-tenant code, gVisor or Firecracker-class isolation is the Meta-quality answer. Containers may be OK with strong additional hardening at smaller scale—be explicit about risk.

**Q7: How do you block network?**  
A: Net namespace with no interfaces / iptables drop / rootless + never configure bridge; verify with exfil tests in CI.

**Q8: Time limits: CPU vs wall?**  
A: CPU time catches busy loops; wall catches sleeps and deadlocks. Enforce both; wall ≥ CPU.

**Q9: How to prevent disk fill?**  
A: quota on writable layer/tmpfs; output byte cap; cleanup after each run.

**Q10: Side-channel leakage of hidden tests?**  
A: Timing differences can leak; mitigate with constant suite structure where feasible, rate limits, and not returning failing input. Perfect hardening is hard—discuss tradeoffs honestly.

**Q11: Special judge safety?**  
A: Special judges are also code—run them in sandbox with trusted pull only from admin artifacts, not user uploads.

### 7.3 Queues, scheduling, capacity

**Q12: Fair scheduling across users?**  
A: Per-user concurrent caps + deficit round-robin across users so one spammer cannot occupy all sandboxes.

**Q13: How to estimate worker count?**  
A: `workers ≈ arrival_rate × avg_service_time × headroom`. Contest forecasts from registrations × expected submits/user.

**Q14: Priority inversion practice vs contest?**  
A: Separate queues/pools; never let Run starve contest Submit.

**Q15: What if Kafka lags 5 minutes mid-contest?**  
A: Scale consumers; shed practice; show “system busy”; never drop AC durability—lag is UX pain, loss is integrity failure.

### 7.4 Data, indexing, storage

**Q16: Indexing for submission history?**  
A: Primary `submission_id`; secondary `(user_id, created_at DESC)`; contest `(contest_id, user_id, created_at)`. Avoid unbounded offset pagination—use cursors.

**Q17: Where is source code stored?**  
A: Object store; DB holds hash/URI. Enables lifecycle (delete code after N days for GDPR) without huge DB TOAST.

**Q18: How to store millions of tests efficiently?**  
A: Pack suite as immutable artifact (`suite_ver.tar` with manifest); workers cache by hash; don’t normalize each test as a hot SQL row on the judge path.

**Q19: Postgres vs NoSQL for submissions?**  
A: Postgres/MySQL fine with sharding at 100×; the bottleneck is usually judge CPU + contest hotspot rows, not submission inserts if IDs are random/ULID and indexes are right.

### 7.5 Leaderboards & contests

**Q20: Why Redis ZSET?**  
A: O(log N) insert/update and efficient top-K range queries. Perfect for contest ranks.

**Q21: How encode score+penalty in one float score?**  
A: Multiply score by large scale and add inverted penalty with careful bounds so ordering matches rules; or use Redis 7+ lt/gt lex patterns—explain deterministically.

**Q22: Leaderboard freeze?**  
A: At freeze time, snapshot public view; continue accepting submits into private score store; unfreeze reveals. Prevents last-hour meta-gaming from public ranks.

**Q23: Realtime via poll vs WS?**  
A: Poll simple but stampedes; WS/SSE better at 100×. Still keep top-N cached to avoid ZSET stampede from WS gateway itself.

**Q24: Rank of arbitrary user?**  
A: `ZREVRANK`; cache own rank on write path for the active user session.

### 7.6 Consistency & idempotency

**Q25: Exactly-once judge?**  
A: At-least-once execution + idempotent result commit on `submission_id` state machine. Dual AC apply must not double-count contest score.

**Q26: Outbox pattern?**  
A: Write submission + outbox row in one DB txn; publisher relays to Kafka—prevents lost jobs.

**Q27: Clock skew across judges?**  
A: Judges don’t decide contest eligibility; API does at enqueue with synced server time (TrueTime/NTP discipline).

### 7.7 Load balancing & hashing

**Q28: How to LB sandboxes?**  
A: Orchestrator assigns to pools with least-loaded / binpack; consistent hashing optional for warm caches of tests, but stickiness less important than capacity.

**Q29: Hot contest_id key?**  
A: Shard leaderboard by contest (one ZSET per contest is fine up to ~1M members). Extreme: hierarchical ranks (local shards + merger) at 1,000× mega-contests.

**Q30: Shard submissions how?**  
A: `hash(user_id) % N` for practice history; contest queries by `contest_id` may need secondary index store or contest-local shard.

### 7.8 Algorithms & fairness

**Q31: Plagiarism detection sketch?**  
A: Normalize AST/tokens; winnowing fingerprints; compare within contest cohort async; false positives need human review—don’t auto-ban in MVP.

**Q32: Anti-cheat beyond plagiarism?**  
A: Rate patterns, multi-account device signals, impossible submit intervals, IP clusters—probabilistic, appeals process.

**Q33: Floating compare?**  
A: Relative/absolute epsilon; beware catastrophic cancellation—special judges for geometry.

### 7.9 Estimation drills

**Q34: Sandboxes for 50K submits/s × 2s?**  
A: 100K concurrent; with 2× headroom 200K slots—multi-cell mandatory.

**Q35: Leaderboard read amplification?**  
A: 500K users × 1 poll/s = 500K/s; with 1s cached top-N shared, origin falls to ~1–10/s plus per-user rank cache.

**Q36: Storage 1B submissions × 2KB code?**  
A: ~2PB raw—lifecycle delete/archive; metadata only long-term.

### 7.10 Alternatives & deal-breakers

**Q37: Judge in AWS Lambda?**  
A: Tempting; cold starts, isolation/custom runtimes, and hostile code limits make dedicated sandbox fleets cleaner. Could exist for tiny trusted snippets—not full LeetCode.

**Q38: Client-side judge?**  
A: Deal-breaker for contests; OK only for toy UI demos with zero trust.

**Q39: Shared VM many tenants without isolation reset?**  
A: Cross-user contamination risk—deal-breaker.

**Q40: What’s the first sentence you’d say at Meta?**  
A: “I’ll separate control plane (submit/contest APIs) from data/execution plane (hostile sandboxes), make submits durable and idempotent, and treat contest start as a planned capacity event with a Redis-backed leaderboard.”

---

### 7.11 Extra Meta-style follow-ups

**Q41: How do you roll a Python image with a CVE?**  
A: Build `r43`; canary; pin contests to frozen images mid-round; migrate practice first; never mid-contest change semantics.

**Q42: Multi-tenant enterprise private problems?**  
A: Separate suite ACLs; dedicated judge allowlists; stronger audit logs.

**Q43: Partial scoring design?**  
A: Sum test weights; leaderboard becomes score points; penalty policy must be redefined—don’t mix ICPC assumptions silently.

**Q44: How to handle interactive problems (guess-the-number)?**  
A: Two-process sandbox with pipe between judge and user program; timeouts on each turn; Phase 1.5.

**Q45: Memory measurement accuracy?**  
A: cgroup memory.current peaks; language runtimes have baseline overhead—publish language-specific stacks.

**Q46: Can users buy capacity?**  
A: Premium concurrency quotas mapped to scheduler weights—productized fairness.

**Q47: Disaster recovery for ongoing contest?**  
A: Hot standby region with async score replica; on failure, promote with potential brief leaderboard freeze and replay from durable submit log.

**Q48: Why not store per-test rows for all submits?**  
A: 20 tests × 1B submits = 20B rows; store aggregate + failing test index; full traces sampled or on demand.

**Q49: API pagination for leaderboard near ties?**  
A: Cursor on `(rank, user_id)`; stable sort keys essential.

**Q50: What’s explicitly out of scope if time is short?**  
A: Community discussions, ML plagiarism, and fancy IDE—nail sandbox isolation, durable submit, contest leaderboard.

---

## Appendix A — End-to-end sequence (practice AC)

```text
1. Client POST /submissions {problem_id, language, source} + Idempotency-Key
2. Submit Svc: auth, quota, validate language pack
3. Put source → object store; INSERT submission(QUEUED); outbox → Kafka
4. 202 {submission_id, status: QUEUED}
5. Judge orchestrator claims job; pin problem_version + suite hash
6. Acquire sandbox slot (language pool); inject source + tests
7. Compile → if fail: JUDGED=CE; release sandbox
8. For each test: run under cgroup limits; compare output
9. First failing policy OR all pass → verdict AC/WA/TLE/MLE/RE
10. Result writer: CAS status QUEUED|RUNNING → JUDGED; persist metrics
11. Client poll/WS receives AC; user history updated
```

## Appendix B — Contest score apply pseudocode

```text
on Judged(submission):
  if not in_contest_window(server_now): return  # already validated at enqueue
  key = (contest_id, user_id, problem_id)
  if verdict != AC:
    incr_wrong(key)  # for penalty
    return
  if already_accepted(key):
    return  # idempotent; no score change
  mark_accepted(key, submission_id, server_ts)
  score = sum(accepted_problems_weights)
  penalty = minutes(first_ac - start) + 20 * wrong_before_ac
  zset_score = encode(score, penalty)
  ZADD leaderboard contest_id zset_score user_id
  publish_delta(contest_id, user_id, rank_hint)
```

## Appendix C — Sandbox deny matrix

| Attack | Control |
|--------|---------|
| Outbound exfil | No net / empty netns |
| Read `/etc/shadow` | Non-root + RO rootfs |
| Write fill disk | tmpfs quota |
| Fork bomb | pids.max |
| Infinite loop | cpu + wall timers |
| Symlink escape | New mount ns; private /tmp |
| Kernel exploit | microVM/gVisor; patch cadence |
| Timing leak tests | Limited feedback; rate limits |

## Appendix D — Capacity worksheet (fill in interview)

```text
Expected contest registrants R = ______
Expected submits/user S = ______
Avg suite time T = ______ seconds
Peak concurrency ≈ (R × S / duration_s) × T × headroom
Language mix: py___% cpp___% java___%
Pre-warm sandboxes = peak_concurrency × 0.3 (idle cushion)
Kafka partitions ≥ max parallel consumers
Redis ZSET members ≈ R
```

## Appendix E — State machine (submission)

```text
CREATED
  → QUEUED          (enqueued)
  → COMPILING       (worker started)
  → RUNNING         (tests)
  → JUDGED_*        (terminal success path)
  → SYSTEM_ERROR    (infra; requeue ≤ N)
  → CANCELED        (user/admin; rare)

Terminal judged states are immutable without audited rejudge record.
```

## Appendix F — Why not run in Lambda / Cloud Functions

| Concern | Detail |
|---------|--------|
| Isolation | Multi-tenant hostile code needs stronger than default |
| Timeouts | Suites + compiles may exceed convenience timeouts |
| Images | Custom language packs / special judges |
| Density cost | Always-on pools win for contest spikes if pre-warmed |
| Networking | Default egress often on — wrong default for judge |

Use dedicated fleets; functions only for tiny trusted snippets if ever.

## Appendix G — Leaderboard freeze UX

```text
T_freeze = contest_end - 60min (configurable)
Public board: snapshot at freeze; no others' new AC shown
Private: user still sees own submits/verdicts
Score store continues accepting applies
At unfreeze: recompute ZSET from score store; publish
```

## Appendix H — Observability red flags

| Signal | Likely cause |
|--------|--------------|
| SE ratio ↑ | Image/host pressure / test infra bug |
| Queue lag ↑ only on py | Pool undersized / image pull |
| CE spike all languages | Broken problem package |
| Leaderboard WS drop | Gateway scale / fanout |
| Dup submission_ids | Idempotency store fail |

## Appendix I — Multi-region contest home

```text
contest_id → home_region (pinned at create)
All contest submits routed to home for eligibility+score
Practice submits stay regional
Leaderboard read replicas worldwide (async)
On home failure: freeze leaderboard; promote secondary after replay
```

## Appendix J — Sample API errors

| Code | When |
|------|------|
| 401 | Unauthenticated |
| 403 | Contest not registered / problem gated |
| 409 | Idempotency conflict different body |
| 429 | Rate limit / concurrency cap |
| 503 | Judge overloaded (Retry-After) |
| 422 | Language disabled / source too large |

## Appendix K — Progressive scale checklist

| Scale | Must say |
|-------|----------|
| Baseline | Async queue + sandbox pool + Redis ZSET |
| 10× | Language pools, pre-warm, top-N cache, object code |
| 100× | Contest priority lanes, sharded submissions, WS fanout |
| 1,000× | Regional practice cells, contest home, edge leaderboard |

## Appendix L — Deal-breaker checklist (print this)

1. User code on API hosts  
2. Sync HTTP waiting on full suite  
3. Client clock for contest end  
4. SQL `ORDER BY score` every poll  
5. Returning hidden tests on WA  
6. No cgroup/network isolation  
7. Lost submit after 202 without outbox/replay  
8. Double-count AC on worker retry  

## Appendix M — Comparison: ACM ICPC vs LeetCode product

| Aspect | ICPC-like | LeetCode practice |
|--------|-----------|-------------------|
| Feedback | Often first-fail | Richer stats |
| Partial score | Rare | Common Phase 1.5 |
| Custom input | Limited | Run path |
| Plagiarism | Strict | Soft async |
| Leaderboard | Central | Per contest |

Design for both modes with policy flags.

## Appendix N — Language pack versioning

```text
language_pack {
  id: "python3",
  image: "judge-python:3.11.r42",
  compiler_cmd / runtime_cmd,
  default_limits,
  libraries_allowlist
}
Contests pin pack digests at start
Practice floats to latest after canary
```

## Appendix O — Meta interview closing

> “I’d separate the control plane from a hostile sandbox execution plane, make submissions durable and idempotent through a queue, scale language-specific judge pools ahead of contests, and serve realtime leaderboards from Redis with cached top-N—never running untrusted code on request servers.”

## Appendix P — 30-minute interview checklist

1. Clarify languages, Run vs Submit, contest scoring, leaderboard freshness.  
2. BOTE: contest submits/s × suite time ⇒ sandbox concurrency.  
3. Draw API → queue → sandbox pools → result writer → Redis ranks.  
4. Deep dive isolation + idempotent score apply.  
5. Walk 10× / 100× / 1,000× (pre-warm, cells, edge ranks).  
6. List deal-breakers.

## Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Sandbox | Isolated execution environment for untrusted code |
| Suite | Ordered tests + limits + comparator |
| Verdict | AC/WA/TLE/MLE/RE/CE/SE |
| Penalty | Contest tie-break time cost |
| ZSET | Redis sorted set for ranks |
| Outbox | DB table ensuring enqueue after commit |
| Pre-warm | Idle sandboxes ready before onsale/contest |

## Appendix R — Failure injection tests

```text
- Kill worker mid-test → requeue → single terminal verdict
- Duplicate Kafka delivery → one JUDGED
- Redis flush → rebuild leaderboard from ContestScore
- Clock jump forward → no mass late accepts (server monotonic)
- Network enable attempt inside sandbox → deny metric++
```

## Appendix S — What “fairness” means here

```text
Same problem_version + suite hash for all contestants
Server time eligibility
No preferential judge hardware classes mid-contest
Published language pack pins
Transparent freeze rules
Abuse limits applied uniformly (plus anti-cheat async)
```

## Appendix T — Anti-patterns (instant red flags)

| Anti-pattern | Why it fails | Say instead |
|--------------|--------------|-------------|
| Execute code in API process | Escape = full breach | Separate sandbox fleet |
| Sync HTTP to VM for Submit | Tail latency + no replay | Durable queue |
| Leaderboard = `ORDER BY` every poll | DB melts at contest | Redis ZSET + cache |
| Trust client contest clock | Time-travel AC | Server monotonic clock |
| Hidden tests in API response | Leak → cheat | Verdict + metrics only |
| One shared queue no priority | Run starves contest | Lane separation |
| Scores only in Redis | Rank amnesia | Rebuild from ContestScore |
| Multi-primary contest scores | Split-brain ranks | Home-region writer |
| Per-test DB rows for all | Storage blowup | Aggregate + first fail |
| “Exactly-once Kafka” as magic | Still need idempotent apply | Fence on submission_id |

## Appendix U — Interview “what to say” pitch (90 seconds)

> “We’re building an online judge: thin API with idempotent submit, durable outbox into priority queues, and Firecracker/gVisor fleets that never share fate with the API. Capacity is sandbox-seconds—submit_rate × suite_time × headroom—not HTTP QPS. Contest scoring is strongly consistent in a home region; Redis ZSET is a rebuildable leaderboard projection with cached top-N and WS deltas. At 10× we pre-warm and shed Run; at 100× we cell by language/region; at 1,000× practice is regional and mega-contests are single-home with edge- Rank snapshots. Deal-breakers: in-process eval, SQL-sorted leaderboards, client clocks, and dual-writer scores.”

## Appendix V — Numeric drill answers (memorize)

```text
2K submits/s × 1.5s = 3K concurrent; ×2 headroom = 6K slots
100K poll/2s = 50K QPS → cache top-N @ 5Hz → origin ~5–50 QPS
10M/day × 2KB = 20GB code/day; 100× = 2TB/day → object lifecycle mandatory
ZADD 20K/s on 100K ZSET — fine; problem is read amplification without cache
```

---

*End of Meta system design: LeetCode Online Coding Judge.*
