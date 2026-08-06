#
# @lc app=leetcode id=3652 lang=python3
#
# [3652] Best Time to Buy and Sell Stock using Strategy
#
# https://leetcode.com/problems/best-time-to-buy-and-sell-stock-using-strategy/description/
#
# algorithms
# Medium (59.74%)
# Likes:    364
# Dislikes: 43
# Total Accepted:    114.8K
# Total Submissions: 192.3K
# Testcase Example:  "[4,2,8]\n[-1,0,1]\n2"
#
#
# You are given two integer arrays prices and strategy, where:
#
# prices[i] is the price of a given stock on the i^th day.
#
# strategy[i] represents a trading action on the i^th day, where:
#
# -1 indicates buying one unit of the stock.
#
# 0 indicates holding the stock.
#
# 1 indicates selling one unit of the stock.
#
# You are also given an even integer k, and may perform at most one
# modification to strategy. A modification consists of:
#
# Selecting exactly k consecutive elements in strategy.
#
# Set the first k / 2 elements to 0 (hold).
#
# Set the last k / 2 elements to 1 (sell).
#
# The profit is defined as the sum of strategy[i] * prices[i] across all
# days.
#
# Return the maximum possible profit you can achieve.
#
# Note: There are no constraints on budget or stock ownership, so all buy
# and sell operations are feasible regardless of past actions.
#
# Example 1:
#
# Input: prices = [4,2,8], strategy = [-1,0,1], k = 2
#
# Output: 10
#
# Explanation:
#
#                         Modification
#                         Strategy
#                         Profit Calculation
#                         Profit
#
#                         Original
#                         [-1, 0, 1]
#                         (-1 × 4) + (0 × 2) + (1 × 8) = -4 + 0 + 8
#                         4
#
#                         Modify [0, 1]
#                         [0, 1, 1]
#                         (0 × 4) + (1 × 2) + (1 × 8) = 0 + 2 + 8
#                         10
#
#                         Modify [1, 2]
#                         [-1, 0, 1]
#                         (-1 × 4) + (0 × 2) + (1 × 8) = -4 + 0 + 8
#                         4
#
# Thus, the maximum possible profit is 10, which is achieved by modifying
# the subarray [0, 1]​​​​​​​.
#
# Example 2:
#
# Input: prices = [5,4,3], strategy = [1,1,0], k = 2
#
# Output: 9
#
# Explanation:
#
#                         Modification
#                         Strategy
#                         Profit Calculation
#                         Profit
#
#                         Original
#                         [1, 1, 0]
#                         (1 × 5) + (1 × 4) + (0 × 3) = 5 + 4 + 0
#                         9
#
#                         Modify [0, 1]
#                         [0, 1, 0]
#                         (0 × 5) + (1 × 4) + (0 × 3) = 0 + 4 + 0
#                         4
#
#                         Modify [1, 2]
#                         [1, 0, 1]
#                         (1 × 5) + (0 × 4) + (1 × 3) = 5 + 0 + 3
#                         8
#
# Thus, the maximum possible profit is 9, which is achieved without any
# modification.
#
# Constraints:
#
# 2 <= prices.length == strategy.length <= 10^5
#
# 1 <= prices[i] <= 10^5
#
# -1 <= strategy[i] <= 1
#
# 2 <= k <= prices.length
#
# k is even
#

# @lc code=start
from typing import List


class Solution:
    def maxProfit(self, prices: List[int], strategy: List[int], k: int) -> int:
        """
        Interview explanation:
        Profit is Σ strategy[i]*prices[i]; one window of length k becomes
        k/2 holds then k/2 sells — pick the window with best delta.

        Algorithm:
        - base = Σ strategy[i]*prices[i].
        - For window [i,i+k): delta = -Σ strategy*price on first half
          + Σ (1-strategy)*price on second half; slide in O(1).
        - Answer max(base, base+delta).

        Complexity: O(n) time, O(1) extra space.
        """
        n = len(prices)
        base = sum(strategy[i] * prices[i] for i in range(n))
        half = k // 2
        # initial window [0, k)
        delta = 0
        for j in range(half):
            delta -= strategy[j] * prices[j]
        for j in range(half, k):
            delta += (1 - strategy[j]) * prices[j]
        best = max(0, delta)
        for i in range(1, n - k + 1):
            # remove i-1 from first half, add i+half-1 into first half (was second)
            # remove i+half-1 from second (becomes first), add i+k-1 into second
            delta += strategy[i - 1] * prices[i - 1]
            delta -= strategy[i + half - 1] * prices[i + half - 1]
            delta -= (1 - strategy[i + half - 1]) * prices[i + half - 1]
            delta += (1 - strategy[i + k - 1]) * prices[i + k - 1]
            best = max(best, delta)
        return base + best
# @lc code=end

