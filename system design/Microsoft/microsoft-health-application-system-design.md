# System Design: Microsoft Ecosystem Health Application

> **Focus areas:** PHI handling · HIPAA-ish controls · Azure Health Data Services / FHIR · Entra identity · Consent · Audit · Data residency · Copilot-for-health boundaries · Device & provider portals  
> **Style:** Regulated product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Trust boundaries explicit; minimum necessary access; audit completeness; deal-breakers for PHI leakage  
> **Interview theme:** Microsoft — **health application** in the Microsoft cloud / HealthVault-era framing evolved to Azure Health Data Services

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

Goal: design a **consumer + clinician-adjacent health application** in the Microsoft ecosystem that stores and exchanges protected health information (PHI) using modern Azure health primitives (FHIR via **Azure Health Data Services**), Entra identity, strict consent, immutable audit, and careful AI/Copilot boundaries—acknowledging the historical HealthVault product lessons without pretending HealthVault is still the platform.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Personal health record + care coordination app | Hospital EHR replacement (Epic-class) |
| Data standard | FHIR R4 resources as system of record | Ad-hoc JSON only |
| Cloud | Azure + Entra + Health Data Services | Unregulated generic CRUD |
| AI | Optional insights with PHI-safe grounding | Unbounded Copilot over all medical data |
| Compliance | HIPAA-ish / HITRUST-oriented controls | Legal advice or certification claim |

**Framing line for interviewers:**

> HealthVault pioneered consumer PHR ideas; today we’d build on **Azure Health Data Services (FHIR)**, **Entra External ID / Entra ID**, **Key Vault**, **Purview**, and regional residency—not a greenfield blob of medical PDFs.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Users? | Patients/consumers; caregivers; clinicians (limited); admins | Role + relationship model |
| F2 | Records? | Conditions, meds, allergies, labs, vitals, documents, care plans | FHIR resources |
| F3 | Ingest? | Manual entry, device/wearable, provider FHIR, CCDA import | Ingestion pipelines |
| F4 | Share? | Patient-directed share with caregiver/clinic | Consent + break-glass rules |
| F5 | Auth? | Entra; MFA; optional verified identity | Strong authN |
| F6 | Notifications? | Med reminders, lab available, share requests | Careful content (min PHI in push) |
| F7 | Search? | Patient timeline; clinician search within consent | Indexed FHIR + ACL |
| F8 | AI? | Summarize my record; explain lab (Phase 1.5) | Isolated AI plane + policy |
| F9 | Audit? | Who viewed/exported what | Immutable audit |
| F10 | Export/delete? | Patient export; right-to-delete where legally applicable | Workflow + legal hold |
| F11 | Offline mobile? | Limited cached vitals | Encrypted device store |
| F12 | Regions? | Data residency by patient geo / tenant | Regional FHIR cells |

**MVP scope:**

1. Patient registration / login (Entra).  
2. FHIR-backed longitudinal record (Patient, Observation, Condition, MedicationStatement, AllergyIntolerance, DocumentReference).  
3. Manual entry + file upload (to blob + DocumentReference).  
4. Caregiver invite with scoped consent.  
5. Provider “view with consent” portal (read).  
6. Timeline UX + basic notifications (pointers, not full PHI in push).  
7. Immutable audit of access/export.  
8. Encryption at rest/in transit; Key Vault CMK hooks.  
9. Regional deployment with residency pin.  
10. AI summary stub behind explicit policy (optional Phase 1.5).

**Out of MVP:** full e-prescribe, claims/billing, complete EHR interoperability network, autonomous diagnosis, research secondary use without governance.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Availability | 99.9% patient read; write paths degrade gracefully |
| N2 | Latency | Timeline p99 < 500ms cached; FHIR write p99 < 1s typical |
| N3 | Durability | No silent PHI loss; geo per policy |
| N4 | Confidentiality | Encryption; strict authZ; min necessary |
| N5 | Audit completeness | Every PHI read/write/export attributable |
| N6 | Consent enforcement | Deny by default across services |
| N7 | Residency | PHI stays in allowed geo |
| N8 | Abuse resistance | Account takeover mitigations (MFA, CA) |
| N9 | AI safety | No training on customer PHI by default; no silent exfil |
| N10 | Break-glass | Rare, timed, audited, alerted |

