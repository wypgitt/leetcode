# System Design: Secure Client–Server Data Exchange

> **Focus areas:** TLS · AuthN/AuthZ · Optional E2E encryption · Key management · Threat model · Privacy · Session security  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Explicit trust boundaries, threat-model-driven controls, honest E2E vs TLS-only tradeoffs, key lifecycle, no crypto handwaving  
> **Interview theme:** Google L5+ security-leaning design — protect data in transit/at rest/in use with scalable auth and privacy

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

Goal: **bound the product**—a **secure client/server data exchange** platform: clients (mobile/web/IoT) exchange sensitive data with backend services under a clear **threat model**, using **TLS**, strong **authentication/authorization**, optional **E2E encryption**, **key management**, auditability, and privacy controls—at progressive QPS and key volume.

### 1.0 What this is / is not

| Dimension | **Secure data exchange (this doc)** | Not this |
|-----------|-------------------------------------|----------|
| Primary job | Confidentiality, integrity, authZ for client↔server data | Full Zero Trust enterprise mesh product pitch |
| Success | Threats mitigated with measurable controls | “Military grade” buzzwords without model |
| Crypto | TLS everywhere; E2E optional for sensitive fields | Invent new public-key scheme in interview |
| Identity | Users + devices + services | Physical access badges |
| Privacy | Minimization, purpose limits, audit | Full compliance legal opinion |

**Scope statement:** Design secure client–server data exchange with TLS, authn/authz, optional E2E, KMS/key lifecycle, and an explicit threat model—scaling through 10× / 100× / 1,000×.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | What data? | User documents/messages/ Panels with PII | Classification tiers |
| F2 | Clients? | Mobile + web; maybe IoT | Cert pinning / WebPKI |
| F3 | AuthN? | OAuth2/OIDC + MFA optional; device identity | Token service; refresh |
| F4 | AuthZ? | RBAC/ABAC on resources | Policy engine |
| F5 | E2E needed? | Optional for highest tier; server processing needs plaintext sometimes | Split tiers |
| F6 | Key mgmt? | Cloud KMS + app-level DEKs | Envelope encryption |
| F7 | Audit? | Who accessed what | Immutable audit log |
| F8 | Sharing? | Share with users/groups | Capability links / ACLs |
| F9 | Offline? | Mobile cache encrypted at rest | Device keystore |
| F10 | Compliance hooks? | Encryption, retention, delete | Crypto-shredding |
| F11 | Abuse? | Rate limits, anomaly | Edge + risk engine |
| F12 | Admin break-glass? | Controlled, audited | Dual control |

**MVP functional scope:**

1. Mutual security baseline: TLS 1.3 in transit; encrypt sensitive data at rest (envelope).  
2. User AuthN (OIDC), short-lived access tokens, refresh token rotation.  
3. AuthZ checks on every resource operation (deny-by-default).  
4. Optional E2E for “vault” objects where server stores ciphertext only.  
5. KMS-backed key hierarchy (KEK/DEK); rotation.  
6. Audit logs for auth and data access.  
7. Client secure storage; certificate transparency / pinning policy for mobile.  
8. Rate limiting + basic bot/risk signals.

**Out of MVP:**

