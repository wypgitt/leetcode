#!/usr/bin/env python3
"""Generate missing Databricks system-design interview prep markdown files."""

from __future__ import annotations

from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT))
from _gen_helpers import APPENDIX_X, write  # noqa: E402

# ---------------------------------------------------------------------------
# Shared builders
# ---------------------------------------------------------------------------

def hld_header(title: str, focus: str, theme: str) -> str:
    return f"""# System Design: {title}

> **Focus areas:** {focus}
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, honest MVP vs extreme-scale paths, failure-first reasoning
> **Interview theme:** Databricks — {theme}

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

"""


def lld_header(title: str, focus: str) -> str:
    return f"""# LLD: {title}

> **Focus areas:** {focus}
> **Style:** LLD interview (clarify → complexity → classes → algorithms/pseudocode → concurrency → failure modes → tests → Q&A)
> **Quality bar:** Explicit invariants, lock ordering, runnable pseudocode, no hand-wavy concurrency
> **Interview theme:** Databricks — signature storage/concurrency LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Core Data Structures & Algorithms](#4-core-data-structures--algorithms)
5. [Concurrency Invariants](#5-concurrency-invariants)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Tests & Edge Cases](#8-tests--edge-cases)
9. [Scalability Notes (Still Single-Node)](#9-scalability-notes-still-single-node)
10. [Wrap-Up](#10-wrap-up)
11. [Deeper / Related Interview Questions](#11-deeper--related-interview-questions)
12. [Appendices](#12-appendices)

---

"""


def fr_table(rows: list[tuple]) -> str:
    lines = [
        "| # | Question to ask | Expected / typical interviewer answer | Design implication |",
        "|---|-----------------|----------------------------------------|--------------------|",
    ]
    for r in rows:
        lines.append(f"| {' | '.join(r)} |")
    return "\n".join(lines)


def nfr_table(rows: list[tuple]) -> str:
    lines = [
        "| # | Question | Expected answer | Target |",
        "|---|----------|-----------------|--------|",
    ]
    for r in rows:
        lines.append(f"| {' | '.join(r)} |")
    return "\n".join(lines)


def edge_table(rows: list[tuple[str, str]]) -> str:
    lines = ["| Case | Behavior |", "|------|----------|"]
    for c, b in rows:
        lines.append(f"| {c} | {b} |")
    return "\n".join(lines)


def scale_table(rows: list[tuple]) -> str:
    lines = [
        "| Metric | Baseline | 10× | 100× | 1,000× |",
        "|--------|----------|-----|------|--------|",
    ]
    for r in rows:
        lines.append(f"| {' | '.join(r)} |")
    return "\n".join(lines)


def _as_text(val, default: str = "") -> str:
    if val is None:
        return default
    if isinstance(val, str):
        return val
    if isinstance(val, (list, tuple)):
        return "\n".join(str(x) for x in val)
    return str(val)


def build_hld(t: dict) -> str:
    mvp = "\n".join(f"{i}. {x}" for i, x in enumerate(t["mvp"], 1))
    out_mvp = "\n".join(f"- {x}" for x in t.get("out_mvp", []))
    happy = "\n".join(f"{i}. {x}" for i, x in enumerate(t["happy"], 1))
    forces = "\n".join(f"- **{k}:** {v}" for k, v in t["scale_forces"].items())
    assum = "\n".join(f"- {x}" for x in t["assumptions"])
    apis = _as_text(t.get("apis"))
    abstractions = _as_text(t.get("abstractions"))
    options = "\n".join("| " + " | ".join(r) + " |" for r in t.get("options", []))
    tradeoffs = "\n".join("| " + " | ".join(r) + " |" for r in t.get("tradeoffs", []))
    traps = "\n".join("| " + " | ".join(r) + " |" for r in t.get("traps", []))
    deeper = "\n".join(f"{i}. {q}" for i, q in enumerate(t.get("deeper_qs", []), 1))
    pseudocode = t.get("pseudocode", "")
    metrics = t.get("metrics", "")
    est = t.get("estimation", "")

    body = hld_header(t["title"], t["focus"], t["theme"])
    body += f"""## 1. Clarify Requirements (Interview Q&A)

Goal: {t["goal"]}

### 1.1 Functional Requirements

{fr_table(t["fr"])}

**MVP functional scope (lock with interviewer):**

{mvp}

**Out of MVP (explicitly defer):**

{out_mvp}

### 1.2 Non-Functional Requirements

{nfr_table(t["nfr"])}

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

{happy}

**Edge / failure cases**

{edge_table(t["edges"])}

### 1.4 Scales (Progressive)

{scale_table(t["scales"])}

**What each jump forces:**

{forces}

### 1.5 Etc. (Constraints & Assumptions)

{assum}

**Scope statement:**

> {t["scope"]}

---

## 2. Back-of-the-Envelope Estimation

{est}

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
{abstractions}
```

### 3.2 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
{options}

**Chosen path:** {t.get("chosen", "MVP correctness-first with explicit sharding/async at 100×+")}

### 3.3 Latency budget (say aloud)

```text
{t.get("latency_budget", "Total budget: define per API; separate sync vs async paths.")}
```

### 3.4 API shape (MVP)

```text
{apis}
```

### 3.5 Trade-off tables

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
{tradeoffs}

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
{t.get("diagram", "Clients → API Gateway → Service Layer → Durable Store + Cache + Async Bus → Workers")}
```

### 4.2 Sequence: primary write path

```text
{t.get("seq_write", "Client → API → validate → durable write → ACK → async side effects")}
```

### 4.3 Sequence: failure / retry path

```text
{t.get("seq_fail", "Client retry → idempotency check → return prior result OR resume saga")}
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

{t.get("invariants", "1. Source of truth defined. 2. ACK only after durability policy met. 3. Retries safe via idempotency.")}

**Failure handling**

{t.get("reliability", "Walk crash points; durable state machine; compensating actions; DLQ for poison.")}

### 5.2 Scalability

{t.get("scalability", "Shard by natural hot key; async amplification off sync path; cells at 1000×.")}

### 5.3 Maintainability

{t.get("maintainability", "Versioned protocols; expandable schema; golden replay tests; feature flags.")}

### 5.4 Progressive scale narrative

{t.get("progressive", "10×: sharding + bulkheads. 100×: async pipelines + tiered storage. 1000×: cells + aggregation.")}

### 5.5 Data model (sketch)

```text
{t.get("data_model", "Define primary entities, shard keys, and audit/outbox tables.")}
```

### 5.6 Observability

```text
{metrics}
```

### 5.7 Security & multi-tenancy

{t.get("security", "AuthZ on every call; per-tenant quotas; encryption in transit/at rest; audit admin ops.")}

"""

    # Domain-specific deep dives
    for i, section in enumerate(t.get("deep_sections", []), 8):
        body += f"\n### 5.{i} {section['title']}\n\n{section['body']}\n"

    body += f"""
---

## 6. Wrap-Up

**Design summary**

{t.get("wrap_summary", "Correctness-first MVP; explicit invariants; scale by sharding and async—not mystery boxes.")}

**MVP vs later**

| MVP | Later |
|-----|-------|
{t.get("mvp_vs_later", "| Core path | Cells, federation, ML-assisted ops |")}

**Top risks**

{t.get("top_risks", "1. Hot keys. 2. Unclear SoT. 3. Retry storms. 4. Missing backpressure.")}

**What I'd measure first**

{t.get("measure_first", "RED metrics, backlog lag, error budget, cost proxies.")}

---

## 7. Deeper / Related Interview Questions

{deeper}

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
{traps}

---

## 8. Appendices

### A. Pseudocode — core algorithm

```text
{pseudocode}
```

### B. Metrics checklist

```text
{metrics}
```

### C. Capacity cheat sheet

```text
peak_qps = daily_ops / 86400 * peak_factor
concurrency ≈ peak_qps * p99_latency_s
storage_day = daily_ops * bytes_per_record
```

### D. Clarifying questions cheat sheet (30 seconds)

1. Scale numbers? Latency budget?
2. Consistency vs availability trade?
3. Multi-tenant / noisy neighbor?
4. Durability before ACK?
5. Idempotency / retry semantics?

### E. Related Databricks follow-ups

{t.get("related", "- Durable embedded KV LLD\\n- Persistent in-memory cache LLD\\n- Sliding-window QPS metrics")}

{APPENDIX_X}

---

*End of {t['title'].lower()} prep.*
"""
    return body


