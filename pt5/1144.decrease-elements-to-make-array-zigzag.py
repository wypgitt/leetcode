from __future__ import annotations

from typing import List


class Solution:
    def movesToMakeZigzag(self, nums: List[int]) -> int:
        n = len(nums)

        def cost_for_valleys(parity: int) -> int:
            moves = 0
            for i, value in enumerate(nums):
                if i % 2 != parity:
                    continue
                left = nums[i - 1] if i > 0 else float("inf")
                right = nums[i + 1] if i + 1 < n else float("inf")
                allowed = min(left, right) - 1
                if value > allowed:
                    moves += value - allowed
            return moves

        return min(cost_for_valleys(0), cost_for_valleys(1))

