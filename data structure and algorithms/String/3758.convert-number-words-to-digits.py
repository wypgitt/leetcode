#
# @lc app=leetcode id=3758 lang=python3
#
# [3758] Convert Number Words to Digits
#
# https://leetcode.com/problems/convert-number-words-to-digits/description/
#
# algorithms
# Medium (67.08%)
# Likes:    4
# Dislikes: 1
# Total Accepted:    644
# Total Submissions: 960
# Testcase Example:  "\"onefourthree\""
#
#
# You are given a string s consisting of lowercase English letters. s may
# contain valid concatenated English words representing the digits 0 to 9,
# without spaces.
#
# Your task is to extract each valid number word in order and convert it
# to its corresponding digit, producing a string of digits.
#
# Parse s from left to right. At each position:
#
# If a valid number word starts at the current position, append its
# corresponding digit to the result and advance by the length of that
# word.
#
# Otherwise, skip exactly one character and continue parsing.
#
# Return the resulting digit string. If no number words are found, return
# an empty string.
#
# Example 1:
#
# Input: s = "onefourthree"
#
# Output: "143"
#
# Explanation:
#
# Parsing from left to right, extract the valid number words "one",
# "four", "three".
#
# These map to digits 1, 4, 3. Thus, the final result is "143".
#
# Example 2:
#
# Input: s = "ninexsix"
#
# Output: "96"
#
# Explanation:
#
# The substring "nine" is a valid number word and maps to 9.
#
# The character "x" does not match any valid number word prefix and is
# skipped.
#
# Then, the substring "six" is a valid number word and maps to 6, so the
# final result is "96".
#
# Example 3:
#
# Input: s = "zeero"
#
# Output: ""
#
# Explanation:
#
# No substring forms a valid number word during left-to-right parsing.
#
# All characters are skipped and incomplete fragments are ignored, so the
# result is an empty string.
#
# Example 4:
#
# Input: s = "tw"
#
# Output: ""
#
# Explanation:
#
# No substring forms a valid number word during left-to-right parsing.
#
# All characters are skipped and incomplete fragments are ignored, so the
# result is an empty string.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s contains only lowercase English letters.
#

# @lc code=start
class Solution:
    def convertNumber(self, s: str) -> str:
        """
        Interview explanation:
        Left-to-right greedy: at each index, take a digit word (length 3..5) if
        it matches; otherwise skip one character.

        Algorithm:
        - Dictionary zero..nine; try lengths 3,4,5; advance by match length or 1.

        Complexity: O(n) time, O(1) extra space.
        """
        lookup = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four": "4",
            "five": "5",
            "six": "6",
            "seven": "7",
            "eight": "8",
            "nine": "9",
        }
        out = []
        i = 0
        n = len(s)
        while i < n:
            matched = False
            for L in (3, 4, 5):
                if i + L <= n and s[i : i + L] in lookup:
                    out.append(lookup[s[i : i + L]])
                    i += L
                    matched = True
                    break
            if not matched:
                i += 1
        return "".join(out)
# @lc code=end
