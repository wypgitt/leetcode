# System Design: Library System (Online + Offline Customers)

> **Focus areas:** Catalog · Circulation (checkout/return) · Holds/reservations · Online + in-branch channels · Inventory truth · Fines/fees · Identity · Multi-branch · Offline-tolerant staff clients · Search
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Single circulation ledger truth; channel-agnostic APIs; deal-breaker = separate “online inventory” vs “offline inventory” without reconciliation
> **Interview theme:** Microsoft public-bank style — **library supporting online and offline customers**; strong object model + distributed consistency story (HLD/LLD hybrid friendly)

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

Goal: design a **public / university library platform** where patrons discover and borrow materials **online** (search, place holds, manage account, e-borrow) and **offline / in-branch** (walk-up checkout at desk or self-check, returns, shelving), with consistent inventory and policies across branches.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Circulation + catalog + patron channels | Full ILS vendor replacement in one hour |
| Inventory | Item-level copies + status ledger | Bookstore retail POS only |
| Online | Web/mobile holds, account, e-resources | Entire city open-data portal |
| Offline | Staff clients + self-check when network flaky | Pure offline multi-week disconnected branches without sync plan |
| Success | Right patron gets right item; no double-loan | QPS vanity |
| Microsoft angle | Clean APIs, identity, eventual sync patterns | “Azure SQL” name-drop without invariants |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Actors? | Patron, librarian/staff, admin, system jobs | RBAC |
| F2 | Catalog? | Works (bib) + Items (copies) + e-resources | FRBR-ish model |
| F3 | Search? | Title/author/ISBN/subject + availability | Index + realtime status |
| F4 | Checkout? | Loan item to patron with due date | Atomic status transition |
| F5 | Return? | Check-in; trigger holds; fines | Return workflow |
| F6 | Holds? | Queue per work/item policy; pickup notices | Hold shelf state machine |
| F7 | Renewals? | Policy-limited; block if hold waiting | Policy engine |
| F8 | Fines/fees? | Overdue, lost, damage | Ledger + payments |
| F9 | Online channel? | Search, holds, renew, pay fines, e-borrow | BFF + notifications |
| F10 | Offline/in-branch? | Desk + self-check; barcode/RFID | Staff API + limited offline cache |
| F11 | Multi-branch? | Shared patrons; item home + current location | Branch topology |
| F12 | Notifications? | Hold ready, due soon, overdue | Email/SMS/push |
| F13 | E-resources? | Licenses, concurrent seats | Separate entitlement service |
| F14 | Reports? | Circ stats, inventory | Analytics eventually |

**MVP scope:**

1. Bib/work + item catalog; basic search.  
2. Patron accounts + library card identity.  
3. Checkout / check-in with barcode.  
4. Holds with pickup branch + expiry.  
5. Online: search, place/cancel hold, view loans, renew.  
6. In-branch staff client for circ desk.  
7. Due dates + overdue fine accrual job.  
8. Notifications for hold ready / due soon.  
9. Basic admin policies (loan length by item type).

**Out of MVP:** full MARC cataloging suite, RFID gate inventory robots, inter-library loan nationwide consortium perfection, sophisticated acquisitions/EDI, complete offline month-long branch autonomy.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Checkout latency in-branch | p99 < 300–500ms when online |
| N2 | Search p95 | < 200–400ms |
| N3 | Availability | High for catalog reads; circ must not silently double-loan |
| N4 | Consistency | Strong for item status transitions |
| N5 | Offline tolerance | Minutes–hours for staff with constrained operations |
| N6 | Audit | Who loaned/returned what when |
| N7 | Privacy | Patron reading history protections (policy) |
| N8 | Scale elasticity | Semester start / tax-form season / summer reading spikes |
| N9 | Durability | No lost checkout events |
| N10 | Accessibility | WCAG for online patron UX |

### 1.3 Cases

