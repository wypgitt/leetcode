# System Design: Digital Game Store (Steam/Epic-like)

> **Focus areas:** Catalog · Entitlements · Purchases · Downloads · DRM keys · Refunds · Anti-fraud  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit latency budgets, honest entitlement consistency, clear PAID→ENTITLED saga  
> **Interview theme:** Databricks — classic HLD; owned digital inventory, CDN delivery, commerce sagas

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

Goal: **bound a digital game store**—browse/search an owned catalog, purchase games, grant durable entitlements, authorize CDN downloads, issue DRM keys, handle refunds/revokes, and resist fraud—without double-charging or granting access without payment.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is the product? | Steam/Epic-like store: we **own** the catalog and sell **digital copies** (unlimited supply for most titles) | No seller fan-out; catalog DB is authoritative for price/availability |
| F2 | Catalog scope? | **50K–200K** SKUs (games + DLC + bundles); metadata, screenshots, system reqs | ProductCatalog service; async search index; PDP reads from SoT |
| F3 | Entitlement model? | Purchase grants **permanent license** to download/play; family sharing optional Phase 2 | Entitlement row `(user_id, product_id)` is the access SoT |
| F4 | Checkout flow? | Cart → price snapshot → payment → **grant entitlement** → receipt | CheckoutSaga: `PAID → ENTITLED`; idempotent end-to-end |
| F5 | Downloads? | Client launcher requests **signed CDN URL**; resume/range GET; multi-GB installers | Download auth ties to entitlement; short-lived signed URLs |
| F6 | DRM / keys? | Some titles need **activation keys** (Steam key, third-party); others keyless | Key pool per SKU; allocate atomically at grant time; revoke on refund |
| F7 | Refunds? | **14-day / 2-hour playtime** policy (typical); revoke entitlement + key | Refund saga: `REFUNDING → ENTITLEMENT_REVOKED → PAYMENT_REFUNDED` |
| F8 | Idempotency? | Retries must not double-charge or double-grant | `(user_id, idempotency_key)` on checkout; payment idem = `order_id` |
| F9 | Pricing & sales? | Base price + **scheduled flash sales** + regional pricing | Price effective-dated; cache bust on sale start; checkout revalidates |
| F10 | Anti-fraud? | Stolen cards, velocity abuse, key reselling, chargeback handling | Risk score pre-auth; block/limit; async review queue |
| F11 | Platform / launcher? | Web store + desktop launcher; library sync, update patches | Entitlement cache on client; patch manifest separate from base game |
| F12 | Publisher / admin? | Ingest titles, upload builds to object storage, set prices, view sales | Control plane; build pipeline to CDN origin; not on hot read path |

**MVP functional scope (lock with interviewer):**

1. **Browse/search** catalog (search index async; PDP from ProductCatalog SoT).
2. **Cart + checkout** with price revalidation at pay time.
3. **CheckoutSaga:** authorize/capture payment → grant entitlement → allocate DRM key if required.
4. **Library API:** list user entitlements; entitlement check before download.
5. **Download auth:** issue signed CDN URL (TTL 15–60 min); range/resume supported.
6. **Refund API:** policy check → revoke entitlement → refund payment → return key to pool.
7. **Idempotency** on checkout and refund; crash-safe saga workers.

**Out of MVP (explicitly defer):**

