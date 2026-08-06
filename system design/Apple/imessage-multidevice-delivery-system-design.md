# System Design: iMessage Multi-Device Delivery

> **Focus areas:** E2E encryption · Per-device fan-out · Offline mailboxes · Push coalescing · Attachments · Battery · Key directory  
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

Goal: **bound delivery**—how a message reaches all of a user's devices with E2E encryption, without the server reading content.

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
| F1 | Who sends/receives? | Apple ID users with registered devices; SMS fallback out of band | Separate iMessage path vs PSTN |
| F2 | Delivery semantics? | At-least-once to each device; UI dedupe | Per-device queues + ack |
| F3 | E2E? | Yes—server cannot read bodies | Encrypt per recipient device |
| F4 | Multi-device? | All signed-in devices receive | Fan-out envelopes + self devices |
| F5 | Offline? | Queue until online; TTL days | Durable mailbox |
| F6 | Attachments? | Encrypted blob refs | Pointer + file key inside E2E body |
| F7 | Groups? | N members × M devices | Fan-out; later sender-keys |
| F8 | Receipts? | Delivered/read optional | Encrypt receipts; user toggles |
| F9 | Edit/unsend? | Windowed edit; best-effort unsend | Mutation messages + tombstones |
| F10 | Spam? | Prefer on-device | Anonymous server signals only |
| F11 | Registration? | Trusted device enrollment | Key directory updates |
| F12 | Push? | APNs wakes; minimal payload | Push as signal, not content |

**MVP functional scope (lock with interviewer):**

1. Register device keys
2. Send 1:1 with per-device envelopes
3. Per-device mailbox + ack GC
4. Self-fanout to sender devices
5. Encrypted attachments
6. Basic group fan-out
7. Coalesced push wakes

**Out of MVP (explicitly defer):**

- Full MLS lecture
- SMS/RCS gateway internals
- Business chat server search
- Guaranteed unsend against offline adversary

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Confidentiality | E2E | Server sees envelopes only |
| N2 | Latency | Interactive | p50 < 300ms online |
| N3 | Offline durability | Days | Multi-AZ mailbox |
| N4 | Battery | Push not poll | Coalesce APNs |
| N5 | Integrity | Tamper-evident | AEAD |
| N6 | Availability | 99.99% send | Retry + degrade |
| N7 | Fan-out cost | Groups OK | Optimize later |
| N8 | Metadata privacy | Minimize | Pad sizes; short logs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. A sends to B; all B devices decrypt; receipts return
2. B offline; queue; fetch; ack; GC
3. A's Mac+iPhone show sent via self-fanout
4. Attachment upload ciphertext + pointer
5. New iPad receives subsequent messages

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Stolen device | Revoke keys; no new decrypt |
| Key directory poison | Transparency/attest; warn on key change |
| Duplicate delivery | Dedupe message_id |
| Partial group fail | Retry missing devices |
| APNs loss | Pull reconcile |
| Huge group | Sender-keys; rate limits |
| Attachment orphan | Refcount + TTL GC |
| Decrypt fail | Quarantine + session repair |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active users | 50M | 500M | 500M+ | 500M+ |
| Messages/day | 10B | 100B | 1T | 10T |
| Peak send QPS | 200K | 2M | 20M | 200M |
| Devices/user | 3 | 3 | 3.5 | 4 |
| Avg envelope | 1KB | 1KB | 1.2KB | 1.5KB |
| Mailbox depth p99 | 500 | 500 | 1K | 2K |
| Attachment uploads/day | 500M | 5B | 50B | 500B |
| Group size p99 | 50 | 50 | 100 | 200 |

**What each jump forces:**

- **10×:** Shard mailboxes; key cache; APNs coalesce
- **100×:** Regional gateways; attachment edge; fanout workers
- **1,000×:** Sender-keys/MLS; sealed sender; metadata minimization

### 1.5 Etc. (Constraints & Assumptions)

- Server untrusted for content
- Metadata still sensitive
- SMS is different channel
- Not designing full APNs internals

**Scope statement:**

> Design an E2E multi-device iMessage-style delivery system: per-device encryption, durable offline mailboxes, attachment ciphertext, group fan-out, push wakes, and progressive scale—without the server reading message bodies.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Daily volume