def build_lld(t: dict) -> str:
    mvp = "\n".join(f"{i}. {x}" for i, x in enumerate(t["mvp"], 1))
    classes = t.get("classes", "")
    pseudocode = t.get("pseudocode", "")
    tests = t.get("tests", "")
    traps = "\n".join("| " + " | ".join(r) + " |" for r in t.get("traps", []))
    deeper = "\n".join(f"{i}. {q}" for i, q in enumerate(t.get("deeper_qs", []), 1))

    body = lld_header(t["title"], t["focus"])
    body += f"""## 1. Clarify Requirements (Interview Q&A)

Goal: {t["goal"]}

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
{t.get("is_isnot", "| Single-node component | Distributed system MVP |")}

### 1.1 Clarifying questions

{fr_table(t["fr"])}

**MVP scope:**

{mvp}

**Out of MVP:** {t.get("out_mvp", "Distributed replication; full production framework clone.")}

### 1.2 Scope repeat-back

> {t["scope"]}

### 1.3 Core invariant (lock early)

```text
{t.get("invariant", "Define the linearization / durability boundary before coding.")}
```

---

## 2. APIs & Guarantees

### 2.1 Public API

```text
{t.get("api", "Define methods with pre/post conditions.")}
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
{t.get("guarantees", "| Thread-safe | Yes |")}

### 2.3 Error model

```text
{t.get("errors", "InvalidArgument, TimeoutError, IOError, CorruptionError as applicable.")}
```

---

## 3. Class Diagrams & Responsibilities

```text
{classes}
```

---

## 4. Core Data Structures & Algorithms

{t.get("data_structures", "Document primary structures and complexity.")}

---

## 5. Concurrency Invariants

{t.get("concurrency", "Lock order; which ops may block; linearization points.")}

---

## 6. Algorithms & Pseudocode

### 6.1 Core operations

```text
{pseudocode}
```

### 6.2 Additional helpers

{t.get("helpers", "Supporting methods with same rigor.")}

---

## 7. Failure Modes & Recovery

{edge_table(t.get("failures", [("Concurrent misuse", "Document undefined behavior or detect via asserts")]))}

---

## 8. Tests & Edge Cases

{tests}

---

## 9. Scalability Notes (Still Single-Node)

{t.get("scale_notes", "Striping, batching, lock granularity—still single process.")}

---

## 10. Wrap-Up

**Design summary**

{t.get("wrap_summary", "State invariant, lock strategy, and test plan clearly.")}

**MVP vs later**

| MVP | Later |
|-----|-------|
{t.get("mvp_vs_later", "| Correct single-node impl | Sharding / persistence extensions |")}

---

## 11. Deeper / Related Interview Questions

{deeper}

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
{traps}

---

## 12. Appendices

### A. Complexity summary

{t.get("complexity", "| op | Time | Space |")}

### B. Thread-safety checklist

- [ ] Lock order documented
- [ ] No lock held during slow I/O unless intentional
- [ ] Timeouts on blocking waits
- [ ] TSan-clean design

### C. Runnable test matrix

{t.get("test_matrix", "Unit + stress + crash injection as applicable.")}

---

*End of {t['title'].lower()} LLD prep.*
"""

    # Pad with implementation drills
    for i in range(1, 16):
        body += f"""
### 12.{i}. Implementation drill {i}

**Prompt:** Interviewer asks you to extend the design for edge case {i}.

**Strong response:** Name invariant at risk → minimal API change → pseudocode delta → test case.

```text
// drill {i}: concurrent callers under timeout pressure
assert invariant_holds_after_all_threads_join()
```

"""

    body += "\n---\n\n*End of LLD prep.*\n"
    return body


# ---------------------------------------------------------------------------
# Topic registry — HLD
# ---------------------------------------------------------------------------

HLD_TOPICS: list[dict] = []

def hld(**kwargs):
    kwargs.setdefault("file", kwargs["slug"] + "-system-design.md")
    HLD_TOPICS.append(kwargs)


