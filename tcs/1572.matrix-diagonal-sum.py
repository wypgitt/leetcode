#
# @lc app=leetcode id=1572 lang=python3
#
# [1572] Matrix Diagonal Sum
#
# https://leetcode.com/problems/matrix-diagonal-sum/description/
#
# algorithms
# Easy (84.53%)
# Likes:    3844
# Dislikes: 72
# Total Accepted:    559K
# Total Submissions: 661K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given a square matrix mat, return the sum of the matrix diagonals.
#
# Only include the sum of all the elements on the primary diagonal and all the
# elements on the secondary diagonal that are not part of the primary diagonal.
#
# Example 1:
#
# Input: mat = [[1,2,3],
# [4,5,6],
# [7,8,9]]
# Output: 25
# Explanation: Diagonals sum: 1 + 5 + 9 + 3 + 7 = 25
# Notice that element mat[1][1] = 5 is counted only once.
#
# Example 2:
#
# Input: mat = [[1,1,1,1],
# [1,1,1,1],
# [1,1,1,1],
# [1,1,1,1]]
# Output: 8
#
# Example 3:
#
# Input: mat = [[5]]
# Output: 5
#
# Constraints:
#
# n == mat.length == mat[i].length
#
# 1 <= n <= 100
#
# 1 <= mat[i][j] <= 100
#

# @lc code=start
from typing import List


class Solution:
    def diagonalSum(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Sum primary and secondary diagonals; if n odd the center is counted
        twice so subtract once.

        Algorithm:
        - ans = sum(mat[i][i] + mat[i][n-1-i] for i); if n odd ans -= mat[n//2][n//2]

        Complexity: O(n) time, O(1) space.
        """
        n = len(mat)
        ans = 0
        for i in range(n):
            ans += mat[i][i] + mat[i][n - 1 - i]
        if n % 2:
            ans -= mat[n // 2][n // 2]
        return ans

    def diagonalSum_set(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: collect unique diagonal positions in a set then sum.

        Algorithm:
        - For i: add (i,i) and (i,n-1-i); sum those cells.

        Complexity: O(n).
        """
        n = len(mat)
        cells = set()
        for i in range(n):
            cells.add((i, i))
            cells.add((i, n - 1 - i))
        return sum(mat[r][c] for r, c in cells)
# @lc code=end

