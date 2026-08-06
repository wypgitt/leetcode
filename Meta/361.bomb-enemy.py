#
# @lc app=leetcode id=361 lang=python3
#
# [361] Bomb Enemy
#
# https://leetcode.com/problems/bomb-enemy/description/
#
# algorithms
# Medium (52.85%)
# Likes:    1003
# Dislikes: 118
# Total Accepted:    87.2K
# Total Submissions: 165.1K
# Testcase Example:  "[[\"0\",\"E\",\"0\",\"0\"],[\"E\",\"0\",\"W\",\"E\"],[\"0\",\"E\",\"0\",\"0\"]]"
#
#
# Given an m x n matrix grid where each cell is either a wall 'W', an
# enemy 'E' or empty '0', return the maximum enemies you can kill using
# one bomb. You can only place the bomb in an empty cell.
#
# The bomb kills all the enemies in the same row and column from the
# planted point until it hits the wall since it is too strong to be
# destroyed.
#
# Example 1:
#
# Input: grid = [["0","E","0","0"],["E","0","W","E"],["0","E","0","0"]]
# Output: 3
#
# Example 2:
#
# Input: grid = [["W","W","W"],["0","0","0"],["E","E","E"]]
# Output: 1
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 500
#
# grid[i][j] is either 'W', 'E', or '0'.
#
# @lc code=start
from typing import List


class Solution:
    def maxKilledEnemies(self, grid: List[List[str]]) -> int:
        """
        Interview explanation:
        DP precompute: for each empty cell, enemies killed = row-segment hits +
        col-segment hits until walls. Sweep rows left-to-right caching rowHits;
        for each col maintain colHits[c] recomputed when hitting a wall.

        Algorithm:
        - For each cell, if wall skip; if at start/after wall, recount enemies
          to next wall in row/col.
        - If empty '0', update max with rowHits + colHits[c].

        Complexity: O(mn) time and O(n) extra space.
        """
        if not grid or not grid[0]:
            return 0
        m, n = len(grid), len(grid[0])
        max_kill = 0
        row_hits = 0
        col_hits = [0] * n

        for i in range(m):
            for j in range(n):
                if j == 0 or grid[i][j - 1] == "W":
                    row_hits = 0
                    k = j
                    while k < n and grid[i][k] != "W":
                        row_hits += grid[i][k] == "E"
                        k += 1
                if i == 0 or grid[i - 1][j] == "W":
                    col_hits[j] = 0
                    k = i
                    while k < m and grid[k][j] != "W":
                        col_hits[j] += grid[k][j] == "E"
                        k += 1
                if grid[i][j] == "0":
                    max_kill = max(max_kill, row_hits + col_hits[j])
        return max_kill
# @lc code=end
