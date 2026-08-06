#!/usr/bin/env python3
"""Generate comprehensive LLD markdown docs for Databricks interview prep."""

from __future__ import annotations

from pathlib import Path

from _lld_expand import expand_doc

OUTPUT_DIR = Path(__file__).parent


def write_doc(filename: str, content: str) -> int:
    path = OUTPUT_DIR / filename
    expanded = expand_doc(filename, content)
    path.write_text(expanded, encoding="utf-8")
    return len(expanded.splitlines())


def main() -> None:
    # Import topic modules for registration side effects
    import _lld_topic_buffered_writer  # noqa: F401
    import _lld_topic_chat_deletion  # noqa: F401
    import _lld_topic_cidr_firewall  # noqa: F401
    import _lld_topic_durable_event_writer  # noqa: F401
    import _lld_topic_kv_race_repair  # noqa: F401
    import _lld_topic_kv_sliding_window_qps  # noqa: F401
    import _lld_topic_type_safe_kv  # noqa: F401
    from _lld_topics import ALL_BUILDERS

    for filename, builder in ALL_BUILDERS:
        lines = write_doc(filename, builder())
        print(f"{filename}: {lines} lines")


if __name__ == "__main__":
    main()
