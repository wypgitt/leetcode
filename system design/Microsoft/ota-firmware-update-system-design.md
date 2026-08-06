# System Design: OTA Firmware / Software Update for Vehicles & Devices

> **Focus areas:** Campaign orchestration · Signed artifacts · Staged rollout / canary · Bandwidth & CDN · Vehicle offline windows · Rollback · Safety interlocks · Fleet telemetry  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Microsoft themes:** Azure IoT Hub / Device Update patterns · Azure Blob + Front Door / CDN · Entra device identity · regional compliance · Azure Monitor / Event Hubs · security & signed updates

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

Goal: **bound the OTA product**—what “update” means (full image vs delta), safety constraints for vehicles/devices, and how campaigns scale from thousands to hundreds of millions of endpoints without melting the network or bricking fleets.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What devices? | Passenger vehicles + IoT gateways; ECUs or OS partitions | Device inventory, capability matrix, A/B slots |
| F2 | Artifact types? | Full images, delta patches, config packages, maps | Artifact store + content-addressed blobs; delta generators |
| F3 | Who initiates? | Cloud campaign; device pulls when eligible | Control plane (campaign) + device agent (pull/apply) |
| F4 | Targeting? | Model/year, region, VIN cohort, software baseline | Queryable device twin / tags; cohort selectors |
| F5 | Rollout policy? | Canary → rings → full; pause/abort; % gates | Staged deployment state machine + health gates |
| F6 | Signing? | Code-signing required; chain of trust to OEM root | Signature verify before apply; key rotation story |
| F7 | Download? | Resume, byte-range, CDN; cellular vs Wi‑Fi preference | Chunked download; bandwidth policies; resume tokens |
| F8 | Apply conditions? | Parked, SOC > X%, ignition off, temperature OK | Device-side interlocks; cloud cannot force unsafe apply |
| F9 | Rollback? | Auto-rollback on boot failure; last-known-good | Dual partition / A-B; health probe after reboot |
| F10 | Telemetry? | Download %, apply result, crash loops, version | Event pipeline; campaign dashboards |
| F11 | Compliance? | Region residency for logs; audit who approved campaign | Azure region cells; immutable audit log |
| F12 | Admin ops? | Pause, resume, abort, force-recall, redrive failed | Control-plane APIs + RBAC (Entra) |

**MVP functional scope (lock with interviewer):**

1. Register devices with identity, model, current version, capabilities.
2. Upload **signed** artifacts (full + optional delta) to blob storage.
3. Create **campaigns** with cohort selector + rollout rings + health gates.
4. Device agent: poll eligibility → download (resumable) → verify → apply under interlocks → report.
5. **A/B partitions** with automatic rollback on failed boot health check.
6. Campaign pause/abort; canary % before wave expansion.
7. Telemetry: version, campaign state, error codes; ops dashboard.
8. Auth: device certs (Entra / DPS-style); operator RBAC.

**Out of MVP (explicitly defer):**

