#
# @lc app=leetcode id=2338 lang=python3
#
# [2338] Count the Number of Ideal Arrays
#
# https://leetcode.com/problems/count-the-number-of-ideal-arrays/description/
#
# algorithms
# Hard (56.91%)
# Likes:    858
# Dislikes: 134
# Total Accepted:    70.9K
# Total Submissions: 124.6K
# Testcase Example:  "2\n5"
#
# You are given two integers n and maxValue, which are used to describe an ideal
# array.
#
# A 0-indexed integer array arr of length n is considered ideal if the following
# conditions hold:
#
#
# Every arr[i] is a value from 1 to maxValue, for 0 <= i < n.
#
#
# Every arr[i] is divisible by arr[i - 1], for 0 < i < n.
#
# Return the number of distinct ideal arrays of length n. Since the answer may
# be very large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: n = 2, maxValue = 5
# Output: 10
# Explanation: The following are the possible ideal arrays:
# - Arrays starting with the value 1 (5 arrays): [1,1], [1,2], [1,3], [1,4],
# [1,5]
# - Arrays starting with the value 2 (2 arrays): [2,2], [2,4]
# - Arrays starting with the value 3 (1 array): [3,3]
# - Arrays starting with the value 4 (1 array): [4,4]
# - Arrays starting with the value 5 (1 array): [5,5]
# There are a total of 5 + 2 + 1 + 1 + 1 = 10 distinct ideal arrays.
#
# Example 2:
#
# Input: n = 5, maxValue = 3
# Output: 11
# Explanation: The following are the possible ideal arrays:
# - Arrays starting with the value 1 (9 arrays):
#    - With no other distinct values (1 array): [1,1,1,1,1]
#    - With 2^nd distinct value 2 (4 arrays): [1,1,1,1,2], [1,1,1,2,2],
# [1,1,2,2,2], [1,2,2,2,2]
#    - With 2^nd distinct value 3 (4 arrays): [1,1,1,1,3], [1,1,1,3,3],
# [1,1,3,3,3], [1,3,3,3,3]
# - Arrays starting with the value 2 (1 array): [2,2,2,2,2]
# - Arrays starting with the value 3 (1 array): [3,3,3,3,3]
# There are a total of 9 + 1 + 1 = 11 distinct ideal arrays.
#
#
#
# Constraints:
#
#
# 2 <= n <= 10^4
#
#
# 1 <= maxValue <= 10^4
#

# @lc code=start
class Solution:
    def idealArrays(self, n: int, maxValue: int) -> int:
        """
        Interview explanation:
        Count length-n arrays with values in 1..maxValue where each element
        divides the next (ideal arrays), mod 1e9+7.

        Algorithm:
        - For each last value x, factorize; each prime exponent e contributes
          C(e + n - 1, e) ways (stars-and-bars). Sum products over all x.

        Complexity: O(maxValue log maxValue) time, O(n + maxValue) space.
        """
        MOD = 10**9 + 7
        # spf sieve
        spf = list(range(maxValue + 1))
        for i in range(2, int(maxValue**0.5) + 1):
            if spf[i] == i:
                for j in range(i * i, maxValue + 1, i):
                    if spf[j] == j:
                        spf[j] = i

        # precompute factorials for C(n-1+e, e) with e up to ~20 (2^20>1e4? maxValue 1e4, max exp ~13 for 2)
        # n up to 1e4, so need C up to n-1+14
        N = n + 20
        fact = [1] * (N + 1)
        for i in range(1, N + 1):
            fact[i] = fact[i - 1] * i % MOD
        invfact = [1] * (N + 1)
        invfact[N] = pow(fact[N], MOD - 2, MOD)
        for i in range(N, 0, -1):
            invfact[i - 1] = invfact[i] * i % MOD

        def C(a: int, b: int) -> int:
            if b < 0 or b > a:
                return 0
            return fact[a] * invfact[b] % MOD * invfact[a - b] % MOD

        ans = 0
        for x in range(1, maxValue + 1):
            ways = 1
            y = x
            while y > 1:
                p = spf[y]
                e = 0
                while y % p == 0:
                    y //= p
                    e += 1
                # distribute e indistinguishable increments into n positions
                # as nondecreasing exponents: C(e + n - 1, e)
                ways = ways * C(e + n - 1, e) % MOD
            ans = (ans + ways) % MOD
        return ans

    def idealArrays_math(self, n: int, maxValue: int) -> int:
        """
        Interview explanation:
        Combinatorics on prime exponents (same as primary).

        Algorithm:
        - Factor each value; multiply stars-and-bars; sum.

        Complexity: O(maxValue log maxValue) time.
        """
        return self.idealArrays(n, maxValue)
# @lc code=end