**Happy online:** search → see available/holdable → place hold → item pulled → notice → pickup checkout → return.  
**Happy offline/in-branch:** walk-in with card → staff scans item → loan created → due slip.  
**Edges:** two desks checkout same item; hold expires; patron blocked for fines; network partition at self-check; renew while hold pending; item marked lost then found; transfer between branches; e-resource seat exhaustion; barcode damaged; duplicate holds; child/guardian policies; privacy “forget history”; semester surge.

| Case | Behavior |
|------|----------|
| Double checkout race | Conditional update on item version; one wins |
| Self-check offline | Allow only safe cached policies; queue sync; block high-risk |
| Hold vs walk-in | Policy: hold shelf reserved; or short transit rules |
| Renew with holds | Deny or shorten |
| Lost item | Bill + status LOST; found → reverse carefully |
| Patron privacy request | Minimize retained history per policy |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Branches | 5 | 50 | 500 | 5,000 |
| Active patrons | 50K | 500K | 5M | 50M |
| Item copies | 200K | 2M | 20M | 200M |
| Circ transactions/day | 5K | 50K | 500K | 5M |
| Search QPS peak | 50 | 500 | 5K | 50K |
| Jump | Single system | Multi-branch SaaS | Consortium / multi-tenant | National platform |

### 1.5 Scope repeat-back

> A multi-branch library platform with a **single item circulation ledger**, bib/item catalog, holds, fines, and **two channels**—online patron apps and in-branch staff/self-check—including **bounded offline** operation for desks, without ever maintaining two irreconcilable inventories.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic

```text
5K circ tx/day ≈ 0.06/s avg; peak open hours 10–20× ⇒ ~1 tx/s
Search/browse much higher: 20–100× circ
Online holds: burst when new releases drop
Staff clients: sticky daytime load
```

### 2.2 Storage

```text
Item row ~200–500 B × 200K ≈ 40–100 MB
Bib records larger (MARC/JSON) — GBs with history
Loans/history: 5K/day × 300 B ≈ 1.5 MB/day → GBs/year
Events/audit: similar order
Search index: bib + availability fields
```

### 2.3 Hot spots

New popular title (50 holds, 3 copies); opening hour desk lines; university syllabus season; website scrape bots.

### 2.4 Offline queue sizing

```text
Branch outage 2 hours × 60 circ/hour ≈ 120 ops queued
Each op 1 KB → trivial storage; conflict rate matters more than bytes
```

### 2.5 Latency budget (checkout)

```text
Scan → staff UI → API authz → policy check → item CAS → loan insert → receipt
50 + 50 + 50 + 100 + 50 ≈ 300ms
```

### 2.6 Bottlenecks

(1) Item-level contention on hot titles (2) search relevance (3) hold notice storms (4) offline sync conflicts (5) payment for fines (6) not raw QPS.

---

## 3. High-Level Design

### 3.1 Core domain model

| Entity | Meaning |
|--------|---------|
| Work/Bib | Intellectual work (book title/edition metadata) |
| Item | Physical copy with barcode/RFID |
| Patron | Cardholder; may have guardians/blocks |
| Loan | Checkout instance: item + patron + due |
| Hold | Reservation queue entry |
| Branch | Location; pickup site; owning library |
| Fee | Fine/bill ledger entry |
| EResource | License + entitlements |
| Policy | Loan rules by patron type × item type |

### 3.2 Planes

| Plane | Responsibility | Consistency |
|-------|----------------|-------------|
| Circulation Ledger | Item status + loans | Strong per item |
| Catalog | Bib/metadata | Admin strong; readers eventual |
| Discovery | Search index | Eventual |
| Holds | Queues + pickup shelf | Strong per work/item policy |
| Fees | Money owed | Strong ledger |
| Identity | Patrons/staff | Strong authn/z |
| Offline Sync | Branch operation queues | Conflict-aware merge |
| Notifications | Outbound messages | At-least-once |
| E-Resources | Concurrent seats | Strong or lease-based |

**Deal-breaker:** “Online availability cache” that can checkout without updating the ledger.

### 3.3 Item status machine

