"""
Approach: Sliding window for positive numbers.
Data structure: two pointers and a running sum represent the current window.
Interview logic: because all numbers are positive, expanding right only increases the sum and moving left only decreases it. Once the sum reaches target, shrink left greedily to find the shortest valid window ending at right.
Complexity: O(n) time, O(1) space.
Tests and edge cases: no valid subarray returns 0; one element can satisfy target; large target may require the whole array.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        left = total = 0
        best = len(nums) + 1
        for right, num in enumerate(nums):
            total += num
            while total >= target:
                best = min(best, right - left + 1)
                total -= nums[left]
                left += 1
        return 0 if best == len(nums) + 1 else best
# @lc code=end
