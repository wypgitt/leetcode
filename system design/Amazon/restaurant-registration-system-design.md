# System Design: Restaurant Registration System (Amazon Logistics / Marketplace)

> **Focus areas:** Merchant onboarding · KYC/KYB · Workflow/state machine · Document vault · Compliance · Multi-country · Idempotency · Case management  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Auditability + fail-closed compliance; deal-breaker: “just insert into restaurants table”  
> **Interview theme:** Amazon SDE III / L6 — **Restaurant / merchant registration & onboarding**

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

Goal: design the system that **onboards restaurants** onto Amazon’s food-delivery marketplace—applications, identity/business verification, contracts, banking, menu bootstrap, risk review, go-live—and ongoing re-verification.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Merchant registration & compliance workflow | Live order dispatch (sibling) |
| Core | Cases, docs, checks, approvals | Courier routing |
| Success | Trusted merchants live fast enough | Vanity signup QPS |
| Amazon lens | Customer trust, ownership, mechanisms | Growth-hack skip KYC |
| Boundary | Hands off “Active Restaurant” to catalog/ops | Doesn’t run deliveries |

### 1.1 Functional Requirements

| # | Q | A | Implication |
|---|---|---|-------------|
| F1 | Who applies? | Owner/manager; maybe agency | Identity of applicant vs business |
| F2 | Data? | Legal name, address, tax id, hours, cuisine, contacts | Schema + localization |
| F3 | Docs? | License, identity, bank proof, food safety | Secure vault + OCR assist |
| F4 | Checks? | KYC/KYB, sanctions, fraud, duplicate | Vendor adapters + orchestration |
| F5 | Human review? | Yes for edge/risk | Case management queues |
| F6 | Contracts? | E-sign MSA / market terms | Versioned agreements |
| F7 | Payout setup? | Bank account verify | Tokenized; PSP link |
| F8 | Menu? | Bootstrap upload / POS sync stub | Gate before go-live |
| F9 | Multi-location? | Chains | Hierarchy org→locations |
| F10 | Status UX? | Applicant portal tracking | Transparent states |
| F11 | Re-KYC? | Periodic / trigger-based | Ongoing compliance |
| F12 | Rejection? | Reasons + appeal | Audit + policy |

**MVP:** Single-country: apply → upload docs → automated checks → optional manual review → contract → payout verify → menu minimum → activate location.  
**Out:** Full POS, ads auction, courier onboarding (separate), global shared single compliance engine without packs.

### 1.2 NFRs

| NFR | Target |
|-----|--------|
| Portal UX | Interactive; upload resilient |
| Check latency | Seconds–hours depending on vendor |
| Durability | No lost applications; docs durable |
| Security | PII/PCI-adjacent vault; encryption; access audit |
| Compliance | Fail-closed on sanctions hits |
| Audit | Immutable decision log |
| Scale | Burst city launches; mostly workflow not QPS |

### 1.3 Cases

Happy: apply→auto-approve→sign→bank→menu→LIVE.  
Edges: duplicate restaurant; sanctions hit; fake docs; OCR fail; vendor timeout; partial chain rollout; address mismatch; chargeback-risk owner; appeal; market policy change mid-funnel; applicant abandons.

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Applications/day | 2K | 20K | 200K | 2M |
| Countries | 5 | 20 | 50 | 100+ |
| Docs stored | 10M | 100M | 1B | 10B |
| Jump | Workflow+vault | Country packs | Vendor mesh+auto | Self-serve global platform |

### 1.5 Repeat-back

“Workflowed restaurant onboarding with KYC/KYB, document vault, human cases, contracts, payout verify, activation handoff—compliance fail-closed—not the delivery runtime.”

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Nature |
|-------|--------|
| Portal writes | Low QPS, high sensitivity |
| Doc uploads | MB media; async virus scan |
| Vendor checks | Burst; rate limits |
| Reviewer tools | Internal QPS low |
| Re-KYC batch | Periodic jobs |

### 2.2 Storage

```text
2K apps/day × 5 docs × 2MB ≈ 20GB/day → object store
Metadata DB small vs blobs
Audit events long retention (years)
```

### 2.3 Human capacity

```text
If 20% need manual review × 2K = 400 cases/day
At 15 min → 100 reviewer-hours → staffing model
Automation rate is the scale lever
```

