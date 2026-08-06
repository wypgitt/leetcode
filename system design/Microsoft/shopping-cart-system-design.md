# System Design: Amazon-Style Shopping Cart

> **Focus areas:** Guest/auth carts · Merge on login · Concurrency · Pricing snapshot · Optional inventory holds · Multi-device sync · Checkout handoff · Idempotency  
> **Style:** Microsoft loop — clear APIs, ownership boundaries, progressive scale (10× → 100× → 1,000×); framed as commerce/cart service a retail or Azure marketplace team might own  
> **Quality bar:** Correct money math, split QPS classes, explicit merge invariants, cart ≠ inventory ≠ payment SoT  
> **Interview theme:** Microsoft HLD (sometimes LLD object model follow-on) — practical distributed cart with Azure-friendly cells

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

Goal: **bound the cart**—durable add/update/remove for guests and authenticated users, correct merge on login, safe concurrent edits across devices, sensible price snapshots, optional soft inventory signals/holds, and a clean handoff to checkout—without making the cart the inventory or payment source of truth.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Shopping cart service + APIs | Full Amazon.com / Azure Marketplace portal |
| Money | Display + snapshot; reprice at checkout | Payment processor / ledger |
| Inventory | Soft advisory (+ optional short hold) | Hard reservation SoT (checkout owns) |
| Microsoft lens | Clean contracts, cells, authz, ops | Premature multi-region active-active writes |

**Scope statement:** Design an Amazon-style shopping cart: guest + user carts, login merge, multi-device concurrency, pricing hydrate, optional soft holds, checkout snapshot—scaled 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Guest carts? | Yes; cookie/device token; TTL (e.g. 30 days) | `guest_id` durable store |
| F2 | Auth carts? | Yes; follow user across devices | Key by `user_id` |
| F3 | Merge? | On login/signup: merge guest into user | Explicit merge policy + audit |
| F4 | Line identity? | SKU/ASIN (+ `offer_id` for marketplace) | Line key `(cart, sku[, offer])` |
| F5 | Quantities? | 1..max_per_item; stock advisory | Cap + soft availability |
| F6 | Price display? | Current price on read; snapshot on add | Reprice before charge |
| F7 | Saved for later? | Phase 1.5 | Separate list entity |
| F8 | Multi-device? | Same user cart; near-real-time enough | Versioned document / OT rebase |
| F9 | Inventory hold? | **Optional soft**; hard reserve at checkout | Feature flag; default advisory |
| F10 | Promotions? | Cart coupon stub; stacking elsewhere | Thin promotions client |
| F11 | Checkout handoff? | Cart snapshot → checkout session | Immutable `snapshot_id` |
| F12 | Persistence? | Survive refresh/app kill | Durable store, not memory-only |
| F13 | Catalog changes? | Discontinued SKUs flagged | Validate on read/mutate |
| F14 | Idempotency? | Add-item retries | Idempotency keys on mutators |
| F15 | Marketplace? | Offer-aware lines Phase 2 | `offer_id` nullable MVP |
| F16 | Regions? | Cart sticky to marketplace/region | Reject cross-region lines |

**MVP functional scope (lock with interviewer):**

1. CRUD cart lines for guest + authenticated user.  
2. **Merge guest → user** on login with documented qty policy.  
3. Optimistic concurrency (`version`) for multi-device.  
4. **Price fields:** `added_price_cents` snapshot + `current_price` on read via pricing.  
5. Soft availability check on add (advisory).  
6. Optional **soft hold** experiment (short TTL)—off by default; defend trade-off.  
7. Create **checkout snapshot** from cart; clear/replace lines after successful order.  
8. TTL GC for guest carts; audit merge events for support.

**Out of MVP:**

