<!-- Adapted into Fundamentals bank from Amazon/shopping-cart-system-design.md for cross-company prep. -->

# System Design: Shopping Cart System

> **Focus areas:** Guest/auth carts · Merge on login · Concurrency · Pricing snapshot · Optional inventory holds · Multi-device sync · Checkout handoff · Idempotency  
> **Style:** Amazon SDE III / L6+ — practicality, reliability, efficiency, operational ownership, progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS classes (read vs mutate vs merge vs reprice), explicit merge invariants, resolved ownership of cart vs price vs inventory

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

Goal: **bound the cart**—durable add/update/remove for guests and authenticated users, correct merge on login, safe concurrent edits across devices, sensible price snapshots, optional soft inventory signals/holds, and a clean handoff to checkout without making the cart the inventory SoT.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Guest carts? | Yes; cookie/device token; TTL (e.g. 30 days) | `guest_id` durable store |
| F2 | Auth carts? | Yes; follow user across devices | Key by `user_id` |
| F3 | Merge? | On login/signup: merge guest into user | Explicit merge policy |
| F4 | Line identity? | ASIN/SKU (+ offer_id for marketplace) | Line key `(cart, asin[, offer])` |
| F5 | Quantities? | 1..max_per_item; stock advisory | Cap + soft availability |
| F6 | Price display? | Show current price; snapshot on add optional | Reprice before checkout |
| F7 | Saved for later? | Phase 1.5 wish/save list | Separate list entity |
| F8 | Multi-device? | Same user cart; near-real-time enough | Versioned document / CRDT-lite |
| F9 | Inventory hold? | **Optional soft**; hard reserve at checkout | Feature flag; default advisory |
| F10 | Promotions? | Cart-level coupon stub; stacking elsewhere | Call promotions thin |
| F11 | Checkout handoff? | Cart snapshot → checkout session | Immutable snapshot id |
| F12 | Persistence? | Survive refresh/app kill | Durable DB not memory-only |
| F13 | Catalog changes? | Discontinued ASINs flagged | Validate on read/mutate |
| F14 | Idempotency? | Add-item retries | Idempotency keys on mutators |
| F15 | Marketplace? | Offer-aware lines Phase 2 | `offer_id` nullable MVP |

**MVP functional scope (lock with interviewer):**

1. CRUD cart lines for guest + user.  
2. **Merge guest → user** on login with documented qty policy.  
3. Optimistic concurrency (`version`) for multi-device.  
4. **Price fields:** `added_price_cents` snapshot + `current_price` on read via pricing service.  
5. Soft availability check on add (advisory).  
6. Optional **soft hold** experiment (short TTL) — off by default; defend trade-off.  
7. Create **checkout snapshot** from cart; clear/replace lines after successful order.  
8. TTL GC for guest carts; audit merge events for support.

**Out of MVP (explicitly defer):**