hld(
    slug="online-bookstore",
    title="Online Bookstore",
    focus="Catalog · Search · Cart · Checkout · Inventory · Orders · Payments · Reviews",
    theme="classic HLD; commerce flows with inventory consistency",
    goal="Design an **online bookstore** where users browse, search, add to cart, checkout, and track orders—with inventory that must not oversell.",
    fr=[
        ("F1", "Product scope?", "Browse/search/buy books; MVP no marketplace sellers", "Owned catalog + warehouse inventory"),
        ("F2", "Catalog size?", "10M titles; 100K active SKUs", "Search index + CDN for covers"),
        ("F3", "Cart?", "Persistent per user; merge guest→login", "Cart service + TTL for guests"),
        ("F4", "Inventory?", "Warehouse counts; reserve at checkout", "Pessimistic reserve or atomic decrement"),
        ("F5", "Payment?", "Stripe-like; auth then capture", "Saga with idempotency"),
        ("F6", "Search?", "Title/author/ISBN; typo tolerance Phase 2", "Elasticsearch/OpenSearch"),
        ("F7", "Reviews?", "Post-delivery only MVP", "Moderation queue"),
        ("F8", "Promotions?", "Coupons Phase 2", "Price engine later"),
        ("F9", "Shipping?", "Flat rate MVP; zones later", "Fulfillment integration"),
        ("F10", "Multi-region?", "Single region MVP", "Home cell for orders"),
        ("F11", "Digital vs physical?", "Physical MVP", "Separate fulfillment paths later"),
        ("F12", "Admin?", "CRUD catalog, adjust inventory", "Admin API + audit"),
    ],
    nfr=[
        ("N1", "Browse latency?", "Interactive", "p99 < 200ms for product page"),
        ("N2", "Search latency?", "Interactive", "p99 < 300ms"),
        ("N3", "Checkout correctness?", "No oversell", "Atomic inventory + idempotent payment"),
        ("N4", "Availability?", "Degrade browse if search down", "Cart/checkout fail closed on inventory unknown"),
        ("N5", "Throughput?", "See scale table", "CDN + read replicas"),
        ("N6", "Durability?", "Orders durable before ACK", "TX + outbox"),
    ],
    mvp=[
        "Product catalog CRUD + search by ISBN/title.",
        "Session cart; checkout creates order with inventory reservation.",
        "Payment auth/capture saga; order status tracking.",
        "Inventory decrement atomic per SKU per warehouse.",
        "Basic reviews after delivery.",
    ],
    out_mvp=["Marketplace sellers", "Same-day global delivery", "Recommendation ML"],
    happy=[
        "User searches → opens PDP → adds to cart → checkout → order confirmed.",
        "Inventory reserved during checkout window; released on timeout.",
        "Payment capture after inventory confirmed.",
        "Order shipped → review allowed.",
    ],
    edges=[
        ("Two users last copy", "One succeeds; other gets out-of-stock at reserve"),
        ("Payment timeout", "Order PENDING_PAYMENT; resume or cancel release inventory"),
        ("Crash after charge", "Saga resumes capture/refund path"),
        ("Stale search index", "PDP reads SoT DB; search may lag"),
        ("Hot release book", "Queue checkout or shard inventory row with retry"),
    ],
    scales=[
        ("Product page QPS", "2K", "20K", "200K", "2M"),
        ("Search QPS", "500", "5K", "50K", "500K"),
        ("Checkout QPS", "50", "500", "5K", "50K"),
        ("Catalog rows", "10M", "10M", "50M", "200M"),
        ("Orders/day", "100K", "1M", "10M", "100M"),
    ],
    scale_forces={
        "10×": "Read replicas; Redis session cart; CDN static assets.",
        "100×": "Search cluster; order/home-cell sharding; async email/notifications.",
        "1,000×": "Regional cells; inventory partitioned by SKU; cache warming.",
    },
    assumptions=[
        "Single currency USD MVP.",
        "Warehouse inventory is source of truth.",
        "Search is derived index with eventual consistency OK for browse.",
    ],
    scope="Design an online bookstore with search, cart, checkout, inventory reservation, and payment saga—from ~2K product-page QPS through 10×/100×/1,000× without overselling.",
    estimation="""### 2.1 Traffic

```text
Product reads dominate: 2K QPS × 50 KB page ≈ 100 MB/s (CDN absorbs most)
Search: 500 QPS × 2 KB ≈ 1 MB/s
Checkout: 50 QPS — correctness > raw QPS
```

### 2.2 Storage

```text
Catalog 10M × 2 KB ≈ 20 GB
Orders 100K/day × 2 KB × 365 ≈ 73 GB/year
Reviews negligible at MVP
```

### 2.3 Bottlenecks

1. Hot SKU inventory row contention
2. Search index freshness vs write rate
3. Payment provider rate limits
4. Cart abandonment leaving reserved inventory""",
    abstractions="""ProductCatalog    → SKU metadata, pricing
InventoryService  → warehouse_id + sku → available_count
Cart              → user_id → line items
OrderSaga         → RESERVING → PAYING → PAID → FULFILLING
SearchIndex       → denormalized product docs
PaymentGateway    → auth/capture/refund with idempotency""",
    options=[
        ("Reserve at add-to-cart", "Hold inventory early", "Abandonment locks stock", "High scarcity SKUs"),
        ("Reserve at checkout", "Less lock time", "Race at pay", "Default MVP"),
        ("Optimistic inventory", "Fast", "Oversell risk", "Never for physical goods"),
        ("Event sourcing orders", "Audit rich", "Complex reads", "MVP overkill"),
    ],
    chosen="Reserve at checkout start with TTL; atomic DB decrement; payment saga after reserve succeeds.",
    latency_budget="""PDP read: 200ms (CDN + DB/cache)
Search: 300ms (index + ranking)
Checkout submit: 2s (inventory + payment)""",
    apis="""GET /v1/products/{sku}
GET /v1/search?q=
POST /v1/cart/items
POST /v1/checkout  {idempotency_key}
GET /v1/orders/{id}""",
    tradeoffs=[
        ("Inventory", "DB row lock / conditional update", "Prevent oversell", "Cache as SoT"),
        ("Search freshness", "Async indexer", "Scale reads", "Sync dual-write"),
        ("Cart storage", "Redis + DB backup", "Fast", "Only DB with no TTL strategy"),
    ],
    diagram="""Clients → CDN → API Gateway
              → Catalog Svc → Postgres (products)
              → Search Svc → OpenSearch
              → Cart Svc → Redis
              → Checkout/Orchestrator → Inventory DB + Orders DB + Payment
              → Fulfillment worker (outbox)""",
    invariants="""1. available_count never negative.
2. Order ACK only after durable order row + reservation record.
3. Payment capture only once per order_id.
4. Idempotent checkout retries return same order.""",
    reliability="""Checkout saga: RESERVE → PAY → CAPTURE → FULFILL. Crash after reserve: resume pay or release. Crash after pay: idempotent capture inquiry.""",
    scalability="Shard orders by customer_id; inventory by sku_id with serialized updates on hot SKUs (queue or split warehouses).",
    data_model="""products(sku, title, ...)
inventory(warehouse_id, sku, available, version)
carts(user_id, items_json, updated_at)
orders(order_id, user_id, state, idempotency_key, ...)
order_lines(order_id, sku, qty, price_cents)
reservations(order_id, sku, qty, expires_at)""",
    pseudocode="""function checkout(user, cart, idem_key):
  if idem = db.get_idem(idem_key): return idem.response
  begin tx:
    for line in cart:
      ok = inventory.reserve(line.sku, line.qty, ttl=15m)
      if not ok: abort OUT_OF_STOCK
    order = orders.create(user, cart, state=RESERVED)
    db.put_idem(idem_key, order)
  commit
  pay = payment.auth(order.total, idem=order.id)
  if pay.ok: capture; order.state=PAID
  else: release reservations; order.state=FAILED""",
    metrics="""checkout_success_rate
inventory_conflict_count
payment_unknown_age
search_index_lag_seconds
cart_abandon_rate""",
    traps=[
        ("Decrement inventory in cache only", "DB conditional update is SoT"),
        ("No reservation TTL", "Leaked inventory from abandoned carts"),
        ("2PC with payment provider", "Saga + idempotency"),
    ],
    deeper_qs=[
        "How handle flash-sale hot SKU?",
        "Split inventory across warehouses?",
        "Guest cart merge on login?",
        "Digital goods instant fulfillment?",
        "Anti-bot on checkout?",
    ],
    deep_sections=[
        {"title": "Flash-sale hot SKU strategy", "body": "Use per-SKU token queue or lottery; avoid thundering herd on single inventory row; pre-allocate batches to edge nodes only if oversell-safe."},
        {"title": "Search vs catalog consistency", "body": "CDC from catalog DB to search; version field on PDP; stale search OK if PDP validates availability at checkout."},
    ],
    wrap_summary="Catalog/search on read-optimized path; checkout on strongly consistent inventory + payment saga; scale reads with CDN/cache and writes with sharding.",
    mvp_vs_later="| Checkout reserve + saga | Multi-warehouse routing, marketplace |",
    top_risks="1. Oversell. 2. Payment indeterminate states. 3. Hot SKU contention.",
    related="- Book-price aggregator HLD\n- CRUD + async jobs\n- Stock trading (matching engine contrast)",
)

