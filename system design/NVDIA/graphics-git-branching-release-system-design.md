# System Design: Graphics Git Branching & Release Engineering

> **Focus areas:** Branch topology · Release trains · Cherry-picks / backports · LTS & hotfix · CI gates · Binary artifacts · Driver versioning · Code freeze · Monorepo vs multi-repo  
> **Style:** End-to-end **process / ops system design** (release engineering as a product) with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit branch invariants, ownership of merges, honest MVP vs mega-monorepo paths, deal-breakers called out  
> **Interview theme:** NVIDIA graphics / driver / GPU software — treat branching & release as a **control plane for change**, not “just Git commands”

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

Goal: **bound the release system**—what “shipping a graphics/driver change” means, which consumers (OEM, ISV, cloud, internal), and at which engineer/repo scale the process still holds.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What is in the repo(s)? | Kernel module, user-mode driver, OpenGL/Vulkan/D3D stacks, firmware blobs refs, tools, tests | Treat as **GPU software product line**, not a single app |
| F2 | Mono or multi-repo? | Often **monorepo-ish** for driver stacks + satellite repos for firmware/docs; or multi-repo with version locks | Need a **release manifest** either way |
| F3 | Who consumes builds? | Internal QA, OEMs, game ISVs, cloud GPU fleets, LTS enterprise | Multiple **release channels** with different freeze windows |
| F4 | Branch model? | Mainline + release branches + LTS + hotfix | Explicit topology + promotion rules |
| F5 | How do fixes land on old releases? | Cherry-pick / backport with approval | Backport queue + conflict policy |
| F6 | Versioning? | Driver version scheme (e.g. `AAA.BB.CC` / branch + build) | Immutable version ↔ commit ↔ artifact tuple |
| F7 | Code freeze? | Soft freeze → hard freeze before GA | Calendar + exception process |
| F8 | CI gates? | Compile matrix, unit, graphics conformance, stress, signed package | Progressive gates; not all on every PR |
| F9 | Binary artifacts? | Signed drivers, packages per OS/GPU SKU, debug symbols | Artifact store + SBOM + provenance |
| F10 | Hotfix SLA? | Critical security/stability in days | Hotfix branch from release tip; minimal diff |
| F11 | LTS? | Enterprise N-year support | Long-lived release branches; sparse merges |
| F12 | Release train cadence? | Monthly / quarterly GA + continuous mainline | Train schedule as first-class object |

**MVP functional scope (lock with interviewer):**

1. **Mainline** (`main` / `master`) always integrable; feature work lands via PR.  
2. **Release branches** cut from mainline at train freeze; only approved cherry-picks after cut.  
3. **Hotfix** from release tip for Sev-1; merge-back policy to mainline.  
4. **LTS** branch(es) with longer support and stricter backport criteria.  
5. **CI gates**: required checks on PR; heavier matrix on merge / nightly / release candidate.  
6. **Version + artifact** binding: every public build has immutable git SHA + version + signed package set.  
7. **Release manifest** listing component SHAs (if multi-repo) or path versions (if monorepo).  
8. Ops: code freeze, exception approval, backport queue, release notes automation.

**Out of MVP (explicitly defer):**

