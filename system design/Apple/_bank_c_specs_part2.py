"""Bank C topic specs part 2 — remaining Apple-domain drills."""
from _bank_c_helpers import S, std_estimation

SPECS_PART2 = [
    S(
        title="Secure iCloud Keychain Synchronization",
        filename="icloud-keychain-sync-system-design.md",
        focus="Secure Enclave · Circle of trust · Escrow · E2E sync · Device approval · Zero-knowledge · Conflict-free creds",
        goal="**bound Keychain sync**—sync passwords, keys, and Wi‑Fi creds across devices with zero-knowledge server storage.",
        scope="Design iCloud Keychain–style sync: Secure Enclave–backed keys, encrypted item blobs, device approval circle, escrow/recovery trade-offs, and conflict-free credential merge—from tens of millions of users through progressive scale.",
        entity="user_id",
        sync_primitive="Encrypted item sync log",
        fr=[("F1","What syncs?","Passwords, keys, certs, Wi‑Fi, Safari autofill","Typed item records"),("F2","E2E?","Yes—server blind","Ciphertext items only"),("F3","New device?","Approve from existing device or escrow","Circle of trust"),("F4","Conflicts?","Rare—items keyed by domain/account","Upsert by stable item id"),("F5","Revoke?","Remove device from circle","Stop wrapping new keys"),("F6","Escrow?","Optional recovery","Security vs UX trade-off"),("F7","Sharing?","Password sharing later","Separate share keys"),("F8","Web?","No raw keys in browser","Out of scope"),("F9","Audit?","Device list only","No plaintext logs"),("F10","TOTP seeds?","Same vault","High sensitivity"),("F11","Corporate MDM?","Separate profile","Split keychain domains"),("F12","Migration?","Schema version per item","Additive evolution")],
        mvp=["Device enrollment + approval", "Encrypted item upsert sync", "Circle of trust management", "Revoke device", "Escrow optional path", "Stable item_id merge"],
        outmvp=["Full HSM escrow lecture", "Cross-platform non-Apple clients", "Enterprise SCIM"],
        nfr=[("N1","Confidentiality","Zero-knowledge","No server decrypt"),("N2","Add device latency","Minutes if approval","User-initiated"),("N3","Sync latency","Background","p99 < 30s after change"),("N4","Integrity","Tamper-evident","AEAD + signatures"),("N5","Availability","99.99%","Local cache always"),("N6","Recovery","Explicit UX","No silent backdoor"),("N7","Battery","Tiny payloads","Coalesce OK"),("N8","Abuse","Stolen account","Step-up + device list")],
        happy=["Save password on iPhone → encrypt → sync → Mac autofill", "New iPad approved from iPhone → unwrap vault key → pull items", "Delete login on Mac → tombstone → removed on iPhone", "Revoke stolen Mac → rotate wraps → no new decrypt"],
        edges=[("Approval timeout","Expire request"),("Escrow recovery","Separate auth factors"),("Duplicate item ids","Upsert"),("Clock skew","Server ts for ordering only"),("Corrupt item","Quarantine + re-sync"),("MDM wipe","Local purge"),("Account transfer","Out of MVP"),("Quantum agility","Version crypto suites")],
        scales=[("Users", "200M", "500M", "800M", "800M+"), ("Items/user avg", "300", "400", "500", "600"), ("Item writes/day", "100M", "1B", "10B", "100B"), ("Avg item blob", "500 B", "600 B", "700 B", "800 B"), ("Devices/user", "3", "3.5", "4", "4"), ("New device enroll/day", "2M", "20M", "200M", "2B"), ("Approval sessions peak", "50K", "500K", "5M", "50M"), ("Revokes/day", "500K", "5M", "50M", "500M")],
        jumps=[("10×","Shard item logs; cache public device keys"),("100×","Regional home cells; batch item deltas"),("1,000×","Strict rate limits; hierarchical snapshots")],
        constraints=["Not designing Secure Enclave silicon", "Escrow is product/legal sensitive", "Zero-knowledge is non-negotiable"],
        abstractions="""```text
User, Device(device_id, identity_key, trust_state)
VaultKey (wrapped per device)
KeychainItem(item_id, type, ciphertext, version)
CircleOfTrust(members[], pending[])
SyncCursor(device_id, seq)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Encrypt items | Secure Enclave | Stores ciphertext |
| Approve device | User on trusted device | Routes approval msgs |
| Autofill decrypt | Yes | Never |
| Item merge | Upsert by item_id | Relay only |""",
        options=[("A. Server-readable vault","Easy autofill web","Breaks zero-knowledge","Apple bar"),("B. Zero-knowledge encrypted items","Privacy","Recovery harder","— chosen"),("C. Per-device vaults only","Simple","No sync","Multi-device"),("D. P2P only sync","No server trust","Offline/recovery hard","Mobile")],
        chosen="Zero-knowledge encrypted items with circle-of-trust device approval and optional escrow recovery.",
        privacy="Vault key never leaves devices as plaintext; server stores wrapped keys and AEAD item blobs; approval requires existing trusted device or escrow.",
        consistency="Upsert by stable `item_id`; deletes are tombstones; ordering via server_seq for audit not merge logic.",
        offline="Local Keychain always authoritative for read; writes queue; sync on connectivity.",
        battery="Small payloads; batch item deltas; low frequency.",
        region="Home cell per user; global anycast API; no cross-region plaintext.",
        abuse="Rate limit enroll; step-up on mass export patterns; device attestation.",
        diagram="""```text
Device A (trusted) ←→ Approval Service ←→ Device B (new)
       ↓                                      ↓
  Keychain local                         Wrap vault key
       ↓                                      ↓
   Item encrypt ──→ Item Sync Log (ciphertext) ──→ other devices
```""",
        designed="Zero-knowledge Keychain sync with Secure Enclave keys, device approval circle, encrypted item upserts, and explicit recovery/escrow modes.",
        tradeoffs=[("Zero-knowledge vs web autofill","ZK","Privacy"),("Escrow vs no recovery","Optional escrow","UX"),("Approval friction","Required","Security"),("Item-level vs blob sync","Item upsert","Merge simplicity")],
        path="MVP: circle + encrypted upsert. Scale: shard logs, batch deltas, regional cells.",
        risks=["Escrow perception as backdoor", "Approval UX friction", "Stolen account + weak 2FA", "Schema migration bugs"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Server can reset passwords | Only if escrow/recovery—explicit |
| 100M × 500B items = PB/day | ~50 GB/day item writes—check math |""",
        bottlenecks="""1. New device approval storms  
2. Item log write QPS  
3. Escrow recovery abuse  
4. Revoke/re-wrap races  
5. Autofill read path (local only)""",
        estimation=std_estimation("Keychain item writes", "100M/day", "~500 B", "2×"),
    ),
    S(
        title="Local-First Document Synchronization",
        filename="local-first-document-sync-system-design.md",
        focus="iCloud Drive · File versions · CRDT metadata · Conflict copies · E2E · On-demand fetch · Battery",
        goal="**bound document sync**—Files-app style sync with local-first open/edit, version history, and conflict copies.",
        scope="Design local-first document sync (Pages/Files/iCloud Drive class): encrypted file blobs, metadata log, conflict copies, on-demand hydration, and battery-aware transfers at progressive scale.",
        entity="container_id / file_id",
        sync_primitive="File metadata log + content-addressed blobs",
        fr=[("F1","Granularity?","Files + folders + packages","Tree + blob refs"),("F2","Conflicts?","Keep both copies","Conflict file naming UX"),("F3","Versions?","History N deep","Snapshot chain"),("F4","Partial sync?","On-demand download","Placeholder + fetch"),("F5","E2E?","Optional ADP","Ciphertext blobs"),("F6","Apps?","Bundle packages atomic","Temp + commit"),("F7","Delete?","Trash window","Tombstones"),("F8","Sharing?","Link/folder share","ACL + share keys"),("F9","Offline?","Edit local copy","Upload on reconnect"),("F10","Large files?","Chunked resumable","Upload sessions"),("F11","Watchers?","FSEvents local","Debounce cloud push"),("F12","Desktop sync?","Mac full tree","Same protocol")],
        mvp=["Local-first open", "Metadata log + blob store", "Conflict copies", "On-demand fetch", "Trash + restore", "Resumable upload", "Debounced directory sync"],
        outmvp=["Real-time multi-user OT", "Deduup across users at 1,000×", "Block-level sync inside files"],
        nfr=[("N1","Privacy","E2E option","Opaque blobs"),("N2","Open local file","Instant","Local path < 100ms"),("N3","Hydrate cloud-only","User-visible","p50 < 3s Wi‑Fi"),("N4","Battery","Defer bulk","Wi‑Fi/charging bias"),("N5","Durability","No silent loss","ACK before eviction"),("N6","Consistency","Eventual metadata","Conflict copies on write clash"),("N7","Availability","99.9%","Offline OK"),("N8","Quota","Enforced","Pause uploads")],
        happy=["Create doc offline → save local → upload → iPad sees file", "Edit same file offline on two Macs → two conflict copies", "Evict local → cloud placeholder → fetch on open", "Move folder → tree ops batch sync", "Delete → trash → restore"],
        edges=[("Package half-written","Atomic commit marker"),("Huge video project","Chunked"),("Rename vs edit race","Separate ops"),("Symlinks","Policy: no or materialize"),("iCloud strip on low disk","Never evict before ACK"),("Path case sensitivity","Normalize"),("Malware scan","Out of band optional"),("Share link revoke","Rekey")],
        scales=[("Users", "100M", "400M", "800M", "800M+"), ("Files/user avg", "5K", "8K", "12K", "15K"), ("Uploads/day", "200M", "2B", "20B", "200B"), ("Avg file", "2 MB", "3 MB", "4 MB", "5 MB"), ("Metadata ops/day", "1B", "10B", "100B", "1T"), ("On-demand fetches/day", "500M", "5B", "50B", "500B"), ("Peak upload QPS", "100K", "1M", "10M", "100M"), ("Containers", "100M", "400M", "800M", "800M+")],
        jumps=[("10×","Shard containers; upload sessions"),("100×","Regional blobs; directory snapshots"),("1,000×","Cold tier; hierarchical cursors")],
        constraints=["Not block-level sync inside PDF", "Packages must commit atomically"],
        abstractions="""```text
Container, File(file_id, path, blob_ref, version)
DirectoryEvent(rename/move/create/delete)
UploadSession, Placeholder(local_evicted)
ConflictCopy(original_id, device_id, ts)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| File bytes encrypt | Yes | Ciphertext store |
| FSEvents debounce | Yes | Receives batched tree ops |
| Conflict detection | Compare version vector | Stores both blobs |
| On-demand fetch | Scheduler | Serves parts |""",
        options=[("A. Block-level sync","Efficient","Complex","MVP"),("B. Whole-file versioned","Simple","Bandwidth","— chosen"),("C. Last writer only","Easy","Data loss","Never"),("D. Central lock server","No conflicts","Offline bad","Mobile")],
        chosen="Whole-file content-addressed blobs with metadata log; write conflicts → sibling conflict copies.",
        privacy="File keys in client; server stores ciphertext; paths may be encrypted in E2E mode.",
        consistency="Per-file version vector; conflict if concurrent writes without knowledge.",
        offline="Full local tree; outbox for ops; upload queue for bytes.",
        battery="Debounce tree ops; defer large files; coalesce metadata.",
        region="Regional blob placement; home cell metadata.",
        abuse="Quota; rate limit download; share link TTL.",
        diagram="""```text
Mac/iOS Files → Local FS + Placeholders → Encrypt → Upload Queue
                        ↓
                 Metadata Log (home cell)
                        ↓
                 Blob Store + Push dirty
```""",
        designed="Local-first document sync with versioned ciphertext blobs, tree metadata log, conflict copies, on-demand hydration, and resumable transfers.",
        tradeoffs=[("Conflict copies vs merge","Copies","Simplicity"),("Whole file vs blocks","Whole file","MVP"),("Eager sync all","On-demand","Disk/battery"),("E2E vs server preview","E2E","Privacy")],
        path="MVP: file versions + conflicts. Scale: shards, regional blobs, snapshots.",
        risks=["Evict-before-ACK", "Package atomicity", "Path normalization bugs", "Thundering fetch herds"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| 200M × 2MB = 400 EB/day | 400 PB/day—still huge; regional sharding required |
| Server merges doc contents under E2E | No |""",
        bottlenecks="""1. Blob ingress/egress  
2. Directory op storms  
3. On-demand fetch stampedes  
4. Conflict copy storage  
5. Placeholder/eviction races""",
        estimation=std_estimation("File uploads", "200M/day × 2 MB ≈ 400 PB/day? → 200e6 × 2e6 = 4e14 B = 400 TB/day", "2–5 MB avg", "3×"),
    ),
    S(
        title="Health Data Sync (Watch ↔ iPhone)",
        filename="health-data-watch-iphone-sync-system-design.md",
        focus="HealthKit · BLE · Privacy · On-device aggregation · Encrypted cloud backup · Low power · Sample merge",
        goal="**bound Health sync**—move workouts, vitals, and activity samples between Watch and iPhone with strict privacy and battery limits.",
        scope="Design HealthKit-class Watch↔iPhone sync plus optional encrypted iCloud backup: local authoritative stores, BLE transport, merge semantics for samples, and zero plaintext health on server.",
        entity="user_id / data_type",
        sync_primitive="Sample batch sync + encrypted backup blob",
        fr=[("F1","Data types?","Steps, HR, workouts, sleep, rings","Typed schemas"),("F2","Privacy?","On-device; encrypted backup","No server ML on raw"),("F3","Transport?","BLE primary; cloud optional","WatchConnectivity"),("F4","Conflicts?","Samples immutable by (type, start, source)","Upsert/dedupe"),("F5","Aggregation?","Rings on-device","Derive locally"),("F6","Third-party apps?","Write with permission","HealthKit ACL"),("F7","Delete?","User purge propagates","Tombstones"),("F8","Real-time?","HR stream during workout","BLE streaming"),("F9","Backup?","Encrypted iCloud category","Optional E2E"),("F10","Clinical?","Out of MVP","Higher bar"),("F11","Watch alone?","Buffer then sync","Local queue"),("F12","Duplicate sources?","Merge policy per type","Prefer Apple Watch")],
        mvp=["BLE sample batch sync", "Dedupe by sample key", "On-device ring aggregation", "Encrypted backup optional", "Permission gates", "Delete propagation"],
        outmvp=["Full FHIR clinical exchange", "Server-side coaching ML on raw", "Cross-user leaderboards with raw HR"],
        nfr=[("N1","Privacy","Health never plaintext server","E2E backup option"),("N2","BLE latency","Seconds for batches","Stream for active workout"),("N3","Battery","Watch ultra low","Batch + compress"),("N4","Accuracy","No double count steps","Dedupe keys"),("N5","Durability","No sample loss","Watch buffer durable"),("N6","Offline","Watch stores days","Backfill on connect"),("N7","Integrity","Signed batches","AEAD"),("N8","Compliance","User consent","Granular permissions")],
        happy=["Run on Watch → samples buffer → BLE to iPhone → rings update", "iPhone backup encrypts vault → iCloud ciphertext", "Third-party app writes weight → permission prompt → sync", "Delete workout → tombstone → Watch purges", "Watch offline day → bulk sync on charge"],
        edges=[("Double step sources","Dedupe policy"),("Clock skew on samples","Use start/end ts + source"),("BLE disconnect mid-workout","Resume stream"),("Large workout GPS","Chunk batches"),("Restore new phone","Decrypt backup"),("Revoke app permission","Stop future writes"),("HR spike glitch","Outlier filter on-device"),("Low Watch storage","Compact buffer")],
        scales=[("Watch pairs", "50M", "100M", "150M", "200M"), ("Samples/day", "5B", "50B", "500B", "5T"), ("Avg sample", "50 B", "60 B", "80 B", "100 B"), ("BLE sessions/day", "100M", "1B", "10B", "100B"), ("Backup/day", "10M", "100M", "1B", "10B"), ("Avg backup delta", "5 MB", "8 MB", "10 MB", "12 MB"), ("Workout streams/min peak", "500K", "5M", "50M", "500M"), ("Apps writing", "10K", "50K", "100K", "200K")],
        jumps=[("10×","Batch compression; typed sharding in backup"),("100×","Incremental backup snapshots"),("1,000×","Strict on-device aggregation only")],
        constraints=["Not designing Watch sensors", "Health data = highest privacy bar", "Server never trains on raw without consent"],
        abstractions="""```text
HealthSample(type, start, end, value, source, device)
WorkoutSession(id, samples[])
RingDay aggregates (on-device)
EncryptedBackupBlob(user_id, generation)
PermissionGrant(app_id, type)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Raw samples | Watch + iPhone | Never plaintext |
| Ring closure | iPhone/Watch compute | No |
| Encrypted backup | Client encrypt | Stores blob |
| Permission | HealthKit local | No central PHI DB |""",
        options=[("A. Cloud authoritative health DB","Analytics easy","Privacy fail","Apple"),("B. On-device SoT + encrypted backup","Privacy","Device loss needs backup","— chosen"),("C. Sync every sample realtime to cloud","Simple","Battery/privacy","No"),("D. P2P only","No server","Restore hard","Needs backup")],
        chosen="On-device HealthKit stores with BLE batch sync; optional encrypted iCloud backup; server blind to samples.",
        privacy="Samples stay on devices; backup is AEAD ciphertext; aggregations for sharing are explicit user actions.",
        consistency="Immutable sample keys; dedupe on ingest; deletes propagate as tombstones.",
        offline="Watch buffers; iPhone merges on connect; rings recompute locally.",
        battery="BLE batching; compress; defer non-workout sync; workout stream only when active.",
        region="Backup regional; no central sample database.",
        abuse="App permission review; rate limit writes per app.",
        diagram="""```text
Apple Watch → Sample Buffer → BLE Batches → iPhone HealthKit
                                ↓
                    On-device Ring Engine
                                ↓
              Optional Encrypt → iCloud Backup Blob
```""",
        designed="Privacy-first health sync: Watch buffers, BLE batches to iPhone authoritative store, on-device aggregation, optional encrypted cloud backup—no plaintext health server.",
        tradeoffs=[("Cloud analytics vs privacy","On-device","HIPAA-like user trust"),("Realtime vs batch","Batch default","Battery"),("Dedupe strictness","Prefer Watch","Accuracy"),("Backup E2E","Yes option","Recovery UX")],
        path="MVP: BLE batch + dedupe. Scale: incremental encrypted backups; no raw sample cloud.",
        risks=["Double counting", "BLE buffer loss", "Permission sprawl", "Backup key loss"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Upload every HR sample live | Watch battery dies |
| Server aggregates rings | Violates on-device story |""",
        bottlenecks="""1. BLE bandwidth during dense workouts  
2. Dedupe correctness  
3. Backup size growth  
4. Third-party write abuse  
5. Restore time on new phone""",
        estimation=std_estimation("Health samples", "5B/day × 50 B ≈ 250 GB/day raw—stays on-device", "50–100 B", "5× workout peaks"),
    ),
    S(
        title="Battery-Conscious Background Upload Scheduler",
        filename="battery-conscious-upload-scheduler-system-design.md",
        focus="BGTaskScheduler · Network · Thermal · Low Power · Priority queues · Coalescing · Fairness · Cross-app",
        goal="**bound upload scheduling**—OS-level scheduler that batches cloud uploads across apps without killing battery.",
        scope="Design a system-wide battery-conscious upload scheduler for iOS/macOS cloud sync agents: priority scoring, network/thermal/battery gates, coalesced radio wakes, and fair cross-app budgets at scale.",
        entity="device_id / upload_job",
        sync_primitive="Priority queue + budget tokens",
        fr=[("F1","Clients?","Photos, iCloud, Messages attachments, Backup","Pluggable agents"),("F2","Inputs?","Battery, thermal, LP mode, network, charging","Policy engine"),("F3","Priority?","User-visible > backlog > prefetch","Score function"),("F4","Fairness?","No single app monopolizes","Per-app caps"),("F5","Resume?","Chunk sessions","Idempotent"),("F6","Cellular?","Policy per job type","User overrides"),("F7","Deadline?","User opened photo → boost","Dynamic reprioritize"),("F8","Metrics?","Energy per upload","Privacy-safe telemetry"),("F9","Debugging?","Instruments hooks","Dev visibility"),("F10","VPN?","Respect routes","Same queue"),("F11","Plugged in?","Max parallelism","Charging lane"),("F12","Server hints?","Optional urgency","Never mandatory")],
        mvp=["Priority queue per device", "Battery/thermal/network gates", "Coalesce radio wakes", "Resumable chunk uploads", "User-visible boost", "Per-app fairness caps"],
        outmvp=["Optimal ML scheduler for all networks", "Cross-vendor OS integration"],
        nfr=[("N1","Battery impact","Minimal overnight","Within OS budget"),("N2","User-visible latency","Fast","Boost path < 2s start"),("N3","Fairness","No starvation","Weighted fair queue"),("N4","Predictability","Deterministic policy","Testable rules"),("N5","Safety","No data loss","ACK before eviction"),("N6","Privacy","No content in logs","Job metadata only"),("N7","Scale","All iOS devices","On-device only control plane"),("N8","Extensibility","New agents","Stable API")],
        happy=["Photo capture queues upload → waits for Wi‑Fi+charge → completes overnight", "User opens cloud-only file → scheduler boosts fetch", "Low Power Mode → defer non-visible", "Three apps backlog → fair shares radio", "Thermal throttle → pause large uploads"],
        edges=[("Flapping network","Hysteresis"),("User toggles cellular allow","Immediate re-score"),("Job too large","Split chunks"),("App killed","Persist queue"),("Server 503","Backoff+jitter"),("Duplicate job ids","Idempotent"),("Roaming cost","Stricter cellular gate"),("MDM policy","Override windows")],
        scales=[("Devices", "200M", "500M", "1B", "1B"), ("Jobs/day", "2B", "20B", "200B", "2T"), ("Avg job", "2 MB", "3 MB", "4 MB", "5 MB"), ("Peak concurrent jobs/device", "5", "8", "10", "12"), ("Radio wakes/day", "50", "40", "30", "25"), ("Apps using scheduler", "20", "40", "60", "80"), ("User boost/day", "10", "15", "20", "25"), ("Energy budget mAh/day", "50", "45", "40", "35")],
        jumps=[("10×","Better coalescing; shared TLS session"),("100×","Predictive Wi‑Fi prefetch windows"),("1,000×","Hardware radio hints integration")],
        constraints=["Scheduler runs on-device", "Server cannot force immediate upload", "Privacy: job metadata only"],
        abstractions="""```text
UploadJob(id, app_id, bytes_remaining, priority_class, network_policy)
SchedulerPolicy(battery gates, thermal gates, fairness weights)
RadioSession(coalesced_jobs[])
ChunkSession(resume tokens)
BudgetToken(app_id, remaining_mAh_estimate)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Priority scoring | Yes | Optional hints only |
| When radio opens | OS scheduler | — |
| Chunk storage | Local + cloud | Receives parts |
| Energy accounting | OS | Aggregate opt-in telemetry |""",
        options=[("A. FIFO queue","Simple","Starvation","Multi-app"),("B. Strict priority preemption","Fast user path","Churn","— chosen with fairness"),("C. Upload immediately always","Fresh sync","Battery death","Mobile"),("D. Server-driven push upload now","Central control","Battery/privacy","No")],
        chosen="Weighted priority queue with coalesced radio sessions, battery/thermal gates, and per-app fairness caps.",
        privacy="Logs contain job sizes and error codes—not file names or bytes.",
        consistency="Jobs idempotent; chunk ACKs durable before local eviction.",
        offline="Queue persists; resume on connectivity with same priorities.",
        battery="Core product goal—minimize wakes; defer; charge+Wi‑Fi lane.",
        region="N/A—device local scheduler.",
        abuse="Malicious app registering huge jobs → caps and attestation.",
        diagram="""```text
Apps → UploadJob API → Priority Queue → Policy Engine (battery/thermal/net)
                              ↓
                     Coalesced Radio Session
                              ↓
                     Chunk Upload to Cloud
```""",
        designed="On-device upload scheduler coalescing jobs across apps, gating on battery/thermal/network, boosting user-visible work, and enforcing fairness without exposing content.",
        tradeoffs=[("Coalesce vs latency","Coalesce default","Battery"),("Fairness vs VIP app","Weighted fair","Trust"),("Cellular default","Defer large","Bill shock"),("Server hints","Optional","Client sovereign")],
        path="MVP: priority + gates + coalesce. Evolve predictive scheduling and tighter energy models.",
        risks=["Starvation bugs", "Boost path neglects fairness", "Evict-before-ACK in apps", "Policy complexity"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Upload each photo immediately | Radio spinup dominates energy |
| Server can force upload | OS policy owns radio |""",
        bottlenecks="""1. Radio wake count  
2. Fairness tuning  
3. Thermal throttle interactions  
4. Chunk resume storms after outage  
5. Cross-app TLS session reuse""",
        estimation=std_estimation("Upload jobs", "2B/day globally", "2–5 MB", "peak evening Wi‑Fi"),
    ),
    S(
        title="Privacy-Preserving Analytics Aggregation",
        filename="privacy-preserving-analytics-system-design.md",
        focus="Differential privacy · On-device · Opt-in · Local aggregation · Secure enclave noise · No raw logs · KPI dashboards",
        goal="**bound analytics**—collect product metrics without storing per-user raw event streams.",
        scope="Design Apple-style privacy-preserving analytics: on-device aggregation, differential privacy noise, opt-in cohorts, encrypted transport of aggregates only, and scalable server rollup—from billions of devices to dashboard SLOs.",
        entity="metric_id / cohort",
        sync_primitive="DP aggregate reports",
        fr=[("F1","Events?","App launches, crashes, feature flags—not content","Typed schemas"),("F2","Opt-in?","User control / settings","No silent full tracking"),("F3","DP?","Noise on device or ingest","Epsilon budgets"),("F4","Granularity?","Daily aggregates","No per-keystroke"),("F5","PII?","Forbidden in payloads","Hashes only if needed"),("F6","Realtime?","Near-line OK","Not second-level funnels"),("F7","Experiments?","A/B with DP","Cohort caps"),("F8","Revoke?","Stop future reports","No retro raw"),("F9","Cross-device?","Per-device reports","No join without consent"),("F10","Attribution?","Campaign buckets coarse","No fingerprint"),("F11","Debug?","Local logs only","Not auto-upload"),("F12","Legal?","Retention limits","Aggregate TTL")],
        mvp=["On-device daily bucket aggregation", "DP noise injection", "Opt-in gate", "Encrypted upload of aggregates", "Server rollup pipelines", "Epsilon budget accounting"],
        outmvp=["Individual user funnels", "Cross-app web tracking graph", "Raw event lake for ads"],
        nfr=[("N1","Privacy","DP + no raw","Plausible deniability"),("N2","Utility","Useful KPIs","Budget trade-off"),("N3","Battery","Once/day batch","Coalesce"),("N4","Bandwidth","KB/day/device","Tiny"),("N5","Latency","Dashboard T+1","Not realtime"),("N6","Integrity","Signed reports","Anti-spoof basic"),("N7","Compliance","GDPR delete","Aggregates only"),("N8","Scale","1B devices","Shard rollups")],
        happy=["Device aggregates crash counts locally → adds noise → uploads ciphertext bucket", "Server sums buckets → dashboard shows trend", "User opts out → stop reports", "Epsilon exhausted → suppress rare events", "A/B cohort reported with min threshold"],
        edges=[("Small cohort suppression","Threshold k"),("Malicious inflation","Outlier caps"),("Clock skew","UTC day bucket"),("Offline week","Single merged report"),("App update schema","Version field"),("Replay report","Nonce + day"),("MDM disable","Policy hook"),("Locale granularity","Coarse buckets only")],
        scales=[("Devices reporting", "500M", "800M", "1B", "1B+"), ("Reports/day", "500M", "800M", "1B", "1B"), ("Avg report", "2 KB", "2 KB", "3 KB", "3 KB"), ("Metrics catalog", "500", "2K", "5K", "10K"), ("Rollup QPS peak", "50K", "200K", "1M", "5M"), ("Dashboard queries/day", "10K", "100K", "1M", "10M"), ("Epsilon budgets", "100", "200", "500", "1K"), ("Experiments active", "100", "500", "2K", "5K")],
        jumps=[("10×","Stream rollup; metric registry"),("100×","Regional aggregation cells"),("1,000×","Hierarchical DP composition accounting")],
        constraints=["No raw event lake", "Interview: contrast with ad-tech tracking", "On-device first"],
        abstractions="""```text
MetricSchema(id, buckets, epsilon_allocation)
LocalAggregator(day, counters[])
DPNoise(seed, epsilon)
AggregateReport(device_anon_id, day, payload_enc)
RollupShard(metric_id, day)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Raw events | Process locally | Never stored |
| Noise injection | Prefer device | Or trusted ingest enclave |
| Dashboards | — | Aggregates only |
| Opt-in | Settings | Enforce drop |""",
        options=[("A. Central raw event pipeline","Rich analytics","Privacy fail","Apple"),("B. On-device DP aggregates","Private","Less granular","— chosen"),("C. No analytics","Max privacy","Blind product","Unrealistic"),("D. Hash user id server-side","Join sessions","Tracking risk","No")],
        chosen="On-device daily aggregation with DP noise and encrypted upload of coarse buckets only.",
        privacy="No persistent per-user event store; reports are anonymous noisy counts; small-N suppression.",
        consistency="Eventual daily buckets; idempotent report per (device, day, schema_v).",
        offline="Buffer counters locally; upload next window.",
        battery="Once-per-day upload; negligible.",
        region="Regional rollup; global merge of aggregates only.",
        abuse="Spoof reports → attestation + rate limits + outlier detection on aggregates.",
        diagram="""```text
App → Local Event Counters → DP Noise → Encrypt Report
                                    ↓
                          Aggregate Ingest → Rollup DB → Dashboards
```""",
        designed="Privacy-preserving analytics via on-device aggregation, differential privacy, opt-in controls, and server storage of noisy aggregates—not raw events.",
        tradeoffs=[("Utility vs epsilon","Budget per metric","Privacy"),("On-device vs server noise","On-device","Trust"),("Realtime vs daily","Daily","Battery/privacy"),("Granularity","Coarse buckets","Re-identification risk")],
        path="MVP: daily DP reports. Scale: rollup sharding, metric registry, experiment framework.",
        risks=["Epsilon mis-accounting", "Small cohort leaks", "Utility too low", "Perception as tracking"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| DP means zero risk | Reduces; epsilon matters |
| 1B devices × 1MB logs = 1 EB/day | Reports are ~2 KB → ~2 TB/day |""",
        bottlenecks="""1. Rollup hot metrics  
2. DP budget management  
3. Schema evolution  
4. Attestation spoofing  
5. Dashboard query cost""",
        estimation=std_estimation("DP reports", "1B/day × 2 KB ≈ 2 TB/day", "2–3 KB", "2× morning upload"),
    ),
    S(
        title="AirDrop-Style Peer-to-Peer Transfer",
        filename="airdrop-p2p-transfer-system-design.md",
        focus="BLE discovery · AWDL · TLS · Contacts-only privacy · Resume · On-device keys · No cloud bytes",
        goal="**bound AirDrop**—discover nearby devices and transfer files directly with privacy and no server storage of content.",
        scope="Design AirDrop-class P2P transfer: BLE/Wi‑Fi Direct discovery, identity via contacts/Apple ID hashes, encrypted session, resume, and battery-aware radio use—without uploading file bytes to cloud.",
        entity="session_id",
        sync_primitive="Direct encrypted session (no cloud SoT)",
        fr=[("F1","Discovery?","BLE + peer Wi‑Fi","Nearby only"),("F2","Privacy?","Contacts only / everyone","Hashed identity"),("F3","Content?","Photos, files, URLs","Opaque bytes"),("F4","Server role?","Optional relay metadata only","No content storage"),("F5","Resume?","Partial transfers","Chunk ack"),("F6","Auth?","Apple ID + certs","Mutual trust UI"),("F7","Spam?","Accept/decline UI","No auto-save"),("F8","Multi-file?","Queue in session","Ordered"),("F9","Mac↔iPhone?","Same protocol","Cross-form-factor"),("F10","Background?","User initiated","Not silent"),("F11","Malware?","Quarantine on receive","Sandbox open"),("F12","Enterprise?","MDM disable","Policy")],
        mvp=["BLE discovery + identity hash", "AWDL data path", "Mutual TLS session", "Encrypt file chunks", "Accept UI", "Resume partial", "No cloud bytes"],
        outmvp=["Internet-wide P2P without proximity", "Server relay of ciphertext at scale"],
        nfr=[("N1","Privacy","No cloud content","Ephemeral session"),("N2","Throughput","Wi‑Fi Direct speeds","Tens MB/s"),("N3","Discovery latency","< 2s nearby","BLE"),("N4","Battery","User initiated","Teardown radios after"),("N5","Security","Mutual auth","Pinning"),("N6","UX","Clear sender preview","Anti spoof"),("N7","Reliability","Resume","Chunk state"),("N8","Scale","Local only","No global QPS")],
        happy=["User share sheet → discover contact's Mac → accept → encrypted chunks → Photos import", "Decline → session torn down", "Walk out of range → pause → resume in range", "Contacts-only hides from strangers", "Multiple photos queue sequentially"],
        edges=[("Stranger spoof name","Contacts-only mitigates"),("Mid-transfer kill","Resume token"),("Low battery","Warn + throttle"),("Hotspot conflict","Radio arbitration"),("Huge video","Chunk + progress"),("Both send simultaneously","Separate sessions"),("Corporate Wi‑Fi isolation","AWDL still works"),("Malicious file","Sandbox viewer")],
        scales=[("Sessions/day global", "50M", "200M", "500M", "1B"), ("Avg transfer", "5 MB", "8 MB", "10 MB", "12 MB"), ("Peak concurrent/local", "3", "4", "5", "6"), ("Discovery broadcasts/s/venue", "100", "500", "2K", "5K"), ("Session duration avg", "5s", "8s", "10s", "12s"), ("Resume rate", "5%", "5%", "4%", "4%"), ("Decline rate", "20%", "20%", "18%", "18%"), ("MDM disabled orgs", "5%", "10%", "15%", "20%")],
        jumps=[("10×","Better radio coexistence"),("100×","Faster crypto (hardware)"),("1,000×","N/A—local protocol")],
        constraints=["Proximity required", "No cloud SoT for bytes", "User must accept inbound"],
        abstractions="""```text
DiscoveryAdvertisement(identity_hash, capabilities)
TransferSession(session_id, keys, chunk_state)
Chunk(index, ciphertext, tag)
AcceptanceToken(user gesture)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| File bytes | P2P only | Not stored |
| Identity hash | Local contacts map | Optional directory |
| Encrypt/session | Both peers | No |
| Discovery | BLE/AWDL | None |""",
        options=[("A. Cloud intermediary upload","Works anywhere","Privacy/latency","AirDrop"),("B. Pure P2P encrypted","Private fast","Proximity","— chosen"),("C. Bluetooth only","Low power","Slow","Large files"),("D. QR code only","Simple","Bad UX","Default")],
        chosen="Proximity P2P with encrypted AWDL session, contacts-based discovery privacy, and no server content retention.",
        privacy="Content never hits cloud; identity leaked only as hashed tokens; user accept required.",
        consistency="Single session SoT between two peers; chunk acks idempotent.",
        offline="N/A—local link; no cloud needed.",
        battery="Tear down AWDL after session; no background discovery by default.",
        region="N/A—local.",
        abuse="Stranger spam → contacts-only; rate limit discovery; no auto-accept.",
        diagram="""```text
Sender iPhone ⇄ BLE Discovery ⇄ Receiver Mac
       ⇅ AWDL encrypted chunks ⇅
   (no cloud file path)
```""",
        designed="AirDrop-style P2P: BLE discovery, AWDL encrypted transfer, contacts-only privacy, accept UI, resume—zero cloud storage of payloads.",
        tradeoffs=[("P2P vs cloud relay","P2P","Privacy/speed"),("Everyone vs contacts","Contacts default","Spam"),("Resume vs restart","Resume","Complexity"),("Background send","User initiated","Battery")],
        path="MVP: discovery + encrypted session. Evolve radio coexistence and faster crypto.",
        risks=["Identity spoofing", "Radio conflicts", "Partial receive junk", "UX decline fatigue"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| AirDrop uploads to iCloud | Defeats purpose |
| Always discoverable | Battery + spam |""",
        bottlenecks="""1. AWDL setup latency  
2. Radio coexistence  
3. Resume state size  
4. Contact hash collisions (rare)  
5. User accept friction""",
        estimation=std_estimation("P2P sessions", "50M/day × 5 MB ≈ 250 TB/day moved device-local—not cloud ingress", "5–12 MB", "evening peaks"),
    ),
    S(
        title="Family Sharing Permissions",
        filename="family-sharing-permissions-system-design.md",
        focus="Apple ID family · ACL · Purchase sharing · Screen Time · Key wrapping · Privacy between members · Child accounts",
        goal="**bound Family Sharing**—share subscriptions and enforce parental controls without leaking private data between members.",
        scope="Design Family Sharing permissions: family group graph, role-based ACLs, shared entitlements, child privacy walls, encrypted personal data separation, and sync of family-scoped settings across devices.",
        entity="family_id / member_id",
        sync_primitive="Family policy graph + encrypted personal partitions",
        fr=[("F1","Roles?","Organizer, parent, child, member","RBAC"),("F2","Share what?","Purchases, subscriptions, locations opt-in","Not personal photos by default"),("F3","Child privacy?","Hide messages/health from parents by default","Policy exceptions Screen Time"),("F4","Purchase?","Organizer pays","Entitlement propagation"),("F5","Leave family?","Revoke entitlements","Rekey"),("F6","Invite?","Email/iMessage","Pending tokens"),("F7","Screen Time?","Parental controls","Separate subsystem sync"),("F8","Location sharing?","Opt-in Find My circle","Not automatic"),("F9","Age up?","Promote child account","Policy transition"),("F10","Region?","Store region alignment","Compliance"),("F11","Audit?","Parent sees activity summaries not content","Aggregates"),("F12","Death/transfer?","Organizer transfer","Support flow")],
        mvp=["Family group CRUD", "Role-based ACL", "Shared entitlements service", "Personal partition isolation", "Invite/leave flows", "Revoke on leave", "Child age policies"],
        outmvp=["Full legal custody workflows", "Cross-platform family beyond Apple"],
        nfr=[("N1","Privacy between members","Strong default walls","No read others' iCloud"),("N2","ACL check latency","< 50ms","Cached entitlements"),("N3","Consistency","Eventual entitlements","Minutes OK"),("N4","Security","Rekey on membership change","Forward secrecy lite"),("N5","Availability","99.99% entitlement reads","CDN cache"),("N6","Compliance","COPPA","Child defaults"),("N7","Battery","Low churn sync","Push on change"),("N8","Abuse","Invite spam limits","Rate limits")],
        happy=["Organizer enables Apple One → entitlements propagate to members", "Child tries purchase → ask to buy flow", "Member leaves → subscriptions revert → rekey shared keys", "Parent sets Screen Time → syncs to child devices", "Teen age-up → privacy defaults shift"],
        edges=[("Organizer leaves","Forced transfer"),("Region mismatch","Block join"),("Stale entitlement cache","TTL + push invalidate"),("Shared app hidden personal data","Partition keys"),("Compromised child device","Local controls"),("Duplicate invites","Idempotent"),("Court order","Support legal process"),("Subscription lapse","Grace period")],
        scales=[("Families", "50M", "80M", "100M", "120M"), ("Members/family avg", "3", "3.5", "4", "4"), ("Entitlement checks/day", "500M", "5B", "50B", "500B"), ("Policy changes/day", "5M", "50M", "500M", "5B"), ("Invites/day", "500K", "5M", "50M", "500M"), ("Leave/revoke/day", "200K", "2M", "20M", "200M"), ("Child accounts", "30M", "50M", "70M", "80M"), ("Cached entitlement QPS peak", "100K", "1M", "10M", "100M")],
        jumps=[("10×","Entitlement CDN; family graph shard"),("100×","Regional policy stores"),("1,000×","Edge ACL cache with signed bundles")],
        constraints=["Not all iCloud data is family-shared", "COPPA/privacy walls are non-negotiable"],
        abstractions="""```text
Family(family_id, organizer_id, region)
Member(user_id, role, age_band)
Entitlement(sku, family_id, seats)
PersonalPartition(user_id, encryption boundary)
PolicyEvent(invite, leave, purchase_request)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Personal iCloud data | E2E user keys | No family read |
| Entitlements | Cached | Authoritative catalog |
| Screen Time rules | Applied locally | Policy sync |
| Purchase ask | UI | Approval workflow |""",
        options=[("A. Shared family vault for all data","Simple sharing","Privacy disaster","No"),("B. Entitlements + isolated partitions","Safe","Complex ACL","— chosen"),("C. Parent can read all child content","Easy monitoring","Trust/legal fail","Default off"),("D. No server family graph","P2P only","Doesn't scale","No")],
        chosen="Family graph for entitlements and policies; cryptographic/logical partitions keep personal data isolated; rekey on membership changes.",
        privacy="Family shares SKUs not messages; child data walled; location opt-in; aggregates for Screen Time not raw content.",
        consistency="Entitlement propagation eventual; membership changes trigger revoke + cache bust.",
        offline="Cached entitlements allow offline app launch within grace TTL.",
        battery="Push on policy change only; no polling.",
        region="Family region locked for store compliance; graph home cell.",
        abuse="Invite rate limits; child purchase friction; audit organizer actions.",
        diagram="""```text
Organizer → Family Graph Service → Entitlement Propagation
                ↓                           ↓
         Member devices ← Policy Sync ← Screen Time / Ask to Buy
Personal iCloud partitions remain isolated (separate keys)
```""",
        designed="Family Sharing with RBAC entitlements, isolated personal partitions, child privacy defaults, rekey on leave, and cached entitlement distribution.",
        tradeoffs=[("Sharing vs privacy","Isolated partitions","Trust"),("Cache TTL vs freshness","Short TTL + push","Latency"),("Parent visibility","Aggregates not content","Ethics"),("Rekey cost","On leave","Security")],
        path="MVP: group + entitlements. Scale: edge cache, sharded graph, policy sync.",
        risks=["Overbroad parent access UX", "Stale entitlements piracy", "Region compliance", "Rekey failures"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Family shares all photos | Opt-in albums only |
| Parent reads iMessages by default | No |""",
        bottlenecks="""1. Entitlement check QPS  
2. Rekey storms on leave  
3. Ask-to-buy latency  
4. Cache invalidation  
5. Cross-region store rules""",
        estimation=std_estimation("Entitlement checks", "500M/day", "tiny ACL blob", "10× peak"),
    ),
]
