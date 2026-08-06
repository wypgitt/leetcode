<!-- Adapted into Fundamentals bank from Amazon/email-delivery-system-system-design.md for cross-company prep. -->

# System Design: Email Delivery System (Amazon Transactional + Marketing)

> **Focus areas:** Template rendering · Preference/consent · Durable outbox · Provider routing · Retries/backoff · Bounce/complaint handling · Deliverability · Idempotency · Multi-tenant isolation  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split transactional vs marketing QPS, explicit deal-breakers, at-least-once with idempotent send keys  
> **Interview theme:** Amazon SDE III / L6 — **Customer Communications** — SES-class reliability with retail trust and marketplace isolation

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

Goal: **bound the email product**—what we guarantee for order/shipping/security mail vs marketing campaigns, how we respect consent, and how we isolate noisy tenants and bad providers at Amazon retail scale.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Reliable outbound email with templates, prefs, delivery tracking | Full ESP product UI for SMBs |
| Planes | Ingest → render → enqueue → send → feedback | Sync SMTP from checkout thread |
| Success | Deliverability + trust + latency SLOs by class | Open-rate vanity alone |

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who sends? | Internal services (Orders, Payments, Security, Marketing) | Producer API + durable outbox |
| F2 | Mail classes? | **Transactional** vs **marketing** (priority isolation) | Separate queues, quotas, SLOs |
| F3 | Templates? | Versioned templates + locale + marketplace | Template service; render workers |
| F4 | Personalization? | Order details, ASINs, deep links | Structured data + safe HTML render |
| F5 | Consent/prefs? | Marketing requires opt-in; transactional always (legal carve-outs) | Preference store gate before enqueue |
| F6 | Delivery semantics? | **At-least-once**; dedupe by `send_id` / idempotency key | Idempotent send ledger |
| F7 | Providers? | Amazon SES-class + failover ESP | Provider router + health scores |
| F8 | Feedback? | Bounces, complaints, deliveries, opens/clicks (sampled) | Feedback ingest → suppression lists |
| F9 | Suppression? | Hard bounce / complaint / unsubscribe | Global + tenant suppressions |
| F10 | Observability? | Per-message status, latency, provider codes | Customer-service lookup + dashboards |
| F11 | Attachments? | Rare for transactional; size caps | Object store pointer pattern |
| F12 | Multi-marketplace? | Locale, From domain, legal footer per marketplace | Cell/key by marketplace |

**MVP functional scope (lock with interviewer):**

1. Producers submit **SendEmail** with idempotency key, template id, data, class, marketplace.  
2. **Durable accept** before ACK; preference/consent check for marketing.  
3. Render HTML/text; assemble headers; DKIM/SPF domain alignment.  
4. Priority queues; workers send via provider; retries with backoff → DLQ.  
5. Bounce/complaint webhooks update suppression; CS can look up `message_id`.  
6. Basic metrics: enqueue, send, bounce, complaint, p99 by class.

**Out of MVP (explicitly defer):**

- Full visual campaign builder  
- Perfect open tracking without privacy tradeoffs  
- SMS/push unified inbox (mention hooks only)  
- Exactly-once without provider cooperation  
- Per-user inbox product (this is outbound delivery)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Transactional freshness | Order confirmation fast | p50 < 5s, p99 < 30s healthy path |
| N2 | Marketing freshness | Soft real-time / batch windows | Minutes OK; fairness across tenants |
| N3 | Durability | No lost accepted sends | Quorum/disk before producer ACK |
| N4 | Availability | High for ingest | 99.9%+ ingest; isolate provider outages |
| N5 | Multi-tenant fairness | One campaign ≠ stall OTP mail | Class + tenant isolation |
| N6 | Deliverability | Reputation protected | Complaint rate << industry thresholds |
| N7 | Security | No SSRF in links; no PII in logs raw | Redaction; signed tracking tokens |
| N8 | Scale | Up to ~1000× send/s class | Progressive scale table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Order placed → Orders service outbox → Email platform accepts → render → SES send → Delivery event.  
2. Marketing campaign scheduled → fan-out recipients → preference filter → paced send.  
3. Hard bounce → suppress address → future marketing skipped; transactional policy explicit.  
4. User unsubscribes → preference update → nearline enforcement.  
5. Provider A degraded → router shifts traffic to B for new sends; in-flight retries careful.  
6. Duplicate producer submit with same key → one logical send.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Producer double publish | Idempotency key → one send ledger row |
| Worker crash after provider 200 | Reconcile via provider message id; don’t double-email blindly |
| Template render throws | Fail send to DLQ; alert template owners; don’t block queue |
| Preference store timeout | **Fail closed for marketing**; transactional may proceed with cache |
| Complaint spike | Auto throttle tenant/campaign; page deliverability |
| OTP mail delayed | Priority lane; page SEV if p99 burns |
| Link tracking broken | Degrade tracking; never break unsubscribe link |
| Huge campaign | Paced enqueue; recipient sharding; budgeted QPS |
| Marketplace legal footer wrong | Template/marketplace version gate; fail closed |
| Attachment too large | Reject at ingest |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Marketplaces | 5 | 10 | 20 | 20+ |
| Producing services | 50 | 100 | 300 | 1K |
| Templates | 2K | 10K | 50K | 200K |
| Sends / day | 100M | 1B | 10B | 100B |
| Peak **ingest** QPS | ~2K | ~20K | ~200K | ~2M |
| Peak **send attempts**/s | ~3K | ~30K | ~400K | ~4M+ |
| Transactional share | 40% | 40% | 35% | 30% |
| Marketing share | 60% | 60% | 65% | 70% |
| Avg retries | 1.2× | 1.2× | 1.3× | 1.4× |
| Suppression list size | 50M | 200M | 1B | 5B |
| Feedback events /s | ~1K | ~10K | ~100K | ~1M |