- Homomorphic encryption for arbitrary server compute  
- Novel post-quantum migration complete (mention hybrid readiness)  
- Full confidential computing fleet (TEE hooks Phase 2)  
- Custom blockchain ledger

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Transit security | Modern TLS | TLS 1.3; AEAD; no TLS<1.2 |
| N2 | Auth latency | Invisible | p99 token validate < 5–10ms cached |
| N3 | Availability | Auth is critical path | 99.95% auth; graceful degrade reads |
| N4 | Key durability | No silent DEK loss | Multi-region KMS; backups of wrapped keys |
| N5 | Audit integrity | Tamper-evident | Append-only + hash chain / WORM |
| N6 | Privacy | Least data | Field-level crypto where needed |
| N7 | Rotation | Routine | DEK rewrap without re-encrypt storm plan |
| N8 | Scale | High QPS APIs | Edge terminate TLS; regional auth |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. User logs in (OIDC + MFA) → access token → upload document → envelope-encrypted at rest.  
2. User downloads → AuthZ allow → decrypt DEK via KMS → stream.  
3. User stores E2E note → client encrypts to recipients → server stores blob opaque.  
4. Key rotation job rewraps DEKs under new KEK.  
5. Share link with expiry + scope → recipient AuthZ.  
6. Logout / revoke → refresh tokens invalidated.  
7. Audit: admin investigates access to doc X.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Stolen refresh token | Rotation reuse detection → revoke family |
| TLS MITM with rogue CA (mobile) | Pinning / public key pin backup pins |
| KMS outage | Fail closed for decrypt; cached DEKs short TTL optional risk |
| User lost E2E key | Data unrecoverable unless escrow policy |
| Confused deputy | Audience-bound tokens; DPoP/mTLS for high risk |
| SSRF via URL fetch | Blocked; allowlist |
| Timing oracle on AuthZ | Constant-time denies where relevant; uniform errors |
| Clock skew JWT | Small skew window; prefer opaque tokens + introspect cache |
| GDPR delete | Delete DEKs (crypto shred) + blob GC |
| Insider DBA | Envelope crypto; audit; least privilege IAM |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Active clients | 5M | 50M | 500M | cell fabric |
| API QPS | 20K | 200K | 2M | 20M |
| AuthN QPS (token issue) | 2K | 20K | 200K | 2M |
| AuthZ checks/s | 20K | 200K | 2M | 20M |
| Encrypt/decrypt ops/s | 5K | 50K | 500K | 5M |
| Keys (DEKs) | 50M | 500M | 5B | hierarchical |
| Audit events/s | 30K | 300K | 3M | stream tiering |
| E2E messages/day | 10M | 100M | 1B | optional path |

**What each jump forces:**

- **10×:** Token cache; KMS envelope with local DEK cache; regional TLS terminators.  
- **100×:** Auth cells; policy decision cache; KMS throughput planning; audit pipeline.  
- **1,000×:** Edge authz for coarse checks; hierarchical keys; confidential compute optional; global CRL/revoke fabric.

### 1.5 Etc. (Constraints & Assumptions)

- Server is trusted for non-E2E data (TLS + at-rest + IAM) — state this explicitly.  
- E2E path: server **untrusted for confidentiality** of ciphertext payloads.  
- Use standard algorithms: AES-GCM, XChaCha20-Poly1305, X25519/RSA-OAEP as appropriate — no homemade ciphers.  
- Compliance is control mapping, not a substitute for threat modeling.

**Scope statement to repeat back:**

> Design a secure client–server data exchange system with TLS 1.3, OIDC authn, deny-by-default authz, KMS envelope encryption at rest, optional client-side E2E for vault-tier objects, key rotation, and tamper-evident audit—scaled via caching, regional cells, and clear trust boundaries.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Baseline | Plane |
|-------|------|----------|-------|
| **TLS handshakes** | New conns | bursty; session tickets help | Edge/L7 |
| **API data plane** | CRUD | 20K/s | App |
| **Token issue/refresh** | Auth | 2K/s | IdP |
| **Token validate** | Every request | 20K/s | Local JWT/JWKS or introspect cache |
| **KMS unwrap** | Per DEK miss | << encrypt ops with cache | KMS |
| **Audit produce** | Per request | ~1× API | Log pipeline |

### 2.2 Crypto cost intuition

```text
AES-GCM throughput on modern CPU >> typical API body sizes
Bottleneck rarely raw AES; often KMS RTT + authz + storage
DEK cache hit rate critical: 99% hit → KMS QPS = 1% of decrypts
5K decrypts/s × 1% = 50 KMS unwraps/s — comfortable
Miss storm after rotation flush → protect with soft TTL + singleflight
```

### 2.3 Token size & header overhead

```text
JWT 1–2 KB on every request can hurt
Prefer opaque access tokens or compact JWTs; cache validation
```

### 2.4 Audit volume

```text
30K events/s × 500 B = 15 MB/s ≈ 1.3 TB/day
Need cheap object store tiers + indexed metadata hot store
```

### 2.5 E2E key fanout

```text
Share vault item to 50 devices: encrypt DEK to 50 device public keys
or encrypt DEK to group key — group key management complexity
```

---

## 3. High-Level Design

### 3.1 Trust boundaries

```text
[Client device] --TLS-- [Edge] --mTLS-- [Services] --IAM-- [KMS/Storage]
     |                                         |
   Secure Enclave/Keystore                 Audit Log (WORM)

E2E vault path: plaintext never leaves client; server sees ciphertext + metadata
```

**Explicit trust:**

