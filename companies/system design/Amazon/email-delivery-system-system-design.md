# System Design: Email Delivery System (Transactional + Marketing)

> **Focus areas:** Intake API · Templates · Personalization · Queueing · ISP reputation · Bounce/complaint handling · Retries · Idempotency · Optional open/click tracking · Multi-region · Per-ISP rate limits  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Correct arithmetic, split QPS types, explicit deal-breakers, at-least-once with caller/idempotency expectations  
> **Amazon lens:** Operational ownership, customer trust (transactional mail), marketplace/seller messaging, SES-like platform thinking, failure isolation across ISPs

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

Goal: **bound the email platform**—what we guarantee to sending teams (transactional SLOs vs marketing bulk), how we protect domain/IP reputation with ISPs, and how we scale intake → render → send → feedback without losing money-critical messages.

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
| F1 | Who sends? | Internal services (orders, auth, payments) + optional marketing/campaign tools + sellers | Multi-tenant intake; tenant quotas; authN/Z |
| F2 | Mail classes? | **Transactional** (OTP, order, receipt) + optional **marketing** / promotional | Separate queues, IPs, policies, SLOs |
| F3 | Content model? | Templates + variables; some raw MIME for advanced | Template service + render workers |
| F4 | Personalization? | Per-recipient merge fields; locale; currency | Render at send time; PII handling |
| F5 | Delivery semantics? | **At-least-once** attempt; no double-charge side effects on caller | Idempotency keys; status API |
| F6 | Tracking? | Optional opens/clicks for marketing; opt-out for transactional privacy | Tracking subdomain; pixel/link rewrite |
| F7 | Bounce/complaint? | Hard bounce suppress; soft retry; complaints → unsubscribe | Feedback loops; suppression list |
| F8 | Unsubscribes? | List-Unsubscribe; preference center for marketing | Compliance path; honor ASAP |
| F9 | Attachments? | Rare for transactional; size-capped | Object store refs, not inline forever |
| F10 | Observability? | Per-message status timeline; bounce codes; ISP metrics | Event store + portal |
| F11 | Domains/IPs? | Platform manages shared + dedicated IPs; DKIM/SPF/DMARC | Reputation & warm-up subsystem |
| F12 | Regions? | Global senders; data residency optional | Multi-region intake; regional send egress |

**MVP functional scope (lock with interviewer):**

1. Authenticated **Send API** (single + batch) with **idempotency key**.  
2. **Template CRUD** + versioning; render with merge data.  
3. Classify mail as **transactional** vs **marketing**; route separately.  
4. Durable enqueue → workers → SMTP/API to ISPs via MTA fleet.  
5. **Retries** with backoff for soft failures; terminal states for hard bounce.  
6. **Suppression list** (unsub, hard bounce, complaint).  
7. Bounce/complaint/FBL ingestion → update status + suppress.  
8. Basic status query + webhooks/events for senders.  
9. Per-tenant and **per-ISP** rate limits; IP warm-up.  
10. Optional open/click tracking for marketing only.

**Out of MVP (explicitly defer):**

- Full ESP marketing studio (drag-drop builder, A/B UI) — API/campaign ingest only  
- Guaranteed inbox placement (we optimize reputation; cannot promise)  
- SMS/push unification (can share preference store later)  
- End-user mailbox hosting (we are a *sending* platform)  
- Exactly-once “customer saw email” (opens are best-effort, privacy-noisy)

### 1.2 Non-Functional Requirements

| # | Question | Expected answer | Target |
|---|----------|-----------------|--------|
| N1 | Intake latency | Fast ACK after durable accept | p99 < 100–200ms in-region |
| N2 | Transactional freshness | OTP / order mail | p50 < 5–15s to ISP handoff; p99 < 60s healthy |
| N3 | Marketing throughput | Bulk campaigns | High aggregate; slower per-msg OK |
| N4 | Durability | No lost accepted sends | Quorum write before ACK |
| N5 | Availability | Intake highly available | 99.9%+; isolate ISP outages |
| N6 | Reputation | Protect shared domains/IPs | Per-ISP pacing; bounce rate alarms |
| N7 | Multi-region | Active-active intake | Home region for send state optional |
| N8 | Compliance | CAN-SPAM / GDPR / CASL paths | Unsub < 24h (aim minutes); audit |
| N9 | Security | No open relay; PII encryption | Auth, TLS, KMS, least privilege |
| N10 | Scale | Through 1,000× send class | See scale table |

### 1.3 Cases (Flows & Edge Cases)

**Happy paths**

1. Order service `Send(template=order_shipped, to=user, idem=orderId)` → durable → render → MTA → ISP 250 → `DELIVERED`.  
2. Soft bounce (mailbox full) → retry schedule → later success.  
3. Hard bounce (user_user) → `BOUNCED` + suppress address.  
4. Marketing campaign 10M recipients → chunked fanout → paced per ISP → tracking links.  
5. User clicks unsubscribe → suppress + webhook to tenant.  
6. Complaint via FBL → suppress + alert tenant reputation.  
7. Duplicate intake with same idempotency key → return original message_id.

**Edge / failure cases**

