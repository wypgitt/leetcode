#!/usr/bin/env python3
"""Rewrite thin Databricks HLD docs: strip filler, adapt gold-standard sources, expand sections."""

from __future__ import annotations

import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
sys.path.insert(0, str(OUT))

from _generate_databricks_docs import HLD_TOPICS, build_hld  # noqa: E402
from _hld_expansions import get_bulk_qa, get_expansion  # noqa: E402

# ---------------------------------------------------------------------------
# Filler removal
# ---------------------------------------------------------------------------

FILLER_MARKERS = [
    "\n## Appendix X — Extended Interview Drill",
    "\n### Pad block 1 — worked failure analysis",
    "\n### Additional practice scenarios",
    "\n### Extra drill line block",
]


def strip_filler(text: str) -> str:
    """Remove Appendix X padding and generic drill blocks."""
    for marker in FILLER_MARKERS:
        idx = text.find(marker)
        if idx >= 0:
            text = text[:idx]
    # Remove operational scenario padding from build_hld
    text = re.sub(
        r"\n### 5\.(?:2[1-9]|3[0-2])\. Operational scenario \d+.*?(?=\n---|\n## 6\.|\Z)",
        "",
        text,
        flags=re.DOTALL,
    )
    text = re.sub(r"\n\{APPENDIX_X\}\s*", "\n", text)
    return text.rstrip() + "\n"


def ensure_footer(text: str, name: str) -> str:
    footer = f"\n*End of {name} HLD prep.*\n"
    if "*End of" not in text[-300:]:
        text = text.rstrip() + footer
    return text


# ---------------------------------------------------------------------------
# Header adaptation
# ---------------------------------------------------------------------------

def databricks_header(text: str, title: str, focus: str, theme: str) -> str:
    lines = text.split("\n")
    if lines and lines[0].startswith("# System Design:"):
        lines[0] = f"# System Design: {title}"
    out = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("> **Focus areas:**"):
            out.append(f"> **Focus areas:** {focus}")
            i += 1
            continue
        if ln.startswith("> **Interview theme:**") or ln.startswith("> **Interview type:**"):
            out.append(f"> **Interview theme:** Databricks — {theme}")
            i += 1
            continue
        out.append(ln)
        i += 1
    body = "\n".join(out)
    if "> **Interview theme:**" not in body[:1200]:
        body = body.replace(
            "> **Quality bar:**",
            f"> **Quality bar:**\n> **Interview theme:** Databricks — {theme}",
            1,
        )
    return body


def adapt_source(
    rel: str,
    title: str,
    focus: str,
    theme: str,
    title_from: str | None = None,
) -> str:
    src = ROOT / rel
    text = src.read_text()
    if title_from:
        text = text.replace(title_from, title, 1)
    text = databricks_header(text, title, focus, theme)
    text = strip_filler(text)
    return text


# ---------------------------------------------------------------------------
# Section 7 Q&A enhancement
# ---------------------------------------------------------------------------

def inject_qa(text: str, qa_blocks: list[tuple[str, str]], section_title: str = "") -> str:
    """Append Q&A answers to section 7 if mostly question-only."""
    if "**Q:" in text and text.count("**Q:") >= 5:
        return text
    marker = "## 7. Deeper / Related Interview Questions"
    idx = text.find(marker)
    if idx < 0:
        return text
    end = text.find("\n## 8.", idx)
    if end < 0:
        end = text.find("\n---", idx + 50)
    if end < 0:
        end = len(text)
    existing = text[idx:end]
    if "**Q:" in existing:
        return text
    qa_md = ""
    if section_title:
        qa_md += f"\n### 7.1 {section_title}\n\n"
    for q, a in qa_blocks:
        qa_md += f"**Q: {q}**  \nA: {a}\n\n"
    new_sec = existing.rstrip() + "\n\n" + qa_md.rstrip() + "\n"
    return text[:idx] + new_sec + text[end:]


# ---------------------------------------------------------------------------
# Expanded build (no filler)
# ---------------------------------------------------------------------------

def apply_expansion(text: str, slug: str) -> str:
    """Insert domain expansion before Wrap-Up if not already present."""
    expansion = get_expansion(slug)
    if not expansion:
        return text
    marker = "\n---\n\n## 6. Wrap-Up"
    if expansion.strip()[:40] in text:
        return text
    idx = text.find(marker)
    if idx < 0:
        return text
    return text[:idx] + "\n" + expansion + "\n" + text[idx:]


def build_quality_hld(t: dict) -> str:
    body = build_hld(t)
    body = strip_filler(body)
    # Remove generic appendix tail if build_hld left thin end marker
    body = re.sub(r"\n---\n\n\*End of .*?\*\n?$", "", body)
    body = apply_expansion(body, t["slug"])
    qa = t.get("qa_pairs") or []
    qa.extend(get_bulk_qa(t["slug"]))
    if not qa and t.get("deeper_qs"):
        qa = [(q.rstrip("?") + "?", _generic_answer(q, t)) for q in t["deeper_qs"]]
    body = inject_qa(body, qa, t.get("qa_section", "Core follow-ups"))
    return ensure_footer(body, t["title"].lower())


def _generic_answer(q: str, t: dict) -> str:
    core = t.get("chosen", t.get("wrap_summary", "correctness-first design with explicit invariants"))
    return f"Anchor on {t['title']}: {core}. Name SoT, shard key, idempotency, and degrade mode."