- Live patching of running critical ECUs without reboot window  
- Peer-to-peer vehicle mesh dissemination (Phase 2 for parking lots)  
- Perfect real-time push to offline vehicles (pull + wake channels)  
- Binary delta generation algorithm internals (treat as offline pipeline)  
- OTA for every ECU simultaneously without orchestration limits  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Campaign control latency | Ops actions fast | Pause/abort p99 < 5s to control plane; device lag = next poll |
| N2 | Artifact durability | Never lose published package | Azure Blob RA-GRS / ZRS; immutable versions |
| N3 | Integrity | No unsigned / tampered apply | Verify signature + hash before write to inactive slot |
| N4 | Availability (control plane) | High for ops & eligibility | 99.9%+ multi-AZ; devices tolerate control-plane blips |
| N5 | Download success | High under flaky networks | Resume; retries; CDN; prefer Wi‑Fi |
| N6 | Safety | Never apply while driving (vehicles) | Hard device interlocks; cloud policy is advisory |
| N7 | Multi-region | Global fleets | Artifacts geo-replicated; campaign state **home cell** per OEM tenant |
| N8 | Scale | Millions → hundreds of millions devices | See scale table; cell + CDN architecture |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Ops uploads signed image v12 → creates campaign canary 1% → devices poll → eligible → download → park → apply → reboot → health OK → report SUCCESS → ring expands.
2. Device on cellular with “Wi‑Fi only for large packages” → defers download until Wi‑Fi → succeeds later.
3. Partial download, car powers off → resume with Range requests → complete.
4. Canary error rate exceeds gate → auto-pause → ops abort → no further expansion.
5. Apply fails boot health → automatic rollback to previous slot → report ROLLBACK.
6. Critical security recall → high-priority campaign, wider wake/notify, still respects safety interlocks for apply.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Unsigned or bad signature | Reject before flash; alert; do not brick |
| Disk full / slot write fail | Fail campaign attempt; keep running slot intact |
| Device offline for weeks | Remains targeted; applies when next online & eligible |
| Duplicate campaign assign | Idempotent device-campaign assignment; one active apply |
| Split-brain two campaigns | Priority + mutual exclusion; queue or supersede policy |
| CDN poisoned / wrong blob | Content hash mismatch → abort; pin by hash not by mutable URL alone |
| Thundering herd at campaign start | Jittered poll; token-bucket download admits; wave schedules |
| Rollback also fails | Mark device UNHEALTHY; roadside/service mode; do not loop forever |
| Operator fat-finger full rollout | RBAC + dual-approval for >X% or prod rings; rate-limit expansion |
| Clock skew breaks cert validity | Allow skew window; prefer device twin time sync |
| Delta base mismatch | Fall back to full image; never apply incompatible delta |
| Legal hold / region leave | Stop new downloads in region; drain in-flight per policy |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Devices (fleet) | 1M | 10M | 100M | 1B |
| Active models / SKUs | 50 | 200 | 1K | 5K |
| Concurrent campaigns | 20 | 100 | 500 | 2K |
| Peak eligibility polls / s | 5K | 50K | 500K | 5M |
| Peak download starts / s | 500 | 5K | 50K | 500K |
| Avg package size | 200 MB | 200 MB | 300 MB | 500 MB (mixed) |
| Delta size (when used) | 20 MB | 20 MB | 30 MB | 50 MB |
| Telemetry events / s | 10K | 100K | 1M | 10M |
| Artifacts stored | 5K | 50K | 500K | 5M |
| Regions (Azure) | 2 | 4 | 10 | 20+ |
| Ops users / tenants (OEM) | 5 | 20 | 100 | 500 |

**What each jump forces:**

- **10×:** CDN mandatory; poll jitter; campaign waves; device twin store sharded; Event Hubs for telemetry.
- **100×:** Regional artifact replicas; download admission control; cell-per-OEM or cell-per-geo; delta pipeline; wake/notification channel separate from heavy download.
- **1,000×:** Hierarchical campaigns (global policy → regional executors); P2P/edge caches optional; telemetry aggregation at edge; strict tenancy cells; cold device archival.

### 1.5 Etc. (Constraints & Assumptions)

- Devices have a **trusted agent** and secure boot / verified boot chain (we design cloud + agent protocol, not silicon).
- **Apply safety** is enforced on-device; cloud sends policy and eligibility.
- Single OEM tenant or multi-OEM SaaS on Azure—design multi-tenant from day 1 (`tenant_id`).
- Cellular costs matter: prefer Wi‑Fi / off-peak; budget caps per device.
- “Microsoft lens”: IoT Hub / Device Update–like control plane, Blob + Azure CDN/Front Door, Event Hubs, Entra RBAC, Key Vault for signing keys (HSM), Azure Monitor.

**Scope statement:**

> Design a multi-tenant OTA update platform for millions to billions of vehicles/devices: signed artifact publishing, cohort campaigns with canary/rings/health gates, resumable CDN downloads, device-side safety interlocks and A/B rollback, and telemetry-driven pause/abort—evolving through 10× / 100× / 1,000× with regional cells and admission-controlled fan-out.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split traffic classes (do not lump)

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Eligibility / twin poll | 5K QPS | 5M QPS | Tiny payloads; cacheable policy |
| Download byte traffic | see bandwidth | see bandwidth | Dominates cost |
| Telemetry ingest | 10K/s | 10M/s | Append-only; aggregate |
| Campaign control API | ~10 QPS | ~1K QPS | Low QPS, high criticality |
| Signature / metadata fetch | 500/s | 500K/s | CDN + edge cache |

**Critical insight:** At scale, **bytes downloaded** and **poll storms** dwarf control-plane QPS. Design CDN + jittered pull; never push multi-hundred-MB payloads through IoT Hub messages.

### 2.2 Bandwidth math

