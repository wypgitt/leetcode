# System Design: Bidirectional Data-Sync Dashboard (with Conflict Resolution)

> **Interview framing:** NVIDIA backend / cloud interviews (team-dependent). Bidirectional sync shows up for device/config state, partner integrations, ops consoles, and multi-region control planes—not only “build Google Docs.” Frame as syncing **structured state** with an **ops dashboard** for conflicts and health.
> **Focus areas:** Bidirectional sync · CRDT / OT / LWW / version vectors · Conflict UI · Offline · Ops dashboard · Idempotency · Causality
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Explicit consistency choice per data class; no single global wall-clock LWW for everything; honest offline & conflict UX; correct fan-out math

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

Goal: **bound sync**—what entities move both ways, who may write, what “conflict” means, whether humans resolve via a dashboard, and offline guarantees.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is syncing? | Structured records: configs, feature flags, device twin state, inventory rows, annotations—not raw video blobs | Document model + attachments by reference |
| F2 | Who are peers? | Many clients (agents/apps) ↔ cloud; optionally cloud ↔ cloud regions; ops edit via dashboard | Hub-and-spoke MVP; mesh later |
| F3 | Direction? | **Bidirectional:** clients push local changes; pull remote; server may push admin overrides | Upload + download pipelines; authority rules |
| F4 | Conflict definition? | Concurrent updates to same field/object without happens-before | Detect with version vectors / CRDT; resolve auto or manual |
| F5 | Resolution policy? | Per-type: LWW for sensors; CRDT merge for sets; **manual** for safety-critical configs | Policy engine + dashboard queue |
| F6 | Offline? | Clients work offline hours; sync when connected | Local store + pending op log |
| F7 | Dashboard? | Ops view: sync lag, conflict queue, force-push, freeze peer, audit | Control plane UI + APIs |
| F8 | Authz? | Peers scoped to tenant/project; ops roles for resolve/override | RBAC on mutations & resolve |
| F9 | Schema evolution? | Fields added over time; old clients | Versioned schemas; tolerant readers |
| F10 | Attachments? | Images/binaries via object storage; sync metadata + hash | Don’t put GB blobs in op log |
| F11 | Notifications? | Realtime when conflict needs human | WebSocket/SSE to dashboard; webhooks optional |
| F12 | Audit? | Who changed what; why resolved | Immutable audit stream |

**MVP functional scope (lock with interviewer):**

1. Entity sync for JSON documents keyed by `(tenant_id, collection, doc_id)`.
2. Client local DB + **op log** (mutations) with idempotency keys.
3. Bidirectional sync protocol: push ops → pull changes since cursor.
4. Conflict detection via **version vectors** (or per-field CRDT where chosen).
5. Auto-resolve policies: LWW timestamp (with caveats), set-union, numeric merge (optional).
6. Manual conflict queue + dashboard UI to pick/merge/override.
7. Offline support with retry; snapshot baseline + incremental ops.
8. Ops metrics: lag, error rate, conflicts/hour, peer health.

**Out of MVP:**

