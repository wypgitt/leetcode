# System Design: Notes Synchronization and Conflict Resolution

> **Focus areas:** CRDT vs op-log · Rich text merge · Attachments · Folders · E2E · Offline · Battery · On-device preview  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths, Apple-style privacy / on-device boundaries

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

Goal: **bound Notes sync**—multi-device note/folder sync with rich-text conflicts, attachments, and Apple-grade privacy.

### 1.0 Apple interview lens (say this early)

| Dimension | Apple-weighted expectation | Anti-pattern |
|-----------|---------------------------|--------------|
| Privacy | Minimize server-visible PII; on-device processing first; retention & deletion are first-class | Logging raw content "for ML" without consent |
| Auth | Apple ID + device attestation; least-privilege tokens | Writable endpoints with guessable IDs |
| APIs | Versioned contracts; idempotency; clear error taxonomy | Chatty RPCs on cellular |
| Storage | Clear SoT; encryption at rest; sync tokens; conflict policy | Dual SoT without reconciliation |
| Offline | Local-first where required; queue + replay | Assume always-online |
| On-device / server | Explicit boundary: what never leaves device | Accidental cloud of secrets/health/raw content |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What syncs? | Notes, folders, tags, attachments, checklists, locks | Separate note body vs attachment plane |
| F2 | Rich text? | Attributed string / block JSON | Field-level or block-level merge |
| F3 | E2E? | Standard + optional E2E category | Ciphertext bodies under E2E |
| F4 | Conflicts? | Rare auto-merge; surface conflict note if ambiguous | 3-way merge + conflict clone |
| F5 | Attachments? | Images, scans, drawings | Encrypted blob refs in note |
| F6 | Shared notes? | Optional collab | Share ACL + share key phase 2 |
| F7 | Offline? | Full edit offline | Outbox + causal ops |
| F8 | Delete? | Recently Deleted window | Tombstones |
| F9 | Search? | On-device index preferred | Encrypted index optional |
| F10 | Locks? | Face ID note lock | Key stays on-device; body extra encrypted |
| F11 | Web? | Limited under E2E | Keys on trusted devices only |
| F12 | Version history? | Optional snapshots | Periodic encrypted snapshots |

**MVP functional scope (lock with interviewer):**

1. Local-first note CRUD
2. Encrypted mutation log per account
3. LWW metadata + block merge for body
4. Attachment upload/download
5. Folder tree sync
6. Conflict note UX
7. Battery-coalesced sync

**Out of MVP (explicitly defer):**

- Real-time OT like Google Docs
- Full CRDT for rich text at 1,000×
- Cross-org enterprise ACLs

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Privacy | E2E option | Server opaque under E2E |
| N2 | Edit latency | Instant local | p99 local write < 50ms |
| N3 | Sync lag | Background OK | p99 cursor lag < 60s active |
| N4 | Battery | No keystroke sync | Debounce + coalesce |
| N5 | Offline | Weeks OK | Outbox durable |
| N6 | Consistency | Eventual | Documented merge |
| N7 | Durability | No lost notes | Local before UI; cloud before eviction |
| N8 | Availability | 99.9% sync plane | Local always works |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Type on iPhone offline → sync on Wi‑Fi → Mac shows note
2. Attach scan → encrypt → upload → iPad fetches thumb
3. Rename folder on Mac → iPhone tree updates
4. Delete → tombstone → restore from Recently Deleted
5. Concurrent checklist toggles merge via OR-set

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Two devices edit same paragraph | Block merge or conflict note |
| Huge attachment | Chunked resumable upload |
| Note lock | Body key wrapped locally |
| Account merge | Out of MVP |
| Import 10k notes | Snapshot baseline |
| Clock skew | Lamport + server_seq |
| Corrupt block | Checksum fail → re-fetch |
| Shared note leave | Rekey share |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Accounts | 100M | 500M | 1B | 1B+ cells |
| Notes/account avg | 200 | 400 | 600 | 800 |
| Edits/day | 500M | 5B | 50B | 500B |
| Attachments/day | 50M | 500M | 5B | 50B |
| Avg note body | 4 KB | 6 KB | 8 KB | 10 KB |
| Avg attachment | 500 KB | 1 MB | 2 MB | 3 MB |
| Sync sessions/day | 200M | 2B | 20B | 200B |
| Conflict rate | 0.1% | 0.1% | 0.05% | 0.05% |