**What each jump forces:**

- **10×:** Durable outbox; class queues; template cache; provider retries; suppression Redis.  
- **100×:** Marketplace cells; shuffle sharding; paced campaign scheduler; cold feedback store.  
- **1,000×:** Hierarchical campaign fan-out; multi-ESP platform; reputation cells; approximate analytics.

### 1.5 Constraints & Assumptions

- Amazon themes: customer trust (OTP/order mail), ownership, frugality, mechanisms over meetings.  
- Email is **best-effort at provider**; we own accept durability + retry policy + reputation.  
- Marketing never blocks transactional lanes.  
- Repeat scope in one breath: *“Durable multi-class email platform with templates, consent, provider routing, and bounce suppression.”*

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Planes

| Plane | Work | Latency class |
|-------|------|---------------|
| Ingest/API | Validate, idempotency, durable write | < 50–100ms p99 |
| Render | Template + data → MIME | Async workers |
| Send | Provider HTTPS/SMTP | Async; provider RTT |
| Feedback | Bounce/complaint/delivery | Nearline |
| Analytics | Opens/clicks aggregates | Batch / sampled |

### 2.2 Storage rough math (baseline day)

- 100M sends/day × ~2KB metadata ≈ 200 GB/day metadata (before compression).  
- Rendered body optional store: sample or pointer; don’t keep full HTML forever.  
- Suppression: 50M keys × ~50B ≈ 2.5 GB hot set—fits Redis/cluster.  
- Feedback 30 days hot; older to S3/cold.

### 2.3 Throughput

Peak send 3K/s × 1.2 retries ≈ 3.6K provider calls/s. At 100× (~400K/s attempts) you need partitioned workers, connection pools, and provider account sharding—not a single SES quota.

### 2.4 Cost levers

- Deduplicate aggressively  
- Pace marketing  
- Cache templates  
- Drop open-pixel vanity at scale  
- Compress/cold-tier logs  

Track **$/1K accepted sends** and **$/1K delivered**.

### 2.5 Capacity sketch

```text
send_workers ≈ (peak_attempt_QPS × avg_provider_sec) / (conns_per_worker × util)
```

Headroom 2–3×; separate fleets for transactional vs marketing.

---

## 3. High-Level Design

### 3.1 Components

1. **Email API / Ingest** — auth, schema validate, class, marketplace, idempotency.  
2. **Send Ledger (SoT)** — durable `send_id` state machine.  
3. **Preference/Consent Service** — marketing gates; transactional policy.  
4. **Template Service** — versioned templates, locales, approval.  
5. **Render Workers** — safe HTML; link rewriting; MIME build.  
6. **Priority Queues** — txn / marketing / low; per-tenant fairness.  
7. **Provider Router + Send Workers** — SES + failover; health scores.  
8. **Feedback Ingest** — SNS/webhooks → suppressions + status.  
9. **Suppression Store** — hot keys; async rebuild.  
10. **Observability / CS Lookup** — message timeline.

### 3.2 State machine (simplified)

```text
ACCEPTED → RENDERED → SENDING → SENT → DELIVERED
                \→ FAILED_RETRYABLE → (backoff) → SENDING
                \→ FAILED_TERMINAL / SUPPRESSED / DLQ
```

### 3.3 Tradeoffs

