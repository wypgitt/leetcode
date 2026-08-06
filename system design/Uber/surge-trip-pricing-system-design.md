# System Design: Surge / Trip Pricing Service

> **Focus areas:** Marketplace pricing · Supply/demand signals · Hex/geohash surge · Quote stickiness · Fairness · Fraud · Real-time vs batch features  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit quote lifecycle, auditability of prices, no silent price flips after accept, honest ML vs rules split  
> **Interview theme:** Uber — **pricing & surge** that balance liquidity, rider trust, and driver earnings

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

Goal: design a **trip pricing service** that produces **upfront quotes** (including surge/multipliers), keeps quotes **consistent through accept**, and adjusts marketplace liquidity via transparent-enough pricing controls.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Quote generation + surge signals + fare finalize | Full matching / dispatch |
| Money | Pricing amounts + audit trail | PCI card processing (payments API owns capture) |
| ML | Features + model hooks | Training platform internals |
| Uber lens | Liquidity, trust, explainability, abuse | Academic optimal auction only |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Upfront price? | Yes for most products | Quote object with expiry |
| F2 | Surge? | Geo + time multiplier / additive | Cell-level signal service |
| F3 | Inputs? | Distance, time, product, city, promo, tolls | Fare breakdown components |
| F4 | Stickiness? | Price locked at request/accept window | Quote id + version immutable for rider accept |
| F5 | Finalize? | Adjust for wait time, route change, tolls | Finalization rules engine |
| F6 | Products? | UberX, Comfort, XL, Reserve… | Product config catalog |
| F7 | Promos? | Coupons, subscriptions | Pricing composition order |
| F8 | Transparency? | Show multiplier / “busier than usual” | UX fields on quote |
| F9 | Experiments? | A/B pricing parameters | Experiment assignment in quote |
| F10 | Fraud? | Quote shopping, GPS spoof, promo abuse | Risk scores + caps |
| F11 | Offline config? | City minimums, per-minute rates | Config service + versioning |
| F12 | Replay? | Why was this $27.40? | Full audit log |

**MVP scope:**

1. Compute quote for `(origin, dest, product, city, user)` with breakdown.  
2. Maintain surge multiplier per geo cell, updated from supply/demand signals.  
3. Create **sticky quote** with TTL; bind to trip on accept.  
4. Finalize fare at trip end with allowed deltas (tolls, wait, cancel fees).  
5. Audit every quote/final fare.  
6. Basic fraud caps (max multiplier, velocity).

**Out of MVP:** continuous auction with per-driver personalized prices at extreme, full RL pricing agent in production without kill switch, cross-city arbitrage markets.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Quote latency | p99 < 150–250ms in-region |
| N2 | Availability | Degrade to last-known surge + base rates, never “no price” if possible |
| N3 | Correctness | Accepted quote honored within policy |
| N4 | Auditability | Reconstruct fare from logged inputs |
| N5 | Freshness of surge | Cell update every few–tens of seconds |
| N6 | Consistency | Quote read-your-writes; surge map eventually consistent OK |
| N7 | Safety | Hard caps / circuit breakers on multipliers |
| N8 | Throughput | See scale table |

### 1.3 Cases

**Happy:** Rider requests quote → surge 1.4× → accepts → trip completes → final ≈ quote (+ toll).  
**Edges:** quote expiry mid-accept; destination change; long wait; cancel fees; stadium spike; promo stacking; two devices quote-shop; signal pipeline lag; model failure → rules fallback; disputed fare.

| Case | Behavior |
|------|----------|
| Quote expired | Requote; do not silently reuse |
| Accept race at expiry | CAS on quote state `OPEN→BOUND` |
| Surge jumps after quote | Bound quote keeps price; new requests see new surge |
| Signal outage | Freeze last surge; alert; widen caps |
| Negative fare components | Clamp; never pay rider via bug |
| Airport flat rates | Product rules override distance |
| Reserved ride | Different pricing timeline |
| Currency/tax | City config; integer minor units |

### 1.4 Progressive scale

| Metric | Base (1 city) | 10× | 100× | 1,000× |
|--------|---------------|-----|------|--------|
| Quote QPS peak | 2K | 20K | 200K | 2M |
| Accept binds / s | 200 | 2K | 20K | 200K |
| Geo cells / city | 5K | 5–20K | — | — |
| Cities | 1 | 20 | 200 | 2,000 |
| Surge updates / s / city | 50 | 500 | 5K | 50K (global sum) |
| Config versions | 10/day | 100/day | 1K/day | continuous experiments |
| Audit events / day | 20M | 200M | 2B | 20B |

