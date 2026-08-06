#
# @lc app=leetcode id=2303 lang=python3
#
# [2303] Calculate Amount Paid in Taxes
#
# https://leetcode.com/problems/calculate-amount-paid-in-taxes/description/
#
# algorithms
# Easy (69.42%)
# Likes:    291
# Dislikes: 297
# Total Accepted:    59.6K
# Total Submissions: 85.9K
# Testcase Example:  "[[3,50],[7,10],[12,25]]\n10"
#
# You are given a 0-indexed 2D integer array brackets where brackets[i] =
# [upper_i, percent_i] means that the i^th tax bracket has an upper bound of
# upper_i and is taxed at a rate of percent_i. The brackets are sorted by upper
# bound (i.e. upper_i-1 < upper_i for 0 < i < brackets.length).
#
# Tax is calculated as follows:
#
#
# The first upper_0 dollars earned are taxed at a rate of percent_0.
#
#
# The next upper_1 - upper_0 dollars earned are taxed at a rate of percent_1.
#
#
# The next upper_2 - upper_1 dollars earned are taxed at a rate of percent_2.
#
#
# And so on.
#
# You are given an integer income representing the amount of money you earned.
# Return the amount of money that you have to pay in taxes. Answers within 10^-5
# of the actual answer will be accepted.
#
#
#
# Example 1:
#
# Input: brackets = [[3,50],[7,10],[12,25]], income = 10
# Output: 2.65000
# Explanation:
# Based on your income, you have 3 dollars in the 1^st tax bracket, 4 dollars in
# the 2^nd tax bracket, and 3 dollars in the 3^rd tax bracket.
# The tax rate for the three tax brackets is 50%, 10%, and 25%, respectively.
# In total, you pay $3 * 50% + $4 * 10% + $3 * 25% = $2.65 in taxes.
#
# Example 2:
#
# Input: brackets = [[1,0],[4,25],[5,50]], income = 2
# Output: 0.25000
# Explanation:
# Based on your income, you have 1 dollar in the 1^st tax bracket and 1 dollar
# in the 2^nd tax bracket.
# The tax rate for the two tax brackets is 0% and 25%, respectively.
# In total, you pay $1 * 0% + $1 * 25% = $0.25 in taxes.
#
# Example 3:
#
# Input: brackets = [[2,50]], income = 0
# Output: 0.00000
# Explanation:
# You have no income to tax, so you have to pay a total of $0 in taxes.
#
#
#
# Constraints:
#
#
# 1 <= brackets.length <= 100
#
#
# 1 <= upper_i <= 1000
#
#
# 0 <= percent_i <= 100
#
#
# 0 <= income <= 1000
#
#
# upper_i is sorted in ascending order.
#
#
# All the values of upper_i are unique.
#
#
# The upper bound of the last tax bracket is greater than or equal to income.
#

# @lc code=start
from typing import List


class Solution:
    def calculateTax(self, brackets: List[List[int]], income: int) -> float:
        """
        Interview explanation:
        Progressive tax: each bracket taxes the portion of income above the
        previous upper bound at that bracket's percent.

        Algorithm:
        - Walk brackets; tax min(income, upper) - prev at rate/100; stop when
          income is fully covered.

        Complexity: O(n) time, O(1) space.
        """
        tax = 0.0
        prev = 0
        for upper, percent in brackets:
            if income <= prev:
                break
            taxed = min(income, upper) - prev
            tax += taxed * percent / 100.0
            prev = upper
        return tax
# @lc code=end
