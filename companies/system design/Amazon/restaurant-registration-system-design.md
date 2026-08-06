# System Design: Restaurant Registration System

> **Focus areas:** Onboarding · Identity & verification · Menu ingestion · Compliance · Banking/payout setup · Geospatial discovery hooks · Amazon / marketplace seller-style rigor for restaurants  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, explicit state machines, compliance gates, Amazon ownership & customer (diner + restaurant) obsession

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

Goal: **bound restaurant onboarding**—take a restaurant from “interested” to “live on the food-delivery marketplace” with verified legal identity, compliant operations, accurate menus, payout readiness, and **geo discovery hooks** so diners can find them—without letting fraud or unsafe actors go live.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who registers? | Owner / manager; maybe chain HQ for multi-outlet | Account + outlet hierarchy |
| F2 | What is registered? | Business entity + one or more outlets (locations) | Separate `Merchant` vs `Outlet` |
| F3 | Verification? | KYB (know your business): legal name, tax id, address proof, ownership | KYB vendor + manual review queue |
| F4 | Compliance? | Food permits, alcohol license, sanitation, local regs | Geo policy checklist |
| F5 | Menus? | Items, modifiers, hours, photos, categories, 86 | Menu service; versioning |
| F6 | Banking? | Payout account (bank / wallet); tax forms | Payments-onboarding; tokenization |
| F7 | Discovery hooks? | Geo point, service radius, cuisine tags, hours → search index | Event to discovery/search |
| F8 | Contract / commercial? | Commission tier, fees, contract accept | Commercial profile |
| F9 | Devices? | Tablet app / POS integration | Device enlistment |
| F10 | SLA to go live? | Days not months; some same-week | Async pipelines + clear blockers |
| F11 | Multi-geo? | Country-specific docs & regs | Policy engine per geo |
| F12 | Updates after live? | Menu edits continuous; re-verify on sensitive changes | Change-risk tiers |
| F13 | Rejection / suspend? | Fraud, bad hygiene, repeated cancellations | State machine + appeals |
| F14 | Idempotency? | Form retries, webhook dupes | Keys on applications |
| F15 | Ops tools? | Reviewer console, document viewer, audit | Human-in-loop |

**MVP functional scope:**

1. Merchant signup + outlet application form.  
2. Document upload (permit, ID, bank).  
3. Automated KYB checks via vendor + rules.  
4. Manual review queue for edge / high-risk.  
5. Menu bootstrap (CSV/UI) with validation.  
6. Hours + geo pin + delivery radius.  
7. Payout method verify (micro-deposit / PSP).  
8. Compliance checklist per city.  
9. Go-live gate: all required checks GREEN → publish to discovery.  
10. Post-live menu update APIs; suspend/revoke.  

**Out of MVP:**

- Full POS bi-directional sync for all vendors  
- Automatic government permit API in every country  
- Perfect fraud ML from day one (start rules + vendor)  
- White-glove chain tooling for 10k outlets (Phase 2)  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Application submit latency | Interactive | p99 < 500ms (excl. uploads) |
| N2 | Document upload | Large images/PDFs | Direct-to-object-store; virus scan |
| N3 | Time-to-decision | Business KPI | p50 < 24h automated; manual p50 < 72h |
| N4 | Durability | Applications never lost | Durable store before ACK |
| N5 | Security | PII/KYC docs highly sensitive | Encryption; strict authz; retention |
| N6 | Auditability | Regulators / disputes | Immutable audit log |
| N7 | Availability | Onboarding degradable | Separate from order path |
| N8 | Scale | See table | Shard by geo |
| N9 | Consistency | Go-live atomic vs discovery | Outbox → search index |
| N10 | Correctness | Don’t go live without payout+permit | Hard gates |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Owner applies → uploads docs → KYB auto-approve → menu imported → bank verified → compliance GREEN → LIVE → appears in search within radius.  
2. Chain HQ creates 20 outlets → shared KYB entity → per-outlet permits/menus.  
3. Reviewer requests resubmit of blurry permit → owner uploads → approve.  
4. Live restaurant updates menu item price → version++ → search/pricing consumers notified.  
5. Alcohol SKU added → extra license check → blocked until compliance OK.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Duplicate applications same tax id | Dedupe / merge flow |
| Stolen identity docs | Vendor risk signal → manual / reject |
| Bank account mismatch name | Fail verification; support path |
| Permit expired | Block go-live or auto-suspend near expiry |
| Geo pin in lake / wrong place | Map validation; reviewer |
| Menu with $0 / huge prices | Validation rules |
| Webhook from KYB delayed | Async state; timeout SLA |
| Partial outbox to search | Retry; outlet not discoverable until indexed OK |
| Owner loses device | Account recovery; re-bind tablet |
| Sanctions hit on UBOs | Hard stop |
| Multi-country tax id formats | Geo validators |
| Thundering herd new city launch | Queue scale; prioritize |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Countries | 5 | 15 | 40 | 80+ |
| Cities | 100 | 1K | 10K | 50K |
| Merchants | 80K | 800K | 8M | 40M |
| Outlets | 100K | 1M | 10M | 50M |
| Applications submitted / day | 2K | 20K | 200K | 2M |
| Peak **application API QPS** | 50 | 500 | 5K | 50K |
| Peak **doc uploads**/s | 20 | 200 | 2K | 20K |
| Menu updates / day | 1M | 10M | 100M | 1B |
| Peak **menu write QPS** | 100 | 1K | 10K | 100K |
| Reviewers (human) | 200 | 1K | 5K | 20K |
| Discovery publishes / day | 5K | 50K | 500K | 5M |

