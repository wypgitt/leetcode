# System Design: Customer / Order / Product Database

> **Focus areas:** Schemas · Partitioning · Access patterns · Consistency · Secondary indexes · Evolution · Progressive scale (10× → 100× → 1,000×)  
> **Style:** Amazon SDE III / L6+ — data modeling for commerce correctness, query efficiency, and operational ownership  
> **Quality bar:** Explicit access patterns before schema, split SoT vs read models, no naive cross-entity joins at scale, evolution without downtime

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

Goal: **design the database layer** for Amazon-class customer, order, and product (catalog) data—schemas, keys, partitions, indexes, consistency, and how the model evolves—not a full storefront UI redesign.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Entities in scope? | **Customer**, **Order** (+ lines), **Product/ASIN** | Three domains; possibly separate stores |
| F2 | One DB or many? | Prefer polyglot / service-owned DBs | Bounded contexts; no god schema |
| F3 | Product model? | ASIN, variants, attributes, media refs, category | Document + relational hybrid OK |
| F4 | Order model? | Header + line items; payments refs; shipments later | Aggregate root = order |
| F5 | Customer model? | Profile, addresses, payment tokens (refs), prefs | PII isolation |
| F6 | Access patterns? | Get product; get customer; create order; list orders by customer; admin lookup by order_id | Design keys from queries |
| F7 | Search products? | Keyword search **out of OLTP DB** | Search index projection |
| F8 | Analytics? | Not on primary OLTP | Warehouse / lake via events |
| F9 | Marketplace? | 1P first; offers can extend product | Product ≠ offer |
| F10 | History? | Orders immutable-ish; product versions | Append + version |
| F11 | Multi-marketplace? | US/EU/… catalogs | Partition by marketplace |
| F12 | Strong needs? | Order create & payment linkage correct | Transactions per aggregate |

**MVP functional scope (lock with interviewer):**

1. Schemas for Customer, Product (ASIN), Order + OrderLine.  
2. Primary keys, partition keys, and **secondary indexes** for stated access patterns.  
3. Consistency model per entity (strong vs eventual projections).  
4. Write paths: create/update customer; publish product; place order.  
5. Read paths: PDP product get; customer profile; order by id; orders by customer.  
6. Evolution: additive columns/fields; dual-write/expand-contract.  
7. Scale story 10× / 100× / 1,000×: sharding, CQRS, archival.

**Out of MVP (explicitly defer):**

- Full graph DB for “customers also bought”  
- OLAP star schemas as primary  
- Global secondary indexes that violate partition strategy without cost discussion  
- Perfect multi-region active-active for orders  
- Storing raw PAN / unrestricted PII in product DB  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Product read latency | PDP path | p99 < 20ms in-region keyed get |
| N2 | Order write durability | Place-order | Quorum/durable before ACK |
| N3 | Customer PII | Encrypted / scoped access | Least privilege; tokenized payments |
| N4 | Availability | Orders critical | Multi-AZ; cell-friendly |
| N5 | Consistency | Per-aggregate strong | Cross-aggregate eventual + saga |
| N6 | Evolution | Online schema changes | Expand/contract; dual read |
| N7 | Retention | Orders years; products current+history | Hot/cold tiers |
| N8 | Operability | Explain every query plan class | No unbounded scans |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `GetProduct(asin, marketplace)` → single key read from product store / cache.  
2. `UpsertCustomer` → profile + address book.  
3. `PlaceOrder` → transactional write of order aggregate (+ outbox).  
4. `ListOrders(customer_id, cursor)` → partition query newest first.  
5. `GetOrder(order_id)` → key lookup (global index or order_id encodes partition).  
6. Product attribute change → new version → projections update.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate place-order | Idempotency table / conditional put |
| List orders without customer partition | Forbidden full scan—require key |
| Product delete with open orders | Soft delete / status; orders keep snapshot |
| Address update mid-checkout | Order stores shipping snapshot |
| Schema add field | Additive; old readers ignore |
| Schema rename/remove | Dual-write; backfill; then contract |
| Hot customer (reseller) | Isolate partition / burst capacity |
| Hot ASIN | Read replicas / cache; write serialization careful |
| Cross-marketplace SKU confusion | Composite key `(marketplace, asin)` |
| Analytics query on OLTP | Reject; use events/warehouse |
| Orphan order lines | Disallow; lines only via aggregate API |
| PII breach blast radius | Separate customer store + encryption |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Customers | 100M | 1B | 10B | 100B* |
| ASINs | 100M | 200M | 400M | 500M+ |
| Orders / day | 5M | 50M | 500M | 5B |
| Peak order writes/s | 2K | 20K | 200K | 2M |
| Peak product reads/s | 200K | 2M | 20M | 200M |
| Peak customer reads/s | 50K | 500K | 5M | 50M |
| Order lines avg | 2.5 | 2.5 | 2.5 | 2.5 |
| Product attrs KB | 2–20 | 2–20 | 2–20 | 2–20 |
| Secondary index fan-out | moderate | high | careful | sparse / async |

