#
# @lc app=leetcode id=3138 lang=python3
#
# [3138] Minimum Length of Anagram Concatenation
#
# https://leetcode.com/problems/minimum-length-of-anagram-concatenation/description/
#
# algorithms
# Medium (39.70%)
# Likes:    208
# Dislikes: 104
# Total Accepted:    34.6K
# Total Submissions: 87.1K
# Testcase Example:  "\"abba\""
#
#
# You are given a string s, which is known to be a concatenation of
# anagrams of some string t.
#
# Return the minimum possible length of the string t.
#
# An anagram is formed by rearranging the letters of a string. For
# example, "aab", "aba", and, "baa" are anagrams of "aab".
#
# Example 1:
#
# Input: s = "abba"
#
# Output: 2
#
# Explanation:
#
# One possible string t could be "ba".
#
# Example 2:
#
# Input: s = "cdef"
#
# Output: 4
#
# Explanation:
#
# One possible string t could be "cdef", notice that t can be equal to s.
#
# Example 2:
#
# Input: s = "abcbcacabbaccba"
#
# Output: 3
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consist only of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def minAnagramLength(self, s: str) -> int:
        """
        Interview explanation:
        s is a concatenation of anagrams of some t; find the minimum |t|.

        Algorithm:
        - |t| must divide n. Try lengths L from 1..n that divide n; check every
          chunk of length L has the same character multiset as s[:L].
        - Return the smallest valid L.

        Complexity: O(n * d(n) * sigma) ~ O(n * #divisors) time, O(sigma) space.
        """
        n = len(s)

        def ok(L: int) -> bool:
            if n % L:
                return False
            base = Counter(s[:L])
            for i in range(L, n, L):
                if Counter(s[i : i + L]) != base:
                    return False
            return True

        for L in range(1, n + 1):
            if n % L == 0 and ok(L):
                return L
        return n
# @lc code=end
