#
# @lc app=leetcode id=1219 lang=python3
#
# [1219] Path with Maximum Gold
#
# https://leetcode.com/problems/path-with-maximum-gold/description/
#
# algorithms
# Medium (68.41%)
# Likes:    3440
# Dislikes: 106
# Total Accepted:    256.2K
# Total Submissions: 374.4K
# Testcase Example:  '[[0,6,0],[5,8,7],[0,9,0]]'
#
# In a gold mine grid of size m x n, each cell in this mine has an integer
# representing the amount of gold in that cell, 0 if it is empty.
# 
# Return the maximum amount of gold you can collect under the conditions:
# 
# 
# Every time you are located in a cell you will collect all the gold in that
# cell.
# From your position, you can walk one step to the left, right, up, or
# down.
# You can't visit the same cell more than once.
# Never visit a cell with 0 gold.
# You can start and stop collecting gold from any position in the grid that has
# some gold.
# 
# 
# 
# Example 1:
# 
# 
# Input: grid = [[0,6,0],[5,8,7],[0,9,0]]
# Output: 24
# Explanation:
# [[0,6,0],
# ⁠[5,8,7],
# ⁠[0,9,0]]
# Path to get the maximum gold, 9 -> 8 -> 7.
# 
# 
# Example 2:
# 
# 
# Input: grid = [[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]]
# Output: 28
# Explanation:
# [[1,0,7],
# ⁠[2,0,6],
# ⁠[3,4,5],
# ⁠[0,3,0],
# ⁠[9,0,20]]
# Path to get the maximum gold, 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7.
# 
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m, n <= 15
# 0 <= grid[i][j] <= 100
# There are at most 25 cells containing gold.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def getMaximumGold(self, grid: List[List[int]]) -> int:
        rows, cols = len(grid), len(grid[0])
        best = 0

        def dfs(row: int, col: int) -> int:
            gold = grid[row][col]
            grid[row][col] = 0
            total = 0

            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] > 0:
                    total = max(total, dfs(nr, nc))

            grid[row][col] = gold
            return gold + total

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] > 0:
                    best = max(best, dfs(row, col))

        return best
# @lc code=end

# Explanation
# -----------
# This is backtracking over the grid. From every nonzero cell, DFS tries all
# four directions, temporarily marks the current cell as 0 to mean "visited in
# this path", and restores it when returning. The function returns the best
# gold collectable starting from that cell.
#
# DFS/backtracking is the right approach because each path cannot revisit a
# cell, and the constraints for nonzero cells are small enough to explore all
# simple paths.
#
# The grid itself is used as the visited structure. That avoids an extra set
# and makes undoing state explicit: save gold, set to 0, explore, restore.
#
# Edge cases: all zero grid returns 0; isolated gold cells return their own
# value; paths may need to turn, so greedy "largest neighbor" is not reliable.
#
# Time complexity: exponential in the number of gold cells in the worst case,
# often bounded as O(g * 3^g) after the first move. Space complexity: O(g) for
# recursion depth.
