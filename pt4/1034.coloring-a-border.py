#
# @lc app=leetcode id=1034 lang=python3
#
# [1034] Coloring A Border
#
# https://leetcode.com/problems/coloring-a-border/description/
#
# algorithms
# Medium (51.25%)
# Likes:    851
# Dislikes: 947
# Total Accepted:    51.4K
# Total Submissions: 100.3K
# Testcase Example:  '[[1,1],[1,2]]\n0\n0\n3'
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
# 
# Example 1:
# Input: grid = [[1,1],[1,2]], row = 0, col = 0, color = 3
# Output: [[3,3],[3,2]]
# Example 2:
# Input: grid = [[1,2,2],[2,3,2]], row = 0, col = 1, color = 3
# Output: [[1,3,3],[2,3,3]]
# Example 3:
# Input: grid = [[1,1,1],[1,1,1],[1,1,1]], row = 1, col = 1, color = 2
# Output: [[2,2,2],[2,1,2],[2,2,2]]
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m, n <= 50
# 1 <= grid[i][j], color <= 1000
# 0 <= row < m
# 0 <= col < n
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def colorBorder(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        rows, cols = len(grid), len(grid[0])
        original = grid[row][col]
        visited = [[False] * cols for _ in range(rows)]
        borders = []
        stack = [(row, col)]
        visited[row][col] = True

        while stack:
            r, c = stack.pop()
            is_border = r in (0, rows - 1) or c in (0, cols - 1)

            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if not (0 <= nr < rows and 0 <= nc < cols):
                    is_border = True
                elif grid[nr][nc] != original:
                    is_border = True
                elif not visited[nr][nc]:
                    visited[nr][nc] = True
                    stack.append((nr, nc))

            if is_border:
                borders.append((r, c))

        for r, c in borders:
            grid[r][c] = color

        return grid
# @lc code=end

"""
Interview Explanation

Core idea:
First find the connected component containing (row, col). A component cell is
on the border if it touches the grid boundary or touches a cell with a
different color.

Algorithm:
1. Store the original color.
2. DFS through cells with that same original color.
3. For each component cell, inspect four neighbors.
4. Mark it as a border if any neighbor is outside the grid or has a different
   color.
5. After traversal, recolor only the collected border cells.

Data structure choice:
The stack performs DFS without recursion depth concerns. A visited matrix keeps
component membership separate from recoloring, which is important when the new
color equals or differs from the original.

Correctness:
DFS visits exactly the cells in the starting connected component because it
only moves through same-color, 4-directionally adjacent cells. The border test
matches the definition directly: boundary adjacency or adjacency to a non-
component cell. Recoloring exactly the collected cells therefore recolors the
component border and leaves interior cells unchanged.

Complexity:
Each cell is visited at most once and each visit checks four neighbors, so time
is O(m * n). The visited matrix and stack use O(m * n) space in the worst case.

Tests and edge cases:
- Single-cell grid: the only cell is a border.
- Entire grid same color: only the outer ring is recolored.
- New color equals original: traversal is still correct because recoloring is
  delayed until after DFS.
- Starting cell already on boundary: it is included as a border.
"""
