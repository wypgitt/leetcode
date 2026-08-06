# System Design: Distributed Task Scheduler

> **Focus areas:** Cron-like schedules · Exactly-once execution *attempts* · Leases · Sharding · Delayed jobs · Retries · DLQ  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct lease/fencing semantics, honest exactly-once vs at-least-once, shard rebalancing, delayed-wheel math, idempotent handlers  
> **Interview theme:** Google L5+ control-plane infrastructure — durable scheduling of millions of jobs without double-run disasters

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

Goal: **bound the product**—a **distributed task scheduler** (cron + one-shot delayed jobs): register schedules, fire due work across a worker fleet with **leases**, survive coordinator failures, support **retries** and **DLQ**, and scale via **sharding**—with precise language about exactly-once.

### 1.0 What this is / is not

| Dimension | **Distributed task scheduler (this doc)** | Not this |
|-----------|-------------------------------------------|----------|
| Primary job | Trigger due tasks reliably at scale | General streaming Flink SQL platform |
| Success | Due work executed; bounded duplicates; operable | Perfect theoretical exactly-once without idempotency |
| Schedules | Cron expressions + one-shot `run_at` | Human calendar UI (see Calendar doc) |
| Execution | Dispatch to workers / queues | In-process `setTimeout` only |
| State | Durable schedules + run history | Best-effort ephemeral timers |

**Scope statement:** Design a distributed task scheduler with cron/delayed jobs, leased execution attempts, sharding, retries, and DLQ—scaling through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Job types? | Cron periodic + one-shot delayed | Two schedule kinds; same dispatcher |
| F2 | Payload? | Opaque bytes/JSON + HTTP/queue target | Worker adapters |
| F3 | Exactly-once? | Exactly-once *attempts* with fencing; handlers idempotent | Lease + attempt_id |
| F4 | Timezone cron? | Yes — cron in TZ | Store TZ; expand in UTC |
| F5 | Catch-up? | Missed runs: skip or backlog policy | Per-job policy |
| F6 | Retries? | Exponential backoff + max attempts | Retry state machine |
| F7 | DLQ? | Yes after max fail | DLQ topic/table + alert |
| F8 | Priority? | Optional queues | Fairness / QoS |
| F9 | Admin? | Pause, trigger-now, inspect runs | Control APIs |
| F10 | Fanout? | One schedule → many shards of work optional | Parent/child jobs |
| F11 | Dedup? | Client `dedupe_key` for one-shots | Unique constraint |
| F12 | Observability? | Lag, success rate, long runners | Metrics + run log |

**MVP functional scope:**

1. Create/update/delete cron schedules and one-shot delayed tasks.  
2. Dispatcher finds due tasks, grants **leases** to workers.  
3. Workers heartbeat lease; complete/fail with terminal states.  
4. Retries with backoff; DLQ after exhaustion.  
5. Shard schedules across dispatcher set; rebalance on membership change.  
6. At-least-once delivery of execution attempts; **fencing tokens** prevent stale workers.  
7. Run history / attempt log.  
8. Pause/resume; manual run.  
9. Per-job concurrency limit (e.g. forbid overlap).

**Out of MVP:**

