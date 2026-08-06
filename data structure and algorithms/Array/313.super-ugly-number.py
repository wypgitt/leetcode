#
# @lc app=leetcode id=313 lang=python3
#
# [313] Super Ugly Number
#
# https://leetcode.com/problems/super-ugly-number/description/
#
# algorithms
# Medium (46.42%)
# Likes:    2305
# Dislikes: 410
# Total Accepted:    166K
# Total Submissions: 357K
# Testcase Example:  "12"
#
# A super ugly number is a positive integer whose prime factors are in the
# array primes.
#
# Given an integer n and an array of integers primes, return the n^th super
# ugly number.
#
# The n^th super ugly number is guaranteed to fit in a 32-bit signed integer.
#
# Example 1:
#
# Input: n = 12, primes = [2,7,13,19]
# Output: 32
# Explanation: [1,2,4,7,8,13,14,16,19,26,28,32] is the sequence of the first 12
# super ugly numbers given primes = [2,7,13,19].
#
# Example 2:
#
# Input: n = 1, primes = [2,3,5]
# Output: 1
# Explanation: 1 has no prime factors, therefore all of its prime factors are
# in the array primes = [2,3,5].
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 1 <= primes.length <= 100
#
# 2 <= primes[i] <= 1000
#
# primes[i] is guaranteed to be a prime number.
#
# All the values of primes are unique and sorted in ascending order.
#

# @lc code=start
from typing import List


class Solution:
    def nthSuperUglyNumber(self, n: int, primes: List[int]) -> int:
        """
        Interview explanation:
        Like ugly number II with a given prime list. Maintain pointers for each
        prime into the DP array; next candidate is min over primes[i]*dp[ptr[i]].

        Algorithm:
        - dp[0] = 1; ptr[i] = 0 for each prime.
        - For each position, take min candidate; advance all pointers that hit it.

        Complexity: O(n * k) time, O(n + k) space.
        """
        dp = [0] * n
        dp[0] = 1
        k = len(primes)
        ptr = [0] * k
        for i in range(1, n):
            nxt = min(primes[j] * dp[ptr[j]] for j in range(k))
            dp[i] = nxt
            for j in range(k):
                if primes[j] * dp[ptr[j]] == nxt:
                    ptr[j] += 1
        return dp[-1]
# @lc code=end

