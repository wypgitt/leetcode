#
# @lc app=leetcode id=3610 lang=python3
#
# [3610] Minimum Number of Primes to Sum to Target
#
# https://leetcode.com/problems/minimum-number-of-primes-to-sum-to-target/description/
#
# algorithms
# Medium (59.88%)
# Likes:    16
# Dislikes: 1
# Total Accepted:    3.5K
# Total Submissions: 5.9K
# Testcase Example:  "10\n2"
#
#
# You are given two integers n and m.
#
# You have to select a multiset of prime numbers from the first m prime
# numbers such that the sum of the selected primes is exactly n. You may
# use each prime number multiple times.
#
# Return the minimum number of prime numbers needed to sum up to n, or -1
# if it is not possible.
#
# Example 1:
#
# Input: n = 10, m = 2
#
# Output: 4
#
# Explanation:
#
# The first 2 primes are [2, 3]. The sum 10 can be formed as 2 + 2 + 3 +
# 3, requiring 4 primes.
#
# Example 2:
#
# Input: n = 15, m = 5
#
# Output: 3
#
# Explanation:
#
# The first 5 primes are [2, 3, 5, 7, 11]. The sum 15 can be formed as 5 +
# 5 + 5, requiring 3 primes.
#
# Example 3:
#
# Input: n = 7, m = 6
#
# Output: 1
#
# Explanation:
#
# The first 6 primes are [2, 3, 5, 7, 11, 13]. The sum 7 can be formed
# directly by prime 7, requiring only 1 prime.
#
# Constraints:
#
# 1 <= n <= 1000
#
# 1 <= m <= 1000
#

# @lc code=start

from typing import List


class Solution:
    def minNumberOfPrimes(self, n: int, m: int) -> int:
        """
        Interview explanation:
        Unbounded knapsack / coin change: form sum n using the first m primes,
        minimize count (each prime reusable).

        Algorithm:
        - Sieve enough primes; DP[x] = min coins for sum x.

        Complexity: O(P log log P + m·n) time, O(n + P) space.
        """
        limit = max(2000, n + 10)
        is_prime = [True] * (limit + 1)
        is_prime[0] = is_prime[1] = False
        primes: List[int] = []
        for i in range(2, limit + 1):
            if not is_prime[i]:
                continue
            primes.append(i)
            if len(primes) >= m:
                break
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
        primes = primes[:m]

        INF = 10**9
        dp = [INF] * (n + 1)
        dp[0] = 0
        for p in primes:
            for x in range(p, n + 1):
                if dp[x - p] + 1 < dp[x]:
                    dp[x] = dp[x - p] + 1
        return dp[n] if dp[n] < INF else -1
# @lc code=end