- Full DAG workflow engine (Airflow/Temporal deep) — mention as Layer 2  
- ML autoscaling of workers beyond simple queue depth  
- Exactly-once side effects without handler idempotency (impossible in general)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Fire accuracy | Near schedule time | p99 lag < 1–5s typical; configurable |
| N2 | Durability | No silent lost schedules | Multi-AZ store |
| N3 | Availability | Dispatch continues on node loss | 99.9%+; lease takeover |
| N4 | Duplicate attempts | Bounded | Fencing; handler idempotent |
| N5 | Throughput | High due QPS | Shard + batch claim |
| N6 | Operability | Safe deploys | Draining, pause flags |
| N7 | Multi-tenant | Noise isolation | Quotas per tenant |
| N8 | Clock | Bounded skew | NTP; lease timeouts >> skew |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Register cron `0 * * * *` → each hour a run attempt → worker succeeds → next fire computed.  
2. One-shot `run_at = now+15m` → becomes due → executes once.  
3. Worker fails mid-job → lease expires → retry attempt with new fencing token.  
4. Handler returns 500 × N → backoff → DLQ → alert.  
5. Dispatcher node dies → shard reassigned → due jobs continue.  
6. Pause job → no new attempts; in-flight finish or cancel per policy.  
7. Manual “run now” → ad-hoc attempt without shifting cron base (policy).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Split brain two dispatchers | Membership + shard locks; only owner claims |
| Stale worker after lease loss | Fencing token rejected on complete |
| Clock jump forward | Due storm; rate limit claims; spill |
| Clock jump backward | Avoid double schedule via last_fire watermark |
| Thundering herd on :00 | Jitter; shard by time+id |
| Long-running job > lease | Heartbeats extend lease |
| Overlapping cron still running | `concurrency=1` skip or queue |
| Poison message | Max attempts → DLQ; don’t infinite retry |
| Hot tenant | Per-tenant claim quotas |
| DST cron | TZ-aware library; document skip/ambiguous |
| Kafka/worker outage | Tasks stay leased/due; backlog visible |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active schedules | 1M | 10M | 100M | 1B |
| Due fires/s peak | 5K | 50K | 500K | 5M |
| Workers | 100 | 1K | 10K | 100K |
| One-shots created/s | 2K | 20K | 200K | 2M |
| Avg attempts / success | 1.1 | 1.1 | 1.2 | 1.2 |
| Dispatchers | 3–9 | 30 | 100+ cells | cell fabric |
| Run history retain | 7–30d | same | tiered | tiered |
| Tenants | 100 | 1K | 10K | 100K |

**What each jump forces:**

- **10×:** Shard by `schedule_id`; batch lease claims; time-bucket indexes.  
- **100×:** Hierarchical wheels / bucket scanners; per-tenant fairness; cell isolation.  
- **1,000×:** Regional cells; near-due pull to memory wheels; separate control vs data planes.

### 1.5 Etc. (Constraints & Assumptions)

- Worker side effects must be **idempotent** or transactional with `attempt_id`.  
- “Exactly-once execution” in distributed systems usually means **exactly-once successful business effect** via idempotency; the scheduler provides **at-most-one active lease** + **exactly-once attempt IDs**.  
- Cron calendar expansion uses a tested library.  
- Storage: Postgres/Spanner/etc. with transactions for claim.

**Scope statement to repeat back:**

> Design a sharded distributed scheduler for cron and delayed jobs where dispatchers claim due work with leases and fencing tokens, workers heartbeat and complete idempotently, failures retry with backoff into a DLQ, and scale proceeds via time-bucket indexes and cell isolation.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **Schedule writes** | CRUD schedules | low–med | Control API |
| **Due scans / claims** | Dispatcher | 5K fires/s | Meta store |
| **Lease heartbeats** | Workers | fires × hb rate | Meta store |
| **Execution** | Worker invoke | 5K/s | Worker fleet |
| **Run log writes** | Attempts | ~6K/s | History store |
| **Retry re-arm** | Failures | ~0.5K/s | Scheduler |

**Anti-pattern:** one “QPS” mixing cron expand, HTTP worker calls, and SQL scans.

### 2.2 Naive scan failure

```text
1M schedules; poll every 1s WHERE next_fire_at <= now()
→ massive table scans / index contention at :00

Need: time-bucketed due index + shard-local scanners
  e.g. secondary index (shard, next_fire_at)
  or bucket tables per minute
```

### 2.3 :00 thundering herd

```text
Many crons at minute 0 → 10× average due rate
Mitigations: deterministic jitter (hash-based seconds), staggered cron, claim rate limits
```

### 2.4 Lease math

```text
lease_ttl = 30s; heartbeat every 10s
detector lag ≈ lease_ttl + scanner period
If worker GC pause > lease_ttl without HB → duplicate attempt risk → fencing saves correctness
```

### 2.5 Storage

```text
Schedule row ~ 500 B → 1M × 500 B = 500 MB
Attempt history 5K/s × 300 B × 86400 ≈ 130 GB/day → retain short hot; cold archive
```

### 2.6 Memory wheel (100×+)

```text
Hold next 1–5 minutes of due jobs in memory per shard
5K/s × 300s = 1.5M entries × 128 B ≈ 192 MB / cell slice — feasible
```

---

## 3. High-Level Design

### 3.1 API

