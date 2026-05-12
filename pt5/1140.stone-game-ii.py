from __future__ import annotations

from functools import lru_cache
from typing import List


class Solution:
    def stoneGameII(self, piles: List[int]) -> int:
        n = len(piles)
        suffix = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            suffix[i] = suffix[i + 1] + piles[i]

        @lru_cache(None)
        def best_from(i: int, m: int) -> int:
            if i >= n:
                return 0
            if 2 * m >= n - i:
                return suffix[i]

            best = 0
            for x in range(1, 2 * m + 1):
                opponent = best_from(i + x, max(m, x))
                best = max(best, suffix[i] - opponent)
            return best

        return best_from(0, 1)

