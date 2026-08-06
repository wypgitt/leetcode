# Fundamentals Doc Style Guide

Mirror `/Users/yingpengwang/leetcode/system design/OpenAI/openai-playground-system-design.md` and Amazon pastebin docs.

Every file MUST include these sections (use exact TOC numbering):

1. Clarify Requirements (Interview Q&A)
   - 1.0 What this is / is not (table)
   - 1.1 Functional requirements — table of Question | Expected interviewer answer | Design implication (8–15 rows)
   - MVP scope bullets + Out of MVP bullets
   - 1.2 Non-functional requirements — latency, availability, durability, consistency, multi-region, security, cost
   - 1.3 Cases — happy paths + edge/failure table
   - 1.4 Scales — Baseline / 10× / 100× / 1,000× metrics table + what each jump forces
   - 1.5 Etc. constraints + scope repeat-back quote
2. Back-of-the-Envelope Estimation — concrete math (QPS, storage, bandwidth, memory, cache, hot keys)
3. High-Level Design — components, APIs, data model, why choose A over B, trade-offs, deal-breakers
4. Architecture Diagram — mermaid flowchart/C4-ish
5. Design Deep Dive
   - 5.1 Reliability (data loss prevention, retries, idempotency, rate limits, backpressure)
   - 5.2 Scalability (scale up/down, sharding, storage tiers, parallelization)
   - 5.3 Maintainability (ops, observability, migrations, multi-tenant)
6. Wrap-Up — decision summary, phased rollout
7. Deeper / Related Interview Questions — 15–30 traps with strong answers (tradeoffs, memory, storage, indexing, LB, consistent hashing, algorithms, DS)

Quality bar:
- Interview-passable for senior / staff loops
- Domain-specific numbers and failure modes (not generic fluff)
- Explicit trade-off tables where choices matter
- Progressive scale jumps that change architecture
- Target **550–900 lines** of substantive markdown per problem
- Filename: `{slug}-system-design.md` under Fundamentals/
- Title: `# System Design: {Title}`
- Focus areas blurb under title
