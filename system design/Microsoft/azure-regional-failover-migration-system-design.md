# System Design: Azure Regional Failover & Service Migration

> **Focus areas:** Region failure / overload · Failover orchestration · Stateful migration · RPO/RTO · Traffic shift · Data residency · Entra & DNS · Runbooks · Copilot/GPU capacity coupling  
> **Style:** Control-plane + data-plane DR design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split detection vs decision vs execution; residency-aware targets; no split-brain writers; deal-breakers explicit  
> **Interview theme:** Microsoft / Azure — **migrate services out of a failing or overloaded region** and operate DR/failover

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

Goal: design the systems and procedures that **detect** an Azure region (or regional stamp) in distress, **decide** a residency-legal failover/migration plan, **execute** traffic + data + dependency moves with bounded RPO/RTO, and **prove** safety (no dual writers, no illegal geo spill)—including when Copilot/GPU capacity is the scarce bottleneck.

### 1.0 What this is / is not

| Dimension | This doc | Not this |
|-----------|----------|----------|
| Job | Regional DR + planned/unplanned migration orchestration | App feature design alone |
| Trigger | Outage, capacity meltdown, AZ cascade, maintenance | Tiny single-VM reboot |
| Scope | Multi-service dependency graph in a stamp/region | One Cosmos container tutorial |
| Identity | Entra tenant continuity across regions | Re-creating all users |
| Compliance | Residency, sovereign clouds, Purview evidence | “Any healthy region is fine” |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Failure types? | Region down, network partition, capacity overload, dependency brownout | Multi-signal detection |
| F2 | Workloads? | Stateless APIs, stateful DBs, queues, AI/GPU, M365-adjacent | Class-specific playbooks |
| F3 | Auto vs human? | Auto for traffic shed; human approve for hard failover | Two-man rule on destructive steps |
| F4 | RPO/RTO? | Tiered by criticality (see NFR) | Replication topology up front |
| F5 | DNS / traffic? | Front Door, Traffic Manager, private DNS | Global traffic plane |
| F6 | Data? | Cosmos/SQL/Storage/Kafka-like; geo-replication variants | Per-store failover APIs |
| F7 | Secrets? | Key Vault per region + replication strategy | MI + KV readiness in target |
| F8 | Identity? | Entra is global; app configs regional | Token audiences / app regs |
| F9 | Residency? | Failover only inside allowed geo | Target allowlists |
| F10 | Order? | Dependency-aware migration graph | Orchestrator DAG |
| F11 | Failback? | Yes, planned | Reverse DAG + catch-up |
| F12 | Comms? | Status page + tenant notifications | Comms as first-class |

**MVP functional scope:**

1. Health signals → incident object for region/stamp.  
2. **Capacity & residency-aware** target selection.  
3. Orchestrated failover DAG: traffic drain → promote data → start compute → verify → cutover.  
4. Stateless services: redeploy/scale in target; shift Front Door.  
5. Stateful: planned promotion of geo-replicas (Cosmos/SQL/Storage patterns).  
6. Queue/bus: drain or dual-publish strategy with idempotent consumers.  
7. GPU/AI pools: capacity reservation in target geo; degrade Copilot if short.  
8. Guardrails: block illegal geo; block dual primary; audit every step.  
9. Failback runbook.  
10. GameDays / chaos evidence.

**Out of MVP:** perfect zero-RPO active-active for all stores; cross-sovereign miracles; fully autonomous failover without human gates for Sev0 data promotion.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Detection | Suspected regional Sev within 1–5 minutes |
| N2 | Decision | Annotated plan in < 15 minutes for known stamps |
| N3 | RTO tier-0 (auth/traffic edge) | 5–30 minutes |
| N4 | RTO tier-1 (customer APIs) | 30–120 minutes |
| N5 | RPO tier-0/1 | 0–seconds (sync/near-sync) to minutes (async) — declare honestly |
| N6 | Safety | No dual writers; no residency violation |
| N7 | Auditability | Every orchestration step attributable |
| N8 | Scalability of orchestrator | Manage thousands of services/resources |
| N9 | Comms latency | Customer-visible banner within minutes of declare |
| N10 | Copilot continuity | Degrade in-geo rather than illegal spill |

### 1.3 Cases

**Happy / planned**

