# System Design: Ad Pacing (Budget + Flight Dates)

> **Focus areas:** Budget burn · Flight windows · Even / ASAP / custom pacing curves · Real-time eligibility · Allocation vs accounting · Overspend control · Coupling to frequency caps  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct money math (minor units), split decision vs billing QPS, explicit overspend tolerance, Netflix Ads 2025–26 themes  
> **Interview theme:** Spend the advertiser’s budget smoothly across the flight without large early dump or late underspend — under decision latency constraints

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

Goal: **bound ad pacing**—control *when* eligible ads may serve so cumulative spend tracks a desired curve across flight dates, without becoming the billing ledger or the frequency-cap system.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Throttle eligibility by budget+time | Frequency capping (sibling) |
| Money | Soft spend signals + hard stop near budget | Full ads ledger / invoicing SoT |
| Curve | Even, ASAP, frontend-loaded, custom | Marketing analytics UI |
| Decision | Go / no-go (+ optional bid multiplier) | Creative ranking ML |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is paced? | Campaign / line item budget | Entity-level controllers |
| F2 | Budget units? | Currency minor units or impression goals | Integer units; clear unit type |
| F3 | Flight? | start_at / end_at with TZ | Windowed controllers |
| F4 | Pacing mode? | EVEN default; ASAP; custom dayparts | Curve function |
| F5 | When check? | Ad decision eligibility | Low-latency read |
| F6 | When update spend? | On billable impression (or win) | Async update + reconcile |
| F7 | Overspend tolerance? | Small PPM; hard stop at limit+epsilon | Reservations near end |
| F8 | Underspend OK? | Prefer slight under vs large over | Conservative throttle |
| F9 | Timezone? | Advertiser / account TZ | Explicit |
| F10 | Hierarchy? | Line budgets roll to campaign | Parent remaining constraints |
| F11 | Ops? | Pause, boost, replan mid-flight | Config versions |
| F12 | Coupling caps? | Must also pass frequency caps | Parallel filters |

**MVP functional scope:**

1. Line/campaign with `budget`, `flight`, `pacing_mode`.  
2. Compute **target spend(t)** curve.  
3. Track **spent** + optional **reserved**.  
4. Decision: `eligible` if `spent+reserved < budget` and ahead/behind controller allows.  
5. Update spend on billable events idempotently.  
6. Hard stop near budget exhaustion.  
7. Metrics: pacing error, overspend PPM, throttle rate.

**Out of MVP:**

- Perfect multi-region exactly-once money without ledger sibling  
- Second-price auction redesign  
- Auto-bidder full RL agent as only design  
- Cross-advertiser budget pooling

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Eligibility latency | Inside decision budget | p99 < 5–15ms |
| N2 | Overspend | Tight | < 0.1–1% depending on policy |
| N3 | Durability of spend | Events durable | Rebuildable from billing events |
| N4 | Availability | Degrade throttle-closed near budget | Explicit policy |
| N5 | Control stability | Avoid oscillation | PID / periodic replan |
| N6 | Scale | 1000× decisions | Cached controller state |
| N7 | Audit | Explain throttle | Config + spend snapshots |
| N8 | Idempotency | No double spend count | event_id |

### 1.3 Cases

**Happy paths**

1. Even pacing across 30-day flight → roughly 1/30 budget/day.  
2. ASAP → serve until budget hits, subject to caps/inventory.  
3. Behind curve midday → loosen throttle; ahead → tighten.  
4. Budget exhausted → ineligible.  
5. Flight not started / ended → ineligible.

**Edge cases**

| Case | Behavior |
|------|----------|
| Burst traffic evening | Throttle by rate, not only daily total |
| Billing event late | Catch-up; may briefly oversit → epsilon hard stop |
| Clock skew | Server time; flight bounds server-side |
| Pause campaign | Immediate ineligible |
| Budget increased mid-flight | Replan remaining curve |
| Zero inventory day | Underspend; optional catch-up flag |
| Dual region updates | Home cell for spend; see multi-region |
| Duplicate beacon | Idempotent |

### 1.4 Scales

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Peak decisions/s | 20K | 200K | 2M | 20M |
| Active lines | 50K | 200K | 1M | 5M |
| Spend updates/s | 5K | 50K | 500K | 5M |
| Replan jobs/min | 1K | 10K | 100K | 1M |

