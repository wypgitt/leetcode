#
# @lc app=leetcode id=3393 lang=python3
#
# [3393] Count Paths With the Given XOR Value
#
# https://leetcode.com/problems/count-paths-with-the-given-xor-value/description/
#
# algorithms
# Medium (40.50%)
# Likes:    96
# Dislikes: 8
# Total Accepted:    22.1K
# Total Submissions: 54.5K
# Testcase Example:  "[[2,1,5],[7,10,0],[12,6,4]]\n11"
#
#
# You are given a 2D integer array grid with size m x n. You are also
# given an integer k.
#
# Your task is to calculate the number of paths you can take from the
# top-left cell (0, 0) to the bottom-right cell (m - 1, n - 1) satisfying
# the following constraints:
#
# You can either move to the right or down. Formally, from the cell (i, j)
# you may move to the cell (i, j + 1) or to the cell (i + 1, j) if the
# target cell exists.
#
# The XOR of all the numbers on the path must be equal to k.
#
# Return the total number of such paths.
#
# Since the answer can be very large, return the result modulo 10^9 + 7.
#
# Example 1:
#
# Input: grid = [[2, 1, 5], [7, 10, 0], [12, 6, 4]], k = 11
#
# Output: 3
#
# Explanation:
#
# The 3 paths are:
#
# (0, 0) → (1, 0) → (2, 0) → (2, 1) → (2, 2)
#
# (0, 0) → (1, 0) → (1, 1) → (1, 2) → (2, 2)
#
# (0, 0) → (0, 1) → (1, 1) → (2, 1) → (2, 2)
#
# Example 2:
#
# Input: grid = [[1, 3, 3, 3], [0, 3, 3, 2], [3, 0, 1, 1]], k = 2
#
# Output: 5
#
# Explanation:
#
# The 5 paths are:
#
# (0, 0) → (1, 0) → (2, 0) → (2, 1) → (2, 2) → (2, 3)
#
# (0, 0) → (1, 0) → (1, 1) → (2, 1) → (2, 2) → (2, 3)
#
# (0, 0) → (1, 0) → (1, 1) → (1, 2) → (1, 3) → (2, 3)
#
# (0, 0) → (0, 1) → (1, 1) → (1, 2) → (2, 2) → (2, 3)
#
# (0, 0) → (0, 1) → (0, 2) → (1, 2) → (2, 2) → (2, 3)
#
# Example 3:
#
# Input: grid = [[1, 1, 1, 2], [3, 0, 3, 2], [3, 0, 2, 2]], k = 10
#
# Output: 0
#
# Constraints:
#
# 1 <= m == grid.length <= 300
#
# 1 <= n == grid[r].length <= 300
#
# 0 <= grid[r][c] < 16
#
# 0 <= k < 16
#

# @lc code=start

from typing import List


class Solution:
    def countPathsWithXorValue(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Paths only right/down; XOR of cells equals k. Values and k are < 16, so
        DP on (r, c, xor) is tiny.

        Algorithm:
        - dp[r][c][x] = ways to reach (r,c) with path XOR x.
        - Transition from left/up; answer dp[m-1][n-1][k] mod 10^9+7.

        Complexity: O(m·n·16) time and space.
        """
        MOD = 10**9 + 7
        m, n = len(grid), len(grid[0])
        dp = [[[0] * 16 for _ in range(n)] for _ in range(m)]
        dp[0][0][grid[0][0]] = 1
        for r in range(m):
            for c in range(n):
                for x in range(16):
                    ways = dp[r][c][x]
                    if not ways:
                        continue
                    if c + 1 < n:
                        nx = x ^ grid[r][c + 1]
                        dp[r][c + 1][nx] = (dp[r][c + 1][nx] + ways) % MOD
                    if r + 1 < m:
                        nx = x ^ grid[r + 1][c]
                        dp[r + 1][c][nx] = (dp[r + 1][c][nx] + ways) % MOD
        return dp[m - 1][n - 1][k]
# @lc code=end
