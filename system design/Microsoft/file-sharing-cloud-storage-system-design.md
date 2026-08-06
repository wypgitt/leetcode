# System Design: File-Sharing Cloud Storage (Enterprise / Collaboration)

> **Focus areas:** Enterprise file share · Namespaces & permissions · Collaboration (co-auth hooks) · Link sharing · Audit/DLP · Metadata vs blob planes · Versioning · Multi-tenant Azure / M365-shaped tenancy  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Distinct from consumer Dropbox sync clients; focus on **share/collaboration control plane**, ACL correctness, audit, and tenant isolation  
> **Interview theme:** Microsoft — SharePoint/OneDrive-for-Business–adjacent enterprise file sharing (not consumer sync protocol deep-dive)

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

Goal: **bound the product**—an **enterprise / generic file-sharing and collaboration storage** service: tenants create sites/drives/folders/files, share with users/groups via ACLs and links, preview/co-author through app hooks, retain versions, and satisfy **audit, DLP, eDiscovery, residency**. This is **not** primarily a consumer “sync-every-filesystem-event across laptops” design (see Dropbox-style docs); sync clients may exist but the interview center of gravity is **sharing, permissions, collaboration, and compliance**.

### 1.0 What this is / is not

| Dimension | This doc (enterprise file share) | Not this (consumer Dropbox sync) |
|-----------|----------------------------------|----------------------------------|
| Primary job | Share + collaborate + govern files in tenants | Multi-device filesystem sync protocol |
| Hard problem | ACL/inheritance, links, audit, DLP, search | Chunk sync, block dedupe, conflict UI |
| Identity | Entra ID users/groups/guests | Consumer MSA-heavy |
| Namespace | Tenant → site/drive → folder tree | Personal root + shared folders |
| Collaboration | Lock/co-auth session hooks, comments | Mostly file replace versions |
| Compliance | Retention, eDiscovery, DLP, WORM optional | Lighter consumer privacy |
| Microsoft lens | SharePoint/OneDrive/Graph-like | Pure sync engine |

**Scope statement:**

> Design a multi-tenant enterprise file-sharing cloud: hierarchical drives, upload/download via blob plane, fine-grained sharing (users/groups/links), versioning, preview/co-auth hooks, search, and compliance controls—scaled from mid-market tenants through 10× / 100× / 1,000× with metadata/blob split and tenant cells.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Tenancy? | Many enterprise tenants; sites/drives inside | Tenant_id everywhere; quotas |
| F2 | Objects? | Files + folders; metadata; versions | Namespace service + blob store |
| F3 | Upload? | Resumable multipart; large files | Upload sessions; checksums |
| F4 | Download? | Authorized URLs (short-lived SAS-like) | AuthZ then redirect/sign |
| F5 | Sharing? | User/group ACL + sharing links (view/edit) | ACL graph + link service |
| F6 | Inheritance? | Folder ACL inherit with break-glass | Efficient permission eval |
| F7 | Collaboration? | Check-out lock OR co-auth app hooks | Lock service; WOPI-like |
| F8 | Versioning? | Keep N versions / Viva retention | Version chain |
| F9 | Search? | Title + full-text + ACL-filtered | Index with security trimming |
| F10 | Preview? | PDF/image/office preview | Async rendition pipeline |
| F11 | Audit? | Who viewed/shared/downloaded | Immutable audit |
| F12 | DLP? | Policy prevent external share of sensitive | Classification + enforce |
| F13 | Guests? | External users via B2B | Guest identity + expiry |
| F14 | Admin? | Retention, legal hold, eDiscovery export | Compliance plane |

**MVP functional scope:**

1. Tenant/drive/folder/file CRUD metadata.  
2. Resumable upload to blob store; download via signed URL after AuthZ.  
3. Share with users/groups; view/edit roles; basic sharing links.  
4. Version on overwrite; list/restore version.  
5. Basic search by name; ACL filtered.  
6. Audit log for share/open/download.  
7. Simple DLP rule: block anonymous links for labeled “confidential.”  
8. Optional file lock for edit.

