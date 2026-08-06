# Fundamentals — 200+ System Design Problem Bank

> Unified cross-company master bank (**449** distinct problem files).
> Style matches `../OpenAI/openai-playground-system-design.md`:
> clarify (Q&A) → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps.
> Progressive scale **10× → 100× → 1,000×**.
>
> **Status:** Every problem has a dedicated `*-system-design.md` (≥550 lines). Highest-priority and overlapping company docs are deepened first; background enrichment continues for remaining files.
> **Start here:** [Highest-priority set](#highest-priority-set-data-platform--backend-background) below, then work section-by-section.


---

## Highest-priority set (data-platform / backend background)

| # | Problem | File |
|---|---------|------|
| 1 | Kafka-style distributed log | [kafka-distributed-log-system-design.md](./kafka-distributed-log-system-design.md) |
| 2 | Real-time event-ingestion platform | [realtime-event-ingestion-system-design.md](./realtime-event-ingestion-system-design.md) |
| 3 | Batch-ingestion platform | [batch-ingestion-platform-system-design.md](./batch-ingestion-platform-system-design.md) |
| 4 | Workflow/DAG execution engine | [workflow-dag-execution-engine-system-design.md](./workflow-dag-execution-engine-system-design.md) |
| 5 | Lakehouse | [lakehouse-system-design.md](./lakehouse-system-design.md) |
| 6 | Distributed query engine | [distributed-query-engine-system-design.md](./distributed-query-engine-system-design.md) |
| 7 | Multi-tenant interactive analytics platform | [multi-tenant-interactive-analytics-system-design.md](./multi-tenant-interactive-analytics-system-design.md) |
| 8 | Metadata catalog | [metadata-catalog-system-design.md](./metadata-catalog-system-design.md) |
| 9 | Schema registry | [schema-registry-system-design.md](./schema-registry-system-design.md) |
| 10 | Change-data capture | [change-data-capture-system-design.md](./change-data-capture-system-design.md) |
| 11 | Event deduplication and exactly-once-like processing | [event-deduplication-exactly-once-system-design.md](./event-deduplication-exactly-once-system-design.md) |
| 12 | Data reconciliation between multiple providers | [data-reconciliation-system-design.md](./data-reconciliation-system-design.md) |
| 13 | Materialized-view system | [materialized-view-system-system-design.md](./materialized-view-system-system-design.md) |
| 14 | Caching for a DAG of dependent materialized views | [dag-materialized-view-caching-system-design.md](./dag-materialized-view-caching-system-design.md) |
| 15 | S3 / blob storage | [s3-blob-storage-system-design.md](./s3-blob-storage-system-design.md) |
| 16 | Distributed key-value store | [distributed-key-value-store-system-design.md](./distributed-key-value-store-system-design.md) |
| 17 | Distributed cache | [distributed-cache-system-design.md](./distributed-cache-system-design.md) |
| 18 | Distributed rate limiter | [distributed-rate-limiter-system-design.md](./distributed-rate-limiter-system-design.md) |
| 19 | Hierarchical quotas (user, team, tenant, API, region) | [hierarchical-quotas-system-design.md](./hierarchical-quotas-system-design.md) |
| 20 | Distributed locks and leases | [distributed-locks-leases-system-design.md](./distributed-locks-leases-system-design.md) |
| 21 | Leader election | [leader-election-system-design.md](./leader-election-system-design.md) |
| 22 | Metrics-monitoring platform | [metrics-monitoring-platform-system-design.md](./metrics-monitoring-platform-system-design.md) |
| 23 | Centralized log collection and search | [centralized-log-collection-search-system-design.md](./centralized-log-collection-search-system-design.md) |
| 24 | Distributed tracing | [distributed-tracing-system-design.md](./distributed-tracing-system-design.md) |
| 25 | Alerting platform | [alerting-platform-system-design.md](./alerting-platform-system-design.md) |
| 26 | Data-quality monitoring platform | [data-quality-monitoring-system-design.md](./data-quality-monitoring-system-design.md) |
| 27 | Data lineage and governance | [data-lineage-governance-system-design.md](./data-lineage-governance-system-design.md) |
| 28 | Multi-region data replication and conflict resolution | [multi-region-replication-conflict-resolution-system-design.md](./multi-region-replication-conflict-resolution-system-design.md) |
| 29 | Compute-cluster control plane | [compute-cluster-control-plane-system-design.md](./compute-cluster-control-plane-system-design.md) |
| 30 | Fair resource allocation across tenants | [fair-resource-allocation-tenants-system-design.md](./fair-resource-allocation-tenants-system-design.md) |
| 31 | Diagnose and redesign an overloaded Kubernetes cluster | [overloaded-kubernetes-cluster-diagnosis-system-design.md](./overloaded-kubernetes-cluster-diagnosis-system-design.md) |
| 32 | Autoscaling | [autoscaling-system-design.md](./autoscaling-system-design.md) |
| 33 | GPU/accelerator scheduler | [gpu-accelerator-scheduler-system-design.md](./gpu-accelerator-scheduler-system-design.md) |
| 34 | Batch-inference API over a GPU cluster | [batch-inference-gpu-cluster-system-design.md](./batch-inference-gpu-cluster-system-design.md) |
| 35 | Retrieval-augmented generation | [retrieval-augmented-generation-system-design.md](./retrieval-augmented-generation-system-design.md) |
| 36 | Vector database | [vector-database-system-design.md](./vector-database-system-design.md) |
| 37 | Model gateway | [model-gateway-system-design.md](./model-gateway-system-design.md) |
| 38 | Per-user token quotas and rate limits | [per-user-token-quotas-rate-limits-system-design.md](./per-user-token-quotas-rate-limits-system-design.md) |
| 39 | Feature store | [feature-store-system-design.md](./feature-store-system-design.md) |
| 40 | Feature store (ML) | [feature-store-ml-system-design.md](./feature-store-ml-system-design.md) |
| 41 | A/B experimentation platform | [ab-experimentation-platform-system-design.md](./ab-experimentation-platform-system-design.md) |
| 42 | Payment gateway | [payment-gateway-system-design.md](./payment-gateway-system-design.md) |
| 43 | Double-entry ledger | [double-entry-ledger-system-design.md](./double-entry-ledger-system-design.md) |
| 44 | Reliable webhook-delivery platform | [reliable-webhook-delivery-system-design.md](./reliable-webhook-delivery-system-design.md) |
| 45 | Ticketmaster | [ticketmaster-system-design.md](./ticketmaster-system-design.md) |
| 46 | Assigned-seat reservation | [assigned-seat-reservation-system-design.md](./assigned-seat-reservation-system-design.md) |
| 47 | Inventory reservation | [inventory-reservation-system-design.md](./inventory-reservation-system-design.md) |
| 48 | Uber or Lyft | [uber-lyft-system-design.md](./uber-lyft-system-design.md) |
| 49 | Real-time driver-location tracking | [realtime-driver-location-tracking-system-design.md](./realtime-driver-location-tracking-system-design.md) |
| 50 | Google Docs collaborative editing | [google-docs-collaborative-editing-system-design.md](./google-docs-collaborative-editing-system-design.md) |
| 51 | Multi-channel notification system | [multi-channel-notification-system-design.md](./multi-channel-notification-system-design.md) |
| 52 | Typeahead / autocomplete | [typeahead-autocomplete-system-design.md](./typeahead-autocomplete-system-design.md) |
| 53 | Full-text search for posts or documents | [full-text-search-system-design.md](./full-text-search-system-design.md) |
| 54 | Dropbox/Google Drive file synchronization | [dropbox-google-drive-sync-system-design.md](./dropbox-google-drive-sync-system-design.md) |
| 55 | Authentication and session management | [authentication-session-management-system-design.md](./authentication-session-management-system-design.md) |
| 56 | Role-based access control | [rbac-system-design.md](./rbac-system-design.md) |
| 57 | Immutable or tamper-evident audit log | [immutable-tamper-evident-audit-log-system-design.md](./immutable-tamper-evident-audit-log-system-design.md) |
| 58 | Migration from a monolith to services | [monolith-to-services-migration-system-design.md](./monolith-to-services-migration-system-design.md) |
| 59 | Zero-downtime database migration | [zero-downtime-database-migration-system-design.md](./zero-downtime-database-migration-system-design.md) |
| 60 | Per-tenant cost attribution and chargeback | [per-tenant-cost-attribution-chargeback-system-design.md](./per-tenant-cost-attribution-chargeback-system-design.md) |
| 61 | Load shedding and graceful degradation | [load-shedding-graceful-degradation-system-design.md](./load-shedding-graceful-degradation-system-design.md) |

---

## Core distributed-system primitives

| # | Problem | File |
|---|---------|------|
| 1 | URL shortener with custom URLs, expiration, and analytics | [url-shortener-system-design.md](./url-shortener-system-design.md) |
| 2 | Pastebin / expiring text-sharing service | [pastebin-system-design.md](./pastebin-system-design.md) |
| 3 | Globally unique ID generator | [globally-unique-id-generator-system-design.md](./globally-unique-id-generator-system-design.md) |
| 4 | Single-machine rate limiter | [single-machine-rate-limiter-system-design.md](./single-machine-rate-limiter-system-design.md) |
| 5 | Distributed rate limiter | [distributed-rate-limiter-system-design.md](./distributed-rate-limiter-system-design.md) |
| 6 | Hierarchical quotas (user, team, tenant, API, region) | [hierarchical-quotas-system-design.md](./hierarchical-quotas-system-design.md) |
| 7 | Token- or spend-budget service | [token-spend-budget-service-system-design.md](./token-spend-budget-service-system-design.md) |
| 8 | Load balancer | [load-balancer-system-design.md](./load-balancer-system-design.md) |
| 9 | Dynamic round-robin router with health checks | [dynamic-round-robin-router-system-design.md](./dynamic-round-robin-router-system-design.md) |
| 10 | API gateway | [api-gateway-system-design.md](./api-gateway-system-design.md) |
| 11 | Service discovery | [service-discovery-system-design.md](./service-discovery-system-design.md) |
| 12 | Consistent-hash routing with replication | [consistent-hash-routing-system-design.md](./consistent-hash-routing-system-design.md) |
| 13 | Configuration-management service | [configuration-management-system-design.md](./configuration-management-system-design.md) |
| 14 | Feature-flag platform | [feature-flag-platform-system-design.md](./feature-flag-platform-system-design.md) |
| 15 | Distributed locks and leases | [distributed-locks-leases-system-design.md](./distributed-locks-leases-system-design.md) |
| 16 | Leader election | [leader-election-system-design.md](./leader-election-system-design.md) |
| 17 | ZooKeeper/Chubby-style coordination service | [zookeeper-chubby-coordination-system-design.md](./zookeeper-chubby-coordination-system-design.md) |
| 18 | Distributed cache | [distributed-cache-system-design.md](./distributed-cache-system-design.md) |
| 19 | Redis | [redis-system-design.md](./redis-system-design.md) |
| 20 | In-memory database | [in-memory-database-system-design.md](./in-memory-database-system-design.md) |
| 21 | Distributed key-value store | [distributed-key-value-store-system-design.md](./distributed-key-value-store-system-design.md) |
| 22 | Disk-backed durable key-value store | [disk-backed-durable-kv-store-system-design.md](./disk-backed-durable-kv-store-system-design.md) |
| 23 | Globally replicated read-heavy store | [globally-replicated-read-heavy-store-system-design.md](./globally-replicated-read-heavy-store-system-design.md) |
| 24 | Distributed SQL database | [distributed-sql-database-system-design.md](./distributed-sql-database-system-design.md) |
| 25 | S3 / blob storage | [s3-blob-storage-system-design.md](./s3-blob-storage-system-design.md) |
| 26 | Distributed filesystem | [distributed-filesystem-system-design.md](./distributed-filesystem-system-design.md) |
| 27 | Dropbox/Google Drive file synchronization | [dropbox-google-drive-sync-system-design.md](./dropbox-google-drive-sync-system-design.md) |
| 28 | Kafka-style distributed log | [kafka-distributed-log-system-design.md](./kafka-distributed-log-system-design.md) |
| 29 | Message queue | [message-queue-system-design.md](./message-queue-system-design.md) |
| 30 | Publish/subscribe infrastructure | [pubsub-infrastructure-system-design.md](./pubsub-infrastructure-system-design.md) |
| 31 | Delayed-message or scheduled-message queue | [delayed-scheduled-message-queue-system-design.md](./delayed-scheduled-message-queue-system-design.md) |
| 32 | Distributed job scheduler | [distributed-job-scheduler-system-design.md](./distributed-job-scheduler-system-design.md) |
| 33 | Distributed cron | [distributed-cron-system-design.md](./distributed-cron-system-design.md) |
| 34 | Workflow/DAG execution engine | [workflow-dag-execution-engine-system-design.md](./workflow-dag-execution-engine-system-design.md) |
| 35 | Reminder service | [reminder-service-system-design.md](./reminder-service-system-design.md) |
| 36 | Serverless execution platform | [serverless-execution-platform-system-design.md](./serverless-execution-platform-system-design.md) |
| 37 | Session or token store | [session-token-store-system-design.md](./session-token-store-system-design.md) |
| 38 | Global distributed counter | [global-distributed-counter-system-design.md](./global-distributed-counter-system-design.md) |
| 39 | Dependency graph and failure-detection service | [dependency-graph-failure-detection-system-design.md](./dependency-graph-failure-detection-system-design.md) |
| 40 | Software deployment with canaries and rollback | [software-deployment-canary-rollback-system-design.md](./software-deployment-canary-rollback-system-design.md) |
| 41 | Over-the-air updates for millions of devices | [ota-updates-millions-devices-system-design.md](./ota-updates-millions-devices-system-design.md) |

## Data platforms, streaming, search, and analytics

| # | Problem | File |
|---|---------|------|
| 1 | Distributed web crawler | [distributed-web-crawler-system-design.md](./distributed-web-crawler-system-design.md) |
| 2 | Web search engine | [web-search-engine-system-design.md](./web-search-engine-system-design.md) |
| 3 | Full-text search for posts or documents | [full-text-search-system-design.md](./full-text-search-system-design.md) |
| 4 | Typeahead / autocomplete | [typeahead-autocomplete-system-design.md](./typeahead-autocomplete-system-design.md) |
| 5 | Geospatial search | [geospatial-search-system-design.md](./geospatial-search-system-design.md) |
| 6 | Vector or semantic search | [vector-semantic-search-system-design.md](./vector-semantic-search-system-design.md) |
| 7 | Metadata catalog | [metadata-catalog-system-design.md](./metadata-catalog-system-design.md) |
| 8 | Schema registry | [schema-registry-system-design.md](./schema-registry-system-design.md) |
| 9 | Batch-ingestion platform | [batch-ingestion-platform-system-design.md](./batch-ingestion-platform-system-design.md) |
| 10 | Real-time event-ingestion platform | [realtime-event-ingestion-system-design.md](./realtime-event-ingestion-system-design.md) |
| 11 | Clickstream collection system | [clickstream-collection-system-design.md](./clickstream-collection-system-design.md) |
| 12 | Log-ingestion pipeline | [log-ingestion-pipeline-system-design.md](./log-ingestion-pipeline-system-design.md) |
| 13 | Stream-processing engine | [stream-processing-engine-system-design.md](./stream-processing-engine-system-design.md) |
| 14 | Batch ETL/ELT platform | [batch-etl-elt-platform-system-design.md](./batch-etl-elt-platform-system-design.md) |
| 15 | Change-data capture | [change-data-capture-system-design.md](./change-data-capture-system-design.md) |
| 16 | Event deduplication and exactly-once-like processing | [event-deduplication-exactly-once-system-design.md](./event-deduplication-exactly-once-system-design.md) |
| 17 | Data reconciliation between multiple providers | [data-reconciliation-system-design.md](./data-reconciliation-system-design.md) |
| 18 | Top-K or trending-items service | [topk-trending-items-system-design.md](./topk-trending-items-system-design.md) |
| 19 | Sliding-window event counter | [sliding-window-event-counter-system-design.md](./sliding-window-event-counter-system-design.md) |
| 20 | Analytics warehouse | [analytics-warehouse-system-design.md](./analytics-warehouse-system-design.md) |
| 21 | Multi-tenant interactive analytics platform | [multi-tenant-interactive-analytics-system-design.md](./multi-tenant-interactive-analytics-system-design.md) |
| 22 | Lakehouse | [lakehouse-system-design.md](./lakehouse-system-design.md) |
| 23 | Distributed query engine | [distributed-query-engine-system-design.md](./distributed-query-engine-system-design.md) |
| 24 | Time-series database | [time-series-database-system-design.md](./time-series-database-system-design.md) |
| 25 | Metrics aggregation and rollups | [metrics-aggregation-rollups-system-design.md](./metrics-aggregation-rollups-system-design.md) |
| 26 | Materialized-view system | [materialized-view-system-system-design.md](./materialized-view-system-system-design.md) |
| 27 | Caching for a DAG of dependent materialized views | [dag-materialized-view-caching-system-design.md](./dag-materialized-view-caching-system-design.md) |
| 28 | A/B experimentation platform | [ab-experimentation-platform-system-design.md](./ab-experimentation-platform-system-design.md) |
| 29 | Feature store | [feature-store-system-design.md](./feature-store-system-design.md) |
| 30 | Recommendation-data pipeline | [recommendation-data-pipeline-system-design.md](./recommendation-data-pipeline-system-design.md) |
| 31 | Data-quality monitoring platform | [data-quality-monitoring-system-design.md](./data-quality-monitoring-system-design.md) |
| 32 | Data lineage and governance | [data-lineage-governance-system-design.md](./data-lineage-governance-system-design.md) |
| 33 | GDPR deletion across data stores and backups | [gdpr-deletion-system-design.md](./gdpr-deletion-system-design.md) |
| 34 | Snapshotting, backup, and point-in-time recovery | [snapshot-backup-pitr-system-design.md](./snapshot-backup-pitr-system-design.md) |
| 35 | Tiered hot/warm/cold data storage | [tiered-hot-warm-cold-storage-system-design.md](./tiered-hot-warm-cold-storage-system-design.md) |
| 36 | Querying massive datasets with stable pagination | [stable-pagination-massive-datasets-system-design.md](./stable-pagination-massive-datasets-system-design.md) |
| 37 | Multi-region data replication and conflict resolution | [multi-region-replication-conflict-resolution-system-design.md](./multi-region-replication-conflict-resolution-system-design.md) |

## Social, communication, and collaboration

| # | Problem | File |
|---|---------|------|
| 1 | Twitter/Facebook/LinkedIn-style news feed | [twitter-facebook-linkedin-news-feed-system-design.md](./twitter-facebook-linkedin-news-feed-system-design.md) |
| 2 | Instagram-style photo feed | [instagram-photo-feed-system-design.md](./instagram-photo-feed-system-design.md) |
| 3 | Reddit or Hacker News | [reddit-hacker-news-system-design.md](./reddit-hacker-news-system-design.md) |
| 4 | TikTok-style ranked video feed | [tiktok-ranked-video-feed-system-design.md](./tiktok-ranked-video-feed-system-design.md) |
| 5 | People you may know | [people-you-may-know-system-design.md](./people-you-may-know-system-design.md) |
| 6 | Social graph and mutual-connections service | [social-graph-mutual-connections-system-design.md](./social-graph-mutual-connections-system-design.md) |
| 7 | Tinder or matching application | [tinder-matching-system-design.md](./tinder-matching-system-design.md) |
| 8 | News-aggregation and personalization service | [news-aggregation-personalization-system-design.md](./news-aggregation-personalization-system-design.md) |
| 9 | Multi-channel notification system | [multi-channel-notification-system-design.md](./multi-channel-notification-system-design.md) |
| 10 | Push notifications | [push-notifications-system-design.md](./push-notifications-system-design.md) |
| 11 | Email-delivery platform | [email-delivery-platform-system-design.md](./email-delivery-platform-system-design.md) |
| 12 | Gmail | [gmail-system-design.md](./gmail-system-design.md) |
| 13 | Disposable-email service with expiring inboxes | [disposable-email-expiring-inboxes-system-design.md](./disposable-email-expiring-inboxes-system-design.md) |
| 14 | One-to-one chat | [one-to-one-chat-system-design.md](./one-to-one-chat-system-design.md) |
| 15 | WhatsApp | [whatsapp-system-design.md](./whatsapp-system-design.md) |
| 16 | Group chat | [group-chat-system-design.md](./group-chat-system-design.md) |
| 17 | Discord or Slack | [discord-slack-system-design.md](./discord-slack-system-design.md) |
| 18 | Twitch/YouTube live comments | [twitch-youtube-live-comments-system-design.md](./twitch-youtube-live-comments-system-design.md) |
| 19 | Presence, typing indicators, and read receipts | [presence-typing-read-receipts-system-design.md](./presence-typing-read-receipts-system-design.md) |
| 20 | Comments, replies, reactions, and mentions | [comments-replies-reactions-mentions-system-design.md](./comments-replies-reactions-mentions-system-design.md) |
| 21 | Content-sharing permission model | [content-sharing-permission-model-system-design.md](./content-sharing-permission-model-system-design.md) |
| 22 | Google Docs collaborative editing | [google-docs-collaborative-editing-system-design.md](./google-docs-collaborative-editing-system-design.md) |
| 23 | Figma/Miro multiplayer canvas | [figma-miro-multiplayer-canvas-system-design.md](./figma-miro-multiplayer-canvas-system-design.md) |
| 24 | Collaborative comments anchored to canvas objects | [collaborative-comments-canvas-system-design.md](./collaborative-comments-canvas-system-design.md) |
| 25 | Version history and undo for a collaborative editor | [version-history-undo-collaborative-editor-system-design.md](./version-history-undo-collaborative-editor-system-design.md) |
| 26 | Calendar and meeting scheduler | [calendar-meeting-scheduler-system-design.md](./calendar-meeting-scheduler-system-design.md) |
| 27 | Zoom or video conferencing | [zoom-video-conferencing-system-design.md](./zoom-video-conferencing-system-design.md) |
| 28 | Online chess/checkers platform | [online-chess-checkers-system-design.md](./online-chess-checkers-system-design.md) |
| 29 | Real-time multiplayer game | [realtime-multiplayer-game-system-design.md](./realtime-multiplayer-game-system-design.md) |
| 30 | Matchmaking | [matchmaking-system-design.md](./matchmaking-system-design.md) |
| 31 | Gaming leaderboard | [gaming-leaderboard-system-design.md](./gaming-leaderboard-system-design.md) |
| 32 | Polling or live audience-participation system | [polling-live-audience-participation-system-design.md](./polling-live-audience-participation-system-design.md) |

## Media and content platforms

| # | Problem | File |
|---|---------|------|
| 1 | YouTube | [youtube-system-design.md](./youtube-system-design.md) |
| 2 | Netflix | [netflix-system-design.md](./netflix-system-design.md) |
| 3 | Spotify | [spotify-system-design.md](./spotify-system-design.md) |
| 4 | Podcast platform | [podcast-platform-system-design.md](./podcast-platform-system-design.md) |
| 5 | Live video streaming | [live-video-streaming-system-design.md](./live-video-streaming-system-design.md) |
| 6 | Video upload and transcoding | [video-upload-transcoding-system-design.md](./video-upload-transcoding-system-design.md) |
| 7 | Image-upload and processing pipeline | [image-upload-processing-system-design.md](./image-upload-processing-system-design.md) |
| 8 | Photo-album service | [photo-album-service-system-design.md](./photo-album-service-system-design.md) |
| 9 | CDN | [cdn-system-design.md](./cdn-system-design.md) |
| 10 | Adaptive-bitrate streaming | [adaptive-bitrate-streaming-system-design.md](./adaptive-bitrate-streaming-system-design.md) |
| 11 | Offline media downloads | [offline-media-downloads-system-design.md](./offline-media-downloads-system-design.md) |
| 12 | Playlists and media libraries | [playlists-media-libraries-system-design.md](./playlists-media-libraries-system-design.md) |
| 13 | Recommendation system | [recommendation-system-system-design.md](./recommendation-system-system-design.md) |
| 14 | Personalized home-page ranking | [personalized-homepage-ranking-system-design.md](./personalized-homepage-ranking-system-design.md) |
| 15 | Content moderation | [content-moderation-system-design.md](./content-moderation-system-design.md) |
| 16 | Copyright or duplicate-content detection | [copyright-duplicate-content-detection-system-design.md](./copyright-duplicate-content-detection-system-design.md) |
| 17 | Subtitle and transcript processing | [subtitle-transcript-processing-system-design.md](./subtitle-transcript-processing-system-design.md) |
| 18 | Synchronized transcript highlighting during audio playback | [synchronized-transcript-highlighting-system-design.md](./synchronized-transcript-highlighting-system-design.md) |
| 19 | Voice-cloning or text-to-speech service | [voice-cloning-tts-system-design.md](./voice-cloning-tts-system-design.md) |
| 20 | Audio/video dubbing workflow | [audio-video-dubbing-workflow-system-design.md](./audio-video-dubbing-workflow-system-design.md) |
| 21 | Collaboration between reviewers, translators, and voice actors | [reviewer-translator-voice-actor-collaboration-system-design.md](./reviewer-translator-voice-actor-collaboration-system-design.md) |
| 22 | Media-frequency capping and deduplication across devices | [media-frequency-capping-dedup-system-design.md](./media-frequency-capping-dedup-system-design.md) |

## Maps, marketplaces, mobility, and logistics

| # | Problem | File |
|---|---------|------|
| 1 | Yelp or places near me | [yelp-places-near-me-system-design.md](./yelp-places-near-me-system-design.md) |
| 2 | Google Maps | [google-maps-system-design.md](./google-maps-system-design.md) |
| 3 | Route planning | [route-planning-system-design.md](./route-planning-system-design.md) |
| 4 | Nearby-friends location sharing | [nearby-friends-location-sharing-system-design.md](./nearby-friends-location-sharing-system-design.md) |
| 5 | Uber or Lyft | [uber-lyft-system-design.md](./uber-lyft-system-design.md) |
| 6 | Real-time driver-location tracking | [realtime-driver-location-tracking-system-design.md](./realtime-driver-location-tracking-system-design.md) |
| 7 | Rider-driver matching | [rider-driver-matching-system-design.md](./rider-driver-matching-system-design.md) |
| 8 | Dispatch across geographic regions | [dispatch-geographic-regions-system-design.md](./dispatch-geographic-regions-system-design.md) |
| 9 | ETA prediction and serving | [eta-prediction-serving-system-design.md](./eta-prediction-serving-system-design.md) |
| 10 | Surge pricing | [surge-pricing-system-design.md](./surge-pricing-system-design.md) |
| 11 | DoorDash or local-delivery service | [doordash-local-delivery-system-design.md](./doordash-local-delivery-system-design.md) |
| 12 | Restaurant discovery and ranking | [restaurant-discovery-ranking-system-design.md](./restaurant-discovery-ranking-system-design.md) |
| 13 | Food-order tracking | [food-order-tracking-system-design.md](./food-order-tracking-system-design.md) |
| 14 | Batched delivery assignment | [batched-delivery-assignment-system-design.md](./batched-delivery-assignment-system-design.md) |
| 15 | Delivery route optimization | [delivery-route-optimization-system-design.md](./delivery-route-optimization-system-design.md) |
| 16 | Driver earnings and payouts | [driver-earnings-payouts-system-design.md](./driver-earnings-payouts-system-design.md) |
| 17 | Reviews, ratings, voting, and reviewer rewards | [reviews-ratings-voting-rewards-system-design.md](./reviews-ratings-voting-rewards-system-design.md) |
| 18 | Airbnb or rental marketplace | [airbnb-rental-marketplace-system-design.md](./airbnb-rental-marketplace-system-design.md) |
| 19 | Marketplace listing and search | [marketplace-listing-search-system-design.md](./marketplace-listing-search-system-design.md) |
| 20 | Rental booking | [rental-booking-system-design.md](./rental-booking-system-design.md) |
| 21 | Split-stay search | [split-stay-search-system-design.md](./split-stay-search-system-design.md) |
| 22 | Listing watchlists and availability alerts | [listing-watchlists-availability-alerts-system-design.md](./listing-watchlists-availability-alerts-system-design.md) |
| 23 | Hotel search and reservation | [hotel-search-reservation-system-design.md](./hotel-search-reservation-system-design.md) |
| 24 | Ticketmaster | [ticketmaster-system-design.md](./ticketmaster-system-design.md) |
| 25 | Assigned-seat reservation | [assigned-seat-reservation-system-design.md](./assigned-seat-reservation-system-design.md) |
| 26 | Online auction | [online-auction-system-design.md](./online-auction-system-design.md) |
| 27 | Package tracking | [package-tracking-system-design.md](./package-tracking-system-design.md) |
| 28 | Shipping-label and carrier-integration service | [shipping-label-carrier-integration-system-design.md](./shipping-label-carrier-integration-system-design.md) |
| 29 | Warehouse inventory and fulfillment | [warehouse-inventory-fulfillment-system-design.md](./warehouse-inventory-fulfillment-system-design.md) |
| 30 | Fleet-management platform | [fleet-management-platform-system-design.md](./fleet-management-platform-system-design.md) |
| 31 | EV charging-station discovery and reservations | [ev-charging-discovery-reservations-system-design.md](./ev-charging-discovery-reservations-system-design.md) |
| 32 | Dynamic delivery pricing | [dynamic-delivery-pricing-system-design.md](./dynamic-delivery-pricing-system-design.md) |
| 33 | Offline reservation cache for mobile clients | [offline-reservation-cache-mobile-system-design.md](./offline-reservation-cache-mobile-system-design.md) |

## E-commerce and advertising

| # | Problem | File |
|---|---------|------|
| 1 | E-commerce product page | [ecommerce-product-page-system-design.md](./ecommerce-product-page-system-design.md) |
| 2 | Product catalog | [product-catalog-system-design.md](./product-catalog-system-design.md) |
| 3 | Product search | [product-search-system-design.md](./product-search-system-design.md) |
| 4 | Shopping cart | [shopping-cart-system-design.md](./shopping-cart-system-design.md) |
| 5 | Checkout | [checkout-system-design.md](./checkout-system-design.md) |
| 6 | Order management | [order-management-system-design.md](./order-management-system-design.md) |
| 7 | Inventory reservation | [inventory-reservation-system-design.md](./inventory-reservation-system-design.md) |
| 8 | Flash sale | [flash-sale-system-design.md](./flash-sale-system-design.md) |
| 9 | Returns and refunds | [returns-refunds-system-design.md](./returns-refunds-system-design.md) |
| 10 | Shipment and fulfillment tracking | [shipment-fulfillment-tracking-system-design.md](./shipment-fulfillment-tracking-system-design.md) |
| 11 | Price tracking and price-change alerts | [price-tracking-alerts-system-design.md](./price-tracking-alerts-system-design.md) |
| 12 | Coupons and promotional rules | [coupons-promotional-rules-system-design.md](./coupons-promotional-rules-system-design.md) |
| 13 | Loyalty-points system | [loyalty-points-system-system-design.md](./loyalty-points-system-system-design.md) |
| 14 | Personalized product recommendations | [personalized-product-recommendations-system-design.md](./personalized-product-recommendations-system-design.md) |
| 15 | Seller marketplace | [seller-marketplace-system-design.md](./seller-marketplace-system-design.md) |
| 16 | Seller ratings and reputation | [seller-ratings-reputation-system-design.md](./seller-ratings-reputation-system-design.md) |
| 17 | Advertisement-serving platform | [advertisement-serving-platform-system-design.md](./advertisement-serving-platform-system-design.md) |
| 18 | Ad auction | [ad-auction-system-design.md](./ad-auction-system-design.md) |
| 19 | Ad targeting | [ad-targeting-system-design.md](./ad-targeting-system-design.md) |
| 20 | Ad-click aggregator | [ad-click-aggregator-system-design.md](./ad-click-aggregator-system-design.md) |
| 21 | Impression and conversion attribution | [impression-conversion-attribution-system-design.md](./impression-conversion-attribution-system-design.md) |
| 22 | Advertiser budget pacing | [advertiser-budget-pacing-system-design.md](./advertiser-budget-pacing-system-design.md) |
| 23 | Cross-device frequency capping | [cross-device-frequency-capping-system-design.md](./cross-device-frequency-capping-system-design.md) |
| 24 | Real-time bidding | [real-time-bidding-system-design.md](./real-time-bidding-system-design.md) |
| 25 | Fraud-resistant ad measurement | [fraud-resistant-ad-measurement-system-design.md](./fraud-resistant-ad-measurement-system-design.md) |

## Payments, banking, fintech, and crypto

| # | Problem | File |
|---|---------|------|
| 1 | Payment gateway | [payment-gateway-system-design.md](./payment-gateway-system-design.md) |
| 2 | Payment orchestration across processors | [payment-orchestration-system-design.md](./payment-orchestration-system-design.md) |
| 3 | Double-entry ledger | [double-entry-ledger-system-design.md](./double-entry-ledger-system-design.md) |
| 4 | Digital wallet | [digital-wallet-system-design.md](./digital-wallet-system-design.md) |
| 5 | Online banking system | [online-banking-system-system-design.md](./online-banking-system-system-design.md) |
| 6 | Account-to-account transfers | [account-to-account-transfers-system-design.md](./account-to-account-transfers-system-design.md) |
| 7 | Peer-to-peer payments | [peer-to-peer-payments-system-design.md](./peer-to-peer-payments-system-design.md) |
| 8 | Scheduled payments and cancellation | [scheduled-payments-cancellation-system-design.md](./scheduled-payments-cancellation-system-design.md) |
| 9 | Subscription billing | [subscription-billing-system-design.md](./subscription-billing-system-design.md) |
| 10 | Recurring invoicing | [recurring-invoicing-system-design.md](./recurring-invoicing-system-design.md) |
| 11 | Merchant payouts | [merchant-payouts-system-design.md](./merchant-payouts-system-design.md) |
| 12 | Marketplace escrow | [marketplace-escrow-system-design.md](./marketplace-escrow-system-design.md) |
| 13 | Refunds | [refunds-system-design.md](./refunds-system-design.md) |
| 14 | Disputes and chargebacks | [disputes-chargebacks-system-design.md](./disputes-chargebacks-system-design.md) |
| 15 | Reliable webhook-delivery platform | [reliable-webhook-delivery-system-design.md](./reliable-webhook-delivery-system-design.md) |
| 16 | Duplicate-payment prevention | [duplicate-payment-prevention-system-design.md](./duplicate-payment-prevention-system-design.md) |
| 17 | Payment reconciliation | [payment-reconciliation-system-design.md](./payment-reconciliation-system-design.md) |
| 18 | Payroll engine | [payroll-engine-system-design.md](./payroll-engine-system-design.md) |
| 19 | Contractor or driver payments | [contractor-driver-payments-system-design.md](./contractor-driver-payments-system-design.md) |
| 20 | Corporate-card controls | [corporate-card-controls-system-design.md](./corporate-card-controls-system-design.md) |
| 21 | Expense-policy rules engine | [expense-policy-rules-engine-system-design.md](./expense-policy-rules-engine-system-design.md) |
| 22 | Expense reimbursement and approval | [expense-reimbursement-approval-system-design.md](./expense-reimbursement-approval-system-design.md) |
| 23 | Loyalty points and cashback | [loyalty-points-cashback-system-design.md](./loyalty-points-cashback-system-design.md) |
| 24 | KYC / customer onboarding | [kyc-customer-onboarding-system-design.md](./kyc-customer-onboarding-system-design.md) |
| 25 | Transaction fraud detection | [transaction-fraud-detection-system-design.md](./transaction-fraud-detection-system-design.md) |
| 26 | Credit or underwriting decisions | [credit-underwriting-decisions-system-design.md](./credit-underwriting-decisions-system-design.md) |
| 27 | Merchant-lending platform | [merchant-lending-platform-system-design.md](./merchant-lending-platform-system-design.md) |
| 28 | Pay-by-bank | [pay-by-bank-system-design.md](./pay-by-bank-system-design.md) |
| 29 | Personal-finance aggregator | [personal-finance-aggregator-system-design.md](./personal-finance-aggregator-system-design.md) |
| 30 | Crowdfunding or donation processing | [crowdfunding-donation-processing-system-design.md](./crowdfunding-donation-processing-system-design.md) |
| 31 | Multicurrency wallet with FX and holds | [multicurrency-wallet-fx-holds-system-design.md](./multicurrency-wallet-fx-holds-system-design.md) |
| 32 | Stock exchange | [stock-exchange-system-design.md](./stock-exchange-system-design.md) |
| 33 | Order book and matching engine | [order-book-matching-engine-system-design.md](./order-book-matching-engine-system-design.md) |
| 34 | Brokerage application | [brokerage-application-system-design.md](./brokerage-application-system-design.md) |
| 35 | Real-time stock-market data | [realtime-stock-market-data-system-design.md](./realtime-stock-market-data-system-design.md) |
| 36 | Cryptocurrency exchange | [cryptocurrency-exchange-system-design.md](./cryptocurrency-exchange-system-design.md) |
| 37 | Crypto order routing across exchanges | [crypto-order-routing-system-design.md](./crypto-order-routing-system-design.md) |
| 38 | Crypto-price aggregation across inconsistent providers | [crypto-price-aggregation-system-design.md](./crypto-price-aggregation-system-design.md) |
| 39 | Blockchain transaction monitoring | [blockchain-transaction-monitoring-system-design.md](./blockchain-transaction-monitoring-system-design.md) |

## Enterprise SaaS, identity, and workflow products

| # | Problem | File |
|---|---------|------|
| 1 | Multi-tenant SaaS platform | [multi-tenant-saas-platform-system-design.md](./multi-tenant-saas-platform-system-design.md) |
| 2 | Tenant isolation and per-tenant quotas | [tenant-isolation-quotas-system-design.md](./tenant-isolation-quotas-system-design.md) |
| 3 | User, organization, team, and workspace hierarchy | [user-org-team-workspace-hierarchy-system-design.md](./user-org-team-workspace-hierarchy-system-design.md) |
| 4 | Authentication and session management | [authentication-session-management-system-design.md](./authentication-session-management-system-design.md) |
| 5 | Role-based access control | [rbac-system-design.md](./rbac-system-design.md) |
| 6 | Attribute-based access control | [abac-system-design.md](./abac-system-design.md) |
| 7 | ACLs for nested resources | [acls-nested-resources-system-design.md](./acls-nested-resources-system-design.md) |
| 8 | SSO | [sso-system-design.md](./sso-system-design.md) |
| 9 | SCIM employee provisioning | [scim-employee-provisioning-system-design.md](./scim-employee-provisioning-system-design.md) |
| 10 | Employee identity lifecycle management | [employee-identity-lifecycle-system-design.md](./employee-identity-lifecycle-system-design.md) |
| 11 | Immutable or tamper-evident audit log | [immutable-tamper-evident-audit-log-system-design.md](./immutable-tamper-evident-audit-log-system-design.md) |
| 12 | Approval-workflow engine | [approval-workflow-engine-system-design.md](./approval-workflow-engine-system-design.md) |
| 13 | Configurable business-rules engine | [configurable-business-rules-engine-system-design.md](./configurable-business-rules-engine-system-design.md) |
| 14 | Workflow-automation product like Zapier | [workflow-automation-zapier-system-design.md](./workflow-automation-zapier-system-design.md) |
| 15 | Helpdesk or customer-support ticketing system | [helpdesk-ticketing-system-design.md](./helpdesk-ticketing-system-design.md) |
| 16 | CRM | [crm-system-design.md](./crm-system-design.md) |
| 17 | Project/task management | [project-task-management-system-design.md](./project-task-management-system-design.md) |
| 18 | Document management with permissions and retention | [document-management-permissions-retention-system-design.md](./document-management-permissions-retention-system-design.md) |
| 19 | Expense-management platform | [expense-management-platform-system-design.md](./expense-management-platform-system-design.md) |
| 20 | Payroll across countries and employment types | [payroll-countries-employment-types-system-design.md](./payroll-countries-employment-types-system-design.md) |
| 21 | Employee onboarding and offboarding | [employee-onboarding-offboarding-system-design.md](./employee-onboarding-offboarding-system-design.md) |
| 22 | Third-party integration platform | [third-party-integration-platform-system-design.md](./third-party-integration-platform-system-design.md) |
| 23 | Webhook ingestion and delivery | [webhook-ingestion-delivery-system-design.md](./webhook-ingestion-delivery-system-design.md) |
| 24 | REST API abstraction and generated client SDK | [rest-api-abstraction-sdk-system-design.md](./rest-api-abstraction-sdk-system-design.md) |
| 25 | Notification-as-a-service product | [notification-as-a-service-system-design.md](./notification-as-a-service-system-design.md) |
| 26 | Subscription plans, entitlements, and feature access | [subscription-plans-entitlements-system-design.md](./subscription-plans-entitlements-system-design.md) |
| 27 | Administrative reporting dashboard | [administrative-reporting-dashboard-system-design.md](./administrative-reporting-dashboard-system-design.md) |
| 28 | Automated ticket-to-code-change workflow | [ticket-to-code-change-workflow-system-design.md](./ticket-to-code-change-workflow-system-design.md) |
| 29 | Resilient bootstrap API for loading an application first screen | [resilient-bootstrap-api-system-design.md](./resilient-bootstrap-api-system-design.md) |
| 30 | Policy-compliance and evidence-collection platform | [policy-compliance-evidence-collection-system-design.md](./policy-compliance-evidence-collection-system-design.md) |

## Observability, reliability, security, and operations

| # | Problem | File |
|---|---------|------|
| 1 | Metrics-monitoring platform | [metrics-monitoring-platform-system-design.md](./metrics-monitoring-platform-system-design.md) |
| 2 | Centralized log collection and search | [centralized-log-collection-search-system-design.md](./centralized-log-collection-search-system-design.md) |
| 3 | Distributed tracing | [distributed-tracing-system-design.md](./distributed-tracing-system-design.md) |
| 4 | APM platform | [apm-platform-system-design.md](./apm-platform-system-design.md) |
| 5 | Error tracking like Sentry | [error-tracking-sentry-system-design.md](./error-tracking-sentry-system-design.md) |
| 6 | Alerting platform | [alerting-platform-system-design.md](./alerting-platform-system-design.md) |
| 7 | Alert deduplication, grouping, and escalation | [alert-dedup-grouping-escalation-system-design.md](./alert-dedup-grouping-escalation-system-design.md) |
| 8 | Public status page | [public-status-page-system-design.md](./public-status-page-system-design.md) |
| 9 | Incident-management and on-call tooling | [incident-management-oncall-system-design.md](./incident-management-oncall-system-design.md) |
| 10 | Service health checks | [service-health-checks-system-design.md](./service-health-checks-system-design.md) |
| 11 | Dependency-aware failure detection | [dependency-aware-failure-detection-system-design.md](./dependency-aware-failure-detection-system-design.md) |
| 12 | Load shedding and graceful degradation | [load-shedding-graceful-degradation-system-design.md](./load-shedding-graceful-degradation-system-design.md) |
| 13 | Autoscaling | [autoscaling-system-design.md](./autoscaling-system-design.md) |
| 14 | Multi-region active-active failover | [multi-region-active-active-failover-system-design.md](./multi-region-active-active-failover-system-design.md) |
| 15 | Disaster recovery | [disaster-recovery-system-design.md](./disaster-recovery-system-design.md) |
| 16 | Backup verification and restoration | [backup-verification-restoration-system-design.md](./backup-verification-restoration-system-design.md) |
| 17 | Canary deployment and automatic rollback | [canary-deployment-automatic-rollback-system-design.md](./canary-deployment-automatic-rollback-system-design.md) |
| 18 | Secrets-management system | [secrets-management-system-design.md](./secrets-management-system-design.md) |
| 19 | Key-management service | [key-management-service-system-design.md](./key-management-service-system-design.md) |
| 20 | Encrypted log collection | [encrypted-log-collection-system-design.md](./encrypted-log-collection-system-design.md) |
| 21 | Security-event / SIEM pipeline | [security-event-siem-pipeline-system-design.md](./security-event-siem-pipeline-system-design.md) |
| 22 | Authentication anomaly detection | [authentication-anomaly-detection-system-design.md](./authentication-anomaly-detection-system-design.md) |
| 23 | Bot, spam, or account-abuse prevention | [bot-spam-abuse-prevention-system-design.md](./bot-spam-abuse-prevention-system-design.md) |
| 24 | WAF or DDoS-protection service | [waf-ddos-protection-system-design.md](./waf-ddos-protection-system-design.md) |
| 25 | Vulnerability-scanning infrastructure | [vulnerability-scanning-infrastructure-system-design.md](./vulnerability-scanning-infrastructure-system-design.md) |
| 26 | Compliance data retention | [compliance-data-retention-system-design.md](./compliance-data-retention-system-design.md) |
| 27 | Privacy-aware audit logging | [privacy-aware-audit-logging-system-design.md](./privacy-aware-audit-logging-system-design.md) |
| 28 | Per-tenant cost attribution and chargeback | [per-tenant-cost-attribution-chargeback-system-design.md](./per-tenant-cost-attribution-chargeback-system-design.md) |
| 29 | SLO/SLA-management platform | [slo-sla-management-platform-system-design.md](./slo-sla-management-platform-system-design.md) |
| 30 | Diagnose and redesign an overloaded Kubernetes cluster | [overloaded-kubernetes-cluster-diagnosis-system-design.md](./overloaded-kubernetes-cluster-diagnosis-system-design.md) |
| 31 | Infrastructure capacity forecasting | [infrastructure-capacity-forecasting-system-design.md](./infrastructure-capacity-forecasting-system-design.md) |

## AI, LLM, and machine-learning systems

| # | Problem | File |
|---|---------|------|
| 1 | ChatGPT | [chatgpt-system-design.md](./chatgpt-system-design.md) |
| 2 | Customer-support chatbot using a third-party LLM | [customer-support-chatbot-llm-system-design.md](./customer-support-chatbot-llm-system-design.md) |
| 3 | OpenAI Playground-style application | [openai-playground-style-app-system-design.md](./openai-playground-style-app-system-design.md) |
| 4 | AI answer engine with search and citations | [ai-answer-engine-search-citations-system-design.md](./ai-answer-engine-search-citations-system-design.md) |
| 5 | Retrieval-augmented generation | [retrieval-augmented-generation-system-design.md](./retrieval-augmented-generation-system-design.md) |
| 6 | Document ingestion for RAG | [document-ingestion-rag-system-design.md](./document-ingestion-rag-system-design.md) |
| 7 | Embedding-generation pipeline | [embedding-generation-pipeline-system-design.md](./embedding-generation-pipeline-system-design.md) |
| 8 | Vector database | [vector-database-system-design.md](./vector-database-system-design.md) |
| 9 | Hybrid lexical and semantic retrieval | [hybrid-lexical-semantic-retrieval-system-design.md](./hybrid-lexical-semantic-retrieval-system-design.md) |
| 10 | Model gateway | [model-gateway-system-design.md](./model-gateway-system-design.md) |
| 11 | Model routing across providers | [model-routing-providers-system-design.md](./model-routing-providers-system-design.md) |
| 12 | Prompt and model-version management | [prompt-model-version-management-system-design.md](./prompt-model-version-management-system-design.md) |
| 13 | Caching for LLM requests | [llm-request-caching-system-design.md](./llm-request-caching-system-design.md) |
| 14 | Streaming LLM responses | [streaming-llm-responses-system-design.md](./streaming-llm-responses-system-design.md) |
| 15 | Batch-inference API over a GPU cluster | [batch-inference-gpu-cluster-system-design.md](./batch-inference-gpu-cluster-system-design.md) |
| 16 | Low-latency online inference | [low-latency-online-inference-system-design.md](./low-latency-online-inference-system-design.md) |
| 17 | Autoscaling for expensive, bursty inference | [autoscaling-bursty-inference-system-design.md](./autoscaling-bursty-inference-system-design.md) |
| 18 | Distributed model training | [distributed-model-training-system-design.md](./distributed-model-training-system-design.md) |
| 19 | Distribute model weights to thousands of machines | [distribute-model-weights-system-design.md](./distribute-model-weights-system-design.md) |
| 20 | GPU/accelerator scheduler | [gpu-accelerator-scheduler-system-design.md](./gpu-accelerator-scheduler-system-design.md) |
| 21 | Allocate shared compute across teams and projects | [shared-compute-allocation-system-design.md](./shared-compute-allocation-system-design.md) |
| 22 | Checkpoint storage and recovery | [checkpoint-storage-recovery-system-design.md](./checkpoint-storage-recovery-system-design.md) |
| 23 | Model registry and deployment platform | [model-registry-deployment-system-design.md](./model-registry-deployment-system-design.md) |
| 24 | Feature store (ML) | [feature-store-ml-system-design.md](./feature-store-ml-system-design.md) |
| 25 | Ranking or recommendation-serving platform | [ranking-recommendation-serving-system-design.md](./ranking-recommendation-serving-system-design.md) |
| 26 | Model-evaluation platform | [model-evaluation-platform-system-design.md](./model-evaluation-platform-system-design.md) |
| 27 | LLM regression testing | [llm-regression-testing-system-design.md](./llm-regression-testing-system-design.md) |
| 28 | Experimentation and model comparison | [experimentation-model-comparison-system-design.md](./experimentation-model-comparison-system-design.md) |
| 29 | Prompt, token, latency, and cost observability | [prompt-token-latency-cost-observability-system-design.md](./prompt-token-latency-cost-observability-system-design.md) |
| 30 | Per-user token quotas and rate limits | [per-user-token-quotas-rate-limits-system-design.md](./per-user-token-quotas-rate-limits-system-design.md) |
| 31 | Autonomous agent platform | [autonomous-agent-platform-system-design.md](./autonomous-agent-platform-system-design.md) |
| 32 | Tool execution and credentials for agents | [agent-tool-execution-credentials-system-design.md](./agent-tool-execution-credentials-system-design.md) |
| 33 | Safeguards and approvals for agents taking actions | [agent-safeguards-approvals-system-design.md](./agent-safeguards-approvals-system-design.md) |
| 34 | Durable agent memory | [durable-agent-memory-system-design.md](./durable-agent-memory-system-design.md) |
| 35 | Multi-step agent workflow orchestration | [multi-step-agent-workflow-orchestration-system-design.md](./multi-step-agent-workflow-orchestration-system-design.md) |
| 36 | Human-in-the-loop review | [human-in-the-loop-review-system-design.md](./human-in-the-loop-review-system-design.md) |
| 37 | Data-labeling platform | [data-labeling-platform-system-design.md](./data-labeling-platform-system-design.md) |
| 38 | Memory-bounded dataset-cleaning pipeline | [memory-bounded-dataset-cleaning-system-design.md](./memory-bounded-dataset-cleaning-system-design.md) |
| 39 | Moderation or classification using external LLMs | [moderation-classification-external-llms-system-design.md](./moderation-classification-external-llms-system-design.md) |
| 40 | AI coding assistant | [ai-coding-assistant-system-design.md](./ai-coding-assistant-system-design.md) |
| 41 | Secure sandboxes for AI-generated code | [secure-sandboxes-ai-generated-code-system-design.md](./secure-sandboxes-ai-generated-code-system-design.md) |
| 42 | Voice generation and cloning | [voice-generation-cloning-system-design.md](./voice-generation-cloning-system-design.md) |
| 43 | Real-time speech-to-speech conversation | [realtime-speech-to-speech-system-design.md](./realtime-speech-to-speech-system-design.md) |

## Devices, mobile, edge, and IoT

| # | Problem | File |
|---|---------|------|
| 1 | IoT device registry | [iot-device-registry-system-design.md](./iot-device-registry-system-design.md) |
| 2 | Device provisioning and authentication | [device-provisioning-authentication-system-design.md](./device-provisioning-authentication-system-design.md) |
| 3 | Device telemetry ingestion | [device-telemetry-ingestion-system-design.md](./device-telemetry-ingestion-system-design.md) |
| 4 | Smart-meter event pipeline | [smart-meter-event-pipeline-system-design.md](./smart-meter-event-pipeline-system-design.md) |
| 5 | Fleet telemetry and remote control | [fleet-telemetry-remote-control-system-design.md](./fleet-telemetry-remote-control-system-design.md) |
| 6 | Over-the-air firmware rollout and rollback | [ota-firmware-rollout-rollback-system-design.md](./ota-firmware-rollout-rollback-system-design.md) |
| 7 | Offline-first mobile application | [offline-first-mobile-application-system-design.md](./offline-first-mobile-application-system-design.md) |
| 8 | Client/server synchronization after long disconnection | [client-server-sync-long-disconnection-system-design.md](./client-server-sync-long-disconnection-system-design.md) |
| 9 | Conflict resolution for offline writes | [conflict-resolution-offline-writes-system-design.md](./conflict-resolution-offline-writes-system-design.md) |
| 10 | Location-sharing service | [location-sharing-service-system-design.md](./location-sharing-service-system-design.md) |
| 11 | Battery-efficient location updates | [battery-efficient-location-updates-system-design.md](./battery-efficient-location-updates-system-design.md) |
| 12 | Mobile push notifications | [mobile-push-notifications-system-design.md](./mobile-push-notifications-system-design.md) |
| 13 | Sensor alerts | [sensor-alerts-system-design.md](./sensor-alerts-system-design.md) |
| 14 | Home-automation infrastructure | [home-automation-infrastructure-system-design.md](./home-automation-infrastructure-system-design.md) |
| 15 | Security-camera upload and streaming | [security-camera-upload-streaming-system-design.md](./security-camera-upload-streaming-system-design.md) |
| 16 | Edge cache | [edge-cache-system-design.md](./edge-cache-system-design.md) |
| 17 | Resumable upload over unreliable networks | [resumable-upload-unreliable-networks-system-design.md](./resumable-upload-unreliable-networks-system-design.md) |
| 18 | Satellite or highly disconnected storage | [satellite-disconnected-storage-system-design.md](./satellite-disconnected-storage-system-design.md) |
| 19 | Global device command-and-control plane | [global-device-command-control-plane-system-design.md](./global-device-command-control-plane-system-design.md) |

## Developer tools and cloud platforms

| # | Problem | File |
|---|---------|------|
| 1 | GitHub or Git repository hosting | [github-git-repository-hosting-system-design.md](./github-git-repository-hosting-system-design.md) |
| 2 | Pull requests, reviews, and branch protection | [pull-requests-reviews-branch-protection-system-design.md](./pull-requests-reviews-branch-protection-system-design.md) |
| 3 | Code search | [code-search-system-design.md](./code-search-system-design.md) |
| 4 | CI/CD platform | [cicd-platform-system-design.md](./cicd-platform-system-design.md) |
| 5 | Distributed build system | [distributed-build-system-system-design.md](./distributed-build-system-system-design.md) |
| 6 | Remote build caching | [remote-build-caching-system-design.md](./remote-build-caching-system-design.md) |
| 7 | Package registry | [package-registry-system-design.md](./package-registry-system-design.md) |
| 8 | Artifact or container registry | [artifact-container-registry-system-design.md](./artifact-container-registry-system-design.md) |
| 9 | Cloud IDE | [cloud-ide-system-design.md](./cloud-ide-system-design.md) |
| 10 | LeetCode or online code judge | [leetcode-online-code-judge-system-design.md](./leetcode-online-code-judge-system-design.md) |
| 11 | Secure untrusted-code execution | [secure-untrusted-code-execution-system-design.md](./secure-untrusted-code-execution-system-design.md) |
| 12 | Notebook platform | [notebook-platform-system-design.md](./notebook-platform-system-design.md) |
| 13 | Collaborative notebooks | [collaborative-notebooks-system-design.md](./collaborative-notebooks-system-design.md) |
| 14 | Database-control plane | [database-control-plane-system-design.md](./database-control-plane-system-design.md) |
| 15 | Compute-cluster control plane | [compute-cluster-control-plane-system-design.md](./compute-cluster-control-plane-system-design.md) |
| 16 | Kubernetes scheduler or operator | [kubernetes-scheduler-operator-system-design.md](./kubernetes-scheduler-operator-system-design.md) |
| 17 | Multi-tenant job-execution platform | [multi-tenant-job-execution-system-design.md](./multi-tenant-job-execution-system-design.md) |
| 18 | Fair resource allocation across tenants | [fair-resource-allocation-tenants-system-design.md](./fair-resource-allocation-tenants-system-design.md) |
| 19 | Cloud connection or database proxy | [cloud-connection-database-proxy-system-design.md](./cloud-connection-database-proxy-system-design.md) |
| 20 | API-management platform | [api-management-platform-system-design.md](./api-management-platform-system-design.md) |
| 21 | Developer webhook platform | [developer-webhook-platform-system-design.md](./developer-webhook-platform-system-design.md) |
| 22 | Migration from a monolith to services | [monolith-to-services-migration-system-design.md](./monolith-to-services-migration-system-design.md) |
| 23 | Zero-downtime database migration | [zero-downtime-database-migration-system-design.md](./zero-downtime-database-migration-system-design.md) |
| 24 | Control-plane / data-plane separation | [control-plane-data-plane-separation-system-design.md](./control-plane-data-plane-separation-system-design.md) |
| 25 | Infrastructure-as-code state management | [iac-state-management-system-design.md](./iac-state-management-system-design.md) |
| 26 | Managed message-queue service | [managed-message-queue-service-system-design.md](./managed-message-queue-service-system-design.md) |
| 27 | Managed feature store or ML pipeline platform | [managed-feature-store-ml-pipeline-system-design.md](./managed-feature-store-ml-pipeline-system-design.md) |

## Domain-specific startup prompts

| # | Problem | File |
|---|---------|------|
| 1 | Patient appointment scheduling | [patient-appointment-scheduling-system-design.md](./patient-appointment-scheduling-system-design.md) |
| 2 | Electronic health-record system | [electronic-health-record-system-design.md](./electronic-health-record-system-design.md) |
| 3 | Provider search and availability | [provider-search-availability-system-design.md](./provider-search-availability-system-design.md) |
| 4 | Telemedicine | [telemedicine-system-design.md](./telemedicine-system-design.md) |
| 5 | Remote-patient monitoring | [remote-patient-monitoring-system-design.md](./remote-patient-monitoring-system-design.md) |
| 6 | Prescription and pharmacy fulfillment | [prescription-pharmacy-fulfillment-system-design.md](./prescription-pharmacy-fulfillment-system-design.md) |
| 7 | Lab-result ingestion and delivery | [lab-result-ingestion-delivery-system-design.md](./lab-result-ingestion-delivery-system-design.md) |
| 8 | Medical claims processing | [medical-claims-processing-system-design.md](./medical-claims-processing-system-design.md) |
| 9 | Clinical alerts | [clinical-alerts-system-design.md](./clinical-alerts-system-design.md) |
| 10 | HIPAA-compliant audit and access controls | [hipaa-compliant-audit-access-system-design.md](./hipaa-compliant-audit-access-system-design.md) |
| 11 | LMS | [lms-system-design.md](./lms-system-design.md) |
| 12 | Live online classes | [live-online-classes-system-design.md](./live-online-classes-system-design.md) |
| 13 | Course recommendations | [course-recommendations-system-design.md](./course-recommendations-system-design.md) |
| 14 | Online examination platform | [online-examination-platform-system-design.md](./online-examination-platform-system-design.md) |
| 15 | Remote proctoring | [remote-proctoring-system-design.md](./remote-proctoring-system-design.md) |
| 16 | Assignment submission and grading | [assignment-submission-grading-system-design.md](./assignment-submission-grading-system-design.md) |
| 17 | Collaborative classroom documents | [collaborative-classroom-documents-system-design.md](./collaborative-classroom-documents-system-design.md) |
| 18 | Warehouse management | [warehouse-management-system-design.md](./warehouse-management-system-design.md) |
| 19 | Inventory forecasting | [inventory-forecasting-system-design.md](./inventory-forecasting-system-design.md) |
| 20 | Shipment tracking across carriers | [shipment-tracking-across-carriers-system-design.md](./shipment-tracking-across-carriers-system-design.md) |
| 21 | Purchase-order workflow | [purchase-order-workflow-system-design.md](./purchase-order-workflow-system-design.md) |
| 22 | Factory telemetry | [factory-telemetry-system-design.md](./factory-telemetry-system-design.md) |
| 23 | Digital twin | [digital-twin-system-design.md](./digital-twin-system-design.md) |
| 24 | Cold-chain monitoring | [cold-chain-monitoring-system-design.md](./cold-chain-monitoring-system-design.md) |
| 25 | Supply-chain event reconciliation | [supply-chain-event-reconciliation-system-design.md](./supply-chain-event-reconciliation-system-design.md) |
| 26 | Property listings and search | [property-listings-search-system-design.md](./property-listings-search-system-design.md) |
| 27 | Home valuation | [home-valuation-system-design.md](./home-valuation-system-design.md) |
| 28 | Mortgage application processing | [mortgage-application-processing-system-design.md](./mortgage-application-processing-system-design.md) |
| 29 | Insurance quoting | [insurance-quoting-system-design.md](./insurance-quoting-system-design.md) |
| 30 | Policy administration | [policy-administration-system-design.md](./policy-administration-system-design.md) |
| 31 | Claims submission and adjudication | [claims-submission-adjudication-system-design.md](./claims-submission-adjudication-system-design.md) |
| 32 | Fraud-resistant damage evidence upload | [fraud-resistant-damage-evidence-upload-system-design.md](./fraud-resistant-damage-evidence-upload-system-design.md) |
| 33 | Electronic signatures | [electronic-signatures-system-design.md](./electronic-signatures-system-design.md) |
| 34 | Contract lifecycle management | [contract-lifecycle-management-system-design.md](./contract-lifecycle-management-system-design.md) |
| 35 | Document review and e-discovery | [document-review-e-discovery-system-design.md](./document-review-e-discovery-system-design.md) |
| 36 | Legal hold and retention | [legal-hold-retention-system-design.md](./legal-hold-retention-system-design.md) |
| 37 | Regulatory monitoring | [regulatory-monitoring-system-design.md](./regulatory-monitoring-system-design.md) |
| 38 | Approval and evidence workflows | [approval-evidence-workflows-system-design.md](./approval-evidence-workflows-system-design.md) |
| 39 | EV charging network | [ev-charging-network-system-design.md](./ev-charging-network-system-design.md) |
| 40 | Electricity-grid telemetry | [electricity-grid-telemetry-system-design.md](./electricity-grid-telemetry-system-design.md) |
| 41 | Demand-response controls | [demand-response-controls-system-design.md](./demand-response-controls-system-design.md) |
| 42 | Renewable-energy forecasting | [renewable-energy-forecasting-system-design.md](./renewable-energy-forecasting-system-design.md) |
| 43 | Carbon-accounting ledger | [carbon-accounting-ledger-system-design.md](./carbon-accounting-ledger-system-design.md) |
| 44 | Energy-market bidding | [energy-market-bidding-system-design.md](./energy-market-bidding-system-design.md) |

## Lower-level and machine-coding system design

| # | Problem | File |
|---|---------|------|
| 1 | LRU or LFU cache | [lru-lfu-cache-system-design.md](./lru-lfu-cache-system-design.md) |
| 2 | Connection pool | [connection-pool-system-design.md](./connection-pool-system-design.md) |
| 3 | Thread pool or task executor | [thread-pool-task-executor-system-design.md](./thread-pool-task-executor-system-design.md) |
| 4 | Bounded blocking queue | [bounded-blocking-queue-system-design.md](./bounded-blocking-queue-system-design.md) |
| 5 | Multi-producer/multi-consumer queue | [multi-producer-multi-consumer-queue-system-design.md](./multi-producer-multi-consumer-queue-system-design.md) |
| 6 | Ring buffer | [ring-buffer-system-design.md](./ring-buffer-system-design.md) |
| 7 | Buffered writer | [buffered-writer-system-design.md](./buffered-writer-system-design.md) |
| 8 | Write-ahead log | [write-ahead-log-system-design.md](./write-ahead-log-system-design.md) |
| 9 | Durable local key-value store | [durable-local-key-value-store-system-design.md](./durable-local-key-value-store-system-design.md) |
| 10 | In-memory filesystem | [in-memory-filesystem-system-design.md](./in-memory-filesystem-system-design.md) |
| 11 | In-memory cloud-storage service | [in-memory-cloud-storage-service-system-design.md](./in-memory-cloud-storage-service-system-design.md) |
| 12 | Range-based file cache | [range-based-file-cache-system-design.md](./range-based-file-cache-system-design.md) |
| 13 | Expiring cache | [expiring-cache-system-design.md](./expiring-cache-system-design.md) |
| 14 | Transactional lock manager | [transactional-lock-manager-system-design.md](./transactional-lock-manager-system-design.md) |
| 15 | Idempotency-key library | [idempotency-key-library-system-design.md](./idempotency-key-library-system-design.md) |
| 16 | Retry system with backoff and circuit breaking | [retry-backoff-circuit-breaker-system-design.md](./retry-backoff-circuit-breaker-system-design.md) |
| 17 | Token-bucket and sliding-window rate limiters | [token-bucket-sliding-window-rate-limiters-system-design.md](./token-bucket-sliding-window-rate-limiters-system-design.md) |
| 18 | Stable cursor pagination | [stable-cursor-pagination-system-design.md](./stable-cursor-pagination-system-design.md) |
| 19 | Trie-based autocomplete component | [trie-based-autocomplete-system-design.md](./trie-based-autocomplete-system-design.md) |
| 20 | IP/CIDR lookup | [ip-cidr-lookup-system-design.md](./ip-cidr-lookup-system-design.md) |
| 21 | Hierarchical filesystem permissions | [hierarchical-filesystem-permissions-system-design.md](./hierarchical-filesystem-permissions-system-design.md) |
| 22 | Recurring scheduler supporting pause, resume, cancel, and retry | [recurring-scheduler-pause-resume-system-design.md](./recurring-scheduler-pause-resume-system-design.md) |
| 23 | Append-only event store | [append-only-event-store-system-design.md](./append-only-event-store-system-design.md) |
| 24 | Lightweight transaction manager | [lightweight-transaction-manager-system-design.md](./lightweight-transaction-manager-system-design.md) |
| 25 | Concurrent counter or statistics aggregator | [concurrent-counter-statistics-aggregator-system-design.md](./concurrent-counter-statistics-aggregator-system-design.md) |
| 26 | Reusable notification library | [reusable-notification-library-system-design.md](./reusable-notification-library-system-design.md) |
