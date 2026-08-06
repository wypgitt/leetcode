#
# @lc app=leetcode id=2328 lang=python3
#
# [2328] Number of Increasing Paths in a Grid
#
# https://leetcode.com/problems/number-of-increasing-paths-in-a-grid/description/
#
# algorithms
# Hard (57.30%)
# Likes:    2136
# Dislikes: 45
# Total Accepted:    85.6K
# Total Submissions: 149.4K
# Testcase Example:  "[[1,1],[3,4]]"
#
# You are given an m x n integer matrix grid, where you can move from a cell to
# any adjacent cell in all 4 directions.
#
# Return the number of strictly increasing paths in the grid such that you can
# start from any cell and end at any cell. Since the answer may be very large,
# return it modulo 10^9 + 7.
#
# Two paths are considered different if they do not have exactly the same
# sequence of visited cells.
#
#
#
# Example 1:
#
# Input: grid = [[1,1],[3,4]]
# Output: 8
# Explanation: The strictly increasing paths are:
# - Paths with length 1: [1], [1], [3], [4].
# - Paths with length 2: [1 -> 3], [1 -> 4], [3 -> 4].
# - Paths with length 3: [1 -> 3 -> 4].
# The total number of paths is 4 + 3 + 1 = 8.
#
# Example 2:
#
# Input: grid = [[1],[2]]
# Output: 3
# Explanation: The strictly increasing paths are:
# - Paths with length 1: [1], [2].
# - Paths with length 2: [1 -> 2].
# The total number of paths is 2 + 1 = 3.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 1 <= m, n <= 1000
#
#
# 1 <= m * n <= 10^5
#
#
# 1 <= grid[i][j] <= 10^5
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def countPaths(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Count strictly increasing paths in a grid (4-dir moves). Each cell is a
        path of length 1.

        Algorithm:
        - Memoized DFS: paths starting at (i,j) = 1 + sum over larger neighbors.

        Complexity: O(m*n) time, O(m*n) space.
        """
        MOD = 10**9 + 7
        m, n = len(grid), len(grid[0])
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        @lru_cache(None)
        def dfs(i: int, j: int) -> int:
            res = 1
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] > grid[i][j]:
                    res = (res + dfs(ni, nj)) % MOD
            return res

        return sum(dfs(i, j) for i in range(m) for j in range(n)) % MOD

    def countPaths_dfs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        DFS + memoization (same as primary).

        Algorithm:
        - Topological-style recursion on increasing values.

        Complexity: O(m*n) time, O(m*n) space.
        """
        return self.countPaths(grid)

    def countPaths_dp(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Sort cells ascending and DP paths ending at each cell.

        Algorithm:
        - Process cells by value; dp[cell] = 1 + sum from smaller neighbors.

        Complexity: O(m*n log(m*n)) time, O(m*n) space.
        """
        MOD = 10**9 + 7
        m, n = len(grid), len(grid[0])
        cells = sorted(((grid[i][j], i, j) for i in range(m) for j in range(n)))
        dp = [[1] * n for _ in range(m)]
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for _, i, j in cells:
            for di, dj in dirs:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] < grid[i][j]:
                    dp[i][j] = (dp[i][j] + dp[ni][nj]) % MOD
        return sum(sum(row) % MOD for row in dp) % MOD
# @lc code=end
