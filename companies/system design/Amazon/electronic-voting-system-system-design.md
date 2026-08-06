# System Design: Electronic Voting System

> **Focus areas:** Eligibility · Ballot casting · Secrecy vs auditability tradeoffs · Integrity · Tally · Abuse resistance · Observability without vote-buying channels · Operational trust  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Principled cryptography (no magical “blockchain votes”), explicit threat model, clear what is proven vs assumed, deal-breakers for “just encrypt ballots in Postgres”  
> **Interview theme:** Amazon SDE III / L6 — design an **electronic voting** system for elections or large org ballots: eligibility, cast, tally, audit—own integrity and abuse resistance; be careful and honest about security tradeoffs

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

Goal: **bound a voting product** that can register eligible voters, let them cast **one ballot** in a contest, protect **ballot secrecy**, produce a **correct tally**, and support **audit / dispute**—while resisting coercion, buying, and insider fraud. This is **not** “put votes on a public blockchain and call it done,” and not a general survey tool.

### 1.0 What this is / is not

| Dimension | **E-voting (this doc)** | Not this |
|-----------|-------------------------|----------|
| Primary job | Eligible cast → secret ballot → integrity-preserving tally | Straw poll / Typeform |
| Success | Correct eligible tally + justifiable audit story | Perfect coercion-resistance in all threat models |
| Hard problem | Secrecy **vs** auditability tension | Horizontal scale trivia alone |
| Trust | Explicit trust assumptions (admins, devices, observers) | Trustless magical crypto |
| Amazon lens | Threat modeling, ownership, blast radius, verifiability | Blockchain buzzwords |
| Scope realism | Often **org elections / constrained remote voting** first; public political elections need paper/risk-limiting audits in many jurisdictions |

**Important honesty (say in interview):** Internet voting for high-stakes political elections is scientifically and operationally fraught (malware on client, coercion at home). Design a **principled system** with stated assumptions; prefer architectures that support **software-independent** audits where required (e.g., paper ballot + electronic count assist). For Amazon-style interviews, a **remote authenticated ballot for org/union/shareholder/club elections** with strong integrity controls is a reasonable scope—call it out.

**Scope statement:** Design an electronic voting system covering eligibility, casting, secrecy/audit tradeoffs, integrity, tally, and abuse resistance—with progressive scale and explicit threat model.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Election types? | Single choice, multi-choice, ranked optional | Ballot schema |
| F2 | Eligibility? | Voter roll / membership list | Registration service |
| F3 | AuthN? | SSO / government ID / one-time codes | Strong auth + step-up |
| F4 | One vote? | Exactly one counted ballot per voter per contest | Tokens / nullification policy |
| F5 | Secrecy? | Cannot link voter→ballot in results | Separation of identity & ballot |
| F6 | Audit? | Prove eligibility & count integrity | Receipts / public boards / RLA hooks |
| F7 | Tally when? | After close; maybe running totals if allowed | Ceremony |
| F8 | Spoiling / change? | Allow replace until close OR irrevocable | Policy |
| F9 | Accessibility? | Screen readers; languages | UX constraints |
| F10 | Observers? | Independent auditors | Read-only evidence exports |
| F11 | Dispute? | Challenge process | Evidence packages |
| F12 | Admin ops? | Create election, freeze roll, close | Privileged workflows + dual control |
| F13 | Channels? | Web; maybe supervised kiosk | Client threat differs |
| F14 | Notifications? | “You voted” without revealing choice | Careful messaging |
| F15 | Multi-contest ballot? | Yes common | Atomic cast of ballot style |

**MVP functional scope:**

1. **Election setup:** contests, candidates/options, schedule, rules.  
2. **Voter roll:** import eligible set; freeze before open (or controlled updates).  
3. **Authenticate voter**; issue **single-use voting privilege** for election.  
4. **Cast ballot** (encrypted or anonymized path); acknowledge receipt **without** enabling vote-selling (careful).  
5. **At-most-one** counted ballot (replace-until-close **or** first-cast irrevocable—pick one).  
6. **Tally** after close with ceremony / threshold decryption or mixnet as chosen.  
7. **Publish results** + audit artifacts (encrypted ballot box, hashes, tallies).  
8. **Admin dual-control** for sensitive ops; full audit log of admin actions.  
9. Rate limits, anomaly detection, abuse locks.  
10. Observer export APIs.

**Out of MVP:**

