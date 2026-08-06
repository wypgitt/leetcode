#
# @lc app=leetcode id=1657 lang=python3
#
# [1657] Determine if Two Strings Are Close
#
# https://leetcode.com/problems/determine-if-two-strings-are-close/description/
#
# algorithms
# Medium (54.39%)
# Likes:    4174
# Dislikes: 363
# Total Accepted:    591K
# Total Submissions: 1.1M
# Testcase Example:  "\"abc\""
#
# Two strings are considered close if you can attain one from the other using
# the following operations:
#
# Operation 1: Swap any two existing characters.
#
# For example, abcde -> aecdb
#
# Operation 2: Transform every occurrence of one existing character into
# another existing character, and do the same with the other character.
#
# For example, aacabb -> bbcbaa (all a's turn into b's, and all b's turn into
# a's)
#
# You can use the operations on either string as many times as necessary.
#
# Given two strings, word1 and word2, return true if word1 and word2 are close,
# and false otherwise.
#
# Example 1:
#
# Input: word1 = "abc", word2 = "bca"
# Output: true
# Explanation: You can attain word2 from word1 in 2 operations.
# Apply Operation 1: "abc" -> "acb"
# Apply Operation 1: "acb" -> "bca"
#
# Example 2:
#
# Input: word1 = "a", word2 = "aa"
# Output: false
# Explanation: It is impossible to attain word2 from word1, or vice versa, in
# any number of operations.
#
# Example 3:
#
# Input: word1 = "cabbba", word2 = "abbccc"
# Output: true
# Explanation: You can attain word2 from word1 in 3 operations.
# Apply Operation 1: "cabbba" -> "caabbb"
# Apply Operation 2: "caabbb" -> "baaccc"
# Apply Operation 2: "baaccc" -> "abbccc"
#
# Constraints:
#
# 1 <= word1.length, word2.length <= 10^5
#
# word1 and word2 contain only lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def closeStrings(self, word1: str, word2: str) -> bool:
        """
        Interview explanation:
        Operations: swap any two chars (permute freely) or transform all
        occurrences of one char into another existing char (swap frequencies).
        Close iff same character set and same multiset of frequencies.

        Algorithm:
        - Counter both; keys equal and sorted values equal.

        Complexity: O(n + Σ) time, O(Σ) space (Σ=26).
        """
        if len(word1) != len(word2):
            return False
        c1, c2 = Counter(word1), Counter(word2)
        return c1.keys() == c2.keys() and sorted(c1.values()) == sorted(c2.values())

    def closeStrings_arrays(self, word1: str, word2: str) -> bool:
        """
        Interview explanation:
        Alternate: fixed 26-length frequency arrays; compare presence bits and
        sorted frequency lists.

        Algorithm:
        - Build cnt1/cnt2[26]; require (c>0) equal per letter; sorted cnts equal.

        Complexity: O(n) time, O(1) space.
        """
        if len(word1) != len(word2):
            return False
        c1 = [0] * 26
        c2 = [0] * 26
        for ch in word1:
            c1[ord(ch) - 97] += 1
        for ch in word2:
            c2[ord(ch) - 97] += 1
        for a, b in zip(c1, c2):
            if (a == 0) != (b == 0):
                return False
        return sorted(c1) == sorted(c2)
# @lc code=end
