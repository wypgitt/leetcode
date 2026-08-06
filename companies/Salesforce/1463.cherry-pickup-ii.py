#
# @lc app=leetcode id=1463 lang=python3
#
# [1463] Cherry Pickup II
#
# https://leetcode.com/problems/cherry-pickup-ii/description/
#
# algorithms
# Hard (72.58%)
# Likes:    4556
# Dislikes: 56
# Total Accepted:    251K
# Total Submissions: 346K
# Testcase Example:  "[[3,1,1],[2,5,1],[1,5,5],[2,1,1]]"
#
# You are given a rows x cols matrix grid representing a field of cherries
# where grid[i][j] represents the number of cherries that you can collect from
# the (i, j) cell.
#
# You have two robots that can collect cherries for you:
#
# Robot #1 is located at the top-left corner (0, 0), and
#
# Robot #2 is located at the top-right corner (0, cols - 1).
#
# Return the maximum number of cherries collection using both robots by
# following the rules below:
#
# From a cell (i, j), robots can move to cell (i + 1, j - 1), (i + 1, j), or (i
# + 1, j + 1).
#
# When any robot passes through a cell, It picks up all cherries, and the cell
# becomes an empty cell.
#
# When both robots stay in the same cell, only one takes the cherries.
#
# Both robots cannot move outside of the grid at any moment.
#
# Both robots should reach the bottom row in grid.
#
# Example 1:
#
# Input: grid = [[3,1,1],[2,5,1],[1,5,5],[2,1,1]]
# Output: 24
# Explanation: Path of robot #1 and #2 are described in color green and blue
# respectively.
# Cherries taken by Robot #1, (3 + 2 + 5 + 2) = 12.
# Cherries taken by Robot #2, (1 + 5 + 5 + 1) = 12.
# Total of cherries: 12 + 12 = 24.
#
# Example 2:
#
# Input: grid =
# [[1,0,0,0,0,0,1],[2,0,0,0,0,3,0],[2,0,9,0,0,0,0],[0,3,0,5,4,0,0],[1,0,2,3,0,0,6]]
# Output: 28
# Explanation: Path of robot #1 and #2 are described in color green and blue
# respectively.
# Cherries taken by Robot #1, (1 + 9 + 5 + 2) = 17.
# Cherries taken by Robot #2, (1 + 3 + 4 + 3) = 11.
# Total of cherries: 17 + 11 = 28.
#
# Constraints:
#
# rows == grid.length
#
# cols == grid[i].length
#
# 2 <= rows, cols <= 70
#
# 0 <= grid[i][j] <= 100
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def cherryPickup(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Two robots start at top corners, move down together each row; collect
        cherries (shared cell counted once). DP on (row, col1, col2).

        Algorithm:
        - dfs(r,c1,c2): cherries at cells + max over 9 move pairs to next row.
        - Memoize; base last row.

        Complexity: O(rows * cols^2) time/space.
        """
        rows, cols = len(grid), len(grid[0])

        @lru_cache(None)
        def dp(r, c1, c2):
            if c1 < 0 or c1 >= cols or c2 < 0 or c2 >= cols:
                return float("-inf")
            val = grid[r][c1] + (0 if c1 == c2 else grid[r][c2])
            if r == rows - 1:
                return val
            best = float("-inf")
            for dc1 in (-1, 0, 1):
                for dc2 in (-1, 0, 1):
                    best = max(best, dp(r + 1, c1 + dc1, c2 + dc2))
            return val + best

        return int(dp(0, 0, cols - 1))

    def cherryPickup_bottomup(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: bottom-up DP iterating rows downward with rolling 2D states.

        Algorithm:
        - dp[c1][c2] at current row; transition from previous with 9 moves.

        Complexity: O(rows * cols^2) time, O(cols^2) space.
        """
        rows, cols = len(grid), len(grid[0])
        NEG = float("-inf")
        dp = [[NEG] * cols for _ in range(cols)]
        dp[0][cols - 1] = grid[0][0] + (0 if 0 == cols - 1 else grid[0][cols - 1])
        for r in range(rows - 1):
            ndp = [[NEG] * cols for _ in range(cols)]
            for c1 in range(cols):
                for c2 in range(cols):
                    if dp[c1][c2] == NEG:
                        continue
                    for dc1 in (-1, 0, 1):
                        for dc2 in (-1, 0, 1):
                            nc1, nc2 = c1 + dc1, c2 + dc2
                            if 0 <= nc1 < cols and 0 <= nc2 < cols:
                                val = grid[r + 1][nc1] + (
                                    0 if nc1 == nc2 else grid[r + 1][nc2]
                                )
                                ndp[nc1][nc2] = max(ndp[nc1][nc2], dp[c1][c2] + val)
            dp = ndp
        return int(max(max(row) for row in dp))
# @lc code=end
