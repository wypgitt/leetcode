#
# @lc app=leetcode id=3233 lang=python3
#
# [3233] Find the Count of Numbers Which Are Not Special
#
# https://leetcode.com/problems/find-the-count-of-numbers-which-are-not-special/description/
#
# algorithms
# Medium (28.33%)
# Likes:    204
# Dislikes: 28
# Total Accepted:    39.9K
# Total Submissions: 140.8K
# Testcase Example:  "5\n7"
#
#
# You are given 2 positive integers l and r. For any number x, all
# positive divisors of x except x are called the proper divisors of x.
#
# A number is called special if it has exactly 2 proper divisors. For
# example:
#
# The number 4 is special because it has proper divisors 1 and 2.
#
# The number 6 is not special because it has proper divisors 1, 2, and 3.
#
# Return the count of numbers in the range [l, r] that are not special.
#
# Example 1:
#
# Input: l = 5, r = 7
#
# Output: 3
#
# Explanation:
#
# There are no special numbers in the range [5, 7].
#
# Example 2:
#
# Input: l = 4, r = 16
#
# Output: 11
#
# Explanation:
#
# The special numbers in the range [4, 16] are 4 and 9.
#
# Constraints:
#
# 1 <= l <= r <= 10^9
#

# @lc code=start
import math


class Solution:
    def nonSpecialCount(self, l: int, r: int) -> int:
        """
        Interview explanation:
        Special numbers have exactly two proper divisors <=> exactly three
        divisors total <=> squares of primes. Count non-special = range size
        minus prime squares in [l, r].

        Algorithm:
        - Sieve primes up to floor(sqrt(r)).
        - Count p^2 in [l, r]; return (r - l + 1) - that count.

        Complexity: O(sqrt(r) log log sqrt(r)) time, O(sqrt(r)) space.
        Alternate: Miller-Rabin primality for each candidate square root.
        """
        def count_prime_squares(limit: int) -> int:
            if limit < 4:
                return 0
            m = int(math.isqrt(limit))
            is_prime = [True] * (m + 1)
            is_prime[0] = is_prime[1] = False
            for i in range(2, int(math.isqrt(m)) + 1):
                if is_prime[i]:
                    step = i
                    start = i * i
                    is_prime[start : m + 1 : step] = [False] * (((m - start) // step) + 1)
            return sum(1 for p in range(2, m + 1) if is_prime[p] and p * p <= limit)

        return (r - l + 1) - (count_prime_squares(r) - count_prime_squares(l - 1))

# @lc code=end
