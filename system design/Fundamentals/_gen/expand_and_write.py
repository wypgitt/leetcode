#!/usr/bin/env python3
"""Expand docs 1-3 and write complete docs 4-10 at senior/staff depth."""
from pathlib import Path

BASE = Path("/Users/yingpengwang/leetcode/system design/Fundamentals")


def append_appendix(path: Path, title: str, sections: list[tuple[str, str]]) -> None:
    parts = [f"\n---\n\n## Appendix — {title}\n"]
    for i, (h, body) in enumerate(sections, 1):
        parts.append(f"\n### A.{i} {h}\n\n{body.strip()}\n")
    text = path.read_text().rstrip() + "\n" + "\n".join(parts) + "\n"
    path.write_text(text)
    print(f"expanded {path.name}: {len(text.splitlines())} lines")


def write(name: str, content: str) -> None:
    p = BASE / name
    p.write_text(content.lstrip() + "\n")
    print(f"wrote {name}: {len(content.splitlines())} lines")


# --- Expand first three ---
append_appendix(
    BASE / "kafka-distributed-log-system-design.md",
    "Operational and Interview Depth",
    [
        (
            "Segment and index layout",
            """
Each partition log is a sequence of segment files with companion offset index and timeindex.
The active segment receives appends; older segments are immutable and eligible for retention
delete or tiered upload. Binary search on the sparse index maps offset to file position in
O(log n) index entries; timestamp searches use the timeindex then a local scan.

**Interview tip:** sparse index density (for example every 4KB) trades memory vs lookup I/O.
Truncation on epoch change: when a follower discovers a leader epoch mismatch, it truncates
to the last matching epoch offset before fetching. This prevents silent divergence after
failover without enabling unclean leader election.
""",
        ),
        (
            "Producer batching math",
            """
```text
batch.size = 64KB, linger.ms = 5, compression = zstd
Effective msg/s per connection rises with batching
Latency ~= linger + network RTT + ISR wait
For payments: linger.ms=0 or 1, acks=all, idempotence=true
For clickstream: linger.ms=20-50, larger batches, lz4/zstd
```

Always separate SLA classes onto different topics or clusters so batching knobs do not collide.
""",
        ),
        (
            "Consumer fetch tuning",
            """
`fetch.min.bytes` / `fetch.max.wait.ms` control server-side batching of fetches. Too aggressive
min.bytes adds latency; too small increases request rate. `max.partition.fetch.bytes` bounds
memory per partition in the consumer. At high partition counts per consumer,
memory ~= partitions * max.partition.fetch.bytes -- a classic foot-gun.
""",
        ),
        (
            "Reassignment and preferred leader",
            """
Partition reassignment moves replicas between brokers with throttles. Prefer automatic
preferred-leader election so leadership returns to the rack-aware preferred replica after
recovery; otherwise leadership skew overloads a subset of brokers. Track preferred replica
imbalance metrics in the weekly ops review.
""",
        ),
        (
            "Quota dimensions",
            """
Produce-byte-rate, fetch-byte-rate, and request-percentage per client.id / user principal.
Quotas protect the control plane as much as disks. At multi-tenant 100x, combine quotas with
separate clusters for whale tenants -- quotas alone cannot fix pathological partition counts.
""",
        ),
        (
            "Security deep dive",
            """
TLS everywhere; SASL/SCRAM or mTLS; ACL on TOPIC, GROUP, TRANSACTIONAL_ID, CLUSTER.
Separate inter-broker and client listeners. Encryption at rest via volume encryption.
Message-level crypto in producers limits compaction usefulness on ciphertext unless envelope
encryption keeps stable keys carefully designed.
""",
        ),
        (
            "Tiered storage failure modes",
            """
Remote upload lag causes local disk pressure; remote fetch errors stall consumer catch-up;
chatty small remote reads explode cost. Mitigations: coalesced remote reads, local cache,
retain longer local for hot partitions, enable per-topic only when retention greatly exceeds
local capacity.
""",
        ),
        (
            "Chaos test script",
            """
1. Kill partition leader under acks=all load -- assert no acked gaps.
2. Pause follower -- ISR shrink -- produce fails when below min.isr.
3. Slow disk injection -- p99 spike alerts.
4. Bounce controller -- brief metadata blip, no data loss.
5. Force rebalance storm -- sticky/cooperative assignor limits revoke scope.
""",
        ),
        (
            "Comparison matrix for close",
            """
| Need | Prefer |
|------|--------|
| Replay + many independent consumers | Kafka log |
| Per-message complex routing / delay | Rabbit/SQS |
| Strict EOS DB sink | Outbox + idempotent sink |
| Multi-PB retention cheap | Tiered Kafka or lake bronze |
| Global order | Single partition (rare) or app sequencer |
""",
        ),
        (
            "Staff talking points",
            """
State HW/ISR/epoch invariants; quantify RF network amplification; refuse unclean election;
show partition budget math; escalate 100x to tiering + federation; separate produce latency
SLO classes; always mention consumer lag age, not just offset delta.
""",
        ),
    ],
)

