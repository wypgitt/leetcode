#
# @lc app=leetcode id=1808 lang=python3
#
# [1808] Maximize Number of Nice Divisors
#
# https://leetcode.com/problems/maximize-number-of-nice-divisors/description/
#
# algorithms
# Hard (36.79%)
# Likes:    235
# Dislikes: 173
# Total Accepted:    11.0K
# Total Submissions: 29.9K
# Testcase Example:  "5"
#
# You are given a positive integer primeFactors. You are asked to construct a
# positive integer n that satisfies the following conditions:
#
# The number of prime factors of n (not necessarily distinct) is at most
# primeFactors.
#
# The number of nice divisors of n is maximized. Note that a divisor of n is
# nice if it is divisible by every prime factor of n. For example, if n = 12,
# then its prime factors are [2,2,3], then 6 and 12 are nice divisors, while 3
# and 4 are not.
#
# Return the number of nice divisors of n. Since that number can be too large,
# return it modulo 10^9 + 7.
#
# Note that a prime number is a natural number greater than 1 that is not a
# product of two smaller natural numbers. The prime factors of a number n is a
# list of prime numbers such that their product equals n.
#
# Example 1:
#
# Input: primeFactors = 5
# Output: 6
# Explanation: 200 is a valid value of n.
# It has 5 prime factors: [2,2,2,5,5], and it has 6 nice divisors:
# [10,20,40,50,100,200].
# There is not other value of n that has at most 5 prime factors and more nice
# divisors.
#
# Example 2:
#
# Input: primeFactors = 8
# Output: 18
#
# Constraints:
#
# 1 <= primeFactors <= 10^9
#

# @lc code=start
class Solution:
    def maxNiceDivisors(self, primeFactors: int) -> int:
        """
        Interview explanation:
        Maximize product of parts summing to primeFactors (integer break with
        factors of 2/3). Prefer 3's; avoid leaving remainder 1 (use 2+2).

        Algorithm (math break-into-3s):
        - If n<=3 return n; else pow(3, n//3) * adjust for n%3; mod 10^9+7.

        Complexity: O(log n) time, O(1) space.
        """
        MOD = 10**9 + 7
        n = primeFactors
        if n <= 3:
            return n
        q, r = divmod(n, 3)
        if r == 0:
            return pow(3, q, MOD)
        if r == 1:
            return pow(3, q - 1, MOD) * 4 % MOD
        return pow(3, q, MOD) * 2 % MOD
# @lc code=end