- Full promotions stacking engine  
- Hard inventory reservation inside cart (belongs to checkout/inventory)  
- Perfect CRDT merges for collaborative household carts  
- Cross-marketplace unified cart of all 3P sites  
- Offline-first mobile with unbounded conflict UI

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Read latency | Cart icon / page | p50 < 30ms, p99 < 100ms |
| N2 | Mutate latency | Add to cart | p50 < 50ms, p99 < 150ms |
| N3 | Durability | Don’t lose cart | Quorum/durable ACK |
| N4 | Availability | High; degrade pricing hydration | Cart lines still load |
| N5 | Consistency | Strong per cart key | Single-writer partition |
| N6 | Merge correctness | No silent line loss | Audited merge |
| N7 | Multi-device | Seconds lag OK | Version conflicts surfaced rarely |
| N8 | Scale | See table | Partition by cart/user id |
| N9 | Security | Can’t read others’ carts | Authz on user; unguessable guest | 
| N10 | Operability | Own pager | Merge error rate, conflict rate |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Guest adds items → browses → logs in → merge → sees combined cart → checkout snapshot.  
2. User adds on phone; sees update on desktop after refresh/short poll.  
3. Update qty; remove line; empty cart.  
4. Price dropped since add → cart shows new price + “price dropped” optional.  
5. Order success → cart lines cleared (or removed purchased).

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Login merge both have same ASIN | Sum qty capped by `max_qty` (chosen policy) |
| Concurrent edits version clash | Retry with latest; last-writer-wins on field policy or merge lines |
| Guest token stolen | HttpOnly secure cookie; rotate on login; don’t put PII in guest id |
| Add discontinued ASIN | Reject |
| Soft hold expires | Cart line remains; badge “hold expired” |
| Pricing service down | Show snapshot / last known; mark stale |
| Inventory says OOS | Allow line but warn; block at checkout |
| Double-click add | Idempotency → one qty increment policy |
| Huge cart (1000 lines) | Cap lines; pagination |
| User has guest on two browsers then login | Merge sequentially; second guest merges into user |
| Partial checkout failure | Cart retained; snapshot abandoned TTL |
| Currency/marketplace region mismatch | Cart region sticky; reject cross-region lines |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active carts (30d) | 50M | 500M | 5B | 50B* |
| DAU touching cart | 5M | 50M | 500M | 5B |
| Cart read QPS peak | 50K | 500K | 5M | 50M |
| Cart mutate QPS peak | 10K | 100K | 1M | 10M |
| Merges / day | 2M | 20M | 200M | 2B |
| Avg lines / cart | 3 | 3 | 4 | 4 |
| Checkout snapshots / day | 3M | 30M | 300M | 3B |
| Soft-hold ops/s (if on) | 1K | 10K | 100K | 1M |

\*Logical carts; cold guests expire; storage tiering.

**What each jump forces:**

- **10×:** DynamoDB/Cassandra-style keyed docs; Redis cache; async price hydrate.  
- **100×:** Cell by user hash; merge as dedicated path; snapshot store; throttle soft holds.  
- **1,000×:** Edge cache for authenticated cart digests carefully; guest local+sync; strict caps.

### 1.5 Etc. (Constraints & Assumptions)

- Cart is **not** payment or inventory SoT.  
- Money integers (cents).  
- Prefer **document-per-cart** for co-located lines.  
- Default: **no hard inventory hold** in cart; optional soft hold discussed as trade-off.

**Scope statement:**

> Design a shopping cart system supporting guest and authenticated users, login merge, concurrent multi-device updates, price snapshots with checkout reprice, optional soft inventory holds, and durable checkout handoff—scaled from tens of millions of carts through 10× / 100× / 1,000× with per-cart strong consistency.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Cart reads** | Icon count, full cart | 50K/s | Cache + KV |
| **Mutations** | add/update/remove | 10K/s | Primary cart store |
| **Merges** | login spikes | bursty | Special path |
| **Reprice hydrate** | pricing batch | with reads | Pricing client |
| **Snapshot create** | pre-checkout | ~checkout QPS | Snapshot store |
| **Soft hold** (opt) | inventory calls | ≤ mutate | Inventory |

### 2.2 Storage

```text
Cart doc ~1–2 KB typical (3 lines)
50M active × 2 KB ≈ 100 GB
Guest churn high → TTL compaction critical
Snapshots ~2 KB × 3M/day ≈ 6 GB/day (retain few days)
Merge audit ~300 B × 2M/day ≈ 0.6 GB/day
```

### 2.3 Cache

```text
Working set ≈ DAU carts × 2 KB
5M × 2 KB ≈ 10 GB — fits Redis cluster baseline
At 100× need tiered / cell-local caches
```

### 2.4 Merge spikes

```text
Prime Day login storms: merges << reads but heavier CPU
Must be idempotent and rate-limited per user
```

### 2.5 Bottleneck ranking

(1) Lost guest cart / bad merge (2) multi-device conflicts (3) chatty pricing fanout (4) accidental hard holds melting inventory (5) hot celebrity user_id rare but real.

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
[Cart icon (n)] → Cart page: lines, qty steppers, price, warnings
Login modal → merge progress → unified cart
Checkout CTA → create snapshot → checkout service
```

### 3.2 Domain model

```text
Cart
 ├── cart_id
 ├── owner: {type: USER|GUEST, id}
 ├── region / marketplace_id
 ├── currency
 ├── lines[]: CartLine
 ├── version
 ├── updated_at
 └── ttl_expires_at? (guest)