- Claiming coercion-proof remote voting against family members watching  
- Fully trustless blockchain national election  
- Homomorphic tally of arbitrary ranked systems without specialist review  
- Client malware immunity  
- Real-time public per-precinct leaking that enables coercion  
- AI to “detect fraud” as sole integrity mechanism

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Integrity | Count matches eligible casts | Verifiable process; end-to-end evidence |
| N2 | Secrecy | No routine voter↔ballot link | Architectural separation + crypto/process |
| N3 | Availability | Cast window critical | 99.9%+ during election; static status page |
| N4 | Scalability | Burst at open/close | Progressive table |
| N5 | Auth strength | High assurance | MFA; phishing-resistant preferred |
| N6 | Auditability | Independent verification feasible | Published digests; observer tools |
| N7 | Abuse resistance | Credential stuffing, bots, buying | Limits, monitoring, receipt design |
| N8 | Operability | Clear ceremony ownership | Runbooks; dual control |
| N9 | Privacy retention | Minimize PII + ballot linkage data | TTL; key destruction |
| N10 | Transparency | Public methods | Document trust model |
| N11 | Latency | Cast interactive | p99 < 1–2s typical |
| N12 | Disaster | Region loss mid-election | Multi-AZ; careful dual-write |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Admin creates election → imports roll → freezes → opens.  
2. Voter authenticates → reviews ballot → submits → sees confirmation code (design carefully).  
3. Voter replaces ballot before close (if allowed) → only last counts.  
4. Close → threshold trustees decrypt / mix → publish tally + artifacts.  
5. Observer verifies ballot box hash chain matches published.  
6. Eligibility check prevents double registration.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Double cast attempt | Reject or supersede per policy |
| Auth succeeds but not on roll | Deny with generic message (anti-enumeration carefully balanced) |
| Ballot cast after close | Reject |
| Partial submit (network drop) | Idempotent cast tokens; clear state |
| Coercion / shoulder surfing | Limited technical mitigation; process warnings; optional panic PIN advanced |
| Vote buying via receipt | Avoid plaintext choice receipts; use tracking numbers that don’t prove choice to third parties without trapdoor |
| Insider tries to add ballots | Append-only ballot box + public count of eligible vs cast + dual control |
| Downtime mid-window | Queue status; extend window by ceremony; paper fallback if high stakes |
| Key loss for decryption | Threshold shares; ceremony rehearsals |
| Phishing site | Branding, phishing-resistant MFA, short links caution |
| Admin unilateral close early | Dual control + public event log |
| Ranked ballot invalid | Client+server validation schema |
| Homoglyph candidate names | Normalize display; freeze ballot definition |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Eligible voters | 100K | 1M | 10M | 100M |
| Contests / election | 5 | 10 | 20 | 50 |
| Peak cast QPS | 500 | 5K | 50K | 500K |
| Concurrent sessions | 20K | 200K | 2M | 20M |
| Ballot size | ~1–5 KB | similar | similar | similar |
| Admin elections concurrent | 10 | 100 | 1K | 10K (SaaS) |
| Audit export size | GB | tens GB | TB | many TB |
| Duration | hours–days | days | days | national window |

**What each jump forces:**

- **10×:** Stateless cast APIs; durable ballot box; MFA at scale; read replicas for status.  
- **100×:** Partition elections; pre-warm capacity; queueing; CDN for static ballot UI; sharded token service.  
- **1,000×:** Cell per geography/election; ceremony automation; paper/risk-limiting audit integration for political; extreme DDoS posture.

### 1.5 Etc. (Constraints & Assumptions)

- **Threat model must be stated** before choosing crypto.  
- Client device may be compromised—limit what E2E crypto can promise for remote voting.  
- Prefer **standard constructions** (threshold ElGamal + mixnet / homomorphic tallies; or separation via anonymous credential + anonymous channel) — don’t invent novel crypto in the interview.  
- **Process controls** (dual custody, observer logs, air-gapped tally) often beat overclaimed crypto.  
- Amazon bar: operational excellence for ceremonies; clear ownership of keys.

**Scope statement:**

> Design an electronic voting system for large authenticated elections: eligibility, one-ballot casting, architectural secrecy, integrity-preserving tally with audit artifacts, and abuse resistance—scaling cast bursts 10×/100×/1,000×—while being explicit about coercion and client-malware limits.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic split

```text
100K voters, many vote near deadline
Assume 40% in last 2 hours → 40K / 7200s ≈ 5.5/s average last window
Peak 50–100× spike with news → design ~500 cast/s baseline peak
At 100× voters: ~50K cast/s peak — web-scale burst problem
```

### 2.2 Storage

```text
Voter roll: 100K × 500B = 50 MB
Ballot box encrypted ballots: 100K × 2KB = 200 MB
Admin audit logs: tens of MB
At 100M voters: ballot box ~200 GB–2 TB + indexes — manageable vs secrecy engineering
```

### 2.3 Tally compute

```text
Homomorphic / mixnet tally: offline ceremony minutes–hours depending on scheme & N
Don’t put tally on synchronous user path
Verification by observers can be parallelized
```

### 2.4 Auth load

