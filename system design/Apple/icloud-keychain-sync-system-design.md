# System Design: Secure iCloud Keychain Synchronization

> **Focus areas:** Secure Enclave · Circle of trust · Escrow · E2E sync · Device approval · Zero-knowledge · Conflict-free creds  
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

Goal: **bound Keychain sync**—sync passwords, keys, and Wi‑Fi creds across devices with zero-knowledge server storage.

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
| F1 | What syncs? | Passwords, keys, certs, Wi‑Fi, Safari autofill | Typed item records |
| F2 | E2E? | Yes—server blind | Ciphertext items only |
| F3 | New device? | Approve from existing device or escrow | Circle of trust |
| F4 | Conflicts? | Rare—items keyed by domain/account | Upsert by stable item id |
| F5 | Revoke? | Remove device from circle | Stop wrapping new keys |
| F6 | Escrow? | Optional recovery | Security vs UX trade-off |
| F7 | Sharing? | Password sharing later | Separate share keys |
| F8 | Web? | No raw keys in browser | Out of scope |
| F9 | Audit? | Device list only | No plaintext logs |
| F10 | TOTP seeds? | Same vault | High sensitivity |
| F11 | Corporate MDM? | Separate profile | Split keychain domains |
| F12 | Migration? | Schema version per item | Additive evolution |

**MVP functional scope (lock with interviewer):**

1. Device enrollment + approval
2. Encrypted item upsert sync
3. Circle of trust management
4. Revoke device
5. Escrow optional path
6. Stable item_id merge

**Out of MVP (explicitly defer):**

- Full HSM escrow lecture
- Cross-platform non-Apple clients
- Enterprise SCIM

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Confidentiality | Zero-knowledge | No server decrypt |
| N2 | Add device latency | Minutes if approval | User-initiated |
| N3 | Sync latency | Background | p99 < 30s after change |
| N4 | Integrity | Tamper-evident | AEAD + signatures |
| N5 | Availability | 99.99% | Local cache always |
| N6 | Recovery | Explicit UX | No silent backdoor |
| N7 | Battery | Tiny payloads | Coalesce OK |
| N8 | Abuse | Stolen account | Step-up + device list |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Save password on iPhone → encrypt → sync → Mac autofill
2. New iPad approved from iPhone → unwrap vault key → pull items
3. Delete login on Mac → tombstone → removed on iPhone
4. Revoke stolen Mac → rotate wraps → no new decrypt

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Approval timeout | Expire request |
| Escrow recovery | Separate auth factors |
| Duplicate item ids | Upsert |
| Clock skew | Server ts for ordering only |
| Corrupt item | Quarantine + re-sync |
| MDM wipe | Local purge |
| Account transfer | Out of MVP |
| Quantum agility | Version crypto suites |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 200M | 500M | 800M | 800M+ |
| Items/user avg | 300 | 400 | 500 | 600 |
| Item writes/day | 100M | 1B | 10B | 100B |
| Avg item blob | 500 B | 600 B | 700 B | 800 B |
| Devices/user | 3 | 3.5 | 4 | 4 |
| New device enroll/day | 2M | 20M | 200M | 2B |
| Approval sessions peak | 50K | 500K | 5M | 50M |
| Revokes/day | 500K | 5M | 50M | 500M |

**What each jump forces:**

- **10×:** Shard item logs; cache public device keys
- **100×:** Regional home cells; batch item deltas
- **1,000×:** Strict rate limits; hierarchical snapshots

### 1.5 Etc. (Constraints & Assumptions)

- Not designing Secure Enclave silicon
- Escrow is product/legal sensitive
- Zero-knowledge is non-negotiable

**Scope statement:**

> Design iCloud Keychain–style sync: Secure Enclave–backed keys, encrypted item blobs, device approval circle, escrow/recovery trade-offs, and conflict-free credential merge—from tens of millions of users through progressive scale.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Daily volume

```text
Keychain item writes operations: 100M/day
Avg payload: ~500 B
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
| Server can reset passwords | Only if escrow/recovery—explicit |
| 100M × 500B items = PB/day | ~50 GB/day item writes—check math |

### 2.8 Critical bottlenecks (rank ordered)

1. New device approval storms  
2. Item log write QPS  
3. Escrow recovery abuse  
4. Revoke/re-wrap races  
5. Autofill read path (local only)

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
User, Device(device_id, identity_key, trust_state)
VaultKey (wrapped per device)
KeychainItem(item_id, type, ciphertext, version)
CircleOfTrust(members[], pending[])
SyncCursor(device_id, seq)
```

