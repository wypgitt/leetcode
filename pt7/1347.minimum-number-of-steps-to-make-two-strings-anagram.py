#
# @lc app=leetcode id=1347 lang=python3
#
# [1347] Minimum Number of Steps to Make Two Strings Anagram
#
# https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram/description/
#
# algorithms
# Medium (82.50%)
# Likes:    2825
# Dislikes: 122
# Total Accepted:    337.5K
# Total Submissions: 409.1K
# Testcase Example:  '"bab"\n"aba"'
#
# You are given two strings of the same length s and t. In one step you can
# choose any character of t and replace it with another character.
# 
# Return the minimum number of steps to make t an anagram of s.
# 
# An Anagram of a string is a string that contains the same characters with a
# different (or the same) ordering.
# 
# 
# Example 1:
# 
# 
# Input: s = "bab", t = "aba"
# Output: 1
# Explanation: Replace the first 'a' in t with b, t = "bba" which is anagram of
# s.
# 
# 
# Example 2:
# 
# 
# Input: s = "leetcode", t = "practice"
# Output: 5
# Explanation: Replace 'p', 'r', 'a', 'i' and 'c' from t with proper characters
# to make t anagram of s.
# 
# 
# Example 3:
# 
# 
# Input: s = "anagram", t = "mangaar"
# Output: 0
# Explanation: "anagram" and "mangaar" are anagrams. 
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 5 * 10^4
# s.length == t.length
# s and t consist of lowercase English letters only.
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import Counter


class Solution:
    def minSteps(self, s: str, t: str) -> int:
        balance = Counter(s)
        for char in t:
            balance[char] -= 1

        return sum(count for count in balance.values() if count > 0)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# We can only replace characters in `t`, so count how many characters `t` is
# missing compared with `s`. Every missing character requires one replacement.
#
# Data structure:
# `Counter(s)` stores required counts. Subtracting each character from `t`
# leaves positive counts for letters still needed by `t`.
#
# Why positives only:
# If a count is negative, `t` has extra copies of that character. Those extras
# are exactly the characters we will replace, but the number of replacements is
# already captured by the positive deficits elsewhere.
#
# Edge cases:
# - Already anagrams: all balances are zero, answer 0.
# - Completely different strings of equal length: answer is the string length.
# - Repeated letters: Counter handles multiplicity.
#
# Complexity:
# - Time: O(n), where n is the string length.
# - Space: O(1) because there are only 26 lowercase English letters.
