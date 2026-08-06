#
# @lc app=leetcode id=1397 lang=python3
#
# [1397] Find All Good Strings
#
# https://leetcode.com/problems/find-all-good-strings/description/
#
# algorithms
# Hard (45.89%)
# Likes:    542
# Dislikes: 131
# Total Accepted:    10.1K
# Total Submissions: 22.0K
# Testcase Example:  "2"
#
# Given the strings s1 and s2 of size n and the string evil, return the number
# of good strings.
#
# A good string has size n, it is alphabetically greater than or equal to s1,
# it is alphabetically smaller than or equal to s2, and it does not contain the
# string evil as a substring. Since the answer can be a huge number, return
# this modulo 10^9 + 7.
#
# Example 1:
#
# Input: n = 2, s1 = "aa", s2 = "da", evil = "b"
# Output: 51
# Explanation: There are 25 good strings starting with 'a':
# "aa","ac","ad",...,"az". Then there are 25 good strings starting with 'c':
# "ca","cc","cd",...,"cz" and finally there is one good string starting with
# 'd': "da".
#
# Example 2:
#
# Input: n = 8, s1 = "leetcode", s2 = "leetgoes", evil = "leet"
# Output: 0
# Explanation: All strings greater than or equal to s1 and smaller than or
# equal to s2 start with the prefix "leet", therefore, there is not any good
# string.
#
# Example 3:
#
# Input: n = 2, s1 = "gx", s2 = "gz", evil = "x"
# Output: 2
#
# Constraints:
#
# s1.length == n
#
# s2.length == n
#
# s1 <= s2
#
# 1 <= n <= 500
#
# 1 <= evil.length <= 50
#
# All strings consist of lowercase English letters.
#

# @lc code=start

from functools import lru_cache


class Solution:
    def findGoodStrings(self, n: int, s1: str, s2: str, evil: str) -> int:
        """
        Interview explanation:
        Count strings of length n in [s1,s2] lexicographically that do not
        contain evil as substring. Digit DP with tight bounds + KMP state on evil.

        Algorithm:
        - Build LPS for evil; dfs(pos, evil_matched, tight_low, tight_high)
        - At each pos choose char from lo..hi; advance KMP; skip if matched==len(evil)
        - Memoize; answer dfs(0,0,True,True) mod 10^9+7

        Complexity: O(n * m * 2 * 2 * 26) with m=|evil|.
        """
        MOD = 10**9 + 7
        m = len(evil)
        pi = [0] * m
        j = 0
        for i in range(1, m):
            while j and evil[i] != evil[j]:
                j = pi[j - 1]
            if evil[i] == evil[j]:
                j += 1
                pi[i] = j

        def advance(state: int, ch: str) -> int:
            while state and evil[state] != ch:
                state = pi[state - 1]
            if evil[state] == ch:
                state += 1
            return state

        @lru_cache(None)
        def dfs(pos: int, state: int, low: bool, high: bool) -> int:
            if state == m:
                return 0
            if pos == n:
                return 1
            lo = s1[pos] if low else "a"
            hi = s2[pos] if high else "z"
            ans = 0
            for o in range(ord(lo), ord(hi) + 1):
                ch = chr(o)
                ns = advance(state, ch)
                ans = (ans + dfs(
                    pos + 1,
                    ns,
                    low and ch == lo,
                    high and ch == hi,
                )) % MOD
            return ans

        return dfs(0, 0, True, True)
# @lc code=end
