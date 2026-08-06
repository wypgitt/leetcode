"""
Approach: Dynamic programming where dp[j] is the largest square side ending at the current row and column j-1.
Data structure: one DP row plus a diagonal variable compresses the classic 2D table to O(cols) space.
Interview logic: a '1' cell can extend a square only if its top, left, and top-left neighbors can support it. The side length is 1 + min(those three sides).
Complexity: O(mn) time, O(n) space.
Tests and edge cases: empty matrix returns 0; all zeros returns 0; all ones returns min(rows, cols)^2.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def maximalSquare(self, matrix: List[List[str]]) -> int:
        if not matrix or not matrix[0]:
            return 0
        cols = len(matrix[0])
        dp = [0] * (cols + 1)
        best = 0
        for row in matrix:
            prev_diag = 0
            for j in range(1, cols + 1):
                top = dp[j]
                if row[j - 1] == '1':
                    dp[j] = 1 + min(dp[j], dp[j - 1], prev_diag)
                    best = max(best, dp[j])
                else:
                    dp[j] = 0
                prev_diag = top
        return best * best
# @lc code=end