| Case | Behavior |
|------|----------|
| Caller retries after timeout | Same Idempotency-Key → one logical message |
| Worker crash after ISP 250 | May re-attempt; ISP/MTA should dedupe Message-ID; status may show retry |
| Template missing variable | Fail render → `FAILED_RENDER`; no send |
| Recipient on suppression | Short-circuit → `SUPPRESSED` (not counted as success) |
| ISP 421 rate limit | Backoff that ISP/IP; don’t burn reputation |
| IP new / cold | Warm-up caps; overflow queue or dedicated pool |
| Open tracking blocked by client | Opens undercounted; never trust for billing critical path |
| Attachment 25MB | Reject at intake (policy e.g. 10MB) |
| PII in logs | Redact; structured fields only |
| Domain DMARC fail | Reject or quarantine send config before go-live |
| Marketing during transactional surge | Separate capacity; never starve OTP queue |
| Region failover mid-send | At-least-once; status eventually consistent |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Sending tenants / apps | 200 | 2K | 20K | 200K |
| Active templates | 5K | 50K | 500K | 5M |
| Messages accepted / day | 50M | 500M | 5B | 50B |
| Peak **intake** QPS | ~2K | ~20K | ~200K | ~2M |
| Peak **send attempts**/s | ~3K | ~30K | ~400K | ~4M+ |
| % transactional | 40% | 40% | 35% | 30% |
| % marketing | 60% | 60% | 65% | 70% |
| Unique recipients / day | 20M | 150M | 1B | 5B+ |
| Bounce events / day | 0.5–2% | similar | similar | similar |
| Complaint rate target | ≪ 0.1% | ≪ 0.1% | ≪ 0.1% | ≪ 0.1% |
| Tracking events / day (optional) | 20M | 200M | 2B | 20B |
| Status/portal read QPS | ~500 | ~5K | ~50K | ~500K |

**What each jump forces:**

- **10×:** Durable outbox/queue; template cache; separate txn/marketing pools; basic per-ISP token buckets; suppression Redis+DB.  
- **100×:** Sharded message store; MTA fleets per class; IP pools + warm-up automation; FBL pipeline; tracking edge; cell-ish tenant isolation.  
- **1,000×:** Multi-region active-active intake; reputation controller as control plane; hierarchical pacing; cold storage for events; sampling; dedicated IPs at scale; ISP-specific connectors.

### 1.5 Etc. (Constraints & Assumptions)

- We hand off to **ISPs/MTAs**; “delivered” means accepted by receiving MTA, not “read by human.”  
- Transactional mail must **never** be stuck behind marketing.  
- Reputation is a **shared scarce resource**; abuse by one tenant can harm others → isolation.  
- Opens/clicks are **optional** and privacy-sensitive; default off for OTP/password mail.  
- Amazon-style ownership: on-call owns bounce spikes, IP blocks, and customer-impacting delays—not “just Kafka lag.”

**Scope statement:**

> Design a multi-tenant email delivery platform: authenticated intake with idempotency, templated personalization, class-separated durable queues, MTA send with per-ISP rate limits and IP reputation management, bounce/complaint/suppression handling, retries, optional tracking, and multi-region scale from ~2K intake QPS through 10× / 100× / 1,000× (~2M intake QPS), with transactional isolation from marketing bulk.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Split QPS classes

| Class | Baseline peak | 1,000× | Notes |
|-------|---------------|--------|-------|
| Intake accept | 2K | 2M | Durable write + auth |
| Render jobs | ~2K | ~2M | Can batch marketing |
| SMTP/API send attempts | ~3K | ~4M+ | Includes retries |
| Bounce/FBL ingest | ~50–100 | ~50K–100K | Spiky after campaigns |
| Tracking (open/click) | ~500 | ~500K+ | Edge-heavy |
| Status reads / webhooks out | ~500 | ~500K | Cache aggressively |
| Suppression checks | ~2K | ~2M | Hot path; cache |

**Critical:** Capacity on **send attempts** and **ISP-limited egress**, not only intake. Marketing retries during ISP throttling can amplify attempts 2–5× if uncapped.

### 2.2 Storage

```text
Message metadata ~400–800 B
Rendered body avg: transactional 5 KB; marketing 15 KB HTML
Keep rendered body short TTL (hours–days); store template+data or MIME in object store

Baseline 50M msgs/day × ~10 KB avg retained artifacts ≈ 500 GB/day raw-ish
With metadata-only hot + body in S3: metadata 50M × 600 B ≈ 30 GB/day
1,000×: 50B msgs/day × 600 B meta ≈ 30 TB/day metadata
Bodies: 50B × 10 KB = 500 TB/day if fully retained — **tier aggressively**

Unit check: 50e9 × 6e2 = 30e12 B = **30 TB/day** metadata (not PB)
Retain hot status 7–30 days; cold analytics 90–365 days; bodies 1–7 days typical
```

### 2.3 Bandwidth

```text
1,000× send 4M attempts/s × 10 KB ≈ 40 GB/s egress peak (pathological)
Realistic peak lower with pacing; still multi-Tbps class globally
→ regional MTA fleets; connection reuse; pipelining carefully per RFC/ISP norms
Tracking 500K events/s × 0.5 KB ≈ 250 MB/s — cheap vs send
```

### 2.4 Memory

```text
Template cache: hot 10K templates × 50 KB = 500 MB per render fleet region
Suppression Bloom/Cuckoo: 1B emails × ~10–20 bits ≈ 1.25–2.5 GB + DB truth
Per-ISP rate limiter state: thousands of keys × small → fits Redis cluster
In-flight leases: millions of message IDs at 1,000× → sharded
```

### 2.5 Reputation / bounce math

```text
Hard bounce rate > ~5–10% sustained → ISP blocks (order-of-magnitude; ISP-specific)
Complaint rate > ~0.1% → severe risk
At 100M sends/day, 0.1% complaints = 100K complaints/day → catastrophic
→ validate lists; double opt-in marketing; suppress aggressively
```

### 2.6 Critical bottlenecks

