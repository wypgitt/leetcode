#
# @lc app=leetcode id=2586 lang=python3
#
# [2586] Count the Number of Vowel Strings in Range
#
# https://leetcode.com/problems/count-the-number-of-vowel-strings-in-range/description/
#
# algorithms
# Easy (74.51%)
# Likes:    388
# Dislikes: 33
# Total Accepted:    93.6K
# Total Submissions: 125.6K
# Testcase Example:  "[\"are\",\"amy\",\"u\"]\n0\n2"
#
# You are given a 0-indexed array of string words and two integers left and
# right.
#
# A string is called a vowel string if it starts with a vowel character and ends
# with a vowel character where vowel characters are 'a', 'e', 'i', 'o', and 'u'.
#
# Return the number of vowel strings words[i] where i belongs to the inclusive
# range [left, right].
#
#
#
# Example 1:
#
# Input: words = ["are","amy","u"], left = 0, right = 2
# Output: 2
# Explanation:
# - "are" is a vowel string because it starts with 'a' and ends with 'e'.
# - "amy" is not a vowel string because it does not end with a vowel.
# - "u" is a vowel string because it starts with 'u' and ends with 'u'.
# The number of vowel strings in the mentioned range is 2.
#
# Example 2:
#
# Input: words = ["hey","aeo","mu","ooo","artro"], left = 1, right = 4
# Output: 3
# Explanation:
# - "aeo" is a vowel string because it starts with 'a' and ends with 'o'.
# - "mu" is not a vowel string because it does not start with a vowel.
# - "ooo" is a vowel string because it starts with 'o' and ends with 'o'.
# - "artro" is a vowel string because it starts with 'a' and ends with 'o'.
# The number of vowel strings in the mentioned range is 3.
#
#
#
# Constraints:
#
#
# 1 <= words.length <= 1000
#
#
# 1 <= words[i].length <= 10
#
#
# words[i] consists of only lowercase English letters.
#
#
# 0 <= left <= right < words.length
#

# @lc code=start
from typing import List


class Solution:
    def vowelStrings(self, words: List[str], left: int, right: int) -> int:
        """
        Interview explanation:
        Count words in words[left..right] that start and end with a vowel.

        Algorithm:
        - Scan the inclusive range; check first/last chars against vowel set.

        Complexity: O(right-left+1) time, O(1) space.
        """
        vowels = set('aeiou')
        return sum(1 for i in range(left, right + 1)
                   if words[i][0] in vowels and words[i][-1] in vowels)
# @lc code=end