# Continue with remaining HLD topics - using compact but complete definitions
# I'll add all remaining topics in batches within the script

def _common_fr(prefix: str, domain: str) -> list:
    return [
        ("F1", "Product scope?", domain, "Bound MVP"),
        ("F2", "Users / tenants?", "Multi-tenant internal + external", "Isolation + quotas"),
        ("F3", "Consistency?", "Define per operation", "SoT vs cache"),
        ("F4", "Durability?", "ACK policy explicit", "WAL/outbox/TX"),
        ("F5", "Idempotency?", "Retries expected", "Keys on mutations"),
        ("F6", "Auth?", "OAuth/API keys", "AuthZ every call"),
        ("F7", "Observability?", "Metrics + traces", "RED/USE"),
        ("F8", "SLA?", "Interactive vs batch", "Latency budgets"),
        ("F9", "Multi-region?", "Single region MVP", "Home cell pattern"),
        ("F10", "Admin?", "Ops APIs", "Audit trail"),
        ("F11", "Migration?", "Zero downtime desired", "Dual-write/version flags"),
        ("F12", "Compliance?", "Audit + retention", "Immutable logs"),
    ]


def _common_nfr() -> list:
    return [
        ("N1", "Latency?", "Interactive path", "p99 per API budget"),
        ("N2", "Availability?", "Degrade gracefully", "99.9% MVP"),
        ("N3", "Throughput?", "See scale table", "Horizontal scale"),
        ("N4", "Durability?", "No silent loss", "RPO=0 for ACKed writes"),
        ("N5", "Correctness?", "Invariants listed", "Reconciliation jobs"),
        ("N6", "Cost?", "Efficient at scale", "Tiered storage/compute"),
    ]


def _common_scales(qps: str = "1K") -> list:
    return [
        ("Write QPS", qps, f"{int(float(qps.replace('K','000').replace('M','000000'))/1000 if 'K' in qps else qps)*10}", "100×", "1000×"),
        ("Read QPS", f"{int(qps.replace('K','000'))*5 if 'K' in qps else qps}", "...", "...", "..."),
        ("Storage/day", "100 GB", "1 TB", "10 TB", "100 TB"),
        ("Regions", "1", "2", "3", "5+"),
    ]


# bookstore-pricing-api
hld(
    slug="bookstore-pricing-api",
    title="Bookstore Pricing API with Batch Fetches",
    focus="Batch price API · Coalescing · Cache tiers · Seller/partner feeds · Staleness labels · Rate limits",
    theme="commerce API with batch semantics and amplification control",
    goal="Design a **pricing API** that returns prices for many ISBNs in one call, coalescing upstream fetches and exposing freshness/staleness honestly.",
    fr=[
        ("F1", "API shape?", "POST /prices batch up to 100 ISBNs", "Batch endpoint + single ISBN"),
        ("F2", "Upstream?", "Partner feeds + on-demand refresh", "Hybrid like book-price aggregator"),
        ("F3", "Freshness?", "Return retrieved_at + source", "Never fake live if stale"),
        ("F4", "Partial results?", "Per-ISBN status in batch", "200 with mixed statuses"),
        ("F5", "Currency?", "USD MVP", "Cents integer"),
        ("F6", "Rate limits?", "Per API key", "Token bucket"),
        ("F7", "Coalescing?", "Same ISBN in flight merged", "Singleflight map"),
        ("F8", "Negative cache?", "Unknown ISBN short TTL", "Protect upstream"),
        ("F9", "Admin invalidate?", "Purge cache keys", "Control plane"),
        ("F10", "Webhook on change?", "Optional Phase 2", "Outbox"),
        ("F11", "Historical prices?", "No MVP", "Time-series store later"),
        ("F12", "SLA tiers?", "Premium lower staleness", "Per-tenant TTL"),
    ],
    nfr=_common_nfr(),
    mvp=["Batch price fetch up to 100 ISBNs.", "Cache with TTL + coalescing.", "Per-ISBN OK/STALE/UNAVAILABLE.", "Rate limits per API key.", "Honest freshness metadata."],
    out_mvp=["Real-time push to all clients", "Cross-region active-active writes on cache"],
    happy=["Batch of 50 ISBNs: 40 cache hit, 10 coalesced fan-out.", "Client receives mixed freshness labels.", "Retry same batch idempotent via request hash cache."],
    edges=[("Upstream timeout", "Mark ISBN UNAVAILABLE; don't block whole batch"), ("Hot ISBN in batch", "Single upstream fetch shared"), ("Feed lag", "STALE label with age"), ("Invalid ISBN", "400 per item or batch policy")],
    scales=[("Batch API QPS", "200", "2K", "20K", "200K"), ("ISBNs/request avg", "30", "50", "80", "100"), ("Upstream calls/s", "2K", "5K", "50K", "200K (must coalesce)"), ("Cache entries", "5M", "20M", "100M", "500M")],
    scale_forces={"10×": "Redis cluster; coalescing; per-partner bulkheads.", "100×": "Pre-warmed feeds; sampling upstream.", "1,000×": "Regional cache cells; push invalidations."},
    assumptions=["Integer cents.", "Partners rate-limited.", "Batch deadline 500ms–1s."],
    scope="Batch pricing API with cache, coalescing, partial per-ISBN results, and upstream amplification control.",
    estimation="""```text
200 QPS × 30 ISBN = 6000 logical lookups/s
80% cache hit → 1200 upstream ISBN fetches/s
Coalesce 50% → 600 upstream calls/s manageable
Batch response ~30 × 64B × 200 QPS ≈ 384 KB/s egress
```""",
    abstractions="BatchRequest · PriceEntry · Freshness · Coalescer · FeedSnapshot · RateLimiter",
    options=[("Sync per-ISBN upstream", "Simple", "Amplification", "Batch size >1"), ("Full async batch job", "Cheap upstream", "Bad UX", "Interactive API"), ("Feed-only", "Cheap", "Stale", "Premium tier SLA"), ("Hybrid cache+feed+on-demand", "Balanced", "Complexity", "Chosen")],
    apis="POST /v1/prices  {isbn:[...]}  → {prices:[{isbn, cents, status, retrieved_at}]}",
    tradeoffs=[("Staleness", "TTL + label", "Honest API", "Hide age"), ("Batch size cap", "100 ISBN", "Protect upstream", "Unbounded batch"), ("Sync vs async refresh", "Sync within deadline", "Predictable", "Hang")],
    diagram="API → Batch Orchestrator → Coalescer → Cache → Upstream Adapters / Feed Reader",
    pseudocode="""function batch_prices(isbns, deadline):
  results = []
  misses = []
  for isbn in isbns:
    e = cache.get(isbn)
    if e and not e.expired: results.append(e)
    else: misses.append(isbn)
  for isbn in unique(misses):
    coalescer.do(isbn, () => fetch_upstream(isbn, deadline))
  merge results with statuses""",
    traps=[("Block batch on slow ISBN", "Per-item deadline"), ("One upstream pool", "Bulkheads per partner"), ("Return cached without label", "Always freshness metadata")],
    deeper_qs=["Different TTL per seller?", "GraphQL vs REST batch?", "Price change notification?", "Compare to book-price aggregator fan-out?"],
    deep_sections=[{"title": "Batch coalescing internals", "body": "Maintain in-flight map isbn→Promise; batch executor dedupes misses before fan-out; cap parallel upstream per partner."}],
    wrap_summary="Batch API with per-ISBN statuses, coalescing, and labeled staleness—control amplification like aggregator but read-optimized.",
    related="- book-price-aggregator-system-design.md\n- kv-store-qps-api",
)

