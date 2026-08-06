#
# @lc app=leetcode id=2184 lang=python3
#
# [2184] Number of Ways to Build Sturdy Brick Wall
#
# https://leetcode.com/problems/number-of-ways-to-build-sturdy-brick-wall/description/
#
# algorithms
# Medium (49.52%)
# Likes:    201
# Dislikes: 130
# Total Accepted:    10.2K
# Total Submissions: 20.7K
# Testcase Example:  "2\n3\n[1,2]"
#
#
# You are given integers height and width which specify the dimensions of
# a brick wall you are building. You are also given a 0-indexed array of
# unique integers bricks, where the i^th brick has a height of 1 and a
# width of bricks[i]. You have an infinite supply of each type of brick
# and bricks may not be rotated.
#
# Each row in the wall must be exactly width units long. For the wall to
# be sturdy, adjacent rows in the wall should not join bricks at the same
# location, except at the ends of the wall.
#
# Return the number of ways to build a sturdy wall. Since the answer may
# be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: height = 2, width = 3, bricks = [1,2]
# Output: 2
# Explanation:
# The first two walls in the diagram show the only two ways to build a
# sturdy brick wall.
# Note that the third wall in the diagram is not sturdy because adjacent
# rows join bricks 2 units from the left.
#
# Example 2:
#
# Input: height = 1, width = 1, bricks = [5]
# Output: 0
# Explanation:
# There are no ways to build a sturdy wall because the only type of brick
# we have is longer than the width of the wall.
#
# Constraints:
#
# 1 <= height <= 100
#
# 1 <= width <= 10
#
# 1 <= bricks.length <= 10
#
# 1 <= bricks[i] <= 10
#
# All the values of bricks are unique.
#
# @lc code=start
from typing import List


class Solution:
    def buildWall(self, height: int, width: int, bricks: List[int]) -> int:
        """
        Interview explanation:
        Premium. Build wall height x width with brick widths from bricks (infinite
        supply, height 1 each). Adjacent rows cannot share an interior join.
        Return ways mod 10^9+7.

        Algorithm:
        (enumerate row configs + DP)
        - DFS all ways to tile one row of `width`; store brick layouts / join masks.
        - Compatible if no shared interior edge (bitmask of joins).
        - dp[h][config]: ways to build h rows ending with config.

        Complexity: O(C^2 * height) where C = #row configs (small: width<=10).
        """
        MOD = 10**9 + 7
        configs = []

        def dfs(filled: int, joins: int) -> None:
            if filled == width:
                configs.append(joins)
                return
            if filled > width:
                return
            for b in bricks:
                nf = filled + b
                if nf > width:
                    continue
                nj = joins
                if nf < width:
                    nj |= 1 << nf
                dfs(nf, nj)

        dfs(0, 0)
        if not configs:
            return 0
        C = len(configs)
        compat = [[] for _ in range(C)]
        for i in range(C):
            for j in range(C):
                if configs[i] & configs[j] == 0:
                    compat[i].append(j)
        dp = [1] * C
        for _ in range(1, height):
            ndp = [0] * C
            for j in range(C):
                for i in compat[j]:
                    ndp[j] = (ndp[j] + dp[i]) % MOD
            dp = ndp
        return sum(dp) % MOD
# @lc code=end
