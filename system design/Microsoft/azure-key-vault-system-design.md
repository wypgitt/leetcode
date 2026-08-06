# System Design: Azure Key Vault–like Secrets Platform

> **Focus areas:** Secrets · Keys · Certificates · HSM · RBAC · Soft-delete · Purge protection · Regional isolation · Audit  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Security invariants explicit; crypto boundaries clear; never invent broken HSM shortcuts; deal-breakers for “just encrypt in Postgres”  
> **Interview theme:** Microsoft Azure — **Key Vault** as a regional, tenant-isolated control + data plane for secrets, keys, and certs  
> **Company flavor:** Entra ID RBAC/access policies, Managed Identity, HSM pools, soft-delete & purge protection, Azure Monitor/Purview audit, sovereign clouds

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

Goal: design an **Azure Key Vault–like** service: customers create vaults to store **secrets**, manage **cryptographic keys** (often in HSMs), and lifecycle **certificates**—with Entra ID authZ, soft-delete, purge protection, regional residency, and comprehensive audit.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Secure secret/key/cert custody + crypto ops | General database |
| Trust | HSM / key boundary; least privilege | App config service without crypto |
| Plane split | Control plane (ARM) vs data plane (vault ops) | Single undifferentiated API |
| Success | Confidentiality, integrity, availability, auditability | Lowest latency cache |
| Microsoft lens | Entra, RBAC, MI, regional Azure, compliance | Consumer password manager UX only |

**Scope statement:** Multi-tenant Key Vault service: vault resource, secrets/keys/certs, HSM-backed key ops, RBAC, soft-delete/purge protection, regional isolation, audit—at Azure public cloud scale.

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Object types? | Secrets, Keys, Certificates | Three object models + versioning |
| F2 | Secret ops? | Set/get/list/delete/recover | Encrypted storage; access logging |
| F3 | Key ops? | Create/import; encrypt/decrypt/sign/verify/wrap/unwrap | HSM or software KSP |
| F4 | Certs? | Create/import; auto-renew hooks; policy | Cert lifecycle + secret material |
| F5 | AuthN? | Entra ID tokens; Managed Identity | No vault-local users as primary |
| F6 | AuthZ? | RBAC on vault + data actions; legacy access policies | Enforce on every data plane call |
| F7 | Soft-delete? | Default on; recoverable window | Tombstones; recover APIs |
| F8 | Purge protection? | Optional; blocks purge until retention | Compliance |
| F9 | Versioning? | Every set creates version; get latest or versioned | Immutable versions |
| F10 | Networking? | Public endpoint + Private Link | Network isolation |
| F11 | HSM SKU? | Standard (software) vs Premium (HSM) | Capacity pools |
| F12 | Backup/restore? | Backup blob encrypted; restore to vault | Disaster recovery |
| F13 | Rotation? | Manual + event hooks for automation | Event Grid integration |
| F14 | Multi-region? | Vault is regional; optional soft-DR patterns | No transparent multi-master secrets |

**MVP functional scope:**

1. Create vault (regional ARM resource) with Entra tenant binding.  
2. RBAC (and/or access policies) for secrets/keys/certs actions.  
3. Secret set/get/list/delete with versions.  
4. Key create in software or HSM; encrypt/decrypt/sign.  
5. Soft-delete + recover; optional purge protection.  
6. Full data-plane audit logs.  
7. Managed Identity caller support.  
8. Soft networking controls (firewall / private endpoint hooks).

**Out of MVP:**

- Customer-managed HSM (Dedicated HSM) full design  
- Transparent cross-region active-active vault  
- Full ACME certificate authority product  
- Client-side SDK deep dive  
- Confidential computing attestation deep dive (mention)

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Confidentiality | Plaintext secrets never logged; keys in HSM boundary |
| N2 | Integrity | Versions immutable; signed audit |
| N3 | Availability | 99.99% data plane regional (Azure-class) |
| N4 | Latency | Secret get p99 tens of ms in-region; key ops higher OK |
| N5 | Durability | RPO≈0 within region; geo backup optional |
| N6 | AuthZ correctness | Fail closed; 100% |
| N7 | Audit | Every data plane access attributable |
| N8 | Isolation | Strict tenant + vault boundary |
| N9 | Soft-delete | Configurable retention (e.g. 7–90 days) |
| N10 | Compliance | SOC/ISO/FedRAMP postures; Purview hooks |

