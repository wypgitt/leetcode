#
# @lc app=leetcode id=3573 lang=python3
#
# [3573] Best Time to Buy and Sell Stock V
#
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-v/description/
#
# algorithms
# Medium (60.59%)
# Likes:    433
# Dislikes: 65
# Total Accepted:    84.1K
# Total Submissions: 138.8K
# Testcase Example:  "[1,7,9,8,2]\n2"
#
#
# You are given an integer array prices where prices[i] is the price of a
# stock in dollars on the i^th day, and an integer k.
#
# You are allowed to make at most k transactions, where each transaction
# can be either of the following:
#
# Normal transaction: Buy on day i, then sell on a later day j where i <
# j. You profit prices[j] - prices[i].
#
# Short selling transaction: Sell on day i, then buy back on a later day j
# where i < j. You profit prices[i] - prices[j].
#
# Note that you must complete each transaction before starting another.
# Additionally, you can't buy or sell on the same day you are selling or
# buying back as part of a previous transaction.
#
# Return the maximum total profit you can earn by making at most k
# transactions.
#
# Example 1:
#
# Input: prices = [1,7,9,8,2], k = 2
#
# Output: 14
#
# Explanation:
#
# We can make $14 of profit through 2 transactions:
#
# A normal transaction: buy the stock on day 0 for $1 then sell it on day
# 2 for $9.
#
# A short selling transaction: sell the stock on day 3 for $8 then buy
# back on day 4 for $2.
#
# Example 2:
#
# Input: prices = [12,16,19,19,8,1,19,13,9], k = 3
#
# Output: 36
#
# Explanation:
#
# We can make $36 of profit through 3 transactions:
#
# A normal transaction: buy the stock on day 0 for $12 then sell it on day
# 2 for $19.
#
# A short selling transaction: sell the stock on day 3 for $19 then buy
# back on day 4 for $8.
#
# A normal transaction: buy the stock on day 5 for $1 then sell it on day
# 6 for $19.
#
# Constraints:
#
# 2 <= prices.length <= 10^3
#
# 1 <= prices[i] <= 10^9
#
# 1 <= k <= prices.length / 2
#

# @lc code=start

from typing import List


class Solution:
    def maximumProfit(self, prices: List[int], k: int) -> int:
        """
        Interview explanation:
        At most k non-overlapping transactions; each is either long
        (buy then sell) or short (sell then buy back). DP tracks flat / long /
        short for each completed-transaction count.

        Algorithm:
        - f[j][0]=flat, f[j][1]=holding long, f[j][2]=holding short after ≤j
          completed deals.
        - Close long: +price → flat; close short: -price → flat.
        - Open long from flat with j-1: -price; open short: +price.

        Complexity: O(n·k) time, O(k) space.
        """
        # Space-optimized over transaction count
        bought = [float('-inf')] * k
        sold = [float('-inf')] * k
        result = [0] * (k + 1)
        for price in prices:
            for i in range(k - 1, -1, -1):
                result[i + 1] = max(result[i + 1], bought[i] + price, sold[i] - price)
                bought[i] = max(bought[i], result[i] - price)
                sold[i] = max(sold[i], result[i] + price)
        return result[k]

    def maximumProfit_3d(self, prices: List[int], k: int) -> int:
        """
        Interview explanation:
        Alternate: explicit 3D DP over day / transactions / state.

        Algorithm:
        - f[i][j][0/1/2] as above; initialize day 0 long/short opens.

        Complexity: O(n·k) time, O(n·k) space.
        """
        n = len(prices)
        f = [[[0] * 3 for _ in range(k + 1)] for _ in range(n)]
        for j in range(1, k + 1):
            f[0][j][1] = -prices[0]
            f[0][j][2] = prices[0]
        for i in range(1, n):
            for j in range(1, k + 1):
                f[i][j][0] = max(
                    f[i - 1][j][0],
                    f[i - 1][j][1] + prices[i],
                    f[i - 1][j][2] - prices[i],
                )
                f[i][j][1] = max(f[i - 1][j][1], f[i - 1][j - 1][0] - prices[i])
                f[i][j][2] = max(f[i - 1][j][2], f[i - 1][j - 1][0] + prices[i])
        return f[n - 1][k][0]
# @lc code=end