**What each jump forces:**

- **10×:** Doc object store + async scan; KYB webhook workers; menu service split.  
- **100×:** Geo policy engine; reviewer workforce tooling; outbox/CDC to search; chain hierarchy.  
- **1,000×:** Highly automated KYB; risk ML; self-serve compliance renewals; sharded merchant cells; near-real-time discovery materialization.

### 1.5 Etc.

- Food-delivery order/match systems exist downstream (sibling design).  
- PSP/KYB vendors for identity & bank verify.  
- Amazon flavor: high bar on trust & safety; clear ownership of go-live gates; operational excellence on review SLAs.

**Scope statement:**

> Design a global restaurant registration & onboarding platform: merchant/outlet applications, KYB & compliance gates, menu bootstrap, payout verification, and geospatial discovery publish—baseline ~100K outlets / ~2K applications/day scaling through 10× / 100× / 1,000×.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | Baseline | 1,000× | Notes |
|-------|----------|--------|-------|
| Application writes | 50/s peak | 50K/s | Strong-ish |
| Doc uploads | 20/s | 20K/s | Bandwidth |
| KYB webhooks | 20/s | 20K/s | Idempotent |
| Reviewer actions | 10/s | 5K/s | Humans |
| Menu writes | 100/s | 100K/s | Hot after live |
| Discovery publish | 5/s | 5K/s | Outbox |
| Read status APIs | 200/s | 200K/s | Cacheable |

**Anti-pattern:** treating menu QPS as onboarding QPS—post-live menu dwarfs registration.

### 2.2 Document storage

```text
Avg application 5 docs × 3 MB = 15 MB
2K apps/day × 15 MB = 30 GB/day
1,000×: 2M × 15 MB = 30 PB/day would be wrong if all new—but many are retries

Steady new: 2M/day × 15 MB = 30 PB? 2e6×15e6=3e13 B = **30 TB/day** — huge
→ compression, size limits (e.g. 10 MB/doc), retention, dedupe, virus scan
Enforce max sizes; lifecycle to cold storage / delete after retention
```

**Unit check:** 2e6 apps × 15 MB = 3e13 B = **30 TB/day** at 1000× if naïve—must limit.

### 2.3 Menu storage

```text
100K outlets × 150 items × 500 B ≈ 7.5 GB
50M outlets × 150 × 500 B ≈ 3.75 PB → normalize, geo cells, don’t copy worldwide
```

### 2.4 Reviewer capacity

```text
If 30% apps need human review, 2K × 0.3 = 600/day
200 reviewers → easy
At 200K apps/day × 0.3 = 60K reviews/day → need automation to drop manual rate to ~2–5%
```

### 2.5 Discovery publish

```text
Go-live + material changes → index update
Doc size ~2 KB
5K/day trivial; 5M/day ≈ 58/s average — fine with Kafka→search
```

---

## 3. High-Level Design

### 3.1 Entities

