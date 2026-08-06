"""
Approach: Binary search on the slope between mid and mid + 1.
Data structure: two index bounds are enough because the virtual boundaries are negative infinity.
Interview logic: if nums[mid] < nums[mid+1], a peak must exist to the right on the rising side. Otherwise, a peak exists at mid or to the left.
Complexity: O(log n) time, O(1) space.
Tests and edge cases: one element returns 0; peak at either boundary; multiple peaks allow any valid index.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def findPeakElement(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1
        while left < right:
            mid = (left + right) // 2
            if nums[mid] < nums[mid + 1]:
                left = mid + 1
            else:
                right = mid
        return left
# @lc code=end