| Decision | Choose | Reject (deal-breaker) |
|----------|--------|------------------------|
| Durability | Outbox/ledger before ACK | Fire-and-forget from checkout |
| Isolation | Class + tenant queues | One FIFO for all mail |
| Consent | Fail closed marketing | Send marketing on pref timeout |
| Provider | Multi-provider router | Hardcode one vendor forever |
| Idempotency | Stable send_id | New message every retry blindly |

### 3.4 APIs (sketch)

```text
POST /v1/email/send
  Idempotency-Key: ...
  { class, template_id, template_version?, locale, marketplace,
    to, data, tags, schedule_at? }

GET /v1/email/messages/{send_id}
POST /v1/preferences/unsubscribe
Admin: pause tenant, redrive DLQ, rotate DKIM
```

---

## 4. Architecture Diagram

```text
Producers (Orders, Pay, Security, Mkt)
        |  idempotent SendEmail
        v
   Email API  ---> Send Ledger (durable)
        |              |
        v              v
 Preferences -----> Render Workers --> MIME
        |              |
        v              v
   Suppression     Priority Queues
   (hot)           [TXN] [MKT] [BULK]
                       |
                       v
               Provider Router
                 /         \
              SES/ESP-A   ESP-B
                       |
                       v
              Feedback Webhooks
                       |
            Status + Suppressions + Metrics
                       |
                 CS Lookup / Portal
```

**Cell sketch (100×+):**

```text
Marketplace cell: US | EU | JP
  each: ledger shard + queues + template cache + provider accounts
Global: suppression bloom/seed sync (eventual) + reputation control plane
```

---

## 5. Design Deep Dive

### 5.1 Invariants

1. Accepted send is durable before producer ACK.  
2. Same idempotency key + body hash → same `send_id`.  
3. Marketing never sends if consent unknown/denied.  
4. Transactional lane not blocked by marketing backlog.  
5. Hard-bounce/complaint addresses suppressed for marketing.  
6. Template+marketplace legal requirements enforced.  
7. Provider response recorded; retries bounded → DLQ.

### 5.2 Idempotency & exactly-once illusion

At-least-once to provider; **effectively-once to customer** via:
- Idempotency key at ingest  
- Provider idempotency keys where supported  
- Reconciliation if worker dies after 200  

Document that duplicate rare emails possible under split-brain; minimize with lease + provider keys.

### 5.3 Deliverability & reputation

- Dedicated IPs/domains per class/marketplace when scale warrants  
- Warmup schedules  
- Complaint/bounce auto-throttle  
- List hygiene  
- Authenticated domains (SPF/DKIM/DMARC)  

Reputation is a **shared resource**—noisy tenant can harm others → isolation.

### 5.4 Preference consistency

Preference updates: strong-ish read-your-writes for unsubscribe links; nearline cache with short TTL. Marketing fail-closed on uncertainty. Transactional: legal/security mail may bypass marketing prefs (state policy).

### 5.5 Progressive scale deep dive

| Jump | Architecture move |
|------|-------------------|
| 10× | Ledger + queues + template cache + Redis suppression |
| 100× | Marketplace cells; shuffle shard send workers; campaign pacing service |
| 1,000× | Hierarchical fan-out (campaign → shard jobs → micro-batches); multi-ESP platform; approx open analytics |

### 5.6 Rendering safety

- Strict templating (no arbitrary code)  
- HTML sanitizer  
- URL allowlists for tracking redirects  
- PII minimization in templates/logs  
- Version pin; canary templates

### 5.7 Failure modes

| Failure | Degrade |
|---------|---------|
| Provider down | Failover; backlog; page if txn SLO burns |
| Pref store down | Marketing pause; txn continue |
| Render spike | Autoscale; shed bulk first |
| Feedback flood | Buffer; prioritize complaints |
| Hot tenant | Quotas; isolate queue |

### 5.8 Data model (sketch)

```text
sends(send_id, idem_key, class, status, template_id, ver, marketplace,
      provider, provider_msg_id, created_at, updated_at, next_attempt_at)
send_attempts(send_id, attempt_n, provider, code, latency_ms, ts)
suppressions(address_hash, reason, marketplace, updated_at)
preferences(user_id, channel, topic, opted_in, updated_at)
templates(template_id, ver, marketplace, locale, body, approved)
```

### 5.9 Security

- AuthN producers (mTLS/IAM)  
- No open relay  
- Signed unsubscribe tokens  
- Redact emails in logs (hash/tokenize)  
- DKIM key rotation  
- Attachment malware scan if enabled

---

## 6. Wrap-Up

### 6.1 What we designed

Multi-class durable email platform: ingest ledger, preferences, templates, render, isolated queues, provider routing, feedback/suppression, progressive cells.

