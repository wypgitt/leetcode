#
# @lc app=leetcode id=309 lang=python3
#
# [309] Best Time to Buy and Sell Stock with Cooldown
#
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/description/
#
# algorithms
# Medium (62.54%)
# Likes:    10147
# Dislikes: 350
# Total Accepted:    808K
# Total Submissions: 1.3M
# Testcase Example:  "[1,2,3,0,2]"
#
# You are given an array prices where prices[i] is the price of a given stock
# on the i^th day.
#
# Find the maximum profit you can achieve. You may complete as many
# transactions as you like (i.e., buy one and sell one share of the stock
# multiple times) with the following restrictions:
#
# After you sell your stock, you cannot buy stock on the next day (i.e.,
# cooldown one day).
#
# Note: You may not engage in multiple transactions simultaneously (i.e., you
# must sell the stock before you buy again).
#
# Example 1:
#
# Input: prices = [1,2,3,0,2]
# Output: 3
# Explanation: transactions = [buy, sell, cooldown, buy, sell]
#
# Example 2:
#
# Input: prices = [1]
# Output: 0
#
# Constraints:
#
# 1 <= prices.length <= 5000
#
# 0 <= prices[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        """
        Interview explanation:
        DP with three states after processing each day:
        hold = max profit holding a stock; sold = just sold today;
        rest = cooldown / idle without stock.

        Transitions:
        - hold' = max(hold, rest - price)
        - sold' = hold + price
        - rest' = max(rest, sold)

        Complexity: O(n) time, O(1) space.
        """
        hold, sold, rest = float("-inf"), 0, 0
        for p in prices:
            prev_sold = sold
            sold = hold + p
            hold = max(hold, rest - p)
            rest = max(rest, prev_sold)
        return max(sold, rest)
# @lc code=end