| Entity | Description |
|--------|-------------|
| MerchantAccount | Login, owners, contacts |
| BusinessEntity | Legal KYB subject |
| Outlet | Physical location / brand unit |
| Application | Onboarding case for outlet/entity |
| Document | Uploaded proof with scan status |
| ComplianceCheck | Typed gate result |
| Menu / Item | Catalog for outlet |
| PayoutMethod | Tokenized bank |
| DiscoveryProfile | Geo + tags + hours projection |
| ReviewTask | Human work item |
| AuditEvent | Immutable log |

### 3.2 Services

| Service | Role |
|---------|------|
| Registration API / BFF | Forms |
| Application Service | Case state machine |
| Document Service | Upload URLs, virus scan, OCR metadata |
| KYB Adapter | Vendor integration |
| Compliance Engine | Geo checklist |
| Menu Onboarding | Bootstrap + validate |
| Payout Onboarding | Bank verify |
| Risk / Fraud | Scores |
| Review Workbench | Human tasks |
| Go-Live Orchestrator | Gate aggregation |
| Discovery Publisher | Outbox to search/geo |
| Notification | Email/SMS to owner |
| Policy Config | Per-geo requirements |
| Identity / Auth | Roles |

### 3.3 Application state machine

```text
DRAFT → SUBMITTED → AUTO_REVIEW → (MANUAL_REVIEW |)
  → ACTION_REQUIRED ↔ resubmit
  → APPROVED_PENDING_SETUP → SETUP_IN_PROGRESS
  → READY_FOR_LIVE → LIVE
  → REJECTED | SUSPENDED | CLOSED

LIVE → SUSPENDED → LIVE (reinstate)
Sensitive change → REVERIFICATION → …
```

### 3.4 Go-live gates (hard)

```text
LIVE iff:
  KYB == PASSED
  AND required permits == PASSED (and not expired)
  AND payout == VERIFIED
  AND menu == MIN_VALID
  AND geo == VALID
  AND contract == ACCEPTED
  AND risk == BELOW_THRESHOLD
  AND device/POS == OPTIONAL_OR_BOUND (policy)
```

### 3.5 Progressive architecture

| Scale | Shape |
|-------|-------|
| 1× | Modular services; Postgres; S3; one KYB vendor |
| 10× | Kafka outbox; async workers; menu service |
| 100× | Geo policy; review workforce platform; CDC search |
| 1000× | Merchant cells; ML risk; automated renewals |

---

## 4. Architecture Diagram

### 4.1 Logical

```text
 Owner App / Web
        │
        ▼
 ┌─────────────┐     presigned PUT      ┌──────────────┐
 │ Registration│───────────────────────►│ Object Store │
 │     BFF     │                        │ + AV scan    │
 └──────┬──────┘                        └──────┬───────┘
        │                                      │
        ▼                                      ▼
 ┌─────────────┐                        ┌──────────────┐
 │ Application │◄──── webhooks ─────────│ KYB / PSP    │
 │   Service   │                        │   Vendors    │
 └──────┬──────┘                        └──────────────┘
        │
        ├────────► Compliance Engine
        ├────────► Menu Onboarding
        ├────────► Payout Onboarding
        ├────────► Risk Engine
        │
        ▼
 ┌─────────────┐     tasks      ┌──────────────┐
 │  Go-Live    │───────────────►│ Review Desk  │
 │ Orchestrator│◄───────────────│  Workbench   │
 └──────┬──────┘                └──────────────┘
        │ outbox
        ▼
 ┌─────────────┐      ┌──────────────┐
 │  Discovery  │─────►│ Search / Geo │
 │  Publisher  │      │    Index     │
 └─────────────┘      └──────────────┘
```

### 4.2 Merchant vs outlet

```text
MerchantAccount
   └── BusinessEntity (KYB)
         ├── Outlet A (permit, menu, geo) → Discovery A
         ├── Outlet B ...
         └── Outlet C ...
```

### 4.3 Outbox to discovery

```text
Txn: mark outlet LIVE + write OutboxEvent
Worker: publish DiscoveryProfile upsert
Search: index geo + hours + cuisine + rating_placeholder
Failure: retry with backoff; outlet flag discoverable=false until ack
```

### 4.4 Document pipeline

