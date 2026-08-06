# System Design: Logging System (Microsoft / Azure Platform)

> **Focus areas:** Ingest fan-in · Buffering · Partitioning · Indexing vs scan · Retention/tiers · Push vs pull · Exactly-once illusions · Multi-tenant isolation · Compliance · Progressive scale  
> **Style:** End-to-end platform design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic on GB/day → partitions; split hot ingest vs query planes; explicit durability/lag trade-offs; Azure Monitor / Log Analytics–adjacent honesty without claiming internals  
> **Interview theme:** Microsoft L61–L64 — design a **logging system** for Azure services, Microsoft 365, and first-party platforms (collect, store, query, alert, retain/compliance)

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

Goal: Design a **multi-tenant logging platform** that ingests high-volume structured/unstructured logs from Azure VMs, AKS, App Services, and first-party services; stores them durably with retention tiers; supports interactive query + alerting; and meets enterprise compliance (residency, immutability, audit).

### 1.0 What this is / is not

| Dimension | **Logging system (this doc)** | Not this |
|-----------|-------------------------------|----------|
| Job | Collect → transport → store → query → alert | Full APM product (traces/metrics may integrate) |
| Success | Durable ingest, bounded lag, useful query latency | Perfect exactly-once analytics |
| Hot path | Agents/collectors → brokers → indexers | Synchronous app blocking on log write |
| Microsoft lens | Azure Monitor–like, Sentinel use cases, compliance | `console.log` tutorial |

### 1.1 Functional requirements

| # | Question | Expected answer | Design implication |
|---|----------|-----------------|--------------------|
| F1 | Sources? | Apps, agents, platform diagnostics, audit | Multiple collectors/protocols |
| F2 | Formats? | JSON structured preferred; plaintext OK | Schema-on-read + optional schema registry |
| F3 | APIs? | Ingest HTTP/gRPC; query API; tail; export | Separate planes |
| F4 | Query? | Filter by time, tenant, service, level, free text | Index + partition pruning |
| F5 | Alerting? | Threshold / absence / ratio on streams | Stream processors |
| F6 | Retention? | Hot days, warm weeks, cold months/years | Storage tiers |
| F7 | Multi-tenant? | Subscription/workspace isolation | Quotas, ACLs |
| F8 | Compliance? | Immutable legal hold, residency | WORM tiers / policy |
| F9 | Delivery? | At-least-once default | Dedup optional |
| F10 | Live tail? | Yes for debug | Separate low-latency path |
| F11 | Export? | Event Hubs / Blob / SIEM | Egress pipelines |
| F12 | PII? | Redaction/tokenization options | Ingest pipelines |

**MVP:** agent + HTTP ingest, durable broker buffer, partitioned object/columnar store, time-indexed query, basic alerts, retention tiers, tenant isolation, metrics on lag/drop.

**Out of MVP:** Full distributed tracing product; ML anomaly as core; globally sync query of all regions as one bitcask; unbounded free-text without partitions.

### 1.2 Non-functional requirements

| # | Target |
|---|--------|
| N1 | Ingest availability 99.9–99.99% with local disk buffer |
| N2 | End-to-end lag p99 minutes under normal (seconds for hot path SKUs) |
| N3 | Query interactive: seconds on hot tier for selective filters |
| N4 | Durability: no silent drop after ACK (broker/WAL) |
| N5 | Multi-AZ; regional residency |
| N6 | Noisy-neighbor quotas (GB/day, QPS, query concurrency) |
| N7 | Encryption in transit/rest; CMK optional |
| N8 | Cost: `$ / GB ingested` + `$ / GB retained` explicit |

### 1.3 Cases

**Happy:** agent batches → broker → indexer → searchable; alert fires; retention rolls to cool tier; live tail for Sev incident.