**Jumps:** 10× = shard by city; 100× = signal pipeline cells + quote store partitioning; 1,000× = hierarchical surge, edge quote caches with careful invalidation, strict experiment platforms.

### 1.5 Scope repeat-back

> Pricing service that generates auditable, sticky upfront quotes using base tariffs + geo surge signals + promos, finalizes fares under explicit rules, fails safe under signal/model outages, and scales city→global via sharded quote and surge planes.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Quote QPS

```text
City peak: 2K quotes/s (many riders browse without requesting)
Accept rate ~10% → 200 trips/s peak city (illustrative)

Payload quote response ~1–2 KB
2K × 2 KB = 4 MB/s egress trivial vs compute

1000×: 2M quotes/s → need heavy caching of surge maps + route estimates
```

### 2.2 Compute cost drivers

```text
Per quote:
  1) route ETA/distance (cacheable)
  2) tariff apply
  3) surge lookup (O(1) cell)
  4) promo
  5) risk
Route service often dominates latency — cache OD pairs aggressively
```

### 2.3 Surge state size

```text
5K cells × 64–128 B = < 1 MB / city — fits everywhere
Global 200 cities × 10K cells ≈ 2M cells → hundreds of MB — still fine sharded
```

### 2.4 Audit storage

```text
Quote audit ~500 B–2 KB with feature snapshot
20M/day × 1 KB = 20 GB/day city-class
1000×: tens of TB/day → sample feature vectors; keep deterministic inputs + config version
```

### 2.5 Bottlenecks

1. Route/ETA dependency latency  
2. Quote store hot keys (popular airports)  
3. Surge signal pipeline lag / stampede  
4. Promo service fan-out  
5. Experiment assignment correctness  
6. Fare dispute replay years later  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Tariff          → city/product base rates (per-min, per-km, booking fee, min fare)
SurgeMap        → cell_id → multiplier / additive + as_of
Quote           → priced offer with TTL, breakdown, config versions
FareFinalization→ trip completion pricing under rules
SignalWindow    → demand/supply metrics per cell over recent windows
```

### 3.2 Composition order (resolve carefully)

```text
base = f(distance, duration, tariff, time_of_day)
surged = apply_surge(base, surge_vector)   // define multiplicative vs additive
priced = apply_fees_taxes(surged)
final_quote = apply_promos(priced, promo_stack)  // order matters; document
clamp(final_quote, min_fare, max_fare_caps)
```

**Deal-breaker:** Undefined promo/surge ordering causing non-reproducible audits.

### 3.3 Options: surge computation

| Option | Pros | Cons | When |
|--------|------|------|------|
| A. Rules on demand/supply ratio | Explainable, safe | Less optimal | MVP / fallback forever |
| B. Periodic batch ML | Better | Stale | Mid scale |
| C. Streaming features + model | Reactive | Complexity, risk | 100×+ with guardrails |
| D. Continuous personalized prices | Liquidity | Trust/fairness hard | Careful product choice |

**Chosen:** Streaming **cell signals** every few seconds → **rules or constrained model** → **hard caps** → quote path reads versioned snapshot.

### 3.4 Quote lifecycle

```text
CREATED → OPEN → BOUND_TO_TRIP → CONSUMED_FOR_FINAL
              ↘ EXPIRED
              ↘ SUPERSEDED (requote)
```

**Invariant:** Once `BOUND_TO_TRIP`, rider-facing total cannot change except **enumerated finalize adjustments**.

### 3.5 Signal pipeline

```text
Trip events + driver presence
  → cell aggregations (open requests, available drivers, ETAs)
  → Surge Controller (caps, smoothing, hysteresis)
  → SurgeMap snapshot (version V)
  → Quote Service reads V
```

**Smoothing:** EMA / hysteresis to avoid flicker (1.9↔2.1 thrash).  
**Hysteresis:** different thresholds up vs down.

### 3.6 Storage choices

| Data | Store |
|------|-------|
| Tariff/config | Versioned config DB + CDN/cache |
| SurgeMap | Redis / memory per city shard |
| Quotes | KV/Cassandra keyed by quote_id; TTL |
| Audit | Append log / object store |
| Features | Online feature store (optional) |

### 3.7 Failure modes & degradations

| Dependency down | Degrade |
|-----------------|---------|
| Route service | Cache / haversine fallback + wider ETA band |
| Surge pipeline | Last-known map + freeze |
| ML model | Rules fallback |
| Promo | Price without promo; or fail closed if promo required |
| Quote DB | In-memory city cache short TTL (riskier) |

### 3.8 API sketch

```text
POST /v1/quotes
  {origin, dest, product_id, pickup_ts?, promo_codes?}
  → {quote_id, total, currency, breakdown, surge, expires_at, display}

