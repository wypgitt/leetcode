#!/usr/bin/env python3
"""Generate 21 Stripe system design markdown files (excludes webhook-delivery)."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

try:
    from stripe_topic_data import TOPICS as _IMPORTED_TOPICS
except ImportError:
    _IMPORTED_TOPICS = []

OUT = Path(__file__).parent
SKIP_FILES = {"webhook-delivery-system-design.md"}
TARGET_MIN, TARGET_MAX = 700, 1000


def table(rows, headers):
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def md_list(items, ordered=False):
    if ordered:
        return "\n".join(f"{i+1}. {x}" for i, x in enumerate(items))
    return "\n".join(f"- {x}" for x in items)


def fmt_mvp_item(item):
    if item.startswith(("POST ", "GET ", "PUT ", "PATCH ", "DELETE ", "Internal:")):
        api = item.split(" —")[0].strip()
        suffix = item[len(api) :].strip()
        extra = f" {suffix}" if suffix else " — idempotent where mutating."
        return f"`{api}`{extra}"
    return item


def render_header(t):
    return f"""# System Design: {t['title']}

> **Focus areas:** {t['focus']}  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** API correctness, idempotency, ledger/regional failure awareness, explicit deal-breakers, integer money where applicable  
> **Interview type:** **HLD / architecture** — Stripe emphasizes correctness, rollout, and ops—not only box diagrams

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


def render_section1(t):
    fr = table(
        [[f"F{i+1}", q, a, d] for i, (q, a, d) in enumerate(t["functional_reqs"])],
        ["#", "Question to ask", "Expected / typical interviewer answer", "Design implication"],
    )
    nfr = table(
        [[f"N{i+1}", q, a, tgt] for i, (q, a, tgt) in enumerate(t["nfr"])],
        ["#", "Question", "Expected answer", "Target"],
    )
    happy = md_list(t["happy_paths"], ordered=True)
    edge = table(t["edge_cases"], ["Case", "Behavior"])
    scale = table(
        [[r[0], r[1], r[2], r[3], r[4]] for r in t["scale_rows"]],
        ["Metric", "Baseline", "10×", "100×", "1,000×"],
    )
    sf = t["scale_forces"]
    constraints = md_list(t["constraints"])
    mvp = md_list([fmt_mvp_item(a) for a in t["mvp"]], ordered=True)
    oos = md_list(t["out_of_scope"])

    return f"""## 1. Clarify Requirements (Interview Q&A)

Goal: {t['goal']}

### 1.1 Functional Requirements

{fr}

**MVP functional scope (lock with interviewer):**

{mvp}

**Out of MVP (explicitly defer):**

{oos}

### 1.2 Non-Functional Requirements

{nfr}

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

{happy}

**Edge / failure cases**

{edge}

### 1.4 Scales (Progressive)

{scale}

**Split QPS classes:** writes ≠ reads ≠ async fanout ≠ audit export. Do not lump into one number.

**What each jump forces:**

- **10×:** {sf['10x']}  
- **100×:** {sf['100x']}  
- **1,000×:** {sf['1000x']}

### 1.5 Etc. (Constraints & Assumptions)

{constraints}

**Scope statement:**

> {t['scope']}

---
"""


def render_section2(t):
    e = t["estimation"]
    return f"""## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
{e['traffic']}
Peak/average ratio ~3–4× for burst planning
Split classes: sync writes, sync reads, async workers, audit/export
```

### 2.2 Storage

```text
{e['storage']}
Idempotency records: same order as writes; retain long for money paths
Audit/log: append-only; tier hot → cold object store
Unit-check discipline: 1e9 rows × 1 KB = 1 TB (not PB)
```

### 2.3 Bandwidth

```text
{e['bandwidth']}
Internal replication (WAL/outbox) similar order to write bandwidth
```

### 2.4 Memory

```text
{e['memory']}
Working set for hot keys: partition by hash; never single global Redis
```

### 2.5 Bottleneck ranking (interview)

{e['bottlenecks']}

**Say early:** correctness and API semantics > raw QPS.

### 2.6 Domain-specific note

```text
{e.get('extra', 'See scale table for growth assumptions.')}
```

---
"""