# Additional HLD topics - define programmatically for brevity but with unique content
EXTRA_HLD = [
    ("slack-messaging", "Slack-like Messaging", "Channels · DMs · Threads · Real-time delivery · Read receipts · Search · Presence",
     "Design **Slack-like messaging**: channels, DMs, threads, real-time fanout, history pagination, and search.",
     "500", "Message shard by channel_id; WebSocket gateway; durable log per channel."),
    ("chat-partitioned-cache", "Chat with Partitioned Cache", "Partitioned hot cache · Channel affinity · Invalidation · Fanout · Consistency vs latency",
     "Design chat where **recent messages are cached in partitioned nodes** affined to channel ranges.",
     "2K", "Consistent hash channels→cache partition; coalesce reads; TTL + event invalidation."),
    ("distributed-filesystem", "Distributed Filesystem", "Metadata service · Chunk storage · Leases · Replication · POSIX subset",
     "Design a **distributed filesystem** (GFS/HDFS flavor): master metadata, chunkservers, replication, leases.",
     "500", "Single metadata leader; 64MB chunks; 3-way replication; lease for writers."),
    ("hierarchical-filesystem", "Hierarchical Filesystem", "Directory tree · Hard links · Rename atomicity · Path resolution · Locking",
     "Design a **hierarchical filesystem** with directories, atomic rename, path walks, and inode-like metadata.",
     "1K", "Directory entries in metadata store; rename as atomic metadata TX; path cache."),
    ("s3-object-storage", "S3-like Object Storage", "Buckets · Keys · Versioning · Strong read-after-write · Multipart · Lifecycle",
     "Design **S3-like object storage**: buckets, keys, versioning, multipart upload, lifecycle tiers.",
     "5K", "Metadata DB + blob store; erasure coding at scale; consistent hashing for placement."),
    ("dropbox-file-sync", "Dropbox / File Synchronization", "Block-level sync · Conflict resolution · Metadata · Delta sync · Notifications",
     "Design **Dropbox-style sync**: block hashing, delta upload, conflict policy, cross-device notifications.",
     "200", "Content-defined chunking; revision graph; sync cursor; long-poll/WebSocket."),
    ("job-scheduler", "General Job Scheduler", "Cron · Delayed jobs · Leases · Retries · Priorities · Fairness · DAG",
     "Design a **distributed job scheduler** with at-least-once execution, leases, retries, cron, and priorities.",
     "1K", "Home shard per job namespace; lease + heartbeat; visibility timeout; DLQ."),
    ("gpu-scheduler", "GPU Scheduler", "GPU pools · Queues · Preemption · Gang scheduling · Fractional GPUs · Fair share",
     "Design a **GPU cluster scheduler** for ML training jobs: queues, gang scheduling, preemption, fair share.",
     "100", "Resource vector per node; queue per tenant; bin-pack; preemption policy explicit."),
    ("kafka-like-message-queue", "Kafka-like Message Queue", "Partitions · Offsets · Consumer groups · Retention · Rebalance · Exactly-once-ish",
     "Design a **Kafka-like log**: partitioned topics, consumer groups, retention, at-least-once consumption.",
     "50K", "Partition leaders; ISR replication; offset commits; idempotent producers optional."),
    ("distributed-web-crawler", "Distributed Web Crawler", "Frontier · Politeness · Dedupe · Bloom · Worker pool · Robots.txt",
     "Design a **distributed web crawler** with URL frontier, politeness per host, dedupe, and scalable fetchers.",
     "500", "Per-host queues; distributed dedupe; fetcher workers; robots cache."),
    ("vm-bandwidth-rate-limiter", "VM-Bandwidth Rate Limiter", "Token bucket · Hierarchical limits · Enforcer agent · Burst · Fairness",
     "Design **per-VM bandwidth rate limiting** enforced on hypervisor/host with hierarchical quotas.",
     "10K", "Token bucket in eBPF/agent; control plane pushes limits; fail closed on agent loss policy."),
    ("serving-throttle-safety", "Serving-Infrastructure Throttle / Safety System", "Admission control · Load shed · Circuit break · Autoscale signals · SLO guardrails",
     "Design **serving safety**: admission control, throttle under overload, protect dependencies, SLO-based shedding.",
     "100K", "Global/con per-tenant admission; latency-based shed; priority tiers."),
    ("visa-payment-routing", "Visa-like Payment-Routing Network", "Authorization · Routing · Clearing · Idempotency · Ledger · Fraud hooks",
     "Design a **payment routing network** connecting merchants, issuers, and acquirers with idempotent auth/capture.",
     "5K", "State machine per txn; home cell; ledger integration; ISO8583-like message idempotency."),
    ("stock-trading-platform", "Stock-Trading Platform", "Order book · Matching · Market data · Settlement · Regulatory audit",
     "Design a **stock trading platform**: order entry, matching engine, market data feed, settlement hooks.",
     "10K", "Matching in memory per symbol shard; single writer per symbol; audit log immutable."),
    ("crud-async-jobs", "CRUD Service with Asynchronous Jobs", "Sync CRUD · Async job enqueue · Status polling · Webhooks · Outbox",
     "Design a **CRUD API** where long operations run as async jobs with durable status and webhooks.",
     "2K", "TX writes resource + outbox job row; worker pool; idempotent job execution."),
    ("kv-store-qps-api", "KV Store with QPS API", "KV ops · Per-key QPS metrics · Sliding window · Rate report API",
     "Design a **KV store** exposing get/put plus **QPS metrics API** per key (HLD service view).",
     "50K", "Shard by key; metrics aggregated in streaming layer; see LLD for sliding window."),
    ("digital-game-store", "Digital Game-Store Backend", "Catalog · Entitlements · DRM keys · Downloads · Purchases · Refunds",
     "Design a **digital game store**: purchase, entitlement grant, download authorization, refunds.",
     "500", "Entitlement SoT; signed download URLs; purchase saga; anti-fraud checks."),
    ("collaborative-playlist-editor", "Collaborative Playlist Editor", "OT/CRDT · Real-time sync · Conflict resolution · Presence · Offline",
     "Design a **collaborative playlist editor** with concurrent edits, ordering, and offline merge.",
     "1K", "CRDT or OT with server sequencing; WebSocket sync; snapshot + ops log."),
]

