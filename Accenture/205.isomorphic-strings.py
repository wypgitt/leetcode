#
# @lc app=leetcode id=205 lang=python3
#
# [205] Isomorphic Strings
#
# https://leetcode.com/problems/isomorphic-strings/description/
#
# algorithms
# Easy (48.85%)
# Likes:    10742
# Dislikes: 2295
# Total Accepted:    2.3M
# Total Submissions: 4.7M
# Testcase Example:  "\"egg\""
#
# Given two strings s and t, determine if they are isomorphic.
#
# Two strings s and t are isomorphic if the characters in s can be replaced to
# get t.
#
# All occurrences of a character must be replaced with another character while
# preserving the order of characters. No two characters may map to the same
# character, but a character may map to itself.
#
# Example 1:
#
# Input: s = "egg", t = "add"
#
# Output: true
#
# Explanation:
#
# The strings s and t can be made identical by:
#
# Mapping 'e' to 'a'.
#
# Mapping 'g' to 'd'.
#
# Example 2:
#
# Input: s = "f11", t = "b23"
#
# Output: false
#
# Explanation:
#
# The strings s and t can not be made identical as '1' needs to be mapped to
# both '2' and '3'.
#
# Example 3:
#
# Input: s = "paper", t = "title"
#
# Output: true
#
# Constraints:
#
# 1 <= s.length <= 5 * 10^4
#
# t.length == s.length
#
# s and t consist of any valid ascii character.
#

# @lc code=start
from typing import Dict


class Solution:
    def isIsomorphic(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Strings are isomorphic iff there is a bijection between characters.
        Maintain two maps (s->t and t->s) and reject any conflicting mapping.

        Algorithm:
        - For each index i, check/set s[i] -> t[i] and t[i] -> s[i].
        - Return False on conflict; True if all pairs are consistent.

        Complexity: O(n) time, O(|Σ|) space.
        """
        s_to_t: Dict[str, str] = {}
        t_to_s: Dict[str, str] = {}
        for a, b in zip(s, t):
            if s_to_t.get(a, b) != b or t_to_s.get(b, a) != a:
                return False
            s_to_t[a] = b
            t_to_s[b] = a
        return True

    def isIsomorphicEncode(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Alternate: encode each string by first-occurrence indices. Equal encodings
        mean the same pattern of character reuse (isomorphism).

        Algorithm:
        - Map each char to the index of its first appearance.
        - Compare the two encoded tuples.

        Complexity: O(n) time, O(|Σ|) space.
        """
        def encode(x: str):
            first = {}
            return tuple(first.setdefault(c, i) for i, c in enumerate(x))

        return encode(s) == encode(t)
# @lc code=end