```text
Baseline: 500 download starts/s × 200 MB = 100 GB/s = 800 Gbps peak if synchronized
→ unacceptable as a simultaneous spike

With waves: 1% of 1M devices/day over 12 hours:
1e6 × 0.01 = 10,000 devices/day canary
10,000 × 200 MB / (12 × 3600) ≈ 46 MB/s ≈ 0.37 Gbps average canary — fine

Full fleet 1M × 200 MB = 200 PB? NO:
1e6 × 200e6 B = 2e14 B = 200 TB total campaign bytes
Over 7 days: 200 TB / (7×86400) ≈ 330 MB/s ≈ 2.6 Gbps average — OK with CDN

1,000× devices (1B) × 500 MB full image = 500e15 B = 500 PB if everyone full-pulls
→ deltas + regional caches + multi-week waves mandatory
If 80% use 50 MB delta: effective ≈ 0.2×500 + 0.8×50 = 100 + 40 = 140 MB avg
1B × 140 MB = 140 PB — still huge → staged over months + edge caches
```

**Unit check:** 1M × 200 MB = 200 × 10^12 B = **200 TB**, not PB. 1B × 200 MB = **200 PB**.

### 2.3 Poll / eligibility load

```text
Naive: 1M devices poll every 30s → 1e6/30 ≈ 33K QPS
Baseline table uses ~5K with smarter intervals (5–15 min) + jitter

1,000×: 1B / 300s avg ≈ 3.3M QPS polls
→ long-poll / push notify for “campaign available”, then pull details
→ edge caches for “no update” responses (CDN/ cached 304)
```

### 2.4 Storage

```text
Artifacts: 5K packages × avg 200 MB ≈ 1 TB (baseline hot)
With versions retained 50× → tens of TB
1,000×: 5M artifacts × 100 MB avg retained ≈ 500 PB? Only if all kept forever
→ lifecycle: keep N versions per model; cold archive; dedupe by content hash

Device twin: ~2 KB × 1M ≈ 2 GB
1B × 2 KB = 2 TB metadata — fine if sharded

Telemetry: 10K events/s × 300 B ≈ 3 MB/s → ~260 GB/day
1,000×: ~260 TB/day raw → aggregate + sample + hot/cold tiers
```

### 2.5 Memory (hot paths)

```text
Campaign assignment cache per region: millions of device_id → campaign_id
1M × 32 B ≈ 32 MB / region (fine)
100M × 32 B ≈ 3.2 GB / cell — shard by device_id

Download admission tokens: small; store in Redis/Azure Cache per region
```

### 2.6 Critical bottlenecks (rank ordered)

1. **Synchronized download storms** at campaign launch  
2. **Eligibility poll storms** from reconnecting fleets  
3. **Cellular cost / ISP peering** for large images  
4. **Bad canary escaping** without health gates  
5. **Telemetry firehose** during mass apply  
6. **Signing key / cert rotation** mistakes  
7. **Home-cell campaign writes** vs global read fan-out  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Tenant (OEM) → Models/SKUs → Device (identity, twin, slots)
Artifact (content_hash, signatures, size, type=full|delta|config)
Release (artifact set for a software train)
Campaign (selector, rings, gates, schedule, priority)
Assignment (device_id, campaign_id, state machine)
Attempt (download/apply try with error codes)
```

**Device assignment state machine:**

```text
TARGETED → ELIGIBLE → DOWNLOADING → DOWNLOADED → APPLYING → REBOOTING
 → SUCCEEDED | ROLLED_BACK | FAILED
Campaign: DRAFT → CANARY → ROLLING → PAUSED → COMPLETED | ABORTED
```

### 3.2 Options: push vs pull vs hybrid

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Cloud push full image via MQTT | Simple mental model | Huge messages; broker melt; offline | Packages > few MB |
| B. Device pull only (poll metadata) | Natural offline; CDN offload | Poll load; slower start | Need sub-second recall without notify |
| C. **Hybrid: notify + pull bytes** | Best of both | Two channels to operate | Team ships notify without authz |
| D. P2P swarm among vehicles | Saves WAN | Security, incomplete graphs | Regulated safety without strong attestation |

**Chosen path:** **Hybrid** — lightweight eligibility/notify (IoT Hub / pubsub), **byte-range download from Azure Blob via CDN/Front Door**, device-side verify/apply. P2P deferred.

### 3.3 Options: where campaign truth lives

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. Single global SQL | Easy transactions | Multi-region lag; scale ceiling | 100M+ devices, multi-OEM |
| B. Device-owned desired state only | Scales with IoT twin | Hard global dashboards/gates | Need fleet-wide pause in seconds |
| C. **Home-cell campaign store + regional executors** | Correct gates; regional download | More moving parts | Dual-active writers on same campaign |

**Chosen:** Campaign + assignment **single-writer home cell** per tenant (or geo); regional **download & telemetry** planes; twin desired/reported for device convergence.

### 3.4 Artifact integrity & signing

```text
Build system → sign with code-signing key in HSM (Azure Key Vault managed HSM)
→ upload to Blob with metadata: content_hash, signer_cert_chain, sbom ref
→ publish immutable version_id
Device: download → sha256 verify → signature verify against pinned OEM roots → apply
```

**Deal-breaker:** Mutable blob URL without hash pin; apply without verify; signing keys in app config.

### 3.5 Rollout rings & health gates

```text
Ring0: internal dogsfood (N devices)
Ring1: canary 0.1–1%
Ring2: 5% → 20% → 50% → 100%
Gates (examples):
  - crash_loop_rate < threshold
  - rollback_rate < threshold
  - success_rate > threshold over window W
  - no Sev-0 telemetry spike
