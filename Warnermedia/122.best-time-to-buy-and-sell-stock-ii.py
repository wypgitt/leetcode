"""
Approach: Greedy accumulation of every profitable adjacent price move.
Data structure: one integer profit is enough because each decision only compares neighboring days.
Interview logic: unlimited transactions turn every upward edge into collectible profit; upward edges over a longer run telescope to peak - valley, while downward edges should be skipped.
Complexity: O(n) time, O(1) space.
Tests and edge cases: one day or descending prices returns 0; strictly increasing prices returns last - first.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        return sum(max(0, prices[i] - prices[i - 1]) for i in range(1, len(prices)))
# @lc code=end
