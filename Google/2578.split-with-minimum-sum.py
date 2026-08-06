#
# @lc app=leetcode id=2578 lang=python3
#
# [2578] Split With Minimum Sum
#
# https://leetcode.com/problems/split-with-minimum-sum/description/
#
# algorithms
# Easy (73.74%)
# Likes:    440
# Dislikes: 35
# Total Accepted:    54.8K
# Total Submissions: 74.4K
# Testcase Example:  "4325"
#
# Given a positive integer num, split it into two non-negative integers num1 and
# num2 such that:
#
#
# The concatenation of num1 and num2 is a permutation of num.
#
#
#
#
# In other words, the sum of the number of occurrences of each digit in num1 and
# num2 is equal to the number of occurrences of that digit in num.
#
#
#
#
#
#
# num1 and num2 can contain leading zeros.
#
# Return the minimum possible sum of num1 and num2.
#
# Notes:
#
#
# It is guaranteed that num does not contain any leading zeros.
#
#
# The order of occurrence of the digits in num1 and num2 may differ from the
# order of occurrence of num.
#
#
#
# Example 1:
#
# Input: num = 4325
# Output: 59
# Explanation: We can split 4325 so that num1 is 24 and num2 is 35, giving a sum
# of 59. We can prove that 59 is indeed the minimal possible sum.
#
# Example 2:
#
# Input: num = 687
# Output: 75
# Explanation: We can split 687 so that num1 is 68 and num2 is 7, which would
# give an optimal sum of 75.
#
#
#
# Constraints:
#
#
# 10 <= num <= 10^9
#

# @lc code=start
class Solution:
    def splitNum(self, num: int) -> int:
        """
        Interview explanation:
        Split digits of num into two integers (order preserved within each) to minimize
        their sum. Greedily assign sorted digits alternately to two numbers.

        Algorithm:
        - Sort digits ascending; build two numbers by alternating digits.

        Complexity: O(D log D) time, O(D) space.
        """
        digits = sorted(str(num))
        a = b = 0
        for i, d in enumerate(digits):
            if i % 2 == 0:
                a = a * 10 + ord(d) - 48
            else:
                b = b * 10 + ord(d) - 48
        return a + b
# @lc code=end