# ---------------------------------------------------------------------------
# Topic-specific Q&A packs
# ---------------------------------------------------------------------------

QA_PACKS: dict[str, list[tuple[str, str]]] = {
    "group-chat-global-deletion": [
        ("What does delete-for-everyone mean under concurrency?",
         "Append a DELETE event with a new channel_seq after the message; clients apply ops in seq order. "
         "If DELETE seq > SEND seq, body is hidden everywhere. Offline devices converge on sync."),
        ("How do you invalidate partitioned caches?",
         "Publish tombstone/delete event on invalidation bus; cache nodes drop message_id keys; "
         "reads check state==DELETED; TTL + version as backup if invalidation missed."),
        ("Can you physically delete the row?",
         "MVP keeps tombstone for sync/search; scrub body/ciphertext; physical purge in cold tier after retention."),
        ("How handle delete racing with in-flight send to same message_id?",
         "Single-writer sequencer per channel; total order via channel_seq resolves all races deterministically."),
        ("E2E encryption impact?",
         "Server stores ciphertext; delete emits signed retract; honest UX: malicious clients may retain plaintext locally."),
        ("Hot channel sequencer bottleneck?",
         "Rate limits, pull-heavy fan-out for large groups, shard channels to cells; celebrity channels tiered."),
        ("Search showing deleted text?",
         "Index consumes tombstone stream; delete updates search doc; lag bounded with SLA on index pipeline."),
        ("Exactly-once delivery with deletes?",
         "At-least-once push + client dedupe by message_id; delete idempotent by message_id + delete idempotency key."),
        ("Multi-region channel home?",
         "Home cell owns seq assignment; regional WS gateways subscribe to event stream; followers OK for history with lag label."),
        ("How test delete visibility?",
         "Chaos: drop invalidation; assert sync path still converges; property test apply(ops) commutative in seq order."),
    ],
    "stock-order-manager": [
        ("Cancel vs fill race — who wins?",
         "Venue is SoT for fills. Local CAS on order_version; if cancel pending but venue fill arrives, "
         "reconcile to FILLED/PARTIAL and alert risk. Never silently drop venue execution."),
        ("Where do GTD/GTC deadlines live?",
         "Durable expire_at on order row + shard-local timer wheel rebuilt on restart; fire triggers venue cancel attempt."),
        ("Idempotency for place/cancel?",
         "(account_id, client_order_id) for place; venue exec_id dedupes fills; cancel retries return same terminal state."),
        ("Shard by account or symbol?",
         "Order API shards by account_id; matching engine shards by symbol. Separate concerns — don't conflate."),
        ("Market open thundering herd?",
         "Pre-warm connections; queue at API with admission; stagger timer wheel buckets; rate limit per account."),
        ("Partial fill then cancel remainder?",
         "Transition PARTIALLY_FILLED; cancel applies to open quantity only; version increments each transition."),
        ("Unknown venue response after cancel sent?",
         "Mark CANCEL_PENDING; inquiry/reconcile job; client polls status; never double-send cancel with new id."),
        ("Audit requirements?",
         "Append-only order events with timestamps; immutable log for regulatory replay; link every state change to cause."),
        ("How scale timers to 1B open orders?",
         "Hierarchical timer wheels per shard; bucket by expire window; cannot single-process scan."),
        ("Difference from matching engine doc?",
         "This doc is order lifecycle + venue gateway + deadlines; matching is in-memory book per symbol shard."),
    ],
}


# ---------------------------------------------------------------------------
# Lakehouse composite
# ---------------------------------------------------------------------------

def lakehouse_object_storage() -> str:
    s3 = adapt_source(
        "Meta/s3-like-object-storage-system-design.md",
        "Lakehouse Object Storage",
        "Object storage · Table transaction log · Medallion layers · Metadata/data plane split · Multipart · ACID commits",
        "lakehouse foundation combining S3-like blob storage with Delta-style table commits on object storage",
        title_from="# System Design: S3-like Object Storage",
    )
    # Reframe intro goal
    s3 = s3.replace(
        "Goal: **bound S3-compatible object storage**",
        "Goal: **bound lakehouse object storage**—durable blobs plus open table format transaction logs enabling ACID commits, time travel, and analytics workloads on the same storage tier",
        1,
    )
    insert = """

### 3.9 Lakehouse table layer (Delta/Iceberg-style)

```text
Table path: s3://bucket/db/table/
  data/           → Parquet/ORC files (immutable once written)
  _delta_log/     → JSON/Avro commit files (ordered version N)
  _checkpoints/   → Parquet summary of log state (optional)
```

**Commit protocol (optimistic concurrency):**

```text
1. Writer stages new data files under data/
2. Writer reads latest table version V from _delta_log/
3. Writer writes commit file (V+1) with add/remove file actions + metadata
4. Commit succeeds iff no other writer created V+1 (put-if-absent / conditional write)
5. Readers: load latest checkpoint + subsequent log files → reconstruct file list snapshot
```

**Reader/writer separation:** object bytes are immutable; **table version** is the mutable pointer set via log append.

### 3.10 Medallion layering

| Layer | Purpose | Write pattern | Read pattern |
|-------|---------|---------------|--------------|
| Bronze | Raw ingest | Append-heavy | Schema-on-read, audit |
| Silver | Cleaned/conformed | MERGE/upsert | BI joins |
| Gold | Aggregates/marts | Batch recompute | Dashboards |

**Deal-breaker:** treating bronze Parquet as mutable files without log — breaks time travel and concurrent writers.

### 3.11 Listing + table metadata costs

Object listing at billions of keys is expensive; table format **reduces hot path** to reading log tail + checkpoint, not listing entire bucket prefix on every query.

"""
    anchor = "### 3.8 Compaction vs delete retention"
    if anchor not in s3:
        anchor = "### 3.7 Log segment structure"
    if anchor in s3:
        s3 = s3.replace(anchor, insert.strip() + "\n\n" + anchor, 1)
    qa = [
        ("Why separate object storage from table log?",
         "Blobs scale cheaply with EC; table log gives atomic version boundaries and time travel without mutating Parquet files."),
        ("What breaks with concurrent writers without OCC?",
         "Lost updates — two writers both publish overlapping file sets; readers see inconsistent snapshots."),
        ("How handle vacuum/delete files still referenced?",
         "Retention window; log retains remove actions; vacuum only deletes files unreferenced by any version ≥ retention cutoff."),
        ("S3 listing at scale?",
         "Avoid full prefix list per query; checkpoint + incremental log tail; partition pruning via stats in log metadata."),
        ("Compare to Hive-style partition directories?",
         "Open table format adds transactional commit boundary; Hive lacks atomic multi-file commits across partitions."),
    ]
    s3 = inject_qa(s3, qa, "Lakehouse-specific")
    return ensure_footer(s3, "lakehouse object storage")


