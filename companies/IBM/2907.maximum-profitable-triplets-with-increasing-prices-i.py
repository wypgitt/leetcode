#
# @lc app=leetcode id=2907 lang=python3
#
# [2907] Maximum Profitable Triplets With Increasing Prices I
#
# https://leetcode.com/problems/maximum-profitable-triplets-with-increasing-prices-i/description/
#
# algorithms
# Medium (56.13%)
# Likes:    23
# Dislikes: 1
# Total Accepted:    2K
# Total Submissions: 3.6K
# Testcase Example:  "[10,2,3,4]\n[100,2,7,10]"
#
#
# Given the 0-indexed arrays prices and profits of length n. There are n
# items in an store where the i^th item has a price of prices[i] and a
# profit of profits[i].
#
# We have to pick three items with the following condition:
#
# prices[i] < prices[j] < prices[k] where i < j < k.
#
# If we pick items with indices i, j and k satisfying the above condition,
# the profit would be profits[i] + profits[j] + profits[k].
#
# Return the maximum profit we can get, and -1 if it's not possible to
# pick three items with the given condition.
#
# Example 1:
#
# Input: prices = [10,2,3,4], profits = [100,2,7,10]
# Output: 19
# Explanation: We can't pick the item with index i=0 since there are no
# indices j and k such that the condition holds.
# So the only triplet we can pick, are the items with indices 1, 2 and 3
# and it's a valid pick since prices[1] < prices[2] < prices[3].
# The answer would be sum of their profits which is 2 + 7 + 10 = 19.
#
# Example 2:
#
# Input: prices = [1,2,3,4,5], profits = [1,5,3,4,6]
# Output: 15
# Explanation: We can select any triplet of items since for each triplet
# of indices i, j and k such that i < j < k, the condition holds.
# Therefore the maximum profit we can get would be the 3 most profitable
# items which are indices 1, 3 and 4.
# The answer would be sum of their profits which is 5 + 4 + 6 = 15.
#
# Example 3:
#
# Input: prices = [4,3,2,1], profits = [33,20,19,87]
# Output: -1
# Explanation: We can't select any triplet of indices such that the
# condition holds, so we return -1.
#
# Constraints:
#
# 3 <= prices.length == profits.length <= 2000
#
# 1 <= prices[i] <= 10^6
#
# 1 <= profits[i] <= 10^6
#
# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, prices: List[int], profits: List[int]) -> int:
        """
        Interview explanation:
        Premium. Pick i < j < k with prices[i] < prices[j] < prices[k];
        maximize profits[i]+profits[j]+profits[k], or -1. n <= 2000.

        Algorithm:
        - Enumerate middle j; scan left for max profit with smaller price,
          right for max profit with larger price; take best sum.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(prices)
        ans = -1
        for j in range(n):
            left = right = 0
            for i in range(j):
                if prices[i] < prices[j]:
                    left = max(left, profits[i])
            for k in range(j + 1, n):
                if prices[k] > prices[j]:
                    right = max(right, profits[k])
            if left and right:
                ans = max(ans, left + profits[j] + right)
        return ans
# @lc code=end