### 1.3 Cases

**Happy**

1. Patient logs in → sees timeline → adds BP observation → syncs from wearable.  
2. Invites spouse caregiver → spouse sees allowed categories only.  
3. Clinic requests access → patient approves time-boxed consent → clinician reads labs.  
4. Patient exports FHIR bundle.  
5. AI summarize (if enabled) → runs in PHI-compliant regional endpoint → returns summary with citations to resources.

**Edges**

| Case | Behavior |
|------|----------|
| Consent expired mid-session | Revoke tokens; deny subsequent reads |
| Caregiver overreach API | AuthZ deny + audit |
| Wrong-patient IDOR | Globally unique IDs + authZ checks; tests |
| Stolen phone | Remote revoke; device encryption; MFA |
| Clinician break-glass ER | Time-boxed elevate + page privacy officer |
| Region failover | Only to residency-legal pair (see failover doc) |
| Copilot in M365 tries to read health tenant | Blocked unless explicit connector + consent |
| Bulk export job | Async; encrypted package; download audit |
| Minor / dependent accounts | Guardian relationship model |
| Conflicting meds from two sources | Provenance; don’t auto-delete; show conflict UX |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Patients | 1M | 10M | 100M | 1B |
| FHIR resources | 200M | 2B | 20B | 200B |
| Peak read QPS | 2K | 20K | 200K | 2M |
| Peak write QPS | 200 | 2K | 20K | 200K |
| Device events / day | 50M | 500M | 5B | 50B |
| Clinician users | 10K | 100K | 1M | 10M |
| Audit events / day | 20M | 200M | 2B | 20B |
| AI summary jobs / day | 50K | 500K | 5M | policy-capped |

**Jumps:** 10× = FHIR cell + device ingest bus; 100× = multi-region residency cells; 1,000× = national-scale PHR with provider network hooks and AI governance platform.

### 1.5 Scope repeat-back

> Design a Microsoft-ecosystem health app: Entra-authenticated patients and caregivers, FHIR system of record on Azure Health Data Services, consent-aware sharing, immutable audit, residency, careful device ingest, and optional PHI-safe AI summaries—not a full hospital EHR.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Load classes

| Class | Baseline | Plane |
|-------|----------|-------|
| Interactive FHIR reads | ~2K QPS | API + FHIR |
| Device telemetry writes | tens of K/s peak | Ingest bus → batch FHIR |
| Timeline BFF reads | ~5K QPS | Cache |
| Audit writes | ≥ every PHI access | Append-only |
| AI jobs | low QPS, heavy tokens | Isolated AI |

### 2.2 Storage

```text
Avg resources/patient ≈ 200 × 2 KB = 400 KB
1M patients ≈ 400 GB FHIR raw + indexes/versions
Documents: 10% patients × 5 docs × 1 MB = 500 GB blobs
Audit: 20M/day × 500 B ≈ 10 GB/day
```

### 2.3 Device ingest

```text
Wearables: 1M DAU × 50 events/day = 50M events/day ≈ 600/s avg; peak 10×
Aggregate on edge/mobile: send 5-min summaries → reduce 10×
```

### 2.4 AI cost caution

```text
Naive “stuff entire record into prompt” = expensive + risky
Retrieve min necessary FHIR resources → summarize with citations
```

### 2.5 Latency budget (timeline)

```text
BFF authZ 10ms + cache 5ms + (miss) FHIR search 100–300ms + assemble 20ms
Target: cache warm p99 < 200–500ms
```

---

## 3. High-Level Design

### 3.1 Trust boundaries

```text
[Mobile/Web Patient] [Caregiver] [Clinician Portal] [Device Cloud]
            \            |              |               /
             \           |              |              /
              v          v              v             v
                 +-----------------------------+
                 | Edge / APIM / WAF           |
                 +-------------+---------------+
                               v
                 +-----------------------------+
                 | Identity: Entra + MFA + CA  |
                 +-------------+---------------+
                               v
                 +-----------------------------+
                 | Health BFF / Consent AuthZ  |  <-- policy decision point
                 +-------------+---------------+
                               v
                 +-----------------------------+
                 | Azure Health Data Services  |
                 | (FHIR service)              |
                 +-----------------------------+
```

