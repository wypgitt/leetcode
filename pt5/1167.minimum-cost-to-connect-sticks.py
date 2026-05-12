from __future__ import annotations

import heapq
from typing import List


class Solution:
    def connectSticks(self, sticks: List[int]) -> int:
        heapq.heapify(sticks)
        total = 0

        while len(sticks) > 1:
            first = heapq.heappop(sticks)
            second = heapq.heappop(sticks)
            merged = first + second
            total += merged
            heapq.heappush(sticks, merged)

        return total