append_appendix(
    BASE / "realtime-event-ingestion-system-design.md",
    "Operational and Interview Depth",
    [
        (
            "SDK design constraints",
            """
Mobile/web SDKs must survive offline, app kill, and flaky networks. Persist a local queue with
max bytes and an explicit drop-oldest or drop-newest policy. Use exponential backoff with full
jitter. Prefer /batch with gzip. Generate message_id client-side before enqueue so retries are
stable. Design for hours of late arrival from mobile background limits.
""",
        ),
        (
            "Enrichment pipeline",
            """
Edge enrichers add received_at, careful geo, library versions, and write_key to tenant_id.
Heavy enrichments (identity graph, bot scores) belong async after the buffer -- never block ACK
on ML. Feature-flag enrichment packs per tenant.
""",
        ),
        (
            "DLQ taxonomy",
            """
| Reason | Action |
|--------|--------|
| SCHEMA_INVALID | Fix producer; replay from DLQ after |
| AUTH_REVOKED | Drop; audit |
| PAYLOAD_TOO_LARGE | Client fix; optional pointer upload |
| CONSENT_BLOCK | Silent drop with metric |
| SINK_TIMEOUT | Retry sink; not ingest DLQ |
""",
        ),
        (
            "Bronze partitioning strategy",
            """
Partition by tenant_id / dt / hour / event. Avoid high-cardinality user_id partitions.
Compaction merges small files per partition hour. For GDPR deletes, plan rewrite jobs or a
secondary index; naive bronze scans are expensive.
""",
        ),
        (
            "Sampling and cost tiers",
            """
Server-side sample rates per event name using deterministic hash(message_id) so retries do not
bias. Always keep errors and security events at 100% sample.
""",
        ),
        (
            "Abuse and bot resistance",
            """
API keys + per-key quotas; WAF; anomaly on EPS spikes. Browser write_keys are exposeable --
bind origins, rate limit, and treat all client payloads as untrusted.
""",
        ),
        (
            "Multi-region residency",
            """
EU tenants resolve to an EU cell; bronze stays in EU. Mirror only aggregated or anonymized data
globally. Call out that cross-region raw PII mirror may be illegal.
""",
        ),
        (
            "E2E canary",
            """
Synthetic SDK emits a unique id every minute per cell; assert Kafka visibility within seconds
and bronze within minutes; page on miss. Keep canaries out of customer billing metrics.
""",
        ),
        (
            "Capacity dialogue sample",
            """
At 1M EPS and 500B, ingress is about 500MB/s, about 1.5GB/s with RF=3. That is tens of brokers
with headroom. Exact 48h UUID dedup is on the order of 1e10+ keys -- shard Bloom+Redis or lean
on sink-level dedup for analytics-grade pipelines.
""",
        ),
        (
            "Staff talking points",
            """
ACK after durable buffer; schema+DLQ; quotas/cells; bronze for replay; late events are normal;
never block collect on warehouse; whale isolation at 100x.
""",
        ),
    ],
)

append_appendix(
    BASE / "workflow-dag-execution-engine-system-design.md",
    "Operational and Interview Depth",
    [
        (
            "Definition validation checklist",
            """
Acyclic; max tasks; max map expansion; required task fields; secret refs; timeout defaults;
queue names exist; retry policies bounded; estimated critical path recorded for SLA.
""",
        ),
        (
            "Outbox pattern for enqueue",
            """
```text
BEGIN;
  UPDATE tasks SET status='READY' WHERE ...;
  INSERT INTO outbox(event_type, payload);
COMMIT;
-- publisher relays outbox to Redis/SQS
```

Prevents "DB says READY but never queued" and the dual-write inverse ghost task.
""",
        ),
        (
            "Worker sandboxing",
            """
Run untrusted containers with CPU/memory limits, egress allowlists, and non-root. Pass params
via files; capture logs to object store with size caps. HTTP activities enforce timeout and
response size limits.
""",
        ),
        (
            "Priority and aging",
            """
High/med/low queues; aging boosts low-priority tasks that waited beyond T to avoid starvation.
Tenant concurrency caps apply after priority selection.
""",
        ),
        (
            "Signals and human tasks",
            """
Run enters WAITING_SIGNAL; external POST resumes with payload; scheduler records the event then
unlocks. Human approval is a durable wait with reminders -- not thread.sleep in a worker.
""",
        ),
        (
            "Saga compensation example",
            """
Book flight, book hotel, charge card. On fail after hotel: compensate cancel hotel, cancel flight.
Compensations must be idempotent and often best-effort with a manual ops queue for hard failures.
""",
        ),
        (
            "History query patterns",
            """
Index (workflow_id, created_at desc) and (status, updated_at). Large attempt payloads become
object pointers. Export to an analytics lake nightly.
""",
        ),
        (
            "Scheduler sharding algorithm",
            """
```text
owner = consistent_hash(run_id, scheduler_nodes)
Only owner advances that run.
On node loss, ring remaps; new owner loads RUNNING runs and reconciles leases.
```
""",
        ),
        (
            "Comparison: managed vs self-built",
            """
Managed Step Functions: less ops, pay per transition, vendor limits. Self-built: deeper
integration and better unit cost at huge scale, but you own HA. Pick self-built in interview
unless told to use cloud primitives.
""",
        ),
        (
            "Staff talking points",
            """
State machines + leases; idempotent activities; outbox; shard schedulers; bound dynamic maps;
archive history; fairness queues; never run business logic inside the scheduler process.
""",
        ),
    ],
)

print("phase1 done")