- Full promotions stacking engine  
- Hard inventory reservation inside cart  
- Perfect CRDT household shared carts  
- Offline-first unbounded conflict UI  
- Cross-site unified 3P cart

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Cart read (icon / page) | p50 < 30ms, p99 < 100ms in-region |
| N2 | Mutate (add/update) | p50 < 50ms, p99 < 150ms |
| N3 | Durability | No silent loss after ACK |
| N4 | Availability | High; degrade pricing hydrate |
| N5 | Consistency | Strong per cart key |
| N6 | Merge correctness | No silent line loss; audited |
| N7 | Multi-device lag | Seconds OK |
| N8 | Security | Authz; unguessable guest tokens |
| N9 | Operability | Merge/conflict/hold metrics + pager |
| N10 | Compliance | PII minimal in cart; region residency hooks |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Guest adds items → browses → logs in → merge → unified cart → checkout snapshot.  
2. User adds on phone; desktop refresh/short poll sees update.  
3. Update qty; remove line; empty cart.  
4. Price drop since add → show current + optional “price dropped”.  
5. Order success → purchased lines cleared.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Login merge same SKU | Sum qty capped by `max_qty` |
| Concurrent edits version clash | 409 → client rebase / retry |
| Guest token stolen | HttpOnly Secure cookie; rotate on login |
| Add discontinued SKU | Reject |
| Soft hold expires | Line remains; badge “hold expired” |
| Pricing down | Show snapshot / last known; mark stale |
| Inventory OOS | Allow line + warn; block at checkout |
| Double-click add | Idempotency → one logical increment |
| Huge cart | Cap lines (e.g. 100); paginate UI |
| Two guests then login | Sequential merges into user |
| Partial checkout failure | Cart retained; snapshot TTL expire |
| Region mismatch | Sticky region; reject cross-region |

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

- **10×:** Keyed document store; Redis cache; async price hydrate; TTL GC.  
- **100×:** Cells by user hash; dedicated merge path; snapshot store; gate soft holds.  
- **1,000×:** Edge digests for badge counts; strict caps; regional cart homes; abuse controls.

### 1.5 Constraints & Assumptions

- Cart is **not** payment or inventory SoT.  
- Money as integers (cents / minor units).  
- Prefer **document-per-cart** for co-located lines.  
- Default: **no hard inventory hold** in cart.  
- Auth via Entra ID / OAuth-style tokens in Microsoft framing; guest via opaque token.

**Repeat-back:**

> Durable guest and user carts with audited login merge, versioned multi-device mutations, price snapshots plus checkout reprice, optional soft holds, and immutable checkout snapshots—strong consistency per cart, progressive cells at scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline peak | Plane |
|-------|------|---------------|-------|
| **Cart reads** | Icon count, full cart | 50K/s | Cache + KV |
| **Mutations** | add/update/remove | 10K/s | Primary cart store |
| **Merges** | login spikes | bursty | dedicated path |
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
5M × 2 KB ≈ 10 GB — fits Redis / Azure Cache cluster baseline
At 100× need cell-local caches
```

### 2.4 Merge spikes

```text
Login storms (sales events): merges << reads but heavier CPU
Must be idempotent and rate-limited per user
```

### 2.5 Latency budget (add-to-cart)

```text
Client → API GW → authz → CAS mutate → cache invalidate → ack
~20 + 20 + 10 + 40 + 20 ≈ 110ms p99 budget (in-region)
Pricing hydrate on read path can be parallel / stale-ok
```

### 2.6 Bottleneck ranking

(1) Lost guest cart / bad merge (2) multi-device conflicts (3) chatty pricing fanout (4) accidental hard holds melting inventory (5) hot celebrity `user_id` rare but real.

---

## 3. High-Level Design

### 3.1 UX surfaces

```text
[Cart icon (n)] → Cart page: lines, qty, price, warnings
Login → merge progress → unified cart
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
 ├── line_id / sku (+ offer_id?)
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
| Cart API | CRUD, merge, snapshot create |
| Cart Store | Document/KV per cart key |
| Cart Cache | Hot reads; badge digests |
| Pricing Client | Batch hydrate current prices |
| Catalog Client | Active/title/dims validation |
| Inventory Client | Advisory + optional soft hold |
| Checkout | Consumes snapshot; reserves stock; pays |
| Identity | User auth; guest token issue/rotate |
| Merge Auditor | Durable merge events |
| GC Worker | Guest TTL, abandoned snapshots |
| Telemetry | Conflict rate, merge fail, lag |

