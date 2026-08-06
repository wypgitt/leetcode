#!/usr/bin/env python3
"""Generate 15 senior/staff Fundamentals system-design docs (overwrite)."""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent


def header(title: str, focus: str, theme: str) -> str:
    return f"""# System Design: {title}

> **Focus areas:** {focus}
> **Style:** End-to-end product design with progressive scale (10× → 100× → 1,000×)
> **Quality bar:** Domain-specific numbers and failure modes; explicit trade-offs; deal-breakers called out
> **Interview theme:** Senior / Staff — **{theme}**

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [Back-of-the-Envelope Estimation](#2-back-of-the-envelope-estimation)
3. [High-Level Design](#3-high-level-design)
4. [Architecture Diagram](#4-architecture-diagram)
5. [Design Deep Dive](#5-design-deep-dive)
6. [Wrap-Up](#6-wrap-up)
7. [Deeper / Related Interview Questions](#7-deeper--related-interview-questions)
8. [Appendices](#8-appendices)

---
"""


def write(name: str, content: str) -> None:
    path = OUT / name
    path.write_text(content if content.endswith("\n") else content + "\n", encoding="utf-8")
    lines = content.count("\n") + (0 if content.endswith("\n") else 1)
    print(f"{name}\t{lines}")


def s1(
    goal: str,
    is_is_not: list[tuple[str, str, str]],
    functional: list[tuple[str, str, str]],
    mvp: list[str],
    out_mvp: list[str],
    nfr: list[tuple[str, str, str]],
    happy: list[str],
    cases: list[tuple[str, str]],
    scales: list[tuple[str, str, str, str, str]],
    jumps: str,
    constraints: list[str],
    scope: str,
) -> str:
    rows_iin = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in is_is_not)
    rows_f = "\n".join(
        f"| F{i} | {q} | {a} | {d} |" for i, (q, a, d) in enumerate(functional, 1)
    )
    mvp_b = "\n".join(f"{i}. {x}" for i, x in enumerate(mvp, 1))
    out_b = "\n".join(f"- {x}" for x in out_mvp)
    rows_n = "\n".join(f"| N{i} | {a} | {b} | {c} |" for i, (a, b, c) in enumerate(nfr, 1))
    happy_b = "\n".join(f"{i}. {x}" for i, x in enumerate(happy, 1))
    rows_c = "\n".join(f"| {a} | {b} |" for a, b in cases)
    rows_s = "\n".join(f"| {a} | {b} | {c} | {d} | {e} |" for a, b, c, d, e in scales)
    cons = "\n".join(f"- {x}" for x in constraints)
    return f"""## 1. Clarify Requirements (Interview Q&A)

Goal: {goal}

### 1.0 What this is / is not

| Dimension | This design | Not this |
|-----------|-------------|----------|
{rows_iin}

### 1.1 Functional Requirements

| # | Question to ask | Expected / typical interviewer answer | Design implication |
|---|-----------------|----------------------------------------|--------------------|
{rows_f}

**MVP functional scope (lock with interviewer):**

{mvp_b}

**Out of MVP (explicitly defer):**

{out_b}

### 1.2 Non-Functional Requirements

| # | Area | Target | Notes |
|---|------|--------|-------|
{rows_n}

### 1.3 Cases (User Flows & Edge Cases)

**Happy paths**

{happy_b}

**Edge / failure cases**

| Case | Behavior |
|------|----------|
{rows_c}

### 1.4 Scales (Progressive)

| Metric | Baseline | 10× | 100× | 1,000× |
|--------|----------|-----|------|--------|
{rows_s}

**What each jump forces architecturally:**

{jumps}

### 1.5 Etc. (Constraints & Assumptions)

{cons}

**Scope statement to repeat back:**

> {scope}

---
"""


def s2(blocks: list[tuple[str, str]], bottleneck: str) -> str:
    parts = ["## 2. Back-of-the-Envelope Estimation\n"]
    for i, (title, body) in enumerate(blocks, 1):
        parts.append(f"### 2.{i} {title}\n\n```text\n{body.strip()}\n```\n")
    parts.append(f"### 2.N Bottleneck ranking\n\n{bottleneck.strip()}\n\n---\n")
    return "\n".join(parts)


