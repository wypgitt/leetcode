#
# @lc app=leetcode id=2921 lang=python3
#
# [2921] Maximum Profitable Triplets With Increasing Prices II
#
# https://leetcode.com/problems/maximum-profitable-triplets-with-increasing-prices-ii/description/
#
# algorithms
# Hard (46.20%)
# Likes:    8
# Dislikes: 1
# Total Accepted:    820
# Total Submissions: 1.8K
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
# 3 <= prices.length == profits.length <= 50000
#
# 1 <= prices[i] <= 5000
#
# 1 <= profits[i] <= 10^6
#
# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, prices: List[int], profits: List[int]) -> int:
        """
        Interview explanation:
        Premium. Same as 2907 (max profit of increasing-price triplet) but
        n up to 5e4 and prices <= 5000 — need ~O(n log M).

        Algorithm:
        - Fenwick (max) trees: left[i] = max profit among earlier items with
          smaller price; right[i] similarly scanning from the right with
          mirrored price index. Combine left[j]+profits[j]+right[j].

        Complexity: O(n log M) time, O(M) space.
        """
        n = len(prices)
        m = max(prices)

        class BIT:
            def __init__(self, size: int):
                self.n = size
                self.t = [0] * (size + 1)

            def update(self, i: int, val: int) -> None:
                while i <= self.n:
                    self.t[i] = max(self.t[i], val)
                    i += i & -i

            def query(self, i: int) -> int:
                res = 0
                while i > 0:
                    res = max(res, self.t[i])
                    i -= i & -i
                return res

        left = [0] * n
        right = [0] * n
        bit1 = BIT(m + 1)
        for i in range(n):
            left[i] = bit1.query(prices[i] - 1)
            bit1.update(prices[i], profits[i])
        bit2 = BIT(m + 1)
        for i in range(n - 1, -1, -1):
            x = m + 1 - prices[i]
            right[i] = bit2.query(x - 1)
            bit2.update(x, profits[i])
        ans = -1
        for i in range(n):
            if left[i] and right[i]:
                ans = max(ans, left[i] + profits[i] + right[i])
        return ans
# @lc code=end