**What each jump forces:**

- **10×:** Shard logs; debounced push
- **100×:** Compaction snapshots; attachment CDN ciphertext
- **1,000×:** Hierarchical cursors; block-level CRDT subset

### 1.5 Etc. (Constraints & Assumptions)

- Not designing full iWork collab
- Rich text merge is hard—document policy
- E2E limits server search

**Scope statement:**

> Design Apple Notes–style sync: local-first editing, encrypted mutation log or CRDT hybrid, attachment blobs, folder hierarchy, explicit conflict UX, and battery-aware background sync—from millions of accounts through 10× / 100× / 1,000× scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Daily volume

```text
Note edits operations: 500M/day
Avg payload: 4–8 KB body + metadata
Peak ≈ 3× average → size sharding + coalescing mandatory at 100×
```

### 2.2 Metadata vs payload split

```text
Control plane (cursors, acks, small envelopes) → high QPS, low bytes
Payload plane (blobs, attachments) → low QPS relative, high bytes
Battery cost often dominated by radio wake count, not raw MB
```

### 2.3 Per-device sync traffic

```text
Active device daily:
  - Pull: cursor fetch + N delta mutations (few MB typical)
  - Push: outbox flush batched every T seconds
  - Large transfers deferred to Wi‑Fi/charging unless user-initiated
```

### 2.4 Control-plane QPS sketch

```text
Users × active fraction × sync sessions/hour → session starts/s
Each session amplifies to metadata req/s
1000×: cells + push coalescing mandatory; no global poll
```

### 2.5 Storage steady state

```text
Delete-after-ack / compaction keeps steady-state ≪ daily write volume
Backlog during outage: hours × peak write rate → plan shard capacity
```

### 2.6 Energy model (qualitative)

```text
E_sync ≈ N_wakes × E_radio_spinup + bytes × E_tx
Minimize N_wakes via coalescing collapse_id / dirty batching
Defer large payloads when Low Power Mode && !charging
```

### 2.7 Unit-check traps

| Claim | Truth |
|-------|-------|
| Sync every keystroke | Battery death |
| Server generates note previews under E2E | Contradiction |
| 500M edits × 1MB = 500 PB/day | Check units—bodies are KB-scale |

### 2.8 Critical bottlenecks (rank ordered)

1. Debounced sync still high QPS at 100×  
2. Attachment ingress  
3. Folder tree deep renames  
4. Conflict note UX volume  
5. Compaction of long note histories

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Account, Note(note_id, folder_id, body_enc, lamport)
Folder(folder_id, parent_id, title)
Attachment(att_id, blob_ref, note_id)
Mutation(op_id, note_id, op_type, payload_enc, lamport)
DeviceCursor(account_id, last_seq)
```

### 3.2 On-device vs server split

| Concern | On-device | Server |
|---------|----------|--------|
| Edit/merge apply | Yes | Orders ops only |
| Encrypt body | Yes | Stores ciphertext |
| Search index | Prefer on-device | Optional encrypted index |
| Preview render | Yes | No plaintext |
| Debounce sync | Yes | Receives batches |

### 3.3 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Full doc CRDT | Auto-merge | Complex rich text | Team capacity |
| B. Op-log + LWW whole doc | Simple | Lost edits | Rich text |
| C. Op-log + block merge + conflict UI | Balanced | Some manual UX | — chosen |
| D. Last sync wins only | Easy | Bad UX | Never |

**Chosen path:** Encrypted op-log with block-level merge; ambiguous regions → conflict note clone.

### 3.4 Privacy, trust, and encryption

Note body encrypted with per-note or account key; attachments separate content keys inside envelope; server sees sizes and opaque refs only under E2E.

### 3.5 Consistency, sync, and conflict resolution

Single-writer home cell assigns `server_seq`; offline ops carry lamport; body merge on apply.

### 3.6 Offline-first behavior

SQLite/Core Data outbox; edit immediately local; sync agent batches on network/battery OK.

### 3.7 Battery, radio, and scheduling

Debounce edits 2–5s; coalesce folder tree ops; defer attachment uploads on cellular.

### 3.8 Multi-region / cell model

Home cell per account; regional blob store; edge read for attachments.

### 3.9 Abuse, auth, and quotas

Rate limits; max note size; attachment quotas.

### 3.10 Key invariants (state these explicitly)

1. **Local durability before UI ACK** for user-initiated writes.
2. **Cloud durability before local eviction** of the last copy of user data (where applicable).
3. **Idempotent apply** — replay of the same `op_id` / `mutation_id` / `message_id` is safe.
4. **Tombstones for delete** — never silently drop data without retention policy.
5. **Single-writer home cell** per user/library/device shard to avoid split brain.
6. **Battery-aware radio use** — coalesce wakes; defer large payloads on cellular/LPM unless user-visible.



### 3.11 Advanced Data Protection (ADP) fork

| Mode | Server sees | On-device responsibility |
|------|-------------|---------------------------|
| ADP / E2E on | Ciphertext blobs + opaque sync envelopes | Decrypt, merge, ML, search |
| Standard protection | May allow richer server-side features | Still minimize retention; disclose trade-off |

**Interview win:** Offer both modes; do not claim server plaintext AI/derivatives while ADP E2E holds.

---

## 4. Architecture Diagram

```text
iPhone/Mac Notes App → Local DB + Outbox → Encrypt
                              ↓
                     Sync Agent (debounced)
                              ↓
              Edge API → Mutation Log (home cell)
                              ↓
              Attachment Store (ciphertext) + Push Coalescer
