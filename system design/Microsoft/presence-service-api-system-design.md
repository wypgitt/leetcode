# System Design: Presence Service API

> **Focus areas:** Online / Away / Busy / Offline · Heartbeats · Subscription fan-out · Privacy · Multi-device · Ephemeral store · Entra ID auth  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Presence is approximate & privacy-gated; never confuse with durable chat truth; subscription storms handled; Microsoft identity/tenant themes explicit  
> **Interview theme:** Microsoft — Teams / Skype / Xbox Live DNA: presence API as a **shared platform service** used by chat, calling, collaboration, and gaming clients  
> **Company flavor:** Entra ID tokens, tenant-scoped visibility rules, regional Azure cells, Purview audit hooks for enterprise presence policies

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

Goal: design a **Presence Service API**—a platform service that tracks user (and optionally device/app) availability states, accepts heartbeats from connection fleets, and notifies authorized subscribers when presence changes—at Microsoft product scale (Teams, Skype, Xbox, Outlook web).

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Ephemeral availability + subscription notifications | Durable chat message store |
| Truth | Approximate, eventually consistent, TTL-driven | Strong ledger of business facts |
| Consumers | Chat, calling, calendar busy, games matchmaking | Payroll / HR system of record |
| Microsoft lens | Entra ID, tenant policies, privacy, regional Azure | Consumer-only anonymous presence |
| Success | Correct enough, private, scalable fan-out | Perfect global instantaneous sync |

**Scope statement:** Design a multi-tenant presence API: publish status via heartbeats/explicit set, resolve effective status across devices, authorize subscribers, fan-out deltas, enforce privacy and enterprise policies—progressively scaled.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Status values? | At least `Online`, `Away`, `Busy`, `DoNotDisturb`, `Offline` (+ optional `BeRightBack`, `AppearOffline`) | Enum + versioned schema; client maps UI |
| F2 | Who sets status? | Auto from connection/heartbeat + explicit user override | Priority rules: override > activity > connection |
| F3 | Heartbeats? | Connection gateway sends heartbeat every N seconds | TTL expiry → Offline; no client polling storm |
| F4 | Multi-device? | Phone + desktop + web; aggregate to one effective status | Device presence + aggregation policy |
| F5 | Subscriptions? | Watch list / roster / conversation members | Sub registry + push deltas |
| F6 | Privacy? | Appear offline; block lists; org policies hide status | Authz on every read/sub |
| F7 | Busy from calendar? | Optional: Entra/Exchange calendar → Busy | Calendar connector; not MVP core |
| F8 | Typing vs presence? | Typing is separate ephemeral signal | Don't overload presence channel |
| F9 | Last seen? | Optional last-online timestamp with privacy | Separate field; coarse granularity |
| F10 | Tenant scope? | Enterprise users isolated by tenant; B2B guest rules | Tenant ID on every key |
| F11 | Auth? | Entra ID OAuth2 / MSAL tokens | Token validation at edge |
| F12 | Batch APIs? | Get presence for roster of 50–200 | Batch read with authz filter |
| F13 | Webhooks? | Optional for bots / Graph subscriptions | Async delivery plane |
| F14 | Admin policies? | Org can disable last-seen / force status visibility | Policy engine |

**MVP functional scope (lock with interviewer):**

1. Authenticated publish: heartbeat from gateway + explicit `PUT /me/presence`.  
2. Status set: Online / Away / Busy / DND / Offline (+ AppearOffline).  
3. Multi-device aggregation to **effective presence**.  
4. Heartbeat TTL → auto Offline.  
5. Subscribe to users (roster); receive delta notifications on connection or webhook.  
6. Batch get presence for up to N users with privacy filter.  
7. Block / appear-offline honored.  
8. Entra ID auth; tenant_id isolation.

**Out of MVP (explicitly defer):**