**Edges:** agent disk full; broker partition; schema explosion; cardinality explosion (unique IDs in indexed fields); query scan from hell; PII leak; clock skew; backfill storm; ransomware delete attempt (immutability); cross-region query fanout.

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Ingest | 50 MB/s (~4 TB/day) | 500 MB/s | 5 GB/s | 50 GB/s |
| Events/s | 500K | 5M | 50M | 500M |
| Unique services | 1K | 5K | 20K | 100K+ |
| Query QPS | 50 | 200 | 1K | 5K+ |
| Retention hot | 7–14d | 14d | 14d | tiered |
| Regions | 2 | 4 | 8 | Many + sovereign |

**Jumps:** single cluster → partitioned brokers + indexer fleet → regional cells + query federator → hierarchical tiering + sampling/admission.

### 1.5 Scope repeat-back

> Design a Microsoft/Azure logging platform: resilient ingest with buffering, durable partitioned storage, time/tenant-aware indexing, query + alert planes, retention/compliance tiers, multi-tenant isolation—and progressive scale from TB/day to multi-PB/day without pretending free-text scans are free.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Volume math

```text
50 MB/s × 86400 ≈ 4.32 TB/day ingest
With 3× replication intermediate ≈ 13 TB/day raw churn (broker)
Hot retain 14d × 4.32 TB ≈ 60 TB hot (before compression)
Compression 5–10× columnar → ~6–12 TB effective hot
100× → 432 TB/day → cells mandatory
```

### 2.2 Event rate

```text
Avg event 100 B → 50 MB/s ≈ 500K events/s
Avg event 1 KB → 50 MB/s ≈ 50K events/s
Design for mixed; cardinality and index cost track fields, not only bytes
```

### 2.3 Partitioning arithmetic

```text
Target partition/stream ~10–50 MB/s
50 MB/s → ~2–5 partitions baseline
5 GB/s → ~100–500 partitions — need automation + cells
Shard key: tenant|service|time_bucket (avoid pure random if query needs prune)
```

### 2.4 Index vs scan cost

```text
Selective query (tenant + service + 15m window): read MBs — interactive
Bad query (full-text * across 14d all tenants): petabyte-class — must deny/admit
Rule: partition prune first; inverted index second; brute scan last + gated
```

### 2.5 Broker buffer sizing

```text
Spike 5× for 10 min: 50 MB/s × 5 × 600 s = 150 GB buffer cluster-wide
Agents local disk: 1–5 GB each for upstream outage
ACK only after broker durable (or local WAL if sync sink)
```

### 2.6 Query fanout

```text
Hot store segments per hour × services
15m query may touch tens–hundreds of segments — parallelize with budget
Federated cross-region query: latency + $ egress — prefer region-local
```

### 2.7 Cost sketch

```text
Dominant: ingest GB + indexed hot storage + query scan GB
Sampling/debug tiers and field allowlists beat “index everything”
Track: $ / GB ingested, $ / GB-month hot, query_scan_GB
```

### 2.8 Lag SLO math

```text
Pipeline stages: agent batch (1–5s) + broker (≈0) + index (1–30s) + searchable
p99 lag target < 60s for ops SKU; < 5–15m for cheap bulk SKU
Backpressure when indexer lag > threshold: shed debug levels first
```

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Responsibility |
|-------|----------------|
| **Collection** | Agents, sidecars, platform diagnostics exporters |
| **Ingest** | Auth, validate, normalize, redact, route |
| **Transport buffer** | Durable broker / WAL (Event Hubs–like) |
| **Indexing / storage** | Hot columnar + inverted indexes; warm/cold object |
| **Query** | Parse, plan, prune, execute, federate |
| **Alert** | Streaming rules / scheduled queries |
| **Control** | Tenants, schemas, retention, quotas |
| **Compliance** | Immutable stores, legal hold, audit |

### 3.2 Push vs pull — Why X over Y

| Model | Pros | Cons | When |
|-------|------|------|------|
| **Push (agent→ingest)** | Low latency; simple firewall egress | Producer overload risk | **Default apps/agents** |
| Pull (collector scrapes) | Central control | Discovery complexity | Some platform metrics |
| Log shipping files | Familiar | Tail latency; disk | Legacy VMs |
| Sidecar | Language-agnostic | Resource tax | K8s |

