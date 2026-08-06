#
# @lc app=leetcode id=3602 lang=python3
#
# [3602] Hexadecimal and Hexatrigesimal Conversion
#
# https://leetcode.com/problems/hexadecimal-and-hexatrigesimal-conversion/description/
#
# algorithms
# Easy (80.99%)
# Likes:    54
# Dislikes: 0
# Total Accepted:    31.9K
# Total Submissions: 39.4K
# Testcase Example:  "13"
#
#
# You are given an integer n.
#
# Return the concatenation of the hexadecimal representation of n^2 and
# the hexatrigesimal representation of n^3.
#
# A hexadecimal number is defined as a base-16 numeral system that uses
# the digits 0 – 9 and the uppercase letters A - F to represent values
# from 0 to 15.
#
# A hexatrigesimal number is defined as a base-36 numeral system that uses
# the digits 0 – 9 and the uppercase letters A - Z to represent values
# from 0 to 35.
#
# Example 1:
#
# Input: n = 13
#
# Output: "A91P1"
#
# Explanation:
#
# n^2 = 13 * 13 = 169. In hexadecimal, it converts to (10 * 16) + 9 = 169,
# which corresponds to "A9".
#
# n^3 = 13 * 13 * 13 = 2197. In hexatrigesimal, it converts to (1 * 36^2)
# + (25 * 36) + 1 = 2197, which corresponds to "1P1".
#
# Concatenating both results gives "A9" + "1P1" = "A91P1".
#
# Example 2:
#
# Input: n = 36
#
# Output: "5101000"
#
# Explanation:
#
# n^2 = 36 * 36 = 1296. In hexadecimal, it converts to (5 * 16^2) + (1 *
# 16) + 0 = 1296, which corresponds to "510".
#
# n^3 = 36 * 36 * 36 = 46656. In hexatrigesimal, it converts to (1 * 36^3)
# + (0 * 36^2) + (0 * 36) + 0 = 46656, which corresponds to "1000".
#
# Concatenating both results gives "510" + "1000" = "5101000".
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start

class Solution:
    def concatHex36(self, n: int) -> str:
        """
        Interview explanation:
        Concatenate n^2 in base 16 with n^3 in base 36 (uppercase digits).

        Algorithm:
        - Convert n*n with hex(); convert n**3 via repeated divmod by 36
          using digits 0-9A-Z.

        Complexity: O(log n) time, O(log n) space.
        """
        def to_base(num: int, base: int) -> str:
            if num == 0:
                return "0"
            digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            chars = []
            while num:
                num, r = divmod(num, base)
                chars.append(digits[r])
            return "".join(reversed(chars))

        return format(n * n, "X") + to_base(n * n * n, 36)

    def concatHex36_manual(self, n: int) -> str:
        """
        Interview explanation:
        Alternate: convert both bases with the same divmod helper.

        Algorithm:
        - to_base(n^2, 16) + to_base(n^3, 36).

        Complexity: O(log n) time, O(log n) space.
        """
        def to_base(num: int, base: int) -> str:
            if num == 0:
                return "0"
            digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            chars = []
            while num:
                num, r = divmod(num, base)
                chars.append(digits[r])
            return "".join(reversed(chars))

        return to_base(n * n, 16) + to_base(n * n * n, 36)
# @lc code=end
