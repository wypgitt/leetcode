#
# @lc app=leetcode id=2539 lang=python3
#
# [2539] Count the Number of Good Subsequences
#
# https://leetcode.com/problems/count-the-number-of-good-subsequences/description/
#
# algorithms
# Medium (48.39%)
# Likes:    42
# Dislikes: 82
# Total Accepted:    4.2K
# Total Submissions: 8.7K
# Testcase Example:  "\"aabb\""
#
#
# A subsequence of a string is good if it is not empty and the frequency
# of each one of its characters is the same.
#
# Given a string s, return the number of good subsequences of s. Since the
# answer may be too large, return it modulo 10^9 + 7.
#
# A subsequence is a string that can be derived from another string by
# deleting some or no characters without changing the order of the
# remaining characters.
#
# Example 1:
#
# Input: s = "aabb"
# Output: 11
# Explanation: The total number of subsequences is 2^4. There are five
# subsequences which are not good: "aabb", "aabb", "aabb", "aabb", and the
# empty subsequence. Hence, the number of good subsequences is 2^4-5 = 11.
#
# Example 2:
#
# Input: s = "leet"
# Output: 12
# Explanation: There are four subsequences which are not good: "leet",
# "leet", "leet", and the empty subsequence. Hence, the number of good
# subsequences is 2^4-4 = 12.
#
# Example 3:
#
# Input: s = "abcd"
# Output: 15
# Explanation: All of the non-empty subsequences are good subsequences.
# Hence, the number of good subsequences is 2^4-1 = 15.
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of only lowercase English letters.
#
# @lc code=start
from collections import Counter
from math import comb


class Solution:
    def countGoodSubsequences(self, s: str) -> int:
        """
        Interview explanation:
        A non-empty subsequence is good if every character that appears in it
        has the same frequency. Count good subsequences of s modulo 10^9+7.

        Algorithm:
        (Combinatorics)
        - Let cnt[c] be frequency of c. For each possible common frequency f
          from 1..max(cnt): each letter with cnt>=f may contribute C(cnt,f)
          ways to include exactly f copies, or 1 way to omit it.
        - Ways for fixed f: product over letters (C(cnt,f)+1) - 1 (exclude empty).
        - Sum over f.

        Complexity: O(n + F * A * cost(comb)) time with F=max freq, A=#distinct;
        O(A) space. (n <= 10^4, F <= n)
        """
        MOD = 10**9 + 7
        cnt = Counter(s)
        ans = 0
        for f in range(1, max(cnt.values()) + 1):
            ways = 1
            for v in cnt.values():
                if v >= f:
                    ways = ways * (comb(v, f) + 1) % MOD
            ans = (ans + ways - 1) % MOD
        return ans

    def countGoodSubsequences_factorial(self, s: str) -> int:
        """
        Interview explanation:
        Alternate: precompute factorials and modular inverses for C(n,k) mod P.

        Algorithm:
        - Same product formula; comb via fact[n]*invfact[k]*invfact[n-k].

        Complexity: O(n + F * A) time, O(n) space.
        """
        MOD = 10**9 + 7
        cnt = Counter(s)
        m = max(cnt.values())
        fact = [1] * (m + 1)
        for i in range(1, m + 1):
            fact[i] = fact[i - 1] * i % MOD
        invfact = [1] * (m + 1)
        invfact[m] = pow(fact[m], MOD - 2, MOD)
        for i in range(m, 0, -1):
            invfact[i - 1] = invfact[i] * i % MOD

        def C(n: int, k: int) -> int:
            return fact[n] * invfact[k] % MOD * invfact[n - k] % MOD

        ans = 0
        for f in range(1, m + 1):
            ways = 1
            for v in cnt.values():
                if v >= f:
                    ways = ways * (C(v, f) + 1) % MOD
            ans = (ans + ways - 1) % MOD
        return ans
# @lc code=end