```text
presigned upload → S3
 → ObjectCreated event
 → AV scan
 → OCR / classify (permit type)
 → attach to Application
 → trigger compliance eval
```

---

## 5. Design Deep Dive

### 5.1 Why registration is a platform

Naïve “User form + admin approve” fails globally: docs differ by country, fraud is real, menus are large, discovery must stay correct, and payouts are money. Treat it like **Amazon Selling Partner onboarding** for restaurants.

### 5.2 Policy engine (geo)

```text
policy(city_id) = {
  required_docs: [...],
  kyb_level: STANDARD|ENHANCED,
  alcohol: rules,
  data_residency: region,
  contract_template_id: ...,
  min_menu_items: 5,
  payout_methods: [...]
}
```

Evaluate checklist continuously as artifacts arrive—not only at submit.

### 5.3 KYB / verification

Stages:

1. Data validation (tax id checksum formats)  
2. Vendor identity verification  
3. Watchlist / sanctions  
4. Address corroboration  
5. Risk score → auto approve / manual / reject  

Idempotent webhook:

```text
vendor_event_id unique → apply status transition CAS
```

### 5.4 Document security

- Presigned upload with content-type & size limits  
- Server-side encryption (KMS)  
- Virus scan before reviewers can download  
- Short-lived signed download URLs  
- Retention: delete after N years / legal hold  
- Field-level encrypt tax ids  

### 5.5 Menu onboarding

Bootstrap paths: UI, CSV, POS pull, photo→OCR (Phase 2).

Validation:

```text
price > 0, currency match, categories non-empty,
hours parseable, modifiers reference valid items,
allergens optional but schema-ready
```

Publish menu versions; discovery may only need categories/price_band not full items.

### 5.6 Geospatial discovery hooks

On go-live / change:

```text
DiscoveryProfile {
  outlet_id, lat, lng, h3,
  service_radius_m,
  hours, cuisine_tags[],
  price_band, status=LIVE,
  prep_time_p50_init,
  ranking_features_bootstrap
}
```

Indexed for:

- `geo distance` queries  
- filter open-now  
- cuisine facets  

**Validation:** pin within city polygon; not in water; radius caps by city.

### 5.7 Payout onboarding

- Collect bank via PSP hosted fields (reduce PCI)  
- Micro-deposit or instant verify  
- Name match against KYB legal entity  
- Tax form (W-9/W-8/local) storage  

No LIVE without VERIFIED payout (hard gate).

### 5.8 Human review workbench

```text
Task {application_id, reason_codes[], priority, sla_due, assignee}
```

Features: doc viewer, map pin, risk signals, decision + reason, audit.

Workforce routing: skill by country/language; unfairness metrics.

### 5.9 Go-live orchestrator

Aggregates gate statuses (like a build pipeline):

```text
gates = {kyb, permits, payout, menu, geo, contract, risk}
READY_FOR_LIVE when all GREEN
GoLive() → CAS state LIVE + outbox
```

Compensations if discovery publish fails: keep LIVE_INTERNAL / DISCOVERABLE=false or rollback per policy—prefer **LIVE but not discoverable** over silent index loss.

### 5.10 Change management after LIVE

| Change | Risk | Action |
|--------|------|--------|
| Item price | Low | Auto |
| Hours | Low–med | Auto + discovery |
| Geo move | High | Re-verify / temporary demote |
| Ownership transfer | High | Full KYB |
| New alcohol category | High | Compliance gate |
| Bank change | High | Re-verify payout |

### 5.11 Fraud patterns

- Synthetic restaurants (no real kitchen)  
- Stolen docs  
- Bust-out fraud on promos  
- Duplicate outlets farming ranking  
- Menu phishing (trademark abuse)  

Signals: geo density anomalies, doc forensics, velocity, shared devices, chargeback history after live.

### 5.12 Eventing & integration

```text
ApplicationSubmitted
DocumentScanned
KybDecision
ComplianceUpdated
MenuBootstrapped
PayoutVerified
OutletLive
OutletSuspended
DiscoveryUpserted
```

Downstream: search, sales tax, account management, device fleet.

### 5.13 Storage design

```text
Postgres/Aurora (geo cell):
  merchants, entities, outlets, applications, checks, review_tasks

S3:
  raw docs (private)

Dynamo (optional hot):
  application_status projection for mobile

OpenSearch/Elastic:
  discovery profiles

Kafka:
  outbox & webhooks
```

