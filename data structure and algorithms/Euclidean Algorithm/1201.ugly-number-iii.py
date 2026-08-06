#
# @lc app=leetcode id=1201 lang=python3
#
# [1201] Ugly Number III
#
# https://leetcode.com/problems/ugly-number-iii/description/
#
# algorithms
# Medium (31.78%)
# Likes:    1338
# Dislikes: 520
# Total Accepted:    45.9K
# Total Submissions: 144K
# Testcase Example:  "3"
#
# An ugly number is a positive integer that is divisible by a, b, or c.
#
# Given four integers n, a, b, and c, return the n^th ugly number.
#
# Example 1:
#
# Input: n = 3, a = 2, b = 3, c = 5
# Output: 4
# Explanation: The ugly numbers are 2, 3, 4, 5, 6, 8, 9, 10... The 3^rd is 4.
#
# Example 2:
#
# Input: n = 4, a = 2, b = 3, c = 4
# Output: 6
# Explanation: The ugly numbers are 2, 3, 4, 6, 8, 9, 10, 12... The 4^th is 6.
#
# Example 3:
#
# Input: n = 5, a = 2, b = 11, c = 13
# Output: 10
# Explanation: The ugly numbers are 2, 4, 6, 8, 10, 11, 12, 13... The 5^th is
# 10.
#
# Constraints:
#
# 1 <= n, a, b, c <= 10^9
#
# 1 <= a * b * c <= 10^18
#
# It is guaranteed that the result will be in range [1, 2 * 10^9].
#


# @lc code=start
from math import gcd

class Solution:
    def nthUglyNumber(self, n: int, a: int, b: int, c: int) -> int:
        """
        Interview explanation:
        Count of ugly numbers <= x is inclusion-exclusion of multiples of a,b,c.
        Binary search the minimal x with count(x) >= n. Use LCM via gcd.

        Algorithm:
        - lcm(x,y)=x*y//gcd; count(x)=x//a+x//b+x//c - x//ab - x//ac - x//bc + x//abc
        - Binary search lo=1, hi=2e9; find leftmost with count>=n

        Complexity: O(log(2e9)) time, O(1) space.
        """
        def lcm(x: int, y: int) -> int:
            return x // gcd(x, y) * y

        ab, ac, bc = lcm(a, b), lcm(a, c), lcm(b, c)
        abc = lcm(ab, c)

        def count(x: int) -> int:
            return x // a + x // b + x // c - x // ab - x // ac - x // bc + x // abc

        lo, hi = 1, 2 * 10**9
        while lo < hi:
            mid = (lo + hi) // 2
            if count(mid) >= n:
                hi = mid
            else:
                lo = mid + 1
        return lo
# @lc code=end
