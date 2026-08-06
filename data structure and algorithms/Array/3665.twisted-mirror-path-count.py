#
# @lc app=leetcode id=3665 lang=python3
#
# [3665] Twisted Mirror Path Count
#
# https://leetcode.com/problems/twisted-mirror-path-count/description/
#
# algorithms
# Medium (47.52%)
# Likes:    86
# Dislikes: 6
# Total Accepted:    15.4K
# Total Submissions: 32.4K
# Testcase Example:  "[[0,1,0],[0,0,1],[1,0,0]]"
#
#
# Given an m x n binary grid grid where:
#
# grid[i][j] == 0 represents an empty cell, and
#
# grid[i][j] == 1 represents a mirror.
#
# A robot starts at the top-left corner of the grid (0, 0) and wants to
# reach the bottom-right corner (m - 1, n - 1). It can move only right or
# down. If the robot attempts to move into a mirror cell, it is reflected
# before entering that cell:
#
# If it tries to move right into a mirror, it is turned down and moved
# into the cell directly below the mirror.
#
# If it tries to move down into a mirror, it is turned right and moved
# into the cell directly to the right of the mirror.
#
# If this reflection would cause the robot to move outside the grid
# boundaries, the path is considered invalid and should not be counted.
#
# Return the number of unique valid paths from (0, 0) to (m - 1, n - 1).
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Note: If a reflection moves the robot into a mirror cell, the robot is
# immediately reflected again based on the direction it used to enter that
# mirror: if it entered while moving right, it will be turned down; if it
# entered while moving down, it will be turned right. This process will
# continue until either the last cell is reached, the robot moves out of
# bounds or the robot moves to a non-mirror cell.
#
# Example 1:
#
# Input: grid = [[0,1,0],[0,0,1],[1,0,0]]
#
# Output: 5
#
# Explanation:
#
#                         Number
#                         Full Path
#
#                         1
#                         (0, 0) → (0, 1) [M] → (1, 1) → (1, 2) [M] → (2,
# 2)
#
#                         2
#                         (0, 0) → (0, 1) [M] → (1, 1) → (2, 1) → (2, 2)
#
#                         3
#                         (0, 0) → (1, 0) → (1, 1) → (1, 2) [M] → (2, 2)
#
#                         4
#                         (0, 0) → (1, 0) → (1, 1) → (2, 1) → (2, 2)
#
#                         5
#                         (0, 0) → (1, 0) → (2, 0) [M] → (2, 1) → (2, 2)
#
# [M] indicates the robot attempted to enter a mirror cell and instead
# reflected.
#
# Example 2:
#
# Input: grid = [[0,0],[0,0]]
#
# Output: 2
#
# Explanation:
#
#                         Number
#                         Full Path
#
#                         1
#                         (0, 0) → (0, 1) → (1, 1)
#
#                         2
#                         (0, 0) → (1, 0) → (1, 1)
#
# Example 3:
#
# Input: grid = [[0,1,1],[1,1,0]]
#
# Output: 1
#
# Explanation:
#
#                         Number
#                         Full Path
#
#                         1
#                         (0, 0) → (0, 1) [M] → (1, 1) [M] → (1, 2)
#
# (0, 0) → (1, 0) [M] → (1, 1) [M] → (2, 1) goes out of bounds, so it is
# invalid.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 2 <= m, n <= 500
#
# grid[i][j] is either 0 or 1.
#
# grid[0][0] == grid[m - 1][n - 1] == 0
#

# @lc code=start
from typing import List


class Solution:
    def uniquePaths(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Moves are only right/down, but mirrors redirect (right→down, down→right)
        and may chain. Precompute final landings, then DP ways on empty cells.

        Algorithm:
        - go[r][c][d]: landing after entering (r,c) while moving down (d=0) or
          right (d=1); build from bottom-right so mirror chains are O(1).
        - dp[0][0] = 1; from each cell push ways into both move landings.
        - Return dp[m-1][n-1] modulo 10^9+7.

        Complexity: O(m n) time and space.
        """
        MOD = 10**9 + 7
        rows, cols = len(grid), len(grid[0])
        go = [[[(-1, -1), (-1, -1)] for _ in range(cols)] for _ in range(rows)]
        for i in range(rows - 1, -1, -1):
            for j in range(cols - 1, -1, -1):
                if grid[i][j] == 0:
                    go[i][j][0] = go[i][j][1] = (i, j)
                else:
                    # d=1 means entered moving right → reflect down
                    go[i][j][1] = go[i][j + 1][0] if j + 1 < cols else (i, j + 1)
                    # d=0 means entered moving down → reflect right
                    go[i][j][0] = go[i + 1][j][1] if i + 1 < rows else (i + 1, j)

        dp = [[0] * cols for _ in range(rows)]
        dp[0][0] = 1
        # dir 0: down, dir 1: right
        deltas = ((1, 0), (0, 1))
        for i in range(rows):
            for j in range(cols):
                if not dp[i][j]:
                    continue
                for d, (di, dj) in enumerate(deltas):
                    ni, nj = i + di, j + dj
                    if 0 <= ni < rows and 0 <= nj < cols:
                        yi, yj = go[ni][nj][1 - d]
                        if 0 <= yi < rows and 0 <= yj < cols:
                            dp[yi][yj] = (dp[yi][yj] + dp[i][j]) % MOD
        return dp[rows - 1][cols - 1]
# @lc code=end