CartLine
 ├── line_id / asin (+ offer_id?)
 ├── qty
 ├── added_price_cents
 ├── added_at
 ├── product_title_snapshot?
 ├── hold_id? (optional soft hold)
 └── flags: unavailable_hint, etc.

MergeEvent
 ├── merge_id, user_id, guest_id
 ├── before_user, before_guest, after
 └── policy_version

CheckoutSnapshot
 ├── snapshot_id, cart_id, user_id
 ├── lines immutable copy + priced_at
 ├── created_at, expires_at
 └── status: OPEN|CONSUMED|EXPIRED
```

**Ownership (resolved):**

| Concern | Source of truth |
|---------|-----------------|
| Cart contents | **Cart service** |
| Current price | **Pricing service** (hydrate) |
| Sellable stock | **Inventory** (checkout reserve) |
| Soft hold (opt) | Inventory hold API, referenced by cart |
| Order | Order service after checkout |
| Catalog active flag | Catalog |

**Deal-breakers:**

- Redis-only cart without durability.  
- Hard-reserving inventory on every add.  
- Merge that drops lines without audit.  
- Trusting cart price at payment without reprice.  
- Using cart `version` incorrectly across guest→user id change.

### 3.3 Service map

| Service | Responsibility |
|---------|----------------|
| Cart API | CRUD, merge, snapshot |
| Cart Store | Keyed durable documents |
| Cart Cache | Read-through / write-through |
| Pricing Client | Batch get prices |
| Catalog Client | Validate ASIN/offer |
| Inventory Client | Advisory availability; optional holds |
| Checkout | Consumes snapshot |
| Identity / Session | Guest cookie + user auth |
| GC / TTL worker | Expire guests & snapshots |
| Audit / Support | Merge event query |

### 3.4 Keying & identity

```text
USER cart key:  user:{user_id}
GUEST cart key: guest:{guest_id}   # 128-bit random
cart_id stable UUID stored inside doc for analytics
On login: merge guest→user; invalidate guest; bind cookie to user session
```

### 3.5 Mutation API semantics

```text
AddItem(asin, qty, idem_key):
  validate catalog active
  advisory inventory (optional)
  upsert line: qty = min(max_qty, existing+qty)  # or set semantics—pick one
  set added_price if new line
  bump version
  optional: SoftHold.ensure(qty)

UpdateQty(asin, qty):
  if qty==0: remove
  CAS version

RemoveItem(asin):
  delete line; release soft hold if any
```

**Idempotency:** for AddItem, store `(owner, idem_key) → result` short TTL.

### 3.6 Guest → user merge (core)

```text
Merge(user_id, guest_id, policy_version):
  lock/order: always load user then guest with transactional strategy
  # Prefer single-partition transform job:
  user = get(user)
  guest = get(guest)
  if guest empty: return user
  if already_merged(guest_id): return user  # idempotent
  merged_lines = {}
  for line in user.lines + guest.lines:
    key = line.asin
    merged_lines[key].qty = min(max_qty, sum)
    # price: keep min added_price or user line preference—document
  write user cart with merged_lines, version++
  write MergeEvent audit
  delete/expire guest cart
  release redundant soft holds; re-ensure for merged qtys if feature on
```

| Conflict policy | Behavior |
|-----------------|----------|
| **Sum qty + cap (chosen)** | Intuitive “don’t lose items” |
| Prefer user qty | Simpler; may drop guest intent |
| Prefer max qty | Middle ground |
| Ask user UI | Best UX; slower interview path |

### 3.7 Concurrency / multi-device

**Chosen:** optimistic concurrency with `version` on cart document.

```text
Write if version == expected; else 409 CONFLICT with server cart
Client retries: rebase qty operations (operational transform lite)
```

For two devices adding different ASINs: rebase unions lines. For same ASIN qty races: last successful write wins after retry—or sum if using op logs.

**Op-log alternative (100×+):** append `CartOp` and materialize—better collaborative semantics, more complexity.

### 3.8 Pricing snapshot

```text
On add: store added_price_cents from Pricing.Get
On read: batch Pricing.Get(asins) → current_price_cents
UI: show current; optionally strike added if higher
Checkout: Pricing.Reprice(snapshot) authoritative
If delta > threshold: checkout asks confirmation
```

Never charge `added_price` blindly after days.

### 3.9 Optional inventory holds

| Mode | Pros | Cons |
|------|------|------|
| Advisory only (default) | Scales; simple | OOS at checkout |
| Soft hold short TTL | Higher convert confidence | Inventory contention; complexity |
| Hard reserve | Almost checkout | Wrong layer; melts stock |

**If soft hold ON:**

```text
hold TTL 10–15 min sliding on cart activity
hold qty = line qty
on merge/update: adjust holds idempotently
on expire: line remains, hold_id cleared
checkout: convert soft holds → hard reservations or release+reserve
```

Defend **default OFF** at Amazon scale unless interviewer pushes conversion metrics.

### 3.10 Checkout handoff

```text
CreateSnapshot(cart_id):
  durable copy of lines + hydrated prices + version
  return snapshot_id