def s3(
    overview: str,
    components: list[str],
    apis: str,
    data_model: str,
    tradeoffs: list[tuple[str, str, str, str]],
    dealbreakers: list[tuple[str, str]],
    why: str,
) -> str:
    comps = "\n".join(f"{i}. **{c}**" for i, c in enumerate(components, 1))
    rows_t = "\n".join(f"| {a} | {b} | {c} | {d} |" for a, b, c, d in tradeoffs)
    rows_d = "\n".join(f"| {a} | {b} |" for a, b in dealbreakers)
    return f"""## 3. High-Level Design

### 3.1 Overview

{overview.strip()}

### 3.2 Components

{comps}

### 3.3 APIs (sketch)

```text
{apis.strip()}
```

### 3.4 Data model (core)

```text
{data_model.strip()}
```

### 3.5 Why choose A over B (trade-offs)

| Decision | Option A | Option B | Choose / when |
|----------|----------|----------|---------------|
{rows_t}

**Why this shape:** {why}

### 3.6 Deal-breakers

| Temptation | Why it fails |
|------------|--------------|
{rows_d}

---
"""


def s4(mermaid: str, sequences: list[tuple[str, str]]) -> str:
    parts = [
        "## 4. Architecture Diagram\n",
        "### 4.1 C4-ish / flow\n",
        "```mermaid\n" + mermaid.strip() + "\n```\n",
    ]
    for i, (title, body) in enumerate(sequences, 1):
        parts.append(f"### 4.{i+1} {title}\n\n```text\n{body.strip()}\n```\n")
    parts.append("---\n")
    return "\n".join(parts)


def s5(
    reliability: list[str],
    scalability: list[tuple[str, str]],
    maintainability: list[str],
    deep_dives: list[tuple[str, str]],
) -> str:
    rel = "\n".join(f"{i}. {x}" for i, x in enumerate(reliability, 1))
    rows_s = "\n".join(f"| {a} | {b} |" for a, b in scalability)
    maint = "\n".join(f"- {x}" for x in maintainability)
    parts = [
        "## 5. Design Deep Dive\n",
        "### 5.1 Reliability (data loss prevention, retries, idempotency, rate limits, backpressure)\n\n",
        rel + "\n",
        "\n### 5.2 Scalability (scale up/down, sharding, storage tiers, parallelization)\n\n",
        "| Scale | Architecture moves |\n|-------|--------------------|\n" + rows_s + "\n",
        "\n### 5.3 Maintainability (ops, observability, migrations, multi-tenant)\n\n",
        maint + "\n",
    ]
    for i, (title, body) in enumerate(deep_dives, 4):
        parts.append(f"\n### 5.{i} {title}\n\n{body.strip()}\n")
    parts.append("\n---\n")
    return "".join(parts)


def s6(
    designed: str,
    decisions: list[str],
    risks: list[str],
    plan: list[tuple[str, str]],
    closer: str,
) -> str:
    dec = "\n".join(f"{i}. {x}" for i, x in enumerate(decisions, 1))
    risk = "\n".join(f"- {x}" for x in risks)
    rows = "\n".join(f"| {a} | {b} |" for a, b in plan)
    return f"""## 6. Wrap-Up

### 6.1 Designed

{designed}

### 6.2 Decisions to defend

{dec}

### 6.3 Risks

{risk}

### 6.4 45-minute interview plan

| Min | Focus |
|-----|-------|
{rows}

### 6.5 Closer

> {closer}

---
"""


def s7(qs: list[tuple[str, str]]) -> str:
    parts = ["## 7. Deeper / Related Interview Questions\n"]
    for i, (q, a) in enumerate(qs, 1):
        parts.append(f"### Q{i}. {q}\n\n{a.strip()}\n")
    parts.append("---\n")
    return "\n".join(parts)


def s8(extras: list[tuple[str, str]], checklist: list[str]) -> str:
    parts = ["## 8. Appendices\n"]
    for i, (title, body) in enumerate(extras, 1):
        parts.append(f"### A{i}. {title}\n\n{body.strip()}\n")
    checks = "\n".join(f"- [ ] {c}" for c in checklist)
    parts.append(f"\n### A-Z. Interview checklist\n\n{checks}\n\n---\n\n*End of doc — senior/staff system design prep.*\n")
    return "\n".join(parts)


# =============================================================================
# Import doc bodies from companion modules to keep this file maintainable
# =============================================================================
if __name__ == "__main__":
    from _gen_senior15_docs import ALL_DOCS  # noqa: E402

    for name, builder in ALL_DOCS:
        content = builder()
        write(name, content)
    print("done", len(ALL_DOCS))