| Op | Semantics |
|----|-----------|
| `POST /v1/schedules` | Create cron or one-shot |
| `PATCH /v1/schedules/{id}` | Update / pause |
| `DELETE /v1/schedules/{id}` | Delete |
| `POST /v1/schedules/{id}:run` | Force run |
| `GET /v1/schedules/{id}/runs` | History |
| `POST /internal/claim` | Dispatcher→worker batch (or pull queue) |
| `POST /internal/heartbeat` | Extend lease |
| `POST /internal/complete` | Success / fail + fencing |

**Schedule schema:**

```text
Schedule {
  schedule_id, tenant_id,
  type: cron | once,
  cron_expr?, tz?,
  run_at?,                // once
  payload_ref, target,    // HTTP, Pub/Sub, queue
  next_fire_at,
  last_fire_at,
  state: active|paused|deleted,
  policy: {
    retry_max, backoff, ttl,
    concurrency, catch_up: skip|all|bounded,
    jitter_ms
  },
  dedupe_key?, version
}
```

**Attempt schema:**

```text
Attempt {
  attempt_id, schedule_id, scheduled_fire_at,
  fencing_token, lease_owner, lease_until,
  status: leased|running|succeeded|failed|dlq,
  try_n, error?, started_at, finished_at
}
```

### 3.2 Core state machine

```text
Schedule.active → (due) → create Attempt(leased)
  → worker running → succeeded → compute next_fire (cron) or terminal (once)
                  → failed → if tries left: re-arm next_fire=now+backoff
                             else: DLQ; cron may still advance per policy
Lease expired → new Attempt with fencing_token+1 (or new attempt_id)
```

### 3.3 Leases & fencing — Why X over Y

| Approach | Pros | Cons | When |
|----------|------|------|------|
| **DB lease row** | Simple transactional claim | DB load | MVP strong |
| **Queue ack visibility** | Natural | Harder cron state | Once jobs |
| **ZooKeeper/etcd lock** | Clear | Ops; not for millions locks | Coarse shard locks |
| **Fencing token** | Stops stale complete | Handler must check | **Always with leases** |

**Claim transaction (sketch):**

```text
BEGIN
  SELECT id FROM schedules
  WHERE shard=? AND state=active AND next_fire_at<=now()
  ORDER BY next_fire_at LIMIT N
  FOR UPDATE SKIP LOCKED

  INSERT attempts(... fencing_token=version ...)
  UPDATE schedules SET next_fire_at=compute_or_far_future,
                      version=version+1
COMMIT
```

Worker must send `attempt_id + fencing_token` on complete; mismatch → reject.

### 3.4 Sharding

```text
shard = hash(schedule_id) % N
OR shard = hash(tenant_id, schedule_id) for locality

Dispatchers: consistent hash / etcd membership assigns shard ranges
Only shard owner runs due scanner for that shard
```

Rebalance: drain — stop claiming; wait lease expiry or transfer carefully; start on new owner.

### 3.5 Delayed jobs & time indexes

| Structure | Role |
|-----------|------|
| `next_fire_at` index per shard | Due poll |
| Time buckets (per minute) | Reduce hot range |
| Hierarchical timing wheel | In-memory near-due |
| External delay queue | Optional for pure one-shots |

**Cron expand:** after success, `next_fire_at = next_cron(after last_scheduled, tz)`.

### 3.6 Retries & DLQ

```text
backoff = min(max_backoff, base * 2^try_n) + jitter
if try_n >= retry_max:
  status=dlq; emit alert; stop retry
else:
  enqueue attempt at now+backoff
```

DLQ contents: payload snapshot + error + attempt history link. Replay API requeues.

### 3.7 Execution adapters

| Target | Pros | Cons |
|--------|------|------|
| HTTP callback | Simple tenants | Timeouts; auth |
| Pub/Sub / Kafka | Decouple | Extra hop |
| Inline worker pool | Low latency | Multi-tenant isolation harder |

**MVP:** claim → internal queue → sandboxed workers → HTTP/queue adapter.

### 3.8 Why X over Y (summary)

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Due scan | Shard + SKIP LOCKED | Scale claims | Global `SELECT due` no shard |
| Correctness | Lease + fencing + idempotent handler | Real-world | “DB unique ⇒ exactly-once side effects” |
| Cron store | next_fire watermark | O(1) due | Re-evaluate all cron strings every tick |
| Delayed | same next_fire index | Unified | Separate fragile timer process only |
| Overlap | concurrency policy | Predictable | Silent parallel doubles |

