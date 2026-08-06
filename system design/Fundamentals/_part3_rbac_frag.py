
def doc_rbac() -> str:
    t = header(
        "RBAC (Role-Based Access Control)",
        "roles · permissions · resource hierarchies · group inheritance · policy eval latency · cache invalidation · audit · ABAC boundary · least privilege · admin delegation",
        "authorization control plane — correct deny/allow under hierarchy, fanout, and cache",
    )
    t += s1(
        "design a production RBAC system that answers authorize(principal, action, resource) with low latency, supports roles/groups/resource hierarchies, audits decisions, and scales policy evaluation QPS without becoming an ABAC kitchen-sink on day one.",
        [
            ("Job", "Role/permission authorization service + admin APIs", "Full IdP, authentication, or WAF"),
            ("Model", "RBAC with groups + resource hierarchy; ABAC hooks later", "Pure ABAC/ReBAC from day one unless asked"),
            ("Enforcement", "Central PDP + local PEP cache at services/gateway", "Only UI-hidden buttons as security"),
            ("Tenancy", "Multi-tenant roles namespaced by tenant", "Single global role soup"),
            ("Scale lens", "Authorize QPS + principals + role bindings", "Only counting role definitions"),
        ],
        [
            ("Principals?", "Users, groups, service accounts", "Subject model + membership expansion"),
            ("Roles?", "Named roles with permission sets; tenant-scoped", "Role catalog + custom roles"),
            ("Permissions?", "action on resource type (docs:read) plus instance checks", "Canonical permission taxonomy"),
            ("Resources?", "Hierarchical (org/folder/project/object)", "Tree walk / materialized path"),
            ("Inheritance?", "Group∋user; role on parent applies to children with optional override", "Explicit deny vs allow precedence"),
            ("Delegation?", "Admin can grant subset of their perms", "Prevent privilege escalation"),
            ("Evaluation API?", "Check + list (what can I see?) both required", "List is harder — needs indexing"),
            ("Latency?", "p99 check < 10–20ms cached; list paginated", "Cache + denormalize"),
            ("Audit?", "All grants + deny/allow sampled/decision logs", "Tamper-evident store"),
            ("ABAC?", "Conditions (IP, time) as optional; not full Cedar day one", "Clear boundary"),
            ("Caching?", "PEP decision cache with invalidation", "Revoke/grant lag SLO"),
            ("Multi-region?", "Replicate policy; home region for writes", "Conflict policy"),
            ("Break-glass?", "Time-boxed emergency role with dual control", "Extra audit"),
            ("API tokens?", "Service accounts with roles; no human sharing", "Machine principals"),
        ],
        [
            "Permission taxonomy + role CRUD",
            "Bind role to principal on resource scope",
            "Authorize check API (allow/deny + reason code)",
            "Group membership with nested groups (depth limit)",
            "Resource hierarchy parent pointers",
            "Decision + grant audit logs",
            "Admin UI/API with least-privilege delegation rules",
            "PEP SDK with local cache",
            "Invalidation on grant/revoke",
            "List-resources-by-permission for one type (MVP)",
        ],
        [
            "Full relationship-based Google Zanzibar clone unless interviewer pushes",
            "Natural language policy authoring",
            "Cross-cloud IAM unification",
            "ML anomaly roles",
            "UI-only enforcement",
        ],
        [
            ("Check latency", "p50 < 5ms; p99 < 20ms with warm cache", "Cold miss budgeted separately"),
            ("Availability", "99.95%+ for check; fail closed for sensitive", "Fail policy per API class"),
            ("Grant durability", "Acked binds survive AZ loss", "Strong write on policy DB"),
            ("Invalidation lag", "< 5–30s depending product risk", "SLO published"),
            ("Consistency", "Read-your-writes for admin after grant in-region", "Global eventual for replicas"),
            ("List throughput", "Paginated; avoid O(catalog) scans", "AuthZ index"),
            ("Security", "No client-side trust; deny by default", "Least privilege"),
            ("Multi-tenant isolation", "Hard tenant boundary in every query", "No cross-tenant role bind"),
            ("Audit retention", "1y+ grants; 30–90d decision samples", "Compliance"),
            ("Cost", "Cache hit rate dominates CPU", "Avoid per-request graph walk unbounded"),
        ],
        [
            "Admin binds role Editor on folder → user edits doc child",
            "Service account CI deploy with deploy role on project",
            "User removed from group → access lost within invalidate SLO",
            "Break-glass grant with auto-expiry",
        ],
        [
            ("Nested group cycle", "Detect on write; reject; depth cap e.g. 5–10"),
            ("Conflicting allow+deny", "Explicit deny wins; document precedence"),
            ("List all docs world", "Must use authz index / ACL filters — never fetch-all then filter only at huge scale"),
            ("Stale cache allow", "TTL≤SLO + pub/sub invalidate on revoke"),
            ("Privilege escalation via custom role", "Custom role perms ⊆ grantor's grantable set"),
            ("Orphan resources", "Default deny; GC bindings"),
            ("Hot tenant policy", "Shard cache; isolate noisy tenants"),
            ("Rename permission", "Versioned perms; dual-read migration"),
            ("Impersonation", "Separate principal act-as with audit"),
            ("Bulk grant 10k users", "Async job + progress; don't block API"),
            ("PDP outage", "Fail closed sensitive; optional cached allow for read-only low-risk if product accepts"),
            ("Cross-tenant bind attempt", "Hard error; security alert"),
            ("Resource move in tree", "Recompute effective access; invalidate subtree"),
            ("Service token leak", "Revoke SA keys; bindings remain until removed"),
        ],
        [
            ("Authorize checks / sec", "10K", "100K", "1M", "10M"),
            ("Principals", "100K", "1M", "100M", "1B"),
            ("Role bindings", "1M", "10M", "1B", "10B"),
            ("Resources", "10M", "100M", "10B", "100B"),
            ("Groups / nesting", "10K / depth3", "100K /5", "10M /5", "100M /5"),
            ("Policy admins QPS", "10", "100", "1K", "10K"),
            ("Tenants", "100", "1K", "100K", "1M"),
            ("Invalidate events / sec", "10", "100", "5K", "50K"),
        ],
        "10×: PDP service + Redis decision cache + Postgres policy. 100×: shard bindings by tenant/resource; authz listing index; nested group expansion cache. 1,000×: Zanzibar-like relation tuples / ReBAC or heavily denormalized ACL bits; cell isolation; streaming invalidation worldwide.",
        [
            "Deny by default everywhere",
            "Check and list are different hard problems",
            "Cache invalidation is part of the security model",
            "Custom roles must not escalate",
            "ABAC conditions are spice, not the meal, for MVP",
        ],
        "We design RBAC with groups and resource hierarchy: a central policy plane, fast authorize checks, listing support, audit, and explicit cache/invalidation SLOs — not a full relationship-tuple megasystem unless scale demands it.",
    )
    t += s2(
        [
            (
                "Check QPS and cache",
                """
1M checks/s at 100×; target ≥ 95% cache hit
Cache miss → expand groups + walk resource ancestors + role perms
Miss budget 1–5ms store; if miss path 50ms, miss rate must be <<1%
Decision cache key: hash(principal_id, action, resource_id, policy_version)
""",
            ),
            (
                "Group expansion",
                """
User in 20 groups average; nested depth 3; expansion fanout ~50–200 group ids
Cache principal→effective_groups with TTL; invalidate on membership change
Cycle detection on write: DFS/Union-find; reject cycles
""",
            ),
            (
                "Resource ancestor walk",
                """
Depth typically ≤ 10 (org…object)
Materialized path / closure table makes check O(1) ancestor fetch
100B resources ⇒ closure table huge; prefer parent pointer + cached ancestor list on object
""",
            ),
            (
                "Binding storage",
                """
1B bindings × 100 bytes ≈ 100 GB
Index (resource_id), (principal_id), (tenant_id, role_id)
Hot folders with 1M member bindings need pagination and sharded edges
""",
            ),
            (
                "List-by-permission",
                """
Naive: scan all resources type=doc — impossible at 10B
Need reverse index: principal(+groups) → resource ids by perm
Or query engine with ACL filter fields (terms) in search
Estimate: 100M docs visible candidates still need cursor + limit
""",
            ),
            (
                "Invalidation fanout",
                """
Revoke group with 100K users → 100K principal cache keys + decision keys
Use policy_generation counter per tenant: bump generation invalidates all tenant decisions cheaply
Trade: coarser invalidation vs precision
""",
            ),
            (
                "Audit volume",
                """
Sample decisions 1–10% plus always log denies for sensitive actions
Grants: every write audited 100%
1M checks/s × 1% × 200B = 2 MB/s ≈ 170 GB/day sampled
""",
            ),
        ],
        """
1. **List/search with authz** — biggest footgun at scale.
2. **Cache vs revoke lag** — security correctness.
3. **Nested group expansion** — CPU and invalidation storms.
4. **Hot resources** (company-wide roles) — binding hotspots.
5. **Admin footguns** — custom roles escalation.
6. **Multi-tenant isolation bugs** — severity SEV0.
""",
    )
    t += s3(
        "Central **Policy Administration Point (PAP)** writes roles/bindings; **Policy Decision Point (PDP)** evaluates checks; services run **Policy Enforcement Points (PEP)** with cached decisions. Resource hierarchy + group expansion feed the evaluator. Listing uses a dedicated authz index, not 'fetch all then filter'.",
        [
            "PAP Admin API — roles, permissions, bindings, groups",
            "Policy DB — durable source of truth",
            "PDP Authorize Service — check + batch check",
            "Expansion Service — groups + ancestors",
            "Decision Cache — Redis / local PEP cache",
            "Invalidation Bus — pub/sub generation bumps",
            "AuthZ Indexer — reverse indexes for list",
            "Audit Pipeline — grants + decisions",
            "PEP SDK — middleware for services/gateway",
            "Tenant Policy Config — fail mode, TTLs",
            "Break-glass Workflow — approvals + expiry",
            "Migration Tools — perm renames, backfills",
        ],
        """
POST /v1/roles {tenant, name, permissions[]}
POST /v1/bindings {principal, role, resource, condition?}
DELETE /v1/bindings/{id}
POST /v1/groups/{id}/members {principal}
POST /v1/authorize/check {subject, action, resource} → {allow, reason, gen}
POST /v1/authorize/batch {checks[]}
GET  /v1/authorize/list {subject, action, type, cursor}
GET  /v1/effective-permissions {subject, resource}
GET  /v1/audit/grants?principal=
POST /v1/break-glass {reason, role, ttl}
""",
        """
Permission {perm_id, action, resource_type}
Role {role_id, tenant_id, name, perm_ids[], grantable_by_role?}
Binding {id, tenant_id, principal_type, principal_id, role_id, resource_id, expires_at?}
Group {group_id, tenant_id, name}
GroupMember {group_id, member_type, member_id}
Resource {resource_id, type, parent_id, tenant_id, path?}
PolicyGeneration {tenant_id, gen}
DecisionAudit {id, subject, action, resource, allow, ts, gen}
""",
        [
            ("Model", "RBAC+hierarchy", "Full Zanzibar ReBAC", "RBAC until list/share graphs demand tuples"),
            ("Deny", "Explicit deny wins", "Allow-only ACLs", "Deny for break/legal holds"),
            ("Cache key", "Include policy gen", "TTL only", "Gen bump for broad revoke"),
            ("List", "Authz reverse index", "Filter in app", "Index required at scale"),
            ("Nested groups", "Depth-capped expansion cache", "Unbounded recursion", "Cap+detect cycles"),
            ("Custom roles", "Subset of grantor perms", "Arbitrary perms", "Anti-escalation"),
            ("PDP placement", "Central + PEP cache", "Copy logic per service", "Central consistency"),
            ("Conditions", "Optional ABAC snippets", "Full policy language", "Boundary clear"),
        ],
        [
            ("UI hiding as authorization", "Trivial bypass via API"),
            ("Fetch-all-then-filter for list", "Melts at catalog scale; leaks timing"),
            ("Fail open on PDP timeout for payments", "Attackers induce timeouts"),
            ("Unbounded nested groups", "Eval CPU bombs"),
            ("Cache without invalidate on revoke", "Ghost access"),
            ("Global roles across tenants", "Cross-tenant breach pattern"),
            ("Putting all perms in JWT for 24h", "Revoke lag = token TTL"),
            ("Admin can grant any perm always", "Escalation chains"),
        ],
        "Authorization is a **deny-by-default decision service** with a versioned policy plane; enforcement is everywhere, policy truth is centralized, listing is indexed.",
    )
    t += s4(
        """
flowchart TB
  Admin --> PAP
  PAP --> PolicyDB[(Policy DB)]
  PAP --> InvBus[Invalidation Bus]
  PAP --> Audit[(Audit)]
  Service -->|check| PEP
  PEP -->|miss| PDP
  PDP --> Expand[Group/Ancestor Expand]
  Expand --> PolicyDB
  PDP --> DecisionCache[(Decision Cache)]
  InvBus --> DecisionCache
  InvBus --> PEP
  PDP --> AuthzIndex[(AuthZ List Index)]
  Service -->|list| PDP
  PDP --> Audit
""",
        [
            (
                "Authorize check sequence",
                """
1. PEP builds key (subject, action, resource, tenant_gen)
2. Local/Redis cache hit → return allow/deny
3. Miss → PDP expands groups (cached) + loads resource ancestors
4. Gather bindings on resource chain for subject∪groups
5. Evaluate allow/deny precedence + optional conditions
6. Store decision with gen; return reason code
7. Sample audit
""",
            ),
            (
                "Grant + invalidate",
                """
1. PAP validates grantor may bind role (delegation)
2. Write binding durable
3. Bump tenant gen OR precise invalidate keys
4. Publish invalidation
5. Audit grant
6. Async update authz list index
""",
            ),
            (
                "List documents subject can read",
                """
1. Expand subject groups
2. Query authz index for (principals, docs:read) with cursor
3. Filter tombstones / still-valid via check if uncertain
4. Return page; never full table scan
""",
            ),
            (
                "Break-glass",
                """
1. Request with reason; dual approval if configured
2. Time-boxed binding expires_at=now+ttl
3. Page security; enhanced audit
4. Auto-revoke job sweeper
""",
            ),
        ],
    )
    t += s5(
        [
            "Deny by default; missing binding = deny.",
            "Explicit deny overrides allow.",
            "All grant/revoke durable before ack; idempotent binding ids.",
            "Invalidation within published SLO; policy generation monotonic.",
            "Fail closed for high-risk actions on PDP errors; document any fail-open exceptions.",
            "Cycle detection on group graphs; depth limits.",
            "Delegation: grantable permission set ⊆ caller's effective grantable set.",
            "Break-glass always audited + TTL.",
            "Tenant_id on every query; automated cross-tenant tests.",
            "Rate-limit admin APIs; bulk via async jobs.",
            "Decision audit sampling + always-on sensitive denies.",
            "PEP libraries versioned; incompatible policy features gated.",
        ],
        [
            ("1×", "Postgres bindings; single PDP; Redis cache; parent pointers"),
            ("10×", "Read replicas; batch check API; group expansion cache; search ACL filters"),
            ("100×", "Shard by tenant; authz reverse index; generation invalidation; regional PDP"),
            ("1,000×", "Relation-tuple store / Zanzibar-style; cells; streaming watch APIs"),
        ],
        [
            "Policy-as-code CI for role packs; review custom roles.",
            "Diff tools for effective permissions before/after grant.",
            "Canary PDP with mirrored traffic.",
            "Chaos: kill PDP; verify fail mode.",
            "Schema migrations for permission renames with dual-read.",
            "SLO dashboards: check p99, invalidate lag, cache hit, list p99.",
        ],
        [
            (
                "Evaluation algorithm",
                """
1. Normalize action to permission id.
2. Expand subject → {user} ∪ groups (cached).
3. Load resource chain [R, parent, …, root].
4. Fetch bindings matching principals × chain.
5. Collect allow and deny; **deny wins**.
6. Evaluate conditions (IP/time) if present.
7. Return decision + debug trace for admins (gated).

Optimize with bitsets for common role packs; avoid N+1 queries (batch binding fetch).
""",
            ),
            (
                "RBAC vs ABAC vs ReBAC boundary",
                """
- **RBAC:** role bundles permissions; good for enterprise admin mental model.
- **ABAC:** attributes/conditions; good for "only from corp IP".
- **ReBAC/Zanzibar:** relationship tuples ("user:U viewer doc:D"); excels at sharing graphs & list.

Staff answer: start RBAC+hierarchy; add conditions lightly; move to tuples when sharing/list graphs dominate.
""",
            ),
            (
                "Cache invalidation strategies",
                """
**Precise keys:** invalidate affected principal/resource — accurate, fanout heavy.
**Generation counter:** tenant_gen++ makes all old cache misses — cheap, thundering herd risk.
**Hybrid:** gen for group changes; precise for single user revoke.

Measure revoke lag SLI from write commit to PEP observe deny.
""",
            ),
            (
                "Least privilege & custom roles",
                """
Custom role creation: permissions must be ⊆ creator's *grantable* set (not merely effective use set).
Separate **use** vs **grant** permissions (IAM PassRole analogue).
Periodic access reviews; unused binding GC hints.
""",
            ),
            (
                "AuthZ for list/search",
                """
Embed ACL terms in search index (user ids + group ids allowed).
Query: filter terms intersect expansion.
Cap clause count; for huge groups use "group:G" term instead of exploding users.
Reindex async on binding change; document lag.
""",
            ),
            (
                "Multi-tenant isolation",
                """
resource.tenant_id must match subject token tenant (unless super-admin audited).
Automated tests attempt cross-tenant check/list/bind.
Physical isolation optional at 1,000× for large tenants (cell).
""",
            ),
        ],
    )
    t += s6(
        "An RBAC control plane with PAP/PDP/PEP, hierarchy + groups, deny-by-default evaluation, generation-aware caching, audited grants, and an authz list index — with a clear path to ReBAC if sharing graphs demand it.",
        [
            "Deny default + explicit deny precedence",
            "Check vs list as separate designs",
            "Policy generation invalidation",
            "Anti-escalation for custom roles",
            "Fail-closed posture for sensitive ops",
            "Depth-capped group expansion",
        ],
        [
            "Stale allow due to slow invalidate",
            "List index lag → over/under sharing UX",
            "Hot group membership storms",
            "Over-built Zanzibar too early",
            "Fail-open antipattern under load",
        ],
        [
            ("0–5", "Requirements: hierarchy, list, ABAC boundary"),
            ("5–12", "BOTE: check QPS, bindings, invalidation"),
            ("12–25", "PAP/PDP/PEP + data model"),
            ("25–35", "Eval algorithm + cache"),
            ("35–42", "List/search authz"),
            ("42–45", "Deal-breakers + SLOs"),
        ],
        "If your authorize() is fast but list-all-then-filter is your sharing model, you do not yet have an authorization system at scale.",
    )
    t += s7(_qs([
        ("Why deny by default?",
         "Missing policy must not become allow. Attackers and bugs omit binds; default deny fails safe. Explicit allows are intentional."),
        ("How do nested groups affect latency?",
         "Expansion can fan out widely. Cache principal→groups, cap depth, detect cycles on write, and invalidate on membership changes. Unbounded recursion is a CPU DoS."),
        ("Explicit deny vs remove allow?",
         "Remove allow is enough when you control all binders. Explicit deny is needed for legal holds, break-glass overrides, or delegated admin where you cannot find all allows quickly."),
        ("JWT carrying roles for 24h?",
         "Makes revoke lag equal token TTL. Prefer short tokens with role version / fetch roles server-side / PEP cache with invalidate."),
        ("How does Google Zanzibar relate?",
         "ReBAC with relation tuples and consistency tokens for list+check at global scale. Use when sharing graphs explode; otherwise RBAC+hierarchy may suffice."),
        ("Check vs list difficulty?",
         "Check is point lookup/walk. List must find unknown resources subject can access — needs reverse index or ACL-aware search, not scan-and-filter."),
        ("Cache stampede after gen bump?",
         "Soft TTLs, singleflight/request coalescing per key, staggered regen, and warm critical subjects. Prefer precise invalidation when fanout small."),
        ("Service accounts vs users?",
         "Same binding model different principal_type. Keys/credentials rotate independently from bindings. Never share human credentials to bots."),
        ("How to prevent privilege escalation?",
         "Grantable permission sets; PassRole-like controls; deny binding roles with broader perms than caller; audit custom role creation."),
        ("What is a policy generation number?",
         "Monotonic tenant counter bumped on broad policy changes; cached decisions store gen; mismatch ⇒ miss. Cheap global invalidate."),
        ("ABAC when?",
         "When attributes/context matter (time, IP, device posture) beyond roles. Keep expressions small and testable; avoid turning into general programming language casually."),
        ("Fail open or closed?",
         "Default closed for mutate/sensitive read. Rare fail-open for non-sensitive reads only with explicit product acceptance and metrics."),
        ("Resource move across tree?",
         "Update parent/path; invalidate subtree decisions; reindex lists; watch for TOCTOU during move."),
        ("How to test RBAC?",
         "Table-driven fixtures for allow/deny; property tests for deny-wins; cross-tenant fuzz; load tests on check and list separately."),
        ("Batch authorize API shape?",
         "POST checks[] up to N (e.g. 100); PDP pipelines expansions once per subject; return aligned results. Avoid chatty per-item RPC from hot loops."),
        ("Hot folder with millions of viewers?",
         "Store group binding on folder not per-user; expand via group membership; list via group term in index."),
        ("Audit PII concerns?",
         "Log ids not emails when possible; restrict decision debug traces; retain grants longer than sampled decisions."),
        ("Multi-region policy writes?",
         "Single home region for PAP writes; replicate read-only to PDP regions; conflict avoidance over multi-master grants."),
        ("Break-glass design?",
         "TTL binding, dual control, paging, immutable logs, automatic expiry sweeper, post-incident review required."),
        ("Permission rename migration?",
         "Introduce new perm; dual-grant in roles; dual-eval period; remove old. Never rename in place without dual-read."),
        ("SDK PEP vs sidecar?",
         "SDK in-process = lower latency; sidecar = polyglot consistency. Many use SDK with shared policy client library."),
        ("How do you bound evaluation CPU?",
         "Depth caps, binding fetch limits, timeout with deny, circuit-break abusive tenants, precompute effective roles for popular combos."),
        ("What's a staff deal-breaker?",
         "'We'll filter in the application after query' as the only list strategy at multi-million resource scale without an authz index story."),
        ("Relationship to authentication?",
         "Authn establishes principal; authz consumes principal id + groups. Keep separate services; never entangle password checks into PDP."),
    ]))
    t += s8(
        [
            (
                "SLO sketch",
                """
| SLI | SLO |
|-----|-----|
| Check availability | 99.95% |
| Check p99 (warm) | < 20ms |
| Invalidate lag p99 | < 30s (tune tighter for sensitive) |
| List p99 first page | < 200ms |
| Cross-tenant incidents | 0 |
""",
            ),
            (
                "Precedence rules",
                """
1. Tenant isolation hard fail
2. Explicit deny
3. Allow via role binding on resource chain
4. Else deny
""",
            ),
            (
                "Ownership",
                """
| Component | Owner |
|-----------|-------|
| PAP/PDP | Identity/AuthZ eng |
| PEP SDK | AuthZ eng + client platforms |
| Authz index | AuthZ + Search |
| Audit | Security |
""",
            ),
            (
                "Failure drills",
                """
1. Revoke role → observe deny within SLO across regions
2. PDP kill → fail closed path
3. Gen bump storm → coalescing holds
4. Nested group cycle attempt → rejected
5. Cross-tenant bind → blocked + alert
""",
            ),
            (
                "Rollout plan",
                """
Week 1–2: check API + bindings + deny default
Week 3–4: groups + hierarchy + cache
Week 5–6: list index for one resource type
Week 7–8: audit + break-glass + delegation guards
""",
            ),
        ],
        [
            "Deny-by-default stated",
            "Check vs list differentiated",
            "Cache invalidation / gen SLO",
            "Group depth + cycles",
            "Anti-escalation custom roles",
            "ABAC boundary clear",
            "Fail-closed posture",
            "BOTE for QPS and bindings",
            "Deal-breakers listed",
            "Audit story",
            "PEP/PDP/PAP split",
            "Path to ReBAC if needed",
        ],
    )
    return t

