#
# @lc app=leetcode id=714 lang=python3
#
# [714] Best Time to Buy and Sell Stock with Transaction Fee
#
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/description/
#
# algorithms
# Medium (72.42%)
# Likes:    7699
# Dislikes: 236
# Total Accepted:    609K
# Total Submissions: 841K
# Testcase Example:  "[1,3,2,8,4,9]"
#
# You are given an array prices where prices[i] is the price of a given stock
# on the i^th day, and an integer fee representing a transaction fee.
#
# Find the maximum profit you can achieve. You may complete as many
# transactions as you like, but you need to pay the transaction fee for each
# transaction.
#
# Note:
#
# You may not engage in multiple transactions simultaneously (i.e., you must
# sell the stock before you buy again).
#
# The transaction fee is only charged once for each stock purchase and sale.
#
# Example 1:
#
# Input: prices = [1,3,2,8,4,9], fee = 2
# Output: 8
# Explanation: The maximum profit can be achieved by:
# - Buying at prices[0] = 1
# - Selling at prices[3] = 8
# - Buying at prices[4] = 4
# - Selling at prices[5] = 9
# The total profit is ((8 - 1) - 2) + ((9 - 4) - 2) = 8.
#
# Example 2:
#
# Input: prices = [1,3,7,5,10,3], fee = 3
# Output: 6
#
# Constraints:
#
# 1 <= prices.length <= 5 * 10^4
#
# 1 <= prices[i] < 5 * 10^4
#
# 0 <= fee < 5 * 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, prices: List[int], fee: int) -> int:
        """
        Interview explanation:
        Unlimited transactions with a fee per sell. DP states: hold = max profit
        holding stock; cash = max profit not holding. Transition with fee on sell.

        Algorithm:
        - hold = -inf, cash = 0.
        - For price p: hold = max(hold, cash - p); cash = max(cash, hold + p - fee)
          (use previous hold carefully — temp variable).

        Complexity: O(n) time, O(1) space.
        """
        hold = float("-inf")
        cash = 0
        for p in prices:
            prev_hold = hold
            hold = max(hold, cash - p)
            cash = max(cash, prev_hold + p - fee)
        return int(cash)
# @lc code=end
