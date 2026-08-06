#
# @lc app=leetcode id=1648 lang=python3
#
# [1648] Sell Diminishing-Valued Colored Balls
#
# https://leetcode.com/problems/sell-diminishing-valued-colored-balls/description/
#
# algorithms
# Medium (30.34%)
# Likes:    1179
# Dislikes: 411
# Total Accepted:    47.4K
# Total Submissions: 156K
# Testcase Example:  "[2,5]"
#
# You have an inventory of different colored balls, and there is a customer
# that wants orders balls of any color.
#
# The customer weirdly values the colored balls. Each colored ball's value is
# the number of balls of that color you currently have in your inventory. For
# example, if you own 6 yellow balls, the customer would pay 6 for the first
# yellow ball. After the transaction, there are only 5 yellow balls left, so
# the next yellow ball is then valued at 5 (i.e., the value of the balls
# decreases as you sell more to the customer).
#
# You are given an integer array, inventory, where inventory[i] represents the
# number of balls of the i^th color that you initially own. You are also given
# an integer orders, which represents the total number of balls that the
# customer wants. You can sell the balls in any order.
#
# Return the maximum total value that you can attain after selling orders
# colored balls. As the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: inventory = [2,5], orders = 4
# Output: 14
# Explanation: Sell the 1st color 1 time (2) and the 2nd color 3 times (5 + 4 +
# 3).
# The maximum total value is 2 + 5 + 4 + 3 = 14.
#
# Example 2:
#
# Input: inventory = [3,5], orders = 6
# Output: 19
# Explanation: Sell the 1st color 2 times (3 + 2) and the 2nd color 4 times (5
# + 4 + 3 + 2).
# The maximum total value is 3 + 2 + 5 + 4 + 3 + 2 = 19.
#
# Constraints:
#
# 1 <= inventory.length <= 10^5
#
# 1 <= inventory[i] <= 10^9
#
# 1 <= orders <= min(sum(inventory[i]), 10^9)
#

# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, inventory: List[int], orders: int) -> int:
        """
        Interview explanation:
        Sell `orders` balls; selling a color with x remaining gives x value then
        x becomes x-1. Maximize sum. Binary search threshold price T: sell all
        units valued > T, then some at T.

        Algorithm (binary search on price):
        - Count how many sells at value > mid; adjust; compute profit arithmetic
          series sum.

        Complexity: O(n log M) time, O(1) space.
        """
        MOD = 10**9 + 7
        lo, hi = 0, max(inventory)

        def sold_above(h: int) -> int:
            # units sellable with values h+1 .. inventory[i]
            return sum(max(0, v - h) for v in inventory)

        # max h such that we can still sell >= orders units above h
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if sold_above(mid) >= orders:
                lo = mid
            else:
                hi = mid - 1
        ans = 0
        sold = 0
        for v in inventory:
            if v > lo:
                cnt = v - lo
                ans += (v + lo + 1) * cnt // 2
                sold += cnt
        # oversold cheapest (value lo+1) units among those above lo
        ans -= (sold - orders) * (lo + 1)
        return ans % MOD

    def maxProfit_sort(self, inventory: List[int], orders: int) -> int:
        """
        Interview explanation:
        Alternate greedy after sorting inventory descending with a sentinel 0:
        sell layers between consecutive heights.

        Algorithm (sort + layers):
        - Sort desc + append 0; for each layer height diff, sell across width;
          arithmetic sum; stop when orders exhausted.

        Complexity: O(n log n) time.
        """
        MOD = 10**9 + 7
        inv = sorted(inventory, reverse=True) + [0]
        ans = 0
        width = 0
        for i in range(len(inv) - 1):
            width += 1
            if inv[i] > inv[i + 1]:
                can = width * (inv[i] - inv[i + 1])
                if orders >= can:
                    # full layers from inv[i] down to inv[i+1]+1
                    a, b = inv[i + 1] + 1, inv[i]
                    ans += width * (a + b) * (b - a + 1) // 2
                    orders -= can
                else:
                    full = orders // width
                    a, b = inv[i] - full + 1, inv[i]
                    if full:
                        ans += width * (a + b) * full // 2
                    rem = orders % width
                    ans += rem * (inv[i] - full)
                    orders = 0
                    break
        return ans % MOD
# @lc code=end