```

---

## 5. Design Deep Dive

### 5.1 Reliability & durability invariants

1. Local durable write before UI ACK for user mutations in **Notes Synchronization and Conflict Resolution**.
2. Cloud durable ACK before local eviction of last copy (where applicable).
3. Idempotent apply by `mutation_id` / `message_id` / `op_id`.
4. Tombstones for deletes; never silent drop.

| Failure | Mitigation |
|---------|------------|
| App kill mid-sync | Resume from outbox/cursor |
| Home cell outage | Local continues; queue; epoch fence on failover |
| Bitrot | AEAD + checksums end-to-end |
| Push loss | Pull reconcile on next wake |
| Dual-writer split brain | Single-writer home cell per `account_id / note_id` |

### 5.2 Scalability & sharding

```text
account_id / note_id → home_cell (consistent hash / directory)
Encrypted mutation log partitioned by account_id / note_id
Hot entities → dedicated shards / rate limits
```

| Scale | Change |
|-------|--------|
| 1× | Monolithic log + object store |
| 10× | Cell directory; push coalescing |
| 100× | Regional placement; compaction/snapshots |
| 1000× | Hierarchical cursors; cold tiers; strict radio budgets |

### 5.3 Maintainability & schema evolution

- Version mutation/envelope schema (`schema_v`, `op_type`).
- Additive fields only for old clients.
- Feature flags per account for new semantics.
- Observability: sizes, latencies, error codes—not plaintext **Notes Synchronization and Conflict Resolution** content.

### 5.4 Conflict resolution walk-through

**Example 1 — concurrent edits offline:**
```text
Device A: set field X @ lamport 5
Device B: set field X @ lamport 6 → B wins (LWW)
Equal lamport → tie-break device_id
```

**Example 2 — delete vs edit:**
```text
Delete tombstone causally after last edit → hidden everywhere
Edit after delete within retention → restore/quarantine UX
```

**Example 3 — set membership:**
```text
OR-set add-wins; remove via tagged tombstone
```

### 5.5 Battery-conscious sync behavior

| Lever | Mechanism |
|-------|-----------|
| Coalesce | Batch mutations; min interval between radio wakes |
| Defer | Large blobs on Wi‑Fi + charging unless user-visible |
| Adaptive parallelism | 1 stream cellular; N on Wi‑Fi |
| Budget | OS background energy integration |
| Push not poll | Dirty-bit wakes; reconcile pull |

### 5.6 Security & privacy checklist

- TLS 1.3; pinning where appropriate.
- Secure Enclave for key material.
- AEAD for sensitive payloads; AAD binds entity ids.
- Server authz: device session touches only owned entities.
- Rate limits on fetch to mitigate account takeover exfil.
- E2E mode: server stores ciphertext only; no plaintext derivatives.

### 5.7 Observability without spying

| Metric OK | Metric NOT OK |
|-----------|----------------|
| Cursor lag, upload success | Message/note/health body text |
| Part retry counts | Raw attachment bytes logged |
| Battery energy samples | Decrypted field values |
| Error codes / sizes | GPS plaintext under E2E |

### 5.8 Progressive scale operations

```text
Baseline: single region, per-user home cell
10×: shard mailboxes/logs; APNs coalescer fleet
100×: regional blob placement; snapshot baselines for far-behind clients
1000×: hierarchical cursors; admission control; cold storage tiers
```

---

## 6. Wrap-Up

### 6.1 What we designed

Local-first Notes with encrypted op-log, block-aware merge, attachment ciphertext, explicit conflict notes, and debounced battery-aware sync.

### 6.2 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| CRDT vs op-log | Op-log + selective merge | Ship complexity |
| Keystroke sync | Debounced batches | Battery |
| E2E vs server search | On-device search under E2E | Privacy |
| Conflict auto vs manual | Auto + conflict note fallback | Trust |

### 6.3 MVP → scale path

MVP: op-log + LWW metadata + block merge. 10–100×: shards, snapshots. 1000×: hierarchical cursors, optional CRDT blocks.

### 6.4 Risks

- Rich text merge bugs
- Chatty sync
- Evict-before-ACK
- Ambiguous conflict UX

---

## 7. Deeper / Related Interview Questions

### 7.1 Notes-specific

**Q: How merge rich text?**  
A: Block/paragraph ops with lamport; conflict note if overlapping edits.

**Q: Checklist items?**  
A: OR-set per item id.

**Q: Locked notes?**  
A: Extra key in Secure Enclave; sync ciphertext only.

### 7.2 Privacy & on-device split

**Q: What must never leave the device plaintext in Notes Synchronization and Conflict Resolution?**  
A: User content and sensitive metadata under E2E/ADP-style modes; server should see ciphertext or anonymized aggregates only.

**Q: How do you explain on-device vs server to the interviewer?**  
A: Client owns encrypt/decrypt, conflict apply, and battery scheduling; server owns durable ordering, fan-out, and blob storage of opaque bytes.

**Q: Can support engineers read user data?**  
A: Not under E2E. Recovery/escrow is an explicit product mode with UX—not a silent backdoor.

### 7.3 Offline & conflicts

**Q: What happens after a week offline?**  
A: Local writes accumulate in an outbox; on reconnect, catch-up via cursor/snapshot; conflicts resolve with documented LWW/CRDT/merge rules.

**Q: How do you avoid silent data loss?**  
A: Local durability before ACK to UI; cloud durable ACK before eviction; idempotent mutation ids; tombstones for deletes.

**Q: Clock skew?**  
A: Do not trust wall clocks alone—use server_seq / lamport / vector clocks as appropriate.

### 7.4 Battery & networking

**Q: Why coalesce sync wakes?**  
A: Radio spin-up dominates energy; batch mutations and use push dirty-bits instead of polling.

**Q: Cellular vs Wi-Fi policy?**  
A: Default: metadata/small on cellular; large blobs on Wi-Fi/charging unless user overrides.

**Q: Low Power Mode?**  
A: Defer background transfers; keep user-initiated paths snappy.

### 7.5 Scale & cells

**Q: Why home cell / single-writer?**  
A: Avoid dual-writer split brain for a user's sync log or mailbox.

**Q: What breaks at 1000× if you keep one Postgres?**  
A: Write QPS, heartbeat/sync chatty paths, and noisy neighbors—must shard by user/library/device.

**Q: How do you shape thundering herds?**  
A: Jitter, coalescing, admission control, snapshot baselines for far-behind clients.

### 7.6 Reliability drills

**Q: Kill app mid-upload/sync?**  
A: Resume with idempotent sessions; fencing tokens if leases exist.

**Q: Home cell failover?**  
A: Epoch fence old primary; expect at-least-once replay; clients idempotent.

**Q: Corruption / bitrot?**  
A: Checksums end-to-end; AEAD tags; re-fetch or re-upload parts.

### 7.7 Interview traps

**Q: Claiming E2E while server generates plaintext derivatives**  
A: Contradiction—call it out.

**Q: Evicting local data before cloud ACK**  
A: Data-loss bug.

**Q: Polling every few seconds forever**  
A: Battery death.

**Q: Unit errors (PB vs TB)**  
A: Always show arithmetic.

### 7.8 Comparison & differentiation

**Q: How is Notes Synchronization and Conflict Resolution different from generic cloud file sync?**  
A: Apple products need explicit on-device vs server boundaries, E2E/ADP modes, battery-aware schedulers, and conflict policies—not just S3 + Postgres.

**Q: How does this compare to Google/Dropbox approach?**  
A: Stress on-device processing, minimal server retention, and user-visible privacy modes without disparaging competitors.

**Q: What would you cut if the interview is 30 minutes?**  
A: Defer extreme scale (1,000×), sharing ACLs, web clients, and federated/ML paths—keep local-first + encryption + sync + conflicts.

### 7.9 Operational drills

**Q: How do you test battery impact?**  
A: Instruments energy trace; count radio wakes; verify coalescing under bursty mutations; compare against baseline budget.

**Q: How do you test conflict correctness?**  
A: Dual-device sim offline edits; property tests on merge; never assert silent data loss.

**Q: What metrics alert on-call without violating privacy?**  
A: Cursor lag, upload failure rate, chunk retries, push wake counts—never body text or decrypted fields.

---

## 8. Appendices

### 8.1 Mutation types

```text
NOTE_CREATE / NOTE_DELETE / NOTE_BODY_PATCH
FOLDER_MOVE / FOLDER_RENAME
ATTACH_ADD / ATTACH_REMOVE
CHECKLIST_TOGGLE (OR-set)
```

### 8.2 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Local-first, durable outbox, basic sync, privacy boundary clear |
| 10× | Sharding/cells, push coalesce, resumable transfers |
| 100× | Regional placement, compaction/snapshots, dedicated hot path |
| 1000× | Hierarchical cursors, cold tiers, strict radio budgets, isolation |

### 8.3 Observability SLOs (privacy-safe)

| SLO | Example |
|-----|---------|
| Local durable write | p99 < 100ms |
| Sync cursor lag (active) | p99 < 60s |
| User-visible fetch | p50 targets per product |
| Unexpected data loss | **0** |
| Background energy | Within OS budget |

Metrics: sizes, latencies, error codes—not plaintext content.

### 8.4 Threat model snapshot

| Threat | Control |
|--------|---------|
| Curious server/admin | E2E ciphertext / on-device processing |
| Stolen device | Secure Enclave, passcode, remote revoke |
| MITM | TLS + pinning where appropriate |
| Account takeover | Step-up auth, device lists, rate limits |
| Integrity attacks | AEAD, checksums, authz on refs |

### 8.5 Reliability test plan

1. Offline write for 24h then sync—no loss in Notes Synchronization and Conflict Resolution.
2. Mid-transfer kill/resume.
3. Dual-device conflicting edits—deterministic merge.
4. Device revoke/key rotation.
5. Cell failover with idempotent replay.
6. Battery: verify coalesced wakes under bursty updates.

### 8.6 Interview 60-second summary

> For Notes Synchronization and Conflict Resolution: keep a crisp local-first story, put encryption and conflict rules on the client, let the server order opaque sync operations and store ciphertext, schedule radios for battery, and scale with per-user cells plus cursors/snapshots. Call out privacy mode forks explicitly.

### 8.7 Decision log template

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trust boundary | Client encrypts sensitive data | Apple privacy bar |
| Sync primitive | Op-log / mailbox / CRDT (pick) | Product semantics |
| Conflict policy | Explicit LWW/OR-set/merge | User trust |
| Offline | Outbox + durable local DB | Airplane mode |
| Scale unit | user/library/device shard | Single-writer |

### 8.8 Open questions for interviewer

1. Is Advanced Data Protection / E2E required or optional for Notes Synchronization and Conflict Resolution?
2. Exact conflict UX when automatic merge is ambiguous?
3. Web/browser clients in scope?
4. Cross-user sharing / family features in MVP?
5. Retention / legal hold constraints?

### 8.9 Related systems map

```text
UI/App → Local DB/Outbox → Encrypt/Keys → Sync Agent
                              ↓
                     Edge API / Home Cell
                              ↓
              Mutation Log / Mailbox / Object Store
                              ↓
                     Push Coalescer → Other Devices
