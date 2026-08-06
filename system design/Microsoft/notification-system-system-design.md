# System Design: Notification System (with Edge Cases)

> **Focus areas:** Multi-channel (push/email/SMS/in-app) · Deduplication · Quiet hours · Preferences/consent · Fan-out · Provider routing · Templates · Priority isolation · Exactly-once illusion · Azure Notification Hubs / ESC narrative  
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)  
> **Quality bar:** Split transactional vs marketing planes, explicit deal-breakers, edge-case completeness  
> **Interview theme:** Microsoft — **Teams / Xbox / Outlook / Azure product notifications** platform

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

Goal: design a **notification platform** that accepts events from many producers, respects user preferences and legal consent, **deduplicates**, honors **quiet hours**, routes across **multi-channel** providers, and remains fair under marketing storms without delaying security/OTP-class messages.

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
| Job | Orchestrate notify across channels | Full ESP marketing studio UI |
| Critical edges | Dedupe, quiet hours, multi-channel merge | “Just call FCM” |
| Success | Right message, right channel, right time, once | Max send volume vanity |
| Microsoft lens | Graph/Teams-like prefs, Azure scale, compliance | Ignore timezone |

### 1.1 Functional Requirements

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
| F1 | Channels? | Push, email, SMS, in-app inbox, web push | Channel adapters |
| F2 | Producers? | Many internal services | Ingest API + authz |
| F3 | Classes? | Transactional / security / marketing | Isolated queues + SLOs |
| F4 | Templates? | Versioned, localized | Template service |
| F5 | Preferences? | Per-channel, per-category opt-in/out | Pref gate |
| F6 | Dedup? | Same logical alert shouldn’t spam | Dedupe keys + windows |
| F7 | Quiet hours? | User/local TZ; security may bypass | Scheduler + policy matrix |
| F8 | Multi-channel strategy? | Prefer push; fallback email; SMS costly | Orchestration policies |
| F9 | Digests? | Collapse marketing into daily digest | Aggregation jobs |
| F10 | Receipts? | Delivered/bounced/clicked (privacy-aware) | Feedback pipeline |
| F11 | Devices? | Multi-device push tokens | Token registry |
| F12 | Tenants? | M365 tenants / game titles | Multi-tenant isolation |

**MVP scope:**

1. `SendNotification` API with idempotency key + dedupe key.  
2. Preference + consent check.  
3. Quiet-hours evaluation with timezone.  
4. Channel selection policy (primary + fallback).  
5. Template render; provider send; retries; DLQ.  
6. In-app inbox write.  
7. Basic receipt webhooks; suppression for hard bounce/opt-out.  
8. Metrics per class/channel/tenant.

**Out of MVP:** perfect cross-device read sync like full Outlook; rich marketing journey builder; RCS; guaranteed SMS in all countries.

### 1.2 Non-Functional Requirements

| # | NFR | Target |
|---|-----|--------|
| N1 | Security/OTP latency | p99 < 10–30s end-to-end |
| N2 | Transactional | p99 < 60s |
| N3 | Marketing | minutes OK; fairness required |
| N4 | Durability | Accepted notify not lost |
| N5 | Dedupe correctness | No duplicate user-visible spam in window |
| N6 | Quiet hours | Honor unless bypass class |
| N7 | Availability | Ingest 99.9%+; provider isolation |
| N8 | Privacy | Minimize PII in logs; consent auditable |

### 1.3 Cases — especially edge cases

**Happy paths**

1. Password reset → security class → bypass quiet hours → SMS + email policy → send.  
2. Teams mention → push to active devices; in-app inbox; dedupe if burst mentions.  
3. Marketing campaign → preference filter → quiet hours defer → digest optional → paced send.  
4. Order shipped → transactional email + push; same `dedupe_key` retries collapse.  
5. User opts out of promos → future marketing blocked; security still flows.  
6. Push fails → fallback email within policy timeout.