**Out of MVP:**

- Perfect WAN POSIX filesystem semantics  
- Global dedupe across all tenants (privacy/legal hard)  
- Full real-time CRDT document editor (hook to separate co-auth service)  
- Consumer selective-sync client protocol deep dive  
- Cross-tenant free-for-all search  

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Metadata latency | p99 < 100–200ms in-region |
| N2 | AuthZ decision | p99 < 20–50ms cached |
| N3 | Upload durability | Erasure-coded / replicated blob; checksum |
| N4 | Consistency | Strong metadata per drive/site; blob immutable content-addressed or versioned |
| N5 | Availability | 99.9%+ metadata; blob multi-AZ |
| N6 | Security trimming | Never leak unauthorized hits in search |
| N7 | Audit completeness | Share/download events durable |
| N8 | Tenant isolation | No cross-tenant access by ID guessing |
| N9 | Residency | Pin tenant data to geo |
| N10 | Scale | Progressive table |

### 1.3 Cases

**Happy paths**

1. User uploads file to folder → metadata commit → blob finalize → searchable.  
2. Share folder with group → members see via inheritance → download signed URL.  
3. Create company link (org-only) → colleague opens → audit.  
4. Co-author: lock or WOPI session → edit in Office web → new version.  
5. DLP blocks anonymous link on confidential file → user notified.  
6. Legal hold prevents delete; eDiscovery export package.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Upload finalize after metadata fail | GC orphan blobs via lease/ref count |
| Concurrent rename/move | Metadata TX / compare version; conflict error |
| ACL change mid-download | Signed URL validity window; short TTL |
| Link leaked externally | Revoke link id; audit; optional expiry/password |
| Inheritance break on subfolder | Store ACL delta; eval walks/caches |
| Search index lag | Eventual; open-by-ID still AuthZ’d against metadata truth |
| Thumbnail poison file | Rendition sandbox; quarantine |
| Tenant over quota | Fail uploads with `413/507` |
| Guest expires | Access denied; cleanup async |
| Ransomware encryption storm | Versioning + anomaly detection + share throttle |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Tenants | 10K | 100K | 1M | 10M |
| Users | 5M | 50M | 500M | 5B |
| Files | 10B | 100B | 1T | 10T |
| Avg file size | 500 KB | 500 KB | 500 KB | 500 KB |
| Metadata QPS (peak) | 50K | 500K | 5M | 50M |
| Upload Gbps (egress/ingress origin) | 40 | 400 | 4K | 40K |
| Share ops / day | 20M | 200M | 2B | 20B |
| Search QPS | 5K | 50K | 500K | 5M |
| Audit events / day | 200M | 2B | 20B | 200B |
| Blob storage | 5 EB units? wait calc | — | — | — |

Storage calc:

```text
10B files × 500 KB = 5e9 × 5e5 = 2.5e15 B = 2.5 PB (baseline)
1000× files → 2.5 EB  (not 5 EB; table note corrected below)
```

| Blob capacity | 2.5 PB | 25 PB | 250 PB | 2.5 EB |

**What each jump forces:**

- **10×:** Metadata sharding by site/drive; signed URL downloads; search security trimming cache.  
- **100×:** Tenant cells; ACL evaluation service; async rendition fleet; audit lake.  
- **1,000×:** Hierarchical namespaces, directory snapshots, edge POPs for blob, policy engine at share-time and download-time.

### 1.5 Etc.

- **Graph-like API** surface preferred (drives/items/permissions).  
- Blobs in **Azure Storage–shaped** system; metadata in partitioned DB.  
- Co-auth via **WOPI-like** interface to Office Online—not implementing OT here.  
- Distinct deliverable from consumer sync: mention sync client as optional consumer of the same API.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split planes