Battery/Network Scheduler influences when Sync Agent runs
```

### 8.10 Glossary extras

| Term | Meaning |
|------|---------|
| Outbox | Local durable queue of pending sync ops |
| Cursor | Per-device progress in server log |
| Home cell | Single-writer region for an entity |
| Tombstone | Soft-delete marker |
| AEAD | Authenticated encryption with associated data |
| Coalescing | Merging many wakes into one radio session |

### 8.11 Anti-patterns

| Anti-pattern | Why it hurts Notes Synchronization and Conflict Resolution |
|--------------|----------------------|
| Chatty per-keystroke sync | Battery + server QPS |
| Server plaintext "for ML" under E2E claim | Privacy contradiction |
| Unbounded full resync | Network/battery meltdown |
| Dual active writers without merge | Split brain |
| Silent conflict drop | User trust destruction |

### 8.12 API sketch (interview whiteboard)

```text
POST /v1/sync/push        batch encrypted mutations (idempotent op_ids)
GET  /v1/sync/pull        ?cursor=&limit=   returns ops + server_seq
POST /v1/blobs/session    resumable upload (parts + complete)
GET  /v1/blobs/{ref}/part fetch ciphertext part (authz)
POST /v1/devices/register key directory / push token
DELETE /v1/devices/{id}   revoke + stop fan-out
GET  /v1/snapshot         optional baseline for far-behind clients
```
All payloads: TLS + device session auth; sensitive fields ciphertext client-side.

### 8.13 Schema sketches (generic)

```text
-- device local
local_records(id, payload, updated_lamport, deleted_at)
outbox(op_id, envelope_enc, created_at)
cursors(shard_id, last_applied_seq)

