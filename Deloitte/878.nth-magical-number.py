#
# @lc app=leetcode id=878 lang=python3
#
# [878] Nth Magical Number
#
# https://leetcode.com/problems/nth-magical-number/description/
#
# algorithms
# Hard (36.95%)
# Likes:    1350
# Dislikes: 171
# Total Accepted:    52.7K
# Total Submissions: 143K
# Testcase Example:  "1"
#
# A positive integer is magical if it is divisible by either a or b.
#
# Given the three integers n, a, and b, return the n^th magical number. Since
# the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 1, a = 2, b = 3
# Output: 2
#
# Example 2:
#
# Input: n = 4, a = 2, b = 3
# Output: 6
#
# Constraints:
#
# 1 <= n <= 10^9
#
# 2 <= a, b <= 4 * 10^4
#

# @lc code=start
import math


class Solution:
    def nthMagicalNumber(self, n: int, a: int, b: int) -> int:
        """
        Interview explanation:
        Count of magical numbers <= x is x//a + x//b - x//lcm. Binary search
        smallest x with count >= n.

        Algorithm (binary search):
        - lo=min(a,b), hi=n*min(a,b). Mid: if count(mid)>=n: hi=mid else lo=mid+1.
        - Return lo % MOD.

        Complexity: O(log (n*min(a,b))) time, O(1) space.
        """
        MOD = 10**9 + 7
        lcm = a * b // math.gcd(a, b)
        lo, hi = min(a, b), n * min(a, b)
        while lo < hi:
            mid = (lo + hi) // 2
            if mid // a + mid // b - mid // lcm >= n:
                hi = mid
            else:
                lo = mid + 1
        return lo % MOD
# @lc code=end

