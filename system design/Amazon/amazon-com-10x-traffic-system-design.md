# System Design: Amazon.com at 10× Traffic

> **Focus areas:** Traffic planes · Edge/CDN · Catalog/search/cart/checkout · Inventory/ATP · Dependency isolation · Load shedding · Caching · Cells · Peak readiness · Progressive 10×→100×→1,000× beyond the prompt
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Split read vs buy paths; deal-breaker: one shared monolith DB for browse+checkout; explicit shed order; customer trust on checkout integrity
> **Interview theme:** Amazon SDE III / L6 — **Scale Amazon.com** under sustained 10× (and discuss 100×/1,000×)—Prime Day / pandemic-class surge thinking

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

Goal: explain how **Amazon.com** (retail site + purchase path) would handle **10× traffic**, with architecture that continues to 100×/1,000×. Interviewers care less about naming every Amazon internal service and more about **planes, bottlenecks, shedding, and integrity**.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Scale customer shopping journeys | Redesign FC robotics |
| Prompt | "10× traffic" | Only CDN caching trivia |
| Integrity | Cart/checkout/inventory correctness | Best-effort browse everywhere |
| Amazon lens | Peak ops, ownership, frugality, trust | Fake infinite horizontal scale handwave |

### 1.1 Functional Requirements (preserve under load)

| # | Journey | Must keep working | Can degrade |
|---|---------|-------------------|-------------|
| F1 | Home/browse | Something useful renders | Personalization richness |
| F2 | Search/PDP | Find & view products | Perfect ranking / every widget |
| F3 | Cart | Add/view reliably | Cross-device instant sync |
| F4 | Checkout | Pay & place order correctly | Fancy upsells |
| F5 | Order history | Eventually | Instant global |
| F6 | Recommendations | Optional | Entire rails empty with fallback |
| F7 | Accounts/login | Auth works | Noncritical profile edits |
| F8 | Prime benefits | Entitlement correct | Marketing modules |

**MVP interview scope:** identify critical vs noncritical paths; design caching, partitioning, async, shedding, and peak ops for 10× with a path to 100×/1000×.

**Out:** rewriting every subsystem in 45 minutes; claiming you'll "just add servers" without dependency math.

### 1.2 Non-Functional Requirements

| # | NFR | Target thinking |
|---|-----|-----------------|
| N1 | Browse p99 | Keep interactive (100s ms) via edge |
| N2 | Search p99 | Tens–low hundreds ms |
| N3 | Checkout success | **Protect** — prefer shed browse than corrupt checkout |
| N4 | Availability | Partial degradation > total blackout |
| N5 | Consistency | Strong for orders/payments/inventory reservations |
| N6 | Cost | 10× traffic ≠ blindly 10× cost — hit rate & shed |
| N7 | Peak | Planned capacity + elasticity + freeze |

### 1.3 Cases

**Happy 10×:** CDN absorbs static & many PDP; search scales; checkout capacity reserved; noncritical widgets shed.  
**Edges:** cache stampedes; dependency retry storms; inventory races; payment PSP latency; regional outage; cart hot keys; bot traffic; flash deals; search thundering for one ASIN; login storms.

| Case | Behavior |
|------|----------|
| Search overload | Shed autocomplete/personalization; keep core search |
| Recs down | Fallback popular / hide widget |
| Cart store hot | Shard + coalesce; never lose adds silently |
| Checkout dependency sick | Queue with honesty; don't double-charge |
| Bots | WAF/bot mgmt at edge early |

### 1.4 Progressive scale (prompt is 10×; still show jumps)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Page views / day | 5B | 50B | 500B | 5T |
| Peak browse QPS | 200K | 2M | 20M | 200M |
| Search QPS | 50K | 500K | 5M | 50M |
| Add-to-cart QPS | 5K | 50K | 500K | 5M |
| Checkout starts / s | 1K | 10K | 100K | 1M |
| Orders / s | 300 | 3K | 30K | 300K |
| Edge cache hit | 80% | 85% | 90% | 95% |
| Origin browse QPS | 40K | 300K | 2M | 10M |

