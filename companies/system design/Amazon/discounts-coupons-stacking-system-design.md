# System Design: Discounts & Coupons (Stacking Rules)

> **Focus areas:** Coupon types · Eligibility · Exclusivity groups · Stacking combinatorics · Cart evaluation order · Fraud/abuse · Promo code inventory · Flash sales · Correctness under concurrency  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS types, explicit deal-breakers, deterministic pricing under contention  
> **Amazon lens:** Commerce ownership, pricing correctness as trust, marketplace seller promos vs Amazon promos, Prime Day–class flash traffic, auditability for finance

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

Goal: **bound a promotions engine**—compute a **deterministic, auditable** discount set for a cart under stacking/exclusivity rules, reserve scarce promo inventory under concurrency, and stop fraud without false-punishing good customers.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who creates promos? | Merchandising, sellers (marketplace), automated campaigns | Multi-tenant promo catalog; approval workflow |
| F2 | Coupon types? | % off, fixed amount, BOGO, free shipping, tiered, gift-with-purchase | Typed benefit calculators |
| F3 | Codes vs automatic? | Both: enter code + auto-apply best deals | Clip/claim + auto evaluator |
| F4 | Stacking? | Configurable: some stack, some exclusive | Exclusivity groups + priority |
| F5 | Eligibility? | User segment, Prime, first order, geo, SKU, category, min spend | Rule engine / predicates |
| F6 | Evaluation when? | Cart view (estimate) + checkout (commit) | Quote vs reserve vs redeem |
| F7 | Inventory? | Limited redemptions globally / per user / per code | Atomic counters / ledgers |
| F8 | Flash sales? | Huge spikes; fair-ish allocation | Reservation TTLs; sharding |
| F9 | Fraud? | Code sharing, bot clip, reseller abuse | Risk scores; velocity; device |
| F10 | Audit? | Why this discount applied; finance reconcile | Explanation + immutable ledger |
| F11 | Currency/tax? | Discount before/after tax per market | Explicit pricing pipeline order |
| F12 | Marketplace? | Seller coupon vs Amazon coupon interactions | Owner scopes + stack policies |

**MVP functional scope (lock with interviewer):**

1. Promo/coupon **catalog** with versions and schedule windows.  
2. Types: percent, fixed, free shipping; optional BOGO as extension.  
3. Eligibility predicates (catalog, cart min, user segment, first-order).  
4. **Exclusivity groups** + stackability flags + priority.  
5. Deterministic **cart evaluation** producing line/cart discounts + explanation.  
6. Code **claim/redeem** with per-user and global inventory.  
7. **Quote** (soft) vs **checkout reserve** (hard) vs **capture on order**.  
8. Basic fraud velocity limits.  
9. Admin + audit log.  
10. Flash-sale safe counters.

**Out of MVP (explicitly defer):**

- Full offer personalization ML ranker (can plug later)  
- Cross-channel coupons (in-store POS) — design hooks only  
- Arbitrary Turing-complete promo scripts in production path  
- Guaranteeing globally optimal combinatorial search at unbounded promo count without caps  
- Cryptocurrency / unusual tender stacking

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Cart evaluate latency | Interactive | p99 < 50–100ms in-region (cached catalog) |
| N2 | Checkout reserve | Strong correctness | Atomic inventory; no oversell beyond policy |
| N3 | Determinism | Same cart+promos → same $ | Pure eval with version pins |
| N4 | Availability | Cart soft-fail graceful | Degrade: fewer autos; never wrong money silently |
| N5 | Auditability | Finance-grade | Immutable application records |
| N6 | Flash scale | Prime Day class | See 1,000×; reservations hold |
| N7 | Consistency | Inventory strong; catalog eventual OK | Pin promo version at checkout |
| N8 | Security | No forgeable client discounts | Server-side authority only |
| N9 | Multi-region | Global storefronts | Regional pricing cells; global code inventory careful |
| N10 | Scale | Through 1,000× evaluate QPS | Progressive table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User applies `SAVE10` → eligible → stacks with auto free-shipping → cart totals update with explanation.  
2. Exclusive brand coupon blocks sitewide % when both present → higher priority wins (policy).  
3. Flash code 1000 uses → 1000 successful reserves; 1001st rejected.  
4. User abandons checkout → reservation TTL expires → inventory returns.  
5. Order placed → redeem captured; code use ledger finalized.  
6. Seller coupon on seller items only; Amazon coupon stacks per rules.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two tabs checkout same single-use code | One wins; other fails at reserve |
| Cart changes after quote | Re-evaluate; invalidate stale quote token |
| Promo ends mid-checkout | Pin version/window at reserve; or revalidate—**pick one** (recommend revalidate + clear message) |
| Floating point money | Integer minor units (cents) only |
| Stacking creates negative price | Floor at 0 per line/cart; policy for cost floor |
| Ineligible SKU added after code | Drop or keep code with partial apply + explain |
| Coupon for category, item removed | Recalc |
| Bot floods evaluate API | Rate limit; cache; CAPTCHA on claim |
| Clock skew on start/end | Server time; schedule with safety margins |
| Partial shipment refund | Reverse discount allocation proportionally (policy) |
| Currency convert mid-session | Sticky currency on quote |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active promos in catalog | 10K | 100K | 1M | 10M |
| Auto-considered promos / cart | 20 | 50 | 100 | 200 (capped) |
| Codes issued (unique) | 5M | 50M | 500M | 5B |
| Cart **evaluate** QPS peak | ~5K | ~50K | ~500K | ~5M |
| Checkout **reserve** QPS peak | ~500 | ~5K | ~50K | ~500K |
| Flash SKU/code contention hot keys | tens | hundreds | thousands | tens of thousands |
| Orders with ≥1 promo / day | 2M | 20M | 200M | 2B |
| Fraud checks / evaluate | ~5K | ~50K | ~500K | ~5M |
| Admin publish QPS | ~10 | ~50 | ~200 | ~1K |

