"""Shared helpers for Databricks doc generation (no filler appendix)."""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent

# Intentionally empty — quality rewrite forbids Appendix X padding
APPENDIX_X = ""


def write(name: str, body: str) -> int:
    path = OUT / name
    path.write_text(body)
    return body.count("\n")
