#
# @lc app=leetcode id=3418 lang=python3
#
# [3418] Maximum Amount of Money Robot Can Earn
#
# https://leetcode.com/problems/maximum-amount-of-money-robot-can-earn/description/
#
# algorithms
# Medium (47.71%)
# Likes:    497
# Dislikes: 33
# Total Accepted:    105.7K
# Total Submissions: 221.5K
# Testcase Example:  "[[0,1,-1],[1,-2,3],[2,-3,4]]"
#
#
# You are given an m x n grid. A robot starts at the top-left corner of
# the grid (0, 0) and wants to reach the bottom-right corner (m - 1, n -
# 1). The robot can move either right or down at any point in time.
#
# The grid contains a value coins[i][j] in each cell:
#
# If coins[i][j] >= 0, the robot gains that many coins.
#
# If coins[i][j] < 0, the robot encounters a robber, and the robber steals
# the absolute value of coins[i][j] coins.
#
# The robot has a special ability to neutralize robbers in at most 2 cells
# on its path, preventing them from stealing coins in those cells.
#
# Note: The robot's total coins can be negative.
#
# Return the maximum profit the robot can gain on the route.
#
# Example 1:
#
# Input: coins = [[0,1,-1],[1,-2,3],[2,-3,4]]
#
# Output: 8
#
# Explanation:
#
# An optimal path for maximum coins is:
#
# Start at (0, 0) with 0 coins (total coins = 0).
#
# Move to (0, 1), gaining 1 coin (total coins = 0 + 1 = 1).
#
# Move to (1, 1), where there's a robber stealing 2 coins. The robot uses
# one neutralization here, avoiding the robbery (total coins = 1).
#
# Move to (1, 2), gaining 3 coins (total coins = 1 + 3 = 4).
#
# Move to (2, 2), gaining 4 coins (total coins = 4 + 4 = 8).
#
# Example 2:
#
# Input: coins = [[10,10,10],[10,10,10]]
#
# Output: 40
#
# Explanation:
#
# An optimal path for maximum coins is:
#
# Start at (0, 0) with 10 coins (total coins = 10).
#
# Move to (0, 1), gaining 10 coins (total coins = 10 + 10 = 20).
#
# Move to (0, 2), gaining another 10 coins (total coins = 20 + 10 = 30).
#
# Move to (1, 2), gaining the final 10 coins (total coins = 30 + 10 = 40).
#
# Constraints:
#
# m == coins.length
#
# n == coins[i].length
#
# 1 <= m, n <= 500
#
# -1000 <= coins[i][j] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maximumAmount(self, coins: List[List[int]]) -> int:
        """
        Interview explanation:
        Path from top-left to bottom-right (right/down only). Negative cells
        are robbers; neutralize at most 2 of them (treat as 0). Maximize
        profit (can be negative).

        Algorithm:
        - DP[r][c][k] = best profit at (r,c) having used k neutralizations.
        - Transition from up/left; if cell < 0, either pay the loss or
          spend one neutralization when k allows.

        Complexity: O(m*n) time, O(m*n) space (k <= 2).
        """
        m, n = len(coins), len(coins[0])
        NEG = -10**18
        dp = [[[NEG] * 3 for _ in range(n)] for _ in range(m)]

        for k in range(3):
            if coins[0][0] >= 0:
                if k == 0:
                    dp[0][0][k] = coins[0][0]
            else:
                dp[0][0][0] = coins[0][0]
                if k >= 1:
                    dp[0][0][1] = 0

        for r in range(m):
            for c in range(n):
                if r == 0 and c == 0:
                    continue
                val = coins[r][c]
                for k in range(3):
                    best_prev = NEG
                    if r > 0:
                        best_prev = max(best_prev, dp[r - 1][c][k])
                    if c > 0:
                        best_prev = max(best_prev, dp[r][c - 1][k])
                    if best_prev > NEG // 2:
                        if val >= 0:
                            dp[r][c][k] = max(dp[r][c][k], best_prev + val)
                        else:
                            dp[r][c][k] = max(dp[r][c][k], best_prev + val)

                    if val < 0 and k >= 1:
                        best_prev = NEG
                        if r > 0:
                            best_prev = max(best_prev, dp[r - 1][c][k - 1])
                        if c > 0:
                            best_prev = max(best_prev, dp[r][c - 1][k - 1])
                        if best_prev > NEG // 2:
                            dp[r][c][k] = max(dp[r][c][k], best_prev)

        return max(dp[m - 1][n - 1])
# @lc code=end