On gate fail: auto PAUSED; alert; require explicit resume
```

**Expansion:** time-based + metric-based; never pure wall-clock full blast.

### 3.6 A/B slots & rollback

| Approach | Use when |
|----------|----------|
| A/B dual partition | Vehicles/OS images (default) |
| Recovery partition + golden | Constrained devices |
| In-place with backup file | Config-only packages |

**Invariant:** Running slot never partially overwritten; write inactive → switch boot pointer → healthcheck → commit; else revert pointer.

### 3.7 Delta vs full

| Concern | Choice | Why | Deal-breaker |
|---------|--------|-----|--------------|
| Bandwidth | Delta when base matches | 10× less bytes typical | Delta without base identity check |
| Correctness | Fallback to full | Base mismatch common in field | Force delta only |
| Pipeline | Offline delta generator | CPU heavy | Generating deltas on API path |

### 3.8 Multi-region & Azure placement

| Plane | Mode |
|-------|------|
| Artifact bytes | Geo-replicated Blob / regional caches / CDN POP |
| Campaign mutations | Home cell (Azure region) per tenant |
| Eligibility APIs | Regional frontends reading cached campaign snapshots |
| Telemetry | Regional Event Hubs → aggregate to home / analytics |
| Keys | Key Vault HSM regional with controlled replication |

**Deal-breaker:** Active-active dual writers expanding the same campaign rings without consensus.

### 3.9 Trade-off tables (memory / cache / queue / DB)

| Concern | Choice | Why | Deal-breaker alternative |
|---------|--------|-----|--------------------------|
| Artifact truth | Content-addressed Blob | Integrity + dedupe | Overwrite same path “latest” |
| Campaign truth | Relational / Cosmos + strict concurrency | Gates need transactions | Redis-only campaign state |
| Notify | IoT Hub / Service Bus | Offline-friendly | SMS to every car for metadata |
| Download admit | Regional token buckets | Protect origin & cellular | Unlimited parallel CDN pulls from one parking lot APN |
| Telemetry | Event Hubs + cold store | Volume | Sync write to SQL per event |
| “No update” | Edge cache / CDN | Kill poll DB | Every poll hits home SQL |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
  Ops (Entra RBAC)          Build / Signing (HSM)
        |                           |
        v                           v
 +--------------+            +------------------+
 | Campaign API |            | Artifact Publish |
 | (home cell)  |            | (immutable blob) |
 +------+-------+            +--------+---------+
        |                              |
        v                              v
 +-------------------+        +------------------+
 | Campaign Store    |        | Azure Blob +     |
 | assignments/rings |        | CDN / Front Door |
 +---------+---------+        +--------+---------+
           |                           |
           v                           |
 +-------------------+                 |
 | Policy Snapshot   |                 |
 | fanout to regions |                 |
 +---------+---------+                 |
           |                           |
           v                           v
 +-------------------+        +------------------+
 | Eligibility +     |<------>| Device Agent     |
 | Notify (IoT Hub)  |        | (vehicle/device) |
 +---------+---------+        +--------+---------+
           |                           |
           v                           v
 +-------------------+        Interlocks → Verify
 | Telemetry Ingest  |<------- Apply A/B → Report
 | (Event Hubs)      |
 +---------+---------+
           v
      Dashboards / Gates / Auto-pause
```

### 4.2 Sequence: canary → expand