Checkout consumes snapshot_id (not live cart) to avoid mid-flight edits
On order PLACED: ClearPurchasedLines or ClearCart (policy)
Abandoned snapshot TTL e.g. 24h
```

### 3.11 API sketch

```text
GET    /v1/carts/me
POST   /v1/carts/me/items          Idempotency-Key
PATCH  /v1/carts/me/items/{asin}   If-Match: version
DELETE /v1/carts/me/items/{asin}
POST   /v1/carts/merge             {guest_id}  (login)
POST   /v1/carts/me/snapshots
GET    /v1/carts/snapshots/{id}
```

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+--------+     +----------+     +------------------+
| Web/App|------→ API GW / BFF ----→ Cart Service   |
+--------+     +----------+     +----+-----+-------+
  guest cookie / auth                |     |
                                     v     v
                              +------+--+ +------+
                              | Cart KV | | Cache|
                              +------+--+ +------+
                                     |
         +-------------+-------------+-------------+
         v             v             v             v
   +---------+   +---------+   +----------+  +-----------+
   | Catalog |   | Pricing |   | Inventory|  | Checkout  |
   +---------+   +---------+   | (advise/ |  | (snapshot)|
                               |  hold)   |  +-----------+
                               +----------+
```

### 4.2 Merge sequence

```text
Client login → Auth OK → POST /carts/merge
CartService:
  begin
  load user cart (or create)
  load guest cart
  compute merged
  put user
  write MergeEvent
  delete guest
  commit
  bust cache
return merged cart
```

### 4.3 Multi-device conflict

```text
Device A: version=5 add ASIN1
Device B: version=5 add ASIN2  (stale)
B write → 409 {version:6, cart:...}
B client merges ASIN2 into latest → version=7
```

### 4.4 Snapshot → checkout

```text
Cart → Snapshot(store) → Checkout.CreateSession(snapshot_id)
  → Inventory.Reserve (hard)
  → Payment...
  → Cart.clear
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Durable cart before ACK** of add.  
2. **Merge idempotent** for `(user_id, guest_id)`.  
3. **No cross-user leakage**; guest ids unguessable.  
4. **Version CAS** on concurrent writes.  
5. **Checkout uses snapshot**, not racy live cart.  
6. **Reprice at checkout** — cart prices advisory.  
7. **Soft holds never exceed line qty**; released on remove.  
8. **Line cap / cart cap** enforced server-side.  
9. **Region/currency sticky** per cart.  
10. **MergeEvent audit** retained for support.

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | DynamoDB/Postgres doc; Redis; monolith Cart service |
| 10× | Cache; batch pricing; async analytics; TTL GC fleet |
| 100× | User cells; snapshot store; op-log optional; hold feature gated |
| 1,000× | Edge read digests for badge counts; careful consistency; strict caps |

**Badge count optimization:** store `line_count` / `total_qty` denormalized on cart header to avoid hydrating full lines for navbar.

### 5.3 Maintainability

- Policy version on merge.  
- Explicit feature flags: `SOFT_HOLD`, `PRICE_DROP_BADGES`.  
- Contract tests with checkout snapshot schema.  
- Chaos: crash mid-merge → idempotent recovery.  
- Avoid unbounded product hydration N+1.

### 5.4 Consistency spectrum

| Data | Model | Why |
|------|-------|-----|
| Cart doc | Strong per key | UX truth |
| Cache | Eventual seconds | Speed |
| Price on cart page | Eventual / request-time | Pricing SoT elsewhere |
| Soft hold | Strong in inventory | If enabled |
| Snapshot | Immutable once created | Checkout stability |
| Merge audit | Append-only | Support |

### 5.5 Merge deep dive — failure modes

```text
Crash after user write before guest delete:
  retry merge sees guest still present → must be safe
  use merge_token on guest: MARK_MERGING → DONE
  or store guest.merged_into=user_id