1. Capacity overload West Europe → drain batch → scale North Europe → shift traffic fractionally.  
2. Planned region maintenance → migrate stamp with customer-visible window.  
3. Single AZ loss → zone-redundant survive; no region failover.

**Unplanned**

1. Region control plane brownout → failover customer stamps to pair region.  
2. Storage backend Sev → promote secondary; rewrite connection strings via app config.  
3. Front Door healthy but origin region dead → origin failover group.

**Edges**

| Case | Behavior |
|------|----------|
| Split brain network | Quorum / witness; fence old primary |
| Target region also hot | Partial admit; shed non-critical; expand capacity |
| Residency forbids pair | Stay down or limited mode; legal > availability |
| Entra global issue | Cannot “failover Entra”; degrade differently |
| Key Vault in dead region | Pre-replicated secrets / secondary KV |
| In-flight Copilot GPU runs | Cancel/incomplete; settle leases; restart in target if legal |
| IaC drift in target | Pre-warm / continuous config sync |
| DNS TTLs too high | Design low TTL + anycast planes |
| Partial dependency success | Rollback graph or hold traffic |
| Sovereign tenant | Only sovereign pair; else outage |

### 1.4 Progressive scale

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Services in stamp | 50 | 500 | 5,000 | 50,000 |
| Stateful stores | 20 | 200 | 2,000 | 20,000 |
| QPS shifted | 100K | 1M | 10M | 100M |
| Data replicated (TB) | 50 | 500 | 5,000 | 50,000+ |
| GPU nodes to place | 200 | 2,000 | 20,000 | 200,000 |
| Concurrent failovers | 1 region | multi-stamp | multi-geo events | global incident fabric |
| Orchestrator steps/run | ~200 | ~2K | ~20K | ~200K |

**Jumps:** 10× = standardized stamps + pair regions; 100× = automated DAG + continuous DR drills; 1,000× = global incident fabric, capacity broker, policy compiler at planet scale.

### 1.5 Scope repeat-back

> Design Azure regional failover/migration: detect distress, choose residency-legal targets, orchestrate dependency-aware cutover for stateless/stateful/AI capacity, prevent split-brain and illegal geo spill, communicate, fail back—scaled from one stamp to fleet-wide DR.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split load classes

| Class | What | Notes |
|-------|------|-------|
| Health signals | metrics/logs/probes | High cardinality; aggregate |
| Orchestrator steps | ARM/control-plane API calls | Rate-limited by Azure RP |
| Data replication catch-up | Bytes/s | Dominates hard failover |
| Traffic shift | DNS/AFD rules | Fast if origins ready |
| GPU cold start | Minutes–hours | Often longest AI RTO |

### 2.2 Replication catch-up math

```text
Async lag L = 120s; write rate W = 500 MB/s
Catch-up backlog ≈ L × W = 60 GB
At catch-up bandwidth B = 1 GB/s ⇒ ~60s (ideal)
Reality: contention + verification ⇒ budget 10–30×
Declare RPO from replication mode, not wishful thinking
```

### 2.3 Traffic drain

```text
In-flight requests avg 200ms; desire <1% errors
Drain: stop new admits → wait 1–5s → connection draining → mark origin down
Sticky sessions / SSE Copilot streams: special cancel protocol
```

### 2.4 Control-plane API budget

```text
2,000 resources × 5 API calls = 10,000 calls
At 50 rps effective ⇒ 200s lower bound + retries
Need parallelism with polite rate limits + idempotent ops
```

### 2.5 DNS / TTL

```text
TTL 60s → clients may stick up to ~60s (plus resolver caching reality)
Prefer Azure Front Door origin groups for faster than public DNS alone
```

### 2.6 GPU capacity

```text
Failing region had 2,000 H100-eq; pair has 800 free
⇒ cannot full-fidelity failover AI
Plan: reserved DR capacity + degrade Copilot interactive watermark + shed batch
```

### 2.7 Cost of warm DR

```text
Warm pair (compute scaled to 20–50% + data geo-repl) costs continuously
Cold DR cheaper, RTO worse
Interview: pick tiered DR classes, not one mode for all services
```

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Role |
|-------|------|
| Detection | Health, SLO burn, dependency probes, capacity |
| Decision | Policy + residency + capacity broker → plan |
| Orchestration | Execute DAG with gates |
| Traffic | AFD / TM / GSLB |
| Data | Replication, promote, fence |
| Identity / secrets | Entra (global), KV/MI regional readiness |
| Comms / audit | Status, customer notices, evidence |

