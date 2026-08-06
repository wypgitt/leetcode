#
# @lc app=leetcode id=1662 lang=python3
#
# [1662] Check If Two String Arrays are Equivalent
#
# https://leetcode.com/problems/check-if-two-string-arrays-are-equivalent/description/
#
# algorithms
# Easy (86.16%)
# Likes:    3175
# Dislikes: 205
# Total Accepted:    631K
# Total Submissions: 733K
# Testcase Example:  "[\"ab\", \"c\"]"
#
# Given two string arrays word1 and word2, return true if the two arrays
# represent the same string, and false otherwise.
#
# A string is represented by an array if the array elements concatenated in
# order forms the string.
#
# Example 1:
#
# Input: word1 = ["ab", "c"], word2 = ["a", "bc"]
# Output: true
# Explanation:
# word1 represents string "ab" + "c" -> "abc"
# word2 represents string "a" + "bc" -> "abc"
# The strings are the same, so return true.
#
# Example 2:
#
# Input: word1 = ["a", "cb"], word2 = ["ab", "c"]
# Output: false
#
# Example 3:
#
# Input: word1 = ["abc", "d", "defg"], word2 = ["abcddefg"]
# Output: true
#
# Constraints:
#
# 1 <= word1.length, word2.length <= 10^3
#
# 1 <= word1[i].length, word2[i].length <= 10^3
#
# 1 <= sum(word1[i].length), sum(word2[i].length) <= 10^3
#
# word1[i] and word2[i] consist of lowercase letters.
#

# @lc code=start
from typing import List


class Solution:
    def arrayStringsAreEqual(self, word1: List[str], word2: List[str]) -> bool:
        """
        Interview explanation:
        Two string arrays represent concatenations; check equality. Join is
        simplest; two-pointer avoids full string allocation.

        Algorithm (join):
        - return ''.join(word1) == ''.join(word2)

        Complexity: O(L) time/space for total length L.
        """
        return "".join(word1) == "".join(word2)

    def arrayStringsAreEqual_twopointer(self, word1: List[str], word2: List[str]) -> bool:
        """
        Interview explanation:
        Alternate: walk both arrays with (word_idx, char_idx) without building strings.

        Algorithm:
        - Advance pointers through chars; mismatch → False; both must end together.

        Complexity: O(L) time, O(1) space.
        """
        i = j = ii = jj = 0
        while i < len(word1) and j < len(word2):
            if word1[i][ii] != word2[j][jj]:
                return False
            ii += 1
            jj += 1
            if ii == len(word1[i]):
                i += 1
                ii = 0
            if jj == len(word2[j]):
                j += 1
                jj = 0
        return i == len(word1) and j == len(word2)
# @lc code=end