**Edge / failure cases (interview meat)**

| Case | Behavior |
|------|----------|
| Producer retries | Idempotency key → one notification id |
| Burst duplicate events (same dedupe_key) | Collapse within dedupe window |
| Near-duplicate different ids | Optional similarity / category rate limits |
| Quiet hours local TZ | Defer to next open window; store scheduled |
| User flies across TZ | Use preference TZ or device-reported policy—document |
| Security during quiet hours | Bypass with audit |
| Multi-device push | Send to all valid tokens OR preferred device—product choice |
| Token invalid | Remove token; don’t retry forever |
| Partial multi-channel success | Record per-channel status; don’t double fallback spam |
| Fallback after success | Must not send email if push delivered (policy) |
| Provider 429 | Backoff; shift provider; protect reputation |
| Preference store timeout | Marketing fail-closed; security use cached last-known with care |
| Consent missing (EU marketing) | Block |
| SMS to landline | Provider error → mark channel failed |
| Unicode / RTL templates | Render tests; length SMS segments |
| Fan-out to 1M users | Chunked expansion; don’t inline |
| Digest + urgent | Urgent bypass digest |
| Click tracking privacy | Signed tokens; respect Apple MPP-like constraints |
| Tenant noisy neighbor | Fair queues |
| Clock skew | Server schedule time; TZ DB updates |
| User disables all channels | In-app only or drop per policy |
| Dedup window vs legal receipt | Keep send ledger even if collapsed |

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
| Users | 10M | 100M | 1B | multi-B |
| Notifications accepted / day | 50M | 500M | 5B | 50B |
| Peak ingest QPS | 2K | 20K | 200K | 2M |
| Peak send attempts / s | 3K | 30K | 300K | 3M |
| Push tokens | 20M | 200M | 2B | 20B |
| Templates | 500 | 2K | 10K | 50K |
| Tenants | 100 | 1K | 10K | 100K |
| Scheduled (quiet defer) backlog | 1M | 10M | 100M | 1B |
| Marketing campaign size | 1M | 10M | 100M | 1B |

**Jumps:**

- **10×:** Separate class queues; provider pools; pref cache.  
- **100×:** Tenant cells; sharded send ledger; scheduler partitions; digest workers.  
- **1,000×:** Hierarchical fan-out; edge preference caches; per-geo provider accounts; realtime suppression fabric.

### 1.5 Scope statement

> Design a multi-channel notification system with durable ingest, preference/consent gating, **deduplication**, **quiet hours**, smart fallback orchestration, provider routing, and progressive scale—without letting marketing starve security messages.

---

## 2. Back-of-the-Envelope Estimation

### 2.1 Plane split

```text
Security: tiny volume, tiny latency SLO, highest priority
Transactional: medium
Marketing: huge volume, elastic, must not steal capacity
Design queues and budgets per class — not one firehose.
```

### 2.2 Storage

```text
Send ledger ~500 B–1 KB / notification attempt
50M/day × 800 B ≈ 40 GB/day
1000× → ~40 TB/day → hot/warm/cold tiers

Push tokens ~200 B × 2B = 400 GB (+ indexes)
Prefs ~100–500 B / user
Dedupe keys: TTL’d KV high QPS
```

### 2.3 Quiet hours backlog math

```text
If 30% of marketing arrives in quiet hours and defers:
0.3 × campaign rate becomes scheduled set
Need time-partitioned scheduler (buckets by send_at minute)
```

### 2.4 Fan-out

```text
Campaign 100M users:
Expansion workers read audience segments in chunks of 1–10K
Each chunk → per-user personalize → enqueue
Avoid 100M-payload single message
```

### 2.5 Cost levers

SMS ≫ email ≫ push. Policy should prefer cheap channels; SMS for security/high intent only. Dedup + quiet hours + digests reduce cost and churn.

### 2.6 Bottlenecks