```text
Ops          Campaign Svc        Gate Evaluator       Devices
 |--create--> DRAFT
 |--start---> CANARY (1%)
 |                |-- assignments --> targeted devices
 |                |                      | poll/notify
 |                |                      | download/apply
 |                |<---- telemetry ------|
 |                |-- metrics window --->|
 |                |<-- PASS -------------|
 |                |-- expand ring 5% --->|
 |                |  FAIL → PAUSED ------|
```

### 4.3 Sequence: download resume + verify

```text
Agent                CDN/Blob              Local Storage
 |--GET manifest---->|
 |<-hash,sig,size----|
 |--GET Range 0-N--->|
 |<-bytes------------|-- write temp
 | (power loss)
 |--GET Range N-end->|
 |<-bytes------------|
 |--sha256+sig verify|
 |--write inactive slot
 |--wait interlocks
 |--switch boot + reboot
 |--healthcheck
 |--commit or rollback
```

### 4.4 Sequence: unsafe apply attempt

```text
Cloud: ELIGIBLE + priority HIGH
Agent: download OK, signature OK
Agent: speed > 0 OR not parked → defer APPLY (stay DOWNLOADED)
Agent: later parked + SOC OK → APPLY
```

### 4.5 Cells at 100×+

```text
                    +----------------------+
                    | Global Catalog       |
                    | (tenants, models)    |
                    +----------+-----------+
                               |
        +----------------------+----------------------+
        |                      |                      |
        v                      v                      v
   Home Cell A            Home Cell B            Home Cell C
   (OEM/Europe)           (OEM/US)               (OEM/APAC)
   Campaign writer        Campaign writer        Campaign writer
        |                      |                      |
        v                      v                      v
   Regional executors + CDN POPs + telemetry hubs (many)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Data loss prevention

- Artifact publish: upload → compute hash → write metadata row **committed** → only then mark RELEASED.  
- Campaign start: durable ring state before devices notified.  
- Device reports: at-least-once telemetry; campaign aggregates use idempotent event ids.  
- **RPO for artifacts ≈ 0** (geo-redundant storage). Campaign metadata synchronous commit in home AZ quorum.

#### 5.1.2 Retries & idempotency

| Operation | Idempotency key | Notes |
|-----------|-----------------|-------|
| Publish artifact | `content_hash` | Same bytes → same artifact_id |
| Assign device | `(device_id, campaign_id)` | Unique |
| Report result | `(device_id, campaign_id, attempt_id)` | Upsert |
| Download | byte ranges | Safe to repeat |

#### 5.1.3 Fencing / concurrency

- Campaign expansion uses **optimistic version** / etag on campaign row.  
- Device: only one APPLY at a time (mutex).  
- Abort sets `campaign_epoch++`; devices drop stale eligibility with old epoch.

#### 5.1.4 Rate limits & admission

- Per-region download token bucket (devices/sec and Gbps).  
- Per-APN / cellular carrier soft caps.  
- Poll rate limits; exponential backoff on 429.  
- Telemetry sampling under storm (always keep failures).

#### 5.1.5 Failure modes

| Failure | Mitigation |
|---------|------------|
| Origin Blob outage | CDN cache; multi-region origins |
| Bad build escapes canary | Gates + auto-pause + signed rollback package ready |
| Agent crash mid-flash | A/B ensures active slot intact |
| Home cell outage | Read-only eligibility from cache; no expansion; RTO via failover + fence |
| Clock / cert expiry | Overlap trust anchors; monitor not_after |

### 5.2 Scalability

#### 5.2.1 Traffic up / down

- **Scale up:** add CDN POPs, regional eligibility replicas, Event Hub throughput units, wave wider.  
- **Scale down:** lengthen poll intervals, shrink rings, pause non-critical campaigns, prefer deltas.  
- Autoscale eligibility frontends on QPS; download path is mostly CDN (elastic).

#### 5.2.2 Storage scale

- Content-addressed dedupe across releases.  
- Lifecycle policies: retain last K images per model.  
- Twin store shard by `hash(device_id)` or hub partitions.  
- Telemetry: hot 7–30 days, cold object/columnar.

#### 5.2.3 Parallelization

- Campaigns independent across tenants.  
- Within campaign, devices parallel with admission caps.  
- Delta generation farm parallel per baseline pair.  
- Gate evaluation periodic, not per-event blocking.

#### 5.2.4 Cells & progressive evolution

| Scale | Architecture |
|-------|--------------|
| 1× | Single region, Blob + CDN, IoT Hub, SQL/Cosmos campaign DB |
| 10× | Multi-AZ, sharded twins, Event Hubs, wave scheduler |
| 100× | Multi-region artifacts, home-cell campaigns, regional admitters |
| 1000× | Many cells, hierarchical policy, edge aggregation, optional P2P caches |

### 5.3 Maintainability

- Clear APIs: Artifacts, Releases, Campaigns, Devices, Telemetry.  
- Package format versioning (`manifest_version`).  
- Agent capability flags in twin (`supports_delta_v2`, `slot_count`).  
- Chaos tests: kill CDN POP, pause mid-campaign, revoke cert.  
- Audit: who approved expansion past 5%.  
- Feature flags for new apply strategies.  
- Separate **control plane** deploys from **agent** rollouts (agents are the hard part).

---

## 6. Wrap-Up

**What we built:** An Azure-friendly OTA platform: signed immutable artifacts on Blob/CDN, campaign home-cell control with canary rings and health gates, hybrid notify+pull device protocol, A/B apply with rollback, and telemetry-driven auto-pause—scaled via jitter, admission control, regional cells, and deltas.

**Strong interview lines:**

1. Bytes go through CDN; control messages stay small.  
2. Safety interlocks are on-device; cloud cannot override physics.  
3. Canary gates beat blind percentage rollouts.  
4. Content hash + signature before any flash.  
5. Progressive scale is about storms (polls/downloads), not just row counts.

**Risks to call out:** cellular cost, long-offline vehicles, rollback failure paths, signing key ops, multi-region campaign split-brain.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & safety

**Q: Can cloud force an update while driving?**  
A: No. Cloud marks eligible; agent enforces park/SOC/speed interlocks. Safety-critical.

**Q: How is this different from mobile app stores?**  
A: Bricking risk, dual partitions, regulatory recalls, larger images, intermittent connectivity, OEM tenancy.

**Q: Security patch vs feature OTA?**  
A: Shared pipeline; different priority, ring speed, and user consent policy.

### 7.2 Bandwidth & CDN

**Q: 100M cars × 200 MB day-one?**  
A: Refuse. Waves + deltas + Wi‑Fi preference + admission. Math: 20 PB if simultaneous—untenable.

**Q: Why not BitTorrent between cars?**  
A: Attractive at 1000× parking-lot density; needs attestation, encryption, and incentives. Defer unless pressed.

**Q: Origin shield?**  
A: Yes—CDN layers so Blob origin sees far fewer GETs.

### 7.3 Consistency & state

**Q: Device twin vs campaign DB — source of truth?**  
A: Campaign DB owns targeting/gates; twin owns desired/reported convergence for the device. Don’t dual-write conflicting truths.

**Q: Exactly-once apply?**  
A: At-least-once attempts; apply is made idempotent via slot version + campaign_epoch.

### 7.4 Memory / storage / DB

**Q: Store all telemetry in SQL?**  
A: Deal-breaker at 1M events/s. Use Event Hubs + cold analytics; SQL for campaign aggregates only.

**Q: Index devices for cohort queries?**  
A: Tags + inverted indexes / Cosmos queries on model, region, version, fleet tags. Precompute large cohorts into assignment partitions.

**Q: Redis for campaign state?**  
A: Cache yes; sole durable truth no.

### 7.5 Security & compliance

**Q: Where do signing keys live?**  
A: HSM/Key Vault; build pipeline signs; devices pin OEM roots; rotation with overlap.

**Q: Compromised CDN edge?**  
A: TLS + hash + signature; CDN cannot forge OEM signature.

**Q: GDPR / region residency?**  
A: Keep VIN-linked telemetry in-region; artifacts often global but metadata localized.

**Q: Secure device identity?**  
A: X.509 via DPS-like provisioning; rotate; revoke stolen vehicles’ credentials.

### 7.6 Algorithms

**Q: Jitter algorithm?**  
A: `next_poll = base + hash(device_id, campaign_id) % window` deterministic spread + random jitter.

**Q: Health gate evaluation?**  
A: Sliding window success/rollback rates with min sample size before expand.

**Q: Delta selection?**  
A: Pick newest delta where `from_version` matches device reported; else full.

### 7.7 Load balancing & hashing

**Q: Shard assignments?**  
A: `shard = hash(tenant_id, device_id) % N`; campaign jobs iterate shards.

**Q: Sticky eligibility?**  
A: Any regional frontend OK if policy snapshot versioned.

### 7.8 Comparison

**Q: vs Azure Device Update for IoT Hub?**  
A: Same shape: import update → group deployments → device agent. Interview expects you to reinvent principles, not product names alone.

**Q: vs Kubernetes rolling update?**  
A: Similar rings/gates; different: offline nodes, bandwidth, physical safety, A/B flash.

### 7.9 Failure drills

**Q: Canary silent failure (metrics lie)?**  
A: Multiple signals: crash, rollback, watchdog, synthetic probe fleet, customer cases.

**Q: Home cell failover mid-expansion?**  
A: Fence epoch; resume from durable ring cursor; expect duplicate notifies—devices idempotent.

### 7.10 Interview traps

| Trap | Pushback |
|------|----------|
| Push 200 MB through message broker | Wrong tool |
| Apply without signature | Safety/security fail |
| Global sync update Friday 5pm | Storm + risk |
| Redis-only campaign | Durability/gates lie |
| 1M×200MB=200PB | **200TB** |
| Cloud overrides driving interlock | Unacceptable |

### 7.11 Related Microsoft domains

**Q: How does this touch Teams / M365?**  
A: Usually doesn’t—unless device is Surface/IoT in enterprise. Frame as Azure IoT / automotive partner cloud.

**Q: Xbox / gaming console OTA?**  
A: Same bones; different consent UX and content packaging; still CDN + rings.

---

## 8. Appendices

### 8.1 API checklist

- [ ] `POST /artifacts` (register metadata + blob SAS)  
- [ ] `POST /releases`  
- [ ] `POST /campaigns` / `POST /campaigns/{id}/start`  
- [ ] `POST /campaigns/{id}/pause|resume|abort`  
- [ ] `POST /campaigns/{id}/expand` (or automatic)  
- [ ] Device: `GET /eligibility`, `POST /reports`  
- [ ] `GET /campaigns/{id}/metrics`  
- [ ] Admin audit export  

### 8.2 Schema sketches

```sql
devices(device_id, tenant_id, model, region, current_version,
        capabilities_json, cert_thumbprint, last_seen)

