"""Shared helpers for Bank C doc generation."""
from __future__ import annotations

APPLE_LENS = """
### 1.0 Apple interview lens (say this early)

| Dimension | Apple-weighted expectation | Anti-pattern |
|-----------|---------------------------|--------------|
| Privacy | Minimize server-visible PII; on-device processing first; retention & deletion are first-class | Logging raw content "for ML" without consent |
| Auth | Apple ID + device attestation; least-privilege tokens | Writable endpoints with guessable IDs |
| APIs | Versioned contracts; idempotency; clear error taxonomy | Chatty RPCs on cellular |
| Storage | Clear SoT; encryption at rest; sync tokens; conflict policy | Dual SoT without reconciliation |
| Offline | Local-first where required; queue + replay | Assume always-online |
| On-device / server | Explicit boundary: what never leaves device | Accidental cloud of secrets/health/raw content |
"""


def std_deep(topic: str, entity: str, sync_primitive: str) -> list[tuple[str, str]]:
    return [
        ("Reliability & durability invariants", f"""1. Local durable write before UI ACK for user mutations in **{topic}**.
2. Cloud durable ACK before local eviction of last copy (where applicable).
3. Idempotent apply by `mutation_id` / `message_id` / `op_id`.
4. Tombstones for deletes; never silent drop.

| Failure | Mitigation |
|---------|------------|
| App kill mid-sync | Resume from outbox/cursor |
| Home cell outage | Local continues; queue; epoch fence on failover |
| Bitrot | AEAD + checksums end-to-end |
| Push loss | Pull reconcile on next wake |
| Dual-writer split brain | Single-writer home cell per `{entity}` |"""),
        ("Scalability & sharding", f"""```text
{entity} → home_cell (consistent hash / directory)
{sync_primitive} partitioned by {entity}
Hot entities → dedicated shards / rate limits
```

| Scale | Change |
|-------|--------|
| 1× | Monolithic log + object store |
| 10× | Cell directory; push coalescing |
| 100× | Regional placement; compaction/snapshots |
| 1000× | Hierarchical cursors; cold tiers; strict radio budgets |"""),
        ("Maintainability & schema evolution", f"""- Version mutation/envelope schema (`schema_v`, `op_type`).
- Additive fields only for old clients.
- Feature flags per account for new semantics.
- Observability: sizes, latencies, error codes—not plaintext **{topic}** content."""),
        ("Conflict resolution walk-through", f"""**Example 1 — concurrent edits offline:**
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
```"""),
        ("Battery-conscious sync behavior", """| Lever | Mechanism |
|-------|-----------|
| Coalesce | Batch mutations; min interval between radio wakes |
| Defer | Large blobs on Wi‑Fi + charging unless user-visible |
| Adaptive parallelism | 1 stream cellular; N on Wi‑Fi |
| Budget | OS background energy integration |
| Push not poll | Dirty-bit wakes; reconcile pull |"""),
        ("Security & privacy checklist", """- TLS 1.3; pinning where appropriate.
- Secure Enclave for key material.
- AEAD for sensitive payloads; AAD binds entity ids.
- Server authz: device session touches only owned entities.
- Rate limits on fetch to mitigate account takeover exfil.
- E2E mode: server stores ciphertext only; no plaintext derivatives."""),
        ("Observability without spying", """| Metric OK | Metric NOT OK |
|-----------|----------------|
| Cursor lag, upload success | Message/note/health body text |
| Part retry counts | Raw attachment bytes logged |
| Battery energy samples | Decrypted field values |
| Error codes / sizes | GPS plaintext under E2E |"""),
        ("Progressive scale operations", """```text
Baseline: single region, per-user home cell
10×: shard mailboxes/logs; APNs coalescer fleet
100×: regional blob placement; snapshot baselines for far-behind clients
1000×: hierarchical cursors; admission control; cold storage tiers
```"""),
    ]


def std_estimation(topic: str, daily_ops: str, avg_size: str, peak_mult: str = "2–5×") -> list[tuple[str, str]]:
    return [
        ("Daily volume", f"""```text
{topic} operations: {daily_ops}
Avg payload: {avg_size}
Peak ≈ {peak_mult} average → size sharding + coalescing mandatory at 100×
```"""),
        ("Metadata vs payload split", """```text
Control plane (cursors, acks, small envelopes) → high QPS, low bytes
Payload plane (blobs, attachments) → low QPS relative, high bytes
Battery cost often dominated by radio wake count, not raw MB
```"""),
        ("Per-device sync traffic", """```text
Active device daily:
  - Pull: cursor fetch + N delta mutations (few MB typical)
  - Push: outbox flush batched every T seconds
  - Large transfers deferred to Wi‑Fi/charging unless user-initiated
```"""),
        ("Control-plane QPS sketch", """```text
Users × active fraction × sync sessions/hour → session starts/s
Each session amplifies to metadata req/s
1000×: cells + push coalescing mandatory; no global poll
```"""),
        ("Storage steady state", """```text
Delete-after-ack / compaction keeps steady-state ≪ daily write volume
Backlog during outage: hours × peak write rate → plan shard capacity
```"""),
        ("Energy model (qualitative)", """```text
E_sync ≈ N_wakes × E_radio_spinup + bytes × E_tx
Minimize N_wakes via coalescing collapse_id / dirty batching
Defer large payloads when Low Power Mode && !charging
```"""),
    ]