(1) Preference checks at volume (2) provider rate limits (3) scheduler hot partitions (4) template render CPU (5) token registry churn (6) feedback ingest spikes.

---

## 3. High-Level Design

### 3.1 Planes

| Plane | Responsibility |
|-------|----------------|
| Ingest | Auth, validate, idempotency, durable accept |
| Decision | Prefs, consent, dedupe, quiet hours, channel policy |
| Render | Templates, locale, safe HTML/text |
| Delivery | Provider adapters, retries, fallback |
| Feedback | Receipts, suppressions, engagement |
| Inbox | In-app notification center |
| Schedule | Deferred send_at execution |

**Deal-breaker:** sending marketing before consent/pref check.

### 3.2 Components

1. **Notification API / Gateway**  
2. **Idempotency + Dedupe Store**  
3. **Preference & Consent Service**  
4. **Policy Engine** (class, quiet hours, channel)  
5. **Scheduler / Deferral**  
6. **Template Service**  
7. **Render Workers**  
8. **Channel Queues** (priority + tenant fairness)  
9. **Provider Adapters** (FCM/APNs/WNS, email ESP, SMS gateway)  
10. **Send Ledger**  
11. **Token Registry**  
12. **Inbox Service**  
13. **Feedback Ingest**  
14. **Suppression Lists**  
15. **Observability / Audit**  

### 3.3 State machine (per notification)

```text
ACCEPTED → DECISION
  → DROPPED_PREF / DROPPED_SUPPRESSED / DROPPED_DEDUPE
  → SCHEDULED (quiet hours)
  → RENDERED → SENDING → SENT / PARTIAL
  → FALLBACK_PENDING → ...
  → FAILED / DLQ
Inbox write may occur at ACCEPTED or SENT depending on product
```

### 3.4 Deduplication design

```text
dedupe_key = producer-supplied or hash(user_id, category, subject_fingerprint)
Window = e.g. 5m for chat bursts, 24h for marketing creatives, 0 for OTP (unique)
Store: (user_id, dedupe_key) -> notification_id, expires_at
First wins; subsequent -> DROPPED_DEDUPE (or refresh count for badge)
Idempotency_key != dedupe_key
  idempotency: exactly one accept of same request
  dedupe: collapse semantically similar intents across producers
```

### 3.5 Quiet hours design

```text
User prefs: {tz, windows: [{start, end, days}], allow_security: true}
Decision:
  if class in BYPASS: send now
  else if now_in_tz within quiet: schedule at next_open(tz, windows)
  else send now
Scheduler: bucket by send_at minute; scanners pull due items
```

**Edge:** recurring campaigns + quiet hours → schedule per user, not one global time.

### 3.6 Multi-channel orchestration

```text
Policy examples:
  SECURITY_OTP: SMS primary, email secondary parallel or sequential
  SOCIAL_MENTION: push all devices + inbox; no SMS
  MARKETING: push if opted; else email; never SMS; digest eligible
  TRANSACTIONAL_SHIPPING: email + push; fallback email if push fails in 2m
```

Fallback rules must check **delivery receipts** to prevent double-channel spam.

### 3.7 Trade-offs

| Topic | Choice | Why |
|-------|--------|-----|
| At-least-once send | Yes | Durability |
| Effectively-once UX | Dedupe + ledger | Users hate spam |
| Sync vs async API | Async 202 | Producer decoupling |
| Push parallel devices | Usually yes | Reach |
| Marketing digests | Opt-in collapse | Fatigue |
| Pref cache | Yes with TTL + invalidate | Scale |
| Exact TZ | IANA TZ DB | Quiet hours correctness |

### 3.8 API sketch

```text
POST /v1/notifications
{
  "idempotency_key": "...",
  "dedupe_key": "mention:thread:123:user:9",
  "class": "TRANSACTIONAL",
  "category": "social.mention",
  "user_id": "...",
  "template_id": "...",
  "data": {...},
  "channel_policy": "DEFAULT",
  "bypass_quiet_hours": false
}

GET /v1/notifications/{id}
GET /v1/users/{id}/inbox
PUT /v1/users/{id}/preferences
```