artifacts(artifact_id, tenant_id, content_hash PK, size, type,
          sig_ref, blob_uri, created_at)

campaigns(campaign_id, tenant_id, release_id, state, epoch,
          selector_json, ring_pct, policy_json, version_etag)

assignments(device_id, campaign_id, state, attempt, updated_at,
            PRIMARY KEY(device_id, campaign_id))

attempts(attempt_id, device_id, campaign_id, error_code,
         bytes_downloaded, started_at, ended_at)
```

### 8.3 Manifest sketch (device-facing)

```json
{
  "manifest_version": 2,
  "campaign_id": "c_123",
  "campaign_epoch": 7,
  "artifacts": [
    {
      "artifact_id": "a_9",
      "type": "delta",
      "from_version": "11.0.4",
      "to_version": "12.0.0",
      "size": 20971520,
      "content_hash": "sha256:...",
      "signature": "base64...",
      "urls": ["https://cdn/.../a_9"]
    }
  ],
  "apply_policy": {"require_parked": true, "min_soc": 0.2}
}
```

### 8.4 Invariants

1. Never flash without hash + signature success.  
2. Never overwrite the running slot in place.  
3. Campaign epoch monotonic; stale eligibility ignored.  
4. Gate fail ⇒ no automatic expansion.  
5. Publish is immutable; “latest” is a pointer, not a blob mutate.  
6. Assignment state transitions are CAS-protected.

### 8.5 Progressive scale playbook

| Scale | Must have |
|-------|-----------|
| 1× | Blob+CDN, signed manifests, A/B, basic campaign, telemetry |
| 10× | Jitter, waves, Event Hubs, twin sharding, pause/abort |
| 100× | Home cell, regional admitters, deltas, multi-region CDN |
| 1000× | Cells, edge agg, hierarchical campaigns, optional P2P cache |

### 8.6 Device agent loop (pseudocode)

```text
loop:
  sleep(jittered_interval) or wake_on_notify
  m = fetch_eligibility()
  if m.epoch < local.epoch: continue
  if m.none: continue
  ensure_download(m)           # resume ranges, verify hash/sig
  if not interlocks_ok(): continue
  if apply_inactive_slot(m) and reboot_and_health_ok():
     report(SUCCESS); commit_slot()
  else:
     rollback(); report(ROLLBACK|FAILED)