| Tier | Server can read plaintext? |
|------|----------------------------|
| Standard data | Yes (after AuthZ) |
| Vault E2E | No |
| Metadata (filenames optional) | Policy-dependent |

### 3.2 API (representative)

| Op | Semantics |
|----|-----------|
| `POST /oauth/token` | Issue/refresh tokens |
| `POST /v1/objects` | Upload (server-side encrypt) |
| `GET /v1/objects/{id}` | Download if AuthZ |
| `POST /v1/vault/objects` | Upload opaque E2E ciphertext |
| `POST /v1/vault/objects/{id}/share` | Add recipient wrappers |
| `POST /v1/keys/rotate` | Control plane |
| `GET /v1/audit` | Admin query |

### 3.3 Authentication design

| Mechanism | Use |
|-----------|-----|
| OIDC authorization code + PKCE | Web/mobile users |
| MFA (WebAuthn/TOTP) | Step-up for sensitive |
| Refresh token rotation | Long-lived sessions |
| mTLS / device attestation | High-assurance devices |
| Service identity (SPIFFE/GCP SA) | Service-to-service |

Access token: short TTL (5–15 min). Validate via JWKS (asymmetric) with local cache, or opaque + introspect cache.

### 3.4 Authorization design

```text
Request → Authenticate principal → load policy → Decision(allow/deny)
Attributes: user, groups, resource owner, sensitivity label, device posture, time
Deny by default
```

Patterns: RBAC for coarse; ABAC/ReBAC (Google Zanzibar-style) for sharing graphs at 100×.

### 3.5 Encryption architecture

#### In transit

- TLS 1.3; modern cipher suites; HSTS; OCSP stapling.  
- Mobile: certificate pinning with backup pins + forced upgrade channel.  
- Internal: mTLS service mesh.

#### At rest (server-trusted tier)

```text
Envelope encryption:
  DEK = random AES-256 key per object (or per user partition)
  ciphertext = AES-GCM(DEK, plaintext, aad=object_id)
  wrapped = KMS_Encrypt(KEK, DEK)
  store {ciphertext, wrapped_dek, kek_id, nonce}
```

#### E2E vault tier

```text
Client:
  DEK = random
  ct = AEAD(DEK, plaintext)
  for each recipient device:
    wrap DEK with recipient public key (or group key)
  upload {ct, wraps[], aad}
Server: store opaque; never sees DEK
```

### 3.6 Key management

| Key | Stored | Purpose |
|-----|--------|---------|
| KEK | KMS HSM | Wrap DEKs |
| DEK | Wrapped in DB | Data encrypt |
| Client identity keys | Device keystore | E2E |
| Token signing keys | KMS / JWKS | JWT |
| Audit signing | KMS | Tamper evidence |

**Rotation:**

1. Create new KEK version.  
2. Rewrap DEKs lazily on read or batch job.  
3. Retire old KEK after rewrap complete.  
4. Token signing keys: overlap JWKS `kid`s.

### 3.7 Why X over Y

| Decision | Choice | Why | Deal-breaker |
|----------|--------|-----|--------------|
| Transit | TLS 1.3 | Standard, hardware offload | Custom crypto over TCP |
| At rest | Envelope + KMS | Scale + rotation | One global AES key in app config |
| AuthN | OIDC + short AT | Federated, revocable | Long-lived JWTs 1y in localStorage |
| E2E | Optional tier | Server features vs privacy | Claiming E2E while server ranks plaintext |
| AuthZ | Central policy | Consistent deny default | “check user_id in query string only” |
| Secrets | KMS/HSM | Audit + access control | Hardcoded keys in repo |

---

## 4. Architecture Diagram

```text
 +-------------+     TLS 1.3      +----------+     mTLS      +----------------+
 | Mobile/Web  | ---------------> | Edge/L7  | ------------> | API Gateway    |
 | (keystore)  |                  | WAF/RL   |               +---+-----+------+
 +------+------+                  +----------+                   |     |
        |                                                      AuthN   AuthZ
        | E2E encrypt locally                                    |     |
        v                                                        v     v
   Vault ciphertext                                      +-------+-----+----+
        |                                                | Data Exchange    |
        v                                                | Service          |
 +------+------+     wrapped DEKs                        +--+--------+-----+
 | Object Store|<-------------------------------------------|        |
 +-------------+                                         encrypt     |
        ^                                                /decrypt    v
        |                                         +------+----+  +---+---+
        |                                         | KMS/HSM   |  | Policy|
        |                                         +-----------+  +-------+
        |                                                ^
 +------+------+     hash-chained                        |
 | Audit Log   |<----- access events --------------------+
 | (WORM)      |
 +-------------+

 IdP / OIDC  ---> Token Service ---> JWKS
 Risk Engine ---> step-up MFA / block
```