**What each jump forces:**

- **10×:** Versioned promo docs; Redis inventory; deterministic evaluator library; quote tokens.  
- **100×:** Shard counters; catalog CDN/cache; exclusivity pre-index; risk service async+sync tiers; reservation service.  
- **1,000×:** Cell by marketplace/region; hot-key inventory spraying; evaluate horizontal scale-out; flash “lottery/queue” for ultra-hot codes; offline combinatorial approx with hard caps.

### 1.5 Etc. (Constraints & Assumptions)

- **Server is source of truth** for price; client suggestions are hints.  
- Money in **integer minor units**.  
- Stacking search is **bounded** (N promos capped; heuristics + priority)—say this explicitly.  
- Amazon trust: **wrong discount** (over-discount) is often worse than denying a promo. Prefer fail-closed on inventory/rules ambiguity.  
- Marketplace: seller-funded vs Amazon-funded discounts need **ledger attribution**.

**Scope statement:**

> Design a discounts & coupons platform: typed promos, eligibility, exclusivity/stacking rules, deterministic cart evaluation with explanations, scarce code inventory with reserve/capture, fraud controls, and flash-sale concurrency safety—from ~5K evaluate QPS through 10× / 100× / 1,000× (~5M evaluate QPS), with checkout correctness preferred over optimistic oversell.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Cart evaluate (read-mostly) | 5K | 5M | Cache catalog; pure CPU |
| Clip/claim code | 200 | 200K | Write-ish |
| Checkout reserve | 500 | 500K | Strong consistency path |
| Capture / finalize on order | 400 | 400K | With order TX |
| Release / TTL expiry | 100 | 100K | Async |
| Fraud score | 5K | 5M | Tiered; cache decisions |
| Admin publish | 10 | 1K | Invalidates caches |

**Critical:** Evaluate QPS ≫ reserve QPS. Optimize read path separately from inventory path. Hot flash codes make **reserve** the hard bottleneck, not evaluate.

### 2.2 Storage

```text
Promo definition ~2–20 KB (rules JSON)
1M promos × 10 KB = 10 GB catalog (fits comfortably; cache hot subset)
Redemption ledger: 200M orders/day × 2 promos × 200 B ≈ 80 GB/day at 100×
1,000×: 2B orders/day × 2 × 200 B = 800 GB/day ledger-ish

Unit check: 2e9 × 2 × 200 = 8e11 B = **800 GB/day** (not PB)
Code inventory rows: 5B codes × 50 B = 250 GB → need hierarchical (campaign counter + sparse per-code)
```

### 2.3 Compute (evaluation)

```text
Evaluate cost ≈ O(L × P_eff) with L line items, P_eff candidate promos after index
Example: L=30, P_eff=50, rules cheap → microseconds–low ms
Danger: naive 2^P stacking subsets → exponential; **must bound**
```

### 2.4 Memory

```text
Hot promo cache per region: 50K promos × 10 KB = 500 MB
Per-user clipped coupons: Redis 100M users × 5 coupons × 50 B = 25 GB (shard)
Inventory hot keys: spray across N counters for flash
```

### 2.5 Flash math

```text
Code with 10K global uses, 100K concurrent checkouts in 10s
Reserve QPS spike 10K/s on one logical key → shard inventory
TTL 10 min; abandoned 70% → replenish via expiry worker
```

### 2.6 Critical bottlenecks

1. Hot promo inventory single counter  
2. Exponential stacking search  
3. Catalog cache stampede on publish  
4. Fraud service latency on checkout path  
5. Cross-region double redeem  
6. Finance reconciliation lag vs real-time promise  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Promo (promo_id, version, owner=amazon|seller_id, schedule, status)
Benefit (PERCENT_OFF | FIXED_OFF | FREE_SHIPPING | BOGO | ...)
Constraint / Predicate (catalog, cart, user, geo, device, ...)
ExclusivityGroup (group_id, mode=MUTEX|STACKABLE_LIMIT)
StackPolicy (priority, combinable_with[], max_stack_depth)
CouponCode (code, promo_id, inventory_mode, per_user_limit)
Clip (user_id, promo_id|code, clipped_at)   -- optional wallet
Quote (quote_id, cart_hash, promo_versions[], discounts[], expires)
Reservation (reservation_id, code/promo, user, units, expires)
Redemption (order_id, promo_version, amount, funding_source)
```

### 3.2 Pricing pipeline order (lock early)

```text
1. List price / deal price (item-level deals)
2. Seller/item coupons
3. Cart-level coupons / codes
4. Shipping fees → shipping promos
5. Tax (market-specific: discount before/after tax)
6. Tender (gift cards) — usually after discounts
```

**Say aloud:** tax interaction is market-specific; state assumption (e.g. discount on pre-tax merchandise subtotal).

### 3.3 Coupon types (benefit calculators)

| Type | Input | Output |
|------|-------|--------|
| PERCENT_OFF | % , basis (eligible subtotal) | cents off, capped |
| FIXED_OFF | amount | cents off, ≤ basis |
| FREE_SHIPPING | shipping quote | shipping → 0 or capped |
| BOGO | buy X get Y | line discounts allocation |
| TIERED | thresholds | pick matching tier |

Allocation: when cart-level discount spans lines, allocate by **eligible line weight** for refunds later.

### 3.4 Eligibility

```text
eligible = schedule_active
  AND user_predicates (Prime, segment, first_order, new_device…)
  AND cart_predicates (min_subtotal, min_qty)
  AND catalog_predicates (ASIN/SKU/category/brand, exclusions)
  AND geo/currency
  AND not in suppressions (fraud, legal)
  AND inventory_remaining (soft check)