### 2.4 Latency expectations

| Step | Expectation |
|------|-------------|
| Save draft | < 300ms |
| Upload | Resumable |
| Auto checks | < 2 min typical |
| Manual | Hours–days SLA by risk |

### 2.5 Bottlenecks

Vendor rate limits; reviewer backlog; doc malware; duplicate detection at chain scale; country policy sprawl.

---

## 3. High-Level Design

### 3.1 Core abstractions

| Abstraction | Meaning |
|-------------|---------|
| `Organization` | Legal entity / chain |
| `LocationApplication` | Restaurant site being onboarded |
| `Applicant` | User identity |
| `Document` | Vault object + metadata |
| `Check` | Automated verification result |
| `Case` | Human review unit |
| `Agreement` | Signed contract version |
| `PayoutMethod` | Tokenized bank |
| `Activation` | Go-live gate bundle |

### 3.2 State machine (location application)

```text
DRAFT → SUBMITTED → CHECKS_RUNNING → AUTO_PASSED|NEEDS_REVIEW
NEEDS_REVIEW → APPROVED|REJECTED|INFO_REQUESTED
APPROVED → CONTRACT_PENDING → PAYOUT_PENDING → MENU_PENDING → READY
READY → LIVE (activation)
Any non-LIVE → WITHDRAWN
REJECTED → APPEAL (limited)
LIVE → REVERIFICATION → ...
```

### 3.3 Orchestration

Use workflow engine (Step Functions / Temporal-like) for long-running waits, retries, human tasks—not a brittle cron of ifs.

### 3.4 Document vault

- Presigned upload to object store.  
- Virus/malware scan.  
- Encryption KMS; bucket policies.  
- OCR/classify async.  
- Access via short-lived URLs; all access audited.

### 3.5 Check adapters

```text
Sanctions | KYB registry | Address | Duplicate | Risk score | Bank verify
→ normalized CheckResult{status, confidence, evidence_refs, vendor}
```

### 3.6 Trade-offs

| Choice | Why |
|--------|-----|
| Workflow engine | Long-running, durable |
| Fail-closed sanctions | Trust/legal |
| Country compliance packs | Global without spaghetti |
| Human in the loop | Adversarial docs |
| Handoff event to catalog | Clear ownership |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Applicant Portal --> API Gateway --> Application Service
                                      | 
                                      +--> Workflow Orchestrator
                                      |        |
                                      |        +--> Check Workers (vendors)
                                      |        +--> Case Service (reviewers)
                                      |        +--> Agreement/E-sign
                                      |        +--> Payout Verify
                                      |        +--> Menu Bootstrap Gate
                                      v
                               Document Vault (S3+KMS)
                                      |
                               Audit / Decision Log
                                      |
                         Activation Event --> Catalog / Restaurant Master