- Perfect global presence with <50ms worldwide consistency  
- Full calendar-derived busy as SoT (hook only)  
- Rich activity (“In a call with X”, “Editing doc Y”) deep product  
- Xbox rich presence game titles as primary design (mention pattern)  
- Cross-cloud sovereign isolation deep dive (mention Azure regions)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Publish latency | Heartbeat → store | p99 < 50–100ms in-region |
| N2 | Notify latency | Change → subscriber online | p50 < 200ms, p99 < 1s in-region |
| N3 | Consistency | Approximate OK | Eventual; stale ≤ TTL window |
| N4 | Availability | Degrade gracefully | Presence optional vs chat; 99.9% target |
| N5 | Fan-out | Popular users | Cap subs; aggregate; shed |
| N6 | Privacy | No unauthorized leak | Authz fail closed |
| N7 | Multi-region | Global users | Regional write affinity; cross-region read approx |
| N8 | Scale | Teams-class | 100M+ DAU class progressive |
| N9 | Audit (enterprise) | Policy changes audited | Purview / audit log hooks |
| N10 | Cost | Ephemeral hot path cheap | Redis/Memory + short TTL; not SQL SoT |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User opens Teams desktop → gateway registers device session → heartbeat → Online.  
2. Idle 5–15 min → Away (client or server idle policy).  
3. User sets Busy → override until clear or TTL.  
4. Colleague with subscription receives delta: Online → Busy.  
5. User closes all apps → TTLs expire → Offline; last_seen updated if allowed.  
6. Batch roster fetch on chat list open → filtered presence map.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Flapping connect/disconnect | Debounce; sticky Online for grace period |
| Dual device: desktop Online, phone Away | Aggregate: Online if any interactive Online |
| AppearOffline | Publishers see Offline; self sees real |
| Blocked subscriber | No presence; treat as unknown/offline |
| Celebrity / exec with 50K watchers | Cap push; poll/batch for long-tail |
| Heartbeat lost (network) | Grace TTL (2–3 missed) then Offline |
| Clock skew | Server TTL based on receive time |
| Cross-tenant guest | Policy: show limited or hide |
| Region failover | Presence rebuild from heartbeats (ephemeral OK) |
| Subscription storm on outage recovery | Backoff; snapshot then deltas |
| DND during call | Calling service may set Busy/InACall |
| Token expired mid-sub | Drop sub; client re-auth |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| MAU | 10M | 100M | 1B | 1B+ multi-product |
| Concurrent online | 1M | 10M | 100M | 100M+ |
| Heartbeats / s | 200K | 2M | 20M | 50M+ |
| Presence updates / s (material) | 10K | 100K | 1M | 5M |
| Avg subscriptions / user | 50 | 80 | 100 | 150 |
| Hot user watchers | 1K | 10K | 100K | 1M (special mode) |
| Tenants | 10K | 100K | 1M | Multi-cloud |
| Regions | 2 | 6 | 20+ | Sovereign + edge |

**Jumps:** 10× = sharded presence store + sub registry; 100× = hybrid notify (push hot, pull cold), regional cells; 1,000× = product-specific presence planes, aggressive shedding, Graph-scale batching.

### 1.5 Scope repeat-back

> Multi-tenant Presence API: Entra-authenticated heartbeats and explicit status, multi-device aggregation, privacy-aware subscriptions and batch reads, approximate eventual consistency with TTL expiry—optimized for massive heartbeat write load and controlled fan-out, never as durable business truth. Distinct from chat message delivery; integrates with Microsoft identity, tenant policy, and regional Azure.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Heartbeat math

```text
Concurrent online sessions S = 10M (10× row)
Heartbeat interval H = 30s
Heartbeat QPS ≈ S / H = 10M / 30 ≈ 333K/s

At 100× with 100M online:
QPS ≈ 100M / 30 ≈ 3.3M/s

Mitigations:
- Gateway aggregates / coalesces (per-user device heartbeat, not per-tab spam)
- Longer H when idle (60–120s)
- Binary compact protocol (not JSON REST per beat)
```

### 2.2 Material update math

```text
Most heartbeats do NOT change status (same Online)
Material change rate ≈ 1–5% of beats or explicit sets
At 333K beats/s → ~3K–15K status mutations/s
Fan-out: each mutation × avg online subscribers watching
If avg 5 online watchers notified → 15K–75K notify msgs/s
Hot users dominate: isolate and cap
```

### 2.3 Storage

```text
Presence record ~ 100–300 bytes (user_id, tenant_id, status, device map, ver, expiry)
10M online × 200 B ≈ 2 GB hot
100M online × 200 B ≈ 20 GB hot (+ replicas)
Subscription edges: user → watchers; invert watcher → targets
100M users × 80 subs × 16 B ≈ 128 GB compressed edge store (sharded)
```

### 2.4 Latency budget (notify path)

```text
Gateway heartbeat → Presence Store CAS → Change log → Sub resolver →
Notify bus → Subscriber's connection gateway → client
Budget in-region: 10 + 20 + 30 + 50 + 50 = ~160ms p50 target
```

### 2.5 Bottlenecks

(1) Heartbeat write QPS (2) Hot-user fan-out (3) Subscription registry size (4) Cross-region curiosity (5) Reconnect storms (6) Privacy evaluation CPU at batch read.

### 2.6 Cost / frugality