```text
Login QPS similar order to cast; MFA OTP issuance spikes
Cache roll membership checks; bloom/negative caching careful (don’t leak roll)
```

### 2.5 Bandwidth

```text
Cast POST ~5–20KB with overhead
500/s × 20KB = 10 MB/s — trivial vs integrity requirements
DDoS is availability threat more than bandwidth cost
```

### 2.6 Scale jump worksheet

| Jump | Bottleneck | Move |
|------|------------|------|
| 10× | Monolith DB locks on cast | Token service + append-only box |
| 100× | Auth/MFA & burst | Pre-warm; shard election; queue |
| 1,000× | National scrutiny + DDoS | Cells; ceremony; paper audit hooks |

### 2.7 Critical bottlenecks

1. Burst cast + auth.  
2. Key ceremony correctness.  
3. Insider ballot stuffing.  
4. Receipts enabling vote selling.  
5. Overpromised secrecy under coercion.

---

## 3. High-Level Design

### 3.1 Design goals (Amazon-flavored)

1. **Correctness of eligible tally** over flashy tech.  
2. **Explicit trust model** written down.  
3. **Secrecy ↔ audit tension** resolved with a chosen pattern (below).  
4. **Dual control** for privileged ops.  
5. **Abuse resistance** as first-class.  
6. **Operational ceremonies** rehearsed.  
7. **Burst availability** for cast window.

### 3.2 Core security properties (define precisely)

| Property | Meaning |
|----------|---------|
| Eligibility | Only roll members cast counted ballots |
| Uniqueness | At most one counted ballot per voter |
| Integrity | Tallied ballots = cast ballots; no silent modify |
| Secrecy (ballot) | Routine processes can’t link voter to choice |
| Verifiability | Individual / universal variants—pick level |
| Robustness | Incomplete decrypt / faults handled |
| Coercion resistance | Hard; often **out of scope** for remote—say so |

### 3.3 Architectural patterns (pick one; discuss tradeoffs)

#### Pattern A — Separate identity channel & anonymous ballot box (pragmatic MVP)

```text
1) Voter auth → spend one-time "cast token" (blinded or anonymized)
2) Ballot submitted with cast token proving eligibility without identity on ballot record
3) Ballot box stores encrypted/anonymous ballots
4) Tally decrypts ballots without voter ids
```

**Pros:** Understandable; good for org elections.  
**Cons:** Token issuance linkage if logs correlate time/IP; need careful network anonymity or accept residual risk.

#### Pattern B — Threshold encryption + homomorphic / mix tally (stronger classic e-voting)

```text
1) Voter auth; encrypt ballot to election public key (threshold)
2) Post encrypted ballot on append-only board with signature tying to voter OR use anonymous credential
3) After close: mixnet shuffle + decrypt OR homomorphic sum (yes/no / specific encodings)
4) Trustees threshold decrypt final
```

**Pros:** Strong audit literature.  
**Cons:** Complexity; specialist crypto; still weak against client malware & coercion.

#### Pattern C — Supervised kiosk + paper (high stakes)

```text
Electronic poll books + ballot marking devices + paper trail + RLA
```

**Pros:** Software-independent audits.  
**Cons:** Not “pure online”; often correct answer for national elections.

**Interview recommendation:** Start with **Pattern A** for org-scale remote; show you know **B** and when **C** is required. Never claim blockchain alone solves secrecy+coercion.

### 3.4 Core components

| Component | Responsibility |
|-----------|----------------|
| Election Admin Service | Config, schedule, freeze, dual control |
| Voter Roll Service | Eligibility records |
| Auth / IdP Integration | MFA login |
| Credential / Token Service | One-time cast rights |
| Ballot Definition Service | Immutable ballot styles after freeze |
| Casting API | Validate + accept ballots |
| Ballot Box (append-only) | Durable encrypted/anonymous ballots |
| Public Bulletin Board | Hashes/events for observers |
| Tally / Ceremony Service | Mix/decrypt/count |
| Results Service | Publish outcomes |
| Audit Export | Evidence packages |
| Abuse / Fraud Monitoring | Anomaly signals (not reading votes) |
| Notification | Cast confirmations (choice-safe) |

### 3.5 API sketch

```text
# Admin (dual control)
POST /admin/elections
POST /admin/elections/{id}/roll:import
POST /admin/elections/{id}/freeze
POST /admin/elections/{id}/open
POST /admin/elections/{id}/close

# Voter
POST /v1/elections/{id}/session      # after IdP
GET  /v1/elections/{id}/ballot
POST /v1/elections/{id}/cast
     body: { ballot_ciphertext_or_choices, client_nonce }
POST /v1/elections/{id}/cast:replace # if policy

# Observe
GET  /public/elections/{id}/board
GET  /public/elections/{id}/results
GET  /audit/elections/{id}/export
```

