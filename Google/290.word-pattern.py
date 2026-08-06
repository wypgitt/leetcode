#
# @lc app=leetcode id=290 lang=python3
#
# [290] Word Pattern
#
# https://leetcode.com/problems/word-pattern/description/
#
# algorithms
# Easy (44.46%)
# Likes:    8065
# Dislikes: 1153
# Total Accepted:    1.2M
# Total Submissions: 2.6M
# Testcase Example:  "\"abba\""
#
# Given a pattern and a string s, find if s follows the same pattern.
#
# Here follow means a full match, such that there is a bijection between a
# letter in pattern and a non-empty word in s. Specifically:
#
# Each letter in pattern maps to exactly one unique word in s.
#
# Each unique word in s maps to exactly one letter in pattern.
#
# No two letters map to the same word, and no two words map to the same letter.
#
# Example 1:
#
# Input: pattern = "abba", s = "dog cat cat dog"
#
# Output: true
#
# Explanation:
#
# The bijection can be established as:
#
# 'a' maps to "dog".
#
# 'b' maps to "cat".
#
# Example 2:
#
# Input: pattern = "abba", s = "dog cat cat fish"
#
# Output: false
#
# Example 3:
#
# Input: pattern = "aaaa", s = "dog cat cat dog"
#
# Output: false
#
# Constraints:
#
# 1 <= pattern.length <= 300
#
# pattern contains only lower-case English letters.
#
# 1 <= s.length <= 3000
#
# s contains only lowercase English letters and spaces ' '.
#
# s does not contain any leading or trailing spaces.
#
# All the words in s are separated by a single space.
#

# @lc code=start
class Solution:
    def wordPattern(self, pattern: str, s: str) -> bool:
        """
        Interview explanation:
        Bijection between pattern characters and words: each char maps to one
        word and each word maps to one char.

        Algorithm:
        - Split s into words; lengths must match pattern.
        - Maintain char→word and word→char maps; reject conflicts.

        Complexity: O(n) time, O(n) space.
        """
        words = s.split()
        if len(pattern) != len(words):
            return False
        c2w, w2c = {}, {}
        for c, w in zip(pattern, words):
            if c in c2w and c2w[c] != w:
                return False
            if w in w2c and w2c[w] != c:
                return False
            c2w[c] = w
            w2c[w] = c
        return True
# @lc code=end