**Chosen:** Push agents/sidecars with local disk spool; optional pull for special sources; batching + compression on wire.

**Deal-breaker:** App thread blocks on remote log HTTP without timeout/buffer.

### 3.3 Buffer — Why X over Y

| Buffer | Pros | Cons |
|--------|------|------|
| **Durable partitioned log (Kafka/Event Hubs-like)** | Replay, fanout, backpressure | Cost/ops |
| Redis lists | Fast | Not durable enough |
| Direct to store | Simple | No shock absorber |
| Local files only | Offline OK | Hard central query |

**Chosen:** Durable broker between ingest and indexers; agents also spool locally.

### 3.4 Storage — Why X over Y

| Store | Pros | Cons |
|-------|------|------|
| **Columnar hot (Parquet/ORC-like) + time partitions** | Cheap scan selective cols | Index build lag |
| Inverted index (Lucene-like) | Fast text | Cardinality / cost |
| Raw Blob only | Cheap | Slow query |
| Row OLTP DB | Familiar | Melts at log volume |

**Chosen:** Hybrid — time/tenant partitioned columnar for analytics + selective inverted indexes for common fields; cold Blob/Archive.

### 3.5 Query — Why X over Y

| Approach | Pros | Cons |
|----------|------|------|
| **Partition prune + columnar + limited inverted** | Scales | Need good schemas |
| Full elastic-everything indexed | UX magic | $ and meltdown |
| Batch only (Hive) | Cheap | Not ops-friendly |

**Chosen:** Interactive on hot with strict admission; async jobs for heavy scans; federated query optional with region pins.

### 3.6 APIs

```text
POST /v1/ingest/{workspace}   batch logs (gzip JSON)
GET  /v1/query                {query, time_from, time_to, limit}
GET  /v1/tail                 SSE/WebSocket filtered stream
PUT  /v1/alerts               rule definitions
POST /v1/export               to Event Hubs / Blob
Admin: retention, schemas, quotas, legal_hold
```

### 3.7 Tradeoffs summary

| Decision | Choice | Deal-breaker |
|----------|--------|--------------|
| Delivery | At-least-once + optional dedup | Pretend exactly-once cheap |
| Buffer | Durable broker | Direct-to-disk only at scale |
| Index all fields | No — allowlists | Cardinality bombs |
| Hot/warm/cold | Tiered | Infinite hot index |
| Multi-tenant | Workspaces + quotas | Shared ungoverned pile |
| Cross-region | Pin + federate carefully | Silent global mega-index |

---

## 4. Architecture Diagram

```text
  Apps / AKS / VMs / Azure platform diagnostics
       |  (agents / sidecars / SDKs)
       v
  Local spool (disk) --retry/backoff-->
       |
       v
  Ingest Front Door / APIM  (TLS, Entra, quotas)
       |
       v
  Ingest Service (normalize, redact, route)
       |
       v
  Durable Broker (partitions by tenant|service|time)
       |                 \
       v                  v
  Indexer Fleet        Stream Alert Processors
       |                  |
       v                  v
  Hot Store (columnar + inverted) --> Query API --> Users / Sentinel / Grafana-like
       |
       v
  Warm/Cold Blob / Archive (immutability / legal hold)
       |
       v
  Export --> Event Hubs / SIEM / Data Lake

  Control Plane: workspaces, schemas, retention, RBAC
  Observability: ingest lag, drop rate, query scan GB
```

**Degrade:** drop debug/verbose first; sample; reject bad tenants; query admission; read-only cold; agent local spool during outage.

---

## 5. Design Deep Dive

### 5.1 Reliability (R)

**Invariants:**

1. After ingest ACK, data is in durable broker (or documented weaker SKU).  
2. Agents never lose beyond local spool capacity without metric `dropped`.  
3. Indexers are idempotent by `(partition, offset)` / event id.  
4. Tenant isolation on query and ingest.  
5. Retention/legal hold cannot be silently shortened.  
6. Clock: prefer event `timestamp` + ingest `received_at`; skew bounded.