# ---------------------------------------------------------------------------
# File registry
# ---------------------------------------------------------------------------

def adapt_book_price(title: str, focus: str, theme: str, body_replacements: list[tuple[str, str]]) -> str:
    """Adapt gold-standard book-price-aggregator depth for sibling commerce docs."""
    text = (OUT / "book-price-aggregator-system-design.md").read_text()
    text = text.replace(
        "# System Design: Book Price Aggregator (Fan-Out to Seller APIs)",
        f"# System Design: {title}",
    )
    text = re.sub(
        r"> \*\*Focus areas:\*\*.*",
        f"> **Focus areas:** {focus}",
        text,
        count=1,
    )
    text = re.sub(
        r"> \*\*Interview theme:\*\*.*",
        f"> **Interview theme:** Databricks — {theme}",
        text,
        count=1,
    )
    for old, new in body_replacements:
        text = text.replace(old, new)
    return strip_filler(text)


def bookstore_pricing_api() -> str:
    text = adapt_book_price(
        "Bookstore Pricing API with Batch Fetches",
        "Batch price API · Coalescing · Cache tiers · Partner feeds · Staleness labels · Rate limits",
        "commerce API with batch semantics and amplification control",
        [
            (
                "Goal: **bound the marketplace intermediary**—fan-out to many seller APIs, aggregate lowest price vs customer bid, and (optionally) place an order without double-charging or double-ordering under crashes.",
                "Goal: **bound a batch pricing read API**—return prices for up to 100 ISBNs per request with coalesced upstream fetches, honest freshness labels, and per-ISBN partial results within a hard deadline.",
            ),
            ("POST /quotes", "POST /v1/prices"),
            ("QuoteRequest", "BatchPriceRequest"),
            ("QuoteResult", "BatchPriceResult"),
            (
                "1. `POST /quotes` — fan-out to sellers for ISBN, aggregate within overall deadline.",
                "1. `POST /v1/prices` — batch up to 100 ISBNs; coalesce upstream fetches within deadline.",
            ),
            (
                "2. Return: `UNAVAILABLE` | `PRICE_ABOVE_BID(min_price)` | `ORDER_PLACED(order_id)` (if bid sufficient).",
                "2. Return per-ISBN: `OK` | `STALE` | `UNAVAILABLE` with `retrieved_at` and optional `source`.",
            ),
            (
                "6. Order path: re-check winning seller, charge customer, place seller order with idempotency keys.",
                "6. Rate limits per API key; SLA tiers with different TTL/staleness bounds.",
            ),
            (
                "> Design a book-price aggregator that fans out to 50–200 seller APIs",
                "> Design a batch bookstore pricing API that coalesces upstream ISBN fetches",
            ),
        ],
    )
    insert = """

### 3.11 Batch-specific semantics

```text
POST /v1/prices { isbns: string[1..100], currency?: "USD" }

Response:
{
  prices: [
    { isbn, status: OK|STALE|UNAVAILABLE|INVALID, price_cents?, retrieved_at, source? }
  ],
  batch_stats: { cache_hits, coalesced_fetches, upstream_errors, deadline_ms }
}
```

**Coalescing across batch:** two ISBNs mapping to same upstream partner batch endpoint should share one HTTP call when partner supports multi-ISBN API.

**Idempotency:** optional `request_id` hash cache for identical batch body within 60s — protects partner from client retry storms.

### 3.12 No buy path on this API

This service is **read-only pricing**. Checkout/buy remains separate order service. Never charge customer from pricing API — avoids coupling money path to cache staleness.

"""
    anchor = "### 3.10 Trade-off tables"
    if anchor in text:
        text = text.replace(anchor, insert.strip() + "\n\n" + anchor, 1)
    qa = [
        ("Batch of 100 with one slow ISBN?", "Per-ISBN deadline inside batch budget; return UNAVAILABLE for slow item; do not block siblings."),
        ("Same ISBN different batches concurrent?", "Singleflight on isbn key merges upstream either way."),
        ("GraphQL vs REST batch?", "REST POST batch simpler for rate limit cost = len(isbns); GraphQL optional later."),
        ("Webhook on price change?", "Phase 2: feed processor emits events; premium tier subscribers."),
    ]
    text = inject_qa(text, qa, "Batch API follow-ups")
    return ensure_footer(text, "bookstore pricing api")