### 3.4 API sketch

```http
GET    /v1/carts/me
PUT    /v1/carts/me/lines/{sku}     # upsert qty; Idempotency-Key
PATCH  /v1/carts/me/lines/{sku}     # qty delta
DELETE /v1/carts/me/lines/{sku}
POST   /v1/carts/merge              # {guest_id} after login
POST   /v1/carts/me/checkout-snapshots
GET    /v1/carts/me/badge           # {total_qty, version}
```

**Headers:** `Authorization` or guest cookie; `If-Match: version` on mutates; `Idempotency-Key` on mutates/merge/snapshot.

**Errors:** `409 VERSION_CONFLICT`, `422 LINE_CAP`, `404 SKU`, `403 REGION`, `429 RATE`.

### 3.5 Merge policy (default)

```text
for each guest line:
  if user has same (sku, offer): qty = min(max_qty, user.qty + guest.qty)
  else: copy line to user cart
guest cart → MERGED (tombstone); cookie rotated
write MergeEvent with before/after
idempotent on (user_id, guest_id)
```

**Alternatives (name them):** last-writer-wins by timestamp; user-wins always; prompt user UI (rarely worth MVP complexity).

### 3.6 Concurrency model

- Single logical document per cart; `version` CAS.  
- Multi-device: optimistic concurrency; clients rebase pending ops on 409.  
- Avoid distributed locks across services on the hot path.  
- Merge runs under user cart lock/CAS after auth; guest frozen.

### 3.7 Checkout handoff

```text
1. Client POST checkout-snapshots (optional reprice pass)
2. Snapshot immutable; status OPEN; TTL (e.g. 30–60 min)
3. Checkout reads snapshot_id only (not live cart)
4. On paid order: CONSUMED; cart clears purchased lines
5. On abandon: EXPIRED; cart unchanged
```

### 3.8 Soft hold (optional, off by default)

| Pros | Cons |
|------|------|
| Better “still available” UX briefly | Inventory pressure; complexity |
| Converts some abandoners | Hold storms at 100× |
| Experiment-friendly | Reconciliation bugs |

**If on:** short TTL (e.g. 5–15 min); hold_id on line; never block cart write if inventory down; reconcile qty changes; release on remove/expire.

### 3.9 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Store | Document/KV per cart | Co-locate lines; simple CAS |
| Consistency | Strong per cart | Merge/qty correctness |
| Cache | Cache-aside + invalidate | Read >> write |
| Price | Snapshot + hydrate | Honesty without blocking mutate |
| Hold | Advisory default | Avoid melting ATP |
| Merge | Sum+cap + audit | Predictable support story |
| Multi-region | Sticky home region | Avoid dual-write carts |
| Badge | Cached digest | Cheap navbar |

### 3.10 Progressive architecture

| Scale | Architecture add |
|-------|------------------|
| 1× | Single region; Cosmos DB / Dynamo-style or Postgres doc; Redis |
| 10× | Cache cluster; batch pricing; GC workers; idempotency table |
| 100× | User-hash cells; merge SLO dashboard; snapshot fleet; hold gate |
| 1,000× | Regional homes; edge badge; abuse caps; optional op-log for sync |

---

## 4. Architecture Diagram

### 4.1 Request path

