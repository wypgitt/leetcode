#
# @lc app=leetcode id=2240 lang=python3
#
# [2240] Number of Ways to Buy Pens and Pencils
#
# https://leetcode.com/problems/number-of-ways-to-buy-pens-and-pencils/description/
#
# algorithms
# Medium (57.03%)
# Likes:    484
# Dislikes: 37
# Total Accepted:    41.5K
# Total Submissions: 72.7K
# Testcase Example:  "20\n10\n5"
#
# You are given an integer total indicating the amount of money you have. You
# are also given two integers cost1 and cost2 indicating the price of a pen and
# pencil respectively. You can spend part or all of your money to buy multiple
# quantities (or none) of each kind of writing utensil.
#
# Return the number of distinct ways you can buy some number of pens and
# pencils.
#
#
#
# Example 1:
#
# Input: total = 20, cost1 = 10, cost2 = 5
# Output: 9
# Explanation: The price of a pen is 10 and the price of a pencil is 5.
# - If you buy 0 pens, you can buy 0, 1, 2, 3, or 4 pencils.
# - If you buy 1 pen, you can buy 0, 1, or 2 pencils.
# - If you buy 2 pens, you cannot buy any pencils.
# The total number of ways to buy pens and pencils is 5 + 3 + 1 = 9.
#
# Example 2:
#
# Input: total = 5, cost1 = 10, cost2 = 10
# Output: 1
# Explanation: The price of both pens and pencils are 10, which cost more than
# total, so you cannot buy any writing utensils. Therefore, there is only 1 way:
# buy 0 pens and 0 pencils.
#
#
#
# Constraints:
#
#
# 1 <= total, cost1, cost2 <= 10^6
#

# @lc code=start
class Solution:
    def waysToBuyPensPencils(self, total: int, cost1: int, cost2: int) -> int:
        """
        Interview explanation:
        Count non-negative (pens, pencils) with cost1*pens + cost2*pencils <= total.

        Algorithm:
        - Enumerate pens = 0..total//cost1; for each, pencils choices =
          total//cost2 + 1 with remaining money.

        Complexity: O(total/cost1) time, O(1) space.
        """
        ans = 0
        for pens in range(total // cost1 + 1):
            remain = total - pens * cost1
            ans += remain // cost2 + 1
        return ans

    def waysToBuyPensPencils_math(self, total: int, cost1: int, cost2: int) -> int:
        """
        Interview explanation:
        Alternate: same enumeration (closed form only if one cost divides nicely).

        Algorithm:
        - Swap so cost1 is larger to slightly fewer iterations.

        Complexity: O(total/max(cost)) time, O(1) space.
        """
        if cost1 < cost2:
            cost1, cost2 = cost2, cost1
        ans = 0
        for x in range(total // cost1 + 1):
            ans += (total - x * cost1) // cost2 + 1
        return ans
# @lc code=end