```text
iMessage envelopes operations: 10B/day × 1 KB ≈ 10 TB/day
Avg payload: 1–1.5 KB
Peak ≈ 2× average → size sharding + coalescing mandatory at 100×
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
| 10B×1KB=10PB/day | **10 TB/day** |
| Fan-out is free | Multiply by devices |
| Peak = average | Use 2–5× |

### 2.8 Critical bottlenecks (rank ordered)

1. Per-device mailbox write QPS  
2. Key directory under send storms  
3. Attachment object store  
4. Sender encrypt CPU for large groups  
5. APNs storms  
6. Ack/GC races

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
User, Device(identity_key, push_token)
Conversation, Message(message_id)
Envelope(recipient_device_id, ciphertext)
MailboxQueue(device_id)
AttachmentBlob(blob_ref)
KeyDirectory(user → device key bundles)
```

### 3.2 On-device vs server split

| Concern | On-device | Server |
|---------|----------|--------|
| Encrypt/decrypt | Yes | No |
| Key gen | Secure Enclave | Public keys only |
| Mailbox | Local outbox | Durable per-device queue |
| Spam ML | Prefer on-device | Anonymous signals |
| Push payload | — | Opaque wake |

### 3.3 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Server plaintext fan-out | Easy | Breaks E2E | Privacy required |
| B. One user key all devices | Fewer encrypts | Revoke weak | Device revoke needed |
| C. Per-device envelopes (+ sender-keys later) | Proper revoke | Costly fan-out | — chosen |
| D. Pure P2P | Max privacy | Offline hard | Mobile offline |

**Chosen path:** Per-device ciphertext envelopes into durable mailboxes; APNs as wake; evolve large groups to sender-keys.

### 3.4 Privacy, trust, and encryption

Sender fetches recipient device pubkeys; AEAD per device (ratchet). Server routes opaque envelopes. Attachments: `file_key` lives inside E2E body; blob store holds ciphertext only.

### 3.5 Consistency, sync, and conflict resolution

Eventual delivery; per-device `arrival_seq`; client dedupe by `message_id`; edits/unsends are new messages referencing targets.

### 3.6 Offline-first behavior

Durable outbox before UI sent; recipient mailbox until fetch+ack; history via encrypted backup (related system).

### 3.7 Battery, radio, and scheduling

Coalesce APNs per conversation; backup pull while active; defer large attachments on cellular.

### 3.8 Multi-region / cell model

Home cell for mailbox metadata; global send anycast → forward; regional attachment placement.

### 3.9 Abuse, auth, and quotas

Rate limits; registration friction; on-device spam; report bundles without plaintext retention.

### 3.10 Key invariants (state these explicitly)

1. **Local durability before UI ACK** for user-initiated writes.
2. **Cloud durability before local eviction** of the last copy of user data (where applicable).
3. **Idempotent apply** — replay of the same `op_id` / `mutation_id` / `message_id` is safe.
4. **Tombstones for delete** — never silently drop data without retention policy.
5. **Single-writer home cell** per user/library/device shard to avoid split brain.
6. **Battery-aware radio use** — coalesce wakes; defer large payloads on cellular/LPM unless user-visible.


### 3.12 Group messaging evolution path

| Phase | Approach | When |
|-------|----------|------|
| MVP | Per-device envelope fan-out | Small groups, 1:1 |
| 10× | Sender chain keys | Medium groups |
| 1000× | MLS-style group sessions | Large groups, lower encrypt CPU |

**Sealed sender (phase 2):** Hide sender identity from server metadata where product allows—separate key server trust assumptions.


### 3.11 Advanced Data Protection (ADP) fork

| Mode | Server sees | On-device responsibility |
|------|-------------|---------------------------|
| ADP / E2E on | Ciphertext blobs + opaque sync envelopes | Decrypt, merge, ML, search |
| Standard protection | May allow richer server-side features | Still minimize retention; disclose trade-off |

**Interview win:** Offer both modes; do not claim server plaintext AI/derivatives while ADP E2E holds.

---

## 4. Architecture Diagram

```text
iPhone A / Mac A → Send API → Key Directory
                 → Fanout Service → Mailboxes (B1,B2,B3)
                 → APNs wake → devices pull/ack
                 → Attachment Object Store (ciphertext)
```