### 6.2 Key decisions worth defending

1. Durable accept before ACK  
2. Transactional/marketing isolation  
3. Fail-closed marketing consent  
4. Idempotent send_id + provider reconciliation  
5. Reputation/tenant isolation  
6. Marketplace cells at 100×  

### 6.3 Risks & follow-ups

- Rare duplicate mail under crashes  
- Deliverability politics across tenants  
- Template misuse / phishing-looking mail  
- Cost of storing bodies  
- Privacy of open/click tracking  

### 6.4 Closer

> **Email Delivery System**: durable multi-class sends, consent, provider routing, suppression, ownership, progressive scale, customer trust (OTP/order mail).

---

## 7. Deeper / Related Interview Questions — Email Delivery

**Q1. Why not send SMTP directly from the Orders service?**

**A:** Couples checkout latency to provider; no shared prefs/suppression/reputation; retries/crash handling duplicated; deal-breaker for platformization.

**Q2. How do you guarantee order confirmation email isn’t stuck behind a marketing blast?**

**A:** Separate queues/fleets/quotas; weighted fair queuing; txn SLO pages independently; marketing shed first.

**Q3. What happens when SES returns 429?**

**A:** Backoff + jitter; respect quotas; spill to secondary provider if policy allows; don’t spin hot loops; tenant pacing.

**Q4. How do you handle unsubscribe under CAP theorem pressure?**

**A:** Prefer fail-closed for marketing; short-TTL cache; signed token path updates SoT; accept brief over-suppress rather than spam.

**Q5. Open tracking vs privacy?**

**A:** Sample or disable by marketplace/regulation; never make delivery success depend on pixels; document Apple MPP noise.

**Q6. How do you redrive DLQ safely?**

**A:** Filter poison templates; rate-limited redrive; new attempt under same send_id policy; audit who redrove.

**Q7. Multi-region active-active?**

**A:** AA ingest gateways OK; **home cell** for send ledger by marketplace/user to avoid dual-send; careful global suppression sync.

**Q8. Deal-breaker?**

**A:** Fire-and-forget email from checkout without durability; or marketing sharing a single FIFO with OTP mail.


## 9. Interview Walkthrough (45 min)

| Time | Focus |
|------|-------|
| 0–5 | Scope + Amazon ownership lens |
| 5–12 | Estimation + progressive scale |
| 12–22 | HLD + ASCII diagram |
| 22–35 | Deep dive (reliability/scale/trust) |
| 35–45 | Tradeoffs, deal-breakers, Q&A |

Restate customer impact; lock MVP; split load classes; name pager owners; refuse deal-breakers.

---

## 10. Operability

### Golden signals
Latency, traffic, errors, saturation, freshness/backlog, trust incidents.

### Rollback ladder
Flag off → revert artifact → shed/reduce load → cell isolate → postmortem with trust section.

### Kill switches
Disable optional stage; freeze nearline; revert pointer; shed traffic; isolate cell/tenant.

### Security/privacy baseline
Authn/z, PII TTLs, encryption, cell isolation, signed artifacts, abuse limits, audit trails.

### Cost worksheet
Dominant cost driver; fastest unit-cost lever; 10× cost with/without architectural jump.

```text
instances ≈ peak_QPS × cpu_sec / (cores × util)
```

### Progressive scale
10× cache/shard/async; 100× cells/partition/edge; 1,000× approximate/platform/multi-tenant cells.

### Cross-team deps
Identity, catalog/inventory, payments, notifications, experimentation, logging — each with failure mitigation.

## More Interview Q&A — Email Delivery System

**Q1. How do you model email state?**

**A:** Append-only attempts + current status on ledger; never delete history needed for audit.

**Q2. Bloom filter for suppression?**

**A:** Optional at 1,000× for negative checks; SoT remains DB; false positives over-suppress (fail closed OK for marketing).

**Q3. How to test templates?**

**A:** Snapshot render tests per marketplace/locale; visual diff canary; PII fixture packs.

**Q4. What is a poison campaign?**

**A:** Render/exception loop or bad links; circuit-break template_id; DLQ without blocking other templates.

**Q5. Click tracking legality?**

**A:** Marketplace policy packs; consent where required; signed short-lived tokens.

**Q6. How do cells fail over?**

**A:** Secondary warm standby ledger shards; DNS/traffic shift; suppress dual-active writers.

**Q7. SES vs custom SMTP relay?**

**A:** Prefer managed ESP; custom relay only with clear ownership of IP reputation.

**Q8. How to handle role accounts like noreply@**

**A:** Policy: allow send from; ignore inbound; monitoring aliases separate.