Presence must be **cheap**: memory store + TTL, not OLTP SQL. Drop typing-like signals first under load. Prefer coalesced heartbeats at edge. Enterprise audit is sampled/async—not on every heartbeat.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Session / Heartbeat | Device liveness from gateways | Ephemeral TTL |
| Presence State | Effective status + overrides | Per-user strong-ish CAS |
| Subscription Registry | Who watches whom | Durable, eventually synced |
| Notify / Fan-out | Delta delivery | Best-effort, at-least-once |
| Policy / Privacy | Blocks, appear-offline, tenant rules | Strong on evaluate path |
| Identity | Entra token validation | Edge + service |

**Deal-breaker:** treating presence store as durable chat SoT or requiring cross-region linearizability for Online/Offline.

### 3.2 Components

1. **API Gateway / Azure Front Door** — TLS, WAF, routing.  
2. **Presence API Service** — REST/gRPC: get, batch get, set, subscribe.  
3. **Heartbeat Ingest** — high-QPS path from connection fleets (Teams, Skype).  
4. **Presence Store** — Redis / Azure Cache / custom memory + WAL.  
5. **Aggregator** — multi-device → effective status.  
6. **Subscription Service** — watch lists, Graph-style subscriptions.  
7. **Notify Dispatcher** — pub/sub to connection gateways / SignalR-like.  
8. **Policy Engine** — privacy, tenant admin, block list cache.  
9. **Entra ID Validator** — JWT / pop tokens, tenant, scopes.  
10. **Calendar Connector** (phase 1.5) — Busy from Exchange.  
11. **Audit / Purview Hook** — policy and admin actions.  
12. **Control Plane** — shard map, rate limits, feature flags.

### 3.3 Effective presence rules (sketch)

```text
Inputs per user:
  devices[]: {device_id, conn_state, last_heartbeat, client_activity}
  override: {status, expires_at} | null
  calendar_busy: bool (optional)
  appear_offline: bool

If appear_offline and viewer != self → Offline
Else if override active → override.status
Else if any device Online & recent activity → Online
Else if any device connected & idle → Away
Else if calendar_busy → Busy
Else → Offline

Version++ on each material change; notify if version changes
```

### 3.4 APIs (sketch)

```text
PUT  /v1/me/presence          {status, expiry?, device_id}
POST /v1/me/heartbeat         {device_id, activity?}   # often internal
GET  /v1/users/{id}/presence
POST /v1/users/presence:batch {user_ids[]}
POST /v1/subscriptions        {user_ids[], channel}
DELETE /v1/subscriptions/{id}
GET  /v1/subscriptions/{id}/delta?since=ver
```

### 3.5 Trade-offs

| Topic | Choice | Why | Deal-breaker if wrong |
|-------|--------|-----|------------------------|
| SoT store | Memory + TTL (+ optional snapshot) | Heartbeat QPS | SQL per heartbeat |
| Consistency | Per-user CAS, cross-region eventual | Scale | Global lock Online |
| Fan-out | Push to online subs; cap hot users | Cost | Full mesh notify |
| Heartbeat owner | Connection gateway, not browser tabs | Storm control | Tab × 5s JSON |
| Privacy | Fail closed on batch | Compliance | Leak then filter |
| Multi-device | Aggregate server-side | UX consistency | Last-writer chaos |
| Calendar | Async enrichment | Don't block heartbeat | Sync Exchange on beat |

### 3.6 Microsoft-specific constraints

| Theme | Implication |
|-------|-------------|
| Entra ID | `oid`, `tid`, roles/scopes on every call |
| Tenant isolation | Keys prefixed `tid/oid`; no cross-tenant default |
| Regional Azure | Presence cell affinity near connection fleet |
| Purview | Audit admin policy; not every Online flip |
| Graph API shape | Align batch/subscribe with Microsoft Graph patterns |
| Teams + Skype + Xbox | Shared platform with product-specific views |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Clients: Teams / Web / Mobile]
        |  WSS / long-lived
        v
[Connection Gateway Fleet] ----heartbeat---->\
        |                                     \
        | subscribe/notify <----+              \
        v                       |               v
[Presence API] -----> [Policy/Entra]     [Heartbeat Ingest]
        |                       |               |
        v                       v               v
[Subscription Registry]   [Block/Privacy] [Presence Store]
        |                                         |
        +----------> [Notify Dispatcher] <--------+
                            |
                            v
                   [Gateway Pub/Sub / SignalR]
                            |
                            v
                      [Subscriber Clients]