### 3.2 On-device vs server split

| Concern | On-device | Server |
|---------|----------|--------|
| Encrypt items | Secure Enclave | Stores ciphertext |
| Approve device | User on trusted device | Routes approval msgs |
| Autofill decrypt | Yes | Never |
| Item merge | Upsert by item_id | Relay only |

### 3.3 Options & trade-offs

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Server-readable vault | Easy autofill web | Breaks zero-knowledge | Apple bar |
| B. Zero-knowledge encrypted items | Privacy | Recovery harder | — chosen |
| C. Per-device vaults only | Simple | No sync | Multi-device |
| D. P2P only sync | No server trust | Offline/recovery hard | Mobile |

**Chosen path:** Zero-knowledge encrypted items with circle-of-trust device approval and optional escrow recovery.

### 3.4 Privacy, trust, and encryption

Vault key never leaves devices as plaintext; server stores wrapped keys and AEAD item blobs; approval requires existing trusted device or escrow.

### 3.5 Consistency, sync, and conflict resolution

Upsert by stable `item_id`; deletes are tombstones; ordering via server_seq for audit not merge logic.

### 3.6 Offline-first behavior

Local Keychain always authoritative for read; writes queue; sync on connectivity.

### 3.7 Battery, radio, and scheduling

Small payloads; batch item deltas; low frequency.

### 3.8 Multi-region / cell model

Home cell per user; global anycast API; no cross-region plaintext.

### 3.9 Abuse, auth, and quotas

Rate limit enroll; step-up on mass export patterns; device attestation.

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
Device A (trusted) ←→ Approval Service ←→ Device B (new)
       ↓                                      ↓
  Keychain local                         Wrap vault key
       ↓                                      ↓
   Item encrypt ──→ Item Sync Log (ciphertext) ──→ other devices
```

---

## 5. Design Deep Dive

### 5.1 Reliability & durability invariants

1. Local durable write before UI ACK for user mutations in **Secure iCloud Keychain Synchronization**.
2. Cloud durable ACK before local eviction of last copy (where applicable).
3. Idempotent apply by `mutation_id` / `message_id` / `op_id`.
4. Tombstones for deletes; never silent drop.

| Failure | Mitigation |
|---------|------------|
| App kill mid-sync | Resume from outbox/cursor |
| Home cell outage | Local continues; queue; epoch fence on failover |
| Bitrot | AEAD + checksums end-to-end |
| Push loss | Pull reconcile on next wake |
| Dual-writer split brain | Single-writer home cell per `user_id` |

### 5.2 Scalability & sharding

```text
user_id → home_cell (consistent hash / directory)
Encrypted item sync log partitioned by user_id
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
- Observability: sizes, latencies, error codes—not plaintext **Secure iCloud Keychain Synchronization** content.

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

Zero-knowledge Keychain sync with Secure Enclave keys, device approval circle, encrypted item upserts, and explicit recovery/escrow modes.

### 6.2 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| Zero-knowledge vs web autofill | ZK | Privacy |
| Escrow vs no recovery | Optional escrow | UX |
| Approval friction | Required | Security |
| Item-level vs blob sync | Item upsert | Merge simplicity |

### 6.3 MVP → scale path

MVP: circle + encrypted upsert. Scale: shard logs, batch deltas, regional cells.

### 6.4 Risks

- Escrow perception as backdoor
- Approval UX friction
- Stolen account + weak 2FA
- Schema migration bugs

---

## 7. Deeper / Related Interview Questions

### 7.1 Privacy & on-device split

**Q: What must never leave the device plaintext in Secure iCloud Keychain Synchronization?**  
A: User content and sensitive metadata under E2E/ADP-style modes; server should see ciphertext or anonymized aggregates only.

**Q: How do you explain on-device vs server to the interviewer?**  
A: Client owns encrypt/decrypt, conflict apply, and battery scheduling; server owns durable ordering, fan-out, and blob storage of opaque bytes.

**Q: Can support engineers read user data?**  
A: Not under E2E. Recovery/escrow is an explicit product mode with UX—not a silent backdoor.

### 7.2 Offline & conflicts

