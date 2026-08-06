#
# @lc app=leetcode id=1052 lang=python3
#
# [1052] Grumpy Bookstore Owner
#
# https://leetcode.com/problems/grumpy-bookstore-owner/description/
#
# algorithms
# Medium (64.11%)
# Likes:    2758
# Dislikes: 268
# Total Accepted:    249K
# Total Submissions: 388K
# Testcase Example:  "[1,0,1,2,1,1,7,5]"
#
# There is a bookstore owner that has a store open for n minutes. You are given
# an integer array customers of length n where customers[i] is the number of
# the customers that enter the store at the start of the i^th minute and all
# those customers leave after the end of that minute.
#
# During certain minutes, the bookstore owner is grumpy. You are given a binary
# array grumpy where grumpy[i] is 1 if the bookstore owner is grumpy during the
# i^th minute, and is 0 otherwise.
#
# When the bookstore owner is grumpy, the customers entering during that minute
# are not satisfied. Otherwise, they are satisfied.
#
# The bookstore owner knows a secret technique to remain not grumpy for minutes
# consecutive minutes, but this technique can only be used once.
#
# Return the maximum number of customers that can be satisfied throughout the
# day.
#
# Example 1:
#
# Input: customers = [1,0,1,2,1,1,7,5], grumpy = [0,1,0,1,0,1,0,1], minutes = 3
#
# Output: 16
#
# Explanation:
#
# The bookstore owner keeps themselves not grumpy for the last 3 minutes.
#
# The maximum number of customers that can be satisfied = 1 + 1 + 1 + 1 + 7 + 5
# = 16.
#
# Example 2:
#
# Input: customers = [1], grumpy = [0], minutes = 1
#
# Output: 1
#
# Constraints:
#
# n == customers.length == grumpy.length
#
# 1 <= minutes <= n <= 2 * 10^4
#
# 0 <= customers[i] <= 1000
#
# grumpy[i] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def maxSatisfied(self, customers: List[int], grumpy: List[int], minutes: int) -> int:
        """
        Interview explanation:
        Always count customers when not grumpy. Additionally, choose a window of
        length `minutes` that maximizes extra customers saved while grumpy —
        sliding window max of grumpy*customers.

        Algorithm:
        - base = sum(customers[i] for not grumpy)
        - Window sum of grumpy customers over minutes; track max extra
        - Return base + max_extra

        Complexity: O(n) time, O(1) space.
        """
        n = len(customers)
        base = sum(c for c, g in zip(customers, grumpy) if g == 0)
        extra = max_extra = 0
        for i in range(n):
            if grumpy[i]:
                extra += customers[i]
            if i >= minutes and grumpy[i - minutes]:
                extra -= customers[i - minutes]
            if i >= minutes - 1:
                max_extra = max(max_extra, extra)
        return base + max_extra
# @lc code=end
