# Apple System Design Interview Prep

> Apple’s bank is **least standardized**. Maps, Siri, iCloud, SRE, and Apple Intelligence teams ask substantially different questions. Rounds are typically **45–60 minutes**. Interviewers emphasize **privacy, authentication, APIs, storage, offline behavior, and on-device/server boundaries**.

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**.

Bank C items are **realistic practice drills** (device/privacy-oriented)—not claimed as confirmed dated interview reports—but they exercise the constraints Apple interviewers reportedly emphasize.

---

## A — Directly reported / interviewer-verified

| # | Problem | File |
|---|---------|------|
| 1 | Peer-to-peer distributed web crawler | [p2p-distributed-web-crawler-system-design.md](./p2p-distributed-web-crawler-system-design.md) |
| 2 | Distributed job scheduler | [distributed-job-scheduler-system-design.md](./distributed-job-scheduler-system-design.md) |
| 3 | Rate limiter | [rate-limiter-system-design.md](./rate-limiter-system-design.md) |
| 4 | Safe restart mechanism for N servers | [safe-server-restart-system-design.md](./safe-server-restart-system-design.md) |
| 5 | CI/CD system | [cicd-system-system-design.md](./cicd-system-system-design.md) |
| 6 | Legacy storage → new storage migration | [storage-system-migration-system-design.md](./storage-system-migration-system-design.md) |
| 7 | Old auth → new auth migration | [authentication-migration-system-design.md](./authentication-migration-system-design.md) |
| 8 | Globally replicated block storage (US/EU, strong consistency) | [global-block-storage-system-design.md](./global-block-storage-system-design.md) |
| 9 | Search typeahead (client/server, privacy of query logs) | [search-typeahead-system-design.md](./search-typeahead-system-design.md) |
| 10 | Applicant-tracking system | [applicant-tracking-system-system-design.md](./applicant-tracking-system-system-design.md) |
| 11 | Canvas application (shapes, layers, undo/redo, collaboration) | [canvas-application-system-design.md](./canvas-application-system-design.md) |
| 12 | Deep-dive / redesign a system you built | [defend-redesign-own-system-system-design.md](./defend-redesign-own-system-system-design.md) |

---

## B — Broader reported bank

| Problem | File |
|---------|------|
| Smart elevator (destination grouping, accessibility, energy) | [smart-elevator-system-design.md](./smart-elevator-system-design.md) |
| Netflix / video streaming | [video-streaming-system-design.md](./video-streaming-system-design.md) |
| Blackjack gaming site | [blackjack-gaming-system-design.md](./blackjack-gaming-system-design.md) |
| Scalable photo-sharing service | [photo-sharing-system-design.md](./photo-sharing-system-design.md) |
| Vehicle-manufacturer data aggregation (unified client API) | [vehicle-data-aggregation-system-design.md](./vehicle-data-aggregation-system-design.md) |
| MapReduce-style aggregation | [mapreduce-aggregation-system-design.md](./mapreduce-aggregation-system-design.md) |
| Cloud file storage and synchronization | [cloud-file-sync-system-design.md](./cloud-file-sync-system-design.md) |
| Distributed cache | [distributed-cache-system-design.md](./distributed-cache-system-design.md) |
| URL shortener | [url-shortener-system-design.md](./url-shortener-system-design.md) |
| Geospatial shortest-route / proximity service | [geospatial-routing-proximity-system-design.md](./geospatial-routing-proximity-system-design.md) |
| Private analytics / telemetry | [private-analytics-telemetry-system-design.md](./private-analytics-telemetry-system-design.md) |

---

## C — Apple-domain practice drills (privacy / sync / on-device)

| Problem | File |
|---------|------|
| iCloud Photo Library synchronization | [icloud-photo-library-sync-system-design.md](./icloud-photo-library-sync-system-design.md) |
| iMessage multi-device delivery | [imessage-multidevice-delivery-system-design.md](./imessage-multidevice-delivery-system-design.md) |
| Notes synchronization and conflict resolution | [notes-sync-conflict-resolution-system-design.md](./notes-sync-conflict-resolution-system-design.md) |
| Secure iCloud Keychain synchronization | [icloud-keychain-sync-system-design.md](./icloud-keychain-sync-system-design.md) |
| Local-first document synchronization | [local-first-document-sync-system-design.md](./local-first-document-sync-system-design.md) |
| Health-data sync (Watch ↔ iPhone) | [health-data-watch-iphone-sync-system-design.md](./health-data-watch-iphone-sync-system-design.md) |
| Battery-conscious background upload scheduler | [battery-conscious-upload-scheduler-system-design.md](./battery-conscious-upload-scheduler-system-design.md) |
| Privacy-preserving analytics aggregation | [privacy-preserving-analytics-system-design.md](./privacy-preserving-analytics-system-design.md) |
| AirDrop-style peer-to-peer transfer | [airdrop-p2p-transfer-system-design.md](./airdrop-p2p-transfer-system-design.md) |
| Family Sharing permissions | [family-sharing-permissions-system-design.md](./family-sharing-permissions-system-design.md) |
| On-device ML model updates | [on-device-ml-model-updates-system-design.md](./on-device-ml-model-updates-system-design.md) |
| Restore-from-backup / new-device setup | [restore-backup-new-device-system-design.md](./restore-backup-new-device-system-design.md) |
| Find My aggregation | [find-my-aggregation-system-design.md](./find-my-aggregation-system-design.md) |
| App Store search and ranking | [app-store-search-ranking-system-design.md](./app-store-search-ranking-system-design.md) |
| Apple Arcade game-progress synchronization | [arcade-game-progress-sync-system-design.md](./arcade-game-progress-sync-system-design.md) |
| Low-power Bluetooth beacon relay | [bluetooth-beacon-relay-system-design.md](./bluetooth-beacon-relay-system-design.md) |
| Offline-first Reminders | [offline-first-reminders-system-design.md](./offline-first-reminders-system-design.md) |
| Safari Reading List synchronization | [safari-reading-list-sync-system-design.md](./safari-reading-list-sync-system-design.md) |
| Local DB with on-demand cloud fetching | [local-db-on-demand-cloud-fetch-system-design.md](./local-db-on-demand-cloud-fetch-system-design.md) |
| Focus Mode propagation across devices | [focus-mode-propagation-system-design.md](./focus-mode-propagation-system-design.md) |

---

**Prep priority (senior backend / distributed systems):** rate limiter → distributed job scheduler → global block storage → storage/auth migration → CI/CD → P2P crawler → safe restart → typeahead → iMessage multi-device → iCloud photo / notes sync → defend your own system.