\*Account-scale thought experiment—hierarchical directories, archival, synthetic ids.

**What each jump forces:**

- **10×:** Shard orders by customer; product keyed gets + cache; GSIs limited.  
- **100×:** CQRS read models; order archival; marketplace partitions; cell-local order DBs.  
- **1,000×:** Hierarchical keys; cold storage; approximate indexes; strict access-pattern allowlist.

### 1.5 Etc. (Constraints & Assumptions)

- **Access patterns drive schema**—never ER diagram first.  
- Money fields: **integer cents** + currency code.  
- Orders store **point-in-time snapshots** of price/title for support/legal.  
- Prefer **service-owned databases** (Customer Service DB, Catalog DB, Order DB).  
- Cross-entity joins happen in application or via projections—not distributed SQL fantasy.

**Scope statement:**

> Design Amazon-style customer, order, and product databases: schemas and keys derived from access patterns, partitioning and secondary indexes that scale, explicit consistency boundaries, CQRS where needed, and online evolution from baseline through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split storage & QPS classes

| Class | Workload | Baseline | 10× | Store |
|-------|----------|----------|-----|-------|
| Product point reads | PDP | 200K/s | 2M/s | Catalog + cache |
| Product writes | Publish | 100/s | 500/s | Catalog SoT |
| Customer reads | Account/checkout | 50K/s | 500K/s | Customer DB |
| Customer writes | Profile | 1K/s | 10K/s | Customer DB |
| Order writes | Place | 2K/s | 20K/s | Order DB |
| Order reads by id | Support/track | 5K/s | 50K/s | Order DB |
| Order lists by customer | Your Orders | 10K/s | 100K/s | Order DB partition query |

### 2.2 Size math

```text
Product doc avg 5 KB × 200M ASINs ≈ 1 TB raw (+ versions, indexes → several TB)
Customer profile 2 KB × 1B ≈ 2 TB (+ addresses)
Order header 1 KB + lines 0.5 KB × 2.5 ≈ 2.25 KB
50M orders/day × 2.25 KB ≈ 112.5 GB/day ≈ 40 TB/year hot
Retain 7 years → plan cold tier; keep 90d–365d hot
```

### 2.3 Index cost intuition

```text
Every GSI/secondary index ≈ extra write amp + storage
Order by customer_id: natural if PK begins with customer_id
Order by order_id globally: needs GSI or order_id → customer_id map
Email → customer_id: sparse unique index; protect against scans
Never index high-cardinality free text in OLTP for search
```

### 2.4 Transaction boundaries

```text
OK in one TX: order header + lines + outbox row (same partition)
NOT in one TX: decrement inventory in another service DB + order write
            → saga / local reserve API
NOT in one TX: update product + all historical orders
```

### 2.5 IOPS sketch (10×)

