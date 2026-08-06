#
# @lc app=leetcode id=318 lang=python3
#
# [318] Maximum Product of Word Lengths
#
# https://leetcode.com/problems/maximum-product-of-word-lengths/description/
#
# algorithms
# Medium (61.44%)
# Likes:    3640
# Dislikes: 146
# Total Accepted:    259K
# Total Submissions: 422K
# Testcase Example:  "[\"abcw\",\"baz\",\"foo\",\"bar\",\"xtfn\",\"abcdef\"]"
#
# Given a string array words, return the maximum value of length(word[i]) *
# length(word[j]) where the two words do not share common letters. If no such
# two words exist, return 0.
#
# Example 1:
#
# Input: words = ["abcw","baz","foo","bar","xtfn","abcdef"]
# Output: 16
# Explanation: The two words can be "abcw", "xtfn".
#
# Example 2:
#
# Input: words = ["a","ab","abc","d","cd","bcd","abcd"]
# Output: 4
# Explanation: The two words can be "ab", "cd".
#
# Example 3:
#
# Input: words = ["a","aa","aaa","aaaa"]
# Output: 0
# Explanation: No such pair of words.
#
# Constraints:
#
# 2 <= words.length <= 1000
#
# 1 <= words[i].length <= 1000
#
# words[i] consists only of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def maxProduct(self, words: List[str]) -> int:
        """
        Interview explanation:
        Two words' lengths multiply if they share no letters. Bitmask each
        word's alphabet (26 bits); if masks & == 0 they are disjoint.

        Algorithm:
        - masks[i] |= 1 << (c - 'a') for each char.
        - Check all pairs; track max len_i * len_j when masks disjoint.

        Complexity: O(n^2 + L) time, O(n) space.
        """
        n = len(words)
        masks = [0] * n
        for i, w in enumerate(words):
            m = 0
            for c in w:
                m |= 1 << (ord(c) - ord("a"))
            masks[i] = m
        best = 0
        for i in range(n):
            for j in range(i + 1, n):
                if masks[i] & masks[j] == 0:
                    best = max(best, len(words[i]) * len(words[j]))
        return best
# @lc code=end