```

Index promos by **trigger dimensions** (brand, category, code) so evaluation doesn’t scan 1M promos.

### 3.5 Exclusivity groups & stacking combinatorics

```text
Each promo ∈ zero or more ExclusivityGroups
Group modes:
  MUTEX — at most one promo from group
  LIMIT_K — at most K
Stack edges:
  promo A combinable_with B (symmetric closure computed at publish)
Priority:
  explicit rank; tie-break by discount amount or promo_id stable sort
```

**Evaluation algorithm (practical):**

1. Generate **candidates** via indexes + clipped codes + entered codes.  
2. Filter eligibility.  
3. Build conflict graph from exclusivity groups.  
4. Search **bounded** combinations: greedy by priority, plus limited beam/K-best for auto-apply “best for customer” within cap (e.g. 2^12 or beam 100).  
5. Choose policy objective: `MAX_CUSTOMER_SAVINGS` under constraints (common) or `MERCHANT_PRIORITY`.  
6. Emit selected set + **explanation** (why others rejected).

**Deal-breaker:** “Try all subsets of 40 promos” in request path (2^40).

### 3.6 Cart evaluation order (deterministic)

```text
function evaluate(cart, user, codes[], ctx):
  pin = loadPromoVersions(now or ctx.pin)
  candidates = indexLookup(cart, user) ∪ resolveCodes(codes) ∪ clipped(user)
  eligible = filter(candidates, cart, user, pin)
  selected = stackSearch(eligible, policies, objective)
  amounts = applyBenefitsInPipelineOrder(cart, selected)
  assert totals >= floors
  return Quote{cart_hash, versions, selected, amounts, explain, exp}
```

Same inputs → same outputs. **No wall-clock randomness** inside eval (fraud jitter stays outside).

### 3.7 Quote vs reserve vs capture

| Phase | Strength | Purpose |
|-------|----------|---------|
| Evaluate/Quote | Soft | UX totals; may race |
| Reserve at checkout start | Hard hold | Inventory + single-use codes |
| Capture on order commit | Final | Ledger + finance |
| Release | TTL / cancel | Return inventory |

```text
Quote token signed: HMAC(cart_hash, promo_versions, amounts, exp)
Checkout: revalidate token OR re-evaluate; then reserve; then place order; capture
```

**Policy choice:** Always **re-evaluate at checkout** (safer) even if quote exists; quote is UX optimization.

### 3.8 Promo code inventory

| Mode | Semantics | Implementation |
|------|-----------|----------------|
| Unlimited | No global cap | Per-user limits only |
| Global N | N total redemptions | Atomic counter / sharded counters |
| Unique codes | 1 code → 1 redeem | Row state UNUSED→RESERVED→USED |
| Per-user N | N per shopper | `(promo,user)` counter |
| Budget cents | Fund cap | Atomic budget ledger |

**Sharded counter pattern (flash):**

```text
logical remaining R
N shards: r_i with sum(r_i) = R
reserve: pick random shard; CAS decrement; if empty try others
slight unfairness OK; avoids single hot key
```

### 3.9 Fraud & abuse

```text
Signals: velocity (codes tried/min), device/browser, IP, account age,
         refund-after-promo pattern, reseller networks, code dump lists
Actions: challenge, block code claim, require sign-in, delay, deny stack
Path: sync cheap rules on evaluate/reserve; async ML enrichment
```

**Deal-breaker:** trusting client-sent `discount_amount`.

### 3.10 Concurrency correctness

```text
Single-use code:
  UPDATE codes SET state='RESERVED', reservation_id=?, exp=?
  WHERE code=? AND state='UNUSED'
  -- 1 row affected wins

Global counter:
  sharded CAS or Redis DECR with check >=0; compensating INCR on release

Checkout + order:
  reserve in Promo Inventory service → order service commit → capture
  Saga: if order fails, release reservation