### 1.3 Cases

**Happy paths**

1. Admin creates vault → assigns RBAC to app MI → app gets secret.  
2. Create RSA key in Premium → app unwraps DEK.  
3. Rotate secret → new version; apps fetch latest.  
4. Delete secret → soft-deleted → recover within window.  
5. Purge protection on → purge rejected until expiry.  
6. Private Link: data plane only via VNet.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Caller lacks RBAC | 403; audit deny |
| Thundering herd get secret | Cache carefully with authZ; prefer app-side cache short TTL |
| HSM pool exhaustion | Throttle key ops; don't spill key material to software silently |
| Soft-deleted name reuse | Block until purge/recover |
| Backup stolen | Backup encrypted to Microsoft / customer key hierarchy |
| Region outage | Vault unavailable; restore from backup to alternate region (customer-driven) |
| Insider admin | Just-enough access; dual control for purge; audit |
| Clock skew | Token lifetime validate; not security via obscurity |
| Cert expire | Alert + auto-renew policy if configured |
| Key destroy with purge protection | Denied |

### 1.4 Progressive scale

| Metric | Base | 10× | 100× | 1,000× |
|--------|------|-----|------|--------|
| Vaults | 100K | 1M | 10M | 100M |
| Objects | 10M | 100M | 1B | 10B |
| Data-plane QPS (get) | 10K | 100K | 1M | 10M |
| Key ops QPS | 1K | 10K | 100K | 500K+ |
| HSM partitions | Few | Many pools | Regional fleets | Sovereign fleets |
| Regions | 2 | 10 | 40+ | + sovereign |
| Tenants | 10K | 100K | 1M | Multi-cloud |

**Jumps:** 10× = partition metadata + envelope encryption; 100× = HSM pool scheduling, private link scale; 1,000× = per-SKU isolation, extreme noisy-neighbor controls.

### 1.5 Scope repeat-back

> Azure Key Vault–like regional service: Entra-authenticated data plane for versioned secrets, HSM/software keys, and certificates; RBAC fail closed; soft-delete and purge protection; encrypted storage with key hierarchy; comprehensive audit—scaled via partitions and HSM pools. Not a general DB; not transparent multi-region multi-master.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Traffic math

```text
1M vaults, avg 5 secret gets/vault/min peak fraction online
Effective: 100K vaults active × 5/min ≈ 500K gets/min ≈ ~8.3K/s average
Peak 10× ⇒ ~80K/s secret gets

Key ops rarer but heavier (HSM latency 5–50ms+)
Premium SKU capacity planned in HSM partitions not CPU alone
```

### 2.2 Storage

```text
Secret blob ciphertext ~ 1–10 KB typical
10M secrets × 5 KB = 50 GB ciphertext (+ versions × N)
Metadata indexes: vault, name, version, ACLs → comparable or larger
HSM key objects: handles + metadata; material inside HSM
```

### 2.3 Key hierarchy (conceptual)

```text
Microsoft Root / Platform keys
  → Regional Key Vault Service KEKs
    → Per-vault encryption keys (VEK)
      → Per-secret DEK or direct wrap
HSM-backed customer keys never export raw outside boundary
```

### 2.4 Latency budget (secret get)

```text
Client → Front door → Data plane authN/Z → Metadata lookup →
Decrypt envelope → Response
Budget: 10 + 15 + 20 + 15 = ~60ms p50 in-region (cached authZ helps)
```

### 2.5 Bottlenecks

(1) AuthZ evaluation (2) Hot vaults (3) HSM queues (4) List operations abuse (5) Soft-delete GC (6) Audit pipeline volume.

### 2.6 Cost

HSM capacity expensive—don't use Premium for pure secret string storage. Encourage Standard for secrets; Premium for key ops. Aggressive app-side caching with rotation awareness reduces QPS bill.

---

## 3. High-Level Design

### 3.1 Planes (critical split)