- Fully decentralized mesh without cloud hub.
- Arbitrary OT for rich text collaborative editing (mention as alternative).
- Perfect global wall-clock ordering.
- Syncing multi-GB datasets inside the op channel.
- Automatic semantic merge of free-form prose without CRDT/OT.

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Sync latency (online) | Near-interactive | p50 < 1s, p99 < 5s for small docs in-region |
| N2 | Conflict durability | No lost ops once ACK’d | RPO ≈ 0 for accepted ops |
| N3 | Offline window | Hours to days | Pending log bounded; compaction |
| N4 | Availability | Hub HA; clients queue | Degrade realtime; keep push/pull |
| N5 | Correctness | No silent drop of concurrent writes | Detect or CRDT-merge; never “last HTTP wins” unnoticed |
| N6 | Dashboard freshness | Ops see conflicts quickly | < 5–10s to appear in queue |
| N7 | Multi-tenant isolation | Strict | Shuffle shard + authz |
| N8 | Throughput | See scale table | Split **op ingest**, **fan-out**, **dashboard queries** |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Client A edits `config.threshold` online → push op → server applies → client B pull → sees update.
2. Client offline edits three fields → reconnect → push batch → ACK → pull remote unrelated docs.
3. Two clients concurrently add tags to a set → CRDT union → both see merged tags, no manual conflict.
4. Two clients concurrently set `mode` to different enums → conflict record → dashboard resolves → both pull winner.
5. Ops force-push “quarantine” flag → clients pull authoritative override.
6. Peer flapping network → idempotent retries; no double apply.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate push (retry) | Idempotency key → same result |
| Clock skew LWW | Prefer hybrid logical clocks / server receive time policy—document hazard |
| Op arrives before snapshot baseline | Buffer or request resync |
| Tombstone vs update | Delete wins per policy or conflict |
| Schema unknown field | Preserve in `extensions` bag; don’t drop |
| Huge pending log offline | Compact; snapshot; refuse unbounded growth |
| Split brain two hubs | Single home cell for tenant docs |
| Malicious peer | Authz + size limits + signed ops optional |
| Resolve race two ops agents | CAS on conflict record; audit loser |
| Partial apply of batch | Per-op ACK; transactional batch optional |
| Client rollback local optimistic UI | Rebase on pull; surface conflict |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants | 1K | 10K | 100K | 1M |
| Peers / clients | 50K | 500K | 5M | 50M |
| Documents | 50M | 500M | 5B | 50B |
| Ops ingested / day | 50M | 500M | 5B | 50B |
| Peak op ingest QPS | ~2K | ~20K | ~200K | ~2M |
| Peak pull/fan-out msgs/s | ~10K | ~100K | ~1M | ~10M |
| Concurrent online peers | 10K | 100K | 1M | 10M |
| Conflicts / day (manual) | 5K | 50K | 500K | 5M |
| Avg doc size | 2 KB | 2 KB | 2–4 KB | 2–4 KB |
| Offline pending ops / peer (p99) | 1K | 1K | 2K | 5K |
| Dashboard MAU (ops users) | 500 | 5K | 50K | 500K |
| Regions | 1 | 2 | 4 | 8+ |

**What each jump forces:**

- **10×:** Shard docs by tenant; op log partitions; websocket fan-out via pubsub.
- **100×:** Per-collection CRDT types; conflict workers; snapshot compaction; home cells.
- **1,000×:** Hierarchical fan-out; edge sync proxies; bloom/filter pull; cold storage for old ops.

### 1.5 Etc. (Constraints & Assumptions)

- Cloud hub is **system of record** for cross-peer visibility (MVP hub-and-spoke).
- Clients may be **untrusted** relative to other tenants; trust within device attestation optional.
- Blobs live in object storage; sync carries hashes + URLs.
- NVIDIA flavor: sync **cluster agent state**, **deployment configs**, or **partner metadata**—mention in intro answers.
- Humans in the loop for **safety-critical** conflicts via dashboard.

**Scope statement:**

> Design a multi-tenant bidirectional sync system with offline-capable clients, version-vector/CRDT/LWW policies per data class, durable op logs, and an ops dashboard for conflict resolution and health—scaling from ~50M ops/day through 10× / 100× / 1,000× without silent lost concurrent updates.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Op ingest (push) | 2K QPS | 2M QPS | Durable append + apply |
| Pull / catch-up | 2K QPS | 2M QPS | Cursor reads |
| Realtime fan-out | 10K msg/s | 10M msg/s | Pubsub / gateway |
| Conflict create | ~1 QPS avg | ~1K QPS | Spiky |
| Dashboard queries | 100 QPS | 100K QPS | Cache + indexes |
| Blob upload (not op plane) | separate | separate | Object store |

**Deal-breaker:** Designing only REST CRUD without an **op log / replication cursor** story.

### 2.2 Storage

```text
Ops: 50M/day × 500 B ≈ 25 GB/day raw ops
Retain hot 30 days ≈ 750 GB
1,000×: 50B/day × 500 B = 25 TB/day → must compact/snapshot aggressively

Docs: 50M × 2 KB ≈ 100 GB
1,000×: 50B × 2 KB = 100 TB document store (sharded)

Conflict records: tiny vs docs but index for dashboard
```

**Unit check:** 50B ops/day × 500 B = 25×10^12 B = **25 TB/day**, not PB.

### 2.3 Fan-out amplification

```text
1 op applied → notify interested peers subscribed to doc/collection
If average 5 online subscribers: fan-out 5× ingest
At 200K ingest → ~1M notifies (matches order of table)
Mitigations: collection-level channels, bloom pull, mute inactive, batch
```

### 2.4 Offline catch-up