---

## 4. Architecture Diagram

### 4.1 End-to-end

```text
Producers -> Notification API -> Durable Log/Queue
                    |
              Decision Workers
               | prefs | dedupe | quiet hours | policy
               v
        Schedule Store ----due----> Send Queues (by class/tenant)
               |
           Render Workers -> Send Ledger
               |
     +---------+----------+----------+
     v         v          v          v
   Push     Email       SMS       Inbox
   FCM/APNs/WNS  ESP    Gateway   DB
     |         |          |
   Feedback/webhooks -> Suppression + Receipts
```

### 4.2 Sequence: quiet hours defer

```text
Accept -> Decision: in quiet hours
Write SCHEDULED(send_at=07:00 local)
ACK 202 to producer
At 07:00 scanner enqueues -> render -> send
```

### 4.3 Sequence: push then email fallback

```text
Send push attempts to tokens
Start fallback timer T
If any push DELIVERED receipt -> cancel email fallback
If all fail or timeout T without deliver -> send email once (idempotent fallback key)
```

### 4.4 Sequence: dedupe collapse

```text
Event A accepted (dedupe_key=K)
Event B arrives with K within window
Mark B DROPPED_DEDUPE; optionally increment collapsed_count on A
Badge/inbox may update once
```

---

## 5. Design Deep Dive

### 5.1 Reliability invariants

1. Durable accept before producer ACK.  
2. Marketing never sends without consent/pref pass.  
3. Security class cannot be stuck behind marketing queues.  
4. Dedupe drops are auditable.  
5. Quiet hours deferrals eventually send or expire with policy.  
6. Fallback never doubles after success receipt.  
7. Provider credentials in Key Vault; rotated.  
8. Suppression honored on hot path.  
9. Tenant isolation for fairness and data.  
10. Template injection safe (no raw HTML from untrusted data).

### 5.2 Scalability

| Scale | Moves |
|-------|-------|
| 1× | One cluster; Redis dedupe; PG ledger; few workers |
| 10× | Class queues; pref cache; HPA; provider fan-out |
| 100× | Shard by user_id; tenant fair queues; scheduler partitions |
| 1000× | Geo cells; hierarchical campaigns; specialized suppression |

### 5.3 Maintainability

- Policy as data (not hardcoded if/else sprawl).  
- Provider adapter interface.  
- Template linting + screenshot tests.  
- Chaos: provider 429, pref outage, clock skew.  
- Canary templates per tenant.

### 5.4 Progressive scale

**1×:** Modular monolith notification service; Redis for idem/dedupe; send workers; FCM+SendGrid-class; prefs in SQL.

**10×:** Split decision/render/send; priority queues; metrics by class; token registry service; webhook feedback at scale.

**100×:** User-sharded send ledger; campaign expansion fleet; quiet-hours scheduler with minute buckets; digest pipeline; multi-provider email/SMS; cell per sovereign region.

**1000×:** Realtime preference edge cache with pubsub invalidation; per-geo IP warm pools; ML send-time optimization (careful with quiet hours interaction); automatic fatigue scoring; mega-campaign orchestration with checkpointed expansion.

### 5.5 Dedup deep dive

| Kind | Mechanism |
|------|-----------|
| Transport idempotency | idempotency_key |
| Semantic dedupe | dedupe_key + TTL window |
| Category rate limit | max N / category / hour |
| Digest collapse | bucket by day + category |
| Provider reconnect storms | token-level backoff |

**Deal-breaker:** using only provider-side dedupe—you still spam across channels.

### 5.6 Quiet hours deep dive