[Exchange Calendar] -.-> [Busy Enricher] -.-> Presence Store
[Purview/Audit] <--- admin policy changes ---
```

### 4.2 Heartbeat sequence

```text
1. Client maintains WSS to Gateway (region R)
2. Gateway authenticates Entra token; binds device_id, oid, tid
3. Every H seconds: Heartbeat Ingest {tid, oid, device_id, activity}
4. Presence Store: refresh TTL; maybe recompute effective status
5. If version changed: emit PresenceChanged event
6. Dispatcher loads online subscribers (capped); push to their gateways
7. If no heartbeats for TTL grace: mark device dead; recompute → Offline
```

### 4.3 Batch read sequence

```text
Client opens chat list → POST batch presence for 100 user_ids
Presence API:
  validate token (tid, scopes)
  for each id: load status; evaluate privacy(viewer, target)
  omit or mask unauthorized
  return map {id → PresenceView}
Cache negative/positive briefly (seconds) carefully with privacy
```

### 4.4 Cell architecture

```text
                [Global Directory: user → home presence cell]
                           |
     +---------------------+---------------------+
     |                     |                     |
 [Cell WestUS]        [Cell Europe]         [Cell Asia]
 Presence Store       Presence Store        Presence Store
 Sub Registry         Sub Registry          Sub Registry
 Gateway affinity     Gateway affinity      Gateway affinity

Cross-cell subscribe: proxy notify or pull from home cell
Failover: rebuild from live heartbeats (seconds of wrong Offline OK)
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. **Presence is approximate** — clients must tolerate staleness up to TTL.  
2. **No silent cross-tenant leak** — every read/sub checks `tid` + B2B rules.  
3. **Privacy fail closed** — appear-offline and blocks hide status.  
4. **Idempotent heartbeats** — duplicates only refresh TTL.  
5. **Version monotonic per user** — subscribers sync by version.  
6. **Override expiry** — Busy/DND cannot stick forever without refresh.  
7. **Gateway is source of device liveness** — browsers don't hammer public REST.  
8. **Degrade order** — drop notify fan-out → drop last-seen → keep set/get self.  
9. **Reconnect snapshot** — after outage, snapshot then deltas (avoid storm).  
10. **Audit admin paths** — policy changes immutable-logged.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single region Redis cluster; monolith Presence API; gateway heartbeats |
| 10× | Shard by `hash(tid, oid)`; separate ingest vs query; sub registry partitioned |
| 100× | Regional cells; hot-user mode (pull); coalesce notifies; idle heartbeat backoff |
| 1000× | Multi-product planes; edge aggregators; sovereign clouds; adaptive shed |

**Sharding key:** `tenant_id + user_id` (never shard only by user without tenant—collisions / isolation risk).

**Hot user pattern:**

```text
If watcher_count > H (e.g. 5K):
  stop per-watcher push
  publish to coarse topic OR require subscribers to poll/batch every T seconds
  executives / celebrities / support bots
```

### 5.3 Maintainability

- Status enum versioned; clients tolerate unknown statuses.  
- Policy as data (tenant config), not hard-coded.  
- Chaos: kill Redis primary; expect Offline flap then heal via heartbeats.  
- Canary cell for aggregation rule changes.  
- Clear SLOs separate from chat SLOs.  
- Owner: Presence Platform team; product teams consume API.

### 5.4 Progressive scale narrative

**1× (startup product):** One Redis, REST set/get, SignalR group per user, privacy basic block list.  

**10× (Teams growth):** Shard store; gateway-native heartbeats; subscription service; batch Graph-like API; Entra mandatory.  

**100× (global enterprise):** Regional cells; calendar Busy; admin policies; Purview audit; hot-user caps; multi-device nuanced aggregation.  

**1000× (Microsoft platform):** Shared presence across M365 + gaming views; sovereign clouds; extreme reconnect drills; cost budgets per heartbeat.

### 5.5 Multi-device aggregation deep dive

| Device A | Device B | Effective |
|----------|----------|-----------|
| Online | Offline | Online |
| Away | Online | Online |
| DND (override) | Online | DND |
| AppearOffline | Online | Offline to others |
| Connected idle | Connected idle | Away |
| None | None | Offline |

**Grace periods:** device disconnect → keep Online 30–60s to absorb laptop sleep flaps.

### 5.6 Subscription models

| Model | Pros | Cons | Use |
|-------|------|------|-----|
| Explicit watch list | Precise | Registry size | Chat roster |
| Implicit (open conversation) | Natural | Churn | Active thread |
| Tenant directory (bad) | — | Impossible scale/privacy | Never |
| Webhook (Graph) | Bots | Delivery complexity | Integrations |

**Registry storage:**

