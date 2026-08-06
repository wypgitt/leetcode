#
# @lc app=leetcode id=2573 lang=python3
#
# [2573] Find the String with LCP
#
# https://leetcode.com/problems/find-the-string-with-lcp/description/
#
# algorithms
# Hard (63.12%)
# Likes:    452
# Dislikes: 62
# Total Accepted:    64.5K
# Total Submissions: 102.3K
# Testcase Example:  "[[4,0,2,0],[0,3,0,1],[2,0,2,0],[0,1,0,1]]"
#
# We define the lcp matrix of any 0-indexed string word of n lowercase English
# letters as an n x n grid such that:
#
#
# lcp[i][j] is equal to the length of the longest common prefix between the
# substrings word[i,n-1] and word[j,n-1].
#
# Given an n x n matrix lcp, return the alphabetically smallest string word that
# corresponds to lcp. If there is no such string, return an empty string.
#
# A string a is lexicographically smaller than a string b (of the same length)
# if in the first position where a and b differ, string a has a letter that
# appears earlier in the alphabet than the corresponding letter in b. For
# example, "aabd" is lexicographically smaller than "aaca" because the first
# position they differ is at the third letter, and 'b' comes before 'c'.
#
#
#
# Example 1:
#
# Input: lcp = [[4,0,2,0],[0,3,0,1],[2,0,2,0],[0,1,0,1]]
# Output: "abab"
# Explanation: lcp corresponds to any 4 letter string with two alternating
# letters. The lexicographically smallest of them is "abab".
#
# Example 2:
#
# Input: lcp = [[4,3,2,1],[3,3,2,1],[2,2,2,1],[1,1,1,1]]
# Output: "aaaa"
# Explanation: lcp corresponds to any 4 letter string with a single distinct
# letter. The lexicographically smallest of them is "aaaa".
#
# Example 3:
#
# Input: lcp = [[4,3,2,1],[3,3,2,1],[2,2,2,1],[1,1,1,3]]
# Output: ""
# Explanation: lcp[3][3] cannot be equal to 3 since word[3,...,3] consists of
# only a single letter; Thus, no answer exists.
#
#
#
# Constraints:
#
#
# 1 <= n == lcp.length == lcp[i].length <= 1000
#
#
# 0 <= lcp[i][j] <= n
#

# @lc code=start
from typing import List


class Solution:
    def findTheString(self, lcp: List[List[int]]) -> str:
        """
        Interview explanation:
        Reconstruct the lexicographically smallest string whose LCP matrix equals lcp,
        or return "" if impossible.

        Algorithm:
        - Greedily assign letters: for i, reuse s[j] when lcp[i][j]>0 for some j<i; else next letter.
        - Validate by recomputing LCP constraints: lcp[i][j] must match equality and recurrence.

        Complexity: O(n^2) time and space.
        """
        n = len(lcp)
        s = [''] * n
        letter = 0
        for i in range(n):
            if s[i]:
                continue
            if letter >= 26:
                return ""
            ch = chr(ord('a') + letter)
            letter += 1
            for j in range(i, n):
                if lcp[i][j] > 0:
                    s[j] = ch
        if any(c == '' for c in s):
            return ""
        # validate
        for i in range(n - 1, -1, -1):
            for j in range(n - 1, -1, -1):
                if s[i] == s[j]:
                    expect = 1 + (lcp[i + 1][j + 1] if i + 1 < n and j + 1 < n else 0)
                else:
                    expect = 0
                if lcp[i][j] != expect:
                    return ""
        return ''.join(s)
# @lc code=end