- Store IANA timezone (`America/Los_Angeles`), not UTC offset only (DST).  
- Windows as local times; compute next open with DST-safe library.  
- BYPASS classes: security, legal, fraud.  
- “Mute chat” vs quiet hours—layer policies.  
- Recurring reminders: compute per occurrence.  
- If user opens app during quiet hours, optional in-app still shows (channel-specific rules).

### 5.7 Multi-channel deep dive

**Reach vs annoyance vs cost.** Encode as scored policy:

```text
candidates = opted_channels ∩ capable_channels
order by (SLO fit, user preference rank, cost)
primary = top
fallback = next if primary fails AND policy.allows_fallback
parallel = only when product requires (rare; OTP email+SMS sometimes)
```

**Receipt truth:** push “sent to APNs” ≠ user saw it. Define fallback on **provider accept**, **delivery**, or **impression**—pick explicitly.

### 5.8 Preference consistency

- Fail-closed marketing on pref outage.  
- Security may use short-TTL cache.  
- Invalidation on pref write via pubsub.  
- Audit log for consent changes (who/when/source).

### 5.9 Provider routing

Health scores; sticky per notification; separate accounts for transactional vs marketing (reputation). **Deal-breaker:** blasting marketing from the OTP email domain/IP.

### 5.10 Deal-breaker gallery

| Temptation | Failure |
|------------|---------|
| One queue for all classes | OTP delayed by campaign |
| No dedupe | User spam / uninstall |
| UTC quiet hours for all | Wrong local nights |
| Fallback without receipt check | Double notify |
| Marketing on transactional domain | Deliverability collapse |
| Dual-write inbox + push without ledger | Inconsistent state |
| PII in plaintext logs | Compliance SEV |
| Infinite retries SMS | Cost blowout |

---

## 6. Wrap-Up

### 6.1 Designed

Multi-channel notification platform with durable ingest, preference/consent, dedupe windows, quiet-hours scheduling, channel fallback orchestration, provider isolation, and progressive fairness at scale.

### 6.2 Decisions to defend

1. Class-isolated queues  
2. idempotency_key + dedupe_key separation  
3. IANA TZ quiet hours  
4. Marketing fail-closed prefs  
5. Fallback gated by receipts  
6. Separate provider reputations  
7. Send ledger as truth  
8. Fair multi-tenant queues  

### 6.3 Risks

- TZ/DST bugs  
- Receipt ambiguity  
- Pref cache staleness  
- Provider outages  
- Campaign expansion lag  
- Fatigue / uninstall  

### 6.4 45-minute plan

| Min | Focus |
|-----|-------|
| 0–5 | Channels, classes, SLOs |
| 5–15 | Ingest, ledger, prefs |
| 15–25 | **Dedupe + quiet hours + multi-channel** |
| 25–35 | Providers, fallback, feedback |
| 35–45 | Scale jumps, deal-breakers |

### 6.5 Closer

> **Notifications:** durable, preference-aware, deduped, quiet-hours correct, multi-channel without double-send, class-isolated at scale—user trust over raw send volume.

---

## 7. Deeper / Related Interview Questions

### 7.1 Dedup

**Q: Who invents dedupe_key?**  
A: Producer best; platform can offer helpers; document collision semantics.

**Q: Can dedupe drop a still-needed update?**  
A: Use versioned dedupe or “last write wins with throttle” for state-sync alerts (battery 20%/15%/10%).

**Q: Cross-channel dedupe?**  
A: Yes—dedupe before channel split; channel attempts child of one notification id.

### 7.2 Quiet hours

**Q: Device TZ vs profile TZ?**  
A: Product policy; profile TZ more stable for email; device for push optional.

**Q: What if next open is 7 days later?**  
A: Cap deferral TTL; expire or drop marketing.

### 7.3 Multi-channel

**Q: Parallel vs sequential OTP?**  
A: Often parallel email+SMS for critical; cost vs UX tradeoff.

**Q: In-app vs push?**  
A: Inbox usually always write for durable history; push is interrupt.

### 7.4 Exactly-once

