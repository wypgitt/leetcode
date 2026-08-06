"""Shared appendix blocks for LLD docs."""

from __future__ import annotations


def common_appendices(slug: str, extra: list[tuple[str, str]] | None = None) -> list[tuple[str, str]]:
    base = [
        ("A. Complexity summary", """| Operation | Time | Space |
|-----------|------|-------|
| Hot-path read | O(1) avg unless noted | O(1) |
| Hot-path write | O(1) avg unless noted | O(1) |
| Scan / enumerate | O(n) | O(n) output |"""),
        ("B. Thread-safety checklist", """- [ ] Lock order documented and acyclic
- [ ] No lock held during slow I/O unless intentional (document)
- [ ] Condition waits use while-loop predicate
- [ ] close() flushes/joins/shuts down deterministically
- [ ] TSan / Helgrind clean on stress tests
- [ ] Metrics use atomics, not lock-protected counters on hot path"""),
        ("C. Options defaults (interview)", """```text
max_entry_bytes = 1_048_576
timeout_ms = 30_000
metrics_enabled = true
```"""),
        ("D. Metrics", """```text
ops_total{op=put|get|...}
latency_ms{op, quantile}
errors_total{code}
queue_depth / buffer_fill_ratio (if applicable)
```"""),
        ("E. Minimal Java-like sketch", f"""```text
// See Section 6 pseudocode for {slug}
// Keep public surface small; test invariants explicitly.
```"""),
    ]
    if extra:
        base.extend(extra)
    base.extend(_extended_appendices(slug))
    return base


def _extended_appendices(slug: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    drills = [
        ("Whiteboard timing (45 min)", "5 clarify · 10 API/classes · 15 pseudocode+concurrency · 5 failures/tests · 5 scale · 5 Q&A"),
        ("Invariant card", "Write 3 invariants on board before coding; refer back when adding features"),
        ("Lock graph", "Draw threads × locks; verify no cycle before implementation"),
        ("Failure story", "Pick one crash point; walk recovery step-by-step"),
        ("Test naming", "test_concurrent_X_when_Y_then_Z for each race fixed"),
    ]
    for i, (title, body) in enumerate(drills, 1):
        items.append((f"I.{i} {title}", body))

    items.append(("J. Comparison — related Databricks LLDs", """| Related doc | When to cross-reference |
|-------------|-------------------------|
| durable-embedded-kv-store | Persistence layer beneath typed API |
| kv-sliding-window-qps | Metrics hooks on get/put |
| kv-race-repair | Correct concurrent counter patterns |
| buffered-writer / durable-event-writer | Serialize + append typed events |"""))

    items.append(("K. Extended edge matrix", """| Edge | Detection | Mitigation | User impact |
|------|-----------|------------|-------------|
| Duplicate request | Idempotency key | Return first result | None |
| Slow path | Timeout | Backpressure / reject | Retryable error |
| Hot key | Metrics | Shard / coalesce | Higher latency |
| Partial failure | Health check | Degrade mode | Explicit error |
| Clock skew | Server time | Don't trust client clocks | Ordering fix |"""))

    items.append(("L. API error taxonomy", """| Code / Exception | When |
|------------------|------|
| InvalidArgument | Bad input, bounds |
| TypeMismatch / Conflict | Schema/type/state conflict |
| Timeout | Blocking op exceeded limit |
| Closed | After shutdown |
| IOError | Underlying I/O failure |"""))

    items.append(("M. Load math template", """```text
peak_qps = daily_ops / 86400 * peak_factor
concurrency ≈ peak_qps * service_time_s
memory_bytes ≈ entries * avg_entry_bytes * overhead_factor
```"""))

    items.append(("N. Interview close sentence", f"""> "For MVP I'd ship the correctness-first single-node design for {slug.replace('-', ' ')} with explicit invariants and TSan-clean concurrency; scale-out would shard by natural key partition and push aggregation off the hot path."""))

    for n in range(1, 16):
        items.append((f"O.{n} Review prompt {n}", f"""**Prompt:** Extend {slug} for stress scenario {n}.

**Strong response:** State invariant → minimal change → pseudocode delta → one test.

```text
// scenario {n}: document expected behavior under concurrency/load
assert postcondition_holds()
```"""))

    items.append(("P. Glossary", """| Term | Meaning |
|------|---------|
| TypeTag | Runtime type identifier for stored blob |
| Linearizable | Ops appear atomic in some serial order |
| Tombstone | Delete marker retained for ordering |
| Backpressure | Slow producers when buffer full |
| LPM | Longest-prefix match (CIDR) |"""))

    items.append(("Q. Final whiteboard checklist", """- [ ] FR/NFR locked with numbers
- [ ] API + error model on board
- [ ] Class diagram + lock order
- [ ] Core pseudocode for 3 ops
- [ ] One failure/recovery story
- [ ] 3 tests (functional, race, edge)
- [ ] 10× scale mention"""))

    return items