**Send path:** UI → outbox → fetch keys → encrypt N envelopes → persist mailboxes → wake → pull → decrypt → ACK.

---

## 5. Design Deep Dive

### 5.1 Reliability & delivery invariants

1. Persist all envelopes before send ACK.  
2. ACK deletes only after local durable store.  
3. Dedupe `message_id`.  
4. Revoked devices receive no new envelopes.

| Failure | Mitigation |
|---------|------------|
| Sender crash post-accept | Server receipt; outbox reconciles |
| Mailbox AZ loss | Quorum write |
| Decrypt fail | Session repair UI |
| Push loss | Pull reconcile |

### 5.2 Scalability

Shard mailbox by `recipient_device_id`; fanout workers; key caches. Groups: MVP per-device → sender-keys → MLS-style at extreme.

### 5.3 Maintainability

Envelope versioning; ratchet agility; feature flags for edit/unsend; don't brick old devices.

### 5.4 Crypto sketch (interview-depth)

```text
X3DH-like session from prekeys → Double Ratchet 1:1
Multi-device: session per device
Groups: fan-out sealed boxes → sender chain keys
```
Naming Signal-style primitives is enough; don't implement crypto in 45 minutes.

### 5.5 Attachments

Encrypt file with `file_key` → chunk upload → message carries `blob_ref + file_key` inside E2E body → recipients download ciphertext.

### 5.6 Registration & trust

Auth + optional existing-device approval; publish keys; history transfer via QR/proximity/encrypted backup—separate design.

---

## 6. Wrap-Up

### 6.1 What we designed

E2E multi-device messaging: clients encrypt per device, servers fan out opaque envelopes to durable mailboxes, APNs wakes devices, attachments are ciphertext, groups evolve to sender-keys.

### 6.2 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| E2E vs server search | E2E | Privacy |
| Per-device vs per-user key | Per-device | Revocation |
| Push content vs signal | Signal | Privacy/size |
| Global order | Per-device mailbox order | Scale |

### 6.3 MVP → scale path

MVP: 1:1+simple groups, mailboxes, attachments. 10–100×: shards + fanout fleet. 1000×: sender-keys, sealed sender.

### 6.4 Risks

- Key directory poison
- Metadata leakage
- Fan-out cost
- Ack/GC races

---

## 7. Deeper / Related Interview Questions

### 7.1 Messaging-specific

**Q: Exactly-once to UI?**  
A: At-least-once + client dedupe.

**Q: Why encrypt to my own Mac?**  
A: Multi-device thread visibility with per-device keys.

**Q: Can Apple read messages?**  
A: Not bodies under E2E; metadata still sensitive.

### 7.2 Privacy & on-device split

**Q: What must never leave the device plaintext in iMessage Multi-Device Delivery?**  
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

**Q: How is iMessage Multi-Device Delivery different from generic cloud file sync?**  
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

### 8.1 Envelope schema

```text
Envelope {{ message_id, conversation_id, recipient_device_id, ciphertext, ratchet_header, arrival_seq }}
```

### 8.2 API checklist

- [ ] Register/Revoke device  
- [ ] GetKeyBundle  
- [ ] SendEnvelopes  
- [ ] FetchMailbox / Ack  
- [ ] Attachment sessions

### 8.3 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Local-first, durable outbox, basic sync, privacy boundary clear |
| 10× | Sharding/cells, push coalesce, resumable transfers |
| 100× | Regional placement, compaction/snapshots, dedicated hot path |
| 1000× | Hierarchical cursors, cold tiers, strict radio budgets, isolation |

### 8.4 Observability SLOs (privacy-safe)

| SLO | Example |
|-----|---------|
| Local durable write | p99 < 100ms |
| Sync cursor lag (active) | p99 < 60s |
| User-visible fetch | p50 targets per product |
| Unexpected data loss | **0** |
| Background energy | Within OS budget |

Metrics: sizes, latencies, error codes—not plaintext content.

### 8.5 Threat model snapshot

| Threat | Control |
|--------|---------|
| Curious server/admin | E2E ciphertext / on-device processing |
| Stolen device | Secure Enclave, passcode, remote revoke |
| MITM | TLS + pinning where appropriate |
| Account takeover | Step-up auth, device lists, rate limits |
| Integrity attacks | AEAD, checksums, authz on refs |

### 8.6 Reliability test plan