**Q: Can we promise once?**  
A: Effectively-once UX via keys; providers may still duplicate rarely—make handlers idempotent client-side when possible.

### 7.5 Templates

**Q: Injection?**  
A: Strict templating; escape; allowlist markdown subset.

**Q: Localization?**  
A: Template variants + ICU message format; fallback locale chain.

### 7.6 Microsoft framing

**Q: Azure Notification Hubs?**  
A: Can be push adapter; you still own prefs/dedupe/quiet hours/orchestration above it.

**Q: Teams notification similarity?**  
A: Mention aggregation, presence-aware delivery, multi-device—good narrative.

### 7.7 Interview traps

| Trap | Better |
|------|--------|
| “Kafka exactly once end-to-end” | Keys + ledger |
| “Sleep until morning in worker” | Durable scheduler |
| “Store quiet hours as UTC offsets” | IANA TZ |
| “Retry email forever” | Budget + DLQ |

### 7.8 Related systems

World-scale website (web push), search (alert digests), transaction microservice (payment receipts), presence service (smart delivery).

### 7.9 LLD pivot

Sketch classes: `PolicyEngine.decide`, `DedupeStore.check`, `QuietHours.next_open`, `FallbackOrchestrator`.

### 7.10 Fatigue

Rate limits per category; global daily interrupt budget; ML send-time optional later.

### 7.11 Suppression

Hard bounce, complaint, explicit unsubscribe, SMS STOP—propagate fast to hot path cache.

### 7.12 Observability

Track: accept → decide → schedule → send → deliver; drop reasons; fallback rates; quiet defer counts; cost per channel.

### 7.13 Security notify

Compromise-resistant: out-of-band channel; no sensitive secrets in push body; deep links signed.

### 7.14 Campaign checkpointing

Expansion workers persist cursor; crash-safe; exactly-once per user via (campaign_id, user_id) idempotency.

### 7.15 Incident vignette

**Symptom:** users report duplicate shipping emails.  
**Investigate:** producer double different idem keys; fallback+push both; dedupe window misconfig; provider retry.  
**Fix:** unify keys; receipt-gated fallback; ledger unique constraints.

---

## 8. Appendices

### 8.1 Schema sketches

```text
Notification(
  id, tenant_id, user_id, class, category,
  idempotency_key, dedupe_key, template_id,
  status, send_at, created_at, metadata
)

NotificationChannelAttempt(
  id, notification_id, channel, provider,
  status, provider_msg_id, attempts, last_error, updated_at
)

UserPreference(
  user_id, category, channel, opted_in, quiet_hours_json, tz, updated_at
)

DedupeRecord(
  user_id, dedupe_key, notification_id, expires_at, collapsed_count
)

DeviceToken(
  token_id, user_id, platform, token, last_seen, status
)

Suppression(
  tenant_id, address_or_token, reason, created_at
)

InboxItem(
  id, user_id, notification_id, title, body, read_at, created_at
)
```

### 8.2 Policy matrix (class × quiet × consent)

| Class | Consent | Quiet hours | Typical channels |
|-------|---------|-------------|------------------|
| SECURITY | Usually N/A | Bypass | SMS/email/push |
| TRANSACTIONAL | Soft | Honor (configurable) | email/push/inbox |
| MARKETING | Required | Honor | push/email/digest |
| LEGAL | Required/forced | Often bypass | email |

### 8.3 API checklist

- [ ] Idempotency-Key  
- [ ] dedupe_key optional but recommended  
- [ ] class required  
- [ ] 202 accepted  
- [ ] Pref CRUD  
- [ ] Inbox list/mark read  
- [ ] Admin resend (careful)  
- [ ] Audit consent  

### 8.4 Glossary

| Term | Meaning |
|------|---------|
| Dedupe window | TTL for semantic collapse |
| Quiet hours | User-local do-not-interrupt window |
| Fallback | Secondary channel after primary failure |
| Suppression | Hard block list |
| Digest | Bundled delayed marketing |
| Send ledger | Durable attempt history |
| Class isolation | Separate capacity for security vs marketing |

