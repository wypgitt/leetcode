from __future__ import annotations

from typing import List


class Solution:
    def kConcatenationMaxSum(self, arr: List[int], k: int) -> int:
        mod = 10**9 + 7

        def kadane(values: List[int]) -> int:
            best = 0
            current = 0
            for value in values:
                current = max(0, current + value)
                best = max(best, current)
            return best

        if k == 1:
            return kadane(arr) % mod

        best_two = kadane(arr * 2)
        total = sum(arr)
        if total > 0:
            best_two += (k - 2) * total

        return best_two % mod

