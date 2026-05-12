#
# @lc app=leetcode id=1324 lang=python3
#
# [1324] Print Words Vertically
#
# https://leetcode.com/problems/print-words-vertically/description/
#
# algorithms
# Medium (67.54%)
# Likes:    828
# Dislikes: 121
# Total Accepted:    52.8K
# Total Submissions: 78.1K
# Testcase Example:  '"HOW ARE YOU"'
#
# Given a string s. Return all the words vertically in the same order in which
# they appear in s.
# Words are returned as a list of strings, complete with spaces when is
# necessary. (Trailing spaces are not allowed).
# Each word would be put on only one column and that in one column there will
# be only one word.
# 
# 
# Example 1:
# 
# 
# Input: s = "HOW ARE YOU"
# Output: ["HAY","ORO","WEU"]
# Explanation: Each word is printed vertically. 
# ⁠"HAY"
# "ORO"
# "WEU"
# 
# 
# Example 2:
# 
# 
# Input: s = "TO BE OR NOT TO BE"
# Output: ["TBONTB","OEROOE","   T"]
# Explanation: Trailing spaces is not allowed. 
# "TBONTB"
# "OEROOE"
# "   T"
# 
# 
# Example 3:
# 
# 
# Input: s = "CONTEST IS COMING"
# Output: ["CIC","OSO","N M","T I","E N","S G","T"]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 200
# s contains only upper case English letters.
# It's guaranteed that there is only one space between 2 words.
# 
#

# @lc code=start
from __future__ import annotations

from typing import List


class Solution:
    def printVertically(self, s: str) -> List[str]:
        words = s.split()
        max_length = max(len(word) for word in words)
        answer = []

        for column in range(max_length):
            vertical_word = []
            for word in words:
                vertical_word.append(word[column] if column < len(word) else " ")
            answer.append("".join(vertical_word).rstrip())

        return answer
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Printing words vertically is equivalent to reading the words column by
# column. For column `i`, take the `i`th character from every word that has one;
# otherwise use a space so later words stay aligned. Then trim trailing spaces.
#
# Data structure:
# A list of words and a temporary list of characters per vertical output row.
# Strings are immutable, so building a list and joining it is cleaner than
# repeated concatenation.
#
# Walkthrough:
# 1. Split the sentence into words.
# 2. The number of output rows is the maximum word length.
# 3. For each character index, gather that index from every word or a padding
#    space if the word is shorter.
# 4. Use `rstrip()` to remove only trailing spaces, as required.
#
# Edge cases:
# - One word: returns each character as its own string.
# - Words of different lengths: internal spaces are preserved, trailing spaces
#   are removed.
# - Multiple words ending before the longest word: `rstrip()` cleans the end of
#   each vertical row.
#
# Complexity:
# - Time: O(w * L), where w is the number of words and L is the longest word.
# - Space: O(w * L) for the output.
