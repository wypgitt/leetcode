# System Design: Git-like Source-Control System

> **Focus areas:** Content-addressed objects · Refs · Packfiles · Clone/fetch/push · Branching/merging · Large repos / monorepos · AuthZ · Shallow/partial clone · GC · Server-side scaling  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct content-addressing math, explicit pack/delta strategy, ref transaction safety, deal-breakers for “SQL blob per file version” at monorepo scale  
> **Interview theme:** Google L5+ — design a Git-class VCS backend (think Piper/Git hosting) with efficient sync, branching, and huge repositories

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

Goal: **bound the product**—a **Git-like source-control system**: content-addressed object store, mutable refs (branches/tags), efficient **clone/fetch/push**, branching workflows, and scale to **large/monorepo** footprints with auth.

### 1.0 What this is / is not

| Dimension | **Git-like source control (this doc)** | Not this |
|-----------|----------------------------------------|----------|
| Primary job | Version files/trees/commits; sync peers | CI/CD product (hooks only) |
| Object model | Content-addressed DAG (blob/tree/commit/tag) | Mutable file overwrite DB |
| Sync | Negotiate missing objects; pack transfer | Always zip whole tree |
| Auth | Repo/branch ACLs; signed pushes optional | Public anonymous write |
| Success | Correct history, fast fetch, safe refs | Real-time Google Docs collab |

**Scope statement:** Design a Git-compatible (or Git-inspired) source-control service: object storage, ref transactions, pack negotiation, branching, auth, and progressive scale to giant monorepos.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Client compatibility? | Prefer Git wire protocol / smart HTTP | Speak fetch-pack / receive-pack |
| F2 | Object types? | blob, tree, commit, tag | Classic Git model |
| F3 | Branching? | Create/delete/fast-forward/force (ACL) | Ref updates atomic |
| F4 | Merge? | Client-side merge; server stores results | Optional server merge later |
| F5 | Clone/fetch? | Full, shallow, partial (blobless/treeless) | Filter + pack |
| F6 | Push checks? | Auth, size limits, hooks, signed commits | Pre-receive hooks |
| F7 | Large files? | LFS or cas pointer | Separate blob store |
| F8 | Monorepo? | Yes — sparse checkout / partial clone | Path filters; virtual FS hooks |
| F9 | Auth? | SSO + fine-grained path/branch ACL | AuthZ service |
| F10 | Code review? | Out of MVP; PR refs as extension | `refs/pull/...` hooks |
| F11 | Mirroring? | Read replicas geo | Async object + ref replicate |
| F12 | GC? | Unreachable object collection | Careful with pending pushes |

**MVP functional scope:**

1. Content-addressed store for blobs/trees/commits/tags.  
2. Refs: `refs/heads/*`, `refs/tags/*` with atomic compare-and-swap.  
3. Smart HTTP (or SSH) upload-pack / receive-pack.  
4. Packfile generation with deltas; thin packs on push.  
5. Clone, fetch, push; shallow clone depth=N.  
6. AuthN (tokens/SSH keys) + AuthZ (repo read/write; protected branches).  
7. Server-side quarantine + hooks (block secrets patterns basic).  
8. Read replicas; primary for ref mutations.  
9. LFS pointers for large binaries.  
10. Basic GC and pack maintenance.

**Out of MVP:**

