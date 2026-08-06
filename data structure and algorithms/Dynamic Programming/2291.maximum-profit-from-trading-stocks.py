#
# @lc app=leetcode id=2291 lang=python3
#
# [2291] Maximum Profit From Trading Stocks
#
# https://leetcode.com/problems/maximum-profit-from-trading-stocks/description/
#
# algorithms
# Medium (48.34%)
# Likes:    193
# Dislikes: 9
# Total Accepted:    18.2K
# Total Submissions: 37.7K
# Testcase Example:  "[5,4,6,2,3]\n[8,5,4,3,5]\n10"
#
#
# You are given two 0-indexed integer arrays of the same length present
# and future where present[i] is the current price of the i^th stock and
# future[i] is the price of the i^th stock a year in the future. You may
# buy each stock at most once. You are also given an integer budget
# representing the amount of money you currently have.
#
# Return the maximum amount of profit you can make.
#
# Example 1:
#
# Input: present = [5,4,6,2,3], future = [8,5,4,3,5], budget = 10
# Output: 6
# Explanation: One possible way to maximize your profit is to:
# Buy the 0^th, 3^rd, and 4^th stocks for a total of 5 + 2 + 3 = 10.
# Next year, sell all three stocks for a total of 8 + 3 + 5 = 16.
# The profit you made is 16 - 10 = 6.
# It can be shown that the maximum profit you can make is 6.
#
# Example 2:
#
# Input: present = [2,2,5], future = [3,4,10], budget = 6
# Output: 5
# Explanation: The only possible way to maximize your profit is to:
# Buy the 2^nd stock, and make a profit of 10 - 5 = 5.
# It can be shown that the maximum profit you can make is 5.
#
# Example 3:
#
# Input: present = [3,3,12], future = [0,3,15], budget = 10
# Output: 0
# Explanation: One possible way to maximize your profit is to:
# Buy the 1^st stock, and make a profit of 3 - 3 = 0.
# It can be shown that the maximum profit you can make is 0.
#
# Constraints:
#
# n == present.length == future.length
#
# 1 <= n <= 1000
#
# 0 <= present[i], future[i] <= 100
#
# 0 <= budget <= 1000
#
# @lc code=start
from typing import List


class Solution:
    def maximumProfit(self, present: List[int], future: List[int], budget: int) -> int:
        """
        Interview explanation:
        0/1 knapsack: buy stock i at present[i] (at most once), sell at future[i];
        maximize profit under budget.

        Algorithm:
        - DP f[j] = max profit with budget j; for each stock update backward.

        Complexity: O(n * budget) time, O(budget) space.
        """
        f = [0] * (budget + 1)
        for a, b in zip(present, future):
            for j in range(budget, a - 1, -1):
                f[j] = max(f[j], f[j - a] + b - a)
        return f[budget]

# @lc code=end
