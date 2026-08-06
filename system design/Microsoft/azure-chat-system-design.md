# System Design: Azure / M365 Enterprise Chat

> **Focus areas:** Entra ID · Tenant isolation · Work chat (1:1, groups, channels) · Compliance (Purview) · Retention / eDiscovery / legal hold · Regional Azure · Guest access  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Enterprise invariants first; messaging core reused from generic chat patterns but **governance is not optional**; deal-breakers for “consumer chat + audit log bolted on”  
> **Interview theme:** Microsoft — **Teams / M365 chat** for Azure AD (Entra) organizations  
> **Differentiation:** Sibling `chat-messaging-system-design.md` is the generic messaging core. **This doc** adds hard tenancy, Purview, retention, eDiscovery, legal hold, DLP, guest/B2B, and residency.

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

Goal: design **enterprise chat for Azure/M365 users**—Teams-like messaging where every message lives inside an Entra **tenant**, with realtime UX **and** compliance: retention, eDiscovery, legal hold, DLP, audit, guest access, and regional data residency.

### 1.0 What this is / is not

| Dimension | **Azure / M365 chat (this doc)** | **Generic chat-messaging (sibling)** |
|-----------|-----------------------------------|--------------------------------------|
| Identity | Entra ID users, groups, guests | Generic user accounts |
| Tenancy | Hard isolation by `tid` | Light / optional |
| Chat types | 1:1, group chat, team channels | 1:1 + social groups |
| Compliance | Purview: retention, eDiscovery, hold, DLP | Basic delete/export hooks |
| Admin | M365 admin / compliance portals | App admin light |
| Guests | B2B guest entitlements | Invite links simple |
| Success | Correct chat **+** defendable compliance | Fast correct chat |
| Encryption | Service + optional customer controls; E2EE limited by compliance | E2EE more plausible as phase 2 |

**Scope statement:** Design M365 enterprise chat: Entra-authenticated messaging with tenant isolation, durable conversation logs, realtime delivery, **and** first-class compliance/residency controls—at progressive enterprise scale.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Identity? | Entra ID; MSA only via guest/special | Token `tid`/`oid` everywhere |
| F2 | Chat types? | 1:1, group chat, channel (team-scoped) | Thread models + roster |
| F3 | Realtime? | Yes (Teams clients) | Gateway fleet |
| F4 | History? | Persistent; policy-governed retention | Compliance store coupling |
| F5 | Guests? | B2B guests in chats/teams | Cross-tenant authZ |
| F6 | Retention? | Purview retention labels/policies | Cannot hard-delete if under retain |
| F7 | eDiscovery? | Search/export for custodians | Indexed compliance corpus |
| F8 | Legal hold? | Preserve content immutable | Hold overrides user delete |
| F9 | DLP? | Policy tips / block sensitive sends | Inline or near-inline scan |
| F10 | Admin audit? | Unified audit log | Every privileged action |
| F11 | Residency? | Tenant geo / multi-geo | Home geography for data |
| F12 | Files? | SharePoint/OneDrive pointers | Don't re-store files in chat blob naively |
| F13 | Presence? | Enterprise policy-gated | Presence service + policy |
| F14 | Encryption? | Service encryption; CMK options; limited E2EE | Compliance vs E2EE tension |

**MVP functional scope:**

1. Entra-auth'd 1:1 and group chat send/receive with per-conversation seq.  
2. Team **channels** as conversations scoped to Team + tenant.  
3. Hard **tenant isolation** on every read/write/fan-out.  
4. Realtime gateways + offline sync + push (WNS/FCM/APNs).  
5. Retention policy engine: retain / delete per policy.  
6. Legal hold: preserve beyond user delete.  
7. eDiscovery search/export hooks (async).  
8. Guest B2B access with entitlement checks.  
9. Audit log emission for message access/admin.  
10. Multi-geo residency pinning for tenant.

**Out of MVP:**