POST /v1/quotes/{id}/bind
  {trip_id} → 200 bound | 409 expired

POST /v1/trips/{id}/fare/finalize
  {actual_route_metrics, tolls, wait_sec, cancel_reason?}
  → {final_fare, deltas[]}

GET /v1/surge?city=&cells=
GET /v1/quotes/{id}/audit
```

### 3.9 Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Sticky quotes | Rider trust vs marketplace lag |
| Cell surge vs personalized | Fairness/UX vs efficiency |
| Frequent surge updates | Liquidity vs flicker |
| Rich feature audit | Debuggability vs cost/PII |

---

## 4. Architecture Diagram

```text
  Rider App / API GW
           |
           v
   +---------------+     +------------------+
   | Quote Service |---->| Route / ETA Svc  |
   | (stateless)   |     +------------------+
   +--+----+-------+
      |    |    \
      |    |     \--> Promo Service
      |    |      \-> Risk / Fraud
      |    v
      |  Config (tariffs, caps, experiments)
      v
   Quote Store (sticky quotes)
      |
      v
   Trip Service (bind quote_id)

  Presence / Trip Events
           |
           v
   +---------------------+
   | Signal Aggregators  |  (per city cell)
   +----------+----------+
              v
   +---------------------+
   | Surge Controller    | --caps/hysteresis--> SurgeMap vN
   +---------------------+
              |
              +--> Quote Service (read snapshots)

  Finalize path: Trip complete → Fare Finalizer → Payments Product API