```text
Peer offline 24h, misses 10K ops relevant:
Pull pages of 500 = 20 round trips; compress; or send snapshot if > threshold
Rule: if lag > T or bytes > B → full snapshot resync for subset
```

### 2.5 Conflict rate

```text
If 0.01% of ops conflict manually:
50M × 1e-4 = 5,000 / day baseline — matches table
Dashboard must prioritize; cannot be email-only at 100×
```

### 2.6 Critical bottlenecks

1. **Hot document** (many writers) → conflict storm  
2. **Fan-out** to huge subscriber sets  
3. **Unbounded op log** without compaction  
4. **LWW clock skew** silent wrong winner  
5. **Dashboard poll** hammering primary  
6. **Large offline reconnect** stampedes  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Document      → (tenant, collection, doc_id) JSON + vector clock / CRDT state
Operation     → idempotent mutation with actor_id, parents, timestamp_hlc
Op Log        → per-shard append-only history
Cursor        → peer’s progress (shard → index/offset)
Conflict      → divergent concurrent ops needing policy/human
Snapshot      → compacted document state + vector
Peer          → client device/agent with local store
Dashboard     → ops UI over conflicts, lag, freezes, audits
```

### 3.2 Sync topology options

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Hub-and-spoke (cloud SoR) | Simple authz, audit, dashboard | Hub bottleneck | Absolute need for offline mesh-only |
| B. Peer mesh CRDT | Offline resilient | Hard authz/security; ops nightmare | Enterprise RBAC + audit required |
| C. Multi-hub with home cell | Scale + region | Cross-cell complexity | Dual-home same doc without CRDT |

**Chosen:** **A for MVP**, evolve to **C** at 100×+ (tenant home cell). Clients never dual-write two hubs for same doc.

### 3.3 Concurrency / merge toolkit (choose per field)

| Technique | Best for | Weakness |
|-----------|----------|----------|
| **LWW** (last-writer-wins) | Low-stakes scalars, sensors | Clock skew; lost updates feel “random” |
| **Version vectors** | Detect concurrent writes | Doesn’t merge values alone |
| **CRDT** (G-Counter, OR-Map, LWW-Register, OR-Set) | Automatic merge | Semantics must fit; memory metadata |
| **OT** | Realtime text | Hard; server transform; usually separate product |
| **Manual 3-way merge** | Configs, safety fields | Needs UI; slower |

**Policy matrix (example):**

```text
tags: OR-Set CRDT
counter_likes: PN-Counter / G-Counter
display_name: LWW-Register (HLC)
safety_mode: version vector → MANUAL conflict if concurrent
nested config blob: field-level policies, not whole-doc LWW
```

**Deal-breaker:** Whole-document LWW for all types in a safety-critical control plane.

### 3.4 Protocol (push / pull)

```text
PushOps:
  client → server: [ops...] each with op_id UUID
  server: durable append → apply → ACK {op_id, server_seq}
  on conflict: ACK accepted but mark conflict OR reject with 409 policy

PullChanges:
  client → server: cursors[], limit
  server → changes / snapshots / conflict notices
  client: apply in causal order; advance cursor

Realtime (optional):
  subscribe(collection|doc) → push notifications of new server_seq
```

**Idempotency:** `(peer_id, op_id)` unique. Retries safe.

### 3.5 Causality & ordering

Use **Hybrid Logical Clocks (HLC)** or Lamport+actor for LWW registers; **version vectors** per doc (or per peer compact VV).

```text
Apply rule:
  if op.parents satisfied (or VV dominates):
     apply
  else:
     buffer until causal predecessors arrive
```

### 3.6 Offline model

```text
Local optimistic apply → enqueue op
On connect: push pending; pull; rebase
If rebase conflict: surface to user or create Conflict for ops
Compaction: when pending large, take local snapshot watermark
```

Storage on client: SQLite / Rocks-like; encryption at rest for sensitive configs.

### 3.7 Conflict lifecycle (dashboard)

```text
OPEN → ASSIGNED → RESOLVED (merged_doc + reason) → CLOSED
        ↓
     ESCALATED / FROZEN_PEER
