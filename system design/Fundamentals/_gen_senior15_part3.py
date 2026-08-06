#!/usr/bin/env python3
"""Senior/staff system-design markdown generators — Part 3 (auth, RBAC, load shedding, k8s diagnosis, DB migration)."""
from __future__ import annotations

import sys
import types

# Allow importing helpers before _gen_senior15_docs is fully assembled.
if "_gen_senior15_docs" not in sys.modules:
    _stub = types.ModuleType("_gen_senior15_docs")
    _stub.ALL_DOCS = []
    sys.modules["_gen_senior15_docs"] = _stub

from _gen_senior15 import header, s1, s2, s3, s4, s5, s6, s7, s8


def _qs(pairs: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Ensure we always ship >=22 interview Q&As."""
    assert len(pairs) >= 22, len(pairs)
    return pairs


def doc_auth_session() -> str:
    t = header(
        "Authentication & Session Management",
        "login · MFA · sessions vs JWT · refresh/rotation · revocation · device sessions · SSO/OIDC · password hashing · brute-force · cookie security · global session store",
        "identity control plane — session correctness under theft, rotation, and multi-device scale",
    )
    t += s1(
        "design a production authentication and session management system: password/SSO login, MFA, durable sessions with rotation/revocation, device inventory, and API auth that survives sticky-session myths and token-theft reality.",
        [
            ("Job", "Authn + session lifecycle for web/mobile/API clients", "Full IAM product, HR directory, or fraud ML platform alone"),
            ("Sessions", "Server-side session store + optional JWT access tokens", "Pure stateless JWT forever with no revocation story"),
            ("Identity", "Local credentials + OIDC/SAML enterprise hooks", "Building a full IdP competing with Okta day one"),
            ("Security", "MFA, rotation, theft detection, cookie hardening", "Security theater without enforceable revocation"),
            ("Scale lens", "Logins/sec + active sessions + validation QPS", "Only counting registered users"),
        ],
        [
            ("Who authenticates?", "Humans (web/mobile) + first-party APIs; service-to-service deferred or mTLS separate", "Separate human session plane from machine auth"),
            ("Password login?", "Yes for consumer; enterprise may force SSO", "Argon2id/bcrypt; never plaintext; migration path for hash upgrades"),
            ("MFA?", "TOTP + WebAuthn preferred; SMS allowed as weaker factor", "Step-up MFA on sensitive actions; enrollment flows"),
            ("Session model?", "Opaque session id in HttpOnly cookie + server session record; short-lived JWT access optional for APIs", "Revocation and rotation are first-class"),
            ("Refresh?", "Refresh tokens rotating; reuse detection", "Family invalidation on theft signals"),
            ("SSO?", "OIDC authorization code + PKCE; SAML for legacy enterprise", "Account linking / JIT provisioning hooks"),
            ("Device sessions?", "List/revoke devices; trust signals (UA, IP, key binding)", "Session inventory UX"),
            ("Logout?", "Local + global logout; SSO logout best-effort", "Clear cookies + delete/deny session row"),
            ("Password reset?", "Time-limited single-use tokens; invalidate sessions on reset", "Email/SMS delivery async; rate-limit resets"),
            ("Brute force?", "Per-IP + per-account progressive delays / lockouts / CAPTCHA", "Do not lock forever without unlock path"),
            ("API clients?", "OAuth2 public+confidential clients; scopes", "Distinct from browser session cookies"),
            ("Multi-region?", "Global session validation; regional sticky optional", "Session store replication or cell routing"),
            ("Audit?", "Login success/fail, MFA, revoke, admin impersonation", "Immutable audit stream"),
            ("Compliance?", "SOC2/ISO; optional session encryption at rest", "PII minimization in logs"),
        ],
        [
            "Email/password register + login with Argon2id hashes",
            "Session create on login; HttpOnly Secure SameSite cookie",
            "Session validate on each request (gateway or auth middleware)",
            "Logout + password reset invalidating sessions",
            "Basic MFA (TOTP) enrollment and challenge",
            "Device session list + revoke",
            "Rate limits / lockout on auth endpoints",
            "Refresh token rotation for mobile/SPA refresh path",
            "OIDC login hook (one provider) with account link",
            "Metrics: login QPS, fail rate, session store latency, revoke lag",
        ],
        [
            "Full passwordless-only product",
            "Complete risk-based continuous auth ML",
            "Building Okta/Auth0 replacement admin suite",
            "Perfect global SSO logout across all IdPs",
            "Hardware HSM-backed every hash day one (nice later)",
        ],
        [
            ("Login latency", "p50 < 150ms; p99 < 400ms excl MFA user think-time", "Hash cost tuned; session write async-ok after durable ack"),
            ("Session validate", "p99 < 20–50ms including cache miss path budgeted", "Hot path must not hit primary DB every request"),
            ("Availability", "99.95%+ for validate; login can degrade with queueing", "Fail closed for authz; careful fail-open never for money paths"),
            ("Durability", "Acked session create survives AZ loss", "RPO≈0 for session rows in region"),
            ("Revocation lag", "< 1–5s global for hard revoke; document SLO", "Cache TTLs bounded by revoke SLO"),
            ("Consistency", "Read-your-writes after login on same region", "Cross-region validate may be slightly stale within SLO"),
            ("Security", "TLS everywhere; cookie flags; CSRF for cookie sessions", "Threat model: XSS, token theft, fixation"),
            ("Multi-region", "Active-passive DR first; active-active session cells if needed", "Sticky user→cell or replicated session store"),
            ("Cost", "Session store memory dominates at huge active sessions", "TTL + idle timeout; compress session payloads"),
            ("Compliance", "Audit retention 1y+; encrypt secrets/KMS", "No passwords in logs ever"),
        ],
        [
            "Register → verify email → login → MFA → session cookie → API calls → refresh → logout",
            "SSO OIDC → callback → link/create user → session",
            "Password reset → invalidate sessions → force re-login",
            "Admin revoke user sessions after compromise",
        ],
        [
            ("Credential stuffing", "Per-account + IP limits; breached-password check; MFA encourage"),
            ("Session fixation", "Rotate session id on privilege elevation / login"),
            ("XSS steals token", "HttpOnly cookie; CSP; short access JWT TTL if used"),
            ("Refresh token reuse", "Detect reuse → revoke token family"),
            ("Clock skew JWT", "Reject outside leeway; prefer opaque sessions for browsers"),
            ("Session store outage", "Degrade: reject new logins; optionally short emergency read-only JWT with tight TTL if pre-issued — document risk"),
            ("MFA device lost", "Recovery codes; support attested reset"),
            ("Cookie blocked", "Mobile native uses secure storage + refresh; not third-party cookies"),
            ("Duplicate login storm", "Idempotent session create; device cap e.g. 20 sessions"),
            ("SSO IdP down", "Show clear error; allow local login if policy permits"),
            ("Password hash upgrade", "Rehash on successful login transparently"),
            ("CSRF on cookie auth", "SameSite=Lax/Strict + CSRF token for state-changing"),
            ("Impersonation", "Separate audit session; time-boxed; dual control"),
            ("Logout race", "Delete session id; caches invalidated; idempotent logout"),
        ],
        [
            ("Logins / sec peak", "500", "5K", "50K", "500K"),
            ("Active sessions", "5M", "50M", "500M", "5B"),
            ("Session validates / sec", "50K", "500K", "5M", "50M"),
            ("Users", "10M", "100M", "1B", "1B+"),
            ("MFA challenges / sec", "50", "500", "5K", "50K"),
            ("Devices / user avg", "2", "2.5", "3", "3+"),
            ("Session TTL", "30d idle", "14–30d", "7–30d tuned", "policy-driven"),
            ("Revoke fanout targets", "1 region", "3 regions", "global edge", "global edge + cells"),
        ],
        "10×: Redis/cluster session store + cache; abandon sticky LB sessions. 100×: shard sessions by session_id/user_id; regional cells; CDN not for sessions. 1,000×: cell architecture, careful JWT hybrid for edge validation with bloom/deny lists for revoke, hash offload, dedicated auth fleet.",
        [
            "Browser cookies ≠ mobile token storage — design both",
            "Never store password-equivalent in JWT forever without revoke plan",
            "MFA user-time excluded from API SLOs",
            "Session payload keep small; load profile elsewhere",
            "Assume XSS will happen; limit blast radius",
        ],
        "We are designing authentication and session management: secure login (password + SSO), MFA, server-backed sessions with rotation/revocation, device session control, and high-QPS validation — not a full CIAM marketing suite.",
    )
    t += s2(
        [
            (
                "Login QPS and hash CPU",
                """
Peak logins = 5K/s (10× mid-scale)
Argon2id ~50–100ms CPU on tuned params (or 20–50ms bcrypt 10–12)
CPU cores needed ≈ 5K × 0.05s = 250 cores busy at peak if naive
⇒ async worker pool / dedicated hash fleet; never block request threads unbounded
Cache negative? Careful — only rate-limit, do not cache "valid password"
""",
            ),
            (
                "Active session memory",
                """
Session record ~400–800 bytes (ids, user_id, device, issued, expiry, refresh family, IP hash)
50M sessions × 600B ≈ 30 GB raw; with Redis overhead ~50–80 GB cluster
5B sessions (1,000×) ⇒ multi-TB sharded; mandatory TTL + idle eviction
Hot validates: cache session digest in L1 (pod) + L2 Redis
""",
            ),
            (
                "Validation QPS",
                """
50K validates/s baseline; 5M/s at 100×
Redis GET ~100K–1M ops/s/node depending size; need cluster + local cache
Local cache TTL 5–30s conflicts with revoke SLO → use explicit invalidation pub/sub
or keep TTL ≤ revoke SLO (e.g. 2s) and size cache for hit rate
Hit rate target ≥ 95% for repeat APIs from same user
""",
            ),
            (
                "Cookie / token bandwidth",
                """
Session id 128-bit opaque → 22–43 char encoding; cookie header overhead small
If fat JWT 2–4KB on every request × 5M QPS = 10–20 GB/s header tax — avoid
Prefer opaque reference tokens for browsers
""",
            ),
            (
                "Refresh traffic",
                """
Mobile refresh every 15–60 min active; 50M MAU × 0.3 active × 24 refresh/day ≈ 360M/day ≈ 4K/s avg
Peaks 10×; rotation = delete+create; must be transactional enough to detect reuse
""",
            ),
            (
                "Audit log volume",
                """
Auth events: login, fail, mfa, refresh, revoke, reset
Assume 10 events / active user / day × 100M = 1B events/day
~200 bytes → 200 GB/day raw; ship to cheap object/columnar; index recent 7–30d hot
""",
            ),
            (
                "MFA TOTP verify",
                """
TOTP verify is cheap CPU; WebAuthn needs attestation path + challenge store
Challenge TTL 60–300s in session store; rate-limit attempts
SMS OTP: provider latency 1–10s; cost dominates; fraud risk high
""",
            ),
        ],
        """
1. **Session validate path** — if this is slow/down, entire product is down.
2. **Password hash CPU** — login floods / stuffing burn CPU; isolate and rate-limit.
3. **Revocation propagation** — security SLO; caches must obey.
4. **Refresh rotation races** — dual-tab / flaky mobile; correctness vs UX.
5. **SSO dependency** — enterprise login availability tied to IdP.
6. **Audit pipeline** — must not block login; still must not lose security events silently.
""",
    )
    t += s3(
        "Split **credential verification**, **session authority**, and **token issuance**. Browsers get opaque session cookies backed by a global session store; native/API clients get rotating refresh + short access tokens. Gateway validates sessions on the hot path via cache; security operations revoke by session_id, user_id, or device_id with bounded lag.",
        [
            "Edge / API Gateway — TLS, WAF, rate limits, cookie parse, CSRF checks",
            "Auth Service — register, login, MFA, reset, SSO callback",
            "Password Hasher — isolated pool (Argon2id); HSM optional later",
            "Session Service — create/get/touch/revoke; device inventory",
            "Session Store — Redis/cluster or Dynamo-like; TTL native",
            "Token Service — refresh rotation; optional JWT access mint/verify",
            "OIDC/SAML Broker — protocol adapters; account link",
            "Risk / Abuse — stuffing scores, impossible travel signals (hooks)",
            "User Directory — profile, credentials, MFA factors, status",
            "Audit Log Pipeline — durable security events",
            "Admin / Support Console — revoke, unlock, view sessions (audited)",
            "Key Management — cookie signing keys, JWT keys, rotation",
            "Notification — email/SMS for reset and MFA",
            "Policy Config — TTLs, MFA required, SSO enforced per tenant",
        ],
        """
POST /v1/auth/register {email, password} → user_id
POST /v1/auth/login {email, password, device} → Set-Cookie session / MFA challenge
POST /v1/auth/mfa/verify {challenge_id, code} → session
POST /v1/auth/logout
POST /v1/auth/password/reset/request {email}
POST /v1/auth/password/reset/confirm {token, new_password}
GET  /v1/sessions → [{session_id, device, last_seen, ...}]
DELETE /v1/sessions/{id}
DELETE /v1/sessions  (all)
POST /v1/oauth/token  (refresh) {refresh_token} → access + new refresh
GET  /v1/oauth/authorize  (OIDC)
POST /v1/oauth/callback
GET  /v1/internal/sessions/validate  (gateway) {sid} → user_id, scopes, exp
POST /v1/admin/users/{id}/revoke_sessions
""",
        """
User {user_id, email, pwd_hash, pwd_algo, status, created_at, ...}
MfaFactor {factor_id, user_id, type, secret_enc, verified_at}
Session {session_id, user_id, device_id, created_at, last_seen, expires_at,
         ip_hash, ua_hash, amr[], refresh_family_id, revoked_at?}
RefreshToken {token_hash, family_id, session_id, expires_at, rotated_from?, reused_at?}
Device {device_id, user_id, name, created_at, last_seen, trust_level}
OidcLink {user_id, issuer, subject}
AuthChallenge {challenge_id, user_id, type, expires_at, attempts}
AuditEvent {id, type, actor, target, ip, ts, meta}
""",
        [
            ("Browser session", "Opaque server session", "JWT-only", "Opaque — revoke & rotate naturally"),
            ("API access", "Short JWT + introspect fallback", "Opaque only", "JWT for scale if deny-list OK"),
            ("Session store", "Redis cluster", "SQL primary every validate", "Redis + async durability pattern"),
            ("Sticky LB", "Avoid for sessions", "Need sticky", "Global store beats sticky"),
            ("MFA default", "WebAuthn/TOTP", "SMS-only", "Prefer phishing-resistant"),
            ("Hash", "Argon2id", "MD5/SHA", "Argon2id/bcrypt only"),
            ("SSO", "OIDC code + PKCE", "Implicit flow", "Never implicit"),
            ("Refresh", "Rotate + reuse detect", "Long-lived static", "Rotate always for public clients"),
        ],
        [
            ("Stateless JWT for everything, 30d expiry, no store", "Cannot revoke theft quickly; fat tokens; secret sprawl"),
            ("Sticky sessions to app memory only", "LB failovers log everyone out; cannot scale horizontally cleanly"),
            ("Validate session hitting SQL primary every request", "DB melts at validate QPS"),
            ("Store JWT in localStorage as primary web auth", "XSS exfil trivial"),
            ("Disable refresh rotation for 'simplicity'", "Stolen refresh lasts forever"),
            ("Fail open when session store down", "Attackers love your outage"),
            ("Log passwords or session ids in plaintext", "Instant compliance + security failure"),
            ("SMS MFA as only factor for high-risk", "SIM swap reality"),
        ],
        "Authn issues **sessions as capability handles**; product APIs trust gateway validation. Keep password CPU and session IO on isolated paths so stuffing cannot melt the product fleet.",
    )
    t += s4(
        """
flowchart TB
  Client -->|TLS| Gateway
  Gateway -->|validate sid| SessionCache[(L1/L2 Session Cache)]
  SessionCache -->|miss| SessionSvc
  SessionSvc --> SessionStore[(Session Store)]
  Client -->|login/MFA/SSO| AuthSvc
  AuthSvc --> Hasher
  AuthSvc --> UserDir[(User Directory)]
  AuthSvc --> SessionSvc
  AuthSvc --> OIDC[OIDC/SAML Broker]
  OIDC --> ExtIdP[External IdP]
  AuthSvc --> Audit[(Audit Pipeline)]
  SessionSvc --> Audit
  TokenSvc --> SessionSvc
  Gateway -->|API| AppServices
  Admin --> SessionSvc
""",
        [
            (
                "Password login + MFA sequence",
                """
1. Client POST /login {email, password, device_attestation?}
2. AuthSvc loads user; rate-limit checks; Hasher verifies
3. If MFA required: create AuthChallenge; return mfa_required
4. Client POST /mfa/verify; AuthSvc verifies TOTP/WebAuthn
5. SessionSvc creates Session + optional Refresh family
6. Set-Cookie: session=<opaque>; HttpOnly; Secure; SameSite=Lax
7. Audit: login_success + amr factors
8. Subsequent API: Gateway extracts cookie → cache/store validate → inject user_id
""",
            ),
            (
                "Refresh rotation + reuse detection",
                """
1. Client POST /oauth/token {refresh_token}
2. TokenSvc hashes token; lookup RefreshToken row
3. If already rotated/reused: revoke entire family + all sessions in family; alert
4. Else: mark old rotated; mint new refresh + access; update session last_seen
5. Return tokens; client drops old refresh
""",
            ),
            (
                "Global revoke after compromise",
                """
1. Admin/user DELETE /sessions or password reset
2. SessionSvc sets revoked_at / deletes keys for user_id
3. Pub/sub invalidate to regional caches
4. Refresh families marked dead
5. Audit + notify user
6. Validate path fails closed within revoke SLO
""",
            ),
            (
                "OIDC authorization code + PKCE",
                """
1. Client → /oauth/authorize redirect to IdP with state+code_challenge
2. User authenticates at IdP; redirect back with code
3. Broker exchanges code+verifier; validates id_token
4. JIT provision or link OidcLink; create local session
5. Set session cookie; optional step-up MFA if policy
""",
            ),
        ],
    )
    t += s5(
        [
            "Session create durable before Set-Cookie ack; retries use login idempotency keys where possible.",
            "Refresh rotation compare-and-swap; reuse ⇒ family kill (theft signal).",
            "Password reset / credential change revokes all sessions by default.",
            "Rate-limit login, reset, MFA verify per account and IP; progressive delay.",
            "Session ids 128+ bit crypto random; never sequential.",
            "Cookie: Secure, HttpOnly, SameSite; __Host- prefix when applicable.",
            "CSRF tokens or double-submit for cookie-authenticated state changes.",
            "Fail closed on session store errors for authenticated routes.",
            "Key rotation for any signed JWTs; kid header; overlap windows.",
            "Audit pipeline buffered durable (Kafka/Kinesis); login not blocked on analytics warehouse.",
            "Device cap: revoke oldest idle when exceeding N sessions.",
            "Clock skew tolerance documented; prefer server session expiry over client JWT clocks when possible.",
        ],
        [
            ("1×", "Single region Redis + Postgres users; monolith auth; local cache optional"),
            ("10×", "Redis cluster; dedicated hash workers; gateway validate path; multi-AZ"),
            ("100×", "Shard sessions; regional cells with user affinity; pub/sub revoke; read replicas directory"),
            ("1,000×", "Cell architecture; edge deny-lists/bloom for revoked JWTs; auth fleet autoscale on login+validate; isolation from product deploys"),
        ],
        [
            "Feature flags for MFA required, SSO enforced, hash params.",
            "Canary auth service with replay of anonymized login traffic patterns.",
            "Session schema version field; tolerant readers.",
            "Dashboards: login success/fail, stuffing score, store p99, revoke lag, refresh reuse events.",
            "Runbooks: session store failover, key compromise, IdP outage.",
            "Privacy: hash IPs/UA in session; retention limits.",
            "Load tests: validate QPS and login hash storms separately.",
        ],
        [
            (
                "Sessions vs JWT (when to hybrid)",
                """
**Opaque server sessions** win for browser apps: revocation is delete-key; payload stays off the wire; fixation controls are straightforward.

**JWT access tokens** help service-to-service or mobile when validation must be local at many gateways. Keep TTL short (5–15 min). Pair with:
- rotating refresh tokens server-side
- revocation: denylist of `jti`/`sid` until TTL expires, or version `token_version` on user checked on sensitive paths
- small claims; no PII sprawl

**Deal:** long-lived unsigned-off JWT without revoke = staff-level reject.

Hybrid pattern: cookie session for web; JWT access for APIs minted from session; revoke session ⇒ deny mint + denylist sid.
""",
            ),
            (
                "Refresh rotation and multi-tab races",
                """
Naive rotate-on-use breaks when two tabs refresh simultaneously: tab A rotates, tab B presents old refresh → false theft detection → angry logout.

Mitigations:
1. **Grace reuse window** (e.g. 10–30s): accept previous refresh once if matches last rotated_from; still flag abnormal patterns.
2. **Refresh mutex** per family in store (SETNX) so concurrent refreshes serialize.
3. **Access token lifetime** long enough to reduce refresh frequency on web.

Document UX: "signed out everywhere" after true reuse outside grace.
""",
            ),
            (
                "Password hashing and stuffing defense",
                """
- Argon2id memory-hard params tuned to ~50–100ms on hash fleet hardware; store `algo|params|salt|hash`.
- On login success with legacy hash, rehash upgrade.
- Breached password detection (k-anonymity API or private bloom) on register/change.
- Stuffing: shared credential lists → per-account attempt counters in Redis with exponential backoff; CAPTCHA after N; optional IP reputation.
- Isolate hash workers with queue + timeout; return 503 with Retry-After under overload rather than melting k8s nodes.
""",
            ),
            (
                "Cookie security and CSRF",
                """
Session cookie attributes: `Secure; HttpOnly; SameSite=Lax` (Strict if UX allows); path=/; prefer `__Host-session` (no Domain, Secure, Path=/).

CSRF: SameSite reduces risk but not enough alone for all browsers/old clients. Use synchronizer token or signed double-submit cookie for POST/PUT/DELETE.

For SPAs: prefer BFF pattern (browser talks same-origin BFF; BFF holds session) over putting refresh tokens in JS-visible storage.
""",
            ),
            (
                "Multi-region session routing",
                """
Options:
1. **Replicated session store** (multi-region Redis/Dynamo global table): simple routing; conflict rare if session_id primary; higher cost/lag.
2. **User/session home cell**: login pins cell; cookie includes cell hint; cross-region users pay redirect.
3. **Regional sessions + central revoke log**: validates local-fast; revokes replicate via stream.

At 100× prefer cells with revoke stream. Measure revoke lag SLI religiously.
""",
            ),
            (
                "Gateway integration patterns",
                """
**Pattern A — Gateway RPC validate:** each request calls SessionSvc. Simple; needs aggressive caching.

**Pattern B — Gateway local cache + async revoke feed:** subscribe to revoke channel; keep bloom/id set of revoked sids; positive cache TTLs short.

**Pattern C — Signed session tickets:** store issues Macaroon/Fernet ticket embedding user_id+exp+sid; gateway verifies with public key; revocation still needs denylist until exp.

Staff expectation: pick one, state revoke lag, and show how CSRF/cookie parsing lives at the edge consistently across languages.
""",
            ),
            (
                "Step-up authentication",
                """
Sensitive operations (change email, add payment method, disable MFA) require recent MFA (`auth_time` within N minutes) or fresh WebAuthn.

Flow: API returns `403 step_up_required` with challenge_id → client completes MFA → session `amr` updated → retry with same idempotency key.

Do not mint a second parallel session for step-up if you can elevate the existing session with fixation-safe rotation of session id.
""",
            ),
            (
                "Observability for auth",
                """
Metrics: `login_attempts{result}`, `mfa_verify{result}`, `session_validate_latency`, `session_cache_hit`, `refresh_reuse_detected`, `revoke_lag_seconds`, `hash_queue_depth`.

Traces: login span should not include password; redact emails in low environments.

Alerts: spike in fail ratio; revoke lag SLO burn; refresh reuse; session store failover events; hash p99.

Fraud hooks: emit auth events to risk platform without blocking; allow risk to demand step-up asynchronously.
""",
            ),
        ],
    )
    t += s6(
        "A dual-path auth system: credential/MFA/SSO issuance into **revocable server sessions**, hot-path validation via cached session store, rotating refresh for native clients, and explicit abuse + audit controls.",
        [
            "Opaque sessions for browsers over eternal JWT",
            "Refresh rotation with reuse detection + grace for races",
            "Isolated password hash fleet and fail-closed validate",
            "Revoke SLO drives cache TTL/invalidation design",
            "OIDC code+PKCE only; no implicit",
            "Device session inventory as first-class UX/security",
        ],
        [
            "Session store outage ⇒ product auth outage (mitigate multi-AZ + DR drills)",
            "False-positive refresh reuse ⇒ mass logout (tune grace)",
            "IdP dependency for SSO-only tenants",
            "Hash param too heavy ⇒ login latency / cost",
            "Cache invalidate bugs ⇒ revoked sessions still accepted until TTL",
        ],
        [
            ("0–5", "Requirements: session vs JWT, MFA, SSO, revoke needs"),
            ("5–12", "BOTE: validate QPS, session memory, hash CPU"),
            ("12–25", "HLD components + cookie/token APIs"),
            ("25–35", "Deep: rotation, revoke, multi-region"),
            ("35–42", "Abuse, CSRF, deal-breakers"),
            ("42–45", "Wrap decisions + SLOs"),
        ],
        "If we cannot revoke a stolen session within our published SLO, we do not have session management — we have hopeful cryptography.",
    )
    t += s7(_qs([
        ("Why not store sessions only in JWT?",
         "JWTs push state to clients. Without a server denylist/version check you cannot revoke promptly after theft, password change, or admin lock. Fat JWTs also tax every request. Use short-lived JWTs at most, with server-side refresh/session authority."),
        ("Sticky load-balancer sessions: ever OK?",
         "Only as a temporary migration hack. Sticky sessions couple availability to a single instance, complicate deploys, and fail on node death. Prefer an external session store shared by all nodes."),
        ("HttpOnly cookie vs Authorization header?",
         "Cookies with HttpOnly reduce XSS exfil for web; need CSRF defenses. Authorization headers fit native/mobile and SPAs with careful token storage (preferably not localStorage). Many mature systems use BFF+cookie for web and header tokens for mobile."),
        ("How do you set Argon2 parameters?",
         "Target a latency budget (e.g. 50–100ms) on dedicated hardware; set memory/time/parallelism accordingly; store params with the hash; re-evaluate yearly as hardware changes; never weaken to fit shared request threads."),
        ("Refresh token reuse detection false positives?",
         "Concurrent tab refresh and flaky retries cause them. Use a short grace window accepting the previous token once, or a per-family lock. Outside grace, treat reuse as compromise and revoke the family."),
        ("SameSite=Strict vs Lax?",
         "Strict maximizes CSRF protection but breaks legitimate cross-site GET navigations that need cookies (return from payment provider). Lax is a common balance; still add CSRF tokens for state-changing requests."),
        ("How fast must revocation be?",
         "Threat-dependent. For known account takeover, seconds matter. Design cache TTL ≤ revoke SLO or push invalidations. Publish the SLO; do not claim 'instant' with 15-minute access JWTs and no denylist."),
        ("Session fixation: how prevented?",
         "Issue a new session id upon login and privilege elevation; bind session to user only after authentication; reject pre-login ids for authenticated use."),
        ("Should access tokens be stored in localStorage?",
         "Avoid for web: any XSS reads them. Prefer HttpOnly cookies via BFF, or in-memory tokens with short TTL plus refresh via HttpOnly cookie."),
        ("OIDC implicit flow?",
         "Deprecated. Use authorization code with PKCE for public clients. Implicit exposes tokens in URLs/logs/history."),
        ("How to handle session store failover?",
         "Multi-AZ Redis/Dynamo with automatic failover; app retries with jitter; during outage fail closed on authenticated APIs; keep login disabled or queued; status page. Practice game days."),
        ("MFA bypass risks?",
         "Recovery codes, support overrides, and 'remember device' are bypass paths. Audit them; rate-limit; require strong verification for recovery; time-box remember-device cookies."),
        ("SMS OTP: when acceptable?",
         "As a step up from password-only for low-risk, or fallback when WebAuthn/TOTP unavailable — never as sole factor for high-value accounts if avoidable. Prefer TOTP/WebAuthn."),
        ("How do you scale session validation to millions QPS?",
         "Local in-process cache + regional Redis cluster; minimize payload; shard by session_id; avoid synchronous cross-region on hot path; optionally embed integrity-checked cache entries with short TTL."),
        ("Password reset security properties?",
         "Single-use, short TTL, high entropy token; send to verified email/phone; on success revoke sessions and refresh families; rate-limit requests to prevent inbox flooding and enumeration tradeoffs (generic responses)."),
        ("What belongs in a session record?",
         "user_id, auth time, amr/acr, device_id, expiry, idle tracking, refresh family, security fingerprints (ip/ua hashes). Not full profile, not permissions dump (fetch/cache separately with their own invalidate)."),
        ("JWT kid and key rotation?",
         "Include kid; keep prior keys for verify during overlap; rotate signing key regularly; automate distribution to gateways; revoke compromised kids immediately."),
        ("How does SSO logout work?",
         "Local logout always. Front-channel/back-channel logout to IdP best-effort; you may not control all SPs. Document that SSO logout is eventual across enterprise apps."),
        ("Device binding / cryptographic session binding?",
         "WebAuthn/DPoP/mTLS can bind tokens to a key proof. Raises complexity; use for high-risk or phishing-resistant requirements. Soft binding via device id is weaker but useful for UX revoke lists."),
        ("How to test auth under stuffing attacks?",
         "Load-gen credential stuffing patterns; verify rate limits, hash fleet isolation, and that product read APIs stay healthy. Alert on fail/success ratio anomalies."),
        ("Cookie theft via XSS: residual risk?",
         "HttpOnly stops JS read, but attacker can still drive browser actions (CSRF-like) if CSRF weak, or exfil via other storage. Defense-in-depth: CSP, CSRF tokens, short idle timeouts, step-up MFA on sensitive ops."),
        ("Why separate amr in session?",
         "Authentication methods references let APIs demand step-up (e.g. payments require MFA recently). Store amr/acr and auth_time for policy decisions without re-login always."),
        ("Global vs regional session IDs?",
         "Use globally unique session_ids (UUIDv4/ULID). Routing hints can be separate cookies. Never assume sequential ids. Sharding uses hash(session_id)."),
        ("What is a staff-level deal-breaker answer?",
         "Claiming 'we use JWT so we are stateless and secure' without revocation, rotation, cookie security, and abuse controls. Call out revoke SLO and session store explicitly."),
        ("How do you migrate hashing algorithms?",
         "Store algo id with hash. On successful login with legacy algo, rehash with Argon2id in the same transaction as last_login update. Dual-verify only during migration window if needed. Force reset only if algo is catastrophically broken (e.g. unsalted MD5) and detection is uncertain."),
        ("Session idle vs absolute timeout?",
         "Idle timeout (e.g. 14d) from last_seen; absolute timeout (e.g. 90d) from created_at forces re-auth. Banking may use minutes idle. Touch last_seen asynchronously with write coalescing to protect store QPS."),
        ("How to handle concurrent logins from many devices?",
         "Allow up to N sessions; when N+1 created, revoke oldest idle (or require user to pick). Enterprise may enforce single session. Always show device list with last_seen and approximate location from IP geocode."),
        ("Why hash refresh tokens at rest?",
         "Store theft should not yield usable refresh tokens. Store SHA-256(token) or HMAC; present token is hashed then looked up. Same for password reset tokens."),
        ("Can CDN cache authenticated responses?",
         "Only with extreme care: cache keys must include auth variance or avoid caching personalized content at CDN. Prefer caching public assets; personalize via uncached API. Wrong CDN caching of Set-Cookie is catastrophic."),
    ]))
    t += s8(
        [
            (
                "SLO sketch",
                """
| SLI | SLO | Notes |
|-----|-----|-------|
| Session validate availability | 99.95% | excl client errors |
| Validate latency p99 | < 50ms | regional |
| Login latency p99 (no MFA UX) | < 400ms | hash included |
| Revoke propagation | < 5s | hard revoke |
| Refresh success (valid tokens) | 99.9% | |
""",
            ),
            (
                "Threat model checklist",
                """
- Credential stuffing / password spray
- Session hijack (XSS, malware, network)
- Refresh token theft
- CSRF
- Fixation
- MFA fatigue / SIM swap
- Support impersonation abuse
- Session store insider access
""",
            ),
            (
                "Ownership",
                """
| Component | Owner |
|-----------|-------|
| Auth service + hasher | Identity eng |
| Session store | Identity + SRE |
| Gateway validate plugin | Edge eng |
| OIDC broker | Identity eng |
| Audit pipeline | Security eng |
| Abuse limits | Safety/Abuse |
""",
            ),
            (
                "Failure drills",
                """
1. Kill primary Redis AZ — validates continue via failover
2. Rotate JWT signing keys mid-traffic
3. Force refresh reuse storm — grace behaves
4. IdP outage — SSO tenants messaging + status
5. Hash fleet CPU saturation — load shed logins, protect validate
""",
            ),
            (
                "Example session record sizes",
                """
```text
session_id          16–32 bytes
user_id             16 bytes
device_id           16 bytes
created/expiry      16 bytes
amr/acr compact     8–32 bytes
ip/ua hashes        32 bytes
refresh_family      16 bytes
flags/version       8 bytes
----------------------------
≈ 150–300 bytes structured + encoding overhead
Budget 512–1024 bytes/entry in Redis including Redis object overhead
```
""",
            ),
            (
                "Config knobs (tenant policy)",
                """
| Knob | Typical consumer | Typical enterprise |
|------|------------------|--------------------|
| Idle timeout | 14–30 days | 8–12 hours |
| Absolute timeout | 90 days | 24 hours |
| MFA required | optional/risk | required |
| SSO enforced | no | yes |
| Max devices | 20 | 5–10 |
| Password min | NIST-ish length | + complexity/breach check |
| Step-up window | 15–60 min | 5–15 min |
""",
            ),
            (
                "API error codes (sketch)",
                """
| Code | Meaning | Client action |
|------|---------|---------------|
| 401 invalid_session | missing/expired/revoked | re-login |
| 401 invalid_grant | bad refresh | re-login |
| 401 reuse_detected | refresh reuse | re-login; show security notice |
| 403 mfa_required | need MFA | complete challenge |
| 403 step_up_required | need fresh MFA | step-up then retry |
| 429 slow_down | rate limit | backoff |
| 503 auth_degraded | store/hash overload | retry with jitter |
""",
            ),
            (
                "Progressive delivery plan",
                """
**Week 1–2:** password login + opaque sessions + logout + reset.
**Week 3–4:** MFA TOTP + device list/revoke + rate limits.
**Week 5–6:** refresh rotation for mobile + gateway validate cache.
**Week 7–8:** OIDC one provider + audit pipeline + revoke SLO dashboards.
**Later:** WebAuthn, risk step-up, multi-region cells, passwordless.
""",
            ),
        ],
        [
            "Opaque session vs JWT decision stated with revoke story",
            "BOTE for validate QPS and session memory",
            "Cookie flags + CSRF called out",
            "Refresh rotation + reuse detection",
            "MFA + SSO hooks",
            "Fail closed on store outage",
            "Progressive scale to cells",
            "Deal-breakers: sticky-only, eternal JWT, logging secrets",
            "SLOs for revoke lag and validate latency",
            "Audit events listed",
            "Step-up auth for sensitive operations",
            "Hash algo migration path",
            "Multi-region revoke lag story",
            "BFF vs localStorage token storage",
            "Gateway validate caching vs revoke SLO tension called out",
        ],
    )
    return t