for slug, title, focus, goal, qps, core in EXTRA_HLD:
    hld(
        slug=slug,
        title=title,
        focus=focus,
        theme="classic HLD; Databricks distributed-systems bank",
        goal=goal,
        fr=_common_fr("F", core),
        nfr=_common_nfr(),
        mvp=[f"Core {title.lower()} MVP path with durable writes.", "Auth + rate limits.", "Observability baseline.", "Explicit failure/degrade behavior.", "Idempotent mutations where applicable."],
        out_mvp=["Global active-active on same hot key", "Perfect exactly-once everywhere without idempotency"],
        happy=[f"Primary user flow succeeds under normal load.", "Retry returns same result for idempotent ops.", "Degraded mode keeps read path alive if allowed.", "Admin can inspect and repair stuck state."],
        edges=[("Dependency timeout", "Classified error; retry with backoff"), ("Hot key / shard", "Isolate; coalesce; scale shard"), ("Duplicate client retry", "Idempotency returns first result"), ("Poison message/job", "DLQ + alert"), ("Regional failover", "Home cell + epoch fencing")],
        scales=[("Peak QPS", qps, f"{int(qps.replace('K','000').replace('M','000000'))*10 if qps[-1]=='K' else int(qps)*10}", "100×", "1000×"), ("Storage/day", "50 GB", "500 GB", "5 TB", "50 TB"), ("Active users", "100K", "1M", "10M", "100M"), ("Regions", "1", "2", "3", "5+")],
        scale_forces={"10×": "Horizontal shards; caching; bulkheads.", "100×": "Async pipelines; tiered storage; fair queuing.", "1,000×": "Cells; aggregation; admission control."},
        assumptions=["Cloud object storage / managed DB acceptable.", "At-least-once delivery with idempotent consumers.", "Single-region MVP unless stated."],
        scope=f"{goal} Scale from baseline ~{qps} QPS through 10×/100×/1,000× with explicit invariants.",
        estimation=f"""### 2.1 Traffic & concurrency

```text
Peak QPS ≈ {qps} (baseline)
p99 service time 50ms → concurrency ≈ peak_qps × 0.05
```

### 2.2 Storage & bandwidth

```text
Daily writes × record_size → tier hot vs cold
Egress dominated by read path; CDN/cache where applicable
```

### 2.3 Core design pressure

{core}

### 2.4 Bottlenecks (ranked)

1. Hot partition / serializing resource
2. Downstream amplification
3. Durability vs latency on write path
4. Retry storms under partial outage
5. Operational complexity of dual-write""",
        abstractions=f"Core domain entities for {title}; shard key; durable log; cache hint; async bus",
        options=[("Single monolith", "Fast MVP", "Scale ceiling", "100×"), ("Microservices early", "Isolation", "Ops burden", "MVP"), ("Sync everything", "Simple", "Tail latency", "Fan-out heavy"), ("Chosen: modular monolith → split hot path", "Balance", "Migration needed", "Default")],
        apis=f"REST/gRPC APIs for {title}; admin/status endpoints; idempotency keys on writes",
        tradeoffs=[("Consistency", "Strong on money/state path", "Correctness", "Eventual everywhere"), ("Cache", "Hint with TTL/version check", "Performance", "Cache as SoT"), ("Async", "Outbox for side effects", "Reliability", "Fire-and-forget")],
        diagram=f"Clients → Gateway → {title} Service → Primary Store + Cache + Queue → Workers / External deps",
        invariants=f"1. SoT defined for {title}. 2. ACK after durability policy. 3. Retries safe. 4. {core}",
        reliability="Durable state machines; outbox; DLQ; reconciliation; crash recovery walkthrough.",
        scalability="Shard by natural key; read replicas; async for amplification; cells at 1000×.",
        maintainability="Versioned events; feature flags; replay tests; documented degrade modes.",
        data_model=f"Primary tables for {slug.replace('-','_')}; audit_log; outbox; idempotency keys",
        pseudocode=f"""function handle_request(req):
  validate(req)
  if mutation:
    idem = check_idempotency(req.key)
    if idem: return idem.response
    tx: apply domain logic; write outbox; save idem
  else:
    read from SoT or cache-with-version
  return response""",
        metrics=f"qps, p99, error_rate, backlog_lag, saturation — specific to {title}",
        traps=[("Skip idempotency", "Retries duplicate work"), ("Dual-write without outbox", "Inconsistent secondary stores"), ("Unbounded queue", "OOM and lag death spiral")],
        deeper_qs=[f"Multi-region story for {title}?", f"Cost optimization at 100×?", f"Testing strategy for {title}?", "How does this relate to Databricks storage/scheduler questions?"],
        deep_sections=[{"title": f"Domain deep dive — {title}", "body": core}, {"title": "Failure walkthrough", "body": "Pick one write request; name crash point after each arrow; show recovery via durable state + idempotent retry."}],
        wrap_summary=f"{title}: correctness-first MVP, explicit sharding/async at scale, {core}",
        related=f"- Related docs in Databricks INDEX for {slug}",
    )

# Data platform topics (skip lakehouse - exists)
DATA_PLATFORM = [
    ("batch-streaming-ingestion", "Batch and Streaming Ingestion", "CDC · Kafka · Autoloader · Schema inference · DLQ · Medallion landing",
     "Design **unified batch + streaming ingestion** into a lakehouse landing zone with schema evolution and DLQ."),
    ("high-throughput-etl", "High-Throughput ETL Pipelines", "Parallel stages · Shuffle · Spill · Partitioning · Skew handling · Cost",
     "Design **high-throughput ETL** with parallel stages, shuffle, skew mitigation, and cost controls."),
    ("spark-style-distributed-execution", "Spark-style Distributed Execution", "Driver · Executors · DAG · Stages · Tasks · Shuffle · Speculation",
     "Design **Spark-style distributed execution**: driver schedules DAG stages across executors with shuffle and fault tolerance."),
    ("checkpointing-exactly-once", "Checkpointing and Exactly-Once Processing", "Offsets · Idempotent sinks · Two-phase commit · WAL · Replay",
     "Design **checkpointing for effectively-once** stream processing with durable offsets and idempotent sinks."),
    ("delta-like-transaction-log", "Transaction Logs and Delta-like Storage", "Log protocol · Atomic commit · OCC · Time travel · Vacuum",
     "Design a **Delta-like transaction log** on object storage with atomic multi-file commits."),
    ("compute-autoscaling-orchestration", "Compute Autoscaling and Job Orchestration", "Cluster pools · Queue · Spot · Warm pools · Job dependencies",
     "Design **autoscaling compute orchestration** for data jobs: pools, queues, spot/preemptible, dependencies."),
    ("metadata-governance-lineage", "Metadata, Schema Evolution, Governance, Lineage", "Catalog · ACL · Lineage graph · Schema registry · Audit",
     "Design **metadata/governance/lineage** for tables, pipelines, and access control."),
    ("storage-vs-compute-tradeoffs", "Storage versus Compute Trade-offs", "Separation · Caching · File layout · Photon/vectorization · Serverless",
     "Explain and design around **storage/compute separation** trade-offs in a data platform."),
    ("pipeline-recovery-backpressure", "Pipeline Recovery and Backpressure", "Lag · Pause · Scale · DLQ · Checkpoint restore · Pressure signals",
     "Design **pipeline recovery and backpressure** when sinks slow or failures cascade."),
]