| Plane | Responsibility | Notes |
|-------|----------------|-------|
| Control plane (ARM) | Create/update/delete vault resource, SKU, networking, purge protection flags | Azure Resource Manager |
| Data plane | Secret/key/cert CRUD + crypto ops | `*.vault.azure.net` style |
| Crypto / HSM | Key material & crypto primitives | FIPS boundary |
| Identity | Entra tokens, MI, RBAC | Fail closed |
| Audit / Monitor | Access logs, metrics, alerts | Immutable-ish |
| Backup | Encrypted export/restore | Customer initiated |

**Deal-breaker:** mixing control-plane Contributor with unconstrained data-plane secret get without RBAC nuance; or storing raw key material in the same DB as metadata without envelope/HSM story.

### 3.2 Components

1. **ARM RP (Resource Provider)** — vault resources, properties, locks.  
2. **Data Plane Gateway** — TLS termination, routing, throttle.  
3. **AuthN Filter** — validate Entra JWT / MI.  
4. **AuthZ Engine** — RBAC + access policies; deny by default.  
5. **Object Metadata Store** — vault/object/version indexes.  
6. **Encrypted Secret Store** — ciphertext blobs.  
7. **Key Management Service** — software keys + HSM proxy.  
8. **HSM Pool Manager** — allocate partitions; health; failover.  
9. **Certificate Service** — policy, issuance hooks, renew.  
10. **Soft-Delete / GC** — retention timers; purge gates.  
11. **Audit Emitter** — Azure Monitor / Event Hub / Purview.  
12. **Private Link Service** — private endpoints.  
13. **Backup Service** — wrap backup packages.

### 3.3 Object model (sketch)

```text
Vault { vault_id, tenant_id, region, sku, soft_delete_retention,
        purge_protection, network_acls, rbac_enabled }

Secret { name, versions[]: { version, ciphertext_ref, content_type, tags, deleted } }
Key    { name, versions[]: { kty, key_ops, hsm_handle?, key_state } }
Cert   { name, policy, versions[]: { cert_cer, key_ref, secret_ref } }
```

### 3.4 Trade-offs

| Topic | Choice | Why | Deal-breaker |
|-------|--------|-----|--------------|
| Vault locality | Regional | Residency + blast radius | Global multi-master vault |
| AuthZ | Entra RBAC data actions | Azure consistency | Vault password as primary |
| Key material | HSM for Premium | Compliance | Exportable “HSM” keys |
| Secret read scale | App cache + short TTL | Cost | KV as every-request config DB blindly |
| Soft-delete default | On | Accidental delete recovery | Hard delete only |
| List secrets | Paginated; limited | Enumeration risk | Unbounded list |
| Backup | Customer-driven encrypted | Control | Transparent geo replicate plaintext |

### 3.5 Microsoft themes

| Theme | Implication |
|-------|-------------|
| Entra ID | Token `tid` must match vault tenant (with Azure Lighthouse exceptions carefully) |
| Managed Identity | First-class caller for apps/VMs/Functions/AKS |
| RBAC | `Key Vault Secrets User`, `Crypto User`, etc. |
| Purview / Defender | Sensitivity + threat detection integrations |
| Regional Azure | Data plane pinned; control plane ARM global |
| Sovereign clouds | Separate instances (Gov, China patterns) |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
[Azure Resource Manager] ---> [Key Vault Resource Provider]
                                      |
                                      v
                               [Vault Metadata]
                                      |
[App / MI / User] ---> [Data Plane Gateway]
                            |  AuthN (Entra)
                            v
                       [AuthZ Engine] ---> deny? audit + 403
                            |
            +---------------+---------------+
            v               v               v
      [Secret Svc]     [Key Svc]      [Cert Svc]
            |               |               |
            v               v               v
   [Encrypted Store]  [HSM Pool / KSP]  [Cert + Key + Secret refs]
            |
            v
      [Audit Pipeline] ---> Azure Monitor / Event Hub / Purview