```

### 4.2 Sequence: happy auto path

```text
Portal -> API: submit
API -> WF: start
WF -> Checks: parallel
Checks -> WF: all PASS
WF -> E-sign: send
Applicant signs
WF -> Bank: verify microdeposits/instant
WF -> Menu: min items present
WF -> Activate: emit LIVE
```

### 4.3 Sequence: manual review

```text
Checks -> RISK/AMBIGUOUS
WF -> Case: create(queue=KYC)
Reviewer -> Case: request_info
Applicant uploads
Reviewer approve -> WF resume
```

### 4.4 Multi-country

Packs configure required docs, vendors, legal entity rules, data residency (vault region), reviewer localization.

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. No LIVE without required checks PASS (or waived with privileged audit).  
2. Sanctions HIT ⇒ cannot activate.  
3. Docs immutable versions; replace = new version.  
4. Decisions append-only.  
5. Idempotent submit / webhook handling.

### 5.2 Scalability

- Low transactional QPS; scale via automation % and reviewer tooling.  
- Shard by `country_id` / `org_id`.  
- Vendor traffic shaping + circuit breakers.  
- Async OCR/check fanout.

### 5.3 Maintainability

- Pack YAML/config for country requirements.  
- Vendor interface stability.  
- Simulation fixtures for workflows.  
- Clear handoff contract to food-delivery runtime.

### 5.4 Duplicate detection

Features: phone, address geocode, tax id, geo proximity + name similarity. Possible matches → case, not silent merge.

### 5.5 Risk & fraud

Synthetic IDs, stolen licenses, mule bank accounts, agency spam. Device signals + velocity + graph links across orgs.

### 5.6 Progressive scale

| Jump | Change |
|------|--------|
| 10× | Better auto-approve; vendor parallelism |
| 100× | Country packs; specialized queues; ML doc assist |
| 1,000× | Global onboarding platform multi-tenant |

### 5.7 Deal-breakers

| Deal-breaker | Why |
|--------------|-----|
| Skip KYC for growth | Trust/legal catastrophe |
| Plaintext docs on app servers | Breach |
| Activate without payout verify | Money SEVs |
| No audit trail | Compliance fail |
| Build full delivery in this hour | Wrong scope |

---

## 6. Wrap-Up

### 6.1 Decisions

Durable workflow; vaulted docs; normalized checks; human cases; country packs; fail-closed sanctions; activation event handoff; append-only decisions.

### 6.2 Risks

Vendor outages stall funnel; reviewer backlog; false duplicate blocks; OCR errors; policy drift; insider access to docs.

### 6.3 45-minute plan

Scope onboarding ≠ delivery → states → HLD vault/workflow → checks/cases → scale/compliance → traps.

### 6.4 Closer

> **Restaurant Registration**: long-running compliance workflow with document vault, KYC/KYB checks, human review, contracts, payout verify, and audited activation—fail-closed, country-packed, handed off to the marketplace runtime.

---

## 7. Deeper / Related Interview Questions

**Q1. Why workflow engine?**  
**A:** Days-long waits, human tasks, retries, visibility.

**Q2. How handle vendor timeout?**  
**A:** Retry/backoff; alternate vendor; escalate case; don’t activate unknown.

**Q3. Waivers?**  
**A:** Privileged role + reason + expiry + audit; never for sanctions HIT.

**Q4. Chain 500 locations?**  
**A:** Org-level KYB once; per-location lighter checks + menu/hours.

**Q5. GDPR delete request?**  
**A:** Legal hold vs delete; minimize; retention schedule.

**Q6. Webhook duplicates?**  
**A:** Idempotency keys on vendor event ids.

**Q7. Who pages activation of sanctioned entity?**  
**A:** Compliance SEV—onboarding + trust.

**Q8. Menu ownership?**  
**A:** Bootstrap gate here; ongoing catalog elsewhere.

**Q9. Agency applicants?**  
**A:** Power of attorney docs; bind to legal owner.

**Q10. Trap: sync monolith script?**  
**A:** Breaks on human latency; use orchestrator.

---

## 8. Appendices

### 8.1 Schema sketches

```text
Org(org_id, legal_name, country, tax_id_hash, status)
LocationApp(app_id, org_id, address, state, risk_score)
Document(doc_id, app_id, type, version, blob_uri, scan_status)
Check(check_id, app_id, type, status, vendor, evidence)
Case(case_id, app_id, queue, assignee, state)
Decision(id, app_id, actor, action, reason, ts)
Agreement(id, org_id, version, signed_at)
PayoutMethod(id, org_id, token_ref, status)
```

### 8.2 Pseudocode: activation gate

```text
function tryActivate(app):
  require state==READY
  require checks.required.all(PASS or WAIVED_AUDITED)
  require not sanctions.HIT
  require agreement.signed
  require payout.verified
  require menu.minimum
  cas(app, READY→LIVE)
  emit RestaurantActivated(app)
  audit(...)