```text
Order writes 20K/s × (1 header + 2.5 lines + 1 outbox + 1 idempotency) ≈ 100K row writes/s
With sharding across 100 partitions ≈ 1K writes/s/partition — comfortable for Dynamo/Aurora shards
Product reads 2M/s → must be ~95%+ cached; DB sees ~100K/s keyed gets
```

---

## 3. High-Level Design

### 3.1 Bounded contexts & stores

| Store | Owns | Does not own |
|-------|------|--------------|
| **Customer DB** | identity link, profile, addresses, prefs, payment method **refs** | Orders, products |
| **Product / Catalog DB** | ASIN identity, attributes, media refs, taxonomy links, versions | Inventory qty, customer PII |
| **Order DB** | orders, lines, snapshots, status, payment refs, idempotency | Live catalog, cart |
| **Projections** | Search docs, “Your Orders” read models, PDP cache | Source of truth writes |

### 3.2 Access patterns (design input)

**Product**

| API | Key | Pattern |
|-----|-----|---------|
| GetProduct | `(marketplace, asin)` | Point get |
| BatchGetProducts | list of asins | Batch get |
| PutProduct | same | Conditional put by version |
| ListByCategory | **not** OLTP primary | Projection / search |

**Customer**

| API | Key | Pattern |
|-----|-----|---------|
| GetCustomer | `customer_id` | Point get |
| LookupByEmail | `email_hash` | Unique secondary → id |
| PutAddress | `customer_id` | Update aggregate / child rows |
| GetPaymentRefs | `customer_id` | Point get subset |

**Order**

| API | Key | Pattern |
|-----|-----|---------|
| CreateOrder | `customer_id` + `order_id` | Partition write |
| GetOrder | `order_id` | GSI or encoded PK |
| ListOrders | `customer_id` + time | Partition query |
| UpdateStatus | `customer_id` + `order_id` | Conditional update |
| GetByIdempotencyKey | `(customer_id, key)` | Point get |

### 3.3 Logical schemas

**Customer**

```text
Customer {
  customer_id: ULID/Snowflake
  email_hash, email_encrypted
  status: ACTIVE|DISABLED
  name, phone_encrypted?
  created_at, updated_at
  version
  preferences: { currency, locale, ... }
}

Address {
  customer_id
  address_id
  line1, line2, city, state, postal, country
  is_default_shipping, is_default_billing
  version
}

PaymentMethodRef {
  customer_id
  payment_method_id
  psp_token          # not PAN
  brand_last4
  exp_month, exp_year
  status
}
```

**Product**

```text
Product {
  marketplace_id
  asin
  title, brand, product_type
  status: ACTIVE|INACTIVE|DISCONTINUED
  attribute_set: map/json   # schema’d by product_type
  media: [ { type, url, sort } ]
  category_ids: []
  version                 # monotonic
  created_at, updated_at
}

ProductVersion (optional table) {
  marketplace_id, asin, version
  snapshot_blob
  changed_by, changed_at
}
```

**Order**

```text
Order {
  customer_id             # partition key
  order_id                # sort key (ULID time-sortable)
  status
  currency
  totals: { items, shipping, tax, discount, grand }  # ints
  shipping_address_snapshot
  billing_address_snapshot
  payment_intent_ref
  placed_at
  version
  marketplace_id
}

OrderLine {
  customer_id, order_id
  line_id
  asin, marketplace_id
  quantity
  unit_price_cents        # snapshot
  title_snapshot
  fulfillment_status
}

IdempotencyRecord {
  customer_id
  idempotency_key
  request_hash
  order_id
  status
  created_at, expires_at
}

Outbox {
  customer_id, order_id, event_id
  event_type, payload
  created_at
}
```

### 3.4 Physical key design options

**Option A — DynamoDB-style single-table per service (Order)**