- Full Piper-style virtual FS + citc workspaces as required  
- Real-time multi-cursor editing  
- Guaranteed GitHub-compatible every extension  
- Server-side merge queue product (mention Phase 1.5)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Durability | No lost commits after ACK push | Multi-AZ object store + WAL refs |
| N2 | Ref correctness | No lost updates / torn refs | Conditional update / transaction |
| N3 | Fetch latency | Interactive for delta sync | p50 seconds for typical day-of-dev |
| N4 | Clone large repo | Must not require full history always | Partial/shallow defaults for mono |
| N5 | Availability read | High | Replicas; stale refs bounded |
| N6 | Write availability | Primary region | Failover runbook |
| N7 | Integrity | Corrupt object detection | Hash verify on receive |
| N8 | Scale | Monorepo TB-class object corpus | Pack sharding; CDN for packs |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. `git clone` → advertise refs → want/have → pack → checkout.  
2. Dev commits locally → `push` → thin pack → server indexes → ref FF update.  
3. `fetch` after day → small pack of new commits/trees/blobs.  
4. Create branch → push new ref → protected main requires review hook.  
5. Tag release → immutable annotated tag object + ref.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Non-FF push to main | Reject unless force+ACL |
| Concurrent pushes same branch | One CAS wins; other retry |
| Corrupt pack | Reject; quarantine |
| Push secret | Hook reject |
| Huge binary | LFS redirect / reject over limit |
| GC deletes object still needed by in-flight clone | Grace period / recent reachable |
| Partial clone missing blob on checkout | Lazy fetch from promisor remote |
| History rewrite force-push | ACL; notify; optional reflog server |
| Fanout 10K clones of mono | Pack cache / CDN bundle |
| Repo delete | Soft delete; GC later |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Repos | 10K | 100K | 1M | 10M |
| Object corpus | 10 TB | 100 TB | 1 PB | 10 PB |
| Peak fetches/s | 100 | 1K | 10K | 100K |
| Peak pushes/s | 20 | 200 | 2K | 20K |
| Largest repo | 50 GB | 500 GB | 5 TB | monorepo fleet |
| Refs / large repo | 5K | 50K | 500K | millions |
| Avg pack size fetch | 5 MB | 5–20 MB | CDN | edge |
| Engineers | 5K | 50K | 100K+ | company-wide |

**What each jump forces:**

- **10×:** Pack caching; read replicas; LFS; protected branch service.  
- **100×:** Partial clone default; pack CDN; ref namespace sharding; GC fleet.  
- **1,000×:** Content-addressed global CAS; monorepo virtualization; cell/regional primaries; bundle streaming.

### 1.5 Etc. (Constraints & Assumptions)

- Clients can be official Git or compatible SDK.  
- Network is WAN — optimize round trips (protocol v2).  
- Objects immutable; refs mutable.  
- SHA-1 legacy vs SHA-256 transition — design hash-agnostic IDs.  
- We are not redesigning three-way merge algebra in depth (client).

**Scope statement to repeat back:**

> Design a Git-like source-control system with content-addressed objects, atomic refs, pack-based sync, auth, and progressive scale including partial clone and pack CDN for monorepos—without storing each file version as an independent SQL row.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Content addressing

```text
blob = hash(header + content)
Identical files across commits/repos → same object ID → natural dedup
```

Monorepo 10M files, avg 4 KB, but only 1% unique new per week:

```text
Naive full snapshots weekly = disaster
Delta + content-address → store unique blobs only
```

### 2.2 History growth

```text
Commits/day = 50K (large co)
Avg new compressed objects / commit = 200 KB equivalent
→ ~10 GB/day raw object growth before packing efficiency
Packs/deltas often 2–10× savings on similar trees
```

### 2.3 Clone cost

```text
Full history mono 2 TB pack — unacceptable default
Shallow depth=1: trees+blobs of tip ≈ 20–100 GB still painful
Partial clone (blobless): commit+tree graph much smaller; blobs lazy
Sparse checkout: working tree subset
```

**Deal-breaker:** “Everyone full-clones the monorepo” as the only mode.

### 2.4 Fetch negotiation

```text
have: local tips; want: remote tips
Server computes reachability difference → pack
Protocol v2: ls-refs filtered → fewer round trips
```

### 2.5 Ref store size

```text
500K refs × 100 B ≈ 50 MB — fine
But updates must be transactional; hot main ref = contention point
```

### 2.6 Pack CPU

```text
Delta compression CPU-heavy
Cache generated packs for popular `(wants, haves)` approximate keys
Or precompute bundles for main HEAD hourly
```

---

## 3. High-Level Design

### 3.1 Object model