```

Idempotency keys on reserve/capture tied to `checkout_attempt_id` / `order_id`.

### 3.11 Multi-region

| Concern | Approach |
|---------|----------|
| Catalog | Replicate globally; versioned; regional cache |
| Evaluate | Regional, read local cache |
| Single-use / tight inventory | **Home region** or global strongly consistent store for that promo |
| Soft auto promos unlimited | Easy multi-region |
| Flash global code | One home inventory cell; other regions proxy reserves |

**Deal-breaker:** multi-region independent DECR without coordination on N=1000 flash codes.

### 3.12 Storage trade-offs

| Component | Choice | Deal-breaker |
|-----------|--------|--------------|
| Promo catalog | Versioned docs + index | In-place mutable rules mid-flight without version |
| Inventory | Redis/DB atomic + ledger | `count++` in app memory |
| Quotes | Signed token / short TTL store | Trust client totals |
| Redemptions | Append-only ledger | Overwrite history |
| Fraud | Tiered cache | Sync call to heavy ML on every cart keystroke |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
┌────────────┐     ┌──────────────┐     ┌─────────────────────┐
│ Storefront │────►│ Cart Service │────►│ Promo Evaluation    │
│  / Checkout│     │              │     │  (pure workers)     │
└────────────┘     └──────┬───────┘     └──────────┬──────────┘
                          │                        │
                          │                        ▼
                          │               ┌─────────────────┐
                          │               │ Promo Catalog   │
                          │               │ Cache + Indexes │
                          │               └─────────────────┘
                          ▼
                 ┌──────────────────┐     ┌─────────────────┐
                 │ Reserve / Redeem │────►│ Inventory Store │
                 │   Service        │     │ (sharded CAS)   │
                 └────────┬─────────┘     └─────────────────┘
                          │
                          ▼
                 ┌──────────────────┐     ┌─────────────────┐
                 │ Order Service    │────►│ Redemption      │
                 │  (capture/saga)  │     │ Ledger          │
                 └──────────────────┘     └─────────────────┘

┌────────────┐   publish    ┌─────────────────┐
│ Merch/Admin│─────────────►│ Promo Control   │──► cache invalidate
│ Seller tools│             │ Plane           │
└────────────┘              └─────────────────┘

┌────────────┐              ┌─────────────────┐
│ Fraud/Risk │◄────────────►│ Evaluate/Reserve│
└────────────┘   signals    └─────────────────┘
```

### 4.2 Evaluation internals

```text
Codes entered / clipped → Resolve → Candidates
Cart lines ─────────────► Catalog Index ──┘
User profile ───────────► Segment match ──┘
                              │
                              ▼
                         Eligibility filter
                              │
                              ▼
                      Stack / exclusivity search
                              │
                              ▼
                    Apply benefits (pipeline order)
                              │
                              ▼
                    Quote + Explanation tree
```

### 4.3 Flash sale inventory

```text
        Reserve(code, user, checkout_id)
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
  Unique code row CAS     Sharded global counters
        │                       │
        └───────────┬───────────┘
                    ▼
            Reservation{TTL}
                    │
        Order success ──► Capture ──► Ledger
        Timeout/cancel ──► Release ──► INCR/UNUSED
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Failure modes

| Failure | Risk | Mitigation |
|---------|------|------------|
| Over-discount bug | Margin loss / trust | Golden carts; shadow eval; floors; canary rules |
| Oversell limited code | Customer anger / legal | Atomic reserve; fail-closed |
| Undersell (counter leak) | Leftover unused | Reconcile job; alerting on drift |
| Catalog cache stale | Wrong eligibility | Version pins; short TTL; push invalidation |
| Fraud false positive | Lost sales | Graduated challenges; appeal path |
| Partial outage of inventory | Checkout fails | Fail-closed for limited; allow unlimited autos |
| Double capture | Double count budget | Idempotent capture by order_id |
| Refund mis-allocation | Finance drift | Store per-line allocation |

#### 5.1.2 Consistency model

- Evaluation: **deterministic function** of pinned inputs.  
- Inventory: **strong** for limited promos (linearizable reserve).  
- Catalog: **eventually consistent** to stores + **version pin** at checkout.  
- Fraud: **best-effort** enrichment; default-allow vs default-deny by risk tier.

#### 5.1.3 Money correctness rules

```text
1. Integer cents everywhere
2. Line floors: discounted_line >= 0
3. Cart floor: merchandise >= 0; shipping >= 0
4. Allocation must sum to cart-level discount
5. Capture amount ≤ reserved amount
6. Refunds use original allocation ratios
```

#### 5.1.4 Amazon ownership themes

- **Customer Obsession:** Clear explanations (“Brand coupon can’t combine with Save20”).  
- **Ownership:** Promo on-call owns oversell & wrong-price Sevs with retail/finance.  
- **Dive Deep:** Trace `quote_id` → `reservation_id` → `order_id` → ledger lines.  
- **Bias for Action vs Correctness:** For money, correctness wins—ship deny with message over silent wrong price.  
- **Frugality:** Bound auto-considered promos; don’t run ML on every keystroke.

### 5.2 Scalability

#### 5.2.1 Progressive scale

| Scale | Moves |
|-------|-------|
| 10× | Cached catalog; Redis per-user clips; single-region atomic inventory |
| 100× | Shard inventory; promo indexes; evaluate horizontally; risk tiering |
| 1,000× | Regional cells; hot-key spraying; flash admission control; offline candidate reduction |

#### 5.2.2 Candidate reduction (critical at 1,000×)

```text
Precompute: brand → promo_ids, category → promo_ids, segment → promo_ids
At evaluate: union indexes for cart entities → intersect schedule bitmap
Hard cap P_eff (e.g. 100) with priority drop of low-rank autos
Codes entered always included
```

#### 5.2.3 Hot-key inventory spraying

```text
R=1_000_000, N=100 shards → ~10_000 each
Reserve: random shard; if empty, probe K others; else FAIL_SOLD_OUT
Trade-off: may fail early while residual in other shards (heal with balancer)
```

For **unique codes**, partition by `hash(code)` across DB shards—natural distribution.

#### 5.2.4 Flash admission control

When reserve error rate spikes:

```text
Edge: token bucket / lottery queue for specific promo_id
Evaluate still works (shows “selling out”)
Reserve path protected
```

Similar to warehouse “door” patterns on Prime Day.

### 5.3 Maintainability

#### 5.3.1 Rule authoring vs execution

- Authors use constrained DSL / form UI → compiled to predicates.  
- **No arbitrary scripts** on checkout path in MVP.  
- Publish validates: cycles in stack graph, impossible constraints, money floors.

#### 5.3.2 Versioning & rollback

```text
promo_id + version immutable once published
Checkout pins versions
Rollback = publish new version reverting fields
Audit: who/when/why
```

#### 5.3.3 Testing strategy

- Property tests: non-negative totals; allocation sums; exclusivity honored.  
- Golden carts per marketplace.  
- Concurrency tests: 10K threads one code.  
- Chaos: kill reserve mid-checkout → saga release.  
- Shadow mode: new stack engine vs old on % traffic.

#### 5.3.4 Observability

| Metric | Why |
|--------|-----|
| Eval p99 / error | UX |
| Reserve success / sold-out / conflict | Flash health |
| Avg discount rate | Margin |
| Oversell incidents | Sev |
| Fraud block rate | Abuse |
| Explanation “rejected exclusive” counts | Merch tuning |
| Cache hit rate | Scale |

Structured log: `promo_versions`, `selected[]`, `rejected_reasons[]`, `cart_hash`.

#### 5.3.5 Finance & funding

```text
Redemption ledger fields:
  amount_cents, funding=AMAZON|SELLER|COFUNDED,
  seller_id?, campaign_id, tax_treatment