| Plane | Baseline peak | 1000× | Notes |
|-------|---------------|-------|-------|
| Metadata read | 40K QPS | 40M | Cache heavily |
| Metadata write | 10K QPS | 10M | Strong consistency |
| AuthZ checks | 80K QPS | 80M | Often >> metadata |
| Blob PUT/GET | Bandwidth bound | Edge | Don’t proxy bytes via app |
| Search | 5K QPS | 5M | ACL filtered |
| Audit append | 5K+ QPS | 5M+ | Cheap append |

**Critical insight:** **AuthZ QPS** can dominate. Design permission evaluation as its own highly cached plane—not a SQL join forest on every download.

### 2.2 Metadata size

```text
Item row ~500 B–1 KB (name, parent, etag, size, owner, pointers)
10B files × 800 B = 8 TB metadata (plus indexes ~2–3× → ~20 TB)
1000×: ~8 PB metadata → cell partitioning mandatory
ACL entries: often more rows than files (fan-out shares)
```

### 2.3 Bandwidth

```text
Never stream 1 GB Office files through API microservice CPU.
Pattern: AuthZ → short-lived signed URL → client ↔ blob store / CDN.
```

### 2.4 Sharing graph

```text
20M share ops/day ≈ 230/s avg; peak 10× → ~2K/s baseline
Each share may expand to group membership eval (Entra group transitive)
Cache group expansion with TTL + invalidation on group change events
```

### 2.5 Critical bottlenecks

1. **Permission evaluation** (inheritance + groups + links)  
2. **Hot directories** (many children listing)  
3. **Search security trimming**  
4. **Audit volume**  
5. **Rendition storms** (new uploads)  
6. **Tenant noisy neighbor** uploads  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Tenant
  └── Site / Drive
        └── Item tree (folder | file)
              ├── Content (blob_id, hash, size)
              ├── Versions[]
              ├── Permissions (ACL grants)
              └── SharingLinks[]
Lock / CoAuthSession
AuditEvent, RetentionPolicy, LegalHold, DlpLabel
```

### 3.2 Options: permission model

| Option | Pros | Cons | Deal-breaker |
|--------|------|------|--------------|
| A. Per-item ACL only | Simple | Huge storage; slow updates | Large enterprises |
| B. Inheritance + ACEs | Natural UX | Eval complexity | — |
| C. Capabilities only (links) | Easy external | Weak enterprise group mgmt | Enterprise required |
| D. Hybrid B+C | Matches reality | Careful precedence | Ignoring precedence rules |

**Chosen:** **Hybrid inheritance ACLs + sharing links**, with explicit precedence (deny/block external > link > inherit).

### 3.3 Metadata vs blob

| Concern | Metadata plane | Blob plane |
|---------|----------------|------------|
| Names, parents, etags | Yes | No |
| Bytes | Pointer | Yes |
| AuthZ | Decision | Enforced via signature/policy |
| Version | Version records | Immutable blob objects |

**Invariant:** Metadata commit that references blob must ensure blob exists (upload session finalize ordering).

### 3.4 Upload session

```text
1. createUploadSession(item_path, size, hash?) → upload_id + URLs
2. client PUTs chunks to blob (or service)
3. finalize: verify checksum → create/update item metadata → version++
4. enqueue: virus scan, DLP classify, index, rendition
```

### 3.5 AuthZ evaluation (resolve ownership of truth)

```text
Effective access(user, item, action):
  if legal_hold_deny_delete and action=delete → deny
  if DLP policy denies action → deny
  if explicit deny ACE → deny
  if sharing link valid presents token → grant link role
  if user/group ACE on item → grant
  else walk parents inheritance until break or root
  check tenant membership / guest validity
