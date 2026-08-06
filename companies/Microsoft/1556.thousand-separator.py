#
# @lc app=leetcode id=1556 lang=python3
#
# [1556] Thousand Separator
#
# https://leetcode.com/problems/thousand-separator/description/
#
# algorithms
# Easy (53.8%)
# Likes:    523
# Dislikes: 48
# Total Accepted:    69.9K
# Total Submissions: 130K
# Testcase Example:  "987"
#
# Given an integer n, add a dot (".") as the thousands separator and return it
# in string format.
#
# Example 1:
#
# Input: n = 987
# Output: "987"
#
# Example 2:
#
# Input: n = 1234
# Output: "1.234"
#
# Constraints:
#
# 0 <= n <= 2^31 - 1
#

# @lc code=start
class Solution:
    def thousandSeparator(self, n: int) -> str:
        """
        Interview explanation:
        Insert '.' as thousands separator from the right of decimal digits.

        Algorithm (string):
        - s=str(n); from right, group every 3 chars; join with '.'.

        Complexity: O(log n) time/space.
        """
        s = str(n)
        parts = []
        while s:
            parts.append(s[-3:])
            s = s[:-3]
        return ".".join(reversed(parts))

    def thousandSeparator_math(self, n: int) -> str:
        """
        Interview explanation:
        Alternate: peel digits with %10 / //10, insert '.' every 3 digits.

        Algorithm:
        - Build reversed digit string with dots; reverse at end. Handle n==0.

        Complexity: O(log n).
        """
        if n == 0:
            return "0"
        digits = []
        cnt = 0
        while n:
            if cnt and cnt % 3 == 0:
                digits.append(".")
            digits.append(str(n % 10))
            n //= 10
            cnt += 1
        return "".join(reversed(digits))
# @lc code=end