**Note:** Numbers are interview-grade magnitudes, not confidential Amazon stats—state that.

**What 10× forces immediately:** edge/CDN, read replicas/caches, search shard capacity, cart/checkout isolation, load shedding, bot defense, dependency budgets, peak runbooks.

**100× / 1000×:** marketplace cells, stricter hierarchy of caches, on-device/edge composition, national/regional buy cells, radical simplification of page modules under peak.

### 1.5 Scope statement

> Scale Amazon.com shopping under 10× traffic by splitting browse/search/cart/checkout planes, absorbing reads at the edge, protecting purchase integrity with isolation and shedding, and outlining further jumps to 100×/1,000× with cells and progressive simplification.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Don't treat "traffic" as one number

```text
Browse QPS ≫ Search QPS ≫ Cart QPS ≫ Checkout QPS ≫ Order finalize QPS
10× browse is mostly cacheable
10× checkout is expensive and stateful
```

### 2.2 Cache leverage

```text
Baseline origin 40K browse/s
If hit rate 80% → 200K browseredge QPS implies 40K origin
10× browser to 2M with hit 85% → origin 300K (7.5× not 10×)
+1% hit rate often > +10% app servers
```

### 2.3 Payload / egress

```text
Average page weight heavily CDN'd (images)
HTML/API JSON 20–100KB personalized
2M QPS × 50KB = 100 GB/s — impossible from one region origin → edge composition / ESI / fragments
```

### 2.4 Checkout math

```text
3K orders/s at 10× peak (example)
Each: authz, tax, inventory reserve, payment, order write, events
⇒ several KU of dependent QPS — capacity plan each dependency
```

### 2.5 Bottleneck ranking