- Multiplayer/matchmaking, friends, achievements, cloud saves
- Family sharing / gift purchases (design hooks: `grantee_user_id`, transfer token)
- In-game microtransactions / wallet
- User-generated marketplace (workshop)
- Full launcher auto-update delta patching algorithm
- Cross-store key redemption (external key import)
- Global active-active entitlement writes for same user

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Browse/search latency? | Interactive | p50 < 150ms, p99 < 500ms (cached PDP); search p99 < 800ms |
| N2 | Checkout latency? | Acceptable wait | p50 < 2s, p99 < 8s (payment provider tail) |
| N3 | Download start latency? | Fast URL issue | p99 < 200ms for signed URL mint (excludes CDN bytes) |
| N4 | Availability (store)? | High during sales | 99.9%+ catalog/checkout; CDN 99.99% |
| N5 | Correctness (money)? | No double charge | Idempotent payment + saga state machine |
| N6 | Correctness (access)? | No free games | Entitlement granted **only after** confirmed payment (or comp admin) |
| N7 | Durability? | Purchases never lost | Order + entitlement persisted before client ACK |
| N8 | Fraud tolerance? | Minimize chargebacks | Pre-auth risk scoring; velocity limits |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User searches → opens PDP → adds to cart → checkout → payment succeeds → entitlement appears in library → download via signed URL.
2. User already owns game → PDP shows "In Library"; cart blocks duplicate (or allows gift slot).
3. Keyless title → grant entitlement only; launcher verifies entitlement hash online periodically.
4. Key-required title → saga allocates key from pool atomically; user sees key in library + email.
5. Client retries checkout with same idempotency key → same order result, no double charge.
6. Partial download → resume with Range requests on same or new signed URL.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Price changed between cart and checkout | Revalidate at checkout; reject or show new price |
| Payment succeeds, grant crashes | Saga resumes → grant entitlement (idempotent) |
| Grant succeeds, payment webhook delayed | Reconcile job; never revoke without refund |
| Duplicate webhook from payment provider | Idempotent handler keyed on `payment_intent_id` |
| Key pool exhausted (rare SKU) | Fail grant step; refund or backorder per policy |
| Refund after partial playtime | Policy engine denies or prorates |
| Refund after key revealed | Revoke entitlement; flag key as revoked in publisher API if supported |
| Stolen card / chargeback | Auto-revoke entitlement; ban velocity pattern |
| Flash sale thundering herd | Queue/checkout tokens; cache PDP; scale checkout workers |
| CDN URL shared on forums | Short TTL + bind to user entitlement check at edge (optional) |
| User downloads while refund processing | Entitlement version fence; mid-download revoke → next chunk 403 |
| Bundle purchase | Grant entitlements for all bundle SKUs in one saga transaction |
| Free weekend / promo comp | Admin grant path bypasses payment; audit logged |
| Regional price / geo block | Price by region; CDN geo routing; block checkout if VPN mismatch (optional) |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Registered users | 5M | 50M | 500M | 5B |
| DAU | 500K | 5M | 50M | 500M |
| Catalog SKUs | 80K | 150K | 400K | 1M |
| Browse/PDP QPS (peak) | 20K | 200K | 2M | 20M |
| Search QPS (peak) | 5K | 50K | 500K | 5M |
| Purchase QPS (peak) | 200 | 2K | 20K | 200K |
| Flash-sale spike (single SKU) | 2K/s | 20K/s | 100K/s | 500K/s (queued) |
| Concurrent downloads (peak) | 50K | 500K | 5M | 50M |
| Avg game download size | 40 GB | 50 GB | 60 GB | 80 GB (patches extra) |
| Entitlement rows (total) | 200M | 2B | 20B | 200B |
| DRM key pool / hot SKU | 10K keys | 100K | 1M | publisher-fed |
| Regions / CDN PoPs | 1 region + CDN | 3 | 10 | global anycast |

**What each jump forces:**

- **10×:** Redis catalog cache; read replicas; checkout saga workers; CDN already mandatory.
- **100×:** Sharded entitlements by `user_id`; Kafka saga; search cluster; flash-sale admission queue.
- **1,000×:** User/cell sharding; entitlement cache layer; edge download auth; separate flash-sale partition; cold entitlement archive.

### 1.5 Etc. (Constraints & Assumptions)

- **We own inventory:** digital copies are unlimited unless DRM key pool is finite.
- **Build artifacts** live in object storage (S3/GCS) fronted by CDN; not in the app DB.
- Money in **integer cents** + ISO currency.
- **Payment provider** supports idempotency keys (Stripe-like).
- **Launcher** can poll library; WebSocket push optional Phase 2.
- Single primary cloud MVP; multi-region CDN; **home cell** for checkout/entitlement writes.

**Scope statement:**

> Design a Steam/Epic-like digital game store with owned catalog, entitlement-based access, PAID→ENTITLED checkout saga, signed CDN downloads, DRM key pools, refund revoke, and anti-fraud—starting at ~500K DAU / 200 purchase QPS and evolving through 10× / 100× / 1,000× with sharded entitlements and flash-sale controls.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Catalog size & read amplification

```text
SKUs: 80,000 (games + DLC + bundles)
Avg PDP payload (cached JSON): ~8 KB
Hot catalog fraction: 5% SKUs → 4,000 titles drive 80% browse traffic

Baseline browse+PDP QPS: 20,000
If every PDP hit DB: 20K × 8 KB ≈ 160 MB/s — manageable with cache
Target cache hit (PDP): 90%+ → ~2K DB reads/s at baseline
```

**Search index (OpenSearch):**

```text
Doc size ~4 KB × 80K ≈ 320 MB index (tiny)
Search QPS 5K; index writes on catalog change ~100/day — negligible
Search is NOT SoT; rebuild from ProductCatalog if corrupted
```

### 2.2 Purchase QPS & checkout load

```text
Baseline peak purchase QPS: 200
Flash sale on AAA title: 2,000 purchases/s for 10 minutes

Per checkout saga DB writes (order of):
  order create, payment state, entitlement insert, key allocate, audit ≈ 5–8 writes
200 QPS × 8 ≈ 1,600 writes/s baseline — Postgres with partitioning OK
2,000 QPS flash → 16K writes/s on hot shard → need queue + shard by product or user
```

**Payment provider ceiling:**

```text
Many PSPs cap ~100–500 auth/s per merchant without pre-arrangement
Flash 2K/s → admission queue + "waiting room" UX or pre-provisioned limit increase
```

### 2.3 Entitlement storage