```

Cache: `(user_id, item_id) → allowed_actions` short TTL + invalidation on ACL change.

**Deal-breaker:** Search returning snippets without security trimming.

### 3.6 Collaboration hooks

| Mode | Mechanism |
|------|-----------|
| Exclusive edit | File lock with timeout/heartbeat |
| Co-authoring | WOPI CheckFileInfo / Lock / PutRelative; editor owns OT |
| Comments | Side-car discussion service keyed by item_id |

### 3.7 Search

```text
ItemChanged events → extract text → index document {item_id, tenant, acl_sig, text}
Query → retrieve candidates → **security trim** against AuthZ (or ACL bitmap) → return
```

ACL signature / security descriptor hash helps cache trim decisions.

### 3.8 Compliance plane

- **Retention**: prevent hard delete until expiry.  
- **Legal hold**: block delete/edit per policy.  
- **eDiscovery**: query + export with audit.  
- **DLP**: classify (MIP labels); enforce on share/download.  
- **Customer-managed keys** optional per tenant.

### 3.9 Multi-region / residency

| Plane | Mode |
|-------|------|
| Metadata | Tenant home geo cell |
| Blobs | Same geo; optional RA-GRS for DR |
| Search | Regional index in geo |
| Admin | Global directory of tenants → home cells |

### 3.10 Microsoft flavor

- **Microsoft Graph** shapes (`/drives/{id}/items`)  
- **Entra ID** groups & B2B guests  
- **Purview** DLP/labels analogies  
- **Azure Blob** + CDN  
- **SharePoint** site semantics (libraries)  

---

## 4. Architecture Diagram

### 4.1 Baseline

```text
Clients (Web/Office/Mobile/Sync optional)
        │
        ▼
   API Gateway + Entra Auth
        │
        ├─► Namespace / Item Metadata Service (sharded)
        ├─► Permission / Link Service
        ├─► Upload Session Service ──► Blob Store (multi-AZ)
        ├─► Search Query (security trimmed)
        ├─► Lock / WOPI Host
        └─► Compliance / DLP Policy Engine
                │
                ▼
        Event Bus → Indexer | Rendition | VirusScan | Audit Lake
```

### 4.2 Download path

```text
GET /items/{id}/content
  → AuthZ(action=read)
  → emit Audit(download)
  → 302 / return { signed_url, expires_in }
Client → Blob GET with signature
```

### 4.3 Share path

```text
POST /items/{id}/permissions { grantee, role }
  → AuthZ(action=share)
  → DLP check (external?)
  → write ACE / link
  → invalidate AuthZ caches
  → notify grantee
  → audit
```

### 4.4 Scale-out cells

```text
Global Tenant Directory → Tenant Home Cell
   Cell: Metadata shards | Blob storage account(s) | Search | Audit | Policy
Edge POPs: signed URL download optimization
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Atomicity of upload finalize

Use two-phase: blob committed (sealed) → metadata TX points to blob. On crash: GC scanner deletes unreferenced sealed blobs older than T; or ref-count table.

#### 5.1.2 Versioning & ransomware

Immutable version blobs; soft-delete recycle bin; anomaly: mass modify → alert admin + auto-block share.

#### 5.1.3 Permission invalidation

ACL change publishes `AclChanged(item_subtree_id)`; AuthZ cache subscribers drop keys; search may reindex `acl_sig`.

#### 5.1.4 Failure modes

| Failure | Degradation |
|---------|-------------|
| Search down | Browse namespace still works |
| Rendition down | Download raw still works |
| DLP classifier lag | Fail-closed for external share on unknown-sensitive or fail-open with audit—**explicit choice** (enterprise often fail-closed for external) |
| Metadata shard down | Partial tenant impact; cell HA |

### 5.2 Scalability

#### 5.2.1 Sharding

| Entity | Key |
|--------|-----|
| Items | `(tenant_id, drive_id)` then range by path/id |
| ACL | item_id |
| Audit | tenant_id + time |
| Blob | hash / uuid; storage accounts per cell |

**Hot folder listing:** paginate; materialize child counts; avoid huge directories (soft limits).

#### 5.2.2 Group expansion

