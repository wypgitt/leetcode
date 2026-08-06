#
# @lc app=leetcode id=2521 lang=python3
#
# [2521] Distinct Prime Factors of Product of Array
#
# https://leetcode.com/problems/distinct-prime-factors-of-product-of-array/description/
#
# algorithms
# Medium (55.01%)
# Likes:    554
# Dislikes: 14
# Total Accepted:    51.3K
# Total Submissions: 93.2K
# Testcase Example:  "[2,4,3,7,10,6]"
#
# Given an array of positive integers nums, return the number of distinct prime
# factors in the product of the elements of nums.
#
# Note that:
#
#
# A number greater than 1 is called prime if it is divisible by only 1 and
# itself.
#
#
# An integer val1 is a factor of another integer val2 if val2 / val1 is an
# integer.
#
#
#
# Example 1:
#
# Input: nums = [2,4,3,7,10,6]
# Output: 4
# Explanation:
# The product of all the elements in nums is: 2 * 4 * 3 * 7 * 10 * 6 = 10080 =
# 2^5 * 3^2 * 5 * 7.
# There are 4 distinct prime factors so we return 4.
#
# Example 2:
#
# Input: nums = [2,4,8,16]
# Output: 1
# Explanation:
# The product of all the elements in nums is: 2 * 4 * 8 * 16 = 1024 = 2^10.
# There is 1 distinct prime factor so we return 1.
#
#
#
# Constraints:
#
#
# 1 <= nums.length <= 10^4
#
#
# 2 <= nums[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def distinctPrimeFactors(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Count distinct primes dividing the product of nums (union of prime
        factors of each element).

        Algorithm:
        - Trial-divide each nums[i]; insert every prime factor into a set.

        Complexity: O(n * sqrt(M)) time, O(π(M)) space (M = max nums[i]).
        """
        primes: set[int] = set()
        for x in nums:
            d = 2
            while d * d <= x:
                if x % d == 0:
                    primes.add(d)
                    while x % d == 0:
                        x //= d
                d += 1
            if x > 1:
                primes.add(x)
        return len(primes)

    def distinctPrimeFactors_spf(self, nums: List[int]) -> int:
        """
        Interview explanation:
        Same distinct-prime-of-product count via smallest-prime-factor sieve.

        Algorithm:
        - Build SPF up to max(nums); factor each value via SPF table.

        Complexity: O(M log log M + n log M) time, O(M) space.
        """
        m = max(nums)
        spf = list(range(m + 1))
        for i in range(2, int(m**0.5) + 1):
            if spf[i] == i:
                for j in range(i * i, m + 1, i):
                    if spf[j] == j:
                        spf[j] = i
        primes: set[int] = set()
        for x in nums:
            while x > 1:
                p = spf[x]
                primes.add(p)
                while x % p == 0:
                    x //= p
        return len(primes)
# @lc code=end
