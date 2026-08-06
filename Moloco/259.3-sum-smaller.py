"""
Approach: Sort, then fix the first number and use two pointers for the remaining pair.
Data structure: sorting enables pointer movement and counting many pairs at once.
Interview logic: with nums[i] fixed, if nums[i] + nums[left] + nums[right] < target, then every index from left+1 through right also works with left because the array is sorted. Count right-left pairs and move left.
Complexity: O(n^2) time, O(1) extra space excluding sort implementation details.
Tests and edge cases: fewer than three numbers returns 0; negative numbers work after sorting; duplicate values are counted by index combinations.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def threeSumSmaller(self, nums: List[int], target: int) -> int:
        nums.sort()
        count = 0
        for i in range(len(nums) - 2):
            left, right = i + 1, len(nums) - 1
            while left < right:
                if nums[i] + nums[left] + nums[right] < target:
                    count += right - left
                    left += 1
                else:
                    right -= 1
        return count
# @lc code=end