- Fully automated cherry-pick conflict resolution without human review  
- Perfect bisectability across closed-source firmware blobs (document boundaries)  
- World-wide simultaneous OEM certification in one train (stagger)  
- Replacing Git with a custom VCS  
- Exact “zero regression forever” on every cherry-pick (impossible—risk triage instead)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | PR merge latency (CI green)? | Developers unblocked | p50 < 30–60 min for default PR set; heavy matrix async |
| N2 | Mainline health? | Always green enough to cut a branch | “Broken main” < few hours; revert culture |
| N3 | Release reproducibility? | Same SHA → same bits (modulo signed timestamps) | Hermetic builds + pinned toolchains |
| N4 | Auditability? | Who approved freeze exception / backport | Immutable audit log |
| N5 | Security? | Signed artifacts; controlled signing keys | HSM / signed CI identity |
| N6 | Scale of engineers? | See progressive table | Branch policy must not require heroic heroes |
| N7 | Multi-platform? | Windows / Linux / etc. | Matrix as cost center—gate wisely |
| N8 | Rollback? | Bad driver → prior version | Versioned artifacts retained; kill-switch channel notes |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Feature lands on `main` via PR → green CI → merge.  
2. Release train: freeze → cut `release/AAA.BB` from green main → RC builds → GA tag → publish artifacts.  
3. Post-cut bugfix on main → cherry-pick to release → CI on release → new RC.  
4. Sev-1 on GA → hotfix branch → patch → ship `.CC+1` → merge-back to main + open release.  
5. LTS: quarterly maintenance drop via curated backport batch.  
6. OEM needs special build: branch or label from known SHA; never from dirty WIP.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Cherry-pick conflict | Human resolve on release branch; no silent skip; track in backport ticket |
| Fix on release but not main | **Merge-back required** or explicit “release-only” waiver with expiry |
| Broken main at cut time | Delay cut; do not cut from red tip without waiver |
| Dual cherry-pick (same fix twice) | Idempotent change-id / `Fixes:` / git notes; detect duplicate |
| Feature accidentally on release branch | Reject; revert; features only via main → forward-port policy |
| Firmware blob mismatch | Manifest pins blob digest; CI fails if driver expects other digest |
| Signing key compromise | Revoke, re-sign policy, halt publish pipeline |
| Long-lived feature branch (months) | Rebase/merge tax; prefer trunk-based + flags |
| Hotfix regresses LTS | Separate LTS cherry-pick decision; not automatic |
| Version collision | Central version allocator; never hand-edit production version twice |
| CI flake blocks train | Quarantine flake; don’t weaken gate permanently |
| Monorepo partial checkout pain | Sparse checkout / virtual monorepo tooling at 100× |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active engineers on stack | 50 | 500 | 5K | 50K (org-wide multi-product) |
| PRs / day | 20 | 200 | 2K | 20K |
| Active release branches | 3–5 | 8–12 | 20–40 | 100+ (many LTS/OEM) |
| OS × GPU SKU CI cells | 50 | 500 | 5K | 50K (sampled) |
| Artifacts / release | 20 packages | 200 | 2K | 20K |
| Cherry-picks / release train | 30 | 300 | 3K | 30K |
| LTS lines supported | 1–2 | 3–4 | 6–8 | 10+ |
| Concurrent trains | 1 | 2 | 3–4 | Many product lines |
| Binary artifact store size | 5 TB | 50 TB | 500 TB | Multi-PB |
| Time to cut release branch | hours | hours | automated minutes | fleet of cutters + health gates |

**What each jump forces:**

- **10×:** Formal release manager role; backport bot; flake quarantine; artifact retention policy.  
- **100×:** Monorepo tooling or strict multi-repo manifests; merge queues; CI sampling + required cores; signed provenance at scale.  
- **1,000×:** Product-line cells (graphics vs compute vs DPU) with shared policy engine; hierarchical release trains; AI-assisted conflict triage still human-gated for driver-critical paths.

### 1.5 Etc. (Constraints & Assumptions)

- We design the **release engineering system** (branch policy, CI orchestration, artifacts, versioning)—not every driver’s runtime behavior.  
- Source of truth for code is **Git**; source of truth for “what shipped” is **version ↔ SHA ↔ artifact digest**.  
- Some blobs are closed / partner-supplied → pin by digest in manifest.  
- Legal / export / OEM NDA builds may need **isolated channels**.  
- “Graphics repository” may span user-mode + KMD; treat as one **product train** even if multi-repo.

**Scope statement:**

> Design a release-engineering control plane for NVIDIA-class GPU/graphics software: trunk-based mainline, release/LTS/hotfix branches, cherry-pick backports, CI gates, driver versioning, signed binary artifacts, and code-freeze operations—scaling from dozens of engineers to organization-wide multi-train fleets.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Engineer & change volume

```text
Baseline: 50 engineers × ~0.4 PR/engineer/day ≈ 20 PRs/day
Avg PR: 3 commits, ~400 LOC touched (highly skewed)
CI default PR: 15 minutes machine-time × 4 shards ≈ 1 hour wall if parallel

10×: 200 PRs/day → need merge queue + auto-rebase; without it, main thrashes
100×: 2K PRs/day → path-based OWNERS, merge trains, speculative CI
```

### 2.2 CI cost (the real tax)

```text
Full matrix cells = OS × arch × GPU family × config (debug/release) × API (GL/VK/…)
Baseline “full” = 50 cells × 2h ≈ 100 machine-hours / full run
If every PR ran full matrix: 20 × 100 = 2,000 machine-hours/day → unsustainable

Rule: PR = smoke + affected paths; nightly = wider; RC = certification matrix
Sampling at 100×: risk-based cell selection + historical flake/failure heatmaps
```

**Critical insight:** Release engineering is often **CI economics + risk triage**, not Git topology trivia.

### 2.3 Artifact storage

```text
Driver package avg 1–3 GB compressed per OS SKU bundle (order-of; varies wildly)
Baseline release: 20 bundles × 2 GB ≈ 40 GB + symbols 2–5×
Retain: all GA forever; RCs 90 days; daily main 14–30 days

100× trains / SKUs: hundreds of TB → lifecycle policies mandatory
1,000×: multi-PB; cold tier + content-addressed dedupe by blob digest
```

