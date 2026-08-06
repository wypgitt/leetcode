#
# @lc app=leetcode id=1967 lang=python3
#
# [1967] Number of Strings That Appear as Substrings in Word
#
# https://leetcode.com/problems/number-of-strings-that-appear-as-substrings-in-word/description/
#
# algorithms
# Easy (86.18%)
# Likes:    977
# Dislikes: 47
# Total Accepted:    249K
# Total Submissions: 289K
# Testcase Example:  "[\"a\",\"abc\",\"bc\",\"d\"]"
#
# Given an array of strings patterns and a string word, return the number of
# strings in patterns that exist as a substring in word.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: patterns = ["a","abc","bc","d"], word = "abc"
# Output: 3
# Explanation:
# - "a" appears as a substring in "abc".
# - "abc" appears as a substring in "abc".
# - "bc" appears as a substring in "abc".
# - "d" does not appear as a substring in "abc".
# 3 of the strings in patterns appear as a substring in word.
#
# Example 2:
#
# Input: patterns = ["a","b","c"], word = "aaaaabbbbb"
# Output: 2
# Explanation:
# - "a" appears as a substring in "aaaaabbbbb".
# - "b" appears as a substring in "aaaaabbbbb".
# - "c" does not appear as a substring in "aaaaabbbbb".
# 2 of the strings in patterns appear as a substring in word.
#
# Example 3:
#
# Input: patterns = ["a","a","a"], word = "ab"
# Output: 3
# Explanation: Each of the patterns appears as a substring in word "ab".
#
# Constraints:
#
# 1 <= patterns.length <= 100
#
# 1 <= patterns[i].length <= 100
#
# 1 <= word.length <= 100
#
# patterns[i] and word consist of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def numOfStrings(self, patterns: List[str], word: str) -> int:
        """
        Interview explanation:
        Count how many pattern strings appear as a substring of word.

        Algorithm:
        - sum(1 for p in patterns if p in word).

        Complexity: O(sum(|p| * |word|)) with native find; O(P) space.
        """
        return sum(1 for p in patterns if p in word)

    def numOfStrings_find(self, patterns: List[str], word: str) -> int:
        """
        Interview explanation:
        Alternate: use str.find explicitly for the same substring checks.

        Algorithm:
        - Count patterns with word.find(p) != -1.

        Complexity: same as primary.
        """
        return sum(word.find(p) != -1 for p in patterns)
# @lc code=end