Daily reconcile vs order payments
```

---

## 6. Wrap-Up

### 6.1 MVP build order

1. Promo types + versioned catalog + cache.  
2. Eligibility + exclusivity + deterministic evaluator + explanations.  
3. Quote API for cart.  
4. Reserve/capture for limited codes.  
5. Fraud velocity.  
6. Flash sharding + TTLs.  
Then: BOGO, budgets, multi-region homes, seller tooling.

### 6.2 Trade-offs to say aloud

| Decision | Trade-off |
|----------|-----------|
| Re-evaluate at checkout | Extra CPU; fewer wrong charges |
| Bounded stack search | May miss global optimum; predictable latency |
| Fail-closed inventory | Lost sales vs oversell |
| Sharded counters | Rare early sold-out vs hot key death |
| Server authority | Can’t do fully offline discounts |
| Greedy+beam vs ILP | Engineering simplicity vs optimal stack |

### 6.3 Risks

- Merch creates contradictory exclusivity → support load (validate at publish).  
- Marketplace disputes on funding.  
- Cross-border tax misconfiguration.  
- Refunds after partial fulfill.  
- Promo DSL creep toward general programming.

### 6.4 60-second pitch

> Promos are versioned documents with typed benefits, eligibility predicates, and exclusivity groups. Cart evaluation is a **deterministic, server-side** function that selects a bounded stack-optimal set and explains rejects. Interactive cart uses soft quotes; checkout **re-validates** and **atomically reserves** scarce inventory (sharded for flash), then captures into an immutable redemption ledger on order success with saga release on failure. Fraud is tiered. We scale evaluate horizontally with indexes/caps, and scale inventory with CAS/sharding and home regions for global limited codes—optimizing for **no silent wrong price** and **no oversell**.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & types

**Q: Coupon vs promotion vs deal?**  
A: Deal often item price rewrite; coupon is conditional benefit; unify under Promo with different applicators.

**Q: BOGO complexity?**  
A: Need line selection policy (cheapest free vs customer choice); allocate discount to gift lines for refunds.

**Q: Free gifts inventory?**  
A: Couples to warehouse inventory—reservation may need dual reserve (promo use + SKU stock).

**Q: Subscription coupons?**  
A: Recurring redemptions with billing cycle limits; different from one-shot codes.

### 7.2 Stacking

**Q: How to present stacking to merch?**  
A: Exclusivity groups + “combinable” matrix; simulate tool with sample carts.

**Q: Best discount vs merchant intent?**  
A: Configurable objective; Amazon often maximizes customer savings within merch constraints.

**Q: Two MUTEX groups overlapping?**  
A: Treat as conflict graph; search must satisfy all groups.

**Q: Stack depth limit?**  
A: Yes (e.g. max 3)—UX and abuse control.

**Q: Exponential blowup?**  
A: Cap candidates; greedy by priority; optional beam search; never full power set of 40.

### 7.3 Evaluation order

**Q: Percent then fixed vs fixed then percent?**  
A: Pipeline must be fixed and documented; versioned. Changing order mid-year is a finance event.

**Q: Item deal + coupon?**  
A: Usually coupon applies to deal price (basis=current); state assumption.

**Q: Shipping promo with free-shipping threshold?**  
A: Recompute shipping after merchandise discounts if policy says so—explicit flag.

### 7.4 Eligibility

**Q: First-order coupon abuse?**  
A: Identity graph (payment/device/address); risk denies; not only `order_count==0`.

**Q: Category exclusion for already-discounted items?**  
A: Predicate `not already_on_lightning_deal` etc.

**Q: Geo eligibility?**  
A: Ship-to address at checkout; cart estimate may use cookie locale with warning.

### 7.5 Inventory & flash

**Q: Soft check at evaluate vs hard at reserve?**  
A: Soft for UX; hard authoritative at reserve. Show “almost gone” heuristics carefully (don’t lie).

**Q: Reservation TTL length?**  
A: Balance abandon vs fairness (5–15 min typical); align with checkout session.

**Q: Why sharding causes false sold-out?**  
A: Residual on other shards; background rebalance; or fallback scan K shards.

**Q: Unique code generation?**  
A: High-entropy; avoid predictable sequences; store hashed codes at rest optional.

**Q: Global budget $1M?**  
A: Atomic budget ledger in cents; reserve amount not just count.

### 7.6 Concurrency & sagas

**Q: Order succeeds, capture fails?**  
A: Outbox/retry capture idempotently; order still valid; promo ledger must catch up.

**Q: Reserve succeeds, order fails?**  
A: Release sync or TTL; measure leak.

**Q: Two codes, one inventory fails?**  
A: Atomic multi-reserve (all-or-nothing) or ordered reserve with compensating release—prefer all-or-nothing API.

**Q: Idempotent reserve?**  
A: Keyed by `checkout_attempt_id`; same key returns same reservation.

### 7.7 Fraud

**Q: Code sharing on forums?**  
A: Per-user limits; one-time unique codes; risk on velocity of distinct users per code for “secret” promos.

**Q: Evaluate API scraping for price?**  
A: Auth, rate limits, bot management; don’t expose admin-only promos.

**Q: Self-preferencing seller abuse?**  
A: Marketplace policy engine; separate from pure stacking math.

### 7.8 Multi-region

**Q: Can EU and US both redeem last global code?**  
A: Not if home inventory is linearizable; yes if wrongly dual-active without coord—**don’t**.

**Q: Catalog publish lag?**  
A: Version pin; checkout fetches authoritative version if cache older than skew budget.

### 7.9 Refunds & cancellations

**Q: Partial cancel?**  
A: Restate allocation; claw back proportional discount; restore inventory only if policy (usually **don’t** restore single-use after fulfill).

**Q: Price adjustment post-order?**  
A: New ledger entries; don’t mutate old redemption rows.

### 7.10 Marketplace funding

**Q: Who pays?**  
A: `funding_source` on redemption; seller billing cycle; Amazon coop campaigns cofunded split rules.

**Q: Seller coupon stacked with Amazon?**  
A: Policy matrix by owner; default often allow if not same exclusivity group.

### 7.11 API design

**Q: Idempotency on apply code?**  
A: Apply is usually cart mutation with user session; reserve uses explicit keys.

**Q: Explanation API?**  
A: Machine codes + localized messages: `EXCLUSIVE_WITH_APPLIED`, `MIN_SPEND_NOT_MET`, `INVENTORY_EMPTY`.

### 7.12 Estimation traps

**Q: 2B orders × 2 redemptions × 200B = 800 TB/day?**  
A: **800 GB/day**. 2e9×2×200=8e11 B=800 GB.

**Q: Evaluate 5M QPS each scanning 1M promos?**  
A: Impossible—indexes + caps mandatory.

**Q: Single Redis key for Prime Day code?**  
A: Hot key meltdown—shard/spray.

### 7.13 Interview traps

**Q: “Client applies 20% and sends total.”**  
A: Never; server recomputes.

**Q: “Floating point is fine.”**  
A: Integer cents.

**Q: “Optimal stacking via ILP each request.”**  
A: Latency/ops risk; bound heuristics unless P tiny.

**Q: “Eventual consistency for single-use codes.”**  
A: Oversell—unacceptable for scarce inventory.

**Q: “One mega if-else for all promos.”**  
A: Unmaintainable; data-driven predicates.

### 7.14 Ownership scenarios

**Q: Sev: 15% over-discount sitewide.**  
A: Kill switch promo versions; pin previous; recompute open carts; finance impact estimate; root-cause eval diff.

**Q: Flash sold out but counter shows 2K left.**  
A: Shard imbalance / reservation leak; reconcile; thaw shards; fix TTL worker.

**Q: Customer claims coupon should stack.**  
A: Pull explanation tree; verify exclusivity config; merch vs bug.

### 7.15 Comparisons

**Q: Rules engine (Drools) vs custom?**  
A: Custom deterministic pipeline usually wins for latency/audit at commerce core; rules engines can be control-plane compilers.

**Q: Coupon service vs price service?**  
A: Price/deals may own item price; coupons own conditional benefits—clear boundary, single pipeline orchestration.

### 7.16 Misc deep cuts

**Q: Auto-apply?** A: Disclose + removable; re-eval if removing a code changes the stack.  
**Q: Code enumeration?** A: High entropy, rate limits, delay, monitor fail ratios.  
**Q: Cache stampede on publish?** A: Epoch bump + singleflight warm; stagger.  
**Q: ML personalization?** A: Rank eligible autos only—never bypass exclusivity/inventory.  
**Q: Gift cards?** A: Tender ≠ coupon; don’t model as the same stack layer.  
**Q: Debug rejects?** A: Reason codes on quote + admin simulator with pinned versions.  
**Q: Invariants to test?** A: Exclusivity, non-negative, allocation sum, capture≤reserve, golden determinism.  
**Q: Partial eligibility?** A: Apply to matching lines; show partial apply in UX.  
**Q: Kill switches?** A: Per-promo/group, autos-off, inventory freeze—all audited.  
**Q: Promo spaghetti?** A: Publish lint, golden cart CI, clear merch ownership, constrained DSL.

**Eval p99 budget sketch:** cache 5 + candidates 10 + eligibility 20 + stack 40 + apply 10 + fraud 10 ≈ 100ms.

---

## 8. Appendices

### 8.1 Schema sketches

```text
promos(promo_id, owner_type, owner_id, status, created_at)
promo_versions(promo_id, version, schedule_start, schedule_end,
               benefit_json, predicates_json, exclusivity_groups[],
               priority, stack_policy_json, published_at, immutable)
