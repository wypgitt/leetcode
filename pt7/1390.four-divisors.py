#
# @lc app=leetcode id=1390 lang=python3
#
# [1390] Four Divisors
#
# https://leetcode.com/problems/four-divisors/description/
#
# algorithms
# Medium (56.64%)
# Likes:    895
# Dislikes: 223
# Total Accepted:    197.1K
# Total Submissions: 348K
# Testcase Example:  '[21,4,7]'
#
# Given an integer array nums, return the sum of divisors of the integers in
# that array that have exactly four divisors. If there is no such integer in
# the array, return 0.
# 
# 
# Example 1:
# 
# 
# Input: nums = [21,4,7]
# Output: 32
# Explanation: 
# 21 has 4 divisors: 1, 3, 7, 21
# 4 has 3 divisors: 1, 2, 4
# 7 has 2 divisors: 1, 7
# The answer is the sum of divisors of 21 only.
# 
# 
# Example 2:
# 
# 
# Input: nums = [21,21]
# Output: 64
# 
# 
# Example 3:
# 
# 
# Input: nums = [1,2,3,4,5]
# Output: 0
# 
# 
# 
# Constraints:
# 
# 
# 1 <= nums.length <= 10^4
# 1 <= nums[i] <= 10^5
# 
# 
#

# @lc code=start
from __future__ import annotations

from math import isqrt
from typing import List


class Solution:
    def sumFourDivisors(self, nums: List[int]) -> int:
        def divisor_sum_if_four(num: int) -> int:
            count = 0
            total = 0

            for divisor in range(1, isqrt(num) + 1):
                if num % divisor != 0:
                    continue

                other = num // divisor
                if divisor == other:
                    count += 1
                    total += divisor
                else:
                    count += 2
                    total += divisor + other

                if count > 4:
                    return 0

            return total if count == 4 else 0

        return sum(divisor_sum_if_four(num) for num in nums)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# For each number, enumerate divisor pairs up to its square root. Count distinct
# divisors and sum them. If the count is exactly four, add that sum to the
# global answer.
#
# Data structure:
# Only two integers per number are needed: `count` and `total`.
#
# Walkthrough:
# 1. For every divisor `d` up to sqrt(num), check divisibility.
# 2. If `d` divides num, the paired divisor is `num // d`.
# 3. Add one divisor for a perfect-square pair, otherwise add both.
# 4. Stop early if the count exceeds four.
# 5. Return the divisor sum only when the count is exactly four.
#
# Edge cases:
# - Prime numbers have two divisors, so they contribute 0.
# - Perfect squares need care not to double-count the square root.
# - Numbers with more than four divisors can return 0 early.
#
# Complexity:
# - Time: O(n * sqrt(M)), where M is the largest value in `nums`.
# - Space: O(1).
#
# Improvement:
# A number has exactly four divisors iff it is `p^3` for prime p or `p*q` for
# two distinct primes p and q. A sieve can exploit that, but square-root
# enumeration is simpler and sufficient for the constraints.
