#
# @lc app=leetcode id=2559 lang=python3
#
# [2559] Count Vowel Strings in Ranges
#
# https://leetcode.com/problems/count-vowel-strings-in-ranges/description/
#
# algorithms
# Medium (67.87%)
# Likes:    1192
# Dislikes: 73
# Total Accepted:    207.3K
# Total Submissions: 305.4K
# Testcase Example:  "[\"aba\",\"bcb\",\"ece\",\"aa\",\"e\"]\n[[0,2],[1,4],[1,1]]"
#
# You are given a 0-indexed array of strings words and a 2D array of integers
# queries.
#
# Each query queries[i] = [l_i, r_i] asks us to find the number of strings
# present at the indices ranging from l_i to r_i (both inclusive) of words that
# start and end with a vowel.
#
# Return an array ans of size queries.length, where ans[i] is the answer to the
# i^th query.
#
# Note that the vowel letters are 'a', 'e', 'i', 'o', and 'u'.
#
#
#
# Example 1:
#
# Input: words = ["aba","bcb","ece","aa","e"], queries = [[0,2],[1,4],[1,1]]
# Output: [2,3,0]
# Explanation: The strings starting and ending with a vowel are "aba", "ece",
# "aa" and "e".
# The answer to the query [0,2] is 2 (strings "aba" and "ece").
# to query [1,4] is 3 (strings "ece", "aa", "e").
# to query [1,1] is 0.
# We return [2,3,0].
#
# Example 2:
#
# Input: words = ["a","e","i"], queries = [[0,2],[0,1],[2,2]]
# Output: [3,2,1]
# Explanation: Every string satisfies the conditions, so we return [3,2,1].
#
#
#
# Constraints:
#
#
# 1 <= words.length <= 10^5
#
#
# 1 <= words[i].length <= 40
#
#
# words[i] consists only of lowercase English letters.
#
#
# sum(words[i].length) <= 3 * 10^5
#
#
# 1 <= queries.length <= 10^5
#
#
# 0 <= l_i <= r_i < words.length
#

# @lc code=start
from typing import List


class Solution:
    def vowelStrings(self, words: List[str], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Count words in each query range that start and end with a vowel.

        Algorithm:
        - Prefix sums of vowel-string indicators; answer = pref[r+1]-pref[l].

        Complexity: O(n+q) time, O(n) space.
        """
        vowels = set('aeiou')
        n = len(words)
        pref = [0] * (n + 1)
        for i, w in enumerate(words):
            pref[i + 1] = pref[i] + (1 if w[0] in vowels and w[-1] in vowels else 0)
        return [pref[r + 1] - pref[l] for l, r in queries]
# @lc code=end