**Q: What happens after a week offline?**  
A: Local writes accumulate in an outbox; on reconnect, catch-up via cursor/snapshot; conflicts resolve with documented LWW/CRDT/merge rules.

**Q: How do you avoid silent data loss?**  
A: Local durability before ACK to UI; cloud durable ACK before eviction; idempotent mutation ids; tombstones for deletes.

**Q: Clock skew?**  
A: Do not trust wall clocks alone—use server_seq / lamport / vector clocks as appropriate.

### 7.3 Battery & networking

**Q: Why coalesce sync wakes?**  
A: Radio spin-up dominates energy; batch mutations and use push dirty-bits instead of polling.

**Q: Cellular vs Wi-Fi policy?**  
A: Default: metadata/small on cellular; large blobs on Wi-Fi/charging unless user overrides.

**Q: Low Power Mode?**  
A: Defer background transfers; keep user-initiated paths snappy.

### 7.4 Scale & cells

**Q: Why home cell / single-writer?**  
A: Avoid dual-writer split brain for a user's sync log or mailbox.

**Q: What breaks at 1000× if you keep one Postgres?**  
A: Write QPS, heartbeat/sync chatty paths, and noisy neighbors—must shard by user/library/device.

**Q: How do you shape thundering herds?**  
A: Jitter, coalescing, admission control, snapshot baselines for far-behind clients.

### 7.5 Reliability drills

**Q: Kill app mid-upload/sync?**  
A: Resume with idempotent sessions; fencing tokens if leases exist.

**Q: Home cell failover?**  
A: Epoch fence old primary; expect at-least-once replay; clients idempotent.

**Q: Corruption / bitrot?**  
A: Checksums end-to-end; AEAD tags; re-fetch or re-upload parts.

### 7.6 Interview traps

**Q: Claiming E2E while server generates plaintext derivatives**  
A: Contradiction—call it out.

**Q: Evicting local data before cloud ACK**  
A: Data-loss bug.

**Q: Polling every few seconds forever**  
A: Battery death.

**Q: Unit errors (PB vs TB)**  
A: Always show arithmetic.

### 7.7 Comparison & differentiation

**Q: How is Secure iCloud Keychain Synchronization different from generic cloud file sync?**  
A: Apple products need explicit on-device vs server boundaries, E2E/ADP modes, battery-aware schedulers, and conflict policies—not just S3 + Postgres.

**Q: How does this compare to Google/Dropbox approach?**  
A: Stress on-device processing, minimal server retention, and user-visible privacy modes without disparaging competitors.

**Q: What would you cut if the interview is 30 minutes?**  
A: Defer extreme scale (1,000×), sharing ACLs, web clients, and federated/ML paths—keep local-first + encryption + sync + conflicts.

### 7.8 Operational drills

**Q: How do you test battery impact?**  
A: Instruments energy trace; count radio wakes; verify coalescing under bursty mutations; compare against baseline budget.

**Q: How do you test conflict correctness?**  
A: Dual-device sim offline edits; property tests on merge; never assert silent data loss.

**Q: What metrics alert on-call without violating privacy?**  
A: Cursor lag, upload failure rate, chunk retries, push wake counts—never body text or decrypted fields.

---

## 8. Appendices

### 8.1 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Local-first, durable outbox, basic sync, privacy boundary clear |
| 10× | Sharding/cells, push coalesce, resumable transfers |
| 100× | Regional placement, compaction/snapshots, dedicated hot path |
| 1000× | Hierarchical cursors, cold tiers, strict radio budgets, isolation |

### 8.2 Observability SLOs (privacy-safe)

| SLO | Example |
|-----|---------|
| Local durable write | p99 < 100ms |
| Sync cursor lag (active) | p99 < 60s |
| User-visible fetch | p50 targets per product |
| Unexpected data loss | **0** |
| Background energy | Within OS budget |

Metrics: sizes, latencies, error codes—not plaintext content.

### 8.3 Threat model snapshot

| Threat | Control |
|--------|---------|
| Curious server/admin | E2E ciphertext / on-device processing |
| Stolen device | Secure Enclave, passcode, remote revoke |
| MITM | TLS + pinning where appropriate |
| Account takeover | Step-up auth, device lists, rate limits |
| Integrity attacks | AEAD, checksums, authz on refs |

### 8.4 Reliability test plan