1. Offline write for 24h then sync—no loss in iMessage Multi-Device Delivery.
2. Mid-transfer kill/resume.
3. Dual-device conflicting edits—deterministic merge.
4. Device revoke/key rotation.
5. Cell failover with idempotent replay.
6. Battery: verify coalesced wakes under bursty updates.

### 8.7 Interview 60-second summary

> For iMessage Multi-Device Delivery: keep a crisp local-first story, put encryption and conflict rules on the client, let the server order opaque sync operations and store ciphertext, schedule radios for battery, and scale with per-user cells plus cursors/snapshots. Call out privacy mode forks explicitly.

### 8.8 Decision log template

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trust boundary | Client encrypts sensitive data | Apple privacy bar |
| Sync primitive | Op-log / mailbox / CRDT (pick) | Product semantics |
| Conflict policy | Explicit LWW/OR-set/merge | User trust |
| Offline | Outbox + durable local DB | Airplane mode |
| Scale unit | user/library/device shard | Single-writer |

### 8.9 Open questions for interviewer

1. Is Advanced Data Protection / E2E required or optional for iMessage Multi-Device Delivery?
2. Exact conflict UX when automatic merge is ambiguous?
3. Web/browser clients in scope?
4. Cross-user sharing / family features in MVP?
5. Retention / legal hold constraints?

### 8.10 Related systems map

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

### 8.11 Glossary extras

| Term | Meaning |
|------|---------|
| Outbox | Local durable queue of pending sync ops |
| Cursor | Per-device progress in server log |
| Home cell | Single-writer region for an entity |
| Tombstone | Soft-delete marker |
| AEAD | Authenticated encryption with associated data |
| Coalescing | Merging many wakes into one radio session |

### 8.12 Anti-patterns

| Anti-pattern | Why it hurts iMessage Multi-Device Delivery |
|--------------|----------------------|
| Chatty per-keystroke sync | Battery + server QPS |
| Server plaintext "for ML" under E2E claim | Privacy contradiction |
| Unbounded full resync | Network/battery meltdown |
| Dual active writers without merge | Split brain |
| Silent conflict drop | User trust destruction |

### 8.13 API sketch (interview whiteboard)

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

### 8.14 Schema sketches (generic)

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

### 8.15 Compaction & snapshot algorithm

```text
periodically per entity shard:
  S = fold(sync_log[1..N]) into encrypted snapshot blob
  publish snapshot@S for cold clients
  retain sync_log (S-W, ∞] for lagging cursors
  GC older ops when all device cursors > S-W (grace period)
```

### 8.16 Priority scoring (scheduler reference)

```text
score = w1*user_visible + w2*small_payload + w3*age_hours
        - w4*cellular_cost - w5*battery_penalty - w6*thermal_penalty
defer if Low Power && !charging && !user_visible
boost user-initiated open/share/export paths immediately
```

### 8.17 Client sync agent pseudocode

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

### 8.18 Home-cell failover note

```text
epoch++
fence old primary writes
clients retry with backoff
in-flight ops idempotent by mutation_id
expect at-least-once delivery of sync ops
```

### 8.19 What "done" looks like in 45 minutes

- Clear MVP scope  
- Correct trust boundary (on-device vs server)  
- One coherent diagram  
- Conflict resolution example  
- Scale + battery paragraph  
- Honest non-goals  

### 8.20 Cellular / Wi‑Fi policy matrix

| Condition | Metadata sync | Small payloads | Large blobs |
|-----------|---------------|----------------|-------------|
| Wi‑Fi | Yes | Yes | Yes |
| Cellular default | Yes | Recent/small | Defer |
| Cellular + user allow | Yes | Yes | Budget-capped |
| Low Power Mode | Coalesce | Defer | Defer |
| Charging + Wi‑Fi | Max throughput | Max | Max |

### 8.21 Interview traps (expanded)

| Trap | Pushback |
|------|----------|
| Server reads user content under E2E claim | Contradiction—call ADP/E2E fork |
| Evict local before cloud ACK | Data-loss bug |
| Poll every few seconds | Battery death |
| Dual active writers without merge | Split brain |
| Unit errors (PB vs TB) | Show arithmetic always |
| "We'll add privacy later" | Apple bar: privacy-first architecture |

---

*End of iMessage multi-device delivery system design.*