**Forces:**  
- **10×:** In-memory controller cache; shard by line_id.  
- **100×:** Home cells; reservation tokens; hierarchical budgets.  
- **1,000×:** Probabilistic throttle; edge eligibility hints; separate hard-stop store.

### 1.5 Scope statement

> Design an ad pacing system that throttles line/campaign eligibility across flight dates to track a spend curve, updates on billable events with idempotency, hard-stops near budget, and scales with decision traffic while keeping overspend within an explicit tolerance.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Even pacing target

```text
budget B = $100,000.00 = 10,000,000 cents
flight = 10 days = 864,000 s
ideal rate = B / T ≈ 11.57 cents/s
At time t from start, target(t) = B × t / T
error = spent - target(t)
```

### 2.2 Decision amplification

```text
20K decisions/s × check 50 lines → naive 1M lookups/s
Cache controller state per line in decision process (push/pull every 1–5s)
→ lookups become local memory
```

### 2.3 Overspend race

```text
Remaining $10; 1,000 parallel decisions each assume OK without reserve
→ disaster overspend
Near exhaustion: require reservation or centralized token bucket
```

### 2.4 QPS classes

| Class | Baseline | 100× | Notes |
|-------|----------|------|-------|
| Eligibility check | 20K | 2M | cached state |
| Spend incr | 5K | 500K | idempotent |
| Replan | 100 | 10K | periodic |
| Billing reconcile | 10 | 1K | async |

### 2.5 Storage

```text
Controller state ~256B × 200K lines ≈ 50MB hot
Spend events durable in log/warehouse
```

### 2.6 Bottlenecks

1. End-of-budget thundering herd  
2. Stale controller → overspend  
3. Oscillation from aggressive control  
4. Ignoring daypart inventory shape  

---

## 3. High-Level Design

### 3.1 Funnel placement

```text
Targeting → PACING eligible → FREQ CAP eligible → rank/auction → serve
                ↑
         Pacing Controller state
                ↑
         Spend events (billing)
```

### 3.2 Controller state

```text
PacingState {
  line_id,
  budget_minor,
  spent_minor,
  reserved_minor,
  flight_start, flight_end,
  mode,
  target_slope,
  throttle_probability,  // or rate limit
  version,
  updated_at
}
```

### 3.3 Eligibility logic

```text
if now < start or now >= end: NO
if spent + reserved >= budget: NO
if mode == ASAP: YES (until budget)
if mode == EVEN:
  target = budget * elapsed / duration
  # PID / heuristic:
  if spent > target + band: NO or random(p_throttle)
  else YES
```

### 3.4 Spend update

```text
ApplyBillable(event_id, line_id, amount_minor):
  idempotent insert event_id
  spent += amount
  release reservation if any
  if spent >= budget: mark EXHAUSTED
```

### 3.5 Reservation (near end / high concurrency)

```text
TryReserve(line_id, amount, ttl):
  if spent+reserved+amount > budget: deny
  reserved += amount
On impression: convert reserve → spend
On TTL: reserved -= amount
```

### 3.6 Replanner

Periodic job computes throttle from error, inventory forecast, daypart multipliers. Pushes versioned state to decision nodes.

### 3.7 Store choices

| Data | Store |
|------|-------|
| Hot pacing state | Redis / in-mem replicated |
| Billable events | Durable log + warehouse |
| Budgets/config | OLTP ads config DB |

### 3.8 Hierarchy

Line cannot spend beyond min(line_remaining, campaign_remaining). Check both states.

### 3.9 Failure policy

| Case | Policy |
|------|--------|
| State store down | Fail closed if near budget; else last-known throttle + alert |
| Billing lag | Conservative remaining |
| Clock issues | Server time only |

### 3.10 Trade-offs

| Topic | Choice |
|-------|--------|
| Serving SoT | Cached controller |
| Money SoT | Billing events / ledger sibling |
| Control | Periodic replan + local throttle |
| Overspend | Reserve near exhaustion |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+-------------+     +----------------+     +------------------+
| Ad Decision |---->| Pacing Filter  |---->| Cap Filter/Rank  |
+-------------+     +-------+--------+     +------------------+
                            |
                            v
                    +-------+--------+
                    | State Cache    |<--- push from Replanner
                    | (per line)     |
                    +-------+--------+
                            |