def S(**kwargs) -> dict:
    defaults = {
        "estimation": None,
        "deep": None,
        "qa_extra": None,
        "apps_extra": None,
        "extras": "",
        "end_name": None,
    }
    defaults.update(kwargs)
    t = defaults
    if t["estimation"] is None:
        t["estimation"] = std_estimation(t["title"], "see scales table", "1–4 KB")
    if t["deep"] is None:
        t["deep"] = std_deep(t["title"], t["entity"], t["sync_primitive"])
    if t["qa_extra"] is None:
        t["qa_extra"] = []
    if t["apps_extra"] is None:
        t["apps_extra"] = []
    if t["end_name"] is None:
        t["end_name"] = t["title"].lower()
    t["apple_lens"] = APPLE_LENS
    return t


def base_qa(topic: str, extra: list) -> list:
    common = [
        ("Privacy & on-device split", [
            (f"What must never leave the device plaintext in {topic}?",
             "User content and sensitive metadata under E2E/ADP-style modes; server should see ciphertext or anonymized aggregates only."),
            ("How do you explain on-device vs server to the interviewer?",
             "Client owns encrypt/decrypt, conflict apply, and battery scheduling; server owns durable ordering, fan-out, and blob storage of opaque bytes."),
            ("Can support engineers read user data?",
             "Not under E2E. Recovery/escrow is an explicit product mode with UX—not a silent backdoor."),
        ]),
        ("Offline & conflicts", [
            ("What happens after a week offline?",
             "Local writes accumulate in an outbox; on reconnect, catch-up via cursor/snapshot; conflicts resolve with documented LWW/CRDT/merge rules."),
            ("How do you avoid silent data loss?",
             "Local durability before ACK to UI; cloud durable ACK before eviction; idempotent mutation ids; tombstones for deletes."),
            ("Clock skew?",
             "Do not trust wall clocks alone—use server_seq / lamport / vector clocks as appropriate."),
        ]),
        ("Battery & networking", [
            ("Why coalesce sync wakes?",
             "Radio spin-up dominates energy; batch mutations and use push dirty-bits instead of polling."),
            ("Cellular vs Wi-Fi policy?",
             "Default: metadata/small on cellular; large blobs on Wi-Fi/charging unless user overrides."),
            ("Low Power Mode?",
             "Defer background transfers; keep user-initiated paths snappy."),
        ]),
        ("Scale & cells", [
            ("Why home cell / single-writer?",
             "Avoid dual-writer split brain for a user's sync log or mailbox."),
            ("What breaks at 1000× if you keep one Postgres?",
             "Write QPS, heartbeat/sync chatty paths, and noisy neighbors—must shard by user/library/device."),
            ("How do you shape thundering herds?",
             "Jitter, coalescing, admission control, snapshot baselines for far-behind clients."),
        ]),
        ("Reliability drills", [
            ("Kill app mid-upload/sync?",
             "Resume with idempotent sessions; fencing tokens if leases exist."),
            ("Home cell failover?",
             "Epoch fence old primary; expect at-least-once replay; clients idempotent."),
            ("Corruption / bitrot?",
             "Checksums end-to-end; AEAD tags; re-fetch or re-upload parts."),
        ]),
        ("Interview traps", [
            ("Claiming E2E while server generates plaintext derivatives",
             "Contradiction—call it out."),
            ("Evicting local data before cloud ACK",
             "Data-loss bug."),
            ("Polling every few seconds forever",
             "Battery death."),
            ("Unit errors (PB vs TB)",
             "Always show arithmetic."),
        ]),
        ("Comparison & differentiation", [
            (f"How is {topic} different from generic cloud file sync?",
             "Apple products need explicit on-device vs server boundaries, E2E/ADP modes, battery-aware schedulers, and conflict policies—not just S3 + Postgres."),
            ("How does this compare to Google/Dropbox approach?",
             "Stress on-device processing, minimal server retention, and user-visible privacy modes without disparaging competitors."),
            (f"What would you cut if the interview is 30 minutes?",
             "Defer extreme scale (1,000×), sharing ACLs, web clients, and federated/ML paths—keep local-first + encryption + sync + conflicts."),
        ]),
        ("Operational drills", [
            ("How do you test battery impact?",
             "Instruments energy trace; count radio wakes; verify coalescing under bursty mutations; compare against baseline budget."),
            ("How do you test conflict correctness?",
             "Dual-device sim offline edits; property tests on merge; never assert silent data loss."),
            ("What metrics alert on-call without violating privacy?",
             "Cursor lag, upload failure rate, chunk retries, push wake counts—never body text or decrypted fields."),
        ]),
    ]
    return extra + common