```text
blob  := file bytes
tree  := list of (mode, name, oid)
commit:= tree oid + parent oids + author + message
tag   := object oid + name + tagger + message
```

DAG: commits → trees → blobs; merges have multiple parents.

### 3.2 Storage layout

| Layer | Store | Notes |
|-------|-------|-------|
| Loose objects (rare) | CAS path `ab/cdef...` | Small/dev |
| Packfiles | `pack-*.pack` + `.idx` | Primary |
| Multi-pack-index | midx | Fast lookup |
| LFS | Separate OID store | Pointers in git |
| Refs | DB / reftable | Atomic CAS |
| Reflog / audit | Append log | Ops |

### 3.3 Wire API

```text
GET  /info/refs?service=git-upload-pack
POST /git-upload-pack     # fetch/clone
GET  /info/refs?service=git-receive-pack
POST /git-receive-pack    # push
SSH: git-upload-pack / git-receive-pack
```

Protocol v2 commands: `ls-refs`, `fetch` with filters (`blob:none`, `tree:<depth>`).

### 3.4 Push transaction

```text
1. AuthZ
2. Receive pack into quarantine
3. Index + verify hashes + connectivity (all new tips reachable)
4. Pre-receive hooks
5. Update refs (CAS old→new) in one transaction
6. Promote quarantined objects
7. Post-receive hooks (CI)
```

### 3.5 Why X over Y

| Decision | Choice | Reject |
|----------|--------|--------|
| Identity | Hash of content | Auto-increment file versions |
| Sync | Negotiate + pack deltas | Always full tree tarball |
| Refs | CAS/transactional | Last-write-wins file edit |
| Large files | LFS pointers | Unlimited blobs in Git packs |
| Monorepo | Partial/sparse | Mandate full clone |
| Read scale | Replicas + pack CDN | Single NFS server |

---

## 4. Architecture Diagram

### 4.1 Serving path

```text
 Client (git)
     │ HTTPS/SSH
     ▼
┌──────────────┐     ┌─────────────┐
│ Front / Auth │────►│ AuthZ       │
└──────┬───────┘     └─────────────┘
       │
       ▼
┌──────────────┐     ┌──────────────────────────┐
│ Upload/Recv  │────►│ Ref Service (primary)     │
│ Pack worker  │     └────────────┬─────────────┘
└──────┬───────┘                  │
       │                          ▼
       │                 ┌──────────────────┐
       └────────────────►│ Object CAS       │
                         │ (packs, midx)    │
                         └────────┬─────────┘
                                  │ replicate
                         ┌────────▼─────────┐
                         │ Read replicas /   │
                         │ Pack CDN edge     │
                         └──────────────────┘
```

### 4.2 Object DAG

```text
commit C2 ──parent──► commit C1
   │                     │
   ▼                     ▼
 tree T2                tree T1
   ├── blob A           ├── blob A  (shared OID)
   └── blob B           └── blob C
```

### 4.3 Fetch negotiation

```text
Client: want main(C5), have C2
Server: objects = reachable(C5) \ reachable(C2)
        pack(objects, delta_base_prefers_client_haves)
Client: index pack → update remote-tracking refs
```

### 4.4 Monorepo partial clone