+-------------+             v
| Impression/ |      +------+---------+
| Billing Evt |----->| Spend Applier  |---- durable log
+-------------+      +------+---------+
                            |
                            v
                     +------+---------+
                     | Replanner      |
                     +----------------+
```

### 4.2 Sequence: even pacing day

```text
t=0: spent=0, target=0 → serve
t=mid: spent ahead → throttle 70%
t=late: spent behind → throttle 0%
t=end: hard stop at budget
```

### 4.3 Sequence: reserve near end

```text
Decision→Pacing: reserve($0.05)
Pacing: OK token_id ttl=60s
Win/impression→Pacing: commit(token_id) or cancel
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Idempotent spend apply** by event_id.  
2. **Hard stop** at budget+epsilon.  
3. **Integer minor units**.  
4. **Flight bounds** enforced server-side.  
5. **Rebuild spent** from events.  
6. **Config version** on decisions.  
7. **No negative remaining**.  

### 5.2 Control theory practical

```text
error = spent - target(t)
throttle_p = clamp(k_p * error / budget, 0, 1)
# add damping / daily caps to avoid oscillation
```

ASAP: throttle_p=0 until exhaustion.

### 5.3 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Redis spent INCR; compute target inline |
| 10× | Replanner push; local caches |
| 100× | Home cell per line shard; reservations |
| 1,000× | Hierarchical aggregates; probabilistic serve |

### 5.4 Maintainability

Metrics: `pacing_error_ratio`, `throttle_rate`, `overspend_ppm`, `reserve_leak_rate`, `exhaustion_latency`.

### 5.5 Coupling to frequency caps

Both filters; pacing doesn’t count impressions for freq; caps don’t track dollars.

### 5.6 Dayparting & inventory

Even pacing on wall clock underspends if nights have no viewing — optional **traffic-weighted curves** using forecasted opportunity volume.

### 5.7 Multi-region

Spend home by `line_id` hash. Remote decision uses replicated state; near exhaustion force home reserve.

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Float dollars | Rounding drift |
| Update spend on bid not win | Desync vs money |
| No hard stop | Severe overspend |
| Replan every request with DB | Latency melt |
| Active-active spent++ | Double count |

### 5.9 Progressive deep dive

**1×:** `spent` Redis; eligibility `spent<budget && in_flight`; daily target naive.  
**10×:** PID throttle; push state.  
**100×:** Reserves; campaign hierarchy; forecast-weighted curves.  
**1,000×:** Edge hints; shard isolations; separate exhaustion service.

### 5.10 Reconciliation

Nightly: sum(events) vs controller spent; repair; alert on drift.

### 5.11 Security

Internal APIs; advertisers see aggregates not per-decision throttle secrets necessarily; audit budget edits.

---

## 6. Wrap-Up

### 6.1 Decisions

| Topic | Decision |
|-------|----------|
| Unit | Integer minor / impression goals |
| Hot path | Cached throttle state |
| Money truth | Billing events |
| Near end | Reservations |
| Default curve | EVEN with bands |

### 6.2 Risks

1. Overspend races  
2. Underspend from over-throttle  
3. Forecast error on traffic-weighted curves  
4. Reserve leaks  

### 6.3 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Budget+flight; not freq caps |
| 5–15 | State + eligibility |
| 15–25 | Even vs ASAP; control loop |
| 25–35 | Overspend + reserves |
| 35–45 | Scale, multi-region, traps |

---

## 7. Deeper / Related Interview Questions

**Q1. Pacing vs capping?**  
A: Pacing = budget/time; capping = user frequency.

**Q2. Why not SQL UPDATE budget each decision?**  
A: Hot contention + latency.

**Q3. ASAP bad?**  
A: Front-loads; may miss later high-value inventory; product choice.

**Q4. How handle timezone?**  
A: Store flight in absolute instants; display in account TZ.

**Q5. Impression goal campaigns?**  
A: Same controller with units=impressions; CPM billing still separate.

**Q6. What if billing pipeline down?**  
A: Freeze or conservative freeze near budget; alert.