**Server-side encrypt upload:**

```text
AuthN → AuthZ(create) → generate DEK → AES-GCM encrypt → KMS wrap DEK
 → store object → audit → return id
```

**E2E upload:**

```text
Client encrypt → POST ciphertext+wraps → AuthZ(store) → store opaque → audit metadata only
```

**Download:**

```text
AuthN → AuthZ(read) → fetch → KMS unwrap DEK (cache) → decrypt stream → audit
E2E: return ciphertext+wrap for device; client unwraps
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Invariants

1. **No plaintext on the wire** outside TLS (and E2E ciphertext is still over TLS).  
2. **Deny-by-default AuthZ** on every data plane call.  
3. **DEKs never stored raw** in DB/logs.  
4. **Fail closed** on KMS/AuthZ failure for decrypt/sensitive ops.  
5. **Refresh rotation reuse** triggers global revoke of token family.  
6. **Audit best-effort sync ≠ silent skip** — buffer durable.

#### 5.1.2 Threat model (STRIDE-ish)

| Threat | Example | Control |
|--------|---------|---------|
| Spoofing | Stolen password | MFA, device bind, anomaly |
| Tampering | Modified body | TLS AEAD; app-level signatures optional |
| Repudiation | “I didn’t access” | Audit with identity |
| Info disclosure | DB dump | Envelope encryption; E2E tier |
| DoS | Token endpoint flood | Rate limit, anycast, CAPTCHA/risk |
| Elevation | IDOR | AuthZ on resource IDs; no trust client |

**Out of scope threats (state them):** nation-state with device implant; compromised client malware reading screen — mitigate via platform security, not app crypto alone.

#### 5.1.3 Session threats

| Attack | Mitigation |
|--------|------------|
| XSS token theft | HttpOnly secure cookies or memory; CSP; avoid long JWT in JS |
| CSRF | SameSite; anti-CSRF for cookie sessions |
| Replay | Short TTL; nonce/DPoP for high risk |
| Refresh theft | Rotate + reuse detection |
| MITM | TLS1.3 + pin |

#### 5.1.4 KMS failure modes

```text
KMS down:
  - Decrypt: fail closed (503)
  - Encrypt new: fail closed OR use cached data-key with strict TTL (document risk)
  - Reads of already-cached DEKs in app memory: policy-limited