---

## 4. Architecture Diagram

```text
  Admin / Tenant API
          |
          v
  +-------+--------+         +------------------+
  | Schedule API   |-------->| Schedule Store   |
  +-------+--------+         | (sharded)        |
          |                  +--------+---------+
          |                           ^
          v                           | claim / complete
  +-------+--------+         +--------+---------+
  | Membership     |         | Dispatchers      |
  | (etcd/ZK)      |-------->| shard owners     |
  +----------------+         +--------+---------+
                                      |
                                      | push/pull jobs
                                      v
                             +--------+---------+
                             | Worker Fleet     |
                             | lease + heartbeat|
                             +--+-----------+---+
                                |           |
                                v           v
                           Adapters      Run History
                           (HTTP/Q)      + Metrics
                                |
                                v
                              DLQ <--- max retries
```

**Due dispatch path:**

```text
Dispatcher loop (per owned shard):
  due = claim_batch(shard, limit, now)
  for job in due:
    enqueue worker(job.attempt_id, fencing_token, payload)
```

**Worker path:**

```text
receive attempt
  heartbeat loop until done
  execute adapter (idempotent with attempt_id)
  complete(success|fail, fencing_token)
```

**Retry path:**

```text
complete(fail)
  if retries left: set next_fire_at = now+backoff (or insert delay row)
  else: write DLQ; mark schedule error state / continue cron per policy
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Durable schedule** before ACK create.  
2. **At most one owning dispatcher** per shard (membership).  
3. **At most one live lease** per active attempt; complete requires fencing token.  
4. **next_fire_at watermark** prevents double-scheduling same cron tick.  
5. **Idempotent handlers** keyed by `attempt_id` or `(schedule_id, scheduled_fire_at)`.  
6. **DLQ is terminal** for that attempt chain until explicit replay.  
7. **Lease expiry ⇒ recoverable** — system must progress.

#### 5.1.2 Exactly-once vocabulary (interview gold)

| Phrase | Meaning |
|--------|---------|
| Exactly-once attempt record | One attempt_id committed for a fire |
| At-most-one active lease | Fencing / lease ownership |
| At-least-once delivery to worker | Retries on uncertainty |
| Exactly-once **effect** | Only if side effect store dedupes attempt_id |

**Deal-breaker:** promising “exactly-once end-to-end” without idempotency keys in the handler/storage.

#### 5.1.3 Lost complete / uncertain result

```text
Worker executed side effect but died before complete RPC
  → lease expires → retry → handler must no-op on same idempotency key
```

#### 5.1.4 Catch-up policies

| Policy | Behavior |
|--------|----------|
| `skip` | Fire once for latest; skip missed |
| `bounded(n)` | Run up to n missed |
| `all` | Dangerous backlog — quota |

Default for most crons: `skip` or `bounded(1)`.

#### 5.1.5 Clock skew

- Synchronize NTP.  
- Lease TTL ≫ max skew.  
- Use storage `now()` for due comparisons when possible.  
- TrueTime-style intervals optional in Spanner world.

### 5.2 Scalability

#### 5.2.1 Claim throughput

```text
Batch claim N=100–500 with SKIP LOCKED
Parallel dispatchers on different shards
Avoid hot shard: hash well; split heavy tenants
```

#### 5.2.2 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | More shards; batching; index `(shard, next_fire_at)` |
| 100× | Near-due memory wheels; tenant fairness; history tiering |
| 1,000× | Cells by region/tenant; push due into per-cell Redis ZSET + durable log |

#### 5.2.3 Hot keys / noisy neighbors

- Per-tenant max claims/s.  
- Separate high-rate one-shot path (pure delay queue).  
- Coalesce fanout schedules (one cron generates child jobs in chunks).

#### 5.2.4 Dispatcher HA

```text
etcd election / consistent hash ring
On owner change:
  1) old owner stops
  2) wait | or fence epoch++ on shard
  3) new owner scans with new epoch
