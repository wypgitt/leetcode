"""
Approach: Find the common binary prefix of left and right.
Data structure: scalar shifts only.
Interview logic: any bit that changes somewhere in [left,right] will be zero in the AND. Repeatedly shift both endpoints right until equal, then shift the common prefix back.
Complexity: O(log right) time, O(1) space.
Tests and edge cases: left == right returns left; ranges crossing a power of two often return 0; large ranges remain fast.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def rangeBitwiseAnd(self, left: int, right: int) -> int:
        shift = 0
        while left < right:
            left >>= 1
            right >>= 1
            shift += 1
        return left << shift
# @lc code=end