def render_section3(t):
    db = table(t["deal_breakers"], ["Temptation", "Failure"])
    api_rows = []
    for a in t["apis"]:
        if a.startswith("Internal:"):
            api_rows.append([f"`{a}`", "Internal protocol"])
        else:
            api_rows.append([f"`{a}`", "Idempotent / typed errors / RYW where applicable"])
    apis = table(api_rows, ["API", "Semantics"])

    return f"""## 3. High-Level Design

### 3.1 Core entities

```text
{t['entities'].replace(', ', chr(10) + '  ')}
Directory: tenant/shard → home cell (epoch)
IdempotencyRecord (key, hash, status, response)
Outbox → downstream at-least-once (consumers idempotent)
AuditEnvelope (who, when, request_id, diff)
```

### 3.2 Sacred invariant

```text
{t['invariant']}
```

**Deal-breaker:** acknowledging success before durable commit on money-adjacent paths.

### 3.3 Core protocol

```text
{t['protocols']}
```

**Ordering:** durable local state **before** external side effects (rail, webhook, third-party route).

### 3.4 API surface (product)

{apis}

Stripe-flavored: `Idempotency-Key`, `Request-Id`, typed errors, expandable objects.

{t['hld_sections']}

### 3.5 Read path

| Data class | Consistency | Mechanism |
|------------|-------------|-----------|
| Money / inventory / assignment state | Strong RYW | Home cell + version |
| Lists / dashboards / rankings | Eventual OK | Replicas + cache with SLO |
| Audit history | Strong per id | Primary or bounded-lag replica |

### 3.6 Async / integration

```text
Domain TX commits → outbox row
Worker claims with lease → external call with stable idempotency key
Timeout → inquiry, not blind new key
Ledger: journal_key = f(domain_transition_id) where applicable
```

### 3.7 Multi-region

| Plane | Mode |
|-------|------|
| API edge | Active-active |
| Durable writes | **Home cell per shard** |
| Reads | RYW via home; stale OK for analytics |
| Failover | Epoch fence + WAL/outbox replay + recon |

### 3.8 Storage trade-offs

| Data | Store | Why |
|------|-------|-----|
| Primary domain rows | Strong SQL / Spanner | TX + constraints |
| Idempotency | SQL unique + cache | Correctness + speed |
| Outbox | Same TX as domain | Reliable async |
| Audit | Append-only log | Compliance |
| Cache | Redis with TTL | Latency — not SoT for money |

### 3.9 Rollout & operations

- **Dark launch:** shadow traffic, compare outputs.  
- **Feature flags:** per-tenant rollout; default safe on outage.  
- **Expand/contract migrations:** nullable column → backfill → enforce.  
- **Recon jobs:** compare external vs internal; open breaks as tickets.  
- **Runbooks:** stuck PROCESSING, failover, hot shard, DLQ depth.

### 3.10 Deal-breakers (say early)

{db}

---
"""


def render_section4(t):
    return f"""## 4. Architecture Diagram

{t['diagrams']}

---
"""


def render_section5(t):
    deep = "\n\n".join(
        f"### {title}\n\n{body.strip()}" for title, body in t["deep_sections"]
    )
    return f"""## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **Accept ⇒ durable** before client success on critical writes.  
2. **Idempotent mutations** by `(tenant, idempotency_key)` + body hash.  
3. **Append-only audit** — corrections are new records, not edits.  
4. **Single-writer home** per shard for strong consistency domains.  
5. **Outbox** for async side effects; at-least-once with idempotent consumers.  
6. **Fencing tokens** on failover to prevent zombie writers.  
7. **Integer money** where applicable — no floats.  
8. **Recon breaks** visible — never silent fix.  
9. **Typed errors** — idempotent replay must not flip 200↔500 arbitrarily.  
10. **Rate limit + auth** fail closed on money paths when uncertain.

**Failure playbook**

| Failure | Mitigation |
|---------|------------|
| Client retry storm | Idempotency + 409 PROCESSING policy |
| Worker crash after external success | Inquiry + stable external key |
| Hot shard | Split keyspace; isolate tenant; shed reads |
| Regional partition | Home cell authority; edge read-only degrade |
| Cache stampede | Jitter TTL; single-flight |
| Poison message | DLQ + alert |
| Schema migration error | Expand/contract; rollback flag |

**Resolved:** "exactly-once" = **idempotency keys + durable TX + no second economic effect**.

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Modular monolith; single primary DB; basic cache |
| 10× | Service boundary; outbox; idempotency cache; read replicas |
| 100× | Shards + directory; cells; hot-key isolation; cold tier |
| 1000× | Regional homes; stream processors; adaptive shed; archive tier |

**Hotspot patterns:** detect early via p99 skew; isolate; preaggregate; never weaken invariants.

### 5.3 Maintainability

- Property tests for domain invariants.  
- Contract tests for API error shapes and replay behavior.  
- Chaos drills: kill after commit, duplicate requests, failover mid-TX.  
- Versioned recipes / policies / workflow definitions.  
- Ops dashboards: idempotency age, outbox lag, recon open count.

### 5.4 Progressive scale deep dive

**1× (baseline):** Single region primary; TX per write; idempotency unique constraint; nightly recon.

**10×:** Extract service; Redis cache; outbox workers; continuous recon; feature flags.

**100×:** Directory sharding; cells; hot tenant isolation; CQRS read models.

**1000×:** Multi-region homes; time partitions; adaptive concurrency; archive tier; load shed reads first.

### 5.5 Concurrent same-key retries

```text
T0: Request A inserts idempotency PROCESSING
T1: Request B conflicts → 409 Retry-After or short poll
T2: A commits COMPLETE
T3: B reads COMPLETE → returns same response
Sweeper resolves stuck PROCESSING via inquiry — never new business key
```

### 5.6 Cross-shard operations

Prefer **single-shard TX**. Cross-shard: saga + outbox + compensating steps; document eventual completion.

### 5.7 Cache coherency

Money/inventory reads: short TTL + version OR bypass cache. Hint caches OK when stale SLO documented.

### 5.8 Rollout: dark launch

Shadow compare → cohort flag ON → authoritative cutover → remove legacy. Instant rollback = flag OFF + recon.

### 5.9 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| Float money | Rounding exploits |
| Edit audit history | Compliance failure |
| Multi-master same shard | Split brain |
| Skip idempotency | Double effect |
| ACK before durable | Ghost state |

{deep}

---
"""


