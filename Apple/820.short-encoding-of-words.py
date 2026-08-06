#
# @lc app=leetcode id=820 lang=python3
#
# [820] Short Encoding of Words
#
# https://leetcode.com/problems/short-encoding-of-words/description/
#
# algorithms
# Medium (60.85%)
# Likes:    1785
# Dislikes: 672
# Total Accepted:    106.3K
# Total Submissions: 174.6K
# Testcase Example:  '["time","me","bell"]'
#
# A valid encoding of an array of words is any reference string s and array of
# indices indices such that:
# 
# 
# words.length == indices.length
# The reference string s ends with the '#' character.
# For each index indices[i], the substring of s starting from indices[i] and up
# to (but not including) the next '#' character is equal to words[i].
# 
# 
# Given an array of words, return the length of the shortest reference string s
# possible of any valid encoding of words.
# 
# 
# Example 1:
# 
# 
# Input: words = ["time", "me", "bell"]
# Output: 10
# Explanation: A valid encoding would be s = "time#bell#" and indices = [0, 2,
# 5].
# words[0] = "time", the substring of s starting from indices[0] = 0 to the
# next '#' is underlined in "time#bell#"
# words[1] = "me", the substring of s starting from indices[1] = 2 to the next
# '#' is underlined in "time#bell#"
# words[2] = "bell", the substring of s starting from indices[2] = 5 to the
# next '#' is underlined in "time#bell#"
# 
# 
# Example 2:
# 
# 
# Input: words = ["t"]
# Output: 2
# Explanation: A valid encoding would be s = "t#" and indices = [0].
# 
# 
# 
# Constraints:
# 
# 
# 1 <= words.length <= 2000
# 1 <= words[i].length <= 7
# words[i] consists of only lowercase letters.
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def minimumLengthEncoding(self, words: List[str]) -> int:
        useful = set(words)
        for word in words:
            for i in range(1, len(word)):
                useful.discard(word[i:])
        return sum(len(word) + 1 for word in useful)
# @lc code=end

"""
Interview explanation:
A word does not need its own encoding if it is a suffix of another encoded word. Put all words in a set, remove every proper suffix of every word, and encode only the remaining words with a trailing '#'.

Data structure: a set gives O(1) average suffix removal and also deduplicates repeated words.

Edge cases: duplicate words count once. A word that is equal to another is not removed as its own proper suffix because suffix iteration starts at index 1.

Complexity: if total word length is L and slicing costs are counted, worst-case time is O(sum len(word)^2). Space is O(L) for the set.
"""
