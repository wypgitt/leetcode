#
# @lc app=leetcode id=1400 lang=python3
#
# [1400] Construct K Palindrome Strings
#
# https://leetcode.com/problems/construct-k-palindrome-strings/description/
#
# algorithms
# Medium (68.54%)
# Likes:    1795
# Dislikes: 160
# Total Accepted:    211K
# Total Submissions: 307.9K
# Testcase Example:  '"annabelle"\n2'
#
# Given a string s and an integer k, return true if you can use all the
# characters in s to construct non-empty k palindrome strings or false
# otherwise.
# 
# 
# Example 1:
# 
# 
# Input: s = "annabelle", k = 2
# Output: true
# Explanation: You can construct two palindromes using all characters in s.
# Some possible constructions "anna" + "elble", "anbna" + "elle", "anellena" +
# "b"
# 
# 
# Example 2:
# 
# 
# Input: s = "leetcode", k = 3
# Output: false
# Explanation: It is impossible to construct 3 palindromes using all the
# characters of s.
# 
# 
# Example 3:
# 
# 
# Input: s = "true", k = 4
# Output: true
# Explanation: The only possible solution is to put each character in a
# separate string.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# s consists of lowercase English letters.
# 1 <= k <= 10^5
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import Counter


class Solution:
    def canConstruct(self, s: str, k: int) -> bool:
        if k > len(s):
            return False

        odd_count = sum(count % 2 for count in Counter(s).values())
        return odd_count <= k
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Every palindrome can have at most one character with an odd frequency. If the
# whole string has `odd_count` odd-frequency characters, we need at least
# `odd_count` palindromes to place those odd centers. We also cannot make more
# non-empty palindromes than there are characters.
#
# Why this is sufficient:
# Once every odd-frequency character has a palindrome center, all even leftover
# characters can be paired around centers or split into additional palindromes.
# If we need more palindromes, we can split character pairs or individual
# characters until reaching `k`, as long as `k <= len(s)`.
#
# Data structure:
# `Counter` gives character frequencies. Only the parity of each frequency
# matters.
#
# Edge cases:
# - `k > len(s)`: impossible because palindromes must be non-empty.
# - `k == len(s)`: always possible, one character per palindrome.
# - All counts even: `odd_count` is 0, so any feasible k works.
#
# Complexity:
# - Time: O(n), count every character once.
# - Space: O(1), at most 26 lowercase letters.