```text
┌──────────┐   ┌─────────────┐   ┌────────────┐   ┌─────────────┐
│ Web/App  │──▶│ API Gateway │──▶│ Cart API   │──▶│ Cart Store  │
└──────────┘   │ + WAF/RL    │   │ (mutate/   │   │ (CAS doc)   │
               └─────────────┘   │  merge/    │   └──────┬──────┘
                                 │  snapshot) │          │
                                 └─────┬──────┘   ┌──────▼──────┐
                                       │          │ Cart Cache  │
                    ┌──────────────────┼──────────┴─────────────┘
                    ▼                  ▼
             ┌────────────┐    ┌────────────┐
             │ Pricing    │    │ Catalog /  │
             │ Inventory  │    │ Identity   │
             └────────────┘    └────────────┘
                    │
                    ▼
             ┌────────────┐    ┌────────────┐
             │ Snapshot   │───▶│ Checkout   │
             │ Store      │    │ (+ Order)  │
             └────────────┘    └────────────┘
```

### 4.2 Merge sequence

```text
Client          Cart API           Store            Audit
  |  login OK      |                 |                |
  |--POST /merge-->|                 |                |
  |                |--CAS load user->|                |
  |                |--load guest---->|                |
  |                |  apply policy   |                |
  |                |--CAS write user>|                |
  |                |--tombstone guest|                |
  |                |--write event------------------>|
  |<-200 merged----|                 |                |
```

### 4.3 Cell topology (100×+)

```text
                 Global Router (user_id / guest_id hash)
                    /        |         \
               Cell A     Cell B     Cell C
            [API+Store+   ...         ...
             Cache+GC]
Guest cookies encode cell hint; sticky after issue.
Cross-cell merge: rare (user moved); forward once.
```

### 4.4 Failure domains