- Full meeting/calling SFU design  
- Full Mesh / immersive  
- Perfect global consumer E2EE (conflicts with eDiscovery)  
- Entire SharePoint design  
- Full Defender suite deep dive (hooks)

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Online delivery | p50 < 200–300ms, p99 < 1s in-region after persist |
| N2 | Durability | ACK'd messages durable; compliance copies durable |
| N3 | Isolation | Zero cross-tenant data leak (SEV1) |
| N4 | Compliance correctness | Hold/retention never silently skipped |
| N5 | Availability | 99.9%+ messaging; compliance pipelines async with backlog SLOs |
| N6 | Residency | Data at rest in declared geo |
| N7 | AuthZ | Fail closed; guest least privilege |
| N8 | Scale | Progressive to M365 global |

### 1.3 Cases

**Happy paths**

1. User A and B same tenant: 1:1 chat; realtime + history.  
2. Channel post in Team → members receive; file link in SharePoint.  
3. Guest G in tenant T chat → entitled; other tenants cannot see.  
4. User deletes message → hidden for users; **retained** for compliance if policy requires.  
5. Legal hold on custodian → content preserved; eDiscovery export.  
6. DLP blocks credit card send → policy tip / reject.  
7. Multi-geo EU tenant → storage in EU cells.

**Edge cases**

| Case | Behavior |
|------|----------|
| Cross-tenant message attempt | Deny unless B2B entitlement |
| User delete under legal hold | Client hide; server preserve |
| Retention expire + no hold | Disposable hard delete GC |
| eDiscovery during move/geo | Consistent export story |
| Guest leaves org | Access revoke; content remains per policy |
| Channel with 20K members | Hybrid fan-out (messaging core) |
| DLP service timeout | Fail policy: prefer fail closed for block-mode policies |
| Admin access content | Audited; privileged roles only |
| External federation | Policy-gated |
| Dual-write lag to compliance index | Search eventual; hold on primary store authoritative |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Tenants | 10K | 100K | 1M | Multi-cloud |
| Seats | 5M | 50M | 500M | 500M+ |
| Messages / day | 500M | 5B | 50B | 100B+ |
| Peak send QPS | 10K | 100K | 1M | 2M+ |
| Channels | 1M | 10M | 100M | 1B |
| eDiscovery cases | 1K | 10K | 100K | 1M |
| Geos | 2 | 8 | 20+ | Sovereign |
| Guests | 1M | 10M | 100M | 100M+ |

**Jumps:** 10× = tenant cells + compliance pipeline; 100× = multi-geo, DLP scale, eDiscovery isolation; 1,000× = sovereign clouds, extreme noisy-tenant controls.

### 1.5 Scope repeat-back

> M365 enterprise chat on Entra ID: tenant-isolated 1:1/group/channel messaging reusing generic messaging mechanics (seq, gateways, hybrid fan-out), plus **first-class** Purview retention, legal hold, eDiscovery, DLP, audit, guest B2B, and regional residency. Compliance can delay user-visible delete but must not lose governed content. Distinct from consumer generic chat.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Messaging math

```text
50M seats × 30% DAU = 15M DAU
15M × 40 msgs/day = 600M msgs/day ≈ 7K/s avg; peak 10× ≈ 70K/s

Enterprise: fewer viral megagroups than consumer; more channels + 1:1
Compliance fan-out: each message may generate index/audit events (+1×–3× write amp)
```

### 2.2 Compliance amplification

```text
Message persist (primary)
+ retention state record
+ audit event (sampled or full per policy)
+ search indexer document
+ DLP scan job (async or sync for block)
⇒ design for 2–5× write amplification vs naive chat
```

### 2.3 Storage

```text
600M × 1.5 KB ≈ 0.9 TB/day hot text/metadata
Retention 3–7 years for some industries → multi-PB per large geo
Files in SharePoint; chat stores pointers + previews
eDiscovery exports: ephemeral working sets in secure blob
```

### 2.4 Latency budget

```text
Send path (allow mode DLP async):
  Gateway → Chat → Tenant authZ → Append → ACK → Fan-out
  + async: DLP, index, audit

Send path (block mode DLP sync):
  + DLP p99 budget 50–150ms or fail closed / queue tip
```

### 2.5 Bottlenecks

(1) Hot tenants (2) channel fan-out (3) DLP inline (4) eDiscovery heavy queries (5) retention GC at Petabyte (6) guest token complexity (7) multi-geo placement mistakes.

