#
# @lc app=leetcode id=1594 lang=python3
#
# [1594] Maximum Non Negative Product in a Matrix
#
# https://leetcode.com/problems/maximum-non-negative-product-in-a-matrix/description/
#
# algorithms
# Medium (51.66%)
# Likes:    1454
# Dislikes: 93
# Total Accepted:    113K
# Total Submissions: 219K
# Testcase Example:  "[[-1,-2,-3],[-2,-3,-3],[-3,-3,-2]]"
#
# You are given a m x n matrix grid. Initially, you are located at the top-left
# corner (0, 0), and in each step, you can only move right or down in the
# matrix.
#
# Among all possible paths starting from the top-left corner (0, 0) and ending
# in the bottom-right corner (m - 1, n - 1), find the path with the maximum
# non-negative product. The product of a path is the product of all integers in
# the grid cells visited along the path.
#
# Return the maximum non-negative product modulo 10^9 + 7. If the maximum
# product is negative, return -1.
#
# Notice that the modulo is performed after getting the maximum product.
#
# Example 1:
#
# Input: grid = [[-1,-2,-3],[-2,-3,-3],[-3,-3,-2]]
# Output: -1
# Explanation: It is not possible to get non-negative product in the path from
# (0, 0) to (2, 2), so return -1.
#
# Example 2:
#
# Input: grid = [[1,-2,1],[1,-2,1],[3,-4,1]]
# Output: 8
# Explanation: Maximum non-negative product is shown (1 * 1 * -2 * -4 * 1 = 8).
#
# Example 3:
#
# Input: grid = [[1,3],[0,-4]]
# Output: 0
# Explanation: Maximum non-negative product is shown (1 * 0 * -4 = 0).
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 15
#
# -4 <= grid[i][j] <= 4
#

# @lc code=start
from typing import List


class Solution:
    def maxProductPath(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Path right/down maximizing product; negatives flip max/min. DP each
        cell keep (max_prod, min_prod) reachable. If final max < 0 return -1;
        else max % (10^9+7).

        Algorithm:
        - mx[i][j], mn[i][j] from top/left candidates * grid[i][j].
        - Track max/min among previous products then multiply.

        Complexity: O(mn) time/space.
        """
        MOD = 10**9 + 7
        m, n = len(grid), len(grid[0])
        mx = [[0] * n for _ in range(m)]
        mn = [[0] * n for _ in range(m)]
        mx[0][0] = mn[0][0] = grid[0][0]
        for i in range(1, m):
            mx[i][0] = mn[i][0] = mx[i - 1][0] * grid[i][0]
        for j in range(1, n):
            mx[0][j] = mn[0][j] = mx[0][j - 1] * grid[0][j]
        for i in range(1, m):
            for j in range(1, n):
                cands = [
                    mx[i - 1][j] * grid[i][j],
                    mn[i - 1][j] * grid[i][j],
                    mx[i][j - 1] * grid[i][j],
                    mn[i][j - 1] * grid[i][j],
                ]
                mx[i][j] = max(cands)
                mn[i][j] = min(cands)
        if mx[m - 1][n - 1] < 0:
            return -1
        return mx[m - 1][n - 1] % MOD
# @lc code=end

