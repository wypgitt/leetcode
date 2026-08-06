#!/usr/bin/env python3
"""Generate comprehensive LLD markdown docs for Databricks interview prep."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

OUTPUT_DIR = Path(__file__).parent


def header(title: str, focus: str, quality: str) -> str:
    return f"""# LLD: {title}

> **Focus areas:** {focus}
> **Style:** LLD interview (clarify → complexity → classes → algorithms/pseudocode → concurrency → failure modes → tests → Q&A)
> **Quality bar:** {quality}
> **Interview theme:** Databricks — signature storage/concurrency LLD

---

## Table of Contents

1. [Clarify Requirements (Interview Q&A)](#1-clarify-requirements-interview-qa)
2. [APIs & Guarantees](#2-apis--guarantees)
3. [Class Diagrams & Responsibilities](#3-class-diagrams--responsibilities)
4. [Core Data Structures & Algorithms](#4-core-data-structures--algorithms)
5. [Concurrency Invariants](#5-concurrency-invariants)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Failure Modes & Recovery](#7-failure-modes--recovery)
8. [Tests & Edge Cases](#8-tests--edge-cases)
9. [Scalability Notes (Still Single-Node)](#9-scalability-notes-still-single-node)
10. [Wrap-Up](#10-wrap-up)
11. [Deeper / Related Interview Questions](#11-deeper--related-interview-questions)
12. [Appendices](#12-appendices)

---"""


def section_1(goal: str, what_is: str, fr_rows: list[tuple], mvp: list[str], scope: str, invariant: str) -> str:
    fr_table = "\n".join(
        f"| F{i} | {q} | {a} | {imp} |" for i, (q, a, imp) in enumerate(fr_rows, 1)
    )
    mvp_lines = "\n".join(f"{i}. {item}" for i, item in enumerate(mvp, 1))
    return f"""
## 1. Clarify Requirements (Interview Q&A)

Goal: {goal}

### 1.0 What this is / is not

| Dimension | This | Not |
|-----------|------|-----|
{what_is}

### 1.1 Clarifying questions

| # | Question | Typical answer | Implication |
|---|----------|----------------|-------------|
{fr_table}

**MVP scope:**

{mvp_lines}

**Out of MVP:** Distributed replication; full production framework clone.

### 1.2 Scope repeat-back

> {scope}

### 1.3 Core invariant (lock early)

```text
{invariant}
```

---"""


def section_2(api: str, guarantees: list[tuple], errors: str) -> str:
    g_table = "\n".join(f"| {p} | {g} |" for p, g in guarantees)
    return f"""
## 2. APIs & Guarantees

### 2.1 Public API

```text
{api}
```

### 2.2 Guarantees table

| Property | Guarantee |
|----------|-----------|
{g_table}

### 2.3 Error model

```text
{errors}
```

---"""


def section_3(classes: list[tuple], diagram: str) -> str:
    c_table = "\n".join(f"| `{name}` | {role} |" for name, role in classes)
    return f"""
## 3. Class Diagrams & Responsibilities

### 3.1 Responsibility table

| Class | Responsibility |
|-------|----------------|
{c_table}

### 3.2 ASCII class diagram

```text
{diagram}
```

---"""


def section_4(content: str) -> str:
    return f"""
## 4. Core Data Structures & Algorithms

{content}

---"""


def section_5(shared: str, invariants: list[str], lock_order: str) -> str:
    inv_table = "\n".join(f"| I{i} | {inv} |" for i, inv in enumerate(invariants, 1))
    return f"""
## 5. Concurrency Invariants

### 5.1 Shared state

{shared}

### 5.2 Lock order (mandatory)

```text
{lock_order}
```

### 5.3 Invariants table

| # | Invariant |
|---|-----------|
{inv_table}

---"""


def section_6(blocks: list[tuple[str, str]]) -> str:
    parts = ["## 6. Algorithms & Pseudocode\n"]
    for i, (title, code) in enumerate(blocks, 1):
        parts.append(f"### 6.{i} {title}\n\n```text\n{code}\n```\n")
    parts.append("---")
    return "\n".join(parts)


def section_7(rows: list[tuple], extra: str = "") -> str:
    table = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in rows)
    return f"""
## 7. Failure Modes & Recovery

| Scenario | On failure | After recovery / mitigation |
|----------|------------|----------------------------|
{table}

{extra}

---"""


def section_8(functional: list[str], concurrency: list[str], crash: list[str] | None = None) -> str:
    func = "\n".join(f"{i}. {t}" for i, t in enumerate(functional, 1))
    conc = "\n".join(f"- {t}" for t in concurrency)
    crash_block = ""
    if crash:
        crash_block = "\n### 8.3 Crash / durability tests\n\n" + "\n".join(
            f"| {a} | {b} | {c} |" for a, b, c in crash
        )
        crash_block = f"\n{crash_block}\n"
    return f"""
## 8. Tests & Edge Cases

### 8.1 Functional tests

{func}

### 8.2 Concurrency tests

{conc}
{crash_block}
### 8.4 Property / invariant checks

```text
Run under ThreadSanitizer; assert documented invariants after join.
Stress: many threads, random keys, bounded runtime — no deadlock, no corruption.
```

---"""


def section_9(content: str) -> str:
    return f"""
## 9. Scalability Notes (Still Single-Node)

{content}

---"""


def section_10(summary: list[str], mvp_later: list[tuple], risks: list[str]) -> str:
    s = "\n".join(f"- {x}" for x in summary)
    ml = "\n".join(f"| {m} | {l} |" for m, l in mvp_later)
    r = "\n".join(f"{i}. {x}" for i, x in enumerate(risks, 1))
    return f"""
## 10. Wrap-Up

**Design summary**

{s}

**MVP vs later**

| MVP | Later |
|-----|-------|
{ml}

**Top risks**

{r}

---"""


def section_11(questions: list[str], traps: list[tuple]) -> str:
    qs = "\n".join(f"{i}. {q}" for i, q in enumerate(questions, 1))
    tt = "\n".join(f"| {t} | {a} |" for t, a in traps)
    return f"""
## 11. Deeper / Related Interview Questions

{qs}

**Interviewer traps**

| Trap | Strong answer |
|------|---------------|
{tt}

---"""


def section_12(appendices: list[tuple[str, str]]) -> str:
    parts = ["## 12. Appendices\n"]
    for label, body in appendices:
        parts.append(f"### {label}\n\n{body}\n")
    parts.append("\n---\n\n*End of LLD prep.*")
    return "\n".join(parts)


def build_doc(parts: list[str]) -> str:
    return "\n".join(parts)