### 2.6 Cost / frugality

Index only what policies require; sample transport metrics; store files once in SPO; cold tier compliance archives; don't run consumer-grade full E2EE that forces brute-force decrypt for eDiscovery.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Identity / Tenancy | Entra tokens, tenant map, guests | Strong authZ |
| Messaging core | Conv log, seq, fan-out, sync | Strong per conv |
| Connection | Gateways | Ephemeral |
| Compliance control | Retention, hold, DLP policies | Policy strongly read |
| Compliance data | Preserve/index/export | Durable; search eventual |
| Files | SharePoint/OneDrive | Separate SoT |
| Audit | Unified audit log | Append-only |
| Admin / Graph | Management APIs | Control plane |

**Deal-breaker:** implementing delete as physical purge without consulting retention/hold; or indexing messages outside tenant crypto/residency boundary.

### 3.2 Components

1. **Entra ID** — authN, groups, B2B guests, Conditional Access.  
2. **Chat / Channel Service** — send, membership, seq (messaging core).  
3. **Tenant Router** — map tid → geo/cell.  
4. **Connection Gateway Fleet** — Teams clients.  
5. **Message Store** — tenant-sharded conversation logs.  
6. **Fan-out / Sync** — hybrid notify + cursors.  
7. **Policy Engine (Purview)** — retention, DLP, communication compliance.  
8. **Hold Service** — legal / eDiscovery holds.  
9. **Compliance Indexer** — eDiscovery corpus.  
10. **eDiscovery / Export** — cases, custodians, exports.  
11. **DLP Scanner** — sensitive types.  
12. **Audit Emitter** — M365 unified audit.  
13. **SharePoint Connector** — file hosting.  
14. **Presence Policy Adapter** — enterprise presence.  
15. **Graph Chat APIs** — app model.

### 3.3 Tenant isolation model

```text
Every row keyed with tenant_id
Every RPC extracts tid from token (never trust body tid)
Fan-out only to principals entitled in same chat within tenant context
Guest: home tid vs resource tid explicit in authZ
Cross-tenant query = SEV1 bug class
```

### 3.4 Delete semantics (enterprise)

```text
UserDelete(message):
  mark user_visible=false / tombstone for clients
  if legal_hold or retention_retain: keep body in compliance store
  else schedule dispose per policy

GC:
  only if disposable AND not held AND retention expired
```

### 3.5 Trade-offs

| Topic | Choice | Why | Deal-breaker |
|-------|--------|-----|--------------|
| E2EE default | Off / limited | eDiscovery & DLP | Blind consumer E2EE as default enterprise |
| Files | SPO/ODSP pointers | One compliance surface | Duplicate file blobs in chat |
| DLP | Policy modes async/sync | Balance UX/risk | Always skip DLP for speed |
| Search | Separate compliance index | Scale | Prod OLTP full scans for eDiscovery |
| Geo | Tenant home geo | Residency law | Store wherever free capacity |
| Guests | Entitlement graph | Security | Trust email domain only |
| Messaging | Reuse generic core | Speed | Rewrite fan-out from scratch uniquely |

### 3.6 Microsoft themes (heavy)

| Theme | Implication |
|-------|-------------|
| Entra ID | CA, PIM for admins, guest B2B |
| Purview | Retention, eDiscovery, Communication Compliance |
| Multi-Geo | Preferred data location |
| Graph | `/chats`, `/teams/.../channels/.../messages` |
| SharePoint | Files lifecycle & permissions |
| Defender | Threat signals on files/links |
| Azure regions | Cells in geo; sovereign offerings |
| Customer Key / encryption | Enterprise encryption controls |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Teams Client]
     | WSS + Entra token
     v
[Connection Gateway]
     |
     v
[Tenant Router] -----> (geo/cell for tid)
     |
     v
[Chat/Channel Service] --authZ--> [Entra / Entitlements / Guest]
     |                               |
     | append                        v
     v                          [Policy Engine]