```

---

## 5. Design Deep Dive

### 5.1 Reliability

- **Idempotent quote create** with optional client `idempotency_key`.  
- **Bind CAS** prevents double-bind.  
- **Deterministic finalize** given inputs + quote snapshot + config version.  
- **Circuit breakers** on multiplier velocity (`Δsurge/min`).  
- **Kill switch** to force multiplier=1.0 city-wide.  
- Multi-AZ quote store; city shard isolation.

**Deal-breaker:** Changing bound quote total without user-visible policy; uncapped surge bug.

### 5.2 Scalability

- Shard Quote Service & SurgeMap by `city_id`.  
- Cache route OD with short TTL keyed by snapped coordinates.  
- Precompute surge snapshots every N seconds; quotes never recompute global state.  
- At 1,000×: edge quote assemblers with signed surge snapshots; central finalize still authoritative.

### 5.3 Maintainability

- **Pure pricing functions** (inputs → outputs) unit-tested across cities.  
- Config as code + approval workflow for tariff changes.  
- Golden trip fixtures for regression.  
- Clear ownership: Pricing owns quote/final; Payments owns capture; Matching owns dispatch.

### 5.4 Fairness & product trust

- Avoid opaque personalization that looks like discrimination without policy.  
- Display “busier than usual” rather than raw internals if required.  
- Same quote for same request context within experiment bucket.  
- Surge smoothing reduces perceived randomness.

### 5.5 Fraud

| Abuse | Control |
|-------|---------|
| Quote shopping | Rate limit; bind short TTL; device velocity |
| Destination pin abuse | Snap + route sanity |
| Promo stacking exploits | Explicit stack rules engine |
| Driver/rider collusion | Risk on finalize deltas |
| Signal gaming | Robust aggregations; outlier caps |

### 5.6 Money correctness

- Store currency **minor units** (cents).  
- Rounding rules documented (half-up per component vs end).  
- Tax inclusive/exclusive per city config.  
- Finalize produces ledger lines: base, surge, toll, wait, promo, tip (tip often separate).

---

## 6. Wrap-Up

> Quotes are sticky, auditable assemblies of tariff + **versioned surge snapshots** + promos. Surge comes from a city cell signal pipeline with caps and hysteresis. Finalize only applies allow-listed deltas. Scale by city sharding and caching routes; fail open to last surge + rules, never uncapped models.

**MVP path:** rules surge + Redis surge map + quote KV + finalize rules.  
**Next:** streaming features, experiments, richer fraud.  
**Risks:** trust (price flips), runaway surge, non-reproducible audits.

---

## 7. Deeper / Related Interview Questions

### 7.1 Quote stickiness

**Q: How long should quotes live?**  
A: Product-specific; often 1–5 minutes. Shorter in extreme surge volatility.

**Q: Can drivers see a different price?**  
A: Often driver sees earnings estimate separately; don’t confuse with rider quote.

**Q: What if route changes mid-trip?**  
A: Policy: threshold deviation → requote or finalize with delta; disclose in ToS/UX.

### 7.2 Surge mechanics

**Q: Multiplier vs additive?**  
A: Pick one primary; document. Multipliers amplify distance/time; additives for booking pressure.

**Q: Flickering surge?**  
A: EMA + hysteresis + min hold time per cell.

**Q: Hex size?**  
A: ~0.5–2 km effective; too small = noise; too large = unfair blending.

### 7.3 Consistency

**Q: Surge map read consistency for quotes?**  
A: Pin `surge_version` into quote; don’t re-read live map at finalize for base surge.

**Q: Two quotes different prices 1s apart?**  
A: Expected if signals move; sticky once bound.

### 7.4 ML

**Q: How to ship ML safely?**  
A: Shadow → limited cells → hard caps → monitoring on acceptance/completion → instant rollback.

**Q: Features online?**  
A: Cell demand, supply, weather, events, historical TOD; careful leakage.

### 7.5 Scale

**Q: 2M quote QPS globally?**  
A: Edge assembly + signed snapshots; almost no per-quote cross-region chat.

**Q: Hot airport cell?**  
A: Separate subcells; dedicated tariff; cache.

### 7.6 Disputes

**Q: Rider says map showed $12 charged $18?**  
A: Audit: quote screenshot fields, bind time, finalize deltas, config version; customer tool.

### 7.7 Comparison

**Q: vs airline dynamic pricing?**  
A: Similar yield management; Uber adds real-time geo liquidity + two-sided marketplace ethics/UX.

**Q: Is this matching?**  
A: No—pricing influences arrival rates; matching assigns drivers.

### 7.8 Arithmetic traps

**Q: Surge 2.5× on $9 base with $2 booking fee — what’s shown?**  
A: Define whether fee is surged. Document: e.g. surge applies to time+distance only, then add fees.

### 7.9 Kill switches

**Q: Model outputs 20×?**  
A: Hard cap (e.g. 3–5× city-configurable) + velocity breaker + paging.

### 7.10 Multi-region

**Q: Active-active quotes?**  
A: City-home region for quote durability; global app routes to city region.

---

## 8. Appendices

### 8.1 Quote schema

```json
{
  "quote_id": "q_...",
  "city_id": "sf",
  "product_id": "uberx",
  "currency": "USD",
  "total_minor": 2740,
  "breakdown": {
    "base_minor": 1200,
    "time_minor": 800,
    "distance_minor": 900,
    "booking_fee_minor": 200,
    "surge_multiplier": 1.4,
    "surge_minor": 840,
    "promo_minor": -200,
    "tax_minor": 0
  },
  "origin": {"lat": 0, "lng": 0, "cell": "882a1..."},
  "dest": {"lat": 0, "lng": 0},
  "route": {"meters": 5200, "seconds": 900, "provider_version": "r23"},
  "surge_version": 123456,
  "tariff_version": 88,
  "experiment_ids": ["exp_price_1:B"],
  "expires_at": "2026-08-06T10:00:00Z",
  "state": "OPEN"
}
```

### 8.2 Pseudocode: create quote

```text
function CreateQuote(req):
  tariff = Config.Tariff(req.city, req.product, now)
  route = RouteSvc.Estimate(req.origin, req.dest) // cached
  cell = Cell(req.origin)
  surge = SurgeMap.Get(req.city, cell) // pin version
  base = TariffApply(tariff, route, now)
  surged = ApplySurge(base, surge, tariff.surge_policy)
  priced = ApplyFeesTaxes(surged, tariff)
  promo = Promo.Evaluate(req.user, priced, req.codes)
  total = Clamp(priced + promo, tariff)
  Risk.Check(req, total, surge)
  quote = Persist(OPEN, all_inputs_versions, total, TTL)
  Audit.Log(quote)
  return quote
```

### 8.3 Pseudocode: surge controller

```text
function UpdateCell(cell, metrics):
  raw = DemandSupplyRatio(metrics) // or model_score
  capped = min(raw, cell.max_multiplier)
  prev = state[cell].multiplier
  next = EMA(prev, capped, alpha)
  if Rising(prev, next) and next-prev < min_step: next = prev
  if Falling and hold_timer_active: next = prev
  state[cell] = {multiplier: next, version: ++V, as_of: now}
