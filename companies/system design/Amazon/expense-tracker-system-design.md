# System Design: Expense Tracker System

> **Focus areas:** Multi-user / org tenancy · Expense capture · Receipts (OCR) · Categories & policies · Reports · Optional approvals · Reimbursement hooks · Audit · Progressive scale  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct multi-tenant isolation, split write vs report planes, explicit approval state machines, deal-breakers for “one shared Postgres table without org_id”  
> **Amazon lens:** Internal expense / T&E–class concerns, contractor orgs, policy compliance, receipt fraud, ownership of financial audit trails

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

Goal: **bound an expense tracker**—employees (and multi-seat orgs) capture spends with receipts, categorize against policy, optionally route approvals, generate reports for finance, and export/reimburse—without leaking data across tenants or losing auditability.

### 1.0 What this is / is not

| Dimension | **Expense tracker (this doc)** | Not this |
|-----------|--------------------------------|----------|
| Primary job | Capture → categorize → (approve) → report / reimburse | Full ERP / general ledger replacement |
| Success | Correct books per org; policy enforced; fast mobile capture | Pretty charts alone |
| Tenancy | Org / workspace isolation hard | Viral consumer-only piggy bank |
| Money | Integer minor units + FX snapshots | Float doubles |
| Approvals | Optional workflow | Mandatory for MVP personal use |
| Amazon lens | Corporate T&E scale, receipt integrity, policy engines | Consumer Mint clone without orgs |

**Scope statement:** Design a multi-user / multi-org expense tracker with receipt storage & OCR, categories & policy rules, reports, optional approval workflows, audit logs, and progressive scale.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Personal vs org? | Both: personal books + company workspaces | Tenant model: `org_id` + membership |
| F2 | Who submits? | Employees, contractors; delegates/admins | RBAC roles |
| F3 | Capture methods? | Manual, mobile photo, email inbox, card feed | Ingestion adapters |
| F4 | Receipts? | Image/PDF upload; OCR extract amount/date/merchant | Object store + OCR pipeline |
| F5 | Categories? | Org chart of accounts + personal custom | Hierarchical categories; mappings |
| F6 | Policies? | Per-diem, category caps, require receipt >$X | Policy engine at submit/approve |
| F7 | Approvals? | Optional; manager chain / amount thresholds | Workflow service |
| F8 | Reports? | By category, project, employee, period; CSV/PDF | Async report jobs + warehouse |
| F9 | Multi-currency? | Yes; home currency reporting | FX rate pin at expense date |
| F10 | Projects / cost centers? | Tag expenses | Dimensions |
| F11 | Card feeds? | Optional corporate card import | Idempotent txn import |
| F12 | Reimbursement? | Export to payroll / mark reimbursed | State + payout hook |
| F13 | Duplicates? | Same receipt twice | Soft-dupe detection |
| F14 | Audit? | Who changed what | Immutable audit log |
| F15 | Search? | Merchant, amount, date, memo | Search index per tenant |

**MVP functional scope:**

1. Orgs, users, roles (member, manager, finance_admin, org_admin).  
2. Create/edit/delete (soft) expenses with line items optional.  
3. Receipt upload to private object storage; link to expense.  
4. OCR async extract → user confirm.  
5. Categories + basic policy (receipt required over threshold).  
6. Optional approval workflow (submit → approve/reject).  
7. List/filter + summary reports for a period.  
8. CSV export.  
9. Audit log of mutations.  
10. Multi-currency with pinned FX.

**Out of MVP:**

