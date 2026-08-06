# Stripe System Design Interview Prep

> Stripe has the **most stable signature bank** among these companies. The design round emphasizes **API correctness, data models, idempotency, regional failure, rollout, and operations**—not only drawing a scalable box diagram.
>
> Mid-level+: dedicated round **45–60 minutes**. Senior candidates may get an additional architecture or API-design round.
>
> **Do not confuse** with Stripe’s separate **integration round** (JSON transform, call documented API, combine local + external data)—those are implementation exercises, not HLD.

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

---

## A — Core verified bank

| Evidence | Problem | File |
|----------|---------|------|
| A | Ledger / bookkeeping service | [ledger-bookkeeping-system-design.md](./ledger-bookkeeping-system-design.md) |
| A | APIs for transactions + transaction log | [transaction-apis-log-system-design.md](./transaction-apis-log-system-design.md) |
| A | Redesign Stripe’s internal authorization system | [internal-authorization-system-design.md](./internal-authorization-system-design.md) |
| A | Rate limiter | [rate-limiter-system-design.md](./rate-limiter-system-design.md) |
| A | Metrics service | [metrics-service-system-design.md](./metrics-service-system-design.md) |
| A | Distributed LRU cache | [distributed-lru-cache-system-design.md](./distributed-lru-cache-system-design.md) |
| A | Application-performance-monitoring (APM) | [apm-system-design.md](./apm-system-design.md) |
| A | Production data-platform sharding problem | [data-platform-sharding-system-design.md](./data-platform-sharding-system-design.md) |

---

## Additional current reported prompts

| Problem | File |
|---------|------|
| End-to-end payment-processing system | [payment-processing-system-design.md](./payment-processing-system-design.md) |
| Webhook-delivery service | [webhook-delivery-system-design.md](./webhook-delivery-system-design.md) |
| Access-management system | [access-management-system-design.md](./access-management-system-design.md) |
| Feature-flag service | [feature-flag-system-design.md](./feature-flag-system-design.md) |
| Merchant-lending platform | [merchant-lending-system-design.md](./merchant-lending-system-design.md) |
| Merchant-ledger service | [merchant-ledger-system-design.md](./merchant-ledger-system-design.md) |
| Strongly consistent scalable ledger + unreliable third-party routing API | [ledger-third-party-routing-system-design.md](./ledger-third-party-routing-system-design.md) |
| Distributed metrics counter | [distributed-metrics-counter-system-design.md](./distributed-metrics-counter-system-design.md) |
| Near-real-time local activity-counting service | [local-activity-counting-system-design.md](./local-activity-counting-system-design.md) |
| Superhero / incident-dispatch marketplace | [incident-dispatch-marketplace-system-design.md](./incident-dispatch-marketplace-system-design.md) |
| Recurring-payment scheduling | [recurring-payment-scheduling-system-design.md](./recurring-payment-scheduling-system-design.md) |
| Retry-safe, idempotent payment processing | [idempotent-payment-processing-system-design.md](./idempotent-payment-processing-system-design.md) |
| Reliable scheduling for asynchronous financial workflows | [async-financial-workflow-scheduling-system-design.md](./async-financial-workflow-scheduling-system-design.md) |
| Instagram-like fallback | [instagram-fallback-system-design.md](./instagram-fallback-system-design.md) |
| Ticketmaster-like fallback | [ticketmaster-fallback-system-design.md](./ticketmaster-fallback-system-design.md) |

---

**Prep priority:** ledger/bookkeeping → transaction APIs → webhook delivery → idempotent payment processing → recurring payments → internal authorization → rate limiter → metrics/APM → sharding → feature flags → merchant lending.

---

## HLD vs integration round (read first)

| Round | What Stripe is testing | What to practice |
|-------|------------------------|------------------|
| **System design (these docs)** | API correctness, data models, idempotency, regional failure, rollout, ops | Clarify → estimate → HLD → deep dive → traps |
| **Integration coding** | Read docs, transform JSON, call APIs, combine local + remote | Not covered here—separate prep |

Do not spend a design interview writing Elements/checkout client boilerplate.

---

## File inventory

All filenames below are unique and present under `./` (core A bank + additional reported prompts). Prefer **Prep priority** order above when time-boxed.