```

### 8.4 Finalize rules (examples)

| Adjustment | Allowed when |
|------------|--------------|
| Tolls | Actual tolls observed / map |
| Wait time | After grace period |
| Cancel fee | Cancel state machine reason |
| Route delta | Beyond X% / Y meters |
| Tip | Separate; not in quote usually |

### 8.5 Config keys

```text
city.product.tariff_version
city.surge.max_multiplier
city.surge.max_delta_per_minute
city.quote.ttl_ms
city.rounding.mode
city.currency
```

### 8.6 Metrics / SLOs

| Metric | SLO |
|--------|-----|
| quote_latency_ms p99 | < 250ms |
| quote_bind_success | > 99% for non-expired |
| surge_pipeline_lag_s | < 30s |
| fare_dispute_rate | monitor regress |
| fallback_rules_ratio | alert if spike |

### 8.7 Event audit lines

```text
QUOTE_CREATED, QUOTE_EXPIRED, QUOTE_BOUND,
FARE_FINALIZED, SURGE_MAP_PUBLISHED, KILL_SWITCH_ON
```

### 8.8 Experiment safety

- Assignment sticky per user/session for quote browsing window.  
- Guardrail metrics: complete rate, cancel rate, driver accept rate, marketplace imbalance.  
- Auto-disable on guardrail breach.

### 8.9 Failure injection

- Route service 500s  
- Surge version stall  
- Quote DB latency 1s  
- Multiplier cap removed (should still have code cap)  
- Clock skew on expiry  

### 8.10 Interview checklist

- [ ] Sticky quote + expiry  
- [ ] Surge version pinned  
- [ ] Caps / hysteresis / kill switch  
- [ ] Promo composition order  
- [ ] Finalize allow-list  
- [ ] Audit reproducibility  
- [ ] City sharding  
- [ ] Fallback path  
- [ ] Minor units / rounding  
- [ ] Fraud velocity  

---

## 9. Extended Deep Dive (Interview Amplifiers)

### 9.1 Quote pinning vs marketplace lag

Sticky quotes protect rider trust but can lag true supply/demand. Mitigations: short TTL under extreme volatility, display “price may update if you wait,” and never mutate a **bound** quote’s rider total except allow-listed finalize deltas.

### 9.2 Signal quality

Raw open requests / available drivers is noisy. Use robust stats (winsorize outliers), ignore ghost demand (rapid cancel loops), and apply hysteresis so cells do not flicker 1.8↔2.0 every few seconds.

### 9.3 Experimentation

Pin experiment assignments into the quote. Guardrails: completion rate, cancel rate, driver accept rate, and marketplace imbalance. Auto-disable on breach.

### 9.4 Airport / venue specials

Flat rates and geofenced tariffs often override pure distance×surge. Model as product rules with higher precedence than generic cell surge.

### 9.5 Fare dispute toolkit

Support must see: quote screenshot fields, surge_version, tariff_version, bind timestamp, finalize deltas, and config approval id. Without this, pricing on-call cannot resolve trust incidents.

### 9.6 Pseudocode: bind quote

```text
function BindQuote(quote_id, trip_id):
  q = lock(quote_id)
  if q.state == BOUND and q.trip_id == trip_id: return q  // idempotent
  if q.state != OPEN or now > q.expires_at: reject EXPIRED
  q.state = BOUND; q.trip_id = trip_id
  audit(BIND)
  return q
```

### 9.7 Degradation matrix

| Dependency | Degrade |
|------------|---------|
| Route ETA | Cached OD / haversine + wider band |
| Surge pipeline | Freeze last map |
| ML model | Rules fallback |
| Promo | Price w/o promo or fail if required |
| Quote DB | Fail closed on bind (money path) |

### 9.8 Metrics that matter

- `quote_latency_ms` p99
- `surge_pipeline_lag_s`
- `quote_expiry_rate`
- `finalize_delta_fraction`
- `fallback_rules_ratio`
- `kill_switch_engagements`

### 9.9 Security / abuse

Rate-limit quote shopping; detect destination pin thrash; clamp personalized features that could encode protected attributes improperly; audit admin tariff edits.

### 9.10 1000× posture

Edge quote assemblers consume **signed surge snapshots** published per city every few seconds. Finalize and ledger remain regional authorities. Marketing/experimentation platforms must not write surge maps directly—only via Surge Controller.

*End of surge / trip pricing system design.*

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).

### Additional deep-dive notes

- Keep city/region cells for blast-radius isolation.
- Prefer server-authoritative timers and versions over client clocks.
- Idempotency keys on all mutating APIs that mobile may retry.
- Outbox pattern for side effects after state transitions.
- Explicit degrade modes: what you turn off first under load.
- Golden fixtures for disputes and fare/state reconstructions.
- Load-test stadium and airport topologies, not only uniform random.
- Document deal-breakers aloud in interviews (double charge, lost trip, etc.).
- Separate control-plane config pushes from data-plane hot paths.
- Measure peak ≠ average; provision for shard imbalance (1.5–2×).