```text
Row: user_id (16B) + product_id (8B) + granted_at + source_order_id + status ≈ 128 B

200M entitlements × 128 B ≈ 25 GB raw
2B (10× users, more purchases) ≈ 250 GB
20B (100×) ≈ 2.5 TB — shard by user_id; index (user_id) for library lookup

Library read QPS: DAU 500K, each opens launcher 1×/day peak window
≈ 500K / 3600 ≈ 140/s average; peak 10× → ~1.4K/s — cache per user helps
```

### 2.4 Download bandwidth & CDN math

```text
Baseline concurrent downloads: 50,000
Avg throughput per download (effective): 50 Mbps (mixed global)
Egress: 50K × 50 Mbps ≈ 2.5 Tbps aggregate — CDN vendor scale, not origin

Daily new bytes if each concurrent completes 40 GB over ~2 hours:
Not all 50K complete same hour; blended:
  50K concurrent × 40 GB over 3h ≈ 667 GB/min ≈ 89 GB/s ≈ 712 Gbps (peak window)

Origin offload: CDN cache hit 95%+ for popular titles
Origin egress mostly long-tail + first-day launch ≪ edge egress
```

**Signed URL mint QPS:**

```text
Downloads start: assume 1 new session / user / hour for 50K concurrent → ~14/s starts
Peak patch day: 500K users patch in 1h → ~140/s URL mint QPS
100×: 5M concurrent → ~1.4K/s mint — stateless, horizontal scale
```

### 2.5 DRM key pool

```text
Key row ~64 B; 1M keys in pool ≈ 64 MB
Allocation: UPDATE ... WHERE status=AVAILABLE LIMIT 1 (or pre-sharded pools)
Hot SKU 10K keys/s allocation → row-level lock pain → partition pool by key_id ranges
Publisher replenishment via async ingest job
```

### 2.6 Object storage (game builds)

```text
80K SKUs × avg 30 GB ≈ 2.4 EB upper bound if all unique — unrealistic
Realistic: 5K distinct build blobs (DLC variants) × 40 GB ≈ 200 TB
+ patches/deltas: +20% → ~240 TB origin storage
CDN caches hot subset; long-tail served from origin on miss
```

### 2.7 Bottlenecks (ranked)

1. Flash-sale checkout write hot spot (single SKU)  
2. Payment provider rate limits  
3. CDN egress cost / launch-day capacity  
4. Entitlement library lookup at 100× without cache  
5. DRM key pool row contention  
6. Fraud review queue backlog during sales  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
ProductCatalog     → SKUs, metadata, prices (effective-dated), build_manifest pointers
EntitlementService → (user_id, product_id) grants; library; access checks
CheckoutSaga       → RESERVING → PAYING → PAID → ENTITLING → ENTITLED | FAILED | REFUNDING
PaymentGateway     → auth/capture/refund with idempotency
KeyPoolService     → allocate/revoke DRM keys per sku_id
DownloadAuth       → entitlement verify → signed CDN URL + optional edge token
SearchIndex        → OpenSearch async projection of catalog (not SoT)
FraudService       → risk score, velocity, block rules
RefundSaga         → policy check → revoke entitlement → refund → restock key
```

### 3.2 Domain model

```text
Product (sku_id)
  ├── type: GAME | DLC | BUNDLE
  ├── title, description, tags, media_urls
  ├── price_rules[] (region, currency, effective_from, cents)
  ├── build_id → manifest in ObjectStore (files, hashes, size)
  ├── drm_type: NONE | KEY | THIRD_PARTY_API
  └── bundle_items[] (sku_ids)

Entitlement (user_id, sku_id) UNIQUE
  ├── status: ACTIVE | REVOKED | PENDING
  ├── source_order_id, granted_at, revoked_at
  ├── drm_key_id (nullable)
  └── version (for optimistic revoke fence)

Order
  ├── order_id, user_id, line_items[], price_snapshot_cents
  ├── state: CREATED → PAYMENT_PENDING → PAID → ENTITLED → COMPLETED
  ├── idempotency_key, payment_ref, fraud_decision
  └── region, currency

DrmKey (sku_id, key_id)
  ├── key ciphertext / HSM ref
  └── status: AVAILABLE | ALLOCATED | REVOKED
```

**Deal-breaker:** Treating search index or CDN as entitlement SoT.

### 3.3 ProductCatalog vs Search vs SoT

| Store | Role | Consistency |
|-------|------|-------------|
| **Postgres (catalog)** | SoT for products, prices, availability flags | Strong on write |
| **Redis** | Hot PDP cache, price cache for sale events | TTL + pub/sub invalidation |
| **OpenSearch** | Full-text search, facets, recommendations input | Eventual (seconds) |
| **Object storage** | Game binaries, manifests | Immutable versions |

**Write path:** Admin publishes product → write Postgres → outbox → indexer updates OpenSearch → CDN ingest for new build (async).

**Read path:** PDP reads Postgres (or Redis cache); search reads OpenSearch; **checkout always re-reads price from Postgres** (or versioned snapshot).

### 3.4 CheckoutSaga (PAID → ENTITLED)

Partners (payment) won't 2PC with us. Use durable saga:

```text
States:
  CREATED
  PRICE_LOCKED          (optional short TTL price snapshot)
  PAYMENT_AUTHORIZED
  PAYMENT_CAPTURED      (= PAID)
  ENTITLEMENT_GRANTED   (= ENTITLED)
  COMPLETED
  FAILED
  REFUNDING
  REFUNDED

