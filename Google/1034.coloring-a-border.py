#
# @lc app=leetcode id=1034 lang=python3
#
# [1034] Coloring A Border
#
# https://leetcode.com/problems/coloring-a-border/description/
#
# algorithms
# Medium (51.56%)
# Likes:    859
# Dislikes: 949
# Total Accepted:    53.6K
# Total Submissions: 104K
# Testcase Example:  "[[1,1],[1,2]]"
#
# You are given an m x n integer matrix grid, and three integers row, col, and
# color. Each value in the grid represents the color of the grid square at that
# location.
#
# Two squares are called adjacent if they are next to each other in any of the
# 4 directions.
#
# Two squares belong to the same connected component if they have the same
# color and they are adjacent.
#
# The border of a connected component is all the squares in the connected
# component that are either adjacent to (at least) a square not in the
# component, or on the boundary of the grid (the first or last row or column).
#
# You should color the border of the connected component that contains the
# square grid[row][col] with color.
#
# Return the final grid.
#
# Example 1:
#
# Input: grid = [[1,1],[1,2]], row = 0, col = 0, color = 3
# Output: [[3,3],[3,2]]
#
# Example 2:
#
# Input: grid = [[1,2,2],[2,3,2]], row = 0, col = 1, color = 3
# Output: [[1,3,3],[2,3,3]]
#
# Example 3:
#
# Input: grid = [[1,1,1],[1,1,1],[1,1,1]], row = 1, col = 1, color = 2
# Output: [[2,2,2],[2,1,2],[2,2,2]]
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# 1 <= grid[i][j], color <= 1000
#
# 0 <= row < m
#
# 0 <= col < n
#

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def colorBorder(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        """
        Interview explanation:
        DFS the connected component of grid[row][col]. A cell is on the border
        if it touches the grid edge or a differently-colored neighbor. Recolor
        those border cells.

        Algorithm:
        - Flood component; collect border cells; paint them

        Complexity: O(m*n) time and space.
        """
        m, n = len(grid), len(grid[0])
        orig = grid[row][col]
        seen = [[False] * n for _ in range(m)]
        borders = []

        def dfs(r: int, c: int) -> None:
            seen[r][c] = True
            is_border = False
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < m and 0 <= nc < n) or grid[nr][nc] != orig:
                    is_border = True
                elif not seen[nr][nc]:
                    dfs(nr, nc)
            if is_border:
                borders.append((r, c))

        dfs(row, col)
        for r, c in borders:
            grid[r][c] = color
        return grid

    def colorBorder_bfs(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        """
        Interview explanation:
        Alternate classic BFS flood-fill of the component; mark border cells
        then recolor.

        Algorithm:
        - Queue from (row,col); visit same-color 4-neighbors; collect borders

        Complexity: O(m*n) time and space.
        """
        m, n = len(grid), len(grid[0])
        orig = grid[row][col]
        # work on a copy of colors via seen
        g = [row[:] for row in grid]
        seen = [[False] * n for _ in range(m)]
        q = deque([(row, col)])
        seen[row][col] = True
        borders = []
        while q:
            r, c = q.popleft()
            is_border = False
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < m and 0 <= nc < n) or g[nr][nc] != orig:
                    is_border = True
                elif not seen[nr][nc]:
                    seen[nr][nc] = True
                    q.append((nr, nc))
            if is_border:
                borders.append((r, c))
        for r, c in borders:
            g[r][c] = color
        return g
# @lc code=end
