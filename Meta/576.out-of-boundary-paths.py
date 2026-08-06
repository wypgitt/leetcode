#
# @lc app=leetcode id=576 lang=python3
#
# [576] Out of Boundary Paths
#
# https://leetcode.com/problems/out-of-boundary-paths/description/
#
# algorithms
# Medium (48.43%)
# Likes:    3994
# Dislikes: 296
# Total Accepted:    230.5K
# Total Submissions: 476K
# Testcase Example:  '2\n2\n2\n0\n0'
#
# There is an m x n grid with a ball. The ball is initially at the position
# [startRow, startColumn]. You are allowed to move the ball to one of the four
# adjacent cells in the grid (possibly out of the grid crossing the grid
# boundary). You can apply at most maxMove moves to the ball.
# 
# Given the five integers m, n, maxMove, startRow, startColumn, return the
# number of paths to move the ball out of the grid boundary. Since the answer
# can be very large, return it modulo 10^9 + 7.
# 
# 
# Example 1:
# 
# 
# Input: m = 2, n = 2, maxMove = 2, startRow = 0, startColumn = 0
# Output: 6
# 
# 
# Example 2:
# 
# 
# Input: m = 1, n = 3, maxMove = 3, startRow = 0, startColumn = 1
# Output: 12
# 
# 
# 
# Constraints:
# 
# 
# 1 <= m, n <= 50
# 0 <= maxMove <= 50
# 0 <= startRow < m
# 0 <= startColumn < n
# 
# 
#

# @lc code=start
from functools import lru_cache


class Solution:
    def findPaths(self, m: int, n: int, maxMove: int, startRow: int, startColumn: int) -> int:
        MOD = 10 ** 9 + 7

        @lru_cache(None)
        def dp(r: int, c: int, moves: int) -> int:
            if r < 0 or r >= m or c < 0 or c >= n:
                return 1
            if moves == 0:
                return 0
            return (dp(r + 1, c, moves - 1) +
                    dp(r - 1, c, moves - 1) +
                    dp(r, c + 1, moves - 1) +
                    dp(r, c - 1, moves - 1)) % MOD

        return dp(startRow, startColumn, maxMove)
# @lc code=end

"""
Interview explanation:
Let dp(r, c, moves) be the number of ways to leave the grid starting from cell (r,c) with at most moves moves remaining. Moving outside contributes 1 successful path. Staying inside with no moves left contributes 0.

Data structure: memoization caches overlapping grid/move states; recursion expresses the four-direction transition directly.

Edge cases: maxMove = 0 returns 0 unless the start were already out of bounds, which constraints do not allow. The modulus is applied at every state.

Complexity: there are m*n*(maxMove+1) states and each has four transitions, so O(m*n*maxMove) time and space.
"""