```text
PK = CUSTOMER#{customer_id}
SK = ORDER#{order_id}
SK = ORDER#{order_id}#LINE#{line_id}
SK = IDEMP#{idempotency_key}
SK = OUTBOX#{event_id}

GSI1: PK = ORDER#{order_id} → get by order_id
```

**Option B — Relational sharded (Aurora/MySQL)**

```text
orders: PRIMARY KEY (customer_id, order_id)
UNIQUE (order_id)  -- global unique via snowflake + optional directory
order_lines: PRIMARY KEY (customer_id, order_id, line_id)
INDEX (order_id) -- careful at scale; prefer directory table
```

**Pick for interview:** state both; choose **Order DB = partition by customer_id** (Dynamo or sharded SQL). Product = key-value by `(marketplace, asin)`. Customer = key by `customer_id` + unique email index.

### 3.5 Secondary indexes (disciplined)

| Index | Purpose | Cost / risk |
|-------|---------|-------------|
| `order_id → customer_id` | Support lookup | Sparse GSI or directory |
| `email_hash → customer_id` | Login | Unique; rate-limit |
| `asin → product` | Primary already | — |
| `status + placed_at` on orders | **Avoid** global | Use streams + ops tooling |
| Category → asins | **Not OLTP** | Search / browse projection |

**Rule:** secondary indexes must map to a **real product query** with known QPS and selectivity.

### 3.6 Consistency model

| Entity / operation | Consistency | Mechanism |
|--------------------|-------------|-----------|
| Create order aggregate | Strong | Single partition TX / TransactWrite |
| Order status update | Strong conditional | version check |
| Product publish | Strong on SoT key | version++ |
| PDP read | Eventual OK | Cache + replicas |
| Search index | Eventual | Async projection |
| Customer email unique | Strong | Conditional put unique item |
| Inventory | **Other service** | Not in these DBs |
| Cross-customer query | N/A | Forbidden on OLTP |

### 3.7 CQRS & projections

```text
Product SoT ──stream──► PDP cache warmer
                     ├─► Search indexer
                     └─► Category browse docs

Order SoT ──outbox──► Fulfillment
                   ├─► Analytics lake
                   └─► Customer “active orders” cache (optional)
```

Reads that are not key-friendly **must** use a projection—don’t add a magical GSI for every dashboard.

### 3.8 Evolution strategy

**Expand/contract:**

1. Add nullable field / new attribute key (expand).  
2. Dual-write old+new; backfill.  
3. Dual-read prefer new.  
4. Stop writing old; remove (contract).

**Product attributes:** schema registry per `product_type`; unknown fields preserved as opaque map with validation at write edge.

**Order immutability:** prefer new events / status transitions over rewriting line price history; corrections via adjustment entities.

### 3.9 Multi-tenancy / marketplace

```text
Product PK: MARKETPLACE#{id}#ASIN#{asin}
Order includes marketplace_id; partition still customer_id (customer shops one locale session)
```

Don’t mix EU PII residency into US cell without policy controls—**residency-aware cell routing**.

### 3.10 Trade-offs

| Decision | Pros | Cons | Pick |
|----------|------|------|------|
| Separate DBs per domain | Autonomy, scale | App joins | Yes |
| Orders PK customer_id | Efficient “Your Orders” | Get-by-order_id needs GSI | Yes |
| Embed lines in order doc | Single get | Large orders limits | OK with max lines |
| Normalized lines table | Large orders | Extra reads | SQL shards |
| Search in SQL LIKE | Simple | Won’t scale | No |
| Global status index | Ops queries | Hot partitions | Async ops DB |

---

## 4. Architecture Diagram

### 4.1 Stores and flows

```text
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Customer API │     │ Catalog API  │     │  Order API   │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Customer DB  │     │ Product DB   │     │  Order DB    │
│ PK: cust_id  │     │ PK: mkt+asin │     │ PK: cust_id  │
│ GSI: email   │     │ versions     │     │ GSI: order_id│
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │                    ├─stream─► Search    │
       │                    ├─stream─► PDP cache │
       │                    │                    ├─outbox─► Bus
       │                    │                    │
       └────────── checkout reads ───────────────┘
```