### 5.14 Consistency

- Application transitions with `version` CAS  
- Outbox pattern for discovery  
- Menu version monotonic per outlet  
- Webhook idempotency keys  

### 5.15 Multi-region

- Merchant home region by country of business  
- Docs never leave residency region  
- Global brand directory optional read-only  

### 5.16 Observability

| Metric | Why |
|--------|-----|
| Time SUBMITTED→LIVE | Funnel |
| Auto-approve rate | Automation |
| Manual SLA breach | Staffing |
| Doc virus positives | Security |
| Discovery lag p99 | CX |
| Suspend rate post-live 30d | Quality of gates |
| Menu validation fail rate | UX |

### 5.17 Failure modes

| Failure | Mode |
|---------|------|
| KYB vendor down | Queue; extend SLA; don’t auto-approve blindly |
| AV scanner down | Block reviewer download; pause approve |
| Search down | Buffer outbox; discoverable=false |
| OCR wrong | Human fallback |

### 5.18 10× / 100× / 1,000×

**10×:** S3+AV; webhook workers; menu split.  
**100×:** Policy-as-data; review platform; CDC; chain APIs.  
**1000×:** Auto KYB majority; ML risk; self-serve renewals; merchant cell sharding; streaming discovery.

### 5.19 Amazon LP

- **Highest standards:** don’t trade fraud for growth quietly  
- **Ownership:** go-live orchestrator owns gate aggregation  
- **Earn trust:** restaurants see clear blockers  
- **Dive deep:** spikes in suspends after a city launch  

### 5.20 API sketch highlights

```text
POST /merchants
POST /outlets/{id}/applications
POST /applications/{id}/documents:presign
POST /applications/{id}/submit
GET  /applications/{id}/gates
POST /outlets/{id}/menus:import
POST /outlets/{id}/payout-methods
POST /outlets/{id}/go-live
POST /review/tasks/{id}/decision
```

---

## 6. Wrap-Up

### 6.1 Summary

A **gated onboarding platform** turning restaurants into trusted, discoverable, payable marketplace sellers via KYB, compliance, menu, payout, and geo publish—with human review when automation is unsure—and scaling by geo policy + automation.

### 6.2 Tradeoffs

| Tradeoff | Choice |
|----------|--------|
| Growth vs trust | Hard gates; automate speed |
| Manual vs auto KYB | Auto-first + manual tail |
| Monolith menu vs service | Separate menu early |
| Sync search vs outbox | Outbox |
| Global DB vs residency cells | Geo home |

### 6.3 Risks

Doc retention cost; vendor outages; false reject good restaurants; discovery lag; ownership transfer fraud.

---

## 7. Deeper / Related Interview Questions

### 7.1 Framing

**Q: Why not just a Google Form + spreadsheet?**  
A: Scale, audit, PII, payments, geo discovery, multi-geo regs.

**Q: Merchant vs outlet?**  
A: Legal entity vs physical selling location—different lifecycles.

**Q: Is this part of the order path?**  
A: No—separate control plane; orders require LIVE outlets.

**Q: Amazon analogy?**  
A: Selling Partner / vendor onboarding with food-specific permits.

**Q: Success metric?**  
A: Time-to-live, auto-approve quality, post-live incident rate, discovery correctness.

### 7.2 State machines

**Q: Why CAS version?**  
A: Concurrent reviewer + webhook races.

**Q: ACTION_REQUIRED loop?**  
A: Request specific docs; don’t reset entire KYB blindly.

**Q: Can LIVE skip payout?**  
A: No—hard gate (unless offline cash geo—document exception).

**Q: Suspend vs reject?**  
A: Reject before live; suspend after.

**Q: Idempotent submit?**  
A: Idempotency-Key; same application id.

### 7.3 KYB & compliance

**Q: Vendor as source of truth?**  
A: Vendor decision + our policy interpretation; we own go-live.

**Q: Expired permit?**  
A: Cron revalidation; grace vs hard suspend by geo.

**Q: Alcohol?**  
A: Separate license; item category gate.

**Q: Sanctions false positive?**  
A: Manual review path; appeals.

**Q: Multi-owner UBOs?**  
A: Collect % ownership; verify thresholds.