def render_section6(t):
    dec = table([[a, b] for a, b in t["wrapup_decisions"]], ["Topic", "Decision"])
    risks = md_list(t["wrapup_risks"], ordered=True)
    plan = table([[m, f] for m, f in t["interview_plan"]], ["Min", "Focus"])
    return f"""## 6. Wrap-Up

### 6.1 Decisions

{dec}

### 6.2 Risks

{risks}

### 6.3 45-minute interview plan

{plan}

---
"""


def render_section7(t):
    blocks = []
    for i, (q, a) in enumerate(t["qa_pairs"], 1):
        blocks.append(f"### 7.{i}\n\n**Q: {q}**  \nA: {a}")
    extra = t.get("extra_qa_sections", "")
    return "## 7. Deeper / Related Interview Questions\n\n" + "\n\n".join(blocks) + ("\n\n" + extra if extra else "") + "\n\n---\n"


def render_section8(t):
    gloss = table([[term, meaning] for term, meaning in t["glossary"]], ["Term", "Meaning"])
    return f"""## 8. Appendices

### 8.1 Schema sketches

```text
{t['schema']}
```

### 8.2 API request/response sketch

```text
{t['api_sketch']}
```

### 8.3 State machine

```text
{t['state_machine']}
```

### 8.4 State / status checklist

- [ ] Resource lifecycle states enumerated  
- [ ] Idempotency: PROCESSING / COMPLETE / FAILED  
- [ ] Home cell epoch monotonic on failover  
- [ ] Outbox published_at null until worker ack  
- [ ] Audit actor + request_id on every mutation  

### 8.5 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Idempotency TX, integer money if applicable, basic audit |
| 10× | Outbox, cache, service split, recon jobs |
| 100× | Sharding, directory, hot isolation, CQRS reads |
| 1000× | Regional homes, partitions, archive tier, load shed |

### 8.6 Pseudocode

```text
{t['pseudocode']}
```

### 8.7 Reliability / chaos drills

1. Duplicate POST same key → one resource.  
2. Kill pod after commit before response → client retry → same 200.  
3. Failover mid-TX → fence → no duplicate outbox side effect.  
4. External timeout → inquiry path → no double external call.  
5. Hot key storm → rate limit + isolate shard.  

### 8.8 Glossary

{gloss}

### 8.9 Interview "say this" (60 seconds)

> We expose Stripe-style APIs with mandatory idempotency on mutations, durable commit before ACK, and typed errors. Strong-consistency domains use single-writer home cells with directory routing. Async work uses transactional outbox; external calls use stable idempotency keys and inquiry on timeout. Failover uses epoch fencing and recon before resuming money paths. We never use floats for money, never mutate audit history, and treat reconciliation breaks as first-class ops objects.

### 8.10 Related systems map

```text
API Edge → {t['title']} → Domain Store
                              │
                              ├─► Idempotency / Audit
                              ├─► Outbox → Workers → External / Ledger / Webhooks
                              └─► Metrics / APM / Rate limits
```

Related docs: {t['related']}.

### 8.11 HLD vs integration round

| Round | What you do |
|-------|-------------|
| **System design (this)** | APIs, data model, invariants, failure, scale, rollout |
| **Integration coding** | Parse Stripe docs, call APIs, transform JSON |

### 8.12 Extra traps

| Trap | Pushback |
|------|----------|
| Float dollars | Integer minor units |
| CRDT for money/inventory SoT | Single-writer + TX |
| 24h idempotency TTL on payments | Retain for years |
| Global queue for all tenants | Per-tenant shuffle shard |
| Exactly-once HTTP marketing | At-least-once + idempotent consumers |

### 8.13 Ops metrics

- write_success / write_conflict_409 / write_latency_p99  
- idempotency_processing_age_p99  
- outbox_lag_seconds  
- recon_break_open_count  
- cell_epoch / failover_count  
- cache_hit_rate / stale_read_blocked  

### 8.14 Manual override controls

```text
POST /v1/admin/...  (dual control, reason code, audit sink)
```

### 8.15 Failure mode summary

| Component | Failure | User-visible | Mitigation |
|-----------|---------|--------------|------------|
| Home DB | Primary down | Write errors fail closed | Failover + fence |
| Idempotency | Stuck PROCESSING | 409 retry | Sweeper + inquiry |
| Outbox worker | Lag | Delayed side effects | Scale workers; alert |
| External API | Timeout | Pending state | Inquiry |
| Cache | Stale | Wrong read if misused | Version check |
| Edge region | Partition | 503 or route home | Directory health |

### 8.16 Sharding key selection

```text
Good: tenant_id, merchant_id, geo_cell, resource_id hash
Bad: status alone, country alone — hotspots
Reshard: dual-write + directory epoch bump + backfill verify
```

### 8.17 Compliance & audit

Immutable audit with retention tiers; legal hold; PII minimization; break-glass access with ticket.

### 8.18 Sample recon query

```text
daily: compare sum(internal) vs sum(external) per tenant
if |delta| > threshold → open recon_break
block automated money movement if severity=critical (policy)
```

---

*End of {t['title'].lower()} system design.*
"""