Transitions (happy path):
  CREATED → validate cart, fraud pre-check, lock prices
  → PAYMENT_AUTHORIZED (auth hold) or direct capture
  → PAYMENT_CAPTURED
  → ENTITLEMENT_GRANTED (insert entitlement + allocate key)
  → COMPLETED
```

**Order of side effects (defend in interview):**

1. **Persist order** in `CREATED` with idempotency key before calling payment.  
2. **Fraud check** — block before auth if high risk.  
3. **Authorize/capture** with idempotency key = `order_id`.  
4. **Grant entitlement** only after `PAYMENT_CAPTURED` confirmed (webhook or sync response).  
5. **Allocate DRM key** in same DB transaction as entitlement when possible.  
6. Mark `COMPLETED`; emit receipt event.

**If payment succeeds but grant fails:** saga retries grant (idempotent upsert on `(user_id, sku_id, order_id)`).  
**If grant succeeds but ack lost:** client retries idempotency → returns existing entitlement.  
**Never:** grant before confirmed payment (except audited comp path).

**Alternative (not MVP):** auth hold → grant → capture. Reduces refund volume but risks free access if capture fails—only if business accepts.

### 3.5 EntitlementService

```text
grant(user_id, sku_id, order_id):
  INSERT entitlement ON CONFLICT (user_id, sku_id) DO NOTHING
    IF existing ACTIVE → idempotent return
  IF sku.drm_type == KEY:
    key = KeyPool.allocate(sku_id)  -- same TX or next saga step with compensator
  RETURN entitlement

has_access(user_id, sku_id):
  SELECT status FROM entitlements WHERE user_id=? AND sku_id=? AND status=ACTIVE
  (cache: entitlements:{user_id} SET of sku_ids, TTL 5–15 min, invalidate on grant/revoke)

library(user_id):
  JOIN entitlements + product metadata (cached)
```

**Bundle expansion:** Checkout expands bundle to constitutent SKUs before grant loop; all-or-nothing in saga.

### 3.6 Download authorization

```text
POST /v1/downloads/{sku_id}/session
  Auth: user JWT
  1. EntitlementService.has_access(user_id, sku_id) — SoT check
  2. Load build_manifest for sku (version user entitled to — usually latest unless pinned)
  3. Mint signed URL:
       CDN URL + HMAC(user_id, sku_id, build_id, exp, nonce)
       TTL: 15–60 minutes
  4. Return { manifest, files: [{path, url, sha256, size}], expires_at }

Client: Range GET on url; on 403/expired → request new session
Optional: CDN edge validates signature + calls lightweight auth subrequest
```

**Deal-breaker:** Long-lived unsigned URLs tied only to SKU without user binding.

### 3.7 Refund & revoke

```text
POST /v1/orders/{order_id}/refund
  1. PolicyEngine (playtime, days since purchase, sku exclusions)
  2. REFUNDING state
  3. EntitlementService.revoke(user_id, sku_id, reason=REFUND)
       SET status=REVOKED, version++
  4. KeyPool.revoke(key_id) → status REVOKED (publisher API notify async)
  5. PaymentGateway.refund(idempotency=order_id+"/refund")
  6. REFUNDED
```

**Mid-download revoke:** Entitlement version in auth token; CDN auth subrequest every N minutes or short TTL forces re-auth → 403.

### 3.8 API shape (MVP)

```text
GET  /v1/catalog/products/{sku_id}     → PDP
GET  /v1/search?q=...                  → OpenSearch proxy
GET  /v1/library                       → user entitlements
POST /v1/cart/checkout                 → {idempotency_key, payment_method}
GET  /v1/orders/{order_id}             → status
POST /v1/downloads/{sku_id}/session  → signed URLs
POST /v1/orders/{order_id}/refund      → policy-gated
```

### 3.9 Anti-fraud (high level)

| Signal | Action |
|--------|--------|
| Velocity: >N purchases / hour / card / IP | Challenge or block |
| New account + high-value cart | Step-up verification |
| BIN/country mismatch | Block or manual review |
| Device fingerprint cluster | Link accounts; limit free promos |
| Chargeback history | Auto-revoke + ban |

Run **pre-auth** scoring; async ML enrichment post-capture; never block entitlement grant on async path.

### 3.10 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Search vs catalog | Postgres SoT, OpenSearch index | Correct price at checkout | Checkout reads search hits |
| Grant timing | After capture confirmed | No free games | Grant before payment |
| Download auth | Short signed URL | Leak containment | Permanent public URLs |
| Key allocation | DB row lock / sharded pools | Correctness | Generate keys at refund |
| Flash sale | Queue + shard checkout | Protect DB/PSP | Unbounded sync checkout |
| Entitlement cache | Redis per user | Library speed | Cache-only access check without TTL invalidation |
| Refund | Revoke then refund | Stop abuse quickly | Refund without revoke |

### 3.11 Latency budget (checkout — say aloud)

```text
Total p99 target: 8s
  API validate + cart:        50ms
  Fraud pre-check:            100ms
  Price lock (DB):            30ms
  Payment auth/capture:       2–6s (PSP tail)
  Grant entitlement + key:      80ms
  Receipt / response:           20ms