```

### 5.2 Scalability

#### 5.2.1 AuthN/AuthZ path

| Technique | Effect |
|-----------|--------|
| Local JWT validate + JWKS cache | Removes IdP roundtrip |
| Opaque token + bloom/version | Fast revoke |
| Policy decision cache | `(principal, resource, action) → allow` short TTL |
| Zanzibar-style at 100× | Scaled ReBAC |

#### 5.2.2 KMS / DEK

- Per-object DEK vs per-user DEK tradeoff: per-object better crypto shred; more wraps.  
- Hierarchical: `KEK → user_KEK → DEK`.  
- Singleflight unwrap; negative cache on deny.

#### 5.2.3 Progressive scale

| Scale | Change |
|-------|--------|
| 10× | Edge TLS; JWKS cache; DEK cache; WAF |
| 100× | Regional IdP; ReBAC; audit stream; KMS quota mgmt |
| 1,000× | Edge coarse authz; key hierarchy; TEE for server-side sensitive compute |

### 5.3 Maintainability

- Crypto in vetted libraries only (Tink / libsodium / BoringSSL).  
- Central “crypto service” vs library: prefer **Tink-style** in clients + servers.  
- Version algorithms in headers (`kid`, `enc_v`).  
- Regular rotation drills; chaos on KMS latency.  
- Security reviews on new data fields (classification).

### 5.4 Privacy

| Control | Mechanism |
|---------|-----------|
| Minimization | Don’t collect; tokenize |
| Purpose limitation | AuthZ scopes (OAuth) |
| Access transparency | User-visible logs Phase 1.5 |
| Deletion | Crypto shred DEK + GC |
| Field-level encryption | PII columns separate DEK |
| Differential retention | Vault vs standard TTLs |

### 5.5 Optional TEE / confidential compute (Phase 2)

For server processing on sensitive data without broad operator access: attest enclaves, seal keys to enclave measurements. Honest caveat: side channels + complexity; not MVP.

### 5.6 Abuse & border security

- WAF, bot management, credential stuffing detection.  
- Per-user and per-IP rate limits.  
- Anomaly: impossible travel, new device → step-up.  
- Export controls on crypto where legally relevant (engineering awareness).

---

## 6. Wrap-Up

### 6.1 Design summary

Secure exchange = **TLS everywhere** + **strong identity** + **deny-default AuthZ** + **KMS envelope at rest** + **optional E2E vault tier** + **tamper-evident audit**, with caches for tokens/DEKs/policy so crypto and auth don’t become the bottleneck.

### 6.2 Key tradeoffs

| Tradeoff | Pick | Cost |
|----------|------|------|
| Server features vs E2E | Tiered data | Two product modes |
| JWT vs opaque | Hybrid/short JWT | Revoke complexity |
| Per-object DEK | Finer shred | More KMS |
| Pinning | Strong MITM defense | Pin rotation ops |

### 6.3 Deal-breakers

1. Rolling your own TLS/crypto protocol.  
2. Long-lived bearer tokens in localStorage without rotation.  
3. Single static AES key in config.  
4. Claiming E2E while server needs plaintext for the same payload.  
5. AuthZ only on UI, not API.  
6. Logging plaintext PII / DEKs.

### 6.4 Progressive scale one-liner

**Baseline:** TLS + OIDC + envelope → **10×:** caches → **100×:** ReBAC + regional auth + audit pipeline → **1,000×:** edge authz + hierarchical keys (+ TEE optional).

### 6.5 Interview closing line

> “We threat-model first: TLS and IAM protect server-trusted data with KMS envelope encryption; vault-tier objects are E2E so the server only stores ciphertext; short-lived tokens, deny-default authz, and audited key operations keep the system honest at scale.”

---

## 7. Deeper / Related Interview Questions

### 7.1 Threat modeling

**Q1: What’s your trust boundary?**  
A: Device keystore; edge; services; KMS; storage. State what each can see.

**Q2: Is the server trusted?**  
A: For standard tier yes; for E2E vault no for confidentiality.

**Q3: Top 3 risks?**  
A: Stolen refresh tokens; IDOR; insider DB access — address each.

**Q4: Nation-state MITM?**  
A: Public CA risk mitigated by pinning/CT; endpoint compromise different class.

**Q5: Malicious client?**  
A: AuthZ still enforced server-side; E2E can’t stop sender leaking.

### 7.2 TLS & transport

**Q6: Why TLS 1.3?**  
A: Faster handshake, removed legacy ciphers, forward secrecy by default.

**Q7: Certificate pinning tradeoffs?**  
A: Stronger MITM resistance; must ship backup pins and update mechanism.

**Q8: Terminate TLS at edge?**  
A: Yes common; then mTLS inward; document plaintext on internal hop risk.

**Q9: gRPC vs HTTPS?**  
A: Both TLS; gRPC good for internal; HTTP/JSON fine public.

**Q10: Perfect forward secrecy?**  
A: ECDHE in TLS 1.3; ephemeral session keys.

### 7.3 AuthN / sessions

**Q11: Why PKCE?**  
A: Stop auth code interception on public clients.

**Q12: Refresh rotation reuse detection?**  
A: If old refresh presented after rotate, steal suspected → revoke family.

**Q13: JWT vs session store?**  
A: JWT scalable validate; revoke harder — use short TTL + denylist/version.

**Q14: mTLS for users?**  
A: Rare; good for devices/services; combine with user tokens.

**Q15: Step-up auth?**  
A: Re-auth MFA for export/delete/share wide.

### 7.4 AuthZ

**Q16: RBAC vs ReBAC?**  
A: RBAC simple roles; ReBAC for document sharing graphs (Zanzibar).

**Q17: IDOR prevention?**  
A: Every ID looked up through AuthZ; no “sequential id ⇒ access”.

**Q18: Capability URLs?**  
A: Random unguessable tokens + expiry + scope; still audit.

**Q19: Policy-as-code?**  
A: Central engine; test policies; canary.

### 7.5 Encryption & KMS

**Q20: Why envelope encryption?**  
A: Local AES speed; KMS protects DEKs; rotation via rewrap.

**Q21: AES-GCM pitfalls?**  
A: Nonce reuse catastrophic; unique nonce per encrypt; AAD bind identity.

**Q22: Crypto shredding?**  
A: Delete DEK wraps ⇒ ciphertext useless; then GC blobs.

**Q23: Key rotation without downtime?**  
A: Dual `kid` accept; lazy rewrap.

**Q24: Client secrets in mobile apps?**  
A: No confidential client secret; use PKCE public client + device attestation optional.

**Q25: Where do E2E private keys live?**  
A: Hardware keystore / StrongBox / Secure Enclave; backups via user recovery key policy.

### 7.6 E2E specifics

**Q26: Can server search E2E data?**  
A: Not plaintext; need client-side search or blind indexes (leakage tradeoff).

**Q27: Multi-device?**  
A: Per-device keys + provisioning; or group key with careful membership changes.

**Q28: Escrow?**  
A: Enterprise optional recovery key split; consumer often no-recovery — product choice.

**Q29: Metadata leakage?**  
A: Sizes, timings, recipient lists — minimize and protect.

### 7.7 Audit & privacy

**Q30: Tamper-evident logs?**  
A: Hash chain + WORM storage + separate admin role.

**Q31: PII in logs?**  
A: Redact; tokenize; never log tokens/DEKs/passwords.

**Q32: Right to delete?**  
A: Delete AuthZ edges + DEKs + schedule blob delete; verify.

### 7.8 Scale & ops

**Q33: KMS hotspot?**  
A: Cache DEKs; hierarchical KEKs; request quotas; regional KMS.

**Q34: Auth cell outage?**  
A: Regional IdP; short-lived tokens keep validating via JWKS cache until expiry.

**Q35: 2M AuthZ/s?**  
A: Decision cache; edge coarse filters; batch; Zanzibar caching.

### 7.9 Alternatives & deal-breakers

**Q36: Only IP allowlists?**  
A: Insufficient for mobile users; spoofable; not AuthZ.

**Q37: Password in DB unsalted?**  
A: Deal-breaker — use Argon2/bcrypt + IdP.

**Q38: Homegrown XOR “encryption”?**  
A: Instant fail.

**Q39: “We use blockchain for security”?**  
A: Not a substitute for TLS/IAM/KMS.

### 7.10 Interview craft

**Q40: How to open?**  
A: Assets, adversaries, trust boundaries → TLS/authn/authz/KMS/E2E tiers.

**Q41: What impresses L5+?**  
A: Explicit server-trusted vs E2E; refresh reuse detection; envelope rotation; IDOR story.

**Q42: Common mistake?**  
A: Equating HTTPS alone with “secure system” (missing AuthZ/at-rest/key management).

---

### Appendix A — Envelope encrypt pseudocode

```text
def store(plaintext, object_id, principal):
  authorize(principal, CREATE, object_id)
  dek = random_bytes(32)
  nonce = random_bytes(12)
  ct = aes_gcm_encrypt(dek, nonce, plaintext, aad=object_id)
  wrapped = kms.encrypt(KEK_ID, dek)
  db.put(object_id, ct, nonce, wrapped, KEK_ID)
  audit(principal, STORE, object_id)