def online_bookstore() -> str:
    text = adapt_book_price(
        "Online Bookstore",
        "Catalog · Search · Cart · Checkout · Inventory · Orders · Payments · Reviews",
        "classic HLD; commerce flows with inventory consistency",
        [
            (
                "# System Design: Book Price Aggregator (Fan-Out to Seller APIs)",
                "# System Design: Online Bookstore",
            ),
            (
                "Goal: **bound the marketplace intermediary**—fan-out to many seller APIs, aggregate lowest price vs customer bid, and (optionally) place an order without double-charging or double-ordering under crashes.",
                "Goal: **bound an online bookstore**—browse/search owned catalog, cart, checkout against warehouse inventory, payment saga, and order tracking without overselling or double-charging.",
            ),
            ("seller APIs", "warehouse inventory"),
            ("QuoteRequest", "CheckoutRequest"),
            ("QuoteResult", "OrderResult"),
            ("fan-out to sellers", "catalog read + inventory reserve"),
            (
                "1. `POST /quotes` — fan-out to sellers for ISBN, aggregate within overall deadline.",
                "1. Catalog browse/search by ISBN/title; product detail pages from SoT DB.",
            ),
            (
                "2. Return: `UNAVAILABLE` | `PRICE_ABOVE_BID(min_price)` | `ORDER_PLACED(order_id)` (if bid sufficient).",
                "2. Cart CRUD; checkout reserves inventory with TTL then payment auth/capture saga.",
            ),
            (
                "3. Per-seller timeout + overall fan-out deadline; **partial results OK**.",
                "3. Search via OpenSearch index (async); PDP validates stock from DB at checkout.",
            ),
            (
                "> Design a book-price aggregator that fans out to 50–200 seller APIs",
                "> Design an online bookstore with search, cart, checkout, inventory reservation, and payment saga",
            ),
        ],
    )
    insert = """

### 3.11 Owned inventory (not marketplace fan-out)

```text
ProductCatalog  → SKU metadata, list price (Postgres + CDN)
InventoryService → warehouse_id + sku → available_count (SoT for stock)
CartService     → user_id → line items (Redis + DB for auth users)
CheckoutSaga    → RESERVING → PAYING → PAID → FULFILLING → SHIPPED
SearchIndex     → denormalized docs (OpenSearch, eventual)
```

**Reserve at checkout start:**

```text
UPDATE inventory SET available = available - qty, version = version + 1
WHERE sku = ? AND available >= qty AND version = ?
```

TTL 15m on reservation; sweeper releases abandoned carts.

### 3.12 API surface

```text
GET  /v1/products/{sku}
GET  /v1/search?q=&page=
POST /v1/cart/items
POST /v1/checkout  { idempotency_key }
GET  /v1/orders/{id}
POST /v1/orders/{id}/cancel  (before ship)
```

"""
    anchor = "### 3.10 Trade-off tables"
    if anchor in text:
        text = text.replace(anchor, insert.strip() + "\n\n" + anchor, 1)
    text = apply_expansion(text, "online-bookstore")
    qa = [
        ("Flash sale hot SKU?", "Per-SKU checkout queue or split pools; never unbounded concurrent reserve on one row."),
        ("Guest cart merge on login?", "Union line items; revalidate inventory; dedupe SKU qty with max policy."),
        ("Search shows in-stock but checkout fails?", "Search lags; PDP/checkout reads SoT; acceptable if checkout is authoritative."),
        ("Multi-warehouse inventory?", "Route reserve to nearest warehouse with stock; split shipment Phase 2."),
    ]
    text = inject_qa(text, qa, "Bookstore commerce")
    return ensure_footer(text, "online bookstore")


def get_kafka() -> str:
    import importlib.util

    spec = importlib.util.spec_from_file_location("_gen_hld_batch", OUT / "_gen_hld_batch.py")
    mod = importlib.util.module_from_spec(spec)
    mod.APPENDIX_X = ""
    mod.OUT = OUT
    mod.write = lambda name, body: len(body.splitlines())
    spec.loader.exec_module(mod)
    body = strip_filler(mod.kafka_mq())
    ckpt = strip_filler(
        adapt_source(
            "Databricks/checkpointing-exactly-once-system-design.md",
            "Kafka-like Message Queue",
            "Topics/partitions · Log segments · Producer acks · Consumer groups · Offsets · Replication · ISR · Checkpointing · Exactly-once",
            "log-based messaging backbone with checkpointing and effectively-once consumption",
            title_from="# System Design: Checkpointing and Exactly-Once Processing",
        )
    )
    # Append checkpointing deep dive from companion doc (sections 5+)
    for section in ("## 5. Design Deep Dive", "## 6. Wrap-Up", "## 7. Deeper"):
        idx = ckpt.find(section)
        if idx >= 0:
            body = body.rstrip() + "\n\n---\n\n## 5A. Checkpointing & effectively-once (merged)\n\n" + ckpt[idx:]
            break
    qa = [
        ("Why pull vs push consumers?", "Pull lets consumer control pace and natural backpressure; push overloads slow consumers."),
        ("What if all ISR followers die?", "With min.insync.replicas and unclean.leader=false, partition goes offline rather than lose data."),
        ("Exactly-once without transactions?", "Not really — at-least-once + idempotent consumer processing is default honest answer."),
        ("How many partitions is too many?", "When metadata/controller overhead and file handle count hurt; rule-of-thumb hundreds per broker, tune."),
        ("Hot partition mitigation?", "Split topic, salt keys, upstream aggregation, or dedicated overweight partition."),
    ]
    body = apply_expansion(body, "kafka-like-message-queue")
    body = inject_qa(body, qa + get_bulk_qa("kafka-like-message-queue"), "Log platform follow-ups")
    return ensure_footer(body, "kafka-like message queue")


