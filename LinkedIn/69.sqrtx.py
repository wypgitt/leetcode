#
# @lc app=leetcode id=69 lang=python3
#
# [69] Sqrt(x)
#
# https://leetcode.com/problems/sqrtx/description/
#
# algorithms
# Easy (42.2%)
# Likes:    9855
# Dislikes: 4649
# Total Accepted:    3.4M
# Total Submissions: 8.0M
# Testcase Example:  "4"
#
# Given a non-negative integer x, return the square root of x rounded down to
# the nearest integer. The returned integer should be non-negative as well.
#
# You must not use any built-in exponent function or operator.
#
# For example, do not use pow(x, 0.5) in c++ or x ** 0.5 in python.
#
# Example 1:
#
# Input: x = 4
# Output: 2
# Explanation: The square root of 4 is 2, so we return 2.
#
# Example 2:
#
# Input: x = 8
# Output: 2
# Explanation: The square root of 8 is 2.82842..., and since we round it down
# to the nearest integer, 2 is returned.
#
# Constraints:
#
# 0 <= x <= 2^31 - 1
#

# @lc code=start
class Solution:
    def mySqrt(self, x: int) -> int:
        """
        Interview explanation:
        Find the greatest integer r such that r*r <= x (floor square root)
        without floating-point builtins.

        Algorithm:
        - Search for r in [1, x // 2] (handle x < 2 directly).
        - mid = (lo + hi + 1) // 2 using upper mid to avoid infinite loops when
          searching for the rightmost feasible value.
        - If mid*mid <= x, mid is feasible -> lo = mid; else hi = mid - 1.
        - Return lo.

        Complexity: O(log x) time, O(1) space.
        """
        if x < 2:
            return x

        lo, hi = 1, x // 2
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if mid * mid <= x:
                lo = mid
            else:
                hi = mid - 1
        return lo
# @lc code=end
