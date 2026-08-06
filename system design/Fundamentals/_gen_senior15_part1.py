#!/usr/bin/env python3
"""Senior/staff system-design markdown generators — Part 1 (5 docs).

Each `doc_*()` RETURNS a complete markdown string (does not write files).
"""
from __future__ import annotations

from _gen_senior15 import header, s1, s2, s3, s4, s5, s6, s7, s8


def _ensure_min(md: str, min_lines: int, pads: list[str]) -> str:
    n = md.count("\n") + (0 if md.endswith("\n") else 1)
    i = 0
    while n < min_lines and pads:
        md = md.rstrip() + "\n\n" + pads[i % len(pads)].strip() + "\n"
        n = md.count("\n") + 1
        i += 1
        if i > len(pads) * 40:
            break
    if not md.endswith("\n"):
        md += "\n"
    return md



# =============================================================================
# 1) Google Docs collaborative editing
# =============================================================================

_PADS_GDOCS = [
    """### Extra: OT transform sketch

```text
Client A: insert("X", pos=5)  Client B: delete(3, len=2) concurrently
Server serializes B first → A must transform insert against delete
If delete range before pos: pos -= 2; else if overlapping: adjust carefully
OT requires TP1: apply(apply(S,op2), transform(op1,op2))
              == apply(apply(S,op1), transform(op2,op1))
```

Interview: total order via server sequencer + per-op-type transform functions.""",
    """### Extra: CRDT list intuition (RGA / Fugue)

```text
Each character = (id=(replica,counter), value, tombstone?)
Insert after left-id; concurrent inserts ordered by id
Deletes are tombstones — never lose concurrent inserts
Snapshot = materialize visible chars; GC after causal frontier ACK
```""",
    """### Extra: Presence fanout budget

```text
50 editors × 10 cursor updates/s = 500 msg/s into doc hub
Fanout to 49 peers ≈ 24.5K msg/s for one hot doc
Mitigations: coalesce (100ms), binary WS, viewport interest mgmt
```""",
    """### Extra: ACL evaluation path

```text
doc_id → ACL version; capabilities: read/comment/edit/manage
Share links: signed tokens with role + expiry; revoke = bump ACL epoch
Offline edit: must re-authz on reconnect before commit to tip
```""",
    """### Extra: Comment threads model

```text
Comment anchored to (start_id, end_id) CRDT positions or sticky bookmarks
Resolve ≠ delete; keep for history; notify @mentions async
Don't put comment bodies in op log of main doc text (separate channel)
```""",
]