**Deal-breaker:** letting clients talk to FHIR with broad service credentials.

### 3.2 Domain model (FHIR-centric)

```text
Patient (resource)
  ├── Observations (vitals, labs)
  ├── Conditions
  ├── MedicationStatements / MedicationRequests
  ├── AllergyIntolerance
  ├── DocumentReference → Blob
  ├── CarePlan / Goals
  ├── Consent (who/what/when/purpose)
  └── Provenance / AuditEvent

Relationships:
  Patient ↔ RelatedPerson (caregiver)
  Patient ↔ Practitioner / Organization (via consent)
```

### 3.3 Identity & roles

| Persona | IdP | AuthZ basis |
|---------|-----|-------------|
| Patient | Entra External ID / Entra ID | Self (`Patient.id` link) |
| Caregiver | Same | Consent scopes |
| Clinician | Entra ID (org tenant) | Org membership + patient consent |
| Service | Managed identity | Narrow app roles |
| Admin / privacy | Entra PIM | Break-glass policies |

Map `oid` ↔ `Patient` via secure link table; never trust client-supplied patient id alone.

### 3.4 Consent model

```text
Consent {
  patient_id,
  grantee_id,              # user or org
  categories[],            # labs, meds, documents, ...
  purposes[],              # treatment, emergency, ...
  actions[],               # read, export
  valid_from, valid_to,
  status                   # active|revoked|expired
}
```

**Enforcement:** every read path calls Policy Decision Point (PDP) with `(actor, patient, resource_category, action)`.

Break-glass: separate purpose `emergency`, short TTL, mandatory notify patient/privacy.

### 3.5 HLD options for system of record

#### Option A — Custom Postgres schemas for health

| Pros | Cons |
|------|------|
| Flexible | Interop pain; reinvent FHIR semantics |

#### Option B — Azure Health Data Services FHIR (chosen)

| Pros | Cons |
|------|------|
| Standard resources, $export, ecosystem | Query patterns must be learned; cost/RU ops |

#### Option C — Documents only (PDFs in blob)

| Pros | Cons |
|------|------|
| Simple | Poor longitudinal analytics / care UX |

**Choice:** **B** + blob for binary; BFF aggregates timeline.

### 3.6 API shape

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/v1/me/timeline` | BFF assembled feed |
| POST | `/v1/me/observations` | Create vitals |
| POST | `/v1/consents` | Grant/revoke |
| GET | `/v1/patients/{id}/...` | Clinician/caregiver gated |
| POST | `/v1/imports` | CCDA/FHIR import job |
| POST | `/v1/exports` | Async export |
| POST | `/v1/ai/summaries` | Policy-gated summary |

Internal: FHIR REST to Health Data Services with **on-behalf** constrained access—not patient passwords to FHIR directly.

### 3.7 Ingestion pipelines

```text
Devices → IoT Hub / Event Hubs → Normalize → Validate → FHIR Observation upsert
Provider FHIR → Bulk import → Mapping → FHIR
Manual UI → BFF → FHIR
Docs → Blob (CMK) → DocumentReference
```

Idempotency keys on device events; provenance for source system.

### 3.8 AI / Copilot boundary (critical)

| Approach | Allowed? |
|----------|----------|
| Send full PHR to public multi-tenant Copilot without BAA/controls | **No** |
| Regional Azure OpenAI / Copilot Studio with PHI-capable tenancy + policy | Conditional |
| Retrieve-min-necessary + summarize + cite resource ids | **Preferred** |
| Use health data to train shared base models | **No by default** |

Architecture:

```text
AI Request → Consent/policy check → Retrieval (allowed resources)
  → Prompt assembly in isolated AI service (regional)
  → Completion → DLP/PHI egress check → Audit → Client
