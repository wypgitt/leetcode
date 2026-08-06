# System Design: Mobile Wallpaper Update at Boot

> **Focus areas:** Android lifecycle · Boot receivers / WorkManager · Persistence · Failure handling · Idempotency · Battery & Doze · Offline-first  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct lifecycle ownership, durable local state, explicit failure/retry budgets, deal-breakers for “just set wallpaper in `onCreate`” fantasies  
> **Interview theme:** Classic Meta mobile systems interview — reliability across process death, boot races, storage failures, and fleet scale config delivery

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: **bound the product**—an Android client capability that **updates device wallpaper after boot** (and on schedule/config push), with durable local persistence, correct lifecycle ownership, and principled failure handling. Server delivers wallpaper assets/config; the hard interview is the **mobile reliability plane**.

### 1.0 What this is / is not

| Dimension | **Wallpaper update at boot (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Apply correct wallpaper after reboot / policy change | Full wallpaper marketplace UX |
| Success | Idempotent apply; survive kill/boot races | Pretty animation demos |
| Persistence | Local state machine + asset cache | “Only in memory” |
| Failure | Retries, backoff, DLQ-equivalent local quarantine | Silent no-op forever |
| Scale | Millions of devices polling/pushing configs | Single-phone script |

**Scope statement:** Design an Android wallpaper-update-at-boot system: lifecycle-safe scheduling, durable persistence, asset download/apply, failure/retry, and fleet-scale config delivery.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | When update? | After boot + when new policy arrives | Boot path + push/poll path |
| F2 | Who owns wallpaper? | Home screen; lock screen optional | `WallpaperManager` scopes |
| F3 | Source of truth? | Server policy per user/device cohort | Config service + local cache |
| F4 | Offline? | Apply last downloaded asset if policy says so | Local asset store required |
| F5 | Formats? | JPEG/PNG/WebP; max resolution caps | Decode + downsample pipeline |
| F6 | User override? | User can pin custom; policy may respect opt-out | Preference flag in local DB |
| F7 | Multi-user Android? | Secondary users Phase 1.5 | Per-user storage dirs |
| F8 | Enterprise MDM? | Optional managed config | DevicePolicy hooks |
| F9 | Progress UX? | Silent background; notification on failure optional | WorkManager + notifications |
| F10 | Rollback? | Keep previous successful wallpaper bytes | Two-slot cache (current/prev) |
| F11 | Idempotency? | Same policy version → no re-apply | Versioned state machine |
| F12 | Telemetry? | Success/fail/latency/battery signals | Event pipeline |

**MVP functional scope:**

1. On `BOOT_COMPLETED` (or equivalent modern path), schedule wallpaper reconciliation work.  
2. Fetch latest wallpaper **policy** (URL, version, hash, apply window).  
3. Download asset if missing/corrupt; verify checksum.  
4. Apply via `WallpaperManager` on a **background worker**, not UI thread.  
5. Persist state: `IDLE | FETCHING | READY | APPLYING | APPLIED | FAILED`.  
6. Retry with exponential backoff; cap attempts; preserve last good wallpaper.  
7. Handle user opt-out and Doze/App Standby constraints.  
8. Emit telemetry for success, failure reason, apply latency.

**Out of MVP:**

- Live wallpaper engines / video wallpapers  
- Full marketplace browse UI  
- Perfect cross-OEM launcher quirks for every skin  
- On-device generative wallpaper ML  
- Lock-screen + home differentiated themes beyond basic API

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Apply reliability after boot | Must eventually apply | ≥99% success within 15 min online |
| N2 | Boot jank | Must not block boot UX | No heavy work on main; defer ≥ tens of seconds |
| N3 | Battery | Background friendly | WorkManager + constraints; no wake-lock abuse |
| N4 | Storage | Bounded cache | Max N assets / size quota (e.g. 50–100 MB) |
| N5 | Integrity | No corrupt apply | SHA-256 verify before set |
| N6 | Privacy | Assets may be user-specific | Auth tokens; no leak in logs |
| N7 | Server availability | Client resilient | Stale policy OK; last-good apply |
| N8 | Scale (fleet) | Meta-scale devices | CDN assets; config edge cache |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Device boots → worker runs → policy unchanged → checksum match → skip apply (idempotent).  
2. Device boots → new policy → download → verify → apply → mark `APPLIED(version)`.  
3. Online push of new wallpaper → enqueue unique work → apply without reboot.  
4. Offline boot → apply cached asset for current policy version.  
5. Apply fails once → retry → succeeds; telemetry records attempt count.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Process killed mid-download | Resume or re-download; partial file not applied |
| Process killed mid-apply | On next run detect incomplete; retry apply from verified file |
| Corrupt download | Checksum fail → delete → retry; never set |
| Disk full | Fail with `NO_SPACE`; trim cache; retry later |
| `WallpaperManager` security exception | Mark permanent fail for session; surface opt-in |
| OEM kills boot receiver | Prefer WorkManager + `BOOT_COMPLETED` enqueue; periodic reconcile |
| Doze / App Standby | Constraints: network + battery not low; exponential backoff |
| Rapid policy churn | Coalesce to latest version; cancel obsolete work |
| User set custom wallpaper | Respect override flag; don’t fight user every boot |
| Clock skew / future `apply_after` | Wait until wall clock ≥ apply_after |
| Huge image (50 MP) | Downsample to display metrics before set |
| Concurrent apply + user change | Single-flight lock; last writer = state machine owner |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active devices | 1M | 10M | 100M | 1B |
| Boots / day (fleet) | 1M | 10M | 100M | 1B |
| Policy fetches / day | 2M | 20M | 200M | 2B |
| Asset downloads / day | 100K | 1M | 10M | 100M |
| Avg asset size | 2 MB | 2 MB | 2–3 MB | 3 MB |
| CDN egress / day | 200 GB | 2 TB | 20–30 TB | 300 TB |
| Config QPS peak | 200 | 2K | 20K | 200K |
| Distinct wallpaper assets | 1K | 10K | 100K | 1M |
| Telemetry events / day | 5M | 50M | 500M | 5B |

**What each jump forces:**

- **10×:** CDN mandatory; config caching; WorkManager unique work names.  
- **100×:** Cohort staggered rollouts; delta policies; asset prefetch by cohort.  
- **1,000×:** Edge config; regional CDNs; aggressive client coalescing; sampling telemetry.

### 1.5 Etc. (Constraints & Assumptions)

- Target: modern Android (API levels agreed with interviewer); note OEM variance.  
- Direct boot / encrypted storage: wallpaper apply may wait until user unlock.  
- Server is config+CDN; we design client state machine deeply + server outline.  
- Wallpaper set requires appropriate permissions / role (app is system/partner or user-granted).

**Scope statement to repeat back:**

> Design an Android wallpaper update-at-boot system with lifecycle-safe scheduling (WorkManager), durable versioned persistence, checksummed asset cache with rollback slot, idempotent apply, failure/retry under Doze, and fleet-scale config/CDN delivery—scaling through staggered cohorts and edge caching.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes (critical)

| Class | What | Baseline peak | 10× | Plane |
|-------|------|---------------|-----|-------|
| **Boot reconcile** | Per boot worker | ~10–50/s avg; spiky mornings | ×10 | Client local |
| **Policy GET** | Config service | ~200 QPS peak | ~2K | Edge + config |
| **Asset GET** | CDN binary | ~20 QPS avg; bursty | ×10 | CDN |
| **Apply** | WallpaperManager | local only | local | Device |
| **Telemetry** | Success/fail | ~100/s | ×10 | Ingest |

**Anti-pattern:** treating “1M devices” as 1M simultaneous boot storms without cohort stagger math.

### 2.2 Boot storm math

```text
Assume 1M devices, 30% reboot in morning 2h window (optimistic extreme)
= 300K boots / 7200s ≈ 42 boots/s average
Peak 10× average ≈ 420 boots/s policy hits if uncached

With ETag / If-None-Match and 95% 304:
  origin config ≈ 21 QPS — fine
Without cache: 420 QPS origin — still OK at baseline; dies at 1000× without edge
```

### 2.3 Storage per device

```text
Two-slot cache: current + previous × 2 MB = 4 MB
Policy JSON + state DB: < 100 KB
Quota headroom for pending download: +2 MB
Total budget ≈ 8–16 MB recommended
```

### 2.4 Battery / CPU

```text
Decode 2 MB JPEG + set wallpaper ≈ tens–hundreds of ms CPU
Must not run on main thread during Activity resume
Defer post-boot by 30–120s random jitter to avoid thundering herd + boot contention
```

### 2.5 Failure budget

```text
Target: 99% apply success within 15 min if online
Assume 2% transient network fail → 3 retries with backoff covers ≈ 99.99% of transient
Permanent fails (permission, disk): surface once; don’t spin forever
```

---


### 2.6 WorkManager vs AlarmManager vs foreground service

```text
AlarmManager exact: Doze-hostile; OEM kills; not for reconcile
Foreground service: user-visible notification — overkill for wallpaper
WorkManager: constraints (net, battery), backoff, unique work, persist — MVP
Expedited work: use sparingly for user-visible “apply now”
```

### 2.7 OEM quirk budget

```text
Assume 5–15% devices on aggressive OEMs delay BG work hours
Mitigations: periodic daily reconcile, FCM high-priority sparingly,
  manufacturer-specific allowlist docs (product/legal), don’t spin in boot receiver
Telemetry by OEM/API level required to see silent failure clusters
```

### 2.8 Progressive capacity

| Resource | Baseline | 10× | 100× | 1,000× |
|----------|----------|-----|------|--------|
| Devices | 1M | 10M | 100M | 1B |
| Policy origin QPS | ~20 w/ ETag | edge | edge | multi-region edge |
| Asset downloads (change day) | low | cohort stagger | prefetch | regional CDN |
| Telemetry | 100/s | sample | sample | aggressive sample |

**Anti-patterns:** heavy work in BOOT_COMPLETED receiver; re-download every boot; 100% fleet flip; ignore Doze.

---

## 3. High-Level Design

### 3.1 Client components

| Component | Responsibility |
|-----------|----------------|
| `BootReconcileReceiver` | On boot, enqueue WorkManager unique work |
| `WallpaperReconcileWorker` | State machine: fetch → download → verify → apply |
| `PolicyStore` | EncryptedSharedPreferences / DataStore for policy+version |
| `AssetCache` | FilesDir slots `current`, `previous`, `staging` |
| `WallpaperApplier` | Calls `WallpaperManager`; catches security errors |
| `TelemetrySink` | Batched events |
| `OverridePrefs` | User opt-out / pin custom |

### 3.2 Server components (outline)

| Component | Responsibility |
|-----------|----------------|
| Config Service | `GET /v1/wallpaper/policy?device=&user=` |
| Asset CDN | Immutable URLs by content hash |
| Rollout Control | Cohort % , kill switch |
| Telemetry pipeline | Success rates by OEM/API |

### 3.3 Policy schema

```text
WallpaperPolicy {
  policy_version: int64,          // monotonic per cohort assignment
  asset_url: string,              // CDN HTTPS
  asset_sha256: string,
  asset_bytes: int,
  target: HOME | LOCK | BOTH,
  apply_after: timestamp,         // optional stagger
  expires_at: timestamp?,
  force: bool,                    // ignore user custom? usually false
  min_app_version: int
}
```

### 3.4 Local state machine

```text
States:
  UNKNOWN
  POLICY_STALE
  FETCHING_POLICY
  NEED_ASSET
  FETCHING_ASSET
  ASSET_READY
  APPLYING
  APPLIED(policy_version)
  FAILED_TRANSIENT(reason, attempts)
  FAILED_PERMANENT(reason)
  SKIPPED_USER_OVERRIDE
  SKIPPED_IDEMPOTENT

Transitions (happy):
  boot/enqueue → POLICY_STALE → FETCHING_POLICY → NEED_ASSET|ASSET_READY
  → FETCHING_ASSET → ASSET_READY → APPLYING → APPLIED
```

**Invariant:** Never transition to `APPLIED` without checksum-verified file and successful `setBitmap`/`setStream` return.

### 3.5 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Scheduling | **WorkManager** unique work | Survives process death; constraints | Fire-and-forget thread in `Application.onCreate` |
| Boot entry | Receiver **enqueues** work only | Fast; defer heavy | Decode wallpaper inside `BroadcastReceiver` |
| Persistence | DataStore/SQLite + file slots | Durable across kills | Memory-only flags |
| Apply thread | Background worker | Avoid ANR/jank | Main-thread `WallpaperManager` with large bitmap |
| Asset integrity | SHA-256 before apply | No corrupt wallpaper | Trust Content-Length alone |
| Updates | Version idempotency | No redundant applies | Re-apply every boot blindly |
| Rollout | Staggered cohorts + jitter | Protect CDN/boot | Instant 100% fleet flip |
| Offline | Last-good cache | Boot without network | Require network every boot |

### 3.6 API (server)

| Op | Semantics |
|----|-----------|
| `GET /v1/wallpaper/policy` | Returns policy; supports `If-None-Match` |
| `GET /cdn/assets/{sha256}` | Immutable asset bytes |
| `POST /v1/wallpaper/telemetry` | Batch client events |
| `POST /admin/rollout` | Cohort percentage / kill switch |

---


### 3.7 BOOT_COMPLETED & Doze deal-breakers

| Anti-pattern | Failure mode |
|--------------|--------------|
| Network in BroadcastReceiver | ANR / truncated work |
| Ignore battery constraints | OEM kill loops |
| No unique work name | Duplicate applies |
| Delete previous on any error | Unrecoverable blank/wrong wallpaper |
| Require unmetered always | Never applies on cellular-only users |

### 3.8 Direct Boot note

```text
Before user unlock: CE storage unavailable
Use device-protected storage only for minimal flags OR wait USER_UNLOCKED
WorkManager constraints: user-present / after unlock
```

---

## 4. Architecture Diagram

```text
                         +-------------------------+
   Device Boot --------> | BootReconcileReceiver   |
                         | (enqueue only, <10ms)   |
                         +------------+------------+
                                      |
                                      v
                         +------------+------------+
                         | WorkManager             |
                         | WallpaperReconcileWorker|
                         | (constraints + backoff) |
                         +------+------+-----------+
                                |      |
                +---------------+      +----------------+
                v                                       v
     +----------+-----------+                 +---------+----------+
     | PolicyStore          |                 | AssetCache         |
     | DataStore / SQLite   |                 | staging/current/   |
     | state machine        |                 | previous files     |
     +----------+-----------+                 +---------+----------+
                |                                       |
                | HTTPS                                 | HTTPS
                v                                       v
     +----------+-----------+                 +---------+----------+
     | Config Service       |                 | CDN (assets)       |
     | edge-cached JSON     |                 | immutable by hash  |
     +----------+-----------+                 +--------------------+
                |
                v
     +----------+-----------+
     | Rollout Control      |
     | cohorts / killswitch |
     +----------------------+

     WallpaperApplier --> WallpaperManager (HOME/LOCK)
     TelemetrySink -----> Telemetry Ingest --> dashboards
```

**Boot path sequence:**

```text
BOOT_COMPLETED
  -> jitter delay (WorkManager initial delay)
  -> load local state
  -> if user_override && !policy.force: SKIPPED_USER_OVERRIDE
  -> GET policy (ETag)
  -> if version == APPLIED version && file ok: SKIPPED_IDEMPOTENT
  -> if asset missing/bad: download to staging -> checksum
  -> rename staging -> current (keep previous)
  -> APPLYING -> WallpaperManager.setStream
  -> APPLIED(version) + telemetry
```

**Failure path:**

```text
error
  -> classify TRANSIENT vs PERMANENT
  -> TRANSIENT: attempts++ ; Result.retry() with backoff
  -> PERMANENT: FAILED_PERMANENT; notify optional; stop
  -> never delete `previous` on failed apply
  -> on success of new: previous = old current
```

**Push/update path (no reboot):**

```text
FCM / config sync
  -> enqueue UniqueWork("wallpaper-reconcile", REPLACE)
  -> same worker as boot (single code path)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Single-flight:** at most one reconcile worker logical owner (unique work name).  
2. **Checksum gate:** no apply without `sha256(file) == policy.asset_sha256`.  
3. **Two-slot safety:** failed apply never destroys last known good file.  
4. **Idempotent apply:** same `policy_version` + valid current file → no-op.  
5. **Boot receiver is thin:** only enqueue; no network/decode.  
6. **Direct boot:** if CE storage locked, wait for unlock broadcast / user-present constraint.

#### 5.1.2 Android lifecycle realities

| Reality | Implication |
|---------|-------------|
| Process death anytime | Persist state before/after each phase |
| `BroadcastReceiver` time limits | Must return quickly |
| Doze / standby buckets | Use WM constraints; accept delay |
| OEM aggressive killing | Periodic reconcile (e.g. daily) as safety net |
| Main-thread ANR | Bitmap decode off main |
| App standby exemptions | Don’t rely on being exempt |

**Deal-breaker:** set wallpaper in `Activity.onResume` after boot — races, jank, missed headless boots.

#### 5.1.3 BOOT_COMPLETED deep dive

```text
Manifest receiver (exported carefully / permission BOOT_COMPLETED):
  onReceive:
    schedule unique WorkRequest with initialDelay = jitter(0..120s)
    return immediately  // <10ms goal

Do NOT: download, decode Bitmap, touch WallpaperManager here
Common bug: starting IntentService that dies under OEM; prefer WM
```

#### 5.1.4 WorkManager configuration deep dive

```text
Constraints:
  NetworkType.CONNECTED (or UNMETERED if asset large & policy says)
  Battery not low optional (product)
Unique work: "wallpaper-reconcile", ExistingWorkPolicy.REPLACE / KEEP
Backoff: EXPONENTIAL, min 10s, cap hours
Periodic: Daily reconcile KEEP — catches missed boots
Expedited: only for explicit user action
```

**REPLACE vs KEEP:** REPLACE when new policy push arrives; KEEP for boot if work already running.

#### 5.1.5 Doze, App Standby, and OEM quirks

| Mode | Effect | Mitigation |
|------|--------|------------|
| Doze | Defer network | WM + FCM; accept delay |
| App Standby bucket | Rare execution | Periodic + push |
| MIUI/ColorOS/etc. | BG kill | Periodic; user education; OEM testing matrix |
| Force-stop | Alarms/WM cancelled | Next boot/launch re-enqueue |

**Interview honesty:** you cannot guarantee sub-minute apply on all OEMs; design idempotent eventual reconcile + telemetry.

#### 5.1.6 Persistence design

```text
policy_store: version, etag, sha256, target, state, attempts, last_error,
              last_success_at, user_override
files: staging.bin → current.bin; keep previous.bin
sidecar current.sha256 for fast check
Atomicity: write staging → fsync → hash → rename → apply → persist APPLIED
```

#### 5.1.7 Failure classification & retry

| Error | Class | Action |
|-------|-------|--------|
| Timeout / 429 / 503 | Transient | Backoff retry |
| Checksum mismatch | Transient→Permanent | Redownload N times |
| SecurityException | Permanent | Stop; needs user |
| ENOSPC | Transient after trim | Evict staging |
| 404 asset | Permanent until new policy | Refetch policy later |

```text
attempts 0..8; backoff min(2^n + jitter, 6h)
Daily periodic catches exhausted retries after network returns
```

#### 5.1.8 Rollback

- Keep `previous.bin`  
- Kill switch policy → prior hash  
- Failed apply leaves last good current  

### 5.2 Scalability

#### 5.2.1 Client fleet

| Technique | Purpose |
|-----------|---------|
| Jitter 0–120s | Smooth storms |
| ETag / 304 | Cut origin |
| Content-addressed assets | CDN forever cache |
| Cohort 1→10→50→100% | Blast radius |
| Telemetry sampling | Cost at 1B |

#### 5.2.2 Server scale

```text
1B devices: boots/day ~1B/86400 ≈ 11.5K/s avg; peak ×10
95% 304 + edge → origin tiny
Asset downloads only on policy change — cohort stagger mandatory
```

#### 5.2.3 Progressive scale

| Scale | Must add |
|-------|----------|
| 10× | CDN + ETag + WM unique work |
| 100× | Cohorts; prefetch; OEM dashboards |
| 1,000× | Edge config; sampling; regional assets |

### 5.3 Maintainability

#### 5.3.1 Single reconcile path

Boot, push, periodic, debug — **same worker**. Divergent paths cause “works on push, fails on boot.”

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| apply_success_rate by OEM/API | Regressions |
| time_boot_to_applied_p99 | SLO |
| checksum_fail_rate | Corruption |
| skipped_idempotent_rate | Sanity |
| permanent_fail_rate | Permissions |
| wm_enqueue_fail | Scheduling |

#### 5.3.3 Testing matrix

- Death between each state; airplane→online; disk full; corrupt staging  
- Policy flip mid-download; direct boot; user override  
- OEM reference devices in lab  

#### 5.3.4 Code structure

```text
schedule/BootEnqueue → work/ReconcileWorker → state/PolicyStore
  → cache/AssetCache → apply/WallpaperApplier → net/PolicyClient
```

### 5.4 Idempotency & concurrency

```text
Single-flight unique work
Same policy_version + valid current hash → SKIPPED_IDEMPOTENT
Concurrent push+boot: REPLACE coalesces to one run
WallpaperManager calls serialized on one background dispatcher
```

### 5.5 Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Heavy BOOT_COMPLETED | Enqueue only |
| Memory-only state | DataStore + files |
| Blind re-apply every boot | Version idempotency |
| Instant 100% rollout | Cohorts + jitter |
| No previous slot | Two-slot cache |
| Main-thread decode | WM background |

---

## 6. Wrap-Up

### 6.1 Design summary

An Android wallpaper-at-boot system is a **durable reconciliation loop**: thin boot enqueue → WorkManager worker → versioned policy fetch → checksummed two-slot asset cache → WallpaperManager apply → persisted `APPLIED`. Reliability comes from idempotency, failure classification, and never doing heavy work in the receiver. Scale comes from CDN-addressed assets, ETag’d policies, jitter, and cohort rollouts.

### 6.2 Key trade-offs

| Trade-off | Choice | Cost |
|-----------|--------|------|
| Eventual apply vs instant at boot | Deferred WM | Wallpaper may lag minutes |
| User override vs enterprise force | Prefer user; force opt-in | Policy complexity |
| Two-slot disk vs one slot | Two-slot | Extra MBs |
| Aggressive retry vs battery | Bounded backoff | Slower recovery |

### 6.3 Deal-breakers (say aloud)

1. Heavy work / network in `BroadcastReceiver.onReceive`.  
2. Apply without checksum.  
3. No persistence of policy version → re-download every boot.  
4. Ignoring Doze constraints with sticky wake locks.  
5. Divergent boot vs push code paths.  
6. Thundering-herd 100% fleet asset flip with no stagger.

### 6.4 Progressive scale one-liner

Baseline: WM + local DB + CDN. → 10×: ETag + unique work. → 100×: cohorts + OEM metrics. → 1,000×: edge config + sampled telemetry.

### 6.5 What to draw first in interview

1. Boot → enqueue → Worker state machine.  
2. Policy store + three files.  
3. Config + CDN.  
4. Failure table.  
5. Jitter/cohort for scale.

---

## 7. Deeper / Related Interview Questions

### 7.1 Lifecycle & Android platform

**Q1: Why not set wallpaper directly in `BOOT_COMPLETED` receiver?**  
A: Receivers have short lifetime expectations; network/decode can be killed; ANR risk if main-thread work; OEMs throttle. Enqueue WorkManager and return.

**Q2: WorkManager vs JobScheduler vs foreground service?**  
A: WM is the compatibility layer over JobScheduler/Alarm; right for deferrable reconcile. Foreground service only if UX requires immediate visible progress—overkill for wallpaper.

**Q3: How do Doze and App Standby affect wallpaper update?**  
A: Jobs defer to maintenance windows unless high-priority push path. Accept delayed apply; use network constraint; don’t hold wake locks across downloads indefinitely.

**Q4: What is Direct Boot and why care?**  
A: Before user unlock, credential-encrypted storage inaccessible. Persist only device-protected state if needed; wait for `USER_UNLOCKED` to read full cache/apply.

**Q5: How do you handle multi-user Android?**  
A: Wallpaper is per-user; run reconcile as correct user; store assets in user-specific dirs; don’t assume single `filesDir` globally.

**Q6: `WallpaperManager.setBitmap` vs `setStream`?**  
A: Prefer stream/file FD to control decode size; decode with `inSampleSize` based on `DisplayMetrics` to avoid OOM on large assets.

**Q7: How to avoid ANR when decoding?**  
A: All decode/apply on WM background executor; never on main. Cap bitmap dimensions to screen×density×safety factor.

**Q8: What if OEM doesn’t deliver `BOOT_COMPLETED` reliably?**  
A: Defense in depth: boot receiver + periodic WM (daily) + on app process start reconcile + FCM config push.

### 7.2 Persistence & consistency

**Q9: What must be persisted vs recomputed?**  
A: Persist policy version, state, attempts, hashes, user override. Recompute “need download?” from file existence + hash.

**Q10: How do you get atomic file replace?**  
A: Write `staging` → fsync → verify → `rename` over `current` (same filesystem). Keep `previous` copy before replacing current.

**Q11: Crash after apply success but before DB write?**  
A: Next run sees same version + matching file → idempotent re-apply OR detect via WallpaperManager (limited) — re-apply is acceptable.

**Q12: Crash after DB says APPLIED but file deleted by user/OS?**  
A: Integrity check on start; if missing/mismatch → `NEED_ASSET` even if version matches.

**Q13: SharedPreferences vs DataStore vs SQLite?**  
A: DataStore for key-value policy/state (typed, async). SQLite if you need queryable history of attempts. Avoid untyped prefs for state machines.

**Q14: How to version migrations of local schema?**  
A: DataStore/SQLite migration version; if corrupt, reset to `POLICY_STALE` and refetch—never brick apply forever.

### 7.3 Failure handling

**Q15: Outline transient vs permanent failures.**  
A: Transient = network, 5xx, checksum (retry), ENOSPC after trim. Permanent = 404 stable, SecurityException, unsupported format, min_app_version fail.

**Q16: How many retries?**  
A: ~5–8 with exponential backoff capped (e.g. 6h) + daily periodic safety net. Infinite tight loops are a battery deal-breaker.

**Q17: What if CDN serves wrong bytes with 200?**  
A: SHA-256 mismatch catches it; delete staging; retry; after N fails quarantine and alert telemetry (integrity incident).

**Q18: Disk full strategy?**  
A: Delete staging first, then previous (keep current), then fail `NO_SPACE`. Never delete `current` before new verified asset ready.

**Q19: Partial download resume?**  
A: Optional HTTP Range; MVP can re-download whole 2 MB. At large video wallpapers, resume matters—out of MVP still mention.

**Q20: How to test failure injection?**  
A: Fake PolicyClient; kill process between states; flip airplane mode; truncate staging file; mock WallpaperManager exceptions.

### 7.4 Idempotency & concurrency

**Q21: Define idempotency key.**  
A: `(policy_version, asset_sha256, target)`. If APPLIED for that key and file OK → skip.

**Q22: Policy churn every minute—what happens?**  
A: Unique work `REPLACE` keeps latest; cancel obsolete downloads when version advances; only latest staging retained.

**Q23: Concurrent boot enqueue + FCM enqueue?**  
A: Same unique work name → coalesced; ExistingWorkPolicy.KEEP or REPLACE with care (REPLACE for newer policy).

**Q24: Can two processes apply simultaneously?**  
A: Unlikely with WM single worker; still use file lock / `AtomicFile` patterns around apply critical section.

### 7.5 Scale & server

**Q25: How to prevent boot thundering herd?**  
A: Client jitter; server cohort `apply_after`; edge cached policy; immutable CDN assets.

**Q26: Why content-addressed asset URLs?**  
A: Cache-Control immutable; safe long TTL; integrity aligns with hash in policy.

**Q27: Config service vs baking assets in APK?**  
A: Dynamic wallpapers / campaigns need server. APK bake only for defaults; still run reconcile for updates.

**Q28: Telemetry volume at 1B devices?**  
A: Sample successes (e.g. 1%); always-on for failures/permanent; aggregate by OEM/version.

**Q29: Kill switch design?**  
A: Policy endpoint returns `force_default` or empty apply; client applies previous/default; edge TTL short enough for emergency.

**Q30: Staged rollout correctness?**  
A: Sticky cohort assignment hashed by device_id; monotonic policy_version per cohort; don’t flap devices across cohorts.

### 7.6 Product / UX / privacy

**Q31: User sets their own wallpaper—do we overwrite on boot?**  
A: Default no (`user_override`). Enterprise `force` may overwrite—make explicit in requirements.

**Q32: Privacy of wallpaper assets?**  
A: Authenticated policy if user-specific; CDN URLs with short-lived signed URLs if sensitive; don’t log tokens.

**Q33: Accessibility / dark mode?**  
A: Optional dual assets in policy (`light_sha`, `dark_sha`); pick by UI mode at apply time.

**Q34: Notification spam?**  
A: Silent success; notify only on permanent failure or user-visible enterprise force—product call.

### 7.7 Alternatives & deal-breakers

**Q35: AlarmManager exact alarm every boot minute?**  
A: Battery nightmare; special permissions; deal-breaker vs WM.

**Q36: Only update wallpaper when user opens app?**  
A: Misses headless boots; fails product requirement “at boot.”

**Q37: Store wallpaper only server-side and stream every boot?**  
A: Breaks offline; wastes bandwidth; deal-breaker.

**Q38: Native init daemon sets wallpaper pre-app?**  
A: Platform/OEM territory; app interview should stay in app+WM space unless system partner role.

### 7.8 Interview craft

**Q39: How to open this interview?**  
A: Clarify boot vs push vs periodic; offline; user override; home vs lock; then draw client state machine before CDN boxes.

**Q40: What numbers matter?**  
A: Asset size, boots/day, % policy change, CDN egress, success SLO, retry budget, cache quota.

**Q41: What impresses Meta L5 mobile?**  
A: Thin receiver, WM constraints, two-slot rollback, checksum gate, idempotent versions, OEM variance humility, jitter/cohorts.

**Q42: Common mistake?**  
A: Designing only the server CDN and hand-waving Android lifecycle/process death.

**Q43: How do you end?**  
A: Restate invariants, failure table, scale stagger, and one deal-breaker you refused.

---


### 7.9 Deep dive extras

**Q44: Why ExistingWorkPolicy.REPLACE on FCM policy push?**  
A: Coalesce bursts of config changes into one reconcile; avoid queue stampedes.

**Q45: How do you verify apply actually changed the wallpaper?**  
A: Persist policy_version after WallpaperManager success; optional screenshot hash is usually too heavy/privacy-invasive — trust API + user reports + OEM metrics.

**Q46: Unmetered-only downloads?**  
A: OK for large assets if product agrees; always allow policy JSON on any network; risk: users never on Wi-Fi never update.

**Q47: What if WallpaperManager succeeds but process dies before DataStore write?**  
A: Next run sees same bytes + same version target → re-apply (idempotent) then persist — acceptable.

**Q48: How does progressive 1,000× change client code?**  
A: Mostly server/edge/telemetry sampling; client still same state machine — that’s the point of good design.

---

### Appendix A — State transition table

| From | Event | To |
|------|-------|-----|
| ANY | boot enqueue | POLICY_STALE |
| POLICY_STALE | user_override | SKIPPED_USER_OVERRIDE |
| POLICY_STALE | start fetch | FETCHING_POLICY |
| FETCHING_POLICY | 304 / same version + file OK | SKIPPED_IDEMPOTENT |
| FETCHING_POLICY | new policy | NEED_ASSET or ASSET_READY |
| NEED_ASSET | start DL | FETCHING_ASSET |
| FETCHING_ASSET | checksum OK | ASSET_READY |
| ASSET_READY | start apply | APPLYING |
| APPLYING | success | APPLIED |
| ANY fetch/apply | transient err | FAILED_TRANSIENT |
| FAILED_TRANSIENT | retry | prior phase |
| ANY | permanent err | FAILED_PERMANENT |

### Appendix B — WorkManager config sketch

```text
Constraints:
  - NetworkType.CONNECTED (if need fetch)
  - BatteryNotLow = true (optional)
  - StorageNotLow = true

OneTimeWorkRequest:
  uniqueName = "wallpaper-reconcile"
  existingWorkPolicy = REPLACE
  initialDelay = random(0..120s) on boot
  backoff = EXPONENTIAL, 30s

PeriodicWorkRequest:
  interval = 24h
  flex = 6h
  same worker
```

### Appendix C — Checksum verify pseudocode

```text
fun verify(file, expectedSha): Boolean {
  val digest = MessageDigest.getInstance("SHA-256")
  file.inputStream().use { input ->
    val buf = ByteArray(8192)
    while (true) {
      val n = input.read(buf)
      if (n <= 0) break
      digest.update(buf, 0, n)
    }
  }
  return digest.digest().toHex() == expectedSha
}
```

### Appendix D — Apply pseudocode

```text
fun apply(policy, file): Result {
  if (!verify(file, policy.sha)) return Fail("checksum")
  val stream = file.inputStream()
  return try {
    when (policy.target) {
      HOME -> wm.setStream(stream, null, true, FLAG_SYSTEM)
      LOCK -> wm.setStream(stream, null, true, FLAG_LOCK)
      BOTH -> { set home; set lock }
    }
    Ok
  } catch (se: SecurityException) {
    PermanentFail(se)
  } catch (oom: OutOfMemoryError) {
    TransientFail("oom")
  }
}
```

### Appendix E — Downsample strategy

```text
targetW = screenWidthPx * 1.5
targetH = screenHeightPx * 1.5
use BitmapFactory.Options.inJustDecodeBounds = true
compute inSampleSize power-of-two
decode bounds-limited bitmap OR prefer setStream with OEM scaling
recycle bitmaps; avoid retaining on heap
```

### Appendix F — Telemetry event schema

```json
{
  "event": "wallpaper_reconcile",
  "policy_version": 184422,
  "result": "APPLIED|SKIPPED_IDEMPOTENT|FAILED_TRANSIENT|FAILED_PERMANENT",
  "attempts": 2,
  "error_code": "CHECKSUM|NO_SPACE|SECURITY|HTTP_503|...",
  "boot_to_apply_ms": 45230,
  "download_bytes": 2097152,
  "oem": "Pixel",
  "api_level": 34,
  "sampled": true
}
```

### Appendix G — Cohort assignment

```text
cohort = hash(device_id + campaign_id) % 100
if cohort < rollout_percent: serve new policy
else: serve sticky prior policy
apply_after = campaign_start + cohort * stagger_bucket
```

### Appendix H — Permission / role matrix

| App type | Typical path |
|----------|--------------|
| User app | REQUEST permission / user picks; limited |
| Partner / privileged | May set wallpaper more freely |
| Device owner / profile owner | Managed configurations |

Interview: state assumption early.

### Appendix I — NFR card

```text
Thin boot receiver
WM unique reconcile
Checksum before apply
Two-slot cache rollback
Idempotent policy_version
99% apply ≤15m online
No wake-lock abuse
CDN + ETag + jitter
```

### Appendix J — Progressive scale table

| Scale | Client | Config | Assets | Telemetry |
|-------|--------|--------|--------|-----------|
| Baseline | WM + DataStore | Single region | CDN | Full events |
| 10× | Unique work + jitter | ETag edge | Immutable hash URLs | Dashboards |
| 100× | Periodic safety net | Cohorts | Prefetch | OEM breakdown |
| 1,000× | Strong coalesce | Global edge | Regional PoPs | Heavy sampling |

### Appendix K — Failure budget math

```text
p_transient = 0.02 per attempt
P(fail 5 times) = 0.02^5 ≈ 3e-9 (independent assumption — optimistic)
Real world correlated outages → need periodic retry after hours
SLO: time-based recovery when network returns, not only N attempts
```

### Appendix L — Debug / ops playbook

| Symptom | Check |
|---------|-------|
| High checksum fails | CDN corruption, middlebox, wrong URL |
| High SECURITY fails | Permission regression / OEM |
| Boot success low, push high | Receiver not firing; rely on periodic |
| Disk errors spike | Cache quota bug; large assets |
| CDN 5xx spike | Rollback cohort; kill switch |

### Appendix M — Comparison: approaches

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| Receiver-only | Simple | Fragile | Reject |
| Foreground service always | Reliable-ish | UX/battery cost | Reject MVP |
| WorkManager reconcile | Durable, constrained | Deferred | **Choose** |
| System binder service | Strong | Needs privilege | Partner-only |

### Appendix N — Sequence: offline then online

```text
boot offline:
  load policy v5 APPLIED, file OK → SKIPPED_IDEMPOTENT (or re-apply if flag)
boot offline, file missing:
  FAILED_TRANSIENT NETWORK; WM retries
network returns:
  fetch policy → download → apply
```

### Appendix O — Sequence: mid-apply kill

```text
ASSET_READY → APPLYING → process death
on restart:
  state APPLYING or ASSET_READY (persist before call)
  file verified → re-enter APPLYING
  success → APPLIED
previous slot still intact throughout
```

### Appendix P — Security notes

- HTTPS only; pin optional for high assurance.  
- Signed URLs expire for private assets.  
- Validate MIME/size before decode.  
- Treat wallpaper as untrusted image: size caps, careful decoders.  
- No PII in asset URLs query logs.

### Appendix Q — Glossary

| Term | Meaning |
|------|---------|
| Reconcile | Make device match desired policy |
| Staging | Incomplete download file |
| Two-slot | current + previous assets |
| Unique work | WM coalescing key |
| Cohort | Rollout partition of devices |
| Direct Boot | Pre-unlock run mode |

### Appendix R — 30m interview checklist

1. Clarify boot/push/offline/override.  
2. Draw thin receiver → WM → state machine.  
3. Persist fields + three files.  
4. Checksum + failure table.  
5. Jitter/cohort scale.  
6. List deal-breakers.  
7. Telemetry + OEM variance.

### Appendix S — Sample policy JSON

```json
{
  "policy_version": 10042,
  "asset_url": "https://cdn.example/a/sha256/ab...cd.webp",
  "asset_sha256": "ab...cd",
  "asset_bytes": 1844220,
  "target": "BOTH",
  "apply_after": "2026-08-06T08:00:00Z",
  "force": false,
  "min_app_version": 240800
}
```

### Appendix T — Local DB fields

| Field | Type | Notes |
|-------|------|-------|
| policy_version | Long | Monotonic assignment |
| etag | String | Conditional GET |
| state | Enum | State machine |
| attempts | Int | Retry counter |
| last_error | String | Truncated |
| user_override | Bool | User pin |
| current_sha | String | Fast check |
| applied_at | Long | Epoch ms |

### Appendix U — Why Meta asks this

Tests whether you can build **reliable mobile systems**: lifecycle, persistence, integrity, battery, and fleet rollout—not whether you know WallpaperManager trivia alone.

### Appendix V — Quick deal-breaker card

| Fantasy | Reality |
|---------|---------|
| Set in onCreate | Missed boots / jank |
| No checksum | Corrupt/black screens |
| Infinite wake lock | Play policy / battery kill |
| Memory-only state | Lost on process death |
| Instant 100% rollout | CDN melt / bad asset blast |

---

*End of Mobile Wallpaper Update at Boot system design.*

---

## 8. Progressive Evolution & Anti-Patterns (Study Card)

### 8.1 10× / 100× / 1,000× evolution

| Jump | Change | Why |
|------|--------|-----|
| →10× | CDN assets; ETag policy; WM unique work | Correctness + mild scale |
| →100× | Cohort stagger; OEM dashboards; prefetch | Blast radius + quirks |
| →1,000× | Edge config; telemetry sampling; regional assets | Boot storms at 1B |

### 8.2 Boot path card

```text
BOOT_COMPLETED → enqueue WM (jitter) → return
Worker: load state → policy ETag → asset staging → sha256
  → rename slots → WallpaperManager → APPLIED persist → telemetry
Same worker for FCM / periodic / debug
```

### 8.3 Doze / OEM honesty card

```text
Cannot promise minute-level on all OEMs
Design: idempotent eventual reconcile + daily periodic + metrics by OEM
Never spin forever in receiver
Direct boot: wait unlock / use DPS carefully
```

### 8.4 Two-slot persistence card

```text
staging → checksum → current; keep previous
APPLIED only after setWallpaper success
Failure leaves last good
Rollback: previous.bin or kill-switch policy hash
```

### 8.5 Anti-patterns

1. Download/decode in BroadcastReceiver  
2. Memory-only “applied” flags  
3. Re-apply every boot blindly  
4. Instant 100% fleet flip  
5. Delete previous on first error  
6. Main-thread Bitmap + WallpaperManager

### 8.6 WorkManager unique work snippet (conceptual)

```text
Constraints: network connected
Initial delay: random 0..120s on boot path
Backoff: exponential
Input: trigger=BOOT|FCM|PERIODIC|DEBUG
Idempotency: policy_version + sha256 gate inside worker
```

### 8.7 Telemetry events

```text
enqueue, policy_304, policy_200, asset_start, asset_ok, checksum_fail,
apply_start, apply_ok, apply_fail, skipped_idempotent, skipped_override
dimensions: oem, api_level, app_version, cohort
sample at high QPS fleets
```

### 8.8 Permission / SecurityException path

```text
If setWallpaper throws SecurityException:
  state=FAILED_PERMANENT
  optional in-app prompt to grant / open settings
  do not retry hot loop
  periodic may re-check if user fixed permissions
```

### 8.9 Cohort rollout

```text
device_id hash → cohort bucket 0–99
policy.serve if bucket < rollout_percent
Kill switch: rollout_percent=0 or force previous asset hash
Stagger downloads independently of boot jitter
```