### 8.5 Progressive scale checklist

| Scale | Must |
|-------|------|
| 1× | Idem + prefs + basic channels |
| 10× | Class queues + dedupe + quiet schedule |
| 100× | Shards + fair tenants + digests |
| 1000× | Geo cells + fatigue + mega-campaign checkpoints |

### 8.6 Quiet hours pseudocode

```text
def decide_send_at(user, n, now_utc):
  if n.class in BYPASS_QUIET:
    return now_utc
  tz = ZoneInfo(user.tz)
  local = now_utc.astimezone(tz)
  if in_quiet(local, user.windows):
    return next_open(local, user.windows).astimezone(timezone.utc)
  return now_utc
```

### 8.7 Fallback pseudocode

```text
async def orchestrate(n, policy):
  primary = policy.primary
  att = await send(n, primary)
  if policy.fallback is None: return
  if att.status == PROVIDER_ACCEPTED and policy.fallback_on == 'FAILURE_ONLY':
    ok = await wait_delivery(att, policy.wait)
    if ok: return
  elif att.status == SUCCESS: return
  await send(n, policy.fallback, idem_suffix='fallback')
```

### 8.8 Dedupe pseudocode

```text
def accept_or_dedupe(user_id, dedupe_key, window, new_id):
  ok = dedupe.set_nx(user_id, dedupe_key, new_id, ttl=window)
  if ok: return CREATE
  dedupe.incr_collapsed(user_id, dedupe_key)
  return DROP
```

### 8.9 Provider adapter interface

```text
class ChannelAdapter:
  def send(self, rendered, attempt_id) -> ProviderResult
  def parse_webhook(self, headers, body) -> Receipt
```

### 8.10 Metrics dictionary

| Metric | Why |
|--------|-----|
| `notify_accept_qps` | Demand |
| `drop_pref_ratio` | Pref health |
| `drop_dedupe_ratio` | Spam collapse |
| `quiet_deferred_count` | Scheduler load |
| `send_p99_by_class` | SLO |
| `fallback_rate` | Policy tuning |
| `provider_error_rate` | Routing |
| `sms_cost_usd` | FinOps |
| `complaint_rate` | Deliverability |

### 8.11 Kill switches

- Pause marketing globally / per tenant  
- Disable SMS  
- Disable fallback  
- Force in-app only  
- Disable digests  
- Freeze template  

### 8.12 Chaos drills

1. Pref service timeout  
2. FCM outage  
3. Duplicate producer storm  
4. DST transition weekend  
5. Scheduler lag  
6. Webhook flood  
7. Bad template deploy  

### 8.13 SEV examples

| SEV | Example |
|-----|---------|
| SEV0 | Security OTP not sending globally |
| SEV1 | Quiet hours broken → night spam surge / legal risk |
| SEV2 | Duplicate sends elevated |
| SEV3 | Single tenant campaign slow |

### 8.14 Interview “say this” (60s)

> I’d separate security/transactional/marketing planes, durably accept with idempotency, then decide via preferences, **dedupe keys**, and **IANA quiet hours**. Multi-channel orchestration uses receipt-gated fallbacks, with isolated provider reputations. Scale with user shards and fair queues—never one firehose.

### 8.15 Cost worksheet

| Channel | Relative cost | Notes |
|---------|---------------|-------|
| In-app | Lowest | Storage |
| Push | Low | Token churn |
| Email | Medium | Deliverability eng |
| SMS | High | Use sparingly |

### 8.16 Oncall first five minutes

1. Which class broken?  
2. Provider status page?  
3. Drop reason spike (pref/dedupe)?  
4. Scheduler lag?  
5. Recent template/policy change?  
6. Tenant campaign runaway?  

### 8.17 Consent audit fields