### 4.2 Order aggregate write path

```text
PlaceOrder
  → BeginIdempotency(customer_id, key)
  → Transact:
       Put Order
       Put Lines
       Put Outbox
       Commit Idempotency → order_id
  → Return order_id
```

### 4.3 Get order by id

```text
GetOrder(order_id)
  → GSI/directory: order_id → customer_id
  → Get PK=customer_id, SK=order_id (+ lines)
  → Authorize caller owns customer_id or support role
```

### 4.4 Product versioning

```text
PutProduct(asin, expected_version, body)
  → Conditional update version = expected+1
  → Append ProductVersion snapshot
  → Emit ProductChanged
```

### 4.5 Shard map (orders)

```text
customer_id ──hash──► shard / cell
                  ┌─ Shard 0
                  ├─ Shard 1
                  ├─ ...
                  └─ Shard N
Hot customer_id → dedicated shard / capacity mode
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. **Order aggregate atomicity** — no header without lines (or explicit empty forbidden).  
2. **Idempotent create** — `(customer_id, idempotency_key)` unique.  
3. **Conditional versions** on product & order status.  
4. **Snapshots on order** — price/title/address frozen at place.  
5. **PII minimization** — payment tokens only; encrypt email/phone.  
6. **Outbox co-committed** with order for reliable events.  
7. **No silent overwrites** — request hash mismatch → 409.  
8. **Authorization on get-by-order_id** after directory lookup.  
9. **Soft delete products**; orders remain readable.  
10. **Backup / PITR** on all three stores; tested restores.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Partial line write | Transaction / single-doc aggregate |
| GSI lag (Dynamo) | Read-after-write via PK; accept GSI lag for support |
| Dual-write projection drift | Stream from SoT only; reconciler |
| Shard outage | Multi-AZ; cell failover; dual-powered critical tables |
| Bad migration | Expand/contract + feature flags |

### 5.2 Scalability

| Scale | Change |
|-------|--------|
| 1× | 1 logical DB each; replicas; Redis product cache |
| 10× | Hash shards on customer_id / asin; GSI directory; archive jobs |
| 100× | Cell-local order DBs; product regional replicas; CQRS lists |
| 1,000× | Hierarchical customer directories; cold order object storage; sparse indexes only |

**Partitioning details**

- **Orders:** `customer_id` hash → N shards; ULID `order_id` for time sort.  
- **Products:** `asin` hash or marketplace-first; replicate reads globally.  
- **Customers:** `customer_id` hash; email unique index in dedicated sparse table.

**Write sharding anti-patterns**

- Partition orders by `status` → hot “PLACED” partition.  
- Partition products by `category` → uneven.  
- Global incrementing integer order_id without directory → bottleneck.

### 5.3 Maintainability / operability

- Document **access pattern catalog** as the schema contract.  
- Migration runbooks with expand/contract checklists.  
- Data quality jobs: orphan lines = 0; totals = sum(lines).  
- TTL on idempotency rows (e.g., 24–72h).  
- Archival: move orders > N days to cold store; keep stub for get-by-id.  
- PII access audit logs.  
- Schema registry for product attributes.

### 5.4 Consistency deep dive

**Single-aggregate strong:** Order create uses TransactWriteItems / SQL TX on shard.

**Cross-aggregate:** Checkout calls Inventory + Payments + Order—**saga**, not 2PC across DBs.

**Read-your-writes:** After place-order, read via PK (`customer_id`,`order_id`), not GSI.

**Product eventual readers:** PDP cache may lag; checkout fetches price from Pricing SoT (may be same catalog version service).

### 5.5 Secondary index deep dive

**Directory table for order_id:**

```text
OrderDirectory {
  pk: order_id
  customer_id
  created_at
}
```

Written in same transaction as order when possible; or relative consistency with retry on miss.

**Email uniqueness:**

```text
EmailIndex {
  pk: EMAIL#{email_hash}
  customer_id
}
Conditional put attribute_not_exists(pk)
```

**Why not GSI on order status:** support tools should consume streams into an **ops index** with controlled retention, not overload OLTP.

### 5.6 Schema evolution deep dive

**Additive JSON attributes:**

```text
product.attribute_set.color = "blue"  # new key OK
```

**Breaking change (rename `name` → `title`):**

1. Write both.  
2. Backfill readers.  
3. Read title prefer, fallback name.  
4. Stop name; remove.

**Enum evolution:** only add statuses; never reuse meanings; map unknown → `UNKNOWN` in readers.

**Large product docs:** keep media in object storage; DB stores refs; avoid 400KB item limits by splitting locale overlays if needed.

### 5.7 Snapshot & legal/support

Orders must answer: “What did the customer buy at what price?” years later even if ASIN title changed → **line snapshots**.

ProductVersion table supports seller tooling / dispute (“what did PDP show?”) with approximate time travel.

### 5.8 Security & privacy

- Field-level encryption for PII.  
- Separate IAM roles per store.  
- Tokenize payment methods via PSP.  
- Redact logs.  
- GDPR/CCPA: delete/anonymize customer; **retain order invoices** per law with minimized PII.

### 5.9 Observability

| Metric | Why |
|--------|-----|
| `product_get_p99` | PDP |
| `order_write_p99` | Checkout |
| `idempotency_conflict_rate` | Client retries |
| `gsi_lag_seconds` | Support UX |
| `shard_hot_partition_throttle` | Scale pain |
| `migration_dual_write_mismatch` | Evolution safety |
| `orphan_line_count` | Invariant |
| `pii_access_count` | Security |

---

## 6. Wrap-Up

### 6.1 What we designed

A **polyglot, access-pattern-first** database design for Customer, Product, and Order aggregates: keys and partitions that match real queries, disciplined secondary indexes, strong consistency within aggregates, CQRS for unkeyable reads, and expand/contract evolution through 10×–1,000× growth.

### 6.2 Key decisions worth defending

1. **Three stores / bounded contexts** — not one mega ERD.  
2. **Access patterns before schema.**  
3. **Orders partitioned by customer_id.**  
4. **order_id directory/GSI** for support lookup.  
5. **Product keyed by marketplace+asin** with versions.  
6. **Order line snapshots** for price/title.  
7. **Outbox with order TX.**  
8. **No OLTP product search.**  
9. **Expand/contract migrations.**  
10. **Integer money; encrypted PII.**

### 6.3 Risks & follow-ups

| Risk | Follow-up |
|------|-----------|
| GSI lag surprises | PK read paths; document lag |
| Hot reseller customer | Isolation / burst |
| Oversized order aggregates | Cap lines; chunk |
| Projection drift | Reconcile jobs |
| Cross-border PII | Residency cells |
| Analytics pressure | Enforce event highway |

### 6.4 How to present in 45 minutes

1. Access patterns whiteboard (8 min)  
2. Schemas + keys (10 min)  
3. Partitioning + indexes (8 min)  
4. Consistency + order TX/outbox (8 min)  
5. Evolution + scale jumps (6 min)  
6. Q&A (remainder)

---

## 7. Deeper / Related Interview Questions

### 7.1 Modeling

**Q1: Why not put inventory_count on Product?**  
A: Different consistency/write rate; owned by Inventory service; product page shows digest projection.

**Q2: Order line vs separate shipment tables?**  
A: MVP lines + fulfillment_status; shipments as child entity when split FC appears.

**Q3: Should customer addresses be normalized globally?**  
A: Per-customer children; don’t dedupe globally across users (PII + UX ownership).

**Q4: Product variants as separate ASINs or parent/child?**  
A: Amazon-style: variation family with child ASINs; each child is buyable key.

### 7.2 Keys & indexes

**Q5: ULID vs UUID for order_id?**  
A: ULID/snowflake sorts by time and avoids random write scatter in SK; still shard by customer.

**Q6: Can email be primary key?**  
A: No—emails change; use immutable customer_id; email as unique secondary.

**Q7: How does GetOrder work if GSI is unavailable?**  
A: Fallback directory table; or encode customer shard hint in order_id (careful with leakage).

**Q8: Secondary index on (asin, placed_at) for “orders of this product”?**  
A: High write amp; use analytics/stream. Support tools ≠ OLTP schema.

### 7.3 Consistency

**Q9: Read-after-write for “Thank you” page?**  
A: Return order payload from write path or PK read; don’t rely on GSI/search.

**Q10: Two devices update default address concurrently.**  
A: Conditional version; loser retries; checkout uses explicit address_id snapshot.

**Q11: Exactly-once order?**  
A: Effectively-once via idempotency + unique constraints.

### 7.4 Scale

**Q12: 100× order list latency.**  
A: Paginate; cache active orders; archive cold; ensure partition query not fan-out.

**Q13: Product item size limit hit.**  
A: Split locale overlays / large HTML into object storage; keep buyable attrs in item.

**Q14: Shard rebalancing orders.**  
A: Consistent hash with virtual nodes; dual-read migration; never scan all orders.

### 7.5 Evolution

**Q15: Add `gift_wrap` boolean.**  
A: Additive nullable; default false; deploy writers; then readers.

**Q16: Split Product into Product + Offer.**  
A: New Offer service; product remains identity; dual-read offers; expand/contract APIs.

**Q17: Migrate MySQL to Dynamo.**  
A: Dual-write period; shadow reads; cutover per cell; reconcile checksums.

### 7.6 Privacy & compliance

**Q18: Right to be forgotten vs order retention.**  
A: Anonymize customer profile; keep legally required invoice fields minimized; document policy.

**Q19: Support agent access.**  
A: Audited break-glass; field-level authz; no wholesale dumps.

### 7.7 Failure interviews

**Q20: Outbox publisher down.**  
A: Orders still committed; catch-up from outbox table; consumers idempotent; alarm on lag.

**Q21: Partial TransactWrite failure.**  
A: All-or-nothing; client retries same idempotency key.

**Q22: Cache serves deleted product.**  
A: Short TTL + explicit invalidate on status change; checkout blocks inactive.

---

## 8. Appendices

## Appendix A — Example physical schemas (SQL sketch)

```sql
CREATE TABLE customers (
  customer_id BIGINT PRIMARY KEY,
  email_hash BYTEA NOT NULL UNIQUE,
  email_enc BYTEA NOT NULL,
  status TEXT NOT NULL,
  profile_json JSONB NOT NULL,
  version INT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE products (
  marketplace_id TEXT NOT NULL,
  asin TEXT NOT NULL,
  title TEXT NOT NULL,
  status TEXT NOT NULL,
  attrs JSONB NOT NULL,
  media JSONB NOT NULL,
  version INT NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (marketplace_id, asin)
);

CREATE TABLE orders (
  customer_id BIGINT NOT NULL,
  order_id BIGINT NOT NULL,
  status TEXT NOT NULL,
  currency CHAR(3) NOT NULL,
  totals JSONB NOT NULL,
  shipping_snapshot JSONB NOT NULL,
  payment_ref TEXT,
  version INT NOT NULL,
  placed_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (customer_id, order_id)
);
CREATE UNIQUE INDEX orders_order_id_uq ON orders(order_id);

CREATE TABLE order_lines (
  customer_id BIGINT NOT NULL,
  order_id BIGINT NOT NULL,
  line_id INT NOT NULL,
  asin TEXT NOT NULL,
  qty INT NOT NULL,
  unit_price_cents BIGINT NOT NULL,
  title_snapshot TEXT NOT NULL,
  PRIMARY KEY (customer_id, order_id, line_id)
);

CREATE TABLE order_idempotency (
  customer_id BIGINT NOT NULL,
  idem_key TEXT NOT NULL,
  request_hash BYTEA NOT NULL,
  order_id BIGINT,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL,
  PRIMARY KEY (customer_id, idem_key)
);
```

## Appendix B — DynamoDB item sketches

```text
PK=CUST#123 SK=PROFILE
PK=CUST#123 SK=ADDR#A1
PK=CUST#123 SK=ORDER#01J...  entity_type=order ...
PK=CUST#123 SK=ORDER#01J...#LINE#1
PK=EMAIL#<hash> SK=CUST  → customer_id
GSI1 PK=ORDER#01J... SK=CUST#123
```

## Appendix C — Access pattern allowlist

1. GetProduct(marketplace, asin)  
2. BatchGetProducts  
3. PutProduct conditional  
4. GetCustomer  
5. LookupCustomerByEmail  
6. PutCustomer / PutAddress  
7. CreateOrder (idempotent)  
8. GetOrderById  
9. ListOrdersByCustomer(cursor)  
10. UpdateOrderStatus conditional  

Anything else → projection or warehouse.

## Appendix D — Scale checklist

- [ ] Patterns documented before indexes  
- [ ] Orders PK includes customer_id  
- [ ] Idempotency table exists  
- [ ] Outbox co-committed  
- [ ] Product version conditional  
- [ ] Line snapshots  
- [ ] PII encryption  
- [ ] Archival plan  
- [ ] No OLTP search  
- [ ] Expand/contract runbook  

## Appendix E — Glossary

| Term | Meaning |
|------|---------|
| Aggregate | Consistency boundary (Order + lines) |
| CQRS | Separate write model vs read projections |
| GSI | Global secondary index |
| Expand/contract | Safe schema migration pattern |
| Directory | order_id → customer_id map |
| Snapshot | Point-in-time copy on order lines |
| Outbox | Reliable event publish from DB |

## Appendix F — Estimation cheat-sheet

```text
Order storage/day ≈ orders/day × ~2–3 KB
Product reads must be cached at 10×+
GSI write amp ≈ +1 write per index per item change
Shard count ≈ peak_writes / per_shard_budget
```

## Appendix G — Status machines (order)

```text
PLACED → PAID → ALLOCATED → SHIPPED → DELIVERED
PLACED → CANCELLED
SHIPPED → RETURN_STARTED → RETURNED
Illegal: DELIVERED → PLACED
```

## Appendix H — Invariant tests

1. Create order twice same key → one order_id.  
2. Totals == sum(line qty × unit_price) + shipping + tax − discount.  
3. GetOrder authorize denies cross-customer.  
4. Product version conflict → 409.  
5. Email unique conflict → 409.  
6. Outbox count == order creates (lag bounded).  

## Appendix I — Archival strategy

```text
Hot DB: 90–365 days
Warm: secondary storage / cheaper replicas 1–3 years
Cold: object store serialized orders + index stub for GetOrder
Job: nightly move; keep directory pointer
```

## Appendix J — Evolution playbook

| Change | Pattern |
|--------|---------|
| Add field | Expand |
| Rename | Dual-write → dual-read → contract |
| Split service | New store + sync + cutover |
| New index | Backfill then flip reads |
| Drop field | Confirm zero reads; contract |

## Appendix K — Anti-patterns

- `SELECT * FROM orders WHERE status='PLACED'` on OLTP  
- Mutable price on historical order lines  
- Email as PK  
- Inventory column on product row as SoT  
- Unbounded JSON without size guards  
- Shared “one Postgres” for all domains at 100×  

## Appendix L — Interview closing line

> “We design databases from access patterns: customer-partitioned orders, marketplace-keyed products, sparse secondary indexes only where product requires them, strong aggregate transactions with outbox, and expand/contract evolution—so 10× is sharding and 100× is cells and CQRS, not heroic joins.”

---

*End of customer / order / product database system design.*
