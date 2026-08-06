"""
Approach: Reduce the circular street to two linear House Robber runs.
Data structure: two scalar DP states per linear run are enough: best up to i-2 and best up to i-1.
Interview logic: the first and last houses are adjacent, so any valid optimal plan excludes at least one of them. Compute the best plan excluding the last house and the best plan excluding the first house, then take the maximum.
Complexity: O(n) time, O(1) space.
Tests and edge cases: one house returns its value; two houses returns max; arrays where the best linear answer would take both ends are corrected by the two-case split.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def rob(self, nums: List[int]) -> int:
        if len(nums) == 1:
            return nums[0]
        def rob_line(arr: List[int]) -> int:
            prev2 = prev1 = 0
            for num in arr:
                prev2, prev1 = prev1, max(prev1, prev2 + num)
            return prev1
        return max(rob_line(nums[:-1]), rob_line(nums[1:]))
# @lc code=end