**Q9. Calendar invites?**

**A:** Out of MVP; specialty MIME path.

**Q10. Metric for deliverability?**

**A:** Complaint%, hard-bounce%, deferred%, inbox placement samples—not just ‘sent’.

**Q11. How do producers authenticate?**

**A:** IAM/mTLS; per-producer quotas; blast radius limits.

**Q12. Scheduled sends?**

**A:** schedule_at with durable wake; avoid huge due-at thundering herds—jitter.

**Q13. What belongs in tags?**

**A:** order_id, campaign_id, team—for attribution; not raw PII.

**Q14. Can marketing use txn From domain?**

**A:** No—reputation isolation; separate domains.

**Q15. How fast is unsubscribe?**

**A:** User-visible minutes; enforce nearline; legal SLAs by region.

**Q16. Deal-breaker restated?**

**A:** No durability; shared FIFO; marketing without consent gate.

## Deep Technical Addenda — Email Delivery System


### Send ledger design

Partition by `hash(send_id)` or carefully chosen keys—prefer send_id for point lookups. Secondary index `idem_key` unique. TTL/archival of bodies separate from status rows.

### Provider adapter interface

```text
send(msg) -> provider_msg_id | retryable_error | terminal_error
inquire(provider_msg_id) -> status
```

Adapters normalize codes; router uses health EMA + error budget.

### Campaign hierarchy

```text
Campaign → ShardPlan (N shards) → MicroBatch (10K recipients) → SendTasks
```

Each level checkpoints; restartable; paced by token buckets.

### Reputation control plane

Global service assigns IP pools, warmup rates, throttle instructions to cells. Emergency push path for complaint crises.

### Privacy of engagement

Prefer aggregated opens/clicks; differential privacy optional at 1,000× analytics; never sell per-user engagement externally.

### Cross-channel hooks

Same preference topics may gate SMS/push later; keep preference schema channel-aware.

### Testing

Chaos: kill send workers mid-flight; preference timeout; provider 500s; duplicate webhooks; template CPU bomb.


## Tradeoff Matrices — Email Delivery System

### Consistency vs latency

| Choice | Latency | Correctness | Use when |
|--------|---------|-------------|----------|
| Sync durable then serve | Higher | Stronger | Money/trust/enforcement paths |
| Serve then async durable | Lower | Risk window | Non-money UX with repair |
| Cached eventual | Lowest | Stale OK | Read-heavy dashboards / portals |

### Exact vs approximate

| Choice | Cost | UX risk | Use when |
|--------|------|---------|----------|
| Exact | High at scale | Low confusion | Checkout, ledger, rating |
| Approximate labeled | Lower | Need UX copy | Analytics, spectate fan-out |
| Hierarchical | Medium | Ops complexity | Multi-region aggregates |

### Availability vs correctness

| Choice | Availability | Correctness | Use when |
|--------|--------------|-------------|----------|
| Fail closed | Lower during dep outage | Safer trust | Fraud, consent, money |
| Fail open degrade | Higher | Risk wrong UX | Optional personalization |
| Shed load | Partial | Protects core | Peak storms |

## Operability Addenda — Email Delivery System

### Deploy pipeline

```text
build artifact → static validation → shadow → canary → bake → full
                     ↓ fail              ↓ guardrail fail
                  reject              auto rollback
```

### Guardrail examples

- p99 latency regression > threshold  
- error/empty/fallback rate rise  
- safety/privacy/trust denials anomaly  
- cost/unit-economics spike  
- backlog/DLQ growth beyond budget  

### Kill switches (name them in interview)

1. Disable optional stage / feature flag  
2. Freeze nearline updates  
3. Revert artifact pointer / config version  
4. Shed traffic / reduce concurrency / reduce K  
5. Cell isolation / pause tenant or marketplace  

### Oncall first five minutes

1. Check golden signals and recent deploys  
2. Confirm blast radius (cell / marketplace / tenant)  
3. Engage kill switch if customer-trust burning  
4. Preserve evidence (logs, samples, config versions)  
5. Customer messaging path if trust incident  

### Cost worksheet

Speak: peak demand → per-node capacity → headroom 2–3× → cache/async/edge lever → what 10× does → architectural jump that bends the curve.

## Worked Capacity Narrative — Email Delivery System

Speak in this order: (1) peak demand math, (2) per-node capacity assumption, (3) headroom factor 2–3×, (4) cache/async/edge lever, (5) what 10× does to the equation, (6) the architectural jump that bends the curve instead of linear hardware growth.

## Customer-Trust Paragraph — Email Delivery System