- Full accounting double-entry GL  
- Automatic IRS schedule generation for all countries  
- Real-time corporate card authorization control  
- ML category with perfect accuracy offline-only forever without confirm  
- Cross-org expense sharing marketplace  

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Mobile capture latency | Snappy upload | Presigned URL; p99 API < 200ms |
| N2 | OCR lag | Seconds–minutes OK | Async; notify on ready |
| N3 | Tenant isolation | Hard | Every query constrained by org_id |
| N4 | Durability | Receipts & expenses durable | Multi-AZ object + DB |
| N5 | Report freshness | Interactive summaries minutes OK | Pre-agg + on-demand |
| N6 | Consistency | Expense mutate strong within org | RDBMS per cell |
| N7 | Security | Private receipts | Encrypted; signed URLs; no public buckets |
| N8 | Scale | See table | Shard by org_id |
| N9 | Compliance | Retention, export, delete | Legal holds; GDPR erase flows |
| N10 | Availability | Capture > fancy reports | Degrade OCR/reports first |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Employee photos receipt → upload → OCR fills $42.50 Starbucks → categorize Meals → submit → manager approves → marked reimbursed.  
2. Personal user tracks groceries without approvals.  
3. Finance admin runs Q2 report by cost center → CSV.  
4. Corporate card feed imports txn → match receipt → attach.  
5. Policy blocks submit without receipt for $75 taxi.  
6. Delegate submits on behalf of exec with audit.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| OCR wrong amount | User edits; store both raw OCR + confirmed |
| Duplicate upload | Warn soft-dupe (amount+date+merchant+hash) |
| Two managers in chain | Sequential or parallel policy |
| Approver leaves company | Reassign queue; escalate |
| FX missing for date | Fallback rate source + flag |
| Huge PDF receipt | Size limits; virus scan |
| Cross-org IDOR | Fail closed; automated tests |
| Edit after approve | Policy: locked or reopen workflow |
| Partial reimbursements | Payment allocations |
| Timezone date boundaries | Org timezone for “expense date” |
| Offline mobile | Local draft; sync later idempotent |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Orgs | 10K | 100K | 1M | 10M |
| Active users | 200K | 2M | 20M | 200M |
| Expenses created / day | 500K | 5M | 50M | 500M |
| Peak write QPS | ~50 | ~500 | ~5K | ~50K |
| Receipt uploads / day | 300K | 3M | 30M | 300M |
| OCR jobs / day | 300K | 3M | 30M | 300M |
| Report runs / day | 50K | 500K | 5M | 50M |
| Avg receipt size | 400 KB | same | same | same |
| Read/list QPS | ~200 | ~2K | ~20K | ~200K |

**What each jump forces:**

- **10×:** Presigned uploads; OCR queue; org-scoped indexes; approval service.  
- **100×:** Shard/cell by org; search index; report warehouse; lifecycle receipts to cold.  
- **1,000×:** Multi-cell tenancy routing; heavy orgs isolated; streaming exports; OCR autoscale pools.

### 1.5 Etc. (Constraints & Assumptions)

- **org_id on every row**; personal workspace is still an org (type=PERSONAL).  
- Money **integer minor units**.  
- Approvals optional per org setting.  
- Prefer **user-confirmed OCR** before reimbursement.  
- Amazon-style ownership: policy false negatives (blocking legit expense) vs false positives (policy bypass)—call out product preference (usually block submit with clear reason).

**Scope statement:**

> Multi-tenant expense tracker: capture, receipts/OCR, categories, policies, optional approvals, reports/exports—from ~50 write QPS through 1,000× (~50K), with hard tenant isolation and auditability.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Create/update expense | 50 | 50K | Strong consistency |
| List/filter | 200 | 200K | Indexes / cache |
| Receipt upload init | 30 | 30K | Presign only |
| OCR complete callbacks | 20 | 20K | Async |
| Submit / approve | 20 | 20K | Workflow |
| Report generate | 5 | 5K | Async jobs |
| Search | 50 | 50K | Per-tenant index |
| Card feed ingest | 10 | 10K | Batch bursts |

### 2.2 Storage

```text
Expense row ~500 B–2 KB
500K/day × 1 KB = 500 MB/day baseline
100×: 50M/day × 1 KB = 50 GB/day

Receipts: 300K/day × 400 KB = 120 GB/day baseline
100×: 30M × 400 KB = 12 TB/day → lifecycle to IA/Glacier

OCR text ~2–5 KB/expense — small vs images
Audit log ~similar order to expense mutations
```

### 2.3 Bandwidth

```text
Upload peak: 30 QPS × 400 KB ≈ 12 MB/s baseline (easy)
1000×: 30K × 400 KB ≈ 12 GB/s → CDN/edge upload + regional buckets
```

### 2.4 Report compute

