from __future__ import annotations

from typing import List


class Solution:
    def longestWPI(self, hours: List[int]) -> int:
        first_seen = {}
        score = 0
        best = 0

        for i, hour in enumerate(hours):
            score += 1 if hour > 8 else -1

            if score > 0:
                best = i + 1
            else:
                if score - 1 in first_seen:
                    best = max(best, i - first_seen[score - 1])

            first_seen.setdefault(score, i)

        return best

