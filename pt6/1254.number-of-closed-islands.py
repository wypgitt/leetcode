#
# @lc app=leetcode id=1254 lang=python3
#
# [1254] Number of Closed Islands
#
# https://leetcode.com/problems/number-of-closed-islands/description/
#
# algorithms
# Medium (67.09%)
# Likes:    4772
# Dislikes: 192
# Total Accepted:    281.6K
# Total Submissions: 419.7K
# Testcase Example:  '[[1,1,1,1,1,1,1,0],[1,0,0,0,0,1,1,0],[1,0,1,0,1,1,1,0],[1,0,0,0,0,1,0,1],[1,1,1,1,1,1,1,0]]'
#
# Given a 2D grid consists of 0s (land) and 1s (water).  An island is a maximal
# 4-directionally connected group of 0s and a closed island is an island
# totally (all left, top, right, bottom) surrounded by 1s.
# 
# Return the number of closed islands.
# 
# 
# Example 1:
# 
# 
# 
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
# 
# 
# 
# Input: grid = [[0,0,1,0,0],[0,1,0,1,0],[0,1,1,1,0]]
# Output: 1
# 
# 
# Example 3:
# 
# 
# Input: grid = [[1,1,1,1,1,1,1],
# [1,0,0,0,0,0,1],
# [1,0,1,1,1,0,1],
# [1,0,1,0,1,0,1],
# [1,0,1,1,1,0,1],
# [1,0,0,0,0,0,1],
# ⁠              [1,1,1,1,1,1,1]]
# Output: 2
# 
# 
# 
# Constraints:
# 
# 
# 1 <= grid.length, grid[0].length <= 100
# 0 <= grid[i][j] <=1
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def closedIsland(self, grid: List[List[int]]) -> int:
        rows, cols = len(grid), len(grid[0])

        def flood(row: int, col: int) -> None:
            stack = [(row, col)]
            grid[row][col] = 1

            while stack:
                r, c = stack.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 0:
                        grid[nr][nc] = 1
                        stack.append((nr, nc))

        for r in range(rows):
            if grid[r][0] == 0:
                flood(r, 0)
            if grid[r][cols - 1] == 0:
                flood(r, cols - 1)

        for c in range(cols):
            if grid[0][c] == 0:
                flood(0, c)
            if grid[rows - 1][c] == 0:
                flood(rows - 1, c)

        closed = 0
        for r in range(1, rows - 1):
            for c in range(1, cols - 1):
                if grid[r][c] == 0:
                    closed += 1
                    flood(r, c)

        return closed
# @lc code=end

# Explanation
# -----------
# Land is 0 and water is 1. First flood-fill every land component connected to
# the border, because those islands cannot be closed. Then scan the interior:
# each remaining 0 starts one closed island, and we flood it so it is counted
# once.
#
# Iterative DFS avoids recursion-depth surprises and uses the grid itself as
# the visited marker by turning visited land into water.
#
# Edge cases: land touching any border is not closed; diagonal contact does not
# connect islands; all-water grids return 0.
#
# Time complexity: O(mn), each cell is processed a constant number of times.
# Space complexity: O(mn) worst-case stack for one large island.
