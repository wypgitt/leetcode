#
# @lc app=leetcode id=408 lang=python3
#
# [408] Valid Word Abbreviation
#
# https://leetcode.com/problems/valid-word-abbreviation/description/
#
# algorithms
# Easy (37.05%)
# Likes:    929
# Dislikes: 2408
# Total Accepted:    364.5K
# Total Submissions: 983.9K
# Testcase Example:  "\"internationalization\"\n\"i12iz4n\""
#
#
# A string can be abbreviated by replacing any number of non-adjacent,
# non-empty substrings with their lengths. The lengths should not have
# leading zeros.
#
# For example, a string such as "substitution" could be abbreviated as
# (but not limited to):
#
# "s10n" ("s ubstitutio n")
#
# "sub4u4" ("sub stit u tion")
#
# "12" ("substitution")
#
# "su3i1u2on" ("su bst i t u ti on")
#
# "substitution" (no substrings replaced)
#
# The following are not valid abbreviations:
#
# "s55n" ("s ubsti tutio n", the replaced substrings are adjacent)
#
# "s010n" (has leading zeros)
#
# "s0ubstitution" (replaces an empty substring)
#
# Given a string word and an abbreviation abbr, return whether the string
# matches the given abbreviation.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: word = "internationalization", abbr = "i12iz4n"
# Output: true
# Explanation: The word "internationalization" can be abbreviated as
# "i12iz4n" ("i nternational iz atio n").
#
# Example 2:
#
# Input: word = "apple", abbr = "a2e"
# Output: false
# Explanation: The word "apple" cannot be abbreviated as "a2e".
#
# Constraints:
#
# 1 <= word.length <= 20
#
# word consists of only lowercase English letters.
#
# 1 <= abbr.length <= 10
#
# abbr consists of lowercase English letters and digits.
#
# All the integers in abbr will fit in a 32-bit integer.
#
# @lc code=start

class Solution:
    def validWordAbbreviation(self, word: str, abbr: str) -> bool:
        """
        Interview explanation:
        Two pointers: walk word and abbr together. Letters must match; digit
        runs form a skip count (no leading zeros). Skip that many chars in word.

        Algorithm:
        - i on word, j on abbr. If digit: parse number (reject leading 0), i+=num.
        - Else require word[i]==abbr[j] and advance both.
        - Valid iff both pointers finish exactly.

        Complexity: O(n+m) time, O(1) space.
        """
        i = j = 0
        n, m = len(word), len(abbr)
        while i < n and j < m:
            if abbr[j].isdigit():
                if abbr[j] == "0":
                    return False
                num = 0
                while j < m and abbr[j].isdigit():
                    num = num * 10 + int(abbr[j])
                    j += 1
                i += num
            else:
                if word[i] != abbr[j]:
                    return False
                i += 1
                j += 1
        return i == n and j == m
# @lc code=end