```

Download session mint p99: **200ms** (entitlement check + manifest + sign).

### 3.12 Multi-region

| Plane | Mode |
|-------|------|
| Catalog reads | Multi-region replicas + CDN |
| Checkout / entitlements | **Home cell** per `user_id` |
| Payment | PSP region rules |
| Downloads | Global CDN; auth API regional |
| Search | Regional OpenSearch replicas |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
          +------------------+          +------------------+
 Clients  | Store Web /      |          | Desktop Launcher |
 (browse) | Launcher UI      |          | (library/download)|
          +--------+---------+          +--------+---------+
                   |                              |
                   v                              v
          +------------------+          +------------------+
          | API Gateway      |          | API Gateway      |
          +--------+---------+          +--------+---------+
                   |                              |
     +-------------+-------------+                |
     v             v             v                v
+----------+ +-----------+ +-----------+  +-------------+
| Catalog  | | Search    | | Checkout  |  | Download    |
| Service  | | Proxy     | | + Saga    |  | Auth Svc    |
+----+-----+ +-----+-----+ +-----+-----+  +------+------+
     |             |             |               |
     v             v             v               v
+----------+ +-----------+ +-----------+  +-------------+
| Postgres | | OpenSearch| | Orders DB |  | Entitlement |
| (catalog)| | (index)   | | + Saga    |  | Service     |
+----------+ +-----------+ +-----+-----+  +------+------+
     |                           |               |
     v                           v               v
+----------+              +-----------+    +-----------+
| Redis    |              | Payment   |    | Key Pool  |
| PDP cache|              | Provider  |    | (Postgres)|
+----------+              +-----------+    +-----------+
                                                        |
     +--------------------------------------------------+
     v
+----------+       +------------------+
| Fraud    |       | CDN (edge)       |
| Service  |       | ← Object Storage |
+----------+       |   (game builds)  |
                   +------------------+
```

### 4.2 Sequence: checkout with idempotency

```text
Client       API          CheckoutSaga    Fraud      Payment     Entitlement   KeyPool
  |--checkout->|              |            |            |              |            |
  |            |--start------>|            |            |              |            |
  |            |              |--score---->|            |              |            |
  |            |              |<-OK--------|            |              |            |
  |            |              |--capture(idem=order_id)->|              |            |
  |            |              |<-PAID-------------------|              |            |
  |            |              |--grant------------------------------->|            |
  |            |              |              |            |              |--alloc-->|
  |            |              |              |            |              |<-key-----|
  |            |              |<-ENTITLED--------------------------------|            |
  |            |<-200 order_id, library_items-|            |              |            |
  |            |              |            |            |              |            |

Retry same Idempotency-Key:
  |--checkout->|
  |            |--lookup idempotency table → return stored 200 (no second capture)
```

### 4.3 Sequence: crash after PAID, before ENTITLED

```text
SagaWorker     OrdersDB       Payment        Entitlement
  |--poll PAID->|              |              |
  |            |              |              |
  |--grant(idem=order_id)------------------->|
  |<-OK (or already exists)-----------------|
  |--ENTITLED->|              |              |
```

If grant permanently fails (key pool empty):

```text
  |--REFUNDING->|
  |--refund(idem=order_id+/refund)--------->|
  |--FAILED---->|
```

### 4.4 Sequence: refund revoke

```text
Client      RefundAPI     Policy      Entitlement    KeyPool    Payment
  |--refund->|             |              |            |          |
  |          |--check----->|              |            |          |
  |          |<-allow------|              |            |          |
  |          |--revoke------------------->|            |          |
  |          |              |              |--revoke-->|          |
  |          |--refund------------------------------------------->|
  |<-OK------|             |              |            |          |
```

Active download: next CDN auth subrequest fails → client shows "purchase refunded."

---

## 5. Design Deep Dive

### 5.1 Checkout saga — reserve / pay / grant

**Do we need inventory reserve?** Digital unlimited copies → **no quantity reserve** for most SKUs. Exceptions:

- **Finite DRM key pool:** soft-reserve key at PAYMENT_AUTHORIZED or allocate at grant with retry/backoff.
- **Flash sale "limited keys" promo:** counter `remaining_keys` with atomic DECR; at 0 reject checkout early.

**Saga implementation:**

```text
orders table: state, version, updated_at
saga_workers: poll state IN (PAYMENT_PENDING, PAID, ENTITLING) OR outbox events
advance(order_id):
  row = SELECT FOR UPDATE
  switch state:
    PAYMENT_PENDING: query PSP; if captured → PAID
    PAID: grant entitlements; → ENTITLING → ENTITLED
    ENTITLING: verify all line items granted → COMPLETED
```

**Idempotency table:**

```text
(user_id, idempotency_key) → order_id, response_body_hash, created_at
TTL cleanup after 24–72h
```

**Payment uncertainty:**

```text
if capture response unknown:
  NEVER new idempotency key
  GET payment by order_id
  if captured → continue to grant
  if failed → FAILED
  if pending → retry with backoff
```

### 5.2 Signed CDN URLs

**Threat model:** Users share URLs; URLs leak in logs/proxies.

**Mitigations:**

| Layer | Mechanism |
|-------|-----------|
| TTL | 15–60 min limits window |
| Binding | HMAC includes `user_id`, `sku_id`, `build_id` |
| Entitlement re-check | Edge auth subrequest to `/internal/auth/download` |
| IP soft-bind | Optional; frustrate casual sharing, not strict (mobile NAT) |
| Rate limit | Per-user concurrent range streams |

**Signing sketch:**

```text
payload = user_id + "|" + sku_id + "|" + build_id + "|" + exp + "|" + nonce
sig = HMAC-SHA256(kms_key, payload)
url = https://cdn.example/builds/{build_id}/{file}?exp=&nonce=&uid=&sig=
```

**Range/resume:** Standard HTTP Range; manifest lists chunk sizes for parallel download in launcher.

**Patch delivery:** Separate smaller manifest `patch_from_build_A_to_B`; same auth path; delta files on CDN.

### 5.3 Entitlement as SoT

**Invariants:**

1. At most one **ACTIVE** entitlement per `(user_id, sku_id)` for standard purchases.  
2. **Grant** implies `source_order_id` links to captured payment (or `source=COMP` admin).  
3. **Revoke** is monotonic; revoked rows never become ACTIVE without new order.  
4. Download auth always checks EntitlementService (cache is performance only).  
5. Library display may lag seconds; access check must not.

**Sharding:**

```text
shard = hash(user_id) mod N
entitlements table partitioned by user_id
library query: single shard lookup — O(1) shard routing
```

**Cache:**

```text
Redis SET entitlements:active:{user_id} = {sku_id...}
Invalidate on grant/revoke/event from outbox
Stale cache max TTL 5 min + pub/sub invalidation < 1s typical
```

**Deal-breaker:** Infer ownership from "user has order row" without entitlement status (refund race).

### 5.4 Flash sales

**Problem:** 100K users buy $5 AAA title in 5 minutes → 333 purchase/s average, peaks 2K–20K/s.

**Controls:**

```text
1. Pre-warm: CDN cache build; Redis PDP; payment PSP limit bump
2. Admission: token queue at API gateway — client sees ETA
3. Shard checkout by user_id (not sku_id) to spread writes
4. Price snapshot precomputed in Redis for sku_id at sale start
5. Idempotency prevents double-buy on retry storm
6. Optional: cap purchases/sec globally with 429 + Retry-After
```

**Counter without overselling keys:**

```text
UPDATE promo_counters SET remaining = remaining - 1
  WHERE sku_id=? AND remaining > 0
RETURNING remaining
-- in checkout CREATED step; if 0 → sold out
```

Digital unlimited: counter only for marketing "first N at discount" not inventory.

### 5.5 Anti-fraud deep dive

**Pre-auth rules engine:**

```text
score = w1*velocity + w2*account_age + w3*geo_mismatch + w4*device_reputation
if score > BLOCK: reject checkout
if score > REVIEW: async hold entitlement grant until review (careful UX)
MVP: block only; manual review async post-hoc
```

**Chargeback / key resale:** Webhook → auto-revoke entitlements + ban fingerprint + publisher key revoke API. Flag accounts with multi-region key activation or buy-refund loops on key SKUs.

### 5.6 Reliability

| Failure | Mitigation |
|---------|------------|
| Postgres primary down | Fail checkout; catalog reads from replica; downloads OK if entitlement cached |
| Payment webhook delay | Saga polls PSP; grant when confirmed |
| Duplicate webhook | Idempotent state transitions |
| Key pool empty at grant | Refund; alert publisher ops |
| CDN origin miss storm | Pre-warm; limit parallel origin fetches |
| Search stale | Acceptable for browse; PDP from SoT |
| Entitlement cache stale after revoke | Pub/sub invalidation; short TTL; version in download auth |

**Hard invariants:**