def doc_google_docs() -> str:
    t = header(
        "Google Docs Collaborative Editing",
        "OT vs CRDT · Op log · Snapshots · Presence/cursors · Doc shards · WebSocket fanout · ACL · Offline · Revisions · Comments",
        "real-time collaborative document editing under concurrent writers",
    )
    t += s1(
        "design a **Google Docs-like** collaborative editor: multiple users edit the same document in near-real-time with presence, comments, revision history, and correct conflict handling.",
        [
            ("Job", "Multiplayer rich-text document with sync", "Full Google Workspace / Sheets/Slides suite"),
            ("Consistency", "Causal + intention-preserving edits", "Strict single-writer locking only"),
            ("Transport", "WebSocket/long-lived sync channel", "Email-style document attach"),
            ("Lens", "Concurrency, fanout, op log, ACL, offline", "Typesetting engine deep dive only"),
            ("Unit of scale", "Concurrent editors/doc + docs edited/day", "Static file hosting"),
        ],
        [
            ("Who can edit concurrently?", "Tens typical; design for 50–100 on a hot doc", "Per-doc realtime hub + presence coalescing"),
            ("Rich text model?", "Paragraphs, styles, lists; suggest mode optional", "Op types beyond insert/delete chars"),
            ("Conflict strategy?", "OT or CRDT — pick and defend", "Sequencer vs commutative merge"),
            ("Offline?", "Edit offline; merge on reconnect", "Client buffer + transform/CRDT integrate"),
            ("Presence?", "Cursors, selections, viewer list", "High-frequency low-priority channel"),
            ("History?", "Version timeline; restore; named versions", "Snapshots + op log addressing"),
            ("Comments?", "Threaded anchors that survive edits", "Separate comment store + sticky anchors"),
            ("Sharing/ACL?", "Owner/editor/commenter/viewer + link sharing", "AuthZ on connect and on mutate"),
            ("Large docs?", "Hundreds of pages OK", "Sharding / chunked materialization"),
            ("Images/files?", "Inline media via object store pointers", "Blob out of band; ops reference IDs"),
            ("Notifications?", " @mention / share emails async OK", "Not on realtime path"),
            ("Mobile?", "Same sync protocol; flaky networks", "Resume, backoff, idempotent commits"),
            ("Suggestions?", "Suggest mode as first-class ops or layered", "Accept/reject workflow"),
            ("Compliance?", "Export, retention, e-discovery hooks", "Immutable revision archive tier"),
        ],
        [
            "Open doc → sync snapshot + tip; WebSocket session",
            "Character/style ops with intention preservation",
            "Presence: cursors + active user list",
            "Comments with anchors; resolve/unresolve",
            "Share ACL + link roles",
            "Revision history list + restore",
            "Offline buffer + reconnect merge",
            "Inline image upload by reference",
            "Basic suggest mode or defer with clear hook",
        ],
        [
            "Full Sheets formula engine / Slides",
            "Pixel-perfect print pagination day one",
            "End-to-end encrypted CRDT without server visibility (hard mode)",
            "Realtime multi-region active-active for every doc day one",
        ],
        [
            ("Latency", "Local echo <50ms; peer visible p50 <200–300ms same region", "UX feels local"),
            ("Availability", "99.9% edit sessions; degrade to read-only if hub down", "Never silent data loss"),
            ("Durability", "Committed ops survive disk/node loss (quorum WAL)", "11 9s for snapshots in object store"),
            ("Consistency", "All editors converge; no torn snapshots", "Session fences on ACL revoke"),
            ("Multi-region", "Docs pinned to home region; cross-region followers", "RPO seconds for DR"),
            ("Security", "ACL on every mutate; signed session; audit share events", "Link revoke immediate-ish"),
            ("Cost", "Presence coalesce; snapshot compaction; cold history tier", "Hot docs dominate WS cost"),
            ("Scale cue", "Concurrent editors/doc + docs actively edited/day", "Shard hubs by doc_id"),
        ],
        [
            "Alice and Bob type in different paragraphs → both see each other quickly",
            "Alice pastes image → blob upload → op inserts media ref",
            "Owner shares link as commenter → Bob can comment not edit",
            "Charlie restores version from yesterday → new tip or branched restore policy",
            "Dana edits on plane offline → reconnect merges without losing work",
        ],
        [
            ("Two inserts at same index", "OT transform or CRDT id order — both retained intentionally"),
            ("User loses WS mid-composition", "Local buffer; resync from last ACK version"),
            ("ACL revoke while editing", "Fence session; force read-only; pending ops rejected"),
            ("100 cursors on one doc", "Coalesce presence; drop fidelity before dropping text ops"),
            ("Doc grows to 10MB text", "Chunked snapshot; lazy load UI; still single logical log or sharded ranges"),
            ("Op log explosion", "Periodic snapshot; truncate acknowledged prefix"),
            ("Split-brain two hubs", "Single sequencer lease per doc; epoch fencing"),
            ("Malformed client op", "Reject; don't advance tip; rate-limit offender"),
            ("Comment anchor deleted text", "Sticky tombstone range; mark orphaned"),
            ("Restore vs concurrent edits", "Restore creates new version from snapshot; concurrent ops transform or branch policy"),
            ("Emoji/UTF-16 index bugs", "Index by CRDT ids or Unicode code points clearly"),
            ("Server deploy mid-session", "Drain connections; clients resume with last_version"),
            ("Hot celebrity doc", "Dedicated hub shard; protect neighboring docs"),
            ("Partial snapshot write", "Object store upload then CAS pointer in metadata"),
        ],
        [
            ("Docs edited/day", "1M", "10M", "100M", "1B"),
            ("Peak concurrent editors/doc", "10", "50", "200", "500+"),
            ("Avg ops/s/active doc", "2", "5", "10", "20"),
            ("Presence msgs/s/hot doc", "20", "200", "2K", "10K"),
            ("Snapshot size p95", "200KB", "1MB", "5MB", "20MB"),
            ("Op log retention hot", "7d", "30d", "90d", "tiered years"),
            ("WS connections global", "1M", "10M", "100M", "500M"),
            ("History restores/day", "10K", "100K", "1M", "10M"),
        ],
        """**10×:** sticky doc hubs, snapshot compaction, presence coalesce.\n
**100×:** doc_id sharding of sync hubs, regional pin, cold history object tier, ACL caching with epoch.\n
**1,000×:** range-sharding huge docs, interest-managed presence, cell isolation for viral docs, CRDT/OT hybrid research carefully justified.""",
        [
            "Clients may be evil/buggy — server validates ops",
            "Rich text schema evolves — versioned op types",
            "Don't build full offline-first mesh without server unless asked",
            "Accessibility & IME composition groups matter for op boundaries",
        ],
        "Google Docs-like realtime editor: durable op log + snapshots, OT or CRDT convergence, WebSocket sync hubs sharded by doc_id, presence coalescing, ACL fences, offline merge, comments/history secondary planes.",
    )
    t += s2(
        [
            ("Active docs & QPS", """
Assume 10M docs edited/day; peak concurrency factor: 1% of DAU docs open
1M simultaneously open docs
Avg 2 text ops/s among active editors distributed → aggregate op ingest:
  If 5% of open docs are actively typing: 50K docs × 2 ops/s = 100K ops/s global
Per-doc sequencer must handle hot doc 20–50 ops/s bursts (paste storms higher)
"""),
            ("Storage: op log + snapshots", """
Avg 500 ops/doc/day × 200 bytes = 100KB/doc/day log
10M docs → 1 PB/day? Calibrate: not all docs equally active
Realistic: 10M × 20KB avg new log/day = 200 TB/day raw before compaction
Snapshots every 1K ops: object store pointers; keep last N snapshots
Compaction reduces hot log to hours–days of ops
"""),
            ("Bandwidth & WebSocket", """
Text op ~100–300B JSON; binary framing smaller
Hot doc 50 editors: 30 ops/s × 200B × 50 fanout ≈ 300 KB/s (manageable)
Presence without coalesce: 50 × 10 updates/s × 100B × 50 = 2.5 MB/s → coalesce!
Global 1M WS × 1 kbps heartbeat ≈ 1 Gbps control plane — shard & regionalize
"""),
            ("Memory: hub process", """
Per doc state: materialization cache 1MB + session table
10K hot docs/hub × 1MB = 10GB → size hubs accordingly
Lease/sequencer metadata small; presence ring buffers bounded
"""),
            ("Cache & hot keys", """
Hot key = celebrity shared doc (all-hands notes)
Cache ACL, snapshot pointer, tip version in memory
Don't cache full presence history; latest cursor map only
"""),
            ("Revision history reads", """
Restore UI lists snapshots; rarely replays entire life log
Provide indexed snapshot timeline; deep archaeology from cold tier
"""),
            ("Comment plane load", """
Comments << text ops; 1–5% of sessions
Index by doc_id; fanout notifications async via queue
"""),
            ("Multi-region RPO math", """
Async replicate WAL to DR region every 1–5s
Pinned primary accepts writes; failover elects new sequencer with fence epoch
"""),
        ],
        """1) **Per-doc sequencer / hub CPU** under paste storms  
2) **Presence fanout** if not coalesced  
3) **Op log growth** without snapshot compaction  
4) **ACL/auth storms** on reconnect after outage  
5) **Large snapshot fetch** for huge docs on cold open""",
    )
    t += s3(
        """Realtime collaborative editing is a **per-document state machine**: clients attach to a sticky sync hub that owns the doc's tip version. Edits are ops appended to a durable log; materialization is a snapshot + replay. Presence is an unreliable best-effort overlay. ACLs gate both subscribe and mutate.""",
        [
            "API Gateway / Edge — TLS, authn, route by doc_id",
            "Sync Hub (sticky) — WebSocket, sequencer, transform/CRDT integrate",
            "Op Log Store — WAL/Kafka/distributed log per shard",
            "Snapshot Store — object storage for compacted states",
            "Doc Metadata DB — ACL, tip pointer, hub lease, title",
            "Presence Service — cursors/selections (coalesced)",
            "Comment Service — threads + anchors",
            "Blob Store — images/attachments",
            "History Service — named versions / restore",
            "Notification Worker — shares, @mentions",
            "AuthZ — session tokens + ACL epoch",
            "Admin/Compliance export",
        ],
        """
WS  /sync/{doc_id}?session=...          # ops + acks + presence multiplex
POST /v1/docs                           # create
GET  /v1/docs/{id}/meta                 # ACL, title, tip_version
POST /v1/docs/{id}/snapshots:restore    # restore
POST /v1/docs/{id}/acl                  # share
POST /v1/docs/{id}/comments             # create thread
POST /v1/blobs                          # upload media → blob_id
GET  /v1/docs/{id}/history              # list versions
""",
        """
DocMeta {doc_id, owner, acl_epoch, tip_version, snapshot_ptr, hub_lease, region}
Op {doc_id, version, op_type, payload, author, ts, session_id}
Snapshot {doc_id, version, object_key, checksum, created_at}
Presence {doc_id, user_id, cursor, selection, ts}  // ephemeral
Comment {comment_id, doc_id, anchor, body, state, created_at}
BlobRef {blob_id, doc_id, object_key, mime}
""",
        [
            ("Concurrency", "OT + server sequencer", "CRDT (no central transform)", "OT if strong central hub OK; CRDT if offline-heavy / P2P-ish"),
            ("Transport", "WebSocket sticky hub", "Poll HTTP", "WS for realtime; poll only fallback"),
            ("History", "Snapshot + log addressable versions", "Full doc copy every save", "Snapshots win at scale"),
            ("Presence", "Separate channel coalesce", "Same as text ops", "Separate — drop under load"),
            ("ACL", "Epoch fence on mutate", "Check only on open", "Epoch — revoke must bite"),
            ("Large doc", "Single log + chunked UI", "Range shards early", "Start single; shard at 100×"),
            ("Media", "Blob refs in ops", "Inline base64 in op log", "Refs only"),
        ],
        [
            ("Last-write-wins whole document", "Lost updates; unacceptable for Docs"),
            ("Global locks per keystroke", "Feels broken; kills concurrency"),
            ("Store doc only in Postgres row UPDATE", "Contention + huge rows + no realtime"),
            ("Fan out every cursor at 60Hz", "Melts hubs"),
            ("Replay full history for every open", "Cold open latency death"),
            ("Ignore IME composition", "Garbled CJK/mobile input"),
        ],
        "Per-doc sticky sequencer + durable op log + snapshots is the backbone; CRDT vs OT is the headline trade-off you must explicitly defend.",
    )
    t += s4(
        """
flowchart TB
  ClientA snync@WebSocket
  ClientB snync@WebSocket
  subgraph Edge
    GW[API Gateway]
  end
  subgraph DocCell
    Hub[Sync Hub / Sequencer]
    Pres[Presence Coalescer]
    Meta[(Doc Meta / ACL)]
    Log[(Op Log)]
    Snap[(Snapshot Objects)]
  end
  Comments[(Comment DB)]
  Blobs[(Blob Store)]
  ClientA --> GW --> Hub
  ClientB --> GW --> Hub
  Hub --> Log
  Hub --> Meta
  Hub --> Snap
  Hub --> Pres
  Hub --> Comments
  ClientA --> Blobs
""",
        [
            ("Edit path sequence", """
1. Client opens doc → fetch ACL + snapshot@V + ops V+1..tip
2. WS connect to hub holding lease for doc_id
3. Local echo apply optimistic op
4. Send op; hub assigns version N; persists WAL; fanouts to peers
5. Clients ACK; transform/CRDT integrate concurrent ops
6. Periodically hub writes snapshot@N; advances snapshot pointer
"""),
            ("Offline reconnect sequence", """
1. Client stores pending ops with local ids
2. On reconnect: fetch tip + ACL epoch
3. If epoch changed → reauthorize; may reject
4. Integrate pending via transform/CRDT against tip
5. Submit; receive final versions; compact local buffer
"""),
            ("ACL revoke fence", """
1. Owner bumps acl_epoch
2. Hub loads new ACL; marks unauthorized sessions fenced
3. In-flight ops from fenced sessions rejected
4. Clients notified → read-only or disconnect
"""),
        ],
    )
    t += s5(
        [
            "Durable WAL before ACK to client (or ack with clear 'uncommitted' UX — prefer quorum durable).",
            "Idempotent client op ids to avoid duplex retries duplicating inserts.",
            "Hub lease with epoch fencing to prevent split-brain dual sequencers.",
            "Snapshot pointer CAS; never publish partial snapshot.",
            "Rate-limit ops/s/session; backpressure via WS window.",
            "Presence droppable; text ops not droppable without user-visible recovery.",
            "Poison op quarantine with version gap repair tooling.",
            "Multi-AZ WAL replication; regional pin with DR runbooks.",
            "Checksum snapshots; verify on load.",
            "Session auth refresh without dropping unacked buffer.",
        ],
        [
            ("1×", "Single region; one hub pool; Postgres meta; object snapshots; Redis presence"),
            ("10×", "Shard hubs by doc_id hash; snapshot compaction workers; presence coalesce; CDN static assets"),
            ("100×", "Doc cells/regions; hot-doc isolation; cold history tier; ACL epoch cache; comment service split"),
            ("1,000×", "Range-shard huge docs; interest management; adaptive sync; per-tenant cells; formal verification of transforms for critical op types"),
        ],
        [
            "Versioned op schema with expand/contract migrations.",
            "Canary hubs on % of doc_id space.",
            "Metrics: integrate lag, transform errors, WS churn, snapshot age, ACL fence rate.",
            "Replay tools for corrupted materialization (rebuild from log).",
            "Feature flags for new op types.",
            "Clear ownership: sync vs comments vs ACL vs compliance.",
        ],
        [
            ("OT vs CRDT deep dive", """
**OT:** central total order; transform peer ops against committed ops; mature in Docs-like systems; hard to get transforms right (TP1); offline requires transformation against gap.

**CRDT:** commutative merge; better offline/multi-primary stories; metadata overhead (IDs/tombstones); GC complexity; UI indices trickier.

**Staff answer:** pick OT+sequencer for Google-Docs-like server authority; mention CRDT if interviewer stresses offline/P2P. Hybrid exists (e.g., CRDT payloads with server ordering for UX).

| Concern | OT | CRDT |
|---------|----|------|
| Server role | Sequencer required | Optional |
| Offline | Harder | Natural |
| Memory | Lower | Tombstones/IDs |
| Implementation risk | Transform bugs | GC / UX indexing |
"""),
            ("Op log, snapshots, compaction", """
Treat the doc as event-sourced. Materialized snapshot every N ops or size threshold. New clients load snapshot + tail. Compaction deletes WAL prefix only after durable snapshot and after slow consumers (history builders) checkpoint. For named versions, retain snapshot refs immutably.
"""),
            ("Presence & cursor fanout", """
Presence is **lossy**. Batch at 100–200ms. Send diffs not full maps. Cap visible cursors (show "and 37 others"). Separate WS channel or message type with lower priority so text ops win under congestion.
"""),
            ("Doc sharding strategies", """
**doc_id sticky hub** handles 99% docs. Huge docs: shard by block/paragraph ranges with a coordination layer for cross-range ops (rare). Viral all-hands: dedicated cell so noisy neighbor doesn't steal CPU from other docs.
"""),
            ("ACL, sharing, offline security", """
Every mutate checks (session → user → role @ acl_epoch). Link sharing uses opaque tokens mapped server-side. Offline edits are provisional until AuthZ passes post-reconnect; never apply fenced ops to tip. Audit log share/revoke.
"""),
            ("Comments, suggestions, revisions", """
Comments: anchor to CRDT positions or sticky bookmarks; separate service. Suggestions: ops tagged `suggest` applied to shadow layer until accept. Revisions: timeline of snapshots + optional semantic named versions; restore spawns new tip from old snapshot (preserve audit).
"""),
        ],
    )
    t += s6(
        "Realtime collaborative document system with per-doc sync hubs, durable op logs, snapshot compaction, OT/CRDT convergence, coalesced presence, ACL epochs, offline merge, comments/history/blob side planes.",
        [
            "Per-doc sticky sequencer / hub lease with fencing",
            "OT vs CRDT explicit choice with trade-offs",
            "Snapshot + WAL rather than whole-doc row updates",
            "Presence lossy & coalesced; text ops reliable",
            "ACL epoch fences for revoke",
            "Offline buffer with reconnect integrate",
            "Hot-doc isolation at scale",
            "Separate comment/history planes",
        ],
        [
            "Transform/CRDT implementation bugs → divergent docs (SEV0)",
            "Split-brain hub dual tips",
            "Presence melting hubs",
            "ACL revoke lag → unauthorized writes",
            "Compaction deleting unsnapshotted WAL",
        ],
        [
            ("0–5", "Scope Docs vs full Workspace; concurrent editors"),
            ("5–15", "Op model + OT/CRDT + sync protocol"),
            ("15–25", "WAL/snapshots/hub sharding"),
            ("25–35", "Presence, ACL, offline, comments"),
            ("35–45", "Scale jumps, failure modes, restore"),
        ],
        "**Google Docs**: sticky per-doc hub, durable ops+snapshots, defend OT/CRDT, coalesce presence, fence ACL, compact logs — convergence and no silent loss.",
    )
    qs = [
        ("OT vs CRDT — which do you pick for Google Docs?", "OT+server sequencer matches Docs' historical approach and server-authoritative ACL/audit. CRDT if offline-first multi-primary is the north star. State transform correctness risk vs tombstone/GC risk."),
        ("How do you prevent split-brain on hubs?", "Distributed lease (etcd/ZK/SQL fencing token). Only lease holder appends versions. On expiry, new leader requires epoch bump; clients reconnect."),
        ("What is intention preservation?", "Concurrent edits should both happen in a way users expect (typing doesn't silently swallow peer inserts). Not the same as linearizability of whole doc."),
        ("How are cursors transformed?", "Map cursor index through concurrent inserts/deletes or store as CRDT position marks. Coalesce sending."),
        ("IME composition?", "Treat composition as atomic commit on confirm; avoid mid-composition transforms that split graphemes."),
        ("How to open a 50MB doc fast?", "Chunked snapshot fetch; virtualized UI; don't replay million ops — must have recent snapshot."),
        ("Where is strong consistency required?", "Version assignment per doc; ACL checks; snapshot pointer. Presence eventually."),
        ("Design share links.", "Opaque token → role mapping; revoke deletes mapping / bumps epoch; optional expiry; password; domain-restricted."),
        ("How does restore work with live editors?", "Publish restore as special op or cut new tip from snapshot with version jump; notify clients to resync hard."),
        ("Offline conflict that can't merge cleanly?", "CRDT almost always merges text; semantic conflicts (accept vs reject suggestion) may need UI. Never drop buffered user text silently."),
        ("Why not Firebase-like LWW fields?", "LWW loses concurrent character inserts. Fine for title field; wrong for body text."),
        ("Binary vs JSON ops?", "Binary smaller/faster; JSON debuggable. Start JSON; move binary under scale."),
        ("Rate limits?", "Per-session ops/s; per-doc aggregate; backoff; paste as chunked ops with size cap."),
        ("Testing convergence?", "Property tests random op schedules; peer fleets; fuzz transformers; snapshot rebuild equals tip."),
        ("Cross-region edit latency?", "Pin primary region near owner/team; cross-region followers read-only or high-lag; avoid multi-writer worldwide for one doc."),
        ("Comments across edits?", "Anchors as positions/marks updated by same sync engine; orphan detection."),
        ("Security of WS?", "Auth token bound to doc; rotate; mute on revoke; don't trust client-authored user_id."),
        ("How to GC CRDT tombstones?", "Track peer checkpoints; GC only below all-replica frontier; snapshots omit GC'd deletes carefully."),
        ("Named versions vs every keystroke history?", "Named/snapshot timeline for UX; fine-grained ops retained for compaction window / legal hold."),
        ("Suggest mode implementation?", "Shadow layer ops; accept converts to main ops; reject discards; still concurrent-safe."),
        ("Media paste race?", "Upload blob first (or upload session); insert ref op; if upload fails show placeholder broken state."),
        ("What metrics for SEV detection?", "Integrate lag, divergence checksum mismatches (sampled), NAK rates, fence rates, hub CPU."),
        ("Checksum divergence repair?", "Rebuild materialization from WAL; compare; force client hard resync; alert."),
        ("Can you shard one doc across hubs?", "Yes at extreme size with range ownership; cross-range transactions rare (join paragraphs); avoid until needed."),
        ("Why sticky sessions?", "Affinity to sequencer state cache; without sticky, every op pays relocation or proxy hop."),
        ("Deal-breaker answer?", "Whole-document LWW or single global lock per keystroke."),
        ("How do mobile flaky networks change design?", "Larger client buffer, idempotent op ids, adaptive batching, resume tokens."),
        ("Export/e-discovery?", "Async render to PDF/DOCX from snapshot; compliance pipeline reads cold archive."),
    ]
    t += s7(qs)
    t += s8(
        [
            ("SLO table", """
| SLO | Target |
|-----|--------|
| Peer op visible p50 (same region) | <300ms |
| Local echo | <50ms |
| Durability of ACKed op | Quorum WAL |
| Divergence incidents | ~0 |
| ACL revoke effectiveness | <5s p99 |
| Cold open to editable (cached snapshot) | <2s p50 |
"""),
            ("Ownership map", """
| Area | Team |
|------|------|
| Sync hub / OT-CRDT | Collab engine |
| WAL/snapshots | Collab storage |
| ACL/sharing | Drive-like policy |
| Presence | Collab UX realtime |
| Comments | Engagement |
| Compliance export | Trust & safety / legal eng |
"""),
            ("Failure drills", """
- Kill hub holder mid-edit; verify lease failover + client resync
- Dual-lease injection (should fence)
- Corrupt snapshot object; fallback to older snapshot+replay
- ACL revoke storm
- Presence amplification attack
"""),
            ("Progressive scale checklist", """
| Jump | Force |
|------|-------|
| 10× | Hub sharding + compaction |
| 100× | Regional pin + cold tier + hot-doc cell |
| 1,000× | Range shards + interest mgmt |
"""),
            ("Interview phrasing cheatsheet", """
"I'll treat each doc as an ordered op log with snapshots. Hubs are sticky by doc_id with leases. Presence is lossy. ACL uses epochs. Offline reconnect integrates then commits."
"""),
        ],
        [
            "Locked concurrent editors + offline + history scope",
            "Chose OT or CRDT with trade-offs table",
            "Drew hub + WAL + snapshot + presence",
            "Explained fanout math and coalesce",
            "Called out split-brain lease fencing",
            "ACL revoke fence",
            "Scale jumps by editors/doc and docs/day",
            "Listed deal-breakers (LWW doc, per-keystroke lock)",
            "22+ deeper Q&A ready",
            "SLOs and failure drills named",
        ],
    )
    return _ensure_min(t, 750, _PADS_GDOCS)