Entra group transitive members cached; on webhook group change → invalidate. For huge groups, evaluate membership via token group claims when present (`groups` overage → graph call).

#### 5.2.3 Progressive scale

| Scale | Must have |
|-------|-----------|
| 1× | Metadata DB, blob, ACLs, signed URL |
| 10× | Shards, search trim, audit pipeline |
| 100× | Tenant cells, policy engine, WOPI host scale |
| 1000× | Directory partitioning, edge blob, hierarchical ACL cache |

### 5.3 Maintainability

Clear service boundaries; Graph-compatible API versioning; schema evolution for items; chaos tests on AuthZ cache correctness (prefer deny on uncertainty for external).

### 5.4 Security deep dive

- Signed URLs: scope to blob, short TTL, optional IP bind for sensitive.  
- Link types: anonymous, org, specific people, password, expiry.  
- Antivirus gating before wide sharing (async; pending state).  
- Tenant isolation tests as CI.  
- Privileged admin actions just-in-time + audited.

### 5.5 Collaboration correctness

Locks: lease with heartbeat; fencing token on put; WOPI lock ids.  
Co-auth: editor resolves content conflicts; storage keeps versions on save checkpoints.

### 5.6 Sync client note (boundary)

Optional clients use delta tokens (`delta` query) from metadata change log—**reuse change feed**, but do not center interview on block-level rsync. If asked: “We expose item change journals; sync engine is a client.”

---

## 6. Wrap-Up

### 6.1 What we designed

An **enterprise file-sharing platform** splitting **metadata/ACL/compliance** from **blob bytes**, with inheritance + links, signed downloads, versioning, security-trimmed search, DLP/retention hooks, and tenant home cells—explicitly distinct from consumer Dropbox sync-centric designs.

### 6.2 Key invariants

1. No content access without AuthZ (signed URL is capability).  
2. Search never bypasses security trimming.  
3. Blob bytes not proxied through metadata tier at scale.  
4. Audit for share/download durable.  
5. Tenant residency respected.

### 6.3 Top trade-offs

| Trade-off | Choice | Why |
|-----------|--------|-----|
| Sync vs share focus | Share/collab/compliance | Microsoft enterprise prompt |
| ACL model | Inheritance + links | Real product shape |
| DLP unknown | Fail-closed external | Safer enterprise default |
| Co-auth | WOPI hooks | Don’t rebuild Office OT |
| Dedup cross-tenant | Avoid / careful | Privacy |

### 6.4 60-second pitch

> We separate namespace/ACL metadata from blob storage. Clients upload via resumable sessions, download via short-lived signed URLs after permission evaluation that understands inheritance, groups, and links. Collaboration uses locks or WOPI to Office. Search is ACL-trimmed; DLP and retention enforce at share and delete time. Scale with tenant cells and AuthZ caching—without pretending to be a WAN POSIX disk.

### 6.5 Risks / follow-ups

- Cross-geo collaboration latency  
- Massive group membership churn  
- Advanced eDiscovery analytics  
- Customer key revocation workflows  

---

## 7. Deeper / Related Interview Questions

### 7.1 Permissions

**Q: How do you evaluate inherited ACLs quickly?**  
A: Cache effective ACLs; store inheritance breaks; walk limited depth with memoization; invalidate on subtree changes.

**Q: Deny vs allow precedence?**  
A: Explicit deny wins; document model; test matrices.

**Q: Sharing link vs ACL?**  
A: Link presents capability token; still subject to DLP and revocation.

**Q: Group nesting?**  
A: Transitive expansion cached; overage handling via Graph.

### 7.2 Consistency

**Q: Read-after-write file content?**  
A: Finalize waits until blob sealed + metadata committed; return etag.

**Q: Move folder with millions of children?**  
A: Pointer parent change O(1) if path materialized lazily OR async path rewrite with dual-read—discuss trade-off.

### 7.3 Search

**Q: How to security-trim at scale?**  
A: Index `acl_sig` / granted principal ids carefully (mind group explosion); post-filter with AuthZ; never return unauthorized snippet.