### 3.6 Data model

**elections** — id, state (`DRAFT/FROZEN/OPEN/CLOSED/TALLIED`), schedule, crypto params, policy flags  

**voters** — election_id, voter_id, eligibility flags, cast_state (`NONE/CAST`), token_id hash  

**ballot_styles** — immutable JSON schema after freeze  

**cast_tokens** — token_id, election_id, spent_at, (no choices)  

**ballot_box** — ballot_id, election_id, ciphertext/payload, cast_at, board_seq, prev_hash  

**admin_audit** — actor, action, reason, cosigner, ts  

**results** — contest tallies, ceremony transcript hash  

### 3.7 Cast flow (Pattern A sketch)

```text
1. Voter authenticates to IdP (MFA)
2. Casting service checks roll + not spent (or supersede policy)
3. Issues short-lived cast capability (server-side)
4. Client submits ballot payload
5. Server:
   - validates schema
   - appends to ballot box under anonymous ballot_id
   - marks voter cast_state without storing choices beside voter_id
   - writes bulletin board event (hash of ballot)
6. Returns confirmation: election id + opaque receipt (NOT cleartext choices)
```

**Separation rule:** DB tables joinable as `voter_id → ballot_choices` in plaintext is a **deal-breaker**.

### 3.8 Tally flow

```text
1. Freeze casting (close)
2. Publish ballot_box root hash
3. Ceremony: trustees present / threshold decrypt or mix
4. Count clear ballots / homomorphic sums
5. Publish results + transcript
6. Destroy/escrow keys per policy
```

### 3.9 Secrecy vs auditability tradeoffs (say this)

| Goal | Technique | Cost |
|------|-----------|------|
| Individual verifiability (“my ballot in box”) | Tracking number / inclusion proof | Can enable vote selling if proves **choice** |
| Universal verifiability | Public board + proofs | Complexity |
| Secrecy | No choice on receipt; unlink identity | Harder disputes of content |
| Coercion resistance | Panic PINs, deniable receipts | Rarely complete remotely |

**Principled MVP stance:**

- Offer **inclusion** proof (ballot hash on board) without revealing choice to a buyer.  
- Rely on **threshold trustees + observer verification** for universal integrity.  
- Do **not** email “You voted for Alice.”

### 3.10 Abuse resistance

| Abuse | Control |
|-------|---------|
| Credential stuffing | MFA, bot detection, lockouts |
| Ballot stuffing by insider | Append-only board; cast count ≤ eligible; dual control; code review |
| Vote buying | No choice-proving receipts; monitoring unusual patterns carefully |
| Phishing | Phishing-resistant MFA; education |
| DDoS | CDN, anycast, pre-provision, static status |
| Roll enumeration | Constant-time responses where needed |
| Admin fraud | Dual control + public event log |
| Client malware | Out of full scope; supervised voting / paper for high stakes |

### 3.11 Tradeoffs table

| Decision | A | B | Pick |
|----------|---|---|------|
| Replace until close | Yes | Irrevocable first | Org: replace; some legal: irrevocable |
| Receipt content | Choice | Opaque | Opaque |
| Crypto | Simple split | Threshold+mix | Split MVP; cite stronger |
| Running totals | Live | After close | After close default |
| Identity | Gov ID | Org SSO | Per context |
| Blockchain board | Public chain | Signed log | Signed append-only log sufficient often |

### 3.12 Deal-breakers

1. Plaintext `votes(voter_id, choice)` as system of record.  
2. “Blockchain” as sole integrity without eligibility model.  
3. Emailing cleartext choices.  
4. Single admin can change roll after open unnoticed.  
5. Claiming coercion-proof home voting.  
6. Inventing novel crypto under time pressure.  
7. Tally by manually downloading CSV as only path with no hashes.  
8. Availability engineering ignored for election night.

---

## 4. Architecture Diagram

### 4.1 End-to-end ASCII

```text
  Voters                    Observers
    │                          │
    ▼                          ▼
 IdP/MFA                   Public Board
    │                          ▲
    ▼                          │
┌─────────────┐   tokens  ┌────┴──────────┐
│ Cast API    │──────────▶│ Ballot Box    │
└──────┬──────┘           │ (append-only) │
       │                  └────┬──────────┘
       ▼                       │
 Voter Roll / Token Svc        │ close
       ▲                       ▼
       │                  Tally Ceremony
 Admin (dual control) ───▶ Results + Audit Export
```

### 4.2 Sequence: cast

```text
Voter→IdP→Cast API: get ballot
Voter→Cast API: submit
Cast API: authz + spend token + validate
Cast API→BallotBox: append encrypted/anon ballot
Cast API→Roll: mark cast
Cast API→Board: publish hash
Cast API→Voter: opaque receipt
```