Double login two tabs:
  both merges idempotent → same end state
```

### 5.6 Concurrency strategies compared

| Approach | When |
|----------|------|
| **Optimistic version (chosen MVP)** | Typical ecommerce |
| Pessimistic lock | Rare; high latency |
| Op log / CRDT-lite | Strong multi-device at 100× |
| LWW blob | Too lossy for qty |

### 5.7 Why cart ≠ inventory

Hard holds on add cause: abandoned carts locking Prime Day stock, distributed complexity, poor browse conversion. Amazon-class systems **reserve at checkout** (or very late). Soft holds are a product experiment with strict TTLs.

### 5.8 Observability

| Metric / alarm | Why |
|----------------|-----|
| `cart_mutate_p99` | UX |
| `merge_success_rate` / `merge_p99` | Login critical |
| `version_conflict_rate` | Multi-device pain |
| `guest_cookie_missing_rate` | Lost carts |
| `snapshot_create_rate` | Funnel |
| `soft_hold_fail_rate` | If enabled |
| `pricing_hydrate_fail` | Degraded UX |
| `avg_lines` / `cart_cap_hits` | Abuse |

---

## 6. Wrap-Up

### 6.1 What we designed

A **durable shopping cart** for guests and users with audited login merge, optimistic concurrency for multi-device use, price snapshots plus live hydration, advisory availability (optional soft holds), and immutable checkout snapshots—without making the cart own inventory or payment correctness.

### 6.2 Key decisions worth defending

1. **Document-per-cart** keyed by user/guest.  
2. **Sum-and-cap merge policy** with audit.  
3. **Optimistic `version` CAS**.  
4. **Advisory inventory; hard reserve at checkout**.  
5. **added_price snapshot + checkout reprice**.  
6. **Snapshot handoff** isolates checkout from live edits.  
7. **Soft holds optional/default off**.  
8. **Idempotent add + idempotent merge**.  
9. **Denormalized badge counts**.  
10. **TTL GC for guests**.

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| Guest cookie cleared | Email cart / app account incentives |
| Merge policy disputes | Support tooling via MergeEvent |
| Pricing fanout | Batch + cache; stale OK briefly |
| Soft hold abuse | Cap + disable flag |
| Huge carts | Hard caps |
| Cell migration users | Sticky cart cell by user hash |

### 6.4 How to present in 45 minutes

1. Guest/user requirements + non-goals (5 min)  
2. Numbers (3 min)  
3. Data model + ownership (7 min)  
4. Merge + concurrency (12 min)  
5. Pricing + holds + snapshot (10 min)  
6. Scale + traps (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Guest & auth

**Q: Where store guest id?**  
A: Secure random in HttpOnly cookie / app secure storage; server validates.

**Q: Guest → user on signup vs login?**  
A: Same merge path.

**Q: Anonymous cart on shared computer?**  
A: Short TTL; logout doesn’t affect other user’s cart; guest separate.

**Q: Cross-device guest without login?**  
A: Generally no; need auth or explicit cart code (rare).

### 7.2 Merge

**Q: Why sum qty?**  
A: Preserves intent; cap prevents absurdity.

**Q: Different offers same ASIN?**  
A: Line key includes offer_id; don’t blindly sum.

**Q: Merge latency budget?**  
A: Tens of ms; if large, async with UI spinner—prefer sync under cap.

**Q: Prove no line loss?**  
A: MergeEvent before/after; property tests.

### 7.3 Concurrency

**Q: Two devices set qty 2 and 5?**  
A: With CAS+retry LWW; with op-log can define rules; mention trade-off.

**Q: Do we need websockets?**  
A: Not MVP; refresh/poll; push nice-to-have.

**Q: Hot user account?**  
A: Single partition still; rare; cache + backoff.

### 7.4 Pricing & checkout

**Q: Why snapshot price on add?**  
A: UX messaging (“was $X when added”); not charge authority.

**Q: Who wins on price change?**  
A: Checkout reprice; confirm if delta large.

**Q: Why snapshot entity?**  
A: Stable input while user pays; cart may change on other device.

**Q: Clear cart when?**  
A: After order PLACED; not on snapshot create.

### 7.5 Inventory holds

**Q: Soft vs hard?**  
A: Soft short TTL advisory lock; hard is checkout reservation.

**Q: Why default off?**  
A: Abandoned carts + scale; conversion experiment only.

**Q: Hold and merge?**  
A: Reconcile holds to merged qtys; never double-hold.

### 7.6 Failure injection

1. Cart DB write ack then crash before response → client idempotent retry.  
2. Merge crash mid-way → idempotent resume.  
3. Cache serves stale empty → version/ETag; prefer read-through primary on mutate.  
4. Pricing timeout → show snapshots; flag degraded.  
5. Inventory advisory timeout → allow add with unknown stock.  
6. Snapshot consumed twice → checkout idempotency prevents double order.  
7. Guest cookie fixation → rotate ids; bind to session secrets.  
8. Conflict storm → exponential retry; coalesce.  
9. GC deletes active guest wrongly → TTL from last activity only.  
10. Soft hold service down → degrade to advisory mode via flag.

### 7.7 Amazon Leadership-flavored probes

**Q: Customer Obsession — lose guest cart on login?**  
A: Unforgivable; merge with audit; measure merge loss metric=0.

**Q: Ownership — checkout OOS after cart said in stock?**  
A: Expected if advisory; improve promise; don’t fake holds everywhere.

**Q: Frugality — soft hold all carts?**  
A: Expensive contention; use selectively.

### 7.8 Comparison traps

**Q: Is cart just a Redis hash?**  
A: Durability, merge, snapshot, authz, multi-device make it a service.

**Q: Same as inventory system?**  
A: Cart consumes inventory APIs; must not become SoT.

**Q: Same as full online store?**  
A: Narrower; go deep on merge/concurrency/snapshot.

### 7.9 Extra interviewer traps (high value)

- Merge policy when both sides have ASIN?  
- What is SoT for price at pay time?  
- Hard hold on add—why dangerous?  
- How does If-Match / version work?  
- Snapshot vs live cart for checkout?  
- Idempotent add semantics (increment vs set)?  
- Guest id entropy?  
- Cross-region cart?  
- Badge count without full read?  
- Soft hold expiry UX?  
- When clear cart?  
- Marketplace offer line keys?  
- How to audit merge disputes?  
- Cap lines why?  
- Deal-breaker Redis-only?

### 7.10 Progressive scale Q&A

**Q: 1×?**  
A: One KV table + API; sync merge.

**Q: 10×?**  
A: Cache; batch pricing; GC workers.

**Q: 100×?**  
A: Cells; snapshots; optional op-log; gate holds.

**Q: 1,000×?**  
A: Edge badge digests; strict caps; regional cart homes.

---

## 8. Appendices

## Appendix A — Example schemas

```sql
CREATE TABLE carts (
  cart_id UUID PRIMARY KEY,
  owner_type TEXT NOT NULL, -- USER|GUEST
  owner_id TEXT NOT NULL,
  region TEXT NOT NULL,
  currency CHAR(3) NOT NULL,
  version BIGINT NOT NULL,
  line_count INT NOT NULL,
  total_qty INT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ttl_expires_at TIMESTAMPTZ,
  UNIQUE (owner_type, owner_id)
);