```text
Pricing down     → serve lines + stale price flag
Inventory down   → advisory skip; no hard fail mutate
Cache down       → read-through store (higher latency)
Store partition  → fail mutate; reads may stale from cache
Checkout down    → cart intact; retry snapshot later
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. After ACK, cart mutation is durable.  
2. Merge never silently drops a line (overflow → explicit error / trim policy).  
3. Snapshot contents frozen at create time.  
4. Checkout must reprice (or confirm stale acknowledgment) before charge.  
5. Soft hold never required for cart correctness.  
6. User A cannot read/mutate User B’s cart.  
7. Idempotent merge/mutate under same key.

**Failure handling**

| Failure | Mitigation |
|---------|------------|
| Partial merge crash | Idempotent merge; transactional write or saga with audit |
| Double snapshot | Idempotency key → same snapshot_id |
| Hold orphan | TTL + reconcile worker |
| Cache poison | Version in cache key; short TTL |
| Guest cookie loss | Accept; can’t recover without sync account |

**Degraded modes:** read-only cart; mutate with stale price; disable soft holds; postpone merge with clear UX.

### 5.2 Scalability

**Partition key:** `owner_type + owner_id` (or `cart_id` with secondary unique owner).

**Hot keys:** celebrity accounts—rare; shard not by SKU. Mitigate with request coalescing on badge, rate limits.

**Read path:** cache-aside; singleflight stampede control; badge endpoint returns digest only.

**Write path:** single-partition CAS; keep docs small (cap lines).

**10×:** cache + GC + batch pricing.  
**100×:** cells; snapshot store separate from hot carts; merge as first-class SLO.  
**1,000×:** regional affinity; edge CDN only for static; badge digests at edge carefully signed; strict line/qty caps; async op-log for multi-device if needed.

**Backpressure:** 429 on mutate storms; shed soft holds first; never drop durable ACK silently—fail loud.

### 5.3 Maintainability

- **API versioning:** `/v1`; additive line fields.  
- **Policy version** on merge events for support forensics.  
- **Feature flags:** soft_hold, max_lines, reprice_strict.  
- **Clear ownership:** Cart team owns contents; Pricing/Inventory SLAs documented.  
- **LLD follow-on (Microsoft often asks):** classes `Cart`, `CartLine`, `MergePolicy`, `CartRepository`, `CheckoutSnapshotFactory`—keep domain pure of HTTP.  
- **Tests:** invariant suite (Appendix I); contract tests with checkout.  
- **Observability:** `merge_fail_rate`, `version_conflict_rate`, `pricing_stale_ratio`, `guest_ttl_gc_lag`, `hold_reconcile_lag`.

### 5.4 Security & compliance

- Guest IDs: 128-bit unguessable; Secure + HttpOnly + SameSite.  
- Authz middleware before every cart access.  
- No payment PAN in cart.  
- Region/marketplace stickiness for residency.  
- Audit merges for disputes; retention policy.

### 5.5 Consistency details

| Operation | Consistency |
|-----------|-------------|
| Line mutate | Linearizable per cart (CAS) |
| Badge read | Read-your-writes preferred; eventual OK ≤ few seconds |
| Price hydrate | Eventual; mark `priced_at` |
| Snapshot vs live cart | Snapshot isolated |
| Soft hold vs line qty | Eventually reconciled |

### 5.6 Money & correctness

```text
All money = integer minor units
Never float sum in API
Display formatting client-side with currency
Checkout reprice: if delta > threshold → confirm UX
```

### 5.7 Multi-device sync strategies

| Approach | When |
|----------|------|
| Version CAS + full doc | MVP; simplest |
| Op-log + rebase | High conflict mobile |
| Short poll / push notify | UX freshness |
| CRDT | Household shared (defer) |

### 5.8 Data lifecycle

```text
Guest ACTIVE → MERGED | EXPIRED(GC)
User cart retained while account live; soft-delete lines
Snapshot OPEN → CONSUMED | EXPIRED
MergeEvent retained per compliance (e.g. 90–365d)
Idempotency keys TTL (e.g. 24–72h)
```

---

## 6. Wrap-Up

### 6.1 Design summary

A **document-per-cart** service with strong CAS, guest TTL, audited merge-on-login, cache for reads, pricing hydrate on read, optional soft holds gated by flag, and **immutable checkout snapshots** so checkout/inventory/payment stay separate planes.

### 6.2 Top trade-offs to verbalize

1. Soft hold off by default vs conversion UX.  
2. Sum+cap merge vs user-prompt merge.  
3. Sticky regional cart vs global active-active.  
4. Cache freshness vs conflict rate.  
5. Snapshot isolation vs “live cart is checkout.”

### 6.3 What I’d build first (week 1–2)

Durable guest/user CRUD + version + merge audit + snapshot create + pricing stub + metrics. Soft holds later behind flag.

### 6.4 Risks & mitigations

| Risk | Mitigation |
|------|------------|
| Merge bugs lose items | Audit + idempotency + invariant tests |
| Inventory melt via holds | Flag off; TTL; caps |
| Checkout price surprise | Mandatory reprice path |
| Guest cookie breakage | Metrics on guest→empty; SameSite tests |
| Cell migration pain | Encode cell; dual-read window |

### 6.5 One-line close

> Cart owns durable lines and merge truth; pricing and inventory advise; checkout consumes snapshots—scale with cache, then cells, never by weakening merge or money invariants.

---

## 7. Deeper / Related Interview Questions

### 7.1 Conceptual

**Q: Why not Redis-only carts?**  
A: Process restarts / cluster fail lose revenue intent; use Redis as cache in front of durable store.

**Q: Why not hard-reserve on add?**  
A: Browse abandon rate high; holds starve inventory; reserve at checkout.

**Q: How does merge stay idempotent?**  
A: Unique `(user_id, guest_id)`; second call returns same result.

**Q: Guest on two devices?**  
A: Two guest carts; each merge into user sequentially after logins.

### 7.2 API / LLD

**Q: Sketch classes.**  
A: `Cart`, `CartLine`, `Money`, `MergePolicy`, `CartService`, `CartRepository`, `SnapshotService`; domain free of servlet types.

**Q: Idempotency storage?**  
A: Keyed by `(owner_key, idem_key)` → response; TTL.

**Q: 409 handling client algorithm?**  
A: Fetch server cart; replay pending ops; PUT with new version.

### 7.3 Scale jumps

**Q: 10×?**  
A: Cache; batch pricing; GC workers.

**Q: 100×?**  
A: Cells; snapshots; gate holds; merge SLO.

**Q: 1,000×?**  
A: Edge badge digests; strict caps; regional homes.

### 7.4 Failure drills

**Q: Pricing 100% down on Black Friday?**  
A: Serve `added_price` / last known; banner stale; checkout may force refresh or fail closed per policy.

**Q: Merge storm latency?**  
A: Rate-limit per user; queue with UX; never drop without message.

### 7.5 Microsoft-flavored

**Q: How would you run this on Azure?**  
A: API Management / Front Door → AKS/App Service; Cosmos DB or Azure SQL; Azure Cache for Redis; Service Bus for GC/reconcile; Entra ID for users; Key Vault for secrets; cells as stamp units.

**Q: Compliance?**  
A: Minimize PII; region stickiness; audit retention; authz tests.

### 7.6 Interviewer traps

| Trap | Better answer |
|------|---------------|
| Jump to Kafka first | Start with cart doc + CAS |
| Global CRDT shared cart MVP | Defer; single-owner doc |
| Float money | Integer cents |
| Cart = inventory | Split planes |
| Skip merge audit | Support can’t debug |
| Active-active multi-region writes | Sticky home + failover |

### 7.7 Related prompts

- Checkout / order service  
- Inventory reservation  
- Promotions stacking  
- Marketplace multi-offer cart  
- Shopping-cart object model (LLD)

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
  sku TEXT NOT NULL,
  offer_id TEXT NOT NULL DEFAULT '',
  qty INT NOT NULL CHECK (qty > 0),
  added_price_cents BIGINT NOT NULL,
  added_at TIMESTAMPTZ NOT NULL,
  hold_id UUID,
  PRIMARY KEY (cart_id, sku, offer_id)
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
| 1,000× | Edge badge digests, op-log optional, strict abuse caps, regional homes |

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
| Cell / stamp | Isolated deployable slice of users |

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
| SKU only in guest | Add to user |
| SKU only in user | Keep |
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
| Concurrent different SKUs | Both present after rebase |
| Snapshot isolation | Live cart edit ≠ snapshot |
| Reprice delta | Checkout confirmation path |
| Remove releases hold | hold gone |
| Guest TTL | GC removes inactive |
| Authz | User A cannot read B |
| Idempotent add | One logical increment |

## Appendix J — Runbook

1. Spike in merge failures → check store; freeze deploys; serve user cart; delay guest merge with banner.  
2. Version conflict storm → look for buggy client loops.  
3. Cache stampede → soft TTL + singleflight.  
4. Accidental soft_hold ON in prod → flag off immediately.  
5. Guest loss reports → cookie/SameSite; metrics on empty-after-add.

## Appendix K — Evolution hooks

```text
Saved for later list
Household shared cart (explicit model)
Marketplace multi-offer lines
Subscriptions flags on lines
Edge-aware regional catalogs
Azure API Management product packaging
```

## Appendix L — Sample cart JSON

```json
{
  "cart_id": "c_123",
  "owner": {"type": "USER", "id": "u_9"},
  "region": "US",
  "currency": "USD",
  "version": 42,
  "lines": [
    {
      "sku": "B00EXAMPLE",
      "offer_id": "",
      "qty": 2,
      "added_price_cents": 1999,
      "current_price_cents": 1799,
      "price_stale": false
    }
  ],
  "totals": {"qty": 2, "estimated_cents": 3598}
}
```

## Appendix M — Azure mapping (interview spice)

| Concern | Azure building block |
|---------|----------------------|
| API edge | Front Door + API Management |
| Compute | AKS / Container Apps |
| Cart store | Cosmos DB (point reads) or Azure SQL |
| Cache | Azure Cache for Redis |
| Async GC | Service Bus / Functions |
| Identity | Microsoft Entra ID |
| Secrets | Key Vault |
| Observability | Azure Monitor + App Insights |

---

*End of design doc. Open with §1 guest/auth + cart≠inventory; whiteboard §3.5 merge + §3.6 concurrency + §3.7 snapshot; close with invariants §5.1 and traps §7.6.*
