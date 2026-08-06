#
# @lc app=leetcode id=1952 lang=python3
#
# [1952] Three Divisors
#
# https://leetcode.com/problems/three-divisors/description/
#
# algorithms
# Easy (64.63%)
# Likes:    647
# Dislikes: 37
# Total Accepted:    148K
# Total Submissions: 228K
# Testcase Example:  "2"
#
# Given an integer n, return true if n has exactly three positive divisors.
# Otherwise, return false.
#
# An integer m is a divisor of n if there exists an integer k such that n = k *
# m.
#
# Example 1:
#
# Input: n = 2
# Output: false
# Explantion: 2 has only two divisors: 1 and 2.
#
# Example 2:
#
# Input: n = 4
# Output: true
# Explantion: 4 has three divisors: 1, 2, and 4.
#
# Constraints:
#
# 1 <= n <= 10^4
#

# @lc code=start
import math


class Solution:
    def isThree(self, n: int) -> bool:
        """
        Interview explanation:
        Exactly 3 positive divisors iff n = p^2 for prime p (divisors 1, p, p^2).

        Algorithm:
        - Let r = isqrt(n); require r*r == n and r is prime.

        Complexity: O(sqrt(n)) time, O(1) space.
        """
        r = int(math.isqrt(n))
        if r * r != n or r < 2:
            return False
        i = 2
        while i * i <= r:
            if r % i == 0:
                return False
            i += 1
        return True

    def isThree_count(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: count divisors by trial division up to sqrt(n).

        Algorithm:
        - Enumerate d|n; return whether count == 3.

        Complexity: O(sqrt(n)) time, O(1) space.
        """
        cnt = 0
        d = 1
        while d * d <= n:
            if n % d == 0:
                cnt += 1 if d * d == n else 2
                if cnt > 3:
                    return False
            d += 1
        return cnt == 3
# @lc code=end

