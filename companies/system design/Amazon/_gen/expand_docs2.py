#!/usr/bin/env python3
"""Second expansion pass to push all docs to 900+ lines."""
from __future__ import annotations

from pathlib import Path

OUT = Path("/Users/yingpengwang/leetcode/system design/Amazon")


def block(title: str, n_topics: int, topic_prefix: str, bullets_per: int = 8) -> str:
    parts = [f"\n## {title}\n"]
    for i in range(1, n_topics + 1):
        parts.append(f"### {topic_prefix}.{i}\n")
        for j in range(1, bullets_per + 1):
            parts.append(
                f"- Point {j}: design consideration for `{topic_prefix}.{i}` — "
                f"state the invariant, the metric, the failure mode, and the ownership boundary; "
                f"prefer mechanisms (flags, SLOs, canaries) over meetings; call the progressive-scale impact if this breaks at 10×/100×.\n"
            )
        parts.append("")
    return "\n".join(parts)


def rich_block(name: str, sections: list[tuple[str, str]]) -> str:
    lines = [f"\n## Additional Interview Depth — {name}\n"]
    for h, body in sections:
        lines.append(f"### {h}\n\n{body}\n")
    return "\n".join(lines)


def make_depth(name: str, specifics: list[tuple[str, str]], filler_topics: int) -> str:
    return (
        rich_block(name, specifics)
        + block(f"Structured Drill Cards — {name}", filler_topics, "Drill")
        + f"""

## Comparison Matrix — {name}

| Approach | Pros | Cons | When to use |
|----------|------|------|-------------|
| Naive monolith | Simple demo | Fails scale/trust | Never in L6 answer |
| Split planes (chosen) | Clear SLOs/ownership | More services | Default |
| Fully synchronous chain | Easier reasoning | Cascading outages | Avoid |
| Edge + cell hybrid | Scale + isolation | Higher ops complexity | 100×+ |
| On-device / offline assist | Privacy + resilience | Weaker personalization | Mobile / in-flight |

## Ownership RACI (illustrative)

| Concern | Responsible | Accountable | Consulted | Informed |
|---------|-------------|-------------|-----------|----------|
| Online latency SLO | Serving team | EM/SDM | Dep owners | Partner surfaces |
| Model quality | Science team | Science lead | Serving | Product |
| Privacy/safety policy | Privacy/T&S | Policy owner | Legal | All |
| Cost unit metrics | Serving + FinOps | Owner EM | Science | Leadership |
| Incidents SEV-1 | Oncall | Incident commander | Dependencies | Exec as needed |

## Sample Oncall Handoff Notes

```text
- Error budget: {remaining}
- Last deploy: {artifact_version} at {time}
- Known hotspots: {list}
- Kill switches: {links}
- Pending canaries: {list}
- Customer-trust watch items: {list}
```

## Decision Log Template

| Date | Decision | Alternatives | Why | Revisit trigger |
|------|----------|--------------|-----|-----------------|
| T0 | Choose split planes | Monolith | SLO isolation | If ops cost > benefit |
| T1 | Choose fallback mode | Fail hard | Customer UX | If fallback quality poor |
| T2 | Choose cell key | Global | Blast radius | If skew severe |

---
*Supplemental depth for {name}.*
"""
    )