```text
Org with 1M expenses/year summarizing by category:
  Warehouse scan or pre-agg rollups by day×category×user
Interactive UI should hit rollups not raw scans at 100×+
```

### 2.5 Critical bottlenecks

1. Receipt storage cost & virus scanning  
2. Hot org (huge enterprise) noisy neighbor  
3. Report scans without rollups  
4. OCR backlog after offsites  
5. Cross-tenant query bugs (security)  
6. Approval queue latency SLAs  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Org (org_id, type=PERSONAL|COMPANY, tz, settings)
Membership (org_id, user_id, role)
Expense (expense_id, org_id, submitter_id, amount_cents, currency,
         fx_rate, home_amount_cents, spent_at, merchant, memo,
         category_id, project_id, status, policy_result)
ExpenseLine (optional itemization)
Receipt (receipt_id, org_id, expense_id, object_key, hash, ocr_status)
OCRResult (receipt_id, raw_json, parsed_amount, parsed_merchant, ...)
Category (org_id, category_id, parent_id, name)
Policy (org_id, rules_json, version)
ApprovalRequest (expense_id, steps[], state)
ReportJob (org_id, query, status, result_url)
AuditEvent (org_id, actor, entity, before/after, at)
```

### 3.2 Status state machine

```text
DRAFT → SUBMITTED → APPROVED → REIMBURSED
              ↓          ↓
           REJECTED   (reopen→DRAFT policy)
DRAFT → (personal no-approve orgs) → BOOKED
```

### 3.3 Tenancy & RBAC

```text
Roles: MEMBER | MANAGER | FINANCE_ADMIN | ORG_ADMIN
Permissions:
  MEMBER: CRUD own drafts; submit
  MANAGER: approve reports of reportees
  FINANCE_ADMIN: all org expenses read; export; mark reimbursed
  ORG_ADMIN: policies, categories, members
Every API: authenticate → authorize(org_id, action) → query WITH org_id
```

**Deal-breaker:** trusting client-sent `org_id` without membership check.

### 3.4 Receipt upload flow

```text
1. Client POST /receipts/presign → {url, receipt_id, object_key}
2. Client PUT bytes to object store
3. Client POST /receipts/{id}/complete → virus scan enqueue + OCR enqueue
4. OCR worker writes OCRResult; notify user
5. User confirms → create/update Expense fields
```

### 3.5 Policy engine

```text
Examples:
  - amount >= 25 USD ⇒ receipt required
  - category=ALCOHOL ⇒ block or flag
  - meals per diem by city/day
  - weekend travel needs project tag
Evaluation points: save draft (warn), submit (enforce), approve (recheck)
Output: allow | deny(code) | flag(codes)
```

### 3.6 Approvals (optional)

```text
Config: approval_required bool + rules (amount thresholds, categories)
Resolver: manager from HR feed / org chart; fallback finance_admin
Steps: sequential chain; each APPROVE/REJECT with comment
SLA timers → escalate
Idempotent actions with action_id
```

### 3.7 Reports

| Type | Serving |
|------|---------|
| Interactive summary (this month by category) | Pre-agg rollups |
| Employee spend vs budget | Rollups + budget table |
| Ad-hoc large export | Async job → CSV in object store |
| Finance close package | Warehouse SQL |

```text
Rollup key: (org_id, day, category_id, user_id, project_id) → sum, count
Update: on expense state change (approved/booked)
```

### 3.8 Card feed & matching

```text
Import bank/card CSV or API → CardTxn(org_id, external_id UNIQUE)
Matcher: amount+date+merchant fuzzy → suggest link to expense/receipt
Manual confirm; never auto-reimburse without policy
```

### 3.9 Search

```text
Per-org index documents: expense_id, merchant, memo, amount, date, category
Engine: OpenSearch/ES with routing=org_id
Privacy: no cross-org search
```

### 3.10 Storage trade-offs

| Store | Role |
|-------|------|
| Postgres/Aurora | Expenses, workflows, membership (by cell) |
| S3 | Receipts, exports |
| SQS/Kafka | OCR, reports, notifications |
| Redis | Sessions, hot summaries |
| OpenSearch | Tenant-routed search |
| Redshift/Snowflake | Heavy analytics |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Mobile] [Web] [Email Ingest] [Card Feed Importer]
              |
              v
        API Gateway + AuthN/Z (org-scoped)
         /          |           \
        v           v            v
  Expense Svc   Receipt Svc   Approval Svc
      |             |              |
      v             v              v
  Policy Engine  S3 + OCR      Notify
      |          Workers
      v
  Postgres (org-sharded) + Rollups/Cache
      |
      v
  Report Job Service --> Warehouse / Export S3
```

