#
# @lc app=leetcode id=1277 lang=python3
#
# [1277] Count Square Submatrices with All Ones
#
# https://leetcode.com/problems/count-square-submatrices-with-all-ones/description/
#
# algorithms
# Medium (80.68%)
# Likes:    5959
# Dislikes: 117
# Total Accepted:    481.9K
# Total Submissions: 597.3K
# Testcase Example:  '[[0,1,1,1],[1,1,1,1],[0,1,1,1]]'
#
# Given a m * n matrix of ones and zeros, return how many square submatrices
# have all ones.
# 
# 
# Example 1:
# 
# 
# Input: matrix =
# [
# [0,1,1,1],
# [1,1,1,1],
# [0,1,1,1]
# ]
# Output: 15
# Explanation: 
# There are 10 squares of side 1.
# There are 4 squares of side 2.
# There is  1 square of side 3.
# Total number of squares = 10 + 4 + 1 = 15.
# 
# 
# Example 2:
# 
# 
# Input: matrix = 
# [
# ⁠ [1,0,1],
# ⁠ [1,1,0],
# ⁠ [1,1,0]
# ]
# Output: 7
# Explanation: 
# There are 6 squares of side 1.  
# There is 1 square of side 2. 
# Total number of squares = 6 + 1 = 7.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= arr.length <= 300
# 1 <= arr[0].length <= 300
# 0 <= arr[i][j] <= 1
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def countSquares(self, matrix: List[List[int]]) -> int:
        rows, cols = len(matrix), len(matrix[0])
        prev = [0] * (cols + 1)
        total = 0

        for r in range(1, rows + 1):
            curr = [0] * (cols + 1)
            for c in range(1, cols + 1):
                if matrix[r - 1][c - 1] == 1:
                    curr[c] = 1 + min(prev[c], curr[c - 1], prev[c - 1])
                    total += curr[c]
            prev = curr

        return total
# @lc code=end

# Explanation
# -----------
# dp[r][c] is the side length of the largest all-ones square ending at cell
# (r, c). If matrix[r][c] is 1, it can extend only as far as the minimum of the
# square sizes ending above, left, and diagonally up-left, plus one.
#
# Every square ending at a cell contributes exactly one count for each side
# length from 1 through dp[r][c], so adding dp[r][c] to the answer counts all
# squares.
#
# A rolling row is enough because each state only needs the previous row and
# current row's left value.
#
# Edge cases: zero cells contribute nothing; one-row or one-column matrices
# still work; all ones count many nested squares.
#
# Time complexity: O(mn).
# Space complexity: O(n).