```

### Appendix B — Envelope decrypt

```text
def load(object_id, principal):
  authorize(principal, READ, object_id)
  row = db.get(object_id)
  dek = dek_cache.get(row.wrapped) or kms.decrypt(row.wrapped)
  return aes_gcm_decrypt(dek, row.nonce, row.ct, aad=object_id)
```

### Appendix C — E2E share

```text
def share(object_ct, dek, recipient_pubs):
  wraps = [seal(pub, dek) for pub in recipient_pubs]
  return {object_ct, wraps}
```

### Appendix D — Refresh rotation

```text
on refresh(old):
  if old.reused: revoke_family(old.family_id); deny
  if old.valid:
    mark_used(old)
    return new_access, new_refresh(family_id)
```

### Appendix E — AuthZ middleware

```text
principal = authenticate(req)
decision = policy.check(principal, action, resource, ctx)
if decision != ALLOW: audit(deny); return 403
proceed(); audit(allow)
```

### Appendix F — Token validation cache

```text
JWKS cache TTL 10m; refresh on unknown kid
local JWT verify signature + exp + aud + iss
optional denylist version check
```

### Appendix G — Key hierarchy

```text
Root KEK (HSM)
  -> App KEK versions
      -> per-user wrapped UserKEK
          -> per-object DEK
