#
# @lc app=leetcode id=1930 lang=python3
#
# [1930] Unique Length-3 Palindromic Subsequences
#
# https://leetcode.com/problems/unique-length-3-palindromic-subsequences/description/
#
# algorithms
# Medium (73.76%)
# Likes:    2875
# Dislikes: 108
# Total Accepted:    371K
# Total Submissions: 502K
# Testcase Example:  "\"aabca\""
#
# Given a string s, return the number of unique palindromes of length three
# that are a subsequence of s.
#
# Note that even if there are multiple ways to obtain the same subsequence, it
# is still only counted once.
#
# A palindrome is a string that reads the same forwards and backwards.
#
# A subsequence of a string is a new string generated from the original string
# with some characters (can be none) deleted without changing the relative
# order of the remaining characters.
#
# For example, "ace" is a subsequence of "abcde".
#
# Example 1:
#
# Input: s = "aabca"
# Output: 3
# Explanation: The 3 palindromic subsequences of length 3 are:
# - "aba" (subsequence of "aabca")
# - "aaa" (subsequence of "aabca")
# - "aca" (subsequence of "aabca")
#
# Example 2:
#
# Input: s = "adc"
# Output: 0
# Explanation: There are no palindromic subsequences of length 3 in "adc".
#
# Example 3:
#
# Input: s = "bbcbaba"
# Output: 4
# Explanation: The 4 palindromic subsequences of length 3 are:
# - "bbb" (subsequence of "bbcbaba")
# - "bcb" (subsequence of "bbcbaba")
# - "bab" (subsequence of "bbcbaba")
# - "aba" (subsequence of "bbcbaba")
#
# Constraints:
#
# 3 <= s.length <= 10^5
#
# s consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def countPalindromicSubsequence(self, s: str) -> int:
        """
        Interview explanation:
        Count distinct length-3 palindromic subsequences (aba form). For each
        letter as outer, take first/last occurrence; count unique chars between.

        Algorithm:
        - For c in a..z: L=first, R=last; if R-L>=2: add len(set(s[L+1:R])).

        Complexity: O(26 * n) time, O(n) space.
        """
        ans = 0
        for c in set(s):
            l, r = s.find(c), s.rfind(c)
            if r - l >= 2:
                ans += len(set(s[l + 1 : r]))
        return ans
# @lc code=end
