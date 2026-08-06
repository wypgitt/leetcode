#
# @lc app=leetcode id=884 lang=python3
#
# [884] Uncommon Words from Two Sentences
#
# https://leetcode.com/problems/uncommon-words-from-two-sentences/description/
#
# algorithms
# Easy (75.8%)
# Likes:    1916
# Dislikes: 209
# Total Accepted:    347K
# Total Submissions: 458K
# Testcase Example:  "\"this apple is sweet\""
#
# A sentence is a string of single-space separated words where each word
# consists only of lowercase letters.
#
# A word is uncommon if it appears exactly once in one of the sentences, and
# does not appear in the other sentence.
#
# Given two sentences s1 and s2, return a list of all the uncommon words. You
# may return the answer in any order.
#
# Example 1:
#
# Input: s1 = "this apple is sweet", s2 = "this apple is sour"
#
# Output: ["sweet","sour"]
#
# Explanation:
#
# The word "sweet" appears only in s1, while the word "sour" appears only in
# s2.
#
# Example 2:
#
# Input: s1 = "apple apple", s2 = "banana"
#
# Output: ["banana"]
#
# Constraints:
#
# 1 <= s1.length, s2.length <= 200
#
# s1 and s2 consist of lowercase English letters and spaces.
#
# s1 and s2 do not have leading or trailing spaces.
#
# All the words in s1 and s2 are separated by a single space.
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def uncommonFromSentences(self, s1: str, s2: str) -> List[str]:
        """
        Interview explanation:
        Uncommon = appears exactly once across both sentences combined.

        Algorithm:
        - Counter of all words; return those with count 1.

        Complexity: O(L) time, O(W) space.
        """
        cnt = Counter(s1.split()) + Counter(s2.split())
        return [w for w, c in cnt.items() if c == 1]
# @lc code=end