### 3.2 Workload classes

| Class | DR pattern | Typical RPO | Typical RTO |
|-------|------------|-------------|-------------|
| Stateless API | Multi-region deploy + traffic | n/a | minutes |
| Cosmos / globally distributed | Multi-region writes or failover | seconds/0 | minutes |
| Azure SQL | Failover groups | seconds–minutes | minutes |
| Storage | GRS/GZRS/RA-GRS | minutes (async) | minutes–hours |
| Event Hubs / Kafka | Mirror / dual ingest | seconds–minutes | minutes |
| Redis | Passive replica / rebuild | minutes–lossy | minutes |
| GPU inference | Pre-warm pools in pair geo | n/a | minutes–hours |
| Edge/AFD | Already global | n/a | seconds–minutes |

### 3.3 HLD options for multi-region

#### Option A — Active-passive pair (chosen default for many enterprise stamps)

| Pros | Cons |
|------|------|
| Clear primary; simpler consistency | Idle capacity cost; failover eventful |

#### Option B — Active-active stateless + single-writer stateful

| Pros | Cons |
|------|------|
| Faster RTO for APIs | Sticky data primary still a cliff |

#### Option C — Multi-master everywhere

| Pros | Cons |
|------|------|
| Fancy | Conflict hell; often wrong for Copilot runs / ledgers |

**Choice:** **B for edge/API**, **A/B hybrid for data**, never C for strongly ordered ledgers without CRDT story.

### 3.4 Detection

```text
Signals:
  - Synthetic probes from multiple geos
  - Error rate / latency SLO burn
  - Azure resource health / activity logs
  - Capacity: CPU, RU, GPU free, queue depth
  - Dependency: Entra, DNS, KV, Graph
  - Human Sev declare

Aggregator:
  region_score = f(signals)
  states: healthy | degraded | suspected_outage | declared_failover
```

**Anti-flap:** multi-signal correlation + min duration; avoid failover on single metric blip.

### 3.5 Decision / policy compiler

```text
inputs:
  stamp_id, failure_mode, residency_policies, capacity_snapshot,
  dependency_graph, customer_impact, human approvals

output:
  FailoverPlan {
    target_region,
    steps[],
    rpo_rto_estimates,
    degradations[] (e.g. Copilot model downgrade),
    abort_conditions
  }
```

**Deal-breaker:** picking `eastus2` for an EU Data Boundary stamp because it is “healthiest.”

### 3.6 Orchestrator DAG (canonical)

```text
1. Declare incident + freeze risky deploys
2. Preflight target (KV, MI, capacity, images)
3. Stop non-critical ingress (batch/evals)
4. Quiesce primary writers / drain
5. Promote / confirm data secondaries
6. Fence old primary (SAS revoke, firewall, break pairing carefully)
7. Apply config (app settings, private endpoints)
8. Warm compute / GPU pools
9. Health verify in target
10. Shift traffic (fractional → 100%)
11. Monitor error budgets
12. Customer comms updates
13. Postmortem + backlog; later failback
```

Human gates before steps 5–6 for Sev0.

### 3.7 Traffic shift strategies

| Mechanism | Use |
|-----------|-----|
| Azure Front Door origin group priority/weight | Primary web/API |
| Traffic Manager | DNS-based non-HTTP / complementary |
| Private DNS + app config | Internal service discovery |
| Client-side region hooks | M365/Copilot pinned cells |

**Fractional cutover:** 1% → 10% → 50% → 100% with automatic rollback on SLO burn.

### 3.8 Data plane patterns (interview table)

| Store | Pattern | Notes |
|-------|---------|-------|
| Cosmos DB | Multi-region; failover priority | Know manual vs automatic failover |
| SQL DB | Auto-failover groups | Listener endpoint abstraction |
| Storage | GRS; account failover API | RPO minutes; verify list/read |
| Event Hubs | Geo-disaster recovery pairing OR product dual-write | Checkpoint rebuild |
| Service Bus | Geo-pairing | Similar |
| Postgres (flexible) | HA + geo-repl if used | Fence carefully |
| Redis Cache | Secondary + flush/rebuild | Often lossy OK for sessions |