**Failure table:**

| Failure | Behavior |
|---------|----------|
| Ingest down | Agent spool; alert |
| Broker AZ loss | RF replicas; producers retry |
| Indexer lag | Autoscale; shed verbose; lag SLO page |
| Query overload | Admission queue; reject expensive plans |
| Corrupt segment | Checksums; rebuild from broker if retained |
| Ransomware delete | Immutable WORM tier / soft-delete |

### 5.2 Scalability (S)

| Scale | Architecture |
|-------|--------------|
| 1× | Broker + indexer + hot store single region |
| 10× | More partitions; schema allowlists; query admission |
| 100× | Workspace cells; federated query; heavy tiering |
| 1,000× | Hierarchical sampling; per-cell brokers; global control only |

**Backpressure hierarchy:** agent batch delay → ingest 429 → broker retention → indexer shed → sample.

### 5.3 Maintainability (M)

Schema guidelines; field budgets; canary indexers; chaos broker loss; query cost explain plans; FinOps chargeback per workspace; runbooks for lag SEVs.

### 5.4 Log shipping vs pull (deep)

**Shipping/push:** best for apps—batch, compress, auth, spool.  
**Pull:** central collectors scrape node log files—ops control, harder identity & lag.  
Hybrid common on VMs: agent tails files (local pull) then pushes remotely.

### 5.5 Exactly-once honesty

End-to-end exactly-once is expensive. Default **at-least-once**; dedup with event_id bloom/TTL caches for alerts; analytics tolerate duplicates or use idempotent sinks.

### 5.6 Indexing & cardinality

Never index unbounded high-cardinality fields (raw request URLs with UUIDs, user-generated filenames) by default. Use keyword allowlists; hash facets; bloom for existence.

### 5.7 Retention & compliance (Microsoft)

| Tier | Latency | Retention | Controls |
|------|---------|-----------|----------|
| Hot | Seconds–minutes searchable | 7–30d | RBAC |
| Warm | Minutes–hours | 30–90d | RBAC |
| Cold/Archive | Hours+ restore | Years | Legal hold / WORM |
| Immutable | Policy-locked | Compliance | Dual control |

Residency: workspace pinned to Azure region/sovereign cloud. Export audited.

### 5.8 Alerting

Streaming: count/error-rate windows on broker streams (low lag).  
Scheduled: query hot store every N minutes (cheaper, higher lag).  
Absence alerts need heartbeats. Notify via Action-Group–like fanout; dedupe storms.

### 5.9 Security

Entra RBAC on workspaces; customer-managed keys optional; PII redaction processors; private link ingest; separate audit log of who queried what.

### 5.10 Progressive scale narrative

> Baseline: agents → ingest → Event Hubs–like broker → indexers → hot columnar/inverted → query/alert.  
> 10×: partitions, quotas, admission, schema discipline.  
> 100×: cells per workspace class, federated query, aggressive tiering.  
> 1,000×: sampling hierarchies, edge aggregation, no single global index.

---

## 6. Wrap-Up

### 6.1 What we designed

Microsoft/Azure logging platform with resilient push ingest, durable broker buffer, hybrid hot storage, query/alert planes, retention/compliance tiers, multi-tenant cells, progressive scale.

### 6.2 Key decisions worth defending

1. Non-blocking agents with disk spool.  
2. Durable broker shock absorber.  
3. At-least-once default honesty.  
4. Partition prune > index everything.  
5. Field allowlists / cardinality control.  
6. Hot/warm/cold + immutability.  
7. Query admission & cost controls.  
8. Cells at 100×.  

### 6.3 Risks & follow-ups

Schema explosion; query bombs; PII; lag SEVs; broker retention too short; cross-region egress bills; silent agent drops.

### 6.4 Closer

> **Logging System**: split planes, durable ingest, tiered store, cardinality discipline, compliance residency, progressive cells—defend every “real-time searchable everything” claim with GB math.

---

## 7. Deeper / Related Interview Questions

**Q1. Push or pull collection?**

