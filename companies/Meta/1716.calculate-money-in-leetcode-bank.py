#
# @lc app=leetcode id=1716 lang=python3
#
# [1716] Calculate Money in Leetcode Bank
#
# https://leetcode.com/problems/calculate-money-in-leetcode-bank/description/
#
# algorithms
# Easy (82.48%)
# Likes:    1858
# Dislikes: 64
# Total Accepted:    310K
# Total Submissions: 375K
# Testcase Example:  "4"
#
# Hercy wants to save money for his first car. He puts money in the Leetcode
# bank every day.
#
# He starts by putting in $1 on Monday, the first day. Every day from Tuesday
# to Sunday, he will put in $1 more than the day before. On every subsequent
# Monday, he will put in $1 more than the previous Monday.
#
# Given n, return the total amount of money he will have in the Leetcode bank
# at the end of the n^th day.
#
# Example 1:
#
# Input: n = 4
# Output: 10
# Explanation: After the 4^th day, the total is 1 + 2 + 3 + 4 = 10.
#
# Example 2:
#
# Input: n = 10
# Output: 37
# Explanation: After the 10^th day, the total is (1 + 2 + 3 + 4 + 5 + 6 + 7) +
# (2 + 3 + 4) = 37. Notice that on the 2^nd Monday, Hercy only puts in $2.
#
# Example 3:
#
# Input: n = 20
# Output: 96
# Explanation: After the 20^th day, the total is (1 + 2 + 3 + 4 + 5 + 6 + 7) +
# (2 + 3 + 4 + 5 + 6 + 7 + 8) + (3 + 4 + 5 + 6 + 7 + 8) = 96.
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def totalMoney(self, n: int) -> int:
        """
        Interview explanation:
        Deposit pattern: week w (0-based) deposits (w+1)+(w+2)+... for up to 7 days.
        Closed form by full weeks + remainder.

        Algorithm:
        - weeks, days = divmod(n, 7)
        - Full weeks: sum_{w=0}^{weeks-1} (7*w + 28) = 7*weeks*(weeks-1)/2 + 28*weeks
        - Remainder: sum_{i=1}^{days} (weeks+i)

        Complexity: O(1) time, O(1) space.
        """
        weeks, days = divmod(n, 7)
        full = weeks * 28 + 7 * weeks * (weeks - 1) // 2
        rest = days * weeks + days * (days + 1) // 2
        return full + rest

    def totalMoney_sim(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: simulate day by day with monday baseline.

        Algorithm:
        - monday=1; day money cycles; each Monday monday++.

        Complexity: O(n) time, O(1) space.
        """
        ans = 0
        monday = 1
        for i in range(n):
            if i % 7 == 0 and i:
                monday += 1
            ans += monday + (i % 7)
        return ans
# @lc code=end
