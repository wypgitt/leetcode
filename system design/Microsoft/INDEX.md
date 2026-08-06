# Microsoft System Design Interview Prep

> Microsoft interviews are **unusually team-specific**. A candidate may design twice—informally in a technical screen and formally in the loop—and “design” may mean **distributed architecture (HLD)** or **working object-oriented code (LLD)**. Prompts often reflect **Azure, Microsoft 365, Copilot, gaming**, or the hiring team’s domain. Themes: security/compliance, regional Azure reliability, clean APIs, and willingness to switch between HLD and coded LLD.

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

Sources informing this bank: Exponent 2026 Microsoft guide, Hello Interview Microsoft dataset, Glassdoor / forum reports, IGotAnOffer lists, L61–L64 candidate reports.

---

## A — Strongest recent / verified (Infrastructure)

| # | Problem | File |
|---|---------|------|
| 1 | OTA firmware / software update for millions of vehicles or devices | [ota-firmware-update-system-design.md](./ota-firmware-update-system-design.md) |
| 2 | File system (files, directories, symlinks, traversal; sometimes code) | [distributed-file-system-system-design.md](./distributed-file-system-system-design.md) |
| 3 | Ordered distributed message log | [ordered-distributed-message-log-system-design.md](./ordered-distributed-message-log-system-design.md) |
| 4 | Leader–follower election | [leader-follower-election-system-design.md](./leader-follower-election-system-design.md) |
| 5 | Distributed key-value store | [distributed-key-value-store-system-design.md](./distributed-key-value-store-system-design.md) |
| 6 | Rate limiter | [rate-limiter-system-design.md](./rate-limiter-system-design.md) |
| 7 | Distributed cache | [distributed-cache-system-design.md](./distributed-cache-system-design.md) |
| 8 | Logging system | [logging-system-system-design.md](./logging-system-system-design.md) |
| 9 | Presence-service API | [presence-service-api-system-design.md](./presence-service-api-system-design.md) |
| 10 | Chat / messaging system | [chat-messaging-system-design.md](./chat-messaging-system-design.md) |

## A — Microsoft / Azure-specific

| # | Problem | File |
|---|---------|------|
| 1 | Azure Key Vault–like secrets, certificates, and encryption keys | [azure-key-vault-system-design.md](./azure-key-vault-system-design.md) |
| 2 | Chat for Azure / Microsoft 365 users | [azure-chat-system-design.md](./azure-chat-system-design.md) |
| 3 | High-volume regional AI / Copilot prompts | [regional-ai-copilot-prompts-system-design.md](./regional-ai-copilot-prompts-system-design.md) |
| 4 | Migrate Azure services from a failing / overloaded region (+ DR) | [azure-regional-failover-migration-system-design.md](./azure-regional-failover-migration-system-design.md) |
| 5 | Health application in the Microsoft ecosystem | [microsoft-health-application-system-design.md](./microsoft-health-application-system-design.md) |

## B — Broader public bank

| Problem | File |
|---------|------|
| Visual Studio–like IDE | [visual-studio-ide-system-design.md](./visual-studio-ide-system-design.md) |
| Instagram | [instagram-system-design.md](./instagram-system-design.md) |
| Uber / ride-hailing | [uber-ride-hailing-system-design.md](./uber-ride-hailing-system-design.md) |
| OpenTable / restaurant reservations | [opentable-restaurant-reservations-system-design.md](./opentable-restaurant-reservations-system-design.md) |
| Dropbox or iCloud | [dropbox-icloud-system-design.md](./dropbox-icloud-system-design.md) |
| Amazon-style shopping cart | [shopping-cart-system-design.md](./shopping-cart-system-design.md) |
| iOS photo gallery | [ios-photo-gallery-system-design.md](./ios-photo-gallery-system-design.md) |
| Running / fitness application API | [running-fitness-api-system-design.md](./running-fitness-api-system-design.md) |
| Tic-tac-toe API | [tic-tac-toe-api-system-design.md](./tic-tac-toe-api-system-design.md) |
| Uber Eats at scale | [uber-eats-system-design.md](./uber-eats-system-design.md) |
| Library system (online + offline customers) | [library-online-offline-system-design.md](./library-online-offline-system-design.md) |
| Generic social-media platform | [generic-social-media-system-design.md](./generic-social-media-system-design.md) |
| Microsoft Teams feature for university students in Japan | [teams-university-japan-system-design.md](./teams-university-japan-system-design.md) |
| High-volume real-time transaction microservice | [realtime-transaction-microservice-system-design.md](./realtime-transaction-microservice-system-design.md) |
| World-scale website | [world-scale-website-system-design.md](./world-scale-website-system-design.md) |
| Notification system (edge cases) | [notification-system-system-design.md](./notification-system-system-design.md) |
| Search engine | [search-engine-system-design.md](./search-engine-system-design.md) |
| Online marketplace / product portal | [online-marketplace-system-design.md](./online-marketplace-system-design.md) |
| Fitness wearable (heart rate) | [fitness-wearable-heart-rate-system-design.md](./fitness-wearable-heart-rate-system-design.md) |
| File-sharing / cloud-storage service | [file-sharing-cloud-storage-system-design.md](./file-sharing-cloud-storage-system-design.md) |
| Message queue | [message-queue-system-design.md](./message-queue-system-design.md) |
| Device / software-update orchestration | [device-update-orchestration-system-design.md](./device-update-orchestration-system-design.md) |
| Regional failover and disaster recovery | See [azure-regional-failover-migration-system-design.md](./azure-regional-failover-migration-system-design.md) |

## Recent HLD / LLD combinations

| Problem | File |
|---------|------|
| Ride-sharing class + database design (LLD) | [ride-sharing-class-db-lld-system-design.md](./ride-sharing-class-db-lld-system-design.md) |
| Khan Academy / Byju’s–style content platform (paid + free) | [khan-academy-content-platform-system-design.md](./khan-academy-content-platform-system-design.md) |

## Low-level variants to prepare

| Problem | File |
|---------|------|
| LRU cache implementation | [lru-cache-lld-system-design.md](./lru-cache-lld-system-design.md) |
| Fixed-size buffer | [fixed-size-buffer-lld-system-design.md](./fixed-size-buffer-lld-system-design.md) |
| File-system classes | [file-system-classes-lld-system-design.md](./file-system-classes-lld-system-design.md) |
| IDE / editor class model | [ide-editor-class-model-lld-system-design.md](./ide-editor-class-model-lld-system-design.md) |
| Shopping-cart or library object model | [shopping-cart-library-object-model-lld-system-design.md](./shopping-cart-library-object-model-lld-system-design.md) |

---

**Notes**

- Overlaps consolidated where one design covers both prompts (e.g. regional failover ↔ Azure region migration).
- Device-update **orchestration** is campaign/fleet control-plane focused; OTA covers end-device delivery for vehicles/IoT.
- Azure chat emphasizes Entra ID, compliance, and M365 tenancy; generic chat covers messaging primitives.
- Prefer team-domain framing in interviews: security, compliance, multi-tenant Azure cells, and API clarity.