```

### 8.3 Glossary

| Term | Meaning |
|------|---------|
| KYC | Know Your Customer |
| KYB | Know Your Business |
| Pack | Country requirements bundle |
| Case | Human review ticket |
| Vault | Encrypted document store |
| Activation | Transition to LIVE merchant |

### 8.4 Progressive checklist

10× automation; 100× packs+ML assist; 1,000× platform.

### 8.5 Reliability tests

1. Double submit → one workflow.  
2. Sanctions HIT blocks LIVE.  
3. Vendor webhook replay idempotent.  
4. Doc access audited.

### 8.6 60s closer

> Applicants submit through a durable workflow: documents land in a KMS vault, checks run via vendor adapters, risky cases go to reviewers, contracts and payout verification gate activation, and we emit an audited LIVE event to the marketplace—country packs configure differences; sanctions fail closed.

---

## Deep Technical Notes — Restaurant Registration

### Draft autosave

CRDT-ish or last-write field patches; conflict rare (single applicant). Optimistic locking on submit.

### OCR assist

Extract license numbers/dates; never auto-trust—prefill + confidence; low confidence → review.

### Evidence packs

Store vendor raw payloads encrypted; retention by law; support appeals.

### Queue design

Queues by country + risk tier + language; SLA clocks; overflow surge staffing.

### Re-verification triggers

Owner change, bank change, chargeback spike, periodic 6–12 months, sanctions list updates.

### Activation dual-write avoidance

Emit outbox event; catalog consumes; registration remains SoT for compliance state.

### PII minimization

Tax ids hashed/encrypted; display masked; reviewers need break-glass for full.

## Interview Cards — Restaurant Registration

### Card 1: Why not a simple CRUD form?

Compliance is long-running, multi-party, audited.

### Card 2: Sanctions?

Fail-closed; block activation; case to compliance.

### Card 3: Docs security?

Presign, scan, KMS, audited access.

### Card 4: Human review?

Cases with SLAs; request-info loops.

### Card 5: Country packs?

Config for docs/vendors/residency.

### Card 6: Chains?

Org KYB + per-location gates.

### Card 7: Handoff?

`RestaurantActivated` to catalog/runtime.

### Card 8: Deal-breaker?

Skip KYC; plaintext docs; no audit; build delivery runtime here.

## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Onboarding ≠ delivery |
| 5–12 | States + volumes |
| 12–22 | HLD vault/workflow |
| 22–35 | Checks, cases, activate |
| 35–45 | Packs, fraud, traps |

## 10. Operability

### Golden signals

Submit→LIVE conversion, time-in-state, check fail rates, case backlog/SLA, vendor errors, activation failures, doc scan malware hits.

### Rollback ladder

Pause activations → revert pack config → force manual for segment → disable vendor → postmortem.

### Kill switches

Freeze LIVE transitions; disable auto-approve; pause country; reject new submits soft-close.

### Security/privacy

Vault IAM; DLP; reviewer training; access reviews; encryption; retention.

### Cost worksheet

```text
Vendor checks $ + reviewer hours + storage
Lever: auto-approve precision/recall; reduce rework INFO_REQUESTED
```

### Cross-team deps

Identity, Fraud/Compliance, E-sign, PSP/Bank, Catalog, Food runtime, Support, Legal.

---

## More Interview Q&A — Restaurant Registration

**Q1. Microdeposits slow?**  
**A:** Instant verification vendors; parallelize; communicate SLA.

**Q2. Fake food license?**  
**A:** Vendor auth + visual forensics + reviewer; risk score.

**Q3. Multi-brand same kitchen?**  
**A:** Policy; link locations; detect virtual brands.

**Q4. Applicant vs beneficial owner?**  
**A:** Collect UBO where required by pack.

**Q5. Partial approve chain?**  
**A:** Location-level LIVE independently.

**Q6. Contract version change?**  
**A:** Re-sign gate for material changes; grandfathering rules Legal-owned.

**Q7. Data residency?**  
**A:** Vault region pinned by pack; metadata may be regional cell.

**Q8. SLA for onboarding?**  
**A:** Product metric; risk tiers different clocks.

**Q9. Integration test strategy?**  
**A:** Vendor sandboxes + recorded fixtures; workflow sim.

**Q10. Why hash tax id?**  
**A:** Minimize exposure; equality match via blind index carefully.

**Q11. Chargeback after LIVE?**  
**A:** Risk triggers re-verification / suspend.

**Q12. Support changing address?**  
**A:** Material change → rechecks.

**Q13. Can ML auto-approve 95%?**  
**A:** Goal; holdout audits; never sanctions.

**Q14. Agency spam applications?**  
**A:** Velocity limits; bond; quality scoring.

**Q15. Difference vs global food delivery doc?**  
**A:** This onboards; that operates orders.

**Q16. First invariant test?**  
**A:** Cannot LIVE on sanctions HIT.

---

## Deep Technical Addenda

### Idempotent webhooks

```text
key = vendor + event_id
if seen(key): return 200
process; store seen; 200
```

### Info-request loops

Cap rounds (e.g., 3); then reject or escalate; prevent infinite limbo.

### Blind duplicate index

Encrypt/HMAC normalized address+phone; probabilistic match → case.

### Break-glass access

Reviewer full-doc view requires reason code; SIEM alert.

### Activation outbox

```text
txn: state=LIVE + outbox_event
publisher: at-least-once to catalog
catalog: idempotent upsert
```

## Tradeoff Matrices — Restaurant Registration

### Auto vs manual

| Choice | Speed | Risk | Use |
|--------|-------|------|-----|
| All manual | Slow | Low miss | Tiny markets |
| Tiered auto | Fast | Managed | **Default** |
| All auto | Fastest | High | Unacceptable |

### Vendor count

| Choice | Resilience | Cost/complexity |
|--------|------------|-----------------|
| Single | Fragile | Simple |
| Primary+failover | Good | **Prefer** |
| Many parallel | Best signal | Expensive |

### Org vs location verification depth

| Entity | Depth |
|--------|-------|
| Org | Full KYB |
| Location | Address/license/menu/hours |

## Operability Addenda

### Deploy pipeline

```text
pack/workflow change → policy review → shadow decisions → canary country → bake
```

### Guardrails

- LIVE with open sanctions = 0  
- Case SLA breach  
- Vendor error spike  
- Auto-approve complaint rate  
- Doc malware detections  

### Kill switches

1. Freeze activations  
2. Disable auto-approve  
3. Pause country pack  
4. Force all to review  
5. Soft-close submits  

## Worked Capacity Narrative

Apps/day × manual % × minutes → reviewer FTE; show automation from 20%→5% manual bends hiring curve; vendors rate limits need shaping at 100×; packs prevent code explosion.

## Customer-Trust Paragraph

Onboarding a fraudulent or unsafe restaurant endangers customers. Fail-closed sanctions and food-safety docs are not optional growth levers. Auditable decisions protect customers and Amazon when regulators ask “why was this live?”

## Progressive Scale Recap

- **10×:** automation + parallel checks  
- **100×:** country packs + ML assist + queue specialization  
- **1,000×:** global merchant onboarding platform  

---

## Supplemental Depth Pack — Restaurant Registration

### S1. Fail-closed sanctions

HIT blocks LIVE.
**Metric:** `live_with_sanctions`.

### S2. Append-only decisions

No silent overwrite.
**Metric:** audit gaps.

### S3. Doc versions

Immutable blobs.
**Metric:** `doc_overwrite_attempts`.

### S4. Workflow durability

Survive process death.
**Metric:** stuck workflows.

### S5. Idempotent webhooks

Replay safe.
**Metric:** duplicate process rate.

### S6. Activation outbox

No dual-write loss.
**Metric:** `live_without_catalog`.

### S7. Pack correctness

Required docs enforced.
**Metric:** `missing_required_doc_live`.

### S8. Unit economics

Cost per LIVE merchant.
**Metric:** `$ / activated_location`.

## Scenario Runbooks

| Scenario | Action |
|----------|--------|
| Vendor down | Failover; extend SLA messaging |
| Malware in upload | Quarantine; block; alert security |
| Reviewer backlog | Raise auto threshold carefully; surge staff |
| Policy change | Snapshot in-flight; dual-run pack versions |
| Fraud ring | Graph block; freeze segment |
| Bad activation | Suspend LIVE; reverse catalog; incident |

## Rapid-Fire Q&A — Restaurant Registration

**Q:** Scope? **A:** Onboarding/compliance.  
**Q:** Not? **A:** Dispatch/orders.  
**Q:** Engine? **A:** Durable workflow.  
**Q:** Docs? **A:** Vault+KMS.  
**Q:** Sanctions? **A:** Fail-closed.  
**Q:** Review? **A:** Cases.  
**Q:** Packs? **A:** Per country.  
**Q:** Activate? **A:** Gated emit.  
**Q:** Chain? **A:** Org+locations.  
**Q:** Duplicate? **A:** Case matches.  
**Q:** Webhook? **A:** Idempotent.  
**Q:** Waiver? **A:** Audited rare.  
**Q:** Menu? **A:** Min gate.  
**Q:** Payout? **A:** Verify before LIVE.  
**Q:** Re-KYC? **A:** Triggers+periodic.  
**Q:** OCR? **A:** Assist not trust.  
**Q:** GDPR? **A:** Retention/legal.  
**Q:** Agency? **A:** POA docs.  
**Q:** Deal-breaker? **A:** Skip KYC.  
**Q:** 10×? **A:** Automate.  
**Q:** 100×? **A:** Packs.  
**Q:** Metric? **A:** Time-to-LIVE + trust.  
**Q:** Outbox? **A:** Yes.  
**Q:** Blind index? **A:** Careful.  
**Q:** Break-glass? **A:** Reason+SIEM.  
**Q:** Info loops? **A:** Capped.  
**Q:** Virtual brands? **A:** Policy link.  
**Q:** UBO? **A:** Pack-required.  
**Q:** Contract rev? **A:** Re-sign rules.  
**Q:** Residency? **A:** Vault region.  
**Q:** Malware? **A:** Scan gate.  
**Q:** Auto 95%? **A:** With audits.  
**Q:** Ownership? **A:** Onboarding oncall.  
**Q:** Suspend? **A:** Risk trigger.  
**Q:** Address change? **A:** Recheck.  
**Q:** Cost lever? **A:** Auto-approve quality.  
**Q:** Shadow pack? **A:** Yes.  
**Q:** FIRST test? **A:** Sanctions block.  
**Q:** Plaintext? **A:** Never.  
**Q:** Cron-only? **A:** Insufficient.  
**Q:** Delivery runtime? **A:** Sibling handoff.  
**Q:** Applicant UX? **A:** State transparency.  
**Q:** Appeal? **A:** Limited path.  
**Q:** Vendor mesh? **A:** At scale.  
**Q:** Graph fraud? **A:** Link orgs.  
**Q:** Activation CAS? **A:** Yes.

## Narrative Walkthrough — Restaurant Registration

### Beat 1

Separate onboarding from delivery runtime; list compliance gates.

### Beat 2

Volumes: not QPS problem—automation & reviewers.

### Beat 3

Draw portal, workflow, vault, checks, cases, activate.

### Beat 4

State machine on board; sanctions invariant.

### Beat 5

Manual case + info-request loop.

### Beat 6

Country packs; chains org/location.

### Beat 7

Security vault; outbox activation; progressive scale.

### Beat 8

Close: trust fail-closed + handoff event + deal-breakers.

## Pre-Onsite Checklist — Restaurant Registration

- [ ] Scope boundary vs food delivery  
- [ ] State machine  
- [ ] Vault properties  
- [ ] Sanctions invariant  
- [ ] Country packs  
- [ ] Activation gates list  
- [ ] Deal-breakers  
- [ ] 60s closer  

### Extra drill

Draw states in 60s.

### Extra drill

List activation gates.

### Extra drill

Webhook idempotency snippet.

### Extra drill

Vault access audit story.

### Extra drill

Duplicate detection features.

### Extra drill

Chain onboarding split.

### Extra drill

Pack contents list.

### Extra drill

Reviewer queue SLAs.

### Extra drill

Re-KYC triggers.

### Extra drill

Outbox activation.

### Extra drill

Waiver policy.

### Extra drill

OCR confidence handling.

### Extra drill

Malware quarantine.

### Extra drill

GDPR vs audit retention tension.

### Extra drill

Vendor failover.

### Extra drill

Auto-approve metrics (precision/recall).

### Extra drill

Info-request cap.

### Extra drill

Break-glass SIEM.

### Extra drill

Suspend LIVE flow.

### Extra drill

Contract version migration.

### Extra drill

UBO collection.

### Extra drill

Agency POA.

### Extra drill

Cost per activation math.

### Extra drill

Shadow pack decisions.

### Extra drill

Kill switches.

### Extra drill

Interview trap: skip KYC.

### Extra drill

60s closer memorization.

### Extra drill

First unit test name.

### Extra drill

Ownership SEV sanctions.

### Extra drill

Menu gate vs catalog ownership.

### Extra drill

Blind index caveats.

### Extra drill

1000× platform vision.

### Extra drill

Compare to courier onboarding.

### Extra drill

Fraud ring response.

---

*End of restaurant registration system design.*
