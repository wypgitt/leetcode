#
# @lc app=leetcode id=3983 lang=python3
#
# [3983] Subsequence After One Replacement
#
# https://leetcode.com/problems/subsequence-after-one-replacement/description/
#
# algorithms
# Medium (21.73%)
# Likes:    94
# Dislikes: 19
# Total Accepted:    21.1K
# Total Submissions: 97.3K
# Testcase Example:  "\"cat\"\n\"chat\""
#
#
# You are given two strings s and t consisting of lowercase English
# letters.
#
# You may choose at most one index in s and replace the character at that
# index with any lowercase English letter.
#
# Return true if it is possible to make s a subsequence of t; otherwise,
# return false.
#
# Example 1:
#
# Input: s = "cat", t = "chat"
#
# Output: true
#
# Explanation:
#
# Replace s[1] from 'a' to 'h'. The resulting string is "cht".
#
# "cht" is a subsequence of "chat" because we can match 'c', 'h', and 't'
# in order.
#
# Example 2:
#
# Input: s = "plane", t = "apple"
#
# Output: false
#
# Explanation:
#
# The characters 'p', 'l', and 'e' can be matched in t, but the remaining
# characters cannot be matched while preserving the required order.
#
# Even after replacing any one character in s, it is impossible to make s
# a subsequence of t.
#
# Constraints:
#
# 1 <= s.length, t.length <= 10^5
#
# s and t consist only of lowercase English letters.
#

# @lc code=start
class Solution:
    def canMakeSubsequence(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Make s a subsequence of t with at most one character replacement in s.
        A replacement acts as one free (wildcard) match for an index of s.

        Algorithm:
        - Scan t left to right with two pointers into s:
          i0 = matched length with 0 replacements,
          i1 = matched length with at most 1 replacement.
        - On each t[j]: extend i1 on an exact match; allow one replacement as
          i0+1; then extend i0 on an exact match.

        Complexity: O(|t|) time, O(1) space.
        """
        m, n = len(s), len(t)
        i0 = i1 = j = 0
        while i1 < m and j < n:
            if s[i1] == t[j]:
                i1 += 1
            i1 = max(i1, i0 + 1)
            if s[i0] == t[j]:
                i0 += 1
            j += 1
        return i1 == m

    def canMakeSubsequence_explicit_states(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Alternate: track how far s is matched under budgets 0 and 1 while
        iterating characters of t (same dual-pointer idea, named states).

        Algorithm:
        - zero/one = progress in s with 0/1 replacements used.
        - For each ch in t: extend one on match; one = max(one, zero+1);
          then extend zero on match.

        Complexity: O(|t|) time, O(1) space.
        """
        zero = one = 0
        m = len(s)
        for ch in t:
            if one < m and s[one] == ch:
                one += 1
            one = max(one, zero + 1)
            if zero < m and s[zero] == ch:
                zero += 1
            if one >= m:
                return True
        return one >= m
# @lc code=end