1. ISP rate limits / reputation blocks (external, hard)  
2. Intake durability under burst  
3. Render CPU for huge personalized campaigns  
4. Hot suppression key / tenant stampede  
5. Shared IP pool contamination by bad tenant  
6. Tracking redirect edge during mega campaigns  
7. Status store write amplification  

---

## 3. High-Level Design

### 3.1 Core abstractions

```text
Tenant (app credentials, quotas, IP pool assignment, compliance profile)
Template (template_id, version, channel=email, locales, from/reply policies)
SendRequest (idempotency_key, class, template|raw, recipients[], data, tags)
Message (message_id, recipient, class, status, next_attempt_at, provider_msg_id)
Suppression (address/domain, reason, tenant_scope|global, expires?)
IpPool / SendingIdentity (domain, dkim, ips[], warm_up_state)
IspLimit (isp, pool, tokens/sec, concurrency)
DeliveryEvent (bounce, complaint, open, click, delivery, reject)
```

### 3.2 Intake path: durable before ACK

```text
POST /v1/email/send
  Headers: Authorization, Idempotency-Key
  Body: class, template_id|html, to[], data, configuration_set

Flow:
  authenticate → authorize tenant → validate schema/size
  check idempotency store (tenant, key)
  if exists → return prior message_id(s)
  pre-check suppression (optional fast path)
  persist SendAccepted (message rows) → ACK 202
  async: enqueue class-specific queue
```

**Batch API:** `POST /v1/email/send-bulk` with chunking (e.g. 50–1000 recipients); each recipient gets `message_id`; batch has `batch_id`.

**Deal-breaker:** ACK 200 before durable persist (“we’ll send from memory”).

### 3.3 Templates & personalization

```text
Template versions immutable once published
Draft → Published(version=n)
Render: MJML/Handlebars/Liquid-like engine
Inputs: recipient profile + request data + locale
Outputs: subject, html, text, headers
PII: render in secure workers; scrub logs; encrypt data at rest
```

**Trade-off:** Render at intake vs at send.

| Approach | Pros | Cons |
|----------|------|------|
| Render at intake | Fail fast; simpler send | Huge storage; stale if delayed |
| Render at send (chosen) | Fresh data path; less storage | Late failure; need data retention until send |
| Hybrid | Cache rendered for retries | Complexity |

**Chosen:** Store **template_id + version + merge data ref**; render just-in-time; cache rendered MIME for retry window.

### 3.4 Queueing & class isolation

```text
                    ┌─ Q_txn_high (OTP, security) ──┐
Intake durable ─────┼─ Q_txn_normal (orders) ──────┼──→ Worker fleets → MTA
                    └─ Q_marketing (paced) ─────────┘
```

Priority: **security/OTP > transactional > marketing**.  
Marketing uses **token buckets** and scheduled send windows.  
**Deal-breaker:** single shared FIFO for OTP and newsletter blasts.

### 3.5 MTA / ISP send path

```text
Worker claims message (lease)
Load suppression → if hit, SUPPRESSED
Render → build MIME (Message-ID stable)
Select IpPool by tenant/class
Acquire ISP permit (rate limit)
Send via SMTP or ISP API
Map response → DELIVERED | RETRY | REJECTED
Emit events; update status
```

Stable **Message-ID** across retries aids ISP/MTA dedupe (not a hard guarantee).

### 3.6 Per-ISP rate limits

```text
Key: (isp_domain, ip_pool) or (isp, tenant, pool)
Algorithm: token bucket + max concurrency
On 421/450 defer: reduce tokens (AIMD), schedule retry
On success: slowly raise toward ceiling (warm-up aware)
```

ISPs (Gmail, Yahoo, Outlook, corporate) behave differently — config-driven connectors.

### 3.7 Retries & backoff

```text
Soft bounce / defer / timeout:
  delay = min(cap, base * 2^attempt) * (1 + jitter)
  # txn: base=10s, cap=1h, max_attempts=8–12
  # marketing: base=1m, cap=6h, max_attempts=5–8
Hard bounce / complaint / user unknown: terminal, suppress
Render failure: terminal (or quarantine for ops)
```

**Transactional OTP special case:** short TTL (e.g. 10–15 min); stop retrying after expiry; caller may re-issue new OTP via new idempotency key.

### 3.8 Idempotency

| Layer | Mechanism |
|-------|-----------|
| Intake | `(tenant_id, Idempotency-Key)` unique → same message_ids |
| Message row | `message_id` PK |
| MIME | Stable `Message-ID` header across attempts |
| Side effects | Status transitions monotonic where possible |
| Webhooks out | Signed events with `event_id`; receivers idempotent |

### 3.9 Bounce, complaint, suppression

```text
ISP DSN / FBL / Event API → Feedback Ingest
  parse type (hard/soft/complaint/delivery)
  update message status
  if hard|complaint → upsert suppression
  notify tenant webhook
  feed reputation controller (bounce%/complaint%)
```

**Suppression scopes:** global address (platform abuse), per-tenant, per-list.  
Marketing must check suppression; transactional may still send legal/security mail under policy (document carefully—password reset often allowed even if marketing-unsubscribed).

### 3.10 Optional tracking (opens/clicks)

```text
Marketing only by default:
  Rewrite links → https://t.{track}/c/{token}
  Inject 1x1 pixel → https://t.{track}/o/{token}
Edge records event → async pipeline → analytics
Token = HMAC(message_id, url, exp) to prevent forgery
```

**Privacy:** honor Do-Not-Track policies per region; transactional templates forbid tracking pixels in MVP policy.

### 3.11 Multi-region

| Path | Strategy |
|------|----------|
| Intake | Active-active regional API; idempotency home sticky by key hash or region header |
| Message state | Home region / cell by `message_id` or tenant |
| Send egress | Send from region close to ISP or identity; respect data residency |
| Suppression | Globally replicated cache; truth in multi-master or primary+CRDT carefully |
| Tracking | Anycast edge; write to nearest region; aggregate async |

