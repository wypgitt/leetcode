#
# @lc app=leetcode id=1735 lang=python3
#
# [1735] Count Ways to Make Array With Product
#
# https://leetcode.com/problems/count-ways-to-make-array-with-product/description/
#
# algorithms
# Hard (55.29%)
# Likes:    325
# Dislikes: 36
# Total Accepted:    10.2K
# Total Submissions: 18.4K
# Testcase Example:  "[[2,6],[5,1],[73,660]]"
#
# You are given a 2D integer array, queries. For each queries[i], where
# queries[i] = [n_i, k_i], find the number of different ways you can place
# positive integers into an array of size n_i such that the product of the
# integers is k_i. As the number of ways may be too large, the answer to the
# i^th query is the number of ways modulo 10^9 + 7.
#
# Return an integer array answer where answer.length == queries.length, and
# answer[i] is the answer to the i^th query.
#
# Example 1:
#
# Input: queries = [[2,6],[5,1],[73,660]]
# Output: [4,1,50734910]
# Explanation: Each query is independent.
# [2,6]: There are 4 ways to fill an array of size 2 that multiply to 6: [1,6],
# [2,3], [3,2], [6,1].
# [5,1]: There is 1 way to fill an array of size 5 that multiply to 1:
# [1,1,1,1,1].
# [73,660]: There are 1050734917 ways to fill an array of size 73 that multiply
# to 660. 1050734917 modulo 10^9 + 7 = 50734910.
#
# Example 2:
#
# Input: queries = [[1,1],[2,2],[3,3],[4,4],[5,5]]
# Output: [1,2,3,10,5]
#
# Constraints:
#
# 1 <= queries.length <= 10^4
#
# 1 <= n_i, k_i <= 10^4
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def waysToFillArray(self, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For (n,k): ways to fill length-n array with product k. Factorize k; for
        each prime power p^e distribute e identical items into n bins: C(e+n-1, e).

        Algorithm:
        - Precompute factorials/inverses; factorize each k; multiply combinations.

        Complexity: O(Q*sqrt(K) + N log MOD) with precompute.
        """
        MOD = 10**9 + 7
        MAXN = 10**4 + 64
        fac = [1] * (MAXN + 1)
        for i in range(1, MAXN + 1):
            fac[i] = fac[i - 1] * i % MOD
        inv = [1] * (MAXN + 1)
        inv[MAXN] = pow(fac[MAXN], MOD - 2, MOD)
        for i in range(MAXN, 0, -1):
            inv[i - 1] = inv[i] * i % MOD

        def comb(n: int, k: int) -> int:
            if k < 0 or k > n:
                return 0
            return fac[n] * inv[k] % MOD * inv[n - k] % MOD

        def factorize(x: int) -> Counter:
            cnt: Counter = Counter()
            d = 2
            while d * d <= x:
                while x % d == 0:
                    cnt[d] += 1
                    x //= d
                d += 1
            if x > 1:
                cnt[x] += 1
            return cnt

        ans = []
        for n, k in queries:
            ways = 1
            for e in factorize(k).values():
                ways = ways * comb(e + n - 1, e) % MOD
            ans.append(ways)
        return ans
# @lc code=end