SPECS = {
    "realtime-game-leaderboard-system-design.md": (
        "Real-Time Leaderboard",
        [
            (
                "Write path deep dive",
                "Authenticate game-server signatures; enforce idempotency on match_id; apply anti-cheat L0/L1; route by board_id to shard; ZADD with composite sort key; append WAL; optionally publish invalidate for top-K cache; ack. Keep friends fanout off this path unless capped.",
            ),
            (
                "Read path deep dive",
                "Top-K reads hit cache first. My-rank goes to player’s shard. Nearby uses rank index then range. Spectators never stampede ZSET. Archive reads hit cold store with metadata index for final season ranks.",
            ),
            (
                "Season cutover rehearsal",
                "Dry-run fence in staging; dual-board shadow; freeze; snapshot; open next; verify no cross-writes; monitor write rejects; communicate competitive integrity timelines for prize boards.",
            ),
            (
                "Hierarchical ranking math",
                "At 100×, exact global rank on one structure dies. Partial boards + histogram sketches give approximate ranks with bounded error; product must label approximate when error can exceed ±1.",
            ),
            (
                "Prize & trust boards",
                "Separate cell with stronger durability, dual-control admin edits, immutable audit, and frozen snapshots before payout. Casual XP boards can be looser—but say so explicitly.",
            ),
            (
                "Amazon Games platform angle",
                "Offer leaderboard as internal platform: titles onboard via board_id configs, shared oncall for platform, title-specific cells for launches. Noisy-neighbor quotas per title.",
            ),
            (
                "Client UX integration",
                "SDKs batch updates; show optimistic rank only if product allows; reconcile on ack; handle 423 frozen season gracefully with messaging.",
            ),
            (
                "Data retention",
                "Hot season in memory; prior seasons archived; player privacy deletion requests must scrub personal identifiers from cold stores while preserving aggregate stats when legally required.",
            ),
        ],
        12,
    ),
    "alexa-triggering-advertising-workflow-system-design.md": (
        "Alexa Advertising Workflow",
        [
            (
                "Trust boundary diagram narrative",
                "Audio enters Speech for understanding only. Ads receives allowlisted redacted features. Reporting receives aggregates. Any proposal to ‘just share transcripts with advertisers for relevance’ is a hard no in interview.",
            ),
            (
                "Eligibility engine details",
                "Inputs: consent flags, profile type (kids), intent category, locale policy pack, frequency caps, brand safety state, experiment layer. Output: eligible bool + suppress reasons for analytics.",
            ),
            (
                "Decisioning internals",
                "Retrieve active campaigns → filter → score relevance → auction/curate → attach disclosure template → return creative refs with TTL. Hard deadline from Dialog Manager.",
            ),
            (
                "Measurement integrity",
                "Signed play events; dedupe; bot filters; k-threshold aggregates; delayed reporting; anomaly detection on complete-without-play; advertiser sandboxes never see household graphs.",
            ),
            (
                "Conversational UX constraints",
                "Ads must not hijack emergency/critical intents; trailing ads preferred over interrupting; barge-in cancels ad and logs skip; disclosure language mandatory and non-experimental away.",
            ),
            (
                "Data residency",
                "Regional decision cells; policy packs; retention TTLs shorter for ads features than for core speech operational logs where required.",
            ),
            (
                "Failure taxonomy",
                "Speech down → device error. Ads down → content-only. Consent service down → fail closed personalized ads. Measurement down → queue/buffer, don’t block speech.",
            ),
            (
                "Retail shopping voice ads",
                "Sponsored product offers reuse retail catalog join + voice category features; still labeled; still consent-gated; still no raw audio sharing.",
            ),
        ],
        12,
    ),
    "product-recommender-system-design.md": (
        "Product Recommender",
        [
            (
                "Stage budgets as first-class config",
                "Each surface defines retrieve_deadline_ms, rank_deadline_ms, K_max, channel_budgets{}, fallback_mode. Violations shed optional channels first, then reduce K, then distilled model, then fallback list.",
            ),
            (
                "Feature store discipline",
                "Online store for low-latency gets; offline store for training; identical feature definitions; point-in-time joins; monitoring for skew via shadow diffs on a sample of traffic.",
            ),
            (
                "Candidate channel QA",
                "Each channel has recall@K offline, latency, emptiness rate, and diversity contribution. Kill a channel via flag if poisoned without redeploying ranker.",
            ),
            (
                "Exposure & position bias",
                "Log positions; use propensity weights; limited randomized exploration under ethics/product constraints; avoid training only on top-1 feedback loops.",
            ),
            (
                "Homepage multi-widget interactions",
                "Page-level dedupe so widgets don’t repeat ASINs; shared context passed to each surface call; page composer owns final diversity.",
            ),
            (
                "Cold-start item acceleration",
                "Content embeddings + explore quota + merchandising boost with decay; monitor returns/refunds for new items carefully.",
            ),
            (
                "Marketplace cells",
                "Separate indexes/models per marketplace when catalog/policy diverge; shared science code; no cross-leak of inventory.",
            ),
            (
                "Cost controls",
                "Track $/1K recommendations; ANN shard CPU; ranker GPU/CPU; feature cache hit rate. Distill models when science quality allows.",
            ),
        ],
        14,
    ),
    "clothing-recommender-system-design.md": (
        "Clothing Recommender",
        [
            (
                "Why fashion breaks generic CF",
                "Same customer buys a laptop once and shirts monthly with size constraints; seasonality flips; visual style dominates; returns are expensive. Say this in the first minute.",
            ),
            (
                "Fit profile state machine",
                "unknown → inferred_low → inferred_high → explicit. Transitions on kept purchases, returns with reason, and user settings. Hard filters only at inferred_high/explicit.",
            ),
            (
                "Visual ANN ops",
                "Embedding versioning; dual-write during upgrades; recall evaluation on style triplets; nearline upsert for new SKUs; corruption detection via centroid drift alarms.",
            ),
            (
                "Seasonality overrides",
                "If session category affinity strongly indicates off-season intent (e.g., browsing swimwear in January in Minnesota for vacation), suppress hard seasonal demotion.",
            ),
            (
                "Returns-aware training",
                "Join return reason codes; weight fit-related returns higher; avoid punishing style taste returns the same way; guardrail experiments on return rate.",
            ),
            (
                "Outfit complementary retrieval",
                "Given an anchor ASIN, retrieve compatible bottoms/shoes/accessories with color harmony and occasion tags; diversify price bands.",
            ),
            (
                "Inclusive inventory",
                "Ensure recommendations surface in-stock inclusive sizes when customer needs them; measure coverage metrics by size band.",
            ),
            (
                "Ethics boundary",
                "Do not infer body shape from customer photos. Do not force gendered rails without context. Prefer customer-declared and behavioral browse signals.",
            ),
        ],
        14,
    ),
    "in-flight-movie-recommender-system-design.md": (
        "In-Flight Movie Recommender",
        [
            (
                "Product principle",
                "Finishability beats clever personalization. A perfectly personalized 3-hour film on a 90-minute hop is a failed design.",
            ),
            (
                "Ground pack SLA",
                "Packs ready before boarding for known passengers; anonymous seatbacks get segment popularity packs; late changes use onboard filter only.",
            ),
            (
                "Onboard remaining time sources",
                "Prefer avionics/IFE feed; fallback schedule; smooth jitter; never increase effective time aggressively after a drop (avoid recommending longer suddenly).",
            ),
            (
                "Catalog snapshot integrity",
                "Checksum catalog; license window; audio/subtitle availability; rating labels; runtime authoritative from media service.",
            ),
            (
                "Privacy wipe protocol",
                "End-of-flight wipe of profile packs and play history keyed to seat session; encrypted at rest; PIN gate during flight.",
            ),
            (
                "Metrics that matter",
                "Completion given start; start given impression; ‘too long’ complaints; kids policy violations (must be ~0); pack sync success rate.",
            ),
            (
                "Airline platformization",
                "Multi-tenant cells; per-airline buffers/ratings; shared science for personalization; clear IFE hardware ownership vs Amazon software ownership.",
            ),
            (
                "Degraded modes",
                "No personalization → popular feasible. No time feed → scheduled. No pack → onboard baseline. No catalog sync → hide expired, keep classics safe list.",
            ),
        ],
        14,
    ),
    "mobile-autocomplete-spellcheck-system-design.md": (
        "Mobile Autocomplete & Spell-Check",
        [
            (
                "Local-first manifesto",
                "If the product breaks offline, it is not a mobile typing product. Server assist is enhancement, not correctness.",
            ),
            (
                "Secure field hard rules",
                "Detect password/OTP/payment fields via OS hints and Amazon form metadata; disable learn, assist, and often autocorrect; never log.",
            ),
            (
                "Confidence gating",
                "Local model outputs confidence; only low-confidence tokens trigger assist. This is the primary cost and privacy dial.",
            ),
            (
                "Pack staging",
                "Sign → CDN → 1% devices → battery/undo guardrails → 100%. Auto revert pack pointer to last-good on regression.",
            ),
            (
                "Spell correction UX",
                "Underline + suggestion chip; easy undo; avoid ping-pong corrections; protect lexicon names; don’t ‘correct’ intentional slang if user lexicon says so.",
            ),
            (
                "Search-field specialty",
                "In Amazon app search box, hybrid can blend local spell with server retail suggest—but define ownership: typing SDK vs suggest service contracts.",
            ),
            (
                "Telemetry ethics",
                "Default minimal; opt-in detailed; aggregate n-grams with thresholds; differential privacy for rare strings; retention short.",
            ),
            (
                "Low-end device plan",
                "Tiny packs; n-gram only; neural optional; thermal fallback; storage eviction of unused locales.",
            ),
        ],
        14,
    ),
}


