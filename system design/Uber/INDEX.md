# Uber System Design Interview Prep

> Uber interviews emphasize **practical, high-scale** problems: geospatial data, real-time streams, marketplaces, and money movement. A common process is ~40 minutes of architecture, then follow-ups on edge cases, requirements, trade-offs, and scaling.
>
> Be ready for: **geospatial indexing**, location freshness, WebSockets/streaming, event-time windows, idempotency, marketplace state transitions, and payment correctness.

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

Exact duplicates from bank A/B are consolidated to one canonical file. Distinct variants (e.g. calendar vs room-reservation) stay separate.

---

## A — Directly reported recent problems

| # | Problem | File |
|---|---------|------|
| 1 | Driver heat-map (ingest locations → analytics dashboard) | [driver-heat-map-system-design.md](./driver-heat-map-system-design.md) |
| 2 | Real-time Uber Eats restaurant metrics (order value + top-K over 1h/1d/1w) | [realtime-restaurant-metrics-system-design.md](./realtime-restaurant-metrics-system-design.md) |
| 3 | Globally distributed travel-query suggestion service | [travel-query-suggestion-system-design.md](./travel-query-suggestion-system-design.md) |
| 4 | Facebook Messenger-like chat | [messenger-chat-system-design.md](./messenger-chat-system-design.md) |
| 5 | Merchant-payment system | [merchant-payment-system-design.md](./merchant-payment-system-design.md) |
| 6 | Scoped delivery system | [scoped-delivery-system-design.md](./scoped-delivery-system-design.md) |
| 7 | Google Calendar | [google-calendar-system-design.md](./google-calendar-system-design.md) |
| 8 | Top-ten movies/series per hour (minute-level viewing events) | [topk-movies-dashboard-system-design.md](./topk-movies-dashboard-system-design.md) |
| 9 | Rider–driver matching | [rider-driver-matching-system-design.md](./rider-driver-matching-system-design.md) |
| 10 | Uber / entire ride-sharing marketplace | [ride-sharing-marketplace-system-design.md](./ride-sharing-marketplace-system-design.md) |
| 11 | Truck-tracking service | [truck-tracking-system-design.md](./truck-tracking-system-design.md) |
| 12 | Google Calendar / room-reservation system | [room-reservation-system-design.md](./room-reservation-system-design.md) |
| 13 | Uber Eats-style feed | [uber-eats-feed-system-design.md](./uber-eats-feed-system-design.md) |
| 14 | Restaurant recommendations for Uber Eats (ML system design) | [restaurant-recommendations-ml-system-design.md](./restaurant-recommendations-ml-system-design.md) |

---

## B — Broader bank (marketplace, mobility, streaming)

| Problem | File |
|---------|------|
| Driver location tracking | [driver-location-tracking-system-design.md](./driver-location-tracking-system-design.md) |
| Surge / trip-pricing service | [surge-trip-pricing-system-design.md](./surge-trip-pricing-system-design.md) |
| Trip lifecycle and state machine | [trip-lifecycle-state-machine-system-design.md](./trip-lifecycle-state-machine-system-design.md) |
| Driver / rider notification service | [driver-rider-notification-system-design.md](./driver-rider-notification-system-design.md) |
| Generic payments-product API | [payments-product-api-system-design.md](./payments-product-api-system-design.md) |
| Food-delivery marketplace | [food-delivery-marketplace-system-design.md](./food-delivery-marketplace-system-design.md) |
| Delivery dispatch | [delivery-dispatch-system-design.md](./delivery-dispatch-system-design.md) |
| Bus-stop or vehicle-position API | [bus-stop-vehicle-position-api-system-design.md](./bus-stop-vehicle-position-api-system-design.md) |
| Search by proximity | [proximity-search-system-design.md](./proximity-search-system-design.md) |
| Sliding-window top-K computation | [sliding-window-topk-system-design.md](./sliding-window-topk-system-design.md) |
| Real-time trending queries | [realtime-trending-queries-system-design.md](./realtime-trending-queries-system-design.md) |
| Trip and marketplace event pipeline | [trip-marketplace-event-pipeline-system-design.md](./trip-marketplace-event-pipeline-system-design.md) |
| TripAdvisor-like review / place platform | [tripadvisor-system-design.md](./tripadvisor-system-design.md) |
| Google Photos (frontend/mobile architecture emphasis) | [google-photos-system-design.md](./google-photos-system-design.md) |
| YouTube feed and its APIs | [youtube-feed-system-design.md](./youtube-feed-system-design.md) |
| Search engine | [search-engine-system-design.md](./search-engine-system-design.md) |

---

## LLD variants

| Problem | File |
|---------|------|
| Meeting-room scheduler (room sizes + booking history) | [meeting-room-scheduler-lld-system-design.md](./meeting-room-scheduler-lld-system-design.md) |
| Randomized set | [randomized-set-lld-system-design.md](./randomized-set-lld-system-design.md) |
| Room-reservation object model | [room-reservation-object-model-lld-system-design.md](./room-reservation-object-model-lld-system-design.md) |
| Extensible counter system | [extensible-counter-lld-system-design.md](./extensible-counter-lld-system-design.md) |
| Delivery / ride-hailing class model | [delivery-ride-hailing-class-model-lld-system-design.md](./delivery-ride-hailing-class-model-lld-system-design.md) |

---

**Prep priority (backend / distributed systems):** rider–driver matching → driver heat map → restaurant metrics → merchant payments → travel-query autocomplete → ride-sharing marketplace → trip lifecycle → surge pricing → notifications → proximity / geospatial.
