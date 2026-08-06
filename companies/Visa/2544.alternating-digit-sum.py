#
# @lc app=leetcode id=2544 lang=python3
#
# [2544] Alternating Digit Sum
#
# https://leetcode.com/problems/alternating-digit-sum/description/
#
# algorithms
# Easy (69.52%)
# Likes:    503
# Dislikes: 23
# Total Accepted:    113K
# Total Submissions: 162.5K
# Testcase Example:  "521"
#
# You are given a positive integer n. Each digit of n has a sign according to
# the following rules:
#
#
# The most significant digit is assigned a positive sign.
#
#
# Each other digit has an opposite sign to its adjacent digits.
#
# Return the sum of all digits with their corresponding sign.
#
#
#
# Example 1:
#
# Input: n = 521
# Output: 4
# Explanation: (+5) + (-2) + (+1) = 4.
#
# Example 2:
#
# Input: n = 111
# Output: 1
# Explanation: (+1) + (-1) + (+1) = 1.
#
# Example 3:
#
# Input: n = 886996
# Output: 0
# Explanation: (+8) + (-8) + (+6) + (-9) + (+9) + (-6) = 0.
#
#
#
# Constraints:
#
#
# 1 <= n <= 10^9
#

# @lc code=start
class Solution:
    def alternateDigitSum(self, n: int) -> int:
        """
        Interview explanation:
        Digits of n alternate + - starting with + on the most significant digit.

        Algorithm:
        - Walk digit string left-to-right with sign flipping each step.

        Complexity: O(log n) time, O(log n) space for digits.
        """
        s = str(n)
        ans = 0
        sign = 1
        for ch in s:
            ans += sign * int(ch)
            sign = -sign
        return ans

    def alternateDigitSum_math(self, n: int) -> int:
        """
        Interview explanation:
        Classic alternate: peel digits from the right, then flip overall sign
        if digit count is even so MSD is positive.

        Algorithm:
        - Extract digits LSB-first with alternating signs; if even length, negate.

        Complexity: O(log n) time, O(1) space.
        """
        ans = 0
        sign = 1
        digits = 0
        x = n
        while x:
            ans += sign * (x % 10)
            sign = -sign
            x //= 10
            digits += 1
        return -ans if digits % 2 == 0 else ans
# @lc code=end