Amazon interviews reward explicit trust reasoning: wrong charges, undelivered critical mail, broken promotions, unfair games, privacy leaks, or silent data loss are not “ops issues”—they are customer-trust incidents. Put fail-closed vs fail-open choices next to the customer impact, not only next to availability percentages.

## Progressive Scale Recap — Email Delivery System

- **10×:** caching, shard split, async offload, sampling, tighter budgets  
- **100×:** cells, hierarchical aggregation, partitioned queues, edge/client head  
- **1,000×:** platform multi-tenant cells, approximate algorithms, specialized fleets  

For each jump, state **what breaks if you only add servers**.

## Supplemental Depth Pack — Email Delivery System
### S1. Ingest durability

Ledger/outbox before ACK; schema validation; producer auth.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S2. Render isolation

Sandbox templates; CPU/memory limits; poison template → DLQ.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S3. Fair queuing

Tenant token buckets; class priority; aging prevention for bulk.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S4. Provider accounts

Shard by reputation pool; warmup; per-marketplace domains.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S5. Suppression correctness

Address normalization; hash keys; reason precedence.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S6. Exactly-once myth

At-least-once + idempotency; document residual duplicate risk.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S7. Observability

Funnel: accepted→rendered→sent→delivered/bounced; break by class.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S8. Disaster recovery

Ledger backups; cell failover; replay with idempotency.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S9. Security mail

Highest priority; minimal deps; pre-rendered critical templates cached.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S10. Abuse

Internal producer quotas; template review; phishing-similar detection hooks.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S11. Localization

Locale fallback chain; marketplace legal strings; RTL HTML tests.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S12. Attachments

Size cap; S3 pointer; malware scan; rare path.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S13. Click redirects

Signed tokens; expiry; SSRF-safe allowlist destinations.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S14. Batch vs realtime

Campaign scheduler vs event-driven txn; different economics.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S15. Unit economics

Track $/1K sends; complaint cost as reputation externality.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?
### S16. Platformization

Shared email platform; per-team quotas; chargeback; SLOs.
**Invariant:** Write the rule as a testable assert in design review.
**Metric:** Name a dashboard panel that detects violation within minutes/hours as appropriate.
**10× note:** Explain whether this theme’s mechanism still holds or must jump architecturally.
**Ownership:** Serving vs science vs privacy/policy—who pages?

## Interview Cards — Email Delivery System

### Card 1: Durable outbox before ACK

Producer gets 200 only after send ledger quorum write. Crash windows reconciled via provider ids.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 2: Class isolation

Txn vs marketing fleets and quotas. Marketing never burns OTP SLO.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 3: Consent fail-closed

If preference store uncertain, skip marketing. Security/order mail follows legal policy.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 4: Idempotent send_id

Idempotency-Key + body hash. Retries don’t create new customer-visible duplicates without reconciliation.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 5: Provider router

Health scores, sticky retries, failover rules that don’t dual-send uncertain in-flight.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 6: Suppression hot path

Redis/cluster for bounce/complaint; async rebuild from SoT; bloom optional at 1,000×.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 7: Campaign pacing

Hierarchical fan-out; per-tenant token buckets; warm IP pools.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 8: Template versioning

Pin version at accept; canary; rollback pointer; marketplace legal footers.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 9: Feedback pipeline

Verify webhooks; idempotent apply; complaint spikes auto-throttle.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 10: CS lookup

Message timeline by send_id/order_id without scanning raw provider logs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 11: PII in logs

Hash/tokenize addresses; structured reason codes; retention TTLs.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 12: DKIM rotation

Dual-key window; domain alignment monitors; page on auth failure spikes.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 13: Cell key

Marketplace (+ maybe class mega-cell). Avoid one global mega-queue.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 14: Cost lever #1

Pace marketing + drop vanity tracking + cold-tier bodies.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 15: Deal-breaker

Sync SMTP in checkout; shared FIFO OTP+blast; marketing on unknown consent.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

### Card 16: SEV definition

OTP/order p99 burn or complaint-rate reputation incident = customer-trust SEV.

**Follow-ups to expect:** What breaks at 10×? Who pages? What is the fallback? What metric proves it worked?

**Amazon ownership angle:** Name the two-pizza boundary, the artifact you deploy, and the customer-trust failure mode if this card is ignored for email delivery.

## Related Deep Dive Q&A — Email Delivery System

**RQ1. Why does 'Durable accept' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Durable accept'. Name who pages and what artifact version you roll back.

**RQ2. How would you test 'Durable accept' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Durable accept'.

**RQ3. What regresses if 'Durable accept' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Durable accept'.

**RQ4. Why does 'Class isolation' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Class isolation'. Name who pages and what artifact version you roll back.

