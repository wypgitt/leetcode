# System Design: Electronic Voting System

> **Focus areas:** Identity/eligibility · Ballot secrecy · Integrity/audit · Idempotent vote · Availability windows · Results · Threat model · Observability without leaking
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Correct arithmetic, explicit invariants, resolved ownership, honest MVP vs extreme-scale paths
> **Interview theme:** Amazon SDE III / L6 — **Electronic voting system** — integrity and secrecy over clever scale tricks

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-q&a)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---

## 1. Clarify Requirements (Interview Q&A)

Goal: design an **electronic voting system** for elections/polls: eligibility, authenticated voting, ballot secrecy, tamper-evident tallies, auditability, and controlled result publication—Amazon bar on threat modeling and ownership.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Cast+tally votes with audit | General social upvote |
| Properties | Integrity, eligibility, secrecy (as scoped) | Perfect coercion-resistance world |
| Amazon lens | Threat model, audit, SEV ownership | Blockchain hype default |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Voters? | Eligible registry | Strong identity proofing |
| F2 | Auth? | Multi-factor during window | Session binding |
| F3 | Ballot? | One vote per race rules | Idempotent cast |
| F4 | Secrecy? | Separate identity from ballot store | Crypto/process controls |
| F5 | Audit? | Append-only cast receipts / ledgers | Public verifiability optional |
| F6 | Window? | Open/close times | Hard cutoffs |
| F7 | Results? | Publish after close+audit | No early leak |
| F8 | Accessibility? | Multi-channel | Out of deep MVP ok |
| F9 | Adversary? | Insiders+DDoS+malware | Threat model explicit |
| F10 | Absentee? | Optional early ballots | Same integrity |
| F11 | Multi-jurisdiction? | Cells per district | Isolation |
| F12 | Dispute? | Risk-limiting audit hooks | Paper optional |

**MVP scope:**

1. Eligibility check
2. AuthN during election window
3. Cast encrypted/blinded ballot once
4. Append-only cast log
5. Tally after close
6. Admin open/close
7. Rate limit+DDoS protections
8. Audit export
9. Monitor without revealing choices

**Out of MVP:** Perfect coercion resistance under family voting; On-chain public everything; National ID replacement project.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Cast latency | p99<2s |
| N2 | Integrity | No undetected alteration |
| N3 | Secrecy | No link identity↔choice in online stores as scoped |
| N4 | Avail during window | 99.9%+ with queues |
| N5 | Cutoff | No casts after close |
| N6 | Audit | Complete trail |
| N7 | DDoS | Absorb/shed |
| N8 | Ops | Least privilege admins |

### 1.3 Cases

**Happy:** eligible login→select→cast once→receipt→after close tally→publish.
**Edges:** double cast; close race; DDoS on close; insider tally tamper; receipt mismatch; early result leak; compromised client.

| Case | Behavior |
|------|----------|
| Duplicate request | Idempotent key returns same result |
| Partial failure mid-path | Compensate or retry with fencing/CAS |
| Hot partition / noisy neighbor | Shuffle shard + fair-share quotas |
| Region / AZ loss | Cell failover; degrade non-critical |
| Clock skew | Server-side truth; opaque tokens |
| Poison input | Quarantine/DLQ; never silent drop of accepted work |
| Authz miss | Fail closed; audit |
| Traffic surge 10× | Shed by priority; preserve SLO class |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Voters | 1M | 10M | 100M | 500M |
| Peak cast/s | 500 | 5K | 50K | 200K |
| Races/ballot | 10 | 20 | 30 | 50 |
| Districts/cells | 50 | 500 | 5K | 50K |
| Election window | 12h | 24h | 48h | days |
| Audit artifacts | GB | 10s GB | TB | 10s TB |

**Jumps:** 10× shard by district; 100× geo cells+edge; 1,000× national multi-jurisdiction federation.

### 1.5 Scope repeat-back

> Election-window voting with eligibility, single-cast integrity, secrecy controls, append-only audit, post-close tally/publish.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Peak

```text
10M voters / 4h ≈ 700/s avg; peak 5–10×
```

### 2.2 Ballot size

