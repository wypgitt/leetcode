#
# @lc app=leetcode id=790 lang=python3
#
# [790] Domino and Tromino Tiling
#
# https://leetcode.com/problems/domino-and-tromino-tiling/description/
#
# algorithms
# Medium (51.27%)
# Likes:    4196
# Dislikes: 1327
# Total Accepted:    290K
# Total Submissions: 565K
# Testcase Example:  "3"
#
# You have two types of tiles: a 2 x 1 domino shape and a tromino shape. You
# may rotate these shapes.
#
# Given an integer n, return the number of ways to tile an 2 x n board. Since
# the answer may be very large, return it modulo 10^9 + 7.
#
# In a tiling, every square must be covered by a tile. Two tilings are
# different if and only if there are two 4-directionally adjacent cells on the
# board such that exactly one of the tilings has both squares occupied by a
# tile.
#
# Example 1:
#
# Input: n = 3
# Output: 5
# Explanation: The five different ways are shown above.
#
# Example 2:
#
# Input: n = 1
# Output: 1
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def numTilings(self, n: int) -> int:
        """
        Interview explanation:
        Tile a 2×n board with dominoes and L-trominoes. DP:
        dp[i] = ways to fully tile 2×i.
        Recurrence: dp[i] = 2*dp[i-1] + dp[i-3] (standard derivation from
        full/partial states), MOD 10^9+7.

        Algorithm:
        - Base: dp[0]=1, dp[1]=1, dp[2]=2, dp[3]=5.
        - For i >= 4: dp[i] = (2*dp[i-1] + dp[i-3]) % MOD.
        - Return dp[n].

        Complexity: O(n) time, O(n) or O(1) space.
        """
        MOD = 10**9 + 7
        if n == 1:
            return 1
        if n == 2:
            return 2
        dp = [0] * (n + 1)
        dp[0], dp[1], dp[2] = 1, 1, 2
        for i in range(3, n + 1):
            dp[i] = (2 * dp[i - 1] + dp[i - 3]) % MOD
        return dp[n]
# @lc code=end

