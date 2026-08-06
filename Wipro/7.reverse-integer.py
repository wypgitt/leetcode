#
# @lc app=leetcode id=7 lang=python3
#
# [7] Reverse Integer
#
# https://leetcode.com/problems/reverse-integer/description/
#
# algorithms
# Medium (31.85%)
# Likes:    15575
# Dislikes: 14008
# Total Accepted:    5M
# Total Submissions: 15.7M
# Testcase Example:  '123'
#
# Given a signed 32-bit integer x, return x with its digits reversed. If
# reversing x causes the value to go outside the signed 32-bit integer range
# [-2^31, 2^31 - 1], then return 0.
# 
# Assume the environment does not allow you to store 64-bit integers (signed or
# unsigned).
# 
# 
# Example 1:
# 
# 
# Input: x = 123
# Output: 321
# 
# 
# Example 2:
# 
# 
# Input: x = -123
# Output: -321
# 
# 
# Example 3:
# 
# 
# Input: x = 120
# Output: 21
# 
# 
# 
# Constraints:
# 
# 
# -2^31 <= x <= 2^31 - 1
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def reverse(self, x: int) -> int:
        """
        Interview explanation:
        Reverse the absolute value digit by digit, then restore the sign. The
        only tricky part is the 32-bit signed integer bound, so the final answer
        is rejected if it falls outside [-2^31, 2^31 - 1].

        Algorithm:
        - Save the sign and work with abs(x).
        - Repeatedly pop the last digit with divmod(num, 10).
        - Push it into result using result * 10 + digit.
        - Apply sign and clamp by returning 0 when out of range.

        Edge cases and tests:
        - Negative values keep their sign, e.g. -123 -> -321.
        - Trailing zeros disappear, e.g. 120 -> 21.
        - Overflow cases such as 1534236469 return 0.

        Complexity: O(log10(abs(x))) time, O(1) space.
        """
        sign = -1 if x < 0 else 1
        x = abs(x)
        ans = 0

        while x:
            x, digit = divmod(x, 10)
            ans = ans * 10 + digit

        ans *= sign
        return ans if -(2 ** 31) <= ans <= 2 ** 31 - 1 else 0
# @lc code=end


