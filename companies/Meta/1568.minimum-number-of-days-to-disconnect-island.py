#
# @lc app=leetcode id=1568 lang=python3
#
# [1568] Minimum Number of Days to Disconnect Island
#
# https://leetcode.com/problems/minimum-number-of-days-to-disconnect-island/description/
#
# algorithms
# Hard (58.67%)
# Likes:    1313
# Dislikes: 224
# Total Accepted:    101K
# Total Submissions: 172K
# Testcase Example:  "[[0,1,1,0],[0,1,1,0],[0,0,0,0]]"
#
# You are given an m x n binary grid grid where 1 represents land and 0
# represents water. An island is a maximal 4-directionally (horizontal or
# vertical) connected group of 1's.
#
# The grid is said to be connected if we have exactly one island, otherwise is
# said disconnected.
#
# In one day, we are allowed to change any single land cell (1) into a water
# cell (0).
#
# Return the minimum number of days to disconnect the grid.
#
# Example 1:
#
# Input: grid = [[0,1,1,0],[0,1,1,0],[0,0,0,0]]
#
# Output: 2
# Explanation: We need at least 2 days to get a disconnected grid.
# Change land grid[1][1] and grid[0][2] to water and get 2 disconnected island.
#
# Example 2:
#
# Input: grid = [[1,1]]
# Output: 2
# Explanation: Grid of full water is also disconnected ([[1,1]] -> [[0,0]]), 0
# islands.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 30
#
# grid[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def minDays(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Disconnect land (4-connected) into >1 island by changing land→water.
        Answer is always 0, 1, or 2. If already disconnected (0/≥2 islands) → 0;
        if some single land removal disconnects → 1; else → 2 (any 2×2 island
        needs 2).

        Algorithm:
        - count_islands(); if !=1 return 0.
        - For each land cell flip to 0, recount; if !=1 return 1; flip back.
        - return 2.

        Complexity: O((mn)^2) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dirs = ((1, 0), (-1, 0), (0, 1), (0, -1))

        def islands() -> int:
            seen = [[False] * n for _ in range(m)]
            cnt = 0

            def dfs(r, c):
                stack = [(r, c)]
                seen[r][c] = True
                while stack:
                    x, y = stack.pop()
                    for dr, dc in dirs:
                        nx, ny = x + dr, y + dc
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1 and not seen[nx][ny]:
                            seen[nx][ny] = True
                            stack.append((nx, ny))

            for i in range(m):
                for j in range(n):
                    if grid[i][j] == 1 and not seen[i][j]:
                        cnt += 1
                        dfs(i, j)
            return cnt

        if islands() != 1:
            return 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 1:
                    grid[i][j] = 0
                    if islands() != 1:
                        grid[i][j] = 1
                        return 1
                    grid[i][j] = 1
        return 2
# @lc code=end

