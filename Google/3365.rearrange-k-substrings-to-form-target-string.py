#
# @lc app=leetcode id=3365 lang=python3
#
# [3365] Rearrange K Substrings to Form Target String
#
# https://leetcode.com/problems/rearrange-k-substrings-to-form-target-string/description/
#
# algorithms
# Medium (56.99%)
# Likes:    89
# Dislikes: 7
# Total Accepted:    28.7K
# Total Submissions: 50.3K
# Testcase Example:  "\"abcd\"\n\"cdab\"\n2"
#
#
# You are given two strings s and t, both of which are anagrams of each
# other, and an integer k.
#
# Your task is to determine whether it is possible to split the string s
# into k equal-sized substrings, rearrange the substrings, and concatenate
# them in any order to create a new string that matches the given string
# t.
#
# Return true if this is possible, otherwise, return false.
#
# An anagram is a word or phrase formed by rearranging the letters of a
# different word or phrase, using all the original letters exactly once.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "abcd", t = "cdab", k = 2
#
# Output: true
#
# Explanation:
#
# Split s into 2 substrings of length 2: ["ab", "cd"].
#
# Rearranging these substrings as ["cd", "ab"], and then concatenating
# them results in "cdab", which matches t.
#
# Example 2:
#
# Input: s = "aabbcc", t = "bbaacc", k = 3
#
# Output: true
#
# Explanation:
#
# Split s into 3 substrings of length 2: ["aa", "bb", "cc"].
#
# Rearranging these substrings as ["bb", "aa", "cc"], and then
# concatenating them results in "bbaacc", which matches t.
#
# Example 3:
#
# Input: s = "aabbcc", t = "bbaacc", k = 2
#
# Output: false
#
# Explanation:
#
# Split s into 2 substrings of length 3: ["aab", "bcc"].
#
# These substrings cannot be rearranged to form t = "bbaacc", so the
# output is false.
#
# Constraints:
#
# 1 <= s.length == t.length <= 2 * 10^5
#
# 1 <= k <= s.length
#
# s.length is divisible by k.
#
# s and t consist only of lowercase English letters.
#
# The input is generated such that s and t are anagrams of each other.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def isPossibleToRearrange(self, s: str, t: str, k: int) -> bool:
        """
        Interview explanation:
        Split both strings into k equal blocks; rearranging s's blocks can match t
        iff the multisets of blocks are identical.

        Algorithm:
        - Block length = n // k; compare Counter of s-blocks vs t-blocks.

        Complexity: O(n) time, O(n) space.
        """
        n = len(s)
        m = n // k
        return Counter(s[i : i + m] for i in range(0, n, m)) == Counter(
            t[i : i + m] for i in range(0, n, m)
        )
# @lc code=end