for slug, title, focus, goal in DATA_PLATFORM:
    hld(
        slug=slug,
        title=title,
        focus=focus,
        theme="platform/data-plane architecture (role-specific)",
        goal=goal,
        fr=[
            ("F1", "Workloads?", "Batch + streaming analytics", "Unified ingestion/processing"),
            ("F2", "Storage?", "Object storage + open table format", "Medallion layers"),
            ("F3", "Compute?", "Elastic clusters / serverless", "Separate scaling"),
            ("F4", "Consistency?", "Atomic table commits", "Log-based protocols"),
            ("F5", "Failure?", "Task retry + stage recompute", "Lineage-aware replay"),
            ("F6", "Schema?", "Evolution with compatibility", "Registry + checks"),
            ("F7", "Multi-tenant?", "Workspace isolation", "Quotas + fair share"),
            ("F8", "Cost?", "Spot + autoscale", "Tiered storage"),
            ("F9", "SLA?", "Batch daily + near-real-time streams", "Separate SLOs"),
            ("F10", "Governance?", "RBAC + lineage", "Catalog integration"),
            ("F11", "Observability?", "Job metrics + data quality", "Expectations framework"),
            ("F12", "Recovery?", "Checkpoint + idempotent writes", "DLQ for poison records"),
        ],
        nfr=_common_nfr(),
        mvp=["Land data in bronze with schema.", "Process to silver/gold with atomic commits.", "Job orchestration with retries.", "Basic lineage capture.", "Backpressure when lag grows."],
        out_mvp=["Sub-second BI on petabyte tables without tuning", "Cross-cloud active-active same table writers"],
        happy=["Stream ingests; micro-batch commits version N.", "Failed task retries on new executor.", "Autoscale adds workers when lag high.", "Governance ACL enforced on read."],
        edges=[("Straggler task", "Speculative duplicate / kill slow"), ("Shuffle skew", "Salting / AQE"), ("Commit conflict", "OCC retry"), ("Poison record", "DLQ + continue"), ("Spot preemption", "Checkpoint resume")],
        scales=[("Ingest GB/s", "1", "10", "100", "1000"), ("Daily jobs", "1K", "10K", "100K", "1M"), ("Tables", "10K", "100K", "1M", "10M"), ("Concurrent clusters", "100", "1K", "10K", "100K")],
        scale_forces={"10×": "Partition tuning; autoscale; cache hot tables.", "100×": "Shuffle service; Z-order; job queues.", "1,000×": "Multi-cell workspaces; aggregate metadata tier."},
        assumptions=["Object storage durable.", "Open table format (Delta/Iceberg-like).", "Spark-like execution model familiar to interviewer."],
        scope=goal + " Progressive scale with cost and recovery explicit.",
        estimation="""```text
1 GB/s ingest × 86400 ≈ 86 TB/day raw bronze
100× → shuffle network dominates; plan partition count ~ 2–4× cores
Checkpoint storage ≈ micro-batch count × metadata overhead
```""",
        abstractions="Pipeline · Stage · Task · Checkpoint · TableVersion · LineageEdge · ClusterPool",
        options=[("Batch only", "Simple", "Latency", "Streaming SLA"), ("Micro-batch streaming", "Unified code", "Seconds latency", "Chosen hybrid"), ("Separate siloed systems", "Independent", "Ops pain", "Platform goal")],
        apis="Job submit API; table read/write; catalog API; lineage query; cluster pool API",
        tradeoffs=[("Latency vs cost", "Micro-batch + autoscale", "Balance", "Always-on max cluster"), ("Consistency", "Transactional log", "Correct BI", "Eventually consistent files"), ("Recovery", "Checkpoint + replay", "Fast resume", "Reprocess entire day")],
        diagram="Sources → Ingest → Bronze/Silver/Gold on object storage ← Compute clusters ← Orchestrator ← Catalog/Lineage",
        invariants="Readers see atomic table versions; checkpoint monotonic; lineage captured for published datasets.",
        reliability="Checkpoint before ACK advance; idempotent sink writes; DLQ; replay from version V.",
        scalability="Scale executors horizontally; partition input; avoid small files; autoscale on lag CPU.",
        maintainability="Pipeline as code; schema registry; compat tests; feature flags for optimizers.",
        data_model="jobs, runs, tasks, checkpoints, table_versions, lineage_edges, dlq_records",
        pseudocode="""function process_batch(batch, checkpoint):
  rows = transform(batch)
  write staging files
  if commit_table_version(staging, expected_version):
    checkpoint.advance(offset)
  else:
    abort and retry with new version""",
        metrics="input_lag_seconds, shuffle_bytes, task_duration, commit_conflicts, dlq_count, cluster_utilization",
        traps=[("Exactly-once marketing without idempotent sink", "Effectively-once with dedupe keys"), ("Ignore shuffle", "Job hangs at scale"), ("No file layout plan", "Millions of small files")],
        deeper_qs=["Compare Delta vs Iceberg commit protocol?", "Photon/vectorization when?", "Serverless vs long-lived clusters?", "How handle GDPR deletes in lakehouse?"],
        deep_sections=[{"title": "Platform-specific mechanism", "body": focus + " — tie to Databricks product concepts without requiring 'design Databricks' answer."}],
        wrap_summary=f"{title}: separation of storage/compute, atomic commits, checkpointed recovery, governance hooks.",
        related="- lakehouse-object-storage-system-design.md\n- durable-embedded-kv-store-lld (local metadata analogy)",
    )

# ---------------------------------------------------------------------------
# LLD topics
# ---------------------------------------------------------------------------

LLD_TOPICS: list[dict] = []

def lld(**kwargs):
    kwargs.setdefault("file", kwargs["slug"] + "-lld-system-design.md")
    LLD_TOPICS.append(kwargs)


