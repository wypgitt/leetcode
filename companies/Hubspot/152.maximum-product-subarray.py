"""
Approach: Kadane-style DP tracking both max and min product ending at the current index.
Data structure: two scalar states are enough because only subarrays ending at the previous element can extend to the current element.
Interview logic: a negative number swaps the role of previous maximum and minimum. Zero naturally resets because starting fresh at num is always considered.
Complexity: O(n) time, O(1) space.
Tests and edge cases: one element; zeros between segments; even vs odd count of negative values.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def maxProduct(self, nums: List[int]) -> int:
        cur_max = cur_min = ans = nums[0]
        for num in nums[1:]:
            if num < 0:
                cur_max, cur_min = cur_min, cur_max
            cur_max = max(num, cur_max * num)
            cur_min = min(num, cur_min * num)
            ans = max(ans, cur_max)
        return ans
# @lc code=end
