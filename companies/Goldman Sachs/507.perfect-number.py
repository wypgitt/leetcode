#
# @lc app=leetcode id=507 lang=python3
#
# [507] Perfect Number
#
# https://leetcode.com/problems/perfect-number/description/
#
# algorithms
# Easy (49.72%)
# Likes:    1327
# Dislikes: 1292
# Total Accepted:    420K
# Total Submissions: 844K
# Testcase Example:  "28"
#
# A perfect number is a positive integer that is equal to the sum of its
# positive divisors, excluding the number itself. A divisor of an integer x is
# an integer that can divide x evenly.
#
# Given an integer n, return true if n is a perfect number, otherwise return
# false.
#
# Example 1:
#
# Input: num = 28
# Output: true
# Explanation: 28 = 1 + 2 + 4 + 7 + 14
# 1, 2, 4, 7, and 14 are all divisors of 28.
#
# Example 2:
#
# Input: num = 7
# Output: false
#
# Constraints:
#
# 1 <= num <= 10^8
#

# @lc code=start
from math import isqrt


class Solution:
    def checkPerfectNumber(self, num: int) -> bool:
        """
        Interview explanation:
        Perfect number = equal to sum of proper divisors (excluding itself).
        Enumerate divisors up to sqrt; sum pairs; exclude num itself.

        Algorithm:
        - If num <= 1: False
        - s = 1; for d in 2..sqrt: if d|num: s += d + num//d (avoid double sqrt)
        - Return s == num.

        Complexity: O(sqrt(num)) time, O(1) space.
        """
        if num <= 1:
            return False
        s = 1
        for d in range(2, isqrt(num) + 1):
            if num % d == 0:
                s += d
                if d != num // d and num // d != num:
                    s += num // d
        return s == num
# @lc code=end
