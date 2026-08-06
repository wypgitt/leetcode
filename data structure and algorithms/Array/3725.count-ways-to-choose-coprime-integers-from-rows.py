#
# @lc app=leetcode id=3725 lang=python3
#
# [3725] Count Ways to Choose Coprime Integers from Rows
#
# https://leetcode.com/problems/count-ways-to-choose-coprime-integers-from-rows/description/
#
# algorithms
# Hard (48.67%)
# Likes:    68
# Dislikes: 4
# Total Accepted:    10.1K
# Total Submissions: 20.8K
# Testcase Example:  "[[1,2],[3,4]]"
#
#
# You are given a m x n matrix mat of positive integers.
#
# Return an integer denoting the number of ways to choose exactly one
# integer from each row of mat such that the greatest common divisor of
# all chosen integers is 1.
#
# Since the answer may be very large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: mat = [[1,2],[3,4]]
#
# Output: 3
#
# Explanation:
#
#                         Chosen integer in the first row
#                         Chosen integer in the second row
#                         Greatest common divisor of chosen integers
#
#                         1
#                         3
#                         1
#
#                         1
#                         4
#                         1
#
#                         2
#                         3
#                         1
#
#                         2
#                         4
#                         2
#
# 3 of these combinations have a greatest common divisor of 1. Therefore,
# the answer is 3.
#
# Example 2:
#
# Input: mat = [[2,2],[2,2]]
#
# Output: 0
#
# Explanation:
#
# Every combination has a greatest common divisor of 2. Therefore, the
# answer is 0.
#
# Constraints:
#
# 1 <= m == mat.length <= 150
#
# 1 <= n == mat[i].length <= 150
#
# 1 <= mat[i][j] <= 150
#

# @lc code=start
from collections import defaultdict
from math import gcd
from typing import List


class Solution:
    def countCoprime(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        DP over the running GCD of chosen values. After all rows, answer is
        ways to finish with gcd == 1.

        Algorithm:
        - dp[g] = ways to have current gcd g (start with dp[0] = 1 sentinel).
        - For each row value x and prior g, add ways into gcd(g, x).

        Complexity: O(m * n * R * log R) time with R = max value (<= 150),
        O(R) space.
        """
        MOD = 10**9 + 7
        dp = {0: 1}
        for row in mat:
            nxt = defaultdict(int)
            for x in row:
                for g, ways in dp.items():
                    ng = gcd(g, x)
                    nxt[ng] = (nxt[ng] + ways) % MOD
            dp = nxt
        return dp.get(1, 0)

    def countCoprime_mobius(self, mat: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate: for each d, count ways where d divides every chosen value,
        then Mobius-invert to get gcd == 1.

        Algorithm:
        - freq multiples per row; multiply across rows for each d.
        - ans = sum mu[d] * ways_divisible_by_d.

        Complexity: O(R log R + m * (n + R log R)) time, O(R) space.
        """
        MOD = 10**9 + 7
        mx = max(max(row) for row in mat)
        spf = list(range(mx + 1))
        primes = []
        for i in range(2, mx + 1):
            if spf[i] == i:
                primes.append(i)
            for p in primes:
                if i * p > mx or p > spf[i]:
                    break
                spf[i * p] = p
        mu = [0] * (mx + 1)
        mu[1] = 1
        for i in range(2, mx + 1):
            if spf[i // spf[i]] == spf[i]:
                mu[i] = 0
            else:
                mu[i] = -mu[i // spf[i]]
        ways = [1] * (mx + 1)
        for row in mat:
            cnt = [0] * (mx + 1)
            for x in row:
                cnt[x] += 1
            for d in range(1, mx + 1):
                total = sum(cnt[j] for j in range(d, mx + 1, d))
                ways[d] = ways[d] * total % MOD
        return sum(ways[d] * mu[d] for d in range(1, mx + 1)) % MOD
# @lc code=end