### 4.3 Sequence: close & tally

```text
Admin+cosigner close → board event
Trustees threshold ceremony → decrypt/mix
Count → publish results + transcript hash
Observers verify inclusion & counts
```

### 4.4 Dual-control admin

```text
Action request by Admin A → pending
Admin B approves with reason → execute → audit log immutable
```

### 4.5 Multi-region cast

```text
Active-active cast APIs; single-writer ballot box partition per election
or regional cast logs merged with deterministic ceremony rules
Prefer: primary region per election for box consistency
```

### 4.6 High-stakes variant (paper)

```text
Electronic pollbook → BMD prints paper → scanner → RLA
E-system assists; paper is ballot of record
```

---

## 5. Design Deep Dive

### 5.1 Reliability & integrity

#### 5.1.1 Invariants

1. Counted ballots ≤ eligible voters.  
2. No plaintext join voter↔choice in OLTP.  
3. Ballot box append-only for an election epoch.  
4. Sensitive admin actions require N-of-M.  
5. Close is irreversible without extraordinary dual ceremony.  
6. Published board hashes match stored box.

#### 5.1.2 Failure modes

| Failure | Mitigation |
|---------|------------|
| Cast API down | Scale out; queue; extend window by policy |
| Duplicate submit | Idempotency key |
| Partial write | Txn: box append + token spend atomic (or compensating with board) |
| Lost decrypt keys | Threshold; backups; rehearsal |
| Insider delete ballots | WORM storage; external board mirrors |
| Clock skew close | NTP; absolute close ts; board sign |

#### 5.1.3 Durability & backup

- Multi-AZ ballot box; cross-region read replica for DR.  
- WORM / object lock for board segments.  
- Encrypted backups; key custody separate.

#### 5.1.4 Consistency nuances

- Voter sees “cast accepted” only after durable append.  
- Replace policy: superseding ballot marked; old invalidated but retained for audit.  
- Global uniqueness via token spend compare-and-set.

#### 5.1.5 Security & crypto principles

- Use vetted libraries; election public key generated in ceremony.  
- Threshold decryption (t-of-n trustees).  
- Avoid storing decryption key on app servers.  
- TLS everywhere; HSTS; strict CSP on ballot UI.  
- Minimize logs: never log choices.  
- Post-election key destruction / escrow policy legal-driven.

### 5.2 Scalability

#### 5.2.1 Cast path scaling

- Stateless cast app tier.  
- Shard token/roll by `voter_id`.  
- Ballot box partition by `election_id` (+ segment).  
- Pre-warm capacity before open.  
- Static assets on CDN; API only for cast.

#### 5.2.2 Auth scaling

- Cache sessions.  
- MFA provider capacity contracts.  
- Backup auth channels for outages (carefully).

#### 5.2.3 Tally scaling

- Offline batch; horizontal verify.  
- For 100M ballots, plan distributed mix/count—still ceremony-gated.

#### 5.2.4 Multi-tenant SaaS elections

- Cell per large customer.  
- Noisy neighbor isolation on cast bursts.  
- Per-election rate limits.

#### 5.2.5 DDoS / availability

- AnyCast, WAF, SYN cookies, cast-specific rate limits.  
- Graceful degrade: read-only “election status” static.  
- Don’t shed integrity checks under load.

#### 5.2.6 Cost controls

- Storage modest; spend is security review, ceremonies, redundancy, support.  
- Don’t overspend on exotic crypto without need.

### 5.3 Maintainability & ownership

#### 5.3.1 Ownership map

| Surface | Owner |
|---------|-------|
| Election admin UX | Product elections |
| Roll & eligibility | Identity/eligibility |
| Cast path | Casting service |
| Crypto/ceremony | Security engineering |
| Bulletin board | Transparency eng |
| Abuse monitoring | Trust & safety |
| Infra burst | SRE |

#### 5.3.2 Safe evolution

- Freeze ballot schema before open.  
- Protocol version embedded in ballot ciphertext header.  
- Never “hot fix” crypto mid-election without ceremony.

#### 5.3.3 Observability & SLOs

| SLO | Target |
|-----|--------|
| Cast success p99 latency | < 2s |
| Cast availability in window | 99.9%+ |
| Token spend correctness | 100% (data integrity) |
| Board publish lag | < few seconds |
| Zero choice leakage in logs | Audited |

Metrics that **must not** exist: dashboards of live choice distributions if secrecy forbids (or carefully delayed).

#### 5.3.4 Progressive scale checklist

**10×:** append-only box; MFA; dual control; opaque receipts.  
**100×:** shards; pre-warm; public board mirrors; anomaly detection.  
**1,000×:** geo cells; formal ceremony automation; RLA/paper integration options.

### 5.4 Deep dive: uniqueness