-- server (home cell)
sync_log(entity_id, server_seq, op_id, envelope_enc, device_id, ts)
blobs(ref, entity_id, size, checksum, storage_class)
upload_sessions(id, entity_id, state, parts_json)
tombstones(entity_id, id, seq, purge_after)
devices(user_id, device_id, keys, push_token, revoked_at)
```

### 8.14 Compaction & snapshot algorithm

```text
periodically per entity shard:
  S = fold(sync_log[1..N]) into encrypted snapshot blob
  publish snapshot@S for cold clients
  retain sync_log (S-W, ∞] for lagging cursors
  GC older ops when all device cursors > S-W (grace period)
```

### 8.15 Priority scoring (scheduler reference)

```text
score = w1*user_visible + w2*small_payload + w3*age_hours
        - w4*cellular_cost - w5*battery_penalty - w6*thermal_penalty
defer if Low Power && !charging && !user_visible
boost user-initiated open/share/export paths immediately
```

### 8.16 Client sync agent pseudocode

```text
loop:
  wait(push_dirty OR timer OR user_action OR battery_ok_window)
  if not network_allowed(): continue
  push_outbox_batch(limit=K)
  pull_since(cursor, limit=K)
  apply_idempotent(mutations)
  ack_cursor()
  maybe_compact_local()
