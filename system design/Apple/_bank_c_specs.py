"""All Bank C topic specifications for doc generation."""
from _bank_c_helpers import S, std_estimation
from _bank_c_specs_part2 import SPECS_PART2
from _bank_c_specs_part3 import SPECS_PART3

MORE_SPECS: list[dict] = []

# ---- Notes ----
MORE_SPECS.append(S(
    title="Notes Synchronization and Conflict Resolution",
    filename="notes-sync-conflict-resolution-system-design.md",
    focus="CRDT vs op-log · Rich text merge · Attachments · Folders · E2E · Offline · Battery · On-device preview",
    goal="**bound Notes sync**—multi-device note/folder sync with rich-text conflicts, attachments, and Apple-grade privacy.",
    scope="Design Apple Notes–style sync: local-first editing, encrypted mutation log or CRDT hybrid, attachment blobs, folder hierarchy, explicit conflict UX, and battery-aware background sync—from millions of accounts through 10× / 100× / 1,000× scale.",
    entity="account_id / note_id",
    sync_primitive="Encrypted mutation log",
    fr=[
        ("F1", "What syncs?", "Notes, folders, tags, attachments, checklists, locks", "Separate note body vs attachment plane"),
        ("F2", "Rich text?", "Attributed string / block JSON", "Field-level or block-level merge"),
        ("F3", "E2E?", "Standard + optional E2E category", "Ciphertext bodies under E2E"),
        ("F4", "Conflicts?", "Rare auto-merge; surface conflict note if ambiguous", "3-way merge + conflict clone"),
        ("F5", "Attachments?", "Images, scans, drawings", "Encrypted blob refs in note"),
        ("F6", "Shared notes?", "Optional collab", "Share ACL + share key phase 2"),
        ("F7", "Offline?", "Full edit offline", "Outbox + causal ops"),
        ("F8", "Delete?", "Recently Deleted window", "Tombstones"),
        ("F9", "Search?", "On-device index preferred", "Encrypted index optional"),
        ("F10", "Locks?", "Face ID note lock", "Key stays on-device; body extra encrypted"),
        ("F11", "Web?", "Limited under E2E", "Keys on trusted devices only"),
        ("F12", "Version history?", "Optional snapshots", "Periodic encrypted snapshots"),
    ],
    mvp=["Local-first note CRUD", "Encrypted mutation log per account", "LWW metadata + block merge for body", "Attachment upload/download", "Folder tree sync", "Conflict note UX", "Battery-coalesced sync"],
    outmvp=["Real-time OT like Google Docs", "Full CRDT for rich text at 1,000×", "Cross-org enterprise ACLs"],
    nfr=[
        ("N1", "Privacy", "E2E option", "Server opaque under E2E"),
        ("N2", "Edit latency", "Instant local", "p99 local write < 50ms"),
        ("N3", "Sync lag", "Background OK", "p99 cursor lag < 60s active"),
        ("N4", "Battery", "No keystroke sync", "Debounce + coalesce"),
        ("N5", "Offline", "Weeks OK", "Outbox durable"),
        ("N6", "Consistency", "Eventual", "Documented merge"),
        ("N7", "Durability", "No lost notes", "Local before UI; cloud before eviction"),
        ("N8", "Availability", "99.9% sync plane", "Local always works"),
    ],
    happy=["Type on iPhone offline → sync on Wi‑Fi → Mac shows note", "Attach scan → encrypt → upload → iPad fetches thumb", "Rename folder on Mac → iPhone tree updates", "Delete → tombstone → restore from Recently Deleted", "Concurrent checklist toggles merge via OR-set"],
    edges=[("Two devices edit same paragraph", "Block merge or conflict note"), ("Huge attachment", "Chunked resumable upload"), ("Note lock", "Body key wrapped locally"), ("Account merge", "Out of MVP"), ("Import 10k notes", "Snapshot baseline"), ("Clock skew", "Lamport + server_seq"), ("Corrupt block", "Checksum fail → re-fetch"), ("Shared note leave", "Rekey share")],
    scales=[("Accounts", "100M", "500M", "1B", "1B+ cells"), ("Notes/account avg", "200", "400", "600", "800"), ("Edits/day", "500M", "5B", "50B", "500B"), ("Attachments/day", "50M", "500M", "5B", "50B"), ("Avg note body", "4 KB", "6 KB", "8 KB", "10 KB"), ("Avg attachment", "500 KB", "1 MB", "2 MB", "3 MB"), ("Sync sessions/day", "200M", "2B", "20B", "200B"), ("Conflict rate", "0.1%", "0.1%", "0.05%", "0.05%")],
    jumps=[("10×", "Shard logs; debounced push"), ("100×", "Compaction snapshots; attachment CDN ciphertext"), ("1,000×", "Hierarchical cursors; block-level CRDT subset")],
    constraints=["Not designing full iWork collab", "Rich text merge is hard—document policy", "E2E limits server search"],
    abstractions="""```text
Account, Note(note_id, folder_id, body_enc, lamport)
Folder(folder_id, parent_id, title)
Attachment(att_id, blob_ref, note_id)
Mutation(op_id, note_id, op_type, payload_enc, lamport)
DeviceCursor(account_id, last_seq)
```""",
    split="""| Concern | On-device | Server |
|---------|----------|--------|
| Edit/merge apply | Yes | Orders ops only |
| Encrypt body | Yes | Stores ciphertext |
| Search index | Prefer on-device | Optional encrypted index |
| Preview render | Yes | No plaintext |
| Debounce sync | Yes | Receives batches |""",
    options=[("A. Full doc CRDT", "Auto-merge", "Complex rich text", "Team capacity"), ("B. Op-log + LWW whole doc", "Simple", "Lost edits", "Rich text"), ("C. Op-log + block merge + conflict UI", "Balanced", "Some manual UX", "— chosen"), ("D. Last sync wins only", "Easy", "Bad UX", "Never")],
    chosen="Encrypted op-log with block-level merge; ambiguous regions → conflict note clone.",
    privacy="Note body encrypted with per-note or account key; attachments separate content keys inside envelope; server sees sizes and opaque refs only under E2E.",
    consistency="Single-writer home cell assigns `server_seq`; offline ops carry lamport; body merge on apply.",
    offline="SQLite/Core Data outbox; edit immediately local; sync agent batches on network/battery OK.",
    battery="Debounce edits 2–5s; coalesce folder tree ops; defer attachment uploads on cellular.",
    region="Home cell per account; regional blob store; edge read for attachments.",
    abuse="Rate limits; max note size; attachment quotas.",
    diagram="""```text
iPhone/Mac Notes App → Local DB + Outbox → Encrypt
                              ↓
                     Sync Agent (debounced)
                              ↓
              Edge API → Mutation Log (home cell)
                              ↓
              Attachment Store (ciphertext) + Push Coalescer
```""",
    designed="Local-first Notes with encrypted op-log, block-aware merge, attachment ciphertext, explicit conflict notes, and debounced battery-aware sync.",
    tradeoffs=[("CRDT vs op-log", "Op-log + selective merge", "Ship complexity"), ("Keystroke sync", "Debounced batches", "Battery"), ("E2E vs server search", "On-device search under E2E", "Privacy"), ("Conflict auto vs manual", "Auto + conflict note fallback", "Trust")],
    path="MVP: op-log + LWW metadata + block merge. 10–100×: shards, snapshots. 1000×: hierarchical cursors, optional CRDT blocks.",
    risks=["Rich text merge bugs", "Chatty sync", "Evict-before-ACK", "Ambiguous conflict UX"],
    unit_traps="""| Claim | Truth |
|-------|-------|
| Sync every keystroke | Battery death |
| Server generates note previews under E2E | Contradiction |
| 500M edits × 1MB = 500 PB/day | Check units—bodies are KB-scale |""",
    bottlenecks="""1. Debounced sync still high QPS at 100×  
2. Attachment ingress  
3. Folder tree deep renames  
4. Conflict note UX volume  
5. Compaction of long note histories""",
    estimation=std_estimation("Note edits", "500M/day", "4–8 KB body + metadata", "3×"),
    qa_extra=[("Notes-specific", [("How merge rich text?", "Block/paragraph ops with lamport; conflict note if overlapping edits."), ("Checklist items?", "OR-set per item id."), ("Locked notes?", "Extra key in Secure Enclave; sync ciphertext only.")])],
    apps_extra=[("Mutation types", """```text
NOTE_CREATE / NOTE_DELETE / NOTE_BODY_PATCH
FOLDER_MOVE / FOLDER_RENAME
ATTACH_ADD / ATTACH_REMOVE
CHECKLIST_TOGGLE (OR-set)
```""")],
))

MORE_SPECS.extend(SPECS_PART2)
MORE_SPECS.extend(SPECS_PART3)
