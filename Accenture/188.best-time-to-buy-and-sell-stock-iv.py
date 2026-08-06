#
# @lc app=leetcode id=188 lang=python3
#
# [188] Best Time to Buy and Sell Stock IV
#
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/description/
#
# algorithms
# Hard (50.92%)
# Likes:    8067
# Dislikes: 228
# Total Accepted:    757K
# Total Submissions: 1.5M
# Testcase Example:  "2"
#
# You are given an integer array prices where prices[i] is the price of a given
# stock on the i^th day, and an integer k.
#
# Find the maximum profit you can achieve. You may complete at most k
# transactions: i.e. you may buy at most k times and sell at most k times.
#
# Note: You may not engage in multiple transactions simultaneously (i.e., you
# must sell the stock before you buy again).
#
# Example 1:
#
# Input: k = 2, prices = [2,4,1]
# Output: 2
# Explanation: Buy on day 1 (price = 2) and sell on day 2 (price = 4), profit =
# 4-2 = 2.
#
# Example 2:
#
# Input: k = 2, prices = [3,2,6,5,0,3]
# Output: 7
# Explanation: Buy on day 2 (price = 2) and sell on day 3 (price = 6), profit =
# 6-2 = 4. Then buy on day 5 (price = 0) and sell on day 6 (price = 3), profit
# = 3-0 = 3.
#
# Constraints:
#
# 1 <= k <= 100
#
# 1 <= prices.length <= 1000
#
# 0 <= prices[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, k: int, prices: List[int]) -> int:
        """
        Interview explanation:
        Generalized stock DP: for each transaction count t, track the best buy
        cost and sell profit. When k is large enough to allow a trade on every
        ascent, fall back to unlimited one-pass profit.

        Algorithm:
        - If k >= n // 2: sum all positive adjacent differences.
        - Else maintain arrays buy[t], sell[t] for t = 1..k.
        - For each price: buy[t] = min(buy[t], price - sell[t-1]);
          sell[t] = max(sell[t], price - buy[t]).
        - Return sell[k].

        Complexity: O(n * k) time, O(k) space (or O(n) for unlimited case).
        """
        n = len(prices)
        if n < 2 or k == 0:
            return 0

        if k >= n // 2:
            return sum(
                max(prices[i] - prices[i - 1], 0) for i in range(1, n)
            )

        buy = [float("inf")] * (k + 1)
        sell = [0] * (k + 1)
        for price in prices:
            for t in range(1, k + 1):
                buy[t] = min(buy[t], price - sell[t - 1])
                sell[t] = max(sell[t], price - buy[t])
        return sell[k]
# @lc code=end