```

### 8.7 Ring expansion policy example

```text
min_sample = 500
window = 2h
expand if:
  success_rate >= 0.99
  rollback_rate <= 0.005
  crash_loop_rate <= 0.001
  and human approval if next_pct >= 0.5
else pause
```

### 8.8 Bandwidth budget worksheet

```text
campaign_bytes ≈ devices_targeted × avg_bytes_effective
avg_bytes_effective = p_delta×delta + (1-p_delta)×full
avg_gbps = campaign_bytes × 8 / (wave_seconds × 1e9)
require avg_gbps < regional_budget × safety_factor(0.5)
```

### 8.9 Telemetry event types

| Event | When |
|-------|------|
| `campaign.eligible` | Device sees assignment |
| `download.started/progress/completed/failed` | Bytes path |
| `apply.started/succeeded/rolled_back/failed` | Flash path |
| `health.boot_ok/boot_fail` | Post-reboot |
| `defer.interlock` | Park/SOC blocks |

### 8.10 Security checklist

- [ ] HSM-backed signing  
- [ ] Device attestation / cert rotation  
- [ ] TLS everywhere  
- [ ] RBAC + dual control for wide rollout  
- [ ] Immutable audit  
- [ ] SAS tokens short-lived for upload  
- [ ] Revocation list for compromised devices  

### 8.11 SLO examples

| SLO | Target |
|-----|--------|
| Manifest fetch p99 (online device) | < 500 ms regional |
| Canary gate decision freshness | < 2 min |
| Pause propagation to eligibility | < 5 s control plane; ≤ next poll on device |
| Undetected unsigned apply | 0 |
| Accidental full-blast without gate | 0 |

### 8.12 Interview 60-second summary

> OTA is a **campaign control plane** plus **device agents**. Artifacts are immutable, signed, CDN-delivered. Devices pull, verify, and apply only under safety interlocks with A/B rollback. Rollouts are ring-based with telemetry health gates and auto-pause. Scale pain is download/poll storms—solved with jitter, admission control, deltas, and regional cells; campaign mutations stay single-writer per tenant home cell on Azure.

### 8.13 Related systems map

```text
Build/Sign → Artifact Blob/CDN
                ↑
