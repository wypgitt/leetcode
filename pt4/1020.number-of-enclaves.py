#
# @lc app=leetcode id=1020 lang=python3
#
# [1020] Number of Enclaves
#
# https://leetcode.com/problems/number-of-enclaves/description/
#
# algorithms
# Medium (71.69%)
# Likes:    4639
# Dislikes: 91
# Total Accepted:    417.7K
# Total Submissions: 582.4K
# Testcase Example:  '[[0,0,0,0],[1,0,1,0],[0,1,1,0],[0,0,0,0]]'
#
# You are given an m x n binary matrix grid, where 0 represents a sea cell and
# 1 represents a land cell.
# 
# A move consists of walking from one land cell to another adjacent
# (4-directionally) land cell or walking off the boundary of the grid.
# 
# Return the number of land cells in grid for which we cannot walk off the
# boundary of the grid in any number of moves.
# 
# 
# Example 1:
# 
# 
# Input: grid = [[0,0,0,0],[1,0,1,0],[0,1,1,0],[0,0,0,0]]
# Output: 3
# Explanation: There are three 1s that are enclosed by 0s, and one 1 that is
# not enclosed because its on the boundary.
# 
# 
# Example 2:
# 
# 
# Input: grid = [[0,1,1,0],[0,0,1,0],[0,0,1,0],[0,0,0,0]]
# Output: 0
# Explanation: All 1s are either on the boundary or can reach the boundary.
# 
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m, n <= 500
# grid[i][j] is either 0 or 1.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def numEnclaves(self, grid: List[List[int]]) -> int:
        rows, cols = len(grid), len(grid[0])

        def erase_boundary_component(start_row: int, start_col: int) -> None:
            if grid[start_row][start_col] == 0:
                return

            stack = [(start_row, start_col)]
            grid[start_row][start_col] = 0
            while stack:
                row, col = stack.pop()
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                        grid[nr][nc] = 0
                        stack.append((nr, nc))

        for row in range(rows):
            erase_boundary_component(row, 0)
            erase_boundary_component(row, cols - 1)

        for col in range(cols):
            erase_boundary_component(0, col)
            erase_boundary_component(rows - 1, col)

        return sum(sum(row) for row in grid)
# @lc code=end

"""
Interview Explanation

Core idea:
An enclave is land that cannot reach the boundary. Instead of asking this
question from every land cell, reverse the viewpoint: every land cell connected
to the boundary is definitely not an enclave. Flood-fill those boundary
components away, then count the land that remains.

Algorithm:
1. Start DFS from every boundary cell that contains land.
2. During DFS, change each reachable land cell from 1 to 0.
3. After all boundary-connected land has been erased, sum the grid. The only
   remaining 1s are enclosed land cells.

Data structure choice:
The explicit stack implements iterative DFS. A recursive DFS could be shorter,
but the grid can be 500 x 500, so recursion may exceed Python's call stack.

Correctness:
Any land cell removed by the DFS has a path of land cells to the boundary, so
it can walk off the grid and is not an enclave. Any land cell not removed has no
land path to any boundary cell; otherwise the boundary DFS for that component
would have reached it. Therefore the final count is exactly the number of
enclave cells.

Complexity:
Each cell is visited at most once, so time is O(m * n). The stack can hold up
to O(m * n) cells in the worst case. The grid is modified in place.

Tests and edge cases:
- All water: every boundary DFS returns immediately, answer is 0.
- All land: boundary DFS erases the whole grid, answer is 0.
- Single row or single column: every land cell is boundary-connected, answer 0.
- A solid island surrounded by water: only that island remains and is counted.
"""