def base_apps(topic: str, extra: list) -> list:
    common = [
        ("Progressive scale checklist",
         """| Scale | Must have |
|-------|-----------|
| 1× | Local-first, durable outbox, basic sync, privacy boundary clear |
| 10× | Sharding/cells, push coalesce, resumable transfers |
| 100× | Regional placement, compaction/snapshots, dedicated hot path |
| 1000× | Hierarchical cursors, cold tiers, strict radio budgets, isolation |"""),
        ("Observability SLOs (privacy-safe)",
         """| SLO | Example |
|-----|---------|
| Local durable write | p99 < 100ms |
| Sync cursor lag (active) | p99 < 60s |
| User-visible fetch | p50 targets per product |
| Unexpected data loss | **0** |
| Background energy | Within OS budget |

Metrics: sizes, latencies, error codes—not plaintext content."""),
        ("Threat model snapshot",
         """| Threat | Control |
|--------|---------|
| Curious server/admin | E2E ciphertext / on-device processing |
| Stolen device | Secure Enclave, passcode, remote revoke |
| MITM | TLS + pinning where appropriate |
| Account takeover | Step-up auth, device lists, rate limits |
| Integrity attacks | AEAD, checksums, authz on refs |"""),
        ("Reliability test plan",
         f"""1. Offline write for 24h then sync—no loss in {topic}.
2. Mid-transfer kill/resume.
3. Dual-device conflicting edits—deterministic merge.
4. Device revoke/key rotation.
5. Cell failover with idempotent replay.
6. Battery: verify coalesced wakes under bursty updates."""),
        ("Interview 60-second summary",
         f"""> For {topic}: keep a crisp local-first story, put encryption and conflict rules on the client, let the server order opaque sync operations and store ciphertext, schedule radios for battery, and scale with per-user cells plus cursors/snapshots. Call out privacy mode forks explicitly."""),
        ("Decision log template",
         """| Decision | Choice | Rationale |
|----------|--------|-----------|
| Trust boundary | Client encrypts sensitive data | Apple privacy bar |
| Sync primitive | Op-log / mailbox / CRDT (pick) | Product semantics |
| Conflict policy | Explicit LWW/OR-set/merge | User trust |
| Offline | Outbox + durable local DB | Airplane mode |
| Scale unit | user/library/device shard | Single-writer |"""),
        ("Open questions for interviewer",
         f"""1. Is Advanced Data Protection / E2E required or optional for {topic}?
2. Exact conflict UX when automatic merge is ambiguous?
3. Web/browser clients in scope?
4. Cross-user sharing / family features in MVP?
5. Retention / legal hold constraints?"""),
        ("Related systems map",
         f"""```text
UI/App → Local DB/Outbox → Encrypt/Keys → Sync Agent
                              ↓
                     Edge API / Home Cell
                              ↓
              Mutation Log / Mailbox / Object Store
                              ↓
                     Push Coalescer → Other Devices
Battery/Network Scheduler influences when Sync Agent runs
```"""),
        ("Glossary extras",
         """| Term | Meaning |
|------|---------|
| Outbox | Local durable queue of pending sync ops |
| Cursor | Per-device progress in server log |
| Home cell | Single-writer region for an entity |
| Tombstone | Soft-delete marker |
| AEAD | Authenticated encryption with associated data |
| Coalescing | Merging many wakes into one radio session |"""),
        ("Anti-patterns",
         f"""| Anti-pattern | Why it hurts {topic} |
|--------------|----------------------|
| Chatty per-keystroke sync | Battery + server QPS |
| Server plaintext "for ML" under E2E claim | Privacy contradiction |
| Unbounded full resync | Network/battery meltdown |
| Dual active writers without merge | Split brain |
| Silent conflict drop | User trust destruction |"""),
        ("API sketch (interview whiteboard)",
         """```text
POST /v1/sync/push        batch encrypted mutations (idempotent op_ids)
GET  /v1/sync/pull        ?cursor=&limit=   returns ops + server_seq
POST /v1/blobs/session    resumable upload (parts + complete)
GET  /v1/blobs/{ref}/part fetch ciphertext part (authz)
POST /v1/devices/register key directory / push token
DELETE /v1/devices/{id}   revoke + stop fan-out
GET  /v1/snapshot         optional baseline for far-behind clients
```
All payloads: TLS + device session auth; sensitive fields ciphertext client-side."""),
        ("Schema sketches (generic)",
         f"""```text
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
```"""),
        ("Compaction & snapshot algorithm",
         """```text
periodically per entity shard:
  S = fold(sync_log[1..N]) into encrypted snapshot blob
  publish snapshot@S for cold clients
  retain sync_log (S-W, ∞] for lagging cursors
  GC older ops when all device cursors > S-W (grace period)
```"""),
        ("Priority scoring (scheduler reference)",
         """```text
score = w1*user_visible + w2*small_payload + w3*age_hours
        - w4*cellular_cost - w5*battery_penalty - w6*thermal_penalty
defer if Low Power && !charging && !user_visible
boost user-initiated open/share/export paths immediately
```"""),
    ]
    return extra + common