[Private Link] ---> Data Plane Gateway (private)
[Backup Svc] <--> Encrypted packages (customer storage)
```

### 4.2 Secret get sequence

```text
1. GET /secrets/{name}?api-version=...
2. Validate bearer token (tid, aud, exp)
3. Resolve vault; check network ACLs / private link
4. Authorize dataAction Microsoft.KeyVault/vaults/secrets/getSecret/action
5. Load latest non-deleted version metadata
6. Fetch ciphertext; unwrap with VEK hierarchy
7. Return value; emit AuditSuccess (no plaintext in logs)
```

### 4.3 Key decrypt (HSM)

```text
1. POST /keys/{name}/decrypt
2. AuthZ key decrypt action
3. Resolve key version → HSM handle in pool P
4. Send cipher to HSM; plaintext/DEK returns to service memory briefly
5. Return to client over TLS; zeroize buffers
6. Audit key op (metadata only)
```

### 4.4 Soft-delete lifecycle

```text
ACTIVE --delete--> SOFT_DELETED --retention--> PURGEABLE --purge--> GONE
                     | recover ↑                 ^
                     +---------------------------+
If purge_protection: PURGEABLE blocked until retention end
```

### 4.5 Regional cell

```text
Region WestUS3
  Data plane cluster
  Metadata store replicas (AZ)
  HSM pool (Premium)
  Audit egress

No sync of secret plaintext to EastUS automatically
Customer backup/restore for DR
```

---

## 5. Design Deep Dive

### 5.1 Reliability & security invariants

1. **Fail closed authZ** — no token / no permission ⇒ deny.  
2. **Tenant match** — token tid aligns with vault tenant (documented exceptions only).  
3. **Plaintext never in logs/metrics**.  
4. **Key material never leaves HSM** for non-exportable keys.  
5. **Versions immutable** — rotation = new version.  
6. **Soft-delete recoverable** until purge.  
7. **Purge protection honored** even by subscription admins (Azure policy story).  
8. **ACK durability** for set operations with quorum.  
9. **Network controls enforced** before object access.  
10. **Audit every data plane access** including denies.  
11. **Zeroize** sensitive buffers after use.  
12. **No silent SKU downgrade** of HSM keys to software.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Regional cluster; Postgres/Cosmos metadata; software keys; 1 HSM partition |
| 10× | Shard vaults by vault_id; envelope encryption; cache authZ decisions briefly |
| 100× | HSM pools + scheduler; private link scale-out; list abuse shields |
| 1000× | SKU isolation; noisy neighbor throttles; sovereign fleets; automated rebalance |

**Hot vault mitigation:** per-vault QPS quotas; client caching guidance; read replicas for metadata; NOT replicating plaintext globally.

### 5.3 Maintainability

- API versioning (`api-version` query) disciplined.  
- RBAC action catalog versioned.  
- HSM firmware upgrades with dual-pool migrate.  
- Chaos: kill data plane pod—tokens still required on replay.  
- Canary regions for protocol changes.  
- Clear SEV taxonomy for suspected key compromise.

### 5.4 Progressive scale narrative

**1×:** Single region MVP; secrets + software keys; RBAC; soft-delete.  
**10×:** Premium HSM; Private Link; backup/restore; cert policies.  
**100×:** Massive multi-tenant partitions; Defender for Key Vault; automation at scale.  
**1000×:** Global Azure footprint; sovereign; extreme compliance regimes.

### 5.5 Envelope encryption deep dive

```text
SecretValue → generate DEK → encrypt value with DEK → wrap DEK with VEK
Store { wrapped_dek, ciphertext, alg }
VEK protected by regional service key (HSM)
Get: unwrap DEK → decrypt value → return → zeroize
```

Benefits: rewrap on VEK rotation without re-encrypting all customer values immediately (lazy), blast-radius control.

### 5.6 RBAC vs access policies

| Model | Pros | Cons |
|-------|------|------|
| Access policies (legacy) | Vault-local simplicity | Doesn't scale with Azure RBAC identity story |
| Azure RBAC | Unified IAM; MI-friendly | Role assignment propagation delay |
| Dual | Migration reality | Complexity—pick one per vault in design |

**Interview pick:** RBAC-first; mention access policies as legacy.

### 5.7 Soft-delete & purge protection

```text
delete(name):
  mark deleted_at; retain until now+retention
  name reserved

recover(name):
  if in soft-delete window: restore ACTIVE

purge(name):
  if purge_protection and now < retain_until: DENY
  else hard delete ciphertext + metadata