**RQ5. How would you test 'Class isolation' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Class isolation'.

**RQ6. What regresses if 'Class isolation' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Class isolation'.

**RQ7. Why does 'Consent fail-closed' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Consent fail-closed'. Name who pages and what artifact version you roll back.

**RQ8. How would you test 'Consent fail-closed' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Consent fail-closed'.

**RQ9. What regresses if 'Consent fail-closed' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Consent fail-closed'.

**RQ10. Why does 'Provider failover' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Provider failover'. Name who pages and what artifact version you roll back.

**RQ11. How would you test 'Provider failover' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Provider failover'.

**RQ12. What regresses if 'Provider failover' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Provider failover'.

**RQ13. Why does 'Suppression lists' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Suppression lists'. Name who pages and what artifact version you roll back.

**RQ14. How would you test 'Suppression lists' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Suppression lists'.

**RQ15. What regresses if 'Suppression lists' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Suppression lists'.

**RQ16. Why does 'Campaign pacing' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Campaign pacing'. Name who pages and what artifact version you roll back.

**RQ17. How would you test 'Campaign pacing' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Campaign pacing'.

**RQ18. What regresses if 'Campaign pacing' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Campaign pacing'.

**RQ19. Why does 'Template canary' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Template canary'. Name who pages and what artifact version you roll back.

**RQ20. How would you test 'Template canary' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Template canary'.

**RQ21. What regresses if 'Template canary' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Template canary'.

**RQ22. Why does 'Webhook idempotency' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Webhook idempotency'. Name who pages and what artifact version you roll back.

**RQ23. How would you test 'Webhook idempotency' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Webhook idempotency'.

**RQ24. What regresses if 'Webhook idempotency' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Webhook idempotency'.

**RQ25. Why does 'Marketplace cells' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Marketplace cells'. Name who pages and what artifact version you roll back.

**RQ26. How would you test 'Marketplace cells' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Marketplace cells'.

**RQ27. What regresses if 'Marketplace cells' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Marketplace cells'.

**RQ28. Why does 'DKIM/DMARC' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'DKIM/DMARC'. Name who pages and what artifact version you roll back.

**RQ29. How would you test 'DKIM/DMARC' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'DKIM/DMARC'.

**RQ30. What regresses if 'DKIM/DMARC' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'DKIM/DMARC'.

**RQ31. Why does 'PII redaction' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'PII redaction'. Name who pages and what artifact version you roll back.

**RQ32. How would you test 'PII redaction' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'PII redaction'.

**RQ33. What regresses if 'PII redaction' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'PII redaction'.

**RQ34. Why does 'DLQ redrive' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'DLQ redrive'. Name who pages and what artifact version you roll back.

**RQ35. How would you test 'DLQ redrive' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'DLQ redrive'.

**RQ36. What regresses if 'DLQ redrive' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'DLQ redrive'.

**RQ37. Why does 'OTP priority' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'OTP priority'. Name who pages and what artifact version you roll back.

**RQ38. How would you test 'OTP priority' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'OTP priority'.

**RQ39. What regresses if 'OTP priority' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'OTP priority'.

**RQ40. Why does 'Reputation throttle' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Reputation throttle'. Name who pages and what artifact version you roll back.

**RQ41. How would you test 'Reputation throttle' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Reputation throttle'.

**RQ42. What regresses if 'Reputation throttle' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Reputation throttle'.

**RQ43. Why does 'Multi-ESP routing' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Multi-ESP routing'. Name who pages and what artifact version you roll back.

**RQ44. How would you test 'Multi-ESP routing' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Multi-ESP routing'.

**RQ45. What regresses if 'Multi-ESP routing' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Multi-ESP routing'.

**RQ46. Why does 'Cost per 1K sends' matter in an L6 interview?**

**A:** State the mechanism, the deal-breaker alternative, and the unit-cost or customer-trust implication for 'Cost per 1K sends'. Name who pages and what artifact version you roll back.

**RQ47. How would you test 'Cost per 1K sends' in staging?**

**A:** Define fixtures, chaos/failure injection, canary metrics, and a rollback path. Include at least one customer-trust assertion for 'Cost per 1K sends'.

**RQ48. What regresses if 'Cost per 1K sends' is ignored at 100×?**

**A:** Latency/error-budget burn, trust incidents, or linear cost growth. State which progressive-scale jump (10×/100×/1,000×) fixes 'Cost per 1K sends'.

## Narrative Walkthrough — Email Delivery System

### Walkthrough beat 1