**Q: Encryption of indexed text?**  
A: Tenant keys; limit sensitive extraction per DLP.

### 7.4 Compliance

**Q: Legal hold vs retention?**  
A: Hold blocks deletion regardless of retention expiry until released.

**Q: eDiscovery export size?**  
A: Async jobs; package to secure blob; audit accessors.

### 7.5 vs Dropbox consumer

**Q: Why different from Dropbox design?**  
A: Emphasis on Entra ACLs, compliance, sharing links governance, WOPI—not block sync protocol.

**Q: Can same system support sync?**  
A: Yes via delta API; different hard parts.

### 7.6 Hotspots

**Q: Viral shared folder?**  
A: Cache metadata; CDN for content; rate-limit listing; shard popular drive read replicas.

**Q: Thumbnail stampede?**  
A: Negative cache; queue renditions; serve placeholder.

### 7.7 Reliability drills

1. Finalize crash → orphan GC.  
2. Revoke link → subsequent AuthZ deny; old signed URL expires quickly.  
3. Classifier down → external share fail-closed.  
4. Dual writers metadata → prevented by etag/version CAS.

### 7.8 Microsoft-specific

**Q: Graph API compatibility?**  
A: Model drives/items/permissions; delta queries; thumbnails.  

**Q: Integration with Teams?**  
A: Files stored in site/drive backing team channel; same permission plane.

### 7.9 Security traps

| Trap | Pushback |
|------|----------|
| Long-lived public blob URLs | Leakage |
| Search without trim | Data breach |
| Proxying all bytes via app | Scale/cost |
| Cross-tenant sequential IDs | Enumeration |

### 7.10 Algorithms

**Q: Path storage?**  
A: Parent pointers + materialized path cache; or materialize path string with care on rename.  

**Q: Change feed?**  
A: Per-drive log of item operations for delta sync & indexers.

### 7.11 Interview arithmetic traps

| Trap | Truth |
|------|-------|
| 10B × 500KB = 5EB | **2.5PB** |
| AuthZ negligible | Often hottest path |

### 7.12 Co-auth

**Q: Who wins conflicts?**  
A: Editor service merges; storage versions on save; locks for binary files.

### 7.13 Quotas

**Q: Soft vs hard?**  
A: Soft warn; hard fail uploads; admin overrides audited.

### 7.14 Guest lifecycle

**Q: Orphan shares?**  
A: Periodic reaper on expired guests; notify owners.

---

## 8. Appendices

### 8.1 Schema sketches

```sql
-- tenants(tenant_id, home_geo, quota_bytes, cmk_ref)
-- drives(drive_id, tenant_id, type, root_item_id)
-- items(
--   item_id PK, drive_id, parent_id, name, type,
--   etag, size, blob_id, hash, status, inherit_break BOOL,
--   created_by, updated_at)
-- versions(item_id, version_id, blob_id, size, created_at, created_by)
-- acls(item_id, grantee_type, grantee_id, role, deny BOOL)
-- links(link_id, item_id, role, scope, secret_hash, expires_at, password_hash)
-- locks(item_id, lock_id, owner, expires_at)
-- audit(event_id, tenant_id, actor, action, item_id, ts, details)
-- retention(item_id, policy_id, hold BOOL)
```

### 8.2 API checklist

- [ ] Drive/item CRUD  
- [ ] `createUploadSession` / finalize  
- [ ] `GET content` → signed URL  
- [ ] Permissions & links CRUD  
- [ ] Versions list/restore  
- [ ] Search  
- [ ] Locks / WOPI  
- [ ] Delta / change token  
- [ ] Admin compliance export  

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| Security trimming | Filter search by AuthZ |
| ACE | Access control entry |
| Inheritance break | Stop ACL parent walk |
| Signed URL / SAS | Time-boxed blob capability |
| WOPI | Protocol for Office editors |
| Legal hold | Block delete for investigation |
| Home geo | Tenant residency cell |