[Message Store (tenant-sharded)]
     |
     +--> [Fan-out/Sync] --> Gateways / Push
     |
     +--> [DLP Scanner] --> allow/block/tip
     |
     +--> [Compliance Indexer] --> [eDiscovery Store]
     |
     +--> [Retention/Hold State]
     |
     +--> [Audit Log]

[SharePoint] <--- file refs --- Chat messages
[Purview Portal / Graph] ---> Hold / Search / Export
```

### 4.2 Send sequence (enterprise)

```text
1. Client send with Entra token
2. Gateway → Chat Service in tenant home geo
3. Validate tid/oid; load membership; guest entitlements
4. Evaluate DLP (sync if block mode)
5. Append MessageEvent with seq; persist retention labels snapshot
6. ACK client
7. Fan-out to entitled members' sessions
8. Async: audit, compliance index, communication compliance classifiers
```

### 4.3 Legal hold + user delete

```text
User clicks Delete
  → Chat Service writes DELETE tombstone for UX (seq++)
  → body remains if HoldService.isHeld(custodian|location)
  → clients hide content
  → eDiscovery still finds body
When hold released AND retention expired → GC eligible
```

### 4.4 Multi-geo

```text
Tenant Contoso: preferred location = EU
  Message store EU cells
  Compliance index EU
  Gateways may be global edges; writes land in EU home
US collaborator guest: content still in Contoso EU store (resource tenant)
```

### 4.5 Relationship to generic chat

```text
+--------------------------------------+
| Enterprise control plane (this doc)  |
|  Tenancy, Purview, Hold, DLP, Audit  |
+------------------+-------------------+
                   |
                   v
+--------------------------------------+
| Messaging core (sibling patterns)    |
|  Seq log, gateways, hybrid fan-out   |
+--------------------------------------+
```

---

## 5. Design Deep Dive

### 5.1 Reliability / compliance invariants

1. **Tenant isolation absolute** — automated tests + invariants.  
2. **ACK ⇒ durable in tenant home store**.  
3. **Hold overrides user delete**.  
4. **Retention retain overrides casual GC**.  
5. **AuthZ fail closed** for guests and apps.  
6. **Audit privileged access**.  
7. **Residency**: at-rest data in geo.  
8. **DLP block-mode**: prefer fail closed on scanner outage (configurable with risk acceptance).  
9. **Idempotent client_msg_id** (messaging core).  
10. **eDiscovery export authenticity** — complete relative to hold scope.  
11. **No cross-tenant fan-out**.  
12. **Policy snapshot** on message for later disposition explainability.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Per-tenant logical partition in shared store; single geo; basic retention |
| 10× | Tenant cells; async compliance pipeline; hybrid channel fan-out |
| 100× | Multi-geo; DLP scale-out; eDiscovery query isolation; noisy neighbor |
| 1000× | Sovereign; dedicated compliance processing; extreme tenant isolation SKUs |

### 5.3 Maintainability

- Policy-as-data from Purview.  
- Clear ownership: Messaging vs Compliance vs Identity.  
- Canary tenants for retention code.  
- Chaos: indexer down—chat still works; search lag SLO.  
- Regular “delete vs hold” game-day drills.  
- Schema versioning for message events **and** compliance docs.

### 5.4 Progressive scale narrative

**1×:** Single geo enterprise chat; Entra; retention simple; eDiscovery export batch.  
**10×:** Teams-like channels; guest B2B; DLP; audit full.  
**100×:** Multi-geo; huge tenants; communication compliance ML; Graph ecosystem.  
**1000×:** Global M365; sovereign clouds; specialized government holdings.

### 5.5 Why not plain E2EE

```text
Enterprise requirements:
  - eDiscovery
  - DLP
  - supervision / communication compliance
  - legal hold
These need server-side authorized access paths
⇒ default service encryption + strict RBAC/audit
Optional encrypted-with-customer-key
True E2EE only for special product modes with compliance trade-offs disclosed
```

**Interview signal:** state the tension explicitly—Microsoft interviewers expect it.

### 5.6 Tenant routing & cells

```text
tid → {geo, cell, encryption_domain}
Cell isolation limits blast radius
Noisy tenant → dedicated cell
Migration between geos: controlled, rare, compliance-reviewed
```

### 5.7 Guest / B2B authZ

```text
Guest token: home tenant + invited resource tenant
Authorize:
  - invitation accepted
  - chat/team membership
  - external access policies
  - Conditional Access satisfied
