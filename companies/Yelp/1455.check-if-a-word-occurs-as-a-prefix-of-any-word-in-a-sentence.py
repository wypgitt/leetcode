#
# @lc app=leetcode id=1455 lang=python3
#
# [1455] Check If a Word Occurs As a Prefix of Any Word in a Sentence
#
# https://leetcode.com/problems/check-if-a-word-occurs-as-a-prefix-of-any-word-in-a-sentence/description/
#
# algorithms
# Easy (68.8%)
# Likes:    1336
# Dislikes: 60
# Total Accepted:    243K
# Total Submissions: 353K
# Testcase Example:  "\"i love eating burger\""
#
# Given a sentence that consists of some words separated by a single space, and
# a searchWord, check if searchWord is a prefix of any word in sentence.
#
# Return the index of the word in sentence (1-indexed) where searchWord is a
# prefix of this word. If searchWord is a prefix of more than one word, return
# the index of the first word (minimum index). If there is no such word return
# -1.
#
# A prefix of a string s is any leading contiguous substring of s.
#
# Example 1:
#
# Input: sentence = "i love eating burger", searchWord = "burg"
# Output: 4
# Explanation: "burg" is prefix of "burger" which is the 4th word in the
# sentence.
#
# Example 2:
#
# Input: sentence = "this problem is an easy problem", searchWord = "pro"
# Output: 2
# Explanation: "pro" is prefix of "problem" which is the 2nd and the 6th word
# in the sentence, but we return 2 as it's the minimal index.
#
# Example 3:
#
# Input: sentence = "i am tired", searchWord = "you"
# Output: -1
# Explanation: "you" is not a prefix of any word in the sentence.
#
# Constraints:
#
# 1 <= sentence.length <= 100
#
# 1 <= searchWord.length <= 10
#
# sentence consists of lowercase English letters and spaces.
#
# searchWord consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def isPrefixOfWord(self, sentence: str, searchWord: str) -> int:
        """
        Interview explanation:
        Find 1-indexed word where searchWord is a prefix; return first such
        index or -1.

        Algorithm:
        - Split sentence; enumerate; if word.startswith(searchWord) return i+1.

        Complexity: O(total length) time, O(1) extra beyond split.
        """
        for i, w in enumerate(sentence.split()):
            if w.startswith(searchWord):
                return i + 1
        return -1

    def isPrefixOfWord_scan(self, sentence: str, searchWord: str) -> int:
        """
        Interview explanation:
        Alternate: single pass without storing all words — track word index
        and match prefix at word starts.

        Algorithm:
        - Walk chars; on word start compare searchWord; increment word index.

        Complexity: O(n) time, O(1) space.
        """
        idx = 1
        i, n, m = 0, len(sentence), len(searchWord)
        while i < n:
            j = 0
            while i < n and j < m and sentence[i] == searchWord[j]:
                i += 1
                j += 1
            if j == m and (i == n or sentence[i] == " "):
                return idx
            while i < n and sentence[i] != " ":
                i += 1
            while i < n and sentence[i] == " ":
                i += 1
            idx += 1
        return -1
# @lc code=end