1. Offline write for 24h then sync—no loss in Secure iCloud Keychain Synchronization.
2. Mid-transfer kill/resume.
3. Dual-device conflicting edits—deterministic merge.
4. Device revoke/key rotation.
5. Cell failover with idempotent replay.
6. Battery: verify coalesced wakes under bursty updates.

### 8.5 Interview 60-second summary

> For Secure iCloud Keychain Synchronization: keep a crisp local-first story, put encryption and conflict rules on the client, let the server order opaque sync operations and store ciphertext, schedule radios for battery, and scale with per-user cells plus cursors/snapshots. Call out privacy mode forks explicitly.

### 8.6 Decision log template

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trust boundary | Client encrypts sensitive data | Apple privacy bar |
| Sync primitive | Op-log / mailbox / CRDT (pick) | Product semantics |
| Conflict policy | Explicit LWW/OR-set/merge | User trust |
| Offline | Outbox + durable local DB | Airplane mode |
| Scale unit | user/library/device shard | Single-writer |

### 8.7 Open questions for interviewer

1. Is Advanced Data Protection / E2E required or optional for Secure iCloud Keychain Synchronization?
2. Exact conflict UX when automatic merge is ambiguous?
3. Web/browser clients in scope?
4. Cross-user sharing / family features in MVP?
5. Retention / legal hold constraints?

### 8.8 Related systems map

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

### 8.9 Glossary extras

| Term | Meaning |
|------|---------|
| Outbox | Local durable queue of pending sync ops |
| Cursor | Per-device progress in server log |
| Home cell | Single-writer region for an entity |
| Tombstone | Soft-delete marker |
| AEAD | Authenticated encryption with associated data |
| Coalescing | Merging many wakes into one radio session |

### 8.10 Anti-patterns

| Anti-pattern | Why it hurts Secure iCloud Keychain Synchronization |
|--------------|----------------------|
| Chatty per-keystroke sync | Battery + server QPS |
| Server plaintext "for ML" under E2E claim | Privacy contradiction |
| Unbounded full resync | Network/battery meltdown |
| Dual active writers without merge | Split brain |
| Silent conflict drop | User trust destruction |

### 8.11 API sketch (interview whiteboard)

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

### 8.12 Schema sketches (generic)

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

### 8.13 Compaction & snapshot algorithm

```text
periodically per entity shard:
  S = fold(sync_log[1..N]) into encrypted snapshot blob
  publish snapshot@S for cold clients
  retain sync_log (S-W, ∞] for lagging cursors
  GC older ops when all device cursors > S-W (grace period)
```

### 8.14 Priority scoring (scheduler reference)

```text
score = w1*user_visible + w2*small_payload + w3*age_hours
        - w4*cellular_cost - w5*battery_penalty - w6*thermal_penalty
defer if Low Power && !charging && !user_visible
boost user-initiated open/share/export paths immediately
```

### 8.15 Client sync agent pseudocode

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

### 8.16 Home-cell failover note

```text
epoch++
fence old primary writes
clients retry with backoff
in-flight ops idempotent by mutation_id
expect at-least-once delivery of sync ops
```

### 8.17 What "done" looks like in 45 minutes

- Clear MVP scope  
- Correct trust boundary (on-device vs server)  
- One coherent diagram  
- Conflict resolution example  
- Scale + battery paragraph  
- Honest non-goals  

### 8.18 Cellular / Wi‑Fi policy matrix

| Condition | Metadata sync | Small payloads | Large blobs |
|-----------|---------------|----------------|-------------|
| Wi‑Fi | Yes | Yes | Yes |
| Cellular default | Yes | Recent/small | Defer |
| Cellular + user allow | Yes | Yes | Budget-capped |
| Low Power Mode | Coalesce | Defer | Defer |
| Charging + Wi‑Fi | Max throughput | Max | Max |

### 8.19 Interview traps (expanded)

| Trap | Pushback |
|------|----------|
| Server reads user content under E2E claim | Contradiction—call ADP/E2E fork |
| Evict local before cloud ACK | Data-loss bug |
| Poll every few seconds | Battery death |
| Dual active writers without merge | Split brain |
| Unit errors (PB vs TB) | Show arithmetic always |
| "We'll add privacy later" | Apple bar: privacy-first architecture |

---

*End of secure icloud keychain synchronization system design.*