1. Idempotent checkout per `(user_id, idempotency_key)`.  
2. Grant only after payment captured.  
3. Revoke before or with refund (never leave active entitlement on refunded order).  
4. DRM key allocated at most once per key row.  
5. Order state transitions monotonic with version column.

### 5.7 Scalability — progressive scale

| Scale | Architecture |
|-------|--------------|
| **1×** | Monolith modules; Postgres catalog+orders+entitlements; Redis cache; single CDN; sync saga in API |
| **10×** | Split services; read replicas; Kafka outbox for saga; OpenSearch cluster; Redis cluster |
| **100×** | Shard entitlements/orders by user_id; dedicated checkout workers; flash-sale queue; edge download auth |
| **1,000×** | Multi-region home cells; entitlement read replicas + local cache; object storage multi-region; separate fraud pipeline |

**1× MVP sketch:**

```text
Checkout API:
  validate idempotency → fraud → price from Postgres → payment.capture
  → TX: insert entitlement + allocate key → update order ENTITLED → commit
  → return library slice

Download API:
  check entitlement → sign URL → return
```

**Progressive additions:** 10× → async saga workers, Redis library cache, catalog→indexer events. 100× → user cells, waiting room, sharded key pools. 1,000× → cold entitlement archive, CDN multi-vendor, regional catalog replicas.

### 5.8 Data model (sketch)

```text
products(sku_id, type, title, drm_type, build_id, metadata_json)
price_rules(sku_id, region, currency, cents, effective_from, effective_to)
orders(order_id, user_id, state, total_cents, idempotency_key, payment_ref, version)
  UNIQUE(user_id, idempotency_key)
entitlements(user_id, sku_id, status, source_order_id, drm_key_id, version)
  PRIMARY KEY(user_id, sku_id)
drm_keys(key_id, sku_id, key_enc, status, allocated_order_id)
  INDEX(sku_id) WHERE status='AVAILABLE'
```

---

## 6. Wrap-Up

**Design summary**

- **Owned digital catalog** in Postgres (SoT); OpenSearch for discovery only.  
- **CheckoutSaga:** confirm payment → grant entitlement → allocate DRM key; idempotent throughout.  
- **EntitlementService** is access SoT; downloads require live check + short signed CDN URLs.  
- **Refunds** revoke entitlement and keys before/with payment refund.  
- **Flash sales** need admission control and user-sharded writes, not infinite sync checkout.  
- **Anti-fraud** pre-auth scoring; chargeback triggers auto-revoke.

**MVP vs later**

| MVP | Later |
|-----|-------|
| Postgres entitlements + sync saga | Kafka saga + user cells |
| Global CDN + signed URLs | Edge auth subrequest everywhere |
| Key pool in Postgres | HSM + publisher API keys |
| Simple fraud rules | ML scoring pipeline |
| Keyless + key-based DRM | Family share, gifts, workshop |

**Top risks**

1. Grant-before-payment bug (free games)  
2. Double capture on idempotency miss  
3. Flash-sale DB/PSP meltdown  
4. Refund without revoke (ongoing piracy)  
5. CDN cost on launch day  

**What I'd measure first in production**

- Saga time-in-state (PAID → ENTITLED), grant failure rate, checkout idempotency hit rate, download 403 after purchase, chargeback-to-revoke latency, key pool depth.

---

## 7. Deeper / Related Interview Questions

### 7.1 Catalog & search

**Q: Why not use OpenSearch as the catalog SoT?**  
A: Search indexes are optimized for retrieval, not transactional price/inventory correctness. Prices change, sales start at exact times, refunds alter ownership—those need ACID rows in Postgres. Search can lag seconds; checkout must read SoT.

**Q: Bundle / DLC rules?**  
A: Bundle SKU expands to grants for each item; block or warn if user owns subset. DLC requires ACTIVE base-game entitlement unless standalone flag set. Launch-day PDP bypasses search via direct `sku_id` route.

### 7.2 Entitlements & library

**Q: Can a user own the same game twice?**  
A: Unique `(user_id, sku_id)` — second purchase returns idempotent "already owned" or converts to gift token (Phase 2).

**Q: How fast does library update after purchase?**  
A: Sync in checkout response includes new items; launcher also polls `/library` or receives push. Target < 2s visible.

**Q: Entitlement cache stale after refund on second device?**  
A: Revoke publishes invalidation; download auth hits SoT; launcher periodic online verify with `version` bump forces UI update.

### 7.3 Checkout & payment

**Q: Auth hold vs capture for digital goods?**  
A: Capture-first after fraud check is simpler for instant gratification. Auth→grant→capture only if chargeback rate dominates and publisher accepts access-before-capture risk.

**Q: Idempotency key scope?**  
A: `(user_id, idempotency_key)` unique → one order. Payment idempotency key = `order_id`. Retries safe for 24–72h.

**Q: Partial checkout failure on multi-item cart?**  
A: MVP: all-or-nothing saga—one payment, loop grants; if one grant fails, refund entire order. Phase 2: partial fulfill with split refunds (complex).