promo_indexes(dimension, key, promo_id, version)  -- serving index
codes(code_hash, promo_id, state, reservation_id, reserved_until, used_by, used_order)
inventory(promo_id, shard, remaining, budget_remaining_cents)
clips(user_id, promo_id, clipped_at)
reservations(reservation_id, checkout_id, user_id, items_json, expires_at, state)
redemptions(redemption_id, order_id, promo_id, version, amount_cents,
            funding, allocation_json, created_at)
  UNIQUE(order_id, promo_id)
eval_audit(quote_id, cart_hash, result_json, at)  -- sampled/TTL
```

### 8.2 API sketches

```text
POST /v1/cart/evaluate
{
  "cart_id": "c1",
  "lines": [{"sku":"A","qty":1,"unit_price_cents":2000,"brand":"X"}],
  "codes": ["SAVE10"],
  "user_ctx": {"user_id":"u1","prime":true,"segment":["new"]}
}
→ {
  "quote_id": "q1",
  "totals": {"subtotal":2000,"discount":200,"shipping":0,"tax":...},
  "applied": [{"promo_id":"p1","version":3,"amount":200}],
  "rejected": [{"code":"SAVE10","reason":"EXCLUSIVE_WITH","other":"p2"}],
  "exp": 1710000600
}

POST /v1/checkout/reserve
Idempotency-Key: chk_123
{ "quote_id":"q1", "checkout_id":"chk_123" }
→ { "reservation_id":"r1", "expires_at": "...", "applied":[...] }