```

### Appendix H — Classification tiers

| Tier | Transit | Rest | Server plaintext |
|------|---------|------|------------------|
| Public | TLS | Optional | Y |
| Sensitive | TLS | Envelope | Y |
| Vault | TLS | Client E2E | N |

### Appendix I — STRIDE checklist card

```text
S: MFA + device
T: TLS + AEAD + integrity
R: Audit
I: Encrypt + AuthZ + minimize
D: Rate limit
E: AuthZ every call
```

### Appendix J — NFR card

```text
TLS1.3 only externally
AT TTL <= 15m
KMS fail closed decrypt
No DEK in logs
Deny-by-default AuthZ
Audit access to sensitive objects
```

### Appendix K — Mobile pinning policy

```text
pins = [current, backup]
on TLS fail due to pin: hard fail
update pins via signed config from app update / remote with authenticity
```

### Appendix L — Audit event

```text
AuditEvent {
  ts, actor, action, resource, result,
  ip, device_id, request_id, prev_hash
}
```

### Appendix M — Progressive scale table

| Scale | Auth | Keys | AuthZ | Audit |
|-------|------|------|-------|-------|
| Base | OIDC | KMS envelope | RBAC | DB log |
| 10× | JWKS cache | DEK cache | Policy cache | Stream |
| 100× | Regional IdP | Hierarchy | ReBAC | Tiered storage |
| 1,000× | Edge coarse | Cell KEKs | Distributed Zanzibar | Lake + WORM |

### Appendix N — Common pushbacks

| Pushback | Response |
|----------|----------|
| “HTTPS is enough” | AuthZ, at-rest, keys, abuse |
| “Put passwords in JWT” | Never |
| “E2E for everything” | Breaks server search/features |
| “Store DEK beside ciphertext unwrapped” | Defeats purpose |

### Appendix O — Glossary

| Term | Meaning |
|------|---------|
| KEK | Key-encryption key |
| DEK | Data-encryption key |
| Envelope encryption | Encrypt data with DEK; wrap DEK with KEK |
| OIDC | Identity layer on OAuth2 |
| ReBAC | Relationship-based access control |
| DPoP | Demonstrating proof-of-possession |
| Crypto shred | Delete keys to render data unrecoverable |

### Appendix P — Worked example

```text
20K API/s, 25% need decrypt → 5K unwrap-or-cache/s
99% DEK cache hit → 50 KMS/s
Audit 20–30K/s → Pub/Sub → cold storage
Token validate local crypto ~ microseconds + JWKS cache
```

### Appendix Q — Confused deputy / SSRF

```text
When server fetches user URL:
  deny link-local, metadata IP, internal CIDR
  authz independent of client-supplied role headers
```

### Appendix R — 30m interview checklist

1. Threat model + trust boundaries.  
2. TLS + OIDC + AuthZ + KMS envelope.  
3. Optional E2E tier honesty.  
4. Rotation, revoke, audit.  
5. Scale caches.  
6. Deal-breakers.

### Appendix S — Algorithm allowlist

```text
TLS: TLS_AES_128_GCM_SHA256 / TLS_AES_256_GCM_SHA384 / CHACHA20
AEAD: AES-256-GCM, XChaCha20-Poly1305
KEM/wrap: KMS-managed; E2E X25519 + AEAD wrap
Hash: SHA-256
Password: Argon2id (IdP)
```

### Appendix T — Break-glass

```text
Dual approval → temporary AuthZ capability → full audit → auto expire
Never permanent god-mode keys on laptops
```

### Appendix U — Related Google systems (conceptual)

| System | Relation |
|--------|----------|
| ALTS / TLS | Transport identity |
| KMS / Cloud HSM | KEKs |
| OAuth / Identity | AuthN |
| Zanzibar | AuthZ scale |
| Tink | Crypto hygiene |
| Confidential Computing | TEE Phase 2 |

### Appendix V — What changes at each scale

| Scale | Must add |
|-------|----------|
| 10× | Caches (token/DEK/policy), edge TLS |
| 100× | ReBAC, regional IdP, audit pipeline |
| 1,000× | Edge authz, key hierarchy, optional TEE |

---

*End of Secure Client–Server Data Exchange system design.*