**Q7. Bid shading interaction?**  
A: Optional multiplier when behind/ahead; keep simple go/no-go in MVP.

**Q8. Cross-line campaign budget?**  
A: Parent remaining gate.

**Q9. Exactly-once spend?**  
A: Idempotent event_id + durable log.

**Q10. Can throttle be random?**  
A: Yes probabilistic throttle reduces synchronization; measure.

**Q11. Leap seconds / DST?**  
A: Use UTC instants; avoid local civil time arithmetic in core.

**Q12. Trap: “Kafka exactly-once = correct budget”?**  
A: Still need idempotent keys + hard stop.

**Q13. Early exhaustion mid-day EVEN?**  
A: Controller too loose or traffic spike; tighten band / rate limit.

**Q14. Catch-up after outage?**  
A: Optional; can cause evening dump — product flag.

**Q15. House ads?**  
A: Not paced by advertiser budget.

**Q16. Multi-currency?**  
A: Budget in contract currency minor units; no silent FX.

**Q17. Who owns overspend money?**  
A: Ads finance policy; engineering keeps PPM within SLO.

**Q18. Edge computation?**  
A: At extreme scale, push throttle_p to edge with short TTL.

**Q19. Relation to data model doc?**  
A: Budgets/flights entities live in ads data model; this is control plane runtime.

**Q20. Metrics to page?**  
A: overspend_ppm, reserve_leak, stuck EXHAUSTED false positives.

---

## 8. Appendices

### A1. Schemas

```text
LineItem {
  line_id, campaign_id,
  budget_minor, currency,
  goal_type: REVENUE | IMPRESSIONS,
  flight_start, flight_end,
  pacing_mode: EVEN | ASAP | DAYPART | CUSTOM,
  pacing_curve_id?,
  state: ACTIVE|PAUSED|EXHAUSTED|ENDED
}

SpendEvent {
  event_id, line_id, campaign_id,
  amount_minor, ts, decision_id, impression_id
}

PacingSnapshot {
  line_id, spent_minor, reserved_minor,
  throttle_p, version, ts
}
```

### A2. Launch checklist

- [ ] Minor units everywhere  
- [ ] Idempotent spend apply  
- [ ] Hard stop chaos test  
- [ ] Reserve leak test  
- [ ] Replan push lag SLO  
- [ ] Shadow pacing vs legacy  

### A3. Glossary

| Term | Meaning |
|------|---------|
| Flight | Serve window |
| Throttle_p | Probability of blocking when ahead |
| Reserve | Temporary hold against budget |
| Overspend PPM | Over-budget per million |
| Replanner | Computes controller updates |

### A4. Traps

| Trap | Pushback |
|------|----------|
| Float money | Integers |
| Spend on bid | Billable only |
| No reserve at end | Overspend |
| Fail open at $0 remaining | Overspend |

### A5. Tests

1. Duplicate event_id → one spend.  
2. Parallel decisions at $0.01 remaining → ≤ epsilon overspend with reserves.  
3. Before flight → ineligible.  
4. Pause → immediate stop.  
5. Rebuild spent from events matches.

### A6. 60-second summary

> Pacing keeps **spend on a curve** across **flight dates**: decision nodes read **cached throttle/hard-stop state**, billable events **idempotently increment spent**, a **replanner** adjusts throttle, and **reservations** protect the last cents — separate from frequency caps and from the financial ledger SoT.

### A7. Related map

```text
Config DB → Replanner → State Cache → Decision Filter
Billing Events → Spend Applier → State + Log
```

### A8. SLO

| SLO | Target |
|-----|--------|
| Eligibility p99 | < 10ms |
| Overspend PPM | < 100 (example) |
| State freshness | < 5s p95 |
| Reserve leak | < 0.01% |

### A9. Curve library

```text
EVEN: target = B * t/T
ASAP: target = B (immediate)
FRONTEND: faster early slope then flatten
CUSTOM: piecewise breakpoints
```

### A10. Ownership

| Concern | Owner |
|---------|-------|
| Pacing runtime | Ads Serving |
| Budget config | Campaign management |
| Billing events | Measurement / money |
| Overspend policy | Ads Finance + Serving |

### A11. Progressive checklist