### 4.2 OCR pipeline

```text
complete → antivirus → OCR vendor/model → parse → OCRResult
       → confidence low? flag needs_review
       → notify client
```

### 4.3 Approval flow

```text
submit → policy.enforce → create ApprovalRequest
      → notify step1 → approve → next step | final APPROVED
                       reject → REJECTED + reason
```

---

## 5. Design Deep Dive

### 5.1 Reliability

**Invariants**

1. Every expense/receipt/audit row has `org_id`.  
2. Membership required for access.  
3. Approved expenses immutable without controlled reopen.  
4. Receipt object keys unguessable; access via short-lived signed URLs.  
5. Report exports contain only authorized org data.

**Failure modes**

| Failure | Mitigation |
|---------|------------|
| OCR provider down | Queue lag; manual entry path |
| Upload incomplete | complete() only after HEAD success |
| Double submit | Idempotency-Key on create/submit |
| Approver unavailable | Escalation / reassignment |
| Rollup lag | Show “as of” timestamp |
| Ransomware on buckets | Versioning + MFA delete |

**Degradation:** OCR optional path; reports delayed; capture always works.

### 5.2 Scalability

| Scale | Tactic |
|-------|--------|
| 10× | Indexes (org_id, spent_at); presign; async OCR |
| 100× | Shard orgs across DB cells; search routing; rollups |
| 1,000× | Isolate elephant orgs; regional cells; streaming export |

**Elephant tenant:** dedicated DB + dedicated OCR concurrency quota.

**List APIs:** keyset pagination `(spent_at, expense_id)`; never OFFSET deep pages.

### 5.3 Maintainability

**Ownership:** Capture/API, Receipts/OCR, Policy, Approvals, Reporting, Identity/Tenancy.

**Config:** Policy versions immutable; evaluate with pin on submit.

**Observability:** upload success, OCR lag/p95, approval SLA, export failures, authz denials (monitor spikes = attacks or bugs).

**Testing:** tenant isolation fuzz; policy golden cases; approval graph tests; IDOR suites mandatory in CI.

---

## 6. Wrap-Up

### 6.1 MVP build order

1. Org/user/RBAC  
2. Expense CRUD + money/FX  
3. Receipts presign + S3  
4. Categories + receipt-required policy  
5. OCR async + confirm  
6. Approvals optional toggle  
7. List/filter + summary rollups  
8. CSV export job  
9. Audit log  
10. Card import lite  

### 6.2 Trade-offs

| Choice | Trade-off |
|--------|-----------|
| Confirm OCR | Slower UX; fewer wrong reimbursements |
| Async reports | Scale; not instant PDF |
| Org shard by hash | Simple; elephants need special case |
| Lock after approve | Control; less flexibility |

### 6.3 Risks

1. Cross-tenant data leak (sev-0).  
2. Receipt malware.  
3. Policy misconfig blocking travel season.  
4. OCR cost blowup.  
5. Approval bottlenecks.

### 6.4 60-second pitch

> Multi-tenant orgs with hard `org_id` isolation and RBAC. Expenses in integer cents with pinned FX. Receipts via presigned upload to private S3, virus scan + OCR async, user confirms. Policy engine on submit; optional multi-step approvals. Rollups for interactive reports; async exports for large CSV. Audit everything. Scale by sharding orgs; isolate elephant tenants.

---

## 7. Deeper / Related Interview Questions

### 7.1 Tenancy

**Q: Personal + company dual books?**  
A: Two memberships; UI context switch; never mix queries.

**Q: Reseller / accounting firm managing many orgs?**  
A: Partner role with explicit grants; still per-org authz.

**Q: Cell migration?**  
A: Sticky org→cell map; dual-write cutover.

