#
# @lc app=leetcode id=200 lang=python3
#
# [200] Number of Islands
#
# https://leetcode.com/problems/number-of-islands/description/
#
# algorithms
# Medium (64.31%)
# Likes:    25040
# Dislikes: 619
# Total Accepted:    4.2M
# Total Submissions: 6.5M
# Testcase Example:  '[["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]'
#
# Given an m x n 2D binary grid grid which represents a map of '1's (land) and
# '0's (water), return the number of islands.
# 
# An island is surrounded by water and is formed by connecting adjacent lands
# horizontally or vertically. You may assume all four edges of the grid are all
# surrounded by water.
# 
# 
# Example 1:
# 
# 
# Input: grid = [
# ⁠ ["1","1","1","1","0"],
# ⁠ ["1","1","0","1","0"],
# ⁠ ["1","1","0","0","0"],
# ⁠ ["0","0","0","0","0"]
# ]
# Output: 1
# 
# 
# Example 2:
# 
# 
# Input: grid = [
# ⁠ ["1","1","0","0","0"],
# ⁠ ["1","1","0","0","0"],
# ⁠ ["0","0","1","0","0"],
# ⁠ ["0","0","0","1","1"]
# ]
# Output: 3
# 
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m, n <= 300
# grid[i][j] is '0' or '1'.
# 
# 
#

"""
Number of Islands can be solved with graph traversal.

Think of the grid as an implicit graph:
    - Each land cell, "1", is a node.
    - Two land cells are connected if they are adjacent vertically or
      horizontally.
    - An island is one connected component of land cells.

Core idea:
    Scan every cell. When we find an unvisited land cell, we have found a new
    island. Then run DFS or BFS from that cell to visit/sink the entire island
    so it will not be counted again.

Both DFS and BFS are optimal:
    Time:  O(m * n)
        Every cell is visited at most once.

    Space: O(m * n) worst case
        The stack/queue can grow to the size of the island in the worst case.

This file includes both:
    - numIslands: DFS version, used by LeetCode submission.
    - numIslandsBFS: BFS version, same behavior with a queue.

Both versions mutate the input grid by changing visited land from "1" to "0".
"""

# @lc code=start
from collections import deque
from typing import List


class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        rows, cols = len(grid), len(grid[0])
        islands = 0

        def dfs(row: int, col: int) -> None:
            if (
                row < 0
                or row == rows
                or col < 0
                or col == cols
                or grid[row][col] == "0"
            ):
                return

            grid[row][col] = "0"
            dfs(row + 1, col)
            dfs(row - 1, col)
            dfs(row, col + 1)
            dfs(row, col - 1)

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == "1":
                    islands += 1
                    dfs(row, col)

        return islands

    def numIslandsBFS(self, grid: List[List[str]]) -> int:
        rows, cols = len(grid), len(grid[0])
        islands = 0
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] == "1":
                    islands += 1
                    grid[row][col] = "0"
                    queue = deque([(row, col)])

                    while queue:
                        cur_row, cur_col = queue.popleft()

                        for row_delta, col_delta in directions:
                            next_row = cur_row + row_delta
                            next_col = cur_col + col_delta

                            if (
                                0 <= next_row < rows
                                and 0 <= next_col < cols
                                and grid[next_row][next_col] == "1"
                            ):
                                grid[next_row][next_col] = "0"
                                queue.append((next_row, next_col))

        return islands
# @lc code=end
