# Amazon System Design Interview Prep (SDE III / L6+)

> Amazon evaluates design for **practicality, reliability, efficiency, optimization, and scalability**. Loops may include HLD, LLD, or both. Dominant themes: commerce/logistics, failure handling, operational ownership, and explicit business trade-offs—not raw scale alone.

Style matches `../OpenAI/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

---

## A — Strongest recent / repeated

| # | Problem | File |
|---|---------|------|
| 1 | A/B experimentation platform | [ab-experimentation-platform-system-design.md](./ab-experimentation-platform-system-design.md) |
| 2 | Delivery locker capacity allocation | [delivery-locker-capacity-allocation-system-design.md](./delivery-locker-capacity-allocation-system-design.md) |
| 3 | Defend & harden a system you built | [defend-harden-existing-system-system-design.md](./defend-harden-existing-system-system-design.md) |
| 4 | Amazon Prime Video / homepage | [amazon-prime-video-system-design.md](./amazon-prime-video-system-design.md) |
| 5 | Rate limiter / expiry throttling | [rate-limiter-expiry-throttling-system-design.md](./rate-limiter-expiry-throttling-system-design.md) |
| 6 | Distributed cache | [distributed-cache-system-design.md](./distributed-cache-system-design.md) |
| 7 | Fake-review detection | [fake-review-detection-system-design.md](./fake-review-detection-system-design.md) |
| 8 | Pastebin | [pastebin-system-design.md](./pastebin-system-design.md) |
| 9 | Email delivery system | [email-delivery-system-system-design.md](./email-delivery-system-system-design.md) |
| 10 | Discounts & coupons (stacking) | [discounts-coupons-stacking-system-design.md](./discounts-coupons-stacking-system-design.md) |
| 11 | Online store | [online-store-system-design.md](./online-store-system-design.md) |
| 12 | Chess / multiplayer game | [multiplayer-chess-game-system-design.md](./multiplayer-chess-game-system-design.md) |

## A/B — Most frequently repeated (public bank)

| # | Problem | File |
|---|---------|------|
| 1 | Parking-payment system | [parking-payment-system-system-design.md](./parking-payment-system-system-design.md) |
| 2 | Amazon warehouse system | [amazon-warehouse-system-system-design.md](./amazon-warehouse-system-system-design.md) |
| 3 | TinyURL / URL shortener | [tinyurl-url-shortener-system-design.md](./tinyurl-url-shortener-system-design.md) |

## B — Commerce & logistics

| Problem | File |
|---------|------|
| Amazon.com at 10× traffic | [amazon-com-10x-traffic-system-design.md](./amazon-com-10x-traffic-system-design.md) |
| Customer / order / product database | [customer-order-product-database-system-design.md](./customer-order-product-database-system-design.md) |
| Ecommerce order-event ingestion API | [ecommerce-order-event-ingestion-api-system-design.md](./ecommerce-order-event-ingestion-api-system-design.md) |
| Bulk product ingestion (duplicates) | [bulk-product-ingestion-system-design.md](./bulk-product-ingestion-system-design.md) |
| Inventory management | [inventory-management-system-system-design.md](./inventory-management-system-system-design.md) |
| Shopping cart | [shopping-cart-system-design.md](./shopping-cart-system-design.md) |
| Pickup-locker software | [pickup-locker-software-system-design.md](./pickup-locker-software-system-design.md) |
| Optimally fill a truck | [optimally-fill-truck-system-design.md](./optimally-fill-truck-system-design.md) |
| Global food-delivery | [global-food-delivery-system-design.md](./global-food-delivery-system-design.md) |
| Delivery-route optimization | [delivery-route-optimization-system-design.md](./delivery-route-optimization-system-design.md) |
| Restaurant registration | [restaurant-registration-system-design.md](./restaurant-registration-system-design.md) |
| Pizza-shop software | [pizza-shop-system-design.md](./pizza-shop-system-design.md) |
| Robo-taxi marketplace | [robo-taxi-marketplace-system-design.md](./robo-taxi-marketplace-system-design.md) |
| Airport management | [airport-management-system-system-design.md](./airport-management-system-system-design.md) |
| Ticketing system | [ticketing-system-system-design.md](./ticketing-system-system-design.md) |
| Credit-card cashback promotion | [credit-card-cashback-promotion-system-design.md](./credit-card-cashback-promotion-system-design.md) |
| Expense tracker | [expense-tracker-system-design.md](./expense-tracker-system-design.md) |
| Phone-billing system | [phone-billing-system-system-design.md](./phone-billing-system-system-design.md) |
| Book-review aggregation | [book-review-aggregation-system-design.md](./book-review-aggregation-system-design.md) |

## B — Distributed systems & APIs

| Problem | File |
|---------|------|
| Job runner | [job-runner-system-design.md](./job-runner-system-design.md) |
| High-volume REST API gateway | [high-volume-rest-api-gateway-system-design.md](./high-volume-rest-api-gateway-system-design.md) |
| Generic scalable microservice | [generic-scalable-microservice-system-design.md](./generic-scalable-microservice-system-design.md) |
| Picture-upload service | [picture-upload-service-system-design.md](./picture-upload-service-system-design.md) |
| Dropbox-like file storage | [dropbox-like-file-storage-system-design.md](./dropbox-like-file-storage-system-design.md) |
| URL connectivity / link-graph | [url-connectivity-link-graph-system-design.md](./url-connectivity-link-graph-system-design.md) |
| Geo-distributed sensor ingestion | [geo-distributed-sensor-ingestion-system-design.md](./geo-distributed-sensor-ingestion-system-design.md) |
| Electronic voting | [electronic-voting-system-system-design.md](./electronic-voting-system-system-design.md) |
| Candidate interview scheduling | [candidate-interview-scheduling-system-design.md](./candidate-interview-scheduling-system-design.md) |

## B — Consumer products

| Problem | File |
|---------|------|
| Twitter / X | [twitter-x-system-design.md](./twitter-x-system-design.md) |
| Facebook / Instagram-style social | [social-network-facebook-instagram-system-design.md](./social-network-facebook-instagram-system-design.md) |
| Find-friends service | [find-friends-service-system-design.md](./find-friends-service-system-design.md) |
| News website | [news-website-system-design.md](./news-website-system-design.md) |
| Search autocomplete | [search-autocomplete-system-design.md](./search-autocomplete-system-design.md) |
| Real-time game leaderboard | [realtime-game-leaderboard-system-design.md](./realtime-game-leaderboard-system-design.md) |
| Alexa triggering / advertising workflow | [alexa-triggering-advertising-workflow-system-design.md](./alexa-triggering-advertising-workflow-system-design.md) |

## B — ML-specific

| Problem | File |
|---------|------|
| Product recommender | [product-recommender-system-design.md](./product-recommender-system-design.md) |
| Clothing recommender | [clothing-recommender-system-design.md](./clothing-recommender-system-design.md) |
| In-flight movie recommender | [in-flight-movie-recommender-system-design.md](./in-flight-movie-recommender-system-design.md) |
| Mobile autocomplete & spell-check | [mobile-autocomplete-spellcheck-system-design.md](./mobile-autocomplete-spellcheck-system-design.md) |

## Mostly LLD / OOD

| Problem | File |
|---------|------|
| Parking lot | [parking-lot-lld-system-design.md](./parking-lot-lld-system-design.md) |
| Elevator | [elevator-lld-system-design.md](./elevator-lld-system-design.md) |
| Deck of cards | [deck-of-cards-lld-system-design.md](./deck-of-cards-lld-system-design.md) |
| Classic games (Snake, Tic-Tac-Toe, Boggle, Poker rules) | [classic-games-ood-system-design.md](./classic-games-ood-system-design.md) |
| Online poker | [online-poker-system-design.md](./online-poker-system-design.md) |
| Coupon class hierarchy | [coupon-class-hierarchy-lld-system-design.md](./coupon-class-hierarchy-lld-system-design.md) |
| Pizza shop OOD | [pizza-shop-ood-system-design.md](./pizza-shop-ood-system-design.md) |
| Online store object model | [online-store-object-model-lld-system-design.md](./online-store-object-model-lld-system-design.md) |

---

**Note:** Overlaps from the public bank are consolidated to one canonical file each. Locker **capacity allocation** and **pickup-locker software** remain separate.
