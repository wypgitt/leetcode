#
# @lc app=leetcode id=1768 lang=python3
#
# [1768] Merge Strings Alternately
#
# https://leetcode.com/problems/merge-strings-alternately/description/
#
# algorithms
# Easy (82.14%)
# Likes:    5018
# Dislikes: 148
# Total Accepted:    2.2M
# Total Submissions: 2.6M
# Testcase Example:  "\"abc\""
#
# You are given two strings word1 and word2. Merge the strings by adding
# letters in alternating order, starting with word1. If a string is longer than
# the other, append the additional letters onto the end of the merged string.
#
# Return the merged string.
#
# Example 1:
#
# Input: word1 = "abc", word2 = "pqr"
# Output: "apbqcr"
# Explanation: The merged string will be merged as so:
# word1: a b c
# word2: p q r
# merged: a p b q c r
#
# Example 2:
#
# Input: word1 = "ab", word2 = "pqrs"
# Output: "apbqrs"
# Explanation: Notice that as word2 is longer, "rs" is appended to the end.
# word1: a b
# word2: p q r s
# merged: a p b q r s
#
# Example 3:
#
# Input: word1 = "abcd", word2 = "pq"
# Output: "apbqcd"
# Explanation: Notice that as word1 is longer, "cd" is appended to the end.
# word1: a b c d
# word2: p q
# merged: a p b q c d
#
# Constraints:
#
# 1 <= word1.length, word2.length <= 100
#
# word1 and word2 consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def mergeAlternately(self, word1: str, word2: str) -> str:
        """
        Interview explanation:
        Merge by alternating characters starting with word1; append leftovers
        from the longer string.

        Algorithm:
        - i over min length: append word1[i], word2[i]; then append remaining suffix.

        Complexity: O(n+m) time and space.
        """
        out = []
        n, m = len(word1), len(word2)
        for i in range(min(n, m)):
            out.append(word1[i])
            out.append(word2[i])
        out.append(word1[min(n, m) :])
        out.append(word2[min(n, m) :])
        return "".join(out)

    def mergeAlternately_zip(self, word1: str, word2: str) -> str:
        """
        Interview explanation:
        Alternate using zip for the common prefix then concatenate remainders.

        Algorithm:
        - ''.join(a+b for a,b in zip(word1,word2)) + word1[m:] + word2[m:]
          with m=min lengths.

        Complexity: O(n+m).
        """
        m = min(len(word1), len(word2))
        return "".join(a + b for a, b in zip(word1, word2)) + word1[m:] + word2[m:]
# @lc code=end
