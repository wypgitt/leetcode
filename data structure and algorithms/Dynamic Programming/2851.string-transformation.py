#
# @lc app=leetcode id=2851 lang=python3
#
# [2851] String Transformation
#
# https://leetcode.com/problems/string-transformation/description/
#
# algorithms
# Hard (27.66%)
# Likes:    187
# Dislikes: 50
# Total Accepted:    7.4K
# Total Submissions: 26.6K
# Testcase Example:  "\"abcd\"\n\"cdab\"\n2"
#
#
# You are given two strings s and t of equal length n. You can perform the
# following operation on the string s:
#
# Remove a suffix of s of length l where 0 < l < n and append it at the
# start of s.
#
#         For example, let s = 'abcd' then in one operation you can remove
# the suffix 'cd' and append it in front of s making s = 'cdab'.
#
# You are also given an integer k. Return the number of ways in which s
# can be transformed into t in exactly k operations.
#
# Since the answer can be large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "abcd", t = "cdab", k = 2
# Output: 2
# Explanation:
# First way:
# In first operation, choose suffix from index = 3, so resulting s =
# "dabc".
# In second operation, choose suffix from index = 3, so resulting s =
# "cdab".
#
# Second way:
# In first operation, choose suffix from index = 1, so resulting s =
# "bcda".
# In second operation, choose suffix from index = 1, so resulting s =
# "cdab".
#
# Example 2:
#
# Input: s = "ababab", t = "ababab", k = 1
# Output: 2
# Explanation:
# First way:
# Choose suffix from index = 2, so resulting s = "ababab".
#
# Second way:
# Choose suffix from index = 4, so resulting s = "ababab".
#
# Constraints:
#
# 2 <= s.length <= 5 * 10^5
#
# 1 <= k <= 10^15
#
# s.length == t.length
#
# s and t consist of only lowercase English alphabets.
#

# @lc code=start
from typing import List


class Solution:
    def numberOfWays(self, s: str, t: str, k: int) -> int:
        """
        Interview explanation:
        Each op cycles s by a non-trivial rotation. Count sequences of exactly k ops
        turning s into t, mod 10^9+7 (k up to 1e15).

        Algorithm:
        - KMP-count how many left-rotations of s equal t (cnt).
        - All target rotations share one DP state; non-targets share another.
        - Transition matrix [[cnt-1, cnt], [n-cnt, n-cnt-1]] raised to k.
        - Start in target iff s == t.

        Complexity: O(n + log k) time, O(n) space.
        """
        MOD = 10**9 + 7
        n = len(s)
        cnt = self._count_rotations(s, t)
        if cnt == 0:
            return 0

        mat = [
            [(cnt - 1) % MOD, cnt % MOD],
            [(n - cnt) % MOD, (n - cnt - 1) % MOD],
        ]
        powered = self._mat_pow(mat, k, MOD)
        # [f_target, f_other] after k steps from unit start
        if s == t:
            return powered[0][0]
        return powered[0][1]

    def _count_rotations(self, s: str, t: str) -> int:
        n = len(s)
        pi = [0] * n
        for i in range(1, n):
            j = pi[i - 1]
            while j and t[i] != t[j]:
                j = pi[j - 1]
            if t[i] == t[j]:
                j += 1
            pi[i] = j
        cnt = j = 0
        text = s + s
        for i in range(2 * n - 1):
            while j and text[i] != t[j]:
                j = pi[j - 1]
            if text[i] == t[j]:
                j += 1
            if j == n:
                if i - n + 1 < n:
                    cnt += 1
                j = pi[j - 1]
        return cnt

    def _mat_mul(
        self, a: List[List[int]], b: List[List[int]], MOD: int
    ) -> List[List[int]]:
        return [
            [
                (a[0][0] * b[0][0] + a[0][1] * b[1][0]) % MOD,
                (a[0][0] * b[0][1] + a[0][1] * b[1][1]) % MOD,
            ],
            [
                (a[1][0] * b[0][0] + a[1][1] * b[1][0]) % MOD,
                (a[1][0] * b[0][1] + a[1][1] * b[1][1]) % MOD,
            ],
        ]

    def _mat_pow(self, mat: List[List[int]], exp: int, MOD: int) -> List[List[int]]:
        r = [[1, 0], [0, 1]]
        m = [row[:] for row in mat]
        while exp:
            if exp & 1:
                r = self._mat_mul(r, m, MOD)
            m = self._mat_mul(m, m, MOD)
            exp >>= 1
        return r
# @lc code=end
