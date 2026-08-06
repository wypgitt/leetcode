#
# @lc app=leetcode id=3302 lang=python3
#
# [3302] Find the Lexicographically Smallest Valid Sequence
#
# https://leetcode.com/problems/find-the-lexicographically-smallest-valid-sequence/description/
#
# algorithms
# Medium (22.40%)
# Likes:    163
# Dislikes: 35
# Total Accepted:    8K
# Total Submissions: 35.8K
# Testcase Example:  "\"vbcca\"\n\"abc\""
#
#
# You are given two strings word1 and word2.
#
# A string x is called almost equal to y if you can change at most one
# character in x to make it identical to y.
#
# A sequence of indices seq is called valid if:
#
# The indices are sorted in ascending order.
#
# Concatenating the characters at these indices in word1 in the same order
# results in a string that is almost equal to word2.
#
# Return an array of size word2.length representing the lexicographically
# smallest valid sequence of indices. If no such sequence of indices
# exists, return an empty array.
#
# Note that the answer must represent the lexicographically smallest
# array, not the corresponding string formed by those indices.
#
# Example 1:
#
# Input: word1 = "vbcca", word2 = "abc"
#
# Output: [0,1,2]
#
# Explanation:
#
# The lexicographically smallest valid sequence of indices is [0, 1, 2]:
#
# Change word1[0] to 'a'.
#
# word1[1] is already 'b'.
#
# word1[2] is already 'c'.
#
# Example 2:
#
# Input: word1 = "bacdc", word2 = "abc"
#
# Output: [1,2,4]
#
# Explanation:
#
# The lexicographically smallest valid sequence of indices is [1, 2, 4]:
#
# word1[1] is already 'a'.
#
# Change word1[2] to 'b'.
#
# word1[4] is already 'c'.
#
# Example 3:
#
# Input: word1 = "aaaaaa", word2 = "aaabc"
#
# Output: []
#
# Explanation:
#
# There is no valid sequence of indices.
#
# Example 4:
#
# Input: word1 = "abc", word2 = "ab"
#
# Output: [0,1]
#
# Constraints:
#
# 1 <= word2.length < word1.length <= 3 * 10^5
#
# word1 and word2 consist only of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def validSequence(self, word1: str, word2: str) -> List[int]:
        """
        Interview explanation:
        Pick the lex-smallest increasing index sequence in word1 whose chars are
        almost equal to word2 (at most one mismatch).

        Algorithm:
        - Right-greedy match: can[j] = position of word2[j] when matching suffix
          word2[j:] from the end of word1 (can[m] = n).
        - Scan left to right; take exact matches greedily. On mismatch, skip once
          iff can[j + 1] > i (remaining suffix still fits after i).

        Complexity: O(n + m) time, O(m) space.
        """
        n, m = len(word1), len(word2)
        can = [-1] * (m + 1)
        can[m] = n
        j = m - 1
        for i in range(n - 1, -1, -1):
            if j >= 0 and word1[i] == word2[j]:
                can[j] = i
                j -= 1

        res: List[int] = []
        i = 0
        skipped = False
        for j in range(m):
            while i < n:
                if word1[i] == word2[j]:
                    res.append(i)
                    i += 1
                    break
                if not skipped and can[j + 1] > i:
                    res.append(i)
                    i += 1
                    skipped = True
                    break
                i += 1
            else:
                return []
        return res
# @lc code=end
