#
# @lc app=leetcode id=243 lang=python3
#
# [243] Shortest Word Distance
#
# https://leetcode.com/problems/shortest-word-distance/description/
#
# algorithms
# Easy (66.37%)
# Likes:    1294
# Dislikes: 129
# Total Accepted:    248.4K
# Total Submissions: 374.3K
# Testcase Example:  "[\"practice\", \"makes\", \"perfect\", \"coding\", \"makes\"]\n\"coding\"\n\"practice\""
#
#
# Given an array of strings wordsDict and two different strings that
# already exist in the array word1 and word2, return the shortest distance
# between these two words in the list.
#
# Example 1:
#
# Input: wordsDict = ["practice", "makes", "perfect", "coding", "makes"],
# word1 = "coding", word2 = "practice"
# Output: 3
#
# Example 2:
#
# Input: wordsDict = ["practice", "makes", "perfect", "coding", "makes"],
# word1 = "makes", word2 = "coding"
# Output: 1
#
# Constraints:
#
# 2 <= wordsDict.length <= 3 * 10^4
#
# 1 <= wordsDict[i].length <= 10
#
# wordsDict[i] consists of lowercase English letters.
#
# word1 and word2 are in wordsDict.
#
# word1 != word2
#
# @lc code=start
from typing import List


class Solution:
    def shortestDistance(self, wordsDict: List[str], word1: str, word2: str) -> int:
        """
        Interview explanation:
        One pass: track the latest indices of word1 and word2; whenever both
        have been seen, update the minimum |i1 - i2|.

        Algorithm:
        - i1 = i2 = -1; ans = inf.
        - For each index i: update i1 or i2 when matching; if both set, min ans.

        Complexity: O(n) time, O(1) space.
        """
        i1 = i2 = -1
        ans = len(wordsDict)
        for i, w in enumerate(wordsDict):
            if w == word1:
                i1 = i
            elif w == word2:
                i2 = i
            if i1 != -1 and i2 != -1:
                ans = min(ans, abs(i1 - i2))
        return ans
# @lc code=end