```text
Forward: watcher_id → {target_ids, channel, ver}
Inverted: target_id → {watcher_ids online}  // for fan-out; capped / sampled
```

### 5.7 Privacy & Entra

```text
Evaluate(viewer, target):
  if target.tid != viewer.tid and not B2B allowed → hide
  if viewer blocked by target → hide
  if target.appear_offline → Offline (or hide last_seen)
  if tenant policy disable_presence → hide
  if target privacy "friends_only" → check relationship service
  else return PresenceView
```

Tokens: validate `aud`, `tid`, `oid`, `scp`/`roles`. Prefer **POP** or bound tokens for gateway. Never trust client-supplied `tid`.

### 5.8 Heartbeat protocol

```text
Internal gRPC: Heartbeat(tenant_id, user_id, device_id, activity_bucket, conn_epoch)
activity_bucket: ACTIVE | IDLE | UNKNOWN
conn_epoch: increments on reconnect to ignore late packets

Public clients should NOT call heartbeat REST at high frequency.
Explicit status uses PUT /me/presence with longer TTL semantics.
```

### 5.9 Failure modes & mitigations

| Failure | User impact | Mitigation |
|---------|-------------|------------|
| Store outage | Everyone Offline / unknown | Local gateway last-known; rebuild |
| Notify bus lag | Stale status UI | UI timeout; batch refresh |
| Sub registry loss | Missed pushes | Periodic roster refresh |
| Auth outage | No new subs | Existing sessions cached claims briefly |
| Thundering herd | Meltdown | Jittered reconnect; snapshot API |
| Hot key | Latency spike | Hot-user mode; strip watchers |

### 5.10 Deal-breakers

| Temptation | Failure |
|------------|---------|
| SQL row update per heartbeat | Melts DB |
| Global total-order presence | Impossible / useless |
| Push to 1M watchers synchronously | Cascading outage |
| Store presence in chat DB transactions | Couples planes |
| Trust client `tid` | Cross-tenant breach |
| Infinite Busy override | Stuck status SEVs |
| Precise last-seen to the second | Privacy + load |
| Presence required for message send | Chat availability drop |

### 5.11 Reliability: exactly-once?

Presence notifications are **at-least-once, lossy OK**. Clients reconcile with version numbers and periodic batch refresh. Do not build two-phase commit for Online.

### 5.12 Scalability: regional affinity

```text
User home cell = f(tid, oid) or org preferred region
Connection gateway may be local; heartbeats forwarded to home cell
Reads: try local cache of remote users with short TTL
Enterprise data residency: presence for tenant pinned to geo
```

### 5.13 Maintainability: observability

- Metrics: heartbeat_qps, material_update_qps, notify_lag, store_hit, authz_deny, hot_user_count  
- Traces: sample only (volume)  
- Drill: “Monday morning login storm” simulation  
- SLO burn alerts separate from Teams messaging SLO

### 5.14 Integration with chat / calling

| Signal | Plane | Reliability |
|--------|-------|-------------|
| Presence | Presence service | Best-effort |
| Typing | Ephemeral pub/sub | Drop first |
| Chat message | Messaging store | Durable |
| Call ringing | Calling signaling | Durable enough for invite |

**Interview signal:** draw the plane split early; Microsoft interviewers punish mixing.

### 5.15 Soft-delete / GDPR

Presence is ephemeral—delete user → drop keys, subs, last_seen. Enterprise retention rarely needs raw Online history; if analytics exist, aggregate and anonymize. Right-to-be-forgotten: purge within policy SLA.

### 5.16 Security

- Rate limit set-status and subscribe APIs.  
- Prevent subscription enumeration of entire tenant.  
- Caps on watch list size (e.g. 2K).  
- Admin-only policy APIs.  
- Threat: presence oracle for stalking—mitigate via privacy defaults and rate limits.

---

## 6. Wrap-Up

### 6.1 Designed

A Microsoft-style Presence Service API: Entra-authenticated heartbeats and overrides, multi-device aggregation, privacy-aware batch reads and subscriptions, sharded ephemeral store, notify dispatcher with hot-user caps, regional cells, Purview hooks for admin policy—not a durable messaging system.

### 6.2 Decisions to defend

1. Ephemeral memory store + TTL as SoT for liveness  
2. Gateway-owned heartbeats (not browser REST spam)  
3. Per-user version + approximate notify  
4. Privacy fail closed with tenant isolation  
5. Hot-user hybrid pull  
6. Plane split from chat/calling  
7. Regional home cell with heartbeat rebuild on failover  
8. Explicit degrade order under load  

### 6.3 Risks

