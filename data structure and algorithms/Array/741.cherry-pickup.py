#
# @lc app=leetcode id=741 lang=python3
#
# [741] Cherry Pickup
#
# https://leetcode.com/problems/cherry-pickup/description/
#
# algorithms
# Hard (40.14%)
# Likes:    4734
# Dislikes: 172
# Total Accepted:    119K
# Total Submissions: 298K
# Testcase Example:  "[[0,1,-1],[1,0,-1],[1,1,1]]"
#
# You are given an n x n grid representing a field of cherries, each cell is
# one of three possible integers.
#
# 0 means the cell is empty, so you can pass through,
#
# 1 means the cell contains a cherry that you can pick up and pass through, or
#
# -1 means the cell contains a thorn that blocks your way.
#
# Return the maximum number of cherries you can collect by following the rules
# below:
#
# Starting at the position (0, 0) and reaching (n - 1, n - 1) by moving right
# or down through valid path cells (cells with value 0 or 1).
#
# After reaching (n - 1, n - 1), returning to (0, 0) by moving left or up
# through valid path cells.
#
# When passing through a path cell containing a cherry, you pick it up, and the
# cell becomes an empty cell 0.
#
# If there is no valid path between (0, 0) and (n - 1, n - 1), then no cherries
# can be collected.
#
# Example 1:
#
# Input: grid = [[0,1,-1],[1,0,-1],[1,1,1]]
# Output: 5
# Explanation: The player started at (0, 0) and went down, down, right right to
# reach (2, 2).
# 4 cherries were picked up during this single trip, and the matrix becomes
# [[0,1,-1],[0,0,-1],[0,0,0]].
# Then, the player went left, up, up, left to return home, picking up one more
# cherry.
# The total number of cherries picked up is 5, and this is the maximum
# possible.
#
# Example 2:
#
# Input: grid = [[1,1,-1],[1,-1,1],[-1,1,1]]
# Output: 0
#
# Constraints:
#
# n == grid.length
#
# n == grid[i].length
#
# 1 <= n <= 50
#
# grid[i][j] is -1, 0, or 1.
#
# grid[0][0] != -1
#
# grid[n - 1][n - 1] != -1
#


# @lc code=start
from functools import lru_cache
from typing import List


class Solution:
    def cherryPickup(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Going to (n-1,n-1) and back equals two people walking from (0,0) to
        (n-1,n-1) simultaneously, collecting cherries once when on the same cell.
        DP on (r1, c1, r2); c2 = r1+c1-r2. Maximize cherries; thorns are -inf.

        Algorithm:
        - dp(r1,c1,r2): if out/thorn return -inf; if at end return grid[end]
        - cherries = grid[r1][c1] + (grid[r2][c2] if distinct else 0)
        - Try 4 move pairs (down/right for each); take max + cherries
        - Answer max(0, dp(0,0,0))

        Complexity: O(n^3) time and space.
        """
        n = len(grid)

        @lru_cache(None)
        def dp(r1: int, c1: int, r2: int) -> int:
            c2 = r1 + c1 - r2
            if (
                r1 >= n
                or c1 >= n
                or r2 >= n
                or c2 >= n
                or grid[r1][c1] < 0
                or grid[r2][c2] < 0
            ):
                return float("-inf")
            if r1 == n - 1 and c1 == n - 1:
                return grid[r1][c1]
            cherries = grid[r1][c1]
            if (r1, c1) != (r2, c2):
                cherries += grid[r2][c2]
            cherries += max(
                dp(r1 + 1, c1, r2 + 1),
                dp(r1 + 1, c1, r2),
                dp(r1, c1 + 1, r2 + 1),
                dp(r1, c1 + 1, r2),
            )
            return cherries

        ans = dp(0, 0, 0)
        return max(0, ans) if ans != float("-inf") else 0
# @lc code=end