Attempts include shard_epoch to reject stale dispatchers
```

### 5.3 Maintainability

- Version payloads; adapter contracts.  
- Migration: dual-read schedule schema.  
- Chaos: kill dispatcher; kill worker mid-lease; delay KMS/network.  
- SLO dashboards: schedule lag, claim errors, DLQ rate, lease expirations.  
- Safe deploy: rolling workers; dispatchers drain shards.

### 5.4 Security & multi-tenancy

- AuthN on control API; tenants isolated.  
- Worker credentials to invoke tenant HTTP — **egress allowlists**.  
- No SSRF: block link-local/metadata.  
- Signed task payloads / HMAC between dispatcher and workers.  
- Secrets in payload refs not inline.

### 5.5 Comparison: scheduler vs workflow engine

| | Scheduler (this) | Temporal/Airflow |
|--|------------------|------------------|
| Unit | Fire task | Long workflow |
| State | next_fire + attempts | Workflow history |
| Use | Cron, reminders, delays | Sagas, human tasks |

Position this design as **Layer 1 firing**; workflows can sit above.

---

## 6. Wrap-Up

### 6.1 Design summary

A distributed task scheduler is a **durable schedule store** with **`next_fire_at` watermarks**, **sharded dispatchers** that **transactionally claim** due work into **leased attempts** with **fencing tokens**, a **worker fleet** with heartbeats, and **retry/DLQ** policies—handlers provide idempotency for exactly-once *effects*.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| DB claim vs delay queue | Unified DB+shards MVP | DB load at extreme |
| Skip vs catch-up | Skip/bounded default | Missed work |
| Short vs long lease | 30s + HB | More HB load |
| Sync HTTP vs queue | Queue for isolation | Latency |

### 6.3 Deal-breakers

1. Single global due-scanner for 100M schedules.  
2. No fencing — stale workers complete successfully after re-lease.  
3. Exactly-once marketing without idempotent handlers.  
4. Infinite retries without DLQ.  
5. Cron without timezone/DST policy.  
6. Ignoring :00 herd and clock jumps.

### 6.4 Progressive scale one-liner

**Baseline:** sharded `next_fire` + SKIP LOCKED leases → **10×:** batching/jitter → **100×:** memory wheels + tenant QoS → **1,000×:** regional cells + hybrid delay queues.

### 6.5 Interview closing line

> “We don’t pretend magic exactly-once side effects—we issue fenced, leased attempts with durable watermarks, retry through backoff into a DLQ, and require handlers to dedupe on attempt identity while sharding due scans so midnight crons don’t melt one database.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Semantics & correctness

**Q1: Exactly-once vs at-least-once?**  
A: Scheduler: at-least-once attempts + at-most-one lease; effects: idempotent handlers.

**Q2: What is a fencing token?**  
A: Monotonic token per lease generation; storage rejects stale completes.

**Q3: How to idempotency-key a cron fire?**  
A: `(schedule_id, scheduled_fire_at)` or `attempt_id` stored in side-effect DB unique constraint.

**Q4: Lease vs lock?**  
A: Lease times out for liveness; lock without TTL can deadlock dead workers.

**Q5: What if complete arrives twice?**  
A: Terminal state machine; second complete no-ops if token matches and already succeeded.

**Q6: Missed fires while paused?**  
A: On resume, apply catch-up policy from watermark.

### 7.2 Cron & time

**Q7: Where store cron?**  
A: Expression + IANA TZ; compute next in UTC.

**Q8: DST gap/overlap?**  
A: Library-defined; document; prefer UTC crons for infra jobs.

**Q9: last_fire vs next_fire?**  
A: `next_fire` for due; `last_scheduled` watermark for correctness.

**Q10: Jitter?**  
A: `hash(schedule_id) % jitter_max` seconds to spread :00.

**Q11: One-shot vs cron unified?**  
A: Yes via `next_fire_at`; once deletes/cancels after success.

### 7.3 Sharding & HA

**Q12: Who owns a shard?**  
A: Membership system assigns; epoch bumps on transfer.

**Q13: Rebalance storm?**  
A: Consistent hashing; move few shards; drain.

**Q14: Can two dispatchers claim same job?**  
A: Prevented by transactional claim / shard epoch + row lock.

**Q15: Hot tenant shard?**  
A: Subshard by schedule_id; tenant rate limits.

**Q16: Why SKIP LOCKED?**  
A: Concurrent claimers don’t block on same rows; each takes different due rows.

### 7.4 Workers & retries

**Q17: Heartbeat failure?**  
A: Lease expires; another worker may start; fencing protects.

**Q18: Long jobs?**  
A: Heartbeat extend; or lease = expected_runtime × factor with cap.

**Q19: Backoff strategy?**  
A: Exp + jitter; cap; dead-letter.

**Q20: Poison pill?**  
A: DLQ + metric; block schedule optional.

**Q21: Partial failure HTTP 200 but business fail?**  
A: Handler must return failure; or use two-phase with store.

**Q22: Concurrency=1?**  
A: Don’t claim if running attempt exists; or overlap policy queue.

### 7.5 Storage & indexes

**Q23: Schema for due queries?**  
A: Primary schedules; index `(shard, state, next_fire_at)`.

**Q24: History growth?**  
A: Hot 7–30d; export to cheap log store; aggregate metrics.

**Q25: Spanner vs Redis due?**  
A: Redis ZSET great for near-due speed; must dual-write durable truth or accept rebuild.

**Q26: Outbox to Kafka for execute?**  
A: Claim inserts outbox; workers consume — decouples execute from claim txn.

### 7.6 DLQ & ops

**Q27: DLQ replay?**  
A: Admin API creates new attempt; resets try_n carefully.

**Q28: Alerting?**  
A: DLQ rate, lag p99, lease expiry spikes, shard owner flapping.

**Q29: Pause all tenant?**  
A: Tenant flag checked in claim query.

**Q30: Migrate cron library version?**  
A: Shadow compute next; diff; staged roll.

### 7.7 Scale drills

**Q31: 500K due/s?**  
A: Many shards × batch claim; memory wheels; workers autoscaled on queue depth.

**Q32: 1B schedules mostly idle?**  
A: Index only near-due via bucketization; cold schedules not in hot memory.

**Q33: Million heartbeats/s?**  
A: Reduce HB frequency; batch HB; lease longer for trusted workers; move leases to lease service.

### 7.8 Alternatives & deal-breakers

**Q34: Single Postgres cron table + pgagent?**  
A: Fine small; fails shard/HA/tenant scale.

**Q35: Only Kafka delay topics?**  
A: Good for one-shots; awkward for mutable cron & pause.

**Q36: Sleep in thread per job?**  
A: Deal-breaker at scale.

**Q37: Distributed lock per job in Redis without durable schedule?**  
A: Loss on Redis flush; need durable SoT.

### 7.9 Interview craft

**Q38: How to open?**  
A: Cron+delay, lease/fencing, retries/DLQ, shard — then due QPS math.

**Q39: What numbers matter?**  
A: Active schedules, peak due/s, workers, retry rate, shard count.

**Q40: What impresses L5+?**  
A: Fencing + idempotency honesty, SKIP LOCKED claims, catch-up policy, :00 jitter, shard epochs.

**Q41: Common mistake?**  
A: Equating “unique job id” with exactly-once side effects; forgetting lease expiry races.

---

### Appendix A — Claim SQL sketch

```sql
WITH due AS (
  SELECT schedule_id FROM schedules
  WHERE shard = $1 AND state = 'active' AND next_fire_at <= $2
  ORDER BY next_fire_at
  LIMIT $3
  FOR UPDATE SKIP LOCKED
)
UPDATE schedules s SET
  next_fire_at = $far_or_next,
  version = version + 1