Revocation: disable user / remove membership → immediate deny on sync/send
```

### 5.8 Retention engine

```text
Policies: retain for T years; delete after; or keep nothing special
Locations: chats, channels, users
On write: compute applicable labels → store on message
Disposition job: query expired candidates → skip if held → purge
User delete ≠ disposition
```

### 5.9 Legal hold

```text
Hold scope: users, teams, chats, queries
Implementation:
  - preserve flag on content locations
  - or copy-on-delete into hold store (design choice)
Interview choice: preserve-in-place + tombstone UX (simpler narrative)
Exports: pull from preserve store with chain-of-custody metadata
```

### 5.10 eDiscovery

```text
Async index pipeline → compliance search cluster (tenant-scoped)
Case → custodians → search → preview → export
Query load isolated from chat OLTP
False negatives from lag: show index freshness; hold based on primary
```

### 5.11 DLP deep dive

| Mode | Path | Failure mode |
|------|------|--------------|
| Audit only | Async | Log only |
| Tip | Near-inline | Warn user |
| Block | Sync evaluate | Fail closed / open per policy |

Sensitive types: creds, PCI, health—configurable. Performance: cache policy; short-circuit small messages; async for large.

### 5.12 Channels vs chats

| | Group chat | Channel |
|-|------------|---------|
| Membership | Explicit roster | Team membership (+ roles) |
| History for new members | Policy | Often from join / team policy |
| Fan-out | Hybrid | Hybrid; larger |
| Files | Chat files folder | Channel SPO folder |
| Compliance location | Chat | Channel/team |

### 5.13 Files & compliance

```text
Message contains sharepoint_item_id / sharing link
File content compliance primarily in SPO pipeline
Chat eDiscovery must join message metadata + file artifacts
Delete message ≠ delete file necessarily (product rules)
```

### 5.14 Failure modes

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Indexer lag | Late eDiscovery | Freshness SLO; primary hold |
| DLP outage | Block or tip degrade | Explicit policy |
| Wrong geo write | Residency incident | Router hard checks |
| Guest token confusion | 403s / leaks | Entitlement cache + tests |
| Retention GC bug | Premature purge | Hold double-check; canaries |
| Hot tenant | Latency | Dedicated cell; rate limits |

### 5.15 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Physical delete on user delete | Legal SEV |
| Shared index without tenant key | Cross-tenant leak |
| E2EE default ignoring eDiscovery | Product lie |
| Store all files again in chat | Dual compliance hell |
| Trust client-sent tenantId | Breach |
| Run eDiscovery queries on OLTP | Melts chat |
| Fail open always on DLP block policies | Data loss events |
| Global multi-master message append | Conflicts + residency pain |

### 5.16 Security

- Entra CA / MFA for clients.  
- App permissions via Graph admin consent.  
- Least privilege for compliance officers.  
- Export packages encrypted; access audited.  
- Transport TLS; at rest service encryption (+ CMK story).  
- Anti-abuse: spam in tenants, malicious guests.

### 5.17 Maintainability: policy explainability

Admins ask “why was this kept/deleted?”  
Store **policy decision IDs** with messages; disposition logs immutable.

### 5.18 Integration with presence

Enterprise presence may hide status via org policy; chat send still allowed. Don't couple availability to authZ for messaging.

### 5.19 Graph API surface

```text
Apps use Graph with application or delegated permissions
Enforce same tenant + compliance constraints
Throttling per app+tenant
Audit app reads of messages (especially application permissions)
```

### 5.20 Reliability: dual stores?

```text
Primary message log = UX + hold preserve-in-place
Compliance index = derived
If conflict: primary wins for preservation
Never index-only without primary durability
```

---

## 6. Wrap-Up

### 6.1 Designed

Azure/M365 enterprise chat: Entra tenancy, messaging core (seq/gateways/hybrid fan-out), Purview retention/hold/eDiscovery/DLP, guest B2B, SharePoint file pointers, multi-geo residency, unified audit—progressive scale with noisy-tenant isolation.

### 6.2 Decisions to defend

1. Hard `tid` isolation on every path  
2. Messaging core reused; compliance plane separate but authoritative for delete  
3. Preserve-in-place legal hold  
4. Limited E2EE due to compliance  
5. Files in SPO not duplicated  
6. Tenant home geo routing  
7. DLP modes explicit  
8. eDiscovery off OLTP  

### 6.3 Risks

- Premature GC bugs  
- Cross-tenant regressions  
- DLP latency vs security  
- Multi-geo migration  
- Index freshness disputes in litigation  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Differentiate from generic chat; Entra/tenant |
| 5–15 | Send path + isolation + seq |
| 15–25 | Retention, hold, delete semantics |
| 25–35 | eDiscovery, DLP, guests, geo |
| 35–45 | Scale, deal-breakers, SEVs |

### 6.5 Closer

> **Azure Chat**: Teams-class enterprise messaging where Entra tenant isolation and Purview compliance are as sacred as realtime delivery—consumer chat patterns reused, governance never bolted on as an afterthought.

---

## 7. Deeper / Related Interview Questions

### 7.1 Conceptual

1. How does this differ from generic chat-messaging?  
2. Why is user delete not physical delete?  
3. Explain preserve-in-place hold.  
4. Why is default E2EE problematic in M365?  
5. How do guests authorize against a resource tenant?  
6. Channel vs group chat membership models.  
7. Where should files live and why?  
8. What is policy snapshotting on write?  
9. Fail closed vs open for DLP.  
10. Why isolate eDiscovery from OLTP?

### 7.2 Quantitative

11. Write amplification if audit+index+DLP async per message.  
12. Storage for 5B msgs/day retained 7 years × 1 KB.  
13. Channel 30K members, 5% active—fan-out strategy.  
14. eDiscovery case scanning 10M messages—architecture.  
15. Multi-geo: % of tenants needing non-default geo.

### 7.3 Failure & compliance

16. Indexer silent drop—detection?  
17. GC deletes held content—prevention layers?  
18. Mis-routed message to wrong geo—incident response.  
19. Guest retains access after leaving—fix?  
20. Export tampering defenses.

### 7.4 Microsoft-flavored

21. Map to Microsoft Graph chat APIs.  
22. Purview retention labels vs policies.  
23. Communication Compliance supervision queues.  
24. Conditional Access impacting gateway sessions.  
25. Customer Key / BYOK implications for search.

### 7.5 Compare

26. Slack Enterprise Grid vs this.  
27. WhatsApp E2EE vs Teams compliance.  
28. Email litigation hold vs chat hold.  
29. Azure Key Vault role when storing chat CMKs.  
30. Presence privacy policies vs chat authZ.

### 7.6 Stretch

31. Design multi-geo tenant move.  
32. Encrypted export with dual control.  
33. Real-time translation compliance implications.  
34. Message recall across devices + compliance.  
35. Sovereign cloud federation limits.

---

## 8. Appendices

### Appendix A — API sketches (Graph-flavored)

#### A.1 Send channel message

```http
POST /teams/{teamId}/channels/{channelId}/messages
Authorization: Bearer {entra_token}
{
  "body": { "contentType": "html", "content": "Ship it" }
}
```

#### A.2 Send chat message

```http
POST /chats/{chatId}/messages
{
  "body": { "contentType": "text", "content": "hello" },
  "clientMsgId": "b7c2..."
}
```

#### A.3 Sync (internal)

```http
GET /internal/v1/tenants/{tid}/sync?cursor=...
→ envelopes with seq-ordered events
```

### Appendix B — Schemas

#### B.1 Tenant placement

```text
TenantPlacement {
  tenant_id: UUID
  preferred_geo: EU | US | APAC | ...
  cell_id: string
  encryption_domain: id
  external_access_policy: ref
}
```

#### B.2 Message (enterprise fields)

```text
MessageEvent {
  tenant_id: UUID
  cid: UUID                 // chat or channel thread
  seq: int64
  message_id: UUID
  client_msg_id: UUID
  sender_oid: UUID
  sender_home_tid: UUID     // for guests
  type: MESSAGE | EDIT | DELETE | SYSTEM
  body: string?
  file_refs: [SharePointRef]
  user_visible: bool
  retention: { policy_ids: [], retain_until: ts? }
  holds: [hold_id]
  dlp: { state: ALLOW|TIP|BLOCK, rule_ids: [] }
  server_ts: ts
}
```

#### B.3 Hold

```text
LegalHold {
  hold_id: UUID
  tenant_id: UUID
  case_id: UUID
  scope: { users: [], teams: [], chats: [] }
  created_by: oid
  created_at: ts
  state: ACTIVE | RELEASED
}
```

#### B.4 Retention decision log

```text
DispositionEvent {
  message_id: UUID
  tenant_id: UUID
  action: RETAIN | DELETE | SKIP_HELD
  policy_id: UUID
  ts: ts
}
```

### Appendix C — AuthZ pseudocode

```text
function authorizeMessageSend(token, cid):
  assert token.valid
  tid = token.tid_resource or routed resource tid
  m = membership.get(tid, cid, token.oid)
  if m missing: deny
  if guest: assert b2b.entitled(token, tid, cid)
  if ca_not_satisfied: deny
  if dlp.block(token, body): deny
  allow