**Deal-breaker:** split-brain double-send without idempotency home for the same key.

### 3.12 Storage / queue trade-offs

| Component | Choice | Deal-breaker |
|-----------|--------|--------------|
| Accept durability | DB/log before 202 | In-memory only ACK |
| Hot schedule | Delay queues / per-shard time index | Global `SELECT due` |
| Bodies | Object store | Unbounded OLTP BLOBs |
| Suppression | Bloom + DB | DB join every send uncached at 2M QPS |
| Secrets/DKIM | KMS/HSM | Private keys on disk in git |
| Events | Append log + TTL | Infinite OLTP growth |

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
┌──────────────┐   HTTPS    ┌─────────────────┐
│ Order/Auth/  │ ─────────► │ Intake API GW   │
│ Marketing/   │            │ Auth, quota,    │
│ Seller apps  │ ◄───────── │ idempotency     │
└──────────────┘   202      └────────┬────────┘
                                     │ durable write
                                     ▼
                            ┌─────────────────┐
                            │ Message Store   │
                            │ + Outbox/Events │
                            └────────┬────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              ▼                      ▼                      ▼
        Q_txn_high              Q_txn_normal            Q_marketing
              │                      │                      │
              ▼                      ▼                      ▼
        ┌──────────────────────────────────────────────────────┐
        │ Render + Send Workers (class-isolated fleets)        │
        │  suppression check │ render │ ISP rate limit │ MIME  │
        └────────────────────────────┬─────────────────────────┘
                                     ▼
                          ┌────────────────────┐
                          │ MTA / SMTP Proxies │
                          │ IpPools + DKIM     │
                          └─────────┬──────────┘
                                    ▼
                              ISPs / Mailboxes
                                    │
                    bounce/FBL/delivery events │
                                    ▼
                          ┌────────────────────┐
                          │ Feedback Ingest    │──► Suppression DB
                          └─────────┬──────────┘──► Reputation Ctrl
                                    ▼
                          Status API / Webhooks / Portal

Optional:
  Click/Open Edge (CDN) ──► Tracking pipeline ──► Analytics
```

### 4.2 Reputation & pacing control plane

```text
Metrics (bounce%, defer%, complaint%, throughput)
        │
        ▼
Reputation Controller
  - per tenant health score
  - per IP warm-up stage
  - per ISP token ceilings
        │
        ▼
Distributed Rate Limiters (Redis/etcd-ish)
        │
        ▼
Send Workers (enforce permits before SMTP)
```

### 4.3 Multi-region sketch

```text
        Clients
     ┌────┴────┐
     ▼         ▼
  API-US     API-EU     (active-active intake)
     │         │
     ▼         ▼
  Cell-US    Cell-EU    (message home by tenant/key)
     │         │
     ▼         ▼
  MTA-US     MTA-EU     (egress + identities)
     └────┬────┘
          ▼
   Global Suppression Repl (async, conflict policy)
```

---

## 5. Design Deep Dive

### 5.1 Reliability

#### 5.1.1 Failure modes & mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| Intake DB down | Cannot accept | Multi-AZ; regional failover; backpressure 503 |
| Queue lag | Delayed mail | Autoscale workers; shed marketing first |
| Render bug | Bad content | Canary templates; version pin; kill switch |
| MTA crash mid-send | Duplicate possible | Stable Message-ID; status at-least-once |
| ISP outage (Gmail) | Deferrals spike | Per-ISP isolation; other ISPs unaffected |
| Poison message | Worker loop | Max attempts → `FAILED`; quarantine |
| Suppression lag | Mail unsubbed user | Sync critical path cache; accept brief window with audit |
| Bad tenant list | IP reputation burn | Tenant isolation; automatic pause on bounce spike |
| Clock skew | Idempotency TTL issues | NTP; store absolute expiry |

#### 5.1.2 Consistency model

- Intake idempotency: **strong** per home for `(tenant, key)`.  
- Message status: **monotonic** state machine with occasional duplicate events.  
- Suppression: **read-your-writes** preferred on unsub path; eventual across regions (seconds).  
- Tracking analytics: **eventual**, lossy OK.

State machine (simplified):

```text
ACCEPTED → RENDERED → SENDING → DELIVERED
                 \       ↓
                  \→ DEFERRED → (retry) → …
                   \→ SUPPRESSED
                    \→ BOUNCED / COMPLAINED / FAILED / EXPIRED
