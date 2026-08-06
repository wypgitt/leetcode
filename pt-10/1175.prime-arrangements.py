#
# @lc app=leetcode id=1175 lang=python3
#
# [1175] Prime Arrangements
#
# https://leetcode.com/problems/prime-arrangements/description/
#
# algorithms
# Easy (61.74%)
# Likes:    451
# Dislikes: 539
# Total Accepted:    46.3K
# Total Submissions: 75.0K
# Testcase Example:  "5"
#
# Return the number of permutations of 1 to n so that prime numbers are at
# prime indices (1-indexed.)
#
# (Recall that an integer is prime if and only if it is greater than 1, and
# cannot be written as a product of two positive integers both smaller than
# it.)
#
# Since the answer may be large, return the answer modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 5
# Output: 12
# Explanation: For example [1,2,5,4,3] is a valid permutation, but [5,2,3,4,1]
# is not because the prime number 5 is at index 1.
#
# Example 2:
#
# Input: n = 100
# Output: 682289015
#
# Constraints:
#
# 1 <= n <= 100
#

# @lc code=start

import math


class Solution:
    def numPrimeArrangements(self, n: int) -> int:
        """
        Interview explanation:
        Primes must occupy prime indices (1-indexed). Count primes in 1..n as p;
        non-primes = n-p. Answer is p! * (n-p)! mod 10^9+7 (permutations within
        each group of indices).

        Algorithm:
        - Sieve or trial division to count primes ≤ n.
        - Return factorial(p) * factorial(n-p) % MOD.

        Complexity: O(n log log n) sieve or O(n√n) trial; O(n) space for sieve.
        """
        MOD = 10**9 + 7

        def count_primes(m: int) -> int:
            if m < 2:
                return 0
            is_prime = [True] * (m + 1)
            is_prime[0] = is_prime[1] = False
            for i in range(2, int(m**0.5) + 1):
                if is_prime[i]:
                    for j in range(i * i, m + 1, i):
                        is_prime[j] = False
            return sum(is_prime)

        p = count_primes(n)
        return (math.factorial(p) * math.factorial(n - p)) % MOD
# @lc code=end
