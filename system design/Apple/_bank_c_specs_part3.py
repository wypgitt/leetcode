"""Bank C topic specs part 3 — final Apple-domain drills."""
from _bank_c_helpers import S, std_estimation

SPECS_PART3 = [
    S(
        title="On-Device ML Model Updates",
        filename="on-device-ml-model-updates-system-design.md",
        focus="Core ML · Delta updates · App Store privacy · On-device inference · Signed bundles · Staged rollout · Battery",
        goal="**bound ML model delivery**—ship updated on-device models safely without exfiltrating user data.",
        scope="Design on-device ML model update system: signed model bundles, delta delivery, staged rollout, compatibility checks, and privacy-safe telemetry—from millions of devices through progressive scale.",
        entity="model_id / device_id",
        sync_primitive="Signed model manifest + delta blobs",
        fr=[("F1","Models?","Photos memories, keyboard, Siri on-device","Per-feature bundles"),("F2","Privacy?","No user data upload for training default","Federated optional separate"),("F3","Delivery?","Background Wi‑Fi","Delta preferred"),("F4","Verify?","Code signing + hash","Reject tamper"),("F5","Rollback?","Keep N-1 bundle","Switch on crash spike"),("F6","A/B?","Device cohort flags","Opt-in metrics only"),("F7","Size?","10–200 MB full; deltas smaller","Resume download"),("F8","Hardware?","ANE/GPU capability matrix","Compatibility manifest"),("F9","Locale?","Per-locale models","Selective fetch"),("F10","Battery?","Charging+Wi‑Fi gate","User unaware"),("F11","Encryption?","TLS + signed at rest on device","No E2E needed"),("F12","Developer?","3rd-party Core ML apps use App Store","Same CDN path")],
        mvp=["Signed model manifest CDN", "Delta update packages", "Device capability matching", "Background download scheduler", "Atomic install + rollback", "Crash spike auto-rollback", "Privacy-safe rollout metrics"],
        outmvp=["Full federated training pipeline", "Server-side inference on user media"],
        nfr=[("N1","Privacy","No raw user content leaves","On-device infer only"),("N2","Download","Background","No UI block"),("N3","Integrity","Signed bundles","Mandatory"),("N4","Battery","Wi‑Fi+charge bias","OS scheduler"),("N5","Availability","CDN 99.99%","Cached N-1"),("N6","Compatibility","No brick old devices","Manifest gates"),("N7","Rollback","< 1h detect","Telemetry thresholds"),("N8","Size","Delta < 30% full typical","Binary diff")],
        happy=["New Photos model staged 1% → metrics OK → 100%", "Device matches ANE → fetch correct variant", "Delta applied → atomic swap → inference uses new weights", "Crash spike → auto rollback manifest", "Locale fr-FR gets localized model"],
        edges=[("Partial download","Resume"),("Wrong variant","Manifest recheck"),("Disk full","Evict old after swap safe"),("MDM block","Skip"),("User Low Power","Defer"),("Signature fail","Reject"),("Two models same slot","Version monotonic"),("Enterprise offline","Use cached")],
        scales=[("Devices eligible", "200M", "500M", "1B", "1B"), ("Model updates/month", "4", "8", "12", "12"), ("Avg delta", "20 MB", "30 MB", "40 MB", "50 MB"), ("Full model", "100 MB", "150 MB", "200 MB", "250 MB"), ("CDN egress/day peak", "5 PB? → 200M×20MB=4PB wrong; 10M updates×20MB=200TB", "200 TB", "500 TB", "1 PB"), ("Rollout stages", "5", "8", "10", "12"), ("Variants", "50", "200", "500", "1K"), ("Rollback events/year", "2", "5", "10", "20")],
        jumps=[("10×","CDN edge; manifest v2"),("100×","P2P cache inside ISP optional"),("1,000×","Binary diff fleet; hardware sharding")],
        constraints=["Inference always on-device for user content", "Signed delivery non-negotiable"],
        abstractions="""```text
ModelManifest(model_id, version, hw_tags, locale, sha256)
DeltaPackage(from_v, to_v, patch_blob)
DeviceProfile(ane, os, locale)
InstallSlot(active, previous)
RolloutCohort(percent, filters)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Inference | Yes | Never on user raw |
| Download install | Background | CDN signed blobs |
| Capability match | Local | Manifest catalog |
| Rollout decision | — | Control plane |""",
        options=[("A. Server inference on photos","Easy updates","Privacy fail","Apple"),("B. Signed on-device bundles + delta","Private","Large downloads","— chosen"),("C. Train in app from user data","Personalized","Creepiness","Opt-in only"),("D. Email models","No","No","No")],
        chosen="Signed CDN model manifests with capability-aware delta downloads, atomic install, staged rollout, auto-rollback.",
        privacy="User content never sent for default updates; telemetry is aggregate crash/latency only.",
        consistency="Monotonic model version per slot; atomic swap.",
        offline="Keep N-1; apply when download completes.",
        battery="Wi‑Fi + charging scheduler integration.",
        region="Regional CDN; same signed manifest globally.",
        abuse="Signature verification; manifest pinning.",
        diagram="""```text
Control Plane → Model Manifest CDN → Device Scheduler
                         ↓
              Verify Sign → Apply Delta → Core ML Runtime
                         ↓
              Privacy-safe rollout metrics
```""",
        designed="On-device ML updates via signed deltas, hardware/locale matching, background install, staged rollout, and rollback—user content stays local.",
        tradeoffs=[("Delta vs full","Delta","Bandwidth"),("Staged vs instant","Staged","Safety"),("On-device vs cloud infer","On-device","Privacy"),("Many variants","Accurate HW/locale","CDN cost")],
        path="MVP: manifest + delta + rollback. Scale: CDN, cohort control, diff optimization.",
        risks=["Bad model bricking feature", "CDN stampede on rollout", "Variant explosion", "Rollback too slow"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Upload photos to improve model by default | No—federated is opt-in separate |
| 1B × 100MB daily | Updates are periodic deltas not daily full |""",
        bottlenecks="""1. CDN egress on wide rollout  
2. Disk space for swap  
3. ANE variant matrix  
4. Crash detection latency  
5. Scheduler fairness vs apps""",
        estimation=std_estimation("Model delta downloads", "10M devices/day × 20 MB ≈ 200 TB/day on rollout day", "20–50 MB delta", "rollout day spike"),
    ),
    S(
        title="Restore-from-Backup / New-Device Setup",
        filename="restore-backup-new-device-system-design.md",
        focus="Encrypted backup · Device migration · Key unwrap · Progressive restore · Wi‑Fi migration · Battery · Privacy",
        goal="**bound new device setup**—restore encrypted backup or transfer directly with minimal downtime and strong privacy.",
        scope="Design restore/backup for new iPhone: encrypted iCloud backup or direct device-to-device migration, key hierarchy unwrap, progressive tiered restore, and battery-aware download scheduling.",
        entity="user_id / backup_generation",
        sync_primitive="Encrypted backup snapshot + migration stream",
        fr=[("F1","Sources?","iCloud encrypted backup, Mac backup, direct migration","Multiple paths"),("F2","E2E?","Backup ciphertext user keys","Server blind"),("F3","Progressive?","Setup assistant usable early","Tier 0 apps first"),("F4","Keys?","From old device or escrow","Secure Enclave wrap"),("F5","Size?","50–200 GB typical","Chunked"),("F6","Direct migration?","Proximity Wi‑Fi","P2P encrypted"),("F7","App data?","Per-app containers","Parallel restore"),("F8","Photos?","Separate photo library sync","May defer bulk"),("F9","Watch?","Pair after phone","Dependent"),("F10","Failure?","Resume","Session tokens"),("F11","Auth?","Apple ID + passcode","Step-up"),("F12","Time?","Hours background OK","UX progress")],
        mvp=["Encrypted backup upload from old device", "New device key unwrap", "Tiered restore (settings, apps, media)", "Resumable chunk download", "Direct migration session", "Progress UI", "Integrity verify per chunk"],
        outmvp=["Cross-vendor Android migration full fidelity", "Instant full restore in minutes for 200GB"],
        nfr=[("N1","Privacy","E2E backup","Server opaque"),("N2","Time to usable","< 30 min partial","Tier 0 first"),("N3","Durability","11 nines backup","Erasure coded"),("N4","Battery old device","Migration while plugged","Warn if not"),("N5","Bandwidth","Wi‑Fi preferred","Cellular optional capped"),("N6","Integrity","Checksums","Per chunk AEAD"),("N7","Availability","Restore 99.9%","Retry"),("N8","Security","Anti brute force","Rate limit unwrap")],
        happy=["New iPhone → sign in → unwrap backup key → download tier 0 → usable → background rest", "Direct migration old→new over Wi‑Fi P2P encrypted", "Resume after reboot continues chunks", "Photos defer to library sync path", "Watch re-pairs after phone ready"],
        edges=[("Wrong Apple ID","Block restore"),("Corrupt chunk","Re-fetch"),("Insufficient iCloud storage","Prompt upgrade"),("2FA new device","Trust flow"),("Old device not available","Escrow recovery"),("Partial app fail","Retry per app"),("Low disk on new","Pause + prompt"),("MDM supervised","Policy profile first")],
        scales=[("Restores/day", "2M", "10M", "20M", "30M"), ("Avg backup", "80 GB", "100 GB", "120 GB", "150 GB"), ("Direct migrations/day", "1M", "5M", "10M", "15M"), ("Chunk size", "4 MB", "8 MB", "8 MB", "16 MB"), ("Peak restore QPS", "50K", "200K", "500K", "1M"), ("Backup generations/user", "3", "5", "7", "10"), ("Tier 0 size", "2 GB", "3 GB", "4 GB", "5 GB"), ("Failed chunk rate", "0.1%", "0.1%", "0.05%", "0.05%")],
        jumps=[("10×","Parallel app restore; edge CDN"),("100×","Incremental forever-backup"),("1,000×","Cold tier backups; dedup across gens")],
        constraints=["Not designing iOS Setup Assistant UI pixels", "Backup E2E is default story"],
        abstractions="""```text
BackupGeneration(id, user_id, manifest_enc, created_at)
BackupChunk(index, ciphertext, aad)
MigrationSession(old_device, new_device, keys)
RestorePlan(tiers[], priorities[])
KeyWrap(backup_key → device SE)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Encrypt backup | Old device | Stores ciphertext |
| Unwrap keys | New device SE | Wrapped blobs only |
| Restore apply | New device | Serves chunks |
| Migration stream | P2P encrypted | Optional rendezvous |""",
        options=[("A. Server-decrypt restore","Easy support","Privacy fail","Apple"),("B. E2E encrypted backup + tiered restore","Private","Long restore","— chosen"),("C. Block-level dedup server-side","Storage save","Needs plaintext hashes","E2E"),("D. Manual iTunes only","Simple","Bad UX","Legacy")],
        chosen="E2E encrypted backup with tiered progressive restore and optional P2P direct migration; server stores opaque chunks.",
        privacy="Backup ciphertext; keys unwrap only on authenticated new device; no server content indexing.",
        consistency="Backup generation monotonic; restore idempotent per chunk index.",
        offline="Migration P2P local; cloud restore needs network.",
        battery="Prefer plugged; parallelize downloads on Wi‑Fi; throttle on battery.",
        region="Regional backup storage; nearest edge fetch.",
        abuse="Rate limit unwrap attempts; attestation on restore.",
        diagram="""```text
Old iPhone → Encrypt Backup → Chunk Upload → Backup Store
New iPhone → Auth → Unwrap Key → Tier0 Download → Apply
Optional: Old ⇄ New P2P Migration Session (encrypted)
```""",
        designed="Encrypted backup and new-device restore with tiered progressive download, P2P migration option, chunk resume, and Secure Enclave key unwrap—server blind to content.",
        tradeoffs=[("Speed vs privacy","E2E ciphertext","Trust"),("Tiered vs all-at-once","Tiered","Time-to-usable"),("Cloud vs direct migration","Both","UX choice"),("Cellular restore","Opt-in capped","Cost")],
        path="MVP: encrypted backup + tier 0. Scale: edge CDN, parallel app restore, incremental backups.",
        risks=["Key loss without escrow", "Long restore UX", "Chunk corruption", "Storage cost"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Apple decrypts backup for support | Not under E2E |
| 2M × 80GB in one day = 160EB | ~160 PB/day peak—still huge; staggered |""",
        bottlenecks="""1. Chunk download bandwidth  
2. Key unwrap auth latency  
3. Apply to disk on new device  
4. Backup storage cost  
5. Migration radio stability""",
        estimation=std_estimation("Backup chunks", "2M restores × 80 GB ≈ 160 PB/day if simultaneous—real staggered ~low PB", "4–16 MB chunk", "evening peaks"),
    ),
    S(
        title="Find My Aggregation",
        filename="find-my-aggregation-system-design.md",
        focus="Bluetooth beacons · Encrypted location · Crowd-sourced relay · Privacy · Rotation keys · Lost Mode · Battery",
        goal="**bound Find My**—aggregate encrypted location reports from billions of devices without Apple learning user locations.",
        scope="Design Find My network: rotating BLE keys, encrypted location reports, crowd-sourced relay, server aggregation without decryption, Lost Mode, and battery-minimal beaconing at scale.",
        entity="accessory_id / owner_id",
        sync_primitive="Encrypted location reports",
        fr=[("F1","Devices?","AirTags, iPhones, Macs, accessories","Unified protocol"),("F2","Privacy?","No location plaintext server","Rotating keys"),("F3","Relay?","Any nearby Apple device uploads report","Crowd network"),("F4","Owner fetch?","Decrypt reports client-side","Owner key"),("F5","Lost Mode?","Show contact message","Public NFC URL"),("F6","Stalking?","Unknown tracker alerts","On-device"),("F7","Precision?","UWB optional","Separate"),("F8","Battery tag?","Year-long coin cell","Minimal adv"),("F9","Separation alerts?","Leave behind notify","Geofence on-device"),("F10","Share item?","Family sharing location opt-in","Separate ACL"),("F11","Anti-replay?","Timestamp windows","Drop stale"),("F12","Lawful?","Legal process limited","No historical plaintext")],
        mvp=["Rotating BLE advertisement keys", "Encrypted location report upload", "Owner decrypt on fetch", "Lost Mode message", "Unknown tracker detection", "Report dedupe + TTL"],
        outmvp=["Real-time continuous tracking at meter precision server-side", "Global heatmaps of devices"],
        nfr=[("N1","Privacy","Server blind","E2E location"),("N2","Latency find","Minutes–hours","Crowd density dependent"),("N3","Tag battery","Months–year","Low duty cycle"),("N4","Relay battery","Minimal impact","Short upload"),("N5","Scale","Billions reports/day","Shard ingest"),("N6","Integrity","Signed reports","Anti-spoof basic"),("N7","Stalker safety","Alerts","On-device"),("N8","Durability","Reports TTL days","Not long-term archive")],
        happy=["AirTag advertises rotating key → stranger iPhone uploads encrypted report → owner iPhone decrypts map point", "Lost Mode NFC shows contact", "Unknown AirTag traveling with user → alert", "Family shared item visible to group decrypt keys", "Tag battery lasts months"],
        edges=[("Dense city fast updates","Many reports dedupe"),("Rural sparse","Slow find"),("Key rotation sync","Owner publishes schedule"),("Malicious flood reports","Rate limit + filter"),("Tracker disable speaker","Safety alert still"),("Airplane tag","Last seen"),("Reset tag","New keypair",),("Subpoena","Cannot decrypt location")],
        scales=[("Active items", "500M", "1B", "2B", "3B"), ("Reports/day", "10B", "100B", "500B", "1T"), ("Avg report", "200 B", "250 B", "300 B", "350 B"), ("Relay devices", "1B", "2B", "3B", "4B"), ("Owner fetches/day", "50M", "200M", "500M", "1B"), ("Lost Mode activations/day", "100K", "500K", "1M", "2M"), ("Unknown tracker alerts/day", "50K", "200K", "500K", "1M"), ("Report TTL hours", "24", "24", "12", "12")],
        jumps=[("10×","Shard report ingest; edge upload"),("100×","Geo-partition TTL stores"),("1,000×","Adaptive relay duty; report summarization before owner fetch")],
        constraints=["Server must not learn locations", "Battery on tag is hard constraint"],
        abstractions="""```text
AccessoryKeyRotation(public_key_period, private_owner_key)
LocationReport(encrypted_payload, relay_device_anon)
OwnerFetchQuery(key_id_range, since_ts)
LostModeMessage(public_nfc)
SeparationAlert(on-device geofence)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Location plaintext | Owner device only | Never |
| BLE advertise | Tag/phone | — |
| Relay upload | Finder phone encrypts? reports already encrypted | Stores blobs |
| Stalker detect | Owner/finder on-device | No |""",
        options=[("A. Central location DB plaintext","Easy maps","Privacy fail","Apple"),("B. Rotating keys + encrypted reports","Private","Crowd needed","— chosen"),("C. GPS only cellular tag","Accurate","Power/cost","AirTag"),("D. Pure local Bluetooth rangefinding","No network","No remote find","Supplement only")],
        chosen="Rotating BLE keys with encrypted crowd-sourced reports; owner derives locations client-side; server stores opaque blobs with TTL.",
        privacy="Location encrypted to owner; rotating keys prevent tracking by network; stalker alerts on-device.",
        consistency="Reports append-only with TTL; owner merge dedupes by time/location cluster.",
        offline="Tag advertises; finder uploads when online; owner fetches when online.",
        battery="Tag: slow adv interval; relay phone: batch uploads.",
        region="Global ingest; geo-sharded TTL storage.",
        abuse="Rate limits; unknown tracker alerts; Lost Mode abuse review.",
        diagram="""```text
AirTag --BLE adv--> Finder iPhone --encrypted report--> Ingest Shard
                                                          ↓
Owner iPhone --fetch reports--> Decrypt --> Map UI
Server never sees coordinates
```""",
        designed="Find My with rotating keys, encrypted crowd-sourced location reports, owner-side decryption, Lost Mode, and on-device anti-stalking—server aggregation without plaintext location.",
        tradeoffs=[("Privacy vs find speed","Privacy","Crowd density"),("Report retention","Short TTL","Storage"),("Tag battery vs update rate","Slow adv","Latency"),("Precision UWB","Optional","Hardware")],
        path="MVP: encrypted reports + owner decrypt. Scale: sharded ingest, TTL geo stores.",
        risks=["Stalking misuse", "Sparse network slow find", "Report flooding", "Key rotation bugs"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Apple knows where all tags are | Only encrypted blobs |
| 10B reports × 1KB = 10PB/day | ~2 TB/day at 200B |""",
        bottlenecks="""1. Report ingest QPS  
2. Owner fetch query fanout  
3. TTL store size  
4. Relay phone battery if misconfigured  
5. Key rotation coordination""",
        estimation=std_estimation("Find My reports", "10B/day × 200 B ≈ 2 TB/day", "200–350 B", "3× peak hours"),
    ),
    S(
        title="App Store Search and Ranking",
        filename="app-store-search-ranking-system-design.md",
        focus="Search index · Privacy-safe queries · Ranking signals · Personalization on-device · Editorial · Abuse · Latency",
        goal="**bound App Store search**—fast relevant search with minimal retention of sensitive query logs.",
        scope="Design App Store search/ranking: inverted index, privacy-safe query handling, on-device personalization features, ranking blend (relevance, quality, business rules), and anti-abuse at billions of queries scale.",
        entity="query_session",
        sync_primitive="Search index + ranking pipeline",
        fr=[("F1","Scope?","Apps, games, IAP, stories","Unified index"),("F2","Privacy?","Minimize query log retention","On-device history option"),("F3","Personalization?","Downloads/genre on-device features","No creepy cross-app web"),("F4","Latency?","< 200ms p50","Edge cache"),("F5","Spelling?","Typo tolerance","Edit distance"),("F6","Ads?","Optional separate auction","Disclosed"),("F7","Kids store?","Safe filtering","Policy layer"),("F8","Localization?","Per storefront locale","Shard indexes"),("F9","Abuse?","Keyword stuffing detection","Developer penalties"),("F10","Editorial?","Boost curated","Manual overrides"),("F11","Offline?","No search","Cache browse"),("F12","Analytics?","Aggregate only","DP")],
        mvp=["Inverted index per locale", "Query parsing + spellcheck", "Ranking blend (text, quality, rules)", "Privacy-safe logging aggregates", "Autocomplete prefix index", "Abuse signals in index"],
        outmvp=["Individual user click models with long-term profiles", "Cross-web tracking for ads"],
        nfr=[("N1","Privacy","No long-lived raw queries","TTL + DP"),("N2","Latency","p50 < 200ms","Regional edge"),("N3","Relevance","Human eval + online metrics","Continuous"),("N4","Availability","99.99%","Degrade browse"),("N5","Fairness","New apps discoverable","Exploration slots"),("N6","Compliance","Regional laws","Geo filters"),("N7","Freshness","New apps hours","Incremental index"),("N8","Scale","100M queries/day","Shard")],
        happy=["User types 'photo edit' → autocomplete → results ranked → tap install", "Typo 'instagrm' corrected", "Kids account filters adult apps", "New app indexed within hours", "Aggregate trending computed with DP"],
        edges=[("Query spam bots","Rate limit"),("Keyword stuffing","Rank penalty"),("Locale mismatch","Storefront lock"),("Zero results","Relax filters"),("Ad auction timeout","Organic only"),("GDPR delete user","No raw profile"),("Index delay","Stale badge"),("Malicious app title squat","Trademark rules")],
        scales=[("Queries/day", "100M", "500M", "1B", "2B"), ("Index size apps", "2M", "3M", "4M", "5M"), ("Autocomplete QPS peak", "200K", "1M", "5M", "10M"), ("Index update/min", "100", "500", "2K", "5K"), ("Storefronts", "175", "175", "175", "175"), ("Ranking features", "50", "100", "200", "300"), ("Exploration slots", "5%", "5%", "3%", "3%"), ("Log retention days", "7", "3", "1", "aggregate only")],
        jumps=[("10×","Regional search cells; prefix cache"),("100×","Learned sparse retrieval; on-device re-rank"),("1,000×","Hybrid ANN + inverted; federated signals opt-in")],
        constraints=["Contrast with ad-tech tracking in interview", "Kids safety rules"],
        abstractions="""```text
AppDocument(app_id, title, keywords, category, quality_score)
InvertedIndex(term → postings)
QueryPlan(tokens, filters, locale)
Ranker(features[]) → blended score
TrendAggregate(day, bucket, dp_noisy_count)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Personal download history | Local features | Not raw export |
| Query string | Sent for search | Short TTL |
| Ranking personalize | Hybrid | Base index server |
| Autocomplete | Cache top prefixes | Edge |""",
        options=[("A. Long-lived user query profiles","High relevance","Privacy creep","Apple"),("B. Server index + short TTL + on-device features","Balanced","Less global personalize","— chosen"),("C. Pure on-device index","Private","Stale/ huge","No"),("D. Manual lists only","Safe","Poor discovery","No")],
        chosen="Regional inverted index with short-TTL query handling, on-device personalization features, blended ranking, and DP aggregate trends.",
        privacy="Queries not retained long-term; personalization from on-device App Store history; trends are DP aggregates.",
        consistency="Index eventually consistent; search reads snapshot version.",
        offline="Browse cached categories; search requires network.",
        battery="Client search API efficient; autocomplete debounced.",
        region="Per-storefront index shards; geo routing.",
        abuse="Keyword spam detection; install fraud signals; rate limits.",
        diagram="""```text
Client (local features) → Search API → Query Parser
                              ↓
                     Inverted Index Shard (locale)
                              ↓
                     Ranker + Policy + Ads slot
                              ↓
                     Results (short-lived query log → DP aggregates)
```""",
        designed="App Store search with sharded inverted index, privacy-safe query TTL, on-device personalization signals, blended ranking, and anti-abuse quality signals.",
        tradeoffs=[("Personalization vs privacy","On-device features","Trust"),("Ads vs organic","Separate auction","UX clarity"),("Freshness vs index cost","Incremental","Lag"),("Exploration vs exploitation","5% slots","Discovery")],
        path="MVP: inverted index + ranker. Scale: regional shards, ANN hybrid, on-device re-rank.",
        risks=["Keyword abuse arms race", "Over-logging queries", "Kids filter errors", "Latency regressions"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Store forever every search | TTL + aggregates |
| 1B queries × 1MB logs | Queries are bytes; logs minimized |""",
        bottlenecks="""1. Autocomplete QPS  
2. Index freshness pipeline  
3. Ranking feature computation  
4. Regional shard hot terms  
5. Ads auction latency""",
        estimation=std_estimation("Search queries", "1B/day", "small query/response", "5× peak"),
    ),
    S(
        title="Apple Arcade Game-Progress Synchronization",
        filename="arcade-game-progress-sync-system-design.md",
        focus="Game saves · Conflict resolution · Offline play · iCloud saves · Anti-cheat · Privacy · Battery",
        goal="**bound Arcade save sync**—sync game progress across devices with offline play and minimal cheating surface.",
        scope="Design Apple Arcade game progress sync: encrypted save blobs, conflict policies per game, offline play, server authoritative checkpoints where needed, and battery-aware background uploads.",
        entity="game_id / player_id",
        sync_primitive="Versioned save blob log",
        fr=[("F1","Saves?","Checkpoint files","Blob + metadata"),("F2","Offline?","Full play offline","Queue upload"),("F3","Conflicts?","Per-game policy: latest checkpoint or merge","Developer SDK"),("F4","Anti-cheat?","Signed checkpoints optional","Server validate"),("F5","Multi-device?","Continue on iPad","Sync on launch"),("F6","Size?","1–10 MB saves","Compress"),("F7","Privacy?","No gameplay analytics raw default","Opt-in"),("F8","Family?","Separate saves per Apple ID","No share"),("F9","Delete?","Remove save on uninstall","Tombstone"),("F10","Resume?","Mid-level","Quick save local"),("F11","Latency?","Fetch on launch","Background prefetch optional"),("F12","Cross-platform?","Apple devices only","Same stack")],
        mvp=["Save blob upload/download API", "Version vector per save slot", "Conflict policy SDK hooks", "Offline local save + queue", "Launch-time fetch", "Encrypted at rest", "Basic anti-tamper checksum"],
        outmvp=["Full server authoritative game state for all genres", "Cross-player sync"],
        nfr=[("N1","Privacy","Saves user-owned","Encrypted optional"),("N2","Launch fetch","p50 < 2s","Small saves"),("N3","Offline"," indefinite","Local always works"),("N4","Integrity","Detect tamper","HMAC optional"),("N5","Battery","Upload on background","Coalesce"),("N6","Consistency","Per-game","Document policy"),("N7","Availability","99.9%","Play offline"),("N8","Fairness","Anti-cheat genre-dependent","Leaderboards separate")],
        happy=["Play on iPhone offline → save local → upload on Wi‑Fi → iPad fetch on launch → continue", "Conflict two devices → SDK picks latest timestamp", "Uninstall → save tombstone", "Signed checkpoint for competitive mode validates"],
        edges=[("Huge world save","Chunk or compress"),("Corrupt save","Fallback previous version"),("Clock cheat","Server time in signed mode"),("Launch before upload completes","Use local"),("Account switch","Isolate saves"),("Developer breaking schema","Version field"),("Low storage","Evict after cloud ACK"),("Cheat upload","Reject signed")],
        scales=[("Players", "50M", "100M", "150M", "200M"), ("Save uploads/day", "200M", "1B", "5B", "10B"), ("Avg save", "2 MB", "3 MB", "4 MB", "5 MB"), ("Launch fetches/day", "300M", "1.5B", "7B", "14B"), ("Games", "500", "1K", "2K", "3K"), ("Save versions kept", "3", "5", "5", "5"), ("Offline sessions/day", "100M", "500M", "2B", "4B"), ("Signed checkpoint/day", "10M", "50M", "200M", "500M")],
        jumps=[("10×","Regional save blobs; CDN"),("100×","Prefetch popular saves; delta compression"),("1,000×","Genre-specific anti-cheat services")],
        constraints=["Games own semantics; platform provides transport", "Not designing game engine"],
        abstractions="""```text
SaveSlot(game_id, player_id, slot_id, version)
SaveBlob(ciphertext, checksum, schema_v)
ConflictPolicy(LWW | server | custom merge)
LaunchSync(fetch_on_start, prefetch)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Gameplay | Local | — |
| Save file | Read/write | Stores versioned blob |
| Conflict pick | SDK + policy | May arbitrate signed |
| Encrypt | Optional client | At rest AES |""",
        options=[("A. Server authoritative sim state","Strong anti-cheat","Not all genres","Some games"),("B. Versioned blob sync + policies","General","Trust client more","— chosen"),("C. No sync","Simple","Bad UX","Arcade"),("D. Realtime sync","MMO","Complex","Out of scope")],
        chosen="Versioned encrypted save blobs with per-game conflict SDK policies and optional signed checkpoints for competitive titles.",
        privacy="Save content not mined for ads; telemetry opt-in separate.",
        consistency="Per-slot version vector; LWW default; developer override.",
        offline="Local save authoritative until upload; merge on sync.",
        battery="Upload after session end on Wi‑Fi; coalesce small saves.",
        region="Regional blob store; home cell metadata.",
        abuse="Signed saves; rate limits; anomaly detection on leaderboards.",
        diagram="""```text
Game Client → Local Save → Upload Queue → Save Blob Store
                ↓ launch fetch
         Other Device Game Client
Optional: Signed Checkpoint Validator
```""",
        designed="Arcade save sync via versioned blobs, offline-first play, launch fetch, per-game conflict policies, optional signed anti-cheat checkpoints.",
        tradeoffs=[("Blob vs server state","Blob default","Genre fit"),("LWW vs merge","Developer choice","UX"),("Encrypt saves","Optional","Performance"),("Prefetch","Faster launch","Bandwidth")],
        path="MVP: blob sync + LWW. Scale: CDN, deltas, signed modes for competitive.",
        risks=["Save corruption", "Clock cheat", "Large save bandwidth", "Wrong conflict policy"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Server plays game for you | Only validates signed checkpoints optionally |
| Sync every frame | Checkpoint blobs only |""",
        bottlenecks="""1. Launch fetch latency  
2. Save size uploads  
3. Version retention storage  
4. Conflict UX  
5. Cheat detection false positives""",
        estimation=std_estimation("Save uploads", "200M/day × 2 MB ≈ 400 TB/day", "2–5 MB", "evening peaks"),
    ),
    S(
        title="Low-Power Bluetooth Beacon Relay",
        filename="bluetooth-beacon-relay-system-design.md",
        focus="BLE mesh relay · Find My class · Battery · Privacy · Rotating IDs · Duty cycle · Offline",
        goal="**bound beacon relay**—extend range of low-power beacons via phone relays without exposing user identity or draining battery.",
        scope="Design a low-power Bluetooth beacon relay network (Find My / accessory class): minimal duty cycle advertisements, encrypted uplink reports, relay phone batch uploads, privacy rotations, and strict battery budgets.",
        entity="beacon_id",
        sync_primitive="Encrypted sighting reports",
        fr=[("F1","Beacon?","Coin cell accessories","Slow adv"),("F2","Relay?","Nearby phones forward","Opt-in OS feature"),("F3","Privacy?","Rotating beacon IDs","No owner track relay phone"),("F4","Payload?","Encrypted location/time","Owner decrypt"),("F5","Duty cycle?","ms级 adv interval sparse","Battery months"),("F6","Relay battery?","Batch uploads","Coalesce"),("F7","Range?","Extend via mesh hops","One hop typical"),("F8","Abuse?","Rate limits","Flooding filters"),("F9","Lost item?","Owner fetch","Same as Find My"),("F10","Android relay?","Out of MVP","Apple network"),("F11","Indoor?","Coarse location","Wi‑Fi/BT fusion on relay phone"),("F12","Firmware?","OTA signed","Accessory updates")],
        mvp=["Sparse BLE advertisements", "Rotating public keys", "Relay phone encrypted report upload", "Owner-side decryption", "Duty cycle enforcement", "Batch relay uploads", "TTL report store"],
        outmvp=["Multi-hop mesh with guaranteed delivery", "Continuous high-rate tracking"],
        nfr=[("N1","Beacon battery","12+ months","µA average"),("N2","Relay impact","< 1% daily phone battery","Batching"),("N3","Privacy","No plaintext location server","E2E"),("N4","Latency","Minutes","Crowd dependent"),("N5","Scale","Billions sightings/day","Ingest shards"),("N6","Integrity","Signed adv","Replay window"),("N7","Durability","TTL hours-days","Not archive"),("N8","Safety","Stalker alerts","On-device")],
        happy=["Beacon advertises → passerby phone uploads encrypted sighting → owner sees update", "Sparse adv preserves battery", "Relay batches 20 sightings one radio wake", "Rotating keys prevent tracking beacon owner via fixed ID"],
        edges=[("No relays rural","Stale last seen"),("Adv collision dense","Random backoff"),("Malicious relay flood","Rate cap"),("Beacon reset","New key enrollment"),("Phone offline","Delayed upload"),("Firmware bug","OTA rollback"),("Legal disable region","Geo policy"),("Tiny battery low","Reduce adv rate")],
        scales=[("Beacons active", "200M", "500M", "1B", "2B"), ("Sightings/day", "5B", "50B", "200B", "500B"), ("Avg report", "180 B", "200 B", "220 B", "250 B"), ("Relay phones", "500M", "1B", "2B", "3B"), ("Adv interval sec", "2", "3", "4", "5"), ("Batch size", "10", "20", "30", "40"), ("TTL hours", "24", "24", "12", "12"), ("OTA/day", "10K", "50K", "200K", "500K")],
        jumps=[("10×","Ingest sharding"),("100×","Geo TTL partitions"),("1,000×","Adaptive adv schedules by crowd density")],
        constraints=["Coin cell power dominates design", "Same privacy bar as Find My"],
        abstractions="""```text
BeaconAdv(rotating_pubkey, battery_status)
SightingReport(enc_location_time, beacon_key_id)
RelayBatch(reports[], relay_anon_id)
DutySchedule(interval, jitter)
```""",
        split="""| Concern | On-device (relay) | Server |
|---------|-------------------|--------|
| Location fix | Relay phone GPS/Wi‑Fi | Never plaintext |
| Upload | Batch when on network | Store encrypted |
| Beacon adv | Accessory firmware | — |
| Owner map | Owner decrypt | Serves blobs |""",
        options=[("A. Fixed MAC beacon","Simple","Trackable","No"),("B. Rotating keys + encrypted relay","Private","Complex","— chosen"),("C. Continuous scanning phones","Fast","Battery death","No"),("D. Cellular in beacon","No relay","Power/cost","Tag size")],
        chosen="Sparse rotating BLE beacons with encrypted relay uploads batched on phones; owner decrypts; server blind.",
        privacy="Rotating IDs; encrypted reports; relay phone doesn't know owner identity.",
        consistency="Sighting reports append-only TTL; owner merges timeline.",
        offline="Beacon still advertises; relay uploads later.",
        battery="Sparse adv; relay batching; phone duty caps.",
        region="Global ingest; geo TTL.",
        abuse="Flood filters; stalker alerts.",
        diagram="""```text
Beacon ~~BLE~~> Relay iPhone --batch encrypted--> Ingest
                                              ↓
Owner iPhone fetch decrypt map
Duty cycle keeps coin cell alive months
```""",
        designed="Low-power beacon relay: sparse rotating BLE, encrypted sighting batches from relay phones, owner decryption, strict duty cycles for tag and phone battery.",
        tradeoffs=[("Adv rate vs find speed","Sparse default","Battery"),("Batch vs realtime upload","Batch","Phone battery"),("TTL vs history","Short","Privacy/storage"),("One-hop vs mesh","One-hop","Simplicity")],
        path="MVP: rotating keys + relay batch. Scale: sharded ingest, adaptive schedules.",
        risks=["Battery underestimate", "Stalking", "Rural coverage", "Flooding"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Phone relays 24/7 scan | Duty capped |
| 5B × 1KB = 5PB/day | ~1 TB/day at 200B |""",
        bottlenecks="""1. Ingest QPS  
2. Relay phone battery if batching fails  
3. Beacon coin cell peak current  
4. Key rotation  
5. Owner fetch fanout""",
        estimation=std_estimation("Sighting reports", "5B/day × 200 B ≈ 1 TB/day", "180–250 B", "3× peak"),
    ),
    S(
        title="Offline-First Reminders",
        filename="offline-first-reminders-system-design.md",
        focus="Local notifications · List sync · CRDT/LWW · Subtasks · Shared lists · Timezone · Battery",
        goal="**bound Reminders sync**—create and fire reminders offline with reliable multi-device sync and conflict resolution.",
        scope="Design offline-first Reminders: local notification scheduling, encrypted sync of lists/items/subtasks, recurrence rules, shared list ACLs, timezone-safe triggers, and battery-minimal background sync.",
        entity="list_id / reminder_id",
        sync_primitive="Encrypted reminder mutation log",
        fr=[("F1","Entities?","Lists, reminders, subtasks, tags","Tree + items"),("F2","Notify?","Local UNUserNotification","Schedule on-device"),("F3","Offline?","Full CRUD","Outbox sync"),("F4","Recurrence?","RRULE","Expand locally"),("F5","Shared lists?","Family/team","ACL + fan-out"),("F6","Conflicts?","LWW fields; OR-set subtasks","Explicit"),("F7","Location?","Geofence optional","On-device"),("F8","Attachments?","Optional small","Blob sync"),("F9","Completed?","Sync completion state","Tombstone or flag"),("F10","Timezone travel?","Recalc fire times","Local TZ"),("F11","Siri?","Parse intent local","Add reminder"),("F12","Widgets?","Read local DB","Same store")],
        mvp=["Local DB + notification scheduler", "Encrypted mutation log sync", "Recurrence expansion on-device", "LWW for title/due", "OR-set subtasks", "Shared list ACL basic", "Timezone recalc on travel"],
        outmvp=["Real-time collaborative editing like Notes", "Server-side notification delivery primary"],
        nfr=[("N1","Fire reliability","On-time local","OS alarm APIs"),("N2","Sync lag","< 60s active","Background"),("N3","Offline","Weeks OK","Outbox"),("N4","Battery","No poll","Push coalesce"),("N5","Privacy","E2E lists option","Encrypted"),("N6","Consistency","Eventual","Document merges"),("N7","Availability","Local always","Cloud 99.9%"),("N8","Shared lists","Minutes sync","OK")],
        happy=["Add reminder offline → local notify scheduled → sync on Wi‑Fi → iPad shows item", "Complete on watch → sync completion → phone clears", "Shared grocery list edits merge", "Travel TZ → fire times shift correctly", "Recurring daily alarm expands locally"],
        edges=[("Duplicate recurrence instances","Stable instance ids"),("Delete list with pending notifies","Cancel local alarms"),("Shared list leave","Revoke ACL"),("Clock change DST","Recalc"),("Geofence denied","Degrade to time-only"),("Large subtasks OR-set","Compact"),("Notification limit OS","Prioritize"),("Conflict due date","LWW")],
        scales=[("Users", "100M", "300M", "500M", "800M"), ("Reminders/user", "100", "150", "200", "250"), ("Mutations/day", "500M", "5B", "50B", "500B"), ("Local notifications/day", "2B", "20B", "200B", "2T"), ("Shared lists", "20M", "50M", "100M", "150M"), ("Geofence reminders", "50M", "100M", "200M", "300M"), ("Sync sessions/day", "150M", "1.5B", "15B", "150B"), ("Recurrence expands/day", "1B", "10B", "100B", "1T")],
        jumps=[("10×","Shard logs; debounce sync"),("100×","Snapshot baselines; shared list fan-out"),("1,000×","Hierarchical cursors")],
        constraints=["Notifications are OS-local; server doesn't fire alarms", "Timezone logic on-device"],
        abstractions="""```text
ReminderList(list_id, acl)
Reminder(id, title, due, recurrence, completed)
Subtask(id, parent_id, title, done)
NotificationSchedule(reminder_id, fire_ts local)
Mutation(op_id, entity, patch_enc)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Fire notification | Yes | No |
| Recurrence expand | Yes | — |
| Sync log | Apply locally | Home cell ordering |
| Geofence | CoreLocation | — |""",
        options=[("A. Server push notifications for all","Central","Offline fail","Reminders"),("B. Local schedule + sync state","Offline-first","Device must be present","— chosen"),("C. Email reminders","Works","Not product","No"),("D. CRDT only","Merge easy","Heavy","Hybrid")],
        chosen="Local notification scheduling with encrypted mutation log sync; LWW/OR-set merges; server never fires time alarms.",
        privacy="Reminder text encrypted under E2E option; server sees schedule metadata minimally.",
        consistency="Home cell `server_seq`; recurrence expanded independently per device from synced rules.",
        offline="Full CRUD; notifications from local DB; sync later.",
        battery="Coalesce sync; geofence minimal regions; no polling.",
        region="Home cell per account; shared lists fan-out.",
        abuse="Shared list invite limits; spam rate cap.",
        diagram="""```text
Reminders App → Local DB + NotificationScheduler
                    ↓
              Sync Agent ↔ Mutation Log
                    ↓
Other devices apply + reschedule local alarms
```""",
        designed="Offline-first Reminders with local alarm scheduling, encrypted sync, recurrence on-device, timezone-aware triggers, and shared list ACLs.",
        tradeoffs=[("Local vs server notify","Local fire","Offline"),("CRDT vs op-log","Op-log + rules","Simplicity"),("Geofence accuracy","OS geofence","Battery"),("E2E vs server search","E2E option","Privacy")],
        path="MVP: local notify + sync. Scale: shards, shared list fan-out, snapshots.",
        risks=["Missed alarms if OS kills", "TZ bugs", "Shared list conflicts", "Notification caps"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Server sends push at due time | Local scheduler |
| Sync every reminder change instantly | Debounced |""",
        bottlenecks="""1. Recurrence expansion CPU  
2. Geofence count limits  
3. Shared list fan-out  
4. Mutation QPS  
5. DST edge cases""",
        estimation=std_estimation("Reminder mutations", "500M/day", "200 B–1 KB", "3× morning"),
    ),
    S(
        title="Safari Reading List Synchronization",
        filename="safari-reading-list-sync-system-design.md",
        focus="Bookmark sync · Offline read · Reader cache · E2E metadata · Conflict · Battery · Low metadata",
        goal="**bound Reading List sync**—sync saved URLs and offline reader content across Apple devices with privacy and battery awareness.",
        scope="Design Safari Reading List sync: URL metadata sync, optional offline archive ciphertext, read/unread state, conflict resolution, and on-device reader rendering with background fetch scheduling.",
        entity="reading_list_id / item_id",
        sync_primitive="Encrypted item mutation log",
        fr=[("F1","Items?","URL, title, preview, read flag","Metadata small"),("F2","Offline?","Save reader archive optional","Encrypted blob"),("F3","Devices?","iPhone, Mac, iPad","Same account"),("F4","Privacy?","Browsing not broadly logged","Reading list explicit save"),("F5","Conflicts?","LWW read flag; duplicate URL merge","Stable item_id"),("F6","Preview fetch?","On-device or background","No server full page store plaintext"),("F7","Delete?","Tombstone","Sync hide"),("F8","Folders?","Optional tags","Set sync"),("F9","Share?","Share sheet export","Out of band"),("F10","Size?","Archive up to few MB","Wi‑Fi fetch"),("F11","Autodelete?","After read optional","Local policy"),("F12","Private browsing save?","Not synced","Separate")],
        mvp=["Save URL → local item → sync metadata", "Read/unread LWW sync", "Optional offline archive encrypt+upload", "Dedupe by canonical URL", "Tombstone delete", "Background fetch on Wi‑Fi", "Push coalesced sync"],
        outmvp=["Full history sync of all browsing", "Server-side page rendering farm under E2E"],
        nfr=[("N1","Privacy","User-initiated saves only","No passive log"),("N2","Sync lag","< 60s","Background"),("N3","Offline read","Cached archive","Local"),("N4","Battery","Defer archive fetch","Wi‑Fi"),("N5","Consistency","Eventual","LWW"),("N6","Storage","Quota per user","Evict old archives"),("N7","Availability","99.9%","Local list works"),("N8","Integrity","HTTPS fetch","Checksum archive")],
        happy=["Save on iPhone → sync → Mac Reading List shows item", "Mark read on Mac → iPhone unread clears", "Download archive on Wi‑Fi → read offline flight", "Delete syncs tombstone", "Duplicate URL merges to one item"],
        edges=[("Paywall page archive fail","Keep URL only"),("Huge page","Size cap"),("URL redirects","Canonicalize"),("Title fetch differs","LWW title"),("Archive corrupt","Re-fetch"),("Low storage","Evict oldest archive post-ACK"),("Login required page","Archive may fail—expected"),("RTL locales","Metadata UTF-8")],
        scales=[("Users", "100M", "200M", "300M", "400M"), ("Items/user", "200", "300", "400", "500"), ("Saves/day", "20M", "100M", "300M", "500M"), ("Archive downloads/day", "5M", "30M", "100M", "200M"), ("Avg metadata", "500 B", "600 B", "700 B", "800 B"), ("Avg archive", "1 MB", "1.5 MB", "2 MB", "2 MB"), ("Mutations/day", "50M", "300M", "1B", "2B"), ("Peak sync QPS", "20K", "100K", "500K", "1M")],
        jumps=[("10×","Shard logs; archive CDN ciphertext"),("100×","Snapshot baselines"),("1,000×","Aggressive archive eviction tiers")],
        constraints=["Only explicit saves—not full history sync", "Archive may be impossible for auth pages"],
        abstractions="""```text
ReadingItem(item_id, url_canonical, title, read, archive_ref?)
ArchiveBlob(ciphertext, fetched_at)
Mutation(op, item_id, fields)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Save action | User explicit | — |
| Fetch page archive | Background URLSession | Stores ciphertext if uploaded |
| Reader render | WebKit local | No |
| Sync metadata | Apply merges | Op log |""",
        options=[("A. Server stores plaintext pages","Reader anywhere","Privacy","Apple"),("B. Metadata sync + optional encrypted archive","Balanced","Fetch failures","— chosen"),("C. Sync all browsing history","Complete","Creepy","No"),("D. URL only no offline","Simple","Weak offline","Phase1 OK")],
        chosen="Explicit-save metadata sync with optional encrypted offline archives fetched on-device and uploaded as ciphertext.",
        privacy="Only user-saved URLs sync—not full history; archives encrypted optional.",
        consistency="Dedupe canonical URL; LWW read flag and title.",
        offline="Local list always; archive if prefetched.",
        battery="Archive fetch Wi‑Fi; coalesce metadata sync.",
        region="Regional blob store for archives.",
        abuse="Quota; size caps; no server-side scraping of arbitrary URLs for other users.",
        diagram="""```text
Safari Save → Local Reading DB → Metadata Sync Log
                    ↓ optional Wi‑Fi
              Fetch Page → Encrypt Archive → Blob Store
Other device ← sync ← apply read/unread
```""",
        designed="Reading List sync for saved URLs with encrypted optional offline archives, read/unread LWW, URL dedupe, and battery-aware archive fetching.",
        tradeoffs=[("Archive vs URL-only","Optional archive","Storage"),("E2E archive","Yes option","Server preview none"),("Fetch on save vs lazy","Lazy/Wi‑Fi","Battery"),("Dedupe strictness","Canonical URL","Merge UX")],
        path="MVP: metadata sync. Add encrypted archives + eviction policies.",
        risks=["Archive fetch failures", "Storage bloat", "URL canonicalization bugs", "Paywall pages"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Sync entire browsing history | Explicit Reading List only |
| Server reads page content under E2E | Ciphertext archive only |""",
        bottlenecks="""1. Archive fetch failures  
2. Blob storage per user  
3. Canonical URL edge cases  
4. Metadata sync QPS  
5. WebKit rendering differences""",
        estimation=std_estimation("Reading list", "50M mutations/day + 5M archives × 1 MB ≈ 5 PB/day? → 5e6×1e6=5e12 B=5 TB/day archives", "500 B meta", "3×"),
    ),
    S(
        title="Local DB with On-Demand Cloud Fetch",
        filename="local-db-on-demand-cloud-fetch-system-design.md",
        focus="Core Data / SQLite · CloudKit-style · Lazy hydration · Query pushdown · Cache · Privacy · Battery",
        goal="**bound lazy cloud DB**—keep authoritative local database with fetch records from cloud on demand, not full mirror.",
        scope="Design local DB with on-demand cloud fetch (CloudKit/Core Data sync class): local queryable cache, cloud as backing store, record-level fetch, encrypted fields, conflict resolution, and minimal radio use.",
        entity="record_type / record_id",
        sync_primitive="Record graph + fetch-on-miss",
        fr=[("F1","Model?","Typed records + relations","Schema registry"),("F2","Local?","Full query local cache subset","SQLite"),("F3","Fetch?","On miss or predicate subscription","Lazy"),("F4","Write?","Local first outbox","Upload async"),("F5","E2E?","Field-level encrypt optional","Server opaque"),("F6","Conflicts?","Record LWW + merge hooks","Per-type"),("F7","Delete?","Tombstone","Cascade rules"),("F8","Share?","CKShare class","ACL"),("F9","Pagination?","Cursor queries","Pushdown"),("F10","Indexes?","Local only","Cloud indexes metadata"),("F11","Migration?","Schema versions","Transform"),("F12","Background?","Prefetch subscriptions","Wi‑Fi")],
        mvp=["Local SQLite cache", "Record upload outbox", "Fetch-on-miss API", "Subscription predicates", "Conflict LWW per record", "Encrypted field support", "Tombstone sync"],
        outmvp=["Full SQL pushdown to cloud globally", "Instant full DB mirror initial"],
        nfr=[("N1","Query latency local","p99 < 10ms","Cached"),("N2","Fetch miss","p50 < 500ms Wi‑Fi","Network"),("N3","Offline","Read cached write queue","Yes"),("N4","Battery","Batch fetches","Coalesce"),("N5","Privacy","E2E fields","Optional"),("N6","Consistency","Eventual per record","Explicit"),("N7","Scale devs","Many apps use framework","Multi-tenant"),("N8","Storage local","Bounded cache","Eviction LRU")],
        happy=["App queries local → miss → fetch record → cache → return", "Local write → outbox → cloud ACK → other device subscription fetch", "Predicate subscription prefetches on Wi‑Fi", "Delete tombstone removes local+cache", "Encrypted field server blind"],
        edges=[("Cache eviction then miss","Refetch"),("Partial graph fetch","Follow references lazy"),("Conflict two fields","Field LWW"),("Huge record","Chunk fields"),("Schema breaking","Migration transform"),("Share revoke","Purge local share records"),("Query flood miss","Batch getRecords"),("Rate limit","Backoff")],
        scales=[("Apps using SDK", "500K", "1M", "2M", "3M"), ("Records total cloud", "50B", "200B", "500B", "1T"), ("Fetches/day", "1B", "10B", "100B", "1T"), ("Writes/day", "200M", "2B", "20B", "200B"), ("Avg record", "2 KB", "3 KB", "4 KB", "5 KB"), ("Local cache/ device", "50 MB", "100 MB", "200 MB", "500 MB"), ("Subscriptions/device", "10", "20", "30", "50"), ("Tenants", "500K", "1M", "2M", "3M")],
        jumps=[("10×","Batch fetch API; regional cells"),("100×","Subscription coalescing; cache admission"),("1,000×","Edge read replicas ciphertext")],
        constraints=["Framework for third-party apps—tenant isolation", "Not full SQL in cloud"],
        abstractions="""```text
Record(type, id, fields{}, version, parent_ref?)
LocalCache(lru, indexes local)
FetchPlan(miss_ids[], predicate_subs[])
OutboxMutation(record_id, delta)
CloudCell(shard by container)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Query execution | Local SQLite | Index metadata only |
| Record bytes encrypt | App optional | Stores ciphertext fields |
| Fetch on miss | Cache manager | Record store |
| Conflict | App callback | Version vectors |""",
        options=[("A. Full mirror sync","Simple queries","Disk/battery","Large apps"),("B. Lazy fetch + local cache","Efficient","Miss latency","— chosen"),("C. Cloud SQL primary","Powerful","Offline bad","Mobile"),("D. Manual REST only","Flexible","Reinvent sync","No")],
        chosen="Local SQLite authoritative for cached subset; cloud backing store; fetch-on-miss and predicate subscriptions; write-through outbox.",
        privacy="App chooses field encryption; server stores opaque; tenant isolation per container.",
        consistency="Per-record version; fetch merges; subscriptions push deltas.",
        offline="Cached reads; writes queued.",
        battery="Batch record fetches; subscription prefetch on Wi‑Fi.",
        region="Cloud cells per container; edge fetch.",
        abuse="Per-app quotas; rate limits.",
        diagram="""```text
App → Local SQLite → (miss) → Fetch API → Cloud Record Store
          ↓ write
       Outbox → Upload → Fan-out subscriptions → other devices
```""",
        designed="Local DB with lazy cloud fetch: cached SQLite, record-level on-demand hydration, outbox writes, subscriptions, optional E2E fields, LRU eviction.",
        tradeoffs=[("Mirror vs lazy","Lazy","Scale"),("Cache size","Bounded LRU","Miss rate"),("Field E2E","App choice","Query limits"),("Subscription granularity","Predicate","Battery")],
        path="MVP: fetch-on-miss + outbox. Scale: batch APIs, cells, edge cache.",
        risks=["Cache stampede", "Eviction thrash", "Conflict callbacks wrong", "Tenant noisy neighbor"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Cloud runs arbitrary SQL on plaintext | Record API not SQL |
| Mirror entire cloud DB on phone | Lazy subset |""",
        bottlenecks="""1. Fetch miss storms  
2. Outbox write QPS  
3. Subscription fan-out  
4. Local cache eviction  
5. Multi-tenant isolation""",
        estimation=std_estimation("Record fetches", "1B/day × 2 KB ≈ 2 TB/day", "2–5 KB", "5× peak"),
    ),
    S(
        title="Focus Mode Propagation Across Devices",
        filename="focus-mode-propagation-system-design.md",
        focus="State sync · Do Not Disturb · Filters · Privacy · Low latency · Calendar triggers · Battery · Family",
        goal="**bound Focus sync**—when user enables a Focus on one device, other devices reflect filters consistently and quickly.",
        scope="Design Focus Mode propagation: focus state and configuration sync across devices, integration with notifications/calendar/location triggers, privacy of app allowlists, low-latency sync, and battery-minimal updates.",
        entity="focus_profile_id",
        sync_primitive="Focus state + config mutation sync",
        fr=[("F1","State?","Active focus id + manual/auto","Small payload"),("F2","Config?","Allowlists, schedules, calendars","Encrypted sync"),("F3","Latency?","Other devices within seconds","Push priority"),("F4","Triggers?","Time, location, app, calendar","Local evaluate"),("F5","Override?","Manual always wins temporarily","TTL override"),("F6","DND integration?","Notification center filters","OS hook"),("F7","Share Focus status?","iMessage optional","Separate"),("F8","Work/personal?","Multiple profiles","List sync"),("F9","Privacy?","App allowlists sensitive","E2E option"),("F10","Watch?","Mirror phone or independent","Policy"),("F11","CarPlay?","Driving focus","Auto"),("F12","Family?","Not auto parent control","Separate Screen Time")],
        mvp=["Focus profile config sync", "Active focus state broadcast", "Push priority channel", "Manual override with TTL", "Local trigger evaluation", "Notification filter apply hook", "Encrypted allowlists"],
        outmvp=["Server-side notification filtering for all apps globally", "Employer remote force focus"],
        nfr=[("N1","Propagate latency","< 5s p95","Push + small payload"),("N2","Battery","Tiny updates","No poll"),("N3","Privacy","Allowlists encrypted option","Sensitive"),("N4","Consistency","Eventual","Manual override rules"),("N5","Offline","Local focus works","Sync later"),("N6","Availability","99.9%","Local filters cached"),("N7","UX","No flapping","Debounce auto triggers"),("N8","Security","No remote force by third party","User controlled")],
        happy=["Enable Work Focus on iPhone → Mac/iPad switch within seconds", "Calendar trigger starts Sleep focus locally on all devices", "Manual override disables auto until TTL", "Edit allowlist on Mac → sync → phone applies", "Watch mirrors phone focus state"],
        edges=[("Conflicting manual on two devices","LWW + manual priority"),("Auto trigger race","Debounce 30s"),("Push delay","Pull on unlock"),("Large allowlist","Compress diff"),("Delete profile","Tombstone + default"),("Timezone schedule","Local eval"),("CarPlay enter/exit","Driving focus"),("MDM do not disturb","Separate channel")],
        scales=[("Users with Focus", "100M", "200M", "300M", "400M"), ("Profiles/user", "5", "8", "10", "12"), ("State changes/day", "500M", "2B", "5B", "10B"), ("Config edits/day", "50M", "200M", "500M", "1B"), ("Devices/user", "3", "3.5", "4", "4"), ("Avg state payload", "200 B", "250 B", "300 B", "300 B"), ("Avg config", "5 KB", "8 KB", "10 KB", "12 KB"), ("Push priority/day", "500M", "2B", "5B", "10B")],
        jumps=[("10×","Coalesce config diffs"),("100×","Edge state cache"),("1,000×","Binary diff profiles")],
        constraints=["Focus is OS-integrated; server doesn't filter notifications directly", "User consent for sharing status"],
        abstractions="""```text
FocusProfile(id, allowlists, schedules, triggers)
FocusState(active_profile_id, manual?, override_until)
ConfigMutation(op, profile_id, diff_enc)
StateBroadcast(user_id, state, version)
```""",
        split="""| Concern | On-device | Server |
|---------|----------|--------|
| Apply DND filters | OS local | — |
| Evaluate triggers | Calendar/location local | — |
| Sync state/config | Apply | Relay ordered ops |
| Share status | Messages optional | Separate |""",
        options=[("A. Server filters notifications","Central","Privacy/latency","No"),("B. Sync state+config; local apply","Fast private","Requires push","— chosen"),("C. Poll every 10s","Simple","Battery","No"),("D. iCloud file drop profiles","Rare updates OK","State slow","No")],
        chosen="Low-latency encrypted sync of focus profiles and active state; each device applies filters locally; priority push for state changes.",
        privacy="Allowlists reveal app usage—encrypt configs; don't log plaintext lists server-side under E2E.",
        consistency="State LWW with manual override precedence; config op-log merge.",
        offline="Local focus continues; state reconciles on reconnect.",
        battery="Tiny payloads; push not poll; debounce auto triggers.",
        region="Home cell per user; global anycast API.",
        abuse="Only user's devices can set state; rate limit.",
        diagram="""```text
iPhone enables Work Focus → StateBroadcast → Push (priority)
                              ↓
Mac/iPad/Watch apply local Notification filters
Config edits via encrypted op-log (debounced)
Triggers evaluated locally per device context
```""",
        designed="Focus Mode propagation via encrypted profile sync and priority state broadcast; local trigger evaluation and notification filtering; manual override rules prevent flapping.",
        tradeoffs=[("Latency vs battery","Priority push small","Energy OK"),("Mirror vs independent Watch","Mirror default","UX"),("E2E allowlists","Yes option","Server blind"),("Auto vs manual","Manual wins","User trust")],
        path="MVP: state broadcast + config sync. Scale: diff compression, edge cache.",
        risks=["Flapping auto triggers", "Push delays", "Allowlist sensitivity", "Override races"],
        unit_traps="""| Claim | Truth |
|-------|-------|
| Server blocks notifications | Local OS applies |
| Poll focus state | Push + pull reconcile |""",
        bottlenecks="""1. Priority push volume  
2. Config diff size  
3. Trigger evaluation differences across devices  
4. Override race UX  
5. Watch mirror lag""",
        estimation=std_estimation("Focus state changes", "500M/day × 200 B ≈ 100 GB/day", "200–300 B state", "5× context switches"),
    ),
]
