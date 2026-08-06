#
# @lc app=leetcode id=1254 lang=python3
#
# [1254] Number of Closed Islands
#
# https://leetcode.com/problems/number-of-closed-islands/description/
#
# algorithms
# Medium (67.24%)
# Likes:    4797
# Dislikes: 192
# Total Accepted:    290K
# Total Submissions: 431K
# Testcase Example:  "[[1,1,1,1,1,1,1,0],[1,0,0,0,0,1,1,0],[1,0,1,0,1,1,1,0],[1,0,0,0,0,1,0,1],[1,1,1,1,1,1,1,0]]"
#
# Given a 2D grid consists of 0s (land) and 1s (water). An island is a maximal
# 4-directionally connected group of 0s and a closed island is an island
# totally (all left, top, right, bottom) surrounded by 1s.
#
# Return the number of closed islands.
#
# Example 1:
#
# Input: grid =
# [[1,1,1,1,1,1,1,0],[1,0,0,0,0,1,1,0],[1,0,1,0,1,1,1,0],[1,0,0,0,0,1,0,1],[1,1,1,1,1,1,1,0]]
# Output: 2
# Explanation:
# Islands in gray are closed because they are completely surrounded by water
# (group of 1s).
#
# Example 2:
#
# Input: grid = [[0,0,1,0,0],[0,1,0,1,0],[0,1,1,1,0]]
# Output: 1
#
# Example 3:
#
# Input: grid = [[1,1,1,1,1,1,1],
# [1,0,0,0,0,0,1],
# [1,0,1,1,1,0,1],
# [1,0,1,0,1,0,1],
# [1,0,1,1,1,0,1],
# [1,0,0,0,0,0,1],
# [1,1,1,1,1,1,1]]
# Output: 2
#
# Constraints:
#
# 1 <= grid.length, grid[0].length <= 100
#
# 0 <= grid[i][j] <=1
#

# @lc code=start

from typing import List


class Solution:
    def closedIsland(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Closed island = 0-component not touching the border. Flood-fill (DFS)
        all border-connected 0s to water first, then count remaining 0
        components.

        Algorithm:
        - For each border cell that is 0: DFS mark as 1.
        - Scan interior; each 0 starts a closed island: DFS mark; ans++.

        Complexity: O(m*n) time and O(m*n) stack space worst case.
        """
        if not grid:
            return 0
        m, n = len(grid), len(grid[0])

        def dfs(i: int, j: int) -> None:
            if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != 0:
                return
            grid[i][j] = 1
            dfs(i + 1, j)
            dfs(i - 1, j)
            dfs(i, j + 1)
            dfs(i, j - 1)

        for i in range(m):
            dfs(i, 0)
            dfs(i, n - 1)
        for j in range(n):
            dfs(0, j)
            dfs(m - 1, j)

        ans = 0
        for i in range(m):
            for j in range(n):
                if grid[i][j] == 0:
                    ans += 1
                    dfs(i, j)
        return ans

    def closedIsland_bfs(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate BFS flood-fill for border exclusion then counting.

        Algorithm:
        - Same as DFS version but use queue for flood fills.

        Complexity: O(m*n) time and space.
        """
        from collections import deque

        if not grid:
            return 0
        m, n = len(grid), len(grid[0])
        g = [row[:] for row in grid]

        def bfs(i: int, j: int) -> None:
            q = deque([(i, j)])
            g[i][j] = 1
            while q:
                x, y = q.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < m and 0 <= ny < n and g[nx][ny] == 0:
                        g[nx][ny] = 1
                        q.append((nx, ny))

        for i in range(m):
            if g[i][0] == 0:
                bfs(i, 0)
            if g[i][n - 1] == 0:
                bfs(i, n - 1)
        for j in range(n):
            if g[0][j] == 0:
                bfs(0, j)
            if g[m - 1][j] == 0:
                bfs(m - 1, j)
        ans = 0
        for i in range(m):
            for j in range(n):
                if g[i][j] == 0:
                    ans += 1
                    bfs(i, j)
        return ans
# @lc code=end
