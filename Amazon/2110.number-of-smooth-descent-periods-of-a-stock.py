#
# @lc app=leetcode id=2110 lang=python3
#
# [2110] Number of Smooth Descent Periods of a Stock
#
# https://leetcode.com/problems/number-of-smooth-descent-periods-of-a-stock/description/
#
# algorithms
# Medium (67.67%)
# Likes:    1094
# Dislikes: 54
# Total Accepted:    146.6K
# Total Submissions: 216.7K
# Testcase Example:  "[3,2,1,4]"
#
# You are given an integer array prices representing the daily price history of
# a stock, where prices[i] is the stock price on the i^th day.
#
# A smooth descent period of a stock consists of one or more contiguous days
# such that the price on each day is lower than the price on the preceding day
# by exactly 1. The first day of the period is exempted from this rule.
#
# Return the number of smooth descent periods.
#
#
#
# Example 1:
#
# Input: prices = [3,2,1,4]
# Output: 7
# Explanation: There are 7 smooth descent periods:
# [3], [2], [1], [4], [3,2], [2,1], and [3,2,1]
# Note that a period with one day is a smooth descent period by the definition.
#
# Example 2:
#
# Input: prices = [8,6,7,7]
# Output: 4
# Explanation: There are 4 smooth descent periods: [8], [6], [7], and [7]
# Note that [8,6] is not a smooth descent period as 8 - 6 ≠ 1.
#
# Example 3:
#
# Input: prices = [1]
# Output: 1
# Explanation: There is 1 smooth descent period: [1]
#
#
#
# Constraints:
#
#
# 1 <= prices.length <= 10^5
#
#
# 1 <= prices[i] <= 10^5
#


# @lc code=start
from typing import List


class Solution:
    def getDescentPeriods(self, prices: List[int]) -> int:
        """
        Interview explanation:
        Smooth descent period: contiguous subarray where each day drops by
        exactly 1. Count all such periods (single days count).

        Algorithm:
        - Scan; maintain streak length of consecutive -1 steps; each day adds
          streak subarrays ending there.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        streak = 0
        for i, p in enumerate(prices):
            if i > 0 and prices[i - 1] - p == 1:
                streak += 1
            else:
                streak = 1
            ans += streak
        return ans

    def getDescentPeriods_math(self, prices: List[int]) -> int:
        """
        Interview explanation:
        Alternate: for each maximal descent run of length L, add L*(L+1)/2.

        Algorithm:
        - Partition into maximal runs; triangular numbers.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        i, n = 0, len(prices)
        while i < n:
            j = i + 1
            while j < n and prices[j - 1] - prices[j] == 1:
                j += 1
            L = j - i
            ans += L * (L + 1) // 2
            i = j
        return ans
# @lc code=end

