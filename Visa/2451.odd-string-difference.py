#
# @lc app=leetcode id=2451 lang=python3
#
# [2451] Odd String Difference
#
# https://leetcode.com/problems/odd-string-difference/description/
#
# algorithms
# Easy (62.17%)
# Likes:    436
# Dislikes: 124
# Total Accepted:    46.1K
# Total Submissions: 74.1K
# Testcase Example:  "[\"adc\",\"wzy\",\"abc\"]"
#
# You are given an array of equal-length strings words. Assume that the length
# of each string is n.
#
# Each string words[i] can be converted into a difference integer array
# difference[i] of length n - 1 where difference[i][j] = words[i][j+1] -
# words[i][j] where 0 <= j <= n - 2. Note that the difference between two
# letters is the difference between their positions in the alphabet i.e. the
# position of 'a' is 0, 'b' is 1, and 'z' is 25.
#
#
# For example, for the string "acb", the difference integer array is [2 - 0, 1 -
# 2] = [2, -1].
#
# All the strings in words have the same difference integer array, except one.
# You should find that string.
#
# Return the string in words that has different difference integer array.
#
#
#
# Example 1:
#
# Input: words = ["adc","wzy","abc"]
# Output: "abc"
# Explanation:
# - The difference integer array of "adc" is [3 - 0, 2 - 3] = [3, -1].
# - The difference integer array of "wzy" is [25 - 22, 24 - 25]= [3, -1].
# - The difference integer array of "abc" is [1 - 0, 2 - 1] = [1, 1].
# The odd array out is [1, 1], so we return the corresponding string, "abc".
#
# Example 2:
#
# Input: words = ["aaa","bob","ccc","ddd"]
# Output: "bob"
# Explanation: All the integer arrays are [0, 0] except for "bob", which
# corresponds to [13, -13].
#
#
#
# Constraints:
#
#
# 3 <= words.length <= 100
#
#
# n == words[i].length
#
#
# 2 <= n <= 20
#
#
# words[i] consists of lowercase English letters.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def oddString(self, words: List[str]) -> str:
        """
        Interview explanation:
        Among words of equal length, all but one share the same difference
        array (words[i][j+1]-words[i][j]). Return the odd word out.

        Algorithm:
        - Build difference tuples; the unique key's word is the answer.

        Complexity: O(n * m) time, O(n * m) space.
        """
        diffs = []
        for w in words:
            diffs.append(tuple(ord(w[j + 1]) - ord(w[j]) for j in range(len(w) - 1)))
        cnt = Counter(diffs)
        odd = next(d for d, c in cnt.items() if c == 1)
        return words[diffs.index(odd)]
# @lc code=end

