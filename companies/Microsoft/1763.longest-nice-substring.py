#
# @lc app=leetcode id=1763 lang=python3
#
# [1763] Longest Nice Substring
#
# https://leetcode.com/problems/longest-nice-substring/description/
#
# algorithms
# Easy (64.6%)
# Likes:    1530
# Dislikes: 988
# Total Accepted:    102K
# Total Submissions: 158K
# Testcase Example:  "\"YazaAay\""
#
# A string s is nice if, for every letter of the alphabet that s contains, it
# appears both in uppercase and lowercase. For example, "abABB" is nice because
# 'A' and 'a' appear, and 'B' and 'b' appear. However, "abA" is not because 'b'
# appears, but 'B' does not.
#
# Given a string s, return the longest substring of s that is nice. If there
# are multiple, return the substring of the earliest occurrence. If there are
# none, return an empty string.
#
# Example 1:
#
# Input: s = "YazaAay"
# Output: "aAa"
# Explanation: "aAa" is a nice string because 'A/a' is the only letter of the
# alphabet in s, and both 'A' and 'a' appear.
# "aAa" is the longest nice substring.
#
# Example 2:
#
# Input: s = "Bb"
# Output: "Bb"
# Explanation: "Bb" is a nice string because both 'B' and 'b' appear. The whole
# string is a substring.
#
# Example 3:
#
# Input: s = "c"
# Output: ""
# Explanation: There are no nice substrings.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of uppercase and lowercase English letters.
#

# @lc code=start
class Solution:
    def longestNiceSubstring(self, s: str) -> str:
        """
        Interview explanation:
        Nice = every letter appears in both cases. Divide-and-conquer: a char
        missing its case-pair cannot belong to any nice substring → split on
        all such chars and recurse; keep longest (leftmost on ties).

        Algorithm:
        - If some ch lacks swapcase(ch): recurse on segments split by such chars.
        - Else s itself is nice.

        Complexity: O(n * Σ) typical / O(n^2) worst, O(n) space.
        """
        def dfs(t: str) -> str:
            if len(t) < 2:
                return ""
            chars = set(t)
            for i, ch in enumerate(t):
                if ch.swapcase() not in chars:
                    left = dfs(t[:i])
                    right = dfs(t[i + 1 :])
                    return left if len(left) >= len(right) else right
            return t

        return dfs(s)

    def longestNiceSubstring_bruteforce(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: examine all O(n^2) substrings and keep the longest nice one
        (leftmost on equal length).

        Algorithm:
        - For i..j: check niceness via set of chars; update best.

        Complexity: O(n^2 * Σ) time, O(Σ) space.
        """
        def nice(t: str) -> bool:
            chars = set(t)
            return all(c.swapcase() in chars for c in chars)

        best = ""
        n = len(s)
        for i in range(n):
            for j in range(i + 1, n):
                sub = s[i : j + 1]
                if len(sub) > len(best) and nice(sub):
                    best = sub
        return best
# @lc code=end