```

#### 5.1.3 Exactly-once vs at-least-once

We promise:

1. Accepted requests are **durably recorded** and will be **attempted**.  
2. Duplicates may occur on crash windows.  
3. Callers use **Idempotency-Key** for intake.  
4. Downstream ISPs may also dedupe on Message-ID—**not relied on alone**.

We do **not** promise a human received/read the email.

#### 5.1.4 Amazon ownership themes

- **Customer Impact:** OTP delay is Sev-high; marketing delay is lower. Separate pages/alarms.  
- **Correctness:** Wrong suppression (blocking password reset) is as bad as spam. Policy matrix explicit.  
- **Operational excellence:** Runbooks for “Gmail 421 storm”, “DKIM break”, “complaint spike”.  
- **Frugality/efficiency:** Don’t store 500 TB/day bodies; tier.  
- **Dive deep:** Bounce code taxonomies, ISP-specific behavior, tenant scorecards.

### 5.2 Scalability

#### 5.2.1 Progressive scale changes

| Scale | Architecture moves |
|-------|--------------------|
| 1×–10× | Monolith OK for control; Redis suppression; 2–3 queues; shared IP with careful monitoring |
| 100× | Shard message store by `message_id`/tenant; MTA autoscaling; dedicated pools for large tenants; feedback Kafka; tracking edge |
| 1,000× | Cells by tenant; hierarchical rate limits; regional identity sets; sampled verbose logs; campaign scheduler separate from txn path |

#### 5.2.2 Sharding keys

| Data | Shard key | Notes |
|------|-----------|-------|
| Messages | `hash(message_id)` or tenant | Avoid hot campaign key without fanout |
| Idempotency | `hash(tenant, key)` | Sticky region |
| Suppression | `hash(normalized_email)` | Global lookup |
| ISP limits | `(isp, pool)` | Hot but few keys — use Redis cluster + local token cache |
| Campaign recipients | `campaign_id + chunk_id` | Pre-chunk at ingest |

**Hot key trap:** one `campaign_id` as Kafka partition key → single-partition meltdown. Fanout to many chunk partitions.

#### 5.2.3 Render at 1,000×

```text
Marketing: pre-resolve template once; stream recipients; parallel render workers
Personalization tokens only (name, order_id) — avoid giant per-user HTML unique blobs when possible
GPU not needed; CPU + cache templates in memory
```

#### 5.2.4 Multi-tenant fairness

- Per-tenant token buckets on intake and send.  
- Naughty tenant automatic **send pause** when bounce/complaint thresholds hit.  
- Dedicated IP option for whales; shared pool for long-tail with stricter caps.  
- Shuffle-shard workers so one tenant’s deferrals don’t HOL-block others.

### 5.3 Maintainability

#### 5.3.1 Configuration as data

ISP rules, warm-up curves, template policies, and class routing should be **config/service data**, not hard-coded if-else for each ISP in 50 places.

#### 5.3.2 Template lifecycle

```text
create draft → lint/preview → approve → publish immutable version
send pins version
rollback = publish older version as new version number (audit)
```

#### 5.3.3 Observability (must-have metrics)

| Metric | Why |
|--------|-----|
| Intake success / latency | Caller SLO |
| Time-to-ISP-accept by class | Customer experience |
| Deferral rate by ISP/IP | Reputation |
| Bounce % / complaint % by tenant | Abuse |
| Queue lag by class | Capacity |
| Suppression hit rate | List hygiene |
| Tracking QPS / error | Edge health |
| DKIM/SPF fail count | Auth breaks |

Tracing: `idempotency_key` → `batch_id` → `message_id` → `smtp_response`.

#### 5.3.4 Testing & game days

- Chaos: kill MTA after 250 OK → duplicate path.  
- Inject Gmail 421 → ensure Outlook unaffected.  
- Burst marketing 10× → OTP p99 stays in SLO.  
- Poison HTML → sandbox render.  
- Unsub → marketing suppressed within SLA; transactional policy verified.

#### 5.3.5 Security & compliance

- No open relay; authenticated intake only.  
- Link redirect open-redirect prevention (allowlist domains or signed tokens only).  
- Encrypt merge data; minimize retention.  
- Audit who published templates and who sent.  
- DMARC alignment for From domains.  
- Abuse detection: sudden 100× tenant volume, high URL malicious score in body.

---

## 6. Wrap-Up

### 6.1 What we’d build first (MVP slice)

1. Intake + idempotency + message store.  
2. Txn/marketing queues + workers.  
3. Template render + SMTP send on shared warmed IPs.  
4. Suppression + bounce ingest.  
5. Per-ISP basic rate limits.  
6. Status API.  
Then: FBL, warm-up controller, tracking edge, multi-region cells.

### 6.2 Explicit trade-offs to say aloud

| Decision | Trade-off |
|----------|-----------|
| At-least-once send | Simpler reliability; possible duplicates |
| Class-separated queues | More ops surface; protects OTP |
| JIT render | Fresher; late failures |
| Shared IP default | Cheaper; noisy-neighbor risk → need controls |
| Opens optional | Privacy + accuracy limits |
| Eventual suppression multi-region | Rare extra send vs strong global sync latency |

### 6.3 Risks & follow-ups

- ISP policy changes (sudden block) — need human+auto response.  
- Seller/marketplace abuse — trust & safety integration.  
- Data residency for EU PII in merge fields.  
- Large attachment product pressure.  
- Webhook delivery to callers (reuse webhook platform patterns).

### 6.4 60-second pitch

> Callers hit a regional intake API with an idempotency key; we durably accept and enqueue into **class-isolated** queues so marketing never starves OTP. Workers check suppression, render pinned template versions, take **per-ISP/IP permits**, and send via DKIM-signed MTA pools with warm-up. Soft failures retry with jittered backoff; hard bounces and complaints update a global suppression list and tenant reputation scores. Status is queryable and pushed via events. Tracking is optional for marketing. Multi-region active-active intake with home cells for send state scales through 10×/100×/1,000× while protecting shared reputation—the real scarce resource.

---

## 7. Deeper / Related Interview Questions

### 7.1 Product & scope

**Q: Transactional vs marketing—why separate?**  
A: Different SLOs, content policies, unsubscribe rules, IP reputation risk, and pacing. Mixing them is a classic outage pattern (newsletter burns IP → OTP fails).

**Q: Do we support raw MIME?**  
A: Yes for advanced tenants; still scan/size-limit; prefer templates for safety.

**Q: Scheduled send?**  
A: Store `send_at`; delay queue; still subject to ISP pacing at fire time.

**Q: A/B subject lines?**  
A: Campaign metadata picks variant sticky per recipient; analytics on opens if enabled.

### 7.2 Idempotency & duplicates

**Q: Caller timeout—did it send?**  
A: RePOST same Idempotency-Key; return same ids; status API for progress.

**Q: Worker sent twice?**  
A: Possible; stable Message-ID; design callers/recipients to tolerate duplicate informational mail; OTP should rotate codes server-side so duplicate email isn’t duplicate auth grant.

**Q: Idempotency TTL?**  
A: 24h–72h typical; store hash of body to detect same key different payload → 409 Conflict.

### 7.3 Templates & personalization

**Q: How to prevent template injection?**  
A: Autoescape HTML; sandbox; forbid raw HTML in user-provided fields unless reviewed.

**Q: Locale?**  
A: Template variants keyed by locale; fallback chain `fr-CA → fr → en`.

**Q: Huge product tables in receipt?**  
A: Cap lines; link to order page; size limits.

### 7.4 Queues & priority

**Q: How many priority levels?**  
A: Small set (3–4). Too many priorities → starvation complexity.

**Q: Fairness among transactional tenants?**  
A: Weighted fair queuing / per-tenant caps inside class.

**Q: Backpressure strategy?**  
A: 429/503 on intake for marketing first; transactional protected capacity reservation (e.g. 30% workers reserved).

### 7.5 ISP reputation

**Q: What is warm-up?**  
A: Gradually increase daily volume on new IPs; monitor defer/bounce; stage gates.

**Q: Shared vs dedicated IP?**  
A: Shared for long-tail; dedicated when volume/reputation isolation justifies cost.

**Q: How do you know ISP?**  
A: MX lookup / recipient domain classification cache; refresh periodically.

**Q: Gmail vs corporate Exchange differences?**  
A: Config: concurrency, idle timeouts, TLS requirements, error taxonomy mapping.

**Q: Deal-breaker for reputation?**  
A: Ignoring complaints/bounces; one global uncapped send loop.

### 7.6 Rate limits

**Q: Token bucket where?**  
A: Distributed limiter before SMTP; local allowance cache to cut Redis QPS; refill from controller ceilings.

**Q: Tenant limit vs ISP limit?**  
A: Must pass **both**. Effective rate = min(tenant, pool, isp, warm-up stage).

**Q: Thundering herd after outage?**  
A: Jittered retries; replay rate limits; circuit per ISP.

### 7.7 Bounce & complaint

**Q: Soft vs hard?**  
A: Hard → suppress permanent; soft → retry; classify via DSN codes + heuristics.

**Q: Complaint without List-Unsubscribe?**  
A: Still suppress; fix templates to include unsub for marketing.

**Q: False hard bounce?**  
A: Appeals/admin remove suppression with audit; prefer conservative suppress.

**Q: Feedback loop delay?**  
A: Hours possible; still process async; don’t block send path on FBL.

### 7.8 Tracking

**Q: Why opens are unreliable?**  
A: Image blocking, proxies prefetch, privacy features (Apple MPP)—treat as directional analytics only.

**Q: Click security?**  
A: Signed tokens; expiry; open-redirect prevention; malware URL scanning on rewrite.

**Q: Disable tracking per message?**  
A: Configuration set / template flag; default off for txn.

### 7.9 Multi-region & DR

**Q: Active-active send—double send risk?**  
A: Idempotency and message home cell; leases with fencing tokens.

**Q: Data residency?**  
A: EU merge data stays in EU cell; may still contact global ISPs—legal review.

**Q: Region outage?**  
A: Fail over intake DNS; in-flight home cell may delay; don’t blindly dual-send.

### 7.10 Data model & APIs

**Q: Status query pattern?**  
A: `GET /messages/{id}` + list by `idempotency_key` / `batch_id`; cursor pagination.

**Q: Webhooks to senders?**  
A: At-least-once signed events; reuse webhook delivery design patterns.

**Q: Search by recipient?**  
A: Secondary index carefully (PII); rate limit; privacy controls.

### 7.11 Abuse & marketplace

**Q: Seller spam?**  
A: Quotas, content scanning, recipient complaint attribution to seller, automatic suspension.

**Q: Phishing templates?**  
A: Brand impersonation detection; link domain allowlists; review workflow for new From domains.

**Q: Credential stuffing OTP flood?**  
A: Upstream auth rate limits; per-recipient OTP mail caps; anomaly detection.

### 7.12 Capacity & estimation traps

**Q: 50B msgs × 10KB = 500 PB/day?**  
A: **500 TB/day** if retained; hence short body TTL. 50e9×1e4 B = 5e14 B = 500 TB.

**Q: Plan capacity on intake only?**  
A: No—retries + ISP deferrals dominate worst days.

**Q: Global single MTA?**  
A: Won’t scale; also poor latency and blast radius.

### 7.13 Consistency edge cases

**Q: Unsub races with in-flight send?**  
A: Check suppression immediately before SMTP; accept rare race with audit; marketing SLA in minutes not ms.

**Q: Template unpublished while campaign running?**  
A: Pin version at accept time; immutable.

**Q: Recipient address normalization?**  
A: Lowercase + Gmail dot canonicalization policy explicit (careful—don’t over-normalize non-Gmail).

### 7.14 Interview traps

**Q: “Email is just SMTP in a loop.”**  
A: Reputation, suppression, class isolation, idempotency, multi-tenant abuse dominate real design.

**Q: “Exactly-once email.”**  
A: Push back; define accept vs handoff vs read.

**Q: “One queue to simplify.”**  
A: OTP buried behind marketing—customer trust failure at Amazon scale.

**Q: “Store forever for analytics.”**  
A: Cost explosion; sample + aggregate + short raw TTL.

**Q: “Tracking pixel on password reset.”**  
A: Privacy/security smell; forbid in policy.

### 7.15 Ownership scenarios (Amazon-style)

**Q: Page: Gmail deferrals 40%.**  
A: Check IP reputation, tenant bounce spikes, warm-up, DNS/DKIM, recent template URL changes; throttle marketing; protect txn pool; communicate.

**Q: Customer says never got order email.**  
A: Trace message_id → SMTP response → bounce?; check spam; suppression; provider outage window.

**Q: Complaint rate doubled overnight.**  
A: Find top tenants/campaigns; pause offenders; review list source; shared IP impact assessment.

### 7.16 Misc deep cuts

**Q: Build vs buy?** A: Still design internals; Amazon expects platform literacy.  
**Q: AIMD pacing?** A: Cut rate on defer (β); raise on success (α); clamp to warm-up; hysteresis.  
**Q: Template SSRF?** A: Pure sandbox—no network/files; timeout + memory cap.  
**Q: Attachments?** A: Size/type allowlist + async malware scan before send.  
**Q: SLOs?** A: OTP intake 99.95% / p99 handoff 30–60s; txn 99.9% / ≤120s; marketing lower, paced OK.

---

## 8. Appendices

### 8.1 Schema sketches

```text
tenants(tenant_id, name, status, quotas_json, ip_pool_id, created_at)
sending_identities(identity_id, domain, dkim_key_ref, dmarc_policy, status)
ip_pools(pool_id, class, warm_up_stage, daily_cap)
ips(ip, pool_id, reputation_score, state)
templates(template_id, tenant_id, name, current_version)
template_versions(template_id, version, subject, html, text, published_at, immutable)
idempotency(tenant_id, key, request_hash, response_ref, expires_at)
  PRIMARY KEY(tenant_id, key)
