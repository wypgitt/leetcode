#
# @lc app=leetcode id=1408 lang=python3
#
# [1408] String Matching in an Array
#
# https://leetcode.com/problems/string-matching-in-an-array/description/
#
# algorithms
# Easy (69.82%)
# Likes:    1514
# Dislikes: 131
# Total Accepted:    301K
# Total Submissions: 432K
# Testcase Example:  "[\"mass\",\"as\",\"hero\",\"superhero\"]"
#
# Given an array of string words, return all strings in words that are a
# substring of another word. You can return the answer in any order.
#
# Example 1:
#
# Input: words = ["mass","as","hero","superhero"]
# Output: ["as","hero"]
# Explanation: "as" is substring of "mass" and "hero" is substring of
# "superhero".
# ["hero","as"] is also a valid answer.
#
# Example 2:
#
# Input: words = ["leetcode","et","code"]
# Output: ["et","code"]
# Explanation: "et", "code" are substring of "leetcode".
#
# Example 3:
#
# Input: words = ["blue","green","bu"]
# Output: []
# Explanation: No string of words is substring of another string.
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 30
#
# words[i] contains only lowercase English letters.
#
# All the strings of words are unique.
#

# @lc code=start
from typing import List


class Solution:
    def stringMatching(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        Return words that are substrings of some other word. Brute-force check
        each word against every other (n<=100, lengths small).

        Algorithm:
        - For each word w, if any other word contains w as substring, keep w.

        Complexity: O(n^2 * L) time, O(1) extra (output excluded).
        """
        ans = []
        for i, w in enumerate(words):
            for j, other in enumerate(words):
                if i != j and w in other:
                    ans.append(w)
                    break
        return ans

    def stringMatching_sorted(self, words: List[str]) -> List[str]:
        """
        Interview explanation:
        Alternate: sort by length ascending; a word can only be substring of a
        longer (or equal-length identical-content) word — still check others.

        Algorithm:
        - Sort by len; for each w check later longer words for containment.

        Complexity: O(n^2 * L + n log n) time.
        """
        words_sorted = sorted(words, key=len)
        ans = []
        n = len(words_sorted)
        for i in range(n):
            for j in range(i + 1, n):
                if words_sorted[i] in words_sorted[j]:
                    ans.append(words_sorted[i])
                    break
        return ans
# @lc code=end