(1) Shared dependencies (identity, inventory, payments) (2) Search clusters (3) Cache stampedes (4) Cart data stores (5) Retry amplification (6) Raw web tier count (often not #1 if cached).

### 2.6 Latency budgets (browse fragment)

```text
Edge 5–20ms + parallel fragment fetches 50–150ms + merge → p99 goal hundreds ms
Checkout: seconds OK if reliable; never silent fail
```

---

## 3. High-Level Design

### 3.1 Critical planes

| Plane | Examples | Scale strategy |
|-------|----------|----------------|
| Static/media | Images, JS, CSS | CDN |
| Browse composition | Home, PDP shell | Edge + fragment caches |
| Search/discover | Query, suggest | Sharded search tier |
| Personalization | Recs, ranking | Async features; shedable |
| Cart | Session/user cart | Sticky shard store |
| Checkout/order | Purchase path | Isolated capacity; strong consistency |
| Post-order | Notifications, tracking | Async |

### 3.2 Components (logical)

1. **Edge / CDN / Bot management**  
2. **API Gateway / Page Composition**  
3. **Catalog service** (item metadata)  
4. **Search / Autocomplete**  
5. **Pricing / Promotions**  
6. **Recommendations**  
7. **Cart service**  
8. **Inventory / ATP**  
9. **Checkout orchestrator**  
10. **Payments**  
11. **Order service**  
12. **Identity / Session**  
13. **Experimentation** (traffic-aware)  
14. **Observability / Load shed controllers**

### 3.3 Shed order (declare explicitly)

```text
1. Ads / decorative modules
2. Recs / personalization richness
3. Reviews secondary pages
4. Autocomplete fuzzy extras
5. Search personalization
6. Browse noncritical fragments
— protect —
7. Cart critical APIs
8. Checkout / payment / order
9. Login/session validation
```

Never shed checkout before recs—say this.

### 3.4 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Page build | Fragments + isolation | One bad widget ≠ blank site |
| Cart | Dedicated store | Protect from browse load |
| Inventory | Reservation leases | Oversell control |
| Peak | Feature freeze + capacity | Stability |
| Personalization | Best-effort | Protect p99 |
| Cells | Marketplace/region | Blast radius |

---

## 4. Architecture Diagram

```text
Client
  → Edge/CDN/WAF/Bot
    → Page Composer / API Gateway
        ├─ Catalog Cache
        ├─ Search
        ├─ Pricing
        ├─ Recs (timeouts, fallback)
        ├─ Reviews (timeouts)
        └─ Session/Identity
    → Cart Service (isolated)
    → Checkout Orchestrator → ATP + Payments + Order Service
                              → Outbox events → fulfillment

Load Shed Controller observes SLOs → toggles feature flags / concurrency caps
```

### 4.1 PDP sequence under load

```text
Edge cache shell
Parallel: catalog, price, deal, recs, reviews
Timeouts per dependency (e.g. recs 50ms)
Degraded PDP still buyable
```

### 4.2 Checkout sequence

```text
Validate session → quote → reserve inventory → tax → payment auth →
persist order → capture/confirm → ack customer
Idempotency keys throughout
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Order place idempotent** — no double charge / double order.  
2. **Inventory reservation** explicit leases.  
3. **Browse degradation ≠ corrupt buy path**.  
4. **Dependency timeouts + bulkheads** everywhere on page.  
5. **Retry budgets** — no retry storms.  
6. **Feature flags** for instant shed.  
7. **Cell isolation** limits outage radius.  
8. **Clock/time** server-side for deals.

### 5.2 Scalability moves for 10×

| Layer | 10× move |
|-------|----------|
| Edge | Expand PoPs; raise cache TTLs carefully; bot mgmt |
| Composer | Autoscale; fragment cache; concurrency caps |
| Search | Add replicas/shards; query cost controls |
| Catalog | Cache aggressively; CQRS read models |
| Cart | Shard by customer_id; raise capacity |
| Checkout | **Reserved** capacity pools separate from browse |
| Data | Read replicas; separate OLTP from analytics |
| Ops | Game day; freeze; war rooms |

### 5.3 Maintainability / peak process

- Dependency SLA catalogs.  
- Automated load tests with production shape (Zipf ASINs).  
- Error budgets per plane.  
- Change freezes near peak.  
- Runbooks for shed toggles.

### 5.4 Progressive scale beyond 10×

**10× (prompt focus):** caching + isolation + shed + capacity + bots.  
**100×:** marketplace/region cells; edge-heavy composition; stricter searchable indexes hierarchy; checkout regional homes.  
**1000×:** radical client/edge rendering; on-device fragments; approximate personalization default; buy-path ultra-minimal; national event traffic engineering.

### 5.5 Bulkheads & timeouts

Each fragment call: timeout, semaphore, fallback. Hystrix-class pattern (conceptually). One reviews outage must not exhaust composer threads.

### 5.6 Cache stampedes

Soft/hard TTL; singleflight/coalescing; jittered expiry; pre-warm top ASINs before deals.

### 5.7 Inventory under surge

Flash deal ASIN: reservation service hot partition → shard by item+attempt; fair queues; serve "sold out" fast rather than timeout; don't lock global inventory DB for browse reads.

### 5.8 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Shared thread pool browse+checkout | Purchase collapse when PDP viral |
| Infinite retries | Cascading failure |
| Personalization on critical path without timeout | Blank pages |
| Global lock per ASIN browse | Meltdown |
| Scale checkout via same burstable pool as images | Bad economics + risk |
| Ignore bots | Paying for scrapers |

---

## 6. Wrap-Up

### 6.1 Designed

A plane-split Amazon.com architecture that absorbs 10× primarily at edge/caches, isolates cart/checkout, sheds noncritical personalization, controls retries/bots, and extends to 100×/1000× via cells and further edge push.

### 6.2 Decisions

1. Split browse vs buy capacity  
2. Fragment timeouts + fallbacks  
3. Explicit shed order  
4. Idempotent checkout  
5. Inventory leases  
6. Bot defense at edge  
7. Peak freeze + game days  
8. Progressive cells for 100×+

### 6.3 Risks

- Hidden shared dependencies (DNS, identity, certs)  
- Stampede on deal ASINs  
- Over-aggressive shed hurting conversion  
- Regional imbalance  
- Payment PSP external limits  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Clarify 10× which journeys; numbers |
| 5–15 | Planes + edge cache math |
| 15–25 | Search/PDP degradation |
| 25–35 | Cart/checkout/inventory protection |
| 35–45 | Shed order, bots, 100× cells, ownership |

### 6.5 Closer

> **Amazon.com 10×:** cache-heavy browse, isolated buy path, bulkheaded fragments, explicit load shedding, idempotent checkout, peak operating mechanisms—and a straight story to 100×/1,000× cells.

---

## 7. Deeper / Related Interview Questions

### 7.1 What does 10× mean?

**Q: 10× page views or 10× revenue?**  
A: Ask. Usually concurrent requests/QPS. Checkout may not scale linearly with browse (browsing bots / window shoppers).

**Q: Global or one region?**  
A: Ask; design for skewed regional peaks (e.g., US Prime Day).

### 7.2 Caching

**Q: Personalized home cacheable?**  
A: Shell + user fragments; anonymous heavily cached; logged-in short TTL fragments.

**Q: PDP cache with price changes?**  
A: Cache catalog; price fragment shorter TTL; deal flags purge.

### 7.3 Search

**Q: How to 10× search?**  
A: Replica sets; shard by term/hash; cache hot queries; reject costly queries; separate suggest cluster.

**Q: Relevance under shed?**  
A: Fall back to less personalized ranking—still correct results.

### 7.4 Cart

**Q: Guest cart storms?**  
A: Cookie carts in edge/KV; merge carefully on login; rate limit.

**Q: Lost add-to-cart?**  
A: SEV-level; durable write before ACK; metrics on add failures.

### 7.5 Checkout & money

**Q: Protect against double place order?**  
A: Idempotency key per attempt; state machine.

**Q: Payment latency spike?**  
A: UX waiting; uncertainty protocol; don't re-post blindly.

### 7.6 Inventory

**Q: Oversell at 10×?**  
A: More races → leases + probabilistic safety stock; customer messaging playbooks.

### 7.7 Dependencies

**Q: Biggest surprise outages?**  
A: Shared auth, certificate expirations, DNS, client feature flags misconfig, retry storms—not only "need more pods".

### 7.8 Bots & scrapers

**Q: How affect 10×?**  
A: Can be majority of "traffic"; challenge/WAF; don't celebrate QPS vanity.

### 7.9 Experiments

**Q: A/B at peak?**  
A: Freeze high-risk; keep sticky assignments; reduce variants.

### 7.10 Multi-region

**Q: Active-active browse?**  
A: Yes often. Checkout home cell by customer/marketplace—stronger consistency.

### 7.11 Interview traps

**Q: "Kubernetes autoscaling solves 10×"?**  
A: Incomplete without dependency & data plane math.  
**Q: Microservices everywhere diagram?**  
A: Prefer planes + failure math.  
**Q: Ignore checkout because browse is bigger?**  
A: Inverted priorities.

### 7.12 Metrics

| Metric | Why |
|--------|-----|
| Origin QPS / hit rate | Cost & scale |
| Fragment timeout rates | Degradation |
| Checkout success rate | Revenue/trust |
| Add-to-cart success | Funnel |
| Shed flag states | Ops |
| Bot ratio | Real load |
| Dependency p99 | Cascades |

### 7.13 Ownership

**Q: Who owns peak?**  
A: Retail website IC + dependency teams on call; clear shed authority.

**Q: Who can flip shed flags?**  
A: Pre-authorized break-glass; audited.

### 7.14 Progressive

**Q: After 10× works, what fails at 100×?**  
A: Cell blast radius, edge composition necessity, search cost, inventory hot partitions, organizational coordination.

### 7.15 Customer trust

**Q: Show wrong price then fail checkout?**  
A: Bad; price guarantee fragments consistency; if degraded, show ranges / confirm at checkout clearly.

---

## 8. Appendices

### 8.1 Dependency budget table (example)

| Dependency | Timeout | Fallback |
|------------|---------|----------|
| Catalog | 50ms | Cached last-good |
| Price | 40ms | Cached / "see checkout" |
| Recs | 30ms | Hide / popular |
| Reviews | 40ms | Hide stars count cached |
| ATP soft | 40ms | Show "limited" vague |
| Cart | 100ms | Error honest retry |
| Checkout reserve | 200ms | Queue / fail soft |

### 8.2 Shed flag checklist

- [ ] `recs_enabled`  
- [ ] `reviews_enabled`  
- [ ] `personalization_rich`  
- [ ] `autocomplete_fuzzy`  
- [ ] `home_modules_*`  
- [ ] `browse_only_mode` (extreme)  

### 8.3 Oncall peak checklist

- [ ] Edge hit rate  
- [ ] Origin CPU / saturation  
- [ ] Search p99 / error  
- [ ] Cart success  
- [ ] Checkout success  
- [ ] Payment PSP  
- [ ] Inventory conflicts  
- [ ] Bot challenges  
- [ ] Shed flags state  
- [ ] Error budget burn  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Plane | Failure/scale domain |
| Bulkhead | Isolation of resources |
| Shed | Deliberate feature off |
| Cell | Blast-radius unit |
| ATP | Available to promise |
| Soft TTL | Refresh before hard expire |
| Game day | Peak rehearsal |

### 8.5 Deal-breakers

- Shared pools browse+checkout  
- No timeouts on fragments  
- Retry amplification  
- Autoscaling mythology without data plane  

### 8.6 Capacity sketch (illustrative)

| Scale | Sketch |
|-------|--------|
| 1× | Multi-AZ services, CDN, search cluster |
| 10× | +cache, +shards, reserved checkout pool, bot mgmt |
| 100× | Cells per marketplace/region, edge composer |
| 1000× | Edge-first pages, minimal buy path, massive TE |

### 8.7 Failure injection

1. Kill recs — pages alive.  
2. Search +50% latency — shed personalization.  
3. Cart shard down — partial; sticky failover.  
4. PSP latency — checkout UX; no double charge.  
5. Viral ASIN — soft sold-out; protect inventory partition.  
6. Retry bug — detect via outbound concurrency.

### 8.8 Order idempotency sketch

```text
Idempotency-Key: customer_id + cart_version + attempt
Order state machine: CREATED→RESERVED→PAID→PLACED
```

### 8.9 Ownership map

| Plane | Owner |
|-------|-------|
| Edge/CDN | Traffic |
| Page composer | Website |
| Search | Search |
| Cart | Cart team |
| Checkout/order | Purchase |
| ATP | Inventory |
| Payments | Payments |
| Peak IC | Rotating L6+ |

### 8.10 Related designs

Distributed cache, search autocomplete, online store, payments, inventory, rate limiter, AB platform.

### 8.11 Interview closer checklist

- [ ] Split planes  
- [ ] Cache math  
- [ ] Bulkheads  
- [ ] Shed order  
- [ ] Checkout integrity  
- [ ] Bots  
- [ ] 100× cells  
- [ ] Ownership  

### 8.12 Static vs dynamic

Push all immutables to CDN; versioned assets; HTML templates short-cached; user-specific late-bind.

### 8.13 Mobile vs web

Shared APIs; different composition; mobile may tolerate fewer widgets—natural shed.

### 8.14 International

Marketplace cells (amazon.co.uk etc.); tax/currency local; don't one-DB global.

### 8.15 Cost narrative

Hit rate, bot ratio, fragment fanout, and unnecessary personalization dominate bill at 10×. Frugality is architectural.

### 8.16 LP hooks

Ownership of peak SEVs; Dive Deep on dependency graphs; Frugality via cache/bots; Customer Obsession protecting checkout honesty; Bias for Action shed early.

### 8.17 Sample degraded PDP JSON

```text
{asin, title, price_fragment_ok, recs: null, reviews: cached_summary, buybox: ok}
```

### 8.18 Retry policy

```text
Idempotent GETs: limited retry with jitter
POSTs: only with idempotency keys
Circuit open: fail fast
```

### 8.19 Pre-warm plan

Top N ASINs, deal pages, search head queries, identity JWKS, rate cards/tax—before event.

### 8.20 Communications

Status page honesty; if checkout impaired, say so; don't gaslight "everything fine" while orders fail.

---

## Deep Technical Notes — Amazon.com 10×

### Fragment graph

Define max parallel fanout (e.g., 8); critical vs optional edges; composer deadline (e.g., 200ms) return partial.

### Session stores

Sticky regional Redis/Dynamo; regenerate on failure carefully; CSRF tokens.

### Catalog read models

Denormalized PDP documents in KV/CDN; updates via stream; eventual for non-price fields.

### Price correctness

Price service authoritative at checkout; browse display may be slightly stale—policy.

### Search cost control

Max clauses; timeout; tiered quality; expensive query queue.

### Cart sharding

`hash(customer_id)`; guest `hash(cart_id)`; avoid hotspot celebrity single cart (rare).

### Checkout reserved pool

Separate cluster/queue quotas; browse autoscaling cannot starve purchase.

### Eventing

Orders to fulfillment via outbox; spike buffers; backpressure to promise engine if FC saturated (network).

### Security at scale

WAF rules; credential stuffing defense; payment PCI scope unchanged by traffic.

### Data retention analytics

Clickstream sample under peak to control cost.

---

## Interview Cards — Amazon.com 10×

### Card 1: Planes split

Browse ≠ search ≠ cart ≠ checkout.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Website IC; trust failure = checkout dark while banners live (bad optics inverted).

### Card 2: Cache math

Hit rate changes origin multiplier.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Traffic + website.

### Card 3: Bulkhead timeouts

Per-fragment deadlines.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Composer.

### Card 4: Shed order

Recs before checkout.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Peak IC authority.

### Card 5: Reserved checkout capacity

Don't share burstable with browse.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Purchase path.

### Card 6: Idempotent order

No double place.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Orders/payments.

### Card 7: Inventory leases

Flash deal protection.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** ATP.

### Card 8: Bot management

Traffic ≠ customers.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Security/traffic.

### Card 9: Stampede control

Singleflight + jitter + prewarm.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Cache platform.

### Card 10: Retry budgets

Prevent cascades.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** All clients.

### Card 11: Search scale

Shards/replicas/cost controls.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Search.

### Card 12: Feature freeze

Peak stability.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Org mechanism.

### Card 13: Cells at 100×

Marketplace/region blast radius.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** Architecture.

### Card 14: Deal-breaker

Shared pools; no timeouts; ignore bots.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** L6 early callout.

### Card 15: Metrics scoreboard

Hit rate, checkout success, fragment timeouts, bot ratio.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** War room wall.

### Card 16: Honest degradation

Buyable PDP without recs.

**Follow-ups:** 10× break? Pager? Fallback? Metric?  
**Ownership:** CX + website.

---

## Scenario Runbooks

### R1 — Prime Day T0 surge
Watch edge hit; enable pre-approved shed; protect checkout pools; bot challenge escalate.

### R2 — Viral deal ASIN
ATP hot partition mode; fast sold-out; prewarm PDP; limit recs pointing stampede.

### R3 — Search yellow
Disable fuzzy/personalization; add replicas; query cost governor.

### R4 — Payment partner brownout
Checkout messaging; extend timeouts carefully; idempotent resume; pause noncritical spends.

### R5 — Retry storm detected
Circuit break; deploy client fix; shed load; postmortem.

---

## Extended Rapid Q&A

**Q: First question you'd ask interviewer?**  
A: 10× on which plane—browse, search, or checkout—and which marketplace?

**Q: Is CDN enough?**  
A: Necessary not sufficient.

**Q: Vertical scale checkout DB?**  
A: Temporary bridge; shard/cell soon.

**Q: GraphQL fanout danger?**  
A: Yes—unbounded fields amplify 10× pain; gate.

**Q: SSR vs CSR?**  
A: Hybrid; edge SSR shells help SEO & first byte; don't block on every widget.

**Q: How to test 10×?**  
A: Shadow traffic + load test with prod Zipf; game days.

**Q: Queue all checkouts?**  
A: Virtual waiting room extreme measure; communicate.

**Q: Consistency for order history?**  
A: Read-after-write in home region; global eventual.

**Q: Who flips shed?**  
A: IC with pre-auth flags.

**Q: What's success?**  
A: Checkout success + customer trust + controlled cost—not peak QPS record.

---

## Alternatives to Kill

| Alt | Why |
|-----|-----|
| One mega DB | Classic meltdown |
| Infinite HPA without quotas | Noisy neighbors / cost |
| Personalization always-on critical | Outages |
| "We'll stream everything via Kafka synchronously" | Wrong tool for page |

---

## LLD Touch (optional)

Not the point of this prompt—but cart item model, order state machine, reservation object if asked.

---

## 60-second Narrative

"10× Amazon.com is not one QPS number. We absorb browse at the edge, bulkhead PDP fragments with timeouts, scale search as its own plane, and **reserve capacity for cart/checkout** with idempotent orders and inventory leases. We shed recs before we risk purchase integrity, fight bots early, and prevent retry storms. For 100× we cell by marketplace/region and push composition outward. Success is checkout success rate and honest degradation—not vanity traffic."

---

## Extra Depth: Waiting Room Design

When checkout starts >> capacity: issue admit tokens; FIFO/lottery fair; keep browse open; expire tokens; never charge before admit. Extreme peak tool.

---

## Extra Depth: Edge Composition

ESI/fragment includes with independent cache policies; fail-open to empty section; signed URLs for private fragments.

---

## Extra Depth: Hidden Shared Fate

Enumerate: auth keys, certificate bundles, feature flag service, DNS, package registries for deploys, logging agents filling disks—capacity plan these too.

---

## Extra Depth: Cost Control Levers

1. +hit rate 2. −bot 3. −fanout 4. sample analytics 5. shed rich modules 6. cheaper search tier for peak 7. image format/quality adaptive.

---

## Extra Depth: Multi-Marketplace Cells

`.com`, `.co.uk`, `.de` isolation; shared platform code; separate data & configs; global brand SEV still needs central IC communications.

---

## Extra Depth: Observability at 10×

Tail sampling traces; high-cardinality careful; RED metrics per plane; business KPIs (checkout success) on same wall as tech.

---

## Extra Depth: Load Test Shape

Include: login storms, deal PDP, search head, add-to-cart bursts, checkout completes, bot patterns, dependency brownouts—not uniform random GETs.

---

## Closing Cheat Sheet

| Topic | Answer |
|-------|--------|
| Traffic | Split planes |
| Browse | Edge/cache |
| Buy | Isolated + idempotent |
| Failures | Timeouts/bulkheads |
| Peak | Shed order + freeze |
| Next | Cells 100× |
| Kill | Shared pools; no budgets |

---

*End of Amazon.com 10× Traffic design notes (Amazon SDE III prep).*