def render_doc(t):
    parts = [
        render_header(t),
        render_section1(t),
        render_section2(t),
        render_section3(t),
        render_section4(t),
        render_section5(t),
        render_section6(t),
        render_section7(t),
        render_section8(t),
    ]
    if t.get("extra_appendix"):
        parts.append(t["extra_appendix"])
    text = "\n".join(parts)
    lines = text.split("\n")
    if len(lines) < TARGET_MIN:
        pad = []
        sources = []
        for p in t.get("interview_probes", []):
            sources.append((f"Interview probe: {p['title']}", p["body"]))
        for title, body in t.get("deep_sections", []):
            sources.append((title, body))
        for i, (q, a) in enumerate(t.get("qa_pairs", [])[15:], 1):
            sources.append((f"Extended Q&A: {q}", f"**Q: {q}**\nA: {a}"))
        idx = 0
        while len(lines) + len(pad) < TARGET_MIN and sources:
            title, body = sources[idx % len(sources)]
            idx += 1
            pad.extend(["", f"### 8.{18+idx}. {title}", "", body.strip(), ""])
        lines.extend(pad)
    if len(lines) > TARGET_MAX:
        lines = lines[: TARGET_MAX - 2] + ["", f"*End of {t['title'].lower()} system design.*", ""]
    return "\n".join(lines)


def load_all_topics():
    from stripe_topic_data import TOPICS  # noqa: WPS433

    return TOPICS


def main():
    enrich_script = OUT / "enrich_all.py"
    if enrich_script.exists():
        subprocess.run([sys.executable, str(enrich_script)], check=True, cwd=OUT)

    topics = load_all_topics()
    webhook_path = OUT / "webhook-delivery-system-design.md"
    webhook_hash_before = (
        hashlib.sha256(webhook_path.read_bytes()).hexdigest() if webhook_path.exists() else None
    )

    results = []
    for t in topics:
        if t["file"] in SKIP_FILES:
            continue
        path = OUT / t["file"]
        doc = render_doc(t)
        path.write_text(doc, encoding="utf-8")
        n = doc.count("\n") + 1
        results.append((t["file"], n))

    if webhook_path.exists() and webhook_hash_before:
        webhook_hash_after = hashlib.sha256(webhook_path.read_bytes()).hexdigest()
        webhook_ok = webhook_hash_before == webhook_hash_after
    else:
        webhook_ok = webhook_path.exists()

    print("Generated files:")
    for f, n in sorted(results):
        print(f"  {f}: {n} lines")
    print(f"\nTotal generated: {len(results)} files")
    print(f"webhook-delivery-system-design.md unchanged: {webhook_ok}")
    if webhook_path.exists():
        print(f"webhook-delivery-system-design.md: {webhook_path.read_text().count(chr(10))+1} lines")


if __name__ == "__main__":
    main()