```

Never log prompts to non-PHI workspaces.

### 3.9 Notifications

Push/email contain **pointers** (“New lab result available”) not values (“HIV positive”).  
Deep link requires re-auth.

### 3.10 Component list

1. Edge / APIM  
2. Entra authN  
3. Health BFF  
4. Consent / PDP service  
5. FHIR service (AHDS)  
6. Blob for documents  
7. Ingest workers  
8. Timeline indexer/cache  
9. Audit service (immutable)  
10. Export/import jobs  
11. Notification service  
12. AI summary service (optional)  
13. Purview / compliance export  
14. Key Vault / CMK  

### 3.11 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| FHIR as SoR | Yes | Interop + clarity |
| BFF timeline | Yes | AuthZ + UX aggregation |
| Push PHI content | No | Device compromise / notifications leak |
| AI default on | No | Explicit opt-in |
| Multi-region writes | Careful | Prefer regional home cell for patient |

---

## 4. Architecture Diagram

### 4.1 Overview

```text
+----------+  +-----------+  +------------+  +----------+
| Patient  |  | Caregiver |  | Clinician  |  | Wearable |
| App      |  | App       |  | Portal     |  | Cloud    |
+----+-----+  +-----+-----+  +------+-----+  +----+-----+
     |              |               |             |
     +------+-------+-------+-------+             |
            v               v                     v
     +------+---------------+------+      +-------+-------+
     | APIM / Front Door           |      | IoT Hub /     |
     +-------------+---------------+      | Event Hubs    |
                   v                      +-------+-------+
     +-------------+---------------+              |
     | Entra ID / External ID      |              |
     +-------------+---------------+              |
                   v                              v
     +-------------+---------------+      +-------+-------+
     | Health BFF + PDP (consent)  |<---->| Ingest Workers|
     +------+----------------+-----+      +-------+-------+
            |                |                    |
            v                v                    v
     +------+-----+   +------+------+      +------+------+
     | Timeline   |   | Audit Log   |      | FHIR upsert |
     | Cache      |   | (append)    |      +------+------+
     +------+-----+   +------+------+             |
            |                ^                    v
            v                |             +------+----------------+
     +------+----------------+------+      | Azure Health Data    |
     | AI Summary (regional, opt)   |      | Services — FHIR      |
     +------------------------------+      +------+----------------+
                                                  |
                                           +------+------+
                                           | Blob + CMK  |
                                           | documents   |
                                           +-------------+
```

### 4.2 Consent check sequence

```text
Clinician GET /patients/{id}/Observation?category=laboratory
  → BFF validates Entra token (practitioner)
  → PDP: consent active for labs + treatment?
     no → 403 + audit deny
     yes → FHIR search
         → filter min necessary
         → audit allow (resource ids / hashes)
         → response
```

### 4.3 Patient home cell

```text
Patient.home_geo = US | EU | ...
All PHI planes (FHIR, blob, audit, AI) in that geo
Global directory holds only routing metadata (patient → geo), not clinical content
```

### 4.4 Export flow

```text
POST /exports → job queued → $export or bundle assemble
  → encrypt package (patient key / wrap with KV)
  → SAS download short-lived
  → audit export
  → expire blob
```

---

## 5. Design Deep Dive

### 5.1 Reliability / security invariants

1. **Deny by default**; consent or self-access required.  
2. Every PHI access emits **AuditEvent** (or equivalent) that cannot be silently dropped if compliance mode on.  
3. Patient home geo is sticky; failover only to legal pair.  
4. Service principals never have unbounded FHIR read across all patients in prod without break-glass.  
5. Document binaries in CMK-encrypted storage; links not guessable.  
6. AI paths are policy-gated and regional.  
7. Notifications minimize PHI.  
8. IDOR tests are release gates.  
9. Break-glass is timed, dual-control optional, loudly audited.  
10. Deletes honor legal retention/holds.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Single regional FHIR, BFF, Event Hubs ingest, PG for consent/link |
| 10× | Timeline cache, bulk import workers, audit lake tiering |
| 100× | Patient home cells by geo; sharded consent; clinician tenancy isolation |
| 1,000× | National exchange connectors; AI governance platform; advanced de-id pipelines |

### 5.3 Maintainability

- FHIR profiles/IGs as versioned contracts.  
- Mapping templates for CCDA→FHIR tested with golden fixtures.  
- Policy-as-code for consent categories.  
- Chaos: revoke consent mid-read; kill audit path (fail closed).  
- Privacy reviews for each new resource type.

### 5.4 Progressive narrative

**1×:** PHR for one country; manual + files; spouse sharing.  
**10×:** Wearables at volume; clinic read portal; export.  
**100×:** Multi-geo residency; hospital FHIR bulk; AI summaries opt-in.  
**1,000×:** Ecosystem of payers/providers; research sandbox with de-identification; strict data trusts.

### 5.5 AuthZ deep dive

```text
modes:
  - patient_self
  - caregiver_consent
  - clinician_consent
  - break_glass_emergency
  - system_job (export) with job-scoped tokens