```

### 8.17 Home-cell failover note

```text
epoch++
fence old primary writes
clients retry with backoff
in-flight ops idempotent by mutation_id
expect at-least-once delivery of sync ops
```

### 8.18 What "done" looks like in 45 minutes

- Clear MVP scope  
- Correct trust boundary (on-device vs server)  
- One coherent diagram  
- Conflict resolution example  
- Scale + battery paragraph  
- Honest non-goals  

### 8.19 Cellular / Wi‑Fi policy matrix

| Condition | Metadata sync | Small payloads | Large blobs |
|-----------|---------------|----------------|-------------|
| Wi‑Fi | Yes | Yes | Yes |
| Cellular default | Yes | Recent/small | Defer |
| Cellular + user allow | Yes | Yes | Budget-capped |
| Low Power Mode | Coalesce | Defer | Defer |
| Charging + Wi‑Fi | Max throughput | Max | Max |

### 8.20 Interview traps (expanded)

| Trap | Pushback |
|------|----------|
| Server reads user content under E2E claim | Contradiction—call ADP/E2E fork |
| Evict local before cloud ACK | Data-loss bug |
| Poll every few seconds | Battery death |
| Dual active writers without merge | Split brain |
| Unit errors (PB vs TB) | Show arithmetic always |
| "We'll add privacy later" | Apple bar: privacy-first architecture |

---

*End of notes synchronization and conflict resolution system design.*