```text
CAST policy irrevocable:
  CAS voter.cast_state NONE→CAST; fail if already CAST

REPLACE policy:
  write new ballot; mark previous ballot_id SUPERSEDED
  voter.current_ballot_id = new
  count only non-superseded at tally
```

### 5.5 Deep dive: bulletin board

```text
event_seq, event_type, payload_hash, prev_hash, signature
Types: ROLL_FROZEN, OPEN, BALLOT_CAST, CLOSE, TALLY
Observers subscribe; mirrors on S3 + independent hosts
```

### 5.6 Deep dive: receipt design

```text
Good: receipt = HMAC(election_id, ballot_id, server_secret) + inclusion seq
Voter can check ballot_id hash appears on board
Buyer cannot learn choice from receipt alone
Bad: receipt includes candidate id plaintext
```

### 5.7 Deep dive: threshold ceremony

```text
Keygen ceremony pre-election: n trustees, threshold t
Decrypt ceremony post-close: ≥t show up; produce transcript
Rehearse on staging with fake ballots
Lost share protocol documented
```

### 5.8 Deep dive: what cryptography cannot fix

- Malware changing vote client-side before encryption.  
- Coercion at kitchen table.  
- Voters photographing ballot.  
- Nation-state targeted phishing.  

**Mitigations are process:** supervised polling, paper, risk-limiting audits, legal deterrence.

### 5.9 Testing & resilience

| Test | Purpose |
|------|---------|
| Double spend tokens | Uniqueness |
| Chaos kill cast mid-write | Atomicity |
| Log redaction scans | Secrecy |
| Ceremony dry runs | Ops |
| Load test open/close | Burst |
| Insider table join attempts | Architecture tests |
| Board hash verify tool | Audit UX |

### 5.10 Comparison: survey vs e-vote vs political election

| | Survey | Org e-vote | Political |
|--|--------|------------|-----------|
| Eligibility | Soft | Hard | Legal roll |
| Secrecy | Mild | Strong | Strong + law |
| Audit | Weak | Board+dual control | RLA/paper often |
| Coercion | Low concern | Medium | Critical |

### 5.11 Amazon leadership connection (brief)

- Dive deep on threat model, not buzzwords.  
- Ownership of ceremony checklists.  
- Disagree & commit on replace vs irrevocable with legal.  
- Frugality: don’t buy blockchain if signed log suffices.  
- Customer trust: silence on live partial results if required.

---

## 6. Wrap-Up

### 6.1 30-second recap

> I’d lock eligibility in a frozen voter roll, authenticate with MFA, and enforce **one counted ballot** via atomic token spend. Ballots go to an **append-only ballot box** architecturally separated from identity, with a **public bulletin board** of hashes. Receipts prove inclusion **without** revealing choices. Tally is a **post-close ceremony** (threshold decrypt/mix or careful anonymous count). I’d be explicit that remote coercion and client malware are not fully solved, and for highest stakes recommend paper/RLA. Scale the cast burst with sharding and pre-warm—not by weakening integrity checks.

### 6.2 Key tradeoffs

1. Pattern A vs B vs paper.  
2. Replace-until-close vs irrevocable.  
3. Individual verifiability vs vote-buying.  
4. Live totals vs secrecy.  
5. Signed log vs public blockchain.  
6. Availability extensions vs election rules.

### 6.3 Risks & follow-ups

- Residual traffic analysis linking.  
- Trustee collusion.  
- Client compromise.  
- Admin social engineering.  
- Legal requirements mismatch.  
- Overconfidence in crypto.

### 6.4 What “good” looks like

- Threat model in first 5 minutes.  
- Secrecy vs audit called out.  
- No plaintext vote table.  
- Dual control.  
- Honest coercion limits.  
- Burst plan + deal-breakers.

---

## 7. Deeper / Related Interview Questions

### 7.1 Requirements & threat model (Q1–Q16)

1. Org election or national?  
2. Adversaries: insider, nation-state, buyer?  
3. Supervised vs home voting?  
4. Legal audit requirements?  
5. Ranked choice needed?  
6. Write-ins?  
7. Provisional ballots?  
8. Accessibility law?  
9. Language support?  
10. Overseas voters?  
11. Observation rights?  
12. Retention law?  
13. Running tallies allowed?  
14. Voter can abstain?  
15. Multi-contest atomicity?  
16. What is explicitly out of scope?

### 7.2 Eligibility & auth (Q17–Q32)

17. Roll freeze timing.  
18. Same-day registration.  
19. Identity proofing.  
20. Phishing-resistant MFA.  
21. Account recovery mid-election.  
22. Shared family email risk.  
23. Voter enumeration.  
24. Deceased voters.  
25. Duplicate identities.  
26. SSO outage.  
27. Step-up auth.  
28. Device binding.  
29. Accessibility vs security.  
30. Credential mailing.  
31. In-person proofing.  
32. Roll public/private.

