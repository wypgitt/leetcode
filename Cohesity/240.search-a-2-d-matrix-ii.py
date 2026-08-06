"""
Approach: Start from the top-right corner and eliminate one row or column each step.
Data structure: row and column indexes only; matrix sortedness supplies direction.
Interview logic: at top-right, values to the left are smaller and values below are larger. If current is too large, move left; if too small, move down.
Complexity: O(m + n) time, O(1) space.
Tests and edge cases: empty matrix returns False; target smaller/larger than all elements; target on boundaries.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        r, c = 0, len(matrix[0]) - 1
        while r < len(matrix) and c >= 0:
            if matrix[r][c] == target:
                return True
            if matrix[r][c] > target:
                c -= 1
            else:
                r += 1
        return False
# @lc code=end