Customer places an order. Orders service writes an outbox event and calls Email API with Idempotency-Key=order_id+event. Ingest validates marketplace/template, writes ACCEPTED to the send ledger, and ACKs in <100ms. Preference check is skipped for transactional class. Render worker builds MIME with order details; send worker routes to SES; Delivery webhook marks DELIVERED. Watch txn p99 and provider error rate live.

### Walkthrough beat 2

Marketing launches a Prime Day campaign to 50M users. Scheduler creates hierarchical shard jobs; each micro-batch checks preferences and suppressions; paced send protects IP reputation. If complaint rate spikes, auto-throttle engages and pages Deliverability. Transactional fleets remain untouched—call out the isolation tradeoff Amazon customer obsession requires.

### Walkthrough beat 3

SES regional degradation: router shifts new traffic to ESP-B; in-flight uncertain sends reconcile via provider message id inquiry—not blind resend. CS lookup still works from ledger. Mention artifact versions: template ver, router config ver, suppression snapshot lag.

## Scenario Runbooks — Email Delivery System

### SEV: OTP email p99 > 2 minutes

1. Confirm class=security/txn dashboards and provider health.
2. Check marketing fleets not sharing workers (misconfig).
3. Engage kill: pause bulk/marketing; scale txn workers.
4. Failover provider if SES errors elevated.
5. Preserve samples; customer messaging if login impacted.
6. Postmortem: queue isolation + quota tests.

### Complaint rate spike on marketplace DE

1. Identify campaign/tenant via tags.
2. Auto-throttle already? If not, pause campaign.
3. Verify unsubscribe links and preference lag.
4. Check list quality / purchased lists (policy violation).
5. Reputation pool isolation for next sends.

### Duplicate order emails reported

1. Pull send_id by order_id; inspect attempts and provider ids.
2. Check producer idempotency misuse (different keys).
3. Check worker crash window + missing provider idempotency.
4. Patch reconciliation; communicate rarity + fix.

## Appendices — Email Delivery System

### A — Glossary
| Term | Meaning |
|------|---------|
| Cell | Failure-isolated unit (marketplace/region/tenant) |
| Nearline | Minutes-latency path |
| Canary | Partial bake of artifact |
| Deal-breaker | Non-negotiable bad design |
| Two-pizza | Ownership team with pager |
| SoT | Source of truth |
| DLQ | Dead-letter queue |
| PIT | Point-in-time (features/state) |
| Transactional mail | Order/OTP/security—high priority |
| ESP | Email service provider |
| Suppression | Do-not-send address list |
| DKIM | DomainKeys Identified Mail |
| Warmup | Gradual IP sending ramp |

### B — Oncall checklist
- [ ] SLOs green / error budget known
- [ ] Rollback armed
- [ ] Kill switches known
- [ ] Cost dashboards
- [ ] Privacy/safety/trust tested
- [ ] DLQ/backlog within budget
- [ ] Recent deploys identified

### C — Topic closer checklist
- [ ] Durable accept + idempotency
- [ ] Txn/marketing isolation
- [ ] Consent fail-closed
- [ ] Provider router + feedback
- [ ] Suppression + CS lookup
- [ ] Progressive cells 10×/100×/1,000×

### D — Metric dictionary (speak these)

| Metric | Why it matters |
|--------|----------------|
| p99 latency by class | Split interactive vs async |
| Error / reject rate | Customer pain |
| Backlog age / DLQ depth | Hidden debt |
| Unit cost ($/1K ops) | Frugality |
| Trust incident count | Leadership principle signal |
| Cache hit rate | Scale lever |
| Cell saturation | Isolation health |

### E — Failure injection catalog

| Inject | Expect |
|--------|--------|
| Dependency timeout | Deadline shed / fallback |
| Dual publish / retry storm | Idempotent no double effect |
| Hot partition | Reshard / isolate |
| Clock skew | Bounded error or fail closed |
| Region loss | Cell failover story |
| Poison message | DLQ, not partition death |

### F — Amazon leadership-principle hooks

| Principle | How it shows in this design |
|-----------|------------------------------|
| Customer Obsession | Explicit trust fail-closed/open |
| Ownership | Named two-pizza + pager |
| Invent & Simplify | Prefer fewer planes with clear contracts |
| Frugality | Unit-cost levers before linear scale-out |
| Dive Deep | Metrics + invariants + runbooks |
| Bias for Action | Kill switches and rollback ladder |
| Earn Trust | Auditability, no silent money/promo bugs |

### G — One-breath closer

> **Email Delivery System**: explicit planes, SLOs, ownership, progressive scale (10×/100×/1,000×), customer trust, unit economics.

---


*End of Email Delivery System system design prep doc.*