```text
AVAILABLE → ON_HOLD_SHELF → LOANED → AVAILABLE
                ↘ IN_TRANSIT → …
LOANED → CLAIMED_RETURNED / LOST / DAMAGED → (resolution)
AVAILABLE → IN_TRANSIT (branch transfer)
E-resource: AVAILABLE_SEAT ↔ CHECKED_OUT_DIGITAL (time-limited)
```

### 3.4 Components

1. **Identity & Cards** — patrons, staff, SSO (university Entra), barcodes.  
2. **Catalog Service** — bib/item CRUD, import.  
3. **Search Service** — indexing, query.  
4. **Circulation Service** — checkout, return, renew (authoritative).  
5. **Holds Service** — place/cancel/fulfill/expire.  
6. **Policy Engine** — loan lengths, limits, blocks.  
7. **Fees Service** — accrual, payments, waivers.  
8. **Patron Portal BFF** — online channel.  
9. **Staff Gateway** — desk/self-check.  
10. **Offline Sync Service** — branch queues, conflict resolution.  
11. **Notification Service**.  
12. **Inventory / Shelving aids** — optional.  
13. **Reporting / Analytics** — async.  
14. **Admin Config**.  
15. **E-Resource Gateway**.

### 3.5 APIs (sketch)

```text
POST /v1/circ/checkout
  {patron_id, item_barcode, branch_id, staff_id?, client_request_id}

POST /v1/circ/checkin
  {item_barcode, branch_id, condition?}

POST /v1/holds
  {patron_id, bib_id, pickup_branch_id}

POST /v1/loans/{id}/renew
GET  /v1/search?q=&branch=

POST /v1/sync/batch          # offline staff flush
  {branch_id, ops:[{op_id, type, payload, ts, base_version}]}
```

### 3.6 Online vs offline channels

| Concern | Online patron | In-branch |
|---------|---------------|-----------|
| Auth | Password/SSO/app | Card + staff session / PIN |
| Primary actions | Holds, renew, pay, e-borrow | Checkout/in, cash/card fines, overrides |
| Latency path | Internet → BFF → services | LAN/WAN → staff gateway |
| Offline | Generally requires net | Bounded offline queue |
| Overrides | Rare | Supervisory overrides with audit |

### 3.7 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Bib vs item | Separate entities | Many copies / one work |
| Availability in search | Indexed approx + read-your-write on detail | Scale search |
| Offline checkout | Allow with risk tiers | Desk continuity |
| Hold at work vs item | Work-level queue typical | Fairness across copies |
| Fine money | Internal ledger + PSP | Audit |
| Multi-tenant consortia | Tenant = library system | 100× |
| Privacy | Configurable retention | Legal/policy variance |
| RFID | Optional parallel identifier | Same ledger |

---

## 4. Architecture Diagram

### 4.1 Context

```text
[Patron Web/Mobile] ──► CDN/BFF ──► API Gateway ──┐
[Staff Desk / Self-Check] ──────► Staff Gateway ──┴──► Services
        │                                              │
        └──── offline queue (bounded) ─────────────────┘
                          │
          ┌───────────────┼────────────────┐
          ▼               ▼                ▼
     Circulation     Catalog/Search     Fees/Holds
     (item CAS)         │                │
          │               ▼                ▼
          └────────── Event bus ──► Notify / Analytics
                          │
                    Identity (SSO/Cards)
```

### 4.2 Checkout sequence (online-connected desk)

```text
scan card → resolve patron → check blocks/fees
scan item → load item version → policy.loan_ok?
CAS item status AVAILABLE→LOANED (or ON_HOLD_SHELF for rightful patron)
insert loan row + outbox event → print due slip
```

### 4.3 Hold fulfillment

```text
copy returned OR available → Holds Service pops next eligible patron
item → IN_TRANSIT/ON_HOLD_SHELF for pickup_branch
notify patron → pickup window timer → expire → next patron
```

### 4.4 Offline sync