```

Ops actions: choose A, choose B, edit merge, rollback to snapshot, freeze peer writes, force authoritative server state.

### 3.8 Authority & overrides

| Actor | Rights |
|-------|--------|
| Device peer | Write allowed fields in scope |
| User peer | Same + UI |
| Ops admin | Override, resolve, freeze, resync |
| Automation | Policy auto-resolve only |

**Server authoritative override** produces an op with `authority=ADMIN` that clients must accept (authz checked).

### 3.9 Trade-off tables

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| SoR | Cloud hub / home cell | Audit + dashboard | Mesh without audit |
| History | Op log + snapshots | Catch-up & debug | State-only overwrite |
| Merge | Per-field policy | Correctness | Global LWW |
| Realtime | Pubsub notify + pull | Scale | Giant payload push always |
| Blobs | Object store | Size | Base64 in ops |
| Dashboard | Indexed conflict service | UX | Grep logs |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
 +-------------+     +-------------+     +----------------+
 | Mobile/Agent|     | Web Client  |     | Ops Dashboard  |
 | (local DB)  |     | (local DB)  |     | (resolve UI)   |
 +------+------+     +------+------+     +--------+-------+
        |                   |                      |
        +---------+---------+                      |
                  | push/pull/ws                   | REST
                  v                                v
         +------------------+             +----------------+
         | Sync Gateway     |             | Conflict API   |
         | authz, rate limit|             | + Audit        |
         +--------+---------+             +--------+-------+
                  |                                |
       +----------+----------+                     |
       |                     |                     |
       v                     v                     v
 +-----------+        +-------------+       +--------------+
 | Op Log    |------->| Apply/Merge |------>| Doc Store    |
 | (sharded) |        | Engine      |       | (sharded)    |
 +-----------+        +------+------+       +--------------+
                             |
                             v
                      +--------------+
                      | Pubsub Fanout|
                      +--------------+
                             |
                             v
                      Object Store (blobs)
```

### 4.2 Sequence: concurrent edit → manual resolve

```text
Client A          Client B           Server              Dashboard
  |-- opA set x=1 -->|                 |
  |                  |-- opB set x=2 ->|
  |                  |                 | detect concurrent (VV)
  |                  |                 |-- create Conflict -->|
  |<- ACK (conflict pending) ----------|                   |
  |                  |<- ACK ----------|                   |
  |                  |                 |                   |-- resolve x=2 -->
  |                  |                 | apply resolve op
  |<- pull x=2 -------------------------- notify ----------|
  |                  |<- pull x=2 -----|                   |
```

### 4.3 Sequence: CRDT auto-merge (OR-Set tags)

```text
A: add tag "gpu"     B: add tag "h100"
Server applies both (OR-Set) → doc.tags = {gpu, h100}
No conflict row; both pull merged
```

### 4.4 Sequence: offline batch

```text
Client (offline): local ops o1,o2,o3
Reconnect:
  Push [o1,o2,o3] → ACK
  Pull since cursor → apply remote
  If conflict on o2 → mark + optional local UX
```

### 4.5 Home cell at scale

```text
Global Directory: tenant → cell
Cell: op log shards | doc store | merge workers | conflict index
Gateways active-active → forward writes to home cell
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Hard invariants**

1. **ACK ⇒ durable op** in op log (quorum).  
2. **Idempotent apply** by `op_id`.  
3. **No silent drop of concurrency:** either CRDT-merge or conflict object.  
4. **Causal apply** (buffer until parents present) or explicit reject+resync.  
5. **Resolve CAS:** conflict transitions monotonic; audit every resolve.  
6. **Tenant isolation** on every read/write path.  
7. **Tombstones retained** until all peers’ cursors pass GC watermark.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| Gateway crash after disk ACK before client ACK | Client retry; idempotent |
| Apply worker crash mid-doc update | Transaction / idempotent projectors |
| Pubsub loss | Pull is source of truth; notify is hint |
| Clock skew | HLC; avoid raw NTP LWW for critical fields |
| Poison op | Dead-letter; freeze peer; don’t block shard |
| Dual home cell | Directory fencing + epoch |

### 5.2 Scalability

| Scale | Architecture |
|-------|--------------|
| 1× | Monolith sync API + Postgres docs/ops; WS optional |
| 10× | Shard by `hash(tenant_id, doc_id)`; Kafka/Pulsar op log; Redis presence |
| 100× | Merge workers; conflict service; snapshotter; home cells start |
| 1000× | Edge sync proxies; hierarchical subscriptions; cold op archive |

**Fan-out techniques**

- Subscribe at collection granularity with server-side filters.  
- Batch notifies (`server_seq` ranges).  
- Slow peers → fall back to pull-only.  
- Shuffle shard noisy tenants.

**Compaction**

```text
For each doc shard:
  periodically build snapshot S at VV
  GC ops covered by S after min_peer_cursor watermark
  peers behind → send snapshot instead of million ops