### 8.4 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Metadata+blob, ACL, signed URL, versions |
| 10× | Search trim, audit, upload sessions |
| 100× | Cells, DLP, WOPI scale-out |
| 1000× | Edge blob, hierarchical caches, directory partitioning |

### 8.5 Link scopes

| Scope | Who |
|-------|-----|
| anonymous | Anyone with link |
| organization | Tenant members |
| users | Explicit list |
| password | Knowledge factor |

### 8.6 AuthZ cache key

```text
key = hash(user_id, item_id, token_grp_hash, link_id?)
value = {roles, expiry, acl_version}
```

### 8.7 Event types

`ItemCreated`, `ItemUpdated`, `ItemDeleted`, `AclChanged`, `LinkRevoked`, `VersionCreated`, `Download`, `DlpBlocked`.

### 8.8 Interview “say this” summary

> Enterprise file share: metadata/ACL/compliance plane + blob plane; inheritance and links; signed downloads; ACL-trimmed search; WOPI for co-auth; tenant cells—not a consumer sync protocol interview.

### 8.9 Extra traps

| Trap | Pushback |
|------|----------|
| Store files on API VM disks | No |
| Global unique sequential item ids across tenants | Hotspot + leakage |
| Infinite directory children | Soft limits |
| Forever versions no quota | Cost explosion |

### 8.10 Reliability test plan

1. Permission revoke mid-session → next AuthZ deny; URL TTL short.  
2. Upload finalize retry → one version.  
3. Group membership removal → cache invalidation path tested.  
4. Legal hold delete attempt → 403.  
5. Search index lag → no unauthorized results even if stale name match filtered.

### 8.11 Observability SLOs

| SLO | Target |
|-----|--------|
| Metadata p99 | < 200ms |
| AuthZ p99 | < 50ms |
| Upload success | > 99.9% |
| Search unauthorized leak | **0** |
| Audit loss | **0** for critical actions |

### 8.12 Related systems map

```text
Entra → API → Metadata/ACL → signed URL → Blob
                 ↓
              Events → Search / DLP / Rendition / Audit
                 ↓
              WOPI → Office Online
```

### 8.13 Distinct from Dropbox consumer sync doc

| Topic | This doc | Dropbox-like doc |
|-------|----------|------------------|
| Block chunking | Optional | Central |
| Conflict UI multi-device | Light | Central |
| DLP / eDiscovery | Central | Light |
| Entra group ACL | Central | Light |
| WOPI | Central | Rare |

### 8.14 Orphan blob GC

```text
sealed_blobs without metadata ref after T → delete
ref_table increments on finalize; decrement on version expire
```

### 8.15 Directory listing pagination

```text
GET children?$top=200&$skiptoken=...
Avoid OFFSET deep pages; use seek by (name, item_id)
```

### 8.16 Mass rename strategy options

| Strategy | Complexity | Consistency |
|----------|------------|-------------|
| Parent pointer only | Low | Paths computed |
| Materialized path update async | Med | Dual-read window |
| Copy-on-write directory snapshot | High | Elegant at extreme scale |

### 8.17 Virus scan gating

```text
upload finalize → state=scanning → clean → state=available
optional: allow uploader access before clean; block share until clean
```

### 8.18 Capacity cheat-sheet

```text
capacity ≈ files × avg_size
metadata ≈ files × ~1KB × index_factor
authz_qps ≈ (downloads + previews + search) × checks_per
```

### 8.19 Sample permission precedence

```text
1) compliance blocks
2) explicit deny
3) valid link capability
4) direct ACE
5) inherited ACE
6) default deny
```

### 8.20 Final deal-breakers

1. Unsigned forever URLs  
2. Search without security trimming  
3. Bytes through app tier at scale  
4. Ignoring tenant residency  
5. No audit on external shares  

---

*End of file-sharing cloud storage system design.*