messages(message_id, tenant_id, batch_id, class, template_id, version,
         recipient_hash, recipient_enc, status, attempt, next_attempt_at,
         isp, pool_id, provider_msg_id, created_at, updated_at)
message_data(message_id, merge_data_ref, rendered_mime_ref, ttl)
suppressions(addr_norm, scope, tenant_id_nullable, reason, created_at, expires_at)
  PRIMARY KEY(addr_norm, scope, tenant_id)
delivery_events(event_id, message_id, type, code, raw_ref, at)
campaigns(campaign_id, tenant_id, schedule_at, status)  -- optional
tracking_tokens(token, message_id, target_url_hash, exp)
```

### 8.2 API sketches

```text
POST /v1/email/send
Idempotency-Key: ord_123_shipped
{
  "class": "transactional",
  "template_id": "order_shipped",
  "template_version": "12",   // optional pin
  "to": [{"email": "a@b.com", "data": {"name": "Ada", "order_id": "O1"}}],
  "from_identity": "noreply@marketplace.example",
  "tags": {"order_id": "O1"}
}

→ 202 {"message_ids": ["msg_..."], "status": "ACCEPTED"}

GET /v1/messages/msg_...
→ {"status": "DELIVERED", "events": [...], "attempts": 1}

POST /v1/email/send-bulk
→ {"batch_id": "bat_...", "accepted": 1000, "suppressed": 12}
```

### 8.3 State machine

```text
ACCEPTED
  → SUPPRESSED (pre-send)
  → FAILED_RENDER
  → SENDING
      → DELIVERED
      → DEFERRED (retryable)
      → REJECTED / BOUNCED / COMPLAINED / FAILED
      → EXPIRED (OTP TTL)
