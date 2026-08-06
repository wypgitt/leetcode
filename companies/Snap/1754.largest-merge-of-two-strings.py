#
# @lc app=leetcode id=1754 lang=python3
#
# [1754] Largest Merge Of Two Strings
#
# https://leetcode.com/problems/largest-merge-of-two-strings/description/
#
# algorithms
# Medium (54.41%)
# Likes:    621
# Dislikes: 87
# Total Accepted:    37.0K
# Total Submissions: 68.0K
# Testcase Example:  "\"cabaa\""
#
# You are given two strings word1 and word2. You want to construct a string
# merge in the following way: while either word1 or word2 are non-empty, choose
# one of the following options:
#
# If word1 is non-empty, append the first character in word1 to merge and
# delete it from word1.
#
# For example, if word1 = "abc" and merge = "dv", then after choosing this
# operation, word1 = "bc" and merge = "dva".
#
# If word2 is non-empty, append the first character in word2 to merge and
# delete it from word2.
#
# For example, if word2 = "abc" and merge = "", then after choosing this
# operation, word2 = "bc" and merge = "a".
#
# Return the lexicographically largest merge you can construct.
#
# A string a is lexicographically larger than a string b (of the same length)
# if in the first position where a and b differ, a has a character strictly
# larger than the corresponding character in b. For example, "abcd" is
# lexicographically larger than "abcc" because the first position they differ
# is at the fourth character, and d is greater than c.
#
# Example 1:
#
# Input: word1 = "cabaa", word2 = "bcaaa"
# Output: "cbcabaaaaa"
# Explanation: One way to get the lexicographically largest merge is:
# - Take from word1: merge = "c", word1 = "abaa", word2 = "bcaaa"
# - Take from word2: merge = "cb", word1 = "abaa", word2 = "caaa"
# - Take from word2: merge = "cbc", word1 = "abaa", word2 = "aaa"
# - Take from word1: merge = "cbca", word1 = "baa", word2 = "aaa"
# - Take from word1: merge = "cbcab", word1 = "aa", word2 = "aaa"
# - Append the remaining 5 a's from word1 and word2 at the end of merge.
#
# Example 2:
#
# Input: word1 = "abcabc", word2 = "abdcaba"
# Output: "abdcabcabcaba"
#
# Constraints:
#
# 1 <= word1.length, word2.length <= 3000
#
# word1 and word2 consist only of lowercase English letters.
#

# @lc code=start
class Solution:
    def largestMerge(self, word1: str, word2: str) -> str:
        """
        Interview explanation:
        Greedily build the lexicographically largest merge: always append a
        char from the larger remaining suffix (compare word1[i:] vs word2[j:]).

        Algorithm:
        - i=j=0; while both nonempty: take from larger suffix; append remainder.

        Complexity: O((n+m)^2) time, O(n+m) space.
        """
        i = j = 0
        n, m = len(word1), len(word2)
        out = []
        while i < n and j < m:
            if word1[i:] > word2[j:]:
                out.append(word1[i])
                i += 1
            else:
                out.append(word2[j])
                j += 1
        out.append(word1[i:])
        out.append(word2[j:])
        return "".join(out)

    def largestMerge_compare(self, word1: str, word2: str) -> str:
        """
        Interview explanation:
        Alternate: same greedy without full suffix slices—manual char-by-char
        lexicographic compare of remaining suffixes.

        Algorithm:
        - Walk while equal chars; pick the side with larger next char (or longer).

        Complexity: O((n+m)^2) time, O(n+m) space.
        """
        i = j = 0
        n, m = len(word1), len(word2)
        out = []
        while i < n and j < m:
            a, b = i, j
            while a < n and b < m and word1[a] == word2[b]:
                a += 1
                b += 1
            if b == m or (a < n and word1[a] > word2[b]):
                out.append(word1[i])
                i += 1
            else:
                out.append(word2[j])
                j += 1
        out.append(word1[i:])
        out.append(word2[j:])
        return "".join(out)
# @lc code=end