### 7.2 Receipts & OCR

**Q: Dedup receipts?**  
A: Content hash per org; warn on collision.

**Q: Build vs buy OCR?**  
A: Buy MVP; keep parsed schema owned; swap providers.

**Q: PII in receipts?**  
A: Encrypt; restrict access; retention TTLs.

### 7.3 Policy

**Q: Per diem complex?**  
A: Lookup tables by city/date; compute day buckets in org TZ.

**Q: Soft vs hard enforce?**  
A: Org setting; MVP hard deny with codes.

### 7.4 Approvals

**Q: Matrix org multiple managers?**  
A: Policy picks primary; CC others.

**Q: Self-approve?**  
A: Forbidden unless org_admin break-glass audited.

**Q: Bulk approve?**  
A: Allowed for finance with limits + sampling audit.

### 7.5 Reports

**Q: Real-time exact?**  
A: Rollups eventual seconds–minutes; “as of” label.

**Q: 10M row export?**  
A: Stream to S3; signed download; don't hold HTTP.

### 7.6 Card feeds

**Q: Idempotent import?**  
A: `UNIQUE(org_id, external_txn_id)`.

**Q: Match confidence?**  
A: Suggest only; human confirm for reimbursement.

### 7.7 Security

**Q: IDOR test?**  
A: Automated cross-org access attempts in CI.

**Q: Signed URL leak?**  
A: Short TTL; content-disposition; optional re-auth for sensitive.

### 7.8 Estimation traps

**Q: 30M receipts × 400KB = 12PB/day?**  
A: 30M×400KB = 12 **TB**/day.

**Q: OFFSET 1M for list?**  
A: Use keyset; OFFSET dies.

### 7.9 Interview traps

**Q: “Global expenses table, filter in app.”**  
A: Authz in service + DB constraints; not client trust.

**Q: “Put receipts on public CDN.”**  
A: Never.

**Q: “Float money.”**  
A: Integer cents.

**Q: “OCR auto-approve payout.”**  
A: Confirm + policy + approvals.

### 7.10 Ownership scenarios

**Q: Sev: receipts from Org A visible in Org B.**  
A: Incident; revoke URLs; patch authz; audit access logs; customer notification.

**Q: OCR backlog 24h after conference.**  
A: Autoscale workers; manual entry; communicate.

**Q: Finance says report totals wrong.**  
A: Check rollup lag vs excluded DRAFT; reconcile job.

### 7.11 Comparisons

**Q: vs Expensify/Concur?**  
A: Same shape; interview focus on tenancy, OCR pipeline, policy, scale.

**Q: vs generic file storage?**  
A: Expense domain state machine + policy + approvals.

### 7.12 Misc deep cuts

**Q: Itemization?** A: Lines sum to header; tax lines.  
**Q: Mileage?** A: Rate tables × distance; GPS optional.  
**Q: Per-seat billing of SaaS?** A: Out of band billing service.  
**Q: Soft delete?** A: Tombstone; retain audit.  
**Q: Legal hold?** A: Suspend TTL deletes.  
**Q: Mobile offline?** A: Draft UUIDs client-generated; sync idempotent.  
**Q: Category ML?** A: Suggest only on MVP.  
**Q: Webhooks to ERP?** A: Outbox on APPROVED.  
**Q: Budgets?** A: Budget entity + alerts on rollups.  
**Q: Multi-entity subsidiaries?** A: Org hierarchy with rollup reporting careful on authz.

---

## 8. Appendices

### 8.1 Schema sketches

```text
orgs(org_id, type, tz, settings_json)
memberships(org_id, user_id, role, UNIQUE(org_id,user_id))
expenses(expense_id, org_id, submitter_id, amount_cents, currency,
  fx_rate_bp, home_amount_cents, spent_at, merchant, memo,
  category_id, project_id, status, policy_version, created_at)
receipts(receipt_id, org_id, expense_id, object_key, sha256, ocr_status)
ocr_results(receipt_id, raw_json, parsed_json, confidence)
categories(org_id, category_id, parent_id, name)
policies(org_id, version, rules_json, published_at)
approvals(approval_id, org_id, expense_id, state, current_step)
approval_steps(approval_id, step_n, approver_id, state, acted_at, comment)
rollups(org_id, day, category_id, user_id, project_id, sum_cents, cnt)
audit_events(id, org_id, actor_id, entity_type, entity_id, payload, at)
card_txns(org_id, external_id, amount_cents, spent_at, merchant, expense_id NULL)
```