**A:** Push agents default; local tail+push hybrid on VMs; pull for niche discovery. Never block app on remote I/O.

**Q2. Why a broker?**

**A:** Durability, replay, fanout to indexers/alerts/export, backpressure shock absorber.

**Q3. At-least-once vs exactly-once?**

**A:** At-least-once default; dedup where needed; exactly-once sinks are specialized and costly.

**Q4. How do you partition?**

**A:** tenant/workspace + service + time; enough partitions for throughput; avoid hot single tenant partition (sub-shard).

**Q5. How is query fast?**

**A:** Time/tenant prune, columnar projection, selective inverted indexes, admission control—not magic full scans.

**Q6. Cardinality explosion?**

**A:** Field allowlists; reject/index-hash high-card fields; budgets per workspace.

**Q7. Retention design?**

**A:** Hot→warm→cold; lifecycle policies; legal hold overrides deletes.

**Q8. Multi-tenant isolation?**

**A:** Workspace keys, RBAC, quotas, optional dedicated cells; query cannot cross without authz.

**Q9. Live tail vs historical query?**

**A:** Tail from broker/stream path; historical from store—different SLOs.

**Q10. Clock skew?**

**A:** Store both event time and received time; window queries document which clock.

**Q11. Backfill?**

**A:** Separate low-priority pipeline; quotas so backfill cannot starve live ingest.

**Q12. PII / GDPR delete?**

**A:** Redact at ingest; crypto-shredding / targeted delete jobs; compliance process—not casual UPDATE.

**Q13. Alert noise?**

**A:** Dedup, inhibit, group; SLO on alert precision; absence via heartbeats.

**Q14. Deal-breaker?**

**A:** Index-all-fields forever; no agent buffer; silent drop without metrics; unbounded cross-tenant queries.

**Q15. Log vs metric vs trace?**

**A:** Logs high-cardinality text; metrics aggregates; traces request graphs—correlate by `trace_id` but store separately.

**Q16. Compression?**

**A:** On wire gzip/zstd; columnar encoding hot; archive codec cold.

**Q17. Schema evolution?**

**A:** Schema-on-read with optional registry; additive fields; break detectors.

**Q18. How to test durability?**

**A:** Kill ingest mid-batch; verify agent retry; kill indexer; replay from broker offsets.

**Q19. Who pages on lag?**

**A:** Logging platform for pipeline; service owner if their volume/quota; jointly for SEV.

**Q20. Cross-region search?**

**A:** Federate with residency checks; expect higher latency/$—or require region pin.

**Q21. Sampling?**

**A:** Dynamic sample verbose; keep errors 100%; head/tail sampling for traces if integrated.

**Q22. Multiline logs?**

**A:** Agent-side merge (stack traces) before ship; careful with boundaries.

**Q23. Windows vs Linux agents?**

**A:** Same push protocol; different file tailers/eventlog readers.

**Q24. SIEM export?**

**A:** Near-real-time Event Hubs stream + batch Blob; schema contracts.

**Q25. Cost control levers?**

**A:** Ingest quotas, sampling, field filters, retention, query scan limits, chargeback.

---

## 8. Appendices

### A — Glossary

| Term | Meaning |
|------|---------|
| Workspace | Tenant isolation unit |
| Broker | Durable partitioned log buffer |
| Hot/warm/cold | Storage tiers by latency/cost |
| Cardinality | Distinct values of a field |
| Partition prune | Skip irrelevant time/tenant segments |
| Spool | Local agent disk buffer |
| WORM | Write-once-read-many immutability |
| Deal-breaker | Index-everything / no buffer / silent drops |

### B — Oncall checklist

- [ ] Ingest lag & drop rate  
- [ ] Broker disk/retention  
- [ ] Indexer lag  
- [ ] Query admission rejects  
- [ ] Top noisy workspaces  
- [ ] Certificate / Entra auth errors  

### C — Event envelope

```text
{
  workspace_id, tenant_id, service, env,
  timestamp, received_at,
  level, resource_id,
  trace_id?, span_id?,
  message, fields{},
  event_id
}
```

