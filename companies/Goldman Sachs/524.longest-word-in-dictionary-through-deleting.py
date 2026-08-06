#
# @lc app=leetcode id=524 lang=python3
#
# [524] Longest Word in Dictionary through Deleting
#
# https://leetcode.com/problems/longest-word-in-dictionary-through-deleting/description/
#
# algorithms
# Medium (52.91%)
# Likes:    1877
# Dislikes: 367
# Total Accepted:    188K
# Total Submissions: 355K
# Testcase Example:  "\"abpcplea\""
#
# Given a string s and a string array dictionary, return the longest string in
# the dictionary that can be formed by deleting some of the given string
# characters. If there is more than one possible result, return the longest
# word with the smallest lexicographical order. If there is no possible result,
# return the empty string.
#
# Example 1:
#
# Input: s = "abpcplea", dictionary = ["ale","apple","monkey","plea"]
# Output: "apple"
#
# Example 2:
#
# Input: s = "abpcplea", dictionary = ["a","b","c"]
# Output: "a"
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# 1 <= dictionary.length <= 1000
#
# 1 <= dictionary[i].length <= 1000
#
# s and dictionary[i] consist of lowercase English letters.
#

# @lc code=start
from typing import List
class Solution:
    def findLongestWord(self, s: str, dictionary: List[str]) -> str:
        """
        Interview explanation:
        A dictionary word is valid if it is a subsequence of s. Among valid
        words pick the longest; ties → lexicographically smallest.

        Algorithm:
        - For each word, two-pointer check subsequence of s.
        - Keep best by (-length, word) order.

        Complexity: O(sum(|w|) + |dict| * |s|) time, O(1) extra beyond answer.
        """
        def is_subseq(word: str) -> bool:
            i = 0
            for ch in s:
                if i < len(word) and ch == word[i]:
                    i += 1
                    if i == len(word):
                        return True
            return i == len(word)

        best = ""
        for word in dictionary:
            if is_subseq(word):
                if len(word) > len(best) or (len(word) == len(best) and word < best):
                    best = word
        return best
# @lc code=end
