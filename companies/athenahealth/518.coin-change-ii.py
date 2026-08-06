#
# @lc app=leetcode id=518 lang=python3
#
# [518] Coin Change II
#
# https://leetcode.com/problems/coin-change-ii/description/
#
# algorithms
# Medium (59.37%)
# Likes:    10372
# Dislikes: 258
# Total Accepted:    1.1M
# Total Submissions: 1.8M
# Testcase Example:  "5"
#
# You are given an integer array coins representing coins of different
# denominations and an integer amount representing a total amount of money.
#
# Return the number of combinations that make up that amount. If that amount of
# money cannot be made up by any combination of the coins, return 0.
#
# You may assume that you have an infinite number of each kind of coin.
#
# The final answer is guaranteed to fit into a signed 32-bit integer.
#
# Example 1:
#
# Input: amount = 5, coins = [1,2,5]
# Output: 4
# Explanation: there are four ways to make up the amount:
# 5=5
# 5=2+2+1
# 5=2+1+1+1
# 5=1+1+1+1+1
#
# Example 2:
#
# Input: amount = 3, coins = [2]
# Output: 0
# Explanation: the amount of 3 cannot be made up just with coins of 2.
#
# Example 3:
#
# Input: amount = 10, coins = [10]
# Output: 1
#
# Constraints:
#
# 1 <= coins.length <= 300
#
# 1 <= coins[i] <= 5000
#
# All the values of coins are unique.
#
# 0 <= amount <= 5000
#

# @lc code=start
from typing import List
class Solution:
    def change(self, amount: int, coins: List[int]) -> int:
        """
        Interview explanation:
        Unbounded knapsack combination DP: outer loop over coins so each
        combination is counted once (order-independent). dp[x] += dp[x-coin].

        Algorithm:
        - dp[0] = 1; for each coin, for x from coin..amount: dp[x] += dp[x-coin].
        - Return dp[amount].

        Complexity: O(amount * len(coins)) time, O(amount) space.
        """
        dp = [0] * (amount + 1)
        dp[0] = 1
        for coin in coins:
            for x in range(coin, amount + 1):
                dp[x] += dp[x - coin]
        return dp[amount]

    def change_2d(self, amount: int, coins: List[int]) -> int:
        """
        Interview explanation:
        Alternate classic 2D DP: dp[i][x] = ways using first i coins to make x.
        Transition: skip coin i-1, or use it (x >= coin).

        Complexity: O(amount * len(coins)) time, O(amount * len(coins)) space
        (can compress to 1D as above).
        """
        n = len(coins)
        dp = [[0] * (amount + 1) for _ in range(n + 1)]
        for i in range(n + 1):
            dp[i][0] = 1
        for i in range(1, n + 1):
            coin = coins[i - 1]
            for x in range(1, amount + 1):
                dp[i][x] = dp[i - 1][x]
                if x >= coin:
                    dp[i][x] += dp[i][x - coin]
        return dp[n][amount]
# @lc code=end