### 7.4 Documents

**Q: Why presigned S3?**  
A: Avoid app server bandwidth; direct upload.

**Q: Virus in PDF?**  
A: AV before processing/review.

**Q: OCR confidence low?**  
A: Manual; don’t auto-fail necessarily.

**Q: Max size?**  
A: Enforce (e.g. 10–15 MB); prevent 30 TB/day blowups.

**Q: Retention?**  
A: Legal hold vs delete; documented policy.

### 7.5 Menus

**Q: CSV injection?**  
A: Validate/sanitize; schema.

**Q: Huge menu 10k items?**  
A: Batch import; async validation; pagination.

**Q: Photos hotlink abuse?**  
A: Re-host / CDN; malware scan images.

**Q: Price currency mismatch?**  
A: Reject; outlet currency locked.

**Q: Discovery need full menu?**  
A: No—profile facets; menu service for detail.

### 7.6 Geo discovery

**Q: Wrong pin ranking exploit?**  
A: Validate polygon; distance-to-address proof; anomaly.

**Q: Service radius huge?**  
A: Cap by city; courier reality.

**Q: Open-now correctness?**  
A: Hours TZ at outlet; index refresh.

**Q: Outbox fail?**  
A: Retry; discoverable flag; alert lag SLO.

**Q: H3 vs geohash?**  
A: Either; be consistent with delivery stack.

### 7.7 Payouts

**Q: PCI scope?**  
A: Hosted fields / tokens; minimize.

**Q: Name mismatch?**  
A: Fail verify; support with docs.

**Q: Change bank after live?**  
A: Re-verify; freeze payouts meantime.

**Q: Split payouts multi-party?**  
A: Defer; single legal entity MVP.

### 7.8 Review ops

**Q: SLA breach?**  
A: Priority queues; surge staffers; auto-extend applicant messaging.

**Q: Reviewer fraud?**  
A: Dual control on high-risk; audit; anomaly.

**Q: Language?**  
A: Route by locale skill.

**Q: Calibration?**  
A: Gold tasks; quality sampling.

### 7.9 Fraud

**Q: Fake restaurant?**  
A: Address intel, device, velocity, post-live order quality feedback loop.

**Q: Trademark menu theft?**  
A: Brand reports; content ops.

**Q: Duplicate tax id?**  
A: Dedupe; investigate.

**Q: Promo abuse newly live?**  
A: Probation limits; risk score.

### 7.10 Scale

**Q: 50K QPS application API?**  
A: Rare; mostly reads—cache status; shard writes by merchant/geo.

**Q: 1B menu updates/day?**  
A: That’s live catalog, not registration—design menu path separately.

**Q: 30 TB/day docs?**  
A: Limit sizes; retention; dedupe; not forever hot.

**Q: Global single Postgres?**  
A: No—geo residency cells.

### 7.11 Consistency & events

**Q: Dual write DB + search?**  
A: Outbox/CDC—no dual write without pattern.

**Q: Webhook before DB visible?**  
A: Idempotent applicator; ordered per application key.

**Q: Exactly-once go-live?**  
A: CAS to LIVE once; outbox at-least-once with upsert.

### 7.12 Security & privacy

**Q: Who can see passport scans?**  
A: Need-to-know reviewers; just-in-time access; audit.

**Q: Encrypt tax id?**  
A: Yes; tokenize/display masked.

**Q: GDPR delete?**  
A: Workflow; retain legal minimum; remove discovery.

### 7.13 Reliability

**Q: KYB outage during launch?**  
A: Queue; communicate; optional limited staging storefront? Prefer wait.

**Q: Search index corruption?**  
A: Rebuild from source outlets LIVE; reconciler.

**Q: Partial gate GREEN flicker?**  
A: Orchestrator snapshots; don’t live on transient.

### 7.14 Comparisons

**Q: vs Uber Eats onboarding?**  
A: Same domain; Amazon emphasizes audit/gates/ownership clarity.

**Q: vs Amazon Seller Central?**  
A: Very similar KYB/payout; food adds permits & menus & geo hours.

**Q: vs plain CRUD users?**  
A: Money + regulated docs + discovery side effects.

### 7.15 Product edges

**Q: Ghost kitchen?**  
A: Allowed with disclosure policy; address still verified.

