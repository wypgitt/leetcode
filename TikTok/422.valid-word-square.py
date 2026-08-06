#
# @lc app=leetcode id=422 lang=python3
#
# [422] Valid Word Square
#
# https://leetcode.com/problems/valid-word-square/description/
#
# algorithms
# Easy (42.92%)
# Likes:    452
# Dislikes: 277
# Total Accepted:    72K
# Total Submissions: 167.8K
# Testcase Example:  "[\"abcd\",\"bnrt\",\"crmy\",\"dtye\"]"
#
#
# Given an array of strings words, return true if it forms a valid word
# square.
#
# A sequence of strings forms a valid word square if the k^th row and
# column read the same string, where 0 <= k < max(numRows, numColumns).
#
# Example 1:
#
# Input: words = ["abcd","bnrt","crmy","dtye"]
# Output: true
# Explanation:
# The 1^st row and 1^st column both read "abcd".
# The 2^nd row and 2^nd column both read "bnrt".
# The 3^rd row and 3^rd column both read "crmy".
# The 4^th row and 4^th column both read "dtye".
# Therefore, it is a valid word square.
#
# Example 2:
#
# Input: words = ["abcd","bnrt","crm","dt"]
# Output: true
# Explanation:
# The 1^st row and 1^st column both read "abcd".
# The 2^nd row and 2^nd column both read "bnrt".
# The 3^rd row and 3^rd column both read "crm".
# The 4^th row and 4^th column both read "dt".
# Therefore, it is a valid word square.
#
# Example 3:
#
# Input: words = ["ball","area","read","lady"]
# Output: false
# Explanation:
# The 3^rd row reads "read" while the 3^rd column reads "lead".
# Therefore, it is NOT a valid word square.
#
# Constraints:
#
# 1 <= words.length <= 500
#
# 1 <= words[i].length <= 500
#
# words[i] consists of only lowercase English letters.
#
# @lc code=start

from typing import List


class Solution:
    def validWordSquare(self, words: List[str]) -> bool:
        """
        Interview explanation:
        A word square means words[i][j] == words[j][i] for all valid positions.
        Check symmetry carefully when rows have unequal lengths.

        Algorithm:
        - For each i,j: if j >= len(words) or i >= len(words[j]) or
          j >= len(words[i]) or words[i][j] != words[j][i]: False.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(words)
        for i in range(n):
            for j in range(len(words[i])):
                if j >= n or i >= len(words[j]) or words[i][j] != words[j][i]:
                    return False
        return True
# @lc code=end
