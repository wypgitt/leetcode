#
# @lc app=leetcode id=625 lang=python3
#
# [625] Minimum Factorization
#
# https://leetcode.com/problems/minimum-factorization/description/
#
# algorithms
# Medium (34.11%)
# Likes:    133
# Dislikes: 112
# Total Accepted:    12.4K
# Total Submissions: 36.3K
# Testcase Example:  "48"
#
#
# Given a positive integer num, return the smallest positive integer x
# whose multiplication of each digit equals num. If there is no answer or
# the answer is not fit in 32-bit signed integer, return 0.
#
# Example 1:
#
# Input: num = 48
# Output: 68
#
# Example 2:
#
# Input: num = 15
# Output: 35
#
# Constraints:
#
# 1 <= num <= 2^31 - 1
#
# @lc code=start

class Solution:
    def smallestFactorization(self, num: int) -> int:
        """
        Interview explanation:
        Premium. Factor num into single digits 9..2 (greedy largest digits) so
        the concatenation of digits in ascending order is the smallest number.
        Return 0 if impossible or result > 2^31-1.

        Algorithm:
        - If num < 10 return num.
        - For d from 9 down to 2: while num % d == 0, append d, num //= d.
        - If num != 1 return 0; else reverse digits to form number; check INT_MAX.

        Complexity: O(log num) factors; O(1) digits (at most ~32).
        """
        if num < 10:
            return num
        digits = []
        for d in range(9, 1, -1):
            while num % d == 0:
                digits.append(d)
                num //= d
        if num != 1:
            return 0
        digits.reverse()
        ans = 0
        for d in digits:
            ans = ans * 10 + d
            if ans > 2**31 - 1:
                return 0
        return ans
# @lc code=end
