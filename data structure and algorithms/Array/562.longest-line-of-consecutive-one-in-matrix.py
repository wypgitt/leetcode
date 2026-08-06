#
# @lc app=leetcode id=562 lang=python3
#
# [562] Longest Line of Consecutive One in Matrix
#
# https://leetcode.com/problems/longest-line-of-consecutive-one-in-matrix/description/
#
# algorithms
# Medium (50.63%)
# Likes:    906
# Dislikes: 119
# Total Accepted:    81.7K
# Total Submissions: 161.3K
# Testcase Example:  "[[0,1,1,0],[0,1,1,0],[0,0,0,1]]"
#
#
# Given an m x n binary matrix mat, return the length of the longest line
# of consecutive one in the matrix.
#
# The line could be horizontal, vertical, diagonal, or anti-diagonal.
#
# Example 1:
#
# Input: mat = [[0,1,1,0],[0,1,1,0],[0,0,0,1]]
# Output: 3
#
# Example 2:
#
# Input: mat = [[1,1,1,1],[0,1,1,0],[0,0,0,1]]
# Output: 4
#
# Constraints:
#
# m == mat.length
#
# n == mat[i].length
#
# 1 <= m, n <= 10^4
#
# 1 <= m * n <= 10^4
#
# mat[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List


class Solution:
    def longestLine(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Track consecutive ones ending at each cell in four directions
        (horizontal, vertical, diagonal, anti-diagonal) with DP. Premium
        classic: one pass, O(1) transitions per cell/direction.

        Algorithm:
        - dp[i][j][d] = length of consecutive ones ending at (i,j) in direction d.
        - For a 1 cell, extend from the previous cell in that direction; else 0.
        - Track the global maximum.

        Complexity: O(mn) time, O(mn) space (can roll to O(n) with care).
        """
        if not mat or not mat[0]:
            return 0
        m, n = len(mat), len(mat[0])
        # 0: horizontal, 1: vertical, 2: diagonal \, 3: anti-diagonal /
        dp = [[[0] * 4 for _ in range(n)] for _ in range(m)]
        ans = 0
        for i in range(m):
            for j in range(n):
                if mat[i][j] == 0:
                    continue
                dp[i][j][0] = (dp[i][j - 1][0] if j else 0) + 1
                dp[i][j][1] = (dp[i - 1][j][1] if i else 0) + 1
                dp[i][j][2] = (dp[i - 1][j - 1][2] if i and j else 0) + 1
                dp[i][j][3] = (dp[i - 1][j + 1][3] if i and j + 1 < n else 0) + 1
                ans = max(ans, max(dp[i][j]))
        return ans
# @lc code=end

