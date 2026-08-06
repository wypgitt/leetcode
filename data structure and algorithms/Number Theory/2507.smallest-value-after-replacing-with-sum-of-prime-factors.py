#
# @lc app=leetcode id=2507 lang=python3
#
# [2507] Smallest Value After Replacing With Sum of Prime Factors
#
# https://leetcode.com/problems/smallest-value-after-replacing-with-sum-of-prime-factors/description/
#
# algorithms
# Medium (50.23%)
# Likes:    471
# Dislikes: 29
# Total Accepted:    34.4K
# Total Submissions: 68.5K
# Testcase Example:  "15"
#
# You are given a positive integer n.
#
# Continuously replace n with the sum of its prime factors.
#
#
# Note that if a prime factor divides n multiple times, it should be included in
# the sum as many times as it divides n.
#
# Return the smallest value n will take on.
#
#
#
# Example 1:
#
# Input: n = 15
# Output: 5
# Explanation: Initially, n = 15.
# 15 = 3 * 5, so replace n with 3 + 5 = 8.
# 8 = 2 * 2 * 2, so replace n with 2 + 2 + 2 = 6.
# 6 = 2 * 3, so replace n with 2 + 3 = 5.
# 5 is the smallest value n will take on.
#
# Example 2:
#
# Input: n = 3
# Output: 3
# Explanation: Initially, n = 3.
# 3 is the smallest value n will take on.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^5
#

# @lc code=start
class Solution:
    def smallestValue(self, n: int) -> int:
        """
        Interview explanation:
        Replace n by the sum of its prime factors (with multiplicity) until the
        value no longer decreases; return that fixed point (a prime or 4...).

        Algorithm:
        - Factorize and sum factors; if sum == n stop (prime), else continue.

        Complexity: O(sqrt(n) * steps) time, O(1) space; steps are tiny.
        """
        def factor_sum(x: int) -> int:
            s = 0
            d = 2
            while d * d <= x:
                while x % d == 0:
                    s += d
                    x //= d
                d += 1
            if x > 1:
                s += x
            return s

        while True:
            nxt = factor_sum(n)
            if nxt == n:
                return n
            n = nxt
# @lc code=end