### 2.4 Cherry-pick / backport load

```text
Post-cut window 4 weeks; ~30 cherry-picks baseline
Conflict rate ~10–20% → 3–6 human resolutions / train
100×: 3K cherry-picks → need bots, change-id tracking, batch backport reviews
```

### 2.5 Version allocation

```text
Driver versions are scarce public identifiers—central allocator
Train AAA.BB.*; hotfix increments build/revision
Never two GA versions for divergent SHAs
```

### 2.6 Critical bottlenecks (rank ordered)

1. **CI matrix explosion** vs engineer velocity  
2. **Cherry-pick conflict storms** after large mainline refactors  
3. **Broken main** blocking release cut  
4. **Signing / publish** as single chokepoint  
5. **LTS drift** (security fixes lag)  
6. **Manifest skew** in multi-repo (component A new, B old)  
7. **Human release manager bus factor** without automation  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
ProductLine     → e.g. GameReady / Studio / Enterprise / CloudDriver
Train           → calendar + version series (AAA.BB)
Branch          → main | release/* | lts/* | hotfix/*
Change          → PR / commit with change-id
Promotion       → main → RC → GA (state machine on Release)
ArtifactSet     → signed packages + SBOM + symbols for a Version
Manifest        → pins of all components (mono path versions or multi SHAs)
BackportRequest → change-id + target branches + risk class
FreezeWindow    → soft/hard freeze + exception tickets
```

**Release state machine:**

```text
OPEN_FOR_FEATURES → SOFT_FREEZE → HARD_FREEZE → RC → GA → MAINTENANCE → EOL
                         ↓              ↓
                    exceptions      cherry-picks only
HOTFIX: GA → HOTFIX_RC → HOTFIX_GA → (merge-back) → MAINTENANCE
```

### 3.2 Options: monorepo vs multi-repo

| Option | Pros | Cons | Deal-breaker when |
|--------|------|------|-------------------|
| A. True monorepo | Atomic cross-component change; one SHA truth | Tooling/CI scale; checkout size | No sparse/virtual monorepo investment at 100× |
| B. Multi-repo + manifest | Clear ownership boundaries | Skew; “works on my machine” combo | Shipping without locked manifest |
| C. Hybrid (core mono + satellites) | Pragmatic for firmware/partner | Two release rhythms | Forgetting to pin satellites |

**Chosen path:**

- **MVP:** Hybrid — core driver/graphics in one (or few) Git repos; firmware/partner as **digest-pinned** artifacts in manifest.  
- **100×+:** Invest in monorepo *or* automated manifest integration CI that tests the **exact** combo that will ship.

### 3.3 Branch topology (chosen)

```text
main ────────────────────────────────────────────►
   \                \                \
    release/580.xx   release/590.xx   lts/550.xx ──► (long)
         \                \
          hotfix/580.xx.y  cherry-picks only

Policy:
- Features → main only (feature flags if needed)
- Release branch: bugfix cherry-picks + version bumps + release notes
- Hotfix: from release tip; minimal diff; merge-back to main mandatory (or waiver)
- LTS: security/critical only; batched; higher bar
```

**Invariant R1:** No feature development directly on `release/*` without Release Manager + Architect exception.

**Invariant R2:** Every commit on `release/*` either (a) came from main via cherry-pick with change-id, or (b) is release metadata (version, notes) explicitly labeled.

**Deal-breaker:** Divergent fix on release with no merge-back—creates permanent fork of truth.

### 3.4 Trunk-based vs long-lived feature branches

| Approach | Use when |
|----------|----------|
| Trunk-based + flags | Default for graphics stacks that must integrate often |
| Short-lived feature branches (< few days) | Large risky work with merge queue |
| Long-lived fork | Almost never—integration debt kills release trains |

**Deal-breaker at 10×+:** Month-long private branches merging “on freeze day.”

### 3.5 Cherry-pick & backport system

```text
1. Fix merges to main with Change-Id / Fixes: BUG-123
2. BackportRequest created (auto from bug severity or manual)
3. Bot attempts cherry-pick to target release/LTS branches
4. On success: PR to release with CI; on conflict: assign owner
5. Tracker updates: which trains contain the fix
6. Release notes generator pulls public-facing items
```

**Conflict policy:** never drop silently; never “approximate” a fix on release without review—driver correctness > velocity.

**Duplicate detection:** same Change-Id already on branch → no-op.

### 3.6 Versioning (driver versions)

Public driver versions are a **product API**. Design:

```text
AAA.BB.CC[.DD]
  AAA  — major train / feature generation (marketing + compatibility story)
  BB   — branch / minor train
  CC   — build / hotfix increment within train
  DD   — optional OEM/special

Binding:
  version V ↔ git_sha S ↔ manifest M ↔ artifact_digests D[]
```

**Allocator service (or locked release DB):**

- Reserves next `CC` atomically for a train.  
- GA publish requires signature + completed checklist.  
- Internal CI builds use `V-dev+sha` or distinct channel—never collide with GA.

**Deal-breaker:** Hand-edited version files racing across two release managers.

### 3.7 Code freeze

| Phase | Allowed | Gate |
|-------|---------|------|
| Soft freeze | Bug fixes + low-risk; features need exception | Extra reviewers |
| Hard freeze | Cherry-picks for approved bugs only | Release board |
| RC | Certification fixes | Escalation only |
| GA cut | Metadata / signing | Automated checklist |

Exceptions: ticket with risk, test plan, rollback plan, approvers (eng + QA + RM).

### 3.8 CI gates (progressive)

```text
PR gate (required):
  - lint / format
  - unit + component tests for touched paths
  - build affected targets
  - smoke GPU tests (small device pool)

Merge / post-merge:
  - wider functional
  - concurrency / leak smoke

Nightly:
  - expanded SKU matrix (sampled)
  - conformance subsets
  - performance regression budgets

RC / release:
  - certification matrix
  - long soak / stress
  - package install tests on golden images
  - SBOM + license + CVE scan on artifacts
```

**Flake policy:** quarantine with owner SLA; quarantined tests cannot be the only gate for a critical path forever.

### 3.9 Binary artifacts & provenance

```text
Build system → content-addressed object store
  inputs: source SHA, toolchain pin, manifest, build flags
  outputs: packages, symbols, SBOM, provenance attestation (SLSA-like)

Publish pipeline:
  candidate → sign (HSM) → channel promote (beta/GA) → CDN / partner drop
```

**Retention:** GA forever; symbols long; intermediate prune.

### 3.10 Hotfix path (fast lane)

```text
Sev-1 identified → RM opens hotfix/release-AAA.BB.CC+1 from GA tag
Minimal patch (prefer already-on-main fix cherry-pick)
Accelerated CI (still must include security-relevant + install smoke)
Sign + publish
Merge-back to main and to any still-open younger release if applicable
Postmortem + automated regression test added
```

**Deal-breaker:** Hotfix from an engineer’s laptop unsigned build.

### 3.11 LTS

LTS is **policy + staffing**, not only a branch:

- Explicit supported window (e.g. N years).  
- Backport criteria: security, data corruption, wide OEM blocker.  
- Periodic maintenance trains (batched) vs drip cherry-picks.  
- CI: smaller matrix but **must stay green**—rotting LTS is a liability.

### 3.12 Multi-region / multi-site engineering

| Plane | Mode |
|-------|------|
| Git primary | Single primary (or Gitaly/geo with clear primary writes) |
| CI farms | Regional GPU farms; cache build objects globally |
| Artifact publish | Multi-CDN; signing centralized |
| Freeze decisions | Follow-the-sun RM rotation with shared calendar |

**Deal-breaker:** Two sites cutting different GA versions for the same train without a global allocator.

---

## 4. Architecture Diagram

```text
                    ┌─────────────────────────────────────────┐
                    │         Release Control Plane            │
                    │  trains · freezes · versions · backports │
                    └───────────────┬─────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          v                         v                         v
   ┌─────────────┐          ┌─────────────┐          ┌─────────────────┐
   │ Git (main,  │          │ CI / CD     │          │ Artifact Store  │
   │ release,    │◄────────►│ merge queue │─────────►│ packages+SBOM   │
   │ lts,hotfix) │  webhooks│ GPU farms   │  publish │ signatures      │
   └─────────────┘          └─────────────┘          └────────┬────────┘
          │                         │                         │
          │ change-id               │ results                 │ promote
          v                         v                         v
   ┌─────────────┐          ┌─────────────┐          ┌─────────────────┐
   │ Backport    │          │ Test / flake│          │ Channels        │
   │ Bot+Queue   │          │ Quarantine  │          │ beta / GA / LTS │
   └─────────────┘          └─────────────┘          └─────────────────┘
          │
          v
   ┌──────────────────────────────────────────────────────────┐
   │ Bug tracker ↔ release notes ↔ OEM/partner portals        │
   └──────────────────────────────────────────────────────────┘

Branch flow (time →):

main:    ●──●──●──●──●──●──●──●──●──●──●──●──►
              \           \ 
               r/580 ●─●─●─●─GA──●hotfix►
                    cherry      │
                     picks      └──► merge-back to main
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**What “reliability” means here:** mainline rarely broken; every GA is rebuildable; hotfixes don’t orphan main; LTS receives critical fixes.

#### 5.1.1 Mainline health

| Practice | Why |
|----------|-----|
| Merge queue / speculative merge | Prevent “green individually, red together” |
| Revert-first culture | Restore green in minutes; fix forward after |
| Mandatory smoke on merge | Cheap catch of integrate breaks |
| Forbidden force-push on main/release | History is audit trail |

**Deal-breaker:** Force-push rewriting GA tags.

#### 5.1.2 Reproducible builds

Pin:

- Compiler / SDK / CUDA toolkit / Windows WDK (as applicable)  
- Containerized or hermetic build images  
- Manifest digests for blobs  

Record **build-info.json** next to artifacts: SHA, tool versions, timestamp, actor.

#### 5.1.3 Merge-back invariant

```text
ON hotfix_shipped(V):
  assert exists commit on main with same Change-Id
    OR waiver ticket with expiry + owner
  else block next freeze for that product line
```

Automate nagging; make waiver visible on release dashboard.

#### 5.1.4 Signing & publish reliability

- Signing service HA but **key material** in HSM.  
- Publish is transactional per version: all-or-nothing channel pointer update.  
- Canary channel before world-wide GA when product allows.

#### 5.1.5 Failure modes & drills

| Failure | Drill |
|---------|-------|
| Broken main at freeze | Delay cut; communicate; no silent cut from red |
| Bad GA | Pull channel pointer to previous GA; publish advisory |
| Compromised CI runner | Invalidate in-flight artifacts; rotate identity |
| Artifact store outage | Multi-region replica; freeze publishes, not development |
| Backport bot wrong conflict resolution | Bot never auto-commits conflict markers; human-only |

### 5.2 Scalability

#### 5.2.1 Scale the Git topology, not just hardware

At 100× engineers, the bottleneck is **coordination**:

- OWNERS / CODEOWNERS path rules  
- Merge queue shards by directory  
- Release trains per product line with shared policy engine  

#### 5.2.2 CI sampling strategy

```text
always: critical path tests for touched components
probabilistic: cells weighted by historical failure × SKU revenue/risk
mandatory RC: certification set frozen per train
```

Document residual risk; sampling without metrics is roulette.

#### 5.2.3 Monorepo scaling toolkit

| Tooling | Role |
|---------|------|
| Sparse checkout / virtual FS | Developer sync time |
| Remote build cache | CI minutes |
| Target graph analysis | Build only affected |
| Large file system (Git LFS or CAS) | Blobs out of Git history when possible |

#### 5.2.4 Progressive scale jump cards

**10×:** “Add merge queue, backport bot, flake quarantine, central version allocator.”  
**100×:** “Path-based CI + manifest integration jobs; multiple trains; artifact lifecycle; RM rotations.”  
**1,000×:** “Policy-as-code across product cells; hierarchical trains; sampled world matrix; dedicated release SRE.”  

#### 5.2.5 What does *not* scale

- One global “release.txt” edited by hand  
- Full matrix on every PR  
- Unlimited LTS lines without staffing model  
- Chat-ops-only freeze decisions with no audit trail  
- Cherry-picking refactors that don’t apply cleanly across 10 branches without redesigning the fix on main  

### 5.3 Maintainability

#### 5.3.1 Policy as code

Encode branch protection, required checks, freeze calendars, backport eligibility in versioned config:

```yaml
# release-policy.yaml (illustrative)
product: GameReady
trains:
  - name: "590"
    cut_from: main
    version_prefix: "590.44"
    freeze:
      soft: "2026-09-01"
      hard: "2026-09-10"
    backport_classes: [security, stability, oem_blocker]
ci:
  pr: [unit, build_affected, smoke_gpu]
  rc: [cert_matrix_590]
```

Review policy PRs like code.

#### 5.3.2 Change-Id discipline

Every fix carries stable **Change-Id** (Gerrit-style) or equivalent so tooling can answer: “Is BUG-123 in 550 LTS?”

#### 5.3.3 Release notes & bug tracking integration

Automate from labeled commits; human edits only public wording. Avoid two sources of truth (spreadsheet + Git).

#### 5.3.4 Developer experience

| Pain | Mitigation |
|------|------------|
| Slow CI | Remote cache + affected targets |
| Confusing branches | One-pager topology + `git nvidia-release` helper |
| Fear of freeze | Clear exception path |
| Hotfix heroics | Templates + checklist automation |

#### 5.3.5 Observability for release engineering

Dashboards:

- Mainline red duration  
- PR time-to-merge  
- Cherry-pick success / conflict rates  
- CI flake rate by suite  
- Train burn-down (open blockers)  
- Artifact publish success  
- LTS CVE aging  

**SLO examples:** main broken < 2h/week; freeze exception SLA < 4 business hours; Sev-1 hotfix candidate build < 24h after fix merge.

### 5.4 Security & compliance (release-specific)

- Signed commits optional; **signed artifacts** mandatory for GA.  
- Least privilege on publish credentials.  
- SBOM + vulnerability scan gate on RC.  
- Partner drops via authenticated portals; audit who downloaded what.  
- Embargoed security fixes: private fork / delayed public branch strategy agreed with PSIRT.

### 5.5 Multi-repo manifest deep dive

```text
manifest.xml / lockfile:
  kmd:     repo@sha
  umd:     repo@sha
  vulkan:  repo@sha
  fw:      cas@digest
  tests:   repo@sha

Integration CI checks out all pins → builds → smokes
Release cut tags the manifest, not only one repo
```

**Skew bug:** UMD expects KMD ioctl N+1 but manifest pins KMD N → catch in integration CI, not at OEM.

### 5.6 OEM / special builds

| Pattern | When |
|---------|------|
| Same GA + config flags | Preferred |
| Branch from GA tag | Rare OEM divergence |
| Separate package branding | Same bits, different wrapper |

Track OEM deltas; plan to die or merge back—permanent forks multiply LTS cost.

### 5.7 Interaction with game/ISV certification

Release trains often align with major game launches / API conformance:

- Soft-freeze earlier for “cert builds.”  
- Keep a **cert pin** SHA even if train continues.  
- Don’t silently replace bits under a cert ID.

---

## 6. Wrap-Up

### 6.1 Summary

| Piece | Choice |
|-------|--------|
| Topology | Trunk `main` + `release/*` + `hotfix/*` + `lts/*` |
| Features | Land on main; flags if needed |
| Fixes to trains | Cherry-pick with Change-Id; conflict → human |
| Versioning | Central allocator; version ↔ SHA ↔ artifacts |
| CI | Progressive gates; full matrix on RC not every PR |
| Artifacts | Signed, provenanced, lifecycle-managed |
| Freeze | Soft → hard → RC → GA with audited exceptions |
| Scale | Merge queues, policy-as-code, product-line cells |

### 6.2 30-second pitch

> Treat GPU/graphics release engineering as a control plane: keep mainline shippable, cut release branches for trains, move fixes by tracked cherry-picks, bind every driver version to a SHA and signed artifacts, and scale by progressive CI plus policy-as-code—not by heroic freezes.

### 6.3 Trade-offs

1. Monorepo atomicity vs tooling cost.  
2. Full CI certainty vs engineer velocity.  
3. Many LTS lines vs security staffing.  
4. Fast hotfix vs merge-back discipline.  
5. OEM forks vs long-term maintainability.

### 6.4 Deal-breakers (memorize)

1. Shipping without immutable version↔SHA↔digest binding.  
2. Release-only fixes that never return to main.  
3. Force-push / rewrite of GA history.  
4. Unsigned “emergency” public drivers.  
5. Full matrix on every PR *or* no matrix on RC.  
6. Multi-repo ship without integration manifest CI.

---

## 7. Deeper / Related Interview Questions

### 7.1 Branching strategy

**Q: Why not Gitflow with `develop` + `main`?**  
A: Extra long-lived branch usually adds lag. Trunk-based + release branches matches driver trains better. Gitflow’s `develop` often becomes a second main with worse discipline.

**Q: Why not only tags on main (no release branch)?**  
A: Post-GA hotfixes need a stable line while main moves fast; tags alone don’t give a maintenance branch.

**Q: When is a release branch cut?**  
A: At soft/hard freeze from a **green** main SHA chosen by RM + CI health dashboard—not from “whoever pushed last.”

**Q: Feature flags in drivers?**  
A: Yes for risky paths; some HW/firmware couplings can’t flag easily—those need branch isolation or later trains.

### 7.2 Cherry-picks & backports

**Q: Cherry-pick vs merge release←main?**  
A: Merging main into release pulls unfinished features. Cherry-pick curated fixes. Occasional merge only with extreme care / topic branches.

**Q: Patch doesn’t apply—rewrite on release?**  
A: Prefer re-implement with same Change-Id and tests; avoid “similar but different” silent behavior drift.

**Q: How to track “fix present in which drivers”?**  
A: Change-Id index + release notes DB; query by bug id.

**Q: Automated conflict resolution with LLMs?**  
A: Assist only; driver correctness requires human + CI; never auto-merge conflicted cherry-picks.

### 7.3 Versioning & artifacts

**Q: Semver vs driver AAA.BB.CC?**  
A: Follow product convention; the invariant is uniqueness + monotonicity within train + immutable binding to bits.

**Q: Can two packages share a version?**  
A: No for GA. Internal rebuilds need distinct identifiers.

**Q: Debug vs retail bits?**  
A: Separate package IDs / channels; never overwrite retail with debug under same version.

**Q: Symbol servers?**  
A: Publish sanitized symbols with retention; tie to version; access control for proprietary stacks.

### 7.4 CI & freeze

**Q: PR red from unrelated flake—what do you do?**  
A: Quarantine flake with owner; rerun; don’t disable suite globally.

**Q: Who can break freeze?**  
A: Named approvers; ticketed exception; auto-expire.

**Q: How do you keep RC matrix finite?**  
A: Risk-tier SKUs; OEM-priority devices; rotate coverage across trains; track escaped defects to retune.

### 7.5 Hotfix & LTS

**Q: Hotfix for one OEM only?**  
A: Prefer config/package branding; if code fork, schedule kill-date and document support cost.

**Q: Security embargo workflow?**  
A: Private fix → coordinated release → multi-branch backport storm under PSIRT calendar.

**Q: LTS missing a fix that main has?**  
A: Explicit risk acceptance or schedule maintenance drop; dashboard CVE age.

### 7.6 Monorepo / multi-repo

**Q: Atomic cross-repo feature?**  
A: Manifest PR that updates multiple pins in one integration test job; or true monorepo.

**Q: Huge binary in Git?**  
A: Don’t; CAS/LFS/artifact pin by digest.

**Q: How does this differ from web microservices repos?**  
A: Driver consumers need coherent **versioned bundles**; microservices often deploy independently—graphics trains are tighter coupled.

### 7.7 Operations & org

**Q: Bus factor on Release Manager?**  
A: Policy-as-code, checklists, on-call RM rotation, automated cutters.

**Q: Metrics that show process health?**  
A: Time-to-merge, main red minutes, conflict rate, escaped defects per GA, hotfix frequency, LTS lag.

**Q: How to migrate from chaotic branching?**  
A: Pick one train as pilot; enforce merge-back; introduce Change-Id; turn on merge queue; don’t big-bang all LTS at once.

### 7.8 NVIDIA-flavored scenarios

**Q: Game launch blocker found 48h before GA?**  
A: Severity triage → hotfix lane or slip GA; never untested mega-merge; communicate channel strategy to partners.

**Q: Cloud provider needs custom kernel skew?**  
A: Manifest pin + cloud channel; certify that combo; don’t pretend desktop GA equals cloud bits.

**Q: Vulkan new version mid-train?**  
A: Usually next train; exception only with conformance plan and flag/guard rails.

### 7.9 Reliability drills

**Q: Publish pipeline pushed wrong channel pointer?**  
A: Immediate rollback pointer; verify CDN purge; audit how approval was bypassed; add two-person rule if missing.

**Q: Tag moved after GA?**  
A: Tags immutable; if mistake, new version—never move.

### 7.10 Comparison questions

**Q: vs Linux stable cherry-pick process?**  
A: Similar spirit (mainline first, stable backports); add driver versioning, signed packages, OEM channels, GPU CI farms.

**Q: vs mobile app store release trains?**  
A: Similar freeze/RC; GPU drivers add HW matrix + kernel coupling + long LTS.

**Q: vs container image tags only?**  
A: Insufficient—need branch maintenance + backport semantics for source, not only image mutability discipline.

### 7.11 Interview traps

**Q: “We’ll just rebase release onto main weekly.”**  
A: Pulls unfinished work; breaks cert pins; creates monster conflicts—use cherry-picks.

**Q: “CI green means ship.”**  
A: Necessary not sufficient—cert matrix, soak, signed artifacts, release notes, partner comms.

**Q: Units:** 200 PRs/day × 2h CI serial ≠ “400 hours” wall-clock if parallelized—say **capacity planning in machine-hours** and **queue wait** separately.

---

## 8. Appendices

### 8.1 Branch protection checklist

```text
main:
  - require PR + N reviewers + CODEOWNERS
  - require CI smoke
  - no force-push; no delete
release/*:
  - RM team approve
  - cherry-pick label required (except version bumps)
  - RC CI for package-affecting changes
tags:
  - signed; immutable
```

### 8.2 Release cut runbook (condensed)

```text
1. Check main green dashboard (soak N hours)
2. Soft freeze announce
3. Cut release/AAA.BB from chosen SHA
4. Allocate version range in version service
5. Build RC0; publish to beta channel
6. Enter hard freeze; backport queue only
7. RC1..RCn until exit criteria
8. GA sign-off checklist
9. Sign + publish GA; immutable tag
10. Open maintenance mode; start next train planning
```

### 8.3 Hotfix checklist

```text
[ ] Bug severity Sev-1/Sev-2 approved
[ ] Fix on main (or waiver)
[ ] Minimal diff review
[ ] Accelerated CI set green
[ ] Version allocated
[ ] Signed artifacts
[ ] Channel publish + notes
[ ] Merge-back verified
[ ] Regression test filed
```

### 8.4 Manifest schema (illustrative)

```json
{
  "product": "GameReady",
  "version": "590.44.01",
  "git": { "repo": "graphics-driver", "sha": "abc123…" },
  "components": {
    "firmware_blob": "sha256:…",
    "vulkan_layer": { "repo": "vk", "sha": "def456…" }
  },
  "build": { "toolchain": "ndk-2026.08", "image": "buildenv@sha256:…" },
  "artifacts": [ { "name": "Windows-x64.exe", "digest": "sha256:…" } ]
}
```

### 8.5 Backport ticket fields

```text
change_id, bug_id, risk_class, source_sha, target_branches[],
state: NEW|PICKED|CONFLICT|MERGED|DROPPED,
conflict_owner, waiver_reason
```

### 8.6 CI gate matrix (example)

| Gate | PR | Nightly | RC |
|------|----|---------|-----|
| Unit | ✓ | ✓ | ✓ |
| Affected build | ✓ | ✓ | ✓ |
| Smoke GPU | ✓ | ✓ | ✓ |
| Conformance subset | sample | ✓ | ✓ |
| Full cert SKUs | | sample | ✓ |
| Soak 24h | | | ✓ |
| SBOM/CVE | | ✓ | ✓ |
| Sign verify | | | ✓ |

### 8.7 Freeze calendar example

```text
T-21d: train branch intent announced
T-14d: soft freeze
T-7d:  hard freeze / RC0
T-2d:  final RC
T-0:   GA
T+14d: first maintenance window preference
```

### 8.8 Roles & RACI (MVP)

| Activity | Eng | QA | RM | Security |
|----------|-----|----|----|----------|
| Merge to main | A/R | C | I | I |
| Approve freeze exception | C | C | A | C |
| Cherry-pick to release | R | C | A | I |
| GA sign-off | C | A/R | A | C |
| Hotfix publish | R | C | A | A (if sec) |

### 8.9 Artifact lifecycle

```text
dev/daily → retain 14–30d
RC        → retain 90d
GA        → retain indefinitely (or legal min)
symbols   → align with support window
yanked    → retain but channel demoted + advisory
```

### 8.10 Sample developer commands (helpers)

```bash
# illustrative wrappers—not a real NVIDIA CLI
nvidia-release status
nvidia-release backport BUG-123 --to release/590.44,lts/550.54
nvidia-release freeze-status 590.44
nvidia-release which-version --change-id I1234abcd
```

### 8.11 Anti-patterns

1. “Private topic branch becomes the release.”  
2. Different fixes for same bug on each LTS with no shared test.  
3. Manual version bump races.  
4. Turning off failing tests to ship.  
5. Storing passwords in CI logs for signing.  
6. Untagged GA (“we know which commit”).  

### 8.12 Progressive scale capacity sheet

```text
Baseline RM: 1 part-time
10×: 1 full-time RM + oncall
100×: RM team + release SRE + backport sheriffs
1,000×: per-product-line RM + central policy/platform team
```

### 8.13 Merge-back tracker query

```sql
-- illustrative
SELECT hotfix_id, version, change_id
FROM hotfixes h
WHERE NOT EXISTS (
  SELECT 1 FROM main_commits m WHERE m.change_id = h.change_id
)
AND h.waiver_id IS NULL;
```

### 8.14 Communication templates

- Soft freeze announce (what allowed / exception link)  
- GA blog / release notes  
- Hotfix advisory  
- Train slip announce with new dates  

### 8.15 Interview board order

1. Clarify consumers & trains  
2. Draw branch topology + invariants  
3. Version↔artifact binding  
4. Cherry-pick workflow  
5. CI progressive gates  
6. Freeze / hotfix / LTS  
7. Scale 10×/100×/1000×  
8. Deal-breakers  

### 8.16 Glossary

| Term | Meaning |
|------|---------|
| Train | Timed release series |
| RC | Release candidate build |
| Change-Id | Stable id across cherry-picks |
| Manifest | Pinned component set |
| Channel | beta/GA/LTS distribution pointer |
| Merge-back | Hotfix returning to main |

### 8.17 Related NVIDIA prep prompts

- Jenkins GPU test matrix  
- Dockerized GPU-test platform  
- Shader compilation pipeline LLD  
- Redesign an existing NVIDIA system  

### 8.18 Final signal

Strong candidates make **invariants and deal-breakers** explicit, separate **PR CI from RC CI**, and treat driver versions as an immutable product API—not a filename someone typed.

---

*End of graphics git branching & release system design.*