POST /v1/checkout/capture
{ "reservation_id":"r1", "order_id":"o9" }
→ { "ok": true }
```

### 8.3 Exclusivity examples

```text
Group SITEWIDE_PERCENT: MUTEX
  - SAVE10 (10% sitewide)
  - SAVE20 (20% sitewide)

Group BRAND_X: MUTEX
  - BRANDX15

Stack policy:
  BRANDX15 combinable with free shipping
  BRANDX15 NOT combinable with SITEWIDE_PERCENT group
```

### 8.4 Stack search pseudocode

```text
function stackSearch(eligible, objective):
  eligible = sortBy(priority desc, promo_id asc)
  best = {}
  beam = [set()]
  for promo in eligible:
    new_beam = []
    for S in beam:
      new_beam.add(S)
      if canAdd(S, promo):           // exclusivity + stack edges + depth
        new_beam.add(S ∪ {promo})
    beam = topK(new_beam, K, objectivePreview)
  return argmax(beam, objectiveExact)
```

### 8.5 Reservation state machine

```text
UNUSED → RESERVED → USED
           ↓
        EXPIRED → UNUSED   (unique codes)
Counter: remaining-- on RESERVE; ++ on RELEASE; capture no further change
```

### 8.6 Allocation example

```text
Eligible lines: L1=3000, L2=1000 (cents)
Cart coupon FIXED 400 off
Allocation by weight:
  L1: 400 * 3000/4000 = 300
  L2: 400 * 1000/4000 = 100