def visa_from_stripe() -> str:
    text = adapt_source(
        "Stripe/payment-processing-system-design.md",
        "Visa-like Payment Routing Network",
        "Authorization routing · Issuer/acquirer · BIN lookup · Idempotency · Ledger · Settlement · Fraud hooks · PCI boundaries",
        "high-reliability payment routing network connecting merchants, issuers, and acquirers",
        title_from="# System Design: Payment Processing",
    )
    insert = """

### 3.14 BIN routing table

```text
bin_ranges(prefix_start, prefix_end, issuer_id, priority, protocol)
longest_prefix_match(pan_token) → RoutingDecision
health: circuit breaker per issuer_endpoint
maintenance mode → secondary route or structured decline
```

### 3.15 Auth vs capture vs settlement

```text
Auth: hold funds / approve — sync hot path p99 < 500ms
Capture: confirm amount ≤ authorized — may be async batch
Settlement: net clearing files hourly/daily — never on auth critical path
```

"""
    anchor = "### 3.13 Ledger coupling"
    if anchor in text:
        text = text.replace(anchor, anchor + insert, 1)
    text = apply_expansion(text, "visa-payment-routing")
    qa = get_bulk_qa("visa-payment-routing")
    text = inject_qa(text, qa, "Payment routing network")
    return ensure_footer(text, "visa payment routing")


def digital_game_store() -> str:
    text = online_bookstore()
    text = text.replace("Online Bookstore", "Digital Game Store")
    text = text.replace(
        "Catalog · Search · Cart · Checkout · Inventory · Orders · Payments · Reviews",
        "Catalog · Entitlements · Purchases · Downloads · DRM keys · Refunds · Anti-fraud",
    )
    text = text.replace("online bookstore", "digital game store")
    text = text.replace("warehouse inventory", "digital entitlements")
    text = text.replace("InventoryService", "EntitlementService")
    text = text.replace("inventory reserve", "entitlement grant")
    insert = """

### 3.13 Digital entitlement model

```text
purchase saga: PAID → ENTITLED → receipt
entitlements(user_id, game_id, granted_at, revoked_at?) UNIQUE active
download: signed CDN URL TTL 15m after entitlement check
refund: revoke entitlement + PSP refund idempotent
```

"""
    anchor = "### 3.12 API surface"
    if anchor in text:
        text = text.replace(anchor, anchor + insert, 1)
    text = apply_expansion(text, "digital-game-store")
    text = inject_qa(text, get_bulk_qa("digital-game-store"), "Game store")
    return ensure_footer(text, "digital game store")


def stock_trading_platform() -> str:
    """Order manager depth + matching engine expansion."""
    som = stock_order_manager()
    text = som.replace("Stock Order Manager", "Stock Trading Platform")
    text = text.replace(
        "Order lifecycle · GTC/GTD · Cancel vs execute · Idempotency · Venue gateway · Timers · Audit",
        "Order book · Matching · Market data · Order entry · Settlement · Regulatory audit",
    )
    text = text.replace(
        "order lifecycle manager",
        "stock trading platform",
    )
    insert = """

## 3A. Matching engine (in-memory per symbol)

```text
Single writer thread per symbol — price-time priority order book
bids: max-heap by price; asks: min-heap by price
Trade events append to immutable audit log before ACK
Market data fan-out decoupled from matching hot path
```

See order path in sections below for gateway → matcher → settlement hooks.

"""
    marker = "## 3. High-Level Design"
    if marker in text:
        text = text.replace(marker, insert.strip() + "\n\n" + marker, 1)
    text = apply_expansion(text, "stock-trading-platform")
    text = inject_qa(text, get_bulk_qa("stock-trading-platform"), "Trading platform")
    return ensure_footer(text, "stock trading platform")


def group_chat_global_deletion() -> str:
    base = adapt_source(
        "OpenAI/slack-system-design.md",
        "Group Chat with Global Deletion Semantics",
        "Message fan-out · Global delete/retract · Concurrent sends · Cache invalidation · Ordering · Idempotency · Multi-device sync",
        "messaging HLD with delete-for-everyone semantics under concurrent sends",
        title_from="# System Design: Slack",
    )
    insert = """

### 3.15 Global delete-for-everyone

```text
DELETE is an event in the channel log with new channel_seq — not silent row removal
Payload scrubbed; tombstone retained for sync and search
Clients apply SEND then DELETE in seq order — concurrent races resolved by total order
Offline devices catch up via GET history / sync including delete events
Cache: invalidation bus on delete; read path checks state==DELETED
```

**Invariant:** After applying all ops ≤ S, if delete seq exists for message M, no client shows body for M.

"""
    anchor = "### 3.14"
    if anchor in base:
        idx = base.find(anchor)
        base = base[:idx] + insert.strip() + "\n\n" + base[idx:]
    elif "### 3.13" in base:
        base = base.replace("### 3.13", insert.strip() + "\n\n### 3.13", 1)
    base = apply_expansion(base, "group-chat-global-deletion")
    base = inject_qa(base, QA_PACKS.get("group-chat-global-deletion", []) + get_bulk_qa("group-chat-global-deletion"), "Global deletion")
    return ensure_footer(base, "group chat global deletion")