```

Legal/compliance: purge protection supports irreversible retention requirements against insider delete.

### 5.8 HSM pool management

```text
Pool P has partitions with capacity (ops/s, key slots)
Key create → schedule partition with affinity
Health check; fence bad partition
Failover: for HSM-backed keys, depends on HSM HA model
  (mirrored partitions / manufacturer HA)
Never "failover" by exporting key to software
```

### 5.9 Certificate lifecycle

```text
Cert Policy → create key (+HSM) → CSR → issue/import → store cert
Auto-renew: before expiry trigger; write new version; Event Grid notify apps
Apps must reload — KV cannot inject into process memory remotely
```

### 5.10 Backup / restore

```text
Backup: produce opaque encrypted blob (Microsoft-managed hierarchy)
Restore: only to same subscription/tenant geography rules
Stolen backup without Microsoft keys ≃ useless
Customer brings own key story (CMK) adds wrap layer
```

### 5.11 Networking

| Mode | Behavior |
|------|----------|
| Public + IP firewall | Allowlist |
| Deny public + Private Link | Private IP only |
| Trusted Microsoft services | Selective bypass exceptions |

Enforce **before** secret fetch.

### 5.12 Threat model highlights

| Threat | Mitigation |
|--------|------------|
| Stolen DB disk | Envelope encryption |
| Stolen token | Short TTL; CAE; MI; least privilege |
| Confused deputy | Audience checks; vault resource scope |
| Insider purge | Purge protection; PIM; audit |
| Side channel logs | Redaction; secure logging libs |
| Rollback attack | Version pins; app awareness |
| Cross-tenant | tid + vault id binding |

### 5.13 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Store secrets plaintext in SQL “because private VNet” | Disk/backup breach |
| Fake HSM (exportable keys labeled HSM) | Compliance fraud |
| Global multi-master secret sync | Consistency + residency breach |
| Skip audit on get for perf | Undetectable exfil |
| AuthZ cache without invalidate forever | Privilege ghost |
| Use KV as ultra-hot config at 1M QPS without cache | Melts; wrong tool |
| Allow purge with protection via backdoor | Compliance SEV |

### 5.14 Reliability: availability patterns

- AZ-redundant data plane + metadata.  
- Throttle over load-shedding with 429.  
- Dependency isolation: audit async with local durable buffer.  
- HSM outage: fail key ops; secret gets may still work if VEK available.  
- Regional loss: customer restore DR (document RTO).

### 5.15 Maintainability: API & SDK

- Strong api-version story.  
- Idempotent create with `If-None-Match` / recover semantics.  
- Clear error taxonomy: 401/403/404/409(name in soft-delete)/429.  
- Client retry guidance: exponential + respect Retry-After.

### 5.16 Managed Identity path

```text
Azure Function → IMDS → token aud=vault → data plane
No secret for credential itself (bootstrapping win)
RBAC assignment on vault scope to MI principalId
```

### 5.17 Rotation patterns

```text
1. Write secret version N+1
2. Event Grid → rotator / apps reload
3. Keep N for overlap window
4. Disable N when safe
Never require downtime if apps support latest version fetch
```

### 5.18 Soft-delete GC & storage reclamation

```text
GC job scans deleted_at < now - retention and purge_protection satisfied
Physically delete ciphertext
Emit audit Purge
Careful: name reuse allowed only after purge
```

---

## 6. Wrap-Up

### 6.1 Designed

Azure Key Vault–like platform: ARM control plane + regional data plane; versioned secrets/keys/certs; Entra RBAC; envelope encryption; HSM pools for Premium; soft-delete/purge protection; Private Link; audit—scaled by vault partitions and crypto capacity.

### 6.2 Decisions to defend

1. Plane split ARM vs data plane  
2. Entra RBAC fail closed  
3. Envelope encryption + HSM boundary  
4. Regional vault residency  
5. Soft-delete + purge protection  
6. Immutable versions  
7. Async audit with durability buffer  
8. Customer-driven geo DR via backup/restore  

### 6.3 Risks

- HSM capacity planning  
- AuthZ propagation delay confusion  
- Hot vaults / anti-patterns as config DB  
- Insider threats  
- Backup key hierarchy complexity  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Objects; planes; Entra |
| 5–15 | Secret get path + encryption hierarchy |
| 15–25 | Keys/HSM + RBAC |
| 25–35 | Soft-delete, purge, audit, network |
| 35–45 | Scale, DR, deal-breakers |

### 6.5 Closer

> **Azure Key Vault**: regional custody of secrets/keys/certs with Entra RBAC, HSM boundaries, soft-delete/purge protection, and auditable data plane—security invariants over naive multi-region sync.

---

## 7. Deeper / Related Interview Questions

### 7.1 Conceptual

1. Control plane vs data plane—why split?  
2. Explain envelope encryption in KV.  
3. Soft-delete vs purge protection.  
4. When Premium (HSM) vs Standard?  
5. How does Managed Identity call vault?  
6. Why are vaults regional?  
7. How do you prevent plaintext logging?  
8. RBAC vs access policies.  
9. How cert auto-renew notifies apps?  
10. What does backup confidentiality rely on?

### 7.2 Quantitative

11. Size storage for 500M secret versions × 4 KB.  
12. HSM pool: 20ms/op → max ops/s per single-threaded partition.  
13. AuthZ cache TTL trade-off math.  
14. Audit volume: 100K gets/s × 500 B metadata.  
15. Thundering herd after rotation event—mitigation sizing.

### 7.3 Security

16. Stolen metadata DB—what's exposed?  
17. Token replay defenses.  
18. Cross-tenant attack via resource ID guess.  
19. Insider with Contributor on RG—what can't they do with purge protection?  
20. Side-channel via timing on 403 vs 404 (existence oracle).

### 7.4 Ops

21. Region loss DR runbook.  
22. HSM firmware upgrade strategy.  
23. Detect anomalous secret get spikes (Defender).  
24. Break-glass access design.  
25. Migrating vault from access policies to RBAC.

### 7.5 Microsoft-flavored

26. Private Link data path.  
27. Azure Policy forcing purge protection.  
28. Integration with App Service / AKS CSI driver patterns.  
29. CMK vs Microsoft-managed keys.  
30. Sovereign cloud isolation.

### 7.6 Stretch

31. Design multi-region read cache without violating residency.  
32. Customer Lockbox-like dual control for support.  
33. Homomorphic or enclave-based secret compute (why usually not).  
34. Key Vault as CA for internal mTLS.  
35. Post-quantum algorithm migration plan.

---

## 8. Appendices

### Appendix A — Data plane API sketches

#### A.1 Set secret

```http
PUT https://{vault}.vault.azure.net/secrets/db-password?api-version=7.4
Authorization: Bearer {token}
{
  "value": "s3cr3t",
  "contentType": "text/plain",
  "tags": {"env": "prod"}
}
→ { "id": ".../secrets/db-password/version", "attributes": {"enabled": true} }
```

#### A.2 Get secret

```http
GET https://{vault}.vault.azure.net/secrets/db-password?api-version=7.4
→ { "value": "s3cr3t", "id": "...", "attributes": { ... } }
```

#### A.3 Key decrypt

```http
POST https://{vault}.vault.azure.net/keys/app-kek/decrypt?api-version=7.4
{
  "alg": "RSA-OAEP-256",
  "value": "<base64 cipher>"
}
```

#### A.4 Soft-delete recover

```http
POST .../deletedsecrets/db-password/recover?api-version=7.4
```

#### A.5 Purge

```http
DELETE .../deletedsecrets/db-password?api-version=7.4
→ 409/403 if purge protection active
```

### Appendix B — Control plane (ARM) sketch

```json
{
  "type": "Microsoft.KeyVault/vaults",
  "apiVersion": "2023-07-01",
  "name": "kv-contoso-prod",
  "location": "westus3",
  "properties": {
    "tenantId": "tid...",
    "sku": { "family": "A", "name": "premium" },
    "enableRbacAuthorization": true,
    "enableSoftDelete": true,
    "softDeleteRetentionInDays": 90,
    "enablePurgeProtection": true,
    "networkAcls": {
      "defaultAction": "Deny",
      "ipRules": [],
      "virtualNetworkRules": []
    }
  }
}
```

### Appendix C — Schemas

#### C.1 Vault metadata

```text
VaultRecord {
  vault_id: UUID
  arm_id: string
  tenant_id: UUID
  region: string
  sku: STANDARD | PREMIUM
  rbac_enabled: bool
  soft_delete_days: int
  purge_protection: bool
  network_acls: NetworkAcls
  created_at: ts
  vault_encryption_key_id: handle
}
```

#### C.2 Secret version

```text
SecretVersion {
  vault_id: UUID
  name: string
  version: UUID
  state: ACTIVE | SOFT_DELETED | PURGED
  ciphertext_ref: blob_id
  wrapped_dek: bytes
  alg: string
  content_type: string
  tags: map
  created_at: ts
  deleted_at: ts?
  recoverable_until: ts?
}
```

#### C.3 Key version

```text
KeyVersion {
  vault_id: UUID
  name: string
  version: UUID
  kty: RSA | EC | OCT
  key_ops: [encrypt, decrypt, sign, verify, wrapKey, unwrapKey]
  hsm_backed: bool
  hsm_partition: id?
  hsm_key_handle: handle?
  software_wrapped_key: bytes?   // standard only
  state: ENABLED | DISABLED | SOFT_DELETED
  created_at: ts
}
```

#### C.4 Audit event

```text
AuditEvent {
  ts: ts
  correlation_id: UUID
  vault_id: UUID
  tenant_id: UUID
  principal_oid: UUID
  action: string
  resource: string
  result: SUCCESS | DENY | ERROR
  network: { private_link: bool, ip?: string }
  // NEVER include secret value or raw key
}
```

### Appendix D — RBAC actions (sample)

| Role | Sample data actions |
|------|---------------------|
| Key Vault Administrator | All data plane |
| Key Vault Secrets Officer | Secrets CRUD |
| Key Vault Secrets User | get/list secrets |
| Key Vault Crypto Officer | Key management |
| Key Vault Crypto User | encrypt/decrypt/sign/verify |
| Key Vault Reader | metadata list only |

### Appendix E — AuthZ pseudocode

```text
function authorize(token, vault, action, resource):
  if !valid(token): return DENY
  if token.tid != vault.tenant_id and !lighthouse_allows(...): return DENY
  if !network_allows(caller, vault): return DENY
  if vault.rbac_enabled:
    if !rbac.allows(token.oid/appid, vault.arm_scope, action): return DENY
  else:
    if !access_policy.allows(token, action): return DENY
  return ALLOW