`user_id, category, channel, action, source, ip/app, ts, text_version`

### 8.18 Inbox semantics

- Durable history separate from interrupt channels  
- Mark read sync  
- Retention limits  
- Deduped notifications still appear once  

### 8.19 Rate limit examples

| Limit | Value (example) |
|-------|-----------------|
| Marketing push / user / day | 5 |
| Social push / user / hour | 30 (then digest) |
| SMS security / user / hour | 5 |
| Tenant marketing QPS | Fair share |

### 8.20 Render safety

- Sandboxed HTML  
- Link allowlist / redirector  
- Size caps  
- SMS segment counting (GSM vs UCS-2)  

### 8.21 Scheduling partitions

```text
shard = hash(user_id) % N
bucket = floor(send_at / 60s)
PK = (shard, bucket, notification_id)
Scanner per shard due buckets
```

### 8.22 Cross-channel status model

```text
Notification.status = max/priority aggregate of attempts
UI shows per-channel details for support
```

### 8.23 Related edge-case pack

| Edge | Note |
|------|------|
| Shared device accounts | Rare; tokens map to user |
| Child accounts | Parental consent |
| Enterprise admin policies | Tenant overrides user marketing |
| Government SMS regulations | Country sender IDs |
| Email threading | Message-ID / References headers |
| Web push VAPID | Key rotation |
| APNs environment prod/sandbox | Misconfig common |
| Android collapse keys | Related to dedupe |
| Badge counts | Collapsed_count updates |
| User deletes app | Token invalid feedback |

### 8.24 Worked capacity narrative

At 300K send/s (100×), with 30% email, ESP connections and domain reputation become the constraint—not your Go workers. Interviewers want to hear provider pools and pacing.

### 8.25 Failure injection catalog

- Drop 50% APNs receipts  
- Pref DB failover  
- Render CPU starve  
- Duplicate webhooks  
- Wrong TZ data version  

### 8.26 Topic closer checklist

- [ ] Named dedupe vs idempotency  
- [ ] Quiet hours TZ story  
- [ ] Multi-channel fallback gated  
- [ ] Class isolation  
- [ ] Progressive scale  
- [ ] Deal-breakers  

### 8.27 One-breath closer

> Accept durably, decide with prefs/dedupe/quiet hours, send multi-channel without double-spam, isolate classes—trust first.

### 8.28 Supplemental Q&A

**Q: Should quiet hours apply to email?**  
A: Often yes for marketing; transactional shipping usually sends; document per category.

**Q: How do digests interact with dedupe?**  
A: Digest builder aggregates dropped-or-deferred items by category; one send keyed by (user, day, category).

**Q: What about presence-aware notify?**  
A: Optional: if user active in app, suppress push and only inbox—reduces annoyance.

**Q: CRM tools dual-sending?**  
A: Platform should be the only egress; producers don’t call ESP directly.

### 8.29 Comparison table: orchestration styles

| Style | Pros | Cons |
|-------|------|------|
| Primary+fallback | Simple | Slower reach |
| Parallel all channels | Fast | Spam/cost |
| User-preferred channel | UX | Reach variance |
| ML send-time | Optimize engagement | Complexity vs quiet hours |

### 8.30 Microsoft culture hooks

- Respect user attention (quiet hours, dedupe)  
- Security messages must be reliable  
- Enterprise admin controls for M365 tenants  
- Global TZ correctness as craftsmanship  

### 8.31 End-to-end example narrative

Teams burst mentions in a thread: producer emits events with `dedupe_key=thread:T:user:U:mention`. First creates inbox+push; next 20 collapse into badge +5. Quiet hours defer non-security. User opens app → inbox shows one item with collapsed count. No SMS. Marketing digest unaffected.

### 8.32 Final reminder

In Microsoft loops, **edge cases are the interview**—lead with dedupe, quiet hours, and multi-channel fallback correctness before drawing 20 boxes.

---

*End of document — Notification System*
