#
# @lc app=leetcode id=1277 lang=python3
#
# [1277] Count Square Submatrices with All Ones
#
# https://leetcode.com/problems/count-square-submatrices-with-all-ones/description/
#
# algorithms
# Medium (80.79%)
# Likes:    5999
# Dislikes: 117
# Total Accepted:    495K
# Total Submissions: 613K
# Testcase Example:  "[[0,1,1,1],[1,1,1,1],[0,1,1,1]]"
#
# Given a m * n matrix of ones and zeros, return how many square submatrices
# have all ones.
#
# Example 1:
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
# There is 1 square of side 3.
# Total number of squares = 10 + 4 + 1 = 15.
#
# Example 2:
#
# Input: matrix =
# [
# [1,0,1],
# [1,1,0],
# [1,1,0]
# ]
# Output: 7
# Explanation:
# There are 6 squares of side 1.
# There is 1 square of side 2.
# Total number of squares = 6 + 1 = 7.
#
# Constraints:
#
# 1 <= arr.length <= 300
#
# 1 <= arr[0].length <= 300
#
# 0 <= arr[i][j] <= 1
#

# @lc code=start

from typing import List


class Solution:
    def countSquares(self, matrix: List[List[int]]) -> int:
        """
        Interview explanation:
        DP: dp[i][j]=side of largest square with bottom-right at (i,j).
        Recurrence: if matrix==1: 1+min(left,up,diag) else 0. Sum all dp.

        Algorithm:
        - Copy/in-place dp on matrix; for i,j>0 update; accumulate ans.

        Complexity: O(m*n) time, O(1) extra if in-place.
        """
        if not matrix:
            return 0
        m, n = len(matrix), len(matrix[0])
        ans = 0
        for i in range(m):
            for j in range(n):
                if matrix[i][j] and i and j:
                    matrix[i][j] = (
                        min(matrix[i - 1][j], matrix[i][j - 1], matrix[i - 1][j - 1])
                        + 1
                    )
                ans += matrix[i][j]
        return ans
# @lc code=end