### 7.3 Crypto & verifiability (Q33–Q52)

33. Explain threshold encryption.  
34. Mixnet vs homomorphic.  
35. Why not invent MAC-only.  
36. Blockchain pros/cons.  
37. Bulletin board design.  
38. Inclusion proofs.  
39. Receipt attacks.  
40. Panic PIN concept.  
41. Software independence.  
42. Risk-limiting audits.  
43. End-to-end verifiability defs.  
44. Client-side encryption trust.  
45. HSM use.  
46. Ceremony transcripts.  
47. Post-quantum posture.  
48. Zero-knowledge use cases.  
49. Separability of identity.  
50. Timing correlation.  
51. Network anonymity (Tor) tradeoffs.  
52. When crypto is overkill.

### 7.4 Integrity ops & abuse (Q53–Q68)

53. Dual control patterns.  
54. Insider detection.  
55. Ballot stuffing tests.  
56. DDoS on election day.  
57. Extending windows.  
58. Incident response mid-cast.  
59. Dispute workflow.  
60. Observer tooling.  
61. Log redaction.  
62. Key destruction.  
63. Change management freeze.  
64. Pen test cadence.  
65. Bug bounty during election?  
66. Social engineering admins.  
67. Media partial results leak.  
68. Post-election audit calendar.

### 7.5 Scale & Amazon (Q69–Q80)

69. Peak cast capacity plan.  
70. Shard strategy.  
71. Multi-region box.  
72. Cost vs assurance.  
73. Ownership map.  
74. SLO vs integrity.  
75. Bar-raiser threat model.  
76. Dive-deep story.  
77. Disagree on blockchain.  
78. Frugality in security.  
79. Customer (voter) trust comms.  
80. 45-minute plan.

---

## 8. Appendices

### Appendix A — Election state machine

```text
DRAFT → FROZEN_ROLL → OPEN → CLOSED → CEREMONY → TALLIED → ARCHIVED
          ↓                      ↓
        ABORTED                SUSPENDED (exceptional)
```

### Appendix B — Opaque receipt (sample)

```json
{
  "election_id": "e_42",
  "ballot_id": "b_9f...",
  "board_seq": 12044,
  "receipt": "hexhmac...",
  "message": "Your ballot was accepted. Choices are not shown."
}
```

### Appendix C — Bulletin event (sample)

```json
{
  "seq": 12044,
  "type": "BALLOT_CAST",
  "payload_hash": "sha256:...",
  "prev_hash": "sha256:...",
  "sig": "..."
}
```

### Appendix D — Error codes

| Code | Meaning |
|------|---------|
| 401 | Auth |
| 403 | Not eligible / already cast |
| 409 | Election not open |
| 422 | Invalid ballot |
| 429 | Rate limited |
| 503 | Temporary; retry |

### Appendix E — Anti-patterns

- Plaintext votes table.  
- Emailing choices.  
- Single admin superuser.  
- Novel crypto.  
- Blockchain-only eligibility.  
- Live choice dashboards under secrecy rules.  
- Logging request bodies.  
- Claiming coercion-proof remote voting.

### Appendix F — Capacity worksheet

```text
eligible_voters =
peak_cast_qps =
mfa_qps =
ballot_bytes =
box_storage =
trustees_t_of_n =
board_mirror_count =
```

### Appendix G — 45-minute timebox

| Min | Topic |
|-----|-------|
| 0–7 | Threat model + scope honesty |
| 7–15 | Eligibility + uniqueness |
| 15–28 | Cast path + secrecy/audit |
| 28–36 | Tally ceremony + abuse |
| 36–42 | Scale burst + ops |
| 42–45 | Wrap |

### Appendix H — Glossary

| Term | Meaning |
|------|---------|
| Ballot box | Store of cast ballots |
| Bulletin board | Public append-only evidence |
| Threshold decrypt | t-of-n key shares |
| Mixnet | Shuffle to break order linkage |
| RLA | Risk-limiting audit |
| Software independence | Detect wrong outcome without trusting software |
| Cast token | One-time eligibility capability |

### Appendix I — Ownership RACI

| Item | R | A | C | I |
|------|---|---|---|---|
| Ceremony | Security | Security | Legal | Observers |
| Cast availability | SRE | Casting | Security | Voters |
| Roll accuracy | Eligibility | Product | Legal | Auditors |
| Receipt UX | Product | Product | Security | Support |

### Appendix J — Progressive scale one-pager

| Scale | Must |
|-------|------|
| 1× | Roll+cast+box+dual control |
| 10× | Board+opaque receipts+MFA |
| 100× | Shard+prewarm+mirrors |
| 1,000× | Cells+RLA/paper options |