### 8.2 API sketches

```text
POST /v1/orgs/{org}/expenses
Idempotency-Key: ...
{ "amount_cents":4250, "currency":"USD", "spent_at":"2026-08-05",
  "merchant":"Starbucks", "category_id":"MEALS" }

POST /v1/orgs/{org}/receipts/presign
→ { "receipt_id":"R1", "upload_url":"...", "headers":{...} }

POST /v1/orgs/{org}/expenses/{id}/submit
POST /v1/orgs/{org}/approvals/{id}/decide
{ "decision":"APPROVE", "comment":"ok" }

POST /v1/orgs/{org}/reports
{ "from":"2026-07-01", "to":"2026-09-30", "group_by":["category"] }
→ { "job_id":"J1" }
GET /v1/orgs/{org}/reports/J1 → { "status":"DONE", "url":"..." }
```

### 8.3 Policy pseudocode

```text
function enforce(expense, policy):
  violations = []
  if expense.amount >= policy.receipt_threshold and not expense.receipt:
    violations.add(RECEIPT_REQUIRED)
  if expense.category in policy.blocked:
    violations.add(CATEGORY_BLOCKED)
  per_diem = lookup(expense)
  if meals_that_day(expense) > per_diem:
    violations.add(PER_DIEM_EXCEEDED)
  return DENY if violations else ALLOW
```

### 8.4 Authorization pseudocode

```text
function authorize(user, org, action, expense=None):
  m = membership(user, org)
  if not m: deny
  if action == READ_ALL and m.role in (FINANCE_ADMIN, ORG_ADMIN): allow
  if action == READ_OWN and expense.submitter == user: allow
  if action == APPROVE and m.role == MANAGER and is_reportee(user, expense.submitter): allow
  deny
```

### 8.5 OCR worker pseudocode

```text
function process(receipt_id):
  obj = s3.get(receipt.object_key)
  av_scan(obj)
  raw = ocr_provider.analyze(obj)
  parsed = normalize(raw)
  save OCRResult
  emit ReceiptReady(receipt_id)
```

### 8.6 Rollup update

```text
on expense APPROVED/BOOKED or amount change:
  upsert rollup keys += delta
on reject/delete:
  upsert rollup keys -= delta
```

### 8.7 Soft-dupe heuristic

```text
same org AND abs(amount match) AND spent_at within 1 day
AND (merchant fuzzy OR receipt hash equal) → warn
```

### 8.8 Glossary

| Term | Meaning |
|------|---------|
| Org | Tenant boundary |
| Home amount | Amount in org reporting currency |
| Rollup | Pre-aggregated totals |
| Presign | Time-limited upload URL |
| Soft-dupe | Likely duplicate warning |
| Elephant tenant | Disproportionately large org |

### 8.9 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | CRUD, receipts S3, categories, basic policy |
| 10× | OCR queue, approvals, audit, CSV export |
| 100× | Org cells, search, rollups, cold storage |
| 1000× | Elephant isolation, streaming export, OCR pools |

### 8.10 Security checklist

- [ ] org_id on all queries  
- [ ] Membership checks  
- [ ] Private bucket + KMS  
- [ ] Short-lived signed URLs  
- [ ] Virus scan  
- [ ] IDOR tests in CI  
- [ ] Admin actions audited  

### 8.11 Operator runbooks

1. Cross-tenant suspicion  
2. OCR outage  
3. Upload failures spike  
4. Approval SLA breach  
5. Export job stuck  
6. Rollup drift  

### 8.12 Worked scale (100×)

```text
50M expenses/day → ~600 average QPS; peak ~5K
Receipts 12 TB/day → lifecycle policies mandatory
Rollups keep UI summaries O(categories) not O(expenses)
```

### 8.13 Worked scale (1,000×)