- Reconnect storms after regional blip  
- Hot executives / bots  
- Cross-region stale UX complaints  
- Policy complexity (B2B guests)  
- Product teams overusing presence for business logic  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: ephemeral API vs chat; statuses; Entra/tenant |
| 5–12 | Heartbeats, TTL, multi-device aggregation |
| 12–22 | Store + APIs + privacy |
| 22–32 | Subscriptions + fan-out + hot users |
| 32–40 | Scale 10×/100×/1000×, regions |
| 40–45 | Deal-breakers, degrade, Microsoft compliance hooks |

### 6.5 Closer

> **Presence Service API**: approximate, private, TTL-driven availability with gateway heartbeats, Entra/tenant isolation, controlled subscription fan-out, and explicit non-goals around durability—built as a Microsoft platform service for M365-scale clients.

---

## 7. Deeper / Related Interview Questions

### 7.1 Conceptual

1. Why must presence be eventually consistent?  
2. How do you aggregate multi-device status fairly?  
3. How does Appear Offline interact with subscriptions?  
4. When do you switch from push notify to pull?  
5. How is presence different from typing indicators?  
6. How do you prevent cross-tenant presence leaks with guests?  
7. Design last-seen with privacy and load in mind.  
8. How would Xbox “rich presence” (game + level) extend this API?  
9. How do calendar Busy signals merge with user override?  
10. What is your degrade order during a Redis outage?

### 7.2 Quantitative

11. Compute heartbeat QPS for 50M online sessions at 45s interval.  
12. If 2% of beats cause material changes and each notifies 8 watchers, what is notify QPS?  
13. Size a presence store for 80M online users at 256 bytes/record with 3× replication.  
14. Cap: max watchers for push before hot-user mode—justify.  
15. Batch API: 200 ids × 10K RPS—authz CPU strategy?

### 7.3 Failure & ops

16. Monday login storm design.  
17. Split-brain between two regions both receiving heartbeats.  
18. Subscription registry loss recovery.  
19. Poison device_id reconnect loop.  
20. How to canary a new aggregation rule.

### 7.4 Microsoft-flavored

21. Map this to Microsoft Graph presence APIs.  
22. Where does Purview show up (and where must it not)?  
23. Data residency for a German tenant’s presence.  
24. How Teams calling “In a call” should update presence.  
25. Entra Conditional Access impact on gateway sessions.

### 7.5 Compare / contrast

26. Presence vs Redis pub/sub toy design—what breaks at scale?  
27. Presence vs chat read receipts—why separate stores?  
28. Consumer Skype vs enterprise Teams policy differences.  
29. How this differs from “last active” analytics pipelines.  
30. Why not store presence rows in Azure SQL Hyperscale?

### 7.6 Stretch

31. Design Graph change notifications for presence.  
32. Anonymous webinar attendee presence (no PII leak).  
33. Federated presence with external partners.  
34. Abuse: presence scraping botnet defenses.  
35. SLO math: error budget for false Offline vs false online.

---

## 8. Appendices

### Appendix A — REST / gRPC API sketches

#### A.1 Set my presence

```http
PUT /v1/me/presence HTTP/1.1
Authorization: Bearer {entra_access_token}
Content-Type: application/json

{
  "status": "busy",
  "expiry": "2026-08-06T19:00:00Z",
  "deviceId": "d_desktop_1",
  "source": "user"
}
```

```json
{
  "userId": "oid...",
  "tenantId": "tid...",
  "effectiveStatus": "busy",
  "version": 184422,
  "asOf": "2026-08-06T18:01:02Z"
}
```

#### A.2 Heartbeat (internal)

```text
rpc Heartbeat(HeartbeatRequest) returns (HeartbeatResponse);

message HeartbeatRequest {
  string tenant_id = 1;
  string user_id = 2;
  string device_id = 3;
  string conn_epoch = 4;
  Activity activity = 5; // ACTIVE, IDLE
  int64 client_time_ms = 6; // informational only
}
```

#### A.3 Batch get

```http
POST /v1/users/presence:batch
{
  "userIds": ["u1", "u2", "u3"]
}
```

```json
{
  "presences": {
    "u1": {"status": "online", "version": 9},
    "u2": {"status": "offline"},
    "u3": {"status": "unknown", "reason": "privacy"}
  }
}
```

#### A.4 Subscribe

```http
POST /v1/subscriptions
{
  "targetUserIds": ["u1", "u2"],
  "channel": {
    "type": "gateway",
    "connectionId": "c_abc"
  },
  "ttlSeconds": 3600
}
```

### Appendix B — Data schemas

