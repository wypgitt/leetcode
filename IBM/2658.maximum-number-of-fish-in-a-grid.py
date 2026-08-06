#
# @lc app=leetcode id=2658 lang=python3
#
# [2658] Maximum Number of Fish in a Grid
#
# https://leetcode.com/problems/maximum-number-of-fish-in-a-grid/description/
#
# algorithms
# Medium (70.35%)
# Likes:    965
# Dislikes: 67
# Total Accepted:    167.2K
# Total Submissions: 237.6K
# Testcase Example:  "[[0,2,1,0],[4,0,0,3],[1,0,0,4],[0,3,2,0]]"
#
# You are given a 0-indexed 2D matrix grid of size m x n, where (r, c)
# represents:
#
#
# A land cell if grid[r][c] = 0, or
#
#
# A water cell containing grid[r][c] fish, if grid[r][c] > 0.
#
# A fisher can start at any water cell (r, c) and can do the following
# operations any number of times:
#
#
# Catch all the fish at cell (r, c), or
#
#
# Move to any adjacent water cell.
#
# Return the maximum number of fish the fisher can catch if he chooses his
# starting cell optimally, or 0 if no water cell exists.
#
# An adjacent cell of the cell (r, c), is one of the cells (r, c + 1), (r, c -
# 1), (r + 1, c) or (r - 1, c) if it exists.
#
#
#
# Example 1:
#
# Input: grid = [[0,2,1,0],[4,0,0,3],[1,0,0,4],[0,3,2,0]]
# Output: 7
# Explanation: The fisher can start at cell (1,3) and collect 3 fish, then move
# to cell (2,3) and collect 4 fish.
#
# Example 2:
#
# Input: grid = [[1,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,1]]
# Output: 1
# Explanation: The fisher can start at cells (0,0) or (3,3) and collect a single
# fish.
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
# 1 <= m, n <= 10
#
#
# 0 <= grid[i][j] <= 10
#

# @lc code=start

from typing import List
from collections import deque


class Solution:
    def findMaxFish(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        0 = land, >0 = water with fish. Collect all fish in a 4-connected water component; return max.

        Algorithm:
        - DFS flood-fill each unvisited water cell; sum fish; track maximum.

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])

        def dfs(i: int, j: int) -> int:
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] == 0:
                return 0
            fish = grid[i][j]
            grid[i][j] = 0
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                fish += dfs(i + di, j + dj)
            return fish

        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    ans = max(ans, dfs(i, j))
        return ans

    def findMaxFish_bfs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate BFS flood-fill for the same connected fish components.

        Algorithm:
        - Queue expand 4-dir; accumulate fish; mark visited water as 0 on a copy.

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        g = [row[:] for row in grid]
        ans = 0
        for i in range(m):
            for j in range(n):
                if g[i][j] == 0:
                    continue
                q = deque([(i, j)])
                fish = 0
                g[i][j] = 0
                while q:
                    x, y = q.popleft()
                    fish += grid[x][y]
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < m and 0 <= ny < n and g[nx][ny]:
                            g[nx][ny] = 0
                            q.append((nx, ny))
                ans = max(ans, fish)
        return ans
# @lc code=end