### Appendix K — Trust assumptions checklist

- [ ] IdP correctly authenticates humans  
- [ ] ≤ t-1 trustees corrupt  
- [ ] Ballot UI not malware (or accept residual risk)  
- [ ] Observers check board  
- [ ] Admins dual-controlled  
- [ ] Coercion out of scope / mitigated by process  

### Appendix L — Minimal threat model

| Adversary | Goal | Control |
|-----------|------|---------|
| External hacker | Stuff ballots | Auth + board |
| Insider admin | Alter tally | Dual control + WORM |
| Vote buyer | Proof of choice | Opaque receipts |
| Coercer | Watch vote | Limited; process |
| DDoS | Block casting | Capacity + CDN |

### Appendix M — Token spend pseudocode

```text
function cast(voter, ballot):
  assert election.open
  assert on_roll(voter)
  token = begin_spend(voter) // CAS
  id = append_box(anonymize(ballot))
  board.append(hash(id))
  commit_spend(token, id)
  return receipt(id)
```

### Appendix N — What to publish

| Artifact | Public? |
|----------|---------|
| Ballot definition | Yes |
| Roll size | Often yes |
| Board hashes | Yes |
| Results | Yes |
| Individual choices | No |
| Voter PII | No |

### Appendix O — Interview “say this” (60 seconds)

> “I’d start from a threat model: eligibility, uniqueness, integrity, secrecy, and be honest that home coercion and malware aren’t fully solvable online. Architecturally I’d separate identity from an append-only ballot box, use MFA and atomic cast tokens, publish a hash bulletin board, and tally via a threshold ceremony after close. Receipts prove inclusion without revealing choices. Dual control for admin. Scale cast bursts with sharding and pre-warm. For national high-stakes, I’d argue for paper and risk-limiting audits.”

### Appendix P — Related systems map

| System | Relation |
|--------|----------|
| SurveyMonkey | Weak cousin |
| Helios / academic e-vote | Crypto patterns |
| Election board systems | High stakes analogue |
| Public transparency logs | Board inspiration |
| HSM/KMS | Key custody |
| IdP/SSO | Auth |

### Appendix Q — Chaos / ceremony drills

1. Kill cast DB mid-append.  
2. Trustee no-show.  
3. Board mirror divergence.  
4. DDoS simulation.  
5. Attempt join voter to ballot in analytics warehouse (must fail).  
6. Replace-policy race.  
7. Clock jump near close.  
8. Phishing drill.

### Appendix R — Metrics catalog (safe)

- `cast_success_rate`  
- `cast_p99`  
- `token_spend_conflicts`  
- `board_lag`  
- `auth_failures`  
- `admin_pending_actions`  
- **Not:** live per-candidate counters if forbidden  

### Appendix S — Dual-control policy examples

| Action | Required |
|--------|----------|
| Open election | 2 admins |
| Close election | 2 admins |
| Roll change after freeze | Forbidden or 3 + legal |
| Export decrypt shares | Ceremony only |
| Publish results | 2 + checksum |

### Appendix T — Ranked ballot note

```text
Validate strict ranking constraints server-side
Tally method (IRV etc.) specified before open
Homomorphic IRV is research-grade — often decrypt-then-count after mix
```

### Appendix U — Logging redaction rules

```text
DenyList fields: choices, rankings, ciphertext if linkable, raw tokens
Allow: election_id, latency, error codes, anonymous ballot_id after accept
```

### Appendix V — Comparison checklist

| Checkpoint | Covered? |
|------------|----------|
| Threat model | Yes |
| Secrecy vs audit | Yes |
| Uniqueness | Yes |
| Dual control | Yes |
| Honest coercion limits | Yes |
| Burst scale | Yes |
| Deal-breakers | Yes |

### Appendix W — Legal / compliance hooks

- Data retention schedules  
- Accessibility (WCAG)  
- Election law freeze dates  
- Observer rights  
- Breach notification  

### Appendix X — Why not “encrypt row with voter key only”

```text
If server can decrypt to tally, server can read choices → secrecy depends on process
If only voter decrypts, tally impossible
Need election keys / anonymization / homomorphic — not naive per-user encrypt
```

### Appendix Y — SaaS multi-election isolation

```text
election_id as tenant partition
Separate KMS keys per election
No cross-election analytics joins on ballots
```

### Appendix Z — Final SDE III checklist

- [ ] Threat model stated  
- [ ] Eligibility + uniqueness  
- [ ] No plaintext vote SOT  
- [ ] Board + tally ceremony  
- [ ] Receipts without choice leak  
- [ ] Dual control  
- [ ] Abuse + DDoS  
- [ ] Coercion honesty  
- [ ] 10×/100×/1,000×  
- [ ] Deal-breakers  

---

*End of electronic voting system design (Amazon SDE III).*