Sum=400 ✓
```

### 8.7 Fraud rule examples

| Rule | Action |
|------|--------|
| >10 code fails / 5 min / user | Temporary claim block |
| New account + high-value limited code | Step-up auth |
| Same device 20 accounts / day | Risk review |
| Code on public pastebin list | Invalidate / rotate |

### 8.8 Glossary

| Term | Meaning |
|------|---------|
| Clip | User saves promo to wallet before cart |
| Quote | Soft evaluation result with TTL |
| Reserve | Hard inventory hold |
| Capture | Final redemption on order |
| Exclusivity group | Mutual exclusion / limit set |
| Funding source | Who pays the discount |
| Basis | Amount % applies to |
| Beam search | Bounded heuristic stack search |
| Home inventory | Single region of truth for scarce codes |

### 8.9 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Types, eligibility, mutex groups, server eval, integer money |
| 10× | Quotes, reserve/capture, Redis inventory, explanations |
| 100× | Indexes, shard counters, fraud velocity, saga release |
| 1000× | Cells, hot-key spray, admission control, candidate caps |

### 8.10 Publish validation checklist

- [ ] Schedule sane  
- [ ] Benefit caps present  
- [ ] Exclusivity graph no paradox warnings  
- [ ] Predicate indexes generated  
- [ ] Funding source set  
- [ ] Per-user limits set for public codes  
- [ ] Simulation on golden carts passes  
- [ ] Kill switch wired  

### 8.11 Operator runbooks

1. Oversell limited campaign  
2. Wrong-price / over-discount  
3. Flash hot-key latency  
4. Catalog epoch stampede  
5. Fraud false-positive surge  
6. Refund allocation mismatch  

### 8.12 Worked scale (100×)

```text
Evaluate 500K QPS × 50 candidates × cheap rules → CPU-bound fleet
Reserve 50K QPS — most unlimited no-ops; flash subset needs shard CAS
Ledger 200M promo-orders/day × 2 × 200 B ≈ 80 GB/day
```

### 8.13 Worked scale (1,000×)

```text
Evaluate 5M QPS → many cells; aggressive caching of segment bitsets
Global flash code 1M uses in 1 minute → ~17K reserves/s sustained;
  design for 10× spike → ~170K/s with sharded counters + admission
Do not put that on one Postgres row
```

### 8.14 Interview “say this” summary

> Server-side deterministic evaluation with version pins; exclusivity groups and bounded stacking search; soft quotes for UX; strong reserve/capture for scarce inventory; integer money with line allocation; fraud tiering; flash via sharded counters and TTLs; multi-region homes for global limited codes; always optimize to avoid silent wrong prices and oversell.

### 8.15 Pseudocode: reserve

```text
function reserve(checkout_id, user, selected[]):
  idem = load(checkout_id)
  if idem: return idem.reservation
  rids = []
  try:
    for item in selected ordered_by(promo_id):  // deadlock-free order
      ok = inventory.reserve(item, user, checkout_id, ttl=10m)
      if !ok: throw SoldOut(item)
      rids.append(item)
    rec = saveReservation(checkout_id, rids)
    return rec
  catch:
    releaseAll(rids)
    throw
```

### 8.16 Pseudocode: eligibility

```text
function isEligible(promo, cart, user, now):
  v = promo.version
  if now < v.start or now >= v.end: return false, SCHEDULE
  if !matchUser(v.user_preds, user): return false, USER
  if !matchCart(v.cart_preds, cart): return false, CART
  basisLines = matchCatalog(v.catalog_preds, cart.lines)
  if basisLines empty and needs_catalog: return false, CATALOG
  if softInventory(promo) == 0: return false, INVENTORY
  return true, basisLines
```

### 8.17 Explanation tree (example JSON)

```text
{
  "applied": [{"promo_id":"BRANDX15","amount":450}],
  "rejected": [
    {"promo_id":"SAVE20","reason":"EXCLUSIVE_GROUP","group":"SITEWIDE_PERCENT",
     "conflict_with":"BRANDX15"},
    {"code":"WELCOME5","reason":"NOT_FIRST_ORDER"}
  ]
}
```

### 8.18 Tax interaction note

```text
US-like assumption for interview:
  taxable_base = merchandise_after_discounts (+ shipping taxable rules vary)
EU VAT display quirks may differ — call out “confirm with tax service”
Never invent tax law; define interface to Tax Service
```

### 8.19 Security checklist

- [ ] Ignore client discount amounts  
- [ ] Signed quotes optional; always revalidate  
- [ ] Authorize seller to only their promos  
- [ ] Rate-limit code guess  
- [ ] Audit publishes  
- [ ] Encrypt/hash codes at rest if sensitive  

### 8.20 Reliability test plan

1. 5K concurrent reserves on N=1000 global → exactly 1000 USED.  
2. Checkout crash after reserve → TTL release.  
3. Double capture same order_id → one ledger row.  
4. MUTEX pair never both applied in 1M fuzz evals.  
5. Publish mid-checkout → pin/revalidate behavior as designed.  
6. Shard residual reconciler restores stranded counts.  

### 8.21 Final trap table

| Trap | Pushback |
|------|----------|
| Client-trusted totals | Fraud / wrong price |
| Float money | Rounding exploits |
| Full subset search | Latency melt |
| Single counter flash | Hot key |
| Eventual single-use | Oversell |
| Mutable live promo | Non-determinism |
| No explanations | Support nightmare |
| 2B×400B=800TB/day ledger | **800GB/day** |

### 8.22 Idempotency matrix

| API | Key | Replay |
|-----|-----|--------|
| Evaluate | Optional | New quote OK |
| Reserve | checkout_id | Same reservation |
| Capture | order_id + promo_id | No-op success |
| Release | reservation_id | No-op if already free |

### 8.23 Whiteboard close

Draw **Eval (CPU/cache)**, **Inventory (CAS)**, **Ledger (append)**—only inventory is strongly consistent for scarce codes. Walk one MUTEX reject and one flash oversell attempt. Integer cents; re-eval at checkout.

> Oversell or undercharge is a **pricing correctness incident**—own the saga, ledger, and customer communication.

---

*End of discounts & coupons (stacking) system design.*