```

### Appendix D — Delete / GC pseudocode

```text
function userDelete(tid, mid):
  write tombstone event (user_visible=false)
  // body remains

function gcCandidate(msg):
  if msg.holds.active: return KEEP
  if now < msg.retention.retain_until: return KEEP
  if policy.requires_retain: return KEEP
  return PURGE
```

### Appendix E — Fan-out with entitlements

```text
function fanout(event):
  members = membership.active(event.tid, event.cid)
  for u in members:
    if !entitled(u, event): continue
    push_or_index(u, event)
```

### Appendix F — DLP evaluation

```text
function dlpCheck(tid, body, mode):
  rules = policyCache.get(tid)
  findings = scan(body, rules)
  if findings and mode == BLOCK: return BLOCK
  if findings and mode == TIP: return TIP
  return ALLOW
```

### Appendix G — eDiscovery flow

```text
Create Case → Add custodians → Apply hold → Search →
Refine → Preview → Export (encrypted package) → Dual-control download → Audit
```

### Appendix H — Multi-geo router

```text
function home(tid):
  p = placement.get(tid)
  return p.geo, p.cell

function write(msg):
  geo, cell = home(msg.tenant_id)
  assert current_cell == cell else forward
  append(msg)
```

### Appendix I — Rate limits (enterprise)

| Scope | Limit ideas |
|-------|-------------|
| User send | Anti-spam |
| App Graph | Per-app per-tenant |
| eDiscovery export | Concurrent case caps |
| Channel post | Large channel throttles |
| Guest invite | Admin-controlled |

### Appendix J — SLO table

| SLO | Target |
|-----|--------|
| Cross-tenant leak | 0 |
| Premature GC of held content | 0 |
| Online deliver p99 | < 1s in-region |
| Index freshness p95 | minutes-class |
| Residency misplacement | 0 |

### Appendix K — Comparison matrix (generic vs azure chat)

| Concern | Generic | Azure chat |
|---------|---------|------------|
| tid on keys | Optional | Mandatory |
| User delete | Often purge/tombstone | Tombstone + retain/hold |
| Search | Product search | Compliance + product |
| Guests | Simple | B2B entitlements |
| Files | Chat blob OK | SPO preferred |
| E2EE | Phase 2 plausible | Conflict with eDiscovery |
| Admin | Light | Purview + Graph |

### Appendix L — SEV taxonomy

| SEV | Example |
|-----|---------|
| SEV1 | Cross-tenant content exposure; held content GC |
| SEV2 | Geo residency violation; tenant-wide outage |
| SEV3 | DLP false allow spike; index lag breach |
| SEV4 | Graph throttle UX |

### Appendix M — Sample retention scenarios

| Scenario | User sees | Compliance sees |
|----------|-----------|-----------------|
| Delete, no retain, no hold | Gone | Gone after GC |
| Delete, retain 3y | Gone | Available |
| Delete, legal hold | Gone | Available |
| Retain expired, hold released | Gone | GC eligible |

### Appendix N — Capacity worksheet

```text
Seats = ______
DAU% = ______
Msgs/day = ______
Compliance write amp = ______
Effective writes/day = ______
Retention years = ______
Cold storage PB = ______
Peak send QPS = ______
```

### Appendix O — Threat model (enterprise)

| Threat | Mitigation |
|--------|------------|
| Cross-tenant read | tid binding; fuzz tests |
| Malicious guest | Entitlement + CA + review |
| Rogue admin | PIM; audit; dual control exports |
| eDiscovery overreach | Role scoping; case ACLs |
| Exfil via app permissions | Admin consent; anomaly detection |
| Residency bypass | Router asserts |

### Appendix P — Observability

Metrics: send_qps_per_tenant, authz_deny, dlp_block, hold_active_count, index_lag, gc_purged, geo_forward  
Alerts: index_lag SLO; unexpected purge of held; cross-tenant deny spikes (or allows!)  

### Appendix Q — Interview script

```text
1. Differentiate from generic chat
2. Entra + tenant isolation
3. Messaging core reuse (seq, fan-out)
4. Delete vs retain vs hold
5. eDiscovery + DLP
6. Guests + multi-geo
7. Deal-breakers / SEV1s
```

### Appendix R — Glossary

| Term | Meaning |
|------|---------|
| Entra ID | Microsoft identity platform |
| tid / oid | Tenant id / user object id |
| Purview | Compliance suite |
| Legal hold | Preserve content for litigation |
| Retention | Keep/delete policies by time |
| eDiscovery | Search/export for legal |
| DLP | Data loss prevention |
| B2B guest | External user invited to tenant |
| Multi-Geo | Preferred data location |
| SPO | SharePoint Online |
| Communication Compliance | Supervision of messages |

### Appendix S — Explicit non-goals

1. Consumer anonymous chat.  
2. Default sealed E2EE destroying eDiscovery.  
3. Rebuilding SharePoint inside chat.  
4. Global multi-master writes across geos.  
5. Using presence as ACL for documents.

### Appendix T — Related docs

- `chat-messaging-system-design.md` — generic messaging core  
- `presence-service-api-system-design.md` — presence  
- `azure-key-vault-system-design.md` — CMK / secrets custody  

### Appendix U — Policy decision record example

```json
{
  "messageId": "m_...",
  "tenantId": "t_...",
  "retentionPolicyIds": ["ret_3y_chats"],
  "holds": ["hold_case_9"],
  "dlp": {"mode": "block", "rules": []},
  "geo": "EU"
}
```

### Appendix V — Guest lifecycle

```text
Invite → Redeem → Membership → Access chat
Remove / account disabled → Access revoke
Content remains in resource tenant per retention/hold
```

### Appendix W — Channel fan-out modes

| Size | Mode |
|------|------|
| < 100 | Push all online |
| 100–5K | Push recent actives; others sync |
| 5K+ | Pull-heavy; notify mentions/@team specially |

### Appendix X — Encryption layers

```text
TLS in transit
Service encryption at rest
Optional customer key for tenant domain
Application permissions still decrypt for authorized compliance roles
Audit all privileged decrypt/export
```

### Appendix Y — Testing matrix

| Test | Expect |
|------|--------|
| Cross-tenant get by id | Deny |
| Delete under hold | Hidden UX; present in eDiscovery |
| Guest removed | Sync/send deny |
| Wrong geo cell | Forward or reject write |
| DLP block | 403/policy tip; no fan-out |
| Indexer down | Chat OK; search lag |

### Appendix Z — Closing checklist

- [ ] Differentiated from generic chat  
- [ ] Entra tid isolation  
- [ ] Delete/retain/hold story  
- [ ] eDiscovery off OLTP  
- [ ] DLP modes  
- [ ] Guests + geo  
- [ ] Files via SPO  
- [ ] SEV1 deal-breakers named  

---

*End of Azure / M365 Enterprise Chat system design prep doc.*