**Q: Webhook vs sync payment confirmation?**  
A: Sync response fast path; webhook authoritative backup; saga reconciles both idempotently.

**Q: Price in cart vs at checkout?**  
A: Cart shows estimate; checkout locks `price_snapshot` with version; if `price_rules` changed, reject with new total.

### 7.4 Downloads & CDN

**Q: Why signed URLs instead of OAuth on every byte?**  
A: CDN edge serves bytes cheaply at scale; OAuth every chunk adds latency and cost. Short signed URL + optional edge auth balances security and throughput.

**Q: 50 Mbps × 50K concurrent — can origin survive?**  
A: No. CDN cache hit 95%+ for popular titles; origin sees long-tail and cold starts only. Pre-warm before launch.

**Q: User shares signed URL?**  
A: TTL expires; HMAC binds user; edge subrequest re-validates entitlement; optional concurrent stream limit.

**Q: Manifests and patches?**  
A: JSON manifest lists files + SHA-256 hashes for parallel verify/download. Patches use separate smaller `patch_manifest` between build versions; same auth path.

### 7.5 DRM & keys

**Q: Key pool exhausted during flash sale?**  
A: Stop sales at checkout validation; queue backorder or refund; alert ops; never generate duplicate keys.

**Q: How to allocate keys without row lock contention?**  
A: Shard pool into buckets; `UPDATE ... WHERE key_id IN (SELECT ... LIMIT 1 FOR UPDATE SKIP LOCKED)`.

**Q: Revoke key on refund if user already redeemed on Steam?**  
A: Best-effort publisher API revoke; entitlement revoked locally regardless; legal/ToS enforcement offline.

**Q: Keyless DRM?**  
A: Entitlement check online; launcher encrypts local files tied to device cert—mention as Phase 2.

### 7.6 Refunds & chargebacks

**Q: Refund order of revoke vs money?**  
A: Revoke entitlement first (stop abuse), then refund payment. If refund fails, manual ops + account suspended.

**Q: 2-hour playtime policy implementation?**  
A: Launcher reports playtime heartbeat to PlaytimeService; refund API sums minutes since grant.

**Q: Chargeback after 30 days?**  
A: Webhook → revoke all entitlements from order; negative balance on account; block future purchases.

**Q: Partial refund on bundle?**  
A: Policy-dependent; MVP disallow or revoke entire bundle.

### 7.7 Fraud, flash sales & scale

**Q: Stolen cards / travel false positives?**  
A: Velocity + AVS/CVV + 3DS on high-risk; step-up auth for travel—not permanent block without appeal. Concurrent distant-geo downloads flag sharing; review async.

**Q: 20K purchases/s on one SKU — single row hot spot?**  
A: Don't shard by sku for orders—shard by user_id. Promo counter is one row—use Redis DECR or pre-partitioned counters.

**Q: Waiting room vs 503?**  
A: Waiting room preserves conversion; 503 loses sales. Token bucket assigns checkout slot.

**Q: When to split checkout service from catalog?**  
A: ~10× when purchase QPS impacts PDP latency—isolate pools and DB connections.

**Q: Multi-region entitlements?**  
A: Home cell per `user_id`; no active-active writes for same user. CDN global; auth API regional with replica read or home RPC. Regional `price_rules` at checkout.

### 7.8 Interviewer traps

| Trap | Strong answer |
|------|---------------|
| "Digital goods need inventory reserve" | Unlimited copies; only key pool or promo counters need atomic decrements |
| "Search index for checkout price" | Postgres SoT; revalidate at pay |
| "Grant then charge for better UX" | Chargeback/free game risk; grant after capture |
| "Permanent download links" | Short signed URLs + entitlement check |
| "Fan-out to publisher APIs per browse" | We own catalog; async publish pipeline only |
| "2PC payment and entitlement" | Saga + idempotency |
| "Refund without revoke" | User keeps playing for free |
| "One global Postgres forever" | Shard entitlements by user at 100× |

### 7.9 Comparison questions

**Q: Steam vs Epic from architecture view?**  
A: Same bones: entitlement library, CDN delivery, checkout saga. Epic often emphasizes free-game promos (flash scale); Steam adds community/marketplace (out of scope). Both need strong download auth and key management.

**Q: How is this different from online bookstore physical goods?**  
A: No warehouse/shipping; unlimited supply; fulfillment is entitlement grant + CDN bytes; fraud and refund revoke dominate over inventory pick-pack.

**Q: How is this different from book-price aggregator?**  
A: We **own** the catalog and inventory (digital copies), not fan-out to seller APIs. No quote aggregation; single merchant checkout saga.

**Q: Relation to S3/object storage design?**  
A: Game builds live in object storage; this design adds commerce layer (entitlement, signed CDN, DRM keys) on top of blob delivery.

---

*End of digital game store HLD prep.*
