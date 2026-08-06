#!/usr/bin/env python3
"""Media docs batch: podcast, live, video-transcode, image, photo-album, CDN."""
from textwrap import dedent
from _gen_batch import write_spec, common_media_qs

def S(**kwargs):
    return kwargs

SPECS = []

SPECS.append(S(
name="podcast-platform-system-design.md",
title="Podcast Platform",
focus="RSS ingest · Long-form audio · Episode CDN · Subscriptions · Transcripts · Chapters · Offline · Analytics · Creator tools",
theme="Podcast platform (Spotify/Apple/Anchor-class)",
goal="design a **podcast platform**: show/episode catalog (RSS + native), global audio delivery, subscriptions, offline, transcripts/chapters, creator analytics, and discovery.",
is_not=[
["Job", "Podcast hosting + listening + discovery", "Music rights platform alone"],
["Ingest", "RSS pull + native upload", "Live radio regulatory system"],
["Lens", "Long episodes, transcripts, creator stats", "Short-form TikTok video"],
],
functional=[
["F1", "Ingest?", "RSS + native multipart upload", "Fetcher + upload service"],
["F2", "Playback?", "Audio via CDN; progressive/HLS audio", "CDN delivery"],
["F3", "Subscribe?", "Follow shows; new episode notify", "Sub graph + push"],
["F4", "Offline?", "Download episodes", "Device storage + optional DRM"],
["F5", "Transcripts?", "ASR + editor", "Async ASR pipeline"],
["F6", "Chapters?", "Time-marked sections", "Metadata sidecars"],
["F7", "Discovery?", "Search, categories, personalized", "Index + recs"],
["F8", "Analytics?", "Streams, listeners, geo for creators", "Event pipeline"],
["F9", "Monetization?", "Ads Dynamic Insertion optional", "DAI hooks"],
["F10", "Clips?", "Shareable snippets MVP optional", "Clip service"],
["F11", "Video podcasts?", "Optional video episodes", "Reuse video ladder lightly"],
["F12", "Payments?", "Subscriptions/paywalled shows optional", "Entitlement"],
["F13", "Moderation?", "Takedowns, copyright claims", "Safety queue"],
["F14", "Cross-app?", "OPML import", "Import tool"],
],
mvp=["RSS ingest + native upload", "Episode CDN play", "Subscribe + notify", "Search/browse", "Basic transcripts", "Creator download stats", "Offline download", "Chapters"],
out_mvp=["Full DAI marketplace", "Complete video-first product", "Global active-active writes"],
nfr=[
["N1", "RSS freshness", "Minutes for popular; hours long-tail"],
["N2", "Play start", "p50 < 500ms–1s"],
["N3", "Durability episodes", "Object store durable"],
["N4", "Notify latency", "Minutes after publish"],
["N5", "Transcript lag", "Hours OK initially"],
["N6", "Analytics delay", "Near-real-time dashboards eventual"],
["N7", "Availability", "99.9% listen path"],
["N8", "Cost", "Storage heavy (long audio); egress moderate"],
],
happy="Creator publishes → ingest → listeners notified → play/download → analytics.",
edges="malformed RSS; huge episode; host bandwidth steal; transcript fail; copyright music bed; flash crowd on celebrity drop.",
cases=[
["RSS 5xx", "Retry with backoff; keep last good enclosure"],
["Enclosure hotlink", "Prefer rehost/cache bytes on our CDN"],
["Duplicate GUID", "Idempotent episode identity"],
["Paywall episode", "Entitlement before URL"],
["Transcript poison audio", "Mark failed; manual retry"],
],
scales=[
["Shows", "100K", "1M", "10M", "50M"],
["Episodes", "1M", "20M", "200M", "1B"],
["MAU listeners", "5M", "50M", "200M", "500M"],
["Publish events/day", "10K", "100K", "1M", "5M"],
["Peak play Gbps", "20", "200", "2K", "10K"],
["ASR hours/day", "1K", "20K", "200K", "1M"],
["Notify fanout/day", "10M", "200M", "2B", "10B"],
["CDN hit", "85%", "92%", "97%", "99%"],
],
jumps="10× rehost+CDN+notify; 100× ASR fleet + creator analytics lake; 1,000× DAI + global catalog cells.",
constraints="RSS ecosystem quirks, creator portability, long retention, music licensing in beds.",
scope="Podcast platform: RSS/native ingest, durable episode audio on CDN, subscriptions/notifications, transcripts/chapters, discovery, creator analytics, offline—tolerant of messy RSS.",
estimates=[
("Storage", "200M episodes × 40 MB avg ≈ 8 EB? calibrate: 20M × 30 MB = 600 TB; rehost multiplies."),
("RSS poll", "1M feeds × poll/hour naive = huge; prioritize by popularity + PubSubHubbub/webhooks."),
("Notify fanout", "Celebrity show 5M subs × push = thundering herd → batch + collapse."),
("ASR cost", "1 hour audio ASR $; prioritize popular + creator-opt-in."),
("Analytics", "play heads every N sec → aggregate per episode."),
],
planes=[
["Ingest", "RSS/native → episode objects", "Idempotent"],
["Catalog", "Shows/episodes metadata", "Strong per show"],
["Delivery", "Audio CDN", "Immutable"],
["Social/sub", "Follows + notify", "Eventual fanout"],
["Intelligence", "ASR/chapters/recs", "Async"],
["Analytics", "Creator metrics", "Eventual"],
],
why_split="Unreliable external RSS must not block listening of already-cached episodes.",
components=["RSS Fetcher/Scheduler", "Native Upload", "Episode Store", "CDN", "Catalog", "Subscription/Notify", "Search", "ASR/Transcript", "Chapters", "Analytics", "Entitlement/Paywall", "Moderation", "DAI (optional)", "OPML import", "Creator Studio", "Recs"],
apis=dedent("""\
POST /shows (native)
POST /shows/{id}/episodes/upload
POST /shows/import_rss {url}
GET  /episodes/{id}/playback
POST /shows/{id}/subscribe
GET  /inbox/episodes
GET  /episodes/{id}/transcript
GET  /creator/stats?show_id=
"""),
data_model=dedent("""\
Show{id, title, rss_url?, owner}
Episode{id, show_id, guid, enclosure_path, duration, publish_at, status}
Subscription{user_id, show_id}
Transcript{episode_id, lang, path, status}
PlayAggregate{episode_id, day, starts, unique_listeners_approx}
"""),
tradeoffs=[
["Rehost vs hotlink", "Rehost popular", "QoE + control"],
["Poll vs push", "Hybrid", "Freshness vs cost"],
["ASR all vs popular", "Tiered", "Cost"],
["Notify", "Collapse batches", "Herd control"],
],
dealbreakers=[
["Poll all feeds every minute", "Ban/cost death"],
["Hotlink only forever", "Broken enclosures / poor QoE"],
["Per-subscriber sync notify storm", "Outage"],
],
mermaid=dedent("""\
flowchart TB
  RSS --> Fetcher --> Catalog
  Creator --> Upload --> Object[(Episode Objects)]
  Fetcher --> Object
  Object --> CDN
  Listener --> Playback --> CDN
  Listener --> Subs --> Notify
  Object --> ASR --> Transcripts
  Listener --> Analytics
"""),
sequences=[
("RSS publish", "Fetcher sees new GUID → download enclosure → store → catalog READY → enqueue notify + ASR."),
("Subscribe inbox", "User opens app → inbox query by subscribed show_ids ordered by publish_at → play."),
],
reliability=["Idempotent GUID/show; retries on RSS; durable raw enclosure; notify at-least-once with client dedup; ASR retry; takedown removes playback auth.",
"Rate-limit fetch per host; backoff 429/503.",
"Poison RSS XML quarantine.",
"Analytics exactly-once-ish via event_id.",
"Paywall URL signing short TTL.",
"Multi-AZ object store.",
"Replay fetcher from cursor.",
"Creator delete → GC with legal retention.",
"Chapter JSON validate.",
"Push provider failure → inbox pull still works."],
scalability=[["1×","Cron fetchers; single region CDN"],["10×","Priority fetch; rehost; push notify"],["100×","ASR fleet; analytics lake; shard inbox"],["1,000×","Global catalog cells; DAI; ML discovery"]],
maintainability=["RSS quirk compatibility layer", "Fetcher canaries", "Transcript model version pins", "Creator-facing SLO dashboards"],
deep_dives=[
("RSS realities", "GUID vs link identity; redirects; huge feeds; PubSubHubbub; per-host politeness."),
("Dynamic ad insertion", "SSAI for podcasts: stitch ad audio; tracking beacons; stale download conflict with ads freshness."),
("Inbox architecture", "Fan-in query vs per-user materialization; hybrid for celebrities."),
("Transcripts", "ASR → punctuation → speaker diarization optional → editor; serve WebVTT-like."),
("Progressive scale", "1× hosting → 10× CDN/notify → 100× ASR/analytics → 1,000× DAI/global."),
],
designed="Podcast platform with RSS/native ingest, CDN audio, subscriptions, transcripts/chapters, analytics, offline.",
decisions=["Rehost popular enclosures","Hybrid poll/push","Tiered ASR","Collapsed notify","Idempotent GUID","Inbox pull always works","Signed paywall URLs","Creator analytics aggregates"],
risks=["RSS ecosystem breakage","Notify herds","ASR cost","DAI vs offline","Copyright music"],
plan45=[["0–5","RSS vs native"],["5–15","Ingest+CDN"],["15–25","Subs/notify/inbox"],["25–35","Transcripts/analytics"],["35–45","Scale/DAI"]],
closer="**Podcast platform**: messy RSS tamed, durable CDN episodes, sane notify, tiered transcripts, creator truth in analytics.",
appendix_extra="### A1. Podcast notes\n\nOPML import; chapter markers; video podcasts as optional render; music bed scanning hooks.\n",
questions=common_media_qs([
("GUID vs URL identity?", "Prefer GUID; fallback link+pubDate; idempotent upsert."),
("Why rehost?", "QoE, longevity, DAI control, protect against origin die."),
("Notify 5M subs?", "Batch/collapse; inbox pull; push best-effort."),
("Offline vs DAI conflict?", "Downloaded episode may have stale ads; policy choices."),
("ASR prioritization?", "Creator opt-in + popularity + language."),
("Feed politeness?", "Per-host limits; respect 429; exponential backoff."),
("Unique listeners?", "HLL / daily sketches; not exact count."),
("Paywalled RSS?", "Tokenized enclosures; private feeds."),
("Chapter edits after publish?", "Version chapters; clients refresh metadata."),
("Spam shows?", "Reputation + abuse classifiers on ingest."),
]),
))

