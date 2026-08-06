"""
Approach: Binary search comparing the middle value with the right endpoint.
Data structure: index bounds only; the rotated sorted invariant supplies the ordering information.
Interview logic: if nums[mid] > nums[right], mid is in the high left segment and the minimum is right of mid. Otherwise, the minimum is at mid or left of it.
Complexity: O(log n) time, O(1) space.
Tests and edge cases: unrotated array; one element; pivot near the beginning or end.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def findMin(self, nums: List[int]) -> int:
        left, right = 0, len(nums) - 1
        while left < right:
            mid = (left + right) // 2
            if nums[mid] > nums[right]:
                left = mid + 1
            else:
                right = mid
        return nums[left]
# @lc code=end