FROM due WHERE s.schedule_id = due.schedule_id
RETURNING s.*;
-- then insert attempts with fencing_token = version
```

### Appendix B — Complete with fencing

```text
def complete(attempt_id, token, result):
  row = attempts.get(attempt_id)
  if row.fencing_token != token: reject
  if row.status in terminal: return ok
  row.status = result
  if result == success and schedule.type == cron:
    schedule.next_fire_at = next_cron(...)
  elif result == fail:
    arm_retry_or_dlq(schedule, row)
```

### Appendix C — Backoff

```text
def backoff(try_n):
  return min(MAX, BASE * 2**try_n) + random(0, JITTER)
```

### Appendix D — Shard assignment

```text
ring = consistent_hash(dispatcher_ids)
owner(shard) = ring.lookup(shard)
on change: epoch[shard]++
```

### Appendix E — Heartbeat

```text
if now < lease_until - renew_before:
  return
UPDATE attempts SET lease_until=now()+TTL
WHERE attempt_id=? AND fencing_token=? AND status='running'
```

### Appendix F — Catch-up

```text
def advance_after_success(sched, scheduled_fire):
  n = next_cron(scheduled_fire)
  if policy == skip:
    while n < now() - grace: n = next_cron(n)
  sched.next_fire_at = n + jitter(sched)