```

### Appendix F — Envelope encrypt/decrypt

```text
function putSecret(value):
  dek = random(256)
  ct = AEAD_encrypt(dek, value)
  wrapped = wrap(vek, dek)
  store(ct, wrapped)
  zeroize(dek, value)

function getSecret():
  (ct, wrapped) = load()
  dek = unwrap(vek, wrapped)
  value = AEAD_decrypt(dek, ct)
  zeroize(dek)
  return value
```

### Appendix G — Soft-delete state machine

```text
ACTIVE
  on delete → SOFT_DELETED(recoverable_until)
SOFT_DELETED
  on recover → ACTIVE
  on purge if allowed → PURGED
  on timer if purge_protection → still wait until recoverable_until
PURGED
  terminal; name free
```

### Appendix H — Rate limits (example)

| Op | Limit |
|----|-------|
| Secret get | Per vault + per principal quotas |
| Secret list | Stricter |
| Key create | Low |
| HSM decrypt | Partition capacity |
| Backup | Rare; expensive |

### Appendix I — Network ACL evaluation order

```text
1. Private endpoint path? → allow if linked
2. Public access disabled? → deny
3. IP / VNet rules
4. Trusted services exceptions
5. Else defaultAction
```

### Appendix J — HSM scheduling

```text
KeyCreate(premium):
  pick partition with free slots + lowest utilization
  generate non-exportable key
  persist handle mapping
  return key metadata (public parts only)
