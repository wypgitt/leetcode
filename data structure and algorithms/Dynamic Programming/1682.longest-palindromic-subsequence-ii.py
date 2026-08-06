#
# @lc app=leetcode id=1682 lang=python3
#
# [1682] Longest Palindromic Subsequence II
#
# https://leetcode.com/problems/longest-palindromic-subsequence-ii/description/
#
# algorithms
# Medium (50.26%)
# Likes:    160
# Dislikes: 30
# Total Accepted:    6.5K
# Total Submissions: 13K
# Testcase Example:  "\"bbabab\""
#
#
# A subsequence of a string s is considered a good palindromic subsequence
# if:
#
# It is a subsequence of s.
#
# It is a palindrome (has the same value if reversed).
#
# It has an even length.
#
# No two consecutive characters are equal, except the two middle ones.
#
# For example, if s = "abcabcabb", then "abba" is considered a good
# palindromic subsequence, while "bcb" (not even length) and "bbbb" (has
# equal consecutive characters) are not.
#
# Given a string s, return the length of the longest good palindromic
# subsequence in s.
#
# Example 1:
#
# Input: s = "bbabab"
# Output: 4
# Explanation: The longest good palindromic subsequence of s is "baab".
#
# Example 2:
#
# Input: s = "dcbccacdb"
# Output: 4
# Explanation: The longest good palindromic subsequence of s is "dccd".
#
# Constraints:
#
# 1 <= s.length <= 250
#
# s consists of lowercase English letters.
#
# @lc code=start
from functools import lru_cache


class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        """
        Interview explanation:
        Premium LPS II: longest palindromic subsequence of even length where
        no two consecutive characters in the subsequence are equal (including
        the two center chars of even LPS). DP on (i,j,prev_char).

        Algorithm (interval DP):
        - dfs(i,j,prev): max even LPS in s[i..j] with first/last char != constraints
          via prev (last chosen outer char). Try match s[i]==s[j]!=prev then +2.

        Complexity: O(n^2 * 27) time/space.
        """
        n = len(s)

        @lru_cache(None)
        def dfs(i: int, j: int, prev: int) -> int:
            if i >= j:
                return 0
            # skip ends
            best = max(dfs(i + 1, j, prev), dfs(i, j - 1, prev))
            if s[i] == s[j]:
                code = ord(s[i]) - 97
                if code != prev:
                    best = max(best, 2 + dfs(i + 1, j - 1, code))
            return best

        return dfs(0, n - 1, 26)
# @lc code=end