```text
clone --filter=blob:none
  → commits+trees only
checkout path/ui
  → lazy fetch blobs for ui/**
promisor remote serves missing OIDs
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **Object immutability:** OID → bytes never change.  
2. **Hash integrity:** reject mismatch on receive.  
3. **Ref updates atomic** with expected old OID (CAS).  
4. **Connectivity:** new ref tips must have full closure in store.  
5. **ACK push ⇒ durable** objects+ref.  
6. **GC never deletes objects reachable from any ref / recent tips / grace.**

#### 5.1.2 Ref transactions

```text
UPDATE refs/heads/main
SET oid=$new WHERE oid=$old
commit with pack promotion
```

Compare-and-swap prevents lost updates when two pushes race.

**Deal-breaker:** racy “read ref, write ref” without CAS.

#### 5.1.3 Quarantine

Pushes land in quarantine so failed hooks don’t pollute CAS with unreachable spam (or isolate until refs move).

#### 5.1.4 Replication

| Data | Mode |
|------|------|
| Objects | Async replicate; fetch can proxy-miss to primary |
| Refs | Sync to quorum/primary; replicas may lag slightly for reads |
| Cross-region | Primary writes; others read-only or regional repos |

#### 5.1.5 Failure modes by scale

| Scale | Risk | Mitigation |
|-------|------|------------|
| Baseline | Disk corrupt | Checksums; multi-AZ |
| 10× | Pack CPU spike | Bundle cache |
| 100× | Ref DB hotspot | Reftable / shard by repo |
| 1,000× | GC races | Grace; generation numbers |

### 5.2 Scalability

#### 5.2.1 Packfiles & deltas

```text
Objects sorted by type/name/size heuristics
Delta against similar objects (same path history)
Thin pack: deltas against bases client already has
```

Multi-pack-index avoids linear scan of many packs.

#### 5.2.2 Pack caching / bundles

```text
Prebuild bundle: main@{hourly} full snapshot for clones
CDN: immutable pack URLs by content hash
Fetch workers generate incremental packs; cache by tip pair
```

#### 5.2.3 Partial clone & sparse

| Technique | Saves |
|-----------|-------|
| `--depth` | History |
| `--filter=blob:none` | Blob bytes |
| Sparse checkout | Working tree |
| Split repos / submodules | Organizational — tradeoffs |

Google-scale monorepos often add **virtual FS** (not full MVP) — mention as Phase 2.

#### 5.2.4 AuthZ at scale

```text
repo-level ACL hot path cached
path-level ACL on push (changed paths) — expensive; cache rules
protected branches: only service account / merge bot
```

#### 5.2.5 Progressive scale narrative

| Jump | Change |
|------|--------|
| →10× | Replicas, LFS, pack cache |
| →100× | Partial clone default, CDN, GC fleet |
| →1,000× | Global CAS cells, monorepo VFS, regional primaries |

### 5.3 Maintainability

#### 5.3.1 Config as data

```text
max_push_bytes: 5GB
max_blob_bytes: 100MB  # else LFS
hook_timeout_s: 30
gc_grace_days: 14
pack_window: 10
protocol: v2
default_filter: blob:none  # for mono repos
```

#### 5.3.2 Observability

| Metric | Why |
|--------|-----|
| `fetch_bytes` / `fetch_latency` | User experience |
| `pack_cpu_seconds` | Capacity |
| `push_reject_total{reason}` | Auth/hook/FF |
| `ref_cas_conflict` | Contention |
| `object_verify_fail` | Corruption/attacks |
| `gc_deleted_objects` | Storage |
| `lfs_bandwidth` | Large media |

#### 5.3.3 Testing

- Corrupt pack fuzz.  
- Concurrent push CAS tests.  
- Partial clone lazy-fetch correctness.  
- GC reachability vs in-flight clones.  
- SHA transition dual-hash fixtures.

#### 5.3.4 Ops

- Repack schedules off-peak.  
- Repo move/migrate tooling.  
- Point-in-time ref restore from audit log.  
- Emergency force-push ACL break-glass.

---

## 6. Wrap-Up

### 6.1 What we designed

A **Git-class VCS**: content-addressed object DAG, transactional refs, pack negotiation for fetch/push, auth/hooks, LFS, and scale via **replicas, pack CDN, partial clone**, and eventual **cells/VFS** for monorepos.

### 6.2 Memorize tradeoffs

| Topic | Tradeoff |
|-------|----------|
| Full vs partial clone | Completeness vs time/bandwidth |
| Delta CPU vs size | Pack time vs transfer |
| Central mono vs multi-repo | Consistency vs blast/clone size |
| Strong ref consistency | Write locality vs global lag |
| GC aggressiveness | Space vs safety |
| Path ACL | Security vs push latency |

### 6.3 30-second scale narrative

Baseline: classic Git server, packs on disk.  
10×: HA + LFS + caches.  
100×: partial clone + CDN.  
1,000×: sharded CAS + monorepo virtualization.

### 6.4 Deal-breakers checklist

- Mutable “file rows” instead of content-addressed objects.  
- Non-atomic ref updates.  
- Full monorepo clone as only supported mode.  
- GC without grace/reachability.  
- Trusting client hashes without verify.  
- Single NFS box for all packs at org scale.

---

## 7. Deeper / Related Interview Questions

### 7.1 Clarifying & product

**Q1: Compatible with Git clients?**  
A: Prefer yes — smart HTTP/SSH protocol.

**Q2: Centralized or distributed?**  
A: Distributed object model; hosted central authoritative refs for teams.

**Q3: PRs in scope?**  
A: Refs + hooks enough MVP; full review product later.

### 7.2 Object model

**Q4: Why content-addressed?**  
A: Integrity, dedup, immutable caching, easy sync.

**Q5: Tree vs storing full snapshots?**  
A: Trees share unchanged subtrees across commits.

**Q6: Merge commit?**  
A: Commit with 2+ parents; tree result of merge.

**Q7: Tag vs branch?**  
A: Branch moves; annotated tag ideally immutable.

### 7.3 Sync & packs

**Q8: What is a packfile?**  
A: Compressed container of objects with optional deltas + index.

**Q9: Thin pack?**  
A: Push omits bases already on server.

**Q10: How fetch finds missing objects?**  
A: Reachability difference between want and have.

**Q11: Protocol v2 benefit?**  
A: Less chatty; server-side ref filtering.

### 7.4 Large repos

**Q12: LFS vs Git objects?**  
A: Pointer small; bytes in LFS CAS with different lifecycle.

**Q13: Partial clone?**  
A: Omit blobs (or trees); fetch on demand.

**Q14: Shallow vs partial?**  
A: Shallow limits history depth; partial limits object types/paths.

**Q15: Monorepo strategy at Google scale?**  
A: Partial/sparse + virtual FS / server-side indexing — mention Piper ideas.

### 7.5 Consistency & GC

**Q16: Concurrent branch update?**  
A: CAS; loser fetches and retries.

**Q17: When GC?**  
A: Unreachable + older than grace; not referenced by reflog/quarantine.

**Q18: Can GC break clones?**  
A: Yes if too eager — grace periods and generation bits.

### 7.6 Security

**Q19: Protected main?**  
A: Deny direct push; allow merge bot; require signed commits optional.

**Q20: Path-restricted write?**  
A: Compute changed paths from push; evaluate ACL.

**Q21: Object hash collision?**  
A: SHA-256 migration; detect; reject.

### 7.7 Estimation drills

**Q22: Why trees save space?**  
A: Unchanged directory → same tree OID reused.

**Q23: 10K clones × 50 GB?**  
A: 500 TB egress — must bundle CDN + partial.

**Q24: Hot main ref QPS?**  
A: Serialize updates per ref; reads from replica/cache.

### 7.8 Alternatives & deal-breakers

**Q25: SVN centralized model?**  
A: Weaker offline; different branching cost — know tradeoff.

**Q26: Store each revision in SQL BLOB?**  
A: Deal-breaker at monorepo scale; no DAG sharing.

**Q27: Only object storage without packs?**  
A: Too many small GETs; packs amortize.

### 7.9 Interview craft

**Q28: How to open?**  
A: Object model → refs → clone/fetch/push → auth → large repo strategy.

**Q29: What impresses L5+?**  
A: CAS+pack math, ref CAS, partial clone, GC safety, progressive CDN/cells.

**Q30: Common mistake?**  
A: Hand-waving “S3 for files” without DAG, packs, or ref transactions.

---

### Appendix A — Object header

```text
"${type} ${size}\0${content}" → hash → oid
```

### Appendix B — Ref DB schema

```text
refs(repo_id, name, oid, peeled_oid, updated_at, updater)
UNIQUE(repo_id, name)
```

### Appendix C — Push CAS

```text
BEGIN
  IF ref.oid != expected_old: ABORT non-ff or conflict
  WRITE objects from quarantine
  SET ref.oid = new