| Scale | Must |
|-------|------|
| 1× | Spent+budget+flight gate |
| 10× | Throttle + push state |
| 100× | Reserves + hierarchy |
| 1,000× | Edge hints + isolation |

### A12. PID notes

```text
Avoid raw derivative noise: use EWMA of error
Clamp daily max burn: min(remaining, daily_cap)
```

### A13. On-call

1. overspend_ppm page → enable strict reserve mode.  
2. Mass underspend → throttle stuck high? replan lag?  
3. EXHAUSTED stuck → spent/rebuild mismatch.

### A14. Naive comparison

| Naive | Failure |
|-------|---------|
| Daily cron budget/N | Intra-day dump |
| SQL row lock per decision | Won’t scale |
| Client-side pacing | Abuse |

### A15. Worked example

```text
B=1_000_000 cents; T=10d
At day 5 noon (~50% time): target≈500_000
spent=650_000 → ahead → throttle
spent=400_000 → behind → serve
```

### A16. Config versioning

Budget edits create new version; replanner computes remaining = new_budget - spent.

### A17. Cost worksheet

```text
redis_ops ≈ spend_updates + state_publishes
decision_cpu += local eligibility (~ns-µs)
```

### A18. Non-goals

- Replacing invoice generation  
- Frequency capping  
- Creative optimization  

### A19. Interaction with delivery forecast

Optional input: predicted opportunities_remaining to reshape even curve to traffic-weighted even.

### A20. Rubric

- Separated pacing vs caps vs ledger  
- Integer money  
- Overspend race addressed  
- Cached hot path  
- Progressive scale  

### A21. Traffic-weighted even pacing

```text
Let F(t) = forecasted cumulative opportunities in [0,t] / total_forecast
target_spend(t) = B * F(t)
# Falls back to wall-clock even if forecast unavailable
```

Binge-heavy evenings pull more budget under traffic-weighted curves — usually desirable vs underspending midday.

### A22. Reserve token schema

```text
ReserveToken {
  token_id, line_id, amount_minor,
  decision_id, expires_at, state: HELD|COMMITTED|EXPIRED|CANCELED
}
```

Commit path must be idempotent on `decision_id` / `impression_id`.

### A23. Parent/child remaining

```text
eligible = line.remaining > 0 AND campaign.remaining > 0
reserve both atomically in home cell order (campaign then line) to avoid deadlock
```

### A24. Oscillation example & fix

```text
t0 ahead → throttle 90% → undershoot
t1 behind → throttle 0% → surge overshoot
Fix: EWMA error, min replan interval, daily burn caps, random throttle
```

### A25. Decision debug record

```json
{
  "line_id": "li_1",
  "spent_minor": 650000,
  "target_minor": 500000,
  "throttle_p": 0.7,
  "budget_minor": 1000000,
  "pacing_version": 42,
  "eligible": false
}
```

### A26. Chaos tests

1. Drop 50% spend events → detect underspend; rebuild from log.  
2. Duplicate spend events → idempotent.  
3. Freeze replanner → stale throttle; alert on freshness SLO.  
4. Burst 10k decisions at $1 remaining with reserves → overspend ≤ epsilon.  
5. Clock jump +1h → targets recompute from server now.

### A27. SLO burn policies

| Signal | Action |
|--------|--------|
| overspend_ppm > budget | Force reserve mode globally for HARD budgets |
| state_freshness p95 > 30s | Page pacing oncall; freeze risky ASAP boosts |
| reserve_leak > threshold | Shorten TTL; fix commit path |

### A28. 90-second closer

> Pacing is a **budget×time controller**: cached throttle/hard-stop at decision, **idempotent spend** from billable events, **replanner** curves (even/ASAP/traffic-weighted), **reservations** near exhaustion, integer minor units — orthogonal to frequency caps and to finance ledgers.

### A29. Self-check

- [ ] Not confused with frequency capping  
- [ ] Overspend race addressed  
- [ ] Flight bounds  
- [ ] Cached hot path  
- [ ] Hierarchy budgets  
- [ ] Progressive scale  

### A30. Config push channel

```text
Replanner → PubSub pacing.state.v1 → Decision nodes apply version CAS
Snapshot every 1–5s per hot line; cold lines lazy pull
```

---

*End of document — Netflix system design interview prep: Ad Pacing.*