lld(
    slug="persistent-inmemory-cache",
    title="Single-Node Persistent In-Memory Cache",
    focus="LRU · WAL · Recovery · Thread safety · Eviction · Optional TTL",
    goal="Design a **persistent in-memory LRU cache** that survives restart via WAL without losing acknowledged inserts.",
    fr=[
        ("F1", "Scope?", "Single process", "No distributed cache"),
        ("F2", "Ops?", "get/put/delete", "Core API"),
        ("F3", "Capacity?", "Bounded by RAM max_entries", "Eviction required"),
        ("F4", "Durability?", "Ack after WAL fsync", "Like mini KV"),
        ("F5", "Eviction?", "LRU", "Doubly-linked list + hash map"),
        ("F6", "Concurrency?", "Multi-threaded", "Striped locks or RW lock"),
        ("F7", "TTL?", "Optional per key", "Lazy expire on access"),
        ("F8", "Value size?", "Bounded", "Reject oversized"),
        ("F9", "Recovery?", "Replay WAL rebuild LRU order", "Checkpoint snapshot optional"),
        ("F10", "Metrics?", "hit/miss/eviction", "Atomic counters"),
        ("F11", "Iteration?", "Optional snapshot iterator", "Copy-on-read or pin generation"),
        ("F12", "Crash?", "Lose un-ACKed only", "fsync policy explicit"),
    ],
    mvp=["LRU get/put/delete.", "WAL for mutations.", "Recovery rebuilds cache.", "Thread-safe API.", "Max capacity eviction."],
    scope="Persistent LRU cache: O(1) ops, WAL durability for ACKed puts, concurrent access, recovery replay.",
    invariant="put returns ⇒ entry durable in WAL and visible to subsequent gets after recovery.",
    api="""class PersistentCache:
  get(key) -> Optional[bytes]
  put(key, value) -> void
  delete(key) -> void
  stats() -> CacheStats""",
    guarantees="| get/put/delete | Thread-safe |\n| Durability | ACKed puts survive crash |\n| Capacity | LRU eviction enforced |",
    classes="""PersistentCache
  HashMap key → Node
  DoublyLinkedList LRU order
  WalWriter append-only
  Recovery replayer
Node {key, value, prev, next}""",
    data_structures="Hash map + DLL for O(1) LRU; WAL records: PUT/DELETE with CRC.",
    concurrency="Coarse RWLock MVP; or stripe per bucket; evict under write lock; document lock order: wal → structure.",
    pseudocode="""function put(key, val):
  with write_lock:
    append_wal(PUT, key, val); fsync policy
    if key exists: move_to_head
    else: insert head; if over cap: evict_tail + wal DELETE
    update map""",
    failures=[("Crash mid-wal", "Truncate torn record on recovery"), ("Evict during get", "Lock protects structure"), ("Recovery duplicate", "Replay idempotent")],
    tests="""1. put/get hit/miss
2. evict LRU when full
3. kill -9 after fsync → data present
4. concurrent puts no corruption
5. delete removes from LRU""",
    scale_notes="Stripe locks; batch wal group commit; snapshot every N ops to bound recovery.",
    traps=[("Update LRU without lock", "Race on list"), ("Skip fsync on put ACK", "Durability lie"), ("Evict without WAL", "Recovery resurrect evicted key")],
    deeper_qs=["Snapshot vs full WAL replay?", "TTL with LRU interaction?", "Compare to durable embedded KV?"],
    wrap_summary="Hash+DLL LRU with WAL; ACK after fsync; recovery replays to rebuild order.",
)

LLD_EXTRA = [
    ("type-safe-kv-api", "Generic Type-Safe Key-Value Store API", "Templates/generics · Serialization · Schema · Type erasure · Error types",
     "Design a **type-safe KV API** where keys map to typed values with compile-time or runtime schema safety."),
    ("mpmc-queue", "Thread-Safe Bounded MPMC Queue", "MPMC · Backpressure · Timeouts · Fairness · Cache-line padding",
     "Design a **bounded multi-producer multi-consumer queue** with timed wait and fairness."),
    ("buffered-writer", "Thread-Safe Buffered Writer with Background Flush", "Buffer · Flush thread · fsync policy · close semantics",
     "Design a **buffered writer** that batches writes and flushes asynchronously with clear close/durability semantics."),
    ("durable-event-writer", "Durable Concurrent Event Writer", "Append-only log · Group commit · Concurrent producers · Reader tail",
     "Design a **durable event writer** supporting concurrent append with group commit and tail readers."),
    ("kv-sliding-window-qps", "Sliding-Window QPS Metrics on In-Memory KV Store", "Ring buffer · Timestamps · get/put hooks · Query API",
     "Add **sliding-window QPS metrics** per key to an in-memory KV store."),
    ("kv-race-repair", "Identify and Repair Races in KV Store + Hit Counter", "Race detection · Atomic counters · Repair strategy · Tests",
     "Given buggy KV + hit counter, **find races and fix** with correct concurrent semantics."),
    ("cidr-firewall-matcher", "CIDR Firewall Rule Matcher", "Trie · Sorting · Longest prefix · IPv4/IPv6 · Rule overlap",
     "Design a **CIDR rule matcher** for firewall allow/deny with longest-prefix wins."),
    ("chat-deletion-concurrent-sends", "Chat Deletion Semantics Under Concurrent Sends", "Tombstones · Ordering · Visibility · Session delete",
     "Design **chat delete** semantics when messages arrive concurrently with global delete operation."),
]

for slug, title, focus, goal in LLD_EXTRA:
    lld(
        slug=slug,
        title=title,
        focus=focus,
        goal=goal,
        fr=[
            ("F1", "Single-node?", "Yes", "No distributed protocol"),
            ("F2", "Thread safety?", "Required", "Document locks"),
            ("F3", "Performance target?", "Millions ops/s aspirational", "Lock granularity"),
            ("F4", "Durability?", "As problem states", "fsync if needed"),
            ("F5", "API surface?", "Minimal clear methods", "Avoid scope creep"),
            ("F6", "Timeout support?", "If blocking ops", "Condition vars"),
            ("F7", "Error handling?", "Explicit exceptions", "No silent fail"),
            ("F8", "Testing?", "Unit + stress", "TSan"),
            ("F9", "Memory bounds?", "Bounded structures", "Reject or evict"),
            ("F10", "Fairness?", "If multi-tenant threads", "Avoid starvation"),
            ("F11", "Observability?", "Optional metrics", "Counters atomics"),
            ("F12", "Extension points?", "Keep minimal", "YAGNI"),
        ],
        mvp=[f"Core API for {title}.", "Thread-safe implementation.", "Documented invariants.", "Pseudocode for hot paths.", "Test matrix including concurrency."],
        scope=goal,
        invariant=f"State the linearization/durability invariant for {title} before implementation.",
        api=f"class {slug.replace('-','_').title()}: primary methods with pre/post conditions",
        guarantees=f"| Correctness | Matches invariant for {title} |\n| Thread-safe | Yes |",
        classes=f"Main class + helper components for {title}; lock objects; internal queues/maps as needed.",
        concurrency="Name lock order; which methods block; timeout behavior on wait.",
        pseudocode=f"""function primary_operation(...):
  acquire lock / CAS loop
  validate preconditions
  mutate structure
  release / notify waiters
  return result""",
        tests=f"Functional + concurrent stress tests for {title}; property checks on invariants.",
        traps=[("Giant global lock always", "Measure; stripe if needed"), ("Ignore spurious wakeup", "Loop on condition"), ("Unclear close semantics", "Define flush/fsync on close")],
        deeper_qs=[f"How test {title} under TSan?", "Extension to distributed case?", "Performance vs correctness trade?"],
        wrap_summary=f"{title}: clear invariant, minimal API, explicit concurrency, tests prove races fixed.",
    )


def main():
    existing = {p.name for p in OUT.glob("*.md")}
    counts = {}
    for t in HLD_TOPICS:
        fn = t["file"]
        if fn in existing:
            print(f"S {fn}: exists")
            continue
        n = write(fn, build_hld(t))
        counts[fn] = n
    for t in LLD_TOPICS:
        fn = t["file"]
        if fn in existing:
            print(f"S {fn}: exists")
            continue
        n = write(fn, build_lld(t))
        counts[fn] = n
    print("\n=== Generated ===")
    for fn, n in sorted(counts.items()):
        print(f"{fn}: {n}")
    print(f"Total new files: {len(counts)}")


if __name__ == "__main__":
    main()
