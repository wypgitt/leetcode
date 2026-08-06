#
# @lc app=leetcode id=1897 lang=python3
#
# [1897] Redistribute Characters to Make All Strings Equal
#
# https://leetcode.com/problems/redistribute-characters-to-make-all-strings-equal/description/
#
# algorithms
# Easy (66.88%)
# Likes:    1175
# Dislikes: 85
# Total Accepted:    162K
# Total Submissions: 242K
# Testcase Example:  "[\"abc\",\"aabc\",\"bc\"]"
#
# You are given an array of strings words (0-indexed).
#
# In one operation, pick two distinct indices i and j, where words[i] is a
# non-empty string, and move any character from words[i] to any position in
# words[j].
#
# Return true if you can make every string in words equal using any number of
# operations, and false otherwise.
#
# Example 1:
#
# Input: words = ["abc","aabc","bc"]
# Output: true
# Explanation: Move the first 'a' in words[1] to the front of words[2],
# to make words[1] = "abc" and words[2] = "abc".
# All the strings are now equal to "abc", so return true.
#
# Example 2:
#
# Input: words = ["ab","a"]
# Output: false
# Explanation: It is impossible to make all the strings equal using the
# operation.
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 100
#
# words[i] consists of lowercase English letters.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def makeEqual(self, words: List[str]) -> bool:
        """
        Interview explanation:
        Freely move characters between words. All words can become equal iff
        every character's total count is divisible by number of words.

        Algorithm:
        - Count all chars; all counts % len(words) == 0.

        Complexity: O(total length) time, O(1) space (26 letters).
        """
        n = len(words)
        cnt = Counter()
        for w in words:
            cnt.update(w)
        return all(v % n == 0 for v in cnt.values())
# @lc code=end
