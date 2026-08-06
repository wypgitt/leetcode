"""
Approach: Dynamic programming with include/exclude states compressed to two integers.
Data structure: prev2 is best up to i-2 and prev1 is best up to i-1, enough to decide house i.
Interview logic: for each house, either skip it and keep prev1, or rob it and add its money to prev2. Take the better choice.
Complexity: O(n) time, O(1) space.
Tests and edge cases: empty list returns 0; one house returns its value; adjacent high values cannot both be taken.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def rob(self, nums: List[int]) -> int:
        prev2 = prev1 = 0
        for num in nums:
            prev2, prev1 = prev1, max(prev1, prev2 + num)
        return prev1
# @lc code=end