CREATE TABLE cart_lines (
  cart_id UUID NOT NULL REFERENCES carts(cart_id),
  asin TEXT NOT NULL,
  offer_id TEXT NOT NULL DEFAULT '',
  qty INT NOT NULL CHECK (qty > 0),
  added_price_cents BIGINT NOT NULL,
  added_at TIMESTAMPTZ NOT NULL,
  hold_id UUID,
  PRIMARY KEY (cart_id, asin, offer_id)
);

CREATE TABLE merge_events (
  merge_id UUID PRIMARY KEY,
  user_id TEXT NOT NULL,
  guest_id TEXT NOT NULL,
  policy_version TEXT NOT NULL,
  before_user JSONB NOT NULL,
  before_guest JSONB NOT NULL,
  after_cart JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (user_id, guest_id)
);

CREATE TABLE checkout_snapshots (
  snapshot_id UUID PRIMARY KEY,
  cart_id UUID NOT NULL,
  user_id TEXT,
  payload JSONB NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE mutation_idempotency (
  owner_key TEXT NOT NULL,
  idem_key TEXT NOT NULL,
  response JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (owner_key, idem_key)
);
```

## Appendix B — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Durable guest/user cart, version CAS, merge+audit, snapshot, reprice hooks |
| 10× | Cache, batch pricing, TTL GC, idempotency store |
| 100× | User cells, gated soft holds, conflict telemetry, snapshot TTL fleet |
| 1,000× | Edge badge digests, op-log optional, strict abuse caps |

## Appendix C — Glossary

| Term | Meaning |
|------|---------|
| Guest cart | Unauthenticated durable cart |
| Merge | Combine guest into user cart |
| Version / CAS | Optimistic concurrency token |
| added_price | Price when line created/updated |
| Snapshot | Immutable checkout input |
| Soft hold | Short-lived optional inventory lease |
| Advisory availability | Non-binding stock hint |
| Badge count | Navbar cart quantity |

## Appendix D — Estimation cheat-sheet

```text
read_QPS >> mutate_QPS >> merge_QPS
storage ≈ active_carts × avg_cart_bytes
cache_working_set ≈ DAU × avg_cart_bytes
Never charge without checkout reprice
```

## Appendix E — Merge policy matrix

| Situation | Result |
|-----------|--------|
| ASIN only in guest | Add to user |
| ASIN only in user | Keep |
| Both | qty = min(max, sum) |
| Conflicting offers | Keep separate lines by offer_id |
| Exceed max lines | Reject merge overflow; ask user to trim |

## Appendix F — State machines

```text
GuestCart: ACTIVE → MERGED → EXPIRED
UserCart: ACTIVE → (lines change) → ACTIVE
Snapshot: OPEN → CONSUMED
                 ↘ EXPIRED
SoftHold (opt): ACTIVE → RELEASED|EXPIRED|CONVERTED
```

## Appendix G — Soft hold reconciliation

```text
desired = line.qty
actual = Inventory.describe_hold(hold_id)
if actual < desired: try extend/increase
if actual > desired: decrease
if fail: clear hold_id; warn UX; keep line
```

## Appendix H — Client conflict rebase

```text
on 409:
  server = response.cart
  for op in pending_ops:
    apply_ot(server, op)
  PUT server with version
```

## Appendix I — Invariant tests

| Test | Expect |
|------|--------|
| Add durable after ACK | Restart still has line |
| Merge sum cap | qty capped; audit written |
| Merge twice | Idempotent |
| Concurrent different ASINs | Both present after rebase |
| Snapshot isolation | Live cart edit ≠ snapshot |
| Reprice delta | Checkout confirmation path |
| Remove releases hold | hold gone |
| Guest TTL | GC removes inactive |
| Authz | User A cannot read B |
| Idempotent add | One logical increment |

## Appendix J — Runbook

1. Spike in merge failures → check DB; freeze deploys; serve user cart without guest merge message.  
2. Version conflict storm → look for buggy client loops.  
3. Cache stampede → soft TTL + singleflight.  
4. Accidental soft_hold ON in prod → flag off immediately.  
5. Guest loss reports → cookie/SameSite issues; metrics.

## Appendix K — Evolution hooks

```text
Saved for later list
Household shared cart (explicit model)
Marketplace multi-offer lines
Subscriptions (Subscribe & Save) flags on lines
Edge-aware regional catalogs
```

---

*End of design doc. Open with §1 guest/auth + cart≠inventory; whiteboard §3.6 merge + §3.7 concurrency + §3.10 snapshot; close with invariants §5.1 and traps §7.9.*