#### B.1 Presence record

```text
PresenceRecord {
  tenant_id: UUID
  user_id: UUID
  effective_status: ENUM
  version: uint64
  override: { status, expires_at, set_by }?
  devices: map<device_id, DevicePresence>
  appear_offline: bool
  last_seen_at: timestamp?          // privacy gated
  calendar_busy_until: timestamp?
  updated_at: timestamp
  expires_at: timestamp             // soft TTL for whole record
}

DevicePresence {
  device_id: string
  conn_state: CONNECTED | DEAD
  last_heartbeat_at: timestamp
  activity: ACTIVE | IDLE
  app: teams | skype | xbox | outlook
  conn_epoch: string
}
```

#### B.2 Subscription edge

```text
Subscription {
  sub_id: UUID
  tenant_id: UUID
  watcher_id: UUID
  target_id: UUID
  channel: GatewayRef | WebhookRef
  created_at: timestamp
  expires_at: timestamp
  min_version_acked: uint64
}
```

#### B.3 PresenceChanged event

```json
{
  "tenantId": "...",
  "userId": "...",
  "version": 184423,
  "effectiveStatus": "away",
  "prevStatus": "online",
  "ts": "2026-08-06T18:10:00Z"
}
```

### Appendix C — Aggregation pseudocode

```text
function computeEffective(rec):
  if rec.override and now < rec.override.expires_at:
    return rec.override.status

  anyOnlineActive = false
  anyConnected = false
  for d in rec.devices.values():
    if d.conn_state == DEAD: continue
    if now - d.last_heartbeat_at > DEVICE_TTL: continue
    anyConnected = true
    if d.activity == ACTIVE: anyOnlineActive = true

  if anyOnlineActive: return ONLINE
  if anyConnected: return AWAY
  if rec.calendar_busy_until and now < rec.calendar_busy_until: return BUSY
  return OFFLINE
```

### Appendix D — Privacy matrix

| Viewer relation | AppearOffline | Blocked | Same tenant | Result |
|-----------------|---------------|---------|-------------|--------|
| Self | yes | n/a | yes | Real status |
| Teammate | yes | no | yes | Offline |
| Teammate | no | no | yes | Effective |
| Teammate | no | yes | yes | Unknown |
| Guest B2B | no | no | no | Policy-limited |
| Anonymous | — | — | — | Denied |

### Appendix E — Rate limits (example)

| API | Limit | Notes |
|-----|-------|-------|
| PUT /me/presence | 10/min/user | Anti-flap |
| Batch get | 30/min/user; max 200 ids | Roster refresh |
| Create subs | 60/min/user; max 2K targets | Cap watch list |
| Heartbeat | Gateway internal quota | Per device 1/(H/2) |
| Webhook delivery | Backoff on 429/5xx | Dead-letter |

### Appendix F — Shard & key layout

```text
Redis key examples:
  p:{tid}:{oid} → PresenceRecord JSON/msgpack
  d:{tid}:{oid}:{device_id} → device TTL key (optional split)
  s:fwd:{tid}:{watcher} → zset/targets
  s:inv:{tid}:{target} → zset/watchers (capped)

Cluster hash tag: {tid:oid} to colocate user keys
```

### Appendix G — SLO / error budget

| SLO | Target | Notes |
|-----|--------|-------|
| Heartbeat write success | 99.99% | Gateway local buffer |
| Self get presence p99 | < 100ms | |
| Notify freshness p99 | < 2s in-region | Best-effort |
| Privacy correctness | 100% | SEV if leak |
| False Offline rate | < 1% sessions during steady state | Flaps excluded |

### Appendix H — Comparison: Presence vs Chat vs Calling

| Dimension | Presence | Chat | Calling |
|-----------|----------|------|---------|
| Durability | Seconds–minutes | Years | Minutes (signaling) |
| Loss tolerance | High | Near-zero after ACK | Low for invites |
| Fan-out | Watchers | Members | Callees |
| Store | Memory | Log/DB | Signaling + media |
| Compliance | Policy/audit light | eDiscovery heavy | Call records |

### Appendix I — 10× / 100× / 1000× checklist

| Concern | 10× | 100× | 1000× |
|---------|-----|------|-------|
| Store | Redis cluster | Regional cells | Multi-cloud cells |
| Fan-out | Push all | Hot-user pull | Adaptive shed |
| Auth | Entra validate | Token cache + POP | Sovereign identity |
| Privacy | Blocks | Tenant policies | Purview + legal holds on policies |
| Heartbeat | 30s | Idle 90s | Edge coalesce |
| Observability | Basic metrics | Reconnect drills | Cost/heartbeat budgets |

