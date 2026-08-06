#
# @lc app=leetcode id=3918 lang=python3
#
# [3918] Sum of Primes Between Number and Its Reverse
#
# https://leetcode.com/problems/sum-of-primes-between-number-and-its-reverse/description/
#
# algorithms
# Medium (76.37%)
# Likes:    33
# Dislikes: 3
# Total Accepted:    40.7K
# Total Submissions: 53.3K
# Testcase Example:  "13"
#
#
# You are given an integer n.
#
# Let r be the integer formed by reversing the digits of n.
#
# Return the sum of all prime numbers between min(n, r) and max(n, r),
# inclusive.
#
# Example 1:
#
# Input: n = 13
#
# Output: 132
#
# Explanation:
#
# The reverse of 13 is 31. Thus, the range is [13, 31].
#
# The prime numbers in this range are 13, 17, 19, 23, 29, and 31.
#
# The sum of these prime numbers is 13 + 17 + 19 + 23 + 29 + 31 = 132.
#
# Example 2:
#
# Input: n = 10
#
# Output: 17
#
# Explanation:
#
# The reverse of 10 is 1. Thus, the range is [1, 10].
#
# The prime numbers in this range are 2, 3, 5, and 7.
#
# The sum of these prime numbers is 2 + 3 + 5 + 7 = 17.
#
# Example 3:
#
# Input: n = 8
#
# Output: 0
#
# Explanation:
#
# The reverse of 8 is 8. Thus, the range is [8, 8].
#
# There are no prime numbers in this range, so the sum is 0.
#
# Constraints:
#
# 1 <= n <= 1000
#

# @lc code=start
class Solution:
    def sumOfPrimesInRange(self, n: int) -> int:
        """
        Interview explanation:
        Sum primes between n and reverse(n), inclusive.

        Algorithm:
        - Reverse digits; take [min, max] of the two.
        - Sieve primes up to the high end; prefix-sum primes and range-query.

        Complexity: O(R log log R) time for R = max(n, rev), O(R) space.
        """
        reversed_n = int(str(n)[::-1])
        left = min(n, reversed_n)
        right = max(n, reversed_n)

        is_prime = self._sieve(right)
        prefix = [0] * (right + 1)

        for value in range(1, right + 1):
            prefix[value] = prefix[value - 1] + (value if is_prime[value] else 0)

        return prefix[right] - (prefix[left - 1] if left > 0 else 0)

    def _sieve(self, limit: int) -> list[bool]:
        if limit < 2:
            return [False] * (limit + 1)

        is_prime = [True] * (limit + 1)
        is_prime[0] = False
        is_prime[1] = False

        p = 2
        while p * p <= limit:
            if is_prime[p]:
                for multiple in range(p * p, limit + 1, p):
                    is_prime[multiple] = False
            p += 1

        return is_prime
# @lc code=end