**Q: Shared kitchen multiple brands?**  
A: Multiple outlets / brands mapped to facility; policy.

**Q: Franchisee vs franchisor?**  
A: Entity hierarchy; contracts.

**Q: Temporary pop-up?**  
A: Short-lived outlet with end date; auto delist.

### 7.16 Observability drills

**Q: Time-to-live doubled?**  
A: Vendor latency, manual backlog, menu validation failures, payout verify.

**Q: Spike in rejects?**  
A: Policy change, fraud ring, OCR bug.

**Q: Live but not searchable?**  
A: Outbox lag, index reject, geo validation, status flag.

### 7.17 Org / ownership

**Q: Who pages discovery lag?**  
A: Publisher/search platform; registration owns outbox production.

**Q: Who owns false approve fraud?**  
A: Risk + registration gates; dive deep jointly.

### 7.18 Arithmetic traps

**Q: 2M apps × 15 MB?**  
A: 30 TB/day—limit docs.

**Q: 50M × 150 × 500 B menus?**  
A: ~3.75 PB if naïve global copy—shard/normalize.

**Q: Manual review at 30% of 200K/day?**  
A: 60K/day—automation mandatory.

### 7.19 APIs & UX

**Q: Show blockers clearly?**  
A: Gate API with reason codes & fix links—customer obsession for restaurants.

**Q: Mobile upload flaky?**  
A: Chunk/resume; idempotent doc ids.

### 7.20 Closing

**Q: One-week city launch readiness?**  
A: Policy pack for city, reviewer staffing, KYB vendor capacity, menu importer hardening, discovery reconciler—not a new blockchain KYC.

---

## 8. Appendices

### 8.1 Schemas

```text
merchants(merchant_id, auth_principal, created_at)
business_entities(entity_id, merchant_id, legal_name, tax_id_enc, country, kyb_status)
outlets(outlet_id, entity_id, name, lat, lng, tz, status, city_id)
applications(application_id, outlet_id, state, version, risk_score, idem_key)
documents(doc_id, application_id, type, s3_uri, av_status, ocr_json)
compliance_checks(check_id, outlet_id, type, status, expires_at, evidence_ref)
menus(outlet_id, menu_version, ...)
items(outlet_id, item_id, menu_version, ...)
payout_methods(payout_id, entity_id, psp_token, status)
discovery_profiles(outlet_id, h3, radius, tags[], hours_json, updated_at)
review_tasks(task_id, application_id, priority, assignee, sla_due, state)
audit_events(id, actor, entity, action, ts, payload_ref)
outbox(id, aggregate_type, aggregate_id, payload, created_at, published_at)
```

### 8.2 Gate matrix (example city)

| Gate | Required | Auto? |
|------|----------|-------|
| KYB | Yes | Vendor |
| Food permit | Yes | OCR+manual |
| Alcohol license | If alcohol SKUs | Manual |
| Payout | Yes | PSP |
| Menu min items | Yes | Rules |
| Geo pin | Yes | Rules+map |
| Contract | Yes | Clickwrap |
| Sanctions | Yes | Vendor |

### 8.3 Invariants

| Invariant | Rule |
|-----------|------|
| LIVE ⇒ all hard gates GREEN | Orchestrator |
| Single LIVE transition | CAS |
| Docs AV clean before review download | Doc service |
| Discovery upsert after LIVE | Outbox |
| Tax id encrypted | Storage |
| Menu currency = outlet currency | Validator |

### 8.4 Scale checklist

| Scale | Must |
|-------|------|
| 1× | App SM, S3 docs, KYB, menu, payout, go-live, search publish |
| 10× | Async webhooks, AV, outbox, menu service |
| 100× | Policy engine, review platform, chains, CDC |
| 1000× | Auto KYB, ML risk, renewals, merchant cells |

### 8.5 Glossary

| Term | Meaning |
|------|---------|
| KYB | Know Your Business |
| UBO | Ultimate beneficial owner |
| Gate | Hard/soft prerequisite for live |
| Outbox | Reliable publish pattern |
| Discovery profile | Search/geo projection |
| 86 | Mark item unavailable |
| Action required | Applicant must fix |
| Probation | Limited live with caps |

### 8.6 Estimation cheat-sheet