### 3.9 Copilot / GPU coupling

Regional Copilot (sibling doc) pins residency. On failover:

1. Compiler retargets to **allowed** pair region.  
2. Capacity broker reserves interactive watermark first.  
3. Batch cancelled; interactive may degrade model.  
4. In-flight runs → incomplete; clients retry against new cell.  
5. Audit pipelines must also be residency-legal in target.

### 3.10 Entra & secrets

- **Entra ID** is not failed over like a regional SQL—identity is global (with sovereign exceptions).  
- Apps use managed identities deployed in target; RBAC pre-granted.  
- Key Vault: secondary vault or multi-region secrets strategy; **never** only-in-primary secrets for tier-0.  
- Certificate binding on AFD pre-staged.

### 3.11 Component list

1. Signal Ingest & Health Score  
2. Incident Service  
3. Policy / Residency Compiler  
4. Capacity Broker (incl. GPU)  
5. Orchestrator (DAG engine)  
6. Resource Adapters (Cosmos/SQL/Storage/K8s/VMSS/AFD)  
7. Traffic Controller  
8. Fence Service  
9. Verification / Synthetic Suite  
10. Comms Service  
11. Audit / Evidence Lake  
12. GameDay Scheduler  

### 3.12 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| Auto data promote | Human-gated Sev0 | Split-brain risk |
| Warm vs cold | Tiered | Cost/RTO |
| Dual-write queues | Selective | Complexity |
| Failback auto | Rarely | Needs catch-up proof |
| Global orchestrator | Active-active meta | Survives region loss |

---

## 4. Architecture Diagram

### 4.1 Control planes

```text
 +------------------+     +-------------------+
 | Synthetics/Probes|---->| Health Aggregator |
 +------------------+     +---------+---------+
 | Azure Resource   |               |
 | Health / Metrics |---------------+
 +------------------+               v
                          +---------+---------+
                          | Incident Service  |
                          +---------+---------+
                                    |
                                    v
 +------------------+     +---------+---------+     +------------------+
 | Residency Policy |---->| Decision Compiler |<----| Capacity Broker  |
 +------------------+     +---------+---------+     | (CPU/RU/GPU)     |
                              |                     +------------------+
                              v
                      +-------+--------+
                      | Orchestrator   |
                      | (DAG + gates)  |
                      +--+-----+----+--+
                         |     |    |
           +-------------+     |    +--------------+
           v                   v                   v
   +---------------+   +---------------+   +---------------+
   | Data Adapters |   | Compute/GPU   |   | Traffic Ctrl  |
   | SQL/Cosmos/.. |   | Adapters      |   | AFD / TM      |
   +---------------+   +---------------+   +---------------+
           |                   |                   |
           +----------+--------+---------+---------+
                      v
               +------+------+
               | Fence +     |
               | Verify +    |
               | Comms/Audit |
               +-------------+
```

### 4.2 Active-passive stamp pair

```text
Clients --> Azure Front Door
               |  primary origin
               +------> Region A (PRIMARY)
               |           - APIs, DBs(primary), GPU pools
               |           - Event ingress
               |
               +------> Region B (SECONDARY/WARM)
                           - APIs scaled low / warm
                           - DB replicas
                           - GPU reserved watermark
                           - Config synced continuously
```

### 4.3 Cutover sequence (ASCII timeline)

```text
t0   detect suspected_outage
t1   declare + freeze deploys
t2   drain batch / stop new heavy admits
t3   quiesce writers
t4   promote data (human gate)
t5   fence old primary
t6   scale compute/GPU in B
t7   synthetics green
t8   AFD weight 1%..100%
t9   monitor / amplify capacity
t10  failback planning later
```

### 4.4 Dependency DAG example

```text
KV ready -> MI RBAC -> SQL promote -> Cosmos failover ->
  App Config flip -> API deploy healthy ->
    AFD shift -> Copilot pools warm -> open interactive
Event Hub pair switch parallel after fence of old publishers
```

### 4.5 Split-brain fence