# =============================================================================
# 2) Uber / Lyft ride matching
# =============================================================================

_PADS_UBER = [
    """### Extra: H3 dispatch cells

```text
H3 res 8 ≈ 0.74 km²; res 9 ≈ 0.1 km²
Core city: res9 k-ring; suburbs res8
Driver geo index: driver_id → cell on each significant move
Match: rider cell → candidates in k-ring → rank ETA/score
```""",
    """### Extra: Trip state machine

```text
REQUESTED → MATCHED → DRIVER_ARRIVING → IN_TRIP → COMPLETED
         ↘ CANCELED_* / EXPIRED / NO_DRIVERS
Authorize payment on match/start; capture on complete
Illegal transitions rejected with idempotent transition_id
```""",
    """### Extra: Location stream budget

```text
1M online drivers × 1Hz = 1M/s — too hot
Use 0.2–0.5Hz moving, slower idle, or distance threshold
Kafka partition by city/geohash; drop stale GPS by ts
```""",
    """### Extra: Surge / pricing signals

```text
Demand = open requests / cell / window
Supply = eligible drivers / cell
Surge multiplier from ratio + ML; smooth to avoid flicker
Show rider quote before confirm; lock quote TTL
```""",
    """### Extra: Dispatch fairness

```text
Avoid always nearest if it starves distant drivers
Balance: ETA, acceptance prob, idle time, cancellation risk
Batch matching windows (1–2s) improve global assignment vs greedy
```""",
]


