#
# @lc app=leetcode id=405 lang=python3
#
# [405] Convert a Number to Hexadecimal
#
# https://leetcode.com/problems/convert-a-number-to-hexadecimal/description/
#
# algorithms
# Easy (54.68%)
# Likes:    1456
# Dislikes: 233
# Total Accepted:    233K
# Total Submissions: 425K
# Testcase Example:  "26"
#
# Given a 32-bit integer num, return a string representing its hexadecimal
# representation. For negative integers, two’s complement method is used.
#
# All the letters in the answer string should be lowercase characters, and
# there should not be any leading zeros in the answer except for the zero
# itself.
#
# Note: You are not allowed to use any built-in library method to directly
# solve this problem.
#
# Example 1:
#
# Input: num = 26
# Output: "1a"
#
# Example 2:
#
# Input: num = -1
# Output: "ffffffff"
#
# Constraints:
#
# -2^31 <= num <= 2^31 - 1
#

# @lc code=start

class Solution:
    def toHex(self, num: int) -> str:
        """
        Interview explanation:
        Treat num as unsigned 32-bit two's complement. Repeatedly take the low
        4 bits as a hex digit and right-shift until zero.

        Algorithm:
        - If num==0 return "0". Mask with 0xffffffff; while n: append hex[n&15], n>>=4.
        - Reverse digits.

        Complexity: O(1) time (≤8 digits), O(1) space.
        """
        if num == 0:
            return "0"
        hex_digits = "0123456789abcdef"
        n = num & 0xFFFFFFFF
        out = []
        while n:
            out.append(hex_digits[n & 15])
            n >>= 4
        return "".join(reversed(out))
# @lc code=end