```text
500M expenses/day → cell routing; many DB clusters
Hot enterprise: dedicated cell
Exports: Spark/Flink style jobs not app servers
```

### 8.14 Interview “say this” summary

> Hard multi-tenant isolation; integer money; presigned receipts + async OCR with confirm; policy on submit; optional approvals; rollups + async exports; audit; shard by org.

### 8.15 Status transitions table

| From | To | Who |
|------|----|-----|
| DRAFT | SUBMITTED | submitter |
| SUBMITTED | APPROVED | approver |
| SUBMITTED | REJECTED | approver |
| APPROVED | REIMBURSED | finance |
| REJECTED | DRAFT | submitter edit |

### 8.16 FX note

```text
home_amount_cents = floor(amount_cents * fx_rate)
store fx_rate source + as_of date with expense
```

### 8.17 Notification matrix

| Event | Notify |
|-------|--------|
| Submitted | Approver |
| Approved/Rejected | Submitter |
| OCR ready | Submitter |
| Report done | Requester |
| Escalation | Fallback approver |

### 8.18 Reliability test plan

1. IDOR: user B cannot read org A expense.  
2. Double submit idempotent.  
3. Approve after policy change → pinned version.  
4. OCR retry poison → DLQ.  
5. Export contains only org rows.  
6. Rollup matches brute sum on sample.

### 8.19 Idempotency matrix

| API | Key | Replay |
|-----|-----|--------|
| Create expense | Idempotency-Key | Same expense_id |
| Complete receipt | receipt_id | No-op |
| Submit | expense_id+version | Same state |
| Approve decide | action_id | Same decision |
| Import card txn | org+external_id | No-op |

### 8.20 Final trap table

| Trap | Pushback |
|------|----------|
| Public receipt URLs | Data leak |
| No org_id | Tenant meltdown |
| Float money | Drift |
| Sync OCR on request | Mobile timeouts |
| OFFSET pagination | Deep page death |
| 30M×400KB=12PB/day | **12TB/day** |

### 8.21 Whiteboard close

Draw **Client → API (authz) → Expense DB**, **Receipts → S3 → OCR**, **Approvals**, **Rollups/Reports**. Walk an IDOR prevention and an approval chain.

> Tenant isolation failures are **sev-0**—design authz first, features second.

### 8.22 Sample policy JSON

```text
{
  "receipt_threshold_cents": 2500,
  "blocked_categories": ["ALCOHOL"],
  "approval": {"above_cents": 10000, "steps": ["MANAGER"]},
  "per_diem": {"MEALS": {"USD": 7500}}
}
```

### 8.23 Interview timing guide

| Minute | Topic |
|--------|-------|
| 0–5 | Tenancy, approvals optional, receipts |
| 5–10 | Scale numbers + storage |
| 10–25 | HLD + OCR + policy |
| 25–40 | Approvals, reports, security |
| 40–45 | 100× elephants + wrap |

---


### 8.24 Deep dive: email receipt ingest

```text
Inbound email address: receipts+{user_token}@expense.example
1. SES/Mail receiving -> S3 raw MIME
2. Parse attachments (pdf/jpg/png); drop executables
3. Map user_token -> user_id + default org
4. Create receipt + OCR; optional auto-draft expense
5. Notify user to confirm category
Security: token unguessable; rate-limit per token; DMARC on domain
```

### 8.25 Deep dive: delegate submit

```text
Grant: delegator -> delegatee with scope (projects, max amount, expiry)
Audit: actor=delegatee, on_behalf_of=delegator
Approvals: still use delegator's manager chain unless policy says otherwise
```

### 8.26 Deep dive: budget alerts

```text
budgets(org_id, dimension_key, period, limit_cents)
on rollup update:
  if sum > 0.8*limit: warn
  if sum > limit: flag expenses / block submit (org setting)
```

### 8.27 Sample report query (warehouse)

```sql
SELECT category_id, SUM(home_amount_cents) AS total, COUNT(*) AS n
FROM expenses_fact
WHERE org_id = :org
  AND spent_at >= :from AND spent_at < :to
  AND status IN ('APPROVED','REIMBURSED','BOOKED')
GROUP BY category_id
ORDER BY total DESC;
```