def doc_uber() -> str:
    t = header(
        "Uber / Lyft Ride Matching",
        "Location stream · Geo index (H3/S2) · Matching/dispatch · ETA · Surge · Trip state machine · Payments hook · Supply/demand",
        "marketplace matching for rides under extreme location QPS",
    )
    t += s1(
        "design an **Uber/Lyft-like** ride-hailing system: riders request trips, drivers share location, matching assigns drivers, trip lifecycle through completion/payment, with surge and ETAs.",
        [
            ("Job", "Two-sided marketplace: match riders↔drivers", "Full autonomous vehicle OS"),
            ("Realtime", "Location + dispatch in seconds", "Long-haul freight logistics"),
            ("Lens", "Geo index, matching, trip FSM, fairness", "Mobile app UI polish only"),
            ("Payments", "Authorize/capture hooks", "Full bank ledger core"),
            ("Scale unit", "Concurrent trips + location updates/s", "Static taxi medallion DB"),
        ],
        [
            ("Who are actors?", "Riders, drivers, dispatch, payments, safety", "Separate apps + shared backend"),
            ("Match latency SLO?", "p50 <3–5s city; show searching UX", "Matching service + geo index"),
            ("Location frequency?", "Sub-second to few seconds; adaptive", "Ingest pipeline + downsampling"),
            ("ETA?", "Pickup + trip ETA from maps/traffic", "Routing service dependency"),
            ("Surge?", "Yes — supply/demand multiplier", "Pricing service + cell signals"),
            ("Trip states?", "Requested→matched→arriving→in_trip→done", "Hard FSM + idempotent transitions"),
            ("Cancellations?", "Rider/driver cancel with fees policy", "State + payments adjustments"),
            ("Payments?", "Pre-auth on match/start; capture end", "Async payment worker; never block GPS"),
            ("Multi-city?", "City/region cells; config per market", "Shard by city_id"),
            ("Pool/shared rides?", "Optional out of MVP or stub", "More complex matching"),
            ("Driver acceptance?", "Offer with timeout; re-match", "Offer service + fallback"),
            ("Fraud/safety?", "Basic GPS sanity; SOS hook", "Risk service async"),
            ("History/receipts?", "Trip history durable", "OLTP + analytics events"),
            ("Offline maps?", "Client concern; server needs routing", "Degrade gracefully if maps slow"),
        ],
        [
            "Rider requests ride with pickup/dropoff",
            "Quote + ETA + surge shown; confirm",
            "Dispatch finds candidates; offers to driver",
            "Driver accepts → trip MATCHED; navigate",
            "Location streaming both sides",
            "Start trip / complete trip; payment capture",
            "Cancel paths with policy",
            "Driver online/offline + availability",
            "Basic surge by geo cell",
        ],
        [
            "Food delivery / scooters full product",
            "Intercity buses",
            "Perfect global active-active matching day one",
            "Fully custom routing graph build (use Maps API OK)",
        ],
        [
            ("Match latency", "p50 <5s; p99 <15s in healthy markets", "Batch window vs greedy trade-off"),
            ("Location ingest", "p99 process <200ms to index", "Drop stale; never block dispatch on slow maps"),
            ("Availability", "99.9% request API; degrade matching regionally", "City cell isolation"),
            ("Durability", "Trip records & payment intents durable", "Location can be sampled/lossy"),
            ("Consistency", "Trip FSM strong; location eventual", "Exactly-once payment effects via idempotency"),
            ("Multi-region", "City pinned; failover playbooks", "Don't dual-match across regions"),
            ("Security", "PII for location; authz trip participants only", "Anti-spoof basics"),
            ("Cost", "Location stream + maps API dominate", "Downsample intelligently"),
        ],
        [
            "Rider requests → matched in seconds → pickup → trip → pay",
            "No drivers → expand radius / wait / fail gracefully",
            "Driver rejects offers → next candidate",
            "Surge hour: quote elevated; still matches",
            "Rider cancels after match → notify driver; fee rules",
        ],
        [
            ("GPS teleport / spoof", "Sanity filters; reject impossible speed; risk score"),
            ("Double match two riders one driver", "Driver lock / offer exclusivity lease"),
            ("Payment auth fails", "Don't start trip; or fail closed per policy"),
            ("Maps ETA timeout", "Cached ETA fallback; match with degraded score"),
            ("City outage", "Isolate blast; neighboring cities unaffected"),
            ("Thundering herd after outage", "Jitter reconnect; re-request matching carefully"),
            ("Driver app killed mid-trip", "Last known location; rider notified; support path"),
            ("Surge flicker", "Temporal smoothing; quote lock TTL"),
            ("Hot stadium exit", "Demand spike; expand supply radius; queue UX"),
            ("Clock skew on GPS ts", "Server receive time + client ts sanity"),
            ("Idempotent re-request", "Idempotency-Key creates one trip request"),
            ("Driver accepts two offers race", "CAS on driver state AVAILABLE→OFFERED→ON_TRIP"),
            ("Partial payment capture fail", "Retry worker; trip still COMPLETED with pay state"),
            ("Privacy: stalk via location", "Strict authz; short-lived location retention for non-trip"),
        ],
        [
            ("Concurrent trips", "50K", "500K", "5M", "20M"),
            ("Online drivers", "100K", "1M", "5M", "20M"),
            ("Location updates/s", "50K", "500K", "5M", "20M+"),
            ("Ride requests/s peak", "1K", "10K", "100K", "500K"),
            ("Match p50", "3s", "3s", "4s", "5s (harder)"),
            ("Cities", "50", "200", "500", "1000+"),
            ("Geo index ops/s", "50K", "500K", "5M", "20M"),
            ("Payment intents/day", "5M", "50M", "200M", "500M"),
        ],
        """**10×:** shard by city; Kafka location pipeline; H3 index; offer timeouts.\\n
**100×:** batch matching; cell-based surge; hot-venue playbooks; multi-region city pins.\\n
**1,000×:** marketplace optimization (global assignment), ML acceptance prediction, extreme stream downsampling, cell isolation.""",
        [
            "Maps/routing is a dependency — design timeouts/fallbacks",
            "Safety & PII are first-class",
            "Marketplace health metrics > raw request QPS",
        ],
        "Uber/Lyft-like matching: adaptive location stream, H3/S2 geo index, dispatch with exclusive offers, trip FSM, surge cells, payment hooks — scaled by concurrent trips and location updates/sec.",
    )
    t += s2(
        [
            ("Location QPS", """
1M online drivers × 0.5 Hz average = 500K updates/s
Payload ~100–200B → ~50–100 MB/s ingest before fanout
Partition by city_id / geohash; consumers update geo index
Idle drivers: 0.05–0.1 Hz; moving: 1 Hz capped
"""),
            ("Matching QPS", """
Peak 10K requests/s globally uneven by city
Each request: geo query k-ring + rank top N + offer
Budget: matching compute << 100ms excluding maps
Batch windows 1s can cut offer spam and improve allocation
"""),
            ("Geo index memory", """
1M drivers × 64B index entry ≈ 64MB — small
But city hotspots need fast structures (in-mem per city cell)
Hex cells with driver sets; update on cell change only
"""),
            ("ETA / maps bandwidth", """
Don't call external maps on every GPS tick
Cache route segments; refresh on deviation
Pickup ETA updates throttled to 2–5s to clients
"""),
            ("Trip storage", """
50M trips/day × 2KB record = 100 TB/day raw? Calibrate:
5M trips/day × 5KB = 25 TB/day with events — use event store + compact records
Location breadcrumbs sampled separately with TTL
"""),
            ("Hot venue math", """
Stadium: 20K requests in 10 min ≈ 33/s local — small globally, huge locally
Local supply short → surge + widen radius + waitlist
Protect city matching workers with venue-specific queues
"""),
            ("Surge signal compute", """
Per cell every 10–30s: demand/supply features
Write multiplier to cell config table cached in matching
"""),
            ("Payment path", """
Authorize ~ trip start QPS; capture ~ complete QPS
Idempotency keys; async retries; never on location path
"""),
        ],
        """1) **Location ingest + geo index updates**  
2) **City-hotspot matching contention**  
3) **Maps/ETA dependency latency**  
4) **Offer/accept races**  
5) **Payment retries vs trip truth**""",
    )
    t += s3(
        """Two-sided realtime marketplace. **Location plane** (lossy, high QPS) feeds a **geo index**. **Matching plane** turns requests into exclusive driver offers. **Trip plane** is a strongly consistent FSM. **Pricing** reads supply/demand cells. **Payments** are async side effects with idempotency.""",
        [
            "Rider/Driver API Gateway",
            "Trip Service (FSM)",
            "Matching / Dispatch Service",
            "Offer Service (timeouts, exclusivity)",
            "Location Ingest (Kafka)",
            "Geo Index (H3/S2)",
            "ETA / Routing Adapter",
            "Pricing / Surge Service",
            "Payments Worker",
            "Notification / Push",
            "Risk / Fraud hooks",
            "Analytics Event Bus",
            "City Config Service",
        ],
        """
POST /v1/trips {pickup, dropoff, product} → trip_id REQUESTED, quote
POST /v1/trips/{id}/cancel
POST /v1/driver/status {online, location?}
POST /v1/driver/offers/{id}/accept|reject
WS   /v1/location/stream  (driver/rider during trip)
GET  /v1/trips/{id}
POST /v1/trips/{id}/transitions {to, ts, idem_key}
""",
        """
Trip {trip_id, rider_id, driver_id?, state, pickup, dropoff, quote, surge, city_id, timestamps}
Driver {driver_id, state, cell_id, last_loc, capacity}
Offer {offer_id, trip_id, driver_id, expires_at, status}
GeoCellStats {cell_id, demand, supply, surge, window}
PaymentIntent {trip_id, auth_id, capture_status, idem_key}
LocationEvent {actor_id, lat, lng, ts, trip_id?}  // hot, TTL
""",
        [
            ("Matching", "Greedy nearest driver", "Batch global assignment", "Greedy MVP; batch at 10–100×"),
            ("Geo index", "H3 cells + k-ring", "R-tree only", "H3/S2 for update-heavy"),
            ("Offers", "Exclusive lease to one driver", "Broadcast to many", "Exclusive reduces double accept"),
            ("Location", "Kafka + downsample", "Sync DB write per ping", "Stream — DB would melt"),
            ("Surge", "Cell ratio + smoothing", "Fixed city multiplier", "Cell-level"),
            ("Consistency", "FSM strong; GPS eventual", "Everything strong", "Mixed consistency"),
            ("Shard key", "city_id then trip_id", "Global trips table", "City first"),
        ],
        [
            ("Sync write every GPS to SQL primary", "Death by QPS"),
            ("No driver exclusivity", "Double booking SEV"),
            ("Match without city isolation", "Noisy neighbor / blast radius"),
            ("Block matching on payment capture", "Wrong dependency direction"),
            ("Unbounded match radius", "Terrible ETA; driver reject spiral"),
        ],
        "Separate lossy location plane from strong trip FSM; exclusive offers; city sharding; H3 candidates + rank.",
    )
    t += s4(
        """
flowchart LR
  RiderApp --> API
  DriverApp --> API
  DriverApp -->|GPS| LocIngest[Location Kafka]
  LocIngest --> GeoIndex[(H3 Geo Index)]
  API --> TripSvc[Trip FSM]
  TripSvc --> Match[Matching]
  Match --> GeoIndex
  Match --> Offer[Offer Service]
  Offer --> DriverApp
  Match --> ETA[Routing/ETA]
  TripSvc --> Price[Pricing/Surge]
  TripSvc --> Pay[Payments]
  TripSvc --> Push[Push/WS]
""",
        [
            ("Happy match sequence", """
1. Rider POST trip → quote (ETA+surge) → confirm REQUESTED
2. Matcher queries H3 k-ring; ranks candidates
3. Create exclusive offer to driver A (TTL 15s)
4. Driver accepts → CAS driver ON_TRIP; trip MATCHED
5. Stream locations; update ETAs throttled
6. Start IN_TRIP → complete → payment capture
"""),
            ("No-accept re-match", """
1. Offer expires / reject
2. Release driver lock if any
3. Re-enter matching with next candidates / widen radius
4. Eventually NO_DRIVERS or keep searching per product policy
"""),
            ("Stadium spike", """
1. Cell demand spikes; surge rises (smoothed)
2. Matching workers consume venue queue
3. Widen radius; prioritize high acceptance drivers
4. UX: longer search; transparency on wait
"""),
        ],
    )
    t += s5(
        [
            "Trip transitions idempotent with transition_id / CAS on state.",
            "Driver offer exclusivity lease prevents double match.",
            "Payment intents idempotent; retries safe.",
            "Location events lossy OK; trip money events not lossy.",
            "Timeouts on maps; degraded ETA.",
            "Rate-limit requests per rider; anti-spoof GPS.",
            "City cell isolation for failures.",
            "Backpressure: drop/downsample location before dropping trip writes.",
            "Replay-safe Kafka consumers for geo index (driver last-loc wins by ts).",
            "Outbox for push notifications from trip transitions.",
        ],
        [
            ("1×", "Single region; Redis geo; monolith trip+match; Stripe-like payments"),
            ("10×", "Kafka locations; H3; city shards; offer service; surge cells"),
            ("100×", "Batch matching; ML accept-prob; multi-region city pins; hot-venue queues"),
            ("1,000×", "Global optimization matching; sophisticated fraud; extreme stream economy; marketplace sims"),
        ],
        [
            "FSM as explicit state machine table — reviewable.",
            "City config as data (radii, timeouts, products).",
            "Dashboards: match rate, cancel rate, ETA error, surge, driver util.",
            "Shadow matching experiments.",
            "Chaos: kill geo index replica; maps latency injection.",
            "Clear on-call ownership per plane (loc vs trip vs pay).",
        ],
        [
            ("Geo indexing (H3/S2)", """
Drivers indexed by cell; updates only on cell change or heartbeat. Query k-ring from pickup. Tune resolution by density. S2 similarly fine — pick one and be consistent. Avoid haversine over millions of drivers globally; always constrain by cell first.
"""),
            ("Matching & fairness", """
Score = f(ETA, acceptance_prob, idle_fairness, cancel_risk, product constraints). Greedy nearest is biased. Batch matching (Hungarian/min-cost flow approximations) improves marketplace KPIs at cost of +0.5–2s latency. Exclusive offers trade utilization for correctness.
"""),
            ("Trip FSM & payments", """
Illegal transitions rejected. Payment authorize early enough to reduce joyride risk; capture on complete; refunds/cancel fees async. Trip truth ≠ payment truth — expose both states. Idempotency keys everywhere money moves.
"""),
            ("Surge & quote locking", """
Cell supply/demand → multiplier with hysteresis. Quote locked for TTL on confirm. Explainability to riders matters for trust. Caps and government rules per city config.
"""),
            ("Supply/demand observability", """
Marketplace is the product: open requests, online drivers, match rate, time-to-match, cancels after match, idle distribution. Use these in autotune radii and incentives (out of MVP but mention).
"""),
            ("Progressive scale narrative", """
**1×:** Redis GEO + simple nearest.  
**10×:** H3 + Kafka + city shards.  
**100×:** batch match + surge cells + venue modes.  
**1,000×:** optimization + ML + global ops excellence.
"""),
        ],
    )
    t += s6(
        "Ride-hailing marketplace with adaptive location streaming, H3 geo index, dispatch/offers, trip FSM, surge pricing cells, and idempotent payments — scaled via city isolation.",
        [
            "Location plane lossy/high-QPS vs trip plane strong",
            "H3/S2 candidate generation",
            "Exclusive driver offers with TTL",
            "City-first sharding",
            "Surge as cell signal with quote TTL",
            "Payment idempotency off critical GPS path",
            "Degraded ETA fallbacks",
            "Hot-venue playbooks",
        ],
        [
            "Double dispatch",
            "Maps outage cascading to no matches",
            "Location pipeline lag → bad ETA/match",
            "Surge UX backlash / oscillation",
            "Payment/trip state divergence unresolved",
        ],
        [
            ("0–5", "Scope marketplace MVP; city assumptions"),
            ("5–15", "Location + geo index"),
            ("15–25", "Matching + offers + FSM"),
            ("25–35", "Surge, payments, failures"),
            ("35–45", "Scale jumps + stadium scenario"),
        ],
        "**Uber/Lyft**: stream locations, index geo, exclusive match, strong trip FSM, async pay — defend marketplace metrics and city isolation.",
    )
    t += s7([
        ("Redis GEO vs H3 sets?", "Redis GEO is great early; H3 cell sets scale clearer for custom ranking, surge, and multi-attribute filters. Many systems start Redis GEO then move."),
        ("How to avoid double matching?", "Offer lease + CAS driver state; only one trip_id bound; competing accepts lose."),
        ("Batch vs greedy matching?", "Greedy simpler/lower latency; batch improves fairness/utilization; use when marketplace KPIs justify +latency."),
        ("What if driver never sends GPS?", "Heartbeat timeout → mark unhealthy; re-match if pre-trip; in-trip trigger safety/support."),
        ("Surge oscillation?", "EMA/hysteresis; min dwell; max step change; lock quote."),
        ("Where is exactly-once needed?", "Payment side effects and trip terminal transitions — via idempotency keys, not magic Kafka."),
        ("How to shard?", "city_id primary; within city by trip_id/driver_id. Matching workers affinity per city."),
        ("ETA wrong constantly?", "Feedback loop from actuals; traffic models; don't over-call remote maps."),
        ("Rider spam requests?", "Idempotency + rate limits + cancel reputation."),
        ("Driver reject storms?", "Score acceptance_prob; reduce spam offers; incentives elsewhere."),
        ("Multi-hop airport queues?", "Special geo zones / queue modes in city config — mention as extension."),
        ("Data retention for location?", "Minutes–hours for free drivers; trip breadcrumbs policy-bound; privacy delete."),
        ("Consistency of surge read?", "Slightly stale OK; cache 5–10s; correctness of money uses locked quote."),
        ("Failover a city cell?", "Active-passive matching for city; prevent dual-active dispatch with lease."),
        ("How to test matching?", "Simulator with recorded supply/demand; metrics vs offline oracle."),
        ("Pool rides?", "Different optimization; delay match aggregation; out of MVP."),
        ("Push vs WS for offers?", "Push for accept UX; WS for in-trip location; both need ack."),
        ("Clock skew?", "Server timestamps for FSM; GPS ts used relative."),
        ("Fraud GPS apps?", "Impossible speed, mock location signals, device attestation — risk service."),
        ("Payment capture retry storm?", "Exponential backoff; poison queue; reconcile job."),
        ("Why not match globally in one queue?", "Latency, noisy neighbor, regulatory/city config — city cells."),
        ("Hot key driver?", "Popular driver isn't a hot key; hot key is stadium cell stats / popular airport."),
        ("Idempotent trip create?", "Idempotency-Key header → same trip_id."),
        ("Cancel after driver arriving?", "FSM allows; fee policy; notify; driver state reset."),
        ("Maps dependency deal-breaker?", "Hard-failing match on maps = outage amplifier; must degrade."),
        ("What KPIs to quote?", "Time-to-match, match rate, cancel rate, ETA error, utilization."),
        ("Offline driver mode?", "Online flag; no offers when offline; flush last location."),
        ("Schema for breadcrumbs?", "Object/columnar cold store; not OLTP rows per ping."),
    ])
    t += s8(
        [
            ("SLO table", """
| SLO | Target |
|-----|--------|
| Time-to-match p50 | <5s |
| Location→index p99 | <200ms |
| Double-match rate | ~0 |
| Trip FSM conflict errors | explained, not silent |
| Payment finalization | <few min p99 with retries |
"""),
            ("Ownership", """
| Plane | Owner |
|-------|-------|
| Location/geo | Mobility realtime |
| Matching | Marketplace |
| Trip FSM | Trip lifecycle |
| Pricing | Pricing/marketplace |
| Payments | Payments |
"""),
            ("Failure drills", """
- Dual active matchers in one city (should not double dispatch)
- Maps 2s latency injection
- Kafka lag spike on location topic
- Payment provider 500 storm
- Stadium load test
"""),
            ("Scale jump table", """
| Jump | Architecture force |
|------|--------------------|
| 10× | Kafka+H3+city shard |
| 100× | Batch match+venue queues |
| 1,000× | Optimization+ML+stream economy |
"""),
        ],
        [
            "Separated location vs trip planes",
            "H3/S2 candidate gen explained",
            "Exclusive offers / double-match prevention",
            "Trip FSM + payment idempotency",
            "Surge cell math",
            "Stadium / hotspot scenario",
            "City isolation",
            "22+ Q&A",
            "Deal-breakers named",
            "SLOs for match and double-dispatch",
        ],
    )
    return _ensure_min(t, 750, _PADS_UBER)