```

### 5.3 Maintainability

- Schema registry for collections; compatibility tests.  
- Policy-as-code for field merge (versioned).  
- Chaos: partition client, reorder ops, duplicate pushes, kill apply workers.  
- Replay tools: rebuild doc projector from op log.  
- Feature flag CRDT vs manual per collection.

**Observability**

- Metrics: ingest QPS, apply lag, pull lag histogram, conflict age, resync rate, peer offline duration, fan-out drop.  
- Trace: `op_id`, `doc_id`, `peer_id`, `conflict_id`.  
- Dashboard SLOs: time-to-ack, time-to-resolve p50/p99.

### 5.4 Progressive scale deep dive

**1× MVP**

```text
POST /sync/push  body: ops[]
GET  /sync/pull?cursor=
Postgres: docs, ops, conflicts
Client: SQLite + queue
Dashboard: simple conflict table
```

**10×**

- Kafka topic per shard; apply consumers.  
- Version vectors in doc row.  
- Pubsub for online peers.  
- Rate limits per peer.

**100×**

- Field-level CRDT library in apply engine.  
- Snapshotter jobs.  
- Conflict Elasticsearch/OpenSearch index for ops UX.  
- Home cell routing.

**1000×**

```text
Edge proxy terminates client sync near region
Forwards to home cell; caches immutable snapshots
Op archive to object storage; rebuild on demand
Hierarchical fanout trees for huge subscriber sets
```

### 5.5 CRDT vs OT vs VV+manual (decision guide)

| If interviewer pushes… | You say… |
|------------------------|----------|
| Collaborative text | OT or specialized CRDT text—separate from config sync |
| Config enums | VV detect + manual / admin authority |
| Presence counters | CRDT counters |
| “Just use timestamps” | Explain skew & lost updates; HLC LWW only for low stakes |

### 5.6 Dashboard design (product + system)

**Views**

1. Conflict inbox (filter tenant, age, collection, severity).  
2. Diff viewer (A vs B vs base).  
3. Peer health (last sync, pending, error).  
4. Lag heatmap by shard.  
5. Audit trail for resolves.  

**APIs**

```text
GET  /conflicts?state=OPEN
GET  /conflicts/{id}
POST /conflicts/{id}/resolve { choice | merged_doc, reason }
POST /peers/{id}/freeze
POST /docs/{id}/force { doc, reason }
GET  /metrics/lag
```

**Deal-breaker:** Dashboard reading primary doc store with full scans every second.

### 5.7 Security

- mTLS or device tokens for agents; SSO for dashboard.  
- Signed ops (optional) to prevent peer spoofing inside tenant.  
- PII minimization in audit.  
- Resolve requires elevated role; dual-control for critical collections.

### 5.8 Deal-breaker gallery

| Temptation | Why it fails |
|------------|--------------|
| REST PUT last-write only | Silent lost updates |
| Global NTP LWW for safety | Clock skew disasters |
| Notify-only without pull | Lost messages ⇒ permanent drift |
| Unbounded op retention in OLTP | Cost & latency melt |
| Single websocket server | Fan-out cliff |
| Dual-active writers two regions same doc | Divergence unless CRDT everywhere |
| Blobs in op log | Throughput death |

---

## 6. Wrap-Up

### 6.1 Key decisions

| Decision | Choice |
|----------|--------|
| Topology | Hub-and-spoke → home cells |
| History | Durable op log + snapshots |
| Merge | Per-field CRDT / LWW / manual |
| Offline | Local store + pending ops + resync |
| Conflicts | First-class records + dashboard |
| Realtime | Notify hint + pull truth |
| Authority | Admin override ops |

### 6.2 Top risks

1. Wrong merge policy on critical fields  
2. Fan-out under-designed  
3. Op log without compaction  
4. Clock-skew LWW  
5. Dashboard not built as its own query path  

### 6.3 45-minute interview plan

| Time | Focus |
|------|-------|
| 0–5 | Entities, offline, conflict definition |
| 5–12 | Op log protocol + idempotency |
| 12–22 | CRDT/VV/LWW matrix + HLD |
| 22–32 | Offline + conflict dashboard |
| 32–40 | Scale & fan-out & cells |
| 40–45 | Failures + deal-breakers |

---

## 7. Deeper / Related Interview Questions

### 7.1 Consistency semantics

**Q: Is the system strongly consistent?**  
A: Hub apply is linearizable per doc shard; clients are eventually consistent with causal pull. Don’t claim global linearizability across offline peers.

**Q: Happens-before?**  
A: Version vectors / parent ids capture causality; concurrent if incomparable VVs.

**Q: Can we avoid conflicts entirely?**  
A: Only with single-writer authority or perfect CRDT modeling—product reality needs both auto and manual.

### 7.2 CRDT details

**Q: OR-Set remove then add?**  
A: Tag adds with unique ids; remove tombstones those tags; concurrent add wins separately—explain briefly.

**Q: LWW-Register safe?**  
A: Use HLC; still loses concurrent semantic intent—OK for display_name, not safety_mode.

**Q: PN-Counter?**  
A: Separate P and N G-Counters; mention if counts sync.

**Q: Metadata growth?**  
A: Compact tombstones with GC watermarks after all peers ack.

### 7.3 OT

**Q: When OT over CRDT?**  
A: Fine-grained collaborative text with server transforms; heavier—usually not for device config sync.

### 7.4 Protocol edge cases

**Q: Out-of-order ops?**  
A: Buffer by parents or request gap fill; snapshots repair.

**Q: Exactly-once?**  
A: At-least-once delivery + idempotent `op_id` apply.

**Q: Push batch atomicity?**  
A: Prefer per-op durability; optional transactional batch for UX.

### 7.5 Offline

**Q: 7 days offline?**  
A: Cap pending; snapshot; on reconnect maybe full resync; conflict likelihood rises—UX must handle.

**Q: Optimistic UI wrong?**  
A: Rebase; show conflict banners; don’t hide server authority.

### 7.6 Dashboard / ops

**Q: Who wins if two ops resolve same conflict?**  
A: CAS on conflict version; loser refreshes.

**Q: Freeze peer?**  
A: Server rejects pushes from peer_id; allow pull; audit.

**Q: Force document?**  
A: Admin op with authority bit; clients must apply; may create local conflict UX.

### 7.7 Multi-region

**Q: Active-active sync hubs?**  
A: Only with CRDT-everywhere or single-writer home cell. Prefer home cell for MVP correctness.

**Q: Peer in region A, home in B?**  
A: Gateway forwards; edge cache snapshots for read-mostly.

### 7.8 Security & abuse

**Q: Peer floods ops?**  
A: Per-peer rate limits; max doc size; quarantine.

**Q: Tenant isolation bug?**  
A: Mandatory tenant_id from auth token, not body; integration tests.

### 7.9 Performance

**Q: Hot doc with 100 writers/s?**  
A: CRDT if possible; else single-writer lease; or shard logical subdocs.

**Q: 10M subscribers to one collection?**  
A: Hierarchical fan-out; pull-based catch-up; don’t unicast 10M huge payloads.

### 7.10 Schema evolution

**Q: Old client missing field?**  
A: Ignore unknown; server preserves; validators versioned.

**Q: Field type change?**  
A: Additive dual fields; migrate; avoid in-place type flip.

### 7.11 NVIDIA-flavored prompts

**Q: Sync GPU agent health + config?**  
A: Telemetry mostly one-way (client→cloud); config bidirectional with admin authority; conflicts on config via dashboard.

**Q: Multi-cluster desired state?**  
A: GitOps-like desired vs reported; sync reported up; desired down; conflict if two control planes set desired—home authority.

### 7.12 Comparison

**Q: vs Firebase / CouchDB / DynamoDB sync?**  
A: Similar op/replication ideas; call out your explicit conflict UX and per-field policies.

**Q: vs Kafka mirror?**  
A: Transport vs document merge semantics—Kafka alone doesn’t resolve JSON conflicts.

### 7.13 Reliability drills

**Q: Drop half of notifies?**  
A: Pull heals; monitor lag.

**Q: Apply projector bug?**  
A: Rebuild from op log; version projectors.

### 7.14 Arithmetic traps

**Q: 50B ops/day × 500 B?**  
A: **25 TB/day** — compaction mandatory.

### 7.15 One-line correctness

> Pull is truth, notify is hint; ACK means durable; concurrent writes become CRDT merges or first-class conflicts—never silent last-PUT-wins on critical fields.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- documents
(tenant_id, collection, doc_id,
 state_json,
 vv BYTEA,              -- version vector
 updated_at,
 PRIMARY KEY (...))

-- ops
(shard, server_seq BIGSERIAL,
 tenant_id, collection, doc_id,
 op_id UUID,
 peer_id,
 parents,
 hlc,
 payload_json,
 UNIQUE(peer_id, op_id))

-- conflicts
(conflict_id, tenant_id, doc_id,
 op_ids[],
 base_snapshot,
 state OPEN|RESOLVED,
 resolved_by, merged_json, reason)

-- peer_cursors
(peer_id, shard, cursor_seq, last_seen)
```

