#
# @lc app=leetcode id=695 lang=python3
#
# [695] Max Area of Island
#
# https://leetcode.com/problems/max-area-of-island/description/
#
# algorithms
# Medium (74.16%)
# Likes:    10726
# Dislikes: 223
# Total Accepted:    1.3M
# Total Submissions: 1.7M
# Testcase Example:  "[[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]]"
#
# You are given an m x n binary matrix grid. An island is a group of 1's
# (representing land) connected 4-directionally (horizontal or vertical.) You
# may assume all four edges of the grid are surrounded by water.
#
# The area of an island is the number of cells with a value 1 in the island.
#
# Return the maximum area of an island in grid. If there is no island, return
# 0.
#
# Example 1:
#
# Input: grid =
# [[0,0,1,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,1,1,0,1,0,0,0,0,0,0,0,0],[0,1,0,0,1,1,0,0,1,0,1,0,0],[0,1,0,0,1,1,0,0,1,1,1,0,0],[0,0,0,0,0,0,0,0,0,0,1,0,0],[0,0,0,0,0,0,0,1,1,1,0,0,0],[0,0,0,0,0,0,0,1,1,0,0,0,0]]
# Output: 6
# Explanation: The answer is not 11, because the island must be connected
# 4-directionally.
#
# Example 2:
#
# Input: grid = [[0,0,0,0,0,0,0,0]]
# Output: 0
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# grid[i][j] is either 0 or 1.
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def maxAreaOfIsland(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Largest 4-connected component of 1s. DFS flood-fill counting cells;
        track maximum area (0 if no islands).

        Algorithm:
        - For each land cell, DFS mark visited (set to 0) and count size.

        Complexity: O(m*n) time, O(m*n) recursion space worst-case.
        """
        if not grid:
            return 0
        m, n = len(grid), len(grid[0])

        def dfs(i: int, j: int) -> int:
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == 0:
                return 0
            grid[i][j] = 0
            return 1 + dfs(i + 1, j) + dfs(i - 1, j) + dfs(i, j + 1) + dfs(i, j - 1)

        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    ans = max(ans, dfs(i, j))
        return ans

    def maxAreaOfIslandBFS(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Same island area via iterative BFS to avoid deep recursion.

        Algorithm:
        - Queue flood-fill; count visited land cells per component.

        Complexity: O(m*n) time, O(m*n) queue space.
        """
        if not grid:
            return 0
        m, n = len(grid), len(grid[0])
        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 0:
                    continue
                area = 0
                q = deque([(i, j)])
                grid[i][j] = 0
                while q:
                    r, c = q.popleft()
                    area += 1
                    for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                        if 0 <= nr < m and 0 <= nc < n and grid[nr][nc]:
                            grid[nr][nc] = 0
                            q.append((nr, nc))
                ans = max(ans, area)
        return ans
# @lc code=end