### 8.28 Mobile offline sync protocol

```text
Client generates expense_id (UUIDv7)
Local draft queue; sync when online
Server create with explicit expense_id + Idempotency-Key
Conflict: server version wins for APPROVED; client merge for DRAFT fields
Receipts: upload when online; link by receipt_id
```

### 8.29 Virus scan pipeline details

```text
complete() -> AV queue
AV clean -> OCR queue
AV infected -> quarantine bucket + notify + mark receipt FAILED_AV
Never OCR infected objects
```

### 8.30 Org chart sync

```text
HRIS feed nightly: manager_id per employee
Approval resolver uses feed version pinned at submit time
If manager missing: escalate to finance_admin queue
```

### 8.31 Cost model sketch

```text
Baseline:
  Receipts 120 GB/day * $0.023/GB-month storage (rough) -> dominate S3
  OCR $0.001-0.01 / page * 300K -> material COGS
  Optimize: compression, resolution caps (e.g. 2K px), cold tier 90d
```

### 8.32 GDPR erase flow

```text
1. Verify identity
2. Soft-delete expenses or anonymize merchant/memo
3. Delete receipt objects (unless legal hold)
4. Tombstone search docs
5. Retain audit minimal where law requires
```

### 8.33 Elephant tenant playbook

```text
Signals: expenses/day >> cell avg; report CPU hot
Actions:
  - move org to dedicated DB
  - dedicated OCR concurrency quota
  - pre-warm rollups hourly
  - disable ad-hoc scans; require warehouse path
```

### 8.34 Comparison matrix (interview)

| Concern | Personal Mint-like | This design |
|---------|--------------------|-------------|
| Tenancy | Single user | Org RBAC |
| Approvals | N/A | Optional workflow |
| Policy | Soft budgets | Enforceable |
| Receipts | Nice-to-have | First-class + OCR |
| Audit | Light | Finance-grade |

### 8.35 More interview Q&A

**Q: How do you prevent receipt screenshot reuse across employees?**  
A: Soft-dupe across org by hash; risk score; not perfect—policy + manager review.

**Q: Should rejected expenses count in budgets?**  
A: Usually no; configure.

**Q: Can finance edit amount after approve?**  
A: Adjustment entity preferred over silent mutate; re-approval if above threshold.

**Q: Webhook retries to ERP?**  
A: Outbox + exponential backoff; idempotency key = expense_id+status+version.

**Q: Full-text search on OCR?**  
A: Index OCR text in tenant search doc; PII awareness.

**Q: Multi-currency report?**  
A: Always show home_amount_cents; optional original currency breakout.

**Q: Rate limit abuse uploads?**  
A: Per-user and per-org quotas; cost controls.

**Q: How to version categories?**  
A: Soft rename; keep id stable; merge tools for admins.

**Q: SSO?**  
A: OIDC/SAML at gateway; SCIM for memberships.

**Q: Data residency?**  
A: Cell by region; org pinned; receipts in regional bucket.

### 8.36 Whiteboard sequence: submit with approval

```text
User -> API submit
API -> Policy.enforce (pin policy_version)
API -> Expense.status=SUBMITTED
API -> Approval.create(steps=[manager])
API -> Notify manager
Manager -> decide APPROVE
Approval -> final -> Expense.APPROVED
Rollup += amount
Outbox -> ERP webhook
```

### 8.37 Failure injection tests

1. Kill OCR mid-job -> retry without dup results.  
2. Approver decide twice -> one effect.  
3. Presign expired -> client re-presign.  
4. DB cell failover -> no cross-org leakage.  
5. Search index lag -> list API still correct from SQL.

### 8.38 Final checklist before coding interview ends

- [ ] Stated org isolation as invariant #1  
- [ ] Integer money + FX pin  
- [ ] Async OCR + confirm  
- [ ] Approvals optional  
- [ ] Rollups vs warehouse  
- [ ] Progressive 10x/100x/1000x  
- [ ] Sev-0 IDOR story  

---


### 8.39 Close

> Ship tenancy and audit first; OCR and approvals second. Integer money; async reports.

*End of Amazon SDE III prep doc: Expense Tracker System.*