### 8.2 API checklist

- [ ] `POST /sync/push`  
- [ ] `GET /sync/pull`  
- [ ] `WS /sync/subscribe`  
- [ ] Conflict CRUD/resolve  
- [ ] Peer freeze / resync  
- [ ] Admin force doc  
- [ ] Metrics lag endpoints  
- [ ] Blob presign upload  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Op | Idempotent mutation with identity |
| VV | Version vector for causality/concurrency |
| CRDT | Conflict-free replicated data type |
| HLC | Hybrid logical clock |
| Cursor | Peer’s consumed server_seq per shard |
| Home cell | Single-writer region for tenant |
| Authority op | Admin override clients must accept |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Push/pull, idempotent ops, VV conflicts, basic UI |
| 10× | Sharded log, pubsub, rate limits |
| 100× | CRDT policies, snapshots, conflict service, cells |
| 1000× | Edge proxies, hierarchical fan-out, cold archive |

### 8.5 Field policy examples

```text
collection: device_config
  fields:
    tags: OR-Set
    nickname: LWW-Register(hlc)
    power_limit_w: MANUAL_ON_CONFLICT
    enabled: LWW-Register(hlc) + admin_can_override
```

### 8.6 Client state machine

```text
ONLINE:  push loop + pull/ws apply
OFFLINE: local apply + queue
RESYNC:  snapshot fetch + cursor reset
CONFLICT_LOCAL: UX banner; await server resolve or local choose if allowed
```