```text
few KB encrypted
```

### 2.3 Ledger

```text
append-only 10M rows
```

### 2.4 Tally

```text
batch per race after close
```

### 2.X Bottlenecks

(1) Hot keys/partitions (2) synchronous fan-out (3) durable write path (4) auth/token validation (5) downstream blast radius (6) not abstract QPS alone.

### 2.Y Cost / frugality

Prefer cheaper read paths over linear DB growth; measure unit cost per successful customer action; sample observability firehoses.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Identity/eligibility | Who may vote | Strong |
| Casting | Accept ballots | Unique per voter/race |
| Ballot secrecy store | Choices | Separated |
| Audit ledger | Tamper-evident | Append-only |
| Tally/publish | Results | After close |

**Deal-breaker:** mixing control-plane config mutations into the data-plane hot path without isolation.

### 3.2 Components

1. **Voter registry** — Eligibility
2. **Auth service** — MFA
3. **Ballot UI/API** — Cast
4. **Cast coordinator** — Idempotent single cast
5. **Encrypted ballot store** — Choices
6. **Receipt service** — Voter proof
7. **Append-only log** — Hash chained
8. **Tally service** — Decrypt/mix as designed
9. **Publish** — Results
10. **Admin control** — Open/close
11. **WAF/DDoS** — Edge
12. **Audit tools** — Export/verify

### 3.3 API sketch

```text
POST /v1/elections/{id}/cast {race_choices} Idempotency
GET /v1/receipt/{id}
POST /v1/admin/close
GET /v1/results (after publish)
```

### 3.4 State machine

```text
Election: SETUP→OPEN→CLOSED→TALLYING→PUBLISHED
Vote: ELIGIBLE→CAST→FINAL (no change or policy-limited)
```

### 3.5 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Secrecy vs audit | Separation+crypto | Tension explicit |
| Change vote | Policy: last cast before close or immutable | Product/law |
| Blockchain | Usually unnecessary | Ops complexity |
| Online only | Optional paper RLA | Trust |
| Early results | Forbidden | Integrity |

---

## 4. Architecture Diagram

```text
Voters->Edge/WAF->Auth->Cast API->Cast Coordinator
Coordinator->Ballot Store (separated)
Coordinator->Append-only Ledger
Close->Tally->Publish
Registry->Auth
```

### 4.1 Cast

```text
Authz eligible→not already final→persist ballot+ledger+receipt txn/outbox→ACK
```

### 4.2 Close

```text
Flip gate; reject late; freeze
```

### 4.3 Tally

```text
Authorized ceremony; produce results+audit artifacts
```

### 4.N Cell / blast-radius model

