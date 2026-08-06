#
# @lc app=leetcode id=2235 lang=python3
#
# [2235] Add Two Integers
#
# https://leetcode.com/problems/add-two-integers/description/
#
# algorithms
# Easy (88.09%)
# Likes:    2180
# Dislikes: 3229
# Total Accepted:    941.4K
# Total Submissions: 1.1M
# Testcase Example:  "12\n5"
#
# Given two integers num1 and num2, return the sum of the two integers.
#
#
#
# Example 1:
#
# Input: num1 = 12, num2 = 5
# Output: 17
# Explanation: num1 is 12, num2 is 5, and their sum is 12 + 5 = 17, so 17 is
# returned.
#
# Example 2:
#
# Input: num1 = -10, num2 = 4
# Output: -6
# Explanation: num1 + num2 = -6, so -6 is returned.
#
#
#
# Constraints:
#
#
# -100 <= num1, num2 <= 100
#

# @lc code=start
class Solution:
    def sum(self, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Return the sum of two integers.

        Algorithm:
        - Direct addition (or bit ops).

        Complexity: O(1) time, O(1) space.
        """
        return num1 + num2

    def sum_bit(self, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Alternate: bitwise sum with carry (mask for Python unlimited ints).

        Algorithm:
        - While b: carry=(a&b)<<1; a^=b; b=carry; use 32-bit mask.

        Complexity: O(1) time, O(1) space.
        """
        MASK = 0xFFFFFFFF
        MAX = 0x7FFFFFFF
        a, b = num1 & MASK, num2 & MASK
        while b:
            carry = (a & b) << 1
            a = (a ^ b) & MASK
            b = carry & MASK
        return a if a <= MAX else ~(a ^ MASK)
# @lc code=end
