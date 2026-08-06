#
# @lc app=leetcode id=2514 lang=python3
#
# [2514] Count Anagrams
#
# https://leetcode.com/problems/count-anagrams/description/
#
# algorithms
# Hard (38.09%)
# Likes:    488
# Dislikes: 45
# Total Accepted:    22K
# Total Submissions: 57.7K
# Testcase Example:  "\"too hot\""
#
# You are given a string s containing one or more words. Every consecutive pair
# of words is separated by a single space ' '.
#
# A string t is an anagram of string s if the i^th word of t is a permutation of
# the i^th word of s.
#
#
# For example, "acb dfe" is an anagram of "abc def", but "def cab" and "adc bef"
# are not.
#
# Return the number of distinct anagrams of s. Since the answer may be very
# large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: s = "too hot"
# Output: 18
# Explanation: Some of the anagrams of the given string are "too hot", "oot
# hot", "oto toh", "too toh", and "too oht".
#
# Example 2:
#
# Input: s = "aa"
# Output: 1
# Explanation: There is only one anagram possible for the given string.
#
#
#
# Constraints:
#
#
# 1 <= s.length <= 10^5
#
#
# s consists of lowercase English letters and spaces ' '.
#
#
# There is single space between consecutive words.
#

# @lc code=start
from collections import Counter


class Solution:
    def countAnagrams(self, s: str) -> int:
        """
        Interview explanation:
        Distinct anagrams of s = product over words of distinct permutations of
        that word (mod 10^9+7).

        Algorithm:
        - Precompute factorials / inv factorials up to n.
        - For each word: n! / (f1! * f2! * ...).

        Complexity: O(n + A log MOD) time for inv (or O(n) with inv fact), O(n) space.
        """
        MOD = 10**9 + 7
        n = len(s)
        fact = [1] * (n + 1)
        for i in range(1, n + 1):
            fact[i] = fact[i - 1] * i % MOD
        inv_fact = [1] * (n + 1)
        inv_fact[n] = pow(fact[n], MOD - 2, MOD)
        for i in range(n, 0, -1):
            inv_fact[i - 1] = inv_fact[i] * i % MOD

        ans = 1
        for word in s.split():
            m = len(word)
            ways = fact[m]
            for c in Counter(word).values():
                ways = ways * inv_fact[c] % MOD
            ans = ans * ways % MOD
        return ans

    def countAnagrams_math(self, s: str) -> int:
        """
        Interview explanation:
        Same multinomial count per word using iterative product and modular inverse.

        Algorithm:
        - For each word of length m with freqs f: product i=1..m of i, divide by
          each f! via modular inverse.

        Complexity: O(n log MOD) time, O(1) extra space beyond counters.
        """
        MOD = 10**9 + 7
        ans = 1
        for word in s.split():
            m = len(word)
            ways = 1
            for i in range(2, m + 1):
                ways = ways * i % MOD
            for c in Counter(word).values():
                den = 1
                for i in range(2, c + 1):
                    den = den * i % MOD
                ways = ways * pow(den, MOD - 2, MOD) % MOD
            ans = ans * ways % MOD
        return ans
# @lc code=end