```

### Appendix K — Cert object relations

```text
Certificate version
  → Key version (private key)
  → Secret version (optional PEM export storage)
  → CER/PFX metadata
Policy drives renew
```

### Appendix L — SLO / error budget

| SLO | Target |
|-----|--------|
| Data plane availability | 99.99% |
| Secret get p99 | < 100–200ms in-region |
| AuthZ incorrect allow | 0 (SEV1) |
| Audit loss | ≈0 (buffered) |
| Silent HSM→software fallback | 0 |

### Appendix M — DR worksheet

```text
RPO regional: ______
RTO restore to alt region: ______
Backup frequency: ______
Purge protection impact on restore: ______
Who can initiate restore: ______
```

### Appendix N — Comparison: KV vs Config Store vs KMS

| System | Stores | Crypto ops | Typical use |
|--------|--------|------------|-------------|
| Key Vault | Secrets/keys/certs | Yes | App secrets + KEKs |
| App Configuration | App settings | No | Non-secret config |
| Managed HSM / Cloud KMS | Keys primarily | Yes | Central CMK |

### Appendix O — Noisy neighbor controls

- Per-tenant and per-vault QPS tokens  
- Separate Premium HSM pools  
- List operation cost multiplier  
- Admission control on create storms  

### Appendix P — Event Grid events (sample)

```text
Microsoft.KeyVault.SecretNewVersionCreated
Microsoft.KeyVault.SecretNearExpiry
Microsoft.KeyVault.KeyNearExpiry
Microsoft.KeyVault.CertificateNewVersionCreated
```

### Appendix Q — Threat model STRIDE (brief)

| STRIDE | Example | Control |
|--------|---------|---------|
| Spoofing | Fake MI | Entra token validation |
| Tampering | Ciphertext bit flip | AEAD |
| Repudiation | Deny get | Audit |
| Info disclosure | Log leak | Redaction; encryption |
| DoS | List bomb | Quotas |
| EoP | Role creep | Least privilege; PIM |

### Appendix R — Capacity worksheet

```text
Vaults = ______
Secrets/vault = ______
Get QPS peak = ______
Key ops QPS = ______
HSM ms/op = ______
HSM partitions needed ≈ key_ops / (1000/ms_per_op) = ______
Storage TB = ______
```

### Appendix S — Interview whiteboard script

```text
1. Clarify secrets vs keys vs certs
2. Draw ARM vs data plane
3. Secret get + envelope encryption
4. RBAC fail closed + MI
5. Soft-delete / purge protection
6. HSM boundary
7. Regional DR via backup
8. Deal-breakers
```

### Appendix T — Glossary

| Term | Meaning |
|------|---------|
| VEK | Vault encryption key |
| DEK | Data encryption key |
| HSM | Hardware security module |
| Soft-delete | Recoverable delete window |
| Purge protection | Blocks hard delete until retention ends |
| MI | Managed Identity |
| ARM | Azure Resource Manager |
| Private Link | Private connectivity to data plane |
| CMK | Customer-managed key |

### Appendix U — Explicit non-goals

1. Transparent multi-region active-active vault.  
2. Using KV as sub-millisecond global config mesh.  
3. Exportable Premium keys.  
4. Skipping audit for “health checks” that fetch secrets.  
5. Storing passwords with reversible logging for support.

### Appendix V — SEV taxonomy

| SEV | Example |
|-----|---------|
| SEV1 | Cross-tenant secret disclosure; HSM key export bug |
| SEV2 | Regional data plane outage |
| SEV3 | Elevated 429s; renew failures |
| SEV4 | Portal UX bug |

### Appendix W — Secure coding checklist (service)

- [ ] AEAD for secret ciphertext  
- [ ] Constant-time compare where needed  
- [ ] Memory zeroization helpers  
- [ ] No ToString on secret types  
- [ ] Structured logging allowlists  
- [ ] Fuzz data plane parsers  

### Appendix X — Related Azure services

- Entra ID / Managed Identity  
- Azure Monitor / Event Grid  
- Private Link  
- Azure Policy  
- Defender for Cloud  
- Managed HSM (sibling premium offering)  
- App Service Key Vault references  

### Appendix Y — Sample deny reasons

```text
Unauthorized
Forbidden (RBAC)
Forbidden (network)
Conflict (soft-deleted name exists)
Forbidden (purge protected)
TooManyRequests
Gone (purged)
```

### Appendix Z — Closing checklist

- [ ] Plane split stated  
- [ ] Envelope + HSM story  
- [ ] RBAC fail closed  
- [ ] Soft-delete/purge  
- [ ] Regional residency  
- [ ] Audit without plaintext  
- [ ] Deal-breakers named  

---

*End of Azure Key Vault–like system design prep doc.*
