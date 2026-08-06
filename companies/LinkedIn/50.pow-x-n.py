#
# @lc app=leetcode id=50 lang=python3
#
# [50] Pow(x, n)
#
# https://leetcode.com/problems/powx-n/description/
#
# algorithms
# Medium (38.61%)
# Likes:    11727
# Dislikes: 10557
# Total Accepted:    2.7M
# Total Submissions: 7M
# Testcase Example:  '2.00000\n10'
#
# Implement pow(x, n), which calculates x raised to the power n (i.e., x^n).
# 
# 
# Example 1:
# 
# 
# Input: x = 2.00000, n = 10
# Output: 1024.00000
# 
# 
# Example 2:
# 
# 
# Input: x = 2.10000, n = 3
# Output: 9.26100
# 
# 
# Example 3:
# 
# 
# Input: x = 2.00000, n = -2
# Output: 0.25000
# Explanation: 2^-2 = 1/2^2 = 1/4 = 0.25
# 
# 
# 
# Constraints:
# 
# 
# -100.0 < x < 100.0
# -2^31 <= n <= 2^31-1
# n is an integer.
# Either x is not zero or n > 0.
# -10^4 <= x^n <= 10^4
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def myPow(self, x: float, n: int) -> float:
        """
        Interview explanation:
        Fast exponentiation uses the binary representation of n. Squaring the
        base each step represents powers x^(1), x^(2), x^(4), ...; when the
        current bit is 1, multiply it into the answer. Negative exponents are
        handled by inverting x and using abs(n).

        Edge cases and tests:
        - n == 0 returns 1.
        - Negative n returns reciprocal power.
        - x == 0 with positive n returns 0 through normal multiplication.

        Complexity: O(log |n|) time, O(1) space.
        """
        if n < 0:
            x = 1 / x
            n = -n

        ans = 1.0
        while n:
            if n & 1:
                ans *= x
            x *= x
            n >>= 1
        return ans
# @lc code=end


