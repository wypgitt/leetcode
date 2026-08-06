#
# @lc app=leetcode id=1905 lang=python3
#
# [1905] Count Sub Islands
#
# https://leetcode.com/problems/count-sub-islands/description/
#
# algorithms
# Medium (73.07%)
# Likes:    2677
# Dislikes: 92
# Total Accepted:    227K
# Total Submissions: 311K
# Testcase Example:  "[[1,1,1,0,0],[0,1,1,1,1],[0,0,0,0,0],[1,0,0,0,0],[1,1,0,1,1]]"
#
# You are given two m x n binary matrices grid1 and grid2 containing only 0's
# (representing water) and 1's (representing land). An island is a group of 1's
# connected 4-directionally (horizontal or vertical). Any cells outside of the
# grid are considered water cells.
#
# An island in grid2 is considered a sub-island if there is an island in grid1
# that contains all the cells that make up this island in grid2.
#
# Return the number of islands in grid2 that are considered sub-islands.
#
# Example 1:
#
# Input: grid1 = [[1,1,1,0,0],[0,1,1,1,1],[0,0,0,0,0],[1,0,0,0,0],[1,1,0,1,1]],
# grid2 = [[1,1,1,0,0],[0,0,1,1,1],[0,1,0,0,0],[1,0,1,1,0],[0,1,0,1,0]]
# Output: 3
# Explanation: In the picture above, the grid on the left is grid1 and the grid
# on the right is grid2.
# The 1s colored red in grid2 are those considered to be part of a sub-island.
# There are three sub-islands.
#
# Example 2:
#
# Input: grid1 = [[1,0,1,0,1],[1,1,1,1,1],[0,0,0,0,0],[1,1,1,1,1],[1,0,1,0,1]],
# grid2 = [[0,0,0,0,0],[1,1,1,1,1],[0,1,0,1,0],[0,1,0,1,0],[1,0,0,0,1]]
# Output: 2
# Explanation: In the picture above, the grid on the left is grid1 and the grid
# on the right is grid2.
# The 1s colored red in grid2 are those considered to be part of a sub-island.
# There are two sub-islands.
#
# Constraints:
#
# m == grid1.length == grid2.length
#
# n == grid1[i].length == grid2[i].length
#
# 1 <= m, n <= 500
#
# grid1[i][j] and grid2[i][j] are either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def countSubIslands(self, grid1: List[List[int]], grid2: List[List[int]]) -> int:
        """
        Interview explanation:
        Count islands in grid2 that are entirely land in grid1 (sub-islands).
        Flood each grid2 island; if any cell is water in grid1, it's not a sub-island.

        Algorithm (DFS):
        - For each unvisited land in grid2, DFS/BFS; mark visited; track if all
          cells are land in grid1; increment if yes.

        Complexity: O(mn) time/space.
        """
        m, n = len(grid2), len(grid2[0])

        def dfs(i: int, j: int) -> bool:
            if i < 0 or i >= m or j < 0 or j >= n or grid2[i][j] == 0:
                return True
            grid2[i][j] = 0
            ok = grid1[i][j] == 1
            for di, dj in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                ok = dfs(i + di, j + dj) and ok
            return ok

        ans = 0
        for i in range(m):
            for j in range(n):
                if grid2[i][j] == 1 and dfs(i, j):
                    ans += 1
        return ans

    def countSubIslands_bfs(self, grid1: List[List[int]], grid2: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic alternate: BFS flood-fill instead of DFS for each island.

        Algorithm:
        - Queue flood from each land cell; same validity check vs grid1.

        Complexity: O(mn) time/space.
        """
        from collections import deque

        m, n = len(grid2), len(grid2[0])
        g2 = [row[:] for row in grid2]
        ans = 0
        for i in range(m):
            for j in range(n):
                if g2[i][j] != 1:
                    continue
                q = deque([(i, j)])
                g2[i][j] = 0
                ok = True
                while q:
                    x, y = q.popleft()
                    if grid1[x][y] == 0:
                        ok = False
                    for dx, dy in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < m and 0 <= ny < n and g2[nx][ny] == 1:
                            g2[nx][ny] = 0
                            q.append((nx, ny))
                if ok:
                    ans += 1
        return ans
# @lc code=end
