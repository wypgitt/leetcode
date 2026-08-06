#
# @lc app=leetcode id=3754 lang=python3
#
# [3754] Concatenate Non-Zero Digits and Multiply by Sum I
#
# https://leetcode.com/problems/concatenate-non-zero-digits-and-multiply-by-sum-i/description/
#
# algorithms
# Easy (66.16%)
# Likes:    267
# Dislikes: 3
# Total Accepted:    193.6K
# Total Submissions: 292.6K
# Testcase Example:  "10203004"
#
#
# You are given an integer n.
#
# Form a new integer x by concatenating all the non-zero digits of n in
# their original order. If there are no non-zero digits, x = 0.
#
# Let sum be the sum of digits in x.
#
# Return an integer representing the value of x * sum.
#
# Example 1:
#
# Input: n = 10203004
#
# Output: 12340
#
# Explanation:
#
# The non-zero digits are 1, 2, 3, and 4. Thus, x = 1234.
#
# The sum of digits is sum = 1 + 2 + 3 + 4 = 10.
#
# Therefore, the answer is x * sum = 1234 * 10 = 12340.
#
# Example 2:
#
# Input: n = 1000
#
# Output: 1
#
# Explanation:
#
# The non-zero digit is 1, so x = 1 and sum = 1.
#
# Therefore, the answer is x * sum = 1 * 1 = 1.
#
# Constraints:
#
# 0 <= n <= 10^9
#

# @lc code=start
class Solution:
    def sumAndMultiply(self, n: int) -> int:
        """
        Interview explanation:
        Build x from non-zero digits of n (or 0), then return x * digit_sum(x).

        Algorithm:
        - Scan digits; accumulate x and sum, skipping zeros.

        Complexity: O(log n) time, O(1) space.
        """
        if n == 0:
            return 0
        x = digit_sum = 0
        for ch in str(n):
            if ch != "0":
                d = ord(ch) - 48
                x = x * 10 + d
                digit_sum += d
        return x * digit_sum

    def sumAndMultiply_math(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: extract digits arithmetically from least significant first,
        then rebuild x in original order via a stack/list.

        Algorithm:
        - Collect non-zero digits LSB-first; reverse to form x and sum.

        Complexity: O(log n) time, O(log n) space.
        """
        if n == 0:
            return 0
        digits = []
        while n:
            n, r = divmod(n, 10)
            if r:
                digits.append(r)
        digits.reverse()
        x = digit_sum = 0
        for d in digits:
            x = x * 10 + d
            digit_sum += d
        return x * digit_sum
# @lc code=end