def stock_order_manager() -> str:
    text = visa_from_stripe()
    text = text.replace("Visa-like Payment Routing Network", "Stock Order Manager")
    text = text.replace(
        "Authorization routing · Issuer/acquirer · BIN lookup · Idempotency · Ledger · Settlement · Fraud hooks · PCI boundaries",
        "Order lifecycle · GTC/GTD · Cancel vs execute · Idempotency · Venue gateway · Timers · Audit",
    )
    text = text.replace("payment routing network", "order lifecycle manager")
    text = text.replace("PaymentIntent", "Order")
    text = text.replace("authorize", "place order")
    insert = """

### 3.16 Order state machine (domain)

```text
QUEUED → OPEN → PARTIALLY_FILLED → FILLED | CANCELED | EXPIRED | REJECTED
CAS on order_version for every transition
Venue is SoT for fills — reconcile late fills after local cancel
Timer wheel on expire_at for GTD orders
Idempotency: (account_id, client_order_id) on place; venue_exec_id on fills
```

"""
    if "### 3.15 Auth vs capture" in text:
        text = text.replace("### 3.15 Auth vs capture", insert.strip() + "\n\n### 3.15 Auth vs capture", 1)
    text = apply_expansion(text, "stock-order-manager")
    text = inject_qa(text, QA_PACKS.get("stock-order-manager", []) + get_bulk_qa("stock-order-manager"), "Order manager")
    return ensure_footer(text, "stock order manager")


def chat_partitioned_cache() -> str:
    gc = group_chat_global_deletion()
    text = databricks_header(
        gc,
        "Chat with Partitioned Cache",
        "Partitioned hot cache · Channel affinity · Invalidation · Fanout · Consistency vs latency",
        "chat with recent messages cached on partitioned nodes affined to channel ranges",
    )
    text = apply_expansion(text, "chat-partitioned-cache")
    text = inject_qa(text, get_bulk_qa("chat-partitioned-cache"), "Partitioned cache")
    return ensure_footer(text, "chat partitioned cache")


def kv_store_qps_api() -> str:
    text = adapt_source(
        "Databricks/durable-embedded-kv-store-lld-system-design.md",
        "KV Store with QPS API",
        "KV ops · Per-key QPS metrics · Sliding window · Sharding · Rate report API · Durability tiers",
        "distributed KV service with get/put/delete plus QPS metrics API per key",
        title_from="# LLD: Crash- and Power-Loss-Safe Embedded KV Store",
    )
    insert = """

## HLD service view (distributed)

```text
API tier: GET/PUT/DELETE /v1/kv/{key}; GET /v1/metrics/qps?key=&window=
Storage: sharded by hash(key); RF=3; home shard linearizable per key
Metrics: each shard emits op events → stream aggregator → sliding window QPS API
```

Single-node LLD sections below inform storage-node design; sharding adds routing layer at 10×.

"""
    marker = "## 1. Clarify Requirements"
    if marker in text:
        text = text.replace(marker, insert.strip() + "\n\n" + marker, 1)
    text = apply_expansion(text, "kv-store-qps-api")
    text = inject_qa(text, get_bulk_qa("kv-store-qps-api"), "KV + QPS API")
    return ensure_footer(text, "kv store qps api")


def collaborative_playlist_editor() -> str:
    text = adapt_source(
        "Amazon/dropbox-like-file-storage-system-design.md",
        "Collaborative Playlist Editor",
        "OT/CRDT · Real-time sync · Conflict resolution · Presence · Offline merge · Server sequencing",
        "collaborative playlist editing with concurrent reorder/add/delete and offline convergence",
        title_from="# System Design: Dropbox-like File Storage",
    )
    insert = """

### 3.11 Playlist op log (instead of file blocks)

```text
Op types: InsertTrack, DeleteTrack, MoveTrack, UpdateMeta
Server assigns monotonic seq per playlist_id
Clients submit ops; server total-orders; broadcast via WebSocket
Offline: fetch ops since last_seq; apply in order
Snapshot + compact op log periodically
```

"""
    anchor = "### 3.4 Trade-offs"
    if anchor in text:
        text = text.replace(anchor, insert.strip() + "\n\n" + anchor, 1)
    text = apply_expansion(text, "collaborative-playlist-editor")
    text = inject_qa(text, get_bulk_qa("collaborative-playlist-editor"), "Collaborative editing")
    return ensure_footer(text, "collaborative playlist editor")