```text
doc_bytes/day ≈ apps/day × docs/app × avg_size
manual_reviews ≈ apps × manual_rate
menu_storage ≈ outlets × items × bytes
discovery_qps ≈ live_changes/day / 86400
```

### 8.7 Reason codes (sample)

```text
DOC_BLURRY, DOC_EXPIRED, KYB_MISMATCH, GEO_INVALID,
MENU_TOO_SMALL, PAYOUT_NAME_MISMATCH, SANCTIONS_HIT,
TRADEMARK_COMPLAINT, RISK_HIGH
```

### 8.8 SLOs

| SLO | Target |
|-----|--------|
| Submit p99 | < 500ms |
| Auto decision p50 | < 24h |
| Manual decision p50 | < 72h |
| Discovery lag after LIVE | p99 < 5 min |
| Unauthorized doc access | 0 |
| LIVE without payout verified | 0 |

### 8.9 Decision log

| Decision | Pick | Why |
|----------|------|-----|
| Upload path | Presigned S3 | Scale/security |
| Search sync | Outbox | Reliability |
| Gates | Hard before LIVE | Trust |
| Menu | Separate service | QPS diverge |
| Residency | Geo home | Compliance |

### 8.10 Related systems

- Global food delivery (orders/match)  
- Payments / ledger  
- Search / discovery  
- Fraud platform  
- Notifications  
- POS integrations  

### 8.11 Narrative (2 min)

> “Restaurant registration is a **trusted onboarding control plane**. Merchants and outlets move through an application state machine with hard gates—KYB, permits, payout, menu, geo, contract, risk. Documents go to encrypted object storage with AV/OCR; decisions come from vendors plus policy plus human review. Go-live is an orchestrated CAS transition that emits an outbox event so geospatial discovery indexes the outlet. At scale, menu traffic separates from onboarding, policies are data, and automation drives manual review toward a thin tail.”

### 8.12 Checkpoint

1. Merchant vs outlet?  
2. Hard go-live gates listed?  
3. Doc upload security?  
4. Outbox to discovery?  
5. Menu QPS separated?  
6. Geo residency?  

### 8.13 Risks register

| Risk | Mitigation |
|------|------------|
| Fraud live | Risk+probation |
| Vendor outage | Queue+SLA comms |
| Doc cost | Size limits+lifecycle |
| False rejects | Appeals+calibration |
| Index lag | Reconciler+SLO |

### 8.14 Sample sequence diagram (text)

```text
Owner: submit application
App: state=SUBMITTED
App: enqueue KYB
Vendor: webhook PASS
Compliance: permits PASS
Owner: import menu OK
Owner: verify bank OK
Orchestrator: all GREEN → READY_FOR_LIVE
Owner: go-live
App: CAS LIVE + outbox
Publisher: upsert discovery
Search: outlet visible nearby
```

### 8.15 Reviewer UI essentials

- Doc gallery with AV badge  
- Map with pin + address  
- Gate checklist  
- Risk panel  
- Decision + reason codes  
- Audit trail  

### 8.16 Policy-as-data example

```json
{
  "city_id": "sea",
  "required_docs": ["FOOD_PERMIT", "OWNER_ID"],
  "kyb_level": "STANDARD",
  "min_menu_items": 5,
  "max_radius_m": 8000,
  "alcohol_requires": ["LIQUOR_LICENSE"]
}
```

### 8.17 Post-live feedback loop

```text
Order quality / complaints / cancellations → Risk → probation/suspend
Feeds future auto-approve thresholds (careful with bias)
```

### 8.18 Extensions

- Photo menu OCR  
- Bulk chain HQ APIs  
- Government permit integrations  
- Insurance certificates  
- Sustainability badges  

### 8.19 Amazon interview tip

Lead with **gates and trust**, not UI fields. Then show async verification, outbox discovery, and scale math on documents/menus.

### 8.20 Final checklist for you

| Done? | Item |
|-------|------|
| ☐ | Clarified merchant/outlet |
| ☐ | Listed hard gates |
| ☐ | Doc security path |
| ☐ | KYB webhook idempotency |
| ☐ | Menu vs onboarding QPS |
| ☐ | Discovery outbox |
| ☐ | 10×/100×/1000× |
| ☐ | 40+ Q&A ready |

---

*End of document — Restaurant Registration System (Amazon SDE III system design)*
