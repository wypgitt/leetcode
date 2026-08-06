#
# @lc app=leetcode id=1219 lang=python3
#
# [1219] Path with Maximum Gold
#
# https://leetcode.com/problems/path-with-maximum-gold/description/
#
# algorithms
# Medium (68.55%)
# Likes:    3457
# Dislikes: 108
# Total Accepted:    261K
# Total Submissions: 381K
# Testcase Example:  "[[0,6,0],[5,8,7],[0,9,0]]"
#
# In a gold mine grid of size m x n, each cell in this mine has an integer
# representing the amount of gold in that cell, 0 if it is empty.
#
# Return the maximum amount of gold you can collect under the conditions:
#
# Every time you are located in a cell you will collect all the gold in that
# cell.
#
# From your position, you can walk one step to the left, right, up, or down.
#
# You can't visit the same cell more than once.
#
# Never visit a cell with 0 gold.
#
# You can start and stop collecting gold from any position in the grid that has
# some gold.
#
# Example 1:
#
# Input: grid = [[0,6,0],[5,8,7],[0,9,0]]
# Output: 24
# Explanation:
# [[0,6,0],
# [5,8,7],
# [0,9,0]]
# Path to get the maximum gold, 9 -> 8 -> 7.
#
# Example 2:
#
# Input: grid = [[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]]
# Output: 28
# Explanation:
# [[1,0,7],
# [2,0,6],
# [3,4,5],
# [0,3,0],
# [9,0,20]]
# Path to get the maximum gold, 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 15
#
# 0 <= grid[i][j] <= 100
#
# There are at most 25 cells containing gold.
#


# @lc code=start
from typing import List

class Solution:
    def getMaximumGold(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Collect max gold on a path without revisiting cells (0 blocked). DFS
        backtracking from every non-zero cell; mark visited as 0 then restore.

        Algorithm:
        - For each cell with gold, DFS 4-dir collecting; backtrack; track global max

        Complexity: O(k * 4^k) worst for k gold cells; grid small (<=25 gold).
        """
        m, n = len(grid), len(grid[0])
        ans = 0

        def dfs(r: int, c: int) -> int:
            if r < 0 or r >= m or c < 0 or c >= n or grid[r][c] == 0:
                return 0
            gold = grid[r][c]
            grid[r][c] = 0
            best = 0
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                best = max(best, dfs(r + dr, c + dc))
            grid[r][c] = gold
            return gold + best

        for i in range(m):
            for j in range(n):
                if grid[i][j]:
                    ans = max(ans, dfs(i, j))
        return ans
# @lc code=end
