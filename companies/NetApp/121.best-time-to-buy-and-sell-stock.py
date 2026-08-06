#
# @lc app=leetcode id=121 lang=python3
#
# [121] Best Time to Buy and Sell Stock
#
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock/description/
#
# algorithms
# Easy (57.19%)
# Likes:    36113
# Dislikes: 1428
# Total Accepted:    8.4M
# Total Submissions: 15M
# Testcase Example:  "[7,1,5,3,6,4]"
#
# You are given an array prices where prices[i] is the price of a given stock
# on the i^th day.
#
# You want to maximize your profit by choosing a single day to buy one stock
# and choosing a different day in the future to sell that stock.
#
# Return the maximum profit you can achieve from this transaction. If you
# cannot achieve any profit, return 0.
#
# Example 1:
#
# Input: prices = [7,1,5,3,6,4]
# Output: 5
# Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit =
# 6-1 = 5.
# Note that buying on day 2 and selling on day 1 is not allowed because you
# must buy before you sell.
#
# Example 2:
#
# Input: prices = [7,6,4,3,1]
# Output: 0
# Explanation: In this case, no transactions are done and the max profit = 0.
#
# Constraints:
#
# 1 <= prices.length <= 10^5
#
# 0 <= prices[i] <= 10^4
#

# @lc code=start
from typing import List
class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """
        Interview explanation:
        One pass: track the minimum price so far as the best buy day, and at
        each day compute sell profit against that minimum. Update the answer
        with the best profit seen.

        Algorithm:
        - min_price = +inf, best = 0.
        - For each price: update min_price; update best with price - min_price.

        Complexity: O(n) time, O(1) space.
        """
        min_price = float("inf")
        best = 0
        for price in prices:
            if price < min_price:
                min_price = price
            else:
                best = max(best, price - min_price)
        return best
# @lc code=end
