#
# @lc app=leetcode id=387 lang=python3
#
# [387] First Unique Character in a String
#
# https://leetcode.com/problems/first-unique-character-in-a-string/description/
#
# algorithms
# Easy (66.01%)
# Likes:    9919
# Dislikes: 336
# Total Accepted:    2.5M
# Total Submissions: 3.8M
# Testcase Example:  "\"leetcode\""
#
# Given a string s, find the first non-repeating character in it and return its
# index. If it does not exist, return -1.
#
# Example 1:
#
# Input: s = "leetcode"
#
# Output: 0
#
# Explanation:
#
# The character 'l' at index 0 is the first character that does not occur at
# any other index.
#
# Example 2:
#
# Input: s = "loveleetcode"
#
# Output: 2
#
# Example 3:
#
# Input: s = "aabb"
#
# Output: -1
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of only lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def firstUniqChar(self, s: str) -> int:
        """
        Interview explanation:
        Count frequencies, then scan left-to-right for the first char with
        count 1. Two passes over a lowercase alphabet string.

        Algorithm:
        - Counter(s); for i, ch in enumerate(s): if count[ch]==1 return i.
        - Else return -1.

        Complexity: O(n) time, O(1) space (26 letters).
        """
        count = Counter(s)
        for i, ch in enumerate(s):
            if count[ch] == 1:
                return i
        return -1
# @lc code=end