### D — Scale checklist

Partitions → quotas/admission → cells → sampling hierarchies; always show GB/day math.

### E — Estimation cheat-sheet

```text
TB/day ≈ MB/s × 0.0864
events/s ≈ bytes/s / avg_event_bytes
partitions ≈ peak_MB_s / MB_s_per_partition
hot_TB ≈ TB/day × hot_days / compression
```

### F — Closer checklist

- [ ] Agent spool  
- [ ] Durable broker  
- [ ] Tiered storage  
- [ ] Cardinality control  
- [ ] Query admission  
- [ ] Compliance residency  

---

## Deep Technical Notes — Logging System

### Agent design

```text
app -> async logger -> lock-free queue -> batcher (size/time)
  -> compress -> HTTPS POST
  on fail: spool to disk (ring/files)
  drop policy: oldest debug first; never silent without counter
```

### Indexer idempotency

Commit consumer offsets only after segment flush fsynced / uploaded + manifest committed. Rebuild manifests on crash.

### Query planner sketch

```text
parse -> authorize workspace
-> time prune -> tenant prune -> service prune
-> choose columnar vs inverted
-> estimate scan_GB -> admit/deny
-> parallel segment readers -> merge/sort/limit
```

### Stream alerts

Windowed aggregations on broker (e.g. 1m error rate). State stores per key with TTL. Output deduped notifications.

### Multiline & stack traces

Agent rules coalesce lines; size cap; if overflow, emit partial + marker.

### Bloom / dictionary encoding

Columnar dictionaries for low-card fields; bloom for “field contains” cheap negatives.

---

## Interview Cards — Logging System (Microsoft)

### Card 1: Push vs pull?

Push default; spool; timeouts. Pull niche.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** AKS sidecar + VM agent story.

### Card 2: Why broker?

Replay, fanout, shock absorber.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Event Hubs–like mental model.

### Card 3: Exactly-once?

At-least-once honesty; dedup selective.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Don’t overpromise SIEM pipelines.

### Card 4: Partitioning?

Tenant/service/time; sub-shard whales.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Noisy subscription isolation.

### Card 5: Fast query?

Prune + columnar + limited inverted + admission.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Cost control / chargeback.

### Card 6: Cardinality?

Allowlists; budgets; hash facets.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Classic Sev from indexing GUIDs.

### Card 7: Retention/compliance?

Tiers + WORM/legal hold + residency.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Enterprise + Sentinel.

### Card 8: Live tail?

Stream path ≠ historical store path.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Incident response UX.

### Card 9: Backpressure?

429, spool, shed verbose, sample.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Protect shared cells.

### Card 10: PII?

Redact; access audit; delete workflows.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Privacy reviews.

### Card 11: Alerting?

Streaming + scheduled; dedupe; heartbeats.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Action groups / on-call.

### Card 12: Deal-breaker?

Index-all; no spool; silent drops; unbounded scans.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Interviewers reward refusals.

### Card 13: Logs vs metrics?

Separate stores; correlate IDs.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Azure Monitor product split intuition.

### Card 14: Cross-region?

Federate consciously; residency first.

**Follow-ups:** 10×? Pages? Fallback? Metric?

**Microsoft angle:** Sovereign clouds.

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope: ingest/query/alert; not full APM |
| 5–12 | Estimation: MB/s → TB/day → partitions |
| 12–22 | HLD + ASCII planes |
| 22–35 | R/S/M: lag, cardinality, tiers, cells |
| 35–45 | Compliance & Q&A |

---

## 10. Operability

### Golden signals

Ingest QPS/bytes, drop rate, broker lag/retention, indexer lag, query latency, query_scan_GB, alert fire rate, auth failures.

### Rollback ladder

Shed verbose → sample → reject heavy queries → pause backfill → read-only warm → cell isolate noisy workspace.

### Kill switches

Per-workspace ingest deny; disable free-text; freeze retention shorten; stop export.

### Security / privacy

RBAC; CMK; private link; query audit; redaction pipelines.