### Appendix J — Sample interview whiteboard script

```text
1. Clarify statuses + privacy + multi-device
2. Draw planes: heartbeat / state / subs / notify / policy
3. Walk heartbeat → TTL → Offline
4. Walk subscribe → change → notify
5. Numbers: heartbeat QPS
6. Hot user problem
7. Entra + tenant isolation
8. Degrade order
9. Close with non-goals (not chat SoT)
```

### Appendix K — Glossary

| Term | Meaning |
|------|---------|
| Effective presence | Aggregated status shown to others |
| Material change | Status/version change worth notifying |
| Home cell | Region owning user's presence record |
| Grace TTL | Delay before Offline after missed heartbeats |
| Hot user | Target with watcher count above push cap |
| Appear offline | Privacy mode forcing Offline to others |
| Entra ID | Microsoft identity platform (Azure AD) |
| Purview | Compliance/audit/governance suite |

### Appendix L — Explicit non-goals

1. Durable forever history of every Online flip.  
2. Cross-planet linearizability.  
3. Using presence as authorization for document access.  
4. Guaranteed typing-level delivery for all watchers.  
5. Replacing Exchange free/busy as calendar SoT.

### Appendix M — Related Microsoft systems (talking points)

- **Microsoft Graph Presence APIs** — public shape inspiration.  
- **Azure SignalR / connection gateways** — notify transport.  
- **Teams** — primary consumer; calling sets InACall.  
- **Exchange free/busy** — calendar enrichment, separate SoT.  
- **Entra ID** — authn/z, tenant, guests.  
- **Azure Cache for Redis / Cosmos** — store options (Redis preferred for TTL).  

### Appendix N — Threat model (brief)

| Threat | Mitigation |
|--------|------------|
| Cross-tenant read | tid binding from token |
| Presence stalking | rate limits, privacy defaults |
| Sub bomb (watch everyone) | caps + anomaly detection |
| Spoofed heartbeats | only gateway service identity |
| Token replay | short TTL, POP, binding |
| Notify eavesdrop | TLS; channel auth |

### Appendix O — Capacity worksheet (fill in interview)

```text
Online sessions S = ______
Heartbeat interval H = ______
Heartbeat QPS = S/H = ______
Material rate m = ______
Avg online watchers w = ______
Notify QPS ≈ m*w = ______
Record size R = ______
Hot store ≈ S * R * replicas = ______
Watch list edges E = users * avg_subs = ______
```

### Appendix P — Sample status enum (versioned)

```text
enum PresenceStatus v1 {
  Offline = 0
  Online = 1
  Away = 2
  Busy = 3
  DoNotDisturb = 4
  BeRightBack = 5
  // v2 additions clients must tolerate:
  // InACall = 6
  // InAConference = 7
  // Presenting = 8
}
```

### Appendix Q — Webhook delivery (Graph-style)

```text
Subscription channel type=webhook:
  POST notification URL with PresenceChanged payloads
  Client must respond 2xx quickly; else backoff
  Validation handshake on create
  Not for 3.3M heartbeat/s — only material changes
  Enterprise: respect data residency for webhook target
```

### Appendix R — Pseudocode notify dispatcher

```text
on PresenceChanged(event):
  watchers = inverted_index.lookup(event.user_id, limit=MAX_PUSH+1)
  if watchers.size > MAX_PUSH:
    mark_hot(event.user_id)
    publish_coarse(event)  // or skip push
    return
  for w in watchers:
    if !privacy_allows(w, event.user_id): continue
    gateway = conn_map.get(w)
    if gateway: enqueue(gateway, event)
    # offline watchers: nothing (they batch on next open)
```

### Appendix S — Testing matrix

| Test | Expect |
|------|--------|
| Dual device Online/Away | Effective Online |
| AppearOffline + subscriber | Offline |
| Blocked viewer batch | unknown / omitted |
| Missed 1 heartbeat | still Online (grace) |
| Missed N heartbeats | Offline |
| Hot user 100K watchers | no meltdown; pull mode |
| Wrong tid in token | 401/403 |
| Reconnect 1M users jitter | shed + snapshot |

### Appendix T — Ownership & SEVs

| SEV | Example | Owner |
|-----|---------|-------|
| SEV1 | Cross-tenant presence leak | Presence + Security |
| SEV2 | Global false Offline > 30 min | Presence Platform |
| SEV3 | Notify delay elevated one region | Regional oncall |
| SEV4 | Calendar Busy incorrect | Connector team |

---

*End of Presence Service API system design prep doc.*
