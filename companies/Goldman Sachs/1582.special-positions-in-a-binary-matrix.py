#
# @lc app=leetcode id=1582 lang=python3
#
# [1582] Special Positions in a Binary Matrix
#
# https://leetcode.com/problems/special-positions-in-a-binary-matrix/description/
#
# algorithms
# Easy (72.73%)
# Likes:    1808
# Dislikes: 82
# Total Accepted:    292K
# Total Submissions: 401K
# Testcase Example:  "[[1,0,0],[0,0,1],[1,0,0]]"
#
# Given an m x n binary matrix mat, return the number of special positions in
# mat.
#
# A position (i, j) is called special if mat[i][j] == 1 and all other elements
# in row i and column j are 0 (rows and columns are 0-indexed).
#
# Example 1:
#
# Input: mat = [[1,0,0],[0,0,1],[1,0,0]]
# Output: 1
# Explanation: (1, 2) is a special position because mat[1][2] == 1 and all
# other elements in row 1 and column 2 are 0.
#
# Example 2:
#
# Input: mat = [[1,0,0],[0,1,0],[0,0,1]]
# Output: 3
# Explanation: (0, 0), (1, 1) and (2, 2) are special positions.
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 100
#
# mat[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def numSpecial(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Special = cell 1 whose row and column each contain exactly one 1.
        Precompute row/col sums; count cells with mat[i][j]==1 and
        rowSum[i]==colSum[j]==1.

        Algorithm:
        - row = sum each row; col = sum each col; count matching ones.

        Complexity: O(mn) time, O(m+n) space.
        """
        m, n = len(mat), len(mat[0])
        row = [sum(r) for r in mat]
        col = [sum(mat[i][j] for i in range(m)) for j in range(n)]
        ans = 0
        for i in range(m):
            for j in range(n):
                if mat[i][j] == 1 and row[i] == 1 and col[j] == 1:
                    ans += 1
        return ans

    def numSpecial_brute(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: for each 1, scan its row and column to verify uniqueness.

        Algorithm:
        - For each 1, check no other 1 in row/col.

        Complexity: O(mn*(m+n)).
        """
        m, n = len(mat), len(mat[0])
        ans = 0
        for i in range(m):
            for j in range(n):
                if mat[i][j] != 1:
                    continue
                if sum(mat[i]) == 1 and sum(mat[r][j] for r in range(m)) == 1:
                    ans += 1
        return ans
# @lc code=end