### Cost worksheet

Ingest GB + hot GB-month + scan GB. Levers: sampling, filters, retention, admission.

### Progressive scale

10× partitions/quotas; 100× cells; 1,000× hierarchical sample + edge aggregate.

### Cross-team deps

Identity, networking, storage/Blob, SIEM, service owners, compliance.

---

## More Interview Q&A — Logging System

**Q1. JSON vs plaintext?**

**A:** Prefer structured JSON; plaintext as `message` with parse pipelines.

**Q2. How big are batches?**

**A:** 100KB–1MB or 1–5s—balance latency vs overhead.

**Q3. Idempotent ingest API?**

**A:** Client event_id + server dedup window optional; still at-least-once from agent retries.

**Q4. Hot partition tenant?**

**A:** Split by hash(service/instance); quota throttle; dedicated cell.

**Q5. Query language?**

**A:** Kusto-like / SQL-like filters; explain plan with estimated scan.

**Q6. Full-text?**

**A:** Limited fields; ngrams costly; prefer structured filters.

**Q7. Retention shorten emergency?**

**A:** Policy gated; audit; legal hold blocks.

**Q8. Multi-line Docker logs?**

**A:** Agent CRI parsers; don’t split stack traces.

**Q9. Encrypt with CMK?**

**A:** Envelope encryption; failure fails closed for that workspace.

**Q10. Canary schema change?**

**A:** Dual-write new field; dashboards adopt; reject breaking types.

**Q11. How to prove no silent drop?**

**A:** Agent `dropped` metrics + end-to-end canaries generating known event rates.

**Q12. Cold restore?**

**A:** Async rehydrate to warm; query after ready; cost warning.

**Q13. Rate limit ingest?**

**A:** Per workspace; 429; agents spool; page on sustained.

**Q14. Correlation with traces?**

**A:** Shared `trace_id`; deep links; don’t store full spans in log index.

**Q15. Windows Event Log?**

**A:** Specialized reader → same envelope; map levels.

**Q16. OpenTelemetry logs?**

**A:** OTLP ingest gateway → normalize to envelope.

**Q17. Disaster recovery?**

**A:** Broker + hot store multi-AZ; cold geo-copy; RPO depends on flush.

**Q18. What is “lag”?**

**A:** `now - received_at` at searchable; or broker consumer lag offset time.

**Q19. Fan-in from millions of devices?**

**A:** Edge aggregate/sample; hierarchical ingest; device auth; quotas.

**Q20. Closing pitch?**

**A:** “Buffered push ingest, durable broker, tiered pruned storage, cardinality discipline, compliance residency—scale by cells, not by indexing every GUID.”

---

## Progressive Architecture Jump Cards

### 1× MVP

Agents → ingest → broker → indexer → hot store → query/alert; 14d hot; basic RBAC.

### 10×

Auto partitions; workspace quotas; query admission; schema allowlists; zstd.

### 100×

Cells; federated query; warm/cold lifecycle; streaming alerts at broker; chargeback.

### 1,000×

Edge aggregation; hierarchical sampling; sovereign cells; global control plane only.

---

## Failure Scenario Scripts

**A — Indexer lag SEV:** Autoscale; shed debug; extend broker retention temporarily; page.

**B — Noisy tenant flood:** Quota 429; cell isolate; sample; notify owner.

**C — Query bomb:** Admission deny; publish scan estimate; offer async job.

**D — Agent disk full:** Drop verbose; metric critical; optionally block app (configurable—rare).

**E — Compliance hold:** Freeze deletes; dual control; audit export.

---

## Worked Example — Partition count

```text
Peak ingest 500 MB/s (10× baseline)
Target 25 MB/s/partition → 20 partitions minimum
With 3 hot workspaces uneven: allocate 8+8+4 or dynamic
Whale workspace 300 MB/s alone → sub-partitions by hash(instance_id)
```

---

## Worked Example — Query cost