SOURCES = {
    "online-bookstore-system-design.md": online_bookstore,
    "bookstore-pricing-api-system-design.md": bookstore_pricing_api,
    "dropbox-file-sync-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Amazon/dropbox-like-file-storage-system-design.md",
            "Dropbox File Sync",
            "Chunking · Dedup · Sync protocol · Metadata · Sharing · Versioning · Conflict · Multi-device",
            "file sync, chunking, metadata correctness; pairs with ranged-file-cache LLD",
            title_from="# System Design: Dropbox-like File Storage",
        ),
        "dropbox file sync",
    ),
    "s3-object-storage-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Meta/s3-like-object-storage-system-design.md",
            "S3-like Object Storage",
            "Bucket/key model · Multipart upload · Metadata vs data plane · Durability · Replication · Consistency · Listing · GC",
            "lakehouse object storage foundation; metadata/data plane split, multipart, durability",
        ),
        "s3 object storage",
    ),
    "job-scheduler-system-design.md": lambda: ensure_footer(
        adapt_source(
            "OpenAI/distributed-job-scheduler-system-design.md",
            "Distributed Job Scheduler",
            "DAG/workflows · Leases/heartbeats · Retries · Priorities · Worker failure · Cron/delayed jobs · Multi-tenant fairness",
            "general-purpose distributed scheduler; classic HLD with lease/fencing depth",
            title_from="# System Design: Distributed Job Scheduler",
        ),
        "job scheduler",
    ),
    "gpu-scheduler-system-design.md": lambda: ensure_footer(
        adapt_source(
            "OpenAI/gpu-scheduler-credits-system-design.md",
            "GPU Scheduler",
            "GPU pools · Gang scheduling · Preemption · Fair share · Quotas · Job placement · Fragmentation · Multi-tenant",
            "GPU cluster scheduling for ML workloads; fairness, preemption, gang scheduling hooks",
            title_from="# System Design: GPU Scheduler (Credits & Fair Share)",
        ),
        "gpu scheduler",
    ),
    "slack-messaging-system-design.md": lambda: ensure_footer(
        adapt_source(
            "OpenAI/slack-system-design.md",
            "Slack-like Messaging",
            "Channels · DMs · Threads · Real-time delivery · Search · Presence · Fan-out · Workspace isolation",
            "enterprise messaging HLD; channel sharding, WS gateway, durable log per channel",
            title_from="# System Design: Slack",
        ),
        "slack messaging",
    ),
    "distributed-web-crawler-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Meta/distributed-web-crawler-system-design.md",
            "Distributed Web Crawler",
            "Frontier · Politeness · Dedupe · Bloom · Worker pool · Robots.txt · URL normalization",
            "large-scale crawler; per-host politeness, distributed dedupe, scalable fetchers",
            title_from="# System Design: Distributed Web Crawler",
        ),
        "distributed web crawler",
    ),
    "kafka-like-message-queue-system-design.md": get_kafka,
    "visa-payment-routing-system-design.md": visa_from_stripe,
    "lakehouse-object-storage-system-design.md": lakehouse_object_storage,
    "serving-throttle-safety-system-design.md": lambda: ensure_footer(
        databricks_header(
            adapt_source(
                "OpenAI/llm-api-rate-limiter-system-design.md",
                "Serving Infrastructure Throttle / Safety",
                "Admission control · RPM/TPM/concurrency · Token bucket · Load shed · Circuit break · SLO guardrails",
                "serving safety and admission control under overload; protect dependencies and SLOs",
                title_from="# System Design: Distributed LLM API Rate Limiter",
            ),
            "Serving Infrastructure Throttle / Safety",
            "Admission control · RPM/TPM/concurrency · Token bucket · Load shed · Circuit break · SLO guardrails",
            "serving safety and admission control under overload; protect dependencies and SLOs",
        ),
        "serving throttle safety",
    ),
    "vm-bandwidth-rate-limiter-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Stripe/rate-limiter-system-design.md",
            "VM Bandwidth Rate Limiter",
            "Token bucket · Hierarchical limits · Hypervisor enforcer · Burst · Fairness · Control plane push",
            "per-VM bandwidth enforcement on host/hypervisor with hierarchical quotas",
            title_from="# System Design: Rate Limiter",
        ),
        "vm bandwidth rate limiter",
    ),
    "batch-streaming-ingestion-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Databricks/high-throughput-etl-system-design.md",
            "Batch and Streaming Ingestion",
            "CDC · Kafka · Autoloader · Schema inference · DLQ · Medallion landing · Checkpointing",
            "unified batch + streaming ingestion into lakehouse landing with schema evolution and recovery",
            title_from="# System Design: High-Throughput ETL Pipelines",
        ).replace(
            "Goal: **bound high-throughput ETL**",
            "Goal: **bound unified batch and streaming ingestion**",
            1,
        ).replace(
            "High-Throughput ETL",
            "Batch and Streaming Ingestion",
        ),
        "batch streaming ingestion",
    ),
    "digital-game-store-system-design.md": digital_game_store,
    "stock-trading-platform-system-design.md": stock_trading_platform,
    "group-chat-global-deletion-system-design.md": group_chat_global_deletion,
    "stock-order-manager-system-design.md": stock_order_manager,
    "chat-partitioned-cache-system-design.md": chat_partitioned_cache,
    "collaborative-playlist-editor-system-design.md": collaborative_playlist_editor,
    "kv-store-qps-api-system-design.md": kv_store_qps_api,
    "hierarchical-filesystem-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Amazon/dropbox-like-file-storage-system-design.md",
            "Hierarchical Filesystem",
            "Directory tree · Hard links · Rename atomicity · Path resolution · Inode metadata · Locking",
            "POSIX-like hierarchical filesystem with atomic rename and path walks",
            title_from="# System Design: Dropbox-like File Storage",
        ).replace("Dropbox-like File Storage", "Hierarchical Filesystem"),
        "hierarchical filesystem",
    ),
    "crud-async-jobs-system-design.md": lambda: ensure_footer(
        adapt_source(
            "Stripe/async-financial-workflow-scheduling-system-design.md",
            "CRUD Service with Asynchronous Jobs",
            "Sync CRUD · Async job enqueue · Status polling · Webhooks · Outbox · Idempotent workers",
            "CRUD API with durable async jobs, status polling, and webhook delivery",
            title_from="# System Design: Async Financial Workflow Scheduling",
        ),
        "crud async jobs",
    ),
}