```text
Old primary network flapping back to life
Without fence: accepts writes → divergent data

Fence actions:
  - remove AFD origin
  - deny public/private network to DB
  - revoke storage keys / rotate
  - break replication role carefully
  - stamp "fenced_generation = N"
New primary only serves if generation matches
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. At most **one primary writer** per stateful partition after cutover.  
2. Failover targets ⊆ residency allowlist.  
3. Orchestrator steps **idempotent** and audited.  
4. Human gate for irreversible promote/fence on tier-0 data.  
5. Traffic never cuts 100% before synthetics pass.  
6. Old primary fenced before declaring success.  
7. Copilot/AI will **degrade or brownout** rather than illegal geo spill.  
8. Secrets/MI exist in target before compute starts.  
9. Failback requires catch-up proof, not vibes.  
10. Detection flaps must not ping-pong regions.

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | Manual runbooks; pair region; AFD; SQL failover group |
| 10× | Stamp template; continuous config sync; capacity broker v1 |
| 100× | DAG orchestrator; adapters; GameDays quarterly per stamp |
| 1,000× | Global incident fabric; automated fractional shift; GPU DR reservations marketplace |

### 5.3 Maintainability

- Stamps as immutable product units with DR class labels.  
- Adapters versioned; contract tests against Azure RP sandboxes.  
- Policy-as-code for residency.  
- Regular GameDays with scored RTO/RPO.  
- Clear SEV ownership: Incident Commander vs Data Captain vs Traffic Captain.

### 5.4 Progressive narrative

**1×:** One app, SQL failover group, TM failover, runbook in wiki.  
**10×:** Microservice stamp; 50 resources; warm secondary; quarterly drill.  
**100×:** Platform orchestrator; multi-stamp; Copilot GPU reservations; customer comms automation.  
**1,000×:** Portfolio of geographies; capacity exchange; automated evidence for compliance audits.

### 5.5 Stateful cutover deep dive (SQL example)

```text
Pre:
  Primary A, geo-replica B in failover group
  App uses failover listener endpoint

During:
  1. Stop writes (or accept brief loss per RPO)
  2. Planned failover API
  3. Wait role transition
  4. Verify read/write on B
  5. Fence A if it returns

App ideally needs **no connection string change** if listener used
```

### 5.6 Cosmos notes

- Understand automatic failover vs manual.  
- Multi-region writes change conflict story—only if product needs it.  
- Priority lists must match residency (EU regions only).

### 5.7 Queue / stream migration

| Strategy | Pros | Cons |
|----------|------|------|
| Geo-pairing failover | Built-in | Lag/checkpoint care |
| Dual publish | Smooth | Exactly-once harder |
| Drain then switch | Clean | Longer RTO |

Consumers must be idempotent either way.

### 5.8 Stateless + config

- Container images in ACR geo-replicated.  
- App Config / Feature Flags dual-region.  
- K8s cluster in pair with matched Helm/GitOps; avoid “docker pull from dead region only.”

### 5.9 Capacity broker algorithm (sketch)

```text
need = forecast(stamp, mode)
legal_targets = residency_filter(stamp)
for t in rank(legal_targets):
  free = capacity(t)
  if free >= need.critical: choose t
  else if free + degradations covers P0: choose t with degradations
else: fail closed / wait for scale-out
```

### 5.10 Overload vs hard outage

| Mode | Actions |
|------|---------|
| Overload | Shed batch, raise prices/quotas, scale, fractional shift, no data promote |
| Hard outage | Full DAG promote + fence |
| Brownout | Mixed; careful not to promote on soft signals |

### 5.11 Failback

```text
After A recovers:
  1. Rebuild A as secondary from B
  2. Catch up
  3. Planned reverse failover in maintenance window
  4. Or keep B primary (pin flip) permanently
