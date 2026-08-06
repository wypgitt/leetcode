#
# @lc app=leetcode id=2478 lang=python3
#
# [2478] Number of Beautiful Partitions
#
# https://leetcode.com/problems/number-of-beautiful-partitions/description/
#
# algorithms
# Hard (33.26%)
# Likes:    373
# Dislikes: 19
# Total Accepted:    13.8K
# Total Submissions: 41.6K
# Testcase Example:  "\"23542185131\"\n3\n2"
#
# You are given a string s that consists of the digits '1' to '9' and two
# integers k and minLength.
#
# A partition of s is called beautiful if:
#
#
# s is partitioned into k non-intersecting substrings.
#
#
# Each substring has a length of at least minLength.
#
#
# Each substring starts with a prime digit and ends with a non-prime digit.
# Prime digits are '2', '3', '5', and '7', and the rest of the digits are
# non-prime.
#
# Return the number of beautiful partitions of s. Since the answer may be very
# large, return it modulo 10^9 + 7.
#
# A substring is a contiguous sequence of characters within a string.
#
#
#
# Example 1:
#
# Input: s = "23542185131", k = 3, minLength = 2
# Output: 3
# Explanation: There exists three ways to create a beautiful partition:
# "2354 | 218 | 5131"
# "2354 | 21851 | 31"
# "2354218 | 51 | 31"
#
# Example 2:
#
# Input: s = "23542185131", k = 3, minLength = 3
# Output: 1
# Explanation: There exists one way to create a beautiful partition: "2354 | 218
# | 5131".
#
# Example 3:
#
# Input: s = "3312958", k = 3, minLength = 1
# Output: 1
# Explanation: There exists one way to create a beautiful partition: "331 | 29 |
# 58".
#
#
#
# Constraints:
#
#
# 1 <= k, minLength <= s.length <= 1000
#
#
# s consists of the digits '1' to '9'.
#

# @lc code=start
class Solution:
    def beautifulPartitions(self, s: str, k: int, minLength: int) -> int:
        """
        Interview explanation:
        Partition digit string into k beautiful parts: each starts with prime
        digit and ends with non-prime; each length >= minLength.

        Algorithm:
        - DP f[i][j]: ways to split first i chars into j parts. Valid end i if
          s[i-1] non-prime and next starts prime (or end). Prefix sums g speed
          transitions f[i][j]=g[i-minLength][j-1].

        Complexity: O(n k) time, O(n k) space.
        """
        primes = "2357"
        if s[0] not in primes or s[-1] in primes:
            return 0
        mod = 10**9 + 7
        n = len(s)
        f = [[0] * (k + 1) for _ in range(n + 1)]
        g = [[0] * (k + 1) for _ in range(n + 1)]
        f[0][0] = g[0][0] = 1
        for i, c in enumerate(s, 1):
            if i >= minLength and c not in primes and (i == n or s[i] in primes):
                for j in range(1, k + 1):
                    f[i][j] = g[i - minLength][j - 1]
            for j in range(k + 1):
                g[i][j] = (g[i - 1][j] + f[i][j]) % mod
        return f[n][k]

    def beautifulPartitions_dfs(self, s: str, k: int, minLength: int) -> int:
        """
        Interview explanation:
        Alternate memoized DFS over cut positions.

        Algorithm:
        - dfs(i, parts): try beautiful first segment starting at i.

        Complexity: O(k n^2) time, O(k n) space.
        """
        from functools import lru_cache

        MOD = 10**9 + 7
        primes = set("2357")
        n = len(s)
        if s[0] not in primes or s[-1] in primes:
            return 0

        @lru_cache(None)
        def dfs(i: int, parts: int) -> int:
            if parts == 0:
                return 1 if i == n else 0
            if i >= n or s[i] not in primes:
                return 0
            ans = 0
            for j in range(i + minLength - 1, n - (parts - 1) * minLength):
                if s[j] not in primes:
                    ans = (ans + dfs(j + 1, parts - 1)) % MOD
            return ans

        return dfs(0, k)
# @lc code=end