TOPIC_BY_SLUG = {t["slug"]: t for t in HLD_TOPICS}

EXTRA_SLUGS = [
    "slack-messaging", "chat-partitioned-cache", "hierarchical-filesystem",
    "s3-object-storage", "dropbox-file-sync", "job-scheduler", "gpu-scheduler",
    "kafka-like-message-queue", "distributed-web-crawler", "vm-bandwidth-rate-limiter",
    "serving-throttle-safety", "visa-payment-routing", "stock-trading-platform",
    "crud-async-jobs", "kv-store-qps-api", "digital-game-store",
    "collaborative-playlist-editor", "batch-streaming-ingestion",
]

# Ensure EXTRA topics exist in TOPIC_BY_SLUG via programmatic entries from generate script
for slug in EXTRA_SLUGS:
    if slug not in TOPIC_BY_SLUG:
        # Minimal fallback — build_quality will still expand
        TOPIC_BY_SLUG[slug] = {
            "slug": slug,
            "title": slug.replace("-", " ").title(),
            "focus": "Core domain · Sharding · Durability · Idempotency",
            "theme": slug.replace("-", " "),
            "goal": f"Design **{slug.replace('-', ' ')}** with explicit invariants and progressive scale.",
            "fr": [("F1", "Scope?", "MVP bounded", "SoT defined")],
            "nfr": [("N1", "Latency?", "Interactive", "p99 budget")],
            "mvp": ["Core write path with durability."],
            "out_mvp": ["Global active-active writes"],
            "happy": ["Happy path succeeds with durable ACK."],
            "edges": [("Crash mid-write", "Idempotent retry")],
            "scales": [("QPS", "1K", "10K", "100K", "1M")],
            "scale_forces": {"10×": "Shard", "100×": "Async", "1,000×": "Cells"},
            "assumptions": ["Single region MVP."],
            "scope": f"Design {slug} from baseline through 1000×.",
            "estimation": "Define peak QPS, storage/day, and bottleneck ranking.",
            "deeper_qs": ["Multi-region?", "Hot key?", "Testing strategy?"],
        }

REWRITE_TARGETS = [
    "online-bookstore-system-design.md",
    "visa-payment-routing-system-design.md",
    "lakehouse-object-storage-system-design.md",
    "job-scheduler-system-design.md",
    "dropbox-file-sync-system-design.md",
    "s3-object-storage-system-design.md",
    "stock-trading-platform-system-design.md",
    "bookstore-pricing-api-system-design.md",
    "distributed-web-crawler-system-design.md",
    "batch-streaming-ingestion-system-design.md",
    "kafka-like-message-queue-system-design.md",
    "gpu-scheduler-system-design.md",
    "hierarchical-filesystem-system-design.md",
    "chat-partitioned-cache-system-design.md",
    "digital-game-store-system-design.md",
    "serving-throttle-safety-system-design.md",
    "vm-bandwidth-rate-limiter-system-design.md",
    "collaborative-playlist-editor-system-design.md",
    "kv-store-qps-api-system-design.md",
    "crud-async-jobs-system-design.md",
    "slack-messaging-system-design.md",
    "group-chat-global-deletion-system-design.md",
    "stock-order-manager-system-design.md",
]

STRIP_ENHANCE: dict[str, str] = {}


def slug_from_name(name: str) -> str:
    return name.replace("-system-design.md", "")


def generate(name: str) -> str:
    if name in SOURCES:
        return SOURCES[name]()
    if name in STRIP_ENHANCE:
        slug = STRIP_ENHANCE[name]
        text = strip_filler((OUT / name).read_text())
        text = apply_expansion(text, slug)
        text = inject_qa(text, QA_PACKS.get(slug, []) + get_bulk_qa(slug), "Interview deep dive")
        return ensure_footer(text, slug.replace("-", " "))
    slug = slug_from_name(name)
    t = TOPIC_BY_SLUG.get(slug)
    if t:
        return build_quality_hld(t)
    raise KeyError(f"No generator for {name}")


def main() -> None:
    results: list[tuple[str, int]] = []
    for name in REWRITE_TARGETS:
        body = generate(name)
        path = OUT / name
        path.write_text(body)
        n = body.count("\n")
        results.append((name, n))
        print(f"WROTE {name}: {n} lines")
    print("\n--- Summary ---")
    for name, n in sorted(results, key=lambda x: x[1]):
        print(f"{n:5d}  {name}")
    avg = sum(n for _, n in results) / len(results)
    print(f"\nAverage: {avg:.0f} lines ({len(results)} files)")


if __name__ == "__main__":
    main()
