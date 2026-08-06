#
# @lc app=leetcode id=3651 lang=python3
#
# [3651] Minimum Cost Path with Teleportations
#
# https://leetcode.com/problems/minimum-cost-path-with-teleportations/description/
#
# algorithms
# Hard (45.33%)
# Likes:    430
# Dislikes: 34
# Total Accepted:    67.1K
# Total Submissions: 147.9K
# Testcase Example:  "[[1,3,3],[2,5,4],[4,3,5]]\n2"
#
#
# You are given a m x n 2D integer array grid and an integer k. You start
# at the top-left cell (0, 0) and your goal is to reach the bottom‐right
# cell (m - 1, n - 1).
#
# There are two types of moves available:
#
# Normal move: You can move right or down from your current cell (i, j),
# i.e. you can move to (i, j + 1) (right) or (i + 1, j) (down). The cost
# is the value of the destination cell.
#
# Teleportation: You can teleport from any cell (i, j), to any cell (x, y)
# such that grid[x][y] <= grid[i][j]; the cost of this move is 0. You may
# teleport at most k times.
#
# Return the minimum total cost to reach cell (m - 1, n - 1) from (0, 0).
#
# Example 1:
#
# Input: grid = [[1,3,3],[2,5,4],[4,3,5]], k = 2
#
# Output: 7
#
# Explanation:
#
# Initially we are at (0, 0) and cost is 0.
#
#                         Current Position
#                         Move
#                         New Position
#                         Total Cost
#
#                         (0, 0)
#                         Move Down
#                         (1, 0)
#                         0 + 2 = 2
#
#                         (1, 0)
#                         Move Right
#                         (1, 1)
#                         2 + 5 = 7
#
#                         (1, 1)
#                         Teleport to (2, 2)
#                         (2, 2)
#                         7 + 0 = 7
#
# The minimum cost to reach bottom-right cell is 7.
#
# Example 2:
#
# Input: grid = [[1,2],[2,3],[3,4]], k = 1
#
# Output: 9
#
# Explanation:
#
# Initially we are at (0, 0) and cost is 0.
#
#                         Current Position
#                         Move
#                         New Position
#                         Total Cost
#
#                         (0, 0)
#                         Move Down
#                         (1, 0)
#                         0 + 2 = 2
#
#                         (1, 0)
#                         Move Right
#                         (1, 1)
#                         2 + 3 = 5
#
#                         (1, 1)
#                         Move Down
#                         (2, 1)
#                         5 + 4 = 9
#
# The minimum cost to reach bottom-right cell is 9.
#
# Constraints:
#
# 2 <= m, n <= 80
#
# m == grid.length
#
# n == grid[i].length
#
# 0 <= grid[i][j] <= 10^4
#
# 0 <= k <= 10
#

# @lc code=start
from typing import List
from collections import defaultdict
from math import inf


class Solution:
    def minCost(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Walk only right/down paying the destination; up to k free teleports
        to any cell with value ≤ current.

        Algorithm:
        - DP f[t][i][j] = min cost with t teleports.
        - Layer 0: standard grid DP right/down.
        - For t≥1: process values high→low, running min of f[t-1] among
          values ≥ v teleports onto all cells of value v; then relax right/down.

        Complexity: O(k * m * n + m*n log(m*n)) time, O(k*m*n) space.
        """
        m, n = len(grid), len(grid[0])
        f = [[[inf] * n for _ in range(m)] for _ in range(k + 1)]
        f[0][0][0] = 0
        for i in range(m):
            for j in range(n):
                if i:
                    f[0][i][j] = min(f[0][i][j], f[0][i - 1][j] + grid[i][j])
                if j:
                    f[0][i][j] = min(f[0][i][j], f[0][i][j - 1] + grid[i][j])
        by_val = defaultdict(list)
        for i, row in enumerate(grid):
            for j, x in enumerate(row):
                by_val[x].append((i, j))
        keys = sorted(by_val, reverse=True)
        for t in range(1, k + 1):
            mn = inf
            for key in keys:
                pos = by_val[key]
                for i, j in pos:
                    mn = min(mn, f[t - 1][i][j])
                for i, j in pos:
                    f[t][i][j] = mn
            for i in range(m):
                for j in range(n):
                    if i:
                        f[t][i][j] = min(f[t][i][j], f[t][i - 1][j] + grid[i][j])
                    if j:
                        f[t][i][j] = min(f[t][i][j], f[t][i][j - 1] + grid[i][j])
        return min(f[t][m - 1][n - 1] for t in range(k + 1))
# @lc code=end