COMMIT
```

### Appendix D — Reachability

```text
def reachable(tips):
  queue = tips
  seen = {}
  while queue:
    o = pop
    if o in seen: continue
    seen.add(o)
    queue += children_referenced_by(o)
  return seen
```

### Appendix E — Filter spec

```text
blob:none
blob:limit=1m
tree:0
combine:blob:none+tree:0
```

### Appendix F — LFS pointer

```text
version https://git-lfs.github.com/spec/v1
oid sha256:...")
size 1234567
```

### Appendix G — Progressive scale table

| Scale | Objects | Fetch | Refs |
|-------|---------|-------|------|
| Baseline | Disk packs | App servers | DB |
| 10× | Multi-AZ CAS | Replicas | HA DB |
| 100× | Sharded packs | CDN bundles | Reftable |
| 1,000× | Global cells | Edge + VFS | Regional |

### Appendix H — Hook points

```text
pre-receive: authz, size, secret scan, FF policy
update: per-ref
post-receive: CI, webhooks
```

### Appendix I — Bundle bit

```text
git bundle create main.bundle main
Immutable; CDN; bootstrap clones then fetch delta
```

### Appendix J — NFR card

```text
CAS verify on push
Ref CAS transactions
Quarantine + hooks
Partial clone for mono
Pack CDN
GC grace
```

### Appendix K — Reftable notes

- Efficient ref storage/log for huge ref counts  
- Transactional updates  

### Appendix L — Secondary indexes (Phase 1.5)

```text
commit-graph file for fast traversal
bitmap indexes for reachability in pack
blame/cache server-side
```

### Appendix M — Common pushbacks

| Pushback | Answer |
|----------|--------|
| “Just use GitHub” | Interview wants internals |
| “Object store = enough” | Need refs, packs, negotiate |
| “Monorepo impossible” | Partial + sparse + VFS patterns |

### Appendix N — Related systems (conceptual)

- Git / GitHub / GitLab  
- Google Piper / CitC concepts  
- Mercurial evolve / Facebook Sapling (discuss tradeoffs) |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| OID | Object ID (hash) |
| Pack | Compressed object container |
| Thin pack | Missing bases assumed present |
| Promisor | Remote that may supply missing objects |
| FF | Fast-forward ref update |

### Appendix P — Worked example

```text
Repo tip C10; client at C7
reachable(C10)-reachable(C7) = 3 commits + few trees/blobs
Pack 2 MB vs full clone 1 GB
```

### Appendix Q — Consistency cheatsheet

| Data | Model |
|------|-------|
| Objects | Immutable, eventual replica |
| Refs primary | Strong CAS |
| Refs replica | Lag OK for fetch if advertised carefully |
| LFS | Durable before pointer push ideally |

### Appendix R — 30m interview checklist

1. Object DAG.  
2. Refs CAS.  
3. Fetch/push packs.  
4. Auth/hooks.  
5. Large repo: LFS + partial.  
6. Scale CDN/replicas.  
7. Deal-breakers.  

### Appendix S — GC pseudocode

```text
reachable = union(reachable(all refs), recent_pushes_grace)
delete packs/objects not in reachable and older than grace
repack survivors
```

### Appendix T — What changes at each scale

| Scale | Key change |
|-------|------------|
| 10× | HA + LFS + cache |
| 100× | Partial + CDN |
| 1,000× | Cells + VFS |

### Appendix U — SSH vs HTTP

```text
SSH: key auth, long sessions
HTTP: tokens, CDN-friendly GETs for packs/bundles
Offer both
```

### Appendix V — Disaster recovery

- Object store cross-region async  
- Ref DB PITR  
- Rebuild midx/commit-graph from packs  

---

*End of git-like source-control system design.*
