from __future__ import annotations

from bisect import bisect_left
from typing import List


class Solution:
    def shortestDistanceColor(self, colors: List[int], queries: List[List[int]]) -> List[int]:
        positions = {1: [], 2: [], 3: []}
        for index, color in enumerate(colors):
            positions[color].append(index)

        answer = []
        for index, color in queries:
            color_positions = positions[color]
            if not color_positions:
                answer.append(-1)
                continue

            insert_at = bisect_left(color_positions, index)
            best = float("inf")
            if insert_at < len(color_positions):
                best = min(best, color_positions[insert_at] - index)
            if insert_at > 0:
                best = min(best, index - color_positions[insert_at - 1])
            answer.append(best)

        return answer

