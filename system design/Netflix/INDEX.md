# Netflix System Design Interview Prep

> Netflix does **not** use one company-wide standardized bank. Interviews are conversational and tied to the hiring team. L4 commonly gets one design interview; L5+ may get two 60-minute discussions, often heavily verbal.
>
> **2025–26 shift:** reports are dominated by **Ads, personalization, and homepage delivery**—not only “design Netflix streaming.”

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

Duplicate frequency-cap / ads-model variants are consolidated into canonical files; prepare **Ads data-modeling** separately from HLD when relevant.

---

## A — Highest-confidence prompts

| Evidence | Problem | File |
|----------|---------|------|
| A | Dynamic recommendation system after profile selection | [dynamic-recommendation-system-design.md](./dynamic-recommendation-system-design.md) |
| A | Event-logging platform: own client libraries vs docs-only | [event-logging-client-ownership-system-design.md](./event-logging-client-ownership-system-design.md) |
| A | Ad-frequency-capping system | [ad-frequency-capping-system-design.md](./ad-frequency-capping-system-design.md) |
| A | Advertisers / campaigns / budgets / targeting / caps / revenue model | [ads-platform-data-model-system-design.md](./ads-platform-data-model-system-design.md) |
| A | Netflix-like video-streaming service | [video-streaming-service-system-design.md](./video-streaming-service-system-design.md) |
| A | Content-delivery network (CDN) | [cdn-system-design.md](./cdn-system-design.md) |
| A | X / Twitter | [twitter-x-system-design.md](./twitter-x-system-design.md) |
| A | Payment system | [payment-system-system-design.md](./payment-system-system-design.md) |
| A | Service that validates and sorts television series | [tv-series-validate-sort-system-design.md](./tv-series-validate-sort-system-design.md) |

---

## Ads question bank (consolidated)

| Problem | File |
|---------|------|
| Real-time frequency capping (creative / line item / campaign / category) | [ad-frequency-capping-system-design.md](./ad-frequency-capping-system-design.md) |
| Rolling-window frequency caps | [rolling-window-frequency-caps-system-design.md](./rolling-window-frequency-caps-system-design.md) |
| Cross-device and cross-region frequency enforcement | [cross-device-frequency-enforcement-system-design.md](./cross-device-frequency-enforcement-system-design.md) |
| Ad frequency + presentation-order tracking | [ad-presentation-order-tracking-system-design.md](./ad-presentation-order-tracking-system-design.md) |
| Ad pacing (budget + flight dates) | [ad-pacing-system-design.md](./ad-pacing-system-design.md) |
| Advertiser / campaign intake schema | [ads-campaign-intake-system-design.md](./ads-campaign-intake-system-design.md) |
| Audience-segment construction + low-latency membership | [audience-segment-membership-system-design.md](./audience-segment-membership-system-design.md) |
| Publisher-specific configuration rules | [publisher-ads-config-rules-system-design.md](./publisher-ads-config-rules-system-design.md) |
| Ads-demand reporting + ETL / warehouse | [ads-demand-reporting-etl-system-design.md](./ads-demand-reporting-etl-system-design.md) |
| Global config rollout + click aggregation | [ads-config-rollout-click-aggregation-system-design.md](./ads-config-rollout-click-aggregation-system-design.md) |

---

## Product, storage, and platform prompts

| Problem | File |
|---------|------|
| Above-the-fold homepage rendering with title deduplication | [homepage-deduplication-system-design.md](./homepage-deduplication-system-design.md) |
| Viewport-based pagination + cross-module deduplication | [viewport-pagination-dedup-system-design.md](./viewport-pagination-dedup-system-design.md) |
| Scalable file-backup system (filesystem primitives) | [file-backup-system-design.md](./file-backup-system-design.md) |
| Crash-resilient filesystem | [crash-resilient-filesystem-system-design.md](./crash-resilient-filesystem-system-design.md) |
| ML-training and batch-inference scheduler | [ml-training-batch-inference-scheduler-system-design.md](./ml-training-batch-inference-scheduler-system-design.md) |
| Video-playlist component (build + optimize) | [video-playlist-component-system-design.md](./video-playlist-component-system-design.md) |

---

**Prep priority:** dynamic recommendations → ad frequency capping → ad pacing → ads data model → homepage / viewport dedup → video streaming → CDN → event-logging ownership → payments → TV-series validate/sort.