```

### Appendix G — Timing wheel (near-due)

```text
wheel[seconds_mod] = list of schedule_ids
ticker each second:
  for id in wheel[now]:
    enqueue_claim_candidate(id)
reload from DB every minute for horizon
```

### Appendix H — DLQ record

```text
DLQItem {
  schedule_id, attempt_id, payload_ref,
  error, try_n, ts, tenant_id
}
```

### Appendix I — Concurrency gate

```text
if policy.concurrency == 1:
  if exists attempt in (leased, running) for schedule_id:
    skip claim (leave next_fire_at as-is or defer)
```

### Appendix J — NFR card

```text
p99 fire lag < 5s (typical)
Leases with fencing
Idempotent handlers required
Sharded due index
DLQ after max retries
Jitter on crons
```

### Appendix K — Membership drain

```text
1. mark dispatcher leaving
2. reassign shards
3. old: stop claim loops
4. wait max_lease_ttl
5. new: start with epoch+1
```

### Appendix L — Adapter HTTP

```text
POST target_url
Headers: X-Attempt-Id, X-Fencing-Token, X-Schedule-Id
Timeout < lease_ttl
Auth: per-tenant HMAC / OIDC
```

### Appendix M — Progressive scale table

| Scale | Due index | Dispatch | Execute | History |
|-------|-----------|----------|---------|---------|
| Base | SQL shard index | 3–9 nodes | Pool | SQL |
| 10× | Buckets | 30 nodes | Queues | SQL+archive |
| 100× | Memory wheel | Cells | Autoscale | Tiered |
| 1,000× | Hybrid Redis+DB | Cell fabric | Regional | Log only hot |

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “Unique constraint = exactly once” | Only on attempt row; not side effects |
| “Use cron on each host” | Duplicate fires; no central control |
| “Kafka is enough” | Still need schedule state & cron |
| “Longer lease = safer” | Worse failover latency |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| Lease | Time-bounded ownership of attempt |
| Fencing token | Generation id to reject stale owners |
| Watermark | last/next scheduled fire |
| DLQ | Dead-letter queue |
| SKIP LOCKED | Claim without waiting on locked rows |
| Catch-up | Policy for missed fires |

### Appendix P — Worked example

```text
1M schedules, 5% fire/hour → ~14 fires/s average
Peak :00 with bad alignment → 5K/s
Shards=64 → ~80 claims/s/shard peak — easy for SQL
Workers 100 → ~50 exec/s each at peak
History 5K/s writes → batch insert
```

### Appendix Q — Failure matrix

| Failure | Detection | Recovery |
|---------|-----------|----------|
| Worker kill | Lease timeout | Re-lease new attempt |
| Dispatcher kill | Membership | Shard takeover |
| DB blip | Health | Backoff scanners |
| Poison | Max tries | DLQ |
| Clock jump | Metrics | Rate limit + alert |

### Appendix R — 30m interview checklist

1. Clarify cron/delay, lease, retry/DLQ, scale.  
2. Due QPS + :00 herd math.  
3. Draw store → sharded dispatcher → workers → DLQ.  
4. Deep dive claim txn + fencing + idempotency.  
5. Scale 10×/100×/1,000×.  
6. Deal-breakers.

### Appendix S — Idempotent handler example

```text
def handle(attempt_id, payload):
  try:
    db.insert_effect(attempt_id, payload)  # unique(attempt_id)
  except Duplicate:
    return OK  # already applied
  do_side_effect(payload)
```

### Appendix T — Metrics

| Metric | Why |
|--------|-----|
| schedule_lag_seconds | SLO |
| claim_batch_size | Tuning |
| lease_expirations | Worker health |
| dlq_count | Poison/bugs |
| shard_reassigns | Stability |

### Appendix U — Related systems (conceptual)

| System | Relation |
|--------|----------|
| Chubby/etcd | Membership |
| Spanner/Postgres | Schedule truth |
| Pub/Sub | Execute bus |
| Borg/K8s | Worker deploy |
| Cloud Scheduler | Product analog |

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Many shards, batch claim, jitter |
| 100× | Near-due wheels, tenant QoS |
| 1,000× | Cells, hybrid delay queues, epoch fencing fabric |

---

*End of Distributed Task Scheduler system design.*
