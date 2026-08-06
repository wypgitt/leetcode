#
# @lc app=leetcode id=2684 lang=python3
#
# [2684] Maximum Number of Moves in a Grid
#
# https://leetcode.com/problems/maximum-number-of-moves-in-a-grid/description/
#
# algorithms
# Medium (58.77%)
# Likes:    958
# Dislikes: 28
# Total Accepted:    134.5K
# Total Submissions: 228.8K
# Testcase Example:  "[[2,4,3,5],[5,4,9,3],[3,4,2,11],[10,9,13,15]]"
#
# You are given a 0-indexed m x n matrix grid consisting of positive integers.
#
# You can start at any cell in the first column of the matrix, and traverse the
# grid in the following way:
#
#
# From a cell (row, col), you can move to any of the cells: (row - 1, col + 1),
# (row, col + 1) and (row + 1, col + 1) such that the value of the cell you move
# to, should be strictly bigger than the value of the current cell.
#
# Return the maximum number of moves that you can perform.
#
#
#
# Example 1:
#
# Input: grid = [[2,4,3,5],[5,4,9,3],[3,4,2,11],[10,9,13,15]]
# Output: 3
# Explanation: We can start at the cell (0, 0) and make the following moves:
# - (0, 0) -> (0, 1).
# - (0, 1) -> (1, 2).
# - (1, 2) -> (2, 3).
# It can be shown that it is the maximum number of moves that can be made.
#
# Example 2:
#
# Input: grid = [[3,2,4],[2,1,9],[1,1,7]]
# Output: 0
# Explanation: Starting from any cell in the first column we cannot perform any
# moves.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 2 <= m, n <= 1000
#
#
# 4 <= m * n <= 10^5
#
#
# 1 <= grid[i][j] <= 10^6
#

# @lc code=start

from typing import List


class Solution:
    def maxMoves(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        From any cell in column 0, move to (r-1/r/r+1, c+1) if strictly greater. Max moves possible.

        Algorithm:
        - DP/reachable set of rows per column; propagate rightward; track farthest column reached.

        Complexity: O(mn) time, O(m) space.
        """
        m, n = len(grid), len(grid[0])
        can = set(range(m))
        for c in range(n - 1):
            nxt = set()
            for r in can:
                for nr in (r - 1, r, r + 1):
                    if 0 <= nr < m and grid[nr][c + 1] > grid[r][c]:
                        nxt.add(nr)
            if not nxt:
                return c
            can = nxt
        return n - 1

    def maxMoves_dp(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate DP: dp[r][c] = max moves starting from (r,c); answer max over column 0.

        Algorithm:
        - Right-to-left: dp[r][c] = 1 + max over valid next cells (or 0 if none).

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(grid), len(grid[0])
        dp = [[0] * n for _ in range(m)]
        for c in range(n - 2, -1, -1):
            for r in range(m):
                best = 0
                for nr in (r - 1, r, r + 1):
                    if 0 <= nr < m and grid[nr][c + 1] > grid[r][c]:
                        best = max(best, 1 + dp[nr][c + 1])
                dp[r][c] = best
        return max(dp[r][0] for r in range(m))
# @lc code=end
