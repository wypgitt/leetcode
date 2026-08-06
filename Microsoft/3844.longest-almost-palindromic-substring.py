#
# @lc app=leetcode id=3844 lang=python3
#
# [3844] Longest Almost-Palindromic Substring
#
# https://leetcode.com/problems/longest-almost-palindromic-substring/description/
#
# algorithms
# Medium (22.89%)
# Likes:    154
# Dislikes: 13
# Total Accepted:    15.5K
# Total Submissions: 67.9K
# Testcase Example:  "\"abca\""
#
#
# You are given a string s consisting of lowercase English letters.
#
# A substring is almost-palindromic if it becomes a palindrome after
# removing exactly one character from it.
#
# Return an integer denoting the length of the longest almost-palindromic
# substring in s.
#
# Example 1:
#
# Input: s = "abca"
#
# Output: 4
#
# Explanation:
#
# Choose the substring "abca".
#
# Remove "abca".
#
# The string becomes "aba", which is a palindrome.
#
# Therefore, "abca" is almost-palindromic.
#
# Example 2:
#
# Input: s = "abba"
#
# Output: 4
#
# Explanation:
#
# Choose the substring "abba".
#
# Remove "abba".
#
# The string becomes "aba", which is a palindrome.
#
# Therefore, "abba" is almost-palindromic.
#
# Example 3:
#
# Input: s = "zzabba"
#
# Output: 5
#
# Explanation:
#
# Choose the substring "zzabba".
#
# Remove "zabba".
#
# The string becomes "abba", which is a palindrome.
#
# Therefore, "zabba" is almost-palindromic.
#
# Constraints:
#
# 2 <= s.length <= 2500
#
# s consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def almostPalindromic(self, s: str) -> int:
        """
        Interview explanation:
        A substring is almost-palindromic if deleting exactly one character
        yields a palindrome. Expand around centers, then allow one skip.

        Algorithm:
        - For each odd/even center, expand while characters match.
        - On mismatch (or after full expand), try skipping left or right once
          and continue expanding; take max length (capped at n).

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(s)

        def expand(l: int, r: int) -> int:
            while l >= 0 and r < n and s[l] == s[r]:
                l -= 1
                r += 1
            l1, r1 = l - 1, r
            l2, r2 = l, r + 1
            while l1 >= 0 and r1 < n and s[l1] == s[r1]:
                l1 -= 1
                r1 += 1
            while l2 >= 0 and r2 < n and s[l2] == s[r2]:
                l2 -= 1
                r2 += 1
            return min(n, max(r1 - l1 - 1, r2 - l2 - 1))

        ans = 0
        for i in range(n):
            ans = max(ans, expand(i, i), expand(i, i + 1))
        return ans
# @lc code=end
