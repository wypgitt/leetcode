# Databricks System Design Interview Prep

> Databricks has two unusually distinct pools:
> 1. **Architecture / HLD** — distributed services, filesystems, schedulers, APIs  
> 2. **Component / LLD** — storage engines, concurrency, durability, caching, runnable pseudocode  
>
> The bank is comparatively **small and repetitive**; seniors often get both HLD and an implementation-oriented LLD round. Recent exact reports remain predominantly general distributed-systems and storage questions—not “design Databricks” or “design Spark.”

Style matches `../OpenAI/*` and `../Amazon/*`: clarify → estimate → HLD + trade-offs → diagram → deep dive (reliability / scalability / maintainability) → wrap-up → interviewer traps. Progressive scale **10× → 100× → 1,000×**. LLD docs include classes, APIs, locks, and pseudocode.

---

## Architecture / HLD bank

| Family | Problem | File |
|--------|---------|------|
| Books / commerce | Book-price aggregator (50–200 seller APIs) | [book-price-aggregator-system-design.md](./book-price-aggregator-system-design.md) |
| Books / commerce | Online bookstore | [online-bookstore-system-design.md](./online-bookstore-system-design.md) |
| Books / commerce | Bookstore pricing API with batch fetches | [bookstore-pricing-api-system-design.md](./bookstore-pricing-api-system-design.md) |
| Messaging | Slack-like messaging | [slack-messaging-system-design.md](./slack-messaging-system-design.md) |
| Messaging | Group chat (global deletion semantics) | [group-chat-global-deletion-system-design.md](./group-chat-global-deletion-system-design.md) |
| Messaging | Chat with partitioned cache | [chat-partitioned-cache-system-design.md](./chat-partitioned-cache-system-design.md) |
| Storage | Distributed filesystem | [distributed-filesystem-system-design.md](./distributed-filesystem-system-design.md) |
| Storage | Hierarchical filesystem | [hierarchical-filesystem-system-design.md](./hierarchical-filesystem-system-design.md) |
| Storage | S3-like object storage | [s3-object-storage-system-design.md](./s3-object-storage-system-design.md) |
| Storage | Dropbox / file synchronization | [dropbox-file-sync-system-design.md](./dropbox-file-sync-system-design.md) |
| Scheduling | Stock-order manager (deadlines + cancellation) | [stock-order-manager-system-design.md](./stock-order-manager-system-design.md) |
| Scheduling | General job scheduler | [job-scheduler-system-design.md](./job-scheduler-system-design.md) |
| Scheduling | GPU scheduler | [gpu-scheduler-system-design.md](./gpu-scheduler-system-design.md) |
| Distributed infra | Kafka-like message queue | [kafka-like-message-queue-system-design.md](./kafka-like-message-queue-system-design.md) |
| Distributed infra | Distributed web crawler | [distributed-web-crawler-system-design.md](./distributed-web-crawler-system-design.md) |
| Distributed infra | VM-bandwidth rate limiter | [vm-bandwidth-rate-limiter-system-design.md](./vm-bandwidth-rate-limiter-system-design.md) |
| Distributed infra | Serving-infrastructure throttle / safety system | [serving-throttle-safety-system-design.md](./serving-throttle-safety-system-design.md) |
| Financial | Visa-like payment-routing network | [visa-payment-routing-system-design.md](./visa-payment-routing-system-design.md) |
| Financial | Stock-trading platform | [stock-trading-platform-system-design.md](./stock-trading-platform-system-design.md) |
| Service / API | CRUD service with asynchronous jobs | [crud-async-jobs-system-design.md](./crud-async-jobs-system-design.md) |
| Service / API | KV store with QPS API | [kv-store-qps-api-system-design.md](./kv-store-qps-api-system-design.md) |
| Service / API | Digital game-store backend | [digital-game-store-system-design.md](./digital-game-store-system-design.md) |
| Product / FE | Collaborative playlist editor | [collaborative-playlist-editor-system-design.md](./collaborative-playlist-editor-system-design.md) |

---

## Component / concurrency / storage LLD bank

| Problem | File |
|---------|------|
| Single-node persistent in-memory cache | [persistent-inmemory-cache-lld-system-design.md](./persistent-inmemory-cache-lld-system-design.md) |
| Crash- and power-loss-safe embedded KV store | [durable-embedded-kv-store-lld-system-design.md](./durable-embedded-kv-store-lld-system-design.md) |
| Concurrent range-aware client-side file cache | [ranged-file-cache-lld-system-design.md](./ranged-file-cache-lld-system-design.md) |
| Generic type-safe key-value-store API | [type-safe-kv-api-lld-system-design.md](./type-safe-kv-api-lld-system-design.md) |
| Thread-safe bounded MPMC queue (timeouts + fairness) | [mpmc-queue-lld-system-design.md](./mpmc-queue-lld-system-design.md) |
| Thread-safe buffered writer with background flush | [buffered-writer-lld-system-design.md](./buffered-writer-lld-system-design.md) |
| Durable concurrent event writer | [durable-event-writer-lld-system-design.md](./durable-event-writer-lld-system-design.md) |
| Sliding-window QPS metrics on in-memory KV store | [kv-sliding-window-qps-lld-system-design.md](./kv-sliding-window-qps-lld-system-design.md) |
| Identify and repair races in KV store + hit counter | [kv-race-repair-lld-system-design.md](./kv-race-repair-lld-system-design.md) |
| CIDR firewall-rule matcher | [cidr-firewall-matcher-lld-system-design.md](./cidr-firewall-matcher-lld-system-design.md) |
| Chat-deletion semantics under concurrent sends | [chat-deletion-concurrent-sends-lld-system-design.md](./chat-deletion-concurrent-sends-lld-system-design.md) |

---

## Data-platform topics (role-specific practice; not a proven fixed bank)

| Problem | File |
|---------|------|
| Batch and streaming ingestion | [batch-streaming-ingestion-system-design.md](./batch-streaming-ingestion-system-design.md) |
| High-throughput ETL pipelines | [high-throughput-etl-system-design.md](./high-throughput-etl-system-design.md) |
| Spark-style distributed execution | [spark-style-distributed-execution-system-design.md](./spark-style-distributed-execution-system-design.md) |
| Checkpointing and exactly-once processing | [checkpointing-exactly-once-system-design.md](./checkpointing-exactly-once-system-design.md) |
| Lakehouse / object-storage architecture | [lakehouse-object-storage-system-design.md](./lakehouse-object-storage-system-design.md) |
| Transaction logs and Delta-like storage | [delta-like-transaction-log-system-design.md](./delta-like-transaction-log-system-design.md) |
| Compute autoscaling and job orchestration | [compute-autoscaling-orchestration-system-design.md](./compute-autoscaling-orchestration-system-design.md) |
| Metadata, schema evolution, governance, lineage | [metadata-governance-lineage-system-design.md](./metadata-governance-lineage-system-design.md) |
| Storage-versus-compute trade-offs | [storage-vs-compute-tradeoffs-system-design.md](./storage-vs-compute-tradeoffs-system-design.md) |
| Pipeline recovery and backpressure | [pipeline-recovery-backpressure-system-design.md](./pipeline-recovery-backpressure-system-design.md) |

---

**Prep priority (backend / data platform):** book-price aggregator → durable KV store → persistent concurrent cache → ranged-read file cache → Slack with global deletion → distributed filesystem / S3 → stock-order manager → Kafka-like MQ → Delta/lakehouse topics for data roles.