```text
Each cell = failure domain (AZ-set or region slice)
No synchronous cross-cell locks on hot path
Control plane pushes config; data plane serves locally
Shuffle sharding for multi-tenant isolation
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. No cast outside window
2. At most one final vote per rules
3. Ledger append-only
4. Tally only when closed
5. Results not early
6. Admin actions dual-control
7. Receipt matches ledger
8. Monitoring doesn't emit choices

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single region hardened |
| 10× | Shard districts |
| 100× | Geo cells; edge cast |
| 1000× | Federated jurisdictions |

### 5.3 Maintainability

- Ceremony runbooks
- Key custody drills
- Load tests near close
- Independent audit tools

### 5.4 Progressive scale narrative

**1×:** City election
**10×:** State
**100×:** National multi-cell
**1000×:** Multi-country federation patterns

### 5.5 Single cast

Unique constraint (election,voter,race) with CAS.

### 5.6 Secrecy separation

Identity tokens ≠ ballot rows join keys online.

### 5.7 Hash ledger

Hash chain / merkle; detect tamper.

### 5.8 Close thundering herd

Queue; do not lose accepted pre-close.

### 5.D Deal-breakers

| Temptation | Failure |
|------------|---------|
| Mutable tallies w/o audit | Stolen election SEV |
| Identity joined to ballot in logs | Secrecy fail |
| Accept after close | Illegitimacy |
| Single admin superpower | Insider risk |
| Blockchain theater without requirements | Wasted trust |
| Public live totals mid-vote | Coercion/bandwagon |

---

## 6. Wrap-Up

### 6.1 Designed

E-voting: eligibility+MFA, single-cast coordinator, secrecy-separated ballot store, append-only ledger, ceremony tally, DDoS-hardened window.

### 6.2 Decisions to defend

1. Hard election window
2. Idempotent single cast
3. Separated secrecy stores
4. Append-only hash ledger
5. Post-close tally only
6. Dual-control admin
7. District cells
8. Receipts for voters

### 6.3 Risks

- Client malware
- Coercion
- Insider keys
- DDoS at close
- Legal process gaps

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Threat model+properties |
| 5–15 | Eligibility+cast |
| 15–25 | Secrecy vs audit |
| 25–35 | Ledger+tally ceremony |
| 35–45 | Scale close+DDoS |

### 6.5 Closer

> **Electronic Voting System**: eligibility, single-cast integrity, secrecy separation, append-only audit, post-close tally—threat model first, hype last.

---

## 7. Deeper / Related Interview Questions

### Interview cards (drill these aloud)

### Card 1: Properties?

Eligibility, integrity, secrecy, audit.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 2: Double vote?

Unique CAS constraint.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 3: Secrecy how?

Separate stores/crypto.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 4: Receipt?

Shows cast recorded not choice publicly.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 5: Close time?

Hard gate+queue drain.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 6: DDoS?

Edge shed+capacity.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 7: Insider?

Dual control+ledger.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 8: Blockchain?

Rarely required.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 9: Paper audit?

RLA hooks optional.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 10: Early leak?

No live totals.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 11: Change mind?

Policy explicit.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 12: Who pages?

Election control plane.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 13: Key ceremony?

Documented custody.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 14: Mobile malware?

Threat residual; education+HSM optional.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 15: Deal-breaker?

Silent tally mutation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

### Card 16: Unit cost?

Secondary to integrity.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored.

---

## 8. Appendices

### A. Glossary

| Term | Meaning |
|------|---------|
| Cell | Isolated failure domain for blast-radius control |
| Fence / fencing token | Invalidates stale writers after lease steal |
| Idempotency key | Client key making retries safe |
| Outbox | Durable event publish coupled to DB commit |
| Shuffle sharding | Map tenants to overlapping server subsets |
| SLO / error budget | Reliability contract; burn rate drives decisions |
| Unit cost | $ per successful customer action |
| DLQ | Dead-letter queue for poison / exhausted retries |
| Control vs data plane | Config/orchestration vs hot-path serving |
| Progressive scale | Explicit 10×/100×/1,000× architecture jumps |

### B. Ownership matrix

| Concern | Owns | Pages when |
|---------|------|------------|
| Hot-path latency/errors | Serving team | p99 / 5xx burn |
| Durability / data loss risk | Storage/data team | RPO/RTO alarms |
| Abuse / security | Trust & safety / AppSec | exploit or abuse spike |
| Cost regression | Serving + FinOps | unit-cost burn |
| Downstream dependency | Owning service | dependency SEV |

### C. Metrics that matter

- Success rate by criticality class
- Latency histograms (p50/p90/p99) on customer-visible path
- Queue lag / backlog age
- Retry / duplicate attempt rate
- Cache hit ratio where applicable
- Error budget burn rate
- Unit cost trend
- Cell imbalance / hot partition indicators

---

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope & non-goals |
| 5–12 | Back-of-envelope math |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive invariants & failures |
| 35–45 | Progressive scale, ownership, SEV |

---

## 10. Operability

### Golden signals

cast success, reject reasons, auth fail, ledger append lag, unique violations, edge 5xx, time-to-close drain, audit verify status

### Rollback ladder

freeze casts→revert cast service→keep ledger immutable always→delay publish

### Kill switches

close election early (policy); disable district; block IP classes; freeze tally publish

### Security / privacy

MFA; HSM keys; dual control; minimal logs; red-team; supply chain on clients

### Cost worksheet

Integrity>cost; still avoid unbounded video KYC; scale edges for peak window only

```text
monthly_$ ≈ traffic_units * unit_cost + storage_GB * $/GB-month + egress
Optimize the dominant term first; measure before optimizing the rest.
```

### Progressive scale (ops view)

- **10×:** horizontal scale + caching + partition by key
- **100×:** cells, multi-region DR, fair multi-tenant isolation
- **1,000×:** edge / specialization, stronger automation, chaos drills

### Cross-team deps

Identity proofing, edge/DDoS, HSM/KMS, legal/compliance, independent auditors, UX a11y

---

## More Interview Q&A — Electronic Voting System

**Q1. Homomorphic tally?**

**A:** Optional advanced.

**Q2. Mixnets?**

**A:** Optional secrecy tech.

**Q3. SMS OTP enough?**

**A:** Often weak; layer.

**Q4. Public bulletin board?**

**A:** Optional transparency.

**Q5. Voter ID photo?**

**A:** PII heavy; careful.

**Q6. Overseas voters?**

**A:** Latency+auth.

**Q7. Exit polls?**

**A:** Outside system.

**Q8. Partial results by district?**

**A:** After local close policy.

**Q9. Pen testing?**

**A:** Mandatory pre-election.

**Q10. What not?**

**A:** Token-gated crypto hype without requirements.

**Q11. How do you canary this?**

**A:** Percent or cell-scoped; auto-rollback on SLO burn.

**Q12. What is the SEV1 customer line?**

**A:** State impact, blast radius, mitigation, next update ETA.

**Q13. How do you test failure?**

**A:** Game day: kill AZ, dependency timeout, duplicate inject.

**Q14. What is read-your-write strategy?**

**A:** Sticky session, sync path, or version tokens as needed.

**Q15. How do you bound cardinality?**

**A:** Allowlists, quotas, deliberate metric labels.

**Q16. What is the degrade mode?**

**A:** Shed noncritical; preserve integrity/security path.

**Q17. How do you handle poison?**

**A:** Quarantine/DLQ; alert owner; capped redrive.

**Q18. What is multi-region story?**

**A:** Home cell writes; regional reads/failover documented.

**Q19. How do you prevent noisy neighbors?**

**A:** Quotas + shuffle sharding + fair queues.

**Q20. What would you not build in MVP?**

**A:** Perfect coercion resistance under family voting.

---

## Worked Capacity Narrative — Electronic Voting System

Peak is short; pre-warm edges. Never scale by weakening audit or uniqueness.

## Customer-Trust Paragraph — Electronic Voting System

Undetected alteration or secrecy breach ends legitimacy. Design for auditors as first-class users.

## Progressive Scale Recap — Electronic Voting System

- **10×:** partition, cache, and operational playbooks
- **100×:** cells, multi-tenant isolation, multi-region DR
- **1,000×:** specialization, edge/hierarchy, chaos automation

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Electronic Voting System

### S1. Threat model first

Adversaries explicit before components.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S2. Election window gates

Hard open/close.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S3. Single-cast integrity

CAS unique votes.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S4. Secrecy separation

No online identity↔choice join.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S5. Append-only ledger

Tamper evidence.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S6. Ceremony tally

Controlled post-close.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S7. Dual-control admin

No lone superuser.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

### S8. District cells

Blast radius / scale.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs platform vs security/privacy—who pages?

## Scenario Runbooks — Electronic Voting System

| Scenario | Immediate action | Customer impact | Follow-up |
|----------|------------------|-----------------|----------|
| DDoS at close | Enable shed; expand edge | Delayed cast UX | Capacity postmortem |
| Suspected ledger gap | Freeze tally; investigate | Delay results | Audit |
| Key compromise | Rotate; ceremony halt | Trust risk | Custody redesign |
| Double-cast bug | Stop casts; reconcile | Integrity risk | Unique constraint fix |
| Early results leak | Investigate channel | Fairness risk | Access revoke |
| Auth outage | Queue; extend? policy | Access pain | IdP failover |


## Rapid-Fire Q&A — Electronic Voting System

**RQ1. Why does 'Threat model first' matter in an L6 interview?**

**A:** Adversaries explicit before components. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ2. How would you test 'Threat model first' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ3. What regresses if 'Threat model first' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ4. Why does 'Election window gates' matter in an L6 interview?**

**A:** Hard open/close. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ5. How would you test 'Election window gates' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ6. What regresses if 'Election window gates' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ7. Why does 'Single-cast integrity' matter in an L6 interview?**

**A:** CAS unique votes. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ8. How would you test 'Single-cast integrity' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ9. What regresses if 'Single-cast integrity' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ10. Why does 'Secrecy separation' matter in an L6 interview?**

**A:** No online identity↔choice join. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ11. How would you test 'Secrecy separation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ12. What regresses if 'Secrecy separation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ13. Why does 'Append-only ledger' matter in an L6 interview?**

**A:** Tamper evidence. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ14. How would you test 'Append-only ledger' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ15. What regresses if 'Append-only ledger' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ16. Why does 'Ceremony tally' matter in an L6 interview?**

**A:** Controlled post-close. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ17. How would you test 'Ceremony tally' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ18. What regresses if 'Ceremony tally' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ19. Why does 'Dual-control admin' matter in an L6 interview?**

**A:** No lone superuser. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ20. How would you test 'Dual-control admin' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ21. What regresses if 'Dual-control admin' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.

**RQ22. Why does 'District cells' matter in an L6 interview?**

**A:** Blast radius / scale. Call the deal-breaker alternative and the unit-cost or trust implication.

**RQ23. How would you test 'District cells' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion.

**RQ24. What regresses if 'District cells' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump fixes it.


## Narrative Walkthrough — Electronic Voting System

### Walkthrough beat 1

Voter authenticates; eligibility ok.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 2

Cast ballot; unique constraint; ledger append; receipt.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 3

Retry cast returns same receipt.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 4

Post-close cast rejected.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 5

Tally ceremony produces results+artifacts.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 6

Publish results; public audit tools verify ledger root.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 7

District cell isolation under load.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

### Walkthrough beat 8

10× shard; 100× geo; 1,000× federation. Deal-breaker: mutable silent tally.

Call out one tradeoff you are making and why Amazon customer obsession prefers that tradeoff here.

## Pre-Onsite Checklist — Electronic Voting System

- [ ] Can explain **Threat model first** with numbers and a deal-breaker
- [ ] Can explain **Election window gates** with numbers and a deal-breaker
- [ ] Can explain **Single-cast integrity** with numbers and a deal-breaker
- [ ] Can explain **Secrecy separation** with numbers and a deal-breaker
- [ ] Can explain **Append-only ledger** with numbers and a deal-breaker
- [ ] Can explain **Ceremony tally** with numbers and a deal-breaker
- [ ] Can explain **Dual-control admin** with numbers and a deal-breaker
- [ ] Can explain **District cells** with numbers and a deal-breaker
- [ ] Has a 30-second runbook for **DDoS at close**
- [ ] Has a 30-second runbook for **Suspected ledger gap**
- [ ] Has a 30-second runbook for **Key compromise**
- [ ] Has a 30-second runbook for **Double-cast bug**
- [ ] Has a 30-second runbook for **Early results leak**
- [ ] Has a 30-second runbook for **Auth outage**
- [ ] Progressive scale 10×/100×/1,000× story rehearsed
- [ ] Pager ownership one-liner ready
- [ ] Unit-cost metric named

### Extra drill

Rehearse explaining Electronic Voting System to a skeptical SDM: start from customer trust, then SLO numbers, then one architecture box that owns the risk, then the kill switch. Mention what you would not build.

### Extra drill

Rehearse a 90-second progressive-scale story for Electronic Voting System: 1× → 10× break → 100× cells → 1,000× specialization.

### Extra drill

Name three wallboard metrics before a peak event and the action each triggers.

### Extra drill

Write the SEV1 one-liner: impact, blast radius, mitigation, next update ETA.

### Extra drill

Defend your consistency choice: what is lost if weakened, and who notices first.

### Extra drill

Cost challenge: cut 30% without violating the top SLO—what do you shed first?

### Extra drill

Security challenge: compromised credential—how do least privilege, fencing, and audit limit damage?

### Extra drill

Multi-tenant challenge: one tenant sends 100×—show fair-share math and protected queues.


*End of document — Electronic Voting System (SDE III)*