```text
Hot: 60 TB compressed columnar 10 TB
Bad query scans 20% of hot = 2 TB → deny or async
Good query: 15m × 1 service ≈ few GB uncompressed → seconds
Admission threshold e.g. scan_GB ≤ 50 for interactive
```

---

## Ownership & SEV Model

| Symptom | Primary | Secondary |
|---------|---------|-----------|
| Ingest 5xx | Logging platform | — |
| Workspace 429 | Workspace owner | Platform quotas |
| Lag all tenants | Platform | Capacity |
| Alert flapping | Rule owner | Platform |
| PII in logs | Service owner | Privacy + platform redaction |
| Illegal cross-tenant query | Security | Platform |

---

## Sample 60-Second Pitch

> Applications and agents push batched, compressed logs through an authenticated ingest layer into a durable partitioned broker. Indexers build time- and tenant-partitioned columnar hot storage with selective inverted indexes—not every field. Query prunes partitions, estimates scan cost, and admits or rejects. Alerts run on streams for low lag or on schedules for cheaper rules. Data ages to warm/cold with optional immutability for compliance. We scale with more partitions and then cells, and we judge health by drop rate, lag, and query scan GB.

---

## Appendix G — Anti-patterns

1. Synchronous logging on request path without timeout.  
2. Indexing raw URLs with UUIDs.  
3. Single partition for all tenants.  
4. Infinite hot retention.  
5. Silent agent drops.  
6. Cross-region mega-query by default.  
7. Exactly-once claims without mechanism.  
8. Shared credentials across workspaces.

---

## Appendix H — Mock pushbacks

**Push:** “We need all logs searchable in 1 second globally.”  
**Reply:** “Here’s GB/s and RTT; we offer regional hot SLOs and federated query with cost.”

**Push:** “Index every field for UX.”  
**Reply:** “Cardinality will bankrupt storage; allowlists + structured fields.”

**Push:** “Exactly-once end-to-end.”  
**Reply:** “At-least-once + idempotent sinks; true EOS is a special project.”

**Push:** “Numbers?”  
**Reply:** Walk §2 TB/day and partition math.

---

## Appendix I — Definition of done

- [ ] Agent spool survives 30m outage test  
- [ ] Broker multi-AZ loss drill  
- [ ] Lag SLO dashboard  
- [ ] Query admission blocks scan bombs  
- [ ] Cardinality budget enforced  
- [ ] Retention + legal hold tested  
- [ ] Canary event rate e2e  

---

## Appendix J — Comparison: shipping architectures

| Architecture | Lag | Durability | Ops complexity | Scale ceiling |
|--------------|-----|------------|----------------|---------------|
| Direct-to-DB | Low | Medium | Low | Low |
| Files + nightly | High | High | Medium | Medium |
| Broker + indexer | Low–med | High | Medium–high | **High** |
| Edge aggregate only | Low | Varies | High | Extreme devices |

---

## Appendix K — Ingest protocol sketch

```text
POST /v1/ingest/{workspace}
Authorization: Bearer <token>
Content-Encoding: gzip
Body: { "events": [ envelope... ], "client_batch_id": "..." }

Responses:
  202 Accepted { "acked": N }
  429 Too Many Requests { "retry_after_ms": ... }
  413 Payload Too Large
```

Partial success: document whether batch is atomic; prefer atomic small batches.

---

## Appendix L — Alert rule examples

```text
error_rate(service=X, window=5m) > 5% -> Sev2
ingest_lag_p99 > 5m for 10m -> page platform
absence(heartbeat_service=Y, window=10m) -> Sev1
```

---

## Appendix M — Field budget policy

| Field class | Indexed | Example |
|-------------|---------|---------|
| Low-card dims | Yes | level, region, status_code |
| Bounded enums | Yes | error_code |
| High-card ids | No (store only) | request_id |
| Free text | Limited | message (optional token) |
| PII | Redact/tokenize | email, phone |

---

## Appendix N — End-to-end canary

Emit 100 events/s with known `canary_id` from each region cell; measure receive→searchable latency; alert on miss/drop. This is the durability proof interviewers like.

---

*End of Microsoft Logging System system design prep.*