implementation options:
  A) BFF enforces before FHIR (MVP)
  B) FHIR SMART on FHIR / fine-grained + BFF defense in depth (Phase 2)
```

Prefer defense in depth: BFF PDP + FHIR authZ constraints.

### 5.6 Encryption & keys

- TLS 1.2+  
- AES-256 at rest; **CMK** in Key Vault for FHIR/storage if customer requires  
- Per-blob encryption optional for ultra-sensitive docs  
- Envelope encryption for export packages  
- Separate keys per geo cell  

### 5.7 Audit design

```text
Audit record:
  actor, actor_role, patient_id, action, resource_types, resource_ids_or_hashes,
  purpose, consent_id, result (allow/deny), ip/device, ts, correlation_id
```

Store append-only (immutable storage / WORM pattern); queryable by privacy officers; patient-visible access history for trust.

### 5.8 Device ingest quality

- Deduplicate by device_event_id  
- Unit normalization  
- Outlier detection (sensor glitches) flagged, not auto-diagnosed  
- Provenance: `device_id`, `app_version`  

### 5.9 Interoperability

| Format | Direction | Notes |
|--------|-----------|-------|
| FHIR R4 | In/out | Primary |
| CCDA | In | Map carefully |
| DICOM | Phase 2 | Imaging via Azure DICOM service sibling |
| Claims EDI | Out of MVP | Different domain |

### 5.10 AI summarization deep dive

```text
1. User opts in + tenant/policy allows
2. Scope: e.g. last 12 months labs + conditions
3. PDP filters resources
4. Retriever packs <= N tokens with citations
5. Model in PHI-compliant regional deployment (Azure OpenAI with BAA/controls)
6. Output grounded; refuse if insufficient data
7. Store summary as Composition? or ephemeral — product choice; if store, consent applies
8. Full prompt/response audit under content-audit mode
```

**Deal-breaker:** using consumer Copilot pool that may retain data for training / wrong residency.

### 5.11 Failure & degradation

| Failure | Action |
|---------|--------|
| FHIR down | Read-only cache for recent timeline; writes queue |
| Audit down | Fail closed PHI reads if required |
| Ingest storm | Drop to aggregate; protect FHIR write budget |
| AI down | Hide feature; clinical record still works |
| Entra down | Existing sessions limited; new auth fails closed |
| Region loss | Failover doc; legal pair only |

### 5.12 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Broad service FHIR admin in mobile BFF | Mass PHI breach |
| PHI in push notifications | Shoulder-surf / lock screen leak |
| Shared AI logs with eng unrestricted | Compliance nightmare |
| Skip consent on “trusted clinic network” | Unauthorized access |
| Global single DB for all geos | Residency breach |
| Soft-delete audit | Tampering risk |
| Auto-diagnose from wearable noise | Clinical safety + liability |
| IDOR via sequential ids | Classic breach pattern |

### 5.13 Observability (privacy-aware)

- Metrics without resource payloads  
- Access deny rates (authZ bugs vs attacks)  
- Export job success  
- Ingest lag  
- AI policy reject rates  
- Break-glass frequency (should be near-zero)  

### 5.14 Threat model (sketch)

| Threat | Mitigation |
|--------|------------|
| Account takeover | MFA, CA, session binding |
| Insider curiosity | Least privilege, audit, UEBA |
| Malicious caregiver | Scoped consent, revoke, alerts |
| Ransomware | Backups, immutability, DR |
| Prompt injection via notes | Untrusted content labels in AI |
| XSS in portal | Standard web hardening |

### 5.15 Relationship to Microsoft products

- **Entra** for identity  
- **Azure Health Data Services** for FHIR (and DICOM later)  
- **Azure Blob + CMK** for documents  
- **Azure Key Vault** / Managed HSM  
- **Microsoft Purview** for governance/catalog  
- **Azure OpenAI** (PHI-capable configuration) for summaries  
- **Intune** optional for clinician devices  
- Historical **HealthVault**: cite lessons (consumer trust, ecosystem, clarity of clinical vs consumer roles)

### 5.16 Data lifecycle

```text
create/import → active use → archive cold tier → delete/export
legal hold blocks delete
versions retained per policy (FHIR versioning)
```

### 5.17 Caregiver & minor nuances

- Guardianship verification workflow (out-of-band / ID verify)  
- Age-out: minor becomes adult → re-consent  
- Intimate partner violence safety: hide locations / notify carefully (product policy)

---

## 6. Wrap-Up

### 6.1 Designed

A Microsoft-ecosystem health application: Entra identity, consent PDP, FHIR on Azure Health Data Services, device ingest, caregiver/clinician sharing, immutable audit, residency cells, and optional PHI-safe AI summaries.

### 6.2 Decisions to defend

1. FHIR as system of record  
2. BFF + PDP deny-by-default  
3. Min PHI in notifications  
4. Patient home geo cells  
5. CMK / Key Vault hooks  
6. Immutable audit; fail closed when required  
7. AI retrieve-min-necessary regional path  
8. Break-glass loudly  
9. Idempotent device ingest  
10. Export encrypted + audited  

### 6.3 Risks

- Consent UX complexity  
- FHIR query performance  
- Interop mapping errors  
- AI hallucination as medical advice (UX disclaimers + grounding)  
- Provider adoption  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope PHR vs EHR; HealthVault→AHDS framing |
| 5–12 | Personas, consent, PHI NFRs |
| 12–25 | HLD + FHIR + diagram |
| 25–35 | Audit, ingest, residency |
| 35–45 | AI boundaries, break-glass, scale |

### 6.5 Closer

> **Microsoft health app**: FHIR truth, Entra + consent as gates, audit always-on, residency sacred, AI optional and leashed—earn trust before features.

---

## 7. Deeper / Related Interview Questions

### 7.1 Compliance

**Q: Are we HIPAA compliant if we use Azure?**  
A: Azure can be HIPAA-eligible with BAA; **your app** must implement administrative/technical safeguards—platform ≠ automatic compliance.

**Q: What is “minimum necessary”?**  
A: Return/process only needed categories/fields for a purpose; design APIs accordingly.

### 7.2 Consent

**Q: Consent cached?**  
A: Short TTL + version; revocation must beat cache quickly (seconds).

**Q: Emergency access without consent?**  
A: Break-glass policy, legal jurisdiction dependent; always audit + notify.

### 7.3 FHIR

**Q: Why not only SQL tables?**  
A: Interoperability, standard operations ($export), ecosystem; BFF can still project UX models.

**Q: How do you page large histories?**  
A: FHIR search paging; timeline materialized views for UX.

### 7.4 AI

**Q: Can Copilot in Word read my labs?**  
A: Not unless explicit connector/consent and compliant path—default deny.

**Q: Hallucinated medication advice?**  
A: Grounded citations; disclaimers; avoid directive clinical orders in consumer MVP.

### 7.5 Security

**Q: IDOR test strategy?**  
A: Automated authZ matrix tests per role; fuzz resource ids; pen tests.

### 7.6 Scale

**Q: Wearable firehose vs FHIR write limits?**  
A: Aggregate/batch; don’t write every heartbeat as a resource.

### 7.7 Comparison traps

**Q: Is this HealthVault rebuilt?**  
A: Spiritual successor themes; modern Azure health stack + clearer clinical boundaries.

**Q: Is this Epic?**  
A: No—consumer/coordination PHR, not inpatient EHR.

### 7.8 Failure injection

1. Revoke consent during clinician session.  
2. Audit pipeline outage.  
3. FHIR 429 under ingest storm.  
4. Stolen refresh token.  
5. Malicious DocumentReference XSS.  
6. AI prompt injection in clinical notes.  
7. Cross-geo mis-route.  
8. Export job lexposure via guessable URL.  
9. Caregiver continues after patient removes.  
10. Clock skew on consent expiry.

### 7.9 Extra traps

- What’s in a crash dump—PHI?  
- How do support engineers access data?  
- How do you de-identify for analytics?  
- What’s the threat of metadata alone (visit to oncology clinic)?  
- How do you handle multi-patient clinicians’ search without leaking?  
- Where do encryption keys live in sovereign cloud?  
- How do you prove audit integrity?  
- What is the UX for conflicting data sources?  
- How do push tokens rotate on device loss?  
- When does offline mobile become a liability?

### 7.10 Related prompts

- Azure regional failover  
- Regional Copilot prompts (contrast PHI vs M365)  
- Key Vault  
- Fitness wearable heart-rate (less regulated sibling)  
- Dropbox/iCloud (contrast threat model)  

---

## 8. Appendices

### Appendix A — Link & consent schemas

```sql
CREATE TABLE patient_identity_links (
  patient_id     UUID PRIMARY KEY,
  entra_oid      UUID NOT NULL UNIQUE,
  home_geo       TEXT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE consents (
  consent_id     UUID PRIMARY KEY,
  patient_id     UUID NOT NULL,
  grantee_type   TEXT NOT NULL, -- user|org
  grantee_id     UUID NOT NULL,
  categories     TEXT[] NOT NULL,
  purposes       TEXT[] NOT NULL,
  actions        TEXT[] NOT NULL,
  valid_from     TIMESTAMPTZ NOT NULL,
  valid_to       TIMESTAMPTZ NOT NULL,
  status         TEXT NOT NULL,
  version        BIGINT NOT NULL,
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX consents_grantee ON consents (grantee_id, status);
```

### Appendix B — Audit event

```json
{
  "id": "uuid",
  "ts": "2026-08-06T00:00:00Z",
  "actor_oid": "...",
  "actor_role": "clinician",
  "patient_id": "...",
  "action": "read",
  "resource_type": "Observation",
  "resource_ids_hash": ["..."],
  "purpose": "treatment",
  "consent_id": "...",
  "result": "allow",
  "correlation_id": "..."
}
```

### Appendix C — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | FHIR, BFF, Entra MFA, consent, audit, CMK hooks |
| 10× | Device bus, timeline cache, export jobs |
| 100× | Geo cells, clinician tenancy, Purview, AI opt-in path |
| 1,000× | Exchange networks, de-id research sandbox, advanced UEBA |

### Appendix D — Glossary

| Term | Meaning |
|------|---------|
| PHI | Protected Health Information |
| FHIR | HL7 Fast Healthcare Interoperability Resources |
| AHDS | Azure Health Data Services |
| PHR | Personal Health Record |
| PDP | Policy Decision Point |
| Break-glass | Emergency elevate access |
| CMK | Customer-managed key |
| BAA | Business Associate Agreement |
| Provenance | Source/attribution metadata |
| HealthVault | Historical Microsoft PHR product |

### Appendix E — Estimation cheat-sheet

```text
Resources ≈ patients × resources_per_patient
Device peak >> FHIR write budget → aggregate
Audit volume ≥ PHI access rate
AI: retrieve min necessary, not whole record
```

### Appendix F — SMART / scopes (phase talk track)

```text
patient/Observation.read
patient/DocumentReference.read
user/Patient.read
launch offline_access ...
Map SMART scopes into PDP categories
```

### Appendix G — Notification copy rules

```text
OK:  "You have a new lab result."
BAD: "Your HbA1c is 9.2%."
OK:  "A clinic requested access."
BAD: Attach clinical PDF in email
```

### Appendix H — AI system prompt principles

```text
- Not a doctor; encourage professional care
- Cite resource ids
- Refuse when data missing
- Treat notes as untrusted for instructions
- No requests to external tools without policy
```

### Appendix I — Interview whiteboard order

1. Personas + trust boundaries  
2. Consent model  
3. FHIR SoR + BFF  
4. Audit + encryption  
5. Ingest  
6. AI leash  
7. Residency cells  

### Appendix J — MVP screen list

1. Login / MFA  
2. Timeline  
3. Add vitals  
4. Documents  
5. Sharing & consent  
6. Access history  
7. Export  
8. Settings (AI opt-in, residency info)  

---

*End of design doc. Open with trust boundaries + consent; whiteboard §4; close with AI/PHI deal-breakers §5.12 and traps §7.*