SPECS.append(S(
name="live-video-streaming-system-design.md",
title="Live Video Streaming",
focus="RTMP/WHIP ingest · Transcode · Low-latency packager · CDN · DVR · Chat hook · Recording · ABR live · Failover",
theme="Live video streaming (Twitch/YouTube Live-class)",
goal="design **live video streaming**: creators ingest live; viewers watch with low-latency ABR via CDN; optional DVR/recording; handle disconnects and spikes.",
is_not=[
["Job", "One-to-many live broadcast", "Zoom mesh conferencing"],
["Latency", "Seconds–low seconds class", "Teleop sub-100ms industrial"],
["Lens", "Ingest durability, LL-HLS/DASH, CDN fanout", "VOD archive alone"],
],
functional=[
["F1", "Ingest?", "RTMP/SRT/WHIP", "Ingest edge"],
["F2", "Transcode?", "Live ladder", "GPU/CPU live workers"],
["F3", "Package?", "LL-HLS / DASH / CMAF", "Packager"],
["F4", "CDN?", "Live-capable edge", "Short TTL segments"],
["F5", "DVR?", "Sliding window", "DVR store"],
["F6", "Record?", "VOD publish after", "Recording pipeline"],
["F7", "Chat?", "Hook only", "Separate chat system"],
["F8", "Auth?", "Stream keys", "Key rotation"],
["F9", "Latency modes?", "Normal vs low latency", "Tunable segments"],
["F10", "Failover?", "Backup ingest", "Redundant ingest"],
["F11", "Thumbnails?", "Live preview images", "Snapshotter"],
["F12", "ABR?", "Multi-rung live", "Ladder"],
["F13", "Geo?", "Global viewers", "Multi-region ingest/cdn"],
["F14", "Moderation?", "Live flags", "Kill switch"],
],
mvp=["Stream key auth","RTMP ingest","Live transcode 3–5 rungs","LL-HLS package","CDN delivery","Disconnect reconnect","Record to VOD basic","Kill switch"],
out_mvp=["Full interactive guest co-watch SFU","Perfect <1s glass-to-glass everywhere","Complete chat product"],
nfr=[
["N1", "Glass-to-glass", "3–10s normal; 1–3s LL mode targets"],
["N2", "Startup", "<2–3s join"],
["N3", "Ingest acceptance", "99.9% sessions start"],
["N4", "Viewer scalability", "Millions via CDN"],
["N5", "Recording durability", "No silent loss of highlights policy"],
["N6", "Key security", "Stream keys unguessable; rotatable"],
["N7", "Failover", "Backup ingest < seconds gap policy"],
["N8", "Cost", "Live encode concurrent $ dominates"],
],
happy="Go live → ingest → ladder → CDN viewers → end → VOD processing.",
edges="WiFi blip; bitrate spike; viral raid; packager crash; region failure; copyright mute; chat toxicity (hook).",
cases=[
["Ingest disconnect", "Reconnect window; slate/last-frame policy; resume"],
["Worker death", "Failover transcoder; brief discontinuity"],
["Viral 100× viewers", "CDN absorbs; protect origin packager"],
["Bad key leak", "Rotate key; kick old session"],
["Kill switch", "Hard stop distribute"],
],
scales=[
["Concurrent lives", "1K", "10K", "100K", "1M"],
["Viewers peak total", "100K", "2M", "20M", "100M"],
["Peak single stream viewers", "10K", "200K", "2M", "10M"],
["Ingest Gbps", "5", "50", "500", "5K"],
["Live encode slots", "1K", "10K", "100K", "1M"],
["Segment duration", "2s", "2s", "1–2s", "LL tuned"],
["DVR window", "30m", "2h", "24h", "policy"],
["Chat QPS hook", "10K", "200K", "2M", "20M"],
],
jumps="10× multi-region ingest+CDN; 100× transcoder autoscaling+hot stream isolation; 1,000× LL optimization+global TE.",
constraints="mobile uplink variance, codec device support, cost of always-on encode, abuse.",
scope="Live broadcast: authenticated ingest, live ladder+LL packaging, CDN fanout, reconnect/DVR/record, kill switch—optimize glass-to-glass vs stability.",
estimates=[
("Encode cost", "100K concurrent lives × 1 GPU-frac each impossible—tier: transcode popular; passthrough/limited ladder for long-tail."),
("Viewer fanout", "2M viewers × 3 Mbps = 6 Tbps CDN problem."),
("Segment rate", "1s segments × N rungs × viewers = immense small-object GETs — CDN essential."),
("Ingest entry", "Anycast ingest edges near creators; not one region."),
("Recording bytes", "Concurrent × bitrate × duration → object store."),
],
planes=[
["Ingest", "Accept creator bytes", "Session sticky"],
["Live process", "Transcode/package", "Stateful workers"],
["Delivery", "CDN live", "Short cache"],
["Control", "Keys, metadata, kill", "Strong"],
["Record/DVR", "Persist windows", "Durable"],
],
why_split="Stateful live workers must be isolated from mass viewer fanout (CDN).",
components=["Stream Key Auth","Ingest Edge (RTMP/WHIP)","Live Transcoder Pool","Packager LL","CDN Live","DVR Store","Recording→VOD","Thumbnail Snapshot","Director/Control API","Health/Alerting","Autoscaler","Kill Switch","Webhook to chat","QoE beacons","Origin Shield live","Multi-region failover"],
apis=dedent("""\
POST /live/streams → stream_id, ingest_url, stream_key
POST /live/streams/{id}/start|stop
GET  /live/streams/{id}/playback → manifest
POST /live/streams/{id}/rotate_key
POST /live/streams/{id}/kill
GET  /live/streams/{id}/dvr?t=
"""),
data_model=dedent("""\
LiveStream{id, owner, status, ingest_region, latency_mode}
IngestSession{id, stream_id, worker, started_at}
RenditionLive{stream_id, rung, packager_path}
Recording{stream_id, vod_asset_id, status}
"""),
tradeoffs=[
["Latency vs stability", "Tunable modes", "Product tiers"],
["Transcode all?", "Tier by popularity", "Cost"],
["LL-HLS vs WebRTC fanout", "LL-HLS/CDN for scale", "WebRTC for ultra-LL small audiences"],
["DVR", "Finite window", "Cost"],
],
dealbreakers=[
["Unicast origin to each viewer", "Meltdown"],
["Single ingest region global", "Latency + fragility"],
["No reconnect semantics", "Creator rage"],
["Long GOP with tiny buffer LL", "Artifacts / rebuffer"],
],
mermaid=dedent("""\
flowchart TB
  Creator --> IngestEdge --> Transcoder --> Packager --> CDN
  Packager --> DVR
  Packager --> Recorder --> VOD
  Viewer --> CDN
  ControlAPI --> IngestEdge
  ControlAPI --> Kill
  Player --> QoE
"""),
sequences=[
("Go live", "Create stream → OBS publishes RTMP → ingest auth → transcoder → packager manifests → CDN → viewers join."),
("Disconnect", "Ingest miss heartbeat → waiting state → reconnect same key → resume; else end after timeout → finalize recording."),
],
reliability=["Stream key hashing; rotate kills old","Worker lease + failover","Packager N+1","CDN short TTL + stale policies careful","Recording fsync checkpoints","Autoscaling predictive for events","Kill switch independent path","Backpressure if packager overload (reject new lives first)","Clock sync for LL","Poison uplink bitrate cap"],
scalability=[["1×","Few workers; cloud CDN live"],["10×","Regional ingest; autoscale GPU"],["100×","Hot stream dedicated packagers; multi-CDN"],["1,000×","Passthrough tiers; global TE; LL experimentation"]],
maintainability=["Latency mode configs","Encoder presets versioned","Game-day raid drills","Per-stream QoE dashboards"],
deep_dives=[
("LL packaging", "Partial segments, HTTP chunked transfer, shorter GOPs; player tune buffer."),
("Transcode economics", "Not all streams deserve 6 rungs; adaptive policy."),
("Hot stream isolation", "Dedicated packager/origin when viewers > threshold."),
("WebRTC vs CDN live", "WebRTC media servers scale poorly to millions; hybrid for co-hosts."),
("Progressive scale", "1× single region → 10× regional ingest → 100× hot isolation → 1,000× tiered encode."),
],
designed="Live streaming with auth ingest, live ladder, LL packaging, CDN fanout, DVR/record, failover, kill switch.",
decisions=["CDN fanout not origin unicast","Regional ingest","Tiered live ladders","Tunable latency modes","Hot stream isolation","Durable recording checkpoints","Independent kill switch","Reconnect windows"],
risks=["Encode $ blowup","LL instability","Key leaks","Regional outage","Copyright"],
plan45=[["0–5","Live vs VOD/Zoom"],["5–15","Ingest+transcode"],["15–25","Package+CDN+LL"],["25–35","Failover/DVR/record"],["35–45","Scale/cost"]],
closer="**Live video**: sticky ingest, tiered live encode, LL packaging, CDN fanout, reconnect/DVR, kill switch—latency vs cost explicit.",
appendix_extra="### A1. Live notes\n\nSRT for bad networks; WHIP for WebRTC ingest; slate on gap; raid/host mode as control events.\n",
questions=common_media_qs([
("Why not WebRTC to all viewers?", "SFU fanout cost/complexity; CDN HLS/DASH scales to millions."),
("Glass-to-glass budget?", "Capture+ingest+transcode+packager+CDN+player buffer — shave each."),
("Backup ingest?", "Dual publish; packager switch on failure; seamless optional."),
("Segment size vs LL?", "Shorter → lower latency, more overhead/rebuffer risk."),
("How to price encode?", "Tier ladders by viewers/popularity; passthrough long-tail."),
("DVR implementation?", "Retain last N segments in object store; playlist window."),
("Stream key security?", "High entropy; TLS ingest; rotate; bind IP optional."),
("GOP and ABR live?", "Keyframes aligned across rungs for clean switches."),
("Chat coupling?", "Async side channel; never block media path."),
("Recording exactly-once?", "Checkpoints + finalize idempotent VOD publish."),
]),
))