```

### 8.4 Normalization & suppression policy matrix

| Mail class | Marketing unsub | Hard bounce | Complaint |
|------------|-----------------|-------------|-----------|
| Marketing | Block | Block | Block |
| Order receipt | Allow (usually) | Block | Allow w/ review |
| OTP / security | Allow | Block | Allow |
| Legal notice | Allow | Block | Allow |

Document with counsel; engineers must not invent casually in interview without stating assumption.

### 8.5 ISP rate limit algorithm (sketch)

```text
function acquirePermit(isp, pool):
  stage = warmUp.ceiling(pool)
  limit = min(config.ispMax[isp], stage, pool.tenantCaps)
  tokens = redis.tokenBucket(key=isp+pool, rate=limit, burst=burst)
  if !tokens: return delayHint()
  return OK

onSmtpResponse(421/450):
  controller.multiplicativeDecrease(isp, pool)
  scheduleRetry(jitteredBackoff())

onSuccessWindow:
  controller.additiveIncrease(isp, pool)
```

### 8.6 Bounce classification cheat sheet

| DSN / signal | Class | Action |
|--------------|-------|--------|
| 5.1.1 user unknown | Hard | Suppress + BOUNCED |
| 5.2.2 mailbox full | Soft | Retry |
| 4.7.0 rate / reputation | Soft/defer | Slow ISP pacing |
| FBL complaint | Complaint | Suppress + alert |
| 5.7.1 policy reject | Terminal | FAILED; investigate content/auth |

### 8.7 Tracking token

```text
token = base64url( message_id | url_id | exp | HMAC )
GET /c/{token} → verify → 302 to url → emit click async
GET /o/{token} → 1x1 gif → emit open async
```

### 8.8 Warm-up stage example

| Day | Cap / IP / day | Notes |
|-----|----------------|-------|
| 1–3 | 200–500 | Monitor |
| 4–7 | 1K–5K | |
| 2nd week | 10K–50K | |
| Steady | Config max | Bounce% gates |

### 8.9 Glossary

| Term | Meaning |
|------|---------|
| MTA | Mail Transfer Agent (our sending agents) |
| ISP | Receiving mailbox providers |
| FBL | Feedback Loop (complaint notices) |
| DSN | Delivery Status Notification |
| DKIM/SPF/DMARC | Email authentication trio |
| Suppression | Do-not-send list |
| Warm-up | Gradual IP volume ramp |
| Configuration set | Tenant send policy bundle (tracking, IP pool, events) |
| Handoff | ISP 2xx/250 accept |

### 8.10 Progressive scale checklist

| Scale | Must have |
|-------|-----------|
| 1× | Durable intake, templates, basic SMTP, suppression, retries |
| 10× | Class queues, ISP buckets, bounce ingest, idempotency |
| 100× | IP pools/warm-up, sharded store, tracking edge, tenant autopause |
| 1000× | Cells, hierarchical pacing, multi-region homes, tiered storage |

### 8.11 Operator runbooks (titles)

1. Gmail deferral storm  
2. DKIM/DNS misconfiguration  
3. Complaint spike tenant isolation  
4. OTP latency SLO burn  
5. Suppression Redis outage (fail policy: fail-open txn vs fail-closed marketing—**decide explicitly**)  
6. Poison campaign pause  

### 8.12 Suppression outage policy (say aloud)

| Class | Redis down | Rationale |
|-------|------------|-----------|
| Marketing | Fail-closed (don’t send) | Legal/reputation |
| OTP | Fail-open with DB fallback sample | Customer login |
| Compromise | Local cache last-known + async reconcile | |

### 8.13 Worked scale example (100×)

```text
Intake peak ~200K msgs/s (spiky campaigns)
Assume 60% marketing paced to avg much lower; txn peak 40K/s
Send attempts with retries ~1.5× → plan ~300K attempts/s globally
Gmail 50% of recipients → Gmail path ~150K attempts/s needs heavy sharding & caps
Metadata 5B msgs/day × 600 B ≈ 3 TB/day
```

### 8.14 Worked scale example (1,000×)

```text
Intake peak ~2M/s → only feasible with massive horizontal cells + heavy batch marketing ingest
Real systems smooth marketing via pre-accepted campaign chunks hours ahead
Txn reserved capacity e.g. 100–200K/s global
Egress bandwidth dominant cost center
Status events: sample verbosely; aggregate ISP metrics in control plane
```

### 8.15 Interview “say this” summary

> Separate **transactional** from **marketing** at every layer—queues, IPs, SLOs, and suppression policy. Durably accept with idempotency, render pinned templates just-in-time, send under **per-ISP/IP rate limits** with warm-up, and treat reputation as the scarce resource. Bounces/complaints feed suppression and tenant health. Optional tracking stays off the transactional path. Scale with sharding and cells; prove you won’t let a newsletter take down password reset.

### 8.16 Pseudocode: send worker

```text
function sendWorkerLoop(class):
  msg = claimDue(class, lease=60s)
  if !msg: poll/backoff; continue
  if suppressed(msg.recipient, msg.class, msg.tenant):
     complete(msg, SUPPRESSED); continue
  if expired(msg): complete(msg, EXPIRED); continue
  mime = renderCacheOrBuild(msg)
  isp = classifyIsp(msg.recipient)
  permit = rateLimit.acquire(isp, msg.pool)
  if !permit: releaseClaim(msg, delay=permit.hint); continue
  resp = mta.send(mime, ip=selectIp(msg.pool))
  if resp.success:
     complete(msg, DELIVERED, provider_id=resp.id)
  else if resp.hardBounce:
     suppress(msg.recipient, HARD_BOUNCE)
     complete(msg, BOUNCED)
  else if resp.retryable:
     scheduleRetry(msg, backoff(msg.attempt, class))
  else:
     complete(msg, FAILED, reason=resp.code)