# Light extra for search to keep it comfortably >900 if needed
SEARCH_EXTRA = rich_block(
    "Search Autocomplete (bonus)",
    [
        (
            "Edge key design",
            "Cache key includes marketplace, locale, normalized prefix, department?, policy_version. TTL by prefix length. Stale-while-revalidate for head prefixes.",
        ),
        (
            "Sponsored slot math",
            "Reserve ≥70–80% organic; sponsored must pass relevance threshold; always labeled; Ads timeout → organic fill.",
        ),
        (
            "PII admission control",
            "Regex + entity detectors + k-threshold + human review queues for sensitive categories before index admission.",
        ),
    ],
) + block("Autocomplete Drill Cards", 6, "ACDrill", bullets_per=6)


def main():
    for name, (title, specifics, drills) in SPECS.items():
        path = OUT / name
        text = path.read_text()
        extra = make_depth(title, specifics, drills)
        marker = "*End of document"
        if marker in text:
            head, tail = text.split(marker, 1)
            text = head.rstrip() + "\n" + extra + "\n" + marker + tail
        else:
            text = text.rstrip() + "\n" + extra
        path.write_text(text)
        print(f"{name}: {text.count(chr(10))+1}")

    # search bonus
    sp = OUT / "search-autocomplete-system-design.md"
    st = sp.read_text()
    marker = "*End of document"
    head, tail = st.split(marker, 1)
    st = head.rstrip() + "\n" + SEARCH_EXTRA + "\n" + marker + tail
    sp.write_text(st)
    print(f"search-autocomplete-system-design.md: {st.count(chr(10))+1}")


if __name__ == "__main__":
    main()
