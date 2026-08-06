#
# @lc app=leetcode id=953 lang=python3
#
# [953] Verifying an Alien Dictionary
#
# https://leetcode.com/problems/verifying-an-alien-dictionary/description/
#
# algorithms
# Easy (56.08%)
# Likes:    5125
# Dislikes: 1684
# Total Accepted:    592K
# Total Submissions: 1.1M
# Testcase Example:  "[\"hello\",\"leetcode\"]"
#
# In an alien language, surprisingly, they also use English lowercase letters,
# but possibly in a different order. The order of the alphabet is some
# permutation of lowercase letters.
#
# Given a sequence of words written in the alien language, and the order of the
# alphabet, return true if and only if the given words are sorted
# lexicographically in this alien language.
#
# Example 1:
#
# Input: words = ["hello","leetcode"], order = "hlabcdefgijkmnopqrstuvwxyz"
# Output: true
# Explanation: As 'h' comes before 'l' in this language, then the sequence is
# sorted.
#
# Example 2:
#
# Input: words = ["word","world","row"], order = "worldabcefghijkmnpqstuvxyz"
# Output: false
# Explanation: As 'd' comes after 'l' in this language, then words[0] >
# words[1], hence the sequence is unsorted.
#
# Example 3:
#
# Input: words = ["apple","app"], order = "abcdefghijklmnopqrstuvwxyz"
# Output: false
# Explanation: The first three characters "app" match, and the second string is
# shorter (in size.) According to lexicographical rules "apple" > "app",
# because 'l' > '∅', where '∅' is defined as the blank character which is less
# than any other character (More info).
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 20
#
# order.length == 26
#
# All characters in words[i] and order are English lowercase letters.
#

# @lc code=start
from typing import List


class Solution:
    def isAlienSorted(self, words: List[str], order: str) -> bool:
        """
        Interview explanation:
        Build rank map from alien order; check consecutive words are
        non-decreasing under that alphabet (prefix shorter comes first).

        Algorithm:
        - rank[c]=i for c in order
        - For each adjacent pair: compare char by char via rank; if unequal,
          require left < right; if all equal, len(left) <= len(right)

        Complexity: O(N) time for total characters, O(1) space (26 letters).
        """
        rank = {c: i for i, c in enumerate(order)}

        def less_eq(a: str, b: str) -> bool:
            for ca, cb in zip(a, b):
                if ca != cb:
                    return rank[ca] < rank[cb]
            return len(a) <= len(b)

        return all(less_eq(words[i], words[i + 1]) for i in range(len(words) - 1))
# @lc code=end