### 8.7 Interview “say this” summary (60 seconds)

> Bidirectional hub sync with durable op logs, offline queues, and per-field merge policies (CRDT / HLC-LWW / manual). Version vectors detect concurrency; conflicts are first-class and resolved in an ops dashboard with audit. Notify for low latency, pull for correctness; scale via shards, snapshots, and tenant home cells.

### 8.8 Extra traps

| Trap | Pushback |
|------|----------|
| Last HTTP PUT wins | Lost updates |
| WS without pull | Drift |
| One merge strategy | Wrong semantics |
| Ops in OLTP forever | Compact |
| 50B×500B=25PB/day | **25TB/day** |

### 8.9 Reliability test plan

1. Duplicate push → single apply.  
2. Concurrent scalar → conflict row.  
3. Concurrent set add → auto union.  
4. Drop notifies → pull heals.  
5. Two resolvers → CAS one winner.  
6. Offline 24h → snapshot path.  

### 8.10 Observability SLOs

| SLO | Target example |
|-----|----------------|
| Push ACK p99 | < 500ms |
| Online propagate p99 | < 5s |
| Conflict visible in UI | < 10s |
| Time-to-resolve (human) | product KPI |
| Drift (peers behind >1h) | alert |

### 8.11 Related systems map

```text
Peers → Sync GW → Op Log → Apply/Merge → Doc Store
                         ↓
                   Conflict Svc → Dashboard
                         ↓
                      Pubsub → Peers
```

### 8.12 Tombstone GC rules

```text
delete op → tombstone retained
GC when: all peer cursors > tombstone_seq AND snapshot covers it
AND legal retain period elapsed
```

### 8.13 Severity model for conflicts

```text
P0: safety_mode / auth / billing fields
P1: deployment config
P2: display metadata
Dashboard sorts by severity × age
```

### 8.14 Blob sync sketch

```text
client uploads blob → object store → op {set field: hash, size, url}
peers pull op → download blob if hash missing
never inline multi-MB in op log
```

### 8.15 NVIDIA bridge lines

- Agents report observed state up; control plane desired state down.  
- Dashboard is for humans when automated merge is unsafe.  
- Tie CRDT choice to data semantics, not buzzwords.

---

*End of bidirectional data-sync dashboard system design.*
