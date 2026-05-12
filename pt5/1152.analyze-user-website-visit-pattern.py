from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations
from typing import DefaultDict, List, Tuple


class Solution:
    def mostVisitedPattern(
        self, username: List[str], timestamp: List[int], website: List[str]
    ) -> List[str]:
        visits: DefaultDict[str, List[str]] = defaultdict(list)
        for time, user, site in sorted(zip(timestamp, username, website)):
            visits[user].append(site)

        pattern_count: Counter[Tuple[str, str, str]] = Counter()
        for sites in visits.values():
            unique_patterns = set(combinations(sites, 3))
            pattern_count.update(unique_patterns)

        if not pattern_count:
            return []

        best_pattern = min(
            pattern_count,
            key=lambda pattern: (-pattern_count[pattern], pattern),
        )
        return list(best_pattern)