# =============================================================================
# 3) Ticketmaster ticket sales
# =============================================================================

_PADS_TM = [
    """### Extra: Seat hold lease

```text
POST hold(seat_ids) → hold_id, expires_at=now+120s
Seat AVAILABLE → HELD(hold_id) via CAS
Checkout presents hold_id; CAS to SOLD if hold valid & unpaid
TTL / expire worker releases HELD → AVAILABLE
```""",
    """### Extra: Waiting room admit math

```text
500K want entry; checkout capacity 5K concurrent
Admit rate ≈ capacity / avg_checkout_seconds
Signed queue tokens; stable order or lottery
Bots: attestation, rate limit, purchase velocity, device farm signals
```""",
    """### Extra: Inventory shard key

```text
Shard by event_id (and section for mega events)
Single-threaded seat allocator per section OR conditional UPDATE
Never claim seats with read-modify-write sans version
```""",
    """### Extra: Flash sale timeline

```text
T-10m: warm caches, preload seat maps, scale holds service
T-0: waiting room → admit → browse/hold → checkout
Payments async confirm; inventory commits before capture OR two-phase with clear compensation
```""",
]


def doc_ticketmaster() -> str:
    t = header(
        "Ticketmaster Ticket Sales",
        "Inventory · Seat maps · Holds/reservations · Checkout · Flash sales · Waiting room · Fraud · Idempotent purchase · Oversell prevention",
        "high-contention inventory under onsale stampedes",
    )
    t += s1(
        "design a **Ticketmaster-like** ticketing system: events with seat maps, fair-ish onsale under huge bursts, temporary holds, checkout/payment, and hard oversell prevention.",
        [
            ("Job", "Sell scarce seats without oversell", "Full venue ops / box office hardware"),
            ("Contention", "Flash onsale stampedes", "Slow evergreen catalog only"),
            ("Lens", "Holds, queues, idempotency, fraud", "Concert recommendation social network"),
            ("Money", "Checkout + refunds hooks", "Issuer bank core"),
            ("Scale unit", "Onsale QPS + hold contention per event", "Average daily browsing"),
        ],
        [
            ("Seated vs GA?", "Both; seats have maps; GA has qty counters", "Different inventory primitives"),
            ("Hold time?", "1–5 minutes typical", "Lease/TTL on inventory"),
            ("Waiting room?", "Yes for mega onsales", "Admit tokens + rate"),
            ("Payments?", "Card authorize then purchase finalize", "Idempotent order service"),
            ("Oversell?", "Never for seats; GA atomic decrement", "CAS/conditional writes"),
            ("Transfers/resale?", "Out of MVP or stub", "Mention secondary market later"),
            ("Fraud?", "Bot mitigation + velocity + payment risk", "Waiting room + device signals"),
            ("Notifications?", "Order email/SMS async", "Not on commit path"),
            ("Multi-event?", "Yes; shard by event_id", "Isolate hot events"),
            ("Partial carts?", "Multiple seats one hold/cart", "Cart object + seat set"),
            ("Price types?", "Standard/VIP; fees shown", "Price rules engine light"),
            ("Accessibility seats?", "Rules for qualified buyers", "Constrained inventory pools"),
            ("Refunds/cancels?", "Policy + release inventory", "Compensation workflows"),
            ("Mobile apps?", "Same APIs; harsher networks", "Idempotency keys"),
        ],
        [
            "Browse event + seat map",
            "Enter waiting room on hot onsale",
            "Hold seats with TTL",
            "Checkout with Idempotency-Key",
            "Payment auth → confirm SOLD",
            "Order/tickets issued",
            "Hold expiry releases seats",
            "Basic bot/rate limits",
            "GA quantity inventory",
        ],
        [
            "Full Fan-to-Fan resale marketplace",
            "Dynamic pricing ML day one",
            "Printer/box-office offline sync",
            "Global active-active writes for same seat",
        ],
        [
            ("Onsale availability", "Survive 100× browse/hold spikes", "Queue + shed + scale out"),
            ("Hold correctness", "No double-hold same seat", "CAS / single allocator"),
            ("Purchase durability", "Confirmed order never loses tickets", "Transactional outbox"),
            ("Latency browse", "Seat map p50 <300ms cached", "Edge cache map tiles/layout"),
            ("Consistency", "Strong for seat state transitions", "Search index eventual"),
            ("Multi-region", "Event home region for inventory writes", "DR runbooks"),
            ("Security/fraud", "Bot resistance; payment 3DS hooks", "Waiting room + WAF"),
            ("Cost", "Burst capacity + CDN for maps", "Autoscale holds/checkout"),
        ],
        [
            "User passes queue → selects seats → hold → pay → tickets",
            "Hold expires mid-checkout → graceful fail; pick again",
            "GA festival: decrement qty atomically",
            "Payment fails → release hold / never SOLD",
            "Onsalle stampede: waiting room paces admits",
        ],
        [
            ("Two users hold same seat", "One CAS wins; other error"),
            ("Double-click pay", "Idempotency-Key returns same order"),
            ("Hold expires after auth before capture", "Explicit compensation; no SOLD without valid hold"),
            ("Bot farm enters queue", "Attestation/rate limits/lottery + purchase caps"),
            ("Inventory service blip", "Fails closed (no sell) not oversell"),
            ("Seat map cache stale", "Versioned map; holds always hit source of truth"),
            ("Refund after scan-in", "Policy engine; state TICKET_USED"),
            ("Clock skew TTL", "Server expiry timestamps only"),
            ("Hot section contention", "Section shard / lock striping"),
            ("Partial seat set unavailable", "Atomic multi-seat hold all-or-nothing"),
            ("Queue token replay", "One-time admit; bind to session"),
            ("Flash sale premature leak", "Feature flag + signed go-live time"),
            ("Payment provider timeout", "Unknown outcome → reconcile; inventory reserved carefully"),
            ("Celebrity event 10M users", "Waiting room + regional edge; inventory still single-home"),
        ],
        [
            ("Peak onsale QPS (browse)", "50K", "500K", "5M", "20M"),
            ("Hold attempts/s", "5K", "50K", "500K", "2M"),
            ("Checkout starts/s", "1K", "10K", "50K", "200K"),
            ("Concurrent waits in room", "100K", "1M", "5M", "20M"),
            ("Seats/event", "20K", "50K", "100K", "100K+"),
            ("Events onsale simultaneous", "10", "100", "500", "2K"),
            ("Order finalizations/s", "500", "5K", "20K", "50K"),
            ("Fraud checks/s", "1K", "10K", "50K", "200K"),
        ],
        """**10×:** waiting room; event_id sharding; seat CAS; cache seat maps.\\n
**100×:** section striping; dedicated hot-event cells; payment reconcile; bot pipeline.\\n
**1,000×:** global edge queue; allocator specialist services; extreme fraud ML; secondary market hooks.""",
        [
            "Fail closed on inventory ambiguity",
            "Idempotency is non-negotiable for pay",
            "Fairness vs throughput trade-off in waiting room — say it aloud",
        ],
        "Ticketmaster-like sales: strong seat inventory with TTL holds, waiting room for onsales, idempotent checkout, fraud controls — never oversell under stampede.",
    )
    t += s2(
        [
            ("Onsale browse bandwidth", """
5M QPS seat map tile/API would melt origin
CDN cache immutable layout; user-specific availability via lightweight polls
Availability polling 1–2s coalesced; or WS section updates for admitted users only
"""),
            ("Hold contention math", """
20K seats; 200K users admitted; hold attempts concentrated on front rows
Per-seat CAS: most fail fast — CPU OK if no global lock
Multi-seat cart: risk of deadlock if lock order inconsistent → ordered seat_id locking
"""),
            ("Waiting room size", """
5M users × 200B token state ≈ 1GB — manageable in Redis cluster
Admit 5K/s; ticket issuance for queue position updates can be sampled
"""),
            ("Checkout + payment", """
10K checkout/s → payment provider limits become bottleneck
Need queueing/retry; don't hold seats longer than policy if pay slow
"""),
            ("Storage", """
Seat rows: event_id, seat_id, state, hold_id, order_id, version
20K seats × 100B × 100K events = 200GB — fine in SQL sharded by event
Orders + tickets larger over years → archive
"""),
            ("Hot key event", """
Single event_id is THE hot partition — isolate on dedicated DB/primary
Neighbor events shouldn't share fate
"""),
            ("Fraud CPU", """
Device score + velocity on each admit/hold/checkout
Cache scores; async enrichment for borderline
"""),
            ("GA counter", """
Atomic DECR IF qty>0; or Redis string with Lua; journal to SQL for durability
"""),
        ],
        """1) **Seat allocator contention on hot sections**  
2) **Waiting room / edge admit**  
3) **Payment provider throughput**  
4) **Cache stampede on seat maps**  
5) **Fail-open bugs that oversell**""",
    )
    t += s3(
        """Ticketing is **scarce inventory with leases**. Browse is cache-heavy; **holds** are strongly consistent leases; **checkout** converts hold→sold with payment and idempotency. Mega onsales add a **waiting room** that paces admits to what inventory/checkout can handle.""",
        [
            "Edge/CDN + Waiting Room",
            "Event Catalog Service",
            "Seat Map Service (layout cached)",
            "Inventory / Hold Service (strong)",
            "Cart / Checkout Service",
            "Order Service",
            "Payment Adapter + Reconcile",
            "Ticket Issuance",
            "Fraud / Bot Mitigation",
            "Notification Workers",
            "Admin Pricing/Allocation tools",
        ],
        """
GET  /v1/events/{id}/seatmap
POST /v1/queue/entry {event_id} → token/position
POST /v1/holds {event_id, seats[]} → hold_id, exp
POST /v1/checkout {hold_id, buyer, Idempotency-Key}
GET  /v1/orders/{id}
POST /v1/holds/{id}/release
""",
        """
Event {event_id, venue_id, onsale_at, home_region, status}
Seat {event_id, seat_id, section, row, state, hold_id, version}
Hold {hold_id, event_id, seats[], user_id, exp, status}
Order {order_id, hold_id, user_id, payment_status, total, idem_key}
Ticket {ticket_id, order_id, seat_id, barcode, state}
QueueToken {token, event_id, user_hash, rank, exp}
""",
        [
            ("Inventory", "Conditional CAS / row version", "Global mutex per event", "CAS/striping — mutex won't scale"),
            ("Queue", "Waiting room + admit rate", "Let everyone hit holds", "Room protects inventory"),
            ("Hold", "TTL lease", "Soft cart without lock", "Soft cart oversells"),
            ("Pay vs inventory", "Reserve then pay then commit", "Pay then hope seat free", "Reserve first"),
            ("Shard", "event_id home", "Random seats globally", "Event home region"),
            ("GA", "Atomic counter", "Count rows sold scan", "Counter"),
            ("Idempotency", "Keyed orders", "Best-effort", "Required"),
        ],
        [
            ("Fail open when inventory uncertain", "Oversell SEV0 brand damage"),
            ("Long holds (hours) at onsale", "Dead inventory; bot camping"),
            ("No idempotency on checkout", "Double charge / double issue"),
            ("Single global Redis for all events without isolation", "Hot key melts everyone"),
            ("Client-trusted seat availability", "Race lies"),
        ],
        "Strong holds with short TTL + waiting room pacing + idempotent checkout is the spine; oversell prevention is the deal-breaker metric.",
    )
    t += s4(
        """
flowchart TB
  User --> Edge[CDN / Waiting Room]
  Edge -->|admitted| API
  API --> Map[Seat Map Cache]
  API --> Inv[Inventory Holds]
  API --> Checkout
  Checkout --> Pay[Payments]
  Checkout --> Orders[(Orders)]
  Inv --> Seats[(Seat State DB)]
  Orders --> Tickets[Ticket Issue]
  Checkout --> Fraud
""",
        [
            ("Hold + purchase sequence", """
1. Admitted user selects seats
2. Hold service CAS seats AVAILABLE→HELD; set Redis/DB TTL
3. Checkout starts with Idempotency-Key
4. Re-validate hold; create order PAYMENT_PENDING
5. Authorize payment
6. CAS seats HELD→SOLD bound to order_id
7. Issue tickets; email async
"""),
            ("Expiry sequence", """
1. TTL fires / worker scans expired holds
2. If still HELD and no committing checkout → AVAILABLE
3. Inflight checkout must re-check and fail if lost hold
"""),
            ("Stampede sequence", """
1. Pre-onsale: users in waiting room
2. Onsale: admit tokens drip
3. Only admitted sessions may hold
4. Shedding returns 'retry' not 500 storms
"""),
        ],
    )
    t += s5(
        [
            "Seat transitions via CAS/version only.",
            "Idempotent checkout keyed by Idempotency-Key.",
            "Fail closed: if seat state unknown, do not sell.",
            "Hold TTL server-side; extend only with strict limits.",
            "Payment reconcile for unknown auth outcomes.",
            "Queue tokens signed and single-use admit.",
            "Rate limits per user/device/session.",
            "Hot-event isolation (dedicated inventory primary).",
            "Outbox for ticket issuance side effects.",
            "Audit log all seat transitions for disputes.",
        ],
        [
            ("1×", "Postgres seats+orders; Redis holds TTL; Stripe; basic rate limit"),
            ("10×", "Waiting room; CDN maps; event shard; idempotency store"),
            ("100×", "Section striping; hot-event cells; fraud platform; payment reconcile fleet"),
            ("1,000×", "Global edge queues; specialized allocators; resale integration; regulatory cells"),
        ],
        [
            "Explicit seat state machine diagram in runbooks.",
            "Load test every major onsale pattern.",
            "Feature flags for onsale go-live.",
            "Metrics: oversell=0, hold conflict rate, checkout success, queue wait.",
            "Canary allocator logic on small events first.",
            "Clear SEV definition for oversell.",
        ],
        [
            ("Holds & oversell prevention", """
All-or-nothing multi-seat holds with ordered locking or single transaction. States: AVAILABLE → HELD → SOLD (or HELD → AVAILABLE). Never SOLD without payment policy satisfied. Use version column: `UPDATE seats SET state=HELD, hold_id=?, version=version+1 WHERE seat_id IN (...) AND state=AVAILABLE AND version IN (...)`.
"""),
            ("Waiting room & fairness", """
Fairness options: FIFO arrival, lottery, loyalty tiers — product choice. Engineering: stable tokens, transparent position, admit matched to measured checkout capacity. Bypass lanes for ADA/presales must be intentional and audited.
"""),
            ("Checkout idempotency & payments", """
Idempotency record stores final order_id + response. Payment unknown → query provider; do not create second auth blindly. Compensation if auth succeeded but inventory commit failed (rare if reserve-first).
"""),
            ("Flash sale readiness", """
Warm caches, pre-scale, freeze deploys, load-shed priorities (browse secondary to hold/checkout), status page. Practice with synthetic onsale drills.
"""),
            ("Fraud & bots", """
Defend queue entry, hold, checkout separately. Purchase caps per user/event. Device attestation. Velocity. Payment risk. Assume determined scalpers — perfect prevention impossible; raise cost.
"""),
            ("GA vs reserved seating", """
GA: atomic quantity. Reserved: per-seat state. Don't mix without pools. Best-available algorithms are optimizer on top of same CAS primitives.
"""),
        ],
    )
    t += s6(
        "Ticketing platform with waiting room, strongly consistent seat holds, idempotent checkout, payment reconciliation, and hot-event isolation — optimized to never oversell under stampede.",
        [
            "Seat CAS/versioned transitions",
            "Short TTL holds",
            "Waiting room paces admit",
            "Idempotent checkout",
            "Fail closed inventory",
            "Event home region / hot cell",
            "Fraud at multiple gates",
            "Payment reconcile path",
        ],
        [
            "Oversell from fail-open",
            "Hold expiry races with payment",
            "Bot capture of inventory",
            "Payment provider outage mid-onsale",
            "Hot event noisy neighbor",
        ],
        [
            ("0–5", "Scope seats+GA; oversell=0 goal"),
            ("5–15", "Inventory holds + state machine"),
            ("15–25", "Waiting room + onsale"),
            ("25–35", "Checkout idempotency + pay"),
            ("35–45", "Fraud, scale jumps, drills"),
        ],
        "**Ticketmaster**: lease seats, pace admits, idempotent pay, fail closed — oversell is the SEV0.",
    )
    t += s7([
        ("How do you guarantee no oversell?", "Conditional updates/CAS on seat state; fail closed; single home for event inventory; exhaustive concurrency tests."),
        ("Hold then pay or pay then hold?", "Hold/reserve first with short TTL; pay; commit. Paying first risks charging without seats."),
        ("What if payment succeeds and commit fails?", "Compensating refund/void; rare if commit is local CAS after auth; reconcile jobs."),
        ("FIFO or lottery queue?", "Product call; FIFO feels fairer; lottery fights bots camping connection start. Explain trade-off."),
        ("Why not serializable DB for whole event?", "Possible for small; under stampede, section striping + CAS scales better than one giant serial queue."),
        ("GA inventory in Redis only?", "Risk durability; use Redis for speed + durable log/SQL commit, or SQL atomic with care."),
        ("Idempotency key TTL?", "Days; persist until order terminal; same key must not map to different carts."),
        ("Seat map consistency?", "Layout immutable versioned; availability from inventory service."),
        ("Multi-region writes?", "Avoid multi-writer per seat; home region; DR failover with fence."),
        ("How long hold TTL?", "Balance UX vs lockup; 2–5 min common; shorter under extreme contention."),
        ("Cart with 8 seats atomic?", "Yes — all CAS in one txn ordered by seat_id."),
        ("Prevent bot holds?", "Queue gates, captcha/attestation, per-user hold caps, anomaly on hold/release patterns."),
        ("Flash sale deploy freeze?", "Yes — change management is part of design."),
        ("Secondary market?", "Separate inventory of listings with transfer of ticket state; out of MVP."),
        ("Barcode security?", "Signed/rotating codes; scan once; rotate on transfer."),
        ("Partial failure issuing tickets?", "Order SOLD + ticket issue outbox retry; user sees order confirmed."),
        ("Thundering herd polls?", "ETag/version; exponential backoff; section-level notifications."),
        ("Clock sync for onsale_at?", "Server gate; don't trust client clock."),
        ("Deadlock on seats?", "Always lock seat_ids sorted."),
        ("What is deal-breaker?", "Optimistic browse cart without server hold selling duplicates."),
        ("Measure fairness?", "Distribution of purchase success vs queue rank; bot purchase rate."),
        ("Spill to read-only mode?", "Browse OK; holds disabled with message better than corruption."),
        ("Price changes mid-hold?", "Lock price in hold/quote snapshot."),
        ("Accessible seating abuse?", "Eligibility checks; audit; limited pool."),
        ("CDC to search?", "Eventual catalog OK; inventory truth not from search."),
        ("Load test reality?", "Production-like waiting room + hold mix; not only GET seatmap."),
        ("Why event_id shard?", "Contention locality; isolation; placement on dedicated hardware for mega events."),
        ("Refund inventory return?", "Only if ticket unused; CAS SOLD→AVAILABLE carefully with order state."),
    ])
    t += s8(
        [
            ("SLO table", """
| SLO | Target |
|-----|--------|
| Oversell | 0 |
| Hold conflict handled cleanly | 100% errors typed |
| Checkout idempotent replay | Correct same order |
| Waiting room availability | 99.9% during onsale |
| Seat map cached p50 | <300ms |
"""),
            ("Ownership", """
| Area | Team |
|------|------|
| Inventory/holds | Ticketing inventory |
| Waiting room | Edge / traffic |
| Checkout/orders | Purchasing |
| Fraud | Risk |
| Payments | Payments |
"""),
            ("Failure drills", """
- Dual write attempt across regions for same event
- Expire holds during payment auth
- Payment 909 unknown outcome
- Bot amplification
- Hot event DB failover
"""),
            ("State machine", """
AVAILABLE → HELD → SOLD → (REFUNDED→AVAILABLE*) 
HELD → AVAILABLE on TTL
*policy gated
"""),
        ],
        [
            "Oversell=0 as hard goal",
            "CAS holds + TTL",
            "Waiting room admit math",
            "Idempotent checkout",
            "Fail closed",
            "Hot-event isolation",
            "Fraud gates",
            "22+ Q&A",
            "Payment reconcile",
            "Onsalle drill checklist",
        ],
    )
    return _ensure_min(t, 750, _PADS_TM)