```text
Staff client local DB:
  - cached patron block flags (TTL)
  - cached item versions snapshot
  - policy bundle
Ops recorded with op_id + base_version
On reconnect: Sync Service applies in order; conflicts → staff resolution queue
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Item status changes only via circulation commands with **CAS/version**.  
2. One active loan per physical item.  
3. Idempotent `client_request_id` / `op_id` for checkout/checkin.  
4. Holds fulfillment is serialized per bib queue.  
5. Fees are ledger entries; waivers audited.  
6. Offline ops never silently invent availability without sync rules.  
7. Privacy controls apply to history retention and staff views.  
8. Notifications are side effects via outbox.  
9. Supervisory overrides require role + reason.  
10. E-resource seats cannot exceed license (lease/count).

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Modular monolith; Postgres; OpenSearch; Redis cache |
| 10× | Split circ/catalog/search; read replicas; branch sharding soft |
| 100× | Multi-tenant cells; per-system DB; shared platform |
| 1000× | Consortium routing; national ILL bridges; regional cells |

### 5.3 Maintainability

- Policy as data (not hardcode loan days).  
- MARC/import pipelines versioned.  
- Circ command handlers tested with race fixtures.  
- Offline conflict simulator.  
- Feature flags for pickup expiry lengths.  
- Schema migrations expand/contract.

### 5.4 Progressive scale

**1×:** One city library, 5 branches, single Postgres, staff web app, patron portal.  
**10×:** Library system SaaS product; many municipalities; standardized offline client.  
**100×:** Consortia sharing catalog subsets; inter-branch courier network integration; multi-tenant isolation.  
**1000×:** National platforms; federated search; ILL protocols; extreme privacy regimes; 24/7 digital.

### 5.5 Double-loan prevention (core)

```text
UPDATE items SET status='LOANED', version=version+1, loan_id=?
WHERE item_id=? AND version=? AND status IN ('AVAILABLE','ON_HOLD_SHELF')
AND (status!='ON_HOLD_SHELF' OR hold_patron_id=?)
```

If 0 rows → conflict; reload; fail soft to staff.

### 5.6 Offline deep dive

**Allowed offline (typical):** checkin; checkout to patrons not blocked in cache; renewals within policy cache.  
**Denied offline:** override blocks; waive large fees; create new patrons (or limited); ILL; destructive deletes.

**Conflict examples:**

| Local op | Server state | Resolution |
|----------|--------------|------------|
| Checkout A | Already loaned online | Reject local; alert staff |
| Checkin | Already available | Idempotent success |
| Checkout A | On hold for B | Reject unless override policy |

**Clock skew:** server time authoritative for due dates; clients send intent; server assigns `due_at`.

### 5.7 Holds & fairness

- Queue ordered by place time + priority classes (disability, staff—policy).  
- When copy frees, assign next; set pickup expiry (e.g. 3–7 days).  
- Cancellation returns to queue.  
- Online patrons and desk patrons share same queue truth.  
- Popular title: many holds, few items → communicate position transparently.

### 5.8 Search & availability

Index bib fields + aggregate availability (`any_available`, `nearest_branch_counts`). Update via events; accept brief staleness. Item detail page reads authoritative circ for “request hold / available at”.

### 5.9 Fines & payments

Nightly/hourly job: loans past due → accrue fee per policy (grace periods). Cap fines if required by law. Pay via PSP; apply to fee ledger; unblock patron when balance < threshold. Staff cash payments recorded with drawer sessions.

### 5.10 Identity

- Library card number + PIN.  
- University: Entra ID / SAML / OIDC federation for students.  
- Staff: SSO + privileged roles.  
- Guardians for juvenile accounts.  
- Block states: fines, expired card, ban.

### 5.11 Privacy (interview signal)

Many jurisdictions treat reading history as sensitive. Options: retain only active loans by default; hash/archive; staff need-to-know; export/delete requests. Don’t put reading history in indiscriminate analytics without governance.

### 5.12 E-resources

Concurrent seat counter with leases (`checkout_digital` TTL). Overdue auto-return. Publisher connectors (authenticated proxy). Separate from physical item CAS but unified patron portal.

### 5.13 Multi-branch transfers

Item `home_branch` vs `current_branch`. Hold pickup may trigger `IN_TRANSIT`. Courier scans update location. Don’t allow checkout while `IN_TRANSIT` except intake.

### 5.14 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Separate online DB inventory | Double loans / ghost copies |
| Offline unlimited checkout | Unreconcilable debt & missing items |
| Search as source of truth | Stale availability loans |
| Fine in floating float field without ledger | Money disputes |
| No idempotency on self-check | Duplicate loans |
| Ignoring holds on renew | Unfairness SEVs |
| Global lock across all items | Unnecessary outages |

### 5.15 Microsoft mapping (optional)

| Concern | Mapping |
|---------|---------|
| Identity | Entra ID for campus libraries |
| APIs | Azure API Management |
| Data | Azure SQL / Cosmos for sync side buffers carefully |
| Events | Service Bus |
| Search | Cognitive Search / OpenSearch |
| Offline | Store-and-forward client; conflict service |
| Secrets | Key Vault |

### 5.16 Consistency matrix

| Data | Model |
|------|-------|
| Item status / loan | Strong CAS |
| Hold queue | Strong per bib |
| Search availability | Eventual |
| Patron profile | Strong |
| Fine balance | Strong ledger |
| Offline queue | Pending → committed/rejected |
| Analytics | Eventual |

### 5.17 Notifications

Events: `HoldReady`, `DueSoon`, `Overdue`, `CardExpiring`. Prefer email; SMS opt-in. Coalesce daily digests for due soon. Respect quiet hours.

### 5.18 Observability

SLIs: checkout success rate, conflict rate, sync reject rate, search latency, hold fulfillment time, notice delivery. Trace `item_id`/`loan_id`. Alert on sync backlog age.

### 5.19 Security

- IDOR on loans/holds.  
- Staff break-glass audited.  
- Rate limit search scrapers.  
- PCI scope minimized for payments.  
- RFID privacy (random reads) considerations.

### 5.20 University semester spike

Pre-scale search; freeze risky deploys; extend hold pickup windows if understaffed; monitor textbook title contention; chat support macros for “all copies loaned”.

---

## 6. Wrap-Up

### 6.1 Designed

Multi-channel library: bib/item catalog, strong circulation ledger, holds, fees, online portal + staff/self-check, bounded offline sync, notifications, e-resource seats—scaled from one system to consortia.

### 6.2 Decisions to defend

1. Bib vs item split  
2. CAS item status as truth  
3. Channel-agnostic circ APIs  
4. Work-level holds queue  
5. Bounded offline with conflict queue  
6. Fee ledger  
7. Privacy-aware history  
8. Search eventual, circ strong  
9. Idempotent ops  
10. Policy as data

### 6.3 Risks

- Offline conflict UX burden on staff  
- Hot title contention  
- Catalog data quality  
- Privacy legal variance  
- Consortium tenancy isolation bugs  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Online+offline meaning; MVP |
| 5–12 | Domain model bib/item/loan/hold |
| 12–22 | Checkout CAS + APIs |
| 22–32 | Holds + offline sync |
| 32–40 | Fines, privacy, search |
| 40–45 | Scale, deal-breakers, closer |

### 6.5 Closer

> **Library online+offline:** one circulation ledger for all channels, CAS on items to prevent double-loans, holds as a fair queue, and bounded offline desk ops with explicit conflict resolution—not two inventories hoping they match.

---

## 7. Deeper / Related Interview Questions

### 7.1 Scope

**Q: What does “offline customers” mean?**  
A: Clarify: (a) in-branch patrons without using the website, and/or (b) staff clients operating under network partition. Design for both; don’t assume only (a).

**Q: Public library vs university?**  
A: Uni adds SSO, reading lists, semester peaks, stricter e-resource licenses; public adds juvenile accounts, broader privacy norms.

### 7.2 Domain / LLD

**Q: Classes you’d code?**  
A: `Bib`, `Item`, `Patron`, `Loan`, `Hold`, `Policy`, `FeeLedger`, `CirculationService`, `HoldQueue`, `SyncOp`.

**Q: Why not only ISBN inventory counts?**  
A: Physical world is copy-level (barcode); counts alone can’t track who has which copy.

### 7.3 Concurrency

**Q: Two self-checks scan same item?**  
A: CAS version; one succeeds; other error “already loaned”.

**Q: Hold assign race on return?**  
A: Serialize fulfillment per bib with transaction or queue lock.

### 7.4 Offline

**Q: How long offline?**  
A: Bound (e.g. 4h); beyond that force read-only or open-ticket mode.

**Q: Could offline checkout an item already loaned online?**  
A: Yes risk → sync reject; operational process to recover item.

**Q: CRDTs for loans?**  
A: Usually wrong; loans need clear authority—use op log + reject, not merge “both loaned”.

### 7.5 Holds

**Q: Cancel hold mid-transit?**  
A: Re-route item to next patron or available.

**Q: Position in queue visible?**  
A: Yes approximate; careful with privacy (don’t reveal others’ identities).

### 7.6 Money

**Q: Fine accrual idempotency?**  
A: Job keys `(loan_id, fine_date)`; don’t double accrue.

**Q: Partial payments?**  
A: Apply FIFO to fee entries; unblock thresholds configurable.

### 7.7 Search

**Q: Filter “available now”?**  
A: Use indexed aggregates; may be slightly stale; verify on action.

**Q: Synonyms / authority control?**  
A: Catalog authority files; search analyzers; defer deep MLS theory unless asked.

### 7.8 Privacy & security

**Q: Staff looking up celebrity loans?**  
A: Need-to-know roles; audit; alerts on unusual lookups.

**Q: GDPR delete?**  
A: Anonymize history per legal retention for fines/audit.

### 7.9 Scale

**Q: 100× multi-tenant?**  
A: Tenant_id isolation; per-tenant DB or strict RLS; careful cross-tenant search bans.

**Q: National ILL?**  
A: Federated requests; different status plane; don’t put remote items in local CAS as available.

### 7.10 Microsoft-flavored

**Q: Integrate with Microsoft 365 university?**  
A: Entra SSO; Teams notifications for hold ready (optional); Graph calendar due dates—keep circ authoritative.

**Q: Build staff client as PWA?**  
A: Good offline story; IndexedDB op queue; background sync.

### 7.11 Rapid-fire

| Q | A |
|---|---|
| Two inventories? | Never |
| Truth? | Item CAS ledger |
| Offline unlimited? | No |
| Holds level? | Usually work/bib |
| Search truth? | No |
| Fine store? | Ledger |
| Idempotency? | op_id |
| SSO? | Entra/OIDC for uni |
| E-seat? | Lease/counter |
| Privacy default? | Minimize history |
| Pickup expiry? | Timer → next |
| Renew + hold? | Deny |
| IN_TRANSIT checkout? | No |
| Self-check IDOR? | Authz card+item |
| Hot title? | Queue transparency |
| Consortium? | Tenant cells |
| Analytics truth? | No |
| Barcode collide? | Unique constraint |
| RFID same? | Alias to item_id |
| Override? | Role+audit |

### 7.12 Traps

- Defining offline as “eventual consistency forever.”  
- Using search index for checkout.  
- Forgetting hold shelf reservations.  
- No patron block checks.  
- Floating fine totals.  
- Ignoring juvenile/guardian.  
- Skipping idempotency on flaky self-check networks.  
- Designing only website and forgetting desk UX.  
- CRDT cargo cult.  
- Global table lock.

---

## 8. Appendices

### Appendix A — Schemas

```sql
CREATE TABLE bibs (
  bib_id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  authors TEXT[],
  isbn TEXT,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE items (
  item_id UUID PRIMARY KEY,
  bib_id UUID NOT NULL REFERENCES bibs(bib_id),
  barcode TEXT NOT NULL UNIQUE,
  home_branch TEXT NOT NULL,
  current_branch TEXT NOT NULL,
  status TEXT NOT NULL,
  version BIGINT NOT NULL DEFAULT 0,
  hold_patron_id UUID,
  loan_id UUID
);

CREATE TABLE patrons (
  patron_id UUID PRIMARY KEY,
  card_number TEXT NOT NULL UNIQUE,
  status TEXT NOT NULL, -- active|blocked|expired
  patron_type TEXT NOT NULL,
  privacy_prefs JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE loans (
  loan_id UUID PRIMARY KEY,
  item_id UUID NOT NULL,
  patron_id UUID NOT NULL,
  checkout_branch TEXT NOT NULL,
  due_at TIMESTAMPTZ NOT NULL,
  returned_at TIMESTAMPTZ,
  state TEXT NOT NULL
);

CREATE TABLE holds (
  hold_id UUID PRIMARY KEY,
  bib_id UUID NOT NULL,
  patron_id UUID NOT NULL,
  pickup_branch TEXT NOT NULL,
  queue_pos BIGINT NOT NULL,
  state TEXT NOT NULL, -- queued|pending_pickup|fulfilled|cancelled|expired
  created_at TIMESTAMPTZ NOT NULL,
  expires_at TIMESTAMPTZ
);

CREATE TABLE fee_ledger (
  entry_id UUID PRIMARY KEY,
  patron_id UUID NOT NULL,
  loan_id UUID,
  amount_cents INT NOT NULL,
  reason TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE sync_ops (
  op_id UUID PRIMARY KEY,
  branch_id TEXT NOT NULL,
  payload JSONB NOT NULL,
  status TEXT NOT NULL, -- pending|committed|rejected
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL
);
```

### Appendix B — Checkout pseudocode

```python
def checkout(patron_id, barcode, branch_id, request_id):
    if seen(request_id): return prior_result(request_id)
    patron = load_patron(patron_id)
    policy.assert_can_borrow(patron)
    item = load_item_by_barcode(barcode)
    loan_id = new_id()
    due = policy.due_date(patron, item)
    rows = cas_loan_item(item, patron_id, loan_id)
    if rows == 0: raise Conflict()
    insert_loan(...)
    outbox("LoanCreated", ...)
    store_idempotent(request_id, loan_id)
    return loan_id
```

### Appendix C — Policy examples

| Patron type | Item type | Loan days | Max items | Renewals |
|-------------|-----------|-----------|-----------|----------|
| Adult | Book | 21 | 50 | 2 |
| Student | Textbook | 14 | 20 | 1 |
| Juvenile | Book | 21 | 30 | 2 |
| Adult | DVD | 7 | 5 | 1 |
| Staff | Book | 60 | 100 | 5 |

### Appendix D — Offline conflict playbook

1. Sync rejects checkout → staff asks patron to wait; locate item.  
2. Repeated conflicts → force online-only mode.  
3. Lost op_id duplicates → idempotent commit.  
4. Patron blocked server-side → reverse local loan if item still in hand; else mark claims returned workflow.

### Appendix E — SLIs

| SLI | Target |
|-----|--------|
| Checkout success (online) | 99.9% excl. conflicts |
| Double-loan incidents | ~0 |
| Sync backlog age | < 5 min p95 when net up |
| Hold notice latency | < 2 min p95 |
| Search p95 | < 300ms |

### Appendix F — Kill switches

- Disable offline checkout  
- Freeze hold placement on bib  
- Pause fine accrual  
- Read-only catalog  
- Disable external e-resource connectors  

### Appendix G — Narrative beats

1. Clarify online vs offline meanings.  
2. Draw bib/item/loan/hold.  
3. CAS checkout.  
4. Holds queue.  
5. Offline sync + conflicts.  
6. Fines/privacy.  
7. Scale to consortia.  
8. Closer.

### Appendix H — Pre-onsite checklist

- [ ] Domain model  
- [ ] CAS explanation  
- [ ] Holds states  
- [ ] Offline bounds  
- [ ] Conflict examples  
- [ ] Privacy stance  
- [ ] Progressive scale  
- [ ] 60s closer  

### Appendix I — Extra drills

1. Draw status FSM.  
2. Write CAS SQL.  
3. List offline allow/deny.  
4. Hold expiry flow.  
5. Fine accrual idempotency.  
6. Semester spike plan.  
7. Entra SSO sketch.  
8. Search staleness story.  
9. ILL vs local item.  
10. Juvenile guardian rules.  
11. Self-check sequence diagram.  
12. Idempotency store fields.  
13. Fee payment apply order.  
14. Privacy deletion plan.  
15. Multi-tenant isolation.  
16. E-resource seat lease.  
17. Barcode vs RFID.  
18. Claimed-returned workflow.  
19. Notification coalesce.  
20. 60s closer.

### Appendix J — Glossary

| Term | Meaning |
|------|---------|
| Bib | Bibliographic record |
| Circ | Circulation |
| Hold shelf | Reserved pickup location |
| ILL | Inter-library loan |
| CAS | Compare-and-swap / conditional update |
| OPAC | Online public access catalog |
| ILS | Integrated library system |

### Appendix K — Object model (LLD sketch)

```text
CirculationService.checkout(cmd) -> Result
PolicyEngine.evaluate(patron, item) -> Decision
ItemRepository.casTransition(...)
HoldQueue.popNext(bib_id) -> Hold
SyncPipeline.apply(op) -> Commit|Reject
FeeLedger.post(entry)
```

### Appendix L — Event types

`ItemCheckedOut`, `ItemCheckedIn`, `HoldPlaced`, `HoldReady`, `HoldExpired`, `LoanRenewed`, `FeeAccrued`, `FeePaid`, `SyncOpRejected`, `ItemLost`, `ItemTransferred`.

### Appendix M — Security checklist

- [ ] Patron can only see own loans/holds  
- [ ] Staff roles least privilege  
- [ ] Audit overrides  
- [ ] PII encryption at rest  
- [ ] Payment PCI scoping  
- [ ] Rate limits  
- [ ] Dependency scanning for staff clients  

### Appendix N — Comparison

| System | Like | Unlike |
|--------|------|--------|
| Inventory retail | Stock counts | Loans + due dates + privacy |
| Ticket booking | Reservations | Long-lived loans, returns |
| Uber Eats | Multi-channel | Not courier dispatch |
| LMS | Uni identity | Different domain objects |

### Appendix O — 60s closer

> We model works and copies separately and make the item circulation ledger authoritative for every channel—web, desk, and self-check. Checkouts are idempotent conditional updates so two scanners can’t double-loan. Holds are a single fair queue that shelves can fulfill. Offline mode is explicitly bounded: staff can keep serving with cached policy, then sync with reject-and-resolve on conflicts—never a second inventory. Fines are a ledger; privacy minimizes reading history. We scale by tenancy and cells, not by weakening item truth.

### Appendix P — Common mistakes

1. Count-only inventory.  
2. Offline CRDT loans.  
3. Search-driven checkout.  
4. Forgetting pickup expiry.  
5. No patron blocks.  
6. Hardcoded policies.  
7. Ignoring privacy.  
8. No idempotency.  
9. Mega-global lock.  
10. Building MARC editor all interview.

### Appendix Q — Sample hold states

`QUEUED → PENDING_PICKUP → FULFILLED`  
`QUEUED → CANCELLED`  
`PENDING_PICKUP → EXPIRED → (next QUEUED)`  

### Appendix R — Branch transfer sequence

```text
request transfer → IN_TRANSIT → courier scan → arrive scan → AVAILABLE or ON_HOLD_SHELF
```

### Appendix S — Metrics dashboard

Circ today; open holds; overdue rate; sync rejects; search latency; fine revenue; hot bibs; staff override rate.

### Appendix T — Sibling prompts

Shopping cart / library object model LLD; online marketplace; notification system; identity/SSO designs.

---

*End of Library online+offline system design prep doc.*