```

### 5.12 Deal-breakers

| Temptation | Failure |
|------------|---------|
| Auto-failover on one noisy metric | Ping-pong outage |
| Ignore residency | Compliance Sev |
| Skip fence | Split-brain corruption |
| 100% traffic before verify | Customer SEV amplification |
| Assume Entra is regional | Wrong mental model |
| No GPU DR plan | Copilot dead while APIs live |
| Manual-only at 100× scale | Impossible RTO |
| Secrets only in primary KV | Hard RTO floor |

### 5.13 Observability & evidence

- Step timeline with actor (user/system).  
- Before/after replication lag graphs.  
- Traffic % and error budgets.  
- Fence proof (network denies).  
- Customer notification IDs.  
- Compliance export: “data remained in geo X.”

### 5.14 Security during failover

- Elevated break-glass identities logged.  
- Rotate keys if region compromise suspected (security incident ≠ capacity incident).  
- Preserve audit logs out-of-band.  
- Beware malicious “failover” social engineering—two-person rule.

### 5.15 GameDay program

| Drill | Frequency | Success |
|-------|-----------|---------|
| Stateless traffic shift | monthly | RTO met, no pages |
| SQL/Cosmos promote | quarterly | RPO/RTO met |
| GPU pool warm | quarterly | Interactive watermark |
| Hard region game | semi-annual | Full DAG |
| Failback | annual | Clean reverse |

### 5.16 Customer tenancy mapping

Enterprise tenants may pin: “West Europe primary, North Europe DR only.” Store in policy service; compiler must read it. Sovereign clouds: separate orchestrator stamp.

### 5.17 Interaction with deployments

Freeze CI/CD to primary during failover; redirect pipelines to target; prevent old primary from receiving “helpful” auto-remediation that unfences it.

---

## 6. Wrap-Up

### 6.1 Designed

An Azure regional failover/migration system: multi-signal detection, residency/capacity-aware planning, gated DAG orchestration across traffic/data/compute/GPU, fencing, verification, comms, failback, and GameDays.

### 6.2 Decisions to defend

1. Tiered DR classes (not one mode)  
2. Human gates on data promote/fence  
3. Residency compiler on targets  
4. Fractional traffic shift  
5. Capacity broker including GPUs  
6. Idempotent adapters  
7. Fence before success  
8. Entra global vs regional secrets distinction  
9. Overload ≠ outage playbooks  
10. Evidence for compliance  

### 6.3 Risks

- Azure RP rate limits during crisis  
- Hidden dependency not in DAG  
- Replication lag underestimated  
- DNS/client sticky behavior  
- Target region contention  
- People/process under stress  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Scope: outage vs overload; residency |
| 5–12 | Workload classes + RPO/RTO |
| 12–25 | Detection → plan → DAG + diagram |
| 25–35 | Data promote, fence, traffic |
| 35–45 | GPU/Copilot, failback, GameDays |

### 6.5 Closer

> **Azure regional failover**: detect honestly, choose legally, orchestrate dependency-aware cutover, fence split-brain, degrade Copilot in-geo when GPUs are short, prove evidence—availability without corrupting data or residency.

---

## 7. Deeper / Related Interview Questions

### 7.1 RPO/RTO

**Q: Customer wants RPO 0 and RTO 0 in one region failure.**  
A: Needs active-active with sync replication / multi-master—costly and often impossible across continents; negotiate tiers.

**Q: What’s your RPO for GRS Storage?**  
A: Typically minutes; don’t claim sync.

### 7.2 Split brain

**Q: Primary comes back during promote.**  
A: Fence; generation numbers; refuse writes with stale role.

### 7.3 Traffic

**Q: Why Front Door over DNS TTL alone?**  
A: Faster origin failover, WAF, anycast; DNS still complementary.

### 7.4 Identity

**Q: Do we failover Entra?**  
A: Generally no—global service; design for Entra dependency differently (cache JWKS, degrade).

### 7.5 Copilot

**Q: Pair region lacks GPUs.**  
A: Reserved DR capacity + degrade + shed batch; never illegal spill.

### 7.6 Orchestration

**Q: How do you make steps idempotent?**  
A: Preflight desired state; conditional APIs; store step cursors; retries safe.

**Q: Partial DAG failure?**  
A: Compensating actions or hard stop with traffic held; never half-promote without fence plan.

### 7.7 Comparison traps

**Q: Is this Kubernetes cluster failover?**  
A: Broader—data, traffic, identity/secrets, GPU, compliance.

**Q: Is Azure Site Recovery enough?**  
A: ASR/VM replication is one tool; PaaS services need native geo features + app orchestration.

### 7.8 Failure injection

1. Fake healthy metrics during outage (rely multi-signal).  
2. Target region API throttling.  
3. KV secret missing in target.  
4. AFD mis-config open redirect.  
5. SQL promote stuck.  
6. Old primary zombie writes.  
7. Checkpoint poison after Event Hubs failover.  
8. Human approver unavailable (escalate).  
9. Residency mis-tag.  
10. GPU drivers lag in warm pool.

### 7.9 Extra traps

- Who is Incident Commander?  
- What’s the abort criteria mid-cutover?  
- How do you test fence without causing an outage?  
- How do private endpoints / VNet integrations failover?  
- What about data residency evidence for auditors?  
- How do you handle long-lived WebSockets/SSE?  
- When is brownout better than failover?  
- How do feature flags interact with split regions?  
- What is the billing impact of warm DR?  
- How do you prevent CI from undeploying the new primary?

### 7.10 Related prompts

- Regional AI / Copilot prompts  
- Distributed KV / cache  
- Logging system  
- Key Vault  
- World-scale website  

---

## 8. Appendices

### Appendix A — Incident object schema

```json
{
  "incident_id": "uuid",
  "stamp_id": "m365-copilot-euw-01",
  "region": "westeurope",
  "state": "declared_failover",
  "failure_mode": "capacity_overload|outage|brownout",
  "signals": [{"name":"gpu_free","value":0.02}],
  "plan_id": "uuid",
  "approvals": [{"step":"promote_sql","by":"user@contoso.com"}],
  "started_at": "...",
  "completed_at": null
}
```

### Appendix B — Orchestrator step table

```sql
CREATE TABLE failover_steps (
  plan_id      UUID NOT NULL,
  seq          INT NOT NULL,
  name         TEXT NOT NULL,
  adapter      TEXT NOT NULL,
  payload      JSONB NOT NULL,
  status       TEXT NOT NULL, -- pending|running|succeeded|failed|skipped
  attempts     INT NOT NULL DEFAULT 0,
  evidence     JSONB,
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (plan_id, seq)
);
```

### Appendix C — DR class checklist

| DR class | Warm compute | Data | Traffic | GPU |
|----------|--------------|------|---------|-----|
| Platinum | Active-active | sync/near | auto fractional | reserved |
| Gold | Warm 50% | async geo | auto | partial reserved |
| Silver | Cold + images | async | manual | best effort |
| Bronze | Rebuild | backups | manual | none |

### Appendix D — Scale checklist

| Scale | Must add |
|-------|----------|
| 1× | Pair region, failover endpoints, runbook, AFD |
| 10× | Stamp templates, secret replication, synthetics |
| 100× | DAG orchestrator, capacity broker, GameDays |
| 1,000× | Global fabric, automated evidence, GPU DR market |

### Appendix E — Glossary

| Term | Meaning |
|------|---------|
| Stamp | Deployable regional unit of a service |
| Pair region | Residency-legal DR counterpart |
| Fence | Prevent old primary from serving/writes |
| Promote | Secondary → primary for stateful store |
| Fractional cutover | Weighted traffic shift |
| GameDay | Scheduled failover drill |
| Capacity broker | Allocates scarce CPU/RU/GPU to plans |
| Residency compiler | Legal target filter |
| RPO/RTO | Data loss / downtime objectives |
| Brownout | Partial impairment vs hard down |

### Appendix F — Estimation cheat-sheet

```text
Backlog bytes ≈ lag_seconds × write_bytes_per_s
Control-plane time ≈ resources × calls_per_resource / rps
DNS-only failover ≥ TTL (often worse)
GPU RTO often dominates AI stamps
```

### Appendix G — Sample customer comms

```text
We are failing over Contoso API from West Europe to North Europe due to regional capacity issues.
EU data residency is preserved. Some Copilot features run on a faster model until GPU capacity recovers.
```

### Appendix H — Preflight checklist

- [ ] Target images present in ACR  
- [ ] KV secrets synced  
- [ ] MI RBAC granted  
- [ ] SQL/Cosmos lag within RPO  
- [ ] GPU watermark reservable  
- [ ] AFD origin healthy  
- [ ] Synthetics configured  
- [ ] Approvers online  
- [ ] Residency policy green  
- [ ] Comms draft ready  

### Appendix I — Rollback triggers

- Error rate > 2× baseline after 5% traffic  
- Data verify fail  
- Fence incomplete  
- Legal policy mismatch discovered  
- Target capacity collapse  

### Appendix J — Interview whiteboard order

1. Failure modes  
2. Workload classes table  
3. Detection → decision → orchestration  
4. Pair-region diagram  
5. SQL/Cosmos + fence  
6. AFD fractional shift  
7. GPU/residency  
8. GameDay  

---

*End of design doc. Open with RPO/RTO + residency; whiteboard §4; close with fence invariants and traps §7.*