```

### 8.17 Pseudocode: intake idempotency

```text
function sendApi(tenant, key, body):
  h = hash(body)
  existing = idem.get(tenant, key)
  if existing:
    if existing.hash != h: return 409
    return 202 existing.response
  msgs = validateAndBuild(body)
  txn:
    insert messages ACCEPTED
    insert idem(tenant, key, h, response)
    outbox enqueue ids
  return 202 response
```

### 8.18 Event types for callers

```text
SendAccepted, RenderFailed, Deferred, Delivered,
Bounced, Complained, Suppressed, Expired, Opened?, Clicked?
```

### 8.19 Security checklist

- [ ] No open relay  
- [ ] TLS in/out  
- [ ] DKIM key in KMS  
- [ ] Template sandbox  
- [ ] Signed tracking tokens  
- [ ] PII redaction in logs  
- [ ] Tenant authZ on templates  
- [ ] Attachment malware scan  
- [ ] Link scanning for phishing  

### 8.20 Reliability test plan

1. Duplicate intake with same key → one message.  
2. Kill worker after 250 → at-most small duplicate; status sane.  
3. Marketing flood → OTP p99 intact.  
4. Hard bounce → suppressed on next send.  
5. Complaint → tenant score drops → autopause threshold.  
6. Tracking token tamper → 403.  
7. ISP 421 → rate decreases; other ISPs steady.  

### 8.21 Final trap table

| Trap | Pushback |
|------|----------|
| Single queue | Starves OTP |
| ACK before durable | Lost mail |
| No suppression | Reputation death |
| Global uncapped send | ISP blocks |
| Track OTP opens | Privacy |
| 50B×10KB=500PB/day | **500TB/day** if kept; don’t keep |
| Exactly-once read receipt | Impossible honestly |
| One IP forever at full blast | No warm-up |

**RFCs to name-drop:** SMTP 5321, message format 5322, DKIM/SPF/DMARC, List-Unsubscribe (8058), DSN 3464.

---

*End of email delivery system design.*