SPECS.append(S(
name="video-upload-transcoding-system-design.md",
title="Video Upload and Transcoding",
focus="Resumable upload · Mezzanine · Probe · Ladder encode · Package HLS/DASH · Thumbnails · Priority queues · DRM optional · QC",
theme="Video upload & transcoding pipeline",
goal="design the **video upload and transcoding pipeline** used under YouTube/Netflix-like products: resumable ingest, durable mezzanine, multi-rung encode, packaging, thumbnails, status, retries.",
is_not=[
["Job", "Ingest→process→artifacts READY", "Full consumer watch app UI"],
["Lens", "Jobs, idempotency, ladders, cost", "Feed ranking"],
],
functional=[
["F1", "Upload?", "Resumable multipart", "Upload service"],
["F2", "Probe?", "ffprobe metadata", "Probe step"],
["F3", "Ladder?", "Multi bitrate/codec", "Encode graph"],
["F4", "Package?", "HLS/DASH/CMAF", "Packager"],
["F5", "Thumbs?", "Sprites/posters", "Thumb job"],
["F6", "DRM?", "Optional CENC", "Key service"],
["F7", "Priority?", "Interactive vs batch", "Queues"],
["F8", "Notify?", "Webhooks/status API", "Callbacks"],
["F9", "QC?", "Black frames, loudness", "QC gates"],
["F10", "Re-encode?", "New codec rollout", "Replay from mezz"],
["F11", "Malware?", "Scan uploads", "Scanner"],
["F12", "Quotas?", "Per-tenant minutes", "Quota service"],
["F13", "Multi-region?", "Upload local", "Regional intake"],
["F14", "Partial publish?", "Min rung first", "Progressive enhance"],
],
mvp=["Resumable upload","Mezz store","Probe+ladder H.264","Package HLS","Thumbs","Job status API","Retries/idempotency","Min-rung publish signal"],
out_mvp=["Perfect perceptual shot-based everywhere","Full studio QC suite"],
nfr=[["N1","Upload resume","Flaky network OK"],["N2","Time-to-first-rung","Minutes for short video"],["N3","Durability mezz","11 9s class"],["N4","Exactly-once publish effect","CAS"],["N5","Tenant isolation","No noisy neighbor starve"],["N6","Observability","Per-job traces"],["N7","Cost","CPU/GPU hours tracked"],["N8","Security","Signed upload URLs"]],
happy="Upload complete → DAG runs → artifacts → READY webhook.",
edges="corrupt file; huge 4K; codec unknown; worker OOM; thundering reencode; tenant flood; packager mismatch.",
cases=[["Chunk retry","Idempotent ETag"],["One rung fail","Retry rung; publish others if policy"],["Re-drive","Same output keys overwrite safely"],["Quota exceed","Reject or queue defer"],["Poison","Quarantine"]],
scales=[["Jobs/day","10K","100K","1M","10M"],["Avg duration min","5","5","8","10"],["Peak jobs/s","2","20","200","2K"],["GPU workers","10","100","1K","10K"],["Storage TB/day","5","50","500","5K"],["Tenants","10","100","1K","10K"],["Webhook QPS","10","100","1K","10K"],["Reencode backlog hrs","1","5","20","100"]],
jumps="10× queue+autoscaling; 100× shard orchestrator+spot GPUs; 1,000× codec fleet efficiency+per-tenant fairness.",
constraints="ffmpeg versions, patent codecs, GPU availability, customer SLA tiers.",
scope="Upload/transcode platform: resumable bytes, durable mezz, idempotent ladder+package DAG, priorities/quotas, webhooks—mezz is source of truth for re-drives.",
estimates=[
("CPU hours", "100K jobs/day × 10 min media × 4× realtime encode ≈ huge — need parallel rungs + efficient presets."),
("Storage", "Mezz + packaged multiplier; lifecycle policies."),
("Queue depth", "Peak 10× avg; SLO on wait time per tier."),
("GPU vs CPU", "AV1 GPU; H.264 CPU; schedule by type."),
("Webhook storms", "Backoff + idempotent customer endpoints."),
],
planes=[["Upload","Bytes in","Idempotent chunks"],["Orchestration","DAG state","Strong job state"],["Workers","Encode/package","At-least-once"],["Artifact store","Outputs","WORM/versioned"],["Control","Quotas/keys","Strong"]],
why_split="Workers are fungible and crashy; job state machine must be authoritative.",
components=["Upload API","Object Store Mezz","Orchestrator/Workflow","Probe Workers","Encode Workers","Package Workers","Thumb Workers","QC Workers","KMS/DRM","Quota","Status/Webhook","Artifact Index","Priority Queues","Autoscaler","Admin Replay"],
apis=dedent("""\
POST /uploads → upload_id, urls
PUT  /uploads/{id}/parts/{n}
POST /uploads/{id}/complete → job_id
GET  /jobs/{id}
POST /jobs/{id}/retry
POST /webhooks/config
GET  /artifacts/{asset_id}
"""),
data_model=dedent("""\
Upload{id, tenant, size, status}
Job{id, asset_id, dag_version, state, priority}
Task{id, job_id, type, attempt, output_keys}
Artifact{asset_id, kind, path, checksum, codec, bitrate}
"""),
tradeoffs=[["DAG engine","Temporal/Step Functions/custom","Ops vs control"],["Spot GPUs","Yes with checkpoints","Cost vs restarts"],["Min publish","Yes","UX"],["Preset quality","Speed vs VMAF","SLA tiers"]],
dealbreakers=[["Non-deterministic output paths","Duplicate waste / broken publish"],["No mezz retention","Cannot reencode"],["Fairness ignored","Enterprise tenants melt"],["Sync encode in upload HTTP","Timeouts"]],
mermaid=dedent("""\
flowchart LR
  Client --> UploadAPI --> Mezz[(Mezz)]
  UploadAPI --> Orchestrator
  Orchestrator --> Probe --> Encode --> Package --> Thumbs
  Encode --> Artifacts[(Artifacts)]
  Package --> Artifacts
  Orchestrator --> Webhooks
  Quota --> Orchestrator
"""),
sequences=[
("Happy DAG", "complete() → create job → probe → parallel encodes → package → thumbs → QC → CAS READY → webhook."),
("Retry", "Task fails → attempt++ → same output key → success → continue DAG."),
],
reliability=["Chunk checksums","Deterministic keys","CAS READY","Poison quarantine","Tenant rate limits","Dead letter queues","Checkpoint long encodes","Webhook signed + retry","Multi-AZ state store","Idempotent admin replay"],
scalability=[["1×","Redis queue + worker pool"],["10×","Sharded queues; autoscale"],["100×","Workflow service; spot GPU; regional intake"],["1,000×","Cell per tenant tier; global reencode program"]],
maintainability=["Pin ffmpeg/image versions","Canary presets with VMAF","Migration: dual package versions","Cost attribution per tenant"],
deep_dives=[
("DAG design", "Tasks: probe, audio, video rungs parallel, package, thumbs, fingerprint hook, QC."),
("Priority/fairness", "WFQ across tenants; interactive lane."),
("Packaging", "CMAF; HLS+DASH; encryption optional."),
("Re-encode campaigns", "Replay mezz with new codec; progressive %."),
("Progressive scale", "1× workers → 10× queues → 100× workflow cells → 1,000× fleet efficiency."),
],
designed="Resumable upload + durable mezz + idempotent transcode/package DAG with quotas, webhooks, progressive publish.",
decisions=["Mezz source of truth","Deterministic artifact keys","Min-rung publish","WFQ fairness","Pinned toolchains","Signed webhooks","Spot+checkpoint","CAS READY"],
risks=["OOM on 8K","Preset regression","Queue poison","Webhook downtime","GPU shortage"],
plan45=[["0–5","Scope pipeline not app"],["5–15","Upload+mezz"],["15–25","DAG+idempotency"],["25–35","Packaging/DRM/QC"],["35–45","Fairness/scale/cost"]],
closer="**Upload/transcode**: resumable ingest, mezz truth, deterministic DAG artifacts, fairness, progressive READY.",
appendix_extra="### A1. Transcode notes\n\nLoudness targets; HDR path; audio language tracks; SSAI markers optional.\n",
questions=common_media_qs([
("Why mezzanine kept?", "Re-encode, new codecs, recover from bad presets."),
("How parallelize encode?", "Per-rung tasks; chunked encoding for long GOP segments with care."),
("Workflow engine choice?", "Managed vs custom — durability, timers, visibility."),
("Tenant fairness algorithm?", "Weighted fair queuing / token budgets on encode minutes."),
("Detect corrupt media?", "Probe + decode smoke; quarantine."),
("Package before all rungs?", "Publish subset; update manifests carefully/versioned."),
("GPU bin packing?", "Pack similar jobs; avoid fragmentation; migration."),
("Checksum strategy?", "Per-part upload + per-artifact content hash."),
("DRM key per asset?", "Key rotation policy; KMS envelopes."),
("SLA tiers?", "Separate queues + different presets."),
]),
))

# fix estimates tuple typo in video-upload - I used a list by mistake in one element
# Fix at runtime below

for i, sp in enumerate(SPECS):
    # normalize estimates if any list slipped in
    est = []
    for e in sp["estimates"]:
        if isinstance(e, list):
            est.append(tuple(e))
        else:
            est.append(e)
    sp["estimates"] = est
    write_spec(sp)
