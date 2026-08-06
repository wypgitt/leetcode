"""
Approach: Two pointers from both ends of the sorted array.
Data structure: indexes only; sorted order replaces a hash table.
Interview logic: if the sum is too small, increasing the left pointer is the only way to make it larger. If too large, decreasing the right pointer is the only way to make it smaller.
Complexity: O(n) time, O(1) space.
Tests and edge cases: exactly one solution; negative numbers; answer indices are 1-based.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        left, right = 0, len(numbers) - 1
        while left < right:
            total = numbers[left] + numbers[right]
            if total == target:
                return [left + 1, right + 1]
            if total < target:
                left += 1
            else:
                right -= 1
        return []
# @lc code=end
