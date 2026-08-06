#
# @lc app=leetcode id=29 lang=python3
#
# [29] Divide Two Integers
#
# https://leetcode.com/problems/divide-two-integers/description/
#
# algorithms
# Medium (19.73%)
# Likes:    6135
# Dislikes: 15281
# Total Accepted:    1.2M
# Total Submissions: 5.9M
# Testcase Example:  '10\n3'
#
# Given two integers dividend and divisor, divide two integers without using
# multiplication, division, and mod operator.
# 
# The integer division should truncate toward zero, which means losing its
# fractional part. For example, 8.345 would be truncated to 8, and -2.7335
# would be truncated to -2.
# 
# Return the quotient after dividing dividend by divisor.
# 
# Note: Assume we are dealing with an environment that could only store
# integers within the 32-bit signed integer range: [−2^31, 2^31 − 1]. For this
# problem, if the quotient is strictly greater than 2^31 - 1, then return 2^31
# - 1, and if the quotient is strictly less than -2^31, then return -2^31.
# 
# 
# Example 1:
# 
# 
# Input: dividend = 10, divisor = 3
# Output: 3
# Explanation: 10/3 = 3.33333.. which is truncated to 3.
# 
# 
# Example 2:
# 
# 
# Input: dividend = 7, divisor = -3
# Output: -2
# Explanation: 7/-3 = -2.33333.. which is truncated to -2.
# 
# 
# 
# Constraints:
# 
# 
# -2^31 <= dividend, divisor <= 2^31 - 1
# divisor != 0
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def divide(self, dividend: int, divisor: int) -> int:
        """
        Interview explanation:
        Division can be built from repeated subtraction, but subtracting one
        divisor at a time is too slow. Instead, repeatedly subtract the largest
        doubled divisor (powers of two multiples) that fits in the remaining
        dividend. This is binary long division using shifts.

        Algorithm:
        - Work with absolute values and record the final sign.
        - While dividend_abs >= divisor_abs, double divisor_abs until the next
          double would be too large.
        - Subtract that chunk and add the corresponding power of two to result.
        - Restore sign and clamp overflow.

        Edge cases and tests:
        - dividend == 0 returns 0.
        - INT_MIN / -1 overflows and must return INT_MAX.
        - Negative signs are handled by xor of sign bits.

        Complexity: O(log^2 N) time in this simple doubling form, O(1) space.
        """
        int_min, int_max = -(2 ** 31), 2 ** 31 - 1
        if dividend == int_min and divisor == -1:
            return int_max

        negative = (dividend < 0) != (divisor < 0)
        dividend_abs, divisor_abs = abs(dividend), abs(divisor)
        quotient = 0

        while dividend_abs >= divisor_abs:
            chunk = divisor_abs
            multiple = 1
            while dividend_abs >= (chunk << 1):
                chunk <<= 1
                multiple <<= 1
            dividend_abs -= chunk
            quotient += multiple

        return -quotient if negative else quotient
# @lc code=end


