#
# @lc app=leetcode id=72 lang=python3
#
# [72] Edit Distance
#
# https://leetcode.com/problems/edit-distance/description/
#
# algorithms
# Medium (60.53%)
# Likes:    16473
# Dislikes: 326
# Total Accepted:    1.5M
# Total Submissions: 2.4M
# Testcase Example:  '"horse"\n"ros"'
#
# Given two strings word1 and word2, return the minimum number of operations
# required to convert word1 to word2.
# 
# You have the following three operations permitted on a word:
# 
# 
# Insert a character
# Delete a character
# Replace a character
# 
# 
# 
# Example 1:
# 
# 
# Input: word1 = "horse", word2 = "ros"
# Output: 3
# Explanation: 
# horse -> rorse (replace 'h' with 'r')
# rorse -> rose (remove 'r')
# rose -> ros (remove 'e')
# 
# 
# Example 2:
# 
# 
# Input: word1 = "intention", word2 = "execution"
# Output: 5
# Explanation: 
# intention -> inention (remove 't')
# inention -> enention (replace 'i' with 'e')
# enention -> exention (replace 'n' with 'x')
# exention -> exection (replace 'n' with 'c')
# exection -> execution (insert 'u')
# 
# 
# 
# Constraints:
# 
# 
# 0 <= word1.length, word2.length <= 500
# word1 and word2 consist of lowercase English letters.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        """
        Interview explanation:
        Edit distance has optimal substructure on prefixes. dp[j] represents the
        minimum edits to convert the processed prefix of word1 to word2[:j]. For
        each new char in word1, update a row using insert, delete, and replace.

        Transitions:
        - If chars match, carry diagonal previous value.
        - Otherwise 1 + min(delete from word1, insert into word1, replace).

        Edge cases and tests:
        - Empty word to non-empty word costs its length.
        - Equal strings cost 0.
        - Classic horse -> ros returns 3.

        Complexity: O(m*n) time, O(n) space.
        """
        m, n = len(word1), len(word2)
        dp = list(range(n + 1))

        for i in range(1, m + 1):
            prev_diag = dp[0]
            dp[0] = i
            for j in range(1, n + 1):
                old = dp[j]
                if word1[i - 1] == word2[j - 1]:
                    dp[j] = prev_diag
                else:
                    dp[j] = 1 + min(dp[j], dp[j - 1], prev_diag)
                prev_diag = old

        return dp[n]
# @lc code=end


