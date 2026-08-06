"""
Approach: Put all numbers in a hash set and only start counting from numbers whose predecessor is absent.
Data structure: the set gives O(1) average membership checks, which avoids sorting.
Interview logic: each consecutive run is explored once from its smallest value, so the total number of inner-loop advances across the whole algorithm is linear.
Complexity: O(n) average time, O(n) space.
Tests and edge cases: empty input returns 0; duplicates collapse in the set; negative values work normally.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def longestConsecutive(self, nums: List[int]) -> int:
        values = set(nums)
        best = 0
        for num in values:
            if num - 1 in values:
                continue
            length = 1
            while num + length in values:
                length += 1
            best = max(best, length)
        return best
# @lc code=end