Ops → Campaign Store (home) → Policy Snapshots → Eligibility/Notify
                                ↓
                          Device Agent → A/B Apply
                                ↓
                          Telemetry → Gates → Pause/Expand
```

### 8.14 Explicit non-goals

- Designing ECU firmware internals  
- Cellular carrier contracts  
- Physical recall logistics  
- Perfect push delivery to powered-off ECUs without wake hardware  

### 8.15 Comparison: orchestration-only vs full OTA

| System | Focus |
|--------|-------|
| Device-update orchestration | Who/when/what percentage (fleet control) |
| This OTA design | + byte delivery, verify, apply, rollback, device interlocks |

Mention sibling orchestration prompt if interviewer scopes cloud-only.

### 8.16 Failure injection test plan

1. Corrupt bytes on CDN → agent hash fail, no apply.  
2. Kill agent mid-write → reboot to old slot.  
3. Spike rollback rate → auto-pause.  
4. Replay old manifest epoch → ignore.  
5. Dual campaign assign → priority/supersede rules hold.  
6. Home cell failover → fence + resume.  

### 8.17 Glossary

| Term | Meaning |
|------|---------|
| Twin | Desired/reported device document |
| Ring | Rollout cohort stage |
| Gate | Metric threshold before expand |
| A/B slot | Dual partition scheme |
| Campaign epoch | Fencing counter for abort/eligibility |
| Content-addressed | Keyed by hash of bytes |

---



### 8.18 Vehicle-specific interlock matrix

| Condition | Download allowed? | Apply allowed? |
|-----------|-------------------|----------------|
| Driving / speed > 0 | Yes (if policy) | **No** |
| Parked, SOC ≥ threshold | Yes | Yes |
| Low SOC | Wi‑Fi only / defer | **No** |
| Factory mode | Yes | Yes (special) |
| Battery thermal high | Maybe | **No** |
| User opt-out feature OTA | Policy | Policy |
| Critical security OTA | Prefer yes download | Still need park |

### 8.19 Campaign priority & supersede rules

```text
if new_campaign.priority > active.priority:
  supersede → mark old SUPERSEDED (if not APPLYING)
if APPLYING: finish or abort policy explicit (usually finish current)
security_recall priority = MAX
```

### 8.20 Cost model talking points

- CDN egress dominates variable cost.  
- Cellular may be OEM-billed—enforce Wi‑Fi preference.  
- Telemetry storage secondary but grows with fleet.  
- Delta generation compute is bursty—batch offline.

---

*End of OTA firmware / software update system design.*
